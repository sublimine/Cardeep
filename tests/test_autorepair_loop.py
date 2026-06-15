"""Auto-repair loop — full fault injection test (SYNTHETIC, zero persistent writes).

Verifies the COMPLETE E2E loop against a REAL asyncpg connection, all inside an
aborted transaction so no row survives after the test:

  A. Status state machine:
       record_run(ok=False) × 1  ->  healthy -> degraded  (DEGRADE_AT = 1)
       record_run(ok=False) × 2  ->  degraded (consecutive_fails = 2)
       record_run(ok=False) × 3  ->  down + breaker OPEN  (DOWN_AT = DOWN_AT, BREAKER_TRIP_AT = 3)

  B. Alert dedup (UPSERT): two calls to auto_repair() on the same origin produce
       exactly ONE open alert row, not two.

  C. Repair action classification:
       "rate limit" reason   ->  ACTION_QUARANTINE (succeeded=TRUE, €0)
       "connection refused"  ->  ACTION_ESCALATE_OWNER (succeeded=TRUE, €0)
       "403 forbidden"       ->  ACTION_REFINGERPRINT (spend-gated, succeeded=FALSE)

  D. Isolation: is_open(source_A) == True does NOT cause is_open(source_B) == True.

  E. Recovery:
       record_run(ok=True)  ->  status='healthy', consecutive_fails=0,
                                breaker='closed', alert resolved (resolved_at IS NOT NULL).

  F. Idempotency: run the loop twice inside the same transaction — the second pass
       starts from a clean slate (consecutive_fails reset by recovery), so status
       returns to healthy and no stale alert leaks across the two cycles.

All DB interactions run inside `async with conn.transaction()` aborted with a
sentinel exception (_Rollback).  The source_key '__autorepair_inject__' is NEVER
committed; source_health, source_breaker, alert, harvest_run, and repair_attempt
tables are left untouched after the test.

Requires: cardeep-pg reachable at 127.0.0.1:5433 (Docker).
Skip marker: @pytest.mark.skipif(not DB_AVAILABLE, ...).
"""
from __future__ import annotations

import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# DB connectivity guard
# ---------------------------------------------------------------------------
DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
SOURCE_A = "__autorepair_inject__"
SOURCE_B = "__autorepair_inject_b__"
PHASE = "scrape"


def _db_available() -> bool:
    try:
        import asyncpg  # noqa: F401
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
    """Sentinel: forces the asyncpg transaction to abort cleanly at test end."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _open_alert_count(conn, origin: str) -> int:
    """Count unresolved alerts for a given exact origin."""
    return await conn.fetchval(
        "SELECT count(*) FROM alert WHERE origin=$1 AND resolved_at IS NULL",
        origin,
    )


async def _health_row(conn, source_key: str) -> dict | None:
    """Fetch source_health row as a plain dict (or None if absent)."""
    row = await conn.fetchrow(
        "SELECT consecutive_fails, status FROM source_health WHERE source_key=$1",
        source_key,
    )
    if row is None:
        return None
    return dict(row)


async def _breaker_state(conn, source_key: str) -> str:
    """Return the breaker state string, or 'closed' if the row is absent."""
    row = await conn.fetchrow(
        "SELECT state FROM source_breaker WHERE source_key=$1", source_key
    )
    return row["state"] if row else "closed"


async def _repair_attempt_count(conn, source_key: str) -> int:
    """Count repair_attempt rows for this source inside the transaction."""
    return await conn.fetchval(
        "SELECT count(*) FROM repair_attempt WHERE source_key=$1", source_key
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestAutoRepairLoopInjection:
    """Full fault-injection test: SYNTHETIC source key, aborted transaction, zero residue."""

    # ------------------------------------------------------------------
    # A — Status state machine: healthy -> degraded -> down
    # ------------------------------------------------------------------
    def test_status_transitions_healthy_degraded_down(self) -> None:
        asyncio.run(self._run_status_transitions())

    async def _run_status_transitions(self) -> None:
        import asyncpg
        from pipeline.ops.health import BREAKER_TRIP_AT, DEGRADE_AT, DOWN_AT, record_run

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                # Before any run: no row exists.
                assert await _health_row(conn, SOURCE_A) is None

                # First failure: consecutive_fails == 1 -> degraded (DEGRADE_AT == 1).
                out1 = await record_run(conn, SOURCE_A, ok=False,
                                        error="synthetic fail 1", phase=PHASE)
                assert out1.consecutive_fails == 1
                assert out1.status == "degraded", (
                    f"First fail should be 'degraded' (DEGRADE_AT={DEGRADE_AT}); "
                    f"got {out1.status!r}"
                )
                assert out1.breaker_state == "closed", (
                    "Breaker must stay closed below BREAKER_TRIP_AT"
                )

                # Second failure: consecutive_fails == 2 -> still degraded, breaker still closed.
                out2 = await record_run(conn, SOURCE_A, ok=False,
                                        error="synthetic fail 2", phase=PHASE)
                assert out2.consecutive_fails == 2
                assert out2.status == "degraded"
                assert out2.breaker_state == "closed"

                # Third failure: consecutive_fails == 3 -> down + breaker OPEN.
                out3 = await record_run(conn, SOURCE_A, ok=False,
                                        error="synthetic fail 3", phase=PHASE)
                assert out3.consecutive_fails == BREAKER_TRIP_AT
                assert out3.status == "down", (
                    f"After {BREAKER_TRIP_AT} fails status must be 'down' "
                    f"(DOWN_AT={DOWN_AT}); got {out3.status!r}"
                )
                assert out3.breaker_state == "open", (
                    f"Breaker must be OPEN at {BREAKER_TRIP_AT} consecutive fails; "
                    f"got {out3.breaker_state!r}"
                )
                assert out3.breaker_tripped is True, (
                    "breaker_tripped must be True on the transition cycle to OPEN"
                )

                # status_changed only True on transition boundaries.
                assert out1.status_changed is True, "First fail: unknown->degraded is a status change"
                assert out2.status_changed is False, "degraded->degraded is NOT a status change"
                assert out3.status_changed is True, "degraded->down IS a status change"

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    # ------------------------------------------------------------------
    # B — Alert dedup: two auto_repair calls = exactly ONE open alert
    # ------------------------------------------------------------------
    def test_alert_dedup_upsert_not_duplicate(self) -> None:
        asyncio.run(self._run_alert_dedup())

    async def _run_alert_dedup(self) -> None:
        import asyncpg
        from pipeline.ops.health import BREAKER_TRIP_AT, auto_repair, build_origin, record_run

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                origin = build_origin(SOURCE_A, PHASE)

                # Trip the breaker first so the context is realistic.
                for _ in range(BREAKER_TRIP_AT):
                    await record_run(conn, SOURCE_A, ok=False,
                                     error="synthetic fail", phase=PHASE)

                # Fire auto_repair TWICE for the exact same origin.
                await auto_repair(conn, SOURCE_A, "synthetic fail", phase=PHASE)
                await auto_repair(conn, SOURCE_A, "synthetic fail again", phase=PHASE)

                # UPSERT dedup: must be exactly ONE open alert, never two.
                n = await _open_alert_count(conn, origin)
                assert n == 1, (
                    f"Dedup: two auto_repair calls must produce 1 open alert for '{origin}'; "
                    f"found {n}"
                )

                # But two repair_attempt rows must be written (one per call).
                attempts = await _repair_attempt_count(conn, SOURCE_A)
                assert attempts == 2, (
                    f"Expected 2 repair_attempt rows (one per call); found {attempts}"
                )

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    # ------------------------------------------------------------------
    # C — classify_failure: quarantine (€0 succeeded=TRUE) and spend-gated
    # ------------------------------------------------------------------
    def test_classify_failure_quarantine_is_zero_cost(self) -> None:
        """'rate limit' reason -> QUARANTINE -> succeeded=TRUE in repair_attempt."""
        asyncio.run(self._run_classify_quarantine())

    async def _run_classify_quarantine(self) -> None:
        import asyncpg
        from pipeline.ops.health import ACTION_QUARANTINE, auto_repair, classify_failure

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                reason = "rate limit exceeded, retry after 60s"
                action = classify_failure(reason, http_status=429)
                assert action == ACTION_QUARANTINE, (
                    f"rate-limit reason must map to QUARANTINE; got {action!r}"
                )

                # Write it to the DB and check succeeded=TRUE.
                await auto_repair(conn, SOURCE_A, reason, phase=PHASE, http_status=429)
                row = await conn.fetchrow(
                    "SELECT action, succeeded FROM repair_attempt "
                    "WHERE source_key=$1 ORDER BY id DESC LIMIT 1",
                    SOURCE_A,
                )
                assert row["action"] == ACTION_QUARANTINE
                assert row["succeeded"] is True, (
                    "QUARANTINE is a €0 action and must have succeeded=TRUE"
                )

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_classify_failure_refingerprint_is_spend_gated(self) -> None:
        """403 reason -> REFINGERPRINT -> succeeded=FALSE (spend-gated scaffold)."""
        asyncio.run(self._run_classify_refingerprint())

    async def _run_classify_refingerprint(self) -> None:
        import asyncpg
        from pipeline.ops.health import ACTION_REFINGERPRINT, auto_repair, classify_failure

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                reason = "403 forbidden"
                action = classify_failure(reason, http_status=403)
                assert action == ACTION_REFINGERPRINT, (
                    f"403 reason must map to REFINGERPRINT; got {action!r}"
                )

                await auto_repair(conn, SOURCE_A, reason, phase=PHASE, http_status=403)
                row = await conn.fetchrow(
                    "SELECT action, succeeded FROM repair_attempt "
                    "WHERE source_key=$1 ORDER BY id DESC LIMIT 1",
                    SOURCE_A,
                )
                assert row["action"] == ACTION_REFINGERPRINT
                assert row["succeeded"] is False, (
                    "REFINGERPRINT is spend-gated; succeeded must be FALSE (scaffold)"
                )

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    # ------------------------------------------------------------------
    # D — Isolation: breaker OPEN on SOURCE_A does not block SOURCE_B
    # ------------------------------------------------------------------
    def test_breaker_isolation_source_a_open_does_not_block_source_b(self) -> None:
        asyncio.run(self._run_breaker_isolation())

    async def _run_breaker_isolation(self) -> None:
        import asyncpg
        from pipeline.ops.health import BREAKER_TRIP_AT, is_open, record_run

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                # Trip breaker on SOURCE_A.
                for _ in range(BREAKER_TRIP_AT):
                    await record_run(conn, SOURCE_A, ok=False,
                                     error="synthetic fail", phase=PHASE)

                # SOURCE_A breaker must be open.
                assert await is_open(conn, SOURCE_A) is True, (
                    "SOURCE_A breaker must be OPEN after consecutive fails"
                )

                # SOURCE_B has had no failures — its breaker must stay closed.
                assert await is_open(conn, SOURCE_B) is False, (
                    "SOURCE_B must be unaffected by SOURCE_A breaker trip — "
                    "isolation violation: a failure on one source must not block another"
                )

                # Confirm SOURCE_B source_health was never written.
                health_b = await _health_row(conn, SOURCE_B)
                assert health_b is None, (
                    "SOURCE_B must have no source_health row — it never ran"
                )

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    # ------------------------------------------------------------------
    # E — Recovery: ok=True resets health + breaker + resolves alert
    # ------------------------------------------------------------------
    def test_recovery_resets_health_breaker_and_resolves_alert(self) -> None:
        asyncio.run(self._run_recovery())

    async def _run_recovery(self) -> None:
        import asyncpg
        from pipeline.ops.health import (
            BREAKER_TRIP_AT,
            auto_repair,
            build_origin,
            is_open,
            record_run,
        )

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                origin = build_origin(SOURCE_A, PHASE)

                # --- FAIL PHASE ---
                for _ in range(BREAKER_TRIP_AT):
                    await record_run(conn, SOURCE_A, ok=False,
                                     error="synthetic fail", phase=PHASE)
                await auto_repair(conn, SOURCE_A, "synthetic fail", phase=PHASE)

                # Pre-conditions.
                assert await is_open(conn, SOURCE_A) is True
                assert await _open_alert_count(conn, origin) == 1

                # --- RECOVERY ---
                ok_out = await record_run(conn, SOURCE_A, ok=True, rows=77, phase=PHASE)

                # Health reset.
                assert ok_out.consecutive_fails == 0, (
                    f"consecutive_fails must be 0 after ok=True; got {ok_out.consecutive_fails}"
                )
                assert ok_out.status == "healthy", (
                    f"status must be 'healthy' after ok=True; got {ok_out.status!r}"
                )

                # Breaker closed.
                assert ok_out.breaker_state == "closed", (
                    f"breaker must be CLOSED after ok=True; got {ok_out.breaker_state!r}"
                )
                assert await is_open(conn, SOURCE_A) is False

                # Alert resolved (B3.2 wiring in record_run).
                remaining_open = await _open_alert_count(conn, origin)
                assert remaining_open == 0, (
                    f"Alert for '{origin}' must be resolved after ok=True; "
                    f"found {remaining_open} still open"
                )

                # Confirm resolved_at is not null.
                resolved_at = await conn.fetchval(
                    "SELECT resolved_at FROM alert WHERE origin=$1 "
                    "AND resolved_at IS NOT NULL LIMIT 1",
                    origin,
                )
                assert resolved_at is not None, (
                    "resolved_at must be non-null after recovery"
                )

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    # ------------------------------------------------------------------
    # F — Idempotency: two complete cycles inside the same transaction
    # ------------------------------------------------------------------
    def test_two_cycles_no_stale_alert_leak(self) -> None:
        """Run fail->recover->fail->recover twice. Second cycle must not see alerts
        from the first cycle (they were resolved). Zero stale alerts at the end."""
        asyncio.run(self._run_two_cycles())

    async def _run_two_cycles(self) -> None:
        import asyncpg
        from pipeline.ops.health import (
            BREAKER_TRIP_AT,
            auto_repair,
            build_origin,
            is_open,
            record_run,
        )

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                origin = build_origin(SOURCE_A, PHASE)

                for cycle in range(2):
                    # Fail phase.
                    for _ in range(BREAKER_TRIP_AT):
                        await record_run(conn, SOURCE_A, ok=False,
                                         error="synthetic fail", phase=PHASE)
                    await auto_repair(conn, SOURCE_A, "synthetic fail", phase=PHASE)

                    assert await is_open(conn, SOURCE_A) is True, (
                        f"Cycle {cycle + 1}: breaker must be OPEN after trip"
                    )
                    assert await _open_alert_count(conn, origin) == 1, (
                        f"Cycle {cycle + 1}: exactly 1 open alert expected"
                    )

                    # Recover.
                    await record_run(conn, SOURCE_A, ok=True, rows=10, phase=PHASE)

                    assert await is_open(conn, SOURCE_A) is False, (
                        f"Cycle {cycle + 1}: breaker must be CLOSED after recovery"
                    )
                    assert await _open_alert_count(conn, origin) == 0, (
                        f"Cycle {cycle + 1}: no open alerts after recovery"
                    )

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    # ------------------------------------------------------------------
    # G — Severity contract: QUARANTINE alert is warning, ESCALATE_OWNER is critical
    # ------------------------------------------------------------------
    def test_alert_severity_matches_action(self) -> None:
        asyncio.run(self._run_alert_severity())

    async def _run_alert_severity(self) -> None:
        import asyncpg
        from pipeline.ops.health import (
            ACTION_QUARANTINE,
            ACTION_ESCALATE_OWNER,
            SEV_WARNING,
            SEV_CRITICAL,
            auto_repair,
            build_origin,
            classify_failure,
        )

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                # QUARANTINE: rate limit -> warning severity.
                await auto_repair(conn, SOURCE_A, "rate limit", phase=PHASE, http_status=429)
                origin_a = build_origin(SOURCE_A, PHASE)
                sev = await conn.fetchval(
                    "SELECT severity FROM alert WHERE origin=$1 AND resolved_at IS NULL",
                    origin_a,
                )
                assert sev == SEV_WARNING, (
                    f"QUARANTINE action must fire a '{SEV_WARNING}' alert; got {sev!r}"
                )

                # ESCALATE_OWNER: unknown error -> critical severity.
                await auto_repair(conn, SOURCE_B, "totally unknown error", phase=PHASE)
                origin_b = build_origin(SOURCE_B, PHASE)
                sev_b = await conn.fetchval(
                    "SELECT severity FROM alert WHERE origin=$1 AND resolved_at IS NULL",
                    origin_b,
                )
                assert sev_b == SEV_CRITICAL, (
                    f"ESCALATE_OWNER action must fire a '{SEV_CRITICAL}' alert; got {sev_b!r}"
                )

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()
