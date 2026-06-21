"""AS24 (AutoScout24-ES) FACET-PARTITION harvester — breaks the /lst 200-page (~4k) cap.

The flat /lst search (autoscout24_wholesale) exposes only ~200 pages / ~4,000 cars, far below the
declared ~278k. AS24 /lst, however, honors `pricefrom`/`priceto` + `sort=price` (verified live:
band 0-2000=498, 2000-4000=2215, 4000-6000=4018). So the catalog is drained by PARTITIONING into
price bands, each under the cap, paged with a STABLE price sort (deterministic — a band drains to its
exact last page). Same idea as coches_net_facet (province + price bands); here price bands are the
clean axis (province on AS24 is a zip+radius, which doesn't map to administrative provinces).

REUSE: every per-listing primitive (parse, geo-resolve, cage, ingest, delta, VAM) is imported from
autoscout24_wholesale — this module only adds (a) the band planner + faceted URL (block 1), and
(b) the band loop with a GLOBAL seen_listing_ids so cross-band overlap collapses exactly once (block 2).

Run:  python -m pipeline.platform.as24_facet [max_bands] [bands]
      python -m pipeline.platform.as24_facet 2 "0:2000,2000:4000"   # explicit cheap bands (bounded test)
"""
from __future__ import annotations

import asyncio
import sys
import time
from collections.abc import Callable

import asyncpg
from curl_cffi import requests as cffi_requests

from pipeline.engine.fetch import FetchEngine
from pipeline.engine.governor import governor, host_of
from pipeline.geo import GeoResolver
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.verify import record_count_verdict
from pipeline.platform.autoscout24_wholesale import (
    AS24_SOURCE_KEY,
    DSN,
    PAGE_SIZE,
    _BASE,
    _find,
    _find_listings,
    _next_data,
    as24_platform_cdp_code,
    emit_new_event,
    ensure_platform_entity,
    link_platform,
    parse_listing_dealer,
    parse_listing_vehicle,
    upsert_dealer,
    upsert_vehicle,
)

# A single /lst search caps at ~200 pages * PAGE_SIZE. Keep a band comfortably under that so its
# last page is reachable; bands at/over this are subdivided.
FACET_CAP = 200 * PAGE_SIZE  # 4000
MAX_PAGES_PER_BAND = 200     # the hard /lst pagination ceiling per search
AS24_FACET_SOURCE_KEY = "as24_facet"  # own health row (does not clobber the flat as24_wholesale health)

# Price domain to cover (EUR). Almost all listings fall well under 10M; the open top band catches any
# tail above PRICE_MAX. Bisection floor: never split a band narrower than this (avoids infinite
# recursion on a price point with > CAP identical-priced listings — accepted as a rare, declared gap).
PRICE_MAX = 1_000_000
_MIN_BAND_WIDTH = 100


def _facet_url(page: int, price_from: int, price_to: int | None) -> str:
    """A price-banded /lst URL with a STABLE price sort. price_to=None -> open-ended top band
    (priceto empty) so the tail above the last bound is still caught."""
    to = "" if price_to is None else str(price_to)
    return (f"{_BASE}/lst?atype=C&cy=E&sort=price&desc=0&size={PAGE_SIZE}&page={page}"
            f"&pricefrom={price_from}&priceto={to}")


def plan_price_bands(
    count_of: Callable[[int, int], int],
    lo: int = 0,
    hi: int = PRICE_MAX,
    min_width: int = _MIN_BAND_WIDTH,
) -> list[tuple[int, int]]:
    """Adaptive partition of [lo, hi) into contiguous price bands each with <= FACET_CAP listings.

    count_of(price_from, price_to) -> AutoScout24 numberOfResults for that band. If a band is already
    under the cap (or hit the min-width floor), keep it whole; otherwise bisect by price and recurse.
    Result is gap-free and contiguous: bands[i].to == bands[i+1].from, covering exactly [lo, hi).
    """
    total = count_of(lo, hi)
    if total <= FACET_CAP or (hi - lo) <= min_width:
        return [(lo, hi)]
    mid = (lo + hi) // 2
    return (plan_price_bands(count_of, lo, mid, min_width)
            + plan_price_bands(count_of, mid, hi, min_width))


def expand_bands(
    bands: list[tuple[int, int | None]],
    count_of: Callable[[int, int], int],
    min_width: int = _MIN_BAND_WIDTH,
) -> list[tuple[int, int | None]]:
    """Expand explicit (possibly too-wide) bands so EVERY closed band is <= FACET_CAP.

    Root-cause fix: passing a wide band (e.g. 18000-19000 = 12,866 cars) to a flat /lst search
    truncates silently at the 200-page cap. Routing each closed band through the adaptive planner
    subdivides the dense ones until they fit, so the catalog is drained completely — never truncated.
    A band already under the cap passes through unchanged. Open-top bands (price_to=None) are kept
    verbatim: an open interval can't be bisected; its tail above the last bound is sparse.
    """
    out: list[tuple[int, int | None]] = []
    for pf, pt in bands:
        if pt is None:
            out.append((pf, pt))
        else:
            out.extend(plan_price_bands(count_of, pf, pt, min_width))
    return out


def _count_sync(price_from: int, price_to: int) -> int:
    """numberOfResults for a band, via a direct (sync) fetch — used ONLY to build the plan (a handful
    of probes, once, off the hot loop). Gentle fixed pacing. On any error, assume dense (=FACET_CAP+1)
    so the planner subdivides rather than under-covering."""
    try:
        r = cffi_requests.get(_facet_url(1, price_from, price_to), impersonate="chrome131", timeout=30)
        time.sleep(0.4)
        if r.status_code != 200:
            return FACET_CAP + 1
        n = _find(_next_data(r.text), "numberOfResults")
        return int(n) if n is not None else FACET_CAP + 1
    except Exception:
        return FACET_CAP + 1


def _parse_bands(spec: str) -> list[tuple[int, int | None]]:
    """Parse '0:2000,2000:4000,200000:' into [(0,2000),(2000,4000),(200000,None)]."""
    out: list[tuple[int, int | None]] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        f, _, t = part.partition(":")
        out.append((int(f), int(t) if t.strip() else None))
    return out


async def harvest_facet(max_bands: int | None = None,
                        bands: list[tuple[int, int | None]] | None = None,
                        skip_bands: int = 0) -> dict:
    """Drain AS24 by price bands, breaking the /lst cap. Reuses every wholesale primitive; the only
    new logic is the band loop + a GLOBAL seen_listing_ids (cross-band dedup). Idempotent ingest."""
    conn = await asyncpg.connect(DSN)
    engine = FetchEngine()
    stats: dict = {
        "pages_fetched": 0, "listings_seen": 0, "dealer_listings": 0, "private_skipped": 0,
        "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0, "new_cars": 0, "edges_created": 0,
        "new_events": 0, "dup_ids_collapsed": 0, "bands_planned": 0, "bands_drained": 0,
    }
    seen_listing_ids: set[str] = set()
    harvested_cageable: set[tuple[str, str]] = set()
    if await is_open(conn, AS24_FACET_SOURCE_KEY):
        print(f"[as24_facet] breaker OPEN for {AS24_FACET_SOURCE_KEY}; skipping (graceful).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": AS24_FACET_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(engine.fetch_text)
    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = as24_platform_cdp_code()
        print(f"[as24_facet] platform {platform_code} (ulid={platform_ulid}); governor paces {host_of(_BASE)}.")

        if bands is None:
            print("[as24_facet] planning adaptive price bands (sync probes)...")
            bands = await asyncio.to_thread(plan_price_bands, _count_sync)
        else:
            print(f"[as24_facet] expanding {len(bands)} explicit band(s) through adaptive planner "
                  "(dense bands subdivide so they never truncate at the page cap)...")
            bands = await asyncio.to_thread(expand_bands, bands, _count_sync)
        full_plan = len(bands)
        if skip_bands:
            bands = bands[skip_bands:]
        if max_bands is not None:
            bands = bands[:max_bands]
        stats["bands_planned"] = len(bands)
        stats["plan_total_bands"] = full_plan
        stats["plan_window"] = f"{skip_bands}:{skip_bands + len(bands)} of {full_plan}"
        print(f"[as24_facet] draining {len(bands)} band(s) [window {stats['plan_window']}] "
              f"(cap {FACET_CAP}/band).")

        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        for pf, pt in bands:
            band_pages = 0
            for page in range(1, MAX_PAGES_PER_BAND + 1):
                engine.last_status = None
                try:
                    html = await governed_fetch(_facet_url(page, pf, pt))
                except Exception as e:  # noqa: BLE001 — throttle/transient: report what we got, stop honestly
                    fetch_error = str(e)
                    last_http = getattr(engine, "last_status", None)
                    print(f"[as24_facet] band {pf}-{pt} page {page} fetch failed ({e}); stopping.")
                    break
                data = _next_data(html)
                listings = _find_listings(data)
                if not listings:
                    break
                band_pages += 1
                stats["pages_fetched"] += 1
                for raw in listings:
                    stats["listings_seen"] += 1
                    lid = str(raw.get("id") or raw.get("identifier") or "")
                    if lid and lid in seen_listing_ids:
                        stats["dup_ids_collapsed"] += 1
                        continue
                    if lid:
                        seen_listing_ids.add(lid)
                    d = parse_listing_dealer(raw)
                    if d is None:
                        stats["private_skipped"] += 1
                        continue
                    stats["dealer_listings"] += 1
                    async with conn.transaction():
                        dealer_ulid = await upsert_dealer(conn, geo, d)
                        if dealer_ulid is None:
                            stats["geo_skipped"] += 1
                            continue
                        v = parse_listing_vehicle(raw)
                        if not v.deep_link:
                            continue
                        harvested_cageable.add((d.source_dealer_id, v.deep_link))
                        vulid, veh_new = await upsert_vehicle(conn, dealer_ulid, v)
                        stats["cars_caged"] += 1
                        if veh_new:
                            stats["new_cars"] += 1
                            await emit_new_event(conn, vulid, dealer_ulid, v)
                            stats["new_events"] += 1
                        if await link_platform(conn, platform_ulid, vulid, v, lid):
                            stats["edges_created"] += 1
            stats["bands_drained"] += 1
            print(f"[as24_facet] band {pf}-{pt}: pages={band_pages} caged_total={stats['cars_caged']} "
                  f"new={stats['new_cars']} distinct_ids={len(seen_listing_ids)}")
            if fetch_error:
                break

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["harvested_distinct_ids"] = len(seen_listing_ids)
        stats["harvested_cageable"] = len(harvested_cageable)
        stats["platform_code"] = platform_code

        # VAM count quorum for the facet slice (like-with-like, same shape as wholesale).
        db_edges = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)
        db_join_vehicles = await conn.fetchval(
            """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid=$1""", platform_ulid)
        verdict = await record_count_verdict(
            conn, subject_type="platform_facet_slice", subject_key=platform_code,
            claim="distinct cageable cars (facet harvest) == platform_listing edges == join-reachable vehicles",
            paths={"db_edges": db_edges, "db_join_vehicles": db_join_vehicles,
                   "harvested_cageable": len(harvested_cageable)},
            tolerance=0.0)
        stats["verdict"] = verdict
        stats["db_edges"] = db_edges
        stats["db_join_vehicles"] = db_join_vehicles

        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, AS24_FACET_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http,
            captured_distinct=stats.get("harvested_cageable"), platform_ulid=platform_ulid)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, AS24_FACET_SOURCE_KEY, run_error or "facet harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    except Exception as exc:  # noqa: BLE001 — any fatal must be RECORDED, not silent.
        try:
            await record_run(conn, AS24_FACET_SOURCE_KEY, ok=False, rows=0,
                             error=f"facet fatal: {type(exc).__name__}: {exc}")
            await auto_repair(conn, AS24_FACET_SOURCE_KEY, str(exc), phase="scrape")
        except Exception:  # noqa: BLE001
            pass
        raise
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    print("\n" + "=" * 64)
    print("AS24 FACET HARVEST REPORT")
    print("=" * 64)
    for k in ("plan_total_bands", "plan_window", "bands_planned", "bands_drained", "pages_fetched",
              "listings_seen", "dealer_listings",
              "private_skipped", "geo_skipped", "dup_ids_collapsed", "cars_caged", "new_cars",
              "edges_created", "new_dealers", "new_events", "harvested_cageable", "db_edges",
              "db_join_vehicles", "verdict", "health_status", "breaker_state"):
        if k in stats:
            print(f"  {k:22}: {stats[k]}")
    print("=" * 64)


def main() -> None:
    max_bands = int(sys.argv[1]) if len(sys.argv) > 1 else None
    bands = _parse_bands(sys.argv[2]) if len(sys.argv) > 2 else None
    skip_bands = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    stats = asyncio.run(harvest_facet(max_bands=max_bands, bands=bands, skip_bands=skip_bands))
    _print_report(stats)


if __name__ == "__main__":
    main()
