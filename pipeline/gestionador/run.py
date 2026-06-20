"""V4 Gestionador — cadence entrypoint for the cohort price-anomaly detector.

Thin runner (audit P2 price_trap v2): connect -> detect_price_trap -> route_anomalies -> close.
Zero external cost (DB reads + gestion_item upserts only). Idempotent within a UTC day
(dedupe_key carries the daily bucket); a persistently-bad car opens a fresh item per calendar day.

Surfacing is QUARANTINE-only: a flagged car is auto-hidden from `servable_vehicle` via an open
quarantining gestion_item, with ZERO write to vehicle.price (fully reversible — close the item to
re-show). Never NULLs, never DELETEs.

Run:  python -m pipeline.gestionador.run            # detect + route (opens quarantine items)
      CARDEEP_DSN=... python -m pipeline.gestionador.run
"""
from __future__ import annotations

import asyncio
import json
import logging
import os

import asyncpg

from pipeline.gestionador import detect
from pipeline.gestionador.detect import detect_price_trap
from pipeline.gestionador.route import route_anomalies

logger = logging.getLogger(__name__)

_DEFAULT_DSN = os.environ.get(
    "CARDEEP_DSN",
    "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep",
)

# Cohort-scan tuning, measured on the live DB (EXPLAIN): the two percentile group-aggregates each
# sort ~1.66M ln-prices, and the planner otherwise picks MERGE joins that add two MORE full sorts of
# the same 1.66M-row base. Forcing HASH joins (enable_mergejoin/nestloop off) drops those two extra
# sorts; a large work_mem keeps the remaining sorts in memory instead of spilling to disk (the spill
# is what turned this into a multi-minute pass). Session-level (this conn only) — env-overridable.
_WORK_MEM = os.environ.get("CARDEEP_GESTIONADOR_WORK_MEM", "384MB")


async def run_price_trap(conn: asyncpg.Connection) -> dict:
    """Detect cohort price anomalies and open/refresh their quarantine items.

    Caller owns the connection (so this composes inside a job's transaction).
    Returns a summary dict (high/low/items counts).
    """
    # SET is a utility statement and rejects bind params; set_config() is the parameterizable,
    # injection-safe equivalent (is_local=false -> session scope, this conn only). The cohort
    # statistic joins a 1.66M-row base to ~9.5k cohort rows — hashing the small side and probing
    # base ONCE is far cheaper than the planner's default sort-merge over the full base twice.
    await conn.execute("SELECT set_config('work_mem', $1, false)", _WORK_MEM)
    await conn.execute("SELECT set_config('enable_mergejoin', 'off', false)")
    await conn.execute("SELECT set_config('enable_nestloop', 'off', false)")
    anomalies = await detect_price_trap(conn)
    item_ids = await route_anomalies(conn, anomalies, actor="gestionador:price_trap")
    high = sum(1 for a in anomalies if a.measured.get("side") == "high")
    low = sum(1 for a in anomalies if a.measured.get("side") == "low")
    return {
        "detector": "price_trap",
        "flagged": len(anomalies),
        "high": high,
        "low": low,
        "items": len(item_ids),
    }


async def run_all(conn: asyncpg.Connection) -> dict:
    """Run EVERY live anomaly detector (V4 gestionador) and route each one's flags.

    Wires the full ``detect.DETECTORS`` registry instead of price_trap alone, skipping
    ``detect.STUB_DETECTORS`` (inert until their backing tables exist). Same €0/QUARANTINE-
    reversible contract as run_price_trap: DB reads + gestion_item upserts only, never NULLs
    or DELETEs. Per-detector isolation — one detector raising is logged and recorded
    (flagged=-1) but never aborts the rest, honouring the never-raises cadence contract.

    Caller owns the connection (composes inside a job's transaction). Returns a summary:
    ``{detectors:{name:{flagged,high,low,items}}, skipped:[...], total_flagged, total_items, errors:{}}``.
    """
    # Same session tuning as run_price_trap: the cohort percentile scan is the heaviest
    # detector; bumping work_mem + forcing hash joins keeps it from spilling. Harmless to
    # the lighter detectors (session scope, this conn only).
    await conn.execute("SELECT set_config('work_mem', $1, false)", _WORK_MEM)
    await conn.execute("SELECT set_config('enable_mergejoin', 'off', false)")
    await conn.execute("SELECT set_config('enable_nestloop', 'off', false)")

    per: dict[str, dict] = {}
    skipped: list[str] = []
    errors: dict[str, str] = {}
    total_flagged = 0
    total_items = 0
    for name, fn in detect.DETECTORS:
        if name in detect.STUB_DETECTORS:
            skipped.append(name)
            continue
        try:
            anomalies = await fn(conn)
            item_ids = await route_anomalies(conn, anomalies, actor=f"gestionador:{name}")
            high = sum(1 for a in anomalies if a.measured.get("side") == "high")
            low = sum(1 for a in anomalies if a.measured.get("side") == "low")
            per[name] = {"flagged": len(anomalies), "high": high, "low": low,
                         "items": len(item_ids)}
            total_flagged += len(anomalies)
            total_items += len(item_ids)
        except Exception as exc:  # noqa: BLE001 — never let one detector abort the cadence
            errors[name] = str(exc)
            per[name] = {"flagged": -1, "high": 0, "low": 0, "items": 0}
            logger.error("gestionador run_all: detector %s failed: %s", name, exc)

    return {
        "detectors": per,
        "skipped": skipped,
        "total_flagged": total_flagged,
        "total_items": total_items,
        "errors": errors,
    }


async def main() -> None:
    """CLI: connect to CARDEEP_DSN, run ALL live detectors, print a JSON summary."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    conn = await asyncpg.connect(_DEFAULT_DSN)
    try:
        summary = await run_all(conn)
    finally:
        await conn.close()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
