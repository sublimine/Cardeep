"""F0 recon for 07-marketing.md — real SQL truth on the fields the ad-audit (C1) and
the feed export (C6) depend on. Re-executable (same pattern as
scripts/f0_market_volume_truth.py, 01-market-intelligence F0).

Measures (plans/cardeep-omni/07-marketing.md S5.2 "Hueco conocido" + S9 F0):
  1. vin_ref / photo_url / photo_hash density on servable_vehicle (available fleet).
  2. platform_listing rows with a non-null platform_price, status='listed'.
  3. GONE vehicle_event count that has >=1 platform_listing edge (any status).
  4. Title richness proxy: vehicles with make+model+year all present (c9 input).
  5. fuel/transmission presence (c6).
"""
from __future__ import annotations

import asyncio
import os

import asyncpg

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")


async def main() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        total_available = await conn.fetchval("SELECT count(*) FROM vehicle WHERE status='available'")
        total_vehicles = await conn.fetchval("SELECT count(*) FROM vehicle")

        vin_ref_present = await conn.fetchval(
            "SELECT count(*) FROM vehicle WHERE status='available' AND vin_ref IS NOT NULL"
        )
        photo_url_present = await conn.fetchval(
            "SELECT count(*) FROM vehicle WHERE status='available' AND photo_url IS NOT NULL"
        )
        photo_hash_present = await conn.fetchval(
            "SELECT count(*) FROM vehicle WHERE status='available' AND photo_hash IS NOT NULL"
        )
        fuel_trans_present = await conn.fetchval(
            "SELECT count(*) FROM vehicle WHERE status='available' AND fuel IS NOT NULL AND transmission IS NOT NULL"
        )
        title_rich = await conn.fetchval(
            "SELECT count(*) FROM vehicle WHERE status='available' AND make IS NOT NULL "
            "AND model IS NOT NULL AND year IS NOT NULL"
        )
        price_present = await conn.fetchval(
            "SELECT count(*) FROM vehicle WHERE status='available' AND price IS NOT NULL AND price > 0"
        )
        km_present = await conn.fetchval(
            "SELECT count(*) FROM vehicle WHERE status='available' AND km IS NOT NULL"
        )

        pl_listed_price = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE status='listed' AND platform_price IS NOT NULL"
        )
        pl_listed_total = await conn.fetchval("SELECT count(*) FROM platform_listing WHERE status='listed'")
        pl_total = await conn.fetchval("SELECT count(*) FROM platform_listing")

        # c10 real signal: listed edges where platform_price != vehicle.price (both present)
        pl_divergent = await conn.fetchval(
            """SELECT count(*) FROM platform_listing pl
                 JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
                WHERE pl.status='listed' AND pl.platform_price IS NOT NULL
                  AND v.price IS NOT NULL AND pl.platform_price <> v.price"""
        )

        # c11 signal: >=2 PRICE_CHANGE events (downward) in 30d on still-available vehicles
        stale_price_drop = await conn.fetchval(
            """
            WITH drops AS (
                SELECT vehicle_ulid, count(*) AS n_drops
                  FROM vehicle_event
                 WHERE event_type = 'PRICE_CHANGE'
                   AND observed_at > now() - interval '30 days'
                   AND (new_value->>'price')::numeric < (old_value->>'price')::numeric
                 GROUP BY vehicle_ulid
                HAVING count(*) >= 2
            )
            SELECT count(*) FROM drops d JOIN vehicle v ON v.vehicle_ulid = d.vehicle_ulid
             WHERE v.status = 'available'
            """
        )

        # GONE events that have >=1 platform_listing edge (any status) — C5 substrate
        gone_total = await conn.fetchval("SELECT count(*) FROM vehicle_event WHERE event_type='GONE'")
        gone_with_platform_edge = await conn.fetchval(
            """SELECT count(DISTINCT ve.vehicle_ulid) FROM vehicle_event ve
                WHERE ve.event_type = 'GONE'
                  AND EXISTS (SELECT 1 FROM platform_listing pl WHERE pl.vehicle_ulid = ve.vehicle_ulid)"""
        )

        # Number of dealers with >=1 listed platform edge (servable) — C3 substrate size
        dealers_with_edges = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM vehicle v
                 JOIN platform_listing pl ON pl.vehicle_ulid = v.vehicle_ulid
                WHERE v.status='available' AND pl.status='listed'"""
        )

        print("=== F0 07-marketing recon ===")
        print(f"vehicle total: {total_vehicles}")
        print(f"vehicle available: {total_available}")
        print(f"vin_ref present (available): {vin_ref_present} ({vin_ref_present/total_available*100:.2f}%)")
        print(f"photo_url present (available): {photo_url_present} ({photo_url_present/total_available*100:.2f}%)")
        print(f"photo_hash present (available): {photo_hash_present} ({photo_hash_present/total_available*100:.2f}%)")
        print(f"fuel+transmission present (available): {fuel_trans_present} ({fuel_trans_present/total_available*100:.2f}%)")
        print(f"title-rich make+model+year (available): {title_rich} ({title_rich/total_available*100:.2f}%)")
        print(f"price>0 present (available): {price_present} ({price_present/total_available*100:.2f}%)")
        print(f"km present (available): {km_present} ({km_present/total_available*100:.2f}%)")
        print(f"platform_listing total rows: {pl_total}")
        print(f"platform_listing listed: {pl_listed_total}")
        print(f"platform_listing listed w/ platform_price: {pl_listed_price} ({(pl_listed_price/pl_listed_total*100 if pl_listed_total else 0):.2f}%)")
        print(f"platform_listing listed w/ price DIVERGENT vs vehicle.price: {pl_divergent}")
        print(f"vehicles w/ >=2 downward PRICE_CHANGE in 30d, still available (c11 signal): {stale_price_drop}")
        print(f"vehicle_event GONE total: {gone_total}")
        print(f"GONE vehicles with >=1 platform_listing edge (any status): {gone_with_platform_edge}")
        print(f"dealers with >=1 available vehicle listed on >=1 platform: {dealers_with_edges}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
