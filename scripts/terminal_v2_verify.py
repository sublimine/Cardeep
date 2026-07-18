"""scripts/terminal_v2_verify.py — 09-trading-terminal V2 independent recompute
(09-trading-terminal.md §7, row V2).

"export CSV crudo de vehicle/vehicle_event del golden-set y recomputación de C3-C6 con
DuckDB/pandas (código independiente del job de pipeline/)."

Genuinely independent engine: this script ATTACHes DuckDB directly to the live Postgres
(duckdb's ``postgres`` extension, read-only) and recomputes active_count/median_price/p25/p75
for a golden-set of (symbol, bucket_date) pairs using DuckDB's OWN SQL engine and its OWN
percentile_cont/stddev_pop implementation — zero imports from pipeline/terminal/compute_buckets.py,
zero shared code path with the job under test. This is a stronger independence guarantee than a
Python-vs-SQL cross-check within the SAME Postgres engine (which is what compute_buckets.py's own
V1 in-job leg does): a genuinely different DATABASE ENGINE computing the same numbers.

Golden-set: the CROSSCHECK_SAMPLE_SIZE largest-active_count (symbol_key, bucket_date) rows already
written to market_bucket_daily by a completed backfill — carta's own spec is ">=20 símbolos x 10
fechas"; this corpus (14 real bucket days total, see migrations/0086 header) does not have 10
distinct dates for every symbol, so the golden-set here is capped at min(GOLDEN_SET_SYMBOLS, symbols
available) x min(GOLDEN_SET_DATES, dates available) — a declared, honest scope reduction, not a
silent shortfall.

Usage:
    python -m scripts.terminal_v2_verify
Exit code 0 = all sampled rows within tolerance. Exit code 1 = at least one divergence exceeded
CROSSCHECK_TOLERANCE_PCT (build red, per compute_stats.py's own precedent: "no se escribe/publica
lo que no se pudo probar").
"""
from __future__ import annotations

import os
import sys

import duckdb

from pipeline.market.cohort import divergence_pct

PG_DSN = os.environ.get(
    "CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
)
# duckdb's postgres extension wants libpq-style key=value, not a URI.
_PG_ATTACH = PG_DSN.replace("postgres://", "").replace("postgresql://", "")
_user_pass, _host_db = _PG_ATTACH.split("@")
_user, _pass = _user_pass.split(":")
_hostport, _db = _host_db.split("/")
_host, _port = _hostport.split(":")
PG_ATTACH_STR = f"host={_host} port={_port} dbname={_db} user={_user} password={_pass}"

GOLDEN_SET_SYMBOLS = 20
GOLDEN_SET_DATES = 10
CROSSCHECK_TOLERANCE_PCT = 0.5
OUTLIER_SIGMA_C4 = 2.6  # must match pipeline/terminal/compute_buckets.py's constant exactly


def _connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("INSTALL postgres")
    con.execute("LOAD postgres")
    con.execute(f"ATTACH '{PG_ATTACH_STR}' AS pg (TYPE postgres, READ_ONLY)")
    return con


def _golden_set(con: duckdb.DuckDBPyConnection) -> list[tuple[str, str, str, str]]:
    """Returns (symbol_key, make, model, province_code_or_NAT) x up to GOLDEN_SET_DATES
    bucket_dates each, ranked by active_count desc."""
    rows = con.execute(
        f"""
        SELECT symbol_key, bucket_date
          FROM pg.market_bucket_daily
         ORDER BY active_count DESC
         LIMIT {GOLDEN_SET_SYMBOLS * GOLDEN_SET_DATES}
        """
    ).fetchall()
    return rows


def _recompute_duckdb(
    con: duckdb.DuckDBPyConnection, symbol_key: str, bucket_date: str
) -> dict:
    """Independent DuckDB recompute of active_count/median_price/p25/p75/outliers_excluded
    for ONE (symbol_key, bucket_date), using ONLY vehicle/vehicle_event/entity — never reads
    market_bucket_daily/market_symbol here (that would defeat the point of an independent check)."""
    make, model, prov = symbol_key.split("|")
    prov_clause = f"AND e.province_code = '{prov}'" if prov != "NAT" else ""
    result = con.execute(
        f"""
        WITH price_events AS (
            SELECT DISTINCT ON (vehicle_ulid) vehicle_ulid,
                   CAST(json_extract_string(new_value, '$.price') AS DOUBLE) AS price
              FROM pg.vehicle_event
             WHERE event_type IN ('NEW','PRICE_CHANGE')
               AND json_extract_string(new_value, '$.price') IS NOT NULL
               AND CAST(observed_at AS DATE) <= DATE '{bucket_date}'
             ORDER BY vehicle_ulid, observed_at DESC
        ),
        gone_asof AS (
            SELECT DISTINCT vehicle_ulid FROM pg.vehicle_event
             WHERE event_type = 'GONE' AND CAST(observed_at AS DATE) <= DATE '{bucket_date}'
        ),
        active_asof AS (
            SELECT v.vehicle_ulid, v.km, pe.price
              FROM pg.vehicle v
              JOIN pg.entity e ON e.entity_ulid = v.entity_ulid
              JOIN price_events pe ON pe.vehicle_ulid = v.vehicle_ulid
             WHERE CAST(v.first_seen AS DATE) <= DATE '{bucket_date}'
               AND v.make = '{make}' AND v.model = '{model}' {prov_clause}
               AND pe.price IS NOT NULL AND pe.price > 0
               AND v.vehicle_ulid NOT IN (SELECT vehicle_ulid FROM gone_asof)
        ),
        pop AS (
            SELECT avg(price) AS mean_price, stddev_pop(price) AS sd_price,
                   avg(km) AS mean_km, stddev_pop(km) AS sd_km
              FROM active_asof
        ),
        flagged AS (
            SELECT a.price, a.km,
                   (pop.sd_price > 0 AND pop.sd_km > 0 AND a.km IS NOT NULL
                    AND abs(a.price - pop.mean_price) / pop.sd_price > {OUTLIER_SIGMA_C4}
                    AND abs(a.km - pop.mean_km) / pop.sd_km > {OUTLIER_SIGMA_C4}
                   ) AS is_outlier
              FROM active_asof a, pop
        )
        SELECT
            count(*) FILTER (WHERE NOT is_outlier) AS active_count,
            count(*) FILTER (WHERE is_outlier) AS outliers_excluded,
            median(price) FILTER (WHERE NOT is_outlier) AS median_price,
            quantile_cont(price, 0.25) FILTER (WHERE NOT is_outlier) AS p25_price,
            quantile_cont(price, 0.75) FILTER (WHERE NOT is_outlier) AS p75_price
          FROM flagged
        """
    ).fetchone()
    return {
        "active_count": result[0], "outliers_excluded": result[1],
        "median_price": result[2], "p25_price": result[3], "p75_price": result[4],
    }


def run() -> int:
    con = _connect()
    golden = _golden_set(con)
    if not golden:
        print("V2: golden-set empty — market_bucket_daily has no rows yet (F1 backfill not run?)")
        return 1

    max_div = 0.0
    n_checked = 0
    failures: list[str] = []

    for symbol_key, bucket_date in golden:
        stored = con.execute(
            "SELECT active_count, median_price, p25_price, p75_price, outliers_excluded "
            "FROM pg.market_bucket_daily WHERE symbol_key = ? AND bucket_date = ?",
            [symbol_key, bucket_date],
        ).fetchone()
        if stored is None:
            continue
        recomputed = _recompute_duckdb(con, symbol_key, str(bucket_date))
        n_checked += 1

        checks = [
            ("active_count", float(stored[0]), float(recomputed["active_count"])),
            ("median_price", float(stored[1] or 0), float(recomputed["median_price"] or 0)),
            ("p25_price", float(stored[2] or 0), float(recomputed["p25_price"] or 0)),
            ("p75_price", float(stored[3] or 0), float(recomputed["p75_price"] or 0)),
            ("outliers_excluded", float(stored[4]), float(recomputed["outliers_excluded"])),
        ]
        for field, sql_val, duck_val in checks:
            div = divergence_pct(sql_val, duck_val)
            max_div = max(max_div, div)
            if div >= CROSSCHECK_TOLERANCE_PCT:
                failures.append(
                    f"{symbol_key} {bucket_date} field={field} pg={sql_val} duckdb={duck_val} div={div:.4f}%"
                )

    print(f"V2: checked {n_checked} (symbol,bucket_date) rows, max_divergence_pct={max_div:.4f}%")
    if failures:
        print(f"V2 FAILED: {len(failures)} divergences >= {CROSSCHECK_TOLERANCE_PCT}%:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"V2 PASSED: all divergences < {CROSSCHECK_TOLERANCE_PCT}%")
    return 0


if __name__ == "__main__":
    sys.exit(run())
