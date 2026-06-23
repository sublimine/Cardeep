"""Backfill the missing GONE vehicle_event for the gone-without-event orphans.

WHAT THIS FIXES
---------------
A vehicle whose status is 'gone' but which has NO GONE row in vehicle_event is a
SILENT baja: the served, append-only history (vehicle_event) is missing the
disappearance that the served state (vehicle.status='gone') already records.

Audit residual (verified live on :5433, 2026-06-23): exactly 24 such orphans
remain, ALL from source_key='subastacar_wholesale', ALL under one seller entity
(entity_ulid=01KV14AFF18RWQGJT0KABKB04A), ALL with the IDENTICAL
last_seen=2026-06-22 12:50:47.361737+00 — i.e. one reconcile sweep. Every one has
a non-null entity_ulid, so every one is attributable (0 un-attributable orphans).

ROOT CAUSE (read, not assumed)
------------------------------
pipeline/platform/subastacar_wholesale.py::_reconcile_aged_out flips
`UPDATE vehicle SET status='gone', last_seen=now() WHERE vehicle_ulid=ANY(...)`
and NEVER calls emit_gone_events -> silent baja. This is the SAME bug class
already fixed for its two sibling auction connectors (group_subastas_wholesale and
localizavo_wholesale both call emit_gone_events after their flip); subastacar was
the lone un-fixed sibling of the P4 silent-gone fix. The connector code itself is
fixed separately; THIS script repairs only the historical 24 rows it left behind.

WHY emit_gone_events CANNOT be reused for THIS backfill
-------------------------------------------------------
pipeline.delta.emit_gone_events inserts via _INSERT_GONE_EVENT, which omits
observed_at -> vehicle_event.observed_at takes its column DEFAULT now() (verified:
observed_at is the ONLY timestamp column on vehicle_event). That stamps the baja as
TODAY, but the real disappearance was detected at the vehicle's last_seen
(2026-06-22 12:50:47), the instant the aged-out sweep flipped it. Using
emit_gone_events live would fabricate a wrong occurred_at on the immutable
timeline. This script therefore uses an observed_at-EXPLICIT INSERT and sets
observed_at = the vehicle's last_seen. occurred_at is honest: last_seen IS the
detected-baja instant for an aged-out reconcile.

NO FABRICATION
--------------
old_value={"price": <float|null>} re-read live from the row (identical to the
reconcile_gone / emit_gone_events convention); new_value=NULL; event_type='GONE';
observed_at = the row's real last_seen. Nothing is invented.

IDEMPOTENT
----------
vehicle_event has NO UNIQUE on (vehicle_ulid, event_type), so a non-guarded re-run
would DUPLICATE GONE rows on the immutable timeline. Each candidate is re-checked
(SELECT 1 ... event_type='GONE') immediately before insert — the same guard
emit_gone_events uses — so a re-run is a clean no-op.

REVERSIBLE
----------
Every inserted event_ulid is captured and printed. No vehicle row is touched
(status is already 'gone'). Full rollback:
    DELETE FROM vehicle_event WHERE event_ulid = ANY(<the printed ulids>);
On --apply the ulids are also written to a sidecar log (see ROLLBACK_LOG) so the
rollback set survives losing the console output.

SCOPE GUARD
-----------
The candidate set is intentionally restricted to the verified orphan signature
(status='gone', non-null entity_ulid, no existing GONE event). Any candidate that
is NOT under subastacar_wholesale is reported and ABORTS the run: a different
silent-gone source would be a new, un-audited bug class that must be traced before
its bajas are reconstructed — not swept up blindly here.

Usage:
    python scripts/backfill_gone_events.py            # DRY-RUN (default): rolls back, prints plan
    python scripts/backfill_gone_events.py --apply    # COMMIT the reconstructed GONE events
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.ids import ulid

DSN = os.environ.get(
    "CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep")

# The verified orphan source. Any candidate outside this source aborts the run
# (see SCOPE GUARD in the module docstring).
EXPECTED_SOURCE_KEY = "subastacar_wholesale"

# Where the committed event_ulids are appended on --apply, so the rollback set
# survives the console scrolling away. Rollback = DELETE ... WHERE event_ulid =
# ANY(<these>).
ROLLBACK_LOG = os.path.join(os.path.dirname(__file__), "backfill_gone_events_rollback.log")


# Candidates: gone, attributable (entity_ulid present), and NOT already carrying a
# GONE event. source_key is read via entity_source for the scope guard; it is a
# LEFT JOIN so a candidate with no source row still surfaces (and then trips the
# guard) rather than being silently filtered out.
_FIND = """
SELECT v.vehicle_ulid,
       v.entity_ulid,
       v.price,
       v.last_seen,
       es.source_key
  FROM vehicle v
  LEFT JOIN entity_source es ON es.entity_ulid = v.entity_ulid
 WHERE v.status = 'gone'
   AND v.entity_ulid IS NOT NULL
   AND NOT EXISTS (SELECT 1 FROM vehicle_event ve
                    WHERE ve.vehicle_ulid = v.vehicle_ulid
                      AND ve.event_type = 'GONE')
 ORDER BY v.vehicle_ulid
"""

# Per-row idempotency guard, evaluated inside the transaction immediately before
# each insert (mirrors pipeline.delta.emit_gone_events). vehicle_event has no
# UNIQUE on (vehicle_ulid, event_type), so this is the only dedup.
_HAS_GONE = """
SELECT 1 FROM vehicle_event
 WHERE vehicle_ulid = $1 AND event_type = 'GONE'
 LIMIT 1
"""

# observed_at-EXPLICIT insert: it names observed_at so it is NOT the column's
# DEFAULT now() path. Column order matches pipeline.delta._INSERT_GONE_EVENT plus
# the explicit observed_at.
_INSERT = """
INSERT INTO vehicle_event
       (event_ulid, vehicle_ulid, entity_ulid, event_type, old_value, new_value, observed_at)
VALUES ($1, $2, $3, 'GONE', $4::jsonb, NULL, $5)
"""

# Post-backfill invariants (computed inside the tx, before commit/rollback).
_REMAINING = """
SELECT count(*) FROM vehicle v
 WHERE v.status = 'gone'
   AND NOT EXISTS (SELECT 1 FROM vehicle_event ve
                    WHERE ve.vehicle_ulid = v.vehicle_ulid
                      AND ve.event_type = 'GONE')
"""

_UNATTRIBUTABLE = """
SELECT count(*) FROM vehicle v
 WHERE v.status = 'gone'
   AND v.entity_ulid IS NULL
   AND NOT EXISTS (SELECT 1 FROM vehicle_event ve
                    WHERE ve.vehicle_ulid = v.vehicle_ulid
                      AND ve.event_type = 'GONE')
"""


def _record_rollback(applied_ulids: list[str]) -> None:
    """Append the committed event_ulids to the sidecar rollback log."""
    if not applied_ulids:
        return
    stamp = datetime.now(timezone.utc).isoformat()
    with open(ROLLBACK_LOG, "a", encoding="utf-8") as fh:
        fh.write(f"# {stamp}  backfill_gone_events --apply  ({len(applied_ulids)} events)\n")
        fh.write(f"# rollback: DELETE FROM vehicle_event WHERE event_ulid = ANY(ARRAY{applied_ulids});\n")
        for u in applied_ulids:
            fh.write(u + "\n")


async def main() -> int:
    apply = "--apply" in sys.argv

    import asyncpg

    conn = await asyncpg.connect(DSN)
    try:
        rows = await conn.fetch(_FIND)
        print(f"candidates (status='gone', attributable, no GONE event): {len(rows)}")

        # SCOPE GUARD: every candidate must be the audited subastacar signature.
        off_scope = [r for r in rows if r["source_key"] != EXPECTED_SOURCE_KEY]
        if off_scope:
            print(
                f"ABORT: {len(off_scope)} candidate(s) are NOT from "
                f"{EXPECTED_SOURCE_KEY!r} — a different silent-gone source is a new, "
                f"un-audited bug class and must be traced before its bajas are "
                f"reconstructed. Off-scope candidates:")
            for r in off_scope[:20]:
                print(f"    {r['vehicle_ulid']} source_key={r['source_key']!r} "
                      f"entity={r['entity_ulid']}")
            return 2

        if not rows:
            print("Nothing to backfill — every gone vehicle already has its GONE event.")
            return 0

        applied_ulids: list[str] = []
        tr = conn.transaction()
        await tr.start()
        try:
            skipped = 0
            for r in rows:
                # Per-row idempotency re-check inside the tx (belt and braces with _FIND).
                if await conn.fetchval(_HAS_GONE, r["vehicle_ulid"]):
                    skipped += 1
                    continue
                price = r["price"]
                old_value = {"price": float(price) if price is not None else None}
                ev_ulid = ulid()
                await conn.execute(
                    _INSERT,
                    ev_ulid,
                    r["vehicle_ulid"],
                    r["entity_ulid"],
                    json.dumps(old_value),
                    r["last_seen"],  # observed_at = real detected-baja instant. NOT now().
                )
                applied_ulids.append(ev_ulid)

            remaining = await conn.fetchval(_REMAINING)
            unattributable = await conn.fetchval(_UNATTRIBUTABLE)

            print(f"reconstructed GONE events (in tx): {len(applied_ulids)}  (skipped existing: {skipped})")
            print(f"remaining gone-without-event after backfill: {remaining}  "
                  f"(un-attributable, entity_ulid NULL: {unattributable})")

            # After the backfill the ONLY rows that may legitimately remain are the
            # un-attributable orphans (no entity_ulid -> no event can be attributed).
            # Any excess is a bug; refuse to commit it.
            assert remaining == unattributable, (
                f"INVARIANT BROKEN: remaining ({remaining}) must equal un-attributable "
                f"orphans ({unattributable}). Aborting without commit.")

            if apply:
                await tr.commit()
                _record_rollback(applied_ulids)
                print(f"APPLIED: {len(applied_ulids)} GONE events committed.")
                print(f"ROLLBACK ({len(applied_ulids)} event_ulids logged to {ROLLBACK_LOG}):")
                print(f"  DELETE FROM vehicle_event WHERE event_ulid = ANY(ARRAY{applied_ulids});")
            else:
                await tr.rollback()
                print("DRY-RUN (rolled back). Re-run with --apply to commit.")
                print("Would-be event_ulids (regenerated fresh on --apply):")
                print(f"  {applied_ulids}")
        except Exception:
            await tr.rollback()
            raise
    finally:
        await conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
