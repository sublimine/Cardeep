"""F2 (01-market-intelligence) — M3/M4/M5/M7/M9/M10 fetch functions.

Each ``fetch_m*`` follows the SAME shape as F1's ``fetch_m1``: returns
``(list[SegmentStat], n_in)`` where n_in is the universe size feeding that metric
(NOT necessarily the same universe as M1 — M3/M5/M7/M9 draw from ``vehicle_event``,
whose population is disjoint from M1's snapshot-of-available-stock population).

Design notes (declared, not hidden):

- **Segmentation**: make + model + a sliding ±1-year band (anchor year, see
  ``pipeline/market/cohort.py`` YEAR_BAND_RADIUS) + fuel + province_code, with a
  province_code=NULL national fallback row — IDENTICAL segmentation to M1, for one
  join key vocabulary across every metric a dealer might compare side by side.
- **M4/M9 reuse M1's `n`** (the already-verified available-canonical count per
  segment) as their population denominator instead of re-deriving it — one fewer
  independent (and potentially divergent) computation of "how many cars are
  available in this segment", and it saves re-paying the ~110s availability scan.
  Passed in explicitly as ``m1_rows``.
- **Windows are dynamic** (``cohort.effective_window_days`` / ``m7_half_window_days``)
  — F0's gate (real span 35d < 90/45/30d nominal) is resolved HERE, at call time,
  never hardcoded.
- **M7's "price momentum"** compares the entry price (``vehicle_event`` NEW row's
  ``new_value->>'price'``, i.e. the price AS FIRST ANNOUNCED) of cars whose NEW event
  falls in the early half of the observed span vs the late half — NOT a live
  point-in-time market snapshot (the system does not have historical inventory
  snapshots, only an event log). This is declared explicitly, not silently assumed:
  see the module docstring of ``fetch_m7``.
- **Known duplicate scan cost** (declared trade-off, not an oversight): each fetch_m*
  re-derives its own ``canon``/``servable_vehicle`` CTEs rather than sharing a
  pre-built temp table with F1's ``fetch_m1`` — refactoring F1's already-verified
  query to share a temp table was assessed as a regression risk not worth the ~110s
  of batch-job runtime it would save (this is a nightly job, not a request path).

BUG FOUND AND FIXED DURING F2 PRODUCTION VERIFICATION (2026-07-17): the FIRST
production run of this module wrote ZERO M7 rows. Root cause traced (not papered
over): the strict canon CTE (``WHERE vc.vehicle_ulid = vc.canonical_vehicle_ulid``,
copied from F1's M1 for consistency) silently excludes every vehicle NEVER touched
by the ``vehicle_cluster`` resolver — 408,155 vehicles (15.3% of the fleet),
391,646 of them ingested AFTER the last ``vam_verified`` run (2026-06-22). M7's
"late half" window is, by construction, the most recent ~17 days — entirely AFTER
that run — so 100% of its candidate NEW events were invisible (verified: 126,341
raw NEW-with-price events in that window, 0 after the strict canon join). M3/M4/
M5/M9 shared the same join and were partially blind to recent GONE/PRICE_CHANGE
activity for the same reason, understating rotation/pressure signals without ever
producing a visible error.

Fix: metrics reading `vehicle_event` for RECENT activity (M3, M4's GONE count, M5's
GONE count, M7, M9) now use ``_COALESCE_CANON_CTE`` below — the canonical
representative of a KNOWN cluster (unchanged) UNION a vehicle that has NEVER been
clustered at all (added back as its own canonical). This mirrors the exact fix
already proven in ``services/api/routers/entities.py:74`` for the identical bug
class ("a vehicle absent from v_canonical_vehicle is its own canonical and MUST be
counted"). M1 and M10 (snapshot-of-available-stock metrics, not recent-window
metrics) deliberately KEEP the strict definition — see ``_STRICT_CANON_CTE`` —
matching 01-market-intelligence-f0.md §9's explicit recommendation for that
metric shape, already shipped and cross-verified in F1. The residual staleness of
the cluster resolver itself (growing daily until it is re-run) is an operational
dependency of a DIFFERENT subsystem, flagged here, not fixed by this pilar.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import asyncpg

from pipeline.market.cohort import (
    M7_NOMINAL_HALF_DAYS,
    MIN_COHORT_N,
    NOMINAL_WINDOW_DAYS_M3,
    NOMINAL_WINDOW_DAYS_M4,
    NOMINAL_WINDOW_DAYS_M5,
    NOMINAL_WINDOW_DAYS_M9,
    SegmentStat,
    YEAR_BAND_RADIUS,
    effective_window_days,
    get_span_days,
    m7_half_window_days,
)

_STRICT_CANON_CTE = """
    canon AS (
        SELECT vc.canonical_vehicle_ulid AS vehicle_ulid
          FROM v_canonical_vehicle vc
         WHERE vc.vehicle_ulid = vc.canonical_vehicle_ulid
    )
"""

# Used ONLY by M10 (snapshot-of-available-stock, same shape as M1) — kept identical
# to F1's already-verified universe. NOT used by the recent-activity metrics below
# (see the bug note in the module docstring).
_CANON_CTE = _STRICT_CANON_CTE

# active_run + coalesce canon: self-canonical member of the verified cluster run,
# UNION a vehicle that has NEVER been touched by ANY cluster run at all (added back
# as its own canonical so recent activity on brand-new inventory is never silently
# invisible). See module docstring for the bug this closes.
_COALESCE_CANON_CTE = """
    active_run AS (
        SELECT cluster_run_id FROM vehicle_cluster_run
         WHERE vam_verified = TRUE ORDER BY run_at DESC LIMIT 1
    ),
    canon AS (
        SELECT vc.canonical_vehicle_ulid AS vehicle_ulid
          FROM vehicle_cluster vc, active_run ar
         WHERE vc.cluster_run_id = ar.cluster_run_id
           AND vc.vehicle_ulid = vc.canonical_vehicle_ulid
        UNION ALL
        SELECT v.vehicle_ulid
          FROM vehicle v, active_run ar
         WHERE NOT EXISTS (
                   SELECT 1 FROM vehicle_cluster vc2
                    WHERE vc2.cluster_run_id = ar.cluster_run_id
                      AND vc2.vehicle_ulid = v.vehicle_ulid
               )
    )
"""

# M5 needs BOTH definitions in the SAME query (avail_by_prov is a snapshot, like M1;
# gone_by_prov is recent-activity, like M3/M4/M7/M9) — distinct CTE names so they can
# coexist in one WITH clause.
_M5_DUAL_CANON_CTE = """
    active_run AS (
        SELECT cluster_run_id FROM vehicle_cluster_run
         WHERE vam_verified = TRUE ORDER BY run_at DESC LIMIT 1
    ),
    canon_strict AS (
        SELECT vc.canonical_vehicle_ulid AS vehicle_ulid
          FROM v_canonical_vehicle vc
         WHERE vc.vehicle_ulid = vc.canonical_vehicle_ulid
    ),
    canon_coalesce AS (
        SELECT vc.canonical_vehicle_ulid AS vehicle_ulid
          FROM vehicle_cluster vc, active_run ar
         WHERE vc.cluster_run_id = ar.cluster_run_id
           AND vc.vehicle_ulid = vc.canonical_vehicle_ulid
        UNION ALL
        SELECT v.vehicle_ulid
          FROM vehicle v, active_run ar
         WHERE NOT EXISTS (
                   SELECT 1 FROM vehicle_cluster vc2
                    WHERE vc2.cluster_run_id = ar.cluster_run_id
                      AND vc2.vehicle_ulid = v.vehicle_ulid
               )
    )
"""


def _m1_index(m1_rows) -> dict[tuple, Any]:
    """Index F1's M1Row list by segment key for O(1) lookup from F2 metrics."""
    return {
        (r.scope, r.make, r.model, r.fuel, r.province_code, r.year): r
        for r in m1_rows
    }


# ---------------------------------------------------------------------------
# M3 — median days-to-retirada (rotation) by segment
# ---------------------------------------------------------------------------

_M3_SQL = f"""
WITH {_COALESCE_CANON_CTE},
gone AS (
    SELECT v.make, v.model, v.year, v.fuel, e.province_code,
           EXTRACT(EPOCH FROM (ve.observed_at - v.first_seen)) / 86400.0 AS days_to_removal
      FROM vehicle_event ve
      JOIN canon c ON c.vehicle_ulid = ve.vehicle_ulid
      JOIN vehicle v ON v.vehicle_ulid = ve.vehicle_ulid
      JOIN entity e ON e.entity_ulid = ve.entity_ulid
     WHERE ve.event_type = 'GONE'
       AND ve.observed_at >= now() - ($3::float8 * INTERVAL '1 day')
       AND ve.observed_at >= v.first_seen
       AND v.make IS NOT NULL AND v.model IS NOT NULL AND v.year IS NOT NULL AND v.fuel IS NOT NULL
       AND e.province_code IS NOT NULL
       AND ($4::text[] IS NULL OR v.make = ANY($4::text[]))
),
universe_count AS (SELECT count(*) AS n_in FROM gone),
prov_years AS (SELECT DISTINCT make, model, fuel, province_code, year AS anchor_year FROM gone),
prov_cohort AS (
    SELECT py.make, py.model, py.fuel, py.province_code, py.anchor_year, g.days_to_removal
      FROM prov_years py
      JOIN gone g ON g.make = py.make AND g.model = py.model AND g.fuel = py.fuel
                 AND g.province_code = py.province_code
                 AND g.year BETWEEN py.anchor_year - $2 AND py.anchor_year + $2
),
prov_stats AS (
    SELECT make, model, fuel, province_code, anchor_year AS year, count(*) AS n,
           percentile_cont(0.5) WITHIN GROUP (ORDER BY days_to_removal) AS median_days
      FROM prov_cohort
     GROUP BY make, model, fuel, province_code, anchor_year
    HAVING count(*) >= $1
),
nat_years AS (SELECT DISTINCT make, model, fuel, year AS anchor_year FROM gone),
nat_cohort AS (
    SELECT ny.make, ny.model, ny.fuel, ny.anchor_year, g.days_to_removal
      FROM nat_years ny
      JOIN gone g ON g.make = ny.make AND g.model = ny.model AND g.fuel = ny.fuel
                 AND g.year BETWEEN ny.anchor_year - $2 AND ny.anchor_year + $2
),
nat_stats AS (
    SELECT make, model, fuel, anchor_year AS year, count(*) AS n,
           percentile_cont(0.5) WITHIN GROUP (ORDER BY days_to_removal) AS median_days
      FROM nat_cohort
     GROUP BY make, model, fuel, anchor_year
    HAVING count(*) >= $1
)
SELECT 'prov'::text AS scope, make, model, fuel, province_code, year, n, median_days FROM prov_stats
UNION ALL
SELECT 'nat'::text AS scope, make, model, fuel, NULL::varchar, year, n, median_days FROM nat_stats
UNION ALL
SELECT 'meta'::text AS scope, NULL, NULL, NULL, NULL, NULL, n_in, NULL FROM universe_count
"""


async def fetch_m3(
    conn: asyncpg.Connection, *, span_days: float | None = None, make_filter: list[str] | None = None
) -> tuple[list[SegmentStat], int, float]:
    """M3: median (GONE.observed_at - vehicle.first_seen) per segment.

    Returns (rows, n_in, window_days_used). Window = effective_window_days(90, span).
    """
    if span_days is None:
        span_days = await get_span_days(conn)
    window = effective_window_days(NOMINAL_WINDOW_DAYS_M3, span_days)

    rows = await conn.fetch(_M3_SQL, MIN_COHORT_N, YEAR_BAND_RADIUS, window, make_filter)
    out: list[SegmentStat] = []
    n_in = 0
    for r in rows:
        if r["scope"] == "meta":
            n_in = int(r["n"])
            continue
        out.append(SegmentStat(
            scope=r["scope"], make=r["make"], model=r["model"], fuel=r["fuel"],
            province_code=r["province_code"], year=int(r["year"]), n=int(r["n"]),
            value_num=float(r["median_days"]),
            value_extra={"window_days": window, "unit": "days_to_listing_removal"},
        ))
    return out, n_in, window


# ---------------------------------------------------------------------------
# M4 — Market Days Supply: available_n / (gone_n_in_window / window_days)
# ---------------------------------------------------------------------------

_M4_GONE_SQL = f"""
WITH {_COALESCE_CANON_CTE},
gone AS (
    SELECT v.make, v.model, v.year, v.fuel, e.province_code
      FROM vehicle_event ve
      JOIN canon c ON c.vehicle_ulid = ve.vehicle_ulid
      JOIN vehicle v ON v.vehicle_ulid = ve.vehicle_ulid
      JOIN entity e ON e.entity_ulid = ve.entity_ulid
     WHERE ve.event_type = 'GONE'
       AND ve.observed_at >= now() - ($2::float8 * INTERVAL '1 day')
       AND v.make IS NOT NULL AND v.model IS NOT NULL AND v.year IS NOT NULL AND v.fuel IS NOT NULL
       AND e.province_code IS NOT NULL
       AND ($3::text[] IS NULL OR v.make = ANY($3::text[]))
),
prov_years AS (SELECT DISTINCT make, model, fuel, province_code, year AS anchor_year FROM gone),
prov_cohort AS (
    SELECT py.make, py.model, py.fuel, py.province_code, py.anchor_year
      FROM prov_years py
      JOIN gone g ON g.make = py.make AND g.model = py.model AND g.fuel = py.fuel
                 AND g.province_code = py.province_code
                 AND g.year BETWEEN py.anchor_year - $1 AND py.anchor_year + $1
),
prov_gone AS (
    SELECT make, model, fuel, province_code, anchor_year AS year, count(*) AS gone_n
      FROM prov_cohort GROUP BY make, model, fuel, province_code, anchor_year
),
nat_years AS (SELECT DISTINCT make, model, fuel, year AS anchor_year FROM gone),
nat_cohort AS (
    SELECT ny.make, ny.model, ny.fuel, ny.anchor_year
      FROM nat_years ny
      JOIN gone g ON g.make = ny.make AND g.model = ny.model AND g.fuel = ny.fuel
                 AND g.year BETWEEN ny.anchor_year - $1 AND ny.anchor_year + $1
),
nat_gone AS (
    SELECT make, model, fuel, anchor_year AS year, count(*) AS gone_n
      FROM nat_cohort GROUP BY make, model, fuel, anchor_year
)
SELECT 'prov'::text AS scope, make, model, fuel, province_code, year, gone_n FROM prov_gone
UNION ALL
SELECT 'nat'::text AS scope, make, model, fuel, NULL::varchar, year, gone_n FROM nat_gone
"""


async def fetch_m4(
    conn: asyncpg.Connection,
    m1_rows: list,
    *,
    span_days: float | None = None,
    make_filter: list[str] | None = None,
) -> tuple[list[SegmentStat], float]:
    """M4: Market Days Supply per M1 segment.

    ``available_n`` comes from ``m1_rows`` (F1's already-verified per-segment count),
    NOT re-derived here (see module docstring). GONE count in the effective window is
    fetched fresh. A segment with gone_n == 0 still WRITES a row (value_num=None,
    "no_rotation_observed") per the carta's explicit "no invented number, no division
    by zero" rule — this is NOT the same as the n<8 suppression (that omits the row
    entirely; here the row exists but honestly reports it has no signal).
    """
    if span_days is None:
        span_days = await get_span_days(conn)
    window = effective_window_days(NOMINAL_WINDOW_DAYS_M4, span_days)

    gone_rows = await conn.fetch(_M4_GONE_SQL, YEAR_BAND_RADIUS, window, make_filter)
    gone_index: dict[tuple, int] = {
        (r["scope"], r["make"], r["model"], r["fuel"], r["province_code"], int(r["year"])): int(r["gone_n"])
        for r in gone_rows
    }

    out: list[SegmentStat] = []
    for m1_row in m1_rows:
        key = (m1_row.scope, m1_row.make, m1_row.model, m1_row.fuel, m1_row.province_code, m1_row.year)
        gone_n = gone_index.get(key, 0)
        available_n = m1_row.n
        if gone_n == 0:
            out.append(SegmentStat(
                scope=m1_row.scope, make=m1_row.make, model=m1_row.model, fuel=m1_row.fuel,
                province_code=m1_row.province_code, year=m1_row.year, n=available_n,
                value_num=None,
                value_extra={"status": "no_rotation_observed", "gone_n": 0,
                             "available_n": available_n, "window_days": window},
            ))
        else:
            daily_rate = gone_n / window
            mds = available_n / daily_rate
            out.append(SegmentStat(
                scope=m1_row.scope, make=m1_row.make, model=m1_row.model, fuel=m1_row.fuel,
                province_code=m1_row.province_code, year=m1_row.year, n=available_n,
                value_num=mds,
                value_extra={"gone_n": gone_n, "available_n": available_n, "window_days": window},
            ))
    return out, window


# ---------------------------------------------------------------------------
# M5 — provincial absorption rate: GONE(30d)/available, no make/model dimension
# ---------------------------------------------------------------------------

_M5_SQL = f"""
WITH {_M5_DUAL_CANON_CTE},
avail_by_prov AS (
    SELECT e.province_code, count(*) AS n_avail
      FROM canon_strict c
      JOIN servable_vehicle v ON v.vehicle_ulid = c.vehicle_ulid
      JOIN entity e ON e.entity_ulid = v.entity_ulid
     WHERE e.province_code IS NOT NULL
       AND ($2::text[] IS NULL OR v.make = ANY($2::text[]))
     GROUP BY e.province_code
),
gone_by_prov AS (
    SELECT e.province_code, count(*) AS n_gone
      FROM vehicle_event ve
      JOIN canon_coalesce c ON c.vehicle_ulid = ve.vehicle_ulid
      JOIN vehicle v ON v.vehicle_ulid = ve.vehicle_ulid
      JOIN entity e ON e.entity_ulid = ve.entity_ulid
     WHERE ve.event_type = 'GONE'
       AND ve.observed_at >= now() - ($1::float8 * INTERVAL '1 day')
       AND e.province_code IS NOT NULL
       AND ($2::text[] IS NULL OR v.make = ANY($2::text[]))
     GROUP BY e.province_code
)
SELECT a.province_code, a.n_avail, COALESCE(g.n_gone, 0) AS n_gone
  FROM avail_by_prov a
  LEFT JOIN gone_by_prov g ON g.province_code = a.province_code
"""


async def fetch_m5(
    conn: asyncpg.Connection, *, span_days: float | None = None, make_filter: list[str] | None = None
) -> tuple[list[SegmentStat], int, float]:
    """M5: absorption rate = GONE(window)/available, per province. No make/model axis.

    n<MIN_COHORT_N on the AVAILABLE side suppresses the province row (an anti-noise
    floor consistent with every other metric — a province with a handful of cars
    should not rank in a demand table).
    """
    if span_days is None:
        span_days = await get_span_days(conn)
    window = effective_window_days(NOMINAL_WINDOW_DAYS_M5, span_days)

    rows = await conn.fetch(_M5_SQL, window, make_filter)
    out: list[SegmentStat] = []
    n_in = 0
    for r in rows:
        n_avail = int(r["n_avail"])
        n_in += n_avail
        if n_avail < MIN_COHORT_N:
            continue
        n_gone = int(r["n_gone"])
        absorption = n_gone / n_avail
        out.append(SegmentStat(
            scope="prov", make=None, model=None, fuel=None,
            province_code=r["province_code"], year=None, n=n_avail,
            value_num=absorption,
            value_extra={"n_gone": n_gone, "n_avail": n_avail, "window_days": window},
        ))
    return out, n_in, window


# ---------------------------------------------------------------------------
# M7 — price momentum: entry-price p50 of early half vs late half of the observed span
# ---------------------------------------------------------------------------

_M7_HALF_SQL = f"""
WITH {_COALESCE_CANON_CTE},
entries AS (
    SELECT v.make, v.model, v.year, v.fuel, e.province_code,
           (ve.new_value ->> 'price')::float8 AS entry_price
      FROM vehicle_event ve
      JOIN canon c ON c.vehicle_ulid = ve.vehicle_ulid
      JOIN vehicle v ON v.vehicle_ulid = ve.vehicle_ulid
      JOIN entity e ON e.entity_ulid = ve.entity_ulid
     WHERE ve.event_type = 'NEW'
       AND ve.new_value ? 'price' AND (ve.new_value ->> 'price') IS NOT NULL
       AND ve.observed_at >= $4::timestamptz AND ve.observed_at < $5::timestamptz
       AND v.make IS NOT NULL AND v.model IS NOT NULL AND v.year IS NOT NULL AND v.fuel IS NOT NULL
       AND e.province_code IS NOT NULL
       AND ($3::text[] IS NULL OR v.make = ANY($3::text[]))
),
prov_years AS (SELECT DISTINCT make, model, fuel, province_code, year AS anchor_year FROM entries),
prov_cohort AS (
    SELECT py.make, py.model, py.fuel, py.province_code, py.anchor_year, e2.entry_price
      FROM prov_years py
      JOIN entries e2 ON e2.make = py.make AND e2.model = py.model AND e2.fuel = py.fuel
                     AND e2.province_code = py.province_code
                     AND e2.year BETWEEN py.anchor_year - $2 AND py.anchor_year + $2
),
prov_stats AS (
    SELECT make, model, fuel, province_code, anchor_year AS year, count(*) AS n,
           percentile_cont(0.5) WITHIN GROUP (ORDER BY entry_price) AS p50
      FROM prov_cohort
     GROUP BY make, model, fuel, province_code, anchor_year
    HAVING count(*) >= $1
),
nat_years AS (SELECT DISTINCT make, model, fuel, year AS anchor_year FROM entries),
nat_cohort AS (
    SELECT ny.make, ny.model, ny.fuel, ny.anchor_year, e2.entry_price
      FROM nat_years ny
      JOIN entries e2 ON e2.make = ny.make AND e2.model = ny.model AND e2.fuel = ny.fuel
                     AND e2.year BETWEEN ny.anchor_year - $2 AND ny.anchor_year + $2
),
nat_stats AS (
    SELECT make, model, fuel, anchor_year AS year, count(*) AS n,
           percentile_cont(0.5) WITHIN GROUP (ORDER BY entry_price) AS p50
      FROM nat_cohort
     GROUP BY make, model, fuel, anchor_year
    HAVING count(*) >= $1
)
SELECT 'prov'::text AS scope, make, model, fuel, province_code, year, n, p50 FROM prov_stats
UNION ALL
SELECT 'nat'::text AS scope, make, model, fuel, NULL::varchar, year, n, p50 FROM nat_stats
"""


async def fetch_m7(
    conn: asyncpg.Connection, *, span_days: float | None = None, make_filter: list[str] | None = None
) -> tuple[list[SegmentStat], float]:
    """M7: momentum = (late.p50 - early.p50) / early.p50, entry price, per segment.

    DECLARED LIMITATION (not silently assumed): "entry price" is the price recorded on
    the vehicle_event NEW row (as first announced), NOT a live point-in-time market
    snapshot — this system has no historical inventory snapshot capability, only an
    append-only event log. A segment where NEITHER half clears MIN_COHORT_N is omitted
    entirely (never a fabricated momentum number) — see 01-market-intelligence-f0.md
    §3 gate resolution: "si el n resultante es insuficiente por partición, M7 se marca
    no disponible" — here realized as "the row is simply not written".
    """
    if span_days is None:
        span_days = await get_span_days(conn)
    half = m7_half_window_days(span_days)

    row = await conn.fetchrow("SELECT max(observed_at) AS mx FROM vehicle_event")
    now_anchor = row["mx"] if row and row["mx"] is not None else datetime.now(timezone.utc)
    mid = now_anchor - timedelta(days=half)
    early_start = now_anchor - timedelta(days=2 * half)

    # _M7_HALF_SQL's upper bound is exclusive ("< $5") so early/late never double-count a
    # row that lands exactly on `mid`. But `now_anchor` itself IS `MAX(observed_at)` from
    # the query above, and vehicle_event.observed_at defaults to Postgres now() (transaction
    # start time, migrations/0003_vehicles_events.sql) — every event written by the SAME
    # ingest transaction shares one identical timestamp. Passing `now_anchor` unmodified as
    # the late half's exclusive upper bound would therefore silently drop the single most
    # recent ingest batch from its own "late" window every time (found via the CI fixture's
    # tiny universe, where it zeroed out M7 entirely — but the same exclusion silently
    # under-counts the freshest batch in production too). Nudge by 1 microsecond (finer than
    # timestamptz's own resolution) so events observed exactly AT now_anchor are correctly
    # counted as "late" without touching the early/mid boundary at all.
    late_upper = now_anchor + timedelta(microseconds=1)

    early_rows = await conn.fetch(
        _M7_HALF_SQL, MIN_COHORT_N, YEAR_BAND_RADIUS, make_filter, early_start, mid
    )
    late_rows = await conn.fetch(
        _M7_HALF_SQL, MIN_COHORT_N, YEAR_BAND_RADIUS, make_filter, mid, late_upper
    )

    def _index(rows):
        return {
            (r["scope"], r["make"], r["model"], r["fuel"], r["province_code"], int(r["year"])): r
            for r in rows
        }

    early_idx = _index(early_rows)
    late_idx = _index(late_rows)

    out: list[SegmentStat] = []
    for key, late_r in late_idx.items():
        early_r = early_idx.get(key)
        if early_r is None:
            continue  # early half didn't clear MIN_COHORT_N -> no momentum number
        early_p50 = float(early_r["p50"])
        late_p50 = float(late_r["p50"])
        if early_p50 == 0:
            continue
        delta_pct = (late_p50 - early_p50) / early_p50 * 100.0
        scope, make, model, fuel, province_code, year = key
        out.append(SegmentStat(
            scope=scope, make=make, model=model, fuel=fuel, province_code=province_code,
            year=year, n=min(int(early_r["n"]), int(late_r["n"])),
            value_num=delta_pct,
            value_extra={
                "p50_early": early_p50, "p50_late": late_p50,
                "n_early": int(early_r["n"]), "n_late": int(late_r["n"]),
                "half_window_days": half,
            },
        ))
    return out, half


# ---------------------------------------------------------------------------
# M9 — seller price-pressure: % of available units with >=1 net price cut in window
# ---------------------------------------------------------------------------

_M9_SQL = f"""
WITH {_COALESCE_CANON_CTE},
changes AS (
    SELECT ve.vehicle_ulid, v.make, v.model, v.year, v.fuel, e.province_code, ve.observed_at,
           (ve.old_value ->> 'price')::float8 AS old_price,
           (ve.new_value ->> 'price')::float8 AS new_price
      FROM vehicle_event ve
      JOIN canon c ON c.vehicle_ulid = ve.vehicle_ulid
      JOIN vehicle v ON v.vehicle_ulid = ve.vehicle_ulid
      JOIN entity e ON e.entity_ulid = ve.entity_ulid
     WHERE ve.event_type = 'PRICE_CHANGE'
       AND v.status = 'available'
       AND ve.observed_at >= now() - ($2::float8 * INTERVAL '1 day')
       AND ve.old_value ? 'price' AND ve.new_value ? 'price'
       AND (ve.old_value ->> 'price') IS NOT NULL AND (ve.new_value ->> 'price') IS NOT NULL
       AND v.make IS NOT NULL AND v.model IS NOT NULL AND v.year IS NOT NULL AND v.fuel IS NOT NULL
       AND e.province_code IS NOT NULL
       AND ($3::text[] IS NULL OR v.make = ANY($3::text[]))
),
per_vehicle AS (
    SELECT vehicle_ulid, make, model, year, fuel, province_code,
           (array_agg(old_price ORDER BY observed_at ASC))[1]  AS first_old,
           (array_agg(new_price ORDER BY observed_at DESC))[1] AS last_new
      FROM changes
     GROUP BY vehicle_ulid, make, model, year, fuel, province_code
),
cut_vehicles AS (
    SELECT make, model, year, fuel, province_code,
           (first_old - last_new) / NULLIF(first_old, 0) AS cut_frac
      FROM per_vehicle
     WHERE first_old > 0 AND last_new < first_old
),
prov_years AS (SELECT DISTINCT make, model, fuel, province_code, year AS anchor_year FROM cut_vehicles),
prov_cohort AS (
    SELECT py.make, py.model, py.fuel, py.province_code, py.anchor_year, cv.cut_frac
      FROM prov_years py
      JOIN cut_vehicles cv ON cv.make = py.make AND cv.model = py.model AND cv.fuel = py.fuel
                          AND cv.province_code = py.province_code
                          AND cv.year BETWEEN py.anchor_year - $1 AND py.anchor_year + $1
),
prov_cuts AS (
    SELECT make, model, fuel, province_code, anchor_year AS year, count(*) AS n_cut,
           percentile_cont(0.5) WITHIN GROUP (ORDER BY cut_frac) AS median_cut
      FROM prov_cohort
     GROUP BY make, model, fuel, province_code, anchor_year
),
nat_years AS (SELECT DISTINCT make, model, fuel, year AS anchor_year FROM cut_vehicles),
nat_cohort AS (
    SELECT ny.make, ny.model, ny.fuel, ny.anchor_year, cv.cut_frac
      FROM nat_years ny
      JOIN cut_vehicles cv ON cv.make = ny.make AND cv.model = ny.model AND cv.fuel = ny.fuel
                          AND cv.year BETWEEN ny.anchor_year - $1 AND ny.anchor_year + $1
),
nat_cuts AS (
    SELECT make, model, fuel, anchor_year AS year, count(*) AS n_cut,
           percentile_cont(0.5) WITHIN GROUP (ORDER BY cut_frac) AS median_cut
      FROM nat_cohort
     GROUP BY make, model, fuel, anchor_year
)
SELECT 'prov'::text AS scope, make, model, fuel, province_code, year, n_cut, median_cut FROM prov_cuts
UNION ALL
SELECT 'nat'::text AS scope, make, model, fuel, NULL::varchar, year, n_cut, median_cut FROM nat_cuts
"""


async def fetch_m9(
    conn: asyncpg.Connection,
    m1_rows: list,
    *,
    span_days: float | None = None,
    make_filter: list[str] | None = None,
) -> tuple[list[SegmentStat], float]:
    """M9: % of available units (per M1 segment) with >=1 NET price cut in the window,
    plus the median accumulated cut fraction among those cut. Population (denominator)
    is M1's `n` — same reuse rationale as M4."""
    if span_days is None:
        span_days = await get_span_days(conn)
    window = effective_window_days(NOMINAL_WINDOW_DAYS_M9, span_days)

    cut_rows = await conn.fetch(_M9_SQL, YEAR_BAND_RADIUS, window, make_filter)
    cut_index = {
        (r["scope"], r["make"], r["model"], r["fuel"], r["province_code"], int(r["year"])): r
        for r in cut_rows
    }

    out: list[SegmentStat] = []
    for m1_row in m1_rows:
        key = (m1_row.scope, m1_row.make, m1_row.model, m1_row.fuel, m1_row.province_code, m1_row.year)
        cut_r = cut_index.get(key)
        n_cut = int(cut_r["n_cut"]) if cut_r else 0
        pct_with_cut = (n_cut / m1_row.n) * 100.0
        median_cut_pct = float(cut_r["median_cut"]) * 100.0 if cut_r else None
        out.append(SegmentStat(
            scope=m1_row.scope, make=m1_row.make, model=m1_row.model, fuel=m1_row.fuel,
            province_code=m1_row.province_code, year=m1_row.year, n=m1_row.n,
            value_num=pct_with_cut,
            value_extra={"n_cut": n_cut, "available_n": m1_row.n,
                         "median_cut_pct": median_cut_pct, "window_days": window},
        ))
    return out, window


# ---------------------------------------------------------------------------
# M10 — multi-platform presence: distribution of COUNT(platform) per canonical unit
# ---------------------------------------------------------------------------

_M10_SQL = f"""
WITH {_CANON_CTE},
cluster_members AS (
    SELECT vehicle_ulid, canonical_vehicle_ulid
      FROM vehicle_cluster
     WHERE cluster_run_id = (
         SELECT cluster_run_id FROM vehicle_cluster_run
          WHERE vam_verified = TRUE ORDER BY run_at DESC LIMIT 1
     )
),
platform_counts AS (
    SELECT cm.canonical_vehicle_ulid AS vehicle_ulid, count(DISTINCT pl.platform_entity_ulid) AS n_platforms
      FROM cluster_members cm
      JOIN platform_listing pl ON pl.vehicle_ulid = cm.vehicle_ulid
     GROUP BY cm.canonical_vehicle_ulid
),
base AS (
    SELECT v.vehicle_ulid, v.make, v.model, v.year, v.fuel, e.province_code,
           COALESCE(pc.n_platforms, 0)::float8 AS n_platforms
      FROM canon c
      JOIN servable_vehicle v ON v.vehicle_ulid = c.vehicle_ulid
      JOIN entity e ON e.entity_ulid = v.entity_ulid
      LEFT JOIN platform_counts pc ON pc.vehicle_ulid = c.vehicle_ulid
     WHERE v.make IS NOT NULL AND v.model IS NOT NULL AND v.year IS NOT NULL AND v.fuel IS NOT NULL
       AND e.province_code IS NOT NULL
       AND ($3::text[] IS NULL OR v.make = ANY($3::text[]))
),
prov_years AS (SELECT DISTINCT make, model, fuel, province_code, year AS anchor_year FROM base),
prov_cohort AS (
    SELECT py.make, py.model, py.fuel, py.province_code, py.anchor_year, b.n_platforms
      FROM prov_years py
      JOIN base b ON b.make = py.make AND b.model = py.model AND b.fuel = py.fuel
                 AND b.province_code = py.province_code
                 AND b.year BETWEEN py.anchor_year - $2 AND py.anchor_year + $2
),
prov_stats AS (
    SELECT make, model, fuel, province_code, anchor_year AS year, count(*) AS n,
           percentile_cont(0.25) WITHIN GROUP (ORDER BY n_platforms) AS p25,
           percentile_cont(0.5)  WITHIN GROUP (ORDER BY n_platforms) AS p50,
           percentile_cont(0.75) WITHIN GROUP (ORDER BY n_platforms) AS p75
      FROM prov_cohort
     GROUP BY make, model, fuel, province_code, anchor_year
    HAVING count(*) >= $1
),
nat_years AS (SELECT DISTINCT make, model, fuel, year AS anchor_year FROM base),
nat_cohort AS (
    SELECT ny.make, ny.model, ny.fuel, ny.anchor_year, b.n_platforms
      FROM nat_years ny
      JOIN base b ON b.make = ny.make AND b.model = ny.model AND b.fuel = ny.fuel
                 AND b.year BETWEEN ny.anchor_year - $2 AND ny.anchor_year + $2
),
nat_stats AS (
    SELECT make, model, fuel, anchor_year AS year, count(*) AS n,
           percentile_cont(0.25) WITHIN GROUP (ORDER BY n_platforms) AS p25,
           percentile_cont(0.5)  WITHIN GROUP (ORDER BY n_platforms) AS p50,
           percentile_cont(0.75) WITHIN GROUP (ORDER BY n_platforms) AS p75
      FROM nat_cohort
     GROUP BY make, model, fuel, anchor_year
    HAVING count(*) >= $1
)
SELECT 'prov'::text AS scope, make, model, fuel, province_code, year, n, p25, p50, p75 FROM prov_stats
UNION ALL
SELECT 'nat'::text AS scope, make, model, fuel, NULL::varchar, year, n, p25, p50, p75 FROM nat_stats
"""


async def fetch_m10(
    conn: asyncpg.Connection, *, make_filter: list[str] | None = None
) -> list[SegmentStat]:
    """M10: distribution of platform-count per canonical unit, by segment.

    p25/p50/p75 here measure NUMBER OF PLATFORMS a physical car is listed on, NOT price
    (reusing the same three columns — declared, not a schema special-case; the unit is
    recorded in value_extra for any consumer that queries the raw table directly).
    """
    rows = await conn.fetch(_M10_SQL, MIN_COHORT_N, YEAR_BAND_RADIUS, make_filter)
    out: list[SegmentStat] = []
    for r in rows:
        out.append(SegmentStat(
            scope=r["scope"], make=r["make"], model=r["model"], fuel=r["fuel"],
            province_code=r["province_code"], year=int(r["year"]), n=int(r["n"]),
            p25=float(r["p25"]), p50=float(r["p50"]), p75=float(r["p75"]),
            value_extra={"unit": "platform_count"},
        ))
    return out
