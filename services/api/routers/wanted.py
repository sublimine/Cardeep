"""/wanted/* — 08-forum-community F2: the "Se busca" board.

PRIORITY 1 of the pilar (carta §3): a structured buy-request matched in near-real-time
against the WHOLE cross-platform census (`vehicle`), not a single portal's own inventory
(AutoTrader) or a closed dealer pool (CarWow) — the one moat the carta's 17-reference
research identified (§2.6.1).

Auth: consumes AUTH-0 (``services/api/routers/auth.py``'s ``get_current_session`` /
``CurrentSession``) — no second user/session schema (00-MASTER.md "Reglas operativas" #4).
Envelope: the standard ``{ok, data, error, meta}`` (entities/geo/vehicles/dealer_ops
precedent) — unlike auth.py/crm_*.py this is a NET-NEW frontend surface with no
pre-existing wire contract to preserve.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from pipeline.ids import ulid
from pipeline.wanted.matcher import (
    CLOSED_REASONS,
    REVIEW_REVEAL_DAYS,
    TTL_CHOICES,
    WANTED_COOLDOWN_DAYS,
    WANTED_MAX_MONTH,
    WANTED_MAX_OPEN,
    reveal_eligible,
)
from pipeline.wanted.run_matcher import match_one_listing
from services.api.deps import err, ok, page_slice, resolve_cluster
from services.api.ratelimit import RATE_DEFAULT, RATE_EXPENSIVE, limiter
from services.api.routers.auth import CurrentSession, get_current_session

router = APIRouter(prefix="/wanted", tags=["wanted"])

FREE_TEXT_MAX_LENGTH = 500
COMMENT_MAX_LENGTH = 500
MATCHES_PAGE_SIZE_DEFAULT = 50


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class WantedCreateRequest(BaseModel):
    make: str = Field(..., min_length=1, max_length=64)
    model: str | None = Field(default=None, max_length=64)
    year_min: int | None = Field(default=None, ge=1900, le=2100)
    year_max: int | None = Field(default=None, ge=1900, le=2100)
    km_max: int | None = Field(default=None, ge=0)
    price_max: float | None = Field(default=None, ge=0)
    fuel: str | None = Field(default=None, max_length=32)
    transmission: str | None = Field(default=None, max_length=32)
    province_code: str = Field(..., min_length=1, max_length=8)
    free_text: str | None = Field(default=None, max_length=FREE_TEXT_MAX_LENGTH)
    ttl_days: int = Field(...)

    @field_validator("ttl_days")
    @classmethod
    def _valid_ttl(cls, v: int) -> int:
        if v not in TTL_CHOICES:
            raise ValueError(f"ttl_days must be one of {TTL_CHOICES}")
        return v


class WantedCloseRequest(BaseModel):
    reason: str = Field(...)

    @field_validator("reason")
    @classmethod
    def _valid_reason(cls, v: str) -> str:
        if v not in CLOSED_REASONS:
            raise ValueError(f"reason must be one of {CLOSED_REASONS}")
        return v


class ReviewCreateRequest(BaseModel):
    axis_trato: int = Field(..., ge=1, le=5)
    axis_anuncio_veraz: int = Field(..., ge=1, le=5)
    axis_disponibilidad_real: int = Field(..., ge=1, le=5)
    axis_agilidad: int = Field(..., ge=1, le=5)
    overall: int = Field(..., ge=1, le=5)
    comment: str | None = Field(default=None, max_length=COMMENT_MAX_LENGTH)
    reviewer_role: str = Field(default="buyer")

    @field_validator("reviewer_role")
    @classmethod
    def _valid_role(cls, v: str) -> str:
        if v not in ("buyer", "dealer"):
            raise ValueError("reviewer_role must be 'buyer' or 'dealer'")
        return v


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _serialize_listing(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "wanted_ulid": row["wanted_ulid"],
        "make": row["make"],
        "model": row["model"],
        "year_min": row["year_min"],
        "year_max": row["year_max"],
        "km_max": row["km_max"],
        "price_max": float(row["price_max"]) if row["price_max"] is not None else None,
        "fuel": row["fuel"],
        "transmission": row["transmission"],
        "province_code": row["province_code"],
        "free_text": row["free_text"],
        "ttl_days": row["ttl_days"],
        "status": row["status"],
        "closed_reason": row["closed_reason"],
        "created_at": str(row["created_at"]),
        "expires_at": str(row["expires_at"]),
    }


def _serialize_match(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "wanted_match_ulid": row["wanted_match_ulid"],
        "vehicle_ulid": row["vehicle_ulid"],
        "match_score": float(row["match_score"]),
        "matched_at": str(row["matched_at"]),
        "notified_at": str(row["notified_at"]) if row["notified_at"] else None,
        "clicked_at": str(row["clicked_at"]) if row["clicked_at"] else None,
        "make": row.get("make"),
        "model": row.get("model"),
        "year": row.get("year"),
        "km": row.get("km"),
        "price": float(row["price"]) if row.get("price") is not None else None,
        "photo_url": row.get("photo_url"),
        "deep_link": row.get("deep_link"),
        "entity_ulid": row.get("entity_ulid"),
        "vehicle_status": row.get("status"),
    }


# ---------------------------------------------------------------------------
# Public aggregates — MUST be declared before /{wanted_ulid} (route-ordering
# discipline, geo.py precedent: static paths first).
# ---------------------------------------------------------------------------

@router.get("/pulse")
@limiter.limit(RATE_DEFAULT)
async def pulse(request: Request) -> JSONResponse:
    """Carta §4.9 — the hero's "pulso vivo": exactly three numbers, each traced to a
    real COUNT. ``threads_active_24h`` is honestly 0 until the forum (F4/F5) exists —
    never fabricated, never omitted."""
    async with request.app.state.pool.acquire() as c:
        open_wanted = await c.fetchval("SELECT COUNT(*) FROM wanted_listing WHERE status = 'open'")
        matches_7d = await c.fetchval(
            "SELECT COUNT(*) FROM wanted_match WHERE notified_at > now() - interval '7 days'"
        )
        threads_active_24h = 0
        forum_exists = await c.fetchval(
            "SELECT 1 FROM information_schema.tables WHERE table_name = 'forum_thread'"
        )
        if forum_exists:
            threads_active_24h = await c.fetchval(
                "SELECT COUNT(DISTINCT thread_ulid) FROM forum_thread "
                "WHERE last_reply_at > now() - interval '24 hours'"
            )
    return ok({
        "threads_active_24h": threads_active_24h,
        "wanted_open": open_wanted,
        "matches_served_7d": matches_7d,
    })


@router.get("/meta/provinces")
@limiter.limit(RATE_DEFAULT)
async def meta_provinces(request: Request) -> JSONResponse:
    """Static reference data for the publish form's province selector (carta §6.1). A tiny,
    self-contained read — not a duplicate of geo.py's own (differently-shaped) endpoints,
    which this router does not own and does not touch."""
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            "SELECT code, name FROM geo_province WHERE country_code = 'ES' ORDER BY name"
        )
    return ok([{"code": r["code"], "name": r["name"]} for r in rows], count=len(rows))


@router.get("/liveness")
@limiter.limit(RATE_DEFAULT)
async def liveness(request: Request) -> JSONResponse:
    """Carta §4.10 — match_liveness_rate: matches with vehicle.status='available' at
    click time / total clicks, 30d window. Published honestly even when it is bad
    (the carta's own words: "es el termómetro honesto de la latencia scraping->clic")."""
    async with request.app.state.pool.acquire() as c:
        row = await c.fetchrow(
            """
            SELECT
                COUNT(*) FILTER (WHERE v.status = 'available') AS live_at_click,
                COUNT(*) AS total_clicks
              FROM wanted_match wm
              JOIN vehicle v ON v.vehicle_ulid = wm.vehicle_ulid
              JOIN entity e ON e.entity_ulid = v.entity_ulid
             WHERE wm.clicked_at > now() - interval '30 days' AND e.country_code = 'ES'
            """
        )
    total = row["total_clicks"] or 0
    rate = (row["live_at_click"] / total) if total > 0 else None
    return ok({
        "match_liveness_rate": rate,
        "live_at_click": row["live_at_click"],
        "total_clicks": total,
        "window_days": 30,
    })


@router.get("/demand")
@limiter.limit(RATE_DEFAULT)
async def demand(request: Request) -> JSONResponse:
    """Carta §6.1 — "la cara pública del tablón": aggregate demand by province+make,
    last 30 days of OPEN requests. Cero maquillaje: a segment with 0 buyers is absent,
    never zero-padded to look populated."""
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            """
            SELECT wl.province_code, gp.name AS province_name, wl.make, wl.fuel,
                   COUNT(*) AS buyers
              FROM wanted_listing wl
              JOIN geo_province gp ON gp.country_code = 'ES' AND gp.code = wl.province_code
             WHERE wl.status = 'open' AND wl.created_at > now() - interval '30 days'
             GROUP BY wl.province_code, gp.name, wl.make, wl.fuel
             ORDER BY buyers DESC
             LIMIT 50
            """
        )
    return ok([dict(r) for r in rows], count=len(rows))


@router.get("/reviews/{cdp_code}")
@limiter.limit(RATE_DEFAULT)
async def dealer_reviews(cdp_code: str, request: Request) -> JSONResponse:
    """Public, revealed-only dealer valoración aggregate (carta §4.6/§6.3). Never
    serves a row with revealed_at IS NULL (§7.7 invariant, contract-tested)."""
    async with request.app.state.pool.acquire() as c:
        cluster = await resolve_cluster(c, cdp_code)
        if cluster is None:
            return err(f"entity {cdp_code} not found", status=404)
        row = await c.fetchrow(
            """
            SELECT
                COUNT(*) AS n,
                COUNT(*) FILTER (WHERE overall >= 4) AS n_positive,
                AVG(axis_trato) AS avg_trato,
                AVG(axis_anuncio_veraz) AS avg_anuncio_veraz,
                AVG(axis_disponibilidad_real) AS avg_disponibilidad_real,
                AVG(axis_agilidad) AS avg_agilidad
              FROM dealer_review
             WHERE entity_ulid = ANY($1::text[])
               AND revealed_at IS NOT NULL
               AND submitted_at > now() - interval '12 months'
               AND reviewer_role = 'buyer'
            """,
            cluster.member_ulids,
        )
    n = row["n"] or 0
    pct_positive = (row["n_positive"] / n) if n > 0 else None
    return ok({
        "cdp_code": cluster.canonical_cdp_code,
        "n_reviews_12m": n,
        "pct_positive_12m": pct_positive,
        "axis_averages": {
            "trato": float(row["avg_trato"]) if row["avg_trato"] is not None else None,
            "anuncio_veraz": float(row["avg_anuncio_veraz"]) if row["avg_anuncio_veraz"] is not None else None,
            "disponibilidad_real": float(row["avg_disponibilidad_real"]) if row["avg_disponibilidad_real"] is not None else None,
            "agilidad": float(row["avg_agilidad"]) if row["avg_agilidad"] is not None else None,
        },
    })


# ---------------------------------------------------------------------------
# Authenticated CRUD
# ---------------------------------------------------------------------------

@router.post("")
@limiter.limit(RATE_DEFAULT)
async def create_wanted(
    payload: WantedCreateRequest,
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        user = await c.fetchrow("SELECT created_at FROM app_user WHERE user_ulid = $1", session.user_ulid)
        if user is None:
            raise HTTPException(status_code=401, detail="invalid or expired session")

        account_age_days = (datetime.now(timezone.utc) - user["created_at"]).days
        if account_age_days < WANTED_COOLDOWN_DAYS:
            # Declared gap (pipeline/wanted/matcher.py module docstring / carta §4.4): the
            # carta also gates on "email verificado", which AUTH-0 (migrations/0073_auth.sql)
            # has no column or flow for yet — only the account-age half of the gate is
            # enforceable today. Not silently skipped: this comment + the carta's F2 closure
            # note both name the gap.
            raise HTTPException(
                status_code=403,
                detail=f"account must be at least {WANTED_COOLDOWN_DAYS} day(s) old to publish a request",
            )

        province_exists = await c.fetchval(
            "SELECT 1 FROM geo_province WHERE country_code = 'ES' AND code = $1", payload.province_code
        )
        if not province_exists:
            raise HTTPException(status_code=422, detail=f"unknown province_code '{payload.province_code}'")

        open_count = await c.fetchval(
            "SELECT COUNT(*) FROM wanted_listing WHERE user_ulid = $1 AND status = 'open'",
            session.user_ulid,
        )
        if open_count >= WANTED_MAX_OPEN:
            raise HTTPException(
                status_code=429,
                detail=f"you already have {open_count} open requests (max {WANTED_MAX_OPEN}); "
                       "close one before publishing a new one",
            )
        month_count = await c.fetchval(
            "SELECT COUNT(*) FROM wanted_listing WHERE user_ulid = $1 AND created_at > now() - interval '30 days'",
            session.user_ulid,
        )
        if month_count >= WANTED_MAX_MONTH:
            raise HTTPException(
                status_code=429,
                detail=f"you have created {month_count} requests in the last 30 days (max {WANTED_MAX_MONTH})",
            )

        now = datetime.now(timezone.utc)
        new_ulid = ulid()
        await c.execute(
            """
            INSERT INTO wanted_listing
                (wanted_ulid, user_ulid, make, model, year_min, year_max, km_max, price_max,
                 fuel, transmission, province_code, free_text, ttl_days, expires_at)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14)
            """,
            new_ulid, session.user_ulid, payload.make, payload.model, payload.year_min, payload.year_max,
            payload.km_max, payload.price_max, payload.fuel, payload.transmission, payload.province_code,
            payload.free_text, payload.ttl_days, now + timedelta(days=payload.ttl_days),
        )
        listing = dict(await c.fetchrow("SELECT * FROM wanted_listing WHERE wanted_ulid = $1", new_ulid))
        matches, exact_count = await match_one_listing(c, listing)

    return ok(
        _serialize_listing(listing),
        matches_now=exact_count,
        top_matches=[_serialize_match(m) for m in matches[:10]],
    )


@router.get("")
@limiter.limit(RATE_DEFAULT)
async def list_my_wanted(
    request: Request,
    status_filter: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    offset = (page - 1) * size
    async with request.app.state.pool.acquire() as c:
        if status_filter:
            rows = await c.fetch(
                "SELECT * FROM wanted_listing WHERE user_ulid = $1 AND status = $2 "
                "ORDER BY created_at DESC LIMIT $3 OFFSET $4",
                session.user_ulid, status_filter, size + 1, offset,
            )
        else:
            rows = await c.fetch(
                "SELECT * FROM wanted_listing WHERE user_ulid = $1 "
                "ORDER BY created_at DESC LIMIT $2 OFFSET $3",
                session.user_ulid, size + 1, offset,
            )
    rows, has_more = page_slice(rows, size)
    items = [_serialize_listing(dict(r)) for r in rows]
    return ok(items, page=page, size=size, returned=len(items), has_more=has_more)


async def _authorize_listing(conn: asyncpg.Connection, user_ulid: str, wanted_ulid: str) -> dict[str, Any]:
    row = await conn.fetchrow("SELECT * FROM wanted_listing WHERE wanted_ulid = $1", wanted_ulid)
    if row is None:
        raise HTTPException(status_code=404, detail=f"wanted listing {wanted_ulid} not found")
    if row["user_ulid"] != user_ulid:
        raise HTTPException(status_code=403, detail="you do not own this request")
    return dict(row)


@router.get("/{wanted_ulid}")
@limiter.limit(RATE_DEFAULT)
async def get_wanted(
    wanted_ulid: str,
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        listing = await _authorize_listing(c, session.user_ulid, wanted_ulid)
    return ok(_serialize_listing(listing))


@router.get("/{wanted_ulid}/matches")
@limiter.limit(RATE_EXPENSIVE)
async def get_matches(
    wanted_ulid: str,
    request: Request,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=MATCHES_PAGE_SIZE_DEFAULT, ge=1, le=200),
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    """Carta §7.3: "cada match mostrado re-verifica vehicle.status='available' en
    render" — a sold car never appears as a live coincidencia, even if the persisted
    wanted_match row is stale."""
    offset = (page - 1) * size
    async with request.app.state.pool.acquire() as c:
        listing = await _authorize_listing(c, session.user_ulid, wanted_ulid)
        rows = await c.fetch(
            """
            SELECT wm.wanted_match_ulid, wm.vehicle_ulid, wm.match_score, wm.matched_at,
                   wm.notified_at, wm.clicked_at,
                   v.make, v.model, v.year, v.km, v.price, v.photo_url, v.deep_link,
                   v.entity_ulid, v.status
              FROM wanted_match wm
              JOIN vehicle v ON v.vehicle_ulid = wm.vehicle_ulid
              JOIN entity e ON e.entity_ulid = v.entity_ulid
             WHERE wm.wanted_ulid = $1 AND v.status = 'available' AND e.country_code = 'ES'
             ORDER BY wm.match_score DESC, wm.wanted_match_ulid
             LIMIT $2 OFFSET $3
            """,
            wanted_ulid, size + 1, offset,
        )
    rows, has_more = page_slice(rows, size)
    items = [_serialize_match(dict(r)) for r in rows]
    _ = listing
    return ok(items, page=page, size=size, returned=len(items), has_more=has_more)


@router.post("/{wanted_ulid}/close")
@limiter.limit(RATE_DEFAULT)
async def close_wanted(
    wanted_ulid: str,
    payload: WantedCloseRequest,
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        listing = await _authorize_listing(c, session.user_ulid, wanted_ulid)
        if listing["status"] not in ("open", "matched"):
            raise HTTPException(status_code=409, detail=f"request is already {listing['status']}")
        await c.execute(
            "UPDATE wanted_listing SET status = 'closed', closed_reason = $1, updated_at = now() "
            "WHERE wanted_ulid = $2",
            payload.reason, wanted_ulid,
        )
        updated = dict(await c.fetchrow("SELECT * FROM wanted_listing WHERE wanted_ulid = $1", wanted_ulid))
    return ok(_serialize_listing(updated))


@router.post("/matches/{wanted_match_ulid}/click")
@limiter.limit(RATE_DEFAULT)
async def click_match(
    wanted_match_ulid: str,
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    """Idempotent: the FIRST click stamps clicked_at; later clicks are a no-op so the
    gate for dealer_review (§4.6) and the match_liveness_rate KPI (§4.10) both read a
    stable timestamp, not a moving one."""
    async with request.app.state.pool.acquire() as c:
        row = await c.fetchrow(
            "SELECT wm.*, wl.user_ulid FROM wanted_match wm "
            "JOIN wanted_listing wl ON wl.wanted_ulid = wm.wanted_ulid "
            "WHERE wm.wanted_match_ulid = $1",
            wanted_match_ulid,
        )
        if row is None:
            raise HTTPException(status_code=404, detail="match not found")
        if row["user_ulid"] != session.user_ulid:
            raise HTTPException(status_code=403, detail="you do not own this request")
        if row["clicked_at"] is None:
            await c.execute(
                "UPDATE wanted_match SET clicked_at = now() WHERE wanted_match_ulid = $1",
                wanted_match_ulid,
            )
    return ok({"wanted_match_ulid": wanted_match_ulid, "clicked": True})


@router.post("/matches/{wanted_match_ulid}/review")
@limiter.limit(RATE_DEFAULT)
async def submit_review(
    wanted_match_ulid: str,
    payload: ReviewCreateRequest,
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    """Carta §4.6 — gate transaccional (eBay) + double-blind (Airbnb, exact 14-day window).

    A review literally cannot exist without an enabling wanted_match (FK NOT NULL,
    migrations/0093_wanted.sql) — this endpoint additionally enforces the BEHAVIOURAL
    half of the gate: the match must be closed as 'bought_via_cardeep' OR have a
    recorded clicked_at.
    """
    async with request.app.state.pool.acquire() as c:
        match = await c.fetchrow(
            "SELECT wm.*, wl.user_ulid AS buyer_user_ulid, wl.closed_reason, v.entity_ulid "
            "FROM wanted_match wm "
            "JOIN wanted_listing wl ON wl.wanted_ulid = wm.wanted_ulid "
            "JOIN vehicle v ON v.vehicle_ulid = wm.vehicle_ulid "
            "JOIN entity e ON e.entity_ulid = v.entity_ulid "
            "WHERE wm.wanted_match_ulid = $1 AND e.country_code = 'ES'",
            wanted_match_ulid,
        )
        if match is None:
            raise HTTPException(status_code=404, detail="match not found")

        gate_ok = match["closed_reason"] == "bought_via_cardeep" or match["clicked_at"] is not None
        if not gate_ok:
            raise HTTPException(
                status_code=403,
                detail="no proven interaction (click-through or closed-as-bought) with this match yet",
            )

        entity_row = await c.fetchrow("SELECT cdp_code FROM entity WHERE entity_ulid = $1", match["entity_ulid"])
        cluster = await resolve_cluster(c, entity_row["cdp_code"]) if entity_row else None

        if payload.reviewer_role == "buyer":
            if session.user_ulid != match["buyer_user_ulid"]:
                raise HTTPException(status_code=403, detail="only the requesting buyer can leave this review")
            reviewed_entity_ulid = cluster.canonical_ulid if cluster else match["entity_ulid"]
        else:  # reviewer_role == "dealer"
            if cluster is None:
                raise HTTPException(status_code=404, detail="dealer entity not found")
            is_member = await c.fetchval(
                "SELECT 1 FROM dealer_membership WHERE user_ulid = $1 AND entity_ulid = $2",
                session.user_ulid, cluster.canonical_ulid,
            )
            if not is_member:
                raise HTTPException(status_code=403, detail="you do not manage this dealer")
            reviewed_entity_ulid = cluster.canonical_ulid

        existing = await c.fetchrow(
            "SELECT * FROM dealer_review WHERE wanted_match_ulid = $1 AND reviewer_role = $2",
            wanted_match_ulid, payload.reviewer_role,
        )
        if existing is not None:
            raise HTTPException(status_code=409, detail="you already reviewed this match")

        now = datetime.now(timezone.utc)
        new_ulid = ulid()
        await c.execute(
            """
            INSERT INTO dealer_review
                (review_ulid, wanted_match_ulid, reviewer_user_ulid, entity_ulid, reviewer_role,
                 axis_trato, axis_anuncio_veraz, axis_disponibilidad_real, axis_agilidad,
                 overall, comment, submitted_at)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
            """,
            new_ulid, wanted_match_ulid, session.user_ulid, reviewed_entity_ulid, payload.reviewer_role,
            payload.axis_trato, payload.axis_anuncio_veraz, payload.axis_disponibilidad_real,
            payload.axis_agilidad, payload.overall, payload.comment, now,
        )

        # Double-blind reveal check: if the counterpart side already exists, evaluate both.
        other_role = "dealer" if payload.reviewer_role == "buyer" else "buyer"
        counterpart = await c.fetchrow(
            "SELECT submitted_at FROM dealer_review WHERE wanted_match_ulid = $1 AND reviewer_role = $2",
            wanted_match_ulid, other_role,
        )
        this_submitted_at = now
        counterpart_submitted_at = counterpart["submitted_at"] if counterpart else None
        if reveal_eligible(this_submitted_at, counterpart_submitted_at, now, REVIEW_REVEAL_DAYS):
            await c.execute(
                "UPDATE dealer_review SET revealed_at = $1 WHERE wanted_match_ulid = $2", now, wanted_match_ulid
            )
            if counterpart is not None:
                await c.execute(
                    "UPDATE dealer_review SET revealed_at = $1 WHERE wanted_match_ulid = $2 AND revealed_at IS NULL",
                    now, wanted_match_ulid,
                )

        review = dict(await c.fetchrow("SELECT * FROM dealer_review WHERE review_ulid = $1", new_ulid))

    return ok({
        "review_ulid": review["review_ulid"],
        "reviewer_role": review["reviewer_role"],
        "revealed": review["revealed_at"] is not None,
        "submitted_at": str(review["submitted_at"]),
    })
