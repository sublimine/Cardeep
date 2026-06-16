"""Backfill GONE events for the silent bajas (audit P4-A).

1,823 vehicles (from group_subastas_wholesale + localizavo_wholesale) were flipped to status='gone'
by their aged-out reconcile WITHOUT a GONE event being recorded — a hole in "historial completo".
The connectors are now fixed (they call pipeline.delta.emit_gone_events); this one-shot completes
the history for the pre-fix rows.

The reconstructed event uses observed_at = vehicle.last_seen (the last time the lot was confirmed
live; the baja happened at-or-after that, so last_seen is a defensible lower-bound timestamp) and the
same old_value={"price": <float|null>} convention as a live GONE. These events are RECONSTRUCTED from
the gone status, NOT observed in real time — that provenance lives in this script, the commit, and
PROGRESO.md. Idempotent: a vehicle that already has a GONE event is skipped, so a re-run is a no-op.

Usage:
    python scripts/backfill_gone_events.py            # DRY-RUN (rolls back, prints counts)
    python scripts/backfill_gone_events.py --apply     # COMMIT the reconstructed events
"""
from __future__ import annotations

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.ids import ulid

DSN = os.environ.get("CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep")

_FIND = """
SELECT v.vehicle_ulid, v.entity_ulid, v.price, v.last_seen
  FROM vehicle v
 WHERE v.status = 'gone'
   AND v.entity_ulid IS NOT NULL
   AND NOT EXISTS (SELECT 1 FROM vehicle_event ve
                    WHERE ve.vehicle_ulid = v.vehicle_ulid AND ve.event_type = 'GONE')
"""

_INSERT = """
INSERT INTO vehicle_event
       (event_ulid, vehicle_ulid, entity_ulid, event_type, old_value, new_value, observed_at)
VALUES ($1, $2, $3, 'GONE', $4::jsonb, NULL, $5)
"""

_REMAINING = """
SELECT count(*) FROM vehicle v
 WHERE v.status = 'gone'
   AND NOT EXISTS (SELECT 1 FROM vehicle_event ve
                    WHERE ve.vehicle_ulid = v.vehicle_ulid AND ve.event_type = 'GONE')
"""

_ORPHANS = """
SELECT count(*) FROM vehicle v
 WHERE v.status = 'gone' AND v.entity_ulid IS NULL
   AND NOT EXISTS (SELECT 1 FROM vehicle_event ve
                    WHERE ve.vehicle_ulid = v.vehicle_ulid AND ve.event_type = 'GONE')
"""


async def main() -> None:
    apply = "--apply" in sys.argv
    import asyncpg
    conn = await asyncpg.connect(DSN)
    try:
        rows = await conn.fetch(_FIND)
        print(f"silent bajas to backfill (gone, has entity, no GONE event): {len(rows)}")
        tr = conn.transaction()
        await tr.start()
        try:
            n = 0
            for r in rows:
                old_value = {"price": float(r["price"]) if r["price"] is not None else None}
                await conn.execute(
                    _INSERT, ulid(), r["vehicle_ulid"], r["entity_ulid"],
                    json.dumps(old_value), r["last_seen"])
                n += 1
            remaining = await conn.fetchval(_REMAINING)
            orphans = await conn.fetchval(_ORPHANS)
            print(f"emitted (in tx): {n}")
            print(f"remaining silent bajas after backfill: {remaining}  (orphans w/o entity: {orphans})")
            assert remaining == orphans, (
                f"after backfill, remaining ({remaining}) must equal un-attributable orphans "
                f"({orphans}) — any excess is a bug")
            if apply:
                await tr.commit()
                print(f"APPLIED: {n} reconstructed GONE events committed.")
            else:
                await tr.rollback()
                print("DRY-RUN (rolled back). Re-run with --apply to commit.")
        except Exception:
            await tr.rollback()
            raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
