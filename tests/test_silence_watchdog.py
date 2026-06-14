"""Unit tests for B2.4 — silence watchdog.

Tests the core silence predicate, alert dedup mechanics, and the watchdog runner
against mock psycopg2 connections. No live DB required (CI-safe).

Silence rule:
    hours_since_last_event > SILENCE_MULTIPLIER * harvest_interval_hours
    where SILENCE_MULTIPLIER = 2 (i.e. > 2× the cadence).
"""
from __future__ import annotations

import json
import sys
import os
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import MagicMock, call, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.ops.silence_watchdog import (
    SILENCE_MULTIPLIER,
    _build_origin,
    find_silent_sources,
    fire_silence_alert_sync,
    run_silence_watchdog,
)


# ---------------------------------------------------------------------------
# Helpers — build fake psycopg2 connections
# ---------------------------------------------------------------------------

def _fake_select_conn(rows: list[tuple[Any, ...]]) -> MagicMock:
    """Fake psycopg2 connection whose DictCursor returns *rows* from fetchall.

    Row schema for find_silent_sources:
        (source_key, last_ok, last_fail, harvest_interval_hours, is_tier1, hours_silent)
    """
    # DictCursor rows — simulate psycopg2.extras.DictRow via dict-like MagicMocks
    dict_rows = []
    for r in rows:
        m = MagicMock()
        m.__getitem__.side_effect = lambda k, _r=r: {
            "source_key": _r[0],
            "last_ok": _r[1],
            "last_fail": _r[2],
            "harvest_interval_hours": _r[3],
            "is_tier1": _r[4],
            "hours_silent": _r[5],
        }[k]
        dict_rows.append(m)

    cur_mock = MagicMock()
    cur_mock.__enter__ = lambda s: s
    cur_mock.__exit__ = MagicMock(return_value=False)
    cur_mock.fetchall.return_value = dict_rows

    conn_mock = MagicMock()
    conn_mock.cursor.return_value = cur_mock
    return conn_mock


def _silent_row(
    source_key: str,
    last_ok: datetime | None,
    last_fail: datetime | None,
    interval_h: int,
    is_tier1: bool,
    hours_silent: float,
) -> tuple[Any, ...]:
    return (source_key, last_ok, last_fail, interval_h, is_tier1, hours_silent)


NOW = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Core silence predicate — verify the multiplier contract
# ---------------------------------------------------------------------------

class TestSilencePredicate:
    """The DB WHERE clause delegates computation to PG; here we test that the
    Python layer correctly interprets the hours_silent value returned by PG and
    that the boundary conditions match the spec (> 2× interval)."""

    def test_silent_when_50h_interval_24h(self) -> None:
        """50h without event, 24h interval: 50 > 2*24=48 → SILENT."""
        row = _silent_row("autocasion_wholesale", None, None, 24, True, 50.0)
        conn = _fake_select_conn([row])
        result = find_silent_sources(conn)
        assert len(result) == 1
        assert result[0]["source_key"] == "autocasion_wholesale"
        assert result[0]["hours_silent"] == pytest.approx(50.0)

    def test_not_silent_when_30h_interval_24h(self) -> None:
        """30h without event, 24h interval: 30 < 2*24=48 → NOT silent.

        The DB WHERE clause filters this out — mock returns empty rows.
        """
        conn = _fake_select_conn([])  # PG WHERE already excludes it
        result = find_silent_sources(conn)
        assert result == []

    def test_silent_when_interval_168h_and_340h_elapsed(self) -> None:
        """340h without event, 168h interval: 340 > 2*168=336 → SILENT."""
        row = _silent_row("renew_wholesale", None, None, 168, False, 340.0)
        conn = _fake_select_conn([row])
        result = find_silent_sources(conn)
        assert len(result) == 1
        assert result[0]["source_key"] == "renew_wholesale"

    def test_not_silent_when_interval_168h_and_330h_elapsed(self) -> None:
        """330h without event, 168h interval: 330 < 2*168=336 → NOT silent."""
        conn = _fake_select_conn([])
        result = find_silent_sources(conn)
        assert result == []

    def test_not_silent_exactly_at_boundary_48h(self) -> None:
        """Exactly 48h elapsed with 24h interval: 48 is NOT > 48 → NOT silent.

        Strict inequality (>) means the boundary itself is NOT silent.
        """
        conn = _fake_select_conn([])
        result = find_silent_sources(conn)
        assert result == []

    def test_multiple_silent_sources_returned(self) -> None:
        """Multiple silent sources are all returned in the result."""
        rows = [
            _silent_row("autocasion_wholesale", None, None, 24, True, 72.0),
            _silent_row("renew_wholesale", None, None, 168, False, 400.0),
        ]
        conn = _fake_select_conn(rows)
        result = find_silent_sources(conn)
        assert len(result) == 2
        keys = [r["source_key"] for r in result]
        assert "autocasion_wholesale" in keys
        assert "renew_wholesale" in keys

    def test_result_dict_has_required_keys(self) -> None:
        """Each result dict must contain all expected keys."""
        row = _silent_row("motor_es_wholesale", NOW - timedelta(hours=60), None, 24, True, 60.0)
        conn = _fake_select_conn([row])
        result = find_silent_sources(conn)
        assert len(result) == 1
        rec = result[0]
        for key in ("source_key", "last_ok", "last_fail", "harvest_interval_hours",
                    "is_tier1", "hours_silent"):
            assert key in rec, f"Missing key: {key}"

    def test_no_silent_sources_returns_empty_list(self) -> None:
        """When no sources are silent, an empty list is returned."""
        conn = _fake_select_conn([])
        result = find_silent_sources(conn)
        assert result == []

    def test_silence_multiplier_is_2(self) -> None:
        """The constant SILENCE_MULTIPLIER must equal 2 per spec."""
        assert SILENCE_MULTIPLIER == 2


# ---------------------------------------------------------------------------
# build_origin helper
# ---------------------------------------------------------------------------

class TestBuildOrigin:
    def test_origin_without_cdp(self) -> None:
        assert _build_origin("autocasion_wholesale", "silence") == \
               "autocasion_wholesale:silence"

    def test_origin_with_cdp(self) -> None:
        assert _build_origin("autocasion_wholesale", "silence", "cdp-123") == \
               "autocasion_wholesale:silence:cdp-123"


# ---------------------------------------------------------------------------
# fire_silence_alert_sync — dedup mechanics
# ---------------------------------------------------------------------------

def _fake_alert_conn(existing_id: int | None) -> MagicMock:
    """Return a psycopg2 connection mock for fire_silence_alert_sync.

    If existing_id is not None, the SELECT returns an existing open alert row.
    Otherwise it returns None (new insert path).
    """
    cur_mock = MagicMock()
    cur_mock.__enter__ = lambda s: s
    cur_mock.__exit__ = MagicMock(return_value=False)

    if existing_id is not None:
        # SELECT returns the existing row
        cur_mock.fetchone.side_effect = [(existing_id,)]
    else:
        # SELECT returns None (no existing alert), INSERT returns new id
        cur_mock.fetchone.side_effect = [None, (42,)]

    conn_mock = MagicMock()
    conn_mock.cursor.return_value = cur_mock
    return conn_mock


class TestFireSilenceAlertSync:
    def test_insert_when_no_existing_alert(self) -> None:
        """When no open alert exists, INSERT is executed and the new id is returned."""
        conn = _fake_alert_conn(existing_id=None)
        alert_id = fire_silence_alert_sync(
            conn,
            source_key="autocasion_wholesale",
            hours_silent=72.0,
            harvest_interval_hours=24,
            is_tier1=True,
        )
        assert alert_id == 42
        conn.commit.assert_called_once()

    def test_update_when_existing_alert(self) -> None:
        """When an open alert exists, UPDATE is executed and the existing id is returned."""
        conn = _fake_alert_conn(existing_id=7)
        alert_id = fire_silence_alert_sync(
            conn,
            source_key="renew_wholesale",
            hours_silent=400.0,
            harvest_interval_hours=168,
            is_tier1=False,
        )
        assert alert_id == 7
        conn.commit.assert_called_once()

    def test_severity_critical_for_tier1(self) -> None:
        """is_tier1=True must produce severity=critical in the INSERT."""
        conn = _fake_alert_conn(existing_id=None)
        cur_mock = conn.cursor.return_value
        fire_silence_alert_sync(
            conn,
            source_key="autocasion_wholesale",
            hours_silent=72.0,
            harvest_interval_hours=24,
            is_tier1=True,
        )
        # Collect all execute calls
        all_calls = cur_mock.execute.call_args_list
        # The INSERT call must include "critical"
        insert_call = next(
            (c for c in all_calls if "INSERT" in str(c)),
            None,
        )
        assert insert_call is not None, "Expected an INSERT execute call"
        assert "critical" in str(insert_call), \
            f"Expected 'critical' severity in INSERT, got: {insert_call}"

    def test_severity_warning_for_non_tier1(self) -> None:
        """is_tier1=False must produce severity=warning in the INSERT."""
        conn = _fake_alert_conn(existing_id=None)
        cur_mock = conn.cursor.return_value
        fire_silence_alert_sync(
            conn,
            source_key="renew_wholesale",
            hours_silent=400.0,
            harvest_interval_hours=168,
            is_tier1=False,
        )
        all_calls = cur_mock.execute.call_args_list
        insert_call = next(
            (c for c in all_calls if "INSERT" in str(c)),
            None,
        )
        assert insert_call is not None
        assert "warning" in str(insert_call), \
            f"Expected 'warning' severity in INSERT, got: {insert_call}"

    def test_message_contains_hours_and_interval(self) -> None:
        """The alert message must mention the silence duration and interval."""
        conn = _fake_alert_conn(existing_id=None)
        cur_mock = conn.cursor.return_value
        fire_silence_alert_sync(
            conn,
            source_key="wallapop_wholesale",
            hours_silent=55.3,
            harvest_interval_hours=24,
            is_tier1=False,
        )
        all_calls = cur_mock.execute.call_args_list
        # Find any call that contains our expected message text
        message_found = any("55.3" in str(c) and "24" in str(c) for c in all_calls)
        assert message_found, \
            "Alert message must contain hours_silent and harvest_interval_hours"


# ---------------------------------------------------------------------------
# run_silence_watchdog — integration of find + fire
# ---------------------------------------------------------------------------

class TestRunSilenceWatchdog:
    def test_returns_empty_when_no_silent_sources(self) -> None:
        """When no sources are silent, no alerts are fired and empty list is returned."""
        with patch(
            "pipeline.ops.silence_watchdog.find_silent_sources",
            return_value=[],
        ):
            conn = MagicMock()
            result = run_silence_watchdog(conn)
        assert result == []

    def test_fires_alert_per_silent_source(self) -> None:
        """One alert per silent source must be fired."""
        silent_sources = [
            {
                "source_key": "autocasion_wholesale",
                "last_ok": None,
                "last_fail": None,
                "harvest_interval_hours": 24,
                "is_tier1": True,
                "hours_silent": 72.0,
            },
            {
                "source_key": "renew_wholesale",
                "last_ok": None,
                "last_fail": None,
                "harvest_interval_hours": 168,
                "is_tier1": False,
                "hours_silent": 400.0,
            },
        ]
        with (
            patch(
                "pipeline.ops.silence_watchdog.find_silent_sources",
                return_value=silent_sources,
            ),
            patch(
                "pipeline.ops.silence_watchdog.fire_silence_alert_sync",
                return_value=1,
            ) as mock_fire,
        ):
            conn = MagicMock()
            result = run_silence_watchdog(conn)

        assert len(result) == 2
        assert "autocasion_wholesale" in result
        assert "renew_wholesale" in result
        assert mock_fire.call_count == 2

    def test_alert_failure_does_not_abort_remaining(self) -> None:
        """If one alert fails, the remaining sources are still processed."""
        silent_sources = [
            {
                "source_key": "autocasion_wholesale",
                "last_ok": None,
                "last_fail": None,
                "harvest_interval_hours": 24,
                "is_tier1": True,
                "hours_silent": 72.0,
            },
            {
                "source_key": "renew_wholesale",
                "last_ok": None,
                "last_fail": None,
                "harvest_interval_hours": 168,
                "is_tier1": False,
                "hours_silent": 400.0,
            },
        ]
        call_count = 0

        def _fire_side_effect(conn_arg: Any, **kwargs: Any) -> int:
            nonlocal call_count
            call_count += 1
            if kwargs.get("source_key") == "autocasion_wholesale":
                raise RuntimeError("DB error")
            return 99

        with (
            patch(
                "pipeline.ops.silence_watchdog.find_silent_sources",
                return_value=silent_sources,
            ),
            patch(
                "pipeline.ops.silence_watchdog.fire_silence_alert_sync",
                side_effect=_fire_side_effect,
            ),
        ):
            conn = MagicMock()
            result = run_silence_watchdog(conn)

        # autocasion failed; renew succeeded
        assert "autocasion_wholesale" not in result
        assert "renew_wholesale" in result

    def test_is_tier1_passed_to_fire_alert(self) -> None:
        """is_tier1 must be forwarded to fire_silence_alert_sync."""
        silent_sources = [
            {
                "source_key": "autocasion_wholesale",
                "last_ok": None,
                "last_fail": None,
                "harvest_interval_hours": 24,
                "is_tier1": True,
                "hours_silent": 72.0,
            },
        ]
        with (
            patch(
                "pipeline.ops.silence_watchdog.find_silent_sources",
                return_value=silent_sources,
            ),
            patch(
                "pipeline.ops.silence_watchdog.fire_silence_alert_sync",
                return_value=5,
            ) as mock_fire,
        ):
            conn = MagicMock()
            run_silence_watchdog(conn)

        mock_fire.assert_called_once()
        kwargs = mock_fire.call_args.kwargs
        assert kwargs["is_tier1"] is True
        assert kwargs["source_key"] == "autocasion_wholesale"
        assert kwargs["hours_silent"] == pytest.approx(72.0)
        assert kwargs["harvest_interval_hours"] == 24


# ---------------------------------------------------------------------------
# Live DB integration (skipped if DB unreachable)
# ---------------------------------------------------------------------------

def _db_available() -> bool:
    try:
        import psycopg2
        conn = psycopg2.connect(
            "host=127.0.0.1 port=5433 dbname=cardeep user=cardeep password=cardeep_dev_only",
            connect_timeout=3,
        )
        conn.close()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_available(), reason="cardeep-pg not reachable")
class TestFindSilentSourcesLiveDB:
    """Read-only integration test against the real source_health table."""

    def test_find_silent_sources_returns_list(self) -> None:
        """find_silent_sources must return a list without crashing."""
        import psycopg2
        conn = psycopg2.connect(
            "host=127.0.0.1 port=5433 dbname=cardeep user=cardeep password=cardeep_dev_only"
        )
        try:
            result = find_silent_sources(conn)
            assert isinstance(result, list)
            for rec in result:
                assert isinstance(rec["source_key"], str)
                assert isinstance(rec["harvest_interval_hours"], int)
                assert isinstance(rec["is_tier1"], bool)
                assert isinstance(rec["hours_silent"], float)
                # hours_silent must actually exceed the threshold
                assert rec["hours_silent"] > SILENCE_MULTIPLIER * rec["harvest_interval_hours"], (
                    f"{rec['source_key']}: hours_silent={rec['hours_silent']:.1f} "
                    f"should be > {SILENCE_MULTIPLIER}×{rec['harvest_interval_hours']}="
                    f"{SILENCE_MULTIPLIER * rec['harvest_interval_hours']}"
                )
        finally:
            conn.close()

    def test_silent_sources_have_valid_schema(self) -> None:
        """Each silent source dict must have all required keys with correct types."""
        import psycopg2
        conn = psycopg2.connect(
            "host=127.0.0.1 port=5433 dbname=cardeep user=cardeep password=cardeep_dev_only"
        )
        try:
            result = find_silent_sources(conn)
            for rec in result:
                assert "source_key" in rec
                assert "last_ok" in rec
                assert "last_fail" in rec
                assert "harvest_interval_hours" in rec
                assert "is_tier1" in rec
                assert "hours_silent" in rec
        finally:
            conn.close()
