"""Advanced R MSE bridge (Rcapture / dga / LCMCR) — robust Rscript subprocess.

Why subprocess and not rpy2: on Windows the stock R binary is not built as a
shared library and rpy2's ``R CMD config`` probe needs Rtools/make, so
``import rpy2.robjects`` fails (verified, not assumed). The Rscript subprocess
contract sidesteps that entirely and uses the SAME real packages — Rcapture's
log-linear model selection (the §2.3 cross-check) and LCMCR's latent-class
Bayesian estimator (heterogeneity-robust).

If no R is found, ``r_available()`` is False and callers keep the pure-Python
estimate with ``r_status='pendiente entorno R'`` — no failure, no pause.

The R cross-check implements the §2 double-verification rule: if R's N̂ diverges
materially from the Python log-linear, the stratum is flagged for distrust.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
from functools import lru_cache

_MSE_R = pathlib.Path(__file__).resolve().parent / "r" / "mse.R"

# Candidate Rscript locations (no-admin user install first, then PATH).
_R_CANDIDATES = [
    r"C:\Users\elias\R-portable\bin\x64\Rscript.exe",
    r"C:\Users\elias\R-portable\bin\Rscript.exe",
    r"C:\Program Files\R\R-4.6.0\bin\x64\Rscript.exe",
]


@lru_cache(maxsize=1)
def r_executable() -> str | None:
    for c in _R_CANDIDATES:
        if os.path.exists(c):
            return c
    from shutil import which

    return which("Rscript")


def r_available() -> bool:
    return r_executable() is not None


def r_status() -> str:
    exe = r_executable()
    return f"available ({exe})" if exe else "pendiente entorno R (Rscript not found)"


def run_mse(freqs: dict[tuple[int, ...], int], *, timeout: int = 180) -> dict | None:
    """Run Rcapture + LCMCR on a capture pattern dict. Returns parsed JSON or None.

    freqs : capture-pattern -> frequency (all-zero excluded).
    Output: {"rcapture": {n_hat, ci_low, ci_high, bic, model}|{error},
             "lcmcr":    {n_hat, ci_low, ci_high}|{error}, "status": ...}
    """
    exe = r_executable()
    if exe is None or not freqs:
        return None
    k = len(next(iter(freqs)))
    patterns = [list(p) + [int(f)] for p, f in freqs.items()]
    payload = {"k": k, "patterns": patterns}
    tmp = pathlib.Path(tempfile.gettempdir()) / f"mse_in_{os.getpid()}.json"
    tmp.write_text(json.dumps(payload), encoding="utf-8")
    try:
        proc = subprocess.run(
            [exe, str(_MSE_R), str(tmp)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if proc.returncode != 0:
            return {"status": "r_error", "stderr": proc.stderr[-500:]}
        out = proc.stdout.strip()
        # the JSON is the last line of stdout
        line = out.splitlines()[-1] if out else ""
        return json.loads(line)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, IndexError) as exc:
        return {"status": "r_error", "exc": str(exc)}
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


def crosscheck(python_n_hat: float, r_result: dict | None, *, tol: float = 0.25) -> dict:
    """§2.3 double-verification: compare Python log-linear N̂ to Rcapture's.

    Returns {agree: bool, rel_diff: float, r_n_hat: float|None, ...}. ``agree``
    is False (distrust) when |relative difference| exceeds ``tol``.
    """
    if not r_result or "rcapture" not in r_result or "error" in r_result.get("rcapture", {}):
        return {"agree": None, "reason": "no_r_estimate", "r_status": r_status()}
    rc = r_result["rcapture"]
    r_n = float(rc["n_hat"])
    rel = abs(r_n - python_n_hat) / max(python_n_hat, 1.0)
    return {
        "agree": rel <= tol,
        "rel_diff": round(rel, 4),
        "r_n_hat": r_n,
        "r_ci": [rc.get("ci_low"), rc.get("ci_high")],
        "r_model": rc.get("model"),
        "lcmcr": r_result.get("lcmcr"),
    }
