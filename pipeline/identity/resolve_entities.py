"""
pipeline/identity/resolve_entities.py
F1 — Entity resolution (β): derives the "same professional dealer" across
channels using inventory fingerprint (Jaccard on B7 canonical_vehicle_ulid)
as the dominant key, reinforced by strong identifiers (phone / website domain).

Methodology (mirrors cluster_dealers.py, espejo metodológico):
  1. INVENTORY FINGERPRINT (dominant): Jaccard on canonical_vehicle_ulid sets
     from B7 (vehicle-identity-det-v1). Only km>0 canonicals with
     entity_count < MAX_ENTITY_COLLISION_K are used (excludes catalog stock).
     Two P-entities from DIFFERENT sources sharing Jaccard >= JACCARD_THETA
     are the same physical dealer.

  2. STRONG-IDENTIFIER REINFORCEMENT (where present):
     - Same 9-digit normalized phone → edge (phone signal).
     - Same domain-normalized website host → edge (website signal).

  3. ANTI-OVER-MERGE GUARDS (§8 of architecture):
     - Catalog canonicals excluded: km=0 OR entity_count >= MAX_ENTITY_COLLISION_K.
     - A high-collision phone token (shared by > MAX_PHONE_COLLISION_K P-entities)
       is treated as a CENTRALITA and must be corroborated by fingerprint Jaccard
       >= JACCARD_THETA OR a second identifier signal (e.g. same website domain).
       Alone it does NOT merge.
     - Cross-province merge requires fingerprint Jaccard >= JACCARD_THETA (strong
       signal). Phone-only or website-only cross-province is BLOCKED.
     - [NEW §B] Chain guard: two entities of the same org (same non-null org_id)
       are ALWAYS blocked from merging. Chain branches share stock and phone/website
       but are distinct physical POS. No signal — fingerprint, phone, or website —
       can override this guard.
     - [NEW §B] City-name guard (INE-validated): if both trade names contain a
       distinct city token validated against geo_municipality.name AND those tokens
       differ between the two entities, they are distinct POS (branches in different
       municipalities) and the fingerprint merge is BLOCKED. This applies to ALL
       fingerprint merges (not just high-collision websites). Only tokens matching
       a real INE municipality name are considered city tokens — prevents false
       positives from generic words like "motor" or "auto".

  4. BLOCKING (O(n²) viable for P ~59k):
     - Fingerprint block: entities sharing at least 1 used-car canonical_vehicle_ulid
       → candidate pair (only within block, no full cartesian product).
     - Phone block: normalized phone token → candidate pair.
     - Website block: domain token → candidate pair.
     Pairwise adjudication only inside blocks.

  5. UNION-FIND: deterministic transitive closure over accepted edges.
     Canonical: richest entity (highest field count) → most vehicles → oldest
     created_at → lexicographic entity_ulid (deterministic tiebreak).

  6. [NEW §C] B1 SEEDING: before applying β edges, the union-find is seeded with
     B1 (dealer-identity-det-v1) aristas from v_canonical. This composes B1 ∘ β
     so that entities already merged by the geo-blocking step are preserved in β.
     Chain guard applies to B1 edges too: no two org-siblings are united via B1.

Run:
    python -m pipeline.identity.resolve_entities
    python pipeline/identity/resolve_entities.py

Requires:
    psycopg2

Idempotent: deletes run_id='entity-resolution-fingerprint-v1' before writing.
Does NOT touch entity rows. Does NOT commit until the full run succeeds.
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
# Constants (calibrated to live data 2026-06-14)
# ---------------------------------------------------------------------------

RUN_ID = "entity-resolution-fingerprint-v1"
RESOLVER = "inventory-fingerprint-v1"

# B7 vehicle-cluster run that provides canonical_vehicle_ulid
VEHICLE_CLUSTER_RUN = "vehicle-identity-det-v1"

# B1 dealer-cluster run (geo-blocking step) — used for B1 edge seeding
DEALER_CLUSTER_RUN = "dealer-identity-det-v1"

# P-stratum kinds (never touches particular=R, never touches plataforma/cadena=C)
P_KINDS = ("compraventa", "concesionario_oficial", "garaje")

# Jaccard threshold: two P-entities from different sources sharing ≥ θ of their
# used-car canonical sets are considered the same dealer.
# Calibrated to live data: typical same-dealer Jaccard >> 0.30;
# typical different-dealer Jaccard << 0.10 (1-2 shared cars at most).
JACCARD_THETA: float = 0.30

# Anti-collision guard 1: exclude canonical vehicles shared by ≥ K distinct
# P-entities (catalog stock, OEM new-car listings, platform aggregators).
# Verified live: 7 canonicals with km>0 have ≥10 P-entities (Seat Leon catalog).
# K=5 is conservative: excludes the 1219 high-collision canonicals.
MAX_ENTITY_COLLISION_K: int = 5

# Anti-collision guard 2: a phone shared by ≥ K distinct P-entities is a
# centralita (call center) and alone cannot trigger a merge.
# K=3 means: if 3+ P-entities share a phone → that phone is a centralita.
MAX_PHONE_COLLISION_K: int = 3


def _get_dsn() -> str:
    return os.environ.get(
        "CARDEEP_DSN",
        "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep",
    )


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

_RE_NON_ALNUM = re.compile(r"[^a-z0-9]")
_RE_SCHEME = re.compile(r"^https?://", re.IGNORECASE)
_RE_WWW = re.compile(r"^www\.", re.IGNORECASE)


def _normalize_phone(phone: str | None) -> str | None:
    """Keep digits only; strip to last 9 digits (Spanish mobile/landline).

    Returns None if fewer than 7 digits remain (too short to be meaningful).
    """
    if not phone or not isinstance(phone, str):
        return None
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) < 7:
        return None
    # Use last 9 digits to normalise international prefix variants
    return digits[-9:]


def _normalize_website_host(website: str | None) -> str | None:
    """Strip scheme + www; return bare lowercase host, no path/query."""
    if not website or not isinstance(website, str) or not website.strip():
        return None
    host = website.strip().lower()
    host = _RE_SCHEME.sub("", host)
    host = _RE_WWW.sub("", host)
    host = host.split("/")[0].split("?")[0].strip()
    return host if host else None


# ---------------------------------------------------------------------------
# City-token extraction (INE-validated, for city-guard §B)
# ---------------------------------------------------------------------------

# Normalise a trade name to ASCII lowercase tokens for city detection.
_RE_NON_WORD = re.compile(r"[^a-z0-9]+")


def _nfkd_lower(text: str) -> str:
    """Fold accents, lowercase — maps 'MÁLAGA' → 'malaga'."""
    return "".join(
        c for c in unicodedata.normalize("NFKD", text.lower())
        if not unicodedata.combining(c)
    )


def _city_tokens(
    trade_name: str | None,
    ine_municipalities: frozenset[str] | None = None,
) -> frozenset[str]:
    """Return a frozenset of city tokens found in a trade name.

    When ine_municipalities is provided (accent-folded, lowercased set of INE
    municipality names), only tokens / token sequences that match a real
    municipality name are returned. This prevents generic words like "motor",
    "auto", or "sl" from being treated as cities.

    Multi-word municipality names (e.g. "alcala de henares") are matched by
    checking all possible n-grams of the trade name tokens in descending length
    order (longest match wins, consuming the matched tokens).

    When ine_municipalities is None (legacy / test mode without DB), falls back
    to the old stopword-based heuristic for backward compatibility with tests
    that do not inject the INE set.
    """
    if not trade_name:
        return frozenset()
    normalized = _nfkd_lower(trade_name)
    tokens = [t for t in _RE_NON_WORD.split(normalized) if t]
    if not tokens:
        return frozenset()

    if ine_municipalities is None:
        # Legacy fallback: stopword-based heuristic (used by unit tests that
        # do not pass an INE set).
        _STOPWORDS = {
            "flexicar", "clicars", "ocasionplus", "carplus",
            "sl", "sa", "slu", "motor", "auto", "cars", "coches",
            "segunda", "mano", "ocasion", "grupo", "concesionario",
            "de", "del", "la", "el", "los", "las", "y",
        }
        return frozenset(t for t in tokens if t and t not in _STOPWORDS)

    # INE-validated path: scan for the longest matching municipality name
    # using a sliding n-gram window (greedy, longest first).
    found: list[str] = []
    n = len(tokens)
    consumed: list[bool] = [False] * n
    # Try all start positions; at each position try longest n-gram first.
    for start in range(n):
        if consumed[start]:
            continue
        matched = False
        for end in range(min(n, start + 6), start, -1):  # max 6-word municipality
            candidate = " ".join(tokens[start:end])
            if candidate in ine_municipalities:
                found.append(candidate)
                for idx in range(start, end):
                    consumed[idx] = True
                matched = True
                break
        # Single-word fallback already covered by the loop above (end = start+1)
        # Nothing extra needed here.
        _ = matched  # suppress unused warning

    return frozenset(found)


def _load_ine_municipalities(conn: Any) -> frozenset[str]:
    """Load all INE municipality names, accent-folded and lowercased.

    Returns a frozenset of strings like {'madrid', 'alcorcon', 'leganes',
    'alcala de henares', ...} suitable for direct membership testing.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT name FROM geo_municipality")
        rows = cur.fetchall()
    result = frozenset(_nfkd_lower(r[0]) for r in rows if r[0])
    log.info("INE municipality set loaded: %d names", len(result))
    return result


# ---------------------------------------------------------------------------
# Union-Find (path-compressed, union-by-rank) — identical to cluster_dealers
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
# Constrained Union-Find — propagates city/org constraints transitively
# ---------------------------------------------------------------------------


class ConstrainedUnionFind:
    """Union-find that carries city_set and org_set metadata per component.

    Two components are allowed to merge ONLY if the resulting merged component
    would have:
      - len(city_set) <= 1  (no two distinct INE-validated city tokens)
      - len(org_set) <= 1   (no two distinct non-null org_id values)

    This prevents transitivity from silently uniting entities that cannot be
    co-located (e.g. A—C—B where C lacks a city token but A and B are in
    different municipalities). The constraint propagates: once a component
    contains a city token, any future union with a component containing a
    *different* city token is rejected.

    city_set values: accent-folded, lowercased INE municipality names (same
    representation as _city_tokens returns). org_set values: org_id strings.
    """

    def __init__(self) -> None:
        self._parent: dict[str, str] = {}
        self._rank: dict[str, int] = {}
        # Metadata stored on the *root* node of each component.
        self._city_set: dict[str, frozenset[str]] = {}  # root -> frozenset of city tokens
        self._org_set: dict[str, frozenset[str]] = {}   # root -> frozenset of non-null org_ids
        self.n_constrained_rejections: int = 0

    def _init(
        self,
        x: str,
        city: frozenset[str] = frozenset(),
        org: frozenset[str] = frozenset(),
    ) -> None:
        if x not in self._parent:
            self._parent[x] = x
            self._rank[x] = 0
            self._city_set[x] = city
            self._org_set[x] = org

    def find(self, x: str) -> str:
        self._init(x)
        while self._parent[x] != x:
            self._parent[x] = self._parent[self._parent[x]]  # path halving
            x = self._parent[x]
        return x

    def constrained_union(self, a: str, b: str) -> bool:
        """Attempt to merge components of a and b.

        Returns True if merged, False if rejected by constraint.

        Constraint: merged city_set must have ≤1 distinct city token AND
        merged org_set must have ≤1 distinct org_id.
        """
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return True  # Already same component — trivially OK.

        merged_city = self._city_set[ra] | self._city_set[rb]
        merged_org = self._org_set[ra] | self._org_set[rb]

        if len(merged_city) > 1 or len(merged_org) > 1:
            self.n_constrained_rejections += 1
            return False

        # Merge by rank (higher rank becomes root).
        if self._rank[ra] < self._rank[rb]:
            ra, rb = rb, ra
        self._parent[rb] = ra
        if self._rank[ra] == self._rank[rb]:
            self._rank[ra] += 1

        # Update root metadata.
        self._city_set[ra] = merged_city
        self._org_set[ra] = merged_org
        return True

    def components(self) -> dict[str, list[str]]:
        """Return {root: [members]} for all registered IDs."""
        groups: dict[str, list[str]] = defaultdict(list)
        for node in self._parent:
            groups[self.find(node)].append(node)
        return dict(groups)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _load_p_entities(conn: Any) -> list[dict]:
    """Load all P-stratum entities with their source keys and org_id."""
    log.info("Loading P-stratum entities from PG ...")
    query = """
        SELECT
            e.entity_ulid,
            e.cdp_code,
            e.trade_name,
            e.kind,
            e.province_code,
            e.municipality_code,
            e.phone,
            e.website,
            e.created_at,
            e.org_id,
            ARRAY_AGG(DISTINCT es.source_key ORDER BY es.source_key)
                FILTER (WHERE es.source_key IS NOT NULL) AS source_keys,
            COUNT(DISTINCT v.vehicle_ulid) AS n_vehicles
        FROM entity e
        LEFT JOIN entity_source es ON es.entity_ulid = e.entity_ulid
        LEFT JOIN vehicle v ON v.entity_ulid = e.entity_ulid
        WHERE e.kind IN ('compraventa', 'concesionario_oficial', 'garaje')
        GROUP BY e.entity_ulid, e.cdp_code, e.trade_name, e.kind,
                 e.province_code, e.municipality_code, e.phone, e.website,
                 e.created_at, e.org_id
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(query)
        rows = [dict(r) for r in cur.fetchall()]
    log.info("Loaded %d P-stratum entities", len(rows))
    return rows


def _load_fingerprints(conn: Any, entity_ulids: list[str]) -> dict[str, set[str]]:
    """Load non-catalog canonical_vehicle_ulid sets per P-entity.

    Exclusion criteria for anti-collision guard:
      - canonical km = 0 (new stock / catalog)
      - canonical shared by >= MAX_ENTITY_COLLISION_K distinct P-entities

    Returns: {entity_ulid: {canonical_vehicle_ulid, ...}}
    """
    log.info(
        "Loading inventory fingerprints (B7 run=%s, km>0, collision_k<%d) ...",
        VEHICLE_CLUSTER_RUN,
        MAX_ENTITY_COLLISION_K,
    )
    # Build set of high-collision canonicals to exclude
    query_high_collision = """
        WITH p_entity_set AS (
            SELECT entity_ulid FROM entity
            WHERE kind IN ('compraventa', 'concesionario_oficial', 'garaje')
        ),
        canon_entity_counts AS (
            SELECT vc.canonical_vehicle_ulid,
                   COUNT(DISTINCT v.entity_ulid) AS n_p_entities
            FROM vehicle_cluster vc
            JOIN vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
            JOIN vehicle cv ON cv.vehicle_ulid = vc.canonical_vehicle_ulid
            WHERE vc.cluster_run_id = %s
              AND v.entity_ulid IN (SELECT entity_ulid FROM p_entity_set)
              AND cv.km IS NOT NULL AND cv.km > 0
            GROUP BY vc.canonical_vehicle_ulid
        )
        SELECT canonical_vehicle_ulid
        FROM canon_entity_counts
        WHERE n_p_entities >= %s
    """
    with conn.cursor() as cur:
        cur.execute(query_high_collision, (VEHICLE_CLUSTER_RUN, MAX_ENTITY_COLLISION_K))
        high_collision = {r[0] for r in cur.fetchall()}
    log.info("High-collision canonicals excluded: %d", len(high_collision))

    # Load used-car canonicals per entity, excluding high-collision
    query_fingerprints = """
        SELECT v.entity_ulid, vc.canonical_vehicle_ulid
        FROM vehicle_cluster vc
        JOIN vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
        JOIN vehicle cv ON cv.vehicle_ulid = vc.canonical_vehicle_ulid
        WHERE vc.cluster_run_id = %s
          AND v.entity_ulid = ANY(%s)
          AND cv.km IS NOT NULL AND cv.km > 0
    """
    fingerprints: dict[str, set[str]] = defaultdict(set)
    with conn.cursor() as cur:
        cur.execute(query_fingerprints, (VEHICLE_CLUSTER_RUN, entity_ulids))
        for row in cur.fetchall():
            canon = row[1]
            if canon not in high_collision:
                fingerprints[row[0]].add(canon)

    total = sum(len(v) for v in fingerprints.values())
    log.info(
        "Fingerprints loaded: %d entities with inventory, %d total used-car canonicals",
        len(fingerprints),
        total,
    )
    return dict(fingerprints)


def _load_b1_edges(conn: Any, all_ulids: set[str]) -> list[tuple[str, str]]:
    """Load B1 (dealer-identity-det-v1) edges from v_canonical.

    Returns a list of (entity_ulid, canonical_ulid) pairs where both members
    are in the P-scope (all_ulids) and entity_ulid != canonical_ulid.

    These edges seed the union-find BEFORE β edges are applied, composing B1∘β.
    """
    log.info("Loading B1 edges from v_canonical (run=%s) ...", DEALER_CLUSTER_RUN)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT entity_ulid, canonical_ulid
            FROM v_canonical
            WHERE entity_ulid != canonical_ulid
              AND cluster_run_id = %s
            """,
            (DEALER_CLUSTER_RUN,),
        )
        rows = cur.fetchall()

    # Filter to P-scope only
    b1_edges = [
        (r[0], r[1])
        for r in rows
        if r[0] in all_ulids and r[1] in all_ulids
    ]
    log.info(
        "B1 edges loaded: %d total in v_canonical, %d in P-scope",
        len(rows),
        len(b1_edges),
    )
    return b1_edges


# ---------------------------------------------------------------------------
# Edge generation
# ---------------------------------------------------------------------------

EdgeType = tuple[str, str, str, float]  # (uid_a, uid_b, signal, probability)


def _jaccard(set_a: set[str], set_b: set[str]) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    if intersection == 0:
        return 0.0
    return intersection / len(set_a | set_b)


def _build_edges(
    entities: list[dict],
    fingerprints: dict[str, set[str]],
    ine_municipalities: frozenset[str] | None = None,
) -> list[EdgeType]:
    """Build all accepted merger edges with their signals.

    Args:
        entities: All P-stratum entity dicts.
        fingerprints: {entity_ulid: set of canonical_vehicle_ulid}.
        ine_municipalities: Accent-folded, lowercased set of INE municipality
            names (from _load_ine_municipalities). When provided, the city-guard
            (§B Guard 2) validates city tokens against real municipality names,
            preventing false positives from generic words. When None, the guard
            falls back to a stopword-exclusion heuristic (used in unit tests).

    Blocking strategy (avoids O(n²) global product):
      Block 1 — fingerprint: entities sharing ≥1 used-car canonical → candidate pair.
      Block 2 — phone: normalized phone token → candidate pair.
      Block 3 — website: domain token → candidate pair.

    Adjudication:
      Within each candidate pair, evaluate signals and apply guards.
    """
    entity_by_ulid: dict[str, dict] = {e["entity_ulid"]: e for e in entities}
    all_ulids = set(entity_by_ulid.keys())

    # Pre-compute normalized identifiers
    phone_map: dict[str, str | None] = {
        uid: _normalize_phone(e.get("phone"))
        for uid, e in entity_by_ulid.items()
    }
    website_map: dict[str, str | None] = {
        uid: _normalize_website_host(e.get("website"))
        for uid, e in entity_by_ulid.items()
    }
    org_map: dict[str, str | None] = {
        uid: e.get("org_id")
        for uid, e in entity_by_ulid.items()
    }

    # Phone collision detection: tokens shared by >= MAX_PHONE_COLLISION_K entities
    phone_buckets: dict[str, list[str]] = defaultdict(list)
    for uid, ph in phone_map.items():
        if ph:
            phone_buckets[ph].append(uid)
    high_collision_phones: set[str] = {
        ph for ph, members in phone_buckets.items()
        if len(members) >= MAX_PHONE_COLLISION_K
    }
    if high_collision_phones:
        log.info(
            "High-collision phone tokens (centralitas, excluded alone): %d",
            len(high_collision_phones),
        )

    # Website collision detection: same guard
    website_buckets: dict[str, list[str]] = defaultdict(list)
    for uid, wh in website_map.items():
        if wh:
            website_buckets[wh].append(uid)
    high_collision_websites: set[str] = {
        wh for wh, members in website_buckets.items()
        if len(members) >= MAX_PHONE_COLLISION_K  # same K
    }

    # -------------------------------------------------------------------------
    # Block 1: fingerprint candidates
    # -------------------------------------------------------------------------
    log.info("Building fingerprint block ...")
    canon_to_entities: dict[str, list[str]] = defaultdict(list)
    for uid, fp in fingerprints.items():
        if uid not in all_ulids:
            continue
        for canon in fp:
            canon_to_entities[canon].append(uid)

    # Collect candidate pairs that share >= 1 canonical
    fp_candidates: set[tuple[str, str]] = set()
    for canon, members in canon_to_entities.items():
        if len(members) < 2:
            continue
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                a, b = members[i], members[j]
                fp_candidates.add((a, b) if a < b else (b, a))

    log.info("Fingerprint candidate pairs: %d", len(fp_candidates))

    # -------------------------------------------------------------------------
    # Block 2: phone candidates
    # -------------------------------------------------------------------------
    ph_candidates: set[tuple[str, str]] = set()
    for ph, members in phone_buckets.items():
        if len(members) < 2:
            continue
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                a, b = members[i], members[j]
                ph_candidates.add((a, b) if a < b else (b, a))

    log.info("Phone candidate pairs: %d", len(ph_candidates))

    # -------------------------------------------------------------------------
    # Block 3: website candidates
    # -------------------------------------------------------------------------
    web_candidates: set[tuple[str, str]] = set()
    for wh, members in website_buckets.items():
        if len(members) < 2:
            continue
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                a, b = members[i], members[j]
                web_candidates.add((a, b) if a < b else (b, a))

    log.info("Website candidate pairs: %d", len(web_candidates))

    # -------------------------------------------------------------------------
    # Adjudicate all candidate pairs
    # -------------------------------------------------------------------------
    all_candidates = fp_candidates | ph_candidates | web_candidates
    log.info("Total candidate pairs (union): %d", len(all_candidates))

    accepted_edges: list[EdgeType] = []
    n_fp_accepted = 0
    n_ph_accepted = 0
    n_web_accepted = 0
    n_combo_accepted = 0
    n_fp_blocked = 0
    n_id_blocked = 0
    n_chain_blocked = 0
    n_city_blocked = 0

    for pair in all_candidates:
        uid_a, uid_b = pair
        ea = entity_by_ulid[uid_a]
        eb = entity_by_ulid[uid_b]

        # ── §B Guard 1: chain siblings (same non-null org_id) → NEVER merge ──
        org_a = org_map.get(uid_a)
        org_b = org_map.get(uid_b)
        if org_a is not None and org_a == org_b:
            # Both are branches of the same chain organization: distinct POS,
            # even if they share stock or identifiers. Hard block, no exception.
            n_chain_blocked += 1
            continue

        # Compute signals
        fp_a = fingerprints.get(uid_a, set())
        fp_b = fingerprints.get(uid_b, set())
        jaccard = _jaccard(fp_a, fp_b)
        fp_ok = jaccard >= JACCARD_THETA

        ph_a = phone_map.get(uid_a)
        ph_b = phone_map.get(uid_b)
        phone_match = bool(ph_a and ph_b and ph_a == ph_b)
        phone_high_collision = bool(
            phone_match and ph_a in high_collision_phones
        )

        wh_a = website_map.get(uid_a)
        wh_b = website_map.get(uid_b)
        website_match = bool(wh_a and wh_b and wh_a == wh_b)
        website_high_collision = bool(
            website_match and wh_a in high_collision_websites
        )

        # Guard: same province check (cross-province requires fingerprint)
        same_province = (
            ea.get("province_code") is not None
            and ea.get("province_code") == eb.get("province_code")
        )
        cross_province = not same_province

        # ── §B Guard 2: city-name guard (INE-validated, universal) ──────────
        # If both trade names name DISTINCT, non-empty municipalities (validated
        # against the real INE geo_municipality set), the entities are different
        # physical POS (branches in different towns). Block ANY fingerprint merge.
        #
        # This replaces the old gated version that only applied when the website
        # was high-collision. The root bug: two branches like "AutosMadrid Alcorcón"
        # and "Autosmadrid Leganés" share Jaccard 1.0 (same virtual stock pool)
        # but are distinct POS in different municipalities — fingerprint alone is
        # insufficient proof of co-location.
        #
        # Pairs that lack city tokens in either name, or share the same city
        # token, pass through as before (legitimate cross-channel dedup).
        if fp_ok:
            city_a = _city_tokens(ea.get("trade_name"), ine_municipalities)
            city_b = _city_tokens(eb.get("trade_name"), ine_municipalities)
            # Distinct city = non-empty, non-overlapping INE-validated tokens.
            if city_a and city_b and not city_a.intersection(city_b):
                n_city_blocked += 1
                continue

        # Adjudication rules:
        #
        # Rule 1: fingerprint alone is sufficient IF Jaccard >= θ.
        #   No source-equality constraint: the whole point is cross-source merge.
        #   (Chain guard §B already blocked same-org pairs above.)
        #
        # Rule 2: phone alone is sufficient ONLY IF:
        #   - phone is NOT a centralita (not high collision), AND
        #   - NOT cross-province (without fingerprint).
        #
        # Rule 3: website alone is sufficient ONLY IF:
        #   - website is NOT high-collision, AND
        #   - NOT cross-province (without fingerprint).
        #
        # Rule 4: centralita phone / high-collision website merges ONLY IF
        #   also supported by fingerprint Jaccard >= θ OR second identifier.
        #
        # Rule 5 (anti-FP from cluster_dealers pattern):
        #   cross-province without fingerprint → BLOCKED regardless of identifiers.

        if fp_ok:
            # Fingerprint dominates: accept regardless of province
            signals = ["fingerprint"]
            if phone_match:
                signals.append("phone")
            if website_match:
                signals.append("website")
            signal_str = "+".join(signals)
            prob = round(jaccard, 4)
            accepted_edges.append((uid_a, uid_b, signal_str, prob))
            if len(signals) == 1:
                n_fp_accepted += 1
            else:
                n_combo_accepted += 1

        elif phone_match and not phone_high_collision and not cross_province:
            # Clean phone signal, same province: accept
            accepted_edges.append((uid_a, uid_b, "phone", 1.0))
            n_ph_accepted += 1

        elif (
            phone_match
            and phone_high_collision
            and website_match
            and not website_high_collision  # website must be clean (non-high-collision)
            and not cross_province
        ):
            # Centralita phone + CLEAN website corroboration, same province: accept.
            # If website is also high-collision, we cannot trust either identifier alone.
            accepted_edges.append((uid_a, uid_b, "phone+website", 1.0))
            n_combo_accepted += 1

        elif website_match and not website_high_collision and not cross_province:
            # Clean website signal, same province: accept
            accepted_edges.append((uid_a, uid_b, "website", 1.0))
            n_web_accepted += 1

        else:
            # Blocked: insufficient signal or anti-FP guard triggered
            if not fp_ok and (phone_match or website_match) and cross_province:
                n_fp_blocked += 1
            else:
                n_id_blocked += 1

    log.info(
        "Accepted edges: %d  (fp=%d, phone=%d, web=%d, combo=%d)",
        len(accepted_edges),
        n_fp_accepted,
        n_ph_accepted,
        n_web_accepted,
        n_combo_accepted,
    )
    log.info(
        "Blocked: cross-province-without-fp=%d  insufficient-signal=%d  "
        "chain-siblings=%d  city-guard=%d",
        n_fp_blocked,
        n_id_blocked,
        n_chain_blocked,
        n_city_blocked,
    )
    return accepted_edges


# ---------------------------------------------------------------------------
# Canonical selection
# ---------------------------------------------------------------------------


def _richness(ent: dict) -> int:
    """Count non-null, non-empty key fields."""
    return sum(
        1
        for f in ("website", "phone", "municipality_code", "address", "cif", "lat")
        if ent.get(f) is not None and str(ent.get(f, "")).strip()
    )


def _select_canonical(
    members: list[str],
    entity_by_ulid: dict[str, dict],
) -> str:
    """Deterministic canonical selection.

    Priority (descending):
      1. Richness (more non-null key fields = better)
      2. n_vehicles (more vehicles = better representation)
      3. created_at (older = more established)
      4. entity_ulid ascending (lexicographic tiebreak)
    """
    def sort_key(uid: str) -> tuple:
        e = entity_by_ulid.get(uid, {})
        return (
            -_richness(e),
            -(e.get("n_vehicles") or 0),
            str(e.get("created_at") or "9999-99-99"),
            uid,
        )

    return min(members, key=sort_key)


# ---------------------------------------------------------------------------
# Cluster table builder
# ---------------------------------------------------------------------------


def _build_resolution_table(
    entities: list[dict],
    edges: list[EdgeType],
    b1_edges: list[tuple[str, str]] | None = None,
    org_map: dict[str, str | None] | None = None,
    ine_municipalities: frozenset[str] | None = None,
) -> tuple[list[dict], int]:
    """Apply constrained union-find over accepted edges → resolution rows.

    Uses ConstrainedUnionFind to propagate city/org constraints transitively,
    preventing over-merge via bridge entities (the A—C—B transitivity bug).

    §C: B1 edges are seeded FIRST (B1∘β composition), also through the
    constrained union so that cross-city B1 edges are rejected too.

    Edges are processed in descending confidence order:
      1. fingerprint+phone+website (highest)
      2. fingerprint+phone / fingerprint+website
      3. fingerprint
      4. phone+website
      5. phone / website
      6. B1 exact (after β, lower confidence — already geo-blocked upstream)

    Returns (resolution_rows, n_constrained_rejections).
    """
    entity_by_ulid: dict[str, dict] = {e["entity_ulid"]: e for e in entities}
    all_ulids = set(entity_by_ulid.keys())
    _org_map = org_map or {}

    log.info(
        "Running constrained union-find: %d entities, %d beta-edges, %d B1-edges ...",
        len(all_ulids),
        len(edges),
        len(b1_edges) if b1_edges else 0,
    )

    # Pre-compute city/org metadata for each entity for the constrained UF.
    # city_set: INE-validated city tokens from trade_name.
    #   IMPORTANT: only populated when ine_municipalities is provided (production).
    #   In legacy/test mode (ine_municipalities=None) city_set is always empty so
    #   the city constraint is inactive — the stopword-heuristic fallback in
    #   _build_edges already handles that path, and its output is pairwise-only.
    #   The constrained UF city constraint is a second-line defence against
    #   transitivity, which only makes sense with INE-validated tokens.
    # org_set: singleton {org_id} if org_id is not null, else empty.
    entity_city: dict[str, frozenset[str]] = {}
    entity_org: dict[str, frozenset[str]] = {}
    for e in entities:
        uid = e["entity_ulid"]
        if ine_municipalities is not None:
            entity_city[uid] = _city_tokens(e.get("trade_name"), ine_municipalities)
        else:
            entity_city[uid] = frozenset()
        org_id = _org_map.get(uid)
        entity_org[uid] = frozenset([org_id]) if org_id is not None else frozenset()

    cuf = ConstrainedUnionFind()
    for uid in all_ulids:
        cuf._init(uid, city=entity_city.get(uid, frozenset()), org=entity_org.get(uid, frozenset()))

    # ── Signal rank for ordering β edges (higher rank → applied first) ────────
    _SIGNAL_RANK: dict[str, int] = {
        "none": 0,
        "phone": 1,
        "website": 1,
        "phone+website": 2,
        "fingerprint": 3,
        "fingerprint+phone": 4,
        "fingerprint+website": 4,
        "fingerprint+phone+website": 5,
    }

    # Sort β edges descending by signal rank then by probability (both desc).
    sorted_edges = sorted(
        edges,
        key=lambda e: (_SIGNAL_RANK.get(e[2], 0), e[3]),
        reverse=True,
    )

    # ── Apply β edges (highest confidence first) ──────────────────────────────
    for uid_a, uid_b, _signal, _prob in sorted_edges:
        if uid_a in all_ulids and uid_b in all_ulids:
            cuf.constrained_union(uid_a, uid_b)

    # ── §C: seed B1 edges AFTER β (lower priority, also constrained) ─────────
    # NOTE: B1 is placed AFTER β so that the high-confidence β edges win
    # when there is a conflict with a cross-city B1 edge.
    n_b1_chain_blocked = 0
    if b1_edges:
        for uid_a, uid_b in b1_edges:
            if uid_a not in all_ulids or uid_b not in all_ulids:
                continue
            # Chain guard: skip if same non-null org (hard block, not constrained).
            oa = _org_map.get(uid_a)
            ob = _org_map.get(uid_b)
            if oa is not None and oa == ob:
                n_b1_chain_blocked += 1
                continue
            cuf.constrained_union(uid_a, uid_b)
        if n_b1_chain_blocked:
            log.info("B1 edges skipped (chain siblings): %d", n_b1_chain_blocked)

    n_rejected = cuf.n_constrained_rejections
    log.info(
        "ConstrainedUnionFind: %d unions rejected (city/org constraint)",
        n_rejected,
    )

    # ── Accumulate max signal/prob per root ───────────────────────────────────
    root_signal: dict[str, str] = {}
    root_prob: dict[str, float] = {}

    for uid_a, uid_b, signal, prob in edges:
        if uid_a not in all_ulids or uid_b not in all_ulids:
            continue
        root = cuf.find(uid_a)
        cur_rank = _SIGNAL_RANK.get(root_signal.get(root, "none"), 0)
        new_rank = _SIGNAL_RANK.get(signal, 0)
        if new_rank > cur_rank:
            root_signal[root] = signal
        if prob > root_prob.get(root, 0.0):
            root_prob[root] = prob

    components = cuf.components()
    result: list[dict] = []
    for _root, members in components.items():
        in_scope = [m for m in members if m in all_ulids]
        if not in_scope:
            continue
        canonical = _select_canonical(in_scope, entity_by_ulid)
        sz = len(in_scope)
        root = cuf.find(canonical)
        sig = root_signal.get(root, "none")
        prob = root_prob.get(root, None)
        if sz == 1:
            sig = "none"
            prob = None
        for uid in in_scope:
            result.append({
                "entity_ulid": uid,
                "resolved_dealer_ulid": canonical,
                "signal": sig,
                "probability": prob,
                "cluster_size": sz,
            })

    n_dealers = len({r["resolved_dealer_ulid"] for r in result})
    log.info("Union-find: %d rows, %d resolved dealers", len(result), n_dealers)
    return result, n_rejected


# ---------------------------------------------------------------------------
# PG write (idempotent)
# ---------------------------------------------------------------------------


def _write_to_pg(
    conn: Any,
    resolution_rows: list[dict],
    n_in: int,
    notes: dict,
) -> None:
    """Write entity_resolution_run + entity_resolution in one transaction.

    Deletes any previous entity-resolution-fingerprint-v1 run first (idempotent).
    Does NOT touch entity rows.
    """
    n_resolved_dealers = len({r["resolved_dealer_ulid"] for r in resolution_rows})
    n_merged = n_in - n_resolved_dealers

    log.info(
        "Writing to PG: n_in=%d | n_resolved_dealers=%d | n_merged=%d",
        n_in,
        n_resolved_dealers,
        n_merged,
    )

    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM entity_resolution WHERE run_id = %s", (RUN_ID,)
            )
            cur.execute(
                "DELETE FROM entity_resolution_run WHERE run_id = %s", (RUN_ID,)
            )
            cur.execute(
                """
                INSERT INTO entity_resolution_run
                    (run_id, resolver, n_in, n_resolved_dealers, n_merged,
                     vam_verified, notes)
                VALUES (%s, %s, %s, %s, %s, FALSE, %s::jsonb)
                """,
                (
                    RUN_ID,
                    RESOLVER,
                    n_in,
                    n_resolved_dealers,
                    n_merged,
                    json.dumps(notes),
                ),
            )

            rows_to_insert = [
                (
                    RUN_ID,
                    r["entity_ulid"],
                    r["resolved_dealer_ulid"],
                    r["signal"],
                    r["probability"],
                )
                for r in resolution_rows
            ]
            psycopg2.extras.execute_values(
                cur,
                """
                INSERT INTO entity_resolution
                    (run_id, entity_ulid, resolved_dealer_ulid, signal, probability)
                VALUES %s
                """,
                rows_to_insert,
                template="(%s, %s, %s, %s, %s)",
                page_size=5000,
            )

    log.info("Write committed. run_id=%s", RUN_ID)


# ---------------------------------------------------------------------------
# Verification and reporting
# ---------------------------------------------------------------------------


def _verify_and_report(conn: Any) -> None:
    """Print run stats, signal breakdown, 20-pair sample, anti-over-merge check."""
    log.info("=== ENTITY RESOLUTION BETA REPORT (%s) ===", RUN_ID)

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

        # 0. Run-level stats
        cur.execute(
            """
            SELECT n_in, n_resolved_dealers, n_merged, notes
            FROM entity_resolution_run
            WHERE run_id = %s
            """,
            (RUN_ID,),
        )
        run = cur.fetchone()
        pct = round(100.0 * run["n_merged"] / run["n_in"], 2) if run["n_in"] else 0
        print(
            f"\n--- RUN STATS ({RUN_ID}) ---\n"
            f"  n_in               : {run['n_in']}\n"
            f"  n_resolved_dealers : {run['n_resolved_dealers']}  "
            f"<= S_obs (dealers profesionales unicos derivados)\n"
            f"  n_merged           : {run['n_merged']} ({pct}% colapso)\n"
            f"  notes              : {run['notes']}\n"
        )

        # 1. Signal breakdown
        cur.execute(
            """
            SELECT signal, COUNT(*) as n_entities,
                   COUNT(DISTINCT resolved_dealer_ulid) as n_dealers
            FROM entity_resolution
            WHERE run_id = %s
            GROUP BY signal
            ORDER BY n_entities DESC
            """,
            (RUN_ID,),
        )
        print("--- SIGNAL BREAKDOWN ---")
        for r in cur.fetchall():
            print(
                f"  signal={r['signal']!r:35s}  "
                f"entities={r['n_entities']:>7,}  "
                f"dealers={r['n_dealers']:>7,}"
            )
        print()

        # 2. Cluster size distribution
        cur.execute(
            """
            SELECT cluster_size, COUNT(*) as n_dealers
            FROM (
                SELECT resolved_dealer_ulid,
                       COUNT(*) as cluster_size
                FROM entity_resolution
                WHERE run_id = %s
                GROUP BY resolved_dealer_ulid
            ) sub
            GROUP BY cluster_size
            ORDER BY cluster_size
            LIMIT 20
            """,
            (RUN_ID,),
        )
        print("--- CLUSTER SIZE DISTRIBUTION ---")
        for r in cur.fetchall():
            print(f"  size={r['cluster_size']:>3d}  n_dealers={r['n_dealers']:>7,}")
        print()

        # 3. 20-pair sample — cross-source pairs with evidence
        cur.execute(
            """
            WITH merged AS (
                SELECT
                    er.resolved_dealer_ulid,
                    er.signal,
                    er.probability,
                    e.entity_ulid,
                    e.trade_name,
                    e.kind,
                    e.province_code,
                    ARRAY_AGG(DISTINCT es.source_key ORDER BY es.source_key) AS source_keys,
                    COUNT(DISTINCT v.vehicle_ulid) AS n_vehicles,
                    ROW_NUMBER() OVER (
                        PARTITION BY er.resolved_dealer_ulid
                        ORDER BY e.entity_ulid ASC
                    ) AS rn
                FROM entity_resolution er
                JOIN entity e ON e.entity_ulid = er.entity_ulid
                LEFT JOIN entity_source es ON es.entity_ulid = e.entity_ulid
                LEFT JOIN vehicle v ON v.entity_ulid = e.entity_ulid
                WHERE er.run_id = %s
                  AND er.signal <> 'none'
                GROUP BY er.resolved_dealer_ulid, er.signal, er.probability,
                         e.entity_ulid, e.trade_name, e.kind, e.province_code
            ),
            cross_source_pairs AS (
                SELECT a.resolved_dealer_ulid,
                       a.signal, a.probability,
                       a.entity_ulid AS ea, a.trade_name AS name_a,
                       a.source_keys AS src_a, a.n_vehicles AS n_a,
                       b.entity_ulid AS eb, b.trade_name AS name_b,
                       b.source_keys AS src_b, b.n_vehicles AS n_b
                FROM merged a
                JOIN merged b ON b.resolved_dealer_ulid = a.resolved_dealer_ulid
                    AND b.rn = 2
                WHERE a.rn = 1
                  AND a.source_keys[1] <> b.source_keys[1]  -- cross-source
            )
            SELECT * FROM cross_source_pairs
            ORDER BY probability DESC NULLS LAST
            LIMIT 20
            """,
            (RUN_ID,),
        )
        pairs = cur.fetchall()
        print("--- 20-PAIR SAMPLE (cross-source, Director VAM) ---")
        for i, p in enumerate(pairs, 1):
            print(
                f"\n  [{i:02d}] signal={p['signal']}  "
                f"J={p['probability']}\n"
                f"        A: [{','.join(p['src_a'] or [])}] "
                f"'{p['name_a']}' ({p['n_a']} coches)\n"
                f"        B: [{','.join(p['src_b'] or [])}] "
                f"'{p['name_b']}' ({p['n_b']} coches)"
            )
        print()

        # 4. Anti-over-merge check: top 15 largest clusters
        cur.execute(
            """
            SELECT
                er.resolved_dealer_ulid,
                rd.trade_name AS canonical_name,
                COUNT(*) AS cluster_size,
                COUNT(DISTINCT e.province_code) AS n_provinces,
                ARRAY_AGG(DISTINCT e.province_code ORDER BY e.province_code)
                    FILTER (WHERE e.province_code IS NOT NULL) AS provinces,
                ARRAY_AGG(DISTINCT es.source_key ORDER BY es.source_key)
                    FILTER (WHERE es.source_key IS NOT NULL) AS sources,
                MAX(er.signal) AS signal
            FROM entity_resolution er
            JOIN entity e ON e.entity_ulid = er.entity_ulid
            JOIN entity rd ON rd.entity_ulid = er.resolved_dealer_ulid
            LEFT JOIN entity_source es ON es.entity_ulid = e.entity_ulid
            WHERE er.run_id = %s
            GROUP BY er.resolved_dealer_ulid, rd.trade_name
            ORDER BY cluster_size DESC
            LIMIT 15
            """,
            (RUN_ID,),
        )
        top15 = cur.fetchall()
        print("--- TOP 15 LARGEST CLUSTERS (anti-over-merge audit) ---")
        for row in top15:
            print(
                f"  canonical='{row['canonical_name']}'  "
                f"size={row['cluster_size']}  "
                f"provinces={row['n_provinces']}  "
                f"signal={row['signal']}\n"
                f"    sources={row['sources']}\n"
                f"    province_list={row['provinces']}"
            )
        print()

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
        # Step 1: Load P-stratum entities (now includes org_id)
        entities = _load_p_entities(conn)
        n_in = len(entities)
        entity_ulids = [e["entity_ulid"] for e in entities]
        all_ulids = set(entity_ulids)

        # Build org_map for chain guard reuse in _build_resolution_table
        org_map: dict[str, str | None] = {
            e["entity_ulid"]: e.get("org_id") for e in entities
        }

        # Step 2: Load inventory fingerprints (B7, used-car canonicals only)
        fingerprints = _load_fingerprints(conn, entity_ulids)

        # Step 3: Load INE municipality set for city-guard (§B Guard 2)
        ine_municipalities = _load_ine_municipalities(conn)

        # Step 4: Load B1 edges for seeding (§C)
        b1_edges = _load_b1_edges(conn, all_ulids)

        # Step 5: Build and adjudicate candidate β edges (with chain guard §B)
        edges = _build_edges(entities, fingerprints, ine_municipalities=ine_municipalities)

        # Step 6: Constrained union-find → resolution rows (β first, then B1)
        resolution_rows, n_constrained_rejections = _build_resolution_table(
            entities,
            edges,
            b1_edges=b1_edges,
            org_map=org_map,
            ine_municipalities=ine_municipalities,
        )

        assert len(resolution_rows) == n_in, (
            f"Row count mismatch: {len(resolution_rows)} != {n_in}"
        )

        # Step 7: Collect notes for audit
        signal_counts: dict[str, int] = defaultdict(int)
        for r in resolution_rows:
            signal_counts[r["signal"]] += 1

        notes = {
            "jaccard_theta": JACCARD_THETA,
            "max_entity_collision_k": MAX_ENTITY_COLLISION_K,
            "max_phone_collision_k": MAX_PHONE_COLLISION_K,
            "vehicle_cluster_run": VEHICLE_CLUSTER_RUN,
            "dealer_cluster_run": DEALER_CLUSTER_RUN,
            "b1_edges_seeded": len(b1_edges),
            "n_constrained_rejections": n_constrained_rejections,
            "signal_counts": dict(signal_counts),
        }

        # Step 8: Write to PG (idempotent, single transaction)
        _write_to_pg(conn, resolution_rows, n_in, notes)

        # Step 9: Verify (read-only)
        conn.autocommit = True
        _verify_and_report(conn)

    except Exception:
        log.exception("Fatal error in entity-resolution-fingerprint-v1 pipeline")
        raise
    finally:
        conn.close()
        log.info("PG connection closed.")


if __name__ == "__main__":
    main()
