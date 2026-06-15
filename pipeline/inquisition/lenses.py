"""Five orthogonal inquisition lenses — SU-B2 ε3.

Public API. Each lens returns a Skeptic that is independent (D ≥ 2) from the
typical producer's StateTuple, then an ASSERT / REFUTE_SOFT / REFUTE_HARD /
ABSTAIN verdict.

Internal Lens A and D implementations live in private modules (_lens_a.py,
_lens_d.py) to stay under the 800-line file limit.

Lens routing matrix (§3.6):
    A_requery       → count, inventory, coverage, kind, denominator
    B_raw_recount   → count, inventory  (€0 IFF raw store exists; else ABSTAIN)
    C_live_refetch  → count, inventory, coverage, kind  (STUB — harvest phase)
    D_cross_source  → count, coverage, kind, denominator
    E_batch_hash    → inventory, delta

Design decisions
----------------
ClaimEnvelope (frozen dataclass) is the unified input contract. It holds
exactly the fields from inquisition_claim that a lens needs, with
producer_state deserialized into a StateTuple. This lets tests build fixtures
without a DB round-trip (unlike passing a raw asyncpg.Record).

measured_value is always a canonical integer string ("12345" not "12345.0").
The quorum's modal Counter uses string equality; "12345" ≠ "12345.0" would
silently split a true quorum.

Every lens that cannot measure returns ABSTAIN with a precise reason.
(Law I: absence of refutation is NOT proof.)

Confidence heuristic: lens-base × source_health_factor.
    A=0.90, B=0.95 (when active), C=N/A, D=0.80, E=1.00 (deterministic hash).
    Source-health factor: healthy=1.0, degraded=0.85, down/unknown=0.70.

StateTuple independence vs typical producer (source=portal, tool=scraper,
cache=snap_T0, path=ingest):
    Lens A: same source+cache, tool=sql, path=lens_a_requery        → D=2
    Lens B: same source+cache, tool=json_parser, path=lens_b_raw    → D=2
    Lens C: source=live_portal, tool=browser, cache=live_T1, ...    → D=4
    Lens D: source=<DIFFERENT>, tool=sql, path=lens_d_xsrc          → D≥2
    Lens E: same source+cache, tool=sha256, path=lens_e_hash        → D=2
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import asyncpg

from pipeline.inquisition.models import Skeptic, StateTuple
from pipeline.inquisition._lens_a import lens_a_requery as _lens_a_impl
from pipeline.inquisition._lens_d import lens_d_cross_source as _lens_d_impl

# ---------------------------------------------------------------------------
# ClaimEnvelope — unified input contract (frozen dataclass)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ClaimEnvelope:
    """Frozen DTO carrying the fields a lens needs to evaluate a claim.

    Maps 1:1 to inquisition_claim columns, with producer_state deserialized
    into a StateTuple for StateTuple arithmetic.

    Fields
    ------
    claim_id:       ULID of the inquisition_claim row.
    subject_type:   count | inventory | coverage | kind | delta |
                    denominator | registral | official | cif | entity_field.
    subject_key:    domain key (e.g. 'province:28', 'kind:desguace',
                    'inventory:<entity_ulid>', 'denominator:P_all').
    asserted_value: the producer's claimed value (str; lenses parse as needed).
    producer_state: the producer's StateTuple (from inquisition_claim.producer_state).
    tolerance:      relative tolerance override (default 0.005 = TAU_REL).
    evidence_uri:   optional URI to raw evidence ('hash:<hex>' for Lens E;
                    'file:///…' for Lens B). None when not applicable.
    """
    claim_id: str
    subject_type: str
    subject_key: str
    asserted_value: str
    producer_state: StateTuple
    tolerance: float
    evidence_uri: str | None


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _canonical_int(value: int | float) -> str:
    """Canonical integer string: str(int(round(value))). Never '1234.0'."""
    return str(int(round(value)))


def _lens_state(source: str, cache: str, tool: str, path: str) -> StateTuple:
    return StateTuple(source=source, tool=tool, cache=cache, path=path)


# ---------------------------------------------------------------------------
# Lens A — re-query via different SQL aggregation path (§3.1)
# Implementation in _lens_a.py; re-exported here for the dispatcher.
# ---------------------------------------------------------------------------

async def lens_a_requery(
    conn: asyncpg.Connection,
    claim: ClaimEnvelope,
) -> Skeptic:
    """Re-derive the claimed value via a different SQL aggregation path.

    Delegates to _lens_a.lens_a_requery; see that module for full docs.
    StateTuple: tool='sql', path='lens_a_requery' → D ≥ 2 vs any ingest state.
    """
    return await _lens_a_impl(conn, claim)


# ---------------------------------------------------------------------------
# Lens B — raw-evidence recount (§3.2)
#
# €0 ONLY if a raw evidence store is reachable at evidence_uri.
# Current state: NO raw store exists. ABSTAINS honestly.
#
# Repo audit (2026-06-15): grepped pipeline/, scrapers/, ops/ for
# 'evidence_store', 'raw_evidence', 'evidence_uri resolver', 'file:///evidence'.
# The inquisition_claim.evidence_uri column exists (0032_inquisition.sql) but
# nothing writes to it yet. _RAW_STORE_AVAILABLE = False.
#
# Implementation stub: set _RAW_STORE_AVAILABLE = True and implement
# _parse_evidence() when harvest stores bytes.
#
# StateTuple: tool='json_parser', path='lens_b_raw_recount' → D ≥ 2.
# ---------------------------------------------------------------------------

_RAW_STORE_AVAILABLE: bool = False


async def lens_b_raw_recount(
    conn: asyncpg.Connection,  # API symmetry; unused until store lands
    claim: ClaimEnvelope,
) -> Skeptic:
    """Recount distinct stable IDs from raw evidence bytes at evidence_uri.

    €0 ONLY when a raw-evidence store is reachable. Current state: ABSTAIN.

    When harvest lands, replace the flag and implement _parse_evidence():
        raw = await load_evidence(claim.evidence_uri)
        stable_ids = _parse_evidence(raw)  # JSON-LD / __NEXT_DATA__ / sitemap
        return Skeptic(lens='B_raw_recount', verdict=..., measured=len(stable_ids))

    StateTuple: tool='json_parser', path='lens_b_raw_recount' → D ≥ 2.
    """
    st = claim.producer_state
    lens_state = _lens_state(st.source, st.cache, "json_parser", "lens_b_raw_recount")

    if not _RAW_STORE_AVAILABLE or not claim.evidence_uri:
        return Skeptic(
            lens="B_raw_recount",
            state=lens_state,
            verdict="ABSTAIN",
            measured_value=None,
            confidence=None,
            reason="no_raw_evidence_store",
        )

    # Stub — reached only when _RAW_STORE_AVAILABLE is set to True:
    return Skeptic(
        lens="B_raw_recount",
        state=lens_state,
        verdict="ABSTAIN",
        measured_value=None,
        confidence=None,
        reason="no_raw_evidence_store",
    )


# ---------------------------------------------------------------------------
# Lens C — live re-fetch (§3.3) — DECLARED STUB
#
# MAKES ZERO NETWORK CALLS. Returns ABSTAIN unconditionally.
# Gated on harvest phase + separate egress identity (different JA3, IP pool).
#
# When active (SU-B3), StateTuple will be:
#   source='live_portal', tool='browser', cache='live_T1', path='lens_c_live_refetch'
#   → D = 4 (maximum independence — differs in all 4 dimensions).
# ---------------------------------------------------------------------------

async def lens_c_live_refetch(
    conn: asyncpg.Connection,  # API symmetry; unused
    claim: ClaimEnvelope,
) -> Skeptic:
    """STUB — live re-fetch from the source portal. ZERO network calls.

    Returns ABSTAIN(reason='live_refetch_requires_harvest') always.

    Implementation notes for SU-B3:
    - Use a separate curl_cffi / Camoufox session with a different JA3 fingerprint
      and a dedicated IP pool to avoid correlated failures with the ingest fleet.
    - Fetch the canonical listing page; count distinct stable IDs.
    - StateTuple: source='live_portal', tool='browser', cache='live_T1',
                  path='lens_c_live_refetch' → D=4 vs any ingest producer.
    """
    # Shape the future state for contract clarity (callers can inspect it)
    lens_state = StateTuple(
        source="live_portal",
        tool="browser",
        cache="live_T1",
        path="lens_c_live_refetch",
    )
    return Skeptic(
        lens="C_live_refetch",
        state=lens_state,
        verdict="ABSTAIN",
        measured_value=None,
        confidence=None,
        reason="live_refetch_requires_harvest",
    )


# ---------------------------------------------------------------------------
# Lens D — cross-source corroboration (§3.4)
# Implementation in _lens_d.py; re-exported here for the dispatcher.
# ---------------------------------------------------------------------------

async def lens_d_cross_source(
    conn: asyncpg.Connection,
    claim: ClaimEnvelope,
) -> Skeptic:
    """Corroborate from an orthogonal source already in the DB.

    Delegates to _lens_d.lens_d_cross_source; see that module for full docs.
    StateTuple: source=<DIFFERENT_SOURCE>, tool='sql', path='lens_d_xsrc' → D ≥ 2.
    """
    return await _lens_d_impl(conn, claim)


# ---------------------------------------------------------------------------
# Lens E — batch set-hash (§3.5)
#
# StateTuple: tool='sha256', path='lens_e_hash' → D ≥ 2 vs any ingest state.
# Applicable: inventory, delta.
# ---------------------------------------------------------------------------

def _compute_set_hash(rows: list[tuple[str, ...]]) -> str:
    """SHA-256 over sorted pipe-delimited canonical row tuples.

    Each row: (vehicle_ulid, price_str, last_seen_bucket).
        price_str        = str(int(price)) if price else 'null'
        last_seen_bucket = ISO date (day granularity — drops HH:MM:SS)

    Sorted over the full joined string → deterministic regardless of
    insertion order.
    """
    def row_str(r: tuple[str, ...]) -> str:
        return "|".join(str(x) if x is not None else "null" for x in r)

    sorted_rows = sorted(row_str(r) for r in rows)
    payload = "\n".join(sorted_rows).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


async def lens_e_batch_hash(
    conn: asyncpg.Connection,
    claim: ClaimEnvelope,
) -> Skeptic:
    """Compute set-hash of the canonical vehicle set and compare to prior hash.

    subject_key = 'inventory:<entity_ulid>' or 'delta:<entity_ulid>'.
    evidence_uri = 'hash:<prior_hex64>' — encodes the prior cycle's hash.

    For 'inventory': if prior hash available → ASSERT (unchanged) or REFUTE_SOFT
        (changed). Without prior hash → ABSTAIN (reports current hash as
        measured_value, seeding the next cycle).
    For 'delta': if current hash equals prior → the claimed delta is impossible
        → REFUTE_HARD(deterministic=True). If hash changed → ASSERT (plausible).

    StateTuple: tool='sha256', path='lens_e_hash' → D ≥ 2 vs any ingest state.
    """
    st = claim.producer_state
    lens_state = _lens_state(st.source, st.cache, "sha256", "lens_e_hash")
    subject_type = claim.subject_type
    key = claim.subject_key

    if subject_type == "inventory" and key.startswith("inventory:"):
        return await _e_inventory(conn, claim, lens_state)
    if subject_type == "delta" and key.startswith("delta:"):
        return await _e_delta(conn, claim, lens_state)

    return Skeptic(
        lens="E_batch_hash",
        state=lens_state,
        verdict="ABSTAIN",
        measured_value=None,
        confidence=None,
        reason=f"lens_e_unsupported_subject:{subject_type}:{key}",
    )


async def _fetch_vehicle_tuples(
    conn: asyncpg.Connection,
    entity_ulid: str,
) -> list[tuple[str, str, str]]:
    """Fetch (vehicle_ulid, price_str, last_seen_bucket) for available vehicles."""
    rows = await conn.fetch(
        """SELECT vehicle_ulid,
                  CASE WHEN price IS NOT NULL THEN CAST(price AS BIGINT)::text
                       ELSE 'null' END AS price_str,
                  (last_seen AT TIME ZONE 'UTC')::date::text AS last_seen_bucket
           FROM vehicle
           WHERE entity_ulid = $1 AND status = 'available'
           ORDER BY vehicle_ulid""",
        entity_ulid,
    )
    return [(r["vehicle_ulid"], r["price_str"], r["last_seen_bucket"]) for r in rows]


async def _e_inventory(
    conn: asyncpg.Connection,
    claim: ClaimEnvelope,
    lens_state: StateTuple,
) -> Skeptic:
    entity_ulid = claim.subject_key.split(":", 1)[1]
    tuples = await _fetch_vehicle_tuples(conn, entity_ulid)
    current_hash = _compute_set_hash(tuples)

    prior_hash: str | None = None
    if claim.evidence_uri and claim.evidence_uri.startswith("hash:"):
        prior_hash = claim.evidence_uri[5:]

    if prior_hash is None:
        return Skeptic(
            lens="E_batch_hash",
            state=lens_state,
            verdict="ABSTAIN",
            measured_value=current_hash,
            confidence=1.0,
            reason="no_prior_hash_to_compare",
        )

    verdict = "ASSERT" if current_hash == prior_hash else "REFUTE_SOFT"
    return Skeptic(
        lens="E_batch_hash",
        state=lens_state,
        verdict=verdict,
        measured_value=current_hash,
        confidence=1.0,
        reason=None if verdict == "ASSERT" else (
            f"hash_changed:prior={prior_hash[:16]}…current={current_hash[:16]}…"
        ),
    )


async def _e_delta(
    conn: asyncpg.Connection,
    claim: ClaimEnvelope,
    lens_state: StateTuple,
) -> Skeptic:
    """Detect empty-delta fraud: unchanged hash ⇒ claimed delta is impossible."""
    entity_ulid = claim.subject_key.split(":", 1)[1]
    tuples = await _fetch_vehicle_tuples(conn, entity_ulid)
    current_hash = _compute_set_hash(tuples)

    prior_hash: str | None = None
    if claim.evidence_uri and claim.evidence_uri.startswith("hash:"):
        prior_hash = claim.evidence_uri[5:]

    if prior_hash is None:
        return Skeptic(
            lens="E_batch_hash",
            state=lens_state,
            verdict="ABSTAIN",
            measured_value=None,
            confidence=None,
            reason="no_prior_hash_for_delta_check",
        )

    if current_hash == prior_hash:
        return Skeptic(
            lens="E_batch_hash",
            state=lens_state,
            verdict="REFUTE_HARD",
            measured_value=current_hash,
            confidence=1.0,
            reason="empty_delta:hash_unchanged_but_delta_claimed",
            deterministic=True,
        )

    return Skeptic(
        lens="E_batch_hash",
        state=lens_state,
        verdict="ASSERT",
        measured_value=current_hash,
        confidence=1.0,
        reason=None,
    )


# ---------------------------------------------------------------------------
# §3.6 lens routing matrix — dispatcher
# ---------------------------------------------------------------------------

_LENS_MATRIX: dict[str, list[str]] = {
    "count":        ["A_requery", "B_raw_recount", "C_live_refetch", "D_cross_source"],
    "inventory":    ["A_requery", "B_raw_recount", "C_live_refetch", "E_batch_hash"],
    "coverage":     ["A_requery", "C_live_refetch", "D_cross_source"],
    "kind":         ["A_requery", "C_live_refetch", "D_cross_source"],
    # §3.6 delta row: A✓ C✓ E✓ mandatory (B◦ optional). A_requery ABSTAINs until a
    # delta event-store handler lands (declared debt — see SU-A4 delta integration);
    # E_batch_hash is the mandatory empty-delta fraud-catcher and works €0.
    "delta":        ["A_requery", "C_live_refetch", "E_batch_hash"],
    "denominator":  ["A_requery", "D_cross_source"],
    "registral":    ["A_requery"],
    "official":     ["A_requery"],
    "cif":          ["A_requery"],
    "entity_field": ["A_requery"],
}

_LENS_FUNCTIONS: dict[str, Any] = {
    "A_requery":      lens_a_requery,
    "B_raw_recount":  lens_b_raw_recount,
    "C_live_refetch": lens_c_live_refetch,
    "D_cross_source": lens_d_cross_source,
    "E_batch_hash":   lens_e_batch_hash,
}


async def run_applicable_lenses(
    conn: asyncpg.Connection,
    claim: ClaimEnvelope,
) -> list[Skeptic]:
    """Run all lenses applicable to claim.subject_type per the §3.6 matrix.

    Lens C always ABSTAINs in the current €0 state (harvest not yet live).
    Lens B always ABSTAINs in the current €0 state (no raw store).

    Runs lenses sequentially within the caller's asyncpg connection to avoid
    connection-level concurrency issues. The ε4 prosecutor should wrap this
    in a read-only transaction (BEGIN READ ONLY) for snapshot isolation.

    Returns the list of Skeptic results in matrix order.
    """
    applicable = _LENS_MATRIX.get(claim.subject_type, [])
    results: list[Skeptic] = []
    for lens_name in applicable:
        fn = _LENS_FUNCTIONS[lens_name]
        results.append(await fn(conn, claim))
    return results
