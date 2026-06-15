"""V3 Inquisition — Prosecutor (SU-B2 ε4).

Public API
----------
prosecute_claim(conn, claim_row) -> dict
    Prosecute a single inquisition_claim atomically.

prosecute_pending(conn, *, limit, actor) -> dict
    Poll PENDING claims and prosecute them.

emit_claim_from_verdict(conn, verification_verdict_row) -> str
    Harvest helper: convert a VAM verification_verdict into an inquisition_claim.

CLI
---
    python -m pipeline.inquisition.prosecutor
    CARDEEP_DSN=postgresql://... python pipeline/inquisition/prosecutor.py

Design decisions
----------------
- prosecute_claim is ATOMIC: it wraps the whole prosecution (PENDING→PROSECUTING,
  skeptic INSERTs, verdict INSERT, →DECIDED, and the router's gestion_item) in a
  single ``conn.transaction()``.  On any failure the transaction rolls back, so
  the claim's status reverts to PENDING (the PROSECUTING write never commits) and
  it is re-eligible on the next poll — there is NO half-prosecuted PROSECUTING
  zombie and no orphan partial skeptic rows.  Plain transaction() (no explicit
  isolation level) nests as a SAVEPOINT when a test already opened a transaction,
  so the same code is correct in production batch and under the test _Rollback
  pattern (no nested-isolation-level conflict).

- Status gate (idempotency): a DECIDED claim is never re-prosecuted (the poll
  selects only status='PENDING').  Two concurrent prosecutors are serialised by
  the row lock the PENDING→PROSECUTING UPDATE takes; the loser's UPDATE matches 0
  rows and skips.

- MVCC safety: the ONLY UPDATE of non-MVCC-friendly columns is claim.status
  (PENDING → PROSECUTING → DECIDED).  These are real state transitions, not
  mutations of unchanged data.  inquisition_skeptic and inquisition_verdict are
  INSERT-only within prosecute_claim.  gestion_items go through open_or_refresh
  (UPSERT, dedupe_key UNIQUE).

- Lens B (raw recount) and Lens C (live re-fetch) ABSTAIN in the current €0
  state.  The prosecutor does not special-case them; the quorum engine handles
  ABSTAIN correctly (counts toward the refute mass, Law I).

- emit_claim_from_verdict is documented but NOT auto-run over all VAM rows.
  That is a harvest-phase decision (SU-A4 delta integration).  Call it
  explicitly in migration/harvest scripts when ready.

- The subject_type 'count' maps to regime DRIFT (models.py regime_for).
  The count claim seeded in tests uses this subject_type.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from typing import Any

import asyncpg

from pipeline.inquisition.lenses import ClaimEnvelope, run_applicable_lenses
from pipeline.inquisition.models import StateTuple, indep_distance, regime_for
from pipeline.inquisition.quorum import decide
from pipeline.inquisition.router import route_verdict

logger = logging.getLogger(__name__)

# Default DSN from environment (allows direct CLI invocation)
_DEFAULT_DSN = os.environ.get(
    "CARDEEP_DSN",
    "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep",
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _state_tuple_from_jsonb(raw: Any) -> StateTuple:
    """Deserialise producer_state JSONB → StateTuple.

    asyncpg returns JSONB columns as dict (or str if the driver doesn't
    auto-parse).  Accepts both forms.
    """
    if isinstance(raw, str):
        data: dict = json.loads(raw)
    else:
        data = dict(raw)  # asyncpg Record / dict

    return StateTuple(
        source=data.get("source", "unknown"),
        tool=data.get("tool", "unknown"),
        cache=data.get("snapshot_id", data.get("cache", "snap_T0")),
        path=data.get("code_path", data.get("path", "unknown")),
    )


def _canonical_str(value: Any) -> str | None:
    """Normalise a value to a canonical string for measured_value fields."""
    if value is None:
        return None
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


# ---------------------------------------------------------------------------
# Core: prosecute_claim
# ---------------------------------------------------------------------------

async def prosecute_claim(
    conn: asyncpg.Connection,
    claim_row: asyncpg.Record,
) -> dict[str, Any]:
    """Prosecute a single inquisition_claim ATOMICALLY and persist the audit trail.

    The entire prosecution runs inside one ``conn.transaction()``: on any failure
    the claim reverts to PENDING (re-eligible next poll) — no PROSECUTING zombie,
    no orphan skeptic rows.  Plain transaction() nests as a SAVEPOINT under a test
    that already opened one, so the same code path is correct in production and tests.

    Returns
    -------
    Summary dict with keys:
        claim_id, verdict, reason_code, routed_action,
        skeptic_count, assert_n, refute_soft_n, refute_hard_n, abstain_n,
        gestion_item_id, skipped, duration_ms.
    """
    async with conn.transaction():
        return await _prosecute_claim_body(conn, claim_row)


async def _prosecute_claim_body(
    conn: asyncpg.Connection,
    claim_row: asyncpg.Record,
) -> dict[str, Any]:
    """Prosecution body — MUST run inside prosecute_claim's transaction.

    Parameters
    ----------
    conn:       asyncpg connection (already inside a transaction).
    claim_row:  Row from inquisition_claim (fetched by prosecute_pending or test).
    """
    claim_id: str = claim_row["claim_id"]
    subject_type: str = claim_row["subject_type"]
    subject_key: str = claim_row["subject_key"]
    asserted_value: str | None = claim_row["asserted_value"]
    tolerance: float = claim_row["tolerance"]
    evidence_uri: str | None = claim_row["evidence_uri"]

    t0 = time.monotonic()

    # ------------------------------------------------------------------
    # Step 1: PENDING → PROSECUTING (single status UPDATE — real transition)
    # ------------------------------------------------------------------
    updated = await conn.fetchval(
        """UPDATE inquisition_claim
              SET status = 'PROSECUTING'
            WHERE claim_id = $1
              AND status = 'PENDING'
        RETURNING claim_id""",
        claim_id,
    )
    if updated is None:
        # Already PROSECUTING or DECIDED — skip safely (idempotency gate)
        return {
            "claim_id":        claim_id,
            "verdict":         None,
            "reason_code":     None,
            "routed_action":   None,
            "skeptic_count":   0,
            "assert_n":        0,
            "refute_soft_n":   0,
            "refute_hard_n":   0,
            "abstain_n":       0,
            "gestion_item_id": None,
            "skipped":         True,
            "duration_ms":     int((time.monotonic() - t0) * 1000),
        }

    # ------------------------------------------------------------------
    # Step 2: Build ClaimEnvelope
    # ------------------------------------------------------------------
    producer_state = _state_tuple_from_jsonb(claim_row["producer_state"])
    envelope = ClaimEnvelope(
        claim_id=claim_id,
        subject_type=subject_type,
        subject_key=subject_key,
        asserted_value=asserted_value or "",
        producer_state=producer_state,
        tolerance=tolerance,
        evidence_uri=evidence_uri,
    )

    # ------------------------------------------------------------------
    # Step 3: Run all applicable lenses (§3.6 matrix)
    # ------------------------------------------------------------------
    skeptics = await run_applicable_lenses(conn, envelope)

    # ------------------------------------------------------------------
    # Step 4: Persist each skeptic → inquisition_skeptic (INSERT-only)
    # ------------------------------------------------------------------
    for skeptic in skeptics:
        dist = indep_distance(skeptic.state, producer_state)
        skeptic_state_json = json.dumps({
            "source": skeptic.state.source,
            "tool":   skeptic.state.tool,
            "cache":  skeptic.state.cache,
            "path":   skeptic.state.path,
        })
        await conn.execute(
            """
            INSERT INTO inquisition_skeptic
                (claim_id, lens, skeptic_state, indep_distance,
                 measured_value, verdict, confidence, reason, evidence)
            VALUES ($1, $2, $3::jsonb, $4, $5, $6, $7, $8, $9::jsonb)
            """,
            claim_id,
            skeptic.lens,
            skeptic_state_json,
            dist,
            _canonical_str(skeptic.measured_value),
            skeptic.verdict,
            skeptic.confidence,
            skeptic.reason,
            json.dumps({"deterministic": skeptic.deterministic}) if skeptic.deterministic else None,
        )

    # ------------------------------------------------------------------
    # Step 5: Quorum decision (§5.4)
    # ------------------------------------------------------------------
    try:
        regime = regime_for(subject_type)
    except ValueError:
        # Unmapped subject_type: default to EXACT (safest — over-refutes)
        from pipeline.inquisition.models import Regime
        regime = Regime.EXACT
        logger.warning(
            "prosecutor: unknown subject_type %r for claim %s; "
            "defaulting to EXACT regime", subject_type, claim_id,
        )

    result = decide(
        skeptics=skeptics,
        producer=producer_state,
        asserted_value=asserted_value or "",
        regime=regime,
    )

    # ------------------------------------------------------------------
    # Step 6a: Route verdict → gestionador (§7)
    # ------------------------------------------------------------------
    routed_action, gestion_item_id = await route_verdict(
        conn,
        claim_id=claim_id,
        subject_type=subject_type,
        subject_key=subject_key,
        quorum_result=result,
        actor="inquisition_prosecutor",
    )

    # ------------------------------------------------------------------
    # Step 6b: Persist inquisition_verdict (INSERT-only; routed_action in same row)
    # ------------------------------------------------------------------
    await conn.execute(
        """
        INSERT INTO inquisition_verdict
            (claim_id, verdict, decided_value, indep_score,
             assert_n, refute_soft_n, refute_hard_n, abstain_n,
             reason_code, routed_action, decided_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, now())
        """,
        claim_id,
        result.verdict,
        result.decided_value,
        result.indep_score,
        result.assert_n,
        result.refute_soft_n,
        result.refute_hard_n,
        result.abstain_n,
        result.reason_code,
        routed_action,
    )

    # ------------------------------------------------------------------
    # Step 7: PROSECUTING → DECIDED
    # ------------------------------------------------------------------
    await conn.execute(
        """UPDATE inquisition_claim
              SET status = 'DECIDED'
            WHERE claim_id = $1""",
        claim_id,
    )

    duration_ms = int((time.monotonic() - t0) * 1000)

    summary: dict[str, Any] = {
        "claim_id":        claim_id,
        "verdict":         result.verdict,
        "reason_code":     result.reason_code,
        "routed_action":   routed_action,
        "skeptic_count":   len(skeptics),
        "assert_n":        result.assert_n,
        "refute_soft_n":   result.refute_soft_n,
        "refute_hard_n":   result.refute_hard_n,
        "abstain_n":       result.abstain_n,
        "gestion_item_id": gestion_item_id,
        "skipped":         False,
        "duration_ms":     duration_ms,
    }

    logger.info(
        "prosecutor: DECIDED claim=%s subject=%s:%s → %s:%s action=%s item=%s [%dms]",
        claim_id, subject_type, subject_key,
        result.verdict, result.reason_code, routed_action, gestion_item_id, duration_ms,
    )

    return summary


# ---------------------------------------------------------------------------
# Batch poller: prosecute_pending
# ---------------------------------------------------------------------------

async def prosecute_pending(
    conn: asyncpg.Connection,
    *,
    limit: int = 100,
    actor: str = "inquisition_prosecutor",
) -> dict[str, Any]:
    """Poll PENDING inquisition_claim rows and prosecute them.

    Uses idx_claim_pending (WHERE status='PENDING' ORDER BY created_at).
    Claims already DECIDED are not re-polled (status gate).

    Parameters
    ----------
    conn:  asyncpg connection.
    limit: maximum claims to process in one batch (default 100).
    actor: actor string propagated to gestion_transition rows.

    Returns
    -------
    Aggregate summary dict:
        total, decided, skipped, errors, verdicts (Counter), duration_ms.
    """
    t0 = time.monotonic()

    rows = await conn.fetch(
        """SELECT claim_id, subject_type, subject_key, asserted_value,
                  producer_state, load_bearing, tolerance, evidence_uri
             FROM inquisition_claim
            WHERE status = 'PENDING'
            ORDER BY created_at
            LIMIT $1""",
        limit,
    )

    total = len(rows)
    decided = 0
    skipped = 0
    errors = 0
    verdicts: dict[str, int] = {}

    for row in rows:
        try:
            summary = await prosecute_claim(conn, row)
            if summary.get("skipped"):
                skipped += 1
            else:
                decided += 1
                v = summary.get("verdict") or "UNKNOWN"
                verdicts[v] = verdicts.get(v, 0) + 1
        except Exception:
            errors += 1
            logger.exception(
                "prosecutor: error prosecuting claim=%s", row["claim_id"]
            )

    duration_ms = int((time.monotonic() - t0) * 1000)

    return {
        "total":       total,
        "decided":     decided,
        "skipped":     skipped,
        "errors":      errors,
        "verdicts":    verdicts,
        "duration_ms": duration_ms,
    }


# ---------------------------------------------------------------------------
# Optional harvest helper: emit_claim_from_verdict
# ---------------------------------------------------------------------------

async def emit_claim_from_verdict(
    conn: asyncpg.Connection,
    verification_verdict_row: asyncpg.Record,
) -> str:
    """Convert a VAM verification_verdict row into an inquisition_claim (PENDING).

    This is the §9 harvest bridge: takes any VAM-produced TRUSTWORTHY verdict and
    submits it to the Inquisition for adversarial re-prosecution.

    Parameters
    ----------
    conn:                     asyncpg connection.
    verification_verdict_row: Row from verification_verdict (VAM table).

    Returns
    -------
    claim_id: ULID of the newly inserted inquisition_claim.

    IMPORTANT — DO NOT auto-run over all VAM rows.
    This function must be called explicitly from a harvest/migration script after
    the VAM harvest phase closes (SU-A4 delta integration).  Auto-running it over
    the full verification_verdict table would flood the inquisition queue.

    Subject-type mapping (VAM subject_type → inquisition subject_type):
        entity_inventory → count
        coverage         → coverage
        <anything else>  → count (safe default; over-refutes, never over-trusts)
    """
    import ulid

    vam_subject_type: str = verification_verdict_row.get("subject_type", "unknown")
    vam_subject_key: str = verification_verdict_row.get("subject_key", "unknown")
    primary_value: str | None = verification_verdict_row.get("primary_value")
    primary_path: str | None = verification_verdict_row.get("primary_path") or "vam"

    # Map VAM subject_type to inquisition subject_type
    _vam_to_inq_subject: dict[str, str] = {
        "entity_inventory": "count",
        "coverage":         "coverage",
        "freshness":        "count",
        "field_fill":       "entity_field",
        "existence":        "entity_field",
        "denominator":      "denominator",
    }
    inq_subject_type = _vam_to_inq_subject.get(vam_subject_type, "count")

    producer_state = json.dumps({
        "source":      primary_path,
        "tool":        "vam_count_quorum",
        "snapshot_id": "vam_snap",
        "code_path":   "pipeline/verify.py",
    })

    claim_id = str(ulid.ULID())
    claim_text = (
        f"VAM harvest: {vam_subject_type}:{vam_subject_key} "
        f"primary_value={primary_value!r} from path={primary_path!r}"
    )

    await conn.execute(
        """
        INSERT INTO inquisition_claim
            (claim_id, subject_type, subject_key, claim,
             asserted_value, producer_state, load_bearing,
             tolerance, evidence_uri, status)
        VALUES ($1, $2, $3, $4, $5, $6::jsonb, TRUE, 0.005, NULL, 'PENDING')
        """,
        claim_id,
        inq_subject_type,
        vam_subject_key,
        claim_text,
        primary_value,
        producer_state,
    )

    logger.info(
        "emit_claim_from_verdict: created claim=%s for vam_subject=%s:%s",
        claim_id, vam_subject_type, vam_subject_key,
    )

    return claim_id


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

async def main() -> None:
    """CLI: connect to CARDEEP_DSN, run prosecute_pending, print JSON summary."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    dsn = os.environ.get("CARDEEP_DSN", _DEFAULT_DSN)
    conn = await asyncpg.connect(dsn)
    try:
        summary = await prosecute_pending(conn, limit=100)
    finally:
        await conn.close()

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
