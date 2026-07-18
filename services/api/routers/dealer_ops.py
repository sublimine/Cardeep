"""/dealer/* — 03-garage-fleet F3: the dealer's OWN write layer.

FIRST write surface of the whole Cardeep API (00-MASTER.md recon: 0 POST/PUT/
PATCH/DELETE routes existed before this file). Everything here writes ONLY to
`fleet_ops`/`fleet_ops_event` (migrations/0080_fleet_ops.sql) — never to
`vehicle`/`vehicle_event`, the append-only census the scraper fleet owns
(carta §5, "censo y workspace no comparten tablas de escritura"; guarded
mechanically by 0034/0035's triggers, which this router never even attempts to
write around since it has no INSERT/UPDATE statement touching those tables at
all — see tests/test_dealer_ops_router.py's explicit before/after snapshot).

Authorization model: every write requires a valid session (AUTH-0,
``get_current_session``) AND that session's user must hold a ``dealer_membership``
row on the CANONICAL entity that owns the target vehicle (resolved the same way
``resolve_cluster`` resolves every other cdp_code in this API — a user who claimed
cdp_code X can manage every vehicle in X's cluster, not just X's own literal
entity_ulid). A session valid for dealer A can never write vehicle rows belonging
to dealer B — enforced by ``_authorize_vehicle`` on every single endpoint below.

Idempotency: re-sending the SAME target status/cost/target_price is a no-op —
no new fleet_ops_event row, ``meta.noop=true`` — so a retried request (client
timeout + retry, double-click) never fabricates a duplicate audit trail entry.

Audit: every write appends one row to fleet_ops_event (actor_user_ulid +
observed_at + from_value/to_value JSONB) BEFORE returning — "quien cambió qué y
cuándo" is always answerable by ``GET /dealer/vehicles/{ulid}/ops-history``, and
a replay of that history reconstructs the current fleet_ops row exactly (K13
protocol, carta §7).
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from pipeline.ids import ulid
from services.api.deps import err, ok, resolve_cluster
from services.api.ratelimit import RATE_DEFAULT, limiter
from services.api.routers.auth import CurrentSession, get_current_session
from services.api.routers.market import compute_price_position

router = APIRouter(prefix="/dealer", tags=["dealer_ops"])

FLEET_OPS_STATUSES: tuple[str, ...] = (
    "entrada", "preparacion", "publicado", "reservado", "vendido", "entregado",
)
"""K13 — must match migrations/0080_fleet_ops.sql's CHECK constraint exactly (the
DB is the final gate either way; this list only produces a clean 422 instead of
a raw constraint-violation 500)."""

NOTE_MAX_LENGTH = 500
REASON_MAX_LENGTH = 64


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class StatusChangeRequest(BaseModel):
    status: str = Field(...)
    note: str | None = Field(default=None, max_length=NOTE_MAX_LENGTH)


class CostRequest(BaseModel):
    purchase_cost: float = Field(..., ge=0)
    note: str | None = Field(default=None, max_length=NOTE_MAX_LENGTH)


class PriceOverrideRequest(BaseModel):
    target_price: float = Field(..., ge=0)
    reason_category: str = Field(..., min_length=1, max_length=REASON_MAX_LENGTH)
    note: str | None = Field(default=None, max_length=NOTE_MAX_LENGTH)


# ---------------------------------------------------------------------------
# Authorization — the core control this whole router exists to prove
# ---------------------------------------------------------------------------

async def _authorize_vehicle(conn, user_ulid: str, vehicle_ulid: str) -> dict[str, Any]:
    """Return the vehicle row iff *user_ulid* manages the dealer that owns it.

    404 (never 403) when the vehicle does not exist at all — does not leak
    existence of a vehicle the caller cannot manage. 403 only once we KNOW the
    vehicle exists and the caller's dealer_membership does not cover its
    (canonical) owning entity.
    """
    vrow = await conn.fetchrow(
        "SELECT vehicle_ulid, entity_ulid, price, status FROM vehicle WHERE vehicle_ulid = $1",
        vehicle_ulid,
    )
    if vrow is None:
        raise HTTPException(status_code=404, detail=f"vehicle {vehicle_ulid} not found")

    erow = await conn.fetchrow("SELECT cdp_code FROM entity WHERE entity_ulid = $1", vrow["entity_ulid"])
    if erow is None:
        raise HTTPException(status_code=404, detail=f"vehicle {vehicle_ulid} not found")

    cluster = await resolve_cluster(conn, erow["cdp_code"])
    if cluster is None:
        raise HTTPException(status_code=404, detail=f"vehicle {vehicle_ulid} not found")

    is_member = await conn.fetchval(
        "SELECT 1 FROM dealer_membership WHERE user_ulid = $1 AND entity_ulid = $2",
        user_ulid, cluster.canonical_ulid,
    )
    if not is_member:
        raise HTTPException(status_code=403, detail="you do not manage this vehicle's dealer")

    return dict(vrow)


def _serialize_ops(row: dict[str, Any] | None, vehicle_ulid: str) -> dict[str, Any]:
    """Shape a fleet_ops row for the API. Absence of a row means the vehicle has
    never been touched by the dealer — the IMPLICIT default state, never
    pre-materialized for every vehicle in the fleet (carta §5: "una fila por
    coche que HA SIDO tocado", not 468 rows created on day one)."""
    if row is None:
        return {
            "vehicle_ulid": vehicle_ulid, "status": "entrada",
            "purchase_cost": None, "target_price": None, "notes": None,
            "updated_at": None, "updated_by_user_ulid": None,
        }
    return {
        "vehicle_ulid": row["vehicle_ulid"],
        "status": row["status"],
        "purchase_cost": float(row["purchase_cost"]) if row["purchase_cost"] is not None else None,
        "target_price": float(row["target_price"]) if row["target_price"] is not None else None,
        "notes": row["notes"],
        "updated_at": str(row["updated_at"]),
        "updated_by_user_ulid": row["updated_by_user_ulid"],
    }


async def _current_ops_row(conn, vehicle_ulid: str) -> dict[str, Any] | None:
    row = await conn.fetchrow("SELECT * FROM fleet_ops WHERE vehicle_ulid = $1", vehicle_ulid)
    return dict(row) if row is not None else None


# ---------------------------------------------------------------------------
# GET /dealer/vehicles/{vehicle_ulid}/ops — current state (K13)
# ---------------------------------------------------------------------------

@router.get("/vehicles/{vehicle_ulid}/ops")
@limiter.limit(RATE_DEFAULT)
async def get_ops(
    vehicle_ulid: str,
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        await _authorize_vehicle(c, session.user_ulid, vehicle_ulid)
        row = await _current_ops_row(c, vehicle_ulid)
        return ok(_serialize_ops(row, vehicle_ulid))


# ---------------------------------------------------------------------------
# GET /dealer/entities/{cdp_code}/fleet-ops — bulk read for the vehicle-pipeline
# board (§6.2). ONE query for the whole fleet, never N+1 per vehicle.
# ---------------------------------------------------------------------------

@router.get("/entities/{cdp_code}/fleet-ops")
@limiter.limit(RATE_DEFAULT)
async def list_fleet_ops(
    cdp_code: str,
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        cluster = await resolve_cluster(c, cdp_code)
        if cluster is None:
            return err(f"entity {cdp_code} not found", status=404)
        is_member = await c.fetchval(
            "SELECT 1 FROM dealer_membership WHERE user_ulid = $1 AND entity_ulid = $2",
            session.user_ulid, cluster.canonical_ulid,
        )
        if not is_member:
            return err("you do not manage this dealer", status=403)

        rows = await c.fetch(
            """
            SELECT fo.* FROM fleet_ops fo
              JOIN vehicle v ON v.vehicle_ulid = fo.vehicle_ulid
             WHERE v.entity_ulid = ANY($1::text[])
            """,
            cluster.member_ulids,
        )
        items = [_serialize_ops(dict(r), r["vehicle_ulid"]) for r in rows]
        return ok(items, count=len(items))


# ---------------------------------------------------------------------------
# PATCH /dealer/vehicles/{vehicle_ulid}/status — K13 transition
# ---------------------------------------------------------------------------

@router.patch("/vehicles/{vehicle_ulid}/status")
@limiter.limit(RATE_DEFAULT)
async def set_status(
    vehicle_ulid: str,
    payload: StatusChangeRequest,
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    if payload.status not in FLEET_OPS_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"status must be one of {FLEET_OPS_STATUSES}, got '{payload.status}'",
        )

    async with request.app.state.pool.acquire() as c:
        await _authorize_vehicle(c, session.user_ulid, vehicle_ulid)
        async with c.transaction():
            current = await _current_ops_row(c, vehicle_ulid)
            current_status = current["status"] if current is not None else "entrada"

            if current_status == payload.status:
                # Idempotent no-op: same target status, no new event, no row touched.
                return ok(_serialize_ops(current, vehicle_ulid), noop=True)

            await c.execute(
                """
                INSERT INTO fleet_ops (vehicle_ulid, status, updated_by_user_ulid)
                VALUES ($1, $2, $3)
                ON CONFLICT (vehicle_ulid) DO UPDATE
                    SET status = EXCLUDED.status, updated_at = now(),
                        updated_by_user_ulid = EXCLUDED.updated_by_user_ulid
                """,
                vehicle_ulid, payload.status, session.user_ulid,
            )
            await c.execute(
                """
                INSERT INTO fleet_ops_event
                    (event_ulid, vehicle_ulid, actor_user_ulid, event_type, from_value, to_value)
                VALUES ($1, $2, $3, 'STATUS_CHANGE', $4, $5)
                """,
                ulid(), vehicle_ulid, session.user_ulid,
                {"status": current_status}, {"status": payload.status, "note": payload.note},
            )
            new_row = await _current_ops_row(c, vehicle_ulid)
        return ok(_serialize_ops(new_row, vehicle_ulid), noop=False)


# ---------------------------------------------------------------------------
# PATCH /dealer/vehicles/{vehicle_ulid}/cost — purchase cost annotation
# ---------------------------------------------------------------------------

@router.patch("/vehicles/{vehicle_ulid}/cost")
@limiter.limit(RATE_DEFAULT)
async def set_cost(
    vehicle_ulid: str,
    payload: CostRequest,
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        await _authorize_vehicle(c, session.user_ulid, vehicle_ulid)
        async with c.transaction():
            current = await _current_ops_row(c, vehicle_ulid)
            current_cost = float(current["purchase_cost"]) if current and current["purchase_cost"] is not None else None

            if current_cost == payload.purchase_cost:
                return ok(_serialize_ops(current, vehicle_ulid), noop=True)

            await c.execute(
                """
                INSERT INTO fleet_ops (vehicle_ulid, purchase_cost, updated_by_user_ulid)
                VALUES ($1, $2, $3)
                ON CONFLICT (vehicle_ulid) DO UPDATE
                    SET purchase_cost = EXCLUDED.purchase_cost, updated_at = now(),
                        updated_by_user_ulid = EXCLUDED.updated_by_user_ulid
                """,
                vehicle_ulid, payload.purchase_cost, session.user_ulid,
            )
            await c.execute(
                """
                INSERT INTO fleet_ops_event
                    (event_ulid, vehicle_ulid, actor_user_ulid, event_type, from_value, to_value)
                VALUES ($1, $2, $3, 'COST_SET', $4, $5)
                """,
                ulid(), vehicle_ulid, session.user_ulid,
                {"purchase_cost": current_cost}, {"purchase_cost": payload.purchase_cost, "note": payload.note},
            )
            new_row = await _current_ops_row(c, vehicle_ulid)
        return ok(_serialize_ops(new_row, vehicle_ulid), noop=False)


# ---------------------------------------------------------------------------
# POST /dealer/vehicles/{vehicle_ulid}/price-override — K15
# ---------------------------------------------------------------------------

@router.post("/vehicles/{vehicle_ulid}/price-override")
@limiter.limit(RATE_DEFAULT)
async def price_override(
    vehicle_ulid: str,
    payload: PriceOverrideRequest,
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    """K15 — every target-price write is captured WITH a reason category and the
    delta vs the market's own suggestion (01's M2, ``compute_price_position`` —
    never re-derived here), closing the Tekion "override gap" (carta §2.1: the
    reference DMS records the new price but not the reason/approver/margin
    impact; Cardeep records all three by construction)."""
    async with request.app.state.pool.acquire() as c:
        await _authorize_vehicle(c, session.user_ulid, vehicle_ulid)

        position = await compute_price_position(c, vehicle_ulid)
        delta_vs_median: float | None = None
        if position.ok and position.data is not None and position.data.get("position") is not None:
            segment_p50 = position.data["position"]["segment_p50"]
            if segment_p50:
                delta_vs_median = (payload.target_price / segment_p50) - 1.0

        async with c.transaction():
            current = await _current_ops_row(c, vehicle_ulid)
            current_target = float(current["target_price"]) if current and current["target_price"] is not None else None

            if current_target == payload.target_price:
                return ok(_serialize_ops(current, vehicle_ulid), noop=True)

            await c.execute(
                """
                INSERT INTO fleet_ops (vehicle_ulid, target_price, updated_by_user_ulid)
                VALUES ($1, $2, $3)
                ON CONFLICT (vehicle_ulid) DO UPDATE
                    SET target_price = EXCLUDED.target_price, updated_at = now(),
                        updated_by_user_ulid = EXCLUDED.updated_by_user_ulid
                """,
                vehicle_ulid, payload.target_price, session.user_ulid,
            )
            await c.execute(
                """
                INSERT INTO fleet_ops_event
                    (event_ulid, vehicle_ulid, actor_user_ulid, event_type,
                     from_value, to_value, reason_category, delta_vs_median)
                VALUES ($1, $2, $3, 'PRICE_OVERRIDE', $4, $5, $6, $7)
                """,
                ulid(), vehicle_ulid, session.user_ulid,
                {"target_price": current_target},
                {"target_price": payload.target_price, "note": payload.note},
                payload.reason_category, delta_vs_median,
            )
            new_row = await _current_ops_row(c, vehicle_ulid)
        return ok(
            _serialize_ops(new_row, vehicle_ulid),
            noop=False,
            delta_vs_median=delta_vs_median,
        )


# ---------------------------------------------------------------------------
# GET /dealer/vehicles/{vehicle_ulid}/ops-history — replay / audit trail
# ---------------------------------------------------------------------------

@router.get("/vehicles/{vehicle_ulid}/ops-history")
@limiter.limit(RATE_DEFAULT)
async def ops_history(
    vehicle_ulid: str,
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    """Full append-only audit trail for one vehicle — "quien cambió qué y
    cuándo" (carta §5 write-surface requirement), oldest first so a caller can
    replay it and reconstruct the current fleet_ops state (§7 K13 protocol)."""
    async with request.app.state.pool.acquire() as c:
        await _authorize_vehicle(c, session.user_ulid, vehicle_ulid)
        rows = await c.fetch(
            """
            SELECT event_ulid, actor_user_ulid, event_type, from_value, to_value,
                   reason_category, delta_vs_median, observed_at
              FROM fleet_ops_event
             WHERE vehicle_ulid = $1
             ORDER BY observed_at ASC, event_ulid ASC
            """,
            vehicle_ulid,
        )
        items = [
            {
                **dict(r),
                "delta_vs_median": float(r["delta_vs_median"]) if r["delta_vs_median"] is not None else None,
                "observed_at": str(r["observed_at"]),
            }
            for r in rows
        ]
        return ok(items, count=len(items), vehicle_ulid=vehicle_ulid)
