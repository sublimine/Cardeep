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

from pipeline.delta_photo import PHASH_HAMMING_MAX, hamming, is_phash
from pipeline.ids import ulid
from pipeline.price_sanity import sanitize_km, sanitize_price

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
   AND status = 'available'
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


async def emit_gone_events(
    conn: asyncpg.Connection,
    vehicle_ulids,
) -> int:
    """Emit the GONE event for vehicles a connector retired DIRECTLY (status already flipped to 'gone').

    group_subastas_wholesale and localizavo_wholesale retire aged-out lots by their platform-edge set
    (not by last_seen), so they cannot route through reconcile_gone — but they MUST still record the
    baja in the immutable timeline, exactly as reconcile_gone does. Before this helper they flipped
    vehicle.status='gone' WITHOUT emitting the event, leaving silent bajas (audit P4: 1,823 gone
    vehicles with no GONE event, all from these two connectors).

    Contract (mirrors reconcile_gone): one GONE event per vehicle, old_value={"price": <float|null>}
    snapshot from the current row, new_value=null, observed_at defaults to now() (the baja is detected
    now). Idempotent: a vehicle that already has a GONE event is skipped — the timeline has no UNIQUE
    on (vehicle_ulid, event_type), so dedup is enforced here. The caller must have already set
    status='gone'; this writes ONLY the event. Returns the number of events emitted.
    """
    emitted = 0
    for vulid in vehicle_ulids:
        row = await conn.fetchrow(
            "SELECT entity_ulid, price FROM vehicle WHERE vehicle_ulid = $1", vulid)
        if row is None or row["entity_ulid"] is None:
            continue  # orphan / missing vehicle — cannot attribute an event
        if await conn.fetchval(
            "SELECT 1 FROM vehicle_event WHERE vehicle_ulid = $1 AND event_type = 'GONE' LIMIT 1",
            vulid,
        ):
            continue  # idempotent: never a duplicate GONE on the immutable timeline
        old_value = {"price": float(row["price"]) if row["price"] is not None else None}
        await conn.execute(
            _INSERT_GONE_EVENT, ulid(), vulid, row["entity_ulid"], json.dumps(old_value))
        emitted += 1
    return emitted


async def reconcile_gone(
    conn: asyncpg.Connection,
    source_key: str,
    run_started_at: datetime,
    *,
    max_gone_fraction: float = 0.5,
    min_coverage: float | None = None,
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
    # COVERAGE GATE (audit P2 SU-A4 GONE): only retire not-re-seen vehicles when the latest harvest
    # was confirmed ~complete. A partial harvest leaves real inventory "not re-seen"; the >50% cap
    # below catches GROSS partials, but a 60%-complete harvest (40% not-seen) slips under it and would
    # falsely retire legit stock. The B9 coverage verdict is the completeness signal: refuse to retire
    # unless captured/declared >= min_coverage and the verdict is not REFUTED. "Better a hole than a lie."
    if min_coverage is not None:
        cov = await conn.fetchrow(
            "SELECT coverage_pct, verdict FROM source_coverage WHERE source_key = $1", source_key)
        if cov is None:
            return 0, (f"reconcile_gone SKIPPED source_key={source_key!r}: no coverage verdict — "
                       f"cannot confirm a complete harvest, refusing to retire any vehicle.")
        cov_pct = float(cov["coverage_pct"]) if cov["coverage_pct"] is not None else None
        if cov_pct is None or cov_pct < min_coverage:
            return 0, (f"reconcile_gone SKIPPED source_key={source_key!r}: coverage {cov_pct} < floor "
                       f"{min_coverage} — harvest incomplete; not-re-seen vehicles are likely "
                       f"un-captured, NOT gone.")
        if cov["verdict"] == "REFUTED":
            return 0, (f"reconcile_gone SKIPPED source_key={source_key!r}: coverage verdict REFUTED "
                       f"(inconsistent counts) — refusing to retire on an untrustworthy harvest.")

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

    # The whole sweep is ONE transaction (H3): either all not-re-seen vehicles are retired or
    # none are — a crash mid-loop must not leave a half-retired inventory (vehicle table and
    # vehicle_event inconsistent). reconcile_gone runs after record_run's own transaction, so
    # this opens a fresh transaction (a savepoint when a caller already holds one).
    gone_count = 0
    async with conn.transaction():
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

            # Mark gone, GUARDED on status='available' (H1): _FIND_STALE takes no FOR UPDATE,
            # so a concurrent retire (another connector, a re-run) can flip this row between
            # the fetch and here. The guard makes the UPDATE affect 0 rows when it is already
            # gone; we then skip the GONE event so the immutable timeline never gets a
            # duplicate GONE (vehicle_event has no UNIQUE on vehicle_ulid+event_type).
            mark_tag = await conn.execute(_MARK_GONE, vulid)
            if mark_tag == "UPDATE 0":
                continue  # already gone (race / re-run) — no duplicate event

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

    # -- PRICE_CHANGE -- (includes the NULL→valid promotion: a vehicle first listed without a
    # price that later gets one must FILL, not stay NULL forever. The old asymmetric guard
    # `old_price is not None` silently dropped that transition across all 26 wholesale connectors.)
    old_price = old.get("price") if isinstance(old, dict) else getattr(old, "price", None)
    new_price = sanitize_price(getattr(new, "price", None))  # junk (<=0 / >10M) -> None -> no event
    if new_price is not None and (old_price is None or float(old_price) != float(new_price)):
        events.append({
            "event_type": "PRICE_CHANGE",
            "old_value": {"price": float(old_price) if old_price is not None else None},
            "new_value": {"price": float(new_price)},
        })

    # -- KM_CHANGE -- (same NULL→valid promotion: km first absent then published must fill)
    old_km = old.get("km") if isinstance(old, dict) else getattr(old, "km", None)
    new_km = sanitize_km(getattr(new, "km", None))  # junk -> None -> no event
    if new_km is not None and (old_km is None or int(old_km) != int(new_km)):
        events.append({
            "event_type": "KM_CHANGE",
            "old_value": {"km": int(old_km) if old_km is not None else None},
            "new_value": {"km": int(new_km)},
        })

    # -- PHOTO_CHANGE -- content-aware when perceptual hashes are present (P08-S2).
    # With a pHash on BOTH sides we compare the 64-bit hash by Hamming distance: a car
    # RE-PHOTOGRAPHED on the SAME url is now caught, and a CDN that ROTATES the url of an
    # UNCHANGED image no longer false-fires. Falls back to the legacy photo_url string compare
    # when either side lacks a (well-formed) phash -> fully backward-compatible with the 26
    # connectors that do not yet populate photo_hash.
    old_photo = old.get("photo_url") if isinstance(old, dict) else getattr(old, "photo_url", None)
    new_photo = getattr(new, "photo_url", None)
    old_phash = old.get("photo_hash") if isinstance(old, dict) else getattr(old, "photo_hash", None)
    new_phash = getattr(new, "photo_hash", None)
    if is_phash(old_phash) and is_phash(new_phash):
        if hamming(old_phash, new_phash) > PHASH_HAMMING_MAX:
            events.append({
                "event_type": "PHOTO_CHANGE",
                "old_value": {"photo": old_photo, "phash": old_phash},
                "new_value": {"photo": new_photo, "phash": new_phash},
            })
    elif new_photo and old_photo != new_photo:
        events.append({
            "event_type": "PHOTO_CHANGE",
            "old_value": {"photo": old_photo},
            "new_value": {"photo": new_photo},
        })

    return events


# ---------------------------------------------------------------------------
# emit_change_deltas — shared landing-time delta emission for RE-SEEN vehicles
# (audit P2 SU-A4). Connector-agnostic: each connector passes its pre-run snapshot
# dict + its freshly-scraped vehicle objects, both keyed identically.
# ---------------------------------------------------------------------------

_BULK_INSERT_DELTA_EVENTS = """
INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type,
        old_value, new_value)
SELECT u.event_ulid, u.vehicle_ulid, u.entity_ulid, u.event_type,
       u.old_value::jsonb, u.new_value::jsonb
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[], $5::text[], $6::text[])
       AS u(event_ulid, vehicle_ulid, entity_ulid, event_type, old_value, new_value)
"""

_BULK_REFRESH_VEHICLES = """
UPDATE vehicle v SET price = COALESCE(u.price, v.price),
                     km = COALESCE(u.km, v.km),
                     photo_url = COALESCE(u.photo_url, v.photo_url)
  FROM unnest($1::text[], $2::numeric[], $3::bigint[], $4::text[])
       AS u(vehicle_ulid, price, km, photo_url)
 WHERE v.vehicle_ulid = u.vehicle_ulid
"""


async def emit_change_deltas(
    conn: asyncpg.Connection,
    existing_snap: dict[Any, dict],
    new_vehicles: dict[Any, Any],
    keys: list,
) -> dict[str, int]:
    """For RE-SEEN vehicles, emit PRICE/KM/PHOTO_CHANGE events + refresh the served row.

    existing_snap[key] = {"vehicle_ulid", "price", "km", "photo_url"} (DB snapshot before this run).
    new_vehicles[key]  = the freshly-scraped vehicle object (attrs: price, km, photo_url).
    keys               = the keys to consider (the window's re-seen+new; new ones have no snapshot
                         and are skipped here — they go through the connector's NEW-event path).

    Writes ONLY vehicle_event (append) and vehicle price/km/photo (MVCC-clean: only rows that
    changed). No network. SAFE on a partial harvest (touches only re-seen vehicles — never retires;
    GONE is handled separately by reconcile_gone, which is coverage-gated). Returns per-type counts.
    Shared across connectors (DRY) so the delta semantics are identical and tested once.
    """
    ev_ulids: list[str] = []
    ev_v: list[str] = []
    ev_e: list[str] = []
    ev_t: list[str] = []
    ev_old: list[str] = []
    ev_new: list[str] = []
    up_v: list[str] = []
    up_price: list = []
    up_km: list = []
    up_photo: list = []
    counts = {"PRICE_CHANGE": 0, "KM_CHANGE": 0, "PHOTO_CHANGE": 0}
    for key in keys:
        snap = existing_snap.get(key)
        if snap is None:
            continue  # genuinely new vehicle — not a delta; handled by the NEW-event path
        new_obj = new_vehicles.get(key)
        if new_obj is None:
            continue
        events = diff_vehicle(snap, new_obj)
        if not events:
            continue
        vid = snap["vehicle_ulid"]
        # entity_ulid is the first element of the (entity_ulid, deep_link) key tuple by convention.
        ent = key[0] if isinstance(key, tuple) else snap.get("entity_ulid")
        for ev in events:
            ev_ulids.append(ulid())
            ev_v.append(vid)
            ev_e.append(ent)
            ev_t.append(ev["event_type"])
            ev_old.append(json.dumps(ev["old_value"]))
            ev_new.append(json.dumps(ev["new_value"]))
            counts[ev["event_type"]] = counts.get(ev["event_type"], 0) + 1
        up_v.append(vid)
        up_price.append(sanitize_price(new_obj.price))   # junk -> None -> COALESCE keeps old (no junk write)
        up_km.append(sanitize_km(new_obj.km))
        up_photo.append(new_obj.photo_url)
    if ev_ulids:
        await conn.execute(_BULK_INSERT_DELTA_EVENTS, ev_ulids, ev_v, ev_e, ev_t, ev_old, ev_new)
    if up_v:
        await conn.execute(_BULK_REFRESH_VEHICLES, up_v, up_price, up_km, up_photo)
    return counts
