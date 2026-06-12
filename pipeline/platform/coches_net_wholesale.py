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
  each CAR                      -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the platform       -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the dealer); platform membership is plural (this edge). The
same physical car can carry BOTH an AS24 edge and a coches.net edge without ever
changing its owning dealer.

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
    """Parse the SELLING DEALER from an item's `seller` + `location`.

    Only professional sellers (isProfessional) with a contractId become entities;
    private sellers are skipped. Geo comes from the item's location, not the seller
    (the seller has no address on this surface)."""
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
    """A fingerprint-coherent curl_cffi POST session for the coches.net search API.

    One session == one Chrome fingerprint == one cookie jar for the whole drain, so
    the paginated harvest looks like one browser. The governor wraps `fetch_page` to
    pace requests by the host bucket; this class only performs the actual POST.
    """

    def __init__(self) -> None:
        self._session = cffi_requests.Session(impersonate=_IMPERSONATE)
        self.last_status: int | None = None

    @staticmethod
    def _payload(page: int, size: int) -> dict:
        # pagination is a NESTED object {page,size}; a top-level "page" is silently
        # ignored by the gateway (recipe root-caused this). price/year/km open.
        return {
            "categoryId": CATEGORY_CARS,
            "sortBy": "relevance",
            "sortOrder": "DESC",
            "pagination": {"page": page, "size": size},
            "price": {"from": None, "to": None},
            "year": {"from": None, "to": None},
            "km": {"from": None, "to": None},
        }

    def fetch_page(self, url: str, *, page: int = 1, size: int = PAGE_SIZE) -> dict:
        """POST the search request for `page` and return the decoded JSON dict.

        `url` is the endpoint (passed so the governor can derive the host and pace
        the bucket). Raises on a non-200 so the caller sees the failure (never masks
        a challenge/empty body — the breaker must catch throttling)."""
        resp = self._session.post(url, json=self._payload(page, size), headers=_HEADERS,
                                  impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url} (page {page})")
        # The API serves UTF-8 JSON; decode explicitly so accented fuel/city names
        # (Diésel, A Coruña) survive regardless of curl_cffi's encoding guess.
        return json.loads(resp.content.decode("utf-8"))


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


async def harvest(max_pages: int = DEFAULT_MAX_PAGES) -> dict:
    conn = await asyncpg.connect(DSN)
    fetcher = CochesFetcher()  # one fingerprint + cookie jar for the whole drain
    stats = {
        "pages_fetched": 0, "items_seen": 0, "dealer_items": 0,
        "private_skipped": 0, "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "price_drops_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "dealers_distinct": 0,
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
    # event loop. No matter how many drains run, the host is never hammered.
    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = coches_platform_cdp_code()
        print(f"[coches_net_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid})")
        print(f"[coches_net_wholesale] governor paces host {host_of(ENDPOINT)} (per-host token bucket).")
        print(f"[coches_net_wholesale] PROOF SLICE cap = {max_pages} pages "
              f"(~{max_pages * PAGE_SIZE} cars). NOT the full ~272k set (full drain = full governed run).")

        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        for page in range(1, max_pages + 1):
            try:
                data = await governed_fetch(ENDPOINT, page=page, size=PAGE_SIZE)
            except Exception as e:  # noqa: BLE001 — throttle/transient: back off, report
                fetch_error = str(e)
                last_http = fetcher.last_status
                print(f"[coches_net_wholesale] page {page} fetch failed ({e}); stopping drain honestly.")
                break
            stats["pages_fetched"] += 1
            meta = data.get("meta") or {}
            if stats["declared_full"] is None:
                stats["declared_full"] = _to_int(meta.get("totalResults"))
            items = data.get("items") or []
            if not items:
                print(f"[coches_net_wholesale] page {page}: no items; stopping.")
                break

            for item in items:
                stats["items_seen"] += 1
                item_id = str(item.get("id") or "")
                if item_id and item_id in seen_ids:
                    stats["dup_ids_collapsed"] += 1
                    continue  # cross-page dedup (stable-sort hazard guard)
                if item_id:
                    seen_ids.add(item_id)

                d = parse_item_dealer(item)
                if d is None:
                    stats["private_skipped"] += 1
                    continue
                stats["dealer_items"] += 1

                async with conn.transaction():
                    dealer_ulid = await upsert_dealer(conn, geo, d)
                    if dealer_ulid is None:
                        stats["geo_skipped"] += 1
                        continue
                    v = parse_item_vehicle(item)
                    if not v.deep_link:
                        continue
                    harvested_cageable.add((d.contract_id, v.deep_link))
                    vulid, veh_new = await upsert_vehicle(conn, dealer_ulid, v)
                    stats["cars_caged"] += 1
                    if v.price_drop:
                        stats["price_drops_captured"] += 1
                    if veh_new:
                        stats["new_cars"] += 1
                        await emit_new_event(conn, vulid, dealer_ulid, v)
                        stats["new_events"] += 1
                    edge_new = await link_platform(conn, platform_ulid, vulid, v)
                    if edge_new:
                        stats["edges_created"] += 1

            print(f"[coches_net_wholesale] page {page}: items={len(items)} "
                  f"caged_total={stats['cars_caged']} edges={stats['edges_created']}")

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
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
        #   harvested_cageable = distinct (contract, deep_link) pulled   (harvest truth)
        # The declared full count (272k) is reported for honesty but is NOT a quorum
        # path (it measures the WHOLE platform, not this 5-page slice).
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
        outcome = await record_run(
            conn, COCHES_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
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
    print("COCHES.NET WHOLESALE HARVEST — PROOF SLICE REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  declared full (source): {stats.get('declared_full')}  (NOT harvested — proof slice)")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  dealer items          : {stats['dealer_items']}")
    print(f"  private skipped       : {stats['private_skipped']}")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page)")
    print(f"  geo skipped (bad prov): {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
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


def main() -> None:
    parser = argparse.ArgumentParser(description="coches.net wholesale proof-slice harvester")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"pages to harvest (size={PAGE_SIZE}); default {DEFAULT_MAX_PAGES} (proof slice)")
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.pages))
    _print_report(stats)


if __name__ == "__main__":
    main()
