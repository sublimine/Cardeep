"""pipeline/arbitrage/geo.py — geo-arbitrage job (04-arbitrage.md F5).

Celda = (make, model, year-band de 2 años, province_code), single-tier minimum n>=15
(§4.4 — "paralelo del Tier-A", no Tier-B fallback for geo cells: a province+model
combination too thin to reach 15 simply never gets a cell, no fallback aggregation).

Gap significance (§4.4): a gap between province A and B for the SAME cohort is only
shown if BOTH cells clear n>=15 AND the median gap exceeds 1.5x the combined
uncertainty. DIMENSIONAL JUDGMENT CALL (declared, not hidden): the carta's literal
formula (``|mediana_A - mediana_B| > 1.5 * sqrt(MAD_A^2 + MAD_B^2) * 1.4826``) mixes
a euro-domain median difference with what would otherwise be an ln-domain MAD unless
converted — this job converts each cell's ln-domain MAD to an approximate EURO-scale
sigma (``sigma_eur = median_price * mad_ln_price * 1.4826``, the standard
relative-volatility-to-absolute-scale approximation for small ln deviations) before
comparing, so both sides of the inequality are in euros. The 1.5 factor and MAD_FLOOR
guard from the shared cohort primitive still apply.
"""
from __future__ import annotations

import argparse
import asyncio
import math
import os
import time
from typing import Any

import asyncpg

from pipeline.gestionador.cohorts import COHORT_MAD_FLOOR
from pipeline.ids import ulid
from pipeline.market.cohort import divergence_pct, median

METHODOLOGY_VERSION = "v1"

GEO_CELL_MIN_N: int = 15          # §4.4: "Mínimo por celda: n>=15 listados servables"
GEO_GAP_SIGNIFICANCE_FACTOR: float = 1.5   # §4.4: gap must exceed 1.5x combined uncertainty

CROSSCHECK_SAMPLE_SIZE: int = 20
CROSSCHECK_TOLERANCE_PCT: float = 0.5


def _make_filter_clause(make_filter: list[str] | None, param_idx: int) -> tuple[str, list[Any]]:
    if not make_filter:
        return "", []
    return f" AND sv.make = ANY(${param_idx}::text[])", [list(make_filter)]


async def fetch_geo_cells(
    conn: asyncpg.Connection, *, make_filter: list[str] | None = None
) -> list[dict[str, Any]]:
    """One row per (country, make, model, year_band_start, province_code) with n>=15."""
    clause, params = _make_filter_clause(make_filter, 1)
    sql = f"""
        WITH cell AS (
            SELECT e.country_code, sv.make, sv.model, (sv.year - (sv.year % 2)) AS year_band_start,
                   e.province_code, ln(sv.price::float8) AS lp, sv.price::float8 AS price
              FROM servable_vehicle sv
              JOIN entity e ON e.entity_ulid = sv.entity_ulid
             WHERE sv.price IS NOT NULL AND sv.price > 0
               AND sv.make IS NOT NULL AND sv.model IS NOT NULL AND sv.year IS NOT NULL
               AND e.province_code IS NOT NULL{clause}
        ),
        agg AS (
            SELECT country_code, make, model, year_band_start, province_code, count(*) AS n,
                   percentile_cont(0.5) WITHIN GROUP (ORDER BY lp)    AS med_lp,
                   percentile_cont(0.5) WITHIN GROUP (ORDER BY price) AS med_price
              FROM cell
             GROUP BY country_code, make, model, year_band_start, province_code
            HAVING count(*) >= {GEO_CELL_MIN_N}
        ),
        mad AS (
            SELECT a.country_code, a.make, a.model, a.year_band_start, a.province_code,
                   a.n, a.med_lp, a.med_price,
                   percentile_cont(0.5) WITHIN GROUP (ORDER BY abs(c.lp - a.med_lp)) AS mad_lp
              FROM cell c
              JOIN agg a ON c.country_code = a.country_code AND c.make = a.make AND c.model = a.model
                        AND c.year_band_start = a.year_band_start AND c.province_code = a.province_code
             GROUP BY a.country_code, a.make, a.model, a.year_band_start, a.province_code,
                      a.n, a.med_lp, a.med_price
        )
        SELECT * FROM mad WHERE mad_lp >= {COHORT_MAD_FLOOR}
    """
    rows = await conn.fetch(sql, *params)
    return [
        {
            "country_code": r["country_code"], "make": r["make"], "model": r["model"],
            "year_band_start": r["year_band_start"], "province_code": r["province_code"],
            "n": int(r["n"]), "median_ln_price": float(r["med_lp"]),
            "mad_ln_price": float(r["mad_lp"]), "median_price": float(r["med_price"]),
        }
        for r in rows
    ]


def compute_geo_gaps(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pure-Python pairing of cells within the SAME cohort (§4.4) — cheap combinatorics
    (at most ~52 provinces per cohort), no need for a second SQL round-trip."""
    by_cohort: dict[tuple, list[dict[str, Any]]] = {}
    for c in cells:
        key = (c["country_code"], c["make"], c["model"], c["year_band_start"])
        by_cohort.setdefault(key, []).append(c)

    gaps: list[dict[str, Any]] = []
    for _cohort_key, cohort_cells in by_cohort.items():
        for i in range(len(cohort_cells)):
            for j in range(i + 1, len(cohort_cells)):
                a, b = cohort_cells[i], cohort_cells[j]
                sigma_a = a["median_price"] * a["mad_ln_price"] * 1.4826
                sigma_b = b["median_price"] * b["mad_ln_price"] * 1.4826
                threshold = GEO_GAP_SIGNIFICANCE_FACTOR * math.sqrt(sigma_a**2 + sigma_b**2)
                gap = abs(a["median_price"] - b["median_price"])
                if gap <= threshold:
                    continue
                cheap, expensive = (a, b) if a["median_price"] <= b["median_price"] else (b, a)
                gaps.append({
                    "country_code": cheap["country_code"], "make": cheap["make"], "model": cheap["model"],
                    "year_band_start": cheap["year_band_start"],
                    "province_cheap": cheap["province_code"], "province_expensive": expensive["province_code"],
                    "median_cheap": cheap["median_price"], "median_expensive": expensive["median_price"],
                    "gap_eur": expensive["median_price"] - cheap["median_price"],
                    "n_cheap": cheap["n"], "n_expensive": expensive["n"],
                })
    return gaps


async def _crosscheck_cells(conn: asyncpg.Connection, cells: list[dict[str, Any]]) -> dict[str, Any]:
    """Fresh raw-fetch + pure-Python recompute of a sample of cells (§7)."""
    if not cells:
        return {"sampled": 0, "passed": True, "max_divergence_pct": 0.0, "segments": []}
    sample = sorted(cells, key=lambda c: c["n"], reverse=True)[:CROSSCHECK_SAMPLE_SIZE]
    max_div = 0.0
    segments = []
    for c in sample:
        raw = await conn.fetch(
            """
            SELECT ln(sv.price::float8) AS lp
              FROM servable_vehicle sv JOIN entity e ON e.entity_ulid = sv.entity_ulid
             WHERE e.country_code = $1 AND sv.make = $2 AND sv.model = $3
               AND (sv.year - (sv.year % 2)) = $4 AND e.province_code = $5
               AND sv.price IS NOT NULL AND sv.price > 0
            """,
            c["country_code"], c["make"], c["model"], c["year_band_start"], c["province_code"],
        )
        lps = sorted(float(r["lp"]) for r in raw)
        py_n = len(lps)
        py_med = median(lps) if lps else 0.0
        d_n = divergence_pct(py_n, c["n"])
        d_med = divergence_pct(py_med, c["median_ln_price"])
        seg_max = max(d_n, d_med)
        max_div = max(max_div, seg_max)
        segments.append({"make": c["make"], "model": c["model"], "province": c["province_code"],
                          "divergence_pct": round(seg_max, 4)})
    return {"sampled": len(sample), "passed": max_div < CROSSCHECK_TOLERANCE_PCT,
            "max_divergence_pct": round(max_div, 4), "segments": segments}


async def run_geo(
    conn: asyncpg.Connection, *, make_filter: list[str] | None = None
) -> tuple[str, dict[str, Any]]:
    """Compute one full geo-arbitrage run: geo_price_cell + geo_price_gap, INSERT-only.

    Never sets published=TRUE (mirrors F1/F4's contract). Raises RuntimeError (run row
    still written for audit) if the dual-path cross-check fails.
    """
    t0 = time.monotonic()
    cells = await fetch_geo_cells(conn, make_filter=make_filter)
    gaps = compute_geo_gaps(cells)
    checks = await _crosscheck_cells(conn, cells)
    checks["elapsed_seconds"] = round(time.monotonic() - t0, 2)

    run_id = ulid()
    async with conn.transaction():
        await conn.execute(
            "INSERT INTO arbitrage_geo_run (run_id, methodology_version, n_cells, n_gaps, checks) "
            "VALUES ($1,$2,$3,$4,$5::jsonb)",
            run_id, METHODOLOGY_VERSION, len(cells), len(gaps), _to_jsonb(checks),
        )
        if cells:
            await conn.executemany(
                "INSERT INTO geo_price_cell (run_id, country_code, make, model, year_band_start, "
                "province_code, n, median_ln_price, mad_ln_price, median_price) "
                "VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)",
                [
                    (run_id, c["country_code"], c["make"], c["model"], c["year_band_start"],
                     c["province_code"], c["n"], c["median_ln_price"], c["mad_ln_price"], round(c["median_price"], 2))
                    for c in cells
                ],
            )
        if gaps:
            await conn.executemany(
                "INSERT INTO geo_price_gap (run_id, country_code, make, model, year_band_start, "
                "province_cheap, province_expensive, median_cheap, median_expensive, gap_eur, "
                "n_cheap, n_expensive) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)",
                [
                    (run_id, g["country_code"], g["make"], g["model"], g["year_band_start"],
                     g["province_cheap"], g["province_expensive"], round(g["median_cheap"], 2),
                     round(g["median_expensive"], 2), round(g["gap_eur"], 2), g["n_cheap"], g["n_expensive"])
                    for g in gaps
                ],
            )

    if not checks["passed"]:
        raise RuntimeError(
            f"arbitrage geo run {run_id}: dual-path cross-check FAILED "
            f"(max_divergence={checks['max_divergence_pct']}%). Run row written for audit; NOT usable."
        )

    return run_id, checks


def _to_jsonb(obj: Any) -> str:
    import json
    return json.dumps(obj)


async def _main() -> None:
    parser = argparse.ArgumentParser(description="04-arbitrage F5 geo-arbitrage job")
    parser.parse_args()
    dsn = os.environ.get("CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep")
    conn = await asyncpg.connect(dsn)
    try:
        run_id, checks = await run_geo(conn)
        print(f"geo run {run_id}: {checks['sampled']} cells crosschecked, "
              f"max_divergence={checks['max_divergence_pct']}%, passed={checks['passed']}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(_main())
