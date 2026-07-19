"""AUTH-0 — /auth/* router: register, login, session, dealer-role claim.

Resolution: 00-MASTER.md §2 C-3. This router is the single fusion of what four cartas
(03-garage-fleet F1, 05-multiposting F3, 06-unified-crm-chat F1-tenancy,
08-forum-community F1) each independently planned to build. Schema lives in
``migrations/0073_auth.sql``; hashing/token primitives live in
``services/api/auth_security.py``; identity checksum validation reuses
``services/api/tax_id.py`` (already in the repo, built for CAPA-0 hard-key validation).

Response contract — deliberately DIFFERENT from the other 5 routers
---------------------------------------------------------------------
``entities.py``/``geo.py``/``ops.py``/``platforms.py``/``vehicles.py`` all wrap responses
in the data-API envelope ``{ok, data, error, meta}``. This router does NOT: it returns
plain JSON matching the shapes ``web/src/auth/AuthContext.tsx`` and ``web/src/api/client.ts``
already call against (``{token, expires_in, user}`` for register/login/refresh,
``{user}`` for /me and /claim-dealer, 204 for /logout) — that frontend contract predates
this router (it was written expecting a real backend behind the ``DEV_BYPASS`` flag) and
changing it would mean a SECOND rewire of the frontend for no benefit. Errors use plain
FastAPI ``HTTPException`` (client.ts reads the body as text on non-2xx, never parses the
envelope), consistent with how ``client.ts`` already treats 401 specially (dispatches
``auth:unauthorized`` and logs out).

Security posture (security review — see plans/cardeep-omni/AUTH-0.md):
  * Argon2id via ``auth_security.py``; timing-safe verification against a dummy hash so a
    login attempt cannot distinguish "wrong password" from "no such account".
  * Sessions are opaque high-entropy tokens; only their SHA-256 hash is persisted. Refresh
    ROTATES the token (old session revoked, new one minted) rather than extending the same
    row, bounding the replay window of a leaked token.
  * RATE_AUTH (10/minute/IP, tighter than RATE_DEFAULT) on every credential-guessing surface:
    register, login, claim-dealer.
  * Dealer-role elevation (``/auth/claim-dealer``) requires a tax ID that (a) passes its
    official BOE checksum (``tax_id.canonical_tax_id``) and (b) matches the census's
    ``entity.cif`` for the claimed ``cdp_code`` — claiming somebody else's dealer profile
    requires knowing their real registered tax ID, not just its public cdp_code.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any

import asyncpg
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from pipeline.ids import ulid
from services.api.auth_security import (
    ACCESS_TOKEN_TTL_SECONDS,
    MAX_PASSWORD_LENGTH,
    hash_password,
    hash_token,
    new_raw_token,
    validate_password_policy,
    verify_password,
)
from services.api.deps import resolve_cluster
from services.api.ratelimit import RATE_AUTH, RATE_DEFAULT, limiter
from services.api.tax_id import canonical_tax_id

router = APIRouter(prefix="/auth", tags=["auth"])

EMAIL_MAX_LENGTH = 254  # RFC 5321 practical envelope limit
NAME_MAX_LENGTH = 200
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=EMAIL_MAX_LENGTH)
    password: str = Field(..., max_length=MAX_PASSWORD_LENGTH)
    name: str = Field(default="", max_length=NAME_MAX_LENGTH)

    @field_validator("email")
    @classmethod
    def _valid_email(cls, v: str) -> str:
        v = v.strip()
        if not _EMAIL_RE.match(v):
            raise ValueError("valid email is required")
        return v.lower()


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=EMAIL_MAX_LENGTH)
    password: str = Field(..., max_length=MAX_PASSWORD_LENGTH)


class ClaimDealerRequest(BaseModel):
    cdp_code: str = Field(..., min_length=1, max_length=64)
    tax_id: str = Field(..., min_length=1, max_length=32)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _serialize_user(row: dict[str, Any]) -> dict[str, Any]:
    """Shape matching web/src/types.ts::User. ``tenant_id`` (snake_case) is read by
    AuthContext.tsx's existing fallback ``raw.tenantId ?? raw.tenant_id ?? ''``."""
    return {
        "id": row["user_ulid"],
        "email": row["email"],
        "name": row["name"] or "",
        "role": row["role"],
        "tenant_id": row.get("tenant_id") or "",
        "plan": row.get("plan") or "starter",
    }


async def _primary_tenant_cdp(conn: asyncpg.Connection, user_ulid: str) -> str | None:
    """The dealer tenant is the entity reached via dealer_membership (MASTER C-3: no
    separate crm_tenant/dealer_account table). Oldest membership wins as "primary" —
    multi-rooftop tenant switching is a future carta's UI, not AUTH-0's job.

    ``country_code = 'ES'`` (tests/test_served_queries_have_country.py): this is the first
    served census query that goes user -> entity (every other one is cdp_code/entity_ulid
    scoped, which already pins the tenant). Explicit today because the program is ES-only
    (pipeline/codes.py DEFAULT_COUNTRY); threading a real country parameter here is the same
    pattern the rest of the pipeline already uses for its country-parametrized coders.
    """
    row = await conn.fetchrow(
        """
        SELECT e.cdp_code
          FROM dealer_membership dm
          JOIN entity e ON e.entity_ulid = dm.entity_ulid
         WHERE dm.user_ulid = $1
           AND e.country_code = 'ES'
         ORDER BY dm.created_at ASC
         LIMIT 1
        """,
        user_ulid,
    )
    return row["cdp_code"] if row else None


async def _load_user_with_tenant(conn: asyncpg.Connection, user_ulid: str) -> dict[str, Any] | None:
    row = await conn.fetchrow("SELECT * FROM app_user WHERE user_ulid = $1", user_ulid)
    if row is None:
        return None
    data = dict(row)
    data["tenant_id"] = (
        await _primary_tenant_cdp(conn, user_ulid) if data["role"] == "dealer" else None
    )
    return data


async def _issue_session(conn: asyncpg.Connection, user_ulid: str) -> tuple[str, int]:
    """Mint a new opaque session token, persist only its hash, return (raw_token, ttl_seconds)."""
    raw = new_raw_token()
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=ACCESS_TOKEN_TTL_SECONDS)
    await conn.execute(
        """
        INSERT INTO user_session (session_ulid, user_ulid, token_hash, created_at, expires_at, last_seen_at)
        VALUES ($1, $2, $3, $4, $5, $4)
        """,
        ulid(), user_ulid, hash_token(raw), now, expires_at,
    )
    return raw, ACCESS_TOKEN_TTL_SECONDS


class CurrentSession:
    """Resolved (session_ulid, user_ulid) for a valid, non-revoked, non-expired bearer token."""

    __slots__ = ("session_ulid", "user_ulid")

    def __init__(self, session_ulid: str, user_ulid: str) -> None:
        self.session_ulid = session_ulid
        self.user_ulid = user_ulid


async def get_current_session(
    request: Request,
    authorization: str | None = Header(default=None),
) -> CurrentSession:
    """FastAPI dependency: resolve the bearer token to a live session, or 401.

    Never distinguishes "malformed header" from "unknown token" from "expired/revoked
    session" in the response — all collapse to the same 401, so a caller cannot probe
    which sessions once existed.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing or invalid Authorization header")
    raw = authorization.split(" ", 1)[1].strip()
    if not raw:
        raise HTTPException(status_code=401, detail="missing or invalid Authorization header")

    token_hash = hash_token(raw)
    async with request.app.state.pool.acquire() as c:
        row = await c.fetchrow(
            """
            SELECT session_ulid, user_ulid
              FROM user_session
             WHERE token_hash = $1 AND revoked_at IS NULL AND expires_at > now()
            """,
            token_hash,
        )
        if row is not None:
            # Best-effort liveness marker; failure to update must never block auth.
            await c.execute(
                "UPDATE user_session SET last_seen_at = now() WHERE session_ulid = $1",
                row["session_ulid"],
            )
    if row is None:
        raise HTTPException(status_code=401, detail="invalid or expired session")
    return CurrentSession(session_ulid=row["session_ulid"], user_ulid=row["user_ulid"])


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/register")
@limiter.limit(RATE_AUTH)
async def register(payload: RegisterRequest, request: Request) -> JSONResponse:
    """Create a 'particular' account and log it in immediately (register-then-auto-login,
    matching web/src/pages/Register.tsx's single-step flow). Dealer role is NOT assignable
    at registration — it is earned via POST /auth/claim-dealer against a real census entity
    (anti dealer-disfrazado, see module docstring)."""
    policy_error = validate_password_policy(payload.password)
    if policy_error:
        raise HTTPException(status_code=400, detail=policy_error)

    async with request.app.state.pool.acquire() as c:
        existing = await c.fetchval(
            "SELECT 1 FROM app_user WHERE email_lower = lower($1)", payload.email
        )
        if existing:
            raise HTTPException(status_code=409, detail="email already registered")

        new_user_ulid = ulid()
        await c.execute(
            """
            INSERT INTO app_user (user_ulid, email, password_hash, name, role)
            VALUES ($1, $2, $3, $4, 'particular')
            """,
            new_user_ulid, payload.email, hash_password(payload.password), payload.name or None,
        )
        raw_token, expires_in = await _issue_session(c, new_user_ulid)
        user = await _load_user_with_tenant(c, new_user_ulid)

    assert user is not None  # just inserted above, on the same acquired connection
    return JSONResponse({"token": raw_token, "expires_in": expires_in, "user": _serialize_user(user)})


@router.post("/login")
@limiter.limit(RATE_AUTH)
async def login(payload: LoginRequest, request: Request) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        row = await c.fetchrow(
            "SELECT * FROM app_user WHERE email_lower = lower($1)", payload.email
        )
        stored_hash = row["password_hash"] if row is not None else None
        password_ok = verify_password(payload.password, stored_hash)

        if row is None or not password_ok:
            # Same 401 for "no such account" and "wrong password" — no enumeration.
            raise HTTPException(status_code=401, detail="invalid email or password")
        if row["status"] != "active":
            raise HTTPException(status_code=403, detail="account is disabled")

        raw_token, expires_in = await _issue_session(c, row["user_ulid"])
        user = await _load_user_with_tenant(c, row["user_ulid"])

    assert user is not None
    return JSONResponse({"token": raw_token, "expires_in": expires_in, "user": _serialize_user(user)})


@router.get("/me")
@limiter.limit(RATE_DEFAULT)
async def me(request: Request, session: CurrentSession = Depends(get_current_session)) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        user = await _load_user_with_tenant(c, session.user_ulid)
    if user is None:
        # The session row is valid but the user vanished (should be impossible: ON DELETE
        # CASCADE removes sessions with the user) — fail closed rather than 500.
        raise HTTPException(status_code=401, detail="invalid or expired session")
    return JSONResponse({"user": _serialize_user(user)})


@router.post("/logout", status_code=204)
@limiter.limit(RATE_DEFAULT)
async def logout(request: Request, session: CurrentSession = Depends(get_current_session)) -> Response:
    async with request.app.state.pool.acquire() as c:
        await c.execute(
            "UPDATE user_session SET revoked_at = now() WHERE session_ulid = $1 AND revoked_at IS NULL",
            session.session_ulid,
        )
    return Response(status_code=204)


@router.post("/refresh")
@limiter.limit(RATE_AUTH)
async def refresh(request: Request, session: CurrentSession = Depends(get_current_session)) -> JSONResponse:
    """Rotate the session: revoke the presented token, mint a fresh one. Bounds the replay
    window of a leaked token to at most one refresh cycle instead of the full 24h TTL."""
    async with request.app.state.pool.acquire() as c:
        async with c.transaction():
            await c.execute(
                "UPDATE user_session SET revoked_at = now() WHERE session_ulid = $1",
                session.session_ulid,
            )
            raw_token, expires_in = await _issue_session(c, session.user_ulid)
    return JSONResponse({"token": raw_token, "expires_in": expires_in})


@router.post("/claim-dealer")
@limiter.limit(RATE_AUTH)
async def claim_dealer(
    payload: ClaimDealerRequest,
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    """Elevate the caller to role='dealer' by proving they know the REAL registered tax ID
    of the entity behind *cdp_code* — the anti dealer-disfrazado control (08 §4.7). Consumed
    by future cartas' UI (03-F1+); this endpoint is the verified primitive they wire a form to.
    """
    normalized_claim = canonical_tax_id(payload.tax_id)
    if normalized_claim is None:
        raise HTTPException(status_code=400, detail="tax_id fails its official checksum")

    async with request.app.state.pool.acquire() as c:
        actor = await c.fetchrow("SELECT role FROM app_user WHERE user_ulid = $1", session.user_ulid)
        if actor is None:
            raise HTTPException(status_code=401, detail="invalid or expired session")
        if actor["role"] == "staff":
            raise HTTPException(status_code=403, detail="staff accounts cannot claim dealer profiles")

        cluster = await resolve_cluster(c, payload.cdp_code)
        if cluster is None:
            raise HTTPException(status_code=404, detail=f"entity {payload.cdp_code} not found")

        entity_row = await c.fetchrow(
            "SELECT cif FROM entity WHERE entity_ulid = $1", cluster.canonical_ulid
        )
        normalized_registered = canonical_tax_id(entity_row["cif"]) if entity_row else None
        if normalized_registered is None:
            raise HTTPException(
                status_code=409,
                detail="this entity has no verifiable tax id on record; claim cannot be checked",
            )
        if normalized_registered != normalized_claim:
            raise HTTPException(
                status_code=403,
                detail="tax_id does not match this entity's registered records",
            )

        async with c.transaction():
            await c.execute(
                """
                INSERT INTO dealer_membership (user_ulid, entity_ulid, role_in_entity)
                VALUES ($1, $2, 'owner')
                ON CONFLICT (user_ulid, entity_ulid) DO NOTHING
                """,
                session.user_ulid, cluster.canonical_ulid,
            )
            await c.execute(
                "UPDATE app_user SET role = 'dealer', updated_at = now() "
                "WHERE user_ulid = $1 AND role = 'particular'",
                session.user_ulid,
            )
        user = await _load_user_with_tenant(c, session.user_ulid)

    assert user is not None
    return JSONResponse({"user": _serialize_user(user)})
