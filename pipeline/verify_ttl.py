"""VERIFY TTL — Verdict freshness TTL policy (WF-INQUISITION δ).

Maps claim_kind → datetime.timedelta for expires_at computation.
Pure, side-effect-free module: import-safe, easily unit-tested.

Design rationale
----------------
Each claim_kind has a different operational cadence:
  - 'count'      : 7 days  — entity inventory counts change weekly (scrapers run
                   ~daily but we tolerate one full weekly cycle before forcing a
                   re-check).
  - 'freshness'  : 1 day   — freshness claims are intrinsically time-bounded; a
                   freshness seal older than 24h is stale by definition.
  - 'coverage'   : 14 days — coverage is driven by harvest campaigns that run less
                   frequently than entity-level counts; two-week window is reasonable.
  - 'field_fill' : 14 days — field completeness drifts slowly; aligns with coverage.
  - 'existence'  : 30 days — entity existence re-confirmation cycles monthly
                   (mirrors STALENESS_TTL['_entity'] = 90d / 3 windows).
  - 'denominator': 30 days — Chapman/Chao2 denominator estimates are expensive to
                   recompute; monthly cadence is correct.

Unknown kind falls back to DEFAULT_TTL ('count' = timedelta(days=7)) — fail-safe
to the SHORTEST meaningful operational cadence, never to an infinite (NULL) seal.
This ensures unknown claim kinds are treated as operational (not structural) and
get re-verified on a weekly basis rather than silently becoming eternal.

timedelta instead of interval strings
--------------------------------------
asyncpg maps Python datetime.timedelta to the Postgres INTERVAL type natively
(pg_type OID 1186).  Passing a raw str to a parameter bound as INTERVAL causes
asyncpg to raise DataError because the client-side codec expects a timedelta
object, not a string.  We return timedelta here so callers never need to manage
the conversion.  The human-readable labels in the docstring remain the source of
truth for the policy intent.
"""
from __future__ import annotations

from datetime import timedelta

# ---------------------------------------------------------------------------
# TTL policy table
# ---------------------------------------------------------------------------

#: claim_kind → timedelta for expires_at.
#: asyncpg encodes timedelta as Postgres INTERVAL natively (OID 1186).
VERDICT_TTL: dict[str, timedelta] = {
    "count":       timedelta(days=7),
    "freshness":   timedelta(days=1),
    "coverage":    timedelta(days=14),
    "field_fill":  timedelta(days=14),
    "existence":   timedelta(days=30),
    "denominator": timedelta(days=30),
}

#: Default TTL used when claim_kind is not found in VERDICT_TTL.
#: Chooses the shortest meaningful operational cadence to err on the side of
#: more frequent re-verification rather than silently leaving verdicts stale.
DEFAULT_TTL: timedelta = VERDICT_TTL["count"]


def ttl_for(claim_kind: str) -> timedelta:
    """Return the timedelta TTL for the given claim_kind.

    Parameters
    ----------
    claim_kind:
        One of 'count', 'freshness', 'coverage', 'field_fill', 'existence',
        'denominator'.  Unrecognised values fall back to DEFAULT_TTL.

    Returns
    -------
    datetime.timedelta
        The TTL as a Python timedelta.  asyncpg encodes this as a Postgres
        INTERVAL transparently, so callers can pass the return value directly
        as a query parameter.
    """
    return VERDICT_TTL.get(claim_kind, DEFAULT_TTL)
