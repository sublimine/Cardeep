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

  4. BLOCKING (O(n²) viable for P ~59k):
     - Fingerprint block: entities sharing at least 1 used-car canonical_vehicle_ulid
       → candidate pair (only within block, no full cartesian product).
     - Phone block: normalized phone token → candidate pair.
     - Website block: domain token → candidate pair.
     Pairwise adjudication only inside blocks.

  5. UNION-FIND: deterministic transitive closure over accepted edges.
     Canonical: richest entity (highest field count) → most vehicles → oldest
     created_at → lexicographic entity_ulid (deterministic tiebreak).

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
# Data loading
# ---------------------------------------------------------------------------


def _load_p_entities(conn: Any) -> list[dict]:
    """Load all P-stratum entities with their source keys."""
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
            ARRAY_AGG(DISTINCT es.source_key ORDER BY es.source_key)
                FILTER (WHERE es.source_key IS NOT NULL) AS source_keys,
            COUNT(DISTINCT v.vehicle_ulid) AS n_vehicles
        FROM entity e
        LEFT JOIN entity_source es ON es.entity_ulid = e.entity_ulid
        LEFT JOIN vehicle v ON v.entity_ulid = e.entity_ulid
        WHERE e.kind IN ('compraventa', 'concesionario_oficial', 'garaje')
        GROUP BY e.entity_ulid, e.cdp_code, e.trade_name, e.kind,
                 e.province_code, e.municipality_code, e.phone, e.website,
                 e.created_at
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
) -> list[EdgeType]:
    """Build all accepted merger edges with their signals.

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

    for pair in all_candidates:
        uid_a, uid_b = pair
        ea = entity_by_ulid[uid_a]
        eb = entity_by_ulid[uid_b]

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

        # Adjudication rules:
        #
        # Rule 1: fingerprint alone is sufficient IF Jaccard >= θ.
        #   No source-equality constraint: the whole point is cross-source merge.
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
        "Blocked: cross-province-without-fp=%d  insufficient-signal=%d",
        n_fp_blocked,
        n_id_blocked,
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
) -> list[dict]:
    """Apply union-find over accepted edges → resolution rows.

    For each entity: which canonical dealer it resolves to,
    the strongest signal in its component, and the max Jaccard in the component.
    """
    entity_by_ulid: dict[str, dict] = {e["entity_ulid"]: e for e in entities}
    all_ulids = set(entity_by_ulid.keys())

    log.info(
        "Running union-find: %d entities, %d edges ...",
        len(all_ulids),
        len(edges),
    )
    uf = UnionFind()
    for uid in all_ulids:
        uf._init(uid)
    for uid_a, uid_b, _signal, _prob in edges:
        if uid_a in all_ulids and uid_b in all_ulids:
            uf.union(uid_a, uid_b)

    # Accumulate max probability per root (for signal reporting)
    root_signal: dict[str, str] = {}
    root_prob: dict[str, float] = {}
    _SIGNAL_RANK = {
        "none": 0,
        "phone": 1,
        "website": 1,
        "phone+website": 2,
        "fingerprint": 3,
        "fingerprint+phone": 4,
        "fingerprint+website": 4,
        "fingerprint+phone+website": 5,
    }

    for uid_a, uid_b, signal, prob in edges:
        if uid_a not in all_ulids or uid_b not in all_ulids:
            continue
        root = uf.find(uid_a)
        cur_rank = _SIGNAL_RANK.get(root_signal.get(root, "none"), 0)
        new_rank = _SIGNAL_RANK.get(signal, 0)
        if new_rank > cur_rank:
            root_signal[root] = signal
        if prob > root_prob.get(root, 0.0):
            root_prob[root] = prob

    components = uf.components()
    result: list[dict] = []
    for _root, members in components.items():
        in_scope = [m for m in members if m in all_ulids]
        if not in_scope:
            continue
        canonical = _select_canonical(in_scope, entity_by_ulid)
        sz = len(in_scope)
        root = uf.find(canonical)
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
    return result


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
        # Step 1: Load P-stratum entities
        entities = _load_p_entities(conn)
        n_in = len(entities)
        entity_ulids = [e["entity_ulid"] for e in entities]

        # Step 2: Load inventory fingerprints (B7, used-car canonicals only)
        fingerprints = _load_fingerprints(conn, entity_ulids)

        # Step 3: Build and adjudicate candidate edges
        edges = _build_edges(entities, fingerprints)

        # Step 4: Union-find → resolution rows
        resolution_rows = _build_resolution_table(entities, edges)

        assert len(resolution_rows) == n_in, (
            f"Row count mismatch: {len(resolution_rows)} != {n_in}"
        )

        # Step 5: Collect notes for audit
        signal_counts: dict[str, int] = defaultdict(int)
        for r in resolution_rows:
            signal_counts[r["signal"]] += 1

        notes = {
            "jaccard_theta": JACCARD_THETA,
            "max_entity_collision_k": MAX_ENTITY_COLLISION_K,
            "max_phone_collision_k": MAX_PHONE_COLLISION_K,
            "vehicle_cluster_run": VEHICLE_CLUSTER_RUN,
            "signal_counts": dict(signal_counts),
        }

        # Step 6: Write to PG (idempotent, single transaction)
        _write_to_pg(conn, resolution_rows, n_in, notes)

        # Step 7: Verify (read-only)
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
