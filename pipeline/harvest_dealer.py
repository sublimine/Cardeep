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
from pipeline.paths import data_root
from pipeline.recipe import write_recipe
from pipeline.sources.autoscout24 import harvest_dealer as scrape_dealer

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
ROOT = Path(__file__).resolve().parent.parent


async def run(slug: str) -> None:
    # A failure anywhere here used to be invisible to monitoring (green-review P2/Q9): a scrape
    # exception crashed the process before the DB connection opened (no record, no alert), and an
    # ingest-level error was print-only. We now fire a dealer-specific alert on every failure path,
    # with the EXACT origin (source/phase/slug). We use fire_alert (per-dealer granularity), NOT
    # record_run — record_run is source-level for 'as24' and would falsely trip the whole-source
    # breaker / GONE sweep for a single bad dealer.
    from pipeline.ops.health import build_origin, fire_alert

    conn = await asyncpg.connect(DSN)
    try:
        # FASE 2 — SCRAPEAR (drain all pages). A scrape failure is an EXPECTED operational outcome
        # (dealer site down / blocked) — alert it and skip the dealer, do not crash silently.
        try:
            harvest = scrape_dealer(slug)
        except Exception as exc:  # noqa: BLE001
            await fire_alert(conn, build_origin("as24", "scrape", slug),
                             severity="error", message=f"as24 scrape failed for {slug!r}: {exc}")
            print(f"[scrape] FAILED {slug}: {exc}")
            return
        print(f"[scrape] dealer={harvest.dealer.company_name if harvest.dealer else None} "
              f"declared={harvest.declared_count} harvested={len(harvest.vehicles)} "
              f"pages={harvest.pages_drained}")
        if not harvest.dealer:
            await fire_alert(conn, build_origin("as24", "scrape", slug),
                             severity="warning", message=f"as24: no dealer parsed for {slug!r}")
            print("no dealer parsed; abort"); return

        # raw dump (ephemeral, gitignored). Country is passed explicitly (ES default):
        # at this point the cdp_code is not yet known (ingest runs below), and this
        # orchestrator is the ES AutoScout24 path. data_root('ES') == data/ES, identical
        # to the old literal; ROOT is threaded so the resolution honors this module's ROOT.
        raw_dir = data_root("ES", root=ROOT) / slug / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        (raw_dir / "harvest.json").write_text(
            json.dumps([v.__dict__ for v in harvest.vehicles], ensure_ascii=False, indent=1),
            encoding="utf-8")

        geo = await GeoResolver.load(conn)
        # FASE 4 — INGEST + delta + VAM
        result = await ingest_dealer(conn, geo, harvest, source_key="as24")
        if result.get("error"):
            await fire_alert(conn, build_origin("as24", "ingest", slug),
                             severity="warning",
                             message=f"as24 ingest error for {slug!r}: {result['error']}")
            print(f"[ingest] error: {result['error']}"); return
        # FASE 3 — RECETA (persist versioned recipe for this dealer)
        recipe_path = write_recipe(result["cdp_code"])
        print(f"[recipe] {recipe_path.relative_to(ROOT)}")
        print(f"[ingest] cdp={result['cdp_code']} available={result['available']} "
              f"declared={result['declared']} new={result['new']} gone={result['gone']} "
              f"price_change={result['price_change']} photo_change={result['photo_change']} "
              f"km_change={result['km_change']} unchanged={result['unchanged']}")
        print(f"[verify] VAM verdict: {result['verdict']}")
    except Exception as exc:  # noqa: BLE001 — UNEXPECTED error (a bug, not a known outcome): alert
        # it with the exact origin so it is visible, then RE-RAISE so it surfaces (never swallowed).
        await fire_alert(conn, build_origin("as24", "harvest", slug),
                         severity="error", message=f"as24 harvest_dealer crashed for {slug!r}: {exc}")
        print(f"[harvest_dealer] FAILED {slug}: {exc}")
        raise
    finally:
        await conn.close()


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python -m pipeline.harvest_dealer <as24_dealer_slug>")
        sys.exit(2)
    asyncio.run(run(sys.argv[1]))


if __name__ == "__main__":
    main()
