"""seat_cupra (CUPRA Approved ES certified-used) WHOLESALE harvester — an OEM-VO portal, end to end.

www.cupra.com ('CUPRA Approved' / 'localizador-stock?t_cartype=used' — the brand's certified-used
"coches de ocasión certificados") is the manufacturer-owned certified-used portal for CUPRA in
Spain. Like spoticar (Stellantis), renew (Renault Group), toyota_lexus (Toyota Group) and Das
WeltAuto (VW Group) it is NOT a car-specialist marketplace (coches.net/autoscout24/motor.es) nor a
generalist classifieds (wallapop): it is an OEM-VO PORTAL — a single brand owner publishing the
certified-used inventory of its own official dealer network (concesionarios oficiales CUPRA). It
is the FIFTH member of the 'oem_vo_portal' source_group, in the new 'seat_cupra_vo' family.

WHY SEPARATE FROM Das WeltAuto (the brand front is 'seat_cupra', the two brands resolve apart):
  * SEAT half  -> SEAT's own "SEAT Ocasión" used portal (www.seat.es) REDIRECTS into Das WeltAuto
                  (www.dasweltauto.es/esp/seat). SEAT certified-used IS Das WeltAuto — ALREADY
                  COVERED by pipeline.platform.dasweltauto_wholesale. We do NOT re-harvest it.
  * CUPRA half -> CUPRA runs its OWN first-party certified-used surface ('CUPRA Approved') on
                  cupra.com, backed by a DISTINCT internal API (the SEAT/CUPRA 'VTP' service,
                  tenant 'cuesgwb' = CUPRA-ES-Gebrauchtwagen). Verified live: that surface serves
                  100% manuf=CUPRA cars (NO SEAT mixed in) — a genuinely distinct portal. THIS is
                  what this connector caches. Verified 2026-06-13 (docs recipe oem_seat_cupra_datalayer.md).

So the 'seat_cupra' brand front splits cleanly: SEAT already lives in Das WeltAuto; CUPRA gets its
own OEM-VO portal here. No double-coverage.

The surface is a Web-Components SPA (cuprawebfe pattern) backed by the VTP REST service. The SPA
calls an internal JSON API at GET https://vtpapi.seat.com/restapi/v1/cuesgwb/search/car —
pagination rides in REQUEST HEADERS (x-page, x-page-items, x-sort), NOT query params. No browser,
no proxy, no cookie warm-up, no auth: just a Chrome TLS fingerprint (curl_cffi). Plain urllib earns
a 403 Forbidden at the edge (a Traefik-fronted gate that fingerprints the client); the chrome131
JA3 passes cleanly with HTTP 200 application/json (defense_tier=t1_soft — an edge gate is present
but serves to curl_cffi, no JS challenge). The response carries
{criteria, results:{result:{cars:[...]}}, combinations} and the authoritative total in the
RESPONSE HEADER x-result-number (== the t_drive facet sum). 12 cars/page by default, but the API
HONOURS a larger x-page-items (96 verified) — FLAT (no relevance cap, no depth wall), walk
page=1..ceil(total/96) to enumerate the full ES public CUPRA stock. Each car carries its selling
official CUPRA dealer via the embedded hypermediadealer.dealer{} object (key, city, name, zip,
position lat/lng) — dealer attribution is per-car, NO PDP fetch needed. This is an OEM certified-
used portal: every car belongs to an official CUPRA dealer (concesionario oficial); there are NO
private sellers.

This module mirrors pipeline.platform.oem_toyota_lexus_wholesale EXACTLY (the proven OEM-VO
template: same dual-membership model, same bulk cage, same governor/health/VAM wiring, same
zip-first geo). It proves the OEM-VO group flows through the ONE architecture, not a fork of it:

  seat_cupra (the OEM-VO portal) -> entity, kind='oem_vo_portal' (+ platform_meta)  [THE PLATFORM]
  each SELLING DEALER            -> entity, kind='compraventa'   (geo-resolved)
  each CAR                       -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the portal          -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the selling dealer); platform membership is plural (this edge). The same
physical car can carry BOTH a seat_cupra edge and a coches.net edge without ever changing its
owning dealer.

GEO anchor (the renew/toyota_lexus model): the embedded dealer carries BOTH a zip and a
position{lat,lng}. We prefer zip->province (first 2 digits = INE province, authoritative); the
lat/lng is the geocode fallback via the ProvinceGeocoder (nearest labeled point) when the zip is
missing/malformed.

Encoding: UNLIKE spoticar/toyota_lexus, this surface serves CLEAN UTF-8 over the wire — the
accented bytes are genuine UTF-8 (e.g. 'automático' = c3 a1, 'Tracción', 'A Coruña' all decode
correctly via resp.content.decode("utf-8")). There is NO mojibake here. _fix() is kept only as a
DEFENSIVE no-op guard (a latin-1 round-trip that returns the input unchanged on already-correct
UTF-8) so the field pipeline matches its OEM-VO siblings; it neither repairs nor corrupts this
surface's already-correct text.

Multi-axis classification (migrations/0016):
  defense_tier = 't1_soft'         (edge gate present, 403 to plain urllib; serves 200 to chrome131; no JS challenge)
  source_group = 'oem_vo_portal'   (the group renew opened; seat_cupra is its fifth member)
  role         = 'platform'
  kind         = 'oem_vo_portal'   (the platform entity's ontology kind, migrations/0005)
  is_tier1     = TRUE              (the public API sits behind an edge gate)
  family       = 'seat_cupra_vo'   (ties the SEAT/CUPRA-group OEM-VO surfaces on the family axis)

PROOF SLICE OR FULL. The CUPRA Approved network declares ~1,323 cars (x-result-number). The set is
small and FLAT, so the FULL drain is in reach in a single run. --pages/--limit bound the run;
--limit converts a target car count to a page count. The declared full count is recorded for the
VAM verdict's slice arithmetic.

Engine: a GET against vtpapi.seat.com/restapi/v1/cuesgwb/search/car routed THROUGH the per-host
governor (the same single choke point coches.net/spoticar/AS24 use). The synchronous curl_cffi GET
runs in a worker thread so the event loop is never blocked, and no host is fetched faster than its
bucket.

Run: python -m pipeline.platform.oem_seat_cupra_wholesale --pages 14
"""
from __future__ import annotations

import argparse
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
from pipeline.geocode import ProvinceGeocoder
from pipeline.ids import ulid
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict
from services.api.codes import _base32, cdp_code

DSN = "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
DSN = os.environ.get("CARDEEP_DSN", DSN)

# ---------------------------------------------------------------------------
# seat_cupra platform identity (OEM-VO portal, migrations/0005 + 0016).
# ---------------------------------------------------------------------------
SC_DOMAIN = "cupra.com"
SC_WEBSITE = "cupra.com"
SC_LEGAL_NAME = "SEAT/CUPRA España (CUPRA Approved)"
SC_TRADE_NAME = "seat_cupra"
SC_SOURCE_KEY = "oem_seat_cupra_wholesale"
SC_WAF = "other"              # Traefik-fronted edge gate; 403s plain urllib, serves to chrome131.
SC_DEFENSE_TIER = "t1_soft"   # edge gate present but serving to curl_cffi (no JS challenge) -> tier 1 soft.
SC_SOURCE_GROUP = "oem_vo_portal"
SC_ROLE = "platform"
SC_KIND = "oem_vo_portal"     # the platform ENTITY's ontology kind (NOT 'plataforma').
SC_FAMILY = "seat_cupra_vo"   # ties the SEAT/CUPRA-group OEM-VO surfaces on the family axis.

# The working request (verified live 2026-06-13; recipe oem_seat_cupra_datalayer.md TL;DR).
_BASE = "https://vtpapi.seat.com"
LIST_PATH = "/restapi/v1/cuesgwb/search/car"   # the internal VTP CUPRA-ES used-car search API.
ENDPOINT = _BASE + LIST_PATH
# The PDP lives on the brand site; the API carries no PDP url, so we mint a canonical, always-
# resolvable deep-link from the brand stock-detail route keyed on the stable carid.
_PDP_BASE = "https://www.cupra.com/es-es/localizador-stock/coche"
_IMPERSONATE = "chrome131"
_TIMEOUT = 40
PAGE_SIZE = 96  # default SPA sends 12; the API HONOURS x-page-items>=96 (verified) -> fewer round-trips.

# Static request headers. Pagination rides in headers per-request (x-page/x-page-items added in the
# fetcher). x-pattern=cuprawebfe identifies the CUPRA web front-end tenant; without it the gate may
# refuse. x-sort=DATE_OFFER DESC is the SPA default and is STABLE for a full crawl.
_HEADERS = {
    "Accept": "application/json",
    "Accept-Language": "es-ES",
    "Referer": "https://www.cupra.com/",
    "Origin": "https://www.cupra.com",
    "x-pattern": "cuprawebfe",
    "x-sort": "DATE_OFFER",
    "x-sort-direction": "DESC",
    "x-car-image-width": "1",     # request the smallest image variant; we only keep one URL.
    "x-car-image-height": "1",
}

# Fuel vocabulary repair. The clean signal is the techdata fuel KEY (PETROL / PURE_DIESEL /
# PURE_ELECTRICAL / SUSTAINING_PETROL [PHEV] / DEPLETING_PETROL [MHEV] / ...). Map that finite,
# verified vocabulary to its proper Spanish label rather than scraping the (mojibake-prone) human
# label. No invention — a fixed lookup over the source's own enum.
_FUEL_KEY_LABEL = {
    "PETROL": "Gasolina",
    "PURE_PETROL": "Gasolina",
    "DEPLETING_PETROL": "Híbrido",            # MHEV / non-plug hybrid petrol
    "SUSTAINING_PETROL": "Híbrido enchufable",  # PHEV
    "DIESEL": "Diésel",
    "PURE_DIESEL": "Diésel",
    "PURE_ELECTRICAL": "Eléctrico",
    "ELECTRICAL": "Eléctrico",
    "CNG": "GNC",
    "LPG": "GLP",
}

# Province sentinel '00' = national (same convention as toyota_lexus/spoticar/renew/coches.net).
# geo_province has NO '00', so the platform ENTITY stores province_code = NULL; '00' lives only
# inside the cdp_code string (free text, no FK). We never pollute geo_province with it.
PLATFORM_PROVINCE_SENTINEL = "00"

# Full-drain default. ~1,323 cars / 96 per page = ~14 data pages. x-result-number + first-empty-page
# bound the run. A small slice (--pages 2) is a proof slice; --pages 14 is the full ES CUPRA stock.
DEFAULT_MAX_PAGES = 14


def sc_platform_cdp_code() -> str:
    """The seat_cupra platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:cupra.com'), province segment '00' (national). Mirrors
    tl_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{SC_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Field helpers (the VTP surface: items[] key/value lists + latin-1 mojibake on human text).
# ---------------------------------------------------------------------------


def _fix(s):
    """Defensive no-op encoding guard. THIS surface serves CLEAN UTF-8 (verified live: 'automático'
    arrives as c3 a1 and decodes correctly), so unlike the spoticar/toyota_lexus siblings there is
    no mojibake to repair. The latin-1 round-trip below is a pure safety net: on already-correct
    UTF-8 it raises UnicodeDecodeError and returns the input UNCHANGED, so it cannot corrupt this
    surface; it only ever activates if upstream encoding regresses to the sibling mojibake pattern.
    Kept for field-pipeline parity with the other OEM-VO connectors."""
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


def _km_int(v):
    """mileage arrives as a Spanish-formatted string ('38.621' = 38621). Strip the thousands dots
    (and any stray non-digits) and parse. Returns None on anything unparseable."""
    if v is None:
        return None
    digits = re.sub(r"[^0-9]", "", str(v))
    return _to_int(digits) if digits else None


def _items_map(items) -> dict:
    """Flatten an items[] list of {key, value, values?} into {key: item} for O(1) lookup."""
    out = {}
    if isinstance(items, list):
        for it in items:
            if isinstance(it, dict) and "key" in it:
                out[it["key"]] = it
    return out


def _item_value(imap: dict, key: str):
    """Scalar `value` of items[key]."""
    it = imap.get(key)
    return it.get("value") if isinstance(it, dict) else None


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL response — field names inspected live 2026-06-13, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class DealerRef:
    """The selling official CUPRA dealer parsed from a car's embedded hypermediadealer.dealer{}.

    The dealer carries: dealer.key (stable per-site id, e.g. 'ESP0A211'), and dealer.items[] with
    {city, name, phone, zip, street, position{latitude,longitude}}. The province comes from the zip
    (first 2 digits = INE province, authoritative); the lat/lng is the geocode fallback. key is the
    stable per-dealer key for cross-source dedup and as the source_ref."""
    dealer_id: str
    name: str | None
    province_code: str | None
    city: str | None
    zip: str | None
    lat: float | None
    lon: float | None


@dataclass
class Vehicle:
    """A car parsed from a single VTP search item."""
    deep_link: str
    listing_ref: str           # VTP stable carid (e.g. 'ESP0A211115431200') — also the dedup key.
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    vin: str | None            # not present on this surface (search payload carries no VIN) -> None.


def _first_image(car: dict) -> str | None:
    """Pick a hosted image URL. VTP nests images under images[].imageGroup.images[].image.href.
    Prefer the first absolute http(s) URL found."""
    imgs = car.get("images")
    if not isinstance(imgs, list):
        return None
    for grp in imgs:
        if not isinstance(grp, dict):
            continue
        inner = (grp.get("imageGroup") or {}).get("images")
        if not isinstance(inner, list):
            continue
        for entry in inner:
            img = (entry or {}).get("image") if isinstance(entry, dict) else None
            href = img.get("href") if isinstance(img, dict) else None
            if isinstance(href, str) and href.startswith("http"):
                return href
    return None


def _fuel_of(car: dict) -> str | None:
    """Resolve the fuel from hypermediatechdata: walk to the data[key='fuel'].techData.values[].key
    (PETROL / PURE_DIESEL / PURE_ELECTRICAL / SUSTAINING_PETROL / ...), map to the Spanish label via
    the fixed verified vocabulary. Returns None when the techdata is absent/unknown."""
    for td in car.get("hypermediatechdata", []) or []:
        if not isinstance(td, dict):
            continue
        for g in (td.get("techDataType") or {}).get("groups", []) or []:
            for d in (g.get("techDataGroup") or {}).get("data", []) or []:
                if isinstance(d, dict) and d.get("key") == "fuel":
                    vals = (d.get("techData") or {}).get("values", []) or []
                    if vals and isinstance(vals[0], dict):
                        key = vals[0].get("key")
                        if isinstance(key, str):
                            return _FUEL_KEY_LABEL.get(key.upper(), _fix(key.replace("_", " ").title()))
    return None


def parse_item_dealer(car: dict) -> DealerRef | None:
    """Parse the SELLING dealer from a car's hypermediadealer.dealer{}. Returns None when there is
    no stable dealer key — the car cannot be attributed to a concrete official dealer."""
    dealer = (car.get("hypermediadealer") or {}).get("dealer") or {}
    dealer_id = dealer.get("key")
    if not dealer_id:
        return None
    dimap = _items_map(dealer.get("items"))
    zip_raw = _item_value(dimap, "zip")
    zip_s = str(zip_raw).strip() if zip_raw not in (None, "") else None
    lat = lon = None
    pos = dimap.get("position")
    if isinstance(pos, dict) and isinstance(pos.get("values"), list):
        pmap = _items_map(pos["values"])
        lat = _to_float(_item_value(pmap, "latitude"))
        lon = _to_float(_item_value(pmap, "longitude"))
    return DealerRef(
        dealer_id=str(dealer_id),
        name=_fix(_item_value(dimap, "name")),
        province_code=None,                       # filled in _parse_window (zip first, then geo).
        city=_fix(_item_value(dimap, "city")),
        zip=zip_s,
        lat=lat,
        lon=lon,
    )


def _build_deep_link(carid: str) -> str:
    """Construct the PDP deep_link. The VTP payload carries NO PDP url; the SPA routes the detail
    view by carid under the brand stock locator. We mint the canonical, always-resolvable path
    keyed on the stable carid (the load-bearing key)."""
    return f"{_PDP_BASE}/{carid}" if carid else ""


def parse_item_vehicle(car: dict) -> Vehicle:
    """Parse the car from a VTP search item (REAL field map: items[] key/value + nested techdata)."""
    imap = _items_map(car.get("items"))

    # price: items[key='prices'].values[key='sale'].raw_value (clean float) — fall back to a parse of
    # the formatted 'value' ('31.990,00') only if raw_value is absent.
    price = None
    prices_it = imap.get("prices")
    if isinstance(prices_it, dict) and isinstance(prices_it.get("values"), list):
        for pv in prices_it["values"]:
            if isinstance(pv, dict) and pv.get("key") == "sale":
                price = _to_float(pv.get("raw_value"))
                if price is None and isinstance(pv.get("value"), str):
                    cleaned = pv["value"].replace(".", "").replace(",", ".")
                    price = _to_float(cleaned)
                break
    if price is not None and price <= 0:
        price = None

    year = _to_int(_item_value(imap, "modelyear"))
    if year is None:
        reg = _item_value(imap, "initialreg")   # 'YYYY-MM-DDT...'
        if isinstance(reg, str) and len(reg) >= 4 and reg[:4].isdigit():
            year = _to_int(reg[:4])
    if year is not None and not (1900 <= year <= 2100):
        year = None

    km = _km_int(_item_value(imap, "mileage"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    make = _fix(_item_value(imap, "manuf")) or "CUPRA"
    model = _fix(_item_value(imap, "model"))
    cartitle = _fix(_item_value(imap, "localCarTitle")) or _fix(_item_value(imap, "cartitle"))
    title = cartitle or " ".join(p for p in (make, model) if p) or None

    # carid is the stable per-car id AND the dedup key. It is clean.
    carid = str(car.get("carid") or "")
    listing_ref = carid

    # transmission from the gearbox item (gear: 'Cambio automático DSG' / 'Cambio manual'); fuel from
    # the techdata fuel key mapped to the Spanish label.
    transmission = _fix(_item_value(imap, "gear"))
    fuel = _fuel_of(car)

    return Vehicle(
        deep_link=_build_deep_link(carid),
        listing_ref=listing_ref,
        title=title,
        make=make,
        model=model,
        year=year,
        km=km,
        price=price,
        fuel=fuel,
        transmission=transmission,
        photo_url=_first_image(car),
        vin=None,   # the VTP search payload carries no VIN.
    )


# ---------------------------------------------------------------------------
# Fetch: a GET (header-paginated) routed THROUGH the governor (same per-host choke point as
# spoticar/toyota_lexus/coches.net).
# ---------------------------------------------------------------------------


class SeatCupraFetcher:
    """A POOL of fingerprint-coherent curl_cffi GET sessions for the VTP search API.

    Same concurrency-vs-coherence model as TLFetcher / SpoticarFetcher: a single curl_cffi Session
    is NOT safe to call from several threads at once, and the governor runs each fetch in its own
    worker thread (asyncio.to_thread). The fix is a bounded POOL — one Session per concurrency slot,
    each its own Chrome fingerprint + cookie jar. The governor's per-host bucket bounds the
    AGGREGATE rate across every session, so the pool widens parallelism WITHOUT out-pacing the host
    (the choke point is the bucket, never the session count).

    The fetcher also captures the authoritative total count from the x-result-number RESPONSE header
    of the first page it sees (the denominator; == the t_drive facet sum)."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None
        self.result_number: int | None = None   # x-result-number from any page (authoritative total).

    def fetch_page(self, url: str, *, page: int = 1, page_size: int = PAGE_SIZE,
                   slot: int = 0) -> dict:
        """The synchronous GET on pool session `slot` (runs in a worker thread).

        Handed to governor().wrap_fetch_text: the governor derives the host from `url`, waits on the
        per-host bucket, then runs THIS off the event loop. `slot`/`page`/`page_size` ride as kwargs
        the governor forwards untouched, so each in-flight request GETs on its own leased,
        never-shared curl_cffi session (thread-safe). Pagination rides in REQUEST HEADERS (x-page,
        x-page-items). Raises on a non-200 so the breaker sees throttling (never masks a
        challenge/empty body)."""
        session = self._sessions[slot]
        headers = dict(_HEADERS)
        headers["x-page"] = str(page)
        headers["x-page-items"] = str(page_size)
        resp = session.get(url, headers=headers, impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url} (page {page})")
        rn = resp.headers.get("x-result-number")
        if rn is not None and self.result_number is None:
            self.result_number = _to_int(rn)
        return json.loads(resp.content.decode("utf-8", "replace"))

    async def fetch_page_async(self, governed_fetch, url: str, *, page: int,
                               page_size: int) -> dict:
        """Lease a pool slot, fetch `page` THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, page=page, page_size=page_size, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer (mirrors oem_toyota_lexus_wholesale: ensure platform, bulk-upsert dealer/vehicle, link
# edge, emit delta, all idempotent ON CONFLICT). Multi-axis 0016 classification set.
# ---------------------------------------------------------------------------

SC_PLATFORM_RECIPE = {
    "version": 1,
    "source": "seat_cupra (CUPRA Approved — cupra.com)",
    "scope": "platform-wholesale (CUPRA ES certified-used 'CUPRA Approved'; Web-Components SPA + VTP JSON API)",
    "engine": "curl_cffi+chrome131_impersonate+vtp_internal_json_api(GET, header-paginated)",
    "access": ("OPEN-via-fingerprint (plain urllib earns 403 Forbidden at a Traefik-fronted edge "
               "gate; chrome131 TLS/JA3 passes cleanly with 200 application/json). No proxy, no "
               "browser, no cookie warm-up, no auth, €0. Public API behind an edge gate -> "
               "is_tier1=TRUE; the JSON serves to curl_cffi -> defense_tier=t1_soft."),
    "data_surface": "internal_api",
    "surface_intent": "vtp_internal_json_api",
    "endpoint": "GET https://vtpapi.seat.com/restapi/v1/cuesgwb/search/car (pagination in headers)",
    "request": {
        "headers": ("Accept application/json, Accept-Language es-ES, Referer/Origin cupra.com, "
                    "x-pattern cuprawebfe, x-sort DATE_OFFER, x-sort-direction DESC, "
                    "x-page=N, x-page-items=96 (page size; API honours >=96)"),
        "params": "NONE (everything rides in headers; no query string needed for the full used set)",
    },
    "enumeration": ("page=1..ceil(total/96) (x-page-items=96; last page = trailing remainder, "
                    "next page = empty/no 'cars' key). x-result-number (RESPONSE header) + "
                    "first-empty-page bound the run; dedup on carid."),
    "denominator": "x-result-number (response header) == Σ criteria.search.criterias[t_drive].possibleItems.number",
    "tenant": "cuesgwb = CUPRA-ES used; serves 100% manuf=CUPRA (SEAT is NOT here — SEAT lives in Das WeltAuto)",
    "platform_entity": ("kind=oem_vo_portal, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=TRUE, defense_tier=t1_soft, source_group=oem_vo_portal, role=platform, "
                        "family=seat_cupra_vo"),
    "dual_membership": ("vehicle.entity_ulid=SELLING DEALER (compraventa); "
                        "platform_listing edge=platform<->vehicle"),
    "field_map": {
        "deep_link": "constructed https://www.cupra.com/es-es/localizador-stock/coche/{carid} (no url in payload)",
        "listing_ref": "results.result.cars[].car.carid (stable id + dedup key)",
        "vin": "NOT PRESENT on the search surface -> NULL (would need a PDP fetch; not worth it)",
        "make": "car.items[key='manuf'].value (always 'CUPRA')",
        "model": "car.items[key='model'].value",
        "title": "car.items[key='localCarTitle'].value (fallback cartitle)",
        "year": "car.items[key='modelyear'].value (fallback initialreg[:4])",
        "km": "car.items[key='mileage'].value ('38.621' -> strip thousands dots -> 38621)",
        "price": "car.items[key='prices'].values[key='sale'].raw_value (EUR; clean float)",
        "fuel": "hypermediatechdata..data[key='fuel'].techData.values[0].key -> Spanish label (fixed map)",
        "transmission": "car.items[key='gear'].value ('Cambio automático DSG' / 'Cambio manual')",
        "photo": "car.images[].imageGroup.images[].image.href (first absolute http(s))",
        "dealer": "car.hypermediadealer.dealer {key, items{city,name,phone,zip,street,position{lat,lng}}}",
        "location": ("dealer zip[:2] = INE province (authoritative); dealer position lat/lng -> "
                     "ProvinceGeocoder fallback; dealer city -> municipality (INE-resolved, best-effort)"),
    },
    "caveats": {
        "page_size": "default 12; API HONOURS x-page-items=96 (verified) -> use 96 for fewer round-trips.",
        "pagination": "in REQUEST HEADERS (x-page / x-page-items), NOT query params.",
        "count_header": "the total is in the RESPONSE header x-result-number, not the JSON body.",
        "encoding": ("CLEAN UTF-8 — no mojibake on this surface (unlike spoticar/toyota_lexus). "
                     "_fix() is a defensive no-op guard only; the wire already decodes correctly."),
        "no_vin": "the search payload carries no VIN (vin_ref stays NULL).",
        "no_private_sellers": "OEM certified-used portal — every car belongs to an official CUPRA dealer.",
        "seat_split": ("the 'seat_cupra' brand front splits: SEAT certified-used redirects into Das "
                       "WeltAuto (already covered by dasweltauto_wholesale); CUPRA is THIS portal."),
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the seat_cupra platform entity + platform_meta exist. Returns the
    platform entity_ulid. kind='oem_vo_portal' (the platform ontology kind), is_tier1=TRUE (an edge
    gate fronts the API), multi-axis 0016 classification set explicitly, data_surface='internal_api'."""
    code = sc_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               defense_tier, source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,$3,$4,$5,NULL,$6,$7::waf_kind,TRUE,'active','platform_label',
               $8::defense_tier,$9::source_group,$10::entity_role,$11, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, website_waf = EXCLUDED.website_waf,
               defense_tier = EXCLUDED.defense_tier, source_group = EXCLUDED.source_group,
               role = EXCLUDED.role, legal_name = EXCLUDED.legal_name, kind = EXCLUDED.kind""",
        eulid, code, SC_KIND, SC_LEGAL_NAME, SC_TRADE_NAME, SC_WEBSITE,
        SC_WAF, SC_DEFENSE_TIER, SC_SOURCE_GROUP, SC_ROLE, SC_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, SC_SOURCE_KEY, SC_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'internal_api',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"endpoint": ENDPOINT, "host": host_of(ENDPOINT),
                           "method": "GET", "page_size": PAGE_SIZE,
                           "denominator": "x-result-number",
                           "tenant": "cuesgwb",
                           "brand": "CUPRA",
                           "surface_intent": "vtp_internal_json_api",
                           "engine": "curl_cffi/chrome131_impersonate"}),
        SC_FAMILY)
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    CUPRA dealers have no bare domain identity on this surface -> identity = name + location + the
    stable dealer key (passed via `address` so two distinct dealers that happen to share a name in
    one municipality never collapse to one entity)."""
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni, address=f"dealer:{d.dealer_id}")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# Default concurrency: pages fetched in parallel per sliding window. vtpapi.seat.com is NOT in the
# governor's JSON_API rate class — it inherits the conservative STEALTH default, the safe direction
# for a t1_soft edge-gated host whose true ceiling is unmeasured. The concurrency only needs to keep
# that (slow) bucket saturated; a small window is plenty.
DEFAULT_CONCURRENCY = 4


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


def _resolve_province(d: DealerRef, geocoder: ProvinceGeocoder) -> str | None:
    """Resolve the dealer's INE province. PRIMARY: the zip's first 2 digits (authoritative, the
    renew/toyota_lexus model). FALLBACK: geocode from lat/lon (nearest labeled point) when the zip
    is missing/malformed. Returns a validated '01'..'52' code or None."""
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


def _parse_window(items_by_page: list[tuple[int, list]], geo: GeoResolver,
                  geocoder: ProvinceGeocoder, seen_ids: set, harvested_cageable: set,
                  stats: dict) -> list[_CageRow]:
    """Parse + geo-resolve every car across the window IN PAGE ORDER — pure CPU, no SQL.

    The EXACT per-item gate (cross-page dedup on carid, dealer-parse skip, geo skip, cageable
    truth), lifted out of the DB loop so the SQL phase is purely set-based. The province is resolved
    zip-first then geocode-fallback. `seen_ids` / `harvested_cageable` / `stats` are mutated here
    with deterministic page-order semantics so the VAM truth is byte-identical regardless of
    batching. Each tuple is (page, cars-list); each cars-list item is a {key, href, car} wrapper."""
    rows: list[_CageRow] = []
    for _page, items in items_by_page:
        for wrapper in items:
            car = wrapper.get("car") if isinstance(wrapper, dict) else None
            if not isinstance(car, dict):
                continue
            stats["items_seen"] += 1
            # cross-page dedup on carid (the stable dedup key; default sort is not stable across a
            # long crawl, so the same car can reappear on a later page).
            item_id = str(car.get("carid") or "")
            if item_id and item_id in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue
            if item_id:
                seen_ids.add(item_id)

            d = parse_item_dealer(car)
            if d is None:
                stats["no_dealer_skipped"] += 1
                continue
            stats["dealer_items"] += 1

            # Geo gate — resolve the province (zip first, lat/lon fallback), then apply the same
            # province-range guard the dealer upsert enforces, done in memory so a bad/missing geo is
            # skipped without ever touching the DB (no FK risk).
            prov = _resolve_province(d, geocoder)
            if not prov:
                stats["geo_skipped"] += 1
                continue
            d = DealerRef(dealer_id=d.dealer_id, name=d.name, province_code=prov,
                          city=d.city, zip=d.zip, lat=d.lat, lon=d.lon)
            muni = geo.municipality_code(prov, d.city)
            dealer_cdp = cdp_code_dealer(d, muni)

            v = parse_item_vehicle(car)
            if not v.deep_link:
                continue
            harvested_cageable.add((d.dealer_id, v.deep_link))
            if v.vin:
                stats["vins_captured"] += 1
            rows.append(_CageRow(
                dealer_id=d.dealer_id, dealer_cdp=dealer_cdp, dealer_name=d.name,
                dealer_province=prov, dealer_muni=muni, vehicle=v))
    return rows


async def _ingest_window(conn: asyncpg.Connection, geo: GeoResolver, geocoder: ProvinceGeocoder,
                         platform_ulid: str, items_by_page: list[tuple[int, list]], seen_ids: set,
                         harvested_cageable: set, stats: dict) -> None:
    """BULK-ingest a whole concurrent page-window in ONE transaction with set-based SQL.

    Mirrors oem_toyota_lexus_wholesale._ingest_window EXACTLY: ONE round-trip per table per window
    (unnest multi-row upserts). The delta/VAM/platform_listing semantics are preserved: same ON
    CONFLICT idempotency, same cageable truth, same NEW-event rule (emitted only for genuinely new
    vehicles). A re-run of an already-harvested window adds 0 rows and 0 events.
    """
    cage = _parse_window(items_by_page, geo, geocoder, seen_ids, harvested_cageable, stats)
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
                           d_munis, d_refs, SC_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_DEALER_SOURCES, d_cdps, d_refs, SC_SOURCE_KEY)
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

        # ---- (5) NEW delta events — only for genuinely new vehicles.
        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                v = cars[k].vehicle
                payload = {"price": v.price, "title": v.title, "platform": SC_TRADE_NAME}
                if v.vin:
                    payload["vin"] = v.vin
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities,
                               ev_payloads)
            stats["new_events"] += len(confirmed_new)


async def harvest(max_pages: int = DEFAULT_MAX_PAGES,
                  concurrency: int = DEFAULT_CONCURRENCY,
                  limit: int | None = None) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    # --limit converts a target car count to a page count (PAGE_SIZE cars/page). The tighter of
    # --pages / --limit bounds the run.
    if limit is not None and limit > 0:
        limit_pages = max(1, math.ceil(limit / PAGE_SIZE))
        max_pages = min(max_pages, limit_pages)
    fetcher = SeatCupraFetcher(pool_size=concurrency)
    stats = {
        "pages_fetched": 0, "items_seen": 0, "dealer_items": 0,
        "no_dealer_skipped": 0, "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "vins_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "dealers_distinct": 0,
        "concurrency": concurrency, "max_pages": max_pages, "private_skipped": 0,
    }
    # Harvest-side truth for the VAM: distinct CAGEABLE cars = distinct (dealer_id, deep_link)
    # pairs that survived dealer-parse + geo-resolution. Like-with-like vs db_edges.
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if the breaker is OPEN (a recent ban/throttle still cooling), skip the drain
    # gracefully — the API keeps serving the last snapshot.
    if await is_open(conn, SC_SOURCE_KEY):
        print(f"[oem_seat_cupra] breaker OPEN for {SC_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, API still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": SC_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        geocoder = await ProvinceGeocoder.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = sc_platform_cdp_code()
        print(f"[oem_seat_cupra] platform entity ready: {platform_code} (ulid={platform_ulid}) "
              f"kind={SC_KIND} group={SC_SOURCE_GROUP} tier={SC_DEFENSE_TIER} family={SC_FAMILY}")
        print(f"[oem_seat_cupra] geocoder anchors: {geocoder.size()} labeled points (lat/lon -> province).")
        print(f"[oem_seat_cupra] governor paces host {host_of(ENDPOINT)} (per-host token bucket, STEALTH class).")
        print(f"[oem_seat_cupra] CONCURRENT drain: window={concurrency} pages in flight. "
              f"Target = {max_pages} pages (~{max_pages * PAGE_SIZE} cars cap; full ES CUPRA stock ~1323).")

        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        # CONCURRENT sliding-window drain. Each window fetches up to `concurrency` pages in parallel
        # through the governor (the host bucket paces the aggregate), then the pages are INGESTED
        # sequentially in page order through the single asyncpg connection. A page that errors or
        # comes back empty (no 'cars') stops the drain honestly. x-result-number bounds the run.
        stop = False
        next_page = 1
        declared = None
        while next_page <= max_pages and not stop:
            window = list(range(next_page, min(next_page + concurrency, max_pages + 1)))
            next_page = window[-1] + 1
            # bound by declared total once known (page p is past the end if (p-1)*size >= total)
            if declared is not None:
                window = [p for p in window if (p - 1) * PAGE_SIZE < declared]
                if not window:
                    break

            results = await asyncio.gather(
                *(fetcher.fetch_page_async(governed_fetch, ENDPOINT, page=p, page_size=PAGE_SIZE)
                  for p in window),
                return_exceptions=True,
            )

            window_pages: list[tuple[int, list]] = []
            for page, data in zip(window, results):
                if isinstance(data, Exception):
                    fetch_error = str(data)
                    last_http = fetcher.last_status
                    print(f"[oem_seat_cupra] page {page} fetch failed ({data}); stopping drain honestly.")
                    stop = True
                    break
                # authoritative total from the x-result-number response header (captured by fetcher).
                if declared is None and fetcher.result_number is not None:
                    declared = fetcher.result_number
                    stats["declared_full"] = declared
                cars = (((data.get("results") or {}).get("result") or {}).get("cars")) or []
                if not cars:
                    print(f"[oem_seat_cupra] page {page}: no cars; stopping (data boundary reached).")
                    stop = True
                    break
                window_pages.append((page, cars))

            if window_pages:
                await _ingest_window(conn, geo, geocoder, platform_ulid, window_pages, seen_ids,
                                     harvested_cageable, stats)
                stats["pages_fetched"] += len(window_pages)
                first_p, last_p = window_pages[0][0], window_pages[-1][0]
                print(f"[oem_seat_cupra] window pages {first_p}-{last_p}: "
                      f"hits={sum(len(it) for _, it in window_pages)} "
                      f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                      f"edges={stats['edges_created']} dealers_seen={len(harvested_cageable)}")

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, SC_PLATFORM_RECIPE)
        print(f"[oem_seat_cupra] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths that all measure
        # "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for seat_cupra   (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join      (DB read truth)
        #   harvested_cageable = distinct (dealer_id, deep_link) pulled    (harvest truth)
        # The declared full count (x-result-number) is reported for honesty but is NOT a quorum path
        # (it measures the WHOLE portal, not necessarily this slice unless the full drain ran).
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

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks seat_cupra, trips the
        # breaker on a ban, and auto-repairs. OK when >=1 page fetched, no fetch error stopped the
        # drain, and the VAM did not refute.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, SC_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, SC_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[oem_seat_cupra] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("SEAT_CUPRA (OEM-VO PORTAL — CUPRA Approved) WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  group / kind          : oem_vo_portal / oem_vo_portal (tier t1_soft, family seat_cupra_vo)")
    print(f"  declared full (source): {stats.get('declared_full')} (x-result-number)")
    print(f"  concurrency (window)  : {stats.get('concurrency')} pages in flight")
    print(f"  target pages          : {stats.get('max_pages')}")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  dealer items          : {stats['dealer_items']}")
    print(f"  no-dealer skipped     : {stats['no_dealer_skipped']}")
    print(f"  private skipped       : {stats['private_skipped']} (OEM portal — none expected)")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page, carid dedup)")
    print(f"  geo skipped (bad geo) : {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for seat_cupra = {stats.get('db_edges')})")
    print(f"  VINs captured         : {stats['vins_captured']} (search surface carries no VIN)")
    print(f"  NEW delta events      : {stats['new_events']}")
    print("  --- VAM count quorum (like-with-like, this slice) ---")
    print(f"  harvested_cageable    : {stats.get('harvested_cageable')}")
    print(f"  db_edges              : {stats.get('db_edges')}")
    print(f"  db_join_vehicles      : {stats.get('db_join_vehicles')}")
    print(f"  VAM verdict           : {stats.get('verdict')}")
    print(f"  health status         : {stats.get('health_status')} / breaker {stats.get('breaker_state')}")
    print(f"  recipe                : {stats.get('recipe_path')}")
    print("=" * 64)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="seat_cupra OEM-VO portal wholesale harvester (concurrent CUPRA-Approved VTP-JSON drain)")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"pages to harvest (size={PAGE_SIZE}); default {DEFAULT_MAX_PAGES} (full ES CUPRA stock)")
    parser.add_argument("--limit", type=int, default=None,
                        help=(f"optional target car count; converted to a page count ({PAGE_SIZE}/page). "
                              f"The tighter of --pages / --limit bounds the run."))
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"pages fetched in parallel per sliding window; default "
                              f"{DEFAULT_CONCURRENCY}. vtpapi.seat.com inherits the conservative "
                              f"STEALTH rate class — the governor's per-host bucket is the real limiter."))
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.pages, args.concurrency, args.limit))
    _print_report(stats)


if __name__ == "__main__":
    main()
