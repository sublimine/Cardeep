"""Production cadence job for C1 (07-marketing F1) — same run+persist pattern as
scripts/refresh_product_stats.py / pipeline/market/compute_stats.py: computed OFF the
request path, one ``listing_audit_run`` row + one ``listing_audit`` row per vehicle,
never recomputed client-side.

Photo dimensions (c8) are the one network-dependent check. To avoid re-hammering CDN
hosts on every run, a vehicle's photo is only re-fetched when its ``photo_url`` changed
since the last run (or it was never measured) — the prior measurement is reused
otherwise. All fetches are paced through pipeline.engine.governor's per-host token
bucket (pipeline/marketing/photo_dims.py).

Scope is bounded by design (``--cdp`` for one dealer, ``--limit`` as a hard safety cap
for an unscoped run) — a single invocation is NOT meant to sweep the full 2.1M-vehicle
servable census in one pass; that is a scheduler-cadence concern (00-MASTER.md S5.4:
"todo job batch de pilar se registra en el scheduler de 00"), out of this script's own
scope. Declared honestly rather than silently capped.

Usage:
    python -m scripts.run_listing_audit --cdp CDP-ES-46-AD9ZXC65
    python -m scripts.run_listing_audit --limit 500
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
from collections import defaultdict
from datetime import date, datetime, timezone

import asyncpg

from pipeline.ids import ulid
from pipeline.marketing.listing_audit import PlatformEdge, VehicleAuditInput, evaluate
from pipeline.marketing.photo_dims import PhotoFetchError, fetch_photo_dimensions

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

STAGNATION_WINDOW_DAYS = 30
DEFAULT_LIMIT = 2000


async def _fetch_vehicles(conn: asyncpg.Connection, *, cdp_code: str | None, limit: int) -> list[dict]:
    if cdp_code is not None:
        rows = await conn.fetch(
            """
            SELECT v.vehicle_ulid, v.price, v.make, v.model, v.year, v.km, v.vin_ref,
                   v.fuel, v.transmission, v.photo_url, v.title
              FROM vehicle v
              JOIN entity e ON e.entity_ulid = v.entity_ulid
             WHERE e.cdp_code = $1 AND v.status = 'available'
             ORDER BY v.vehicle_ulid
            """,
            cdp_code,
        )
    else:
        rows = await conn.fetch(
            """
            SELECT vehicle_ulid, price, make, model, year, km, vin_ref, fuel,
                   transmission, photo_url, title
              FROM vehicle
             WHERE status = 'available'
             ORDER BY vehicle_ulid
             LIMIT $1
            """,
            limit,
        )
    return [dict(r) for r in rows]


async def _fetch_platform_edges(conn: asyncpg.Connection, ulids: list[str]) -> dict[str, list[PlatformEdge]]:
    if not ulids:
        return {}
    rows = await conn.fetch(
        "SELECT vehicle_ulid, platform_price, status FROM platform_listing WHERE vehicle_ulid = ANY($1::text[])",
        ulids,
    )
    out: dict[str, list[PlatformEdge]] = defaultdict(list)
    for r in rows:
        price = float(r["platform_price"]) if r["platform_price"] is not None else None
        out[r["vehicle_ulid"]].append(PlatformEdge(platform_price=price, status=r["status"]))
    return out


async def _fetch_price_drops(conn: asyncpg.Connection, ulids: list[str]) -> dict[str, int]:
    if not ulids:
        return {}
    rows = await conn.fetch(
        """
        SELECT vehicle_ulid, count(*) AS n_drops
          FROM vehicle_event
         WHERE event_type = 'PRICE_CHANGE'
           AND vehicle_ulid = ANY($1::text[])
           AND observed_at > now() - ($2 || ' days')::interval
           AND (new_value->>'price')::numeric < (old_value->>'price')::numeric
         GROUP BY vehicle_ulid
        """,
        ulids, str(STAGNATION_WINDOW_DAYS),
    )
    return {r["vehicle_ulid"]: r["n_drops"] for r in rows}


async def _fetch_cached_photo_dims(conn: asyncpg.Connection, ulids: list[str]) -> dict[str, tuple[str | None, int | None, int | None]]:
    """Latest known (photo_url, width, height) per vehicle from v_latest_listing_audit's
    c8 evidence — so an unchanged photo is never re-downloaded on every run."""
    if not ulids:
        return {}
    rows = await conn.fetch(
        "SELECT vehicle_ulid, checks FROM v_latest_listing_audit WHERE vehicle_ulid = ANY($1::text[])",
        ulids,
    )
    out: dict[str, tuple[str | None, int | None, int | None]] = {}
    for r in rows:
        checks = r["checks"] if isinstance(r["checks"], list) else json.loads(r["checks"])
        c8 = next((c for c in checks if c.get("check_id") == "c8"), None)
        if c8 is None:
            continue
        ev = c8.get("evidence", {})
        out[r["vehicle_ulid"]] = (ev.get("photo_url"), ev.get("width"), ev.get("height"))
    return out


async def _resolve_photo_dims(
    vehicle_ulid: str, photo_url: str | None,
    cached: dict[str, tuple[str | None, int | None, int | None]],
) -> tuple[int | None, int | None]:
    if photo_url is None:
        return None, None
    prev = cached.get(vehicle_ulid)
    if prev is not None and prev[0] == photo_url and prev[1] is not None:
        return prev[1], prev[2]
    try:
        w, h = await fetch_photo_dimensions(photo_url)
        return w, h
    except PhotoFetchError:
        return None, None


def _serialize_checks(result) -> list[dict]:
    return [
        {
            "check_id": c.check_id, "label": c.label, "passed": c.passed,
            "points_awarded": c.points_awarded, "points_possible": c.points_possible,
            "message": c.message, "evidence": c.evidence,
        }
        for c in result.checks
    ]


async def run(*, cdp_code: str | None, limit: int, fetch_photos: bool, dsn: str = DSN) -> dict:
    conn = await asyncpg.connect(dsn)
    try:
        run_ulid = ulid()
        started_at = datetime.now(timezone.utc)
        vehicles = await _fetch_vehicles(conn, cdp_code=cdp_code, limit=limit)
        ulids = [v["vehicle_ulid"] for v in vehicles]

        edges_by_vehicle = await _fetch_platform_edges(conn, ulids)
        drops_by_vehicle = await _fetch_price_drops(conn, ulids)
        cached_photo_dims = await _fetch_cached_photo_dims(conn, ulids) if fetch_photos else {}

        today = date.today()
        rows_to_insert: list[tuple] = []
        score_histogram: dict[int, int] = defaultdict(int)

        for v in vehicles:
            width = height = None
            if fetch_photos:
                width, height = await _resolve_photo_dims(v["vehicle_ulid"], v["photo_url"], cached_photo_dims)

            audit_input = VehicleAuditInput(
                vehicle_ulid=v["vehicle_ulid"], price=float(v["price"]) if v["price"] is not None else None,
                make=v["make"], model=v["model"], year=v["year"], km=v["km"], vin_ref=v["vin_ref"],
                fuel=v["fuel"], transmission=v["transmission"], photo_url=v["photo_url"], title=v["title"],
                photo_width=width, photo_height=height,
                platform_edges=tuple(edges_by_vehicle.get(v["vehicle_ulid"], ())),
                price_drops_30d=drops_by_vehicle.get(v["vehicle_ulid"], 0),
                today=today,
            )
            result = evaluate(audit_input)
            score_histogram[result.score // 10 * 10] += 1
            rows_to_insert.append((run_ulid, v["vehicle_ulid"], result.score, json.dumps(_serialize_checks(result))))

        async with conn.transaction():
            await conn.execute(
                "INSERT INTO listing_audit_run (run_ulid, started_at, vehicles_audited, engine_version) "
                "VALUES ($1, $2, $3, 'v1')",
                run_ulid, started_at, len(vehicles),
            )
            if rows_to_insert:
                await conn.executemany(
                    "INSERT INTO listing_audit (run_ulid, vehicle_ulid, score, checks) VALUES ($1, $2, $3, $4::jsonb)",
                    rows_to_insert,
                )
            await conn.execute(
                "UPDATE listing_audit_run SET finished_at = now() WHERE run_ulid = $1", run_ulid,
            )

        return {
            "run_ulid": run_ulid, "vehicles_audited": len(vehicles),
            "score_histogram": dict(sorted(score_histogram.items())),
        }
    finally:
        await conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cdp", default=None, help="Audit only this dealer's cdp_code")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Safety cap for an unscoped run")
    parser.add_argument("--no-photos", action="store_true", help="Skip the network-dependent c8 photo-dimension check (dims stay unmeasured)")
    args = parser.parse_args()

    summary = asyncio.run(run(cdp_code=args.cdp, limit=args.limit, fetch_photos=not args.no_photos))
    print(f"listing_audit run {summary['run_ulid']}: {summary['vehicles_audited']} vehicles audited")
    print(f"score histogram (bucketed by 10): {summary['score_histogram']}")


if __name__ == "__main__":
    main()
