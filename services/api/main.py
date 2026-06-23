"""Cardeep live API (F2 skeleton -> F6 full, all 7 gaps closed).

Serves per-entity inventory and delta over the PostgreSQL backbone.
Consistent envelope: {ok, data, error, meta}.

Run: uvicorn services.api.main:app --host 127.0.0.1 --port 8090

Pagination (B3.1)
-----------------
Endpoints that can return unbounded rows accept:
  page: int >= 1          (default 1)
  size: int in [1..200]   (default 50, clamped)

The ``meta`` block for paginated responses carries:
  {page, size, returned, has_more}

``has_more`` is True when the DB returned exactly ``size`` rows, meaning
there MAY be a next page.  A full COUNT(*) is intentionally avoided on
tables with 500 k+ rows.

Sealed product surface
----------------------
  - /entities/{cdp}/inventory dedups WITHIN the dealer cluster by
    canonical_vehicle_ulid (collapses the dealer's own cross-platform
    duplicates; KEEPS cars whose global canonical sits in another dealer —
    the dealer genuinely lists them). /stats (authed) reports the GLOBAL unique
    count (v_canonical_vehicle canonical-only + available).
  - /geo endpoints serve only active non-particular entities (status='active'
    AND kind <> 'particular'). NOTE (audit P2 E-platforms-status): the per-dealer
    /entities/{cdp}/inventory and /platforms/{cdp}/inventory endpoints deliberately
    do NOT apply the entity-status filter — a directly-requested dealer's stock is
    served regardless of verification status ("sacarle TODO su stock"), whereas /geo
    is the curated map of confirmed (active) dealers. The divergence is intentional.
  - /health is a liveness probe (status + DB ping, UNAUTHENTICATED); product counts
    moved to /stats (authed) — coverage scale is a competitive signal (audit P2/P1).
  - /delta is cluster-aware: events from ALL cluster members.
  - /vehicles/{ulid} resolves aliases to canonical; /vehicles/{ulid}/history
    returns the full event stream for a vehicle.
  - /geo/{province}/municipalities/{muni}/entities scopes to a municipality.
  - /alerts returns active (unresolved) alerts with origin.
  - /sources returns source_health rows for monitoring.

SU-D2: Security hardening
--------------------------
  Rate-limiting (slowapi, in-memory):
    Global default: 120/minute. Expensive endpoints: 30/minute.
    Controlled by env var CARDEEP_API_RATELIMIT_ENABLED (default "1").
    Set to "0" for test runs to avoid tripping the 89 existing API tests.
    429 responses use the project envelope {ok, data, error, meta}.

  Response caching (cachetools TTLCache, in-memory):
    Stable read endpoints (inventory/geo-tree/completeness) are cached
    for CACHE_TTL_SECONDS seconds with a CACHE_MAXSIZE entry cap.
    Cache key = METHOD:PATH?sorted-query-string.
    meta.cache = "hit" | "miss" is injected into every cached response.
    /health, /alerts, /sources are explicitly excluded.
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Shared helpers — re-exported here so test files that import from
# services.api.main (e.g. `from services.api.main import DSN`) keep working.
from services.api.deps import (  # noqa: F401
    DSN,
    ClusterInfo,
    err,
    ok,
    require_api_key,
    resolve_cluster,
)
from services.api.ratelimit import limiter, rate_limit_handler
from services.api.routers import entities, geo, ops, platforms, vehicles

# Prod-gated fail-fast: in CARDEEP_ENV=prod, refuse to start on the dev-default DSN.
# No-op in dev/test (CARDEEP_ENV unset) — startup stays byte-identical.
from pipeline.config_guard import assert_safe_dsn


@asynccontextmanager
async def lifespan(app: FastAPI):
    assert_safe_dsn(DSN, var="CARDEEP_DSN")
    app.state.pool = await asyncpg.create_pool(DSN, min_size=1, max_size=8)
    try:
        yield
    finally:
        await app.state.pool.close()


app = FastAPI(title="Cardeep API", version="0.2.0", lifespan=lifespan)

# ---------------------------------------------------------------------------
# SU-D2: Rate-limiting middleware and exception handler.
#
# SlowAPIMiddleware intercepts every request and enforces limits declared via
# @limiter.limit() decorators on individual route handlers.
# The custom rate_limit_handler replaces slowapi's plain-text 429 response
# with the project's consistent {ok, data, error, meta} envelope.
# ---------------------------------------------------------------------------

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# ---------------------------------------------------------------------------
# CORS — the browser frontend (web/) is served from a different origin in dev
# (Vite :5173 / preview :4173) and would otherwise be blocked. Origins are
# configurable via CARDEEP_CORS_ORIGINS (comma-separated) for other deployments.
# Added last so it is the outermost middleware and handles preflight first.
# ---------------------------------------------------------------------------
_cors_origins = os.environ.get(
    "CARDEEP_CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins.split(",") if o.strip()],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["X-API-Key", "Content-Type"],
)

app.include_router(ops.router)
app.include_router(entities.router)
app.include_router(geo.router)
app.include_router(vehicles.router)
app.include_router(platforms.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8090)
