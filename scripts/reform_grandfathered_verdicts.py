"""Reform grandfathered verification_verdict rows so quorum is real (audit P2 D-grandfathered).

PROBLEM (verified live 2026-06-15): 989/1024 TRUSTWORTHY verdicts have quorum_n<2 because they were
written by the pre-B-1 verifier in the OLD shapes:
  - independent_values as a JSON OBJECT  {"fetched":1292,"db_ingested":1292,...}  (new shape: array)
  - verifier_paths     as a STRING array ["db_ingested","fetched","source_declared"] (new: [{family,origin}])
The GENERATED columns quorum_n=cdp_modal_cluster(independent_values,tolerance),
family_n=cdp_distinct_families(verifier_paths), origin_n=cdp_distinct_origins(verifier_paths) all
return 0 for those shapes, so chk_trustworthy_needs_quorum (NOT VALID) could never be validated.

FIX: reform each object-shaped row to the new shapes using the canonical _path_family() from
pipeline.verify (no re-VAM needed — the values are recoverable). The GENERATED columns recompute on
UPDATE. For TRUSTWORTHY rows we set the verdict via the SAME SQL quorum functions on the reformed
values, so verdict and the GENERATED columns are consistent and chk_trustworthy_needs_quorum is
satisfied — a row that cannot prove quorum>=2 ∧ family>=2 ∧ origin>=2 is honestly downgraded to
UNVERIFIED (Law I: confess the hole, never certify a shared blind spot). NULL-independent_values
TRUSTWORTHY rows (no data at all) are downgraded to UNVERIFIED. Finally VALIDATE the constraint.

Run:  python scripts/reform_grandfathered_verdicts.py            # dry-run (report only)
      python scripts/reform_grandfathered_verdicts.py --apply    # execute + VALIDATE constraint
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import asyncpg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.verify import _path_family

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

# Reform + decide verdict in ONE update. The verdict CASE calls the SAME functions the GENERATED
# columns use on the SAME reformed values, so verdict <-> (quorum_n,family_n,origin_n) are consistent
# and chk_trustworthy_needs_quorum (enforced on UPDATE even while NOT VALID) is never violated.
_REFORM_SQL = """
UPDATE verification_verdict SET
  independent_values = $2::jsonb,
  verifier_paths     = $3::jsonb,
  verdict = CASE
    WHEN verdict = 'TRUSTWORTHY' THEN
      CASE WHEN cdp_modal_cluster($2::jsonb, tolerance) >= 2
            AND cdp_distinct_families($3::jsonb) >= 2
            AND cdp_distinct_origins($3::jsonb)  >= 2
           THEN 'TRUSTWORTHY' ELSE 'UNVERIFIED' END
    ELSE verdict END
WHERE id = $1
"""

_DOWNGRADE_NULL_SQL = """
UPDATE verification_verdict SET verdict = 'UNVERIFIED'
WHERE verdict = 'TRUSTWORTHY' AND independent_values IS NULL
RETURNING id
"""


def _reform_paths(vp) -> list[dict] | None:
    """String-array verifier_paths -> [{family,origin}]. Already-object arrays pass through."""
    if not isinstance(vp, list) or not vp:
        return None
    if isinstance(vp[0], dict):
        return vp  # already new shape
    return [{"family": _path_family(str(s)), "origin": str(s)} for s in vp]


async def main(apply: bool) -> None:
    conn = await asyncpg.connect(DSN)
    try:
        rows = await conn.fetch(
            "SELECT id, verdict, independent_values, verifier_paths, quorum_n "
            "FROM verification_verdict "
            "WHERE jsonb_typeof(independent_values) = 'object' ORDER BY id")
        stay_trustworthy = downgraded = reformed_other = skipped = 0
        for r in rows:
            iv = json.loads(r["independent_values"]) if isinstance(r["independent_values"], str) else r["independent_values"]
            vp = json.loads(r["verifier_paths"]) if isinstance(r["verifier_paths"], str) else r["verifier_paths"]
            if not isinstance(iv, dict):
                skipped += 1
                continue
            iv_arr = list(iv.values())                 # object -> array of values
            vp_objs = _reform_paths(vp)
            if vp_objs is None:
                skipped += 1
                continue
            # Predict the verdict outcome for reporting (same predicate as the SQL CASE).
            fams = {p["family"] for p in vp_objs}
            origs = {p["origin"] for p in vp_objs}
            from collections import Counter
            modal = max(Counter(iv_arr).values()) if iv_arr else 0
            keeps = r["verdict"] == "TRUSTWORTHY" and modal >= 2 and len(fams) >= 2 and len(origs) >= 2
            if r["verdict"] == "TRUSTWORTHY":
                if keeps:
                    stay_trustworthy += 1
                else:
                    downgraded += 1
            else:
                reformed_other += 1
            if apply:
                await conn.execute(_REFORM_SQL, r["id"],
                                   json.dumps(iv_arr), json.dumps(vp_objs))
        null_downgraded = 0
        if apply:
            null_ids = await conn.fetch(_DOWNGRADE_NULL_SQL)
            null_downgraded = len(null_ids)
        else:
            null_downgraded = await conn.fetchval(
                "SELECT count(*) FROM verification_verdict "
                "WHERE verdict='TRUSTWORTHY' AND independent_values IS NULL")

        print(f"object-shaped rows         : {len(rows)}")
        print(f"  TRUSTWORTHY -> stay        : {stay_trustworthy}")
        print(f"  TRUSTWORTHY -> UNVERIFIED  : {downgraded}")
        print(f"  non-TRUSTWORTHY reformed   : {reformed_other}")
        print(f"  skipped (unexpected shape) : {skipped}")
        print(f"NULL-iv TRUSTWORTHY -> UNVERIFIED: {null_downgraded}")

        if apply:
            # Now every TRUSTWORTHY row has real quorum -> close the grandfathering window.
            await conn.execute(
                "ALTER TABLE verification_verdict VALIDATE CONSTRAINT chk_trustworthy_needs_quorum")
            bad = await conn.fetchval(
                "SELECT count(*) FROM verification_verdict WHERE verdict='TRUSTWORTHY' "
                "AND (quorum_n<2 OR family_n<2 OR origin_n<2)")
            print(f"\nAPPLIED. chk_trustworthy_needs_quorum VALIDATED. "
                  f"TRUSTWORTHY-without-quorum remaining: {bad} (must be 0)")
        else:
            print("\nDRY-RUN — no writes. Re-run with --apply to execute + VALIDATE the constraint.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main(apply="--apply" in sys.argv))
