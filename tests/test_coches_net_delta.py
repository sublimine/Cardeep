"""Live rolled-back test for the shared A4 delta emitter (audit P2 SU-A4 phase 1).

Verifies pipeline.delta.emit_change_deltas — the connector-agnostic helper wired into the high-volume
landings (coches.net, wallapop). A re-seen vehicle with a changed price/km/photo emits the 3 change
events AND the served row is refreshed; an unchanged re-seen vehicle emits nothing (no false positives).
Uses a real vehicle (rolled back) so it exercises the real SQL + constraints. SKIP if no DB.
"""
from __future__ import annotations

import asyncio
from types import SimpleNamespace

import asyncpg
import pytest

from pipeline.delta import emit_change_deltas

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"


def _db_ok() -> bool:
    async def _p() -> bool:
        try:
            c = await asyncpg.connect(DSN, timeout=3)
            await c.close()
            return True
        except Exception:
            return False
    try:
        return asyncio.run(_p())
    except Exception:
        return False


SKIP = pytest.mark.skipif(not _db_ok(), reason="cardeep-pg not reachable")


def _veh(*, price, km, photo_url):
    # Minimal stand-in for a scraped vehicle: emit_change_deltas/diff_vehicle read only these attrs.
    return SimpleNamespace(price=price, km=km, photo_url=photo_url)


async def _probe_vehicle(c):
    return await c.fetchrow(
        "SELECT v.vehicle_ulid, v.entity_ulid, v.deep_link, v.price, v.km, v.photo_url "
        "FROM vehicle v JOIN entity_source es ON es.entity_ulid=v.entity_ulid "
        "WHERE es.source_key='coches_net_wholesale' AND v.price IS NOT NULL LIMIT 1")


@SKIP
def test_reseen_vehicle_emits_changes_and_refreshes_row():
    async def body():
        c = await asyncpg.connect(DSN)
        tr = c.transaction()
        await tr.start()
        try:
            row = await _probe_vehicle(c)
            if row is None:
                pytest.skip("no coches_net vehicle with a price to probe")
            key = (row["entity_ulid"], row["deep_link"])
            snap = {"vehicle_ulid": row["vehicle_ulid"], "price": row["price"],
                    "km": row["km"], "photo_url": row["photo_url"]}
            new_price = float(row["price"]) + 1234.0
            new_km = (int(row["km"]) if row["km"] is not None else 0) + 777
            new_photo = "https://test/CHANGED.jpg"
            new_vehicles = {key: _veh(price=new_price, km=new_km, photo_url=new_photo)}

            counts = await emit_change_deltas(c, {key: snap}, new_vehicles, [key])
            assert counts == {"PRICE_CHANGE": 1, "KM_CHANGE": 1, "PHOTO_CHANGE": 1}

            evs = {r["event_type"] for r in await c.fetch(
                "SELECT event_type FROM vehicle_event WHERE vehicle_ulid=$1 "
                "AND event_type IN ('PRICE_CHANGE','KM_CHANGE','PHOTO_CHANGE')", row["vehicle_ulid"])}
            assert {"PRICE_CHANGE", "KM_CHANGE", "PHOTO_CHANGE"} <= evs
            refreshed = await c.fetchrow(
                "SELECT price, km, photo_url FROM vehicle WHERE vehicle_ulid=$1", row["vehicle_ulid"])
            assert float(refreshed["price"]) == new_price
            assert int(refreshed["km"]) == new_km
            assert refreshed["photo_url"] == new_photo
        finally:
            await tr.rollback()
            await c.close()
    asyncio.run(body())


@SKIP
def test_unchanged_vehicle_emits_nothing():
    async def body():
        c = await asyncpg.connect(DSN)
        tr = c.transaction()
        await tr.start()
        try:
            row = await _probe_vehicle(c)
            if row is None:
                pytest.skip("no coches_net vehicle to probe")
            key = (row["entity_ulid"], row["deep_link"])
            snap = {"vehicle_ulid": row["vehicle_ulid"], "price": row["price"],
                    "km": row["km"], "photo_url": row["photo_url"]}
            new_vehicles = {key: _veh(
                price=float(row["price"]) if row["price"] is not None else None,
                km=int(row["km"]) if row["km"] is not None else None,
                photo_url=row["photo_url"])}
            before = await c.fetchval(
                "SELECT count(*) FROM vehicle_event WHERE vehicle_ulid=$1", row["vehicle_ulid"])
            counts = await emit_change_deltas(c, {key: snap}, new_vehicles, [key])
            assert counts == {"PRICE_CHANGE": 0, "KM_CHANGE": 0, "PHOTO_CHANGE": 0}
            after = await c.fetchval(
                "SELECT count(*) FROM vehicle_event WHERE vehicle_ulid=$1", row["vehicle_ulid"])
            assert after == before
        finally:
            await tr.rollback()
            await c.close()
    asyncio.run(body())
