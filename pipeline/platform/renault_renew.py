"""Renault Renew (es.renew.auto) used-car commerce API — €0 connector.

The whole Spanish Renault-network used stock (multi-brand: trade-ins of RENAULT/DACIA + FORD/NISSAN/
etc. physically held at Renault dealers) is served by one public commerce API, no login:

    GET https://es.renew.auto/wired/commerce/v1/products
        ?locale=es-ES&channel=main&pageSize=50&page={0..}&q=productType==vehicle_uci

Response: {currentPage, pageSize, totalElements, totalPages, data:[...]}. Each car carries its selling
dealer in `dealer` (dealerId/name/address.postalCode) — so we group by dealer like Spoticar/BMW and
drain ALL of Spain without enumerating per-dealer slugs. The stable per-car id is `productId`
(VEH_<rrf>_<plate>); the platform exposes no per-car canonical URL so deep_link is a synthetic stable
key from productId. Verified live 2026-06-22: totalElements=5695. Parser is pure.
"""
from __future__ import annotations

import argparse
import asyncio
import json as _json
import math
import os

import asyncpg
from curl_cffi import requests as _cffi

from pipeline.ids import ulid
from pipeline.platform._core.sql import (
    BULK_INSERT_EVENTS,
    BULK_INSERT_VEHICLES,
    BULK_TOUCH_VEHICLES,
)
from services.api.codes import cdp_code

RENEW_SOURCE_KEY = "renault_renew"
DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
_URL = ("https://es.renew.auto/wired/commerce/v1/products?locale=es-ES&channel=main"
        "&pageSize={n}&page={page}&q=productType==vehicle_uci")
_PAGE = 50
_IMPERSONATE = "chrome131"
_TIMEOUT = 45
_PAGE_DELAY = 0.25
_MAX_PAGES = 400


# --- pure parser (unit-tested offline) --------------------------------------------------------
def renew_total(obj: dict) -> int:
    return int(obj.get("totalElements") or 0)


def _label(d):
    return (d or {}).get("label") if isinstance(d, dict) else None


def _photo(assets):
    for a in assets or []:
        if a.get("assetType") == "picture":
            for r in a.get("renditions") or []:
                if r.get("resolutionType") == "medium":
                    return r.get("url")
    return None


def vehicle_from_renew(p: dict) -> dict | None:
    if not isinstance(p, dict):
        return None
    pid = p.get("productId") or p.get("identifier")
    if not pid:
        return None
    dealer = p.get("dealer") or (p.get("dealers") or [{}])[0] or {}
    did = str(dealer.get("dealerId") or p.get("codeRRFSiteExposition") or "unknown")
    addr = dealer.get("address") or {}
    make = _label(p.get("brand"))
    model = _label(p.get("model")) or (p.get("model") or {}).get("groupLabel")
    version = _label(p.get("version"))
    prices = p.get("prices") or []
    price = None
    if prices and isinstance(prices[0], dict):
        price = prices[0].get("priceWithTaxes") or prices[0].get("customerDisplayPrice")
    year = p.get("modelYear")
    try:
        year = int(year) if year is not None else None
    except (TypeError, ValueError):
        year = None
    km = p.get("mileage") if (p.get("mileageUnit") or "KM").upper() == "KM" else None
    return {
        "url": f"https://es.renew.auto/vehiculo/{pid}",          # synthetic stable key (no per-car canonical URL)
        "make": make,
        "model": model,
        "year": year,
        "km": int(km) if isinstance(km, (int, float)) else None,
        "price": float(price) if isinstance(price, (int, float)) else None,
        "ref": str(pid),
        "fuel": _label(p.get("energy")),
        "title": " ".join(x for x in (make, model, version) if x) or None,
        "photo_url": _photo(p.get("assets")),
        "dealer_id": did,
        "dealer_name": (dealer.get("name") or "").strip() or None,
        "dealer_zip": (addr.get("postalCode") or "").strip() or None,
    }


def parse_renew_page(obj: dict) -> list[dict]:
    out = []
    for p in (obj.get("data") or []):
        v = vehicle_from_renew(p)
        if v:
            out.append(v)
    return out


# --- live drain + cage ------------------------------------------------------------------------
async def _drain_all(get, max_pages: int | None = None) -> list[dict]:
    first = await get(0)
    if not first:
        return []
    j = _json.loads(first)
    total = renew_total(j)
    pages = min(_MAX_PAGES, math.ceil(total / _PAGE)) if total else 1
    if max_pages:
        pages = min(pages, max_pages)
    print(f"[renew] totalElements={total} pages={pages}")
    by_id = {v["ref"]: v for v in parse_renew_page(j)}
    consecutive_empty = 0
    for p in range(1, pages):
        page_v = []
        for _ in range(2):                            # transient 5xx/empty -> retry once
            b = await get(p)
            if b:
                try:
                    page_v = parse_renew_page(_json.loads(b))
                except Exception:  # noqa: BLE001
                    page_v = []
            if page_v:
                break
            await asyncio.sleep(0.6)
        if not page_v:
            consecutive_empty += 1
            if consecutive_empty >= 4:
                print(f"[renew] {consecutive_empty} consecutive empty pages at page={p}; stop")
                break
            continue
        consecutive_empty = 0
        for v in page_v:
            by_id.setdefault(v["ref"], v)
        await asyncio.sleep(_PAGE_DELAY)
    return list(by_id.values())


async def _upsert_dealer(conn, did: str, name: str | None, zip_: str | None) -> str:
    safe = "".join(ch for ch in did if ch.isalnum()) or "unknown"
    code = cdp_code(province_code="00", domain=f"d{safe}.renew.auto")
    tn = (name or f"renew-{did}").strip()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name, website,
               is_tier1, status, kind_source, sells_cars, first_discovered_source, last_seen)
           VALUES ($1,$2,'concesionario_oficial',$3,$3,$4,FALSE,'active','platform_label',TRUE,$5, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen=now()""",
        ulid(), code, tn, f"es.renew.auto/dealer/{did}", RENEW_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at=now()",
        eulid, RENEW_SOURCE_KEY, str(did))
    return eulid


async def _ingest(conn, dealer_ulid: str, vehicles: list[dict], stats: dict) -> None:
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
                                "source": RENEW_SOURCE_KEY}) for l in confirmed]
            await conn.execute(BULK_INSERT_EVENTS, [ulid() for _ in confirmed],
                               [vid_for[l] for l in confirmed], [dealer_ulid] * len(confirmed), evp)


async def _amain(max_pages):
    session = _cffi.AsyncSession(impersonate=_IMPERSONATE, timeout=_TIMEOUT, allow_redirects=True,
                                 headers={"Accept": "application/json"})

    async def get(page):
        try:
            r = await session.get(_URL.format(n=_PAGE, page=page))
        except Exception:  # noqa: BLE001
            return None
        return r.text if r.status_code == 200 else None
    try:
        vehicles = await _drain_all(get, max_pages)
    finally:
        await session.close()
    by_dealer: dict[str, list[dict]] = {}
    for v in vehicles:
        by_dealer.setdefault(v["dealer_id"], []).append(v)
    pool = await asyncpg.create_pool(DSN, min_size=2, max_size=6)
    stats = {"cars": 0, "new": 0}
    dealers = 0
    try:
        for did, vs in by_dealer.items():
            async with pool.acquire() as conn:
                eulid = await _upsert_dealer(conn, did, vs[0].get("dealer_name"), vs[0].get("dealer_zip"))
                await _ingest(conn, eulid, vs, stats)
                dealers += 1
    finally:
        await pool.close()
    print("=" * 64)
    print(f"  renew: vehicles={len(vehicles)} dealers={dealers} caged={stats['cars']} new={stats['new']}")
    print("=" * 64)


def main() -> None:
    p = argparse.ArgumentParser(description="Renault Renew ES used-car €0 connector")
    p.add_argument("--pages", type=int, default=None)
    a = p.parse_args()
    asyncio.run(_amain(a.pages))


if __name__ == "__main__":
    main()
