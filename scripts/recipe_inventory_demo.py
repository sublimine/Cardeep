"""Demonstrate the recipe-first inventory cycle over real discovered dealers' own websites.

Picks a varied sample of dealers that carry their OWN website (not a marketplace), and runs
the recipe harness on each: discover stock page -> extract k sample vehicles (JSON-LD) ->
persist the recipe -> VAM-verify -> DELETE the sample -> mark VERIFIED/FAILED. Reports how
many recipes end VERIFIED. Recipe-first: only a tiny sample is pulled and it is wiped; no
inventory is persisted.

Usage: python -m scripts.recipe_inventory_demo [N]
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timezone

import asyncpg

from pipeline.recipe_extract_web import GenericWebExtractor
from pipeline.recipe_harness import RecipeHarness

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# Curated varied targets are drawn live, but we bias toward real used-car shops and away from
# pure-OEM landing pages / non-car sites by requiring a car-ish kind and a bare-domain website.
# DISTINCT website (PA reuses placeholder hosts like beedigital across many listings) and
# exclude web-builder / social / placeholder hosts that are never a real dealer stock site.
_PICK = """
  SELECT DISTINCT ON (lower(website)) cdp_code, coalesce(legal_name,trade_name,'?') AS nm, website
  FROM entity
  WHERE website ~* '^https?://' AND kind IN ('compraventa','concesionario_oficial')
    AND website !~* '(paginasamarillas|wallapop|coches\\.net|autoscout|milanuncios|motor\\.es|autocasion|facebook|instagram|twitter|youtube|linkedin|beedigital|wixsite|\\.wix\\.|sites\\.google|blogspot|webnode|jimdo|godaddysites|negocio\\.site|micrositios)'
    AND website ~* '(coche|auto|motor|car|wagen|vehic|ocasion|coches|coches|cars|seminuevo|km0)'
  ORDER BY lower(website), random()
  LIMIT $1
"""


async def _rows_for_websites(conn, webs: list[str]):
    out = []
    for w in webs:
        r = await conn.fetchrow(
            "SELECT cdp_code, coalesce(legal_name,trade_name,'?') AS nm, website FROM entity "
            "WHERE lower(website) = lower($1) LIMIT 1", w)
        out.append(r or {"cdp_code": None, "nm": "?", "website": w})
    return out


async def run(n: int, websites: list[str] | None = None) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn = await asyncpg.connect(DSN)
    try:
        if websites:
            rows = await _rows_for_websites(conn, websites)
            n = len(rows)
        else:
            rows = await conn.fetch(_PICK, max(n * 3, n))  # over-fetch; many sites won't reach/parse
        extractor = GenericWebExtractor()
        harness = RecipeHarness(extractor, conn=conn, now_iso=now)
        verified = failed = 0
        results = []
        for r in rows:
            if verified + failed >= n:
                break
            web = r["website"].strip()
            try:
                res = await harness.run(web, k=5, cdp_code=r["cdp_code"] or f"web-{abs(hash(web))%10**8}")
            except Exception as exc:  # noqa: BLE001 — unreachable/blocked site is a FAILED recipe, not a crash
                failed += 1
                results.append((r["nm"], web, "FAILED", f"transport: {type(exc).__name__}", 0))
                print(f"  FAILED  {web[:48]:50} unreachable ({type(exc).__name__})", flush=True)
                continue
            if res.status == "VERIFIED":
                verified += 1
            else:
                failed += 1
            results.append((r["nm"], web, res.status, res.reason, res.parsed))
            print(f"  {res.status:8} {web[:48]:50} parsed={res.parsed} verdict={res.verdict} "
                  f":: {res.reason[:60]}", flush=True)

        print(f"\n[recipe-inventory] dealers attempted={verified+failed} "
              f"VERIFIED={verified} FAILED={failed}")
    finally:
        await conn.close()


if __name__ == "__main__":
    if "--websites" in sys.argv:
        webs = sys.argv[sys.argv.index("--websites") + 1].split(",")
        asyncio.run(run(len(webs), websites=webs))
    else:
        asyncio.run(run(int(sys.argv[1]) if len(sys.argv) > 1 else 8))
