"""Tests for the extracted canonical_key forward-coverage (audit P2 B-canonical-key).

Two layers:
  - PURE unit (no DB): candidate_kwargs still yields kwargs that cdp_pair turns into a KNOWN live
    cdp_code — guards the extraction from scripts/ into pipeline/ against logic drift.
  - LIVE rolled-back: NULL a real entity's canonical_key, run backfill, assert it re-derives the
    SAME key (the re-hash gate works end-to-end on real data). Rolled back — no permanent change.
"""
from __future__ import annotations

import asyncio

import asyncpg
import pytest

from pipeline.identity.canonical_key_backfill import backfill_canonical_keys, candidate_kwargs
from services.api.codes import cdp_pair

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"


# --------------------------------------------------------------------------- pure unit (no DB)

class TestCandidateKwargs:
    def test_particular_cochesnet_reproduces_golden_code(self):
        # A coches.net particular row -> the kwargs whose cdp_pair is the known live CDP-ES-50-FPB3W1R6.
        row = {"kind": "particular", "province_code": "50", "source_key": "coches_net_wholesale",
               "source_ref": None, "trade_name": None, "legal_name": None, "municipality_code": None,
               "website": None, "cif": None, "address": None}
        kws = list(candidate_kwargs(row))
        assert kws, "expected at least one candidate for a coches.net particular"
        assert any(cdp_pair(**kw)[1] == "CDP-ES-50-FPB3W1R6" for kw in kws)

    def test_milanuncios_particular_uses_source_ref_as_seller(self):
        # milanuncios seller id comes from source_ref -> known live CDP-ES-04-CR8NMA86.
        row = {"kind": "particular", "province_code": "04", "source_key": "milanuncios_wholesale",
               "source_ref": "109905688", "trade_name": None, "legal_name": None,
               "municipality_code": None, "website": None, "cif": None, "address": None}
        assert any(cdp_pair(**kw)[1] == "CDP-ES-04-CR8NMA86" for kw in candidate_kwargs(row))

    def test_dealer_with_domain_yields_domain_candidate(self):
        row = {"kind": "compraventa", "province_code": "28", "source_key": "as24", "source_ref": None,
               "trade_name": "Talleres X", "legal_name": None, "municipality_code": "28079",
               "website": "ford.es", "cif": None, "address": None}
        kws = list(candidate_kwargs(row))
        assert {"province_code": "28", "domain": "ford.es"} in kws

    def test_particular_without_resolvable_seller_yields_nothing(self):
        # No source mapping + no seller id -> no candidate (conservative, never guesses).
        row = {"kind": "particular", "province_code": "28", "source_key": "unknown_src",
               "source_ref": None, "trade_name": None, "legal_name": None, "municipality_code": None,
               "website": None, "cif": None, "address": None}
        assert list(candidate_kwargs(row)) == []


# --------------------------------------------------------------------------- live, rolled back

def _db_ok() -> bool:
    async def _p() -> bool:
        try:
            c = await asyncpg.connect(DSN, timeout=3)
            await c.close()
            return True
        except Exception:
            return False
    try:
        return asyncio.run(_p())
    except Exception:
        return False


SKIP = pytest.mark.skipif(not _db_ok(), reason="cardeep-pg not reachable")


@SKIP
def test_backfill_rederives_a_real_key_rolled_back():
    async def body():
        c = await asyncpg.connect(DSN)
        tr = c.transaction()
        await tr.start()
        try:
            row = await c.fetchrow(
                "SELECT entity_ulid, canonical_key FROM entity "
                "WHERE canonical_key IS NOT NULL AND kind='particular' LIMIT 1")
            if row is None:
                pytest.skip("no filled particular canonical_key to probe")
            orig = row["canonical_key"]
            await c.execute("UPDATE entity SET canonical_key=NULL WHERE entity_ulid=$1",
                            row["entity_ulid"])
            summary = await backfill_canonical_keys(c, apply=True)
            refilled = await c.fetchval(
                "SELECT canonical_key FROM entity WHERE entity_ulid=$1", row["entity_ulid"])
            # The gate re-derived the EXACT original pre-image (a wrong key could never be written).
            assert refilled == orig
            assert summary["matched"] >= 1
        finally:
            await tr.rollback()
            await c.close()
    asyncio.run(body())
