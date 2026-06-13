"""wallapop FACET-PARTITION harvester — breaks the flat-cursor depth ceiling.

THE PROBLEM. wallapop's `GET api.wallapop.com/api/v3/search/section` declares ~651k
ES cars (category_id=100; the live `remaining_documents` oracle, see below), but a
SINGLE undivided `order_by=newest` cursor saturates far short of that: a flat run
drains one ordering of the whole catalog from a fixed default centroid and caps
(observed ~347k caged on the wholesale module's flat pass) well before
`remaining_documents -> 0`. That is a drain-DEPTH ceiling, not a coverage gap
(docs/architecture/segments/wallapop.md §4): every segment lives inside the one cat-100
catalog, so the missing cars are simply past the depth one cursor reaches.

THE FIX (verified live 2026-06-13 against the API, NOT assumed):
  1) READ THE COUNT ORACLE. The `meta.next_page` JWT carries
     `params.nextPageParams.pointers.ORGANIC.remaining_documents` — the live count of
     documents behind the cursor for the EXACT filtered view requested. A `limit`-free
     first-page GET therefore yields a precise per-cell denominator (the wallapop analogue
     of milanuncios `pagination.totalHits`). Baseline (no filter) reads 651,372.
  2) PARTITION BY SELLER TYPE. `seller_type` ∈ {professional, private} is a clean,
     server-honored 2-way split (professional 346,079 + private 305,253 = 651,332 ≈
     baseline — verified). Geo lat/long is NOT a real partition axis here: every centroid
     returns the SAME national pool (a Madrid centroid still serves Navarra/Zaragoza items;
     `distance`/`radius`/`max_distance` are silently ignored — verified), so unlike
     milanuncios's province axis, the geo grid does not shard wallapop. seller_type does.
  3) SUB-PARTITION BY PRICE BAND. `min_sale_price`/`max_sale_price` genuinely narrow the
     view (each band's `remaining_documents` is a real fraction of the seller-type total —
     verified). Each (seller_type × price band) cell is sized under a safe cursor depth;
     any cell still over the cap is RECURSIVELY bisected by price using the oracle until
     every leaf cell is drainable. seller_type × price band is a gap-free, count-provable
     partition; cross-cell overlap (a car at a band boundary, live jitter) is collapsed
     exactly once by the GLOBAL item-id dedup the cage already enforces (ON CONFLICT).

THE FACET REQUEST (the shape the API honors — verified live, distinct from the flat
shape the wholesale module sends):
    GET .../search/section?source=deep_link&category_id=100&order_by=newest
        &section_type=organic_search_results
        &seller_type={professional|private}
        &min_sale_price=F&max_sale_price=T
paged by the opaque `meta.next_page` JWT (replayed as &next_page=<jwt>), ~40 items/page,
to the cell's natural chain-end (an empty page) — exactly the wholesale `_drain_query` loop.

ARCHITECTURE REUSE. This module does NOT fork the harvest engine. It imports the
wholesale module's proven cage/parse/DB/identity layer wholesale — the memory-bounded
`_build_cage` (item-id dedup + per-seller attribution via cached `GET /users/{id}` +
geo-resolve), the unnest BATCH `_ingest_window` (the same ~6 set-based statements per
window), the per-host governor (api.wallapop.com in the JSON_API 12 req/s class), the
S-HEALTH breaker, the VAM count quorum, the dual-membership platform_listing model, and
the legacy-bucket cleanup. The ONLY additions here are: (a) the `remaining_documents`
oracle reader, (b) the recursive seller_type × price-band partition plan, and (c) a
partition loop that drains each cell through that same `_drain_query` machinery with the
GLOBAL `_RunState` (bounded seen_ids) so cross-cell overlap collapses exactly once. Delta
/ VAM / idempotency are preserved byte-for-byte (same ON CONFLICT, same NEW-event rule).

Run: python -m pipeline.platform.wallapop_facet
     python -m pipeline.platform.wallapop_facet --seller-types professional --concurrency 12
     python -m pipeline.platform.wallapop_facet --cell-max 30000 --target 250000
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import time
import uuid

import asyncpg

from pipeline.engine.governor import governor, host_of
from pipeline.geo import GeoResolver
from pipeline.geocode import ProvinceGeocoder
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict

# Reuse the wholesale module's proven machinery — parse, attribute, cage, bulk-ingest, identity.
from pipeline.platform.wallapop_wholesale import (
    CATEGORY_CARS,
    DSN,
    PAGE_ITEMS,
    SEARCH_ENDPOINT,
    WP_PLATFORM_RECIPE,
    WP_SOURCE_KEY,
    WP_TRADE_NAME,
    WallapopFetcher,
    _BoundedSeen,
    _RunState,
    _build_cage,
    _env_int,
    _ingest_window,
    cleanup_legacy_buckets,
    ensure_platform_entity,
    wallapop_platform_cdp_code,
)

# ---------------------------------------------------------------------------
# Partition plan (verified live 2026-06-13 — see module docstring).
# ---------------------------------------------------------------------------

# seller_type is the primary, server-honored split. Both kinds are sellable inventory and
# both are caged identically by the wholesale `_build_cage` (professional -> compraventa
# dealer, private -> per-seller particular); the param only narrows the view so each cursor
# is shorter. 'professional'/'private' are the ONLY accepted values (seller_type=normal ->
# HTTP 400, verified).
SELLER_TYPES: tuple[str, ...] = ("professional", "private")

# A cell whose remaining_documents exceeds this gets RECURSIVELY price-bisected until every
# leaf is at/under it. 40,000 is conservative: a flat cursor was verified to walk past offset
# 80,000 cleanly (no server cap at depth), so a 40k cell exhausts on its own chain-end with an
# order-of-magnitude of headroom. Env-overridable to tighten the ceiling per host pressure.
DEFAULT_CELL_MAX = _env_int("WP_CELL_MAX", 40_000)

# The seed price bands (EUR). (None = open end.) Verified to honor min_sale_price/max_sale_price
# and to keep most resulting cells under the cap; the few dense leaves (e.g. private 3000-5000,
# professional 12000-16000) are recursively bisected by `_split_band` using the live oracle.
SEED_PRICE_BANDS: tuple[tuple[int | None, int | None], ...] = (
    (None, 1000),
    (1000, 2000),
    (2000, 3000),
    (3000, 5000),
    (5000, 8000),
    (8000, 12000),
    (12000, 16000),
    (16000, 20000),
    (20000, 25000),
    (25000, 35000),
    (35000, 50000),
    (50000, None),
)

# Recursion floor: never bisect a band narrower than this many EUR. A 250-EUR-wide band that
# is still dense is a genuine price spike (many identical-priced cars); it is kept and drained
# to its natural chain-end (its own cursor still walks deep), logged as a residual.
MIN_BAND_WIDTH_EUR = 250

# The open top band's notional ceiling for bisection math only (cars priced above this are
# rare; the band stays open-ended on the wire). Used solely to pick a midpoint when splitting
# a (lo, None) band.
OPEN_TOP_CEILING_EUR = 200_000

# A hard page ceiling per cell — a guardrail, never expected to bite (a real cell ends on an
# empty page first). Sized for the densest leaf (~CELL_MAX/40 pages) plus headroom.
MAX_PAGES_PER_CELL = max(400, (DEFAULT_CELL_MAX // PAGE_ITEMS) + 400)


def _read_remaining(data: dict) -> int | None:
    """Read `pointers.ORGANIC.remaining_documents` from a section response's next_page JWT.

    The JWT is unsigned-read only (we never verify/forge it — we only decode the public
    claims the server put there). Returns the live document count behind the cursor for the
    EXACT filtered view, or None if the view has no next page (then the page's own item count
    is the whole cell). NO secret is read; this is the server's own published denominator."""
    nxt = (data.get("meta") or {}).get("next_page")
    if not nxt:
        return None
    try:
        payload = nxt.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        body = json.loads(base64.urlsafe_b64decode(payload))
        ptr = (((body.get("params") or {}).get("nextPageParams") or {})
               .get("pointers") or {}).get("ORGANIC") or {}
        rd = ptr.get("remaining_documents")
        return int(rd) if rd is not None else None
    except Exception:  # noqa: BLE001 — a malformed JWT just means "no oracle this probe".
        return None


def _cell_params(seller_type: str, lo: int | None, hi: int | None) -> dict:
    """The facet GET params for one (seller_type, price-band) cell — the verified shape."""
    p = {
        "source": "deep_link",
        "category_id": CATEGORY_CARS,
        "search_id": str(uuid.uuid4()),
        "order_by": "newest",
        "section_type": "organic_search_results",
        "seller_type": seller_type,
    }
    if lo is not None:
        p["min_sale_price"] = str(lo)
    if hi is not None:
        p["max_sale_price"] = str(hi)
    return p


# ---------------------------------------------------------------------------
# Partition planning — probe each cell's remaining_documents; recursively price-bisect any
# cell over the cap until every leaf is drainable. The coverage-proof spine.
# ---------------------------------------------------------------------------


async def _probe_remaining(fetcher: WallapopFetcher, governed_fetch, seller_type: str,
                           lo: int | None, hi: int | None) -> int | None:
    """One governed first-page GET -> the cell's live remaining_documents (the count oracle).

    Routed through the SAME per-host bucket as the drain (no second uncontrolled hammer). The
    first page also returns up to PAGE_ITEMS items, so a cell with no next_page is sized by
    that page directly (handled by the caller)."""
    try:
        data = await fetcher.fetch_async(governed_fetch, SEARCH_ENDPOINT,
                                         params=_cell_params(seller_type, lo, hi))
    except Exception:  # noqa: BLE001 — a failed probe -> treat as unknown (drain it anyway).
        return None
    rd = _read_remaining(data)
    if rd is not None:
        return rd
    # No next page: the cell fits on one page; its size is that page's item count.
    items = ((data.get("data") or {}).get("section") or {}).get("items") or []
    return len(items)


async def _split_band(fetcher: WallapopFetcher, governed_fetch, seller_type: str,
                      lo: int | None, hi: int | None, cell_max: int,
                      stats: dict) -> list[dict]:
    """Return the drainable leaf cells covering (seller_type, [lo,hi]) — recursively bisected.

    If the cell's remaining_documents <= cell_max it is a single leaf. Otherwise the price
    interval is bisected at its midpoint and each half is recursed. The recursion stops when a
    band is narrower than MIN_BAND_WIDTH_EUR (a genuine price spike: kept whole, drained to its
    own chain-end, counted as a residual). Every leaf carries its probed declared count so the
    coverage sum is provable."""
    rd = await _probe_remaining(fetcher, governed_fetch, seller_type, lo, hi)
    stats["probes"] += 1
    declared = rd if rd is not None else cell_max  # unknown -> assume worst, still drained
    if declared <= cell_max:
        return [{"seller_type": seller_type, "lo": lo, "hi": hi,
                 "declared": declared, "capped": False}]

    # Dense cell -> bisect by price. Determine a concrete [a, b] interval to split.
    a = lo if lo is not None else 0
    b = hi if hi is not None else OPEN_TOP_CEILING_EUR
    if (b - a) <= MIN_BAND_WIDTH_EUR:
        # cannot split further: a real price spike. Keep whole; its cursor still drains deep.
        stats["cells_capped"] += 1
        return [{"seller_type": seller_type, "lo": lo, "hi": hi,
                 "declared": declared, "capped": True}]
    mid = a + (b - a) // 2
    # round the midpoint to a tidy 100-EUR step so adjacent cells share clean boundaries.
    mid = max(a + MIN_BAND_WIDTH_EUR, (mid // 100) * 100)
    if mid <= a or mid >= b:
        mid = a + (b - a) // 2
    left = await _split_band(fetcher, governed_fetch, seller_type, lo, mid, cell_max, stats)
    # the right half keeps the ORIGINAL open top (hi may be None) so coverage stays gap-free.
    right = await _split_band(fetcher, governed_fetch, seller_type, mid, hi, cell_max, stats)
    return left + right


async def plan_partitions(fetcher: WallapopFetcher, governed_fetch,
                          seller_types: tuple[str, ...], cell_max: int,
                          stats: dict) -> tuple[list[dict], int]:
    """Build the drainable leaf-cell list and the summed declared coverage.

    For each seller_type, walk the seed price bands; recursively bisect any band over cell_max.
    coverage_sum is the capture-recapture path: sum of every leaf's declared count, compared
    against the baseline national declared (read once, reported for honesty)."""
    partitions: list[dict] = []
    coverage_sum = 0
    for st in seller_types:
        for lo, hi in SEED_PRICE_BANDS:
            leaves = await _split_band(fetcher, governed_fetch, st, lo, hi, cell_max, stats)
            partitions.extend(leaves)
            coverage_sum += sum(c["declared"] for c in leaves)
    return partitions, coverage_sum


async def _baseline_declared(fetcher: WallapopFetcher, governed_fetch) -> int | None:
    """The national declared total (no seller/price filter): baseline remaining_documents.

    Reported for honesty (the coverage floor); NOT a quorum path — the quorum is the three
    orthogonal DB counts of what actually landed."""
    try:
        data = await fetcher.fetch_async(governed_fetch, SEARCH_ENDPOINT, params={
            "source": "deep_link", "category_id": CATEGORY_CARS,
            "search_id": str(uuid.uuid4()), "order_by": "newest",
            "section_type": "organic_search_results"})
    except Exception:  # noqa: BLE001
        return None
    return _read_remaining(data)


# ---------------------------------------------------------------------------
# Orchestration — plan, then drain every cell through the shared `_drain_query` machinery,
# then the SAME VAM count quorum + S-HEALTH heartbeat + legacy cleanup the wholesale runs.
# ---------------------------------------------------------------------------

DEFAULT_CONCURRENCY = 12      # in-flight GETs per cell window; JSON_API governor bucket is the limiter.
DEFAULT_TARGET = 700_000      # cage the whole catalog by default (a cell ends naturally first).


async def _drain_cell(fetcher: WallapopFetcher, governed_fetch, conn, platform_ulid,
                      geo, geocoder, state, stats, cell: dict, target: int,
                      max_pages: int) -> tuple[bool, str | None, int | None]:
    """Drain ONE (seller_type, price-band) cell to its natural chain-end via the JWT chain.

    Reuses the wholesale `_build_cage` + `_ingest_window` per page (item-id dedup, cached
    seller attribution, geo-resolve, bulk batch ingest), exactly like the wholesale
    `_drain_query` flat loop — only the seed params now carry seller_type + price band. The
    GLOBAL `state` (bounded seen_ids + seller LRU) dedups across cells. Returns
    (target_reached, fetch_error, last_http)."""
    params = _cell_params(cell["seller_type"], cell["lo"], cell["hi"])
    next_jwt: str | None = None
    for _page in range(max_pages):
        q = {"next_page": next_jwt} if next_jwt else params
        try:
            data = await fetcher.fetch_async(governed_fetch, SEARCH_ENDPOINT, params=q)
        except Exception as e:  # noqa: BLE001 — a fetch failure stops THIS cell, records the breaker signal.
            return False, str(e), fetcher.last_status
        stats["pages_fetched"] += 1
        section = (data.get("data") or {}).get("section") or {}
        items = section.get("items") or []
        if not items:
            break  # clean chain-end for this cell.
        # GRACEFUL DEGRADATION: a late per-window failure degrades (log + skip the page, keep
        # the chain alive) — never sinks the whole drain (mirrors the wholesale loop).
        try:
            cage = await _build_cage(items, fetcher, governed_fetch, geo, geocoder, state, stats)
            await _ingest_window(conn, platform_ulid, cage, stats)
        except Exception as e:  # noqa: BLE001 — contain a late window failure, keep draining.
            stats["window_errors"] = stats.get("window_errors", 0) + 1
            print(f"[wallapop_facet] window error (cell {cell['seller_type']} "
                  f"{cell['lo']}-{cell['hi']} page {_page}, degraded+continue): "
                  f"{type(e).__name__}: {e}", flush=True)
            next_jwt = (data.get("meta") or {}).get("next_page")
            if not next_jwt:
                break
            continue
        if state.cageable_count >= target:
            return True, None, None
        next_jwt = (data.get("meta") or {}).get("next_page")
        if not next_jwt:
            break  # clean chain-end.
    return False, None, None


async def harvest(seller_types: tuple[str, ...] = SELLER_TYPES,
                  concurrency: int = DEFAULT_CONCURRENCY,
                  cell_max: int = DEFAULT_CELL_MAX,
                  target: int = DEFAULT_TARGET,
                  max_pages: int = MAX_PAGES_PER_CELL) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    fetcher = WallapopFetcher(pool_size=concurrency)
    stats = {
        "pages_fetched": 0, "items_seen": 0, "pro_items": 0, "private_items": 0,
        "geo_skipped": 0, "dup_ids_collapsed": 0, "seller_lookups": 0,
        "seller_lookup_errors": 0, "new_dealers": 0, "cars_caged": 0, "new_cars": 0,
        "edges_created": 0, "new_events": 0, "dealers_distinct": 0, "window_errors": 0,
        "declared_full": 651000, "concurrency": concurrency, "target": target,
        "cell_max": cell_max, "probes": 0, "cells_capped": 0, "partitions": 0,
        "partitions_clean": 0, "partitions_errored": 0, "coverage_sum": 0,
        "baseline_declared": None,
    }
    state = _RunState()

    # S-HEALTH gate: if wallapop's breaker is OPEN (a recent ban/throttle still cooling),
    # skip the drain gracefully — the API keeps serving the last snapshot ("no se cae").
    if await is_open(conn, WP_SOURCE_KEY):
        print(f"[wallapop_facet] breaker OPEN for {WP_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, API still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": WP_SOURCE_KEY}

    # GOVERNOR: the single per-host choke point. EVERY GET (probe + search + users/{id})
    # passes through api.wallapop.com's token bucket (JSON_API class: 12 req/s steady, burst
    # 24), off the event loop. The host is never hammered: the bucket is the limiter.
    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_get)

    fetch_error: str | None = None
    last_http: int | None = None
    t0 = time.monotonic()
    try:
        geo = await GeoResolver.load(conn)
        geocoder = await ProvinceGeocoder.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = wallapop_platform_cdp_code()
        print(f"[wallapop_facet] platform entity ready: {platform_code} (ulid={platform_ulid})")
        print(f"[wallapop_facet] governor paces host {host_of(SEARCH_ENDPOINT)} "
              f"(JSON_API token bucket); geocoder has {geocoder.size()} labeled points.")

        # ---- PLAN: read the baseline oracle, then probe + recursively bisect every cell.
        stats["baseline_declared"] = await _baseline_declared(fetcher, governed_fetch)
        print(f"[wallapop_facet] baseline national declared (remaining_documents) = "
              f"{stats['baseline_declared']} (clamp-free oracle; honesty floor, not a quorum path)")
        print(f"[wallapop_facet] planning FACET partitions: seller_types={list(seller_types)} "
              f"x price bands, cell_max={cell_max} (recursively bisected by the live oracle)...")
        partitions, coverage_sum = await plan_partitions(
            fetcher, governed_fetch, seller_types, cell_max, stats)
        stats["partitions"] = len(partitions)
        stats["coverage_sum"] = coverage_sum
        capped = [c for c in partitions if c.get("capped")]
        print(f"[wallapop_facet] PLAN: {len(partitions)} leaf cells "
              f"({stats['probes']} oracle probes, {len(capped)} price-spike cells kept whole); "
              f"sum(cell declared)={coverage_sum} vs baseline={stats['baseline_declared']}")

        owners_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        cars_before = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)
        stats["wallapop_cars_before"] = cars_before

        # ---- DRAIN: every leaf cell through the shared cage+batch machinery, GLOBAL dedup.
        target_reached = False
        for i, cell in enumerate(partitions, 1):
            if target_reached:
                break
            reached, cerr, chttp = await _drain_cell(
                fetcher, governed_fetch, conn, platform_ulid, geo, geocoder, state, stats,
                cell, target, max_pages)
            if cerr is not None:
                stats["partitions_errored"] += 1
                fetch_error, last_http = cerr, chttp
                print(f"[wallapop_facet] cell {cell['seller_type']} {cell['lo']}-{cell['hi']} "
                      f"failed ({cerr}); recording + stopping drain honestly.")
                target_reached = True
            else:
                stats["partitions_clean"] += 1
                if reached:
                    target_reached = True
            elapsed = time.monotonic() - t0
            cpm = stats["cars_caged"] / (elapsed / 60) if elapsed > 0 else 0.0
            band = f"{cell['lo']}-{cell['hi']}"
            print(f"[wallapop_facet] [{i}/{len(partitions)}] {cell['seller_type'][:4]:>4} "
                  f"{band:<14} declared={cell['declared']:6d} -> caged_total={stats['cars_caged']} "
                  f"new={stats['new_cars']} edges_run={stats['edges_created']} "
                  f"distinct_ids={state.distinct_ids} | {cpm:.0f} cars/min "
                  f"{'STOP' if cerr else 'CLEAN'}", flush=True)

        elapsed = time.monotonic() - t0
        stats["elapsed_s"] = elapsed
        stats["cars_per_min"] = stats["cars_caged"] / (elapsed / 60) if elapsed > 0 else 0.0

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

        # LEGACY CLEANUP (PG DELETE+INSERT doctrine): retire obsolete per-province 'garaje'
        # buckets now that privates are caged per-seller. Re-point is VAM-verified inside; only
        # superseded bucket cars are removed — total wallapop cars never drop. Idempotent.
        await cleanup_legacy_buckets(conn, platform_ulid, stats)

        # Persist the recipe annotated with the FACET enumeration (the base recipe is unchanged
        # except the enumeration string records the seller_type × price-band partition).
        run_recipe = {**WP_PLATFORM_RECIPE,
                      "enumeration": ("FACET partition (depth-cap fix): seller_type "
                                      "{professional,private} x price band (min_sale_price/"
                                      "max_sale_price), each cell sized <= cell_max via the live "
                                      "pointers.ORGANIC.remaining_documents oracle and drained by "
                                      "the meta.next_page JWT chain to its natural end; geo lat/"
                                      "long is NOT a partition axis (every centroid returns the "
                                      "national pool). Global item-id dedup collapses cross-cell "
                                      "overlap. Supersedes the flat order_by=newest cursor that "
                                      "depth-capped (~347k) short of the ~651k catalog."),
                      "facet_axes": {"seller_type": list(SELLER_TYPES),
                                     "price": "min_sale_price/max_sale_price (EUR)",
                                     "count_oracle": "next_page JWT pointers.ORGANIC.remaining_documents"}}
        recipe_path = write_recipe(platform_code, run_recipe)
        print(f"[wallapop_facet] recipe written: {recipe_path}")

        # ---- VAM count quorum — THREE orthogonal DB paths, each measuring "distinct cageable
        # cars served for wallapop", derived independently (edge-count / join-reachability /
        # native-id count). The declared baseline + coverage_sum are honesty, not quorum paths.
        db_edges = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)
        db_join_vehicles = await conn.fetchval(
            """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               JOIN entity d ON d.entity_ulid = v.entity_ulid
               WHERE pl.platform_entity_ulid=$1""", platform_ulid)
        db_distinct_refs = await conn.fetchval(
            "SELECT count(DISTINCT listing_ref) FROM platform_listing WHERE platform_entity_ulid=$1",
            platform_ulid)
        verdict = await record_count_verdict(
            conn, subject_type="platform_slice", subject_key=platform_code,
            claim="platform_listing edges == join-reachable vehicles == distinct native listing_refs",
            paths={"db_edges": db_edges, "db_join_vehicles": db_join_vehicles,
                   "db_distinct_refs": db_distinct_refs},
            tolerance=0.0)
        stats["verdict"] = verdict
        stats["db_edges"] = db_edges
        stats["db_join_vehicles"] = db_join_vehicles
        stats["db_distinct_refs"] = db_distinct_refs
        stats["cageable_pulls"] = state.cageable_count
        stats["harvested_distinct_ids"] = state.distinct_ids
        stats["distinct_sellers_resident"] = len(state.seller_cache)
        stats["platform_code"] = platform_code
        stats["platform_ulid"] = platform_ulid
        stats["recipe_path"] = str(recipe_path)

        # NO-DROP GUARD: total wallapop distinct listings (= edges, post-cleanup) MUST be >= the
        # pre-run count. The cleanup only removed bucket cars with a live per-seller twin, so the
        # distinct-listing total can only GROW (new facet harvest) — never shrink.
        stats["wallapop_cars_after"] = db_edges
        stats["cars_did_not_drop"] = db_edges >= stats.get("wallapop_cars_before", 0)
        if not stats["cars_did_not_drop"]:
            verdict = "REFUTED"
            stats["verdict"] = verdict
            print(f"[wallapop_facet] FATAL no-drop guard: cars dropped "
                  f"{stats.get('wallapop_cars_before')} -> {db_edges}.")

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks wallapop, trips
        # the breaker on a ban, auto-repairs. OK when >=1 page fetched, no fetch error stopped a
        # cell, and the VAM did not refute.
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
        print(f"\n[wallapop_facet] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("WALLAPOP FACET-PARTITION HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  declared full (oracle): ~{stats.get('baseline_declared')} (national remaining_documents)")
    print("  --- coverage (seller_type x price-band facet partition) ---")
    print(f"  leaf cells            : {stats.get('partitions')} "
          f"({stats.get('partitions_clean')} clean / {stats.get('partitions_errored')} errored)")
    print(f"  oracle probes         : {stats.get('probes')} "
          f"(price-spike cells kept whole: {stats.get('cells_capped')})")
    print(f"  cell_max (split bar)  : {stats.get('cell_max')}")
    print(f"  sum(cell declared)    : {stats.get('coverage_sum')}")
    print("  --- drain ---")
    print(f"  concurrency (window)  : {stats.get('concurrency')} in-flight GETs")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  distinct listing ids  : {stats.get('harvested_distinct_ids')}")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-cell + cross-page)")
    print(f"  resident sellers (LRU): {stats.get('distinct_sellers_resident')} "
          f"({stats['seller_lookups']} lookups, {stats['seller_lookup_errors']} errors)")
    print(f"  PRO items / private   : {stats['pro_items']} / {stats['private_items']}")
    print(f"  geo/attr skipped      : {stats['geo_skipped']}")
    print(f"  PRO dealers attributed: {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  particulars attributed: {stats.get('particulars_distinct')} distinct (per-seller)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for wallapop = {stats.get('db_edges')})")
    print(f"  NEW delta events      : {stats['new_events']}")
    print(f"  cars/min              : {stats.get('cars_per_min', 0):.0f} "
          f"(elapsed {stats.get('elapsed_s', 0):.0f}s)")
    print("  --- legacy garaje bucket cleanup (PG DELETE+INSERT) ---")
    print(f"  buckets before/after  : {stats.get('bucket_entities_before')} -> {stats.get('bucket_entities_after')}"
          f" ({stats.get('bucket_entities_deleted')} removed)")
    print(f"  wallapop cars before  : {stats.get('wallapop_cars_before')}")
    print(f"  wallapop cars after   : {stats.get('wallapop_cars_after')} "
          f"(no-drop guard: {'OK' if stats.get('cars_did_not_drop') else 'FAILED'})")
    print("  --- VAM count quorum (3 orthogonal DB paths, this platform) ---")
    print(f"  db_edges              : {stats.get('db_edges')}")
    print(f"  db_join_vehicles      : {stats.get('db_join_vehicles')}")
    print(f"  db_distinct_refs      : {stats.get('db_distinct_refs')}")
    print(f"  VAM verdict           : {stats.get('verdict')}")
    print(f"  health status         : {stats.get('health_status')} / breaker {stats.get('breaker_state')}")
    print(f"  recipe                : {stats.get('recipe_path')}")
    print("=" * 64)


def _parse_seller_types(arg: str | None) -> tuple[str, ...]:
    if not arg:
        return SELLER_TYPES
    out: list[str] = []
    for tok in arg.split(","):
        tok = tok.strip().lower()
        if tok in SELLER_TYPES and tok not in out:
            out.append(tok)
    return tuple(out) or SELLER_TYPES


def main() -> None:
    parser = argparse.ArgumentParser(
        description="wallapop FACET-partition harvester (seller_type x price-band, oracle-planned)")
    parser.add_argument("--seller-types", type=str, default=None,
                        help="comma list of seller_type cells to drain (professional,private); default both")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"in-flight GETs per cell window; default {DEFAULT_CONCURRENCY}. The "
                              f"governor's JSON_API per-host bucket is the real limiter."))
    parser.add_argument("--cell-max", type=int, default=DEFAULT_CELL_MAX,
                        help=(f"recursively price-bisect any cell whose remaining_documents exceeds "
                              f"this; default {DEFAULT_CELL_MAX} (well inside the verified cursor depth)."))
    parser.add_argument("--target", type=int, default=DEFAULT_TARGET,
                        help=(f"distinct cars to cage this run before stopping; default {DEFAULT_TARGET} "
                              f"(the whole catalog; a cell ends naturally first)."))
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES_PER_CELL,
                        help=f"hard page ceiling per cell (guardrail); default {MAX_PAGES_PER_CELL}")
    args = parser.parse_args()
    seller_types = _parse_seller_types(args.seller_types)
    stats = asyncio.run(harvest(seller_types, args.concurrency, args.cell_max,
                                args.target, args.max_pages))
    _print_report(stats)


if __name__ == "__main__":
    main()
