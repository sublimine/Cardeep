"""End-to-end runner for the exhaustiveness framework.

  python -m pipeline.exhaustiveness.cli run [--run-id ID] [--threshold 0.95] [--include-mkt]

Builds the capture matrix from the live DB, estimates every stratum, persists the
results, and prints the first real denominator + certified coverage with CI.
"""

from __future__ import annotations

import argparse
import sys

from pipeline.exhaustiveness import capture, seal
from pipeline.exhaustiveness.estimators_r import r_status


def run(run_id: str, threshold: float, include_mkt: bool,
        unit: str = "resolved", splink_run_id: str | None = None,
        r_crosscheck: bool = False) -> int:
    print("=" * 74)
    print("CARDEEP — EXHAUSTIVENESS FRAMEWORK (sec2 V2)")
    print("=" * 74)
    print(f"build_run_id : {run_id}")
    print(f"threshold    : {threshold:.2%}")
    print(f"capture unit : {unit}")
    print(f"R bridge     : {r_status()}")
    print()

    bsum = capture.build(run_id, unit=unit, splink_run_id=splink_run_id)
    print("CAPTURE MATRIX BUILT (live DB 127.0.0.1:5433):")
    for k, v in bsum.items():
        print(f"  {k:<20} {v}")
    print()

    res = seal.compute(run_id, threshold=threshold, include_mkt=include_mkt,
                       r_crosscheck=r_crosscheck)
    print(f"ORTHOGONAL LISTS (MSE): {res['buckets']}")
    print(
        f"strata={res['n_strata']}  identified={res['n_strata_identified']}  "
        f"unidentified={res['n_strata_unidentified']} (n_obs_uncertified="
        f"{res['n_obs_uncertified']})  sealed={res['n_strata_sealed']}"
    )
    print()
    nat = res["national_certified"]
    print("NATIONAL CERTIFIED DENOMINATOR (identified strata only):")
    print(f"  observed in identified strata n_obs  = {nat['n_obs']}")
    print(f"  N_hat (stratified sum)               = {nat['n_hat_stratified_sum']}")
    print(f"  95% CI                               = [{nat['ci_low']}, {nat['ci_high']}]")
    print(f"  certified coverage (point)           = {nat['coverage_point']:.2%}")
    print(f"  certified coverage (lower bound)     = {nat['coverage_lower']:.2%}")
    print(f"  SEALED at {threshold:.0%}?                       = {nat['sealed']}")
    print(f"  UNCERTIFIED (denominator unknown)    = {res['uncertified']['n_obs']} observed dealers")
    print()
    cc = res["national_pooled_crosscheck"]
    if cc:
        print("POOLED national cross-check (UNRELIABLE — heterogeneity):")
        print(f"  N_hat={cc['n_hat']}  CI=[{cc['ci_low']}, {cc['ci_high']}]  ({cc['method']})")
        print()

    # top sealed / strongest strata
    sealed = [s for s in res["seals"] if s.sealed]
    print(f"SEALED STRATA ({len(sealed)}):")
    for s in sorted(sealed, key=lambda x: -x.estimate.n_obs)[:15]:
        e = s.estimate
        print(
            f"  {s.province_code} {s.segment:<14} n_obs={e.n_obs:<6} "
            f"N_hat={e.n_hat:8.1f} cov_low={e.coverage_lower:.2%} K={e.k_lists} {e.method}"
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="exhaustiveness")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--run-id", default="first-real-20260620")
    r.add_argument("--threshold", type=float, default=0.95)
    r.add_argument("--include-mkt", action="store_true")
    r.add_argument("--unit", choices=["resolved", "splink"], default="resolved")
    r.add_argument("--splink-run-id", default="splink-current")
    r.add_argument("--r-crosscheck", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return run(args.run_id, args.threshold, args.include_mkt,
                   unit=args.unit, splink_run_id=args.splink_run_id,
                   r_crosscheck=args.r_crosscheck)
    return 1


if __name__ == "__main__":
    sys.exit(main())
