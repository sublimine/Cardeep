"""VECTOR 5 — Recursive graph discovery (groups, branches, franchises).

From each known dealer website, crawl the corporate graph: jump to its branches,
parent group and sibling dealerships. Captures the sede that never lists itself but
hangs off a group — Quadis (+100), Huertas (+50), Caetano, etc. (plano §1.3 V5).

Mechanism (Tier-0, free):
1. Seed frontier = websites of already-known entities (live DB), or a targeted set
   via CARDEEP_GRAPH_SEEDS for recipe-first verification.
2. For each page: parse schema.org JSON-LD for AutoDealer/AutomotiveBusiness/Organization
   nodes with a postal address (each = a branch entity), and follow on-site links whose
   text/URL signals locations ("instalaciones", "concesionarios", "sucursales",
   "delegaciones", "nuestros-centros"), depth-bounded.
3. Emit one DiscoveredEntity per branch with its own address -> the INE resolver + the
   identity guard keep sibling branches as distinct entities (chain), not duplicates.

Recipe-first: CARDEEP_GRAPH_LIMIT seeds, CARDEEP_GRAPH_MAX_PAGES crawl budget,
CARDEEP_GRAPH_SEEDS to target specific groups. Self-isolates if no seed is reachable.
"""
from __future__ import annotations

import json
import os
import re
import threading
import urllib.parse

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/146.0 Safari/537.36"

# Anchor hints that a link leads to branch/location pages.
_BRANCH_HINTS = (
    "instalacion", "concesionario", "sucursal", "delegacion", "delegación", "nuestros-centros",
    "centros", "tiendas", "ubicacion", "ubicación", "donde-estamos", "puntos-de-venta",
    "red-de", "nuestra-red", "sedes", "locations", "dealers",
)
_DEALER_TYPES = {"autodealer", "automotivebusiness", "autorepair", "automobiledealer", "store",
                 "organization", "localbusiness"}


def _registrable_domain(url: str) -> str | None:
    try:
        netloc = urllib.parse.urlsplit(url).netloc.lower()
    except Exception:  # noqa: BLE001
        return None
    netloc = netloc.split("@")[-1].split(":")[0]
    return netloc[4:] if netloc.startswith("www.") else (netloc or None)


def _run_async(coro):
    box: dict = {}

    def worker():
        import asyncio

        box["v"] = asyncio.new_event_loop().run_until_complete(coro)

    t = threading.Thread(target=worker)
    t.start()
    t.join()
    return box.get("v")


async def _load_seed_sites(limit: int | None) -> list[str]:
    import asyncpg

    conn = await asyncpg.connect(DSN)
    try:
        q = ("SELECT DISTINCT website FROM entity WHERE website IS NOT NULL AND website <> '' "
             "AND status='active' ORDER BY website")
        if limit:
            q += f" LIMIT {int(limit)}"
        return [r["website"] for r in await conn.fetch(q)]
    finally:
        await conn.close()


def _fetch_requests(url: str) -> str | None:
    import requests

    try:
        r = requests.get(url, headers={"User-Agent": _UA}, timeout=20, allow_redirects=True)
        ct = r.headers.get("content-type", "")
        return r.text if (r.status_code == 200 and "html" in ct) else None
    except Exception:  # noqa: BLE001 — a dead/WAF'd seed must not kill the crawl
        return None


def _make_engine():
    """Build the antidetection FetchEngine (Tier-0 curl_cffi + Tier-1 browser on WAF).

    Returns None when the engine is unavailable or disabled (CARDEEP_GRAPH_TIER1=0),
    in which case the crawl falls back to plain requests. Tier-1 only fires on an
    actually-detected challenge, so most pages still serve cheaply via Tier-0.
    """
    if os.environ.get("CARDEEP_GRAPH_TIER1", "1") == "0":
        return None
    try:
        from pipeline.engine.fetch import FetchEngine

        return FetchEngine(allow_tier1_escalation=True, tier1_headless=False)
    except Exception:  # noqa: BLE001 — curl_cffi/engine missing: use requests fallback
        return None


def _fetch(url: str, engine=None) -> str | None:
    """Fetch HTML. Prefers the antidetection engine (gets 200 past Tier-1 WAFs that
    bare requests cannot), falling back to plain requests on any engine failure."""
    if engine is not None:
        try:
            from pipeline.engine.fetch import FetchError

            try:
                return engine.fetch_text(url)
            except FetchError:
                return None
        except Exception:  # noqa: BLE001 — engine path broke; try requests below
            pass
    return _fetch_requests(url)


def _iter_jsonld(html: str):
    for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.S | re.I):
        raw = m.group(1).strip()
        try:
            data = json.loads(raw)
        except Exception:  # noqa: BLE001
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
            elif isinstance(node, dict):
                if "@graph" in node:
                    stack.extend(node["@graph"] if isinstance(node["@graph"], list) else [node["@graph"]])
                yield node
                for v in node.values():
                    if isinstance(v, (list, dict)):
                        stack.append(v)


def _type_matches(node: dict) -> bool:
    t = node.get("@type")
    types = [t] if isinstance(t, str) else (t or [])
    return any(str(x).lower() in _DEALER_TYPES for x in types)


def _branch_from_node(node: dict, base_url: str) -> DiscoveredEntity | None:
    name = node.get("name") or node.get("legalName")
    addr = node.get("address")
    if isinstance(addr, list):
        addr = addr[0] if addr else None
    if not isinstance(addr, dict):
        return None  # no postal address -> not a locatable branch
    locality = addr.get("addressLocality")
    postcode = addr.get("postalCode")
    street = addr.get("streetAddress")
    geo = node.get("geo") if isinstance(node.get("geo"), dict) else {}
    site = node.get("url") or base_url
    province = str(postcode)[:2] if postcode and str(postcode)[:2].isdigit() else None
    if not (name and (locality or postcode)):
        return None
    return DiscoveredEntity(
        kind="concesionario_oficial",
        source_key="graph_recursive",
        source_ref=f"{_registrable_domain(base_url)}|{name}|{locality or postcode}",
        legal_name=name,
        trade_name=name,
        province_name=province,
        municipality_name=locality,
        address=street,
        postcode=str(postcode) if postcode else None,
        lat=_to_float(geo.get("latitude")),
        lon=_to_float(geo.get("longitude")),
        phone=node.get("telephone"),
        website=site,
        extra={"vector": 5, "seed": base_url},
    )


def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _branch_links(html: str, base_url: str) -> list[str]:
    out: list[str] = []
    base_dom = _registrable_domain(base_url)
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.S | re.I):
        href, text = m.group(1), re.sub(r"<[^>]+>", " ", m.group(2)).lower()
        hint = (href.lower() + " " + text)
        if not any(h in hint for h in _BRANCH_HINTS):
            continue
        full = urllib.parse.urljoin(base_url, href)
        if _registrable_domain(full) == base_dom and full != base_url:
            out.append(full.split("#")[0])
    # dedup preserving order
    seen: set[str] = set()
    return [u for u in out if not (u in seen or seen.add(u))]


class GraphRecursiveAdapter(SourceAdapter):
    """V5 — recursive corporate-graph crawl for branches/groups/franchises."""

    source_key = "graph_recursive"

    def __init__(self) -> None:
        self._rows: list[DiscoveredEntity] | None = None
        self._isolated: str | None = None
        self._pages = 0
        self._engine_kind = "requests"

    def _seeds(self) -> list[str]:
        env = os.environ.get("CARDEEP_GRAPH_SEEDS")
        if env:
            seeds = []
            for s in env.split(","):
                s = s.strip()
                if s:
                    seeds.append(s if "://" in s else "https://" + s)
            return seeds
        limit = os.environ.get("CARDEEP_GRAPH_LIMIT", "40")
        return _run_async(_load_seed_sites(int(limit))) or []

    def _build(self) -> list[DiscoveredEntity]:
        max_pages = int(os.environ.get("CARDEEP_GRAPH_MAX_PAGES", "120"))
        seeds = self._seeds()
        if not seeds:
            self._isolated = "no seed websites available"
            return []
        frontier = list(seeds)
        visited: set[str] = set()
        seen_ref: set[str] = set()
        out: list[DiscoveredEntity] = []
        reachable = False
        # One engine for the whole crawl = one coherent fingerprint + clearance cache,
        # so a Tier-1 solve on a group domain is reused across its branch pages.
        engine = _make_engine()
        self._engine_kind = "tier1" if engine is not None else "requests"
        while frontier and self._pages < max_pages:
            url = frontier.pop(0)
            if url in visited:
                continue
            visited.add(url)
            html = _fetch(url, engine)
            self._pages += 1
            if not html:
                continue
            reachable = True
            for node in _iter_jsonld(html):
                if not _type_matches(node):
                    continue
                ent = _branch_from_node(node, url)
                if ent and ent.source_ref not in seen_ref:
                    seen_ref.add(ent.source_ref)
                    out.append(ent)
            # only expand branch links from seed pages (depth 1) to bound the crawl
            if url in seeds:
                for link in _branch_links(html, url)[:12]:
                    if link not in visited:
                        frontier.append(link)
        if not reachable:
            self._isolated = "no seed website reachable (offline or all WAF-blocked)"
        return out

    def _load(self) -> list[DiscoveredEntity]:
        if self._rows is None:
            try:
                self._rows = self._build()
            except Exception as e:  # noqa: BLE001
                self._isolated = f"graph crawl error: {e!r}"
                self._rows = []
        return self._rows

    def declared_count(self) -> int | None:
        return None

    def fetch(self) -> list[DiscoveredEntity]:
        rows = self._load()
        if self._isolated:
            print(f"[graph_recursive] ISOLATED — {self._isolated}")
            return []
        print(f"[graph_recursive] engine={self._engine_kind} pages_crawled={self._pages} "
              f"branches={len(rows)}")
        return rows
