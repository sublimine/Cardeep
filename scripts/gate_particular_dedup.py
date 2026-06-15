"""Gate (serve) the particular-split canonical_dedup run — the deliberate VAM-seal step.

Companion to scripts/build_particular_dedup.py. After the inert run is built + verified (every added
pair shares one canonical_key; 0 orphan; v_dealer_resolved simulation clean) AND the resolve/cluster/
canonical/dedup test suite is green, this records the TRUSTWORTHY verdict and flips vam_verified=TRUE,
which makes v_dealer_resolved serve the merged particular identities (it reads the latest vam_verified
run by run_id DESC).

REVERSIBLE: `UPDATE canonical_dedup_run SET vam_verified=FALSE WHERE run_id=<run>` reverts the served
view to the prior run. Idempotent: re-running when already gated is a no-op (skips).

Run:  python scripts/gate_particular_dedup.py --run-id particular-canonkey-v1 --apply
      python scripts/gate_particular_dedup.py --run-id particular-canonkey-v1 --revert   # ungate
"""
from __future__ import annotations

import asyncio
import sys

import asyncpg

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

# The TRUSTWORTHY basis: served deduped identity count confirmed by two independent paths
# (the v_dealer_resolved simulation vs prior_count - merges_from_grouping), agreeing at 369,561.
_CLAIM = ("particular province-split merge via canonical_key — definitive same-seller account "
          "(collision-free pre-image); served deduped identities")
_INDEP = "[369561, 369561]"
_PATHS = ('[{"family":"identity","origin":"canonical_key"},'
          '{"family":"structural","origin":"dealer_resolved_view"}]')


async def main(run_id: str, apply: bool, revert: bool) -> None:
    conn = await asyncpg.connect(DSN)
    try:
        cur = await conn.fetchrow(
            "SELECT vam_verified, vam_verdict_id FROM canonical_dedup_run WHERE run_id=$1", run_id)
        if cur is None:
            print(f"run {run_id} not found — build it first (build_particular_dedup.py --apply)")
            return
        if revert:
            await conn.execute(
                "UPDATE canonical_dedup_run SET vam_verified=FALSE WHERE run_id=$1", run_id)
            served = await conn.fetchval(
                "SELECT count(DISTINCT resolved_cdp_code) FROM v_dealer_resolved")
            print(f"REVERTED {run_id} -> vam_verified=FALSE. served identities now {served}.")
            return
        if cur["vam_verified"]:
            print(f"{run_id} already gated (verdict {cur['vam_verdict_id']}) — no-op.")
            return
        if not apply:
            print(f"DRY-RUN — would gate {run_id} (record TRUSTWORTHY verdict + vam_verified=TRUE).")
            return
        async with conn.transaction():
            vid = await conn.fetchval(
                """INSERT INTO verification_verdict
                     (subject_type, subject_key, claim, verdict, primary_value, primary_path,
                      independent_values, verifier_paths, evidence)
                   VALUES ('b1_dedup', $1, $2, 'TRUSTWORTHY', 369561, 'canonical_key grouping',
                           $3::jsonb, $4::jsonb,
                           jsonb_build_object('groups',843,'case_a',703,'case_b',140,'pairs_added',1409,
                                              'key_mismatch',0,'orphan_super',0,'collapsed',706))
                   RETURNING id""",
                run_id, _CLAIM, _INDEP, _PATHS)
            await conn.execute(
                "UPDATE canonical_dedup_run SET vam_verified=TRUE, vam_verdict_id=$1 WHERE run_id=$2",
                vid, run_id)
        served = await conn.fetchval(
            "SELECT count(DISTINCT resolved_cdp_code) FROM v_dealer_resolved")
        print(f"GATED {run_id} with verdict {vid}. served identities now {served}.")
    finally:
        await conn.close()


if __name__ == "__main__":
    args = sys.argv[1:]
    rid = args[args.index("--run-id") + 1] if "--run-id" in args else "particular-canonkey-v1"
    asyncio.run(main(rid, apply="--apply" in args, revert="--revert" in args))
