"""Resumable, concurrent AutoScout24 seller census (mirrors the other census runners).

Enumerates dealer slugs from the open /lst surface, then concurrently fetches+parses each
dealer profile page and upserts incrementally (asyncpg autocommit) — progress survives any
kill, re-invoking resumes. Persists ONLY entities (recipe-first).

Usage: python -m scripts.census_autoscout24_batched [--pages N] [--workers W] [--final-vam]
"""
from __future__ import annotations

import argparse
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import asyncpg

from pipeline.discover import _upsert
from pipeline.geo import GeoResolver
from pipeline.sources.autoscout24_census import (
    SOURCE_KEY,
    AutoScout24CensusAdapter,
    dealer_entity,
)
from pipeline.verify import record_count_verdict

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")


def _fetch(slug: str):
    try:
        return slug, dealer_entity(slug)
    except Exception:  # noqa: BLE001
        return slug, "EXCLUDED"


async def run(pages: int, workers: int, final_vam: bool) -> None:
    adapter = AutoScout24CensusAdapter(max_pages_per_sort=pages)
    universe = adapter.slug_universe()
    print(f"[as24] enumerated {len(universe)} distinct dealer slugs", flush=True)

    conn = await asyncpg.connect(DSN)
    try:
        done = {r["source_ref"] for r in await conn.fetch(
            "SELECT source_ref FROM entity_source WHERE source_key=$1", SOURCE_KEY)}
        pending = [s for s in universe if s not in done]
        print(f"[as24] done={len(done)} pending={len(pending)}", flush=True)

        geo = await GeoResolver.load(conn)
        new = collapsed = skipped = excluded = processed = 0
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_fetch, s) for s in pending]
            for fut in as_completed(futures):
                slug, e = fut.result()
                if e == "EXCLUDED" or e is None:
                    excluded += 1
                    continue
                was_new, _g, prov_ok = await _upsert(conn, geo, e)
                processed += 1
                if not prov_ok:
                    skipped += 1
                elif was_new:
                    new += 1
                else:
                    collapsed += 1
                if processed % 100 == 0:
                    print(f"[as24] +{processed} (new={new} collapsed={collapsed} "
                          f"skipped={skipped} excluded={excluded})", flush=True)

        ingested = await conn.fetchval(
            "SELECT count(*) FROM entity_source WHERE source_key=$1", SOURCE_KEY)
        print(f"[as24] DONE: processed={processed} new={new} collapsed={collapsed} "
              f"skipped={skipped} excluded={excluded} entity_source_total={ingested}")

        if final_vam:
            verdict = await record_count_verdict(
                conn, subject_type="source", subject_key=SOURCE_KEY,
                claim=f"autoscout24 seller census: {ingested} dealers ingested",
                paths={"slugs_enumerated": len(universe), "entities_ingested_total": ingested},
                tolerance=0.05, claim_kind="coverage")
            print(f"[as24] VAM verdict = {verdict}")
    finally:
        await conn.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=20)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--final-vam", action="store_true")
    a = ap.parse_args()
    asyncio.run(run(a.pages, a.workers, a.final_vam))
