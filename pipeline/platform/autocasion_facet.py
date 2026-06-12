"""autocasion FACET-PARTITION harvester — drains the FULL inventory past the 10k wall.

THE PROBLEM (proven, docs/architecture/tier1_recipes/autocasion_datalayer.md). Both
autocasion surfaces — GraphQL `search` and the flat SSR results stream
`/coches-ocasion?page=N` — share ONE Elasticsearch backend with
`index.max_result_window = 10000`. Any request whose `from + size > 10000` 500s; SSR
mirrors it (`/coches-ocasion?page=384` → "no hemos encontrado" at ~26×384 ≈ 10k). The
flat wholesale module (pipeline.platform.autocasion_wholesale) is therefore an
UN-PARTITIONED proof slice that caps far below the declared ~123k — it can never reach
the whole inventory through one undivided relevance stream.

THE FIX (verified live 2026-06-12 — the recipe's "UNCAPPED SURFACE", NOT assumed):
URL-PATH FACET PARTITION BY MAKE. autocasion serves the full catalogue, with NO cap,
through per-make SSR facet pages whose every slice is < 10k:
  1) ENUMERATE the partition keys: GraphQL `brands(type:CAR)` → 184 make slugs
     (~114 with live stock). Add the 52 `provinces` for the one make over 10k.
  2) SIZE each slice from the SSR facet `<title>` counter (no GraphQL needed):
     GET /coches-segunda-mano/{make}-ocasion → "<title>N.NNN {Make} de segunda mano…".
     Only MERCEDES-BENZ (~10,940) exceeds 10k; every other make is < 10k.
  3) DRAIN makes < 10k: GET /coches-segunda-mano/{make}-ocasion?page=1..N
     (~26 PDP -ref{ID} cards/page) until a page yields 0 refs.
  4) SPLIT MERCEDES-BENZ by the 52 provinces:
     GET /coches-segunda-mano/mercedes-benz-ocasion/{province}?page=N — every province
     slice verified < 10k (madrid 4,105 / barcelona 2,165 / valencia 1,658 …).
  Σ make slices ≈ 123,530 ≈ the SRP declared 123,512. No slice exceeds 10k, so the ES
  wall is NEVER hit and the partition is the complete, uncapped surface.

ARCHITECTURE REUSE. This module does NOT fork the harvest engine — it is the exact same
move pipeline.platform.coches_net_facet makes for coches.net. It imports the wholesale
module's proven per-ref cage path (`process_ref`: GraphQL ad() hydrate → PDP JSON-LD
AutoDealer → per-car transaction → delta NEW/PRICE_CHANGE → platform_listing edge,
idempotent ON CONFLICT), its platform identity, the per-host governor (gql + www buckets),
the S-HEALTH breaker, the VAM count quorum, and the dual-membership model. The ONLY
additions are: (a) the make/province partition enumeration + sizing, (b) the partition
plan (make slices; MB→province), and (c) the partition loop that drains each slice's SSR
?page=N through that same machinery with a GLOBAL seen_ids set so cross-slice overlap is
collapsed exactly once. Delta / VAM / idempotency are preserved byte-for-byte.

Run (full uncapped drain — every make slice, the operator's one command):
    python -m pipeline.platform.autocasion_facet --makes all
Run (bounded proof — first N makes by size, or named makes):
    python -m pipeline.platform.autocasion_facet --max-makes 15
    python -m pipeline.platform.autocasion_facet --make seat --make volkswagen
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time

import asyncpg

from pipeline.engine.governor import governor, host_of
from pipeline.geo import GeoResolver
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict

# Reuse the wholesale module's proven machinery — identity, fetcher, cage path, parsers.
from pipeline.platform.autocasion_wholesale import (
    AC_PLATFORM_RECIPE,
    AC_SOURCE_KEY,
    DSN,
    GQL_ENDPOINT,
    SSR_HOST,
    SSR_ITEMS_PER_PAGE,
    AutocasionFetcher,
    _to_int,
    autocasion_platform_cdp_code,
    ensure_platform_entity,
    parse_ssr_refs,
    process_ref,
)

# ---------------------------------------------------------------------------
# Partition plan (verified live 2026-06-12 — see module docstring + recipe).
# ---------------------------------------------------------------------------

# A make whose <title> total exceeds this gets province-sub-partitioned. 10,000 is the
# hard ES max_result_window; sizing under it guarantees the slice drains to its own end
# without hitting the relevance wall. Only MERCEDES-BENZ exceeds it today.
SPLIT_THRESHOLD = 10_000

# A hard page ceiling per slice — a guardrail, never expected to bite (a real slice ends
# on the first 0-ref page well before this). 10k/26 ≈ 385; this is comfortable headroom.
MAX_PAGES_PER_SLICE = 600

# GraphQL enumeration of the partition keys (OPEN, no auth).
_BRANDS_QUERY = "{brands(type:CAR){id name slug}}"
_PROVINCES_QUERY = "{provinces{id name slug}}"

# SSR facet <title> -> slice total: "<title>N.NNN {Make} de segunda mano…".
_TITLE_TOTAL_RE = re.compile(r"<title>\s*([\d\.]+)\s")

# The make whose single slice exceeds 10k and must be split by province. Held as a slug so
# the split rule is keyed off the live <title> size, not a hardcoded make list (future
# drift-safe: any make that grows past 10k is split the same way).
MERCEDES_SLUG = "mercedes-benz"


def _facet_path(make_slug: str, province_slug: str | None = None) -> str:
    """The SSR facet path for a slice. make-only, or make×province for the split make."""
    base = f"{SSR_HOST}/coches-segunda-mano/{make_slug}-ocasion"
    return f"{base}/{province_slug}" if province_slug else base


def _parse_title_total(html: str) -> int:
    """Slice total from the SSR facet <title> ("5.448 SEAT de segunda mano…" -> 5448)."""
    m = _TITLE_TOTAL_RE.search(html)
    if not m:
        return 0
    return _to_int(m.group(1).replace(".", "")) or 0


# ---------------------------------------------------------------------------
# Partition enumeration + sizing. Each probe is a single governed GET/POST; the slice
# total rides in the facet <title>, so sizing needs no GraphQL search call (and never
# touches the 10k wall). coverage_sum = Σ(slice declared) is the capture-recapture path.
# ---------------------------------------------------------------------------


async def enumerate_makes(governed_fetch) -> list[dict]:
    """GraphQL brands(type:CAR) -> the make partition keys (id, name, slug)."""
    raw = await governed_fetch(GQL_ENDPOINT, method="POST", gql={"query": _BRANDS_QUERY})
    brands = ((json.loads(raw).get("data") or {}).get("brands")) or []
    return [b for b in brands if b.get("slug")]


async def enumerate_provinces(governed_fetch) -> list[dict]:
    """GraphQL provinces -> the 52 province keys (for splitting the over-10k make)."""
    raw = await governed_fetch(GQL_ENDPOINT, method="POST", gql={"query": _PROVINCES_QUERY})
    provs = ((json.loads(raw).get("data") or {}).get("provinces")) or []
    return [p for p in provs if p.get("slug")]


async def plan_partitions(governed_fetch, makes: list[dict],
                          provinces: list[dict]) -> tuple[list[dict], int, int]:
    """Build the slice list + summed declared coverage.

    For each make: probe its <title> total. If 0 (no live stock) skip it. If <=
    SPLIT_THRESHOLD it is one slice. If it exceeds it (only MERCEDES-BENZ today), split
    into the 52 province slices (each sized from its own <title>). Returns
    (slices, coverage_sum, makes_with_stock). coverage_sum sums the slices ACTUALLY
    drained (province bands for the split make, not the make aggregate) so it matches what
    the drain traverses."""
    slices: list[dict] = []
    coverage_sum = 0
    makes_with_stock = 0
    for mk in makes:
        slug = mk["slug"]
        html = await governed_fetch(_facet_path(slug))
        total = _parse_title_total(html)
        if total <= 0:
            continue  # make with no live stock — not a partition.
        makes_with_stock += 1
        if total <= SPLIT_THRESHOLD:
            slices.append({"make": slug, "make_name": mk.get("name"), "province": None,
                           "province_name": None, "declared": total})
            coverage_sum += total
            continue
        # Over the 10k wall -> province sub-partition (each province slice < 10k, verified).
        print(f"[autocasion_facet] make {slug} declared {total} > {SPLIT_THRESHOLD}; "
              f"splitting by {len(provinces)} provinces.")
        for pv in provinces:
            phtml = await governed_fetch(_facet_path(slug, pv["slug"]))
            pt = _parse_title_total(phtml)
            if pt <= 0:
                continue
            slices.append({"make": slug, "make_name": mk.get("name"),
                           "province": pv["slug"], "province_name": pv.get("name"),
                           "declared": pt})
            coverage_sum += pt
    return slices, coverage_sum, makes_with_stock


# ---------------------------------------------------------------------------
# Drain one slice (make, or make×province) to its end via SSR ?page=N through the SAME
# per-ref cage path the wholesale module uses. GLOBAL seen_ids / harvested_cageable /
# stats so cross-slice overlap (a listing under make AND make×province) collapses once.
# ---------------------------------------------------------------------------


async def _drain_slice(conn: asyncpg.Connection, geo: GeoResolver, platform_ulid: str,
                       fetcher: AutocasionFetcher, governed_fetch, slc: dict,
                       seen_ids: set, harvested_cageable: set,
                       stats: dict) -> tuple[bool, str | None, int | None]:
    """Drain a single facet slice to exhaustion (first 0-ref page = clean end).

    Returns (clean_finish, fetch_error, last_http). clean_finish=True means the slice
    ended on an empty/no-results page (fully drained); False means an SSR fetch error
    stopped it (the breaker signal). Each ?page=N is enumerated, then every -ref{ID} on it
    is hydrated + caged through process_ref (the shared, proven path). A GLOBAL seen_ids
    dedups across BOTH pages and slices."""
    path = _facet_path(slc["make"], slc["province"])
    fetch_error: str | None = None
    last_http: int | None = None
    for page in range(1, MAX_PAGES_PER_SLICE + 1):
        # Step 1 — enumerate ad ids from this slice's SSR results page.
        try:
            html = await governed_fetch(f"{path}?page={page}")
        except Exception as e:  # noqa: BLE001
            fetch_error = str(e)
            last_http = fetcher.last_status
            print(f"[autocasion_facet] slice {slc['make']}"
                  f"{('/' + slc['province']) if slc['province'] else ''} page {page} "
                  f"SSR failed ({e}); stopping this slice honestly.")
            break
        stats["pages_fetched"] += 1
        refs = parse_ssr_refs(html)
        if not refs:
            break  # clean end of this slice (0 refs / "no hemos encontrado").

        for pdp_url, ad_id in refs:
            err = await process_ref(conn, geo, platform_ulid, governed_fetch,
                                    pdp_url, ad_id, seen_ids, harvested_cageable, stats)
            if err == "fetch":
                last_http = fetcher.last_status

    clean_finish = fetch_error is None
    return clean_finish, fetch_error, last_http


# ---------------------------------------------------------------------------
# Orchestration — plan, then drain every slice through the shared machinery, then the
# SAME VAM count quorum + recipe + S-HEALTH heartbeat the wholesale module runs.
# ---------------------------------------------------------------------------


async def harvest_facet(make_filter: list[str] | None = None,
                        max_makes: int | None = None) -> dict:
    """Drain autocasion by make-partition.

    make_filter: explicit make slugs to drain (None = all makes with stock).
    max_makes:   after sizing, keep only the first N makes (by descending declared size)
                 — the bounded proof knob. None = no cap (the full uncapped drain).
    """
    conn = await asyncpg.connect(DSN)
    fetcher = AutocasionFetcher()  # one fingerprint + cookie jar for the whole drain
    stats = {
        "pages_fetched": 0, "refs_seen": 0, "ads_hydrated": 0, "pdp_fetched": 0,
        "private_skipped": 0, "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "price_changes_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "fetch_errors": 0,
        "parse_errors": 0, "dealers_distinct": 0,
        "makes_total": 0, "makes_with_stock": 0, "slices": 0,
        "slices_clean": 0, "slices_errored": 0, "coverage_sum": 0,
    }
    # GLOBAL harvest truth — distinct across ALL slices (cross-slice overlap from a listing
    # appearing under make AND make×province collapses here exactly once).
    seen_ids: set[str] = set()
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if autocasion's breaker is OPEN (recent ban cooling), skip gracefully.
    if await is_open(conn, AC_SOURCE_KEY):
        print(f"[autocasion_facet] breaker OPEN for {AC_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, last snapshot still served).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": AC_SOURCE_KEY}

    # GOVERNOR: the single per-host choke point. gql.autocasion.com (JSON_API bucket) and
    # www.autocasion.com (STEALTH bucket) are paced independently.
    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch)

    fetch_error: str | None = None
    last_http: int | None = None
    t0 = time.monotonic()
    try:
        geo = await GeoResolver.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = autocasion_platform_cdp_code()
        print(f"[autocasion_facet] platform entity ready: {platform_code} (ulid={platform_ulid})")
        print(f"[autocasion_facet] governor paces hosts {host_of(SSR_HOST)} + "
              f"{host_of(GQL_ENDPOINT)} (per-host token buckets).")

        # ---- ENUMERATE the partition keys.
        makes = await enumerate_makes(governed_fetch)
        provinces = await enumerate_provinces(governed_fetch)
        stats["makes_total"] = len(makes)
        print(f"[autocasion_facet] brands(type:CAR) -> {len(makes)} makes; "
              f"provinces -> {len(provinces)} (for the >10k make split).")
        if make_filter:
            wanted = {s.lower() for s in make_filter}
            makes = [m for m in makes if m["slug"].lower() in wanted]
            print(f"[autocasion_facet] --make filter -> {len(makes)} makes: "
                  f"{[m['slug'] for m in makes]}")

        # ---- PLAN: size every make slice from its <title>; split the >10k make by province.
        print(f"[autocasion_facet] planning slices over {len(makes)} makes "
              f"(split threshold {SPLIT_THRESHOLD})...")
        slices, coverage_sum, makes_with_stock = await plan_partitions(
            governed_fetch, makes, provinces)
        stats["makes_with_stock"] = makes_with_stock
        stats["coverage_sum"] = coverage_sum
        stats["declared_full"] = coverage_sum

        # Bounded proof: keep the N largest slices (by declared size) so the proof drains
        # several COMPLETE mid/large slices end to end, proving the partition reaches past
        # the 10k wall. None = the full uncapped drain (every slice).
        if max_makes is not None and max_makes > 0:
            slices = sorted(slices, key=lambda s: s["declared"], reverse=True)[:max_makes]
            coverage_sum = sum(s["declared"] for s in slices)
            stats["coverage_sum"] = coverage_sum
            print(f"[autocasion_facet] --max-makes {max_makes} -> draining the "
                  f"{len(slices)} largest slices (sum declared = {coverage_sum}).")
        stats["slices"] = len(slices)
        split_make = sorted({s["make"] for s in slices if s["province"]})
        print(f"[autocasion_facet] PLAN: {len(slices)} slices to drain; "
              f"province-split makes = {split_make or 'none'}; "
              f"sum(slice declared) = {coverage_sum}.")

        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        # ---- DRAIN: every slice to its end through the shared per-ref cage path.
        for i, slc in enumerate(slices, 1):
            clean, perr, phttp = await _drain_slice(
                conn, geo, platform_ulid, fetcher, governed_fetch, slc,
                seen_ids, harvested_cageable, stats)
            if clean:
                stats["slices_clean"] += 1
            else:
                stats["slices_errored"] += 1
                fetch_error = perr or fetch_error
                last_http = phttp if phttp is not None else last_http
            elapsed = time.monotonic() - t0
            cpm = stats["cars_caged"] / (elapsed / 60) if elapsed > 0 else 0.0
            label = slc["make"] + (f"/{slc['province']}" if slc["province"] else "")
            print(f"[autocasion_facet] [{i}/{len(slices)}] {label:<28} "
                  f"declared={slc['declared']:6d} -> caged_total={stats['cars_caged']} "
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

        recipe = dict(AC_PLATFORM_RECIPE)
        recipe["scope"] = ("platform-facet (URL-path make partition; make×province for the "
                           ">10k make — uncapped surface past ES max_result_window=10000)")
        recipe["enumeration"] = (
            "FACET partitions: brands(type:CAR) make slugs sized by SSR <title>; "
            f"makes >{SPLIT_THRESHOLD} split by 52 provinces; each slice drained "
            "GET /coches-segunda-mano/{make}-ocasion[/{province}]?page=1..N to first 0-ref page")
        recipe_path = write_recipe(platform_code, recipe)
        print(f"[autocasion_facet] recipe written: {recipe_path}")

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

        # ---- S-HEALTH heartbeat. OK when pages fetched, no fetch error stopped a slice,
        # VAM did not refute. A partial-but-clean run (some slice errored) records the error.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, AC_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, AC_SOURCE_KEY, run_error or "facet harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[autocasion_facet] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("AUTOCASION FACET-PARTITION HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print("  --- coverage proof (capture-recapture) ---")
    print(f"  makes (total/w-stock) : {stats.get('makes_total')} / {stats.get('makes_with_stock')}")
    print(f"  slices drained        : {stats.get('slices')} "
          f"({stats.get('slices_clean')} clean / {stats.get('slices_errored')} errored)")
    print(f"  sum(slice declared)   : {stats.get('coverage_sum')}  (declared full this run)")
    print("  --- drain ---")
    print(f"  SSR pages fetched     : {stats['pages_fetched']}")
    print(f"  refs seen             : {stats['refs_seen']}")
    print(f"  distinct listing ids  : {stats.get('harvested_distinct_ids')}")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page + cross-slice)")
    print(f"  ads hydrated (gql)    : {stats['ads_hydrated']}")
    print(f"  PDPs fetched          : {stats['pdp_fetched']}")
    print(f"  private/no-dealer skip: {stats['private_skipped']}")
    print(f"  geo skipped (bad prov): {stats['geo_skipped']}")
    print(f"  fetch errors (ad/pdp) : {stats['fetch_errors']}")
    print(f"  parse errors (skipped): {stats['parse_errors']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for autocasion = {stats.get('db_edges')})")
    print(f"  price changes captured: {stats['price_changes_captured']}")
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


def main() -> None:
    # Windows consoles default to cp1252; force UTF-8 on stdout/stderr so the report's
    # em-dash and accented dealer/city names in error lines never crash the run.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):  # pragma: no cover — non-reconfigurable stream
            pass
    parser = argparse.ArgumentParser(
        description="autocasion FACET-PARTITION harvester (make-partition uncapped drain to 100%)")
    parser.add_argument("--make", action="append", default=None, metavar="SLUG",
                        help="drain only this make slug (repeatable: --make seat --make audi). "
                             "Omit to enumerate all makes.")
    parser.add_argument("--makes", type=str, default=None,
                        help="'all' = the FULL uncapped drain (every make slice, one command). "
                             "Equivalent to omitting --make/--max-makes.")
    parser.add_argument("--max-makes", type=int, default=None,
                        help="bounded proof: drain only the N LARGEST slices by declared size "
                             "(several complete slices end to end). Omit for the full drain.")
    args = parser.parse_args()

    make_filter: list[str] | None = None
    if args.make:
        make_filter = list(args.make)
    elif args.makes and args.makes.lower() != "all":
        make_filter = [s.strip() for s in args.makes.split(",") if s.strip()]

    stats = asyncio.run(harvest_facet(make_filter=make_filter, max_makes=args.max_makes))
    _print_report(stats)


if __name__ == "__main__":
    main()
