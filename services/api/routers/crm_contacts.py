"""services/api/routers/crm_contacts.py — 06-unified-crm-chat F2.

CRUD for `crm_contact`, scoped by tenant (`services/api/crm_deps.py::require_tenant`),
following the exact pattern `services/api/routers/dealer_ops.py` established (Pydantic
request bodies, `Depends`, transactional writes) — the CRM's first write surface.

Response contract: PLAIN JSON matching `web/src/types.ts::Contact`/`Activity` exactly
(NOT the `{ok,data,error,meta}` envelope the 5 census routers use) — same precedent
AUTH-0 set in `services/api/routers/auth.py`, because `web/src/pages/Contacts.tsx`'s
`ContactList`/`ContactDetail` interfaces and the `useApi<T>` hook already expect this
exact raw shape (`{contacts, total}` / `{contact, activities}`), written before any
backend existed for them.

Phone normalization reuses `pipeline.identity.phone.normalize_e164` (the repo's existing
ES-authoritative E.164 normalizer) instead of a second implementation.
"""
from __future__ import annotations

from typing import Any

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from pipeline.identity.phone import normalize_e164
from pipeline.ids import ulid
from services.api.crm_deps import TenantContext, require_tenant
from services.api.deps import page_slice
from services.api.ics_vcard import build_vcard
from services.api.ratelimit import RATE_DEFAULT, limiter

router = APIRouter(prefix="/contacts", tags=["crm_contacts"])

NAME_MAX = 200
EMAIL_MAX = 254
PHONE_MAX = 32

_ACTIVITY_TYPE_FOR_DIRECTION = {"inbound": "inquiry", "outbound": "reply"}


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class ContactCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=NAME_MAX)
    email: str | None = Field(default=None, max_length=EMAIL_MAX)
    phone: str | None = Field(default=None, max_length=PHONE_MAX)


class ContactUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=NAME_MAX)
    email: str | None = Field(default=None, max_length=EMAIL_MAX)
    phone: str | None = Field(default=None, max_length=PHONE_MAX)


# ---------------------------------------------------------------------------
# Serialization — matches web/src/types.ts field-for-field (camelCase)
# ---------------------------------------------------------------------------

def _serialize_contact(row: dict[str, Any], cdp_code: str, deal_count: int) -> dict[str, Any]:
    return {
        "id": row["contact_ulid"],
        "tenantId": cdp_code,
        "name": row["name"] or "",
        "email": row["email"] or "",
        "phone": row["phone_e164"] or row["phone_raw"] or "",
        "createdAt": row["created_at"].isoformat(),
        "updatedAt": row["updated_at"].isoformat(),
        "dealCount": deal_count,
    }


def _serialize_activity(activity_ulid: str, deal_ulid: str | None, type_: str, body: str,
                         created_at: Any, cdp_code: str) -> dict[str, Any]:
    return {
        "id": activity_ulid,
        "tenantId": cdp_code,
        "dealId": deal_ulid or "",
        "type": type_,
        "body": body,
        "createdAt": created_at.isoformat(),
    }


# ---------------------------------------------------------------------------
# GET /contacts — paginated list, optional free-text search
# ---------------------------------------------------------------------------

@router.get("")
@limiter.limit(RATE_DEFAULT)
async def list_contacts(
    request: Request,
    search: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    tenant: TenantContext = Depends(require_tenant),
) -> JSONResponse:
    offset = (page - 1) * size
    pattern = f"%{search.strip()}%" if search.strip() else None

    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            """
            SELECT ct.*, (SELECT count(*) FROM crm_deal d WHERE d.contact_ulid = ct.contact_ulid) AS deal_count
              FROM crm_contact ct
             WHERE ct.entity_ulid = $1
               AND ($2::text IS NULL OR ct.name ILIKE $2 OR ct.email_lower ILIKE $2
                    OR ct.phone_e164 ILIKE $2 OR ct.phone_raw ILIKE $2)
             ORDER BY ct.updated_at DESC
             LIMIT $3 OFFSET $4
            """,
            tenant.entity_ulid, pattern, size + 1, offset,
        )
        rows, _has_more = page_slice(rows, size)
        total = await c.fetchval(
            """
            SELECT count(*) FROM crm_contact ct
             WHERE ct.entity_ulid = $1
               AND ($2::text IS NULL OR ct.name ILIKE $2 OR ct.email_lower ILIKE $2
                    OR ct.phone_e164 ILIKE $2 OR ct.phone_raw ILIKE $2)
            """,
            tenant.entity_ulid, pattern,
        )
        items = [_serialize_contact(dict(r), tenant.cdp_code, r["deal_count"]) for r in rows]
        return JSONResponse({"contacts": items, "total": total})


# ---------------------------------------------------------------------------
# GET /contacts/{id} — detail + unified timeline (carta §4 "historial unificado")
# ---------------------------------------------------------------------------

@router.get("/{contact_ulid}")
@limiter.limit(RATE_DEFAULT)
async def get_contact(
    contact_ulid: str,
    request: Request,
    tenant: TenantContext = Depends(require_tenant),
) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        row = await c.fetchrow(
            """
            SELECT ct.*, (SELECT count(*) FROM crm_deal d WHERE d.contact_ulid = ct.contact_ulid) AS deal_count
              FROM crm_contact ct
             WHERE ct.contact_ulid = $1 AND ct.entity_ulid = $2
            """,
            contact_ulid, tenant.entity_ulid,
        )
        if row is None:
            raise HTTPException(status_code=404, detail=f"contact {contact_ulid} not found")

        activity_rows = await c.fetch(
            """
            SELECT activity_ulid, deal_ulid, type, body, created_at
              FROM crm_activity
             WHERE contact_ulid = $1
             ORDER BY created_at DESC
             LIMIT 50
            """,
            contact_ulid,
        )
        message_rows = await c.fetch(
            """
            SELECT m.message_ulid AS activity_ulid, conv.deal_ulid, m.direction, m.body, m.sent_at AS created_at
              FROM crm_message m
              JOIN crm_conversation conv ON conv.conversation_ulid = m.conversation_ulid
             WHERE conv.contact_ulid = $1
             ORDER BY m.sent_at DESC
             LIMIT 50
            """,
            contact_ulid,
        )

        merged = [
            (r["created_at"], _serialize_activity(r["activity_ulid"], r["deal_ulid"], r["type"], r["body"],
                                                    r["created_at"], tenant.cdp_code))
            for r in activity_rows
        ] + [
            (r["created_at"], _serialize_activity(r["activity_ulid"], r["deal_ulid"],
                                                    _ACTIVITY_TYPE_FOR_DIRECTION[r["direction"]], r["body"],
                                                    r["created_at"], tenant.cdp_code))
            for r in message_rows
        ]
        merged.sort(key=lambda pair: pair[0], reverse=True)

        return JSONResponse({
            "contact": _serialize_contact(dict(row), tenant.cdp_code, row["deal_count"]),
            "activities": [item for _, item in merged[:50]],
        })


# ---------------------------------------------------------------------------
# GET /contacts/{id}/vcard — F6 RFC 6350 export ("se abre en su iPhone/Android
# directamente"). Verified independently in tests/test_ics_vcard.py via `vobject`.
# ---------------------------------------------------------------------------

@router.get("/{contact_ulid}/vcard")
@limiter.limit(RATE_DEFAULT)
async def export_contact_vcard(
    contact_ulid: str, request: Request, tenant: TenantContext = Depends(require_tenant),
) -> Response:
    async with request.app.state.pool.acquire() as c:
        row = await c.fetchrow(
            "SELECT * FROM crm_contact WHERE contact_ulid = $1 AND entity_ulid = $2", contact_ulid, tenant.entity_ulid
        )
    if row is None:
        raise HTTPException(status_code=404, detail=f"contact {contact_ulid} not found")

    vcard_text = build_vcard(name=row["name"] or "Sin nombre", phone_e164=row["phone_e164"], email=row["email"])
    return Response(
        content=vcard_text, media_type="text/vcard",
        headers={"Content-Disposition": f'attachment; filename="{contact_ulid}.vcf"'},
    )


# ---------------------------------------------------------------------------
# POST /contacts — anti-decorative-button: "Save contact" must persist for real
# ---------------------------------------------------------------------------

@router.post("", status_code=201)
@limiter.limit(RATE_DEFAULT)
async def create_contact(
    payload: ContactCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_tenant),
) -> JSONResponse:
    email_lower = payload.email.strip().lower() if payload.email and payload.email.strip() else None
    phone_raw = payload.phone.strip() if payload.phone and payload.phone.strip() else None
    phone_e164 = normalize_e164(phone_raw) if phone_raw else None
    new_ulid = ulid()

    async with request.app.state.pool.acquire() as c:
        try:
            await c.execute(
                """
                INSERT INTO crm_contact (contact_ulid, entity_ulid, name, email, phone_raw, phone_e164)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                new_ulid, tenant.entity_ulid, payload.name.strip(), email_lower, phone_raw, phone_e164,
            )
        except asyncpg.UniqueViolationError as exc:
            raise HTTPException(
                status_code=409, detail="a contact with this phone or email already exists for this tenant"
            ) from exc

        row = await c.fetchrow("SELECT * FROM crm_contact WHERE contact_ulid = $1", new_ulid)
    return JSONResponse(_serialize_contact(dict(row), tenant.cdp_code, 0), status_code=201)


# ---------------------------------------------------------------------------
# PATCH /contacts/{id} — edit
# ---------------------------------------------------------------------------

@router.patch("/{contact_ulid}")
@limiter.limit(RATE_DEFAULT)
async def update_contact(
    contact_ulid: str,
    payload: ContactUpdateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_tenant),
) -> JSONResponse:
    fields_set = payload.model_fields_set
    async with request.app.state.pool.acquire() as c:
        current = await c.fetchrow(
            "SELECT * FROM crm_contact WHERE contact_ulid = $1 AND entity_ulid = $2", contact_ulid, tenant.entity_ulid
        )
        if current is None:
            raise HTTPException(status_code=404, detail=f"contact {contact_ulid} not found")

        new_name = payload.name.strip() if "name" in fields_set and payload.name else current["name"]
        new_email = current["email"]
        if "email" in fields_set:
            new_email = payload.email.strip().lower() if payload.email and payload.email.strip() else None
        new_phone_raw = current["phone_raw"]
        new_phone_e164 = current["phone_e164"]
        if "phone" in fields_set:
            new_phone_raw = payload.phone.strip() if payload.phone and payload.phone.strip() else None
            new_phone_e164 = normalize_e164(new_phone_raw) if new_phone_raw else None

        try:
            await c.execute(
                """
                UPDATE crm_contact
                   SET name = $2, email = $3, phone_raw = $4, phone_e164 = $5, updated_at = now()
                 WHERE contact_ulid = $1
                """,
                contact_ulid, new_name, new_email, new_phone_raw, new_phone_e164,
            )
        except asyncpg.UniqueViolationError as exc:
            raise HTTPException(
                status_code=409, detail="a contact with this phone or email already exists for this tenant"
            ) from exc

        deal_count = await c.fetchval("SELECT count(*) FROM crm_deal WHERE contact_ulid = $1", contact_ulid)
        row = await c.fetchrow("SELECT * FROM crm_contact WHERE contact_ulid = $1", contact_ulid)
    return JSONResponse(_serialize_contact(dict(row), tenant.cdp_code, deal_count))


# ---------------------------------------------------------------------------
# DELETE /contacts/{id} — blocked (409) while the contact still owns real
# relationship rows (deals/conversations); no frontend surface calls this yet.
# ---------------------------------------------------------------------------

@router.delete("/{contact_ulid}", status_code=204)
@limiter.limit(RATE_DEFAULT)
async def delete_contact(
    contact_ulid: str,
    request: Request,
    tenant: TenantContext = Depends(require_tenant),
) -> Response:
    async with request.app.state.pool.acquire() as c:
        current = await c.fetchrow(
            "SELECT 1 FROM crm_contact WHERE contact_ulid = $1 AND entity_ulid = $2", contact_ulid, tenant.entity_ulid
        )
        if current is None:
            raise HTTPException(status_code=404, detail=f"contact {contact_ulid} not found")
        try:
            await c.execute("DELETE FROM crm_contact WHERE contact_ulid = $1", contact_ulid)
        except asyncpg.ForeignKeyViolationError as exc:
            raise HTTPException(
                status_code=409,
                detail="contact has deals or conversations attached; cannot delete",
            ) from exc
    return Response(status_code=204)
