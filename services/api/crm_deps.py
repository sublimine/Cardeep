"""Shared CRM tenancy resolution — 06-unified-crm-chat F2.

The CRM has NO ``crm_tenant``/``crm_user`` table (00-MASTER.md C-3/C-4 resolution): the
tenant IS the dealer's canonical ``entity_ulid``, reached through AUTH-0's
``dealer_membership`` (migrations/0073_auth.sql). Every ``crm_*`` router scopes every
single query by the entity_ulid this module resolves — the same discipline
``services/api/routers/dealer_ops.py`` already applies via ``resolve_cluster()`` +
``dealer_membership`` for ``fleet_ops``.

Resolution order:
  1. ``X-Tenant-ID`` header (a cdp_code) if present — resolved to its canonical cluster,
     then checked against the caller's ``dealer_membership``. Mismatched/foreign tenant
     -> 403 (never silently falls back — a dealer viewing another dealer's CRM data is
     the exact failure dealer_ops.py's tests guard against).
  2. Otherwise, the caller's OLDEST membership (same "primary tenant" rule
     ``services/api/routers/auth.py::_primary_tenant_cdp`` already uses for ``/auth/me``).
  3. No membership at all -> 403 ("claim a dealer first", AUTH-0's ``/auth/claim-dealer``).
"""
from __future__ import annotations

from fastapi import Depends, Header, HTTPException, Request

from services.api.deps import resolve_cluster
from services.api.routers.auth import CurrentSession, get_current_session


class TenantContext:
    """Resolved (entity_ulid, cdp_code, user_ulid, member_ulids) for the current
    authenticated request. ``member_ulids`` is the FULL dealer cluster (own cross-
    platform duplicate entities) — F5's vehicle-search matcher scopes to it, same as
    dealer_ops.py's fleet-ops bulk read ("sacarle TODO su stock")."""

    __slots__ = ("entity_ulid", "cdp_code", "user_ulid", "member_ulids")

    def __init__(self, entity_ulid: str, cdp_code: str, user_ulid: str, member_ulids: list[str] | None = None) -> None:
        self.entity_ulid = entity_ulid
        self.cdp_code = cdp_code
        self.user_ulid = user_ulid
        self.member_ulids = member_ulids if member_ulids is not None else [entity_ulid]


async def _primary_membership(conn, user_ulid: str) -> tuple[str, str] | None:
    row = await conn.fetchrow(
        """
        SELECT dm.entity_ulid, e.cdp_code
          FROM dealer_membership dm
          JOIN entity e ON e.entity_ulid = dm.entity_ulid
         WHERE dm.user_ulid = $1
         ORDER BY dm.created_at ASC
         LIMIT 1
        """,
        user_ulid,
    )
    return (row["entity_ulid"], row["cdp_code"]) if row is not None else None


async def require_tenant(
    request: Request,
    session: CurrentSession = Depends(get_current_session),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> TenantContext:
    async with request.app.state.pool.acquire() as conn:
        if x_tenant_id:
            cluster = await resolve_cluster(conn, x_tenant_id)
            if cluster is None:
                raise HTTPException(status_code=404, detail=f"tenant {x_tenant_id} not found")
            is_member = await conn.fetchval(
                "SELECT 1 FROM dealer_membership WHERE user_ulid = $1 AND entity_ulid = $2",
                session.user_ulid, cluster.canonical_ulid,
            )
            if not is_member:
                raise HTTPException(status_code=403, detail="you do not manage this tenant")
            return TenantContext(
                cluster.canonical_ulid, cluster.canonical_cdp_code, session.user_ulid, cluster.member_ulids
            )

        primary = await _primary_membership(conn, session.user_ulid)
        if primary is None:
            raise HTTPException(
                status_code=403,
                detail="account has no dealer membership; claim a dealer via /auth/claim-dealer first",
            )
        entity_ulid, cdp_code = primary
        cluster = await resolve_cluster(conn, cdp_code)
        member_ulids = cluster.member_ulids if cluster is not None else [entity_ulid]
        return TenantContext(entity_ulid, cdp_code, session.user_ulid, member_ulids)
