"""V4 Gestionador — State machine and routing (V4-GESTIONADOR.md §4).

Responsibilities:
  1. UPSERT anomalies into gestion_item (idempotent via dedupe_key UNIQUE).
  2. Record every state change in gestion_transition (append-only).
  3. Enforce valid transitions (raises ValueError on illegal moves).
  4. Gate RESOLVED: requires verdict_id FK (no independent recheck = no close).
  5. SLA stamping on open/route.

All DB writes are MVCC-safe:
  - gestion_item: INSERT ... ON CONFLICT (dedupe_key) DO UPDATE
    (update measured + severity only; state/opened_at preserved if already open)
  - gestion_transition: INSERT-only, never UPDATE or DELETE
"""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from typing import Any

import asyncpg

from .detect import AnomalyResult

# ---------------------------------------------------------------------------
# SLA per lane (V4 §4.4)
# ---------------------------------------------------------------------------
LANE_SLA: dict[str, timedelta | None] = {
    "AUTO_FIX":        timedelta(hours=6),
    "RESEARCH":        timedelta(days=7),
    "QUARANTINE":      timedelta(hours=48),
    "ESCALATE_GASTO":  None,   # awaits human/budget
    "ESCALATE_OWNER":  None,
}

# ---------------------------------------------------------------------------
# Valid state transitions (V4 §4.2)
# ---------------------------------------------------------------------------
#   OPEN → ROUTED, QUARANTINED, WONT_FIX
#   ROUTED → IN_PROGRESS, ESCALATED, QUARANTINED, WONT_FIX
#   IN_PROGRESS → REVERIFYING, QUARANTINED, WONT_FIX
#   REVERIFYING → RESOLVED, REOPENED
#   QUARANTINED → IN_PROGRESS, RESOLVED, WONT_FIX
#   ESCALATED → IN_PROGRESS, WONT_FIX
#   RESOLVED → REOPENED   (regression)
#   REOPENED → ROUTED, IN_PROGRESS, WONT_FIX
#   WONT_FIX → (terminal)
VALID_TRANSITIONS: dict[str, set[str]] = {
    "OPEN":         {"ROUTED", "QUARANTINED", "WONT_FIX"},
    "ROUTED":       {"IN_PROGRESS", "ESCALATED", "QUARANTINED", "WONT_FIX"},
    "IN_PROGRESS":  {"REVERIFYING", "QUARANTINED", "WONT_FIX"},
    "REVERIFYING":  {"RESOLVED", "REOPENED"},
    "QUARANTINED":  {"IN_PROGRESS", "RESOLVED", "WONT_FIX"},
    "ESCALATED":    {"IN_PROGRESS", "WONT_FIX"},
    "RESOLVED":     {"REOPENED"},
    "REOPENED":     {"ROUTED", "IN_PROGRESS", "WONT_FIX"},
    "WONT_FIX":     set(),   # terminal state
}

ALL_STATES = frozenset(VALID_TRANSITIONS.keys())


def assert_valid_transition(from_state: str | None, to_state: str) -> None:
    """Raise ValueError if the transition is not in the state machine."""
    if to_state not in ALL_STATES:
        raise ValueError(f"Unknown target state: {to_state!r}")
    if from_state is None:
        if to_state != "OPEN":
            raise ValueError(
                f"Initial transition must target OPEN, got {to_state!r}"
            )
        return
    if from_state not in VALID_TRANSITIONS:
        raise ValueError(f"Unknown source state: {from_state!r}")
    allowed = VALID_TRANSITIONS[from_state]
    if to_state not in allowed:
        raise ValueError(
            f"Illegal transition {from_state!r} → {to_state!r}. "
            f"Allowed from {from_state!r}: {sorted(allowed)}"
        )


# ---------------------------------------------------------------------------
# Core UPSERT: open or refresh a managed item
# ---------------------------------------------------------------------------

async def open_or_refresh(
    conn: asyncpg.Connection,
    anomaly: AnomalyResult,
    *,
    actor: str = "detector",
) -> int:
    """INSERT a new gestion_item or UPDATE measured/severity if dedupe_key
    already exists with an open item.

    Returns the item id.

    MVCC contract:
      - INSERT: one round-trip, no churn.
      - ON CONFLICT: only updates measured + severity (never state/opened_at).
        If the existing item is already RESOLVED/WONT_FIX, we re-open it
        (regression case) by setting state=REOPENED and appending a transition.
    """
    sla_delta = LANE_SLA.get(anomaly.lane)

    # Compute sla_due as a concrete datetime (or None) so asyncpg can bind it as
    # TIMESTAMPTZ without type-inference ambiguity.  Previously the SQL computed
    # ``now() + $10::interval`` inside the query, which caused AmbiguousParameterError
    # when sla_delta is None (asyncpg cannot infer the OID of a NULL parameter that
    # only appears inside a CASE branch).  Computing client-side and passing the
    # result as a typed datetime removes the ambiguity.
    now_utc = datetime.now(tz=timezone.utc)
    sla_due: datetime | None = (now_utc + sla_delta) if sla_delta is not None else None

    upsert_sql = """
        INSERT INTO gestion_item
            (detector, subject_type, subject_key, severity, score,
             measured, baseline, lane, state, quarantines,
             opened_at, sla_due, dedupe_key)
        VALUES
            ($1, $2, $3, $4, $5,
             $6::jsonb, $7::jsonb, $8, 'OPEN', $9,
             now(), $10, $11)
        ON CONFLICT (dedupe_key) DO UPDATE
            SET
                measured   = EXCLUDED.measured,
                severity   = EXCLUDED.severity,
                score      = EXCLUDED.score,
                -- Reopen if previously closed
                state      = CASE
                    WHEN gestion_item.closed_at IS NOT NULL THEN 'REOPENED'
                    ELSE gestion_item.state
                END,
                closed_at     = CASE
                    WHEN gestion_item.closed_at IS NOT NULL THEN NULL
                    ELSE gestion_item.closed_at
                END,
                closed_reason = CASE
                    WHEN gestion_item.closed_at IS NOT NULL THEN NULL
                    ELSE gestion_item.closed_reason
                END
        RETURNING id, state, (xmax = 0) AS is_new
    """

    row = await conn.fetchrow(
        upsert_sql,
        anomaly.detector,
        anomaly.subject_type,
        anomaly.subject_key,
        anomaly.severity,
        anomaly.score,
        json.dumps(anomaly.measured),
        json.dumps(anomaly.baseline) if anomaly.baseline else None,
        anomaly.lane,
        anomaly.quarantines,
        sla_due,      # datetime | None — asyncpg encodes as TIMESTAMPTZ natively
        anomaly.dedupe_key,
    )

    item_id = row["id"]
    is_new = row["is_new"]
    current_state = row["state"]

    if is_new:
        # First detection: record the OPEN transition
        await _append_transition(
            conn, item_id,
            from_state=None,
            to_state="OPEN",
            actor=actor,
            note=f"Detector fired: {anomaly.detector} on {anomaly.subject_key}",
            payload=anomaly.measured,
        )
    else:
        # Re-detection: record a refresh / reopen transition
        note = (
            "Regression: item reopened by detector re-fire"
            if current_state == "REOPENED"
            else "Detector re-fired: measured evidence refreshed"
        )
        await _append_transition(
            conn, item_id,
            from_state=None if current_state == "OPEN" else current_state,
            to_state=current_state,
            actor=actor,
            note=note,
            payload=anomaly.measured,
        )

    return item_id


# ---------------------------------------------------------------------------
# State transition
# ---------------------------------------------------------------------------

async def transition(
    conn: asyncpg.Connection,
    item_id: int,
    to_state: str,
    *,
    actor: str,
    note: str | None = None,
    payload: dict[str, Any] | None = None,
    verdict_id: int | None = None,
) -> None:
    """Advance a gestion_item to a new state.

    Validates the transition against the state machine, writes the audit
    row to gestion_transition, and updates gestion_item accordingly.

    RESOLVED requires verdict_id (V4 §4.2: "No verdict_id → no RESOLVED").
    """
    # Fetch current state
    item = await conn.fetchrow(
        "SELECT state, closed_at FROM gestion_item WHERE id = $1",
        item_id,
    )
    if item is None:
        raise ValueError(f"gestion_item {item_id} not found")

    from_state = item["state"]
    assert_valid_transition(from_state, to_state)

    # Closure proof guard
    if to_state == "RESOLVED" and verdict_id is None:
        raise ValueError(
            f"RESOLVED requires verdict_id — no independent recheck recorded "
            f"for item {item_id}"
        )

    # Build the UPDATE
    update_parts = ["state = $2"]
    params: list[Any] = [item_id, to_state]
    param_idx = 3

    if to_state in ("RESOLVED", "WONT_FIX"):
        update_parts.append(f"closed_at = now()")
        update_parts.append(f"closed_reason = ${param_idx}")
        params.append(note or to_state)
        param_idx += 1

    if verdict_id is not None:
        update_parts.append(f"verdict_id = ${param_idx}")
        params.append(verdict_id)
        param_idx += 1

    # Re-open: clear closed fields
    if to_state == "REOPENED":
        update_parts.extend(["closed_at = NULL", "closed_reason = NULL"])

    await conn.execute(
        f"UPDATE gestion_item SET {', '.join(update_parts)} WHERE id = $1",
        *params,
    )

    await _append_transition(
        conn, item_id,
        from_state=from_state,
        to_state=to_state,
        actor=actor,
        note=note,
        payload=payload,
    )


# ---------------------------------------------------------------------------
# Bulk route: take a list of AnomalyResults, upsert all, auto-advance to ROUTED
# ---------------------------------------------------------------------------

async def route_anomalies(
    conn: asyncpg.Connection,
    anomalies: list[AnomalyResult],
    *,
    actor: str = "gestionador",
) -> list[int]:
    """Open (or refresh) each anomaly and advance new items to ROUTED.

    Returns list of item ids.
    """
    item_ids: list[int] = []
    for anomaly in anomalies:
        item_id = await open_or_refresh(conn, anomaly, actor=actor)
        # Fetch fresh state to decide if we should auto-route
        state_row = await conn.fetchrow(
            "SELECT state FROM gestion_item WHERE id = $1", item_id
        )
        current = state_row["state"] if state_row else "OPEN"
        if current == "OPEN":
            target = _routing_lane_to_first_state(anomaly.lane, anomaly.quarantines)
            await transition(
                conn, item_id, target,
                actor=actor,
                note=f"Auto-routed to {anomaly.lane} by routing function",
            )
        item_ids.append(item_id)
    return item_ids


def _routing_lane_to_first_state(lane: str, quarantines: bool) -> str:
    """Map lane to the first post-OPEN state (V4 §4.1 routing function)."""
    if quarantines:
        return "QUARANTINED"
    if lane in ("ESCALATE_GASTO", "ESCALATE_OWNER"):
        return "ESCALATED"
    return "ROUTED"


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

async def _append_transition(
    conn: asyncpg.Connection,
    item_id: int,
    *,
    from_state: str | None,
    to_state: str,
    actor: str,
    note: str | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    """Append-only insert into gestion_transition."""
    await conn.execute(
        """
        INSERT INTO gestion_transition
            (item_id, from_state, to_state, actor, note, payload)
        VALUES ($1, $2, $3, $4, $5, $6::jsonb)
        """,
        item_id,
        from_state,
        to_state,
        actor,
        note,
        json.dumps(payload) if payload else None,
    )
