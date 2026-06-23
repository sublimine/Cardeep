"""Seed a TINY synthetic census fixture for the CI `db-tests` job.

Why: the db-tests job runs against an ephemeral, migrated, geo-seeded Postgres with NO census, so the
census-dependent tests (which read real entities/vehicles) fail. This inserts a SMALL, deterministic,
idempotent fixture so a first batch of those tests can run in CI. It is ADDITIVE and ON CONFLICT DO
NOTHING — re-running is a no-op, and it must never break the tests that already pass on the empty DB.

Scope (batch A): a handful of active compraventa dealers in province 28 / municipality 28079 (both
present from the geo seed), each with an entity_source, plus a few available vehicles. Enough for
test_evict (reads one real dealer), test_entity_muni_province_invariant (needs one entity with a
municipality), and test_emit_gone_events (needs an available vehicle with no prior GONE event).

IDs use the Crockford-26 / cdp_code formats the schema + G1 validator require. Run AFTER `migrate up`
and the geo seed. Reads CARDEEP_DSN (the CI job points it at the ephemeral 127.0.0.1:5433).
Usage: python -m scripts.seed_ci_fixture
"""
from __future__ import annotations

import asyncio
import os

import asyncpg

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# Crockford-safe (no I/L/O/U) fixed identifiers — deterministic so re-runs are idempotent.
_PROV = "28"
_MUNI = "28079"
_N_DEALERS = 25  # >=20 so province-28 pagination (OLA 2) has two distinct pages later, too
_N_VEHICLES = 25


def _entity_ulid(i: int) -> str:
    return f"FXTRE{str(i).zfill(21)}"  # 5 + 21 = 26 Crockford chars


def _cdp(i: int) -> str:
    return f"CDP-ES-{_PROV}-FXTRE{str(i).zfill(3)}"  # suffix FXTRE001 = 8 Crockford chars


def _vehicle_ulid(i: int) -> str:
    return f"FXTVH{str(i).zfill(21)}"


async def main() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        dealers = [
            (
                _entity_ulid(i), _cdp(i), "compraventa", f"CI Fixture Dealer {i}",
                _PROV, _MUNI, "active", True,
            )
            for i in range(1, _N_DEALERS + 1)
        ]
        await conn.executemany(
            "INSERT INTO entity (entity_ulid, cdp_code, kind, trade_name, province_code, "
            "municipality_code, status, sells_cars) "
            "VALUES ($1,$2,$3::entity_kind,$4,$5,$6,$7::entity_status,$8) "
            "ON CONFLICT (entity_ulid) DO NOTHING",
            dealers,
        )
        await conn.executemany(
            "INSERT INTO entity_source (entity_ulid, source_key, source_ref) "
            "VALUES ($1, 'ci_fixture', 'seed') ON CONFLICT (entity_ulid, source_key) DO NOTHING",
            [(_entity_ulid(i),) for i in range(1, _N_DEALERS + 1)],
        )
        # Available vehicles under the FIRST dealer (servable: status='available', 0<price<=5M).
        first = _entity_ulid(1)
        vehicles = [
            (_vehicle_ulid(i), first, f"https://ci.fixture/veh/{i}", f"CI Car {i}", 12000 + i * 100)
            for i in range(1, _N_VEHICLES + 1)
        ]
        await conn.executemany(
            "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, price, status) "
            "VALUES ($1,$2,$3,$4,$5,'available') ON CONFLICT (vehicle_ulid) DO NOTHING",
            vehicles,
        )
        ne = await conn.fetchval("SELECT count(*) FROM entity WHERE cdp_code LIKE 'CDP-ES-28-FXTRE%'")
        nv = await conn.fetchval("SELECT count(*) FROM vehicle WHERE entity_ulid = $1", first)
        print(f"ci-fixture seeded: dealers={ne} vehicles_under_first={nv}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
