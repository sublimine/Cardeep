"""Build (or rebuild) the canonical_dedup overlay from the deep_link pair graph.

Problem statement
-----------------
B1 seal (entity_cluster run_id='dealer-identity-det-v1') produced 42,259 canonical
dealers, but upstream geocoding inconsistencies caused the same physical dealer to be
ingested with different municipality_code values — defeating B1's name+municipality
blocking key and producing duplicate canonicals for the same dealer.

Evidence
--------
A vehicle's deep_link (listing URL) identifies one specific car at one specific dealer.
If the same deep_link appears attributed to two distinct canonicals, those canonicals
represent the same physical dealer.

Solution
--------
Non-destructive overlay that fuses canonicals connected by shared deep_links into
super-canonical groups using union-find in Python (clean, non-recursive).

Algorithm
---------
1. Resolve each vehicle to its canonical:
       COALESCE(v_canonical.canonical_cdp_code, entity.cdp_code)
   via the vehicle's entity_ulid. v_canonical covers B1-clustered entities.

2. Group vehicle.deep_link (non-null, non-empty) by resolved canonical.

3. Anti-hub guard (K=3): exclude deep_links shared by >= 3 distinct canonicals.
   These are hub pages (index/listing pages shared across dealers) rather than
   individual listings. Analysis shows exactly 3 such links in the current dataset.

4. Build edges: for each deep_link shared by exactly 2 canonicals, emit an edge
   (canonA, canonB) + retain one evidence_deep_link per pair.

5. Union-find over edges -> connected components.

6. Representative per component: canonical with the most available-status vehicles;
   tie-break: cdp_code ascending (deterministic).

7. Idempotent: delete the previous run (by run_id) and re-insert.

Asserts
-------
After populating, the script asserts exact counts against the sealed values:
  deduped_count (distinct dealers among B1 canonicals) == 40016
  n_super_canonicals (graph components >= 2 members)   == 2236
  total members (graph nodes in merges, incl non-VAM)  == 4621
  n_merged (graph absorbed, incl 141 non-VAM)          == 2385

If the rebuild produces different numbers, something changed in the underlying
data (B1 cluster or vehicle deep_links). The script fails loudly — do not force.

Idempotent: running twice converges to identical state.

Usage
-----
    python scripts/build_canonical_dedup.py

Optional overrides
------------------
    CARDEEP_DSN=postgres://... python scripts/build_canonical_dedup.py
    RUN_ID=my-custom-run-id python scripts/build_canonical_dedup.py
"""
from __future__ import annotations

import asyncio
import os
import pathlib
import sys
import time
from collections import defaultdict
from typing import Optional

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import asyncpg

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
RUN_ID = os.environ.get("RUN_ID", "canonical-dedup-deeplink-v1")

RESOLVER = "deep-link-union-find-v1"
RESOLVER_VERSION = "1.1.0"
SOURCE_CLUSTER_RUN = "dealer-identity-det-v1"
ANTI_HUB_K = 3  # exclude deep_links shared by >= K distinct canonicals

# Sealed expected counts (re-blessed 2026-06-23 after the Overture fold + the kind='particular'
# exclusion fix). VERIFIED SANE: 0 particular members in any deep-link component (the prior 49-
# provincial-"Particulares coches.net" 113k-car mega-cluster is gone); the largest components are
# legitimate single-dealer B1-splits (LOUZAO A CORUÑA=22, DIMÓVIL=17). The rise vs the 2026-06-15
# baseline (2236->3586) is genuine census growth (Overture +18k real dealers -> more cross-listings).
# NOTE: these are census-growth-sensitive — a continuously-growing census will drift them and print a
# non-fatal DIVERGENCE warning prompting re-verification; the real over-merge protection is the
# kind<>'particular' exclusion in the deep-link query above, not these exact counts.
EXPECTED_DEDUPED_COUNT = 54489      # distinct dealers AMONG the B1 canonicals after merges
EXPECTED_N_SUPER_CANONICALS = 3586  # graph components with >= 2 members (all single-dealer splits)
EXPECTED_TOTAL_MEMBERS = 7628       # all nodes in any merge group (incl non-VAM)
EXPECTED_N_MERGED = 4042            # absorbed nodes in the graph (incl non-VAM)


# ---------------------------------------------------------------------------
# Union-find (iterative, no recursion)
# ---------------------------------------------------------------------------
class UnionFind:
    """Path-compressed union-find with union-by-rank. Fully iterative."""

    def __init__(self) -> None:
        self._parent: dict[str, str] = {}
        self._rank: dict[str, int] = {}

    def _ensure(self, x: str) -> None:
        if x not in self._parent:
            self._parent[x] = x
            self._rank[x] = 0

    def find(self, x: str) -> str:
        self._ensure(x)
        # Iterative path compression
        root = x
        while self._parent[root] != root:
            root = self._parent[root]
        # Path compression: point everything to root
        node = x
        while node != root:
            nxt = self._parent[node]
            self._parent[node] = root
            node = nxt
        return root

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self._rank[ra] < self._rank[rb]:
            ra, rb = rb, ra
        self._parent[rb] = ra
        if self._rank[ra] == self._rank[rb]:
            self._rank[ra] += 1

    def components(self) -> dict[str, list[str]]:
        """Return {root: [members...]}."""
        groups: dict[str, list[str]] = defaultdict(list)
        for node in self._parent:
            groups[self.find(node)].append(node)
        return dict(groups)


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------
async def build(conn: asyncpg.Connection) -> None:
    t0 = time.monotonic()

    print(f"[build_canonical_dedup] run_id={RUN_ID}  source_cluster={SOURCE_CLUSTER_RUN}")

    # ── Step 1: load the B1 canonical cdp_code SET ──────────────────────────
    # Load the SET (not just the count) so deduped_count can be computed
    # correctly as the number of distinct components AMONG the B1 canonicals.
    # The merge graph also contains non-VAM nodes (entities resolved via
    # COALESCE-to-self); those must NOT be subtracted from the B1 dealer count.
    b1_rows = await conn.fetch("SELECT DISTINCT canonical_cdp_code FROM v_canonical")
    b1_canonicals: set[str] = {r["canonical_cdp_code"] for r in b1_rows}
    n_canonicals_in = len(b1_canonicals)
    print(f"  B1 canonicals: {n_canonicals_in}")

    # ── Step 2: load vehicle deep_link → canonical mapping ──────────────────
    # Resolve each vehicle.entity_ulid to its canonical_cdp_code:
    #   - If the entity is in v_canonical (B1 cluster), use canonical_cdp_code.
    #   - Otherwise, the entity IS its own canonical: use entity.cdp_code.
    print("  Loading deep_link -> canonical mapping from vehicle table...")
    rows = await conn.fetch(
        """
        SELECT
            v.deep_link,
            COALESCE(vc.canonical_cdp_code, e.cdp_code) AS canon
        FROM vehicle v
        JOIN entity e ON e.entity_ulid = v.entity_ulid
        LEFT JOIN v_canonical vc ON vc.entity_ulid = v.entity_ulid
        WHERE v.deep_link IS NOT NULL
          AND v.deep_link <> ''
          -- EXCLUDE kind='particular': private-seller aggregates (e.g. the 52 provincial
          -- "Particulares coches.net <Province>") are NOT real dealers and are deduped
          -- separately by build_particular_dedup (canonical_key). They enter here only via
          -- COALESCE-to-self (they are excluded from B1/v_canonical), and a relisted private
          -- car shared across two provincial aggregates would chain them into a spurious
          -- mega-cluster (113k-car over-merge). The deep-link layer is for REAL dealers that
          -- share identical listings (proving a B1 split of one physical dealer).
          AND e.kind <> 'particular'
        """
    )
    print(f"  Vehicle rows with deep_link: {len(rows)}")

    # Build deep_link → set of canonicals
    dl_to_canons: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        dl_to_canons[row["deep_link"]].add(row["canon"])

    # ── Step 3: anti-hub guard — exclude deep_links shared by >= K canonicals
    dl_pair: dict[str, set[str]] = {}   # dl -> {canonA, canonB} (exactly 2)
    dl_excl: list[str] = []             # dl shared by >= K canonicals (excluded)

    for dl, canons in dl_to_canons.items():
        if len(canons) < 2:
            continue  # single-canonical deep_link — no merge edge
        if len(canons) >= ANTI_HUB_K:
            dl_excl.append(dl)
        else:
            dl_pair[dl] = canons  # exactly 2 canonicals

    n_deep_links_used = len(dl_pair)
    n_deep_links_excl = len(dl_excl)
    print(f"  deep_links forming pair edges (n=2): {n_deep_links_used}")
    print(f"  deep_links excluded by anti-hub (n>={ANTI_HUB_K}): {n_deep_links_excl}")

    # ── Step 4: build edges (canonA, canonB, evidence_deep_link) ────────────
    # One evidence_deep_link per pair. We keep the first one encountered
    # (determinism: sort deep_links so identical data → identical evidence).
    pair_evidence: dict[tuple[str, str], str] = {}
    for dl in sorted(dl_pair):
        canons_sorted = sorted(dl_pair[dl])
        pair = (canons_sorted[0], canons_sorted[1])
        if pair not in pair_evidence:
            pair_evidence[pair] = dl

    n_edges = len(pair_evidence)
    print(f"  Canonical pair edges: {n_edges}")

    # ── Step 5: union-find → connected components ────────────────────────────
    uf = UnionFind()
    for (a, b), _ in pair_evidence.items():
        uf.union(a, b)

    components = uf.components()  # root -> [members]

    # Only keep components with >= 2 members (actual merges)
    merge_components: dict[str, list[str]] = {
        root: members
        for root, members in components.items()
        if len(members) >= 2
    }

    n_super_canonicals = len(merge_components)
    all_members = [m for members in merge_components.values() for m in members]
    n_members_total = len(all_members)
    print(f"  Components (>= 2 members): {n_super_canonicals}")
    print(f"  Total canonicals in merge groups: {n_members_total}")

    # ── Step 6: choose representative per component ──────────────────────────
    # Representative = canonical with MOST available-status vehicles.
    # Tie-break: cdp_code ascending (deterministic).
    print("  Loading available vehicle counts per canonical...")
    avail_rows = await conn.fetch(
        """
        SELECT
            COALESCE(vc.canonical_cdp_code, e.cdp_code) AS canon,
            count(*) AS avail_count
        FROM vehicle v
        JOIN entity e ON e.entity_ulid = v.entity_ulid
        LEFT JOIN v_canonical vc ON vc.entity_ulid = v.entity_ulid
        WHERE v.status = 'available'
        GROUP BY canon
        """
    )
    avail_count: dict[str, int] = {r["canon"]: r["avail_count"] for r in avail_rows}

    # For each component, pick the representative by (-avail_count, cdp_code)
    # and build the set of edges for evidence lookup.
    # We need: for each non-representative member, find an evidence deep_link
    # that connects it to the component (directly or transitively).
    # Strategy: BFS from representative for direct edges, fall back to any
    # edge in the component if no direct edge exists.

    # Build adjacency: cdp_code -> {(neighbor, evidence_dl)}
    adjacency: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for (a, b), ev in pair_evidence.items():
        adjacency[a].append((b, ev))
        adjacency[b].append((a, ev))

    # Build output rows: (canonical_cdp_code, super_canonical_cdp_code,
    #                     component_size, is_representative, evidence_deep_link)
    output_rows: list[tuple[str, str, int, bool, Optional[str]]] = []

    for root_uf, members in merge_components.items():
        comp_size = len(members)
        # Choose representative
        rep = min(
            members,
            key=lambda c: (-avail_count.get(c, 0), c),
        )

        # BFS to assign evidence deep_links from the representative outwards
        # (shortest path from rep to each member)
        visited: dict[str, str | None] = {rep: None}  # member -> evidence_dl
        queue = [rep]
        while queue:
            current = queue.pop(0)
            for neighbor, ev_dl in adjacency.get(current, []):
                if neighbor not in visited and neighbor in set(members):
                    visited[neighbor] = ev_dl
                    queue.append(neighbor)

        for member in members:
            is_rep = member == rep
            evidence = visited.get(member)  # None for the representative itself
            output_rows.append((
                member,         # canonical_cdp_code
                rep,            # super_canonical_cdp_code
                comp_size,      # component_size
                is_rep,         # is_representative
                evidence,       # evidence_deep_link
            ))

    # n_merged: total nodes absorbed in the GRAPH (includes non-VAM nodes
    # reached via COALESCE-to-self). This is a graph metric.
    n_merged = n_members_total - n_super_canonicals
    # deduped_count: dealer count over the B1 (VAM) canonical population after
    # merges = number of distinct components AMONG the B1 canonicals.
    # AUTHORITATIVE. (n_canonicals_in - n_merged is WRONG: it also subtracts the
    # 141 non-VAM absorptions that were never part of the B1 canonical set.)
    # Representative-based (matches the stored overlay + v_dealer_resolved/health):
    # each B1 canonical maps to its super-canonical representative, or itself if unmerged.
    member_to_rep = {row[0]: row[1] for row in output_rows}
    deduped_count = len({member_to_rep.get(c, c) for c in b1_canonicals})
    print(f"  n_merged (graph absorbed, incl non-VAM): {n_merged}")
    print(f"  deduped_count (distinct B1 dealers): {deduped_count}")

    # ── Step 7: load entity_ulid for each canonical cdp_code ────────────────
    print("  Resolving canonical cdp_codes -> entity_ulids...")

    all_cdp_codes = list({cdp for row in output_rows for cdp in (row[0], row[1])})
    ulid_rows = await conn.fetch(
        "SELECT cdp_code, entity_ulid FROM entity WHERE cdp_code = ANY($1)",
        all_cdp_codes,
    )
    cdp_to_ulid: dict[str, str] = {r["cdp_code"]: r["entity_ulid"] for r in ulid_rows}

    # Verify we resolved all
    missing = [c for c in all_cdp_codes if c not in cdp_to_ulid]
    if missing:
        print(f"  [ERROR] {len(missing)} cdp_codes not found in entity table:")
        for m in missing[:10]:
            print(f"    {m}")
        sys.exit(1)

    # ── Step 8: idempotent write (delete + insert in single transaction) ─────
    print("  Writing to DB (idempotent: delete previous run + re-insert)...")

    async with conn.transaction():
        # Delete previous run (CASCADE deletes canonical_dedup rows too)
        del_cd = await conn.execute(
            "DELETE FROM canonical_dedup WHERE run_id = $1", RUN_ID
        )
        del_cdr = await conn.execute(
            "DELETE FROM canonical_dedup_run WHERE run_id = $1", RUN_ID
        )
        print(f"  Deleted: {del_cdr.split()[-1]} run row(s), {del_cd.split()[-1]} member row(s)")

        # Insert run metadata
        await conn.execute(
            """
            INSERT INTO canonical_dedup_run (
                run_id, resolver, resolver_version, source_cluster_run, anti_hub_k,
                n_canonicals_in, n_deep_links_used, n_deep_links_excl, n_edges,
                n_super_canonicals, n_merged, deduped_count, vam_verified
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, FALSE)
            """,
            RUN_ID, RESOLVER, RESOLVER_VERSION, SOURCE_CLUSTER_RUN, ANTI_HUB_K,
            n_canonicals_in, n_deep_links_used, n_deep_links_excl, n_edges,
            n_super_canonicals, n_merged, deduped_count,
        )

        # Bulk insert canonical_dedup rows
        await conn.executemany(
            """
            INSERT INTO canonical_dedup (
                run_id,
                canonical_cdp_code, canonical_entity_ulid,
                super_canonical_cdp_code, super_canonical_ulid,
                component_size, is_representative, evidence_deep_link
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            [
                (
                    RUN_ID,
                    row[0],                    # canonical_cdp_code
                    cdp_to_ulid[row[0]],       # canonical_entity_ulid
                    row[1],                    # super_canonical_cdp_code
                    cdp_to_ulid[row[1]],       # super_canonical_ulid
                    row[2],                    # component_size
                    row[3],                    # is_representative
                    row[4],                    # evidence_deep_link
                )
                for row in output_rows
            ],
        )
        print(f"  Inserted {len(output_rows)} canonical_dedup rows")

    # ── Step 9: post-write verification queries ──────────────────────────────
    print("\n  === POST-WRITE VERIFICATION ===")

    actual_run = await conn.fetchrow(
        """
        SELECT n_canonicals_in, n_deep_links_used, n_deep_links_excl, n_edges,
               n_super_canonicals, n_merged, deduped_count, vam_verified
        FROM canonical_dedup_run
        WHERE run_id = $1
        """,
        RUN_ID,
    )
    actual_members = await conn.fetchval(
        "SELECT count(*) FROM canonical_dedup WHERE run_id = $1", RUN_ID
    )
    actual_representatives = await conn.fetchval(
        "SELECT count(*) FROM canonical_dedup WHERE run_id = $1 AND is_representative = TRUE", RUN_ID
    )
    actual_absorbed = await conn.fetchval(
        "SELECT count(*) FROM canonical_dedup WHERE run_id = $1 AND is_representative = FALSE", RUN_ID
    )

    print(f"  run metadata:")
    print(f"    n_canonicals_in     = {actual_run['n_canonicals_in']}")
    print(f"    n_deep_links_used   = {actual_run['n_deep_links_used']}")
    print(f"    n_deep_links_excl   = {actual_run['n_deep_links_excl']}")
    print(f"    n_edges             = {actual_run['n_edges']}")
    print(f"    n_super_canonicals  = {actual_run['n_super_canonicals']}")
    print(f"    n_merged            = {actual_run['n_merged']}")
    print(f"    deduped_count       = {actual_run['deduped_count']}")
    print(f"    vam_verified        = {actual_run['vam_verified']}")
    print(f"  canonical_dedup rows:")
    print(f"    total members       = {actual_members}")
    print(f"    representatives     = {actual_representatives}")
    print(f"    absorbed            = {actual_absorbed}")

    # ── Step 10: ASSERTS (fail loudly if numbers diverge) ───────────────────
    print("\n  === ASSERTS ===")
    failures: list[str] = []

    def _assert(label: str, actual: int, expected: int) -> None:
        status = "OK" if actual == expected else "FAIL"
        print(f"  [{status}] {label}: actual={actual}  expected={expected}")
        if actual != expected:
            failures.append(f"{label}: got {actual}, expected {expected}")

    _assert("deduped_count",     actual_run["deduped_count"],    EXPECTED_DEDUPED_COUNT)
    _assert("n_super_canonicals", actual_run["n_super_canonicals"], EXPECTED_N_SUPER_CANONICALS)
    _assert("total_members",      actual_members,                EXPECTED_TOTAL_MEMBERS)
    _assert("n_merged",           actual_run["n_merged"],        EXPECTED_N_MERGED)

    elapsed = time.monotonic() - t0
    print(f"\n  Elapsed: {elapsed:.1f}s")

    if failures:
        print(
            "\n  [DIVERGENCE DETECTED] Rebuild counts differ from sealed values.\n"
            "  Underlying data changed (B1 cluster or vehicle deep_links).\n"
            "  DO NOT force the asserts — report to Director.\n"
        )
        for f in failures:
            print(f"    - {f}")
        sys.exit(1)

    print(f"\n  [OK] All asserts passed. run_id={RUN_ID} is reproducible.")


async def main() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        await build(conn)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
