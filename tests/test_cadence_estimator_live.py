"""F4 — estimate_change_rate()/apply_cadence_estimate() against a REAL live DB connection.

vehicle_event is append-only at the DB level (a trigger REJECTS DELETE — confirmed live:
asyncpg.exceptions.RestrictViolationError: "vehicle_event is append-only: DELETE
forbidden"). So, like tests/test_resilience_loop.py and test_autorepair_loop.py, this uses
a single aborted transaction (`async with conn.transaction(): ... raise _Rollback`): all
synthetic INSERTs (source_health, entity, entity_source, vehicle, vehicle_event,
harvest_run) and the estimator's own reads/writes happen on the SAME connection inside the
SAME uncommitted transaction (read-your-own-writes), then the whole thing rolls back —
zero persistent rows, and the append-only constraint is never even invoked.
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
SOURCE_KEY = "__f4_cadence_live_test__"
# entity/vehicle ulid columns carry a CHECK constraint ('^[0-9A-HJKMNP-TV-Z]{26}$', migration
# 0006) — Crockford-base32-shaped, 26 chars. Fixed, recognizable test fixtures (not real
# ULIDs, just shape-valid ones); never persisted since the whole test rolls back.
# NOTE: a v1 of this test (since fixed) briefly ran with a committing (non-transactional)
# connection and left a permanent residue at ENTITY_ULID/VEHICLE_ULID = ...TESTENT7Y.../
# ...TESTVEH7C3... (vehicle_event's append-only DELETE guard, migration 0035, made it
# undeletable; the synthetic vehicle was corrected to status='gone' so it is excluded from
# every real product_stats/dealers query — see the F3/F4 delivery report). This test now
# uses a DIFFERENT fixture id (below) and the aborted-transaction pattern exclusively, so it
# can never repeat that mistake.
ENTITY_ULID = "0F4CADENC3TESTENT7Y0000002"
VEHICLE_ULID = "0F4CADENC3TESTVEH7C3000002"


def _db_available() -> bool:
    try:
        return asyncio.run(_ping())
    except Exception:
        return False


async def _ping() -> bool:
    try:
        import asyncpg
        conn = await asyncpg.connect(DSN, timeout=3)
        await conn.close()
        return True
    except Exception:
        return False


DB_AVAILABLE = _db_available()


class _Rollback(Exception):
    """Sentinel: forces the transaction to abort cleanly at test end."""


@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestEstimateChangeRateLiveDB:
    def test_estimator_reads_real_visit_and_change_history(self) -> None:
        asyncio.run(self._run())

    async def _run(self) -> None:
        import asyncpg

        from pipeline.ops.cadence_estimator import apply_cadence_estimate, estimate_change_rate

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                now = datetime.now(timezone.utc)
                window_start = now - timedelta(hours=24 * 10)

                await conn.execute(
                    "INSERT INTO source_health (source_key, harvest_interval_hours, "
                    "last_ok, consecutive_fails, country_code) "
                    "VALUES ($1, 24, $2, 0, 'ES')",
                    SOURCE_KEY, now,
                )
                await conn.execute(
                    "INSERT INTO entity (entity_ulid, cdp_code, kind) VALUES ($1, $2, 'garaje')",
                    ENTITY_ULID, "CDP-ES-TEST-F4CADENCE-002",
                )
                await conn.execute(
                    "INSERT INTO entity_source (entity_ulid, source_key) VALUES ($1, $2)",
                    ENTITY_ULID, SOURCE_KEY,
                )
                await conn.execute(
                    "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link) VALUES ($1, $2, $3)",
                    VEHICLE_ULID, ENTITY_ULID, "https://example.test/f4-cadence-vehicle",
                )

                # 10 daily visits (harvest_run). Only visits at day-index 0,1,2 have a
                # matching vehicle_event within the same 24h bucket — the other 7 are
                # "visited, unchanged".
                for day in range(10):
                    started_at = window_start + timedelta(hours=24 * day, minutes=5)
                    await conn.execute(
                        "INSERT INTO harvest_run (source_key, started_at, finished_at, ok, rows) "
                        "VALUES ($1, $2, $2, true, 1)",
                        SOURCE_KEY, started_at,
                    )

                for day in (0, 1, 2):
                    await conn.execute(
                        "INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, "
                        "event_type, observed_at) VALUES ($1, $2, $3, 'PRICE_CHANGE', $4)",
                        f"__f4_evt_002_{day}__", VEHICLE_ULID, ENTITY_ULID,
                        window_start + timedelta(hours=24 * day, minutes=10),
                    )

                est = await estimate_change_rate(
                    conn, SOURCE_KEY, lookback_days=10, min_windows=5, now=now,
                )
                assert est is not None, "10 visited daily windows must clear MIN_WINDOWS=5"
                assert est.n_visited == 10
                assert est.n_unchanged == 7, "days 0,1,2 changed; days 3..9 (7 days) unchanged"
                assert est.lambda_per_hour > 0
                assert 24 <= est.computed_interval_hours <= 2160

                await apply_cadence_estimate(conn, est)

                row = await conn.fetchrow(
                    "SELECT observed_change_rate, computed_interval_hours, cadence_computed_at, "
                    "cadence_mode FROM source_health WHERE source_key=$1",
                    SOURCE_KEY,
                )
                assert row["observed_change_rate"] == pytest.approx(est.lambda_per_hour)
                assert row["computed_interval_hours"] == est.computed_interval_hours
                assert row["cadence_computed_at"] is not None
                assert row["cadence_mode"] == "static", (
                    "apply_cadence_estimate must NEVER flip cadence_mode — that is a "
                    "deliberate, separate operator rollout step"
                )

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_insufficient_sample_returns_none(self) -> None:
        asyncio.run(self._run_insufficient())

    async def _run_insufficient(self) -> None:
        import asyncpg

        from pipeline.ops.cadence_estimator import estimate_change_rate

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                now = datetime.now(timezone.utc)
                await conn.execute(
                    "INSERT INTO source_health (source_key, harvest_interval_hours, "
                    "last_ok, consecutive_fails, country_code) "
                    "VALUES ($1, 24, $2, 0, 'ES')",
                    SOURCE_KEY, now,
                )
                # Only 2 visits — below MIN_WINDOWS=5.
                for day in range(2):
                    await conn.execute(
                        "INSERT INTO harvest_run (source_key, started_at, finished_at, ok, rows) "
                        "VALUES ($1, $2, $2, true, 1)",
                        SOURCE_KEY, now - timedelta(hours=24 * day),
                    )
                est = await estimate_change_rate(
                    conn, SOURCE_KEY, lookback_days=10, min_windows=5, now=now,
                )
                assert est is None

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()
