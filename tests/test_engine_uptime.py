"""Unit tests for pipeline.ops.engine_uptime (F6, 00-marketplace-engine.md).

Pure module — no DB, no mocks needed. Covers bucket_uptime's window partitioning and
clipped_window's anti-alucinación guard (never fabricating pre-ledger history as downtime).
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.ops.engine_uptime import (
    DEFAULT_BUCKET_MINUTES,
    UptimeReport,
    bucket_uptime,
    clipped_window,
    uptime_report_to_dict,
)

UTC = timezone.utc
_START = datetime(2026, 7, 18, 0, 0, 0, tzinfo=UTC)


# ---------------------------------------------------------------------------
# bucket_uptime — pure bucketing math
# ---------------------------------------------------------------------------

class TestBucketUptimeEmptyWindow:
    def test_zero_width_window_returns_no_buckets_not_zero_pct(self) -> None:
        """window_end == window_start must report pct=None (no data), never 0%."""
        report = bucket_uptime([], window_start=_START, window_end=_START)
        assert report.buckets_total == 0
        assert report.buckets_with_beat == 0
        assert report.uptime_pct is None

    def test_inverted_window_returns_no_buckets(self) -> None:
        report = bucket_uptime([], window_start=_START, window_end=_START - timedelta(hours=1))
        assert report.buckets_total == 0
        assert report.uptime_pct is None


class TestBucketUptimeNoBeats:
    def test_no_beats_at_all_is_zero_pct_not_none(self) -> None:
        """A real span with zero heartbeats IS 0% uptime (not 'no data') — buckets_total > 0."""
        end = _START + timedelta(hours=1)
        report = bucket_uptime([], window_start=_START, window_end=end)
        assert report.buckets_total == 4  # 60min / 15min buckets
        assert report.buckets_with_beat == 0
        assert report.uptime_pct == 0.0


class TestBucketUptimeFullCoverage:
    def test_one_beat_per_bucket_is_100pct(self) -> None:
        end = _START + timedelta(hours=1)  # 4 buckets of 15 min
        beats = [
            _START + timedelta(minutes=2),
            _START + timedelta(minutes=17),
            _START + timedelta(minutes=32),
            _START + timedelta(minutes=47),
        ]
        report = bucket_uptime(beats, window_start=_START, window_end=end)
        assert report.buckets_total == 4
        assert report.buckets_with_beat == 4
        assert report.uptime_pct == 100.0

    def test_dense_beats_every_2min_still_100pct(self) -> None:
        """The real production cadence: a heartbeat every 2 min densely fills every 15-min bucket."""
        end = _START + timedelta(hours=2)
        beats = [_START + timedelta(minutes=2 * i) for i in range(61)]  # every 2min for 2h
        report = bucket_uptime(beats, window_start=_START, window_end=end)
        assert report.buckets_total == 8
        assert report.buckets_with_beat == 8
        assert report.uptime_pct == 100.0


class TestBucketUptimePartial:
    def test_gap_in_the_middle_is_reflected_proportionally(self) -> None:
        """4 buckets, only bucket 1 and 4 have a beat -> 50%."""
        end = _START + timedelta(hours=1)
        beats = [
            _START + timedelta(minutes=5),    # bucket 0 [0,15)
            _START + timedelta(minutes=50),   # bucket 3 [45,60)
        ]
        report = bucket_uptime(beats, window_start=_START, window_end=end)
        assert report.buckets_total == 4
        assert report.buckets_with_beat == 2
        assert report.uptime_pct == 50.0

    def test_beat_exactly_at_bucket_boundary_belongs_to_the_later_bucket(self) -> None:
        """A beat at t=15min falls in [15,30), not [0,15) — half-open interval convention."""
        end = _START + timedelta(minutes=30)
        beats = [_START + timedelta(minutes=15)]
        report = bucket_uptime(beats, window_start=_START, window_end=end)
        assert report.buckets_total == 2
        assert report.buckets_with_beat == 1  # only the second bucket has the beat

    def test_beats_outside_window_are_ignored(self) -> None:
        end = _START + timedelta(minutes=30)
        beats = [
            _START - timedelta(minutes=5),   # before window
            end + timedelta(minutes=5),      # after window
        ]
        report = bucket_uptime(beats, window_start=_START, window_end=end)
        assert report.buckets_total == 2
        assert report.buckets_with_beat == 0
        assert report.uptime_pct == 0.0

    def test_unsorted_beats_are_handled_correctly(self) -> None:
        end = _START + timedelta(hours=1)
        beats = [
            _START + timedelta(minutes=47),
            _START + timedelta(minutes=2),
            _START + timedelta(minutes=32),
            _START + timedelta(minutes=17),
        ]
        report = bucket_uptime(beats, window_start=_START, window_end=end)
        assert report.buckets_with_beat == 4


class TestBucketUptimeTrailingPartialBucket:
    def test_short_trailing_bucket_still_counts_as_one_bucket(self) -> None:
        """37 minutes over 15-min buckets = 2 full + 1 short (7min) = 3 buckets total."""
        end = _START + timedelta(minutes=37)
        report = bucket_uptime([], window_start=_START, window_end=end)
        assert report.buckets_total == 3

    def test_beat_landing_in_short_trailing_bucket_counts(self) -> None:
        end = _START + timedelta(minutes=37)
        beats = [_START + timedelta(minutes=33)]
        report = bucket_uptime(beats, window_start=_START, window_end=end)
        assert report.buckets_total == 3
        assert report.buckets_with_beat == 1


class TestBucketUptimeCustomGranularity:
    def test_default_bucket_minutes_is_15(self) -> None:
        assert DEFAULT_BUCKET_MINUTES == 15

    def test_custom_bucket_minutes_changes_partition_count(self) -> None:
        end = _START + timedelta(hours=1)
        report = bucket_uptime([], window_start=_START, window_end=end, bucket_minutes=30)
        assert report.buckets_total == 2


# ---------------------------------------------------------------------------
# clipped_window — anti-alucinación guard
# ---------------------------------------------------------------------------

class TestClippedWindow:
    def test_no_observed_history_returns_zero_width_window(self) -> None:
        """observed_since=None (no ledger rows yet) must never fabricate 30 days of downtime."""
        now = _START
        start, end, full = clipped_window(now=now, requested_days=30, observed_since=None)
        assert start == end == now.replace(tzinfo=UTC)
        assert full is False

    def test_full_history_available_reports_full_window(self) -> None:
        now = _START
        observed_since = now - timedelta(days=45)  # ledger older than the requested 30d
        start, end, full = clipped_window(now=now, requested_days=30, observed_since=observed_since)
        assert start == now - timedelta(days=30)
        assert end == now
        assert full is True

    def test_partial_history_clips_to_observed_since(self) -> None:
        """Ledger only 5 days old but 30 days were requested -> clip to 5 days, flag False."""
        now = _START
        observed_since = now - timedelta(days=5)
        start, end, full = clipped_window(now=now, requested_days=30, observed_since=observed_since)
        assert start == observed_since
        assert end == now
        assert full is False

    def test_exact_boundary_observed_since_equals_requested_start_is_full(self) -> None:
        now = _START
        observed_since = now - timedelta(days=30)
        _, _, full = clipped_window(now=now, requested_days=30, observed_since=observed_since)
        assert full is True

    def test_naive_datetimes_treated_as_utc(self) -> None:
        now = _START.replace(tzinfo=None)
        observed_since = (now - timedelta(days=45)).replace(tzinfo=None)
        start, end, full = clipped_window(now=now, requested_days=30, observed_since=observed_since)
        assert full is True
        assert start.tzinfo is not None


# ---------------------------------------------------------------------------
# uptime_report_to_dict — serialization shape
# ---------------------------------------------------------------------------

class TestUptimeReportToDict:
    def test_shape_and_rounding(self) -> None:
        report = UptimeReport(
            window_start=_START, window_end=_START + timedelta(hours=1),
            bucket_minutes=15, buckets_total=3, buckets_with_beat=1, uptime_pct=33.333333,
        )
        d = uptime_report_to_dict(report, requested_days=30, full_window_available=True)
        assert d["requested_days"] == 30
        assert d["full_window_available"] is True
        assert d["bucket_minutes"] == 15
        assert d["buckets_total"] == 3
        assert d["buckets_with_beat"] == 1
        assert d["uptime_pct"] == 33.33
        assert "observed_from" in d and "observed_to" in d

    def test_none_pct_serializes_as_none(self) -> None:
        report = UptimeReport(
            window_start=_START, window_end=_START,
            bucket_minutes=15, buckets_total=0, buckets_with_beat=0, uptime_pct=None,
        )
        d = uptime_report_to_dict(report, requested_days=30, full_window_available=False)
        assert d["uptime_pct"] is None
