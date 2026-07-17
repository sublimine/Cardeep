"""Unit tests for pipeline/market/cohort.py — pure functions, no DB, no network.

These pin down the exact percentile_cont formula (hand-calculated) so a future edit
cannot silently drift from PostgreSQL's own percentile_cont semantics without a test
catching it (the whole point of this module is being an INDEPENDENT recompute path).
"""
from __future__ import annotations

import pytest

from pipeline.market.cohort import (
    MIN_COHORT_N,
    YEAR_BAND_RADIUS,
    divergence_pct,
    median,
    percentile_cont,
    year_band,
)


class TestPercentileCont:
    def test_ten_evenly_spaced_values_hand_calculated(self) -> None:
        """values = 100..1000 step 100 (n=10). Hand-derived via PG's percentile_cont
        formula: RN = 1 + q*(n-1), CRN=floor(RN), FRN=RN-CRN, interpolate.
          q=0.25 -> RN=3.25 -> x3=300, x4=400 -> 300 + 0.25*100 = 325
          q=0.50 -> RN=5.50 -> x5=500, x6=600 -> 500 + 0.50*100 = 550
          q=0.75 -> RN=7.75 -> x7=700, x8=800 -> 700 + 0.75*100 = 775
        """
        values = [100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0]
        assert percentile_cont(values, 0.25) == pytest.approx(325.0)
        assert percentile_cont(values, 0.50) == pytest.approx(550.0)
        assert percentile_cont(values, 0.75) == pytest.approx(775.0)

    def test_single_value_returns_that_value_for_any_q(self) -> None:
        assert percentile_cont([42.0], 0.0) == 42.0
        assert percentile_cont([42.0], 0.5) == 42.0
        assert percentile_cont([42.0], 1.0) == 42.0

    def test_q_zero_returns_minimum(self) -> None:
        values = [10.0, 20.0, 30.0]
        assert percentile_cont(values, 0.0) == 10.0

    def test_q_one_returns_maximum(self) -> None:
        values = [10.0, 20.0, 30.0]
        assert percentile_cont(values, 1.0) == 30.0

    def test_odd_count_median_is_middle_element(self) -> None:
        values = [5.0, 1.0, 9.0]  # unsorted on purpose to prove caller-sorts contract below
        values_sorted = sorted(values)
        assert median(values_sorted) == 5.0

    def test_empty_input_raises(self) -> None:
        with pytest.raises(ValueError):
            percentile_cont([], 0.5)

    def test_q_out_of_range_raises(self) -> None:
        with pytest.raises(ValueError):
            percentile_cont([1.0, 2.0], 1.5)
        with pytest.raises(ValueError):
            percentile_cont([1.0, 2.0], -0.1)


class TestDivergencePct:
    def test_identical_values_zero_divergence(self) -> None:
        assert divergence_pct(100.0, 100.0) == 0.0

    def test_both_zero_is_zero_divergence(self) -> None:
        assert divergence_pct(0.0, 0.0) == 0.0

    def test_one_zero_is_full_divergence(self) -> None:
        assert divergence_pct(0.0, 50.0) == 100.0

    def test_known_relative_divergence(self) -> None:
        # |100.5 - 100| / max(100.5,100) * 100 = 0.5/100.5*100 ~= 0.4975%
        d = divergence_pct(100.5, 100.0)
        assert d == pytest.approx(0.4975124378109453)

    def test_within_tolerance_example(self) -> None:
        assert divergence_pct(1000.0, 1004.0) < 0.5  # well within the <0.5% cross-check tolerance


class TestYearBand:
    def test_default_radius_is_one(self) -> None:
        assert year_band(2020) == (2019, 2021)

    def test_custom_radius(self) -> None:
        assert year_band(2020, radius=2) == (2018, 2022)


def test_min_cohort_n_matches_carta_anti_noise_rule() -> None:
    """n<8 must never publish a number (iSeeCars pattern, carta §4 M1 row)."""
    assert MIN_COHORT_N == 8


def test_year_band_radius_is_one_per_carta_m1() -> None:
    assert YEAR_BAND_RADIUS == 1
