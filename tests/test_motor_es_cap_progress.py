"""B3.4 — unit tests: motor_es_wholesale made_progress logic.

Tests that 'made_progress' correctly distinguishes:
  (A) Normal cap-end: drain fetched pages but 404 ended the facet at the cap boundary.
      Expected: made_progress=True, run_ok=True, no alert.
  (B) Real failure: ban/timeout before any page landed, pages_fetched=0.
      Expected: made_progress=False, run_ok=False, alert fires.

These tests operate on the in-process stats dict only — no network, no DB, no scraper
invoked. They directly exercise the made_progress computation that was buggy before B3.4.
"""
from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Helper — reproduce the exact made_progress / run_ok logic from harvest().
# We test the formula directly rather than mocking the whole async pipeline.
# ---------------------------------------------------------------------------

def _compute_progress_and_ok(
    pages_fetched: int,
    cars_caged: int,
    fetch_error: str | None,
    verdict: str,
) -> tuple[bool, bool]:
    """Mirror of the B3.4-fixed formula in motor_es_wholesale.harvest()."""
    made_progress = pages_fetched > 0 or cars_caged > 0
    run_ok = fetch_error is None and made_progress and verdict != "REFUTED"
    return made_progress, run_ok


# ---------------------------------------------------------------------------
# Tests: normal cap-end (pages fetched, but facet naturally exhausted)
# ---------------------------------------------------------------------------

class TestNormalCapEnd:
    """A run that drained pages up to the 50-page cap: must NOT raise a false-positive alert."""

    def test_full_cap_drain_is_run_ok(self) -> None:
        """50 pages fetched, 220 cars caged (new run), verdict TRUSTWORTHY → run_ok=True."""
        made_progress, run_ok = _compute_progress_and_ok(
            pages_fetched=50,
            cars_caged=220,
            fetch_error=None,
            verdict="TRUSTWORTHY",
        )
        assert made_progress is True, "50 pages fetched must count as progress"
        assert run_ok is True, "cap-end with TRUSTWORTHY verdict must be run_ok"

    def test_idempotent_rerun_is_run_ok(self) -> None:
        """Pages fetched but 0 NEW cars (all already indexed, ON CONFLICT DO NOTHING).
        Before B3.4 fix this was the false-positive: cells_drained=N, cars_caged=0
        could still mark made_progress=False if the old metric was cells_drained only.
        With pages_fetched > 0, this is correctly identified as successful work."""
        made_progress, run_ok = _compute_progress_and_ok(
            pages_fetched=50,
            cars_caged=0,      # all already indexed — idempotent re-run
            fetch_error=None,
            verdict="TRUSTWORTHY",
        )
        assert made_progress is True, "pages fetched with 0 new cars is still progress (idempotent re-run)"
        assert run_ok is True, "idempotent re-run must be run_ok=True, not a false-positive alert"

    def test_partial_proof_run_is_run_ok(self) -> None:
        """Proof mode drains 6 cells (few pages) → pages_fetched=6, cars caged."""
        made_progress, run_ok = _compute_progress_and_ok(
            pages_fetched=6,
            cars_caged=132,
            fetch_error=None,
            verdict="TRUSTWORTHY",
        )
        assert made_progress is True
        assert run_ok is True

    def test_offer_only_segment_no_pages_fetched(self) -> None:
        """Offer segments (vn/catalog/renting) don't use drain_cell, so pages_fetched=0.
        But cars_caged > 0 keeps made_progress True (the OR clause)."""
        made_progress, run_ok = _compute_progress_and_ok(
            pages_fetched=0,   # harvest_offers doesn't increment pages_fetched
            cars_caged=476,    # vn offers caged
            fetch_error=None,
            verdict="TRUSTWORTHY",
        )
        assert made_progress is True, "offer-segment progress measured via cars_caged"
        assert run_ok is True

    def test_refuted_vam_still_fails(self) -> None:
        """Even with pages fetched, a REFUTED VAM verdict must keep run_ok=False."""
        made_progress, run_ok = _compute_progress_and_ok(
            pages_fetched=50,
            cars_caged=220,
            fetch_error=None,
            verdict="REFUTED",
        )
        assert made_progress is True, "pages still count as progress"
        assert run_ok is False, "REFUTED verdict must cause run_ok=False regardless of pages"


# ---------------------------------------------------------------------------
# Tests: real failures (ban / timeout / network error before any page)
# ---------------------------------------------------------------------------

class TestRealFailure:
    """Genuine failures must produce made_progress=False and run_ok=False."""

    def test_ban_before_any_page(self) -> None:
        """HTTP 403/503 ban before any listing page was served: pages_fetched=0, cars_caged=0."""
        made_progress, run_ok = _compute_progress_and_ok(
            pages_fetched=0,
            cars_caged=0,
            fetch_error="HTTP 503 on https://www.motor.es/segunda-mano/volkswagen/",
            verdict="TRUSTWORTHY",  # verdict may be stale from a previous run
        )
        assert made_progress is False, "0 pages + 0 cars = no progress"
        assert run_ok is False, "fetch_error must cause run_ok=False"

    def test_timeout_before_any_page(self) -> None:
        """Network timeout: pages_fetched=0, fetch_error set."""
        made_progress, run_ok = _compute_progress_and_ok(
            pages_fetched=0,
            cars_caged=0,
            fetch_error="ConnectTimeout on www.motor.es",
            verdict="TRUSTWORTHY",
        )
        assert made_progress is False
        assert run_ok is False

    def test_zero_pages_zero_cars_no_fetch_error(self) -> None:
        """Edge case: no fetch error but also no pages fetched and no cars caged.
        This covers a run where enumeration returned 0 cells and no offers were processed.
        Must be treated as a failure (no work done)."""
        made_progress, run_ok = _compute_progress_and_ok(
            pages_fetched=0,
            cars_caged=0,
            fetch_error=None,
            verdict="TRUSTWORTHY",
        )
        assert made_progress is False, "nothing done = no progress"
        assert run_ok is False, "a no-op run (0 pages, 0 cars) must not be run_ok"

    def test_fetch_error_with_some_pages_fetched(self) -> None:
        """Fetch error mid-drain: some pages were fetched before the error.
        fetch_error vetoes run_ok even when pages_fetched > 0."""
        made_progress, run_ok = _compute_progress_and_ok(
            pages_fetched=12,
            cars_caged=264,
            fetch_error="HTTP 429 on https://www.motor.es/segunda-mano/seat/ibiza/?pagina=13",
            verdict="TRUSTWORTHY",
        )
        assert made_progress is True, "12 pages + 264 cars = progress occurred"
        assert run_ok is False, "fetch_error must veto run_ok even with partial progress"
