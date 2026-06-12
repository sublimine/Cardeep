"""volvo_jlr_suzuki (Volvo Selekt + Jaguar/Land Rover Approved + Suzuki ES) WHOLESALE harvester.

selekt.volvocars.es ('Volvo Selekt'), approved.es.landrover.com + approved.es.jaguar.com
('Jaguar/Land Rover Approved') are the manufacturer-owned certified-used (VO) portals for Volvo
and JLR in Spain. Like spoticar (Stellantis), renew (Renault Group) and toyota_lexus (Toyota
Group) they are NOT car-specialist marketplaces (coches.net/autoscout24/motor.es) nor generalist
classifieds (wallapop): they are OEM-VO PORTALS — a brand owner publishing the certified-used
inventory of its own official dealer network (concesionarios oficiales). They are the
volvo_jlr_suzuki FRONT of the 'oem_vo_portal' source_group, in the new 'volvo_jlr_suzuki_vo'
family, siblings of spoticar/renew/toyota_lexus under the same ONE architecture.

Unlike the single-backend siblings, this front spans TWO distinct vendor platforms behind ONE
connector — proving the OEM-VO group is an ARCHITECTURE, not a single-API special case:

  Volvo Selekt          -> Codeweavers "Digital Retail Store" storefront
                           POST services.codeweavers.net/api/vehicles/search-with-facets (REST).
                           Guest customer token minted from the store ApiKey, sent as
                           x-cw-customertoken. FLAT pagination (Page + ResultsPerPage). ~1,311 cars.
  Jaguar + Land Rover   -> GForces NetDirector AVL <jlr-global-avl> web component
    Approved               POST production-api.search-api.netdirector.auto/api/vehicle-search?uuid=..
                           (GraphQL getCount+getAll). Static Authorization client token, brand by
                           companyHash+manufacturer. FLAT pagination. Jaguar ~35 + Land Rover ~399.

No browser at harvest, no proxy, no cookie warm-up, €0 — just a Chrome TLS fingerprint
(curl_cffi chrome131). Neither search API enforces a bot WAF (both serve to curl_cffi: the
Codeweavers API on the guest token, the AVL API on the client token). The public sites front
behind tier-1 CDNs/WAFs -> is_tier1=TRUE, defense_tier=t1_soft. Each record carries the car AND
its selling official dealer embedded — dealer attribution is per-car, NO PDP fetch needed. This is
an OEM certified-used portal: every car belongs to an official dealer (concesionario oficial);
there are NO private sellers. Verified live 2026-06-13
(docs/architecture/tier1_recipes/oem_volvo_jlr_suzuki_datalayer.md).

This module mirrors pipeline.platform.oem_toyota_lexus_wholesale EXACTLY (the proven multi-surface
OEM-VO template: same dual-membership model, same bulk cage, same governor/health/VAM wiring). It
proves the OEM-VO group flows through the ONE architecture, not a fork of it:

  volvo_jlr_suzuki (the OEM-VO portal) -> entity, kind='oem_vo_portal' (+ platform_meta) [PLATFORM]
  each SELLING official dealer         -> entity, kind='compraventa'   (geo-resolved)
  each CAR                             -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the portal                -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the selling concesionario oficial); platform membership is plural (this
edge). The same physical car can carry BOTH a volvo_jlr_suzuki edge and a coches.net edge without
ever changing its owning dealer.

GEO anchor: BOTH platforms carry an authoritative postcode (Volvo Retailer.Address.Postcode; AVL
location.details.address.postcode). The first 2 digits = INE province (the renew model). Volvo
also carries lat/lng (Retailer.Address.Location) as a geocode fallback; AVL has no lat/lng (postcode
only). The municipality is best-effort from the city literal.

Encoding trap: BOTH surfaces serve human-text fields as latin-1 mojibake over the wire
(autom�tico = "automático", Di�sel = "Diésel", Informaci�n = "Información"). Re-encode every
human-text field: s.encode("latin-1").decode("utf-8"). The numeric fields, stable ids and VIN are clean.

Suzuki: auto.suzuki.es/vehiculos-ocasion is a DIRECTORY of 30 dealer subsites on redsuzuki.es,
each server-rendering its own HTML listing with no central clean JSON surface — a per-dealer HTML
scrape, NOT a clean uncapped data-layer surface. Per "exhaust uncapped surfaces; connect as many
as expose a clean surface" it is recon'd and DEFERRED (its 30 subsites are catalogued in the
recipe for a future long-tail pass), not forced through this OEM-VO connector.

Multi-axis classification (migrations/0016):
  defense_tier = 't1_soft'             (sites front behind tier-1 CDNs/WAFs; the JSON APIs serve to
                                        curl_cffi on a token, no JS challenge)
  source_group = 'oem_vo_portal'       (the group renew opened; this is its volvo/jlr/suzuki front)
  role         = 'platform'
  kind         = 'oem_vo_portal'       (the platform entity's ontology kind, migrations/0005)
  is_tier1     = TRUE                  (tier-1 WAF/CDN fronts the public sites)
  family       = 'volvo_jlr_suzuki_vo' (ties the volvo/jlr/suzuki OEM-VO siblings on the family axis)

PROOF SLICE OR FULL. The connected surfaces declare ~1,745 cars (Volvo ~1,311 + Land Rover ~399 +
Jaguar ~35). The set is small and FLAT, so the FULL drain is in reach in a single run. --pages/
--limit bound the run; --limit converts a target car count to a page count. The declared full
count is recorded for the VAM verdict's slice arithmetic.

Engine: per-surface GET/POST routed THROUGH the per-host governor (the same single choke point
coches.net/spoticar/AS24 use). The synchronous curl_cffi call runs in a worker thread so the event
loop is never blocked, and no host is fetched faster than its bucket.

Run: python -m pipeline.platform.oem_volvo_jlr_suzuki_wholesale --pages 20
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
import re
import unicodedata
import uuid as _uuidlib
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
# volvo_jlr_suzuki platform identity (OEM-VO portal, migrations/0005 + 0016).
# ---------------------------------------------------------------------------
VJS_DOMAIN = "selekt.volvocars.es"   # the front's canonical identity domain (Volvo is the largest surface).
VJS_WEBSITE = "selekt.volvocars.es"
VJS_LEGAL_NAME = "Volvo Selekt + Jaguar/Land Rover Approved (ES)"
VJS_TRADE_NAME = "volvo_jlr_suzuki"
VJS_SOURCE_KEY = "oem_volvo_jlr_suzuki_wholesale"
VJS_WAF = "other"               # tier-1 CDN/WAF fronts the public sites; APIs serve to curl_cffi.
VJS_DEFENSE_TIER = "t1_soft"    # WAF/CDN present but serving to curl_cffi (token-gated, no JS challenge).
VJS_SOURCE_GROUP = "oem_vo_portal"
VJS_ROLE = "platform"
VJS_KIND = "oem_vo_portal"      # the platform ENTITY's ontology kind (NOT 'plataforma').
VJS_FAMILY = "volvo_jlr_suzuki_vo"

_IMPERSONATE = "chrome131"
_TIMEOUT = 45

# --- Volvo Selekt (Codeweavers storefront) ---------------------------------
# Static store identity, extracted ONCE from the index HTML's cw-application-configuration meta
# (base64-then-url-encoded JSON). The guest customer token is minted per run from the ApiKey.
CW_API = "https://services.codeweavers.net"
CW_INIT_PATH = "/api/guest/initialise/proposal"
CW_COUNT_PATH = "/api/vehicles/search/count"
CW_SEARCH_PATH = "/api/vehicles/search-with-facets"
CW_REFERENCE = "9d888d9b-7428-4e3c-9763-621c6311e3f2"   # cw-application-configuration.Reference
CW_API_KEY = "n1WG1lPrjpggL45z6p"                       # .Authentication.ApiKey
CW_ORG_REF = "55388"                                    # CodeweaversReference (init OrganisationIdentifier)
CW_STORE_ORIGIN = "https://selekt.volvocars.es"
CW_STORE_REFERER = "https://selekt.volvocars.es/es-ES/store/used-cars"
CW_PDP_BASE = "https://selekt.volvocars.es/es-ES/store/used-cars"

# --- Jaguar + Land Rover Approved (NetDirector AVL GraphQL) -----------------
AVL_API = ("https://production-api.search-api.netdirector.auto/api/vehicle-search"
           "?uuid=5942c2c0-6601-11eb-b21b-b1ad5fa81f89")
AVL_AUTH = "4d598000-5b04-11eb-ab95-ab946a2c7e0d"       # static Authorization client token (both brands).
# The EXACT field selection the live <jlr-global-avl> component requests (proven 200; a trimmed set
# triggers a GraphQL syntax error). getCount returns the denominator; getAll returns the page.
_AVL_FIELDS = (
    "{ franchiseHash groupHash id mainImage createdAt productionYear "
    "registration { year date number } bodyStyle manufacturer model variant modelCode type "
    "description odometer { value unit } engine { description size } fuel { type typeEnglish } "
    "transmission { type } colour { exterior interior } "
    "price { current base deposit currencyCode vatIncluded conditional list } "
    "location { name hash details { address { name hash city country postcode county line1 line2 "
    "line3 timezone } departments { name hash phoneNumber isDefault } } } "
    "power { maxPs maxHp } custom status offer tax { band } vin "
    "identifiers { stockId dealerId manufacturerId } condition isFranchiseApproved shippingStatus "
    "isExDemo numImages saleLocations { name manufacturerDealerNumber } }"
)

# Page sizes. Both APIs honour large pages and the sets are small + FLAT, so a few pages drain each.
CW_PAGE_SIZE = 100      # Volvo Selekt: 1311 / 100 = 14 pages (page 14 = 11 trailing).
AVL_PAGE_SIZE = 100     # JLR: LR 399 = 4 pages, Jaguar 35 = 1 page.

# Province sentinel '00' = national (same convention as the OEM-VO siblings). geo_province has NO
# '00', so the platform ENTITY stores province_code = NULL; '00' lives only inside the cdp_code
# string (free text, no FK). We never pollute geo_province with it.
PLATFORM_PROVINCE_SENTINEL = "00"

# Full-drain default. PAGE_SIZE 100; 20 pages/surface covers the largest network (Volvo 14) with margin.
DEFAULT_MAX_PAGES = 20


# The vendor platform discriminator for a brand surface.
PLATFORM_CODEWEAVERS = "codeweavers"
PLATFORM_AVL = "netdirector_avl"


@dataclass(frozen=True)
class _BrandSurface:
    """One brand surface: which vendor platform serves it, the brand label, and how to drive it.

    platform   = PLATFORM_CODEWEAVERS | PLATFORM_AVL (picks the fetch + parse path).
    brand      = human brand label (and AVL `manufacturer` value).
    company_hash = AVL companyHash searchParam (None for Codeweavers).
    portal_host  = human label / PDP host."""
    platform: str
    brand: str
    company_hash: str | None
    portal_host: str
    referer: str


_SURFACES = (
    _BrandSurface(PLATFORM_CODEWEAVERS, "Volvo", None,
                  "selekt.volvocars.es", "https://selekt.volvocars.es"),
    _BrandSurface(PLATFORM_AVL, "Land Rover", "1c0df99311526c1ec3af03a70a6da4e2eaa801a2",
                  "approved.es.landrover.com", "https://approved.es.landrover.com"),
    _BrandSurface(PLATFORM_AVL, "Jaguar", "c2b4772858deec1ccea04ea99556cb37b5bd68ab",
                  "approved.es.jaguar.com", "https://approved.es.jaguar.com"),
)


def vjs_platform_cdp_code() -> str:
    """The volvo_jlr_suzuki platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:selekt.volvocars.es'), province segment '00' (national). Mirrors
    tl_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{VJS_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Field helpers (both surfaces: nested objects/arrays + latin-1 mojibake on human text).
# ---------------------------------------------------------------------------


def _fix(s):
    """Repair latin-1 mojibake on human-text fields (autom�tica -> automática, Di�sel -> Diésel,
    Informaci�n -> Información). The wire bytes were UTF-8 mis-decoded as latin-1 upstream;
    re-encode to recover. Numeric fields, stable ids and VIN are clean and never passed here."""
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


def _get(d, *path):
    """Safe nested getter: _get(car, 'Physical', 'Vin')."""
    cur = d
    for k in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


_SLUG_NONWORD = re.compile(r"[^a-z0-9]+")


def _slugify(s) -> str:
    """ASCII-fold + kebab-case a human string for the PDP slug (SEO decoration; the id is the
    load-bearing key)."""
    if not isinstance(s, str):
        return ""
    s = _fix(s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return _SLUG_NONWORD.sub("-", s.lower()).strip("-")


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL responses — field names inspected live 2026-06-13, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class DealerRef:
    """The selling official dealer parsed from a single car's embedded dealer block.

    Both surfaces attach the full dealer per car with an authoritative postcode (first 2 digits =
    INE province, the renew model). Volvo also carries lat/lng (geocode fallback); AVL carries
    none. The stable dealer id is the per-dealer key for cross-source dedup and as the source_ref."""
    dealer_id: str
    name: str | None
    province_code: str | None
    city: str | None
    zip: str | None
    lat: float | None
    lon: float | None


@dataclass
class Vehicle:
    """A car parsed from a single search item (either surface)."""
    deep_link: str
    listing_ref: str           # stable car id — also the dedup key.
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


# --- Volvo Selekt (Codeweavers) parsing ------------------------------------


def _cw_feature(car_vehicle: dict, label: str) -> str | None:
    """Pull a Marketing.Features[Label==label].DisplayValue (localized Spanish) — preferred over the
    English Specification value. Latin-1 repaired."""
    feats = _get(car_vehicle, "Marketing", "Features")
    if isinstance(feats, list):
        for f in feats:
            if isinstance(f, dict) and f.get("Label") == label:
                return _fix(f.get("DisplayValue") or f.get("Value"))
    return None


def _cw_first_image(car_vehicle: dict) -> str | None:
    imgs = car_vehicle.get("Images")
    if isinstance(imgs, list):
        for it in imgs:
            if isinstance(it, dict):
                u = it.get("Url")
                if isinstance(u, str) and u:
                    if u.startswith("//"):
                        return "https:" + u
                    return u if u.startswith("http") else "https://" + u.lstrip("/")
    return None


def _cw_parse_dealer(car: dict) -> DealerRef | None:
    """Parse the SELLING dealer from a Codeweavers Results[].Retailer block."""
    rt = car.get("Retailer") or {}
    dealer_id = rt.get("Reference")
    if not dealer_id:
        return None
    addr = rt.get("Address") or {}
    loc = addr.get("Location") or {}
    zip_raw = addr.get("Postcode")
    zip_s = str(zip_raw).strip() if zip_raw not in (None, "") else None
    return DealerRef(
        dealer_id=str(dealer_id),
        name=_fix(rt.get("Name")),
        province_code=None,                       # filled in _parse_window (zip first, then geo).
        city=_fix(addr.get("TownCity")),
        zip=zip_s,
        lat=_to_float(loc.get("Latitude")),
        lon=_to_float(loc.get("Longitude")),
    )


def _cw_parse_vehicle(car: dict, surface: _BrandSurface) -> Vehicle:
    """Parse the car from a Codeweavers Results[].Vehicle block (REAL field map).

    IDENTITY TRAP (verified live 2026-06-13): the Codeweavers search endpoint SAMPLES + RESHUFFLES
    its result set per request — two full crawls share 0 common Vehicle.Reference (an ephemeral
    per-listing token) but ~95% common VIN / ExternalVehicleId. So Reference is NOT a durable car
    identity and MUST NOT key the deep_link/dedup (it would make every run add "new" cars). The
    durable key is the STOCK identity: ExternalVehicleId (MDX-xxxx, always present) preferred,
    falling back to the VIN. Keying the deep_link on it makes the connector idempotent across runs
    (same car -> same deep_link -> ON CONFLICT DO NOTHING)."""
    v = car.get("Vehicle") or {}
    spec = v.get("Specification") or {}
    phys = v.get("Physical") or {}

    price = _to_float(phys.get("OnTheRoadPrice"))
    if price is None:
        price = _to_float(_get(phys, "CostBreakdown", "BasePrice"))
    if price is not None and price <= 0:
        price = None

    year = _to_int(spec.get("ModelYear"))
    if year is not None and not (1900 <= year <= 2100):
        year = None

    km = _to_int(phys.get("Mileage"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    make = _fix(spec.get("Manufacturer")) or surface.brand
    model = _fix(spec.get("Model"))
    version = _fix(spec.get("Variant"))
    title = " ".join(p for p in (make, model, version) if p) or None

    vin = phys.get("Vin")
    ext_id = phys.get("ExternalVehicleId")

    # The DURABLE stock identity = the dedup key. ExternalVehicleId (MDX-xxxx) is stable across the
    # API's per-request reshuffle; VIN is the fallback. The rotating Vehicle.Reference is NEVER the key.
    stock_key = str(ext_id or vin or "").strip()
    listing_ref = stock_key

    # fuel/transmission: prefer the Spanish Marketing DisplayValue; fall back to the English spec.
    fuel = _cw_feature(v, "Fuel") or _fix(spec.get("FuelType"))
    transmission = _cw_feature(v, "Transmission") or _fix(spec.get("Transmission"))

    # deep_link keyed PURELY on the DURABLE stock id (the ON CONFLICT (entity_ulid, deep_link) key
    # MUST be byte-stable across runs). The rotating per-session Reference is deliberately NOT in the
    # path — it would re-break idempotency and it does not durably resolve a PDP anyway.
    deep_link = ""
    if stock_key:
        slug = "-".join(p for p in (_slugify(make), _slugify(model), str(year or "")) if p)
        deep_link = (f"{CW_PDP_BASE}/{slug}/{stock_key}" if slug
                     else f"{CW_PDP_BASE}/{stock_key}")

    return Vehicle(
        deep_link=deep_link, listing_ref=listing_ref, title=title, make=make, model=model,
        year=year, km=km, price=price, fuel=fuel, transmission=transmission,
        photo_url=_cw_first_image(v), vin=str(vin) if vin else None)


# --- Jaguar + Land Rover Approved (NetDirector AVL) parsing ------------------


def _avl_first_image(car: dict) -> str | None:
    u = car.get("mainImage")
    if isinstance(u, str) and u:
        if u.startswith("//"):
            return "https:" + u
        return u if u.startswith("http") else "https://" + u.lstrip("/")
    return None


def _avl_parse_dealer(car: dict) -> DealerRef | None:
    """Parse the SELLING dealer from an AVL location block. No lat/lng on this surface."""
    loc = car.get("location") or {}
    dealer_id = loc.get("hash")
    addr = _get(loc, "details", "address") or {}
    if not dealer_id:
        dealer_id = addr.get("hash")
    if not dealer_id:
        return None
    zip_raw = addr.get("postcode")
    zip_s = str(zip_raw).strip() if zip_raw not in (None, "") else None
    return DealerRef(
        dealer_id=str(dealer_id),
        name=_fix(loc.get("name") or addr.get("name")),
        province_code=None,                       # filled in _parse_window (zip only here).
        city=_fix(addr.get("city")),
        zip=zip_s,
        lat=None,
        lon=None,
    )


def _avl_parse_vehicle(car: dict, surface: _BrandSurface) -> Vehicle:
    """Parse the car from an AVL data.getAll[] item (REAL field map)."""
    price = _to_float(_get(car, "price", "current"))
    if price is None:
        price = _to_float(_get(car, "price", "base"))
    if price is not None and price <= 0:
        price = None

    year = _to_int(car.get("productionYear"))
    if year is None:
        year = _to_int(_get(car, "registration", "year"))
    if year is not None and not (1900 <= year <= 2100):
        year = None

    km = _to_int(_get(car, "odometer", "value"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    make = _fix(car.get("manufacturer")) or surface.brand
    model = _fix(car.get("model"))
    version = _fix(car.get("variant"))
    title = " ".join(p for p in (make, model, version) if p) or None

    listing_ref = str(car.get("id") or _get(car, "identifiers", "stockId") or "")

    fuel = _fix(_get(car, "fuel", "type"))
    transmission = _fix(_get(car, "transmission", "type"))

    # VIN: prefer the explicit vin; registration.number is the same VIN on this surface.
    vin = car.get("vin") or _get(car, "registration", "number")

    deep_link = f"{surface.referer}/used/{listing_ref}" if listing_ref else ""

    return Vehicle(
        deep_link=deep_link, listing_ref=listing_ref, title=title, make=make, model=model,
        year=year, km=km, price=price, fuel=fuel, transmission=transmission,
        photo_url=_avl_first_image(car), vin=str(vin) if vin else None)


def parse_item_dealer(car: dict, surface: _BrandSurface) -> DealerRef | None:
    """Dispatch the dealer parse on the surface's vendor platform."""
    if surface.platform == PLATFORM_CODEWEAVERS:
        return _cw_parse_dealer(car)
    return _avl_parse_dealer(car)


def parse_item_vehicle(car: dict, surface: _BrandSurface) -> Vehicle:
    """Dispatch the vehicle parse on the surface's vendor platform."""
    if surface.platform == PLATFORM_CODEWEAVERS:
        return _cw_parse_vehicle(car, surface)
    return _avl_parse_vehicle(car, surface)


# ---------------------------------------------------------------------------
# Fetch: per-surface GET/POST routed THROUGH the governor (same per-host choke point as the siblings).
# ---------------------------------------------------------------------------


class VJSFetcher:
    """A POOL of fingerprint-coherent curl_cffi sessions for BOTH vendor APIs.

    Same concurrency-vs-coherence model as TLFetcher / SpoticarFetcher: a single curl_cffi Session
    is NOT safe to call from several threads at once, and the governor runs each fetch in its own
    worker thread (asyncio.to_thread). The fix is a bounded POOL — one Session per concurrency slot,
    each its own Chrome fingerprint + cookie jar. The governor's per-host bucket bounds the AGGREGATE
    rate across every session, so the pool widens parallelism WITHOUT out-pacing the host.

    The Codeweavers guest customer token is minted once per run (mint_cw_token) and reused by every
    slot; it is per-session-agnostic (a bearer-style header, not a session cookie)."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None
        self.cw_token: str | None = None

    def mint_cw_token(self) -> str:
        """Mint the Volvo Selekt guest customer token from the store ApiKey (synchronous; called
        once before the Codeweavers drain). Raises on a non-200 so the breaker sees the failure."""
        session = self._sessions[0]
        resp = session.post(
            CW_API + CW_INIT_PATH,
            json={"ApiKey": CW_API_KEY,
                  "OrganisationIdentifier": {"Type": "CodeweaversReference", "Value": CW_ORG_REF}},
            headers=self._cw_headers(), impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} minting Codeweavers token")
        tok = (resp.json() or {}).get("UserToken")
        if not tok:
            raise RuntimeError("Codeweavers init returned no UserToken")
        self.cw_token = tok
        return tok

    @staticmethod
    def _cw_headers(token: str | None = None) -> dict:
        h = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Accept-Language": "es-ES,es;q=0.9",
            "Origin": CW_STORE_ORIGIN,
            "Referer": CW_STORE_ORIGIN + "/",
            "x-cw-digitalretailstorereference": CW_REFERENCE,
            "x-cw-applicationname": "Storefront",
            "x-cw-applicationinstanceid": str(_uuidlib.uuid4()),
            "x-cw-anti-cache": str(_uuidlib.uuid4()),
            "x-cw-accept-language": "es-es",
            "x-cw-referer": CW_STORE_REFERER,
        }
        if token:
            h["x-cw-customertoken"] = token
        return h

    @staticmethod
    def _avl_headers(surface: _BrandSurface) -> dict:
        return {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Accept-Language": "es-ES,es;q=0.9",
            "Authorization": AVL_AUTH,
            "Origin": surface.referer,
            "Referer": surface.referer + "/",
        }

    def fetch_page(self, url: str, *, surface_idx: int = 0, page: int = 1,
                   page_size: int = 100, slot: int = 0) -> dict:
        """The synchronous GET/POST on pool session `slot` (runs in a worker thread).

        Handed to governor().wrap_fetch_text: the governor derives the host from `url`, waits on the
        per-host bucket, then runs THIS off the event loop. `surface_idx`/`page`/`slot` ride as kwargs
        the governor forwards untouched, so each in-flight request runs on its own leased, never-shared
        curl_cffi session (thread-safe). Raises on a non-200 (or GraphQL errors) so the breaker sees
        throttling and never masks a challenge/empty body."""
        surface = _SURFACES[surface_idx]
        session = self._sessions[slot]
        if surface.platform == PLATFORM_CODEWEAVERS:
            body = {"Filters": {"Vehicle": {}}, "ResultsPerPage": page_size, "Page": page}
            resp = session.post(url, json=body, headers=self._cw_headers(self.cw_token),
                                impersonate=_IMPERSONATE, timeout=_TIMEOUT)
            self.last_status = resp.status_code
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code} on Codeweavers (page {page})")
            return json.loads(resp.content.decode("utf-8", "replace"))

        # NetDirector AVL GraphQL.
        sp = (f'{{companyHash: ["{surface.company_hash}"], manufacturer: "{surface.brand}", '
              f'condition: "used"}}')
        query = (f'query {{ getCount (searchParams: {sp}) '
                 f'getAll (searchParams: {sp}, pagination: {{currentPage: {page}, '
                 f'pageSize: {page_size}}}, sortParams: [{{fieldName: currentPrice, '
                 f'direction: asc}}]) {_AVL_FIELDS} }}')
        resp = session.post(url, json={"query": query}, headers=self._avl_headers(surface),
                            impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on AVL {surface.brand} (page {page})")
        doc = json.loads(resp.content.decode("utf-8", "replace"))
        if doc.get("errors"):
            raise RuntimeError(f"AVL GraphQL errors {surface.brand} (page {page}): {doc['errors']}")
        return doc

    async def fetch_page_async(self, governed_fetch, url: str, *, surface_idx: int, page: int,
                               page_size: int) -> dict:
        """Lease a pool slot, fetch `page` THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, surface_idx=surface_idx, page=page,
                                        page_size=page_size, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer (mirrors oem_toyota_lexus_wholesale: ensure platform, bulk-upsert dealer/vehicle, link
# edge, emit delta, all idempotent ON CONFLICT). Multi-axis 0016 classification set.
# ---------------------------------------------------------------------------

VJS_PLATFORM_RECIPE = {
    "version": 1,
    "source": "volvo_jlr_suzuki (selekt.volvocars.es + approved.es.landrover.com + approved.es.jaguar.com)",
    "scope": ("platform-wholesale (Volvo Selekt + Jaguar/Land Rover Approved ES certified-used; "
              "TWO vendor platforms — Codeweavers REST + NetDirector AVL GraphQL — one connector)"),
    "engine": "curl_cffi+chrome131_impersonate+two_internal_json_apis(POST)",
    "access": ("OPEN-via-fingerprint+token. Volvo Selekt: Codeweavers storefront; guest customer "
               "token minted from the store ApiKey, sent as x-cw-customertoken; no bot WAF. JLR: "
               "NetDirector AVL search-api; static Authorization client token + uuid; no bot WAF. "
               "No proxy, no browser, no cookie warm-up, €0. Public sites front behind tier-1 "
               "CDNs/WAFs -> is_tier1=TRUE; the JSON APIs serve to curl_cffi -> defense_tier=t1_soft."),
    "data_surface": "internal_api",
    "surface_intent": "two_internal_json_apis",
    "endpoint": ("VOLVO: POST https://services.codeweavers.net/api/vehicles/search-with-facets ; "
                 "JLR: POST https://production-api.search-api.netdirector.auto/api/vehicle-search?uuid=.."),
    "request": {
        "volvo": ("guest token via POST /api/guest/initialise/proposal "
                  "{ApiKey, OrganisationIdentifier{CodeweaversReference 55388}}; then search body "
                  "{Filters:{Vehicle:{}}, ResultsPerPage:100, Page:N}; headers "
                  "x-cw-customertoken + x-cw-digitalretailstorereference + x-cw-applicationname Storefront"),
        "jlr": ("GraphQL {query: getCount(SP) getAll(SP, pagination{currentPage,pageSize}, sortParams) "
                "FIELDS}; SP={companyHash:[<hash>], manufacturer:<brand>, condition:\"used\"}; header "
                "Authorization: <static client token>. LR hash 1c0df9..a2 / Jaguar hash c2b477..ab"),
    },
    "enumeration": ("PER SURFACE: Volvo Page=1..14 @100 (TotalPages/TotalResults bound it); "
                    "Land Rover/Jaguar currentPage=1.. @100 (getCount bounds it). dedup on the "
                    "stable car id (Volvo Vehicle.Reference / AVL id). Stop on empty page."),
    "denominator": ("Volvo: count.TotalResults (==search.TotalResults) ; "
                    "JLR: data.getCount (per brand). Front total = Σ surfaces (~1745)."),
    "platform_entity": ("kind=oem_vo_portal, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=TRUE, defense_tier=t1_soft, source_group=oem_vo_portal, role=platform, "
                        "family=volvo_jlr_suzuki_vo"),
    "dual_membership": ("vehicle.entity_ulid=SELLING DEALER (compraventa); "
                        "platform_listing edge=platform<->vehicle"),
    "field_map": {
        "volvo": {
            "listing_ref": "Results[].Vehicle.Reference (UUID; stable id + dedup key)",
            "vin": "Results[].Vehicle.Physical.Vin",
            "make": "Vehicle.Specification.Manufacturer",
            "model": "Vehicle.Specification.Model",
            "version": "Vehicle.Specification.Variant",
            "year": "Vehicle.Specification.ModelYear",
            "km": "Vehicle.Physical.Mileage",
            "price": "Vehicle.Physical.OnTheRoadPrice (EUR)",
            "fuel": "Vehicle.Marketing.Features[Label=Fuel].DisplayValue (Spanish; fallback Specification.FuelType)",
            "transmission": "Vehicle.Marketing.Features[Label=Transmission].DisplayValue (Spanish)",
            "photo": "Vehicle.Images[0].Url",
            "dealer": "Results[].Retailer {Reference, Name, Address{Postcode, TownCity, Location{Latitude,Longitude}}}",
            "location": "Retailer.Address.Postcode[:2]=INE province; Location lat/lng = geocode fallback; TownCity=municipality",
            "deep_link": "constructed selekt.volvocars.es/es-ES/store/used-cars/<slug>/<Reference>",
        },
        "jlr": {
            "listing_ref": "data.getAll[].id (== identifiers.stockId; stable id + dedup key)",
            "vin": "data.getAll[].vin (== registration.number)",
            "make": "getAll[].manufacturer",
            "model": "getAll[].model",
            "version": "getAll[].variant",
            "year": "getAll[].productionYear (fallback registration.year)",
            "km": "getAll[].odometer.value (unit km)",
            "price": "getAll[].price.current (EUR; fallback .base)",
            "fuel": "getAll[].fuel.type (Spanish)",
            "transmission": "getAll[].transmission.type (Spanish)",
            "photo": "getAll[].mainImage (protocol-relative -> https)",
            "dealer": "getAll[].location {hash, name, details.address{postcode, city, county, line1}}",
            "location": "location.details.address.postcode[:2]=INE province (no lat/lng on this surface); city=municipality",
            "deep_link": "constructed approved.es.<brand>.com/used/<id>",
        },
    },
    "caveats": {
        "two_platforms": "ONE connector, TWO vendor APIs (Codeweavers REST + NetDirector AVL GraphQL).",
        "page_keys": "Volvo uses Page+ResultsPerPage (NOT PageSize); AVL uses pagination{currentPage,pageSize}.",
        "encoding": ("BOTH surfaces serve human text as latin-1 mojibake (autom�tica, Di�sel, "
                     "Informaci�n); repair with s.encode('latin-1').decode('utf-8'). ids/vin/numeric clean."),
        "geo": ("BOTH carry an authoritative postcode (province = first 2 digits). Volvo also has "
                "lat/lng (geocode fallback); AVL has postcode only."),
        "no_private_sellers": "OEM certified-used portals — every car belongs to an official dealer.",
        "suzuki_deferred": ("auto.suzuki.es is a directory of 30 redsuzuki.es dealer subsites with "
                            "per-dealer server-rendered HTML — NOT a clean uncapped surface; DEFERRED."),
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the volvo_jlr_suzuki platform entity + platform_meta exist. Returns the
    platform entity_ulid. kind='oem_vo_portal' (the platform ontology kind), is_tier1=TRUE (tier-1
    CDN/WAF fronts the public sites), multi-axis 0016 classification set explicitly,
    data_surface='internal_api'."""
    code = vjs_platform_cdp_code()
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
        eulid, code, VJS_KIND, VJS_LEGAL_NAME, VJS_TRADE_NAME, VJS_WEBSITE,
        VJS_WAF, VJS_DEFENSE_TIER, VJS_SOURCE_GROUP, VJS_ROLE, VJS_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, VJS_SOURCE_KEY, VJS_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'internal_api',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"volvo_endpoint": CW_API + CW_SEARCH_PATH,
                           "jlr_endpoint": AVL_API,
                           "method": "POST",
                           "page_size": {"volvo": CW_PAGE_SIZE, "jlr": AVL_PAGE_SIZE},
                           "denominator": "count.TotalResults + getCount",
                           "brands": [s.brand for s in _SURFACES],
                           "platforms": sorted({s.platform for s in _SURFACES}),
                           "surface_intent": "two_internal_json_apis",
                           "engine": "curl_cffi/chrome131_impersonate"}),
        VJS_FAMILY)
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    These dealers have no bare-domain identity on these surfaces -> identity = name + location + the
    stable dealer id (passed via `address` so two distinct dealers that happen to share a name in one
    municipality never collapse to one entity)."""
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni, address=f"dealer:{d.dealer_id}")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# Default concurrency: pages fetched in parallel per sliding window. Neither vendor host is in the
# governor's JSON_API rate class — they inherit the conservative STEALTH default, the safe direction
# for unmeasured token-gated hosts. The concurrency only needs to keep that (slow) bucket saturated.
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
    renew model). FALLBACK: geocode from lat/lon (nearest labeled point) when the zip is
    missing/malformed (Volvo only; AVL has no lat/lon). Returns a validated '01'..'52' code or None."""
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


def _items_of(data: dict, surface: _BrandSurface) -> tuple[list, int | None]:
    """Extract (items, declared_total) from a raw page response per vendor platform."""
    if surface.platform == PLATFORM_CODEWEAVERS:
        items = data.get("Results") or []
        total = _to_int(data.get("TotalResults"))
        return items, total
    inner = data.get("data") or {}
    items = inner.get("getAll") or []
    total = _to_int(inner.get("getCount"))
    return items, total


def _parse_window(items_by_page: list[tuple[int, int, list]], geo: GeoResolver,
                  geocoder: ProvinceGeocoder, seen_ids: set, harvested_cageable: set,
                  stats: dict) -> list[_CageRow]:
    """Parse + geo-resolve every car across the window IN ORDER — pure CPU, no SQL.

    The EXACT per-item gate (cross-page dedup on the stable id, dealer-parse skip, geo skip, cageable
    truth), lifted out of the DB loop so the SQL phase is purely set-based. The province is resolved
    zip-first then geocode-fallback. `seen_ids` / `harvested_cageable` / `stats` are mutated here with
    deterministic order semantics so the VAM truth is byte-identical regardless of batching. Each
    tuple is (page, surface_idx, items); surface_idx picks the right parse + PDP surface."""
    rows: list[_CageRow] = []
    for _page, surface_idx, items in items_by_page:
        surface = _SURFACES[surface_idx]
        for car in items:
            if not isinstance(car, dict):
                continue
            stats["items_seen"] += 1

            v = parse_item_vehicle(car, surface)
            # cross-page dedup on the stable car id (default sort is not stable across a long crawl,
            # so the same car can reappear on a later page).
            item_id = v.listing_ref
            if item_id and item_id in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue
            if item_id:
                seen_ids.add(item_id)

            d = parse_item_dealer(car, surface)
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
                         platform_ulid: str, items_by_page: list[tuple[int, int, list]],
                         seen_ids: set, harvested_cageable: set, stats: dict) -> None:
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
                           d_munis, d_refs, VJS_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_DEALER_SOURCES, d_cdps, d_refs, VJS_SOURCE_KEY)
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
                payload = {"price": v.price, "title": v.title, "platform": VJS_TRADE_NAME}
                if v.vin:
                    payload["vin"] = v.vin
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities,
                               ev_payloads)
            stats["new_events"] += len(confirmed_new)


def _endpoint_for(surface: _BrandSurface) -> str:
    return CW_API + CW_SEARCH_PATH if surface.platform == PLATFORM_CODEWEAVERS else AVL_API


def _page_size_for(surface: _BrandSurface) -> int:
    return CW_PAGE_SIZE if surface.platform == PLATFORM_CODEWEAVERS else AVL_PAGE_SIZE


async def _drain_surface(conn, geo, geocoder, platform_ulid, fetcher, governed_fetch,
                         surface_idx: int, max_pages: int, concurrency: int,
                         seen_ids: set, harvested_cageable: set, stats: dict
                         ) -> tuple[str | None, int | None]:
    """Drain ONE brand surface by walking its page cursor in concurrent windows.

    Returns (fetch_error, last_http). The page cursor is per-surface; the declared total (read from
    the first page) + emptiness bound the run. Pages are fetched in parallel through the governor (the
    host bucket paces the aggregate) then ingested sequentially in page order."""
    surface = _SURFACES[surface_idx]
    endpoint = _endpoint_for(surface)
    page_size = _page_size_for(surface)
    fetch_error: str | None = None
    last_http: int | None = None
    declared_total: int | None = None
    stop = False
    next_page = 1  # both APIs are 1-based page indices.
    print(f"[oem_volvo_jlr_suzuki] === draining {surface.brand} "
          f"({surface.portal_host}, {surface.platform}) ===")
    while next_page <= max_pages and not stop:
        window = list(range(next_page, min(next_page + concurrency, max_pages + 1)))
        next_page = window[-1] + 1
        # bound by declared total once known (1-based pages: page p covers rows (p-1)*size..)
        if declared_total is not None:
            window = [p for p in window if (p - 1) * page_size < declared_total]
            if not window:
                break

        results = await asyncio.gather(
            *(fetcher.fetch_page_async(governed_fetch, endpoint, surface_idx=surface_idx,
                                       page=p, page_size=page_size) for p in window),
            return_exceptions=True,
        )

        window_pages: list[tuple[int, int, list]] = []
        for page, data in zip(window, results):
            if isinstance(data, Exception):
                fetch_error = str(data)
                last_http = fetcher.last_status
                print(f"[oem_volvo_jlr_suzuki] {surface.brand} page {page} fetch failed ({data}); "
                      f"stopping this surface honestly.")
                stop = True
                break
            items, total = _items_of(data, surface)
            if declared_total is None and total is not None:
                declared_total = total
                stats["declared_per_brand"][surface.brand] = declared_total
                stats["declared_full"] = (stats["declared_full"] or 0) + declared_total
            if not items:
                print(f"[oem_volvo_jlr_suzuki] {surface.brand} page {page}: no results; "
                      f"stopping (data boundary reached).")
                stop = True
                break
            window_pages.append((page, surface_idx, items))

        if window_pages:
            await _ingest_window(conn, geo, geocoder, platform_ulid, window_pages, seen_ids,
                                 harvested_cageable, stats)
            stats["pages_fetched"] += len(window_pages)
            first_p, last_p = window_pages[0][0], window_pages[-1][0]
            print(f"[oem_volvo_jlr_suzuki] {surface.brand} pages {first_p}-{last_p}: "
                  f"hits={sum(len(it) for _, _, it in window_pages)} "
                  f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                  f"edges={stats['edges_created']} dealers_seen={len(harvested_cageable)}")
    return fetch_error, last_http


async def harvest(max_pages: int = DEFAULT_MAX_PAGES,
                  concurrency: int = DEFAULT_CONCURRENCY,
                  limit: int | None = None) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    # --limit converts a target car count to a page count (PAGE_SIZE cars/page). The tighter of
    # --pages / --limit bounds the run (applied PER SURFACE, using the larger page size for the cap).
    if limit is not None and limit > 0:
        limit_pages = max(1, math.ceil(limit / min(CW_PAGE_SIZE, AVL_PAGE_SIZE)))
        max_pages = min(max_pages, limit_pages)
    fetcher = VJSFetcher(pool_size=concurrency)
    stats = {
        "pages_fetched": 0, "items_seen": 0, "dealer_items": 0,
        "no_dealer_skipped": 0, "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "vins_captured": 0,
        "declared_full": None, "declared_per_brand": {}, "dup_ids_collapsed": 0,
        "dealers_distinct": 0, "concurrency": concurrency, "max_pages": max_pages,
        "private_skipped": 0,
    }
    # Harvest-side truth for the VAM: distinct CAGEABLE cars = distinct (dealer_id, deep_link)
    # pairs that survived dealer-parse + geo-resolution. Like-with-like vs db_edges.
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if the breaker is OPEN (a recent ban/throttle still cooling), skip the drain
    # gracefully — the APIs keep serving the last snapshot.
    if await is_open(conn, VJS_SOURCE_KEY):
        print(f"[oem_volvo_jlr_suzuki] breaker OPEN for {VJS_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, APIs still serve last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": VJS_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        geocoder = await ProvinceGeocoder.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = vjs_platform_cdp_code()
        print(f"[oem_volvo_jlr_suzuki] platform entity ready: {platform_code} (ulid={platform_ulid}) "
              f"kind={VJS_KIND} group={VJS_SOURCE_GROUP} tier={VJS_DEFENSE_TIER} family={VJS_FAMILY}")
        print(f"[oem_volvo_jlr_suzuki] geocoder anchors: {geocoder.size()} labeled points (lat/lon -> province).")
        print(f"[oem_volvo_jlr_suzuki] CONCURRENT drain: window={concurrency} pages in flight. "
              f"Target = {max_pages} pages/surface x {len(_SURFACES)} surfaces; full ES stock ~1745.")

        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        # Drain each brand surface in turn (each its own page cursor + declared total). The
        # Codeweavers guest token is minted lazily just before the first Codeweavers surface.
        for surface_idx, surface in enumerate(_SURFACES):
            if surface.platform == PLATFORM_CODEWEAVERS and fetcher.cw_token is None:
                try:
                    fetcher.mint_cw_token()
                    print(f"[oem_volvo_jlr_suzuki] Codeweavers guest token minted "
                          f"(store {CW_REFERENCE}).")
                except Exception as exc:  # noqa: BLE001 — a mint failure stops the drain honestly.
                    fetch_error = f"codeweavers token mint failed: {exc}"
                    last_http = fetcher.last_status
                    print(f"[oem_volvo_jlr_suzuki] {fetch_error}; skipping Volvo surface.")
                    continue
            err, http = await _drain_surface(
                conn, geo, geocoder, platform_ulid, fetcher, governed_fetch, surface_idx,
                max_pages, concurrency, seen_ids, harvested_cageable, stats)
            if err is not None:
                fetch_error = err
                last_http = http
                # a hard fetch error on one surface stops the whole drain honestly (breaker must see it).
                break

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, VJS_PLATFORM_RECIPE)
        print(f"[oem_volvo_jlr_suzuki] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths that all measure
        # "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for volvo_jlr_suzuki  (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join          (DB read truth)
        #   harvested_cageable = distinct (dealer_id, deep_link) pulled        (harvest truth)
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

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks volvo_jlr_suzuki, trips
        # the breaker on a ban, and auto-repairs. OK when >=1 page fetched, no fetch error stopped the
        # drain, and the VAM did not refute.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, VJS_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, VJS_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[oem_volvo_jlr_suzuki] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("VOLVO+JLR+SUZUKI (OEM-VO PORTAL) WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  group / kind          : oem_vo_portal / oem_vo_portal (tier t1_soft, family volvo_jlr_suzuki_vo)")
    print(f"  declared full (source): {stats.get('declared_full')} {stats.get('declared_per_brand')}")
    print(f"  concurrency (window)  : {stats.get('concurrency')} pages in flight")
    print(f"  target pages/surface  : {stats.get('max_pages')}")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  dealer items          : {stats['dealer_items']}")
    print(f"  no-dealer skipped     : {stats['no_dealer_skipped']}")
    print(f"  private skipped       : {stats['private_skipped']} (OEM portal — none expected)")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page, id dedup)")
    print(f"  geo skipped (bad geo) : {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for volvo_jlr_suzuki = {stats.get('db_edges')})")
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
        description="volvo_jlr_suzuki OEM-VO portal wholesale harvester (two-platform JSON drain)")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"pages PER SURFACE to harvest (size 100); default {DEFAULT_MAX_PAGES} (full ES stock)")
    parser.add_argument("--limit", type=int, default=None,
                        help=("optional target car count PER SURFACE; converted to a page count "
                              "(100/page). The tighter of --pages / --limit bounds the run."))
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"pages fetched in parallel per sliding window; default "
                              f"{DEFAULT_CONCURRENCY}. The vendor hosts inherit the conservative "
                              f"STEALTH rate class — the governor's per-host bucket is the real limiter."))
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.pages, args.concurrency, args.limit))
    _print_report(stats)


if __name__ == "__main__":
    main()
