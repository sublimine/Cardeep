"""Nissan PACE used cars (gq-eu-prod.nissanpace.com GraphQL) — €0 API connector.

The Spanish Nissan used inventory is BRAND-WIDE (not per-dealer-site; the 191 red.nissan.es slugs
are dead 302->root). It is served by a Cognito-token-gated GraphQL API, but the token is PUBLIC
(no login):

  1) GET https://apigateway-eu-prod.nissanpace.com/euw1nisprod/public-access-token
        ?brand=NISSAN&dataSourceType=live&market=ES&client=euecomm   -> {idToken}
  2) POST https://gq-eu-prod.nissanpace.com/graphql   header Authorization: <idToken>
        op GetUsedCarsInventoryData, pageNumber 1..totalPages (15/page)

$.data.getUsedCarsInventoryData.vehicles[] carry their dealer{dealerId,dealerName}; group by
dealerId and cage per dealer. Verified live 2026-06-22: totalCount=1526, totalPages=102.
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

NI_SOURCE_KEY = "nissan_used"
DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
_TOKEN_URL = ("https://apigateway-eu-prod.nissanpace.com/euw1nisprod/public-access-token"
              "?brand=NISSAN&dataSourceType=live&market=ES&client=euecomm")
_GQL_URL = "https://gq-eu-prod.nissanpace.com/graphql"
_QUERY = (
    "query GetUsedCarsInventoryData($marketConfig: MarketConfig!, "
    "$usedCarsInventoryInputData: UsedCarsInventoryInputData!) {\n"
    " getUsedCarsInventoryData(marketConfig: $marketConfig, "
    "usedCarsInventoryInputData: $usedCarsInventoryInputData) {\n"
    "  vehicles { vin make modelName version mileage registrationYear registrationMonth "
    "fuelType rrpPrice discountedPrice vehiclesku dealer { dealerId dealerName } }\n"
    "  metaData { totalCount totalPages pageIndex hasMorePages }\n"
    " } }")
_IMPERSONATE = "chrome131"
_TIMEOUT = 40
_PAGE_DELAY = 0.2


def _variables(page: int) -> dict:
    return {
        "marketConfig": {"brand": "NISSAN", "country": "ES", "language": "es",
                         "metadata": {"clientApp": "[WEB]USEDCARS", "correlationId": ""}},
        "usedCarsInventoryInputData": {
            "usedCarsServletURL": "/content/nissan_prod/es_ES/index/cf-used-cars-ecom.model.json",
            "parentFilter": "queryFilters", "queryFilters": [{"type": "make", "values": ["Nissan"]}],
            "rangeFilters": [], "pageNumber": page, "dealerId": "", "vinListType": "used_cars",
            "includeCentralStock": False, "withDiscounts": False, "minLatestAchievementPoint": 40,
            "postalcode": "0", "sortingCriteria": {"type": "PRICE", "order": "ASC"}},
    }


# --- pure parser (unit-tested offline) --------------------------------------------------------
def _to_int(v):
    if isinstance(v, (int, float)):
        return int(v)
    if v is None:
        return None
    m = re.search(r"\d+", str(v))
    return int(m.group(0)) if m else None


def vehicle_from_nissan(v: dict) -> dict | None:
    sku = v.get("vehiclesku") or v.get("vin")
    if not sku:
        return None
    price = v.get("discountedPrice") or v.get("rrpPrice")
    dealer = v.get("dealer") or {}
    return {
        "url": f"https://ocasion.nissan.es/vehicle/{sku}",
        "make": (v.get("make") or "").title() or "Nissan",
        "model": v.get("modelName"),
        "year": _to_int(v.get("registrationYear")),
        "km": _to_int(v.get("mileage")),
        "price": float(price) if isinstance(price, (int, float)) and price else None,
        "ref": v.get("vin"),
        "fuel": v.get("fuelType"),
        "title": " ".join(x for x in (v.get("make"), v.get("modelName"), v.get("version")) if x) or None,
        "photo_url": None,
        "dealer_id": str(dealer.get("dealerId") or "unknown"),
        "dealer_name": dealer.get("dealerName"),
    }


def _block(obj: dict) -> dict:
    return ((obj.get("data") or {}).get("getUsedCarsInventoryData") or {})


def parse_nissan_page(obj: dict) -> list[dict]:
    out = []
    for v in (_block(obj).get("vehicles") or []):
        if isinstance(v, dict):
            n = vehicle_from_nissan(v)
            if n:
                out.append(n)
    return out


def total_pages(obj: dict) -> int:
    return int((_block(obj).get("metaData") or {}).get("totalPages") or 0)


# --- live drain + cage ------------------------------------------------------------------------
async def _drain_all(post, max_pages: int | None = None) -> list[dict]:
    first = await post(1)
    if not first:
        return []
    j = _json.loads(first)
    pages = total_pages(j)
    if max_pages:
        pages = min(pages, max_pages)
    vehicles = parse_nissan_page(j)
    print(f"[nissan] totalCount={(_block(j).get('metaData') or {}).get('totalCount')} pages={pages}")
    for p in range(2, pages + 1):
        b = await post(p)
        if b:
            try:
                vehicles.extend(parse_nissan_page(_json.loads(b)))
            except Exception:  # noqa: BLE001
                pass
        await asyncio.sleep(_PAGE_DELAY)
    return vehicles


async def _upsert_ni_dealer(conn, did: str, name: str | None) -> str:
    code = cdp_code(province_code="00", domain=f"d{did}.nissan.es")
    tn = (name or f"nissan-{did}").strip()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name, website,
               is_tier1, status, kind_source, sells_cars, first_discovered_source, last_seen)
           VALUES ($1,$2,'concesionario_oficial',$3,$3,$4,FALSE,'active','platform_label',TRUE,$5, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen=now()""",
        ulid(), code, tn, f"ocasion.nissan.es/dealer/{did}", NI_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at=now()",
        eulid, NI_SOURCE_KEY, str(did))
    return eulid


async def _ingest_ni(conn, dealer_ulid: str, vehicles: list[dict], stats: dict) -> None:
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
                                "source": NI_SOURCE_KEY}) for l in confirmed]
            await conn.execute(BULK_INSERT_EVENTS, [ulid() for _ in confirmed],
                               [vid_for[l] for l in confirmed], [dealer_ulid] * len(confirmed), evp)


async def _amain(max_pages):
    session = _cffi.AsyncSession(impersonate=_IMPERSONATE, timeout=_TIMEOUT, allow_redirects=True)
    try:
        tok = (await session.get(_TOKEN_URL)).json().get("idToken")
        if not tok:
            print("[nissan] no token; abort")
            return

        async def post(page):
            body = _json.dumps({"operationName": "GetUsedCarsInventoryData", "query": _QUERY,
                                "variables": _variables(page)})
            try:
                r = await session.post(_GQL_URL, data=body, headers={
                    "Authorization": tok, "Content-Type": "application/json",
                    "Origin": "https://ocasion.nissan.es", "Referer": "https://ocasion.nissan.es/"})
            except Exception:  # noqa: BLE001
                return None
            return r.text if r.status_code == 200 else None
        vehicles = await _drain_all(post, max_pages)
    finally:
        await session.close()
    by_dealer = defaultdict(list)
    for v in vehicles:
        by_dealer[v["dealer_id"]].append(v)
    pool = await asyncpg.create_pool(DSN, min_size=2, max_size=6)
    stats = {"cars": 0, "new": 0}
    dealers = 0
    try:
        for did, vs in by_dealer.items():
            async with pool.acquire() as conn:
                eulid = await _upsert_ni_dealer(conn, did, vs[0].get("dealer_name"))
                await _ingest_ni(conn, eulid, vs, stats)
                dealers += 1
    finally:
        await pool.close()
    print("=" * 64)
    print(f"  nissan: vehicles={len(vehicles)} dealers={dealers} caged={stats['cars']} new={stats['new']}")
    print("=" * 64)


def main() -> None:
    p = argparse.ArgumentParser(description="Nissan PACE used-car €0 connector")
    p.add_argument("--pages", type=int, default=None)
    a = p.parse_args()
    asyncio.run(_amain(a.pages))


if __name__ == "__main__":
    main()
