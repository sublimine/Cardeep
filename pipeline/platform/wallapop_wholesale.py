"""wallapop WHOLESALE harvester — the FREE GIANT (~750k cars), end to end.

wallapop (C2C + PRO classifieds) is a verified-FREE Tier-1 marketplace: its public
mobile-app JSON API answers a plain Chrome TLS fingerprint (curl_cffi chrome131) with
NO proxy, NO browser, NO cookie warm-up, NO JS challenge. Verified live 2026-06-12
(docs/architecture/tier1_recipes/wallapop.md): real ES cars + PRO-dealer attribution,
geo honored via explicit lat/long, JWT-chained pagination. is_tier1=TRUE (a giant Tier-1
brand) but defense_tier='t1_soft' (the API host is unwalled to curl_cffi — no active
sensor on the search path). source_group='marketplace_generalist' (C2C + PRO, not a
car-specialist marketplace like coches.net), data_surface='app_api' (the mobile-app
gateway, not an SSR/__NEXT_DATA__ surface).

This module mirrors pipeline.platform.coches_net_wholesale's FAST pattern EXACTLY —
concurrent fetch window + unnest-based BATCH ingest (a handful of bulk SQL statements
per window, not per-row) + governor + health + VAM + platform_listing dual-membership —
and adapts it to wallapop's three realities:

  1. ENUMERATION is keyword/geo-scoped, NOT a flat catalog. The section API returns
     results for a `keywords` term around a lat/long. To sweep broad inventory we iterate
     a set of ~40 common car-brand keywords (toyota, bmw, mercedes, ...) and DEDUPE by
     item id across the whole run. Each keyword is paged by the opaque `next_page` JWT
     (meta.next_page), replayed as &next_page=<jwt>, ~40 items/page, until the chain ends.

  2. SELLER attribution is a SECOND fetch per seller. Each item carries a `user_id`;
     GET /api/v3/users/{id} returns type ("professional"|"normal") + web_slug + micro_name
     + the seller's own location (zip -> INE province). Professional sellers become
     `compraventa` entities (the SELLING DEALER). PRIVATE sellers (type 'normal') become
     PER-SELLER `particular` entities: wallapop exposes a STABLE user_id per seller, so one
     real human = one entity, and a private with N cars is a single multi-car seller
     (cdp_code via particular_platform='wallapop' + particular_seller_id=user_id; see
     PARTICULAR_* below). User lookups are CACHED for the whole run (one HTTP per distinct
     seller, not per listing). Both seller types own their cars + carry the platform_listing
     edge + emit the NEW delta event identically — a buyer never rejects a car for being
     sold by a private, so private inventory is served exactly like a dealer's.

  3. GEO often lacks a clean province on the item. We derive it, in order: the seller's
     own user.location.zip (CP[:2] = INE province, like autocasion), then the item
     location.region2/city via the geo resolver, then the item lat/long via the
     ProvinceGeocoder (nearest labeled point). First hit wins.

Dual membership (identical to coches.net/autocasion):

  wallapop (the marketplace) -> entity, kind='plataforma'  (+ platform_meta, app_api)
  each PRO SELLING DEALER     -> entity, kind='compraventa' (geo-resolved)
  each PRIVATE seller         -> entity, kind='particular'  (per-seller, geo-resolved)
  each CAR                    -> vehicle, OWNED BY its dealer/particular (entity_ulid=owner)
  the car ON the platform     -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the dealer/particular); platform membership is plural (this edge). The
same physical car can carry a wallapop edge AND a coches.net edge without ever changing
its owning dealer.

Engine: GET (search/section + users/{id}) against api.wallapop.com, routed THROUGH the
per-host governor (the same single choke point AS24/coches.net use; api.wallapop.com is
in the governor's JSON_API fast class). The synchronous curl_cffi GETs run in worker
threads so the event loop is never blocked, and no host is fetched faster than its bucket.

Run: python -m pipeline.platform.wallapop_wholesale --target 8000
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import uuid
from dataclasses import dataclass, field

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

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# ---------------------------------------------------------------------------
# wallapop platform identity (00-TIER1-REGISTRY; recipe wallapop.md).
# ---------------------------------------------------------------------------
WP_DOMAIN = "wallapop.com"
WP_WEBSITE = "wallapop.com"
WP_TRADE_NAME = "wallapop"
WP_SOURCE_KEY = "wallapop_wholesale"
# The API host is unwalled to curl_cffi (no active sensor on the search path) -> the
# truthful waf_kind is 'none'. is_tier1 is still TRUE (giant Tier-1 brand) and the
# multi-axis defense_tier is 't1_soft' per the task mandate (a soft-walled giant).
WP_WAF = "none"

# Multi-axis classification the platform entity carries (migrations/0016).
WP_DEFENSE_TIER = "t1_soft"               # soft wall: app API serves curl_cffi, no sensor.
WP_SOURCE_GROUP = "marketplace_generalist"  # C2C + PRO classifieds (not car-specialist).
WP_ROLE = "platform"

# The working request (recipe TL;DR; verified live 2026-06-12).
SEARCH_ENDPOINT = "https://api.wallapop.com/api/v3/search/section"
USER_ENDPOINT = "https://api.wallapop.com/api/v3/users"   # + /{id}
CATEGORY_CARS = "100"                     # category_id 100 = Coches (cars vertical).
_PDP_BASE = "https://es.wallapop.com/item/"  # web_slug -> public PDP url.
_IMPERSONATE = "chrome131"
_TIMEOUT = 40

# A stable tracking id pair (recipe §1.2: any stable numeric id is accepted; no auth).
_MPID = "-3729988211333550697"

# Geo grid: explicit lat/long is HONORED by the server (recipe §0). A small grid of ES
# city centroids x the keyword sweep widens national coverage beyond Madrid. Dedup by item
# id collapses the inevitable cross-centroid overlap. Centroids verified against geo.
_GEO_GRID = [
    ("40.4168", "-3.7038"),   # Madrid
    ("41.3874", "2.1686"),    # Barcelona
    ("39.4699", "-0.3763"),   # Valencia
    ("37.3891", "-5.9845"),   # Sevilla
    ("43.2630", "-2.9350"),   # Bilbao
    ("36.7213", "-4.4214"),   # Malaga
    ("41.6488", "-0.8891"),   # Zaragoza
    ("43.3623", "-8.4115"),   # A Coruna
]

# ~40 common car-brand keywords. The section API is keyword-scoped, so the union over these
# (x the geo grid) approximates broad national inventory; item-id dedup makes the union clean.
_KEYWORDS = [
    "toyota", "bmw", "mercedes", "audi", "seat", "renault", "peugeot", "citroen",
    "opel", "ford", "volkswagen", "kia", "hyundai", "nissan", "fiat", "dacia",
    "volvo", "mazda", "skoda", "honda", "mini", "land rover", "jeep", "suzuki",
    "mitsubishi", "alfa romeo", "lexus", "porsche", "smart", "tesla", "cupra",
    "jaguar", "ds", "chevrolet", "chrysler", "lancia", "subaru", "ssangyong",
    "infiniti", "mg",
]

# Province sentinel '00' = national (same convention as AS24/coches.net/autocasion).
# geo_province has NO '00', so the platform ENTITY stores province_code = NULL; '00'
# lives only inside the cdp_code string (free text, no FK).
PLATFORM_PROVINCE_SENTINEL = "00"

# PRIVATE sellers -> PER-SELLER 'particular' entities. wallapop exposes a STABLE user_id per
# seller (GET /users/{id}), so a private is a REAL identifiable human, not an anonymous bucket:
# one entity per user_id, a private with N cars is one multi-car seller. cdp_code is minted via
# the canonical particular_platform/particular_seller_id path -> 'particular:wallapop:{user_id}'
# -> CDP-ES-{prov}-{hash}. kind='particular', sells_cars=TRUE (the car IS for sale), province
# geo-resolved, kind_source MIRRORS the dealer rows (PARTICULAR_KIND_SOURCE), role left NULL.
# The car, the platform_listing edge and the NEW delta event are caged IDENTICALLY to a dealer's.
PARTICULAR_PLATFORM = "wallapop"          # particular_platform tag for cdp_code (matches user_id source)
PARTICULAR_KIND = "particular"            # entity_kind (migration 0017)
PARTICULAR_KIND_SOURCE = "platform_label" # SAME value the connector uses for its dealer rows
PARTICULAR_DEFAULT_NAME = "Particular"    # trade_name fallback when micro_name/handle is absent
# Legacy: the prior design folded privates into one per-province 'garaje' bucket named
# "Particulares wallapop {prov}". Those 50 obsolete bucket entities are CLEANED UP (PG
# DELETE+INSERT doctrine) after re-harvesting privates per-seller — see cleanup_legacy_buckets.
LEGACY_BUCKET_NAME_PREFIX = "Particulares wallapop"
LEGACY_BUCKET_KIND = "garaje"

DEFAULT_TARGET = 8000          # distinct cars to cage this run (~5k-15k mandated chunk).
PAGE_ITEMS = 40                # the section API serves ~40 items/page (recipe verified).
MAX_PAGES_PER_QUERY = 60       # JWT-chain safety cap per (keyword, centroid) before moving on.


def wallapop_platform_cdp_code() -> str:
    """The wallapop platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:wallapop.com'), province segment '00' (national). Mirrors
    coches_net/autocasion so all platforms mint codes the same way."""
    key = f"domain:{WP_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


def _headers() -> dict:
    """Minimal verified header set (recipe §1.2). A FRESH x-deviceid per call (recipe §6:
    rotate x-deviceid per session); mpid/trackinguserid are stable tracking ids, any value
    accepted; no auth bearer needed for public search."""
    return {
        "accept": "application/json, text/plain, */*",
        "accept-language": "es,es-ES;q=0.9",
        "deviceos": "0", "x-deviceos": "0",
        "x-appversion": "822640",
        "x-deviceid": str(uuid.uuid4()),
        "mpid": _MPID, "trackinguserid": _MPID,
        "referer": "https://es.wallapop.com/",
        "origin": "https://es.wallapop.com",
        "sec-ch-ua-platform": '"Windows"',
    }


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL response — field names inspected live, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class SellerRef:
    """A seller resolved from GET /api/v3/users/{id} (cached per run).

    type 'professional' -> a real selling DEALER (compraventa entity). type 'normal' ->
    a private individual minted as a PER-SELLER 'particular' entity (stable user_id identity).
    The seller's OWN location.zip is the strongest geo anchor (CP[:2] = INE province, like
    autocasion); web_slug is the stable public handle used for cross-source dedup + source_ref."""
    user_id: str
    is_professional: bool
    web_slug: str | None
    name: str | None
    zip: str | None
    city: str | None
    featured: bool


@dataclass
class Vehicle:
    """A car parsed from a single wallapop search item (REAL field map, recipe §2)."""
    deep_link: str
    listing_ref: str           # wallapop native listing id (item.id)
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None           # type_attributes.engine (ASCII-folded label on the wire)
    transmission: str | None   # not in section type_attributes; left None (honest)
    photo_url: str | None
    version: str | None        # type_attributes.version (kept in the NEW-event payload)
    item_lat: float | None     # item location latitude (geocoder fallback)
    item_lon: float | None
    item_region: str | None    # location.region2 (province name candidate)
    item_city: str | None      # location.city (municipality candidate)


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


def _prov_from_cp(zipcode) -> str | None:
    """Spanish postcode's first two digits ARE the INE province code (01..52).
    28070 -> '28' (Madrid). Same rule autocasion uses. Returns None if out of range."""
    if not zipcode:
        return None
    s = "".join(ch for ch in str(zipcode) if ch.isdigit())
    if len(s) < 2:
        return None
    p = s[:2]
    return p if ("01" <= p <= "52") else None


def _first_image(images) -> str | None:
    """item.images[0].urls.big|medium|small (recipe §2)."""
    if not isinstance(images, list) or not images:
        return None
    urls = (images[0] or {}).get("urls") or {}
    return urls.get("big") or urls.get("medium") or urls.get("small")


def parse_seller(user_id: str, payload: dict) -> SellerRef:
    """Parse a SellerRef from a GET /api/v3/users/{id} response (REAL field map)."""
    loc = payload.get("location") or {}
    return SellerRef(
        user_id=user_id,
        is_professional=(payload.get("type") == "professional"),
        web_slug=payload.get("web_slug"),
        name=payload.get("micro_name"),
        zip=loc.get("zip"),
        city=loc.get("city"),
        featured=bool(payload.get("featured")),
    )


def parse_item_vehicle(item: dict) -> Vehicle:
    """Parse the car from a wallapop search item (REAL field map, recipe §2)."""
    price_obj = item.get("price") or {}
    price = _to_float(price_obj.get("amount"))

    ta = item.get("type_attributes") or {}
    year = _to_int(ta.get("year"))
    if year is not None and not (1900 <= year <= 2100):
        year = None
    km = _to_int(ta.get("km"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    web_slug = item.get("web_slug") or ""
    deep_link = (_PDP_BASE + web_slug) if web_slug else ""

    make = ta.get("brand")
    model = ta.get("model")
    title = item.get("title") or " ".join(p for p in (make, model) if p) or None

    loc = item.get("location") or {}
    return Vehicle(
        deep_link=deep_link,
        listing_ref=str(item.get("id") or ""),
        title=title,
        make=make,
        model=model,
        year=year,
        km=km,
        price=price,
        fuel=ta.get("engine"),           # label only (Gasolina/Hibrido/Diesel, ASCII-folded)
        transmission=None,               # not exposed on the section type_attributes
        photo_url=_first_image(item.get("images")),
        version=ta.get("version"),
        item_lat=_to_float(loc.get("latitude")),
        item_lon=_to_float(loc.get("longitude")),
        item_region=loc.get("region2"),
        item_city=loc.get("city"),
    )


# ---------------------------------------------------------------------------
# Fetch: GET (search/section + users/{id}) routed THROUGH the governor.
# ---------------------------------------------------------------------------


class WallapopFetcher:
    """A POOL of fingerprint-coherent curl_cffi GET sessions for the wallapop API.

    Concurrency vs. coherence (identical doctrine to CochesFetcher). A single curl_cffi
    Session is NOT thread-safe, and the governor runs each fetch in its own worker thread
    (asyncio.to_thread). The fix is a small bounded POOL: one Session per concurrency slot,
    leased by index so each in-flight coroutine owns a distinct, never-shared session for
    the duration of its GET. The governor's per-host bucket still bounds the AGGREGATE rate
    across the whole pool, so the pool widens parallelism WITHOUT out-pacing the host.

    Two surfaces share the pool and the host bucket (both api.wallapop.com): the search
    section GET and the per-seller users/{id} GET — so user lookups are paced by the same
    bucket as search, never a second uncontrolled hammer."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch_get(self, url: str, *, params: dict | None = None, slot: int = 0) -> dict:
        """The synchronous GET on pool session `slot` (runs in a worker thread).

        This is the callable handed to governor().wrap_fetch_text: the governor derives the
        host from `url`, waits on the per-host bucket, then runs THIS off the event loop.
        `slot`/`params` ride as kwargs the governor forwards untouched. Raises on a non-200
        so the breaker catches throttling (never masks a challenge/empty body).

        The body is decoded as STRICT UTF-8 (verified live: location.city carries proper
        UTF-8 accents, e.g. 'Leganés' = ...c3 a9...; the section type_attributes.engine is
        already ASCII-folded server-side). A strict decode preserves the accented city/region
        names the geo resolver needs."""
        session = self._sessions[slot]
        resp = session.get(url, params=params, headers=_headers(),
                           impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url}")
        return json.loads(resp.content.decode("utf-8"))

    async def fetch_async(self, governed_fetch, url: str, *, params: dict | None = None) -> dict:
        """Lease a pool slot, fetch THROUGH the governor on that slot, release it.

        `governed_fetch` is governor().wrap_fetch_text(self.fetch_get): the governor derives
        the host, waits on the per-host bucket (the real limiter), then runs the synchronous
        GET off the event loop — passing `slot`/`params` through. The slot lease guarantees
        no two concurrent coroutines ever touch the same session."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, params=params, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer (mirrors coches_net_wholesale: ensure platform, bulk upsert dealer/vehicle,
# link edge, emit delta, all idempotent ON CONFLICT).
# ---------------------------------------------------------------------------

WP_PLATFORM_RECIPE = {
    "version": 1,
    "source": "wallapop.com",
    "scope": "platform-wholesale (api.wallapop.com /api/v3/search/section app JSON API)",
    "engine": "curl_cffi+chrome131_impersonate+json_api(GET)+jwt_pagination",
    "access": ("FREE: public mobile-app JSON API answers a Chrome TLS fingerprint cold "
               "(no proxy, no browser, no cookie warm-up, no JS challenge). is_tier1=TRUE "
               "(giant Tier-1 brand) but defense_tier=t1_soft (API host unwalled to "
               "curl_cffi). No auth bearer for public search."),
    "data_surface": "app_api",
    "surface_intent": "json_api",
    "endpoints": {
        "search": "GET https://api.wallapop.com/api/v3/search/section",
        "seller": "GET https://api.wallapop.com/api/v3/users/{user_id}",
    },
    "request": {
        "search_params": ("keywords=<term>&source=deep_link&category_id=100&search_id=<uuid>"
                          "&latitude=<lat>&longitude=<lon>&order_by=most_relevance"
                          "&section_type=organic_search_results"),
        "headers": ("accept json; accept-language es; deviceos/x-deviceos=0; x-appversion; "
                    "x-deviceid=<uuid per session>; mpid/trackinguserid=stable; "
                    "referer/origin es.wallapop.com; sec-ch-ua-platform Windows"),
        "pagination": "opaque next_page JWT in meta.next_page replayed as &next_page=<jwt>, ~40/page",
    },
    "enumeration": ("keyword sweep (~40 car brands) x ES geo-centroid grid (lat/long HONORED); "
                    "each (keyword,centroid) paged by the meta.next_page JWT until the chain ends; "
                    "dedup by item id across the whole run"),
    "platform_entity": ("kind=plataforma, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=TRUE, defense_tier=t1_soft, source_group=marketplace_generalist, "
                        "role=platform, data_surface=app_api"),
    "attribution": ("per-item user_id -> GET /users/{id} (cached per run): type "
                    "'professional' -> compraventa DEALER; type 'normal' -> PER-SELLER "
                    "'particular' entity (cdp particular:wallapop:{user_id}; one human=one "
                    "entity, sells_cars=TRUE; car+edge+delta caged identically to a dealer)"),
    "dual_membership": "vehicle.entity_ulid=SELLING DEALER/particular; platform_listing edge=platform<->vehicle",
    "geo": ("dealer province from user.location.zip[:2] (INE) -> item region2/city via "
            "GeoResolver -> item lat/long via ProvinceGeocoder (first hit wins)"),
    "field_map": {
        "listing_ref": "item.id (wallapop native listing id)",
        "deep_link": "https://es.wallapop.com/item/ + item.web_slug",
        "make": "item.type_attributes.brand",
        "model": "item.type_attributes.model",
        "year": "item.type_attributes.year",
        "km": "item.type_attributes.km",
        "version": "item.type_attributes.version",
        "price": "item.price.amount (EUR)",
        "fuel": "item.type_attributes.engine (label)",
        "photo_url": "item.images[0].urls.big|medium|small",
        "location": "item.location {region2, city, latitude, longitude, postal_code}",
        "seller": "users/{user_id} {type, web_slug, micro_name, featured, location.zip/city}",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the wallapop platform entity + platform_meta exist.
    Returns the platform entity_ulid. is_tier1=TRUE (giant brand) with the explicit
    multi-axis classification: defense_tier=t1_soft, source_group=marketplace_generalist,
    role=platform (migrations/0016). data_surface='app_api' (schema-valid; the mobile-app
    gateway). website_waf='none' (the API path is unwalled to curl_cffi — truthful)."""
    code = wallapop_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               defense_tier, source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,'plataforma',$3,$3,NULL,$4,$5,TRUE,'active','platform_label',
               $6,$7,$8,$9, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, website_waf = EXCLUDED.website_waf,
               defense_tier = EXCLUDED.defense_tier, source_group = EXCLUDED.source_group,
               role = EXCLUDED.role""",
        eulid, code, WP_TRADE_NAME, WP_WEBSITE, WP_WAF,
        WP_DEFENSE_TIER, WP_SOURCE_GROUP, WP_ROLE, WP_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, WP_SOURCE_KEY, WP_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'app_api',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({
            "search": SEARCH_ENDPOINT, "seller": USER_ENDPOINT + "/{id}",
            "host": host_of(SEARCH_ENDPOINT), "method": "GET", "category_id": CATEGORY_CARS,
            "page_items": PAGE_ITEMS, "surface_intent": "json_api",
            "pagination": "next_page JWT", "engine": "curl_cffi/chrome131_impersonate"}),
        "wallapop")
    return eulid


def _particular_cdp(province_code: str, user_id: str) -> str:
    """A PER-SELLER private 'particular' cdp_code via the canonical generator.

    Identity is the platform's OWN stable seller id (canonical_key
    'particular:wallapop:{user_id}' -> CDP-ES-{prov}-{hash}). One entity per real human, so
    a private with N cars is a single multi-car seller. Deterministic -> re-runs idempotent,
    and a particular never collides with a PRO dealer (distinct canonical_key namespace)."""
    return cdp_code(province_code=province_code,
                    particular_platform=PARTICULAR_PLATFORM,
                    particular_seller_id=user_id)


def cdp_code_dealer(s: SellerRef, province_code: str, muni: str | None) -> str:
    """Mint a PRO dealer's immutable cdp_code via the canonical generator.

    wallapop PRO sellers have no bare domain on this surface -> identity = name + location +
    the stable web_slug (passed via `address` so two distinct PRO sellers that share a name
    in one municipality never collapse to one entity). web_slug falls back to user_id."""
    handle = s.web_slug or s.user_id
    return cdp_code(province_code=province_code, domain=None, name=s.name,
                    municipality_code=muni, address=f"wallapop_user:{handle}")


# The bulk statements — ONE round-trip per table per window (unnest-based multi-row upsert),
# the SAME idempotency the per-row path would use (ON CONFLICT byte-for-byte), so a re-run of
# an already-harvested window adds 0 rows and 0 events. Mirrors coches_net_wholesale.

_BULK_UPSERT_OWNERS = """
INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
        province_code, municipality_code, is_tier1, status, kind_source,
        sells_cars, role, first_discovered_source, last_seen)
SELECT u.entity_ulid, u.cdp_code, u.kind::entity_kind, u.name, u.name,
       u.province_code, u.municipality_code, FALSE, 'active', 'platform_label',
       u.sells_cars, u.role::entity_role, $1, now()
  FROM unnest($2::text[], $3::text[], $4::text[], $5::char(2)[], $6::char(5)[],
              $7::text[], $8::bool[], $9::text[])
       AS u(entity_ulid, cdp_code, name, province_code, municipality_code,
            kind, sells_cars, role)
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


# ---------------------------------------------------------------------------
# Caging: a fully-parsed, geo-anchored, attributed car ready for the bulk window.
# ---------------------------------------------------------------------------


@dataclass
class _CageRow:
    """One fully-resolved car ready for the bulk cage — owner already attributed + geo-anchored,
    before any SQL. Carries everything the batched upserts need so the DB phase touches no
    per-item Python logic, only set-based statements."""
    owner_cdp: str             # dealer cdp OR per-seller particular cdp (the entity_ulid owner)
    owner_kind: str            # 'compraventa' (PRO) | 'particular' (private per-seller)
    owner_name: str | None
    owner_province: str
    owner_muni: str | None
    owner_sells_cars: bool
    owner_role: str | None     # 'standalone_pos' (PRO) | None (particular, per mandate)
    source_ref: str            # web_slug (PRO) | user_id (particular) for entity_source
    is_professional: bool
    featured: bool
    vehicle: Vehicle


@dataclass
class _RunState:
    """Cross-window run state: id dedup, the cageable VAM set, and the per-run seller cache."""
    seen_ids: set = field(default_factory=set)
    harvested_cageable: set = field(default_factory=set)  # distinct (owner_cdp, deep_link)
    seller_cache: dict = field(default_factory=dict)      # user_id -> SellerRef | None


def _resolve_province(s: SellerRef, v: Vehicle, geo: GeoResolver,
                      geocoder: ProvinceGeocoder) -> tuple[str | None, str | None]:
    """Derive (province_code, municipality_code), first hit wins:
      1. seller's own user.location.zip[:2] (INE province) + item/seller city -> muni
      2. item location.region2/city via the GeoResolver
      3. item lat/long via the ProvinceGeocoder (nearest labeled point)
    Returns (None, None) only when no signal resolves to a valid INE province."""
    # 1) seller zip -> province (strongest: the dealer's own registered address).
    prov = _prov_from_cp(s.zip)
    if prov:
        muni = geo.municipality_code(prov, s.city) or geo.municipality_code(prov, v.item_city)
        return prov, muni
    # 2) item region2 (province NAME) -> province; then city -> muni.
    prov = geo.province_code(v.item_region)
    if prov:
        muni = geo.municipality_code(prov, v.item_city) or geo.municipality_code(prov, s.city)
        return prov, muni
    # 2b) globally-unique city name -> (province, muni) in one shot.
    gp, gm = geo.resolve_city_global(v.item_city)
    if gp:
        return gp, gm
    # 3) item lat/long -> nearest labeled province (free geocoder).
    prov = geocoder.nearest_province(v.item_lat, v.item_lon)
    if prov and prov.isdigit() and "01" <= prov <= "52":
        muni = geo.municipality_code(prov, v.item_city)
        return prov, muni
    return None, None


async def _resolve_seller(fetcher: WallapopFetcher, governed_fetch, state: _RunState,
                          user_id: str, stats: dict) -> SellerRef | None:
    """Resolve a seller via GET /users/{id}, CACHED per run (one HTTP per distinct seller).
    Returns None if the lookup fails (the item is then skipped — no unattributed cars)."""
    if user_id in state.seller_cache:
        return state.seller_cache[user_id]
    try:
        payload = await fetcher.fetch_async(governed_fetch, f"{USER_ENDPOINT}/{user_id}")
        seller = parse_seller(user_id, payload)
        stats["seller_lookups"] += 1
    except Exception:  # noqa: BLE001 — one failed seller lookup never sinks the drain.
        seller = None
        stats["seller_lookup_errors"] += 1
    state.seller_cache[user_id] = seller
    return seller


async def _build_cage(items: list, fetcher: WallapopFetcher, governed_fetch, geo: GeoResolver,
                      geocoder: ProvinceGeocoder, state: _RunState, stats: dict) -> list:
    """Parse + attribute + geo-resolve every NEW item in a window -> list[_CageRow].

    This is the per-item gate (cross-query id dedup, seller attribution, geo skip), done
    BEFORE any cage SQL so the DB phase is purely set-based. Seller lookups (cached) are the
    only network here; they run sequentially per item but hit the per-run cache, so a busy
    PRO dealer with 200 cars costs ONE users/{id} call, not 200."""
    rows: list[_CageRow] = []
    for item in items:
        stats["items_seen"] += 1
        item_id = str(item.get("id") or "")
        if not item_id or item_id in state.seen_ids:
            stats["dup_ids_collapsed"] += 1 if item_id else 0
            continue
        state.seen_ids.add(item_id)

        # car vertical guard: category_id 100 only (the search is already scoped, but be strict).
        if str(item.get("category_id") or "") not in ("100", ""):
            continue

        v = parse_item_vehicle(item)
        if not v.deep_link or not (v.make or v.title):
            continue

        user_id = str(item.get("user_id") or "")
        if not user_id:
            stats["geo_skipped"] += 1
            continue
        seller = await _resolve_seller(fetcher, governed_fetch, state, user_id, stats)
        if seller is None:
            stats["geo_skipped"] += 1
            continue

        prov, muni = _resolve_province(seller, v, geo, geocoder)
        if not prov or not (prov.isdigit() and "01" <= prov <= "52"):
            stats["geo_skipped"] += 1
            continue

        if seller.is_professional:
            stats["pro_items"] += 1
            owner_cdp = cdp_code_dealer(seller, prov, muni)
            cage = _CageRow(
                owner_cdp=owner_cdp, owner_kind="compraventa", owner_name=seller.name,
                owner_province=prov, owner_muni=muni, owner_sells_cars=True,
                owner_role="standalone_pos",
                source_ref=(seller.web_slug or seller.user_id),
                is_professional=True, featured=seller.featured, vehicle=v)
        else:
            stats["private_items"] += 1
            # private -> PER-SELLER 'particular' entity (stable user_id identity). One real
            # human = one entity; a private with N cars is one multi-car seller. The car IS
            # for sale -> sells_cars=TRUE. role left NULL (per mandate); kind_source mirrors
            # the dealer rows. trade_name = the seller's micro_name/handle, else "Particular".
            owner_cdp = _particular_cdp(prov, seller.user_id)
            owner_name = seller.name or seller.web_slug or PARTICULAR_DEFAULT_NAME
            cage = _CageRow(
                owner_cdp=owner_cdp, owner_kind=PARTICULAR_KIND,
                owner_name=owner_name,
                owner_province=prov, owner_muni=muni, owner_sells_cars=True,
                owner_role=None, source_ref=seller.user_id,
                is_professional=False, featured=seller.featured, vehicle=v)

        state.harvested_cageable.add((owner_cdp, v.deep_link))
        rows.append(cage)
    return rows


async def _ingest_window(conn: asyncpg.Connection, platform_ulid: str, cage: list,
                         stats: dict) -> None:
    """BULK-ingest a parsed/attributed window in ONE transaction with set-based SQL.

    Replaces a per-row drain with ONE round-trip per table per window (unnest multi-row
    upserts). Delta/VAM/platform_listing semantics are preserved EXACTLY: same ON CONFLICT
    idempotency, same cageable truth, same NEW-event rule (emitted only for genuinely new
    vehicles). A re-run of an already-harvested window adds 0 rows and 0 events.

    Phases (single transaction): dedup owners by cdp -> bulk-upsert owners + sources ->
    split vehicles existing/new (one SELECT) -> bulk-touch existing + bulk-insert new ->
    confirm landed -> bulk-upsert edges (RETURNING counts new) -> bulk-insert NEW events."""
    if not cage:
        return

    async with conn.transaction():
        # ---- OWNERS: dedup by cdp within the window, bulk-upsert, resolve ulids.
        owners: dict[str, _CageRow] = {}
        for r in cage:
            owners.setdefault(r.owner_cdp, r)  # first occurrence wins (deterministic)
        o_cdps = list(owners.keys())
        o_ulids = [ulid() for _ in o_cdps]
        o_names = [owners[c].owner_name for c in o_cdps]
        o_provs = [owners[c].owner_province for c in o_cdps]
        o_munis = [owners[c].owner_muni for c in o_cdps]
        o_kinds = [owners[c].owner_kind for c in o_cdps]
        o_sells = [owners[c].owner_sells_cars for c in o_cdps]
        o_roles = [owners[c].owner_role for c in o_cdps]
        o_refs = [owners[c].source_ref for c in o_cdps]
        await conn.execute(_BULK_UPSERT_OWNERS, WP_SOURCE_KEY, o_ulids, o_cdps, o_names,
                           o_provs, o_munis, o_kinds, o_sells, o_roles)
        await conn.execute(_BULK_UPSERT_OWNER_SOURCES, o_cdps, o_refs, WP_SOURCE_KEY)
        cdp_to_ulid: dict[str, str] = {
            row["cdp_code"]: row["entity_ulid"]
            for row in await conn.fetch(
                "SELECT cdp_code, entity_ulid FROM entity WHERE cdp_code = ANY($1::text[])",
                o_cdps)
        }

        # ---- attach resolved owner_ulid; dedup cars by (owner_ulid, deep_link) within window.
        cars: dict[tuple[str, str], _CageRow] = {}
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

        confirmed_new: list[tuple[str, str]] = []
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
            for k in new_keys:
                real = landed.get(k)
                if real is not None and real == vehicle_ulid_for[k]:
                    confirmed_new.append(k)
                elif real is not None:
                    vehicle_ulid_for[k] = real     # lost the race; adopt their ulid
                else:
                    row = await conn.fetchrow(
                        "SELECT vehicle_ulid FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2",
                        k[0], k[1])
                    if row is not None:
                        vehicle_ulid_for[k] = row["vehicle_ulid"]

        stats["cars_caged"] += len(car_keys)
        stats["new_cars"] += len(confirmed_new)

        # ---- EDGES: one batched upsert; RETURNING (xmax=0) counts genuinely new edges.
        e_vehicles = [vehicle_ulid_for[k] for k in car_keys]
        e_urls = [cars[k].vehicle.deep_link for k in car_keys]
        e_refs = [cars[k].vehicle.listing_ref for k in car_keys]
        e_prices = [cars[k].vehicle.price for k in car_keys]
        edge_rows = await conn.fetch(_BULK_UPSERT_EDGES, e_vehicles, e_urls, e_refs,
                                     e_prices, platform_ulid)
        stats["edges_created"] += sum(1 for row in edge_rows if row["inserted"])

        # ---- NEW delta events — only for genuinely new vehicles (version kept in payload).
        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                r = cars[k]
                v = r.vehicle
                payload = {"price": v.price, "title": v.title, "platform": WP_TRADE_NAME,
                           "seller_type": "professional" if r.is_professional else "private"}
                if v.version:
                    payload["version"] = v.version
                if r.featured:
                    payload["featured_dealer"] = True
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities, ev_payloads)
            stats["new_events"] += len(confirmed_new)


# ---------------------------------------------------------------------------
# Legacy cleanup: retire the obsolete per-province 'garaje' buckets (PG DELETE+INSERT
# doctrine). A car under a bucket is SUPERSEDED once the SAME listing (deep_link) is now
# owned by a per-seller kind='particular' entity. We VAM-VERIFY the re-point FIRST, then
# delete ONLY the superseded bucket cars + their now-redundant platform_listing edges +
# any bucket entity left with zero cars. A bucket car NOT yet re-pointed (this bounded run
# didn't re-harvest its listing) is LEFT UNTOUCHED — never orphaned, never a car-count drop;
# a later full drain re-points it and a later cleanup retires it. Idempotent + reversible.
# ---------------------------------------------------------------------------

async def cleanup_legacy_buckets(conn: asyncpg.Connection, platform_ulid: str,
                                 stats: dict) -> None:
    """Retire superseded legacy 'garaje' buckets after the per-seller re-harvest.

    SAFETY (mandate): (1) re-point VERIFY — only a bucket car whose deep_link is now owned by
    a kind='particular' entity is deletable; (2) NO professional/compraventa car is ever
    touched (the filter is strictly kind='garaje' + the legacy name prefix); (3) total
    wallapop cars MUST NOT drop — every deleted bucket car has a live per-seller twin, so the
    distinct-listing count is preserved. All within ONE transaction.

    Records bucket_* stats: how many buckets existed, how many cars were superseded (deletable),
    how many were NOT yet re-pointed (left intact this run), and the final bucket count."""
    # Bucket inventory BEFORE (truth snapshot).
    buckets_before = await conn.fetchval(
        "SELECT count(*) FROM entity WHERE kind=$1 AND trade_name LIKE $2",
        LEGACY_BUCKET_KIND, LEGACY_BUCKET_NAME_PREFIX + "%")
    bucket_cars_before = await conn.fetchval(
        """SELECT count(*) FROM vehicle v JOIN entity e ON e.entity_ulid=v.entity_ulid
           WHERE e.kind=$1 AND e.trade_name LIKE $2""",
        LEGACY_BUCKET_KIND, LEGACY_BUCKET_NAME_PREFIX + "%")
    stats["bucket_entities_before"] = buckets_before
    stats["bucket_cars_before"] = bucket_cars_before
    if not buckets_before:
        stats["bucket_entities_after"] = 0
        stats["bucket_cars_superseded"] = 0
        stats["bucket_cars_not_repointed"] = 0
        stats["bucket_entities_deleted"] = 0
        return

    async with conn.transaction():
        # SUPERSEDED = bucket cars whose deep_link is now owned by a kind='particular' entity
        # (the per-seller re-point). This is the re-point VERIFY: a bucket car only qualifies
        # for deletion if its real listing demonstrably survives under a particular owner.
        superseded = await conn.fetch(
            """SELECT bv.vehicle_ulid
                 FROM vehicle bv
                 JOIN entity be ON be.entity_ulid = bv.entity_ulid
                WHERE be.kind = $1 AND be.trade_name LIKE $2
                  AND EXISTS (
                    SELECT 1 FROM vehicle pv
                      JOIN entity pe ON pe.entity_ulid = pv.entity_ulid
                     WHERE pe.kind = 'particular'
                       AND pv.deep_link = bv.deep_link)""",
            LEGACY_BUCKET_KIND, LEGACY_BUCKET_NAME_PREFIX + "%")
        superseded_ulids = [r["vehicle_ulid"] for r in superseded]
        stats["bucket_cars_superseded"] = len(superseded_ulids)
        stats["bucket_cars_not_repointed"] = bucket_cars_before - len(superseded_ulids)

        if superseded_ulids:
            # DELETE the superseded bucket VEHICLES. platform_listing + vehicle_event rows on
            # those vehicles CASCADE away (FK ON DELETE CASCADE, verified). Only the superseded
            # bucket car (its own vehicle_ulid) is removed — the per-seller twin is a DISTINCT
            # vehicle_ulid with its own live edge, so the distinct-listing total holds (no drop).
            await conn.execute(
                "DELETE FROM vehicle WHERE vehicle_ulid = ANY($1::text[])",
                superseded_ulids)

        # DELETE bucket entities now holding ZERO cars (fully superseded). A bucket that still
        # owns un-repointed cars is KEPT so its remaining real listings stay served. The
        # entity delete CASCADES to entity_source/platform_meta/entity_alias (verified FKs).
        deleted_entities = await conn.fetch(
            """DELETE FROM entity e
                WHERE e.kind = $1 AND e.trade_name LIKE $2
                  AND NOT EXISTS (SELECT 1 FROM vehicle v WHERE v.entity_ulid = e.entity_ulid)
                RETURNING e.entity_ulid""",
            LEGACY_BUCKET_KIND, LEGACY_BUCKET_NAME_PREFIX + "%")
        stats["bucket_entities_deleted"] = len(deleted_entities)

    stats["bucket_entities_after"] = await conn.fetchval(
        "SELECT count(*) FROM entity WHERE kind=$1 AND trade_name LIKE $2",
        LEGACY_BUCKET_KIND, LEGACY_BUCKET_NAME_PREFIX + "%")
    print(f"[wallapop_wholesale] legacy cleanup: buckets {buckets_before}->"
          f"{stats['bucket_entities_after']}; superseded bucket cars deleted="
          f"{stats['bucket_cars_superseded']}; left intact (not yet re-pointed)="
          f"{stats['bucket_cars_not_repointed']}; bucket entities removed="
          f"{stats['bucket_entities_deleted']}.")


# ---------------------------------------------------------------------------
# Orchestration: keyword sweep x geo grid, JWT-chained, concurrent seller-resolve windows.
# ---------------------------------------------------------------------------

DEFAULT_CONCURRENCY = 12   # in-flight GETs per window; the JSON_API governor bucket is the limiter.


async def _drain_query(fetcher: WallapopFetcher, governed_fetch, conn, platform_ulid,
                       geo, geocoder, state, stats, *, keywords: str, lat: str, lon: str,
                       target: int, order_by: str = "most_relevance",
                       max_pages: int = MAX_PAGES_PER_QUERY) -> tuple[bool, str | None, int | None]:
    """Drain ONE query via the JWT chain until it ends, the page cap is hit, or the global
    target is reached. Each page is parsed+attributed+geo-resolved then BULK-ingested.
    Returns (target_reached, fetch_error, last_http).

    Two modes share this loop:
      * keyword+centroid (order_by=most_relevance) — the supplement sweep.
      * FLAT (keywords='', no lat/lon, order_by=newest) — the primary enumerator that walks
        the whole UNFILTERED cars vertical (~651k) by the next_page JWT chain (verified live).
    keywords/lat/lon are only sent when non-empty so the flat pass stays global."""
    params = {
        "source": "deep_link", "category_id": CATEGORY_CARS,
        "search_id": str(uuid.uuid4()),
        "order_by": order_by, "section_type": "organic_search_results",
    }
    if keywords:
        params["keywords"] = keywords
    if lat and lon:
        params["latitude"] = lat
        params["longitude"] = lon
    next_jwt: str | None = None
    for _page in range(max_pages):
        q = {"next_page": next_jwt} if next_jwt else params
        try:
            data = await fetcher.fetch_async(governed_fetch, SEARCH_ENDPOINT, params=q)
        except Exception as e:  # noqa: BLE001
            return False, str(e), fetcher.last_status
        stats["pages_fetched"] += 1
        section = (data.get("data") or {}).get("section") or {}
        items = section.get("items") or []
        if not items:
            break
        cage = await _build_cage(items, fetcher, governed_fetch, geo, geocoder, state, stats)
        await _ingest_window(conn, platform_ulid, cage, stats)
        if len(state.harvested_cageable) >= target:
            return True, None, None
        next_jwt = (data.get("meta") or {}).get("next_page")
        if not next_jwt:
            break
    return False, None, None


async def harvest(target: int = DEFAULT_TARGET, concurrency: int = DEFAULT_CONCURRENCY) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    fetcher = WallapopFetcher(pool_size=concurrency)
    stats = {
        "pages_fetched": 0, "items_seen": 0, "pro_items": 0, "private_items": 0,
        "geo_skipped": 0, "dup_ids_collapsed": 0, "seller_lookups": 0,
        "seller_lookup_errors": 0, "new_dealers": 0, "cars_caged": 0, "new_cars": 0,
        "edges_created": 0, "new_events": 0, "dealers_distinct": 0,
        "declared_full": 750000, "concurrency": concurrency, "target": target,
    }
    state = _RunState()

    # S-HEALTH gate: if wallapop's breaker is OPEN (a recent ban/throttle still cooling),
    # skip the drain gracefully — the API keeps serving the last snapshot ("no se cae").
    if await is_open(conn, WP_SOURCE_KEY):
        print(f"[wallapop_wholesale] breaker OPEN for {WP_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, API still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": WP_SOURCE_KEY}

    # GOVERNOR: the single per-host choke point. EVERY GET (search + users/{id}) passes
    # through api.wallapop.com's token bucket (JSON_API class: 12 req/s steady, burst 24),
    # off the event loop. No matter how many requests are in flight, the host is never
    # hammered: the bucket is the limiter, not Python's awaits.
    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_get)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        geocoder = await ProvinceGeocoder.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = wallapop_platform_cdp_code()
        print(f"[wallapop_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid})")
        print(f"[wallapop_wholesale] governor paces host {host_of(SEARCH_ENDPOINT)} "
              f"(JSON_API token bucket); geocoder has {geocoder.size()} labeled points.")
        print(f"[wallapop_wholesale] sweep: {len(_KEYWORDS)} keywords x {len(_GEO_GRID)} centroids, "
              f"JWT-chained, target={target} distinct cars (concurrency window={concurrency}).")

        owners_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        # Whole-platform car-count snapshot BEFORE the run: the final guard proves the cleanup
        # never dropped a single distinct wallapop listing (re-point, not orphan).
        cars_before = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)
        stats["wallapop_cars_before"] = cars_before

        target_reached = False

        # PRIMARY enumerator: a single FLAT order_by=newest cursor over the UNFILTERED cars
        # vertical (no keyword, no geo) walks the whole live catalog (~651k) by the next_page
        # JWT chain — verified live (40/page, distinct, chains cleanly). The keyword x centroid
        # sweep below stays as a SUPPLEMENT for any tail the flat cursor depth-caps.
        flat_pages = max(MAX_PAGES_PER_QUERY, (target // 40) + 200)
        freached, ferr, fhttp = await _drain_query(
            fetcher, governed_fetch, conn, platform_ulid, geo, geocoder, state, stats,
            keywords="", lat="", lon="", target=target, order_by="newest", max_pages=flat_pages)
        if freached:
            target_reached = True
        elif ferr:
            fetch_error, last_http = ferr, fhttp
        print(f"[wallapop_wholesale] flat newest-cursor pass done: "
              f"{len(state.harvested_cageable)} distinct cars caged (target {target}).")

        for kw in _KEYWORDS:
            if target_reached:
                break
            for lat, lon in _GEO_GRID:
                reached, ferr, fhttp = await _drain_query(
                    fetcher, governed_fetch, conn, platform_ulid, geo, geocoder, state,
                    stats, keywords=kw, lat=lat, lon=lon, target=target)
                if ferr is not None:
                    fetch_error, last_http = ferr, fhttp
                    print(f"[wallapop_wholesale] query '{kw}'@{lat},{lon} failed ({ferr}); "
                          f"recording + stopping drain honestly.")
                    target_reached = True
                    break
                if reached:
                    target_reached = True
                    break
            print(f"[wallapop_wholesale] after '{kw}': caged={stats['cars_caged']} "
                  f"distinct={len(state.harvested_cageable)} edges={stats['edges_created']} "
                  f"pro={stats['pro_items']} priv={stats['private_items']} "
                  f"sellers={stats['seller_lookups']}")

        owners_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(owners_after - owners_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               JOIN entity d ON d.entity_ulid = v.entity_ulid
               WHERE pl.platform_entity_ulid = $1 AND d.kind='compraventa'""", platform_ulid)
        stats["particulars_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               JOIN entity d ON d.entity_ulid = v.entity_ulid
               WHERE pl.platform_entity_ulid = $1 AND d.kind='particular'""", platform_ulid)

        # LEGACY CLEANUP (PG DELETE+INSERT doctrine): retire the obsolete per-province 'garaje'
        # buckets now that privates are caged PER-SELLER. Re-point is VAM-verified inside; only
        # superseded bucket cars (whose listing survives under a particular) are removed — total
        # wallapop cars never drop, no professional car is touched. Idempotent across re-runs.
        await cleanup_legacy_buckets(conn, platform_ulid, stats)

        recipe_path = write_recipe(platform_code, WP_PLATFORM_RECIPE)
        print(f"[wallapop_wholesale] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths that all
        # measure "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for wallapop      (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join      (DB read truth)
        #   harvested_cageable = distinct (owner, deep_link) pulled        (harvest truth)
        # The declared full (~750k) is reported for honesty, NOT a quorum path.
        db_edges = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)
        db_join_vehicles = await conn.fetchval(
            """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               JOIN entity d ON d.entity_ulid = v.entity_ulid
               WHERE pl.platform_entity_ulid=$1""", platform_ulid)
        harvested_cageable_n = len(state.harvested_cageable)
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
        stats["harvested_distinct_ids"] = len(state.seen_ids)
        stats["distinct_sellers"] = len(state.seller_cache)
        stats["platform_code"] = platform_code
        stats["platform_ulid"] = platform_ulid
        stats["recipe_path"] = str(recipe_path)

        # NO-DROP GUARD: total wallapop distinct listings (= edges, post-cleanup) MUST be >=
        # the pre-run count. The cleanup only removed bucket cars that have a live per-seller
        # twin, so the distinct-listing total can only GROW (new harvest) — never shrink.
        stats["wallapop_cars_after"] = db_edges
        stats["cars_did_not_drop"] = db_edges >= stats.get("wallapop_cars_before", 0)
        if not stats["cars_did_not_drop"]:
            # A real regression: refuse to call the run OK so the breaker/repair records it.
            verdict = "REFUTED"
            stats["verdict"] = verdict
            print(f"[wallapop_wholesale] FATAL no-drop guard: cars dropped "
                  f"{stats.get('wallapop_cars_before')} -> {db_edges}.")

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks wallapop,
        # trips the breaker on a ban, and auto-repairs. OK when >=1 page fetched, no fetch
        # error stopped the drain, and the VAM did not refute.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, WP_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, WP_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[wallapop_wholesale] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("WALLAPOP WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  declared full (source): ~{stats.get('declared_full')} (NOT harvested — chunk)")
    print(f"  target (distinct cars): {stats.get('target')}")
    print(f"  concurrency (window)  : {stats.get('concurrency')} in-flight GETs")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  distinct sellers      : {stats.get('distinct_sellers')} "
          f"({stats['seller_lookups']} lookups, {stats['seller_lookup_errors']} errors)")
    print(f"  PRO items             : {stats['pro_items']}")
    print(f"  private items         : {stats['private_items']} (-> per-seller particular entities)")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-query)")
    print(f"  geo/attr skipped      : {stats['geo_skipped']}")
    print(f"  PRO dealers attributed: {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  particulars attributed: {stats.get('particulars_distinct')} distinct (per-seller)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for wallapop = {stats.get('db_edges')})")
    print(f"  NEW delta events      : {stats['new_events']}")
    print("  --- legacy garaje bucket cleanup (PG DELETE+INSERT) ---")
    print(f"  buckets before/after  : {stats.get('bucket_entities_before')} -> {stats.get('bucket_entities_after')}"
          f" ({stats.get('bucket_entities_deleted')} removed)")
    print(f"  bucket cars superseded: {stats.get('bucket_cars_superseded')} deleted "
          f"(re-pointed to per-seller); {stats.get('bucket_cars_not_repointed')} left intact")
    print(f"  wallapop cars before  : {stats.get('wallapop_cars_before')}")
    print(f"  wallapop cars after   : {stats.get('wallapop_cars_after')} "
          f"(no-drop guard: {'OK' if stats.get('cars_did_not_drop') else 'FAILED'})")
    print("  --- VAM count quorum (like-with-like, this slice) ---")
    print(f"  harvested_cageable    : {stats.get('harvested_cageable')}")
    print(f"  db_edges              : {stats.get('db_edges')}")
    print(f"  db_join_vehicles      : {stats.get('db_join_vehicles')}")
    print(f"  VAM verdict           : {stats.get('verdict')}")
    print(f"  health status         : {stats.get('health_status')} / breaker {stats.get('breaker_state')}")
    print(f"  recipe                : {stats.get('recipe_path')}")
    print("=" * 64)


def main() -> None:
    parser = argparse.ArgumentParser(description="wallapop wholesale harvester (keyword sweep, JWT-chained, concurrent)")
    parser.add_argument("--target", type=int, default=DEFAULT_TARGET,
                        help=f"distinct cars to cage this run; default {DEFAULT_TARGET} (~5k-15k mandated chunk)")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"in-flight GETs per window; default {DEFAULT_CONCURRENCY}. The "
                              f"governor's JSON_API per-host bucket is the real limiter."))
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.target, args.concurrency))
    _print_report(stats)


if __name__ == "__main__":
    main()
