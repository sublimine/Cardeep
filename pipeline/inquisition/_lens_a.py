"""Lens A — re-query via a different SQL aggregation path (§3.1, SU-B2 ε3).

Private module. Import via pipeline.inquisition.lenses, not directly.

StateTuple independence: tool='sql', path='lens_a_requery'
→ differs from any scraper producer on tool+path → D ≥ 2.

Applicable subject_types: count, inventory, coverage, kind, denominator.
"""
from __future__ import annotations

import asyncpg

from pipeline.inquisition.models import Skeptic, StateTuple, regime_for
from pipeline.inquisition.quorum import within_tolerance


def _canonical_int(value: int | float) -> str:
    """Canonical integer string: never '1234.0', always '1234'."""
    return str(int(round(value)))


def _lens_state_a(source: str, cache: str) -> StateTuple:
    return StateTuple(source=source, tool="sql", cache=cache, path="lens_a_requery")


async def lens_a_requery(
    conn: asyncpg.Connection,
    claim: object,
) -> Skeptic:
    """Re-derive the claimed value via a different SQL aggregation path.

    Uses a SUBQUERY or GROUP BY form that no ingest worker would emit,
    ensuring the SQL path is structurally distinct from the producer's.
    claim is a ClaimEnvelope (duck-typed to avoid circular import).
    """
    st = claim.producer_state  # type: ignore[attr-defined]
    lens_state = _lens_state_a(st.source, st.cache)

    subject_type = claim.subject_type

    if subject_type == "count":
        return await _a_count(conn, claim, lens_state)
    if subject_type == "kind":
        return await _a_kind(conn, claim, lens_state)
    if subject_type == "coverage":
        return await _a_coverage(conn, claim, lens_state)
    if subject_type == "inventory":
        return await _a_inventory(conn, claim, lens_state)
    if subject_type == "denominator":
        return await _a_denominator(conn, claim, lens_state)

    return Skeptic(
        lens="A_requery",
        state=lens_state,
        verdict="ABSTAIN",
        measured_value=None,
        confidence=None,
        reason=f"lens_a_unsupported_subject_type:{subject_type}",
    )


async def _a_count(
    conn: asyncpg.Connection,
    claim: object,
    lens_state: StateTuple,
) -> Skeptic:
    """Count entities in segment derived from subject_key via subquery form.

    subject_key formats:
        'province:<code>'  → COUNT(*) WHERE province_code=<code>
        'kind:<kind_name>' → COUNT(*) WHERE kind=<kind_name>
        'all'              → COUNT(*) total
        '<two-char-code>'  → COUNT(*) WHERE province_code=<code>
    """
    key: str = claim.subject_key  # type: ignore[attr-defined]
    asserted = float(claim.asserted_value)  # type: ignore[attr-defined]
    regime = regime_for(claim.subject_type)  # type: ignore[attr-defined]

    if key.startswith("province:"):
        province_code = key.split(":", 1)[1]
        row = await conn.fetchrow(
            "SELECT COUNT(*) AS n FROM (SELECT entity_ulid FROM entity WHERE province_code = $1) sub",
            province_code,
        )
    elif key.startswith("kind:"):
        kind_name = key.split(":", 1)[1]
        row = await conn.fetchrow(
            "SELECT COUNT(*) AS n FROM (SELECT entity_ulid FROM entity WHERE kind = $1::entity_kind) sub",
            kind_name,
        )
    elif key == "all":
        row = await conn.fetchrow(
            "SELECT COUNT(*) AS n FROM (SELECT entity_ulid FROM entity) sub"
        )
    else:
        row = await conn.fetchrow(
            "SELECT COUNT(*) AS n FROM (SELECT entity_ulid FROM entity WHERE province_code = $1) sub",
            key,
        )

    measured = int(row["n"])
    measured_str = _canonical_int(measured)
    in_tol = within_tolerance(float(measured), asserted, regime)
    verdict = "ASSERT" if in_tol else "REFUTE_SOFT"

    return Skeptic(
        lens="A_requery",
        state=lens_state,
        verdict=verdict,
        measured_value=measured_str,
        confidence=0.90,
        reason=None if verdict == "ASSERT" else (
            f"measured={measured_str} vs asserted={claim.asserted_value}"  # type: ignore[attr-defined]
        ),
    )


async def _a_kind(
    conn: asyncpg.Connection,
    claim: object,
    lens_state: StateTuple,
) -> Skeptic:
    """Re-derive kind count via GROUP BY aggregation path.

    subject_key = 'kind:<kind_name>' → asserted_value = count for that kind.
    EXACT regime.
    """
    key: str = claim.subject_key  # type: ignore[attr-defined]
    asserted = float(claim.asserted_value)  # type: ignore[attr-defined]
    regime = regime_for(claim.subject_type)  # type: ignore[attr-defined]

    if not key.startswith("kind:"):
        return Skeptic(
            lens="A_requery",
            state=lens_state,
            verdict="ABSTAIN",
            measured_value=None,
            confidence=None,
            reason=f"lens_a_kind_unsupported_key_format:{key}",
        )

    kind_name = key.split(":", 1)[1]
    # GROUP BY path differs from direct WHERE kind=X
    row = await conn.fetchrow(
        """SELECT SUM(n) AS n
           FROM (SELECT kind, COUNT(*) AS n FROM entity GROUP BY kind) sub
           WHERE kind = $1::entity_kind""",
        kind_name,
    )
    measured = int(row["n"] or 0)
    measured_str = _canonical_int(measured)
    in_tol = within_tolerance(float(measured), asserted, regime)
    verdict = "ASSERT" if in_tol else "REFUTE_SOFT"

    return Skeptic(
        lens="A_requery",
        state=lens_state,
        verdict=verdict,
        measured_value=measured_str,
        confidence=0.90,
        reason=None if verdict == "ASSERT" else (
            f"measured={measured_str} vs asserted={claim.asserted_value}"  # type: ignore[attr-defined]
        ),
    )


async def _a_coverage(
    conn: asyncpg.Connection,
    claim: object,
    lens_state: StateTuple,
) -> Skeptic:
    """Re-derive coverage count via COUNT(DISTINCT entity_ulid).

    subject_key = 'coverage:<kind_name>'.  EXACT regime.
    """
    key: str = claim.subject_key  # type: ignore[attr-defined]
    asserted = float(claim.asserted_value)  # type: ignore[attr-defined]
    regime = regime_for(claim.subject_type)  # type: ignore[attr-defined]

    if not key.startswith("coverage:"):
        return Skeptic(
            lens="A_requery",
            state=lens_state,
            verdict="ABSTAIN",
            measured_value=None,
            confidence=None,
            reason=f"lens_a_coverage_unsupported_key:{key}",
        )

    kind_name = key.split(":", 1)[1]
    row = await conn.fetchrow(
        "SELECT COUNT(DISTINCT entity_ulid) AS n FROM entity WHERE kind = $1::entity_kind",
        kind_name,
    )
    measured = int(row["n"] or 0)
    measured_str = _canonical_int(measured)
    in_tol = within_tolerance(float(measured), asserted, regime)
    verdict = "ASSERT" if in_tol else "REFUTE_SOFT"

    return Skeptic(
        lens="A_requery",
        state=lens_state,
        verdict=verdict,
        measured_value=measured_str,
        confidence=0.90,
        reason=None if verdict == "ASSERT" else (
            f"measured={measured_str} vs asserted={claim.asserted_value}"  # type: ignore[attr-defined]
        ),
    )


async def _a_inventory(
    conn: asyncpg.Connection,
    claim: object,
    lens_state: StateTuple,
) -> Skeptic:
    """Re-count vehicles with price IS NOT NULL via FILTER clause aggregation.

    subject_key = 'inventory:<entity_ulid>'. DRIFT regime.
    """
    key: str = claim.subject_key  # type: ignore[attr-defined]
    asserted = float(claim.asserted_value)  # type: ignore[attr-defined]
    regime = regime_for(claim.subject_type)  # type: ignore[attr-defined]

    if not key.startswith("inventory:"):
        return Skeptic(
            lens="A_requery",
            state=lens_state,
            verdict="ABSTAIN",
            measured_value=None,
            confidence=None,
            reason=f"lens_a_inventory_unsupported_key:{key}",
        )

    entity_ulid = key.split(":", 1)[1]
    # FILTER clause differs from simple WHERE price IS NOT NULL subquery
    row = await conn.fetchrow(
        """SELECT COUNT(*) FILTER (WHERE price IS NOT NULL) AS n
           FROM vehicle
           WHERE entity_ulid = $1 AND status = 'available'""",
        entity_ulid,
    )
    measured = int(row["n"] or 0)
    measured_str = _canonical_int(measured)
    in_tol = within_tolerance(float(measured), asserted, regime)
    verdict = "ASSERT" if in_tol else "REFUTE_SOFT"

    return Skeptic(
        lens="A_requery",
        state=lens_state,
        verdict=verdict,
        measured_value=measured_str,
        confidence=0.90,
        reason=None if verdict == "ASSERT" else (
            f"measured={measured_str} vs asserted={claim.asserted_value}"  # type: ignore[attr-defined]
        ),
    )


async def _a_denominator(
    conn: asyncpg.Connection,
    claim: object,
    lens_state: StateTuple,
) -> Skeptic:
    """Re-read denominator point_est from denominator_estimate. EXACT regime.

    subject_key = 'denominator:<segment>' or 'denominator:<segment>:<province_code>'.
    """
    key: str = claim.subject_key  # type: ignore[attr-defined]
    asserted = float(claim.asserted_value)  # type: ignore[attr-defined]
    regime = regime_for(claim.subject_type)  # type: ignore[attr-defined]

    parts = key.split(":")
    if len(parts) < 2 or parts[0] != "denominator":
        return Skeptic(
            lens="A_requery",
            state=lens_state,
            verdict="ABSTAIN",
            measured_value=None,
            confidence=None,
            reason=f"lens_a_denominator_unsupported_key:{key}",
        )

    segment = parts[1]
    province_code: str | None = parts[2] if len(parts) >= 3 else None

    if province_code:
        row = await conn.fetchrow(
            """SELECT point_est FROM denominator_estimate
               WHERE segment = $1 AND province_code = $2
               ORDER BY created_at DESC LIMIT 1""",
            segment, province_code,
        )
    else:
        row = await conn.fetchrow(
            """SELECT point_est FROM denominator_estimate
               WHERE segment = $1 AND province_code IS NULL
               ORDER BY created_at DESC LIMIT 1""",
            segment,
        )

    if row is None:
        return Skeptic(
            lens="A_requery",
            state=lens_state,
            verdict="ABSTAIN",
            measured_value=None,
            confidence=None,
            reason=f"denominator_estimate_not_found:{key}",
        )

    measured = float(row["point_est"])
    measured_str = _canonical_int(measured)
    in_tol = within_tolerance(measured, asserted, regime)
    verdict = "ASSERT" if in_tol else "REFUTE_SOFT"

    return Skeptic(
        lens="A_requery",
        state=lens_state,
        verdict=verdict,
        measured_value=measured_str,
        confidence=0.90,
        reason=None if verdict == "ASSERT" else (
            f"measured={measured_str} vs asserted={claim.asserted_value}"  # type: ignore[attr-defined]
        ),
    )
