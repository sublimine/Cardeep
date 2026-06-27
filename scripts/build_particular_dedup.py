"""Build an INERT canonical_dedup run that adds the particular province-split merges (audit P2
B-particular-province-split; see docs/architecture/11-IDENTITY-RESOLUTION-AUTHORITY.md "Update").

A particular seller listing in N provinces gets N cdp_codes that share the 8-char hash suffix (the hash
excludes province) but differ in the province prefix. canonical_key (= the literal pre-image
'particular:{platform}:{seller_id}', collision-free, backfilled + re-hash-gated this session) is the
DEFINITIVE same-seller discriminator the original deferral lacked.

This produces a NEW canonical_dedup_run that is a SUPERSET of the served run:
  1. copies every row of the served run verbatim (dealers + the 139 deep_link particular merges + the
     2 cross-kind groups stay byte-identical), then
  2. adds, for each (canonical_key, country_code) shared by >1 particular, merge rows mapping the
     still-unmapped members to a representative, by case:
       A. no member mapped yet      -> representative = MOST-AVAILABLE member (tie-break cdp asc)
       B. partially mapped to ONE   -> reuse that existing super-canonical (consistency)
          particular super
       C. mapped to a dealer super  -> SKIP the whole group (preserve current; flagged for per-merge
          or to multiple supers       review — these are the 2 cross-kind cases)

COUNTRY-PROOF: the split-group key carries country_code (see _PARTICULAR_GROUP_SQL), so a
canonical_key that ever appeared under two countries can never fuse particulares across a border
(latent today, same defect as the dealer overlays — migrations/0053 lets a 2nd country reuse the ES
numeric code space). A pre-write BLOCKING guard (_assert_no_cross_country_particular) is the
defense-in-depth mirror of cluster_vehicles._assert_no_cross_country_clusters.

The new run is vam_verified=FALSE -> v_dealer_resolved (which reads only the latest vam_verified=TRUE
run) is UNCHANGED. Nothing served moves until a deliberate gate after E2E regression. Fully reversible
(DELETE the run). Verification: every added pair shares one canonical_key + one country; dealer rows untouched.

Run:  python scripts/build_particular_dedup.py             # dry-run (case counts, no writes)
      python scripts/build_particular_dedup.py --apply --run-id particular-canonkey-v1
"""
from __future__ import annotations

import asyncio
import os
import sys
from collections import defaultdict
from pathlib import Path

import asyncpg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DSN = os.environ.get("CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep")
DEFAULT_NEW_RUN = "particular-canonkey-v1"


# ---------------------------------------------------------------------------
# Particular canonical_key (+country) split-group SQL + case core (module scope)
# ---------------------------------------------------------------------------
# Extracted to module scope so the country-isolation golden
# (tests/test_country_isolation_overlay_dedup.py) drives the REAL grouping + case
# classification the build runs, not a copy — mirrors build_canonical_dedup's
# _DEEPLINK_CANON_SQL + _build_deeplink_merge_graph.
#
# COUNTRY-PROOF: country_code is part of the split-group key. A particular seller
# split across N PROVINCES of one country shares its canonical_key (the hash
# excludes province) and ONE country_code, so the legitimate province-split merge
# is untouched; but two particulares in DIFFERENT countries that happened to share
# a canonical_key land in DIFFERENT groups and never fuse — the cross-border
# false-merge vector. entity.country_code is CHAR(2) NOT NULL DEFAULT 'ES'
# (migrations/0052), so for a single-country census country_code is a constant key
# element and the grouping is BYTE-IDENTICAL to the pre-country behaviour.
_PARTICULAR_GROUP_SQL = """
    SELECT canonical_key,
           country_code,
           array_agg(cdp_code ORDER BY cdp_code)     AS cdps,
           array_agg(entity_ulid ORDER BY cdp_code)  AS ulids
      FROM entity
     WHERE kind='particular' AND canonical_key IS NOT NULL
     GROUP BY canonical_key, country_code HAVING count(*) > 1
"""


def compute_particular_overlay(grp_rows, mapped, avail):
    """Pure core (no I/O): classify each (canonical_key, country) split-group into
    Case A/B/C and return the new merge pairs. Single source of truth for which
    particulares fuse — drives both build() and the country-isolation golden.

    grp_rows: rows from _PARTICULAR_GROUP_SQL (canonical_key, country_code, cdps[], ulids[]).
    mapped  : {canonical_cdp_code: (super_cdp, super_ulid, super_kind)} from the served run.
    avail   : {canonical_cdp_code: available_vehicle_count} for representative pick.

    Returns (new_pairs, case_a, case_b, case_c, skipped_groups, code_country) where
    each new_pair is (canon_cdp, canon_ulid, super_cdp, super_ulid, is_rep, key, size).
    """
    case_a = case_b = case_c = 0
    new_pairs: list[tuple] = []
    skipped_groups: list[str] = []
    code_country: dict[str, str] = {}
    for g in grp_rows:
        cdps, ulids, key = g["cdps"], g["ulids"], g["canonical_key"]
        country = g["country_code"]
        for c in cdps:
            code_country[c] = country
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
            # Case A: fully unmapped -> representative = MOST-AVAILABLE member (tie-break cdp asc),
            # consistent with the rest of the pipeline.
            case_a += 1
            rep_cdp, rep_ulid = min(members, key=lambda m: (-avail.get(m[0], 0), m[0]))
        size = len(members)
        for c, u in members:
            if c in mapped:
                continue                                       # never override an existing mapping
            new_pairs.append((c, u, rep_cdp, rep_ulid, c == rep_cdp, key, size))
    return new_pairs, case_a, case_b, case_c, skipped_groups, code_country


def _assert_no_cross_country_particular(new_pairs, code_country) -> None:
    """BLOCKING country-isolation guard — runs BEFORE the write/commit.

    The PRIMARY prevention is mechanical and lives in the group key:
    _PARTICULAR_GROUP_SQL keys every split-group by country_code, so a cross-border
    merge pair is never generated. This guard is the defense-in-depth mirror of
    cluster_vehicles._assert_no_cross_country_clusters: it recomputes, per
    particular super-canonical, the set of distinct member country_codes and RAISES
    if any fused group spans >1 country — aborting the run (rollback; nothing
    written) so a cross-border false-merge can never be written or served.
    """
    comp_countries: dict[str, set[str]] = defaultdict(set)
    for (c, _u, sc, _su, _is_rep, _key, _size) in new_pairs:
        for code in (c, sc):                  # count BOTH endpoints of the fusion
            cc = code_country.get(code)
            if cc:
                comp_countries[sc].add(cc)
    offenders = {
        sc: sorted(ccs)
        for sc, ccs in comp_countries.items()
        if len(ccs) > 1
    }
    if offenders:
        sample = list(offenders.items())[:5]
        raise RuntimeError(
            f"COUNTRY-PROOF VIOLATION: {len(offenders)} particular super-canonical(s) span "
            f">1 country_code — refusing to write/serve a cross-border false-merge. "
            f"sample={sample}"
        )


async def build(conn: asyncpg.Connection, apply: bool, new_run_id: str) -> None:
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

    # Particular (canonical_key, country) groups (>1 entity = province-split). Verified same-seller.
    grp_rows = await conn.fetch(_PARTICULAR_GROUP_SQL)

    # Available-vehicle count per canonical, for richest-member representative selection.
    avail_rows = await conn.fetch(
        """SELECT COALESCE(vc.canonical_cdp_code, e.cdp_code) AS canon, count(*) AS c
             FROM vehicle v
             JOIN entity e ON e.entity_ulid = v.entity_ulid
             LEFT JOIN v_canonical vc ON vc.entity_ulid = v.entity_ulid
            WHERE v.status='available'
            GROUP BY 1""")
    avail = {r["canon"]: r["c"] for r in avail_rows}

    new_pairs, case_a, case_b, case_c, skipped_groups, code_country = compute_particular_overlay(
        grp_rows, mapped, avail)

    # BLOCKING country-isolation guard (pre-write): abort before any write if a
    # particular merge pair would fuse two countries. Mirror of
    # cluster_vehicles._assert_no_cross_country_clusters.
    _assert_no_cross_country_particular(new_pairs, code_country)

    print(f"served run: {served_run}  ({len(served_rows)} rows copied)")
    print(f"particular (canonical_key, country) groups (split): {len(grp_rows)}")
    print(f"  case A (new merge, rep=most-avail):  {case_a}")
    print(f"  case B (reuse existing particular):  {case_b}")
    print(f"  case C (cross-kind/conflict, SKIP):  {case_c}  -> {skipped_groups[:5]}{'...' if case_c>5 else ''}")
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
                  jsonb_build_object('basis','copies '||$3||' + particular canonical_key+country merges',
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
        # 2) add the particular canonical_key+country merges
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


async def main() -> None:
    args = sys.argv[1:]
    run_id = DEFAULT_NEW_RUN
    if "--run-id" in args:
        run_id = args[args.index("--run-id") + 1]
    conn = await asyncpg.connect(DSN)
    try:
        await build(conn, apply="--apply" in args, new_run_id=run_id)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
