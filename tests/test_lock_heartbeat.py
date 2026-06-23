"""Unit tests for the advisory-lock heartbeat + stale-lease detection helper.

Covers the pure TTL math (the heart of stale detection) and the best-effort
psycopg2 DB layer against MagicMock connections. No live DB required (CI-safe).

Stale rule (mirrors silence_watchdog's strict "> threshold" convention):
    stale  <=>  now - last_heartbeat  >  ttl_minutes
A missing/None last_heartbeat is treated as stale. The default TTL is 6 min
(3x the 2-min heartbeat cadence).
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import psycopg2
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.ops.lock_heartbeat import (
    _DEFAULT_HEARTBEAT_MIN,
    _DEFAULT_TTL_MIN,
    _LEASE_TABLE,
    check_and_clear_stale_lease,
    heartbeat_interval_minutes,
    is_lease_stale,
    lease_ttl_minutes,
    read_lease,
    record_heartbeat,
)

UTC = timezone.utc
_NOW = datetime(2026, 6, 23, 12, 0, 0, tzinfo=UTC)
_LOCK_KEY = 0x43415244  # harvest scheduler singleton lock (scheduler.py:842)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_conn_with_row(row):
    """Build a MagicMock psycopg2 connection whose cursor.fetchone returns ``row``.

    Supports the `with conn.cursor(...) as cur:` context-manager protocol used by the
    module so the same mock works for both DictCursor reads and plain writes.
    """
    cur = MagicMock()
    cur.fetchone.return_value = row
    cur.__enter__.return_value = cur
    cur.__exit__.return_value = False
    conn = MagicMock()
    conn.cursor.return_value = cur
    return conn, cur


def _undefined_table_conn():
    """A connection whose cursor.execute raises psycopg2 UndefinedTable (pre-0054 DB)."""
    cur = MagicMock()
    cur.__enter__.return_value = cur
    cur.__exit__.return_value = False
    cur.execute.side_effect = psycopg2.errors.UndefinedTable("relation does not exist")
    conn = MagicMock()
    conn.cursor.return_value = cur
    return conn, cur


# ---------------------------------------------------------------------------
# TTL configuration
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_default_ttl_is_three_times_heartbeat():
    # Arrange / Act done at import; Assert the documented 3x relationship.
    assert _DEFAULT_TTL_MIN == 3 * _DEFAULT_HEARTBEAT_MIN
    assert _DEFAULT_HEARTBEAT_MIN == 2
    assert _DEFAULT_TTL_MIN == 6


@pytest.mark.unit
def test_ttl_and_heartbeat_defaults_when_env_unset(monkeypatch):
    monkeypatch.delenv("CARDEEP_LEASE_TTL_MIN", raising=False)
    monkeypatch.delenv("CARDEEP_LEASE_HEARTBEAT_MIN", raising=False)
    assert lease_ttl_minutes() == _DEFAULT_TTL_MIN
    assert heartbeat_interval_minutes() == _DEFAULT_HEARTBEAT_MIN


@pytest.mark.unit
def test_ttl_env_override(monkeypatch):
    monkeypatch.setenv("CARDEEP_LEASE_TTL_MIN", "15")
    assert lease_ttl_minutes() == 15


@pytest.mark.unit
@pytest.mark.parametrize("bad", ["0", "-5", "notanumber", ""])
def test_ttl_env_garbage_falls_back_to_default(monkeypatch, bad):
    monkeypatch.setenv("CARDEEP_LEASE_TTL_MIN", bad)
    assert lease_ttl_minutes() == _DEFAULT_TTL_MIN


# ---------------------------------------------------------------------------
# Pure TTL math — is_lease_stale (core stale-detection surface)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_fresh_heartbeat_is_not_stale():
    last = _NOW - timedelta(minutes=1)
    assert is_lease_stale(last, now=_NOW, ttl_minutes=6) is False


@pytest.mark.unit
def test_old_heartbeat_is_stale():
    last = _NOW - timedelta(minutes=10)
    assert is_lease_stale(last, now=_NOW, ttl_minutes=6) is True


@pytest.mark.unit
def test_heartbeat_exactly_at_ttl_is_not_yet_stale():
    # Strict boundary: age must EXCEED ttl, not merely equal it.
    last = _NOW - timedelta(minutes=6)
    assert is_lease_stale(last, now=_NOW, ttl_minutes=6) is False


@pytest.mark.unit
def test_heartbeat_one_second_past_ttl_is_stale():
    last = _NOW - timedelta(minutes=6, seconds=1)
    assert is_lease_stale(last, now=_NOW, ttl_minutes=6) is True


@pytest.mark.unit
def test_none_heartbeat_is_stale():
    # A lease row with a NULL/missing heartbeat cannot vouch for a living holder.
    assert is_lease_stale(None, now=_NOW, ttl_minutes=6) is True


@pytest.mark.unit
def test_naive_heartbeat_treated_as_utc():
    # A naive datetime must not raise a naive/aware subtraction error.
    naive_last = datetime(2026, 6, 23, 11, 50, 0)  # 10 min before _NOW, no tzinfo
    assert is_lease_stale(naive_last, now=_NOW, ttl_minutes=6) is True
    fresh_naive = datetime(2026, 6, 23, 11, 59, 0)  # 1 min before _NOW
    assert is_lease_stale(fresh_naive, now=_NOW, ttl_minutes=6) is False


@pytest.mark.unit
def test_is_lease_stale_uses_env_ttl_when_not_passed(monkeypatch):
    monkeypatch.setenv("CARDEEP_LEASE_TTL_MIN", "30")
    last = _NOW - timedelta(minutes=20)  # stale at 6, fresh at 30
    assert is_lease_stale(last, now=_NOW) is False


# ---------------------------------------------------------------------------
# record_heartbeat — best-effort UPSERT
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_record_heartbeat_executes_upsert_and_returns_true():
    conn, cur = _mock_conn_with_row(None)
    ok = record_heartbeat(conn, _LOCK_KEY, holder="harvest", pid=4321)

    assert ok is True
    assert cur.execute.call_count == 1
    sql, params = cur.execute.call_args.args
    assert "INSERT INTO scheduler_lease" in sql
    assert "ON CONFLICT (lock_key) DO UPDATE" in sql
    assert params == {"lock_key": _LOCK_KEY, "holder": "harvest", "pid": 4321}


@pytest.mark.unit
def test_record_heartbeat_defaults_pid_to_current_process():
    conn, cur = _mock_conn_with_row(None)
    record_heartbeat(conn, _LOCK_KEY, holder="discovery")
    _, params = cur.execute.call_args.args
    assert params["pid"] == os.getpid()


@pytest.mark.unit
def test_record_heartbeat_missing_table_is_best_effort():
    # Pre-0054 DB: the UPSERT must NOT raise — the daemon boots byte-identically.
    conn, cur = _undefined_table_conn()
    ok = record_heartbeat(conn, _LOCK_KEY, holder="harvest")
    assert ok is False
    conn.rollback.assert_called_once()


@pytest.mark.unit
def test_record_heartbeat_generic_db_error_is_swallowed():
    cur = MagicMock()
    cur.__enter__.return_value = cur
    cur.__exit__.return_value = False
    cur.execute.side_effect = psycopg2.OperationalError("connection reset")
    conn = MagicMock()
    conn.cursor.return_value = cur

    ok = record_heartbeat(conn, _LOCK_KEY)
    assert ok is False
    conn.rollback.assert_called_once()


# ---------------------------------------------------------------------------
# read_lease
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_read_lease_returns_dict_for_existing_row():
    last = _NOW - timedelta(minutes=2)
    started = _NOW - timedelta(hours=3)
    row = {
        "lock_key": _LOCK_KEY,
        "holder": "harvest",
        "pid": 999,
        "started_at": started,
        "last_heartbeat": last,
    }
    conn, _ = _mock_conn_with_row(row)
    result = read_lease(conn, _LOCK_KEY)

    assert result == {
        "lock_key": _LOCK_KEY,
        "holder": "harvest",
        "pid": 999,
        "started_at": started,
        "last_heartbeat": last,
    }


@pytest.mark.unit
def test_read_lease_returns_none_for_absent_row():
    conn, _ = _mock_conn_with_row(None)
    assert read_lease(conn, _LOCK_KEY) is None


@pytest.mark.unit
def test_read_lease_missing_table_returns_none_best_effort():
    conn, _ = _undefined_table_conn()
    assert read_lease(conn, _LOCK_KEY) is None
    conn.rollback.assert_called_once()


# ---------------------------------------------------------------------------
# check_and_clear_stale_lease — the pre-acquire diagnostic
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_stale_lease_detected_returns_true_and_logs_critical(caplog):
    stale_row = {
        "lock_key": _LOCK_KEY,
        "holder": "harvest",
        "pid": 13337,
        "started_at": _NOW - timedelta(hours=5),
        "last_heartbeat": _NOW - timedelta(minutes=20),  # > 6 min TTL
    }
    conn, _ = _mock_conn_with_row(stale_row)
    with caplog.at_level("CRITICAL", logger="cardeep.lock_heartbeat"):
        result = check_and_clear_stale_lease(conn, _LOCK_KEY, now=_NOW, ttl_minutes=6)

    assert result is True
    assert any("stale lease detected" in r.message for r in caplog.records)
    # We must NEVER unlock a foreign session's advisory lock.
    sql_calls = " ".join(str(c) for c in conn.cursor.return_value.execute.call_args_list)
    assert "advisory_unlock" not in sql_calls


@pytest.mark.unit
def test_fresh_lease_returns_false():
    fresh_row = {
        "lock_key": _LOCK_KEY,
        "holder": "harvest",
        "pid": 7,
        "started_at": _NOW - timedelta(hours=1),
        "last_heartbeat": _NOW - timedelta(minutes=1),  # well within TTL
    }
    conn, _ = _mock_conn_with_row(fresh_row)
    assert check_and_clear_stale_lease(conn, _LOCK_KEY, now=_NOW, ttl_minutes=6) is False


@pytest.mark.unit
def test_absent_lease_returns_false():
    # Clean start: no lease row yet -> nothing stale, proceed to acquire as usual.
    conn, _ = _mock_conn_with_row(None)
    assert check_and_clear_stale_lease(conn, _LOCK_KEY, now=_NOW, ttl_minutes=6) is False


@pytest.mark.unit
def test_missing_table_returns_false_best_effort():
    # Pre-0054 DB -> read returns None -> diagnostic is a no-op (feature inert).
    conn, _ = _undefined_table_conn()
    assert check_and_clear_stale_lease(conn, _LOCK_KEY, now=_NOW, ttl_minutes=6) is False


@pytest.mark.unit
def test_null_heartbeat_lease_is_stale():
    null_row = {
        "lock_key": _LOCK_KEY,
        "holder": "harvest",
        "pid": 1,
        "started_at": _NOW - timedelta(hours=2),
        "last_heartbeat": None,
    }
    conn, _ = _mock_conn_with_row(null_row)
    assert check_and_clear_stale_lease(conn, _LOCK_KEY, now=_NOW, ttl_minutes=6) is True
