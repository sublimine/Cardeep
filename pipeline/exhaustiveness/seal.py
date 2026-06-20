"""Sealing: per-stratum estimation, national roll-up, and the seal verdict.

Sealing criterion (§2.6): a stratum is SEALED at threshold X iff its
``coverage_lower`` (= n_obs / ci_high, the conservative figure) >= X. The point
estimate is never used to certify.

National roll-up: the certified denominator is the SUM of per-stratum N̂ (the
plan mandates stratification; a single pooled national fit pools heterogeneous
strata and is reported only as an unreliable cross-check). Strata CIs are combined
assuming between-stratum independence (variances add).
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass

import psycopg2

from pipeline.exhaustiveness import capture
from pipeline.exhaustiveness import estimators as est

DSN = capture.DSN
DEFAULT_THRESHOLD = 0.95


@dataclass
class StratumSeal:
    province_code: str | None
    segment: str | None
    estimate: est.Estimate
    threshold: float
    sealed: bool


def _seal_one(prov, seg, freqs, threshold) -> StratumSeal:
    e = est.estimate_stratum(freqs)
    cov_lower = e.coverage_lower
    sealed = (
        e.identified
        and math.isfinite(cov_lower)
        and cov_lower >= threshold
    )
    return StratumSeal(prov, seg, e, threshold, sealed)


def compute(
    build_run_id: str,
    *,
    dsn: str = DSN,
    threshold: float = DEFAULT_THRESHOLD,
    include_mkt: bool = False,
) -> dict:
    """Estimate every stratum, persist to exhaustiveness_estimate, return summary."""
    patterns, buckets = capture.read_patterns(
        build_run_id, dsn=dsn, include_mkt=include_mkt
    )
    seals: list[StratumSeal] = []
    for (prov, seg), freqs in sorted(
        patterns.items(), key=lambda kv: (kv[0][0] or "", kv[0][1] or "")
    ):
        seals.append(_seal_one(prov, seg, freqs, threshold))

    # national roll-up: only IDENTIFIED strata contribute their N̂; unidentified
    # strata (sparse overlap) contribute their observed floor only, so the
    # certified denominator is never inflated by explosive sparse estimates.
    identified = [s for s in seals if s.estimate.identified]
    unidentified = [s for s in seals if not s.estimate.identified]
    n_obs_total = sum(s.estimate.n_obs for s in seals)
    n_hat_sum = sum(s.estimate.n_hat for s in identified)
    n_hat_sum += sum(s.estimate.n_obs for s in unidentified)  # floor for the rest
    usable = identified
    half_widths = [
        (s.estimate.ci_high - s.estimate.n_hat)
        for s in identified
        if math.isfinite(s.estimate.ci_high)
    ]
    nat_se = math.sqrt(sum((hw / 1.96) ** 2 for hw in half_widths)) if half_widths else 0.0
    nat_ci_low = max(n_obs_total, n_hat_sum - 1.96 * nat_se)
    nat_ci_high = n_hat_sum + 1.96 * nat_se
    nat_cov_point = n_obs_total / n_hat_sum if n_hat_sum else float("nan")
    nat_cov_lower = n_obs_total / nat_ci_high if nat_ci_high else float("nan")

    # pooled national fit (cross-check only, flagged unreliable)
    pooled_freqs: dict[tuple[int, ...], int] = {}
    for freqs in patterns.values():
        for pat, f in freqs.items():
            pooled_freqs[pat] = pooled_freqs.get(pat, 0) + f
    pooled = est.estimate_stratum(pooled_freqs) if pooled_freqs else None

    _persist(build_run_id, seals, threshold, buckets,
             national=(n_obs_total, n_hat_sum, nat_ci_low, nat_ci_high,
                       nat_cov_point, nat_cov_lower), dsn=dsn)

    return {
        "build_run_id": build_run_id,
        "buckets": list(buckets),
        "n_strata": len(seals),
        "n_strata_identified": len(identified),
        "n_strata_unidentified": len(unidentified),
        "n_obs_uncertified": sum(s.estimate.n_obs for s in unidentified),
        "n_strata_sealed": sum(1 for s in seals if s.sealed),
        "national": {
            "n_obs": n_obs_total,
            "n_hat_stratified_sum": round(n_hat_sum, 1),
            "ci_low": round(nat_ci_low, 1),
            "ci_high": round(nat_ci_high, 1),
            "coverage_point": round(nat_cov_point, 4),
            "coverage_lower": round(nat_cov_lower, 4),
            "sealed": nat_cov_lower >= threshold,
        },
        "national_pooled_crosscheck": (
            {
                "n_hat": round(pooled.n_hat, 1),
                "ci_low": round(pooled.ci_low, 1),
                "ci_high": round(pooled.ci_high, 1),
                "method": pooled.method,
                "note": "pooled across heterogeneous strata — UNRELIABLE, cross-check only",
            }
            if pooled
            else None
        ),
        "seals": seals,
    }


def _persist(build_run_id, seals, threshold, buckets, *, national, dsn):
    conn = psycopg2.connect(dsn)
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                "DELETE FROM exhaustiveness_estimate WHERE build_run_id = %s",
                (build_run_id,),
            )
            for s in seals:
                e = s.estimate
                diag = dict(e.diagnostics)
                diag["buckets"] = list(buckets)
                cur.execute(
                    """
                    INSERT INTO exhaustiveness_estimate
                      (build_run_id, province_code, segment, k_lists, n_obs, n_hat,
                       ci_low, ci_high, coverage_point, coverage_lower, method,
                       confidence, seal_threshold, sealed, diagnostics)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        build_run_id, s.province_code, s.segment, e.k_lists, e.n_obs,
                        e.n_hat, e.ci_low,
                        (e.ci_high if math.isfinite(e.ci_high) else 1e18),
                        (e.coverage_point if math.isfinite(e.coverage_point) else 0.0),
                        (e.coverage_lower if math.isfinite(e.coverage_lower) else 0.0),
                        e.method, e.confidence, threshold, s.sealed,
                        json.dumps(diag),
                    ),
                )
            # national row (province_code NULL, segment NULL)
            n_obs, n_hat, cl, ch, cp, clow = national
            cur.execute(
                """
                INSERT INTO exhaustiveness_estimate
                  (build_run_id, province_code, segment, k_lists, n_obs, n_hat,
                   ci_low, ci_high, coverage_point, coverage_lower, method,
                   confidence, seal_threshold, sealed, diagnostics)
                VALUES (%s,NULL,NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    build_run_id, len(buckets), n_obs, n_hat, cl, ch, cp, clow,
                    "stratified_sum", "high", threshold, clow >= threshold,
                    json.dumps({"buckets": list(buckets), "rollup": "sum_of_strata"}),
                ),
            )
    finally:
        conn.close()
