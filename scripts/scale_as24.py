"""Scale AutoScout24: discover dealers at volume, harvest each dealer's full
inventory (entity + vehicles + delta + VAM), persist recipe.

Harvesting a dealer ingests both its entity (from the profile page) and its
inventory, so discovery and inventory scale together. Rate-limited and polite.

Usage: python -m scripts.scale_as24 [discover_pages] [max_dealers]
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path

import asyncpg

from pipeline.geo import GeoResolver
from pipeline.ingest import ingest_dealer
from pipeline.recipe import write_recipe
from pipeline.sources.autoscout24 import collect_dealer_slugs, harvest_dealer

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
ROOT = Path(__file__).resolve().parent.parent


async def main(discover_pages: int, max_dealers: int) -> None:
    print(f"[scale] discovering dealers from {discover_pages} /lst pages...")
    dealers = collect_dealer_slugs(max_pages=discover_pages)
    slugs = list(dealers.keys())[:max_dealers]
    print(f"[scale] {len(dealers)} distinct dealers found; harvesting {len(slugs)}")

    conn = await asyncpg.connect(DSN)
    totals = {"dealers": 0, "vehicles": 0, "trustworthy": 0, "refuted": 0, "empty": 0, "errors": 0}
    try:
        geo = await GeoResolver.load(conn)
        for i, slug in enumerate(slugs, 1):
            try:
                harvest = harvest_dealer(slug)
                if not harvest.dealer or not harvest.vehicles:
                    totals["empty"] += 1
                    print(f"  [{i}/{len(slugs)}] {slug}: empty/no-dealer")
                    time.sleep(0.5)
                    continue
                result = await ingest_dealer(conn, geo, harvest, source_key="as24")
                if result.get("error"):
                    totals["errors"] += 1
                    print(f"  [{i}/{len(slugs)}] {slug}: {result['error']}")
                    continue
                write_recipe(result["cdp_code"])
                totals["dealers"] += 1
                totals["vehicles"] += result["available"]
                totals["trustworthy" if result["verdict"] == "TRUSTWORTHY" else "refuted"] += 1
                print(f"  [{i}/{len(slugs)}] {result['cdp_code']} {harvest.dealer.company_name}: "
                      f"{result['available']} cars, new={result['new']} {result['verdict']}")
            except Exception as e:  # noqa: BLE001 — one dealer failing must not stop the sweep
                totals["errors"] += 1
                print(f"  [{i}/{len(slugs)}] {slug}: EXCEPTION {type(e).__name__}: {e}")
            time.sleep(0.5)

        served = await conn.fetchval("SELECT count(*) FROM vehicle WHERE status='available'")
        ents = await conn.fetchval("SELECT count(*) FROM entity")
        print(f"\n[scale] done. dealers_ingested={totals['dealers']} vehicles_added={totals['vehicles']} "
              f"trustworthy={totals['trustworthy']} refuted={totals['refuted']} "
              f"empty={totals['empty']} errors={totals['errors']}")
        print(f"[scale] GLOBAL now: entities={ents} vehicles_available={served}")
    finally:
        await conn.close()


if __name__ == "__main__":
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    asyncio.run(main(pages, cap))
