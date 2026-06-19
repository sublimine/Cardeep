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

    # ── 2. Residual name+muni groups still split across >1 resolved code ──────
    grp_rows = await conn.fetch(
        """
        WITH base AS (
            SELECT lower(regexp_replace(coalesce(e.trade_name,e.legal_name),'[^a-zA-Z0-9]','','g')) nm,
                   e.municipality_code mc, e.cdp_code, e.entity_ulid, e.address,
                   COALESCE(vdr.resolved_cdp_code, e.cdp_code) rcode
            FROM entity e
            LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid = e.entity_ulid
            WHERE e.kind NOT IN ('particular') AND e.status='active'
              AND coalesce(e.trade_name,e.legal_name) IS NOT NULL
              AND e.municipality_code IS NOT NULL ),
        g AS (SELECT nm, mc FROM base GROUP BY nm, mc HAVING count(DISTINCT rcode) > 1)
        SELECT b.nm, b.mc, b.cdp_code, b.rcode, b.address
        FROM base b JOIN g ON g.nm=b.nm AND g.mc=b.mc
        ORDER BY b.nm, b.mc
        """
    )
    groups: dict[tuple[str, str], list[asyncpg.Record]] = defaultdict(list)
    for r in grp_rows:
        groups[(r["nm"], r["mc"])].append(r)

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

    # ── 3. Classify groups; build residual edges for SAFE ones only ──────────
    new_edges: list[tuple[str, str]] = []   # (resolved_code_i, representative)
    safe_groups = excluded_chain = excluded_addr = 0
    collapsed_codes = 0
    for (nm, mc), members in groups.items():
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
        # representative = resolved code with most available vehicles; tie-break cdp asc
        rep = min(rcodes, key=lambda c: (-avail.get(c, 0), c))
        for ri in rcodes:
            if ri != rep:
                new_edges.append((ri, rep))
                collapsed_codes += 1
        safe_groups += 1

    print(f"  residual groups total={len(groups)}  SAFE={safe_groups}  "
          f"excl_chain={excluded_chain}  excl_addr={excluded_addr}")
    print(f"  residual edges (codes collapsed)={collapsed_codes}")

    # ── 4. Union-find over base edges + residual edges ───────────────────────
    uf = UnionFind()
    for r in base_rows:
        uf.union(r["canonical_cdp_code"], r["super_canonical_cdp_code"])
    for a, b in new_edges:
        uf.union(a, b)
    comps = {root: m for root, m in uf.components().items() if len(m) >= 2}

    # PRESERVE base representatives: a component that already existed in BASE keeps
    # its stored super_canonical (so served cdp_codes for untouched dealers do NOT
    # churn). A newly-fused component has exactly one base super present (the
    # dominant's) -> use it. Pure-new components (none) fall back to (-avail, cdp).
    base_super = {r["canonical_cdp_code"]: r["super_canonical_cdp_code"] for r in base_rows}
    out: list[tuple[str, str, int, bool]] = []   # (canon, super, comp_size, is_rep)
    multi_base = 0
    for _, members in comps.items():
        present = {base_super[m] for m in members if m in base_super}
        if len(present) == 1:
            rep = next(iter(present))
        elif len(present) == 0:
            rep = min(members, key=lambda c: (-avail.get(c, 0), c))
        else:
            multi_base += 1                       # would fuse two base components — flagged below
            rep = min(present, key=lambda c: (-avail.get(c, 0), c))
        for m in members:
            out.append((m, rep, len(members), m == rep))

    # ── 5. Safety asserts vs the base overlay ────────────────────────────────
    m2rep = {row[0]: row[1] for row in out}              # new: member -> final rep
    base_super_map = {r["canonical_cdp_code"]: r["super_canonical_cdp_code"] for r in base_rows}

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
    # SAFE residual groups. No collateral movement anywhere else.
    safe_codes: set[str] = set()
    for (nm, mc), members in groups.items():
        if any(tok in nm for tok in CHAIN_TOKENS):
            continue
        if len({_norm(m["address"]) for m in members if m["address"]}) > 1:
            continue
        for m in members:
            safe_codes.add(m["cdp_code"])
            safe_codes.add(m["rcode"])
    all_nodes = {c for row in out for c in (row[0], row[1])} | set(base_super_map)
    changed = [c for c in all_nodes if base_rep(c) != new_rep(c)]
    collateral = [c for c in changed if c not in safe_codes]

    # Served dealer count (full universe) — the metric that matters.
    served_before = await conn.fetchval(
        """SELECT count(DISTINCT COALESCE(vdr.resolved_cdp_code, e.cdp_code))
           FROM entity e LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid=e.entity_ulid
           WHERE e.status='active' AND e.kind<>'particular'""")
    served_after = served_before - collapsed_codes

    failures = []
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
        await conn.execute(
            """INSERT INTO canonical_dedup_run
               (run_id, resolver, resolver_version, source_cluster_run, anti_hub_k,
                n_canonicals_in, n_super_canonicals, n_merged, deduped_count, vam_verified, notes)
               VALUES ($1,$2,$3,$4,3,$5,$6,$7,$8,TRUE,$9)""",
            RUN_ID, RESOLVER, RESOLVER_VERSION, SOURCE_CLUSTER_RUN,
            len(safe_codes), len(comps), len(out) - len(comps), served_after,
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
