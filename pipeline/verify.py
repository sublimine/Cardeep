"""VERIFICAR — VAM count quorum. Persists a verification_verdict.

A count is TRUSTWORTHY only if >=2 orthogonal paths agree within tolerance.

WF-INQUISITION δ (2026-06-15):
  - Added claim_kind and expires_in parameters (backward-compatible defaults).
  - New verdicts now carry expires_at = now() + ttl_for(claim_kind).
  - Existing callers that do not pass claim_kind continue to receive claim_kind='count'
    and a 7-day TTL, which is the shortest operational cadence (fail-safe).
  - Grandfathered structural seals (B1/β/B7) written before this change keep
    expires_at=NULL (eternal) — they are never backfilled.

asyncpg interval handling
--------------------------
asyncpg maps Python datetime.timedelta → Postgres INTERVAL (OID 1186) natively.
Passing a raw str as an INTERVAL parameter raises DataError because the client
codec expects a timedelta.  verify_ttl.ttl_for() returns timedelta, so callers
never need an explicit cast.  The INSERT uses ``now() + $12`` (not ``$12::interval``)
because asyncpg resolves the type from the Python value, not the SQL cast.
"""
from __future__ import annotations

import json
from datetime import timedelta

import asyncpg

from pipeline.verify_ttl import ttl_for


async def record_count_verdict(
    conn: asyncpg.Connection,
    *,
    subject_type: str,
    subject_key: str,
    claim: str,
    paths: dict[str, int],
    tolerance: float = 0.0,
    claim_kind: str = "count",
    expires_in: timedelta | None = None,
) -> str:
    """paths: {path_name: count}. Quorum rule (mandate: ">=2 orthogonal paths agree"):
    TRUSTWORTHY when the modal value is supported by >=2 paths and no rival value also
    reaches >=2 (a clean majority). A lone divergent path (e.g. a source counter that
    over-counts duplicates) does not refute when >=2 independent paths agree.

    Parameters
    ----------
    conn:
        Live asyncpg connection.
    subject_type:
        Verification subject type (e.g. 'entity_inventory', 'source_coverage').
    subject_key:
        Unique key within subject_type (e.g. a cdp_code or source_key).
    claim:
        Human-readable claim being verified.
    paths:
        Dict of {path_name: count} — the orthogonal evidence paths for the quorum.
    tolerance:
        Relative divergence tolerance for a TRUSTWORTHY verdict under soft quorum.
    claim_kind:
        Kind of claim per the verification_verdict CHECK constraint.
        One of: 'count', 'field_fill', 'existence', 'freshness', 'coverage',
        'denominator'.  Defaults to 'count'.  All existing callers omit this
        parameter and continue to receive 'count' unchanged.
    expires_in:
        Explicit timedelta override for expires_at.
        When None (default), the TTL is derived from claim_kind via ttl_for().
        Pass timedelta(0) (zero delta) to suppress TTL and produce expires_at=NULL
        (structural / eternal seal — use sparingly and only for non-operational
        verdicts that should never expire).
    """
    from collections import Counter

    # Resolve the timedelta that will be passed to Postgres.
    # timedelta(0) (zero) means "no expiry" (NULL path, eternal seal).
    # None triggers the policy lookup by claim_kind.
    # asyncpg maps timedelta → INTERVAL (OID 1186) natively; never pass a str.
    if expires_in is None:
        resolved_interval: timedelta | None = ttl_for(claim_kind)
    elif expires_in == timedelta(0):
        resolved_interval = None   # explicit eternal seal
    else:
        resolved_interval = expires_in

    items = [(k, v) for k, v in paths.items() if v is not None]
    values = [v for _, v in items]
    primary_path, primary_value = next(iter(paths.items()))
    if len(values) < 2:
        verdict, divergence = "UNVERIFIED", None
    else:
        freq = Counter(values)
        (top_val, top_n), = freq.most_common(1)
        rivals = [val for val, n in freq.items() if n >= 2 and val != top_val]
        lo, hi = min(values), max(values)
        divergence = (hi - lo) / hi if hi else 0.0
        # The primary path (what actually landed, e.g. db_ingested) MUST agree with at
        # least one other path — otherwise a fetched/declared pair could mask real
        # ingestion loss (collisions/skips). Silent data loss never reads as TRUSTWORTHY.
        primary_agrees = sum(1 for v in values if v == primary_value) >= 2
        if top_n >= 2 and not rivals and primary_agrees:
            verdict = "TRUSTWORTHY"
        elif divergence <= tolerance:
            verdict = "TRUSTWORTHY"
        else:
            verdict = "REFUTED"

    if resolved_interval is not None:
        # expires_at computed server-side so it is consistent with now() in the same
        # transaction as created_at.  asyncpg maps timedelta → Postgres INTERVAL
        # (OID 1186) natively.  We use ``now() + $12`` — no explicit cast needed
        # because the client codec resolves the INTERVAL type from the Python value.
        await conn.execute(
            """INSERT INTO verification_verdict
                 (subject_type, subject_key, claim, primary_value, primary_path,
                  verifier_paths, independent_values, divergence, verdict, evidence,
                  claim_kind, expires_at)
               VALUES ($1,$2,$3,$4,$5,$6::jsonb,$7::jsonb,$8,$9,$10,
                       $11, now() + $12)""",
            subject_type, subject_key, claim, str(primary_value), primary_path,
            json.dumps(list(paths.keys())), json.dumps(paths), divergence, verdict,
            f"paths={paths}",
            claim_kind, resolved_interval,
        )
    else:
        # Eternal seal (expires_at=NULL): structural verdicts that should never expire.
        await conn.execute(
            """INSERT INTO verification_verdict
                 (subject_type, subject_key, claim, primary_value, primary_path,
                  verifier_paths, independent_values, divergence, verdict, evidence,
                  claim_kind)
               VALUES ($1,$2,$3,$4,$5,$6::jsonb,$7::jsonb,$8,$9,$10,$11)""",
            subject_type, subject_key, claim, str(primary_value), primary_path,
            json.dumps(list(paths.keys())), json.dumps(paths), divergence, verdict,
            f"paths={paths}",
            claim_kind,
        )

    return verdict
