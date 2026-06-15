"""/vehicles/{ulid} — vehicle detail, history, and platform listing endpoints.

SU-D2 additions:
  - /vehicles/{ulid}: RATE_DEFAULT; not cached (vehicle state changes after
    each harvest run — price, km, status).
  - /vehicles/{ulid}/history: RATE_DEFAULT; not cached (event stream appends
    on every harvest; consumers expect fresh data).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from services.api.deps import err, ok, require_api_key
from services.api.ratelimit import RATE_DEFAULT, limiter

router = APIRouter()


# ---------------------------------------------------------------------------
# GAP 2 new: /vehicles/{ulid} detail + /vehicles/{ulid}/history
# ---------------------------------------------------------------------------

@router.get("/vehicles/{vehicle_ulid}/history")
@limiter.limit(RATE_DEFAULT)
async def vehicle_history(
    vehicle_ulid: str,
    request: Request,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """GAP-2: Full event history for a vehicle (NEW→PRICE_CHANGE→GONE), oldest first.

    If *vehicle_ulid* is a non-canonical alias the history is still served —
    the alias vehicle_ulid is a real row in vehicle_event; aliasing is an
    entity-level concept for cross-dealer duplicates, not an erasure of history.

    Pagination: oldest events first (ASC) so callers can replay the timeline.
    """
    offset = (page - 1) * size
    async with request.app.state.pool.acquire() as c:
        exists = await c.fetchval(
            "SELECT 1 FROM vehicle WHERE vehicle_ulid = $1", vehicle_ulid)
        if exists is None:
            return err(f"vehicle {vehicle_ulid} not found")
        rows = await c.fetch(
            """
            SELECT event_type, old_value, new_value, observed_at
              FROM vehicle_event
             WHERE vehicle_ulid = $1
             ORDER BY observed_at ASC, event_type
             LIMIT $2 OFFSET $3
            """,
            vehicle_ulid,
            size,
            offset,
        )
        items = [{**dict(r), "observed_at": str(r["observed_at"])} for r in rows]
        return ok(
            items,
            page=page,
            size=size,
            returned=len(items),
            has_more=len(items) == size,
            vehicle_ulid=vehicle_ulid,
        )


@router.get("/vehicles/{vehicle_ulid}")
@limiter.limit(RATE_DEFAULT)
async def vehicle_detail(
    vehicle_ulid: str,
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """GAP-2: Full detail for a single vehicle.

    If *vehicle_ulid* is a non-canonical alias (per v_canonical_vehicle),
    the canonical_vehicle_ulid is exposed so callers can redirect.
    Returns 404 with coherent message when the ulid does not exist at all.
    """
    async with request.app.state.pool.acquire() as c:
        row = await c.fetchrow(
            """
            SELECT v.vehicle_ulid, v.make, v.model, v.year, v.km, v.price, v.currency,
                   v.photo_url, v.deep_link, v.title, v.fuel, v.transmission,
                   v.status, v.first_seen, v.last_seen,
                   vc.canonical_vehicle_ulid
              FROM vehicle v
              LEFT JOIN v_canonical_vehicle vc ON vc.vehicle_ulid = v.vehicle_ulid
             WHERE v.vehicle_ulid = $1
            """,
            vehicle_ulid,
        )
        if row is None:
            return err(f"vehicle {vehicle_ulid} not found")
        data = dict(row)
        data["price"] = float(data["price"]) if data["price"] is not None else None
        data["first_seen"] = str(data["first_seen"])
        data["last_seen"] = str(data["last_seen"])
        canonical = data.pop("canonical_vehicle_ulid")
        data["is_canonical"] = (canonical is None) or (canonical == vehicle_ulid)
        data["canonical_vehicle_ulid"] = canonical if canonical else vehicle_ulid
        return ok(data)
