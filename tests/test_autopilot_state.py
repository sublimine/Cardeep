"""Tests for pipeline/autopilot/state.py — the country-autopilot campaign state machine.

Two layers, mirroring the gestion_item suite (tests/test_gestionador.py):

  * PURE (no DB): the transition machine itself — ``assert_valid_transition`` accepts every
    legal edge of REGISTERED -> KNOW_COUNTRY -> BOOTSTRAPPED -> IN_COVERAGE -> SEALED and REJECTS
    every illegal one (skip, regression, leaving the terminal SEALED, unknown state). These are
    the ``@pytest.mark.unit`` predicates and need no database.

  * INTEGRATION (:5434 dry-run only): a real campaign is registered and walked all the way
    REGISTERED -> ... -> SEALED through ``register`` / ``transition`` against migration 0067, and
    the append-only ``country_campaign_transition`` ledger is asserted to hold one row per hop.
    The whole walk runs inside an asyncpg transaction that is ROLLED BACK, so the dry-run census
    is left byte-identical (zero residue). Hard-pinned to :5434; refuses :5433 (live prod).

ISOLATION (inviolable): the integration layer NEVER touches :5433. It refuses any DSN that
mentions :5433 and skips when the dry-run DB is unreachable.
"""
from __future__ import annotations

import asyncio
import os

import pytest

from pipeline.autopilot.state import (
    ALL_STATES,
    BOOTSTRAPPED,
    IN_COVERAGE,
    INITIAL_STATE,
    KNOW_COUNTRY,
    REGISTERED,
    SEALED,
    VALID_TRANSITIONS,
    CampaignTransitionError,
    assert_valid_transition,
    current_state,
    next_state,
    register,
    transition,
)

# The canonical forward lifecycle (the bible's COVER(CC) progression).
FORWARD_PATH = [REGISTERED, KNOW_COUNTRY, BOOTSTRAPPED, IN_COVERAGE, SEALED]


# ===========================================================================
# PURE unit layer — the state machine (no DB, no network)
# ===========================================================================
class TestStateMachineShape:
    """The machine declares exactly the five lifecycle states, SEALED terminal."""

    pytestmark = pytest.mark.unit

    def test_all_five_states_present(self) -> None:
        assert ALL_STATES == frozenset(FORWARD_PATH)

    def test_initial_state_is_registered(self) -> None:
        assert INITIAL_STATE == REGISTERED

    def test_sealed_is_terminal(self) -> None:
        assert VALID_TRANSITIONS[SEALED] == set()

    def test_each_nonterminal_has_exactly_one_forward_edge(self) -> None:
        # The lifecycle is strictly linear: every non-terminal state advances to exactly one next.
        for frm, to in zip(FORWARD_PATH, FORWARD_PATH[1:]):
            assert VALID_TRANSITIONS[frm] == {to}


class TestLegalTransitions:
    """Every forward edge of the lifecycle is accepted."""

    pytestmark = pytest.mark.unit

    @pytest.mark.parametrize("frm, to", list(zip(FORWARD_PATH, FORWARD_PATH[1:])))
    def test_forward_edge_accepted(self, frm: str, to: str) -> None:
        # Act / Assert — must not raise.
        assert_valid_transition(frm, to)

    def test_initial_registration_accepted(self) -> None:
        # from_state is None only for the birth transition, which must target REGISTERED.
        assert_valid_transition(None, REGISTERED)

    def test_next_state_walks_the_linear_path(self) -> None:
        # Arrange / Act / Assert
        assert next_state(REGISTERED) == KNOW_COUNTRY
        assert next_state(KNOW_COUNTRY) == BOOTSTRAPPED
        assert next_state(BOOTSTRAPPED) == IN_COVERAGE
        assert next_state(IN_COVERAGE) == SEALED
        assert next_state(SEALED) is None  # terminal


class TestIllegalTransitionsRejected:
    """Illegal edges RAISE — the core fail-closed guard."""

    pytestmark = pytest.mark.unit

    def test_skip_state_rejected(self) -> None:
        # REGISTERED cannot jump straight to BOOTSTRAPPED (skips KNOW_COUNTRY).
        with pytest.raises(CampaignTransitionError):
            assert_valid_transition(REGISTERED, BOOTSTRAPPED)

    def test_skip_to_sealed_rejected(self) -> None:
        with pytest.raises(CampaignTransitionError):
            assert_valid_transition(REGISTERED, SEALED)

    def test_regression_rejected(self) -> None:
        # Going backward is illegal (the lifecycle only advances).
        with pytest.raises(CampaignTransitionError):
            assert_valid_transition(BOOTSTRAPPED, KNOW_COUNTRY)
        with pytest.raises(CampaignTransitionError):
            assert_valid_transition(IN_COVERAGE, REGISTERED)

    def test_terminal_sealed_rejects_every_move(self) -> None:
        for to in FORWARD_PATH:
            with pytest.raises(CampaignTransitionError):
                assert_valid_transition(SEALED, to)

    def test_self_loop_rejected(self) -> None:
        with pytest.raises(CampaignTransitionError):
            assert_valid_transition(KNOW_COUNTRY, KNOW_COUNTRY)

    def test_unknown_target_state_rejected(self) -> None:
        with pytest.raises(CampaignTransitionError):
            assert_valid_transition(REGISTERED, "DECOMMISSIONED")

    def test_unknown_source_state_rejected(self) -> None:
        with pytest.raises(CampaignTransitionError):
            assert_valid_transition("PURGATORY", KNOW_COUNTRY)

    def test_initial_transition_must_target_registered(self) -> None:
        with pytest.raises(CampaignTransitionError):
            assert_valid_transition(None, KNOW_COUNTRY)

    def test_error_is_a_valueerror(self) -> None:
        # A CampaignTransitionError must remain a ValueError so existing `except ValueError`
        # handlers (the gestion convention) still catch an illegal campaign move.
        assert issubclass(CampaignTransitionError, ValueError)


# ===========================================================================
# INTEGRATION layer — a real campaign on the :5434 dry-run DB (rolled back)
# ===========================================================================
_DRYRUN_DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5434/cardeep"
_SYNTHETIC_CC = "XX"  # the architecture's synthetic onboarding country; never a real tenant


def _target_dsn() -> str:
    return os.environ.get("CARDEEP_DSN", _DRYRUN_DSN)


class _Rollback(Exception):
    """Sentinel: forces the asyncpg transaction to abort cleanly at test end."""


def _db_available() -> bool:
    dsn = _target_dsn()
    if "5433" in dsn:
        return False  # never probe live prod
    try:
        return asyncio.run(_ping(dsn))
    except Exception:
        return False


async def _ping(dsn: str) -> bool:
    try:
        import asyncpg
        conn = await asyncpg.connect(dsn, timeout=3)
        await conn.close()
        return True
    except Exception:
        return False


DB_AVAILABLE = _db_available()


@pytest.mark.integration
@pytest.mark.skipif(
    not DB_AVAILABLE,
    reason="dry-run cardeep-pg not reachable at :5434 (or CARDEEP_DSN points at :5433)",
)
class TestCampaignProgressionOnDryRun:
    """A synthetic 'XX' campaign walks REGISTERED -> SEALED, all inside an aborted txn."""

    def test_refuses_live_prod_dsn(self) -> None:
        # The mandate: this golden NEVER runs against :5433. Make the refusal explicit.
        assert "5433" not in _target_dsn(), "integration DSN must be the :5434 dry-run"

    def test_full_progression_and_append_only_ledger(self) -> None:
        asyncio.run(self._run_progression())

    async def _run_progression(self) -> None:
        import asyncpg

        dsn = _target_dsn()
        assert "5433" not in dsn  # belt-and-braces inside the coroutine
        conn = await asyncpg.connect(dsn)
        try:
            with pytest.raises(_Rollback):
                async with conn.transaction():
                    # Pre-condition: the synthetic campaign must not already exist in the dry-run.
                    assert await current_state(conn, _SYNTHETIC_CC) is None

                    # Birth in REGISTERED.
                    state = await register(conn, _SYNTHETIC_CC, actor="test")
                    assert state == REGISTERED
                    assert await current_state(conn, _SYNTHETIC_CC) == REGISTERED

                    # register is idempotent: a second call neither errors nor double-appends.
                    assert await register(conn, _SYNTHETIC_CC, actor="test") == REGISTERED

                    # Walk every forward hop to SEALED.
                    for to in FORWARD_PATH[1:]:
                        await transition(conn, _SYNTHETIC_CC, to, actor="test",
                                         note=f"advance to {to}")
                        assert await current_state(conn, _SYNTHETIC_CC) == to

                    assert await current_state(conn, _SYNTHETIC_CC) == SEALED

                    # Append-only ledger: exactly one row per hop (birth + 4 advances = 5),
                    # and the recorded to_state sequence equals the forward path.
                    rows = await conn.fetch(
                        "SELECT from_state, to_state FROM country_campaign_transition "
                        "WHERE country_code = $1 ORDER BY id",
                        _SYNTHETIC_CC,
                    )
                    assert [r["to_state"] for r in rows] == FORWARD_PATH
                    assert rows[0]["from_state"] is None  # birth has no from_state

                    raise _Rollback()
        finally:
            await conn.close()

    def test_illegal_transition_raises_on_live_machine(self) -> None:
        asyncio.run(self._run_illegal())

    async def _run_illegal(self) -> None:
        import asyncpg

        dsn = _target_dsn()
        assert "5433" not in dsn
        conn = await asyncpg.connect(dsn)
        try:
            with pytest.raises(_Rollback):
                async with conn.transaction():
                    await register(conn, _SYNTHETIC_CC, actor="test")
                    # REGISTERED -> IN_COVERAGE is an illegal skip; it must RAISE and write nothing.
                    with pytest.raises(CampaignTransitionError):
                        await transition(conn, _SYNTHETIC_CC, IN_COVERAGE, actor="test")
                    # State is unchanged after the rejected move.
                    assert await current_state(conn, _SYNTHETIC_CC) == REGISTERED
                    raise _Rollback()
        finally:
            await conn.close()

    def test_transition_unknown_campaign_raises(self) -> None:
        asyncio.run(self._run_unknown())

    async def _run_unknown(self) -> None:
        import asyncpg

        dsn = _target_dsn()
        assert "5433" not in dsn
        conn = await asyncpg.connect(dsn)
        try:
            with pytest.raises(_Rollback):
                async with conn.transaction():
                    # No register() first -> the campaign does not exist -> RAISE (no silent create).
                    with pytest.raises(CampaignTransitionError):
                        await transition(conn, "ZZ", KNOW_COUNTRY, actor="test")
                    raise _Rollback()
        finally:
            await conn.close()
