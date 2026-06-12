"""Seed one real pilot entity + vehicle + delta event to prove the F2 backbone.

Pilot: ZONAUTO SUR S.L. — Hyundai dealer, Pinto (Madrid), from the AMDA Madrid
census source (verified live 2026-06-12). Demonstrates the full data column:
entity (with cdp_code + geo) -> vehicle -> append-only NEW event.

Idempotent: ON CONFLICT DO NOTHING on natural keys.

Usage: python -m scripts.seed_pilot
"""
from __future__ import annotations

import asyncio
import os
import secrets
import time

import asyncpg

from services.api.codes import cdp_code

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def ulid() -> str:
    """Minimal time-ordered ULID-like id (48-bit ms time + 80-bit randomness)."""
    ts = int(time.time() * 1000)
    rnd = int.from_bytes(secrets.token_bytes(10), "big")
    num = (ts << 80) | rnd
    out = []
    for _ in range(26):
        out.append(_CROCKFORD[num & 0x1F])
        num >>= 5
    return "".join(reversed(out))


async def main() -> None:
    code = cdp_code(province_code="28", domain="zonauto.es")
    eulid = ulid()
    conn = await asyncpg.connect(DSN)
    try:
        existing = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
        if existing:
            eulid = existing
            print(f"entity already present: {code} ({eulid})")
        else:
            await conn.execute(
                """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
                       province_code, municipality_code, address, postcode, phone, email,
                       website, website_waf, is_tier1, status, first_discovered_source)
                   VALUES ($1,$2,'concesionario_oficial','ZONAUTO SUR S.L.','Zonauto Sur',
                       '28','28113','C. Sestao 3, Pinto','28320','916910808',
                       'ventas.zonauto@redhyundai.com','zonauto.es','none',FALSE,'active','amda_madrid')""",
                eulid, code)
            await conn.execute(
                "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES "
                "($1,'amda_madrid','https://www.amdamadrid.com/concesionarios-asociados/') "
                "ON CONFLICT DO NOTHING", eulid)
            print(f"inserted entity: {code} ({eulid})")

        veh_exists = await conn.fetchval(
            "SELECT vehicle_ulid FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2",
            eulid, "https://zonauto.es/hyundai-tucson-2022-ref001")
        if not veh_exists:
            vulid = ulid()
            await conn.execute(
                """INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model,
                       year, km, price, fuel, transmission, status)
                   VALUES ($1,$2,'https://zonauto.es/hyundai-tucson-2022-ref001',
                       'Hyundai Tucson 1.6 TGDi Maxx','Hyundai','Tucson',2022,38500,23900,
                       'Gasolina','Manual','available')""",
                vulid, eulid)
            await conn.execute(
                """INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type, new_value)
                   VALUES ($1,$2,$3,'NEW', $4::jsonb)""",
                ulid(), vulid, eulid, '{"price": 23900, "title": "Hyundai Tucson 1.6 TGDi Maxx"}')
            print(f"inserted vehicle + NEW event ({vulid})")
        else:
            print("vehicle already present")

        print("cdp_code:", code)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
