"""Integrity guards for the canonical dealer dedup (v_dealer_resolved).

This view is the FOUNDATION under the dealer count, the served canonical inventory, AND the
SU-SEAL numerator (v_province_seal uses COUNT(DISTINCT COALESCE(resolved_ulid, entity_ulid))).
A dedup integrity break — an entity in two clusters, a dangling resolved_ulid, or an
alias→alias chain — would silently corrupt all three. These tests pin the three structural
invariants against the live DB so any future regression in the dedup is caught.

Read-only.
"""
from __future__ import annotations

import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"


def _db_available() -> bool:
    async def _ping() -> bool:
        try:
            import asyncpg
            conn = await asyncpg.connect(DSN, timeout=3)
            await conn.close()
            return True
        except Exception:
            return False
    try:
        return asyncio.run(_ping())
    except Exception:
        return False


DB_AVAILABLE = _db_available()


def _scalar(sql: str) -> int:
    async def _go() -> int:
        import asyncpg
        conn = await asyncpg.connect(DSN)
        try:
            return await conn.fetchval(sql)
        finally:
            await conn.close()
    return asyncio.run(_go())


@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestDedupIntegrity:
    def test_no_entity_in_two_clusters(self) -> None:
        """Each entity_ulid resolves at most once — no entity belongs to two clusters."""
        dup = _scalar(
            "SELECT count(*) FROM (SELECT entity_ulid FROM v_dealer_resolved "
            "GROUP BY entity_ulid HAVING count(*) > 1) t")
        assert dup == 0, f"{dup} entities appear in >1 dedup cluster"

    def test_no_dangling_resolved_ulid(self) -> None:
        """Every resolved_ulid points to a real entity (no dangling canonical)."""
        dangling = _scalar(
            "SELECT count(*) FROM v_dealer_resolved vdr WHERE vdr.resolved_ulid IS NOT NULL "
            "AND NOT EXISTS (SELECT 1 FROM entity e WHERE e.entity_ulid = vdr.resolved_ulid)")
        assert dangling == 0, f"{dangling} resolved_ulid values point to no entity"

    def test_no_alias_of_alias_chain(self) -> None:
        """The dedup is FLAT: an alias resolves to a CANONICAL, never to another alias.
        A two-hop chain (A→B→C) would make COALESCE(resolved_ulid, entity_ulid) collapse
        inconsistently and break the seal numerator's distinct count."""
        chains = _scalar(
            "SELECT count(*) FROM v_dealer_resolved a "
            "JOIN v_dealer_resolved b ON b.entity_ulid = a.resolved_ulid "
            "WHERE a.resolved_ulid IS NOT NULL AND b.resolved_ulid IS NOT NULL "
            "AND b.resolved_ulid <> b.entity_ulid")
        assert chains == 0, f"{chains} alias→alias chains (dedup must be flat)"

    def test_canonical_universe_is_plausible(self) -> None:
        """Sanity floor: the distinct canonical dealer count stays in the sealed band
        (B1∘dedup ≈ 40k canonical dealers). Guards against a dedup that collapses everything
        to a handful or explodes back to the raw entity count."""
        canon = _scalar(
            "SELECT count(DISTINCT COALESCE(vdr.resolved_ulid, e.entity_ulid)) "
            "FROM entity e LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid = e.entity_ulid "
            "WHERE e.kind <> 'particular'")
        assert 30_000 <= canon <= 60_000, f"canonical dealer universe {canon} outside sane band"
