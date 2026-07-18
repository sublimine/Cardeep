"""Tests for pipeline/wanted/matcher.py — pure scoring functions (08-forum-community F2).

Property tests at the EXACT boundaries the carta names (§4.4, §7.3): year +/-1/+/-2,
km*1.2, price*1.1. No DB required — these are pure functions, the independent
verification leg for the SQL scoring in tests/test_wanted_router.py.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from pipeline.wanted.matcher import (
    GEO_ADJACENT_PROVINCE,
    GEO_OTHER,
    GEO_SAME_PROVINCE,
    VehicleCandidate,
    WantedCriteria,
    compute_match_score,
    geo_component,
    km_component,
    make_model_component,
    price_component,
    reveal_eligible,
    year_component,
)


class TestMakeModelComponent:
    def test_exact_match_scores_one(self):
        assert make_model_component("Volkswagen", "Golf", "Volkswagen", "Golf") == 1.0

    def test_alias_normalizes_through_pipeline_map(self):
        # "vw" and "Volkswagen" both canonicalize to "Volkswagen" via make_normalizer._CANON
        assert make_model_component("vw", "Golf", "VOLKSWAGEN", "golf") == 1.0

    def test_different_make_scores_zero(self):
        assert make_model_component("Ford", "Focus", "Volkswagen", "Golf") == 0.0

    def test_different_model_scores_zero_no_fuzzy(self):
        assert make_model_component("Volkswagen", "Polo", "Volkswagen", "Golf") == 0.0

    def test_null_wanted_model_is_wildcard(self):
        assert make_model_component("Volkswagen", "Passat", "Volkswagen", None) == 1.0

    def test_model_whitespace_and_case_insensitive(self):
        assert make_model_component("Volkswagen", "  Golf  GTI ", "Volkswagen", "golf gti") == 1.0

    def test_both_blank_make_never_matches(self):
        assert make_model_component(None, None, "", None) == 0.0


class TestYearComponent:
    def test_inside_range_scores_one(self):
        assert year_component(2019, 2018, 2020) == 1.0

    def test_exactly_one_year_below_range_scores_one(self):
        assert year_component(2017, 2018, 2020) == 1.0  # dist == YEAR_FULL_RADIUS (1)

    def test_exactly_one_year_above_range_scores_one(self):
        assert year_component(2021, 2018, 2020) == 1.0

    def test_exactly_two_years_below_range_scores_half(self):
        assert year_component(2016, 2018, 2020) == 0.5  # dist == YEAR_HALF_RADIUS (2)

    def test_exactly_two_years_above_range_scores_half(self):
        assert year_component(2022, 2018, 2020) == 0.5

    def test_three_years_out_scores_zero(self):
        assert year_component(2015, 2018, 2020) == 0.0
        assert year_component(2023, 2018, 2020) == 0.0

    def test_single_point_year_min_equals_max(self):
        assert year_component(2020, 2020, 2020) == 1.0
        assert year_component(2021, 2020, 2020) == 1.0
        assert year_component(2022, 2020, 2020) == 0.5
        assert year_component(2023, 2020, 2020) == 0.0

    def test_no_year_criteria_scores_zero(self):
        assert year_component(2020, None, None) == 0.0

    def test_no_vehicle_year_scores_zero(self):
        assert year_component(None, 2018, 2020) == 0.0


class TestKmComponent:
    def test_at_or_under_max_scores_one(self):
        assert km_component(100_000, 120_000) == 1.0
        assert km_component(120_000, 120_000) == 1.0

    def test_just_over_max_scores_half(self):
        assert km_component(120_001, 120_000) == 0.5

    def test_exactly_at_1_2x_multiplier_scores_half(self):
        assert km_component(144_000, 120_000) == 0.5  # 120_000 * 1.2 == 144_000

    def test_just_over_1_2x_multiplier_scores_zero(self):
        assert km_component(144_001, 120_000) == 0.0

    def test_missing_criteria_scores_zero(self):
        assert km_component(100_000, None) == 0.0
        assert km_component(None, 120_000) == 0.0


class TestPriceComponent:
    def test_at_or_under_max_scores_one(self):
        assert price_component(15_000, 15_000) == 1.0

    def test_exactly_at_1_1x_multiplier_scores_half(self):
        assert price_component(16_500, 15_000) == 0.5  # 15_000 * 1.1 == 16_500

    def test_just_over_1_1x_multiplier_scores_zero(self):
        assert price_component(16_500.01, 15_000) == 0.0

    def test_missing_criteria_scores_zero(self):
        assert price_component(15_000, None) == 0.0


class TestGeoComponent:
    ADJ = frozenset({"29", "41", "14", "11"})  # Malaga's real neighbours (11,14,18,29,41)

    def test_same_province_scores_full(self):
        assert geo_component("29", "29", self.ADJ) == GEO_SAME_PROVINCE

    def test_adjacent_province_scores_partial(self):
        assert geo_component("41", "29", self.ADJ) == GEO_ADJACENT_PROVINCE

    def test_distant_province_scores_minimum(self):
        assert geo_component("08", "29", self.ADJ) == GEO_OTHER

    def test_null_vehicle_province_scores_minimum(self):
        assert geo_component(None, "29", self.ADJ) == GEO_OTHER


class TestComputeMatchScore:
    def test_perfect_match_scores_100(self):
        wanted = WantedCriteria("Volkswagen", "Golf", 2018, 2020, 120_000, 15_000, "29")
        vehicle = VehicleCandidate("Volkswagen", "Golf", 2019, 80_000, 12_000, "29")
        assert compute_match_score(wanted, vehicle, frozenset()) == 100.0

    def test_carta_worked_example_antequera_golf(self):
        # carta §6.1's own example: "Golf 2.0 TDI en Antequera" matching a Malaga-area request.
        wanted = WantedCriteria("Volkswagen", "Golf", 2017, 2019, 120_000, 15_000, "29")
        vehicle = VehicleCandidate("Volkswagen", "Golf", 2018, 60_000, 14_200, "29")
        assert compute_match_score(wanted, vehicle, frozenset()) == 100.0

    def test_wrong_make_still_scores_but_below_listing_threshold_is_not_asserted_here(self):
        # Documents the formula's own edge case (module docstring): a non-matching make
        # contributes 0 on that axis alone; the SQL query never surfaces such a row at all
        # (WHERE-filtered by make before scoring — see build_candidate_query).
        wanted = WantedCriteria("Volkswagen", "Golf", 2018, 2020, 120_000, 15_000, "29")
        vehicle = VehicleCandidate("Ford", "Focus", 2019, 80_000, 12_000, "29")
        score = compute_match_score(wanted, vehicle, frozenset())
        assert score == 15.0 + 15.0 + 20.0 + 15.0  # year + km + price + geo, make_model=0

    def test_score_is_deterministic_and_bounded(self):
        wanted = WantedCriteria("BMW", "Serie 3", 2015, 2017, 150_000, 20_000, "28")
        vehicle = VehicleCandidate("BMW", "Serie 3", 2010, 300_000, 40_000, "08")
        score = compute_match_score(wanted, vehicle, frozenset())
        assert 0.0 <= score <= 100.0
        assert score == compute_match_score(wanted, vehicle, frozenset())  # pure, no side effects


NOW = datetime(2026, 7, 18, tzinfo=timezone.utc)


class TestRevealEligible:
    def test_both_submitted_reveals_immediately(self):
        t1 = NOW - timedelta(days=1)
        assert reveal_eligible(t1, NOW, NOW) is True

    def test_only_one_side_within_window_stays_hidden(self):
        t1 = NOW - timedelta(days=5)
        assert reveal_eligible(t1, None, NOW) is False

    def test_only_one_side_past_window_reveals(self):
        t1 = NOW - timedelta(days=15)
        assert reveal_eligible(t1, None, NOW) is True

    def test_neither_side_submitted_stays_hidden(self):
        assert reveal_eligible(None, None, NOW) is False

    def test_exactly_14_days_reveals(self):
        t1 = NOW - timedelta(days=14)
        assert reveal_eligible(t1, None, NOW) is True


def test_log10_gravity_not_used_here_placeholder():
    # Guard against accidental drift: this module owns ONLY the wanted-board matcher,
    # not the forum ranking formula (§4.1, separate module pipeline/forum/ranking.py).
    assert not hasattr(__import__("pipeline.wanted.matcher", fromlist=["dummy"]), "rank_score")
