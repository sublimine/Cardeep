"""/market/* — market-intelligence endpoints (pilar 01-market-intelligence, F3-F5).

Ownership: 00-MASTER.md resolution C-1 assigns this file and the ``/market/*``
namespace to pilar 01 exclusively. Pilar 09 (trading-terminal) owns a SEPARATE
``services/api/routers/terminal.py`` with ``/terminal/*`` — never this file. This
is ALSO the shared comparables engine pilar 03 (K9/K10/K11) and 07 (C2) are
expected to consume rather than re-derive (00-MASTER.md §98) — one implementation.

Scope built so far: M1/M3/M4/M5/M7/M9/M10 (F3, served from ``market_stat``), M8
(F4, served from ``dgt_corroboration``), and M2 (F5, price-position — computed
live against the latest published M1 row, never precomputed/stored per-vehicle:
storing a ratio for millions of vehicles that only changes when a NEW market_stat
run publishes would be pure staleness risk for zero benefit over a cheap live
lookup+division).

DECLARED GAP (not hidden): M6 (value curve by age cohort) is named in the carta's
router design (§5) but was never assigned a construction phase in §9's F0-F5 list
(F1=M1 only, F2=M3/M4/M5/M7/M9/M10 explicitly, F7=M6 LONGITUDINAL only — the
cross-sectional Fase-1 of M6 has no owning phase). Rather than fabricate M6 data to
fill the router's advertised shape, this endpoint simply omits M6 from the served
metric set until a future block computes it. The frontend spec (§6 item 5, "¿Cómo
pierde valor?") is therefore NOT servable from this router yet — declared here, not
silently dropped.

Every response carries ``run_id``, the run's ``computed_at``/``window_description``,
and each metric's own ``n`` + window — the carta's transversal rule ("todo widget
muestra n, ventana y timestamp del run"). A segment that never cleared
MIN_COHORT_N is simply ABSENT from the response body, never a fabricated zero.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from services.api.cache import cache_set, try_cache_get
from services.api.deps import err, ok, require_api_key
from services.api.ratelimit import RATE_DEFAULT, RATE_EXPENSIVE, limiter

router = APIRouter()

# Metrics served by /market/segments/.../stats (M2/M8 have their own dedicated
# endpoints below; M6 is a declared gap — see module docstring).
_SERVED_METRICS: tuple[str, ...] = ("M1", "M3", "M4", "M5", "M7", "M9", "M10")

# M2 price-position bands (carta §4 M2 row). [ASUMIDO -> re-verified in F5 against
# the REAL distribution of price/p50 ratios across 1,183,432 live canonical
# vehicles: p25=0.898, p50=1.000, p75=1.127 (01-market-intelligence-f5.md has the
# full percentile table). These cuts land close to the natural IQR split and are
# KEPT, not silently changed — a METHODOLOGY recalibration is explicitly reserved
# by the project's own model-routing doctrine for a caro-model adversarial gate
# (Fable 5/Opus), which this execution context could not invoke as a literal
# separate model call; the full analysis needed for that gate is written up in
# the F5 report so the decision can be made quickly, not re-derived from scratch.
M2_BELOW_MARKET_CUT: float = 0.92
M2_ABOVE_MARKET_CUT: float = 1.08


def _price_position_band(ratio: float) -> str:
    if ratio < M2_BELOW_MARKET_CUT:
        return "below_market"
    if ratio > M2_ABOVE_MARKET_CUT:
        return "above_market"
    return "at_market"


async def _latest_published_run(conn) -> dict[str, Any] | None:
    row = await conn.fetchrow(
        "SELECT run_id, run_at, methodology_version, window_description, metrics_computed "
        "FROM market_stat_run WHERE published = TRUE ORDER BY run_at DESC LIMIT 1"
    )
    return dict(row) if row is not None else None


def _row_payload(r: dict[str, Any]) -> dict[str, Any]:
    """Shape one market_stat row for the API — omits NULL distribution/scalar fields
    instead of serializing them as null noise (M1/M10 use p25/p50/p75; M3/M4/M5/M7/M9
    use value_num/value_extra — a row never has both shapes populated)."""
    payload: dict[str, Any] = {"n": r["n"]}
    if r["p25"] is not None:
        payload["p25"] = float(r["p25"])
    if r["p50"] is not None:
        payload["p50"] = float(r["p50"])
    if r["p75"] is not None:
        payload["p75"] = float(r["p75"])
    if r["value_num"] is not None:
        payload["value"] = float(r["value_num"])
    if r["value_extra"] is not None:
        payload["detail"] = r["value_extra"]
    return payload


# ---------------------------------------------------------------------------
# GET /market/segments/{make}/{model}/stats — M1/M3/M4/M7/M9/M10 for one segment
# ---------------------------------------------------------------------------

@router.get("/market/segments/{make}/{model}/stats")
@limiter.limit(RATE_DEFAULT)
async def segment_stats(
    make: str,
    model: str,
    request: Request,
    year: int = Query(..., description="Anchor year of the +/-1 sliding band (e.g. 2024)"),
    fuel: str = Query(..., description="Fuel type, exact match (e.g. 'Gasolina', 'Diesel')"),
    province: str | None = Query(default=None, description="2-char province code; omitted = national only"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """M1 (price p25/p50/p75), M3 (days-to-retirada), M4 (MDS), M7 (momentum),
    M9 (seller pressure), M10 (platform-count distribution) for one segment.

    Segment resolution honesty (carta §6 item 1): when ``province`` is given, the
    provincial row is served if it cleared MIN_COHORT_N; otherwise this endpoint
    falls back to the national row and sets ``fallback_to_national: true`` on that
    metric so the frontend can render the honest "aún no hay muestra suficiente en
    tu provincia" copy instead of silently swapping numbers. A metric absent from
    BOTH scopes is simply not a key in ``metrics`` — never a fabricated value.
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        run = await _latest_published_run(c)
        if run is None:
            return err("no published market_stat run yet", status=503)

        rows = await c.fetch(
            """
            SELECT metric_id, province_code, n, p25, p50, p75, value_num, value_extra
              FROM market_stat
             WHERE run_id = $1 AND make = $2 AND model = $3 AND year = $4 AND fuel = $5
               AND metric_id = ANY($6::text[])
               AND (province_code = $7 OR province_code IS NULL)
            """,
            run["run_id"], make, model, year, fuel, list(_SERVED_METRICS), province,
        )
        if not rows:
            return err(
                f"no market data for {make} {model} (year={year}, fuel={fuel}) — "
                f"either the segment does not exist or every cohort is below the "
                f"minimum sample size (n>=8)",
                status=404,
            )

        by_metric_scope: dict[str, dict[str, dict]] = {}
        for r in rows:
            scope = "prov" if r["province_code"] is not None else "nat"
            by_metric_scope.setdefault(r["metric_id"], {})[scope] = dict(r)

        metrics: dict[str, Any] = {}
        for metric_id, scopes in by_metric_scope.items():
            wanted_scope = "prov" if (province is not None and "prov" in scopes) else "nat"
            if wanted_scope not in scopes:
                wanted_scope = "nat" if "nat" in scopes else "prov"
            chosen = scopes[wanted_scope]
            payload = _row_payload(chosen)
            payload["scope"] = wanted_scope
            payload["fallback_to_national"] = (province is not None and wanted_scope == "nat")
            metrics[metric_id] = payload

        response = ok(
            {
                "make": make, "model": model, "year": year, "fuel": fuel,
                "province_requested": province,
                "metrics": metrics,
            },
            run_id=run["run_id"],
            run_at=str(run["run_at"]),
            methodology_version=run["methodology_version"],
            window_description=run["window_description"],
        )
        return cache_set(request, response)


# ---------------------------------------------------------------------------
# GET /market/provinces/demand — M5 provincial absorption ranking
# ---------------------------------------------------------------------------

@router.get("/market/provinces/demand")
@limiter.limit(RATE_EXPENSIVE)
async def provinces_demand(
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """M5 ranking: absorption rate (GONE/available in the run's window) per province.

    No make/model dimension (carta §4 M5 row: national demand map, not a segment
    filter) — every province that cleared MIN_COHORT_N on the available side in the
    latest published run, ordered by absorption rate descending.
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        run = await _latest_published_run(c)
        if run is None:
            return err("no published market_stat run yet", status=503)

        rows = await c.fetch(
            """
            SELECT province_code, n, value_num, value_extra
              FROM market_stat
             WHERE run_id = $1 AND metric_id = 'M5'
             ORDER BY value_num DESC NULLS LAST
            """,
            run["run_id"],
        )
        items = [
            {
                "province_code": r["province_code"],
                "n_available": r["n"],
                "absorption_rate": float(r["value_num"]) if r["value_num"] is not None else None,
                "detail": r["value_extra"],
            }
            for r in rows
        ]
        response = ok(
            items,
            run_id=run["run_id"],
            run_at=str(run["run_at"]),
            window_description=run["window_description"],
            count=len(items),
        )
        return cache_set(request, response)


# ---------------------------------------------------------------------------
# GET /market/dgt-corroboration — M8 (F4): DGT-vs-GONE cohort corroboration
# ---------------------------------------------------------------------------

async def _latest_corroboration_run(conn) -> dict[str, Any] | None:
    row = await conn.fetchrow(
        "SELECT run_id, run_at, month, methodology_version, notes "
        "FROM dgt_corroboration_run ORDER BY run_at DESC LIMIT 1"
    )
    return dict(row) if row is not None else None


@router.get("/market/dgt-corroboration")
@limiter.limit(RATE_DEFAULT)
async def dgt_corroboration(
    request: Request,
    province: str | None = Query(default=None, description="2-char province code; omitted = national rows"),
    make: str | None = Query(default=None, description="Make, case-insensitive"),
    model: str | None = Query(default=None, description="Model, case-insensitive; omitted = make-level rows only"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """M8: what fraction of Cardeep's GONE signal is corroborated against the DGT's
    official monthly transfer registry, per (province+make[+model]) cohort.

    Published as a DATA-QUALITY metric (carta §4 M8 row) — a low ratio is not hidden,
    it is the honest measurement of how much of the "listing removed" proxy actually
    lines up with an official ownership-transfer record for that cohort+month. No
    per-VIN join is possible (DGT restricts the chassis number since 2025-02-01);
    this is COHORT-level corroboration only, never a per-unit "this exact car sold"
    claim (carta §3.2 declared limit).
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        run = await _latest_corroboration_run(c)
        if run is None:
            return err("no dgt_corroboration run yet", status=503)

        make_norm = make.strip().upper() if make else None
        model_norm = model.strip().upper() if model else None

        rows = await c.fetch(
            """
            SELECT province_code, make, model, gone_count, dgt_count, ratio
              FROM dgt_corroboration
             WHERE run_id = $1
               AND (province_code = $2 OR $2 IS NULL)
               AND (make = $3 OR $3 IS NULL)
               AND (model IS NOT DISTINCT FROM $4)
             ORDER BY gone_count DESC
             LIMIT 200
            """,
            run["run_id"], province, make_norm, model_norm,
        )
        items = [
            {
                "province_code": r["province_code"],
                "make": r["make"],
                "model": r["model"],
                "gone_count": r["gone_count"],
                "dgt_count": r["dgt_count"],
                "ratio": float(r["ratio"]) if r["ratio"] is not None else None,
            }
            for r in rows
        ]
        response = ok(
            items,
            run_id=run["run_id"],
            run_at=str(run["run_at"]),
            month=run["month"],
            methodology_version=run["methodology_version"],
            notes=run["notes"],
            count=len(items),
        )
        return cache_set(request, response)


# ---------------------------------------------------------------------------
# GET /market/price-position/{vehicle_ulid} — M2 (F5)
# ---------------------------------------------------------------------------

@router.get("/market/price-position/{vehicle_ulid}")
@limiter.limit(RATE_DEFAULT)
async def price_position(
    vehicle_ulid: str,
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """M2: is THIS specific listing priced below/at/above its segment's market
    (M1's p50), and by how much. This is the shared comparables engine 03
    (garage-fleet K9) and 07 (marketing C2) are meant to consume rather than
    re-derive (00-MASTER.md §98) — one implementation, used by every consumer.

    Computed LIVE against the latest published M1 row for this vehicle's own
    segment (make+model+its own year as the +/-1 band anchor+fuel+province, with
    the same national fallback as ``/market/segments/.../stats``) — never
    precomputed/stored per-vehicle.

    Cuts (<0.92 / 0.92-1.08 / >1.08) are PUBLISHED in the response, not a black
    box (carta §4 M2 row, explicit contrast with CarGurus' undisclosed thresholds).

    Honest degradation, never a fabricated ratio:
      - vehicle_ulid not found -> 404.
      - vehicle exists but has no price, or make/model/year/fuel/province
        incomplete, or its segment never cleared MIN_COHORT_N even nationally in
        the latest published run -> 200 with ``position: null`` and a ``reason``.
    """
    async with request.app.state.pool.acquire() as c:
        vrow = await c.fetchrow(
            """
            SELECT v.vehicle_ulid, v.make, v.model, v.year, v.fuel, v.price,
                   e.province_code
              FROM vehicle v
              JOIN entity e ON e.entity_ulid = v.entity_ulid
             WHERE v.vehicle_ulid = $1
            """,
            vehicle_ulid,
        )
        if vrow is None:
            return err(f"vehicle {vehicle_ulid} not found", status=404)

        if vrow["price"] is None:
            return ok(
                {"vehicle_ulid": vehicle_ulid, "position": None, "reason": "vehicle has no price"}
            )
        if any(vrow[f] is None for f in ("make", "model", "year", "fuel", "province_code")):
            return ok(
                {"vehicle_ulid": vehicle_ulid, "position": None,
                 "reason": "vehicle is missing make/model/year/fuel/province — cannot resolve a segment"}
            )

        run = await _latest_published_run(c)
        if run is None:
            return err("no published market_stat run yet", status=503)

        m1_rows = await c.fetch(
            """
            SELECT province_code, p50, n
              FROM market_stat
             WHERE run_id = $1 AND metric_id = 'M1' AND make = $2 AND model = $3
               AND year = $4 AND fuel = $5 AND (province_code = $6 OR province_code IS NULL)
            """,
            run["run_id"], vrow["make"], vrow["model"], vrow["year"], vrow["fuel"], vrow["province_code"],
        )
        if not m1_rows:
            return ok(
                {"vehicle_ulid": vehicle_ulid, "position": None,
                 "reason": "no M1 data for this segment (n<8 even nationally, or segment never computed)"},
                run_id=run["run_id"],
            )

        prov_row = next((r for r in m1_rows if r["province_code"] is not None), None)
        chosen = prov_row if prov_row is not None else next(r for r in m1_rows if r["province_code"] is None)
        scope = "prov" if chosen is prov_row else "nat"

        p50 = float(chosen["p50"])
        price = float(vrow["price"])
        ratio = price / p50 if p50 > 0 else None
        if ratio is None:
            return ok(
                {"vehicle_ulid": vehicle_ulid, "position": None, "reason": "segment p50 is zero"},
                run_id=run["run_id"],
            )

        return ok(
            {
                "vehicle_ulid": vehicle_ulid,
                "price": price,
                "segment": {
                    "make": vrow["make"], "model": vrow["model"], "year": vrow["year"],
                    "fuel": vrow["fuel"], "province_code": vrow["province_code"],
                },
                "position": {
                    "ratio": ratio,
                    "band": _price_position_band(ratio),
                    "cuts": {"below_market_lt": M2_BELOW_MARKET_CUT, "above_market_gt": M2_ABOVE_MARKET_CUT},
                    "segment_p50": p50,
                    "segment_n": chosen["n"],
                    "scope": scope,
                    "fallback_to_national": scope == "nat",
                },
            },
            run_id=run["run_id"],
            run_at=str(run["run_at"]),
        )
