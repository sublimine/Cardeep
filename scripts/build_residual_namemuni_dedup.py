"""Residual name+municipality dealer-dedup overlay (SAFE straggler collapse).

Problem
-------
After B1 (entity_cluster 'dealer-identity-det-v1') and the deep-link/particular
canonical_dedup overlays, a small residual of the SAME physical dealer survives
split across >1 resolved cdp_code. These are stragglers that share an EXACT
(normalized_name, municipality_code) with a dominant already-merged cluster but
escaped B1's blocking (normalization edges; OEM per-listing fragmentation).

Measured 2026-06-20: 80 name+municipality groups still resolve to >1 dealer in
v_dealer_resolved; 1 of them spans distinct street addresses (possible branch)
and is EXCLUDED. The remaining 79 share one address (or none) -> one location.

Solution (non-destructive, reversible)
--------------------------------------
A new canonical_dedup_run that REPRODUCES the current served overlay
(particular-canonkey-v1) via union-find over its existing member->super edges,
then ADDS edges that fuse each residual group's distinct resolved codes into the
group's dominant representative. Rows are written fully path-compressed (every
canonical -> its final representative), matching build_canonical_dedup.py so the
single-lookup v_dealer_resolved view stays correct.

Safety guards (asserts; fail loudly, never force)
-------------------------------------------------
0. COUNTRY-PROOF: the straggler group key carries country_code (see
   _RESIDUAL_GROUP_SQL + compute_residual_overlay), so two dealers sharing a
   normalized name in the SAME numeric municipality_code but DIFFERENT countries
   can never co-fuse (migrations/0053 lets DE province '28' coexist with ES
   Madrid '28'). A pre-write BLOCKING guard (_assert_no_cross_country_residual)
   is the defense-in-depth mirror of cluster_vehicles._assert_no_cross_country_clusters.
1. Same municipality for every member of a group (blocking key).
2. Same normalized street address OR all-null within a group (no branch merge).
3. Chain names excluded (flexicar/ocasionplus/clicars/carplus/...): they share
   names across distinct physical branches.
4. The pre-existing component set is PRESERVED: every super-canonical from
   particular-canonkey-v1 remains a representative; the only change is residual
   stragglers joining a dominant. assert new_deduped == old_deduped - collapsed.

Reversibility
-------------
Run is written vam_verified=FALSE by default; --commit gates it TRUE only after
all asserts pass. A snapshot of canonical_dedup[_run] is taken first. To roll
back: DELETE FROM canonical_dedup_run WHERE run_id='residual-namemuni-v1'
(CASCADE) -> v_dealer_resolved falls back to particular-canonkey-v1.

Usage
-----
    python scripts/build_residual_namemuni_dedup.py            # dry-run (no write)
    python scripts/build_residual_namemuni_dedup.py --commit   # write + gate VAM
"""
from __future__ import annotations

import asyncio
import os
import pathlib
import re
import sys
import unicodedata
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import asyncpg

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
RUN_ID = os.environ.get("RUN_ID", "residual-namemuni-v1")
BASE_RUN = "particular-canonkey-v1"   # the current served canonical_dedup run we extend
RESOLVER = "residual-namemuni-union-find-v1"
RESOLVER_VERSION = "1.0.0"
SOURCE_CLUSTER_RUN = "dealer-identity-det-v1"

# Chain tokens whose name is shared across distinct physical branches — never
# collapse by name. Mirrors the cross_source_dedup chain-exclusion philosophy.
CHAIN_TOKENS = (
    "flexicar", "ocasionplus", "clicars", "carplus", "clickautos", "hrmotor",
    "csvmotor", "domingoalonso", "movento", "stellantis", "kmcero", "km0",
)


def _norm(text: str | None) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", text.lower())


class UnionFind:
    def __init__(self) -> None:
        self._p: dict[str, str] = {}
        self._r: dict[str, int] = {}

    def _ensure(self, x: str) -> None:
        if x not in self._p:
            self._p[x] = x
            self._r[x] = 0

    def find(self, x: str) -> str:
        self._ensure(x)
        root = x
        while self._p[root] != root:
            root = self._p[root]
        node = x
        while node != root:
            self._p[node], node = root, self._p[node]
        return root

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self._r[ra] < self._r[rb]:
            ra, rb = rb, ra
        self._p[rb] = ra
        if self._r[ra] == self._r[rb]:
            self._r[ra] += 1

    def components(self) -> dict[str, list[str]]:
        g: dict[str, list[str]] = defaultdict(list)
        for n in self._p:
            g[self.find(n)].append(n)
        return dict(g)


# ---------------------------------------------------------------------------
# Residual name+muni+country group SQL + merge core (module scope)
# ---------------------------------------------------------------------------
# Extracted to module scope so the country-isolation golden
# (tests/test_country_isolation_overlay_dedup.py) drives the REAL grouping +
# classification the build runs, not a copy — mirrors build_canonical_dedup's
# _DEEPLINK_CANON_SQL + _build_deeplink_merge_graph. build() loads rows via
# asyncpg; the golden loads the same rows via psycopg2 inside a rolled-back
# transaction — both feed compute_residual_overlay, the single source of truth
# for which codes fuse.
#
# COUNTRY-PROOF: country_code is part of the straggler group key. The CTE `base`
# carries e.country_code (cc); `g` GROUPS BY nm, mc, cc and the join re-binds cc,
# so two dealers sharing a normalized name in the SAME numeric municipality_code
# but DIFFERENT countries can NEVER share a group — the cross-border false-merge
# vector (migrations/0053 lets DE province '28' coexist with ES Madrid '28').
# entity.country_code is CHAR(2) NOT NULL DEFAULT 'ES' (migrations/0052), so for a
# single-country census cc is a constant key element and the grouping — therefore
# every fusion — is BYTE-IDENTICAL to the pre-country behaviour.
_RESIDUAL_GROUP_SQL = """
    WITH base AS (
        SELECT lower(regexp_replace(coalesce(e.trade_name,e.legal_name),'[^a-zA-Z0-9]','','g')) nm,
               e.municipality_code mc, e.country_code cc, e.cdp_code, e.entity_ulid, e.address,
               COALESCE(vdr.resolved_cdp_code, e.cdp_code) rcode
        FROM entity e
        LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid = e.entity_ulid
        WHERE e.kind NOT IN ('particular') AND e.status='active'
          AND coalesce(e.trade_name,e.legal_name) IS NOT NULL
          AND e.municipality_code IS NOT NULL ),
    g AS (SELECT nm, mc, cc FROM base GROUP BY nm, mc, cc HAVING count(DISTINCT rcode) > 1)
    SELECT b.nm, b.mc, b.cc, b.cdp_code, b.rcode, b.address
    FROM base b JOIN g ON g.nm=b.nm AND g.mc=b.mc AND g.cc=b.cc
    ORDER BY b.nm, b.mc, b.cc
"""


def compute_residual_overlay(grp_rows, base_rows, avail):
    """Pure merge core (no I/O): classify residual (name, muni, country) groups
    and fold the SAFE ones into the BASE overlay via union-find. Returns the data
    build() needs to assert + persist. Single source of truth for which codes
    fuse — drives both build() and the country-isolation golden.

    grp_rows : rows from _RESIDUAL_GROUP_SQL (nm, mc, cc, cdp_code, rcode, address).
    base_rows: canonical_dedup rows for BASE_RUN (canonical_cdp_code, super_canonical_cdp_code).
    avail    : {resolved_cdp_code: available_vehicle_count} for representative pick.

    Returns a dict with: groups, new_edges, comps, out, safe_codes,
    base_super_map, code_country, multi_base, stats.
    """
    # base_super: canonical -> stored super in BASE_RUN. base_members: super ->
    # the full set of base members it aggregates. Used by the bystander-drag
    # refinement (root fix for the cross-dealer over-merge the safety assert caught).
    base_super_run = {r["canonical_cdp_code"]: r["super_canonical_cdp_code"] for r in base_rows}
    base_members: dict[str, set[str]] = defaultdict(set)
    for r in base_rows:
        base_members[r["super_canonical_cdp_code"]].add(r["canonical_cdp_code"])
        base_members[r["super_canonical_cdp_code"]].add(r["super_canonical_cdp_code"])

    def _resolved_base_super(code: str) -> str:
        """Stored base super-canonical for a resolved code, else the code itself."""
        return base_super_run.get(code, code)

    # Group members by (nm, mc, cc) — country IS part of the key (COUNTRY-PROOF):
    # a straggler group never spans a border. code_country maps every group code
    # (cdp_code + its rcode) to its country, for the blocking guard below.
    groups: dict[tuple[str, str, str], list] = defaultdict(list)
    code_country: dict[str, str] = {}
    for r in grp_rows:
        groups[(r["nm"], r["mc"], r["cc"])].append(r)
        code_country[r["cdp_code"]] = r["cc"]
        code_country[r["rcode"]] = r["cc"]

    # A base super-canonical the group touches that carries a BYSTANDER member
    # outside the group's own {cdp_code ∪ rcode} would be collaterally dragged by
    # the name-key edge -> ambiguous cross-dealer fusion. Such groups are excluded.
    def _is_eligible(members) -> bool:
        rcodes = {m["rcode"] for m in members}
        own_codes = {m["cdp_code"] for m in members} | rcodes
        touched_supers = {_resolved_base_super(rc) for rc in rcodes}
        for sup in touched_supers:
            if base_members.get(sup, {sup}) - own_codes:
                return False
        return True

    new_edges: list[tuple[str, str]] = []   # (resolved_code_i, representative)
    safe_groups = excluded_chain = excluded_addr = excluded_ambiguous = 0
    collapsed_codes = 0
    for (nm, mc, cc), members in groups.items():
        if any(tok in nm for tok in CHAIN_TOKENS):
            excluded_chain += 1
            continue
        addrs = {_norm(m["address"]) for m in members if m["address"]}
        if len(addrs) > 1:                      # distinct street addresses -> possible branches
            excluded_addr += 1
            continue
        rcodes = sorted({m["rcode"] for m in members})
        if len(rcodes) < 2:
            continue
        if not _is_eligible(members):           # bystander drag -> ambiguous cross-dealer fusion
            excluded_ambiguous += 1
            print(f"  EXCLUDED ambiguous group nm={nm!r} mc={mc!r} cc={cc!r} rcodes={rcodes} "
                  f"(name-key edge would fuse >1 distinct base dealer + drag a bystander)")
            continue
        # representative = resolved code with most available vehicles; tie-break cdp asc
        rep = min(rcodes, key=lambda c: (-avail.get(c, 0), c))
        for ri in rcodes:
            if ri != rep:
                new_edges.append((ri, rep))
                collapsed_codes += 1
        safe_groups += 1

    # Union-find over base edges + residual edges
    uf = UnionFind()
    for r in base_rows:
        uf.union(r["canonical_cdp_code"], r["super_canonical_cdp_code"])
    for a, b in new_edges:
        uf.union(a, b)
    comps = {root: m for root, m in uf.components().items() if len(m) >= 2}

    # PRESERVE base representatives: an existing component keeps its stored super;
    # a newly-fused component has exactly one base super present (the dominant's).
    out: list[tuple[str, str, int, bool]] = []   # (canon, super, comp_size, is_rep)
    multi_base = 0
    for _, members in comps.items():
        present = {base_super_run[m] for m in members if m in base_super_run}
        if len(present) == 1:
            rep = next(iter(present))
        elif len(present) == 0:
            rep = min(members, key=lambda c: (-avail.get(c, 0), c))
        else:
            multi_base += 1                       # would fuse two base components — flagged below
            rep = min(present, key=lambda c: (-avail.get(c, 0), c))
        for m in members:
            out.append((m, rep, len(members), m == rep))

    # safe_codes: codes inside SAFE residual groups (SAME eligibility filters as
    # above). Whitelists the only canonicals allowed to change representative.
    safe_codes: set[str] = set()
    for (nm, mc, cc), members in groups.items():
        if any(tok in nm for tok in CHAIN_TOKENS):
            continue
        if len({_norm(m["address"]) for m in members if m["address"]}) > 1:
            continue
        if not _is_eligible(members):
            continue
        for m in members:
            safe_codes.add(m["cdp_code"])
            safe_codes.add(m["rcode"])

    return {
        "groups": dict(groups),
        "new_edges": new_edges,
        "comps": comps,
        "out": out,
        "safe_codes": safe_codes,
        "base_super_map": base_super_run,
        "code_country": code_country,
        "multi_base": multi_base,
        "stats": {
            "safe_groups": safe_groups,
            "excluded_chain": excluded_chain,
            "excluded_addr": excluded_addr,
            "excluded_ambiguous": excluded_ambiguous,
            "collapsed_codes": collapsed_codes,
        },
    }


def _assert_no_cross_country_residual(out, code_country) -> None:
    """BLOCKING country-isolation guard — runs BEFORE the write/commit.

    The PRIMARY prevention is mechanical and lives in the group key:
    _RESIDUAL_GROUP_SQL / compute_residual_overlay key every straggler group by
    country_code, so a cross-border fusion edge is never generated. This guard is
    the defense-in-depth mirror of cluster_vehicles._assert_no_cross_country_clusters:
    it recomputes, per residual super-canonical, the set of distinct member
    country_codes and RAISES if any fused component spans >1 country — aborting the
    run (rollback; nothing is written) so a cross-border false-merge can never be
    written or served. Codes with no known country (base-only nodes) are skipped.
    """
    comp_countries: dict[str, set[str]] = defaultdict(set)
    for (canon, super_, _size, _is_rep) in out:
        for code in (canon, super_):          # count BOTH endpoints of the fusion
            cc = code_country.get(code)
            if cc:
                comp_countries[super_].add(cc)
    offenders = {
        super_: sorted(ccs)
        for super_, ccs in comp_countries.items()
        if len(ccs) > 1
    }
    if offenders:
        sample = list(offenders.items())[:5]
        raise RuntimeError(
            f"COUNTRY-PROOF VIOLATION: {len(offenders)} residual super-canonical(s) span "
            f">1 country_code — refusing to write/serve a cross-border false-merge. "
            f"sample={sample}"
        )


async def build(conn: asyncpg.Connection, commit: bool) -> None:
    # ── 1. Existing served overlay edges (member -> super) from BASE_RUN ──────
    base_rows = await conn.fetch(
        "SELECT canonical_cdp_code, super_canonical_cdp_code FROM canonical_dedup WHERE run_id=$1",
        BASE_RUN,
    )
    if not base_rows:
        print(f"[FATAL] base run {BASE_RUN} has no rows; aborting.")
        sys.exit(1)
    print(f"[residual-dedup] base={BASE_RUN} rows={len(base_rows)}")

    # ── 2. Residual name+muni+country groups still split across >1 resolved code
    # Grouping SQL + classification/union-find live at module scope
    # (_RESIDUAL_GROUP_SQL + compute_residual_overlay) so the country-isolation
    # golden drives the EXACT decision logic this build runs, not a copy.
    grp_rows = await conn.fetch(_RESIDUAL_GROUP_SQL)

    # available-count per resolved code (for deterministic representative pick)
    avail = {
        r["rcode"]: r["c"]
        for r in await conn.fetch(
            """
            SELECT COALESCE(vdr.resolved_cdp_code, e.cdp_code) rcode, count(*) c
            FROM vehicle v JOIN entity e ON e.entity_ulid=v.entity_ulid
            LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid=e.entity_ulid
            WHERE v.status='available' GROUP BY 1
            """
        )
    }

    # ── 3. Classify groups + fold into base overlay (pure core) ──────────────
    res = compute_residual_overlay(grp_rows, base_rows, avail)
    groups = res["groups"]
    new_edges = res["new_edges"]
    comps = res["comps"]
    out = res["out"]
    safe_codes = res["safe_codes"]
    base_super_map = res["base_super_map"]
    code_country = res["code_country"]
    multi_base = res["multi_base"]
    safe_groups = res["stats"]["safe_groups"]
    excluded_chain = res["stats"]["excluded_chain"]
    excluded_addr = res["stats"]["excluded_addr"]
    excluded_ambiguous = res["stats"]["excluded_ambiguous"]
    collapsed_codes = res["stats"]["collapsed_codes"]

    # ── 3b. BLOCKING country-isolation guard (pre-write, COUNTRY-PROOF) ───────
    # Aborts the run (rollback — nothing written) before the write transaction if
    # any fused residual super-canonical spans >1 country. Mirror of
    # cluster_vehicles._assert_no_cross_country_clusters; defense-in-depth behind
    # the country_code group key.
    _assert_no_cross_country_residual(out, code_country)

    print(f"  residual groups total={len(groups)}  SAFE={safe_groups}  "
          f"excl_chain={excluded_chain}  excl_addr={excluded_addr}  "
          f"excl_ambiguous={excluded_ambiguous}")
    print(f"  residual edges (codes collapsed)={collapsed_codes}")

    # ── 5. Safety asserts vs the base overlay ────────────────────────────────
    m2rep = {row[0]: row[1] for row in out}              # new: member -> final rep

    def base_rep(c: str) -> str:
        return base_super_map.get(c, c)                   # stored base super, else self

    def new_rep(c: str) -> str:
        return m2rep.get(c, c)

    # Invariant 1: no base representative is re-absorbed (no existing merge undone),
    # unless it is a residual resolved code we intentionally fused.
    intentional = {e[0] for e in new_edges}
    base_reps = {r["super_canonical_cdp_code"] for r in base_rows}
    broken = [rp for rp in base_reps if new_rep(rp) != rp and rp not in intentional]

    # Invariant 2: the ONLY canonicals whose representative changed are inside the
    # SAFE residual groups (safe_codes uses the same eligibility filters as step 3).
    all_nodes = {c for row in out for c in (row[0], row[1])} | set(base_super_map)
    changed = [c for c in all_nodes if base_rep(c) != new_rep(c)]
    collateral = [c for c in changed if c not in safe_codes]

    # Served dealer count (full universe) — the metric that matters.
    served_before = await conn.fetchval(
        """SELECT count(DISTINCT COALESCE(vdr.resolved_cdp_code, e.cdp_code))
           FROM entity e LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid=e.entity_ulid
           WHERE e.status='active' AND e.kind<>'particular'""")
    served_after = served_before - collapsed_codes
    # VAM 2nd orthogonal path for served_after (the mig 0070 proof): recount the served universe with
    # the overlay applied (new_rep), INDEPENDENT of collapsed_codes. Arithmetic path = served_before -
    # collapsed_codes; structural path = distinct reps after mapping every served code through the
    # overlay. If they disagree the overlay is inconsistent and the run must NOT be served.
    _served_codes = [r["rcode"] for r in await conn.fetch(
        """SELECT DISTINCT COALESCE(vdr.resolved_cdp_code, e.cdp_code) AS rcode
           FROM entity e LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid=e.entity_ulid
           WHERE e.status='active' AND e.kind<>'particular'""")]
    served_after_recount = len({new_rep(c) for c in _served_codes})

    failures = []
    if served_after != served_after_recount:
        failures.append(f"served_after path disagreement: arithmetic={served_after} vs "
                        f"overlay-recount={served_after_recount} (overlay inconsistent — not serving)")
    if broken:
        failures.append(f"{len(broken)} base representatives re-absorbed unexpectedly")
    if collateral:
        failures.append(f"{len(collateral)} canonicals changed rep OUTSIDE safe groups (collateral)")
    if multi_base:
        print(f"  NOTE: {multi_base} residual group(s) fuse TWO pre-existing base dealers "
              f"(both already had inventory clusters) — review before commit")

    print(f"\n  served dealers (active, non-particular): before={served_before} "
          f"after={served_after}  delta=-{collapsed_codes}")
    print(f"  base_rows={len(base_rows)} final_rows={len(out)} "
          f"final_reps={sum(1 for r in out if r[3])}  changed_nodes={len(changed)}")

    if failures:
        print("\n  [SAFETY ASSERT FAILED] - not writing:")
        for f in failures:
            print(f"    - {f}")
        sys.exit(1)
    print("  [OK] safety asserts passed (no broken merges, no collateral)")

    if not commit:
        print("\n  DRY-RUN (no write). Re-run with --commit to persist + gate VAM.")
        return

    # ── 6. Snapshot + write in a single transaction ──────────────────────────
    cdp_to_ulid = {
        r["cdp_code"]: r["entity_ulid"]
        for r in await conn.fetch(
            "SELECT cdp_code, entity_ulid FROM entity WHERE cdp_code = ANY($1)",
            list({c for row in out for c in (row[0], row[1])}),
        )
    }
    missing = [c for row in out for c in (row[0], row[1]) if c not in cdp_to_ulid]
    if missing:
        print(f"  [FATAL] {len(set(missing))} cdp_codes missing from entity; abort.")
        sys.exit(1)

    async with conn.transaction():
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS canonical_dedup_backup_20260620 AS "
            "SELECT * FROM canonical_dedup WHERE FALSE")
        await conn.execute("TRUNCATE canonical_dedup_backup_20260620")
        await conn.execute(
            "INSERT INTO canonical_dedup_backup_20260620 SELECT * FROM canonical_dedup")
        await conn.execute("DELETE FROM canonical_dedup WHERE run_id=$1", RUN_ID)
        await conn.execute("DELETE FROM canonical_dedup_run WHERE run_id=$1", RUN_ID)
        # VAM seal (mig 0070): record the TRUSTWORTHY verdict for served_after from the two orthogonal
        # paths asserted-equal above (arithmetic served_before-collapsed vs structural overlay-recount)
        # and link vam_verdict_id — exactly like gate_particular_dedup. The two agreeing values give
        # quorum_n=2, and two distinct families/origins give family_n=2/origin_n=2, satisfying
        # chk_trustworthy_needs_quorum and the 0070 trigger. (Real two-path quorum, not a literal [N,N].)
        vam_vid = await conn.fetchval(
            """INSERT INTO verification_verdict
                 (subject_type, subject_key, claim, verdict, primary_value, primary_path,
                  independent_values, verifier_paths, claim_kind, tolerance, method_version, evidence)
               VALUES ('b1_dedup', $1,
                       'residual name+muni overlay — served deduped identities (active, non-particular)',
                       'TRUSTWORTHY', $2, 'served_before - collapsed_codes', $3::jsonb, $4::jsonb,
                       'count', 0, 'residual-namemuni-v1',
                       jsonb_build_object('served_before',$5::int,'collapsed_codes',$6::int,
                                          'safe_groups',$7::int))
               RETURNING id""",
            RUN_ID, served_after,
            f"[{served_after}, {served_after_recount}]",
            '[{"family":"arithmetic","origin":"served_minus_collapsed"},'
            '{"family":"structural","origin":"overlay_recount"}]',
            served_before, collapsed_codes, safe_groups)
        await conn.execute(
            """INSERT INTO canonical_dedup_run
               (run_id, resolver, resolver_version, source_cluster_run, anti_hub_k,
                n_canonicals_in, n_super_canonicals, n_merged, deduped_count, vam_verified,
                vam_verdict_id, notes)
               VALUES ($1,$2,$3,$4,3,$5,$6,$7,$8,TRUE,$9,$10)""",
            RUN_ID, RESOLVER, RESOLVER_VERSION, SOURCE_CLUSTER_RUN,
            len(safe_codes), len(comps), len(out) - len(comps), served_after, vam_vid,
            f'{{"basis":"{BASE_RUN}+residual-namemuni","safe_groups":{safe_groups},'
            f'"collapsed_codes":{collapsed_codes},"excl_chain":{excluded_chain},'
            f'"excl_addr":{excluded_addr}}}',
        )
        await conn.executemany(
            """INSERT INTO canonical_dedup
               (run_id, canonical_cdp_code, canonical_entity_ulid,
                super_canonical_cdp_code, super_canonical_ulid,
                component_size, is_representative)
               VALUES ($1,$2,$3,$4,$5,$6,$7)""",
            [(RUN_ID, r[0], cdp_to_ulid[r[0]], r[1], cdp_to_ulid[r[1]], r[2], r[3]) for r in out],
        )
    print(f"\n  [WRITTEN] run_id={RUN_ID} vam_verified=TRUE rows={len(out)} "
          f"(snapshot: canonical_dedup_backup_20260620)")


async def main() -> None:
    commit = "--commit" in sys.argv
    conn = await asyncpg.connect(DSN)
    try:
        await build(conn, commit)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
