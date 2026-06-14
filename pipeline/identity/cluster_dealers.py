"""
pipeline/identity/cluster_dealers.py
CAMPAIGN dealer-identity-det-v1 -- fully deterministic union-find clustering.

Replaces both cluster_dealers_run2.py (which depended on the now-deleted
splink-b13-run1 for edge type 4) and cluster_dealers.py (Splink legacy).

Four edge types, all reproducible from the current DB state:

  1. normalized_name + municipality_code  (exact, high-certainty)
  2. phone_digits + municipality_code      (exact, >= 7 digits)
  3. normalized_website_host + municipality_code
                                          (same-muni guard against chain
                                           collapse; NOT cross-municipality)
  4. SQL levenshtein fuzzy:               SAME municipality_code AND
                                           levenshtein(normalized_name) <= 2
                                           ONLY in blocks with <= 500 entities
                                           (pairwise cost guard; large munis
                                           are already covered by edges 1-3)

Run:
    python -m pipeline.identity.cluster_dealers
    python pipeline/identity/cluster_dealers.py

Requires:
    psycopg2, PostgreSQL extension fuzzystrmatch (installed automatically).

Idempotent: deletes cluster_run_id='dealer-identity-det-v1' before writing.
Does NOT touch 'splink-b13-run2' (vam_verified=TRUE, sealed).
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

RUN_ID = "dealer-identity-det-v1"
RESOLVER = "union-find-deterministic"
RESOLVER_VERSION = "2.1.0"  # FIX-A: fuzzy min-len guard; FIX-B: legal-suffix strip
SCOPE_CONDITION = "kind <> 'particular' AND status <> 'closed'"
SCOPE_SQL = "kind <> 'particular'"  # stored in entity_cluster_run.scope

# Fuzzy levenshtein cap: skip intra-muni fuzzy for municipalities with more
# than this many in-scope entities.  Rationale: O(n²) pairwise comparison
# at n=500 produces 125k pairs per block; at n=1507 (Madrid 28079) it would
# produce ~1.1M pairs with heavy PG CPU and minimal marginal gain (edges 1-3
# already cover exact matches, which dominate in large munis).
FUZZY_BLOCK_CAP = 500

# Levenshtein threshold: only merge if normalized_name distance <= this.
# Distance 2 catches typos (missing letter, transposition) without collapsing
# distinct brands ("BMW" ≠ "BM" is distance 1, but normalized forms differ).
FUZZY_MAX_LEVENSHTEIN = 2

# FIX A — minimum normalised-name length to qualify for fuzzy matching.
# Short names (e.g. 'megar' len=5, 'vegar' len=5) are more likely to be
# genuinely distinct dealers than typos; a Levenshtein-1 edit on a 5-char
# name is 20% of the string and should not trigger a merge.
# Names with fewer than 8 alnum characters after normalisation are excluded.
FUZZY_MIN_NAME_LEN = 8

# Source-group priority for canonical selection (higher = preferred).
SOURCE_GROUP_RANK: dict[str, int] = {
    "oem_dealer_network": 10,
    "association": 9,
    "official_registry": 8,
    "marketplace_motor": 7,
    "directory": 6,
}

BLOCKING_RULES: list[str] = [
    "normalized_name + municipality_code (exact; legal-suffix stripped via FIX-B)",
    "phone_digits + municipality_code (exact, >= 7 digits)",
    "normalized_website_host + municipality_code (exact, same-muni guard)",
    f"levenshtein(normalized_name) <= {FUZZY_MAX_LEVENSHTEIN} + same municipality_code "
    f"(SQL fuzzy, blocks <= {FUZZY_BLOCK_CAP} entities, "
    f"min_name_len >= {FUZZY_MIN_NAME_LEN} per FIX-A)",
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
_RE_SCHEME = re.compile(r"^https?://", re.IGNORECASE)
_RE_WWW = re.compile(r"^www\.", re.IGNORECASE)

# Societory suffixes to strip from normalised names (FIX B).
# Order matters: longer patterns must precede their shorter prefixes.
_LEGAL_SUFFIXES: tuple[str, ...] = (
    "sociedadlimitadaunipersonal",
    "sociedadanonima",
    "sociedadlimitada",
    "scoop",
    "scp",
    "slu",
    "sau",
    "sll",
    "sl",
    "sa",
)
# Pre-compile a single regex that matches exactly one suffix at the end.
_RE_LEGAL_SUFFIX = re.compile(
    r"(" + "|".join(re.escape(s) for s in _LEGAL_SUFFIXES) + r")$"
)
# Minimum characters required AFTER stripping the suffix; avoids turning
# short but valid names into empty strings (e.g. a hypothetical 2-char name).
_MIN_NAME_LEN_AFTER_STRIP = 3


def _normalize_name(name: str | None) -> str | None:
    """NFKD -> ASCII ignore -> lower -> strip non-[a-z0-9] -> strip legal suffix.

    The legal-suffix strip (FIX B) removes trailing societory forms such as
    'sa', 'sl', 'slu', 'sau', etc. so that 'AUTOMOCION DEL OESTE, S.A.' and
    'AUTOMOCION DEL OESTE' produce the same normalised key and are captured
    by edge 1 (exact name + muni) without needing fuzzy matching.

    A suffix is only removed when the remaining string has at least
    _MIN_NAME_LEN_AFTER_STRIP characters; otherwise the raw (no-suffix)
    form is returned unchanged to avoid false positives on very short names.

    Returns None if input is empty or produces an empty string.
    """
    if name is None or not isinstance(name, str) or not name.strip():
        return None
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_bytes = nfkd.encode("ascii", "ignore")
    clean = _RE_NON_ALNUM.sub("", ascii_bytes.decode("ascii").lower())
    if not clean:
        return None
    # Strip up to one legal suffix from the end (greedy: longest match wins
    # because _LEGAL_SUFFIXES is ordered longest-first and the regex
    # alternation is tried left-to-right).
    m = _RE_LEGAL_SUFFIX.search(clean)
    if m:
        stripped = clean[: m.start()]
        if len(stripped) >= _MIN_NAME_LEN_AFTER_STRIP:
            clean = stripped
    return clean


def _normalize_phone(phone: str | None) -> str | None:
    """Keep digits only; require >= 7 digits."""
    if phone is None or not isinstance(phone, str) or not phone.strip():
        return None
    digits = "".join(c for c in phone if c.isdigit())
    return digits if len(digits) >= 7 else None


def _normalize_website_host(website: str | None) -> str | None:
    """Strip scheme + www, extract bare host, lower, drop path/query."""
    if website is None or not isinstance(website, str) or not website.strip():
        return None
    host = website.strip().lower()
    host = _RE_SCHEME.sub("", host)
    host = _RE_WWW.sub("", host)
    host = host.split("/")[0].split("?")[0].strip()
    return host if host else None


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
            self._parent[x] = self._parent[self._parent[x]]  # path compression
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


def _load_entities(conn: Any) -> list[dict]:
    """Load all in-scope entities from PG."""
    log.info("Loading entities from PG ...")
    query = f"""
        SELECT
            entity_ulid,
            cdp_code,
            trade_name,
            municipality_code,
            website,
            phone,
            address,
            lat,
            cif,
            source_group::text AS source_group,
            created_at AS first_seen
        FROM entity
        WHERE {SCOPE_CONDITION}
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(query)
        rows = [dict(r) for r in cur.fetchall()]
    log.info("Loaded %d entities", len(rows))
    return rows


def _load_fuzzy_sql_edges(
    conn: Any,
    entities: list[dict],
) -> tuple[list[tuple[str, str]], int, int]:
    """
    Load levenshtein-fuzzy edges via SQL with normalized names pre-computed
    in Python (using the canonical _normalize_name function) and uploaded
    to a PG temp table.

    Strategy:
      - Normalise names in Python (NFKD->ASCII->strip non-alnum) — same logic
        used for edge type 1, guaranteeing consistency.
      - Upload (entity_ulid, municipality_code, norm_name) to a PG temp table.
      - Compute municipality block sizes; skip blocks > FUZZY_BLOCK_CAP.
      - For eligible blocks, self-join in PG using fuzzystrmatch.levenshtein,
        emitting pairs where distance <= FUZZY_MAX_LEVENSHTEIN AND norm_name
        is NOT identical (exact matches are covered by edge type 1).

    Note: unaccent() extension is NOT available; normalisation is done in Python.

    Returns:
        edges           -- list of (u1, u2) pairs with u1 < u2
        n_munis_skipped -- number of municipality blocks exceeding the cap
        n_ents_skipped  -- total entities in those skipped blocks
    """
    log.info(
        "Computing SQL fuzzy levenshtein edges (cap=%d, max_dist=%d) ...",
        FUZZY_BLOCK_CAP,
        FUZZY_MAX_LEVENSHTEIN,
    )

    # Build normalised rows in Python.
    norm_rows: list[tuple[str, str, str]] = []  # (entity_ulid, muni, norm_name)
    for ent in entities:
        uid = ent["entity_ulid"]
        muni = (ent.get("municipality_code") or "").strip() or None
        if muni is None:
            continue
        nn = _normalize_name(ent.get("trade_name"))
        if nn:
            norm_rows.append((uid, muni, nn))

    log.info("Uploading %d normalised rows to PG temp table ...", len(norm_rows))

    with conn.cursor() as cur:
        # Ensure fuzzystrmatch is available (idempotent).
        cur.execute("CREATE EXTENSION IF NOT EXISTS fuzzystrmatch")

        # Build temp table from Python-normalised data.
        cur.execute("DROP TABLE IF EXISTS _tmp_fuzzy_candidates")
        cur.execute("""
            CREATE TEMP TABLE _tmp_fuzzy_candidates (
                entity_ulid  text NOT NULL,
                muni_code    text NOT NULL,
                norm_name    text NOT NULL
            )
        """)
        psycopg2.extras.execute_values(
            cur,
            "INSERT INTO _tmp_fuzzy_candidates VALUES %s",
            norm_rows,
            template="(%s, %s, %s)",
            page_size=5000,
        )
        cur.execute(
            "CREATE INDEX ON _tmp_fuzzy_candidates(muni_code)"
        )

        # Compute block sizes.
        cur.execute(f"""
            SELECT muni_code,
                   COUNT(*) AS n,
                   COUNT(*) > {FUZZY_BLOCK_CAP} AS skipped
            FROM _tmp_fuzzy_candidates
            GROUP BY muni_code
        """)
        block_rows = cur.fetchall()

    skipped_munis = {r[0] for r in block_rows if r[2]}
    n_munis_skipped = len(skipped_munis)
    n_ents_skipped = sum(r[1] for r in block_rows if r[2])

    if n_munis_skipped:
        log.warning(
            "FUZZY CAP: skipping %d municipality block(s) with > %d entities "
            "(%d total entities; covered by exact edges 1-3). Skipped: %s",
            n_munis_skipped,
            FUZZY_BLOCK_CAP,
            n_ents_skipped,
            sorted(skipped_munis),
        )
    else:
        log.info("All municipality blocks are within the fuzzy cap.")

    with conn.cursor() as cur:
        # Self-join within eligible blocks only.
        # Exclude pairs where norm_name is identical (edge 1 handles those).
        # FIX A: skip fuzzy for short names (len < FUZZY_MIN_NAME_LEN) to
        # avoid merging distinct short-name dealers like 'megar'/'vegar'.
        cur.execute(f"""
            SELECT a.entity_ulid AS uid_a,
                   b.entity_ulid AS uid_b
            FROM _tmp_fuzzy_candidates a
            JOIN _tmp_fuzzy_candidates b
              ON  a.muni_code = b.muni_code
              AND a.entity_ulid < b.entity_ulid
              AND a.norm_name <> b.norm_name
            JOIN (
                SELECT muni_code
                FROM _tmp_fuzzy_candidates
                GROUP BY muni_code
                HAVING COUNT(*) <= {FUZZY_BLOCK_CAP}
            ) eligible ON eligible.muni_code = a.muni_code
            WHERE length(a.norm_name) >= {FUZZY_MIN_NAME_LEN}
              AND length(b.norm_name) >= {FUZZY_MIN_NAME_LEN}
              AND levenshtein(a.norm_name, b.norm_name) <= {FUZZY_MAX_LEVENSHTEIN}
        """)
        raw_pairs = cur.fetchall()

        cur.execute("DROP TABLE IF EXISTS _tmp_fuzzy_candidates")

    edges: list[tuple[str, str]] = [
        (r[0], r[1]) if r[0] < r[1] else (r[1], r[0])
        for r in raw_pairs
    ]
    log.info(
        "SQL fuzzy: %d edge pairs from %d eligible blocks",
        len(edges),
        len(block_rows) - n_munis_skipped,
    )
    return edges, n_munis_skipped, n_ents_skipped


# ---------------------------------------------------------------------------
# Edge generation (in-Python edges 1-3)
# ---------------------------------------------------------------------------


def _build_deterministic_edges(entities: list[dict]) -> list[tuple[str, str]]:
    """
    Build edge types 1, 2, and 3 in Python using index structures.

    Edge 1: normalized_name + municipality_code (exact)
    Edge 2: phone_digits + municipality_code    (exact, >= 7 digits)
    Edge 3: normalized_website_host + municipality_code (same-muni guard)

    Returns deduplicated (u1, u2) pairs with u1 < u2.
    """
    idx_name_muni: dict[tuple[str, str], list[str]] = defaultdict(list)
    idx_phone_muni: dict[tuple[str, str], list[str]] = defaultdict(list)
    idx_web_muni: dict[tuple[str, str], list[str]] = defaultdict(list)

    for ent in entities:
        uid = ent["entity_ulid"]
        muni = (ent.get("municipality_code") or "").strip() or None
        if muni is None:
            continue

        nn = _normalize_name(ent.get("trade_name"))
        if nn:
            idx_name_muni[(nn, muni)].append(uid)

        ph = _normalize_phone(ent.get("phone"))
        if ph:
            idx_phone_muni[(ph, muni)].append(uid)

        wh = _normalize_website_host(ent.get("website"))
        if wh:
            idx_web_muni[(wh, muni)].append(uid)

    edge_set: set[tuple[str, str]] = set()

    def _add_bucket(bucket: list[str]) -> None:
        for i in range(len(bucket)):
            for j in range(i + 1, len(bucket)):
                u, v = bucket[i], bucket[j]
                edge_set.add((u, v) if u < v else (v, u))

    log.info("Building edge type 1 (norm_name + muni) ...")
    n1 = sum(1 for b in idx_name_muni.values() if len(b) > 1)
    for bucket in idx_name_muni.values():
        if len(bucket) > 1:
            _add_bucket(bucket)
    log.info("  buckets > 1: %d", n1)

    log.info("Building edge type 2 (phone + muni) ...")
    n2 = sum(1 for b in idx_phone_muni.values() if len(b) > 1)
    for bucket in idx_phone_muni.values():
        if len(bucket) > 1:
            _add_bucket(bucket)
    log.info("  buckets > 1: %d", n2)

    log.info("Building edge type 3 (website_host + muni, same-muni guard) ...")
    n3 = sum(1 for b in idx_web_muni.values() if len(b) > 1)
    for bucket in idx_web_muni.values():
        if len(bucket) > 1:
            _add_bucket(bucket)
    log.info("  buckets > 1: %d", n3)

    log.info("Deterministic edges (1+2+3): %d unique pairs", len(edge_set))
    return list(edge_set)


# ---------------------------------------------------------------------------
# Canonical selection
# ---------------------------------------------------------------------------


def _source_group_rank(sg: str | None) -> int:
    return SOURCE_GROUP_RANK.get(sg, 1) if sg else 1


def _richness(ent: dict) -> int:
    return sum(
        1 for f in ("website", "phone", "address", "cif", "lat")
        if ent.get(f) is not None and str(ent.get(f, "")).strip()
    )


def _select_canonical(members: list[str], entity_by_ulid: dict[str, dict]) -> str:
    """
    Pick the canonical entity for a cluster.

    Priority (descending):
      1. source_group rank (higher = preferred)
      2. richness (more non-null key attrs = better)
      3. first_seen (older = better)
      4. cdp_code (ascending tiebreak)
    """
    def sort_key(uid: str) -> tuple:
        ent = entity_by_ulid.get(uid, {})
        return (
            -_source_group_rank(ent.get("source_group")),
            -_richness(ent),
            str(ent.get("first_seen") or "9999-99-99"),
            ent.get("cdp_code") or "ZZZZ",
        )

    return min(members, key=sort_key)


# ---------------------------------------------------------------------------
# Cluster table builder
# ---------------------------------------------------------------------------


def _build_cluster_table(
    entities: list[dict],
    edges: list[tuple[str, str]],
) -> list[dict]:
    """
    Apply union-find over all edges and return cluster assignment rows.

    Returns list of dicts:
        entity_ulid, canonical_ulid, match_probability (None), cluster_size
    """
    entity_by_ulid: dict[str, dict] = {e["entity_ulid"]: e for e in entities}
    all_ulids = set(entity_by_ulid.keys())

    log.info(
        "Running union-find: %d entities, %d edges ...",
        len(all_ulids), len(edges),
    )
    uf = UnionFind()
    for uid in all_ulids:
        uf._init(uid)
    for u, v in edges:
        if u in all_ulids and v in all_ulids:
            uf.union(u, v)

    components = uf.components()
    result: list[dict] = []
    for _root, members in components.items():
        in_scope = [m for m in members if m in all_ulids]
        if not in_scope:
            continue
        canonical = _select_canonical(in_scope, entity_by_ulid)
        sz = len(in_scope)
        for uid in in_scope:
            result.append({
                "entity_ulid": uid,
                "canonical_ulid": canonical,
                "match_probability": None,
                "cluster_size": sz,
            })

    n_clusters = len({r["canonical_ulid"] for r in result})
    log.info("Union-find: %d rows, %d clusters", len(result), n_clusters)
    return result


# ---------------------------------------------------------------------------
# PG write (idempotent)
# ---------------------------------------------------------------------------


def _write_to_pg(
    conn: Any,
    cluster_rows: list[dict],
    n_entities_in: int,
    fuzzy_cap_meta: dict,
) -> None:
    """
    Write entity_cluster_run + entity_cluster in a single transaction.
    Deletes any previous dealer-identity-det-v1 run first.
    """
    n_clusters_out = len({r["canonical_ulid"] for r in cluster_rows})
    n_merged = n_entities_in - n_clusters_out

    blocking_rules_with_meta = list(BLOCKING_RULES)
    blocking_rules_with_meta.append(
        f"fuzzy_cap_meta: {json.dumps(fuzzy_cap_meta)}"
    )

    log.info(
        "Writing to PG: n_in=%d | n_clusters=%d | n_merged=%d",
        n_entities_in, n_clusters_out, n_merged,
    )

    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM entity_cluster WHERE cluster_run_id = %s",
                (RUN_ID,),
            )
            cur.execute(
                "DELETE FROM entity_cluster_run WHERE cluster_run_id = %s",
                (RUN_ID,),
            )

            cur.execute(
                """
                INSERT INTO entity_cluster_run
                    (cluster_run_id, resolver, resolver_version, scope,
                     threshold, blocking_rules, n_entities_in, n_clusters_out,
                     n_merged, vam_verified)
                VALUES (%s, %s, %s, %s, NULL, %s::jsonb, %s, %s, %s, FALSE)
                """,
                (
                    RUN_ID,
                    RESOLVER,
                    RESOLVER_VERSION,
                    SCOPE_SQL,
                    json.dumps(blocking_rules_with_meta),
                    n_entities_in,
                    n_clusters_out,
                    n_merged,
                ),
            )

            rows_to_insert = [
                (
                    RUN_ID,
                    r["entity_ulid"],
                    r["canonical_ulid"],
                    r["match_probability"],
                    r["cluster_size"],
                )
                for r in cluster_rows
            ]
            psycopg2.extras.execute_values(
                cur,
                """
                INSERT INTO entity_cluster
                    (cluster_run_id, entity_ulid, canonical_ulid,
                     match_probability, cluster_size)
                VALUES %s
                """,
                rows_to_insert,
                template="(%s, %s, %s, %s, %s)",
                page_size=5000,
            )

    log.info("Write committed. run_id=%s", RUN_ID)


# ---------------------------------------------------------------------------
# Verification queries
# ---------------------------------------------------------------------------


def _verify_and_report(conn: Any, fuzzy_cap_meta: dict) -> None:
    """Run the five Director-mandated checks and print compact report."""
    log.info("=== VERIFICATION REPORT (%s) ===", RUN_ID)

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

        # 0. Run-level stats
        cur.execute(
            """
            SELECT n_entities_in, n_clusters_out, n_merged
            FROM entity_cluster_run
            WHERE cluster_run_id = %s
            """,
            (RUN_ID,),
        )
        run = cur.fetchone()
        pct = (
            round(100.0 * run["n_merged"] / run["n_entities_in"], 2)
            if run["n_entities_in"] else 0
        )
        print(
            f"\n--- RUN STATS ({RUN_ID}) ---\n"
            f"  n_entities_in : {run['n_entities_in']}\n"
            f"  n_clusters_out: {run['n_clusters_out']}\n"
            f"  n_merged      : {run['n_merged']} ({pct}% colapso)\n"
            f"  fuzzy_cap     : munis_skipped={fuzzy_cap_meta['n_munis_skipped']} "
            f"entities_skipped={fuzzy_cap_meta['n_ents_skipped']} "
            f"(cap={FUZZY_BLOCK_CAP}, levenshtein<={FUZZY_MAX_LEVENSHTEIN})\n"
        )

        # 1. RECALL intra-fuente
        cur.execute(
            """
            WITH groups AS (
                SELECT
                    e.first_discovered_source,
                    e.trade_name,
                    e.municipality_code,
                    COUNT(*) AS n_ents,
                    COUNT(DISTINCT ec.canonical_ulid) AS n_canonicals
                FROM entity e
                JOIN entity_cluster ec ON ec.entity_ulid = e.entity_ulid
                WHERE ec.cluster_run_id = %s
                  AND e.kind <> 'particular'
                  AND e.municipality_code IS NOT NULL
                GROUP BY e.first_discovered_source, e.trade_name, e.municipality_code
                HAVING COUNT(*) > 1
            )
            SELECT
                COUNT(*) AS total_groups,
                SUM(CASE WHEN n_canonicals = 1 THEN 1 ELSE 0 END) AS groups_merged,
                ROUND(
                    100.0 * SUM(CASE WHEN n_canonicals = 1 THEN 1 ELSE 0 END)
                    / NULLIF(COUNT(*), 0),
                2) AS recall_pct
            FROM groups
            """,
            (RUN_ID,),
        )
        recall = cur.fetchone()
        print(
            f"--- CHECK 1: RECALL intra-fuente ---\n"
            f"  Total grupos (>1 entidad, mismo source+trade_name+muni): "
            f"{recall['total_groups']}\n"
            f"  Grupos con 1 solo canónico: {recall['groups_merged']}\n"
            f"  Recall: {recall['recall_pct']}%  (objetivo ~100%)\n"
        )

        # 2. PRECISION: canonicals spanning >1 municipality without shared website/phone
        cur.execute(
            """
            WITH cluster_munis AS (
                SELECT
                    ec.canonical_ulid,
                    COUNT(DISTINCT e.municipality_code)
                        FILTER (WHERE e.municipality_code IS NOT NULL) AS n_munis,
                    COUNT(DISTINCT e.website)
                        FILTER (WHERE e.website IS NOT NULL AND e.website <> '')
                        AS n_sites,
                    COUNT(DISTINCT e.phone)
                        FILTER (WHERE e.phone IS NOT NULL AND e.phone <> '')
                        AS n_phones,
                    MAX(ec.cluster_size) AS csize
                FROM entity_cluster ec
                JOIN entity e ON e.entity_ulid = ec.entity_ulid
                WHERE ec.cluster_run_id = %s
                GROUP BY ec.canonical_ulid
            )
            SELECT COUNT(*) AS fp_count
            FROM cluster_munis
            WHERE n_munis > 1
              AND n_sites = 0
              AND n_phones = 0
              AND csize > 1
            """,
            (RUN_ID,),
        )
        prec = cur.fetchone()
        print(
            f"--- CHECK 2: PRECISION (cross-muni sin web ni phone compartido) ---\n"
            f"  Falsos positivos: {prec['fp_count']}  (objetivo 0)\n"
        )

        # 3. CADENAS: Flexicar, OcasionPlus — must stay separated by municipality
        for chain, pattern in [
            ("Flexicar", "%flexicar%"),
            ("OcasionPlus", "%ocasionplus%"),
        ]:
            cur.execute(
                """
                SELECT
                    COUNT(DISTINCT ec.canonical_ulid) AS n_canonicals,
                    COUNT(DISTINCT e.municipality_code)
                        FILTER (WHERE e.municipality_code IS NOT NULL) AS n_munis,
                    COUNT(*) AS n_entities
                FROM entity_cluster ec
                JOIN entity e ON e.entity_ulid = ec.entity_ulid
                WHERE ec.cluster_run_id = %s
                  AND e.website ILIKE %s
                  AND e.kind <> 'particular'
                """,
                (RUN_ID, pattern),
            )
            row = cur.fetchone()
            status = (
                "OK -- separadas por muni"
                if row["n_canonicals"] >= row["n_munis"]
                else "WARN -- posible colapso de cadena"
            )
            print(
                f"--- CHECK 3: CADENA {chain} ---\n"
                f"  Entidades: {row['n_entities']} | "
                f"Municipios: {row['n_munis']} | "
                f"Canónicos: {row['n_canonicals']}  [{status}]\n"
            )

        # 4. MOBILITY CENTRO muni 28134 — 480+ entities -> must collapse to 1
        cur.execute(
            """
            SELECT
                COUNT(DISTINCT ec.canonical_ulid) AS n_canonicals,
                COUNT(*) AS n_entities
            FROM entity_cluster ec
            JOIN entity e ON e.entity_ulid = ec.entity_ulid
            WHERE ec.cluster_run_id = %s
              AND e.trade_name = 'MOBILITY CENTRO'
              AND e.municipality_code = '28134'
            """,
            (RUN_ID,),
        )
        mob = cur.fetchone()
        status = "OK" if mob["n_canonicals"] == 1 else "FAIL"
        print(
            f"--- CHECK 4: MOBILITY CENTRO (muni 28134) ---\n"
            f"  Entidades: {mob['n_entities']} -> "
            f"Canónicos: {mob['n_canonicals']}  [{status} -- objetivo: 1]\n"
        )

        # 5. Top 5 largest clusters
        cur.execute(
            """
            SELECT
                ec.canonical_ulid,
                ce.trade_name AS canonical_name,
                ec.cluster_size,
                COUNT(DISTINCT e.municipality_code) AS n_munis
            FROM entity_cluster ec
            JOIN entity e ON e.entity_ulid = ec.entity_ulid
            JOIN entity ce ON ce.entity_ulid = ec.canonical_ulid
            WHERE ec.cluster_run_id = %s
            GROUP BY ec.canonical_ulid, ce.trade_name, ec.cluster_size
            ORDER BY ec.cluster_size DESC
            LIMIT 5
            """,
            (RUN_ID,),
        )
        top5 = cur.fetchall()
        print("--- CHECK 5: TOP 5 LARGEST CLUSTERS ---")
        for row in top5:
            print(
                f"  canonical={row['canonical_ulid']!r}  "
                f"name={row['canonical_name']!r}  "
                f"size={row['cluster_size']}  "
                f"n_munis={row['n_munis']}"
            )
        print()

        # 6. FIX A — Megar vs Vegar: must be in DISTINCT canonicals.
        # We look for unique (trade_name, muni) combos with ILIKE to be
        # case-insensitive and group them; psycopg2 receives only one %s.
        cur.execute(
            """
            SELECT
                e.trade_name,
                e.municipality_code,
                ec.canonical_ulid
            FROM entity e
            JOIN entity_cluster ec ON ec.entity_ulid = e.entity_ulid
            WHERE ec.cluster_run_id = %s
              AND (e.trade_name ILIKE 'megar' OR e.trade_name ILIKE 'vegar')
            ORDER BY e.trade_name, e.municipality_code
            """,
            (RUN_ID,),
        )
        megar_rows = cur.fetchall()
        # Collect distinct (trade_name_lower, muni) → canonical pairs.
        # Each unique (name, muni) key should map to exactly one canonical.
        name_muni_to_canonical: dict[tuple[str, str], str] = {}
        for r in megar_rows:
            key = (r["trade_name"].lower(), r["municipality_code"] or "")
            name_muni_to_canonical[key] = r["canonical_ulid"]
        distinct_name_munis = set(name_muni_to_canonical.keys())
        distinct_canonicals = set(name_muni_to_canonical.values())
        megar_present = any(k[0] == "megar" for k in distinct_name_munis)
        vegar_present = any(k[0] == "vegar" for k in distinct_name_munis)
        if not megar_present or not vegar_present:
            fixa_status = f"N/A -- megar={megar_present}, vegar={vegar_present} en scope"
        elif len(distinct_canonicals) >= 2:
            fixa_status = "OK -- canónicos DISTINTOS (Megar != Vegar)"
        else:
            fixa_status = "FAIL -- Megar y Vegar colapsados en el mismo canónico"
        print("--- CHECK 6: FIX A (Megar vs Vegar — nombres cortos) ---")
        for key, canonical in sorted(name_muni_to_canonical.items()):
            print(
                f"  trade_name={key[0]!r}  muni={key[1]}  "
                f"canonical={canonical!r}"
            )
        print(f"  [{fixa_status}]\n")

        # 7. FIX B — AUTOMOCION DEL OESTE variants: must merge to 1 canonical.
        # The check is scoped to entities whose normalised name starts with
        # 'automociondeloeste' (which includes the S.A./S.L. variants after
        # legal-suffix stripping), grouped by municipality_code.  For each
        # municipality we check that all entities share a single canonical.
        # Note: %% escapes the literal percent sign for psycopg2.
        cur.execute(
            """
            SELECT
                e.trade_name,
                e.municipality_code,
                ec.canonical_ulid
            FROM entity e
            JOIN entity_cluster ec ON ec.entity_ulid = e.entity_ulid
            WHERE ec.cluster_run_id = %s
              AND e.trade_name ILIKE '%%automocion%%del%%oeste%%'
              AND e.municipality_code IS NOT NULL
            ORDER BY e.municipality_code, e.trade_name
            """,
            (RUN_ID,),
        )
        oeste_rows = cur.fetchall()
        # Group by municipality and check per-muni uniqueness of canonical.
        from collections import defaultdict as _dd
        muni_to_canonicals: dict[str, set[str]] = _dd(set)
        muni_to_names: dict[str, set[str]] = _dd(set)
        for r in oeste_rows:
            muni_to_canonicals[r["municipality_code"]].add(r["canonical_ulid"])
            muni_to_names[r["municipality_code"]].add(r["trade_name"])
        if not oeste_rows:
            fixb_status = "N/A -- entidades no encontradas en scope"
        else:
            bad_munis = {m for m, c in muni_to_canonicals.items() if len(c) > 1}
            if not bad_munis:
                fixb_status = (
                    "OK -- todas las variantes societarias por municipio "
                    "confluyen en 1 canónico"
                )
            else:
                fixb_status = (
                    f"FAIL -- {len(bad_munis)} municipio(s) con >1 canónico: "
                    f"{sorted(bad_munis)}"
                )
        print("--- CHECK 7: FIX B (AUTOMOCION DEL OESTE variantes societarias) ---")
        for muni, canonicals in sorted(muni_to_canonicals.items()):
            names_str = " | ".join(sorted(muni_to_names[muni]))
            print(
                f"  muni={muni}  n_canonicals={len(canonicals)}  "
                f"names=[{names_str}]"
            )
        print(f"  [{fixb_status}]\n")

    log.info("=== END REPORT ===")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    dsn = _get_dsn()
    log.info("Connecting to PG ...")
    conn = psycopg2.connect(dsn)
    conn.autocommit = False

    try:
        # Step 1: Load entities
        entities = _load_entities(conn)
        n_entities_in = len(entities)

        # Step 2: Build deterministic edges (1, 2, 3) in Python
        det_edges = _build_deterministic_edges(entities)

        # Step 3: Build SQL fuzzy levenshtein edges (4) inside PG
        # This runs in a sub-transaction with temp tables; we commit after.
        fuzzy_edges, n_munis_skipped, n_ents_skipped = _load_fuzzy_sql_edges(conn, entities)
        conn.commit()  # commit the CREATE EXTENSION (if it ran for first time)
        fuzzy_cap_meta = {
            "n_munis_skipped": n_munis_skipped,
            "n_ents_skipped": n_ents_skipped,
            "cap": FUZZY_BLOCK_CAP,
            "max_levenshtein": FUZZY_MAX_LEVENSHTEIN,
        }

        # Step 4: Merge all edges
        all_edges: list[tuple[str, str]] = det_edges + fuzzy_edges
        # Deduplicate across edge type lists
        all_edges = list(set(all_edges))
        log.info(
            "Total unique edges after merge: %d "
            "(det=%d, fuzzy=%d)",
            len(all_edges), len(det_edges), len(fuzzy_edges),
        )

        # Step 5: Union-find -> cluster assignments
        cluster_rows = _build_cluster_table(entities, all_edges)

        assert len(cluster_rows) == n_entities_in, (
            f"Row count mismatch: {len(cluster_rows)} != {n_entities_in}"
        )

        # Step 6: Write to PG (idempotent, single transaction)
        _write_to_pg(conn, cluster_rows, n_entities_in, fuzzy_cap_meta)

        # Step 7: Verify (read-only, autocommit safe)
        conn.autocommit = True
        _verify_and_report(conn, fuzzy_cap_meta)

    except Exception:
        log.exception("Fatal error in dealer-identity-det-v1 pipeline")
        raise
    finally:
        conn.close()
        log.info("PG connection closed.")


if __name__ == "__main__":
    main()
