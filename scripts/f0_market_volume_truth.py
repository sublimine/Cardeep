"""F0 (01-market-intelligence) — direct SQL volume truth for the market-intelligence pilar.

One-shot verification script (not a permanent module): runs every measurement listed in
carta section 9 F0 directly against the live cardeep-pg, twice where a second independent
path exists, and prints a report consumed to write
plans/cardeep-omni/01-market-intelligence-f0.md by hand (with the exact numbers, not
paraphrased).

Usage: python -m scripts.f0_market_volume_truth
"""
from __future__ import annotations

import asyncio
import os

import asyncpg

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")


async def main() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        print("=== F0.1 vehicle rows by status ===")
        rows = await conn.fetch("SELECT status, count(*) AS n FROM vehicle GROUP BY status ORDER BY status")
        for r in rows:
            print(f"  {r['status']:>10}: {r['n']:,}")
        total_vehicle = await conn.fetchval("SELECT count(*) FROM vehicle")
        print(f"  TOTAL: {total_vehicle:,}")

        print("\n=== F0.2 vehicle_event rows by type ===")
        rows = await conn.fetch(
            "SELECT event_type, count(*) AS n FROM vehicle_event GROUP BY event_type ORDER BY event_type"
        )
        for r in rows:
            print(f"  {r['event_type']:>14}: {r['n']:,}")
        total_events = await conn.fetchval("SELECT count(*) FROM vehicle_event")
        print(f"  TOTAL: {total_events:,}")

        print("\n=== F0.3 span temporal real ===")
        row = await conn.fetchrow(
            "SELECT min(observed_at) AS min_obs, max(observed_at) AS max_obs FROM vehicle_event"
        )
        print(f"  vehicle_event.observed_at: {row['min_obs']}  ->  {row['max_obs']}")
        span_days = (row["max_obs"] - row["min_obs"]).days if row["min_obs"] and row["max_obs"] else None
        print(f"  span_days = {span_days}")
        row2 = await conn.fetchrow("SELECT min(first_seen) AS min_fs, max(first_seen) AS max_fs FROM vehicle")
        print(f"  vehicle.first_seen: {row2['min_fs']}  ->  {row2['max_fs']}")

        print("\n=== F0.4 % price IS NULL (available only, servable_vehicle) ===")
        row = await conn.fetchrow(
            "SELECT count(*) AS n_total, "
            "count(*) FILTER (WHERE price IS NULL) AS n_null "
            "FROM servable_vehicle"
        )
        pct = (row["n_null"] / row["n_total"] * 100) if row["n_total"] else 0
        print(f"  servable_vehicle total={row['n_total']:,} price_null={row['n_null']:,} ({pct:.2f}%)")
        row_raw = await conn.fetchrow(
            "SELECT count(*) AS n_total, count(*) FILTER (WHERE price IS NULL) AS n_null "
            "FROM vehicle WHERE status='available'"
        )
        pct_raw = (row_raw["n_null"] / row_raw["n_total"] * 100) if row_raw["n_total"] else 0
        print(
            f"  raw vehicle status='available' total={row_raw['n_total']:,} "
            f"price_null={row_raw['n_null']:,} ({pct_raw:.2f}%)  [2nd via independent filter path]"
        )

        print("\n=== F0.5 % coches con make+model+year completos (available) ===")
        row = await conn.fetchrow(
            "SELECT count(*) AS n_total, "
            "count(*) FILTER (WHERE make IS NOT NULL AND model IS NOT NULL AND year IS NOT NULL) AS n_full "
            "FROM servable_vehicle"
        )
        pct_full = (row["n_full"] / row["n_total"] * 100) if row["n_total"] else 0
        print(f"  servable_vehicle total={row['n_total']:,} full_mmy={row['n_full']:,} ({pct_full:.2f}%)")

        print("\n=== F0.6 runs vam_verified en vehicle_cluster_run ===")
        rows = await conn.fetch(
            "SELECT vam_verified, count(*) AS n FROM vehicle_cluster_run GROUP BY vam_verified ORDER BY vam_verified"
        )
        if not rows:
            print("  vehicle_cluster_run: 0 rows (tabla vacía)")
        for r in rows:
            print(f"  vam_verified={r['vam_verified']}: {r['n']}")
        n_verified_runs = await conn.fetchval(
            "SELECT count(*) FROM vehicle_cluster_run WHERE vam_verified = TRUE"
        )
        print(f"  n_vam_verified_runs = {n_verified_runs}")
        n_canonical_rows = await conn.fetchval("SELECT count(*) FROM v_canonical_vehicle")
        print(f"  v_canonical_vehicle row count (served resolution) = {n_canonical_rows:,}")

        print("\n=== F0.7 cardinalidad de segmentos con n>=8 (M1 cohort: make+model+year_band+fuel+province) ===")
        # year_band: bands of width 1 as the carta says "banda de año (+/-1)" -> group by year directly
        # as the band anchor; n>=8 counted per exact (make,model,year,fuel,province_code) cohort on
        # servable_vehicle joined to entity for province_code. Canonical-only when a vam_verified run
        # exists (F0.6 determines that; here we report BOTH so F1 design decision is data-driven).
        row = await conn.fetchrow(
            """
            WITH cohort AS (
                SELECT v.make, v.model, v.year, v.fuel, e.province_code, count(*) AS n
                  FROM servable_vehicle v
                  JOIN entity e ON e.entity_ulid = v.entity_ulid
                 WHERE v.price IS NOT NULL AND v.make IS NOT NULL AND v.model IS NOT NULL
                   AND v.year IS NOT NULL AND e.province_code IS NOT NULL
                 GROUP BY v.make, v.model, v.year, v.fuel, e.province_code
            )
            SELECT count(*) FILTER (WHERE n >= 8) AS n_ge8,
                   count(*) AS n_total_cohorts,
                   sum(n) FILTER (WHERE n >= 8) AS vehicles_in_ge8_cohorts
              FROM cohort
            """
        )
        print(
            f"  cohorts total={row['n_total_cohorts']:,}  cohorts n>=8={row['n_ge8']:,}  "
            f"vehicles covered by n>=8 cohorts={row['vehicles_in_ge8_cohorts'] or 0:,}"
        )

        print("\n=== F0.8 contraste independiente: schema_migrations ledger (verifica migrate.py aplicado) ===")
        last_mig = await conn.fetchrow(
            "SELECT version, filename FROM schema_migrations ORDER BY version DESC LIMIT 1"
        )
        print(f"  last applied migration: {last_mig['version']} {last_mig['filename']}")

        print("\n=== F0.9 available_inventory global (2a vía, contraste con entities.py:83) ===")
        n_avail_global = await conn.fetchval(
            "SELECT count(DISTINCT COALESCE(vc.canonical_vehicle_ulid, v.vehicle_ulid)) "
            "FROM servable_vehicle v LEFT JOIN v_canonical_vehicle vc ON vc.vehicle_ulid = v.vehicle_ulid"
        )
        print(f"  global canonical-dedup available count = {n_avail_global:,}")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
