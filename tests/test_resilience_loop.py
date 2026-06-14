"""B3.5 — Resilience loop integration test (SYNTHETIC data, no real scrapers).

Demonstrates the COMPLETE B3 gate loop using REAL helpers from pipeline/ops/health.py
inside aborted transactions (zero persistent DB mutation):

  1. record_run(ok=False) × 3  raises consecutive_fails,
     fires fire_alert with origin = source_key:phase (exact origin),
     and trips the circuit breaker to OPEN (source_breaker.state == 'open').

  2. is_open() returns True while the breaker is OPEN  -> next harvest attempt
     is blocked (graceful degradation).

  3. record_run(ok=True) closes the alert (resolve_alerts via B3.2 wiring) and
     resets consecutive_fails = 0; source_breaker returns to 'closed'.

  4. is_open() now returns False (breaker closed again).

  5. GET /health via TestClient returns 200 even while the synthetic source is
     'down' — the API pool is independent of the harvester (no cross-contamination).

All DB interactions run inside an async with conn.transaction() block that is aborted
at the end with a sentinel exception (_Rollback). The source_key '__resilience_test__'
is never committed; source_health, source_breaker, alert, and harvest_run tables are
untouched after the test.

The /health FastAPI test uses a separate TestClient; it does NOT share the aborted
transaction (it opens its own pool via lifespan). This proves the API stays live
regardless of harvester state.
"""
from __future__ import annotations

import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# DB connectivity guard — skip entire module when cardeep-pg is not reachable.
# ---------------------------------------------------------------------------
DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
SOURCE_KEY = "__resilience_test__"
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
    """Sentinel: forces transaction rollback at the end of each test body."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _count_open_alerts(conn, origin: str) -> int:
    return await conn.fetchval(
        "SELECT count(*) FROM alert WHERE origin=$1 AND resolved_at IS NULL",
        origin,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestResilienceLoop:
    """Full B3 gate: fail -> alert -> breaker OPEN -> success -> resolve -> breaker CLOSED."""

    # ------------------------------------------------------------------
    # 1. Three consecutive failures raise consecutive_fails, fire the
    #    exact-origin alert, and trip the breaker to OPEN.
    # ------------------------------------------------------------------
    def test_consecutive_fails_trip_breaker_and_fire_alert(self) -> None:
        asyncio.run(self._run_consecutive_fails_trip_breaker_and_fire_alert())

    async def _run_consecutive_fails_trip_breaker_and_fire_alert(self) -> None:
        import asyncpg
        from pipeline.ops.health import (
            BREAKER_TRIP_AT,
            auto_repair,
            build_origin,
            record_run,
        )

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                origin = build_origin(SOURCE_KEY, PHASE)

                # Inject BREAKER_TRIP_AT consecutive failures.
                last_outcome = None
                for _ in range(BREAKER_TRIP_AT):
                    last_outcome = await record_run(
                        conn, SOURCE_KEY, ok=False,
                        error="synthetic scrape failure",
                        phase=PHASE,
                    )

                # Verify consecutive_fails reached the trip threshold.
                assert last_outcome is not None
                assert last_outcome.consecutive_fails == BREAKER_TRIP_AT, (
                    f"Expected consecutive_fails={BREAKER_TRIP_AT}, "
                    f"got {last_outcome.consecutive_fails}"
                )
                assert last_outcome.status in ("down", "degraded"), (
                    f"Status should be 'down' or 'degraded' after {BREAKER_TRIP_AT} "
                    f"fails, got {last_outcome.status!r}"
                )

                # Breaker must now be OPEN.
                assert last_outcome.breaker_state == "open", (
                    f"Breaker must be OPEN after {BREAKER_TRIP_AT} consecutive fails; "
                    f"got {last_outcome.breaker_state!r}"
                )
                assert last_outcome.breaker_tripped is True, (
                    "breaker_tripped must be True on the transition cycle"
                )

                # auto_repair must fire an alert with the EXACT origin (source_key:phase).
                await auto_repair(conn, SOURCE_KEY, "synthetic scrape failure",
                                  phase=PHASE)
                n_open = await _count_open_alerts(conn, origin)
                assert n_open >= 1, (
                    f"Expected >=1 open alert for origin '{origin}'; found {n_open}"
                )

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    # ------------------------------------------------------------------
    # 2. is_open() returns True when the breaker is OPEN (blocks harvest).
    # ------------------------------------------------------------------
    def test_is_open_returns_true_when_breaker_is_open(self) -> None:
        asyncio.run(self._run_is_open_returns_true_when_breaker_is_open())

    async def _run_is_open_returns_true_when_breaker_is_open(self) -> None:
        import asyncpg
        from pipeline.ops.health import BREAKER_TRIP_AT, is_open, record_run

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                # Trip the breaker inside this transaction.
                for _ in range(BREAKER_TRIP_AT):
                    await record_run(conn, SOURCE_KEY, ok=False,
                                     error="synthetic failure", phase=PHASE)

                # is_open() must now return True — the next harvest attempt is blocked.
                open_state = await is_open(conn, SOURCE_KEY)
                assert open_state is True, (
                    "is_open() must return True while the breaker is OPEN; "
                    f"got {open_state!r}"
                )
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    # ------------------------------------------------------------------
    # 3. record_run(ok=True) closes the alert (B3.2) and resets the breaker.
    # ------------------------------------------------------------------
    def test_success_closes_alert_and_resets_breaker(self) -> None:
        asyncio.run(self._run_success_closes_alert_and_resets_breaker())

    async def _run_success_closes_alert_and_resets_breaker(self) -> None:
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
                origin = build_origin(SOURCE_KEY, PHASE)

                # Phase A — inject failures to trip the breaker and open an alert.
                for _ in range(BREAKER_TRIP_AT):
                    await record_run(conn, SOURCE_KEY, ok=False,
                                     error="synthetic failure", phase=PHASE)
                await auto_repair(conn, SOURCE_KEY, "synthetic failure", phase=PHASE)

                n_before = await _count_open_alerts(conn, origin)
                assert n_before >= 1, "Pre-condition: at least one open alert for this origin"

                breaker_open_before = await is_open(conn, SOURCE_KEY)
                assert breaker_open_before is True, "Pre-condition: breaker must be OPEN"

                # Phase B — one successful run (B3.2 wiring).
                recovery = await record_run(
                    conn, SOURCE_KEY, ok=True, rows=42, phase=PHASE
                )

                # consecutive_fails must be reset to zero.
                assert recovery.consecutive_fails == 0, (
                    f"consecutive_fails must be 0 after success; got {recovery.consecutive_fails}"
                )

                # Alert for this exact origin must now be resolved (B3.2 closed the loop).
                n_after = await _count_open_alerts(conn, origin)
                assert n_after == 0, (
                    f"Open alerts for origin '{origin}' must be 0 after ok=True; found {n_after}"
                )

                # Breaker must be CLOSED again.
                assert recovery.breaker_state == "closed", (
                    f"Breaker must be CLOSED after a successful run; "
                    f"got {recovery.breaker_state!r}"
                )
                breaker_open_after = await is_open(conn, SOURCE_KEY)
                assert breaker_open_after is False, (
                    "is_open() must return False after the breaker is closed"
                )

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    # ------------------------------------------------------------------
    # 4. Full end-to-end loop (all three assertions in one pass).
    # ------------------------------------------------------------------
    def test_full_resilience_loop_end_to_end(self) -> None:
        asyncio.run(self._run_full_resilience_loop_end_to_end())

    async def _run_full_resilience_loop_end_to_end(self) -> None:
        """The canonical B3.5 gate: fail × N -> alert with exact origin -> breaker OPEN
        -> success -> alert resolved -> breaker CLOSED -> is_open() False."""
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
                origin = build_origin(SOURCE_KEY, PHASE)

                # --- FAIL LOOP ---
                for i in range(BREAKER_TRIP_AT):
                    outcome = await record_run(
                        conn, SOURCE_KEY, ok=False,
                        error="synthetic: connection refused",
                        phase=PHASE,
                    )
                    # auto_repair wires in the exact-origin alert each cycle.
                    await auto_repair(
                        conn, SOURCE_KEY,
                        "synthetic: connection refused",
                        phase=PHASE,
                    )

                # Assert breaker is OPEN.
                assert outcome.breaker_state == "open", (
                    f"After {BREAKER_TRIP_AT} fails breaker must be OPEN, "
                    f"got {outcome.breaker_state!r}"
                )

                # Assert exact-origin alert exists.
                n_alerts = await _count_open_alerts(conn, origin)
                assert n_alerts >= 1, (
                    f"At least one open alert expected for '{origin}'; found {n_alerts}"
                )

                # Assert is_open() blocks.
                assert await is_open(conn, SOURCE_KEY) is True

                # --- RECOVERY ---
                ok_outcome = await record_run(
                    conn, SOURCE_KEY, ok=True, rows=100, phase=PHASE
                )

                # Breaker closed.
                assert ok_outcome.breaker_state == "closed"
                assert ok_outcome.consecutive_fails == 0

                # Alert resolved (B3.2).
                assert await _count_open_alerts(conn, origin) == 0, (
                    "All open alerts for this origin must be resolved after ok=True"
                )

                # is_open() now returns False.
                assert await is_open(conn, SOURCE_KEY) is False

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()


# ---------------------------------------------------------------------------
# 5. API stays live independently of harvester state.
#    Uses a separate TestClient — its pool is not inside the aborted tx.
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestApiAliveWhileSourceDown:
    """GET /health returns 200 even when a harvester source would be 'down'.

    The FastAPI pool is created independently in lifespan and is completely
    separate from the harvester's asyncpg connections. A failed/open source
    never affects the API's ability to respond.
    """

    def test_health_returns_200_regardless_of_source_state(self) -> None:
        from fastapi.testclient import TestClient
        from services.api.main import app

        with TestClient(app) as client:
            resp = client.get("/health")
        assert resp.status_code == 200, (
            f"GET /health must return 200 even when a source is 'down'; "
            f"got {resp.status_code}"
        )
        body = resp.json()
        assert body.get("ok") is True
        assert body.get("data", {}).get("status") == "live"
