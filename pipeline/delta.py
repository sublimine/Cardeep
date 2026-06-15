"""Shared delta machinery for the CARDEEP pipeline.

Two public building blocks:

1.  reconcile_gone(conn, source_key, run_started_at, *, min_captured)
    ----------------------------------------------------------------
    Marks available vehicles from a given source as 'gone' when they were
    not seen in the latest harvest run (last_seen < run_started_at).

    Design contract
    ~~~~~~~~~~~~~~~
    - Source-scoped: only touches vehicles that have an entity_source row for
      source_key.  No cross-source contamination.
    - Idempotent: a second call with the same run_started_at is a no-op
      (the vehicles already have status='gone' so the WHERE status='available'
      filter skips them).
    - Safety guard (min_captured): if the harvest captured fewer than
      min_captured vehicles, the sweep is aborted and (0, reason) is returned.
      This prevents a failed or aborted run from retiring the entire inventory.
      Callers MUST pass the real count of vehicles ingested in the run.
    - MVCC-safe: emits INSERT new vehicle_event + UPDATE vehicle.  No UPDATE of
      non-mutated rows (unchanged vehicles are not touched; only status-changing
      rows are written).

2.  diff_vehicle(old, new) -> list[dict]
    -----------------------------------
    Pure function.  Compares an existing vehicle snapshot (dict-like, keys:
    price, km, photo_url) against a freshly scraped one and returns a list of
    delta event dicts ready to be persisted.  Each dict has keys:
        event_type, old_value, new_value
    where old_value / new_value are Python objects (not JSON strings) — the
    caller is responsible for serialising them before INSERT.

    Supported change types: PRICE_CHANGE, KM_CHANGE, PHOTO_CHANGE.
    Returns [] when nothing changed (no false positives).

Cabling plan (A4-phase-2)
~~~~~~~~~~~~~~~~~~~~~~~~~
diff_vehicle is ready to be imported by the 43 wholesale connectors that
currently emit only NEW.  The wiring pattern per connector is:

    from pipeline.delta import diff_vehicle
    ...
    for v in scraped_vehicles:
        existing_row = existing.get(v.deep_link)
        if existing_row is None:
            # ... existing NEW path ...
        else:
            events = diff_vehicle(existing_row, v)
            for ev in events:
                await _emit_event(conn, vulid, eulid, ev)
            await conn.execute("UPDATE vehicle SET last_seen=now() ...")

This sweep (43 connectors) is deferred to A4-phase-2 because it requires a
coordinated commit across the entire fleet and a test run per connector family
to confirm no regressions.  The helper is designed, tested, and ready.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

import asyncpg

from pipeline.ids import ulid

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# reconcile_gone
# ---------------------------------------------------------------------------

_FIND_STALE = """
SELECT v.vehicle_ulid, v.price
  FROM vehicle v
  JOIN entity_source es ON es.entity_ulid = v.entity_ulid
 WHERE es.source_key = $1
   AND v.status      = 'available'
   AND v.last_seen   < $2
"""

_MARK_GONE = """
UPDATE vehicle
   SET status    = 'gone',
       last_seen = now()
 WHERE vehicle_ulid = $1
"""

_INSERT_GONE_EVENT = """
INSERT INTO vehicle_event
       (event_ulid, vehicle_ulid, entity_ulid, event_type, old_value, new_value)
VALUES ($1, $2, $3, 'GONE', $4::jsonb, NULL)
"""

_GET_ENTITY_ULID = """
SELECT entity_ulid FROM vehicle WHERE vehicle_ulid = $1
"""

# Below this inventory size the gone-fraction guard is NOT enforced — a handful
# of vehicles can legitimately all disappear between two runs. The guard exists
# to stop a partial/failed harvest from wiping a non-trivial inventory.
MIN_INVENTORY_FOR_GUARD = 20


async def reconcile_gone(
    conn: asyncpg.Connection,
    source_key: str,
    run_started_at: datetime,
    *,
    max_gone_fraction: float = 0.5,
) -> tuple[int, str]:
    """Mark stale vehicles from source_key as gone (not re-seen in the latest run).

    A vehicle is "stale" when status='available' and last_seen < run_started_at
    (the harvest did not refresh it).  Source-scoped (entity_source), idempotent
    (already-gone rows are skipped by the status filter), MVCC-safe (only the
    status-changing rows are written).

    SAFETY GUARD — gone-fraction cap (self-contained, does NOT trust the caller)
    --------------------------------------------------------------------------
    A partial or failed harvest leaves most of the inventory "not re-seen", which
    would falsely retire it. Real churn between two runs of a used-car source is a
    small fraction; retiring more than ``max_gone_fraction`` of a non-trivial
    inventory (>= MIN_INVENTORY_FOR_GUARD) in one sweep is almost certainly a
    broken run, so the sweep ABORTS without touching anything. (The previous
    ``min_captured`` guard was unsafe: it never compared captured-vs-expected, so
    a partial run — e.g. wallapop capturing 5k of 588k — would have retired the
    other ~99%.)

    Args:
        conn:            Active asyncpg connection.
        source_key:      Source identifier (e.g. 'wallapop_wholesale').
        run_started_at:  Harvest start; vehicles with last_seen < this are stale.
        max_gone_fraction: Abort if stale/available exceeds this (default 0.50),
                         for inventories of at least MIN_INVENTORY_FOR_GUARD.

    Returns:
        (gone_count, reason) — gone_count is 0 when skipped/aborted; reason is
        always a non-empty explanation.
    """
    # How many vehicles this source currently owns as available (the denominator).
    available_count: int = await conn.fetchval(
        """SELECT COUNT(*)
             FROM vehicle v
             JOIN entity_source es ON es.entity_ulid = v.entity_ulid
            WHERE es.source_key = $1
              AND v.status      = 'available'""",
        source_key,
    ) or 0
    if available_count == 0:
        return 0, (
            f"reconcile_gone: source_key={source_key!r} — no available vehicles; "
            f"nothing to do."
        )

    # Candidates: available vehicles from this source not re-seen in the run.
    rows = await conn.fetch(_FIND_STALE, source_key, run_started_at)
    stale_count = len(rows)
    if stale_count == 0:
        return 0, (
            f"reconcile_gone: source_key={source_key!r} — 0 stale "
            f"(all {available_count} available vehicles were re-seen)."
        )

    # Safety guard: refuse to retire an implausible fraction of a non-trivial
    # inventory in one sweep (partial/failed run, not real churn).
    fraction = stale_count / available_count
    if available_count >= MIN_INVENTORY_FOR_GUARD and fraction > max_gone_fraction:
        reason = (
            f"reconcile_gone ABORTED for source_key={source_key!r}: would retire "
            f"{stale_count}/{available_count} ({fraction:.0%}) > ceiling "
            f"{max_gone_fraction:.0%} — almost certainly a partial/failed harvest, "
            f"not real churn. No vehicles touched."
        )
        logger.warning(reason)
        return 0, reason

    gone_count = 0
    for row in rows:
        vulid: str = row["vehicle_ulid"]
        price = row["price"]

        # Resolve entity_ulid for the event row.
        entity_ulid: str | None = await conn.fetchval(_GET_ENTITY_ULID, vulid)
        if entity_ulid is None:
            # Orphan vehicle (no entity) — skip, log, do not mark gone.
            logger.warning(
                "reconcile_gone: vehicle_ulid=%s has no entity_ulid; skipping", vulid
            )
            continue

        # Mark gone (status change only — no other mutation).
        await conn.execute(_MARK_GONE, vulid)

        # Emit GONE event with old_value snapshot matching ingest.py convention:
        # old_value = {"price": <float|null>}, new_value = null.
        old_value: dict[str, Any] = {"price": float(price) if price is not None else None}
        await conn.execute(
            _INSERT_GONE_EVENT,
            ulid(), vulid, entity_ulid, json.dumps(old_value),
        )
        gone_count += 1

    reason = (
        f"reconcile_gone: source_key={source_key!r} — "
        f"marked {gone_count}/{available_count} vehicles as gone "
        f"(last_seen < {run_started_at.isoformat()}, "
        f"fraction={fraction:.0%} <= ceiling {max_gone_fraction:.0%})."
    )
    return gone_count, reason


# ---------------------------------------------------------------------------
# diff_vehicle — pure function, no I/O
# ---------------------------------------------------------------------------

def diff_vehicle(
    old: dict[str, Any],
    new: Any,
) -> list[dict[str, Any]]:
    """Compare an existing vehicle snapshot against a freshly scraped record.

    Args:
        old: Dict-like snapshot from the DB.  Expected keys (all optional):
             price (Decimal/float/int/None), km (int/None), photo_url (str/None).
        new: Object with attributes price, km, photo_url (any may be None).
             Typically a scraped dataclass instance, but any object with those
             attributes is accepted.

    Returns:
        List of event dicts, each with keys:
            event_type  str   — 'PRICE_CHANGE', 'KM_CHANGE', or 'PHOTO_CHANGE'
            old_value   dict  — snapshot before change (Python object, not JSON)
            new_value   dict  — value after change (Python object, not JSON)
        Returns [] when nothing changed (no false positives generated).

    No DB I/O.  Caller is responsible for persisting the returned events.
    """
    events: list[dict[str, Any]] = []

    # -- PRICE_CHANGE --
    old_price = old.get("price") if isinstance(old, dict) else getattr(old, "price", None)
    new_price = getattr(new, "price", None)
    if (
        old_price is not None
        and new_price is not None
        and float(old_price) != float(new_price)
    ):
        events.append({
            "event_type": "PRICE_CHANGE",
            "old_value": {"price": float(old_price)},
            "new_value": {"price": float(new_price)},
        })

    # -- KM_CHANGE --
    old_km = old.get("km") if isinstance(old, dict) else getattr(old, "km", None)
    new_km = getattr(new, "km", None)
    if (
        old_km is not None
        and new_km is not None
        and int(old_km) != int(new_km)
    ):
        events.append({
            "event_type": "KM_CHANGE",
            "old_value": {"km": int(old_km)},
            "new_value": {"km": int(new_km)},
        })

    # -- PHOTO_CHANGE --
    old_photo = old.get("photo_url") if isinstance(old, dict) else getattr(old, "photo_url", None)
    new_photo = getattr(new, "photo_url", None)
    if new_photo and old_photo != new_photo:
        events.append({
            "event_type": "PHOTO_CHANGE",
            "old_value": {"photo": old_photo},
            "new_value": {"photo": new_photo},
        })

    return events
