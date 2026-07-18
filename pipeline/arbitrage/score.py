"""pipeline/arbitrage/score.py — deal-score batch job (04-arbitrage.md F1).

Computes ``cohort_stats`` + ``deal_score`` for the ``servable_vehicle`` universe
(hygiene-cleared: excludes price_trap-quarantined vehicles, per §4.1 "un vehículo
flaggeado por detect_price_trap NUNCA es chollo") using the shared cohort robust-z
primitive (pipeline/gestionador/cohorts.py) — the SAME statistical machine
``detect_price_trap`` uses for hygiene, reinterpreted for opportunity (00-MASTER.md
C-1/C-12: one cohort implementation, not a second divergent one).

Bands (§4.1, anchored on the Iglewicz & Hoaglin modified z-score, |z|>3.5 outlier /
[2,3.5] borderline — structurally identical to price_trap's own robust-z):
    z <= -PRICE_TRAP_COHORT_Z (-6.0)   -> NOT a chollo, price_trap territory (excluded)
    -6.0 < z <= -3.5                    -> 'chollo_fuerte'
    -3.5 < z <= -2.0                    -> 'bajo_mercado'
    z > -2.0                            -> not a candidate, not written

Only badged candidates are written to ``deal_score`` (not every servable vehicle) —
the table would otherwise carry a row for 2M+ vehicles per run for zero product
benefit; only rows a dealer could act on matter (04-arbitrage.md §5.2 table + this
job's own scoping decision, documented here since the carta did not pin an exact row
count).

Verification protocol (§7 row 1, "Mediana/MAD de cohorte"): ``crosscheck_cohort_stats``
independently recomputes a sample of >=20 cohorts via a FRESH raw fetch + pure-Python
median/MAD (reusing ``pipeline.market.cohort.median`` — 00-MASTER.md C-1, one
percentile implementation project-wide) and compares against the SQL-computed values
written by this job. Discrepancy > 0.5% on any sampled cohort fails the run: the run
row is still written (audit trail) but ``published`` stays FALSE and the caller must
raise (mirrors ``compute_stats.py``'s F1 contract for 01-market-intelligence).

Publish gate: this module NEVER sets published=TRUE — that is a human/F2 decision
(mirrors compute_stats.py's F1 contract). The API (F2) serves the latest run
unconditionally on ``published`` because 04, unlike 01, has no run-over-run
volatility gate yet; this is declared, not hidden (see services/api/routers/arbitrage.py).
"""
from __future__ import annotations

import argparse
import asyncio
import os
import time
from typing import Any

import asyncpg

from pipeline.gestionador.cohorts import CohortScoredVehicle, fetch_cohort_scored
from pipeline.gestionador.detect import PRICE_TRAP_COHORT_Z
from pipeline.ids import ulid
from pipeline.market.cohort import divergence_pct, median

METHODOLOGY_VERSION = "v1"

DEAL_SCORE_CHOLLO_FUERTE_Z: float = -3.5
DEAL_SCORE_BAJO_MERCADO_Z: float = -2.0
# The frontier shared with price_trap's quarantine threshold (§4.1: "Frontera compartida
# con PRICE_TRAP_COHORT_Z"). Defense-in-depth: servable_vehicle already excludes vehicles
# gestion_item has quarantined, but a vehicle can score z<=-6 in THIS job's own cohort
# pass (a different population than price_trap's) before price_trap's own next run catches
# it — this floor guarantees the frontier holds regardless of cadence skew between jobs.
DEAL_SCORE_FLOOR_Z: float = -PRICE_TRAP_COHORT_Z

CROSSCHECK_SAMPLE_SIZE: int = 20
CROSSCHECK_TOLERANCE_PCT: float = 0.5

_SERVABLE_BASE_SELECT: str = (
    "SELECT sv.vehicle_ulid, sv.price, sv.make, sv.model, sv.year, e.country_code "
    "FROM servable_vehicle sv JOIN entity e ON e.entity_ulid = sv.entity_ulid"
)
_SERVABLE_BASE_SELECT_FILTERED: str = _SERVABLE_BASE_SELECT + " WHERE sv.make = ANY($4::text[])"


def band_for_z(z: float) -> str | None:
    """Deal-score band for a cohort z-score, or None if not a chollo candidate (§4.1)."""
    if z <= DEAL_SCORE_FLOOR_Z:
        return None
    if z <= DEAL_SCORE_CHOLLO_FUERTE_Z:
        return "chollo_fuerte"
    if z <= DEAL_SCORE_BAJO_MERCADO_Z:
        return "bajo_mercado"
    return None


class _CohortKey:
    """Hashable (country, make, model, year) cohort identity."""
    __slots__ = ("country_code", "make", "model", "year")

    def __init__(self, country_code: str, make: str, model: str | None, year: int) -> None:
        self.country_code = country_code
        self.make = make
        self.model = model
        self.year = year

    def __hash__(self) -> int:
        return hash((self.country_code, self.make, self.model, self.year))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _CohortKey) and (
            self.country_code, self.make, self.model, self.year
        ) == (other.country_code, other.make, other.model, other.year)


async def fetch_scored(
    conn: asyncpg.Connection, *, make_filter: list[str] | None = None
) -> list[CohortScoredVehicle]:
    """The servable-vehicle cohort pass — deal-score's universe (§4.1).

    *make_filter* scopes the scan to specific makes (mirrors
    ``pipeline.market.compute_stats.fetch_m1``'s ``make_filter`` — used by tests to
    run against a synthetic slice in milliseconds instead of the full multi-million-row
    servable_vehicle population).
    """
    if make_filter:
        return await fetch_cohort_scored(
            conn, base_select_sql=_SERVABLE_BASE_SELECT_FILTERED, base_params=(list(make_filter),)
        )
    return await fetch_cohort_scored(conn, base_select_sql=_SERVABLE_BASE_SELECT)


async def crosscheck_cohort_stats(
    conn: asyncpg.Connection, cohorts: list[dict[str, Any]]
) -> dict[str, Any]:
    """Independent SQL-raw-fetch + pure-Python recompute of a sample of cohorts (§7 row 1).

    Mirrors ``pipeline/market/compute_stats.py::crosscheck_m1``: for each of the
    largest-n sampled cohorts, refetch the RAW ln(price) list directly from
    servable_vehicle (bypassing the job's own CTE chain entirely), recompute
    median+MAD in pure Python via the SAME canonical percentile helper
    01-market-intelligence factored (``pipeline.market.cohort.median`` — C-1: one
    percentile implementation, not a second divergent one), and compare.
    """
    if not cohorts:
        return {"sampled": 0, "passed": True, "max_divergence_pct": 0.0,
                "segments": [], "tolerance_pct": CROSSCHECK_TOLERANCE_PCT}

    sample = sorted(cohorts, key=lambda c: c["n"], reverse=True)[:CROSSCHECK_SAMPLE_SIZE]
    segments: list[dict[str, Any]] = []
    max_div = 0.0

    for c in sample:
        raw = await conn.fetch(
            """
            SELECT ln(sv.price::float8) AS lp
              FROM servable_vehicle sv
              JOIN entity e ON e.entity_ulid = sv.entity_ulid
             WHERE e.country_code = $1 AND sv.make = $2
               AND sv.model IS NOT DISTINCT FROM $3
               AND sv.year = $4
               AND sv.price IS NOT NULL AND sv.price > 0
            """,
            c["country_code"], c["make"], c["model"], c["year"],
        )
        lps = sorted(float(r["lp"]) for r in raw)
        py_n = len(lps)
        py_med_lp = median(lps) if lps else 0.0
        py_mad_lp = median(sorted(abs(x - py_med_lp) for x in lps)) if lps else 0.0

        div_n = divergence_pct(py_n, c["n"])
        div_med = divergence_pct(py_med_lp, c["median_ln_price"])
        div_mad = divergence_pct(py_mad_lp, c["mad_ln_price"])
        seg_max = max(div_n, div_med, div_mad)
        max_div = max(max_div, seg_max)

        segments.append({
            "country_code": c["country_code"], "make": c["make"], "model": c["model"],
            "year": c["year"],
            "sql": {"n": c["n"], "median_ln_price": c["median_ln_price"], "mad_ln_price": c["mad_ln_price"]},
            "python": {"n": py_n, "median_ln_price": py_med_lp, "mad_ln_price": py_mad_lp},
            "divergence_pct": round(seg_max, 4),
        })

    return {
        "sampled": len(sample),
        "passed": max_div < CROSSCHECK_TOLERANCE_PCT,
        "max_divergence_pct": round(max_div, 4),
        "tolerance_pct": CROSSCHECK_TOLERANCE_PCT,
        "segments": segments,
    }


async def run_score(
    conn: asyncpg.Connection, *, make_filter: list[str] | None = None
) -> tuple[str, dict[str, Any]]:
    """Compute one full deal-score run: cohort_stats + deal_score rows, INSERT-only.

    Returns (run_id, checks). Raises RuntimeError (run row still written, for audit)
    if the dual-path cross-check fails — the caller must not treat that run as usable.
    Never sets published=TRUE (DB default FALSE) — mirrors compute_stats.py's F1 gate.
    """
    t0 = time.monotonic()
    scored = await fetch_scored(conn, make_filter=make_filter)

    cohorts_seen: dict[_CohortKey, dict[str, Any]] = {}
    for row in scored:
        key = _CohortKey(row.country_code, row.make, row.model, row.year)
        if key not in cohorts_seen:
            cohorts_seen[key] = {
                "country_code": row.country_code, "make": row.make, "model": row.model,
                "year": row.year, "tier": "B" if row.tier_b else "A", "n": row.n,
                "median_ln_price": row.med_lp, "mad_ln_price": row.mad_lp,
                "median_price": row.med_price,
            }

    deals: list[tuple] = []
    run_id = ulid()
    for row in scored:
        band = band_for_z(row.z)
        if band is None:
            continue
        savings = row.med_price - row.price
        deals.append((
            run_id, row.vehicle_ulid, row.z, band, round(savings, 2),
            row.make, row.model, row.year, "B" if row.tier_b else "A",
            row.n, round(row.med_price, 2),
        ))

    checks = await crosscheck_cohort_stats(conn, list(cohorts_seen.values()))
    checks["elapsed_seconds"] = round(time.monotonic() - t0, 2)

    async with conn.transaction():
        await conn.execute(
            "INSERT INTO arbitrage_run (run_id, methodology_version, n_in, n_cohorts, n_deals, checks) "
            "VALUES ($1, $2, $3, $4, $5, $6::jsonb)",
            run_id, METHODOLOGY_VERSION, len(scored), len(cohorts_seen), len(deals),
            _to_jsonb(checks),
        )
        if cohorts_seen:
            await conn.executemany(
                "INSERT INTO cohort_stats (run_id, country_code, make, model, year, tier, n, "
                "median_ln_price, mad_ln_price, median_price) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)",
                [
                    (run_id, v["country_code"], v["make"], v["model"], v["year"], v["tier"],
                     v["n"], v["median_ln_price"], v["mad_ln_price"], round(v["median_price"], 2))
                    for v in cohorts_seen.values()
                ],
            )
        if deals:
            await conn.executemany(
                "INSERT INTO deal_score (run_id, vehicle_ulid, z, band, savings_eur, cohort_make, "
                "cohort_model, cohort_year, cohort_tier, cohort_n, cohort_median_price) "
                "VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)",
                deals,
            )

    if not checks["passed"]:
        raise RuntimeError(
            f"arbitrage score run {run_id}: SQL-vs-Python cross-check FAILED — "
            f"max divergence {checks['max_divergence_pct']:.4f}% >= tolerance "
            f"{CROSSCHECK_TOLERANCE_PCT}%. Run row written for audit; NOT usable. Details: {checks}"
        )

    return run_id, checks


def _to_jsonb(obj: Any) -> str:
    import json
    return json.dumps(obj)


async def _main() -> None:
    parser = argparse.ArgumentParser(description="04-arbitrage F1 deal-score job")
    parser.parse_args()
    dsn = os.environ.get("CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep")
    conn = await asyncpg.connect(dsn)
    try:
        run_id, checks = await run_score(conn)
        print(f"arbitrage run {run_id}: {checks['sampled']} cohorts crosschecked, "
              f"max_divergence={checks['max_divergence_pct']}%, passed={checks['passed']}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(_main())
