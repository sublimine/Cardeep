"""Honda ES per-dealer used-car (SSR) — €0 connector.

Each Honda dealer microsite ({slug}.honda.es) renders its used stock server-side:

    GET https://{host}/es/ocasion-honda/buscador            (page 1, + data-found total)
    GET https://{host}/es/ocasion/page{N}/xhr-results/       (page N>1, AJAX fragment)

Cars are <article id="vehicleMDX-{ID}"> blocks (allBrands -> multi-brand trade-ins). Fields:
  - data-link="/es/ocasion/{brand}/{model}/{variant}-{id}"  -> real per-car URL + make/model
  - price after `IVA incluido</div><div class="h3...">{N}&nbsp;&euro;</div>`
  - specs as <li title="Kilometraje|Combustible|..."><span data-value>{VALUE}</span></li>
  - year after title="Año de matriculación".
The stable per-car id is the vehicleMDX id; deep_link is the real data-link URL. Verified live
2026-06-22 (mcar-madrid: data-found=28, 12/page, xhr pagination confirmed). Parser is pure.
"""
from __future__ import annotations

import argparse
import asyncio
import html as _html
import json as _json
import math
import os
import re

import asyncpg
from curl_cffi import requests as _cffi

from pipeline.ids import ulid
from pipeline.platform._core.sql import (
    BULK_INSERT_EVENTS,
    BULK_INSERT_VEHICLES,
    BULK_TOUCH_VEHICLES,
)
from services.api.codes import cdp_code

HONDA_SOURCE_KEY = "honda_ocasion"
DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
_PAGE = 12
_IMPERSONATE = "chrome131"
_TIMEOUT = 40
_DEALER_DELAY = 0.3
_PAGE_DELAY = 0.2
_MAX_PAGES = 60


# --- pure parser (unit-tested offline) --------------------------------------------------------
def _to_int(s):
    m = re.search(r"\d[\d.]*", str(s or "").replace("&nbsp;", " "))
    return int(m.group(0).replace(".", "")) if m else None


def _to_float(s):
    m = re.search(r"\d[\d.]*", str(s or "").replace("&nbsp;", " "))
    return float(m.group(0).replace(".", "")) if m else None


def honda_found(html: str) -> int:
    m = re.search(r'data-found="(\d+)"', html)
    return int(m.group(1)) if m else 0


def parse_honda_cards(html: str, host: str) -> list[dict]:
    out, seen = [], set()
    for chunk in html.split('<article id="vehicleMDX-')[1:]:
        vid = chunk[:chunk.find('"')]
        if not vid or vid in seen:
            continue
        seen.add(vid)
        art = chunk[:9000]
        link = re.search(r'data-link="([^"]+)"', art)
        link = link.group(1) if link else None
        parts = [p for p in (link or "").split("/") if p]      # es, ocasion, brand, model, variant-id
        make = parts[2].replace("-", " ").title() if len(parts) > 2 else None
        model = parts[3].replace("-", " ").title() if len(parts) > 3 else None
        price = re.search(r'IVA incluido</div>\s*<div class="h3[^"]*"[^>]*>\s*([\d.]+)', art)
        specs = {}
        for m in re.finditer(r'title="([^"]+)"[^>]*>\s*<span[^>]*data-label[^>]*>[^<]*</span>'
                             r'\s*<span[^>]*data-value[^>]*>([^<]+)</span>', art):
            specs[_html.unescape(m.group(1)).strip().lower()] = _html.unescape(m.group(2)).strip()
        year = re.search(r'matriculaci[^"]*"[^>]*>\s*<span[^>]*>\s*(\d{4})', art) \
            or re.search(r'matriculaci\S*\D{0,40}(20[0-2]\d|19\d\d)', art)
        out.append({
            "url": f"https://{host}{link}" if link else f"https://{host}/es/ocasion/v/{vid.lower()}",
            "make": make,
            "model": model,
            "year": int(year.group(1)) if year else None,
            "km": _to_int(specs.get("kilometraje")),
            "price": _to_float(price.group(1)) if price else None,
            "ref": vid,
            "fuel": specs.get("combustible") or None,
            "title": " ".join(x for x in (make, model) if x) or None,
            "photo_url": None,
        })
    return out


# --- live drain + cage ------------------------------------------------------------------------
def _host(website: str) -> str | None:
    m = re.search(r"https?://([a-z0-9.-]*honda\.es)", website or "", re.I)
    return m.group(1).lower() if m else None


async def _resolve_or_mint(conn, host: str) -> str:
    row = await conn.fetchrow(
        "SELECT entity_ulid FROM entity WHERE website ILIKE $1 ORDER BY last_seen DESC LIMIT 1",
        f"%{host}%")
    if row:
        eulid = row["entity_ulid"]
    else:
        code = cdp_code(province_code="00", domain=host)
        await conn.execute(
            """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name, website,
                   is_tier1, status, kind_source, sells_cars, first_discovered_source, last_seen)
               VALUES ($1,$2,'concesionario_oficial',$3,$3,$4,FALSE,'active','platform_label',TRUE,$5, now())
               ON CONFLICT (cdp_code) DO UPDATE SET last_seen=now()""",
            ulid(), code, host.split(".")[0], f"https://{host}", HONDA_SOURCE_KEY)
        eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at=now()",
        eulid, HONDA_SOURCE_KEY, host)
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
                                "source": HONDA_SOURCE_KEY}) for l in confirmed]
            await conn.execute(BULK_INSERT_EVENTS, [ulid() for _ in confirmed],
                               [vid_for[l] for l in confirmed], [dealer_ulid] * len(confirmed), evp)


async def _drain_host(session, host: str) -> list[dict]:
    try:
        r = await session.get(f"https://{host}/es/ocasion-honda/buscador")
    except Exception:  # noqa: BLE001
        return []
    if r.status_code != 200:
        return []
    total = honda_found(r.text)
    cars = {c["ref"]: c for c in parse_honda_cards(r.text, host)}
    pages = min(_MAX_PAGES, max(1, math.ceil(total / _PAGE))) if total else 1
    for p in range(2, pages + 1):
        try:
            rp = await session.get(f"https://{host}/es/ocasion/page{p}/xhr-results/",
                                   headers={"X-Requested-With": "XMLHttpRequest"})
        except Exception:  # noqa: BLE001
            break
        if rp.status_code != 200:
            break
        new = parse_honda_cards(rp.text, host)
        if not new:
            break
        for c in new:
            cars.setdefault(c["ref"], c)
        await asyncio.sleep(_PAGE_DELAY)
    return list(cars.values())


async def _amain(limit):
    conn0 = await asyncpg.connect(DSN)
    rows = await conn0.fetch("SELECT DISTINCT website FROM entity WHERE website ILIKE '%honda.es%'")
    await conn0.close()
    hosts = sorted({h for h in (_host(r["website"]) for r in rows) if h and h != "honda.es"})
    if limit:
        hosts = hosts[:limit]
    print(f"[honda] dealer hosts={len(hosts)}")
    session = _cffi.AsyncSession(impersonate=_IMPERSONATE, timeout=_TIMEOUT, allow_redirects=True)
    pool = await asyncpg.create_pool(DSN, min_size=2, max_size=6)
    stats = {"cars": 0, "new": 0}
    live = 0
    try:
        for host in hosts:
            cars = await _drain_host(session, host)
            if cars:
                live += 1
                async with pool.acquire() as conn:
                    eulid = await _resolve_or_mint(conn, host)
                    await _ingest(conn, eulid, cars, stats)
            await asyncio.sleep(_DEALER_DELAY)
    finally:
        await session.close()
        await pool.close()
    print("=" * 64)
    print(f"  honda: hosts={len(hosts)} live={live} caged={stats['cars']} new={stats['new']}")
    print("=" * 64)


def main() -> None:
    p = argparse.ArgumentParser(description="Honda ES used-car €0 connector")
    p.add_argument("--limit", type=int, default=None)
    a = p.parse_args()
    asyncio.run(_amain(a.limit))


if __name__ == "__main__":
    main()
