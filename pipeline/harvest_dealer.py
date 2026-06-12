"""Per-dealer E2E orchestrator: SCRAPEAR -> RECETA -> INGEST -> VERIFICAR.

Chains the inventory phases for one AutoScout24 dealer slug. Raw harvest is
dumped to data/ (gitignored, ephemeral); the recipe is committed; inventory +
delta land in PostgreSQL with a VAM verdict.

Usage: python -m pipeline.harvest_dealer <as24_dealer_slug>
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

import asyncpg

from pipeline.geo import GeoResolver
from pipeline.ingest import ingest_dealer
from pipeline.recipe import write_recipe
from pipeline.sources.autoscout24 import harvest_dealer as scrape_dealer

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
ROOT = Path(__file__).resolve().parent.parent


async def run(slug: str) -> None:
    # FASE 2 — SCRAPEAR (drain all pages)
    harvest = scrape_dealer(slug)
    print(f"[scrape] dealer={harvest.dealer.company_name if harvest.dealer else None} "
          f"declared={harvest.declared_count} harvested={len(harvest.vehicles)} "
          f"pages={harvest.pages_drained}")
    if not harvest.dealer:
        print("no dealer parsed; abort"); return

    # raw dump (ephemeral, gitignored)
    raw_dir = ROOT / "data" / "ES" / slug / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "harvest.json").write_text(
        json.dumps([v.__dict__ for v in harvest.vehicles], ensure_ascii=False, indent=1),
        encoding="utf-8")

    conn = await asyncpg.connect(DSN)
    try:
        geo = await GeoResolver.load(conn)
        # FASE 4 — INGEST + delta + VAM
        result = await ingest_dealer(conn, geo, harvest, source_key="as24")
        if result.get("error"):
            print(f"[ingest] error: {result['error']}"); return
        # FASE 3 — RECETA (persist versioned recipe for this dealer)
        recipe_path = write_recipe(result["cdp_code"])
        print(f"[recipe] {recipe_path.relative_to(ROOT)}")
        print(f"[ingest] cdp={result['cdp_code']} available={result['available']} "
              f"declared={result['declared']} new={result['new']} gone={result['gone']} "
              f"price_change={result['price_change']} photo_change={result['photo_change']} "
              f"km_change={result['km_change']} unchanged={result['unchanged']}")
        print(f"[verify] VAM verdict: {result['verdict']}")
    finally:
        await conn.close()


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python -m pipeline.harvest_dealer <as24_dealer_slug>")
        sys.exit(2)
    asyncio.run(run(sys.argv[1]))


if __name__ == "__main__":
    main()
