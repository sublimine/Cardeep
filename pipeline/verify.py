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


def _path_family(path_name: str) -> str:
    """Map a VAM path name to its collector FAMILY (V3 §4).

    The deep-ledger CHECK (chk_trustworthy_needs_quorum, 0026) computes family_n via
    cdp_distinct_families(verifier_paths) and requires >=2 distinct families for a
    TRUSTWORTHY verdict. This maps each path name (e.g. 'db_ingested', 'fetched',
    'source_declared') to a coarse collector family so that family_n is real. Unknown
    names collapse to a single 'other' family — so unproven orthogonality NEVER grants a
    quorum (Law I: better to under-certify than to certify a shared blind spot).
    """
    n = path_name.lower()
    if any(k in n for k in ("db", "ingest", "persist", "land", "stored", "cdp", "distinct", "join")):
        return "db"
    if any(k in n for k in ("fetch", "harvest", "scrape", "http", "api", "live", "cage", "pair", "page")):
        return "http"
    if any(k in n for k in ("declar", "source", "oracle", "header", "total", "numberofresults", "remaining")):
        return "source"
    if any(k in n for k in ("registr", "official", "dgt", "cnae", "faconauto", "borme", "census")):
        return "registral"
    return "other"


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
    measured_by_observation: bool = False,
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
    # Deep-ledger 0026 contract: the DB CHECK chk_trustworthy_needs_quorum requires
    # quorum_n>=2 AND family_n>=2 AND origin_n>=2, recomputed from independent_values
    # (numeric array) and verifier_paths (array of {family,origin} objects). We compute
    # the SAME independence here so a TRUSTWORTHY we emit ALWAYS satisfies the CHECK —
    # otherwise the INSERT raises CheckViolation and record_count_verdict deadlocks
    # (the bug the audit caught: 989/991 TRUSTWORTHY had quorum_n=0 from string paths).
    families = {_path_family(k) for k, _ in items}
    origins = {k for k, _ in items}
    has_independence = len(families) >= 2 and len(origins) >= 2
    verifier_paths_json = json.dumps(
        [{"family": _path_family(k), "origin": k} for k, _ in items]
    )
    independent_values_json = json.dumps(values)
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
        modal_ok = top_n >= 2 and not rivals and primary_agrees
        # Soft (drift) agreement: >=2 paths whose FULL spread (hi-lo)/hi is within tolerance.
        # The spread includes the primary path, so a divergent primary (silent ingest loss)
        # widens it past tolerance and fails here — tolerance never hides real disagreement.
        # This is len(values)>=2, NOT top_n>=2: continuous 2-path comparisons (e.g. coverage
        # captured_db=274144 vs declared_total=271981, 0.8% apart) are never EXACTLY equal, so a
        # top_n>=2 requirement forced them to REFUTED — which then blocked reconcile_gone (delta
        # bajas) for every healthy-coverage source. Drift agreement is NOT enough to CERTIFY:
        # the DB CHECK chk_trustworthy_needs_quorum demands quorum_n>=2 (an EXACT modal cluster),
        # so drift-but-not-exact resolves to UNVERIFIED — honest ("cannot quorum-certify") and
        # crucially NOT REFUTED, so downstream consumers that only gate on REFUTED proceed.
        drift_ok = len(values) >= 2 and divergence <= tolerance
        # EXACT_ZERO fix (P09-S1): a modal value of 0 is almost always "no data observed"
        # (absence / fetch error / empty metric), NOT a measured empty set. A zero quorum
        # must NOT certify TRUSTWORTHY unless the caller explicitly OBSERVED the emptiness
        # (measured_by_observation=True). Otherwise 0==0==0 across orthogonal paths certified
        # absence-as-truth (10 web_generic recipes carried vam_verdict TRUSTWORTHY with
        # fetched:0). Better a hole than a lie — a non-observed zero falls to UNVERIFIED.
        zero_certifiable = top_val != 0 or measured_by_observation
        if modal_ok and has_independence and zero_certifiable:
            # Exact modal quorum (>=2 identical values) across >=2 orthogonal families/origins:
            # the ONLY shape the DB invariant accepts as TRUSTWORTHY.
            verdict = "TRUSTWORTHY"
        elif modal_ok or drift_ok:
            # Either a same-family exact cluster (no independence) OR soft drift agreement
            # (within tolerance but not exactly equal): values do NOT disagree, but cannot be
            # certified under the quorum invariant → UNVERIFIED (never REFUTED).
            verdict = "UNVERIFIED"
        else:
            verdict = "REFUTED"

    if resolved_interval is not None:
        # expires_at computed server-side so it is consistent with now() in the same
        # transaction as created_at.  asyncpg maps timedelta → Postgres INTERVAL
        # (OID 1186) natively.  We use ``now() + $12`` — no explicit cast needed
        # because the client codec resolves the INTERVAL type from the Python value.
        new_id = await conn.fetchval(
            """INSERT INTO verification_verdict
                 (subject_type, subject_key, claim, primary_value, primary_path,
                  verifier_paths, independent_values, divergence, verdict, evidence,
                  claim_kind, expires_at)
               VALUES ($1,$2,$3,$4,$5,$6::jsonb,$7::jsonb,$8,$9,$10,
                       $11, now() + $12)
               RETURNING id""",
            subject_type, subject_key, claim, str(primary_value), primary_path,
            verifier_paths_json, independent_values_json, divergence, verdict,
            f"paths={paths}",
            claim_kind, resolved_interval,
        )
    else:
        # Eternal seal (expires_at=NULL): structural verdicts that should never expire.
        new_id = await conn.fetchval(
            """INSERT INTO verification_verdict
                 (subject_type, subject_key, claim, primary_value, primary_path,
                  verifier_paths, independent_values, divergence, verdict, evidence,
                  claim_kind)
               VALUES ($1,$2,$3,$4,$5,$6::jsonb,$7::jsonb,$8,$9,$10,$11)
               RETURNING id""",
            subject_type, subject_key, claim, str(primary_value), primary_path,
            verifier_paths_json, independent_values_json, divergence, verdict,
            f"paths={paths}",
            claim_kind,
        )

    # D-supersession (audit P2): the newest verdict for a (subject_type, subject_key, claim) is the
    # ONLY active one. Mark all prior actives as superseded so the read-side filter
    # `superseded_by IS NULL` (evict Gate-1, inquisition scheduler, idx_verdict_latest) sees exactly
    # one current verdict instead of an unbounded accumulation of historical TRUSTWORTHY/REFUTED.
    await conn.execute(
        """UPDATE verification_verdict SET superseded_by = $1
            WHERE subject_type = $2 AND subject_key = $3 AND claim = $4
              AND id <> $1 AND superseded_by IS NULL""",
        new_id, subject_type, subject_key, claim,
    )

    return verdict
