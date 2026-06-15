"""Live rolled-back tests for the reconcile_gone coverage gate (audit P2 SU-A4 GONE).

reconcile_gone now refuses to retire not-re-seen vehicles unless the source's latest B9 coverage
confirms a complete harvest (coverage_pct >= min_coverage and verdict != REFUTED). This guards the
GONE/bajas event from a partial harvest falsely retiring un-captured stock. Tested with a synthetic
source_coverage row + a test source_key that owns no vehicles (the gate short-circuits before the
count), so the gate's decision is isolated. All rolled back. SKIP if no DB.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import asyncpg
import pytest

from pipeline.delta import reconcile_gone

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
_SRC = "test-reconcile-gone-cov"
_T0 = datetime(2020, 1, 1, tzinfo=timezone.utc)


def _db_ok() -> bool:
    async def _p() -> bool:
        try:
            c = await asyncpg.connect(DSN, timeout=3)
            await c.close()
            return True
        except Exception:
            return False
    try:
        return asyncio.run(_p())
    except Exception:
        return False


SKIP = pytest.mark.skipif(not _db_ok(), reason="cardeep-pg not reachable")


async def _set_cov(c, *, coverage_pct, verdict):
    await c.execute("DELETE FROM source_coverage WHERE source_key=$1", _SRC)
    await c.execute(
        "INSERT INTO source_coverage (source_key, declared_total, captured_db, coverage_pct, verdict) "
        "VALUES ($1, 100, $2, $3, $4)",
        _SRC, int(100 * coverage_pct), coverage_pct, verdict)


def _run(coro_fn):
    async def body():
        c = await asyncpg.connect(DSN)
        tr = c.transaction()
        await tr.start()
        try:
            return await coro_fn(c)
        finally:
            await tr.rollback()
            await c.close()
    return asyncio.run(body())


@SKIP
def test_low_coverage_refuses_to_retire():
    async def body(c):
        await _set_cov(c, coverage_pct=0.50, verdict="TRUSTWORTHY")
        n, reason = await reconcile_gone(c, _SRC, _T0, min_coverage=0.9)
        assert n == 0
        assert "SKIPPED" in reason and "coverage" in reason.lower()
    _run(body)


@SKIP
def test_no_coverage_verdict_refuses_to_retire():
    async def body(c):
        await c.execute("DELETE FROM source_coverage WHERE source_key=$1", _SRC)
        n, reason = await reconcile_gone(c, _SRC, _T0, min_coverage=0.9)
        assert n == 0
        assert "SKIPPED" in reason and "no coverage verdict" in reason
    _run(body)


@SKIP
def test_refuted_coverage_refuses_to_retire():
    async def body(c):
        await _set_cov(c, coverage_pct=0.95, verdict="REFUTED")
        n, reason = await reconcile_gone(c, _SRC, _T0, min_coverage=0.9)
        assert n == 0
        assert "SKIPPED" in reason and "REFUTED" in reason
    _run(body)


@SKIP
def test_sufficient_coverage_passes_the_gate():
    # coverage >= floor + not REFUTED -> the gate does NOT short-circuit; with no vehicles for this
    # test source, it proceeds to the available-count path and reports "no available vehicles".
    async def body(c):
        await _set_cov(c, coverage_pct=0.95, verdict="TRUSTWORTHY")
        n, reason = await reconcile_gone(c, _SRC, _T0, min_coverage=0.9)
        assert n == 0
        assert "no available vehicles" in reason  # passed the coverage gate, reached the count
    _run(body)


@SKIP
def test_min_coverage_none_is_backward_compatible():
    # Without min_coverage the gate is skipped entirely (legacy behavior preserved).
    async def body(c):
        await c.execute("DELETE FROM source_coverage WHERE source_key=$1", _SRC)
        n, reason = await reconcile_gone(c, _SRC, _T0)
        assert n == 0
        assert "no available vehicles" in reason  # reached the count path, no coverage check
    _run(body)
