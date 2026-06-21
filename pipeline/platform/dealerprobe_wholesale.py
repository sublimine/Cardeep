"""DealerProbe connector — generic €0 own-site dealer auto-harvester (cascade + cage).

Built on the pure, unit-tested classifiers in `dealerprobe.py` (sitemap / JSON-LD / microdata /
SSR). NO per-dealer REGISTRY — the recon proved ~80% of inventory hangs off self-describing
signals. Cascade per domain: robots.txt -> sitemap discovery -> car sitemaps -> per-vehicle URL
frontier (or SSR home/listing links) -> PDP fetch -> JSON-LD || microdata || SSR inline specs.
The dealer is the OWNER (own-site stock, no marketplace edge), source_key 'dealerprobe_ownsite'.

Pure cascade (frontier, parse_pdp) is unit-tested offline with an injected fetch. The DB cage
(_upsert_dealer_dp / _ingest_dp / probe_dealer / main) is validated in vivo — it reuses the
wholesale spine (resolve_dealer_for_host, cdp_code, the canonical BULK SQL) with DP_SOURCE_KEY.
"""
from __future__ import annotations

import argparse
import asyncio
import json as _json
import os
import re
from collections.abc import Awaitable, Callable
from urllib.parse import urlparse

import asyncpg
from curl_cffi import requests as _cffi

from pipeline.ids import ulid
from pipeline.ops.health import is_open, record_run
from pipeline.platform._core.sql import (
    BULK_INSERT_EVENTS,
    BULK_INSERT_VEHICLES,
    BULK_TOUCH_VEHICLES,
)
from pipeline.platform.dealerprobe import (
    _ssr_km,
    _ssr_price,
    _ssr_year,
    classify_loc,
    extract_vehicle_links,
    is_vehicle_sitemap,
    parse_jsonld_vehicles,
    parse_microdata_vehicles,
    parse_ssr_cards,
)
from pipeline.platform.family_dealerk_wholesale import resolve_dealer_for_host
from services.api.codes import cdp_code

DP_SOURCE_KEY = "dealerprobe_ownsite"

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
_IMPERSONATE = "chrome131"
_TIMEOUT = 20
_DEALER_CAP = 400
_LISTING_PATHS = ("", "/coches-ocasion", "/coches-segunda-mano", "/vehiculos", "/stock", "/ocasion", "/coches")

_LOC_RE = re.compile(r"<loc>\s*(.*?)\s*</loc>", re.I | re.S)
_ROBOTS_SITEMAP_RE = re.compile(r"(?im)^\s*sitemap:\s*(\S+)")
_SITEMAP_CANDIDATES = ("/sitemap.xml", "/sitemap_index.xml", "/sitemap-index.xml")
_MAX_SITEMAPS_FETCHED = 60          # guardrail: never chase an unbounded index tree


async def probe_sitemap_frontier(
    fetch: Callable[[str], Awaitable[str | None]],
    domain: str,
    cap: int = 500,
) -> list[str]:
    """Return up to `cap` per-vehicle detail URLs discovered through the dealer's car sitemaps.

    `fetch` is an injected async (url) -> body|None (the governor-wrapped curl in production, a
    fake in tests). Walks robots.txt -> declared sitemaps (or /sitemap.xml fallbacks), expands
    <sitemapindex> following ONLY car-named children (is_vehicle_sitemap) + nested indexes, and
    from each <urlset> keeps the <loc>s that classify_loc()s as per_vehicle. Order-preserving,
    de-duplicated, bounded by `cap` and a hard sitemap-fetch ceiling.
    """
    base = (domain if domain.startswith("http") else f"https://{domain}").rstrip("/")

    robots = await fetch(f"{base}/robots.txt")
    sitemaps = [m.group(1).strip() for m in _ROBOTS_SITEMAP_RE.finditer(robots)] if robots else []
    if not sitemaps:
        sitemaps = [base + c for c in _SITEMAP_CANDIDATES]

    queue = list(dict.fromkeys(sitemaps))
    seen_sm: set[str] = set()
    seen_url: set[str] = set()
    frontier: list[str] = []
    fetched = 0

    while queue and len(frontier) < cap and fetched < _MAX_SITEMAPS_FETCHED:
        sm = queue.pop(0)
        if sm in seen_sm:
            continue
        seen_sm.add(sm)
        xml = await fetch(sm)
        fetched += 1
        if not xml:
            continue
        locs = _LOC_RE.findall(xml)
        if "<sitemapindex" in xml.lower():
            for loc in locs:                       # an index of sub-sitemaps
                if loc not in seen_sm and (is_vehicle_sitemap(loc) or "index" in loc.lower()):
                    queue.append(loc)
        else:
            for loc in locs:                       # a urlset of pages
                if loc in seen_url:
                    continue
                if classify_loc(loc) == "per_vehicle":
                    seen_url.add(loc)
                    frontier.append(loc)
                    if len(frontier) >= cap:
                        break
    return frontier


def _extract_pdp(html: str, url: str) -> dict | None:
    """One vehicle from a detail page by signal quality: JSON-LD -> microdata -> SSR inline specs.
    The SSR fallback matters: the recon showed JSON-LD is only ~11% — most PDPs carry price/km/year
    in plain HTML. Returns None only if there is no vehicle signal at all (sold/empty page)."""
    for parser in (parse_jsonld_vehicles, parse_microdata_vehicles):
        found = parser(html)
        if found:
            v = dict(found[0])
            v["url"] = v.get("url") or url
            return v
    price = _ssr_price(html)
    if price is not None:                       # SSR PDP: price inline is the floor signal
        return {"url": url, "ref": None, "title": None, "make": None, "model": None,
                "year": _ssr_year(html), "km": _ssr_km(html), "price": price}
    return None


async def parse_pdp(
    fetch: Callable[[str], Awaitable[str | None]],
    url: str,
) -> dict | None:
    """Fetch one per-vehicle detail page and return ONE normalized vehicle (JSON-LD -> microdata ->
    SSR inline specs). None if dead/sold/no vehicle data."""
    html = await fetch(url)
    if not html:
        return None
    return _extract_pdp(html, url)


# --- connector spine: own-site cage + per-dealer cascade + CLI (component 4b-ii) --------------

# Hosts whose "website" is NOT a drainable own-site: OEM brand-networks (the dealer's stock lives
# on the brand platform, not a generic sitemap), national marketplaces/aggregators (covered by
# their own connectors), SEO directory placeholders, and social profiles. Conservative on purpose
# — only CLEAR noise is dropped; unknown domains are kept and let the live status decide.
_NON_DRAINABLE_HOSTS = frozenset({
    # OEM brand networks
    "kia.com", "hyundai.es", "nissan.es", "renault.es", "dacia.es", "citroen.es", "ds.es",
    "peugeot.es", "opel.es", "bmw.es", "mini.es", "mercedes-benz.es", "audi.es", "volkswagen.es",
    "skoda.es", "seat", "cupraofficial.es", "ford.es", "toyota.es", "lexus.es", "mazda.es",
    "honda.es", "fiat.es", "jeep.es", "alfaromeo.es", "suzuki.es", "mitsubishi-motors.es",
    "volvocars.com", "kia.es", "hyundai.com",
    # national marketplaces / aggregators (own connectors elsewhere)
    "coches.net", "milanuncios.com", "wallapop.com", "autoscout24.es", "autoscout24.com",
    "clicars.com", "ocasionplus.es", "flexicar.es", "cargurus.es", "autocasion.com",
    # SEO directories / placeholders / social
    "beedigital.es", "paginasamarillas.es", "axesor.es", "einforma.com", "infoempresa.com",
    "facebook.com", "m.facebook.com", "instagram.com", "youtube.com", "twitter.com", "x.com",
    "tiktok.com", "linkedin.com", "wa.me", "whatsapp.com", "t.me", "google.com",
})


def _drainable_website(url: str) -> bool:
    """True iff `url` is a real own-site worth probing (not OEM-network/marketplace/social/junk).

    Drops malformed URLs (double scheme, no host) and any host that equals or is a subdomain of a
    known non-drainable host. Unknown domains pass — the live probe status classifies them."""
    if not url or url.count("://") != 1:
        return False                                  # e.g. http://www.https://www.x.com
    host = (urlparse(url).netloc or "").lower().split(":")[0]
    host = re.sub(r"^www\.", "", host)
    if not host or "." not in host:
        return False
    return not any(host == bad or host.endswith("." + bad) for bad in _NON_DRAINABLE_HOSTS)


class _Fetcher:
    """curl_cffi GET; returns body only on HTTP 200 (else None), last_status kept for diagnosis.
    A broken TLS cert is a dealer-side cosmetic defect, not an unreachable site: retry once with
    verification relaxed so a reachable dealer is not lost. Network/DNS failures -> None."""
    def __init__(self) -> None:
        self._s = _cffi.Session(impersonate=_IMPERSONATE)
        self.last_status: int | None = None

    def fetch(self, url: str) -> str | None:
        try:
            r = self._s.get(url, impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        except Exception as e:  # noqa: BLE001
            if any(t in type(e).__name__ for t in ("SSL", "Certificate")):
                try:
                    r = self._s.get(url, impersonate=_IMPERSONATE, timeout=_TIMEOUT, verify=False)
                except Exception:
                    self.last_status = None
                    return None
            else:
                self.last_status = None
                return None
        self.last_status = r.status_code
        return r.text if r.status_code == 200 else None


def _build_fetch():
    fetcher = _Fetcher()

    async def gf(url: str):
        return await asyncio.to_thread(fetcher.fetch, url)

    return gf, fetcher


async def _upsert_dealer_dp(conn: asyncpg.Connection, host: str) -> dict:
    """Own-site dealer entity for `host`: reuse the existing DB entity (matched by website) and
    stamp dealerprobe provenance, else mint a domain-keyed compraventa. source_key=DP_SOURCE_KEY."""
    existing = await resolve_dealer_for_host(conn, host)
    if existing:
        await conn.execute("UPDATE entity SET last_seen=now() WHERE entity_ulid=$1", existing["entity_ulid"])
        await conn.execute(
            "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
            "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at=now()",
            existing["entity_ulid"], DP_SOURCE_KEY, host)
        return existing
    bare = re.sub(r"^www\.", "", host.lower())
    code = cdp_code(province_code="00", domain=bare)
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name, website,
               is_tier1, status, kind_source, sells_cars, first_discovered_source, last_seen)
           VALUES ($1,$2,'compraventa',$3,$3,$4,FALSE,'active','platform_label',TRUE,$5, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen=now()""",
        ulid(), code, bare, bare, DP_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at=now()",
        eulid, DP_SOURCE_KEY, host)
    return {"entity_ulid": eulid, "cdp_code": code, "trade_name": bare, "website": bare}


async def _ingest_dp(conn: asyncpg.Connection, dealer_ulid: str, vehicles: list[dict], stats: dict) -> None:
    """Idempotent own-site cage on (entity_ulid, deep_link): touch existing, insert new, emit NEW."""
    by_link: dict[str, dict] = {}
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
                col("fuel"), [None] * n, col("photo_url"), [None] * n)
            landed = {r["deep_link"]: r["vehicle_ulid"] for r in await conn.fetch(
                "SELECT vehicle_ulid, deep_link FROM vehicle WHERE vehicle_ulid=ANY($1::text[])",
                [vid_for[l] for l in new_links])}
            for l in new_links:
                real = landed.get(l)
                if real == vid_for[l]:
                    confirmed.append(l)
                elif real:
                    vid_for[l] = real
        stats["cars_ingested"] += len(links)
        stats["new_cars"] += len(confirmed)
        if confirmed:
            evp = [_json.dumps({"price": by_link[l].get("price"), "title": by_link[l].get("title"),
                                "source": DP_SOURCE_KEY}) for l in confirmed]
            await conn.execute(BULK_INSERT_EVENTS, [ulid() for _ in confirmed],
                               [vid_for[l] for l in confirmed], [dealer_ulid] * len(confirmed), evp)
            stats["new_events"] += len(confirmed)


async def probe_dealer(conn, governed_fetch, fetcher, domain: str, cap: int = _DEALER_CAP) -> dict:
    """Cascade one dealer's OWN SITE: sitemap frontier (or SSR home/listing links) -> per-PDP
    vehicle -> own-site cage. status: live/dead/walled/noise. €0, no JS."""
    bare = re.sub(r"^www\.", "", domain.strip().lower()).split("/")[0]
    base = f"https://{bare}"
    summary = {"domain": bare, "status": "dead", "vehicles": 0, "new": 0, "frontier": 0, "signal": None}

    frontier = await probe_sitemap_frontier(governed_fetch, bare, cap)
    signal = "sitemap"
    home_seen = False
    if not frontier:
        signal = "ssr"
        for path in _LISTING_PATHS:
            html = await governed_fetch(base + path)
            if not html:
                continue
            home_seen = True
            for l in extract_vehicle_links(html, base + path + "/"):
                if l not in frontier:
                    frontier.append(l)
            if len(frontier) >= cap:
                break
        if not frontier:
            summary["status"] = ("walled" if fetcher.last_status == 403
                                  else "dead" if not home_seen else "noise")
            return summary

    summary["status"] = "live"
    summary["frontier"] = len(frontier)
    summary["signal"] = signal
    vehicles = []
    for url in frontier[:cap]:
        v = await parse_pdp(governed_fetch, url)
        if v:
            vehicles.append(v)
        await asyncio.sleep(0.2)                # gentle per-host pacing
    dealer = await _upsert_dealer_dp(conn, bare)
    stats = {"cars_ingested": 0, "new_cars": 0, "new_events": 0}
    await _ingest_dp(conn, dealer["entity_ulid"], vehicles, stats)
    summary["vehicles"] = stats["cars_ingested"]
    summary["new"] = stats["new_cars"]
    summary["dealer_cdp"] = dealer.get("cdp_code")
    return summary


async def _select_drainable(conn, limit):
    """Un-harvested compraventa websites, noise-filtered down to drainable own-sites."""
    rows = await conn.fetch(
        """SELECT website FROM entity e
             WHERE kind='compraventa' AND website IS NOT NULL AND website<>''
               AND NOT EXISTS (SELECT 1 FROM entity_source es
                               WHERE es.entity_ulid=e.entity_ulid
                                 AND (es.source_key LIKE 'family_%' OR es.source_key=$1))
             ORDER BY last_seen DESC""",
        DP_SOURCE_KEY)
    cand = [r["website"] for r in rows]
    drainable = [w for w in cand if _drainable_website(w)]
    print(f"[dealerprobe] --from-db candidates={len(cand)} drainable={len(drainable)} "
          f"dropped_noise={len(cand) - len(drainable)}")
    return drainable[:limit] if limit else drainable


async def _amain(domains, from_db, limit, cap, concurrency):
    pool = await asyncpg.create_pool(DSN, min_size=2, max_size=max(4, concurrency + 2))
    try:
        async with pool.acquire() as conn:
            if await is_open(conn, DP_SOURCE_KEY):
                print(f"[dealerprobe] breaker OPEN for {DP_SOURCE_KEY}; skipping (graceful).")
                return
            if from_db and not domains:
                domains = await _select_drainable(conn, limit)
        domains = domains or []
        sem = asyncio.Semaphore(concurrency)

        async def work(d):
            async with sem:
                fetcher = _Fetcher()                  # own session per concurrent worker

                async def gf(u):
                    return await asyncio.to_thread(fetcher.fetch, u)
                async with pool.acquire() as conn:
                    try:
                        return await probe_dealer(conn, gf, fetcher, d, cap)
                    except Exception as e:  # noqa: BLE001
                        return {"domain": d, "status": "error", "error": str(e)[:160],
                                "vehicles": 0, "new": 0}

        results = await asyncio.gather(*[work(d) for d in domains])
        total_caged = sum(r.get("vehicles", 0) for r in results)
        total_new = sum(r.get("new", 0) for r in results)
        for s in results:
            print(f"[dealerprobe] {str(s.get('domain')):40} {str(s.get('status')):7} "
                  f"signal={s.get('signal')} frontier={s.get('frontier', 0)} "
                  f"caged={s.get('vehicles', 0)} new={s.get('new', 0)}"
                  f"{' ERR=' + s['error'] if s.get('error') else ''}")
        try:
            async with pool.acquire() as conn:
                await record_run(conn, DP_SOURCE_KEY, ok=True, rows=total_caged, error=None)
        except Exception as e:  # noqa: BLE001
            print(f"[dealerprobe] record_run skipped: {e}")
        print("=" * 64)
        print(f"  dealers probed : {len(domains)}  (concurrency={concurrency})")
        print(f"  cars caged     : {total_caged} ({total_new} new)")
        print("  by status      : " + ", ".join(
            f"{st}={sum(1 for r in results if r.get('status') == st)}"
            for st in ("live", "dead", "walled", "noise", "error")))
        print("=" * 64)
    finally:
        await pool.close()


def main() -> None:
    p = argparse.ArgumentParser(description="DealerProbe — generic €0 own-site dealer auto-harvester")
    p.add_argument("--domains", nargs="*", default=None, help="explicit dealer domains to probe")
    p.add_argument("--from-db", action="store_true", help="probe DB dealers with a website not yet own-site-harvested")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--cap", type=int, default=_DEALER_CAP, help="max vehicles per dealer")
    p.add_argument("--concurrency", type=int, default=8, help="dealers probed in parallel")
    a = p.parse_args()
    asyncio.run(_amain(a.domains, a.from_db, a.limit, a.cap, a.concurrency))


if __name__ == "__main__":
    main()
