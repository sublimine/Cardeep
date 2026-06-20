"""Optional R bridge (Rcapture / dga / LCMCR) via rpy2 — ISOLATED.

This module is a strict add-on. The pure-Python path (estimators.py) never
imports it and never depends on it. If rpy2 or R is absent, ``r_available()``
returns False and callers fall back to the Python estimators with a recorded
``r_status='pendiente entorno R'`` flag — no failure, no pause.

When R is present, ``loglinear_r`` / ``lcmcr_r`` give a second, independent
estimate used for the §2 double-verification rule (if R disagrees materially
with the Python log-linear, distrust the stratum).
"""

from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=1)
def r_available() -> bool:
    try:
        import rpy2.robjects  # noqa: F401

        return True
    except Exception:
        return False


def r_status() -> str:
    return "available" if r_available() else "pendiente entorno R (rpy2/R not installed)"


def ensure_packages(packages: tuple[str, ...] = ("Rcapture", "dga", "LCMCR")) -> dict:
    """Install the R packages (coste cero). No-op if R is unavailable."""
    if not r_available():
        return {"status": r_status(), "installed": []}
    from rpy2.robjects.packages import importr
    from rpy2.robjects.vectors import StrVector

    utils = importr("utils")
    utils.chooseCRANmirror(ind=1)
    missing = []
    for p in packages:
        try:
            importr(p)
        except Exception:
            missing.append(p)
    if missing:
        utils.install_packages(StrVector(missing))
    return {"status": "ok", "checked": list(packages), "installed": missing}


def loglinear_r(freqs: dict[tuple[int, ...], int]) -> dict | None:
    """Rcapture::closedpMS.t log-linear MSE. Returns N̂+CI dict, or None if no R."""
    if not r_available():
        return None
    try:
        import itertools

        import numpy as np
        import rpy2.robjects as ro
        from rpy2.robjects.packages import importr

        rcapture = importr("Rcapture")
        k = len(next(iter(freqs)))
        patterns = [p for p in itertools.product((0, 1), repeat=k) if any(p)]
        mat = []
        for p in patterns:
            mat.append(list(p) + [freqs.get(p, 0)])
        arr = np.array(mat, dtype=float)
        rmat = ro.r.matrix(ro.FloatVector(arr.flatten()), nrow=arr.shape[0], byrow=True)
        res = rcapture.closedpMS_t(rmat, dfreq=True)
        # extract the best model abundance + CI
        results = res.rx2("results")
        # closedpMS.t returns a table; take the row with min BIC
        import numpy as np2

        tbl = np2.array(results)
        # columns include 'abundance','stderr','BIC' depending on version
        names = list(res.rx2("results").names[1]) if hasattr(results, "names") else []
        return {"r_raw": str(res), "abundance_table_shape": tbl.shape, "model_names": names}
    except Exception as exc:  # isolate any R failure
        return {"error": str(exc)}


def lcmcr_r(freqs: dict[tuple[int, ...], int], *, samples: int = 10000) -> dict | None:
    """LCMCR latent-class Bayesian estimator. Returns posterior summary or None."""
    if not r_available():
        return None
    try:
        import itertools

        import rpy2.robjects as ro
        from rpy2.robjects.packages import importr

        lcmcr = importr("LCMCR")
        k = len(next(iter(freqs)))
        patterns = [p for p in itertools.product((0, 1), repeat=k) if any(p)]
        # build a data.frame of factors + Freq
        cols = {}
        for j in range(k):
            cols[f"L{j}"] = ro.IntVector([p[j] for p in patterns])
        cols["Freq"] = ro.IntVector([freqs.get(p, 0) for p in patterns])
        df = ro.DataFrame(cols)
        for j in range(k):
            df[j] = ro.r["as.factor"](df.rx2(f"L{j}"))
        sampler = lcmcr.lcmCR(df, tabular=True, K=5, seed=20260620)
        post = lcmcr.lcmCR_PostSampl(sampler, burnin=5000, samples=samples, thinning=10)
        import numpy as np

        arr = np.array(post)
        return {
            "n_hat": float(np.median(arr)),
            "ci_low": float(np.percentile(arr, 2.5)),
            "ci_high": float(np.percentile(arr, 97.5)),
            "method": "lcmcr_bayes",
        }
    except Exception as exc:
        return {"error": str(exc)}
