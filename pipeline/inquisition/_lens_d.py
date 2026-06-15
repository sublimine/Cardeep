"""Lens D — cross-source corroboration (§3.4, SU-B2 ε3).

Private module. Import via pipeline.inquisition.lenses, not directly.

StateTuple independence: source=<DIFFERENT_SOURCE>, tool='sql', path='lens_d_xsrc'
→ differs from any ingest producer on source+path → D ≥ 2 (often D=3).

Cross-source witnesses confirmed in the live DB (verified 2026-06-15):
    'dgt_cat'              → 1 292 desguace (official DGT register, Catalonia)
    'wallapop_wholesale'   → 224 822 entities (independent commercial platform)
    'milanuncios_wholesale'→ 123 600 entities (independent commercial platform)

Applicable subject_types: count, coverage, kind, denominator.
"""
from __future__ import annotations

import asyncpg

from pipeline.inquisition.models import Skeptic, StateTuple, regime_for
from pipeline.inquisition.quorum import within_tolerance

_XSRC_DESGUACE_WITNESS: str = "dgt_cat"
_XSRC_GENERAL_WITNESSES: list[str] = [
    "wallapop_wholesale",
    "milanuncios_wholesale",
]


def _canonical_int(value: int | float) -> str:
    return str(int(round(value)))


def _d_state(source: str, cache: str) -> StateTuple:
    return StateTuple(source=source, tool="sql", cache=cache, path="lens_d_xsrc")


async def _source_health_factor(
    conn: asyncpg.Connection,
    source_key: str,
) -> float:
    """Confidence multiplier from source_health.status.

    healthy → 1.0 | degraded → 0.85 | down/unknown → 0.70
    """
    row = await conn.fetchrow(
        "SELECT status FROM source_health WHERE source_key = $1",
        source_key,
    )
    if row is None:
        return 0.70
    return {"healthy": 1.0, "degraded": 0.85}.get(row["status"], 0.70)


async def lens_d_cross_source(
    conn: asyncpg.Connection,
    claim: object,
) -> Skeptic:
    """Corroborate from an orthogonal source already in the DB.

    Routes by subject_type + subject_key to the most appropriate witness:
        coverage:desguace         → dgt_cat (official registral)
        coverage:<other kind>     → wallapop_wholesale
        count:kind:<name>         → wallapop_wholesale
        count:province:<code>     → wallapop_wholesale
        kind:<name>               → wallapop_wholesale (fallback: milanuncios)
        denominator:<segment>     → denominator_estimate.sources_used ≥ 2

    Returns ABSTAIN(reason='no_cross_source_witness:…') if no witness exists.
    """
    subject_type: str = claim.subject_type  # type: ignore[attr-defined]
    key: str = claim.subject_key  # type: ignore[attr-defined]
    st: StateTuple = claim.producer_state  # type: ignore[attr-defined]

    if subject_type == "coverage" and key == "coverage:desguace":
        return await _d_coverage_desguace(conn, claim, st)

    if subject_type == "coverage" and key.startswith("coverage:"):
        kind_name = key.split(":", 1)[1]
        return await _d_coverage_kind(conn, claim, st, kind_name, "wallapop_wholesale")

    if subject_type == "count":
        return await _d_count(conn, claim, st)

    if subject_type == "kind" and key.startswith("kind:"):
        kind_name = key.split(":", 1)[1]
        return await _d_kind(conn, claim, st, kind_name)

    if subject_type == "denominator":
        return await _d_denominator(conn, claim, st)

    lens_state = _d_state("no_witness", st.cache)
    return Skeptic(
        lens="D_cross_source",
        state=lens_state,
        verdict="ABSTAIN",
        measured_value=None,
        confidence=None,
        reason=f"no_cross_source_witness:{subject_type}:{key}",
    )


async def _d_coverage_desguace(
    conn: asyncpg.Connection,
    claim: object,
    producer_state: StateTuple,
) -> Skeptic:
    """Official DGT Catalan register witness for desguace entity count (1 292)."""
    lens_state = _d_state(_XSRC_DESGUACE_WITNESS, producer_state.cache)

    row = await conn.fetchrow(
        """SELECT COUNT(DISTINCT e.entity_ulid) AS n
           FROM entity e
           JOIN entity_source es ON e.entity_ulid = es.entity_ulid
           WHERE es.source_key = $1 AND e.kind = 'desguace'::entity_kind""",
        _XSRC_DESGUACE_WITNESS,
    )
    measured = int(row["n"] or 0)
    measured_str = _canonical_int(measured)
    asserted = float(claim.asserted_value)  # type: ignore[attr-defined]
    regime = regime_for(claim.subject_type)  # type: ignore[attr-defined]
    in_tol = within_tolerance(float(measured), asserted, regime)
    verdict = "ASSERT" if in_tol else "REFUTE_SOFT"
    hf = await _source_health_factor(conn, _XSRC_DESGUACE_WITNESS)

    return Skeptic(
        lens="D_cross_source",
        state=lens_state,
        verdict=verdict,
        measured_value=measured_str,
        confidence=round(0.80 * hf, 4),
        reason=None if verdict == "ASSERT" else (
            f"dgt_cat_measured={measured_str} vs asserted={claim.asserted_value}"  # type: ignore[attr-defined]
        ),
    )


async def _d_coverage_kind(
    conn: asyncpg.Connection,
    claim: object,
    producer_state: StateTuple,
    kind_name: str,
    witness_source: str,
) -> Skeptic:
    """Commercial witness for coverage count of a given kind."""
    lens_state = _d_state(witness_source, producer_state.cache)

    row = await conn.fetchrow(
        """SELECT COUNT(DISTINCT e.entity_ulid) AS n
           FROM entity e
           JOIN entity_source es ON e.entity_ulid = es.entity_ulid
           WHERE es.source_key = $1 AND e.kind = $2::entity_kind""",
        witness_source, kind_name,
    )
    measured = int(row["n"] or 0)

    if measured == 0:
        return Skeptic(
            lens="D_cross_source",
            state=lens_state,
            verdict="ABSTAIN",
            measured_value=None,
            confidence=None,
            reason=f"no_cross_source_witness:coverage:{kind_name}:{witness_source}",
        )

    measured_str = _canonical_int(measured)
    asserted = float(claim.asserted_value)  # type: ignore[attr-defined]
    regime = regime_for(claim.subject_type)  # type: ignore[attr-defined]
    in_tol = within_tolerance(float(measured), asserted, regime)
    verdict = "ASSERT" if in_tol else "REFUTE_SOFT"
    hf = await _source_health_factor(conn, witness_source)

    return Skeptic(
        lens="D_cross_source",
        state=lens_state,
        verdict=verdict,
        measured_value=measured_str,
        confidence=round(0.80 * hf, 4),
        reason=None if verdict == "ASSERT" else (
            f"{witness_source}_measured={measured_str} vs asserted={claim.asserted_value}"  # type: ignore[attr-defined]
        ),
    )


async def _d_count(
    conn: asyncpg.Connection,
    claim: object,
    producer_state: StateTuple,
) -> Skeptic:
    """Cross-source count via wallapop_wholesale as secondary commercial witness."""
    key: str = claim.subject_key  # type: ignore[attr-defined]
    asserted = float(claim.asserted_value)  # type: ignore[attr-defined]
    regime = regime_for(claim.subject_type)  # type: ignore[attr-defined]
    witness = "wallapop_wholesale"
    lens_state = _d_state(witness, producer_state.cache)

    if key.startswith("kind:"):
        kind_name = key.split(":", 1)[1]
        row = await conn.fetchrow(
            """SELECT COUNT(DISTINCT e.entity_ulid) AS n
               FROM entity e
               JOIN entity_source es ON e.entity_ulid = es.entity_ulid
               WHERE es.source_key = $1 AND e.kind = $2::entity_kind""",
            witness, kind_name,
        )
    elif key.startswith("province:"):
        province_code = key.split(":", 1)[1]
        row = await conn.fetchrow(
            """SELECT COUNT(DISTINCT e.entity_ulid) AS n
               FROM entity e
               JOIN entity_source es ON e.entity_ulid = es.entity_ulid
               WHERE es.source_key = $1 AND e.province_code = $2""",
            witness, province_code,
        )
    else:
        return Skeptic(
            lens="D_cross_source",
            state=lens_state,
            verdict="ABSTAIN",
            measured_value=None,
            confidence=None,
            reason=f"no_cross_source_witness:count:{key}",
        )

    measured = int(row["n"] or 0)
    if measured == 0:
        return Skeptic(
            lens="D_cross_source",
            state=lens_state,
            verdict="ABSTAIN",
            measured_value=None,
            confidence=None,
            reason=f"no_cross_source_witness:count:{key}:{witness}",
        )

    measured_str = _canonical_int(measured)
    in_tol = within_tolerance(float(measured), asserted, regime)
    verdict = "ASSERT" if in_tol else "REFUTE_SOFT"
    hf = await _source_health_factor(conn, witness)

    return Skeptic(
        lens="D_cross_source",
        state=lens_state,
        verdict=verdict,
        measured_value=measured_str,
        confidence=round(0.80 * hf, 4),
        reason=None if verdict == "ASSERT" else (
            f"{witness}_measured={measured_str} vs asserted={claim.asserted_value}"  # type: ignore[attr-defined]
        ),
    )


async def _d_kind(
    conn: asyncpg.Connection,
    claim: object,
    producer_state: StateTuple,
    kind_name: str,
) -> Skeptic:
    """Cross-source kind count from wallapop (fallback: milanuncios)."""
    asserted = float(claim.asserted_value)  # type: ignore[attr-defined]
    regime = regime_for(claim.subject_type)  # type: ignore[attr-defined]

    for witness in _XSRC_GENERAL_WITNESSES:
        lens_state = _d_state(witness, producer_state.cache)
        row = await conn.fetchrow(
            """SELECT COUNT(DISTINCT e.entity_ulid) AS n
               FROM entity e
               JOIN entity_source es ON e.entity_ulid = es.entity_ulid
               WHERE es.source_key = $1 AND e.kind = $2::entity_kind""",
            witness, kind_name,
        )
        measured = int(row["n"] or 0)
        if measured > 0:
            measured_str = _canonical_int(measured)
            in_tol = within_tolerance(float(measured), asserted, regime)
            verdict = "ASSERT" if in_tol else "REFUTE_SOFT"
            hf = await _source_health_factor(conn, witness)
            return Skeptic(
                lens="D_cross_source",
                state=lens_state,
                verdict=verdict,
                measured_value=measured_str,
                confidence=round(0.80 * hf, 4),
                reason=None if verdict == "ASSERT" else (
                    f"{witness}_measured={measured_str} vs asserted={claim.asserted_value}"  # type: ignore[attr-defined]
                ),
            )

    lens_state = _d_state("no_witness", producer_state.cache)
    return Skeptic(
        lens="D_cross_source",
        state=lens_state,
        verdict="ABSTAIN",
        measured_value=None,
        confidence=None,
        reason=f"no_cross_source_witness:kind:{kind_name}",
    )


async def _d_denominator(
    conn: asyncpg.Connection,
    claim: object,
    producer_state: StateTuple,
) -> Skeptic:
    """Cross-check denominator via sources_used ≥ 2 in denominator_estimate.

    The 'cross-source' corroboration here is the multi-source provenance
    already embedded in denominator_estimate.sources_used. If the estimate
    integrates ≥ 2 independent sources, we treat the point_est as a
    cross-corroborated witness of the asserted value.
    """
    key: str = claim.subject_key  # type: ignore[attr-defined]
    parts = key.split(":")
    lens_state = _d_state("denominator_estimate", producer_state.cache)

    if len(parts) < 2:
        return Skeptic(
            lens="D_cross_source",
            state=lens_state,
            verdict="ABSTAIN",
            measured_value=None,
            confidence=None,
            reason=f"no_cross_source_witness:denominator:{key}",
        )

    segment = parts[1]
    province_code: str | None = parts[2] if len(parts) >= 3 else None

    if province_code:
        row = await conn.fetchrow(
            """SELECT point_est, sources_used FROM denominator_estimate
               WHERE segment = $1 AND province_code = $2
               ORDER BY created_at DESC LIMIT 1""",
            segment, province_code,
        )
    else:
        row = await conn.fetchrow(
            """SELECT point_est, sources_used FROM denominator_estimate
               WHERE segment = $1 AND province_code IS NULL
               ORDER BY created_at DESC LIMIT 1""",
            segment,
        )

    if row is None:
        return Skeptic(
            lens="D_cross_source",
            state=lens_state,
            verdict="ABSTAIN",
            measured_value=None,
            confidence=None,
            reason=f"no_cross_source_witness:denominator_estimate_missing:{key}",
        )

    sources_used = row["sources_used"]
    n_sources = len(sources_used) if isinstance(sources_used, list) else 0

    if n_sources < 2:
        return Skeptic(
            lens="D_cross_source",
            state=lens_state,
            verdict="ABSTAIN",
            measured_value=None,
            confidence=None,
            reason=f"no_cross_source_witness:denominator_single_source:{key}",
        )

    measured = float(row["point_est"])
    measured_str = _canonical_int(measured)
    asserted = float(claim.asserted_value)  # type: ignore[attr-defined]
    regime = regime_for(claim.subject_type)  # type: ignore[attr-defined]
    in_tol = within_tolerance(measured, asserted, regime)
    verdict = "ASSERT" if in_tol else "REFUTE_SOFT"

    return Skeptic(
        lens="D_cross_source",
        state=lens_state,
        verdict=verdict,
        measured_value=measured_str,
        confidence=0.80,
        reason=None if verdict == "ASSERT" else (
            f"denom_measured={measured_str} vs asserted={claim.asserted_value}"  # type: ignore[attr-defined]
        ),
    )
