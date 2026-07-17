"""F4 — Cho & Garcia-Molina (2003) per-source change-rate estimator
(plans/cardeep-omni/00-marketplace-engine.md F4).

TDD, pure-math first: the estimator's core (MLE change rate from censored "changed since
last visit" observations, and the fixed-window bucketing that turns raw timestamps into
those observations) is fully deterministic and DB-free — tested here with synthetic
timestamp lists before any DB-facing code is exercised. The DB-facing wrapper
(estimate_change_rate) is covered separately in test_cadence_estimator_live.py against
real June vehicle_event/harvest_run history (the backtest data).
"""
from __future__ import annotations

import math
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.ops.cadence_estimator import (
    CADENCE_CEIL_HOURS,
    CADENCE_FLOOR_HOURS,
    _bucket_visited_and_changed,
    _clamp_interval_hours,
    _mle_change_rate,
)

T0 = datetime(2026, 6, 1, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# 1. _mle_change_rate — the Cho & Garcia-Molina improved frequency estimator
# ---------------------------------------------------------------------------

class TestMleChangeRate:
    def test_all_windows_changed_gives_high_rate(self) -> None:
        """Every visited window saw a change -> rate approaches (but never reaches, thanks
        to the +0.5 correction) the 1/window_hours ceiling."""
        lam = _mle_change_rate(n_visited=20, n_unchanged=0, window_hours=24)
        assert lam > 0
        # -ln(0.5/20.5)/24 — sanity bound: much higher than a source that rarely changes.
        lam_rare = _mle_change_rate(n_visited=20, n_unchanged=18, window_hours=24)
        assert lam > lam_rare

    def test_no_changes_gives_low_but_nonzero_rate(self) -> None:
        """Zero observed changes must NOT yield lambda=0 (the +0.5 correction prevents the
        degenerate case where a source would be estimated as literally never changing)."""
        lam = _mle_change_rate(n_visited=20, n_unchanged=20, window_hours=24)
        assert lam > 0

    def test_matches_closed_form(self) -> None:
        n, unchanged, window_hours = 30, 10, 24
        expected = -math.log((unchanged + 0.5) / (n + 1)) / window_hours
        assert _mle_change_rate(n, unchanged, window_hours) == pytest.approx(expected)

    def test_higher_unchanged_fraction_gives_lower_rate(self) -> None:
        lam_mostly_changed = _mle_change_rate(n_visited=20, n_unchanged=2, window_hours=24)
        lam_mostly_unchanged = _mle_change_rate(n_visited=20, n_unchanged=18, window_hours=24)
        assert lam_mostly_changed > lam_mostly_unchanged


# ---------------------------------------------------------------------------
# 2. _bucket_visited_and_changed — fixed-window bucketing of raw timestamps
# ---------------------------------------------------------------------------

class TestBucketVisitedAndChanged:
    def test_visit_with_no_change_counts_as_unchanged(self) -> None:
        visits = [T0 + timedelta(hours=12)]
        changes: list[datetime] = []
        n_visited, n_unchanged = _bucket_visited_and_changed(
            visits, changes, T0, window_hours=24, n_windows=1)
        assert (n_visited, n_unchanged) == (1, 1)

    def test_visit_with_change_counts_as_changed(self) -> None:
        visits = [T0 + timedelta(hours=1)]
        changes = [T0 + timedelta(hours=12)]
        n_visited, n_unchanged = _bucket_visited_and_changed(
            visits, changes, T0, window_hours=24, n_windows=1)
        assert (n_visited, n_unchanged) == (1, 0)

    def test_never_visited_window_excluded_from_sample(self) -> None:
        """A window with no visit contributes NOTHING to n_visited — we cannot claim
        'unchanged' for a window we never looked at."""
        visits: list[datetime] = []
        changes = [T0 + timedelta(hours=5)]  # a change we could not have observed
        n_visited, n_unchanged = _bucket_visited_and_changed(
            visits, changes, T0, window_hours=24, n_windows=1)
        assert n_visited == 0

    def test_multiple_windows_split_correctly(self) -> None:
        # 3 windows of 24h. Window 0: visited+changed. Window 1: visited+unchanged.
        # Window 2: never visited.
        visits = [T0 + timedelta(hours=1), T0 + timedelta(hours=30)]
        changes = [T0 + timedelta(hours=2)]
        n_visited, n_unchanged = _bucket_visited_and_changed(
            visits, changes, T0, window_hours=24, n_windows=3)
        assert n_visited == 2
        assert n_unchanged == 1  # only window 1 (visited, no change)

    def test_multiple_visits_in_same_window_still_one_bucket(self) -> None:
        visits = [T0 + timedelta(hours=1), T0 + timedelta(hours=2), T0 + timedelta(hours=3)]
        changes: list[datetime] = []
        n_visited, n_unchanged = _bucket_visited_and_changed(
            visits, changes, T0, window_hours=24, n_windows=1)
        assert (n_visited, n_unchanged) == (1, 1)

    def test_timestamps_outside_range_ignored(self) -> None:
        visits = [T0 - timedelta(hours=5), T0 + timedelta(hours=1000)]  # before / way after
        changes: list[datetime] = []
        n_visited, n_unchanged = _bucket_visited_and_changed(
            visits, changes, T0, window_hours=24, n_windows=2)
        assert n_visited == 0


# ---------------------------------------------------------------------------
# 3. _clamp_interval_hours — the F4 safety floor/ceiling (§5.3: never hammer, never abandon)
# ---------------------------------------------------------------------------

class TestClampIntervalHours:
    def test_floor_applied(self) -> None:
        assert _clamp_interval_hours(1) == CADENCE_FLOOR_HOURS

    def test_ceiling_applied(self) -> None:
        assert _clamp_interval_hours(999999) == CADENCE_CEIL_HOURS

    def test_within_range_unchanged(self) -> None:
        assert _clamp_interval_hours(100) == 100

    def test_floor_is_24(self) -> None:
        assert CADENCE_FLOOR_HOURS == 24

    def test_ceiling_is_2160(self) -> None:
        assert CADENCE_CEIL_HOURS == 2160
