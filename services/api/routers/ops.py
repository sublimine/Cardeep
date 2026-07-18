"""/health, /alerts, /sources, /engine/status — operational monitoring endpoints.

SU-D2 additions:
  - /health: rate-limited at RATE_HEALTH (generous — liveness probes must pass).
  - /alerts: rate-limited at RATE_DEFAULT; NOT cached (near-real-time data).
  - /sources: rate-limited at RATE_DEFAULT; NOT cached (monitoring data).

F5 addition (00-marketplace-engine.md):
  - /engine/status: rate-limited at RATE_DEFAULT; NOT cached (the badge/uptime signal §7
    exists to make trustworthy — a cached "live" reading would defeat the whole point).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import asyncpg
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from pipeline.ops.engine_uptime import bucket_uptime, clipped_window, uptime_report_to_dict
from services.api.cache import cache_set, try_cache_get
from services.api.deps import err, ok, page_slice, require_api_key
from services.api.ratelimit import RATE_DEFAULT, RATE_EXPENSIVE, RATE_HEALTH, limiter
from services.api.stats import DEFAULT_COUNTRY, fetch_stats

router = APIRouter()


# ---------------------------------------------------------------------------
# /health — UNAUTHENTICATED liveness probe (no business data)
# /stats  — AUTHENTICATED sealed product counts (moved off /health: audit)
# ---------------------------------------------------------------------------

@router.get("/health")
@limiter.limit(RATE_HEALTH)
async def health(request: Request) -> JSONResponse:
    """Liveness probe — UNAUTHENTICATED by contract (load balancers / uptime probes).

    Returns only {status, db}. It deliberately exposes NO product counts: coverage
    totals (dealers / vehicles) are a competitive signal and now live behind auth at
    /stats — the audit flagged that anonymous callers could read the product's scale
    here. A single ``SELECT 1`` round-trip makes this a real liveness check (DB
    reachable), not merely process-up, while staying cheap (the old /health ran 5
    expensive COUNT(*) on every probe — uncached).
    """
    db_ok = True
    try:
        async with request.app.state.pool.acquire() as c:
            await c.fetchval("SELECT 1")
    except Exception:
        db_ok = False
    return ok({"status": "live" if db_ok else "degraded",
               "db": "ok" if db_ok else "down"})


@router.get("/stats")
@limiter.limit(RATE_EXPENSIVE)
async def stats(
    request: Request,
    country: str = Query(
        default=DEFAULT_COUNTRY, min_length=2, max_length=2,
        description="ISO-3166 alpha-2 tenant whose product counts to report (default 'ES')."),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Sealed product counts — AUTHENTICATED (competitive coverage signal).

    Moved off /health (audit): anonymous callers must not learn coverage scale.

    Per-country (0066): ``?country`` selects the tenant (default 'ES'); the counts are scoped to that
    one country, never a country-blind sum. The default 'ES' is byte-identical to the historical /stats.

    dealers        — REAL car sales points ("Puntos de venta"): resolved-distinct,
                     kind NOT IN (particular, desguace), with >=1 servable vehicle.
                     Excludes private platform listings (particular), parts-only
                     scrapyards (desguace) and discovered-but-empty entities. Honest
                     figure ~19.1k (the old kind<>'particular' count ~54.6k included
                     ~35.4k empty + ~2.3k desguace). See services/api/stats.py.
    vehicles_unique_available — canonical-only + status='available' (one row per
                    physical car, not the raw count that includes cross-entity aliases).
    events         — total event rows (not filtered: historical record).
    provinces      — static geo table row count.
    municipalities — static geo table row count.

    SU-D2: RATE_EXPENSIVE + cached (5 COUNT(*) over full tables; stable between
    harvests). Caching here also removes the per-probe cost the old /health paid.
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        # Fast path: the precomputed product_stats row for `country` (one row per tenant since 0066,
        # refreshed off-request by the scheduler) — a single-row read instead of 5 COUNT(DISTINCT)/JOIN
        # over millions (~83s cold). fetch_stats falls back to a live compute when the row/table/column
        # is absent (pre-migration / pre-first-refresh / a tenant not yet refreshed), so the endpoint
        # always returns the EXACT counts. computed_at is exposed so the (bounded) cache age is explicit.
        counts, computed_at = await fetch_stats(c, country.upper())
    if computed_at is not None:
        response = ok({"counts": counts}, computed_at=str(computed_at), source="precomputed")
    else:
        response = ok({"counts": counts}, source="live")
    return cache_set(request, response)


# ---------------------------------------------------------------------------
# GAP 5 new: /alerts (active unresolved) + /sources (source_health)
# ---------------------------------------------------------------------------

@router.get("/alerts")
@limiter.limit(RATE_DEFAULT)
async def list_alerts(
    request: Request,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """GAP-5: Active (unresolved) alerts with exact origin.

    Columns served: id, origin, severity, message, payload, created_at.
    Sorted by severity priority (critical → warning → info) then by most
    recent first so the most urgent alerts surface at the top.

    Only rows WHERE resolved_at IS NULL are returned — resolved alerts
    are not surfaced here (historical; use a separate query if needed).

    Not cached: alert state can change at any time.
    """
    offset = (page - 1) * size
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            """
            SELECT id, origin, severity, message, payload, created_at
              FROM alert
             WHERE resolved_at IS NULL
             ORDER BY
               CASE severity
                 WHEN 'critical' THEN 0
                 WHEN 'warning'  THEN 1
                 ELSE                 2
               END,
               created_at DESC
             LIMIT $1 OFFSET $2
            """,
            size + 1,
            offset,
        )
        rows, has_more = page_slice(rows, size)
        items = [
            {
                **dict(r),
                "created_at": str(r["created_at"]),
            }
            for r in rows
        ]
        return ok(
            items,
            page=page,
            size=size,
            returned=len(items),
            has_more=has_more,
        )


@router.get("/sources")
@limiter.limit(RATE_DEFAULT)
async def list_sources(
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """GAP-5: Source health overview for all known scrapers/sources.

    Columns: source_key, status, consecutive_fails, last_ok, last_fail, is_tier1.
    Sorted: degraded/down first (most urgent), then by consecutive_fails DESC
    so the sickest sources are at the top.

    Not cached: source_health is near-real-time monitoring data.
    """
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            """
            SELECT source_key, status, consecutive_fails,
                   last_ok, last_fail, is_tier1
              FROM source_health
             ORDER BY
               CASE status
                 WHEN 'down'     THEN 0
                 WHEN 'degraded' THEN 1
                 WHEN 'unknown'  THEN 2
                 ELSE                 3
               END,
               consecutive_fails DESC,
               source_key
            """
        )
        items = [
            {
                **dict(r),
                "last_ok": str(r["last_ok"]) if r["last_ok"] else None,
                "last_fail": str(r["last_fail"]) if r["last_fail"] else None,
            }
            for r in rows
        ]
        return ok(items, count=len(items))


# ---------------------------------------------------------------------------
# F5 (00-marketplace-engine.md): /engine/status — motor status surface.
#
# Exposes the §4 badge (LATIENDO/DEGRADADO/PARADO), the harvest scheduler's lease/heartbeat,
# apscheduler_jobs (the §7 vía-B signal — a caller polling this twice >=15min apart can confirm
# next_run_time actually advanced, independent of scheduler_lease), an honest best-effort
# cold-start replay-progress figure, and the F6 uptime track record (30d/90d).
# ---------------------------------------------------------------------------

# The harvest scheduler's singleton advisory-lock key (pipeline/ops/scheduler.py:
# `_SCHEDULER_SINGLETON_LOCK = 0x43415244`). Duplicated as a LOCAL literal, never imported: this
# async asyncpg API process must not import pipeline.ops.scheduler (sync psycopg2 + subprocess,
# heavy import chain) — same "no shared import graph with what is observed" reasoning as
# pipeline/ops/engine_watchdog.py's own local _HARVEST_LOCK_KEY.
_HARVEST_LOCK_KEY: int = 0x43415244  # 1128354372

# Mirrors pipeline.ops.scheduler.TICK_INTERVAL_MINUTES (local literal, same reasoning as above —
# kept honest by a contract test, tests/test_engine_status_api.py::test_tick_interval_matches_
# scheduler_constant, which imports the real constant and asserts equality without importing it
# at runtime here).
_TICK_INTERVAL_MINUTES: int = 15

# §4 badge boundaries: LATIENDO age < 2xTICK (30min); DEGRADADO age < 24h; PARADO otherwise/no lease.
_BADGE_LATIENDO_MAX_SECONDS: int = 2 * _TICK_INTERVAL_MINUTES * 60
_BADGE_DEGRADADO_MAX_SECONDS: int = 24 * 3600


def _engine_badge(age_seconds: float | None) -> str:
    """Pure §4 badge classification. ``age_seconds=None`` (no lease row at all) is PARADO."""
    if age_seconds is None:
        return "PARADO"
    if age_seconds < _BADGE_LATIENDO_MAX_SECONDS:
        return "LATIENDO"
    if age_seconds < _BADGE_DEGRADADO_MAX_SECONDS:
        return "DEGRADADO"
    return "PARADO"


def _job_next_run_iso(next_run_time: float | None) -> str | None:
    """apscheduler_jobs.next_run_time is a POSIX float (APScheduler's own storage format,
    SQLAlchemyJobStore) — convert to an ISO-8601 UTC string for the JSON payload. None
    (a paused/removed job) stays None."""
    if next_run_time is None:
        return None
    return datetime.fromtimestamp(next_run_time, tz=timezone.utc).isoformat()


@router.get("/engine/status")
@limiter.limit(RATE_DEFAULT)
async def engine_status(
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """F5: motor status — badge + lease/heartbeat + apscheduler jobs + cold-start replay
    progress + F6 uptime track record (30d/90d).

    Badge (§4 row 1) is computed in SQL (``age_seconds = EXTRACT(EPOCH FROM now()-last_heartbeat)``)
    so the LATIENDO/DEGRADADO/PARADO boundary is never skewed by API-host vs DB-host clock drift.

    ``replay_progress`` is an honest APPROXIMATION, not the exact "fuentes DUE al arrancar" the
    carta describes: that denominator (how many sources were overdue at the exact instant the
    current holder claimed the lease) is not captured anywhere and cannot be reconstructed
    retroactively. What IS verifiable — and is what this reports — is how many of the registered
    sources have a successful harvest (``last_ok``) at or after the current holder's
    ``started_at``, out of the total registered; the ``note`` field says so explicitly rather
    than silently presenting an approximation as the exact promised metric.

    ``uptime`` (F6) is computed from ``engine_heartbeat_log`` (migration 0085), which did not
    exist before this fase shipped — a fresh deployment reports ``full_window_available: false``
    and a short ``observed_from``/``observed_to`` span rather than fabricating pre-ledger history
    as downtime (pipeline.ops.engine_uptime's own anti-alucinación guard).

    Not cached: this endpoint IS the near-real-time trust signal §7 exists to serve.
    """
    async with request.app.state.pool.acquire() as c:
        lease = await c.fetchrow(
            """
            SELECT holder, pid, started_at, last_heartbeat,
                   EXTRACT(EPOCH FROM (now() - last_heartbeat)) AS age_seconds
              FROM scheduler_lease
             WHERE lock_key = $1
            """,
            _HARVEST_LOCK_KEY,
        )
        age_seconds = float(lease["age_seconds"]) if lease is not None else None

        # apscheduler_jobs is owned by APScheduler's SQLAlchemyJobStore, not a migration — it is
        # created lazily the first time pipeline.ops.scheduler's live daemon starts (see
        # pipeline/ops/scheduler.py::_start_scheduler, `jobstores = {"default": SQLAlchemyJobStore(...)}`).
        # On a freshly migrated DB where the harvest daemon has never run yet (fresh deploy / the
        # db-tests CI seed, which only migrates + seeds — it never starts the scheduler process), the
        # table does not exist. An honest "no jobs registered yet" (empty list) rather than a 500 —
        # same anti-alucinación posture as the F6 uptime ledger below (never fabricate, degrade
        # explicitly), and the same UndefinedTableError idiom services/api/stats.py::fetch_stats
        # already uses for product_stats pre-migration/pre-first-refresh.
        try:
            jobs = await c.fetch("SELECT id, next_run_time FROM apscheduler_jobs ORDER BY next_run_time")
        except asyncpg.exceptions.UndefinedTableError:
            jobs = []

        sources_total = await c.fetchval("SELECT count(*) FROM source_health")
        sources_harvested_since_start = None
        if lease is not None:
            sources_harvested_since_start = await c.fetchval(
                "SELECT count(*) FROM source_health WHERE last_ok >= $1",
                lease["started_at"],
            )

        # F6 — fetch once, derive BOTH 30d and 90d reports from the same beat list (no duplicate
        # query for the two windows).
        now_db = await c.fetchval("SELECT now()")
        observed_since = await c.fetchval(
            "SELECT min(beat_at) FROM engine_heartbeat_log WHERE lock_key = $1",
            _HARVEST_LOCK_KEY,
        )
        beats: list[datetime] = []
        if observed_since is not None:
            beat_rows = await c.fetch(
                "SELECT beat_at FROM engine_heartbeat_log "
                "WHERE lock_key = $1 AND beat_at >= $2 ORDER BY beat_at",
                _HARVEST_LOCK_KEY, now_db - timedelta(days=90),
            )
            beats = [r["beat_at"] for r in beat_rows]

    uptime: dict[str, dict] = {}
    for days in (30, 90):
        win_start, win_end, full = clipped_window(
            now=now_db, requested_days=days, observed_since=observed_since)
        report = bucket_uptime(beats, window_start=win_start, window_end=win_end)
        uptime[f"{days}d"] = uptime_report_to_dict(report, requested_days=days, full_window_available=full)

    return ok({
        "badge": _engine_badge(age_seconds),
        "lease": {
            "holder": lease["holder"] if lease is not None else None,
            "pid": lease["pid"] if lease is not None else None,
            "started_at": str(lease["started_at"]) if lease is not None else None,
            "last_heartbeat": str(lease["last_heartbeat"]) if lease is not None else None,
            "age_seconds": age_seconds,
        },
        "jobs": [
            {"id": j["id"], "next_run_time": _job_next_run_iso(j["next_run_time"])}
            for j in jobs
        ],
        "replay_progress": {
            "sources_total": sources_total,
            "sources_harvested_since_holder_started": sources_harvested_since_start,
            "note": (
                "aproximado: fuentes con last_ok posterior al arranque del holder actual, sobre "
                "el total registrado — NO es 'fuentes DUE al arrancar' (ese dato no se captura "
                "retroactivamente)"
            ),
        },
        "uptime": uptime,
    })
