"""Nissan Intelligent Choice (Nissan ES certified-used) WHOLESALE harvester — a FIFTH OEM-VO portal, end to end.

www.ocasion.nissan.es is the manufacturer certified-used portal for Nissan in Spain ("Nissan
Intelligent Choice" — the brand's official seminuevos/ocasión programme, every car a "Nissan
Certified" unit sold by a concesionario oficial Nissan). Like renew (Renault Group), spoticar
(Stellantis), Das WeltAuto (VW Group) and toyota_lexus it is NOT a car-specialist marketplace
(coches.net/autoscout24/motor.es) nor a generalist classifieds (wallapop): it is an OEM-VO
PORTAL — a single brand-owner publishing the certified-used inventory of its own official dealer
network. It is the FIFTH member of the 'oem_vo_portal' source_group, in a new
'nissan_intelligent_choice' family.

WHY NISSAN OF THE THREE (nissan_mazda_honda front): the INTEL named Nissan Intelligent Choice +
Mazda Selected + Honda Approved and said "pick whichever exposes a clean surface". Probed live
2026-06-13:
  - Nissan  ocasion.nissan.es  -> Next.js SSR app backed by an AWS AppSync GraphQL data-layer.
                                  CLEAN, FLAT, fully-specced JSON + a dealer-locator query that
                                  resolves every dealerId to postCode/lat-lng/city. CHOSEN.
  - Mazda   mazdaselected.es    -> WALLED: TLS connect times out to curl_cffi (no clean surface
                                  reachable; needs camoufox / a different ingress). Skipped.
  - Honda   vehiculosdeocasion.honda.es -> server-rendered jQuery site; the "buscador" paginates
                                  by re-GETting the SAME HTML URL (no JSON data-layer). That is an
                                  HTML/facet workaround, not a data-layer surface — and the brief
                                  is "exhaust uncapped data-layer surfaces before any facet
                                  workaround". Skipped in favour of Nissan's pristine API.
So this connector caters the front by connecting the ONE of the three that exposes a real
internal data surface — Nissan — exactly as spoticar caters the whole Stellantis group through
one portal.

THE SURFACE (verified live 2026-06-13; recipe oem_nissan_mazda_honda_datalayer.md):
  1. A public, unauthenticated token mint:
        GET https://apigateway-eu-prod.nissanpace.com/euw1nisprod/public-access-token
            ?brand=NISSAN&dataSourceType=live&market=ES&client=euecomm
     returns {idToken: "<Cognito JWT>"} — no login, no cookie warm-up, no proxy. €0.
  2. The inventory GraphQL (AWS AppSync) at
        POST https://gq-eu-prod.nissanpace.com/graphql
     with header  Authorization: <idToken>  and the GetUsedCarsInventoryData query (lifted
     byte-for-byte from the site's own index chunk). variables.usedCarsInventoryInputData.pageNumber
     walks page 1..104. The response carries metaData.totalCount (1546) / totalPages (104), and
     vehicles[] = 15 FULLY-SPECCED cars/page, each with a REAL per-car VIN (gold for cross-source
     dedup) and an embedded dealer {dealerId, dealerName}. FLAT — no relevance cap, no depth wall.
  3. The dealer-locator GraphQL on the SAME endpoint:
        getDealersData(marketConfig, locationDataInput{lat,long,radius,unit})
     centred on Spain with a 2000 km radius returns the WHOLE Nissan ES dealer roster (180
     concesionarios oficiales) each with postCode + city + location{gpsLatitude,gpsLongitude}.
     The inventory's dealer object has NO geo, so we pre-fetch this roster ONCE and map every
     car's dealerId -> postCode (first 2 digits = INE province) + lat/lng (geocoder fallback).

curl_cffi chrome131 serves the whole flow with no WAF challenge -> defense_tier='t0_open'. There
is no Akamai/Cloudflare gate on the API (the public token endpoint and AppSync both answer the
Chrome JA3 directly). This is an OEM certified-used portal: every car belongs to a Nissan dealer
(concesionario oficial); there are NO private sellers.

This module mirrors pipeline.platform.spoticar_wholesale / renew_wholesale EXACTLY (same dual-
membership model, same bulk cage, same governor/health/VAM wiring). It proves the OEM-VO group
flows through the ONE architecture, not a fork of it:

  nissan (the OEM-VO portal)  -> entity, kind='oem_vo_portal' (+ platform_meta)  [THE PLATFORM]
  each SELLING DEALER         -> entity, kind='compraventa'   (geo-resolved)
  each CAR                    -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the portal       -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the selling concesionario); platform membership is plural (this edge). The
same physical car can carry BOTH a nissan edge and a coches.net edge without ever changing its
owning dealer.

GEO anchor difference vs spoticar: spoticar dealers carry only lat/lng (geocoded). Nissan dealers
carry BOTH a real postCode (first 2 digits = INE province, the exact primary path) AND a lat/lng
(the ProvinceGeocoder fallback when the postcode is missing/odd). The municipality is resolved
from (province, city) via the GeoResolver; dealerId = the Nissan internal dealer code (NOT a
province prefix — dealer 41020014 sits in postcode 08210/Barcelona — so the geo comes from the
locator roster, never the id).

Encoding trap (same as spoticar): the API serves dealer/city text as latin-1 mojibake over the
wire (LLANS� = "LLANSÀ", BARBER� = "BARBERÀ"). Re-encode every human-text field:
s.encode("latin-1").decode("utf-8"). The numeric fields, VIN and dealerId are clean.

Multi-axis classification (migrations/0016):
  defense_tier = 't0_open'                 (open AppSync GraphQL + public token; no WAF challenge)
  source_group = 'oem_vo_portal'           (the group renew opened; nissan is its fifth member)
  role         = 'platform'
  kind         = 'oem_vo_portal'           (the platform entity's ontology kind, migrations/0005)
  is_tier1     = FALSE                     (no WAF fronting the API)
  family       = 'nissan_intelligent_choice'

PROOF SLICE OR FULL. nissan declares 1,546 cars (metaData.totalCount). The set is small and FLAT,
so the FULL drain is in reach in a single run: --pages 104 walks the whole index (page 104 = 1
trailing car, page 105 = 0). --pages/--limit bound the run; --limit converts a target car count
to a page count. The declared full count is recorded for the VAM verdict's slice arithmetic.

Engine: a POST against gq-eu-prod.nissanpace.com/graphql routed THROUGH the per-host governor
(the same single choke point coches.net/renew/spoticar use). The synchronous curl_cffi POST runs
in a worker thread so the event loop is never blocked, and no host is fetched faster than its
bucket (gq-eu-prod.nissanpace.com inherits the conservative STEALTH class).

Run: python -m pipeline.platform.oem_nissan_mazda_honda_wholesale --pages 104
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
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
# nissan platform identity (OEM-VO portal, migrations/0005 + 0016).
# ---------------------------------------------------------------------------
NISSAN_DOMAIN = "ocasion.nissan.es"
NISSAN_WEBSITE = "ocasion.nissan.es"
NISSAN_LEGAL_NAME = "Nissan Iberia (Nissan Intelligent Choice)"
NISSAN_TRADE_NAME = "nissan_intelligent_choice"
NISSAN_SOURCE_KEY = "nissan_intelligent_choice_wholesale"
NISSAN_WAF = "none"               # the AppSync GraphQL + public token serve to curl_cffi with no challenge.
NISSAN_DEFENSE_TIER = "t0_open"   # open API, no WAF challenge -> tier 0.
NISSAN_SOURCE_GROUP = "oem_vo_portal"
NISSAN_ROLE = "platform"
NISSAN_KIND = "oem_vo_portal"     # the platform ENTITY's ontology kind (NOT 'plataforma').
NISSAN_FAMILY = "nissan_intelligent_choice"

# The working requests (verified live 2026-06-13; recipe oem_nissan_mazda_honda_datalayer.md).
_SITE = "https://www.ocasion.nissan.es"
TOKEN_URL = ("https://apigateway-eu-prod.nissanpace.com/euw1nisprod/public-access-token"
             "?brand=NISSAN&dataSourceType=live&market=ES&client=euecomm")
ENDPOINT = "https://gq-eu-prod.nissanpace.com/graphql"   # the AWS AppSync inventory + dealer API.

_HEADERS = {
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Accept-Language": "es-ES,es;q=0.9",
    "Origin": _SITE,
    "Referer": _SITE + "/",
}
_PDP_BASE = _SITE + "/all-vehicles/detail/"   # vehiclesku -> canonical PDP path.
_IMPERSONATE = "chrome131"
_TIMEOUT = 45
PAGE_SIZE = 15  # the API serves a FIXED 15 cars/page (server-side; not a request param).

# The GraphQL operation, lifted BYTE-FOR-BYTE from the site's own index chunk
# (index-f3e7293228f0bf0c.js). Trimmed to the fields we actually cage (the full chunk query also
# pulls msrpOfferPrice/facets/i18n labels we don't need). The shape of vehicles{} and metaData{}
# is unchanged from the live query.
_INVENTORY_QUERY = (
    "query GetUsedCarsInventoryData($marketConfig: MarketConfig!, "
    "$usedCarsInventoryInputData: UsedCarsInventoryInputData!) { "
    "getUsedCarsInventoryData(marketConfig: $marketConfig, "
    "usedCarsInventoryInputData: $usedCarsInventoryInputData) { "
    "vehicles { make modelName version shortVersion mileage registrationYear registrationMonth "
    "fuelType transmission gearbox rrpPrice discountedPrice thumbnailUrl "
    "dealer { dealerId dealerName } vin vehiclesku modelYear certificationLabel } "
    "metaData { totalCount totalPages pageIndex pageSize hasMorePages } } }"
)

# The dealer-locator operation (same endpoint). Spain-centred, 2000 km radius -> the whole ES
# Nissan roster (180 concesionarios) each with postCode + city + lat/lng. Fetched ONCE per run.
_DEALERS_QUERY = (
    "query GetDealers($marketConfig: MarketConfig!, $loc: LocationInput) { "
    "getDealersData(marketConfig: $marketConfig, locationDataInput: $loc) { "
    "id name postCode city region stateCode addressLine1 "
    "location { gpsLatitude gpsLongitude } } }"
)

# The market config + base input (lifted from attributesData.variables on the SSR page).
_MARKET_CONFIG = {"brand": "NISSAN", "country": "ES", "language": "es",
                  "metadata": {"clientApp": "[WEB]USEDCARS", "correlationId": ""}}
_BASE_INPUT = {
    "usedCarsServletURL": "/content/nissan_prod/es_ES/index/cf-used-cars-ecom.model.json",
    "includeCentralStock": False,
    "minLatestAchievementPoint": 40,
    "withDiscounts": False,
    "vinListType": "used_cars",
    "dealerId": "",
    "queryFilters": [{"type": "make", "values": ["Nissan"]}],
    "parentFilter": "queryFilters",
}
# Spain centre + 2000 km radius covers the whole peninsula + islands for the dealer roster.
_DEALER_LOC = {"lat": 40.4, "long": -3.7, "radius": 2000, "unit": "K"}

# Month abbreviations the API uses for registrationMonth (kept for completeness; we cage the year).
# Province sentinel '00' = national (same convention as renew/spoticar/coches.net). geo_province
# has NO '00', so the platform ENTITY stores province_code = NULL; '00' lives only inside the
# cdp_code string (free text, no FK). We never pollute geo_province with it.
PLATFORM_PROVINCE_SENTINEL = "00"

# Full-drain default. 1,546 cars / 15 per page = 104 data pages (page 104 = 1 trailing car;
# 105+ = 0). totalCount + emptiness bound the run. A small slice (--pages 5) is a proof slice;
# --pages 104 is the full ES public stock.
DEFAULT_MAX_PAGES = 104


def nissan_platform_cdp_code() -> str:
    """The nissan platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:ocasion.nissan.es'), province segment '00' (national). Mirrors
    spoticar_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{NISSAN_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Field helpers (the nissan surface: scalar fields + latin-1 mojibake on human text).
# ---------------------------------------------------------------------------


def _fix(s):
    """Repair latin-1 mojibake on human-text fields (LLANS� -> LLANSÀ, BARBER� ->
    BARBERÀ). The wire bytes were UTF-8 mis-decoded as latin-1 upstream; re-encode to recover.
    Numeric fields, VIN and dealerId are clean and never passed here."""
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
        return int(float(v))   # mileage arrives as "91587.0"; float-then-int is safe.
    except (TypeError, ValueError):
        return None


def _to_float(v):
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# Fuel/gearbox normalization. The API serves clean accent-free codes for the finite vocabularies;
# normalize to proper Spanish labels deterministically (no invention, just the clean source signal).
_FUEL_CLEAN = {
    "gasolina": "Gasolina", "diesel": "Diésel", "disel": "Diésel",
    "electrico": "Eléctrico", "hibrido": "Híbrido",
    "hibridoenchufable": "Híbrido enchufable", "glp": "GLP", "gnc": "GNC",
}
_GEARBOX_CLEAN = {"manual": "Manual", "automatico": "Automático", "automtico": "Automático"}


def _norm_key(s) -> str:
    import re as _re
    return _re.sub(r"[^a-z]", "", str(s).lower()) if isinstance(s, str) else ""


def _clean_fuel(fuel) -> str | None:
    val = _fix(fuel)
    if not isinstance(val, str):
        return None
    return _FUEL_CLEAN.get(_norm_key(val), val)


def _clean_gearbox(transmission) -> str | None:
    val = _fix(transmission)
    if not isinstance(val, str):
        return None
    return _GEARBOX_CLEAN.get(_norm_key(val), val)


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL response — field names inspected live 2026-06-13, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class DealerGeo:
    """A Nissan concesionario from the dealer-locator roster (getDealersData).

    Carries the geo anchor the inventory's bare dealer object lacks: postCode (first 2 digits =
    INE province, the exact primary path), city (-> municipality), and lat/lng (the geocoder
    fallback). id is the Nissan internal dealer code (== the inventory's dealerId), the stable
    per-dealer key for cross-source dedup and the source_ref."""
    dealer_id: str
    name: str | None
    post_code: str | None
    city: str | None
    lat: float | None
    lng: float | None


@dataclass
class Vehicle:
    """A car parsed from a single nissan inventory item."""
    deep_link: str
    listing_ref: str           # nissan stable car id (vehiclesku) — also the dedup key.
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    vin: str | None            # REAL per-car VIN — gold for cross-source dedup.
    dealer_id: str             # the selling concesionario's Nissan code (joins to the roster).
    dealer_name: str | None


def parse_dealer_geo(node: dict) -> DealerGeo | None:
    """Parse one roster dealer. Returns None when there is no stable id."""
    did = node.get("id")
    if not did:
        return None
    loc = node.get("location") or {}
    return DealerGeo(
        dealer_id=str(did),
        name=_fix(node.get("name")),
        post_code=(str(node["postCode"]).strip() if node.get("postCode") else None),
        city=_fix(node.get("city")),
        lat=_to_float(loc.get("gpsLatitude")),
        lng=_to_float(loc.get("gpsLongitude")),
    )


def parse_item_vehicle(v: dict) -> Vehicle | None:
    """Parse the car from a nissan inventory item (REAL field map). Returns None when there is no
    selling dealer id (the car cannot be attributed to a concrete concesionario)."""
    dealer = v.get("dealer") or {}
    dealer_id = dealer.get("dealerId")
    if not dealer_id:
        return None

    # discountedPrice is the offer price; rrpPrice the RRP. Prefer the offer (what is sold).
    price = _to_float(v.get("discountedPrice")) or _to_float(v.get("rrpPrice"))

    year = _to_int(v.get("registrationYear")) or _to_int(v.get("modelYear"))
    if year is not None and not (1900 <= year <= 2100):
        year = None

    km = _to_int(v.get("mileage"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    # vehiclesku is the stable per-car id AND the dedup key (es_NISSAN_<vin>). Clean.
    sku = v.get("vehiclesku") or v.get("vin") or ""
    listing_ref = str(sku)
    deep_link = (_PDP_BASE + listing_ref) if listing_ref else ""

    make = _fix(v.get("make")) or "NISSAN"
    model = _fix(v.get("modelName"))
    version = _fix(v.get("version"))
    title = " ".join(p for p in (make, model, version) if p) or None

    vin = v.get("vin")

    return Vehicle(
        deep_link=deep_link,
        listing_ref=listing_ref,
        title=title,
        make=make,
        model=model,
        year=year,
        km=km,
        price=price,
        fuel=_clean_fuel(v.get("fuelType")),
        transmission=_clean_gearbox(v.get("transmission")),
        photo_url=(v.get("thumbnailUrl") if isinstance(v.get("thumbnailUrl"), str)
                   and v.get("thumbnailUrl").startswith("http") else None),
        vin=str(vin) if vin else None,
        dealer_id=str(dealer_id),
        dealer_name=_fix(dealer.get("dealerName")),
    )


# ---------------------------------------------------------------------------
# Fetch: a POST routed THROUGH the governor (same per-host choke point as renew/spoticar).
# ---------------------------------------------------------------------------


class NissanFetcher:
    """A POOL of fingerprint-coherent curl_cffi POST sessions for the nissan AppSync GraphQL API.

    Same concurrency-vs-coherence model as SpoticarFetcher / RenewFetcher: a single curl_cffi
    Session is NOT safe to call from several threads at once, and the governor runs each fetch in
    its own worker thread (asyncio.to_thread). The fix is a bounded POOL — one Session per
    concurrency slot, each its own Chrome fingerprint + cookie jar. The governor's per-host bucket
    bounds the AGGREGATE rate across every session, so the pool widens parallelism WITHOUT
    out-pacing the host (the choke point is the bucket, never the session count).

    The Cognito idToken is minted ONCE at construction from the public token endpoint (no auth,
    no cookie) and reused as the Authorization header for every POST. AppSync authorizes on this
    JWT (the bare x-api-key alone returns Unauthorized — verified live)."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None
        self._token: str = self._mint_token()

    def _mint_token(self) -> str:
        """GET the public access token (a fresh Cognito idToken JWT). No auth, no cookie warm-up."""
        resp = self._sessions[0].get(TOKEN_URL, headers={"Accept": "*/*", "Origin": _SITE,
                                     "Referer": _SITE + "/"}, impersonate=_IMPERSONATE,
                                     timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"token endpoint HTTP {resp.status_code}")
        tok = json.loads(resp.content.decode("utf-8", "replace")).get("idToken")
        if not tok:
            raise RuntimeError("token endpoint returned no idToken")
        return tok

    def _post(self, slot: int, query: str, variables: dict) -> dict:
        """Synchronous AppSync POST on pool session `slot`. Raises on a non-200 OR a GraphQL
        errors array so the breaker sees throttling/auth-loss (never masks a failure)."""
        session = self._sessions[slot]
        body = {"query": query, "variables": variables}
        headers = {**_HEADERS, "Authorization": self._token}
        resp = session.post(ENDPOINT, json=body, headers=headers,
                            impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {ENDPOINT}")
        payload = json.loads(resp.content.decode("utf-8", "replace"))
        if payload.get("errors"):
            raise RuntimeError(f"GraphQL errors: {json.dumps(payload['errors'])[:200]}")
        return payload.get("data") or {}

    def fetch_page(self, url: str, *, page: int = 1, slot: int = 0) -> dict:
        """The governed inventory fetch for one page (runs in a worker thread).

        Handed to governor().wrap_fetch_text: the governor derives the host from `url`, waits on
        the per-host bucket, then runs THIS off the event loop. `slot`/`page` ride as kwargs the
        governor forwards untouched, so each in-flight request POSTs on its own leased, never-shared
        curl_cffi session (thread-safe). `url` is used only for host derivation (the POST always
        targets ENDPOINT)."""
        inp = {**_BASE_INPUT, "pageNumber": page}
        data = self._post(slot, _INVENTORY_QUERY,
                          {"marketConfig": _MARKET_CONFIG, "usedCarsInventoryInputData": inp})
        return data.get("getUsedCarsInventoryData") or {}

    def fetch_dealers(self) -> list[dict]:
        """Fetch the full ES Nissan dealer roster ONCE (Spain-centred, 2000 km). Not governed in a
        pool — a single locator call before the drain begins."""
        data = self._post(0, _DEALERS_QUERY,
                          {"marketConfig": _MARKET_CONFIG, "loc": _DEALER_LOC})
        return data.get("getDealersData") or []

    async def fetch_page_async(self, governed_fetch, url: str, *, page: int) -> dict:
        """Lease a pool slot, fetch `page` THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, page=page, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer (mirrors spoticar_wholesale: ensure platform, bulk-upsert dealer/vehicle, link edge,
# emit delta, all idempotent ON CONFLICT). Multi-axis 0016 classification set.
# ---------------------------------------------------------------------------

NISSAN_PLATFORM_RECIPE = {
    "version": 1,
    "source": "Nissan Intelligent Choice (www.ocasion.nissan.es)",
    "scope": "platform-wholesale (Nissan ES certified-used; Next.js SSR + AWS AppSync GraphQL API)",
    "engine": "curl_cffi+chrome131_impersonate+aws_appsync_graphql(POST)+public_cognito_token",
    "access": ("OPEN-via-fingerprint. A public, unauthenticated token endpoint mints a fresh "
               "Cognito idToken; the AppSync GraphQL authorizes on that JWT (the bare x-api-key "
               "alone returns Unauthorized). No proxy, no browser, no login, €0. No WAF fronting "
               "the API -> is_tier1=FALSE, defense_tier=t0_open."),
    "data_surface": "internal_api",
    "surface_intent": "aws_appsync_graphql_api",
    "token_endpoint": ("GET https://apigateway-eu-prod.nissanpace.com/euw1nisprod/"
                       "public-access-token?brand=NISSAN&dataSourceType=live&market=ES&client=euecomm"),
    "endpoint": "POST https://gq-eu-prod.nissanpace.com/graphql (Authorization: <idToken>)",
    "operation": "GetUsedCarsInventoryData(marketConfig, usedCarsInventoryInputData{pageNumber, queryFilters:[make=Nissan]})",
    "dealer_locator": ("getDealersData(marketConfig, locationDataInput{lat:40.4,long:-3.7,radius:2000,unit:K}) "
                       "-> 180 concesionarios each with postCode + city + location{gpsLatitude,gpsLongitude}; "
                       "fetched ONCE; maps inventory dealerId -> geo"),
    "enumeration": ("usedCarsInventoryInputData.pageNumber=1..104 (15 cars/page; page 104 = 1 "
                    "trailing car, 105+ = 0). metaData.totalCount (1546) + first-empty-page bound "
                    "the run; dedup on vehiclesku."),
    "denominator": "metaData.totalCount (1546)",
    "platform_entity": ("kind=oem_vo_portal, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=FALSE, defense_tier=t0_open, source_group=oem_vo_portal, "
                        "role=platform, family=nissan_intelligent_choice"),
    "dual_membership": ("vehicle.entity_ulid=SELLING DEALER (compraventa); "
                        "platform_listing edge=platform<->vehicle"),
    "field_map": {
        "deep_link": "_PDP_BASE + vehicles[].vehiclesku",
        "listing_ref": "vehicles[].vehiclesku (es_NISSAN_<vin>; stable id + dedup key)",
        "vin": "vehicles[].vin (REAL per-car VIN — gold for cross-source dedup)",
        "make": "vehicles[].make (NISSAN)",
        "model": "vehicles[].modelName",
        "version": "vehicles[].version",
        "year": "vehicles[].registrationYear (fallback modelYear)",
        "km": "vehicles[].mileage ('91587.0' -> float -> int)",
        "price": "vehicles[].discountedPrice (fallback rrpPrice)",
        "fuel": "vehicles[].fuelType (normalized vocabulary)",
        "transmission": "vehicles[].transmission (gearbox: manual/automatico -> Manual/Automático)",
        "dealer": "vehicles[].dealer {dealerId, dealerName}; geo from the getDealersData roster by dealerId",
        "location": ("roster postCode (first 2 digits = INE province, primary) -> ProvinceGeocoder "
                     "lat/lng fallback; roster city -> municipality (INE-resolved)"),
    },
    "caveats": {
        "page_size": "fixed 15 cars/page (server-side; not a request param).",
        "encoding": ("dealer/city text is latin-1 mojibake over the wire (LLANS�, BARBER�); "
                     "repair with s.encode('latin-1').decode('utf-8'). VIN/dealerId/numeric clean."),
        "auth": ("AppSync needs the Cognito idToken in Authorization; the x-api-key alone is "
                 "Unauthorized. Mint a fresh idToken per run from the public token endpoint."),
        "dealer_id_not_province": ("the inventory dealerId is a Nissan internal code, NOT an INE "
                                   "prefix (41020014 sits in 08210/Barcelona); geo comes from the "
                                   "locator roster's postCode/lat-lng, never the id."),
        "no_private_sellers": "OEM certified-used portal — every car belongs to a Nissan concesionario.",
        "siblings_walled": ("Mazda mazdaselected.es TLS-times-out to curl_cffi; Honda "
                            "vehiculosdeocasion.honda.es has no JSON data-layer (HTML buscador). "
                            "Nissan is the only clean data surface of the three."),
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the nissan platform entity + platform_meta exist. Returns the platform
    entity_ulid. kind='oem_vo_portal' (the platform ontology kind), is_tier1=FALSE (no WAF fronts
    the API), multi-axis 0016 classification set explicitly, data_surface='internal_api'."""
    code = nissan_platform_cdp_code()
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
        eulid, code, NISSAN_KIND, NISSAN_LEGAL_NAME, NISSAN_TRADE_NAME, NISSAN_WEBSITE,
        NISSAN_WAF, NISSAN_DEFENSE_TIER, NISSAN_SOURCE_GROUP, NISSAN_ROLE, NISSAN_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, NISSAN_SOURCE_KEY, NISSAN_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'internal_api',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"endpoint": ENDPOINT, "host": host_of(ENDPOINT),
                           "method": "POST", "page_size": PAGE_SIZE,
                           "denominator": "metaData.totalCount",
                           "surface_intent": "aws_appsync_graphql_api",
                           "token_endpoint": host_of(TOKEN_URL),
                           "engine": "curl_cffi/chrome131_impersonate"}),
        NISSAN_FAMILY)
    return eulid


def cdp_code_dealer(d: DealerGeo, prov: str, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    Nissan concesionarios have no bare domain on this surface -> identity = name + location + the
    stable Nissan dealer code (passed via `address` so two distinct POS that happen to share a name
    in one municipality never collapse to one entity)."""
    return cdp_code(province_code=prov, domain=None, name=d.name,
                    municipality_code=muni, address=f"dealer:{d.dealer_id}")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# Default concurrency: pages fetched in parallel per sliding window. gq-eu-prod.nissanpace.com is
# NOT in the governor's JSON_API rate class — it inherits the conservative STEALTH default, the
# safe direction for an OEM API whose true ceiling is unmeasured. The concurrency only needs to
# keep that (slow) bucket saturated; a small window is plenty.
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


def _resolve_dealer_geo(d: DealerGeo, geo: GeoResolver, geocoder: ProvinceGeocoder
                        ) -> tuple[str | None, str | None]:
    """Resolve (province_code, municipality_code) for a roster dealer.

    Primary path: the postCode's first 2 digits == INE province (exact, what the OEM publishes).
    Fallback: the dealer's lat/lng through the ProvinceGeocoder (nearest labeled point) when the
    postcode is missing/out-of-range. Municipality is then resolved from (province, city)."""
    prov: str | None = None
    if d.post_code and len(d.post_code) >= 2 and d.post_code[:2].isdigit():
        cand = d.post_code[:2]
        if "01" <= cand <= "52":
            prov = cand
    if prov is None and d.lat is not None and d.lng is not None:
        cand = geocoder.nearest_province(d.lat, d.lng)
        if cand and cand.isdigit() and "01" <= cand <= "52":
            prov = cand
    if prov is None:
        return (None, None)
    muni = geo.municipality_code(prov, d.city)
    return (prov, muni)


def _parse_window(vehicles_by_page: list[tuple[int, list]], geo: GeoResolver,
                  geocoder: ProvinceGeocoder, dealer_geo: dict[str, DealerGeo],
                  seen_ids: set, harvested_cageable: set, stats: dict) -> list[_CageRow]:
    """Parse + geo-resolve every car across the window IN PAGE ORDER — pure CPU, no SQL.

    The EXACT per-item gate (cross-page dedup on vehiclesku, dealer-parse skip, geo skip, cageable
    truth), lifted out of the DB loop so the SQL phase is purely set-based. The province is taken
    from the pre-fetched dealer roster (postCode -> INE province, lat/lng fallback). `seen_ids` /
    `harvested_cageable` / `stats` are mutated here with deterministic page-order semantics so the
    VAM truth is byte-identical regardless of batching."""
    rows: list[_CageRow] = []
    for _page, vehicles in vehicles_by_page:
        for vnode in vehicles:
            stats["items_seen"] += 1
            v = parse_item_vehicle(vnode)
            if v is None:
                stats["no_dealer_skipped"] += 1
                continue
            # cross-page dedup on vehiclesku (the stable dedup key; the default sort is not stable
            # across a long crawl, so the same car can reappear on a later page).
            item_id = v.listing_ref or v.vin
            if item_id and item_id in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue
            if item_id:
                seen_ids.add(item_id)
            stats["dealer_items"] += 1

            # Geo gate — resolve the province from the dealer roster (postCode primary, lat/lng
            # fallback). A dealer not in the roster, or with no resolvable geo, is skipped without
            # ever touching the DB (no FK risk).
            dg = dealer_geo.get(v.dealer_id)
            if dg is None:
                # the car names a dealer the locator roster did not return — synthesize a minimal
                # geo-less ref so the geocoder fallback still has a name/id; skip if no geo at all.
                dg = DealerGeo(dealer_id=v.dealer_id, name=v.dealer_name, post_code=None,
                               city=None, lat=None, lng=None)
            prov, muni = _resolve_dealer_geo(dg, geo, geocoder)
            if not prov:
                stats["geo_skipped"] += 1
                continue
            dealer_name = dg.name or v.dealer_name
            dg = DealerGeo(dealer_id=dg.dealer_id, name=dealer_name, post_code=dg.post_code,
                           city=dg.city, lat=dg.lat, lng=dg.lng)
            dealer_cdp = cdp_code_dealer(dg, prov, muni)

            if not v.deep_link:
                continue
            harvested_cageable.add((dg.dealer_id, v.deep_link))
            if v.vin:
                stats["vins_captured"] += 1
            rows.append(_CageRow(
                dealer_id=dg.dealer_id, dealer_cdp=dealer_cdp, dealer_name=dealer_name,
                dealer_province=prov, dealer_muni=muni, vehicle=v))
    return rows


async def _ingest_window(conn: asyncpg.Connection, geo: GeoResolver, geocoder: ProvinceGeocoder,
                         dealer_geo: dict[str, DealerGeo], platform_ulid: str,
                         vehicles_by_page: list[tuple[int, list]], seen_ids: set,
                         harvested_cageable: set, stats: dict) -> None:
    """BULK-ingest a whole concurrent page-window in ONE transaction with set-based SQL.

    Mirrors spoticar_wholesale._ingest_window EXACTLY: ONE round-trip per table per window (unnest
    multi-row upserts). The delta/VAM/platform_listing semantics are preserved: same ON CONFLICT
    idempotency, same cageable truth, same NEW-event rule (emitted only for genuinely new
    vehicles). A re-run of an already-harvested window adds 0 rows and 0 events.
    """
    cage = _parse_window(vehicles_by_page, geo, geocoder, dealer_geo, seen_ids,
                         harvested_cageable, stats)
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
                           d_munis, d_refs, NISSAN_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_DEALER_SOURCES, d_cdps, d_refs, NISSAN_SOURCE_KEY)
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
                payload = {"price": v.price, "title": v.title, "platform": NISSAN_TRADE_NAME}
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
    # --limit converts a target car count to a page count (15 cars/page). The tighter of
    # --pages / --limit bounds the run.
    if limit is not None and limit > 0:
        limit_pages = max(1, math.ceil(limit / PAGE_SIZE))
        max_pages = min(max_pages, limit_pages)
    stats = {
        "pages_fetched": 0, "items_seen": 0, "dealer_items": 0,
        "no_dealer_skipped": 0, "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "vins_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "dealers_distinct": 0,
        "concurrency": concurrency, "max_pages": max_pages, "private_skipped": 0,
        "roster_dealers": 0,
    }
    # Harvest-side truth for the VAM: distinct CAGEABLE cars = distinct (dealer_id, deep_link)
    # pairs that survived dealer-parse + geo-resolution. Like-with-like vs db_edges.
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if nissan's breaker is OPEN (a recent ban/throttle still cooling), skip the
    # drain gracefully — the API keeps serving the last snapshot.
    if await is_open(conn, NISSAN_SOURCE_KEY):
        print(f"[nissan_wholesale] breaker OPEN for {NISSAN_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, API still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": NISSAN_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(None)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        geocoder = await ProvinceGeocoder.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = nissan_platform_cdp_code()
        print(f"[nissan_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid}) "
              f"kind={NISSAN_KIND} group={NISSAN_SOURCE_GROUP} tier={NISSAN_DEFENSE_TIER} "
              f"family={NISSAN_FAMILY}")

        # Mint the token + build the fetch pool (token minted in the constructor).
        fetcher = NissanFetcher(pool_size=concurrency)
        governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)
        print(f"[nissan_wholesale] Cognito idToken minted from the public endpoint (len="
              f"{len(fetcher._token)}).")

        # Pre-fetch the dealer roster ONCE (postCode + lat/lng per concesionario).
        roster_raw = await asyncio.to_thread(fetcher.fetch_dealers)
        dealer_geo: dict[str, DealerGeo] = {}
        for node in roster_raw:
            dg = parse_dealer_geo(node)
            if dg is not None:
                dealer_geo[dg.dealer_id] = dg
        stats["roster_dealers"] = len(dealer_geo)
        print(f"[nissan_wholesale] dealer roster: {len(dealer_geo)} concesionarios with geo "
              f"(postCode -> INE province; lat/lng fallback).")
        print(f"[nissan_wholesale] geocoder anchors: {geocoder.size()} labeled points (lat/lng -> province).")
        print(f"[nissan_wholesale] governor paces host {host_of(ENDPOINT)} (per-host token bucket, STEALTH class).")
        print(f"[nissan_wholesale] CONCURRENT drain: window={concurrency} pages in flight. "
              f"Target = {max_pages} pages (~{max_pages * PAGE_SIZE} cars; full ES stock = 1546).")

        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        # CONCURRENT sliding-window drain. Each window fetches up to `concurrency` pages in parallel
        # through the governor (the host bucket paces the aggregate), then the pages are INGESTED
        # sequentially in page order through the single asyncpg connection. A page that errors or
        # comes back empty stops the drain honestly (end of data — page 104 is the true boundary —
        # or a throttle the breaker must catch). totalCount also bounds the run.
        stop = False
        next_page = 1
        while next_page <= max_pages and not stop:
            window = list(range(next_page, min(next_page + concurrency, max_pages + 1)))
            next_page = window[-1] + 1

            results = await asyncio.gather(
                *(fetcher.fetch_page_async(governed_fetch, ENDPOINT, page=p) for p in window),
                return_exceptions=True,
            )

            window_pages: list[tuple[int, list]] = []
            for page, data in zip(window, results):
                if isinstance(data, Exception):
                    fetch_error = str(data)
                    last_http = fetcher.last_status
                    print(f"[nissan_wholesale] page {page} fetch failed ({data}); stopping drain honestly.")
                    stop = True
                    break
                if stats["declared_full"] is None:
                    md = data.get("metaData") or {}
                    stats["declared_full"] = _to_int(md.get("totalCount"))
                vehicles = data.get("vehicles") or []
                if not vehicles:
                    print(f"[nissan_wholesale] page {page}: no vehicles; stopping (data boundary reached).")
                    stop = True
                    break
                window_pages.append((page, vehicles))

            if window_pages:
                await _ingest_window(conn, geo, geocoder, dealer_geo, platform_ulid, window_pages,
                                     seen_ids, harvested_cageable, stats)
                stats["pages_fetched"] += len(window_pages)
                first_p, last_p = window_pages[0][0], window_pages[-1][0]
                print(f"[nissan_wholesale] window pages {first_p}-{last_p}: "
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

        recipe_path = write_recipe(platform_code, NISSAN_PLATFORM_RECIPE)
        print(f"[nissan_wholesale] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths that all measure
        # "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for nissan   (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join (DB read truth)
        #   harvested_cageable = distinct (dealer_id, deep_link) pulled (harvest truth)
        # The declared full count (1546) is reported for honesty but is NOT a quorum path (it
        # measures the WHOLE portal, not necessarily this slice unless the full drain ran).
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

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks nissan, trips the
        # breaker on a ban, and auto-repairs. OK when >=1 page fetched, no fetch error stopped the
        # drain, and the VAM did not refute.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, NISSAN_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, NISSAN_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[nissan_wholesale] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("NISSAN INTELLIGENT CHOICE (OEM-VO PORTAL) WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  group / kind          : oem_vo_portal / oem_vo_portal (tier t0_open, family nissan_intelligent_choice)")
    print(f"  declared full (source): {stats.get('declared_full')}")
    print(f"  dealer roster (geo)   : {stats.get('roster_dealers')} concesionarios")
    print(f"  concurrency (window)  : {stats.get('concurrency')} pages in flight")
    print(f"  target pages          : {stats.get('max_pages')}")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  dealer items          : {stats['dealer_items']}")
    print(f"  no-dealer skipped     : {stats['no_dealer_skipped']}")
    print(f"  private skipped       : {stats['private_skipped']} (OEM portal — none expected)")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page, vehiclesku dedup)")
    print(f"  geo skipped (bad geo) : {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for nissan = {stats.get('db_edges')})")
    print(f"  VINs captured         : {stats['vins_captured']}")
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
        description="Nissan Intelligent Choice OEM-VO portal wholesale harvester "
                    "(concurrent AWS AppSync GraphQL drain)")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"pages to harvest (size={PAGE_SIZE}); default {DEFAULT_MAX_PAGES} (full ES stock)")
    parser.add_argument("--limit", type=int, default=None,
                        help=("optional target car count; converted to a page count (15/page). "
                              "The tighter of --pages / --limit bounds the run."))
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"pages fetched in parallel per sliding window; default "
                              f"{DEFAULT_CONCURRENCY}. gq-eu-prod.nissanpace.com inherits the "
                              f"conservative STEALTH rate class — the governor's per-host bucket "
                              f"is the real limiter."))
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.pages, args.concurrency, args.limit))
    _print_report(stats)


if __name__ == "__main__":
    main()
