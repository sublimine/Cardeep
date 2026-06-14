"""
pipeline/identity/cluster_vehicles.py
CAMPAIGN vehicle-identity-det-v1 — deterministic union-find clustering of physical cars.

Identifies listings that represent the SAME physical car across platforms
(wallapop, milanuncios, coches.net, etc.) WITHOUT ever mutating vehicle rows.

Two edge types, both reproducible from current DB state:

  A. photo_url (identical, normalized):
     Same byte-level photo URL → same physical car.  SUFFICIENT ALONE.
     False-positive risk: near-zero (platforms use CDN-unique URLs).

  B. firma (make + model + year + km EXACT + price ±2% + same province_code):
     Cross-entity duplicate.  REQUIRES at least one corroborating guard:
       b1. normalized title matches, OR
       b2. same entity_ulid (same dealer listed twice).
     Anti-FP: NEVER merge cross-province.  Two identical cars can exist in
     the same province at the same price — guard b1/b2 prevents collapse.

Canonical selection: earliest first_seen (oldest listing = primary source).
Tiebreak: vehicle_ulid lexicographic ascending (deterministic).

Run:
    python -m pipeline.identity.cluster_vehicles
    python pipeline/identity/cluster_vehicles.py

Idempotent: deletes cluster_run_id='vehicle-identity-det-v1' before writing.
Does NOT touch any other run.

Requires:
    psycopg2, PostgreSQL (no extensions needed).
"""
from __future__ import annotations

import json
import logging
import os
import re
import sys
import unicodedata
from collections import defaultdict
from typing import Any

import psycopg2
import psycopg2.extras

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RUN_ID = "vehicle-identity-det-v1"
RESOLVER = "union-find-deterministic"
RESOLVER_VERSION = "1.0.0"
SCOPE_CONDITION = "status = 'available'"

# Price tolerance for firma-based matching: ±2% of the lower price.
PRICE_TOL_PCT = 0.02

# Blocking rules stored for audit / reproducibility.
BLOCKING_RULES: list[str] = [
    "photo_url normalized (exact): same CDN photo = same physical car [signal A, sufficient alone]",
    (
        "firma = exact(make, model, year, km) + price ±2% + same province_code "
        "+ (same normalized_title OR same entity_ulid) [signal B, anti-FP guards mandatory]"
    ),
]


def _get_dsn() -> str:
    return os.environ.get(
        "CARDEEP_DSN",
        "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep",
    )


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

_RE_NON_ALNUM = re.compile(r"[^a-z0-9]")
_RE_QUERY = re.compile(r"\?.*$")
_RE_TRAILING_SLASH = re.compile(r"/+$")
_RE_SCHEME = re.compile(r"^https?://", re.IGNORECASE)
_RE_RESIZE_SUFFIX = re.compile(
    r"[/_-](?:thumb|thumbnail|small|medium|large|\d+x\d+|\d+w)$",
    re.IGNORECASE,
)


def _normalize_photo_url(url: str | None) -> str | None:
    """Normalize a photo URL for deduplication.

    Steps:
      1. Strip whitespace.
      2. Lowercase.
      3. Remove query string (CDN resize params vary; path is stable).
      4. Strip trailing slashes.
      5. Remove known resize/thumbnail suffixes from the path.

    Returns None for empty/missing URLs.
    """
    if not url or not url.strip():
        return None
    u = url.strip().lower()
    u = _RE_QUERY.sub("", u)
    u = _RE_TRAILING_SLASH.sub("", u)
    u = _RE_RESIZE_SUFFIX.sub("", u)
    return u if u else None


def _normalize_title(title: str | None) -> str | None:
    """NFKD → ASCII ignore → lower → strip non-[a-z0-9].

    Returns None for empty/missing titles.
    """
    if not title or not title.strip():
        return None
    nfkd = unicodedata.normalize("NFKD", title)
    clean = _RE_NON_ALNUM.sub("", nfkd.encode("ascii", "ignore").decode("ascii").lower())
    return clean if clean else None


def _prices_within_tolerance(p_a: Any, p_b: Any) -> bool:
    """Return True if both prices are within PRICE_TOL_PCT of each other."""
    if p_a is None or p_b is None:
        return False
    try:
        fa, fb = float(p_a), float(p_b)
    except (TypeError, ValueError):
        return False
    if fa <= 0 or fb <= 0:
        return False
    lower = min(fa, fb)
    return abs(fa - fb) / lower <= PRICE_TOL_PCT


# ---------------------------------------------------------------------------
# Union-Find (path-compressed, union-by-rank)
# ---------------------------------------------------------------------------


class UnionFind:
    """Path-compressed, union-by-rank union-find over string IDs."""

    def __init__(self) -> None:
        self._parent: dict[str, str] = {}
        self._rank: dict[str, int] = {}

    def _init(self, x: str) -> None:
        if x not in self._parent:
            self._parent[x] = x
            self._rank[x] = 0

    def find(self, x: str) -> str:
        self._init(x)
        while self._parent[x] != x:
            self._parent[x] = self._parent[self._parent[x]]  # path halving
            x = self._parent[x]
        return x

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
        """Return {root: [members]} for all registered IDs."""
        groups: dict[str, list[str]] = defaultdict(list)
        for node in self._parent:
            groups[self.find(node)].append(node)
        return dict(groups)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _load_vehicles(conn: Any) -> list[dict]:
    """Load all in-scope vehicles with entity province_code via JOIN."""
    log.info("Loading vehicles from PG (status='available') ...")
    query = """
        SELECT
            v.vehicle_ulid,
            v.entity_ulid,
            v.make,
            v.model,
            v.year,
            v.km,
            v.price,
            v.title,
            v.photo_url,
            v.first_seen,
            e.province_code
        FROM vehicle v
        LEFT JOIN entity e ON e.entity_ulid = v.entity_ulid
        WHERE v.status = 'available'
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(query)
        rows = [dict(r) for r in cur.fetchall()]
    log.info("Loaded %d vehicles", len(rows))
    return rows


# ---------------------------------------------------------------------------
# Edge generation
# ---------------------------------------------------------------------------


def _build_edges(
    vehicles: list[dict],
) -> tuple[list[tuple[str, str, str]], dict[tuple[str, str], str]]:
    """Build all deduplication edges.

    Returns:
        edges:       list of (ulid_a, ulid_b, signal) — signal ∈ {'photo_url','firma','both'}
        edge_signals: dict (min_ulid, max_ulid) → signal (for cluster_size assignment)
    """
    # -----------------------------------------------------------------------
    # Signal A: photo_url index
    # -----------------------------------------------------------------------
    log.info("Building Signal A edges (photo_url) ...")
    idx_photo: dict[str, list[str]] = defaultdict(list)
    for v in vehicles:
        norm = _normalize_photo_url(v.get("photo_url"))
        if norm:
            idx_photo[norm].append(v["vehicle_ulid"])

    photo_edges: set[tuple[str, str]] = set()
    for bucket in idx_photo.values():
        if len(bucket) < 2:
            continue
        for i in range(len(bucket)):
            for j in range(i + 1, len(bucket)):
                a, b = bucket[i], bucket[j]
                photo_edges.add((a, b) if a < b else (b, a))
    log.info("  Signal A pairs: %d", len(photo_edges))

    # -----------------------------------------------------------------------
    # Signal B: firma index
    # Anti-FP guards: (1) same province_code, (2) title match OR same entity
    # -----------------------------------------------------------------------
    log.info("Building Signal B edges (firma + anti-FP guards) ...")

    # Group by (make, model, year, km, province_code) — the firma block key.
    # price ±2% is checked pairwise within the block.
    idx_firma: dict[tuple, list[dict]] = defaultdict(list)
    for v in vehicles:
        make = (v.get("make") or "").strip().lower() or None
        model = (v.get("model") or "").strip().lower() or None
        year = v.get("year")
        km = v.get("km")
        province = v.get("province_code") or None

        if not (make and model and year is not None and km is not None and province):
            continue

        block_key = (make, model, year, km, province)
        idx_firma[block_key].append(v)

    firma_edges: set[tuple[str, str]] = set()
    n_blocks_checked = 0
    for block_key, bucket in idx_firma.items():
        if len(bucket) < 2:
            continue
        n_blocks_checked += 1
        for i in range(len(bucket)):
            for j in range(i + 1, len(bucket)):
                va, vb = bucket[i], bucket[j]

                # Price guard: must be within ±2%
                if not _prices_within_tolerance(va.get("price"), vb.get("price")):
                    continue

                # Anti-FP guard: require at least one corroborating signal
                # (1) same entity_ulid, OR (2) same normalized title
                same_entity = va["entity_ulid"] == vb["entity_ulid"]
                ta = _normalize_title(va.get("title"))
                tb = _normalize_title(vb.get("title"))
                same_title = bool(ta and tb and ta == tb)

                if not (same_entity or same_title):
                    continue

                a, b = va["vehicle_ulid"], vb["vehicle_ulid"]
                firma_edges.add((a, b) if a < b else (b, a))

    log.info(
        "  Signal B firma blocks checked=%d  pairs produced=%d",
        n_blocks_checked,
        len(firma_edges),
    )

    # -----------------------------------------------------------------------
    # Merge into unified edge list, tagging signal type
    # -----------------------------------------------------------------------
    both = photo_edges & firma_edges
    only_photo = photo_edges - firma_edges
    only_firma = firma_edges - photo_edges

    edge_list: list[tuple[str, str, str]] = []
    edge_signal_map: dict[tuple[str, str], str] = {}

    for pair in both:
        edge_list.append((pair[0], pair[1], "both"))
        edge_signal_map[pair] = "both"
    for pair in only_photo:
        edge_list.append((pair[0], pair[1], "photo_url"))
        edge_signal_map[pair] = "photo_url"
    for pair in only_firma:
        edge_list.append((pair[0], pair[1], "firma"))
        edge_signal_map[pair] = "firma"

    log.info(
        "Total edges: %d  (photo_only=%d  firma_only=%d  both=%d)",
        len(edge_list),
        len(only_photo),
        len(only_firma),
        len(both),
    )
    return edge_list, edge_signal_map


# ---------------------------------------------------------------------------
# Canonical selection
# ---------------------------------------------------------------------------


def _select_canonical(members: list[str], vehicle_by_ulid: dict[str, dict]) -> str:
    """Select canonical listing: earliest first_seen, tiebreak ulid ascending."""
    def sort_key(uid: str) -> tuple:
        v = vehicle_by_ulid.get(uid, {})
        return (
            str(v.get("first_seen") or "9999-99-99"),
            uid,
        )
    return min(members, key=sort_key)


# ---------------------------------------------------------------------------
# Cluster table builder
# ---------------------------------------------------------------------------


def _build_cluster_table(
    vehicles: list[dict],
    edges: list[tuple[str, str, str]],
    edge_signal_map: dict[tuple[str, str], str],
) -> list[dict]:
    """Apply union-find and return per-vehicle cluster assignment rows.

    For each vehicle, match_signal reflects the strongest signal in its cluster:
      'both' > 'photo_url' > 'firma'
    Singletons get match_signal='none'.
    """
    vehicle_by_ulid: dict[str, dict] = {v["vehicle_ulid"]: v for v in vehicles}
    all_ulids = set(vehicle_by_ulid.keys())

    log.info("Running union-find: %d vehicles, %d edges ...", len(all_ulids), len(edges))
    uf = UnionFind()
    for uid in all_ulids:
        uf._init(uid)
    for a, b, _sig in edges:
        if a in all_ulids and b in all_ulids:
            uf.union(a, b)

    # Build signal strength per root — highest signal present in the cluster
    _SIGNAL_RANK = {"none": 0, "firma": 1, "photo_url": 2, "both": 3}
    root_signal: dict[str, str] = defaultdict(lambda: "none")
    for a, b, sig in edges:
        if a not in all_ulids or b not in all_ulids:
            continue
        root = uf.find(a)
        if _SIGNAL_RANK[sig] > _SIGNAL_RANK[root_signal[root]]:
            root_signal[root] = sig

    components = uf.components()
    result: list[dict] = []
    n_clusters = 0
    for _root, members in components.items():
        in_scope = [m for m in members if m in all_ulids]
        if not in_scope:
            continue
        canonical = _select_canonical(in_scope, vehicle_by_ulid)
        sz = len(in_scope)
        sig = root_signal.get(uf.find(canonical), "none")
        n_clusters += 1
        for uid in in_scope:
            result.append({
                "vehicle_ulid": uid,
                "canonical_vehicle_ulid": canonical,
                "match_signal": sig if sz > 1 else "none",
                "match_probability": None,
                "cluster_size": sz,
            })

    log.info("Union-find done: %d rows, %d clusters", len(result), n_clusters)
    return result


# ---------------------------------------------------------------------------
# PG write (idempotent)
# ---------------------------------------------------------------------------


def _write_to_pg(
    conn: Any,
    cluster_rows: list[dict],
    n_in: int,
    edge_signal_map: dict[tuple[str, str], str],
) -> None:
    """Write vehicle_cluster_run + vehicle_cluster in a single transaction.

    Deletes any previous vehicle-identity-det-v1 run first (idempotent).
    """
    n_clusters = len({r["canonical_vehicle_ulid"] for r in cluster_rows})
    n_merged = n_in - n_clusters

    # Edge-type breakdown for notes
    counts: dict[str, int] = defaultdict(int)
    for sig in edge_signal_map.values():
        counts[sig] += 1
    notes = json.dumps({
        "edges_photo_url": counts.get("photo_url", 0),
        "edges_firma": counts.get("firma", 0),
        "edges_both": counts.get("both", 0),
    })

    log.info(
        "Writing to PG: n_in=%d  n_clusters=%d  n_merged=%d",
        n_in, n_clusters, n_merged,
    )

    with conn:
        with conn.cursor() as cur:
            # Idempotent: delete previous run
            cur.execute(
                "DELETE FROM vehicle_cluster WHERE cluster_run_id = %s", (RUN_ID,)
            )
            cur.execute(
                "DELETE FROM vehicle_cluster_run WHERE cluster_run_id = %s", (RUN_ID,)
            )

            cur.execute(
                """
                INSERT INTO vehicle_cluster_run
                    (cluster_run_id, resolver, resolver_version, scope,
                     blocking_rules, n_in, n_clusters, n_merged, vam_verified, notes)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s, FALSE, %s)
                """,
                (
                    RUN_ID,
                    RESOLVER,
                    RESOLVER_VERSION,
                    SCOPE_CONDITION,
                    json.dumps(BLOCKING_RULES),
                    n_in,
                    n_clusters,
                    n_merged,
                    notes,
                ),
            )

            rows_to_insert = [
                (
                    RUN_ID,
                    r["vehicle_ulid"],
                    r["canonical_vehicle_ulid"],
                    r["match_signal"],
                    r["match_probability"],
                    r["cluster_size"],
                )
                for r in cluster_rows
            ]
            psycopg2.extras.execute_values(
                cur,
                """
                INSERT INTO vehicle_cluster
                    (cluster_run_id, vehicle_ulid, canonical_vehicle_ulid,
                     match_signal, match_probability, cluster_size)
                VALUES %s
                """,
                rows_to_insert,
                template="(%s, %s, %s, %s, %s, %s)",
                page_size=5000,
            )

    log.info("Write committed. run_id=%s", RUN_ID)


# ---------------------------------------------------------------------------
# Measurement and validation
# ---------------------------------------------------------------------------


def _measure_and_validate(conn: Any) -> None:
    """Measure unique physical cars + 20-pair sample for Director validation."""
    log.info("=== B7 MEASUREMENT & VALIDATION REPORT (%s) ===", RUN_ID)

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

        # --- 0. Run-level stats ---
        cur.execute(
            """
            SELECT n_in, n_clusters, n_merged, notes
            FROM vehicle_cluster_run
            WHERE cluster_run_id = %s
            """,
            (RUN_ID,),
        )
        run = cur.fetchone()
        pct = round(100.0 * run["n_merged"] / run["n_in"], 2) if run["n_in"] else 0
        print(
            f"\n--- RUN STATS ---\n"
            f"  listings_in  : {run['n_in']:,}\n"
            f"  unique_cars  : {run['n_clusters']:,}\n"
            f"  merged       : {run['n_merged']:,} ({pct}% colapso)\n"
            f"  edge_notes   : {run['notes']}\n"
        )

        # --- 1. Breakdown by signal ---
        cur.execute(
            """
            SELECT
                match_signal,
                COUNT(*) FILTER (WHERE cluster_size > 1) AS listings_in_multi,
                COUNT(DISTINCT canonical_vehicle_ulid) FILTER (WHERE cluster_size > 1) AS clusters
            FROM vehicle_cluster
            WHERE cluster_run_id = %s
            GROUP BY match_signal
            ORDER BY match_signal
            """,
            (RUN_ID,),
        )
        print("--- SIGNAL BREAKDOWN ---")
        for r in cur.fetchall():
            print(
                f"  signal={r['match_signal']!r:12s}  "
                f"multi-listing clusters={r['clusters']:>7,}  "
                f"listings={r['listings_in_multi']:>8,}"
            )
        print()

        # --- 2. Platform breakdown for merged clusters ---
        cur.execute(
            """
            SELECT
                regexp_replace(v.deep_link, '^https?://([^/]+).*', '\\1') AS host,
                COUNT(*) AS listings,
                COUNT(DISTINCT vc.canonical_vehicle_ulid) AS canonical_cars
            FROM vehicle_cluster vc
            JOIN vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
            WHERE vc.cluster_run_id = %s
              AND vc.cluster_size > 1
            GROUP BY host
            ORDER BY listings DESC
            LIMIT 15
            """,
            (RUN_ID,),
        )
        print("--- PLATFORM BREAKDOWN (merged clusters only) ---")
        for r in cur.fetchall():
            print(
                f"  {r['host']:45s} listings={r['listings']:>7,}  "
                f"canonical_cars={r['canonical_cars']:>7,}"
            )
        print()

        # --- 3. Province sample: 28 (Madrid) + 08 (Barcelona) ---
        for prov, pname in [("28", "Madrid"), ("08", "Barcelona")]:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total_listings,
                    COUNT(DISTINCT vc.canonical_vehicle_ulid) AS unique_cars,
                    COUNT(*) - COUNT(DISTINCT vc.canonical_vehicle_ulid) AS merged
                FROM vehicle_cluster vc
                JOIN vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
                LEFT JOIN entity e ON e.entity_ulid = v.entity_ulid
                WHERE vc.cluster_run_id = %s
                  AND e.province_code = %s
                """,
                (RUN_ID, prov),
            )
            r = cur.fetchone()
            print(
                f"--- PROVINCE {prov} ({pname}) ---\n"
                f"  total_listings={r['total_listings']:,}  "
                f"unique_cars={r['unique_cars']:,}  "
                f"merged={r['merged']:,}\n"
            )

        # --- 4. 20-pair sample for Director validation ---
        # Pick 10 pairs matched by photo_url and 10 by firma (or both).
        cur.execute(
            """
            WITH merged AS (
                SELECT
                    vc.canonical_vehicle_ulid,
                    vc.match_signal,
                    vc.cluster_size,
                    v.vehicle_ulid,
                    v.deep_link,
                    v.make,
                    v.model,
                    v.year,
                    v.km,
                    v.price,
                    v.photo_url,
                    v.title,
                    ROW_NUMBER() OVER (
                        PARTITION BY vc.canonical_vehicle_ulid
                        ORDER BY v.first_seen ASC, v.vehicle_ulid ASC
                    ) AS rn
                FROM vehicle_cluster vc
                JOIN vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
                WHERE vc.cluster_run_id = %s
                  AND vc.cluster_size = 2
                  AND vc.match_signal IN ('photo_url', 'firma', 'both')
            )
            SELECT
                a.canonical_vehicle_ulid,
                a.match_signal,
                a.deep_link    AS dl_a,  a.make AS make_a,  a.model AS model_a,
                a.year AS year_a,  a.km AS km_a,  a.price AS price_a,
                a.photo_url    AS photo_a,  a.title AS title_a,
                b.deep_link    AS dl_b,  b.make AS make_b,  b.model AS model_b,
                b.year AS year_b,  b.km AS km_b,  b.price AS price_b,
                b.photo_url    AS photo_b,  b.title AS title_b
            FROM merged a
            JOIN merged b ON b.canonical_vehicle_ulid = a.canonical_vehicle_ulid AND b.rn = 2
            WHERE a.rn = 1
            LIMIT 20
            """,
            (RUN_ID,),
        )
        pairs = cur.fetchall()
        print("--- 20-PAIR SAMPLE (Director VAM) ---")
        for i, p in enumerate(pairs, 1):
            # Extract platform from deep_link
            def _host(dl: str | None) -> str:
                if not dl:
                    return "?"
                m = re.search(r"https?://([^/]+)", dl)
                return m.group(1) if m else "?"

            print(
                f"\n  [{i:02d}] signal={p['match_signal']}  "
                f"canonical={p['canonical_vehicle_ulid']}\n"
                f"        A: [{_host(p['dl_a'])}] "
                f"{p['make_a']} {p['model_a']} {p['year_a']} "
                f"{p['km_a']}km €{p['price_a']}\n"
                f"           title={str(p['title_a'])[:60]}\n"
                f"           photo={str(p['photo_a'])[:70]}\n"
                f"        B: [{_host(p['dl_b'])}] "
                f"{p['make_b']} {p['model_b']} {p['year_b']} "
                f"{p['km_b']}km €{p['price_b']}\n"
                f"           title={str(p['title_b'])[:60]}\n"
                f"           photo={str(p['photo_b'])[:70]}"
            )

    log.info("=== END B7 REPORT ===")


# ---------------------------------------------------------------------------
# Verification queries
# ---------------------------------------------------------------------------


def _run_anti_fp_checks(conn: Any) -> None:
    """Run Director-mandated anti-false-positive checks."""
    log.info("=== ANTI-FP CHECKS ===")

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

        # Check 1: No cross-province merges
        cur.execute(
            """
            SELECT COUNT(*) AS cross_prov_clusters
            FROM (
                SELECT vc.canonical_vehicle_ulid
                FROM vehicle_cluster vc
                JOIN vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
                LEFT JOIN entity e ON e.entity_ulid = v.entity_ulid
                WHERE vc.cluster_run_id = %s
                  AND e.province_code IS NOT NULL
                GROUP BY vc.canonical_vehicle_ulid
                HAVING COUNT(DISTINCT e.province_code) > 1
            ) sub
            """,
            (RUN_ID,),
        )
        r = cur.fetchone()
        status = "OK (0)" if r["cross_prov_clusters"] == 0 else f"FAIL ({r['cross_prov_clusters']})"
        print(f"\n--- CHECK 1: No cross-province merges ---\n  {status}")

        # Check 2: No cluster_size > 20 (pathological chain collapse)
        cur.execute(
            """
            SELECT COUNT(*) AS giant_clusters
            FROM (
                SELECT canonical_vehicle_ulid, MAX(cluster_size) AS sz
                FROM vehicle_cluster
                WHERE cluster_run_id = %s
                GROUP BY canonical_vehicle_ulid
                HAVING MAX(cluster_size) > 20
            ) sub
            """,
            (RUN_ID,),
        )
        r = cur.fetchone()
        status = "OK" if r["giant_clusters"] == 0 else f"WARN ({r['giant_clusters']} clusters > 20 listings)"
        print(f"--- CHECK 2: No pathological giant clusters (>20) ---\n  {status}")

        # Check 3: All vehicle_ulids covered exactly once
        cur.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM vehicle WHERE status='available') AS total_vehicles,
                (SELECT COUNT(*) FROM vehicle_cluster WHERE cluster_run_id=%s) AS clustered,
                (SELECT COUNT(DISTINCT vehicle_ulid) FROM vehicle_cluster WHERE cluster_run_id=%s) AS distinct_clustered
            """,
            (RUN_ID, RUN_ID),
        )
        r = cur.fetchone()
        ok = r["total_vehicles"] == r["clustered"] == r["distinct_clustered"]
        status = "OK" if ok else f"FAIL total={r['total_vehicles']} clustered={r['clustered']} distinct={r['distinct_clustered']}"
        print(f"--- CHECK 3: All available vehicles covered exactly once ---\n  {status}")

        # Check 4: singletons report match_signal='none'
        cur.execute(
            """
            SELECT COUNT(*) AS bad_singletons
            FROM vehicle_cluster
            WHERE cluster_run_id = %s
              AND cluster_size = 1
              AND match_signal <> 'none'
            """,
            (RUN_ID,),
        )
        r = cur.fetchone()
        status = "OK" if r["bad_singletons"] == 0 else f"FAIL ({r['bad_singletons']})"
        print(f"--- CHECK 4: Singletons have match_signal='none' ---\n  {status}")

    log.info("=== END ANTI-FP CHECKS ===")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    dsn = _get_dsn()
    log.info("Connecting to PG ...")
    conn = psycopg2.connect(dsn)
    conn.autocommit = False

    try:
        # Step 1: Load
        vehicles = _load_vehicles(conn)
        n_in = len(vehicles)

        # Step 2: Build edges
        edges, edge_signal_map = _build_edges(vehicles)

        # Step 3: Union-find → cluster rows
        cluster_rows = _build_cluster_table(vehicles, edges, edge_signal_map)

        assert len(cluster_rows) == n_in, (
            f"Row count mismatch: {len(cluster_rows)} != {n_in}"
        )

        # Step 4: Write to PG (idempotent)
        _write_to_pg(conn, cluster_rows, n_in, edge_signal_map)

        # Step 5: Measure + validate (read-only)
        conn.autocommit = True
        _measure_and_validate(conn)
        _run_anti_fp_checks(conn)

    except Exception:
        log.exception("Fatal error in vehicle-identity-det-v1 pipeline")
        raise
    finally:
        conn.close()
        log.info("PG connection closed.")


if __name__ == "__main__":
    main()
