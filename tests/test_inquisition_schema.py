"""Tests for migrations/0032_inquisition.sql — the V3 Inquisition tabular foundation.

The load-bearing assertion: the trustworthy_needs_independence CHECK makes Laws II+III
(Producer Exclusion + Orthogonal Quorum) a DATABASE INVARIANT — it is physically
impossible to persist a TRUSTWORTHY verdict without >=2 asserting skeptics, an
independence score >=2, and zero un-vetoed hard refutations. We prove that directly
against the live schema (rolled back, no pollution).

These are REAL-DB tests on purpose: the invariant lives in Postgres, not in Python, so
a mocked connection could not exercise it (the lesson from the gestionador mock blind
spot that hid a shipped crash). Pattern mirrors test_inquisition_schedule.py.
"""
from __future__ import annotations

import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"


async def _ping() -> bool:
    try:
        import asyncpg
        conn = await asyncpg.connect(DSN, timeout=3)
        await conn.close()
        return True
    except Exception:
        return False


def _db_available() -> bool:
    try:
        import asyncpg  # noqa: F401
        return asyncio.run(_ping())
    except Exception:
        return False


DB_AVAILABLE = _db_available()


class _Rollback(Exception):
    """Sentinel that forces transaction rollback without persisting any state."""


_CLAIM_INSERT = """
    INSERT INTO inquisition_claim (claim_id, subject_type, subject_key, claim, producer_state)
    VALUES ($1, $2, 'test_subject', 'test claim', '{}'::jsonb)
"""
_VERDICT_INSERT = """
    INSERT INTO inquisition_verdict
        (claim_id, verdict, indep_score, assert_n, refute_soft_n, refute_hard_n, abstain_n)
    VALUES ($1, $2, $3, $4, 0, $5, 0)
"""


@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestTrustworthyInvariant:
    """trustworthy_needs_independence: TRUSTWORTHY requires indep>=2 AND assert>=2 AND hard=0."""

    def test_trustworthy_with_low_indep_is_rejected(self) -> None:
        asyncio.run(self._reject("TRUSTWORTHY", indep=1, assert_n=2, hard=0))

    def test_trustworthy_with_one_assert_is_rejected(self) -> None:
        asyncio.run(self._reject("TRUSTWORTHY", indep=2, assert_n=1, hard=0))

    def test_trustworthy_with_hard_refute_is_rejected(self) -> None:
        asyncio.run(self._reject("TRUSTWORTHY", indep=2, assert_n=2, hard=1))

    def test_valid_trustworthy_is_accepted(self) -> None:
        asyncio.run(self._accept("TRUSTWORTHY", indep=2, assert_n=2, hard=0))

    def test_refuted_without_independence_is_accepted(self) -> None:
        """The invariant gates ONLY TRUSTWORTHY; a REFUTED with indep=0/hard=1 is legal."""
        asyncio.run(self._accept("REFUTED", indep=0, assert_n=0, hard=1))

    def test_inconclusive_with_low_indep_is_accepted(self) -> None:
        asyncio.run(self._accept("INCONCLUSIVE", indep=1, assert_n=1, hard=0))

    async def _reject(self, verdict: str, *, indep: int, assert_n: int, hard: int) -> None:
        import asyncpg
        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                await conn.execute(_CLAIM_INSERT, "__inv_reject__", "count")
                with pytest.raises(asyncpg.exceptions.CheckViolationError) as exc:
                    await conn.execute(
                        _VERDICT_INSERT, "__inv_reject__", verdict, indep, assert_n, hard
                    )
                assert "trustworthy_needs_independence" in str(exc.value), (
                    f"expected the independence invariant to reject "
                    f"{verdict} indep={indep} assert={assert_n} hard={hard}"
                )
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    async def _accept(self, verdict: str, *, indep: int, assert_n: int, hard: int) -> None:
        import asyncpg
        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                await conn.execute(_CLAIM_INSERT, "__inv_accept__", "count")
                await conn.execute(
                    _VERDICT_INSERT, "__inv_accept__", verdict, indep, assert_n, hard
                )
                row = await conn.fetchrow(
                    "SELECT verdict FROM inquisition_verdict WHERE claim_id = '__inv_accept__'"
                )
                assert row is not None and row["verdict"] == verdict
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()


@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestInquisitionSchemaShape:
    """The three tables, their CHECK domains, the denominator FK, and the grants exist."""

    def test_three_tables_exist(self) -> None:
        asyncio.run(self._run_tables_exist())

    async def _run_tables_exist(self) -> None:
        import asyncpg
        conn = await asyncpg.connect(DSN)
        try:
            names = await conn.fetch(
                """SELECT tablename FROM pg_tables
                   WHERE tablename IN
                     ('inquisition_claim','inquisition_skeptic','inquisition_verdict')"""
            )
            found = {r["tablename"] for r in names}
            assert found == {
                "inquisition_claim", "inquisition_skeptic", "inquisition_verdict"
            }, f"missing inquisition tables; found {found}"
        finally:
            await conn.close()

    def test_subject_type_check_rejects_garbage(self) -> None:
        asyncio.run(self._run_subject_check())

    async def _run_subject_check(self) -> None:
        import asyncpg
        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                with pytest.raises(asyncpg.exceptions.CheckViolationError):
                    await conn.execute(_CLAIM_INSERT, "__bad_subj__", "not_a_subject_type")
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_inquisitor_role_has_select(self) -> None:
        asyncio.run(self._run_role_grant())

    async def _run_role_grant(self) -> None:
        import asyncpg
        conn = await asyncpg.connect(DSN)
        try:
            # has_table_privilege confirms the read-only inquisitor can read the ledger.
            for tbl in ("inquisition_claim", "inquisition_skeptic", "inquisition_verdict"):
                can_select = await conn.fetchval(
                    "SELECT has_table_privilege('cardeep_inquisitor', $1, 'SELECT')", tbl
                )
                assert can_select is True, f"cardeep_inquisitor must have SELECT on {tbl}"
        finally:
            await conn.close()


# ---------------------------------------------------------------------------
# P09-S4: the PRECISION gate (migration 0050). Skips unless 0050 is applied to the
# target DB (gated on live; runs in CI and the ephemeral verify where `migrate up`
# builds the full schema incl. 0050). Target DB overridable via CARDEEP_DSN.
# ---------------------------------------------------------------------------
_P09_DSN = os.environ.get("CARDEEP_DSN", DSN)

_VERDICT_PREC_INSERT = """
    INSERT INTO inquisition_verdict
        (claim_id, verdict, indep_score, assert_n, refute_soft_n, refute_hard_n, abstain_n,
         precision_n, sample_seed, ci_upper, p0_contract)
    VALUES ($1, $2, 2, 2, 0, 0, 0, $3, $4, $5, $6)
"""


def _precision_ready(dsn: str) -> bool:
    async def _chk() -> bool:
        import asyncpg
        try:
            conn = await asyncpg.connect(dsn, timeout=3)
        except Exception:
            return False
        try:
            return await conn.fetchval(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name='inquisition_verdict' AND column_name='p0_contract'"
            ) is not None
        finally:
            await conn.close()
    try:
        return asyncio.run(_chk())
    except Exception:
        return False


PRECISION_READY = _precision_ready(_P09_DSN)


@pytest.mark.skipif(
    not PRECISION_READY,
    reason="migration 0050 not applied to target DB (gated on live; runs in CI / ephemeral verify)",
)
class TestPrecisionGate:
    """trustworthy_needs_precision (0050): a TRUSTWORTHY verdict that declares a precision
    contract can only be written when its defect-rate upper bound is <= the contract p0."""

    def test_precision_columns_exist(self) -> None:
        asyncio.run(self._cols())

    async def _cols(self) -> None:
        import asyncpg
        conn = await asyncpg.connect(_P09_DSN)
        try:
            rows = await conn.fetch(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='inquisition_verdict' "
                "AND column_name IN ('precision_n','sample_seed','ci_upper','p0_contract')"
            )
            assert {r["column_name"] for r in rows} == {
                "precision_n", "sample_seed", "ci_upper", "p0_contract"}
        finally:
            await conn.close()

    def test_trustworthy_over_contract_is_rejected(self) -> None:
        asyncio.run(self._reject(ci_upper=0.05, p0=0.01))

    def test_trustworthy_within_contract_is_accepted(self) -> None:
        asyncio.run(self._accept(ci_upper=0.005, p0=0.01))

    def test_trustworthy_without_contract_is_accepted(self) -> None:
        # Legacy verdict: no precision contract (p0 NULL) -> the precision gate does not apply.
        asyncio.run(self._accept(ci_upper=None, p0=None))

    async def _reject(self, *, ci_upper: float, p0: float) -> None:
        import asyncpg
        conn = await asyncpg.connect(_P09_DSN)
        try:
            async with conn.transaction():
                await conn.execute(_CLAIM_INSERT, "__prec_reject__", "count")
                with pytest.raises(asyncpg.exceptions.CheckViolationError) as exc:
                    await conn.execute(
                        _VERDICT_PREC_INSERT, "__prec_reject__", "TRUSTWORTHY", 300, "seed-x",
                        ci_upper, p0)
                assert "trustworthy_needs_precision" in str(exc.value)
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    async def _accept(self, *, ci_upper, p0) -> None:
        import asyncpg
        conn = await asyncpg.connect(_P09_DSN)
        try:
            async with conn.transaction():
                await conn.execute(_CLAIM_INSERT, "__prec_accept__", "count")
                await conn.execute(
                    _VERDICT_PREC_INSERT, "__prec_accept__", "TRUSTWORTHY", 459, "seed-y",
                    ci_upper, p0)
                row = await conn.fetchrow(
                    "SELECT p0_contract FROM inquisition_verdict WHERE claim_id='__prec_accept__'")
                assert row is not None
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_sample_event_and_contract_accept_rows(self) -> None:
        asyncio.run(self._provenance())

    async def _provenance(self) -> None:
        import asyncpg
        conn = await asyncpg.connect(_P09_DSN)
        try:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO verification_contract (subject_pattern, gates, ttl_seconds) "
                    "VALUES ($1, $2::jsonb, $3)", "platform:*", '{"p0":0.01,"conf":0.99}', 86400)
                await conn.execute(
                    "INSERT INTO sample_event (seed, plan, sampled_keys) "
                    "VALUES ($1, $2::jsonb, $3::jsonb)",
                    "seed-z", '{"n":459,"c":0}', '["k1","k2","k3"]')
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()
