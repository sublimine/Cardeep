"""coches.net WHOLESALE harvester — the SECOND giant marketplace, end to end.

coches.net is a Tier-1 marketplace (Adevinta / Schibsted Spain Motor, fronted by
Imperva). Unlike AS24's SSR __NEXT_DATA__ surface, coches.net exposes an OPEN
internal JSON API (`POST https://web.gw.coches.net/search`) that needs NO browser,
NO proxy, NO cookie warm-up — just a Chrome TLS fingerprint (curl_cffi) and the
right minimal headers (Origin / Referer / X-Schibsted-Tenant). Verified live
2026-06-12 (docs/architecture/tier1_recipes/coches_net.md): 272k cars, dealer
attribution attached. is_tier1=TRUE because the public site sits behind Imperva;
the API host happens to be unwalled, which is exactly what the recipe records.

This module mirrors pipeline.platform.autoscout24_wholesale EXACTLY (same dual-
membership model, same caging, same governor/health/VAM wiring). It proves a
SECOND platform flows through one architecture, not a fork of it:

  coches.net (the marketplace)  -> entity, kind='plataforma'  (+ platform_meta)
  each SELLING DEALER           -> entity, kind='compraventa' (geo-resolved)
  each PRIVATE seller's car     -> owned by the per-province 'particular' bucket entity
  each CAR                      -> vehicle, OWNED BY its dealer/bucket (entity_ulid=owner)
  the car ON the platform       -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the dealer/bucket); platform membership is plural (this edge). The
same physical car can carry BOTH an AS24 edge and a coches.net edge without ever changing
its owning dealer.

PRIVATE sellers are NOT skipped — a private individual's car is real inventory a buyer can
purchase, so it must be served. coches.net ANONYMISES privates (seller.contractId is the
shared sentinel "1" across all of them; seller.name is a non-unique first name), so there
is NO stable per-seller id. We therefore cage every private car under ONE synthetic
'particular' bucket entity PER PROVINCE (location.mainProvinceId; '00' fallback when
missing). The car, the edge and the NEW delta event are all caged exactly like a dealer's
car — only per-human identity the source withholds is bucketed, never fabricated.

PROOF SLICE, NOT THE FULL HARVEST. coches.net declares ~272k results
(meta.totalResults). Draining all of it (~2,728 requests at size=100) needs the
full governed run (spend/rate budget, page-window stability). Here we cap at
MAX_PAGES (~5 pages x 100 = ~500 cars) and log the cap honestly. The declared full
count is recorded for the VAM verdict's slice arithmetic.

Engine: a POST against web.gw.coches.net routed THROUGH the per-host governor (the
same single choke point AS24 uses). The synchronous curl_cffi POST runs in a worker
thread so the event loop is never blocked, and no host is fetched faster than its
bucket.

Run: python -m pipeline.platform.coches_net_wholesale --pages 5
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
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
# coches.net platform identity (00-TIER1-REGISTRY; recipe coches_net.md).
# ---------------------------------------------------------------------------
COCHES_DOMAIN = "coches.net"
COCHES_WEBSITE = "coches.net"
COCHES_TRADE_NAME = "coches.net"
COCHES_SOURCE_KEY = "coches_net_wholesale"
COCHES_WAF = "imperva"  # the public site is Imperva-fronted -> is_tier1=TRUE.

# The working request (recipe TL;DR; verified live 2026-06-12).
ENDPOINT = "https://web.gw.coches.net/search"
CATEGORY_CARS = 2500  # categoryId 2500 = turismos (cars).
_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.coches.net",
    "Referer": "https://www.coches.net/segunda-mano/",
    "X-Schibsted-Tenant": "coches",
}
_PDP_BASE = "https://www.coches.net"  # item.url is a relative PDP path.
_IMPERSONATE = "chrome131"
_TIMEOUT = 40

# Province sentinel '00' = national (same convention as AS24). geo_province has NO
# '00', so the platform ENTITY stores province_code = NULL; '00' lives only inside
# the cdp_code string (free text, no FK). We never pollute geo_province with it.
PLATFORM_PROVINCE_SENTINEL = "00"

# PROOF SLICE cap. ~5 pages * 100 = ~500 cars. NOT the ~272k full set (full drain
# = the full governed run, ~2,728 requests at size=100).
DEFAULT_MAX_PAGES = 5
PAGE_SIZE = 100  # the API honors size up to 100 (recipe verified).

# PRIVATE-seller bucket. coches.net ANONYMISES privates: seller.contractId is the SHARED
# sentinel "1" across ALL privates and seller.name is a non-unique first name (verified
# live 2026-06-12: page 1500 is ~89% private, every one carries contractId="1"). There is
# NO stable per-seller id, so we DO NOT fabricate per-human identity the source withholds.
# Instead every private car is owned by ONE synthetic 'particular' bucket entity PER
# PROVINCE (canonical_key 'particular:cochesnet:{province}'). The car, the platform_listing
# edge and the NEW delta event are all caged exactly like a dealer's car; only per-seller
# identity is bucketed. The bucket entity MIRRORS the platform's dealer rows
# (is_tier1=FALSE, source_group/role NULL, kind_source='platform_label') and differs only
# in kind='particular' + sells_cars=TRUE.
PARTICULAR_KIND = "particular"
PARTICULAR_NAME_PREFIX = "Particulares coches.net"
# Fallback province sentinel when location.mainProvinceId is missing/invalid: bucket the
# car under '00' so no real car is ever dropped for want of a clean province. '00' is NOT a
# geo_province FK, so the bucket entity stores province_code=NULL for the '00' bucket (the
# '00' still anchors the cdp_code string); a real 1..52 province stores its code normally.
PARTICULAR_PROVINCE_FALLBACK = "00"

# transmissionTypeId -> human label (coches.net codes; verified live: only 1/2 seen).
_TRANSMISSION = {1: "Manual", 2: "Automático"}


def coches_platform_cdp_code() -> str:
    """The coches.net platform's immutable cdp_code. Built from the bare domain
    identity (canonical_key 'domain:coches.net'), province segment '00' (national).
    Mirrors as24_platform_cdp_code() so both platforms mint codes the same way."""
    key = f"domain:{COCHES_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL response — field names inspected live, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class DealerRef:
    """The selling dealer parsed from a single item's `seller` + `location`.

    coches.net's seller carries only name + contractId + ratings (NO address/zip).
    The geo anchor therefore comes from the ITEM's location (mainProvinceId is the
    INE province code; cityLiteral resolves the municipality). contractId is the
    stable per-dealer id used for cross-source dedup and as the source_ref."""
    contract_id: str
    name: str | None
    province_code: str | None
    city: str | None
    score_average: float | None
    comments_number: int | None


@dataclass
class Vehicle:
    """A car parsed from a single coches.net search item."""
    deep_link: str
    listing_ref: str           # coches.net native ad id (item.id)
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    price_drop: dict | None     # price.priceDropData {date, amountFromOriginal, percentageFromOriginal}


def _to_int(v):
    if v is None:
        return None
    try:
        n = int(v)
    except (TypeError, ValueError):
        return None
    return n


def _prov2(province_id) -> str | None:
    """coches.net location.mainProvinceId IS the INE province code (28=Madrid,
    15=A Coruña, 38=Sta.C.Tenerife — verified live). Zero-pad to 2 digits."""
    if province_id is None:
        return None
    try:
        n = int(province_id)
    except (TypeError, ValueError):
        return None
    if not (1 <= n <= 52):
        return None
    return f"{n:02d}"


def _first_image(resources) -> str | None:
    if not isinstance(resources, list):
        return None
    for res in resources:
        if isinstance(res, dict) and res.get("type") == "IMAGE" and res.get("url"):
            return res["url"]
    return None


def parse_item_dealer(item: dict) -> DealerRef | None:
    """Parse the SELLING DEALER from an item's `seller` + `location`, or None if the item
    is a PRIVATE seller (the caller then cages it into the per-province 'particular' bucket).

    Only professional sellers (isProfessional) with a contractId become compraventa entities;
    a private seller returns None here BUT is NOT dropped — the caller routes it to the
    'particular' bucket. Geo comes from the item's location, not the seller (the seller has
    no address on this surface)."""
    seller = item.get("seller") or {}
    if not seller.get("isProfessional"):
        return None
    contract_id = seller.get("contractId")
    if not contract_id:
        return None
    loc = item.get("location") or {}
    prov = _prov2(loc.get("mainProvinceId"))
    ratings = seller.get("ratings") or {}
    return DealerRef(
        contract_id=str(contract_id),
        name=seller.get("name"),
        province_code=prov,
        city=loc.get("cityLiteral"),
        score_average=ratings.get("scoreAverage"),
        comments_number=ratings.get("commentsNumber"),
    )


def parse_item_vehicle(item: dict) -> Vehicle:
    """Parse the car from a coches.net search item (REAL field map)."""
    price_obj = item.get("price") or {}
    amount = price_obj.get("amount")
    try:
        price = float(amount) if amount is not None else None
    except (TypeError, ValueError):
        price = None

    year = _to_int(item.get("year"))
    if year is not None and not (1900 <= year <= 2100):
        year = None
    km = _to_int(item.get("km"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    url = item.get("url") or ""
    deep_link = (_PDP_BASE + url) if url.startswith("/") else url

    make = item.get("make")
    model = item.get("model")
    title = item.get("title") or " ".join(p for p in (make, model) if p) or None

    return Vehicle(
        deep_link=deep_link,
        listing_ref=str(item.get("id") or ""),
        title=title,
        make=make,
        model=model,
        year=year,
        km=km,
        price=price,
        fuel=item.get("fuelType"),  # already a clean UTF-8 string (Diésel/Eléctrico/...)
        transmission=_TRANSMISSION.get(item.get("transmissionTypeId")),
        photo_url=_first_image(item.get("resources")),
        price_drop=price_obj.get("priceDropData"),
    )


# ---------------------------------------------------------------------------
# Fetch: a POST routed THROUGH the governor (same per-host choke point as AS24).
# ---------------------------------------------------------------------------


class CochesFetcher:
    """A POOL of fingerprint-coherent curl_cffi POST sessions for the coches.net API.

    Concurrency vs. coherence. A single `curl_cffi` Session is NOT safe to call from
    several threads at once, and the governor runs each fetch in its own worker thread
    (asyncio.to_thread) — so a concurrent drain with ONE shared session would race the
    session's internal state. The fix is a small bounded POOL: one Session per
    concurrency slot, each its own Chrome fingerprint + cookie jar. Within a slot the
    drain still looks like one continuous browser; across slots it looks like a handful
    of independent browsers hitting a public API — which is exactly what a JSON gateway
    built for millions of users sees all day. The governor's per-host bucket still bounds
    the AGGREGATE rate across every session, so the pool widens parallelism WITHOUT
    out-pacing the host (the choke point is the bucket, never the session count).

    `last_status` reflects the most recent POST across the pool — sufficient for the
    breaker's http_status signal (a throttle shows as the same non-200 on any slot).
    """

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        # One coherent session per slot. Built lazily would race; build them up front
        # under no contention so the pool is ready before the first concurrent window.
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        # Hand a session to a worker by slot index so each concurrent coroutine owns a
        # distinct, never-shared session for the duration of its POST (thread-safe).
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    @staticmethod
    def _payload(page: int, size: int) -> dict:
        # pagination is a NESTED object {page,size}; a top-level "page" is silently
        # ignored by the gateway (recipe root-caused this). price/year/km open.
        # NO sortBy: 'relevance' silently caps the gateway result set at ~155k (frontend-only
        # cap, verified by hand). The DEFAULT order has NO cap and enumerates all 272k pages.
        return {
            "categoryId": CATEGORY_CARS,
            "pagination": {"page": page, "size": size},
            "price": {"from": None, "to": None},
            "year": {"from": None, "to": None},
            "km": {"from": None, "to": None},
        }

    def fetch_page(self, url: str, *, page: int = 1, size: int = PAGE_SIZE,
                   slot: int = 0) -> dict:
        """The synchronous POST on pool session `slot` (runs in a worker thread).

        This is the callable handed to governor().wrap_fetch_text: the governor derives
        the host from `url`, waits on the per-host bucket, then runs THIS off the event
        loop. `slot` rides as a kwarg the governor forwards untouched, so each in-flight
        request POSTs on its own leased, never-shared curl_cffi session (thread-safe).
        `slot` defaults to 0 so the sequential/single-session contract still holds.

        Raises on a non-200 so the caller sees the failure (never masks a challenge/empty
        body — the breaker must catch throttling)."""
        session = self._sessions[slot]
        resp = session.post(url, json=self._payload(page, size), headers=_HEADERS,
                            impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url} (page {page})")
        # The API serves UTF-8 JSON; decode explicitly so accented fuel/city names
        # (Diésel, A Coruña) survive regardless of curl_cffi's encoding guess.
        return json.loads(resp.content.decode("utf-8"))

    async def fetch_page_async(self, governed_fetch, url: str, *, page: int,
                               size: int = PAGE_SIZE) -> dict:
        """Lease a pool slot, fetch `page` THROUGH the governor on that slot, release it.

        `governed_fetch` is governor().wrap_fetch_text(self.fetch_page): the governor
        derives the host, waits on the per-host bucket (the real limiter), then runs the
        synchronous POST off the event loop — passing `slot` through to fetch_page. The
        slot lease guarantees no two concurrent coroutines ever touch the same session."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, page=page, size=size, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer (mirrors autoscout24_wholesale: ensure platform, upsert dealer/vehicle,
# link edge, emit delta, all idempotent ON CONFLICT).
# ---------------------------------------------------------------------------

COCHES_PLATFORM_RECIPE = {
    "version": 1,
    "source": "coches.net",
    "scope": "platform-wholesale (web.gw.coches.net/search JSON API)",
    "engine": "curl_cffi+chrome131_impersonate+json_api(POST)",
    "access": ("OPEN internal JSON API (Chrome TLS fingerprint; no proxy, no browser, "
               "no cookie warm-up). Public site is Imperva-fronted -> is_tier1=true; "
               "the API host web.gw.coches.net is unwalled."),
    "data_surface": "internal_api",
    "surface_intent": "json_api",
    "endpoint": "POST https://web.gw.coches.net/search",
    "request": {
        "headers": "Content-Type/Accept application/json, Origin, Referer, X-Schibsted-Tenant: coches",
        "body": "categoryId=2500, sortBy=relevance, pagination={page:N,size:100} (NESTED — top-level page ignored)",
    },
    "enumeration": "pagination.page=1..N, size=100; meta.totalResults/totalPages drive the full drain",
    "platform_entity": "kind=plataforma, province_code=NULL (sentinel 00 in cdp_code only), is_tier1=TRUE",
    "dual_membership": "vehicle.entity_ulid=SELLING DEALER (compraventa); platform_listing edge=platform<->vehicle",
    "particulares": ("private sellers caged, NOT skipped: source anonymises privates "
                     "(contractId='1' sentinel, first-name only) -> per-province 'particular' "
                     "bucket (canonical_key 'particular:cochesnet:{province}', '00' fallback); "
                     "kind=particular, sells_cars=TRUE, mirrors dealer rows (is_tier1=FALSE, "
                     "source_group/role NULL, kind_source=platform_label); car+edge+delta caged"),
    "field_map": {
        "deep_link": "item.url (prefixed with https://www.coches.net)",
        "listing_ref": "item.id (coches.net native ad id)",
        "make": "item.make",
        "model": "item.model",
        "year": "item.year",
        "km": "item.km",
        "price": "item.price.amount",
        "price_drop": "item.price.priceDropData {date, amountFromOriginal, percentageFromOriginal}",
        "fuel": "item.fuelType (UTF-8 string)",
        "transmission": "item.transmissionTypeId (1=Manual, 2=Automático)",
        "photo_url": "item.resources[type=IMAGE][0].url",
        "dealer": "item.seller {name, contractId, isProfessional, ratings}",
        "location": "item.location {mainProvinceId(=INE province code), cityLiteral}",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the coches.net platform entity + platform_meta exist.
    Returns the platform entity_ulid. Mirrors AS24 but is_tier1=TRUE (Imperva) and
    data_surface='internal_api' (the schema-valid value; 'json_api' intent is kept
    in surface_detail since the platform_meta CHECK does not allow that literal)."""
    code = coches_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               first_discovered_source, last_seen)
           VALUES ($1,$2,'plataforma',$3,$3,NULL,$4,$5,TRUE,'active','platform_label',$6, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, website_waf = EXCLUDED.website_waf""",
        eulid, code, COCHES_TRADE_NAME, COCHES_WEBSITE, COCHES_WAF, COCHES_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, COCHES_SOURCE_KEY, COCHES_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like)
           VALUES ($1,'internal_api',$2::jsonb,FALSE,FALSE)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail""",
        eulid, json.dumps({"endpoint": ENDPOINT, "host": host_of(ENDPOINT),
                           "method": "POST", "category_id": CATEGORY_CARS,
                           "size": PAGE_SIZE, "surface_intent": "json_api",
                           "engine": "curl_cffi/chrome131_impersonate"}))
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    coches.net dealers have no bare domain on this surface -> identity = name +
    location + the stable contractId (passed via `address` so two distinct contracts
    that happen to share a name in one municipality never collapse to one entity)."""
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni, address=f"contract:{d.contract_id}")


def cdp_code_particular(province_code: str) -> str:
    """Mint the per-province private-seller 'particular' bucket cdp_code via the canonical
    generator's particular path (canonical_key 'particular:cochesnet:{province}').

    coches.net anonymises privates -> the province code IS the seller id (the source
    withholds per-human identity). Deterministic over (platform, province) so re-runs are
    idempotent and a PRO dealer can never collide with the bucket. The cdp_code's province
    segment uses the SAME province (or '00' for the no-province fallback bucket)."""
    return cdp_code(province_code=province_code, particular_platform=COCHES_DOMAIN,
                    particular_seller_id=province_code)


async def upsert_dealer(conn: asyncpg.Connection, geo: GeoResolver, d: DealerRef) -> str | None:
    """Upsert the selling dealer entity (kind='compraventa', geo-resolved).
    Returns the dealer entity_ulid, or None if it cannot be geo-anchored."""
    if not d.province_code:
        return None
    if not (d.province_code.isdigit() and "01" <= d.province_code <= "52"):
        return None
    muni = geo.municipality_code(d.province_code, d.city)
    code = cdp_code_dealer(d, muni)
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, municipality_code, is_tier1, status, kind_source,
               sells_cars, first_discovered_source, last_seen)
           VALUES ($1,$2,'compraventa',$3,$3,$4,$5,FALSE,'active','platform_label',TRUE,$6, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()""",
        eulid, code, d.name, d.province_code, muni, COCHES_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, COCHES_SOURCE_KEY, d.contract_id)
    return eulid


async def upsert_vehicle(conn: asyncpg.Connection, dealer_ulid: str, v: Vehicle) -> tuple[str, bool]:
    """Upsert the vehicle OWNED BY the dealer (entity_ulid=dealer).
    Returns (vehicle_ulid, was_new). Idempotent on (entity_ulid, deep_link)."""
    row = await conn.fetchrow(
        "SELECT vehicle_ulid FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2",
        dealer_ulid, v.deep_link)
    if row is not None:
        vulid = row["vehicle_ulid"]
        await conn.execute(
            "UPDATE vehicle SET last_seen=now(), status='available' WHERE vehicle_ulid=$1", vulid)
        return vulid, False
    vulid = ulid()
    await conn.execute(
        """INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model,
               year, km, price, fuel, transmission, photo_url, vin_ref, status)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,'available')
           ON CONFLICT (entity_ulid, deep_link) DO NOTHING""",
        vulid, dealer_ulid, v.deep_link, v.title, v.make, v.model, v.year, v.km, v.price,
        v.fuel, v.transmission, v.photo_url, v.listing_ref)
    real = await conn.fetchval(
        "SELECT vehicle_ulid FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2",
        dealer_ulid, v.deep_link)
    return real, (real == vulid)


async def link_platform(conn: asyncpg.Connection, platform_ulid: str, vehicle_ulid: str,
                        v: Vehicle) -> bool:
    """INSERT the platform_listing edge (platform <-> vehicle). Idempotent.
    Returns True if a NEW edge was created."""
    inserted = await conn.fetchval(
        """INSERT INTO platform_listing (vehicle_ulid, platform_entity_ulid, listing_url,
               listing_ref, platform_price, status, first_seen, last_seen)
           VALUES ($1,$2,$3,$4,$5,'listed', now(), now())
           ON CONFLICT (vehicle_ulid, platform_entity_ulid)
             DO UPDATE SET last_seen = now(), status = 'listed',
                           platform_price = EXCLUDED.platform_price,
                           listing_ref = EXCLUDED.listing_ref
           RETURNING (xmax = 0) AS inserted""",
        vehicle_ulid, platform_ulid, v.deep_link, v.listing_ref, v.price)
    return bool(inserted)


async def emit_new_event(conn: asyncpg.Connection, vulid: str, dealer_ulid: str, v: Vehicle) -> None:
    """Emit the delta NEW event (same shape as pipeline.ingest). The coches.net
    price-drop history (priceDropData) is captured here — it is gold for delta."""
    payload = {"price": v.price, "title": v.title, "platform": COCHES_TRADE_NAME}
    if v.price_drop:
        payload["price_drop"] = v.price_drop
    await conn.execute(
        "INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type, "
        "old_value, new_value) VALUES ($1,$2,$3,'NEW',NULL,$4::jsonb)",
        ulid(), vulid, dealer_ulid, json.dumps(payload))


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# Default concurrency: pages fetched in parallel per sliding window. The governor
# (now 12 req/s for web.gw.coches.net) is the real limiter, so this only needs to be
# wide enough to keep the bucket saturated — ~15 in-flight requests comfortably feed a
# 12 req/s steady + 24 burst bucket without idle gaps. Higher just queues on the bucket.
DEFAULT_CONCURRENCY = 15


@dataclass
class _CageRow:
    """One fully-parsed, geo-anchored car ready for the bulk cage — the in-memory result
    of the parse+resolve phase, before any SQL. Carries everything the batched upserts need
    so the DB phase touches no per-item Python logic, only set-based statements.

    ONE row shape serves both owner kinds. A PROFESSIONAL seller -> owner_kind='compraventa'
    (sells_cars=TRUE, province+muni geo-resolved, source_ref=contractId). A PRIVATE seller ->
    owner_kind='particular' (the per-province bucket: sells_cars=TRUE, province=the INE code
    or NULL for the '00' fallback, no muni, source_ref='particular:{prov}'). Both mirror the
    platform's dealer rows (is_tier1=FALSE, source_group/role NULL, kind_source set by the
    bulk statement); only kind differs."""
    owner_cdp: str
    owner_kind: str               # 'compraventa' (dealer) | 'particular' (private bucket)
    owner_name: str | None
    owner_province: str | None    # INE code; NULL only for the '00' particular fallback bucket
    owner_muni: str | None        # dealers may have a muni; particular buckets never do
    source_ref: str               # dealer contractId | 'particular:{prov}' for the bucket
    vehicle: Vehicle


# The four bulk statements. Each is ONE round-trip per table per window (unnest-based
# multi-row upsert), replacing the ~400 serialized statements/page the row-by-row path did.
# The ON CONFLICT clauses are byte-for-byte the same idempotency the per-row path used, so
# a re-run of an already-harvested window adds 0 rows and 0 events.

_BULK_UPSERT_OWNERS = """
INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
        province_code, municipality_code, is_tier1, status, kind_source,
        sells_cars, first_discovered_source, last_seen)
SELECT u.entity_ulid, u.cdp_code, u.kind::entity_kind, u.name, u.name,
       u.province_code, u.municipality_code, FALSE, 'active', 'platform_label',
       TRUE, $8, now()
  FROM unnest($1::text[], $2::text[], $3::text[], $4::char(2)[], $5::char(5)[],
              $6::text[], $7::text[]) AS u(entity_ulid, cdp_code, name, province_code,
                               municipality_code, source_ref, kind)
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


def _province_name(prov: str | None, prov_names: dict[str, str]) -> str:
    """The human province label for a particular bucket's trade_name. Falls back to a stable
    'ES' label for the '00' no-province bucket so the entity name is never empty."""
    if not prov:
        return "ES"
    return prov_names.get(prov, prov)


def _parse_window(items_by_page: list[tuple[int, list]], geo: GeoResolver,
                  prov_names: dict[str, str], seen_ids: set, harvested_cageable: set,
                  stats: dict) -> list[_CageRow]:
    """Parse + geo-resolve every item across the window IN PAGE ORDER — pure CPU, no SQL.

    This is the per-item gate (cross-page dedup, geo gate, cageable truth), lifted out of the
    DB loop so the SQL phase is purely set-based. Both owner kinds are produced here as one
    uniform _CageRow stream:

      * PROFESSIONAL seller -> kind='compraventa' (geo-resolved dealer; a bad province is
        skipped so a dealer is never minted without a real INE anchor — the dealer's identity
        IS its location, so an unanchored dealer is junk).
      * PRIVATE seller -> kind='particular' (the per-province bucket). coches.net anonymises
        privates, so we NEVER drop the car: a missing/invalid province buckets the car under
        the '00' fallback (province_code NULL on the entity, '00' in the cdp_code) rather than
        skipping it. A private car is real inventory a buyer can purchase — it must be served.

    `seen_ids`/`harvested_cageable`/`stats` are mutated with deterministic page-order
    semantics, so the VAM truth (distinct (owner_cdp, deep_link) pairs) stays exact."""
    rows: list[_CageRow] = []
    for _page, items in items_by_page:
        for item in items:
            stats["items_seen"] += 1
            item_id = str(item.get("id") or "")
            if item_id and item_id in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue  # cross-page dedup (stable-sort hazard guard)
            if item_id:
                seen_ids.add(item_id)

            v = parse_item_vehicle(item)
            if not v.deep_link:
                continue
            if v.price_drop:
                stats["price_drops_captured"] += 1

            d = parse_item_dealer(item)
            if d is not None:
                # ---- PROFESSIONAL: a real selling dealer. Geo gate (same range guard
                # upsert_dealer applied) — a bad province skips the dealer without touching DB.
                stats["dealer_items"] += 1
                if not d.province_code:
                    stats["geo_skipped"] += 1
                    continue
                if not (d.province_code.isdigit() and "01" <= d.province_code <= "52"):
                    stats["geo_skipped"] += 1
                    continue
                muni = geo.municipality_code(d.province_code, d.city)
                owner_cdp = cdp_code_dealer(d, muni)
                harvested_cageable.add((owner_cdp, v.deep_link))
                rows.append(_CageRow(
                    owner_cdp=owner_cdp, owner_kind="compraventa", owner_name=d.name,
                    owner_province=d.province_code, owner_muni=muni,
                    source_ref=d.contract_id, vehicle=v))
            else:
                # ---- PRIVATE: cage into the per-province 'particular' bucket. Never dropped.
                stats["private_caged"] += 1
                loc = item.get("location") or {}
                prov = _prov2(loc.get("mainProvinceId"))  # None -> fallback bucket '00'
                bucket_prov = prov or PARTICULAR_PROVINCE_FALLBACK
                owner_cdp = cdp_code_particular(bucket_prov)
                pname = _province_name(prov, prov_names)
                harvested_cageable.add((owner_cdp, v.deep_link))
                rows.append(_CageRow(
                    owner_cdp=owner_cdp, owner_kind=PARTICULAR_KIND,
                    owner_name=f"{PARTICULAR_NAME_PREFIX} {pname}",
                    # entity.province_code is a geo_province FK -> NULL for the '00' bucket
                    # (the '00' lives only in the cdp_code string, same as the platform entity).
                    owner_province=prov,
                    owner_muni=None,
                    source_ref=f"particular:{bucket_prov}", vehicle=v))
    return rows


async def _ingest_window(conn: asyncpg.Connection, geo: GeoResolver,
                         prov_names: dict[str, str], platform_ulid: str,
                         items_by_page: list[tuple[int, list]], seen_ids: set,
                         harvested_cageable: set, stats: dict) -> None:
    """BULK-ingest a whole concurrent page-window in ONE transaction with set-based SQL.

    Replaces the ~400-statements-per-page row-by-row drain with ONE round-trip per table
    per window (unnest multi-row upserts). The delta/VAM/platform_listing semantics are
    preserved EXACTLY: same ON CONFLICT idempotency, same cageable truth, same NEW-event
    rule (emitted only for genuinely new vehicles), same price-drop capture in the payload.
    A re-run of an already-harvested window adds 0 rows and 0 events.

    Phases inside the single transaction:
      1) parse+geo-resolve in memory (no SQL) -> cageable _CageRow list
      2) dedup dealers by cdp_code, bulk-upsert dealers + entity_source, map cdp_code->ulid
      3) split vehicles into existing vs new (one SELECT), bulk-touch existing, bulk-insert
         new (with a Python-minted ulid each), confirm which inserts actually landed
      4) bulk-upsert platform_listing edges (RETURNING counts the genuinely new edges)
      5) bulk-insert NEW delta events for the genuinely new vehicles only
    """
    cage = _parse_window(items_by_page, geo, prov_names, seen_ids, harvested_cageable, stats)
    if not cage:
        return

    async with conn.transaction():
        # ---- (2) OWNERS (dealers + particular buckets): dedup by cdp_code within the window,
        # bulk-upsert (kind-aware), resolve ulids. Both kinds flow through ONE upsert.
        owners: dict[str, _CageRow] = {}
        for r in cage:
            owners.setdefault(r.owner_cdp, r)  # first occurrence wins (deterministic)
        d_ulids = [ulid() for _ in owners]
        d_cdps = list(owners.keys())
        d_names = [owners[c].owner_name for c in d_cdps]
        d_provs = [owners[c].owner_province for c in d_cdps]
        d_munis = [owners[c].owner_muni for c in d_cdps]
        d_refs = [owners[c].source_ref for c in d_cdps]
        d_kinds = [owners[c].owner_kind for c in d_cdps]
        await conn.execute(_BULK_UPSERT_OWNERS, d_ulids, d_cdps, d_names, d_provs,
                           d_munis, d_refs, d_kinds, COCHES_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_OWNER_SOURCES, d_cdps, d_refs, COCHES_SOURCE_KEY)
        cdp_to_ulid: dict[str, str] = {
            row["cdp_code"]: row["entity_ulid"]
            for row in await conn.fetch(
                "SELECT cdp_code, entity_ulid FROM entity "
                "WHERE cdp_code = ANY($1::text[])", d_cdps)
        }

        # ---- attach the resolved owner_ulid to each cage row; dedup cars within the window
        # by (owner_ulid, deep_link) so the same ad seen twice in one window is one car.
        cars: dict[tuple[str, str], _CageRow] = {}
        for r in cage:
            du = cdp_to_ulid.get(r.owner_cdp)
            if du is None:
                continue  # owner upsert race-impossible here, but stay defensive
            key = (du, r.vehicle.deep_link)
            if key not in cars:
                cars[key] = r

        # ---- (3) VEHICLES: one SELECT splits existing vs new (idempotency truth). Existing
        # -> bulk touch (last_seen/status). New -> Python-minted ulid + bulk insert.
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
            # Confirm which minted ulids actually landed (ON CONFLICT DO NOTHING could drop
            # one if a concurrent writer inserted the same (entity,deep_link) first). Only a
            # confirmed-new vehicle is counted new + gets a NEW event — preserves idempotency.
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
                    # our insert was conflicted away by a row we can't see in this tx snapshot;
                    # re-resolve so the edge/stat still points at a real vehicle.
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

        # ---- (5) NEW delta events — only for genuinely new vehicles, price-drop preserved.
        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                v = cars[k].vehicle
                payload = {"price": v.price, "title": v.title, "platform": COCHES_TRADE_NAME}
                if v.price_drop:
                    payload["price_drop"] = v.price_drop
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
    # One coherent curl_cffi session PER concurrency slot (a single shared session is not
    # thread-safe under the governor's to_thread fetch). The governor's per-host bucket
    # still bounds the aggregate rate across the whole pool, so widening the pool widens
    # parallelism WITHOUT out-pacing the host.
    fetcher = CochesFetcher(pool_size=concurrency)
    stats = {
        "pages_fetched": 0, "items_seen": 0, "dealer_items": 0,
        "private_caged": 0, "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "price_drops_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "dealers_distinct": 0,
        "particular_buckets": 0, "new_particular_buckets": 0, "concurrency": concurrency,
    }
    # Harvest-side truth for the VAM: distinct CAGEABLE cars = distinct
    # (contract_id, deep_link) pairs that survived dealer-parse + geo-resolution.
    # Like-with-like vs db_edges (raw ids include private sellers + cross-page dupes).
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if coches.net's breaker is OPEN (a recent ban/throttle still
    # cooling), skip the drain gracefully — the API keeps serving the last snapshot.
    if await is_open(conn, COCHES_SOURCE_KEY):
        print(f"[coches_net_wholesale] breaker OPEN for {COCHES_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, API still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": COCHES_SOURCE_KEY}

    # GOVERNOR: the single per-host choke point. wrap_fetch_text takes our POST
    # callable; every page passes through web.gw.coches.net's token bucket, off the
    # event loop. No matter how many pages are in flight, the host is never hammered:
    # the bucket (now 12 req/s for this JSON host) is the limiter, not Python's awaits.
    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        # code -> human province label, for the particular bucket trade_name (e.g.
        # '28' -> 'Madrid'). Loaded once per run; the '00' fallback bucket uses 'ES'.
        prov_names = {r["code"]: r["name"]
                      for r in await conn.fetch("SELECT code, name FROM geo_province")}
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = coches_platform_cdp_code()
        print(f"[coches_net_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid})")
        print(f"[coches_net_wholesale] governor paces host {host_of(ENDPOINT)} (per-host token bucket).")
        print(f"[coches_net_wholesale] CONCURRENT drain: window={concurrency} pages in flight "
              f"(governor is the limiter). Target = {max_pages} pages (~{max_pages * PAGE_SIZE} cars).")

        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa' "
            "AND first_discovered_source=$1", COCHES_SOURCE_KEY)}
        # Scope the bucket-delta to THIS connector's own particulares. Other connectors
        # (wallapop, milanuncios) write their own kind='particular' rows concurrently, so a
        # global count would attribute their buckets to this run. first_discovered_source
        # pins the count to coches.net's contribution only.
        particulars_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='particular' "
            "AND first_discovered_source=$1", COCHES_SOURCE_KEY)}

        # CONCURRENT sliding-window drain. Each window fetches up to `concurrency` pages
        # in parallel through the governor (the host bucket paces the aggregate), then the
        # pages are INGESTED sequentially in page order through the single asyncpg
        # connection. Fetch is the slow leg (network + bucket); ingest is fast and DB-bound,
        # so overlapping fetches while ingesting the previous window is where the speed is.
        # A page that errors or comes back empty stops the drain honestly (end of data or a
        # throttle the breaker must catch) — the same stop semantics as the sequential loop.
        stop = False
        next_page = max(1, start_page)
        while next_page <= max_pages and not stop:
            window = list(range(next_page, min(next_page + concurrency, max_pages + 1)))
            next_page = window[-1] + 1

            # fan-out: fetch every page in this window concurrently, paced by the bucket.
            results = await asyncio.gather(
                *(fetcher.fetch_page_async(governed_fetch, ENDPOINT, page=p, size=PAGE_SIZE)
                  for p in window),
                return_exceptions=True,
            )

            # fan-in: collect the window's pages IN PAGE ORDER (so dedup + counts stay
            # deterministic), then BULK-ingest the whole window in ONE transaction. A failed
            # or empty page stops the drain after the in-order pages before it are ingested.
            window_pages: list[tuple[int, list]] = []
            for page, data in zip(window, results):
                if isinstance(data, Exception):
                    fetch_error = str(data)
                    last_http = fetcher.last_status
                    print(f"[coches_net_wholesale] page {page} fetch failed ({data}); stopping drain honestly.")
                    stop = True
                    break
                meta = data.get("meta") or {}
                if stats["declared_full"] is None:
                    stats["declared_full"] = _to_int(meta.get("totalResults"))
                items = data.get("items") or []
                if not items:
                    print(f"[coches_net_wholesale] page {page}: no items; stopping.")
                    stop = True
                    break
                window_pages.append((page, items))

            if window_pages:
                # ONE transaction, set-based SQL: ~6 statements for the whole window instead
                # of ~400 per page. Idempotency/delta/VAM semantics are byte-identical.
                await _ingest_window(conn, geo, prov_names, platform_ulid, window_pages,
                                     seen_ids, harvested_cageable, stats)
                stats["pages_fetched"] += len(window_pages)
                first_p, last_p = window_pages[0][0], window_pages[-1][0]
                print(f"[coches_net_wholesale] window pages {first_p}-{last_p}: "
                      f"items={sum(len(it) for _, it in window_pages)} "
                      f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                      f"edges={stats['edges_created']}")

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa' "
            "AND first_discovered_source=$1", COCHES_SOURCE_KEY)}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        particulars_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='particular' "
            "AND first_discovered_source=$1", COCHES_SOURCE_KEY)}
        stats["new_particular_buckets"] = len(particulars_after - particulars_before)
        # distinct particular buckets that actually OWN a coches.net-listed car this run.
        stats["particular_buckets"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               JOIN entity e ON e.entity_ulid = v.entity_ulid
               WHERE pl.platform_entity_ulid = $1 AND e.kind='particular'""", platform_ulid)
        # distinct OWNERS (dealers + particular buckets) reachable via the edge join.
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, COCHES_PLATFORM_RECIPE)
        print(f"[coches_net_wholesale] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths that
        # all measure "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for coches.net (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join     (DB read truth)
        #   harvested_cageable = distinct (owner_cdp, deep_link) pulled  (harvest truth)
        #                        — owner = dealer cdp OR particular-bucket cdp.
        # The declared full count (272k) is reported for honesty but is NOT a quorum
        # path (it measures the WHOLE platform, not this slice).
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

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks coches.net,
        # trips the breaker on a ban, and auto-repairs. OK when >=1 page fetched, no fetch
        # error stopped the drain, and the VAM did not refute.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        # B9 coverage gate: declared_full = meta.totalResults from first page response.
        # harvested_cageable = distinct (owner_cdp, deep_link) pairs from the drain.
        outcome = await record_run(
            conn, COCHES_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http,
            declared_total=stats.get("declared_full"),
            captured_distinct=stats.get("harvested_cageable"),
            platform_ulid=platform_ulid)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, COCHES_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[coches_net_wholesale] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("COCHES.NET WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  declared full (source): {stats.get('declared_full')}")
    print(f"  concurrency (window)  : {stats.get('concurrency')} pages in flight")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  dealer items          : {stats['dealer_items']}")
    print(f"  private caged         : {stats['private_caged']} (-> per-province particular bucket)")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page)")
    print(f"  geo skipped (bad prov): {stats['geo_skipped']} (dealers only; privates never dropped)")
    print(f"  owners attributed     : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new dealers this run)")
    print(f"  particular buckets    : {stats.get('particular_buckets')} distinct "
          f"({stats.get('new_particular_buckets')} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for coches.net = {stats.get('db_edges')})")
    print(f"  price drops captured  : {stats['price_drops_captured']}")
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
    parser = argparse.ArgumentParser(description="coches.net wholesale harvester (concurrent JSON-API drain)")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"pages to harvest (size={PAGE_SIZE}); default {DEFAULT_MAX_PAGES}")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"pages fetched in parallel per sliding window; default "
                              f"{DEFAULT_CONCURRENCY}. The governor's per-host bucket is the "
                              f"real limiter — this only needs to keep the bucket saturated."))
    parser.add_argument("--start-page", type=int, default=1,
                        help="first page to fetch (skip already-harvested pages for an efficient top-up)")
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.pages, args.concurrency, args.start_page))
    _print_report(stats)


if __name__ == "__main__":
    main()
