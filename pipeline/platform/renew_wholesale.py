"""renew (Renault/Dacia certified-used) WHOLESALE harvester — the FIRST OEM-VO portal, end to end.

es.renew.auto is the manufacturer certified-used portal for the Renault Group in Spain
(Renault + Dacia + Refactory-reconditioned stock). It is NOT a car-specialist marketplace
(coches.net/autoscout24/motor.es) nor a generalist classifieds (wallapop): it is an
OEM-VO PORTAL — a single brand-owner publishing the certified-used inventory of its own
dealer network. That is a NEW source_group ('oem_vo_portal'), a NEW entity kind for the
platform itself ('oem_vo_portal'), and the OWNER's explicit demand: "los demás con su
sistema" — beyond the giant marketplaces, work the OEM certified-used portals too.

The surface is an AEM + Elasticsearch faceted catalog fronted by a React-Router single-fetch
loader. The public page /vehiculos accepts RAW Elasticsearch facet params in the query string
(brand.label.raw=RENAULT, model.label.raw=CLIO, ...). The SAME route exposes a clean JSON
loader at /vehiculos.data?<facets>&page=N: no browser, no proxy, no cookie warm-up — just a
Chrome TLS fingerprint (curl_cffi) and a GET. Inside that JSON, the slice
content.contentZone.slice243v0.data carries:
    totalElements / totalPages   -> the census denominator (per facet)
    data[]                        -> 23 cars/page, each a fully-specced object
    each car.vehicleExhibitionSite-> the SELLING DEALER (dealerId, name, postalCode, locality,
                                     geolocalization) — STRONG per-dealer attribution
Verified live 2026-06-12: 5,739 cars unfiltered (RENAULT 4,274 + DACIA 1,012 + others), the
`page` param is a clean stable paginator (zero cross-page id overlap over 138 cars / 6 pages),
each car carries a REAL per-vehicle VIN (unlike motor.es's dummy) — gold for cross-source dedup.

This module mirrors pipeline.platform.coches_net_wholesale EXACTLY (same dual-membership model,
same bulk cage, same governor/health/VAM wiring). It proves the OEM-VO group flows through the
ONE architecture, not a fork of it:

  renew (the OEM-VO portal)  -> entity, kind='oem_vo_portal' (+ platform_meta)  [THE PLATFORM]
  each EXHIBITION-SITE DEALER-> entity, kind='compraventa'   (geo-resolved)
  each CAR                   -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the portal      -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the exhibition-site dealer); platform membership is plural (this edge).
The same physical car can carry BOTH a renew edge and a coches.net edge without ever changing
its owning dealer.

Multi-axis classification (migrations/0016):
  defense_tier = 't0_open'         (open .data JSON loader; no WAF challenge to curl_cffi)
  source_group = 'oem_vo_portal'   (the NEW group this connector opens)
  role         = 'platform'
  kind         = 'oem_vo_portal'   (the platform entity's ontology kind, migrations/0005)

PROOF SLICE, NOT THE FULL HARVEST. renew declares ~5,739 cars unfiltered (totalElements).
Draining all of it (~250 pages at 23/page) needs the full governed run. Here we cap at
MAX_PAGES and log the cap honestly. The declared full count is recorded for the VAM verdict's
slice arithmetic.

Engine: a GET against es.renew.auto/vehiculos.data routed THROUGH the per-host governor (the
same single choke point coches.net/AS24 use). The synchronous curl_cffi GET runs in a worker
thread so the event loop is never blocked, and no host is fetched faster than its bucket.

Run: python -m pipeline.platform.renew_wholesale --pages 8
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from urllib.parse import quote

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
# renew platform identity (OEM-VO portal, migrations/0005 + 0016).
# ---------------------------------------------------------------------------
RENEW_DOMAIN = "es.renew.auto"
RENEW_WEBSITE = "es.renew.auto"
RENEW_LEGAL_NAME = "Renault Group España (renew)"
RENEW_TRADE_NAME = "renew"
RENEW_SOURCE_KEY = "renew_wholesale"
RENEW_WAF = "none"               # the .data loader serves to curl_cffi with no challenge.
RENEW_DEFENSE_TIER = "t0_open"   # open JSON loader, no WAF challenge -> tier 0.
RENEW_SOURCE_GROUP = "oem_vo_portal"
RENEW_ROLE = "platform"
RENEW_KIND = "oem_vo_portal"     # the platform ENTITY's ontology kind (NOT 'plataforma').
RENEW_FAMILY = "renault_group"   # ties co-defended OEM-VO siblings (Spoticar/DasWeltAuto...) by family axis.

# The working request (verified live 2026-06-12).
_BASE = "https://es.renew.auto"
LIST_PATH = "/vehiculos.data"    # React-Router single-fetch loader; same route as the SSR page.
ENDPOINT = _BASE + LIST_PATH
_HEADERS = {
    "Accept": "*/*",
    "Referer": "https://es.renew.auto/vehiculos",
    "X-Requested-With": "XMLHttpRequest",
}
_PDP_BASE = "https://es.renew.auto/vehiculos/detalle.html?productId="  # car.productId -> canonical PDP.
_IMPERSONATE = "chrome131"
_TIMEOUT = 40
PAGE_SIZE = 23  # the loader serves a fixed 23 cars/page (verified live).

# Province sentinel '00' = national (same convention as coches.net/AS24). geo_province has NO
# '00', so the platform ENTITY stores province_code = NULL; '00' lives only inside the cdp_code
# string (free text, no FK). We never pollute geo_province with it.
PLATFORM_PROVINCE_SENTINEL = "00"

# PROOF SLICE cap. ~8 pages * 23 = ~184 cars. NOT the ~5,739 full set (full drain = ~250 pages).
DEFAULT_MAX_PAGES = 8

# The brand facets the OWNER named (renew is a Renault-Group portal). 'ALL' = unfiltered census.
# The drain runs unfiltered by default (the portal's full stock); a brand facet narrows it.
_BRAND_FACET_KEY = "brand.label.raw"


def renew_platform_cdp_code() -> str:
    """The renew platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:es.renew.auto'), province segment '00' (national). Mirrors
    coches_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{RENEW_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL response — field names inspected live, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class DealerRef:
    """The selling EXHIBITION-SITE dealer parsed from a single car's vehicleExhibitionSite.

    renew attaches the full physical site per car: dealerId (stable per-site id), name,
    and address {postalCode, locality}. The geo anchor is the postalCode (first 2 digits =
    INE province code) + locality (resolves the municipality). dealerId is the stable
    per-dealer key used for cross-source dedup and as the source_ref."""
    dealer_id: str
    name: str | None
    province_code: str | None
    city: str | None
    postal_code: str | None


@dataclass
class Vehicle:
    """A car parsed from a single renew search item."""
    deep_link: str
    listing_ref: str           # renew native vehicle id (car.identifier)
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


def _to_int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _prov_from_postal(postal) -> str | None:
    """Spanish postal codes are 5 digits; the first 2 ARE the INE province code (28xxx=Madrid,
    08xxx=Barcelona, 15xxx=A Coruña). Zero-pad and range-check (01..52)."""
    if not postal:
        return None
    s = str(postal).strip()
    if len(s) < 2 or not s[:2].isdigit():
        return None
    p = s[:2]
    if not ("01" <= p <= "52"):
        return None
    return p


def _first_photo(assets) -> str | None:
    """car.assets[0].renditions[] holds the image URLs at several resolutions. Prefer 'medium'
    (a real, hosted image URL), fall back to the first rendition with a url."""
    if not isinstance(assets, list):
        return None
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        rends = asset.get("renditions")
        if not isinstance(rends, list):
            continue
        chosen = None
        for rend in rends:
            if not isinstance(rend, dict) or not rend.get("url"):
                continue
            if rend.get("resolutionType") == "medium":
                return rend["url"]
            if chosen is None:
                chosen = rend["url"]
        if chosen:
            return chosen
    return None


def _year_from_first_reg(date_str) -> int | None:
    """firstRegistrationDate is 'YYYY-MM-DD'. Extract YYYY, range-guard."""
    if not date_str or not isinstance(date_str, str) or len(date_str) < 4:
        return None
    y = _to_int(date_str[:4])
    if y is None or not (1900 <= y <= 2100):
        return None
    return y


def parse_item_dealer(item: dict) -> DealerRef | None:
    """Parse the SELLING dealer from a car's vehicleExhibitionSite (the physical site that
    holds the car). dealer (fallback) and vehicleExhibitionSite carry the same shape; the
    exhibition site is the authoritative selling location."""
    site = item.get("vehicleExhibitionSite") or item.get("dealer") or {}
    dealer_id = site.get("dealerId")
    if not dealer_id:
        return None
    addr = site.get("address") or {}
    postal = addr.get("postalCode")
    prov = _prov_from_postal(postal)
    return DealerRef(
        dealer_id=str(dealer_id),
        name=site.get("name"),
        province_code=prov,
        city=addr.get("locality"),
        postal_code=str(postal) if postal else None,
    )


def parse_item_vehicle(item: dict) -> Vehicle:
    """Parse the car from a renew search item (REAL field map)."""
    prices = item.get("prices")
    price = None
    if isinstance(prices, list) and prices:
        p0 = prices[0] or {}
        amount = p0.get("customerDisplayPrice")
        if amount is None:
            amount = p0.get("priceWithTaxes")
        try:
            price = float(amount) if amount is not None else None
        except (TypeError, ValueError):
            price = None

    km = _to_int(item.get("mileage"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    brand = (item.get("brand") or {}).get("label")
    model = (item.get("model") or {}).get("label")
    version = (item.get("version") or {}).get("label")
    title = " ".join(p for p in (brand, model, version) if p) or item.get("name") or None

    product_id = item.get("productId") or ""
    identifier = item.get("identifier") or product_id
    deep_link = (_PDP_BASE + quote(str(product_id), safe="")) if product_id else ""

    energy = item.get("energy") or {}
    transmission = item.get("transmission") or {}

    return Vehicle(
        deep_link=deep_link,
        listing_ref=str(identifier),
        title=title,
        make=brand,
        model=model,
        year=_year_from_first_reg(item.get("firstRegistrationDate")),
        km=km,
        price=price,
        fuel=energy.get("label") or energy.get("groupLabel"),
        transmission=transmission.get("label"),
        photo_url=_first_photo(item.get("assets")),
        vin=item.get("vin") or None,
    )


# ---------------------------------------------------------------------------
# Fetch: a GET routed THROUGH the governor (same per-host choke point as coches.net).
# ---------------------------------------------------------------------------


class RenewFetcher:
    """A POOL of fingerprint-coherent curl_cffi GET sessions for the renew .data loader.

    Same concurrency-vs-coherence model as CochesFetcher: a single curl_cffi Session is NOT
    safe to call from several threads at once, and the governor runs each fetch in its own
    worker thread (asyncio.to_thread). The fix is a bounded POOL — one Session per concurrency
    slot, each its own Chrome fingerprint + cookie jar. The governor's per-host bucket bounds
    the AGGREGATE rate across every session, so the pool widens parallelism WITHOUT out-pacing
    the host (the choke point is the bucket, never the session count).
    """

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch_page(self, url: str, *, page: int = 1, brand: str | None = None,
                   slot: int = 0) -> dict:
        """The synchronous GET on pool session `slot` (runs in a worker thread).

        Handed to governor().wrap_fetch_text: the governor derives the host from `url`, waits
        on the per-host bucket, then runs THIS off the event loop. `slot` rides as a kwarg the
        governor forwards untouched, so each in-flight request GETs on its own leased,
        never-shared curl_cffi session (thread-safe). Raises on a non-200 so the breaker sees
        throttling (never masks a challenge/empty body)."""
        params = {"page": page}
        if brand:
            params[_BRAND_FACET_KEY] = brand
        session = self._sessions[slot]
        resp = session.get(url, params=params, headers=_HEADERS,
                           impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url} (page {page})")
        # UTF-8 JSON; decode explicitly so accented fuel/city names survive curl_cffi's guess.
        return json.loads(resp.content.decode("utf-8"))

    async def fetch_page_async(self, governed_fetch, url: str, *, page: int,
                               brand: str | None = None) -> dict:
        """Lease a pool slot, fetch `page` THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, page=page, brand=brand, slot=slot)
        finally:
            self._free.put_nowait(slot)


def extract_block(data: dict) -> dict | None:
    """Pull the search slice out of the .data loader JSON. The cars live at
    content.contentZone.slice243v0.data ({totalElements, totalPages, data[], facets}). The
    slice key is stable for the listing route; we resolve it defensively by scanning the
    contentZone for the child that carries a 'data' dict with 'totalElements'."""
    content = data.get("content") or {}
    zone = content.get("contentZone") or {}
    if not isinstance(zone, dict):
        return None
    # Fast path: the known slice key.
    slice_node = zone.get("slice243v0")
    if isinstance(slice_node, dict):
        blk = slice_node.get("data")
        if isinstance(blk, dict) and "totalElements" in blk:
            return blk
    # Defensive scan: any slice child whose .data is the search block (route may rename slices).
    for key, node in zone.items():
        if not isinstance(node, dict):
            continue
        blk = node.get("data")
        if isinstance(blk, dict) and "totalElements" in blk and isinstance(blk.get("data"), list):
            return blk
    return None


# ---------------------------------------------------------------------------
# DB layer (mirrors coches_net_wholesale: ensure platform, bulk-upsert dealer/vehicle,
# link edge, emit delta, all idempotent ON CONFLICT). Multi-axis 0016 classification set.
# ---------------------------------------------------------------------------

RENEW_PLATFORM_RECIPE = {
    "version": 1,
    "source": "renew (es.renew.auto)",
    "scope": "platform-wholesale (AEM+Elasticsearch faceted catalog via React-Router .data loader)",
    "engine": "curl_cffi+chrome131_impersonate+es_facet_json(GET)",
    "access": ("OPEN/FREE (Chrome TLS fingerprint; no proxy, no browser, no cookie warm-up). "
               "The /vehiculos route accepts RAW Elasticsearch facet params; its .data single-"
               "fetch loader returns clean faceted JSON. No WAF challenge -> defense_tier=t0_open."),
    "data_surface": "es_facet",
    "surface_intent": "es_facet_json_loader",
    "endpoint": "GET https://es.renew.auto/vehiculos.data?<es_facets>&page=N",
    "request": {
        "headers": "Accept */*, Referer /vehiculos, X-Requested-With XMLHttpRequest",
        "facets": "RAW Elasticsearch params: brand.label.raw=RENAULT, model.label.raw=CLIO, ... (omit for full census)",
    },
    "enumeration": ("page=1..N (23 cars/page, zero cross-page id overlap — clean stable paginator); "
                    "block.totalElements/totalPages drive the full drain (~5,739 cars / ~250 pages unfiltered)"),
    "block_path": "content.contentZone.slice243v0.data {totalElements, totalPages, data[], facets}",
    "platform_entity": ("kind=oem_vo_portal, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=FALSE, defense_tier=t0_open, source_group=oem_vo_portal, role=platform, "
                        "family=renault_group"),
    "dual_membership": ("vehicle.entity_ulid=SELLING EXHIBITION-SITE DEALER (compraventa); "
                        "platform_listing edge=platform<->vehicle"),
    "field_map": {
        "deep_link": "https://es.renew.auto/vehiculos/detalle.html?productId={car.productId}",
        "listing_ref": "car.identifier (renew native vehicle id; {dealerPrefix}_{plate})",
        "vin": "car.vin (REAL per-car VIN — gold for cross-source dedup)",
        "make": "car.brand.label",
        "model": "car.model.label",
        "version": "car.version.label",
        "year": "car.firstRegistrationDate (YYYY-MM-DD -> YYYY)",
        "km": "car.mileage (mileageUnit=KM)",
        "price": "car.prices[0].customerDisplayPrice (fallback priceWithTaxes), EUR",
        "fuel": "car.energy.label (Diesel/Gasolina/Eléctrico/...)",
        "transmission": "car.transmission.label (Manual/Automático)",
        "photo_url": "car.assets[0].renditions[resolutionType=medium].url",
        "dealer": "car.vehicleExhibitionSite {dealerId, name, address.postalCode, address.locality, geolocalization}",
        "location": "postalCode[:2] = INE province code; locality -> municipality (INE-resolved)",
    },
    "caveats": {
        "page_size": "fixed 23 cars/page (loader-controlled, not a request param).",
        "vin_gold": "unlike motor.es (dummy VIN), renew exposes a REAL per-car VIN.",
        "multi_brand": "unfiltered census includes RENAULT + DACIA + Refactory-reconditioned others.",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the renew platform entity + platform_meta exist. Returns the
    platform entity_ulid. kind='oem_vo_portal' (the platform ontology kind), is_tier1=FALSE
    (no hard WAF), multi-axis 0016 classification set explicitly, data_surface='es_facet'."""
    code = renew_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               defense_tier, source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,$3,$4,$5,NULL,$6,$7,FALSE,'active','platform_label',
               $8::defense_tier,$9::source_group,$10::entity_role,$11, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, website_waf = EXCLUDED.website_waf,
               defense_tier = EXCLUDED.defense_tier, source_group = EXCLUDED.source_group,
               role = EXCLUDED.role, legal_name = EXCLUDED.legal_name, kind = EXCLUDED.kind""",
        eulid, code, RENEW_KIND, RENEW_LEGAL_NAME, RENEW_TRADE_NAME, RENEW_WEBSITE, RENEW_WAF,
        RENEW_DEFENSE_TIER, RENEW_SOURCE_GROUP, RENEW_ROLE, RENEW_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, RENEW_SOURCE_KEY, RENEW_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'es_facet',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"endpoint": ENDPOINT, "host": host_of(ENDPOINT),
                           "method": "GET", "page_size": PAGE_SIZE,
                           "facet_key": _BRAND_FACET_KEY,
                           "block_path": "content.contentZone.slice243v0.data",
                           "surface_intent": "es_facet_json_loader",
                           "engine": "curl_cffi/chrome131_impersonate"}),
        RENEW_FAMILY)
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    renew exhibition-site dealers have no bare domain on this surface -> identity = name +
    location + the stable dealerId (passed via `address` so two distinct sites that happen to
    share a name in one municipality never collapse to one entity)."""
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni, address=f"dealer:{d.dealer_id}")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# Default concurrency: pages fetched in parallel per sliding window. The governor's per-host
# bucket is the real limiter, so this only needs to be wide enough to keep the bucket saturated.
DEFAULT_CONCURRENCY = 8


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


# The four bulk statements — ONE round-trip per table per window (unnest-based multi-row upsert),
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


def _parse_window(items_by_page: list[tuple[int, list]], geo: GeoResolver,
                  seen_ids: set, harvested_cageable: set, stats: dict) -> list[_CageRow]:
    """Parse + geo-resolve every car across the window IN PAGE ORDER — pure CPU, no SQL.

    The EXACT per-item gate (cross-page dedup, dealer-parse skip, geo skip, cageable truth),
    lifted out of the DB loop so the SQL phase is purely set-based. `seen_ids` /
    `harvested_cageable` / `stats` are mutated here with deterministic page-order semantics so
    the VAM truth is byte-identical regardless of batching."""
    rows: list[_CageRow] = []
    for _page, items in items_by_page:
        for item in items:
            stats["items_seen"] += 1
            item_id = str(item.get("identifier") or item.get("productId") or "")
            if item_id and item_id in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue  # cross-page dedup (stable-sort hazard guard)
            if item_id:
                seen_ids.add(item_id)

            d = parse_item_dealer(item)
            if d is None:
                stats["no_dealer_skipped"] += 1
                continue
            stats["dealer_items"] += 1

            # Geo gate — same province-range guard the dealer upsert applies, done in memory so a
            # bad province is skipped without ever touching the DB (no FK risk).
            if not d.province_code:
                stats["geo_skipped"] += 1
                continue
            if not (d.province_code.isdigit() and "01" <= d.province_code <= "52"):
                stats["geo_skipped"] += 1
                continue
            muni = geo.municipality_code(d.province_code, d.city)
            dealer_cdp = cdp_code_dealer(d, muni)

            v = parse_item_vehicle(item)
            if not v.deep_link:
                continue
            harvested_cageable.add((d.dealer_id, v.deep_link))
            if v.vin:
                stats["vins_captured"] += 1
            rows.append(_CageRow(
                dealer_id=d.dealer_id, dealer_cdp=dealer_cdp, dealer_name=d.name,
                dealer_province=d.province_code, dealer_muni=muni, vehicle=v))
    return rows


async def _ingest_window(conn: asyncpg.Connection, geo: GeoResolver, platform_ulid: str,
                         items_by_page: list[tuple[int, list]], seen_ids: set,
                         harvested_cageable: set, stats: dict) -> None:
    """BULK-ingest a whole concurrent page-window in ONE transaction with set-based SQL.

    Mirrors coches_net_wholesale._ingest_window EXACTLY: ONE round-trip per table per window
    (unnest multi-row upserts). The delta/VAM/platform_listing semantics are preserved: same
    ON CONFLICT idempotency, same cageable truth, same NEW-event rule (emitted only for
    genuinely new vehicles). A re-run of an already-harvested window adds 0 rows and 0 events.
    """
    cage = _parse_window(items_by_page, geo, seen_ids, harvested_cageable, stats)
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
                           d_munis, d_refs, RENEW_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_DEALER_SOURCES, d_cdps, d_refs, RENEW_SOURCE_KEY)
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
                payload = {"price": v.price, "title": v.title, "platform": RENEW_TRADE_NAME}
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
                  brand: str | None = None) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    fetcher = RenewFetcher(pool_size=concurrency)
    stats = {
        "pages_fetched": 0, "items_seen": 0, "dealer_items": 0,
        "no_dealer_skipped": 0, "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "vins_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "dealers_distinct": 0,
        "concurrency": concurrency, "brand_facet": brand or "ALL",
    }
    # Harvest-side truth for the VAM: distinct CAGEABLE cars = distinct (dealer_id, deep_link)
    # pairs that survived dealer-parse + geo-resolution. Like-with-like vs db_edges.
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if renew's breaker is OPEN (a recent ban/throttle still cooling), skip the
    # drain gracefully — the API keeps serving the last snapshot.
    if await is_open(conn, RENEW_SOURCE_KEY):
        print(f"[renew_wholesale] breaker OPEN for {RENEW_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, API still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": RENEW_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = renew_platform_cdp_code()
        print(f"[renew_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid}) "
              f"kind={RENEW_KIND} group={RENEW_SOURCE_GROUP} tier={RENEW_DEFENSE_TIER}")
        print(f"[renew_wholesale] governor paces host {host_of(ENDPOINT)} (per-host token bucket).")
        print(f"[renew_wholesale] CONCURRENT drain: window={concurrency} pages in flight, "
              f"brand={brand or 'ALL'}. Target = {max_pages} pages (~{max_pages * PAGE_SIZE} cars).")

        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        # CONCURRENT sliding-window drain. Each window fetches up to `concurrency` pages in
        # parallel through the governor (the host bucket paces the aggregate), then the pages are
        # INGESTED sequentially in page order through the single asyncpg connection. A page that
        # errors or comes back empty stops the drain honestly (end of data or a throttle the
        # breaker must catch) — the same stop semantics as coches.net.
        stop = False
        next_page = 1
        while next_page <= max_pages and not stop:
            window = list(range(next_page, min(next_page + concurrency, max_pages + 1)))
            next_page = window[-1] + 1

            results = await asyncio.gather(
                *(fetcher.fetch_page_async(governed_fetch, ENDPOINT, page=p, brand=brand)
                  for p in window),
                return_exceptions=True,
            )

            window_pages: list[tuple[int, list]] = []
            for page, data in zip(window, results):
                if isinstance(data, Exception):
                    fetch_error = str(data)
                    last_http = fetcher.last_status
                    print(f"[renew_wholesale] page {page} fetch failed ({data}); stopping drain honestly.")
                    stop = True
                    break
                block = extract_block(data)
                if block is None:
                    fetch_error = "search block not found in .data loader (route/slice drift?)"
                    print(f"[renew_wholesale] page {page}: search block missing; stopping.")
                    stop = True
                    break
                if stats["declared_full"] is None:
                    stats["declared_full"] = _to_int(block.get("totalElements"))
                items = block.get("data") or []
                if not items:
                    print(f"[renew_wholesale] page {page}: no items; stopping.")
                    stop = True
                    break
                window_pages.append((page, items))

            if window_pages:
                await _ingest_window(conn, geo, platform_ulid, window_pages, seen_ids,
                                     harvested_cageable, stats)
                stats["pages_fetched"] += len(window_pages)
                first_p, last_p = window_pages[0][0], window_pages[-1][0]
                print(f"[renew_wholesale] window pages {first_p}-{last_p}: "
                      f"items={sum(len(it) for _, it in window_pages)} "
                      f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                      f"edges={stats['edges_created']}")

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, RENEW_PLATFORM_RECIPE)
        print(f"[renew_wholesale] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths that all measure
        # "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for renew      (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join   (DB read truth)
        #   harvested_cageable = distinct (dealer_id, deep_link) pulled (harvest truth)
        # The declared full count (5,739) is reported for honesty but is NOT a quorum path
        # (it measures the WHOLE portal, not this slice).
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

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks renew, trips the
        # breaker on a ban, and auto-repairs. OK when >=1 page fetched, no fetch error stopped
        # the drain, and the VAM did not refute.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, RENEW_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, RENEW_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[renew_wholesale] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("RENEW (OEM-VO PORTAL) WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  group / kind          : oem_vo_portal / oem_vo_portal (tier t0_open)")
    print(f"  brand facet           : {stats.get('brand_facet')}")
    print(f"  declared full (source): {stats.get('declared_full')}")
    print(f"  concurrency (window)  : {stats.get('concurrency')} pages in flight")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  dealer items          : {stats['dealer_items']}")
    print(f"  no-dealer skipped     : {stats['no_dealer_skipped']}")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page)")
    print(f"  geo skipped (bad prov): {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for renew = {stats.get('db_edges')})")
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
    parser = argparse.ArgumentParser(description="renew OEM-VO portal wholesale harvester (concurrent es_facet drain)")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"pages to harvest (size={PAGE_SIZE}); default {DEFAULT_MAX_PAGES}")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"pages fetched in parallel per sliding window; default "
                              f"{DEFAULT_CONCURRENCY}. The governor's per-host bucket is the real "
                              f"limiter — this only needs to keep the bucket saturated."))
    parser.add_argument("--brand", type=str, default=None,
                        help="optional Elasticsearch brand facet (e.g. RENAULT, DACIA); omit for full census")
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.pages, args.concurrency, args.brand))
    _print_report(stats)


if __name__ == "__main__":
    main()
