"""/market/* — market-intelligence endpoints (pilar 01-market-intelligence, F3+F4).

Ownership: 00-MASTER.md resolution C-1 assigns this file and the ``/market/*``
namespace to pilar 01 exclusively. Pilar 09 (trading-terminal) owns a SEPARATE
``services/api/routers/terminal.py`` with ``/terminal/*`` — never this file.

Scope built so far: M1/M3/M4/M5/M7/M9/M10 (F3, served from ``market_stat``) and M8
(F4, served from ``dgt_corroboration`` — DGT-vs-GONE cohort corroboration). One
metric is DELIBERATELY absent, not an oversight:

  - M2 (price-position, ``/market/price-position/{vehicle_ulid}``) is F5's scope —
    it is NOT built here. Creating that path now with no real ratio logic behind it
    would BE the exact mock violation this pilar exists to remove from `Api.tsx`.

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

# Metrics this router is authorized to serve today (F3 scope — see module docstring
# for why M2/M6/M8 are deliberately excluded).
_SERVED_METRICS: tuple[str, ...] = ("M1", "M3", "M4", "M5", "M7", "M9", "M10")


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
