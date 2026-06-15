"""/health, /alerts, /sources — operational monitoring endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from services.api.deps import err, ok, require_api_key

router = APIRouter()


# ---------------------------------------------------------------------------
# GAP 1+7 fix: /health reports sealed counts
# ---------------------------------------------------------------------------

@router.get("/health")
async def health(request: Request) -> JSONResponse:
    """Liveness probe with sealed product counts.

    dealers        — sealed dealer count from v_dealer_resolved excluding
                     particulares (40 016: kind <> 'particular').
    vehicles_unique_available — canonical-only + status='available' (1 486 285,
                    not the 1 689 243 raw including cross-entity aliases).
    events         — total event rows (not filtered: historical record).
    provinces      — static geo table row count.
    municipalities — static geo table row count.
    """
    async with request.app.state.pool.acquire() as c:
        counts = {
            "dealers": await c.fetchval(
                """
                SELECT count(DISTINCT vdr.resolved_cdp_code)
                  FROM v_dealer_resolved vdr
                  JOIN entity e ON e.entity_ulid = vdr.entity_ulid
                 WHERE e.kind <> 'particular'
                """
            ),
            "vehicles_unique_available": await c.fetchval(
                """
                SELECT count(*)
                  FROM v_canonical_vehicle vc
                  JOIN vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
                 WHERE vc.vehicle_ulid = vc.canonical_vehicle_ulid
                   AND v.status = 'available'
                """
            ),
            "events": await c.fetchval("SELECT count(*) FROM vehicle_event"),
            "provinces": await c.fetchval("SELECT count(*) FROM geo_province"),
            "municipalities": await c.fetchval("SELECT count(*) FROM geo_municipality"),
        }
    return ok({"status": "live", "counts": counts})


# ---------------------------------------------------------------------------
# GAP 5 new: /alerts (active unresolved) + /sources (source_health)
# ---------------------------------------------------------------------------

@router.get("/alerts")
async def list_alerts(
    request: Request,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """GAP-5: Active (unresolved) alerts with exact origin.

    Columns served: id, origin, severity, message, payload, created_at.
    Sorted by severity priority (critical → warning → info) then by most
    recent first so the most urgent alerts surface at the top.

    Only rows WHERE resolved_at IS NULL are returned — resolved alerts
    are not surfaced here (historical; use a separate query if needed).
    """
    offset = (page - 1) * size
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            """
            SELECT id, origin, severity, message, payload, created_at
              FROM alert
             WHERE resolved_at IS NULL
             ORDER BY
               CASE severity
                 WHEN 'critical' THEN 0
                 WHEN 'warning'  THEN 1
                 ELSE                 2
               END,
               created_at DESC
             LIMIT $1 OFFSET $2
            """,
            size,
            offset,
        )
        items = [
            {
                **dict(r),
                "created_at": str(r["created_at"]),
            }
            for r in rows
        ]
        return ok(
            items,
            page=page,
            size=size,
            returned=len(items),
            has_more=len(items) == size,
        )


@router.get("/sources")
async def list_sources(
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """GAP-5: Source health overview for all known scrapers/sources.

    Columns: source_key, status, consecutive_fails, last_ok, last_fail, is_tier1.
    Sorted: degraded/down first (most urgent), then by consecutive_fails DESC
    so the sickest sources are at the top.
    """
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            """
            SELECT source_key, status, consecutive_fails,
                   last_ok, last_fail, is_tier1
              FROM source_health
             ORDER BY
               CASE status
                 WHEN 'down'     THEN 0
                 WHEN 'degraded' THEN 1
                 WHEN 'unknown'  THEN 2
                 ELSE                 3
               END,
               consecutive_fails DESC,
               source_key
            """
        )
        items = [
            {
                **dict(r),
                "last_ok": str(r["last_ok"]) if r["last_ok"] else None,
                "last_fail": str(r["last_fail"]) if r["last_fail"] else None,
            }
            for r in rows
        ]
        return ok(items, count=len(items))
