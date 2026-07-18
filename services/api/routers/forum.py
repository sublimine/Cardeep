"""/forum/* — 08-forum-community F4: the conversation layer (PRIORITY 2, carta §3).

Built on the "Se busca" board's infra: AUTH-0 sessions, geo_province, and — critically —
the wanted board's own reputation source ("+15 petición cerrada como comprado vía match")
is how a user crosses the votar >= rep 10 threshold BEFORE a single forum vote exists —
the carta's own "tablón antes que foro" build order (§9) is this cold-start bootstrap,
not a coincidence (see plans/cardeep-omni/08-forum-community.md §10).

Anchors (post_anchor) are polymorphic and verified against the LIVE census at render time
(carta §4.2): a vehicle/entity anchor whose target has vanished degrades to an unverified
state rather than silently keeping a stale badge.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from pipeline.forum.ranking import ANCHOR_CAP, rank_score
from pipeline.forum.reputation import (
    DOWNVOTE_PRIVILEGE_MIN_REP,
    FLAG_PRIVILEGE_MIN_REP,
    PEER_INFLATION_WINDOW_DAYS,
    REP_DAILY_CAP,
    VOTE_PRIVILEGE_MIN_REP,
    can_downvote,
    can_flag,
    can_vote,
    upvote_delta,
)
from pipeline.ids import ulid
from services.api.deps import err, ok, page_slice, resolve_cluster
from services.api.ratelimit import RATE_DEFAULT, RATE_EXPENSIVE, limiter
from services.api.routers.auth import CurrentSession, get_current_session

router = APIRouter(prefix="/forum", tags=["forum"])

TITLE_MAX_LENGTH = 200
BODY_MAX_LENGTH = 5000
THREAD_TYPES: tuple[str, ...] = ("discussion", "price_check")
ANCHOR_TYPES: tuple[str, ...] = ("vehicle", "entity", "province")
THREADS_PAGE_SIZE_DEFAULT = 30


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class AnchorRequest(BaseModel):
    anchor_type: str
    anchor_ref: str = Field(..., min_length=1, max_length=64)

    @field_validator("anchor_type")
    @classmethod
    def _valid_type(cls, v: str) -> str:
        if v not in ANCHOR_TYPES:
            raise ValueError(f"anchor_type must be one of {ANCHOR_TYPES}")
        return v


class ThreadCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=TITLE_MAX_LENGTH)
    body: str = Field(..., min_length=1, max_length=BODY_MAX_LENGTH)
    thread_type: str = Field(default="discussion")
    province_code: str | None = Field(default=None, max_length=8)
    anchors: list[AnchorRequest] = Field(default_factory=list)

    @field_validator("thread_type")
    @classmethod
    def _valid_thread_type(cls, v: str) -> str:
        if v not in THREAD_TYPES:
            raise ValueError(f"thread_type must be one of {THREAD_TYPES}")
        return v


class PostCreateRequest(BaseModel):
    body: str = Field(..., min_length=1, max_length=BODY_MAX_LENGTH)
    anchors: list[AnchorRequest] = Field(default_factory=list)


class VoteRequest(BaseModel):
    value: int = Field(...)

    @field_validator("value")
    @classmethod
    def _valid_value(cls, v: int) -> int:
        if v not in (-1, 0, 1):
            raise ValueError("value must be -1 (downvote), 0 (remove vote) or 1 (upvote)")
        return v


class FlagRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=200)


class ModerationResolveRequest(BaseModel):
    resolution: Literal["removed", "dismissed"]


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

async def _current_rep(conn: asyncpg.Connection, user_ulid: str) -> int:
    """Carta §4.5 invariant: 'el número mostrado en perfil DEBE coincidir con la suma del
    ledger' — this IS that sum, the single source of truth, never a cached counter."""
    total = await conn.fetchval(
        "SELECT COALESCE(SUM(delta), 0) FROM reputation_event WHERE user_ulid = $1", user_ulid
    )
    return int(total)


async def _reconstruct_price_from_events(conn: asyncpg.Connection, vehicle_ulid: str) -> float | None:
    """Carta §7.1 vía B: 'último PRICE_CHANGE.new_value, o NEW si no hay cambios' — the
    SAME append-only ledger every other verification protocol in this codebase treats as
    the second, independent path (0003_vehicles_events.sql's own doctrine)."""
    row = await conn.fetchrow(
        "SELECT new_value FROM vehicle_event WHERE vehicle_ulid = $1 AND event_type = 'PRICE_CHANGE' "
        "ORDER BY observed_at DESC LIMIT 1",
        vehicle_ulid,
    )
    if row is not None and isinstance(row["new_value"], dict) and row["new_value"].get("price") is not None:
        return float(row["new_value"]["price"])
    row2 = await conn.fetchrow(
        "SELECT new_value FROM vehicle_event WHERE vehicle_ulid = $1 AND event_type = 'NEW' "
        "ORDER BY observed_at ASC LIMIT 1",
        vehicle_ulid,
    )
    if row2 is not None and isinstance(row2["new_value"], dict) and row2["new_value"].get("price") is not None:
        return float(row2["new_value"]["price"])
    return None


PRICE_MATCH_TOLERANCE = 0.01  # float rounding slack, not a real-world price difference


def _price_confirmed(live_price: float | None, reconstructed_price: float | None) -> bool:
    """Pure comparison — carta §4.2 condition (2) / §7.1 vía B. Extracted from
    ``_verify_anchor`` (which does the DB I/O) so the exact-match arithmetic is testable
    without a database (tests/test_forum_router.py's live-DB tests would otherwise be
    the only way to exercise this, and doing so would require writing a synthetic
    PRICE_CHANGE row into the REAL, DELETE-blocked vehicle_event ledger — migrations/
    0035_append_only_row_guards.sql makes that append-only violation impossible to
    clean up afterwards, so this logic is deliberately isolated instead)."""
    if live_price is None or reconstructed_price is None:
        return False
    return abs(reconstructed_price - live_price) <= PRICE_MATCH_TOLERANCE


async def _flag_anchor_drift(conn: asyncpg.Connection, anchor_ref: str, live_price: float | None, reconstructed_price: float | None) -> None:
    """Carta §7.6: every double-vía failure emits an `alert` row — reused verbatim
    (0004_verification_health.sql schema), never a second alerting table (carta §5.1)."""
    await conn.execute(
        "INSERT INTO alert (origin, severity, message, payload) VALUES ($1, $2, $3, $4)",
        "community.anchor_drift", "warning",
        f"vehicle {anchor_ref}: live price and vehicle_event reconstruction disagree",
        {"vehicle_ulid": anchor_ref, "live_price": live_price, "reconstructed_price": reconstructed_price},
    )


async def _verify_anchor(conn: asyncpg.Connection, anchor_type: str, anchor_ref: str) -> dict[str, Any] | None:
    """Return a JSONB-able snapshot if the anchor target exists NOW, else None (carta §4.2:
    'nunca badge por defecto' — an anchor to a vanished target is stored anyway, per the
    carta's drift-detection intent, but flagged unverified via a null snapshot).

    Carta §4.2's TWO conditions for the "DATO VERIFICADO" badge: (1) the target exists
    (this function returning non-None at all) AND (2) the live price matches the
    independent reconstruction from vehicle_event (§7.1 vía B). Condition 2 is encoded as
    ``price_confirmed`` in the snapshot — the router only sets ``verified=True`` when
    BOTH hold (see ``_insert_anchors``/``get_thread`` below).
    """
    if anchor_type == "vehicle":
        row = await conn.fetchrow(
            "SELECT make, model, year, price, status, photo_url, deep_link, last_seen "
            "FROM vehicle WHERE vehicle_ulid = $1",
            anchor_ref,
        )
        if row is None:
            return None
        live_price = float(row["price"]) if row["price"] is not None else None
        reconstructed = await _reconstruct_price_from_events(conn, anchor_ref)
        price_confirmed = _price_confirmed(live_price, reconstructed)
        if not price_confirmed and reconstructed is not None and live_price is not None:
            await _flag_anchor_drift(conn, anchor_ref, live_price, reconstructed)
        return {
            "make": row["make"], "model": row["model"], "year": row["year"],
            "price": live_price, "status": row["status"],
            "photo_url": row["photo_url"], "deep_link": row["deep_link"], "last_seen": str(row["last_seen"]),
            "price_confirmed": price_confirmed,
        }
    if anchor_type == "entity":
        cluster = await resolve_cluster(conn, anchor_ref)
        if cluster is None:
            return None
        row = await conn.fetchrow("SELECT trade_name FROM entity WHERE entity_ulid = $1", cluster.canonical_ulid)
        stock = await conn.fetchval(
            "SELECT COUNT(*) FROM vehicle WHERE entity_ulid = ANY($1::text[]) AND status = 'available'",
            cluster.member_ulids,
        )
        return {
            "cdp_code": cluster.canonical_cdp_code, "trade_name": row["trade_name"] if row else None,
            "stock_available": int(stock),
        }
    if anchor_type == "province":
        row = await conn.fetchrow(
            "SELECT name FROM geo_province WHERE country_code = 'ES' AND code = $1", anchor_ref
        )
        if row is None:
            return None
        return {"name": row["name"]}
    return None


def _is_badge_verified(anchor_type: str, snapshot: dict[str, Any]) -> bool:
    """Carta §4.2's FULL two-condition badge (existence AND, for vehicles, price
    cross-check) — stricter than §4.1's ranking-only 'exists' count (kept separate,
    see ``_verify_anchor``'s docstring). Entity/province anchors have no price to
    cross-check, so existence alone satisfies the badge for them."""
    if not snapshot:
        return False
    if anchor_type == "vehicle":
        return bool(snapshot.get("price_confirmed", False))
    return True


async def _insert_anchors(conn: asyncpg.Connection, post_ulid: str, anchors: list[AnchorRequest]) -> int:
    """Insert anchors, returning the count of VERIFIED ones (existence confirmed now)."""
    verified_count = 0
    for a in anchors:
        snapshot = await _verify_anchor(conn, a.anchor_type, a.anchor_ref)
        if snapshot is not None:
            verified_count += 1
        await conn.execute(
            "INSERT INTO post_anchor (anchor_ulid, post_ulid, anchor_type, anchor_ref, snapshot) "
            "VALUES ($1, $2, $3, $4, $5)",
            ulid(), post_ulid, a.anchor_type, a.anchor_ref, snapshot or {},
        )
    return verified_count


async def _rep_daily_credited(conn: asyncpg.Connection, user_ulid: str) -> int:
    row = await conn.fetchval(
        "SELECT COALESCE(SUM(delta), 0) FROM reputation_event "
        "WHERE user_ulid = $1 AND reason IN ('upvote_anchor','upvote_no_anchor','downvote_received','downvote_cast') "
        "AND created_at > now() - interval '1 day'",
        user_ulid,
    )
    return int(row)


async def _last_pair_credit(conn: asyncpg.Connection, author_ulid: str, voter_ulid: str) -> datetime | None:
    return await conn.fetchval(
        "SELECT created_at FROM reputation_event "
        "WHERE user_ulid = $1 AND related_user_ulid = $2 "
        "AND reason IN ('upvote_anchor','upvote_no_anchor','downvote_received') "
        "ORDER BY created_at DESC LIMIT 1",
        author_ulid, voter_ulid,
    )


async def _author_roles(conn: asyncpg.Connection, user_ulids: list[str]) -> dict[str, str]:
    """Carta §4.7 (PistonHeads-exact: reglas distintas para dealer vs particular):
    'las peticiones y posts muestran SIEMPRE el rol'. Batch fetch, never N+1."""
    if not user_ulids:
        return {}
    rows = await conn.fetch(
        "SELECT user_ulid, role FROM app_user WHERE user_ulid = ANY($1::text[])", list(set(user_ulids))
    )
    return {r["user_ulid"]: r["role"] for r in rows}


def _serialize_thread(row: dict[str, Any], rank: float | None = None, author_role: str | None = None) -> dict[str, Any]:
    d = {
        "thread_ulid": row["thread_ulid"],
        "title": row["title"],
        "author_user_ulid": row["author_user_ulid"],
        "author_role": author_role,  # carta §4.7: role is ALWAYS shown
        "province_code": row["province_code"],
        "thread_type": row["thread_type"],
        "created_at": str(row["created_at"]),
        "last_reply_at": str(row["last_reply_at"]),
        "reply_count": row["reply_count"],
        "net_votes": row.get("net_votes", 0),
        "verified_anchor_count": row.get("verified_anchor_count", 0),
    }
    if rank is not None:
        d["rank_score"] = rank
    return d


# ---------------------------------------------------------------------------
# Feed
# ---------------------------------------------------------------------------

@router.get("/threads")
@limiter.limit(RATE_EXPENSIVE)
async def list_threads(
    request: Request,
    sort: str = Query(default="hot", pattern="^(hot|recent)$"),
    province: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=THREADS_PAGE_SIZE_DEFAULT, ge=1, le=100),
) -> JSONResponse:
    """Carta §6.2: feed ordered by rank_score (§4.1) with a 'recientes' toggle. Province
    filter clicks through from the SpainMap heatmap (§4.8)."""
    offset = (page - 1) * size
    async with request.app.state.pool.acquire() as c:
        base_rows = await c.fetch(
            """
            SELECT t.*,
                   COALESCE(v.net_votes, 0) AS net_votes,
                   COALESCE(a.verified_anchor_count, 0) AS verified_anchor_count,
                   EXTRACT(EPOCH FROM (now() - t.created_at)) / 3600.0 AS hours_age
              FROM forum_thread t
              LEFT JOIN (
                  SELECT fp.thread_ulid, SUM(pv.value) AS net_votes
                    FROM forum_post fp JOIN post_vote pv ON pv.post_ulid = fp.post_ulid
                   GROUP BY fp.thread_ulid
              ) v ON v.thread_ulid = t.thread_ulid
              LEFT JOIN (
                  SELECT fp.thread_ulid, COUNT(*) FILTER (WHERE pa.snapshot <> '{}'::jsonb) AS verified_anchor_count
                    FROM forum_post fp JOIN post_anchor pa ON pa.post_ulid = fp.post_ulid
                   GROUP BY fp.thread_ulid
              ) a ON a.thread_ulid = t.thread_ulid
             WHERE ($1::varchar IS NULL OR t.province_code = $1::varchar)
            """,
            province,
        )
        items = [dict(r) for r in base_rows]
        roles = await _author_roles(c, [it["author_user_ulid"] for it in items])
    if sort == "hot":
        for it in items:
            it["_rank"] = rank_score(int(it["net_votes"]), int(it["verified_anchor_count"]), float(it["hours_age"]))
        items.sort(key=lambda x: x["_rank"], reverse=True)
    else:
        items.sort(key=lambda x: x["created_at"], reverse=True)
    page_items = items[offset:offset + size]
    has_more = len(items) > offset + size
    out = [_serialize_thread(it, it.get("_rank"), roles.get(it["author_user_ulid"])) for it in page_items]
    return ok(out, page=page, size=size, returned=len(out), has_more=has_more)


# ---------------------------------------------------------------------------
# Anchor search (DataLinker composer, carta §6.3)
# ---------------------------------------------------------------------------

@router.get("/anchor-search")
@limiter.limit(RATE_DEFAULT)
async def anchor_search(
    request: Request,
    q: str = Query(..., min_length=2, max_length=100),
    kind: str = Query(default="vehicle", pattern="^(vehicle|entity)$"),
) -> JSONResponse:
    """Composer 'vincular dato': selects a REAL entity from the live census, never a
    pasted URL (carta §6.3)."""
    async with request.app.state.pool.acquire() as c:
        if kind == "vehicle":
            rows = await c.fetch(
                """
                SELECT v.vehicle_ulid, v.make, v.model, v.year, v.price, v.deep_link
                  FROM vehicle v
                  JOIN entity e ON e.entity_ulid = v.entity_ulid
                 WHERE v.status = 'available' AND e.country_code = 'ES'
                   AND (v.make ILIKE $1 OR v.model ILIKE $1 OR v.title ILIKE $1)
                 LIMIT 20
                """,
                f"%{q}%",
            )
            items = [
                {
                    "anchor_type": "vehicle", "anchor_ref": r["vehicle_ulid"],
                    "label": f"{r['make']} {r['model']} ({r['year']})",
                    "price": float(r["price"]) if r["price"] is not None else None,
                    "deep_link": r["deep_link"],
                }
                for r in rows
            ]
        else:
            rows = await c.fetch(
                "SELECT cdp_code, trade_name FROM entity WHERE country_code = 'ES' AND (trade_name ILIKE $1 OR cdp_code ILIKE $1) LIMIT 20",
                f"%{q}%",
            )
            items = [
                {"anchor_type": "entity", "anchor_ref": r["cdp_code"], "label": r["trade_name"] or r["cdp_code"]}
                for r in rows
            ]
    return ok(items, count=len(items))


# ---------------------------------------------------------------------------
# Thread detail + create
# ---------------------------------------------------------------------------

@router.get("/threads/{thread_ulid}")
@limiter.limit(RATE_DEFAULT)
async def get_thread(thread_ulid: str, request: Request) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        thread = await c.fetchrow("SELECT * FROM forum_thread WHERE thread_ulid = $1", thread_ulid)
        if thread is None:
            return err(f"thread {thread_ulid} not found", status=404)

        posts = await c.fetch(
            "SELECT * FROM forum_post WHERE thread_ulid = $1 ORDER BY created_at ASC", thread_ulid
        )
        post_ulids = [p["post_ulid"] for p in posts]
        anchor_rows = await c.fetch(
            "SELECT * FROM post_anchor WHERE post_ulid = ANY($1::text[])", post_ulids
        ) if post_ulids else []
        vote_rows = await c.fetch(
            "SELECT post_ulid, SUM(value) AS net FROM post_vote WHERE post_ulid = ANY($1::text[]) GROUP BY post_ulid",
            post_ulids,
        ) if post_ulids else []
        net_by_post = {r["post_ulid"]: int(r["net"]) for r in vote_rows}
        anchors_by_post: dict[str, list[dict[str, Any]]] = {}
        for a in anchor_rows:
            anchors_by_post.setdefault(a["post_ulid"], []).append({
                "anchor_ulid": a["anchor_ulid"], "anchor_type": a["anchor_type"],
                "anchor_ref": a["anchor_ref"], "snapshot": a["snapshot"],
                "verified": _is_badge_verified(a["anchor_type"], a["snapshot"]),
            })

        all_author_ulids = [thread["author_user_ulid"]] + [p["author_user_ulid"] for p in posts]
        roles = await _author_roles(c, all_author_ulids)

        post_items = [
            {
                "post_ulid": p["post_ulid"], "author_user_ulid": p["author_user_ulid"],
                "author_role": roles.get(p["author_user_ulid"]),  # carta §4.7: always shown
                "body": p["body"], "is_first_post": p["is_first_post"],
                "created_at": str(p["created_at"]), "net_votes": net_by_post.get(p["post_ulid"], 0),
                "anchors": anchors_by_post.get(p["post_ulid"], []),
            }
            for p in posts
        ]
    return ok({**_serialize_thread(dict(thread), author_role=roles.get(thread["author_user_ulid"])), "posts": post_items})


@router.post("/threads")
@limiter.limit(RATE_DEFAULT)
async def create_thread(
    payload: ThreadCreateRequest,
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    """Carta §6.2: the 'price_check' thread type (Edmunds pattern, §2.5) requires >=1
    anchor — an obligatory anchor for a type whose whole point is validating a price."""
    if payload.thread_type == "price_check" and not payload.anchors:
        raise HTTPException(status_code=422, detail="price_check threads require at least one anchor")

    async with request.app.state.pool.acquire() as c:
        if payload.province_code:
            exists = await c.fetchval(
                "SELECT 1 FROM geo_province WHERE country_code='ES' AND code = $1", payload.province_code
            )
            if not exists:
                raise HTTPException(status_code=422, detail=f"unknown province_code '{payload.province_code}'")

        async with c.transaction():
            new_thread_ulid = ulid()
            await c.execute(
                "INSERT INTO forum_thread (thread_ulid, author_user_ulid, title, province_code, thread_type) "
                "VALUES ($1,$2,$3,$4,$5)",
                new_thread_ulid, session.user_ulid, payload.title, payload.province_code, payload.thread_type,
            )
            new_post_ulid = ulid()
            await c.execute(
                "INSERT INTO forum_post (post_ulid, thread_ulid, author_user_ulid, body, is_first_post) "
                "VALUES ($1,$2,$3,$4,TRUE)",
                new_post_ulid, new_thread_ulid, session.user_ulid, payload.body,
            )
            await _insert_anchors(c, new_post_ulid, payload.anchors)
        thread = await c.fetchrow("SELECT * FROM forum_thread WHERE thread_ulid = $1", new_thread_ulid)
    return ok({**_serialize_thread(dict(thread)), "first_post_ulid": new_post_ulid})


@router.post("/threads/{thread_ulid}/posts")
@limiter.limit(RATE_DEFAULT)
async def create_reply(
    thread_ulid: str,
    payload: PostCreateRequest,
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        thread = await c.fetchrow("SELECT thread_ulid FROM forum_thread WHERE thread_ulid = $1", thread_ulid)
        if thread is None:
            raise HTTPException(status_code=404, detail=f"thread {thread_ulid} not found")

        async with c.transaction():
            new_post_ulid = ulid()
            await c.execute(
                "INSERT INTO forum_post (post_ulid, thread_ulid, author_user_ulid, body) VALUES ($1,$2,$3,$4)",
                new_post_ulid, thread_ulid, session.user_ulid, payload.body,
            )
            await _insert_anchors(c, new_post_ulid, payload.anchors)
            await c.execute(
                "UPDATE forum_thread SET reply_count = reply_count + 1, last_reply_at = now() WHERE thread_ulid = $1",
                thread_ulid,
            )
    return ok({"post_ulid": new_post_ulid, "thread_ulid": thread_ulid})


# ---------------------------------------------------------------------------
# Voting — privilege-gated, anti-inflado, daily-capped (carta §4.5)
# ---------------------------------------------------------------------------

@router.post("/posts/{post_ulid}/vote")
@limiter.limit(RATE_DEFAULT)
async def vote_post(
    post_ulid: str,
    payload: VoteRequest,
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        post = await c.fetchrow("SELECT post_ulid, author_user_ulid FROM forum_post WHERE post_ulid = $1", post_ulid)
        if post is None:
            raise HTTPException(status_code=404, detail=f"post {post_ulid} not found")
        if post["author_user_ulid"] == session.user_ulid:
            raise HTTPException(status_code=403, detail="you cannot vote on your own post")

        rep = await _current_rep(c, session.user_ulid)
        if payload.value == 1 and not can_vote(rep):
            raise HTTPException(status_code=403, detail=f"votar requiere reputación >= {VOTE_PRIVILEGE_MIN_REP}")
        if payload.value == -1 and not can_downvote(rep):
            raise HTTPException(
                status_code=403, detail=f"downvote requiere reputación >= {DOWNVOTE_PRIVILEGE_MIN_REP}"
            )

        async with c.transaction():
            if payload.value == 0:
                await c.execute(
                    "DELETE FROM post_vote WHERE post_ulid = $1 AND user_ulid = $2", post_ulid, session.user_ulid
                )
            else:
                await c.execute(
                    "INSERT INTO post_vote (post_ulid, user_ulid, value) VALUES ($1,$2,$3) "
                    "ON CONFLICT (post_ulid, user_ulid) DO UPDATE SET value = EXCLUDED.value, created_at = now()",
                    post_ulid, session.user_ulid, payload.value,
                )

                author_ulid = post["author_user_ulid"]
                last_credit = await _last_pair_credit(c, author_ulid, session.user_ulid)
                now = datetime.now(timezone.utc)
                within_window = last_credit is not None and (now - last_credit) < timedelta(days=PEER_INFLATION_WINDOW_DAYS)

                if not within_window:
                    daily_credited = await _rep_daily_credited(c, author_ulid)
                    if daily_credited < REP_DAILY_CAP:
                        if payload.value == 1:
                            # §4.5's "post con anchor VERIFICADO" uses the same strict
                            # two-condition badge as §4.2 (existence + price cross-check
                            # for vehicles) — a post whose anchor exists but whose price
                            # has drifted from the ledger reconstruction should not earn
                            # the higher bonus either.
                            anchor_rows = await c.fetch(
                                "SELECT anchor_type, snapshot FROM post_anchor WHERE post_ulid = $1", post_ulid
                            )
                            has_verified_anchor = any(
                                _is_badge_verified(r["anchor_type"], r["snapshot"]) for r in anchor_rows
                            )
                            delta = upvote_delta(has_verified_anchor)
                            reason = "upvote_anchor" if has_verified_anchor else "upvote_no_anchor"
                        else:
                            delta = -2
                            reason = "downvote_received"
                        await c.execute(
                            "INSERT INTO reputation_event (event_ulid, user_ulid, delta, reason, related_user_ulid, source_post_ulid) "
                            "VALUES ($1,$2,$3,$4,$5,$6)",
                            ulid(), author_ulid, delta, reason, session.user_ulid, post_ulid,
                        )
                    if payload.value == -1:
                        voter_daily = await _rep_daily_credited(c, session.user_ulid)
                        if voter_daily < REP_DAILY_CAP:
                            await c.execute(
                                "INSERT INTO reputation_event (event_ulid, user_ulid, delta, reason, related_user_ulid, source_post_ulid) "
                                "VALUES ($1,$2,-1,'downvote_cast',$3,$4)",
                                ulid(), session.user_ulid, author_ulid, post_ulid,
                            )

            net = await c.fetchval("SELECT COALESCE(SUM(value), 0) FROM post_vote WHERE post_ulid = $1", post_ulid)
    return ok({"post_ulid": post_ulid, "net_votes": int(net), "your_vote": payload.value})


# ---------------------------------------------------------------------------
# Moderation (carta §4.5: 'moderar/borrar = SIEMPRE manual de staff'; §4.5 Craigslist-exact:
# the hide threshold N is never published in the API response)
# ---------------------------------------------------------------------------

@router.post("/posts/{post_ulid}/flag")
@limiter.limit(RATE_DEFAULT)
async def flag_post(
    post_ulid: str,
    payload: FlagRequest,
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        post = await c.fetchrow("SELECT post_ulid FROM forum_post WHERE post_ulid = $1", post_ulid)
        if post is None:
            raise HTTPException(status_code=404, detail=f"post {post_ulid} not found")
        rep = await _current_rep(c, session.user_ulid)
        if not can_flag(rep):
            raise HTTPException(status_code=403, detail=f"flag requiere reputación >= {FLAG_PRIVILEGE_MIN_REP}")
        existing = await c.fetchval(
            "SELECT 1 FROM moderation_flag WHERE post_ulid = $1 AND flagger_user_ulid = $2",
            post_ulid, session.user_ulid,
        )
        if existing:
            raise HTTPException(status_code=409, detail="you already flagged this post")
        await c.execute(
            "INSERT INTO moderation_flag (flag_ulid, post_ulid, flagger_user_ulid, reason) VALUES ($1,$2,$3,$4)",
            ulid(), post_ulid, session.user_ulid, payload.reason,
        )
    return ok({"post_ulid": post_ulid, "flagged": True})


async def _require_staff(conn: asyncpg.Connection, user_ulid: str) -> None:
    role = await conn.fetchval("SELECT role FROM app_user WHERE user_ulid = $1", user_ulid)
    if role != "staff":
        raise HTTPException(status_code=403, detail="staff only")


@router.get("/moderation/queue")
@limiter.limit(RATE_DEFAULT)
async def moderation_queue(
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        await _require_staff(c, session.user_ulid)
        rows = await c.fetch(
            """
            SELECT mf.*, fp.body, fp.author_user_ulid
              FROM moderation_flag mf JOIN forum_post fp ON fp.post_ulid = mf.post_ulid
             WHERE mf.resolved_at IS NULL
             ORDER BY mf.created_at ASC
            """
        )
    items = [
        {
            "flag_ulid": r["flag_ulid"], "post_ulid": r["post_ulid"], "reason": r["reason"],
            "created_at": str(r["created_at"]), "post_body": r["body"], "post_author": r["author_user_ulid"],
        }
        for r in rows
    ]
    return ok(items, count=len(items))


@router.post("/moderation/flags/{flag_ulid}/resolve")
@limiter.limit(RATE_DEFAULT)
async def resolve_flag(
    flag_ulid: str,
    payload: ModerationResolveRequest,
    request: Request,
    session: CurrentSession = Depends(get_current_session),
) -> JSONResponse:
    """Carta §4.5: moderation is ALWAYS manual staff action, never automatic (Discourse
    TL4-exact rule). SLA-to-resolution is measured by ``resolved_at - created_at`` —
    the internal-SLA metric F6 publishes (carta §9 F6)."""
    async with request.app.state.pool.acquire() as c:
        await _require_staff(c, session.user_ulid)
        flag = await c.fetchrow("SELECT * FROM moderation_flag WHERE flag_ulid = $1", flag_ulid)
        if flag is None:
            raise HTTPException(status_code=404, detail="flag not found")
        if flag["resolved_at"] is not None:
            raise HTTPException(status_code=409, detail="flag already resolved")
        await c.execute(
            "UPDATE moderation_flag SET resolved_at = now(), resolved_by_user_ulid = $1, resolution = $2 "
            "WHERE flag_ulid = $3",
            session.user_ulid, payload.resolution, flag_ulid,
        )
    return ok({"flag_ulid": flag_ulid, "resolution": payload.resolution})


@router.get("/moderation/sla")
@limiter.limit(RATE_DEFAULT)
async def moderation_sla(
    request: Request,
    session: CurrentSession = Depends(get_current_session),
    window_days: int = Query(default=30, ge=1, le=365),
) -> JSONResponse:
    """Carta §9 F6 / §2.3 (Nextdoor reference: ~90% reviewed <6h — our own number is
    MEASURED and published INTERNALLY, never promised until it is real). Staff-only:
    an SLA number is an operational metric, not a public trust signal (unlike
    match_liveness_rate, carta §4.10, which IS public by design)."""
    async with request.app.state.pool.acquire() as c:
        await _require_staff(c, session.user_ulid)
        rows = await c.fetch(
            """
            SELECT EXTRACT(EPOCH FROM (resolved_at - created_at)) / 3600.0 AS hours
              FROM moderation_flag
             WHERE resolved_at IS NOT NULL AND created_at > now() - make_interval(days => $1)
             ORDER BY hours
            """,
            window_days,
        )
        pending = await c.fetchval(
            "SELECT COUNT(*) FROM moderation_flag WHERE resolved_at IS NULL"
        )
    hours = [float(r["hours"]) for r in rows]
    if not hours:
        return ok({
            "n_resolved": 0, "median_hours": None, "p90_hours": None,
            "pct_under_6h": None, "pending_now": pending, "window_days": window_days,
        })
    hours.sort()
    n = len(hours)
    median = hours[n // 2] if n % 2 else (hours[n // 2 - 1] + hours[n // 2]) / 2
    p90 = hours[min(n - 1, int(0.9 * n))]
    pct_under_6h = sum(1 for h in hours if h <= 6.0) / n
    return ok({
        "n_resolved": n, "median_hours": median, "p90_hours": p90,
        "pct_under_6h": pct_under_6h, "pending_now": pending, "window_days": window_days,
    })


# ---------------------------------------------------------------------------
# Profile (carta §6.4)
# ---------------------------------------------------------------------------

@router.get("/users/{user_ulid}")
@limiter.limit(RATE_DEFAULT)
async def user_profile(user_ulid: str, request: Request) -> JSONResponse:
    async with request.app.state.pool.acquire() as c:
        user = await c.fetchrow("SELECT user_ulid, name, role, created_at FROM app_user WHERE user_ulid = $1", user_ulid)
        if user is None:
            return err(f"user {user_ulid} not found", status=404)
        rep = await _current_rep(c, user_ulid)
        breakdown = await c.fetch(
            "SELECT reason, SUM(delta) AS total, COUNT(*) AS n FROM reputation_event "
            "WHERE user_ulid = $1 GROUP BY reason ORDER BY total DESC",
            user_ulid,
        )
        thread_count = await c.fetchval("SELECT COUNT(*) FROM forum_thread WHERE author_user_ulid = $1", user_ulid)
        post_count = await c.fetchval("SELECT COUNT(*) FROM forum_post WHERE author_user_ulid = $1", user_ulid)
        wanted_count = await c.fetchval("SELECT COUNT(*) FROM wanted_listing WHERE user_ulid = $1", user_ulid)
    return ok({
        "user_ulid": user["user_ulid"], "name": user["name"], "role": user["role"],
        "member_since": str(user["created_at"]),
        "reputation": rep,
        "reputation_breakdown": [
            {"reason": r["reason"], "total": int(r["total"]), "count": int(r["n"])} for r in breakdown
        ],
        "thread_count": thread_count, "post_count": post_count, "wanted_count": wanted_count,
    })
