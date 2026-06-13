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


@app.get("/geo/{province_code}/tree")
async def province_inventory_tree(province_code: str) -> JSONResponse:
    """Province inventory grouped pais -> PROVINCIA -> COMARCA -> ciudad, with a
    clean count tree and zero NULL-geo noise (only municipality-resolved entities,
    inner-joined through the comarca layer)."""
    async with app.state.pool.acquire() as c:
        prov = await c.fetchrow(
            "SELECT code, name, ccaa_code, ccaa_name FROM geo_province WHERE code=$1",
            province_code)
        if prov is None:
            return err(f"province {province_code} not found")
        rows = await c.fetch(
            """SELECT co.id AS comarca_id, co.name AS comarca, co.ine_code,
                      m.code AS municipality_code, m.name AS municipality,
                      count(e.entity_ulid) AS entities,
                      count(*) FILTER (WHERE e.kind='compraventa')          AS compraventa,
                      count(*) FILTER (WHERE e.kind='concesionario_oficial') AS oficial,
                      count(*) FILTER (WHERE e.kind='desguace')             AS desguace,
                      count(*) FILTER (WHERE e.kind='plataforma')           AS plataforma
                 FROM entity e
                 JOIN geo_municipality m ON m.code = e.municipality_code
                 JOIN geo_comarca      co ON co.id = m.comarca_id
                WHERE e.province_code = $1 AND e.comarca_id IS NOT NULL
                GROUP BY co.id, co.name, co.ine_code, m.code, m.name
                HAVING count(e.entity_ulid) > 0
                ORDER BY co.ine_code, entities DESC, m.name""",
            province_code)
        comarcas: dict[int, dict[str, Any]] = {}
        prov_total = 0
        for r in rows:
            node = comarcas.setdefault(r["comarca_id"], {
                "comarca_id": r["comarca_id"], "ine_code": r["ine_code"],
                "name": r["comarca"], "entities": 0, "municipalities": []})
            node["entities"] += r["entities"]
            prov_total += r["entities"]
            node["municipalities"].append({
                "municipality_code": r["municipality_code"], "name": r["municipality"],
                "entities": r["entities"], "compraventa": r["compraventa"],
                "oficial": r["oficial"], "desguace": r["desguace"],
                "plataforma": r["plataforma"]})
        # province-only entities (have province, no municipality) reported separately,
        # never mixed into the comarca tree as noise.
        province_only = await c.fetchval(
            "SELECT count(*) FROM entity WHERE province_code=$1 AND municipality_code IS NULL",
            province_code)
        tree = {
            "province": {"code": prov["code"], "name": prov["name"],
                         "ccaa_code": prov["ccaa_code"], "ccaa_name": prov["ccaa_name"]},
            "comarcas": list(comarcas.values()),
            "entities_geo_clean": prov_total,
            "entities_province_only_no_municipality": province_only,
        }
        return ok(tree, comarca_count=len(comarcas), province=province_code)


@app.get("/geo/completeness")
async def geo_completeness() -> JSONResponse:
    """National geo-completeness report: how many entities/vehicles carry the full
    pais+PROVINCIA+COMARCA+ciudad grid vs partial, every number from a live query."""
    async with app.state.pool.acquire() as c:
        e_total = await c.fetchval("SELECT count(*) FROM entity")
        e_full = await c.fetchval(
            "SELECT count(*) FROM entity WHERE province_code IS NOT NULL "
            "AND municipality_code IS NOT NULL AND comarca_id IS NOT NULL")
        e_no_comarca_city = await c.fetchval(
            "SELECT count(*) FROM entity WHERE municipality_code IS NOT NULL AND comarca_id IS NULL")
        e_prov_only = await c.fetchval(
            "SELECT count(*) FROM entity WHERE province_code IS NOT NULL AND municipality_code IS NULL")
        e_no_geo = await c.fetchval("SELECT count(*) FROM entity WHERE province_code IS NULL")
        v_total = await c.fetchval("SELECT count(*) FROM vehicle")
        v_full = await c.fetchval(
            "SELECT count(*) FROM vehicle v JOIN entity e ON e.entity_ulid=v.entity_ulid "
            "WHERE e.province_code IS NOT NULL AND e.municipality_code IS NOT NULL "
            "AND e.comarca_id IS NOT NULL")
        geo = {
            "provinces": await c.fetchval("SELECT count(*) FROM geo_province"),
            "comarcas": await c.fetchval("SELECT count(*) FROM geo_comarca"),
            "municipalities": await c.fetchval("SELECT count(*) FROM geo_municipality"),
            "municipalities_with_comarca": await c.fetchval(
                "SELECT count(*) FROM geo_municipality WHERE comarca_id IS NOT NULL"),
        }
        return ok({
            "geo_grid": geo,
            "entities": {
                "total": e_total, "full_prov_comarca_muni": e_full,
                "municipality_no_comarca_ceuta_melilla": e_no_comarca_city,
                "province_only": e_prov_only, "no_geo": e_no_geo,
                "full_pct": round(100 * e_full / e_total, 2) if e_total else 0,
            },
            "vehicles": {
                "total": v_total, "full_prov_comarca_muni": v_full,
                "full_pct": round(100 * v_full / v_total, 2) if v_total else 0,
            },
        })


@app.get("/platforms/{cdp_code}/inventory")
async def platform_inventory(cdp_code: str) -> JSONResponse:
    """Cars linked to a platform via platform_listing, each WITH its selling-dealer
    attribution (the dual-membership proof: platform edge + singular dealer owner)."""
    async with app.state.pool.acquire() as c:
        prow = await c.fetchrow(
            "SELECT entity_ulid, trade_name, kind FROM entity WHERE cdp_code=$1", cdp_code)
        if prow is None:
            return err(f"platform {cdp_code} not found")
        if prow["kind"] != "plataforma":
            return err(f"entity {cdp_code} is kind '{prow['kind']}', not a plataforma", status=400)
        rows = await c.fetch(
            """SELECT pl.listing_ref, pl.listing_url, pl.platform_price, pl.status AS listing_status,
                      pl.first_seen AS listed_first_seen, pl.last_seen AS listed_last_seen,
                      v.vehicle_ulid, v.make, v.model, v.year, v.km, v.price, v.currency,
                      v.fuel, v.transmission, v.photo_url, v.status AS vehicle_status,
                      d.cdp_code AS dealer_cdp_code, d.trade_name AS dealer_name,
                      d.province_code AS dealer_province, d.municipality_code AS dealer_municipality,
                      d.kind AS dealer_kind
                 FROM platform_listing pl
                 JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
                 JOIN entity d ON d.entity_ulid = v.entity_ulid
                WHERE pl.platform_entity_ulid = $1 AND pl.status = 'listed'
                ORDER BY pl.first_seen DESC""",
            prow["entity_ulid"])
        items = []
        for r in rows:
            d = dict(r)
            d["platform_price"] = float(r["platform_price"]) if r["platform_price"] is not None else None
            d["price"] = float(r["price"]) if r["price"] is not None else None
            d["listed_first_seen"] = str(r["listed_first_seen"])
            d["listed_last_seen"] = str(r["listed_last_seen"])
            items.append(d)
        return ok(items, count=len(items), platform=prow["trade_name"], cdp_code=cdp_code)


@app.get("/vehicles/{vehicle_ulid}/platforms")
async def vehicle_platforms(vehicle_ulid: str) -> JSONResponse:
    """The platforms a car is listed on (its platform_listing edges), plus the car's
    singular owning dealer — proving ownership and membership are distinct axes."""
    async with app.state.pool.acquire() as c:
        vrow = await c.fetchrow(
            """SELECT v.vehicle_ulid, v.make, v.model, v.year, v.deep_link,
                      d.cdp_code AS dealer_cdp_code, d.trade_name AS dealer_name, d.kind AS dealer_kind
                 FROM vehicle v JOIN entity d ON d.entity_ulid = v.entity_ulid
                WHERE v.vehicle_ulid = $1""", vehicle_ulid)
        if vrow is None:
            return err(f"vehicle {vehicle_ulid} not found")
        rows = await c.fetch(
            """SELECT e.cdp_code, e.trade_name, e.website, e.is_tier1,
                      pl.listing_ref, pl.listing_url, pl.platform_price, pl.status,
                      pl.first_seen, pl.last_seen
                 FROM platform_listing pl
                 JOIN entity e ON e.entity_ulid = pl.platform_entity_ulid
                WHERE pl.vehicle_ulid = $1
                ORDER BY pl.first_seen DESC""", vehicle_ulid)
        platforms = []
        for r in rows:
            d = dict(r)
            d["platform_price"] = float(r["platform_price"]) if r["platform_price"] is not None else None
            d["first_seen"] = str(r["first_seen"])
            d["last_seen"] = str(r["last_seen"])
            platforms.append(d)
        vehicle = {"vehicle_ulid": vrow["vehicle_ulid"], "make": vrow["make"],
                   "model": vrow["model"], "year": vrow["year"], "deep_link": vrow["deep_link"],
                   "owning_dealer": {"cdp_code": vrow["dealer_cdp_code"],
                                     "name": vrow["dealer_name"], "kind": vrow["dealer_kind"]}}
        return ok({"vehicle": vehicle, "platforms": platforms}, count=len(platforms))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8090)
