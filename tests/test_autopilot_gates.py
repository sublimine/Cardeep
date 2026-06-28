"""Tests for pipeline/autopilot/gates.py — the campaign gate registry (GASTO / PROD / LEGAL).

The doctrine under test (plans/country-autopilot/01-ARCHITECTURE.md, "Las PUERTAS"):
a campaign gate PARKS — it returns a ``GATED`` / PENDIENTE-OWNER result WITHOUT raising and
WITHOUT stopping the loop. A closed gate marks its item PENDING-OWNER; the orchestrator records
that and proceeds to the next country (the never-stop doctrine). This is the *aparca-no-detiene*
frontier, and it is the opposite of ``config_guard``'s fail-closed RAISE.

These are pure, DB-less, network-less unit tests. ``CARDEEP_ENV`` is controlled per-test via
monkeypatch; the default suite (CARDEEP_ENV unset) arms no prod guard, so behaviour is
byte-identical. The PROD-gate tests pass DSN *strings* to config_guard, which only does string
matching — nothing ever connects to a database.
"""
from __future__ import annotations

import pytest

from pipeline import config_guard
from pipeline.autopilot.gates import (
    DEFAULT_GATES,
    BUDGET_ENV,
    CampaignAction,
    GastoGate,
    GateStatus,
    LegalGate,
    ProdGate,
    clear_to_proceed,
    evaluate_gates,
    parked,
)

pytestmark = pytest.mark.unit

# A dev-default DSN carrying the credential config_guard treats as "no real DSN supplied".
_DEV_DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"


def _clear_action(**over) -> CampaignAction:
    """A fully-cleared, €0, dry-run, legal-signed action — every gate should be OPEN."""
    base = dict(country_code="XX", spend_eur=0.0, targets_prod=False, dsn=None, legal_cleared=True)
    base.update(over)
    return CampaignAction(**base)


# ---------------------------------------------------------------------------
# GASTO gate — elevates discover_schedule's requires_env / _gated primitive
# ---------------------------------------------------------------------------
class TestGastoGate:
    def test_zero_spend_is_open(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Today every route is €0; with no spend there is nothing to gate, even without the env.
        monkeypatch.delenv(BUDGET_ENV, raising=False)
        result = GastoGate().check(_clear_action(spend_eur=0.0))
        assert result.status is GateStatus.OPEN
        assert result.is_open

    def test_spend_without_budget_env_parks(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # spend > 0 and no owner budget authorization -> PARK (PENDIENTE-OWNER), never raise.
        monkeypatch.delenv(BUDGET_ENV, raising=False)
        result = GastoGate().check(_clear_action(spend_eur=12.5))
        assert result.status is GateStatus.GATED
        assert result.pending_owner is True
        assert BUDGET_ENV in (result.reason or "")

    def test_spend_with_budget_env_is_open(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Owner unlocked the budget via env -> the spend route is cleared.
        monkeypatch.setenv(BUDGET_ENV, "1")
        result = GastoGate().check(_clear_action(spend_eur=12.5))
        assert result.status is GateStatus.OPEN

    def test_check_never_raises_on_spend(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(BUDGET_ENV, raising=False)
        # Must return a result, not raise — the loop must not crash on a spend route.
        assert GastoGate().check(_clear_action(spend_eur=999.0)).is_gated


# ---------------------------------------------------------------------------
# PROD gate — reuses config_guard, converts its fail-closed RAISE into a PARK
# ---------------------------------------------------------------------------
class TestProdGate:
    def test_dryrun_is_open(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Build + dry-run (:5434) is auto-approved: not targeting prod -> OPEN.
        monkeypatch.delenv("CARDEEP_ENV", raising=False)
        result = ProdGate().check(_clear_action(targets_prod=False))
        assert result.status is GateStatus.OPEN

    def test_live_prod_action_parks(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # A live :5433/prod cutover is structurally the owner's call -> PARK (never raise).
        monkeypatch.delenv("CARDEEP_ENV", raising=False)
        result = ProdGate().check(_clear_action(targets_prod=True))
        assert result.status is GateStatus.GATED
        assert result.pending_owner is True

    def test_prod_failclosed_is_parked_not_raised(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # THE BOUNDARY (aparca-vs-detiene): in prod with the dev-default DSN, config_guard
        # RAISES (fail-closed, detiene). The PROD gate REUSES config_guard but must convert that
        # RAISE into a GATED park (aparca) so the autopilot loop never crashes.
        monkeypatch.setenv("CARDEEP_ENV", "prod")

        # 1) config_guard itself STOPS the world (raises) on the same inputs:
        with pytest.raises(RuntimeError):
            config_guard.require_prod_secrets((_DEV_DSN, "CARDEEP_DSN"))

        # 2) the gate PARKS instead of raising, and surfaces config_guard's reason:
        result = ProdGate().check(_clear_action(targets_prod=True, dsn=_DEV_DSN))
        assert result.status is GateStatus.GATED
        assert result.pending_owner is True
        assert "config_guard" in (result.reason or "").lower()


# ---------------------------------------------------------------------------
# LEGAL gate — no code primitive; an owner-signed legal/ToS clearance
# ---------------------------------------------------------------------------
class TestLegalGate:
    def test_uncleared_parks(self) -> None:
        result = LegalGate().check(_clear_action(legal_cleared=False))
        assert result.status is GateStatus.GATED
        assert result.pending_owner is True

    def test_cleared_is_open(self) -> None:
        result = LegalGate().check(_clear_action(legal_cleared=True))
        assert result.status is GateStatus.OPEN


# ---------------------------------------------------------------------------
# Registry — the frontier: evaluate_gates NEVER stops the loop
# ---------------------------------------------------------------------------
class TestRegistryFrontier:
    def test_clear_action_all_open(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CARDEEP_ENV", raising=False)
        monkeypatch.delenv(BUDGET_ENV, raising=False)
        results = evaluate_gates(_clear_action())
        assert all(r.is_open for r in results)
        assert clear_to_proceed(results) is True
        assert parked(results) == ()

    def test_worst_case_parks_everything_without_raising(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # All three gates closed at once. evaluate_gates must RETURN three parked results and
        # raise NOTHING — proving the loop can mark PENDING-OWNER and carry on (never-stop).
        monkeypatch.setenv("CARDEEP_ENV", "prod")
        monkeypatch.delenv(BUDGET_ENV, raising=False)
        action = CampaignAction(
            country_code="XX", spend_eur=50.0, targets_prod=True, dsn=_DEV_DSN,
            legal_cleared=False,
        )
        results = evaluate_gates(action)  # must not raise
        assert len(results) == len(DEFAULT_GATES) == 3
        assert all(r.is_gated for r in results)
        assert {r.gate for r in results} == {"GASTO", "PROD", "LEGAL"}
        assert clear_to_proceed(results) is False
        assert len(parked(results)) == 3
        # Every parked gate is explicitly PENDIENTE-OWNER.
        assert all(r.pending_owner for r in parked(results))

    def test_one_closed_gate_does_not_mask_open_ones(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Only LEGAL closed; GASTO (€0) and PROD (dry-run) stay open. The loop sees exactly one
        # parked item and the rest clear.
        monkeypatch.delenv("CARDEEP_ENV", raising=False)
        monkeypatch.delenv(BUDGET_ENV, raising=False)
        results = evaluate_gates(_clear_action(legal_cleared=False))
        assert clear_to_proceed(results) is False
        assert [r.gate for r in parked(results)] == ["LEGAL"]

    def test_evaluate_gates_is_pure_no_exception_contract(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Defensive: across a matrix of adversarial actions, evaluate_gates returns and never raises.
        monkeypatch.setenv("CARDEEP_ENV", "prod")
        for spend in (0.0, 0.01, 1_000_000.0):
            for prod in (False, True):
                for legal in (False, True):
                    action = CampaignAction(
                        country_code="XX", spend_eur=spend, targets_prod=prod,
                        dsn=_DEV_DSN, legal_cleared=legal,
                    )
                    results = evaluate_gates(action)  # never raises
                    assert len(results) == 3
                    # Each result is one of the two terminal statuses, never an exception.
                    assert all(r.status in (GateStatus.OPEN, GateStatus.GATED) for r in results)
