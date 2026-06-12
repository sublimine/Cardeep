"""coches.net FACET-PARTITION harvester — breaks the relevance-pagination cap.

THE PROBLEM. coches.net's `POST web.gw.coches.net/search` is an open JSON gateway
that declares ~272k cars (meta.totalResults), but a SINGLE undivided query sorted by
`relevance` does NOT let you page all the way down: relevance is non-deterministic
across pages (the same ad reshuffles), so a flat drain silently re-serves a bounded
top slice and caps far below the declared total. The wholesale module
(pipeline.platform.coches_net_wholesale) hit exactly that ceiling (~155k edges).

THE FIX (verified live 2026-06-12 against the gateway, NOT assumed):
  1) SORT by price, not relevance. A price-ordered sequence is STABLE — paging is
     deterministic, so a partition drains to its exact last page (verified: prov 28
     page 564 returns 34 items, page 565 returns 0 — a clean, exhaustive boundary).
  2) PARTITION by province. The 52 Spanish province ids each carry a totalResults
     well under any safe drain depth. Summed across all 52 they cover the national
     set (sum=278,818 vs national 272,639 — a 2.3% cross-province overlap that
     dedup-by-listing-id collapses for free via the cage's ON CONFLICT).
  3) SUB-PARTITION the dense provinces by price band. Three provinces exceed the
     15,000 split threshold — 8 (Barcelona 26,500), 28 (Madrid 56,334),
     46 (Valencia 16,611) — so each is split into 7 price bands, every band under
     the cap. (Bands verified live; the densest band, prov 28 15k-25k = 15,768, still
     drains cleanly at ~158 pages, far inside the proven 564-page depth.)

THE FACET PAYLOAD (the SHAPE the gateway honors — verified live, distinct from the
flat relevance shape the wholesale module sends):
    {"pagination":{"page":N,"size":100},
     "sort":{"term":"price","order":"ASC"},
     "filters":{"categoryId":2500,"provinceIds":[P],"price":{"from":F,"to":T}}}
The `provinceIds` filter genuinely applies (prov 99 -> 0 results; prov 8 -> only
province-8 items) and `price{from,to}` genuinely narrows (band sums ~= province
total). categoryId 2500 = turismos (cars).

ARCHITECTURE REUSE. This module does NOT fork the harvest engine. It imports the
wholesale module's proven cage/parse/DB layer wholesale — the concurrent fetch
window, the unnest BATCH ingest (the same ~6 set-based statements per window), the
per-host governor (web.gw.coches.net in the JSON_API 12 req/s class), S-HEALTH
breaker, VAM count quorum, and the dual-membership platform_listing model. The ONLY
additions here are: (a) a facet payload builder, (b) the partition plan, and (c) a
partition loop that drains each partition through that same machinery with a GLOBAL
seen_ids set so cross-partition overlap is collapsed exactly once. Delta / VAM /
idempotency are preserved byte-for-byte (same ON CONFLICT, same NEW-event rule).

Run: python -m pipeline.platform.coches_net_facet
     python -m pipeline.platform.coches_net_facet --provinces 28,8,46 --concurrency 15
"""
from __future__ import annotations

import argparse
import asyncio
import json
import time

import asyncpg
from curl_cffi import requests as cffi_requests

from pipeline.engine.governor import governor, host_of
from pipeline.geo import GeoResolver
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict

# Reuse the wholesale module's proven machinery — parse, cage, bulk-ingest, identity.
from pipeline.platform.coches_net_wholesale import (
    CATEGORY_CARS,
    COCHES_PLATFORM_RECIPE,
    COCHES_SOURCE_KEY,
    COCHES_TRADE_NAME,
    DSN,
    ENDPOINT,
    PAGE_SIZE,
    _HEADERS,
    _IMPERSONATE,
    _TIMEOUT,
    _ingest_window,
    _to_int,
    coches_platform_cdp_code,
    ensure_platform_entity,
)

# ---------------------------------------------------------------------------
# Partition plan (verified live 2026-06-12 — see module docstring).
# ---------------------------------------------------------------------------

# A province whose totalResults exceeds this gets price-band sub-partitioned. 15,000 is
# conservative: a partition of 15k drains in 150 pages, an order of magnitude inside the
# 564-page depth proven to drain cleanly. Provinces under it drain whole in one sweep.
SPLIT_THRESHOLD = 15_000

# The 7 price bands for dense provinces. (None = open end.) Verified to honor price{from,to}
# and to keep every resulting sub-partition under the cap (densest = prov 28 15k-25k ~15.8k).
PRICE_BANDS: tuple[tuple[int | None, int | None], ...] = (
    (None, 3000),
    (3000, 6000),
    (6000, 10000),
    (10000, 15000),
    (15000, 25000),
    (25000, 50000),
    (50000, None),
)

SPANISH_PROVINCES = tuple(range(1, 53))  # INE province ids 1..52.

# A hard page ceiling per partition — a guardrail, never expected to bite (a real
# partition ends naturally on an empty page well before this). Sized for the densest
# single-province sweep (prov 28 ~564 pages) plus headroom.
MAX_PAGES_PER_PARTITION = 800


# ---------------------------------------------------------------------------
# Facet fetcher — same pooled, governed, thread-safe POST as the wholesale fetcher,
# but with the FACET payload (province + price band) instead of the flat relevance one.
# ---------------------------------------------------------------------------


class FacetFetcher:
    """Pool of fingerprint-coherent curl_cffi POST sessions, one per concurrency slot.

    Identical concurrency/coherence contract to CochesFetcher (one Session per slot, leased
    by index so no two coroutines ever share a session under the governor's to_thread fetch).
    The only difference is the payload: this posts the FACET shape (sort=price, nested
    filters with provinceIds + price band) that the gateway paginates deterministically."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    @staticmethod
    def _payload(page: int, size: int, *, province: int,
                 price_from: int | None, price_to: int | None) -> dict:
        # The FACET shape the gateway honors (verified live): nested sort + filters.
        # provinceIds narrows to one province; price{from,to} narrows the band (open
        # ends are null). sort.term=price gives the STABLE, fully-drainable order.
        return {
            "pagination": {"page": page, "size": size},
            "sort": {"term": "price", "order": "ASC"},
            "filters": {
                "categoryId": CATEGORY_CARS,
                "provinceIds": [province],
                "price": {"from": price_from, "to": price_to},
            },
        }

    def fetch_page(self, url: str, *, page: int = 1, size: int = PAGE_SIZE,
                   province: int, price_from: int | None = None,
                   price_to: int | None = None, slot: int = 0) -> dict:
        """Synchronous facet POST on pool session `slot` (runs in a governor worker thread).

        Same contract as CochesFetcher.fetch_page — leased slot = never-shared session,
        raise on non-200 so the breaker sees throttling, explicit UTF-8 decode so accented
        names survive. The partition coordinates (province/band) ride as kwargs the governor
        forwards untouched."""
        session = self._sessions[slot]
        resp = session.post(
            url,
            json=self._payload(page, size, province=province,
                               price_from=price_from, price_to=price_to),
            headers=_HEADERS, impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url} "
                               f"(prov {province}, band {price_from}-{price_to}, page {page})")
        return json.loads(resp.content.decode("utf-8"))

    async def fetch_page_async(self, governed_fetch, url: str, *, page: int,
                               province: int, price_from: int | None = None,
                               price_to: int | None = None, size: int = PAGE_SIZE) -> dict:
        """Lease a pool slot, fetch THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_fetch(
                url, page=page, size=size, province=province,
                price_from=price_from, price_to=price_to, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# Partition planning — read each province's totalResults from meta, split the dense
# ones by price band. This is the COVERAGE-PROOF spine: every partition's declared
# totalResults is summed and compared to the national declared total.
# ---------------------------------------------------------------------------


def _meta_total(fetcher: FacetFetcher, *, province: int,
                price_from: int | None, price_to: int | None) -> int:
    """A cheap size=1 facet probe returning meta.totalResults for one partition.

    Runs OUTSIDE the governor (a single tiny request per partition during planning, well
    under the human-cadence floor) so planning is fast; the heavy drain stays governed."""
    data = fetcher.fetch_page(ENDPOINT, page=1, size=1, province=province,
                              price_from=price_from, price_to=price_to)
    return _to_int((data.get("meta") or {}).get("totalResults")) or 0


def plan_partitions(fetcher: FacetFetcher, provinces: tuple[int, ...]) -> tuple[list[dict], int]:
    """Build the partition list and the summed declared coverage.

    For each province: probe its total. If <= SPLIT_THRESHOLD, it is one partition. If it
    exceeds it, split into the 7 price bands (each probed for its own declared total). The
    returned coverage_sum is the independent capture-recapture path: sum of every
    partition's meta.totalResults, to be compared against the national declared total."""
    partitions: list[dict] = []
    coverage_sum = 0
    for prov in provinces:
        total = _meta_total(fetcher, province=prov, price_from=None, price_to=None)
        time.sleep(0.08)  # human-cadence floor between planning probes.
        if total <= SPLIT_THRESHOLD:
            partitions.append({"province": prov, "price_from": None, "price_to": None,
                               "declared": total})
            coverage_sum += total
            continue
        # Dense province -> price-band sub-partitions. Sum the BANDS' declared totals (the
        # real fetched coverage), not the province aggregate, so coverage_sum matches what
        # the drain will actually traverse.
        for frm, to in PRICE_BANDS:
            bt = _meta_total(fetcher, province=prov, price_from=frm, price_to=to)
            time.sleep(0.06)
            partitions.append({"province": prov, "price_from": frm, "price_to": to,
                               "declared": bt})
            coverage_sum += bt
    return partitions, coverage_sum


def _national_total(fetcher: FacetFetcher) -> int:
    """The national declared total (no province filter) — the coverage-proof target."""
    payload = {"pagination": {"page": 1, "size": 1},
               "sort": {"term": "price", "order": "ASC"},
               "filters": {"categoryId": CATEGORY_CARS, "price": {"from": None, "to": None}}}
    session = fetcher._sessions[0]
    resp = session.post(ENDPOINT, json=payload, headers=_HEADERS,
                        impersonate=_IMPERSONATE, timeout=_TIMEOUT)
    data = json.loads(resp.content.decode("utf-8"))
    return _to_int((data.get("meta") or {}).get("totalResults")) or 0


# ---------------------------------------------------------------------------
# Drain one partition through the SAME concurrent-window + bulk-ingest machinery the
# wholesale module uses. The only changes: the facet fetcher and the partition coords.
# seen_ids / harvested_cageable / stats are GLOBAL across partitions so cross-partition
# overlap is collapsed once and the harvest truth is one coherent set.
# ---------------------------------------------------------------------------


async def _drain_partition(conn: asyncpg.Connection, geo: GeoResolver, platform_ulid: str,
                           fetcher: FacetFetcher, governed_fetch, partition: dict,
                           concurrency: int, seen_ids: set, harvested_cageable: set,
                           stats: dict) -> tuple[bool, str | None, int | None]:
    """Drain a single partition to exhaustion via the concurrent sliding window.

    Returns (clean_finish, fetch_error, last_http). clean_finish=True means the partition
    ended on an empty page (fully drained); False means a fetch error stopped it (the
    breaker signal). Each window fetches up to `concurrency` pages in parallel through the
    governor, then bulk-ingests them in page order in ONE transaction — byte-identical to
    the wholesale window ingest. A GLOBAL seen_ids dedups across BOTH pages and partitions."""
    prov = partition["province"]
    frm, to = partition["price_from"], partition["price_to"]
    stop = False
    fetch_error: str | None = None
    last_http: int | None = None
    next_page = 1
    while next_page <= MAX_PAGES_PER_PARTITION and not stop:
        window = list(range(next_page,
                            min(next_page + concurrency, MAX_PAGES_PER_PARTITION + 1)))
        next_page = window[-1] + 1

        results = await asyncio.gather(
            *(fetcher.fetch_page_async(governed_fetch, ENDPOINT, page=p, province=prov,
                                       price_from=frm, price_to=to, size=PAGE_SIZE)
              for p in window),
            return_exceptions=True,
        )

        window_pages: list[tuple[int, list]] = []
        for page, data in zip(window, results):
            if isinstance(data, Exception):
                fetch_error = str(data)
                last_http = fetcher.last_status
                print(f"[coches_net_facet] prov {prov} band {frm}-{to} page {page} "
                      f"fetch failed ({data}); stopping this partition honestly.")
                stop = True
                break
            items = data.get("items") or []
            if not items:
                stop = True  # clean end of this partition.
                break
            window_pages.append((page, items))

        if window_pages:
            await _ingest_window(conn, geo, platform_ulid, window_pages, seen_ids,
                                 harvested_cageable, stats)
            stats["pages_fetched"] += len(window_pages)

    clean_finish = fetch_error is None
    return clean_finish, fetch_error, last_http


# ---------------------------------------------------------------------------
# Orchestration — plan, then drain every partition through the shared machinery,
# then the SAME VAM count quorum + S-HEALTH heartbeat the wholesale module runs.
# ---------------------------------------------------------------------------

DEFAULT_CONCURRENCY = 15


async def harvest_facet(provinces: tuple[int, ...] = SPANISH_PROVINCES,
                        concurrency: int = DEFAULT_CONCURRENCY) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    fetcher = FacetFetcher(pool_size=concurrency)
    stats = {
        "pages_fetched": 0, "items_seen": 0, "dealer_items": 0,
        "private_skipped": 0, "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "price_drops_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "dealers_distinct": 0,
        "concurrency": concurrency, "partitions": 0, "partitions_clean": 0,
        "partitions_errored": 0, "coverage_sum": 0, "national_total": None,
    }
    # GLOBAL harvest truth — distinct across ALL partitions (cross-partition overlap from
    # province/price edge-membership collapses here exactly once).
    seen_ids: set[str] = set()
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if the breaker is OPEN (recent ban cooling), skip gracefully.
    if await is_open(conn, COCHES_SOURCE_KEY):
        print(f"[coches_net_facet] breaker OPEN for {COCHES_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, API still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": COCHES_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None
    t0 = time.monotonic()
    try:
        geo = await GeoResolver.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = coches_platform_cdp_code()
        print(f"[coches_net_facet] platform entity ready: {platform_code} (ulid={platform_ulid})")
        print(f"[coches_net_facet] governor paces host {host_of(ENDPOINT)} (JSON_API bucket).")

        # ---- PLAN: probe every province's total; split the dense ones by price band.
        print(f"[coches_net_facet] planning partitions over {len(provinces)} provinces "
              f"(split threshold {SPLIT_THRESHOLD})...")
        national = _national_total(fetcher)
        stats["national_total"] = national
        stats["declared_full"] = national
        partitions, coverage_sum = plan_partitions(fetcher, provinces)
        stats["partitions"] = len(partitions)
        stats["coverage_sum"] = coverage_sum
        split_provs = sorted({p["province"] for p in partitions
                              if p["price_from"] is not None or p["price_to"] is not None})
        print(f"[coches_net_facet] PLAN: {len(partitions)} partitions; "
              f"price-split provinces = {split_provs}")
        print(f"[coches_net_facet] COVERAGE PROOF: sum(partition declared)={coverage_sum} "
              f"vs national declared={national} "
              f"(overlap {coverage_sum - national:+d}, {100*(coverage_sum-national)/max(national,1):+.1f}%)")

        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        # ---- DRAIN: every partition through the shared concurrent+batch machinery.
        for i, partition in enumerate(partitions, 1):
            prov = partition["province"]
            frm, to = partition["price_from"], partition["price_to"]
            band_label = "all" if frm is None and to is None else f"{frm}-{to}"
            clean, perr, phttp = await _drain_partition(
                conn, geo, platform_ulid, fetcher, governed_fetch, partition,
                concurrency, seen_ids, harvested_cageable, stats)
            if clean:
                stats["partitions_clean"] += 1
            else:
                stats["partitions_errored"] += 1
                fetch_error = perr or fetch_error
                last_http = phttp if phttp is not None else last_http
            elapsed = time.monotonic() - t0
            cpm = stats["cars_caged"] / (elapsed / 60) if elapsed > 0 else 0.0
            print(f"[coches_net_facet] [{i}/{len(partitions)}] prov {prov:2d} band {band_label:<11} "
                  f"declared={partition['declared']:6d} -> caged_total={stats['cars_caged']} "
                  f"new={stats['new_cars']} edges={stats['edges_created']} "
                  f"distinct_ids={len(seen_ids)} | {cpm:.0f} cars/min "
                  f"{'CLEAN' if clean else 'ERROR'}")

        elapsed = time.monotonic() - t0
        stats["elapsed_s"] = elapsed
        stats["cars_per_min"] = stats["cars_caged"] / (elapsed / 60) if elapsed > 0 else 0.0

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe = dict(COCHES_PLATFORM_RECIPE)
        recipe["scope"] = ("platform-facet (web.gw.coches.net/search; province + price-band "
                           "partitions, sort=price for deterministic full drain)")
        recipe["enumeration"] = (f"FACET partitions: provinceIds 1..52 (sort=price ASC); "
                                 f"provinces >{SPLIT_THRESHOLD} split into 7 price bands; "
                                 f"each partition drained to empty page")
        recipe_path = write_recipe(platform_code, recipe)
        print(f"[coches_net_facet] recipe written: {recipe_path}")

        # ---- VAM count quorum — same three orthogonal like-with-like paths as wholesale.
        db_edges = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)
        db_join_vehicles = await conn.fetchval(
            """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               JOIN entity d ON d.entity_ulid = v.entity_ulid
               WHERE pl.platform_entity_ulid=$1""", platform_ulid)
        harvested_cageable_n = len(harvested_cageable)
        verdict = await record_count_verdict(
            conn, subject_type="platform_facet", subject_key=platform_code,
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

        # ---- S-HEALTH heartbeat. OK when pages fetched, no fetch error stopped a partition,
        # VAM did not refute. A partial-but-clean run (some partition errored) records the error.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, COCHES_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, COCHES_SOURCE_KEY, run_error or "facet harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[coches_net_facet] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("COCHES.NET FACET-PARTITION HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  national declared     : {stats.get('national_total')}")
    print("  --- coverage proof (capture-recapture) ---")
    print(f"  partitions            : {stats.get('partitions')} "
          f"({stats.get('partitions_clean')} clean / {stats.get('partitions_errored')} errored)")
    print(f"  sum(partition declared): {stats.get('coverage_sum')}")
    print(f"  national declared      : {stats.get('national_total')}")
    nat = stats.get('national_total') or 1
    cov = stats.get('coverage_sum') or 0
    print(f"  overlap               : {cov - nat:+d} ({100*(cov-nat)/nat:+.1f}%)")
    print("  --- drain ---")
    print(f"  concurrency (window)  : {stats.get('concurrency')} pages in flight")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  distinct listing ids  : {stats.get('harvested_distinct_ids')}")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page + cross-partition)")
    print(f"  dealer items          : {stats['dealer_items']}")
    print(f"  private skipped       : {stats['private_skipped']}")
    print(f"  geo skipped (bad prov): {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for coches.net = {stats.get('db_edges')})")
    print(f"  price drops captured  : {stats['price_drops_captured']}")
    print(f"  NEW delta events      : {stats['new_events']}")
    print(f"  cars/min              : {stats.get('cars_per_min', 0):.0f} "
          f"(elapsed {stats.get('elapsed_s', 0):.0f}s)")
    print("  --- VAM count quorum (like-with-like) ---")
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="coches.net FACET-PARTITION harvester (breaks the relevance cap toward 100%)")
    parser.add_argument("--provinces", type=str, default=None,
                        help="comma-separated INE province ids (1..52); default = all 52")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"pages fetched in parallel per sliding window; default "
                              f"{DEFAULT_CONCURRENCY}. The governor's per-host bucket is the "
                              f"real limiter — this only needs to keep the bucket saturated."))
    args = parser.parse_args()
    provinces = _parse_provinces(args.provinces)
    stats = asyncio.run(harvest_facet(provinces, args.concurrency))
    _print_report(stats)


if __name__ == "__main__":
    main()
