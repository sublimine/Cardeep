"""T1.3-ext — invariants of the Inquisition quorum engine (the VAM adversarial core, §5.2/§5.4).

`within_tolerance` (§5.2) and `decide` (§5.4) are PURE. These pin the verdict logic that certifies
every served census number: a TRUSTWORTHY verdict requires ≥2 INDEPENDENT asserting skeptics agreeing
(no rival, no refute majority); a credible HARD refute vetoes; a lone path never certifies. No DB.
"""
from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from pipeline.inquisition.models import Regime, Skeptic, StateTuple
from pipeline.inquisition.quorum import decide, within_tolerance

pytestmark = pytest.mark.unit

_PROD = StateTuple("prod", "sql", "snap0", "ingest")


def _sk(verdict, value, n, det=False):
    # state differs from the producer AND from every other skeptic in all 4 dims (D=4) -> always
    # admitted and mutually independent, so the test exercises decide()'s logic, not admission edges.
    st_ = StateTuple(f"src{n}", f"tool{n}", f"cache{n}", f"path{n}")
    return Skeptic(lens="A_requery", state=st_, verdict=verdict, measured_value=value,
                   confidence=1.0, reason="r", deterministic=det)


# ---- §5.2 within_tolerance ----
@given(asserted=st.floats(min_value=1, max_value=1e7, allow_nan=False, allow_infinity=False),
       measured=st.floats(min_value=0, max_value=2e7, allow_nan=False, allow_infinity=False))
def test_drift_band_is_max_rel_abs(asserted, measured):
    tol = max(0.005 * asserted, 50.0)   # hardcoded oracle (independent of TAU_REL/TAU_ABS)
    assert within_tolerance(measured, asserted, Regime.DRIFT) == (abs(measured - asserted) <= tol)


def test_exact_regime_requires_equality():
    assert within_tolerance(100, 100, Regime.EXACT) is True
    assert within_tolerance(101, 100, Regime.EXACT) is False


# ---- §5.4 decide ----
def test_two_independent_asserts_same_value_is_trustworthy():
    r = decide([_sk("ASSERT", "100", 1), _sk("ASSERT", "100", 2)],
               _PROD, asserted_value="100", regime=Regime.EXACT)
    assert r.verdict == "TRUSTWORTHY" and r.decided_value == "100" and r.indep_score >= 2


def test_credible_deterministic_hard_refute_vetoes():
    r = decide([_sk("ASSERT", "100", 1), _sk("ASSERT", "100", 2),
                _sk("REFUTE_HARD", None, 3, det=True)],
               _PROD, asserted_value="100", regime=Regime.EXACT)
    assert r.verdict == "REFUTED"


def test_single_assert_has_no_independent_path():
    r = decide([_sk("ASSERT", "100", 1)], _PROD, asserted_value="100", regime=Regime.EXACT)
    assert r.verdict == "REFUTED" and r.reason_code == "NO_INDEPENDENT_PATH"


def test_rival_value_is_split_quorum():
    r = decide([_sk("ASSERT", "100", 1), _sk("ASSERT", "100", 2),
                _sk("ASSERT", "200", 3), _sk("ASSERT", "200", 4)],
               _PROD, asserted_value="100", regime=Regime.EXACT)
    assert r.verdict == "REFUTED" and r.reason_code == "SPLIT_QUORUM"


def test_refute_majority_refutes():
    r = decide([_sk("ASSERT", "100", 1), _sk("ASSERT", "100", 2),
                _sk("REFUTE_SOFT", "90", 3), _sk("REFUTE_SOFT", "90", 4)],
               _PROD, asserted_value="100", regime=Regime.EXACT)
    assert r.verdict == "REFUTED" and r.reason_code == "MAJORITY_REFUTE"


def test_lone_nondeterministic_hard_refute_is_demoted_not_a_veto():
    # §5.5 false-veto guard: a single NON-deterministic hard refute must NOT veto on its own.
    r = decide([_sk("ASSERT", "100", 1), _sk("ASSERT", "100", 2),
                _sk("REFUTE_HARD", None, 3, det=False)],
               _PROD, asserted_value="100", regime=Regime.EXACT)
    assert r.verdict == "TRUSTWORTHY"
