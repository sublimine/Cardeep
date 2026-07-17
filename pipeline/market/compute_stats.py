"""compute_stats.py — market-intelligence batch job (CAMPAIGN 01-market-intelligence).

F1 scope: M1 (price distribution by segment) only. F2 extends this module with
M3/M4/M5/M7/M9/M10 in the SAME run (one job, one market_stat_run per execution,
carrying whichever metrics it computed in `metrics_computed`).

Universe (per 01-market-intelligence-f0.md §9, "recomendación: la estricta
v_canonical_vehicle JOIN"): exactly one row per physical vehicle — the canonical
representative of the single vam_verified cluster run (v_canonical_vehicle WHERE
vehicle_ulid = canonical_vehicle_ulid) — joined to servable_vehicle (available,
price-sane, not quarantined) and entity (province_code). This is deliberately the
STRICT definition, not the COALESCE-fallback used by entities.py:74 for per-dealer
serving; a market segment must never double-count a car that already has a verified
canonical representative elsewhere.

M1 segmentation (carta §4, row M1): make + model + a SLIDING +/-1 year band (anchor
year Y groups vehicle.year IN (Y-1, Y, Y+1) — see pipeline/market/cohort.py
YEAR_BAND_RADIUS) + fuel + province_code. Rows with n < MIN_COHORT_N are NEVER
written (the "muestra insuficiente" rule is enforced by SQL HAVING, not by a
post-hoc filter in Python — a row that fails the bar never exists to begin with).

National fallback (carta §6, item 1: "si n<8 en tu provincia, te enseñamos el dato
nacional"): the SAME job also computes a province_code=NULL row per
make+model+fuel+anchor_year, widening the cohort to the whole country. Both scopes
are computed in ONE SQL statement (a single materialized `base` CTE feeds both the
provincial and the national branch, so the ~110s cost of building the universe is
paid once, not twice).

Verification protocol (carta §7, row 1): the SQL path (percentile_cont in PG) is
PRIMARY. A SAMPLE of the largest-n computed segments is independently recomputed in
pure Python (pipeline/market/cohort.percentile_cont) from a fresh raw fetch of that
exact segment's rows, and compared with divergence tolerance <0.5%. The comparison
result is written into market_stat_run.checks (auditable, not just printed).

Publish gate: F1 NEVER sets published=TRUE (the criterion explicitly wants a
"run de prueba con published=FALSE"). F2 adds the +/-3% run-over-run gate + human
closure that flips it.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
from typing import Any, NamedTuple

import asyncpg

from pipeline.ids import ulid
from pipeline.market.cohort import (
    METHODOLOGY_VERSION,
    MIN_COHORT_N,
    YEAR_BAND_RADIUS,
    divergence_pct,
    percentile_cont,
)

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# Number of largest-n segments cross-checked SQL-vs-Python per run (carta F1 criterion:
# "recomputo Python vs SQL sobre 5 segmentos reales"). Kept as a module constant so F2's
# extension for the other metrics can reuse the same sample size without a magic number.
CROSSCHECK_SAMPLE_SIZE = 5

# Tolerance for the SQL-vs-Python divergence (carta §7 row 1: "<0.5% para percentiles").
CROSSCHECK_TOLERANCE_PCT = 0.5

WINDOW_DESCRIPTION_M1 = (
    "M1: snapshot vivo (sin ventana temporal — distribución de precio anunciado HOY sobre "
    f"stock canónico disponible; banda de año +/-{YEAR_BAND_RADIUS})"
)


class M1Row(NamedTuple):
    scope: str  # 'prov' | 'nat'
    make: str
    model: str
    fuel: str | None
    province_code: str | None
    year: int
    n: int
    p25: float
    p75: float
    p50: float


# ---------------------------------------------------------------------------
# M1 — price distribution by segment
# ---------------------------------------------------------------------------

_M1_SQL = """
WITH canon AS (
    SELECT vc.canonical_vehicle_ulid AS vehicle_ulid
      FROM v_canonical_vehicle vc
     WHERE vc.vehicle_ulid = vc.canonical_vehicle_ulid
),
base AS (
    SELECT v.vehicle_ulid, v.make, v.model, v.year, v.fuel, v.price::float8 AS price,
           e.province_code
      FROM canon c
      JOIN servable_vehicle v ON v.vehicle_ulid = c.vehicle_ulid
      JOIN entity e ON e.entity_ulid = v.entity_ulid
     WHERE v.price IS NOT NULL AND v.make IS NOT NULL AND v.model IS NOT NULL
       AND v.year IS NOT NULL AND v.fuel IS NOT NULL AND e.province_code IS NOT NULL
       AND ($3::text[] IS NULL OR v.make = ANY($3::text[]))
),
universe_count AS (
    SELECT count(*) AS n_in FROM base
),
prov_years AS (
    SELECT DISTINCT make, model, fuel, province_code, year AS anchor_year FROM base
),
prov_cohort AS (
    SELECT py.make, py.model, py.fuel, py.province_code, py.anchor_year, b.price
      FROM prov_years py
      JOIN base b
        ON b.make = py.make AND b.model = py.model AND b.fuel = py.fuel
       AND b.province_code = py.province_code
       AND b.year BETWEEN py.anchor_year - $2 AND py.anchor_year + $2
),
prov_stats AS (
    SELECT make, model, fuel, province_code, anchor_year AS year,
           count(*) AS n,
           percentile_cont(0.25) WITHIN GROUP (ORDER BY price) AS p25,
           percentile_cont(0.5)  WITHIN GROUP (ORDER BY price) AS p50,
           percentile_cont(0.75) WITHIN GROUP (ORDER BY price) AS p75
      FROM prov_cohort
     GROUP BY make, model, fuel, province_code, anchor_year
    HAVING count(*) >= $1
),
nat_years AS (
    SELECT DISTINCT make, model, fuel, year AS anchor_year FROM base
),
nat_cohort AS (
    SELECT ny.make, ny.model, ny.fuel, ny.anchor_year, b.price
      FROM nat_years ny
      JOIN base b
        ON b.make = ny.make AND b.model = ny.model AND b.fuel = ny.fuel
       AND b.year BETWEEN ny.anchor_year - $2 AND ny.anchor_year + $2
),
nat_stats AS (
    SELECT make, model, fuel, anchor_year AS year,
           count(*) AS n,
           percentile_cont(0.25) WITHIN GROUP (ORDER BY price) AS p25,
           percentile_cont(0.5)  WITHIN GROUP (ORDER BY price) AS p50,
           percentile_cont(0.75) WITHIN GROUP (ORDER BY price) AS p75
      FROM nat_cohort
     GROUP BY make, model, fuel, anchor_year
    HAVING count(*) >= $1
)
SELECT 'prov'::text AS scope, make, model, fuel, province_code, year,
       n, p25, p50, p75
  FROM prov_stats
UNION ALL
SELECT 'nat'::text AS scope, make, model, fuel, NULL::varchar AS province_code, year,
       n, p25, p50, p75
  FROM nat_stats
UNION ALL
SELECT 'meta'::text AS scope, NULL, NULL, NULL, NULL, NULL,
       n_in, NULL, NULL, NULL
  FROM universe_count
"""


async def fetch_m1(
    conn: asyncpg.Connection, make_filter: list[str] | None = None
) -> tuple[list[M1Row], int]:
    """Run the M1 SQL and split the result into (segment rows, universe n_in).

    The 'meta' row (see _M1_SQL) is always present (universe_count is a scalar CTE with
    exactly one row even when zero cohorts pass the n>=MIN_COHORT_N bar), so n_in is
    ALWAYS recoverable even in the degenerate all-suppressed case.

    ``make_filter``: None means the full national universe (production use). A
    non-empty list scopes the computation to those makes ONLY — used by the test suite
    to exercise the exact same SQL path against a synthetic slice in milliseconds
    instead of the full multi-minute national run; never used in production calls.
    """
    rows = await conn.fetch(_M1_SQL, MIN_COHORT_N, YEAR_BAND_RADIUS, make_filter)
    segment_rows: list[M1Row] = []
    n_in = 0
    for r in rows:
        if r["scope"] == "meta":
            n_in = int(r["n"])
            continue
        segment_rows.append(
            M1Row(
                scope=r["scope"],
                make=r["make"],
                model=r["model"],
                fuel=r["fuel"],
                province_code=r["province_code"],
                year=int(r["year"]),
                n=int(r["n"]),
                p25=float(r["p25"]),
                p50=float(r["p50"]),
                p75=float(r["p75"]),
            )
        )
    return segment_rows, n_in


async def crosscheck_m1(conn: asyncpg.Connection, rows: list[M1Row]) -> dict[str, Any]:
    """Independent Python recompute of the largest-n segments (carta §7 row 1).

    For each of the top-``CROSSCHECK_SAMPLE_SIZE`` rows by `n`, refetch the RAW price list
    for that exact segment (same filter conditions as `base`, same +/-year band, same
    scope) directly — bypassing the SQL percentile_cont path entirely — sort in pure
    Python, and recompute p25/p50/p75 via ``pipeline.market.cohort.percentile_cont``.
    Returns a JSON-serialisable dict written verbatim into market_stat_run.checks.
    """
    if not rows:
        return {"sampled": 0, "max_divergence_pct": 0.0, "segments": [], "tolerance_pct": CROSSCHECK_TOLERANCE_PCT}

    sample = sorted(rows, key=lambda r: r.n, reverse=True)[:CROSSCHECK_SAMPLE_SIZE]
    segments: list[dict[str, Any]] = []
    max_div = 0.0

    for row in sample:
        if row.scope == "prov":
            raw = await conn.fetch(
                """
                WITH canon AS (
                    SELECT vc.canonical_vehicle_ulid AS vehicle_ulid
                      FROM v_canonical_vehicle vc WHERE vc.vehicle_ulid = vc.canonical_vehicle_ulid
                )
                SELECT v.price::float8 AS price
                  FROM canon c
                  JOIN servable_vehicle v ON v.vehicle_ulid = c.vehicle_ulid
                  JOIN entity e ON e.entity_ulid = v.entity_ulid
                 WHERE v.make = $1 AND v.model = $2 AND v.fuel = $3 AND e.province_code = $4
                   AND v.year BETWEEN $5 AND $6 AND v.price IS NOT NULL
                """,
                row.make, row.model, row.fuel, row.province_code,
                row.year - YEAR_BAND_RADIUS, row.year + YEAR_BAND_RADIUS,
            )
        else:  # 'nat'
            raw = await conn.fetch(
                """
                WITH canon AS (
                    SELECT vc.canonical_vehicle_ulid AS vehicle_ulid
                      FROM v_canonical_vehicle vc WHERE vc.vehicle_ulid = vc.canonical_vehicle_ulid
                )
                SELECT v.price::float8 AS price
                  FROM canon c
                  JOIN servable_vehicle v ON v.vehicle_ulid = c.vehicle_ulid
                  JOIN entity e ON e.entity_ulid = v.entity_ulid
                 WHERE v.make = $1 AND v.model = $2 AND v.fuel = $3
                   AND v.year BETWEEN $4 AND $5 AND v.price IS NOT NULL
                   AND e.province_code IS NOT NULL
                """,
                row.make, row.model, row.fuel,
                row.year - YEAR_BAND_RADIUS, row.year + YEAR_BAND_RADIUS,
            )
        prices = sorted(float(r["price"]) for r in raw)
        py_n = len(prices)
        py_p25 = percentile_cont(prices, 0.25)
        py_p50 = percentile_cont(prices, 0.5)
        py_p75 = percentile_cont(prices, 0.75)

        div_n = divergence_pct(py_n, row.n)
        div_p25 = divergence_pct(py_p25, row.p25)
        div_p50 = divergence_pct(py_p50, row.p50)
        div_p75 = divergence_pct(py_p75, row.p75)
        seg_max = max(div_n, div_p25, div_p50, div_p75)
        max_div = max(max_div, seg_max)

        segments.append({
            "scope": row.scope, "make": row.make, "model": row.model, "fuel": row.fuel,
            "province_code": row.province_code, "year": row.year,
            "sql": {"n": row.n, "p25": row.p25, "p50": row.p50, "p75": row.p75},
            "python": {"n": py_n, "p25": py_p25, "p50": py_p50, "p75": py_p75},
            "divergence_pct": {"n": div_n, "p25": div_p25, "p50": div_p50, "p75": div_p75},
        })

    return {
        "sampled": len(segments),
        "max_divergence_pct": max_div,
        "tolerance_pct": CROSSCHECK_TOLERANCE_PCT,
        "passed": max_div < CROSSCHECK_TOLERANCE_PCT,
        "segments": segments,
    }


async def run_compute(
    conn: asyncpg.Connection, *, publish: bool = False, make_filter: list[str] | None = None
) -> str:
    """Execute one full compute_stats run: M1 -> market_stat_run + market_stat rows.

    Returns the new run_id. ``publish`` defaults to False (F1 criterion: "run de prueba
    con published=FALSE" — F2 is the one that adds the +/-3% gate deciding this).
    Raises RuntimeError if the SQL-vs-Python cross-check fails tolerance — an unverified
    run is NEVER written (doctrina antialucinación: no se escribe lo que no se pudo probar).
    ``make_filter``: test-only scoping, see ``fetch_m1``.
    """
    t0 = time.monotonic()
    rows, n_in = await fetch_m1(conn, make_filter)
    checks = await crosscheck_m1(conn, rows)
    elapsed = time.monotonic() - t0

    if not checks["passed"] and checks["sampled"] > 0:
        raise RuntimeError(
            f"compute_stats M1: SQL-vs-Python cross-check FAILED — "
            f"max divergence {checks['max_divergence_pct']:.4f}% >= tolerance "
            f"{CROSSCHECK_TOLERANCE_PCT}%. Run NOT written. Details: {checks}"
        )

    run_id = ulid()
    checks["elapsed_seconds"] = round(elapsed, 2)

    async with conn.transaction():
        await conn.execute(
            """
            INSERT INTO market_stat_run
                (run_id, methodology_version, window_description, n_in,
                 metrics_computed, checks, published, published_at, notes)
            VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7, $8, $9)
            """,
            run_id, METHODOLOGY_VERSION, WINDOW_DESCRIPTION_M1, n_in,
            ["M1"], _to_jsonb(checks), publish,
            None if not publish else _now_utc(), None,
        )
        if rows:
            await conn.executemany(
                """
                INSERT INTO market_stat
                    (run_id, metric_id, make, model, year, fuel, province_code,
                     n, p25, p50, p75)
                VALUES ($1, 'M1', $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                [
                    (run_id, r.make, r.model, r.year, r.fuel, r.province_code,
                     r.n, r.p25, r.p50, r.p75)
                    for r in rows
                ],
            )
    return run_id


def _now_utc():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)


def _to_jsonb(obj: Any) -> str:
    import json
    return json.dumps(obj)


def _stat_tuple(run_id: str, metric_id: str, r: Any) -> tuple:
    """Normalize an M1Row or a SegmentStat into one market_stat insert tuple.

    M1Row has no value_num/value_extra — getattr defaults them to None so both row
    shapes (F1's M1Row and F2's SegmentStat, see pipeline/market/cohort.py) flow
    through the SAME insert statement.
    """
    value_extra = getattr(r, "value_extra", None)
    return (
        run_id, metric_id, r.make, r.model, r.year, r.fuel, r.province_code, r.n,
        r.p25, r.p50, r.p75,
        getattr(r, "value_num", None),
        _to_jsonb(value_extra) if value_extra is not None else None,
    )


_INSERT_STAT_SQL = """
    INSERT INTO market_stat
        (run_id, metric_id, make, model, year, fuel, province_code, n, p25, p50, p75,
         value_num, value_extra)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13::jsonb)
"""


async def run_compute_full(
    conn: asyncpg.Connection,
    *,
    publish_intent: bool = False,
    director_confirmed_anomalies: bool = False,
    make_filter: list[str] | None = None,
) -> tuple[str, Any]:
    """F2: one run computing M1 + M3/M4/M5/M7/M9/M10, then (optionally) the publish gate.

    Returns (run_id, gate_result_or_None). gate_result is None when
    ``publish_intent`` is False (the run is written but nobody asked to publish it —
    mirrors F1's ``run_compute`` default). When ``publish_intent`` is True, the +/-3%
    run-over-run gate (pipeline/market/publish_gate.py) runs against the current
    latest PUBLISHED run (if any — the very first run has no baseline, see that
    module's bootstrap handling) and, if clean (or ``director_confirmed_anomalies``),
    flips published=TRUE.
    """
    # Import here (not at module top) to avoid a hard circular-ish coupling for F1
    # callers that only need run_compute(); F2 callers pay this import once.
    from pipeline.market.metrics_f2 import fetch_m3, fetch_m4, fetch_m5, fetch_m7, fetch_m9, fetch_m10
    from pipeline.market.publish_gate import publish_run

    t0 = time.monotonic()
    span_days = await _span_days(conn)

    m1_rows, n_in_m1 = await fetch_m1(conn, make_filter)
    checks = await crosscheck_m1(conn, m1_rows)
    if not checks["passed"] and checks["sampled"] > 0:
        raise RuntimeError(
            f"compute_stats M1: SQL-vs-Python cross-check FAILED — "
            f"max divergence {checks['max_divergence_pct']:.4f}% >= tolerance "
            f"{CROSSCHECK_TOLERANCE_PCT}%. Run NOT written."
        )

    m3_rows, n_in_m3, w3 = await fetch_m3(conn, span_days=span_days, make_filter=make_filter)
    m4_rows, w4 = await fetch_m4(conn, m1_rows, span_days=span_days, make_filter=make_filter)
    m5_rows, n_in_m5, w5 = await fetch_m5(conn, span_days=span_days, make_filter=make_filter)
    m7_rows, w7 = await fetch_m7(conn, span_days=span_days, make_filter=make_filter)
    m9_rows, w9 = await fetch_m9(conn, m1_rows, span_days=span_days, make_filter=make_filter)
    m10_rows = await fetch_m10(conn, make_filter=make_filter)

    elapsed = time.monotonic() - t0
    checks["elapsed_seconds_all_metrics"] = round(elapsed, 2)
    window_desc = (
        f"{WINDOW_DESCRIPTION_M1} | M3={w3:.1f}d | M4={w4:.1f}d | M5={w5:.1f}d | "
        f"M7_half={w7:.1f}d (2x) | M9={w9:.1f}d | span_days_observed={span_days:.1f}"
    )

    run_id = ulid()
    all_rows: list[tuple] = []
    all_rows += [_stat_tuple(run_id, "M1", r) for r in m1_rows]
    all_rows += [_stat_tuple(run_id, "M3", r) for r in m3_rows]
    all_rows += [_stat_tuple(run_id, "M4", r) for r in m4_rows]
    all_rows += [_stat_tuple(run_id, "M5", r) for r in m5_rows]
    all_rows += [_stat_tuple(run_id, "M7", r) for r in m7_rows]
    all_rows += [_stat_tuple(run_id, "M9", r) for r in m9_rows]
    all_rows += [_stat_tuple(run_id, "M10", r) for r in m10_rows]

    async with conn.transaction():
        await conn.execute(
            """
            INSERT INTO market_stat_run
                (run_id, methodology_version, window_description, n_in,
                 metrics_computed, checks, published, published_at, notes)
            VALUES ($1, $2, $3, $4, $5, $6::jsonb, FALSE, NULL, $7)
            """,
            run_id, METHODOLOGY_VERSION, window_desc, n_in_m1,
            ["M1", "M3", "M4", "M5", "M7", "M9", "M10"], _to_jsonb(checks),
            f"n_in per metric: M1={n_in_m1} M3={n_in_m3} M5={n_in_m5}",
        )
        if all_rows:
            await conn.executemany(_INSERT_STAT_SQL, all_rows)

    gate_result = None
    if publish_intent:
        gate_result = await publish_run(
            conn, run_id, director_confirmed_anomalies=director_confirmed_anomalies
        )
    return run_id, gate_result


async def _span_days(conn: asyncpg.Connection) -> float:
    from pipeline.market.cohort import get_span_days
    return await get_span_days(conn)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true", help="mark the run published=TRUE (F1 default: never)")
    parser.add_argument("--full", action="store_true", help="F2: compute M1+M3/M4/M5/M7/M9/M10 in one run")
    parser.add_argument(
        "--confirm-anomalies", action="store_true",
        help="Director override: publish even if the +/-3% gate is red",
    )
    args = parser.parse_args()

    conn = await asyncpg.connect(DSN, command_timeout=900)
    try:
        if args.full:
            run_id, gate_result = await run_compute_full(
                conn, publish_intent=args.publish, director_confirmed_anomalies=args.confirm_anomalies
            )
            n_rows = await conn.fetchval("SELECT count(*) FROM market_stat WHERE run_id = $1", run_id)
            run_row = await conn.fetchrow(
                "SELECT n_in, published, metrics_computed FROM market_stat_run WHERE run_id = $1", run_id
            )
            print(f"run_id={run_id}")
            print(f"n_in(M1)={run_row['n_in']}")
            print(f"metrics_computed={run_row['metrics_computed']}")
            print(f"market_stat rows written={n_rows}")
            print(f"published={run_row['published']}")
            if gate_result is not None:
                print(f"gate: has_baseline={gate_result.has_baseline} compared={gate_result.compared} "
                      f"anomalies={len(gate_result.anomalies)} max_div={gate_result.max_divergence_pct:.3f}%")
        else:
            run_id = await run_compute(conn, publish=args.publish)
            n_rows = await conn.fetchval("SELECT count(*) FROM market_stat WHERE run_id = $1", run_id)
            run_row = await conn.fetchrow(
                "SELECT n_in, published, checks FROM market_stat_run WHERE run_id = $1", run_id
            )
            print(f"run_id={run_id}")
            print(f"n_in={run_row['n_in']}")
            print(f"market_stat rows written={n_rows}")
            print(f"published={run_row['published']}")
            print(f"checks={run_row['checks']}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
