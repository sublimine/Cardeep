"""P05: the unified _core.ensure_platform_entity writes the SAME rows the 29 hand-copies did.

Real-DB, rolled back (no pollution); runs on the live DB or an ephemeral one. Verifies the first
strangler adopter (coches_net via COCHES_SPEC) produces the correct entity / entity_source /
platform_meta rows and is idempotent. A behaviour-preserving characterization test of the refactor.
"""
from __future__ import annotations

import asyncio
import json
import os

import pytest

DSN = os.environ.get("CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep")


def _db_available() -> bool:
    async def _ping() -> bool:
        import asyncpg
        try:
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
    """Forces rollback so the test never persists state."""


@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestPlatformPersistenceCore:
    def test_coches_spec_writes_expected_rows(self) -> None:
        asyncio.run(self._run())

    async def _run(self) -> None:
        import asyncpg

        from pipeline.platform._core.persistence import ensure_platform_entity
        from pipeline.platform.coches_net_wholesale import COCHES_SPEC

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                eulid = await ensure_platform_entity(conn, COCHES_SPEC)
                e = await conn.fetchrow(
                    "SELECT kind, legal_name, trade_name, website, website_waf, is_tier1, "
                    "first_discovered_source, status FROM entity WHERE cdp_code=$1",
                    COCHES_SPEC.cdp_code)
                assert e is not None
                assert e["kind"] == "plataforma"
                assert e["trade_name"] == COCHES_SPEC.trade_name
                assert e["legal_name"] == COCHES_SPEC.trade_name
                assert e["website"] == COCHES_SPEC.website
                assert e["website_waf"] == COCHES_SPEC.website_waf
                assert e["is_tier1"] == COCHES_SPEC.is_tier1
                assert e["first_discovered_source"] == COCHES_SPEC.source_key
                assert e["status"] == "active"

                es = await conn.fetchrow(
                    "SELECT source_ref FROM entity_source WHERE entity_ulid=$1 AND source_key=$2",
                    eulid, COCHES_SPEC.source_key)
                assert es is not None and es["source_ref"] == COCHES_SPEC.source_ref

                pm = await conn.fetchrow(
                    "SELECT data_surface, surface_detail, requires_creds, is_platform_like "
                    "FROM platform_meta WHERE entity_ulid=$1", eulid)
                assert pm is not None
                assert pm["data_surface"] == COCHES_SPEC.data_surface
                assert pm["requires_creds"] == COCHES_SPEC.requires_creds
                assert pm["is_platform_like"] == COCHES_SPEC.is_platform_like
                sd = pm["surface_detail"]
                sd = json.loads(sd) if isinstance(sd, str) else sd
                assert sd["method"] == "POST" and sd["surface_intent"] == "json_api"
                assert sd["endpoint"] == COCHES_SPEC.surface_detail["endpoint"]
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_idempotent_upsert(self) -> None:
        asyncio.run(self._run_idem())

    async def _run_idem(self) -> None:
        import asyncpg

        from pipeline.platform._core.persistence import ensure_platform_entity
        from pipeline.platform.coches_net_wholesale import COCHES_SPEC

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                u1 = await ensure_platform_entity(conn, COCHES_SPEC)
                u2 = await ensure_platform_entity(conn, COCHES_SPEC)
                assert u1 == u2  # same entity_ulid -> idempotent
                n = await conn.fetchval(
                    "SELECT count(*) FROM entity WHERE cdp_code=$1", COCHES_SPEC.cdp_code)
                assert n == 1
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()
