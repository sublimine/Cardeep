"""/arbitrage/* — deal-score, desync, and methodology endpoints (pilar 04-arbitrage, F2).

Ownership: 00-MASTER.md resolution C-2 assigns ``web/src/pages/Arbitrage.tsx`` and the
whole "chollo" concept to pilar 04 exclusively (01-market-intelligence's M2 is a
DIFFERENT, general price-position signal, never surfaced on this page). This router
owns the ``/arbitrage/*`` namespace the same way ``market.py`` owns ``/market/*``.

Publish gate (declared, not hidden): unlike ``market_stat_run`` (01-market-intelligence,
which gates publication behind a run-over-run ±3% volatility check), ``arbitrage_run``
has no such gate defined by this carta — F1's ``pipeline/arbitrage/score.py`` never
flips ``published`` (mirrors its F1-only contract). This router therefore serves the
LATEST run by ``run_at`` unconditionally; a future phase may add a publish workflow
identical to market's if run-over-run instability is observed in production.

Frescura (anti-Zillow gate, §4.1/§4.2): every deal/desync row is re-verified LIVE
against ``servable_vehicle``/``vehicle.last_seen`` at SERVE time, not run-compute time
— a vehicle quarantined or gone stale after the batch run computed its score is never
served, even if its ``deal_score`` row still exists until the next run purges it.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from pipeline.arbitrage.decay import MIN_CYCLES_PER_COHORT, MIN_OBS_PER_BUCKET
from pipeline.arbitrage.geo import GEO_CELL_MIN_N, GEO_GAP_SIGNIFICANCE_FACTOR
from pipeline.arbitrage.score import (
    DEAL_SCORE_BAJO_MERCADO_Z,
    DEAL_SCORE_CHOLLO_FUERTE_Z,
    DEAL_SCORE_FLOOR_Z,
    METHODOLOGY_VERSION as SCORE_METHODOLOGY_VERSION,
)
from pipeline.gestionador.cohorts import COHORT_MAD_FLOOR, COHORT_MIN_TIER_A, COHORT_MIN_TIER_B
from pipeline.paths import DEFAULT_COUNTRY
from services.api.cache import cache_set, try_cache_get
from services.api.deps import err, ok, page_slice, require_api_key
from services.api.ratelimit import RATE_DEFAULT, RATE_EXPENSIVE, limiter

router = APIRouter()

# §4.1 "Frescura (gate anti-Zillow)": <=72h fully fresh; 72h-7d served with a "sin
# re-verificar" flag; >7d never served, regardless of how recent the scoring run was.
FRESHNESS_FRESH_HOURS: int = 72
FRESHNESS_MAX_DAYS: int = 7

# §4.2 desync predicate thresholds.
DESYNC_MIN_REL: float = 0.01     # >=1%
DESYNC_MIN_ABS_EUR: float = 100  # AND >=100€ (both must hold)


async def _latest_run(conn) -> dict[str, Any] | None:
    row = await conn.fetchrow(
        "SELECT run_id, run_at, methodology_version, n_in, n_cohorts, n_deals, checks, published "
        "FROM arbitrage_run ORDER BY run_at DESC LIMIT 1"
    )
    return dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# GET /arbitrage/summary — the 4 header KPIs (§6 item 1), each traced to its own §4 rule
# ---------------------------------------------------------------------------

@router.get("/arbitrage/summary")
@limiter.limit(RATE_DEFAULT)
async def summary(
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """The 4 "Reposición" header KPIs — every one a live COUNT/median against the DB,
    never a cached literal (§6 item 1 bans "letra pequeña"; the carta bans ANY
    hardcoded business number in the TSX, so this endpoint exists precisely to replace
    the mock's "37" / "€2.140" / "12" literals).

    ``median_days_to_gone``: an UNWEIGHTED median of each cleared cohort's own median
    days-to-GONE (declared approximation — a cycle-weighted global median would need
    re-deriving from raw per-vehicle cycles across every cohort, too expensive for a
    summary card; the per-cohort figure in /arbitrage/time-curves is the exact one).
    ``null`` with a reason when no cohort has cleared the F4 minimum yet.
    """
    async with request.app.state.pool.acquire() as c:
        score_run = await _latest_run(c)
        decay_run = await _latest_decay_run(c)

        chollos_activos = 0
        ahorro_mediano = None
        if score_run is not None:
            row = await c.fetchrow(
                f"""
                SELECT count(*) AS n,
                       percentile_cont(0.5) WITHIN GROUP (ORDER BY ds.savings_eur) AS median_savings
                  FROM deal_score ds
                  JOIN servable_vehicle v ON v.vehicle_ulid = ds.vehicle_ulid
                  JOIN entity e ON e.entity_ulid = v.entity_ulid
                 WHERE ds.run_id = $1 AND e.country_code = $2
                   AND v.last_seen >= now() - interval '{FRESHNESS_MAX_DAYS} days'
                """,
                score_run["run_id"], DEFAULT_COUNTRY,
            )
            chollos_activos = int(row["n"])
            ahorro_mediano = float(row["median_savings"]) if row["median_savings"] is not None else None

        desync_row = await c.fetchrow(
            f"""
            SELECT count(*) AS n
              FROM platform_listing pl
              JOIN servable_vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
              JOIN entity e ON e.entity_ulid = v.entity_ulid
             WHERE pl.status = 'listed' AND pl.platform_price IS NOT NULL AND v.price IS NOT NULL
               AND e.country_code = $3
               AND v.last_seen >= now() - interval '{FRESHNESS_FRESH_HOURS} hours'
               AND pl.last_seen >= now() - interval '{FRESHNESS_FRESH_HOURS} hours'
               AND abs(pl.platform_price - v.price) >= GREATEST($1, $2 * v.price)
            """,
            DESYNC_MIN_ABS_EUR, DESYNC_MIN_REL, DEFAULT_COUNTRY,
        )
        desyncs_activos = int(desync_row["n"])

        mediana_dias_a_salida = None
        if decay_run is not None:
            median_days_row = await c.fetchrow(
                "SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY median_days_to_gone) AS m "
                "FROM market_cycle_stats WHERE run_id = $1",
                decay_run["run_id"],
            )
            if median_days_row is not None and median_days_row["m"] is not None:
                mediana_dias_a_salida = float(median_days_row["m"])

        return ok({
            "chollos_activos": chollos_activos,
            "ahorro_mediano_eur": ahorro_mediano,
            "desyncs_activos": desyncs_activos,
            "mediana_dias_a_salida": mediana_dias_a_salida,
            "mediana_dias_a_salida_reason": None if mediana_dias_a_salida is not None else
                "ninguna cohorte alcanza aún el mínimo de ciclos NEW→GONE requerido",
        })


# ---------------------------------------------------------------------------
# GET /arbitrage/deals — the "Chollos de reposición" ranking (§4.1, §6 item 2)
# ---------------------------------------------------------------------------

@router.get("/arbitrage/deals")
@limiter.limit(RATE_DEFAULT)
async def deals(
    request: Request,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    make: str | None = Query(default=None, description="Make, case-insensitive substring"),
    province: str | None = Query(default=None, description="2-char province code"),
    band: str | None = Query(default=None, description="'chollo_fuerte' | 'bajo_mercado'"),
    min_savings: float | None = Query(default=None, ge=0, description="Minimum savings_eur"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Deal-score ranking, ordered by savings_eur (dealer's "margen bruto aparente")
    descending — the carta's default sort (§6 item 2). Re-verifies freshness AND
    non-quarantine status LIVE (joins servable_vehicle, not the raw vehicle table) so a
    vehicle that went stale or got price_trap-quarantined since the run computed it is
    never served, even though its deal_score row still exists until the next run.
    """
    if band is not None and band not in ("chollo_fuerte", "bajo_mercado"):
        return err("band must be 'chollo_fuerte' or 'bajo_mercado'", status=400)

    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        run = await _latest_run(c)
        if run is None:
            return err("no arbitrage_run yet — the deal-score job has not run", status=503)

        offset = (page - 1) * size
        rows = await c.fetch(
            f"""
            SELECT ds.vehicle_ulid, ds.z, ds.band, ds.savings_eur, ds.cohort_n,
                   ds.cohort_median_price, ds.cohort_make, ds.cohort_model, ds.cohort_year,
                   ds.cohort_tier,
                   v.title, v.make, v.model, v.year, v.km, v.price, v.currency, v.deep_link,
                   v.first_seen, v.last_seen,
                   e.cdp_code, e.trade_name, e.province_code,
                   (v.last_seen >= now() - interval '{FRESHNESS_FRESH_HOURS} hours') AS fresh,
                   extract(epoch FROM (now() - v.first_seen)) / 86400.0 AS days_on_market
              FROM deal_score ds
              JOIN servable_vehicle v ON v.vehicle_ulid = ds.vehicle_ulid
              JOIN entity e ON e.entity_ulid = v.entity_ulid
             WHERE ds.run_id = $1
               AND e.country_code = $8
               AND v.last_seen >= now() - interval '{FRESHNESS_MAX_DAYS} days'
               AND ($2::text IS NULL OR v.make ILIKE $2)
               AND ($3::text IS NULL OR e.province_code = $3)
               AND ($4::text IS NULL OR ds.band = $4)
               AND ($5::numeric IS NULL OR ds.savings_eur >= $5)
             ORDER BY ds.savings_eur DESC
             LIMIT $6 OFFSET $7
            """,
            run["run_id"], make, province, band, min_savings, size + 1, offset, DEFAULT_COUNTRY,
        )
        rows, has_more = page_slice(rows, size)
        items = [
            {
                "vehicle_ulid": r["vehicle_ulid"],
                "title": r["title"], "make": r["make"], "model": r["model"], "year": r["year"],
                "km": r["km"],
                "price": float(r["price"]) if r["price"] is not None else None,
                "currency": r["currency"], "deep_link": r["deep_link"],
                "dealer": {"cdp_code": r["cdp_code"], "trade_name": r["trade_name"]},
                "province_code": r["province_code"],
                "z": round(float(r["z"]), 2),
                "band": r["band"],
                "savings_eur": float(r["savings_eur"]),
                "cohort": {
                    "n": r["cohort_n"], "median_price": float(r["cohort_median_price"]),
                    "make": r["cohort_make"], "model": r["cohort_model"], "year": r["cohort_year"],
                    "tier": r["cohort_tier"],
                },
                "days_on_market": round(float(r["days_on_market"]), 1),
                "fresh": r["fresh"],
                "last_seen": str(r["last_seen"]),
            }
            for r in rows
        ]
        response = ok(
            items,
            page=page, size=size, returned=len(items), has_more=has_more,
            run_id=run["run_id"], run_at=str(run["run_at"]),
            methodology_version=run["methodology_version"],
        )
        return cache_set(request, response)


# ---------------------------------------------------------------------------
# GET /arbitrage/desync — dealer<->platform price desync (§4.2)
# ---------------------------------------------------------------------------

@router.get("/arbitrage/desync")
@limiter.limit(RATE_EXPENSIVE)
async def desync(
    request: Request,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Live-computed desync between a vehicle's own price and its platform_listing
    price (§4.2) — identity is certain BY CONSTRUCTION (same fila-edge), so this needs
    no batch run/table: it is always computed fresh, exactly like M2 (01-market-intelligence).

    Predicate: |platform_price - price| >= GREATEST(100, 1% of price), both prices
    non-null, both sides' last_seen <= 72h (§4.2's own freshness gate — tighter than
    deals' 7-day window, since a desync is a live A/B-price fact, not a historical rank).
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    offset = (page - 1) * size
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            f"""
            SELECT v.vehicle_ulid, v.make, v.model, v.year, v.deep_link,
                   v.price AS dealer_price, v.last_seen AS dealer_last_seen,
                   pl.platform_price, pl.listing_url AS platform_url, pl.last_seen AS platform_last_seen,
                   d.cdp_code AS dealer_cdp_code, d.trade_name AS dealer_name,
                   p.cdp_code AS platform_cdp_code, p.trade_name AS platform_name,
                   abs(pl.platform_price - v.price) AS delta_eur
              FROM platform_listing pl
              JOIN servable_vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
              JOIN entity d ON d.entity_ulid = v.entity_ulid
              JOIN entity p ON p.entity_ulid = pl.platform_entity_ulid
             WHERE pl.status = 'listed'
               AND d.country_code = $5 AND p.country_code = $5
               AND pl.platform_price IS NOT NULL AND v.price IS NOT NULL
               AND v.last_seen >= now() - interval '{FRESHNESS_FRESH_HOURS} hours'
               AND pl.last_seen >= now() - interval '{FRESHNESS_FRESH_HOURS} hours'
               AND abs(pl.platform_price - v.price) >= GREATEST($1, $2 * v.price)
             ORDER BY delta_eur DESC
             LIMIT $3 OFFSET $4
            """,
            DESYNC_MIN_ABS_EUR, DESYNC_MIN_REL, size + 1, offset, DEFAULT_COUNTRY,
        )
        rows, has_more = page_slice(rows, size)
        items = [
            {
                "vehicle_ulid": r["vehicle_ulid"], "make": r["make"], "model": r["model"],
                "year": r["year"],
                "dealer": {
                    "cdp_code": r["dealer_cdp_code"], "trade_name": r["dealer_name"],
                    "price": float(r["dealer_price"]), "url": r["deep_link"],
                    "last_seen": str(r["dealer_last_seen"]),
                },
                "platform": {
                    "cdp_code": r["platform_cdp_code"], "trade_name": r["platform_name"],
                    "price": float(r["platform_price"]), "url": r["platform_url"],
                    "last_seen": str(r["platform_last_seen"]),
                },
                "delta_eur": float(r["delta_eur"]),
                "delta_pct": round(float(r["delta_eur"]) / float(r["dealer_price"]) * 100.0, 2)
                if r["dealer_price"] else None,
            }
            for r in rows
        ]
        response = ok(items, page=page, size=size, returned=len(items), has_more=has_more)
        return cache_set(request, response)


def _year_band_start(year: int) -> int:
    return year - (year % 2)


async def _latest_decay_run(conn) -> dict[str, Any] | None:
    row = await conn.fetchrow(
        "SELECT run_id, run_at, methodology_version FROM arbitrage_decay_run ORDER BY run_at DESC LIMIT 1"
    )
    return dict(row) if row is not None else None


async def _latest_geo_run(conn) -> dict[str, Any] | None:
    row = await conn.fetchrow(
        "SELECT run_id, run_at, methodology_version FROM arbitrage_geo_run ORDER BY run_at DESC LIMIT 1"
    )
    return dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# GET /arbitrage/time-curves/{make}/{model} — "Ritmo de mercado" (F4, §4.3, §6 item 4)
# ---------------------------------------------------------------------------

@router.get("/arbitrage/time-curves/{make}/{model}")
@limiter.limit(RATE_DEFAULT)
async def time_curves(
    make: str,
    model: str,
    request: Request,
    year: int = Query(..., description="Anchor year of the 2-year band (e.g. 2022 -> [2022,2023])"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Days-to-GONE distribution + age-bucket decay curve for one cohort.

    Honest empty state (§6 item 4, "Aún no hay historial suficiente"): a cohort under
    either minimum (MIN_CYCLES_PER_COHORT for the cycle stats, MIN_OBS_PER_BUCKET per
    bucket for the decay curve) returns ``cycle_stats: null`` / an empty ``buckets``
    array with an explicit ``reason`` — never a fabricated number. "Salida del mercado
    != venta confirmada" (§4.3) is echoed in every response.
    """
    band = _year_band_start(year)
    async with request.app.state.pool.acquire() as c:
        run = await _latest_decay_run(c)
        if run is None:
            return err("no arbitrage_decay_run yet — the time-arbitrage job has not run", status=503)

        cycle_row = await c.fetchrow(
            "SELECT n_cycles, median_days_to_gone, p25_days_to_gone, p75_days_to_gone, "
            "pct_price_drop_before_gone FROM market_cycle_stats "
            "WHERE run_id=$1 AND make=$2 AND model=$3 AND year_band_start=$4",
            run["run_id"], make, model, band,
        )
        cycle_stats = (
            {
                "n_cycles": cycle_row["n_cycles"],
                "median_days_to_gone": float(cycle_row["median_days_to_gone"]),
                "p25_days_to_gone": float(cycle_row["p25_days_to_gone"]),
                "p75_days_to_gone": float(cycle_row["p75_days_to_gone"]),
                "pct_price_drop_before_gone": float(cycle_row["pct_price_drop_before_gone"]),
            }
            if cycle_row is not None else None
        )

        bucket_rows = await c.fetch(
            "SELECT bucket_label, bucket_min_days, n, median_relative_price FROM market_decay "
            "WHERE run_id=$1 AND make=$2 AND model=$3 AND year_band_start=$4 "
            "ORDER BY bucket_min_days ASC",
            run["run_id"], make, model, band,
        )
        buckets = [
            {"bucket_label": r["bucket_label"], "bucket_min_days": r["bucket_min_days"],
             "n": r["n"], "median_relative_price": float(r["median_relative_price"])}
            for r in bucket_rows
        ]

        return ok(
            {
                "make": make, "model": model, "year_band_start": band,
                "cycle_stats": cycle_stats,
                "cycle_stats_reason": None if cycle_stats is not None else
                    f"cohorte con menos de {MIN_CYCLES_PER_COHORT} ciclos NEW→GONE completos en los últimos 12 meses",
                "buckets": buckets,
                "buckets_reason": None if buckets else
                    f"ningún bucket de edad alcanza el mínimo de {MIN_OBS_PER_BUCKET} observaciones",
                "disclaimer": "Salida del mercado (GONE) != venta confirmada — puede ser retirada, "
                              "reserva o fallo de captura.",
            },
            run_id=run["run_id"], run_at=str(run["run_at"]), methodology_version=run["methodology_version"],
        )


# ---------------------------------------------------------------------------
# GET /arbitrage/geo/{make}/{model} — "Mapa de precio por provincia" (F5, §4.4, §6 item 5)
# ---------------------------------------------------------------------------

@router.get("/arbitrage/geo/{make}/{model}")
@limiter.limit(RATE_DEFAULT)
async def geo(
    make: str,
    model: str,
    request: Request,
    year: int = Query(..., description="Anchor year of the 2-year band"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Per-province median (choropleth cells, n>=15 only) + significant province-pair
    gaps for one cohort (§4.4). A province with n<15 for this cohort simply has no
    cell — never an interpolated/fabricated value."""
    band = _year_band_start(year)
    async with request.app.state.pool.acquire() as c:
        run = await _latest_geo_run(c)
        if run is None:
            return err("no arbitrage_geo_run yet — the geo-arbitrage job has not run", status=503)

        cell_rows = await c.fetch(
            "SELECT province_code, n, median_price FROM geo_price_cell "
            "WHERE run_id=$1 AND make=$2 AND model=$3 AND year_band_start=$4 "
            "ORDER BY median_price ASC",
            run["run_id"], make, model, band,
        )
        gap_rows = await c.fetch(
            "SELECT province_cheap, province_expensive, median_cheap, median_expensive, "
            "gap_eur, n_cheap, n_expensive FROM geo_price_gap "
            "WHERE run_id=$1 AND make=$2 AND model=$3 AND year_band_start=$4 "
            "ORDER BY gap_eur DESC",
            run["run_id"], make, model, band,
        )

        return ok(
            {
                "make": make, "model": model, "year_band_start": band,
                "cells": [
                    {"province_code": r["province_code"], "n": r["n"], "median_price": float(r["median_price"])}
                    for r in cell_rows
                ],
                "cells_reason": None if cell_rows else
                    f"ninguna provincia alcanza el mínimo de {GEO_CELL_MIN_N} anuncios para esta cohorte",
                "gaps": [
                    {
                        "province_cheap": r["province_cheap"], "province_expensive": r["province_expensive"],
                        "median_cheap": float(r["median_cheap"]), "median_expensive": float(r["median_expensive"]),
                        "gap_eur": float(r["gap_eur"]), "n_cheap": r["n_cheap"], "n_expensive": r["n_expensive"],
                    }
                    for r in gap_rows
                ],
                "disclaimer": "Precios de oferta del censo, no de transacción.",
            },
            run_id=run["run_id"], run_at=str(run["run_at"]), methodology_version=run["methodology_version"],
        )


# ---------------------------------------------------------------------------
# GET /arbitrage/methodology — the honesty endpoint (§4, §6 item 1: "cómo se calcula")
# ---------------------------------------------------------------------------

@router.get("/arbitrage/methodology")
@limiter.limit(RATE_DEFAULT)
async def methodology(
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Publish every threshold and minimum-N this pilar uses — never a black box
    (04-arbitrage.md §3: "los umbrales de Cardeep serán públicos y auditables",
    explicit contrast with CarGurus' undisclosed cuts)."""
    return ok({
        "methodology_version": SCORE_METHODOLOGY_VERSION,
        "deal_score": {
            "cohort": {
                "tier_a_min_n": COHORT_MIN_TIER_A,
                "tier_b_min_n": COHORT_MIN_TIER_B,
                "tier_b_key": "(make, year), model NULL — fallback when Tier-A cohort is too small",
                "mad_floor_ln_price": COHORT_MAD_FLOOR,
                "z_formula": "z = (ln(price) - median_ln_price_cohort) / (1.4826 * MAD_ln_price_cohort)",
            },
            "bands": {
                "price_trap_frontier_z": DEAL_SCORE_FLOOR_Z,
                "chollo_fuerte_max_z": DEAL_SCORE_CHOLLO_FUERTE_Z,
                "bajo_mercado_max_z": DEAL_SCORE_BAJO_MERCADO_Z,
                "description": (
                    f"z <= {DEAL_SCORE_FLOOR_Z}: not a deal (price_trap territory); "
                    f"{DEAL_SCORE_FLOOR_Z} < z <= {DEAL_SCORE_CHOLLO_FUERTE_Z}: chollo_fuerte; "
                    f"{DEAL_SCORE_CHOLLO_FUERTE_Z} < z <= {DEAL_SCORE_BAJO_MERCADO_Z}: bajo_mercado; "
                    f"z > {DEAL_SCORE_BAJO_MERCADO_Z}: not shown"
                ),
            },
            "freshness": {
                "fresh_hours": FRESHNESS_FRESH_HOURS,
                "max_age_days": FRESHNESS_MAX_DAYS,
                "rule": "last_seen <= 72h: fresh; 72h-7d: served with 'sin re-verificar'; >7d: excluded",
            },
        },
        "desync": {
            "min_relative_pct": DESYNC_MIN_REL * 100,
            "min_absolute_eur": DESYNC_MIN_ABS_EUR,
            "freshness_hours": FRESHNESS_FRESH_HOURS,
            "rule": "both sides' last_seen <= 72h AND delta >= GREATEST(min_absolute_eur, min_relative_pct * price)",
        },
        "time_arbitrage": {
            "min_cycles_per_cohort": MIN_CYCLES_PER_COHORT,
            "min_observations_per_bucket": MIN_OBS_PER_BUCKET,
            "cycle_lookback_months": 12,
            "age_buckets_days": ["0-7", "8-15", "16-30", "31-60", "61-90", "90+"],
            "rule": "cohort = (make, model, 2-year band); a cycle/bucket below its minimum is never shown",
        },
        "geo_arbitrage": {
            "cell_min_n": GEO_CELL_MIN_N,
            "gap_significance_factor": GEO_GAP_SIGNIFICANCE_FACTOR,
            "rule": "cell = (make, model, 2-year band, province); a gap is shown only if both cells "
                    "clear cell_min_n AND |median_a - median_b| > factor * sqrt(sigma_a^2 + sigma_b^2), "
                    "sigma = median_price * mad_ln_price * 1.4826 (euro-scale uncertainty)",
        },
        "disclaimers": [
            "Precios de oferta del censo, no precios de transacción confirmada.",
            "Un GONE no es una venta confirmada — puede ser retirada, reserva o fallo de captura.",
            "No es arbitraje cuantitativo (sin cointegración ni ejecución simultánea): es señal de "
            "asimetría informativa sobre precio de oferta.",
        ],
    })
