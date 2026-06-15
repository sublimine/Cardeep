"""Regression tests for the VAM quorum format fix (audit finding B-1).

The deep-ledger CHECK chk_trustworthy_needs_quorum (migration 0026) computes
quorum_n/family_n/origin_n via GENERATED columns over independent_values (a numeric
JSONB array) and verifier_paths (a JSONB array of {family,origin} objects). Before
this fix, record_count_verdict wrote verifier_paths as a string array and
independent_values as a dict → the generated columns returned 0 → 989/991 TRUSTWORTHY
verdicts had quorum_n=0, AND any NEW TRUSTWORTHY verdict raised CheckViolationError
(verify.py was in write-deadlock). The fix aligns the Python verdict logic with the
DB invariant: TRUSTWORTHY requires a modal cluster >=2 AND >=2 distinct collector
families AND >=2 distinct origins; the written shape lets the generated columns
recompute the same quorum.

All DB writes run in a rolled-back transaction (no persistence; the audit hash-chain
row the trigger appends is discarded with the rollback).
"""
from __future__ import annotations

import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.verify import _path_family  # noqa: E402

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
    """Forces rollback — nothing persists, the audit-chain row is discarded."""


# ---------------------------------------------------------------------------
# Unit: the family mapping (pure)
# ---------------------------------------------------------------------------

class TestPathFamily:
    def test_db_family(self) -> None:
        assert _path_family("db_ingested") == "db"
        assert _path_family("cars_ingested_distinct") == "db"

    def test_http_family(self) -> None:
        assert _path_family("fetched") == "http"
        assert _path_family("harvested_pairs") == "http"

    def test_source_family(self) -> None:
        assert _path_family("source_declared") == "source"
        assert _path_family("declared_total") == "source"

    def test_unknown_collapses_to_other(self) -> None:
        # Unknown names share ONE family so unproven orthogonality never grants quorum.
        assert _path_family("zzz") == "other"
        assert _path_family("foo") == _path_family("bar") == "other"


# ---------------------------------------------------------------------------
# DB integration: the verdict + the recomputed generated columns
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestQuorumWiring:
    """Every case rolled back. Asserts the verdict AND the generated columns the DB
    recomputes — proving Python and the chk_trustworthy_needs_quorum CHECK agree."""

    def _run(self, paths, expect_verdict, *, min_quorum=None, min_family=None):
        asyncio.run(self._case(paths, expect_verdict, min_quorum, min_family))

    async def _case(self, paths, expect_verdict, min_quorum, min_family) -> None:
        import asyncpg
        from pipeline.verify import record_count_verdict
        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                v = await record_count_verdict(
                    conn, subject_type="__test_quorum__", subject_key="x",
                    claim="quorum regression", paths=paths,
                )
                assert v == expect_verdict, f"{paths} → expected {expect_verdict}, got {v}"
                row = await conn.fetchrow(
                    "SELECT quorum_n, family_n, origin_n, verdict FROM verification_verdict "
                    "WHERE subject_type='__test_quorum__' ORDER BY id DESC LIMIT 1"
                )
                assert row["verdict"] == expect_verdict
                if min_quorum is not None:
                    assert row["quorum_n"] >= min_quorum
                if min_family is not None:
                    assert row["family_n"] >= min_family
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_two_orthogonal_families_agree_is_trustworthy_no_deadlock(self) -> None:
        # The exact case that used to raise CheckViolationError (write-deadlock).
        self._run({"db_ingested": 140, "fetched": 140}, "TRUSTWORTHY",
                  min_quorum=2, min_family=2)

    def test_three_families_agree_is_trustworthy(self) -> None:
        self._run({"db_ingested": 140, "fetched": 140, "source_declared": 140},
                  "TRUSTWORTHY", min_quorum=3, min_family=3)

    def test_same_family_pair_is_not_trustworthy(self) -> None:
        # Two 'db' paths agree on the value but are not >=2 orthogonal families →
        # UNVERIFIED (cannot certify), NOT a CheckViolation deadlock.
        self._run({"db_ingested": 140, "db_count": 140}, "UNVERIFIED")

    def test_single_path_unverified(self) -> None:
        self._run({"db_ingested": 140}, "UNVERIFIED")

    def test_divergent_refuted(self) -> None:
        self._run({"db_ingested": 140, "fetched": 900, "source_declared": 50}, "REFUTED")
