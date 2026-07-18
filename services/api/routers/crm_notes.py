"""services/api/routers/crm_notes.py — 06-unified-crm-chat F6.

CRUD for `crm_note`, scoped by tenant — replaces `web/src/pages/Notes.tsx`'s
localStorage persistence (carta §1 gap #6: "Notas sincronizadas entre el móvil del
comercial y el PC de la oficina — hoy se pierden al limpiar caché — inaceptable").

Response contract: PLAIN JSON matching `web/src/types.ts::Note` (see F6 addition) —
same precedent as every other crm_* router (auth.py/crm_contacts.py/crm_deals.py).
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from pipeline.ids import ulid
from services.api.crm_deps import TenantContext, require_tenant
from services.api.ratelimit import RATE_DEFAULT, limiter

router = APIRouter(prefix="/notes", tags=["crm_notes"])

NOTE_COLORS: tuple[str, ...] = ("neutral", "amber", "sky", "emerald", "rose")
TITLE_MAX = 200
BODY_MAX = 8000


class NoteCreateRequest(BaseModel):
    title: str = Field(default="", max_length=TITLE_MAX)
    body: str = Field(default="", max_length=BODY_MAX)
    color: str = Field(default="neutral")
    pinned: bool = Field(default=False)


class NoteUpdateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=TITLE_MAX)
    body: str | None = Field(default=None, max_length=BODY_MAX)
    color: str | None = Field(default=None)
    pinned: bool | None = Field(default=None)


def _serialize_note(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["note_ulid"],
        "title": row["title"] or "",
        "body": row["body"] or "",
        "color": row["color"],
        "pinned": row["pinned"],
        "createdAt": row["created_at"].isoformat(),
        "updatedAt": row["updated_at"].isoformat(),
    }


@router.get("")
@limiter.limit(RATE_DEFAULT)
async def list_notes(request: Request, tenant: TenantContext = Depends(require_tenant)) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            "SELECT * FROM crm_note WHERE entity_ulid = $1 ORDER BY pinned DESC, updated_at DESC",
            tenant.entity_ulid,
        )
    return JSONResponse({"notes": [_serialize_note(dict(r)) for r in rows]})


@router.post("", status_code=201)
@limiter.limit(RATE_DEFAULT)
async def create_note(
    payload: NoteCreateRequest, request: Request, tenant: TenantContext = Depends(require_tenant),
) -> JSONResponse:
    if payload.color not in NOTE_COLORS:
        raise HTTPException(status_code=422, detail=f"color must be one of {NOTE_COLORS}")

    new_ulid = ulid()
    async with request.app.state.pool.acquire() as c:
        await c.execute(
            """
            INSERT INTO crm_note (note_ulid, entity_ulid, author_user_ulid, title, body, color, pinned)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            new_ulid, tenant.entity_ulid, tenant.user_ulid, payload.title, payload.body, payload.color, payload.pinned,
        )
        row = await c.fetchrow("SELECT * FROM crm_note WHERE note_ulid = $1", new_ulid)
    return JSONResponse(_serialize_note(dict(row)), status_code=201)


@router.patch("/{note_ulid}")
@limiter.limit(RATE_DEFAULT)
async def update_note(
    note_ulid: str, payload: NoteUpdateRequest, request: Request,
    tenant: TenantContext = Depends(require_tenant),
) -> JSONResponse:
    fields_set = payload.model_fields_set
    if "color" in fields_set and payload.color is not None and payload.color not in NOTE_COLORS:
        raise HTTPException(status_code=422, detail=f"color must be one of {NOTE_COLORS}")

    async with request.app.state.pool.acquire() as c:
        current = await c.fetchrow(
            "SELECT * FROM crm_note WHERE note_ulid = $1 AND entity_ulid = $2", note_ulid, tenant.entity_ulid
        )
        if current is None:
            raise HTTPException(status_code=404, detail=f"note {note_ulid} not found")

        new_title = payload.title if "title" in fields_set and payload.title is not None else current["title"]
        new_body = payload.body if "body" in fields_set and payload.body is not None else current["body"]
        new_color = payload.color if "color" in fields_set and payload.color is not None else current["color"]
        new_pinned = payload.pinned if "pinned" in fields_set and payload.pinned is not None else current["pinned"]

        await c.execute(
            """
            UPDATE crm_note SET title = $2, body = $3, color = $4, pinned = $5, updated_at = now()
             WHERE note_ulid = $1
            """,
            note_ulid, new_title, new_body, new_color, new_pinned,
        )
        row = await c.fetchrow("SELECT * FROM crm_note WHERE note_ulid = $1", note_ulid)
    return JSONResponse(_serialize_note(dict(row)))


@router.delete("/{note_ulid}", status_code=204)
@limiter.limit(RATE_DEFAULT)
async def delete_note(
    note_ulid: str, request: Request, tenant: TenantContext = Depends(require_tenant),
) -> Response:
    async with request.app.state.pool.acquire() as c:
        current = await c.fetchval(
            "SELECT 1 FROM crm_note WHERE note_ulid = $1 AND entity_ulid = $2", note_ulid, tenant.entity_ulid
        )
        if current is None:
            raise HTTPException(status_code=404, detail=f"note {note_ulid} not found")
        await c.execute("DELETE FROM crm_note WHERE note_ulid = $1", note_ulid)
    return Response(status_code=204)
