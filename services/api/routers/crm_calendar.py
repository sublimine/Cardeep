"""services/api/routers/crm_calendar.py — 06-unified-crm-chat F6.

CRUD for `crm_event`, scoped by tenant — replaces `web/src/pages/Calendar.tsx`'s
MOCK_EVENTS with real per-tenant persistence, plus RFC 5545 (.ics) export per event
(`GET /calendar/events/{id}/ics`) so a dealer's calendar opens directly in Google
Calendar/Outlook/Apple Calendar without explaining what CalDAV is (carta §6).

Response contract: PLAIN JSON matching `web/src/types.ts::CalEvent` (F6 addition) for
the CRUD surface; the `.ics` endpoint returns `text/calendar` (RFC 5545), not JSON.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from pipeline.ids import ulid
from services.api.crm_deps import TenantContext, require_tenant
from services.api.ics_vcard import build_ics_event
from services.api.ratelimit import RATE_DEFAULT, limiter

router = APIRouter(prefix="/calendar", tags=["crm_calendar"])

EVENT_TYPES: tuple[str, ...] = ("visit", "call", "reminder", "delivery")
TITLE_MAX = 200


class EventCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(..., min_length=1, max_length=TITLE_MAX)
    starts_at: str = Field(..., alias="startsAt")  # ISO 8601
    ends_at: str | None = Field(default=None, alias="endsAt")
    type: str = Field(default="visit")
    location: str | None = Field(default=None)
    contact_id: str | None = Field(default=None, alias="contactId")
    deal_id: str | None = Field(default=None, alias="dealId")


def _serialize_event(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["event_ulid"],
        "title": row["title"],
        "startsAt": row["starts_at"].isoformat(),
        "endsAt": row["ends_at"].isoformat() if row["ends_at"] else None,
        "type": row["event_type"],
        "location": row["location"],
        "contactId": row["contact_ulid"],
        "contactName": row.get("contact_name"),
        "dealId": row["deal_ulid"],
        "createdAt": row["created_at"].isoformat(),
    }


_EVENT_JOIN_SQL = """
    SELECT e.*, ct.name AS contact_name
      FROM crm_event e
      LEFT JOIN crm_contact ct ON ct.contact_ulid = e.contact_ulid
"""


def _parse_iso(value: str, field: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"{field} must be a valid ISO 8601 datetime") from exc
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


@router.get("/events")
@limiter.limit(RATE_DEFAULT)
async def list_events(
    request: Request,
    start: str | None = Query(default=None),
    end: str | None = Query(default=None),
    tenant: TenantContext = Depends(require_tenant),
) -> JSONResponse:
    start_dt = _parse_iso(start, "start") if start else None
    end_dt = _parse_iso(end, "end") if end else None
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            _EVENT_JOIN_SQL
            + """
             WHERE e.entity_ulid = $1
               AND ($2::timestamptz IS NULL OR e.starts_at >= $2)
               AND ($3::timestamptz IS NULL OR e.starts_at <= $3)
             ORDER BY e.starts_at ASC
            """,
            tenant.entity_ulid, start_dt, end_dt,
        )
    return JSONResponse({"events": [_serialize_event(dict(r)) for r in rows]})


@router.post("/events", status_code=201)
@limiter.limit(RATE_DEFAULT)
async def create_event(
    payload: EventCreateRequest, request: Request, tenant: TenantContext = Depends(require_tenant),
) -> JSONResponse:
    if payload.type not in EVENT_TYPES:
        raise HTTPException(status_code=422, detail=f"type must be one of {EVENT_TYPES}")
    starts_at = _parse_iso(payload.starts_at, "startsAt")
    ends_at = _parse_iso(payload.ends_at, "endsAt") if payload.ends_at else None

    new_ulid = ulid()
    async with request.app.state.pool.acquire() as c:
        if payload.contact_id:
            exists = await c.fetchval(
                "SELECT 1 FROM crm_contact WHERE contact_ulid = $1 AND entity_ulid = $2",
                payload.contact_id, tenant.entity_ulid,
            )
            if exists is None:
                raise HTTPException(status_code=404, detail=f"contact {payload.contact_id} not found")

        await c.execute(
            """
            INSERT INTO crm_event (event_ulid, entity_ulid, title, starts_at, ends_at, event_type,
                                    location, contact_ulid, deal_ulid, created_by_user_ulid)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """,
            new_ulid, tenant.entity_ulid, payload.title, starts_at, ends_at, payload.type,
            payload.location, payload.contact_id, payload.deal_id, tenant.user_ulid,
        )
        row = await c.fetchrow(_EVENT_JOIN_SQL + " WHERE e.event_ulid = $1", new_ulid)
    return JSONResponse(_serialize_event(dict(row)), status_code=201)


@router.delete("/events/{event_ulid}", status_code=204)
@limiter.limit(RATE_DEFAULT)
async def delete_event(
    event_ulid: str, request: Request, tenant: TenantContext = Depends(require_tenant),
) -> Response:
    async with request.app.state.pool.acquire() as c:
        exists = await c.fetchval(
            "SELECT 1 FROM crm_event WHERE event_ulid = $1 AND entity_ulid = $2", event_ulid, tenant.entity_ulid
        )
        if exists is None:
            raise HTTPException(status_code=404, detail=f"event {event_ulid} not found")
        await c.execute("DELETE FROM crm_event WHERE event_ulid = $1", event_ulid)
    return Response(status_code=204)


@router.get("/events/{event_ulid}/ics")
@limiter.limit(RATE_DEFAULT)
async def export_event_ics(
    event_ulid: str, request: Request, tenant: TenantContext = Depends(require_tenant),
) -> Response:
    """RFC 5545 export — carta §6: "export .ics -> aparece en su Google Calendar
    sin explicarle qué es CalDAV". Verified independently in
    tests/test_ics_vcard.py via the `icalendar` library (not this module's own code)."""
    async with request.app.state.pool.acquire() as c:
        row = await c.fetchrow(
            "SELECT * FROM crm_event WHERE event_ulid = $1 AND entity_ulid = $2", event_ulid, tenant.entity_ulid
        )
    if row is None:
        raise HTTPException(status_code=404, detail=f"event {event_ulid} not found")

    ics_text = build_ics_event(
        uid=row["event_ulid"], title=row["title"], starts_at=row["starts_at"], ends_at=row["ends_at"],
        location=row["location"],
    )
    return Response(
        content=ics_text, media_type="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="{row["event_ulid"]}.ics"'},
    )
