"""faciliteacoches + RACC ocasión WHOLESALE harvester — two genuinely-NEW car-selling channels.

Both channels surfaced from the keyword census with count=0 in the DB and were verified reachable
FREE with a Chrome TLS fingerprint (curl_cffi chrome131; no proxy, no browser, no cookie warm-up).
They are two MEMBERS of one connector, mirroring pipeline.platform.group_vo_chains_wholesale EXACTLY
(same governor choke point, same GeoResolver, same idempotent ON CONFLICT BULK unnest ingest, same
NEW-delta events, same VAM count quorum, same S-HEALTH heartbeat/breaker). This proves a THIRD shape
of platform flows through the one architecture, never a fork of it:

  1. FACILITEACOCHES (faciliteacoches.com) — kind='plataforma', source_group='marketplace_motor'.
     A CaixaBank/ARVAL VO+renting AGGREGATOR (Next.js App Router on Vercel). Each car carries FULL
     dealer attribution in its RSC data-layer: `dealerData` (the OEM/dealer group — id_mf, name, slug,
     province, cp, city) AND `shopData` (the PHYSICAL selling shop where the car sits — its own
     name/province/region/cp/city). The car a buyer purchases has a REAL selling point: that physical
     SHOP. So this is the per-SELLING-POINT owner model (mirrors coches_net dealers / Flexicar
     branches):
       faciliteacoches (the platform)  -> entity, kind='plataforma' (+ platform_meta)
       each selling SHOP               -> entity, kind='compraventa' (geo-resolved from shopData)
       each CAR                        -> vehicle, OWNED BY its shop (entity_ulid=shop)
       the car on the aggregator       -> platform_listing edge (platform_entity <-> vehicle)
     Surface/enumeration: the SRP `/es/es/coches/ocasion/compra` resolves its results through a
     DEFERRED RSC server promise — `?page=N` is ignored and the browser pages via a Next.js server
     action (not header-reachable). The CANONICAL full-stock index is the sitemap
     `/peninsula-baleares/sitemap/coches-ficha.xml` (21,989 car PDP URLs live 2026-06-13). We drain
     PDP-by-PDP from that index: each PDP `/es/es/ficha/{slug}-{id_mf}` re-emits the SAME RSC car
     object with dealerData + shopData, so every drained car is fully attributed and geo-anchored. The
     id_mf tail of the PDP slug is the stable native listing_ref. t0_open (Vercel, no WAF challenge).

  2. RACC (cochesocasion.racc.es) — kind='plataforma', source_group='association'.
     The RACC auto-club VO portal (WordPress, Apache/PHP 8.3). It aggregates dealer inventory feeds
     (fotos.inventario.pro); the SRP card carries the car (make/model/version/year/km/price/fuel/
     transmission/photo + native compare-id + deep link) but NOT the seller — the seller (dealer) is
     on the PDP JSON-LD `offers.seller` (@type:Organization, name). The surface exposes NO per-car
     province/address (a national inventory portal), so the SELLER is anchored national (province
     NULL) — the per-dealer-by-name owner model (chain-as-owner style, but one owner per dealer name):
       RACC (the portal)               -> entity, kind='plataforma' (+ platform_meta)
       each selling DEALER (by name)   -> entity, kind='compraventa' (national; geo NULL)
       each CAR                        -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
       the car on the portal           -> platform_listing edge (portal_entity <-> vehicle)
     A car whose PDP exposes no seller is caged under the PORTAL bucket (never dropped). Surface/
     enumeration: GET `?pg=N` paginates SERVER-side cleanly (disjoint card sets per page; total=939,
     total_pages=79, 12 cards/page live 2026-06-13). The card gives every field except the seller; one
     extra PDP GET per car resolves seller (Organization name) + VIN (the stable native listing_ref).
     t0_open (no WAF).

PROOF SLICE, NOT THE FULL HARVEST. faciliteacoches declares ~21,989 cars (the ficha sitemap index);
RACC declares 939 (ajax total). Each member caps at MAX_PAGES/MAX_CARS (logged honestly) and records
the declared full count for the VAM slice arithmetic; the full drain is the full governed run.

Run: python -m pipeline.platform.faciliteacoches_racc_wholesale --pages 6
     python -m pipeline.platform.faciliteacoches_racc_wholesale --members faciliteacoches --pages 8
     python -m pipeline.platform.faciliteacoches_racc_wholesale --members racc --pages 10
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import html as _html
import json
import os
import re
import sys
from dataclasses import dataclass, field

import asyncpg
from curl_cffi import requests as cffi_requests

from pipeline.engine.governor import governor, host_of
from pipeline.geo import GeoResolver
from pipeline.ids import ulid
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict
from services.api.codes import _base32, cdp_code

DSN = os.environ.get("CARDEEP_DSN",
                     "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# ---------------------------------------------------------------------------
# Shared identity / knobs.
# ---------------------------------------------------------------------------
PLATFORM_KIND = "plataforma"        # both channels are aggregator platforms.
SELLING_KIND = "compraventa"        # a per-shop / per-dealer selling point.
PLATFORM_PROVINCE_SENTINEL = "00"   # national segment in a platform's cdp_code (mirrors marketplaces).
_IMPERSONATE = "chrome131"
_TIMEOUT = 45

DEFAULT_MAX_PAGES = 6
DEFAULT_CONCURRENCY = 6

# faciliteacoches PDP pages are heavy (one car each); cap pages*PDPs_PER_PAGE -> bounded slice.
FACI_PDPS_PER_PAGE = 12  # virtual page size for the sitemap-index drain (cars per "page").

_PORTAL_BUCKET_NAME = "Vendedor sin atribuir RACC"  # RACC car with no PDP seller -> portal bucket.


def _to_int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _prov_from_cp(cp) -> str | None:
    """A Spanish 5-digit postal code's first two digits ARE the INE province code (28xxx -> 28 Madrid,
    08xxx -> 08 Barcelona). Returns a zero-padded '01'..'52' or None."""
    if cp is None:
        return None
    digits = re.sub(r"[^\d]", "", str(cp))
    if len(digits) < 2:
        return None
    p = digits[:2]
    return p if "01" <= p <= "52" else None


def _price_float(v):
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f > 0 else None


def _km_guard(v):
    n = _to_int(v)
    if n is None:
        return None
    return n if 0 <= n <= 5_000_000 else None


def _year_guard(v):
    n = _to_int(v)
    if n is None:
        return None
    return n if 1900 <= n <= 2100 else None


# ===========================================================================
# Parsed shapes
# ===========================================================================


@dataclass
class Vehicle:
    """A car parsed from either channel's data-layer (REAL field map per member)."""
    deep_link: str
    listing_ref: str            # native id (faciliteacoches id_mf / RACC VIN)
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    prev_price: float | None    # previous price -> price-drop delta (faciliteacoches prevPrice)
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    # owner attribution carried on the car itself:
    owner_name: str | None      # shopData.name (faciliteacoches) | seller Organization name (RACC)
    owner_province: str | None  # INE code resolved from shopData.cp (faciliteacoches); None for RACC
    owner_city: str | None      # shopData.city (faciliteacoches); None for RACC
    owner_key: str | None       # shopData.id_mf (faciliteacoches) | normalized seller name (RACC)
    dealer_group: str | None    # dealerData.name parent group (faciliteacoches); None for RACC


@dataclass
class CageRow:
    """One fully-parsed, owner-resolved car ready for the bulk cage. ONE shape serves both members.
    Geo-anchored selling point (faciliteacoches shop) -> owner_kind='compraventa' with province+muni;
    national dealer (RACC, no surface geo) -> owner_kind='compraventa' province NULL; unattributable
    car -> the PLATFORM entity bucket (owner_cdp == platform_cdp)."""
    owner_cdp: str
    owner_name: str | None
    owner_province: str | None
    owner_muni: str | None
    source_ref: str
    is_platform_bucket: bool
    vehicle: Vehicle


# ===========================================================================
# FACILITEACOCHES member (per-shop owner; sitemap-index PDP drain; RSC car object)
# ===========================================================================

FACI_DOMAIN = "faciliteacoches.com"
FACI_LEGAL_NAME = "Facilitea Coches"
FACI_TRADE_NAME = "Facilitea Coches"
FACI_SOURCE_KEY = "faciliteacoches_wholesale"
FACI_FAMILY = "faciliteacoches"
FACI_SITEMAP = "https://faciliteacoches.com/peninsula-baleares/sitemap/coches-ficha.xml"
FACI_SRP = "https://www.faciliteacoches.com/es/es/coches/ocasion/compra"
FACI_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.faciliteacoches.com/",
}
_NEXT_F_RE = re.compile(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', re.S)


def platform_cdp_code(domain: str) -> str:
    """A platform's immutable cdp_code, built from the bare domain identity (canonical_key
    'domain:<domain>') with the national province segment '00'. Mirrors every other connector."""
    key = f"domain:{domain}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


def _decode_next_f(html_text: str) -> str:
    """Join + JSON-decode the Next.js RSC flight chunks (self.__next_f.push([1,"..."])) into the
    single escaped payload string that carries the car objects. Empty string when none present."""
    chunks = _NEXT_F_RE.findall(html_text)
    if not chunks:
        return ""
    try:
        return json.loads('"' + "".join(chunks) + '"')
    except (ValueError, TypeError):
        return ""


def _extract_faci_cars(payload: str) -> list[dict]:
    """Extract every top-level car object from a decoded RSC payload. Each car object starts with the
    literal `{"site":"es"` and carries an `"id_mf"` key; we balance braces with string/escape
    awareness so nested objects (matrixRenting, dealerData, shopData) never break the scan. Returns
    the list of parsed dicts (the PDP yields one; the SRP yields the page window)."""
    cars: list[dict] = []
    seen_spans: set[int] = set()
    pos = 0
    needle = '{"site":"es"'
    while True:
        st = payload.find(needle, pos)
        if st < 0:
            break
        pos = st + len(needle)
        if st in seen_spans:
            continue
        # the object must carry an id_mf shortly after to be a car (not some other site:es blob).
        if payload.find('"id_mf"', st, st + 200) < 0:
            continue
        depth = 0
        instr = False
        esc = False
        end = -1
        for j in range(st, len(payload)):
            c = payload[j]
            if esc:
                esc = False
                continue
            if c == "\\":
                esc = True
                continue
            if c == '"':
                instr = not instr
                continue
            if instr:
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    end = j + 1
                    break
        if end < 0:
            continue
        try:
            o = json.loads(payload[st:end])
        except (ValueError, TypeError):
            continue
        if "id_mf" in o:
            cars.append(o)
            seen_spans.add(st)
            pos = end
    return cars


def parse_faci_car(o: dict) -> Vehicle | None:
    """Parse one faciliteacoches RSC car object into a Vehicle with per-shop owner attribution.

    Owner = the PHYSICAL shop (shopData) where the car sits: its own name + cp(->INE province) + city.
    The dealerData parent group is kept as dealer_group (provenance). When shopData lacks a usable cp,
    fall back to dealerData's cp/province/city; when neither geo-resolves, owner_province stays None
    and the resolver cages the car under the platform bucket (never dropped, never fabricated)."""
    id_mf = o.get("id_mf")
    slug = o.get("slug")
    if id_mf is None or not slug:
        return None
    deep_link = f"https://www.faciliteacoches.com/es/es/ficha/{slug}"
    make = o.get("make")
    model = o.get("model")
    version = o.get("version")
    title = o.get("name") or " ".join(p for p in (make, model, version) if p) or None

    sh = o.get("shopData")
    dd = o.get("dealerData")
    # the RSC stream sometimes emits shopData/dealerData as an unresolved reference (a "$..." string)
    # instead of the object; treat any non-dict as absent so attribution degrades gracefully.
    if not isinstance(sh, dict):
        sh = {}
    if not isinstance(dd, dict):
        dd = {}
    # prefer the physical shop's geo; fall back to the dealer group's HQ geo.
    cp = sh.get("cp") or dd.get("cp")
    prov = _prov_from_cp(cp)
    owner_name = sh.get("name") or dd.get("name")
    owner_city = sh.get("city") or dd.get("city")
    owner_key = sh.get("id_mf") or dd.get("id_mf") or sh.get("id") or dd.get("id")

    gearbox = o.get("gearbox")
    trans = None
    if isinstance(gearbox, str) and gearbox:
        trans = "Automático" if gearbox.lower().startswith("auto") else "Manual"

    photo = None
    imgs = o.get("imgs")
    if isinstance(imgs, list) and imgs and isinstance(imgs[0], dict):
        photo = imgs[0].get("src")

    return Vehicle(
        deep_link=deep_link, listing_ref=str(id_mf), title=title, make=make, model=model,
        year=_year_guard(o.get("registrationDate") or o.get("year")),
        km=_km_guard(o.get("km")), price=_price_float(o.get("price")),
        prev_price=_price_float(o.get("prevPrice")), fuel=o.get("fuel"),
        transmission=trans, photo_url=photo, owner_name=owner_name,
        owner_province=prov, owner_city=owner_city,
        owner_key=str(owner_key) if owner_key is not None else None,
        dealer_group=dd.get("name"))


# ===========================================================================
# RACC member (per-dealer-by-name owner; ?pg=N card drain + PDP seller enrich)
# ===========================================================================

RACC_DOMAIN = "racc.es"               # the parent club; the VO portal lives on cochesocasion.racc.es.
RACC_PORTAL_HOST_DOMAIN = "cochesocasion.racc.es"
RACC_LEGAL_NAME = "RACC Coches de Ocasión"
RACC_TRADE_NAME = "RACC Coches de Ocasión"
RACC_SOURCE_KEY = "racc_ocasion_wholesale"
RACC_FAMILY = "racc"
RACC_SRP = "https://cochesocasion.racc.es/coches-ocasion/vehiculos-de-ocasion/"
RACC_PDP_BASE = "https://cochesocasion.racc.es/coches-ocasion/vehiculos-de-ocasion/"
RACC_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://cochesocasion.racc.es/coches-ocasion/vehiculos-de-ocasion/",
}
RACC_PAGE_SIZE = 12  # cards per ?pg=N page (server-side paginated; total_pages * 12 ~= total).

# one result card is a `<div id="wrapper-{id}" ...> ... </div>` swiper slide; split on the wrapper.
_RACC_WRAPPER_RE = re.compile(r'<div id="wrapper-(\d+)"(.*?)(?=<div id="wrapper-\d+"|<div class="pagination)', re.S)
_RACC_SLUG_RE = re.compile(r'/vehiculos-de-ocasion/([a-z0-9-]+)/"')
_RACC_TITLE_RE = re.compile(r'car-card__title mb-3">([^<]+)</h5>')
_RACC_SUB_RE = re.compile(r'car-card__subtitle">([^<]+)</h6>')
_RACC_YEAR_RE = re.compile(r'Matriculaci[^:<]*:\s*&nbsp;\s*(\d{4})')
_RACC_KM_RE = re.compile(r'Kilometraje:\s*&nbsp;\s*([\d.]+)')
_RACC_PRICE_RE = re.compile(r'car-card__title mb-0">([\d.]+)')
_RACC_CMP_RE = re.compile(r'addToCompare\((\d+)\)')
_RACC_LABEL_RE = re.compile(r'card-icon-grid__label">([^<]+)</label>')
_RACC_IMG_RE = re.compile(r'<img class="car-card__image"\s+src="([^"]+)"')
_RACC_TOTAL_PAGES_RE = re.compile(r'pagination__pages-left">de\s*(\d+)')

# fuel labels RACC renders in the icon grid (UPPER) vs transmission (lower); classify by membership.
_RACC_FUELS = {"GASOLINA", "DIESEL", "DIÉSEL", "HÍBRIDO", "HIBRIDO", "ELÉCTRICO", "ELECTRICO",
               "HÍBRIDO ENCHUFABLE", "GLP", "GNC", "HÍBRIDO/GASOLINA"}
_RACC_TRANS = {"AUTOMÁTICO", "AUTOMATICO", "MANUAL"}


def _norm_seller_key(name: str | None) -> str | None:
    """Normalize a RACC seller Organization name to a stable per-dealer key (lowercased, collapsed
    whitespace). The seller has no id on the surface, so its normalized name IS its identity — two
    cars from 'Grupo M-AUTOMOCION' must collapse to one dealer entity, never fabricated."""
    if not name:
        return None
    k = re.sub(r"\s+", " ", name.strip()).lower()
    return k or None


def parse_racc_cards(html_text: str) -> tuple[list[Vehicle], int | None]:
    """Parse a RACC ?pg=N SRP page -> (vehicles, total_pages). Each result is one `<div id=wrapper-{id}>`
    swiper slide carrying make/model/version/year/km/price/fuel/transmission/photo + the native
    compare-id + the PDP deep link. The SELLER is NOT on the card (it is on the PDP) — owner_name is
    left None here and filled by the PDP enrich pass."""
    total_pages = None
    m = _RACC_TOTAL_PAGES_RE.search(html_text)
    if m:
        total_pages = _to_int(m.group(1))
    vehicles: list[Vehicle] = []
    for wid, body in _RACC_WRAPPER_RE.findall(html_text):
        slug_m = _RACC_SLUG_RE.search(body)
        if not slug_m:
            continue
        slug = slug_m.group(1)
        deep_link = f"{RACC_PDP_BASE}{slug}/"
        cmp_m = _RACC_CMP_RE.search(body)
        native_id = cmp_m.group(1) if cmp_m else wid
        title_m = _RACC_TITLE_RE.search(body)
        sub_m = _RACC_SUB_RE.search(body)
        make_model = _html.unescape(title_m.group(1).strip()) if title_m else None
        version = _html.unescape(sub_m.group(1).strip()) if sub_m else None
        make = make_model.split(" ", 1)[0] if make_model else None
        model = make_model.split(" ", 1)[1] if make_model and " " in make_model else None
        title = " ".join(p for p in (make_model, version) if p) or make_model
        year_m = _RACC_YEAR_RE.search(body)
        km_m = _RACC_KM_RE.search(body)
        price_m = _RACC_PRICE_RE.search(body)
        img_m = _RACC_IMG_RE.search(body)
        fuel = None
        trans = None
        for lbl in _RACC_LABEL_RE.findall(body):
            up = _html.unescape(lbl.strip()).upper()
            if up in _RACC_FUELS and fuel is None:
                fuel = _html.unescape(lbl.strip())
            elif up in _RACC_TRANS and trans is None:
                trans = _html.unescape(lbl.strip()).capitalize()
        vehicles.append(Vehicle(
            deep_link=deep_link, listing_ref=str(native_id), title=title, make=make, model=model,
            year=_year_guard(year_m.group(1)) if year_m else None,
            km=_km_guard(re.sub(r"[^\d]", "", km_m.group(1))) if km_m else None,
            price=_price_float(re.sub(r"[^\d]", "", price_m.group(1))) if price_m else None,
            prev_price=None, fuel=fuel, transmission=trans,
            photo_url=img_m.group(1) if img_m else None,
            owner_name=None, owner_province=None, owner_city=None,
            owner_key=None, dealer_group=None))
    return vehicles, total_pages


_RACC_LD_RE = re.compile(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S)


def parse_racc_pdp_seller(html_text: str) -> tuple[str | None, str | None]:
    """Parse a RACC PDP -> (seller_name, vin). The seller is offers.seller.name (Organization) in the
    `@type:Car` JSON-LD; the VIN is vehicleIdentificationNumber (the stable native id). Either may be
    None (a car with no declared seller caged under the portal bucket; VIN falls back to the card id)."""
    seller = None
    vin = None
    for block in _RACC_LD_RE.findall(html_text):
        try:
            d = json.loads(block)
        except (ValueError, TypeError):
            continue
        if not isinstance(d, dict) or d.get("@type") != "Car":
            continue
        vin = d.get("vehicleIdentificationNumber") or vin
        offers = d.get("offers") or {}
        if isinstance(offers, dict):
            sl = offers.get("seller") or {}
            if isinstance(sl, dict):
                seller = sl.get("name") or seller
    return (seller.strip() if isinstance(seller, str) else seller,
            str(vin).strip() if vin is not None else None)


# ===========================================================================
# Member descriptor
# ===========================================================================


@dataclass
class Member:
    key: str
    domain: str                 # the identity domain for the platform cdp_code.
    legal_name: str
    trade_name: str
    family: str
    source_group: str           # entity.source_group literal.
    data_surface: str           # platform_meta data_surface literal (schema-valid CHECK value).
    surface_intent: str
    endpoint: str               # the harvested data-layer entry URL (for meta/recipe).
    host: str
    page_size: int
    recipe: dict
    pdp_host: str = ""          # second host paced when a member also fetches PDPs (RACC/faciliteacoches).


FACI_RECIPE = {
    "version": 1,
    "source": "faciliteacoches.com",
    "group": "marketplace_motor",
    "scope": "VO aggregator wholesale (Facilitea Coches; sitemap-index PDP drain; Next.js RSC car object)",
    "engine": "curl_cffi+chrome131_impersonate+sitemap_index+rsc_car_object(GET)",
    "access": ("OPEN server-rendered Next.js App Router on Vercel (Chrome TLS fingerprint; no proxy, "
               "no browser, no cookie warm-up). No WAF challenge -> defense_tier t0_open."),
    "data_surface": "next_data",
    "surface_intent": "sitemap_index_pdp_rsc",
    "endpoint": "GET sitemap /peninsula-baleares/sitemap/coches-ficha.xml -> per-car PDP /es/es/ficha/{slug}-{id_mf}",
    "enumeration": ("the SRP /coches/ocasion/compra resolves results through a DEFERRED RSC server "
                    "promise (?page=N ignored; browser pages via a Next.js server action, not header-"
                    "reachable). CANONICAL full index = sitemap coches-ficha.xml (21,989 PDP URLs live). "
                    "Drain PDP-by-PDP: each PDP re-emits the RSC car object with full attribution."),
    "platform_entity": ("kind=plataforma, province_code=NULL (sentinel 00 in cdp_code), is_tier1=FALSE, "
                        "defense_tier=t0_open, source_group=marketplace_motor, role=platform, family=faciliteacoches"),
    "ownership": ("PER-SHOP: each car attributes to its REAL physical selling shop (shopData: "
                  "name+cp(INE prov)+city), parented by dealerData group. vehicle.entity_ulid=shop; "
                  "platform_listing edge=platform<->vehicle. A car whose shop/dealer geo cannot be "
                  "resolved cages under the platform bucket (never dropped, never fabricated)."),
    "field_map": {
        "deep_link": "https://www.faciliteacoches.com/es/es/ficha/{car.slug}",
        "listing_ref": "car.id_mf (Facilitea native stock id == PDP slug tail)",
        "make": "car.make", "model": "car.model", "version": "car.version", "title": "car.name",
        "year": "car.registrationDate||car.year", "km": "car.km", "price": "car.price",
        "prev_price": "car.prevPrice (price-drop delta)", "fuel": "car.fuel (clean ES label)",
        "transmission": "car.gearbox (automatico->Automático / else Manual)",
        "photo_url": "car.imgs[0].src",
        "shop": "car.shopData {id_mf,name,province,region,cp,city}  (the PHYSICAL selling point)",
        "dealer_group": "car.dealerData {id_mf,name,slug,province,cp,city}  (the parent OEM/dealer group)",
    },
    "caveats": {
        "rsc_pagination": ("the SRP returns the SAME first ~39 cars for every ?page/path variant — its "
                           "results are a deferred RSC promise; full enumeration MUST use the ficha sitemap."),
        "shop_vs_dealer": ("shopData.cp is the car's real location (varies per car); dealerData.cp is the "
                           "dealer-group HQ (constant across a group's cars) — anchor geo to the SHOP first."),
        "data_surface_label": ("schema CHECK has no 'sitemap_index' literal; stored as 'next_data' (the RSC "
                               "car object we parse) with surface_intent precise."),
    },
}

RACC_RECIPE = {
    "version": 1,
    "source": "cochesocasion.racc.es",
    "group": "association",
    "scope": "auto-club VO portal wholesale (RACC; ?pg=N SRP card drain + PDP JSON-LD seller enrich)",
    "engine": "curl_cffi+chrome131_impersonate+ssr_html_cards+pdp_jsonld_seller(GET)",
    "access": ("OPEN server-rendered WordPress HTML (Apache/PHP 8.3; Chrome TLS fingerprint; no proxy, "
               "no browser, no cookie warm-up). No WAF -> defense_tier t0_open."),
    "data_surface": "json_ld",
    "surface_intent": "ssr_html_cards_plus_pdp_jsonld",
    "endpoint": "GET https://cochesocasion.racc.es/coches-ocasion/vehiculos-de-ocasion/?pg=N",
    "enumeration": ("?pg=1..N paginates SERVER-side (disjoint card sets per page; 12 cards/page). The "
                    "SRP pagination declares total_pages ('de 79'); admin-ajax get_search_result "
                    "declares total=939 live. Per-car PDP GET resolves seller + VIN."),
    "platform_entity": ("kind=plataforma, province_code=NULL (sentinel 00 in cdp_code), is_tier1=FALSE, "
                        "defense_tier=t0_open, source_group=association, role=platform, family=racc"),
    "ownership": ("PER-DEALER-BY-NAME: the card carries the car but not the seller; the PDP JSON-LD "
                  "offers.seller (Organization name) IS the dealer. The portal exposes NO per-car "
                  "province/address (national inventory aggregation), so the dealer is anchored national "
                  "(province NULL). vehicle.entity_ulid=dealer; platform_listing edge=portal<->vehicle. "
                  "A car whose PDP has no seller cages under the portal bucket (never dropped)."),
    "field_map": {
        "card_id": "addToCompare({id}) / <div id=wrapper-{id}> (native compare id)",
        "deep_link": "card <a href> .../vehiculos-de-ocasion/{slug}/",
        "listing_ref": "PDP vehicleIdentificationNumber (VIN; stable) — falls back to card id",
        "make/model": "h5.car-card__title (Make Model)", "version": "h6.car-card__subtitle",
        "year": "card 'Matriculación: {YYYY}'", "km": "card 'Kilometraje: {n}'",
        "price": "card .car-card__title.mb-0 '{n}€'", "fuel": "card .card-icon-grid__label (fuel set)",
        "transmission": "card .card-icon-grid__label (Automático/Manual)",
        "photo_url": "card img.car-card__image src",
        "seller": "PDP @type:Car offers.seller.name (Organization) -> per-dealer owner",
    },
    "caveats": {
        "no_surface_geo": ("the SRP and PDP expose NO per-car province/address; the dealer is anchored "
                           "national (province NULL). Per-branch geo would need a deeper concessionaire "
                           "map probe (concessionarie-map-item) — never fabricated here."),
        "page_param": "?pg=N is the working server-side page param; ?page/?pagina/path/N are ignored.",
        "ajax_total": "admin-ajax.php action=get_search_result returns total/total_pages (939 / 79 live).",
    },
}


def build_faciliteacoches() -> Member:
    return Member(
        key=FACI_SOURCE_KEY, domain=FACI_DOMAIN, legal_name=FACI_LEGAL_NAME,
        trade_name=FACI_TRADE_NAME, family=FACI_FAMILY, source_group="marketplace_motor",
        data_surface="next_data", surface_intent="sitemap_index_pdp_rsc", endpoint=FACI_SITEMAP,
        host=host_of(FACI_SRP), page_size=FACI_PDPS_PER_PAGE, recipe=FACI_RECIPE,
        pdp_host=host_of("https://www.faciliteacoches.com/"))


def build_racc() -> Member:
    return Member(
        key=RACC_SOURCE_KEY, domain=RACC_PORTAL_HOST_DOMAIN, legal_name=RACC_LEGAL_NAME,
        trade_name=RACC_TRADE_NAME, family=RACC_FAMILY, source_group="association",
        data_surface="json_ld", surface_intent="ssr_html_cards_plus_pdp_jsonld", endpoint=RACC_SRP,
        host=host_of(RACC_SRP), page_size=RACC_PAGE_SIZE, recipe=RACC_RECIPE,
        pdp_host=host_of(RACC_PDP_BASE))


MEMBER_BUILDERS = {"faciliteacoches": build_faciliteacoches, "racc": build_racc}


# ===========================================================================
# Fetch: a POOL of fingerprint-coherent curl_cffi sessions, routed THROUGH the governor.
# ===========================================================================


class WebFetcher:
    """One curl_cffi Session per concurrency slot (a single shared session is not thread-safe under the
    governor's to_thread fetch). The governor's per-host bucket bounds the aggregate rate, so the pool
    widens parallelism WITHOUT out-pacing the host (the bucket is the limiter)."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch_get(self, url: str, *, headers: dict | None = None, slot: int = 0) -> str:
        """Synchronous GET on pool session `slot` (runs in a worker thread). Returns decoded text.
        Raises on non-200 so the breaker sees throttling (never masks a challenge/empty body)."""
        session = self._sessions[slot]
        resp = session.get(url, headers=headers or {}, impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url}")
        return resp.content.decode("utf-8", "replace")

    async def fetch_async(self, governed_fetch, url: str, **kw) -> str:
        """Lease a pool slot, fetch THROUGH the governor on that slot, release it. `governed_fetch` is
        governor().wrap_fetch_text(self.fetch_get); the governor paces the host then runs the
        synchronous GET off the event loop with `slot` forwarded untouched."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, slot=slot, **kw)
        finally:
            self._free.put_nowait(slot)


# ===========================================================================
# DB layer — ensure the platform entity, bulk-upsert per-shop/per-dealer owners, bulk-insert vehicles
# + edges + NEW events, all idempotent ON CONFLICT (BULK unnest). Byte-identical to the group template.
# ===========================================================================


async def ensure_platform_entity(conn: asyncpg.Connection, m: Member) -> str:
    """Idempotently ensure the platform's entity + platform_meta exist. Returns the platform ulid.
    kind=plataforma, role=platform, province NULL (national; '00' in cdp_code), is_tier1=FALSE,
    defense_tier=t0_open (both channels are unwalled first-party surfaces)."""
    code = platform_cdp_code(m.domain)
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               sells_cars, defense_tier, source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,$3::entity_kind,$4,$5,NULL,$6,'none'::waf_kind,FALSE,'active','platform_label',
               TRUE,'t0_open'::defense_tier,$7::source_group,'platform'::entity_role,$8, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, defense_tier = EXCLUDED.defense_tier,
               source_group = EXCLUDED.source_group, role = EXCLUDED.role,
               kind = EXCLUDED.kind, legal_name = EXCLUDED.legal_name""",
        eulid, code, PLATFORM_KIND, m.legal_name, m.trade_name, m.domain, m.source_group, m.key)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, m.key, m.domain)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,$2,$3::jsonb,FALSE,FALSE,$4)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, m.data_surface,
        json.dumps({"endpoint": m.endpoint, "host": m.host, "method": "GET",
                    "page_size": m.page_size, "surface_intent": m.surface_intent,
                    "engine": "curl_cffi/chrome131_impersonate"}),
        m.family)
    return eulid


def cdp_code_owner(name: str, province: str | None, muni: str | None, ref: str) -> str:
    """Mint a selling point's immutable cdp_code via the canonical generator. The shop/dealer has no
    bare domain (it lives under the aggregator) -> identity = name + location + the stable per-owner
    ref (shop id_mf / normalized seller name), passed via `address` so two owners sharing a name in one
    municipality never collapse to one entity.

    A NATIONAL owner (RACC dealer / shop with no resolvable geo) has no INE province on the surface, so
    its code uses the '00' national sentinel as the province segment — canonical_key then falls into
    the (name + province_code 'p00') branch keyed by the stable owner ref. The ENTITY row still stores
    province_code = NULL (the '00' is a geo_province non-FK sentinel that lives only in the code
    string, exactly like the platform entity). A geo-anchored owner passes its real INE province."""
    seg_province = province if province else PLATFORM_PROVINCE_SENTINEL
    return cdp_code(province_code=seg_province, domain=None, name=name,
                    municipality_code=muni, address=f"owner:{ref}")


# The bulk statements — ONE round-trip per table per window (unnest multi-row upsert), byte-for-byte
# the same idempotency every other connector uses. A re-run of an already-harvested window adds 0
# rows and 0 events.

_BULK_UPSERT_OWNERS = """
INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
        province_code, municipality_code, is_tier1, status, kind_source,
        sells_cars, defense_tier, source_group, role, first_discovered_source, last_seen)
SELECT u.entity_ulid, u.cdp_code, 'compraventa'::entity_kind, u.name, u.name,
       u.province_code, u.municipality_code, FALSE, 'active', 'platform_label',
       TRUE, 't0_open'::defense_tier, $8::source_group, 'standalone_pos'::entity_role, $9, now()
  FROM unnest($1::text[], $2::text[], $3::text[], $4::char(2)[], $5::char(5)[],
              $6::text[], $7::text[]) AS u(entity_ulid, cdp_code, name, province_code,
                               municipality_code, source_ref, _ref)
ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()
"""

_BULK_UPSERT_OWNER_SOURCES = """
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


def resolve_cage_rows(vehicles: list[Vehicle], m: Member, platform_ulid: str, platform_cdp: str,
                      geo: GeoResolver, seen_ids: set, harvested_cageable: set,
                      stats: dict) -> list[CageRow]:
    """Resolve every parsed vehicle to its owner — pure CPU, no SQL. A geo-anchored selling point
    (faciliteacoches shop with a valid INE province) routes to a compraventa entity geo-resolved from
    its cp+city; a national dealer (RACC seller, no surface geo) routes to a compraventa entity with
    province NULL; an unattributable car (no owner name/key) routes to the PLATFORM bucket so a real
    car is never dropped. Cross-page dedup on listing_ref. Cageable truth = distinct
    (owner_cdp, deep_link)."""
    rows: list[CageRow] = []
    for v in vehicles:
        stats["items_seen"] += 1
        if v.listing_ref and v.listing_ref in seen_ids:
            stats["dup_ids_collapsed"] += 1
            continue
        if v.listing_ref:
            seen_ids.add(v.listing_ref)
        if not v.deep_link:
            stats["no_link_skipped"] += 1
            continue
        if v.prev_price is not None and v.price is not None and v.prev_price > v.price:
            stats["price_drops_captured"] += 1

        owner_name = v.owner_name
        owner_key = v.owner_key or _norm_seller_key(owner_name)
        if not owner_name or not owner_key:
            # no resolvable owner -> cage under the platform bucket (never dropped, never fabricated).
            stats["platform_bucket"] += 1
            harvested_cageable.add((platform_cdp, v.deep_link))
            rows.append(CageRow(owner_cdp=platform_cdp, owner_name=m.trade_name,
                                owner_province=None, owner_muni=None, source_ref=m.domain,
                                is_platform_bucket=True, vehicle=v))
            continue

        prov = v.owner_province
        muni = None
        if prov and prov.isdigit() and "01" <= prov <= "52":
            muni = geo.municipality_code(prov, v.owner_city)
            stats["owner_geo_anchored"] += 1
        else:
            prov = None  # national owner (RACC dealer / unresolved shop cp)
            stats["owner_national"] += 1
        owner_cdp = cdp_code_owner(owner_name, prov, muni, owner_key)
        harvested_cageable.add((owner_cdp, v.deep_link))
        rows.append(CageRow(owner_cdp=owner_cdp, owner_name=owner_name, owner_province=prov,
                            owner_muni=muni, source_ref=f"owner:{owner_key}",
                            is_platform_bucket=False, vehicle=v))
    return rows


async def ingest_window(conn: asyncpg.Connection, m: Member, platform_ulid: str, platform_cdp: str,
                        geo: GeoResolver, vehicles: list[Vehicle], seen_ids: set,
                        harvested_cageable: set, cdp_to_ulid: dict[str, str], stats: dict) -> None:
    """BULK-ingest a window of parsed cars in ONE transaction with set-based SQL. Geo-anchored / national
    owners are bulk-upserted (kind=compraventa) and mapped cdp->ulid; platform-bucket cars cage straight
    under the platform ulid. Then vehicles split existing/new (one SELECT), bulk-touch + bulk-insert,
    edges bulk-upsert (RETURNING counts new edges), NEW events fire for genuinely new vehicles only.
    Idempotency/delta/VAM semantics are byte-identical to group_vo_chains_wholesale."""
    cage = resolve_cage_rows(vehicles, m, platform_ulid, platform_cdp, geo, seen_ids,
                             harvested_cageable, stats)
    if not cage:
        return

    async with conn.transaction():
        # ---- OWNERS: dedup real selling points by cdp_code; the platform cdp resolves to platform_ulid.
        owners: dict[str, CageRow] = {}
        for r in cage:
            if not r.is_platform_bucket and r.owner_cdp not in cdp_to_ulid:
                owners.setdefault(r.owner_cdp, r)
        if owners:
            cdps = list(owners.keys())
            ulids = [ulid() for _ in cdps]
            names = [owners[c].owner_name for c in cdps]
            provs = [owners[c].owner_province for c in cdps]
            munis = [owners[c].owner_muni for c in cdps]
            refs = [owners[c].source_ref for c in cdps]
            await conn.execute(_BULK_UPSERT_OWNERS, ulids, cdps, names, provs, munis, refs,
                               refs, m.source_group, m.key)
            await conn.execute(_BULK_UPSERT_OWNER_SOURCES, cdps, refs, m.key)
            for row in await conn.fetch(
                    "SELECT cdp_code, entity_ulid FROM entity WHERE cdp_code = ANY($1::text[])", cdps):
                cdp_to_ulid[row["cdp_code"]] = row["entity_ulid"]
        cdp_to_ulid[platform_cdp] = platform_ulid

        # ---- attach owner ulid to each car; dedup within the window by (owner_ulid, deep_link).
        cars: dict[tuple[str, str], CageRow] = {}
        for r in cage:
            ou = cdp_to_ulid.get(r.owner_cdp)
            if ou is None:
                continue
            key = (ou, r.vehicle.deep_link)
            cars.setdefault(key, r)

        car_keys = list(cars.keys())
        if not car_keys:
            return
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
                vehicle_ulid_for[key] = ulid()
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
                [x[3].photo_url for x in ins], [x[3].listing_ref for x in ins])
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
                    vehicle_ulid_for[k] = real
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

        # ---- EDGES: platform<->vehicle. RETURNING (xmax=0) counts genuinely new edges.
        e_vehicles = [vehicle_ulid_for[k] for k in car_keys]
        e_urls = [cars[k].vehicle.deep_link for k in car_keys]
        e_refs = [cars[k].vehicle.listing_ref for k in car_keys]
        e_prices = [cars[k].vehicle.price for k in car_keys]
        edge_rows = await conn.fetch(_BULK_UPSERT_EDGES, e_vehicles, e_urls, e_refs,
                                     e_prices, platform_ulid)
        stats["edges_created"] += sum(1 for row in edge_rows if row["inserted"])

        # ---- NEW delta events — only for genuinely new vehicles, price-drop preserved.
        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                v = cars[k].vehicle
                payload = {"price": v.price, "title": v.title, "platform": m.trade_name}
                if v.prev_price is not None and v.price is not None and v.prev_price > v.price:
                    payload["price_drop"] = {"from": v.prev_price, "to": v.price,
                                             "amount": v.prev_price - v.price}
                if v.dealer_group:
                    payload["dealer_group"] = v.dealer_group
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities, ev_payloads)
            stats["new_events"] += len(confirmed_new)


# ===========================================================================
# Per-member harvest
# ===========================================================================


async def _faci_load_pdp_index(fetcher: WebFetcher, governed_sitemap) -> list[str]:
    """Fetch the faciliteacoches ficha sitemap (through the governor) and return every car PDP URL.
    This is the canonical full-stock index (the SRP cannot be header-paginated). Empty on failure."""
    try:
        xml = await fetcher.fetch_async(governed_sitemap, FACI_SITEMAP, headers=FACI_HEADERS)
    except Exception:
        return []
    return re.findall(r"<loc>(.*?/ficha/.*?)</loc>", xml)


async def harvest_member(conn: asyncpg.Connection, member_name: str, geo: GeoResolver,
                         max_pages: int, concurrency: int) -> dict:
    """Drain ONE channel member end to end: ensure the platform entity, drain its data-layer
    concurrently through the governor, BULK-cage every window, write the recipe, run the VAM quorum,
    record the S-HEALTH heartbeat. Returns the member's stats dict."""
    m = MEMBER_BUILDERS[member_name]()
    fetcher = WebFetcher(pool_size=concurrency)
    gov = governor()
    governed_get = gov.wrap_fetch_text(fetcher.fetch_get)

    stats = {
        "member": member_name, "source_key": m.key, "pages_fetched": 0, "items_seen": 0,
        "cars_caged": 0, "new_cars": 0, "edges_created": 0, "new_events": 0,
        "price_drops_captured": 0, "declared_full": None, "dup_ids_collapsed": 0,
        "no_link_skipped": 0, "owner_geo_anchored": 0, "owner_national": 0,
        "platform_bucket": 0, "pdp_fetched": 0, "pdp_failed": 0,
        "concurrency": concurrency, "max_pages": max_pages,
    }
    harvested_cageable: set[tuple[str, str]] = set()

    if await is_open(conn, m.key):
        print(f"[facilitea_racc:{member_name}] breaker OPEN for {m.key}; skipping drain "
              f"(graceful degradation, site still serves last snapshot).")
        return {**stats, "skipped": True, "reason": "breaker_open"}

    fetch_error: str | None = None
    last_http: int | None = None
    platform_ulid = await ensure_platform_entity(conn, m)
    platform_cdp = platform_cdp_code(m.domain)
    cdp_to_ulid: dict[str, str] = {platform_cdp: platform_ulid}
    edges_before = await conn.fetchval(
        "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)

    print(f"[facilitea_racc:{member_name}] platform entity ready: {platform_cdp} (ulid={platform_ulid}) "
          f"kind=plataforma group={m.source_group} role=platform family={m.family}")
    print(f"[facilitea_racc:{member_name}] governor paces host {m.host}"
          f"{(' + ' + m.pdp_host) if m.pdp_host and m.pdp_host != m.host else ''}; "
          f"CONCURRENT drain window={concurrency}, target={max_pages} pages (~{m.page_size} cars/page).")

    seen_ids: set[str] = set()

    if m.family == FACI_FAMILY:
        await _harvest_faciliteacoches(conn, m, fetcher, governed_get, geo, platform_ulid,
                                       platform_cdp, cdp_to_ulid, seen_ids, harvested_cageable,
                                       stats, max_pages, concurrency)
        fetch_error = stats.pop("_fetch_error", None)
        last_http = stats.pop("_last_http", None)
    else:
        await _harvest_racc(conn, m, fetcher, governed_get, geo, platform_ulid, platform_cdp,
                            cdp_to_ulid, seen_ids, harvested_cageable, stats, max_pages, concurrency)
        fetch_error = stats.pop("_fetch_error", None)
        last_http = stats.pop("_last_http", None)

    recipe_path = write_recipe(platform_cdp, m.recipe)
    stats["recipe_path"] = str(recipe_path)
    print(f"[facilitea_racc:{member_name}] recipe written: {recipe_path}")

    # VAM count quorum — THREE orthogonal like-with-like paths, all "distinct cageable cars":
    #   db_edges           = platform_listing rows for this platform  (DB write truth)
    #   db_join_vehicles   = distinct vehicles via the edge join       (DB read truth)
    #   harvested_cageable = distinct (owner_cdp, deep_link) pulled    (harvest truth)
    db_edges = await conn.fetchval(
        "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)
    db_join_vehicles = await conn.fetchval(
        """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
           JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
           JOIN entity e ON e.entity_ulid = v.entity_ulid
           WHERE pl.platform_entity_ulid=$1""", platform_ulid)
    harvested_cageable_n = len(harvested_cageable)
    verdict = await record_count_verdict(
        conn, subject_type="platform_slice", subject_key=platform_cdp,
        claim="distinct cageable cars (harvest) == platform_listing edges == join-reachable vehicles",
        paths={"db_edges": db_edges, "db_join_vehicles": db_join_vehicles,
               "harvested_cageable": harvested_cageable_n}, tolerance=0.0)
    stats["verdict"] = verdict
    stats["db_edges"] = db_edges
    stats["db_join_vehicles"] = db_join_vehicles
    stats["harvested_cageable"] = harvested_cageable_n
    stats["harvested_distinct_ids"] = len(seen_ids)
    stats["edges_new_this_run"] = db_edges - (edges_before or 0)
    stats["platform_code"] = platform_cdp
    stats["platform_ulid"] = platform_ulid
    stats["owners_distinct"] = await conn.fetchval(
        """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
           JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
           WHERE pl.platform_entity_ulid=$1""", platform_ulid)

    run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
    run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
    outcome = await record_run(conn, m.key, ok=run_ok, rows=stats["cars_caged"],
                               error=run_error, http_status=last_http)
    stats["health_status"] = outcome.status
    stats["breaker_state"] = outcome.breaker_state
    if not run_ok:
        stats["repair_action"] = await auto_repair(
            conn, m.key, run_error or "harvest failed", phase="scrape", http_status=last_http)
    return stats


async def _harvest_faciliteacoches(conn, m, fetcher, governed_get, geo, platform_ulid, platform_cdp,
                                   cdp_to_ulid, seen_ids, harvested_cageable, stats,
                                   max_pages, concurrency) -> None:
    """faciliteacoches: load the ficha sitemap index, then drain PDP-by-PDP in concurrent windows. Each
    PDP yields one fully-attributed RSC car object (dealerData + shopData). The full index size is the
    declared count; max_pages * FACI_PDPS_PER_PAGE bounds the proof slice."""
    pdp_urls = await _faci_load_pdp_index(fetcher, governed_get)
    stats["declared_full"] = len(pdp_urls)
    if not pdp_urls:
        stats["_fetch_error"] = "ficha sitemap index empty/unreachable"
        stats["_last_http"] = fetcher.last_status
        print(f"[facilitea_racc:faciliteacoches] ficha sitemap empty; stopping.")
        return
    print(f"[facilitea_racc:faciliteacoches] ficha sitemap index: {len(pdp_urls)} car PDPs (declared full).")

    target = min(max_pages * FACI_PDPS_PER_PAGE, len(pdp_urls))
    todo = pdp_urls[:target]
    stop = False
    idx = 0
    page_no = 0
    while idx < len(todo) and not stop:
        window = todo[idx: idx + concurrency]
        idx += len(window)
        results = await asyncio.gather(
            *(fetcher.fetch_async(governed_get, u, headers=FACI_HEADERS) for u in window),
            return_exceptions=True)
        window_vehicles: list[Vehicle] = []
        for url, data in zip(window, results):
            if isinstance(data, Exception):
                stats["_fetch_error"] = str(data)
                stats["_last_http"] = fetcher.last_status
                stats["pdp_failed"] += 1
                print(f"[facilitea_racc:faciliteacoches] PDP fetch failed ({data}); stopping honestly.")
                stop = True
                break
            stats["pdp_fetched"] += 1
            payload = _decode_next_f(data)
            if not payload:
                continue
            for o in _extract_faci_cars(payload):
                v = parse_faci_car(o)
                if v is not None:
                    window_vehicles.append(v)
        if window_vehicles:
            await ingest_window(conn, m, platform_ulid, platform_cdp, geo, window_vehicles,
                                seen_ids, harvested_cageable, cdp_to_ulid, stats)
            page_no += 1
            stats["pages_fetched"] = page_no
            print(f"[facilitea_racc:faciliteacoches] window {page_no} ({stats['pdp_fetched']} PDPs): "
                  f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                  f"edges={stats['edges_created']} geo_anchored={stats['owner_geo_anchored']} "
                  f"national={stats['owner_national']} drops={stats['price_drops_captured']}")


async def _harvest_racc(conn, m, fetcher, governed_get, geo, platform_ulid, platform_cdp,
                        cdp_to_ulid, seen_ids, harvested_cageable, stats,
                        max_pages, concurrency) -> None:
    """RACC: drain ?pg=N SRP pages (12 cards each), then enrich each card with its PDP seller (the
    dealer) + VIN before caging the page. Cards carry every field except the seller; the PDP JSON-LD
    offers.seller resolves the per-dealer owner. A card whose PDP has no seller cages under the portal
    bucket (never dropped)."""
    stop = False
    next_page = 1
    while next_page <= max_pages and not stop:
        window = list(range(next_page, min(next_page + concurrency, max_pages + 1)))
        next_page = window[-1] + 1
        urls = [(RACC_SRP if p == 1 else f"{RACC_SRP}?pg={p}") for p in window]
        results = await asyncio.gather(
            *(fetcher.fetch_async(governed_get, u, headers=RACC_HEADERS) for u in urls),
            return_exceptions=True)

        window_vehicles: list[Vehicle] = []
        for page, data in zip(window, results):
            if isinstance(data, Exception):
                stats["_fetch_error"] = str(data)
                stats["_last_http"] = fetcher.last_status
                print(f"[facilitea_racc:racc] page {page} fetch failed ({data}); stopping honestly.")
                stop = True
                break
            cards, total_pages = parse_racc_cards(data)
            if stats["declared_full"] is None and total_pages is not None:
                stats["declared_full"] = total_pages * RACC_PAGE_SIZE
            if not cards:
                print(f"[facilitea_racc:racc] page {page}: no cards; stopping (boundary).")
                stop = True
                break
            window_vehicles.extend(cards)
            stats["pages_fetched"] += 1

        if not window_vehicles:
            continue

        # ---- PDP enrich pass: resolve seller (dealer) + VIN per card, concurrently through the governor.
        pdp_results = await asyncio.gather(
            *(fetcher.fetch_async(governed_get, v.deep_link, headers=RACC_HEADERS)
              for v in window_vehicles),
            return_exceptions=True)
        for v, pdp in zip(window_vehicles, pdp_results):
            if isinstance(pdp, Exception):
                stats["pdp_failed"] += 1
                continue
            stats["pdp_fetched"] += 1
            seller, vin = parse_racc_pdp_seller(pdp)
            if seller:
                v.owner_name = seller
                v.owner_key = _norm_seller_key(seller)
            if vin:
                v.listing_ref = vin  # the VIN is the stable native id (better than the compare id)

        await ingest_window(conn, m, platform_ulid, platform_cdp, geo, window_vehicles,
                            seen_ids, harvested_cageable, cdp_to_ulid, stats)
        print(f"[facilitea_racc:racc] window {window[0]}-{window[0]+len(window)-1}: "
              f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
              f"edges={stats['edges_created']} dealers_national={stats['owner_national']} "
              f"portal_bucket={stats['platform_bucket']} pdp={stats['pdp_fetched']}")


async def harvest(members: list[str], max_pages: int = DEFAULT_MAX_PAGES,
                  concurrency: int = DEFAULT_CONCURRENCY) -> list[dict]:
    """Drain each requested channel member sequentially against ONE shared connection (the per-host
    governor keeps each member's host paced; members hit different hosts so they never contend)."""
    conn = await asyncpg.connect(DSN)
    try:
        geo = await GeoResolver.load(conn)
        out = []
        for name in members:
            out.append(await harvest_member(conn, name, geo, max_pages, concurrency))
        return out
    finally:
        await conn.close()


def _print_report(all_stats: list[dict]) -> None:
    for stats in all_stats:
        name = stats.get("member")
        if stats.get("skipped"):
            print(f"\n[facilitea_racc:{name}] SKIPPED: {stats.get('reason')}")
            continue
        print("\n" + "=" * 66)
        print(f"FACILITEACOCHES+RACC WHOLESALE HARVEST — {name.upper()} — REPORT")
        print("=" * 66)
        print(f"  platform cdp_code     : {stats.get('platform_code')}")
        print(f"  declared full (source): {stats.get('declared_full')}")
        print(f"  concurrency / target  : {stats.get('concurrency')} in flight / {stats.get('max_pages')} pages")
        print(f"  pages fetched         : {stats['pages_fetched']}")
        print(f"  PDPs fetched / failed : {stats.get('pdp_fetched')} / {stats.get('pdp_failed')}")
        print(f"  items seen            : {stats['items_seen']}")
        print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page)")
        print(f"  no-link skipped       : {stats['no_link_skipped']}")
        print(f"  owners geo-anchored   : {stats.get('owner_geo_anchored')} "
              f"(national: {stats.get('owner_national')}, platform bucket: {stats.get('platform_bucket')})")
        print(f"  owners attributed     : {stats.get('owners_distinct')} distinct selling points")
        print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
        print(f"  platform_listing edges: {stats['edges_created']} created "
              f"(db total = {stats.get('db_edges')}, +{stats.get('edges_new_this_run')} this run)")
        print(f"  price drops captured  : {stats['price_drops_captured']}")
        print(f"  NEW delta events      : {stats['new_events']}")
        print("  --- VAM count quorum (like-with-like, this slice) ---")
        print(f"  harvested_cageable    : {stats.get('harvested_cageable')}")
        print(f"  db_edges              : {stats.get('db_edges')}")
        print(f"  db_join_vehicles      : {stats.get('db_join_vehicles')}")
        print(f"  VAM verdict           : {stats.get('verdict')}")
        print(f"  health status         : {stats.get('health_status')} / breaker {stats.get('breaker_state')}")
        print(f"  recipe                : {stats.get('recipe_path')}")
        print("=" * 66)


def _force_utf8_stdout() -> None:
    """Windows consoles/pipes default to cp1252, which cannot encode the accented car titles this
    connector prints (Híbrido, Diésel, Automático) — a raw print() then crashes the drain mid-flight.
    Reconfigure stdout/stderr to UTF-8 (errors='replace'). Idempotent, no-op where already UTF-8."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass


def main() -> None:
    _force_utf8_stdout()
    parser = argparse.ArgumentParser(
        description=("faciliteacoches (sitemap-index PDP RSC) + RACC ocasión (SRP cards + PDP JSON-LD "
                     "seller) wholesale harvester"))
    parser.add_argument("--members", nargs="+", default=["faciliteacoches", "racc"],
                        choices=sorted(MEMBER_BUILDERS.keys()),
                        help="which channel members to harvest; default both.")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"pages to harvest per member; default {DEFAULT_MAX_PAGES}.")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=f"requests in flight per window; default {DEFAULT_CONCURRENCY}.")
    args = parser.parse_args()
    all_stats = asyncio.run(harvest(args.members, args.pages, args.concurrency))
    _print_report(all_stats)


if __name__ == "__main__":
    main()
