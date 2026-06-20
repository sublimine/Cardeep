"""P05: the unified _core.ensure_platform_entity writes the SAME rows the hand-copies did.

Real-DB, rolled back (no pollution); runs on the live DB or an ephemeral one. Spec-driven and
parametrized over every migrated connector spec, so each adopter is proven behaviour-preserving
against the FULL variation range (coches_net: is_tier1+waf+conflict-refresh; AS24: minimal,
is_tier1=False, no waf, empty conflict-refresh). A characterization test of the strangler refactor.
"""
from __future__ import annotations

import asyncio
import json
import os
from dataclasses import replace

import pytest

from pipeline.platform._core.persistence import ensure_platform_entity
from pipeline.platform.autocasion_wholesale import AC_SPEC
from pipeline.platform.autoscout24_wholesale import AS24_SPEC
from pipeline.platform.coches_com_wholesale import COCHES_COM_SPEC
from pipeline.platform.coches_net_wholesale import COCHES_SPEC
from pipeline.platform.localizavo_wholesale import LV_SPEC
from pipeline.platform.miclasico_wholesale import MC_SPEC
from pipeline.platform.motorflash_wholesale import MF_SPEC
from pipeline.platform.oem_audi_wholesale import AUDI_SPEC
from pipeline.platform.oem_ford_wholesale import FORD_SPEC
from pipeline.platform.oem_hyundai_wholesale import HY_SPEC
from pipeline.platform.oem_kia_wholesale import KIA_SPEC
from pipeline.platform.oem_mercedes_benz_wholesale import MB_SPEC
from pipeline.platform.oem_nissan_mazda_honda_wholesale import NISSAN_SPEC
from pipeline.platform.oem_toyota_lexus_wholesale import TL_SPEC
from pipeline.platform.oem_volvo_jlr_suzuki_wholesale import VJS_SPEC
from pipeline.platform.spoticar_wholesale import SPOTICAR_SPEC

DSN = os.environ.get("CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep")

# Every connector migrated to the _core. Add each new adopter's spec here as it lands. Covers the
# variation range: coches_net/coches_com (mid+extras), AS24 (minimal), autocasion (maximal), miclasico
# (source_group/role), localizavo + the OEM VO portals (spoticar/audi/ford/hyundai/kia/toyota_lexus =
# distinct legal_name + kind), motorflash (is_platform_like=True aggregator, empty conflict_refresh).
SPECS = [COCHES_SPEC, AS24_SPEC, AC_SPEC, MC_SPEC, LV_SPEC, COCHES_COM_SPEC, MF_SPEC,
         SPOTICAR_SPEC, AUDI_SPEC, FORD_SPEC, HY_SPEC, KIA_SPEC, TL_SPEC,
         MB_SPEC, NISSAN_SPEC, VJS_SPEC]
_IDS = [s.source_key for s in SPECS]


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
@pytest.mark.parametrize("spec", SPECS, ids=_IDS)
class TestPlatformPersistenceCore:
    def test_writes_rows_matching_spec(self, spec) -> None:
        asyncio.run(self._run(spec))

    async def _run(self, spec) -> None:
        import asyncpg
        # Force the INSERT path with a fresh test cdp_code so the row reflects the SPEC exactly
        # (the live platform entity already exists -> the conflict path would show its existing,
        # non-refreshed values). Rolled back, so the test row never persists.
        spec = replace(spec, cdp_code=f"CDP-ES-00-P05-{spec.source_key}")
        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                eulid = await ensure_platform_entity(conn, spec)
                e = await conn.fetchrow(
                    "SELECT kind, legal_name, trade_name, website, website_waf, is_tier1, "
                    "first_discovered_source, status, defense_tier, source_group, role "
                    "FROM entity WHERE cdp_code=$1", spec.cdp_code)
                assert e is not None
                assert e["kind"] == spec.kind
                assert e["trade_name"] == spec.trade_name
                assert e["legal_name"] == (spec.legal_name if spec.legal_name is not None
                                           else spec.trade_name)
                assert e["website"] == spec.website
                assert e["website_waf"] == spec.website_waf
                assert e["is_tier1"] == spec.is_tier1
                assert e["first_discovered_source"] == spec.source_key
                assert e["status"] == "active"
                assert e["defense_tier"] == spec.defense_tier
                assert e["source_group"] == spec.source_group
                assert e["role"] == spec.role

                es = await conn.fetchrow(
                    "SELECT source_ref FROM entity_source WHERE entity_ulid=$1 AND source_key=$2",
                    eulid, spec.source_key)
                assert es is not None and es["source_ref"] == spec.source_ref

                pm = await conn.fetchrow(
                    "SELECT data_surface, surface_detail, requires_creds, is_platform_like, family "
                    "FROM platform_meta WHERE entity_ulid=$1", eulid)
                assert pm is not None
                assert pm["data_surface"] == spec.data_surface
                assert pm["requires_creds"] == spec.requires_creds
                assert pm["is_platform_like"] == spec.is_platform_like
                assert pm["family"] == spec.family
                sd = pm["surface_detail"]
                sd = json.loads(sd) if isinstance(sd, str) else sd
                assert sd == spec.surface_detail
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_idempotent_upsert(self, spec) -> None:
        asyncio.run(self._run_idem(spec))

    async def _run_idem(self, spec) -> None:
        import asyncpg
        spec = replace(spec, cdp_code=f"CDP-ES-00-P05I-{spec.source_key}")
        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                u1 = await ensure_platform_entity(conn, spec)
                u2 = await ensure_platform_entity(conn, spec)
                assert u1 == u2  # same entity_ulid -> idempotent
                n = await conn.fetchval(
                    "SELECT count(*) FROM entity WHERE cdp_code=$1", spec.cdp_code)
                assert n == 1
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()
