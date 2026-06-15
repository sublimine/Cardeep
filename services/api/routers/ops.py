"""/health, /alerts, /sources — operational monitoring endpoints.

SU-D2 additions:
  - /health: rate-limited at RATE_HEALTH (generous — liveness probes must pass).
  - /alerts: rate-limited at RATE_DEFAULT; NOT cached (near-real-time data).
  - /sources: rate-limited at RATE_DEFAULT; NOT cached (monitoring data).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from services.api.cache import cache_set, try_cache_get
from services.api.deps import err, ok, require_api_key
from services.api.ratelimit import RATE_DEFAULT, RATE_EXPENSIVE, RATE_HEALTH, limiter

router = APIRouter()


# ---------------------------------------------------------------------------
# /health — UNAUTHENTICATED liveness probe (no business data)
# /stats  — AUTHENTICATED sealed product counts (moved off /health: audit)
# ---------------------------------------------------------------------------

@router.get("/health")
@limiter.limit(RATE_HEALTH)
async def health(request: Request) -> JSONResponse:
    """Liveness probe — UNAUTHENTICATED by contract (load balancers / uptime probes).

    Returns only {status, db}. It deliberately exposes NO product counts: coverage
    totals (dealers / vehicles) are a competitive signal and now live behind auth at
    /stats — the audit flagged that anonymous callers could read the product's scale
    here. A single ``SELECT 1`` round-trip makes this a real liveness check (DB
    reachable), not merely process-up, while staying cheap (the old /health ran 5
    expensive COUNT(*) on every probe — uncached).
    """
    db_ok = True
    try:
        async with request.app.state.pool.acquire() as c:
            await c.fetchval("SELECT 1")
    except Exception:
        db_ok = False
    return ok({"status": "live" if db_ok else "degraded",
               "db": "ok" if db_ok else "down"})


@router.get("/stats")
@limiter.limit(RATE_EXPENSIVE)
async def stats(
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Sealed product counts — AUTHENTICATED (competitive coverage signal).

    Moved off /health (audit): anonymous callers must not learn coverage scale.

    dealers        — sealed dealer count from v_dealer_resolved excluding
                     particulares (40 016: kind <> 'particular').
    vehicles_unique_available — canonical-only + status='available' (1 486 285,
                    not the 1 689 243 raw including cross-entity aliases).
    events         — total event rows (not filtered: historical record).
    provinces      — static geo table row count.
    municipalities — static geo table row count.

    SU-D2: RATE_EXPENSIVE + cached (5 COUNT(*) over full tables; stable between
    harvests). Caching here also removes the per-probe cost the old /health paid.
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

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
    response = ok({"counts": counts})
    return cache_set(request, response)


# ---------------------------------------------------------------------------
# GAP 5 new: /alerts (active unresolved) + /sources (source_health)
# ---------------------------------------------------------------------------

@router.get("/alerts")
@limiter.limit(RATE_DEFAULT)
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

    Not cached: alert state can change at any time.
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
@limiter.limit(RATE_DEFAULT)
async def list_sources(
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """GAP-5: Source health overview for all known scrapers/sources.

    Columns: source_key, status, consecutive_fails, last_ok, last_fail, is_tier1.
    Sorted: degraded/down first (most urgent), then by consecutive_fails DESC
    so the sickest sources are at the top.

    Not cached: source_health is near-real-time monitoring data.
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
