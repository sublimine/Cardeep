"""F3 — health.py additions: exponential backoff jitter + Hystrix-correct half-open gate.

Two things this covers that pipeline/ops/health.py did not have before F3:

  1. _compute_backoff_cooldown_seconds — jitter on the exponential cooldown (Zyte pattern,
     00-marketplace-engine.md §2), so several sources tripping together do not all re-probe
     at the exact same instant. Pure function, no DB.

  2. is_open() now blocks a SECOND caller while a probe is already outstanding (state
     'half_open'): before F3 it returned False (allowed) for ANY state other than 'open',
     which meant a half-open window admitted more than the Hystrix-mandated single probe.
     Uses the same aborted-transaction pattern as tests/test_resilience_loop.py (synthetic
     source_key, zero persistent writes).
"""
from __future__ import annotations

import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.ops.health import (
    BREAKER_COOLDOWN_SEC,
    BREAKER_JITTER_FRAC,
    _compute_backoff_cooldown_seconds,
)

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
SOURCE_KEY = "__f3_jitter_test__"
PHASE = "scrape"


def _db_available() -> bool:
    try:
        import asyncpg
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
    pass


# ---------------------------------------------------------------------------
# 1. _compute_backoff_cooldown_seconds — pure, deterministic via injected rng
# ---------------------------------------------------------------------------

class _FixedRng:
    """Deterministic stand-in for random.Random: uniform() always returns a fixed offset."""

    def __init__(self, offset: float) -> None:
        self._offset = offset

    def uniform(self, low: float, high: float) -> float:
        # Return the requested offset, clamped into [low, high] like random.uniform would
        # for a legitimate value (both are symmetric around 0 in the real call site).
        return self._offset


class TestBackoffJitter:
    def test_depth_zero_is_base_cooldown_when_no_jitter(self) -> None:
        result = _compute_backoff_cooldown_seconds(0, rng=_FixedRng(0.0))
        assert result == BREAKER_COOLDOWN_SEC

    def test_depth_doubles_nominal_each_step(self) -> None:
        d0 = _compute_backoff_cooldown_seconds(0, rng=_FixedRng(0.0))
        d1 = _compute_backoff_cooldown_seconds(1, rng=_FixedRng(0.0))
        d2 = _compute_backoff_cooldown_seconds(2, rng=_FixedRng(0.0))
        assert d1 == pytest.approx(d0 * 2)
        assert d2 == pytest.approx(d0 * 4)

    def test_cap_is_respected(self) -> None:
        # A very deep depth must hit the 86400s (24h) cap, not grow unbounded.
        result = _compute_backoff_cooldown_seconds(20, rng=_FixedRng(0.0))
        assert result <= 86400

    def test_jitter_moves_result_within_bounds(self) -> None:
        base = 900
        nominal = base  # depth=0
        jitter_amount = nominal * BREAKER_JITTER_FRAC
        high = _compute_backoff_cooldown_seconds(0, base=base, rng=_FixedRng(jitter_amount))
        low = _compute_backoff_cooldown_seconds(0, base=base, rng=_FixedRng(-jitter_amount))
        assert high == pytest.approx(nominal + jitter_amount)
        assert low == pytest.approx(max(base, nominal - jitter_amount))

    def test_jitter_never_produces_shorter_than_base(self) -> None:
        """The floor at `base` guards against jitter producing a near-zero cooldown."""
        result = _compute_backoff_cooldown_seconds(0, base=900, rng=_FixedRng(-10_000))
        assert result >= 900

    def test_real_rng_produces_variance_across_calls(self) -> None:
        """With the REAL module-level random (no injected rng), repeated calls at the same
        depth must not all be identical — this is what a thundering-herd fix requires."""
        results = {_compute_backoff_cooldown_seconds(0) for _ in range(20)}
        assert len(results) > 1, (
            "20 calls at the same depth produced identical cooldowns — jitter is not active"
        )


# ---------------------------------------------------------------------------
# 2. is_open() — half-open blocks a second concurrent caller (Hystrix: exactly one probe)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestHalfOpenSingleProbe:
    def test_second_call_after_transition_is_blocked(self) -> None:
        asyncio.run(self._run())

    async def _run(self) -> None:
        import asyncpg

        from pipeline.ops.health import BREAKER_TRIP_AT, is_open, record_run

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                for _ in range(BREAKER_TRIP_AT):
                    await record_run(conn, SOURCE_KEY, ok=False, error="synthetic", phase=PHASE)

                # Force the cooldown into the past (simulate time passing).
                await conn.execute(
                    "UPDATE source_breaker SET cooldown_until = now() - interval '1 second' "
                    "WHERE source_key=$1",
                    SOURCE_KEY,
                )

                # First caller: cooldown elapsed -> claims the slot -> allowed (False = not blocked).
                first = await is_open(conn, SOURCE_KEY)
                assert first is False, "First caller after cooldown must be let through"

                # Second caller, same instant: the slot is now half_open -> must be BLOCKED.
                second = await is_open(conn, SOURCE_KEY)
                assert second is True, (
                    "A second caller while a probe is already outstanding (half_open) must "
                    "be blocked — Hystrix admits exactly ONE request during half-open"
                )

                state = await conn.fetchval(
                    "SELECT state FROM source_breaker WHERE source_key=$1", SOURCE_KEY)
                assert state == "half_open"

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_probe_success_closes_from_half_open(self) -> None:
        asyncio.run(self._run_success())

    async def _run_success(self) -> None:
        import asyncpg

        from pipeline.ops.health import BREAKER_TRIP_AT, is_open, record_run

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                for _ in range(BREAKER_TRIP_AT):
                    await record_run(conn, SOURCE_KEY, ok=False, error="synthetic", phase=PHASE)
                await conn.execute(
                    "UPDATE source_breaker SET cooldown_until = now() - interval '1 second' "
                    "WHERE source_key=$1",
                    SOURCE_KEY,
                )
                assert await is_open(conn, SOURCE_KEY) is False  # claims -> half_open

                # The probe succeeds.
                outcome = await record_run(conn, SOURCE_KEY, ok=True, rows=5, phase=PHASE)
                assert outcome.breaker_state == "closed"
                assert await is_open(conn, SOURCE_KEY) is False

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()
