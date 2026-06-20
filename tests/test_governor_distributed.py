"""Distributed governor: in-memory parity (unit) + shared Postgres state (live)."""
import asyncio
import os

import asyncpg
import pytest

from pipeline.engine.governor import RateGovernor
from pipeline.engine.ratelimit_pg import PostgresRateLimiter

_DSN = os.environ.get("CARDEEP_DSN",
                      "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")


# ---- unit: governor delegates to a backend, accumulates waited (no DB) ------

class _FakeBackend:
    """Grants after `deny_n` denials; records the resolved profile it was called with."""
    def __init__(self, deny_n=0):
        self.deny_n = deny_n
        self.calls = []

    async def acquire(self, host, *, rate, burst, min_spacing, jitter):
        self.calls.append((host, rate, burst, min_spacing, jitter))
        return 0.123 * self.deny_n  # pretend it waited proportional to denials


@pytest.mark.asyncio
async def test_governor_routes_to_backend_when_set():
    be = _FakeBackend()
    g = RateGovernor(backend=be)
    g.configure_host("hard.example", rate_per_sec=0.7, burst=1, min_spacing_s=1.4)
    waited = await g.acquire("hard.example")
    assert be.calls and be.calls[0][0] == "hard.example"
    # the host override profile is passed through to the backend
    assert be.calls[0][1] == 0.7 and be.calls[0][3] == 1.4
    assert waited == 0.0


@pytest.mark.asyncio
async def test_in_memory_default_still_works_without_backend():
    g = RateGovernor(rate_per_sec=1000, burst=5)  # fast: no real wait
    waited = await g.acquire("open.example")
    assert waited == 0.0  # first token is immediate


@pytest.mark.asyncio
async def test_pg_acquire_loop_sleeps_until_granted(monkeypatch):
    # Drive the PostgresRateLimiter.acquire loop with a stubbed _try_acquire (no DB):
    # deny twice (wait 0.5s each) then grant; assert it accumulated the waits.
    rl = PostgresRateLimiter(_DSN)
    seq = [(False, 0.5), (False, 0.5), (True, 0.0)]
    calls = {"n": 0}

    async def fake_try(host, *, rate, burst, min_spacing):
        v = seq[calls["n"]]
        calls["n"] += 1
        return v

    slept = []

    async def fake_sleep(d):
        slept.append(d)

    monkeypatch.setattr(rl, "_try_acquire", fake_try)
    waited = await rl.acquire("h", rate=1, burst=1, min_spacing=1, jitter=0, sleep=fake_sleep)
    assert calls["n"] == 3
    assert waited == pytest.approx(1.0)  # 0.5 + 0.5
    assert slept == [0.5, 0.5]


# ---- live integration against the real Postgres (skips if unreachable) ------

async def _pg_reachable() -> bool:
    try:
        c = await asyncpg.connect(_DSN, timeout=5)
        await c.close()
        return True
    except Exception:
        return False


@pytest.mark.asyncio
async def test_live_two_instances_share_bucket_state():
    if not await _pg_reachable():
        pytest.skip("Postgres not reachable")
    host = "test-shared.example"
    a = PostgresRateLimiter(_DSN)
    b = PostgresRateLimiter(_DSN)
    await a.ensure_schema()
    # reset the row deterministically: burst=2, very slow refill so it won't top up
    async with (await a._get_pool()).acquire() as conn:
        await conn.execute("DELETE FROM engine_ratelimit_bucket WHERE host=$1", host)
    try:
        # burst=2 tokens total, shared. Two instances (simulating two processes)
        # should get exactly 2 immediate grants between them, then be throttled.
        g1, _ = await a._try_acquire(host, rate=0.001, burst=2, min_spacing=0)
        g2, _ = await b._try_acquire(host, rate=0.001, burst=2, min_spacing=0)
        g3, w3 = await a._try_acquire(host, rate=0.001, burst=2, min_spacing=0)
        assert g1 is True and g2 is True   # both shared the 2-token burst
        assert g3 is False and w3 > 0      # third is throttled by SHARED state
    finally:
        await a.close()
        await b.close()


@pytest.mark.asyncio
async def test_live_ban_scar_is_shared_across_instances():
    if not await _pg_reachable():
        pytest.skip("Postgres not reachable")
    host = "test-ban.example"
    a = PostgresRateLimiter(_DSN)
    b = PostgresRateLimiter(_DSN)
    await a.ensure_schema()
    try:
        await a.record_ban(host, cooldown_s=30)
        # a DIFFERENT instance observes the ban (shared scar) and is denied with a wait
        granted, wait = await b._try_acquire(host, rate=10, burst=10, min_spacing=0)
        assert granted is False and wait > 0
    finally:
        async with (await a._get_pool()).acquire() as conn:
            await conn.execute("DELETE FROM engine_ratelimit_bucket WHERE host=$1", host)
        await a.close()
        await b.close()
