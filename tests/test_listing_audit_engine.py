"""TDD for pipeline/marketing/listing_audit.py (C1, plans/cardeep-omni/07-marketing.md
S4/S9 F1: "tests de cada check con fixtures golden (coche perfecto=100, degradaciones
conocidas=puntos exactos)"). Pure unit tests, zero DB, zero network.
"""
from __future__ import annotations

from datetime import date

import pytest

from pipeline.marketing.listing_audit import (
    MIN_PHOTO_HEIGHT,
    MIN_PHOTO_WIDTH,
    STAGNATION_MIN_DROPS,
    TOTAL_POINTS,
    PlatformEdge,
    VehicleAuditInput,
    evaluate,
)

TODAY = date(2026, 7, 18)


def _perfect_input(**overrides) -> VehicleAuditInput:
    base = dict(
        vehicle_ulid="V1",
        price=19900.0,
        make="BMW",
        model="320d",
        year=2021,
        km=68000,
        vin_ref="WBA3A5C50DF595785",
        fuel="Diésel",
        transmission="Automático",
        photo_url="https://cdn.example.com/1.jpg",
        title="BMW 320d 2021 automático azul metalizado 68.000km",
        photo_width=1200,
        photo_height=900,
        platform_edges=(PlatformEdge(platform_price=19900.0, status="listed"),),
        price_drops_30d=0,
        today=TODAY,
    )
    base.update(overrides)
    return VehicleAuditInput(**base)


class TestWeights:
    def test_weights_sum_to_100(self):
        assert TOTAL_POINTS == 100


class TestPerfectCar:
    def test_perfect_vehicle_scores_100(self):
        result = evaluate(_perfect_input())
        assert result.score == 100
        assert all(c.passed for c in result.checks)
        assert result.failed_checks == ()


class TestDegradations:
    def test_no_price_loses_exactly_12(self):
        result = evaluate(_perfect_input(price=None))
        assert result.score == 88
        c1 = next(c for c in result.checks if c.check_id == "c1")
        assert not c1.passed and c1.points_awarded == 0

    def test_zero_price_fails_c1(self):
        result = evaluate(_perfect_input(price=0))
        c1 = next(c for c in result.checks if c.check_id == "c1")
        assert not c1.passed

    def test_missing_model_loses_exactly_10(self):
        result = evaluate(_perfect_input(model=None))
        assert result.score == 90

    def test_invalid_year_loses_exactly_8(self):
        result = evaluate(_perfect_input(year=1850))
        assert result.score == 92
        result_future = evaluate(_perfect_input(year=2200))
        assert result_future.score == 92

    def test_missing_km_loses_exactly_10(self):
        result = evaluate(_perfect_input(km=None))
        assert result.score == 90

    def test_missing_vin_loses_exactly_12(self):
        result = evaluate(_perfect_input(vin_ref=None))
        assert result.score == 88

    def test_listing_id_style_vin_fails_c5(self):
        """The known real-world contamination pattern (04-arbitrage F6): AS24
        listing-IDs mislabeled as vin_ref. Must NOT pass as a valid VIN."""
        result = evaluate(_perfect_input(vin_ref="12345678"))
        c5 = next(c for c in result.checks if c.check_id == "c5")
        assert not c5.passed

    def test_lowercase_vin_still_passes(self):
        result = evaluate(_perfect_input(vin_ref="wba3a5c50df595785"))
        c5 = next(c for c in result.checks if c.check_id == "c5")
        assert c5.passed

    def test_missing_fuel_loses_exactly_6(self):
        result = evaluate(_perfect_input(fuel=None))
        assert result.score == 94

    def test_no_photo_loses_exactly_10(self):
        result = evaluate(_perfect_input(photo_url=None))
        assert result.score == 90

    def test_small_photo_loses_exactly_8(self):
        result = evaluate(_perfect_input(photo_width=640, photo_height=480))
        assert result.score == 92
        c8 = next(c for c in result.checks if c.check_id == "c8")
        assert "640" in c8.message and "480" in c8.message

    def test_unmeasured_photo_dims_fails_honestly_not_silently(self):
        """Carta: never fabricate a pass. Unmeasured dims must fail c8, with a
        message distinguishing 'unknown' from 'measured and too small'."""
        result = evaluate(_perfect_input(photo_width=None, photo_height=None))
        c8 = next(c for c in result.checks if c.check_id == "c8")
        assert not c8.passed
        assert c8.evidence["measured"] is False
        assert "aún" in c8.message or "pendiente" in c8.message

    def test_exact_minimum_photo_size_passes(self):
        result = evaluate(_perfect_input(photo_width=MIN_PHOTO_WIDTH, photo_height=MIN_PHOTO_HEIGHT))
        c8 = next(c for c in result.checks if c.check_id == "c8")
        assert c8.passed

    def test_poor_title_loses_exactly_6(self):
        result = evaluate(_perfect_input(title="BMW 320d 2021"))
        assert result.score == 94

    def test_no_title_fails_c9(self):
        result = evaluate(_perfect_input(title=None))
        c9 = next(c for c in result.checks if c.check_id == "c9")
        assert not c9.passed

    def test_price_divergence_loses_exactly_10(self):
        result = evaluate(_perfect_input(
            platform_edges=(PlatformEdge(platform_price=18900.0, status="listed"),)
        ))
        assert result.score == 90
        c10 = next(c for c in result.checks if c.check_id == "c10")
        assert "18900.0€" in c10.message

    def test_removed_edge_never_counts_against_c10(self):
        result = evaluate(_perfect_input(
            platform_edges=(PlatformEdge(platform_price=99999.0, status="removed"),)
        ))
        c10 = next(c for c in result.checks if c.check_id == "c10")
        assert c10.passed

    def test_no_edges_passes_c10_vacuously(self):
        result = evaluate(_perfect_input(platform_edges=()))
        c10 = next(c for c in result.checks if c.check_id == "c10")
        assert c10.passed

    def test_stagnation_signal_loses_exactly_8(self):
        result = evaluate(_perfect_input(price_drops_30d=STAGNATION_MIN_DROPS))
        assert result.score == 92
        c11 = next(c for c in result.checks if c.check_id == "c11")
        assert not c11.passed

    def test_one_drop_does_not_trigger_stagnation(self):
        result = evaluate(_perfect_input(price_drops_30d=1))
        c11 = next(c for c in result.checks if c.check_id == "c11")
        assert c11.passed

    def test_worst_reachable_score_is_10_not_0(self):
        """c10 (price coherence) can only ever FAIL when v.price is known (you cannot
        diverge from a price you don't have) -- so a vehicle with price=None always
        vacuously passes c10, and the true floor of this engine is 10, never 0. This
        is a documented property of the design, not a scoring bug: c1 (price) and c10
        (coherence) can never both fail from the same vehicle."""
        result = evaluate(VehicleAuditInput(
            vehicle_ulid="V-worst", price=None, make=None, model=None, year=None,
            km=None, vin_ref=None, fuel=None, transmission=None, photo_url=None,
            title=None, photo_width=None, photo_height=None,
            platform_edges=(PlatformEdge(platform_price=1.0, status="listed"),),
            price_drops_30d=5, today=TODAY,
        ))
        assert result.score == 10
        passed_ids = [c.check_id for c in result.checks if c.passed]
        assert passed_ids == ["c10"]

    def test_worst_reachable_score_with_price_present_is_12(self):
        """When price IS present (so c10 can genuinely fail on divergence), the floor
        rises to exactly c1's 12 points -- confirms c1/c10 are mutually exclusive
        failure modes by construction."""
        result = evaluate(VehicleAuditInput(
            vehicle_ulid="V-worst-priced", price=19900.0, make=None, model=None,
            year=None, km=None, vin_ref=None, fuel=None, transmission=None,
            photo_url=None, title=None, photo_width=None, photo_height=None,
            platform_edges=(PlatformEdge(platform_price=1.0, status="listed"),),
            price_drops_30d=5, today=TODAY,
        ))
        assert result.score == 12
        passed_ids = [c.check_id for c in result.checks if c.passed]
        assert passed_ids == ["c1"]


class TestEvidencePersisted:
    def test_every_check_carries_evidence_and_message(self):
        result = evaluate(_perfect_input())
        for c in result.checks:
            assert c.evidence is not None
            assert c.message
            assert c.points_possible > 0

    def test_checks_count_is_eleven(self):
        result = evaluate(_perfect_input())
        assert len(result.checks) == 11
