"""Lens B (orthogonal recount) + Lens C (live refetch) — now ACTIVE, not abstaining."""
from dataclasses import dataclass

import pytest

from pipeline.inquisition import _lens_c
from pipeline.inquisition.lenses import lens_b_raw_recount, lens_c_live_refetch
from pipeline.inquisition.models import StateTuple


@dataclass
class _Claim:
    subject_type: str
    subject_key: str
    asserted_value: str
    producer_state: StateTuple
    evidence_uri: str | None = None
    tolerance: float = 0.005


_PROD = StateTuple(source="portal", tool="scraper", cache="snap_T0", path="ingest")


class _FakeConn:
    """Returns a queued scalar for fetchrow({'n': ...})."""
    def __init__(self, n):
        self._n = n

    async def fetchrow(self, *a, **k):
        return {"n": self._n}


# ---- Lens B: orthogonal recount asserts/refutes a real number ---------------

@pytest.mark.asyncio
async def test_lens_b_count_asserts_when_ledger_matches():
    claim = _Claim("count", "province:28", "100", _PROD)
    sk = await lens_b_raw_recount(_FakeConn(100), claim)
    assert sk.verdict == "ASSERT"
    assert sk.measured_value == "100"
    assert sk.lens == "B_raw_recount"
    # independence from Lens A: tool+path differ
    assert sk.state.tool == "ledger" and sk.state.path == "lens_b_raw_recount"


@pytest.mark.asyncio
async def test_lens_b_count_refutes_on_divergence():
    # ledger sees 80 distinct entities but producer claimed 100 -> REFUTE (phantom rows)
    claim = _Claim("count", "province:28", "1000", _PROD)
    sk = await lens_b_raw_recount(_FakeConn(100), claim)
    assert sk.verdict == "REFUTE_SOFT"
    assert sk.reason == "raw_recount_mismatch"


@pytest.mark.asyncio
async def test_lens_b_inventory_counts_distinct_deeplinks():
    claim = _Claim("inventory", "inventory:E1", "12", _PROD)
    sk = await lens_b_raw_recount(_FakeConn(12), claim)
    assert sk.verdict == "ASSERT" and sk.measured_value == "12"
    assert sk.state.tool == "distinct_id"


@pytest.mark.asyncio
async def test_lens_b_abstains_on_unsupported_type():
    claim = _Claim("kind", "kind:desguace", "5", _PROD)
    sk = await lens_b_raw_recount(_FakeConn(5), claim)
    assert sk.verdict == "ABSTAIN"


# ---- Lens C: live refetch via injected fetcher ------------------------------

def _jsonld(n):
    return "".join('<script>{"@type":"Car"}</script>' for _ in range(n))


@pytest.mark.asyncio
async def test_lens_c_asserts_when_live_count_matches(monkeypatch):
    _lens_c.set_fetcher(lambda url: _jsonld(10))
    try:
        claim = _Claim("count", "province:28", "10", _PROD,
                       evidence_uri="count:https://portal.example/listing")
        sk = await lens_c_live_refetch(None, claim)
        assert sk.verdict == "ASSERT" and sk.measured_value == "10"
        assert sk.state.path == "lens_c_live_refetch" and sk.state.source == "live_portal"
    finally:
        _lens_c.set_fetcher(None)


@pytest.mark.asyncio
async def test_lens_c_refutes_when_live_count_diverges(monkeypatch):
    _lens_c.set_fetcher(lambda url: _jsonld(100))
    try:
        claim = _Claim("count", "province:28", "1000", _PROD,
                       evidence_uri="https://portal.example/listing")
        sk = await lens_c_live_refetch(None, claim)
        assert sk.verdict == "REFUTE_SOFT"
    finally:
        _lens_c.set_fetcher(None)


@pytest.mark.asyncio
async def test_lens_c_abstains_without_fetchable_uri():
    claim = _Claim("count", "province:28", "10", _PROD, evidence_uri=None)
    sk = await lens_c_live_refetch(None, claim)
    assert sk.verdict == "ABSTAIN" and sk.reason == "live_refetch_no_fetchable_uri"


@pytest.mark.asyncio
async def test_lens_c_abstains_when_fetch_fails(monkeypatch):
    def boom(url):
        raise RuntimeError("blocked")
    _lens_c.set_fetcher(boom)
    try:
        claim = _Claim("count", "province:28", "10", _PROD,
                       evidence_uri="https://portal.example/x")
        sk = await lens_c_live_refetch(None, claim)
        assert sk.verdict == "ABSTAIN" and sk.reason.startswith("live_fetch_failed")
    finally:
        _lens_c.set_fetcher(None)
