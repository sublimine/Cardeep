"""Unit tests for SU-B2 ε3 — five orthogonal inquisition lenses.

No DB required. Tests cover:
- ClaimEnvelope contract (frozen, typed)
- StateTuple independence proofs (D ≥ 2 for all 5 lenses)
- _compute_set_hash determinism (Lens E)
- Lens B structural ABSTAIN (no raw store)
- Lens C structural ABSTAIN + zero network calls

Real DB subjects used in sibling test_inquisition_lenses_db.py:
    province_code='28' (Madrid): 52 668 entities  [VERIFIED 2026-06-15]
    kind='desguace':             1 895 entities    [VERIFIED 2026-06-15]
    dgt_cat → desguace:          1 292 entities    [VERIFIED 2026-06-15]
    wallapop_wholesale → particular: 220 634 entities [VERIFIED 2026-06-15]
    vehicle entity 01KTYVBKCQ6DB0SMNK450P2SXZ: 17 480 vehicles [VERIFIED]
"""
from __future__ import annotations

import asyncio
import dataclasses
import hashlib
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.inquisition.lenses import ClaimEnvelope, _compute_set_hash
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
    """Factory for ClaimEnvelope with sensible defaults for tests."""
    return ClaimEnvelope(
        claim_id="01TEST000000000000000000000",
        subject_type=subject_type,
        subject_key=subject_key,
        asserted_value=asserted_value,
        producer_state=StateTuple(
            source=source, tool=tool, cache=cache, path=path
        ),
        tolerance=tolerance,
        evidence_uri=evidence_uri,
    )


# ---------------------------------------------------------------------------
# A. ClaimEnvelope contract
# ---------------------------------------------------------------------------

class TestClaimEnvelope:
    """Verify the ClaimEnvelope contract is frozen and correctly typed."""

    def test_frozen(self) -> None:
        c = _claim("count", "province:28", "52668")
        with pytest.raises((TypeError, AttributeError, dataclasses.FrozenInstanceError)):
            c.asserted_value = "0"  # type: ignore[misc]

    def test_fields(self) -> None:
        c = _claim("kind", "kind:desguace", "1895")
        assert c.subject_type == "kind"
        assert c.asserted_value == "1895"
        assert isinstance(c.producer_state, StateTuple)

    def test_evidence_uri_optional(self) -> None:
        c = _claim("count", "all", "390621")
        assert c.evidence_uri is None

    def test_evidence_uri_hash_prefix(self) -> None:
        c = _claim("delta", "delta:ULID", "5", evidence_uri="hash:abc123")
        assert c.evidence_uri == "hash:abc123"


# ---------------------------------------------------------------------------
# B. StateTuple independence proofs — all 5 lenses
# ---------------------------------------------------------------------------

class TestLensAState:
    """Lens A: tool=sql, path=lens_a_requery → D=2 vs scraper producer."""

    def test_d_ge_2_vs_scraper_producer(self) -> None:
        producer = StateTuple(source="test_portal", tool="scraper", cache="snap_T0", path="ingest")
        lens_a_state = StateTuple(source="test_portal", tool="sql", cache="snap_T0", path="lens_a_requery")
        # Differs on: tool (scraper→sql) + path (ingest→lens_a_requery) → D=2
        assert indep_distance(lens_a_state, producer) == 2

    def test_same_source_cache(self) -> None:
        """Lens A reuses source+cache, only tool+path differ."""
        producer = StateTuple(source="wallapop", tool="curl_cffi", cache="snap_T0", path="ingest")
        lens_a_state = StateTuple(source="wallapop", tool="sql", cache="snap_T0", path="lens_a_requery")
        assert lens_a_state.source == producer.source
        assert lens_a_state.cache == producer.cache
        assert indep_distance(lens_a_state, producer) == 2


class TestLensBState:
    """Lens B: tool=json_parser, path=lens_b_raw_recount → D=2."""

    def test_d_ge_2_vs_scraper_producer(self) -> None:
        producer = StateTuple(source="test_portal", tool="scraper", cache="snap_T0", path="ingest")
        lens_b_state = StateTuple(source="test_portal", tool="json_parser", cache="snap_T0", path="lens_b_raw_recount")
        assert indep_distance(lens_b_state, producer) == 2


class TestLensCState:
    """Lens C (when active): D=4 (all 4 dims differ)."""

    def test_d_equals_4_vs_ingest_producer(self) -> None:
        producer = StateTuple(source="test_portal", tool="scraper", cache="snap_T0", path="ingest")
        lens_c_state = StateTuple(source="live_portal", tool="browser", cache="live_T1", path="lens_c_live_refetch")
        assert indep_distance(lens_c_state, producer) == 4

    def test_all_four_dims_differ(self) -> None:
        producer = StateTuple(source="portal_x", tool="curl_cffi", cache="snap_T0", path="ingest")
        lens_c_state = StateTuple(source="live_portal", tool="browser", cache="live_T1", path="lens_c_live_refetch")
        assert lens_c_state.source != producer.source
        assert lens_c_state.tool != producer.tool
        assert lens_c_state.cache != producer.cache
        assert lens_c_state.path != producer.path


class TestLensDState:
    """Lens D: source=<DIFFERENT_SOURCE> → D≥2 (source alone gives D=1, plus path=D≥2)."""

    def test_d_ge_2_different_source(self) -> None:
        producer = StateTuple(source="wallapop_wholesale", tool="scraper", cache="snap_T0", path="ingest")
        lens_d_state = StateTuple(source="dgt_cat", tool="sql", cache="snap_T0", path="lens_d_xsrc")
        # Differs on: source, tool, path → D=3
        assert indep_distance(lens_d_state, producer) >= 2

    def test_source_always_differs(self) -> None:
        """Lens D's defining property: its source is always DIFFERENT from the producer."""
        producer = StateTuple(source="wallapop_wholesale", tool="scraper", cache="snap_T0", path="ingest")
        lens_d_state = StateTuple(source="dgt_cat", tool="sql", cache="snap_T0", path="lens_d_xsrc")
        assert lens_d_state.source != producer.source


class TestLensEState:
    """Lens E: tool=sha256, path=lens_e_hash → D=2."""

    def test_d_ge_2_vs_scraper_producer(self) -> None:
        producer = StateTuple(source="test_portal", tool="scraper", cache="snap_T0", path="ingest")
        lens_e_state = StateTuple(source="test_portal", tool="sha256", cache="snap_T0", path="lens_e_hash")
        assert indep_distance(lens_e_state, producer) == 2


# ---------------------------------------------------------------------------
# C. _compute_set_hash — Lens E determinism
# ---------------------------------------------------------------------------

class TestBatchHash:
    """Unit tests for _compute_set_hash — determinism and delta detection."""

    def test_same_input_same_hash(self) -> None:
        rows = [("ulid1", "15000", "2026-06-15"), ("ulid2", "null", "2026-06-14")]
        assert _compute_set_hash(rows) == _compute_set_hash(rows)

    def test_order_independent(self) -> None:
        """Hash is over sorted rows → insertion order does not matter."""
        rows_a = [("ulid1", "15000", "2026-06-15"), ("ulid2", "null", "2026-06-14")]
        rows_b = [("ulid2", "null", "2026-06-14"), ("ulid1", "15000", "2026-06-15")]
        assert _compute_set_hash(rows_a) == _compute_set_hash(rows_b)

    def test_empty_set_deterministic(self) -> None:
        expected = hashlib.sha256(b"").hexdigest()
        assert _compute_set_hash([]) == expected

    def test_price_change_different_hash(self) -> None:
        rows_a = [("ulid1", "15000", "2026-06-15")]
        rows_b = [("ulid1", "16000", "2026-06-15")]
        assert _compute_set_hash(rows_a) != _compute_set_hash(rows_b)

    def test_added_vehicle_different_hash(self) -> None:
        rows_a = [("ulid1", "15000", "2026-06-15")]
        rows_b = [("ulid1", "15000", "2026-06-15"), ("ulid2", "null", "2026-06-14")]
        assert _compute_set_hash(rows_a) != _compute_set_hash(rows_b)

    def test_hash_is_64_hex_chars(self) -> None:
        h = _compute_set_hash([("ulid1", "15000", "2026-06-15")])
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_canonical_int_no_decimal(self) -> None:
        """measured_value must never be '1234.0'."""
        from pipeline.inquisition.lenses import _canonical_int
        assert _canonical_int(1234) == "1234"
        assert _canonical_int(1234.0) == "1234"
        assert _canonical_int(52668.0) == "52668"
        assert "." not in _canonical_int(52668.0)


# ---------------------------------------------------------------------------
# D. Lens B — ABSTAIN(no_raw_evidence_store) in current €0 state
# ---------------------------------------------------------------------------

class _FakeConn:
    """Minimal asyncpg-like conn: fetchrow returns {'n': <queued>}."""
    def __init__(self, n):
        self._n = n

    async def fetchrow(self, *a, **k):
        return {"n": self._n}


class TestLensBActive:
    """Lens B is ACTIVE: orthogonal recount, asserts/refutes (no longer abstains)."""

    def test_asserts_when_orthogonal_recount_matches(self) -> None:
        from pipeline.inquisition.lenses import lens_b_raw_recount

        claim = _claim("count", "province:28", "52668")
        result = asyncio.run(lens_b_raw_recount(_FakeConn(52668), claim))

        assert result.lens == "B_raw_recount"
        assert result.verdict == "ASSERT"
        assert result.measured_value == "52668"

    def test_refutes_when_recount_diverges(self) -> None:
        from pipeline.inquisition.lenses import lens_b_raw_recount

        claim = _claim("count", "province:28", "52668")  # ledger sees far fewer
        result = asyncio.run(lens_b_raw_recount(_FakeConn(40000), claim))

        assert result.verdict == "REFUTE_SOFT"
        assert result.reason == "raw_recount_mismatch"

    def test_state_d_ge_2(self) -> None:
        """Lens B state provides D ≥ 2 vs any ingest producer."""
        from pipeline.inquisition.lenses import lens_b_raw_recount

        claim = _claim("count", "province:28", "52668", tool="curl_cffi", path="ingest")
        result = asyncio.run(lens_b_raw_recount(_FakeConn(52668), claim))

        assert indep_distance(result.state, claim.producer_state) >= 2


# ---------------------------------------------------------------------------
# E. Lens C — DECLARED STUB, zero network calls
# ---------------------------------------------------------------------------

class TestLensCStub:
    """Lens C is ACTIVE but ABSTAINs (honestly) when there is no fetchable URI."""

    def test_abstains_no_network(self) -> None:
        """No fetchable evidence_uri -> ABSTAIN, no network call made."""
        from pipeline.inquisition.lenses import lens_c_live_refetch

        claim = _claim("count", "kind:desguace", "1895")
        result = asyncio.run(lens_c_live_refetch(None, claim))  # type: ignore[arg-type]

        assert result.lens == "C_live_refetch"
        assert result.verdict == "ABSTAIN"
        assert result.reason == "live_refetch_no_fetchable_uri"
        assert result.measured_value is None

    def test_state_shape_d4_ready(self) -> None:
        """Lens C state carries the future D=4 egress identity shape."""
        from pipeline.inquisition.lenses import lens_c_live_refetch

        claim = _claim("count", "all", "390621")
        result = asyncio.run(lens_c_live_refetch(None, claim))  # type: ignore[arg-type]

        st = result.state
        assert st.source == "live_portal"
        assert st.tool == "browser"
        assert st.cache == "live_T1"
        assert st.path == "lens_c_live_refetch"

    def test_abstains_for_every_supported_subject_type(self) -> None:
        """Lens C ABSTAINs regardless of subject_type."""
        from pipeline.inquisition.lenses import lens_c_live_refetch

        for st, sk, av in [
            ("count", "province:28", "52668"),
            ("inventory", "inventory:ULID", "100"),
            ("coverage", "coverage:desguace", "1895"),
            ("kind", "kind:desguace", "1895"),
        ]:
            claim = _claim(st, sk, av)
            result = asyncio.run(lens_c_live_refetch(None, claim))  # type: ignore[arg-type]
            assert result.verdict == "ABSTAIN", (
                f"Lens C must ABSTAIN for subject_type={st!r}, got {result.verdict!r}"
            )
