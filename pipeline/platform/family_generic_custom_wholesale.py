"""Generic/custom FAMILY harvester — the bespoke long-tail, end to end.

This is the SECOND long-tail family connector, sibling to
`pipeline.platform.family_dealerk_wholesale`. Where DealerK proves the EASY
multiplier (one byte-identical WordPress/Elementor template shared by every
member, so ONE parser drains them all), this module proves the HARD half of the
mandate: the **generic / custom** family — 83 dealers across 73 own-site domains
whose HTML carries NO detectable shared platform signal. Each is a bespoke,
hand-built (or small-vendor) site, so there is no single template to fingerprint.

The mandate is explicit that this family is LOW leverage / LOW priority precisely
because there is no shared template: each dealer needs an INDIVIDUAL recipe. The
multiplier here is therefore architectural rather than template-level: ONE
connector spine (the same cage / governor / health-breaker / VAM / delta / recipe
machinery the marketplace connectors use) drives N per-dealer recipes. We do NOT
fork the architecture per dealer; we register a small per-dealer `DealerRecipe`
(its listing path + its card parser) and the shared spine harvests every one.

Within the bespoke crowd there are still micro-families. The clearest verified
live 2026-06-13 is the **Pymecar** dealer-site stack (cards on `img.pymecar.com`,
identical `car-card` / `bPrice` / `priceweb` / `lin-inf` markup): carhay.com and
autopai.es share ONE parser (`parse_pymecar`). So even inside "generic/custom",
one recipe can serve several dealers — the multiplier survives.

Ownership model (identical to the DealerK family — the long-tail half):
  the dealer            -> entity (already in DB; resolve by website host, touch)
  each car on its site  -> vehicle, OWNED BY that dealer (entity_ulid = dealer)

There is NO platform_listing edge: a dealer's own website is the PRIMARY source of
its own stock, not a third-party marketplace. Ownership is singular and direct.

This module mirrors `family_dealerk_wholesale`'s spine EXACTLY — same governor
choke point, same GeoResolver, same idempotent ON CONFLICT upserts, same NEW-delta
events, same VAM count quorum, same S-HEALTH heartbeat + breaker — so the bespoke
long-tail flows through the ONE proven architecture, not a fork of it. The ONLY
difference from DealerK is that the parser is selected per dealer (a registry)
instead of one parser for the whole family, because the markup is not shared.

Verified live 2026-06-13 against five real generic/custom dealers from their OWN
websites (all already present as entities in cardeep-pg):
  autofesa.com (28), carhay.com (28), autopai.es (29),
  arguelles-automoviles.com (28), frworldcars.com (02).

Run:  python -m pipeline.platform.family_generic_custom_wholesale --dealers autofesa.com carhay.com
      python -m pipeline.platform.family_generic_custom_wholesale --all
"""
from __future__ import annotations

import argparse
import asyncio
import html as _htmllib
import json
import os
import re
import sys
from dataclasses import dataclass
from typing import Callable

import asyncpg
from curl_cffi import requests as cffi_requests

from pipeline.engine.governor import governor
from pipeline.geo import GeoResolver
from pipeline.ids import ulid
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict
from services.api.codes import cdp_code

DSN = os.environ.get("CARDEEP_DSN",
                     "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# ---------------------------------------------------------------------------
# Family identity. The source_key is the FAMILY, not a single dealer: every dealer
# harvested through this connector is attested by the same provenance key, and the
# connector is one file shared by the whole family (one recipe-spec per member).
# ---------------------------------------------------------------------------
FAMILY_KEY = "family_generic_custom"
FAMILY_NAME = "Generic / custom (bespoke own-site) dealer family"

_IMPERSONATE = "chrome131"
_TIMEOUT = 30
DEFAULT_MAX_PAGES = 15  # generous; most long-tail dealers fit in a handful of pages.


# ---------------------------------------------------------------------------
# Parsed shape (field names taken from the REAL card markup, not assumed).
# ---------------------------------------------------------------------------
@dataclass
class Vehicle:
    deep_link: str
    listing_ref: str | None  # native id in the PDP path when the site exposes one
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    photo_url: str | None


# ---------------------------------------------------------------------------
# Shared parsing helpers.
# ---------------------------------------------------------------------------
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _clean(s: str | None) -> str | None:
    if s is None:
        return None
    s = _htmllib.unescape(s)
    s = _TAG_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s).strip()
    return s or None


def _euros_to_float(raw: str | None) -> float | None:
    """'59.500 €' / '14.300' / '45.590 �' -> 59500.0. Spanish thousands sep is '.'.
    We strip every non-digit and read the integer euros (cards never show cents)."""
    if not raw:
        return None
    digits = re.sub(r"[^\d]", "", raw)
    if not digits:
        return None
    try:
        val = float(digits)
    except ValueError:
        return None
    # guard against absurd values from a mis-grabbed token (e.g. phone numbers)
    if val < 100 or val > 5_000_000:
        return None
    return val


def _split_make_model(text: str | None) -> tuple[str | None, str | None]:
    text = _clean(text)
    if not text:
        return (None, None)
    parts = text.split()
    if len(parts) == 1:
        return (parts[0], None)
    return (parts[0], " ".join(parts[1:]))


def _abs_url(base: str, href: str) -> str:
    href = href.strip()
    if href.startswith("http"):
        return href
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("./"):
        href = href[1:]
    if not href.startswith("/"):
        href = "/" + href
    return base.rstrip("/") + href


def _parse_spec_line(text: str | None) -> tuple[int | None, int | None, str | None]:
    """Parse a free-form 'YEAR | FUEL | KM | ...' or 'YEAR  KM km  FUEL' spec line
    into (year, km, fuel). Order-agnostic: we scan for a 4-digit year, a km figure,
    and a known fuel keyword wherever they appear."""
    if not text:
        return (None, None, None)
    t = _htmllib.unescape(text)
    year = km = None
    fuel = None
    my = re.search(r"\b(19|20)\d{2}\b", t)
    if my:
        y = int(my.group(0))
        if 1900 <= y <= 2100:
            year = y
    mk = re.search(r"([\d.\s]{2,})\s*km\b", t, re.I)
    if mk:
        kd = re.sub(r"[^\d]", "", mk.group(1))
        if kd:
            k = int(kd)
            if 0 <= k <= 5_000_000:
                km = k
    for kw in ("Diésel", "Diesel", "Gasolina", "Híbrido", "Hibrido",
               "Eléctrico", "Electrico", "GLP", "GNC", "Gas"):
        if re.search(re.escape(kw), t, re.I):
            fuel = kw.replace("é", "e").replace("í", "i")
            break
    # the encoding-mangled 'DI�SEL' / 'H�BRIDO' fallbacks
    if fuel is None:
        if re.search(r"di.?sel", t, re.I):
            fuel = "Diesel"
        elif re.search(r"h.?brido", t, re.I):
            fuel = "Hibrido"
        elif re.search(r"el.?ctrico", t, re.I):
            fuel = "Electrico"
    return (year, km, fuel)


# ---------------------------------------------------------------------------
# Per-dealer parsers. Each reads ONE bespoke layout, verified live 2026-06-13.
# A parser takes (listing_html, base_url) and returns list[Vehicle].
# ---------------------------------------------------------------------------
# The Pymecar card WRAPPER is `<div class="car-card">` or `<div class="car-card
# showHover" ...>`. We must split ONLY on the wrapper, NOT on the inner
# `car-card-img` / `car-card-data` blocks (which would tear the price away from the
# maker anchor). The negative lookahead excludes the hyphenated inner classes.
_PYMECAR_CARD = re.compile(r'class="car-card(?!-)')
_PYMECAR_LINK = re.compile(r'<a[^>]+href="([^"]+)"[^>]*title="[^"]*"')
_PYMECAR_MAKER = re.compile(r'class="maker[^"]*">\s*<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>')
_PYMECAR_VERSION = re.compile(r'class="version[^"]*">\s*<strong>([^<]+)</strong>')
_PYMECAR_SPEC = re.compile(r'class="lin-inf[^"]*">\s*<small>([^<]+)</small>')
_PYMECAR_PRICEWEB = re.compile(r'class="priceweb">\s*([0-9][0-9.\s]*)\s*')
_PYMECAR_PRICE = re.compile(r'class="price">\s*<span[^>]*>\s*([0-9][0-9.\s]*)')
_PYMECAR_IMG = re.compile(r'src="(https?://img\.pymecar\.com/[^"]+?\.jpe?g)"', re.I)


def parse_pymecar(html_text: str, base: str) -> list[Vehicle]:
    """Pymecar dealer-site stack (carhay.com, autopai.es). Cards delimited by the
    'car-card' class; price is `priceweb` (the cash price; `tachado` is the struck
    pre-finance price); spec line is `lin-inf` -> 'YEAR | FUEL | KM | CV | TRANS'."""
    frags = _PYMECAR_CARD.split(html_text)
    out: list[Vehicle] = []
    seen: set[str] = set()
    for frag in frags[1:]:
        # the maker anchor carries BOTH the canonical detail link and the make text
        mm = _PYMECAR_MAKER.search(frag)
        if not mm:
            continue
        deep_link = _abs_url(base, mm.group(1))
        if deep_link in seen:
            continue
        seen.add(deep_link)
        make = _clean(mm.group(2))
        version_m = _PYMECAR_VERSION.search(frag)
        version = _clean(version_m.group(1)) if version_m else None
        # make-anchor text is e.g. 'VOLKSWAGEN CALIFORNIA' -> make + model head
        mk, md = _split_make_model(make)
        title_bits = [b for b in (make, version) if b]
        title = " ".join(title_bits) if title_bits else make
        spec_m = _PYMECAR_SPEC.search(frag)
        year, km, fuel = _parse_spec_line(spec_m.group(1) if spec_m else None)
        pw = _PYMECAR_PRICEWEB.search(frag)
        price = _euros_to_float(pw.group(1) if pw else None)
        if price is None:
            pm = _PYMECAR_PRICE.search(frag)
            price = _euros_to_float(pm.group(1) if pm else None)
        img = _PYMECAR_IMG.search(frag)
        listing_ref = None
        mref = re.search(r"_(\d+)(?:[/?#]|$)", deep_link)
        if mref:
            listing_ref = mref.group(1)
        out.append(Vehicle(
            deep_link=deep_link, listing_ref=listing_ref, title=title,
            make=mk, model=md, year=year, km=km, price=price, fuel=fuel,
            photo_url=img.group(1) if img else None))
    return out


_AUTOFESA_CARD = re.compile(r'class="vehicle-card__title"')
_AUTOFESA_LINK = re.compile(r'<a[^>]+href="([^"]+)"')
# Some autofesa cards cross-link the title anchor to an external marketplace
# (autoscout24.es). The dealer's OWN PDP is the only valid deep_link for own-site
# ownership, so we keep ONLY anchors that stay on the dealer's own domain.
_AUTOFESA_OWN_PDP = re.compile(r'/coches-de-ocasion/|/coches-segunda-mano/')
_AUTOFESA_MAKE = re.compile(r'class="make">([^<]+)</span>')
_AUTOFESA_MODEL = re.compile(r'class="model">([^<]+)</span>')
_AUTOFESA_VERSION = re.compile(r'class="version">([^<]+)</span>')
_AUTOFESA_FEATURES = re.compile(r'class="vehicle-card__features".*?<ul[^>]*>(.*?)</ul>', re.S)
_AUTOFESA_LI = re.compile(r'<li[^>]*>(.*?)</li>', re.S)
_AUTOFESA_CURRENT = re.compile(r'class="current">.*?<span>\s*([0-9][0-9.\s]*)\s*</span>', re.S)
_AUTOFESA_IMG = re.compile(r'<img[^>]+src="(https?://[^"]+?\.(?:jpe?g|png|webp))"', re.I)


def parse_autofesa(html_text: str, base: str) -> list[Vehicle]:
    """autofesa.com bespoke 'vehicle-card__*' layout. Make/model/version in the title
    block; features <ul> carries YEAR / KM / FUEL / TRANS as <li>; the cash price is
    the `current` block (`old-price` is the struck pre-finance price)."""
    frags = _AUTOFESA_CARD.split(html_text)
    out: list[Vehicle] = []
    seen: set[str] = set()
    bare = re.sub(r"^https?://(www\.)?", "", base).split("/")[0].lower()
    for frag in frags[1:]:
        # pick the FIRST anchor that is the dealer's OWN PDP (skip external/AS24
        # cross-links and same-host non-PDP anchors), so ownership stays own-site.
        deep_link = None
        for cand in _AUTOFESA_LINK.findall(frag):
            absu = _abs_url(base, cand)
            host_ok = bare in re.sub(r"^https?://(www\.)?", "", absu).split("/")[0].lower()
            if host_ok and _AUTOFESA_OWN_PDP.search(absu):
                deep_link = absu
                break
        if not deep_link or deep_link in seen:
            continue
        seen.add(deep_link)
        make = _clean(_AUTOFESA_MAKE.search(frag).group(1)) if _AUTOFESA_MAKE.search(frag) else None
        model = _clean(_AUTOFESA_MODEL.search(frag).group(1)) if _AUTOFESA_MODEL.search(frag) else None
        version = _clean(_AUTOFESA_VERSION.search(frag).group(1)) if _AUTOFESA_VERSION.search(frag) else None
        title = " ".join(b for b in (make, model, version) if b) or None
        year = km = None
        fuel = None
        feats = _AUTOFESA_FEATURES.search(frag)
        if feats:
            items = [_clean(x) for x in _AUTOFESA_LI.findall(feats.group(1))]
            joined = " | ".join(x for x in items if x)
            year, km, fuel = _parse_spec_line(joined)
        cur = _AUTOFESA_CURRENT.search(frag)
        price = _euros_to_float(cur.group(1) if cur else None)
        img = _AUTOFESA_IMG.search(frag)
        out.append(Vehicle(
            deep_link=deep_link, listing_ref=None, title=title,
            make=make, model=model, year=year, km=km, price=price, fuel=fuel,
            photo_url=img.group(1) if img else None))
    return out


# arguelles cards: each card is a `class="product"` wrapper holding a detail link
# /coches-segunda-mano/<Prov>/<id>-...-ocasion-<prov>.html (the link appears 3x per
# card — image, title, button — so we split on the WRAPPER, not the link).
_ARG_CARD = re.compile(r'class="product"')
_ARG_LINK = re.compile(
    r'href="(/coches-segunda-mano/[A-Za-zÀ-ſ]+/(\d+)-[^"]+?\.html)"')
_ARG_MAKE = re.compile(r'class="mc">\s*([^<]+?)\s*</span>\s*<span class="mod">\s*([^<]+?)\s*</span>')
_ARG_PRICE = re.compile(r'class="mc"[^>]*>\s*([0-9][0-9.\s]*)\s*[€�&]')
_ARG_YD = re.compile(r'class="yd"[^>]*>\s*([^<]+?)\s*</span>')
_ARG_IMG = re.compile(r'<img[^>]+src="(https?://[^"]+?\.(?:JPG|jpe?g|png|webp))"', re.I)


def parse_arguelles(html_text: str, base: str) -> list[Vehicle]:
    """arguelles-automoviles.com bespoke inline-style cards. Each `class="product"`
    fragment holds one car: the detail link carries a leading numeric id; make/model
    in `mc`/`mod`; price in the float-right `mc`; the three `yd` spans are
    YEAR / KM / FUEL in order."""
    out: list[Vehicle] = []
    seen: set[str] = set()
    for frag in _ARG_CARD.split(html_text)[1:]:
        lk = _ARG_LINK.search(frag)
        if not lk:
            continue
        deep_link = _abs_url(base, lk.group(1))
        listing_ref = lk.group(2)
        if deep_link in seen:
            continue
        seen.add(deep_link)
        mk = md = None
        mm = _ARG_MAKE.search(frag)
        if mm:
            mk = _clean(mm.group(1))
            md = _clean(mm.group(2))
        title = " ".join(b for b in (mk, md) if b) or None
        # price: the first `mc` span that is a euro figure (the make `mc` is text).
        price = None
        for pm in _ARG_PRICE.finditer(frag):
            price = _euros_to_float(pm.group(1))
            if price:
                break
        yds = [_clean(x) for x in _ARG_YD.findall(frag)]
        joined = " | ".join(x for x in yds if x)
        year, km, fuel = _parse_spec_line(joined)
        img = _ARG_IMG.search(frag)
        out.append(Vehicle(
            deep_link=deep_link, listing_ref=listing_ref, title=title,
            make=mk, model=md, year=year, km=km, price=price, fuel=fuel,
            photo_url=img.group(1) if img else None))
    return out


# frworldcars: blog-style <article> cards; detail link /vehiculos/YYYY/MM/DD/<slug>/
_FRW_ARTICLE = re.compile(r'<article>', re.I)
_FRW_LINK = re.compile(r'<a[^>]+href="(/vehiculos/\d{4}/\d{2}/\d{2}/[^"]+/)"[^>]*title="([^"]*)"')
_FRW_H3 = re.compile(r'<h3>\s*(.*?)\s*</h3>', re.S)
_FRW_IMG = re.compile(r'<img[^>]+src="(https?://[^"]+?\.(?:jpe?g|png|webp))"', re.I)
# title like "MERCEDES CLA 45 AMG S COUPE 4MATIC+, NUEVO MODELO 2020. 69.900 . OFERTA..."
_FRW_PRICE_IN_TITLE = re.compile(r'(\d{1,3}(?:[.\s]\d{3})+)\s*(?:€|�|&euro;|EUR|\.)')


def parse_frworldcars(html_text: str, base: str) -> list[Vehicle]:
    """frworldcars.com blog-style premium/classic cards. Each <article> has a
    /vehiculos/Y/M/D/<slug>/ link and an <h3> headline that embeds make/model/year
    and the price (e.g. '... NUEVO MODELO 2020. 69.900 €. OFERTA ...'). Bespoke and
    price-in-title, so we parse make/model/year/price out of the headline text."""
    frags = _FRW_ARTICLE.split(html_text)
    out: list[Vehicle] = []
    seen: set[str] = set()
    for frag in frags[1:]:
        lk = _FRW_LINK.search(frag)
        if not lk:
            continue
        deep_link = _abs_url(base, lk.group(1))
        if deep_link in seen:
            continue
        seen.add(deep_link)
        head = _clean(_FRW_H3.search(frag).group(1)) if _FRW_H3.search(frag) else _clean(lk.group(2))
        title = head
        make = model = None
        if head:
            toks = head.split()
            if toks:
                make = toks[0].capitalize()
                if len(toks) > 1:
                    model = toks[1]
        my = re.search(r"\b(19|20)\d{2}\b", head or "")
        year = int(my.group(0)) if my else None
        price = None
        if head:
            pm = _FRW_PRICE_IN_TITLE.search(head)
            price = _euros_to_float(pm.group(1)) if pm else None
        img = _FRW_IMG.search(frag)
        # native id: the slug is stable; use the date+slug tail as listing_ref
        mref = re.search(r"/vehiculos/(\d{4}/\d{2}/\d{2}/[^/]+)/", deep_link)
        out.append(Vehicle(
            deep_link=deep_link, listing_ref=mref.group(1) if mref else None,
            title=title, make=make, model=model, year=year, km=None,
            price=price, fuel=None, photo_url=img.group(1) if img else None))
    return out


# ---------------------------------------------------------------------------
# Per-dealer recipe registry. Each member of the generic/custom family declares
# its OWN listing path, pagination template and parser — because there is no shared
# template to fingerprint. This registry IS the family: ONE connector, N recipes.
# `pages`: 'query' -> ?page=N ; 'single' -> one page (site has no server pagination).
# ---------------------------------------------------------------------------
@dataclass
class DealerRecipe:
    host: str
    listing_path: str
    parser: Callable[[str, str], list[Vehicle]]
    pages: str = "query"           # 'query' (?page=N) | 'single'
    subfamily: str = "custom"
    notes: str = ""


REGISTRY: dict[str, DealerRecipe] = {
    "autofesa.com": DealerRecipe(
        host="autofesa.com", listing_path="/coches-segunda-mano",
        parser=parse_autofesa, pages="query", subfamily="custom",
        notes="bespoke vehicle-card__* layout; ?page=N pagination verified live"),
    "carhay.com": DealerRecipe(
        host="carhay.com", listing_path="/coches-segunda-mano/",
        parser=parse_pymecar, pages="single", subfamily="pymecar",
        notes="Pymecar stack (img.pymecar.com); single listing page (AJAX paging)"),
    "autopai.es": DealerRecipe(
        host="autopai.es", listing_path="/vehiculos-ocasion/",
        parser=parse_pymecar, pages="single", subfamily="pymecar",
        notes="Pymecar stack (shares parse_pymecar with carhay.com)"),
    "arguelles-automoviles.com": DealerRecipe(
        host="arguelles-automoviles.com", listing_path="/coches-segunda-mano.html",
        parser=parse_arguelles, pages="single", subfamily="custom",
        notes="bespoke inline-style cards; full inventory on one page"),
    "frworldcars.com": DealerRecipe(
        host="frworldcars.com", listing_path="/vehiculos/",
        parser=parse_frworldcars, pages="single", subfamily="custom",
        notes="blog-style <article> cards; price embedded in <h3> headline"),
}


# ---------------------------------------------------------------------------
# Fetch — one curl_cffi GET per page, routed THROUGH the governor (per-host bucket).
# ---------------------------------------------------------------------------
class FamilyFetcher:
    def __init__(self) -> None:
        self._session = cffi_requests.Session(impersonate=_IMPERSONATE)
        self.last_status: int | None = None

    def fetch(self, url: str) -> str:
        resp = self._session.get(url, impersonate=_IMPERSONATE, timeout=_TIMEOUT,
                                 allow_redirects=True)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url}")
        return resp.text


# ---------------------------------------------------------------------------
# The family recipe — ONE asset shared by the family, carrying every member's spec.
# ---------------------------------------------------------------------------
def _build_family_recipe() -> dict:
    members = {}
    for host, rc in REGISTRY.items():
        members[host] = {
            "listing_path": rc.listing_path,
            "pagination": ("?page=N until a page yields no new cards"
                           if rc.pages == "query" else "single listing page"),
            "parser": rc.parser.__name__,
            "subfamily": rc.subfamily,
            "notes": rc.notes,
        }
    return {
        "version": 1,
        "source": FAMILY_KEY,
        "family": FAMILY_NAME,
        "scope": "long-tail dealer OWN-SITE inventory, bespoke/custom (no shared platform)",
        "engine": "curl_cffi+chrome131_impersonate+html(GET, server-rendered)",
        "access": ("OPEN public dealer websites (Chrome TLS fingerprint; no proxy, no "
                   "browser, no creds). Server-rendered HTML — no JS execution needed."),
        "data_surface": "dealer_site_html",
        "fingerprint": ("NONE shared — this is the generic/custom family: each dealer is "
                        "a bespoke site with no detectable platform signal, so membership "
                        "is by curated registry, not by a single fingerprint. Micro-family "
                        "'pymecar' (img.pymecar.com car-card markup) shares ONE parser."),
        "ownership": "vehicle.entity_ulid = the DEALER itself (own-site stock; no marketplace edge)",
        "multiplier": ("architectural: ONE connector spine (cage/governor/health/VAM/delta) "
                       "drives N per-dealer recipes; within it the 'pymecar' parser already "
                       "serves multiple dealers (carhay.com + autopai.es)."),
        "members": members,
    }


# ---------------------------------------------------------------------------
# DB layer — idempotent upserts mirroring family_dealerk_wholesale (no edge).
# ---------------------------------------------------------------------------
async def resolve_dealer_for_host(conn: asyncpg.Connection, host: str) -> dict | None:
    bare = re.sub(r"^www\.", "", host.lower())
    row = await conn.fetchrow(
        """SELECT entity_ulid, cdp_code, trade_name, province_code, municipality_code, website
             FROM entity
            WHERE kind IN ('compraventa','concesionario_oficial')
              AND website IS NOT NULL AND website <> ''
              AND lower(regexp_replace(regexp_replace(website,'^https?://',''),'^www\\.','')) LIKE $1
            ORDER BY last_seen DESC
            LIMIT 1""",
        f"{bare}%")
    return dict(row) if row else None


async def upsert_dealer_by_host(conn: asyncpg.Connection, host: str) -> dict | None:
    """Return the owning dealer entity for `host`, stamping the family provenance.
    Preferred path: the dealer is already in the DB (matched by website host).
    Fallback: mint a minimal domain-keyed entity so the harvest still has a real
    owner (province NULL; the cdp_code carries the bare-domain identity)."""
    existing = await resolve_dealer_for_host(conn, host)
    if existing:
        await conn.execute("UPDATE entity SET last_seen = now() WHERE entity_ulid = $1",
                           existing["entity_ulid"])
        await conn.execute(
            "INSERT INTO entity_source (entity_ulid, source_key, source_ref) "
            "VALUES ($1,$2,$3) ON CONFLICT (entity_ulid, source_key) "
            "DO UPDATE SET seen_at = now()",
            existing["entity_ulid"], FAMILY_KEY, host)
        return existing

    bare = re.sub(r"^www\.", "", host.lower())
    code = cdp_code(province_code="00", domain=bare)
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               website, is_tier1, status, kind_source, sells_cars,
               first_discovered_source, last_seen)
           VALUES ($1,$2,'compraventa',$3,$3,$4,FALSE,'active','platform_label',TRUE,$5, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()""",
        eulid, code, bare, bare, FAMILY_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) "
        "VALUES ($1,$2,$3) ON CONFLICT (entity_ulid, source_key) "
        "DO UPDATE SET seen_at = now()",
        eulid, FAMILY_KEY, host)
    return {"entity_ulid": eulid, "cdp_code": code, "trade_name": bare,
            "province_code": None, "municipality_code": None, "website": bare}


_BULK_INSERT_VEHICLES = """
INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model,
        year, km, price, fuel, photo_url, vin_ref, status)
SELECT u.vehicle_ulid, u.entity_ulid, u.deep_link, u.title, u.make, u.model,
       u.year, u.km, u.price, u.fuel, u.photo_url, u.vin_ref, 'available'
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[], $5::text[], $6::text[],
              $7::int[], $8::int[], $9::numeric[], $10::text[], $11::text[], $12::text[])
       AS u(vehicle_ulid, entity_ulid, deep_link, title, make, model,
            year, km, price, fuel, photo_url, vin_ref)
ON CONFLICT (entity_ulid, deep_link) DO NOTHING
"""

_BULK_TOUCH_VEHICLES = """
UPDATE vehicle v SET last_seen = now(), status = 'available'
  FROM unnest($1::text[]) AS u(vehicle_ulid)
 WHERE v.vehicle_ulid = u.vehicle_ulid
"""

_BULK_INSERT_EVENTS = """
INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type,
        old_value, new_value)
SELECT u.event_ulid, u.vehicle_ulid, u.entity_ulid, 'NEW', NULL, u.new_value::jsonb
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[])
       AS u(event_ulid, vehicle_ulid, entity_ulid, new_value)
"""


async def ingest_dealer_vehicles(conn: asyncpg.Connection, dealer_ulid: str,
                                 vehicles: list[Vehicle], stats: dict) -> None:
    """Bulk-upsert one dealer's whole harvest in ONE transaction, set-based SQL.
    Idempotent on (entity_ulid, deep_link): existing cars are touched, genuinely new
    cars are inserted and get a NEW delta event. A re-run adds 0 rows and 0 events."""
    by_link: dict[str, Vehicle] = {}
    for v in vehicles:
        if v.deep_link and v.deep_link not in by_link:
            by_link[v.deep_link] = v
    if not by_link:
        return
    links = list(by_link.keys())

    async with conn.transaction():
        existing = {
            row["deep_link"]: row["vehicle_ulid"]
            for row in await conn.fetch(
                "SELECT vehicle_ulid, deep_link FROM vehicle "
                "WHERE entity_ulid = $1 AND deep_link = ANY($2::text[])",
                dealer_ulid, links)
        }
        touch_ulids: list[str] = []
        new_links: list[str] = []
        vehicle_ulid_for: dict[str, str] = {}
        for link in links:
            ex = existing.get(link)
            if ex is not None:
                vehicle_ulid_for[link] = ex
                touch_ulids.append(ex)
            else:
                vid = ulid()
                vehicle_ulid_for[link] = vid
                new_links.append(link)

        if touch_ulids:
            await conn.execute(_BULK_TOUCH_VEHICLES, touch_ulids)

        confirmed_new: list[str] = []
        if new_links:
            ins = [(vehicle_ulid_for[l], dealer_ulid, l, by_link[l]) for l in new_links]
            await conn.execute(
                _BULK_INSERT_VEHICLES,
                [x[0] for x in ins], [x[1] for x in ins], [x[2] for x in ins],
                [x[3].title for x in ins], [x[3].make for x in ins], [x[3].model for x in ins],
                [x[3].year for x in ins], [x[3].km for x in ins], [x[3].price for x in ins],
                [x[3].fuel for x in ins], [x[3].photo_url for x in ins],
                [x[3].listing_ref for x in ins])
            landed = {
                row["deep_link"]: row["vehicle_ulid"]
                for row in await conn.fetch(
                    "SELECT vehicle_ulid, deep_link FROM vehicle "
                    "WHERE vehicle_ulid = ANY($1::text[])",
                    [vehicle_ulid_for[l] for l in new_links])
            }
            for link in new_links:
                real = landed.get(link)
                if real is not None and real == vehicle_ulid_for[link]:
                    confirmed_new.append(link)
                elif real is not None:
                    vehicle_ulid_for[link] = real
                else:
                    row = await conn.fetchrow(
                        "SELECT vehicle_ulid FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2",
                        dealer_ulid, link)
                    if row is not None:
                        vehicle_ulid_for[link] = row["vehicle_ulid"]

        stats["cars_ingested"] += len(links)
        stats["new_cars"] += len(confirmed_new)

        if confirmed_new:
            ev_u, ev_v, ev_e, ev_p = [], [], [], []
            for link in confirmed_new:
                v = by_link[link]
                payload = {"price": v.price, "title": v.title, "family": FAMILY_KEY}
                ev_u.append(ulid())
                ev_v.append(vehicle_ulid_for[link])
                ev_e.append(dealer_ulid)
                ev_p.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_u, ev_v, ev_e, ev_p)
            stats["new_events"] += len(confirmed_new)


# ---------------------------------------------------------------------------
# Per-dealer harvest: resolve -> drain pages with the dealer's parser -> ingest.
# ---------------------------------------------------------------------------
async def harvest_one_dealer(conn: asyncpg.Connection, governed_fetch,
                             rc: DealerRecipe, max_pages: int, stats: dict) -> dict:
    bare = re.sub(r"^www\.", "", rc.host.lower())
    summary = {"host": bare, "subfamily": rc.subfamily, "vehicles": 0, "new": 0,
               "dealer_cdp": None, "pages": 0, "path": rc.listing_path}

    base = f"https://www.{bare}"
    # confirm the base resolves; fall back to bare host if www. fails.
    listing_url = base + rc.listing_path
    try:
        html_text = await governed_fetch(listing_url)
    except Exception:
        base = f"https://{bare}"
        listing_url = base + rc.listing_path
        try:
            html_text = await governed_fetch(listing_url)
        except Exception as e:
            summary["error"] = f"listing fetch failed: {e}"
            stats["dealers_failed"] += 1
            return summary

    cards = rc.parser(html_text, base)
    if not cards:
        summary["error"] = "listing yielded no cards (layout changed or empty)"
        stats["dealers_empty"] += 1
        return summary
    all_vehicles: list[Vehicle] = list(cards)
    summary["pages"] = 1

    if rc.pages == "query":
        seen_links = {v.deep_link for v in cards}
        page = 2
        while page <= max_pages:
            url = f"{base}{rc.listing_path}?page={page}"
            try:
                ph = await governed_fetch(url)
            except Exception:
                break
            pcards = rc.parser(ph, base)
            fresh = [c for c in pcards if c.deep_link not in seen_links]
            if not fresh:
                break
            for c in fresh:
                seen_links.add(c.deep_link)
            all_vehicles.extend(fresh)
            summary["pages"] = page
            page += 1

    dealer = await upsert_dealer_by_host(conn, bare)
    if dealer is None:
        summary["error"] = "could not resolve owning dealer"
        stats["dealers_failed"] += 1
        return summary
    summary["dealer_cdp"] = dealer["cdp_code"]

    before_new = stats["new_cars"]
    await ingest_dealer_vehicles(conn, dealer["entity_ulid"], all_vehicles, stats)
    summary["vehicles"] = len({v.deep_link for v in all_vehicles})
    summary["new"] = stats["new_cars"] - before_new
    stats["dealers_harvested"] += 1
    stats["harvested_pairs"].update(
        (dealer["entity_ulid"], v.deep_link) for v in all_vehicles if v.deep_link)
    return summary


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
async def harvest(dealers: list[str] | None, run_all: bool, max_pages: int) -> dict:
    conn = await asyncpg.connect(DSN)
    fetcher = FamilyFetcher()
    stats = {
        "dealers_requested": 0, "dealers_harvested": 0,
        "dealers_empty": 0, "dealers_failed": 0, "dealers_unknown": 0,
        "cars_ingested": 0, "new_cars": 0, "new_events": 0,
        "harvested_pairs": set(), "summaries": [],
    }

    if await is_open(conn, FAMILY_KEY):
        print(f"[{FAMILY_KEY}] breaker OPEN; skipping drain (graceful degradation).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": FAMILY_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch)

    last_http: int | None = None
    try:
        # GeoResolver is loaded to keep parity with the family spine (the dealer is
        # resolved from the DB, so no geo inference is needed here, but loading it
        # keeps the contract identical and validates the geo tables exist).
        await GeoResolver.load(conn)

        if run_all or not dealers:
            targets = list(REGISTRY.keys())
        else:
            targets = []
            for d in dealers:
                bare = re.sub(r"^www\.", "", re.sub(r"^https?://", "", d.strip().lower())).split("/")[0]
                if bare in REGISTRY:
                    targets.append(bare)
                else:
                    print(f"[{FAMILY_KEY}] unknown dealer '{d}' — not in registry; skipping.")
                    stats["dealers_unknown"] += 1
        stats["dealers_requested"] = len(targets)

        print(f"[{FAMILY_KEY}] family={FAMILY_NAME}")
        print(f"[{FAMILY_KEY}] governor paces each dealer host independently "
              f"(per-host token bucket). ONE connector -> {len(targets)} dealers, "
              f"each with its own recipe.")

        for host in targets:
            rc = REGISTRY[host]
            summary = await harvest_one_dealer(conn, governed_fetch, rc, max_pages, stats)
            stats["summaries"].append(summary)
            print(f"[{FAMILY_KEY}]   {summary['host']:30s} {summary['subfamily']:8s} "
                  f"path={summary.get('path')} vehicles={summary['vehicles']:3d} "
                  f"new={summary['new']:3d}" +
                  (f"  ERR={summary['error']}" if summary.get("error") else ""))
            last_http = fetcher.last_status

        recipe_path = write_recipe(FAMILY_KEY, _build_family_recipe())
        print(f"[{FAMILY_KEY}] family recipe written: {recipe_path}")

        # VAM count quorum (like-with-like) for this family slice:
        #   harvested_pairs    = distinct (dealer, deep_link) pulled this run (harvest truth)
        #   db_family_vehicles = vehicles in DB owned by the dealers this source attests,
        #                        scoped to the deep_links pulled this run (DB read truth)
        family_dealer_ulids = [
            r["entity_ulid"] for r in await conn.fetch(
                "SELECT entity_ulid FROM entity_source WHERE source_key = $1", FAMILY_KEY)]
        db_family_vehicles = 0
        if family_dealer_ulids and stats["harvested_pairs"]:
            db_family_vehicles = await conn.fetchval(
                """SELECT count(*) FROM vehicle
                    WHERE entity_ulid = ANY($1::text[])
                      AND deep_link = ANY($2::text[])""",
                family_dealer_ulids,
                [p[1] for p in stats["harvested_pairs"]]) or 0
        harvested_n = len(stats["harvested_pairs"])
        verdict = await record_count_verdict(
            conn, subject_type="family_slice", subject_key=FAMILY_KEY,
            claim="distinct (dealer, deep_link) harvested == family vehicles persisted in DB",
            paths={"db_family_vehicles": db_family_vehicles,
                   "harvested_pairs": harvested_n,
                   "cars_ingested_distinct": harvested_n},
            tolerance=0.0)
        stats["verdict"] = verdict
        stats["db_family_vehicles"] = db_family_vehicles
        stats["harvested_pairs_n"] = harvested_n
        stats["recipe_path"] = str(recipe_path)
        stats["family_dealers_attested"] = len(family_dealer_ulids)

        run_ok = (stats["dealers_harvested"] > 0 and verdict != "REFUTED")
        run_error = None if run_ok else f"VAM verdict {verdict}"
        outcome = await record_run(
            conn, FAMILY_KEY, ok=run_ok, rows=stats["cars_ingested"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, FAMILY_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        stats.pop("harvested_pairs", None)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[{FAMILY_KEY}] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 66)
    print("GENERIC/CUSTOM FAMILY — BESPOKE LONG-TAIL HARVEST REPORT")
    print("=" * 66)
    print(f"  family               : {FAMILY_NAME}")
    print(f"  dealers requested    : {stats['dealers_requested']}")
    print(f"  dealers harvested    : {stats['dealers_harvested']}")
    print(f"  empty inventory      : {stats['dealers_empty']}")
    print(f"  failed               : {stats['dealers_failed']}")
    print(f"  cars ingested        : {stats['cars_ingested']} ({stats['new_cars']} new)")
    print(f"  NEW delta events     : {stats['new_events']}")
    print(f"  family dealers attested (entity_source): {stats.get('family_dealers_attested')}")
    print("  --- VAM count quorum (like-with-like, this slice) ---")
    print(f"  harvested_pairs      : {stats.get('harvested_pairs_n')}")
    print(f"  db_family_vehicles   : {stats.get('db_family_vehicles')}")
    print(f"  VAM verdict          : {stats.get('verdict')}")
    print(f"  health / breaker     : {stats.get('health_status')} / {stats.get('breaker_state')}")
    print(f"  recipe               : {stats.get('recipe_path')}")
    print("  --- the multiplier (one connector -> N dealers, one parser -> M) ---")
    for s in stats.get("summaries", []):
        print(f"    {s['host']:30s} {s['subfamily']:8s} {s['vehicles']:3d} cars "
              f"(new {s['new']:3d})  cdp={s.get('dealer_cdp')}")
    print("=" * 66)


def main() -> None:
    p = argparse.ArgumentParser(
        description="Generic/custom bespoke long-tail family harvester (one connector -> N dealers)")
    p.add_argument("--dealers", nargs="*", default=None,
                   help="explicit dealer hosts from the registry (e.g. autofesa.com carhay.com)")
    p.add_argument("--all", action="store_true", help="harvest every registered dealer")
    p.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES,
                   help=f"max listing pages per dealer; default {DEFAULT_MAX_PAGES}")
    args = p.parse_args()
    stats = asyncio.run(harvest(args.dealers, args.all, args.max_pages))
    _print_report(stats)


if __name__ == "__main__":
    main()
