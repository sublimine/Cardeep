"""Dedup + upsert helpers for association-mined dealers (discover_associations front).

Dedup strategy (per CARDEEP mandate):
  1. Bare-host website match against existing entity.website (any source).
  2. Normalized name + municipality_code match.
  3. Normalized name + province_code (when municipality unknown).
A new dealer is upserted ONLY when none of the above hit an existing row.

We build an in-memory index ONCE from the live DB so dedup is O(1) per candidate
and we never trust injected state without reading the source of truth.
"""
from __future__ import annotations

import os
import re
import secrets
import time
import unicodedata
from dataclasses import dataclass, field

import psycopg2
import psycopg2.extras

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.api.codes import cdp_code  # noqa: E402

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def ulid() -> str:
    ts = int(time.time() * 1000)
    rnd = int.from_bytes(secrets.token_bytes(10), "big")
    num = (ts << 80) | rnd
    out = []
    for _ in range(26):
        out.append(_CROCKFORD[num & 0x1F])
        num >>= 5
    return "".join(reversed(out))


def normalize_name(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    # strip legal suffixes that vary across sources
    text = re.sub(r"[^a-z0-9 ]+", " ", text.lower())
    text = re.sub(r"\b(s\s?l\s?u?|s\s?a\s?u?|s\s?c\s?p?|sociedad limitada|sociedad anonima)\b", " ", text)
    text = re.sub(r"\s+", "", text)
    return text


def bare_host(website: str | None) -> str | None:
    if not website:
        return None
    d = website.lower().strip()
    d = re.sub(r"^https?://", "", d)
    d = re.sub(r"^www\.", "", d)
    d = d.split("?")[0].split("#")[0].rstrip("/")
    host = d.partition("/")[0]
    return host or None


@dataclass
class DedupIndex:
    by_host: dict = field(default_factory=dict)
    by_name_muni: dict = field(default_factory=dict)
    by_name_prov: dict = field(default_factory=dict)

    @classmethod
    def load(cls, conn) -> "DedupIndex":
        idx = cls()
        cur = conn.cursor()
        cur.execute(
            "SELECT cdp_code, trade_name, legal_name, website, municipality_code, province_code FROM entity"
        )
        for cdp, trade, legal, website, muni, prov in cur:
            h = bare_host(website)
            if h:
                idx.by_host.setdefault(h, cdp)
            for nm in (trade, legal):
                if not nm:
                    continue
                n = normalize_name(nm)
                if not n:
                    continue
                if muni:
                    idx.by_name_muni.setdefault((n, muni), cdp)
                if prov:
                    idx.by_name_prov.setdefault((n, prov), cdp)
        cur.close()
        return idx

    def match(self, *, name: str | None, website: str | None,
              municipality_code: str | None, province_code: str | None):
        """Return (existing_cdp, reason) if duplicate, else (None, None)."""
        h = bare_host(website)
        if h and h in self.by_host:
            return self.by_host[h], f"host:{h}"
        if name:
            n = normalize_name(name)
            if n and municipality_code and (n, municipality_code) in self.by_name_muni:
                return self.by_name_muni[(n, municipality_code)], f"name+muni:{n}|{municipality_code}"
            if n and province_code and (n, province_code) in self.by_name_prov:
                return self.by_name_prov[(n, province_code)], f"name+prov:{n}|{province_code}"
        return None, None

    def register(self, *, cdp: str, name: str | None, website: str | None,
                 municipality_code: str | None, province_code: str | None) -> None:
        h = bare_host(website)
        if h:
            self.by_host.setdefault(h, cdp)
        if name:
            n = normalize_name(name)
            if n and municipality_code:
                self.by_name_muni.setdefault((n, municipality_code), cdp)
            if n and province_code:
                self.by_name_prov.setdefault((n, province_code), cdp)


class GeoResolver:
    """Resolve province name -> code and (name, province) -> municipality_code."""

    def __init__(self, conn):
        self.prov_by_name = {}
        self.muni = {}  # (norm_muni_name, prov_code) -> code
        cur = conn.cursor()
        cur.execute("SELECT code, name FROM geo_province")
        for code, name in cur:
            self.prov_by_name[normalize_name(name)] = code
            # also index each slash-variant (Araba/Alava)
            for part in re.split(r"[/]", name):
                p = normalize_name(part)
                if p:
                    self.prov_by_name.setdefault(p, code)
        cur.execute("SELECT code, name, province_code FROM geo_municipality")
        for code, name, prov in cur:
            self.muni.setdefault((normalize_name(name), prov), code)
            for part in re.split(r"[/]", name):
                p = normalize_name(part)
                if p:
                    self.muni.setdefault((p, prov), code)
        cur.close()

    PROV_ALIASES = {
        "alava": "01", "araba": "01", "gipuzkoa": "20", "guipuzcoa": "20",
        "bizkaia": "48", "vizcaya": "48", "lacoruna": "15", "coruna": "15",
        "acoruna": "15", "lleida": "25", "lerida": "25", "girona": "17",
        "gerona": "17", "ourense": "32", "orense": "32", "illesbalears": "07",
        "islasbaleares": "07", "baleares": "07", "balears": "07",
        "santacruzdetenerife": "38", "tenerife": "38", "laspalmas": "35",
        "castellon": "12", "castello": "12", "alacant": "03", "alicante": "03",
        "valencia": "46", "valencia/valencia": "46", "asturias": "33",
        "navarra": "31", "nafarroa": "31", "cantabria": "39", "madrid": "28",
        "barcelona": "08", "tarragona": "43", "zaragoza": "50", "malaga": "29",
        "sevilla": "41", "murcia": "30", "lleida/lerida": "25",
    }

    def province(self, name: str | None) -> str | None:
        if not name:
            return None
        n = normalize_name(name)
        if n in self.prov_by_name:
            return self.prov_by_name[n]
        if n in self.PROV_ALIASES:
            return self.PROV_ALIASES[n]
        return None

    def municipality(self, name: str | None, prov_code: str | None) -> str | None:
        if not name or not prov_code:
            return None
        return self.muni.get((normalize_name(name), prov_code))


def upsert_entity(conn, idx: DedupIndex, *, name: str, kind: str, source_key: str,
                  source_ref: str, website: str | None = None,
                  province_code: str | None = None, municipality_code: str | None = None,
                  address: str | None = None, phone: str | None = None,
                  email: str | None = None, legal_name: str | None = None):
    """Dedup then insert. Returns (cdp_code, status) where status in
    {'new','dup','skip'}. Always attaches an entity_source row when entity exists."""
    existing, reason = idx.match(name=name, website=website,
                                 municipality_code=municipality_code,
                                 province_code=province_code)
    cur = conn.cursor()
    host = bare_host(website)
    if existing:
        # attach association as a corroborating source on the existing entity
        cur.execute(
            "INSERT INTO entity_source (entity_ulid, source_key, source_ref) "
            "SELECT entity_ulid, %s, %s FROM entity WHERE cdp_code=%s "
            "ON CONFLICT DO NOTHING",
            (source_key, source_ref, existing))
        cur.close()
        return existing, "dup", reason

    if not province_code:
        cur.close()
        return None, "skip", "no_province"

    code = cdp_code(province_code=province_code, domain=host,
                    name=name, municipality_code=municipality_code, address=address)
    # guard: code might already exist (same canonical key seen this run)
    cur.execute("SELECT entity_ulid FROM entity WHERE cdp_code=%s", (code,))
    row = cur.fetchone()
    if row:
        cur.execute(
            "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES (%s,%s,%s) "
            "ON CONFLICT DO NOTHING", (row[0], source_key, source_ref))
        idx.register(cdp=code, name=name, website=website,
                     municipality_code=municipality_code, province_code=province_code)
        cur.close()
        return code, "dup", "cdp_exists"

    eulid = ulid()
    cur.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, municipality_code, address, phone, email, website,
               website_waf, is_tier1, status, first_discovered_source, kind_source,
               source_group, sells_cars)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'none',FALSE,'unverified',%s,'legal_census','association',TRUE)
        """,
        (eulid, code, kind, legal_name or name, name, province_code, municipality_code,
         address, phone, email, website, source_key))
    cur.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES (%s,%s,%s) "
        "ON CONFLICT DO NOTHING", (eulid, source_key, source_ref))
    idx.register(cdp=code, name=name, website=website,
                 municipality_code=municipality_code, province_code=province_code)
    cur.close()
    return code, "new", None


def connect():
    return psycopg2.connect(DSN)
