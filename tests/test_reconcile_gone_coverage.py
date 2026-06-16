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


_SRC_INTEG = "test-record-run-gone-integ"


@SKIP
def test_record_run_wires_reconcile_gone_when_run_started_at_given():
    # The central integration: record_run(ok, declared_total, run_started_at) records coverage then
    # invokes reconcile_gone. This test source owns no vehicles -> captured_db=0 -> coverage 0 < floor
    # -> reconcile_gone SKIPS on its coverage gate (no retirement). The point: record_run wires through
    # to reconcile_gone without crashing, and retires nothing on an incomplete/zero-coverage harvest.
    from pipeline.ops.health import record_run

    async def body(c):
        await c.execute("DELETE FROM source_coverage WHERE source_key=$1", _SRC_INTEG)
        out = await record_run(c, _SRC_INTEG, ok=True, rows=5, declared_total=100,
                               captured_distinct=50, run_started_at=_T0)
        assert out is not None  # completed; reconcile_gone was invoked + coverage-gated, no exception
        # No vehicles exist for this source, so nothing could be retired regardless.
        gone = await c.fetchval(
            "SELECT count(*) FROM vehicle_event WHERE event_type='GONE' "
            "AND entity_ulid IN (SELECT entity_ulid FROM entity_source WHERE source_key=$1)",
            _SRC_INTEG)
        assert gone == 0
    _run(body)


@SKIP
def test_prior_last_ok_fallback_retires_stale_vehicle_end_to_end():
    # The method improvement: with NO explicit run_started_at, record_run falls back to the prior
    # source_health.last_ok as the "not re-seen" boundary, so GONE auto-activates for any coverage-
    # instrumented source. Full chain: a stale vehicle (last_seen 10d ago) + prior last_ok 5d ago +
    # a complete harvest (declared=captured=1 -> coverage 1.0 >= floor) -> the vehicle is retired.
    from pipeline.ids import ulid
    from pipeline.ops.health import record_run

    eulid = ulid()
    vulid = ulid()

    async def body(c):
        await c.execute("DELETE FROM source_coverage WHERE source_key=$1", _SRC_INTEG)
        await c.execute(
            "INSERT INTO entity (entity_ulid, cdp_code, kind, status, province_code) "
            "VALUES ($1,$2,'compraventa','active','28')", eulid, "CDP-ES-28-TESTGN01")
        await c.execute(
            "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,'t')",
            eulid, _SRC_INTEG)
        await c.execute(
            "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, status, last_seen, price) "
            "VALUES ($1,$2,'http://t/gone','available', now() - interval '10 days', 1000)",
            vulid, eulid)
        await c.execute(
            "INSERT INTO source_health (source_key, last_ok, status) "
            "VALUES ($1, now() - interval '5 days', 'healthy') "
            "ON CONFLICT (source_key) DO UPDATE SET last_ok = EXCLUDED.last_ok", _SRC_INTEG)

        # declared_total=1 matches the 1 captured vehicle -> coverage 1.0 >= 0.9; no run_started_at.
        out = await record_run(c, _SRC_INTEG, ok=True, rows=1, declared_total=1,
                               captured_distinct=1)
        assert out is not None
        # The stale vehicle (last_seen 10d < prior last_ok 5d) was retired via the prior_last_ok boundary.
        status = await c.fetchval("SELECT status FROM vehicle WHERE vehicle_ulid=$1", vulid)
        assert status == "gone", f"expected gone, got {status}"
        gone = await c.fetchval(
            "SELECT count(*) FROM vehicle_event WHERE vehicle_ulid=$1 AND event_type='GONE'", vulid)
        assert gone == 1
    _run(body)


@SKIP
def test_first_run_no_prior_last_ok_skips_gone():
    # First-ever run (no prior source_health row) -> prior_last_ok is None -> no boundary -> GONE
    # skipped (nothing to compare against yet). Backward-compatible for never-run sources.
    from pipeline.ops.health import record_run

    async def body(c):
        await c.execute("DELETE FROM source_health WHERE source_key=$1", _SRC_INTEG)
        await c.execute("DELETE FROM source_coverage WHERE source_key=$1", _SRC_INTEG)
        out = await record_run(c, _SRC_INTEG, ok=True, rows=5, declared_total=100,
                               captured_distinct=50)
        assert out is not None
    _run(body)
