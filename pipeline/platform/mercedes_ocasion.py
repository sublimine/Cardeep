"""Mercedes-Benz Certified used-car (ocasion.mercedes-benz.es) — €0 connector.

The national used-car stock is shipped as a single JS cache document:

    GET https://ocasion.mercedes-benz.es/jscache?language=es-ES&type=vehiclelist&area=1

which embeds three JS consts:
  - fispor.DEFAULT = column order (positional field codes) for each vehicle row
  - fofisp.DEFAULT = per-field decode maps (brandi: meb->Mercedes-Benz, modtyp: code->model,
                     seller: code->dealer name)
  - dbveda        = array of positional rows (one per car; ~4817 nationwide)

ONE GET = the whole country. We zip fispor onto each row, decode make/model/dealer via fofisp,
read year/km/price positionally, and cage per dealer (seller code). GET-only, no auth, €0.
Verified live 2026-06-22. Parser is pure (the JS text in, vehicles out) and unit-tested offline.
"""
from __future__ import annotations

import argparse
import asyncio
import json as _json
import os
import re
from collections import defaultdict

import asyncpg
from curl_cffi import requests as _cffi

from pipeline.ids import ulid
from pipeline.platform._core.sql import (
    BULK_INSERT_EVENTS,
    BULK_INSERT_VEHICLES,
    BULK_TOUCH_VEHICLES,
)
from services.api.codes import cdp_code

MB_SOURCE_KEY = "mercedes_ocasion"
DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
_URL = "https://ocasion.mercedes-benz.es/jscache?language=es-ES&type=vehiclelist&area=1"
_DETAIL = "https://ocasion.mercedes-benz.es/es/coche-ocasion/{ordnbr}"
_IMPERSONATE = "chrome131"
_TIMEOUT = 40


# --- pure parser (unit-tested offline) --------------------------------------------------------
def _grab(js: str, pat: str) -> str | None:
    m = re.search(pat, js, re.S)
    return m.group(1) if m else None


def _decode_map(fofisp: dict, field: str) -> dict:
    """code -> label map for a field (fofisp.DEFAULT[field].val), or {}."""
    d = (fofisp.get("DEFAULT") or {}).get(field) or {}
    val = d.get("val")
    return val if isinstance(val, dict) else {}


def parse_mercedes_jscache(js: str) -> list[dict]:
    """Vehicles from the jscache JS document (fispor columns + fofisp maps + dbveda rows)."""
    # fispor = {"DEFAULT":[...flat string array...]} -> first '}' closes it (no braces inside).
    fispor = _grab(js, r'fispor\s*=\s*(\{.*?\})\s*;')
    # dbveda = [[...],[...]] -> ends at the only '];' (rows are joined by '],['; ';' only at end).
    dbveda = _grab(js, r'dbveda\s*=\s*(\[.*?\])\s*;')
    # fofisp = {"DEFAULT":{...nested...}} -> anchor on the trailing '; <decl> fofili' to grab it whole.
    fofisp = _grab(js, r'fofisp\s*=\s*(\{.*?\})\s*;\s*(?:const|var|let)?\s*fofili')
    if not (fispor and dbveda):
        return []
    try:
        cols = _json.loads(fispor)["DEFAULT"]
        rows = _json.loads(dbveda)
        fof = _json.loads(fofisp) if fofisp else {"DEFAULT": {}}
    except Exception:  # noqa: BLE001
        return []
    idx = {c: i for i, c in enumerate(cols)}
    brandi_m = _decode_map(fof, "brandi")
    modtyp_m = _decode_map(fof, "modtyp")
    seller_m = _decode_map(fof, "seller")

    def cell(row, field):
        i = idx.get(field)
        return row[i] if i is not None and i < len(row) else None

    out = []
    for row in rows:
        if not isinstance(row, list):
            continue
        ordnbr = cell(row, "ordnbr")
        make_c = cell(row, "brandi")
        model_c = cell(row, "modtyp")
        seller_c = cell(row, "seller")
        make = brandi_m.get(str(make_c), make_c)
        model = modtyp_m.get(str(model_c), model_c)
        seller = seller_m.get(str(seller_c), None)
        year = cell(row, "modyer")
        km = cell(row, "mileag")
        price = cell(row, "ofprgr")
        if make is None and model is None:
            continue
        # ordnbr (tail of the row) is empty in this feed; fall back to a STABLE content key as the
        # dedup deep_link (seller+make+model+year+km+price ~ one physical car). Real ordnbr if present.
        if ordnbr not in (None, "", 0, "0", 0.0):
            deep = _DETAIL.format(ordnbr=ordnbr)
            ref = str(ordnbr)
        else:
            slug = re.sub(r"[^a-z0-9]+", "-",
                          f"{seller_c}-{make}-{model}-{year}-{km}-{price}".lower()).strip("-")
            deep = "https://ocasion.mercedes-benz.es/es/coche-ocasion/" + slug
            ref = None
        out.append({
            "url": deep,
            "make": str(make) if make is not None else None,
            "model": str(model) if model is not None else None,
            "year": int(year) if isinstance(year, (int, float)) else None,
            "km": int(km) if isinstance(km, (int, float)) else None,
            "price": float(price) if isinstance(price, (int, float)) and price else None,
            "ref": ref,
            "fuel": None,
            "title": " ".join(x for x in (str(make) if make else "", str(model) if model else "") if x) or None,
            "photo_url": None,
            "seller_code": str(seller_c) if seller_c is not None else "unknown",
            "dealer_name": seller or (f"mercedes-seller-{seller_c}"),
        })
    return out


# --- live cage (validated in vivo) ------------------------------------------------------------
async def _upsert_mb_dealer(conn, seller_code: str, name: str | None) -> str:
    code = cdp_code(province_code="00", domain=f"seller{seller_code}.ocasion.mercedes-benz.es")
    tn = (name or f"mercedes-seller-{seller_code}").strip()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name, website,
               is_tier1, status, kind_source, sells_cars, first_discovered_source, last_seen)
           VALUES ($1,$2,'concesionario_oficial',$3,$3,$4,FALSE,'active','platform_label',TRUE,$5, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen=now()""",
        ulid(), code, tn, f"ocasion.mercedes-benz.es/seller/{seller_code}", MB_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at=now()",
        eulid, MB_SOURCE_KEY, str(seller_code))
    return eulid


async def _ingest_mb(conn, dealer_ulid: str, vehicles: list[dict], stats: dict) -> None:
    by_link = {}
    for v in vehicles:
        u = v.get("url")
        if u and u not in by_link:
            by_link[u] = v
    if not by_link:
        return
    links = list(by_link.keys())
    async with conn.transaction():
        existing = {r["deep_link"]: r["vehicle_ulid"] for r in await conn.fetch(
            "SELECT vehicle_ulid, deep_link FROM vehicle WHERE entity_ulid=$1 AND deep_link=ANY($2::text[])",
            dealer_ulid, links)}
        touch, new_links, vid_for = [], [], {}
        for l in links:
            ex = existing.get(l)
            if ex:
                vid_for[l] = ex
                touch.append(ex)
            else:
                vid_for[l] = ulid()
                new_links.append(l)
        if touch:
            await conn.execute(BULK_TOUCH_VEHICLES, touch)
        confirmed = []
        if new_links:
            def col(k):
                return [by_link[l].get(k) for l in new_links]
            n = len(new_links)
            await conn.execute(
                BULK_INSERT_VEHICLES,
                [vid_for[l] for l in new_links], [dealer_ulid] * n, new_links,
                col("title"), col("make"), col("model"), col("year"), col("km"), col("price"),
                col("fuel"), [None] * n, col("photo_url"), col("ref"))
            landed = {r["deep_link"]: r["vehicle_ulid"] for r in await conn.fetch(
                "SELECT vehicle_ulid, deep_link FROM vehicle WHERE vehicle_ulid=ANY($1::text[])",
                [vid_for[l] for l in new_links])}
            for l in new_links:
                if landed.get(l) == vid_for[l]:
                    confirmed.append(l)
        stats["cars"] += len(links)
        stats["new"] += len(confirmed)
        if confirmed:
            evp = [_json.dumps({"price": by_link[l].get("price"), "title": by_link[l].get("title"),
                                "source": MB_SOURCE_KEY}) for l in confirmed]
            await conn.execute(BULK_INSERT_EVENTS, [ulid() for _ in confirmed],
                               [vid_for[l] for l in confirmed], [dealer_ulid] * len(confirmed), evp)


async def _amain():
    async with _cffi.AsyncSession(impersonate=_IMPERSONATE, timeout=_TIMEOUT, allow_redirects=True) as s:
        r = await s.get(_URL)
        js = r.text if r.status_code == 200 else ""
    vehicles = parse_mercedes_jscache(js)
    print(f"[mercedes] parsed vehicles={len(vehicles)}")
    by_seller = defaultdict(list)
    for v in vehicles:
        by_seller[v["seller_code"]].append(v)
    pool = await asyncpg.create_pool(DSN, min_size=2, max_size=6)
    stats = {"cars": 0, "new": 0}
    dealers = 0
    try:
        for sc, vs in by_seller.items():
            async with pool.acquire() as conn:
                eulid = await _upsert_mb_dealer(conn, sc, vs[0].get("dealer_name"))
                await _ingest_mb(conn, eulid, vs, stats)
                dealers += 1
    finally:
        await pool.close()
    print("=" * 64)
    print(f"  mercedes: vehicles={len(vehicles)} dealers(seller)={dealers} caged={stats['cars']} new={stats['new']}")
    print("=" * 64)


def main() -> None:
    argparse.ArgumentParser(description="Mercedes-Benz ocasion €0 connector").parse_args()
    asyncio.run(_amain())


if __name__ == "__main__":
    main()
