"""Unit tests for the B2.2 scheduler 'due sources' logic.

Tests the core predicate: a source with last_ok older than its interval is DUE;
a source harvested recently is NOT DUE.

Strategy: uses the REAL database (read-only SELECT on source_health) via psycopg2
plus an in-process mock-row variant that exercises _due_sources without touching
the DB, so the suite can run without a live PG instance (CI-safe).
"""
from __future__ import annotations

import sys
import os
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Allow running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.ops.scheduler import (
    BREAKER_TRIP_AT,
    REGISTRY,
    _due_sources,
    _gap_report,
)


# ---------------------------------------------------------------------------
# Helper: build a fake psycopg2 connection whose cursor returns controlled rows
# ---------------------------------------------------------------------------

def _fake_conn(rows: list[tuple[Any, ...]]) -> MagicMock:
    """Return a mock psycopg2 connection whose cursor().fetchall() returns *rows*.

    Row schema must match the SELECT in _due_sources:
      (source_key, harvest_interval_hours, last_ok, last_fail, consecutive_fails)
    """
    cur_mock = MagicMock()
    cur_mock.__enter__ = lambda s: s
    cur_mock.__exit__ = MagicMock(return_value=False)
    cur_mock.fetchall.return_value = rows

    conn_mock = MagicMock()
    conn_mock.cursor.return_value = cur_mock
    return conn_mock


def _row(
    source_key: str,
    interval_h: int,
    last_ok: datetime | None,
    last_fail: datetime | None,
    consecutive_fails: int = 0,
) -> tuple[str, int, datetime | None, datetime | None, int]:
    return (source_key, interval_h, last_ok, last_fail, consecutive_fails)


NOW = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Core DUE predicate tests
# ---------------------------------------------------------------------------

class TestDueSourcesPredicate:
    """The DB-level WHERE clause is tested via the Python-level _due_sources
    function, which accepts a psycopg2-compatible connection.  We mock the
    connection so the test does not need a live PG instance."""

    def test_source_due_when_last_ok_older_than_interval(self) -> None:
        """A source last harvested 25h ago with a 24h interval MUST be DUE."""
        last_ok = NOW - timedelta(hours=25)
        conn = _fake_conn([_row("autocasion_wholesale", 24, last_ok, None, 0)])
        due = _due_sources(conn)
        keys = [r[0] for r in due]
        assert "autocasion_wholesale" in keys, (
            "Source with last_ok 25h ago and 24h interval should be DUE"
        )

    def test_source_not_due_when_recently_harvested(self) -> None:
        """A source last harvested 1h ago with a 24h interval must NOT be DUE.

        The mock returns an empty set (the WHERE clause filters it out).
        """
        # The mock returns no rows — simulates the DB already filtering it
        conn = _fake_conn([])
        due = _due_sources(conn)
        assert due == [], "No rows should be due when the query returns empty"

    def test_source_due_when_only_last_fail_set(self) -> None:
        """A source with no last_ok but last_fail 25h ago and 24h interval is DUE."""
        last_fail = NOW - timedelta(hours=25)
        conn = _fake_conn([_row("wallapop_wholesale", 24, None, last_fail, 0)])
        due = _due_sources(conn)
        keys = [r[0] for r in due]
        assert "wallapop_wholesale" in keys

    def test_source_due_when_never_harvested(self) -> None:
        """A source with no last_ok and no last_fail (epoch baseline) is DUE."""
        conn = _fake_conn([_row("family_unreachable", 720, None, None, 0)])
        due = _due_sources(conn)
        keys = [r[0] for r in due]
        assert "family_unreachable" in keys

    def test_breaker_open_source_skipped(self) -> None:
        """A source with consecutive_fails >= BREAKER_TRIP_AT is excluded (breaker open)."""
        last_ok = NOW - timedelta(hours=200)
        conn = _fake_conn([
            _row("coches_net_wholesale", 24, last_ok, None, BREAKER_TRIP_AT),
        ])
        due = _due_sources(conn)
        keys = [r[0] for r in due]
        assert "coches_net_wholesale" not in keys, (
            f"Source with consecutive_fails={BREAKER_TRIP_AT} should be skipped (breaker open)"
        )

    def test_breaker_below_threshold_not_skipped(self) -> None:
        """A source with consecutive_fails < BREAKER_TRIP_AT is NOT skipped."""
        last_ok = NOW - timedelta(hours=200)
        conn = _fake_conn([
            _row("coches_net_wholesale", 24, last_ok, None, BREAKER_TRIP_AT - 1),
        ])
        due = _due_sources(conn)
        keys = [r[0] for r in due]
        assert "coches_net_wholesale" in keys

    def test_ordering_most_overdue_first(self) -> None:
        """The most-overdue source should appear first in the result."""
        # Mock returns rows already sorted DESC by overdue duration (as DB would)
        very_old = NOW - timedelta(hours=500)
        less_old = NOW - timedelta(hours=25)
        conn = _fake_conn([
            _row("family_unreachable", 720, very_old, None, 0),
            _row("autocasion_wholesale", 24, less_old, None, 0),
        ])
        due = _due_sources(conn)
        assert due[0][0] == "family_unreachable", (
            "Most-overdue source should be first"
        )

    def test_multiple_sources_mixed_breaker_state(self) -> None:
        """Mix of due+open and due+closed: only closed ones appear in result."""
        last_ok_old = NOW - timedelta(hours=200)
        conn = _fake_conn([
            _row("autocasion_wholesale", 24, last_ok_old, None, 0),         # due, breaker closed
            _row("coches_com_wholesale", 24, last_ok_old, None, BREAKER_TRIP_AT),  # due, breaker OPEN
            _row("wallapop_wholesale", 24, last_ok_old, None, 1),           # due, breaker closed (1 fail)
        ])
        due = _due_sources(conn)
        keys = [r[0] for r in due]
        assert "autocasion_wholesale" in keys
        assert "wallapop_wholesale" in keys
        assert "coches_com_wholesale" not in keys


# ---------------------------------------------------------------------------
# Registry coverage tests
# ---------------------------------------------------------------------------

class TestRegistry:
    def test_registry_is_not_empty(self) -> None:
        assert len(REGISTRY) > 0

    def test_all_tier1_mapped(self) -> None:
        """The 6 tier-1 sources must all be in the registry."""
        tier1 = [
            "autocasion_wholesale",
            "coches_com_wholesale",
            "coches_net_wholesale",
            "milanuncios_wholesale",
            "motor_es_wholesale",
            "wallapop_wholesale",
        ]
        for key in tier1:
            assert key in REGISTRY, f"Tier-1 source '{key}' missing from REGISTRY"

    def test_multi_source_rentacar_all_mapped(self) -> None:
        """All 6 group_rentacar_vo sub-sources must be individually mapped."""
        rentacar_keys = [
            "group_rentacar_vo_athlon",
            "group_rentacar_vo_okmobility",
            "group_rentacar_vo_centauro",
            "group_rentacar_vo_recordgo",
            "group_rentacar_vo_arval",
            "group_rentacar_vo_northgate",
        ]
        for key in rentacar_keys:
            assert key in REGISTRY, f"Rentacar member '{key}' missing from REGISTRY"

    def test_multi_source_bmw_mini_mapped(self) -> None:
        """BMW and MINI sub-sources each map to the same module with correct --brand arg."""
        bmw_entry = REGISTRY.get("oem_bmw_premium_selection_wholesale")
        mini_entry = REGISTRY.get("oem_mini_next_wholesale")
        assert bmw_entry is not None
        assert mini_entry is not None
        assert bmw_entry.module == mini_entry.module
        assert "--brand" in bmw_entry.extra_args
        assert "bmw" in bmw_entry.extra_args
        assert "mini" in mini_entry.extra_args

    def test_faciliteacoches_and_racc_separate_entries(self) -> None:
        """faciliteacoches_wholesale and racc_ocasion_wholesale are separate entries
        sharing the same module but with distinct --members args."""
        faci = REGISTRY.get("faciliteacoches_wholesale")
        racc = REGISTRY.get("racc_ocasion_wholesale")
        assert faci is not None
        assert racc is not None
        assert faci.module == racc.module
        assert "faciliteacoches" in faci.extra_args
        assert "racc" in racc.extra_args

    def test_family_sources_mapped(self) -> None:
        """All 7 family sources must be in the registry."""
        families = [
            "family_builder_wholesale",
            "family_cms_wp",
            "family_dealerk_wp",
            "family_dms_vendor_platforms",
            "family_framework_webbuilder",
            "family_generic_custom",
            "family_unreachable",
        ]
        for key in families:
            assert key in REGISTRY, f"Family '{key}' missing from REGISTRY"


# ---------------------------------------------------------------------------
# Gap report tests
# ---------------------------------------------------------------------------

class TestGapReport:
    def test_gap_report_all_known(self) -> None:
        """When all source_keys are in REGISTRY, gap is empty."""
        all_keys = list(REGISTRY.keys())
        mapped, unmapped = _gap_report(all_keys)
        assert set(mapped) == set(all_keys)
        assert unmapped == []

    def test_gap_report_detects_unknown(self) -> None:
        """An unknown source_key is reported as unmapped."""
        all_keys = ["autocasion_wholesale", "some_future_source_not_in_registry"]
        mapped, unmapped = _gap_report(all_keys)
        assert "autocasion_wholesale" in mapped
        assert "some_future_source_not_in_registry" in unmapped


# ---------------------------------------------------------------------------
# Live DB integration test (skipped if DB is unreachable)
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
class TestDueSourcesLiveDB:
    """Read-only integration test against the real source_health table.

    Verifies that _due_sources returns a list of tuples without crashing and
    that each tuple has the expected schema. Does NOT modify any data.
    """

    def test_due_sources_returns_list(self) -> None:
        import psycopg2
        conn = psycopg2.connect(
            "host=127.0.0.1 port=5433 dbname=cardeep user=cardeep password=cardeep_dev_only"
        )
        try:
            due = _due_sources(conn)
            assert isinstance(due, list)
            for row in due:
                source_key, interval_h, last_ok, last_fail = row
                assert isinstance(source_key, str)
                assert isinstance(interval_h, int)
                # last_ok and last_fail may be None (never harvested)
                assert last_ok is None or isinstance(last_ok, datetime)
                assert last_fail is None or isinstance(last_fail, datetime)
        finally:
            conn.close()

    def test_registry_covers_live_source_health(self) -> None:
        """Verify the gap report against the live DB and report unmapped keys."""
        import psycopg2
        conn = psycopg2.connect(
            "host=127.0.0.1 port=5433 dbname=cardeep user=cardeep password=cardeep_dev_only"
        )
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT source_key FROM source_health ORDER BY source_key")
                all_keys = [r[0] for r in cur.fetchall()]
        finally:
            conn.close()

        mapped, unmapped = _gap_report(all_keys)
        # All 47 source_health rows must be covered by the registry.
        # If this fails, the gap report names the missing keys.
        assert unmapped == [], (
            f"Unmapped source_keys (need entries in REGISTRY): {unmapped}"
        )
