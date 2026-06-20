"""Lens B — orthogonal raw recount (§3.2), now ACTIVE.

Previously this lens abstained unconditionally (`_RAW_STORE_AVAILABLE=False`) on
the grounds that no separate raw-evidence byte store existed. That left count/
inventory subjects with only Lens A asserting → the quorum's ≥2-independent-ASSERT
gate could never be met → TRUSTWORTHY was structurally unreachable.

Lens B does NOT need a separate byte store to be a genuine orthogonal recount: it
recounts the SAME claimed quantity from a DIFFERENT raw representation than Lens A,
along a path no ingest worker emits, so it catches failure modes A is blind to.

  count  : A scans the `entity` table directly. B recounts DISTINCT entities via
           the append-only provenance ledger `entity_source` (the raw record of
           who-saw-what). Divergence = entities with no provenance row (phantom
           rows A would happily count) → B REFUTES. tool='ledger'.
  inventory: A counts raw vehicle ROWS with a price (FILTER). B counts DISTINCT
           `deep_link` (the source's stable id) among them. Divergence = duplicate
           rows inflating A's count while the distinct-id set stays smaller → B
           REFUTES. tool='distinct_id'.

Independence: tool+path differ from Lens A (sql / lens_a_requery), so the pairwise
StateTuple distance is ≥2 — B is an admissible second skeptic. It is endogenous to
our DB (same source+cache); the externally-independent lenses are C (live portal)
and D (cross-source). B's job is to corroborate-or-refute A's number by an
independent internal path, exactly as the §3.2 design intended.
"""
from __future__ import annotations

import asyncpg

from pipeline.inquisition.models import Skeptic, StateTuple, regime_for
from pipeline.inquisition.quorum import within_tolerance


def _canonical_int(value: int | float) -> str:
    return str(int(round(value)))


def _state(source: str, cache: str, tool: str) -> StateTuple:
    return StateTuple(source=source, tool=tool, cache=cache, path="lens_b_raw_recount")


async def lens_b_raw_recount(conn: asyncpg.Connection, claim) -> Skeptic:
    st = claim.producer_state
    subject_type = claim.subject_type

    if subject_type == "count":
        return await _b_count(conn, claim, st)
    if subject_type == "inventory":
        return await _b_inventory(conn, claim, st)

    return Skeptic(
        lens="B_raw_recount",
        state=_state(st.source, st.cache, "ledger"),
        verdict="ABSTAIN",
        measured_value=None,
        confidence=None,
        reason=f"lens_b_unsupported_subject_type:{subject_type}",
    )


async def _b_count(conn: asyncpg.Connection, claim, st) -> Skeptic:
    """Recount distinct entities through the provenance ledger (orthogonal to A)."""
    key: str = claim.subject_key
    asserted = float(claim.asserted_value)
    regime = regime_for(claim.subject_type)
    lens_state = _state(st.source, st.cache, "ledger")

    if key.startswith("province:") or (len(key) == 2 and key.isalnum() and ":" not in key):
        province = key.split(":", 1)[1] if ":" in key else key
        row = await conn.fetchrow(
            """SELECT COUNT(DISTINCT es.entity_ulid) AS n
                 FROM entity_source es
                 JOIN entity e ON e.entity_ulid = es.entity_ulid
                WHERE e.province_code = $1""",
            province,
        )
    elif key.startswith("kind:"):
        kind_name = key.split(":", 1)[1]
        row = await conn.fetchrow(
            """SELECT COUNT(DISTINCT es.entity_ulid) AS n
                 FROM entity_source es
                 JOIN entity e ON e.entity_ulid = es.entity_ulid
                WHERE e.kind = $1::entity_kind""",
            kind_name,
        )
    elif key == "all":
        row = await conn.fetchrow(
            """SELECT COUNT(DISTINCT es.entity_ulid) AS n
                 FROM entity_source es
                 JOIN entity e ON e.entity_ulid = es.entity_ulid""")
    else:
        return Skeptic(
            lens="B_raw_recount", state=lens_state, verdict="ABSTAIN",
            measured_value=None, confidence=None,
            reason=f"lens_b_count_unsupported_key:{key}")

    measured = int(row["n"] or 0)
    return _verdict(lens_state, measured, asserted, regime)


async def _b_inventory(conn: asyncpg.Connection, claim, st) -> Skeptic:
    """Recount DISTINCT stable ids (deep_link) — catches duplicate-row inflation."""
    key: str = claim.subject_key
    asserted = float(claim.asserted_value)
    regime = regime_for(claim.subject_type)
    lens_state = _state(st.source, st.cache, "distinct_id")

    if not key.startswith("inventory:"):
        return Skeptic(
            lens="B_raw_recount", state=lens_state, verdict="ABSTAIN",
            measured_value=None, confidence=None,
            reason=f"lens_b_inventory_unsupported_key:{key}")

    entity_ulid = key.split(":", 1)[1]
    row = await conn.fetchrow(
        """SELECT COUNT(DISTINCT deep_link) AS n
             FROM vehicle
            WHERE entity_ulid = $1 AND status = 'available' AND price IS NOT NULL""",
        entity_ulid,
    )
    measured = int(row["n"] or 0)
    return _verdict(lens_state, measured, asserted, regime)


def _verdict(lens_state: StateTuple, measured: int, asserted: float, regime) -> Skeptic:
    in_tol = within_tolerance(float(measured), asserted, regime)
    return Skeptic(
        lens="B_raw_recount",
        state=lens_state,
        verdict="ASSERT" if in_tol else "REFUTE_SOFT",
        measured_value=_canonical_int(measured),
        confidence=0.95 if in_tol else None,
        reason=None if in_tol else "raw_recount_mismatch",
    )
