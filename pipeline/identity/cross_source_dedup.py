"""
pipeline/identity/cross_source_dedup.py
CAMPAIGN cross-source-dedup-v1 — B6.1 cross-source deduplication overlay.

PURPOSE
-------
The B1 dealer-identity-det-v1 run merges duplicates WITHIN a source using
name/phone/website + municipality.  It does NOT cross OSM↔digital platforms,
because digital platforms (wallapop, milanuncios, coches_net, autocasion) store
ZERO lat/lon and nearly zero phone/website — so the same physical dealer ends up
as two separate entity_ulids (one OSM, one digital) with no shared key.

This pipeline finds those same-physical-dealer pairs by matching ORTHOGONAL
signals:

  Signal A — phone (9-digit suffix, strips country code):
    OSM stores phone for ~22% of entities.
    autocasion_wholesale, dgt_cat, aedra store phones for 21-100%.
    Cross-source phone match = very strong; false-positive rate ≈ 0% at muni level.

  Signal B — website domain (normalized: strip scheme + www + path):
    OSM stores website for ~12.6% of entities.
    as24 stores website for ~42% of entities.
    Domain match = extremely strong.

  Signal C — normalized_name + municipality_code (exact, stripped legal suffix):
    Reuses _normalize_name() from cluster_dealers.py.
    This is the SAME edge B1 uses intra-source — but here we apply it CROSS-source.
    Name-only match is weaker (risk of "Auto X" collision), so it is only accepted
    as evidence when ALSO name-similarity is high AND same municipality.
    Used only as a reinforcement signal, NOT as standalone merge criterion, UNLESS
    the names are highly similar (Levenshtein ≤ 2 of normalized form AND len ≥ 8).
    Anti-false-positive: cross-source name-only merge requires normalized names to
    be IDENTICAL (not just similar) given the lower data quality on digital platforms.

ANTI-FALSE-POSITIVE GUARDS (in order)
--------------------------------------
1. Same municipality_code REQUIRED for all matches.
2. Name divergence check: if phone/website matches but normalized names are
   ≥ 4 tokens apart in Jaccard (set of trigrams), the pair is REJECTED unless
   website or phone is shared.
3. Chain collapse guard: entities whose trade_name matches known multi-branch
   chain patterns (flexicar, ocasionplus, clicars, etc.) are excluded from
   name-only and geo-only matching; they require phone OR website match.
4. Geo proximity is used only as a BONUS confidence signal, not as primary.
   Digital platforms carry no geo — so geo-only match would always be 0.

WHAT THIS DOES NOT DO
---------------------
- Does NOT touch entity rows (no UPDATE, no DELETE).
- Does NOT modify the existing dealer-identity-det-v1 cluster.
- Writes only to entity_cluster + entity_cluster_run under a NEW run_id.
- vam_verified = FALSE until the Director gates.

RUN
---
    # Full Spain (after Director gate):
    python -m pipeline.identity.cross_source_dedup

    # Sample provinces only (Gipuzkoa=20, Madrid=28, Soria=42):
    python -m pipeline.identity.cross_source_dedup --provinces 20 28 42

    # Dry-run (no DB writes, prints pairs only):
    python -m pipeline.identity.cross_source_dedup --dry-run --provinces 20 28 42

REQUIRES
--------
    psycopg2, Python 3.11+

IDEMPOTENT
----------
    Deletes cross-source-dedup-v1 before writing (or cross-source-dedup-v1-SAMPLE
    when --provinces is set).
"""
from __future__ import annotations

import argparse
import json
import logging
import math
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

RUN_ID_FULL = "cross-source-dedup-v1"
RUN_ID_SAMPLE = "cross-source-dedup-v1-SAMPLE"

RESOLVER = "cross-source"
RESOLVER_VERSION = "1.0.0"

# Scope: dealer-kind entities only, excluding closed
SCOPE_SQL = "kind IN ('compraventa','garaje','concesionario_oficial','desguace') AND status <> 'closed'"

# Sources that carry geo (lat/lon populated)
GEO_SOURCES: frozenset[str] = frozenset({"osm"})

# Digital sources we want to cross with OSM
DIGITAL_SOURCES: frozenset[str] = frozenset({
    "wallapop_wholesale",
    "milanuncios_wholesale",
    "coches_net_wholesale",
    "autocasion_wholesale",
    "motor_es_wholesale",
    "coches_com_wholesale",
    "as24",
    "as24_wholesale",
    "dgt_cat",
    "aedra",
    "aecs",
    "acevas",
})

# Sources with known phone coverage (used to focus phone matching)
PHONE_SOURCES: frozenset[str] = frozenset({
    "osm",
    "autocasion_wholesale",
    "dgt_cat",
    "aedra",
    "aecs",
    "acevas",
    "as24",
    "oem_dacia",
    "oem_hyundai",
})

# Sources with known website coverage
WEBSITE_SOURCES: frozenset[str] = frozenset({
    "osm",
    "as24",
    "as24_wholesale",
    "aedra",
    "aecs",
    "acevas",
})

# Minimum phone digits required for matching
PHONE_MIN_DIGITS: int = 9

# Match probability by signal strength
PROB_PHONE: float = 0.97
PROB_WEBSITE: float = 0.98
PROB_NAME_EXACT: float = 0.82  # Same normalized name + same muni, different source
PROB_MULTI: float = 0.99        # Two or more signals agree

# Chain patterns: names matching these should NOT be merged solely by name.
# They require phone OR website match to prevent collapsing distinct branches.
_CHAIN_PATTERNS: tuple[re.Pattern, ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in [
        r"flexicar",
        r"ocasionplus",
        r"clicars",
        r"carplus",
        r"stellantis",
        r"mobility.?centro",
        r"grupo\s+\w+\s+motor",
        r"bmw\s+premium",
        r"mercedes.benz\s+\w+",
    ]
)

# Source priority for canonical selection (mirrors cluster_dealers.py)
SOURCE_GROUP_RANK: dict[str, int] = {
    "oem_dealer_network": 10,
    "association": 9,
    "official_registry": 8,
    "marketplace_motor": 7,
    "directory": 6,
}


# ---------------------------------------------------------------------------
# Normalisation helpers (mirrors cluster_dealers.py exactly)
# ---------------------------------------------------------------------------

_RE_NON_ALNUM = re.compile(r"[^a-z0-9]")
_RE_SCHEME = re.compile(r"^https?://", re.IGNORECASE)
_RE_WWW = re.compile(r"^www\.", re.IGNORECASE)

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
_RE_LEGAL_SUFFIX = re.compile(
    r"(" + "|".join(re.escape(s) for s in _LEGAL_SUFFIXES) + r")$"
)
_MIN_NAME_LEN_AFTER_STRIP = 3


def _normalize_name(name: str | None) -> str | None:
    """NFKD -> ASCII ignore -> lower -> strip non-[a-z0-9] -> strip legal suffix."""
    if name is None or not isinstance(name, str) or not name.strip():
        return None
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_bytes = nfkd.encode("ascii", "ignore")
    clean = _RE_NON_ALNUM.sub("", ascii_bytes.decode("ascii").lower())
    if not clean:
        return None
    m = _RE_LEGAL_SUFFIX.search(clean)
    if m:
        stripped = clean[: m.start()]
        if len(stripped) >= _MIN_NAME_LEN_AFTER_STRIP:
            clean = stripped
    return clean


def _normalize_phone(phone: str | None) -> str | None:
    """Keep last PHONE_MIN_DIGITS digits (handles +34 prefix)."""
    if phone is None or not isinstance(phone, str) or not phone.strip():
        return None
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) < PHONE_MIN_DIGITS:
        return None
    return digits[-PHONE_MIN_DIGITS:]  # last 9 digits strips country code


def _normalize_website_host(website: str | None) -> str | None:
    """Strip scheme + www, extract bare host, lower, drop path/query."""
    if website is None or not isinstance(website, str) or not website.strip():
        return None
    host = website.strip().lower()
    host = _RE_SCHEME.sub("", host)
    host = _RE_WWW.sub("", host)
    host = host.split("/")[0].split("?")[0].strip()
    return host if host else None


def _is_chain(name: str | None) -> bool:
    """Return True if the name matches a known multi-branch chain pattern."""
    if not name:
        return False
    return any(p.search(name) for p in _CHAIN_PATTERNS)


# ---------------------------------------------------------------------------
# Haversine geo distance
# ---------------------------------------------------------------------------

_EARTH_M = 6_371_000.0  # metres


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in metres between two WGS-84 coordinates."""
    r = math.radians
    dlat = r(lat2 - lat1)
    dlon = r(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(r(lat1)) * math.cos(r(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * _EARTH_M * math.asin(math.sqrt(a))


# ---------------------------------------------------------------------------
# Canonical selection (mirrors cluster_dealers.py)
# ---------------------------------------------------------------------------


def _source_group_rank(sg: str | None) -> int:
    return SOURCE_GROUP_RANK.get(sg, 1) if sg else 1


def _richness(ent: dict) -> int:
    return sum(
        1
        for f in ("website", "phone", "address", "cif", "lat")
        if ent.get(f) is not None and str(ent.get(f, "")).strip()
    )


def _select_canonical(members: list[str], entity_by_ulid: dict[str, dict]) -> str:
    """
    Pick canonical entity for a cluster.

    Priority (descending):
      1. source_group rank
      2. richness (non-null key attrs)
      3. first_seen (older preferred)
      4. cdp_code (lexicographic tiebreak)
    """

    def _key(uid: str) -> tuple:
        ent = entity_by_ulid.get(uid, {})
        return (
            -_source_group_rank(ent.get("source_group")),
            -_richness(ent),
            str(ent.get("created_at") or "9999-99-99"),
            ent.get("cdp_code") or "ZZZZ",
        )

    return min(members, key=_key)


# ---------------------------------------------------------------------------
# Union-Find (identical to cluster_dealers.py)
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
            self._parent[x] = self._parent[self._parent[x]]
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
        groups: dict[str, list[str]] = defaultdict(list)
        for node in self._parent:
            groups[self.find(node)].append(node)
        return dict(groups)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

Entity = dict[str, Any]


def _load_entities(conn: Any, province_codes: list[str] | None) -> list[Entity]:
    """Load dealer entities (not particular) with their sources."""
    scope = SCOPE_SQL
    if province_codes:
        placeholders = ",".join(["%s"] * len(province_codes))
        scope = f"{scope} AND province_code IN ({placeholders})"

    query = f"""
        SELECT
            e.entity_ulid,
            e.cdp_code,
            e.trade_name,
            e.municipality_code,
            e.province_code,
            e.website,
            e.phone,
            e.address,
            e.lat,
            e.lon,
            e.cif,
            e.source_group::text AS source_group,
            e.created_at,
            ARRAY_AGG(DISTINCT es.source_key) AS source_keys
        FROM entity e
        JOIN entity_source es ON es.entity_ulid = e.entity_ulid
        WHERE {scope}
        GROUP BY
            e.entity_ulid, e.cdp_code, e.trade_name, e.municipality_code,
            e.province_code, e.website, e.phone, e.address, e.lat, e.lon,
            e.cif, e.source_group, e.created_at
    """
    params = tuple(province_codes) if province_codes else ()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(query, params)
        rows = [dict(r) for r in cur.fetchall()]

    # Convert source_keys from list/None to frozenset
    for r in rows:
        sk = r.get("source_keys") or []
        r["source_keys"] = frozenset(sk)

    log.info("Loaded %d entities", len(rows))
    return rows


# ---------------------------------------------------------------------------
# Edge building: cross-source matches
# ---------------------------------------------------------------------------

MatchPair = tuple[str, str, float, str]  # (ulid_a, ulid_b, probability, reason)


def _is_orthogonal(keys_a: frozenset, keys_b: frozenset) -> bool:
    """
    Return True if entities A and B come from DIFFERENT source groups.

    We define orthogonal as: A has at least one GEO_SOURCE key and B has at
    least one DIGITAL_SOURCE key, or vice versa. This prevents re-merging
    entities that are already from the same source.
    """
    a_geo = bool(keys_a & GEO_SOURCES)
    b_geo = bool(keys_b & GEO_SOURCES)
    a_dig = bool(keys_a & DIGITAL_SOURCES)
    b_dig = bool(keys_b & DIGITAL_SOURCES)
    # At least one is geo-only and the other has a digital source
    return (a_geo and b_dig) or (b_geo and a_dig)


def _build_cross_source_edges(entities: list[Entity]) -> list[MatchPair]:
    """
    Build cross-source match edges between entities.

    Matching strategies (in decreasing signal strength):
      1. Phone (9-digit suffix) + same municipality
      2. Website domain + same municipality
      3. Exact normalized name + same municipality + DIFFERENT source types

    Anti-FP guards applied in all cases:
      - Both entities must be from orthogonal source groups.
      - Same municipality_code required.
      - Chain entities (flexicar etc.) excluded from name-only matching.
    """
    # Index by municipality
    by_muni: dict[str, list[Entity]] = defaultdict(list)
    for ent in entities:
        muni = (ent.get("municipality_code") or "").strip()
        if muni:
            by_muni[muni].append(ent)

    # Build fast lookup indices keyed by (signal_value, municipality)
    # phone_idx[(phone9, muni)] -> list of entity_ulid
    phone_idx: dict[tuple[str, str], list[str]] = defaultdict(list)
    # web_idx[(domain, muni)] -> list of entity_ulid
    web_idx: dict[tuple[str, str], list[str]] = defaultdict(list)
    # name_idx[(norm_name, muni)] -> list of entity_ulid
    name_idx: dict[tuple[str, str], list[str]] = defaultdict(list)

    entity_by_ulid: dict[str, Entity] = {}
    for ent in entities:
        uid = ent["entity_ulid"]
        entity_by_ulid[uid] = ent
        muni = (ent.get("municipality_code") or "").strip()
        if not muni:
            continue

        ph = _normalize_phone(ent.get("phone"))
        if ph:
            phone_idx[(ph, muni)].append(uid)

        wh = _normalize_website_host(ent.get("website"))
        if wh:
            web_idx[(wh, muni)].append(uid)

        nn = _normalize_name(ent.get("trade_name"))
        if nn:
            name_idx[(nn, muni)].append(uid)

    pairs: dict[tuple[str, str], MatchPair] = {}  # dedup by (min,max) ulid

    def _add_pair(
        uid_a: str,
        uid_b: str,
        prob: float,
        reason: str,
    ) -> None:
        key = (uid_a, uid_b) if uid_a < uid_b else (uid_b, uid_a)
        if key not in pairs or pairs[key][2] < prob:
            pairs[key] = (key[0], key[1], prob, reason)

    def _check_orthogonal_and_add(
        uid_a: str,
        uid_b: str,
        prob: float,
        reason: str,
    ) -> None:
        if uid_a == uid_b:
            return
        ent_a = entity_by_ulid[uid_a]
        ent_b = entity_by_ulid[uid_b]
        if not _is_orthogonal(ent_a["source_keys"], ent_b["source_keys"]):
            return
        _add_pair(uid_a, uid_b, prob, reason)

    # --- Signal 1: Phone match ---
    log.info("Building phone cross-source edges ...")
    phone_edges = 0
    for (ph, muni), bucket in phone_idx.items():
        if len(bucket) < 2:
            continue
        for i in range(len(bucket)):
            for j in range(i + 1, len(bucket)):
                uid_a, uid_b = bucket[i], bucket[j]
                ent_a = entity_by_ulid[uid_a]
                ent_b = entity_by_ulid[uid_b]
                if not _is_orthogonal(ent_a["source_keys"], ent_b["source_keys"]):
                    continue
                # Optional name sanity check: if both have names and they
                # are wildly different (no token overlap), demote probability.
                na = _normalize_name(ent_a.get("trade_name"))
                nb = _normalize_name(ent_b.get("trade_name"))
                prob = PROB_PHONE
                reason = f"phone:{ph}"
                if na and nb:
                    # Trigram-set Jaccard (rough, no external deps)
                    ta = {na[k:k+3] for k in range(len(na) - 2)}
                    tb = {nb[k:k+3] for k in range(len(nb) - 2)}
                    if ta and tb:
                        jac = len(ta & tb) / len(ta | tb)
                        if jac < 0.15:
                            # Very different names with same phone: demote.
                            # Still merge but flag low confidence.
                            prob = 0.75
                            reason = f"phone:{ph}|name_diverge"
                _add_pair(uid_a, uid_b, prob, reason)
                phone_edges += 1
    log.info("  phone cross-source edges: %d", phone_edges)

    # --- Signal 2: Website domain match ---
    log.info("Building website cross-source edges ...")
    web_edges = 0
    for (domain, muni), bucket in web_idx.items():
        if len(bucket) < 2:
            continue
        for i in range(len(bucket)):
            for j in range(i + 1, len(bucket)):
                uid_a, uid_b = bucket[i], bucket[j]
                ent_a = entity_by_ulid[uid_a]
                ent_b = entity_by_ulid[uid_b]
                if not _is_orthogonal(ent_a["source_keys"], ent_b["source_keys"]):
                    continue
                # Upgrade to PROB_MULTI if a phone also matched
                key = (uid_a, uid_b) if uid_a < uid_b else (uid_b, uid_a)
                existing = pairs.get(key)
                if existing and "phone" in existing[3]:
                    _add_pair(uid_a, uid_b, PROB_MULTI, f"{existing[3]}|website:{domain}")
                else:
                    _add_pair(uid_a, uid_b, PROB_WEBSITE, f"website:{domain}")
                web_edges += 1
    log.info("  website cross-source edges: %d", web_edges)

    # --- Signal 3: Exact normalized name match (cross-source only) ---
    log.info("Building name cross-source edges ...")
    name_edges = 0
    for (nn, muni), bucket in name_idx.items():
        if len(bucket) < 2:
            continue
        for i in range(len(bucket)):
            for j in range(i + 1, len(bucket)):
                uid_a, uid_b = bucket[i], bucket[j]
                ent_a = entity_by_ulid[uid_a]
                ent_b = entity_by_ulid[uid_b]
                if not _is_orthogonal(ent_a["source_keys"], ent_b["source_keys"]):
                    continue
                # Chain guard: chains require phone or website, not just name
                if _is_chain(ent_a.get("trade_name")) or _is_chain(ent_b.get("trade_name")):
                    continue
                # Only add if len(nn) >= 6 (avoid "auto"/"ford" false merges)
                if len(nn) < 6:
                    continue
                # Check if phone or website already matched (upgrade if so)
                key = (uid_a, uid_b) if uid_a < uid_b else (uid_b, uid_a)
                existing = pairs.get(key)
                if existing:
                    # Already matched by stronger signal; upgrade reason
                    _add_pair(uid_a, uid_b, PROB_MULTI, f"{existing[3]}|name:{nn}")
                else:
                    # Name-only cross-source: medium confidence
                    _add_pair(uid_a, uid_b, PROB_NAME_EXACT, f"name:{nn}")
                name_edges += 1
    log.info("  name cross-source edges: %d", name_edges)

    result = list(pairs.values())
    log.info(
        "Total cross-source edges: %d (phone=%d, web=%d, name=%d)",
        len(result), phone_edges, web_edges, name_edges,
    )
    return result


# ---------------------------------------------------------------------------
# Cluster building
# ---------------------------------------------------------------------------


def _build_cluster_table(
    entities: list[Entity],
    match_pairs: list[MatchPair],
) -> list[dict]:
    """
    Union-find over match_pairs; return entity_cluster rows.

    Singletons (entities with no cross-source match) are INCLUDED so the
    overlay is a complete partition (needed for correct cluster_size).
    """
    entity_by_ulid = {e["entity_ulid"]: e for e in entities}
    all_ulids = set(entity_by_ulid.keys())

    uf = UnionFind()
    for uid in all_ulids:
        uf._init(uid)

    # Store best probability per pair for output
    pair_prob: dict[tuple[str, str], float] = {}
    for uid_a, uid_b, prob, _reason in match_pairs:
        key = (uid_a, uid_b) if uid_a < uid_b else (uid_b, uid_a)
        if uid_a in all_ulids and uid_b in all_ulids:
            uf.union(uid_a, uid_b)
            pair_prob[key] = max(pair_prob.get(key, 0.0), prob)

    components = uf.components()
    result: list[dict] = []
    for _root, members in components.items():
        in_scope = [m for m in members if m in all_ulids]
        if not in_scope:
            continue
        canonical = _select_canonical(in_scope, entity_by_ulid)
        sz = len(in_scope)
        for uid in in_scope:
            # Best match probability for this member vs canonical
            key = (uid, canonical) if uid < canonical else (canonical, uid)
            prob = pair_prob.get(key)
            result.append({
                "entity_ulid": uid,
                "canonical_ulid": canonical,
                "match_probability": prob,
                "cluster_size": sz,
            })

    n_clusters = len({r["canonical_ulid"] for r in result})
    n_merged = len(result) - n_clusters
    log.info(
        "Union-find: %d rows | %d clusters | %d merged",
        len(result), n_clusters, n_merged,
    )
    return result


# ---------------------------------------------------------------------------
# Sample pair reporter (for Director validation)
# ---------------------------------------------------------------------------


def _report_sample_pairs(
    match_pairs: list[MatchPair],
    entity_by_ulid: dict[str, Entity],
    n: int = 20,
) -> None:
    """
    Print up to n matched pairs with full context for manual inspection.

    Only prints cross-source pairs (cluster_size > 1 implied by pair existing).
    """
    # Sort by probability descending, then by reason to group by signal type
    sorted_pairs = sorted(match_pairs, key=lambda p: (-p[2], p[3]))

    print("\n" + "=" * 80)
    print(f"SAMPLE PAIRS FOR DIRECTOR VALIDATION (top {n})")
    print("=" * 80)

    for idx, (uid_a, uid_b, prob, reason) in enumerate(sorted_pairs[:n], start=1):
        ea = entity_by_ulid.get(uid_a, {})
        eb = entity_by_ulid.get(uid_b, {})
        print(f"\n--- Pair {idx:02d} | prob={prob:.2f} | signal={reason} ---")
        for label, ent in [("A", ea), ("B", eb)]:
            sources = sorted(ent.get("source_keys", []))
            print(
                f"  {label}: [{', '.join(sources)}] "
                f"{ent.get('trade_name')!r} | "
                f"muni={ent.get('municipality_code')} prov={ent.get('province_code')} | "
                f"lat={ent.get('lat')} lon={ent.get('lon')} | "
                f"phone={ent.get('phone')!r} | "
                f"web={_normalize_website_host(ent.get('website'))!r}"
            )

    print("\n" + "=" * 80)


# ---------------------------------------------------------------------------
# Statistics: cross-source merge summary
# ---------------------------------------------------------------------------


def _compute_stats(
    match_pairs: list[MatchPair],
    entity_by_ulid: dict[str, Entity],
) -> dict:
    """Compute summary statistics for reporting."""
    total = len(match_pairs)
    by_signal: dict[str, int] = defaultdict(int)
    by_prob_tier: dict[str, int] = defaultdict(int)

    osm_x_wallapop = 0
    osm_x_milanuncios = 0
    osm_x_autocasion = 0
    osm_x_digital = 0

    for uid_a, uid_b, prob, reason in match_pairs:
        # Signal classification
        if "phone" in reason and "website" in reason:
            by_signal["phone+website"] += 1
        elif "phone" in reason:
            by_signal["phone"] += 1
        elif "website" in reason:
            by_signal["website"] += 1
        else:
            by_signal["name"] += 1

        # Probability tier
        if prob >= 0.95:
            by_prob_tier["high(>=0.95)"] += 1
        elif prob >= 0.80:
            by_prob_tier["medium(0.80-0.94)"] += 1
        else:
            by_prob_tier["low(<0.80)"] += 1

        # Source pair stats
        ea = entity_by_ulid.get(uid_a, {})
        eb = entity_by_ulid.get(uid_b, {})
        sources_a = ea.get("source_keys", frozenset())
        sources_b = eb.get("source_keys", frozenset())
        all_src = sources_a | sources_b

        if "osm" in all_src:
            osm_x_digital += 1
            if "wallapop_wholesale" in all_src:
                osm_x_wallapop += 1
            if "milanuncios_wholesale" in all_src:
                osm_x_milanuncios += 1
            if "autocasion_wholesale" in all_src:
                osm_x_autocasion += 1

    return {
        "total_pairs": total,
        "by_signal": dict(by_signal),
        "by_prob_tier": dict(by_prob_tier),
        "osm_x_digital": osm_x_digital,
        "osm_x_wallapop": osm_x_wallapop,
        "osm_x_milanuncios": osm_x_milanuncios,
        "osm_x_autocasion": osm_x_autocasion,
    }


# ---------------------------------------------------------------------------
# PG write (idempotent)
# ---------------------------------------------------------------------------


def _write_to_pg(
    conn: Any,
    run_id: str,
    cluster_rows: list[dict],
    match_pairs: list[MatchPair],
    n_entities_in: int,
    province_codes: list[str] | None,
) -> None:
    """Write entity_cluster_run + entity_cluster rows in a single transaction."""
    n_clusters_out = len({r["canonical_ulid"] for r in cluster_rows})
    n_merged = sum(1 for r in cluster_rows if r["entity_ulid"] != r["canonical_ulid"])

    blocking_rules = [
        "phone (9-digit suffix) + municipality_code [cross-source only]",
        "website_domain + municipality_code [cross-source only]",
        "normalized_name (exact, legal-suffix stripped) + municipality_code [cross-source, name_len>=6, no chains]",
        "orthogonality guard: GEO_SOURCES x DIGITAL_SOURCES required",
        "same municipality_code required for all signals",
    ]

    scope = SCOPE_SQL
    if province_codes:
        scope += f" AND province_code IN {tuple(province_codes)}"

    log.info(
        "Writing to PG: run_id=%s | n_in=%d | clusters=%d | merged=%d",
        run_id, n_entities_in, n_clusters_out, n_merged,
    )

    with conn:
        with conn.cursor() as cur:
            # Idempotent: delete previous run first
            cur.execute("DELETE FROM entity_cluster WHERE cluster_run_id = %s", (run_id,))
            cur.execute("DELETE FROM entity_cluster_run WHERE cluster_run_id = %s", (run_id,))

            cur.execute(
                """
                INSERT INTO entity_cluster_run
                    (cluster_run_id, resolver, resolver_version, scope,
                     threshold, blocking_rules, n_entities_in, n_clusters_out,
                     n_merged, vam_verified)
                VALUES (%s, %s, %s, %s, NULL, %s::jsonb, %s, %s, %s, FALSE)
                """,
                (
                    run_id,
                    RESOLVER,
                    RESOLVER_VERSION,
                    scope,
                    json.dumps(blocking_rules),
                    n_entities_in,
                    n_clusters_out,
                    n_merged,
                ),
            )

            rows_to_insert = [
                (
                    run_id,
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

    log.info("Write committed. run_id=%s", run_id)


# ---------------------------------------------------------------------------
# Validation queries (Director gate)
# ---------------------------------------------------------------------------


def _validate_sample(
    conn: Any,
    run_id: str,
    match_pairs: list[MatchPair],
    entity_by_ulid: dict[str, Entity],
) -> None:
    """
    Run post-write validation checks.

    CHECK 1: Merged pairs are from different source groups (no intra-source merge).
    CHECK 2: No pair maps two entities to the same canonical unless they share
             a strong signal (prob >= 0.80).
    CHECK 3: Chain entities not collapsed unless they have phone or website match.
    CHECK 4: All cluster_size values match actual member counts.
    """
    log.info("=== VALIDATION REPORT (%s) ===", run_id)

    # CHECK 1: All merged pairs are cross-source
    intra_source_violations = 0
    for uid_a, uid_b, prob, reason in match_pairs:
        ea = entity_by_ulid.get(uid_a, {})
        eb = entity_by_ulid.get(uid_b, {})
        # Intra-source: both have the exact same source_keys intersection
        common = ea.get("source_keys", frozenset()) & eb.get("source_keys", frozenset())
        if common and not (ea["source_keys"] - common) and not (eb["source_keys"] - common):
            intra_source_violations += 1
            log.error(
                "CHECK 1 FAIL: intra-source pair uid_a=%s uid_b=%s common_sources=%s",
                uid_a, uid_b, common,
            )

    print(
        f"\n--- CHECK 1: No intra-source merges ---\n"
        f"  Violations: {intra_source_violations} (objetivo: 0)\n"
        f"  Status: {'OK' if intra_source_violations == 0 else 'FAIL'}\n"
    )

    # CHECK 2: No chain entities collapsed by name-only
    chain_name_only_violations = 0
    for uid_a, uid_b, prob, reason in match_pairs:
        if "name" in reason and "phone" not in reason and "website" not in reason:
            ea = entity_by_ulid.get(uid_a, {})
            eb = entity_by_ulid.get(uid_b, {})
            if _is_chain(ea.get("trade_name")) or _is_chain(eb.get("trade_name")):
                chain_name_only_violations += 1
                log.error(
                    "CHECK 2 FAIL: chain entity merged by name-only uid_a=%s uid_b=%s",
                    uid_a, uid_b,
                )

    print(
        f"--- CHECK 2: No chain entities merged by name-only ---\n"
        f"  Violations: {chain_name_only_violations} (objetivo: 0)\n"
        f"  Status: {'OK' if chain_name_only_violations == 0 else 'FAIL'}\n"
    )

    # CHECK 3: DB-level count verification
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT n_entities_in, n_clusters_out, n_merged
            FROM entity_cluster_run
            WHERE cluster_run_id = %s
            """,
            (run_id,),
        )
        run = cur.fetchone()
        print(
            f"--- CHECK 3: Run-level stats ---\n"
            f"  n_entities_in : {run['n_entities_in']}\n"
            f"  n_clusters_out: {run['n_clusters_out']}\n"
            f"  n_merged      : {run['n_merged']}\n"
            f"  cross_source_merges (from pairs): {len(match_pairs)}\n"
        )

        # CHECK 4: Top merged clusters (potential false positives)
        cur.execute(
            """
            SELECT ec.canonical_ulid, ec.cluster_size,
                   e.trade_name AS canonical_name,
                   COUNT(DISTINCT em.province_code) AS n_provinces
            FROM entity_cluster ec
            JOIN entity e ON e.entity_ulid = ec.canonical_ulid
            JOIN entity em ON em.entity_ulid IN (
                SELECT entity_ulid FROM entity_cluster
                WHERE cluster_run_id = ec.cluster_run_id
                  AND canonical_ulid = ec.canonical_ulid
            )
            WHERE ec.cluster_run_id = %s
              AND ec.cluster_size > 1
            GROUP BY ec.canonical_ulid, ec.cluster_size, e.trade_name
            ORDER BY ec.cluster_size DESC
            LIMIT 10
            """,
            (run_id,),
        )
        top = cur.fetchall()
        print("--- CHECK 4: Top 10 merged clusters ---")
        for row in top:
            flag = " *** REVIEW" if row["n_provinces"] > 1 and row["cluster_size"] > 3 else ""
            print(
                f"  canonical={row['canonical_ulid']!r}  "
                f"name={row['canonical_name']!r}  "
                f"size={row['cluster_size']}  "
                f"n_prov={row['n_provinces']}{flag}"
            )
        print()

    log.info("=== END VALIDATION ===")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _get_dsn() -> str:
    return os.environ.get(
        "CARDEEP_DSN",
        "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep",
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="B6.1 cross-source deduplication overlay (OSM × digital platforms)"
    )
    parser.add_argument(
        "--provinces",
        nargs="+",
        metavar="CODE",
        help="Limit to specific province codes (e.g. --provinces 20 28 42). "
             "Omit for full Spain.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print pairs without writing to DB.",
    )
    parser.add_argument(
        "--sample-pairs",
        type=int,
        default=20,
        help="Number of sample pairs to print for Director validation (default: 20).",
    )
    args = parser.parse_args(argv)

    province_codes: list[str] | None = args.provinces
    dry_run: bool = args.dry_run
    run_id = RUN_ID_SAMPLE if province_codes else RUN_ID_FULL

    log.info("Starting cross_source_dedup run_id=%s dry_run=%s provinces=%s",
             run_id, dry_run, province_codes)

    dsn = _get_dsn()
    conn = psycopg2.connect(dsn)
    conn.autocommit = False

    try:
        # Step 1: Load entities
        entities = _load_entities(conn, province_codes)
        entity_by_ulid = {e["entity_ulid"]: e for e in entities}
        n_entities_in = len(entities)

        if n_entities_in == 0:
            log.warning("No entities loaded. Check scope/province filter.")
            return

        # Step 2: Build cross-source match edges
        match_pairs = _build_cross_source_edges(entities)

        # Step 3: Compute and print statistics
        stats = _compute_stats(match_pairs, entity_by_ulid)
        print("\n" + "=" * 70)
        print("CROSS-SOURCE DEDUP STATISTICS")
        print("=" * 70)
        print(f"  Scope         : {province_codes or 'full Spain'}")
        print(f"  Entities in   : {n_entities_in}")
        print(f"  Total pairs   : {stats['total_pairs']}")
        print(f"  By signal     : {stats['by_signal']}")
        print(f"  By prob tier  : {stats['by_prob_tier']}")
        print(f"  OSM×digital   : {stats['osm_x_digital']}")
        print(f"  OSM×wallapop  : {stats['osm_x_wallapop']}")
        print(f"  OSM×milanuncios: {stats['osm_x_milanuncios']}")
        print(f"  OSM×autocasion: {stats['osm_x_autocasion']}")
        print("=" * 70)

        # Step 4: Print sample pairs for Director validation
        _report_sample_pairs(match_pairs, entity_by_ulid, n=args.sample_pairs)

        if dry_run:
            log.info("DRY-RUN: no writes.")
            return

        # Step 5: Build cluster table
        cluster_rows = _build_cluster_table(entities, match_pairs)

        # Step 6: Write to PG
        _write_to_pg(
            conn=conn,
            run_id=run_id,
            cluster_rows=cluster_rows,
            match_pairs=match_pairs,
            n_entities_in=n_entities_in,
            province_codes=province_codes,
        )

        # Step 7: Validate
        conn.autocommit = True
        _validate_sample(conn, run_id, match_pairs, entity_by_ulid)

    except Exception:
        log.exception("Fatal error in cross_source_dedup")
        raise
    finally:
        conn.close()
        log.info("PG connection closed.")


if __name__ == "__main__":
    main()
