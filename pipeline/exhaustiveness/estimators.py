"""Pure-Python multi-list capture-recapture (MSE) estimators.

The numbers here are the part of the system we cannot get wrong, so this module
has zero external service dependencies (no DB, no R) and is fully unit-tested
against textbook values.

Estimators
----------
- ``chapman``            : 2-list Chapman estimator with Seber variance and a
                          non-parametric bootstrap CI (Wald is poor for small m).
- ``loglinear_mse``      : K-list Fienberg log-linear estimator. Fits a Poisson
                          GLM over the observed capture cells, predicts the
                          unobserved all-zero cell, and reports a delta-method CI.
                          Pairwise interactions are added by BIC selection so list
                          dependence widens the interval instead of biasing N.
- ``dependence_robust_bound`` : conservative partial-identification interval that
                          does not assume independence (the honest band).
- ``estimate_stratum``   : dispatcher choosing the model by list count / density.

A capture pattern is a tuple of 0/1 of length K (one entry per list, in a fixed
list order). The all-zero pattern is the unobserved cell and must NOT appear in
the input frequencies.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field

import numpy as np


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------
@dataclass
class Estimate:
    """A denominator estimate for one stratum.

    n_obs    : observed distinct entities (sum of all non-zero-pattern freqs).
    n_hat    : point estimate of the true population.
    ci_low   : lower bound of the 95% CI for N (>= n_obs).
    ci_high  : upper bound of the 95% CI for N.
    method   : estimator id.
    k_lists  : number of lists with >0 captures in the stratum.
    confidence : 'high' | 'low' | 'none' — analyst-facing trust flag.
    diagnostics : free-form model detail.
    """

    n_obs: int
    n_hat: float
    ci_low: float
    ci_high: float
    method: str
    k_lists: int
    confidence: str = "low"
    identified: bool = True  # False => sparse overlap, N̂ not trustworthy
    diagnostics: dict = field(default_factory=dict)

    @property
    def coverage_point(self) -> float:
        return self.n_obs / self.n_hat if self.n_hat > 0 else float("nan")

    @property
    def coverage_lower(self) -> float:
        """Conservative coverage: observed over the UPPER bound of N̂.

        This is the anti-maquillaje figure used for sealing.
        """
        return self.n_obs / self.ci_high if self.ci_high > 0 else float("nan")


# ---------------------------------------------------------------------------
# 2-list Chapman
# ---------------------------------------------------------------------------
def chapman_point(n1: int, n2: int, m: int) -> tuple[float, float]:
    """Chapman N_hat and Seber variance. m = overlap between the two lists."""
    n_hat = ((n1 + 1) * (n2 + 1) / (m + 1)) - 1
    num = (n1 + 1) * (n2 + 1) * (n1 - m) * (n2 - m)
    den = (m + 1) ** 2 * (m + 2)
    var = num / den if den > 0 else float("inf")
    return n_hat, var


def chapman(
    n1: int,
    n2: int,
    m: int,
    *,
    n_boot: int = 4000,
    seed: int = 20260620,
) -> Estimate:
    """Chapman estimator with a non-parametric bootstrap CI.

    n1, n2 : sizes of list 1 and list 2 (incl. the overlap).
    m      : number of entities captured by BOTH lists.
    """
    if m < 0 or n1 < m or n2 < m:
        raise ValueError(f"invalid capture counts n1={n1} n2={n2} m={m}")
    n_obs = n1 + n2 - m
    n_hat, var = chapman_point(n1, n2, m)

    # Bootstrap: resample the union of observed individuals, each labelled by
    # which list(s) saw it, and recompute Chapman. This propagates the
    # discreteness of small m far better than the normal Wald interval.
    only1 = n1 - m
    only2 = n2 - m
    labels = np.array([0] * only1 + [1] * only2 + [2] * m)  # 0=L1,1=L2,2=both
    rng = np.random.default_rng(seed)
    boot = np.empty(n_boot)
    size = labels.size
    for i in range(n_boot):
        s = rng.choice(labels, size=size, replace=True)
        bn1 = int(np.count_nonzero(s == 0) + np.count_nonzero(s == 2))
        bn2 = int(np.count_nonzero(s == 1) + np.count_nonzero(s == 2))
        bm = int(np.count_nonzero(s == 2))
        bhat, _ = chapman_point(bn1, bn2, bm)
        boot[i] = bhat
    ci_low = float(max(n_obs, np.percentile(boot, 2.5)))
    ci_high = float(max(ci_low, np.percentile(boot, 97.5)))
    confidence = "low"  # 2-list is a floor, never a certification (per §2.3)
    return Estimate(
        n_obs=n_obs,
        n_hat=float(n_hat),
        ci_low=ci_low,
        ci_high=ci_high,
        method="chapman_bootstrap",
        k_lists=2,
        confidence=confidence,
        diagnostics={"n1": n1, "n2": n2, "m": m, "seber_var": var, "n_boot": n_boot},
    )


# ---------------------------------------------------------------------------
# K-list log-linear (Fienberg) MSE
# ---------------------------------------------------------------------------
def _design_and_counts(
    freqs: dict[tuple[int, ...], int], k: int, interactions: list[tuple[int, int]]
) -> tuple[np.ndarray, np.ndarray]:
    """Build (X, y) over all 2^k - 1 observable cells.

    Cells absent from ``freqs`` contribute a structural zero count (0), which is
    valid for Poisson log-linear fitting; the unobserved all-zero cell is
    excluded (it is what we estimate).
    """
    patterns = [
        p for p in itertools.product((0, 1), repeat=k) if any(p)
    ]
    y = np.array([freqs.get(p, 0) for p in patterns], dtype=float)
    cols = [np.ones(len(patterns))]  # intercept
    for j in range(k):
        cols.append(np.array([p[j] for p in patterns], dtype=float))
    for a, b in interactions:
        cols.append(np.array([p[a] * p[b] for p in patterns], dtype=float))
    X = np.column_stack(cols)
    return X, y


def _fit_poisson(X: np.ndarray, y: np.ndarray):
    """Fit Poisson GLM (log link). Returns statsmodels result or None on failure."""
    try:
        import statsmodels.api as sm

        model = sm.GLM(y, X, family=sm.families.Poisson())
        res = model.fit(maxiter=200)
        return res
    except Exception:
        return None


def loglinear_mse(
    freqs: dict[tuple[int, ...], int],
    *,
    select_interactions: bool = True,
    max_interactions: int = 6,
) -> Estimate:
    """K-list Fienberg log-linear MSE estimator.

    freqs : capture-pattern -> frequency (all-zero pattern excluded).

    Model: Poisson log-linear with main effects, optionally adding pairwise
    interactions chosen greedily by BIC. The expected unobserved cell is
    exp(intercept); N_hat = n_obs + exp(intercept). CI via delta method on the
    intercept, widened to reflect interaction uncertainty.
    """
    if not freqs:
        raise ValueError("empty capture frequencies")
    k = len(next(iter(freqs)))
    if any(len(p) != k for p in freqs):
        raise ValueError("inconsistent pattern lengths")
    if (0,) * k in freqs:
        raise ValueError("all-zero pattern must not be supplied")
    n_obs = int(sum(freqs.values()))
    lists_present = [j for j in range(k) if any(p[j] for p in freqs)]
    k_present = len(lists_present)

    # main-effects-only baseline
    chosen: list[tuple[int, int]] = []
    X, y = _design_and_counts(freqs, k, chosen)
    res = _fit_poisson(X, y)
    if res is None:
        # degenerate — fall back to observed count (no extrapolation possible)
        return Estimate(
            n_obs=n_obs,
            n_hat=float(n_obs),
            ci_low=float(n_obs),
            ci_high=float(n_obs),
            method="loglinear_failed",
            k_lists=k_present,
            confidence="none",
            diagnostics={"reason": "glm_fit_failed"},
        )
    best_bic = res.bic_llf
    best_res, best_X = res, X

    if select_interactions and k_present >= 3:
        candidates = list(itertools.combinations(lists_present, 2))
        improved = True
        while improved and len(chosen) < max_interactions:
            improved = False
            trial_best = None
            for cand in candidates:
                if cand in chosen:
                    continue
                X2, y2 = _design_and_counts(freqs, k, chosen + [cand])
                r2 = _fit_poisson(X2, y2)
                if r2 is None:
                    continue
                if r2.bic_llf < best_bic - 1e-6:
                    if trial_best is None or r2.bic_llf < trial_best[0]:
                        trial_best = (r2.bic_llf, cand, r2, X2)
            if trial_best is not None:
                best_bic, cand, best_res, best_X = trial_best
                chosen.append(cand)
                improved = True

    intercept = float(best_res.params[0])
    se_intercept = float(np.sqrt(best_res.cov_params()[0, 0]))
    m0 = math.exp(intercept)
    n_hat = n_obs + m0
    # delta method on exp(beta0): se(m0) = m0 * se(beta0); on N it is the same.
    se_n = m0 * se_intercept
    ci_low = max(float(n_obs), n_hat - 1.96 * se_n)
    ci_high = max(ci_low, n_hat + 1.96 * se_n)
    confidence = "high" if k_present >= 3 else "low"
    return Estimate(
        n_obs=n_obs,
        n_hat=float(n_hat),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        method="loglinear_bic" if chosen else "loglinear_independent",
        k_lists=k_present,
        confidence=confidence,
        diagnostics={
            "interactions": [list(c) for c in chosen],
            "bic": float(best_bic),
            "intercept": intercept,
            "se_intercept": se_intercept,
            "m0_unobserved": m0,
        },
    )


# ---------------------------------------------------------------------------
# Dependence-robust partial-identification bound
# ---------------------------------------------------------------------------
def dependence_robust_bound(freqs: dict[tuple[int, ...], int]) -> tuple[float, float]:
    """Honest band that does NOT assume list independence.

    Lower bound: the observed count (you have at least what you saw).
    Upper bound: the maximum log-linear N over the model class {independent,
    each single pairwise interaction}. Positive list dependence inflates N, so
    taking the max over plausible dependence structures yields a conservative
    ceiling — the right denominator for anti-maquillaje sealing.
    """
    n_obs = int(sum(freqs.values()))
    k = len(next(iter(freqs)))
    lists_present = [j for j in range(k) if any(p[j] for p in freqs)]
    candidate_models: list[list[tuple[int, int]]] = [[]]
    for cand in itertools.combinations(lists_present, 2):
        candidate_models.append([cand])
    highs = [n_obs]
    for inter in candidate_models:
        X, y = _design_and_counts(freqs, k, inter)
        res = _fit_poisson(X, y)
        if res is None:
            continue
        m0 = math.exp(float(res.params[0]))
        se = math.exp(float(res.params[0])) * float(np.sqrt(res.cov_params()[0, 0]))
        highs.append(n_obs + m0 + 1.96 * se)
    return float(n_obs), float(max(highs))


# ---------------------------------------------------------------------------
# Stratum dispatcher
# ---------------------------------------------------------------------------
# A stratum estimate is "identified" only if the overlap pins N̂ down. With very
# sparse overlap, log-linear / Chapman N̂ explodes (m0 -> huge); such estimates
# are flagged unidentified and excluded from the certified national roll-up.
# N̂ must be <= IDENT_CAP * n_obs to be certifiable. 5.0 => a stratum is only
# "identified" if its implied coverage floor is >= 20%; below that the overlap
# does not pin N down and the stratum is reported as uncertified, not sealed.
IDENT_CAP = 5.0


def _mark_identified(e: "Estimate") -> "Estimate":
    cap = IDENT_CAP * e.n_obs
    if e.n_obs <= 0 or not math.isfinite(e.ci_high):
        e.identified = False
    elif e.n_hat > cap or e.ci_high > cap:
        # bounded point estimate but explosive interval => not pinned down
        e.identified = False
    else:
        e.identified = e.confidence != "none"
    if not e.identified and e.confidence == "high":
        e.confidence = "low"
    return e


def estimate_stratum(
    freqs: dict[tuple[int, ...], int],
    *,
    list_order: list[str] | None = None,
) -> Estimate:
    """Choose the estimator by list count / data density (per §2.4).

    K>=3 with data  -> log-linear MSE (BIC interactions); validate-able by R.
    K==2            -> Chapman bootstrap (floor, low confidence).
    K<2 or no data  -> no extrapolation; N_hat = n_obs, confidence 'none'.

    The result is flagged ``identified`` iff the overlap pins N̂ down (finite CI
    and N̂ <= IDENT_CAP * n_obs); unidentified strata are observed-floor only.
    """
    if not freqs:
        raise ValueError("empty stratum")
    k = len(next(iter(freqs)))
    n_obs = int(sum(freqs.values()))
    lists_present = [j for j in range(k) if any(p[j] for p in freqs)]
    k_present = len(lists_present)

    if k_present >= 3:
        est = loglinear_mse(freqs)
        # widen with the dependence-robust ceiling so the seal stays honest
        _, robust_high = dependence_robust_bound(freqs)
        if robust_high > est.ci_high:
            est.ci_high = robust_high
        if list_order:
            est.diagnostics["list_order"] = list_order
        return _mark_identified(est)

    if k_present == 2:
        j1, j2 = lists_present
        n1 = sum(f for p, f in freqs.items() if p[j1])
        n2 = sum(f for p, f in freqs.items() if p[j2])
        m = sum(f for p, f in freqs.items() if p[j1] and p[j2])
        est = chapman(n1, n2, m)
        if list_order:
            est.diagnostics["list_order"] = list_order
        return _mark_identified(est)

    # single list — cannot estimate the unseen; report observed only
    return Estimate(
        n_obs=n_obs,
        n_hat=float(n_obs),
        ci_low=float(n_obs),
        ci_high=float("inf"),
        method="single_list_no_estimate",
        k_lists=k_present,
        confidence="none",
        identified=False,
        diagnostics={"reason": "need >=2 orthogonal lists"},
    )
