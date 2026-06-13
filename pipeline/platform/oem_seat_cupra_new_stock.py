"""seat_cupra_new (SEAT + CUPRA ES official NEW-CAR stock locator) WHOLESALE harvester.

This is the OEM NEW-CAR stock surface for the SEAT/CUPRA brands in Spain — DISTINCT from the
OEM-VO certified-USED portal already harvested by `oem_seat_cupra_wholesale` (cupra.com /
dasweltauto). www.seat.es/localizador-stock and www.cupra.com/es-es/localizador-stock are the
two manufacturer-owned "localizador de stock" surfaces: a brand publishing the BRAND-NEW cars its
official dealer network (concesionarios oficiales) already has built and ready for immediate
delivery ("disponibilidad inmediata"). Every car here is segment='new' (available_from=Immediately,
a production date, NO mileage/registration), the new-stock sibling of the marketplace `segment=new`
slice already caged from coches.net — but here it is OEM-OFFICIAL and dealer-attributed per car.

Both SPAs embed the SAME backend: the VW-Group VTP (Vehicle Trade Platform) "stock locator" REST
service at vtpapi.seat.com/restapi/v1. They call ONE internal JSON API —
GET /restapi/v1/{stockType}/search/car — differing only by the per-brand stockType path segment
(SEAT=stesnwb, CUPRA=cuesnwb) and the `x-pattern` header (seatwebfe / cuprawebfe). The `x-pattern`
header IS the only access gate: with it the API serves HTTP 200 application/json to PLAIN curl_cffi
(no browser, no proxy, no cookie warm-up, no auth token, €0). Without it -> 401 VtpApiUnauthorized.
The host occasionally returns a transient 500 INTERNAL ERROR under burst; a short retry clears it,
and the per-host governor (STEALTH class) keeps the aggregate rate gentle. defense_tier=t0_open.
Verified live 2026-06-13 (curl_cffi chrome131: SEAT national total ~1733, CUPRA ~1063).

Response shape (field names inspected live, NOT assumed):
  {criteria:{...}, results:{result:{cars:[{key, href, car:{carid, items:[...], hypermediadealer}}]}},
   combinations:{...}}
The per-car page size is the `x-page-items` header; `x-page` is a 1-based PAGE index. The default
sort (PRICE_SALE/ASC) is NOT stable across a long crawl (page 2 re-shows ~half of page 1), so we
DEDUP on car.carid across the whole drain (the toyota USC model). The denominator is the sum of the
`t_body` criteria possibleItems counts (== total cars matching the empty filter), recorded for the
VAM slice arithmetic.

Each car.items[] is a flat key/value list (latin-1 over the wire on a few human fields):
  carid              -> stable per-car id + dedup key (e.g. ESP0A411034050-2026-781)
  localCarTitle      -> "Seat Ibiza Nuevo 1.0 MPI 59 KW (80 CV) Start/Stop +"
  manuf / model      -> brand / model
  body / gear / drive / doors / smod / color / padtype
  motor.values       -> fuel (Gasolina/Diesel/Híbrido/Eléctrico) + power.kw / power.ps
  prices.values      -> sale {raw_value EUR} (the offer price) + list {raw_value} (PVP)
  available_from     -> "Immediately" (every car: brand-new stock)
  dateproduction     -> ISO date the car was built
And car.hypermediadealer.dealer.items[] carries the SELLING official dealer per car:
  dealer_id_snw      -> stable dealer id (e.g. 0A411) — the per-dealer dedup key + source_ref
  name, city, region, street, street_type, zip (INE province = zip[:2]), phone, website,
  position.latitude / position.longitude (geocode fallback when zip missing).

This module mirrors pipeline.platform.oem_toyota_lexus_wholesale (the proven OEM dual-membership
template: per-brand offset/page drain, bulk cage, governor/health/VAM wiring) and stamps the
platform_listing edge with segment='new' the way coches_net_segments does. It proves the OEM
NEW-stock group flows through the ONE architecture, not a fork of it:

  seat_cupra_new (the OEM new-stock platform) -> entity, kind='plataforma' (+ platform_meta) [PLATFORM]
  each SELLING official dealer                -> entity, kind='concesionario_oficial' (geo-resolved)
  each NEW CAR                                -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the locator                      -> platform_listing edge, segment='new'

Multi-axis classification (migrations/0016 + 0019):
  defense_tier = 't0_open'           (vtpapi serves 200 to plain curl with only the x-pattern header)
  source_group = 'oem_dealer_network'(the BRAND's official new-stock network, NOT an oem_vo_portal)
  role         = 'platform'
  kind         = 'plataforma'        (the platform entity's ontology kind — a stock-locator surface)
  is_tier1     = FALSE               (no tier-1 WAF fronts the API)
  family       = 'vw_group_new'      (ties the VW-Group OEM NEW-stock siblings on the family axis)
  segment      = 'new'               (stamped on every platform_listing edge)

Run: python -m pipeline.platform.oem_seat_cupra_new_stock --pages 200
     python -m pipeline.platform.oem_seat_cupra_new_stock --brand seat
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
import re
import sys
import time
from dataclasses import dataclass

import asyncpg
from curl_cffi import requests as cffi_requests

from pipeline.engine.governor import governor, host_of
from pipeline.geo import GeoResolver
from pipeline.geocode import ProvinceGeocoder
from pipeline.ids import ulid
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict
from services.api.codes import _base32, cdp_code

DSN = "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
DSN = os.environ.get("CARDEEP_DSN", DSN)

# ---------------------------------------------------------------------------
# seat_cupra_new platform identity (OEM new-stock locator; migrations/0005 + 0016 + 0019).
# ---------------------------------------------------------------------------
SCN_DOMAIN = "seat.es"
SCN_WEBSITE = "seat.es"
SCN_LEGAL_NAME = "SEAT + CUPRA España (Localizador de Stock — coches nuevos)"
SCN_TRADE_NAME = "seat_cupra_new"
SCN_SOURCE_KEY = "oem_seat_cupra_new_stock"
SCN_WAF = "none"                  # vtpapi serves to plain curl; only the x-pattern header gates it.
SCN_DEFENSE_TIER = "t0_open"      # 200 to plain curl_cffi with the x-pattern header -> tier 0 open.
SCN_SOURCE_GROUP = "oem_dealer_network"   # the BRAND's official new-stock network (NOT oem_vo_portal).
SCN_ROLE = "platform"
SCN_KIND = "plataforma"          # the platform ENTITY's ontology kind (a stock-locator surface).
SCN_FAMILY = "vw_group_new"      # ties the VW-Group OEM NEW-stock siblings on the family axis.
SCN_SEGMENT = "new"              # every edge from this surface is brand-new stock.

# The VTP stock-locator REST service. ONE host, ONE path shape; the brand rides in the stockType
# path segment + the x-pattern header (verified live 2026-06-13 via the SPA XHR capture).
_BASE = "https://vtpapi.seat.com/restapi/v1"
_IMPERSONATE = "chrome131"
_TIMEOUT = 40
PAGE_SIZE = 12          # x-page-items. The host 500s above ~12; the SPA itself sends 12.
_MAX_RETRIES = 5        # the host emits transient 500 INTERNAL ERROR under burst; a short retry clears it.
_RETRY_SLEEP = 2.0


@dataclass(frozen=True)
class _BrandSurface:
    """One VTP brand surface (stockType path + x-pattern header). Together SEAT+CUPRA enumerate
    the whole VW-Group passenger-brand ES new-stock network reachable on this backend."""
    brand: str            # human label / CLI key.
    stock_type: str       # the {stockType} path segment.
    pattern: str          # the x-pattern header value (the access gate).
    origin: str           # Origin/Referer the SPA sends.
    pdp_base: str         # PDP base for the deep_link.
    manuf: str            # expected manuf value (anti-hallucination guard on the slice).


_SURFACES = (
    _BrandSurface("seat", "stesnwb", "seatwebfe", "https://www.seat.es",
                  "https://www.seat.es/localizador-stock", "Seat"),
    _BrandSurface("cupra", "cuesnwb", "cuprawebfe", "https://www.cupra.com",
                  "https://www.cupra.com/es-es/localizador-stock", "Cupra"),
)
_SURFACE_BY_KEY = {s.brand: s for s in _SURFACES}

PLATFORM_PROVINCE_SENTINEL = "00"   # national platform; '00' lives only inside the cdp_code string.
DEFAULT_MAX_PAGES = 250             # ~1733 SEAT / ~1063 CUPRA at 12/page -> ~145/~89 pages; 250 covers both.
DEFAULT_CONCURRENCY = 3             # the host is gentle (STEALTH class + 500-prone); a small window is plenty.


def scn_platform_cdp_code() -> str:
    """The seat_cupra_new platform's immutable cdp_code. Built from a NEW-stock identity key
    (NOT the bare 'domain:seat.es' — that namespace belongs to a future SEAT brand site entity);
    province segment '00' (national). Mirrors tl_platform_cdp_code() minting discipline."""
    key = f"new_stock:{SCN_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Field helpers (the VTP surface: nested key/value items + occasional latin-1 mojibake).
# ---------------------------------------------------------------------------


def _fix(s):
    """Repair latin-1 mojibake on human-text fields. The wire bytes are UTF-8 mis-decoded as
    latin-1 upstream on some accented values; re-encode to recover. Numeric ids stay clean."""
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


_SLUG_NONWORD = re.compile(r"[^a-z0-9]+")


def _slugify(s) -> str:
    if not isinstance(s, str):
        return ""
    s = _fix(s)
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return _SLUG_NONWORD.sub("-", s.lower()).strip("-")


def _items_map(items: list) -> dict:
    """Flatten car.items[] (a list of {key, value|values|...}) into {key: entry}."""
    out = {}
    if isinstance(items, list):
        for it in items:
            if isinstance(it, dict) and it.get("key"):
                out[it["key"]] = it
    return out


def _item_value(m: dict, key: str):
    """Read a scalar `value` from a flattened item entry."""
    entry = m.get(key)
    if isinstance(entry, dict):
        return entry.get("value")
    return None


def _motor_field(m: dict, sub_key: str):
    """Read a motor sub-value (fuel / power.kw / power.ps) from the nested motor item."""
    motor = m.get("motor")
    if isinstance(motor, dict):
        for v in motor.get("values", []):
            if isinstance(v, dict) and v.get("key") == sub_key:
                return v.get("value")
    return None


def _price_sale(m: dict):
    """The offer (sale) price raw_value in EUR. Falls back to formatted `value` parse."""
    prices = m.get("prices")
    if isinstance(prices, dict):
        for v in prices.get("values", []):
            if isinstance(v, dict) and v.get("key") == "sale":
                raw = v.get("raw_value")
                if raw is not None:
                    return _to_float(raw)
                txt = v.get("value")
                if isinstance(txt, str):
                    return _to_float(txt.replace(".", "").replace(",", "."))
    return None


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL response — field names inspected live 2026-06-13, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class DealerRef:
    dealer_id: str
    name: str | None
    province_code: str | None
    city: str | None
    zip: str | None
    lat: float | None
    lon: float | None


@dataclass
class Vehicle:
    deep_link: str
    listing_ref: str          # carid — stable id + dedup key.
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None            # brand-new stock: km is 0/None (no mileage field on the surface).
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None


def _first_image(car: dict) -> str | None:
    """Pick a hosted render image URL. VTP nests render images under images[].imageGroup.images[]."""
    imgs = car.get("images")
    if not isinstance(imgs, list):
        return None
    for grp in imgs:
        if not isinstance(grp, dict):
            continue
        ig = grp.get("imageGroup") or grp
        sub = ig.get("images") if isinstance(ig, dict) else None
        if isinstance(sub, list):
            for entry in sub:
                img = entry.get("image") if isinstance(entry, dict) else None
                href = img.get("href") if isinstance(img, dict) else None
                if isinstance(href, str) and href.startswith("http"):
                    return href
        # some surfaces put href directly on the group entry
        href = grp.get("href")
        if isinstance(href, str) and href.startswith("http"):
            return href
    return None


def parse_item_dealer(car: dict) -> DealerRef | None:
    """Parse the SELLING official dealer from car.hypermediadealer.dealer.items[]."""
    hd = car.get("hypermediadealer") or {}
    dealer = hd.get("dealer") or {}
    dm = _items_map(dealer.get("items"))
    dealer_id = _item_value(dm, "dealer_id_snw") or dealer.get("key")
    if not dealer_id:
        return None
    zip_raw = _item_value(dm, "zip")
    zip_s = str(zip_raw).strip() if zip_raw not in (None, "") else None
    lat = lon = None
    pos = dm.get("position")
    if isinstance(pos, dict):
        for v in pos.get("values", []):
            if isinstance(v, dict):
                if v.get("key") == "latitude":
                    lat = _to_float(v.get("value"))
                elif v.get("key") == "longitude":
                    lon = _to_float(v.get("value"))
    return DealerRef(
        dealer_id=str(dealer_id),
        name=_fix(_item_value(dm, "name")),
        province_code=None,                  # filled in _parse_window (zip first, then geo).
        city=_fix(_item_value(dm, "city")),
        zip=zip_s,
        lat=lat,
        lon=lon,
    )


def _build_deep_link(carid: str, surface: _BrandSurface) -> str:
    """Construct a stable PDP deep_link. The VTP payload carries an API `href` (datastore URL),
    not a public PDP url; the SPA builds the public PDP from the carid. We mint a canonical,
    always-attributable locator deep_link keyed on the carid (the load-bearing id)."""
    if not carid:
        return ""
    return f"{surface.pdp_base}?carid={carid}"


def parse_item_vehicle(car: dict, surface: _BrandSurface) -> Vehicle:
    """Parse the NEW car from a VTP search result item (REAL field map)."""
    m = _items_map(car.get("items"))
    carid = str(car.get("carid") or car.get("key") or "")

    make = _fix(_item_value(m, "manuf")) or surface.manuf
    model = _fix(_item_value(m, "model"))
    title = _fix(_item_value(m, "localCarTitle")) or " ".join(p for p in (make, model) if p) or None

    year = None
    dp = _item_value(m, "dateproduction")        # ISO 'YYYY-MM-DD...'
    if isinstance(dp, str) and len(dp) >= 4:
        year = _to_int(dp[:4])
    if year is None:
        do = _item_value(m, "dateoffer")
        if isinstance(do, str) and len(do) >= 4:
            year = _to_int(do[:4])
    if year is not None and not (1990 <= year <= 2100):
        year = None

    fuel = _fix(_motor_field(m, "fuel"))
    transmission = _fix(_item_value(m, "gear"))
    price = _price_sale(m)
    if price is not None and price <= 0:
        price = None

    return Vehicle(
        deep_link=_build_deep_link(carid, surface),
        listing_ref=carid,
        title=title,
        make=make,
        model=model,
        year=year,
        km=0,                                    # brand-new stock: zero kilometres.
        price=price,
        fuel=fuel,
        transmission=transmission,
        photo_url=_first_image(car),
    )


# ---------------------------------------------------------------------------
# Fetch: a GET routed THROUGH the governor (same per-host choke point the fleet uses), with a
# small in-fetch retry for the host's transient 500s.
# ---------------------------------------------------------------------------


class VTPFetcher:
    """A POOL of fingerprint-coherent curl_cffi GET sessions for the VTP search API.

    Same concurrency-vs-coherence contract as the toyota/coches fetchers: one Session per
    concurrency slot (a single curl_cffi Session is not thread-safe under the governor's
    to_thread fetch). The per-host token bucket bounds the AGGREGATE rate across the pool."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch_page(self, url: str, *, stock_type: str, pattern: str, origin: str,
                   page: int = 1, page_size: int = PAGE_SIZE, slot: int = 0) -> dict:
        """Synchronous GET on pool session `slot` (runs in a worker thread).

        Retries the host's transient 500 INTERNAL ERROR a few times before raising (so the
        breaker only ever sees a genuine, persistent failure — never a one-off blip)."""
        session = self._sessions[slot]
        full = f"{url}/{stock_type}/search/car"
        headers = {
            "Accept": "application/json",
            "x-pattern": pattern,
            "x-page": str(page),
            "x-page-items": str(page_size),
            "x-sort": "PRICE_SALE",
            "x-sort-direction": "ASC",
            "accept-language": "es-ES",
            "Referer": origin + "/",
            "x-car-image-width": "2048",
            "x-car-image-height": "1080",
        }
        last_status = None
        for attempt in range(_MAX_RETRIES):
            resp = session.get(full, headers=headers, impersonate=_IMPERSONATE, timeout=_TIMEOUT)
            last_status = resp.status_code
            self.last_status = last_status
            if resp.status_code == 200:
                return json.loads(resp.content.decode("utf-8", "replace"))
            # 500 is the known transient; back off and retry. 401/403/429 are real -> raise now.
            if resp.status_code in (401, 403, 429):
                raise RuntimeError(f"HTTP {resp.status_code} on {full} (pattern {pattern} page {page})")
            time.sleep(_RETRY_SLEEP)
        raise RuntimeError(f"HTTP {last_status} on {full} after {_MAX_RETRIES} retries "
                           f"(pattern {pattern} page {page})")

    async def fetch_page_async(self, governed_fetch, url: str, *, stock_type: str, pattern: str,
                               origin: str, page: int, page_size: int) -> dict:
        slot = await self._free.get()
        try:
            return await governed_fetch(url, stock_type=stock_type, pattern=pattern, origin=origin,
                                        page=page, page_size=page_size, slot=slot)
        finally:
            self._free.put_nowait(slot)


def _extract_total(data: dict) -> int | None:
    """The denominator: sum of the t_body criteria possibleItems counts (== total cars matching
    the empty filter). Read from each page's `criteria` block (present on every response)."""
    try:
        crits = data["criteria"]["search"]["criterias"]
    except (KeyError, TypeError):
        return None
    for c in crits:
        if isinstance(c, dict) and (c.get("criteria") or {}).get("key") == "t_body":
            items = c.get("possibleItems") or []
            return sum(_to_int(i.get("number")) or 0 for i in items)
    return None


def _extract_cars(data: dict) -> list:
    """The car list lives at results.result.cars[]."""
    try:
        cars = data["results"]["result"]["cars"]
    except (KeyError, TypeError):
        return []
    return cars if isinstance(cars, list) else []


# ---------------------------------------------------------------------------
# DB layer (mirrors oem_toyota_lexus_wholesale; dealers are concesionario_oficial /
# oem_dealer_network, edges stamped segment='new'). Multi-axis 0016 + 0019.
# ---------------------------------------------------------------------------

SCN_PLATFORM_RECIPE = {
    "version": 1,
    "source": "seat_cupra_new (seat.es/localizador-stock + cupra.com/es-es/localizador-stock)",
    "scope": "platform-wholesale (SEAT + CUPRA ES OFFICIAL NEW-CAR stock locator; VW-Group VTP REST API)",
    "engine": "curl_cffi+chrome131_impersonate+vtp_internal_json_api(GET)",
    "access": ("OPEN (t0_open). VTP serves 200 application/json to PLAIN curl_cffi when the "
               "x-pattern header is present (seatwebfe/cuprawebfe); without it -> 401 "
               "VtpApiUnauthorized. No proxy, no browser, no cookie warm-up, no auth token, €0. "
               "Transient 500 INTERNAL ERROR under burst -> short retry clears it. is_tier1=FALSE."),
    "data_surface": "internal_api",
    "surface_intent": "vtp_stock_locator_json_api",
    "endpoint": "GET https://vtpapi.seat.com/restapi/v1/{stockType}/search/car",
    "request": {
        "stock_type": {"seat": "stesnwb", "cupra": "cuesnwb"},
        "headers": ("x-pattern: seatwebfe|cuprawebfe (ACCESS GATE), x-page (1-based PAGE), "
                    "x-page-items (page size, <=12), x-sort PRICE_SALE, x-sort-direction ASC"),
        "note": "no region matrix param -> the full national set; PER-CAR dealer zip yields province.",
    },
    "enumeration": ("PER BRAND: x-page=1..N step 1 (PAGE_SIZE=12). The default sort is NOT stable "
                    "across pages -> DEDUP on car.carid across the whole drain. Stop on empty "
                    "cars[] or page*size >= declared total."),
    "denominator": "Σ criteria.search.criterias[t_body].possibleItems[].number (cars matching empty filter)",
    "platform_entity": ("kind=plataforma, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=FALSE, defense_tier=t0_open, source_group=oem_dealer_network, "
                        "role=platform, family=vw_group_new"),
    "dual_membership": ("vehicle.entity_ulid=SELLING official dealer (concesionario_oficial); "
                        "platform_listing edge=platform<->vehicle, segment='new'"),
    "field_map": {
        "deep_link": "constructed {pdp_base}?carid={carid} (payload href is the datastore URL)",
        "listing_ref": "car.carid (stable id + dedup key, e.g. ESP0A411034050-2026-781)",
        "title": "items.localCarTitle (fallback manuf+model)",
        "make": "items.manuf", "model": "items.model",
        "year": "items.dateproduction[:4] (fallback dateoffer[:4])",
        "km": "0 (brand-new stock — no mileage field on the surface)",
        "price": "items.prices.values[sale].raw_value (EUR; list = PVP)",
        "fuel": "items.motor.values[fuel]", "transmission": "items.gear",
        "photo": "car.images[].imageGroup.images[].image.href (render)",
        "dealer": ("car.hypermediadealer.dealer.items {dealer_id_snw, name, city, region, street, "
                   "zip, phone, website, position.latitude/longitude}"),
        "location": ("dealer.zip[:2] = INE province (authoritative); position lat/lon -> "
                     "ProvinceGeocoder fallback; dealer.city -> municipality (INE-resolved)"),
    },
    "segment": "new (every car: available_from=Immediately, dateproduction set, no mileage)",
    "caveats": {
        "x_pattern_gate": "the x-pattern header is the only access gate; it is brand-specific.",
        "page_size": "x-page-items <= 12; the host 500s on larger page sizes.",
        "unstable_sort": "PRICE_SALE/ASC repeats items across pages -> carid dedup is mandatory.",
        "transient_500": "the host emits transient 500 under burst; retry with backoff.",
        "encoding": "a few human-text fields are latin-1 mojibake; repair with encode/decode.",
        "all_official_dealers": "OEM new-stock locator — every car belongs to an official dealer.",
    },
    "verified_live": "2026-06-13 (SEAT ~1733, CUPRA ~1063 national; plain curl_cffi chrome131).",
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the seat_cupra_new platform entity + platform_meta. kind='plataforma',
    is_tier1=FALSE, multi-axis 0016 set, data_surface='internal_api'."""
    code = scn_platform_cdp_code()
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
        eulid, code, SCN_KIND, SCN_LEGAL_NAME, SCN_TRADE_NAME, SCN_WEBSITE,
        SCN_WAF, SCN_DEFENSE_TIER, SCN_SOURCE_GROUP, SCN_ROLE, SCN_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, SCN_SOURCE_KEY, SCN_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'internal_api',$2::jsonb,FALSE,TRUE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"endpoint": _BASE + "/{stockType}/search/car",
                           "host": host_of(_BASE), "method": "GET", "page_size": PAGE_SIZE,
                           "denominator": "sum(t_body criteria counts)",
                           "brands": {s.brand: s.stock_type for s in _SURFACES},
                           "patterns": {s.brand: s.pattern for s in _SURFACES},
                           "segment": SCN_SEGMENT,
                           "surface_intent": "vtp_stock_locator_json_api",
                           "engine": "curl_cffi/chrome131_impersonate"}),
        SCN_FAMILY)
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the official dealer's immutable cdp_code. Identity = name + location + the stable
    dealer_id_snw (via `address`) so two distinct dealers sharing a name in one municipality
    never collapse to one entity."""
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni, address=f"dealer:{d.dealer_id}")


# Bulk statements — ONE round-trip per table per window (unnest multi-row upsert), same idempotency
# as the row-by-row path. Dealers carry the 0016 axes (concesionario_oficial / oem_dealer_network /
# standalone_pos). The edge is stamped segment='new' (0019).

_BULK_UPSERT_DEALERS = """
INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
        province_code, municipality_code, is_tier1, status, kind_source,
        sells_cars, source_group, role, first_discovered_source, last_seen)
SELECT u.entity_ulid, u.cdp_code, 'concesionario_oficial', u.name, u.name,
       u.province_code, u.municipality_code, FALSE, 'active', 'platform_label',
       TRUE, 'oem_dealer_network'::source_group, 'standalone_pos'::entity_role, $7, now()
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

_BULK_UPSERT_SEGMENT_EDGES = """
INSERT INTO platform_listing (vehicle_ulid, platform_entity_ulid, listing_url,
        listing_ref, platform_price, segment, status, first_seen, last_seen)
SELECT u.vehicle_ulid, $5, u.listing_url, u.listing_ref, u.platform_price,
       $6, 'listed', now(), now()
  FROM unnest($1::text[], $2::text[], $3::text[], $4::numeric[])
       AS u(vehicle_ulid, listing_url, listing_ref, platform_price)
ON CONFLICT (vehicle_ulid, platform_entity_ulid)
  DO UPDATE SET last_seen = now(), status = 'listed',
                platform_price = EXCLUDED.platform_price,
                listing_ref = EXCLUDED.listing_ref,
                segment = EXCLUDED.segment
RETURNING (xmax = 0) AS inserted
"""

_BULK_INSERT_EVENTS = """
INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type,
        old_value, new_value)
SELECT u.event_ulid, u.vehicle_ulid, u.entity_ulid, 'NEW', NULL, u.new_value::jsonb
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[])
       AS u(event_ulid, vehicle_ulid, entity_ulid, new_value)
"""


def _resolve_province(d: DealerRef, geocoder: ProvinceGeocoder) -> str | None:
    """Resolve the dealer's INE province. PRIMARY: zip[:2] (authoritative). FALLBACK: geocode
    from lat/lon. Returns a validated '01'..'52' code or None."""
    if d.zip:
        digits = re.sub(r"\D", "", d.zip)
        if len(digits) >= 2:
            prov = digits[:2]
            if "01" <= prov <= "52":
                return prov
    if d.lat is not None and d.lon is not None:
        prov = geocoder.nearest_province(d.lat, d.lon)
        if prov and prov.isdigit() and "01" <= prov <= "52":
            return prov
    return None


@dataclass
class _CageRow:
    dealer_id: str
    dealer_cdp: str
    dealer_name: str | None
    dealer_province: str
    dealer_muni: str | None
    vehicle: Vehicle


def _parse_window(items_by_page: list[tuple[int, str, list]], geo: GeoResolver,
                  geocoder: ProvinceGeocoder, seen_ids: set, harvested_cageable: set,
                  stats: dict) -> list[_CageRow]:
    """Parse + geo-resolve every car across the window IN ORDER — pure CPU, no SQL. Cross-page
    dedup on car.carid (the sort is unstable). Each tuple is (page, brand, cars)."""
    rows: list[_CageRow] = []
    for _page, brand, cars in items_by_page:
        surface = _SURFACE_BY_KEY.get(brand, _SURFACES[0])
        for cw in cars:
            if not isinstance(cw, dict):
                continue
            car = cw.get("car") if isinstance(cw.get("car"), dict) else cw
            if not isinstance(car, dict):
                continue
            stats["items_seen"] += 1
            carid = str(car.get("carid") or car.get("key") or "")
            if carid and carid in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue
            if carid:
                seen_ids.add(carid)

            d = parse_item_dealer(car)
            if d is None:
                stats["no_dealer_skipped"] += 1
                continue
            stats["dealer_items"] += 1

            prov = _resolve_province(d, geocoder)
            if not prov:
                stats["geo_skipped"] += 1
                continue
            d = DealerRef(dealer_id=d.dealer_id, name=d.name, province_code=prov,
                          city=d.city, zip=d.zip, lat=d.lat, lon=d.lon)
            muni = geo.municipality_code(prov, d.city)
            dealer_cdp = cdp_code_dealer(d, muni)

            v = parse_item_vehicle(car, surface)
            if not v.deep_link:
                continue
            harvested_cageable.add((d.dealer_id, v.deep_link))
            rows.append(_CageRow(
                dealer_id=d.dealer_id, dealer_cdp=dealer_cdp, dealer_name=d.name,
                dealer_province=prov, dealer_muni=muni, vehicle=v))
    return rows


async def _ingest_window(conn: asyncpg.Connection, geo: GeoResolver, geocoder: ProvinceGeocoder,
                         platform_ulid: str, items_by_page: list[tuple[int, str, list]],
                         seen_ids: set, harvested_cageable: set, stats: dict) -> None:
    """BULK-ingest a whole page-window in ONE transaction with set-based SQL (mirrors
    oem_toyota_lexus_wholesale._ingest_window; edge stamped segment='new')."""
    cage = _parse_window(items_by_page, geo, geocoder, seen_ids, harvested_cageable, stats)
    if not cage:
        return

    async with conn.transaction():
        dealers: dict[str, _CageRow] = {}
        for r in cage:
            dealers.setdefault(r.dealer_cdp, r)
        d_ulids = [ulid() for _ in dealers]
        d_cdps = list(dealers.keys())
        d_names = [dealers[c].dealer_name for c in d_cdps]
        d_provs = [dealers[c].dealer_province for c in d_cdps]
        d_munis = [dealers[c].dealer_muni for c in d_cdps]
        d_refs = [dealers[c].dealer_id for c in d_cdps]
        await conn.execute(_BULK_UPSERT_DEALERS, d_ulids, d_cdps, d_names, d_provs,
                           d_munis, d_refs, SCN_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_DEALER_SOURCES, d_cdps, d_refs, SCN_SOURCE_KEY)
        cdp_to_ulid: dict[str, str] = {
            row["cdp_code"]: row["entity_ulid"]
            for row in await conn.fetch(
                "SELECT cdp_code, entity_ulid FROM entity WHERE cdp_code = ANY($1::text[])", d_cdps)
        }

        cars: dict[tuple[str, str], _CageRow] = {}
        for r in cage:
            du = cdp_to_ulid.get(r.dealer_cdp)
            if du is None:
                continue
            key = (du, r.vehicle.deep_link)
            if key not in cars:
                cars[key] = r

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

        e_vehicles = [vehicle_ulid_for[k] for k in car_keys]
        e_urls = [cars[k].vehicle.deep_link for k in car_keys]
        e_refs = [cars[k].vehicle.listing_ref for k in car_keys]
        e_prices = [cars[k].vehicle.price for k in car_keys]
        edge_rows = await conn.fetch(_BULK_UPSERT_SEGMENT_EDGES, e_vehicles, e_urls, e_refs,
                                     e_prices, platform_ulid, SCN_SEGMENT)
        stats["edges_created"] += sum(1 for row in edge_rows if row["inserted"])

        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                v = cars[k].vehicle
                payload = {"price": v.price, "title": v.title,
                           "platform": SCN_TRADE_NAME, "segment": SCN_SEGMENT}
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities, ev_payloads)
            stats["new_events"] += len(confirmed_new)


async def _drain_brand(conn, geo, geocoder, platform_ulid, fetcher, governed_fetch,
                       surface: _BrandSurface, max_pages: int, concurrency: int,
                       seen_ids: set, harvested_cageable: set, stats: dict) -> tuple[str | None, int | None]:
    """Drain ONE brand surface by walking x-page in concurrent windows. Returns (fetch_error,
    last_http). declared total (from the first page's t_body criteria) + emptiness bound the run."""
    fetch_error: str | None = None
    last_http: int | None = None
    declared_total: int | None = None
    stop = False
    next_page = 1
    print(f"[seat_cupra_new] === draining brand={surface.brand} ({surface.stock_type}) ===")
    while next_page <= max_pages and not stop:
        window = list(range(next_page, min(next_page + concurrency, max_pages + 1)))
        next_page = window[-1] + 1
        if declared_total is not None:
            window = [p for p in window if (p - 1) * PAGE_SIZE < declared_total]
            if not window:
                break

        results = await asyncio.gather(
            *(fetcher.fetch_page_async(governed_fetch, _BASE, stock_type=surface.stock_type,
                                       pattern=surface.pattern, origin=surface.origin,
                                       page=p, page_size=PAGE_SIZE) for p in window),
            return_exceptions=True,
        )

        window_pages: list[tuple[int, str, list]] = []
        for page, data in zip(window, results):
            if isinstance(data, Exception):
                fetch_error = str(data)
                last_http = fetcher.last_status
                print(f"[seat_cupra_new] brand={surface.brand} page {page} fetch failed ({data}); "
                      f"stopping this brand honestly.")
                stop = True
                break
            if declared_total is None:
                declared_total = _extract_total(data)
                stats["declared_per_brand"][surface.brand] = declared_total
                if stats["declared_full"] is None:
                    stats["declared_full"] = 0
                stats["declared_full"] += declared_total or 0
            cars = _extract_cars(data)
            if not cars:
                print(f"[seat_cupra_new] brand={surface.brand} page {page}: no cars; stopping "
                      f"(data boundary reached).")
                stop = True
                break
            window_pages.append((page, surface.brand, cars))

        if window_pages:
            await _ingest_window(conn, geo, geocoder, platform_ulid, window_pages, seen_ids,
                                 harvested_cageable, stats)
            stats["pages_fetched"] += len(window_pages)
            first_p, last_p = window_pages[0][0], window_pages[-1][0]
            print(f"[seat_cupra_new] brand={surface.brand} pages {first_p}-{last_p}: "
                  f"hits={sum(len(c) for _, _, c in window_pages)} "
                  f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                  f"edges={stats['edges_created']} dealers_seen={len(harvested_cageable)}")
    return fetch_error, last_http


async def harvest(brands: list[str] | None = None, max_pages: int = DEFAULT_MAX_PAGES,
                  concurrency: int = DEFAULT_CONCURRENCY, limit: int | None = None) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    if limit is not None and limit > 0:
        limit_pages = max(1, math.ceil(limit / PAGE_SIZE))
        max_pages = min(max_pages, limit_pages)
    surfaces = [_SURFACE_BY_KEY[b] for b in brands] if brands else list(_SURFACES)
    fetcher = VTPFetcher(pool_size=concurrency)
    stats = {
        "pages_fetched": 0, "items_seen": 0, "dealer_items": 0, "no_dealer_skipped": 0,
        "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0, "new_cars": 0, "edges_created": 0,
        "new_events": 0, "declared_full": None, "declared_per_brand": {}, "dup_ids_collapsed": 0,
        "dealers_distinct": 0, "concurrency": concurrency, "max_pages": max_pages,
    }
    harvested_cageable: set[tuple[str, str]] = set()

    if await is_open(conn, SCN_SOURCE_KEY):
        print(f"[seat_cupra_new] breaker OPEN for {SCN_SOURCE_KEY}; skipping drain (graceful).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": SCN_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        geocoder = await ProvinceGeocoder.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = scn_platform_cdp_code()
        print(f"[seat_cupra_new] platform entity ready: {platform_code} (ulid={platform_ulid}) "
              f"kind={SCN_KIND} group={SCN_SOURCE_GROUP} tier={SCN_DEFENSE_TIER} family={SCN_FAMILY}")
        print(f"[seat_cupra_new] geocoder anchors: {geocoder.size()} labeled points.")
        print(f"[seat_cupra_new] governor paces host {host_of(_BASE)} (per-host bucket, STEALTH class).")
        print(f"[seat_cupra_new] CONCURRENT drain: window={concurrency}, {max_pages} pages/brand x "
              f"{len(surfaces)} brands ({[s.brand for s in surfaces]}), segment='{SCN_SEGMENT}'.")

        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='concesionario_oficial'")}

        for surface in surfaces:
            err, http = await _drain_brand(
                conn, geo, geocoder, platform_ulid, fetcher, governed_fetch, surface,
                max_pages, concurrency, seen_ids, harvested_cageable, stats)
            if err is not None:
                fetch_error = err
                last_http = http
                break

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='concesionario_oficial'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, SCN_PLATFORM_RECIPE)
        print(f"[seat_cupra_new] recipe written: {recipe_path}")

        db_edges = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1 AND segment=$2",
            platform_ulid, SCN_SEGMENT)
        db_join_vehicles = await conn.fetchval(
            """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               JOIN entity d ON d.entity_ulid = v.entity_ulid
               WHERE pl.platform_entity_ulid=$1 AND pl.segment=$2""", platform_ulid, SCN_SEGMENT)
        harvested_cageable_n = len(harvested_cageable)
        verdict = await record_count_verdict(
            conn, subject_type="platform_segment_slice", subject_key=f"{platform_code}:{SCN_SEGMENT}",
            claim="distinct cageable new cars (harvest) == segment edges (db) == join-reachable vehicles",
            paths={"db_edges": db_edges, "db_join_vehicles": db_join_vehicles,
                   "harvested_cageable": harvested_cageable_n},
            tolerance=0.02)
        stats["verdict"] = verdict
        stats["db_edges"] = db_edges
        stats["db_join_vehicles"] = db_join_vehicles
        stats["harvested_cageable"] = harvested_cageable_n
        stats["harvested_distinct_ids"] = len(seen_ids)
        stats["platform_code"] = platform_code
        stats["platform_ulid"] = platform_ulid
        stats["recipe_path"] = str(recipe_path)

        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(conn, SCN_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
                                   error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, SCN_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[seat_cupra_new] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("SEAT+CUPRA (OEM NEW-CAR STOCK LOCATOR) WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  group / kind          : oem_dealer_network / plataforma (tier t0_open, family vw_group_new)")
    print(f"  segment               : {SCN_SEGMENT}")
    print(f"  declared full (source): {stats.get('declared_full')} {stats.get('declared_per_brand')}")
    print(f"  concurrency (window)  : {stats.get('concurrency')} pages in flight")
    print(f"  target pages/brand    : {stats.get('max_pages')}")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  dealer items          : {stats['dealer_items']}")
    print(f"  no-dealer skipped     : {stats['no_dealer_skipped']}")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page carid dedup)")
    print(f"  geo skipped (bad geo) : {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total new for seat_cupra_new = {stats.get('db_edges')})")
    print(f"  NEW delta events      : {stats['new_events']}")
    print("  --- VAM count quorum (like-with-like, segment=new) ---")
    print(f"  harvested_cageable    : {stats.get('harvested_cageable')}")
    print(f"  db_edges              : {stats.get('db_edges')}")
    print(f"  db_join_vehicles      : {stats.get('db_join_vehicles')}")
    print(f"  VAM verdict           : {stats.get('verdict')}")
    print(f"  health status         : {stats.get('health_status')} / breaker {stats.get('breaker_state')}")
    print(f"  recipe                : {stats.get('recipe_path')}")
    print("=" * 64)


def _force_utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass


def main() -> None:
    _force_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="seat_cupra_new OEM new-car stock-locator wholesale harvester (VTP GET drain)")
    parser.add_argument("--brand", choices=[s.brand for s in _SURFACES], default=None,
                        help="harvest a single brand surface (default: both SEAT + CUPRA)")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"pages PER BRAND (size={PAGE_SIZE}); default {DEFAULT_MAX_PAGES} (full ES stock)")
    parser.add_argument("--limit", type=int, default=None,
                        help=f"optional target car count PER BRAND; converted to a page count ({PAGE_SIZE}/page).")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=f"pages in flight per window; default {DEFAULT_CONCURRENCY} (gentle host).")
    args = parser.parse_args()
    brands = [args.brand] if args.brand else None
    stats = asyncio.run(harvest(brands, args.pages, args.concurrency, args.limit))
    _print_report(stats)


if __name__ == "__main__":
    main()
