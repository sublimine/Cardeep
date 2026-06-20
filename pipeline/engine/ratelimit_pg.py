"""Distributed per-host rate limiter on Postgres (shared state across processes).

The in-memory governor (governor.py) throttles correctly inside ONE process, but
its buckets and ban scars live in RAM — N workers (or a VPS restart) each start
with a full bucket and a clean slate, so they collectively hammer a host and
re-earn a ban the moment we scale out. This backend moves the bucket state into
Postgres (the DB we already run), so every worker draws from the SAME per-host
token bucket and SEES the same ban cooldown.

Design (why a SQL function, not app-side math): the refill + spend must be ATOMIC
across processes. A read-modify-write in Python would race between workers. Instead
one `engine_ratelimit_acquire()` plpgsql call does refill + spacing-floor + spend
+ ban-check under the row lock the UPDATE already takes, returning (granted, wait).
The Python side just loops: granted -> return; else sleep(wait) and retry — exactly
the shape of the in-memory `_Bucket.acquire`, so the governor seam is unchanged.

Ban scars (`banned_until`) persist in the same row, so a ban one worker observes
throttles ALL workers until it expires — the distributed equivalent of the AS24
scar. Uses the DB clock (`clock_timestamp()`) as the single shared "now".
"""
from __future__ import annotations

import asyncpg

_SCHEMA = """
CREATE TABLE IF NOT EXISTS engine_ratelimit_bucket (
    host          text PRIMARY KEY,
    rate          double precision NOT NULL,
    burst         double precision NOT NULL,
    min_spacing   double precision NOT NULL,
    tokens        double precision NOT NULL,
    last_refill   timestamptz NOT NULL DEFAULT clock_timestamp(),
    last_grant    timestamptz NOT NULL DEFAULT to_timestamp(0),
    banned_until  timestamptz
);
"""

# Atomic: refill -> ban-check -> spacing-floor -> spend, all under the row lock.
# Returns (granted bool, wait_seconds double). Idempotent (CREATE OR REPLACE).
_FUNC = """
CREATE OR REPLACE FUNCTION engine_ratelimit_acquire(
    p_host text, p_rate double precision, p_burst double precision,
    p_min_spacing double precision)
RETURNS TABLE(granted boolean, wait_seconds double precision)
LANGUAGE plpgsql AS $$
DECLARE
    v_now timestamptz := clock_timestamp();
    v_tokens double precision;
    v_last_refill timestamptz;
    v_last_grant timestamptz;
    v_banned timestamptz;
    v_elapsed double precision;
    v_spacing_gap double precision;
    v_need_token double precision;
BEGIN
    INSERT INTO engine_ratelimit_bucket(host, rate, burst, min_spacing, tokens)
    VALUES (p_host, p_rate, p_burst, p_min_spacing, p_burst)
    ON CONFLICT (host) DO UPDATE SET rate = EXCLUDED.rate, burst = EXCLUDED.burst,
        min_spacing = EXCLUDED.min_spacing;

    SELECT tokens, last_refill, last_grant, banned_until
      INTO v_tokens, v_last_refill, v_last_grant, v_banned
      FROM engine_ratelimit_bucket WHERE host = p_host FOR UPDATE;

    -- refill
    v_elapsed := EXTRACT(EPOCH FROM (v_now - v_last_refill));
    IF v_elapsed > 0 THEN
        v_tokens := LEAST(p_burst, v_tokens + v_elapsed * p_rate);
        v_last_refill := v_now;
    END IF;

    -- ban scar: shared cooldown, throttles every worker
    IF v_banned IS NOT NULL AND v_banned > v_now THEN
        UPDATE engine_ratelimit_bucket
           SET tokens = v_tokens, last_refill = v_last_refill WHERE host = p_host;
        RETURN QUERY SELECT false, EXTRACT(EPOCH FROM (v_banned - v_now))::double precision;
        RETURN;
    END IF;

    -- spacing floor
    v_spacing_gap := CASE WHEN EXTRACT(EPOCH FROM v_last_grant) > 0
        THEN p_min_spacing - EXTRACT(EPOCH FROM (v_now - v_last_grant)) ELSE 0 END;

    IF v_tokens >= 1.0 AND v_spacing_gap <= 0 THEN
        UPDATE engine_ratelimit_bucket
           SET tokens = v_tokens - 1.0, last_refill = v_last_refill, last_grant = v_now
         WHERE host = p_host;
        RETURN QUERY SELECT true, 0::double precision;
        RETURN;
    END IF;

    -- denied: persist refill, report the shortest wait that could satisfy both
    UPDATE engine_ratelimit_bucket
       SET tokens = v_tokens, last_refill = v_last_refill WHERE host = p_host;
    v_need_token := CASE WHEN v_tokens >= 1.0 THEN 0 ELSE (1.0 - v_tokens) / p_rate END;
    RETURN QUERY SELECT false, GREATEST(v_need_token, v_spacing_gap, 0.001)::double precision;
END;
$$;
"""


class PostgresRateLimiter:
    """Shared per-host bucket on Postgres. One instance per process; all share rows."""

    def __init__(self, dsn: str, *, pool: asyncpg.Pool | None = None) -> None:
        self._dsn = dsn
        self._pool = pool

    async def _get_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self._dsn, min_size=1, max_size=4)
        return self._pool

    async def ensure_schema(self) -> None:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(_SCHEMA)
            await conn.execute(_FUNC)

    async def _try_acquire(self, host: str, *, rate: float, burst: float,
                           min_spacing: float) -> tuple[bool, float]:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT granted, wait_seconds FROM engine_ratelimit_acquire($1,$2,$3,$4)",
                host, rate, burst, min_spacing)
        return bool(row["granted"]), float(row["wait_seconds"])

    async def acquire(self, host: str, *, rate: float, burst: float,
                      min_spacing: float, jitter: float = 0.0,
                      sleep=None) -> float:
        """Block until a token is granted for `host`; return total seconds waited.

        Mirrors the in-memory bucket: loops try_acquire -> sleep(wait+jitter). The
        atomic SQL means concurrent workers serialize on the row, so the aggregate
        rate against a host never exceeds the ceiling no matter how many processes.
        """
        import asyncio
        import random
        sleeper = sleep or asyncio.sleep
        waited = 0.0
        while True:
            granted, wait = await self._try_acquire(
                host, rate=rate, burst=burst, min_spacing=min_spacing)
            if granted:
                return waited
            delay = wait + (random.uniform(0.0, jitter) if jitter else 0.0)
            waited += delay
            await sleeper(delay)

    async def record_ban(self, host: str, cooldown_s: float) -> None:
        """Set a shared cooldown for `host` (the distributed ban scar)."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO engine_ratelimit_bucket(host, rate, burst, min_spacing, "
                "tokens, banned_until) VALUES ($1, 1, 1, 1, 0, "
                "clock_timestamp() + ($2 || ' seconds')::interval) "
                "ON CONFLICT (host) DO UPDATE SET banned_until = "
                "clock_timestamp() + ($2 || ' seconds')::interval",
                host, str(cooldown_s))

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
