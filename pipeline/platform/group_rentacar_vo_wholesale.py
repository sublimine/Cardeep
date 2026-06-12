"""rentacar_vo WHOLESALE harvester — rent-a-car companies selling their EX-FLEET used cars.

This is a SEPARATE source_group ('rentacar_vo'): rent-a-car operators that liquidate their
own used fleet through a dedicated used-stock storefront. The car a buyer purchases is a real
selling point — the rent-a-car COMPANY itself — so the company is caged as the entity and every
ex-fleet car is OWNED BY it, exactly as a marketplace's dealer owns its cars.

PRIMARY MEMBER — OK Mobility (okmobility.com/en/buy-car/used). Verified LIVE 2026-06-13:
a Spanish mobility operator (HQ Palma de Mallorca) that sells its ex-rental fleet through a
server-rendered, paginated used-stock storefront. The data-layer is SSR HTML: each car is a
`<a class="own-car-card" data-carid=N ...>` card carrying the deep link, the internal car id,
the image (cdn.okrentacar.es — the ex-rental CDN, proof of fleet origin), make+model, version,
year, km, fuel, transmission, the current price and (when present) the previous price for a
price-drop delta. No browser, no proxy, no cookie warm-up — a Chrome TLS fingerprint
(curl_cffi impersonate=chrome131) over `GET /en/buy-car/used?page=N` returns the same markup the
browser renders. `id="total-cars"` declares the full stock (172 verified live). The storefront's
public site carries an Opticks bot-protection beacon, but the listing HTML is unwalled.

This module mirrors pipeline.platform.coches_net_wholesale / oem_audi_wholesale EXACTLY (same
platform/owner model, same caging, same governor/health/VAM wiring), proving the rentacar_vo group
flows through the ONE architecture, not a fork of it:

  OK Mobility (the rent-a-car company) -> entity, kind='rent_a_car_vo' (+ platform_meta)  [SELLING POINT]
  each EX-FLEET CAR                     -> vehicle, OWNED BY the company (entity_ulid=company)
  the car ON the storefront            -> platform_listing edge (company_entity <-> vehicle)

Ownership and platform-membership coincide here: a single-operator storefront has exactly ONE
selling entity (the company), so the owning entity and the platform entity are the SAME row. The
platform_listing edge still records the listing (url, ref, price) so the car carries the same
membership signal a marketplace car does, and the same physical car could in principle also carry
a coches.net/AS24 edge (OK Mobility also lists on coches.net) without changing its owner here.

The company is geo-anchored to its registered HQ province (Palma de Mallorca -> INE 07, Illes
Balears). Individual showroom branches (Palma, Barcelona, Bilbao, Cuenca, Jaén) are NOT exposed
per-car on the listing surface, so we do NOT fabricate a per-branch owner the source withholds:
the company IS the selling point and owns the car. The branch network is recorded in the recipe
for a future per-branch attribution pass once the detail surface is drained.

PROOF SLICE / FULL DRAIN. OK Mobility declares ~172 cars (id="total-cars"). At ~35 cars/SSR page
that is ~5 pages — small enough that the default run drains the WHOLE storefront. MAX_PAGES caps
the page window honestly; the declared full count is recorded for the VAM verdict's arithmetic.

Engine: a GET against okmobility.com routed THROUGH the per-host governor (the same single choke
point coches.net/AS24 use). The synchronous curl_cffi GET runs in a worker thread so the event
loop is never blocked, and no host is fetched faster than its bucket.

Run: python -m pipeline.platform.group_rentacar_vo_wholesale --pages 6
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
import re
import sys
from dataclasses import dataclass

import asyncpg
from curl_cffi import requests as cffi_requests

from pipeline.engine.governor import governor, host_of
from pipeline.geo import GeoResolver
from pipeline.ids import ulid
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict
from services.api.codes import _base32, cdp_code

DSN = "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
DSN = os.environ.get("CARDEEP_DSN", DSN)

# ---------------------------------------------------------------------------
# rentacar_vo group + OK Mobility member identity (the 0016 multi-axis classification).
# ---------------------------------------------------------------------------
OK_DOMAIN = "okmobility.com"
OK_WEBSITE = "okmobility.com"
OK_LEGAL_NAME = "OK Mobility Group"
OK_TRADE_NAME = "OK Mobility"
OK_SOURCE_KEY = "group_rentacar_vo_okmobility"
OK_FAMILY = "okmobility"

OK_KIND = "rent_a_car_vo"          # entity_kind: a rent-a-car operator selling its VO fleet.
OK_SOURCE_GROUP = "rentacar_vo"    # source_group (the group this connector opens).
OK_ROLE = "chain"                  # entity_role: a single-brand chain of showroom branches.
OK_DEFENSE_TIER = "t1_soft"        # listing HTML is unwalled; the public site carries an Opticks
                                   # bot beacon -> soft, not t0_open.
OK_WAF = None                      # no hard WAF fronts the listing HTML itself.

# OK Mobility's registered HQ is Palma de Mallorca -> INE province 07 (Illes Balears). The company
# is the singular selling entity; its branches (Palma/Barcelona/Bilbao/Cuenca/Jaén) are not exposed
# per-car on the listing surface, so the company anchors to its HQ province (never fabricated).
OK_HQ_PROVINCE = "07"
OK_HQ_CITY = "Palma de Mallorca"

# The working request (verified live 2026-06-13). The '/en/' locale serves; '/es/' 404s.
_BASE = "https://okmobility.com"
ENDPOINT = "https://okmobility.com/en/buy-car/used"
_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://okmobility.com/en/buy-car/",
}
_IMPERSONATE = "chrome131"
_TIMEOUT = 40

# Province sentinel '00' = national, mirrors the marketplaces. The platform/company entity stores
# its REAL HQ province (07), so '00' is only used in code paths that need a national segment.
PLATFORM_PROVINCE_SENTINEL = "00"

# PROOF/FULL cap. ~35 cars/SSR page, ~172 declared -> ~5 pages drains the whole storefront. A
# default of 6 covers the full set with margin; a smaller --pages caps the window honestly.
DEFAULT_MAX_PAGES = 6

# ---------------------------------------------------------------------------
# SSR-HTML card regexes (field names inspected live, not assumed — see module docstring).
# ---------------------------------------------------------------------------
# A single car card starts at <a class="own-car-card" ...> and carries data-carid + a deep link.
_CARD_SPLIT = re.compile(r'(?=<a [^>]*class="own-car-card")')
_RE_HREF = re.compile(r'href="(https://okmobility\.com/en/buy-car/used/[^"]+/\d+)"')
_RE_CARID = re.compile(r'data-carid="(\d+)"')
_RE_PROGICIEL = re.compile(r'data-carProgicielId="(\d+)"', re.I)
_RE_IMG = re.compile(r'data-srcbg="([^"]+)"')
_RE_NAME = re.compile(r'car-name"[^>]*>\s*([^<]+?)\s*<')
_RE_MOTOR = re.compile(r'car-motorization">\s*([^<]+?)\s*<')
_RE_SUMMARY = re.compile(r'car-summary">(.*?)</div>', re.S)
_RE_SUMMARY_SPAN = re.compile(r'<span>\s*([^<|]+?)\s*</span>')
_RE_PRICE = re.compile(r'paying-prices">.*?big-cipher-text">\s*([\d.,]+)', re.S)
_RE_PREV = re.compile(r'deleted-small-cipher-text">\s*([\d.,]+)')
_RE_TOTAL = re.compile(r'id="total-cars"[^>]*>\s*([\d.,]+)')

# fuel labels seen live (EN locale): Gasoline/Diesel/Electric/Hybrid/Plug-in Hybrid. Kept raw.
# transmission: Manual/Automatic. No mapping table needed — the surface already serves clean labels.


def ok_platform_cdp_code() -> str:
    """OK Mobility's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:okmobility.com') with the HQ province segment (07). Mirrors
    coches_platform_cdp_code() so every selling point mints codes the same way."""
    key = f"domain:{OK_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{OK_HQ_PROVINCE}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Parsed shapes
# ---------------------------------------------------------------------------


@dataclass
class Vehicle:
    """A car parsed from one OK Mobility SSR used-stock card."""
    deep_link: str
    listing_ref: str            # OK Mobility internal car id (data-carid) — stable cross-run id.
    progiciel_id: str | None    # the id in the URL tail (progiciel/stock id); kept for the recipe.
    title: str | None
    make: str | None
    model: str | None
    version: str | None
    year: int | None
    km: int | None
    price: float | None
    prev_price: float | None    # previous price -> price-drop delta (gold for the delta event).
    fuel: str | None
    transmission: str | None
    photo_url: str | None


def _to_int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _eur_to_float(s: str | None) -> float | None:
    """OK Mobility prices are ES-formatted thousands ('16.641', '18.490'). Strip the dot
    thousands-separator -> plain integer euros. No decimals on the listing surface."""
    if not s:
        return None
    digits = re.sub(r"[^\d]", "", s)
    if not digits:
        return None
    try:
        return float(digits)
    except (TypeError, ValueError):
        return None


def _km_to_int(s: str | None) -> int | None:
    """'29.863 Km' -> 29863. Strip the 'Km' suffix and the dot thousands-separator."""
    if not s:
        return None
    digits = re.sub(r"[^\d]", "", s)
    if not digits:
        return None
    n = int(digits)
    return n if 0 <= n <= 5_000_000 else None


def _split_make_model(name: str | None) -> tuple[str | None, str | None]:
    """car-name is 'Skoda Kamiq Selection' / 'SEAT Arona Fr Xl Rx' / 'BMW Serie 1 Nv'. The first
    token is the make; the rest is the model line. A two-word make ('Mercedes-Benz', 'Land Rover')
    is hyphenated or two tokens — we keep the first token as make and let the title carry the full
    string, since the canonical make set is not enforced here (display-grade attribution)."""
    if not name:
        return None, None
    parts = name.split()
    if not parts:
        return None, None
    make = parts[0]
    # Two-token makes the surface renders with a space.
    TWO = {"land": "Land Rover", "alfa": "Alfa Romeo", "aston": "Aston Martin", "ds": "DS"}
    if len(parts) >= 2 and parts[0].lower() in TWO and TWO[parts[0].lower()].lower().endswith(parts[1].lower()):
        make = TWO[parts[0].lower()]
        model = " ".join(parts[2:]) or None
        return make, model
    model = " ".join(parts[1:]) or None
    return make, model


def parse_card(block: str) -> Vehicle | None:
    """Parse one OK Mobility SSR card block into a Vehicle, or None if it is not a real car card
    (missing the deep link or the internal id — never fabricate)."""
    href = _RE_HREF.search(block)
    cid = _RE_CARID.search(block)
    if not href or not cid:
        return None
    deep_link = href.group(1)
    listing_ref = cid.group(1)
    pid = _RE_PROGICIEL.search(block)
    img = _RE_IMG.search(block)
    name = _RE_NAME.search(block)
    motor = _RE_MOTOR.search(block)

    year = km = fuel = trans = None
    summ = _RE_SUMMARY.search(block)
    if summ:
        parts = [s.strip() for s in _RE_SUMMARY_SPAN.findall(summ.group(1)) if s.strip()]
        if len(parts) >= 1:
            year = _to_int(parts[0])
            if year is not None and not (1900 <= year <= 2100):
                year = None
        if len(parts) >= 2:
            km = _km_to_int(parts[1])
        if len(parts) >= 3:
            fuel = parts[2] or None
        if len(parts) >= 4:
            trans = parts[3] or None

    title = name.group(1).strip() if name else None
    make, model = _split_make_model(title)
    price = _eur_to_float(_RE_PRICE.search(block).group(1)) if _RE_PRICE.search(block) else None
    prev = _eur_to_float(_RE_PREV.search(block).group(1)) if _RE_PREV.search(block) else None

    return Vehicle(
        deep_link=deep_link,
        listing_ref=listing_ref,
        progiciel_id=pid.group(1) if pid else None,
        title=title,
        make=make,
        model=model,
        version=motor.group(1).strip() if motor else None,
        year=year,
        km=km,
        price=price,
        prev_price=prev,
        fuel=fuel,
        transmission=trans,
        photo_url=img.group(1) if img else None,
    )


def parse_page(html: str) -> tuple[list[Vehicle], int | None]:
    """Parse a full SSR list page -> (vehicles, declared_total). The page is split on the card
    anchor; the first fragment is the page chrome (no card) and is skipped by parse_card."""
    total_m = _RE_TOTAL.search(html)
    declared = _to_int(total_m.group(1).replace(".", "").replace(",", "")) if total_m else None
    vehicles: list[Vehicle] = []
    for block in _CARD_SPLIT.split(html):
        if "own-car-card" not in block or "data-carid" not in block:
            continue
        v = parse_card(block)
        if v is not None:
            vehicles.append(v)
    return vehicles, declared


# ---------------------------------------------------------------------------
# Fetch: a GET routed THROUGH the governor (same per-host choke point as coches.net/AS24).
# ---------------------------------------------------------------------------


class OkFetcher:
    """A POOL of fingerprint-coherent curl_cffi GET sessions for the OK Mobility SSR storefront.

    A single curl_cffi Session is not thread-safe under the governor's to_thread fetch, so we lease
    one Session per concurrency slot. The governor's per-host bucket bounds the aggregate rate, so
    the pool widens parallelism WITHOUT out-pacing the host (the bucket is the limiter)."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch_page(self, url: str, *, page: int = 1, slot: int = 0) -> str:
        """The synchronous GET on pool session `slot` (runs in a worker thread). Returns the raw
        HTML text. `page` rides as the ?page=N query param. Raises on a non-200 so the breaker sees
        the failure (never masks a challenge/empty body)."""
        session = self._sessions[slot]
        full = f"{url}?page={page}" if page and page > 1 else url
        resp = session.get(full, headers=_HEADERS, impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {full}")
        # Serve UTF-8 explicitly so accented model/version text survives curl_cffi's encoding guess.
        return resp.content.decode("utf-8", "replace")

    async def fetch_page_async(self, governed_fetch, url: str, *, page: int) -> str:
        """Lease a pool slot, fetch `page` THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, page=page, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# Recipe (persisted to countries/ES/recipes/<cdp_code>.yaml AND docs datalayer .md).
# ---------------------------------------------------------------------------

OK_PLATFORM_RECIPE = {
    "version": 1,
    "source": "okmobility.com",
    "group": "rentacar_vo",
    "scope": "rentacar_vo wholesale (OK Mobility SSR HTML used-stock storefront, per-page paginated)",
    "engine": "curl_cffi+chrome131_impersonate+ssr_html_embedded_card_markup(GET)",
    "access": ("OPEN server-rendered HTML (Chrome TLS fingerprint; no proxy, no browser, no cookie "
               "warm-up). '/en/' locale serves; '/es/' 404s. Public site carries an Opticks bot "
               "beacon -> defense_tier t1_soft; the listing HTML itself is unwalled."),
    "data_surface": "sitemap",
    "surface_intent": "ssr_html_embedded_card_markup",
    "endpoint": "GET https://okmobility.com/en/buy-car/used?page=N",
    "enumeration": "?page=1..N (~35 cars/SSR page); id=\"total-cars\" declares the full stock (172 live)",
    "platform_entity": ("kind=rent_a_car_vo, province_code=07 (Palma HQ), is_tier1=FALSE, "
                        "defense_tier=t1_soft, source_group=rentacar_vo, role=chain, family=okmobility"),
    "ownership": ("the rent-a-car COMPANY is the singular selling point -> it OWNS every ex-fleet "
                  "car (vehicle.entity_ulid=company). platform_listing edge=company<->vehicle records "
                  "the listing. owner entity == platform entity (single-operator storefront)."),
    "branches": ("showroom network recorded for a future per-branch pass (NOT exposed per-car on the "
                 "list surface): Palma/Gran Via Asima+Levante+Manacor (07009/07007/07500), "
                 "Barcelona/El Prat+Calonge (08), Bilbao/Sestao (48910), Cuenca (16004), Jaén (23009)"),
    "field_map": {
        "deep_link": "a.own-car-card href (absolute /en/buy-car/used/{brand}/{model}/{trim}/{sku}/{id})",
        "listing_ref": "a.own-car-card data-carid (internal OK Mobility car id; stable dedup key)",
        "progiciel_id": "URL tail id (data-carProgicielId; stock/progiciel id)",
        "make_model": "div.car-name (make = first token; model = remainder)",
        "version": "div.car-motorization (e.g. '1.0 TSI 95')",
        "summary": "div.car-summary spans = [year | km | fuel | transmission]",
        "price": "div.paying-prices div.big-cipher-text (ES thousands; current price)",
        "prev_price": "div.deleted-small-cipher-text (previous price -> price-drop delta)",
        "fuel": "car-summary[2] (Gasoline/Diesel/Electric/Hybrid; raw EN label)",
        "transmission": "car-summary[3] (Manual/Automatic; raw EN label)",
        "photo_url": "div.car-image data-srcbg (cdn.okrentacar.es — ex-rental fleet CDN)",
    },
    "caveats": {
        "locale": "'/en/' serves HTTP 200; '/es/' 404s on this surface.",
        "encoding": "the € glyph is UTF-8 over the wire; decode content as UTF-8 (prices are clean digits).",
        "no_per_branch_geo": ("the listing surface does not attribute a car to a showroom branch; the "
                              "company is anchored to its HQ province (07) and owns the car. A per-branch "
                              "owner is NOT fabricated; the detail page carries store=<id> for a later pass."),
        "members": ("group rentacar_vo also includes Centauro (centauro.net, Next.js app — needs an XHR "
                    "probe), Record Go (recordgoocasion.es, WordPress sitemap + SSR PDP), Sixt/Europcar/"
                    "Goldcar — added as further members under this same architecture."),
    },
}


# ---------------------------------------------------------------------------
# DB layer (mirrors coches_net_wholesale / oem_audi_wholesale: ensure platform, upsert company-owned
# vehicles, link edge, emit delta, all idempotent ON CONFLICT, BULK unnest ingest).
# ---------------------------------------------------------------------------


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the OK Mobility company entity + platform_meta exist. Returns the entity
    ulid. kind='rent_a_car_vo', source_group='rentacar_vo', role='chain', anchored to HQ province 07.
    data_surface='sitemap' (the schema-valid literal closest to a paginated SSR-HTML surface; the
    precise 'ssr_html_embedded_card_markup' intent is kept in surface_detail)."""
    code = ok_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               sells_cars, defense_tier, source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,$3::entity_kind,$4,$5,$6,$7,$8::waf_kind,FALSE,'active','platform_label',
               TRUE,$9::defense_tier,$10::source_group,$11::entity_role,$12, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, website_waf = EXCLUDED.website_waf,
               defense_tier = EXCLUDED.defense_tier, source_group = EXCLUDED.source_group,
               role = EXCLUDED.role, kind = EXCLUDED.kind, legal_name = EXCLUDED.legal_name,
               province_code = EXCLUDED.province_code""",
        eulid, code, OK_KIND, OK_LEGAL_NAME, OK_TRADE_NAME, OK_HQ_PROVINCE, OK_WEBSITE,
        OK_WAF, OK_DEFENSE_TIER, OK_SOURCE_GROUP, OK_ROLE, OK_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, OK_SOURCE_KEY, OK_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'sitemap',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"endpoint": ENDPOINT, "host": host_of(ENDPOINT), "method": "GET",
                           "enumeration": "?page=N", "declared_total_id": "total-cars",
                           "surface_intent": "ssr_html_embedded_card_markup",
                           "engine": "curl_cffi/chrome131_impersonate"}),
        OK_FAMILY)
    return eulid


# The bulk statements — ONE round-trip per table per window (unnest-based multi-row upsert),
# byte-for-byte the same idempotency the marketplace connectors use. A re-run of an already-harvested
# window adds 0 rows and 0 events. Here the owner of EVERY car is the single company entity, so the
# owner upsert is the platform entity itself (no per-car owner table — the edge already records it).

_BULK_INSERT_VEHICLES = """
INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model,
        year, km, price, fuel, transmission, photo_url, vin_ref, status)
SELECT u.vehicle_ulid, u.entity_ulid, u.deep_link, u.title, u.make, u.model,
       u.year, u.km, u.price, u.fuel, u.transmission, u.photo_url, u.vin_ref, 'available'
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[], $5::text[], $6::text[],
              $7::int[], $8::int[], $9::numeric[], $10::text[], $11::text[], $12::text[],
              $13::text[])
       AS u(vehicle_ulid, entity_ulid, deep_link, title, make, model,
            year, km, price, fuel, transmission, photo_url, vin_ref)
ON CONFLICT (entity_ulid, deep_link) DO NOTHING
"""

_BULK_TOUCH_VEHICLES = """
UPDATE vehicle v SET last_seen = now(), status = 'available'
  FROM unnest($1::text[]) AS u(vehicle_ulid)
 WHERE v.vehicle_ulid = u.vehicle_ulid
"""

_BULK_UPSERT_EDGES = """
INSERT INTO platform_listing (vehicle_ulid, platform_entity_ulid, listing_url,
        listing_ref, platform_price, status, first_seen, last_seen)
SELECT u.vehicle_ulid, $5, u.listing_url, u.listing_ref, u.platform_price,
       'listed', now(), now()
  FROM unnest($1::text[], $2::text[], $3::text[], $4::numeric[])
       AS u(vehicle_ulid, listing_url, listing_ref, platform_price)
ON CONFLICT (vehicle_ulid, platform_entity_ulid)
  DO UPDATE SET last_seen = now(), status = 'listed',
                platform_price = EXCLUDED.platform_price,
                listing_ref = EXCLUDED.listing_ref
RETURNING (xmax = 0) AS inserted
"""

_BULK_INSERT_EVENTS = """
INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type,
        old_value, new_value)
SELECT u.event_ulid, u.vehicle_ulid, u.entity_ulid, 'NEW', NULL, u.new_value::jsonb
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[])
       AS u(event_ulid, vehicle_ulid, entity_ulid, new_value)
"""


def _parse_window(pages: list[tuple[int, str]], seen_ids: set, harvested_cageable: set,
                  company_ulid: str, stats: dict) -> list[Vehicle]:
    """Parse every card across the window IN PAGE ORDER — pure CPU, no SQL. Cross-page dedup on the
    internal car id (a paginated SSR walk can repeat a card across a window boundary if stock shifts
    mid-crawl). The cageable truth is (company_ulid, deep_link) since the company owns every car."""
    out: list[Vehicle] = []
    for _page, html in pages:
        vehicles, declared = parse_page(html)
        if stats["declared_full"] is None and declared is not None:
            stats["declared_full"] = declared
        for v in vehicles:
            stats["items_seen"] += 1
            if v.listing_ref and v.listing_ref in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue
            if v.listing_ref:
                seen_ids.add(v.listing_ref)
            if not v.deep_link:
                stats["no_link_skipped"] += 1
                continue
            if v.prev_price is not None and v.price is not None and v.prev_price > v.price:
                stats["price_drops_captured"] += 1
            harvested_cageable.add((company_ulid, v.deep_link))
            out.append(v)
    return out


async def _ingest_window(conn: asyncpg.Connection, company_ulid: str,
                         pages: list[tuple[int, str]], seen_ids: set,
                         harvested_cageable: set, stats: dict) -> None:
    """BULK-ingest a whole concurrent page-window in ONE transaction with set-based SQL. The owner of
    every car is the single company entity, so there is no per-car owner upsert — the cars insert
    straight under company_ulid, the edge records the listing, the NEW event fires for genuinely new
    vehicles only. Idempotency/delta/VAM semantics are byte-identical to the marketplace connectors."""
    cage = _parse_window(pages, seen_ids, harvested_cageable, company_ulid, stats)
    if not cage:
        return

    async with conn.transaction():
        # dedup cars within the window by (company_ulid, deep_link).
        cars: dict[tuple[str, str], Vehicle] = {}
        for v in cage:
            key = (company_ulid, v.deep_link)
            if key not in cars:
                cars[key] = v

        car_keys = list(cars.keys())
        v_links = [k[1] for k in car_keys]
        existing: dict[tuple[str, str], str] = {
            (row["entity_ulid"], row["deep_link"]): row["vehicle_ulid"]
            for row in await conn.fetch(
                """SELECT vehicle_ulid, entity_ulid, deep_link FROM vehicle
                   WHERE entity_ulid = $1 AND deep_link = ANY($2::text[])""",
                company_ulid, v_links)
        }

        vehicle_ulid_for: dict[tuple[str, str], str] = {}
        new_keys: list[tuple[str, str]] = []
        touch_ulids: list[str] = []
        for key in car_keys:
            ex = existing.get(key)
            if ex is not None:
                vehicle_ulid_for[key] = ex
                touch_ulids.append(ex)
            else:
                vehicle_ulid_for[key] = ulid()
                new_keys.append(key)

        if touch_ulids:
            await conn.execute(_BULK_TOUCH_VEHICLES, touch_ulids)

        if new_keys:
            ins = [(vehicle_ulid_for[k], k[0], cars[k]) for k in new_keys]
            await conn.execute(
                _BULK_INSERT_VEHICLES,
                [x[0] for x in ins], [x[1] for x in ins], [x[2].deep_link for x in ins],
                [x[2].title for x in ins], [x[2].make for x in ins], [x[2].model for x in ins],
                [x[2].year for x in ins], [x[2].km for x in ins], [x[2].price for x in ins],
                [x[2].fuel for x in ins], [x[2].transmission for x in ins],
                [x[2].photo_url for x in ins], [x[2].listing_ref for x in ins])
            landed = {
                (row["entity_ulid"], row["deep_link"]): row["vehicle_ulid"]
                for row in await conn.fetch(
                    """SELECT vehicle_ulid, entity_ulid, deep_link FROM vehicle
                       WHERE vehicle_ulid = ANY($1::text[])""",
                    [vehicle_ulid_for[k] for k in new_keys])
            }
            confirmed_new = []
            for k in new_keys:
                real = landed.get(k)
                if real is not None and real == vehicle_ulid_for[k]:
                    confirmed_new.append(k)
                elif real is not None:
                    vehicle_ulid_for[k] = real
                else:
                    row = await conn.fetchrow(
                        "SELECT vehicle_ulid FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2",
                        k[0], k[1])
                    if row is not None:
                        vehicle_ulid_for[k] = row["vehicle_ulid"]
        else:
            confirmed_new = []

        stats["cars_caged"] += len(car_keys)
        stats["new_cars"] += len(confirmed_new)

        # ---- EDGES: one batched upsert; RETURNING (xmax=0) counts genuinely new edges.
        e_vehicles = [vehicle_ulid_for[k] for k in car_keys]
        e_urls = [cars[k].deep_link for k in car_keys]
        e_refs = [cars[k].listing_ref for k in car_keys]
        e_prices = [cars[k].price for k in car_keys]
        edge_rows = await conn.fetch(_BULK_UPSERT_EDGES, e_vehicles, e_urls, e_refs,
                                     e_prices, company_ulid)
        stats["edges_created"] += sum(1 for row in edge_rows if row["inserted"])

        # ---- NEW delta events — only for genuinely new vehicles, price-drop preserved.
        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                v = cars[k]
                payload = {"price": v.price, "title": v.title, "platform": OK_TRADE_NAME}
                if v.prev_price is not None and v.price is not None and v.prev_price > v.price:
                    payload["price_drop"] = {"from": v.prev_price, "to": v.price,
                                             "amount": v.prev_price - v.price}
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities, ev_payloads)
            stats["new_events"] += len(confirmed_new)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# okmobility.com is a first-party storefront; a small window keeps the governor's per-host bucket
# saturated without out-pacing it. The bucket is the limiter, not the window.
DEFAULT_CONCURRENCY = 4


async def harvest(max_pages: int = DEFAULT_MAX_PAGES,
                  concurrency: int = DEFAULT_CONCURRENCY,
                  limit: int | None = None) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    if limit is not None and limit > 0:
        # ~35 cars/page; convert a target car count to a page cap.
        limit_pages = max(1, math.ceil(limit / 35))
        max_pages = min(max_pages, limit_pages)
    fetcher = OkFetcher(pool_size=concurrency)
    stats = {
        "pages_fetched": 0, "items_seen": 0, "cars_caged": 0, "new_cars": 0,
        "edges_created": 0, "new_events": 0, "price_drops_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "no_link_skipped": 0,
        "concurrency": concurrency, "max_pages": max_pages,
    }
    harvested_cageable: set[tuple[str, str]] = set()

    if await is_open(conn, OK_SOURCE_KEY):
        print(f"[group_rentacar_vo] breaker OPEN for {OK_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, storefront still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": OK_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        # GeoResolver is loaded for parity with the family/marketplace connectors and to validate the
        # HQ province exists; the company is anchored to province 07 directly (no per-car geo here).
        await GeoResolver.load(conn)
        company_ulid = await ensure_platform_entity(conn)
        platform_code = ok_platform_cdp_code()
        print(f"[group_rentacar_vo] company entity ready: {platform_code} (ulid={company_ulid}) "
              f"kind={OK_KIND} group={OK_SOURCE_GROUP} role={OK_ROLE} tier={OK_DEFENSE_TIER} "
              f"family={OK_FAMILY} hq_province={OK_HQ_PROVINCE}")
        print(f"[group_rentacar_vo] governor paces host {host_of(ENDPOINT)} (per-host token bucket).")
        print(f"[group_rentacar_vo] CONCURRENT SSR drain: window={concurrency} pages in flight. "
              f"Target = {max_pages} pages (~35 cars/page).")

        seen_ids: set[str] = set()
        edges_before = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", company_ulid)

        stop = False
        next_page = 1
        while next_page <= max_pages and not stop:
            window = list(range(next_page, min(next_page + concurrency, max_pages + 1)))
            next_page = window[-1] + 1

            results = await asyncio.gather(
                *(fetcher.fetch_page_async(governed_fetch, ENDPOINT, page=p) for p in window),
                return_exceptions=True,
            )

            window_pages: list[tuple[int, str]] = []
            for page, data in zip(window, results):
                if isinstance(data, Exception):
                    fetch_error = str(data)
                    last_http = fetcher.last_status
                    print(f"[group_rentacar_vo] page {page} fetch failed ({data}); stopping drain honestly.")
                    stop = True
                    break
                vehicles, _ = parse_page(data)
                if not vehicles:
                    print(f"[group_rentacar_vo] page {page}: no cards; stopping (data boundary reached).")
                    stop = True
                    break
                window_pages.append((page, data))

            if window_pages:
                await _ingest_window(conn, company_ulid, window_pages, seen_ids,
                                     harvested_cageable, stats)
                stats["pages_fetched"] += len(window_pages)
                first_p, last_p = window_pages[0][0], window_pages[-1][0]
                print(f"[group_rentacar_vo] window pages {first_p}-{last_p}: "
                      f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                      f"edges={stats['edges_created']} drops={stats['price_drops_captured']}")

        recipe_path = write_recipe(platform_code, OK_PLATFORM_RECIPE)
        print(f"[group_rentacar_vo] recipe written: {recipe_path}")

        # VAM count quorum — THREE orthogonal like-with-like paths, all "distinct cageable cars":
        #   db_edges           = platform_listing rows for OK Mobility  (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join     (DB read truth)
        #   harvested_cageable = distinct (company, deep_link) pulled     (harvest truth)
        db_edges = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", company_ulid)
        db_join_vehicles = await conn.fetchval(
            """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               JOIN entity e ON e.entity_ulid = v.entity_ulid
               WHERE pl.platform_entity_ulid=$1""", company_ulid)
        harvested_cageable_n = len(harvested_cageable)
        verdict = await record_count_verdict(
            conn, subject_type="platform_slice", subject_key=platform_code,
            claim="distinct cageable cars (harvest) == platform_listing edges == join-reachable vehicles",
            paths={"db_edges": db_edges, "db_join_vehicles": db_join_vehicles,
                   "harvested_cageable": harvested_cageable_n},
            tolerance=0.0)
        stats["verdict"] = verdict
        stats["db_edges"] = db_edges
        stats["db_join_vehicles"] = db_join_vehicles
        stats["harvested_cageable"] = harvested_cageable_n
        stats["harvested_distinct_ids"] = len(seen_ids)
        stats["edges_new_this_run"] = db_edges - (edges_before or 0)
        stats["platform_code"] = platform_code
        stats["platform_ulid"] = company_ulid
        stats["recipe_path"] = str(recipe_path)

        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, OK_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, OK_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[group_rentacar_vo] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("RENTACAR_VO WHOLESALE HARVEST — OK MOBILITY — REPORT")
    print("=" * 64)
    print(f"  company cdp_code      : {stats.get('platform_code')}")
    print(f"  group / kind / role   : rentacar_vo / rent_a_car_vo / chain (tier t1_soft, family okmobility)")
    print(f"  declared full (source): {stats.get('declared_full')}")
    print(f"  concurrency (window)  : {stats.get('concurrency')} pages in flight")
    print(f"  target pages          : {stats.get('max_pages')}")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page, data-carid dedup)")
    print(f"  no-link skipped       : {stats['no_link_skipped']}")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new) — owned by OK Mobility")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total = {stats.get('db_edges')}, +{stats.get('edges_new_this_run')} this run)")
    print(f"  price drops captured  : {stats['price_drops_captured']}")
    print(f"  NEW delta events      : {stats['new_events']}")
    print("  --- VAM count quorum (like-with-like, this slice) ---")
    print(f"  harvested_cageable    : {stats.get('harvested_cageable')}")
    print(f"  db_edges              : {stats.get('db_edges')}")
    print(f"  db_join_vehicles      : {stats.get('db_join_vehicles')}")
    print(f"  VAM verdict           : {stats.get('verdict')}")
    print(f"  health status         : {stats.get('health_status')} / breaker {stats.get('breaker_state')}")
    print(f"  recipe                : {stats.get('recipe_path')}")
    print("=" * 64)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="rentacar_vo wholesale harvester (OK Mobility SSR used-stock storefront)")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"SSR pages to harvest (~35 cars/page); default {DEFAULT_MAX_PAGES} (drains ~172)")
    parser.add_argument("--limit", type=int, default=None,
                        help="optional target car count; converted to a page cap. Tighter of --pages/--limit wins.")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=f"pages fetched in parallel per window; default {DEFAULT_CONCURRENCY}.")
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.pages, args.concurrency, args.limit))
    _print_report(stats)


if __name__ == "__main__":
    main()
