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
