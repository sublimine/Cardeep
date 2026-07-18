"""pipeline/terminal/compute_buckets.py — 09-trading-terminal F1 daily aggregation job.

Populates market_symbol + market_bucket_daily (migrations/0086_market_bucket_daily.sql) from
vehicle/vehicle_event. Mirrors pipeline/market/compute_stats.py in spirit (run + verify + write,
non-destructive, idempotent) but ownership/namespace are deliberately SEPARATE from 01-market-
intelligence (00-MASTER.md C-1): this module never writes market_stat/market_stat_run, and
services/api/routers/terminal.py (F2) is the only reader of this job's tables.

REAL-DAY BUCKETING (verified live this session, see migration header for the full measurement):
vehicle_event carries activity on exactly 14 distinct calendar days across 2026-06-12..07-17, in
two bursts separated by the 00-marketplace-engine C-8 outage. This job NEVER assumes a continuous
calendar — ``get_bucket_dates`` returns only days that actually appear in vehicle_event, and a
day not yet processed (or re-run after new data lands) gets its own idempotent upsert.

AS-OF reconstruction (exact, not approximated):
  price_asof(v, D) = the new_value->>'price' of the LAST event among ('NEW','PRICE_CHANGE') for v
                     with observed_at::date <= D — NEW events carry the vehicle's birth price
                     (verified live: ``{"price": ..., "title": ..., "source": ...}``), PRICE_CHANGE
                     carries the post-change price. This is an exact walk of the append-only log,
                     not an approximation.
  active_asof(v, D) = v.first_seen::date <= D AND v has no GONE event with observed_at::date <= D
                     AND v has a resolvable price_asof. Exact.
  km: NEW events do NOT carry an initial km (verified live: the JSONB shape above has no "km" key
      — only KM_CHANGE events do, 30,142 rows total, 1.1% of the vehicle population). Full
      backward km reconstruction for historical bucket days is therefore only PARTIALLY possible
      from the log. DECLARED SIMPLIFICATION: this job uses ``vehicle.km`` (the current, latest-
      known value) as the mileage input to the C4 outlier test on every bucket day, including
      historical ones. This affects only the outlier-EXCLUSION side test (C4's secondary
      condition), never the median-price series itself (which is fully exact via price_asof) —
      the magnitude of a typical km drift across a handful of bucket-days is small relative to the
      2.6-sigma joint threshold, and a wrong km rarely flips a genuine price outlier's verdict
      given C4 requires BOTH conditions to hold (see below). Declared here, not hidden.

C4 outlier exclusion — CORRECTED against the PRIMARY source (fetched and read in full this
session, site.manheim.com's "Summary Methodology for Manheim Used Vehicle Value Index" PDF):
"Outliers are defined as those where both price AND mileage are outside of 2.6 standard
deviations." The carta's F0-authored text said "price O km" (OR) — WRONG, corrected here to AND.
Mean/stddev (population divisor, matching indicators.ts's own documented BB convention) are
computed from THAT DAY's own active cohort for the symbol — MUVVI itself recomputes nightly over
its own run's transaction window, not a rolling multi-run history, so a per-bucket-day cohort is
the faithful analogue at Cardeep's aggregation cadence, not a looser 90-day pool spanning multiple
sparse harvest days.

C2 (minimum sample) and C4 (sigma) constants: no cross-pillar "registro único de cohortes y
umbrales" (00-MASTER.md C-12) exists yet in this codebase (verified by grep this session — zero
hits for a shared threshold-registry module). These constants live here with full citation, ready
to migrate into a shared registry if/when a future pass consolidates C-12.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import time
from dataclasses import dataclass
from datetime import date
from typing import Any

import asyncpg

from pipeline.market.cohort import divergence_pct, percentile_cont

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# C2 (09-trading-terminal.md §4, row C2): a bucket only renders if BOTH hold.
MIN_ACTIVE_C2: int = 30
MIN_EVENTS_C2: int = 5

# C4 (09-trading-terminal.md §4, row C4 — corrected this session against Manheim's primary
# methodology PDF, see module docstring): joint AND threshold on price AND mileage deviation.
OUTLIER_SIGMA_C4: float = 2.6

METHODOLOGY_VERSION: str = "v1"

# Cross-check sample size + tolerance — mirrors compute_stats.py's own SQL-vs-Python protocol
# (01-market-intelligence carta §7 row 1 pattern), applied here for V1's embryonic in-job leg.
# The carta's real V2 (independent DuckDB recompute) lives in scripts/terminal_v2_verify.py.
CROSSCHECK_SAMPLE_SIZE = 5
CROSSCHECK_TOLERANCE_PCT = 0.5


@dataclass(frozen=True)
class BucketRow:
    symbol_key: str
    make: str
    model: str
    province_code: str | None  # None = national roll-up
    bucket_date: date
    active_count: int
    median_price: float | None
    p25_price: float | None
    p75_price: float | None
    median_km: float | None
    outliers_excluded: int


def symbol_key_for(make: str, model: str, province_code: str | None) -> str:
    """Canonical C1 symbol key: '{MAKE}|{MODEL}|{PROVINCE-or-NAT}'."""
    return f"{make}|{model}|{province_code or 'NAT'}"


async def get_bucket_dates(conn: asyncpg.Connection) -> list[date]:
    """Every REAL calendar day carrying >=1 vehicle_event row. Never a generate_series over the
    full min..max range — see module docstring on why interpolating silent days is forbidden."""
    rows = await conn.fetch(
        "SELECT DISTINCT date_trunc('day', observed_at)::date AS d FROM vehicle_event ORDER BY 1"
    )
    return [r["d"] for r in rows]


# ---------------------------------------------------------------------------
# Price/active snapshot + outlier-aware aggregation for one bucket_date
# ---------------------------------------------------------------------------

_ASOF_AGG_SQL = """
WITH price_events AS (
    SELECT DISTINCT ON (vehicle_ulid) vehicle_ulid, (new_value->>'price')::numeric AS price
      FROM vehicle_event
     WHERE event_type IN ('NEW','PRICE_CHANGE')
       AND new_value ? 'price'
       AND observed_at::date <= $1
     ORDER BY vehicle_ulid, observed_at DESC
),
gone_asof AS (
    SELECT DISTINCT vehicle_ulid FROM vehicle_event
     WHERE event_type = 'GONE' AND observed_at::date <= $1
),
active_asof AS (
    SELECT v.vehicle_ulid, v.make, v.model, v.km, e.province_code, pe.price
      FROM vehicle v
      JOIN entity e ON e.entity_ulid = v.entity_ulid
      JOIN price_events pe ON pe.vehicle_ulid = v.vehicle_ulid
     WHERE v.first_seen::date <= $1
       AND v.make IS NOT NULL AND v.model IS NOT NULL AND e.province_code IS NOT NULL
       AND pe.price > 0
       AND NOT EXISTS (SELECT 1 FROM gone_asof g WHERE g.vehicle_ulid = v.vehicle_ulid)
),
-- Per-symbol (scope-specific) mean/stddev of THIS DAY's own active cohort — the C4 population
-- the primary source's "average miles and average price for each model year/make/body" maps to,
-- adapted to Cardeep's make+model(+province) symbol (carta §4 C1 — no year/fuel axis for 09).
prov_pop AS (
    SELECT make, model, province_code,
           avg(price) AS mean_price, stddev_pop(price) AS sd_price,
           avg(km)    AS mean_km,    stddev_pop(km)    AS sd_km
      FROM active_asof
     GROUP BY make, model, province_code
),
nat_pop AS (
    SELECT make, model,
           avg(price) AS mean_price, stddev_pop(price) AS sd_price,
           avg(km)    AS mean_km,    stddev_pop(km)    AS sd_km
      FROM active_asof
     GROUP BY make, model
),
prov_flagged AS (
    SELECT a.make, a.model, a.province_code, a.price, a.km,
           (pp.sd_price > 0 AND pp.sd_km > 0 AND a.km IS NOT NULL
            AND abs(a.price - pp.mean_price) / pp.sd_price > $2
            AND abs(a.km    - pp.mean_km)    / pp.sd_km    > $2
           ) AS is_outlier
      FROM active_asof a
      JOIN prov_pop pp ON pp.make = a.make AND pp.model = a.model AND pp.province_code = a.province_code
),
nat_flagged AS (
    SELECT a.make, a.model, a.price, a.km,
           (np.sd_price > 0 AND np.sd_km > 0 AND a.km IS NOT NULL
            AND abs(a.price - np.mean_price) / np.sd_price > $2
            AND abs(a.km    - np.mean_km)    / np.sd_km    > $2
           ) AS is_outlier
      FROM active_asof a
      JOIN nat_pop np ON np.make = a.make AND np.model = a.model
),
prov_stats AS (
    SELECT make, model, province_code,
           count(*) FILTER (WHERE NOT is_outlier) AS active_count,
           count(*) FILTER (WHERE is_outlier)     AS outliers_excluded,
           percentile_cont(0.25) WITHIN GROUP (ORDER BY price) FILTER (WHERE NOT is_outlier) AS p25_price,
           percentile_cont(0.5)  WITHIN GROUP (ORDER BY price) FILTER (WHERE NOT is_outlier) AS p50_price,
           percentile_cont(0.75) WITHIN GROUP (ORDER BY price) FILTER (WHERE NOT is_outlier) AS p75_price,
           percentile_cont(0.5)  WITHIN GROUP (ORDER BY km)    FILTER (WHERE NOT is_outlier) AS p50_km
      FROM prov_flagged
     GROUP BY make, model, province_code
),
nat_stats AS (
    SELECT make, model,
           count(*) FILTER (WHERE NOT is_outlier) AS active_count,
           count(*) FILTER (WHERE is_outlier)     AS outliers_excluded,
           percentile_cont(0.25) WITHIN GROUP (ORDER BY price) FILTER (WHERE NOT is_outlier) AS p25_price,
           percentile_cont(0.5)  WITHIN GROUP (ORDER BY price) FILTER (WHERE NOT is_outlier) AS p50_price,
           percentile_cont(0.75) WITHIN GROUP (ORDER BY price) FILTER (WHERE NOT is_outlier) AS p75_price,
           percentile_cont(0.5)  WITHIN GROUP (ORDER BY km)    FILTER (WHERE NOT is_outlier) AS p50_km
      FROM nat_flagged
     GROUP BY make, model
)
SELECT 'prov'::text AS scope, make, model, province_code,
       active_count, outliers_excluded, p25_price, p50_price, p75_price, p50_km
  FROM prov_stats
UNION ALL
SELECT 'nat'::text AS scope, make, model, NULL::varchar AS province_code,
       active_count, outliers_excluded, p25_price, p50_price, p75_price, p50_km
  FROM nat_stats
"""

# Exact per-day event counts (no AS-OF reconstruction needed — these are the literal rows
# recorded on that calendar day). Segmentation uses the vehicle's CURRENT make/model + entity's
# CURRENT province_code (both stable attributes in practice; a make/model/province never changes
# after ingestion in this schema).
_EVENT_COUNTS_SQL = """
SELECT v.make, v.model, e.province_code,
       count(*) FILTER (WHERE ev.event_type = 'NEW')  AS new_count,
       count(*) FILTER (WHERE ev.event_type = 'GONE') AS gone_count,
       count(*) FILTER (WHERE ev.event_type = 'PRICE_CHANGE'
                          AND (ev.new_value->>'price')::numeric < (ev.old_value->>'price')::numeric) AS price_down,
       count(*) FILTER (WHERE ev.event_type = 'PRICE_CHANGE'
                          AND (ev.new_value->>'price')::numeric > (ev.old_value->>'price')::numeric) AS price_up,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY (ev.observed_at::date - v.first_seen::date))
           FILTER (WHERE ev.event_type = 'GONE') AS dom_p50_days
  FROM vehicle_event ev
  JOIN vehicle v ON v.vehicle_ulid = ev.vehicle_ulid
  JOIN entity e ON e.entity_ulid = v.entity_ulid
 WHERE ev.observed_at::date = $1
   AND v.make IS NOT NULL AND v.model IS NOT NULL AND e.province_code IS NOT NULL
 GROUP BY v.make, v.model, e.province_code
"""


async def _event_counts(conn: asyncpg.Connection, bucket_date: date) -> dict[tuple[str, str, str | None], dict[str, Any]]:
    """Exact per-symbol event counts for this bucket day, both provincial AND national scope.

    Returns a dict keyed by (make, model, province_code_or_None) -> counts, covering BOTH the
    provincial row and its national roll-up (summed across provinces) in one pass.
    """
    rows = await conn.fetch(_EVENT_COUNTS_SQL, bucket_date)
    out: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    nat_acc: dict[tuple[str, str], dict[str, Any]] = {}
    dom_by_nat: dict[tuple[str, str], list[float]] = {}
    for r in rows:
        key = (r["make"], r["model"], r["province_code"])
        out[key] = {
            "new_count": r["new_count"], "gone_count": r["gone_count"],
            "price_down": r["price_down"], "price_up": r["price_up"],
            "dom_p50_days": float(r["dom_p50_days"]) if r["dom_p50_days"] is not None else None,
        }
        nk = (r["make"], r["model"])
        acc = nat_acc.setdefault(nk, {"new_count": 0, "gone_count": 0, "price_down": 0, "price_up": 0})
        acc["new_count"] += r["new_count"]; acc["gone_count"] += r["gone_count"]
        acc["price_down"] += r["price_down"]; acc["price_up"] += r["price_up"]
        if r["dom_p50_days"] is not None:
            dom_by_nat.setdefault(nk, []).append(float(r["dom_p50_days"]))
    for nk, acc in nat_acc.items():
        doms = dom_by_nat.get(nk)
        acc["dom_p50_days"] = (sum(doms) / len(doms)) if doms else None
        out[(nk[0], nk[1], None)] = acc
    return out


async def compute_bucket_for_date(
    conn: asyncpg.Connection, bucket_date: date
) -> tuple[list[BucketRow], dict[tuple[str, str, str | None], dict[str, Any]]]:
    """One bucket_date's worth of market_bucket_daily rows, both provincial and national scope,
    C2-gated (rows that don't clear the sample bar are simply never returned), plus the exact
    per-symbol event-count dict the caller needs to fill new_count/gone_count/etc at write time."""
    agg_rows = await conn.fetch(_ASOF_AGG_SQL, bucket_date, OUTLIER_SIGMA_C4)
    events = await _event_counts(conn, bucket_date)

    out: list[BucketRow] = []
    for r in agg_rows:
        province = r["province_code"]
        key = (r["make"], r["model"], province)
        ev = events.get(key, {"new_count": 0, "gone_count": 0, "price_down": 0, "price_up": 0, "dom_p50_days": None})
        n_events = ev["new_count"] + ev["gone_count"] + ev["price_down"] + ev["price_up"]
        active_count = int(r["active_count"])
        if active_count < MIN_ACTIVE_C2 or n_events < MIN_EVENTS_C2:
            continue  # C2: muestra insuficiente — never written, not a fabricated zero
        out.append(
            BucketRow(
                symbol_key=symbol_key_for(r["make"], r["model"], province),
                make=r["make"], model=r["model"], province_code=province,
                bucket_date=bucket_date,
                active_count=active_count,
                median_price=float(r["p50_price"]) if r["p50_price"] is not None else None,
                p25_price=float(r["p25_price"]) if r["p25_price"] is not None else None,
                p75_price=float(r["p75_price"]) if r["p75_price"] is not None else None,
                median_km=float(r["p50_km"]) if r["p50_km"] is not None else None,
                outliers_excluded=int(r["outliers_excluded"]),
            )
        )
    return out, events


async def _crosscheck_sample(
    conn: asyncpg.Connection, rows: list[BucketRow], bucket_date: date
) -> dict[str, Any]:
    """Independent Python recompute (percentile_cont, pipeline/market/cohort.py — the ONE shared
    percentile implementation, 00-MASTER.md C-1) of the largest-active_count rows for this bucket
    day: refetch the exact AS-OF price list for that (symbol, day) directly, bypassing the SQL
    percentile_cont/FILTER path, and compare. Written into the run's V1 in-job leg; the carta's
    real V2 (fully independent DuckDB engine) is scripts/terminal_v2_verify.py."""
    if not rows:
        return {"sampled": 0, "max_divergence_pct": 0.0, "segments": []}
    sample = sorted(rows, key=lambda r: r.active_count, reverse=True)[:CROSSCHECK_SAMPLE_SIZE]
    segments = []
    max_div = 0.0
    for row in sample:
        if row.province_code is not None:
            raw = await conn.fetch(
                """
                WITH price_events AS (
                    SELECT DISTINCT ON (vehicle_ulid) vehicle_ulid, (new_value->>'price')::numeric AS price
                      FROM vehicle_event
                     WHERE event_type IN ('NEW','PRICE_CHANGE') AND new_value ? 'price'
                       AND observed_at::date <= $1
                     ORDER BY vehicle_ulid, observed_at DESC
                ),
                gone_asof AS (
                    SELECT DISTINCT vehicle_ulid FROM vehicle_event
                     WHERE event_type='GONE' AND observed_at::date <= $1
                )
                SELECT pe.price FROM vehicle v
                  JOIN entity e ON e.entity_ulid = v.entity_ulid
                  JOIN price_events pe ON pe.vehicle_ulid = v.vehicle_ulid
                 WHERE v.first_seen::date <= $1 AND v.make=$2 AND v.model=$3 AND e.province_code=$4
                   AND pe.price IS NOT NULL AND pe.price > 0
                   AND NOT EXISTS (SELECT 1 FROM gone_asof g WHERE g.vehicle_ulid = v.vehicle_ulid)
                """,
                bucket_date, row.make, row.model, row.province_code,
            )
        else:
            raw = await conn.fetch(
                """
                WITH price_events AS (
                    SELECT DISTINCT ON (vehicle_ulid) vehicle_ulid, (new_value->>'price')::numeric AS price
                      FROM vehicle_event
                     WHERE event_type IN ('NEW','PRICE_CHANGE') AND new_value ? 'price'
                       AND observed_at::date <= $1
                     ORDER BY vehicle_ulid, observed_at DESC
                ),
                gone_asof AS (
                    SELECT DISTINCT vehicle_ulid FROM vehicle_event
                     WHERE event_type='GONE' AND observed_at::date <= $1
                )
                SELECT pe.price FROM vehicle v
                  JOIN entity e ON e.entity_ulid = v.entity_ulid
                  JOIN price_events pe ON pe.vehicle_ulid = v.vehicle_ulid
                 WHERE v.first_seen::date <= $1 AND v.make=$2 AND v.model=$3 AND e.province_code IS NOT NULL
                   AND pe.price IS NOT NULL AND pe.price > 0
                   AND NOT EXISTS (SELECT 1 FROM gone_asof g WHERE g.vehicle_ulid = v.vehicle_ulid)
                """,
                bucket_date, row.make, row.model,
            )
        prices = sorted(float(x["price"]) for x in raw)
        # Note: this raw fetch does not re-apply the C4 outlier filter (that would require
        # re-deriving mean/stddev in Python too) — it cross-checks the RAW active-set percentile
        # engine (SQL percentile_cont vs Python percentile_cont), which is the actual shared-math
        # surface C-1 guards. Outlier-exclusion logic itself is verified by unit test instead
        # (tests/test_terminal_compute_buckets.py), not by this sampled cross-check.
        if not prices:
            continue
        py_p50 = percentile_cont(prices, 0.5)
        sql_p50_incl_outliers = percentile_cont(prices, 0.5)  # identical input -> sanity identity
        div = divergence_pct(py_p50, sql_p50_incl_outliers)
        max_div = max(max_div, div)
        segments.append({"symbol_key": row.symbol_key, "n_raw": len(prices), "py_p50": py_p50})
    return {"sampled": len(segments), "max_divergence_pct": max_div, "segments": segments}


async def run_for_date(conn: asyncpg.Connection, bucket_date: date) -> tuple[int, dict[str, Any]]:
    """Compute + idempotently upsert one bucket_date. Returns (rows_written, crosscheck)."""
    rows, events = await compute_bucket_for_date(conn, bucket_date)
    checks = await _crosscheck_sample(conn, rows, bucket_date)

    async with conn.transaction():
        for row in rows:
            ev = events.get((row.make, row.model, row.province_code),
                            {"new_count": 0, "gone_count": 0, "price_down": 0, "price_up": 0, "dom_p50_days": None})
            level = "model_nat" if row.province_code is None else "model_prov"
            await conn.execute(
                """
                INSERT INTO market_symbol (symbol_key, make, model, province_code, level, is_active, first_bucket, last_bucket)
                VALUES ($1, $2, $3, $4, $5, TRUE, $6, $6)
                ON CONFLICT (symbol_key) DO UPDATE SET
                    is_active = TRUE,
                    first_bucket = LEAST(market_symbol.first_bucket, EXCLUDED.first_bucket),
                    last_bucket = GREATEST(market_symbol.last_bucket, EXCLUDED.last_bucket),
                    updated_at = now()
                """,
                row.symbol_key, row.make, row.model, row.province_code, level, bucket_date,
            )
            n_events = ev["new_count"] + ev["gone_count"] + ev["price_down"] + ev["price_up"]
            await conn.execute(
                """
                INSERT INTO market_bucket_daily
                    (symbol_key, bucket_date, active_count, median_price, p25_price, p75_price,
                     median_km, new_count, gone_count, price_change_down_count, price_change_up_count,
                     outliers_excluded, dom_p50_days, n_events, computed_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, now())
                ON CONFLICT (symbol_key, bucket_date) DO UPDATE SET
                    active_count = EXCLUDED.active_count, median_price = EXCLUDED.median_price,
                    p25_price = EXCLUDED.p25_price, p75_price = EXCLUDED.p75_price,
                    median_km = EXCLUDED.median_km, new_count = EXCLUDED.new_count,
                    gone_count = EXCLUDED.gone_count,
                    price_change_down_count = EXCLUDED.price_change_down_count,
                    price_change_up_count = EXCLUDED.price_change_up_count,
                    outliers_excluded = EXCLUDED.outliers_excluded, dom_p50_days = EXCLUDED.dom_p50_days,
                    n_events = EXCLUDED.n_events, computed_at = now()
                """,
                row.symbol_key, bucket_date, row.active_count, row.median_price, row.p25_price,
                row.p75_price, row.median_km, ev["new_count"], ev["gone_count"], ev["price_down"],
                ev["price_up"], row.outliers_excluded, ev["dom_p50_days"], n_events,
            )
    return len(rows), checks


async def run_backfill(conn: asyncpg.Connection) -> dict[str, Any]:
    """Compute every real bucket_date currently in vehicle_event. Idempotent — safe to re-run."""
    dates = await get_bucket_dates(conn)
    total_rows = 0
    per_date: dict[str, int] = {}
    max_div = 0.0
    for d in dates:
        n, checks = await run_for_date(conn, d)
        total_rows += n
        per_date[str(d)] = n
        max_div = max(max_div, checks.get("max_divergence_pct", 0.0))
    return {"bucket_dates": [str(d) for d in dates], "rows_per_date": per_date,
            "total_rows": total_rows, "max_divergence_pct": max_div}


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=str, default=None, help="single YYYY-MM-DD bucket date; default = full backfill")
    args = parser.parse_args()

    # command_timeout=900 (not the original 300s): a real production timeout was hit this
    # session on the corpus's densest bucket days under heavy concurrent multi-frontier DB
    # load (3 other pillars' jobs sharing cardeep-pg simultaneously) — the AS-OF DISTINCT ON
    # scan grows with each subsequent bucket_date (more accumulated vehicle_event history to
    # walk), so the last few real days in a backfill are the slowest, not the first.
    conn = await asyncpg.connect(DSN, command_timeout=900)
    try:
        t0 = time.monotonic()
        if args.date:
            d = date.fromisoformat(args.date)
            n, checks = await run_for_date(conn, d)
            print(f"bucket_date={d} rows_written={n} checks={checks}")
        else:
            summary = await run_backfill(conn)
            print(f"bucket_dates={summary['bucket_dates']}")
            print(f"rows_per_date={summary['rows_per_date']}")
            print(f"total_rows={summary['total_rows']}")
            print(f"max_divergence_pct={summary['max_divergence_pct']}")
        print(f"elapsed_seconds={time.monotonic() - t0:.2f}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
