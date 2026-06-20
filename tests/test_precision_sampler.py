"""P09-S2: muestreador de PRECISION (AQL c=0 / SPRT Wald / Wilson).

Reproduce los numeros trabajados de docs/architecture/verification/V6-STATISTICAL-RIGOR.md
(Tabla 2.2 zero-defect, §3.2 SPRT, §5.1 Wilson). Puro, sin DB ni red.
"""
from __future__ import annotations

import pytest

from pipeline.inquisition import sampler


@pytest.mark.unit
def test_zero_defect_plan_matches_v6_table_2_2():
    # V6 Tabla 2.2 (p0 = 1%): n = 299 @95%, 459 @99%, 688 @99.9% (binomial-exacto c=0).
    assert sampler.plan_zero_defect(20000, 0.01, 0.99)["n"] == 459
    assert sampler.plan_zero_defect(20000, 0.01, 0.95)["n"] == 299
    assert sampler.plan_zero_defect(20000, 0.01, 0.999)["n"] == 688
    assert sampler.plan_zero_defect(20000, 0.01, 0.99)["c"] == 0


@pytest.mark.unit
def test_zero_defect_plan_capped_at_lot_size():
    # No se puede muestrear mas que el lote: n se capa a N.
    assert sampler.plan_zero_defect(50, 0.01, 0.99)["n"] == 50


@pytest.mark.unit
def test_wilson_upper_zero_of_300():
    lo, hi = sampler.wilson_interval(0, 300, conf=0.95)
    assert lo == 0.0
    assert abs(hi - 0.01264) < 0.0005  # V6 §5.1: ~1.26%


@pytest.mark.unit
def test_sprt_plan_constants_match_v6_3_2():
    p = sampler.sprt_plan(p1=0.005, p2=0.02, alpha=0.05, beta=0.10)
    assert abs(p["k"] - 1.4014) < 0.002
    assert abs(p["s"] - 0.010841) < 0.0002
    assert abs(p["h1"] - 2.0625) < 0.002
    assert abs(p["h2"] - 1.6065) < 0.002


@pytest.mark.unit
def test_sprt_accepts_clean_batch_at_191():
    p = sampler.sprt_plan(0.005, 0.02, 0.05, 0.10)
    assert sampler.sprt_evaluate([0] * 190, p)["verdict"] == "continue"  # aun no a 190
    r = sampler.sprt_evaluate([0] * 191, p)
    assert r["verdict"] == "accept" and r["m_stop"] == 191  # V6 §3.2: 0 defectos -> accept a 191


@pytest.mark.unit
def test_sprt_rejects_filthy_batch_early():
    p = sampler.sprt_plan(0.005, 0.02, 0.05, 0.10)
    r = sampler.sprt_evaluate([1, 1], p)
    assert r["verdict"] == "reject" and r["m_stop"] == 2


@pytest.mark.unit
def test_sprt_d2_rejects_around_m37():
    p = sampler.sprt_plan(0.005, 0.02, 0.05, 0.10)
    scores = [1] + [0] * 34 + [1]  # 2o defecto en m=36
    r = sampler.sprt_evaluate(scores, p)
    assert r["verdict"] == "reject" and 30 <= r["m_stop"] <= 38  # V6: d=2 rechaza ~m37


@pytest.mark.unit
def test_precision_estimate_worst_case_lower():
    est = sampler.precision_estimate(0, 300, conf=0.95)
    assert est["precision"] == 1.0
    # precision_lower usa la cota SUPERIOR del defect-rate (anti-maquillaje).
    assert abs(est["precision_lower"] - (1.0 - 0.01264)) < 0.0005
