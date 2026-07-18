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
    PEER_INFLATION_WINDOW_DAYS,
    REP_DAILY_CAP,
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


async def _verify_anchor(conn: asyncpg.Connection, anchor_type: str, anchor_ref: str) -> dict[str, Any] | None:
    """Return a JSONB-able snapshot if the anchor target exists NOW, else None (carta §4.2:
    'nunca badge por defecto' — an anchor to a vanished target is stored anyway, per the
    carta's drift-detection intent, but flagged unverified via a null snapshot)."""
    if anchor_type == "vehicle":
        row = await conn.fetchrow(
            "SELECT make, model, year, price, status, photo_url, deep_link, last_seen "
            "FROM vehicle WHERE vehicle_ulid = $1",
            anchor_ref,
        )
        if row is None:
            return None
        return {
            "make": row["make"], "model": row["model"], "year": row["year"],
            "price": float(row["price"]) if row["price"] is not None else None, "status": row["status"],
            "photo_url": row["photo_url"], "deep_link": row["deep_link"], "last_seen": str(row["last_seen"]),
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


def _serialize_thread(row: dict[str, Any], rank: float | None = None) -> dict[str, Any]:
    d = {
        "thread_ulid": row["thread_ulid"],
        "title": row["title"],
        "author_user_ulid": row["author_user_ulid"],
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
    if sort == "hot":
        for it in items:
            it["_rank"] = rank_score(int(it["net_votes"]), int(it["verified_anchor_count"]), float(it["hours_age"]))
        items.sort(key=lambda x: x["_rank"], reverse=True)
    else:
        items.sort(key=lambda x: x["created_at"], reverse=True)
    page_items = items[offset:offset + size]
    has_more = len(items) > offset + size
    out = [_serialize_thread(it, it.get("_rank")) for it in page_items]
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
                SELECT vehicle_ulid, make, model, year, price, deep_link
                  FROM vehicle
                 WHERE status = 'available' AND (make ILIKE $1 OR model ILIKE $1 OR title ILIKE $1)
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
                "SELECT cdp_code, trade_name FROM entity WHERE trade_name ILIKE $1 OR cdp_code ILIKE $1 LIMIT 20",
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
                "verified": a["snapshot"] != {},
            })

        post_items = [
            {
                "post_ulid": p["post_ulid"], "author_user_ulid": p["author_user_ulid"],
                "body": p["body"], "is_first_post": p["is_first_post"],
                "created_at": str(p["created_at"]), "net_votes": net_by_post.get(p["post_ulid"], 0),
                "anchors": anchors_by_post.get(p["post_ulid"], []),
            }
            for p in posts
        ]
    return ok({**_serialize_thread(dict(thread)), "posts": post_items})


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
            raise HTTPException(status_code=403, detail=f"votar requiere reputación >= {10}")
        if payload.value == -1 and not can_downvote(rep):
            raise HTTPException(status_code=403, detail="downvote requiere más reputación")

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
                            anchor_count = await c.fetchval(
                                "SELECT COUNT(*) FROM post_anchor WHERE post_ulid = $1 AND snapshot <> '{}'::jsonb",
                                post_ulid,
                            )
                            delta = upvote_delta(anchor_count > 0)
                            reason = "upvote_anchor" if anchor_count > 0 else "upvote_no_anchor"
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
            raise HTTPException(status_code=403, detail="flag requiere más reputación")
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
