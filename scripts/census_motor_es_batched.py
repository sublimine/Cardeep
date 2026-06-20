"""Robust, resumable, concurrent motor.es seller census (mirrors census_autocasion_batched).

Enumerates the ~536 dealers from the motor.es /concesionarios/ directory (province in URL),
then concurrently fetches+parses each dealer page (city/phone for cdp dedup + clustering),
upserting each entity incrementally (asyncpg autocommit) so progress survives any kill and
re-invoking resumes. Persists ONLY entities — no vehicle/inventory rows (recipe-first).

Usage: python -m scripts.census_motor_es_batched [--limit N] [--workers W] [--final-vam]
"""
from __future__ import annotations

import argparse
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import asyncpg

from pipeline.discover import _upsert
from pipeline.geo import GeoResolver
from pipeline.sources.autocasion_census import _http_get
from pipeline.sources.motor_es_census import (
    _BASE,
    MotorEsCensusAdapter,
    parse_dealer_page,
)
from pipeline.verify import record_count_verdict

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
SOURCE_KEY = "motor_es_census"


def _fetch(ref: tuple[str, str]):
    prov_slug, slug = ref
    try:
        html = _http_get(f"{_BASE}/concesionarios/{prov_slug}/{slug}/")
    except Exception:  # noqa: BLE001
        return ref, "EXCLUDED"
    rec = parse_dealer_page(html)
    return ref, (rec or None)


async def run(limit: int, final_vam: bool, workers: int) -> None:
    adapter = MotorEsCensusAdapter()
    refs = list(adapter._crawl().keys())
    total_universe = len(refs)

    conn = await asyncpg.connect(DSN)
    try:
        done = {r["source_ref"] for r in await conn.fetch(
            "SELECT source_ref FROM entity_source WHERE source_key=$1", SOURCE_KEY)}
        pending = [r for r in refs if f"{r[0]}/{r[1]}" not in done]
        print(f"[motor.es] universe={total_universe} done={len(done)} pending={len(pending)} "
              f"-> processing up to {limit} this call")

        geo = await GeoResolver.load(conn)
        new = collapsed = skipped = excluded = processed = 0
        targets = pending[:limit]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_fetch, r) for r in targets]
            for fut in as_completed(futures):
                (prov_slug, slug), rec = fut.result()
                if rec == "EXCLUDED" or rec is None:
                    excluded += 1
                    continue
                e = adapter.entity_from(prov_slug, slug, rec)
                was_new, _g, prov_ok = await _upsert(conn, geo, e)
                processed += 1
                if not prov_ok:
                    skipped += 1
                elif was_new:
                    new += 1
                else:
                    collapsed += 1
                if processed % 100 == 0:
                    print(f"[motor.es] +{processed} (new={new} collapsed={collapsed} "
                          f"skipped={skipped} excluded={excluded})", flush=True)

        done_now = await conn.fetchval(
            "SELECT count(*) FROM entity_source WHERE source_key=$1", SOURCE_KEY)
        print(f"[motor.es] BATCH DONE: processed={processed} new={new} collapsed={collapsed} "
              f"skipped_no_province={skipped} excluded={excluded}")
        print(f"[motor.es] entity_source({SOURCE_KEY})={done_now} / universe={total_universe}")

        if final_vam and len(pending) <= limit:
            ingested = done_now
            gap = total_universe - ingested
            coverage = ingested / total_universe if total_universe else 0.0
            verdict = await record_count_verdict(
                conn, subject_type="source", subject_key=SOURCE_KEY,
                claim=(f"motor.es seller census coverage: {ingested}/{total_universe} "
                       f"directory sellers ingested ({coverage:.1%}); gap={gap}"),
                paths={"directory_declared": total_universe, "entities_ingested": ingested},
                tolerance=0.02, claim_kind="coverage")
            print(f"[motor.es] FULL-RUN VAM verdict = {verdict} "
                  f"(ingested={ingested} declared={total_universe} coverage={coverage:.1%} gap={gap})")
    finally:
        await conn.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=800)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--final-vam", action="store_true")
    a = ap.parse_args()
    asyncio.run(run(a.limit, a.final_vam, a.workers))
