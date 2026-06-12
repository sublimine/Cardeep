"""Parallel AutoScout24 harvest worker. Reads the discovered dealer set and
harvests its slice [offset::stride], ingesting entity+inventory+delta+VAM per
dealer. Run N copies concurrently with offset 0..N-1, stride N.

Usage: python -m scripts.as24_harvest_batch <offset> <stride> [dealers_json]
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
from pipeline.sources.autoscout24 import harvest_dealer

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
ROOT = Path(__file__).resolve().parent.parent


async def main(offset: int, stride: int, dealers_path: Path) -> None:
    dealers = json.loads(dealers_path.read_text(encoding="utf-8"))
    slugs = list(dealers.keys())[offset::stride]
    tag = f"w{offset}/{stride}"
    print(f"[{tag}] {len(slugs)} dealers in slice")
    conn = await asyncpg.connect(DSN)
    done = cars = ok = bad = 0
    try:
        geo = await GeoResolver.load(conn)
        for slug in slugs:
            try:
                h = harvest_dealer(slug)
                if not h.dealer or not h.vehicles:
                    bad += 1
                    time.sleep(0.6)
                    continue
                r = await ingest_dealer(conn, geo, h, source_key="as24")
                if r.get("error"):
                    bad += 1
                    continue
                write_recipe(r["cdp_code"])
                done += 1
                cars += r["available"]
                ok += int(r["verdict"] == "TRUSTWORTHY")
            except Exception as e:  # noqa: BLE001 — one dealer must not kill the worker
                bad += 1
                print(f"[{tag}] {slug}: {type(e).__name__}")
            time.sleep(0.6)
        print(f"[{tag}] DONE dealers={done} cars={cars} trustworthy={ok} failed={bad}")
    finally:
        await conn.close()


if __name__ == "__main__":
    off = int(sys.argv[1]); strd = int(sys.argv[2])
    path = Path(sys.argv[3]) if len(sys.argv) > 3 else ROOT / "data" / "as24_dealers.json"
    asyncio.run(main(off, strd, path))
