"""Cardeep live API (F2 skeleton -> F6 full).

Serves per-entity inventory and delta over the PostgreSQL backbone.
Consistent envelope: {ok, data, error, meta}.

Run: uvicorn services.api.main:app --host 127.0.0.1 --port 8090
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

import asyncpg
from fastapi import FastAPI
from fastapi.responses import JSONResponse

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(DSN, min_size=1, max_size=8)
    try:
        yield
    finally:
        await app.state.pool.close()


app = FastAPI(title="Cardeep API", version="0.1.0", lifespan=lifespan)


def ok(data: Any, **meta: Any) -> JSONResponse:
    return JSONResponse({"ok": True, "data": data, "error": None, "meta": meta or None})


def err(message: str, status: int = 404) -> JSONResponse:
    return JSONResponse({"ok": False, "data": None, "error": message, "meta": None}, status_code=status)


@app.get("/health")
async def health() -> JSONResponse:
    async with app.state.pool.acquire() as c:
        counts = {
            "entities": await c.fetchval("SELECT count(*) FROM entity"),
            "vehicles_available": await c.fetchval("SELECT count(*) FROM vehicle WHERE status='available'"),
            "events": await c.fetchval("SELECT count(*) FROM vehicle_event"),
            "provinces": await c.fetchval("SELECT count(*) FROM geo_province"),
            "municipalities": await c.fetchval("SELECT count(*) FROM geo_municipality"),
        }
    return ok({"status": "live", "counts": counts})


@app.get("/entities/{cdp_code}")
async def get_entity(cdp_code: str) -> JSONResponse:
    async with app.state.pool.acquire() as c:
        row = await c.fetchrow("SELECT * FROM entity WHERE cdp_code = $1", cdp_code)
        if row is None:
            return err(f"entity {cdp_code} not found")
        n = await c.fetchval(
            "SELECT count(*) FROM vehicle WHERE entity_ulid=$1 AND status='available'", row["entity_ulid"])
        data = dict(row)
        data["created_at"] = str(data["created_at"])
        data["last_seen"] = str(data["last_seen"])
        data["available_inventory"] = n
        return ok(data)


@app.get("/entities/{cdp_code}/inventory")
async def get_inventory(cdp_code: str) -> JSONResponse:
    async with app.state.pool.acquire() as c:
        eulid = await c.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", cdp_code)
        if eulid is None:
            return err(f"entity {cdp_code} not found")
        rows = await c.fetch(
            "SELECT vehicle_ulid, deep_link, title, make, model, year, km, price, currency, "
            "fuel, transmission, photo_url, status, first_seen, last_seen "
            "FROM vehicle WHERE entity_ulid=$1 AND status='available' ORDER BY first_seen DESC",
            eulid)
        items = [{**dict(r), "price": float(r["price"]) if r["price"] is not None else None,
                  "first_seen": str(r["first_seen"]), "last_seen": str(r["last_seen"])} for r in rows]
        return ok(items, count=len(items))


@app.get("/entities/{cdp_code}/delta")
async def get_delta(cdp_code: str, since: str | None = None) -> JSONResponse:
    async with app.state.pool.acquire() as c:
        eulid = await c.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", cdp_code)
        if eulid is None:
            return err(f"entity {cdp_code} not found")
        if since:
            rows = await c.fetch(
                "SELECT event_type, old_value, new_value, observed_at FROM vehicle_event "
                "WHERE entity_ulid=$1 AND observed_at >= $2::timestamptz ORDER BY observed_at DESC",
                eulid, since)
        else:
            rows = await c.fetch(
                "SELECT event_type, old_value, new_value, observed_at FROM vehicle_event "
                "WHERE entity_ulid=$1 ORDER BY observed_at DESC LIMIT 500", eulid)
        items = [{**dict(r), "observed_at": str(r["observed_at"])} for r in rows]
        return ok(items, count=len(items))


@app.get("/geo/{province_code}/entities")
async def entities_by_province(province_code: str) -> JSONResponse:
    async with app.state.pool.acquire() as c:
        rows = await c.fetch(
            "SELECT cdp_code, kind, trade_name, legal_name, municipality_code, is_tier1, status "
            "FROM entity WHERE province_code=$1 ORDER BY trade_name", province_code)
        return ok([dict(r) for r in rows], count=len(rows), province=province_code)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8090)
