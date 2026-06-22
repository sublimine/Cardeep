"""Spoticar (Stellantis pan-brand used-car marketplace) — €0 API connector.

Stellantis dealers' used stock (Citroën/Peugeot/Opel/DS/Fiat/Jeep) does NOT live on the OEM
dealer microsites (redoficial.citroen.es / redcomercial.peugeot.es — those are dead BigIP stubs
or new-car-only brochures). It lives on spoticar.es behind a public Elasticsearch-backed JSON API:

    GET https://www.spoticar.es/api/vehicleoffers/paginate/search?page={N}   (12 cars/page)
    headers: X-Requested-With: XMLHttpRequest, Referer: .../comprar-coches-de-ocasion

One national sweep (page 1..lastPage) returns EVERY used car; each carries its point-of-sale
(field_pdv_geo_id / title / city). We group by geo_id and cage per dealer. GET-only, no auth, €0.
Verified live 2026-06-22: count.value=6411, lastPage=583, hits[*]._source as below.
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

SP_SOURCE_KEY = "spoticar_api"
DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
_BASE = "https://www.spoticar.es"
_PAGINATE = _BASE + "/api/vehicleoffers/paginate/search?page={page}"
_HEADERS = {"X-Requested-With": "XMLHttpRequest", "Referer": _BASE + "/comprar-coches-de-ocasion"}
_IMPERSONATE = "chrome131"
_TIMEOUT = 30
_PAGE_DELAY = 0.25


# --- pure parsers (unit-tested offline) -------------------------------------------------------
def _first(v):
    """Spoticar stores every scalar as a 1-element array; unwrap it."""
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _to_int(v):
    v = _first(v)
    if isinstance(v, (int, float)):
        return int(v)
    if v is None:
        return None
    m = re.search(r"\d+", str(v))
    return int(m.group(0)) if m else None


def _to_float(v):
    v = _first(v)
    if isinstance(v, (int, float)):
        return float(v)
    if v is None:
        return None
    s = re.sub(r"[^\d.]", "", str(v))
    return float(s) if s else None


def vehicle_from_source(src: dict) -> dict | None:
    """Normalize one Spoticar hit._source into the canonical vehicle dict. None if no detail URL."""
    url = _first(src.get("url"))
    if not url:
        return None
    if url.startswith("/"):
        url = _BASE + url
    make = _first(src.get("marque"))
    model = _first(src.get("model"))
    version = _first(src.get("version"))
    title = " ".join(str(x) for x in (make, model, version) if x) or None
    return {
        "url": url,
        "make": make,
        "model": model,
        "year": _to_int(src.get("field_vo_annee_modele")),
        "km": _to_int(src.get("field_vo_km")),
        "price": _to_float(src.get("field_vo_prix_base")),
        "ref": _first(src.get("field_vo_vin")),
        "fuel": _first(src.get("fuel_type")),
        "title": title,
        "photo_url": None,
        "geo_id": _first(src.get("field_pdv_geo_id")),
        "dealer_name": _first(src.get("field_pdv_title")),
        "city": _first(src.get("field_pdv_city")),
    }


def parse_spoticar_page(obj: dict) -> list[dict]:
    """Vehicles from one paginate/search JSON response ($.hits[*]._source)."""
    out = []
    for h in (obj.get("hits") or []):
        src = h.get("_source") if isinstance(h, dict) else None
        if isinstance(src, dict):
            v = vehicle_from_source(src)
            if v:
                out.append(v)
    return out


def page_meta(obj: dict) -> tuple[int, int]:
    """(total_count, last_page) from a paginate/search response."""
    cnt = obj.get("count") or {}
    total = cnt.get("value") if isinstance(cnt, dict) else (cnt or 0)
    return int(total or 0), int(obj.get("lastPage") or 1)


# --- live drain + cage (validated in vivo) ----------------------------------------------------
async def _drain_all(fetch, max_pages: int | None = None) -> list[dict]:
    """Sweep the national result set page 1..lastPage; return all vehicles (each carries geo_id)."""
    first = await fetch(_PAGINATE.format(page=1))
    if not first:
        return []
    j = _json.loads(first)
    total, last = page_meta(j)
    if max_pages:
        last = min(last, max_pages)
    vehicles = parse_spoticar_page(j)
    print(f"[spoticar] total_cars={total} last_page={last} (draining {last} pages)")
    for page in range(2, last + 1):
        b = await fetch(_PAGINATE.format(page=page))
        if b:
            try:
                vehicles.extend(parse_spoticar_page(_json.loads(b)))
            except Exception:  # noqa: BLE001
                pass
        await asyncio.sleep(_PAGE_DELAY)
    return vehicles


async def _upsert_spoticar_dealer(conn, geo_id: str, name: str | None, city: str | None) -> str:
    """One entity per Spoticar point-of-sale (stable cdp_code keyed by geo_id). source_key=SP."""
    code = cdp_code(province_code="00", domain=f"{geo_id}.spoticar.es")   # bare synthetic host, unique/dealer
    tn = (name or f"spoticar-{geo_id}").strip()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name, website,
               is_tier1, status, kind_source, sells_cars, first_discovered_source, last_seen)
           VALUES ($1,$2,'compraventa',$3,$3,$4,FALSE,'active','platform_label',TRUE,$5, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen=now()""",
        ulid(), code, tn, f"spoticar.es/pos/{geo_id}", SP_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at=now()",
        eulid, SP_SOURCE_KEY, str(geo_id))
    return eulid


async def _ingest_sp(conn, dealer_ulid: str, vehicles: list[dict], stats: dict) -> None:
    """Idempotent cage on (entity_ulid, deep_link); event source=SP_SOURCE_KEY (honest tagging)."""
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
                                "source": SP_SOURCE_KEY}) for l in confirmed]
            await conn.execute(BULK_INSERT_EVENTS, [ulid() for _ in confirmed],
                               [vid_for[l] for l in confirmed], [dealer_ulid] * len(confirmed), evp)


def _build_fetch():
    session = _cffi.AsyncSession(impersonate=_IMPERSONATE, timeout=_TIMEOUT,
                                 allow_redirects=True, headers=_HEADERS)

    async def gf(url):
        try:
            r = await session.get(url)
        except Exception:  # noqa: BLE001
            return None
        return r.text if r.status_code == 200 else None

    return gf, session


async def _amain(max_pages):
    gf, session = _build_fetch()
    try:
        vehicles = await _drain_all(gf, max_pages)
    finally:
        await session.close()
    by_geo = defaultdict(list)
    for v in vehicles:
        by_geo[v.get("geo_id") or "unknown"].append(v)
    pool = await asyncpg.create_pool(DSN, min_size=2, max_size=6)
    stats = {"cars": 0, "new": 0}
    dealers = 0
    try:
        for geo, vs in by_geo.items():
            async with pool.acquire() as conn:
                eulid = await _upsert_spoticar_dealer(conn, geo, vs[0].get("dealer_name"), vs[0].get("city"))
                await _ingest_sp(conn, eulid, vs, stats)
                dealers += 1
    finally:
        await pool.close()
    print("=" * 64)
    print(f"  spoticar: vehicles_fetched={len(vehicles)} dealers(geo_id)={dealers} "
          f"caged={stats['cars']} new={stats['new']}")
    print("=" * 64)


def main() -> None:
    p = argparse.ArgumentParser(description="Spoticar (Stellantis) €0 used-car API connector")
    p.add_argument("--pages", type=int, default=None, help="cap pages drained (validation); default=all")
    a = p.parse_args()
    asyncio.run(_amain(a.pages))


if __name__ == "__main__":
    main()
