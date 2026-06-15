"""Build an INERT canonical_dedup run that adds the particular province-split merges (audit P2
B-particular-province-split; see docs/architecture/11-IDENTITY-RESOLUTION-AUTHORITY.md "Update").

A particular seller listing in N provinces gets N cdp_codes that share the 8-char hash suffix (the hash
excludes province) but differ in the province prefix. canonical_key (= the literal pre-image
'particular:{platform}:{seller_id}', collision-free, backfilled + re-hash-gated this session) is the
DEFINITIVE same-seller discriminator the original deferral lacked.

This produces a NEW canonical_dedup_run that is a SUPERSET of the served run:
  1. copies every row of the served run verbatim (dealers + the 139 deep_link particular merges + the
     2 cross-kind groups stay byte-identical), then
  2. adds, for each canonical_key shared by >1 particular, merge rows mapping the still-unmapped members
     to a representative, by case:
       A. no member mapped yet      -> representative = MIN(cdp_code) in the group (deterministic)
       B. partially mapped to ONE   -> reuse that existing super-canonical (consistency)
          particular super
       C. mapped to a dealer super  -> SKIP the whole group (preserve current; flagged for per-merge
          or to multiple supers       review — these are the 2 cross-kind cases)

The new run is vam_verified=FALSE -> v_dealer_resolved (which reads only the latest vam_verified=TRUE
run) is UNCHANGED. Nothing served moves until a deliberate gate after E2E regression. Fully reversible
(DELETE the run). Verification: every added pair shares one canonical_key; dealer rows untouched.

Run:  python scripts/build_particular_dedup.py             # dry-run (case counts, no writes)
      python scripts/build_particular_dedup.py --apply --run-id particular-canonkey-v1
"""
from __future__ import annotations

import asyncio
import sys
from collections import defaultdict
from pathlib import Path

import asyncpg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
DEFAULT_NEW_RUN = "particular-canonkey-v1"


async def build(apply: bool, new_run_id: str) -> None:
    conn = await asyncpg.connect(DSN)
    try:
        served = await conn.fetchrow(
            "SELECT run_id, source_cluster_run FROM canonical_dedup_run "
            "WHERE vam_verified ORDER BY run_id DESC LIMIT 1")
        if served is None:
            print("no vam_verified canonical_dedup_run — abort")
            return
        served_run = served["run_id"]

        # Served map: canonical_cdp_code -> (super_cdp, super_ulid, super_kind)
        served_rows = await conn.fetch(
            """SELECT cd.canonical_cdp_code, cd.super_canonical_cdp_code, cd.super_canonical_ulid,
                      se.kind::text AS super_kind
                 FROM canonical_dedup cd
                 JOIN entity se ON se.entity_ulid = cd.super_canonical_ulid
                WHERE cd.run_id = $1""", served_run)
        mapped = {r["canonical_cdp_code"]: (r["super_canonical_cdp_code"],
                                            r["super_canonical_ulid"], r["super_kind"])
                  for r in served_rows}

        # Particular canonical_key groups (>1 entity = province-split). Verified same-seller.
        grp_rows = await conn.fetch(
            """SELECT canonical_key,
                      array_agg(cdp_code ORDER BY cdp_code)     AS cdps,
                      array_agg(entity_ulid ORDER BY cdp_code)  AS ulids
                 FROM entity
                WHERE kind='particular' AND canonical_key IS NOT NULL
                GROUP BY canonical_key HAVING count(*) > 1""")

        case_a = case_b = case_c = 0
        new_pairs: list[tuple] = []        # (canon_cdp, canon_ulid, super_cdp, super_ulid, is_rep, key, size)
        skipped_groups: list[str] = []
        for g in grp_rows:
            cdps, ulids, key = g["cdps"], g["ulids"], g["canonical_key"]
            members = list(zip(cdps, ulids))                       # aligned (same ORDER BY cdp_code)
            existing = {mapped[c] for c, _ in members if c in mapped}
            super_kinds = {e[2] for e in existing}
            if len(existing) > 1 or (super_kinds and super_kinds != {"particular"}):
                # Case C: cross-kind super, or members already split across >1 super -> preserve, skip.
                case_c += 1
                skipped_groups.append(key)
                continue
            if existing:
                # Case B: partially merged to ONE particular super -> reuse it.
                case_b += 1
                rep_cdp, rep_ulid, _ = next(iter(existing))
            else:
                # Case A: fully unmapped -> representative = MIN(cdp_code) (members sorted by cdp_code).
                case_a += 1
                rep_cdp, rep_ulid = members[0]
            size = len(members)
            for c, u in members:
                if c in mapped:
                    continue                                       # never override an existing mapping
                new_pairs.append((c, u, rep_cdp, rep_ulid, c == rep_cdp, key, size))

        print(f"served run: {served_run}  ({len(served_rows)} rows copied)")
        print(f"particular canonical_key groups (split): {len(grp_rows)}")
        print(f"  case A (new merge, rep=min cdp):      {case_a}")
        print(f"  case B (reuse existing particular):   {case_b}")
        print(f"  case C (cross-kind/conflict, SKIP):   {case_c}  -> {skipped_groups[:5]}{'...' if case_c>5 else ''}")
        print(f"new merge rows to add: {len(new_pairs)}")

        if not apply:
            print("\nDRY-RUN — no writes.")
            return

        async with conn.transaction():
            await conn.execute(
                """INSERT INTO canonical_dedup_run
                     (run_id, resolver, resolver_version, source_cluster_run, anti_hub_k,
                      n_canonicals_in, n_super_canonicals, n_merged, deduped_count, vam_verified, notes)
                   VALUES ($1,'deep-link+canonkey-v1','1.0.0',$2,3,NULL,NULL,NULL,NULL,FALSE,
                      jsonb_build_object('basis','copies '||$3||' + particular canonical_key merges',
                                         'case_a',$4::int,'case_b',$5::int,'case_c_skipped',$6::int,
                                         'added_rows',$7::int))""",
                new_run_id, served["source_cluster_run"], served_run, case_a, case_b, case_c, len(new_pairs))
            # 1) copy served rows verbatim
            await conn.execute(
                """INSERT INTO canonical_dedup
                     (run_id, canonical_cdp_code, canonical_entity_ulid, super_canonical_cdp_code,
                      super_canonical_ulid, component_size, is_representative, evidence_deep_link)
                   SELECT $1, canonical_cdp_code, canonical_entity_ulid, super_canonical_cdp_code,
                          super_canonical_ulid, component_size, is_representative, evidence_deep_link
                     FROM canonical_dedup WHERE run_id = $2""",
                new_run_id, served_run)
            # 2) add the particular canonical_key merges
            await conn.executemany(
                """INSERT INTO canonical_dedup
                     (run_id, canonical_cdp_code, canonical_entity_ulid, super_canonical_cdp_code,
                      super_canonical_ulid, component_size, is_representative, evidence_deep_link)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
                   ON CONFLICT (run_id, canonical_cdp_code) DO NOTHING""",
                [(new_run_id, c, u, sc, su, size, is_rep, f"canonical_key:{key}")
                 for (c, u, sc, su, is_rep, key, size) in new_pairs])
            n_rows = await conn.fetchval(
                "SELECT count(*) FROM canonical_dedup WHERE run_id=$1", new_run_id)
        print(f"\nAPPLIED. new run '{new_run_id}' has {n_rows} rows (vam_verified=FALSE, INERT).")
    finally:
        await conn.close()


if __name__ == "__main__":
    args = sys.argv[1:]
    run_id = DEFAULT_NEW_RUN
    if "--run-id" in args:
        run_id = args[args.index("--run-id") + 1]
    asyncio.run(build(apply="--apply" in args, new_run_id=run_id))
