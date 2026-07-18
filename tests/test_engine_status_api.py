"""Tests for GET /engine/status (F5, 00-marketplace-engine.md).

Covers:
  - the pure §4 badge classification (_engine_badge) and next_run_time ISO conversion
  - the contract that ops.py's local _TICK_INTERVAL_MINUTES never drifts from the real
    pipeline.ops.scheduler.TICK_INTERVAL_MINUTES it deliberately does NOT import
  - the live endpoint: envelope shape, badge is one of the 3 §4 values, lease/uptime/
    replay_progress fields present and honestly typed (uptime_pct is None, not 0, when the
    F6 ledger has no observed history yet)

All live-DB tests connect to the real cardeep-pg at 127.0.0.1:5433 and are skipped when it is
unreachable (same guard pattern as tests/test_api_gaps.py).
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timezone

import asyncpg
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.api.main import app
from services.api.routers.ops import (
    _BADGE_DEGRADADO_MAX_SECONDS,
    _BADGE_LATIENDO_MAX_SECONDS,
    _HARVEST_LOCK_KEY,
    _TICK_INTERVAL_MINUTES,
    _engine_badge,
    _job_next_run_iso,
)


# ---------------------------------------------------------------------------
# DB connectivity guard (mirrors test_api_gaps.py)
# ---------------------------------------------------------------------------

def _db_available() -> bool:
    async def _ping() -> bool:
        try:
            conn = await asyncpg.connect(
                "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep", timeout=3,
            )
            await conn.close()
            return True
        except Exception:
            return False
    try:
        return asyncio.run(_ping())
    except Exception:
        return False


DB_AVAILABLE = _db_available()
SKIP_NO_DB = pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Contract: the local literal must never drift from the real scheduler constant.
# ---------------------------------------------------------------------------

class TestTickIntervalContract:
    def test_local_constant_matches_real_scheduler_constant(self) -> None:
        """ops.py deliberately does NOT import pipeline.ops.scheduler (sync psycopg2 +
        subprocess into an async asyncpg process) — this test is the drift guard instead."""
        from pipeline.ops.scheduler import TICK_INTERVAL_MINUTES

        assert _TICK_INTERVAL_MINUTES == TICK_INTERVAL_MINUTES

    def test_local_lock_key_matches_real_scheduler_singleton_lock(self) -> None:
        assert _HARVEST_LOCK_KEY == 0x43415244 == 1128354372

    def test_badge_boundaries_are_derived_from_tick_interval(self) -> None:
        assert _BADGE_LATIENDO_MAX_SECONDS == 2 * _TICK_INTERVAL_MINUTES * 60
        assert _BADGE_DEGRADADO_MAX_SECONDS == 24 * 3600


# ---------------------------------------------------------------------------
# _engine_badge — pure §4 classification
# ---------------------------------------------------------------------------

class TestEngineBadge:
    def test_no_lease_row_is_parado(self) -> None:
        assert _engine_badge(None) == "PARADO"

    def test_fresh_heartbeat_is_latiendo(self) -> None:
        assert _engine_badge(60.0) == "LATIENDO"  # 1 min old

    def test_just_under_30min_is_latiendo(self) -> None:
        assert _engine_badge(30 * 60 - 1) == "LATIENDO"

    def test_exactly_30min_is_degradado(self) -> None:
        """Strict '<' boundary: exactly 30min is NOT latiendo anymore."""
        assert _engine_badge(30 * 60) == "DEGRADADO"

    def test_just_under_24h_is_degradado(self) -> None:
        assert _engine_badge(24 * 3600 - 1) == "DEGRADADO"

    def test_exactly_24h_is_parado(self) -> None:
        assert _engine_badge(24 * 3600) == "PARADO"

    def test_18_days_old_is_parado(self) -> None:
        """The real 2026-06-29 outage this whole carta exists to make visible."""
        assert _engine_badge(18 * 24 * 3600) == "PARADO"


# ---------------------------------------------------------------------------
# _job_next_run_iso — apscheduler's POSIX-float storage -> ISO-8601
# ---------------------------------------------------------------------------

class TestJobNextRunIso:
    def test_none_stays_none(self) -> None:
        assert _job_next_run_iso(None) is None

    def test_float_converts_to_iso_utc(self) -> None:
        ts = datetime(2026, 7, 18, 12, 0, 0, tzinfo=timezone.utc).timestamp()
        iso = _job_next_run_iso(ts)
        assert iso == "2026-07-18T12:00:00+00:00"


# ---------------------------------------------------------------------------
# Live endpoint
# ---------------------------------------------------------------------------

class TestEngineStatusEndpoint:
    @SKIP_NO_DB
    def test_returns_200_with_envelope_shape(self, client: TestClient) -> None:
        r = client.get("/engine/status")
        assert r.status_code == 200
        body = r.json()
        assert set(body.keys()) == {"ok", "data", "error", "meta"}
        assert body["ok"] is True

    @SKIP_NO_DB
    def test_badge_is_one_of_the_three_values(self, client: TestClient) -> None:
        data = client.get("/engine/status").json()["data"]
        assert data["badge"] in ("LATIENDO", "DEGRADADO", "PARADO")

    @SKIP_NO_DB
    def test_lease_fields_present(self, client: TestClient) -> None:
        lease = client.get("/engine/status").json()["data"]["lease"]
        assert set(lease.keys()) == {"holder", "pid", "started_at", "last_heartbeat", "age_seconds"}

    @SKIP_NO_DB
    def test_jobs_is_a_list_of_id_and_next_run_time(self, client: TestClient) -> None:
        jobs = client.get("/engine/status").json()["data"]["jobs"]
        assert isinstance(jobs, list)
        for j in jobs:
            assert set(j.keys()) == {"id", "next_run_time"}

    @SKIP_NO_DB
    def test_replay_progress_shape_and_honesty_note(self, client: TestClient) -> None:
        rp = client.get("/engine/status").json()["data"]["replay_progress"]
        assert "sources_total" in rp
        assert "sources_harvested_since_holder_started" in rp
        assert "DUE al arrancar" in rp["note"]  # explicit approximation disclosure

    @SKIP_NO_DB
    def test_uptime_has_30d_and_90d_with_full_shape(self, client: TestClient) -> None:
        uptime = client.get("/engine/status").json()["data"]["uptime"]
        assert set(uptime.keys()) == {"30d", "90d"}
        for window in ("30d", "90d"):
            report = uptime[window]
            assert set(report.keys()) == {
                "requested_days", "full_window_available", "observed_from", "observed_to",
                "bucket_minutes", "buckets_total", "buckets_with_beat", "uptime_pct",
            }
        assert uptime["30d"]["requested_days"] == 30
        assert uptime["90d"]["requested_days"] == 90

    @SKIP_NO_DB
    def test_uptime_pct_is_never_a_fabricated_zero_before_first_ledger_row(self, client: TestClient) -> None:
        """Anti-alucinación guard, live check: if engine_heartbeat_log has no rows yet for the
        harvest lock, uptime_pct must be None (no data), never a fake 0%/100%."""
        async def _min_beat() -> "datetime | None":
            conn = await asyncpg.connect(
                "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep", timeout=5,
            )
            try:
                return await conn.fetchval(
                    "SELECT min(beat_at) FROM engine_heartbeat_log WHERE lock_key = $1",
                    _HARVEST_LOCK_KEY,
                )
            finally:
                await conn.close()

        observed_since = asyncio.run(_min_beat())
        uptime = client.get("/engine/status").json()["data"]["uptime"]
        if observed_since is None:
            assert uptime["30d"]["uptime_pct"] is None
            assert uptime["30d"]["full_window_available"] is False

    @SKIP_NO_DB
    def test_health_and_stats_unaffected_by_engine_status_addition(self, client: TestClient) -> None:
        """Regression: adding /engine/status must not perturb sibling endpoints in this router."""
        r_health = client.get("/health")
        assert r_health.status_code == 200
        r_sources = client.get("/sources")
        assert r_sources.status_code == 200
        r_alerts = client.get("/alerts")
        assert r_alerts.status_code == 200
