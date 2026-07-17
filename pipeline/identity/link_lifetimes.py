"""
pipeline/identity/link_lifetimes.py
CAMPAIGN vehicle-lifetime-det-v1 — deterministic re-identification of a physical car
across SEQUENTIAL episodes (Pillar 02-history-reports F1, plans/cardeep-omni).

Identifies when a vehicle went GONE at one dealer and reappeared weeks/months later
— possibly at a DIFFERENT dealer, possibly on a different platform — WITHOUT ever
mutating a single row in vehicle or vehicle_event. Mirrors cluster_vehicles.py (B7)
in shape: union-find-free deterministic resolver, run+gate audit table, non-
destructive overlay.

WHY THIS IS A DIFFERENT PROBLEM FROM cluster_vehicles.py (0023)
----------------------------------------------------------------
0023/cluster_vehicles.py dedups SIMULTANEOUS listings of the same physical car across
platforms (same-time duplicates). This module links SEQUENTIAL episodes over TIME —
a car that left the market and came back. Consequences that flow from this distinction:

  - Province is EXPECTED to change between episodes (a car resold months later can
    easily end up in a different city/dealer) — unlike 0023's Signal B, which treats
    a cross-province match as suspicious. This module does NOT gate on province.
  - Price is EXPECTED to differ (different dealer, different asking price) — unlike
    0023's firma, which requires price parity as a duplicate-detection signal. This
    module does NOT gate on price.
  - Country is still a hard guard (COUNTRY-PROOF convention, project-wide): a car
    legitimately crossing a border between episodes is a real but out-of-scope case
    for v1 (would require EUCARIS-style cross-border reasoning); blocking it is a
    declared, conservative choice, not an oversight.

F0 FINDING THAT SHAPES THIS ENGINE (plans/cardeep-omni/02-history-reports.md §10)
----------------------------------------------------------------------------------
`vehicle.vin_ref` is contaminated: 94.4% of rows are non-null, but the overwhelming
majority hold a PLATFORM-INTERNAL id, not a VIN — pipeline/sources/autoscout24.py:208
stores AutoScout24's own listing `id`/`identifier` there. Only rows whose vin_ref is
EXACTLY 17 characters AND matches the real VIN alphabet (no I/O/Q) are treated as a
genuine VIN by this engine (`_normalize_vin`). Measured live: 25,777 such rows, 100%
of them from OEM certified-pre-owned sources (Toyota, BMW Premium Selection, Audi,
Volvo Selekt, ...) — ZERO from wallapop/milanuncios/coches.net/autoscout24/autocasion,
the marketplaces where the "coche rebotado entre compraventas" scenario actually lives.
This means v1's real yield is small (344 GONE vehicles with >=1 cross-dealer candidate,
measured in F0) — a declared, honest limitation, not hidden. The day photo_hash gets
populated (04-F6, a separate workstream), this SAME engine picks up more links with
zero code changes: the photo_hash path below is fully implemented and unit-tested
today even though production has 0 non-null photo_hash rows.

CORROBORATION DESIGN DECISION (declared, not silently assumed — pillar letter §7 is
ambiguous on this exact point)
----------------------------------------------------------------------------------
§7 of the pillar letter requires a primary signal (vin_ref exact OR photo_hash exact)
PLUS a corroborating signal: "la otra de las dos, o firma make/model/year + km
monótono no decreciente + coherencia temporal". Read literally, a genuine km
RETREAT (declared km lower on the later listing — exactly the anomaly C8 exists to
surface) would fail corroboration and the link could never be shown, which would
make it structurally impossible to ever detect the very phenomenon the product
wants to highlight. This module resolves the tension explicitly: km evaluation
(`_evaluate_km`) uses the SAME anti-noise threshold C8 itself uses (1,000 km) to
decide "coherent" vs "retreat", but a flagged retreat DOES NOT block the link — it
lowers `match_probability` and is carried verbatim in `evidence.km_retreat_flagged`
so C8 can surface it downstream. A HARD reject only happens on a firma mismatch
(make/model/year genuinely differ) — that is treated as evidence the primary-signal
match itself is spurious (contaminated vin_ref, hash collision), not as a business
signal worth keeping at low confidence. This mirrors cluster_vehicles.py's own
precedent: rejected candidates are not persisted, not merely hidden.

Anti-FP hard guards
--------------------
  - Predecessor must be status='gone' (still 'available' = hasn't left the market).
  - Predecessor must have no 'available' sibling in its 0023 canonical cluster (a
    car simultaneously listed on two platforms that loses ONE listing has not left
    the market — only lifetime_link.py cares about "market exit", not delisting).
  - Cross-country blocked (COUNTRY-PROOF convention).
  - Temporal order: successor.first_seen strictly after predecessor.last_seen,
    within LIFETIME_WINDOW_DAYS.
  - Firma mismatch (make/model/year) on an otherwise-matching primary signal
    REJECTS the pair outright.
  - photo_hash high-collision guard (catalogue/stock photo shared by >=K listings)
    excluded from Signal matching — mirrors cluster_vehicles.py's
    PHOTO_HIGH_COLLISION_K (fleet twins with the same catalogue photo, trap #1).

Run:
    python -m pipeline.identity.link_lifetimes

Idempotent: deletes cluster_run_id=RUN_ID before writing. Does NOT touch any other run.

Requires:
    psycopg2, PostgreSQL (no extensions needed).
"""
from __future__ import annotations

import json
import logging
import os
import re
import sys
from collections import defaultdict
from typing import Any

import psycopg2
import psycopg2.extras

from pipeline.identity.cluster_vehicles import UnionFind

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RUN_ID = "vehicle-lifetime-det-v1"
RESOLVER = "sequential-bucket-chain-deterministic"
RESOLVER_VERSION = "1.0.0"
SCOPE_CONDITION = "vin_ref IS NOT NULL OR photo_hash IS NOT NULL"

# Re-appearance window: 0-12 months, measured and justified in F0 (02-history-reports.md §10.3).
LIFETIME_WINDOW_DAYS = 365

# Anti-noise threshold for km evaluation — DELIBERATELY the same value C8 (the product's
# own km-retreat alert, plans/cardeep-omni/02-history-reports.md §4) uses, so "coherent
# enough to link" and "worth alerting on" share one number, never drift apart.
KM_NOISE_THRESHOLD_KM = 1000

# Catalogue/stock photo_hash guard: a hash shared by >= K distinct listings is a stock
# image, not a unique physical-car photo. Mirrors cluster_vehicles.py's
# PHOTO_HIGH_COLLISION_K (same value, same rationale: fleet twins with a shared
# catalogue photo must never be treated as the same physical unit).
PHOTO_HASH_HIGH_COLLISION_K = 12

# Real VIN alphabet: 17 chars, no I/O/Q (avoid confusion with 1/0), matches the
# strict pattern used to measure the F0 coverage numbers.
_VIN_RE = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")

# Confidence ladder — declared, relative, not derived from ground-truth outcome data
# (no such data exists yet; §8 of the pillar letter explicitly forbids inventing a
# synthetic score without ground truth. These are ORDINAL confidence weights for
# match_probability, re-calibrate once §7's N=50 manual sample runs).
_PROB_BOTH_SIGNALS = 0.98
_PROB_VIN_COHERENT = 0.92
_PROB_VIN_KM_UNKNOWN = 0.85
_PROB_VIN_RETREAT = 0.80
_PROB_PHOTO_COHERENT = 0.85
_PROB_PHOTO_KM_UNKNOWN = 0.78
_PROB_PHOTO_RETREAT = 0.70

BLOCKING_RULES: list[str] = [
    "primary signal: vin_ref exact (17-char, strict VIN alphabet, trim+uppercase) OR "
    "photo_hash exact (excluding catalogue/stock hashes shared by >= "
    f"{PHOTO_HASH_HIGH_COLLISION_K} listings)",
    "corroboration: the OTHER of the two signals also matching (match_signal='both') "
    "OR firma (make+model+year exact, normalized) + temporal order; a firma MISMATCH "
    "on a matching primary signal REJECTS the pair outright (not persisted at low "
    "confidence — mirrors cluster_vehicles.py precedent)",
    f"km evaluation: retreat beyond {KM_NOISE_THRESHOLD_KM}km is FLAGGED (evidence."
    "km_retreat_flagged=true, lowers match_probability) but does NOT block the link — "
    "declared design decision, see module docstring (the pillar's own C8 alert depends "
    "on this exact case being linkable, not silently rejected)",
    "country-isolation guard: never link cross-country (COUNTRY-PROOF convention); "
    "province and price are explicitly NOT gated (expected to differ across episodes, "
    "unlike cluster_vehicles.py's simultaneous-duplicate signals)",
    f"temporal window: 0 < (successor.first_seen - predecessor.last_seen) <= "
    f"{LIFETIME_WINDOW_DAYS} days",
    "predecessor must be status='gone' AND have no 'available' sibling in its 0023 "
    "canonical cluster (still_active_predecessors) — the physical car must have "
    "genuinely left the market, not merely lost one of several simultaneous listings",
    "HARD anti-churn guard (added after the first live run, 2026-07-18, evidence in "
    "plans/cardeep-omni/02-history-reports.md §10): predecessor and successor deep_link "
    "domain must DIFFER. The first run's 208 candidate edges were 100% intra-domain "
    "(same OEM certified-pre-owned portal reissuing a listing under a new URL) — portal "
    "listing churn, not a car resurfacing at an independent business. Same-domain "
    "candidates are never linked, regardless of signal strength.",
]


def _get_dsn() -> str:
    return os.environ.get(
        "CARDEEP_DSN",
        "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep",
    )


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------


def _normalize_vin(vin_ref: str | None) -> str | None:
    """Return the trimmed, uppercased VIN if it is pattern-valid; else None.

    Guards against the F0 contamination finding: most non-null vin_ref values are
    platform-internal listing ids (autoscout24.py:208), not VINs. Only a 17-char
    string drawn from the real VIN alphabet (no I/O/Q) is accepted.
    """
    if not vin_ref or not vin_ref.strip():
        return None
    v = vin_ref.strip().upper()
    return v if _VIN_RE.match(v) else None


def _normalize_photo_hash(photo_hash: str | None) -> str | None:
    """Return the trimmed photo_hash, or None for empty/missing."""
    if not photo_hash or not photo_hash.strip():
        return None
    return photo_hash.strip()


def _normalize_field(v: str | None) -> str | None:
    if not v or not v.strip():
        return None
    return v.strip().lower()


_DOMAIN_RE = re.compile(r"^https?://([^/]+)", re.IGNORECASE)


def _platform_domain(deep_link: str | None) -> str | None:
    """Extract the lowercased host from a deep_link, or None if unavailable.

    ANTI-CHURN GUARD (added after the first live F1 run, 2026-07-18 — declared,
    evidence-based hardening, not a speculative guard): the run's 208 raw
    candidate edges were audited by SQL against the live DB and found to be
    100% intra-domain (same OEM certified-pre-owned portal — Volvo Selekt, BMW
    Premium Selection, Spoticar/Stellantis, Toyota, Mini Next). Every single one
    was the SAME manufacturer-network website reissuing a listing under a new
    URL/listing_ref (75% within <1 day, the rest in a suspiciously narrow 7-30
    day band matching a recrawl cadence, not organic resale timing; km values
    were frequently IDENTICAL or suspiciously round, e.g. 5000/10000/15000 tier
    placeholders) — portal-side listing churn, not a car leaving one independent
    business and resurfacing at another. See
    plans/cardeep-omni/02-history-reports.md §10 for the full audit. Domain
    match is therefore a HARD block (see _evaluate_pair), not a probability
    discount: with today's data, a same-domain "reappearance" has never once
    been observed to be genuine.
    """
    if not deep_link or not deep_link.strip():
        return None
    m = _DOMAIN_RE.match(deep_link.strip())
    return m.group(1).lower() if m else None


def _firma_matches(va: dict, vb: dict) -> bool:
    """Firma = make + model + year, exact after normalization. ALL three required —
    a missing field on either side fails the match (cannot corroborate on absence)."""
    ma, mb = _normalize_field(va.get("make")), _normalize_field(vb.get("make"))
    moa, mob = _normalize_field(va.get("model")), _normalize_field(vb.get("model"))
    ya, yb = va.get("year"), vb.get("year")
    if not (ma and mb and moa and mob and ya is not None and yb is not None):
        return False
    return ma == mb and moa == mob and ya == yb


def _evaluate_km(km_from: Any, km_to: Any) -> dict:
    """Evaluate km coherence between predecessor and successor.

    Returns {"km_known": bool, "km_delta": int|None, "km_retreat_flagged": bool}.
    A retreat beyond KM_NOISE_THRESHOLD_KM is flagged but never blocks the link
    (declared design decision, see module docstring).
    """
    if km_from is None or km_to is None:
        return {"km_known": False, "km_delta": None, "km_retreat_flagged": False}
    delta = int(km_to) - int(km_from)
    return {
        "km_known": True,
        "km_delta": delta,
        "km_retreat_flagged": delta < -KM_NOISE_THRESHOLD_KM,
    }


def _within_window(predecessor_last_seen: Any, successor_first_seen: Any) -> bool:
    """True if 0 < gap <= LIFETIME_WINDOW_DAYS (strict temporal order required)."""
    gap = successor_first_seen - predecessor_last_seen
    if gap.total_seconds() <= 0:
        return False
    return gap.days <= LIFETIME_WINDOW_DAYS


# ---------------------------------------------------------------------------
# Bucketing (groups a physical car's episodes by identity signal)
# ---------------------------------------------------------------------------


def _build_vin_buckets(vehicles: list[dict]) -> dict[str, list[dict]]:
    """Group vehicles by normalized, pattern-valid VIN. Singleton buckets (no
    re-appearance candidate) are dropped."""
    idx: dict[str, list[dict]] = defaultdict(list)
    for v in vehicles:
        vin = _normalize_vin(v.get("vin_ref"))
        if vin:
            idx[vin].append(v)
    return {k: v for k, v in idx.items() if len(v) >= 2}


def _build_photo_hash_buckets(vehicles: list[dict]) -> dict[str, list[dict]]:
    """Group vehicles by normalized photo_hash, excluding catalogue/stock hashes
    shared by >= PHOTO_HASH_HIGH_COLLISION_K listings (trap #1: fleet twins).
    Singleton buckets are dropped."""
    idx: dict[str, list[dict]] = defaultdict(list)
    for v in vehicles:
        h = _normalize_photo_hash(v.get("photo_hash"))
        if h:
            idx[h].append(v)
    return {
        k: v
        for k, v in idx.items()
        if 2 <= len(v) < PHOTO_HASH_HIGH_COLLISION_K
    }


# ---------------------------------------------------------------------------
# Edge building
# ---------------------------------------------------------------------------


def _sort_key(v: dict) -> tuple:
    return (v["first_seen"], v["vehicle_ulid"])


def _candidate_pairs(bucket: list[dict]) -> list[tuple[dict, dict]]:
    """Consecutive pairs in first_seen order — a bucket represents one physical
    car's sequential episodes; only ADJACENT episodes are attempted (no skip-ahead:
    if the immediate next episode fails its guards, the chain simply does not
    extend past that point for this run — a broken adjacency is real information,
    not something to paper over by matching a further episode instead)."""
    ordered = sorted(bucket, key=_sort_key)
    return list(zip(ordered, ordered[1:]))


def _evaluate_pair(
    predecessor: dict,
    successor: dict,
    still_active_predecessors: set[str],
    vin_match: bool,
    photo_match: bool,
) -> dict | None:
    """Apply every anti-FP guard + corroboration rule to one candidate pair.
    Returns an edge dict, or None if the pair must not be linked."""
    if predecessor["vehicle_ulid"] == successor["vehicle_ulid"]:
        return None
    if predecessor.get("status") != "gone":
        return None
    if predecessor["vehicle_ulid"] in still_active_predecessors:
        return None
    if predecessor.get("country_code") != successor.get("country_code"):
        return None
    if not _within_window(predecessor["last_seen"], successor["first_seen"]):
        return None
    dom_from = _platform_domain(predecessor.get("deep_link"))
    dom_to = _platform_domain(successor.get("deep_link"))
    if dom_from and dom_to and dom_from == dom_to:
        # Hard anti-churn guard — see _platform_domain docstring for the live-data
        # evidence that made this a block rather than a confidence discount.
        return None

    km_eval = _evaluate_km(predecessor.get("km"), successor.get("km"))

    if vin_match and photo_match:
        signal = "both"
        probability = _PROB_BOTH_SIGNALS
    elif vin_match or photo_match:
        # Corroboration required: firma must match (make/model/year); a mismatch
        # REJECTS the pair outright (see module docstring).
        if not _firma_matches(predecessor, successor):
            return None
        signal = "vin_ref" if vin_match else "photo_hash"
        if not km_eval["km_known"]:
            probability = _PROB_VIN_KM_UNKNOWN if vin_match else _PROB_PHOTO_KM_UNKNOWN
        elif km_eval["km_retreat_flagged"]:
            probability = _PROB_VIN_RETREAT if vin_match else _PROB_PHOTO_RETREAT
        else:
            probability = _PROB_VIN_COHERENT if vin_match else _PROB_PHOTO_COHERENT
    else:
        return None

    evidence = {
        "vin_ref": _normalize_vin(predecessor.get("vin_ref")) if vin_match else None,
        "photo_hash": _normalize_photo_hash(predecessor.get("photo_hash")) if photo_match else None,
        "make": predecessor.get("make"),
        "model": predecessor.get("model"),
        "year": predecessor.get("year"),
        "km_from": predecessor.get("km"),
        "km_to": successor.get("km"),
        "km_delta": km_eval["km_delta"],
        "km_known": km_eval["km_known"],
        "km_retreat_flagged": km_eval["km_retreat_flagged"],
        "date_from": str(predecessor["last_seen"]),
        "date_to": str(successor["first_seen"]),
        "entity_from": predecessor.get("entity_ulid"),
        "entity_to": successor.get("entity_ulid"),
        "domain_from": dom_from,
        "domain_to": dom_to,
    }

    return {
        "vehicle_ulid_from": predecessor["vehicle_ulid"],
        "vehicle_ulid_to": successor["vehicle_ulid"],
        "match_signal": signal,
        "match_probability": probability,
        "evidence": evidence,
    }


def _build_edges(
    vehicles: list[dict],
    still_active_predecessors: set[str],
) -> list[dict]:
    """Build all lifetime edges from vin_ref and photo_hash buckets, deduplicating
    a pair found via both bucket types into a single 'both'-signal edge."""
    vin_buckets = _build_vin_buckets(vehicles)
    photo_buckets = _build_photo_hash_buckets(vehicles)

    vin_pairs: dict[tuple[str, str], tuple[dict, dict]] = {}
    for bucket in vin_buckets.values():
        for pred, succ in _candidate_pairs(bucket):
            vin_pairs[(pred["vehicle_ulid"], succ["vehicle_ulid"])] = (pred, succ)

    photo_pairs: dict[tuple[str, str], tuple[dict, dict]] = {}
    for bucket in photo_buckets.values():
        for pred, succ in _candidate_pairs(bucket):
            photo_pairs[(pred["vehicle_ulid"], succ["vehicle_ulid"])] = (pred, succ)

    all_keys = set(vin_pairs) | set(photo_pairs)
    edges: list[dict] = []
    for key in all_keys:
        pred, succ = vin_pairs.get(key) or photo_pairs.get(key)
        vin_match = key in vin_pairs
        photo_match = key in photo_pairs
        edge = _evaluate_pair(pred, succ, still_active_predecessors, vin_match, photo_match)
        if edge is not None:
            edges.append(edge)

    log.info(
        "Built %d lifetime edges (vin candidate pairs=%d, photo candidate pairs=%d)",
        len(edges), len(vin_pairs), len(photo_pairs),
    )
    return edges


def _count_chains(edges: list[dict]) -> int:
    """Number of distinct lifetime chains (connected components over the edge
    endpoints). Reuses cluster_vehicles.py's UnionFind — no duplication."""
    uf = UnionFind()
    nodes: set[str] = set()
    for e in edges:
        uf.union(e["vehicle_ulid_from"], e["vehicle_ulid_to"])
        nodes.add(e["vehicle_ulid_from"])
        nodes.add(e["vehicle_ulid_to"])
    roots = {uf.find(n) for n in nodes}
    return len(roots)


# ---------------------------------------------------------------------------
# PG data access
# ---------------------------------------------------------------------------


def _load_vehicles(conn: Any) -> list[dict]:
    """Load every vehicle carrying a candidate identity signal, with entity
    country_code via JOIN (vehicle has no country_code of its own, mig 0003;
    country is reached via entity, mig 0052 — same pattern as cluster_vehicles.py)."""
    log.info("Loading candidate vehicles from PG (vin_ref or photo_hash present) ...")
    query = """
        SELECT
            v.vehicle_ulid, v.entity_ulid, v.make, v.model, v.year, v.km,
            v.vin_ref, v.photo_hash, v.status, v.first_seen, v.last_seen,
            v.deep_link, e.country_code
        FROM vehicle v
        LEFT JOIN entity e ON e.entity_ulid = v.entity_ulid
        WHERE (v.vin_ref IS NOT NULL AND v.vin_ref <> '')
           OR (v.photo_hash IS NOT NULL AND v.photo_hash <> '')
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(query)
        rows = [dict(r) for r in cur.fetchall()]
    log.info("Loaded %d candidate vehicles", len(rows))
    return rows


def _load_still_active_predecessors(conn: Any) -> set[str]:
    """Vehicles that are status='gone' but have an 'available' sibling in the
    latest vam_verified 0023 canonical cluster — the physical car never left the
    market, only this one listing did. These must never be used as a lifetime
    predecessor."""
    query = """
        WITH latest_run AS (
            SELECT cluster_run_id FROM vehicle_cluster_run
            WHERE vam_verified = TRUE ORDER BY run_at DESC LIMIT 1
        ),
        cluster_status AS (
            SELECT vc.canonical_vehicle_ulid, vc.vehicle_ulid, v.status
            FROM vehicle_cluster vc
            JOIN latest_run lr ON lr.cluster_run_id = vc.cluster_run_id
            JOIN vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
            WHERE vc.cluster_size > 1
        )
        SELECT DISTINCT cs.vehicle_ulid
        FROM cluster_status cs
        WHERE cs.status = 'gone'
          AND EXISTS (
              SELECT 1 FROM cluster_status sib
              WHERE sib.canonical_vehicle_ulid = cs.canonical_vehicle_ulid
                AND sib.vehicle_ulid <> cs.vehicle_ulid
                AND sib.status = 'available'
          )
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT to_regclass('vehicle_cluster_run') IS NOT NULL AS exists_run"
        )
        if not cur.fetchone()[0]:
            log.warning("vehicle_cluster_run table not found — skipping active-sibling guard")
            return set()
        cur.execute(query)
        rows = {r[0] for r in cur.fetchall()}
    log.info("Loaded %d gone-vehicles with an active 0023 cluster sibling (excluded as predecessors)", len(rows))
    return rows


def _assert_no_cross_country_edges(edges: list[dict], vehicle_by_ulid: dict[str, dict]) -> None:
    """BLOCKING pre-write guard (mirrors cluster_vehicles.py's
    _assert_no_cross_country_clusters) — defense-in-depth mirror of the edge-level
    country check already applied in _evaluate_pair."""
    offenders = []
    for e in edges:
        va = vehicle_by_ulid.get(e["vehicle_ulid_from"], {})
        vb = vehicle_by_ulid.get(e["vehicle_ulid_to"], {})
        if va.get("country_code") != vb.get("country_code"):
            offenders.append((e["vehicle_ulid_from"], e["vehicle_ulid_to"]))
    if offenders:
        raise RuntimeError(
            f"COUNTRY-PROOF VIOLATION: {len(offenders)} lifetime edge(s) span "
            f">1 country_code — refusing to write/serve. sample={offenders[:5]}"
        )
    log.info("Country-isolation guard OK: %d edges, all single-country.", len(edges))


def _write_to_pg(conn: Any, edges: list[dict], n_in: int) -> None:
    """Write lifetime_link_run + lifetime_link in a single transaction. Idempotent:
    deletes any previous RUN_ID run first."""
    n_chains = _count_chains(edges)
    n_linked = len(edges)

    counts: dict[str, int] = defaultdict(int)
    for e in edges:
        counts[e["match_signal"]] += 1
    notes = json.dumps({
        "edges_vin_ref": counts.get("vin_ref", 0),
        "edges_photo_hash": counts.get("photo_hash", 0),
        "edges_both": counts.get("both", 0),
    })

    log.info("Writing to PG: n_in=%d n_chains=%d n_linked=%d", n_in, n_chains, n_linked)

    with conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM lifetime_link WHERE run_id = %s", (RUN_ID,))
            cur.execute("DELETE FROM lifetime_link_run WHERE run_id = %s", (RUN_ID,))

            cur.execute(
                """
                INSERT INTO lifetime_link_run
                    (run_id, resolver, resolver_version, scope,
                     blocking_rules, n_in, n_chains, n_linked, vam_verified, notes)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s, FALSE, %s)
                """,
                (
                    RUN_ID, RESOLVER, RESOLVER_VERSION, SCOPE_CONDITION,
                    json.dumps(BLOCKING_RULES), n_in, n_chains, n_linked, notes,
                ),
            )

            if edges:
                rows_to_insert = [
                    (
                        RUN_ID,
                        e["vehicle_ulid_from"],
                        e["vehicle_ulid_to"],
                        e["match_signal"],
                        e["match_probability"],
                        json.dumps(e["evidence"]),
                    )
                    for e in edges
                ]
                psycopg2.extras.execute_values(
                    cur,
                    """
                    INSERT INTO lifetime_link
                        (run_id, vehicle_ulid_from, vehicle_ulid_to,
                         match_signal, match_probability, evidence)
                    VALUES %s
                    """,
                    rows_to_insert,
                    template="(%s, %s, %s, %s, %s, %s::jsonb)",
                    page_size=1000,
                )

    log.info("Write committed. run_id=%s", RUN_ID)


def _measure_and_validate(conn: Any, edges: list[dict]) -> None:
    """Print a measurement report + a sample of edges for Director validation
    (§7 of the pillar letter: N=50 manual sample before the first vam_verified=TRUE)."""
    log.info("=== F1 MEASUREMENT & VALIDATION REPORT (%s) ===", RUN_ID)
    print(f"\n--- RUN STATS ---\n  edges_total : {len(edges)}\n  chains      : {_count_chains(edges)}\n")

    by_signal: dict[str, int] = defaultdict(int)
    retreats = 0
    for e in edges:
        by_signal[e["match_signal"]] += 1
        if e["evidence"]["km_retreat_flagged"]:
            retreats += 1
    print("--- SIGNAL BREAKDOWN ---")
    for sig, n in sorted(by_signal.items()):
        print(f"  signal={sig!r:12s}  edges={n:>5,}")
    print(f"\n  km_retreat_flagged edges: {retreats}")

    print("\n--- SAMPLE (up to 50, for Director VAM per §7) ---")
    for i, e in enumerate(edges[:50], 1):
        ev = e["evidence"]
        print(
            f"  [{i:02d}] {e['vehicle_ulid_from']} -> {e['vehicle_ulid_to']}  "
            f"signal={e['match_signal']}  p={e['match_probability']}  "
            f"{ev['make']} {ev['model']} {ev['year']}  "
            f"km {ev['km_from']}->{ev['km_to']} (retreat={ev['km_retreat_flagged']})  "
            f"{ev['entity_from']}->{ev['entity_to']}  "
            f"{ev['date_from']}->{ev['date_to']}"
        )
    log.info("=== END F1 REPORT ===")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    dsn = _get_dsn()
    log.info("Connecting to PG ...")
    conn = psycopg2.connect(dsn)
    conn.autocommit = False

    try:
        vehicles = _load_vehicles(conn)
        n_in = len(vehicles)
        still_active_predecessors = _load_still_active_predecessors(conn)

        edges = _build_edges(vehicles, still_active_predecessors)

        vehicle_by_ulid = {v["vehicle_ulid"]: v for v in vehicles}
        _assert_no_cross_country_edges(edges, vehicle_by_ulid)

        _write_to_pg(conn, edges, n_in)

        conn.autocommit = True
        _measure_and_validate(conn, edges)

    except Exception:
        log.exception("Fatal error in vehicle-lifetime-det-v1 pipeline")
        raise
    finally:
        conn.close()
        log.info("PG connection closed.")


if __name__ == "__main__":
    main()
