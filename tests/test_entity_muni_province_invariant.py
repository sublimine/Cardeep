"""DB-invariant tests for chk_entity_muni_province (migration 0041, audit SU-A6 coherence).

Spanish INE municipality codes are 5 digits whose first 2 ARE the province code. The CHECK
constraint enforces municipality_code[:2] == province_code whenever both are set, so a
muni-province mismatch can never reach the served surface via a code regression. NULL muni or
NULL province are allowed (the un-served geo-gap dealers).

All writes run in a rolled-back transaction — nothing persists.
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


class _Rollback(Exception):
    """Forces rollback — nothing persists."""


@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestMuniProvinceInvariant:
    def _one_muni_entity(self):
        async def _go():
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                return await conn.fetchval(
                    "SELECT entity_ulid FROM entity WHERE municipality_code IS NOT NULL LIMIT 1")
            finally:
                await conn.close()
        return asyncio.run(_go())

    def test_mismatch_is_rejected(self) -> None:
        """A muni/province pair that is each individually VALID (passes the FKs) but mutually
        INCONSISTENT (Madrid muni 28079 + Barcelona province 08) must raise on the CHECK — proving
        the CHECK fires independently of the province/municipality foreign keys."""
        import asyncpg
        eid = self._one_muni_entity()
        assert eid is not None, "need at least one entity with a municipality_code"

        async def _go() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                with pytest.raises(asyncpg.exceptions.CheckViolationError):
                    async with conn.transaction():
                        await conn.execute(
                            "UPDATE entity SET municipality_code='28079', province_code='08' "
                            "WHERE entity_ulid=$1", eid)
            finally:
                await conn.close()
        asyncio.run(_go())

    def test_consistent_is_allowed(self) -> None:
        """A consistent muni/province pair (28079 -> 28) is accepted (rolled back)."""
        import asyncpg
        eid = self._one_muni_entity()

        async def _go() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                try:
                    async with conn.transaction():
                        await conn.execute(
                            "UPDATE entity SET province_code='28', municipality_code='28079' "
                            "WHERE entity_ulid=$1", eid)
                        raise _Rollback
                except _Rollback:
                    pass
            finally:
                await conn.close()
        asyncio.run(_go())  # no exception == accepted

    def test_null_muni_allows_any_province(self) -> None:
        """NULL municipality_code (un-served gap dealer) is EXEMPT from the muni-province CHECK:
        setting muni=NULL with a province (08) that would be inconsistent with the prior muni is
        accepted. (province must still be a valid geo_province — the FK is independent.)"""
        import asyncpg
        eid = self._one_muni_entity()

        async def _go() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                try:
                    async with conn.transaction():
                        await conn.execute(
                            "UPDATE entity SET municipality_code=NULL, province_code='08' "
                            "WHERE entity_ulid=$1", eid)
                        raise _Rollback
                except _Rollback:
                    pass
            finally:
                await conn.close()
        asyncio.run(_go())  # no exception == NULL muni is exempt from the muni-province CHECK

    def test_no_existing_violations(self) -> None:
        """The whole served table already satisfies the invariant (constraint VALIDATED)."""
        import asyncpg

        async def _go() -> int:
            conn = await asyncpg.connect(DSN)
            try:
                return await conn.fetchval(
                    "SELECT count(*) FROM entity WHERE municipality_code IS NOT NULL "
                    "AND province_code IS NOT NULL AND left(municipality_code,2) <> province_code")
            finally:
                await conn.close()
        assert asyncio.run(_go()) == 0
