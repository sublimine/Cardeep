"""oem_ford (Ford Selección ES certified-used) WHOLESALE harvester — a FIFTH OEM-VO portal, end to end.

secure.ford.es/compra/explora/vehiculos-de-ocasion ('Ford Selección', the Approved-Used / Ford
Store VO programme) is the manufacturer-owned certified-used portal for Ford in Spain. Like spoticar
(Stellantis), renew (Renault Group), Das WeltAuto (VW Group) and toyota_lexus (Toyota Group) it is
NOT a car-specialist marketplace (coches.net/autoscout24/motor.es) nor a generalist classifieds
(wallapop): it is an OEM-VO PORTAL — a single brand owner publishing the certified-used inventory of
its own official dealer network (concesionarios oficiales Ford). It is the FIFTH member of the
'oem_vo_portal' source_group, in the new 'ford_vo' family, the sibling of spoticar/renew/dasweltauto/
toyota_lexus under the same ONE architecture.

The surface is an AngularJS SPA (Ford GUXFOE 'approved-used' clientlib) backed by the Ford eUsed
('eUSL') service. The SPA calls ONE internal JSON API — POST
https://www.servicescache.ford.com/api/eUsed/v1/searchVehicles — guarded by Akamai (the API 401s
plain curl) plus a SOFT consumer gate: two computed headers x-eusl-consumer / x-eusl-k. NO bearer
token, NO cookie, NO browser, NO auth login — the headers are generated client-side and are fully
reproducible (verified live 2026-06-13):

  x-eusl-consumer = "b-{applicationName}-{env}"      -> "b-gux_approved_used-prod"
  x-eusl-k        = base64( "{epoch_millis}:{nonce}" )   nonce = 16 random bytes, hex (32 chars)

(plus Referer https://secure.ford.es/ + Origin, to pass Akamai's source check). The applicationName
is the SPA's hard-coded bslHeaderValue 'gux_approved_used'; env derives from the host (secure.ford.es
-> 'prod'). These two headers, regenerated per request, unlock the API cleanly with curl_cffi
chrome131 (defense_tier=t1_soft — Akamai present + a soft, reproducible consumer gate; no JS
challenge). is_tier1=TRUE (the API is fronted by Akamai; akamai-grn header verified).

The request is a GEO-RADIUS search: longLatCoordinates="{lng},{lat}" + distance (km). The radius is
NOT capped — a single national query from the centre of Spain with distance>=2500 km swallows the
whole peninsula AND the Canaries (verified: 482 cars peninsula-only at 1000-1500 km, 543 at
distance>=2000 km). The body's pagination={maxRecords,startingRecord} is a ROW cursor and maxRecords
is honoured well past the page the SPA requests (144) — maxRecords=20000 returns ALL 543 cars in one
response. The set is therefore SMALL and FLAT: ONE national query drains the entire Ford Selección ES
public stock (543 cars, 31 official dealers, 0 missing dealer/postcode/geo — verified live).

The response is {data:{VehicleInventoryList:{totalMatches, VehicleInventoryItem:[{...}]}}}. Each
VehicleInventoryItem carries the car (Vehicle.*) AND its selling official dealer
(VendorInformation.* — VendorCode, VendorName, full postal Address+PostCode+coords). Dealer
attribution is embedded per-car, NO PDP fetch needed. This is an OEM certified-used portal: every
car belongs to a Ford official dealer (concesionario oficial); there are NO private sellers.
Verified live 2026-06-13 (docs/architecture/tier1_recipes/oem_ford_datalayer.md).

This module mirrors pipeline.platform.spoticar_wholesale / oem_toyota_lexus_wholesale EXACTLY (the
proven OEM-VO template: same dual-membership model, same bulk cage, same governor/health/VAM wiring).
It proves the OEM-VO group flows through the ONE architecture, not a fork of it:

  oem_ford (the OEM-VO portal) -> entity, kind='oem_vo_portal' (+ platform_meta)  [THE PLATFORM]
  each SELLING DEALER          -> entity, kind='compraventa'   (geo-resolved)
  each CAR                     -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the portal        -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the selling dealer); platform membership is plural (this edge). The same
physical car can carry BOTH a ford edge and a coches.net edge without ever changing its owning dealer.

GEO anchor: the USC-style VendorInformation.ContactInformation.Address.PostCode IS present and
authoritative — the first 2 digits are the INE province (the renew/toyota model). We prefer
zip->province; the embedded LocationByCoordinates.Latitude/Longitude is the fallback via the
ProvinceGeocoder (nearest labeled point) when the zip is missing/malformed.

Encoding: the eUsed API serves clean UTF-8 (verified — 'GARANTÍA', 'táctil', 'señales' arrive
intact, NOT latin-1 mojibake like spoticar). So NO _fix() round-trip is applied; human-text fields
are taken as-is. There is NO per-car VIN on this surface — only the matrícula
(Vehicle.Identity.RegistrationNumber), kept as the listing fingerprint; vin_ref stays NULL.

Multi-axis classification (migrations/0016):
  defense_tier = 't1_soft'         (Akamai present + a soft reproducible consumer gate; no JS challenge)
  source_group = 'oem_vo_portal'   (the group renew opened; ford is its fifth member)
  role         = 'platform'
  kind         = 'oem_vo_portal'   (the platform entity's ontology kind, migrations/0005)
  is_tier1     = TRUE              (the eUsed API is fronted by Akamai)
  family       = 'ford_vo'         (ties the Ford-group OEM-VO sibling on the family axis)

PROOF SLICE OR FULL. Ford Selección ES declares ~543 cars (totalMatches at distance>=2500 km). The
set is small and FLAT, so the FULL drain is in reach in a SINGLE national request: --pages 1 with the
default page size (20000) walks the whole index. --pages/--limit bound the run; --limit converts a
target car count to a page count. The declared full count is recorded for the VAM verdict's slice
arithmetic.

Engine: a POST against www.servicescache.ford.com/api/eUsed/v1/searchVehicles routed THROUGH the
per-host governor (the same single choke point coches.net/spoticar/AS24 use). The synchronous
curl_cffi POST runs in a worker thread so the event loop is never blocked, and no host is fetched
faster than its bucket (www.servicescache.ford.com inherits the conservative STEALTH class — t1_soft).

Run: python -m pipeline.platform.oem_ford_wholesale --pages 1
"""
from __future__ import annotations

import argparse
import sys
import asyncio
import base64
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
# oem_ford platform identity (OEM-VO portal, migrations/0005 + 0016).
# ---------------------------------------------------------------------------
FORD_DOMAIN = "ford.es"
FORD_WEBSITE = "ford.es"
FORD_LEGAL_NAME = "Ford España (Ford Selección)"
FORD_TRADE_NAME = "ford"
FORD_SOURCE_KEY = "oem_ford_wholesale"
FORD_WAF = "akamai"             # eUsed API 401s plain curl; akamai-grn header present -> is_tier1=TRUE.
FORD_DEFENSE_TIER = "t1_soft"   # Akamai + soft reproducible consumer gate (no JS challenge) -> tier 1 soft.
FORD_SOURCE_GROUP = "oem_vo_portal"
FORD_ROLE = "platform"
FORD_KIND = "oem_vo_portal"     # the platform ENTITY's ontology kind (NOT 'plataforma').
FORD_FAMILY = "ford_vo"         # ties the Ford-group OEM-VO sibling on the family axis.

# The working request (verified live 2026-06-13; recipe oem_ford_datalayer.md TL;DR).
_BASE = "https://www.servicescache.ford.com"
LIST_PATH = "/api/eUsed/v1/searchVehicles"   # the internal eUsed search JSON API.
ENDPOINT = _BASE + LIST_PATH
_PDP_BASE = "https://secure.ford.es/compra/explora/vehiculos-de-ocasion/turismos/results#vehicleDetails"
_IMPERSONATE = "chrome131"
_TIMEOUT = 90

# The eUSL soft-gate (reverse-engineered live from guxfoeApprovedUsed.js v5.35.0). The SPA generates
# both headers per request: consumer = "b-{applicationName}-{env}", k = base64("{millis}:{nonce}").
_EUSL_APPLICATION = "gux_approved_used"   # the SPA's hard-coded bslHeaderValue.
_EUSL_ENV = "prod"                        # derived from host secure.ford.es -> 'prod'.
_EUSL_CONSUMER = f"b-{_EUSL_APPLICATION}-{_EUSL_ENV}"

# Geo-radius national query. longLatCoordinates is "lng,lat"; distance>=2500 km swallows the whole
# peninsula + Canaries (verified: 543 cars saturated). Centre of Spain (Madrid-ish) + a wide radius.
_NATIONAL_LNG = "-3.70"
_NATIONAL_LAT = "40.0"
_NATIONAL_DISTANCE_KM = "2500"
_VEHICLE_CATEGORY = "10"   # 'Personal' (turismos) per searchOptions; the SPA splits "10:Personal".

# Body page size. pagination.maxRecords is honoured well past the SPA's 144 — a single 20000-record
# request returns the entire 543-car national stock FLAT. PAGE_SIZE is the maxRecords per request;
# startingRecord is the ROW cursor (startingRecord += PAGE_SIZE).
PAGE_SIZE = 20000

# Full-drain default. The whole Ford Selección ES network is ~543 cars and FLAT, so ONE national
# request (maxRecords=20000) drains it. DEFAULT_MAX_PAGES=1 walks the whole index; --limit can still
# narrow it. totalMatches + emptiness bound the run.
DEFAULT_MAX_PAGES = 1

# Province sentinel '00' = national (same convention as renew/spoticar/toyota/coches.net/AS24).
# geo_province has NO '00', so the platform ENTITY stores province_code = NULL; '00' lives only
# inside the cdp_code string (free text, no FK). We never pollute geo_province with it.
PLATFORM_PROVINCE_SENTINEL = "00"


def _eusl_headers() -> dict[str, str]:
    """Generate the per-request eUSL soft-gate headers (the EXACT algorithm in guxfoeApprovedUsed.js
    generateToken): consumer is the fixed "b-gux_approved_used-prod"; k is base64 of
    "{epoch_millis}:{nonce}" where nonce is 16 random bytes rendered as 32 hex chars. Regenerated
    per call so each request carries a fresh, valid token (no replay, no shared state)."""
    import time
    nonce = os.urandom(16).hex()
    raw = f"{int(time.time() * 1000)}:{nonce}"
    token = base64.b64encode(raw.encode("utf-8")).decode("ascii")
    return {"x-eusl-consumer": _EUSL_CONSUMER, "x-eusl-k": token}


_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-ES,es;q=0.9",
    "Content-Type": "application/json;charset=UTF-8",
    "Referer": "https://secure.ford.es/",            # Akamai source check requires the ford.es referer.
    "Origin": "https://secure.ford.es",
}


def ford_platform_cdp_code() -> str:
    """The ford platform's immutable cdp_code. Built from the bare domain identity (canonical_key
    'domain:ford.es'), province segment '00' (national). Mirrors spoticar_platform_cdp_code() so
    every platform mints codes the same way."""
    key = f"domain:{FORD_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Field helpers (the eUsed surface: deeply-nested ShortDescription/Code objects, clean UTF-8).
# ---------------------------------------------------------------------------


def _to_int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        try:
            return int(float(v))
        except (TypeError, ValueError):
            return None


def _to_float(v):
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _short(node):
    """Most eUsed enum-ish fields are {"ShortDescription": "...", "Code": {...}}. Pull the human
    ShortDescription scalar; None when absent. Text is clean UTF-8 (no mojibake repair needed)."""
    if isinstance(node, dict):
        val = node.get("ShortDescription")
        return val if isinstance(val, str) and val.strip() else None
    if isinstance(node, str) and node.strip():
        return node
    return None


def _first_address_line(addr: dict) -> str | None:
    """VendorInformation.ContactInformation.Address.FreeTextAddress.AddressLine[].value."""
    try:
        lines = addr["FreeTextAddress"]["AddressLine"]
    except (KeyError, TypeError):
        return None
    if isinstance(lines, list):
        for ln in lines:
            if isinstance(ln, dict):
                v = ln.get("value")
                if isinstance(v, str) and v.strip():
                    return v.strip()
    return None


def _postcode(addr: dict) -> str | None:
    """Address.PostCode.Identifier[0].value (e.g. '28005'). The Identifier list may carry trailing
    nulls; pick the first non-null with a value."""
    try:
        ids = addr["PostCode"]["Identifier"]
    except (KeyError, TypeError):
        return None
    if isinstance(ids, list):
        for it in ids:
            if isinstance(it, dict):
                v = it.get("value")
                if isinstance(v, str) and v.strip():
                    return v.strip()
    return None


def _locality(addr: dict) -> str | None:
    """Address.Locality.NameElement[0].value (e.g. 'MADRID')."""
    try:
        els = addr["Locality"]["NameElement"]
    except (KeyError, TypeError):
        return None
    if isinstance(els, list):
        for el in els:
            if isinstance(el, dict):
                v = el.get("value")
                if isinstance(v, str) and v.strip():
                    return v.strip()
    return None


def _coords(addr: dict) -> tuple[float | None, float | None]:
    """Address.LocationByCoordinates.Latitude/Longitude.DegreesMeasure -> (lat, lon)."""
    try:
        loc = addr["LocationByCoordinates"]
        lat = _to_float(loc["Latitude"]["DegreesMeasure"])
        lon = _to_float(loc["Longitude"]["DegreesMeasure"])
        return (lat, lon)
    except (KeyError, TypeError):
        return (None, None)


def _first_image(vehicle: dict) -> str | None:
    """Vehicle.Configuration.Appearance.ImageRef[0].value — first absolute http(s) image URL."""
    try:
        refs = vehicle["Configuration"]["Appearance"]["ImageRef"]
    except (KeyError, TypeError):
        return None
    if isinstance(refs, list):
        for ref in refs:
            if isinstance(ref, dict):
                u = ref.get("value")
                if isinstance(u, str) and u.startswith("http"):
                    return u
    return None


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL response — field names inspected live 2026-06-13, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class DealerRef:
    """The selling Ford official dealer parsed from a single car's VendorInformation.

    The eUsed doc attaches the full point-of-sale per car: VendorCode (stable per-dealer id),
    VendorName, full postal Address (FreeText + PostCode + Locality + LocationByCoordinates). The
    province comes from the PostCode's first 2 digits (authoritative, the renew model); lat/lon is
    the geocode fallback. VendorCode is the stable per-dealer key for cross-source dedup and as the
    source_ref."""
    dealer_id: str
    name: str | None
    province_code: str | None
    city: str | None
    zip: str | None
    address: str | None
    lat: float | None
    lon: float | None


@dataclass
class Vehicle:
    """A car parsed from a single Ford eUsed VehicleInventoryItem."""
    deep_link: str
    listing_ref: str           # Ford stable car id (Vehicle.Identity.ID) — also the dedup key.
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    vin: str | None            # NO VIN on this surface; matrícula (RegistrationNumber) kept instead.


def parse_item_dealer(item: dict) -> DealerRef | None:
    """Parse the SELLING dealer from a car's VendorInformation. Returns None when there is no stable
    dealer id (VendorCode) — the car cannot be attributed to a concrete POS."""
    vi = item.get("VendorInformation") or {}
    dealer_id = vi.get("VendorCode")
    if not dealer_id:
        return None
    addr = (vi.get("ContactInformation") or {}).get("Address") or {}
    lat, lon = _coords(addr)
    name = vi.get("VendorName")
    name = name.strip() if isinstance(name, str) and name.strip() else None
    return DealerRef(
        dealer_id=str(dealer_id),
        name=name,
        province_code=None,                      # filled by _resolve_province in _parse_window.
        city=_locality(addr),
        zip=_postcode(addr),
        address=_first_address_line(addr),
        lat=lat,
        lon=lon,
    )


def parse_item_vehicle(item: dict) -> Vehicle:
    """Parse the car from a Ford eUsed VehicleInventoryItem (REAL field map, clean UTF-8)."""
    vehicle = item.get("Vehicle") or {}
    vi = item.get("VendorInformation") or {}
    cfg = vehicle.get("Configuration") or {}

    # Price: VendorInformation.Price.value (currency EUR). VATIncIndicator notes whether VAT is
    # included; we store the published value as-is (the price the buyer sees on the PDP).
    price = _to_float((vi.get("Price") or {}).get("value"))

    # Year: History.YearOfProduction (string) — fallback to the registration date's year.
    history = vehicle.get("History") or {}
    year = _to_int(history.get("YearOfProduction"))
    if year is None:
        dor = history.get("DateOfRegistration")  # 'MM/YYYY'
        if isinstance(dor, str) and "/" in dor:
            year = _to_int(dor.rsplit("/", 1)[-1])
    if year is not None and not (1900 <= year <= 2100):
        year = None

    # Km: CurrentCondition.CurrentOdometerReading.value.
    km = _to_int(((vehicle.get("CurrentCondition") or {}).get("CurrentOdometerReading") or {}).get("value"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    make = _short(vehicle.get("Brand"))
    model = _short(vehicle.get("Model"))
    variant = _short(vehicle.get("Variant"))
    title = " ".join(p for p in (make, model, variant) if p) or None

    fuel = _short(cfg.get("FuelType"))
    transmission = _short(cfg.get("TransmissionType"))

    # carid is the stable per-car id AND the dedup key. Clean integer.
    identity = vehicle.get("Identity") or {}
    car_id = identity.get("ID")
    listing_ref = str(car_id) if car_id not in (None, "") else ""

    # Deep link: the SPA PDP route is #vehicleDetails/{ID}/{VendorCode}. Build the canonical
    # absolute URL so platform_listing.listing_url + vehicle.deep_link are stable and dedup-clean.
    dealer_code = vi.get("VendorCode")
    deep_link = (f"{_PDP_BASE}/{listing_ref}/{dealer_code}"
                 if listing_ref and dealer_code else "")

    return Vehicle(
        deep_link=deep_link,
        listing_ref=listing_ref,
        title=title,
        make=make,
        model=model,
        year=year,
        km=km,
        price=price,
        fuel=fuel,
        transmission=transmission,
        photo_url=_first_image(vehicle),
        vin=None,   # no VIN on this surface; matrícula is not a VIN, so vin_ref stays NULL.
    )


# ---------------------------------------------------------------------------
# Fetch: a POST routed THROUGH the governor (same per-host choke point as renew/coches.net).
# ---------------------------------------------------------------------------


class FordFetcher:
    """A POOL of fingerprint-coherent curl_cffi POST sessions for the Ford eUsed search API.

    Same concurrency-vs-coherence model as SpoticarFetcher / RenewFetcher: a single curl_cffi
    Session is NOT safe to call from several threads at once, and the governor runs each fetch in
    its own worker thread (asyncio.to_thread). The fix is a bounded POOL — one Session per
    concurrency slot, each its own Chrome fingerprint + cookie jar. The governor's per-host bucket
    bounds the AGGREGATE rate across every session, so the pool widens parallelism WITHOUT
    out-pacing the host (the choke point is the bucket, never the session count).
    """

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def _build_body(self, starting_record: int, page_size: int) -> dict:
        """The national geo-radius search body. Mirrors the EXACT live SPA payload (captured from
        the real searchVehicles POST) but widened: distance=2500 km (national + Canaries), all
        ranges unbounded so NOTHING is filtered out, maxRecords=page_size, startingRecord=cursor."""
        return {
            "locale": "es_ES",
            "vehicleCategory": _VEHICLE_CATEGORY,
            "distance": _NATIONAL_DISTANCE_KM,
            "longLatCoordinates": f"{_NATIONAL_LNG},{_NATIONAL_LAT}",
            "price": {"minPrice": "0", "maxPrice": "9999999"},
            "enginePower": {"min": "0", "max": "99999"},
            "ageOfVehicle": {"min": "0", "max": "99"},
            "mileage": {"min": "0", "max": "9999999"},
            "resultOrder": {"orderBy": "Price", "sortOrder": "Ascending"},
            "pagination": {"maxRecords": page_size, "startingRecord": starting_record},
        }

    def fetch_page(self, url: str, *, offset: int = 0, page_size: int = PAGE_SIZE,
                   slot: int = 0) -> dict:
        """The synchronous POST on pool session `slot` (runs in a worker thread).

        Handed to governor().wrap_fetch_text: the governor derives the host from `url`, waits on the
        per-host bucket, then runs THIS off the event loop. `slot`/`offset`/`page_size` ride as
        kwargs the governor forwards untouched, so each in-flight request POSTs on its own leased,
        never-shared curl_cffi session (thread-safe). A FRESH eUSL token is minted per request (the
        soft-gate forbids replay). Raises on a non-200 so the breaker sees throttling (never masks
        a challenge/empty body)."""
        session = self._sessions[slot]
        headers = dict(_HEADERS)
        headers.update(_eusl_headers())
        body = self._build_body(offset, page_size)
        resp = session.post(url, data=json.dumps(body), headers=headers,
                            impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url} (offset {offset})")
        # The eUsed API serves clean UTF-8 JSON; decode explicitly.
        return json.loads(resp.content.decode("utf-8", "replace"))

    async def fetch_page_async(self, governed_fetch, url: str, *, offset: int,
                               page_size: int = PAGE_SIZE) -> dict:
        """Lease a pool slot, fetch `offset` THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, offset=offset, page_size=page_size, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer (mirrors spoticar_wholesale: ensure platform, bulk-upsert dealer/vehicle, link edge,
# emit delta, all idempotent ON CONFLICT). Multi-axis 0016 classification set.
# ---------------------------------------------------------------------------

FORD_PLATFORM_RECIPE = {
    "version": 1,
    "source": "ford (Ford Selección — secure.ford.es/compra/explora/vehiculos-de-ocasion)",
    "scope": "platform-wholesale (Ford ES certified-used; AngularJS GUXFOE SPA + eUsed JSON API)",
    "engine": "curl_cffi+chrome131_impersonate+internal_eused_json_api(POST)",
    "access": ("OPEN-via-fingerprint+soft-gate. The eUsed API 401s plain curl (Akamai source check + "
               "consumer gate). Two computed headers unlock it: x-eusl-consumer='b-gux_approved_used-prod', "
               "x-eusl-k=base64('{millis}:{nonce}') (16-byte hex nonce), regenerated per request, plus "
               "Referer https://secure.ford.es/. No proxy, no browser, no cookie, no auth, €0. Public API "
               "behind Akamai -> is_tier1=TRUE; the soft reproducible gate (no JS challenge) -> "
               "defense_tier=t1_soft."),
    "data_surface": "internal_api",
    "surface_intent": "internal_eused_json_api",
    "endpoint": "POST https://www.servicescache.ford.com/api/eUsed/v1/searchVehicles",
    "request": {
        "headers": ("Accept application/json, Content-Type application/json, Referer "
                    "https://secure.ford.es/, Origin https://secure.ford.es, x-eusl-consumer "
                    "b-gux_approved_used-prod, x-eusl-k base64('{epoch_millis}:{16B-hex-nonce}')"),
        "eusl_algo": ("reverse-engineered from guxfoeApprovedUsed.js v5.35.0 generateToken: "
                      "consumer='b-'+applicationName+'-'+env (applicationName='gux_approved_used' is "
                      "the SPA bslHeaderValue; env='prod' from host); k=base64(Date.now()+':'+nonce), "
                      "nonce=16 random bytes hex."),
        "body": ("JSON: locale=es_ES, vehicleCategory='10' (Personal/turismos), distance (km), "
                 "longLatCoordinates='{lng},{lat}', price/enginePower/ageOfVehicle/mileage ranges, "
                 "resultOrder={orderBy,sortOrder}, pagination={maxRecords,startingRecord}"),
    },
    "enumeration": ("SINGLE national geo-radius query: longLatCoordinates='-3.70,40.0' + distance=2500 km "
                    "(swallows peninsula + Canaries; 482 cars at <=1500 km, 543 at >=2000 km). "
                    "pagination.maxRecords=20000 returns ALL 543 in ONE response (FLAT, no depth wall). "
                    "startingRecord is a ROW cursor for safety; totalMatches + empty VehicleInventoryItem "
                    "bound the run; dedup on Vehicle.Identity.ID."),
    "denominator": "data.VehicleInventoryList.totalMatches (543) == distinct Vehicle.Identity.ID == Σ dealer attribution",
    "platform_entity": ("kind=oem_vo_portal, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=TRUE, defense_tier=t1_soft, source_group=oem_vo_portal, role=platform, "
                        "family=ford_vo"),
    "dual_membership": ("vehicle.entity_ulid=SELLING DEALER (compraventa); "
                        "platform_listing edge=platform<->vehicle"),
    "field_map": {
        "deep_link": "secure.ford.es/.../results#vehicleDetails/{Vehicle.Identity.ID}/{VendorCode}",
        "listing_ref": "Vehicle.Identity.ID (stable car id + dedup key)",
        "vin": "NONE on this surface (only Vehicle.Identity.RegistrationNumber matrícula) -> vin_ref NULL",
        "make": "Vehicle.Brand.ShortDescription (FORD)",
        "model": "Vehicle.Model.ShortDescription",
        "variant": "Vehicle.Variant.ShortDescription",
        "year": "Vehicle.History.YearOfProduction (fallback DateOfRegistration year)",
        "km": "Vehicle.CurrentCondition.CurrentOdometerReading.value",
        "price": "VendorInformation.Price.value (currency EUR; VATIncIndicator notes VAT inclusion)",
        "fuel": "Vehicle.Configuration.FuelType.ShortDescription",
        "transmission": "Vehicle.Configuration.TransmissionType.ShortDescription",
        "photo": "Vehicle.Configuration.Appearance.ImageRef[0].value",
        "dealer": "VendorInformation {VendorCode, VendorName, ContactInformation.Address.*}",
        "location": ("Address.PostCode.Identifier[0].value[:2] = INE province (authoritative); "
                     "Address.LocationByCoordinates.Lat/Lon -> ProvinceGeocoder fallback; "
                     "Address.Locality.NameElement[0].value -> municipality (INE-resolved)"),
    },
    "caveats": {
        "page_size": "pagination.maxRecords is honoured well past the SPA's 144; 20000 returns all 543 FLAT.",
        "radius_not_capped": "distance is NOT capped — distance>=2500 km enumerates the whole country.",
        "lnglat_order": "longLatCoordinates is 'lng,lat' (NOT lat,lng) — wrong order yields 0 matches.",
        "encoding": "clean UTF-8 over the wire (NOT latin-1 mojibake like spoticar); no _fix() applied.",
        "no_vin": "no per-car VIN; only the matrícula (RegistrationNumber). vin_ref stays NULL.",
        "eusl_freshness": "x-eusl-k must be regenerated per request (timestamp+nonce); replay is rejected.",
        "no_private_sellers": "OEM certified-used portal — every car belongs to a Ford official dealer.",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the ford platform entity + platform_meta exist. Returns the platform
    entity_ulid. kind='oem_vo_portal' (the platform ontology kind), is_tier1=TRUE (Akamai fronts the
    eUsed API), multi-axis 0016 classification set explicitly, data_surface='internal_api'."""
    code = ford_platform_cdp_code()
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
        eulid, code, FORD_KIND, FORD_LEGAL_NAME, FORD_TRADE_NAME, FORD_WEBSITE,
        FORD_WAF, FORD_DEFENSE_TIER, FORD_SOURCE_GROUP, FORD_ROLE, FORD_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, FORD_SOURCE_KEY, FORD_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'internal_api',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"endpoint": ENDPOINT, "host": host_of(ENDPOINT),
                           "method": "POST", "page_size": PAGE_SIZE,
                           "denominator": "totalMatches",
                           "surface_intent": "internal_eused_json_api",
                           "engine": "curl_cffi/chrome131_impersonate+eusl_soft_gate"}),
        FORD_FAMILY)
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    Ford dealers have no bare domain on this surface -> identity = name + location + the stable
    VendorCode (passed via `address` so two distinct POS that happen to share a name in one
    municipality never collapse to one entity)."""
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni, address=f"dealer:{d.dealer_id}")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# Default concurrency: pages fetched in parallel per sliding window. www.servicescache.ford.com is
# NOT in the governor's JSON_API rate class — it inherits the conservative STEALTH default, the safe
# direction for a t1_soft Akamai-fronted host whose true ceiling is unmeasured. With the whole stock
# in ONE national request, concurrency rarely matters here, but the window machinery is kept
# byte-identical to the proven OEM-VO template.
DEFAULT_CONCURRENCY = 2


@dataclass
class _CageRow:
    """One fully-parsed, geo-anchored car ready for the bulk cage — the in-memory result of the
    parse+resolve phase, before any SQL. Carries everything the batched upserts need so the DB
    phase touches no per-item Python logic, only set-based statements."""
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
    renew/toyota model). FALLBACK: geocode from lat/lon (nearest labeled point) when the zip is
    missing/malformed. Returns a validated '01'..'52' code or None."""
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
    """Parse + geo-resolve every car across the window IN ORDER — pure CPU, no SQL.

    The EXACT per-item gate (cross-page dedup on Vehicle.Identity.ID, dealer-parse skip, geo skip,
    cageable truth), lifted out of the DB loop so the SQL phase is purely set-based. The province is
    resolved zip-first then geocode-fallback. `seen_ids` / `harvested_cageable` / `stats` are mutated
    here with deterministic order semantics so the VAM truth is byte-identical regardless of
    batching. Each tuple is (offset, items)."""
    rows: list[_CageRow] = []
    for _offset, items in items_by_page:
        for item in items:
            if not isinstance(item, dict):
                continue
            stats["items_seen"] += 1
            # cross-page dedup on the car id (the stable dedup key; default sort is not stable across
            # a long crawl, so the same car can reappear on a later page/offset).
            try:
                item_id = str((item.get("Vehicle") or {}).get("Identity", {}).get("ID") or "")
            except (AttributeError, TypeError):
                item_id = ""
            if item_id and item_id in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue
            if item_id:
                seen_ids.add(item_id)

            d = parse_item_dealer(item)
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
                          city=d.city, zip=d.zip, address=d.address, lat=d.lat, lon=d.lon)
            muni = geo.municipality_code(prov, d.city)
            dealer_cdp = cdp_code_dealer(d, muni)

            v = parse_item_vehicle(item)
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

    Mirrors spoticar_wholesale._ingest_window EXACTLY: ONE round-trip per table per window (unnest
    multi-row upserts). The delta/VAM/platform_listing semantics are preserved: same ON CONFLICT
    idempotency, same cageable truth, same NEW-event rule (emitted only for genuinely new vehicles).
    A re-run of an already-harvested window adds 0 rows and 0 events.
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
                           d_munis, d_refs, FORD_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_DEALER_SOURCES, d_cdps, d_refs, FORD_SOURCE_KEY)
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
                payload = {"price": v.price, "title": v.title, "platform": FORD_TRADE_NAME}
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
    fetcher = FordFetcher(pool_size=concurrency)
    stats = {
        "pages_fetched": 0, "items_seen": 0, "dealer_items": 0,
        "no_dealer_skipped": 0, "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "vins_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "dealers_distinct": 0,
        "concurrency": concurrency, "max_pages": max_pages, "private_skipped": 0,
    }
    # Harvest-side truth for the VAM: distinct CAGEABLE cars = distinct (dealer_id, deep_link) pairs
    # that survived dealer-parse + geo-resolution. Like-with-like vs db_edges.
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if ford's breaker is OPEN (a recent ban/throttle still cooling), skip the drain
    # gracefully — the API keeps serving the last snapshot.
    if await is_open(conn, FORD_SOURCE_KEY):
        print(f"[oem_ford_wholesale] breaker OPEN for {FORD_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, API still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": FORD_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        geocoder = await ProvinceGeocoder.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = ford_platform_cdp_code()
        print(f"[oem_ford_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid}) "
              f"kind={FORD_KIND} group={FORD_SOURCE_GROUP} tier={FORD_DEFENSE_TIER} "
              f"family={FORD_FAMILY}")
        print(f"[oem_ford_wholesale] geocoder anchors: {geocoder.size()} labeled points (lat/lon -> province).")
        print(f"[oem_ford_wholesale] governor paces host {host_of(ENDPOINT)} (per-host token bucket, STEALTH class).")
        print(f"[oem_ford_wholesale] CONCURRENT drain: window={concurrency} requests in flight. "
              f"Target = {max_pages} request(s) (~{max_pages * PAGE_SIZE} cars cap; full ES stock ~543).")

        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        # CONCURRENT sliding-window drain. Each window fetches up to `concurrency` requests in
        # parallel through the governor (the host bucket paces the aggregate), then the responses are
        # INGESTED sequentially in offset order through the single asyncpg connection. A response that
        # errors or comes back empty stops the drain honestly (end of data, or a throttle the breaker
        # must catch). totalMatches also bounds the run. With PAGE_SIZE=20000 the whole stock arrives
        # in the first request; the loop naturally stops on the next empty offset.
        stop = False
        next_page = 0
        while next_page < max_pages and not stop:
            window = list(range(next_page, min(next_page + concurrency, max_pages)))
            next_page = window[-1] + 1

            results = await asyncio.gather(
                *(fetcher.fetch_page_async(governed_fetch, ENDPOINT, offset=p * PAGE_SIZE)
                  for p in window),
                return_exceptions=True,
            )

            window_pages: list[tuple[int, list]] = []
            for page, data in zip(window, results):
                if isinstance(data, Exception):
                    fetch_error = str(data)
                    last_http = fetcher.last_status
                    print(f"[oem_ford_wholesale] request {page} fetch failed ({data}); stopping drain honestly.")
                    stop = True
                    break
                vil = ((data.get("data") or {}).get("VehicleInventoryList") or {})
                if stats["declared_full"] is None:
                    stats["declared_full"] = _to_int(vil.get("totalMatches"))
                items = vil.get("VehicleInventoryItem") or []
                if not items:
                    print(f"[oem_ford_wholesale] request {page} (offset {page * PAGE_SIZE}): no items; "
                          f"stopping (data boundary reached).")
                    stop = True
                    break
                window_pages.append((page * PAGE_SIZE, items))

            if window_pages:
                await _ingest_window(conn, geo, geocoder, platform_ulid, window_pages, seen_ids,
                                     harvested_cageable, stats)
                stats["pages_fetched"] += len(window_pages)
                first_p, last_p = window_pages[0][0], window_pages[-1][0]
                print(f"[oem_ford_wholesale] window offsets {first_p}-{last_p}: "
                      f"items={sum(len(it) for _, it in window_pages)} "
                      f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                      f"edges={stats['edges_created']} dealers_seen={len(harvested_cageable)}")
            # If the only request returned fewer than PAGE_SIZE rows, the stock is fully drained —
            # the next offset would be empty, so stop without an extra round-trip.
            if window_pages and sum(len(it) for _, it in window_pages) < PAGE_SIZE * len(window_pages):
                stop = True

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, FORD_PLATFORM_RECIPE)
        print(f"[oem_ford_wholesale] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths that all measure
        # "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for ford      (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join  (DB read truth)
        #   harvested_cageable = distinct (dealer_id, deep_link) pulled (harvest truth)
        # The declared full count (totalMatches) is reported for honesty but is NOT a quorum path (it
        # measures the WHOLE portal, equal to this slice only when the full national drain ran).
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

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks ford, trips the
        # breaker on a ban, and auto-repairs. OK when >=1 request fetched, no fetch error stopped the
        # drain, and the VAM did not refute.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, FORD_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, FORD_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[oem_ford_wholesale] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("FORD SELECCIÓN (OEM-VO PORTAL) WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  group / kind          : oem_vo_portal / oem_vo_portal (tier t1_soft, family ford_vo)")
    print(f"  declared full (source): {stats.get('declared_full')}")
    print(f"  concurrency (window)  : {stats.get('concurrency')} requests in flight")
    print(f"  target requests       : {stats.get('max_pages')}")
    print(f"  requests fetched      : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  dealer items          : {stats['dealer_items']}")
    print(f"  no-dealer skipped     : {stats['no_dealer_skipped']}")
    print(f"  private skipped       : {stats['private_skipped']} (OEM portal — none expected)")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page, Identity.ID dedup)")
    print(f"  geo skipped (bad geo) : {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for ford = {stats.get('db_edges')})")
    print(f"  VINs captured         : {stats['vins_captured']} (no VIN on this surface — expected 0)")
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
        description="ford OEM-VO portal wholesale harvester (concurrent internal-eUsed-JSON drain)")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=(f"requests to harvest (size={PAGE_SIZE}); default {DEFAULT_MAX_PAGES} "
                              f"(one national request drains the full ES stock ~543)"))
    parser.add_argument("--limit", type=int, default=None,
                        help=("optional target car count; converted to a request count "
                              "(PAGE_SIZE/request). The tighter of --pages / --limit bounds the run."))
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"requests fetched in parallel per sliding window; default "
                              f"{DEFAULT_CONCURRENCY}. www.servicescache.ford.com inherits the "
                              f"conservative STEALTH rate class — the governor's per-host bucket is "
                              f"the real limiter."))
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.pages, args.concurrency, args.limit))
    _print_report(stats)


if __name__ == "__main__":
    main()
