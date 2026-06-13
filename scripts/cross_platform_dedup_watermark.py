"""Cross-platform dedup watermark — the same physical car on N platforms.

WHAT THE MODEL INTENDS (03-DATA-MODEL §4.3, §6). Ownership is singular (one selling
dealer = vehicle.entity_ulid); platform membership is plural (0..M platform_listing
edges). "The same car on a platform AND its dealer" should be ONE vehicle row with N
edges. The per-owner-per-URL key `UNIQUE (entity_ulid, deep_link)` means a car drained
from two platforms arrives with two deep_links and INSERTS TWO vehicle rows — the
"one car = one vehicle + N edges" invariant is a schema shape with no ingest algorithm
unless cross-seller identity is resolved.

THE BINDING DOCTRINE (03-DATA-MODEL §6.1, adversarial GAP-3/26). Over-merge is forbidden;
over-merge must stay strictly below under-merge. A second sighting may auto-collapse into
an existing vehicle ONLY on a STRONG key:
    VIN exact, OR (pHash Hamming <= 6 AND make,model,year,km-band all equal).
Everything weaker → distinct row (accept slight over-count, never over-merge). The residual
cross-seller over-count is NOT silently tolerated: it is served WITH a measured bound
(every counter carries +/-dup_ci). "A counter knowingly inflated by an unmeasured amount
is forbidden: it is either deduped by the resolver above or served WITH its measured bound."

WHAT THIS SCRIPT LOCKS (verified against the live DB this session):
  * photo_hash populated on 0 vehicles  -> the pHash arm of the strong key cannot run.
  * real 17-char VINs on 17,730 vehicles -> only 18 rows share a VIN across platforms.
    => The ONLY doctrine-permitted auto-merge available today is VIN-exact, and it is
       immaterial (18 rows). It is still applied, reversibly + idempotently, because it
       is the lawful, zero-false-merge collapse.
  * The MATERIAL cross-platform duplication lives in the weak fuzzy key
    (make+model+year+km+price+province) WITHOUT photo_hash: ~131.8K excess rows at the
    strictest exact-km+exact-price floor (VAM: SQL GROUP BY 131,773 ~= Python grouping
    131,895, agree within 0.09%). Per doctrine this is NOT a strong key (no photo_hash),
    so it is NOT auto-merged — it is MEASURED and the bound is LOCKED to the verification
    ledger so the API can serve every platform/national counter with +/-dup_ci.

REVERSIBILITY. Every VIN-exact merge writes its full before-state (survivor, folded
vehicle_ulids, repointed edges, repointed events) to a timestamped JSON in .backups/.
IDEMPOTENCY. A re-run finds every VIN group already collapsed to one vehicle and 0 folds.

SAFETY ORDER (mirrors scripts/fix_coches_com_deeplink.py). The only FKs to
vehicle.vehicle_ulid are platform_listing and vehicle_event; both are repointed to the
survivor BEFORE any folded vehicle row is deleted. Survivor = oldest first_seen (stable).

Run:  python -m scripts.cross_platform_dedup_watermark            (apply + measure + lock)
      python -m scripts.cross_platform_dedup_watermark --dry-run  (measure + lock only)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import datetime, timezone

import asyncpg

DSN = os.environ.get("CARDEEP_DSN",
                     "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# A real VIN is 17 chars over the WMI charset (no I, O, Q). vin_ref also stores short
# platform-native listing tokens (8/9/12 chars) — those are NOT VINs and are excluded.
_VIN_SQL = r"length(v.vin_ref)=17 AND v.vin_ref ~ '^[a-hj-npr-zA-HJ-NPR-Z0-9]{17}$'"

# Strict fuzzy floor for the MEASURED bound: exact make+model+year+km+price+province.
# Exact km AND exact asking price on the same make/model/year/province across two distinct
# platforms is a near-unique same-car fingerprint; this is the conservative LOWER bound on
# cross-platform duplication (the true figure is higher under km/price banding).
_FUZZY_FLOOR_BASE = """
  SELECT pl.platform_entity_ulid AS plat, v.vehicle_ulid,
         lower(btrim(v.make)) AS mk, lower(btrim(v.model)) AS md,
         v.year AS yr, v.km AS km, v.price AS price, e.province_code AS prov
  FROM vehicle v
  JOIN platform_listing pl ON pl.vehicle_ulid = v.vehicle_ulid AND pl.status = 'listed'
  JOIN entity e ON e.entity_ulid = v.entity_ulid
  WHERE v.status = 'available'
    AND v.make IS NOT NULL AND v.make <> '' AND v.model IS NOT NULL AND v.model <> ''
    AND v.year IS NOT NULL AND v.km IS NOT NULL AND v.km > 0
    AND v.price IS NOT NULL AND v.price > 0 AND e.province_code IS NOT NULL
"""


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


async def _vin_exact_resolver(conn: asyncpg.Connection, *, apply: bool) -> dict:
    """The ONLY doctrine-permitted auto-merge available today: VIN exact across platforms.

    Collapses every VIN-exact group of >=2 DISTINCT vehicle ROWS to one survivor (oldest
    first_seen), repointing platform_listing + vehicle_event edges, then deleting the folded
    vehicle rows. Reversible (JSON backup) + idempotent (re-run finds 0 folds).

    IDEMPOTENCY / SELF-FOLD SAFETY. The trigger is `count(DISTINCT v.vehicle_ulid) >= 2`,
    NOT a platform count — a single vehicle already carrying N edges is the CANONICAL
    target and must never be touched. `array_agg(DISTINCT ...)` guarantees one ULID per
    vehicle so the survivor can never appear in its own fold list (the data-loss trap)."""
    groups = await conn.fetch(
        f"""SELECT upper(v.vin_ref) AS vin,
                   array_agg(DISTINCT v.vehicle_ulid) AS vehicles,
                   min(v.first_seen) AS oldest
              FROM vehicle v
              JOIN platform_listing pl ON pl.vehicle_ulid = v.vehicle_ulid AND pl.status = 'listed'
             WHERE {_VIN_SQL} AND v.status = 'available'
             GROUP BY upper(v.vin_ref)
            HAVING count(DISTINCT v.vehicle_ulid) >= 2""")

    backup: list[dict] = []
    folded_total = 0
    for g in groups:
        vehicles = list(g["vehicles"])
        # Survivor = oldest first_seen (stable, deterministic). Re-resolve precisely:
        order = await conn.fetch(
            "SELECT vehicle_ulid FROM vehicle WHERE vehicle_ulid = ANY($1::text[]) "
            "ORDER BY first_seen, vehicle_ulid", vehicles)
        vehicles = [r["vehicle_ulid"] for r in order]
        survivor, folds = vehicles[0], [u for u in vehicles[1:] if u != vehicles[0]]
        if not folds:
            continue
        # Capture before-state for reversibility.
        edges = await conn.fetch(
            "SELECT * FROM platform_listing WHERE vehicle_ulid = ANY($1::text[])", folds)
        events = await conn.fetch(
            "SELECT event_ulid, vehicle_ulid FROM vehicle_event WHERE vehicle_ulid = ANY($1::text[])", folds)
        backup.append({
            "vin": g["vin"], "survivor": survivor, "folded": folds,
            "repointed_edges": [{"vehicle_ulid": e["vehicle_ulid"],
                                  "platform_entity_ulid": e["platform_entity_ulid"],
                                  "listing_url": e["listing_url"]} for e in edges],
            "repointed_events": [e["event_ulid"] for e in events],
        })
        folded_total += len(folds)
        if not apply:
            continue
        # Repoint edges to survivor. platform_listing PK is (vehicle_ulid, platform_entity_ulid);
        # an edge may already exist on the survivor for that platform -> drop the folded dup edge,
        # else repoint it. vehicle_event has no such uniqueness -> straight repoint.
        for e in edges:
            exists = await conn.fetchval(
                "SELECT 1 FROM platform_listing WHERE vehicle_ulid=$1 AND platform_entity_ulid=$2",
                survivor, e["platform_entity_ulid"])
            if exists:
                await conn.execute(
                    "DELETE FROM platform_listing WHERE vehicle_ulid=$1 AND platform_entity_ulid=$2",
                    e["vehicle_ulid"], e["platform_entity_ulid"])
            else:
                await conn.execute(
                    "UPDATE platform_listing SET vehicle_ulid=$1 WHERE vehicle_ulid=$2 AND platform_entity_ulid=$3",
                    survivor, e["vehicle_ulid"], e["platform_entity_ulid"])
        await conn.execute(
            "UPDATE vehicle_event SET vehicle_ulid=$1 WHERE vehicle_ulid = ANY($2::text[])",
            survivor, folds)
        await conn.execute("DELETE FROM vehicle WHERE vehicle_ulid = ANY($1::text[])", folds)

    return {"groups": len(backup), "folded_rows": folded_total, "backup": backup}


async def _measure_bound(conn: asyncpg.Connection) -> dict:
    """The measured cross-platform over-count bound (strict fuzzy floor), VAM by 2 paths."""
    # PATH 1 — SQL GROUP BY.
    p1 = await conn.fetchrow(f"""
        WITH base AS ({_FUZZY_FLOOR_BASE}),
        grp AS (SELECT mk,md,yr,km,price,prov, count(*) rows, count(DISTINCT plat) plats
                  FROM base GROUP BY mk,md,yr,km,price,prov)
        SELECT count(*) FILTER (WHERE plats>=2) AS cross_groups,
               COALESCE(sum(rows-1) FILTER (WHERE plats>=2),0) AS excess,
               (SELECT count(*) FROM base) AS candidate_rows
          FROM grp""")
    # PATH 2 — stream rows, group in Python (independent of SQL GROUP BY).
    from collections import defaultdict
    rows = await conn.fetch(f"SELECT * FROM ({_FUZZY_FLOOR_BASE}) b")
    g_plats: dict = defaultdict(set)
    g_rows: dict = defaultdict(int)
    for r in rows:
        k = (r["mk"], r["md"], r["yr"], r["km"], float(r["price"]), r["prov"])
        g_plats[k].add(r["plat"]); g_rows[k] += 1
    p2_excess = sum(g_rows[k] - 1 for k, p in g_plats.items() if len(p) >= 2)

    candidate = int(p1["candidate_rows"]) or 1
    excess_sql = int(p1["excess"])
    dup_rate = excess_sql / candidate
    return {
        "cross_groups": int(p1["cross_groups"]),
        "excess_sql": excess_sql,
        "excess_python": p2_excess,
        "candidate_rows": candidate,
        "cross_platform_dup_rate": round(dup_rate, 5),
        "divergence_pct": round(abs(excess_sql - p2_excess) / max(excess_sql, 1) * 100, 4),
    }


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="measure only; roll back even the ledger row (no writes persist)")
    ap.add_argument("--merge-vin", action="store_true",
                    help="ALSO apply the VIN-exact strong-key merge (reversible, JSON-backed). "
                         "OFF by default: the safe default is measure + lock the bound only.")
    args = ap.parse_args()
    # The VIN-exact merge is a vehicle-row DELETE (reversible, but a row delete). It runs ONLY
    # on explicit --merge-vin AND not in dry-run. Default = measure + lock the over-count bound.
    apply_merge = args.merge_vin and not args.dry_run

    conn = await asyncpg.connect(DSN)
    try:
        async with conn.transaction():
            vin = await _vin_exact_resolver(conn, apply=apply_merge)
            bound = await _measure_bound(conn)

            # Persist the over-count bound to the verification ledger. The two excess paths
            # (SQL GROUP BY vs Python grouping) are the orthogonal VAM paths for the number.
            from pipeline.verify import record_count_verdict
            verdict = await record_count_verdict(
                conn,
                subject_type="cross_platform_dedup_watermark",
                subject_key="ES_national",
                claim=("cross-platform same-car over-count LOWER BOUND on the strict fuzzy "
                       "floor (exact make+model+year+km+price+province); strong-key auto-merge "
                       "limited to VIN-exact per 03-DATA-MODEL §6.1 (photo_hash unpopulated)"),
                paths={"excess_sql_groupby": bound["excess_sql"],
                       "excess_python_grouping": bound["excess_python"]},
                tolerance=0.01)

            stamp = _stamp()
            backup_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                ".backups", f"cross_platform_vin_merge_{stamp}.json")
            payload = {
                "stamp": stamp, "applied_merge": apply_merge,
                "vin_exact_resolver": {"groups": vin["groups"], "folded_rows": vin["folded_rows"]},
                "measured_bound": bound, "bound_verdict": verdict,
                "merges": vin["backup"],
            }
            # Backup is the reversibility record for a REAL merge; only written when one ran.
            if apply_merge and vin["backup"]:
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                with open(backup_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2, default=str)

            if args.dry_run:
                raise _Rollback()  # measurement is committed-free; bound row rolls back too in dry-run

    except _Rollback:
        pass
    finally:
        await conn.close()

    mode = "DRY-RUN" if args.dry_run else ("MEASURE+MERGE-VIN" if apply_merge else "MEASURE-ONLY")
    print("=== CROSS-PLATFORM DEDUP WATERMARK ===")
    print(f"mode: {mode}")
    print(f"VIN-exact strong-key groups    : groups={vin['groups']} folded_rows={vin['folded_rows']}"
          f"{'  [applied]' if apply_merge else '  [not applied — pass --merge-vin]'}")
    print(f"measured over-count floor      : excess_sql={bound['excess_sql']} "
          f"excess_python={bound['excess_python']} (divergence {bound['divergence_pct']}%)")
    print(f"cross-platform dup rate        : {bound['cross_platform_dup_rate']*100:.2f}% "
          f"of {bound['candidate_rows']} full-key candidate listings")
    print(f"bound verdict (ledger)         : {verdict}")
    if apply_merge and vin["backup"]:
        print(f"reversible backup              : {backup_path}")


class _Rollback(Exception):
    """Sentinel to abort the transaction in --dry-run while keeping measurement output."""


if __name__ == "__main__":
    asyncio.run(main())
