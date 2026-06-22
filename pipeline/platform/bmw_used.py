"""BMW Premium Selection / STOLO Stock Locator — €0 API connector.

Spanish BMW used inventory is served by the STOLO data service (public x-api-key, no login):

    POST https://stolo-data-service.prod.stolo.eu-central-1.aws.bmw.cloud/vehiclesearch/search/
         es-es/coches-segunda-mano?country=ES&category=BM&clientid=66_STOCK_DLO
         &maxResults={<=12}&startIndex={0..}
    header x-api-key: 7f66...ec98 ; body {}

$.metadata.totalCount + $.hits[*].vehicle. The real used price is offering.offerPrices[{buno}]
.offerGrossPrice (NOT price.grossSalesPrice, which is the configured list price). Each car's dealer
is ordering.distributionData.destinationLocationDomesticDealerName/Buno. Verified live 2026-06-22:
totalCount=3331. Flat paging may cap (~1212); we sweep startIndex and stop on empty/cap.
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

BMW_SOURCE_KEY = "bmw_used"
DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
_URL = ("https://stolo-data-service.prod.stolo.eu-central-1.aws.bmw.cloud/vehiclesearch/search/"
        "es-es/coches-segunda-mano?country=ES&category=BM&clientid=66_STOCK_DLO"
        "&maxResults={n}&startIndex={start}")
_HEADERS = {"x-api-key": "7f665f5b3cb8fe8e83293052367c575f666078b87570d5557f02f248ec98",
            "Content-Type": "application/json", "Accept": "application/json",
            "Origin": "https://www.bmw.es", "Referer": "https://www.bmw.es/"}
_PAGE = 12
_IMPERSONATE = "chrome131"
_TIMEOUT = 40
_PAGE_DELAY = 0.2


# --- pure parser (unit-tested offline) --------------------------------------------------------
def _price(v: dict) -> float | None:
    """Used asking price = offering.offerPrices[<car dealer buno>].offerGrossPrice (fallback first)."""
    op = (v.get("offering") or {}).get("offerPrices") or {}
    buno = ((v.get("ordering") or {}).get("distributionData") or {}).get("destinationLocationDomesticDealerBuno")
    if buno is not None and str(buno) in op:
        gp = op[str(buno)].get("offerGrossPrice")
        if gp:
            return float(gp)
    for d in op.values():
        if isinstance(d, dict) and d.get("offerGrossPrice"):
            return float(d["offerGrossPrice"])
    return None


def vehicle_from_bmw(hit: dict) -> dict | None:
    v = hit.get("vehicle") if isinstance(hit, dict) else None
    if not isinstance(v, dict):
        return None
    vid = v.get("vssId") or v.get("documentId")
    if not vid:
        return None
    spec = ((v.get("vehicleSpecification") or {}).get("modelAndOption") or {})
    dist = ((v.get("ordering") or {}).get("distributionData") or {})
    prod = ((v.get("ordering") or {}).get("productionData") or {})
    year = str(prod.get("productionDate") or "")[:4] or None
    try:
        year = int(year) if year else None
    except (TypeError, ValueError):
        year = None
    model = (spec.get("model") or {}).get("modelName")
    make = spec.get("brand") or "BMW"
    km = (v.get("vehicleLifeCycle") or {}).get("mileage", {})
    km = km.get("km") if isinstance(km, dict) else None
    return {
        "url": f"https://www.bmw.es/es/coches-ocasion/vehicle/{vid}",
        "make": make,
        "model": model,
        "year": year,
        "km": int(km) if isinstance(km, (int, float)) else None,
        "price": _price(v),
        "ref": v.get("documentId"),
        "fuel": None,
        "title": " ".join(x for x in (make, model) if x) or None,
        "photo_url": None,
        "dealer_id": str(dist.get("destinationLocationDomesticDealerBuno")
                         or dist.get("destinationLocationDomesticDealerNumber") or "unknown"),
        "dealer_name": dist.get("destinationLocationDomesticDealerName"),
    }


def parse_bmw_page(obj: dict) -> list[dict]:
    out = []
    for h in (obj.get("hits") or []):
        v = vehicle_from_bmw(h)
        if v:
            out.append(v)
    return out


def total_count(obj: dict) -> int:
    return int((obj.get("metadata") or {}).get("totalCount") or 0)


# --- live drain + cage ------------------------------------------------------------------------
async def _drain_all(post, max_pages: int | None = None) -> list[dict]:
    first = await post(0)
    if not first:
        return []
    j = _json.loads(first)
    total = total_count(j)
    pages = (total + _PAGE - 1) // _PAGE
    if max_pages:
        pages = min(pages, max_pages)
    vehicles = parse_bmw_page(j)
    print(f"[bmw] totalCount={total} pages={pages}")
    consecutive_empty = 0
    for p in range(1, pages):
        page_v = []
        for attempt in range(2):                     # CDN throws transient 503/empty -> retry once
            b = await post(p * _PAGE)
            if b:
                try:
                    page_v = parse_bmw_page(_json.loads(b))
                except Exception:  # noqa: BLE001
                    page_v = []
            if page_v:
                break
            await asyncio.sleep(0.6)
        if not page_v:
            consecutive_empty += 1
            if consecutive_empty >= 4:               # real cap (not a transient) -> stop
                print(f"[bmw] {consecutive_empty} consecutive empty pages at startIndex={p * _PAGE}; stop")
                break
            continue
        consecutive_empty = 0
        vehicles.extend(page_v)
        await asyncio.sleep(_PAGE_DELAY)
    return vehicles


async def _upsert_bmw_dealer(conn, did: str, name: str | None) -> str:
    code = cdp_code(province_code="00", domain=f"d{did}.bmw.es")
    tn = (name or f"bmw-{did}").strip()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name, website,
               is_tier1, status, kind_source, sells_cars, first_discovered_source, last_seen)
           VALUES ($1,$2,'concesionario_oficial',$3,$3,$4,FALSE,'active','platform_label',TRUE,$5, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen=now()""",
        ulid(), code, tn, f"bmw.es/dealer/{did}", BMW_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at=now()",
        eulid, BMW_SOURCE_KEY, str(did))
    return eulid


async def _ingest_bmw(conn, dealer_ulid: str, vehicles: list[dict], stats: dict) -> None:
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
                                "source": BMW_SOURCE_KEY}) for l in confirmed]
            await conn.execute(BULK_INSERT_EVENTS, [ulid() for _ in confirmed],
                               [vid_for[l] for l in confirmed], [dealer_ulid] * len(confirmed), evp)


async def _amain(max_pages):
    session = _cffi.AsyncSession(impersonate=_IMPERSONATE, timeout=_TIMEOUT,
                                 allow_redirects=True, headers=_HEADERS)

    async def post(start):
        try:
            r = await session.post(_URL.format(n=_PAGE, start=start), data="{}")
        except Exception:  # noqa: BLE001
            return None
        return r.text if r.status_code in (200, 201) else None
    try:
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
                eulid = await _upsert_bmw_dealer(conn, did, vs[0].get("dealer_name"))
                await _ingest_bmw(conn, eulid, vs, stats)
                dealers += 1
    finally:
        await pool.close()
    print("=" * 64)
    print(f"  bmw: vehicles={len(vehicles)} dealers={dealers} caged={stats['cars']} new={stats['new']}")
    print("=" * 64)


def main() -> None:
    p = argparse.ArgumentParser(description="BMW STOLO used-car €0 connector")
    p.add_argument("--pages", type=int, default=None)
    a = p.parse_args()
    asyncio.run(_amain(a.pages))


if __name__ == "__main__":
    main()
