"""services/api/routers/crm_inbox.py — 06-unified-crm-chat F4.

Serves the EXACT paths `web/src/hooks/useInbox.ts` has called since before this router
existed (`GET /inbox`, `GET /inbox/{id}`, `POST /inbox/{id}/reply`, `PATCH /inbox/{id}`) —
the frontend contract predates the backend (same precedent as `auth.py`/`crm_contacts.py`).
Response contract: PLAIN JSON matching `web/src/types.ts::Conversation`/`Message`.

Channel: email only (F4 scope; WhatsApp is F7, gated). Sending goes through
`services/crm/email_send.py` (SMTP); every outbound message's "Enviado" state is gated
on a REAL provider ACK (carta §7 protocol) — never a bare 200 from this endpoint.
"""
from __future__ import annotations

from typing import Any

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from pipeline.ids import ulid
from services.api.crm_deps import TenantContext, require_tenant
from services.api.deps import page_slice
from services.api.ratelimit import RATE_DEFAULT, limiter
from services.api.vehicle_context import batch_vehicle_summaries, compute_vehicle_context
from services.crm.email_send import EmailSendError, send_email

router = APIRouter(prefix="/inbox", tags=["crm_inbox"])

CONVERSATION_STATUSES: tuple[str, ...] = ("open", "replied", "closed", "spam")


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class ReplyRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    body: str = Field(..., min_length=1)
    template_id: str | None = Field(default=None, alias="template_id")
    send_via: str = Field(default="email", alias="send_via")


class ConversationPatchRequest(BaseModel):
    status: str | None = Field(default=None)
    unread: bool | None = Field(default=None)


# ---------------------------------------------------------------------------
# Serialization — matches web/src/types.ts::Conversation/Message field-for-field
# ---------------------------------------------------------------------------

def _serialize_conversation(row: dict[str, Any], cdp_code: str, vehicle_context: dict[str, Any] | None = None) -> dict[str, Any]:
    last_at = row["last_message_at"] or row["created_at"]
    return {
        "id": row["conversation_ulid"],
        "tenantId": cdp_code,
        "contactId": row["contact_ulid"],
        "vehicleId": row["vehicle_ulid"] or "",
        "dealId": row["deal_ulid"] or "",
        "sourcePlatform": row["source_platform"] or "manual",
        "externalId": row.get("external_id") or "",
        "subject": row["subject"] or "",
        "status": row["status"],
        "unread": (row.get("unread_count") or 0) > 0,
        "lastMessageAt": last_at.isoformat(),
        "createdAt": row["created_at"].isoformat(),
        "contactName": row.get("contact_name"),
        "vehicleName": row.get("vehicle_name"),
        "previewBody": row.get("preview_body"),
        # F5: carta §4 "chip de vehículo" — only present when vehicle_ulid resolves
        # against the live census; absent (never fabricated) otherwise.
        "vehicleContext": vehicle_context,
    }


def _serialize_message(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["message_ulid"],
        "conversationId": row["conversation_ulid"],
        "direction": row["direction"],
        "senderName": row["sender_name"] or "",
        "senderEmail": row["sender_email"] or "",
        "body": row["body"],
        "templateId": row["template_ulid"] or None,
        "sentVia": row["sent_via"],
        "sentAt": row["sent_at"].isoformat(),
        "readAt": row["read_at"].isoformat() if row["read_at"] else None,
    }


_CONV_LIST_SQL = """
    SELECT conv.*, ct.name AS contact_name,
           CASE WHEN v.vehicle_ulid IS NOT NULL
                THEN concat_ws(' ', v.make, v.model, v.year::text)
           END AS vehicle_name,
           (SELECT count(*) FROM crm_message m
             WHERE m.conversation_ulid = conv.conversation_ulid
               AND m.direction = 'inbound' AND m.read_at IS NULL) AS unread_count,
           (SELECT body FROM crm_message m
             WHERE m.conversation_ulid = conv.conversation_ulid
             ORDER BY m.sent_at DESC LIMIT 1) AS preview_body,
           (SELECT provider_message_id FROM crm_message m
             WHERE m.conversation_ulid = conv.conversation_ulid
             ORDER BY m.sent_at ASC LIMIT 1) AS external_id
      FROM crm_conversation conv
      LEFT JOIN crm_contact ct ON ct.contact_ulid = conv.contact_ulid
      LEFT JOIN vehicle v ON v.vehicle_ulid = conv.vehicle_ulid
"""


# ---------------------------------------------------------------------------
# GET /inbox — paginated conversation list, optional status filter
# ---------------------------------------------------------------------------

@router.get("")
@limiter.limit(RATE_DEFAULT)
async def list_conversations(
    request: Request,
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    tenant: TenantContext = Depends(require_tenant),
) -> JSONResponse:
    if status is not None and status not in CONVERSATION_STATUSES:
        raise HTTPException(status_code=422, detail=f"status must be one of {CONVERSATION_STATUSES}")

    offset = (page - 1) * size
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            _CONV_LIST_SQL
            + """
             WHERE conv.entity_ulid = $1 AND ($2::text IS NULL OR conv.status = $2::crm_conversation_status)
             ORDER BY conv.last_message_at DESC NULLS LAST, conv.created_at DESC
             LIMIT $3 OFFSET $4
            """,
            tenant.entity_ulid, status, size + 1, offset,
        )
        rows, _has_more = page_slice(rows, size)
        total = await c.fetchval(
            "SELECT count(*) FROM crm_conversation WHERE entity_ulid = $1 AND ($2::text IS NULL OR status = $2::crm_conversation_status)",
            tenant.entity_ulid, status,
        )
        # F5: one batched query for every vehicle referenced on this page, never N+1.
        vehicle_ulids = [r["vehicle_ulid"] for r in rows if r["vehicle_ulid"]]
        contexts = await batch_vehicle_summaries(c, vehicle_ulids)
        items = [_serialize_conversation(dict(r), tenant.cdp_code, contexts.get(r["vehicle_ulid"])) for r in rows]
        return JSONResponse({"conversations": items, "total": total})


# ---------------------------------------------------------------------------
# GET /inbox/stream — SSE refresh signal (F4). Declared BEFORE `/{conversation_ulid}`
# so FastAPI's registration-order matching does not swallow "stream" as a path param
# (same fix as crm_deals.py's `/summary` vs `/{deal_ulid}`). EventSource cannot set an
# Authorization header, so auth here is a raw session token in the query string (same
# opaque-token verification as get_current_session, just sourced differently).
# ---------------------------------------------------------------------------

async def _resolve_session_from_token(request: Request, raw_token: str) -> str | None:
    """Return user_ulid for a live session token, or None. Mirrors
    services/api/routers/auth.py::get_current_session's query, minus the header parsing."""
    from services.api.auth_security import hash_token

    async with request.app.state.pool.acquire() as c:
        row = await c.fetchrow(
            "SELECT user_ulid FROM user_session WHERE token_hash = $1 AND revoked_at IS NULL AND expires_at > now()",
            hash_token(raw_token),
        )
    return row["user_ulid"] if row is not None else None


@router.get("/stream")
async def inbox_stream(
    request: Request,
    token: str = Query(...),
    tenant_id: str = Query(..., alias="tenant"),
) -> StreamingResponse:
    """Emits an SSE event whenever the tenant's inbox state changes (new inbound message,
    status change). Poll-based (2s) rather than LISTEN/NOTIFY — simplest correct
    implementation for this pilar's traffic scale; no new infra dependency."""
    user_ulid = await _resolve_session_from_token(request, token)
    if user_ulid is None:
        raise HTTPException(status_code=401, detail="invalid or expired session")

    async with request.app.state.pool.acquire() as c:
        is_member = await c.fetchval(
            "SELECT 1 FROM dealer_membership dm JOIN entity e ON e.entity_ulid = dm.entity_ulid "
            "WHERE dm.user_ulid = $1 AND e.cdp_code = $2",
            user_ulid, tenant_id,
        )
    if not is_member:
        raise HTTPException(status_code=403, detail="you do not manage this tenant")

    async def event_source():
        import asyncio
        import json as _json

        last_seen_at = None
        # Initial retry hint for the browser's EventSource reconnect backoff.
        yield "retry: 3000\n\n"
        while True:
            if await request.is_disconnected():
                break
            async with request.app.state.pool.acquire() as c:
                row = await c.fetchrow(
                    """
                    SELECT max(GREATEST(last_message_at, created_at)) AS latest
                      FROM crm_conversation WHERE entity_ulid = (
                          SELECT entity_ulid FROM entity WHERE cdp_code = $1
                      )
                    """,
                    tenant_id,
                )
            latest = row["latest"] if row else None
            if latest is not None and latest != last_seen_at:
                last_seen_at = latest
                yield f"data: {_json.dumps({'type': 'inbox_updated', 'at': latest.isoformat()})}\n\n"
            await asyncio.sleep(2)

    return StreamingResponse(event_source(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# GET /inbox/{id} — thread detail; opening a conversation marks its inbound
# messages read (carta §7 E2E protocol: "el contador decrementa exactamente en
# el nº de mensajes marcados").
# ---------------------------------------------------------------------------

@router.get("/{conversation_ulid}")
@limiter.limit(RATE_DEFAULT)
async def get_conversation(
    conversation_ulid: str,
    request: Request,
    tenant: TenantContext = Depends(require_tenant),
) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        row = await c.fetchrow(
            _CONV_LIST_SQL + " WHERE conv.conversation_ulid = $1 AND conv.entity_ulid = $2",
            conversation_ulid, tenant.entity_ulid,
        )
        if row is None:
            raise HTTPException(status_code=404, detail=f"conversation {conversation_ulid} not found")

        await c.execute(
            """
            UPDATE crm_message SET read_at = now()
             WHERE conversation_ulid = $1 AND direction = 'inbound' AND read_at IS NULL
            """,
            conversation_ulid,
        )

        message_rows = await c.fetch(
            "SELECT * FROM crm_message WHERE conversation_ulid = $1 ORDER BY sent_at ASC",
            conversation_ulid,
        )
        # Re-read the conversation row so `unread` reflects the just-applied read_at update.
        fresh = await c.fetchrow(
            _CONV_LIST_SQL + " WHERE conv.conversation_ulid = $1 AND conv.entity_ulid = $2",
            conversation_ulid, tenant.entity_ulid,
        )
        vehicle_context = (
            await compute_vehicle_context(c, fresh["vehicle_ulid"]) if fresh["vehicle_ulid"] else None
        )
        return JSONResponse({
            "conversation": _serialize_conversation(dict(fresh), tenant.cdp_code, vehicle_context),
            "messages": [_serialize_message(dict(m)) for m in message_rows],
        })


# ---------------------------------------------------------------------------
# POST /inbox/{id}/reply — send via the conversation's channel (F4: email only).
# "Enviado" is gated on a REAL SMTP ACK — never painted from a bare 200 (carta §7).
# ---------------------------------------------------------------------------

@router.post("/{conversation_ulid}/reply", status_code=201)
@limiter.limit(RATE_DEFAULT)
async def reply(
    conversation_ulid: str,
    payload: ReplyRequest,
    request: Request,
    tenant: TenantContext = Depends(require_tenant),
) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        conv = await c.fetchrow(
            "SELECT * FROM crm_conversation WHERE conversation_ulid = $1 AND entity_ulid = $2",
            conversation_ulid, tenant.entity_ulid,
        )
        if conv is None:
            raise HTTPException(status_code=404, detail=f"conversation {conversation_ulid} not found")
        if conv["channel"] != "email":
            raise HTTPException(
                status_code=422,
                detail=f"channel '{conv['channel']}' has no send integration yet (F4 = email only)",
            )

        contact = await c.fetchrow("SELECT * FROM crm_contact WHERE contact_ulid = $1", conv["contact_ulid"])
        if contact is None or not contact["email"]:
            raise HTTPException(status_code=422, detail="contact has no email address on file")

        # Find the Message-ID of the last INBOUND message, if any, for In-Reply-To threading.
        last_inbound_id = await c.fetchval(
            """
            SELECT provider_message_id FROM crm_message
             WHERE conversation_ulid = $1 AND direction = 'inbound' AND provider_message_id IS NOT NULL
             ORDER BY sent_at DESC LIMIT 1
            """,
            conversation_ulid,
        )

        try:
            sent_message_id = send_email(
                to_addr=contact["email"],
                subject=conv["subject"] or "Re: tu consulta",
                body=payload.body,
                in_reply_to=last_inbound_id,
            )
        except EmailSendError as exc:
            # Never a fake "sent" check — the caller sees the real failure (carta §6).
            raise HTTPException(status_code=502, detail=f"No se pudo enviar: {exc}") from exc

        new_ulid = ulid()
        async with c.transaction():
            await c.execute(
                """
                INSERT INTO crm_message (message_ulid, conversation_ulid, direction, sender_name, sender_email,
                                          body, template_ulid, sent_via, provider_message_id, provider_ack_at)
                VALUES ($1, $2, 'outbound', $3, $4, $5, $6, 'email', $7, now())
                """,
                new_ulid, conversation_ulid, None, None, payload.body, payload.template_id, sent_message_id,
            )
            await c.execute(
                "UPDATE crm_conversation SET status = 'replied', last_message_at = now() WHERE conversation_ulid = $1",
                conversation_ulid,
            )

        row = await c.fetchrow("SELECT * FROM crm_message WHERE message_ulid = $1", new_ulid)
    return JSONResponse(_serialize_message(dict(row)), status_code=201)


# ---------------------------------------------------------------------------
# PATCH /inbox/{id} — status / read-state changes
# ---------------------------------------------------------------------------

@router.patch("/{conversation_ulid}")
@limiter.limit(RATE_DEFAULT)
async def patch_conversation(
    conversation_ulid: str,
    payload: ConversationPatchRequest,
    request: Request,
    tenant: TenantContext = Depends(require_tenant),
) -> JSONResponse:
    fields_set = payload.model_fields_set
    if "status" in fields_set and payload.status is not None and payload.status not in CONVERSATION_STATUSES:
        raise HTTPException(status_code=422, detail=f"status must be one of {CONVERSATION_STATUSES}")

    async with request.app.state.pool.acquire() as c:
        current = await c.fetchrow(
            "SELECT * FROM crm_conversation WHERE conversation_ulid = $1 AND entity_ulid = $2",
            conversation_ulid, tenant.entity_ulid,
        )
        if current is None:
            raise HTTPException(status_code=404, detail=f"conversation {conversation_ulid} not found")

        new_status = payload.status if ("status" in fields_set and payload.status is not None) else current["status"]

        async with c.transaction():
            await c.execute(
                "UPDATE crm_conversation SET status = $2 WHERE conversation_ulid = $1", conversation_ulid, new_status
            )
            if "unread" in fields_set and payload.unread is False:
                await c.execute(
                    """
                    UPDATE crm_message SET read_at = now()
                     WHERE conversation_ulid = $1 AND direction = 'inbound' AND read_at IS NULL
                    """,
                    conversation_ulid,
                )

        row = await c.fetchrow(
            _CONV_LIST_SQL + " WHERE conv.conversation_ulid = $1 AND conv.entity_ulid = $2",
            conversation_ulid, tenant.entity_ulid,
        )
    return JSONResponse(_serialize_conversation(dict(row), tenant.cdp_code))
