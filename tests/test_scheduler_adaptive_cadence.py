"""F4 — _due_sources()'s adaptive-cadence SQL CASE (00-marketplace-engine.md F4 / §5.3).

The estimator's pure math is covered in test_cadence_estimator.py; this file proves the
SQL wiring itself: a source in cadence_mode='static' (the default for every pre-F4 row)
behaves byte-identically to before F4, and a source explicitly flipped to 'adaptive' with a
computed_interval_hours is scheduled by THAT interval instead of harvest_interval_hours —
both directions (an adaptive interval SHORTER than the static one pulls a source IN as due
sooner; a LONGER one pushes a due source OUT). Real committed rows + `finally` cleanup
(source_health/source_breaker are not append-only, unlike vehicle_event).
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

PSYCOPG2_DSN = "host=127.0.0.1 port=5433 dbname=cardeep user=cardeep password=cardeep_dev_only"
SOURCE_KEY = "__f4_adaptive_sql_test__"


def _db_available() -> bool:
    try:
        import psycopg2
        conn = psycopg2.connect(PSYCOPG2_DSN, connect_timeout=3)
        conn.close()
        return True
    except Exception:
        return False


DB_AVAILABLE = _db_available()


@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestAdaptiveCadenceSql:
    def _cleanup(self, cur) -> None:
        cur.execute("DELETE FROM source_health WHERE source_key=%s", (SOURCE_KEY,))

    def test_static_mode_uses_harvest_interval_hours(self) -> None:
        """Default cadence_mode='static': behaves exactly as pre-F4, ignoring
        computed_interval_hours entirely even when one happens to be populated."""
        import psycopg2

        from pipeline.ops.scheduler import _due_sources

        conn = psycopg2.connect(PSYCOPG2_DSN)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                self._cleanup(cur)
                # last_ok 30h ago: DUE for a 24h static interval, NOT due for a 168h one.
                # computed_interval_hours=168 is populated but must be IGNORED in static mode.
                cur.execute(
                    "INSERT INTO source_health (source_key, harvest_interval_hours, "
                    "last_ok, consecutive_fails, country_code, cadence_mode, "
                    "computed_interval_hours) "
                    "VALUES (%s, 24, now() - interval '30 hours', 0, 'ES', 'static', 168)",
                    (SOURCE_KEY,),
                )
            due = _due_sources(conn)
            assert SOURCE_KEY in [r[0] for r in due], (
                "static mode must use harvest_interval_hours (24h, satisfied by a 30h-old "
                "last_ok), ignoring the populated but inactive computed_interval_hours (168h)"
            )
        finally:
            with conn.cursor() as cur:
                self._cleanup(cur)
            conn.close()

    def test_adaptive_mode_uses_computed_interval_shorter_pulls_in(self) -> None:
        """cadence_mode='adaptive' with a SHORTER computed interval makes a source due
        sooner than its static harvest_interval_hours would."""
        import psycopg2

        from pipeline.ops.scheduler import _due_sources

        conn = psycopg2.connect(PSYCOPG2_DSN)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                self._cleanup(cur)
                # last_ok 30h ago: NOT due for a 168h static interval, but DUE for a 24h
                # adaptive one.
                cur.execute(
                    "INSERT INTO source_health (source_key, harvest_interval_hours, "
                    "last_ok, consecutive_fails, country_code, cadence_mode, "
                    "computed_interval_hours) "
                    "VALUES (%s, 168, now() - interval '30 hours', 0, 'ES', 'adaptive', 24)",
                    (SOURCE_KEY,),
                )
            due = _due_sources(conn)
            assert SOURCE_KEY in [r[0] for r in due], (
                "adaptive mode must use computed_interval_hours (24h) instead of the static "
                "168h — the 30h-old last_ok clears the shorter adaptive threshold"
            )
        finally:
            with conn.cursor() as cur:
                self._cleanup(cur)
            conn.close()

    def test_adaptive_mode_uses_computed_interval_longer_pushes_out(self) -> None:
        """cadence_mode='adaptive' with a LONGER computed interval keeps a source that
        WOULD be due under its static interval from being scheduled yet — the compression
        (or here, extension) is symmetric, not one-directional."""
        import psycopg2

        from pipeline.ops.scheduler import _due_sources

        conn = psycopg2.connect(PSYCOPG2_DSN)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                self._cleanup(cur)
                # last_ok 30h ago: DUE for a 24h static interval, but NOT due for a 720h
                # adaptive one.
                cur.execute(
                    "INSERT INTO source_health (source_key, harvest_interval_hours, "
                    "last_ok, consecutive_fails, country_code, cadence_mode, "
                    "computed_interval_hours) "
                    "VALUES (%s, 24, now() - interval '30 hours', 0, 'ES', 'adaptive', 720)",
                    (SOURCE_KEY,),
                )
            due = _due_sources(conn)
            assert SOURCE_KEY not in [r[0] for r in due], (
                "adaptive mode must use computed_interval_hours (720h) instead of the "
                "static 24h — the 30h-old last_ok does NOT clear the longer adaptive threshold"
            )
        finally:
            with conn.cursor() as cur:
                self._cleanup(cur)
            conn.close()

    def test_adaptive_mode_without_estimate_falls_back_to_static(self) -> None:
        """cadence_mode='adaptive' but computed_interval_hours IS NULL (never estimated
        yet, or the sample was insufficient): must fall back to harvest_interval_hours,
        never treat NULL as 'always due' or 'never due'."""
        import psycopg2

        from pipeline.ops.scheduler import _due_sources

        conn = psycopg2.connect(PSYCOPG2_DSN)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                self._cleanup(cur)
                cur.execute(
                    "INSERT INTO source_health (source_key, harvest_interval_hours, "
                    "last_ok, consecutive_fails, country_code, cadence_mode) "
                    "VALUES (%s, 24, now() - interval '30 hours', 0, 'ES', 'adaptive')",
                    (SOURCE_KEY,),
                )
            due = _due_sources(conn)
            assert SOURCE_KEY in [r[0] for r in due], (
                "adaptive mode with a NULL computed_interval_hours must fall back to the "
                "24h static interval (satisfied by the 30h-old last_ok)"
            )
        finally:
            with conn.cursor() as cur:
                self._cleanup(cur)
            conn.close()
