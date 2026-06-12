"""toyota_lexus (Toyota Plus + Lexus Select ES certified-used) WHOLESALE harvester — end to end.

www.toyota.es ('Toyota Ocasión' / Toyota Plus / Toyota Approved Used) and www.lexusauto.es
('Lexus Select' seminuevos certificados) are the two manufacturer-owned certified-used portals
for the Toyota Group in Spain. Like spoticar (Stellantis) and renew (Renault Group) they are NOT
car-specialist marketplaces (coches.net/autoscout24/motor.es) nor generalist classifieds
(wallapop): they are OEM-VO PORTALS — a brand owner publishing the certified-used inventory of
its own official dealer network (concesionarios oficiales). They are the THIRD member of the
'oem_vo_portal' source_group, in the new 'toyota_lexus_vo' family, the sibling of spoticar/renew
under the same ONE architecture.

Both SPAs embed the SAME backend: the Toyota-Europe 'USC' (Used Stock Cars) Web Components
service. They call ONE internal JSON API — POST /v1/api/usedcars/results/es/es?brand={brand} —
differing only by the ?brand= query param (toyota vs lexus) and the brand still served from the
SAME ES distributorCode (9424M). No browser, no proxy, no cookie warm-up, no auth: the API sits
behind AWS CloudFront with NO bot WAF and serves HTTP 200 application/json even to plain curl
(defense_tier=t0_open). We drive it with curl_cffi chrome131 only for fleet engine-coherence.

The response carries {totalResultCount, totalPageCount, results:[{...}]} — the per-car page size
is the body's `resultCount`, and `offset` is a ROW cursor; walk offset=0..totalResultCount, FLAT
(no relevance cap, no depth wall). Each `results[]` doc carries the car AND its selling official
dealer via the embedded `dealer{}` object (id, name, full address+zip, lat/lon, website, phone) —
dealer attribution is per-car, NO PDP fetch needed. This is an OEM certified-used portal: every
car belongs to a Toyota/Lexus official dealer; there are NO private sellers. Verified live
2026-06-13 (docs/architecture/tier1_recipes/oem_toyota_lexus_datalayer.md).

This module mirrors pipeline.platform.spoticar_wholesale EXACTLY (the proven OEM-VO template:
same dual-membership model, same bulk cage, same governor/health/VAM wiring). It proves the
OEM-VO group flows through the ONE architecture, not a fork of it:

  toyota_lexus (the OEM-VO portal) -> entity, kind='oem_vo_portal' (+ platform_meta)  [PLATFORM]
  each SELLING DEALER              -> entity, kind='compraventa'   (geo-resolved)
  each CAR                         -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the portal            -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the selling dealer); platform membership is plural (this edge). The same
physical car can carry BOTH a toyota_lexus edge and a coches.net edge without ever changing its
owning dealer.

GEO anchor difference vs spoticar: spoticar had no postal code (geocode from lat/lng). The USC
`dealer.address.zip` IS present and authoritative — the first 2 digits are the INE province (the
renew model). We prefer zip->province; the embedded `geoLocation.lat/lon` is the fallback via the
ProvinceGeocoder (nearest labeled point) when the zip is missing/malformed.

Encoding trap: the API serves brand/dealer/city/colour text as latin-1 mojibake over the wire
(autom�tico = "automático", LA CORU�A = "LA CORUÑA", Gris �gata = "Gris ágata"). Re-encode every
human-text field: s.encode("latin-1").decode("utf-8"). The numeric fields, id and vin are clean.

Multi-axis classification (migrations/0016):
  defense_tier = 't0_open'         (CloudFront, no WAF; serves to plain curl — genuinely open)
  source_group = 'oem_vo_portal'   (the group renew opened; toyota_lexus is its third member)
  role         = 'platform'
  kind         = 'oem_vo_portal'   (the platform entity's ontology kind, migrations/0005)
  is_tier1     = FALSE             (no tier-1 WAF fronts the API)
  family       = 'toyota_lexus_vo' (ties the Toyota-group OEM-VO siblings on the family axis)

PROOF SLICE OR FULL. The two networks declare ~3,840 cars (Toyota ~3,274 + Lexus ~562). The set
is small and FLAT, so the FULL drain is in reach in a single run. --pages/--limit bound the run;
--limit converts a target car count to a page count. The declared full count is recorded for the
VAM verdict's slice arithmetic.

Engine: a POST against usc-webcomponents.toyota-europe.com/v1/api/usedcars/results/es/es routed
THROUGH the per-host governor (the same single choke point coches.net/spoticar/AS24 use). The
synchronous curl_cffi POST runs in a worker thread so the event loop is never blocked, and no host
is fetched faster than its bucket.

Run: python -m pipeline.platform.oem_toyota_lexus_wholesale --pages 80
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
# toyota_lexus platform identity (OEM-VO portal, migrations/0005 + 0016).
# ---------------------------------------------------------------------------
TL_DOMAIN = "toyota.es"
TL_WEBSITE = "toyota.es"
TL_LEGAL_NAME = "Toyota España (Toyota Plus + Lexus Select)"
TL_TRADE_NAME = "toyota_lexus"
TL_SOURCE_KEY = "oem_toyota_lexus_wholesale"
TL_WAF = "none"               # CloudFront fronts the API but NO bot WAF; serves to plain curl.
TL_DEFENSE_TIER = "t0_open"   # genuinely open (200 to plain urllib) -> tier 0 open.
TL_SOURCE_GROUP = "oem_vo_portal"
TL_ROLE = "platform"
TL_KIND = "oem_vo_portal"     # the platform ENTITY's ontology kind (NOT 'plataforma').
TL_FAMILY = "toyota_lexus_vo" # ties the Toyota-group OEM-VO siblings on the family axis.

# The working request (verified live 2026-06-13; recipe oem_toyota_lexus_datalayer.md TL;DR).
_BASE = "https://usc-webcomponents.toyota-europe.com"
LIST_PATH = "/v1/api/usedcars/results/es/es"   # the internal USC results JSON API.
ENDPOINT = _BASE + LIST_PATH
_DISTRIBUTOR_CODE = "9424M"   # the ES distributor; same for both brands.
_IMPERSONATE = "chrome131"
_TIMEOUT = 40
PAGE_SIZE = 48  # body `resultCount` governs page size (SPA sends 11; API honours >=100).

# The two official OEM-VO portals served by the ONE USC backend. Each brand is a separate
# ?brand= scope; together they enumerate the whole Toyota+Lexus ES certified-used network.
@dataclass(frozen=True)
class _BrandSurface:
    brand: str            # ?brand= query param value.
    portal_base: str      # the PDP base used to construct deep_links.
    portal_host: str      # human label.

_SURFACES = (
    _BrandSurface("toyota", "https://www.toyota.es/coches-segunda-mano", "toyota.es"),
    _BrandSurface("lexus", "https://www.lexusauto.es/lexus-seminuevos", "lexusauto.es"),
)

_HEADERS = {
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Accept-Language": "es-ES,es;q=0.9",
    "Origin": "https://www.toyota.es",
    "Referer": "https://www.toyota.es/",
}

# Province sentinel '00' = national (same convention as spoticar/renew/coches.net). geo_province
# has NO '00', so the platform ENTITY stores province_code = NULL; '00' lives only inside the
# cdp_code string (free text, no FK). We never pollute geo_province with it.
PLATFORM_PROVINCE_SENTINEL = "00"

# Full-drain default. ~3,840 cars across both brands. With PAGE_SIZE=48 the Toyota network is
# ~69 pages and Lexus ~12; 80 pages PER BRAND covers each whole network with margin. The drain is
# per-brand: each brand walks offset 0..totalResultCount independently.
DEFAULT_MAX_PAGES = 80


def tl_platform_cdp_code() -> str:
    """The toyota_lexus platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:toyota.es'), province segment '00' (national). Mirrors
    spoticar_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{TL_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Field helpers (the USC surface: nested objects + latin-1 mojibake on human text).
# ---------------------------------------------------------------------------


def _fix(s):
    """Repair latin-1 mojibake on human-text fields (autom�tico -> automático, LA CORU�A ->
    LA CORUÑA, Gris �gata -> Gris ágata). The wire bytes were UTF-8 mis-decoded as latin-1
    upstream; re-encode to recover. Numeric fields, id and vin are clean and never passed here."""
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
    """Safe nested getter: _get(car, 'product', 'brand', 'description')."""
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
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return _SLUG_NONWORD.sub("-", s.lower()).strip("-")


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL response — field names inspected live 2026-06-13, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class DealerRef:
    """The selling official dealer parsed from a single car's embedded `dealer{}` object.

    USC attaches the full dealer per car: dealer.id (stable), dealer.name, dealer.address
    {city, zip, region}, dealer.geoLocation {lat, lon}. The province comes from the zip
    (first 2 digits = INE province, authoritative); the lat/lon is the geocode fallback. id is
    the stable per-dealer key for cross-source dedup and as the source_ref."""
    dealer_id: str
    name: str | None
    province_code: str | None
    city: str | None
    zip: str | None
    lat: float | None
    lon: float | None


@dataclass
class Vehicle:
    """A car parsed from a single USC results item."""
    deep_link: str
    listing_ref: str           # USC stable car id (UUID) — also the dedup key.
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


def _first_image(car: dict) -> str | None:
    """Pick a hosted image URL. USC images are protocol-relative ('//used-car-publisher…');
    promote to https. Prefer the first sequenced image."""
    imgs = car.get("images")
    if isinstance(imgs, list) and imgs:
        url = None
        # honour `sequence` if present (1 = primary); else first.
        try:
            first = min((i for i in imgs if isinstance(i, dict) and i.get("url")),
                        key=lambda i: _to_int(i.get("sequence")) or 1_000_000, default=None)
            url = first.get("url") if first else None
        except (ValueError, TypeError):
            url = imgs[0].get("url") if isinstance(imgs[0], dict) else None
        if isinstance(url, str) and url:
            if url.startswith("//"):
                return "https:" + url
            return url if url.startswith("http") else "https://" + url.lstrip("/")
    return None


def parse_item_dealer(car: dict) -> DealerRef | None:
    """Parse the SELLING dealer from a car's embedded `dealer{}`. Returns None when there is no
    stable dealer id — the car cannot be attributed to a concrete official dealer."""
    dealer = car.get("dealer") or {}
    dealer_id = dealer.get("id") or car.get("dealerId")
    if not dealer_id:
        return None
    addr = dealer.get("address") or {}
    geo = dealer.get("geoLocation") or {}
    zip_raw = addr.get("zip")
    zip_s = str(zip_raw).strip() if zip_raw not in (None, "") else None
    return DealerRef(
        dealer_id=str(dealer_id),
        name=_fix(dealer.get("name")),
        province_code=None,                       # filled in _parse_window (zip first, then geo).
        city=_fix(addr.get("city")),
        zip=zip_s,
        lat=_to_float(geo.get("lat")),
        lon=_to_float(geo.get("lon")),
    )


def _build_deep_link(car: dict, surface: _BrandSurface) -> str:
    """Construct the PDP deep_link. The USC payload carries NO PDP url; the SPA builds it from the
    record as {portal_base}/pdp.{brand}-{model}-{year}-{body}-{transmission}-{fuel}-{id}. The
    terminal UUID (id) is the load-bearing key; the leading slug is SEO decoration. We mint the
    canonical, always-resolvable path."""
    car_id = car.get("id")
    if not car_id:
        return ""
    brand = _slugify(_get(car, "product", "brand", "description")) or surface.brand
    model = _slugify(_get(car, "product", "model", "description"))
    year = _get(car, "product", "modelYear") or ""
    body = _slugify(_get(car, "product", "bodyType"))
    trans = _slugify(_get(car, "product", "transmission", "transmissionType", "description"))
    fuel = _slugify(_get(car, "product", "engine", "marketingFuelType", "description"))
    parts = [p for p in (brand, model, str(year), body, trans, fuel) if p]
    slug = "-".join(parts)
    return f"{surface.portal_base}/pdp.{slug}-{car_id}" if slug else f"{surface.portal_base}/pdp.{car_id}"


def parse_item_vehicle(car: dict, surface: _BrandSurface) -> Vehicle:
    """Parse the car from a USC results item (REAL field map, nested objects)."""
    price = _to_float(_get(car, "price", "sellingPriceInclVAT"))
    if price is not None and price <= 0:
        price = None

    year = _to_int(_get(car, "product", "modelYear"))
    if year is None:
        reg = _get(car, "history", "registrationDate")  # 'YYYY-MM-DD'
        if isinstance(reg, str) and len(reg) >= 4:
            year = _to_int(reg[:4])
    if year is not None and not (1900 <= year <= 2100):
        year = None

    km = _to_int(_get(car, "mileage", "value"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    make = _fix(_get(car, "product", "brand", "description"))
    model = _fix(_get(car, "product", "model", "description"))
    version = _fix(_get(car, "product", "versionName"))
    title = " ".join(p for p in (make, model, version) if p) or None

    # The car id (UUID) is the stable per-car id AND the dedup key. It is clean.
    listing_ref = str(car.get("id") or "")

    # fuel: prefer the marketing fuel type (Híbrido/Eléctrico/…); transmission from the gearbox
    # transmissionType (Automático/Manual). Both are latin-1 repaired.
    fuel = (_fix(_get(car, "product", "engine", "marketingFuelType", "description"))
            or _fix(_get(car, "product", "engine", "displayFuelType")))
    transmission = _fix(_get(car, "product", "transmission", "transmissionType", "description"))

    vin = car.get("vin")

    return Vehicle(
        deep_link=_build_deep_link(car, surface),
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
        vin=str(vin) if vin else None,
    )


# ---------------------------------------------------------------------------
# Fetch: a POST routed THROUGH the governor (same per-host choke point as spoticar/coches.net).
# ---------------------------------------------------------------------------


class TLFetcher:
    """A POOL of fingerprint-coherent curl_cffi POST sessions for the USC results API.

    Same concurrency-vs-coherence model as SpoticarFetcher / CochesFetcher: a single curl_cffi
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

    def fetch_page(self, url: str, *, brand: str = "toyota", offset: int = 0,
                   page_size: int = PAGE_SIZE, slot: int = 0) -> dict:
        """The synchronous POST on pool session `slot` (runs in a worker thread).

        Handed to governor().wrap_fetch_text: the governor derives the host from `url`, waits on
        the per-host bucket, then runs THIS off the event loop. `slot`/`brand`/`offset` ride as
        kwargs the governor forwards untouched, so each in-flight request POSTs on its own leased,
        never-shared curl_cffi session (thread-safe). Raises on a non-200 so the breaker sees
        throttling (never masks a challenge/empty body)."""
        session = self._sessions[slot]
        body = {
            "uscEnv": "production",
            "filters": [],
            "filterContext": "used",
            "offset": offset,
            "resultCount": page_size,
            "sortOrder": "published",
            "distributorCode": _DISTRIBUTOR_CODE,
            "includeActiveFilterAggregations": False,
            "enableBiasedSort": False,
            "disabledFiltersIds": [],
            "enableExperimentalTotalCountQuery": False,
            "enableVehicleAggregations": False,
            "vehicleAggregationsVersionCode": "",
            "hasContentBlock": False,
            "enableDirectStockBiasedSort": False,
        }
        resp = session.post(f"{url}?brand={brand}", json=body, headers=_HEADERS,
                            impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url} (brand {brand} offset {offset})")
        return json.loads(resp.content.decode("utf-8", "replace"))

    async def fetch_page_async(self, governed_fetch, url: str, *, brand: str, offset: int,
                               page_size: int) -> dict:
        """Lease a pool slot, fetch `offset` THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, brand=brand, offset=offset,
                                        page_size=page_size, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer (mirrors spoticar_wholesale: ensure platform, bulk-upsert dealer/vehicle, link edge,
# emit delta, all idempotent ON CONFLICT). Multi-axis 0016 classification set.
# ---------------------------------------------------------------------------

TL_PLATFORM_RECIPE = {
    "version": 1,
    "source": "toyota_lexus (toyota.es + lexusauto.es)",
    "scope": "platform-wholesale (Toyota Plus + Lexus Select ES certified-used; USC Web Components JSON API)",
    "engine": "curl_cffi+chrome131_impersonate+usc_internal_json_api(POST)",
    "access": ("OPEN (t0_open). USC API behind AWS CloudFront with NO bot WAF — serves 200 "
               "application/json to plain curl. chrome131 used only for fleet coherence. No proxy, "
               "no browser, no cookie warm-up, no auth, €0. is_tier1=FALSE (no tier-1 WAF)."),
    "data_surface": "internal_api",
    "surface_intent": "usc_internal_json_api",
    "endpoint": "POST https://usc-webcomponents.toyota-europe.com/v1/api/usedcars/results/es/es?brand={toyota|lexus}",
    "request": {
        "headers": "Content-Type application/json, Accept */*, Origin/Referer toyota.es",
        "body": ("uscEnv=production, filters=[], filterContext=used, offset=ROW cursor, "
                 "resultCount=page size, sortOrder=published, distributorCode=9424M"),
    },
    "enumeration": ("PER BRAND: offset=0..totalResultCount step resultCount; brand=toyota (~3274) "
                    "+ brand=lexus (~562). dedup on results[].id (UUID). Stop on "
                    "offset>=totalResultCount or empty results[]."),
    "denominator": "totalResultCount (top-level) == Σ aggregations.usedCarBrand doc_count",
    "platform_entity": ("kind=oem_vo_portal, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=FALSE, defense_tier=t0_open, source_group=oem_vo_portal, role=platform, "
                        "family=toyota_lexus_vo"),
    "dual_membership": ("vehicle.entity_ulid=SELLING DEALER (compraventa); "
                        "platform_listing edge=platform<->vehicle"),
    "field_map": {
        "deep_link": "constructed {portal_base}/pdp.{slug}-{id} (no url field in payload)",
        "listing_ref": "results[].id (UUID; stable id + dedup key)",
        "vin": "results[].vin (REAL per-car VIN — gold for cross-source dedup)",
        "make": "results[].product.brand.description",
        "model": "results[].product.model.description",
        "version": "results[].product.versionName",
        "year": "results[].product.modelYear (fallback history.registrationDate[:4])",
        "km": "results[].mileage.value",
        "price": "results[].price.sellingPriceInclVAT (currencyCode=EUR)",
        "fuel": "results[].product.engine.marketingFuelType.description (fallback displayFuelType)",
        "transmission": "results[].product.transmission.transmissionType.description",
        "photo": "results[].images[0].url (protocol-relative -> https)",
        "dealer": "results[].dealer {id, name, address{city,zip,region}, geoLocation{lat,lon}, website, phone}",
        "location": ("dealer.address.zip[:2] = INE province (authoritative); "
                     "dealer.geoLocation lat/lon -> ProvinceGeocoder fallback; "
                     "dealer.address.city -> municipality (INE-resolved, best-effort)"),
    },
    "caveats": {
        "page_size": "body `resultCount` IS the page size (SPA sends 11; API honours >=100).",
        "offset": "`offset` is a ROW offset, not a page index — offset += resultCount.",
        "brand_scope": "?brand=toyota returns the whole network incl. non-Toyota trade-ins (cage all).",
        "encoding": ("brand/dealer/city/colour text is latin-1 mojibake (autom�tico, LA CORU�A); "
                     "repair with s.encode('latin-1').decode('utf-8'). id/vin/numeric clean."),
        "no_pdp_url": "no PDP url in payload — constructed from id + slug fields.",
        "no_private_sellers": "OEM certified-used portal — every car belongs to an official dealer.",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the toyota_lexus platform entity + platform_meta exist. Returns the
    platform entity_ulid. kind='oem_vo_portal' (the platform ontology kind), is_tier1=FALSE (no
    tier-1 WAF), multi-axis 0016 classification set explicitly, data_surface='internal_api'."""
    code = tl_platform_cdp_code()
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
        eulid, code, TL_KIND, TL_LEGAL_NAME, TL_TRADE_NAME, TL_WEBSITE,
        TL_WAF, TL_DEFENSE_TIER, TL_SOURCE_GROUP, TL_ROLE, TL_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, TL_SOURCE_KEY, TL_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'internal_api',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"endpoint": ENDPOINT, "host": host_of(ENDPOINT),
                           "method": "POST", "page_size": PAGE_SIZE,
                           "denominator": "totalResultCount",
                           "brands": [s.brand for s in _SURFACES],
                           "distributor_code": _DISTRIBUTOR_CODE,
                           "surface_intent": "usc_internal_json_api",
                           "engine": "curl_cffi/chrome131_impersonate"}),
        TL_FAMILY)
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    USC dealers have no bare domain identity on this surface (their `website` is a toyota.es
    instalaciones path, NOT a bare host) -> identity = name + location + the stable dealer.id
    (passed via `address` so two distinct dealers that happen to share a name in one municipality
    never collapse to one entity)."""
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni, address=f"dealer:{d.dealer_id}")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# Default concurrency: pages fetched in parallel per sliding window. The USC host is NOT in the
# governor's JSON_API rate class — it inherits the conservative STEALTH default, the safe direction
# for an unmeasured host. The concurrency only needs to keep that (slow) bucket saturated; a small
# window is plenty.
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


def _parse_window(items_by_page: list[tuple[int, str, list]], geo: GeoResolver,
                  geocoder: ProvinceGeocoder, seen_ids: set, harvested_cageable: set,
                  stats: dict) -> list[_CageRow]:
    """Parse + geo-resolve every car across the window IN ORDER — pure CPU, no SQL.

    The EXACT per-item gate (cross-page dedup on results[].id, dealer-parse skip, geo skip,
    cageable truth), lifted out of the DB loop so the SQL phase is purely set-based. The province
    is resolved zip-first then geocode-fallback. `seen_ids` / `harvested_cageable` / `stats` are
    mutated here with deterministic order semantics so the VAM truth is byte-identical regardless
    of batching. Each tuple is (offset, brand, items); the brand picks the right PDP surface."""
    by_brand = {s.brand: s for s in _SURFACES}
    rows: list[_CageRow] = []
    for _offset, brand, items in items_by_page:
        surface = by_brand.get(brand, _SURFACES[0])
        for car in items:
            if not isinstance(car, dict):
                continue
            stats["items_seen"] += 1
            # cross-page dedup on the car id (the stable dedup key; default sort is not stable
            # across a long crawl, so the same car can reappear on a later page).
            item_id = str(car.get("id") or "")
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
            # province-range guard the dealer upsert enforces, done in memory so a bad/missing geo
            # is skipped without ever touching the DB (no FK risk).
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
            if v.vin:
                stats["vins_captured"] += 1
            rows.append(_CageRow(
                dealer_id=d.dealer_id, dealer_cdp=dealer_cdp, dealer_name=d.name,
                dealer_province=prov, dealer_muni=muni, vehicle=v))
    return rows


async def _ingest_window(conn: asyncpg.Connection, geo: GeoResolver, geocoder: ProvinceGeocoder,
                         platform_ulid: str, items_by_page: list[tuple[int, str, list]],
                         seen_ids: set, harvested_cageable: set, stats: dict) -> None:
    """BULK-ingest a whole concurrent page-window in ONE transaction with set-based SQL.

    Mirrors spoticar_wholesale._ingest_window EXACTLY: ONE round-trip per table per window (unnest
    multi-row upserts). The delta/VAM/platform_listing semantics are preserved: same ON CONFLICT
    idempotency, same cageable truth, same NEW-event rule (emitted only for genuinely new
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
                           d_munis, d_refs, TL_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_DEALER_SOURCES, d_cdps, d_refs, TL_SOURCE_KEY)
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
                payload = {"price": v.price, "title": v.title, "platform": TL_TRADE_NAME}
                if v.vin:
                    payload["vin"] = v.vin
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities,
                               ev_payloads)
            stats["new_events"] += len(confirmed_new)


async def _drain_brand(conn, geo, geocoder, platform_ulid, fetcher, governed_fetch,
                       surface: _BrandSurface, max_pages: int, concurrency: int,
                       seen_ids: set, harvested_cageable: set, stats: dict) -> tuple[str | None, int | None]:
    """Drain ONE brand surface (?brand=...) by walking the offset cursor in concurrent windows.

    Returns (fetch_error, last_http). The offset cursor is per-brand; totalResultCount (read from
    the first page) + emptiness bound the run. Pages are fetched in parallel through the governor
    (the host bucket paces the aggregate) then ingested sequentially in offset order."""
    fetch_error: str | None = None
    last_http: int | None = None
    declared_total: int | None = None
    stop = False
    next_page = 0  # page index within this brand (0-based)
    print(f"[oem_toyota_lexus] === draining brand={surface.brand} ({surface.portal_host}) ===")
    while next_page < max_pages and not stop:
        window = list(range(next_page, min(next_page + concurrency, max_pages)))
        next_page = window[-1] + 1
        # bound by declared total once known
        if declared_total is not None:
            window = [p for p in window if p * PAGE_SIZE < declared_total]
            if not window:
                break

        results = await asyncio.gather(
            *(fetcher.fetch_page_async(governed_fetch, ENDPOINT, brand=surface.brand,
                                       offset=p * PAGE_SIZE, page_size=PAGE_SIZE) for p in window),
            return_exceptions=True,
        )

        window_pages: list[tuple[int, str, list]] = []
        for page, data in zip(window, results):
            if isinstance(data, Exception):
                fetch_error = str(data)
                last_http = fetcher.last_status
                print(f"[oem_toyota_lexus] brand={surface.brand} page {page} fetch failed ({data}); "
                      f"stopping this brand honestly.")
                stop = True
                break
            if declared_total is None:
                declared_total = _to_int(data.get("totalResultCount"))
                stats["declared_per_brand"][surface.brand] = declared_total
                if stats["declared_full"] is None:
                    stats["declared_full"] = 0
                stats["declared_full"] += declared_total or 0
            items = data.get("results") or []
            if not items:
                print(f"[oem_toyota_lexus] brand={surface.brand} page {page}: no results; "
                      f"stopping (data boundary reached).")
                stop = True
                break
            window_pages.append((page * PAGE_SIZE, surface.brand, items))

        if window_pages:
            await _ingest_window(conn, geo, geocoder, platform_ulid, window_pages, seen_ids,
                                 harvested_cageable, stats)
            stats["pages_fetched"] += len(window_pages)
            first_p, last_p = window_pages[0][0], window_pages[-1][0]
            print(f"[oem_toyota_lexus] brand={surface.brand} offsets {first_p}-{last_p}: "
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
    # --pages / --limit bounds the run (applied PER BRAND).
    if limit is not None and limit > 0:
        limit_pages = max(1, math.ceil(limit / PAGE_SIZE))
        max_pages = min(max_pages, limit_pages)
    fetcher = TLFetcher(pool_size=concurrency)
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
    # gracefully — the API keeps serving the last snapshot.
    if await is_open(conn, TL_SOURCE_KEY):
        print(f"[oem_toyota_lexus] breaker OPEN for {TL_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, API still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": TL_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        geocoder = await ProvinceGeocoder.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = tl_platform_cdp_code()
        print(f"[oem_toyota_lexus] platform entity ready: {platform_code} (ulid={platform_ulid}) "
              f"kind={TL_KIND} group={TL_SOURCE_GROUP} tier={TL_DEFENSE_TIER} family={TL_FAMILY}")
        print(f"[oem_toyota_lexus] geocoder anchors: {geocoder.size()} labeled points (lat/lon -> province).")
        print(f"[oem_toyota_lexus] governor paces host {host_of(ENDPOINT)} (per-host token bucket, STEALTH class).")
        print(f"[oem_toyota_lexus] CONCURRENT drain: window={concurrency} pages in flight. "
              f"Target = {max_pages} pages/brand x {len(_SURFACES)} brands "
              f"(~{max_pages * PAGE_SIZE * len(_SURFACES)} cars cap; full ES stock ~3840).")

        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        # Drain each brand surface in turn (each its own offset cursor + declared total).
        for surface in _SURFACES:
            err, http = await _drain_brand(
                conn, geo, geocoder, platform_ulid, fetcher, governed_fetch, surface,
                max_pages, concurrency, seen_ids, harvested_cageable, stats)
            if err is not None:
                fetch_error = err
                last_http = http
                # a hard fetch error on one brand stops the whole drain honestly (breaker must see it).
                break

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, TL_PLATFORM_RECIPE)
        print(f"[oem_toyota_lexus] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths that all measure
        # "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for toyota_lexus   (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join        (DB read truth)
        #   harvested_cageable = distinct (dealer_id, deep_link) pulled      (harvest truth)
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

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks toyota_lexus, trips
        # the breaker on a ban, and auto-repairs. OK when >=1 page fetched, no fetch error stopped
        # the drain, and the VAM did not refute.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, TL_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, TL_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[oem_toyota_lexus] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("TOYOTA+LEXUS (OEM-VO PORTAL) WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  group / kind          : oem_vo_portal / oem_vo_portal (tier t0_open, family toyota_lexus_vo)")
    print(f"  declared full (source): {stats.get('declared_full')} {stats.get('declared_per_brand')}")
    print(f"  concurrency (window)  : {stats.get('concurrency')} pages in flight")
    print(f"  target pages/brand    : {stats.get('max_pages')}")
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
          f"(db total for toyota_lexus = {stats.get('db_edges')})")
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
        description="toyota_lexus OEM-VO portal wholesale harvester (concurrent USC-JSON drain)")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"pages PER BRAND to harvest (size={PAGE_SIZE}); default {DEFAULT_MAX_PAGES} (full ES stock)")
    parser.add_argument("--limit", type=int, default=None,
                        help=(f"optional target car count PER BRAND; converted to a page count "
                              f"({PAGE_SIZE}/page). The tighter of --pages / --limit bounds the run."))
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"pages fetched in parallel per sliding window; default "
                              f"{DEFAULT_CONCURRENCY}. The USC host inherits the conservative STEALTH "
                              f"rate class — the governor's per-host bucket is the real limiter."))
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.pages, args.concurrency, args.limit))
    _print_report(stats)


if __name__ == "__main__":
    main()
