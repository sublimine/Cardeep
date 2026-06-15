"""V3 Inquisition — Manager Router (V3-INQUISITION.md §7).

Deterministic routing: verdict + reason_code → gestionador lane → gestion_item.

Every Inquisition verdict that is not clean-TRUSTWORTHY is routed to exactly one
of four actions.  Routing is a pure table lookup — no agent discretion, fully
auditable.  Same lie always routes the same way.

Also writes an alert row for critical-severity routes (the existing ``alert``
table from migrations/0004).  The ``source_health`` table is NOT updated here:
the staleness detector (detect.py 3.4) owns source_health; the router only reads
the verdict facts it already knows.

Design decisions
----------------
- The mapping table is encoded as a tuple-keyed dict for O(1) lookup and so the
  full table can be tested exhaustively in a single loop (router_mapping_rows()).
- reason_code matching uses an ordered resolution: exact match → prefix match →
  catch-all per verdict class.
- AnomalyResult.score: 1.0 for hard/deterministic routes, 0.5 for soft/research
  routes.  This matches the severity semantics and keeps the gestion_item score
  field meaningful for prioritisation.
- dedupe_key format: 'inquisition:<subject_type>:<subject_key>' — intentionally
  subject-scoped (one open item per data object, not per reason code) so that
  successive re-prosecutions refresh rather than stack.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

import asyncpg

from pipeline.gestionador.detect import AnomalyResult
from pipeline.gestionador.route import open_or_refresh
from pipeline.inquisition.quorum import QuorumResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Routing table (§7 — sealed by Director on 2026-06-15)
#
# Each row: (verdict, reason_code_match, action, lane, quarantines, severity)
#   reason_code_match: exact string or sentinel '*' for catch-all within a verdict
#   action: the §7 string written to inquisition_verdict.routed_action
#   lane:   the gestionador lane (AnomalyResult.lane)
#   score:  1.0 for hard-evidence routes; 0.5 for soft/research
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _RouteRow:
    """One row of the sealed routing table."""
    verdict: str
    reason_match: str         # exact reason_code, or '*' for catch-all
    action: str               # 'fix'|'research'|'quarantine'|'escalate'|'none'
    lane: str                 # AUTO_FIX|RESEARCH|QUARANTINE|ESCALATE_OWNER|...
    quarantines: bool
    severity: str             # 'info'|'warning'|'critical'
    score: float


# fmt: off
_ROUTING_TABLE: list[_RouteRow] = [
    # -----------------------------------------------------------------------
    # TRUSTWORTHY — no action, no gestion_item
    # -----------------------------------------------------------------------
    _RouteRow("TRUSTWORTHY",  "*",                    "none",       "AUTO_FIX",      False, "info",     0.0),

    # -----------------------------------------------------------------------
    # REFUTED — hard-evidence routes (critical, score=1.0)
    # -----------------------------------------------------------------------
    _RouteRow("REFUTED",      "silent_cap",           "fix",        "AUTO_FIX",      False, "critical", 1.0),
    _RouteRow("REFUTED",      "fabrication",          "quarantine", "QUARANTINE",    True,  "critical", 1.0),
    _RouteRow("REFUTED",      "empty_delta",          "quarantine", "QUARANTINE",    True,  "critical", 1.0),
    _RouteRow("REFUTED",      "raw_vs_db_mismatch",   "fix",        "AUTO_FIX",      False, "critical", 1.0),

    # -----------------------------------------------------------------------
    # REFUTED — soft-evidence routes (warning, score=0.5)
    # -----------------------------------------------------------------------
    _RouteRow("REFUTED",      "stale",                "fix",        "AUTO_FIX",      False, "warning",  0.5),
    _RouteRow("REFUTED",      "kind_contradiction",   "fix",        "AUTO_FIX",      False, "warning",  0.5),
    _RouteRow("REFUTED",      "NO_INDEPENDENT_PATH",  "escalate",   "ESCALATE_OWNER",False, "warning",  0.5),
    _RouteRow("REFUTED",      "MAJORITY_REFUTE",      "research",   "RESEARCH",      False, "warning",  0.5),
    _RouteRow("REFUTED",      "SPLIT_QUORUM",         "research",   "RESEARCH",      False, "warning",  0.5),
    # Catch-all for any other REFUTED reason
    _RouteRow("REFUTED",      "*",                    "research",   "RESEARCH",      False, "warning",  0.5),

    # -----------------------------------------------------------------------
    # INCONCLUSIVE — escalate to owner for manual triage
    # -----------------------------------------------------------------------
    _RouteRow("INCONCLUSIVE", "*",                    "escalate",   "ESCALATE_OWNER",False, "info",     0.5),

    # -----------------------------------------------------------------------
    # QUARANTINED — quarantine lane regardless of reason
    # -----------------------------------------------------------------------
    _RouteRow("QUARANTINED",  "*",                    "quarantine", "QUARANTINE",    True,  "critical", 1.0),
]
# fmt: on


def _lookup_route(verdict: str, reason_code: str | None) -> _RouteRow:
    """Find the routing row for a (verdict, reason_code) pair.

    Resolution order:
      1. Exact match on (verdict, reason_code).
      2. Catch-all '*' for the same verdict.
      3. Fallback: RESEARCH on the same verdict (should never be reached).
    """
    rc = reason_code or ""

    # 1. Exact match
    for row in _ROUTING_TABLE:
        if row.verdict == verdict and row.reason_match == rc:
            return row

    # 2. Catch-all for this verdict
    for row in _ROUTING_TABLE:
        if row.verdict == verdict and row.reason_match == "*":
            return row

    # 3. Hard fallback (defensive — the table is exhaustive)
    logger.warning(
        "router._lookup_route: no match for verdict=%r reason=%r; defaulting to RESEARCH",
        verdict, reason_code,
    )
    return _RouteRow(verdict, "*", "research", "RESEARCH", False, "warning", 0.5)


def router_mapping_rows() -> list[_RouteRow]:
    """Return the sealed routing table for exhaustive test coverage."""
    return list(_ROUTING_TABLE)


# ---------------------------------------------------------------------------
# Public routing function
# ---------------------------------------------------------------------------

async def route_verdict(
    conn: asyncpg.Connection,
    *,
    claim_id: str,
    subject_type: str,
    subject_key: str,
    quorum_result: QuorumResult,
    actor: str = "inquisition_prosecutor",
) -> tuple[str, int | None]:
    """Route a quorum result through the §7 Manager Router.

    Steps:
      1. Look up the deterministic route row.
      2. For non-'none' actions: open a gestion_item via open_or_refresh.
      3. For critical routes: write an alert row (existing ``alert`` table).
      4. Return (routed_action, item_id | None).

    Parameters
    ----------
    conn:           asyncpg connection (caller's transaction).
    claim_id:       ULID of the inquisition_claim being prosecuted.
    subject_type:   inquisition_claim.subject_type.
    subject_key:    inquisition_claim.subject_key.
    quorum_result:  result of decide() — carries verdict, reason_code, counts.
    actor:          actor string written to gestion_transition.

    Returns
    -------
    (routed_action: str, item_id: int | None)
        item_id is None when routed_action == 'none' (TRUSTWORTHY; no gestion_item).
    """
    route = _lookup_route(quorum_result.verdict, quorum_result.reason_code)
    action = route.action

    if action == "none":
        # TRUSTWORTHY — nothing to open, no alert
        return ("none", None)

    # Build the AnomalyResult for the gestionador
    detector = f"inquisition:{quorum_result.reason_code or quorum_result.verdict}"
    dedupe_key = f"inquisition:{subject_type}:{subject_key}"

    measured: dict[str, Any] = {
        "verdict":         quorum_result.verdict,
        "reason_code":     quorum_result.reason_code,
        "assert_n":        quorum_result.assert_n,
        "refute_soft_n":   quorum_result.refute_soft_n,
        "refute_hard_n":   quorum_result.refute_hard_n,
        "abstain_n":       quorum_result.abstain_n,
        "indep_score":     quorum_result.indep_score,
        "decided_value":   quorum_result.decided_value,
        "claim_id":        claim_id,
    }
    baseline: dict[str, Any] = {
        "action":          action,
        "lane":            route.lane,
        "quarantines":     route.quarantines,
        "severity":        route.severity,
    }

    anomaly = AnomalyResult(
        detector=detector,
        subject_type=subject_type,
        subject_key=subject_key,
        severity=route.severity,
        score=route.score,
        measured=measured,
        baseline=baseline,
        lane=route.lane,
        quarantines=route.quarantines,
        dedupe_key=dedupe_key,
    )

    item_id = await open_or_refresh(conn, anomaly, actor=actor)

    # Write alert for critical-severity routes (reuse existing alert table)
    if route.severity == "critical":
        await _write_alert(conn, origin=subject_key, severity=route.severity,
                           message=_alert_message(quorum_result, subject_type, subject_key),
                           payload=measured)

    logger.info(
        "router: claim=%s subject=%s:%s verdict=%s reason=%s → action=%s lane=%s item=%s",
        claim_id, subject_type, subject_key,
        quorum_result.verdict, quorum_result.reason_code,
        action, route.lane, item_id,
    )

    return (action, item_id)


# ---------------------------------------------------------------------------
# Alert writer (reuses existing alert table from migrations/0004)
# ---------------------------------------------------------------------------

async def _write_alert(
    conn: asyncpg.Connection,
    *,
    origin: str,
    severity: str,
    message: str,
    payload: dict[str, Any],
) -> None:
    """Insert a row into the existing alert table.

    alert columns (verified 2026-06-15):
      origin TEXT NOT NULL, severity TEXT NOT NULL, message TEXT NOT NULL,
      payload JSONB, created_at TIMESTAMPTZ NOT NULL DEFAULT now(), resolved_at TIMESTAMPTZ
    """
    await conn.execute(
        """
        INSERT INTO alert (origin, severity, message, payload)
        VALUES ($1, $2, $3, $4::jsonb)
        """,
        origin,
        severity,
        message,
        json.dumps(payload),
    )


def _alert_message(
    result: QuorumResult,
    subject_type: str,
    subject_key: str,
) -> str:
    """Build a compact human-readable alert message."""
    return (
        f"Inquisition critical: {result.verdict}:{result.reason_code} "
        f"on {subject_type}:{subject_key} "
        f"(assert={result.assert_n} soft={result.refute_soft_n} "
        f"hard={result.refute_hard_n} abstain={result.abstain_n})"
    )
