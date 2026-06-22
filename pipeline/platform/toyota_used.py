"""Toyota Plus / Used-Stock-Cars (usc-webcomponents.toyota-europe.com) — €0 API connector.

Spanish Toyota used inventory is served by a public JSON API (no auth):

    POST https://usc-webcomponents.toyota-europe.com/v1/api/usedcars/results/es/es
         ?brand=toyota&uscEnv=production&sortOrder=published
    body: {"uscEnv":"production","filters":[],"filterContext":"used","offset":N,
           "resultCount":100,"sortOrder":"published","distributorCode":"94244",
           "includeActiveFilterAggregations":false}

Paginate by offset up to $.totalResultCount; each result carries its dealer (dealer.localId /
name / address.city). Group by dealer.localId and cage per dealer. Verified live 2026-06-22:
totalResultCount=3157, results[*].product.{brand,model,modelYear}, price.sellingPriceInclVAT.
"""
from __future__ import annotations

import argparse
import asyncio
import json as _json
import os
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

TY_SOURCE_KEY = "toyota_used"
DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
_URL = ("https://usc-webcomponents.toyota-europe.com/v1/api/usedcars/results/es/es"
        "?brand=toyota&uscEnv=production&sortOrder=published")
_HEADERS = {"Content-Type": "application/json", "Origin": "https://www.toyota.es",
            "Referer": "https://www.toyota.es/"}
_DISTRIBUTOR = "94244"
_PAGE = 100
_IMPERSONATE = "chrome131"
_TIMEOUT = 40
_PAGE_DELAY = 0.25


def _body(offset: int, count: int) -> str:
    return _json.dumps({"uscEnv": "production", "filters": [], "filterContext": "used",
                        "offset": offset, "resultCount": count, "sortOrder": "published",
                        "distributorCode": _DISTRIBUTOR, "includeActiveFilterAggregations": False})


# --- pure parser (unit-tested offline) --------------------------------------------------------
def vehicle_from_result(r: dict) -> dict | None:
    """Normalize one Toyota usedcars result into the canonical vehicle dict. None without id."""
    cid = r.get("id")
    if not cid:
        return None
    prod = r.get("product") or {}
    brand = (prod.get("brand") or {}).get("description")
    model = (prod.get("model") or {}).get("description")
    year = prod.get("modelYear") or (str(r.get("productionDate") or "")[:4] or None)
    try:
        year = int(year) if year else None
    except (TypeError, ValueError):
        year = None
    price = (r.get("price") or {}).get("sellingPriceInclVAT")
    dealer = r.get("dealer") or {}
    addr = dealer.get("address") or {}
    return {
        "url": f"https://www.toyota.es/coches-segunda-mano/vo/{cid}",
        "make": brand,
        "model": model,
        "year": year,
        "km": r.get("mileage") if isinstance(r.get("mileage"), (int, float)) else None,
        "price": float(price) if isinstance(price, (int, float)) and price else None,
        "ref": r.get("vin") or str(cid),
        "fuel": None,
        "title": " ".join(x for x in (brand, model) if x) or None,
        "photo_url": None,
        "dealer_local": str(dealer.get("localId") or "unknown"),
        "dealer_name": dealer.get("name") or None,
        "city": addr.get("city"),
    }


def parse_toyota_results(obj: dict) -> list[dict]:
    out = []
    for r in (obj.get("results") or []):
        if isinstance(r, dict):
            v = vehicle_from_result(r)
            if v:
                out.append(v)
    return out


def total_count(obj: dict) -> int:
    return int(obj.get("totalResultCount") or 0)


# --- live drain + cage ------------------------------------------------------------------------
async def _drain_all(post, max_pages: int | None = None) -> list[dict]:
    first = await post(_body(0, _PAGE))
    if not first:
        return []
    j = _json.loads(first)
    total = total_count(j)
    pages = (total + _PAGE - 1) // _PAGE
    if max_pages:
        pages = min(pages, max_pages)
    vehicles = parse_toyota_results(j)
    print(f"[toyota] total={total} pages={pages}")
    for p in range(1, pages):
        b = await post(_body(p * _PAGE, _PAGE))
        if b:
            try:
                vehicles.extend(parse_toyota_results(_json.loads(b)))
            except Exception:  # noqa: BLE001
                pass
        await asyncio.sleep(_PAGE_DELAY)
    return vehicles


async def _upsert_ty_dealer(conn, local: str, name: str | None) -> str:
    code = cdp_code(province_code="00", domain=f"d{local.replace('-', '')}.toyota.es")
    tn = (name or f"toyota-{local}").strip()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name, website,
               is_tier1, status, kind_source, sells_cars, first_discovered_source, last_seen)
           VALUES ($1,$2,'concesionario_oficial',$3,$3,$4,FALSE,'active','platform_label',TRUE,$5, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen=now()""",
        ulid(), code, tn, f"toyota.es/dealer/{local}", TY_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at=now()",
        eulid, TY_SOURCE_KEY, str(local))
    return eulid


async def _ingest_ty(conn, dealer_ulid: str, vehicles: list[dict], stats: dict) -> None:
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
                                "source": TY_SOURCE_KEY}) for l in confirmed]
            await conn.execute(BULK_INSERT_EVENTS, [ulid() for _ in confirmed],
                               [vid_for[l] for l in confirmed], [dealer_ulid] * len(confirmed), evp)


async def _amain(max_pages):
    session = _cffi.AsyncSession(impersonate=_IMPERSONATE, timeout=_TIMEOUT,
                                 allow_redirects=True, headers=_HEADERS)

    async def post(body):
        try:
            r = await session.post(_URL, data=body)
        except Exception:  # noqa: BLE001
            return None
        return r.text if r.status_code == 200 else None
    try:
        vehicles = await _drain_all(post, max_pages)
    finally:
        await session.close()
    by_dealer = defaultdict(list)
    for v in vehicles:
        by_dealer[v["dealer_local"]].append(v)
    pool = await asyncpg.create_pool(DSN, min_size=2, max_size=6)
    stats = {"cars": 0, "new": 0}
    dealers = 0
    try:
        for dl, vs in by_dealer.items():
            async with pool.acquire() as conn:
                eulid = await _upsert_ty_dealer(conn, dl, vs[0].get("dealer_name"))
                await _ingest_ty(conn, eulid, vs, stats)
                dealers += 1
    finally:
        await pool.close()
    print("=" * 64)
    print(f"  toyota: vehicles={len(vehicles)} dealers={dealers} caged={stats['cars']} new={stats['new']}")
    print("=" * 64)


def main() -> None:
    p = argparse.ArgumentParser(description="Toyota Plus used-car €0 connector")
    p.add_argument("--pages", type=int, default=None)
    a = p.parse_args()
    asyncio.run(_amain(a.pages))


if __name__ == "__main__":
    main()
