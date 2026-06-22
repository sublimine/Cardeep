"""Hyundai ES seminuevos (per-dealer OpenCart SSR) — €0 connector.

Each Hyundai dealer's full used stock renders server-side in ONE page (pagination ignored):

    GET https://www.hyundai.es/concesionarios/{slug}/seminuevos

Cars are <div class="ucar-container__item"> cards: title in .ucar__info__title, price in
.ucar__info__price__num, km/year in .ucar__info__list__item, images under S3 .../stock/{CODE}/.
The detalle href carries a per-RENDER vid token (NOT stable) — so the stable per-car id is the S3
stock CODE (e.g. 5192LYW), used as deep_link. Verified live 2026-06-22. Parser is pure.
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

HY_SOURCE_KEY = "hyundai_used"
DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
_IMPERSONATE = "chrome131"
_TIMEOUT = 30
_DEALER_DELAY = 0.3


# --- pure parser (unit-tested offline) --------------------------------------------------------
def _to_int(s):
    m = re.search(r"\d[\d.]*", str(s or ""))
    return int(m.group(0).replace(".", "")) if m else None


def _to_float(s):
    m = re.search(r"\d[\d.]*", str(s or ""))
    return float(m.group(0).replace(".", "")) if m else None


def parse_hyundai_cards(html: str) -> list[dict]:
    """Vehicles from one dealer /seminuevos SSR page. Keyed by the stable S3 stock code."""
    out, seen = [], set()
    blocks = html.split("ucar-container__item")[1:]
    for b in blocks:
        b = b[:6000]
        stock = re.search(r"/stock/([A-Za-z0-9]+)/", b)
        if not stock:
            continue
        code = stock.group(1)
        if code in seen:
            continue
        seen.add(code)
        cid = re.search(r"concesionario_id=(\d+)", b)
        title = re.search(r'ucar__info__title[^>]*>([^<]+)<', b)
        title = title.group(1).strip() if title else None
        price = re.search(r'ucar__info__price__num[^>]*>([\d.\s]+)<', b)
        items = [re.sub(r"<[^>]+>", "", x).strip()
                 for x in re.findall(r'ucar__info__list__item[^>]*>(.*?)</li>', b, re.S)]
        km = year = None
        for it in items:
            mk = re.search(r"([\d.]+)\s*km", it, re.I)
            if mk and km is None:
                km = _to_int(mk.group(1))
            my = re.search(r"\b(19[89]\d|20[0-2]\d)\b", it)
            if my and year is None:
                year = int(my.group(0))
        out.append({
            "url": f"https://www.hyundai.es/seminuevos/{code}",
            "make": None,                                # card title is the model; brand not asserted
            "model": title,
            "year": year,
            "km": km,
            "price": _to_float(price.group(1)) if price else None,
            "ref": code,
            "fuel": None,
            "title": title,
            "photo_url": None,
            "concesionario_id": cid.group(1) if cid else None,
        })
    return out


# --- live drain + cage ------------------------------------------------------------------------
def _slug(website: str) -> str | None:
    m = re.search(r"concesionarios/([^/?#]+)", website or "")
    return m.group(1) if m else None


async def _resolve_or_mint(conn, slug: str) -> str:
    row = await conn.fetchrow(
        "SELECT entity_ulid FROM entity WHERE website ILIKE $1 ORDER BY last_seen DESC LIMIT 1",
        f"%concesionarios/{slug}%")
    if row:
        eulid = row["entity_ulid"]
    else:
        code = cdp_code(province_code="00", domain=f"{slug}.concesionarios.hyundai.es")
        await conn.execute(
            """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name, website,
                   is_tier1, status, kind_source, sells_cars, first_discovered_source, last_seen)
               VALUES ($1,$2,'concesionario_oficial',$3,$3,$4,FALSE,'active','platform_label',TRUE,$5, now())
               ON CONFLICT (cdp_code) DO UPDATE SET last_seen=now()""",
            ulid(), code, slug, f"hyundai.es/concesionarios/{slug}", HY_SOURCE_KEY)
        eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at=now()",
        eulid, HY_SOURCE_KEY, slug)
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
                                "source": HY_SOURCE_KEY}) for l in confirmed]
            await conn.execute(BULK_INSERT_EVENTS, [ulid() for _ in confirmed],
                               [vid_for[l] for l in confirmed], [dealer_ulid] * len(confirmed), evp)


async def _amain(limit):
    conn0 = await asyncpg.connect(DSN)
    rows = await conn0.fetch(
        "SELECT DISTINCT website FROM entity WHERE website ILIKE '%hyundai.es/concesionarios/%'")
    await conn0.close()
    slugs = sorted({s for s in (_slug(r["website"]) for r in rows) if s and s != "index.php"})
    if limit:
        slugs = slugs[:limit]
    print(f"[hyundai] dealer slugs={len(slugs)}")
    session = _cffi.AsyncSession(impersonate=_IMPERSONATE, timeout=_TIMEOUT, allow_redirects=True)
    pool = await asyncpg.create_pool(DSN, min_size=2, max_size=6)
    stats = {"cars": 0, "new": 0}
    live = 0
    try:
        for slug in slugs:
            try:
                r = await session.get(f"https://www.hyundai.es/concesionarios/{slug}/seminuevos")
                cards = parse_hyundai_cards(r.text) if r.status_code == 200 else []
            except Exception:  # noqa: BLE001
                cards = []
            if cards:
                live += 1
                async with pool.acquire() as conn:
                    eulid = await _resolve_or_mint(conn, slug)
                    await _ingest(conn, eulid, cards, stats)
            await asyncio.sleep(_DEALER_DELAY)
    finally:
        await session.close()
        await pool.close()
    print("=" * 64)
    print(f"  hyundai: dealers={len(slugs)} live={live} caged={stats['cars']} new={stats['new']}")
    print("=" * 64)


def main() -> None:
    p = argparse.ArgumentParser(description="Hyundai ES seminuevos €0 connector")
    p.add_argument("--limit", type=int, default=None)
    a = p.parse_args()
    asyncio.run(_amain(a.limit))


if __name__ == "__main__":
    main()
