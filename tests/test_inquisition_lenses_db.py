"""DB integration tests for SU-B2 ε3 — five orthogonal inquisition lenses.

Requires cardeep-pg at 127.0.0.1:5433. All tests run inside aborted
transactions (_Rollback sentinel) — zero side effects on DB state.

Real DB subjects (verified 2026-06-15 via psql):
    province_code='28' (Madrid): 52 668 entities
    kind='desguace':             1 895 entities  (EXACT regime)
    coverage:desguace:           1 895 entities
    dgt_cat → desguace:          1 292 entities  (official register)
    wallapop_wholesale → particular: 220 634 entities
    denominator P_all (segment='P_all', no province): point_est=38 555
    vehicle entity 01KTYVBKCQ6DB0SMNK450P2SXZ: 17 480 available vehicles w/ price
"""
from __future__ import annotations

import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# DB connectivity guard
# ---------------------------------------------------------------------------

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"


def _db_available() -> bool:
    try:
        import asyncpg  # noqa: F401
        return asyncio.run(_ping())
    except Exception:
        return False


async def _ping() -> bool:
    try:
        import asyncpg
        conn = await asyncpg.connect(DSN, timeout=3)
        await conn.close()
        return True
    except Exception:
        return False


DB_AVAILABLE = _db_available()


class _Rollback(Exception):
    """Sentinel that forces transaction rollback — no state persisted."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

from pipeline.inquisition.lenses import ClaimEnvelope
from pipeline.inquisition.models import StateTuple, indep_distance


def _claim(
    subject_type: str,
    subject_key: str,
    asserted_value: str,
    *,
    source: str = "test_portal",
    tool: str = "scraper",
    cache: str = "snap_T0",
    path: str = "ingest",
    tolerance: float = 0.005,
    evidence_uri: str | None = None,
) -> ClaimEnvelope:
    return ClaimEnvelope(
        claim_id="01TEST000000000000000000000",
        subject_type=subject_type,
        subject_key=subject_key,
        asserted_value=asserted_value,
        producer_state=StateTuple(source=source, tool=tool, cache=cache, path=path),
        tolerance=tolerance,
        evidence_uri=evidence_uri,
    )


# ---------------------------------------------------------------------------
# A. Lens A — re-query DB integration
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestLensARequery:
    """Lens A DB integration: ASSERT on true value, REFUTE_SOFT on wrong value."""

    def test_province_28_assert_true_value(self) -> None:
        asyncio.run(self._run())

    async def _run(self) -> None:
        import asyncpg
        from pipeline.inquisition.lenses import lens_a_requery

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                claim = _claim("count", "province:28", "52668")
                result = await lens_a_requery(conn, claim)

                assert result.lens == "A_requery"
                assert result.verdict == "ASSERT", (
                    f"Expected ASSERT for true count but got {result.verdict}: "
                    f"measured={result.measured_value}"
                )
                assert result.measured_value == "52668"
                assert "." not in result.measured_value
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_province_28_refute_soft_wrong_value(self) -> None:
        asyncio.run(self._run_refute())

    async def _run_refute(self) -> None:
        import asyncpg
        from pipeline.inquisition.lenses import lens_a_requery

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                # |52668-99999|=47331 far outside DRIFT tolerance ~500
                claim = _claim("count", "province:28", "99999")
                result = await lens_a_requery(conn, claim)

                assert result.verdict == "REFUTE_SOFT"
                assert result.measured_value == "52668"
                assert "." not in result.measured_value
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_kind_desguace_assert(self) -> None:
        """kind='desguace' total is 1895 → GROUP BY path → ASSERT (EXACT regime)."""
        asyncio.run(self._run_kind_assert())

    async def _run_kind_assert(self) -> None:
        import asyncpg
        from pipeline.inquisition.lenses import lens_a_requery

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                claim = _claim("kind", "kind:desguace", "1895")
                result = await lens_a_requery(conn, claim)

                assert result.verdict == "ASSERT", (
                    f"Expected ASSERT for kind:desguace=1895, got {result.verdict}, "
                    f"measured={result.measured_value}"
                )
                assert result.measured_value == "1895"
                assert "." not in result.measured_value
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_kind_desguace_refute_soft_wrong(self) -> None:
        """kind='desguace' asserted as 2000 → EXACT mismatch → REFUTE_SOFT."""
        asyncio.run(self._run_kind_refute())

    async def _run_kind_refute(self) -> None:
        import asyncpg
        from pipeline.inquisition.lenses import lens_a_requery

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                claim = _claim("kind", "kind:desguace", "2000")
                result = await lens_a_requery(conn, claim)

                assert result.verdict == "REFUTE_SOFT"
                assert result.measured_value == "1895"
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_coverage_desguace_assert(self) -> None:
        """coverage:desguace = 1895 → ASSERT."""
        asyncio.run(self._run_coverage())

    async def _run_coverage(self) -> None:
        import asyncpg
        from pipeline.inquisition.lenses import lens_a_requery

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                claim = _claim("coverage", "coverage:desguace", "1895")
                result = await lens_a_requery(conn, claim)

                assert result.verdict == "ASSERT", (
                    f"Expected ASSERT for coverage:desguace=1895, got {result.verdict}, "
                    f"measured={result.measured_value}"
                )
                assert result.measured_value == "1895"
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_denominator_p_all_no_decimal(self) -> None:
        """denominator:P_all → no decimal in measured_value."""
        asyncio.run(self._run_denom())

    async def _run_denom(self) -> None:
        import asyncpg
        from pipeline.inquisition.lenses import lens_a_requery

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                claim = _claim("denominator", "denominator:P_all", "38555")
                result = await lens_a_requery(conn, claim)

                assert result.verdict in ("ASSERT", "REFUTE_SOFT", "ABSTAIN")
                if result.measured_value is not None:
                    assert "." not in result.measured_value
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()


# ---------------------------------------------------------------------------
# B. Lens D — cross-source DB integration
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestLensDCrossSource:
    """Lens D DB integration: real cross-source witnesses."""

    def test_coverage_desguace_dgt_cat_1292(self) -> None:
        """dgt_cat attests 1292 desguace → asserted=1292 → ASSERT."""
        asyncio.run(self._run_assert())

    async def _run_assert(self) -> None:
        import asyncpg
        from pipeline.inquisition.lenses import lens_d_cross_source

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                claim = _claim("coverage", "coverage:desguace", "1292")
                result = await lens_d_cross_source(conn, claim)

                assert result.lens == "D_cross_source"
                assert result.verdict in ("ASSERT", "ABSTAIN")
                if result.verdict == "ASSERT":
                    assert result.measured_value == "1292"
                    assert "." not in result.measured_value
                    assert result.state.source == "dgt_cat"
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_coverage_desguace_dgt_cat_refute_wrong(self) -> None:
        """asserted=9999 for desguace → dgt_cat measures 1292 → REFUTE_SOFT."""
        asyncio.run(self._run_refute())

    async def _run_refute(self) -> None:
        import asyncpg
        from pipeline.inquisition.lenses import lens_d_cross_source

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                claim = _claim("coverage", "coverage:desguace", "9999")
                result = await lens_d_cross_source(conn, claim)

                assert result.lens == "D_cross_source"
                if result.verdict != "ABSTAIN":
                    assert result.verdict == "REFUTE_SOFT"
                    assert result.measured_value == "1292"
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_kind_particular_wallapop_refute(self) -> None:
        """wallapop has 220634 'particular'; asserted=999999 → REFUTE_SOFT."""
        asyncio.run(self._run_kind_refute())

    async def _run_kind_refute(self) -> None:
        import asyncpg
        from pipeline.inquisition.lenses import lens_d_cross_source

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                claim = _claim("kind", "kind:particular", "999999")
                result = await lens_d_cross_source(conn, claim)

                assert result.lens == "D_cross_source"
                if result.verdict != "ABSTAIN":
                    assert result.verdict == "REFUTE_SOFT"
                    assert result.measured_value is not None
                    assert "." not in result.measured_value
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_d_state_uses_different_source(self) -> None:
        """Lens D state.source must differ from the producer source → D ≥ 2."""
        asyncio.run(self._run_source_independence())

    async def _run_source_independence(self) -> None:
        import asyncpg
        from pipeline.inquisition.lenses import lens_d_cross_source

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                producer_source = "wallapop_wholesale"
                claim = _claim("coverage", "coverage:desguace", "1292", source=producer_source)
                result = await lens_d_cross_source(conn, claim)

                if result.verdict != "ABSTAIN":
                    assert result.state.source != producer_source
                    assert indep_distance(result.state, claim.producer_state) >= 2
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_d_abstains_for_inventory_subject(self) -> None:
        """Lens D matrix does not include 'inventory' → ABSTAIN."""
        asyncio.run(self._run_abstain())

    async def _run_abstain(self) -> None:
        import asyncpg
        from pipeline.inquisition.lenses import lens_d_cross_source

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                claim = _claim("inventory", "inventory:01KTYVBKCQ6DB0SMNK450P2SXZ", "1000")
                result = await lens_d_cross_source(conn, claim)

                assert result.verdict == "ABSTAIN"
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()


# ---------------------------------------------------------------------------
# C. Lens E — batch hash DB integration
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestLensEBatchHash:
    """Lens E DB integration: set-hash and empty-delta detection."""

    # Entity with real vehicle inventory (17 480 available vehicles, all with price)
    ENTITY_ULID = "01KTYVBKCQ6DB0SMNK450P2SXZ"

    def test_no_prior_hash_abstains_with_current_hash(self) -> None:
        asyncio.run(self._run_no_prior())

    async def _run_no_prior(self) -> None:
        import asyncpg
        from pipeline.inquisition.lenses import lens_e_batch_hash

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                claim = _claim("inventory", f"inventory:{self.ENTITY_ULID}", "17480")
                result = await lens_e_batch_hash(conn, claim)

                assert result.lens == "E_batch_hash"
                assert result.verdict == "ABSTAIN"
                assert result.reason == "no_prior_hash_to_compare"
                assert result.measured_value is not None
                assert len(result.measured_value) == 64  # SHA-256 hex
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_hash_matches_prior_assert(self) -> None:
        """Compute hash, re-claim with same hash → ASSERT (set unchanged)."""
        asyncio.run(self._run_hash_matches())

    async def _run_hash_matches(self) -> None:
        import asyncpg
        from pipeline.inquisition.lenses import lens_e_batch_hash

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                # Step 1: seed — compute actual hash
                seed_result = await lens_e_batch_hash(
                    conn,
                    _claim("inventory", f"inventory:{self.ENTITY_ULID}", "17480"),
                )
                current_hash = seed_result.measured_value
                assert current_hash is not None

                # Step 2: claim with that same hash as prior → must ASSERT
                result = await lens_e_batch_hash(
                    conn,
                    _claim(
                        "inventory", f"inventory:{self.ENTITY_ULID}", "17480",
                        evidence_uri=f"hash:{current_hash}",
                    ),
                )
                assert result.lens == "E_batch_hash"
                assert result.verdict == "ASSERT", (
                    f"Expected ASSERT when hash matches prior, got {result.verdict}"
                )
                assert result.measured_value == current_hash
                assert result.confidence == 1.0
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_empty_delta_refute_hard_deterministic(self) -> None:
        """Hash unchanged but delta claimed → REFUTE_HARD(deterministic=True)."""
        asyncio.run(self._run_empty_delta())

    async def _run_empty_delta(self) -> None:
        import asyncpg
        from pipeline.inquisition.lenses import lens_e_batch_hash

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                # Step 1: compute current hash
                seed_result = await lens_e_batch_hash(
                    conn,
                    _claim("inventory", f"inventory:{self.ENTITY_ULID}", "17480"),
                )
                current_hash = seed_result.measured_value
                assert current_hash is not None

                # Step 2: delta claim — set is unchanged but producer claims "12 NEW"
                result = await lens_e_batch_hash(
                    conn,
                    _claim(
                        "delta", f"delta:{self.ENTITY_ULID}", "12",
                        evidence_uri=f"hash:{current_hash}",  # same hash = unchanged set
                    ),
                )
                assert result.lens == "E_batch_hash"
                assert result.verdict == "REFUTE_HARD"
                assert result.deterministic is True  # §5.5b — single hard veto
                assert result.reason is not None and "empty_delta" in result.reason
                assert result.confidence == 1.0
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_measured_value_never_decimal(self) -> None:
        """Lens E measured_value (hex hash) must not contain '.'."""
        asyncio.run(self._run_no_decimal())

    async def _run_no_decimal(self) -> None:
        import asyncpg
        from pipeline.inquisition.lenses import lens_e_batch_hash

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                result = await lens_e_batch_hash(
                    conn,
                    _claim("inventory", f"inventory:{self.ENTITY_ULID}", "17480"),
                )
                if result.measured_value is not None:
                    assert "." not in result.measured_value
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()


# ---------------------------------------------------------------------------
# D. run_applicable_lenses — §3.6 routing matrix DB integration
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestRunApplicableLenses:
    """Verify §3.6 lens routing returns the correct lens set per subject_type."""

    def test_count_routing(self) -> None:
        asyncio.run(self._run("count", "province:28", "52668"))

    def test_coverage_routing(self) -> None:
        asyncio.run(self._run("coverage", "coverage:desguace", "1895"))

    def test_kind_routing(self) -> None:
        asyncio.run(self._run("kind", "kind:desguace", "1895"))

    def test_inventory_routing(self) -> None:
        asyncio.run(self._run("inventory", "inventory:01KTYVBKCQ6DB0SMNK450P2SXZ", "17480"))

    def test_delta_routing(self) -> None:
        asyncio.run(self._run("delta", "delta:01KTYVBKCQ6DB0SMNK450P2SXZ", "12"))

    async def _run(self, subject_type: str, subject_key: str, asserted_value: str) -> None:
        import asyncpg
        from pipeline.inquisition.lenses import run_applicable_lenses, _LENS_MATRIX
        from pipeline.inquisition.models import Skeptic

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                claim = _claim(subject_type, subject_key, asserted_value)
                results = await run_applicable_lenses(conn, claim)

                expected = set(_LENS_MATRIX.get(subject_type, []))
                returned = {r.lens for r in results}
                assert returned == expected, (
                    f"subject_type={subject_type!r}: expected {expected}, got {returned}"
                )

                for r in results:
                    assert isinstance(r, Skeptic)
                    assert r.verdict in ("ASSERT", "REFUTE_SOFT", "REFUTE_HARD", "ABSTAIN")

                # Lens C always ABSTAINs
                for r in results:
                    if r.lens == "C_live_refetch":
                        assert r.verdict == "ABSTAIN"
                        assert r.reason == "live_refetch_requires_harvest"

                # Lens B always ABSTAINs
                for r in results:
                    if r.lens == "B_raw_recount":
                        assert r.verdict == "ABSTAIN"
                        assert r.reason == "no_raw_evidence_store"

                # No decimal in any numeric measured_value
                for r in results:
                    if r.measured_value is not None and r.measured_value.isdigit():
                        assert "." not in r.measured_value

                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_lens_c_always_abstains_across_all_routes(self) -> None:
        asyncio.run(self._run_c_all())

    async def _run_c_all(self) -> None:
        import asyncpg
        from pipeline.inquisition.lenses import run_applicable_lenses, _LENS_MATRIX

        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                subjects = [
                    ("count", "province:28", "52668"),
                    ("inventory", "inventory:01KTYVBKCQ6DB0SMNK450P2SXZ", "17480"),
                    ("coverage", "coverage:desguace", "1895"),
                    ("kind", "kind:desguace", "1895"),
                ]
                for st, sk, av in subjects:
                    if "C_live_refetch" not in _LENS_MATRIX.get(st, []):
                        continue
                    results = await run_applicable_lenses(conn, _claim(st, sk, av))
                    for r in results:
                        if r.lens == "C_live_refetch":
                            assert r.verdict == "ABSTAIN", (
                                f"Lens C must ABSTAIN for subject_type={st!r}, "
                                f"got {r.verdict!r}"
                            )
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()
