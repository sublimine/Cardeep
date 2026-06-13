"""coches.net SEGMENT harvester — the NEW / KM0 / RENTING offer surfaces, end to end.

The used (Ocasión) catalog already flows through `coches_net_wholesale` (272k cars via
`POST web.gw.coches.net/search`). coches.net ALSO sells three more offer segments that
the public SRP exposes at `/nuevo/` `/km-0/` `/renting/` — but those HTML routes return
HTTP 405 to curl_cffi AND to a full stealth browser (camoufox): the route itself is
method/route-blocked, not JS-challenged.

The data, however, never comes from that HTML. The SRP is a client-side SPA that fetches
its listings from the SAME gateway the used drain uses — only with a DIFFERENT request
SCHEMA. The used connector POSTs a FLAT body (categoryId + pagination). The segment SRPs
POST a WRAPPED body: {pagination, sort, filters:{...}} where filters.offerTypeIds selects
the segment. That wrapped schema was discovered by warming the SPA in camoufox (land on
the working homepage, then client-side-navigate via the SPA router so NO 405 document GET
happens) and intercepting the real gateway XHR. Discovery is browser-only and ONE-TIME;
the gateway answers the wrapped body for plain curl_cffi (no browser, no proxy, no
cookies) exactly as it does for the flat body. Verified live 2026-06-13:

    new      filters.offerTypeIds=[1]          -> 6151  (offerType.literal 'Nuevo')
    km0      filters.offerTypeIds=[2,3,4,5]    -> 3105  (offerType.literal 'Km0')
    renting  filters.offerTypeIds=[10]         -> 1302  (offerType.literal 'Subscription')

Every car here is DEALER-OWNED (segment items are professional inventory: 30/30 sampled
items carried seller.contractId). They are caged through the SAME dual-membership model
as the used drain — coches.net platform entity, the selling dealer (kind='compraventa',
geo-resolved), the vehicle owned by that dealer, and a platform_listing edge — with the
edge STAMPED with `segment` (new|km0|renting) via the 0019 migration's column. The same
parse/geo/cage primitives are REUSED from coches_net_wholesale, so this is one more
surface on one architecture, not a fork of it.

Run:
    python -m pipeline.platform.coches_net_segments              # all three segments, full
    python -m pipeline.platform.coches_net_segments --segment new
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys

import asyncpg
from curl_cffi import requests as cffi_requests

from pipeline.engine.governor import governor, host_of
from pipeline.geo import GeoResolver
from pipeline.ids import ulid
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict

from pipeline.platform.coches_net_wholesale import (
    DSN, ENDPOINT, PAGE_SIZE, CATEGORY_CARS, COCHES_SOURCE_KEY, COCHES_TRADE_NAME,
    _HEADERS, _IMPERSONATE, _TIMEOUT,
    _CageRow, _parse_window, parse_item_vehicle,
    coches_platform_cdp_code, ensure_platform_entity,
    COCHES_PLATFORM_RECIPE, _force_utf8_stdout,
)

# ---------------------------------------------------------------------------
# Segment taxonomy — ground truth from the live SPA gateway capture (2026-06-13).
# Each segment is the SAME /search endpoint with a DIFFERENT filters.offerTypeIds.
# `referer` mirrors the SRP the SPA navigates to (the gateway honours it as the slice
# context); `segment` is the value stamped on the platform_listing edge.
# ---------------------------------------------------------------------------
SEGMENTS: dict[str, dict] = {
    "new": {
        "segment": "new",
        "offer_type_ids": [1],
        "referer": "https://www.coches.net/nuevo/",
        "expected_literal": "Nuevo",
    },
    "km0": {
        "segment": "km0",
        "offer_type_ids": [2, 3, 4, 5],
        "referer": "https://www.coches.net/km-0/",
        "expected_literal": "Km0",
    },
    "renting": {
        "segment": "renting",
        "offer_type_ids": [10],
        "referer": "https://www.coches.net/renting/",
        "expected_literal": "Subscription",
    },
}

# The WRAPPED request envelope the segment SRPs send (verified live). All filter fields
# are present-but-open exactly as the SPA sends them; only offerTypeIds (and the cars
# category) carry the slice. A leaner body works too, but we mirror the SPA byte-shape so
# the gateway sees an indistinguishable request.
SORT = {"order": "desc", "term": "relevance"}


def _segment_payload(offer_type_ids: list[int], page: int, size: int) -> dict:
    """Build the wrapped {pagination, sort, filters} body for an offer segment.

    The gateway IGNORES a flat top-level offerTypeIds (that is why the used connector's
    flat schema never selected a segment); the slice ONLY takes effect inside `filters`.
    `categories.category1Ids=[2500]` scopes to turismos exactly like the used drain.
    """
    return {
        "pagination": {"page": page, "size": size},
        "sort": SORT,
        "filters": {
            "categories": {"category1Ids": [CATEGORY_CARS]},
            "offerTypeIds": offer_type_ids,
            "price": {"from": None, "to": None},
            "year": {"from": None, "to": None},
            "km": {"from": None, "to": None},
        },
    }


class SegmentFetcher:
    """A POOL of fingerprint-coherent curl_cffi POST sessions, one per concurrency slot.

    Identical pooling contract to CochesFetcher (a single curl_cffi Session is not
    thread-safe under the governor's to_thread fetch), but it POSTs the WRAPPED segment
    body. The per-host token bucket still bounds the aggregate rate across the pool.
    """

    def __init__(self, offer_type_ids: list[int], referer: str, pool_size: int = 1) -> None:
        self._offer_type_ids = offer_type_ids
        self._headers = dict(_HEADERS)
        self._headers["Referer"] = referer
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch_page(self, url: str, *, page: int = 1, size: int = PAGE_SIZE,
                   slot: int = 0) -> dict:
        session = self._sessions[slot]
        resp = session.post(url, json=_segment_payload(self._offer_type_ids, page, size),
                            headers=self._headers, impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url} (page {page})")
        return json.loads(resp.content.decode("utf-8"))

    async def fetch_page_async(self, governed_fetch, url: str, *, page: int,
                               size: int = PAGE_SIZE) -> dict:
        slot = await self._free.get()
        try:
            return await governed_fetch(url, page=page, size=size, slot=slot)
        finally:
            self._free.put_nowait(slot)


# A segment-aware edge upsert: same idempotency as the used path, plus the `segment`
# stamp (0019 migration). One round-trip per window (unnest multi-row upsert).
_BULK_UPSERT_SEGMENT_EDGES = """
INSERT INTO platform_listing (vehicle_ulid, platform_entity_ulid, listing_url,
        listing_ref, platform_price, segment, status, first_seen, last_seen)
SELECT u.vehicle_ulid, $5, u.listing_url, u.listing_ref, u.platform_price,
       $6, 'listed', now(), now()
  FROM unnest($1::text[], $2::text[], $3::text[], $4::numeric[])
       AS u(vehicle_ulid, listing_url, listing_ref, platform_price)
ON CONFLICT (vehicle_ulid, platform_entity_ulid)
  DO UPDATE SET last_seen = now(), status = 'listed',
                platform_price = EXCLUDED.platform_price,
                listing_ref = EXCLUDED.listing_ref,
                segment = EXCLUDED.segment
RETURNING (xmax = 0) AS inserted
"""

# Reuse the used connector's owner/source/vehicle/event bulk statements verbatim — the
# only edge-shape difference is the segment column above.
from pipeline.platform.coches_net_wholesale import (  # noqa: E402
    _BULK_UPSERT_OWNERS, _BULK_UPSERT_OWNER_SOURCES, _BULK_INSERT_VEHICLES,
    _BULK_TOUCH_VEHICLES, _BULK_INSERT_EVENTS,
)


async def _ingest_segment_window(conn, geo, prov_names, platform_ulid, segment,
                                 items_by_page, seen_ids, harvested_cageable, stats) -> None:
    """BULK-ingest one page-window for a segment in ONE transaction, set-based SQL.

    Mirrors coches_net_wholesale._ingest_window EXACTLY (owners -> vehicles -> edges ->
    NEW events) but stamps the edge with `segment`. The dual-membership, idempotency,
    delta and VAM semantics are byte-identical to the used path."""
    cage = _parse_window(items_by_page, geo, prov_names, seen_ids, harvested_cageable, stats)
    if not cage:
        return

    async with conn.transaction():
        owners: dict[str, _CageRow] = {}
        for r in cage:
            owners.setdefault(r.owner_cdp, r)
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
                "SELECT cdp_code, entity_ulid FROM entity WHERE cdp_code = ANY($1::text[])",
                d_cdps)
        }

        cars: dict[tuple[str, str], _CageRow] = {}
        for r in cage:
            du = cdp_to_ulid.get(r.owner_cdp)
            if du is None:
                continue
            key = (du, r.vehicle.deep_link)
            if key not in cars:
                cars[key] = r

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
                    "SELECT vehicle_ulid, entity_ulid, deep_link FROM vehicle "
                    "WHERE vehicle_ulid = ANY($1::text[])",
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

        e_vehicles = [vehicle_ulid_for[k] for k in car_keys]
        e_urls = [cars[k].vehicle.deep_link for k in car_keys]
        e_refs = [cars[k].vehicle.listing_ref for k in car_keys]
        e_prices = [cars[k].vehicle.price for k in car_keys]
        edge_rows = await conn.fetch(_BULK_UPSERT_SEGMENT_EDGES, e_vehicles, e_urls, e_refs,
                                     e_prices, platform_ulid, segment)
        stats["edges_created"] += sum(1 for row in edge_rows if row["inserted"])

        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                v = cars[k].vehicle
                payload = {"price": v.price, "title": v.title,
                           "platform": COCHES_TRADE_NAME, "segment": segment}
                if v.price_drop:
                    payload["price_drop"] = v.price_drop
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities,
                               ev_payloads)
            stats["new_events"] += len(confirmed_new)


async def harvest_segment(conn, geo, prov_names, platform_ulid, name: str,
                          concurrency: int) -> dict:
    """Drain ONE segment fully (the segments are small: 1.3k-6.2k cars), caging dealers,
    vehicles and segment-stamped edges. Returns this segment's stats slice."""
    cfg = SEGMENTS[name]
    fetcher = SegmentFetcher(cfg["offer_type_ids"], cfg["referer"], pool_size=concurrency)
    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    stats = {
        "segment": name, "pages_fetched": 0, "items_seen": 0, "dealer_items": 0,
        "private_caged": 0, "geo_skipped": 0, "cars_caged": 0, "new_cars": 0,
        "edges_created": 0, "new_events": 0, "price_drops_captured": 0,
        "dup_ids_collapsed": 0, "declared_full": None,
    }
    seen_ids: set[str] = set()
    harvested_cageable: set[tuple[str, str]] = set()

    # First page: learn meta.totalResults/totalPages and confirm the slice is the
    # expected offer segment (anti-hallucination: the offerType literal must match).
    first = fetcher.fetch_page(ENDPOINT, page=1, size=PAGE_SIZE)
    meta = first.get("meta") or {}
    stats["declared_full"] = meta.get("totalResults")
    total_pages = meta.get("totalPages") or 1
    items0 = first.get("items") or []
    literals = {(i.get("offerType") or {}).get("literal") for i in items0[:10]}
    stats["offer_literals_seen"] = sorted(x for x in literals if x)
    if cfg["expected_literal"] not in literals and items0:
        print(f"[segments] WARN {name}: expected offerType '{cfg['expected_literal']}' "
              f"but saw {literals}; proceeding (gateway is source of truth).")
    print(f"[segments] {name}: declared total={stats['declared_full']} pages={total_pages} "
          f"literals={stats['offer_literals_seen']}")

    # ingest page 1, then drain the rest in concurrent windows.
    await _ingest_segment_window(conn, geo, prov_names, platform_ulid, name,
                                 [(1, items0)], seen_ids, harvested_cageable, stats)
    stats["pages_fetched"] += 1

    next_page = 2
    stop = False
    while next_page <= total_pages and not stop:
        window = list(range(next_page, min(next_page + concurrency, total_pages + 1)))
        next_page = window[-1] + 1
        results = await asyncio.gather(
            *(fetcher.fetch_page_async(governed_fetch, ENDPOINT, page=p, size=PAGE_SIZE)
              for p in window),
            return_exceptions=True)
        window_pages: list[tuple[int, list]] = []
        for page, data in zip(window, results):
            if isinstance(data, Exception):
                print(f"[segments] {name} page {page} failed ({data}); stopping segment.")
                stop = True
                break
            items = data.get("items") or []
            if not items:
                stop = True
                break
            window_pages.append((page, items))
        if window_pages:
            await _ingest_segment_window(conn, geo, prov_names, platform_ulid, name,
                                         window_pages, seen_ids, harvested_cageable, stats)
            stats["pages_fetched"] += len(window_pages)
            print(f"[segments] {name} pages {window_pages[0][0]}-{window_pages[-1][0]}: "
                  f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                  f"edges={stats['edges_created']}")

    stats["harvested_cageable"] = len(harvested_cageable)
    stats["harvested_distinct_ids"] = len(seen_ids)
    # DB read-truth for THIS segment slice (edges stamped with this segment on this platform).
    stats["db_segment_edges"] = await conn.fetchval(
        "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1 AND segment=$2",
        platform_ulid, name)
    return stats


async def harvest(segments: list[str], concurrency: int = 8) -> dict:
    conn = await asyncpg.connect(DSN)
    try:
        if await is_open(conn, COCHES_SOURCE_KEY):
            print(f"[segments] breaker OPEN for {COCHES_SOURCE_KEY}; skipping.")
            return {"skipped": True, "reason": "breaker_open"}

        geo = await GeoResolver.load(conn)
        prov_names = {r["code"]: r["name"]
                      for r in await conn.fetch("SELECT code, name FROM geo_province")}
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = coches_platform_cdp_code()
        print(f"[segments] platform entity ready: {platform_code} (ulid={platform_ulid})")
        print(f"[segments] governor paces host {host_of(ENDPOINT)}; segments={segments}")

        per_segment = {}
        last_http = None
        fetch_error = None
        for name in segments:
            try:
                per_segment[name] = await harvest_segment(
                    conn, geo, prov_names, platform_ulid, name, concurrency)
                last_http = 200
            except Exception as e:
                fetch_error = str(e)
                print(f"[segments] {name} ERROR: {e}")
                per_segment[name] = {"segment": name, "error": str(e)}

        # platform-wide segment distribution (DB truth across all segments).
        seg_dist = {r["segment"]: r["n"] for r in await conn.fetch(
            "SELECT segment, count(*) AS n FROM platform_listing "
            "WHERE platform_entity_ulid=$1 GROUP BY segment ORDER BY segment", platform_ulid)}

        # VAM quorum per segment: harvested_cageable == db_segment_edges.
        for name, s in per_segment.items():
            if "error" in s:
                continue
            verdict = await record_count_verdict(
                conn, subject_type="platform_segment_slice",
                subject_key=f"{platform_code}:{name}",
                claim=f"distinct cageable {name} cars (harvest) == segment edges (db)",
                paths={"harvested_cageable": s["harvested_cageable"],
                       "db_segment_edges": s["db_segment_edges"]},
                tolerance=0.02)
            s["verdict"] = verdict

        # recipe: extend the coches.net platform recipe with the segment surface.
        recipe = dict(COCHES_PLATFORM_RECIPE)
        recipe["segments"] = {
            "discovery": ("SPA gateway capture via camoufox: land homepage, client-side "
                          "navigate (SPA router) to /nuevo//km-0//renting/ to avoid the "
                          "405 document GET, intercept the real /search XHR. The wrapped "
                          "{pagination,sort,filters} body then works for plain curl_cffi."),
            "endpoint": "POST https://web.gw.coches.net/search (WRAPPED body)",
            "filter": "filters.offerTypeIds + filters.categories.category1Ids=[2500]",
            "map": {k: {"offerTypeIds": v["offer_type_ids"], "literal": v["expected_literal"]}
                    for k, v in SEGMENTS.items()},
            "edge_flag": "platform_listing.segment in (new,km0,renting)",
            "verified_live": "2026-06-13",
        }
        recipe_path = write_recipe(platform_code, recipe)

        total_caged = sum(s.get("cars_caged", 0) for s in per_segment.values())
        run_ok = fetch_error is None and total_caged > 0
        outcome = await record_run(conn, COCHES_SOURCE_KEY, ok=run_ok, rows=total_caged,
                                   error=fetch_error, http_status=last_http)

        return {
            "per_segment": per_segment,
            "platform_segment_distribution": seg_dist,
            "platform_code": platform_code,
            "platform_ulid": platform_ulid,
            "recipe_path": str(recipe_path),
            "health_status": outcome.status,
            "breaker_state": outcome.breaker_state,
        }
    finally:
        await conn.close()


def _print_report(result: dict) -> None:
    if result.get("skipped"):
        print(f"\n[segments] SKIPPED: {result.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("COCHES.NET SEGMENTS HARVEST — REPORT (new / km0 / renting)")
    print("=" * 64)
    print(f"  platform cdp_code     : {result.get('platform_code')}")
    for name, s in result["per_segment"].items():
        if "error" in s:
            print(f"  [{name}] ERROR: {s['error']}")
            continue
        print(f"  [{name}] declared={s.get('declared_full')} pages={s['pages_fetched']} "
              f"items={s['items_seen']} caged={s['cars_caged']} new={s['new_cars']} "
              f"edges={s['edges_created']}")
        print(f"        VAM: harvested_cageable={s.get('harvested_cageable')} "
              f"db_segment_edges={s.get('db_segment_edges')} verdict={s.get('verdict')}")
    print(f"  platform segment dist : {result.get('platform_segment_distribution')}")
    print(f"  health status         : {result.get('health_status')} / "
          f"breaker {result.get('breaker_state')}")
    print(f"  recipe                : {result.get('recipe_path')}")
    print("=" * 64)


def main() -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description="coches.net new/km0/renting segment harvester")
    ap.add_argument("--segment", choices=list(SEGMENTS), default=None,
                    help="harvest a single segment (default: all three)")
    ap.add_argument("--concurrency", type=int, default=8)
    args = ap.parse_args()
    segments = [args.segment] if args.segment else list(SEGMENTS)
    result = asyncio.run(harvest(segments, concurrency=args.concurrency))
    _print_report(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
