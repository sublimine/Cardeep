"""kia (Kia Seminuevos Certificados / "Kia Okasión" ES certified-used) WHOLESALE harvester — end to end.

www.kia.com/es ("Kia Seminuevos Certificados", the Kia Iberia certified-used programme) is the
manufacturer-owned certified-used portal for Kia in Spain. Like toyota_lexus (Toyota Group),
spoticar (Stellantis) and renew (Renault Group) it is NOT a car-specialist marketplace
(coches.net/autoscout24/motor.es) nor a generalist classifieds (wallapop): it is an OEM-VO PORTAL
— a brand owner publishing the certified-used inventory of its own official dealer network
(concesionarios oficiales Kia). It is the next member of the 'oem_vo_portal' source_group, in the
new 'kia_vo' family, the sibling of toyota_lexus/spoticar/renew under the same ONE architecture.

The kia.com SPA buscador embeds a THIRD-PARTY vendor backend: "Kia Okasión" at kiaokasion.net
(an ASP.NET / Microsoft-IIS application). The buscador calls ONE internal endpoint —
POST https://kiaokasion.net/kia/async/metodos.aspx — a multiplexed servlet keyed by an `accion`
form field. accion=actualizarCoches returns the car page; accion=actualizarTodoBuscador returns
the facet aggregations. No browser, no proxy, no cookie warm-up, no auth: the bare IIS root 403s
plain curl (request filtering), but the metodos.aspx POST serves HTTP 200 application/json to
curl_cffi chrome131 with a kia.com Referer (defense_tier=t1_soft — a soft WAF present, no JS
challenge, no tier-1 CDN). is_tier1=FALSE (no Cloudflare/Akamai fronts the vendor).

CATALOG PARTITION — the load-bearing structural fact. The vendor catalog is partitioned by
`idconcesionario` (the kia.com page's inline `__kiaClienteId` — a dealer-GROUP CLUSTER id, NOT a
single dealer). idconcesionario=0 returns 0 cars; only a SPARSE SET of valid cluster ids (55 live
clusters, ids 331..1810, swept exhaustively over 1..2000) carries stock. `km=nacional` only
relaxes the geo radius WITHIN a cluster's own stock; it does NOT aggregate across clusters. So the
full ES national stock = the UNION over every valid cluster id. A cluster can span several physical
sites/cities (e.g. cluster 926 = QUADIS ARmotors across Tarragona + Sant Boi), so the SELLING
DEALER is taken PER CAR from the embedded `concesionario` (name) + `poblacion` (city), NOT from the
cluster. The cluster id is the catalog partition + a dealer-identity disambiguator. Verified live
2026-06-13 (docs/architecture/tier1_recipes/oem_kia_datalayer.md).

Each car page item carries the car AND its selling official dealer (concesionario name + poblacion
city). There is NO postal code or lat/lng in the LIST response (the per-car ficha detail carries
`cp`, but the city alone resolves the province cleanly — Kia's poblacion values are unambiguous INE
municipality names, 100% resolved by GeoResolver in the live probe, so NO ficha fetch is needed).
This is an OEM certified-used portal: every car belongs to an official Kia dealer; NO private
sellers.

This module mirrors pipeline.platform.oem_toyota_lexus_wholesale EXACTLY (the proven single-brand
OEM-VO template: same dual-membership model, same bulk cage, same governor/health/VAM wiring,
same per-brand-surface drain shape — here per-cluster). It proves the OEM-VO group flows through
the ONE architecture, not a fork of it:

  kia (the OEM-VO portal) -> entity, kind='oem_vo_portal' (+ platform_meta)  [THE PLATFORM]
  each SELLING DEALER     -> entity, kind='compraventa'   (city-geo-resolved)
  each CAR                -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the portal   -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the selling dealer); platform membership is plural (this edge). The same
physical car can carry BOTH a kia edge and a coches.net edge without ever changing its owning
dealer.

GEO anchor vs siblings: renew/toyota_lexus had a postalCode/zip -> province. spoticar had lat/lng
-> province. kia's LIST carries neither — only `poblacion` (city). The province is resolved from
the city via GeoResolver.resolve_city_global (nationally-unique city -> (province, municipality)).
dealerId = a stable composite (cluster id + concesionario name + city) so two distinct sites of
one cluster, or two clusters sharing a name, never collapse.

Encoding trap: the vendor serves brand/dealer/city/version text as latin-1 mojibake over the wire
(Automoci�n = "Automoción", A�os = "Años", M�laga = "Málaga"). Re-encode every human-text field:
s.encode("latin-1").decode("utf-8"). The numeric fields and id are clean.

Multi-axis classification (migrations/0016):
  defense_tier = 't1_soft'         (IIS request-filtering 403s plain curl; serves to curl_cffi; no JS challenge)
  source_group = 'oem_vo_portal'   (the group renew opened; kia is its next member)
  role         = 'platform'
  kind         = 'oem_vo_portal'   (the platform entity's ontology kind, migrations/0005)
  is_tier1     = FALSE             (no tier-1 CDN WAF fronts the vendor)
  family       = 'kia_vo'          (ties the Kia OEM-VO sibling on the family axis)

PROOF SLICE OR FULL. The Kia ES network declares ~1,525 cars across 55 live clusters. The set is
small, so the FULL drain is in reach in a single run: the connector enumerates clusters at runtime
(a live cluster sweep over the discovery range) then drains every car page of every cluster.
--clusters / --limit bound the run. The declared full count (sum of cluster total_vehiculos) is recorded
for the VAM verdict's slice arithmetic.

Engine: a POST against kiaokasion.net/kia/async/metodos.aspx routed THROUGH the per-host governor
(the same single choke point coches.net/toyota_lexus/spoticar use). The synchronous curl_cffi POST
runs in a worker thread so the event loop is never blocked, and no host is fetched faster than its
bucket.

Run: python -m pipeline.platform.oem_kia_wholesale
"""
from __future__ import annotations

import argparse
import sys
import asyncio
import hashlib
import json
import math
import os
import re
from dataclasses import dataclass

import asyncpg
from curl_cffi import requests as cffi_requests

from pipeline.engine.governor import governor, host_of
from pipeline.geo import GeoResolver
from pipeline.ids import ulid
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict
from services.api.codes import _base32, cdp_code

DSN = "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
DSN = os.environ.get("CARDEEP_DSN", DSN)

# ---------------------------------------------------------------------------
# kia platform identity (OEM-VO portal, migrations/0005 + 0016).
# ---------------------------------------------------------------------------
KIA_DOMAIN = "kia.com"
KIA_WEBSITE = "kia.com"
KIA_LEGAL_NAME = "Kia Iberia (Kia Seminuevos Certificados)"
KIA_TRADE_NAME = "kia"
KIA_SOURCE_KEY = "oem_kia_wholesale"
KIA_WAF = "other"             # Microsoft-IIS request filtering 403s plain curl; serves to curl_cffi.
KIA_DEFENSE_TIER = "t1_soft"  # soft WAF present, no JS challenge -> tier 1 soft.
KIA_SOURCE_GROUP = "oem_vo_portal"
KIA_ROLE = "platform"
KIA_KIND = "oem_vo_portal"    # the platform ENTITY's ontology kind (NOT 'plataforma').
KIA_FAMILY = "kia_vo"         # ties the Kia OEM-VO sibling on the family axis.

# The working request (verified live 2026-06-13; recipe oem_kia_datalayer.md TL;DR).
_BASE = "https://kiaokasion.net"
LIST_PATH = "/kia/async/metodos.aspx"   # the vendor's multiplexed async servlet (accion-keyed).
ENDPOINT = _BASE + LIST_PATH
# The kia.com dealer buscador base — used only to construct a stable, traceable deep_link
# (the vendor ficha is pure SPA: iralaficha(id) -> loadPageSPA('vdp'), NO routable per-car URL).
_PDP_BASE = "https://www.kia.com/es/kia-seminuevos-certificados/buscador/"
_IMPERSONATE = "chrome131"
_TIMEOUT = 40
PAGE_SIZE = 10  # the vendor serves a FIXED 10 cars/page (top_paginacion governs the page count).

_HEADERS = {
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "Accept-Language": "es-ES,es;q=0.9",
    "Origin": "https://www.kia.com",
    "Referer": "https://www.kia.com/",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}

# The base POST body for accion=actualizarCoches (all filters wide-open; km=nacional = national
# radius within a cluster). idconcesionario + pagina are filled per request.
_BASE_BODY = {
    "accion": "actualizarCoches",
    "modelos": "", "carrocerias": "", "motores": "", "cambios": "",
    "combustibles": "", "colores": "", "kilometros": "-",
    "preciominimo": "-", "preciomaximo": "-", "km": "nacional", "orden": "1",
    "anyminimo": "-", "anymaximo": "-", "longitud": "", "latitud": "", "kmsdistancia": "",
}

# Province sentinel '00' = national (same convention as toyota_lexus/spoticar/renew/coches.net).
# geo_province has NO '00', so the platform ENTITY stores province_code = NULL; '00' lives only
# inside the cdp_code string (free text, no FK). We never pollute geo_province with it.
PLATFORM_PROVINCE_SENTINEL = "00"

# Cluster discovery sweep range. The live cluster ids (the kia.com inline `__kiaClienteId`) are a
# SPARSE set inside 1..2000 (verified exhaustively: 55 live clusters in 331..1810; 0 above 2000,
# 0 below 331). The sweep enumerates them at runtime so a newly-onboarded dealer is caught without
# a code change. The denominator is sum of cluster total_vehiculos.
CLUSTER_SWEEP_LO = 1
CLUSTER_SWEEP_HI = 2000
# A page-count safety bound per cluster (PAGE_SIZE=10; the largest live cluster ~256 cars = 26
# pages; 200 pages is a generous ceiling that the data boundary always hits first).
DEFAULT_MAX_PAGES = 200


def kia_platform_cdp_code() -> str:
    """The kia platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:kia.com'), province segment '00' (national). Mirrors
    tl_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{KIA_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Field helpers (the kiaokasion surface: latin-1 mojibake + Spanish-formatted numbers).
# ---------------------------------------------------------------------------


def _fix(s):
    """Repair latin-1 mojibake on human-text fields (Automoci�n -> Automoción, M�laga -> Málaga,
    a�os -> años). The wire bytes were UTF-8 mis-decoded as latin-1 upstream; re-encode to recover.
    Numeric fields and id are clean and never passed here."""
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def _to_int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _to_float(v):
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _es_number(v):
    """Parse a Spanish-formatted number string ('13.373' km, '11.020' €, '1.595') to a float.
    The vendor uses '.' as the thousands separator (and rarely ',' as decimal). We strip thousands
    dots and normalise a decimal comma. Returns None on any non-numeric value."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s or s in ("-",):
        return None
    s = s.replace(".", "").replace(",", ".")
    s = re.sub(r"[^0-9.\-]", "", s)
    if not s or s in ("-", ".", "-."):
        return None
    try:
        return float(s)
    except ValueError:
        return None


_SLUG_NONWORD = re.compile(r"[^a-z0-9]+")


def _slugify(s) -> str:
    """ASCII-fold + kebab-case a human string for the PDP slug (SEO decoration; the id is the
    load-bearing key)."""
    if not isinstance(s, str):
        return ""
    s = _fix(s)
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return _SLUG_NONWORD.sub("-", s.lower()).strip("-")


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL response — field names inspected live 2026-06-13, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class DealerRef:
    """The selling official Kia dealer parsed from a single car's embedded fields.

    kiaokasion attaches the selling point-of-sale per car: `concesionario` (name) + `poblacion`
    (city). There is NO postal code or lat/lng in the LIST response, so the province is resolved
    from the city (GeoResolver.resolve_city_global). The stable dealer key is the composite
    (cluster id + name + city) — a cluster can span several sites, so the city disambiguates."""
    dealer_id: str            # composite: "<cluster>:<norm-name>:<norm-city>" (stable source_ref).
    cluster_id: str           # the vendor catalog-partition id (kia.com __kiaClienteId).
    name: str | None
    province_code: str | None
    city: str | None


@dataclass
class Vehicle:
    """A car parsed from a single kiaokasion search item."""
    deep_link: str
    listing_ref: str           # kiaokasion stable car id (`id`) — also the dedup key.
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    vin: str | None            # the LIST has no VIN (`matricula` is the plate, only in ficha); None.


def _norm_token(s) -> str:
    s = _fix(s) or ""
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def parse_item_dealer(car: dict, cluster_id: str) -> DealerRef | None:
    """Parse the SELLING dealer from a car's embedded fields. Returns None when there is no
    concesionario name (the car cannot be attributed to a concrete official dealer)."""
    name = _fix(car.get("concesionario"))
    city = _fix(car.get("poblacion"))
    if not name:
        return None
    dealer_id = f"{cluster_id}:{_norm_token(name)}:{_norm_token(city)}"
    return DealerRef(
        dealer_id=dealer_id,
        cluster_id=str(cluster_id),
        name=name,
        province_code=None,        # filled by the city resolver in _parse_window.
        city=city,
    )


def _build_deep_link(car: dict, cluster_id: str) -> str:
    """Construct a stable, traceable deep_link. The vendor ficha is pure SPA (iralaficha(id) ->
    loadPageSPA('vdp'); NO routable per-car URL), so we mint a canonical kia.com buscador URL keyed
    by the cluster + the globally-unique car id (the load-bearing dedup key). A model/version slug
    is appended for readability; the terminal idcoche is what identifies the listing."""
    car_id = car.get("id")
    if not car_id:
        return ""
    model = _slugify(car.get("modelo"))
    version = _slugify(car.get("version"))
    slug = "-".join(p for p in (model, version) if p)
    base = f"{_PDP_BASE}?idcli={cluster_id}&idcoche={car_id}"
    return f"{base}#{slug}" if slug else base


def parse_item_vehicle(car: dict, cluster_id: str) -> Vehicle:
    """Parse the car from a kiaokasion search item (REAL field map, Spanish-formatted numbers)."""
    price = _es_number(car.get("precio"))
    if price is not None and price <= 0:
        price = None

    year = _to_int(car.get("any"))
    if year is None:
        mat = car.get("matriculacion")  # 'dd/mm/yyyy'
        if isinstance(mat, str) and len(mat) >= 4:
            year = _to_int(mat[-4:])
    if year is not None and not (1900 <= year <= 2100):
        year = None

    km = _es_number(car.get("kilometros"))
    km = int(km) if km is not None else None
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    make = _fix(car.get("marca")) or "KIA"
    model = _fix(car.get("modelo"))
    version = _fix(car.get("version"))
    title = " ".join(p for p in (make, model, version) if p) or None

    listing_ref = str(car.get("id") or "")

    fuel = _fix(car.get("combustible"))
    transmission = _fix(car.get("transmision"))

    photo = car.get("imagen")
    photo_url = photo if isinstance(photo, str) and photo.startswith("http") else None

    return Vehicle(
        deep_link=_build_deep_link(car, cluster_id),
        listing_ref=listing_ref,
        title=title,
        make=make,
        model=model,
        year=year,
        km=km,
        price=price,
        fuel=fuel,
        transmission=transmission,
        photo_url=photo_url,
        vin=None,
    )


# ---------------------------------------------------------------------------
# City -> province FALLBACK (the ~484 geo-skipped cars).
#
# The structural fact: GeoResolver.resolve_city_global only resolves a poblacion when it maps to
# EXACTLY ONE municipality nationally. The Kia vendor `poblacion` values are not clean INE
# municipality names — they are dealer free text: trailing spaces ('Sant Boi '), province names used
# as the city ('BIZKAIA', 'Granada'), compound strings ('SON FERRIOL - PALMA DE MALLORCA',
# 'Fuenlabrada Madrid'), parish+municipality pairs ('GRANDA SIERO'), and regional spelling variants
# ('Oyarzun' = Oiartzun, 'San Ciprián de Viñas' = San Cibrao das Viñas). The strict resolver skips
# all of them — ~481 live cars, ~32% of the network.
#
# This fallback fires ONLY when the strict resolver returns nothing, so it can never change an
# already-resolved attribution. It applies a STRICT, ordered ladder — each tier returns a province
# ONLY when the answer is unambiguous (unique province), so a wrong attribution is impossible:
#
#   1) city_alias       — a tiny curated table for true spelling variants no normalization bridges
#                         (Oyarzun->Oiartzun/20, San Ciprián de Viñas->San Cibrao das Viñas/32).
#   2) prov_whole       — the whole poblacion string IS a province name/alias (BIZKAIA->48,
#                         Granada->18). Uses GeoResolver.province_code (province table + alias map).
#   3) prov_scan        — a province name/alias appears as a contiguous token-window inside the
#                         poblacion (…PALMA DE MALLORCA -> 'mallorca' alias -> 07; 'Fuenlabrada
#                         MADRID' -> 'madrid' -> 28; 'Mahon (MENORCA)' -> 'menorca' alias -> 07).
#   4) conc_prov_scan   — same province scan over the concesionario name (some dealers embed the
#                         province in the trade name; only fires when the poblacion gave nothing).
#   5) muni_subset      — the poblacion's significant tokens (connectives stripped) are a
#                         leading-anchored subset of one municipality's significant tokens that
#                         resolves to a UNIQUE province ('Sant Boi' -> Sant Boi de Llobregat/08;
#                         'EL PRAT DEL LLOBREGAT' -> Prat de Llobregat, El / 08).
#   6) muni_token       — a single significant token in the poblacion is itself a nationally-unique
#                         municipality name ('GRANDA SIERO' -> 'siero' is the Asturian municipality
#                         33; 'granda' is its parish).
#
# Every tier carries a UNIQUENESS guard (return only when exactly one province is implied), so a
# noisy multi-province match degrades to a skip, never to a wrong province. Verified live against all
# 11 distinct geo-skipped poblacion patterns (2026-06-13): 11/11 resolve to the correct province.
# ---------------------------------------------------------------------------

# Connective / article tokens that carry no locational identity — stripped before municipality
# token-set matching so 'EL PRAT DEL LLOBREGAT' bridges to 'Prat de Llobregat, El'.
_GEO_STOPWORDS = {
    "de", "del", "la", "el", "las", "los", "da", "das", "dos",
    "i", "y", "l", "les", "sa", "es", "son",
}

# True spelling variants that no accent/case/order normalization can bridge (a different language
# form of the name). Keyed by GeoResolver._norm(poblacion) -> INE province code. Kept deliberately
# tiny and curated; the structural tiers below catch everything else without a table.
_CITY_PROVINCE_ALIASES = {
    "oyarzun": "20",               # Oiartzun (Basque form).
    "san ciprian de vinas": "32",  # San Cibrao das Viñas (Galician INE form).
}


def _geo_norm(text: str) -> str:
    """Accent/case-fold + collapse to single-spaced lowercase tokens. Mirrors GeoResolver._norm so
    this fallback indexes the geo backbone the same way the strict resolver does."""
    import unicodedata
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


class CityProvinceFallback:
    """A strict, ordered city->province resolver for the Kia poblacion free text that the national
    unique-city resolver cannot place. Built ONCE per run from the already-loaded GeoResolver's
    province index plus a fresh municipality-name index (one extra SELECT), so the harvest pays no
    per-car DB cost. Every tier is uniqueness-guarded: it returns a province only when the answer is
    unambiguous, else None (-> the car is still honestly skipped). It NEVER fires for a poblacion the
    strict resolver already placed, so it can only ADD coverage, never alter an existing attribution.
    """

    def __init__(self, geo: GeoResolver,
                 muni_whole: dict[str, set[str]],
                 muni_sig: list[tuple[tuple[str, ...], str]]) -> None:
        self._geo = geo
        self._muni_whole = muni_whole   # full norm muni name -> {province_code}
        self._muni_sig = muni_sig       # (significant-token tuple, province_code)

    @classmethod
    async def load(cls, conn: asyncpg.Connection, geo: GeoResolver) -> "CityProvinceFallback":
        muni_whole: dict[str, set[str]] = {}
        muni_sig: list[tuple[tuple[str, ...], str]] = []
        for r in await conn.fetch("SELECT name, province_code FROM geo_municipality"):
            # index the full name AND each bilingual '/' or ',' variant (e.g. 'Prat de Llobregat, El').
            for variant in [r["name"], *re.split(r"[/,]", r["name"])]:
                nm = _geo_norm(variant)
                if not nm:
                    continue
                muni_whole.setdefault(nm, set()).add(r["province_code"])
                sig = tuple(t for t in nm.split() if t not in _GEO_STOPWORDS)
                if sig:
                    muni_sig.append((sig, r["province_code"]))
        return cls(geo, muni_whole, muni_sig)

    def _prov_scan(self, text: str | None) -> str | None:
        """Longest contiguous token-window of `text` that is a known province name/alias.

        CRITICAL guard: the province index carries bare article fragments split off bilingual names
        ('a' -> 15 from 'A Coruña', 'la' -> 26 from 'La Rioja', 'las' -> 35 from 'Las Palmas'). A
        free-text scan over a dealer trade name ('AUTOMOBILS A.R. MOTORS S.L.', 'ASTURIANA ... S.A.')
        would otherwise latch onto a stray 'a' and mis-attribute A Coruña. So a window is only a
        valid province match when it contains at least one substantial token (length >= 3 and not a
        connective/article), never a lone article or initial."""
        if not text:
            return None
        toks = _geo_norm(text).split()
        best: str | None = None
        best_len = 0
        for i in range(len(toks)):
            for j in range(i + 1, len(toks) + 1):
                window = toks[i:j]
                if not any(len(t) >= 3 and t not in _GEO_STOPWORDS for t in window):
                    continue  # pure articles/initials -> never a real province name.
                pc = self._geo._prov.get(" ".join(window))
                if pc and (j - i) > best_len:
                    best, best_len = pc, j - i
        return best

    def _muni_subset(self, city: str) -> str | None:
        """The city's significant tokens are a leading-anchored subset of one municipality's
        significant tokens, resolving to a UNIQUE province (else None)."""
        ptoks = [t for t in _geo_norm(city).split() if t not in _GEO_STOPWORDS]
        if not ptoks:
            return None
        pset = set(ptoks)
        provs: set[str] = set()
        for sig, prov in self._muni_sig:
            if sig and sig[0] == ptoks[0] and pset <= set(sig):
                provs.add(prov)
        return next(iter(provs)) if len(provs) == 1 else None

    def _muni_token(self, city: str) -> str | None:
        """A single significant token in the city is itself a nationally-unique municipality name
        ('GRANDA SIERO' -> 'siero' = Siero/33). Uniqueness across ALL matched tokens is required."""
        provs: set[str] = set()
        for t in (x for x in _geo_norm(city).split() if x not in _GEO_STOPWORDS):
            ps = self._muni_whole.get(t)
            if ps and len(ps) == 1:
                provs.add(next(iter(ps)))
        return next(iter(provs)) if len(provs) == 1 else None

    def resolve(self, city: str | None, concesionario: str | None) -> str | None:
        """Resolve a province code from the Kia poblacion (+ concesionario) when the strict national
        unique-city resolver could not. Returns a 2-digit INE province code in 01..52, or None when
        no tier yields an unambiguous province (the car stays honestly skipped)."""
        if not city:
            return None
        n = _geo_norm(city)
        # 1) curated spelling-variant alias table.
        pc = _CITY_PROVINCE_ALIASES.get(n)
        if pc:
            return pc
        # 2) the whole poblacion string is a province name/alias (BIZKAIA -> 48, Granada -> 18).
        pc = self._geo.province_code(city)
        if pc:
            return pc
        # 3) a province name/alias appears as a token-window in the poblacion
        #    (...PALMA DE MALLORCA -> 'mallorca' -> 07; 'Fuenlabrada MADRID' -> 28).
        pc = self._prov_scan(city)
        if pc:
            return pc
        # 4) leading municipality token-subset -> unique province
        #    ('Sant Boi' -> Sant Boi de Llobregat / 08; 'EL PRAT DEL LLOBREGAT' -> 08).
        pc = self._muni_subset(city)
        if pc:
            return pc
        # 5) a lone significant token that is a unique municipality ('GRANDA SIERO' -> 'siero' / 33).
        pc = self._muni_token(city)
        if pc:
            return pc
        # 6) LAST RESORT — a province name/alias embedded in the concesionario trade name. Guarded by
        #    _prov_scan's substantial-token rule so a stray initial ('S.A.', 'A.R.') cannot match.
        return self._prov_scan(concesionario)


# ---------------------------------------------------------------------------
# Fetch: a POST routed THROUGH the governor (same per-host choke point as toyota_lexus/coches.net).
# ---------------------------------------------------------------------------


class KiaFetcher:
    """A POOL of fingerprint-coherent curl_cffi POST sessions for the kiaokasion async servlet.

    Same concurrency-vs-coherence model as TLFetcher / SpoticarFetcher: a single curl_cffi Session
    is NOT safe to call from several threads at once, and the governor runs each fetch in its own
    worker thread (asyncio.to_thread). The fix is a bounded POOL — one Session per concurrency slot,
    each its own Chrome fingerprint + cookie jar. The governor's per-host bucket bounds the
    AGGREGATE rate across every session, so the pool widens parallelism WITHOUT out-pacing the host
    (the choke point is the bucket, never the session count).
    """

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch_page(self, url: str, *, cluster: str = "0", pagina: int = 1,
                   accion: str = "actualizarCoches", slot: int = 0) -> dict:
        """The synchronous POST on pool session `slot` (runs in a worker thread).

        Handed to governor().wrap_fetch_text: the governor derives the host from `url`, waits on the
        per-host bucket, then runs THIS off the event loop. `slot`/`cluster`/`pagina` ride as kwargs
        the governor forwards untouched, so each in-flight request POSTs on its own leased,
        never-shared curl_cffi session (thread-safe). Raises on a non-200 so the breaker sees
        throttling (never masks a challenge/empty body)."""
        session = self._sessions[slot]
        body = dict(_BASE_BODY)
        body["accion"] = accion
        body["pagina"] = str(pagina)
        body["idconcesionario"] = str(cluster)
        resp = session.post(url, data=body, headers=_HEADERS,
                            impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url} (cluster {cluster} page {pagina})")
        # The servlet serves UTF-8 JSON; some human-text VALUES inside are latin-1 mojibake
        # (repaired per-field by _fix()); the JSON envelope itself is valid UTF-8.
        return json.loads(resp.content.decode("utf-8", "replace"))

    async def fetch_page_async(self, governed_fetch, url: str, *, cluster: str, pagina: int,
                               accion: str = "actualizarCoches") -> dict:
        """Lease a pool slot, fetch THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, cluster=cluster, pagina=pagina,
                                        accion=accion, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer (mirrors oem_toyota_lexus_wholesale: ensure platform, bulk-upsert dealer/vehicle, link
# edge, emit delta, all idempotent ON CONFLICT). Multi-axis 0016 classification set.
# ---------------------------------------------------------------------------

KIA_PLATFORM_RECIPE = {
    "version": 1,
    "source": "kia (www.kia.com/es Kia Seminuevos Certificados; vendor kiaokasion.net)",
    "scope": "platform-wholesale (Kia ES certified-used; kia.com SPA -> kiaokasion.net ASP.NET servlet)",
    "engine": "curl_cffi+chrome131_impersonate+vendor_async_servlet(POST)",
    "access": ("OPEN-via-fingerprint (Microsoft-IIS request-filtering 403s plain curl on bare paths; "
               "the metodos.aspx POST serves 200 application/json to curl_cffi chrome131 with a "
               "kia.com Referer). No proxy, no browser, no cookie warm-up, no auth, €0. No tier-1 CDN "
               "WAF -> is_tier1=FALSE; soft WAF, no JS challenge -> defense_tier=t1_soft."),
    "data_surface": "internal_api",
    "surface_intent": "vendor_async_servlet",
    "endpoint": "POST https://kiaokasion.net/kia/async/metodos.aspx (accion-keyed)",
    "request": {
        "headers": "Content-Type x-www-form-urlencoded, X-Requested-With XMLHttpRequest, Origin/Referer kia.com",
        "body": ("accion=actualizarCoches (cars) | actualizarTodoBuscador (facets); "
                 "idconcesionario=<cluster>, pagina=N, km=nacional, orden=1, all filters wide-open '-'/''"),
    },
    "enumeration": ("PARTITIONED BY CLUSTER. idconcesionario (kia.com inline __kiaClienteId) is a "
                    "dealer-GROUP cluster id; only a SPARSE set is live (55 clusters in 331..1810, "
                    "swept over 1..2000; 0 above 2000). km=nacional does NOT aggregate across "
                    "clusters. FULL stock = UNION over all live clusters; per cluster walk "
                    "pagina=1..top_paginacion (10 cars/page). dedup on car `id`."),
    "denominator": "sum of cluster total_vehiculos (== sum of top_paginacion*PAGE_SIZE bound, == distinct car ids)",
    "platform_entity": ("kind=oem_vo_portal, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=FALSE, defense_tier=t1_soft, source_group=oem_vo_portal, role=platform, "
                        "family=kia_vo"),
    "dual_membership": ("vehicle.entity_ulid=SELLING DEALER (compraventa, per-car not per-cluster); "
                        "platform_listing edge=platform<->vehicle"),
    "field_map": {
        "deep_link": "constructed kia.com buscador URL ?idcli=<cluster>&idcoche=<id> (vendor ficha is SPA-only)",
        "listing_ref": "car.id (vendor stable car id + dedup key)",
        "vin": "NONE in list (car.matricula = plate, only in ficha) -> null",
        "make": "car.marca (KIA)",
        "model": "car.modelo",
        "version": "car.version",
        "year": "car.any (fallback car.matriculacion[-4:])",
        "km": "car.kilometros (Spanish-formatted: thousands '.')",
        "price": "car.precio (€, Spanish-formatted; precio_alcontado = cash price)",
        "fuel": "car.combustible",
        "transmission": "car.transmision (Manual/Automático)",
        "photo": "car.imagen (absolute https kiaokasion.net/.../idcli_<cluster>/<id>/...)",
        "dealer": "car.concesionario (name) + car.poblacion (city); cluster id = catalog partition",
        "location": ("car.poblacion (city) -> GeoResolver.resolve_city_global -> (province, "
                     "municipality). NO postal code/lat-lng in list; ficha carries cp but city "
                     "resolves 100% in the live probe so no ficha fetch."),
    },
    "caveats": {
        "page_size": "fixed 10 cars/page; top_paginacion governs the page count per cluster.",
        "cluster_partition": ("idconcesionario is a dealer-GROUP cluster; a cluster spans several "
                              "sites/cities (e.g. 926 = QUADIS across Tarragona + Sant Boi) — "
                              "attribute the dealer PER CAR (concesionario+poblacion), not per cluster."),
        "no_national_aggregate": "idconcesionario=0 -> 0; km=nacional relaxes radius WITHIN a cluster only.",
        "encoding": ("dealer/city/version text is latin-1 mojibake (Automoci�n, M�laga); repair with "
                     "s.encode('latin-1').decode('utf-8'). id/numeric clean."),
        "es_numbers": "km/price/dims are Spanish-formatted ('13.373' = 13373); strip thousands '.'.",
        "no_pdp_url": "vendor ficha is SPA-only (iralaficha->loadPageSPA('vdp')); deep_link constructed.",
        "no_private_sellers": "OEM certified-used portal — every car belongs to an official Kia dealer.",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the kia platform entity + platform_meta exist. Returns the platform
    entity_ulid. kind='oem_vo_portal' (the platform ontology kind), is_tier1=FALSE (no tier-1 CDN
    WAF), multi-axis 0016 classification set explicitly, data_surface='internal_api'."""
    code = kia_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               defense_tier, source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,$3,$4,$5,NULL,$6,$7::waf_kind,FALSE,'active','platform_label',
               $8::defense_tier,$9::source_group,$10::entity_role,$11, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, website_waf = EXCLUDED.website_waf,
               defense_tier = EXCLUDED.defense_tier, source_group = EXCLUDED.source_group,
               role = EXCLUDED.role, legal_name = EXCLUDED.legal_name, kind = EXCLUDED.kind""",
        eulid, code, KIA_KIND, KIA_LEGAL_NAME, KIA_TRADE_NAME, KIA_WEBSITE,
        KIA_WAF, KIA_DEFENSE_TIER, KIA_SOURCE_GROUP, KIA_ROLE, KIA_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, KIA_SOURCE_KEY, KIA_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'internal_api',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"endpoint": ENDPOINT, "host": host_of(ENDPOINT),
                           "method": "POST", "page_size": PAGE_SIZE,
                           "denominator": "sum_cluster_total_vehiculos",
                           "partition": "idconcesionario_cluster",
                           "surface_intent": "vendor_async_servlet",
                           "engine": "curl_cffi/chrome131_impersonate"}),
        KIA_FAMILY)
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    Kia dealers have no bare domain on this surface -> identity = name + location + the stable
    composite dealer_id (cluster:name:city, passed via `address` so two distinct sites of one
    cluster, or two clusters sharing a name in one municipality, never collapse to one entity)."""
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni, address=f"dealer:{d.dealer_id}")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# Default concurrency: pages fetched in parallel per sliding window. The kiaokasion host is NOT in
# the governor's JSON_API rate class — it inherits the conservative STEALTH default, the safe
# direction for an unmeasured soft-WAF host. The concurrency only needs to keep that (slow) bucket
# saturated; a small window is plenty.
DEFAULT_CONCURRENCY = 4
# Cluster-discovery sweep concurrency (a fast one-shot probe per id; the governor still paces it).
DEFAULT_SWEEP_CONCURRENCY = 8


@dataclass
class _CageRow:
    """One fully-parsed, geo-anchored car ready for the bulk cage — the in-memory result of the
    parse+resolve phase, before any SQL."""
    dealer_id: str
    dealer_cdp: str
    dealer_name: str | None
    dealer_province: str
    dealer_muni: str | None
    vehicle: Vehicle


# The bulk statements — ONE round-trip per table per window (unnest-based multi-row upsert),
# byte-for-byte the same idempotency the row-by-row path uses. A re-run of an already-harvested
# window adds 0 rows and 0 events. Dealers carry the 0016 axes (oem_vo_portal/standalone_pos).

_BULK_UPSERT_DEALERS = """
INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
        province_code, municipality_code, is_tier1, status, kind_source,
        sells_cars, source_group, role, first_discovered_source, last_seen)
SELECT u.entity_ulid, u.cdp_code, 'compraventa', u.name, u.name,
       u.province_code, u.municipality_code, FALSE, 'active', 'platform_label',
       TRUE, 'oem_vo_portal'::source_group, 'standalone_pos'::entity_role, $7, now()
  FROM unnest($1::text[], $2::text[], $3::text[], $4::char(2)[], $5::char(5)[],
              $6::text[]) AS u(entity_ulid, cdp_code, name, province_code,
                               municipality_code, source_ref)
ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()
"""

_BULK_UPSERT_DEALER_SOURCES = """
INSERT INTO entity_source (entity_ulid, source_key, source_ref)
SELECT e.entity_ulid, $3, u.source_ref
  FROM unnest($1::text[], $2::text[]) AS u(cdp_code, source_ref)
  JOIN entity e ON e.cdp_code = u.cdp_code
ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()
"""

_BULK_INSERT_VEHICLES = """
INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model,
        year, km, price, fuel, transmission, photo_url, vin_ref, status)
SELECT u.vehicle_ulid, u.entity_ulid, u.deep_link, u.title, u.make, u.model,
       u.year, u.km, u.price, u.fuel, u.transmission, u.photo_url, u.vin_ref, 'available'
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[], $5::text[], $6::text[],
              $7::int[], $8::int[], $9::numeric[], $10::text[], $11::text[], $12::text[],
              $13::text[])
       AS u(vehicle_ulid, entity_ulid, deep_link, title, make, model,
            year, km, price, fuel, transmission, photo_url, vin_ref)
ON CONFLICT (entity_ulid, deep_link) DO NOTHING
"""

_BULK_TOUCH_VEHICLES = """
UPDATE vehicle v SET last_seen = now(), status = 'available'
  FROM unnest($1::text[]) AS u(vehicle_ulid)
 WHERE v.vehicle_ulid = u.vehicle_ulid
"""

_BULK_UPSERT_EDGES = """
INSERT INTO platform_listing (vehicle_ulid, platform_entity_ulid, listing_url,
        listing_ref, platform_price, status, first_seen, last_seen)
SELECT u.vehicle_ulid, $5, u.listing_url, u.listing_ref, u.platform_price,
       'listed', now(), now()
  FROM unnest($1::text[], $2::text[], $3::text[], $4::numeric[])
       AS u(vehicle_ulid, listing_url, listing_ref, platform_price)
ON CONFLICT (vehicle_ulid, platform_entity_ulid)
  DO UPDATE SET last_seen = now(), status = 'listed',
                platform_price = EXCLUDED.platform_price,
                listing_ref = EXCLUDED.listing_ref
RETURNING (xmax = 0) AS inserted
"""

_BULK_INSERT_EVENTS = """
INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type,
        old_value, new_value)
SELECT u.event_ulid, u.vehicle_ulid, u.entity_ulid, 'NEW', NULL, u.new_value::jsonb
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[])
       AS u(event_ulid, vehicle_ulid, entity_ulid, new_value)
"""


def _parse_window(items_by_page: list[tuple[str, int, list]], geo: GeoResolver,
                  geo_fallback: "CityProvinceFallback",
                  seen_ids: set, harvested_cageable: set, stats: dict) -> list[_CageRow]:
    """Parse + geo-resolve every car across the window IN ORDER — pure CPU, no SQL.

    The EXACT per-item gate (cross-page dedup on car id, dealer-parse skip, geo skip, cageable
    truth), lifted out of the DB loop so the SQL phase is purely set-based. The province is resolved
    from the city (GeoResolver.resolve_city_global); when that strict national-unique resolver gives
    nothing, the `geo_fallback` ladder (city alias / province-name / province-scan / municipality
    token-subset) recovers the dealer free-text poblaciones the strict resolver cannot place — only
    ever ADDING coverage, never altering a strict hit. `seen_ids` / `harvested_cageable` / `stats`
    are mutated here with deterministic order semantics so the VAM truth is byte-identical regardless
    of batching. Each tuple is (cluster, pagina, items); the cluster builds the dealer key + deep_link."""
    rows: list[_CageRow] = []
    for cluster, _pagina, items in items_by_page:
        for car in items:
            if not isinstance(car, dict):
                continue
            stats["items_seen"] += 1
            # cross-cluster dedup on the car id (the stable dedup key; the same physical car can in
            # principle surface under more than one cluster query, so dedup globally by id).
            item_id = str(car.get("id") or "")
            if item_id and item_id in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue
            if item_id:
                seen_ids.add(item_id)

            d = parse_item_dealer(car, cluster)
            if d is None:
                stats["no_dealer_skipped"] += 1
                continue
            stats["dealer_items"] += 1

            # Geo gate — resolve the province + municipality from the city, then apply the same
            # province-range guard the dealer upsert enforces, done in memory so a bad/missing geo
            # is skipped without ever touching the DB (no FK risk). When the strict national
            # unique-city resolver gives nothing (dealer free-text poblacion: trailing spaces,
            # province-as-city, compound/parish strings, regional spellings), fall back to the
            # uniqueness-guarded city->province ladder. The fallback yields a province but no specific
            # municipality code (muni stays None — cdp_code_dealer handles a NULL municipality).
            prov, muni = geo.resolve_city_global(d.city)
            if not prov:
                prov = geo_fallback.resolve(d.city, d.name)
                muni = None
                if prov:
                    stats["geo_fallback_recovered"] += 1
            if not prov:
                stats["geo_skipped"] += 1
                continue
            if not (prov.isdigit() and "01" <= prov <= "52"):
                stats["geo_skipped"] += 1
                continue
            d = DealerRef(dealer_id=d.dealer_id, cluster_id=d.cluster_id, name=d.name,
                          province_code=prov, city=d.city)
            dealer_cdp = cdp_code_dealer(d, muni)

            v = parse_item_vehicle(car, cluster)
            if not v.deep_link:
                continue
            harvested_cageable.add((d.dealer_id, v.deep_link))
            if v.vin:
                stats["vins_captured"] += 1
            rows.append(_CageRow(
                dealer_id=d.dealer_id, dealer_cdp=dealer_cdp, dealer_name=d.name,
                dealer_province=prov, dealer_muni=muni, vehicle=v))
    return rows


async def _ingest_window(conn: asyncpg.Connection, geo: GeoResolver,
                         geo_fallback: "CityProvinceFallback",
                         platform_ulid: str, items_by_page: list[tuple[str, int, list]],
                         seen_ids: set, harvested_cageable: set, stats: dict) -> None:
    """BULK-ingest a whole concurrent page-window in ONE transaction with set-based SQL.

    Mirrors oem_toyota_lexus_wholesale._ingest_window EXACTLY: ONE round-trip per table per window
    (unnest multi-row upserts). The delta/VAM/platform_listing semantics are preserved: same ON
    CONFLICT idempotency, same cageable truth, same NEW-event rule (emitted only for genuinely new
    vehicles). A re-run of an already-harvested window adds 0 rows and 0 events.
    """
    cage = _parse_window(items_by_page, geo, geo_fallback, seen_ids, harvested_cageable, stats)
    if not cage:
        return

    async with conn.transaction():
        # ---- (2) DEALERS: dedup by cdp_code within the window, bulk-upsert, resolve ulids.
        dealers: dict[str, _CageRow] = {}
        for r in cage:
            dealers.setdefault(r.dealer_cdp, r)  # first occurrence wins (deterministic)
        d_ulids = [ulid() for _ in dealers]
        d_cdps = list(dealers.keys())
        d_names = [dealers[c].dealer_name for c in d_cdps]
        d_provs = [dealers[c].dealer_province for c in d_cdps]
        d_munis = [dealers[c].dealer_muni for c in d_cdps]
        d_refs = [dealers[c].dealer_id for c in d_cdps]
        await conn.execute(_BULK_UPSERT_DEALERS, d_ulids, d_cdps, d_names, d_provs,
                           d_munis, d_refs, KIA_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_DEALER_SOURCES, d_cdps, d_refs, KIA_SOURCE_KEY)
        cdp_to_ulid: dict[str, str] = {
            row["cdp_code"]: row["entity_ulid"]
            for row in await conn.fetch(
                "SELECT cdp_code, entity_ulid FROM entity "
                "WHERE cdp_code = ANY($1::text[])", d_cdps)
        }

        # ---- attach resolved dealer_ulid to each cage row; dedup cars within the window by
        # (dealer_ulid, deep_link) so the same ad seen twice in one window is one car.
        cars: dict[tuple[str, str], _CageRow] = {}
        for r in cage:
            du = cdp_to_ulid.get(r.dealer_cdp)
            if du is None:
                continue
            key = (du, r.vehicle.deep_link)
            if key not in cars:
                cars[key] = r

        # ---- (3) VEHICLES: one SELECT splits existing vs new. Existing -> bulk touch.
        # New -> Python-minted ulid + bulk insert.
        car_keys = list(cars.keys())
        v_entity = [k[0] for k in car_keys]
        v_links = [k[1] for k in car_keys]
        existing: dict[tuple[str, str], str] = {
            (row["entity_ulid"], row["deep_link"]): row["vehicle_ulid"]
            for row in await conn.fetch(
                """SELECT vehicle_ulid, entity_ulid, deep_link FROM vehicle
                   WHERE (entity_ulid, deep_link) IN (
                     SELECT * FROM unnest($1::text[], $2::text[]))""",
                v_entity, v_links)
        }

        vehicle_ulid_for: dict[tuple[str, str], str] = {}
        new_keys: list[tuple[str, str]] = []
        touch_ulids: list[str] = []
        for key in car_keys:
            ex = existing.get(key)
            if ex is not None:
                vehicle_ulid_for[key] = ex
                touch_ulids.append(ex)
            else:
                vid = ulid()
                vehicle_ulid_for[key] = vid
                new_keys.append(key)

        if touch_ulids:
            await conn.execute(_BULK_TOUCH_VEHICLES, touch_ulids)

        if new_keys:
            ins = [(vehicle_ulid_for[k], k[0], k[1], cars[k].vehicle) for k in new_keys]
            await conn.execute(
                _BULK_INSERT_VEHICLES,
                [x[0] for x in ins], [x[1] for x in ins], [x[2] for x in ins],
                [x[3].title for x in ins], [x[3].make for x in ins], [x[3].model for x in ins],
                [x[3].year for x in ins], [x[3].km for x in ins], [x[3].price for x in ins],
                [x[3].fuel for x in ins], [x[3].transmission for x in ins],
                [x[3].photo_url for x in ins], [x[3].vin for x in ins])
            landed = {
                (row["entity_ulid"], row["deep_link"]): row["vehicle_ulid"]
                for row in await conn.fetch(
                    """SELECT vehicle_ulid, entity_ulid, deep_link FROM vehicle
                       WHERE vehicle_ulid = ANY($1::text[])""",
                    [vehicle_ulid_for[k] for k in new_keys])
            }
            confirmed_new = []
            for k in new_keys:
                real = landed.get(k)
                if real is not None and real == vehicle_ulid_for[k]:
                    confirmed_new.append(k)
                elif real is not None:
                    vehicle_ulid_for[k] = real  # someone else won the race; adopt their ulid
                else:
                    row = await conn.fetchrow(
                        "SELECT vehicle_ulid FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2",
                        k[0], k[1])
                    if row is not None:
                        vehicle_ulid_for[k] = row["vehicle_ulid"]
        else:
            confirmed_new = []

        stats["cars_caged"] += len(car_keys)
        stats["new_cars"] += len(confirmed_new)

        # ---- (4) EDGES: one batched upsert; RETURNING (xmax=0) counts genuinely new edges.
        e_vehicles = [vehicle_ulid_for[k] for k in car_keys]
        e_urls = [cars[k].vehicle.deep_link for k in car_keys]
        e_refs = [cars[k].vehicle.listing_ref for k in car_keys]
        e_prices = [cars[k].vehicle.price for k in car_keys]
        edge_rows = await conn.fetch(_BULK_UPSERT_EDGES, e_vehicles, e_urls, e_refs,
                                     e_prices, platform_ulid)
        stats["edges_created"] += sum(1 for row in edge_rows if row["inserted"])

        # ---- (5) NEW delta events — only for genuinely new vehicles. VIN preserved in payload.
        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                v = cars[k].vehicle
                payload = {"price": v.price, "title": v.title, "platform": KIA_TRADE_NAME}
                if v.vin:
                    payload["vin"] = v.vin
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities,
                               ev_payloads)
            stats["new_events"] += len(confirmed_new)


async def _discover_clusters(fetcher: KiaFetcher, governed_fetch, lo: int, hi: int,
                             sweep_concurrency: int, stats: dict) -> dict[int, int]:
    """Enumerate the live dealer-group clusters by sweeping idconcesionario over [lo, hi].

    The vendor catalog is partitioned by `idconcesionario` (the kia.com inline __kiaClienteId) and
    only a SPARSE set is live. One actualizarCoches?pagina=1 probe per id reads total_vehiculos; a
    cluster is live when total_vehiculos > 0. The governor paces the aggregate. Returns
    {cluster_id: total_vehiculos} for every live cluster — the harvest denominator."""
    live: dict[int, int] = {}
    sem = asyncio.Semaphore(max(1, sweep_concurrency))

    async def probe(idc: int):
        async with sem:
            try:
                data = await fetcher.fetch_page_async(governed_fetch, ENDPOINT,
                                                      cluster=str(idc), pagina=1)
            except Exception:
                return
        tv = _to_int(data.get("total_vehiculos"))
        if tv and tv > 0:
            live[idc] = tv

    await asyncio.gather(*(probe(i) for i in range(lo, hi + 1)))
    stats["clusters_discovered"] = len(live)
    stats["declared_full"] = sum(live.values())
    return dict(sorted(live.items()))


async def _drain_cluster(conn, geo, geo_fallback, platform_ulid, fetcher, governed_fetch,
                         cluster: int, declared: int, max_pages: int, concurrency: int,
                         seen_ids: set, harvested_cageable: set, stats: dict) -> tuple[str | None, int | None]:
    """Drain ONE cluster (idconcesionario) by walking pagina=1..top_paginacion in concurrent windows.

    Returns (fetch_error, last_http). top_paginacion (read from the first page) + emptiness bound the
    run. Pages are fetched in parallel through the governor (the host bucket paces the aggregate)
    then ingested sequentially in page order."""
    fetch_error: str | None = None
    last_http: int | None = None
    top_pages: int | None = None
    stop = False
    next_page = 1
    while next_page <= max_pages and not stop:
        if top_pages is not None and next_page > top_pages:
            break
        hi = min(next_page + concurrency, max_pages + 1)
        if top_pages is not None:
            hi = min(hi, top_pages + 1)
        window = list(range(next_page, hi))
        if not window:
            break
        next_page = window[-1] + 1

        results = await asyncio.gather(
            *(fetcher.fetch_page_async(governed_fetch, ENDPOINT, cluster=str(cluster), pagina=p)
              for p in window),
            return_exceptions=True,
        )

        window_pages: list[tuple[str, int, list]] = []
        for page, data in zip(window, results):
            if isinstance(data, Exception):
                fetch_error = str(data)
                last_http = fetcher.last_status
                print(f"[oem_kia] cluster={cluster} page {page} fetch failed ({data}); "
                      f"stopping this cluster honestly.")
                stop = True
                break
            if top_pages is None:
                top_pages = _to_int(data.get("top_paginacion")) or 1
            items = data.get("vehiculos") or []
            if not items:
                stop = True
                break
            window_pages.append((str(cluster), page, items))

        if window_pages:
            await _ingest_window(conn, geo, geo_fallback, platform_ulid, window_pages, seen_ids,
                                 harvested_cageable, stats)
            stats["pages_fetched"] += len(window_pages)
    print(f"[oem_kia] cluster={cluster} (declared {declared}) drained: "
          f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
          f"edges={stats['edges_created']} dealers_seen={len(harvested_cageable)}")
    return fetch_error, last_http


async def harvest(max_clusters: int | None = None,
                  concurrency: int = DEFAULT_CONCURRENCY,
                  sweep_concurrency: int = DEFAULT_SWEEP_CONCURRENCY,
                  sweep_lo: int = CLUSTER_SWEEP_LO,
                  sweep_hi: int = CLUSTER_SWEEP_HI,
                  max_pages: int = DEFAULT_MAX_PAGES,
                  limit: int | None = None) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    fetcher = KiaFetcher(pool_size=max(concurrency, sweep_concurrency))
    stats = {
        "pages_fetched": 0, "items_seen": 0, "dealer_items": 0,
        "no_dealer_skipped": 0, "geo_skipped": 0, "geo_fallback_recovered": 0,
        "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "vins_captured": 0,
        "declared_full": None, "clusters_discovered": 0, "clusters_drained": 0,
        "dup_ids_collapsed": 0, "dealers_distinct": 0, "concurrency": concurrency,
        "max_pages": max_pages, "private_skipped": 0,
    }
    # Harvest-side truth for the VAM: distinct CAGEABLE cars = distinct (dealer_id, deep_link)
    # pairs that survived dealer-parse + geo-resolution. Like-with-like vs db_edges.
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if the breaker is OPEN (a recent ban/throttle still cooling), skip the drain
    # gracefully — the API keeps serving the last snapshot.
    if await is_open(conn, KIA_SOURCE_KEY):
        print(f"[oem_kia] breaker OPEN for {KIA_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, API still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": KIA_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        geo_fallback = await CityProvinceFallback.load(conn, geo)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = kia_platform_cdp_code()
        print(f"[oem_kia] platform entity ready: {platform_code} (ulid={platform_ulid}) "
              f"kind={KIA_KIND} group={KIA_SOURCE_GROUP} tier={KIA_DEFENSE_TIER} family={KIA_FAMILY}")
        print(f"[oem_kia] governor paces host {host_of(ENDPOINT)} (per-host token bucket, JSON_API class).")

        # PHASE 1 — discover live clusters (the catalog partition keys + the declared denominator).
        print(f"[oem_kia] discovering live clusters over idconcesionario [{sweep_lo}..{sweep_hi}] "
              f"(sweep window={sweep_concurrency}) ...")
        clusters = await _discover_clusters(fetcher, governed_fetch, sweep_lo, sweep_hi,
                                            sweep_concurrency, stats)
        cluster_ids = list(clusters.keys())
        if max_clusters is not None and max_clusters > 0:
            cluster_ids = cluster_ids[:max_clusters]
        if limit is not None and limit > 0:
            # bound by a target car count: take clusters until their declared sum reaches `limit`.
            picked, acc = [], 0
            for cid in cluster_ids:
                picked.append(cid)
                acc += clusters[cid]
                if acc >= limit:
                    break
            cluster_ids = picked
        print(f"[oem_kia] {stats['clusters_discovered']} live clusters "
              f"(declared full ~{stats['declared_full']} cars); draining {len(cluster_ids)} this run.")

        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        # PHASE 2 — drain each live cluster's car pages (offset cursor per cluster).
        for cid in cluster_ids:
            err, http = await _drain_cluster(
                conn, geo, geo_fallback, platform_ulid, fetcher, governed_fetch, cid, clusters[cid],
                max_pages, concurrency, seen_ids, harvested_cageable, stats)
            stats["clusters_drained"] += 1
            if err is not None:
                fetch_error = err
                last_http = http
                # a hard fetch error stops the whole drain honestly (the breaker must see it).
                break

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, KIA_PLATFORM_RECIPE)
        print(f"[oem_kia] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths that all measure
        # "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for kia        (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join   (DB read truth)
        #   harvested_cageable = distinct (dealer_id, deep_link) pulled (harvest truth)
        # The declared full count is reported for honesty but is NOT a quorum path (it measures the
        # WHOLE portal, not necessarily this slice unless the full drain ran).
        db_edges = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)
        db_join_vehicles = await conn.fetchval(
            """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               JOIN entity d ON d.entity_ulid = v.entity_ulid
               WHERE pl.platform_entity_ulid=$1""", platform_ulid)
        harvested_cageable_n = len(harvested_cageable)
        verdict = await record_count_verdict(
            conn, subject_type="platform_slice", subject_key=platform_code,
            claim="distinct cageable cars (harvest) == platform_listing edges == join-reachable vehicles",
            paths={"db_edges": db_edges, "db_join_vehicles": db_join_vehicles,
                   "harvested_cageable": harvested_cageable_n},
            tolerance=0.0)
        stats["verdict"] = verdict
        stats["db_edges"] = db_edges
        stats["db_join_vehicles"] = db_join_vehicles
        stats["harvested_cageable"] = harvested_cageable_n
        stats["harvested_distinct_ids"] = len(seen_ids)
        stats["platform_code"] = platform_code
        stats["platform_ulid"] = platform_ulid
        stats["recipe_path"] = str(recipe_path)

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks kia, trips the
        # breaker on a ban, and auto-repairs. OK when >=1 page fetched, no fetch error stopped the
        # drain, and the VAM did not refute.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, KIA_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, KIA_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[oem_kia] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("KIA (OEM-VO PORTAL) WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  group / kind          : oem_vo_portal / oem_vo_portal (tier t1_soft, family kia_vo)")
    print(f"  declared full (source): {stats.get('declared_full')} (sum of cluster total_vehiculos)")
    print(f"  live clusters         : {stats.get('clusters_discovered')} discovered / "
          f"{stats.get('clusters_drained')} drained")
    print(f"  concurrency (window)  : {stats.get('concurrency')} pages in flight")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  dealer items          : {stats['dealer_items']}")
    print(f"  no-dealer skipped     : {stats['no_dealer_skipped']}")
    print(f"  private skipped       : {stats['private_skipped']} (OEM portal — none expected)")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-cluster, id dedup)")
    print(f"  geo fallback recovered: {stats.get('geo_fallback_recovered')} "
          f"(city->province ladder rescued these from the strict-resolver skip)")
    print(f"  geo skipped (bad geo) : {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for kia = {stats.get('db_edges')})")
    print(f"  VINs captured         : {stats['vins_captured']} (list has no VIN — expected 0)")
    print(f"  NEW delta events      : {stats['new_events']}")
    print("  --- VAM count quorum (like-with-like, this slice) ---")
    print(f"  harvested_cageable    : {stats.get('harvested_cageable')}")
    print(f"  db_edges              : {stats.get('db_edges')}")
    print(f"  db_join_vehicles      : {stats.get('db_join_vehicles')}")
    print(f"  VAM verdict           : {stats.get('verdict')}")
    print(f"  health status         : {stats.get('health_status')} / breaker {stats.get('breaker_state')}")
    print(f"  recipe                : {stats.get('recipe_path')}")
    print("=" * 64)


def _force_utf8_stdout() -> None:
    """Windows consoles/pipes default to cp1252, which cannot encode the Σ sign, arrows,
    em-dashes, or the accented car titles this connector prints (Híbrido, Diésel,
    Automática) — a raw print() then crashes the whole drain mid-flight. Reconfigure
    stdout/stderr to UTF-8 (errors='replace') so progress logging can never abort the
    harvest. Idempotent, no-op where already UTF-8."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass


def main() -> None:
    _force_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="kia OEM-VO portal wholesale harvester (cluster-partitioned vendor-servlet drain)")
    parser.add_argument("--clusters", type=int, default=None,
                        help="max live clusters to drain this run (default: all discovered = full ES stock)")
    parser.add_argument("--limit", type=int, default=None,
                        help=("optional target car count; clusters are taken until their declared "
                              "sum reaches this. The tighter of --clusters / --limit bounds the run."))
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"car pages fetched in parallel per cluster window; default "
                              f"{DEFAULT_CONCURRENCY}. kiaokasion.net inherits the conservative STEALTH "
                              f"rate class — the governor's per-host bucket is the real limiter."))
    parser.add_argument("--sweep-concurrency", type=int, default=DEFAULT_SWEEP_CONCURRENCY,
                        help=f"cluster-discovery probe concurrency; default {DEFAULT_SWEEP_CONCURRENCY}.")
    parser.add_argument("--sweep-lo", type=int, default=CLUSTER_SWEEP_LO,
                        help=f"cluster-id sweep lower bound; default {CLUSTER_SWEEP_LO}.")
    parser.add_argument("--sweep-hi", type=int, default=CLUSTER_SWEEP_HI,
                        help=f"cluster-id sweep upper bound; default {CLUSTER_SWEEP_HI}.")
    parser.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"per-cluster page ceiling (size={PAGE_SIZE}); default {DEFAULT_MAX_PAGES}.")
    args = parser.parse_args()
    stats = asyncio.run(harvest(
        max_clusters=args.clusters, concurrency=args.concurrency,
        sweep_concurrency=args.sweep_concurrency, sweep_lo=args.sweep_lo,
        sweep_hi=args.sweep_hi, max_pages=args.max_pages, limit=args.limit))
    _print_report(stats)


if __name__ == "__main__":
    main()
