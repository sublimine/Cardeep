"""Shared synthetic-fixture helpers for the market-intelligence (pilar 01) test suite.

Extracted from tests/test_market_compute_stats.py (F1) so F2's metric tests
(tests/test_market_metrics_f2.py) do not duplicate the seeding boilerplate — DRY per
rules/common/coding-style.md ("Extract repeated logic ... when the repetition is real").

SAFETY CONTRACT (same as tests/test_evict.py, tests/test_market_compute_stats.py):
every DB-touching test using these helpers MUST run inside a transaction that is
ALWAYS rolled back via ``_TestRollback`` — never committed. Synthetic makes are
distinctively prefixed (``__CARDEEP_TEST_...__``) so they can never collide with real
inventory even if a rollback were somehow skipped.
"""
from __future__ import annotations

from datetime import datetime

import asyncpg

from pipeline.ids import ulid


class _TestRollback(Exception):
    """Raised to unwind a test transaction — never committed, see module docstring."""


async def vam_verified_run_id(conn: asyncpg.Connection) -> str:
    row = await conn.fetchrow(
        "SELECT cluster_run_id FROM vehicle_cluster_run WHERE vam_verified = TRUE "
        "ORDER BY run_at DESC LIMIT 1"
    )
    assert row is not None, "no vam_verified vehicle_cluster_run exists — F0 precondition violated"
    return row["cluster_run_id"]


async def seed_vehicle(
    conn: asyncpg.Connection,
    cluster_run_id: str,
    *,
    make: str,
    model: str,
    fuel: str,
    year: int,
    province_code: str,
    price: float | None,
    status: str = "available",
    first_seen: datetime | None = None,
) -> str:
    """Insert one synthetic entity+vehicle+vehicle_cluster row (self-canonical).

    Returns the vehicle_ulid. Passes servable_vehicle (when status='available') and
    resolves via v_canonical_vehicle (attached to the real vam_verified cluster run).
    """
    entity_ulid = ulid()
    vehicle_ulid = ulid()
    cdp_code = f"CDP-ES-{province_code}-TST{vehicle_ulid[-8:]}"
    await conn.execute(
        "INSERT INTO entity (entity_ulid, cdp_code, kind, province_code, status) "
        "VALUES ($1, $2, 'compraventa'::entity_kind, $3, 'unverified'::entity_status)",
        entity_ulid, cdp_code, province_code,
    )
    if first_seen is not None:
        await conn.execute(
            "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, make, model, year, "
            "fuel, price, status, first_seen, last_seen) "
            "VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$10)",
            vehicle_ulid, entity_ulid, f"https://example.test/{vehicle_ulid}",
            make, model, year, fuel, price, status, first_seen,
        )
    else:
        await conn.execute(
            "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, make, model, year, "
            "fuel, price, status) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)",
            vehicle_ulid, entity_ulid, f"https://example.test/{vehicle_ulid}",
            make, model, year, fuel, price, status,
        )
    await conn.execute(
        "INSERT INTO vehicle_cluster (cluster_run_id, vehicle_ulid, canonical_vehicle_ulid, "
        "match_signal, cluster_size) VALUES ($1,$2,$2,'test',1)",
        cluster_run_id, vehicle_ulid,
    )
    return vehicle_ulid


async def seed_event(
    conn: asyncpg.Connection,
    *,
    vehicle_ulid: str,
    entity_ulid: str,
    event_type: str,
    old_value: dict | None,
    new_value: dict | None,
    observed_at: datetime,
) -> None:
    """Insert one synthetic vehicle_event row with an explicit observed_at (test control
    over exact day-deltas / early-vs-late windowing — production code never backdates)."""
    import json
    await conn.execute(
        "INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type, "
        "old_value, new_value, observed_at) VALUES ($1,$2,$3,$4,$5::jsonb,$6::jsonb,$7)",
        ulid(), vehicle_ulid, entity_ulid, event_type,
        json.dumps(old_value) if old_value is not None else None,
        json.dumps(new_value) if new_value is not None else None,
        observed_at,
    )


async def entity_ulid_of(conn: asyncpg.Connection, vehicle_ulid: str) -> str:
    row = await conn.fetchrow("SELECT entity_ulid FROM vehicle WHERE vehicle_ulid = $1", vehicle_ulid)
    assert row is not None
    return row["entity_ulid"]


async def seed_platform_entity(conn: asyncpg.Connection, *, province_code: str = "28") -> str:
    """Insert one synthetic 'plataforma' entity, return its entity_ulid."""
    entity_ulid = ulid()
    cdp_code = f"CDP-ES-{province_code}-PLT{entity_ulid[-8:]}"
    await conn.execute(
        "INSERT INTO entity (entity_ulid, cdp_code, kind, province_code, status) "
        "VALUES ($1, $2, 'plataforma'::entity_kind, $3, 'unverified'::entity_status)",
        entity_ulid, cdp_code, province_code,
    )
    return entity_ulid


async def seed_platform_listing(
    conn: asyncpg.Connection, *, vehicle_ulid: str, platform_entity_ulid: str, listing_url: str
) -> None:
    await conn.execute(
        "INSERT INTO platform_listing (vehicle_ulid, platform_entity_ulid, listing_url) "
        "VALUES ($1,$2,$3)",
        vehicle_ulid, platform_entity_ulid, listing_url,
    )
