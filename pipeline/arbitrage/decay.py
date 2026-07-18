"""pipeline/arbitrage/decay.py — time-arbitrage job (04-arbitrage.md F4).

Two signals, two tables (migrations/0081_arbitrage_decay.sql — a declared deviation
from the carta's single-table §5.2 naming; see that migration's header for why):

1. ``market_cycle_stats`` — "Curva de salida por cohorte" (§4.3): for cohorts
   (make, model, 2-year year-band) with >=50 completed NEW->GONE cycles in the last
   12 months, publishes median/P25/P75 days-to-GONE and the fraction of cycles with
   at least one price DROP before GONE. One cycle per vehicle (its EARLIEST NEW
   paired with the EARLIEST GONE strictly after it) — a relisted vehicle's later
   cycles are not counted, a documented scoping decision, not a hidden one.

2. ``market_decay`` — "Curva de decaimiento por cohorte" (§4.3): every price
   OBSERVATION-POINT a vehicle has (its initial NEW price at age 0, plus each
   PRICE_CHANGE's new price at its own age) is one sample of price-relative-to-
   initial at that age. Bucketed into the 6 age buckets the carta names
   (0-7/8-15/16-30/31-60/61-90/90+ days); a bucket with n<30 is never written
   (mínimo-N-o-silencio, patente Mercari §2.5).

"salida del mercado ≠ venta confirmada" (§4.3): a GONE event is never described as a
sale anywhere in this module's output or the API surface built on top of it.

Verification (§7, streamlined for this phase — declared, not the carta's full
holdout-backtest): each of a sample of >=20 cohorts/cells is independently
recomputed via a FRESH raw refetch + pure-Python percentile (``pipeline.market.
cohort.median`` — one percentile implementation project-wide, C-1) and compared
against the SQL-computed value. A true forward-holdout backtest (train on all-but-
last-month, score against the held-out month) is a declared gap for a future pass —
this is a real dual-path cross-check, just not that specific temporal design.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import time
from typing import Any

import asyncpg

from pipeline.ids import ulid
from pipeline.market.cohort import divergence_pct, median

METHODOLOGY_VERSION = "v1"

MIN_CYCLES_PER_COHORT: int = 50     # §4.3: ">=50 ciclos completos NEW->GONE en los últimos 12 meses"
MIN_OBS_PER_BUCKET: int = 30        # §4.3: "cada punto exige >=30 observaciones en el bucket"
CYCLE_LOOKBACK_MONTHS: int = 12

_BUCKET_CASE_SQL = """
    CASE WHEN age_days <= 7  THEN '0-7'
         WHEN age_days <= 15 THEN '8-15'
         WHEN age_days <= 30 THEN '16-30'
         WHEN age_days <= 60 THEN '31-60'
         WHEN age_days <= 90 THEN '61-90'
         ELSE '90+' END
"""
BUCKET_MIN_DAYS: dict[str, int] = {"0-7": 0, "8-15": 8, "16-30": 16, "31-60": 31, "61-90": 61, "90+": 91}

CROSSCHECK_SAMPLE_SIZE: int = 20
CROSSCHECK_TOLERANCE_PCT: float = 0.5


def _make_filter_clause(make_filter: list[str] | None, param_idx: int) -> tuple[str, list[Any]]:
    if not make_filter:
        return "", []
    return f" AND v.make = ANY(${param_idx}::text[])", [list(make_filter)]


# ---------------------------------------------------------------------------
# 1. market_cycle_stats — days-to-GONE distribution per cohort
# ---------------------------------------------------------------------------

async def fetch_cycle_stats(
    conn: asyncpg.Connection, *, make_filter: list[str] | None = None
) -> list[dict[str, Any]]:
    clause, params = _make_filter_clause(make_filter, 1)
    sql = f"""
        WITH cycles AS (
            SELECT DISTINCT ON (v.vehicle_ulid)
                   v.vehicle_ulid, v.make, v.model, v.year, e.country_code,
                   ne.observed_at AS new_at, ge.observed_at AS gone_at
              FROM vehicle v
              JOIN entity e ON e.entity_ulid = v.entity_ulid
              JOIN vehicle_event ne ON ne.vehicle_ulid = v.vehicle_ulid AND ne.event_type = 'NEW'
              JOIN vehicle_event ge ON ge.vehicle_ulid = v.vehicle_ulid AND ge.event_type = 'GONE'
                                    AND ge.observed_at > ne.observed_at
             WHERE v.make IS NOT NULL AND v.model IS NOT NULL AND v.year IS NOT NULL{clause}
             ORDER BY v.vehicle_ulid, ne.observed_at ASC, ge.observed_at ASC
        ),
        recent AS (
            SELECT *, (year - (year % 2)) AS year_band_start,
                   EXTRACT(EPOCH FROM (gone_at - new_at)) / 86400.0 AS days_to_gone
              FROM cycles
             WHERE gone_at >= now() - interval '{CYCLE_LOOKBACK_MONTHS} months'
               AND gone_at > new_at
        ),
        price_drop AS (
            SELECT r.vehicle_ulid,
                   EXISTS (
                       SELECT 1 FROM vehicle_event pc
                        WHERE pc.vehicle_ulid = r.vehicle_ulid AND pc.event_type = 'PRICE_CHANGE'
                          AND pc.observed_at > r.new_at AND pc.observed_at < r.gone_at
                          AND (pc.new_value->>'price')::numeric < (pc.old_value->>'price')::numeric
                   ) AS had_drop
              FROM recent r
        )
        SELECT r.country_code, r.make, r.model, r.year_band_start, count(*) AS n,
               percentile_cont(0.5)  WITHIN GROUP (ORDER BY r.days_to_gone) AS median_days,
               percentile_cont(0.25) WITHIN GROUP (ORDER BY r.days_to_gone) AS p25_days,
               percentile_cont(0.75) WITHIN GROUP (ORDER BY r.days_to_gone) AS p75_days,
               avg(CASE WHEN pd.had_drop THEN 1.0 ELSE 0.0 END) AS pct_price_drop
          FROM recent r JOIN price_drop pd ON pd.vehicle_ulid = r.vehicle_ulid
         GROUP BY r.country_code, r.make, r.model, r.year_band_start
        HAVING count(*) >= {MIN_CYCLES_PER_COHORT}
    """
    rows = await conn.fetch(sql, *params)
    return [
        {
            "country_code": r["country_code"], "make": r["make"], "model": r["model"],
            "year_band_start": r["year_band_start"], "n": int(r["n"]),
            "median_days": float(r["median_days"]), "p25_days": float(r["p25_days"]),
            "p75_days": float(r["p75_days"]), "pct_price_drop": float(r["pct_price_drop"]),
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# 2. market_decay — age-bucket relative-price curve
# ---------------------------------------------------------------------------

async def fetch_decay_buckets(
    conn: asyncpg.Connection, *, make_filter: list[str] | None = None
) -> list[dict[str, Any]]:
    clause, params = _make_filter_clause(make_filter, 1)
    sql = f"""
        WITH samples AS (
            SELECT v.vehicle_ulid, v.make, v.model, v.year, e.country_code,
                   0.0 AS age_days, (ev.new_value->>'price')::numeric AS price_at_point
              FROM vehicle v
              JOIN entity e ON e.entity_ulid = v.entity_ulid
              JOIN vehicle_event ev ON ev.vehicle_ulid = v.vehicle_ulid AND ev.event_type = 'NEW'
             WHERE v.make IS NOT NULL AND v.model IS NOT NULL AND v.year IS NOT NULL
               AND (ev.new_value->>'price') IS NOT NULL{clause}
            UNION ALL
            SELECT v.vehicle_ulid, v.make, v.model, v.year, e.country_code,
                   EXTRACT(EPOCH FROM (ev.observed_at - v.first_seen)) / 86400.0 AS age_days,
                   (ev.new_value->>'price')::numeric AS price_at_point
              FROM vehicle v
              JOIN entity e ON e.entity_ulid = v.entity_ulid
              JOIN vehicle_event ev ON ev.vehicle_ulid = v.vehicle_ulid AND ev.event_type = 'PRICE_CHANGE'
             WHERE v.make IS NOT NULL AND v.model IS NOT NULL AND v.year IS NOT NULL
               AND (ev.new_value->>'price') IS NOT NULL{clause}
        ),
        initial AS (
            SELECT vehicle_ulid, price_at_point AS initial_price FROM samples WHERE age_days = 0.0
        ),
        relative AS (
            SELECT s.vehicle_ulid, s.make, s.model, s.year, s.country_code, s.age_days,
                   s.price_at_point / i.initial_price AS relative_price
              FROM samples s JOIN initial i ON i.vehicle_ulid = s.vehicle_ulid
             WHERE i.initial_price > 0 AND s.age_days >= 0
        ),
        bucketed AS (
            SELECT *, {_BUCKET_CASE_SQL} AS bucket_label, (year - (year % 2)) AS year_band_start
              FROM relative
        )
        SELECT country_code, make, model, year_band_start, bucket_label, count(*) AS n,
               percentile_cont(0.5) WITHIN GROUP (ORDER BY relative_price) AS median_relative_price
          FROM bucketed
         GROUP BY country_code, make, model, year_band_start, bucket_label
        HAVING count(*) >= {MIN_OBS_PER_BUCKET}
    """
    # make_filter's placeholder ($1) is TEXTUALLY repeated in both UNION ALL branches, but it is
    # still the SAME positional parameter — asyncpg binds one value to every occurrence of $1, so
    # it is passed ONCE, not once per branch.
    rows = await conn.fetch(sql, *params)
    return [
        {
            "country_code": r["country_code"], "make": r["make"], "model": r["model"],
            "year_band_start": r["year_band_start"], "bucket_label": r["bucket_label"],
            "n": int(r["n"]), "median_relative_price": float(r["median_relative_price"]),
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Dual-path verification (§7, streamlined — see module docstring)
# ---------------------------------------------------------------------------

async def _crosscheck_cycle_stats(conn: asyncpg.Connection, cohorts: list[dict[str, Any]]) -> dict[str, Any]:
    if not cohorts:
        return {"sampled": 0, "passed": True, "max_divergence_pct": 0.0, "segments": []}
    sample = sorted(cohorts, key=lambda c: c["n"], reverse=True)[:CROSSCHECK_SAMPLE_SIZE]
    max_div = 0.0
    segments = []
    for c in sample:
        raw = await conn.fetch(
            f"""
            WITH cycles AS (
                SELECT DISTINCT ON (v.vehicle_ulid) v.vehicle_ulid, ne.observed_at AS new_at, ge.observed_at AS gone_at
                  FROM vehicle v
                  JOIN entity e ON e.entity_ulid = v.entity_ulid
                  JOIN vehicle_event ne ON ne.vehicle_ulid = v.vehicle_ulid AND ne.event_type = 'NEW'
                  JOIN vehicle_event ge ON ge.vehicle_ulid = v.vehicle_ulid AND ge.event_type = 'GONE'
                                        AND ge.observed_at > ne.observed_at
                 WHERE e.country_code = $1 AND v.make = $2 AND v.model = $3 AND (v.year - (v.year % 2)) = $4
                 ORDER BY v.vehicle_ulid, ne.observed_at ASC, ge.observed_at ASC
            )
            SELECT EXTRACT(EPOCH FROM (gone_at - new_at)) / 86400.0 AS days
              FROM cycles WHERE gone_at >= now() - interval '{CYCLE_LOOKBACK_MONTHS} months' AND gone_at > new_at
            """,
            c["country_code"], c["make"], c["model"], c["year_band_start"],
        )
        days = sorted(float(r["days"]) for r in raw)
        py_n = len(days)
        py_median = median(days) if days else 0.0
        d_n = divergence_pct(py_n, c["n"])
        d_med = divergence_pct(py_median, c["median_days"])
        seg_max = max(d_n, d_med)
        max_div = max(max_div, seg_max)
        segments.append({"make": c["make"], "model": c["model"], "year_band_start": c["year_band_start"],
                          "sql_n": c["n"], "python_n": py_n, "divergence_pct": round(seg_max, 4)})
    return {"sampled": len(sample), "passed": max_div < CROSSCHECK_TOLERANCE_PCT,
            "max_divergence_pct": round(max_div, 4), "segments": segments}


async def _crosscheck_decay_buckets(conn: asyncpg.Connection, buckets: list[dict[str, Any]]) -> dict[str, Any]:
    if not buckets:
        return {"sampled": 0, "passed": True, "max_divergence_pct": 0.0, "segments": []}
    sample = sorted(buckets, key=lambda b: b["n"], reverse=True)[:CROSSCHECK_SAMPLE_SIZE]
    max_div = 0.0
    segments = []
    for b in sample:
        min_d, max_d = _bucket_day_range(b["bucket_label"])
        raw = await conn.fetch(
            f"""
            WITH samples AS (
                SELECT v.vehicle_ulid, 0.0 AS age_days, (ev.new_value->>'price')::numeric AS price_at_point
                  FROM vehicle v JOIN entity e ON e.entity_ulid = v.entity_ulid
                  JOIN vehicle_event ev ON ev.vehicle_ulid = v.vehicle_ulid AND ev.event_type = 'NEW'
                 WHERE e.country_code = $1 AND v.make = $2 AND v.model = $3 AND (v.year - (v.year % 2)) = $4
                   AND (ev.new_value->>'price') IS NOT NULL
                UNION ALL
                SELECT v.vehicle_ulid, EXTRACT(EPOCH FROM (ev.observed_at - v.first_seen)) / 86400.0,
                       (ev.new_value->>'price')::numeric
                  FROM vehicle v JOIN entity e ON e.entity_ulid = v.entity_ulid
                  JOIN vehicle_event ev ON ev.vehicle_ulid = v.vehicle_ulid AND ev.event_type = 'PRICE_CHANGE'
                 WHERE e.country_code = $1 AND v.make = $2 AND v.model = $3 AND (v.year - (v.year % 2)) = $4
                   AND (ev.new_value->>'price') IS NOT NULL
            ),
            initial AS (SELECT vehicle_ulid, price_at_point AS initial_price FROM samples WHERE age_days = 0.0)
            SELECT s.price_at_point / i.initial_price AS relative_price
              FROM samples s JOIN initial i ON i.vehicle_ulid = s.vehicle_ulid
             WHERE i.initial_price > 0 AND s.age_days >= $5 AND s.age_days <= $6
            """,
            b["country_code"], b["make"], b["model"], b["year_band_start"], min_d, max_d,
        )
        vals = sorted(float(r["relative_price"]) for r in raw)
        py_n = len(vals)
        py_median = median(vals) if vals else 0.0
        d_n = divergence_pct(py_n, b["n"])
        d_med = divergence_pct(py_median, b["median_relative_price"])
        seg_max = max(d_n, d_med)
        max_div = max(max_div, seg_max)
        segments.append({"make": b["make"], "model": b["model"], "bucket": b["bucket_label"],
                          "sql_n": b["n"], "python_n": py_n, "divergence_pct": round(seg_max, 4)})
    return {"sampled": len(sample), "passed": max_div < CROSSCHECK_TOLERANCE_PCT,
            "max_divergence_pct": round(max_div, 4), "segments": segments}


def _bucket_day_range(label: str) -> tuple[float, float]:
    ranges = {"0-7": (0.0, 7.0), "8-15": (8.0, 15.0), "16-30": (16.0, 30.0),
              "31-60": (31.0, 60.0), "61-90": (61.0, 90.0), "90+": (91.0, 1e9)}
    return ranges[label]


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

async def run_decay(
    conn: asyncpg.Connection, *, make_filter: list[str] | None = None
) -> tuple[str, dict[str, Any]]:
    """Compute one full time-arbitrage run: market_cycle_stats + market_decay, INSERT-only.

    Never sets published=TRUE (mirrors F1's contract). Raises RuntimeError if either
    dual-path cross-check fails (the run row is still written for audit).
    """
    t0 = time.monotonic()
    cycle_rows = await fetch_cycle_stats(conn, make_filter=make_filter)
    bucket_rows = await fetch_decay_buckets(conn, make_filter=make_filter)

    checks_cycle = await _crosscheck_cycle_stats(conn, cycle_rows)
    checks_bucket = await _crosscheck_decay_buckets(conn, bucket_rows)
    checks = {
        "cycle_stats": checks_cycle, "decay_buckets": checks_bucket,
        "elapsed_seconds": round(time.monotonic() - t0, 2),
        "declared_gap": "streamlined dual-path (fresh SQL+Python recompute), not the carta's full "
                         "forward-holdout backtest — see module docstring.",
    }
    passed = checks_cycle["passed"] and checks_bucket["passed"]

    run_id = ulid()
    async with conn.transaction():
        await conn.execute(
            "INSERT INTO arbitrage_decay_run (run_id, methodology_version, n_cycles_scanned, "
            "n_cohorts_cycle, n_bucket_rows, checks) VALUES ($1,$2,$3,$4,$5,$6::jsonb)",
            run_id, METHODOLOGY_VERSION,
            sum(c["n"] for c in cycle_rows), len(cycle_rows), len(bucket_rows),
            _to_jsonb(checks),
        )
        if cycle_rows:
            await conn.executemany(
                "INSERT INTO market_cycle_stats (run_id, country_code, make, model, year_band_start, "
                "n_cycles, median_days_to_gone, p25_days_to_gone, p75_days_to_gone, pct_price_drop_before_gone) "
                "VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)",
                [
                    (run_id, c["country_code"], c["make"], c["model"], c["year_band_start"], c["n"],
                     c["median_days"], c["p25_days"], c["p75_days"], c["pct_price_drop"])
                    for c in cycle_rows
                ],
            )
        if bucket_rows:
            await conn.executemany(
                "INSERT INTO market_decay (run_id, country_code, make, model, year_band_start, "
                "bucket_label, bucket_min_days, n, median_relative_price) "
                "VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)",
                [
                    (run_id, b["country_code"], b["make"], b["model"], b["year_band_start"],
                     b["bucket_label"], BUCKET_MIN_DAYS[b["bucket_label"]], b["n"], b["median_relative_price"])
                    for b in bucket_rows
                ],
            )

    if not passed:
        raise RuntimeError(
            f"arbitrage decay run {run_id}: dual-path cross-check FAILED. Run row written for audit; "
            f"NOT usable. cycle_stats={checks_cycle}, decay_buckets={checks_bucket}"
        )

    return run_id, checks


def _to_jsonb(obj: Any) -> str:
    import json
    return json.dumps(obj)


async def _main() -> None:
    parser = argparse.ArgumentParser(description="04-arbitrage F4 time-arbitrage job")
    parser.parse_args()
    dsn = os.environ.get("CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep")
    conn = await asyncpg.connect(dsn)
    try:
        run_id, checks = await run_decay(conn)
        print(f"decay run {run_id}: cycle_stats={checks['cycle_stats']['sampled']} sampled "
              f"(max_div={checks['cycle_stats']['max_divergence_pct']}%), "
              f"decay_buckets={checks['decay_buckets']['sampled']} sampled "
              f"(max_div={checks['decay_buckets']['max_divergence_pct']}%)")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(_main())
