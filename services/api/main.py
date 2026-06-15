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
    the dealer genuinely lists them). /health reports the GLOBAL unique count
    (v_canonical_vehicle canonical-only + available = 1 486 285).
  - /geo endpoints serve only active non-particular entities (status='active'
    AND kind <> 'particular').
  - /health reports sealed dealer count (v_canonical) and sealed vehicle
    count (v_canonical_vehicle canonical + available).
  - /delta is cluster-aware: events from ALL cluster members.
  - /vehicles/{ulid} resolves aliases to canonical; /vehicles/{ulid}/history
    returns the full event stream for a vehicle.
  - /geo/{province}/municipalities/{muni}/entities scopes to a municipality.
  - /alerts returns active (unresolved) alerts with origin.
  - /sources returns source_health rows for monitoring.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI

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
from services.api.routers import entities, geo, ops, platforms, vehicles


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(DSN, min_size=1, max_size=8)
    try:
        yield
    finally:
        await app.state.pool.close()


app = FastAPI(title="Cardeep API", version="0.2.0", lifespan=lifespan)

app.include_router(ops.router)
app.include_router(entities.router)
app.include_router(geo.router)
app.include_router(vehicles.router)
app.include_router(platforms.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8090)
