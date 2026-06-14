"""B3.2 — unit tests: resolve_alerts wired into record_run success path.

Strategy: use an asyncpg pool against the real DB running in Docker, but inside an
aborted transaction so NO persistent writes occur — the alert table is left intact.

The test:
1. Inserts a synthetic open alert for 'test_src_b32:scrape'.
2. Inserts a synthetic open alert for a DIFFERENT source 'other_src:scrape'
   (must NOT be resolved).
3. Inserts a synthetic open alert for the SAME source but a DIFFERENT phase
   'test_src_b32:discover' (must NOT be resolved by a scrape-phase record_run).
4. Calls record_run(ok=True, phase='scrape') for 'test_src_b32'.
5. Asserts the scrape alert is resolved (resolved_at IS NOT NULL inside the txn).
6. Asserts the discover alert and other_src alert are still open.
7. Rolls back — no persistent DB mutation.

All assertions happen within the aborted transaction; the DB is read-only post-test.
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# DB connectivity guard — skip if cardeep-pg is not reachable
# ---------------------------------------------------------------------------
DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"


def _db_available() -> bool:
    try:
        import asyncpg  # noqa: F401 — just check it's importable
        result = asyncio.run(_ping())
        return result
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _insert_open_alert(conn, origin: str, severity: str = "warning") -> int:
    """Insert a synthetic open alert and return its id."""
    return await conn.fetchval(
        """INSERT INTO alert (origin, severity, message, payload)
           VALUES ($1, $2, 'test alert for B3.2', '{}')
           RETURNING id""",
        origin, severity,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestResolveAlertsWiredInRecordRun:
    """All tests use an aborted transaction — zero persistent writes to alert/source_health."""

    def test_scrape_success_closes_scrape_alert_only(self) -> None:
        """record_run(ok=True, phase='scrape') resolves scrape alert, leaves discover + other untouched."""
        asyncio.run(self._run_scrape_success_closes_scrape_alert_only())

    async def _run_scrape_success_closes_scrape_alert_only(self) -> None:
        import asyncpg
        from pipeline.ops.health import record_run

        SOURCE = "test_src_b32"
        OTHER_SOURCE = "other_src_b32"

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                # Ensure source_health rows exist (or will be upserted by record_run).
                # We deliberately do NOT pre-insert them — record_run handles the upsert.

                # 1. Insert three synthetic open alerts.
                scrape_alert_id = await _insert_open_alert(conn, f"{SOURCE}:scrape")
                discover_alert_id = await _insert_open_alert(conn, f"{SOURCE}:discover")
                other_alert_id = await _insert_open_alert(conn, f"{OTHER_SOURCE}:scrape")

                # 2. Call record_run for SOURCE with ok=True, phase='scrape'.
                outcome = await record_run(conn, SOURCE, ok=True, phase="scrape")

                # 3. Check the scrape alert is now resolved.
                scrape_row = await conn.fetchrow(
                    "SELECT resolved_at FROM alert WHERE id=$1", scrape_alert_id
                )
                assert scrape_row["resolved_at"] is not None, (
                    f"Scrape alert id={scrape_alert_id} must be resolved after ok=True scrape run"
                )

                # 4. Discover alert for the SAME source must still be open.
                discover_row = await conn.fetchrow(
                    "SELECT resolved_at FROM alert WHERE id=$1", discover_alert_id
                )
                assert discover_row["resolved_at"] is None, (
                    f"Discover alert id={discover_alert_id} must NOT be resolved by a scrape run"
                )

                # 5. Other source's alert must still be open.
                other_row = await conn.fetchrow(
                    "SELECT resolved_at FROM alert WHERE id=$1", other_alert_id
                )
                assert other_row["resolved_at"] is None, (
                    f"Other-source alert id={other_alert_id} must NOT be resolved"
                )

                # 6. RunOutcome sanity.
                assert outcome.source_key == SOURCE
                assert outcome.status == "healthy"
                assert outcome.consecutive_fails == 0

                # Abort — no persistent writes.
                raise _Rollback

        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_no_open_alert_noop(self) -> None:
        """record_run(ok=True) with no open alert for that origin returns healthy without error."""
        asyncio.run(self._run_no_open_alert_noop())

    async def _run_no_open_alert_noop(self) -> None:
        import asyncpg
        from pipeline.ops.health import record_run

        SOURCE = "test_src_b32_clean"
        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                # No alert inserted for this source — resolve_alerts must be a no-op.
                outcome = await record_run(conn, SOURCE, ok=True, phase="scrape")
                assert outcome.status == "healthy"
                assert outcome.consecutive_fails == 0
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_failed_run_does_not_resolve_alerts(self) -> None:
        """record_run(ok=False) must NOT resolve open alerts."""
        asyncio.run(self._run_failed_run_does_not_resolve_alerts())

    async def _run_failed_run_does_not_resolve_alerts(self) -> None:
        import asyncpg
        from pipeline.ops.health import record_run

        SOURCE = "test_src_b32_fail"
        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                alert_id = await _insert_open_alert(conn, f"{SOURCE}:scrape", severity="critical")

                await record_run(
                    conn, SOURCE, ok=False, phase="scrape",
                    error="synthetic failure for B3.2 test",
                )

                row = await conn.fetchrow(
                    "SELECT resolved_at FROM alert WHERE id=$1", alert_id
                )
                assert row["resolved_at"] is None, (
                    f"Alert id={alert_id} must remain open after a failed run"
                )
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_discover_success_closes_discover_alert_not_scrape(self) -> None:
        """record_run(ok=True, phase='discover') closes discover alert, leaves scrape alert open."""
        asyncio.run(self._run_discover_success_closes_discover_alert_not_scrape())

    async def _run_discover_success_closes_discover_alert_not_scrape(self) -> None:
        import asyncpg
        from pipeline.ops.health import record_run

        SOURCE = "test_src_b32_disc"
        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                scrape_alert_id = await _insert_open_alert(conn, f"{SOURCE}:scrape")
                discover_alert_id = await _insert_open_alert(conn, f"{SOURCE}:discover")

                await record_run(conn, SOURCE, ok=True, phase="discover")

                # Discover alert resolved.
                disc_row = await conn.fetchrow(
                    "SELECT resolved_at FROM alert WHERE id=$1", discover_alert_id
                )
                assert disc_row["resolved_at"] is not None, (
                    f"Discover alert id={discover_alert_id} must be resolved after ok=True discover run"
                )

                # Scrape alert still open.
                scrape_row = await conn.fetchrow(
                    "SELECT resolved_at FROM alert WHERE id=$1", scrape_alert_id
                )
                assert scrape_row["resolved_at"] is None, (
                    f"Scrape alert id={scrape_alert_id} must NOT be resolved by a discover run"
                )
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_backward_compat_default_phase_is_scrape(self) -> None:
        """Omitting phase= defaults to 'scrape' (backward-compatible with all existing callers)."""
        asyncio.run(self._run_backward_compat_default_phase_is_scrape())

    async def _run_backward_compat_default_phase_is_scrape(self) -> None:
        import asyncpg
        from pipeline.ops.health import record_run

        SOURCE = "test_src_b32_compat"
        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                scrape_alert_id = await _insert_open_alert(conn, f"{SOURCE}:scrape")

                # Omit phase — must default to scrape.
                await record_run(conn, SOURCE, ok=True)

                scrape_row = await conn.fetchrow(
                    "SELECT resolved_at FROM alert WHERE id=$1", scrape_alert_id
                )
                assert scrape_row["resolved_at"] is not None, (
                    "Default phase='scrape' must resolve the scrape alert"
                )
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()


# ---------------------------------------------------------------------------
# Sentinel exception used to abort transactions cleanly
# ---------------------------------------------------------------------------

class _Rollback(Exception):
    """Internal sentinel: raised to force transaction rollback inside 'async with conn.transaction()'."""
