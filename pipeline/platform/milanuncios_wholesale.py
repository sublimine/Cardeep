"""milanuncios WHOLESALE harvester — the Adevinta GENERALIST giant, end to end.

milanuncios (Adevinta Spain) is a verified-FREE Tier-1 marketplace: its SPA's own JSON
data layer answers a plain Chrome TLS fingerprint (curl_cffi chrome131) with NO proxy,
NO browser, NO reese84, NO auth, NO cookie warm-up. Verified live 2026-06-12
(docs/architecture/tier1_recipes/milanuncios_datalayer.md): real ES cars, first-class
dealer attribution (authorId/authorName), per-item professional/private flag, exact
per-cell counts. is_tier1=TRUE (a giant Tier-1 brand) but defense_tier='t1_soft' (the
search gateway is unwalled to curl_cffi — no active sensor on the read path).
source_group='marketplace_generalist' (C2C + PRO classifieds, NOT a car-specialist
marketplace like coches.net), data_surface='internal_api' (the SPA's REST gateway),
platform_meta.family='adevinta' (co-defended with the Adevinta siblings).

This module mirrors pipeline.platform.coches_net_wholesale's FAST pattern EXACTLY —
platform entity + per-car cage (dealer upsert + vehicle owned-by-dealer + platform_listing
edge + NEW delta event + versioned recipe + VAM verdict), idempotent ON CONFLICT, every
fetch through governor().wrap_fetch_text, is_open breaker gate + record_run + auto_repair,
and the unnest-based BATCH ingest (a handful of bulk SQL statements per window, not per
row). It adapts that proven machinery to milanuncios's three realities:

  1. ENUMERATION is FACET PARTITION (the coches_net_facet strategy, here over a GET API).
     A single filtered view is hard-capped at a 10,000-doc Elasticsearch window (offset/
     sort/cursor all capped — verified). The catalog is reached by sharding `province`
     (INE 1..52). The API publishes EXACT per-cell counts: pagination.totalHits.relation
     =="eq" means value is the exact count (<10k, fully offset-drainable); =="gte" (value
     10000) means >10k -> sub-shard that province by price bands until every band is "eq",
     then drain each. Province × price-band is a gap-free, count-provable partition.

  2. ATTRIBUTION is FIRST-CLASS on the item (no second fetch, unlike wallapop). Each ad
     carries authorId + authorName + a `type` discriminator ("professional"|"private").
     BOTH kinds are caged as sellable inventory (a private car a buyer can purchase is real
     supply): professional ads become `compraventa` entities (the SELLING DEALER); private
     ads become PER-SELLER `particular` entities keyed on the stable authorId
     (canonical_key 'particular:milanuncios:{authorId}'), so one human listing N cars
     collapses to ONE multi-car particular. Each owner's cars carry the same platform_listing
     edge. Only an ad with NO authorId is unattributed_skipped (it cannot be keyed to an owner).

  3. STRINGS are latin-1 MOJIBAKE over the wire (h<bad>brido=híbrido, a<bad>o=año). Every
     human string is repaired with s.encode("latin-1").decode("utf-8") before it is caged.

Dual membership (identical to coches.net/wallapop):

  milanuncios (the marketplace) -> entity, kind='plataforma'  (+ platform_meta, family=adevinta)
  each PRO SELLING DEALER        -> entity, kind='compraventa' (geo-resolved)
  each PRIVATE SELLER (per human) -> entity, kind='particular'  (geo-resolved, authorId-keyed)
  each CAR                       -> vehicle, OWNED BY its owner  (entity_ulid=dealer|particular)
  the car ON the platform        -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the dealer OR the particular); platform membership is plural (this
edge). The same physical car can carry a milanuncios edge AND a coches.net edge without
changing its owner.

Engine: GET against searchapi.gw.milanuncios.com, routed THROUGH the per-host governor
(the same single choke point AS24/coches.net/wallapop use; the host joins the JSON_API
fast class). The synchronous curl_cffi GETs run in worker threads so the event loop is
never blocked, and no host is fetched faster than its bucket.

Run: python -m pipeline.platform.milanuncios_wholesale --pages 100
     python -m pipeline.platform.milanuncios_wholesale --provinces 42,28 --limit 100
"""
from __future__ import annotations

import argparse
import sys
import asyncio
import hashlib
import json
import os
import time
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

DSN = os.environ.get("CARDEEP_DSN",
                     "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# ---------------------------------------------------------------------------
# milanuncios platform identity (00-TIER1-REGISTRY; recipe milanuncios_datalayer.md).
# ---------------------------------------------------------------------------
MN_DOMAIN = "milanuncios.com"
MN_WEBSITE = "milanuncios.com"
MN_TRADE_NAME = "milanuncios"
MN_SOURCE_KEY = "milanuncios_wholesale"
# The search gateway is unwalled to curl_cffi (no active sensor on the read path) -> the
# truthful waf_kind is 'none'. is_tier1 is still TRUE (giant Tier-1 brand); the multi-axis
# defense_tier is 't1_soft' per the task mandate (a soft-walled generalist giant).
MN_WAF = "none"

# Multi-axis classification the platform entity carries (migrations/0016).
MN_DEFENSE_TIER = "t1_soft"                  # soft wall: search API serves curl_cffi cold.
MN_SOURCE_GROUP = "marketplace_generalist"   # C2C + PRO classifieds (not car-specialist).
MN_ROLE = "platform"
MN_FAMILY = "adevinta"                        # co-defended Adevinta sibling (platform_meta).

# The working request (recipe TL;DR; verified live 2026-06-12).
ENDPOINT = "https://searchapi.gw.milanuncios.com/v4/classifieds"
CATEGORY_CARS = "13"          # category=13 = Coches (cars vertical).
TRANSACTION_SUPPLY = "supply"  # transaction=supply = for-sale ads.
_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "es-ES,es;q=0.9",
    "origin": "https://www.milanuncios.com",
    "referer": "https://www.milanuncios.com/",
    "sec-ch-ua-platform": '"Windows"',
}
_PDP_BASE = "https://www.milanuncios.com"  # ad.url is a relative PDP path (…-{adId}.htm).
_IMG_BASE = "https://"                       # photos imageUrls lack a scheme on the wire.
_IMPERSONATE = "chrome131"
_TIMEOUT = 40

# Province sentinel '00' = national (same convention as AS24/coches.net/wallapop). geo_province
# has NO '00', so the platform ENTITY stores province_code = NULL; '00' lives only inside the
# cdp_code string (free text, no FK). We never pollute geo_province with it.
PLATFORM_PROVINCE_SENTINEL = "00"

# Page size: the API honors limit up to 100 (101+ silently degrades to a 30-ad fallback).
PAGE_SIZE = 100

# The hard Elasticsearch window per filtered view: offset+limit must stay <= 10,000 or the
# response collapses to a degenerate page-1 reset. Every partition cell is sized <=10k so
# offset paging exhausts it; this is the per-cell drain ceiling.
ES_WINDOW_CAP = 10_000

# A province whose totalHits is "gte"/10000 (>10k) gets price-band sub-partitioned. The 6
# metro provinces that need it (verified live): Alicante=3, Barcelona=8, Madrid=28,
# Malaga=29, Sevilla=41, Valencia=46. Each band returns "eq" and is fully offset-drainable.
PRICE_BANDS: tuple[tuple[int | None, int | None], ...] = (
    (None, 1000),
    (1000, 2000),
    (2000, 3000),
    (3000, 5000),
    (5000, 8000),
    (8000, 12000),
    (12000, 18000),
    (18000, 25000),
    (25000, 40000),
    (40000, 70000),
    (70000, 150000),
    (150000, None),
)

SPANISH_PROVINCES = tuple(range(1, 53))  # INE province ids 1..52.

# ---------------------------------------------------------------------------
# SEGMENTS — milanuncios has ONE flat supply index, not separate segment backends.
# Every sellable car (used, km0, seminuevo, "a estrenar", pro, private) is an ordinary
# transaction=supply ad INSIDE this one ES index; "segments" are per-item FACET slices, not
# separate products (verified 2026-06-13, docs/architecture/segments/milanuncios.md). So the
# segment flag is an OPTIONAL FACET NARROWING of every partition cell — the SAME cage contract,
# only the per-cell query params change. `all` (default) = the whole index = legacy behavior =
# full coverage. The narrower segments exist only for targeted re-drains.
#
# Ignored-param trap (verified): condition/vehicleState/isNew/km0 query params are SILENTLY
# IGNORED by the API. The REAL facet axes that "take" are kilometersFrom/kilometersTo (km0 and
# "a estrenar" are km-band slices, NOT a condition enum). milanuncios has NO new-car catalog/
# configurator and NO renting product on its coches vertical, so those segments do not exist.
SEGMENTS: dict[str, dict[str, str]] = {
    "all": {},                                  # the whole flat supply index (full coverage).
    "vo": {"kilometersFrom": "1000"},           # used / ocasión (excludes near-new km<1000).
    "km0": {"kilometersTo": "1000"},            # km0 / seminuevo / near-new (km<=1000).
    "vn": {"kilometersTo": "100"},              # "nuevo / a estrenar" lowest-km (no true catalog).
    "catalog": {"kilometersTo": "100"},         # alias of vn — milanuncios has no separate catalog.
    "renting": None,                            # not a milanuncios product (handled: clean exit).
}
DEFAULT_SEGMENT = "all"

# transmission raw value (uppercase EN token on the wire) -> human label.
_TRANSMISSION = {"AUTOMATIC": "Automático", "MANUAL": "Manual"}
# fuel raw value (lowercase EN slug on the wire) -> human label (the formatted value is
# mojibake; the raw slug is clean ASCII, so we map it to a stable Spanish label).
_FUEL = {
    "gasoline": "Gasolina", "petrol": "Gasolina", "diesel": "Diésel",
    "hybrid": "Híbrido", "plugin_hybrid": "Híbrido enchufable",
    "electric": "Eléctrico", "lpg": "GLP", "cng": "GNC", "gas": "Gas",
}


def _demojibake(s):
    """milanuncios serves human strings as latin-1 mojibake (the bytes are UTF-8 read as
    latin-1). Re-encode latin-1 then decode UTF-8 to restore accents. Non-str / already-clean
    values pass through unharmed (the round-trip is a no-op on pure ASCII)."""
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def milanuncios_platform_cdp_code() -> str:
    """The milanuncios platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:milanuncios.com'), province segment '00' (national). Mirrors
    coches_net/wallapop so all platforms mint codes the same way."""
    key = f"domain:{MN_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL response — field names inspected live, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class DealerRef:
    """The selling dealer parsed from a single ad's author + location.

    milanuncios attribution is first-class on the ad: authorId is the stable per-seller id
    (the cross-source dedup key + source_ref), authorName the trade name. Geo comes from the
    ad's location (province.id = INE province code; city.name resolves the municipality)."""
    author_id: str
    name: str | None
    province_code: str | None
    city: str | None


@dataclass
class ParticularRef:
    """A PRIVATE individual seller parsed from a single ad's author + location.

    The MODEL is PER-SELLER: milanuncios exposes a STABLE authorId on private ads too, so a
    real human who lists N cars collapses to ONE particular entity (canonical_key
    'particular:milanuncios:{authorId}'), exactly like the dealer path keys on authorId. A
    private car IS sellable inventory a buyer can purchase, so it is CAGED, not skipped —
    owned by its particular + carrying a platform_listing edge identical to a dealer car. Geo
    comes from the ad's location (province.id = INE code; city.name resolves the municipality)."""
    author_id: str
    name: str | None
    province_code: str | None
    city: str | None


@dataclass
class Vehicle:
    """A car parsed from a single milanuncios ad (REAL field map, recipe §3)."""
    deep_link: str
    listing_ref: str           # milanuncios native ad id (ad.id)
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    previous_price: float | None  # price-drop signal (ad.previousPrice)


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


def _prov2(province_id) -> str | None:
    """milanuncios location.province.id IS the INE province code (28=Madrid, 42=Soria —
    verified live). Zero-pad to 2 digits; reject out-of-range."""
    n = _to_int(province_id)
    if n is None or not (1 <= n <= 52):
        return None
    return f"{n:02d}"


def _attrs(ad: dict) -> dict:
    """Flatten ad.attributes[] -> {raw_field_name: raw_value}. Each entry is
    {field:{raw,formatted}, value:{raw,formatted}}; the raw field name is a clean ASCII
    slug (kilometers/year/fuel/transmission/hp), the raw value is the machine value."""
    out: dict[str, str] = {}
    for a in ad.get("attributes") or []:
        if not isinstance(a, dict):
            continue
        field = (a.get("field") or {}).get("raw")
        val = (a.get("value") or {}).get("raw")
        if field is not None:
            out[field] = val
    return out


def _first_photo(ad_id: str, photos_by_id: dict) -> str | None:
    """Resolve the first image for an ad from the top-level photos[] (joined by adId).
    imageUrls lack a scheme on the wire ('images.milanuncios.com/...') -> prefix https://."""
    urls = photos_by_id.get(ad_id)
    if not urls:
        return None
    raw = urls[0]
    if not isinstance(raw, str) or not raw:
        return None
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    return _IMG_BASE + raw


def parse_ad_dealer(ad: dict) -> DealerRef | None:
    """Parse the SELLING DEALER from a PROFESSIONAL ad's author + location.

    Returns a DealerRef only for ad.type == 'professional' WITH an authorId; otherwise None
    (a private ad is handled by parse_ad_particular, NOT skipped). Geo comes from the ad's
    location."""
    if ad.get("type") != "professional":
        return None
    author_id = ad.get("authorId")
    if not author_id:
        return None
    loc = ad.get("location") or {}
    prov = _prov2(((loc.get("province") or {}).get("id")))
    city = _demojibake((loc.get("city") or {}).get("name"))
    return DealerRef(
        author_id=str(author_id),
        name=_demojibake(ad.get("authorName")),
        province_code=prov,
        city=city,
    )


def parse_ad_particular(ad: dict) -> ParticularRef | None:
    """Parse the PRIVATE individual seller from a non-professional ad's author + location.

    Returns a ParticularRef for ad.type != 'professional' WITH an authorId (the stable
    per-seller id that collapses one human's N cars into ONE particular entity); None if the
    ad has no authorId to anchor identity (cannot cage what cannot be keyed). The private car
    is sellable inventory and IS caged owned-by the particular — no longer skipped."""
    if ad.get("type") == "professional":
        return None
    author_id = ad.get("authorId")
    if not author_id:
        return None
    loc = ad.get("location") or {}
    prov = _prov2(((loc.get("province") or {}).get("id")))
    city = _demojibake((loc.get("city") or {}).get("name"))
    return ParticularRef(
        author_id=str(author_id),
        name=_demojibake(ad.get("authorName")),
        province_code=prov,
        city=city,
    )


def parse_ad_vehicle(ad: dict, photos_by_id: dict) -> Vehicle:
    """Parse the car from a milanuncios ad (REAL field map). Strings demojibake'd."""
    at = _attrs(ad)

    price_obj = ad.get("price") or {}
    cash = price_obj.get("cash") or {}
    price = _to_float(cash.get("value"))
    prev = _to_float(ad.get("previousPrice"))

    year = _to_int(at.get("year"))
    if year is not None and not (1900 <= year <= 2100):
        year = None
    km = _to_int(at.get("kilometers"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    url = ad.get("url") or ""
    deep_link = (_PDP_BASE + url) if url.startswith("/") else url

    ad_id = str(ad.get("id") or "")
    title = _demojibake(ad.get("title"))

    fuel_raw = at.get("fuel")
    fuel = _FUEL.get(fuel_raw, _demojibake(fuel_raw)) if fuel_raw else None
    trans_raw = at.get("transmission")
    transmission = _TRANSMISSION.get(trans_raw, _demojibake(trans_raw)) if trans_raw else None

    return Vehicle(
        deep_link=deep_link,
        listing_ref=ad_id,
        title=title,
        make=None,   # milanuncios ads carry make only inside categories/title (kept in title)
        model=None,
        year=year,
        km=km,
        price=price,
        fuel=fuel,
        transmission=transmission,
        photo_url=_first_photo(ad_id, photos_by_id),
        previous_price=prev,
    )


# ---------------------------------------------------------------------------
# Fetch: a GET routed THROUGH the governor (same per-host choke point as wallapop).
# ---------------------------------------------------------------------------


class MilanunciosFetcher:
    """A POOL of fingerprint-coherent curl_cffi GET sessions for the milanuncios API.

    Concurrency vs. coherence (identical doctrine to CochesFetcher/WallapopFetcher). A single
    curl_cffi Session is NOT thread-safe, and the governor runs each fetch in its own worker
    thread (asyncio.to_thread). The fix is a small bounded POOL: one Session per concurrency
    slot, leased by index so each in-flight coroutine owns a distinct, never-shared session
    for the duration of its GET. The governor's per-host bucket still bounds the AGGREGATE
    rate across the whole pool, so the pool widens parallelism WITHOUT out-pacing the host.

    `last_status` reflects the most recent GET across the pool — sufficient for the breaker's
    http_status signal (a throttle shows as the same non-200 on any slot).
    """

    def __init__(self, pool_size: int = 1,
                 segment_params: dict[str, str] | None = None) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None
        # The active segment's facet params (e.g. {"kilometersTo":"1000"} for km0); empty for
        # the default `all` segment. Merged into EVERY request so probe + drain see the same
        # filtered view — the partition's eq/gte counts and the drained ads stay consistent.
        self._segment_params: dict[str, str] = dict(segment_params or {})

    def _params(self, *, offset: int, limit: int, province: int,
                price_from: int | None, price_to: int | None) -> dict:
        # The verified GET shape: category=13 + transaction=supply + sort=newest, partitioned
        # by the singular `province` (INE code; provinceIds/regions are SILENTLY ignored) and
        # the priceFrom/priceTo band. offset walks the cell; limit honored to 100. The segment
        # facet params (km band; empty for `all`) ride on every request so the filtered view is
        # identical for the count probe and the offset drain.
        p = {
            "category": CATEGORY_CARS,
            "transaction": TRANSACTION_SUPPLY,
            "limit": str(limit),
            "offset": str(offset),
            "sort": "newest",
            "province": str(province),
        }
        if price_from is not None:
            p["priceFrom"] = str(price_from)
        if price_to is not None:
            p["priceTo"] = str(price_to)
        p.update(self._segment_params)
        return p

    def fetch_page(self, url: str, *, offset: int = 0, limit: int = PAGE_SIZE,
                   province: int, price_from: int | None = None,
                   price_to: int | None = None, slot: int = 0) -> dict:
        """The synchronous GET on pool session `slot` (runs in a governor worker thread).

        This is the callable handed to governor().wrap_fetch_text: the governor derives the
        host from `url`, waits on the per-host bucket, then runs THIS off the event loop. The
        partition coordinates (province/band/offset) ride as kwargs the governor forwards
        untouched, so each in-flight request GETs on its own leased, never-shared session.

        Raises on a non-200 so the breaker sees the failure (never masks a challenge/empty
        body). Decodes explicitly so the latin-1 mojibake repair downstream is deterministic."""
        session = self._sessions[slot]
        resp = session.get(
            url, params=self._params(offset=offset, limit=limit, province=province,
                                     price_from=price_from, price_to=price_to),
            headers=_HEADERS, impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url} "
                               f"(prov {province}, band {price_from}-{price_to}, offset {offset})")
        return json.loads(resp.content.decode("utf-8"))

    async def fetch_page_async(self, governed_fetch, url: str, *, offset: int,
                               province: int, price_from: int | None = None,
                               price_to: int | None = None, limit: int = PAGE_SIZE) -> dict:
        """Lease a pool slot, fetch THROUGH the governor on that slot, release it.

        `governed_fetch` is governor().wrap_fetch_text(self.fetch_page): the governor derives
        the host, waits on the per-host bucket (the real limiter), then runs the synchronous
        GET off the event loop — passing the partition coords through. The slot lease
        guarantees no two concurrent coroutines ever touch the same session."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, offset=offset, limit=limit, province=province,
                                        price_from=price_from, price_to=price_to, slot=slot)
        finally:
            self._free.put_nowait(slot)

    def probe_total(self, *, province: int, price_from: int | None = None,
                    price_to: int | None = None) -> tuple[str, int]:
        """A cheap limit=1 probe returning (relation, value) from pagination.totalHits.

        This is the coverage ORACLE: relation=='eq' -> value is the EXACT cell count (<10k,
        fully offset-drainable); relation=='gte' (value 10000) -> the cell holds >10k docs and
        must be sub-sharded. Runs OUTSIDE the governor (a single tiny request per partition
        during planning, well under the human-cadence floor) so planning is fast; the heavy
        drain stays governed."""
        data = self.fetch_page(ENDPOINT, offset=0, limit=1, province=province,
                               price_from=price_from, price_to=price_to)
        th = (data.get("pagination") or {}).get("totalHits") or {}
        relation = th.get("relation") or "gte"
        value = _to_int(th.get("value")) or 0
        return relation, value


# ---------------------------------------------------------------------------
# DB layer (mirrors coches_net_wholesale: ensure platform, bulk upsert dealer/vehicle,
# link edge, emit delta, all idempotent ON CONFLICT).
# ---------------------------------------------------------------------------

MN_PLATFORM_RECIPE = {
    "version": 1,
    "source": "milanuncios.com",
    "scope": ("platform-wholesale (searchapi.gw.milanuncios.com/v4/classifieds JSON API; "
              "province + price-band FACET partition for full coverage)"),
    "engine": "curl_cffi+chrome131_impersonate+json_api(GET)+facet_partition",
    "access": ("FREE: the SPA's own JSON data layer answers a Chrome TLS fingerprint cold "
               "(no proxy, no browser, no reese84, no auth, no cookie warm-up). is_tier1=TRUE "
               "(giant Tier-1 brand) but defense_tier=t1_soft (search gateway unwalled to "
               "curl_cffi). The public site/sitemap are GeeTest/S3-walled; the search API is not."),
    "data_surface": "internal_api",
    "surface_intent": "json_api",
    "endpoint": "GET https://searchapi.gw.milanuncios.com/v4/classifieds",
    "request": {
        "headers": "accept json, accept-language es-ES, origin/referer www.milanuncios.com, sec-ch-ua-platform Windows",
        "params": ("category=13 (coches), transaction=supply, limit=100 (101+ -> 30-ad fallback), "
                   "offset=N (hard cap 10000), sort=newest, province=<INE 1..52 SINGULAR>, "
                   "priceFrom/priceTo=<band> (provinceIds/regions/make SILENTLY ignored)"),
    },
    "enumeration": ("FACET partition: province 1..52; read pagination.totalHits.relation — "
                    "'eq' -> exact count <10k, drain by offset+=100; 'gte'(10000) -> >10k, "
                    "sub-shard by priceFrom/priceTo bands until every band is 'eq', then drain"),
    "platform_entity": ("kind=plataforma, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=TRUE, defense_tier=t1_soft, source_group=marketplace_generalist, "
                        "role=platform, data_surface=internal_api, platform_meta.family=adevinta"),
    "seller_policy": ("per-item ad.type discriminator, BOTH caged as sellable inventory: "
                      "'professional' -> compraventa DEALER (authorId/authorName); 'private' -> "
                      "PER-SELLER particular (canonical_key particular:milanuncios:{authorId}, so "
                      "one human's N cars collapse to ONE entity). Particular mirrors the dealer "
                      "rows (is_tier1=FALSE, source_group=NULL, kind_source=platform_label, "
                      "sells_cars=TRUE) and leaves role NULL. Only an ad with no authorId on "
                      "either path is unattributed_skipped (cannot key an owner)."),
    "dual_membership": ("vehicle.entity_ulid=OWNER (compraventa DEALER or particular HUMAN); "
                        "platform_listing edge=platform<->vehicle (identical for both kinds)"),
    "encoding": "human strings are latin-1 mojibake -> s.encode('latin-1').decode('utf-8')",
    "field_map": {
        "listing_ref": "ad.id (milanuncios native ad id)",
        "deep_link": "ad.url (prefixed https://www.milanuncios.com)",
        "title": "ad.title (demojibake'd)",
        "price": "ad.price.cash.value (EUR int; label is mojibake)",
        "previous_price": "ad.previousPrice (price-drop signal)",
        "year": "attributes[year].value.raw",
        "km": "attributes[kilometers].value.raw",
        "fuel": "attributes[fuel].value.raw (slug -> ES label)",
        "transmission": "attributes[transmission].value.raw (AUTOMATIC/MANUAL -> ES label)",
        "photo_url": "photos[adId].imageUrls[0] (prefixed https://)",
        "dealer": "ad {type, authorId, authorName}",
        "location": "ad.location {province.id(=INE code), city.name}",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the milanuncios platform entity + platform_meta exist.

    Returns the platform entity_ulid. is_tier1=TRUE (giant brand) with the explicit multi-axis
    classification: defense_tier=t1_soft, source_group=marketplace_generalist, role=platform
    (migrations/0016) and platform_meta.family='adevinta'. data_surface='internal_api'
    (schema-valid; the SPA's REST gateway). website_waf='none' (the search path is unwalled to
    curl_cffi — truthful)."""
    code = milanuncios_platform_cdp_code()
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
        eulid, code, MN_TRADE_NAME, MN_WEBSITE, MN_WAF,
        MN_DEFENSE_TIER, MN_SOURCE_GROUP, MN_ROLE, MN_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, MN_SOURCE_KEY, MN_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'internal_api',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"endpoint": ENDPOINT, "host": host_of(ENDPOINT),
                           "method": "GET", "category": CATEGORY_CARS,
                           "transaction": TRANSACTION_SUPPLY, "limit": PAGE_SIZE,
                           "surface_intent": "json_api", "partition": "province x price-band",
                           "engine": "curl_cffi/chrome131_impersonate"}),
        MN_FAMILY)
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    milanuncios dealers have no bare domain on this surface -> identity is name + location
    (name + municipality_code), mirroring the conservative rule used for mercedes_benz /
    das_weltauto.  The authorId is intentionally excluded: it is per-listing-session
    unstable (the same physical dealer appears under N different authorIds across crawl
    windows), so including it would fragment one physical dealer into N CARDEEP entities.
    The authorId is preserved as source_ref in entity_source for traceability only."""
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni)


def cdp_code_particular(p: ParticularRef) -> str:
    """Mint the particular's immutable cdp_code via the canonical PARTICULAR generator.

    Identity is the source's OWN stable seller id (canonical_key
    'particular:milanuncios:{authorId}') so a private human's N cars collapse to ONE entity.
    We do NOT fabricate per-seller identity from name+location; the authorId is the truth the
    source already publishes, and using it makes re-runs idempotent and cross-source-stable."""
    return cdp_code(province_code=p.province_code, particular_platform="milanuncios",
                    particular_seller_id=p.author_id)


# The bulk statements — ONE round-trip per table per window (unnest-based multi-row upsert),
# the SAME idempotency the per-row path would use (ON CONFLICT byte-for-byte), so a re-run of
# an already-harvested window adds 0 rows and 0 events. Mirrors coches_net_wholesale exactly.

_BULK_UPSERT_DEALERS = """
INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
        province_code, municipality_code, is_tier1, status, kind_source,
        sells_cars, role, first_discovered_source, last_seen)
SELECT u.entity_ulid, u.cdp_code, 'compraventa', u.name, u.name,
       u.province_code, u.municipality_code, FALSE, 'active', 'platform_label',
       TRUE, 'standalone_pos', $7, now()
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

# PARTICULARS: a private individual seller is FIRST-CLASS sellable inventory. The row MIRRORS
# the milanuncios dealer rows on the classification axes (is_tier1=FALSE, source_group=NULL
# exactly like the dealer bulk upsert leaves them, kind_source='platform_label'), differing
# only where it MUST: kind='particular', and role is left NULL (a private human is not a
# point-of-sale role). sells_cars=TRUE (the car is for sale). Idempotent ON CONFLICT (cdp_code);
# a re-run only ADDs new humans and never UPDATEs a non-mutated row beyond last_seen.
#
# B4.4: ON CONFLICT fills municipality_code / province_code ONLY when NULL in the existing
# row (COALESCE pattern). A re-scrape with the improved B4.2 fuzzy resolver will backfill
# the municipality that the old exact-only resolver left NULL, without ever overwriting a
# value that was already resolved. DEALERS are intentionally excluded: their cdp_code
# embeds municipality_code in the identity hash, so changing muni would change identity.
_BULK_UPSERT_PARTICULARS = """
INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
        province_code, municipality_code, is_tier1, status, kind_source,
        sells_cars, first_discovered_source, last_seen)
SELECT u.entity_ulid, u.cdp_code, 'particular', u.name, u.name,
       u.province_code, u.municipality_code, FALSE, 'active', 'platform_label',
       TRUE, $7, now()
  FROM unnest($1::text[], $2::text[], $3::text[], $4::char(2)[], $5::char(5)[],
              $6::text[]) AS u(entity_ulid, cdp_code, name, province_code,
                               municipality_code, source_ref)
ON CONFLICT (cdp_code) DO UPDATE SET
    last_seen         = now(),
    municipality_code = COALESCE(entity.municipality_code, EXCLUDED.municipality_code),
    province_code     = COALESCE(entity.province_code,     EXCLUDED.province_code)
"""

_BULK_UPSERT_PARTICULAR_SOURCES = """
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


@dataclass
class _CageRow:
    """One fully-parsed, geo-anchored car ready for the bulk cage — the in-memory result of
    the parse+resolve phase, before any SQL. Carries everything the batched upserts need so
    the DB phase touches no per-item Python logic, only set-based statements.

    The row is OWNER-AGNOSTIC: a professional ad's car is owned by a 'compraventa' dealer, a
    private ad's car by a 'particular' human — both flow through the SAME vehicle/edge/event
    cage. `owner_kind` ('compraventa'|'particular') routes only the entity upsert (two
    set-based statements split by kind); everything downstream is identical. `owner_ref` is the
    stable authorId (the source_ref + harvest dedup key for both), `seller_type` rides the NEW
    event payload ('professional'|'private')."""
    author_id: str
    owner_cdp: str
    owner_name: str | None
    owner_province: str
    owner_muni: str | None
    owner_kind: str          # 'compraventa' (dealer) | 'particular' (private human)
    seller_type: str         # 'professional' | 'private' — for the NEW event payload
    vehicle: Vehicle


def _photos_index(data: dict) -> dict:
    """Build {adId: imageUrls[]} from the page's top-level photos[] (joined by adId)."""
    out: dict[str, list] = {}
    for ph in data.get("photos") or []:
        if not isinstance(ph, dict):
            continue
        ad_id = str(ph.get("adId") or "")
        urls = ph.get("imageUrls") or []
        if ad_id and urls:
            out[ad_id] = urls
    return out


def _parse_window(pages: list[dict], geo: GeoResolver, seen_ids: set,
                  harvested_cageable: set, stats: dict) -> list[_CageRow]:
    """Parse + geo-resolve every ad across the window IN ORDER — pure CPU, no SQL.

    This is the EXACT per-item gate the row-by-row path would apply (cross-page dedup, private
    skip, geo skip, cageable truth), lifted out of the DB loop so the SQL phase is purely
    set-based. `seen_ids`/`harvested_cageable`/`stats` are mutated here with deterministic
    order semantics, so the VAM truth is byte-identical to a serial path."""
    rows: list[_CageRow] = []
    for data in pages:
        photos_by_id = _photos_index(data)
        for ad in data.get("ads") or []:
            stats["items_seen"] += 1
            ad_id = str(ad.get("id") or "")
            if ad_id and ad_id in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue  # cross-cell / cross-page dedup (offset overlap + cross-partition).
            if ad_id:
                seen_ids.add(ad_id)

            # OWNER resolution: professional -> dealer (compraventa); private -> particular
            # (a real human who is sellable inventory, NOT skipped). Both key on the stable
            # authorId, so the resolution is uniform: produce one owner descriptor either way.
            d = parse_ad_dealer(ad)
            if d is not None:
                author_id = d.author_id
                owner_name = d.name
                owner_province = d.province_code
                owner_city = d.city
                owner_kind = "compraventa"
                seller_type = "professional"
                stats["dealer_items"] += 1
            else:
                p = parse_ad_particular(ad)
                if p is None:
                    # An ad with no authorId on either path cannot be keyed to any owner.
                    stats["unattributed_skipped"] += 1
                    continue
                author_id = p.author_id
                owner_name = p.name
                owner_province = p.province_code
                owner_city = p.city
                owner_kind = "particular"
                seller_type = "private"
                stats["private_caged"] += 1   # private ad -> CAGED as a particular.

            # Geo gate — the exact province-range guard the owner upsert applies, done in
            # memory so a bad province is skipped without ever touching the DB (no FK risk).
            if not owner_province:
                stats["geo_skipped"] += 1
                continue
            if not (owner_province.isdigit() and "01" <= owner_province <= "52"):
                stats["geo_skipped"] += 1
                continue
            muni = geo.municipality_code(owner_province, owner_city)
            if owner_kind == "particular":
                owner_cdp = cdp_code_particular(ParticularRef(
                    author_id=author_id, name=owner_name,
                    province_code=owner_province, city=owner_city))
            else:
                owner_cdp = cdp_code_dealer(DealerRef(
                    author_id=author_id, name=owner_name,
                    province_code=owner_province, city=owner_city), muni)

            v = parse_ad_vehicle(ad, photos_by_id)
            if not v.deep_link:
                continue
            harvested_cageable.add((author_id, v.deep_link))
            if v.previous_price is not None:
                stats["price_drops_captured"] += 1
            rows.append(_CageRow(
                author_id=author_id, owner_cdp=owner_cdp, owner_name=owner_name,
                owner_province=owner_province, owner_muni=muni, owner_kind=owner_kind,
                seller_type=seller_type, vehicle=v))
    return rows


async def _ingest_window(conn: asyncpg.Connection, geo: GeoResolver, platform_ulid: str,
                         pages: list[dict], seen_ids: set, harvested_cageable: set,
                         stats: dict) -> None:
    """BULK-ingest a whole concurrent page-window in ONE transaction with set-based SQL.

    Replaces a per-row drain with ONE round-trip per table per window (unnest multi-row
    upserts). The delta/VAM/platform_listing semantics are preserved EXACTLY: same ON CONFLICT
    idempotency, same cageable truth, same NEW-event rule (emitted only for genuinely new
    vehicles), same price-drop capture in the payload. A re-run of an already-harvested window
    adds 0 rows and 0 events.

    Phases inside the single transaction:
      1) parse+geo-resolve in memory (no SQL) -> cageable _CageRow list
      2) dedup dealers by cdp_code, bulk-upsert dealers + entity_source, map cdp_code->ulid
      3) split vehicles into existing vs new (one SELECT), bulk-touch existing, bulk-insert
         new (Python-minted ulid each), confirm which inserts actually landed
      4) bulk-upsert platform_listing edges (RETURNING counts the genuinely new edges)
      5) bulk-insert NEW delta events for the genuinely new vehicles only
    """
    cage = _parse_window(pages, geo, seen_ids, harvested_cageable, stats)
    if not cage:
        return

    async with conn.transaction():
        # ---- (2) OWNERS: dedup by cdp_code within the window, bulk-upsert SPLIT BY KIND
        # (dealers -> kind=compraventa, particulars -> kind=particular), resolve ulids. Two
        # set-based statements per kind; both key the source_ref on the stable authorId.
        owners: dict[str, _CageRow] = {}
        for r in cage:
            owners.setdefault(r.owner_cdp, r)  # first occurrence wins (deterministic)
        dealer_cdps = [c for c, r in owners.items() if r.owner_kind == "compraventa"]
        particular_cdps = [c for c, r in owners.items() if r.owner_kind == "particular"]

        if dealer_cdps:
            d_ulids = [ulid() for _ in dealer_cdps]
            d_names = [owners[c].owner_name for c in dealer_cdps]
            d_provs = [owners[c].owner_province for c in dealer_cdps]
            d_munis = [owners[c].owner_muni for c in dealer_cdps]
            d_refs = [owners[c].author_id for c in dealer_cdps]
            await conn.execute(_BULK_UPSERT_DEALERS, d_ulids, dealer_cdps, d_names, d_provs,
                               d_munis, d_refs, MN_SOURCE_KEY)
            await conn.execute(_BULK_UPSERT_DEALER_SOURCES, dealer_cdps, d_refs, MN_SOURCE_KEY)

        if particular_cdps:
            p_ulids = [ulid() for _ in particular_cdps]
            p_names = [owners[c].owner_name for c in particular_cdps]
            p_provs = [owners[c].owner_province for c in particular_cdps]
            p_munis = [owners[c].owner_muni for c in particular_cdps]
            p_refs = [owners[c].author_id for c in particular_cdps]
            await conn.execute(_BULK_UPSERT_PARTICULARS, p_ulids, particular_cdps, p_names,
                               p_provs, p_munis, p_refs, MN_SOURCE_KEY)
            await conn.execute(_BULK_UPSERT_PARTICULAR_SOURCES, particular_cdps, p_refs,
                               MN_SOURCE_KEY)

        owner_cdps = dealer_cdps + particular_cdps
        cdp_to_ulid: dict[str, str] = {
            row["cdp_code"]: row["entity_ulid"]
            for row in await conn.fetch(
                "SELECT cdp_code, entity_ulid FROM entity WHERE cdp_code = ANY($1::text[])",
                owner_cdps)
        }

        # ---- attach resolved owner_ulid; dedup cars by (owner_ulid, deep_link) in window.
        cars: dict[tuple[str, str], _CageRow] = {}
        for r in cage:
            du = cdp_to_ulid.get(r.owner_cdp)
            if du is None:
                continue  # owner upsert race-impossible here, but stay defensive
            key = (du, r.vehicle.deep_link)
            cars.setdefault(key, r)

        # ---- (3) VEHICLES: one SELECT splits existing vs new (idempotency truth).
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
            # Confirm which minted ulids actually landed (ON CONFLICT DO NOTHING could drop one
            # if a concurrent writer inserted the same (entity,deep_link) first). Only a
            # confirmed-new vehicle is counted new + gets a NEW event — preserves idempotency.
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

        # ---- (4) EDGES: one batched upsert; RETURNING (xmax=0) counts genuinely new edges.
        e_vehicles = [vehicle_ulid_for[k] for k in car_keys]
        e_urls = [cars[k].vehicle.deep_link for k in car_keys]
        e_refs = [cars[k].vehicle.listing_ref for k in car_keys]
        e_prices = [cars[k].vehicle.price for k in car_keys]
        edge_rows = await conn.fetch(_BULK_UPSERT_EDGES, e_vehicles, e_urls, e_refs,
                                     e_prices, platform_ulid)
        stats["edges_created"] += sum(1 for row in edge_rows if row["inserted"])

        # ---- (5) NEW delta events — only for genuinely new vehicles, price-drop preserved.
        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                row = cars[k]
                v = row.vehicle
                payload = {"price": v.price, "title": v.title, "platform": MN_TRADE_NAME,
                           "seller_type": row.seller_type}
                if v.previous_price is not None:
                    payload["previous_price"] = v.previous_price
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities,
                               ev_payloads)
            stats["new_events"] += len(confirmed_new)


# ---------------------------------------------------------------------------
# Partition planning — read each province's totalHits.relation/value; split the dense ones
# by price band until every cell is "eq" (<10k, offset-drainable). The coverage-proof spine.
# ---------------------------------------------------------------------------


def plan_partitions(fetcher: MilanunciosFetcher, provinces: tuple[int, ...],
                    stats: dict) -> tuple[list[dict], int]:
    """Build the partition list and the summed declared coverage.

    For each province: probe totalHits. relation=='eq' -> one partition (exact count). 'gte'
    (>10k) -> split into price bands, each probed; a band still 'gte' is kept and drained to
    the 10k cap (honest residual, logged) — for the metro provinces every band resolves 'eq'.
    coverage_sum is the capture-recapture path: sum of every partition's declared count, to be
    compared against the national declared total."""
    partitions: list[dict] = []
    coverage_sum = 0
    for prov in provinces:
        rel, val = fetcher.probe_total(province=prov)
        time.sleep(0.05)  # human-cadence floor between planning probes.
        if rel == "eq":
            partitions.append({"province": prov, "price_from": None, "price_to": None,
                               "declared": val, "exact": True})
            coverage_sum += val
            continue
        # Dense province -> price-band sub-partitions. Sum the BANDS' declared totals (the
        # real fetched coverage), not the clamped province aggregate.
        stats["dense_provinces"] += 1
        for frm, to in PRICE_BANDS:
            brel, bval = fetcher.probe_total(province=prov, price_from=frm, price_to=to)
            time.sleep(0.04)
            partitions.append({"province": prov, "price_from": frm, "price_to": to,
                               "declared": bval, "exact": (brel == "eq")})
            coverage_sum += min(bval, ES_WINDOW_CAP) if brel != "eq" else bval
            if brel != "eq":
                stats["bands_still_capped"] += 1
    return partitions, coverage_sum


def _national_total(fetcher: MilanunciosFetcher) -> tuple[str, int]:
    """The national declared total (no province filter). >50k always reads 'gte'/10000
    (clamped), so this is a floor, not a quorum path — reported for honesty only."""
    p = {"category": CATEGORY_CARS, "transaction": TRANSACTION_SUPPLY, "limit": "1",
         "sort": "newest"}
    p.update(fetcher._segment_params)  # national count of the ACTIVE segment's view.
    resp = fetcher._sessions[0].get(ENDPOINT, params=p, headers=_HEADERS,
                                    impersonate=_IMPERSONATE, timeout=_TIMEOUT)
    th = (resp.json().get("pagination") or {}).get("totalHits") or {}
    return th.get("relation") or "gte", _to_int(th.get("value")) or 0


# ---------------------------------------------------------------------------
# Drain one partition cell to exhaustion via the concurrent sliding window + bulk ingest.
# ---------------------------------------------------------------------------


async def _drain_partition(conn: asyncpg.Connection, geo: GeoResolver, platform_ulid: str,
                           fetcher: MilanunciosFetcher, governed_fetch, partition: dict,
                           concurrency: int, max_pages: int, page_size: int,
                           seen_ids: set, harvested_cageable: set,
                           stats: dict) -> tuple[bool, str | None, int | None]:
    """Drain a single partition cell to exhaustion via the concurrent sliding window.

    Returns (clean_finish, fetch_error, last_http). clean_finish=True means the cell ended on
    an empty/short page (fully drained) or hit the 10k window / max_pages cap; False means a
    fetch error stopped it (the breaker signal). Each window fetches up to `concurrency` pages
    in parallel through the governor (the host bucket paces the aggregate), then BULK-ingests
    them in offset order in ONE transaction. A GLOBAL seen_ids dedups across pages AND cells."""
    prov = partition["province"]
    frm, to = partition["price_from"], partition["price_to"]
    # The offset cap for this cell: never page past the 10k ES window, and never past the
    # caller's --pages bound (the proof slice ceiling). Both expressed in offsets.
    max_offset = min(ES_WINDOW_CAP, max_pages * page_size)

    stop = False
    fetch_error: str | None = None
    last_http: int | None = None
    next_offset = 0
    while next_offset < max_offset and not stop:
        # build a window of offsets, all < max_offset.
        offsets: list[int] = []
        off = next_offset
        for _ in range(concurrency):
            if off >= max_offset:
                break
            offsets.append(off)
            off += page_size
        next_offset = off
        if not offsets:
            break

        results = await asyncio.gather(
            *(fetcher.fetch_page_async(governed_fetch, ENDPOINT, offset=o, province=prov,
                                       price_from=frm, price_to=to, limit=page_size)
              for o in offsets),
            return_exceptions=True,
        )

        window_pages: list[dict] = []
        for o, data in zip(offsets, results):
            if isinstance(data, Exception):
                fetch_error = str(data)
                last_http = fetcher.last_status
                print(f"[milanuncios_wholesale] prov {prov} band {frm}-{to} offset {o} "
                      f"fetch failed ({data}); stopping this partition honestly.")
                stop = True
                break
            ads = data.get("ads") or []
            if not ads:
                stop = True  # clean end of this cell.
                break
            window_pages.append(data)
            # a short page (< page_size) means the cell is exhausted after this page.
            if len(ads) < page_size:
                stop = True

        if window_pages:
            await _ingest_window(conn, geo, platform_ulid, window_pages, seen_ids,
                                 harvested_cageable, stats)
            stats["pages_fetched"] += len(window_pages)

    clean_finish = fetch_error is None
    return clean_finish, fetch_error, last_http


# ---------------------------------------------------------------------------
# Orchestration — plan, then drain every partition through the shared machinery, then the
# SAME VAM count quorum + S-HEALTH heartbeat the wholesale siblings run.
# ---------------------------------------------------------------------------

DEFAULT_CONCURRENCY = 15
DEFAULT_MAX_PAGES = 100   # per-cell page cap (proof bound); a real cell ends naturally first.


async def harvest(provinces: tuple[int, ...] = SPANISH_PROVINCES,
                  concurrency: int = DEFAULT_CONCURRENCY,
                  max_pages: int = DEFAULT_MAX_PAGES,
                  page_size: int = PAGE_SIZE,
                  segment: str = DEFAULT_SEGMENT) -> dict:
    # Resolve the segment to its facet params. `all` (default) = no facet = the whole flat
    # supply index = full coverage = legacy behavior. `renting` is not a milanuncios product:
    # exit cleanly without a drain (no edges to add, no false count).
    segment = (segment or DEFAULT_SEGMENT).lower()
    if segment not in SEGMENTS:
        raise SystemExit(f"unknown --segment {segment!r}; valid: {', '.join(SEGMENTS)}")
    segment_params = SEGMENTS[segment]
    if segment_params is None:
        print(f"[milanuncios_wholesale] segment '{segment}' is not a milanuncios product "
              f"(no renting/subscription on the coches vertical); nothing to drain.")
        return {"skipped": True, "reason": f"segment_{segment}_not_a_product",
                "source_key": MN_SOURCE_KEY, "segment": segment}

    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    page_size = max(1, min(page_size, PAGE_SIZE))
    fetcher = MilanunciosFetcher(pool_size=concurrency, segment_params=segment_params)
    stats = {
        "pages_fetched": 0, "items_seen": 0, "dealer_items": 0,
        "private_caged": 0, "unattributed_skipped": 0, "geo_skipped": 0,
        "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "price_drops_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "dealers_distinct": 0,
        "particulars_distinct": 0, "new_particulars": 0,
        "concurrency": concurrency, "partitions": 0, "partitions_clean": 0,
        "partitions_errored": 0, "coverage_sum": 0, "national_relation": None,
        "dense_provinces": 0, "bands_still_capped": 0, "page_size": page_size,
        "max_pages": max_pages, "segment": segment,
        "segment_params": dict(segment_params),
    }
    # GLOBAL harvest truth — distinct across ALL partitions (cross-cell overlap from province/
    # price edge-membership + offset overlap collapses here exactly once).
    seen_ids: set[str] = set()
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if milanuncios's breaker is OPEN (a recent ban/throttle still cooling),
    # skip the drain gracefully — the API keeps serving the last snapshot ("no se cae").
    if await is_open(conn, MN_SOURCE_KEY):
        print(f"[milanuncios_wholesale] breaker OPEN for {MN_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, API still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": MN_SOURCE_KEY}

    # GOVERNOR: the single per-host choke point. EVERY page passes through
    # searchapi.gw.milanuncios.com's token bucket (JSON_API class: 12 req/s steady, burst 24),
    # off the event loop. No matter how many pages are in flight, the host is never hammered:
    # the bucket is the limiter, not Python's awaits.
    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None
    t0 = time.monotonic()
    try:
        geo = await GeoResolver.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = milanuncios_platform_cdp_code()
        print(f"[milanuncios_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid})")
        print(f"[milanuncios_wholesale] governor paces host {host_of(ENDPOINT)} (JSON_API bucket).")

        # ---- PLAN: probe every province's totalHits; split the dense ones by price band.
        seg_label = segment + (f" {segment_params}" if segment_params else " (full index)")
        print(f"[milanuncios_wholesale] segment = {seg_label}")
        print(f"[milanuncios_wholesale] planning FACET partitions over {len(provinces)} "
              f"provinces (limit={page_size}, max_pages/cell={max_pages})...")
        nat_rel, nat_val = _national_total(fetcher)
        stats["national_relation"] = f"{nat_rel}:{nat_val}"
        stats["declared_full"] = nat_val
        partitions, coverage_sum = plan_partitions(fetcher, provinces, stats)
        stats["partitions"] = len(partitions)
        stats["coverage_sum"] = coverage_sum
        split_provs = sorted({p["province"] for p in partitions
                              if p["price_from"] is not None or p["price_to"] is not None})
        print(f"[milanuncios_wholesale] PLAN: {len(partitions)} partitions; "
              f"price-split (dense) provinces = {split_provs}")
        print(f"[milanuncios_wholesale] COVERAGE PROOF: sum(partition declared)={coverage_sum} "
              f"(national declared reads {nat_rel}:{nat_val} — clamped floor, not a quorum path)")

        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        particulars_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='particular'")}

        # ---- DRAIN: every partition cell through the shared concurrent+batch machinery.
        for i, partition in enumerate(partitions, 1):
            prov = partition["province"]
            frm, to = partition["price_from"], partition["price_to"]
            band_label = "all" if frm is None and to is None else f"{frm}-{to}"
            clean, perr, phttp = await _drain_partition(
                conn, geo, platform_ulid, fetcher, governed_fetch, partition,
                concurrency, max_pages, page_size, seen_ids, harvested_cageable, stats)
            if clean:
                stats["partitions_clean"] += 1
            else:
                stats["partitions_errored"] += 1
                fetch_error = perr or fetch_error
                last_http = phttp if phttp is not None else last_http
            elapsed = time.monotonic() - t0
            cpm = stats["cars_caged"] / (elapsed / 60) if elapsed > 0 else 0.0
            print(f"[milanuncios_wholesale] [{i}/{len(partitions)}] prov {prov:2d} "
                  f"band {band_label:<13} declared={partition['declared']:6d} -> "
                  f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                  f"edges={stats['edges_created']} priv_caged={stats['private_caged']} "
                  f"distinct_ids={len(seen_ids)} | {cpm:.0f} cars/min "
                  f"{'CLEAN' if clean else 'ERROR'}")

        elapsed = time.monotonic() - t0
        stats["elapsed_s"] = elapsed
        stats["cars_per_min"] = stats["cars_caged"] / (elapsed / 60) if elapsed > 0 else 0.0

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        particulars_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='particular'")}
        stats["new_particulars"] = len(particulars_after - particulars_before)
        # distinct OWNERS reachable through the milanuncios edge, split by kind. Both dealers
        # and particulars own caged cars + carry the platform_listing edge, so both are counted
        # via the same join — the only difference is the entity kind filter.
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               JOIN entity e ON e.entity_ulid = v.entity_ulid
               WHERE pl.platform_entity_ulid = $1 AND e.kind = 'compraventa'""", platform_ulid)
        stats["particulars_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               JOIN entity e ON e.entity_ulid = v.entity_ulid
               WHERE pl.platform_entity_ulid = $1 AND e.kind = 'particular'""", platform_ulid)

        # Persist the recipe annotated with THIS run's segment view (a facet of the one flat
        # supply index; 'all' = the whole index). The base recipe is unchanged; we add the
        # segment so the artifact records exactly which view was drained.
        run_recipe = {**MN_PLATFORM_RECIPE, "segment": segment,
                      "segment_params": dict(segment_params),
                      "segment_note": ("milanuncios is ONE flat supply index; segments are "
                                       "per-item facet slices (km band / sellerType), NOT "
                                       "separate backends. 'all' = full coverage.")}
        recipe_path = write_recipe(platform_code, run_recipe)
        print(f"[milanuncios_wholesale] recipe written: {recipe_path}")

        # ---- VAM count quorum — THREE orthogonal like-with-like paths that all measure
        #   "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for milanuncios   (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join      (DB read truth)
        #   harvested_cageable = distinct (authorId, deep_link) pulled     (harvest truth)
        # The declared full (national, clamped) is reported for honesty but is NOT a quorum
        # path (it measures the WHOLE platform, clamped, not this drained slice).
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

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks milanuncios,
        # trips the breaker on a ban, and auto-repairs. OK when >=1 page fetched, no fetch
        # error stopped a partition, and the VAM did not refute.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, MN_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, MN_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[milanuncios_wholesale] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("MILANUNCIOS WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  segment               : {stats.get('segment')} {stats.get('segment_params') or '(full index)'}")
    print(f"  national declared     : {stats.get('national_relation')} (clamped floor)")
    print("  --- coverage (facet partition) ---")
    print(f"  partitions            : {stats.get('partitions')} "
          f"({stats.get('partitions_clean')} clean / {stats.get('partitions_errored')} errored)")
    print(f"  dense provinces split : {stats.get('dense_provinces')} "
          f"(bands still >10k: {stats.get('bands_still_capped')})")
    print(f"  sum(partition declared): {stats.get('coverage_sum')}")
    print("  --- drain ---")
    print(f"  concurrency (window)  : {stats.get('concurrency')} pages in flight "
          f"(limit={stats.get('page_size')}, max_pages/cell={stats.get('max_pages')})")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  distinct listing ids  : {stats.get('harvested_distinct_ids')}")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page + cross-cell)")
    print(f"  dealer items          : {stats['dealer_items']}")
    print(f"  private CAGED          : {stats['private_caged']} (particular owners, sellable)")
    print(f"  unattributed skipped  : {stats.get('unattributed_skipped', 0)} (no authorId)")
    print(f"  geo skipped (bad prov): {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  particulars attributed: {stats.get('particulars_distinct', 0)} distinct "
          f"({stats.get('new_particulars', 0)} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for milanuncios = {stats.get('db_edges')})")
    print(f"  price drops captured  : {stats['price_drops_captured']}")
    print(f"  NEW delta events      : {stats['new_events']}")
    print(f"  cars/min              : {stats.get('cars_per_min', 0):.0f} "
          f"(elapsed {stats.get('elapsed_s', 0):.0f}s)")
    print("  --- VAM count quorum (like-with-like, this slice) ---")
    print(f"  harvested_cageable    : {stats.get('harvested_cageable')}")
    print(f"  db_edges              : {stats.get('db_edges')}")
    print(f"  db_join_vehicles      : {stats.get('db_join_vehicles')}")
    print(f"  VAM verdict           : {stats.get('verdict')}")
    print(f"  health status         : {stats.get('health_status')} / breaker {stats.get('breaker_state')}")
    print(f"  recipe                : {stats.get('recipe_path')}")
    print("=" * 64)


def _parse_provinces(arg: str | None) -> tuple[int, ...]:
    if not arg:
        return SPANISH_PROVINCES
    out: list[int] = []
    for tok in arg.split(","):
        tok = tok.strip()
        if not tok:
            continue
        n = int(tok)
        if 1 <= n <= 52:
            out.append(n)
    return tuple(out) or SPANISH_PROVINCES


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
        description="milanuncios wholesale harvester (facet-partition JSON-API drain)")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=(f"max pages PER partition cell (proof bound; size={PAGE_SIZE}); "
                              f"default {DEFAULT_MAX_PAGES}. A cell ends naturally on an empty/"
                              f"short page first. The 10k ES window also caps each cell."))
    parser.add_argument("--limit", type=int, default=PAGE_SIZE,
                        help=f"page size (ads/request; max {PAGE_SIZE}, 101+ degrades); default {PAGE_SIZE}")
    parser.add_argument("--provinces", type=str, default=None,
                        help="comma-separated INE province ids (1..52); default = all 52")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"pages fetched in parallel per sliding window; default "
                              f"{DEFAULT_CONCURRENCY}. The governor's per-host bucket is the "
                              f"real limiter — this only needs to keep the bucket saturated."))
    parser.add_argument("--segment", type=str, default=DEFAULT_SEGMENT,
                        choices=tuple(SEGMENTS.keys()),
                        help=("inventory segment (a FACET of the one flat supply index): "
                              "all (default, full coverage) | vo (used, km>=1000) | km0 "
                              "(km<=1000) | vn (nuevo/a estrenar, km<=100) | catalog (alias of "
                              "vn; milanuncios has no separate new-car catalog) | renting "
                              "(no-op: not a milanuncios product). 'all' drains every segment."))
    args = parser.parse_args()
    provinces = _parse_provinces(args.provinces)
    stats = asyncio.run(harvest(provinces, args.concurrency, args.pages, args.limit,
                                args.segment))
    _print_report(stats)


if __name__ == "__main__":
    main()
