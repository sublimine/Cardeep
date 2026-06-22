"""SEAT / Das WeltAuto ES used-car (per-dealer SSR) — €0 connector.

Each SEAT/Cupra dealer's full used stock renders server-side, paginated 23/page:

    GET https://www.dasweltauto.es/esp/concesionario-seat-{slug}?pagina={N}

Every card carries two HTML-entity-encoded JSON blobs:
  - data-configuration = the vehicle (VehicleManufacturer, Carline.Name, Model.Name/Year,
    Vehicle.VehicleId/Milage/Registration, Budget.Price.price, Engine.FuelType.Main)
  - data-partner       = the dealer (InformationBnr id, InformationName/City/ZIP) — identical for
    every card on a dealer page (it is a per-dealer page).
Total is `numberOfResults`. NOTE verified live 2026-06-22: requesting a page beyond the last does
NOT return empty — it CLAMPS to the last page. So the stop condition is ceil(total/23), and cars are
de-duplicated by the stable Vehicle.VehicleId (the platform exposes no per-car canonical URL, only
per-model galleries, so deep_link is a synthetic stable key built from VehicleId). Parser is pure.

The dealer slug comes from the existing concesionarios.seat entities (overview-dw.dealer.{slug}.html);
inventory is attached to that entity when present, else a new entity is minted.
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

SEAT_SOURCE_KEY = "seat_dasweltauto"
DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
_BASE = "https://www.dasweltauto.es/esp/concesionario-seat-{slug}"
_PAGE = 23
_IMPERSONATE = "chrome131"
_TIMEOUT = 40
_DEALER_DELAY = 0.3
_PAGE_DELAY = 0.2
_MAX_PAGES = 60                                   # safety cap (clamp-paging guard)


# --- pure parser (unit-tested offline) --------------------------------------------------------
def _to_int(s):
    m = re.search(r"\d[\d.]*", str(s or ""))
    return int(m.group(0).replace(".", "")) if m else None


def _to_float(s):
    m = re.search(r"\d[\d.]*", str(s or "").replace(",", "."))
    return float(m.group(0).replace(".", "")) if m else None


def _blobs(html: str, attr: str) -> list[dict]:
    out = []
    for m in re.finditer(attr + r'=(["\'])(.*?)\1', html, re.S):
        try:
            out.append(_json.loads(_html.unescape(m.group(2))))
        except (ValueError, TypeError):
            continue
    return out


def seat_total(html: str) -> int:
    m = re.search(r'numberOfResults"\s*:\s*"?(\d+)', html)
    return int(m.group(1)) if m else 0


def parse_seat_dealer(html: str) -> dict | None:
    blobs = _blobs(html, "data-partner")
    if not blobs:
        return None
    d = blobs[0]
    return {
        "bnr": str(d.get("InformationBnr") or "").strip() or None,
        "name": (d.get("InformationName") or "").strip() or None,
        "city": (d.get("InformationCity") or "").strip() or None,
        "zip": (d.get("InformationZIP") or "").strip() or None,
    }


def parse_seat_cards(html: str) -> list[dict]:
    out, seen = [], set()
    for c in _blobs(html, "data-configuration"):
        veh = c.get("Vehicle") or {}
        vid = str(veh.get("VehicleId") or "").strip()
        if not vid or vid in seen:
            continue
        seen.add(vid)
        model = c.get("Model") or {}
        carline = c.get("Carline") or {}
        budget = ((c.get("Budget") or {}).get("Price") or {})
        fuel = (((c.get("Engine") or {}).get("FuelType") or {}).get("Main") or "").strip() or None
        out.append({
            "url": f"https://www.dasweltauto.es/esp/vehiculo/{vid}",   # synthetic stable key (no per-car canonical URL)
            "make": (c.get("VehicleManufacturer") or "").strip() or None,
            "model": (carline.get("Name") or "").strip() or None,
            "year": _to_int(model.get("Year") or (c.get("Production") or {}).get("Year")),
            "km": _to_int(veh.get("Milage")),
            "price": _to_float(budget.get("price")),
            "ref": vid,
            "fuel": fuel,
            "title": (model.get("Name") or "").strip() or None,
            "photo_url": None,
        })
    return out


# --- live drain + cage ------------------------------------------------------------------------
async def _resolve_or_mint(conn, slug: str, dealer: dict) -> str:
    row = await conn.fetchrow(
        "SELECT entity_ulid FROM entity WHERE website ILIKE $1 ORDER BY last_seen DESC LIMIT 1",
        f"%dealer.{slug}.html%")
    if row:
        eulid = row["entity_ulid"]
    else:
        bnr = dealer.get("bnr") or slug
        code = cdp_code(province_code="00", domain=f"bnr{bnr}.dasweltauto.es")
        tn = dealer.get("name") or slug
        await conn.execute(
            """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name, website,
                   is_tier1, status, kind_source, sells_cars, first_discovered_source, last_seen)
               VALUES ($1,$2,'concesionario_oficial',$3,$3,$4,FALSE,'active','platform_label',TRUE,$5, now())
               ON CONFLICT (cdp_code) DO UPDATE SET last_seen=now()""",
            ulid(), code, tn, f"dasweltauto.es/esp/concesionario-seat-{slug}", SEAT_SOURCE_KEY)
        eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at=now()",
        eulid, SEAT_SOURCE_KEY, slug)
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
                                "source": SEAT_SOURCE_KEY}) for l in confirmed]
            await conn.execute(BULK_INSERT_EVENTS, [ulid() for _ in confirmed],
                               [vid_for[l] for l in confirmed], [dealer_ulid] * len(confirmed), evp)


def _slug(website: str) -> str | None:
    m = re.search(r"dealer\.([a-z0-9_-]+)\.html", website or "", re.I)
    return m.group(1).lower() if m else None


async def _drain_slug(session, slug: str) -> tuple[dict | None, list[dict]]:
    try:
        r = await session.get(_BASE.format(slug=slug) + "?pagina=1")
    except Exception:  # noqa: BLE001
        return None, []
    if r.status_code != 200:
        return None, []
    html1 = r.text
    dealer = parse_seat_dealer(html1)
    total = seat_total(html1)
    cars = {c["ref"]: c for c in parse_seat_cards(html1)}
    pages = min(_MAX_PAGES, max(1, math.ceil(total / _PAGE)))
    for p in range(2, pages + 1):
        try:
            rp = await session.get(_BASE.format(slug=slug) + f"?pagina={p}")
        except Exception:  # noqa: BLE001
            break
        if rp.status_code != 200:
            break
        for c in parse_seat_cards(rp.text):
            cars.setdefault(c["ref"], c)          # dedup by VehicleId (clamp-paging guard)
        await asyncio.sleep(_PAGE_DELAY)
    return dealer, list(cars.values())


async def _amain(limit):
    conn0 = await asyncpg.connect(DSN)
    rows = await conn0.fetch(
        "SELECT DISTINCT website FROM entity WHERE website ILIKE '%overview-dw.dealer.%' "
        "OR website ILIKE '%.dealer.%.html%'")
    await conn0.close()
    slugs = sorted({s for s in (_slug(r["website"]) for r in rows) if s})
    if limit:
        slugs = slugs[:limit]
    print(f"[seat] dealer slugs={len(slugs)}")
    session = _cffi.AsyncSession(impersonate=_IMPERSONATE, timeout=_TIMEOUT, allow_redirects=True)
    pool = await asyncpg.create_pool(DSN, min_size=2, max_size=6)
    stats = {"cars": 0, "new": 0}
    live = 0
    try:
        for slug in slugs:
            dealer, cars = await _drain_slug(session, slug)
            if cars:
                live += 1
                async with pool.acquire() as conn:
                    eulid = await _resolve_or_mint(conn, slug, dealer or {})
                    await _ingest(conn, eulid, cars, stats)
            await asyncio.sleep(_DEALER_DELAY)
    finally:
        await session.close()
        await pool.close()
    print("=" * 64)
    print(f"  seat: dealers={len(slugs)} live={live} caged={stats['cars']} new={stats['new']}")
    print("=" * 64)


def main() -> None:
    p = argparse.ArgumentParser(description="SEAT/DasWeltAuto ES used-car €0 connector")
    p.add_argument("--limit", type=int, default=None)
    a = p.parse_args()
    asyncio.run(_amain(a.limit))


if __name__ == "__main__":
    main()
