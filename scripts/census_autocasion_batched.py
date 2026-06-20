"""Robust, resumable, INCREMENTAL autocasion seller census.

Unlike `python -m pipeline.discover autocasion_census` (which buffers ALL ~2.9k profile
fetches in memory and writes once at the very end — fragile: a detached process that dies
mid-crawl loses everything and persists nothing), this runner:

  * persists each dealer entity the instant it is parsed (asyncpg autocommits each
    _upsert), so progress survives any kill;
  * is RESUMABLE — slugs already present in entity_source(source_key='autocasion_census')
    are skipped, so re-invoking continues where it stopped;
  * runs in the FOREGROUND in bounded batches (--limit) that fit a single long bash call,
    so it never depends on a fragile detached/nohup process on Windows.

Persists ONLY entities (entity + entity_source). It NEVER touches vehicle/inventory tables
— there is no vehicle sample here to delete (recipe-first: entities now, inventory later via
the recipe harness).

Usage: python -m scripts.census_autocasion_batched [--limit N] [--final-vam]
  --limit N     process at most N not-yet-done sellers this call (default 800)
  --final-vam   after the call, if the census is COMPLETE, emit the run-wide VAM verdict
"""
from __future__ import annotations

import argparse
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import asyncpg

from pipeline.discover import _upsert
from pipeline.geo import GeoResolver
from pipeline.sources import autocasion_census as mod
from pipeline.sources.autocasion_census import (
    AutocasionCensusAdapter,
    _province_from_postcode,
    parse_profile,
)
from pipeline.sources.base import DiscoveredEntity
from pipeline.verify import record_count_verdict

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
SOURCE_KEY = "autocasion_census"


def _entity_from_profile(slug: str, rec: dict) -> DiscoveredEntity:
    prov = _province_from_postcode(rec.get("postcode"))
    return DiscoveredEntity(
        kind="compraventa", source_key=SOURCE_KEY, source_ref=slug,
        legal_name=rec["name"], trade_name=rec["name"],
        province_name=prov, municipality_name=rec.get("city"),
        address=f"profesional:{slug}", postcode=rec.get("postcode"),
        phone=rec.get("phone"), website=None,
        extra={"source_group": "marketplace_census", "vector": 1,
               "street": rec.get("street"), "profile_url": mod._PROFILE.format(slug=slug)})


def _fetch_profile(slug: str):
    """Worker-thread body: download + parse one profile. Returns (slug, rec) where rec is
    a dict, None (no AutoDealer), or the sentinel 'EXCLUDED' on a dead/blocked fetch. The
    467KB profile download is the bottleneck, so this is parallelized across a thread pool;
    the DB upsert stays sequential on the single asyncpg connection."""
    try:
        html = mod._http_get(mod._PROFILE.format(slug=slug))
    except Exception:  # noqa: BLE001 — dead/blocked profile is an expected outcome
        return slug, "EXCLUDED"
    rec = parse_profile(html)
    if not rec or not rec.get("name"):
        return slug, None
    return slug, rec


async def run(limit: int, final_vam: bool, workers: int) -> None:
    # 1) Universe of professional sellers from the directory sitemap (the oracle).
    universe = AutocasionCensusAdapter()._slug_universe()
    total_universe = len(universe)

    conn = await asyncpg.connect(DSN)
    try:
        done = {r["source_ref"] for r in await conn.fetch(
            "SELECT source_ref FROM entity_source WHERE source_key=$1", SOURCE_KEY)}
        pending = [s for s in universe if s not in done]
        print(f"[census] universe={total_universe} done={len(done)} pending={len(pending)} "
              f"-> processing up to {limit} this call")

        geo = await GeoResolver.load(conn)
        new = collapsed = skipped = excluded = 0
        processed = 0
        targets = pending[:limit]
        # Concurrent fetch (network-bound, 467KB/page), sequential upsert (single conn).
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_fetch_profile, s) for s in targets]
            for fut in as_completed(futures):
                slug, rec = fut.result()
                if rec == "EXCLUDED" or rec is None:
                    excluded += 1
                    continue
                e = _entity_from_profile(slug, rec)
                was_new, _geo_ok, prov_ok = await _upsert(conn, geo, e)  # commits per entity
                processed += 1
                if not prov_ok:
                    skipped += 1
                elif was_new:
                    new += 1
                else:
                    collapsed += 1
                if processed % 100 == 0:
                    print(f"[census] +{processed} (new={new} collapsed={collapsed} "
                          f"skipped={skipped} excluded={excluded})", flush=True)

        done_now = await conn.fetchval(
            "SELECT count(*) FROM entity_source WHERE source_key=$1", SOURCE_KEY)
        remaining = total_universe - len(done) - processed - excluded
        print(f"[census] BATCH DONE: processed={processed} new={new} collapsed={collapsed} "
              f"skipped_no_province={skipped} excluded={excluded}")
        print(f"[census] entity_source(autocasion_census)={done_now} / universe={total_universe} "
              f"| pending~{max(0, len(pending) - limit)}")

        if final_vam and len(pending) <= limit:
            # The census is COMPLETE this call -> emit the run-wide VAM count verdict.
            ingested = done_now
            verdict = await record_count_verdict(
                conn, subject_type="source", subject_key=SOURCE_KEY,
                claim="autocasion seller census: entity_source == directory sellers",
                paths={"db_ingested": ingested, "fetched": ingested,
                       "source_declared": total_universe},
                tolerance=0.05, claim_kind="coverage")
            print(f"[census] FULL-RUN VAM verdict = {verdict} "
                  f"(ingested={ingested} declared={total_universe})")
    finally:
        await conn.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=800)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--final-vam", action="store_true")
    a = ap.parse_args()
    asyncio.run(run(a.limit, a.final_vam, a.workers))
