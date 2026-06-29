"""T1.3-ext — property invariants of the ingest-boundary numeric publish-gate (price_sanity).

These gates feed the SERVED delta: a value that PASSES must be in-range, and junk must be nulled,
over the WHOLE input space (not a handful of examples). The range oracles are HARDCODED here
(5_000_000 / 1_500_000), independent of the module constants, so a mutation of PRICE_MAX / KM_MAX is
genuinely caught (non-vacuity recorded in plans/road-to-13/PROGRESO.md).
"""
from __future__ import annotations

from datetime import datetime

import pytest
from hypothesis import given
from hypothesis import strategies as st

from pipeline.price_sanity import (
    sanitize_km,
    sanitize_price,
    sanitize_year,
    sanitize_year_km,
)

pytestmark = pytest.mark.unit

_PRICE_MAX = 5_000_000   # contract ceiling — hardcoded oracle, independent of the module constant
_KM_MAX = 1_500_000


@given(st.one_of(st.integers(min_value=-10**9, max_value=10**9),
                 st.floats(allow_nan=False, allow_infinity=False)))
def test_price_gate_passes_only_in_range(p):
    out = sanitize_price(p)
    if out is not None:
        assert 0 < float(out) <= _PRICE_MAX   # whatever passes the gate is valid
        assert out == p                        # ...and returned UNCHANGED


@given(st.floats(min_value=0.01, max_value=float(_PRICE_MAX), allow_nan=False, allow_infinity=False))
def test_valid_price_is_preserved(p):
    assert sanitize_price(p) == p


@given(st.integers(min_value=-10**9, max_value=10**9))
def test_km_gate_passes_only_in_range(k):
    out = sanitize_km(k)
    if out is not None:
        assert 0 <= int(out) < _KM_MAX
        assert out == k


@given(st.integers())
def test_year_gate_passes_only_in_range(y):
    out = sanitize_year(y)
    if out is not None:
        assert 1900 <= int(out) <= datetime.now().year + 1
        assert out == y


@given(st.integers(min_value=1900, max_value=2035), st.integers(min_value=0, max_value=2_000_000))
def test_year_km_cross_nulls_only_the_impossible_age(year, km):
    y, k = sanitize_year_km(year, km)
    age = datetime.now().year - year
    impossible = (age <= 0 and km > 300_000) or (age <= 1 and km > 500_000)
    if impossible:
        assert y is None and k is None   # NULL BOTH (which field is wrong is ambiguous)
    else:
        assert y == year and k == km     # both preserved


def test_documented_sentinels_are_nulled():
    # the real served sentinels the module was calibrated against MUST be rejected.
    assert sanitize_price(10_000_000) is None    # Qashqai @ €10M sentinel
    assert sanitize_price(9_999_999) is None     # all-9s "price on request"
    assert sanitize_price(0) is None and sanitize_price(-5) is None
    assert sanitize_km(1_500_000) is None        # Wallapop unset-odometer sentinel (>=)
    assert sanitize_km(5_000_000) is None
    assert sanitize_year(2098) is None and sanitize_year(1899) is None
