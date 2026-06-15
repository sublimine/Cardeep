"""WF-INQUISITION cadence — verdict TTL re-verification scheduler (SU-B2 δ).

Finds verification_verdict rows whose TTL has lapsed (expires_at < now()) and
opens/refreshes a gestion_item in the RESEARCH lane so that a human or automated
workflow can trigger re-verification.

Design constraints
------------------
- €0: no scraping, no LLM, no HTTP calls. Pure DB reads + gestion_item upserts.
- MVCC-safe: uses gestionador.route.open_or_refresh (INSERT … ON CONFLICT DO UPDATE).
  Never issues UPDATE on non-mutated rows directly.
- Idempotent: re-running produces at most one open gestion_item per
  (subject_type, subject_key, claim) tuple regardless of how often it is run.
- Grandfathered verdicts (expires_at IS NULL) are never touched — they are
  structural seals and get re-verified when their subject is re-harvested.
- Already-superseded verdicts (superseded_by IS NOT NULL) are excluded: a newer
  verdict has already addressed the chain; no re-verification is needed.

CLI usage
---------
    python -m pipeline.ops.inquisition_schedule

Or directly:
    python pipeline/ops/inquisition_schedule.py

Both connect via the CARDEEP_DSN environment variable, run schedule_reverification,
and print the summary as JSON to stdout.
"""
from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Any

import asyncpg

from pipeline.gestionador.detect import AnomalyResult
from pipeline.gestionador.route import open_or_refresh

# ---------------------------------------------------------------------------
# The query that drives the cadence.
#
# Inclusion criteria (each is mandatory):
#   1. expires_at IS NOT NULL  — excludes grandfathered eternal seals.
#   2. expires_at < now()      — the TTL has lapsed; a re-verification is due.
#   3. superseded_by IS NULL   — the latest non-superseded verdict for this
#                                subject+claim; a newer verdict already exists
#                                if superseded_by is set.
#
# The partial index idx_verdict_expiry covers criteria 1 automatically, making
# this query fast even on large verdict tables.
# ---------------------------------------------------------------------------
_FIND_EXPIRED_SQL = """
SELECT
    id,
    subject_type,
    subject_key,
    claim,
    claim_kind,
    verdict,
    expires_at,
    created_at
FROM verification_verdict
WHERE expires_at IS NOT NULL
  AND expires_at < now()
  AND superseded_by IS NULL
ORDER BY expires_at ASC
"""

# Severity derivation thresholds (days overdue).
# These map to the same vocabulary used by the existing detectors:
# 'info' | 'warning' | 'critical'.  No new scale is introduced.
_OVERDUE_WARN_DAYS: float = 1.0    # overdue > 1 day  → warning
_OVERDUE_CRIT_DAYS: float = 7.0    # overdue > 7 days → critical


def _overdue_seconds(expires_at: datetime) -> float:
    """Return how many seconds past the expiry the verdict is, as a float."""
    now_utc = datetime.now(tz=timezone.utc)
    # expires_at from asyncpg is timezone-aware (TIMESTAMPTZ).
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    delta = now_utc - expires_at
    return max(delta.total_seconds(), 0.0)


def _severity_from_overdue(overdue_seconds: float) -> str:
    """Map overdue duration to the existing detector severity vocabulary.

    Uses the same thresholds as staleness (3.4) — the problem is analogous:
    a verdict is stale, and the staleness ratio determines urgency.
    """
    overdue_days = overdue_seconds / 86400.0
    if overdue_days > _OVERDUE_CRIT_DAYS:
        return "critical"
    if overdue_days > _OVERDUE_WARN_DAYS:
        return "warning"
    return "info"


def _score_from_overdue(overdue_seconds: float) -> float:
    """Normalised anomaly score in [0, 1] proportional to overdue duration.

    Saturates at 1.0 when overdue by >= 30 days.
    """
    overdue_days = overdue_seconds / 86400.0
    return min(overdue_days / 30.0, 1.0)


async def find_expired(conn: asyncpg.Connection) -> list[asyncpg.Record]:
    """Return all lapsed, non-superseded verification_verdict rows.

    Uses idx_verdict_expiry (partial index on expires_at WHERE IS NOT NULL)
    for efficient scan.

    Returns
    -------
    list[asyncpg.Record]
        Rows with columns: id, subject_type, subject_key, claim, claim_kind,
        verdict, expires_at, created_at.  Empty list when nothing is expired.
    """
    return await conn.fetch(_FIND_EXPIRED_SQL)


async def schedule_reverification(
    conn: asyncpg.Connection,
    *,
    actor: str = "inquisition_cadence",
) -> dict[str, Any]:
    """Queue re-verification for every lapsed verdict.

    For each expired verification_verdict row, builds an AnomalyResult with
    detector='stale_verdict' and calls open_or_refresh via the gestionador.
    The dedupe_key guarantees exactly one open gestion_item per
    (subject_type, subject_key, claim) tuple — idempotent refresh otherwise.

    Parameters
    ----------
    conn:
        Live asyncpg connection.
    actor:
        Actor label written to gestion_transition rows.  Defaults to
        'inquisition_cadence'.

    Returns
    -------
    dict
        Summary with keys:
          expired_found       — total expired rows found
          items_opened_or_refreshed — items written to gestion_item
          by_claim_kind       — count of expired rows per claim_kind
    """
    expired_rows = await find_expired(conn)

    by_claim_kind: dict[str, int] = {}
    items_opened: int = 0

    for row in expired_rows:
        # Tally by claim_kind for the summary.
        ck = row["claim_kind"] or "count"
        by_claim_kind[ck] = by_claim_kind.get(ck, 0) + 1

        expires_at: datetime = row["expires_at"]
        overdue_sec = _overdue_seconds(expires_at)
        severity = _severity_from_overdue(overdue_sec)
        score = _score_from_overdue(overdue_sec)

        subject_type: str = row["subject_type"]
        subject_key: str = row["subject_key"]
        claim: str = row["claim"]
        verdict_id: int = row["id"]
        original_verdict: str = row["verdict"]
        created_at: datetime = row["created_at"]

        # Ensure expires_at is timezone-aware for isoformat().
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        # dedupe_key: one item per stale (subject_type, subject_key, claim).
        # Omits verdict_id deliberately — the item represents the ongoing need
        # to re-verify this subject+claim, not a specific verdict instance.
        dedupe_key = f"stale_verdict:{subject_type}:{subject_key}:{claim}"

        anomaly = AnomalyResult(
            detector="stale_verdict",
            subject_type=subject_type,
            subject_key=subject_key,
            severity=severity,
            score=score,
            measured={
                "verdict_id":         verdict_id,
                "claim":              claim,
                "claim_kind":         ck,
                "original_verdict":   original_verdict,
                "expires_at":         expires_at.isoformat(),
                "overdue_seconds":    round(overdue_sec),
                "overdue_days":       round(overdue_sec / 86400.0, 2),
            },
            baseline={
                "policy":             "WF-INQUISITION δ (SU-B2)",
                "claim_kind":         ck,
                "warn_threshold_days": _OVERDUE_WARN_DAYS,
                "crit_threshold_days": _OVERDUE_CRIT_DAYS,
                "created_at":         created_at.isoformat() if created_at else None,
            },
            lane="RESEARCH",
            # stale_verdict never auto-quarantines: the data may still be valid,
            # it merely needs a fresh re-verification pass.
            quarantines=False,
            dedupe_key=dedupe_key,
        )

        await open_or_refresh(conn, anomaly, actor=actor)
        items_opened += 1

    return {
        "expired_found":            len(expired_rows),
        "items_opened_or_refreshed": items_opened,
        "by_claim_kind":            by_claim_kind,
    }


# ---------------------------------------------------------------------------
# CLI entry point — WF-INQUISITION cadence command
# ---------------------------------------------------------------------------

async def main() -> None:
    """Connect, schedule re-verifications, print JSON summary.

    Safe to run repeatedly (idempotent).  Reads CARDEEP_DSN from the
    environment.  Exits 1 if DSN is missing or connection fails.
    """
    dsn = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
    conn = await asyncpg.connect(dsn)
    try:
        summary = await schedule_reverification(conn)
    finally:
        await conn.close()

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
