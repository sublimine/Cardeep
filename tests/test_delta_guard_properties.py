"""T1.3-ext — property invariants of the GONE guard (delta_guard.should_emit_gone).

A GONE sweep retires inventory; firing it on a PARTIAL harvest would wipe cars that still exist (a
visible lie at the served surface). This guard only allows the sweep when the drain is provably
complete. Verified over the WHOLE input space (Hypothesis); range oracles hardcoded (0.95 / 0.50),
independent of the module constants, so a mutation is genuinely caught.
"""
from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from pipeline.delta_guard import should_emit_gone

pytestmark = pytest.mark.unit

_DECLARED = 0.95   # contract thresholds (hardcoded oracle)
_PREV = 0.50


@given(declared=st.integers(1, 10**6), harvested=st.integers(0, 10**6))
def test_declared_probe_allows_iff_complete(declared, harvested):
    allow, _ = should_emit_gone(harvested, declared, previous_available=None)
    assert allow == (harvested >= declared * _DECLARED)


@given(prev=st.integers(1, 10**6))
def test_declared_zero_with_existing_stock_never_wipes(prev):
    # count=0 on a valid response (gateway anomaly) must NEVER authorize wiping live stock.
    allow, _ = should_emit_gone(0, 0, previous_available=prev)
    assert allow is False


@given(prev=st.integers(1, 10**6), harvested=st.integers(0, 10**6))
def test_fallback_probe_allows_iff_half(prev, harvested):
    allow, _ = should_emit_gone(harvested, None, previous_available=prev)
    assert allow == (harvested >= prev * _PREV)


def test_first_run_or_empty_history_allows():
    assert should_emit_gone(0, None, None)[0] is True
    assert should_emit_gone(0, None, 0)[0] is True


@given(declared=st.integers(2, 10**6))
def test_severe_partial_drain_never_authorizes_a_sweep(declared):
    # a drain that captured <~1% of the declared total must NEVER allow a GONE sweep.
    allow, _ = should_emit_gone(harvested=declared // 100, declared=declared,
                                previous_available=declared)
    assert allow is False
