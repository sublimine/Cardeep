"""Shared cohort robust-z helper — the canonical (make, model, year) median+MAD
primitive on ln(price), factored OUT of detect.py (04-arbitrage.md F1).

00-MASTER.md resolution C-1/C-12: one percentile/cohort implementation project-wide.
``pipeline/market/cohort.py`` already owns the generic percentile/median helper for
01-market-intelligence (window/segment stats over p25/p50/p75). THIS module owns the
distinct primitive both `detect_price_trap` (hygiene: quarantine) and
`pipeline/arbitrage/score.py::compute_deal_scores` (opportunity: chollo) need — a
model-aware, MAD-robust anomaly z-score with a Tier-A/Tier-B fallback and a
near-degenerate-cohort guard (Law I). Two callers, one SQL primitive: neither
re-derives the CTE chain.

Regression safety: `detect_price_trap`'s existing test suite
(tests/test_gestionador.py::TestPriceTrap) mocks `conn.fetch` at the boundary and
never inspects SQL text, so swapping its internal query construction to call through
this module is behavior-preserving BY CONSTRUCTION as long as the returned rows carry
the same columns. Verified live against production `cardeep-pg`: the flagged-vehicle
set (order + count, hashed) is byte-identical before and after this refactor (04-F1
verification log).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import asyncpg

# Cohort guards (04-arbitrage.md §4.1: "Cohorte: idéntica a price_trap"). These were
# PRICE_TRAP_COHORT_MIN_A / PRICE_TRAP_COHORT_MIN_B / PRICE_TRAP_MAD_FLOOR in detect.py;
# moved here as the single source of truth. detect.py re-exports the old names as aliases
# so no external reference breaks.
COHORT_MIN_TIER_A: int = 15   # (make, model, year), n >= this
COHORT_MIN_TIER_B: int = 30   # (make, year) fallback, model NULL, n >= this
COHORT_MAD_FLOOR: float = 0.05  # Law I: skip near-degenerate cohorts (ln-price MAD < 5%)


@dataclass(frozen=True)
class CohortScoredVehicle:
    """One vehicle scored against its own (country, make, model|NULL, year) cohort."""
    vehicle_ulid: str
    price: float
    make: str
    model: str | None
    year: int
    country_code: str
    n: int
    med_price: float
    med_lp: float
    mad_lp: float
    z: float
    tier_b: bool


def cohort_ctes_sql(base_select_sql: str) -> str:
    """Return the ``base``/``med``/``mad``/``scored`` CTE chain (as bare CTE bodies,
    to be embedded after a caller's own ``WITH`` keyword) for *base_select_sql* — a
    full ``SELECT vehicle_ulid, price, make, model, year, country_code FROM ...``
    statement defining the population to cohort-score (e.g. all available vehicles
    for price_trap's hygiene pass, or ``servable_vehicle`` for deal-score's
    hygiene-cleared opportunity universe, per 04-arbitrage.md §4.1).

    Positional params consumed by the returned SQL: $1=min_tier_a, $2=min_tier_b,
    $3=mad_floor. The caller's own final SELECT continues numbering from $4.

    NULL-safe join on ``model`` (``COALESCE(..., '§§NULL§§')``) so the Tier-B
    model-NULL group joins back to itself. Cohort key includes ``country_code`` so a
    second tenant's price distribution never pools into an ES cohort's median/MAD
    (mirrors detect_price_trap's original single-tenant-safe design).
    """
    return f"""
    base AS (
        SELECT vehicle_ulid, price::float8 AS price, ln(price::float8) AS lp,
               make, model, year, country_code
          FROM ({base_select_sql}) src
         WHERE price IS NOT NULL AND price > 0 AND make IS NOT NULL AND year IS NOT NULL
    ),
    med AS (
        SELECT country_code, make, model, year, count(*) AS n,
               percentile_cont(0.5) WITHIN GROUP (ORDER BY lp)    AS med_lp,
               percentile_cont(0.5) WITHIN GROUP (ORDER BY price) AS med_price
          FROM base
         GROUP BY country_code, make, model, year
        HAVING count(*) >= CASE WHEN model IS NOT NULL THEN $1::int ELSE $2::int END
    ),
    mad AS (
        SELECT * FROM (
            SELECT b.country_code, b.make, b.model, b.year, m.n, m.med_lp, m.med_price,
                   percentile_cont(0.5) WITHIN GROUP (ORDER BY abs(b.lp - m.med_lp)) AS mad_lp
              FROM base b
              JOIN med m ON b.country_code = m.country_code AND b.make = m.make AND b.year = m.year
                        AND COALESCE(b.model, '§§NULL§§') = COALESCE(m.model, '§§NULL§§')
             GROUP BY b.country_code, b.make, b.model, b.year, m.n, m.med_lp, m.med_price
        ) q WHERE mad_lp >= $3
    ),
    scored AS (
        SELECT b.vehicle_ulid, b.price, b.make, b.model, b.year, b.country_code,
               mad.n, mad.med_price, mad.med_lp, mad.mad_lp,
               (b.lp - mad.med_lp) / (1.4826 * mad.mad_lp) AS z,
               (mad.model IS NULL) AS tier_b
          FROM base b
          JOIN mad ON b.country_code = mad.country_code AND b.make = mad.make AND b.year = mad.year
                  AND COALESCE(b.model, '§§NULL§§') = COALESCE(mad.model, '§§NULL§§')
    )
    """


async def fetch_cohort_scored(
    conn: asyncpg.Connection,
    *,
    base_select_sql: str,
    base_params: Sequence[Any] = (),
    min_tier_a: int = COHORT_MIN_TIER_A,
    min_tier_b: int = COHORT_MIN_TIER_B,
    mad_floor: float = COHORT_MAD_FLOOR,
) -> list[CohortScoredVehicle]:
    """Cohort robust-z for every vehicle in *base_select_sql*'s population, unfiltered
    by any anomaly threshold — the caller (price_trap for quarantine, deal-score for
    opportunity) applies its OWN z-threshold/band logic on top of this shared primitive.

    *base_params* are extra positional params *base_select_sql* references starting at
    $4 (e.g. a make filter for a fast, scoped test run — $1-$3 are always min_tier_a/
    min_tier_b/mad_floor, consumed by the ``med``/``mad`` CTEs regardless of textual
    position, per asyncpg/Postgres positional-param resolution).
    """
    sql = f"WITH {cohort_ctes_sql(base_select_sql)} SELECT * FROM scored"
    rows = await conn.fetch(sql, min_tier_a, min_tier_b, mad_floor, *base_params)
    return [
        CohortScoredVehicle(
            vehicle_ulid=str(r["vehicle_ulid"]),
            price=float(r["price"]),
            make=r["make"],
            model=r["model"],
            year=r["year"],
            country_code=r["country_code"],
            n=int(r["n"]),
            med_price=float(r["med_price"]),
            med_lp=float(r["med_lp"]),
            mad_lp=float(r["mad_lp"]),
            z=float(r["z"]),
            tier_b=bool(r["tier_b"]),
        )
        for r in rows
    ]
