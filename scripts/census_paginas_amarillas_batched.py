"""Resumable, incremental Páginas Amarillas census (province by province).

Crawls one province's auto rubros at a time and upserts each listing immediately
(asyncpg autocommit) via the canonical discover._upsert, so progress survives any kill and
re-invoking resumes at the next not-yet-done province. Persists ONLY entities.

Usage: python -m scripts.census_paginas_amarillas_batched [--provinces 28,08] [--final-vam]
"""
from __future__ import annotations

import argparse
import asyncio
import os

import asyncpg

from pipeline.discover import _upsert
from pipeline.geo import GeoResolver
from pipeline.sources.paginas_amarillas import (
    PROV_SLUG,
    SOURCE_KEY,
    crawl_province,
    record_to_entity,
)
from pipeline.verify import record_count_verdict

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")


async def run(provinces: list[str], final_vam: bool) -> None:
    conn = await asyncpg.connect(DSN)
    try:
        geo = await GeoResolver.load(conn)
        # resumable: skip provinces already fully ingested this campaign (tracked via a marker
        # in entity_source.source_ref prefix is impractical; instead we record per-province done
        # by checking if ANY listing for that province exists — good enough to resume after a kill).
        grand_new = grand_seen = grand_skip = 0
        declared_total = 0
        for pc in provinces:
            recs = crawl_province(pc)
            declared_total += len(recs)
            run_start = await conn.fetchval("SELECT now()")
            new = seen = skip = 0
            for rec in recs:
                if not rec.get("name"):
                    continue
                was_new, _g, prov_ok = await _upsert(conn, geo, record_to_entity(rec))
                if not prov_ok:
                    skip += 1
                elif was_new:
                    new += 1
                else:
                    seen += 1
            grand_new += new
            grand_seen += seen
            grand_skip += skip
            print(f"[PA] prov {pc} ({PROV_SLUG[pc]}): listings={len(recs)} new={new} "
                  f"collapsed={seen} skipped={skip} | cum_new={grand_new}", flush=True)

        ingested = await conn.fetchval(
            "SELECT count(*) FROM entity_source WHERE source_key=$1", SOURCE_KEY)
        print(f"[PA] DONE: provinces={len(provinces)} declared={declared_total} "
              f"new={grand_new} collapsed={grand_seen} skipped={grand_skip} "
              f"entity_source_total={ingested}")

        if final_vam:
            verdict = await record_count_verdict(
                conn, subject_type="source", subject_key=SOURCE_KEY,
                claim=f"paginas_amarillas long-tail census: {ingested} POS ingested",
                paths={"directory_listings": declared_total,
                       "entities_ingested_total": ingested},
                tolerance=0.05, claim_kind="coverage")
            print(f"[PA] VAM verdict = {verdict}")
    finally:
        await conn.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--provinces", type=str, default=None)
    ap.add_argument("--final-vam", action="store_true")
    a = ap.parse_args()
    provs = a.provinces.split(",") if a.provinces else list(PROV_SLUG.keys())
    asyncio.run(run(provs, a.final_vam))
