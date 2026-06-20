"""P09-S5: the precision gate wired into quorum.decide() (offline, pure).

TRUSTWORTHY now requires count-quorum AND, when the subject carries a precision contract, the
precision gate to have PASSED. A FAILED precision sample downgrades TRUSTWORTHY -> INCONCLUSIVE
(PRECISION_GATE_FAILED), never REFUTED. No contract / no budget (precision=None) -> no gating
(cost-zero default: absence never blocks a count-quorum verdict). Additive: precision=None
reproduces the pre-S5 behaviour exactly.
"""
from __future__ import annotations

import pytest

from pipeline.inquisition.models import Regime, Skeptic, StateTuple
from pipeline.inquisition.quorum import PrecisionGate, decide

_P = StateTuple(source="autoscout24", tool="curl_cffi", cache="snap_T0", path="ingest")


def _sk(state: StateTuple, verdict: str, measured: str | None = None) -> Skeptic:
    return Skeptic(lens="A_requery", state=state, verdict=verdict, measured_value=measured,
                   confidence=None, reason=None)


def _trustworthy_skeptics() -> list[Skeptic]:
    # Two ASSERT skeptics, each D>=2 from the producer AND from each other -> indep_score>=2.
    s1 = _sk(StateTuple("coches_net", "sql", "snap_T1", "recount"), "ASSERT", "1000")
    s2 = _sk(StateTuple("overture", "browser", "snap_T2", "xsrc"), "ASSERT", "1000")
    return [s1, s2]


@pytest.mark.unit
def test_baseline_trustworthy_without_precision_is_unchanged():
    r = decide(_trustworthy_skeptics(), _P, asserted_value="1000", regime=Regime.EXACT)
    assert r.verdict == "TRUSTWORTHY" and r.decided_value == "1000"
    assert r.p0_contract is None and r.ci_upper is None  # no contract -> no precision metadata


@pytest.mark.unit
def test_precision_passed_keeps_trustworthy_and_carries_metadata():
    gate = PrecisionGate(passed=True, ci_upper=0.005, p0_contract=0.01,
                         precision_n=459, sample_seed="seed-1")
    r = decide(_trustworthy_skeptics(), _P, asserted_value="1000", regime=Regime.EXACT,
               precision=gate)
    assert r.verdict == "TRUSTWORTHY"
    assert r.ci_upper == 0.005 and r.p0_contract == 0.01
    assert r.precision_n == 459 and r.sample_seed == "seed-1"


@pytest.mark.unit
def test_precision_failed_downgrades_trustworthy_to_inconclusive():
    gate = PrecisionGate(passed=False, ci_upper=0.05, p0_contract=0.01,
                         precision_n=300, sample_seed="seed-2")
    r = decide(_trustworthy_skeptics(), _P, asserted_value="1000", regime=Regime.EXACT,
               precision=gate)
    assert r.verdict == "INCONCLUSIVE"          # NOT refuted
    assert r.reason_code == "PRECISION_GATE_FAILED"
    assert r.decided_value is None
    assert r.ci_upper == 0.05 and r.p0_contract == 0.01  # metadata carried for audit


@pytest.mark.unit
def test_precision_does_not_rescue_a_failed_count_quorum():
    # Two skeptics identical to the producer (D=0) -> not admitted -> NO_INDEPENDENT_PATH.
    # A passing precision gate must NOT turn this into TRUSTWORTHY.
    sks = [_sk(_P, "ASSERT", "1000"), _sk(_P, "ASSERT", "1000")]
    gate = PrecisionGate(passed=True, ci_upper=0.001, p0_contract=0.01)
    r = decide(sks, _P, asserted_value="1000", regime=Regime.EXACT, precision=gate)
    assert r.verdict == "REFUTED"
    assert r.reason_code == "NO_INDEPENDENT_PATH"
