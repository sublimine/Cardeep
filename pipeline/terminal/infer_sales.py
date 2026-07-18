"""pipeline/terminal/infer_sales.py — 09-trading-terminal Fase 4: "venta probable" inference.

Populates market_sale_inference (migrations/0090). CONSUMES pipeline/identity/link_lifetimes.py's
served output (v_vehicle_lifetime) per 00-MASTER.md resolution C-9 — this job does NOT build its
own reappearance heuristic over vehicle_cluster (the carta's original, now-superseded design); it
queries the SAME view 02-history-reports serves from, and its own confidence formula caps itself
low precisely BECAUSE that engine currently has near-zero real coverage (verified live this
session — see migrations/0090's header for the exact measurement: 12,526 VIN candidate pairs, 0
survive the resolver's anti-FP guards, v_vehicle_lifetime is empty).

Idempotent: a full re-run recomputes every candidate row from scratch and upserts by vehicle_ulid
(PG MVCC doctrine: no need for a run+gate table here — unlike market_bucket_daily, this table has
no historical time axis to preserve; each row IS the current best-known inference for that
vehicle, superseded in place as evidence improves, e.g. once 02's engine gains real edges).
"""
from __future__ import annotations

import argparse
import asyncio
import os
import time
from typing import Any

import asyncpg

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# Price-band for "probable_sale" (carta §4 C5: "ultimo precio dentro de +/-25% de la mediana").
PRICE_BAND_PCT = 0.25

# Confidence ladder — declared, ordinal (no ground-truth outcome data exists yet to calibrate
# against, same doctrine as link_lifetimes.py's own _PROB_* constants: §8 of the pillar letter
# forbids inventing a synthetic score without ground truth). Re-calibrate once V4's N>=50 manual
# audit sample produces a measured false-positive rate.
CONFIDENCE_RELISTED = 0.90              # a real lifetime_link edge is fairly direct evidence
CONFIDENCE_PROBABLE_SALE_NO_SIGNAL = 0.55   # lifetime_link engine has 0 corpus-wide edges today
CONFIDENCE_PROBABLE_SALE_WITH_SIGNAL = 0.80  # once the engine has ANY real edges (future state)
CONFIDENCE_DELISTED = 0.30               # gone, no reappearance found, price doesn't fit market


async def _lifetime_link_total_edges(conn: asyncpg.Connection) -> int:
    """Global coverage check — see module docstring. Queried FRESH every run (never cached):
    the whole point is that this number should start moving as 02-F1/04-F6 land more identity
    signal, and this job's confidence must react automatically, not via a hardcoded assumption."""
    exists = await conn.fetchval("SELECT to_regclass('v_vehicle_lifetime') IS NOT NULL")
    if not exists:
        return 0
    return await conn.fetchval("SELECT count(*) FROM v_vehicle_lifetime")


_CANDIDATES_SQL = """
SELECT v.vehicle_ulid, v.make, v.model, v.price, v.km, v.last_seen AS gone_at,
       e.province_code
  FROM vehicle v
  JOIN entity e ON e.entity_ulid = v.entity_ulid
 WHERE v.status = 'gone'
   AND v.make IS NOT NULL AND v.model IS NOT NULL AND v.price IS NOT NULL
"""


async def _symbol_medians(conn: asyncpg.Connection) -> dict[tuple[str, str, str | None], tuple[str, float]]:
    """Latest (symbol_key, median_price) per (make, model, province|None), both scopes."""
    rows = await conn.fetch(
        """
        SELECT DISTINCT ON (symbol_key) symbol_key, bucket_date, median_price
          FROM market_bucket_daily
         ORDER BY symbol_key, bucket_date DESC
        """
    )
    by_symbol: dict[str, float | None] = {r["symbol_key"]: r["median_price"] for r in rows}
    out: dict[tuple[str, str, str | None], tuple[str, float]] = {}
    sym_rows = await conn.fetch("SELECT symbol_key, make, model, province_code FROM market_symbol")
    for r in sym_rows:
        median = by_symbol.get(r["symbol_key"])
        if median is not None:
            out[(r["make"], r["model"], r["province_code"])] = (r["symbol_key"], float(median))
    return out


async def _lifetime_link_edge_vehicles(conn: asyncpg.Connection) -> set[str]:
    exists = await conn.fetchval("SELECT to_regclass('v_vehicle_lifetime') IS NOT NULL")
    if not exists:
        return set()
    rows = await conn.fetch("SELECT DISTINCT vehicle_ulid_from FROM v_vehicle_lifetime")
    return {r["vehicle_ulid_from"] for r in rows}


async def run(conn: asyncpg.Connection) -> dict[str, Any]:
    total_edges = await _lifetime_link_total_edges(conn)
    engine_has_signal = total_edges > 0
    relisted_vehicles = await _lifetime_link_edge_vehicles(conn)
    medians = await _symbol_medians(conn)

    candidates = await conn.fetch(_CANDIDATES_SQL)

    rows_to_write: list[tuple] = []
    counts = {"probable_sale": 0, "relisted": 0, "delisted": 0, "skipped_no_symbol": 0}

    for r in candidates:
        vulid = r["vehicle_ulid"]
        key_prov = (r["make"], r["model"], r["province_code"])
        key_nat = (r["make"], r["model"], None)
        symbol_info = medians.get(key_prov) or medians.get(key_nat)
        if symbol_info is None:
            counts["skipped_no_symbol"] += 1
            continue
        symbol_key, median_price = symbol_info
        last_price = float(r["price"])
        price_ratio = last_price / median_price if median_price > 0 else None

        if vulid in relisted_vehicles:
            inference = "relisted"
            confidence = CONFIDENCE_RELISTED
        elif price_ratio is not None and (1 - PRICE_BAND_PCT) <= price_ratio <= (1 + PRICE_BAND_PCT):
            inference = "probable_sale"
            confidence = CONFIDENCE_PROBABLE_SALE_WITH_SIGNAL if engine_has_signal else CONFIDENCE_PROBABLE_SALE_NO_SIGNAL
        else:
            inference = "delisted"
            confidence = CONFIDENCE_DELISTED
        counts[inference] += 1

        evidence = {
            "last_price": last_price,
            "symbol_median": median_price,
            "price_ratio": price_ratio,
            "price_band_pct": PRICE_BAND_PCT,
            "lifetime_link_checked": True,
            "lifetime_link_edge_found": vulid in relisted_vehicles,
            "lifetime_link_total_edges_corpus_wide": total_edges,
            "lifetime_link_coverage": "near_zero" if not engine_has_signal else "partial",
        }
        rows_to_write.append((vulid, symbol_key, r["gone_at"], inference, confidence, evidence))

    # Bulk upsert via executemany — a real performance bug this session's own test run caught:
    # one awaited round-trip INSERT per candidate (potentially hundreds of thousands of gone
    # vehicles matching an active symbol) left a test connection "idle in transaction" for 10+
    # minutes between statements. executemany reuses one prepared statement across all rows in
    # a single batch, the same fix pattern link_lifetimes.py already uses (psycopg2.extras.
    # execute_values) for its own bulk write.
    _UPSERT_SQL = """
        INSERT INTO market_sale_inference
            (vehicle_ulid, symbol_key, gone_at, inference, confidence, evidence, computed_at)
        VALUES ($1, $2, $3, $4, $5, $6::jsonb, now())
        ON CONFLICT (vehicle_ulid) DO UPDATE SET
            symbol_key = EXCLUDED.symbol_key, gone_at = EXCLUDED.gone_at,
            inference = EXCLUDED.inference, confidence = EXCLUDED.confidence,
            evidence = EXCLUDED.evidence, computed_at = now()
    """
    if rows_to_write:
        async with conn.transaction():
            await conn.executemany(
                _UPSERT_SQL,
                [
                    (vulid, symbol_key, gone_at, inference, confidence, _to_jsonb(evidence))
                    for vulid, symbol_key, gone_at, inference, confidence, evidence in rows_to_write
                ],
            )

    return {
        "n_candidates": len(candidates), "n_written": len(rows_to_write),
        "lifetime_link_total_edges": total_edges, "engine_has_signal": engine_has_signal,
        "counts": counts,
    }


def _to_jsonb(obj: Any) -> str:
    import json
    return json.dumps(obj)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    conn = await asyncpg.connect(DSN, command_timeout=600)  # margin for shared-DB contention, see compute_buckets.py's own note
    try:
        t0 = time.monotonic()
        summary = await run(conn)
        print(f"n_candidates={summary['n_candidates']}")
        print(f"n_written={summary['n_written']}")
        print(f"lifetime_link_total_edges={summary['lifetime_link_total_edges']} engine_has_signal={summary['engine_has_signal']}")
        print(f"counts={summary['counts']}")
        print(f"elapsed_seconds={time.monotonic() - t0:.2f}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
