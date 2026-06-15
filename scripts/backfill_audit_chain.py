"""Backfill the tamper-evident verdict_audit hash-chain (audit P2 D-audit-chain-grandfather-gap).

trg_verdict_audit_append is AFTER INSERT (forward-only) and 0026 did no backfill, so the chain
covers only 46/1085 verdicts (verdict_id 1111-1410); the 1039 pre-genesis verdicts (incl. the
reformed grandfathered TRUSTWORTHY) have ZERO tamper-evidence. This appends a hash-chained audit row
for each unaudited verdict, in id order, CHAINED AFTER the current tail (non-destructive — verdict_audit
is append-only/immutable; reconstructing would violate that). The payload/chain_hash are computed by
Postgres with the EXACT same expressions as cdp_audit_append (0026:208-219), so the hashes match the
trigger byte-for-byte. Verify-before-commit: the dry-run backfills in a rolled-back transaction and
checks the whole chain (0 bad links) before --apply ever commits.

Run:  python scripts/backfill_audit_chain.py            # dry-run (backfill + verify, ROLLBACK)
      python scripts/backfill_audit_chain.py --apply     # commit iff the chain verifies clean
"""
from __future__ import annotations

import asyncio
import sys

import asyncpg

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

# EXACT payload formula from cdp_audit_append (0026). Computed in PG so it matches the trigger.
_PAYLOAD = """encode(digest(
  COALESCE(subject_type,'')||'|'||COALESCE(subject_key,'')||'|'||COALESCE(claim,'')||'|'||
  COALESCE(verdict,'')||'|'||COALESCE(primary_value,'')||'|'||
  COALESCE(verifier_paths::text,'[]')||'|'||COALESCE(independent_values::text,'[]')||'|'||
  COALESCE(quorum_n::text,'0')||'|'||COALESCE(family_n::text,'0'), 'sha256'), 'hex')"""

_APPEND_ONE = f"""
INSERT INTO verdict_audit
  (verdict_id, subject_type, subject_key, claim, verdict, quorum_n, family_n,
   payload_hash, prev_hash, chain_hash)
SELECT id, subject_type, subject_key, claim, verdict, quorum_n, family_n,
       {_PAYLOAD},
       $2,
       encode(digest(COALESCE($2,'GENESIS') || '|' || {_PAYLOAD}, 'sha256'), 'hex')
FROM verification_verdict WHERE id = $1
RETURNING chain_hash
"""

# Whole-chain integrity: every row's chain_hash must equal sha256(coalesce(prev,'GENESIS')|payload).
_VERIFY = """
SELECT
  (SELECT count(*) FROM verification_verdict v
     WHERE NOT EXISTS (SELECT 1 FROM verdict_audit a WHERE a.verdict_id = v.id)) AS unaudited,
  (SELECT count(*) FROM verdict_audit
     WHERE chain_hash <> encode(digest(COALESCE(prev_hash,'GENESIS')||'|'||payload_hash,'sha256'),'hex')) AS bad_chain,
  (SELECT count(*) FROM verdict_audit) AS total_audit
"""


async def main(apply: bool) -> None:
    conn = await asyncpg.connect(DSN)
    try:
        tr = conn.transaction()
        await tr.start()
        prev = await conn.fetchval("SELECT chain_hash FROM verdict_audit ORDER BY seq DESC LIMIT 1")
        ids = [r["id"] for r in await conn.fetch(
            "SELECT v.id FROM verification_verdict v "
            "WHERE NOT EXISTS (SELECT 1 FROM verdict_audit a WHERE a.verdict_id = v.id) "
            "ORDER BY v.id")]
        for vid in ids:
            prev = await conn.fetchval(_APPEND_ONE, vid, prev)
        v = await conn.fetchrow(_VERIFY)
        print(f"appended {len(ids)} audit rows")
        print(f"verify -> unaudited={v['unaudited']}  bad_chain={v['bad_chain']}  total_audit={v['total_audit']}")
        clean = v["unaudited"] == 0 and v["bad_chain"] == 0
        if apply and clean:
            await tr.commit()
            print("COMMITTED — chain now covers every verdict, 0 broken links.")
        elif apply:
            await tr.rollback()
            print("ROLLED BACK — verification not clean; refusing to commit a broken chain.")
        else:
            await tr.rollback()
            print("DRY-RUN — rolled back. Re-run with --apply (commits iff clean).")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main(apply="--apply" in sys.argv))
