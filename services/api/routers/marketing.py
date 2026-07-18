"""/entities/{cdp}/listing-audit, /channel-radar, /feed/{target} and /vehicles/{ulid}/
adcopy -- pilar 07-marketing (plans/cardeep-omni/07-marketing.md).

Ownership: this is a NEW router (00-MASTER.md S5.1 file-ownership table has no prior
claimant on ``services/api/routers/marketing.py`` or these paths) -- zero collision
with market.py (01, ``/market/*``), publishing.py (05, ``/publishing/*``) or
arbitrage.py (04, ``/arbitrage/*``).

Cross-pilar reuse (00-MASTER.md C-1/C-12 "un solo calculo"): price-position (C2) is
NEVER re-derived here -- ``compute_price_position`` is imported directly from
market.py, the exact function 03-garage-fleet's ``dealer_ops.py`` already imports for
the same reason. Coverage/divergence classification (C3/C4) reuse the pure functions
already extracted by 05-multiposting's publishing.py (``_coverage_band``,
``_price_divergence``) -- the SAME pattern ``tests/test_api_publishing.py`` itself
already uses (importing those underscore-prefixed helpers across a module boundary is
established precedent in this codebase, not a private API violation).
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from services.api.cache import cache_set, try_cache_get
from services.api.deps import err, ok, page_slice, require_api_key, resolve_cluster
from services.api.ratelimit import RATE_DEFAULT, RATE_EXPENSIVE, limiter

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /entities/{cdp_code}/listing-audit -- C1 (F1)
# ---------------------------------------------------------------------------

_LISTING_AUDIT_SQL = """
    SELECT v.vehicle_ulid, v.deep_link, v.title, v.make, v.model, v.year, v.price,
           v.currency, v.photo_url, la.score, la.checks, la.computed_at
      FROM v_latest_listing_audit la
      JOIN vehicle v ON v.vehicle_ulid = la.vehicle_ulid
     WHERE v.entity_ulid = ANY($1::text[]) AND v.status = 'available'
     ORDER BY la.score ASC, v.vehicle_ulid
     LIMIT $2 OFFSET $3
"""


@router.get("/entities/{cdp_code}/listing-audit")
@limiter.limit(RATE_EXPENSIVE)
async def listing_audit(
    cdp_code: str,
    request: Request,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """C1 — "Arregla estos primero" (carta S6 Bloque 1): the dealer's own vehicles,
    worst score first, each with its 11-check breakdown already computed by
    scripts/run_listing_audit.py (never recomputed here — this endpoint ONLY reads
    ``v_latest_listing_audit``, the persisted evidence, per carta S4 C1: "El score se
    persiste con la lista de checks fallados, nunca solo el agregado").

    A vehicle with NO row yet in ``listing_audit`` (audit job has not reached it) is
    simply absent from this list — never a fabricated score. ``meta.audited_count``
    vs ``meta.total_available`` lets the frontend show honest audit coverage.
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        cluster = await resolve_cluster(c, cdp_code)
        if cluster is None:
            return err(f"dealer {cdp_code} not found", status=404)

        total_available = await c.fetchval(
            "SELECT count(*) FROM vehicle WHERE entity_ulid = ANY($1::text[]) AND status = 'available'",
            cluster.member_ulids,
        )
        latest_run = await c.fetchrow(
            """SELECT lar.run_ulid, lar.finished_at
                 FROM listing_audit la
                 JOIN listing_audit_run lar ON lar.run_ulid = la.run_ulid
                 JOIN vehicle v ON v.vehicle_ulid = la.vehicle_ulid
                WHERE v.entity_ulid = ANY($1::text[])
                ORDER BY la.computed_at DESC LIMIT 1""",
            cluster.member_ulids,
        )
        audited_count = await c.fetchval(
            """SELECT count(*) FROM v_latest_listing_audit la
                 JOIN vehicle v ON v.vehicle_ulid = la.vehicle_ulid
                WHERE v.entity_ulid = ANY($1::text[]) AND v.status = 'available'""",
            cluster.member_ulids,
        )

        offset = (page - 1) * size
        rows = await c.fetch(_LISTING_AUDIT_SQL, cluster.member_ulids, size + 1, offset)
        rows, has_more = page_slice(rows, size)

        items = [
            {
                "vehicle_ulid": r["vehicle_ulid"],
                "deep_link": r["deep_link"],
                "title": r["title"],
                "make": r["make"],
                "model": r["model"],
                "year": r["year"],
                "price": float(r["price"]) if r["price"] is not None else None,
                "currency": r["currency"],
                "photo_url": r["photo_url"],
                "score": r["score"],
                "checks": r["checks"],
                "computed_at": str(r["computed_at"]),
            }
            for r in rows
        ]

        response = ok(
            items,
            page=page, size=size, returned=len(items), has_more=has_more,
            dealer={"cdp_code": cluster.canonical_cdp_code},
            total_available=total_available,
            audited_count=audited_count,
            latest_run_id=latest_run["run_ulid"] if latest_run else None,
            latest_run_finished_at=str(latest_run["finished_at"]) if latest_run and latest_run["finished_at"] else None,
        )
    return cache_set(request, response)
