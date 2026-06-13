"""autocasion FACET-PARTITION harvester — drains the FULL inventory of EVERY segment.

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

EVERY SEGMENT, NOT ONLY USED (owner mandate — verified live 2026-06-13,
docs/architecture/segments/autocasion.md). autocasion exposes THREE drainable inventory
segments, each its OWN SSR facet tree carrying PDP -ref{ID} cards and a <title> count,
each drained by the SAME make-partition machinery — only the facet path template + title
shape differ per segment:
  • vo  (USED / ocasión)  — /coches-segunda-mano/{make}-ocasion[/{province}]   ~123,512
        (the historical default; MERCEDES-BENZ > 10k → province split)
  • vn  (NEW / coches nuevos, == the new-car catalog: every make/model/version offer is a
        sellable -ref{ID} ad) — /coches-nuevos/{make}                            ~5,946
        (76 makes w/ stock; EVERY make < 10k → no province split needed)
  • km0 (KM0 / Demo)      — /coches-km0/{make}-km0                                ~5,994
        (84 makes w/ stock; EVERY make < 10k → no province split needed)
RENTING does not exist on autocasion (every /renting* path 404s); `catalog` is an alias of
`vn` (the new offers ARE the catalog). ad() hydration + PDP JSON-LD AutoDealer attribution
were verified live on a vn ref (AUDI A3, dealer unoauto/28027) and a km0 ref (SEAT Arona,
km0=true) — so the proven cage path drains vn/km0 byte-for-byte, no new hydrate code.
Site-displayed reconciliation: 123,512 (vo) + 5,946 (vn) + 5,994 (km0) ≈ 135,452 cars.

ARCHITECTURE REUSE. This module does NOT fork the harvest engine — it is the exact same
move pipeline.platform.coches_net_facet makes for coches.net. It imports the wholesale
module's proven per-ref cage path (`process_ref`: GraphQL ad() hydrate → PDP JSON-LD
AutoDealer → per-car transaction → delta NEW/PRICE_CHANGE → platform_listing edge,
idempotent ON CONFLICT), its platform identity, the per-host governor (gql + www buckets),
the S-HEALTH breaker, the VAM count quorum, and the dual-membership model. The ONLY
additions are: (a) the SEGMENT descriptor (per-segment facet path + title shape),
(b) the make/province partition enumeration + sizing over the chosen segment(s),
(c) the partition plan (make slices; province-split only when a slice > 10k), and (d) the
partition loop that drains each slice's SSR ?page=N through that same machinery with a
GLOBAL seen_ids set so cross-slice AND cross-segment overlap is collapsed exactly once.
Delta / VAM / idempotency are preserved byte-for-byte.

Run (FULL uncapped drain of EVERY segment — the operator's one command):
    python -m pipeline.platform.autocasion_facet --segment all
Run (one segment fully):
    python -m pipeline.platform.autocasion_facet --segment vn
    python -m pipeline.platform.autocasion_facet --segment km0
    python -m pipeline.platform.autocasion_facet --segment vo   (default; back-compat)
Run (bounded proof — first N slices by size, or named makes, within a segment):
    python -m pipeline.platform.autocasion_facet --segment vn --max-makes 5
    python -m pipeline.platform.autocasion_facet --segment vn --make seat --make audi
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
from dataclasses import dataclass

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
    _dedup_ref,
    _to_int,
    autocasion_platform_cdp_code,
    cage_hydrated,
    ensure_platform_entity,
    hydrate_ref,
    parse_ssr_refs,
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

# Per-PAGE hydration concurrency. A page carries ~26 refs; each ref is a gql POST
# (gql.autocasion.com, JSON_API bucket 12 req/s) + a PDP GET (www.autocasion.com, STEALTH
# bucket 2 req/s, 0.5 s min-spacing). Hydrating ONE AT A TIME (the old serial drain) leaves
# both buckets 1-in-flight — a whole make of ~8k cars drains at ~0.61 s/car (~84 min) with
# NO log line until the slice ENDS, which reads as a freeze. Running a page's refs through
# asyncio.gather lets the governor fill the buckets concurrently — it remains the TRUE
# ceiling (concurrency only keeps the buckets saturated, it can NEVER out-pace a host).
#
# MEASURED 2026-06-13 (live audi, serial vs gather=12): IDENTICAL ~0.61 s/car. The binding
# constraint is the www.autocasion.com PDP-GET bucket (2 req/s + 0.5 s spacing), needed once
# per car for dealer attribution — so 12-wide gather queues on that floor and matches serial.
# Concurrency is therefore correct + safe (mandate: "do NOT out-pace gql.autocasion.com" — it
# CAN'T, by construction) and future-proofs the gql side if the www pace is ever raised on
# EVIDENCE, but it is NOT today's speed lever. Today's lever the operator owns is the www
# bucket rate in governor.py (documented MEASURED-permissive), a ban-surface change left to
# the operator. The real fix this module delivers is VISIBLE INCREMENTAL progress (below),
# so an 84-min audi drain is a healthy climbing counter, not a silent freeze.
HYDRATE_CONCURRENCY = 12

# Print a progress line every N pages WITHIN a slice (not only at slice-end), so caged_total
# climbs visibly during a big make and a stall is detectable in seconds, not hidden for an
# hour. A page is ~26 cars, so every 5 pages ≈ ~130 cars ≈ a heartbeat every ~30-60 s.
PROGRESS_EVERY_PAGES = 5

# GraphQL enumeration of the partition keys (OPEN, no auth).
_BRANDS_QUERY = "{brands(type:CAR){id name slug}}"
_PROVINCES_QUERY = "{provinces{id name slug}}"

# SSR facet <title> -> slice total: "<title>N.NNN {Make} de segunda mano…".
_TITLE_TOTAL_RE = re.compile(r"<title>\s*([\d\.]+)\s")

# The make whose single slice exceeds 10k and must be split by province. Held as a slug so
# the split rule is keyed off the live <title> size, not a hardcoded make list (future
# drift-safe: any make that grows past 10k is split the same way).
MERCEDES_SLUG = "mercedes-benz"


# ---------------------------------------------------------------------------
# SEGMENT descriptors — each inventory segment autocasion exposes as its OWN SSR facet
# tree (verified live 2026-06-13, docs/architecture/segments/autocasion.md). Each segment
# is drained by the SAME make-partition machinery; only the facet-path template and the
# make-facet <title> shape differ. A segment whose make slice exceeds 10k is split by
# province the same way the used segment splits MERCEDES-BENZ (none of vn/km0 do today —
# every make slice < 10k — but the split path is segment-generic, future-drift-safe).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Segment:
    """One drainable inventory segment of autocasion.

    key:        the --segment selector (vo|vn|km0).
    label:      human label for the report / recipe.
    make_path:  SSR facet path template for a make slice -> "{make}" is the brand slug.
    prov_path:  SSR facet path template for a make×province slice when a make > 10k; takes
                "{make}" and "{prov}". Used only when SPLIT_THRESHOLD is exceeded.
    The slice <title> always leads with the slice total ("161 Seat nuevos…",
    "74 Km 0 Seat…", "5.448 SEAT de segunda mano…") so _parse_title_total reads all three.
    """
    key: str
    label: str
    make_path: str
    prov_path: str


# vo: the historical default — used/ocasión, make[-province] facet, MB splits by province.
SEG_VO = Segment(
    key="vo", label="USED (ocasión)",
    make_path="/coches-segunda-mano/{make}-ocasion",
    prov_path="/coches-segunda-mano/{make}-ocasion/{prov}",
)
# vn: NEW / coches nuevos (the new-car catalog). Make facet /coches-nuevos/{make};
# province facet /coches-nuevos/{make}/{prov}-provincia (only if a make ever > 10k).
SEG_VN = Segment(
    key="vn", label="NEW (coches nuevos / catalog)",
    make_path="/coches-nuevos/{make}",
    prov_path="/coches-nuevos/{make}/{prov}-provincia",
)
# km0: KM0 / Demo. Make facet /coches-km0/{make}-km0; province facet
# /coches-km0/{make}-km0/{prov} (only if a make ever > 10k; km0 uses bare city slugs).
SEG_KM0 = Segment(
    key="km0", label="KM0 (km cero / demo)",
    make_path="/coches-km0/{make}-km0",
    prov_path="/coches-km0/{make}-km0/{prov}",
)

# Canonical registry + the aliases the owner mandate names. `catalog` == vn (the new
# offers ARE the catalog). `renting` does not exist on autocasion (every /renting* 404s) —
# accepted as a selector but resolves to an empty plan and is reported as a non-existent
# segment (honest declared gap, never a silent skip).
SEGMENTS: dict[str, Segment] = {s.key: s for s in (SEG_VO, SEG_VN, SEG_KM0)}
SEGMENT_ALIASES: dict[str, str] = {"catalog": "vn", "vehiculos-nuevos": "vn"}
NONEXISTENT_SEGMENTS: set[str] = {"renting"}
ALL_SEGMENT_KEYS: list[str] = ["vo", "vn", "km0"]


def resolve_segments(selector: str | None) -> tuple[list[Segment], list[str]]:
    """Resolve a --segment selector to (segments_to_drain, nonexistent_requested).

    selector None or 'vo' -> [vo] (back-compat default). 'all' -> [vo, vn, km0].
    A comma list ('vn,km0') -> those. Aliases map to their canonical key. A requested
    segment that does not exist on autocasion (renting) is returned in the second list so
    the caller can report it as a declared gap rather than silently dropping it."""
    if not selector or selector.lower() == "vo":
        return [SEG_VO], []
    sel = selector.lower()
    if sel == "all":
        return [SEGMENTS[k] for k in ALL_SEGMENT_KEYS], []
    wanted: list[Segment] = []
    nonexistent: list[str] = []
    seen: set[str] = set()
    for raw in sel.split(","):
        name = raw.strip()
        if not name:
            continue
        canon = SEGMENT_ALIASES.get(name, name)
        if canon in NONEXISTENT_SEGMENTS:
            nonexistent.append(name)
            continue
        seg = SEGMENTS.get(canon)
        if seg is None:
            raise SystemExit(
                f"[autocasion_facet] unknown segment '{name}'. "
                f"Valid: {', '.join(ALL_SEGMENT_KEYS)}, all, "
                f"{', '.join(SEGMENT_ALIASES)} (alias of vn); renting (non-existent).")
        if seg.key not in seen:
            seen.add(seg.key)
            wanted.append(seg)
    return wanted, nonexistent


def _facet_path(seg: Segment, make_slug: str, province_slug: str | None = None) -> str:
    """The SSR facet URL for a slice of `seg`: make-only, or make×province for a split make."""
    if province_slug:
        rel = seg.prov_path.format(make=make_slug, prov=province_slug)
    else:
        rel = seg.make_path.format(make=make_slug)
    return f"{SSR_HOST}{rel}"


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


async def plan_partitions(governed_fetch, seg: Segment, makes: list[dict],
                          provinces: list[dict]) -> tuple[list[dict], int, int]:
    """Build the slice list + summed declared coverage for ONE segment.

    For each make: probe its <title> total on `seg`'s make facet. If 0 (no live stock in
    this segment) skip it. If <= SPLIT_THRESHOLD it is one slice. If it exceeds it (only
    MERCEDES-BENZ on vo today; never on vn/km0), split into province slices (each sized
    from its own <title>). Returns (slices, coverage_sum, makes_with_stock). coverage_sum
    sums the slices ACTUALLY drained (province bands for a split make, not the make
    aggregate) so it matches what the drain traverses. Every slice carries its `segment`
    key so the drain rebuilds the right facet path and seen_ids dedups cross-segment."""
    slices: list[dict] = []
    coverage_sum = 0
    makes_with_stock = 0
    for mk in makes:
        slug = mk["slug"]
        html = await governed_fetch(_facet_path(seg, slug))
        total = _parse_title_total(html)
        if total <= 0:
            continue  # make with no live stock in this segment — not a partition.
        makes_with_stock += 1
        if total <= SPLIT_THRESHOLD:
            slices.append({"segment": seg.key, "make": slug, "make_name": mk.get("name"),
                           "province": None, "province_name": None, "declared": total})
            coverage_sum += total
            continue
        # Over the 10k wall -> province sub-partition (each province slice < 10k, verified).
        print(f"[autocasion_facet] [{seg.key}] make {slug} declared {total} > "
              f"{SPLIT_THRESHOLD}; splitting by {len(provinces)} provinces.")
        for pv in provinces:
            phtml = await governed_fetch(_facet_path(seg, slug, pv["slug"]))
            pt = _parse_title_total(phtml)
            if pt <= 0:
                continue
            slices.append({"segment": seg.key, "make": slug, "make_name": mk.get("name"),
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
                       seen_ids: set, harvested_cageable: set, stats: dict,
                       concurrency: int = HYDRATE_CONCURRENCY,
                       max_pages: int = MAX_PAGES_PER_SLICE,
                       ) -> tuple[bool, str | None, int | None]:
    """Drain a single facet slice to exhaustion (first 0-ref page = clean end).

    Returns (clean_finish, fetch_error, last_http). clean_finish=True means the slice
    ended on an empty/no-results page (fully drained); False means an SSR fetch error
    stopped it (the breaker signal).

    Each ?page=N is enumerated, then the page's fresh -ref{ID}s are hydrated CONCURRENTLY
    (PHASE A — gql ad() + PDP JSON-LD, up to HYDRATE_CONCURRENCY in flight so the governor
    fills both host buckets instead of crawling 1-in-flight) and caged SEQUENTIALLY on the
    single asyncpg connection (PHASE B — the byte-for-byte cage tail). Ingest is INCREMENTAL
    (committed per car, per page) and a progress line prints every PROGRESS_EVERY_PAGES pages
    so caged_total climbs visibly and a stall surfaces in seconds, not at slice-end.
    A GLOBAL seen_ids dedups across BOTH pages and slices (and across segments)."""
    seg = SEGMENTS[slc["segment"]]
    path = _facet_path(seg, slc["make"], slc["province"])
    label = f"{seg.key}:{slc['make']}" + (f"/{slc['province']}" if slc["province"] else "")
    fetch_error: str | None = None
    last_http: int | None = None
    sem = asyncio.Semaphore(max(1, concurrency))
    t_slice = time.monotonic()

    async def _hydrate(pdp_url: str, ad_id: str):
        async with sem:
            return await hydrate_ref(geo, governed_fetch, pdp_url, ad_id, stats)

    for page in range(1, max(1, max_pages) + 1):
        # Step 1 — enumerate ad ids from this slice's SSR results page.
        try:
            html = await governed_fetch(f"{path}?page={page}")
        except Exception as e:  # noqa: BLE001
            fetch_error = str(e)
            last_http = fetcher.last_status
            print(f"[autocasion_facet] [{seg.key}] slice "
                  f"{slc['make']}{('/' + slc['province']) if slc['province'] else ''} "
                  f"page {page} SSR failed ({e}); stopping this slice honestly.")
            break
        stats["pages_fetched"] += 1
        refs = parse_ssr_refs(html)
        if not refs:
            break  # clean end of this slice (0 refs / "no hemos encontrado").

        # Pre-dedup against the GLOBAL seen set BEFORE hydrating: a ref already seen on an
        # earlier page/slice/segment is accounted (dup_ids_collapsed) and never re-fetched.
        fresh: list[tuple[str, str]] = []
        for pdp_url, ad_id in refs:
            stats["refs_seen"] += 1
            if _dedup_ref(ad_id, seen_ids, stats):
                fresh.append((pdp_url, ad_id))

        if fresh:
            # PHASE A — concurrent network hydrate (governed; buckets are the real ceiling).
            results = await asyncio.gather(
                *(_hydrate(pdp_url, ad_id) for pdp_url, ad_id in fresh),
                return_exceptions=True)
            # PHASE B — sequential DB cage on the single connection (asyncpg-safe).
            for res in results:
                if isinstance(res, Exception):
                    stats["parse_errors"] += 1
                    continue
                if res == "fetch":
                    last_http = fetcher.last_status
                    continue
                if isinstance(res, str):
                    continue  # 'skip' — already accounted in hydrate_ref's stats.
                await cage_hydrated(conn, geo, platform_ulid, res,
                                    harvested_cageable, stats)

        # Incremental progress heartbeat — caged_total climbs WITHIN the slice now.
        if page % PROGRESS_EVERY_PAGES == 0:
            dt = time.monotonic() - t_slice
            cpm = stats["cars_caged"] / (dt / 60) if dt > 0 else 0.0
            print(f"[autocasion_facet] [{seg.key}] {label:<28} page {page:>3} "
                  f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                  f"edges={stats['edges_created']} | {cpm:.0f} cars/min")

    clean_finish = fetch_error is None
    return clean_finish, fetch_error, last_http


# ---------------------------------------------------------------------------
# Orchestration — plan, then drain every slice through the shared machinery, then the
# SAME VAM count quorum + recipe + S-HEALTH heartbeat the wholesale module runs.
# ---------------------------------------------------------------------------


async def harvest_facet(make_filter: list[str] | None = None,
                        max_makes: int | None = None,
                        segments: list[Segment] | None = None,
                        nonexistent: list[str] | None = None,
                        concurrency: int = HYDRATE_CONCURRENCY,
                        max_pages_per_slice: int | None = None) -> dict:
    """Drain autocasion by make-partition, over one or more SEGMENTS.

    make_filter: explicit make slugs to drain (None = all makes with stock).
    max_makes:   after sizing, keep only the first N slices (by descending declared size)
                 — the bounded proof knob. None = no cap (the full uncapped drain).
    segments:    the segments to drain (None = [vo], the back-compat default). Each is
                 planned independently then concatenated into ONE slice list so the GLOBAL
                 seen_ids set collapses any cross-segment overlap exactly once.
    nonexistent: segment names requested that do not exist on autocasion (e.g. renting),
                 carried into the report as a declared gap (never a silent skip).
    concurrency: per-page hydration concurrency (refs hydrated in flight). The governor's
                 per-host bucket stays the true ceiling; this only keeps it saturated.
    max_pages_per_slice: hard page cap per slice for a BOUNDED test (None = drain to the
                 slice's natural 0-ref end). Lets an audi-only test cap cleanly + fast.
    """
    nonexistent = nonexistent or []
    if segments is None:
        segments = [SEG_VO]  # back-compat default (only when caller passed nothing)
    if not segments:
        # Only non-existent segment(s) requested (e.g. renting) — nothing to drain, but
        # report honestly instead of silently defaulting to vo.
        return {"skipped": True, "reason": "no_existing_segment",
                "segments_nonexistent": list(nonexistent), "source_key": AC_SOURCE_KEY}
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
        "concurrency": max(1, concurrency),
        "segments_requested": [s.key for s in segments],
        "segments_nonexistent": list(nonexistent),
        "per_segment": {},  # key -> {label, makes_with_stock, slices, declared, caged}
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

        # ---- ENUMERATE the partition keys (shared across every segment — same make/province
        # vocabulary; each segment only differs in its facet-path template + title shape).
        makes = await enumerate_makes(governed_fetch)
        provinces = await enumerate_provinces(governed_fetch)
        stats["makes_total"] = len(makes)
        seg_keys = ", ".join(s.key for s in segments)
        print(f"[autocasion_facet] brands(type:CAR) -> {len(makes)} makes; "
              f"provinces -> {len(provinces)} (for any >10k make split). "
              f"segments = [{seg_keys}]"
              + (f"; non-existent requested = {nonexistent}" if nonexistent else ""))
        if make_filter:
            wanted = {s.lower() for s in make_filter}
            makes = [m for m in makes if m["slug"].lower() in wanted]
            print(f"[autocasion_facet] --make filter -> {len(makes)} makes: "
                  f"{[m['slug'] for m in makes]}")

        # ---- PLAN: per segment, size every make slice from its <title>; split any >10k
        # make by province. Concatenate into ONE slice list (seen_ids dedups cross-segment).
        slices: list[dict] = []
        coverage_sum = 0
        makes_with_stock_union: set[str] = set()
        for seg in segments:
            print(f"[autocasion_facet] [{seg.key}] planning slices over {len(makes)} makes "
                  f"(split threshold {SPLIT_THRESHOLD})...")
            seg_slices, seg_cov, seg_mws = await plan_partitions(
                governed_fetch, seg, makes, provinces)
            slices.extend(seg_slices)
            coverage_sum += seg_cov
            makes_with_stock_union.update(s["make"] for s in seg_slices)
            stats["per_segment"][seg.key] = {
                "label": seg.label, "makes_with_stock": seg_mws,
                "slices": len(seg_slices), "declared": seg_cov, "caged": 0,
                "split_makes": sorted({s["make"] for s in seg_slices if s["province"]}),
            }
            print(f"[autocasion_facet] [{seg.key}] planned {len(seg_slices)} slices "
                  f"({seg_mws} makes w/ stock); declared = {seg_cov}.")
        stats["makes_with_stock"] = len(makes_with_stock_union)
        stats["coverage_sum"] = coverage_sum
        stats["declared_full"] = coverage_sum

        # Bounded proof: keep the N largest slices (by declared size) ACROSS segments so the
        # proof drains several COMPLETE mid/large slices end to end, proving the partition
        # reaches past the 10k wall. None = the full uncapped drain (every slice).
        if max_makes is not None and max_makes > 0:
            slices = sorted(slices, key=lambda s: s["declared"], reverse=True)[:max_makes]
            coverage_sum = sum(s["declared"] for s in slices)
            stats["coverage_sum"] = coverage_sum
            print(f"[autocasion_facet] --max-makes {max_makes} -> draining the "
                  f"{len(slices)} largest slices (sum declared = {coverage_sum}).")
        stats["slices"] = len(slices)
        split_make = sorted({f"{s['segment']}:{s['make']}" for s in slices if s["province"]})
        print(f"[autocasion_facet] PLAN: {len(slices)} slices to drain across "
              f"{len(segments)} segment(s); province-split = {split_make or 'none'}; "
              f"sum(slice declared) = {coverage_sum}.")

        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        # ---- DRAIN: every slice to its end through the shared per-ref cage path.
        slice_page_cap = max_pages_per_slice if max_pages_per_slice else MAX_PAGES_PER_SLICE
        for i, slc in enumerate(slices, 1):
            caged_before = stats["cars_caged"]
            clean, perr, phttp = await _drain_slice(
                conn, geo, platform_ulid, fetcher, governed_fetch, slc,
                seen_ids, harvested_cageable, stats,
                concurrency=concurrency, max_pages=slice_page_cap)
            # Attribute this slice's caged delta to its segment (distinct cars; cross-segment
            # dups already collapsed by the global seen_ids, so this is non-double-counting).
            seg_row = stats["per_segment"].get(slc["segment"])
            if seg_row is not None:
                seg_row["caged"] += stats["cars_caged"] - caged_before
            if clean:
                stats["slices_clean"] += 1
            else:
                stats["slices_errored"] += 1
                fetch_error = perr or fetch_error
                last_http = phttp if phttp is not None else last_http
            elapsed = time.monotonic() - t0
            cpm = stats["cars_caged"] / (elapsed / 60) if elapsed > 0 else 0.0
            label = f"{slc['segment']}:" + slc["make"] + (
                f"/{slc['province']}" if slc["province"] else "")
            print(f"[autocasion_facet] [{i}/{len(slices)}] {label:<32} "
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

        seg_keys = [s.key for s in segments]
        recipe = dict(AC_PLATFORM_RECIPE)
        recipe["scope"] = (
            f"platform-facet, segments={seg_keys} (URL-path make partition per segment; "
            "make×province for any >10k make — uncapped surface past ES max_result_window=10000)")
        recipe["segments"] = {
            s.key: {"label": s.label, "make_facet": s.make_path,
                    "province_facet": s.prov_path} for s in segments}
        recipe["enumeration"] = (
            "FACET partitions PER SEGMENT: brands(type:CAR) make slugs sized by each "
            "segment's SSR <title>; any make slice >"
            f"{SPLIT_THRESHOLD} split by province; each slice drained "
            "GET {segment_make_facet}[/{province}]?page=1..N to first 0-ref page. "
            "Segments: vo=/coches-segunda-mano/{make}-ocasion, vn=/coches-nuevos/{make}, "
            "km0=/coches-km0/{make}-km0. seen_ids dedups cross-page+cross-slice+cross-segment.")
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
    print(f"  segments requested    : {stats.get('segments_requested')}"
          + (f"  (non-existent: {stats.get('segments_nonexistent')})"
             if stats.get('segments_nonexistent') else ""))
    per_seg = stats.get("per_segment") or {}
    if per_seg:
        print("  --- per-segment plan + drain ---")
        for key, row in per_seg.items():
            print(f"    [{key:<4}] {row.get('label','')[:24]:<24} "
                  f"makes_w_stock={row.get('makes_with_stock'):>3} "
                  f"slices={row.get('slices'):>3} declared={row.get('declared'):>7} "
                  f"caged={row.get('caged'):>7}"
                  + (f" split={row.get('split_makes')}" if row.get('split_makes') else ""))
    print("  --- coverage proof (capture-recapture) ---")
    print(f"  makes (total/w-stock) : {stats.get('makes_total')} / {stats.get('makes_with_stock')}")
    print(f"  slices drained        : {stats.get('slices')} "
          f"({stats.get('slices_clean')} clean / {stats.get('slices_errored')} errored)")
    print(f"  sum(slice declared)   : {stats.get('coverage_sum')}  (declared full this run, all segments)")
    print("  --- drain ---")
    print(f"  hydrate concurrency   : {stats.get('concurrency')} refs in flight per page")
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
    # Windows consoles default to cp1252; force UTF-8 on stdout/stderr so the report's
    # em-dash and accented dealer/city names in error lines never crash the run.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):  # pragma: no cover — non-reconfigurable stream
            pass
    parser = argparse.ArgumentParser(
        description="autocasion FACET-PARTITION harvester (per-segment make-partition drain to 100%)")
    parser.add_argument("--segment", type=str, default=None, metavar="SEG",
                        help="segment(s) to drain: all | vo | vn | km0 (comma-list ok, e.g. "
                             "vn,km0). 'all' = vo+vn+km0 (every sellable segment). 'catalog' "
                             "is an alias of vn (the new-car catalog). 'renting' is accepted "
                             "but reported as non-existent on autocasion. Omit = vo (back-compat).")
    parser.add_argument("--make", action="append", default=None, metavar="SLUG",
                        help="drain only this make slug (repeatable: --make seat --make audi). "
                             "Omit to enumerate all makes. Applies within the chosen segment(s).")
    parser.add_argument("--makes", type=str, default=None,
                        help="'all' = the FULL uncapped drain (every make slice, one command). "
                             "Equivalent to omitting --make/--max-makes.")
    parser.add_argument("--max-makes", type=int, default=None,
                        help="bounded proof: drain only the N LARGEST slices by declared size "
                             "(several complete slices end to end). Omit for the full drain.")
    parser.add_argument("--concurrency", type=int, default=HYDRATE_CONCURRENCY,
                        help=(f"per-page hydration concurrency (refs hydrated in flight); "
                              f"default {HYDRATE_CONCURRENCY}. The governor's per-host bucket "
                              f"is the real limiter — this only keeps the bucket saturated."))
    parser.add_argument("--max-pages-per-slice", type=int, default=None,
                        help="BOUNDED test: hard cap on SSR pages drained PER slice (~26 cars/"
                             "page). Omit to drain each slice to its natural 0-ref end.")
    args = parser.parse_args()

    make_filter: list[str] | None = None
    if args.make:
        make_filter = list(args.make)
    elif args.makes and args.makes.lower() != "all":
        make_filter = [s.strip() for s in args.makes.split(",") if s.strip()]

    segments, nonexistent = resolve_segments(args.segment)
    if not segments and nonexistent:
        print(f"[autocasion_facet] only non-existent segment(s) requested ({nonexistent}); "
              f"nothing to drain on autocasion.")
    stats = asyncio.run(harvest_facet(
        make_filter=make_filter, max_makes=args.max_makes,
        segments=segments, nonexistent=nonexistent,
        concurrency=args.concurrency,
        max_pages_per_slice=args.max_pages_per_slice))
    _print_report(stats)


if __name__ == "__main__":
    main()
