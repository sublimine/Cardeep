"""T2.3 — Chao (1987) non-parametric lower-bound MSE estimator (pure-Python, no DB / no R).

Robust to capture heterogeneity: it assumes NEITHER list independence NOR homogeneity, so it is the
honest floor for sparse, heterogeneous strata where the log-linear N̂ explodes. Verified here against
closed-form textbook values. N̂ = S_obs + f1²/(2 f2), bias-corrected to S_obs + f1(f1-1)/2 when f2==0;
f1/f2 = entities seen by exactly one / exactly two lists.

SCOPE: this adds the verified estimator to the module. It is NOT wired into estimate_stratum (which
feeds the LIVE served seal) here — changing the served roll-up needs the DB dry-run+golden+Ferrari
lane, and docker is down. Wiring Chao into the roll-up is the DB-gated follow-up (plans/road-to-13).
"""
from __future__ import annotations

import math

import pytest

from pipeline.exhaustiveness.estimators import chao_lower

pytestmark = pytest.mark.unit

# 3 lists: singletons f1 = 5+3+2 = 10; doubletons f2 = 3+1+1 = 5; triple = 4. S_obs = 19.
_FREQS_F2POS = {
    (1, 0, 0): 5, (0, 1, 0): 3, (0, 0, 1): 2,
    (1, 1, 0): 3, (1, 0, 1): 1, (0, 1, 1): 1,
    (1, 1, 1): 4,
}


def test_chao_point_with_doubletons():
    # N̂ = S_obs + f1²/(2 f2) = 19 + 100/10 = 29
    e = chao_lower(_FREQS_F2POS)
    assert e.n_obs == 19
    assert e.n_hat == pytest.approx(29.0)
    assert e.method == "chao1"
    assert e.diagnostics["f1"] == 10 and e.diagnostics["f2"] == 5


def test_chao_bias_corrected_when_no_doubletons():
    # f1=7, f2=0 -> bias-corrected N̂ = 7 + 7·6/2 = 28
    e = chao_lower({(1, 0): 4, (0, 1): 3})
    assert e.n_obs == 7
    assert e.n_hat == pytest.approx(28.0)
    assert e.method == "chao1_bias_corrected"


def test_chao_ci_brackets_point_and_floors_at_nobs():
    e = chao_lower(_FREQS_F2POS)
    assert e.n_obs <= e.ci_low <= e.n_hat <= e.ci_high
    assert math.isfinite(e.ci_high)


def test_chao_coverage_lower_is_conservative():
    # coverage_lower = n_obs/ci_high <= coverage_point = n_obs/n_hat (the anti-maquillaje figure)
    e = chao_lower(_FREQS_F2POS)
    assert e.coverage_lower <= e.coverage_point


def test_chao_rejects_empty_and_all_zero():
    with pytest.raises(ValueError):
        chao_lower({})
    with pytest.raises(ValueError):
        chao_lower({(0, 0): 3})
