"""Country-autopilot campaign state machine — the spine the orchestrator drives every country
through (Phase E, plans/country-autopilot/01-ARCHITECTURE.md §E).

The lifecycle is the COVER(CC) progression of docs/generic-engine-bible/COVER-NEW-COUNTRY.md:

    REGISTERED -> KNOW_COUNTRY -> BOOTSTRAPPED -> IN_COVERAGE -> SEALED   (SEALED terminal)

One country == one ``country_campaign`` row (PK ``country_code``, migration 0067). This module is
the *code mirror* of that table's discipline and a faithful sibling of ``pipeline/gestionador/
route.py``:

  * the legal EDGES live in :data:`VALID_TRANSITIONS`;
  * :func:`assert_valid_transition` REJECTS every illegal move (skip, regression, leaving the
    terminal SEALED, unknown state) by raising :class:`CampaignTransitionError` — exactly as
    route.py's ``assert_valid_transition`` raises ``ValueError``;
  * every state change is APPENDED to ``country_campaign_transition`` (append-only — the history
    IS the proof, like ``gestion_transition``); rows are never UPDATEd or DELETEd.

DB contract (MVCC-safe, mirrors route.py):
  * :func:`register`   — INSERT ... ON CONFLICT (country_code) DO NOTHING; idempotent birth in
    REGISTERED, appends the initial ``None -> REGISTERED`` transition only on first creation.
  * :func:`transition` — a single UPDATE of ``state`` + ``updated_at``, guarded by the fetched
    current state; appends the audit row.
  * The two are pure-async over an ``asyncpg`` connection so a caller controls the transaction
    boundary (the tests run them inside an aborted transaction, leaving zero residue).

ES byte-identical: ``country_campaign`` / ``country_campaign_transition`` are NEW, EMPTY tables;
no ES census row is read or written, so single-tenant ES behaviour is 100% preserved. ES is the
hand-built incumbent and is NOT auto-registered here.
"""
from __future__ import annotations

import json
from typing import Any

import asyncpg

# ---------------------------------------------------------------------------
# The states (string constants — the same values stored in the DB CHECK)
# ---------------------------------------------------------------------------
REGISTERED = "REGISTERED"
KNOW_COUNTRY = "KNOW_COUNTRY"
BOOTSTRAPPED = "BOOTSTRAPPED"
IN_COVERAGE = "IN_COVERAGE"
SEALED = "SEALED"

#: The state a freshly-registered campaign is born in.
INITIAL_STATE = REGISTERED

# ---------------------------------------------------------------------------
# The machine — strictly linear forward progression; SEALED is terminal.
# (Faithful to the bible: the lifecycle ADVANCES through the gates, it does not regress. Illegal
# edges are rejected here AND bounded by the state CHECK in migration 0067.)
# ---------------------------------------------------------------------------
VALID_TRANSITIONS: dict[str, set[str]] = {
    REGISTERED:   {KNOW_COUNTRY},
    KNOW_COUNTRY: {BOOTSTRAPPED},
    BOOTSTRAPPED: {IN_COVERAGE},
    IN_COVERAGE:  {SEALED},
    SEALED:       set(),   # terminal — no exit
}

ALL_STATES = frozenset(VALID_TRANSITIONS.keys())


class CampaignTransitionError(ValueError):
    """Raised on an illegal campaign state transition.

    Subclasses :class:`ValueError` so an existing ``except ValueError`` handler (the gestion
    convention) still catches an illegal campaign move.
    """


def assert_valid_transition(from_state: str | None, to_state: str) -> None:
    """Raise :class:`CampaignTransitionError` if ``from_state -> to_state`` is not a legal edge.

    ``from_state`` is ``None`` ONLY for the initial registration, which MUST target REGISTERED
    (mirrors route.py's ``None -> OPEN`` birth rule).
    """
    if to_state not in ALL_STATES:
        raise CampaignTransitionError(f"Unknown target state: {to_state!r}")
    if from_state is None:
        if to_state != INITIAL_STATE:
            raise CampaignTransitionError(
                f"Initial transition must target {INITIAL_STATE!r}, got {to_state!r}"
            )
        return
    if from_state not in VALID_TRANSITIONS:
        raise CampaignTransitionError(f"Unknown source state: {from_state!r}")
    allowed = VALID_TRANSITIONS[from_state]
    if to_state not in allowed:
        raise CampaignTransitionError(
            f"Illegal transition {from_state!r} -> {to_state!r}. "
            f"Allowed from {from_state!r}: {sorted(allowed)}"
        )


def next_state(from_state: str) -> str | None:
    """Return the single legal forward state after ``from_state``, or ``None`` if terminal.

    Convenience for the orchestrator's COVER(CC) advance step: the lifecycle is linear, so each
    non-terminal state has exactly one successor.
    """
    if from_state not in VALID_TRANSITIONS:
        raise CampaignTransitionError(f"Unknown source state: {from_state!r}")
    nxt = VALID_TRANSITIONS[from_state]
    return next(iter(nxt)) if nxt else None


# ---------------------------------------------------------------------------
# Country-code normalization (CHAR(2) in the schema)
# ---------------------------------------------------------------------------

def _normalize_cc(country_code: str) -> str:
    cc = (country_code or "").strip().upper()
    if len(cc) != 2:
        raise ValueError(f"country_code must be 2 chars (ISO), got {country_code!r}")
    return cc


# ---------------------------------------------------------------------------
# DB operations (asyncpg — caller owns the transaction boundary)
# ---------------------------------------------------------------------------

async def register(
    conn: asyncpg.Connection,
    country_code: str,
    *,
    actor: str = "autopilot",
    detail: dict[str, Any] | None = None,
) -> str:
    """Birth a campaign in REGISTERED (idempotent). Return the campaign's current state.

    The initial ``None -> REGISTERED`` transition is appended ONLY when the row is newly created
    (ON CONFLICT DO NOTHING), so re-registering an existing campaign neither errors nor double-
    writes the audit trail.
    """
    cc = _normalize_cc(country_code)
    row = await conn.fetchrow(
        """
        INSERT INTO country_campaign (country_code, state, detail)
        VALUES ($1, $2, $3::jsonb)
        ON CONFLICT (country_code) DO NOTHING
        RETURNING state
        """,
        cc, INITIAL_STATE, json.dumps(detail or {}),
    )
    if row is not None:
        await _append_transition(
            conn, cc, from_state=None, to_state=INITIAL_STATE, actor=actor,
            note="campaign registered", detail=detail,
        )
        return INITIAL_STATE
    # Already existed: return its current state, append nothing (idempotent).
    return await conn.fetchval(
        "SELECT state FROM country_campaign WHERE country_code = $1", cc
    )


async def transition(
    conn: asyncpg.Connection,
    country_code: str,
    to_state: str,
    *,
    actor: str,
    note: str | None = None,
    detail: dict[str, Any] | None = None,
) -> None:
    """Advance a campaign to ``to_state``: validate the edge, UPDATE the row, append the audit.

    Raises :class:`CampaignTransitionError` on an illegal edge OR an unknown campaign (no silent
    creation — a campaign must be :func:`register`-ed first).
    """
    cc = _normalize_cc(country_code)
    row = await conn.fetchrow(
        "SELECT state FROM country_campaign WHERE country_code = $1", cc
    )
    if row is None:
        raise CampaignTransitionError(
            f"country_campaign {cc!r} not found — register() it first"
        )
    from_state = row["state"]
    assert_valid_transition(from_state, to_state)

    # Single UPDATE: advance state, stamp updated_at, shallow-merge optional detail. The explicit
    # ::jsonb cast pins the parameter OID so a NULL detail binds cleanly (no AmbiguousParameter).
    await conn.execute(
        """
        UPDATE country_campaign
        SET state = $2,
            updated_at = now(),
            detail = CASE WHEN $3::jsonb IS NULL THEN detail ELSE detail || $3::jsonb END
        WHERE country_code = $1
        """,
        cc, to_state, json.dumps(detail) if detail else None,
    )
    await _append_transition(
        conn, cc, from_state=from_state, to_state=to_state, actor=actor,
        note=note, detail=detail,
    )


async def current_state(conn: asyncpg.Connection, country_code: str) -> str | None:
    """Return the campaign's current state, or ``None`` if it is not registered."""
    return await conn.fetchval(
        "SELECT state FROM country_campaign WHERE country_code = $1",
        _normalize_cc(country_code),
    )


async def mark_pending_gates(
    conn: asyncpg.Connection,
    country_code: str,
    gates: "list[tuple[str, str | None]]",
) -> None:
    """Persist the campaign's PENDIENTE-OWNER gate marks as CONSULTABLE state (autonomy-e2e 1.2).

    The orchestrator's gates (GASTO/PROD/LEGAL) PARK without stopping the loop; until now the marks
    rode only in the in-memory ``CampaignResult`` + the transition audit (an event, not state). This
    stamps them on ``country_campaign.detail['pending_owner_gates']`` so a resume/supervisor can ASK
    the DB which countries are blocked on which gate. Idempotent shallow-merge; an empty list CLEARS
    the mark (the country is no longer waiting on the owner). Decoupled from ``gates.py`` by contract:
    it takes plain ``(gate_name, reason)`` tuples, not ``GateResult`` — no layer dependency.
    """
    cc = _normalize_cc(country_code)
    marks = [{"gate": g, "reason": r} for g, r in gates]
    await conn.execute(
        """
        UPDATE country_campaign
        SET detail = detail || jsonb_build_object('pending_owner_gates', $2::jsonb),
            updated_at = now()
        WHERE country_code = $1
        """,
        cc, json.dumps(marks),
    )


async def pending_owner_gates(conn: asyncpg.Connection) -> "dict[str, list[str]]":
    """Resume view: ``{country_code: [gate, ...]}`` for every campaign parked PENDIENTE-OWNER.

    Reads the marks set by :func:`mark_pending_gates`; a campaign with an empty/absent list is not
    blocked and does not appear. The DB-backed answer to "what is waiting on the owner?" — the piece
    the loop needs to resume and the owner needs to see the honest frontier.
    """
    rows = await conn.fetch(
        """
        SELECT country_code, detail->'pending_owner_gates' AS gates
        FROM country_campaign
        WHERE detail ? 'pending_owner_gates'
          AND jsonb_array_length(detail->'pending_owner_gates') > 0
        """
    )
    out: dict[str, list[str]] = {}
    for r in rows:
        gates = r["gates"]
        if isinstance(gates, str):
            gates = json.loads(gates)
        out[r["country_code"]] = [g["gate"] for g in gates]
    return out


async def register_sealed_incumbent(
    conn: asyncpg.Connection,
    country_code: str,
    *,
    actor: str = "owner",
    detail: dict[str, Any] | None = None,
) -> str:
    """Backfill an ALREADY-COVERED incumbent country directly in SEALED (autonomy-e2e 1.3).

    ES is the hand-built census — it never walked the onboarding loop, so it cannot be ``register``-ed
    (REGISTERED) and then ``transition``-ed (the state machine would force the full forward path). This
    stamps the campaign row straight in SEALED with a declared ``None -> SEALED`` 'incumbent backfill'
    audit row, idempotent (``ON CONFLICT DO NOTHING`` — re-running neither errors nor double-writes the
    ledger). ES byte-identical: ``country_campaign`` is a NEW table; no census row is read or written.
    Returns the campaign's current state (SEALED on create; the existing state if already present).
    """
    cc = _normalize_cc(country_code)
    base_detail = {"incumbent": True, **(detail or {})}
    row = await conn.fetchrow(
        """
        INSERT INTO country_campaign (country_code, state, detail)
        VALUES ($1, $2, $3::jsonb)
        ON CONFLICT (country_code) DO NOTHING
        RETURNING state
        """,
        cc, SEALED, json.dumps(base_detail),
    )
    if row is not None:
        await _append_transition(
            conn, cc, from_state=None, to_state=SEALED, actor=actor,
            note="incumbent backfill (already-covered census; did not walk the onboarding loop)",
            detail=base_detail,
        )
        return SEALED
    return await conn.fetchval(
        "SELECT state FROM country_campaign WHERE country_code = $1", cc
    )


async def _append_transition(
    conn: asyncpg.Connection,
    country_code: str,
    *,
    from_state: str | None,
    to_state: str,
    actor: str,
    note: str | None = None,
    detail: dict[str, Any] | None = None,
) -> None:
    """Append-only insert into ``country_campaign_transition`` (never UPDATE/DELETE)."""
    await conn.execute(
        """
        INSERT INTO country_campaign_transition
            (country_code, from_state, to_state, actor, note, detail)
        VALUES ($1, $2, $3, $4, $5, $6::jsonb)
        """,
        country_code, from_state, to_state, actor, note,
        json.dumps(detail) if detail else None,
    )
