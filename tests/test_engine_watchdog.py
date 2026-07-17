"""Unit tests for the F1 external engine watchdog (pipeline.ops.engine_watchdog).

Covers the pure classification predicate (no DB) and the mocked DB layer (dedup
INSERT/UPDATE alert contract, lease read). No live DB required (CI-safe) — mirrors
the mock pattern of test_lock_heartbeat.py / test_silence_watchdog.py.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.ops.engine_watchdog import (
    ENGINE_STALE_THRESHOLD_MINUTES,
    _ALERT_ORIGIN,
    classify_engine_status,
    fire_engine_down_alert_sync,
    read_engine_lease,
    resolve_engine_alert_if_recovered,
    run_watchdog_cycle,
)

UTC = timezone.utc
_NOW = datetime(2026, 7, 17, 12, 0, 0, tzinfo=UTC)


# ---------------------------------------------------------------------------
# Pure classification — boundary contract (mirrors silence_watchdog's "> threshold")
# ---------------------------------------------------------------------------

class TestClassifyEngineStatus:
    def test_none_heartbeat_is_sin_lease(self) -> None:
        assert classify_engine_status(None, now=_NOW) == "SIN_LEASE"

    def test_fresh_heartbeat_is_latiendo(self) -> None:
        beat = _NOW - timedelta(minutes=10)
        assert classify_engine_status(beat, now=_NOW) == "LATIENDO"

    def test_exactly_at_threshold_is_still_latiendo(self) -> None:
        """Exactly 30min old: strict '>' means the boundary itself is NOT stale."""
        beat = _NOW - timedelta(minutes=ENGINE_STALE_THRESHOLD_MINUTES)
        assert classify_engine_status(beat, now=_NOW) == "LATIENDO"

    def test_just_past_threshold_is_degradado_parado(self) -> None:
        beat = _NOW - timedelta(minutes=ENGINE_STALE_THRESHOLD_MINUTES, seconds=1)
        assert classify_engine_status(beat, now=_NOW) == "DEGRADADO_PARADO"

    def test_18_days_old_is_degradado_parado(self) -> None:
        """The real 2026-06-29 outage this watchdog exists to catch."""
        beat = _NOW - timedelta(days=18)
        assert classify_engine_status(beat, now=_NOW) == "DEGRADADO_PARADO"

    def test_naive_datetime_treated_as_utc(self) -> None:
        beat = (_NOW - timedelta(minutes=5)).replace(tzinfo=None)
        assert classify_engine_status(beat, now=_NOW) == "LATIENDO"

    def test_custom_threshold_override(self) -> None:
        beat = _NOW - timedelta(minutes=5)
        assert classify_engine_status(beat, now=_NOW, threshold_minutes=1) == "DEGRADADO_PARADO"


# ---------------------------------------------------------------------------
# Mocked DB layer — lease read
# ---------------------------------------------------------------------------

class TestReadEngineLease:
    def test_returns_dict_when_row_present(self) -> None:
        row = {
            "lock_key": 0x43415244,
            "holder": "harvest",
            "pid": 34712,
            "started_at": _NOW,
            "last_heartbeat": _NOW,
        }
        cur = MagicMock()
        cur.fetchone.return_value = row
        cur.__enter__.return_value = cur
        cur.__exit__.return_value = False
        conn = MagicMock()
        conn.cursor.return_value = cur

        result = read_engine_lease(conn)
        assert result == row

    def test_returns_none_when_no_row(self) -> None:
        cur = MagicMock()
        cur.fetchone.return_value = None
        cur.__enter__.return_value = cur
        cur.__exit__.return_value = False
        conn = MagicMock()
        conn.cursor.return_value = cur

        assert read_engine_lease(conn) is None


# ---------------------------------------------------------------------------
# Mocked DB layer — dedup-aware alert fire/resolve
# ---------------------------------------------------------------------------

class TestFireEngineDownAlert:
    def test_inserts_new_alert_when_none_open(self) -> None:
        cur = MagicMock()
        cur.fetchone.side_effect = [None, (99,)]  # SELECT: none open; INSERT ... RETURNING id
        cur.__enter__.return_value = cur
        cur.__exit__.return_value = False
        conn = MagicMock()
        conn.cursor.return_value = cur

        alert_id = fire_engine_down_alert_sync(
            conn, age_minutes=45.0, last_heartbeat=_NOW, holder="harvest", pid=34712,
        )

        assert alert_id == 99
        insert_call = [c for c in cur.execute.call_args_list if "INSERT INTO alert" in c.args[0]]
        assert len(insert_call) == 1
        assert insert_call[0].args[1][0] == _ALERT_ORIGIN
        assert insert_call[0].args[1][1] == "critical"
        conn.commit.assert_called_once()

    def test_updates_existing_open_alert_instead_of_duplicating(self) -> None:
        cur = MagicMock()
        cur.fetchone.side_effect = [(7,)]  # SELECT finds an existing open alert id=7
        cur.__enter__.return_value = cur
        cur.__exit__.return_value = False
        conn = MagicMock()
        conn.cursor.return_value = cur

        alert_id = fire_engine_down_alert_sync(
            conn, age_minutes=60.0, last_heartbeat=_NOW, holder="harvest", pid=34712,
        )

        assert alert_id == 7
        update_calls = [c for c in cur.execute.call_args_list if "UPDATE alert" in c.args[0]]
        assert len(update_calls) == 1
        insert_calls = [c for c in cur.execute.call_args_list if "INSERT INTO alert" in c.args[0]]
        assert len(insert_calls) == 0

    def test_missing_lease_message_names_it_explicitly(self) -> None:
        cur = MagicMock()
        cur.fetchone.side_effect = [None, (5,)]
        cur.__enter__.return_value = cur
        cur.__exit__.return_value = False
        conn = MagicMock()
        conn.cursor.return_value = cur

        fire_engine_down_alert_sync(
            conn, age_minutes=float("inf"), last_heartbeat=None, holder=None, pid=None,
        )
        insert_call = [c for c in cur.execute.call_args_list if "INSERT INTO alert" in c.args[0]]
        message = insert_call[0].args[1][2]
        assert "MISSING" in message


class TestResolveEngineAlertIfRecovered:
    def test_returns_true_when_a_row_was_closed(self) -> None:
        cur = MagicMock()
        cur.rowcount = 1
        cur.__enter__.return_value = cur
        cur.__exit__.return_value = False
        conn = MagicMock()
        conn.cursor.return_value = cur

        assert resolve_engine_alert_if_recovered(conn) is True
        conn.commit.assert_called_once()

    def test_returns_false_when_nothing_to_close(self) -> None:
        cur = MagicMock()
        cur.rowcount = 0
        cur.__enter__.return_value = cur
        cur.__exit__.return_value = False
        conn = MagicMock()
        conn.cursor.return_value = cur

        assert resolve_engine_alert_if_recovered(conn) is False


# ---------------------------------------------------------------------------
# run_watchdog_cycle — DB-unreachable path (the "el apagón de la DB también debe
# verse" requirement): must write the external log WITHOUT a live DB connection.
# ---------------------------------------------------------------------------

class TestRunWatchdogCycleDbUnreachable:
    def test_writes_external_log_when_db_unreachable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "engine_watchdog.log"
            # Port 1 on localhost: nothing listens there — guaranteed connection refusal,
            # no live DB required for this test to be deterministic.
            record = run_watchdog_cycle(
                dsn="host=127.0.0.1 port=1 dbname=x user=x password=x connect_timeout=1",
                log_path=log_path,
            )
            assert record["status"] == "DB_UNREACHABLE"
            assert log_path.exists()
            lines = log_path.read_text(encoding="utf-8").strip().splitlines()
            assert len(lines) == 1
            logged = json.loads(lines[0])
            assert logged["status"] == "DB_UNREACHABLE"

    def test_threshold_override_is_reflected_in_dry_run_record(self) -> None:
        """F1 drill acceleration: --threshold-minutes overrides the 30-min default for one
        call without touching the module constant (production default stays untouched)."""
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "engine_watchdog.log"
            record = run_watchdog_cycle(
                dsn="host=127.0.0.1 port=1 dbname=x user=x password=x connect_timeout=1",
                log_path=log_path,
                dry_run=True,
                threshold_minutes=2,
            )
            # DB-unreachable path doesn't reach the threshold field — this asserts the plumbing
            # doesn't raise/break with the new kwarg; the classification-level boundary is
            # covered by TestClassifyEngineStatus.test_custom_threshold_override.
            assert record["status"] == "DB_UNREACHABLE"

    def test_dry_run_writes_no_log_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "engine_watchdog.log"
            run_watchdog_cycle(
                dsn="host=127.0.0.1 port=1 dbname=x user=x password=x connect_timeout=1",
                log_path=log_path,
                dry_run=True,
            )
            assert not log_path.exists()
