"""Live-DB regression tests for the corrected inquisition claim emitter (audit P2 D-inquisition).

Guards the central re-key fix: VAM entity_inventory/generic_dealer_site_inventory verdicts must emit
inquisition claims keyed 'inventory:<entity_ulid>' (so Lens A measures the REAL available count), NOT
the old 'count'+cdp_code (which made Lens A count provinces → 0 → falsely REFUTE). All rolled back.
"""
from __future__ import annotations

import asyncio

import asyncpg
import pytest

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"


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


async def _run(coro_fn):
    c = await asyncpg.connect(DSN)
    tr = c.transaction()
    await tr.start()
    try:
        return await coro_fn(c)
    finally:
        await tr.rollback()
        await c.close()


@SKIP
def test_entity_inventory_rekeyed_to_inventory_ulid():
    from pipeline.inquisition.prosecutor import emit_claim_from_verdict

    async def body(c):
        vv = await c.fetchrow(
            "SELECT * FROM verification_verdict WHERE subject_type='entity_inventory' "
            "AND superseded_by IS NULL LIMIT 1")
        if vv is None:
            pytest.skip("no entity_inventory verdict")
        cid = await emit_claim_from_verdict(c, vv)
        claim = await c.fetchrow(
            "SELECT subject_type, subject_key FROM inquisition_claim WHERE claim_id=$1", cid)
        # Re-keyed: 'inventory:<entity_ulid>', NOT the VAM cdp_code (the meaning-corruption fix).
        assert claim["subject_type"] == "inventory"
        assert claim["subject_key"].startswith("inventory:")
        assert claim["subject_key"] != vv["subject_key"]
    asyncio.run(_run(body))


@SKIP
def test_emitter_is_idempotent():
    from pipeline.inquisition.prosecutor import emit_claim_from_verdict

    async def body(c):
        vv = await c.fetchrow(
            "SELECT * FROM verification_verdict WHERE subject_type='entity_inventory' "
            "AND superseded_by IS NULL LIMIT 1")
        if vv is None:
            pytest.skip("no entity_inventory verdict")
        first = await emit_claim_from_verdict(c, vv)
        second = await emit_claim_from_verdict(c, vv)
        assert first is not None and second is None  # one open claim per subject
    asyncio.run(_run(body))


@SKIP
def test_unsupported_subject_type_skipped():
    from pipeline.inquisition.prosecutor import emit_claim_from_verdict

    async def body(c):
        vv = await c.fetchrow(
            "SELECT * FROM verification_verdict WHERE subject_type='platform_slice' "
            "AND superseded_by IS NULL LIMIT 1")
        if vv is None:
            pytest.skip("no platform_slice verdict")
        # No €0 lens measures a platform_slice; must SKIP (None), never coerce to a 'count' claim.
        assert await emit_claim_from_verdict(c, vv) is None
    asyncio.run(_run(body))
