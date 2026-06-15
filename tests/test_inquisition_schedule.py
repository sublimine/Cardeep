"""Tests for WF-INQUISITION δ: verify_ttl, record_count_verdict TTL wiring,
find_expired, and schedule_reverification.

Design
------
- TTL unit tests: pure Python, no DB required.
- DB integration tests: each test opens a real connection to cardeep-pg, runs
  inside an aborted transaction (_Rollback sentinel), and rolls back cleanly.
  The hash-chain trigger fires on INSERT but the verdict_audit row is discarded
  with the transaction rollback — no audit chain contamination.
- Test seed verdicts use verdict='UNVERIFIED' to avoid triggering the
  chk_trustworthy_needs_quorum CHECK (NOT VALID but enforced on new rows).
  UNVERIFIED never requires quorum_n/family_n/origin_n.
- All tests are synchronous at the top level (asyncio.run) matching the
  pattern established in test_coverage_verify.py and test_gestionador.py.

asyncpg INTERVAL handling
--------------------------
verify_ttl.ttl_for() returns datetime.timedelta.  asyncpg maps timedelta to
Postgres INTERVAL (OID 1186) natively; it cannot encode a raw str as INTERVAL.
The TTL unit tests compare against timedelta values, not strings.

DB access
---------
Tests are skipped when cardeep-pg is not reachable at 127.0.0.1:5433.
"""
from __future__ import annotations

import asyncio
import datetime
from datetime import timedelta
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# DB connectivity guard — identical pattern to test_coverage_verify.py
# ---------------------------------------------------------------------------
DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"


def _db_available() -> bool:
    try:
        import asyncpg  # noqa: F401
        return asyncio.run(_ping())
    except Exception:
        return False


async def _ping() -> bool:
    try:
        import asyncpg
        conn = await asyncpg.connect(DSN, timeout=3)
        await conn.close()
        return True
    except Exception:
        return False


DB_AVAILABLE = _db_available()


class _Rollback(Exception):
    """Sentinel that forces transaction rollback without persisting any state."""


# ---------------------------------------------------------------------------
# A. Unit tests — pipeline.verify_ttl (no DB required)
# ---------------------------------------------------------------------------

class TestTTLPolicy:
    """Pure unit tests for pipeline.verify_ttl.ttl_for.

    ttl_for() returns datetime.timedelta (not str), because asyncpg maps
    timedelta to Postgres INTERVAL natively and cannot encode raw strings.
    """

    def test_count_returns_7_days(self) -> None:
        from pipeline.verify_ttl import ttl_for
        assert ttl_for("count") == timedelta(days=7)

    def test_freshness_returns_1_day(self) -> None:
        from pipeline.verify_ttl import ttl_for
        assert ttl_for("freshness") == timedelta(days=1)

    def test_coverage_returns_14_days(self) -> None:
        from pipeline.verify_ttl import ttl_for
        assert ttl_for("coverage") == timedelta(days=14)

    def test_field_fill_returns_14_days(self) -> None:
        from pipeline.verify_ttl import ttl_for
        assert ttl_for("field_fill") == timedelta(days=14)

    def test_existence_returns_30_days(self) -> None:
        from pipeline.verify_ttl import ttl_for
        assert ttl_for("existence") == timedelta(days=30)

    def test_denominator_returns_30_days(self) -> None:
        from pipeline.verify_ttl import ttl_for
        assert ttl_for("denominator") == timedelta(days=30)

    def test_unknown_kind_falls_back_to_count_default(self) -> None:
        """Unrecognised claim_kind must return the COUNT default (7 days), not None."""
        from pipeline.verify_ttl import ttl_for, DEFAULT_TTL, VERDICT_TTL
        result = ttl_for("completely_unknown_kind_xyz")
        assert result == DEFAULT_TTL
        assert DEFAULT_TTL == VERDICT_TTL["count"]
        assert isinstance(result, timedelta)

    def test_unknown_kind_is_timedelta_7_days(self) -> None:
        """Concrete assertion: unknown → timedelta(days=7) (shortest operational cadence)."""
        from pipeline.verify_ttl import ttl_for
        assert ttl_for("nonexistent") == timedelta(days=7)

    def test_all_known_kinds_return_timedelta(self) -> None:
        from pipeline.verify_ttl import ttl_for, VERDICT_TTL
        for kind in VERDICT_TTL:
            result = ttl_for(kind)
            assert isinstance(result, timedelta), (
                f"ttl_for({kind!r}) must return timedelta, got {type(result)!r}"
            )
            assert result.total_seconds() > 0, (
                f"ttl_for({kind!r}) must be a positive duration, got {result!r}"
            )


# ---------------------------------------------------------------------------
# B. DB integration — record_count_verdict now sets expires_at
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestRecordCountVerdictTTL:
    """Verify that new verdicts carry expires_at ≈ created_at + TTL."""

    def test_count_verdict_has_expires_at_7_days(self) -> None:
        asyncio.run(self._run_count_verdict_ttl())

    async def _run_count_verdict_ttl(self) -> None:
        import asyncpg
        from pipeline.verify import record_count_verdict

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                # Two paths that agree → TRUSTWORTHY is attempted, but
                # chk_trustworthy_needs_quorum (NOT VALID, enforced on inserts)
                # requires quorum_n >= 2 AND family_n >= 2 AND origin_n >= 2.
                # verifier_paths must be a JSONB array of objects with 'family'
                # and 'origin' keys to satisfy the generated columns.
                # Simpler: use two paths that DIVERGE to produce REFUTED (or use
                # a single path to produce UNVERIFIED) — both bypass the quorum check.
                # We use a single-path scenario → UNVERIFIED.
                await record_count_verdict(
                    conn,
                    subject_type="test_ttl_subject",
                    subject_key="__inquisition_ttl_test__",
                    claim="unit test claim for TTL verification",
                    paths={"only_path": 100},   # single path → UNVERIFIED, no quorum needed
                    claim_kind="count",
                )

                row = await conn.fetchrow(
                    """SELECT created_at, expires_at, claim_kind
                       FROM verification_verdict
                       WHERE subject_type = 'test_ttl_subject'
                         AND subject_key = '__inquisition_ttl_test__'
                       ORDER BY created_at DESC
                       LIMIT 1""",
                )
                assert row is not None, "Verdict row must have been inserted"
                assert row["claim_kind"] == "count"
                assert row["expires_at"] is not None, (
                    "expires_at must be set for claim_kind='count'"
                )

                created_at = row["created_at"]
                expires_at = row["expires_at"]

                # Normalise to UTC if needed.
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=datetime.timezone.utc)
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=datetime.timezone.utc)

                delta_days = (expires_at - created_at).total_seconds() / 86400.0
                # Allow ±2 minutes of clock jitter between the Python now() and the
                # Postgres now() used inside the INSERT.  7 days = 604800 seconds;
                # we just verify we're within 5 minutes of the expected window.
                tolerance_days = 5 / (60 * 24)   # 5 minutes in days
                assert abs(delta_days - 7.0) < tolerance_days, (
                    f"expires_at should be ~7 days after created_at; "
                    f"got delta={delta_days:.6f} days"
                )

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_freshness_verdict_has_1_day_ttl(self) -> None:
        asyncio.run(self._run_freshness_ttl())

    async def _run_freshness_ttl(self) -> None:
        import asyncpg
        from pipeline.verify import record_count_verdict

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                await record_count_verdict(
                    conn,
                    subject_type="test_ttl_subject",
                    subject_key="__inquisition_freshness_test__",
                    claim="freshness unit test",
                    paths={"only_path": 1},
                    claim_kind="freshness",
                )

                row = await conn.fetchrow(
                    """SELECT created_at, expires_at, claim_kind
                       FROM verification_verdict
                       WHERE subject_key = '__inquisition_freshness_test__'
                       ORDER BY created_at DESC LIMIT 1""",
                )
                assert row is not None
                assert row["claim_kind"] == "freshness"
                assert row["expires_at"] is not None

                created_at = row["created_at"]
                expires_at = row["expires_at"]
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=datetime.timezone.utc)
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=datetime.timezone.utc)

                delta_days = (expires_at - created_at).total_seconds() / 86400.0
                tolerance_days = 5 / (60 * 24)
                assert abs(delta_days - 1.0) < tolerance_days, (
                    f"freshness verdict should expire in ~1 day; got {delta_days:.6f}"
                )

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_backward_compat_default_claim_kind_is_count(self) -> None:
        """Callers that omit claim_kind must get 'count' + 7-day TTL (no regression)."""
        asyncio.run(self._run_backward_compat())

    async def _run_backward_compat(self) -> None:
        import asyncpg
        from pipeline.verify import record_count_verdict

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                # Simulate an old caller: only the original parameters are passed.
                verdict = await record_count_verdict(
                    conn,
                    subject_type="test_ttl_subject",
                    subject_key="__inquisition_compat_test__",
                    claim="backward compat test",
                    paths={"path_a": 50},   # single path → UNVERIFIED
                    # claim_kind and expires_in intentionally omitted
                )
                assert verdict == "UNVERIFIED"

                row = await conn.fetchrow(
                    """SELECT claim_kind, expires_at
                       FROM verification_verdict
                       WHERE subject_key = '__inquisition_compat_test__'
                       ORDER BY created_at DESC LIMIT 1""",
                )
                assert row is not None
                assert row["claim_kind"] == "count", (
                    "Default claim_kind must be 'count' for backward compatibility"
                )
                assert row["expires_at"] is not None, (
                    "Default claim_kind='count' must produce a 7-day TTL, not NULL"
                )

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()


# ---------------------------------------------------------------------------
# C. DB integration — find_expired filters correctly
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestFindExpired:
    """Verify the 4 filter cases for find_expired."""

    def test_filter_matrix(self) -> None:
        asyncio.run(self._run_filter_matrix())

    async def _run_filter_matrix(self) -> None:
        """Insert four verdict rows with different (expires_at, superseded_by) states
        and assert that find_expired returns exactly the one that is expired and
        non-superseded.

        Rows:
          1. expires_at=NULL, superseded_by=NULL  → EXCLUDED (eternal seal)
          2. expires_at=future, superseded_by=NULL → EXCLUDED (not yet expired)
          3. expires_at=past, superseded_by=NULL   → INCLUDED
          4. expires_at=past, superseded_by=3.id   → EXCLUDED (superseded)
        """
        import asyncpg
        from pipeline.ops.inquisition_schedule import find_expired

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                now_utc = datetime.datetime.now(tz=datetime.timezone.utc)
                future_ts = now_utc + datetime.timedelta(days=30)
                past_ts_2d = now_utc - datetime.timedelta(days=2)
                past_ts_1d = now_utc - datetime.timedelta(days=1)

                # Row 1: eternal seal (NULL expires_at) — omit expires_at entirely.
                row1 = await conn.fetchrow(
                    """INSERT INTO verification_verdict
                           (subject_type, subject_key, claim,
                            primary_value, primary_path,
                            verifier_paths, independent_values,
                            divergence, verdict, evidence, claim_kind)
                       VALUES ('test_inq','__inq_filter_test__','claim_eternal',
                               '0','path','[]'::jsonb,'[]'::jsonb,
                               NULL,'UNVERIFIED','test','count')
                       RETURNING id""",
                )
                _id1 = row1["id"]

                # Row 2: future expires_at (not yet expired) — passed as datetime.
                row2 = await conn.fetchrow(
                    """INSERT INTO verification_verdict
                           (subject_type, subject_key, claim,
                            primary_value, primary_path,
                            verifier_paths, independent_values,
                            divergence, verdict, evidence, claim_kind, expires_at)
                       VALUES ('test_inq','__inq_filter_test__','claim_future',
                               '0','path','[]'::jsonb,'[]'::jsonb,
                               NULL,'UNVERIFIED','test','count', $1)
                       RETURNING id""",
                    future_ts,
                )
                _id2 = row2["id"]

                # Row 3: PAST expires_at, not superseded → MUST BE INCLUDED.
                row3 = await conn.fetchrow(
                    """INSERT INTO verification_verdict
                           (subject_type, subject_key, claim,
                            primary_value, primary_path,
                            verifier_paths, independent_values,
                            divergence, verdict, evidence, claim_kind, expires_at)
                       VALUES ('test_inq','__inq_filter_test__','claim_expired',
                               '0','path','[]'::jsonb,'[]'::jsonb,
                               NULL,'UNVERIFIED','test','count', $1)
                       RETURNING id""",
                    past_ts_2d,
                )
                id3 = row3["id"]

                # Row 4: PAST expires_at but superseded_by = id3 → EXCLUDED.
                await conn.fetchrow(
                    """INSERT INTO verification_verdict
                           (subject_type, subject_key, claim,
                            primary_value, primary_path,
                            verifier_paths, independent_values,
                            divergence, verdict, evidence, claim_kind,
                            expires_at, superseded_by)
                       VALUES ('test_inq','__inq_filter_test__','claim_superseded',
                               '0','path','[]'::jsonb,'[]'::jsonb,
                               NULL,'UNVERIFIED','test','count', $1, $2)
                       RETURNING id""",
                    past_ts_1d,
                    id3,
                )

                expired_rows = await find_expired(conn)

                # Filter only OUR test rows (other expired verdicts may exist in DB).
                our_ids = {r["id"] for r in expired_rows
                           if r["subject_type"] == "test_inq"
                           and r["subject_key"] == "__inq_filter_test__"}

                assert id3 in our_ids, (
                    f"Row 3 (past, non-superseded) must appear in find_expired; "
                    f"found ids: {our_ids}"
                )
                assert _id1 not in our_ids, "Row 1 (eternal) must be excluded"
                assert _id2 not in our_ids, "Row 2 (future) must be excluded"
                # Verify no superseded row leaks in (row 4 has claim='claim_superseded'):
                superseded_claims = {r["claim"] for r in expired_rows
                                     if r["subject_type"] == "test_inq"
                                     and r["subject_key"] == "__inq_filter_test__"}
                assert "claim_superseded" not in superseded_claims, (
                    "Superseded verdict must be excluded from find_expired"
                )

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()


# ---------------------------------------------------------------------------
# D. DB integration — schedule_reverification idempotency
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestScheduleReverification:
    """Verify that schedule_reverification opens exactly one gestion_item per
    stale verdict and is idempotent on the second call."""

    def test_opens_item_for_expired_verdict(self) -> None:
        asyncio.run(self._run_opens_item())

    async def _run_opens_item(self) -> None:
        import asyncpg
        from pipeline.ops.inquisition_schedule import schedule_reverification

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                # Seed one expired verdict.
                row = await conn.fetchrow(
                    """INSERT INTO verification_verdict
                           (subject_type, subject_key, claim,
                            primary_value, primary_path,
                            verifier_paths, independent_values,
                            divergence, verdict, evidence, claim_kind, expires_at)
                       VALUES ('test_inq','__inq_schedule_test__','schedule claim',
                               '42','path_a','[]'::jsonb,'[]'::jsonb,
                               NULL,'UNVERIFIED','test','count',
                               now() - interval '3 days')
                       RETURNING id""",
                )
                verdict_id = row["id"]

                # First run: must open a gestion_item.
                summary1 = await schedule_reverification(
                    conn, actor="test_inquisition_1"
                )

                # Verify gestion_item was created with correct fields.
                item = await conn.fetchrow(
                    """SELECT detector, subject_type, subject_key, dedupe_key, state
                       FROM gestion_item
                       WHERE detector = 'stale_verdict'
                         AND subject_type = 'test_inq'
                         AND subject_key = '__inq_schedule_test__'
                       ORDER BY opened_at DESC
                       LIMIT 1""",
                )
                assert item is not None, (
                    "gestion_item with detector='stale_verdict' must exist after scheduling"
                )
                assert item["detector"] == "stale_verdict"
                assert item["subject_type"] == "test_inq"
                assert item["subject_key"] == "__inq_schedule_test__"
                expected_dedupe = (
                    "stale_verdict:test_inq:__inq_schedule_test__:schedule claim"
                )
                assert item["dedupe_key"] == expected_dedupe, (
                    f"dedupe_key mismatch: expected {expected_dedupe!r}, "
                    f"got {item['dedupe_key']!r}"
                )
                assert item["state"] == "OPEN"

                # Summary must report at least 1 expired and 1 item.
                # (There may be MORE expired verdicts from other tests in the DB,
                #  so we use >= rather than ==.)
                assert summary1["expired_found"] >= 1
                assert summary1["items_opened_or_refreshed"] >= 1
                assert "count" in summary1["by_claim_kind"]

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_idempotent_second_run_no_duplicate(self) -> None:
        """Running schedule_reverification twice must NOT create a second gestion_item."""
        asyncio.run(self._run_idempotent())

    async def _run_idempotent(self) -> None:
        import asyncpg
        from pipeline.ops.inquisition_schedule import schedule_reverification

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                # Seed one expired verdict.
                await conn.fetchrow(
                    """INSERT INTO verification_verdict
                           (subject_type, subject_key, claim,
                            primary_value, primary_path,
                            verifier_paths, independent_values,
                            divergence, verdict, evidence, claim_kind, expires_at)
                       VALUES ('test_inq','__inq_idem_test__','idem claim',
                               '99','path_x','[]'::jsonb,'[]'::jsonb,
                               NULL,'UNVERIFIED','test','count',
                               now() - interval '5 days')
                       RETURNING id""",
                )

                # First run.
                await schedule_reverification(conn, actor="test_inquisition_idem_1")

                # Second run: must NOT create a duplicate gestion_item.
                await schedule_reverification(conn, actor="test_inquisition_idem_2")

                count = await conn.fetchval(
                    """SELECT count(*)
                       FROM gestion_item
                       WHERE detector = 'stale_verdict'
                         AND subject_type = 'test_inq'
                         AND subject_key = '__inq_idem_test__'""",
                ) or 0

                assert count == 1, (
                    f"Idempotency violated: expected 1 gestion_item, got {count}. "
                    "open_or_refresh must upsert, not insert twice."
                )

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_eternal_verdicts_are_not_scheduled(self) -> None:
        """Verdicts with expires_at=NULL (grandfathered seals) must never be queued."""
        asyncio.run(self._run_eternal_excluded())

    async def _run_eternal_excluded(self) -> None:
        import asyncpg
        from pipeline.ops.inquisition_schedule import schedule_reverification

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                # Seed one eternal verdict (no expires_at).
                await conn.execute(
                    """INSERT INTO verification_verdict
                           (subject_type, subject_key, claim,
                            primary_value, primary_path,
                            verifier_paths, independent_values,
                            divergence, verdict, evidence, claim_kind)
                       VALUES ('test_inq','__inq_eternal_test__','eternal claim',
                               '0','path','[]'::jsonb,'[]'::jsonb,
                               NULL,'UNVERIFIED','test','count')""",
                )

                items_before = await conn.fetchval(
                    """SELECT count(*) FROM gestion_item
                       WHERE detector = 'stale_verdict'
                         AND subject_key = '__inq_eternal_test__'""",
                ) or 0

                await schedule_reverification(conn, actor="test_inquisition_eternal")

                items_after = await conn.fetchval(
                    """SELECT count(*) FROM gestion_item
                       WHERE detector = 'stale_verdict'
                         AND subject_key = '__inq_eternal_test__'""",
                ) or 0

                assert items_after == items_before, (
                    "Eternal verdict (expires_at=NULL) must NOT generate a gestion_item"
                )

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_severity_derives_from_overdue_duration(self) -> None:
        """Overdue > 7 days must produce severity='critical'."""
        asyncio.run(self._run_severity_critical())

    async def _run_severity_critical(self) -> None:
        import asyncpg
        from pipeline.ops.inquisition_schedule import schedule_reverification

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                await conn.fetchrow(
                    """INSERT INTO verification_verdict
                           (subject_type, subject_key, claim,
                            primary_value, primary_path,
                            verifier_paths, independent_values,
                            divergence, verdict, evidence, claim_kind, expires_at)
                       VALUES ('test_inq','__inq_sev_test__','severity claim',
                               '0','path','[]'::jsonb,'[]'::jsonb,
                               NULL,'UNVERIFIED','test','count',
                               now() - interval '10 days')
                       RETURNING id""",
                )

                await schedule_reverification(conn, actor="test_inquisition_sev")

                item = await conn.fetchrow(
                    """SELECT severity, measured
                       FROM gestion_item
                       WHERE detector = 'stale_verdict'
                         AND subject_type = 'test_inq'
                         AND subject_key = '__inq_sev_test__'
                       ORDER BY opened_at DESC LIMIT 1""",
                )
                assert item is not None
                assert item["severity"] == "critical", (
                    f"10-day overdue verdict must produce severity='critical'; "
                    f"got {item['severity']!r}"
                )

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()
