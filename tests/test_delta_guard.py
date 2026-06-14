"""Unit tests for B2.3 — pipeline/delta_guard.py::should_emit_gone.

All tests use synthetic data.  No DB connection, no scraper invocation.
Strategy: exhaustively cover all decision branches in should_emit_gone,
including boundary conditions at the exact thresholds.
"""
from __future__ import annotations

import pytest

from pipeline.delta_guard import (
    DECLARED_THRESHOLD,
    PREVIOUS_THRESHOLD,
    should_emit_gone,
)


# ---------------------------------------------------------------------------
# Branch 1: declared count is available (primary probe)
# ---------------------------------------------------------------------------

class TestDeclaredProbe:
    """should_emit_gone with a real declared count."""

    def test_harvested_at_threshold_exactly_allowed(self) -> None:
        """Exactly at declared * 0.95 → allowed (boundary: inclusive)."""
        declared = 100
        harvested = int(declared * DECLARED_THRESHOLD)  # 95
        allow, reason = should_emit_gone(harvested=harvested, declared=declared)
        assert allow is True, f"Expected allow=True at exact threshold; got reason={reason!r}"
        assert "declared probe" in reason

    def test_harvested_98_declared_100_allowed(self) -> None:
        """Scenario (a): harvested=98, declared=100 → GONE permitted."""
        allow, reason = should_emit_gone(harvested=98, declared=100)
        assert allow is True
        assert "declared probe" in reason

    def test_harvested_60_declared_100_blocked(self) -> None:
        """Scenario (b): harvested=60, declared=100 → GONE blocked with reason."""
        allow, reason = should_emit_gone(harvested=60, declared=100)
        assert allow is False
        assert "partial harvest" in reason
        assert "60" in reason
        assert "declared probe" in reason

    def test_harvested_94_declared_100_blocked(self) -> None:
        """Just below 95 % threshold (94/100) must be blocked."""
        allow, reason = should_emit_gone(harvested=94, declared=100)
        assert allow is False, "94/100 < 0.95; must block"
        assert "partial harvest" in reason

    def test_harvested_100_declared_100_allowed(self) -> None:
        """Full harvest (100 %) is always allowed."""
        allow, reason = should_emit_gone(harvested=100, declared=100)
        assert allow is True

    def test_harvested_zero_declared_positive_blocked(self) -> None:
        """Zero vehicles harvested against a positive declared total → blocked."""
        allow, reason = should_emit_gone(harvested=0, declared=50)
        assert allow is False
        assert "partial harvest" in reason

    def test_declared_zero_harvested_zero_allowed(self) -> None:
        """Declared=0 (empty lot): 0 >= 0 * 0.95 = 0 → allowed (nothing to GONE)."""
        allow, reason = should_emit_gone(harvested=0, declared=0)
        assert allow is True

    def test_large_catalog_above_threshold(self) -> None:
        """5000-car lot with 4800 harvested (96 %) → allowed."""
        allow, reason = should_emit_gone(harvested=4800, declared=5000)
        assert allow is True

    def test_large_catalog_below_threshold(self) -> None:
        """5000-car lot with 2000 harvested (40 %) → blocked."""
        allow, reason = should_emit_gone(harvested=2000, declared=5000)
        assert allow is False


# ---------------------------------------------------------------------------
# Branch 2: no declared count — fallback to previous_available
# ---------------------------------------------------------------------------

class TestFallbackProbe:
    """should_emit_gone when declared is None (no site-level denominator)."""

    def test_scenario_c_blocked(self) -> None:
        """Scenario (c): declared=None, harvested=50, previous=120 → blocked.

        50 < 0.50 * 120 = 60 → partial harvest, suppress GONE.
        """
        allow, reason = should_emit_gone(
            harvested=50, declared=None, previous_available=120
        )
        assert allow is False
        assert "partial harvest" in reason
        assert "fallback probe" in reason
        assert "50" in reason
        assert "120" in reason

    def test_scenario_d_allowed(self) -> None:
        """Scenario (d): declared=None, harvested=80, previous=120 → allowed.

        80 >= 0.50 * 120 = 60 → sweep permitted.
        """
        allow, reason = should_emit_gone(
            harvested=80, declared=None, previous_available=120
        )
        assert allow is True
        assert "fallback probe" in reason
        assert "conservative fallback applied" in reason

    def test_fallback_exactly_at_threshold_allowed(self) -> None:
        """Exactly at previous * 0.50 → allowed (boundary: inclusive)."""
        previous = 200
        harvested = int(previous * PREVIOUS_THRESHOLD)  # 100
        allow, reason = should_emit_gone(
            harvested=harvested, declared=None, previous_available=previous
        )
        assert allow is True

    def test_fallback_just_below_threshold_blocked(self) -> None:
        """One below the 50 % floor → blocked."""
        previous = 200
        harvested = int(previous * PREVIOUS_THRESHOLD) - 1  # 99
        allow, reason = should_emit_gone(
            harvested=harvested, declared=None, previous_available=previous
        )
        assert allow is False

    def test_no_previous_available_first_run(self) -> None:
        """First-ever run: declared=None, previous_available=None → allowed.

        No previous inventory means there is nothing to falsely GONE.
        """
        allow, reason = should_emit_gone(
            harvested=5, declared=None, previous_available=None
        )
        assert allow is True
        assert "first run" in reason or "no previous" in reason.lower()

    def test_previous_available_zero_treated_as_first_run(self) -> None:
        """previous_available=0 (empty DB): allowed, nothing to falsely retire."""
        allow, reason = should_emit_gone(
            harvested=0, declared=None, previous_available=0
        )
        assert allow is True

    def test_inventory_contraction_within_tolerance(self) -> None:
        """Legitimate 40 % contraction: 60 harvested from 100 previous → allowed (60 >= 50)."""
        allow, reason = should_emit_gone(
            harvested=60, declared=None, previous_available=100
        )
        assert allow is True

    def test_inventory_contraction_beyond_tolerance_blocked(self) -> None:
        """Suspect 90 % contraction: 10 from 100 previous → blocked (10 < 50)."""
        allow, reason = should_emit_gone(
            harvested=10, declared=None, previous_available=100
        )
        assert allow is False


# ---------------------------------------------------------------------------
# Return type contract
# ---------------------------------------------------------------------------

class TestReturnContract:
    """should_emit_gone always returns (bool, non-empty str)."""

    @pytest.mark.parametrize(
        "harvested, declared, previous",
        [
            (98, 100, None),
            (60, 100, None),
            (50, None, 120),
            (80, None, 120),
            (0, None, None),
            (100, 0, None),
        ],
    )
    def test_return_type_is_tuple_bool_str(
        self, harvested: int, declared: int | None, previous: int | None
    ) -> None:
        result = should_emit_gone(
            harvested=harvested, declared=declared, previous_available=previous
        )
        allow, reason = result
        assert isinstance(allow, bool), "First element must be bool"
        assert isinstance(reason, str), "Second element must be str"
        assert len(reason) > 0, "Reason must not be empty"


# ---------------------------------------------------------------------------
# Threshold constants sanity
# ---------------------------------------------------------------------------

class TestConstants:
    def test_declared_threshold_is_095(self) -> None:
        assert DECLARED_THRESHOLD == 0.95

    def test_previous_threshold_is_050(self) -> None:
        assert PREVIOUS_THRESHOLD == 0.50
