"""Live verification of the autocasion CENSUS adapter against the running DB.

Runs a bounded sample through the CANONICAL discover path (pipeline.discover._upsert +
record_count_verdict) — not a parallel re-implementation — and reports:
  * new entities minted vs collapsed-on-cdp (the dedup proof against wholesale),
  * geo-resolution coverage,
  * the VAM count verdict,
  * how many sampled dealers already existed by cdp_code (record-linkage at work).

Usage: python -m scripts.verify_autocasion_census [N]   (N = sample size, default 80)
"""
from __future__ import annotations

import asyncio
import os
import sys

import asyncpg

from pipeline.discover import _upsert
from pipeline.geo import GeoResolver
from pipeline.sources.autocasion_census import AutocasionCensusAdapter
from pipeline.verify import record_count_verdict

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")


async def run(n: int) -> None:
    adapter = AutocasionCensusAdapter(max_dealers=n, sleep_s=0.15)
    print(f"[census] fetching sitemap + {n} profiles…")
    entities = adapter.fetch()
    declared = adapter.declared_count()
    print(f"[census] declared(sitemap slice)={declared} fetched(parsed profiles)={len(entities)} "
          f"excluded={adapter.excluded_count}")

    conn = await asyncpg.connect(DSN)
    try:
        geo = await GeoResolver.load(conn)
        run_start = await conn.fetchval("SELECT now()")
        new = resolved = skipped = 0
        for e in entities:
            was_new, geo_ok, prov_ok = await _upsert(conn, geo, e)
            new += int(was_new)
            resolved += int(geo_ok)
            if not prov_ok:
                skipped += 1
        in_db = await conn.fetchval(
            "SELECT count(*) FROM entity_source WHERE source_key=$1 AND seen_at >= $2",
            adapter.source_key, run_start)
        collapsed = len(entities) - new - skipped
        print(f"[census] NEW entities minted = {new}")
        print(f"[census] COLLAPSED onto existing cdp (dedup) = {collapsed}")
        print(f"[census] skipped_no_province = {skipped}")
        print(f"[census] geo municipality_resolved = {resolved}/{len(entities)}")
        print(f"[census] entity_source rows this run = {in_db}")

        verdict = await record_count_verdict(
            conn, subject_type="source", subject_key=adapter.source_key,
            claim="entity count == declared count (sample)",
            paths={"db_ingested": in_db, "fetched": len(entities),
                   "source_declared": declared},
            tolerance=0.05)
        print(f"[census] VAM verdict = {verdict}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run(int(sys.argv[1]) if len(sys.argv) > 1 else 80))
