"""services/api/routers/crm_deals.py — 06-unified-crm-chat F2/F5.

CRUD for `crm_deal`, scoped by tenant. Implements the Salesforce Amount x Probability
model (carta §4): every stage transition appends to `crm_deal_stage_event` (same
append-only-ledger-plus-current-state-row doctrine as `fleet_ops`/`fleet_ops_event`),
`won_at`/`lost_at` are stamped once, and `probability` auto-recomputes to the stage's
default UNLESS the caller explicitly overrides it in the same request (Salesforce-style:
"stage change resets probability unless manually pinned").

F5 adds the census cross-reference: every deal carries a `vehicleContext` chip (days in
stock, current price, price history for the detail view — `services/api/vehicle_context.py`,
the SAME computation `/vehicles/{ulid}` serves, never a second formula) plus a text->
inventory candidate matcher (`GET /deals/vehicle-search`) for the "New deal" picker.

Response contract: PLAIN JSON matching `web/src/types.ts::Deal` field-for-field (NOT the
`{ok,data,error,meta}` envelope) — same precedent as `crm_contacts.py`/`auth.py`, because
`web/src/hooks/useDeals.ts`/`useKanban.ts` already call `/deals` expecting this exact raw
shape (`{deals, total}` / a bare `Deal`).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from pipeline.ids import ulid
from services.api.crm_deps import TenantContext, require_tenant
from services.api.deps import page_slice
from services.api.ratelimit import RATE_DEFAULT, limiter
from services.api.vehicle_context import batch_vehicle_summaries, compute_vehicle_context

router = APIRouter(prefix="/deals", tags=["crm_deals"])

# Matches migrations/0084_crm.sql's crm_deal_stage enum and web/src/hooks/useKanban.ts's
# STAGES exactly — the SAME six values, same order, one source of truth on each side.
STAGES: tuple[str, ...] = ("lead", "contacted", "offer", "negotiation", "won", "lost")

# carta §4 exact defaults: "lead 10%, contacted 25%, offer 50%, negotiation 75%, won 100%,
# lost 0% — editable por deal". Auto-applied on create and on every stage change that the
# caller does not explicitly override in the same request.
STAGE_PROBABILITY_DEFAULTS: dict[str, float] = {
    "lead": 10.0, "contacted": 25.0, "offer": 50.0, "negotiation": 75.0, "won": 100.0, "lost": 0.0,
}

PRIORITIES: tuple[str, ...] = ("low", "medium", "high")


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Request bodies — camelCase aliases so the wire shape matches web/src/types.ts::Deal
# ---------------------------------------------------------------------------

class DealCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    contact_id: str = Field(..., alias="contactId", min_length=1)
    vehicle_id: str | None = Field(default=None, alias="vehicleId")
    stage: str = Field(default="lead")
    price: float | None = Field(default=None, ge=0)
    priority: str | None = Field(default=None)


class DealUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    stage: str | None = Field(default=None)
    vehicle_id: str | None = Field(default=None, alias="vehicleId")
    price: float | None = Field(default=None, ge=0)
    priority: str | None = Field(default=None)
    probability: float | None = Field(default=None, ge=0, le=100)


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

def _serialize_deal(row: dict[str, Any], cdp_code: str, vehicle_context: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "id": row["deal_ulid"],
        "tenantId": cdp_code,
        "contactId": row["contact_ulid"],
        "vehicleId": row["vehicle_ulid"] or "",
        "stage": row["stage"],
        "assigneeId": row["assignee_user_ulid"] or None,
        "priority": row["priority"],
        "createdAt": row["created_at"].isoformat(),
        "updatedAt": row["updated_at"].isoformat(),
        "contactName": row.get("contact_name"),
        "vehicleName": row.get("vehicle_name"),
        "price": float(row["amount"]) if row["amount"] is not None else None,
        "probability": float(row["probability"]) if row["probability"] is not None else None,
        # F5: carta §4 "chip de contexto" — only present when vehicle_ulid resolves
        # against the live census; never fabricated when it doesn't (carta §5 negative test).
        "vehicleContext": vehicle_context,
    }


_DEAL_JOIN_SQL = """
    SELECT d.*, ct.name AS contact_name,
           CASE WHEN v.vehicle_ulid IS NOT NULL
                THEN concat_ws(' ', v.make, v.model, v.year::text)
           END AS vehicle_name
      FROM crm_deal d
      LEFT JOIN crm_contact ct ON ct.contact_ulid = d.contact_ulid
      LEFT JOIN vehicle v ON v.vehicle_ulid = d.vehicle_ulid
"""


async def _fetch_deal(conn, deal_ulid: str, entity_ulid: str):
    return await conn.fetchrow(_DEAL_JOIN_SQL + " WHERE d.deal_ulid = $1 AND d.entity_ulid = $2", deal_ulid, entity_ulid)


async def _serialize_deal_full(conn, row, cdp_code: str) -> dict[str, Any]:
    """Single-resource serialization: includes the FULL vehicle context (price
    history) — used by every endpoint that returns exactly one deal."""
    vehicle_context = await compute_vehicle_context(conn, row["vehicle_ulid"]) if row["vehicle_ulid"] else None
    return _serialize_deal(dict(row), cdp_code, vehicle_context)


# ---------------------------------------------------------------------------
# GET /deals/summary — pipeline expected value + 90d lead time (carta §4 Kanban header)
# Declared BEFORE /{deal_ulid} so FastAPI does not swallow "summary" as a path param.
# ---------------------------------------------------------------------------

@router.get("/summary")
@limiter.limit(RATE_DEFAULT)
async def deals_summary(request: Request, tenant: TenantContext = Depends(require_tenant)) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        expected = await c.fetchval(
            """
            SELECT COALESCE(SUM(amount * probability / 100.0), 0)
              FROM crm_deal
             WHERE entity_ulid = $1 AND stage NOT IN ('won', 'lost')
               AND amount IS NOT NULL AND probability IS NOT NULL
            """,
            tenant.entity_ulid,
        )
        # Kanban University rule 5 (lead time): AVG(won_at - created_at) over deals won in
        # a 90-day rolling window (carta §4 exact spec).
        lead_time = await c.fetchval(
            """
            SELECT AVG(EXTRACT(EPOCH FROM (won_at - created_at)) / 86400.0)
              FROM crm_deal
             WHERE entity_ulid = $1 AND stage = 'won' AND won_at IS NOT NULL
               AND won_at >= now() - interval '90 days'
            """,
            tenant.entity_ulid,
        )
        stage_rows = await c.fetch(
            "SELECT stage, count(*) AS n FROM crm_deal WHERE entity_ulid = $1 GROUP BY stage",
            tenant.entity_ulid,
        )
    return JSONResponse({
        "expectedValue": float(expected),
        "avgLeadTimeDays": float(lead_time) if lead_time is not None else None,
        "byStage": {r["stage"]: r["n"] for r in stage_rows},
    })


# ---------------------------------------------------------------------------
# GET /deals/vehicle-search — F5 text->inventory matcher (carta §8: deterministic
# SQL candidate search; the dealer confirms with a click — this endpoint only ever
# returns CANDIDATES from the tenant's own live inventory, never auto-attaches one).
# Declared BEFORE /{deal_ulid} for the same routing-order reason as /summary.
# ---------------------------------------------------------------------------

@router.get("/vehicle-search")
@limiter.limit(RATE_DEFAULT)
async def vehicle_search(
    request: Request,
    q: str = Query(..., min_length=2, max_length=120),
    tenant: TenantContext = Depends(require_tenant),
) -> JSONResponse:
    pattern = f"%{q.strip()}%"
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            """
            SELECT vehicle_ulid, make, model, year, price, status, first_seen
              FROM vehicle
             WHERE entity_ulid = ANY($1::text[])
               AND status != 'gone'
               AND (make ILIKE $2 OR model ILIKE $2 OR title ILIKE $2
                    OR concat_ws(' ', make, model, year::text) ILIKE $2)
             ORDER BY last_seen DESC
             LIMIT 10
            """,
            tenant.member_ulids, pattern,
        )
        now = datetime.now(timezone.utc)
        candidates = [
            {
                "vehicleUlid": r["vehicle_ulid"],
                "label": f"{r['make']} {r['model']} {r['year']} · €{float(r['price']):,.0f}".replace(",", ".")
                         if r["price"] is not None else f"{r['make']} {r['model']} {r['year']}",
                "daysInStock": (now - r["first_seen"]).days,
            }
            for r in rows
        ]
        return JSONResponse({"candidates": candidates})


# ---------------------------------------------------------------------------
# GET /deals — paginated list, optional stage filter
# ---------------------------------------------------------------------------

@router.get("")
@limiter.limit(RATE_DEFAULT)
async def list_deals(
    request: Request,
    stage: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=100, ge=1, le=200),
    tenant: TenantContext = Depends(require_tenant),
) -> JSONResponse:
    if stage is not None and stage not in STAGES:
        raise HTTPException(status_code=422, detail=f"stage must be one of {STAGES}")

    offset = (page - 1) * size
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            _DEAL_JOIN_SQL
            + """
             WHERE d.entity_ulid = $1 AND ($2::text IS NULL OR d.stage = $2::crm_deal_stage)
             ORDER BY d.updated_at DESC
             LIMIT $3 OFFSET $4
            """,
            tenant.entity_ulid, stage, size + 1, offset,
        )
        rows, _has_more = page_slice(rows, size)
        total = await c.fetchval(
            "SELECT count(*) FROM crm_deal WHERE entity_ulid = $1 AND ($2::text IS NULL OR stage = $2::crm_deal_stage)",
            tenant.entity_ulid, stage,
        )
        # F5: one batched query for every vehicle referenced on this page, never N+1.
        vehicle_ulids = [r["vehicle_ulid"] for r in rows if r["vehicle_ulid"]]
        contexts = await batch_vehicle_summaries(c, vehicle_ulids)
        items = [_serialize_deal(dict(r), tenant.cdp_code, contexts.get(r["vehicle_ulid"])) for r in rows]
        return JSONResponse({"deals": items, "total": total})


# ---------------------------------------------------------------------------
# GET /deals/{id} — single deal (bare Deal, matches useDeal(id))
# ---------------------------------------------------------------------------

@router.get("/{deal_ulid}")
@limiter.limit(RATE_DEFAULT)
async def get_deal(
    deal_ulid: str,
    request: Request,
    tenant: TenantContext = Depends(require_tenant),
) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        row = await _fetch_deal(c, deal_ulid, tenant.entity_ulid)
        if row is None:
            raise HTTPException(status_code=404, detail=f"deal {deal_ulid} not found")
        return JSONResponse(await _serialize_deal_full(c, row, tenant.cdp_code))


# ---------------------------------------------------------------------------
# POST /deals — create; seeds crm_deal_stage_event(None -> stage) so lead-time replay
# starts from creation, not from the first later transition.
# ---------------------------------------------------------------------------

@router.post("", status_code=201)
@limiter.limit(RATE_DEFAULT)
async def create_deal(
    payload: DealCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_tenant),
) -> JSONResponse:
    if payload.stage not in STAGES:
        raise HTTPException(status_code=422, detail=f"stage must be one of {STAGES}")
    if payload.priority is not None and payload.priority not in PRIORITIES:
        raise HTTPException(status_code=422, detail=f"priority must be one of {PRIORITIES}")

    async with request.app.state.pool.acquire() as c:
        contact = await c.fetchval(
            "SELECT 1 FROM crm_contact WHERE contact_ulid = $1 AND entity_ulid = $2",
            payload.contact_id, tenant.entity_ulid,
        )
        if contact is None:
            raise HTTPException(status_code=404, detail=f"contact {payload.contact_id} not found")

        new_ulid = ulid()
        probability = STAGE_PROBABILITY_DEFAULTS[payload.stage]
        won_at = _now() if payload.stage == "won" else None
        lost_at = _now() if payload.stage == "lost" else None

        try:
            async with c.transaction():
                await c.execute(
                    """
                    INSERT INTO crm_deal (deal_ulid, entity_ulid, contact_ulid, vehicle_ulid, stage,
                                           amount, probability, priority, won_at, lost_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """,
                    new_ulid, tenant.entity_ulid, payload.contact_id, payload.vehicle_id or None,
                    payload.stage, payload.price, probability, payload.priority, won_at, lost_at,
                )
                await c.execute(
                    """
                    INSERT INTO crm_deal_stage_event (event_ulid, deal_ulid, from_stage, to_stage, actor_user_ulid)
                    VALUES ($1, $2, NULL, $3, $4)
                    """,
                    ulid(), new_ulid, payload.stage, tenant.user_ulid,
                )
        except asyncpg.ForeignKeyViolationError as exc:
            raise HTTPException(status_code=404, detail=f"vehicle {payload.vehicle_id} not found") from exc

        row = await _fetch_deal(c, new_ulid, tenant.entity_ulid)
        body = await _serialize_deal_full(c, row, tenant.cdp_code)
    return JSONResponse(body, status_code=201)


# ---------------------------------------------------------------------------
# PATCH /deals/{id} — stage transitions (Kanban drag, "Advance" button), field edits
# ---------------------------------------------------------------------------

@router.patch("/{deal_ulid}")
@limiter.limit(RATE_DEFAULT)
async def update_deal(
    deal_ulid: str,
    payload: DealUpdateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_tenant),
) -> JSONResponse:
    fields_set = payload.model_fields_set

    if "stage" in fields_set and payload.stage is not None and payload.stage not in STAGES:
        raise HTTPException(status_code=422, detail=f"stage must be one of {STAGES}")
    if "priority" in fields_set and payload.priority is not None and payload.priority not in PRIORITIES:
        raise HTTPException(status_code=422, detail=f"priority must be one of {PRIORITIES}")

    async with request.app.state.pool.acquire() as c:
        current = await c.fetchrow(
            "SELECT * FROM crm_deal WHERE deal_ulid = $1 AND entity_ulid = $2", deal_ulid, tenant.entity_ulid
        )
        if current is None:
            raise HTTPException(status_code=404, detail=f"deal {deal_ulid} not found")

        new_stage = current["stage"]
        if "stage" in fields_set and payload.stage is not None:
            new_stage = payload.stage
        stage_changed = new_stage != current["stage"]

        new_amount = float(current["amount"]) if current["amount"] is not None else None
        if "price" in fields_set:
            new_amount = payload.price

        new_priority = current["priority"]
        if "priority" in fields_set:
            new_priority = payload.priority

        new_vehicle = current["vehicle_ulid"]
        if "vehicle_id" in fields_set:
            new_vehicle = payload.vehicle_id or None

        new_probability = float(current["probability"]) if current["probability"] is not None else None
        if "probability" in fields_set:
            new_probability = payload.probability
        elif stage_changed:
            # Caller changed stage without pinning probability -> auto-recompute
            # the new stage's default (carta §4, Salesforce-style behaviour).
            new_probability = STAGE_PROBABILITY_DEFAULTS[new_stage]

        won_at = current["won_at"]
        lost_at = current["lost_at"]
        if stage_changed:
            if new_stage == "won":
                won_at = won_at or _now()
            elif new_stage == "lost":
                lost_at = lost_at or _now()

        try:
            async with c.transaction():
                await c.execute(
                    """
                    UPDATE crm_deal
                       SET stage = $2, amount = $3, probability = $4, priority = $5,
                           vehicle_ulid = $6, won_at = $7, lost_at = $8, updated_at = now()
                     WHERE deal_ulid = $1
                    """,
                    deal_ulid, new_stage, new_amount, new_probability, new_priority, new_vehicle, won_at, lost_at,
                )
                if stage_changed:
                    await c.execute(
                        """
                        INSERT INTO crm_deal_stage_event (event_ulid, deal_ulid, from_stage, to_stage, actor_user_ulid)
                        VALUES ($1, $2, $3, $4, $5)
                        """,
                        ulid(), deal_ulid, current["stage"], new_stage, tenant.user_ulid,
                    )
        except asyncpg.ForeignKeyViolationError as exc:
            raise HTTPException(status_code=404, detail=f"vehicle {payload.vehicle_id} not found") from exc

        row = await _fetch_deal(c, deal_ulid, tenant.entity_ulid)
        body = await _serialize_deal_full(c, row, tenant.cdp_code)
    return JSONResponse(body)
