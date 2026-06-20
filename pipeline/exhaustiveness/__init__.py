"""Exhaustiveness Framework — certify 100% coverage with confidence intervals.

This package implements the §2 mandate of MASTER_PLAN_CARDEEP_V2: stratified
multi-list capture-recapture (MSE) over the orthogonal discovery lists, with a
formal sealing criterion based on the *lower bound* of the coverage CI.

Layers:
  lists        — orthogonal-list taxonomy (source_key -> list bucket).
  estimators   — pure-Python MSE: Chapman+bootstrap, log-linear (Fienberg),
                 dependence-robust partial-identification bound.
  estimators_r — optional rpy2 bridge to Rcapture/dga/LCMCR (isolated; the
                 pure-Python path never depends on it).
  capture      — build the discovery_capture matrix from the live DB.
  seal         — sealing criterion + per-stratum coverage report.

Doctrine: the point estimate is never used to certify coverage. Sealing uses
N_hat_upper so that coverage_lower = n_obs / N_hat_upper, the conservative
(anti-maquillaje) figure.
"""

from __future__ import annotations

__all__ = ["estimators", "lists", "seal"]
