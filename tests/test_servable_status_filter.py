"""Invariant tests for servable_vehicle as the TRUE live-served surface (migration 0045).

servable_vehicle is the publish-gate view migration 0031 declares the API must read through:
"the instant a quarantining item opens, the subject vanishes from every served surface —
mechanically, not by promise." Before 0045 the view guarded price + quarantine but NOT status, so
it contained 7,721 'gone' (sold/withdrawn) cars — a baja served as live stock. 0045 adds the
status='available' guard and the routers now read through the view (entities/platforms/ops), so all
three guards (status, price, quarantine) apply at one source of truth.

These tests pin that contract against the live DB:
  - no 'gone' car is servable (the baja stays in /delta + /history, never live inventory);
  - no non-positive price is servable (junk);
  - every servable row is status='available' and a subset of the available universe;
  - a quarantining gestion_item makes its subject vanish from servable_vehicle, mechanically
    (proven in a rolled-back transaction so the live data is untouched).
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


def _scalar(sql: str):
    async def _go():
        import asyncpg
        conn = await asyncpg.connect(DSN)
        try:
            return await conn.fetchval(sql)
        finally:
            await conn.close()
    return asyncio.run(_go())


@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestServableStatusFilter:
    def test_no_gone_car_is_servable(self) -> None:
        assert _scalar("SELECT count(*) FROM servable_vehicle WHERE status <> 'available'") == 0

    def test_no_nonpositive_price_is_servable(self) -> None:
        assert _scalar("SELECT count(*) FROM servable_vehicle WHERE price <= 0") == 0

    def test_servable_is_subset_of_available(self) -> None:
        servable = _scalar("SELECT count(*) FROM servable_vehicle")
        available = _scalar("SELECT count(*) FROM vehicle WHERE status='available'")
        # servable <= available (it removes price<=0 and quarantined from the available set);
        # it must never EXCEED available — that was the bug (gone cars inflated it past available).
        assert servable <= available, f"servable {servable} must not exceed available {available}"

    def test_quarantine_hides_subject_from_servable_mechanically(self) -> None:
        """Open a quarantining gestion_item -> the car vanishes from servable_vehicle. Rolled back."""
        async def _go() -> tuple[int, int, int]:
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                target = await conn.fetchval("SELECT vehicle_ulid FROM servable_vehicle LIMIT 1")
                assert target is not None, "no servable vehicle to test with"
                tr = conn.transaction()
                await tr.start()
                try:
                    before = await conn.fetchval(
                        "SELECT count(*) FROM servable_vehicle WHERE vehicle_ulid=$1", target)
                    await conn.execute(
                        "INSERT INTO gestion_item "
                        "(detector, subject_type, subject_key, severity, measured, lane, "
                        " quarantines, dedupe_key) "
                        "VALUES ('coherence_test','vehicle',$1,'critical','{}'::jsonb,'QUARANTINE',"
                        " true,'coherence_test:'||$1)",
                        target)
                    after = await conn.fetchval(
                        "SELECT count(*) FROM servable_vehicle WHERE vehicle_ulid=$1", target)
                finally:
                    await tr.rollback()
                restored = await conn.fetchval(
                    "SELECT count(*) FROM servable_vehicle WHERE vehicle_ulid=$1", target)
                return before, after, restored
            finally:
                await conn.close()

        before, after, restored = asyncio.run(_go())
        assert before == 1, "target should be servable before quarantine"
        assert after == 0, "quarantined car must vanish from servable_vehicle"
        assert restored == 1, "rollback must restore the car (live data untouched)"


@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestServableEntity:
    """servable_entity is the dealer-listing publish-gate (0031). The /geo listing endpoints now
    read through it (not raw `entity`), so a quarantined dealer vanishes from province/municipality/
    tree listings — the same 0031 invariant the servable_vehicle fix restored for inventory."""

    def test_servable_entity_subset_of_entity(self) -> None:
        servable = _scalar("SELECT count(*) FROM servable_entity")
        total = _scalar("SELECT count(*) FROM entity")
        # servable_entity removes only entities with an open quarantine -> never exceeds entity.
        assert servable <= total, f"servable_entity {servable} must not exceed entity {total}"

    def test_quarantine_hides_dealer_from_servable_entity_mechanically(self) -> None:
        """Open a quarantining gestion_item (keyed by cdp_code) -> the dealer vanishes. Rolled back."""
        async def _go() -> tuple[int, int, int]:
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                cdp = await conn.fetchval(
                    "SELECT cdp_code FROM servable_entity WHERE kind <> 'particular' "
                    "AND cdp_code IS NOT NULL LIMIT 1")
                assert cdp is not None, "no servable dealer to test with"
                tr = conn.transaction()
                await tr.start()
                try:
                    before = await conn.fetchval(
                        "SELECT count(*) FROM servable_entity WHERE cdp_code=$1", cdp)
                    await conn.execute(
                        "INSERT INTO gestion_item "
                        "(detector, subject_type, subject_key, severity, measured, lane, "
                        " quarantines, dedupe_key) "
                        "VALUES ('coherence_test','entity',$1,'critical','{}'::jsonb,'QUARANTINE',"
                        " true,'coherence_test_entity:'||$1)",
                        cdp)
                    after = await conn.fetchval(
                        "SELECT count(*) FROM servable_entity WHERE cdp_code=$1", cdp)
                finally:
                    await tr.rollback()
                restored = await conn.fetchval(
                    "SELECT count(*) FROM servable_entity WHERE cdp_code=$1", cdp)
                return before, after, restored
            finally:
                await conn.close()

        before, after, restored = asyncio.run(_go())
        assert before == 1, "dealer should be servable before quarantine"
        assert after == 0, "quarantined dealer must vanish from servable_entity"
        assert restored == 1, "rollback must restore the dealer (live data untouched)"
