"""Unit tests for the scheduler crash-before-record_run safety net (green-review H7/M5).

_record_crash_if_unrecorded records a failure to source_health ONLY when the connector did not
write its own harvest_run this cycle — detected via the pre-launch harvest_run id high-water.
These tests mock the asyncpg connection + record_run, so they need no live DB and assert the
double-count guard deterministically.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

from pipeline.ops import scheduler


def _mock_conn(newest: int) -> AsyncMock:
    conn = AsyncMock()
    conn.fetchval = AsyncMock(return_value=newest)
    conn.close = AsyncMock()
    return conn


def test_records_when_connector_did_not_record():
    # newest harvest_run id == pre_max_id → no new row appeared → the connector crashed before
    # its own record_run → the scheduler MUST record the failure.
    conn = _mock_conn(newest=5)
    with (
        patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
        patch("pipeline.ops.health.record_run", new=AsyncMock()) as rr,
    ):
        scheduler._record_crash_if_unrecorded("src-x", exit_code=-1, pre_max_id=5)
    rr.assert_awaited_once()
    _, kwargs = rr.call_args
    assert kwargs.get("ok") is False
    assert "exited -1" in kwargs.get("error", "")


def test_skips_when_connector_recorded():
    # newest harvest_run id > pre_max_id → the connector wrote its own outcome → the scheduler
    # must NOT record (no double-count of consecutive_fails / breaker trips).
    conn = _mock_conn(newest=7)
    with (
        patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
        patch("pipeline.ops.health.record_run", new=AsyncMock()) as rr,
    ):
        scheduler._record_crash_if_unrecorded("src-x", exit_code=1, pre_max_id=5)
    rr.assert_not_awaited()


def test_records_unconditionally_when_high_water_unknown():
    # pre_max_id is None (the high-water query failed) → record unconditionally: better an extra
    # alert than a silently-swallowed crash.
    conn = _mock_conn(newest=999)  # must not even be consulted
    with (
        patch("asyncpg.connect", new=AsyncMock(return_value=conn)),
        patch("pipeline.ops.health.record_run", new=AsyncMock()) as rr,
    ):
        scheduler._record_crash_if_unrecorded("src-x", exit_code=-2, pre_max_id=None)
    rr.assert_awaited_once()


def test_recorder_never_raises_on_db_error():
    # A failure opening the connection must be swallowed+logged, never bubble into heartbeat_tick.
    with (
        patch("asyncpg.connect", new=AsyncMock(side_effect=OSError("no db"))),
        patch("pipeline.ops.health.record_run", new=AsyncMock()) as rr,
    ):
        scheduler._record_crash_if_unrecorded("src-x", exit_code=-1, pre_max_id=5)  # must not raise
    rr.assert_not_awaited()
