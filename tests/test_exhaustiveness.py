"""Tests for the exhaustiveness MSE estimators (the numbers we cannot get wrong).

Validated against textbook capture-recapture values and deterministic synthetic
populations with a known true N.
"""

from __future__ import annotations

import math

import pytest

from pipeline.exhaustiveness import estimators as est


# ---------------------------------------------------------------------------
# Chapman — textbook value
# ---------------------------------------------------------------------------
def test_chapman_point_textbook():
    # n1=200, n2=120, m=40 -> N_hat = 201*121/41 - 1 = 592.24...
    n_hat, var = est.chapman_point(200, 120, 40)
    assert n_hat == pytest.approx(592.24, abs=0.1)
    assert var > 0


def test_chapman_estimate_ci_brackets_point():
    e = est.chapman(200, 120, 40, n_boot=2000)
    assert e.n_obs == 200 + 120 - 40  # 280
    assert e.ci_low <= e.n_hat <= e.ci_high
    assert e.ci_low >= e.n_obs  # never claim fewer than observed
    assert e.confidence == "low"  # 2-list is a floor


def test_chapman_rejects_impossible_overlap():
    with pytest.raises(ValueError):
        est.chapman(10, 10, 20)  # m > n1


# ---------------------------------------------------------------------------
# Log-linear — 2 lists reduces to Petersen under independence
# ---------------------------------------------------------------------------
def test_loglinear_two_list_matches_petersen():
    # cells: (1,1)=40, (1,0)=160, (0,1)=80 ; Petersen N = 200*120/40 = 600
    freqs = {(1, 1): 40, (1, 0): 160, (0, 1): 80}
    e = est.loglinear_mse(freqs, select_interactions=False)
    assert e.n_obs == 280
    assert e.n_hat == pytest.approx(600.0, rel=0.02)


# ---------------------------------------------------------------------------
# Log-linear — 3 independent lists recover the true N exactly
# ---------------------------------------------------------------------------
def _independent_cells(N: int, ps: tuple[float, ...]) -> dict[tuple[int, ...], int]:
    import itertools

    out: dict[tuple[int, ...], int] = {}
    for pat in itertools.product((0, 1), repeat=len(ps)):
        prob = 1.0
        for bit, p in zip(pat, ps):
            prob *= p if bit else (1 - p)
        if any(pat):
            out[pat] = round(N * prob)
    return out


def test_loglinear_three_list_recovers_true_n():
    # N=1000, capture probs .3/.4/.5 independent -> unobserved cell = 210
    freqs = _independent_cells(1000, (0.3, 0.4, 0.5))
    e = est.loglinear_mse(freqs)
    assert e.n_hat == pytest.approx(1000.0, rel=0.03)
    assert e.ci_low <= 1000 <= e.ci_high
    assert e.k_lists == 3
    assert e.confidence == "high"


def test_loglinear_positive_dependence_widens_not_biases():
    # Inject positive dependence between lists 1&2; the estimator should still
    # bracket a plausible N and not collapse to n_obs.
    freqs = {
        (1, 1, 1): 80,
        (1, 1, 0): 90,
        (1, 0, 1): 40,
        (1, 0, 0): 50,
        (0, 1, 1): 45,
        (0, 1, 0): 55,
        (0, 0, 1): 120,
    }
    e = est.loglinear_mse(freqs)
    assert e.n_hat > e.n_obs
    assert e.ci_high > e.ci_low


# ---------------------------------------------------------------------------
# Dependence-robust bound — ceiling >= log-linear upper, floor == observed
# ---------------------------------------------------------------------------
def test_dependence_robust_bound():
    freqs = _independent_cells(1000, (0.3, 0.4, 0.5))
    low, high = est.dependence_robust_bound(freqs)
    n_obs = sum(freqs.values())
    assert low == n_obs
    assert high >= 1000 * 0.9  # ceiling at least near true N


# ---------------------------------------------------------------------------
# Stratum dispatcher
# ---------------------------------------------------------------------------
def test_estimate_stratum_dispatches_by_k():
    three = _independent_cells(1000, (0.3, 0.4, 0.5))
    e3 = est.estimate_stratum(three)
    assert e3.k_lists == 3
    assert "loglinear" in e3.method

    two = {(1, 1): 40, (1, 0): 160, (0, 1): 80}
    e2 = est.estimate_stratum(two)
    assert e2.method == "chapman_bootstrap"

    one = {(1, 0): 50}
    e1 = est.estimate_stratum(one)
    assert e1.confidence == "none"
    assert math.isinf(e1.ci_high)


def test_sparse_overlap_flagged_unidentified():
    # 3 lists, near-zero overlap -> log-linear N̂ explodes -> must be unidentified
    freqs = {
        (1, 0, 0): 5000,
        (0, 1, 0): 4000,
        (0, 0, 1): 3000,
        (1, 1, 0): 1,
        (1, 0, 1): 1,
        (0, 1, 1): 1,
    }
    e = est.estimate_stratum(freqs)
    assert e.identified is False  # sparse -> not trustworthy


def test_dense_overlap_is_identified():
    freqs = _independent_cells(1000, (0.3, 0.4, 0.5))
    e = est.estimate_stratum(freqs)
    assert e.identified is True


def test_coverage_lower_uses_upper_bound():
    e = est.Estimate(
        n_obs=80, n_hat=100.0, ci_low=90.0, ci_high=125.0,
        method="x", k_lists=3, confidence="high",
    )
    assert e.coverage_point == pytest.approx(0.8)
    assert e.coverage_lower == pytest.approx(80 / 125.0)  # conservative


# ---------------------------------------------------------------------------
# R bridge (advanced MSE) — skipped if R is not installed
# ---------------------------------------------------------------------------
def test_r_bridge_recovers_known_n():
    from pipeline.exhaustiveness import estimators_r as R

    if not R.r_available():
        pytest.skip(f"R not available: {R.r_status()}")
    freqs = _independent_cells(1000, (0.3, 0.4, 0.5))
    res = R.run_mse(freqs)
    assert res is not None and res.get("status") == "ok"
    assert res["rcapture"]["n_hat"] == pytest.approx(1000, rel=0.05)
    cc = R.crosscheck(1000.0, res)
    assert cc["agree"] is True


def test_rpy2_inprocess_lcmcr():
    from pipeline.exhaustiveness import estimators_r as R

    if not R.rpy2_available():
        pytest.skip("rpy2 not available (needs R + Rtools make)")
    freqs = _independent_cells(1000, (0.3, 0.4, 0.5))
    res = R.lcmcr_rpy2(freqs, samples=2000, burnin=1000)
    assert res is not None and "n_hat" in res
    assert res["n_hat"] == pytest.approx(1000, rel=0.10)
    assert res["method"] == "lcmcr_rpy2"


def test_r_crosscheck_flags_divergence():
    from pipeline.exhaustiveness import estimators_r as R

    fake_r = {"rcapture": {"n_hat": 5000.0, "ci_low": 4000, "ci_high": 6000, "model": "x"}}
    cc = R.crosscheck(1000.0, fake_r)
    assert cc["agree"] is False  # 5x divergence => distrust


def test_splink_normalisers():
    from pipeline.exhaustiveness import splink_merge as sm

    assert sm._norm_name("AUTOMOCIÓN del Oeste, S.L.") == "automocion del oeste"
    assert sm._host("https://www.AutoX.es/stock") == "autox.es"
    assert sm._digits("+34 911-22-33-44") == "911223344"  # last 9 digits


def test_splink_union_find_merges_transitively():
    from pipeline.exhaustiveness.splink_merge import _UF

    uf = _UF()
    uf.union("b", "c")
    uf.union("c", "d")
    assert uf.find("b") == uf.find("d") == "b"  # lowest id is root


# ---------------------------------------------------------------------------
# External triangulation seam (§2.7)
# ---------------------------------------------------------------------------
def test_triangulation_verdicts():
    from pipeline.exhaustiveness import triangulation as T

    assert T.triangulate(1000, 1000)["verdict"] == "consistent"
    assert T.triangulate(2000, 1000)["verdict"] == "n_hat_high"
    assert T.triangulate(500, 1000)["verdict"] == "n_hat_low"
    assert T.triangulate(1000, None)["verdict"] == "no_anchor"


def test_triangulation_loads_csv(tmp_path):
    from pipeline.exhaustiveness import triangulation as T

    csv_file = tmp_path / "c.csv"
    csv_file.write_text(
        "province_code,segment,n_external\n28,compraventa,1200\n,,40000\n",
        encoding="utf-8",
    )
    d = T.load_external_census(csv_file)
    assert d[("28", "compraventa")] == 1200.0
    assert d[(None, None)] == 40000.0
