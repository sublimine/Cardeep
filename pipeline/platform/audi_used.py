"""Audi OneAudi / VTP used cars (scs.audi.de SCS backend) — €0 API connector.

Spanish Audi used inventory is served by the SCS national backend (public static Token, no login):

    GET https://scs.audi.de/api/v2/search/filter/esuc/es?from={offset}&size={n}
        header: Token: FJ54W6H        (do NOT send a sort param -> 400)

$.vehicleBasic[*] = cars; $.totalCount = total. Paginate from/size up to totalCount; each car
carries its dealer (dealer.dealerContextLinkData[0].dealerId / groupName / city). Price is in
typedPrices (type 'retail' = selling price); km is not exposed in this feed (null). entryUrl is the
real per-car detail link. Verified live 2026-06-22: totalCount=4082.
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

AU_SOURCE_KEY = "audi_used"
DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
_URL = "https://scs.audi.de/api/v2/search/filter/esuc/es?from={frm}&size={size}"
_HEADERS = {"Token": "FJ54W6H", "Accept": "application/json", "Referer": "https://www.audi.es/"}
_PAGE = 100
_IMPERSONATE = "chrome131"
_TIMEOUT = 40
_PAGE_DELAY = 0.25


# --- pure parser (unit-tested offline) --------------------------------------------------------
def _price(typed_prices) -> float | None:
    if not isinstance(typed_prices, list):
        return None
    by = {p.get("type"): p.get("amount") for p in typed_prices if isinstance(p, dict)}
    for t in ("retail", "sales", "offer", "regular"):
        if isinstance(by.get(t), (int, float)) and by[t]:
            return float(by[t])
    for p in typed_prices:
        if isinstance(p, dict) and isinstance(p.get("amount"), (int, float)) and p["amount"]:
            return float(p["amount"])
    return None


def vehicle_from_audi(car: dict) -> dict | None:
    cid = car.get("carId") or car.get("id")
    if not cid:
        return None
    model = (car.get("model") or {}).get("description")
    year = car.get("modelYear")
    try:
        year = int(year) if year is not None else None
    except (TypeError, ValueError):
        year = None
    dealer = car.get("dealer") or {}
    dcl = (dealer.get("dealerContextLinkData") or [{}])
    dcl0 = dcl[0] if dcl else {}
    return {
        "url": car.get("entryUrl") or f"https://www.audi.es/es/web/es/usados.html#{cid}",
        "make": "Audi",
        "model": model,
        "year": year,
        "km": None,                                  # not exposed in the SCS list feed
        "price": _price(car.get("typedPrices")),
        "ref": str(cid),
        "fuel": (car.get("fuel") or {}).get("description") if isinstance(car.get("fuel"), dict) else None,
        "title": model or "Audi",
        "photo_url": None,
        "dealer_id": str(dcl0.get("dealerId") or dealer.get("rawDealerId") or "unknown"),
        "dealer_name": dcl0.get("groupName") or dcl0.get("originalGroupName"),
        "city": dealer.get("city"),
    }


def parse_audi(obj: dict) -> list[dict]:
    out = []
    for car in (obj.get("vehicleBasic") or []):
        if isinstance(car, dict):
            v = vehicle_from_audi(car)
            if v:
                out.append(v)
    return out


def total_count(obj: dict) -> int:
    return int(obj.get("totalCount") or 0)


# --- live drain + cage ------------------------------------------------------------------------
async def _drain_all(get, max_pages: int | None = None) -> list[dict]:
    first = await get(_URL.format(frm=0, size=_PAGE))
    if not first:
        return []
    j = _json.loads(first)
    total = total_count(j)
    pages = (total + _PAGE - 1) // _PAGE
    if max_pages:
        pages = min(pages, max_pages)
    vehicles = parse_audi(j)
    print(f"[audi] total={total} pages={pages}")
    for p in range(1, pages):
        b = await get(_URL.format(frm=p * _PAGE, size=_PAGE))
        if b:
            try:
                vehicles.extend(parse_audi(_json.loads(b)))
            except Exception:  # noqa: BLE001
                pass
        await asyncio.sleep(_PAGE_DELAY)
    return vehicles


async def _upsert_au_dealer(conn, did: str, name: str | None) -> str:
    code = cdp_code(province_code="00", domain=f"d{did}.audi.es")
    tn = (name or f"audi-{did}").strip()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name, website,
               is_tier1, status, kind_source, sells_cars, first_discovered_source, last_seen)
           VALUES ($1,$2,'concesionario_oficial',$3,$3,$4,FALSE,'active','platform_label',TRUE,$5, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen=now()""",
        ulid(), code, tn, f"audi.es/dealer/{did}", AU_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at=now()",
        eulid, AU_SOURCE_KEY, str(did))
    return eulid


async def _ingest_au(conn, dealer_ulid: str, vehicles: list[dict], stats: dict) -> None:
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
                                "source": AU_SOURCE_KEY}) for l in confirmed]
            await conn.execute(BULK_INSERT_EVENTS, [ulid() for _ in confirmed],
                               [vid_for[l] for l in confirmed], [dealer_ulid] * len(confirmed), evp)


async def _amain(max_pages):
    session = _cffi.AsyncSession(impersonate=_IMPERSONATE, timeout=_TIMEOUT,
                                 allow_redirects=True, headers=_HEADERS)

    async def get(url):
        try:
            r = await session.get(url)
        except Exception:  # noqa: BLE001
            return None
        return r.text if r.status_code == 200 else None
    try:
        vehicles = await _drain_all(get, max_pages)
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
                eulid = await _upsert_au_dealer(conn, did, vs[0].get("dealer_name"))
                await _ingest_au(conn, eulid, vs, stats)
                dealers += 1
    finally:
        await pool.close()
    print("=" * 64)
    print(f"  audi: vehicles={len(vehicles)} dealers={dealers} caged={stats['cars']} new={stats['new']}")
    print("=" * 64)


def main() -> None:
    p = argparse.ArgumentParser(description="Audi SCS used-car €0 connector")
    p.add_argument("--pages", type=int, default=None)
    a = p.parse_args()
    asyncio.run(_amain(a.pages))


if __name__ == "__main__":
    main()
