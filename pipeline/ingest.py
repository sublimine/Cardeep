"""FASE 4 — API/INGEST with the live delta engine.

Upserts the dealer entity and reconciles its inventory against the harvest:
  NEW           -> insert vehicle + event
  GONE          -> available vehicle no longer harvested -> status=gone + event
  PRICE_CHANGE  -> price differs -> update price + event
  PHOTO_CHANGE  -> photo_url differs -> update + event
  KM_CHANGE     -> km differs -> update + event
Unchanged rows only refresh last_seen (never an UPDATE of non-mutated data).
Closes with a VAM count quorum (declared == available in DB).
"""
from __future__ import annotations

import json

import asyncpg

from pipeline.ids import ulid
from pipeline.sources.autoscout24 import DealerHarvest, RECIPE_VERSION
from pipeline.geo import GeoResolver
from pipeline.verify import record_count_verdict
from services.api.codes import cdp_code


async def _event(conn, vulid, eulid, etype, old, new):
    await conn.execute(
        "INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type, old_value, new_value) "
        "VALUES ($1,$2,$3,$4,$5::jsonb,$6::jsonb)",
        ulid(), vulid, eulid, etype,
        json.dumps(old) if old is not None else None,
        json.dumps(new) if new is not None else None)


async def ingest_dealer(conn: asyncpg.Connection, geo: GeoResolver, harvest: DealerHarvest,
                        source_key: str = "as24") -> dict:
    d = harvest.dealer
    if d is None or not d.province_code:
        return {"error": "no dealer / province", "ingested": 0}

    muni = geo.municipality_code(d.province_code, d.city)
    code = cdp_code(province_code=d.province_code, domain=d.website, name=d.company_name,
                    municipality_code=muni, address=d.street)
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, municipality_code, address, postcode, website, is_tier1,
               status, recipe_version, first_discovered_source, last_seen)
           VALUES ($1,$2,'concesionario_oficial',$3,$3,$4,$5,$6,$7,$8,FALSE,'active',$9,$10, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(), recipe_version = EXCLUDED.recipe_version""",
        eulid, code, d.company_name, d.province_code, muni, d.street, d.zip, d.website,
        RECIPE_VERSION, source_key)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, source_key, d.source_dealer_id)

    # current snapshot in DB for this entity
    existing = {r["deep_link"]: r for r in await conn.fetch(
        "SELECT vehicle_ulid, deep_link, price, km, photo_url, status FROM vehicle WHERE entity_ulid=$1",
        eulid)}
    harvested_links = set()
    counts = {"new": 0, "price_change": 0, "photo_change": 0, "km_change": 0, "gone": 0, "unchanged": 0}

    for v in harvest.vehicles:
        harvested_links.add(v.deep_link)
        row = existing.get(v.deep_link)
        if row is None:
            vulid = ulid()
            await conn.execute(
                """INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model,
                       year, km, price, fuel, transmission, photo_url, vin_ref, recipe_version, status)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,'available')""",
                vulid, eulid, v.deep_link, v.title, v.make, v.model, v.year, v.km, v.price,
                v.fuel, v.transmission, v.photo_url, v.vin_ref, RECIPE_VERSION)
            await _event(conn, vulid, eulid, "NEW", None,
                         {"price": v.price, "title": v.title})
            counts["new"] += 1
        else:
            vulid = row["vehicle_ulid"]
            changed = False
            if v.price is not None and row["price"] is not None and float(v.price) != float(row["price"]):
                await conn.execute("UPDATE vehicle SET price=$1 WHERE vehicle_ulid=$2", v.price, vulid)
                await _event(conn, vulid, eulid, "PRICE_CHANGE", {"price": float(row["price"])}, {"price": v.price})
                counts["price_change"] += 1; changed = True
            if v.km is not None and row["km"] is not None and int(v.km) != int(row["km"]):
                await conn.execute("UPDATE vehicle SET km=$1 WHERE vehicle_ulid=$2", v.km, vulid)
                await _event(conn, vulid, eulid, "KM_CHANGE", {"km": row["km"]}, {"km": v.km})
                counts["km_change"] += 1; changed = True
            if v.photo_url and v.photo_url != row["photo_url"]:
                await conn.execute("UPDATE vehicle SET photo_url=$1 WHERE vehicle_ulid=$2", v.photo_url, vulid)
                await _event(conn, vulid, eulid, "PHOTO_CHANGE", {"photo": row["photo_url"]}, {"photo": v.photo_url})
                counts["photo_change"] += 1; changed = True
            if row["status"] != "available":
                await conn.execute("UPDATE vehicle SET status='available' WHERE vehicle_ulid=$1", vulid)
                changed = True
            await conn.execute("UPDATE vehicle SET last_seen=now() WHERE vehicle_ulid=$1", vulid)
            counts["unchanged"] += int(not changed)

    # GONE: available rows in DB not in this harvest
    for link, row in existing.items():
        if link not in harvested_links and row["status"] == "available":
            await conn.execute("UPDATE vehicle SET status='gone' WHERE vehicle_ulid=$1", row["vehicle_ulid"])
            await _event(conn, row["vehicle_ulid"], eulid, "GONE", {"price": float(row["price"]) if row["price"] else None}, None)
            counts["gone"] += 1

    available = await conn.fetchval(
        "SELECT count(*) FROM vehicle WHERE entity_ulid=$1 AND status='available'", eulid)
    verdict = await record_count_verdict(
        conn, subject_type="entity_inventory", subject_key=code,
        claim="available inventory == source declared count",
        paths={"db_available": available, "harvested": len(harvest.vehicles),
               "source_declared": harvest.declared_count},
        tolerance=0.0)
    return {"cdp_code": code, "entity_ulid": eulid, "available": available,
            "declared": harvest.declared_count, "verdict": verdict, **counts}
