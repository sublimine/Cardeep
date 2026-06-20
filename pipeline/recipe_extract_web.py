"""Generic dealer-website inventory extractor — the §4 cost-0 (JSON-LD) ladder rung.

Drives the recipe harness over an ARBITRARY dealer's own website (not a known marketplace):
discover the stock/inventory page from the homepage, then extract a small sample of vehicles
from schema.org JSON-LD (``Car`` / ``Vehicle`` / ``Product`` / ``Motorcycle``) — the universal,
zero-cost structured layer that CMS/DMS dealer sites emit. Sites that expose no vehicle JSON-LD
(JS-rendered "crappy" webs) yield an empty sample, so the harness marks their recipe FAILED with
a precise reason — the honest recipe-first outcome, never a fake success. Those are the targets
for the higher §4 rungs (declared CSS selectors / local-LLM), out of scope for this rung.

Transport goes through the shared antidetection engine (``pipeline.engine.fetch.fetch_text``),
so a WAF-gated dealer site escalates to the browser tier transparently.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict

from pipeline.engine.fetch import fetch_text
from pipeline.recipe_harness import Sample
from pipeline.recipe_schema import Fingerprint, Pagination, Parsing, Recipe, Transport

log = logging.getLogger(__name__)

_VEHICLE_TYPES = ("Car", "Vehicle", "MotorizedVehicle", "Motorcycle", "Product")
_STOCK_HINT = re.compile(
    r'href="([^"]*(?:coches|vehiculos|veh%C3|stock|ocasion|inventario|segunda-mano|'
    r'nuestros-coches|vehiculos-ocasion|km0|kilometro-0)[^"]*)"', re.I)
_LD = re.compile(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S)
_COUNT_HINT = re.compile(r'(\d{1,5})\s*(?:veh[ií]culos|coches)\b', re.I)
_MARKETPLACES = ("paginasamarillas", "facebook", "instagram", "twitter", "youtube",
                 "wallapop", "coches.net", "autoscout", "milanuncios")


def find_stock_url(home_html: str, base: str) -> str | None:
    """Best-effort discovery of the dealer's inventory page URL from homepage anchors."""
    for href in _STOCK_HINT.findall(home_html):
        href = href.replace("&amp;", "&").split("#")[0]
        if any(m in href for m in _MARKETPLACES):
            continue
        if href.startswith("http"):
            url = href
        elif href.startswith("/"):
            url = base.rstrip("/") + href
        else:
            url = base.rstrip("/") + "/" + href
        return url
    return None


def vehicles_from_jsonld(html: str) -> list[dict]:
    """Recursively collect schema.org vehicle objects from every JSON-LD block.

    A node counts as a vehicle when its @type is one of the vehicle types AND it carries a
    name (the minimal identity). Price/url are pulled when present (they make the listing
    actionable but a named model is enough to count it as a parsed vehicle)."""
    out: list[dict] = []
    for block in _LD.findall(html):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
                continue
            if not isinstance(node, dict):
                continue
            t = node.get("@type", "")
            t_str = " ".join(t) if isinstance(t, list) else str(t)
            if any(vt in t_str for vt in _VEHICLE_TYPES) and node.get("name"):
                offers = node.get("offers")
                price = None
                if isinstance(offers, dict):
                    price = offers.get("price")
                elif isinstance(offers, list) and offers:
                    price = (offers[0] or {}).get("price") if isinstance(offers[0], dict) else None
                out.append({"name": str(node.get("name"))[:120],
                            "price": price, "url": node.get("url"), "type": t_str})
            for v in node.values():
                if isinstance(v, (dict, list)):
                    stack.append(v)
    return out


_MICRO_ITEM = re.compile(
    r'itemscope[^>]*itemtype="[^"]*(?:Car|Vehicle|Product|MotorizedVehicle)"(.*?)'
    r'(?=itemscope[^>]*itemtype="[^"]*(?:Car|Vehicle|Product|MotorizedVehicle)"|$)', re.S | re.I)


def vehicles_from_microdata(html: str) -> list[dict]:
    """schema.org MICRODATA rung: each itemscope of a vehicle type, with itemprop name +
    offers/price. Complements JSON-LD (some dealer CMS emit one or the other)."""
    out: list[dict] = []
    for block in _MICRO_ITEM.findall(html):
        nm = re.search(r'itemprop="name"[^>]*(?:content="([^"]+)"|>\s*([^<]+))', block)
        name = (nm.group(1) or nm.group(2)).strip() if nm else None
        if not name:
            continue
        pm = re.search(r'itemprop="price"[^>]*(?:content="([^"]+)"|>\s*([\d.,]+))', block)
        price = (pm.group(1) or pm.group(2)) if pm else None
        um = re.search(r'itemprop="url"[^>]*(?:content="([^"]+)"|href="([^"]+)")', block)
        url = (um.group(1) or um.group(2)) if um else None
        out.append({"name": name[:120], "price": price, "url": url, "type": "microdata"})
    return out


def _valid(v: dict) -> bool:
    # a sample-valid vehicle has a model name and at least one actionable signal (price or url)
    return bool(v.get("name")) and (v.get("price") is not None or bool(v.get("url")))


class GenericWebExtractor:
    """Harness Extractor for an arbitrary dealer website (dealer_ref == the website URL)."""

    source = "web_generic"

    def __init__(self) -> None:
        self._disc: dict[str, dict] = {}  # website -> {stock_url, declared}

    def recipe_template(self, dealer_ref: str) -> Recipe:
        d = self._disc.get(dealer_ref, {})
        stock = d.get("stock_url") or dealer_ref
        return Recipe(
            source=self.source, dealer_ref=dealer_ref, kind="compraventa",
            transport=Transport(engine="curl_cffi", base_url=dealer_ref, impersonate="chrome", timeout_s=30),
            fingerprint=Fingerprint(user_agent="engine-managed"),
            pagination=Pagination(strategy="single_page", url_template=stock,
                                  declared_path="page text: N vehículos", stop="empty_page"),
            parsing=Parsing(engine=d.get("engine", "jsonld"), container_path="schema.org Car|Vehicle|Product",
                            field_map={"name": "jsonld .name", "price": "jsonld .offers.price",
                                       "url": "jsonld .url"}),
        )

    def sample(self, dealer_ref: str, k: int) -> Sample:
        """Discover the stock page and pull up to k JSON-LD vehicles from it."""
        home = fetch_text(dealer_ref, tier=0)
        stock_url = find_stock_url(home, dealer_ref)
        # the homepage itself may already list stock; fall back to it.
        pages = [u for u in (stock_url, dealer_ref) if u]
        vehicles: list[dict] = []
        used_url = dealer_ref
        used_engine = "jsonld"
        declared = None
        for url in pages:
            html = home if url == dealer_ref and stock_url is None else fetch_text(url, tier=0)
            vs = vehicles_from_jsonld(html)
            engine = "jsonld"
            if not vs:
                vs = vehicles_from_microdata(html)
                engine = "microdata"
            if vs:
                vehicles, used_url, used_engine = vs, url, engine
                m = _COUNT_HINT.search(html)
                declared = int(m.group(1)) if m else None
                break
        self._disc[dealer_ref] = {"stock_url": used_url, "declared": declared, "engine": used_engine}
        sliced = vehicles[:k]
        parsed = [v for v in sliced if _valid(v)]
        full = declared is not None and declared <= len(sliced)
        return Sample(declared=declared, fetched=len(sliced), parsed=parsed, full_dealer=full)
