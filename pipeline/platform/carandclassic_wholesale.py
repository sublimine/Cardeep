"""Car & Classic WHOLESALE harvester — the classic/collector marketplace, end to end.

Car & Classic (carandclassic.com) is Europe's largest classic/collector-car vertical
(pan-EU, Laravel + Inertia.js + Vue SSR, fronted by Cloudflare). The public site is
Cloudflare-walled (is_tier1=TRUE) but SERVES cleanly to a Chrome TLS fingerprint
(curl_cffi/chrome131) with NO proxy, NO browser, NO cookie warm-up — defense_tier
t1_soft. Verified live 2026-06-13.

The data surface is the Inertia.js page payload embedded in every SSR HTML response:

    <script data-page="app" type="application/json">{"component":"search/index/Page",
      "props":{...,"searchResults":{"data":[<car>...],"pagination":{...}}}}</script>

That `searchResults.data` array is a fully-structured JSON record per car (id, slug,
url, title, price{value(cents),currency}, make, year, attributes{mileage,fuelType,
transmissionType,engineSize,gears,colour}, location{countryCode,region,town}, type,
isSold). Pagination is a clean `?page=N`; `searchResults.pagination.total` declares the
result count. The ES surface is `?vehicle_type=cars&country=ES` — 618 classic cars
LOCATED IN SPAIN (verified live 2026-06-13), 59-60 per page, 11 pages.

OWNER DECISION (2026-06-13): classic/collector marketplaces are IN SCOPE and MERGED into
the normal market as kind='compraventa' — NO special type, NO new source_group, like any
other used-car seller. This connector caches the Spanish classic-car inventory exactly
that way.

CAGING — source-truthful, owner-aligned. Car & Classic ANONYMISES the selling dealer on
every accessible surface: the search payload carries NO seller; the PDP's `listing.seller`
returns clientId/businessName/shortName/sellerWebsite ALL null even for dealers (verified
live across 14 PDPs 2026-06-13 — only sellerType + town + listingsCount are exposed, never
a stable per-dealer id). There is therefore NO stable per-dealer identity to mint, so we
DO NOT fabricate one. Following the proven coches.net pattern for anonymised sellers, every
ES classic car is owned by ONE synthetic 'compraventa' bucket entity PER PROVINCE
(canonical_key 'name:compraventas clasicos car&classic|p{province}'), geo-resolved from the
car's location.town. A car whose town cannot be geo-anchored (mojibake/missing) is bucketed
under the '00' national fallback so NO real car is ever dropped. This mirrors the template's
caging exactly — car + platform_listing edge + NEW delta event — and respects the owner's
order: the marketplace's classic inventory is served as compraventa, merged, no new type.

This module mirrors pipeline.platform.coches_net_wholesale EXACTLY (same dual-membership
model, same caging, same governor/health/VAM wiring) so a THIRD-kind marketplace flows
through the one architecture, not a fork of it:

  Car & Classic (the marketplace) -> entity, kind='plataforma'  (+ platform_meta)
  each per-province compraventa    -> entity, kind='compraventa' (geo-resolved bucket)
  each CAR                         -> vehicle, OWNED BY its bucket (entity_ulid=owner)
  the car ON the platform          -> platform_listing edge (platform <-> vehicle)

Run: python -m pipeline.platform.carandclassic_wholesale --pages 11
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import html
import json
import re
import sys
from dataclasses import dataclass

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
import os

DSN = os.environ.get("CARDEEP_DSN", DSN)

# ---------------------------------------------------------------------------
# Car & Classic platform identity. The public site is Cloudflare-fronted ->
# is_tier1=TRUE; the SSR HTML (Inertia payload) serves to chrome131 unwalled.
# ---------------------------------------------------------------------------
CC_DOMAIN = "carandclassic.com"
CC_WEBSITE = "carandclassic.com"
CC_TRADE_NAME = "Car & Classic"
CC_SOURCE_KEY = "carandclassic_wholesale"
CC_WAF = "cloudflare"

# The working request (verified live 2026-06-13). The ES car-stock surface.
_PDP_BASE = "https://www.carandclassic.com"
SEARCH_URL = "https://www.carandclassic.com/es/buscar"
SEARCH_PARAMS = "vehicle_type=cars&country=ES"  # ES classic CARS only
_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}
_IMPERSONATE = "chrome131"
_TIMEOUT = 45

# Province sentinel '00' = national fallback (same convention as coches.net). geo_province
# has NO '00', so the platform ENTITY + the '00' fallback bucket store province_code=NULL;
# '00' lives only inside the cdp_code string (free text, no FK).
PLATFORM_PROVINCE_SENTINEL = "00"

# Inertia payload regex — the one structured surface. Anchored on the exact script tag.
_INERTIA_RE = re.compile(
    r'<script data-page="app" type="application/json">(.*?)</script>', re.S)

# ES is 11 pages at ~59/page (618 cars). Default drains the whole ES surface.
DEFAULT_MAX_PAGES = 12
# pages fetched in parallel per sliding window. The governor's per-host bucket is the
# real limiter; this only needs to keep the bucket saturated.
DEFAULT_CONCURRENCY = 6

# Per-province 'compraventa' bucket. Car & Classic anonymises the dealer (clientId/
# businessName null even on the PDP), so there is NO stable per-dealer id to mint — we
# bucket the ES classic inventory by province as compraventa (owner order: merged, no new
# type). The bucket MIRRORS a normal platform dealer row (is_tier1=FALSE, source_group/role
# NULL, kind_source='platform_label', sells_cars=TRUE) and differs only in being a province
# aggregate of an anonymised-seller surface.
BUCKET_KIND = "compraventa"
BUCKET_NAME_PREFIX = "Compraventas clasicos Car&Classic"
BUCKET_PROVINCE_FALLBACK = "00"

# Car & Classic exposes fuel/transmission in English -> normalise to Spanish for coherence
# with every other connector (coches.net/AS24 serve Spanish labels).
_FUEL = {
    "petrol": "Gasolina", "gasoline": "Gasolina", "diesel": "Diésel",
    "electric": "Eléctrico", "hybrid": "Híbrido", "lpg": "GLP", "gas": "GLP",
}
_TRANSMISSION = {"manual": "Manual", "automatic": "Automático", "auto": "Automático"}


def cc_platform_cdp_code() -> str:
    """The Car & Classic platform's immutable cdp_code. Built from the bare domain
    identity (canonical_key 'domain:carandclassic.com'), province segment '00' (national).
    Mirrors coches_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{CC_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL Inertia searchResults.data record).
# ---------------------------------------------------------------------------


@dataclass
class Vehicle:
    """A car parsed from a single Car & Classic searchResults.data item."""
    deep_link: str
    listing_ref: str           # Car & Classic native ad id (item.id)
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    town: str | None           # location.town — the geo anchor for the province bucket


def _to_int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _clean_town(town: str | None) -> str | None:
    """Normalise a free-text town from the source into a geo-resolvable name.

    Two source defects are fixed without ever fabricating a location:
      1) the U+FFFD replacement char the source emits in some names (origin mojibake:
         'Val�ncia', 'San Sebasti�n') is stripped so the accent-insensitive GeoResolver
         still matches 'Valencia'/'San Sebastian'.
      2) free-text suffixes the source appends ('Lorca, Spain', 'Aspe/Alicante',
         'Archena - Murcia') are trimmed to the leading municipality token so the city
         resolves; the trailing province/country is dropped (the GeoResolver re-derives the
         province from the municipality). Only a clean cut on the first separator — never a
         guess.
    A name that collapses to empty (pure mojibake/blank) returns None -> the car falls to
    the '00' national bucket, never dropped."""
    if not town:
        return None
    cleaned = town.replace("�", "").strip()
    if not cleaned:
        return None
    # Drop a trailing ', Spain' / ', España' the source sometimes appends.
    cleaned = re.sub(r",\s*(?:spain|espa[nñ]a)\s*$", "", cleaned, flags=re.IGNORECASE).strip()
    # Split on the first municipality<->region separator ( , / - ) and keep the head token.
    # 'Aspe/Alicante' -> 'Aspe'; 'Archena - Murcia' -> 'Archena'; 'Lorca, Spain' -> 'Lorca'.
    head = re.split(r"\s*[,/]\s*|\s+-\s+", cleaned, maxsplit=1)[0].strip()
    return head or cleaned or None


def _first_image(images) -> str | None:
    if not isinstance(images, list):
        return None
    for img in images:
        if isinstance(img, dict) and img.get("url"):
            url = img["url"]
            # images[].url is a relative /uploads/... path served from assets.carandclassic.com
            if url.startswith("/"):
                return "https://assets.carandclassic.com" + url
            return url
    return None


def _model_from_title(title: str | None, make: str | None) -> str | None:
    """Car & Classic titles are '{year} {make} {model...}'. Derive the model by stripping a
    leading 4-digit year and the make. Best-effort (the source has no discrete model field on
    this surface); None when nothing remains."""
    if not title:
        return None
    rest = re.sub(r"^\s*\d{4}\s+", "", title)
    if make:
        rest = re.sub(rf"^\s*{re.escape(make)}\s+", "", rest, flags=re.IGNORECASE)
    rest = rest.strip()
    return rest or None


def parse_item_vehicle(item: dict) -> Vehicle | None:
    """Parse the car from a Car & Classic searchResults.data item (REAL field map).
    Returns None for a sold car (isSold) or one with no usable URL."""
    if item.get("isSold"):
        return None
    url = item.get("url") or ""
    if not url:
        return None
    deep_link = (_PDP_BASE + url) if url.startswith("/") else url

    price_obj = item.get("price") or {}
    raw_price = price_obj.get("value")
    price = None
    if raw_price is not None:
        try:
            # price.value is in MINOR units (cents): 1900000 -> 19000.00 EUR (verified live).
            price = float(raw_price) / 100.0
        except (TypeError, ValueError):
            price = None

    year = _to_int(item.get("year"))
    if year is not None and not (1900 <= year <= 2100):
        year = None

    attrs = item.get("attributes") or {}
    mileage = attrs.get("mileage") or {}
    km = _to_int(mileage.get("value"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    make = item.get("make")
    title = item.get("title")
    loc = item.get("location") or {}

    return Vehicle(
        deep_link=deep_link,
        listing_ref=str(item.get("id") or ""),
        title=title,
        make=make,
        model=_model_from_title(title, make),
        year=year,
        km=km,
        price=price,
        fuel=_FUEL.get((attrs.get("fuelType") or "").lower()),
        transmission=_TRANSMISSION.get((attrs.get("transmissionType") or "").lower()),
        photo_url=_first_image(item.get("images")),
        town=_clean_town(loc.get("town")),
    )


# ---------------------------------------------------------------------------
# Fetch: a GET routed THROUGH the governor (same per-host choke point as coches.net),
# returning the parsed Inertia searchResults block. A pool of fingerprint-coherent
# curl_cffi sessions, one per concurrency slot (a single session is not thread-safe).
# ---------------------------------------------------------------------------


class CCFetcher:
    """A POOL of fingerprint-coherent curl_cffi GET sessions for the Car & Classic SSR
    surface. One Session per concurrency slot (a shared session races under the governor's
    to_thread fetch); each its own Chrome fingerprint + cookie jar. The governor's per-host
    bucket bounds the AGGREGATE rate across the pool, so the pool widens parallelism WITHOUT
    out-pacing the host."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    @staticmethod
    def _page_url(page: int) -> str:
        return f"{SEARCH_URL}?{SEARCH_PARAMS}&page={page}"

    def fetch_page(self, url: str, *, page: int = 1, slot: int = 0) -> dict:
        """The synchronous GET on pool session `slot` (runs in a worker thread).

        Returns the parsed Inertia `searchResults` dict {data:[...], pagination:{...}}.
        Raises on a non-200 or a missing/garbled Inertia payload so the breaker catches a
        challenge/empty body (never masks a throttle). The HTML is decoded as UTF-8
        explicitly so accented town/title names survive curl_cffi's encoding guess."""
        session = self._sessions[slot]
        resp = session.get(self._page_url(page), headers=_HEADERS,
                           impersonate=_IMPERSONATE, timeout=_TIMEOUT, allow_redirects=True)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url} (page {page})")
        body = resp.content.decode("utf-8", errors="replace")
        m = _INERTIA_RE.search(body)
        if not m:
            raise RuntimeError(f"no Inertia payload on {url} (page {page}) — surface changed/walled")
        # The payload is HTML-attribute-escaped JSON; unescape entities before parsing.
        raw = html.unescape(m.group(1))
        try:
            page_obj = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Inertia JSON parse failed on page {page}: {exc}") from exc
        props = page_obj.get("props") or {}
        sr = props.get("searchResults") or {}
        return {"data": sr.get("data") or [], "pagination": sr.get("pagination") or {}}

    async def fetch_page_async(self, governed_fetch, url: str, *, page: int) -> dict:
        """Lease a pool slot, fetch `page` THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, page=page, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer (mirrors coches_net_wholesale: ensure platform, bulk-upsert province buckets +
# vehicles + edges + delta, all idempotent ON CONFLICT).
# ---------------------------------------------------------------------------

CC_PLATFORM_RECIPE = {
    "version": 1,
    "source": "carandclassic.com",
    "scope": "platform-wholesale (Inertia searchResults JSON in SSR HTML)",
    "engine": "curl_cffi+chrome131_impersonate+inertia_json",
    "access": ("OPEN SSR HTML (Chrome TLS fingerprint; no proxy, no browser, no cookie "
               "warm-up). Public site Cloudflare-fronted -> is_tier1=true; serves to "
               "chrome131 unwalled (defense_tier t1_soft)."),
    "data_surface": "next_data",  # schema-valid literal for an embedded SSR JSON payload
    "surface_intent": "inertia_json",
    "endpoint": "GET https://www.carandclassic.com/es/buscar?vehicle_type=cars&country=ES&page=N",
    "request": {
        "headers": "Accept text/html, Accept-Language es-ES",
        "surface": ("<script data-page='app' type='application/json'> Inertia payload; "
                    "props.searchResults.data[] = per-car record"),
    },
    "enumeration": "page=1..N; props.searchResults.pagination.total/last_page drive the full drain (ES=618, 11 pages)",
    "platform_entity": "kind=plataforma, province_code=NULL (sentinel 00 in cdp_code only), is_tier1=TRUE",
    "dual_membership": "vehicle.entity_ulid=per-province compraventa BUCKET; platform_listing edge=platform<->vehicle",
    "caging": ("source anonymises the dealer (clientId/businessName null even on PDP), so NO "
               "stable per-dealer id -> per-province 'compraventa' bucket (canonical_key "
               "'name:compraventas clasicos car&classic|p{province}', '00' national fallback); "
               "owner order: classic marketplace MERGED as compraventa, no new type. car+edge+delta caged"),
    "field_map": {
        "deep_link": "item.url (prefixed with https://www.carandclassic.com)",
        "listing_ref": "item.id (native ad id)",
        "title": "item.title ('{year} {make} {model}')",
        "make": "item.make",
        "model": "derived from title (strip year+make)",
        "year": "item.year",
        "km": "item.attributes.mileage.value",
        "price": "item.price.value / 100 (minor units -> EUR)",
        "fuel": "item.attributes.fuelType (en->es)",
        "transmission": "item.attributes.transmissionType (en->es)",
        "photo_url": "item.images[0].url (prefixed with https://assets.carandclassic.com)",
        "location": "item.location {countryCode=ES, town}",
        "sold_filter": "item.isSold -> skipped",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the Car & Classic platform entity + platform_meta exist.
    Returns the platform entity_ulid. is_tier1=TRUE (Cloudflare), source_group=
    marketplace_motor (a car-specialist marketplace), data_surface='next_data' (the
    schema-valid literal for an embedded SSR JSON payload)."""
    code = cc_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,'plataforma',$3,$3,NULL,$4,$5,TRUE,'active','platform_label',
               'marketplace_motor','platform',$6, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, website_waf = EXCLUDED.website_waf,
               source_group = EXCLUDED.source_group, role = EXCLUDED.role""",
        eulid, code, CC_TRADE_NAME, CC_WEBSITE, CC_WAF, CC_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, CC_SOURCE_KEY, CC_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like)
           VALUES ($1,'next_data',$2::jsonb,FALSE,FALSE)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail""",
        eulid, json.dumps({"endpoint": SEARCH_URL, "host": host_of(SEARCH_URL),
                           "method": "GET", "params": SEARCH_PARAMS,
                           "surface_intent": "inertia_json",
                           "engine": "curl_cffi/chrome131_impersonate"}))
    return eulid


def cdp_code_bucket(province_code: str) -> str:
    """Mint the per-province compraventa bucket cdp_code via the canonical name+province
    generator (canonical_key 'name:compraventas clasicos car&classic|p{province}'). The
    province IS the only identity the anonymised surface exposes, so the bucket is
    deterministic over (platform, province) and idempotent across re-runs. The '00' fallback
    bucket uses province '00' in the cdp_code string but stores province_code=NULL on the
    entity (no geo_province FK)."""
    return cdp_code(province_code=province_code, name=BUCKET_NAME_PREFIX)


# ---------------------------------------------------------------------------
# Bulk statements — ONE round-trip per table per window (unnest-based multi-row upsert).
# Byte-for-byte the same idempotency the coches.net path uses; a re-run adds 0 rows/events.
# ---------------------------------------------------------------------------

_BULK_UPSERT_BUCKETS = """
INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
        province_code, is_tier1, status, kind_source,
        source_group, role, sells_cars, first_discovered_source, last_seen)
SELECT u.entity_ulid, u.cdp_code, 'compraventa'::entity_kind, u.name, u.name,
       u.province_code, FALSE, 'active', 'platform_label',
       NULL, NULL, TRUE, $5, now()
  FROM unnest($1::text[], $2::text[], $3::text[], $4::char(2)[])
       AS u(entity_ulid, cdp_code, name, province_code)
ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()
"""

_BULK_UPSERT_BUCKET_SOURCES = """
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
        listing_ref, platform_price, status, segment, first_seen, last_seen)
SELECT u.vehicle_ulid, $5, u.listing_url, u.listing_ref, u.platform_price,
       'listed', 'used', now(), now()
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


def _province_name(prov: str | None, prov_names: dict[str, str]) -> str:
    """The human province label for a bucket's trade_name suffix. 'ES' for the '00' bucket."""
    if not prov:
        return "ES"
    return prov_names.get(prov, prov)


@dataclass
class _CageRow:
    """One fully-parsed, geo-anchored car ready for the bulk cage."""
    owner_cdp: str
    owner_name: str | None
    owner_province: str | None    # INE code; NULL only for the '00' fallback bucket
    source_ref: str               # 'cc:{province}' — the bucket's source attribution
    vehicle: Vehicle


def _parse_window(items_by_page: list[tuple[int, list]], geo: GeoResolver,
                  prov_names: dict[str, str], seen_ids: set, harvested_cageable: set,
                  stats: dict) -> list[_CageRow]:
    """Parse + geo-resolve every item across the window IN PAGE ORDER — pure CPU, no SQL.

    Every ES classic car is caged into its per-province 'compraventa' bucket. The province
    comes from geo-resolving location.town nationally (resolve_city_global, unambiguous-only);
    a town that cannot be anchored (mojibake/missing/ambiguous) falls to the '00' national
    bucket so NO real car is ever dropped. seen_ids dedups the same native id across pages
    (stable-sort hazard guard). harvested_cageable holds distinct (owner_cdp, deep_link)
    pairs for the VAM harvest-truth path."""
    rows: list[_CageRow] = []
    for _page, items in items_by_page:
        for item in items:
            stats["items_seen"] += 1
            item_id = str(item.get("id") or "")
            if item_id and item_id in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue
            if item_id:
                seen_ids.add(item_id)

            if item.get("isSold"):
                stats["sold_skipped"] += 1
                continue
            v = parse_item_vehicle(item)
            if v is None or not v.deep_link:
                continue

            # Province from town (national unambiguous resolve). None -> '00' national bucket.
            prov, _muni = geo.resolve_city_global(v.town)
            if prov is None:
                stats["town_unresolved"] += 1
            bucket_prov = prov or BUCKET_PROVINCE_FALLBACK
            owner_cdp = cdp_code_bucket(bucket_prov)
            pname = _province_name(prov, prov_names)
            harvested_cageable.add((owner_cdp, v.deep_link))
            rows.append(_CageRow(
                owner_cdp=owner_cdp,
                owner_name=f"{BUCKET_NAME_PREFIX} {pname}",
                # entity.province_code is a geo_province FK -> NULL for the '00' bucket
                # (the '00' lives only in the cdp_code string, same as the platform entity).
                owner_province=prov,
                source_ref=f"cc:{bucket_prov}",
                vehicle=v))
    return rows


async def _ingest_window(conn: asyncpg.Connection, geo: GeoResolver,
                         prov_names: dict[str, str], platform_ulid: str,
                         items_by_page: list[tuple[int, list]], seen_ids: set,
                         harvested_cageable: set, stats: dict) -> None:
    """BULK-ingest a whole concurrent page-window in ONE transaction with set-based SQL.
    Mirrors coches_net_wholesale._ingest_window exactly: same ON CONFLICT idempotency, same
    cageable truth, same NEW-event rule (emitted only for genuinely new vehicles)."""
    cage = _parse_window(items_by_page, geo, prov_names, seen_ids, harvested_cageable, stats)
    if not cage:
        return

    async with conn.transaction():
        # ---- (2) OWNERS (per-province compraventa buckets): dedup by cdp_code, bulk-upsert.
        owners: dict[str, _CageRow] = {}
        for r in cage:
            owners.setdefault(r.owner_cdp, r)
        d_ulids = [ulid() for _ in owners]
        d_cdps = list(owners.keys())
        d_names = [owners[c].owner_name for c in d_cdps]
        d_provs = [owners[c].owner_province for c in d_cdps]
        d_refs = [owners[c].source_ref for c in d_cdps]
        await conn.execute(_BULK_UPSERT_BUCKETS, d_ulids, d_cdps, d_names, d_provs,
                           CC_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_BUCKET_SOURCES, d_cdps, d_refs, CC_SOURCE_KEY)
        cdp_to_ulid: dict[str, str] = {
            row["cdp_code"]: row["entity_ulid"]
            for row in await conn.fetch(
                "SELECT cdp_code, entity_ulid FROM entity "
                "WHERE cdp_code = ANY($1::text[])", d_cdps)
        }

        # ---- attach owner_ulid; dedup cars within the window by (owner_ulid, deep_link).
        cars: dict[tuple[str, str], _CageRow] = {}
        for r in cage:
            du = cdp_to_ulid.get(r.owner_cdp)
            if du is None:
                continue
            key = (du, r.vehicle.deep_link)
            if key not in cars:
                cars[key] = r

        # ---- (3) VEHICLES: split existing vs new (one SELECT), touch existing, insert new.
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
                payload = {"price": v.price, "title": v.title, "platform": CC_TRADE_NAME}
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities,
                               ev_payloads)
            stats["new_events"] += len(confirmed_new)


async def harvest(max_pages: int = DEFAULT_MAX_PAGES,
                  concurrency: int = DEFAULT_CONCURRENCY,
                  start_page: int = 1) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    fetcher = CCFetcher(pool_size=concurrency)
    stats = {
        "pages_fetched": 0, "items_seen": 0, "sold_skipped": 0,
        "town_unresolved": 0, "new_buckets": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "buckets_distinct": 0,
        "concurrency": concurrency,
    }
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: skip gracefully if the breaker is OPEN.
    if await is_open(conn, CC_SOURCE_KEY):
        print(f"[carandclassic_wholesale] breaker OPEN for {CC_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, API still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": CC_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        prov_names = {r["code"]: r["name"]
                      for r in await conn.fetch("SELECT code, name FROM geo_province")}
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = cc_platform_cdp_code()
        print(f"[carandclassic_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid})")
        print(f"[carandclassic_wholesale] governor paces host {host_of(SEARCH_URL)} (per-host token bucket).")
        print(f"[carandclassic_wholesale] CONCURRENT drain: window={concurrency} pages in flight. "
              f"Target = {max_pages} pages (ES classic cars).")

        seen_ids: set[str] = set()
        buckets_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa' "
            "AND first_discovered_source=$1", CC_SOURCE_KEY)}

        stop = False
        next_page = max(1, start_page)
        while next_page <= max_pages and not stop:
            window = list(range(next_page, min(next_page + concurrency, max_pages + 1)))
            next_page = window[-1] + 1

            results = await asyncio.gather(
                *(fetcher.fetch_page_async(governed_fetch, SEARCH_URL, page=p)
                  for p in window),
                return_exceptions=True,
            )

            window_pages: list[tuple[int, list]] = []
            for page, data in zip(window, results):
                if isinstance(data, Exception):
                    fetch_error = str(data)
                    last_http = fetcher.last_status
                    print(f"[carandclassic_wholesale] page {page} fetch failed ({data}); stopping drain honestly.")
                    stop = True
                    break
                pag = data.get("pagination") or {}
                if stats["declared_full"] is None:
                    stats["declared_full"] = _to_int(pag.get("total"))
                items = data.get("data") or []
                if not items:
                    print(f"[carandclassic_wholesale] page {page}: no items; stopping.")
                    stop = True
                    break
                window_pages.append((page, items))

            if window_pages:
                await _ingest_window(conn, geo, prov_names, platform_ulid, window_pages,
                                     seen_ids, harvested_cageable, stats)
                stats["pages_fetched"] += len(window_pages)
                first_p, last_p = window_pages[0][0], window_pages[-1][0]
                print(f"[carandclassic_wholesale] window pages {first_p}-{last_p}: "
                      f"items={sum(len(it) for _, it in window_pages)} "
                      f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                      f"edges={stats['edges_created']}")

        buckets_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa' "
            "AND first_discovered_source=$1", CC_SOURCE_KEY)}
        stats["new_buckets"] = len(buckets_after - buckets_before)
        stats["buckets_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, CC_PLATFORM_RECIPE)
        print(f"[carandclassic_wholesale] recipe written: {recipe_path}")

        # VAM count quorum — THREE orthogonal like-with-like paths (this slice):
        db_edges = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)
        db_join_vehicles = await conn.fetchval(
            """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
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

        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, CC_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, CC_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[carandclassic_wholesale] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("CAR & CLASSIC WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  declared full (source): {stats.get('declared_full')} (ES classic cars)")
    print(f"  concurrency (window)  : {stats.get('concurrency')} pages in flight")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  sold skipped          : {stats['sold_skipped']}")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page)")
    print(f"  town unresolved       : {stats['town_unresolved']} (-> '00' national bucket; never dropped)")
    print(f"  province buckets      : {stats['buckets_distinct']} distinct "
          f"({stats['new_buckets']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for Car & Classic = {stats.get('db_edges')})")
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
    """Windows consoles default to cp1252, which cannot encode accented car titles
    (Híbrido, Diésel). Reconfigure stdout/stderr to UTF-8 so progress logging can never
    abort the harvest. Idempotent."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass


def main() -> None:
    _force_utf8_stdout()
    parser = argparse.ArgumentParser(description="Car & Classic wholesale harvester (Inertia-JSON drain)")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"pages to harvest; default {DEFAULT_MAX_PAGES} (ES surface is ~11 pages)")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"pages fetched in parallel per sliding window; default "
                              f"{DEFAULT_CONCURRENCY}. The governor's per-host bucket is the real limiter."))
    parser.add_argument("--start-page", type=int, default=1,
                        help="first page to fetch (skip already-harvested pages for a top-up)")
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.pages, args.concurrency, args.start_page))
    _print_report(stats)


if __name__ == "__main__":
    main()
