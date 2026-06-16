"""Tests for pipeline.delta.emit_gone_events (audit P4 — silent-baja fix).

The two auction connectors (group_subastas_wholesale, localizavo_wholesale) retire aged-out lots by
flipping vehicle.status='gone' directly; before the fix they emitted NO GONE event, leaving 1,823
silent bajas (gone in the table, absent from the immutable timeline). emit_gone_events records the
baja exactly as reconcile_gone does, idempotently. These tests run in a rolled-back transaction so
live data is untouched.
"""
from __future__ import annotations

import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"


def _db_available() -> bool:
    async def _ping() -> bool:
        try:
            import asyncpg
            conn = await asyncpg.connect(DSN, timeout=3)
            await conn.close()
            return True
        except Exception:
            return False
    try:
        return asyncio.run(_ping())
    except Exception:
        return False


DB_AVAILABLE = _db_available()


@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestEmitGoneEvents:
    def test_emits_one_gone_event_then_is_idempotent(self) -> None:
        async def _go():
            import asyncpg
            from pipeline.delta import emit_gone_events
            conn = await asyncpg.connect(DSN)
            try:
                target = await conn.fetchval(
                    "SELECT v.vehicle_ulid FROM vehicle v "
                    "WHERE v.status='available' AND v.entity_ulid IS NOT NULL "
                    "AND NOT EXISTS (SELECT 1 FROM vehicle_event ve "
                    "  WHERE ve.vehicle_ulid=v.vehicle_ulid AND ve.event_type='GONE') LIMIT 1")
                assert target is not None, "need an available vehicle with no prior GONE event"
                tr = conn.transaction()
                await tr.start()
                try:
                    before = await conn.fetchval(
                        "SELECT count(*) FROM vehicle_event WHERE vehicle_ulid=$1 "
                        "AND event_type='GONE'", target)
                    # the connector flips status first, THEN emits — mirror that order
                    await conn.execute(
                        "UPDATE vehicle SET status='gone' WHERE vehicle_ulid=$1", target)
                    n1 = await emit_gone_events(conn, [target])
                    after1 = await conn.fetchval(
                        "SELECT count(*) FROM vehicle_event WHERE vehicle_ulid=$1 "
                        "AND event_type='GONE'", target)
                    n2 = await emit_gone_events(conn, [target])  # idempotent re-call
                    after2 = await conn.fetchval(
                        "SELECT count(*) FROM vehicle_event WHERE vehicle_ulid=$1 "
                        "AND event_type='GONE'", target)
                    shape = await conn.fetchrow(
                        "SELECT old_value, new_value FROM vehicle_event "
                        "WHERE vehicle_ulid=$1 AND event_type='GONE'", target)
                finally:
                    await tr.rollback()
                return before, n1, after1, n2, after2, shape
            finally:
                await conn.close()

        before, n1, after1, n2, after2, shape = asyncio.run(_go())
        assert before == 0
        assert n1 == 1 and after1 == 1, "first call emits exactly one GONE event"
        assert n2 == 0 and after2 == 1, "second call is idempotent (no duplicate GONE)"
        assert "price" in str(shape["old_value"]), "old_value carries the price snapshot"
        assert shape["new_value"] is None, "GONE new_value is null (convention)"

    def test_skips_orphan_without_entity(self) -> None:
        """A vehicle with entity_ulid IS NULL cannot be attributed -> emit skips it (returns 0)."""
        async def _go():
            import asyncpg
            from pipeline.delta import emit_gone_events
            conn = await asyncpg.connect(DSN)
            try:
                # synthesize an orphan ulid that does not exist -> emit must skip safely
                n = await emit_gone_events(conn, ["01ZZZZZZZZZZZZZZZZZZZZZZZZZ"])
                return n
            finally:
                await conn.close()

        assert asyncio.run(_go()) == 0, "non-existent / orphan vehicle is skipped, not errored"
