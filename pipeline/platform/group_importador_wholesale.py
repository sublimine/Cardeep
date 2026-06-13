"""importador WHOLESALE harvester — populate the EMPTY kind='importador' channel.

The keyword census (docs/research/KEYWORD_CHANNEL_MAP.md §NUEVO-3) surfaced a real,
reachable family of IMPORT OPERATORS — dealers whose whole proposition is selling used
cars IMPORTED (mostly from Germany) at a 10-20% saving. The taxonomy already carries
`kind='importador'` but it held ZERO entities (verified live 2026-06-13: `SELECT count(*)
FROM entity WHERE kind='importador'` = 0). This connector is the channel's FIRST writer.

Of the census candidates, only ONE exposes its OWN-SITE stock on a free, curl_cffi-reachable
surface — the rest are WordPress lead-gen / info sites WITHOUT a machine-readable own stock
catalog (declared honestly in the recipe + the connector report). The reachable member:

  1. MODRIVE (modrive.com) — kind='importador', source_group='long_tail_web', role='standalone_pos'.
     CHAIN/IMPORTER-AS-OWNER: the SSR listing does not attribute a car to a physical branch, so
     the importer OWNS every car it lists (owner entity == platform entity), exactly like
     OcasionPlus / Clicars in group_vo_chains_wholesale:
       MODRIVE (the importer)        -> entity, kind='importador' (+ platform_meta)  [SELLING POINT]
       each CAR                      -> vehicle, OWNED BY the importer (entity_ulid=importer)
       the car on the importer site  -> platform_listing edge (importer_entity <-> vehicle)
     Surface (probed live 2026-06-13, curl_cffi chrome131 + Playwright network capture): the
     server-rendered `/coches-segunda-mano/` page emits a schema.org JSON-LD `@graph` whose
     `ItemList` carries 19 `Vehicle` objects, each with name (make+model), image, url (per-car
     deep link whose tail `-{id}/` is the native listing_ref) and offers.price (EUR). A page-level
     `Product.offers` `AggregateOffer` declares `offerCount`. No WAF -> defense_tier t0_open;
     chrome131 serves it cleanly. The visual grid declares "2021 Coches" total, but that FULL
     catalog is rendered by an AutoUncle third-party widget (assets.autouncle.com GraphQL) — a
     DIFFERENT host, NOT MODRIVE's own first-party surface; harvesting it would scrape AutoUncle's
     shared multi-dealer feed, not the operator's own stock. We therefore harvest MODRIVE's OWN
     SSR JSON-LD ItemList (the operator's first-party surface, €0, curl_cffi) and record the
     declared 2021 + the AutoUncle widget honestly in the recipe as the deeper future surface.

This connector mirrors group_vo_chains_wholesale (chain-as-owner member) and coches_net_wholesale
EXACTLY — same governor choke point, same GeoResolver, same idempotent ON CONFLICT BULK unnest
ingest, same NEW-delta events, same VAM count quorum, same S-HEALTH heartbeat/breaker. It is the
SAME architecture parameterised for a new kind, not a fork.

The pagination of MODRIVE's SSR JSON-LD ItemList is a FIXED featured block (page/2/ returns the
same id-set as page 1 — the real catalog paginates only in the AutoUncle widget, not the SSR
JSON-LD). The harvester therefore reads page 1 and stops when the next page adds no new ids — the
honest boundary of the own-site SSR surface (declared in the recipe).

Run: python -m pipeline.platform.group_importador_wholesale --pages 3
     python -m pipeline.platform.group_importador_wholesale --members modrive --pages 3
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
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

DSN = os.environ.get("CARDEEP_DSN",
                     "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# ---------------------------------------------------------------------------
# importador group identity (the 0016 multi-axis classification).
# ---------------------------------------------------------------------------
GROUP_SOURCE_GROUP = "long_tail_web"     # source_group: import operators are own-site long-tail web.
GROUP_ROLE = "standalone_pos"            # entity_role: an importer is its own single selling point.
IMPORTER_KIND = "importador"             # entity_kind: the channel this connector POPULATES.

_IMPERSONATE = "chrome131"
_TIMEOUT = 40
PLATFORM_PROVINCE_SENTINEL = "00"        # national segment for an importer's cdp_code.

DEFAULT_MAX_PAGES = 3
DEFAULT_CONCURRENCY = 3

_LD_RE = re.compile(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S)


def _to_int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


# ===========================================================================
# Parsed shapes
# ===========================================================================


@dataclass
class Vehicle:
    """A car parsed from an importer's data-layer item (REAL field map per member)."""
    deep_link: str
    listing_ref: str            # native ad/stock id (the deep-link '-{id}/' tail)
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    prev_price: float | None    # previous price -> price-drop delta (None where the source omits it)
    fuel: str | None
    transmission: str | None
    photo_url: str | None


@dataclass
class CageRow:
    """One fully-parsed, owner-resolved car ready for the bulk cage. The importer entity itself
    owns the car (importer-as-owner model), so owner_kind is always IMPORTER_KIND and the owner is
    the importer's own cdp_code."""
    owner_cdp: str
    owner_kind: str
    owner_name: str | None
    owner_province: str | None
    owner_muni: str | None
    source_ref: str
    vehicle: Vehicle


# ===========================================================================
# MODRIVE member (importer-as-owner model; SSR JSON-LD ItemList of Vehicle)
# ===========================================================================
#
# modrive.com is a German-import used-car operator. The SSR `/coches-segunda-mano/` page emits a
# schema.org JSON-LD `@graph` whose ItemList holds 19 ListItem->Vehicle objects (name, image, url,
# offers.price) and a page-level Product.AggregateOffer.offerCount. The deep-link tail '-{id}/' is
# the native listing_ref. No WAF -> t0_open. The full 2021-car catalog is an AutoUncle third-party
# widget (assets.autouncle.com GraphQL) — a DIFFERENT host, not MODRIVE's own surface; we harvest
# the operator's own SSR ItemList and record the AutoUncle widget honestly in the recipe.

MOD_DOMAIN = "modrive.com"
MOD_LEGAL_NAME = "MODRIVE"
MOD_TRADE_NAME = "MODRIVE"
MOD_SOURCE_KEY = "group_importador_modrive"
MOD_FAMILY = "modrive"
MOD_SRP = "https://www.modrive.com/coches-segunda-mano/"
MOD_PAGE_SIZE = 19  # ListItem->Vehicle objects per SSR JSON-LD ItemList page.
MOD_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.modrive.com/",
}

_MOD_ID_RE = re.compile(r"-(\d+)/?$")


def importer_cdp_code(domain: str) -> str:
    """An importer's immutable cdp_code, built from the bare domain identity (canonical_key
    'domain:<domain>') with the national province segment '00'. Mirrors chain_cdp_code() so every
    own-site operator mints codes the same way."""
    key = f"domain:{domain}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


def _mod_listing_ref(url: str) -> str:
    """The MODRIVE deep link is '.../coches-segunda-mano/{slug}-{id}/'. The numeric tail before the
    trailing '/' is the native stock id. Falls back to the cleaned url when no clean tail exists."""
    m = _MOD_ID_RE.search(url or "")
    if m:
        return m.group(1)
    return (url or "").rstrip("/")


def _split_make_model(name: str | None) -> tuple[str | None, str | None]:
    """MODRIVE's Vehicle.name is 'Make Model version...' (e.g. 'BMW Serie 1 116d'). The first token
    is the make; the remainder is the model+version. Never fabricated — make/model are both None
    when the name is empty."""
    if not name:
        return (None, None)
    parts = name.strip().split(" ", 1)
    make = parts[0] or None
    model = parts[1] if len(parts) > 1 else None
    return (make, model)


def parse_modrive_page(html_text: str) -> tuple[list[Vehicle], int | None]:
    """Parse a MODRIVE SSR page -> (vehicles, declared_total). The JSON-LD `@graph` holds one
    `ItemList` of 19 ListItem->Vehicle objects and a page-level `Product` whose AggregateOffer
    declares offerCount (the SSR-surface count). Each Vehicle carries name (make+model), image,
    url (deep link) and offers.price; year/km/fuel/transmission are NOT on this surface (the
    operator omits them from the JSON-LD), so they are left None — never fabricated."""
    declared: int | None = None
    vehicles: list[Vehicle] = []
    for block in _LD_RE.findall(html_text):
        try:
            d = json.loads(block)
        except (ValueError, TypeError):
            continue
        graph = d.get("@graph") if isinstance(d, dict) else None
        nodes = graph if isinstance(graph, list) else ([d] if isinstance(d, dict) else [])
        for node in nodes:
            if not isinstance(node, dict):
                continue
            ntype = node.get("@type")
            # full-stock count on the page-level Product's AggregateOffer.
            if ntype == "Product":
                offers = node.get("offers") or {}
                if isinstance(offers, dict) and offers.get("@type") == "AggregateOffer":
                    declared = _to_int(offers.get("offerCount")) or declared
            if ntype != "ItemList":
                continue
            for el in node.get("itemListElement", []):
                if not isinstance(el, dict):
                    continue
                item = el.get("item") if isinstance(el.get("item"), dict) else el
                if not isinstance(item, dict):
                    continue
                itype = item.get("@type")
                is_vehicle = itype == "Vehicle" or (isinstance(itype, list) and "Vehicle" in itype)
                if not is_vehicle:
                    continue
                url = item.get("url") or item.get("@id")
                if not url:
                    continue
                offers = item.get("offers") or {}
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                price = offers.get("price") if isinstance(offers, dict) else None
                try:
                    price = float(price) if price is not None else None
                except (TypeError, ValueError):
                    price = None
                if price is not None and price <= 0:
                    price = None
                name = item.get("name")
                make, model = _split_make_model(name)
                image = item.get("image")
                if isinstance(image, list):
                    image = image[0] if image else None
                vehicles.append(Vehicle(
                    deep_link=url, listing_ref=_mod_listing_ref(url), title=name,
                    make=make, model=model, year=None, km=None, price=price,
                    prev_price=None, fuel=None, transmission=None, photo_url=image))
    return vehicles, declared


# ===========================================================================
# Member descriptor
# ===========================================================================


@dataclass
class Member:
    key: str
    domain: str
    legal_name: str
    trade_name: str
    family: str
    data_surface: str           # platform_meta data_surface literal (schema-valid)
    surface_intent: str
    endpoint: str
    host: str
    page_size: int
    recipe: dict


MODRIVE_RECIPE = {
    "version": 1,
    "source": "modrive.com",
    "group": "importador",
    "scope": "importador wholesale (MODRIVE SSR JSON-LD ItemList of Vehicle, own-site surface)",
    "engine": "curl_cffi+chrome131_impersonate+ssr_jsonld_itemlist(GET)",
    "access": ("OPEN server-rendered HTML carrying schema.org JSON-LD (Chrome TLS fingerprint; no "
               "proxy, no browser, no cookie warm-up). No WAF -> defense_tier t0_open."),
    "data_surface": "json_ld",
    "surface_intent": "ssr_jsonld_itemlist",
    "endpoint": "GET https://www.modrive.com/coches-segunda-mano/",
    "enumeration": ("the SSR JSON-LD ItemList is a FIXED featured block of 19 Vehicle objects; "
                    "page/N/ returns the SAME id-set (verified live) — the full catalog paginates "
                    "ONLY in the AutoUncle widget, not the SSR JSON-LD. The harvester reads the "
                    "own-site ItemList and stops when the next page adds no new ids."),
    "platform_entity": ("kind=importador, province_code=NULL (sentinel 00 in cdp_code), is_tier1=FALSE, "
                        "defense_tier=t0_open, source_group=long_tail_web, role=standalone_pos, "
                        "family=modrive"),
    "ownership": ("IMPORTER-AS-OWNER: the SSR listing does not attribute a car to a physical branch, "
                  "so the importer OWNS every car (vehicle.entity_ulid=importer). platform_listing "
                  "edge=importer<->vehicle. owner entity == platform entity."),
    "field_map": {
        "deep_link": "ItemList.itemListElement[].item.url (per-car PDP)",
        "listing_ref": "deep-link numeric tail before trailing '/' (native stock id)",
        "make": "Vehicle.name first token", "model": "Vehicle.name remainder",
        "title": "Vehicle.name", "price": "Vehicle.offers.price (EUR)",
        "photo_url": "Vehicle.image[0]",
        "declared_full": "page-level Product.offers(AggregateOffer).offerCount",
    },
    "caveats": {
        "own_surface_only": ("MODRIVE's OWN SSR JSON-LD ItemList is harvested (the operator's "
                             "first-party surface). The visual grid declares 2021 cars total, but "
                             "that FULL catalog is rendered by an AutoUncle THIRD-PARTY widget "
                             "(assets.autouncle.com GraphQL) on a different host — NOT the "
                             "operator's own surface; harvesting it would scrape AutoUncle's shared "
                             "multi-dealer feed, not MODRIVE's own stock. Recorded honestly as the "
                             "deeper future surface, not silently scraped."),
        "missing_fields": ("year/km/fuel/transmission are NOT in the JSON-LD ItemList (the operator "
                           "omits them); they are left NULL, never fabricated. A per-PDP pass could "
                           "enrich them later."),
        "data_surface_label": "schema enum has 'json_ld'; surface_intent 'ssr_jsonld_itemlist' is precise.",
    },
}


def build_modrive() -> Member:
    return Member(
        key=MOD_SOURCE_KEY, domain=MOD_DOMAIN, legal_name=MOD_LEGAL_NAME,
        trade_name=MOD_TRADE_NAME, family=MOD_FAMILY,
        data_surface="json_ld", surface_intent="ssr_jsonld_itemlist", endpoint=MOD_SRP,
        host=host_of(MOD_SRP), page_size=MOD_PAGE_SIZE, recipe=MODRIVE_RECIPE)


MEMBER_BUILDERS = {"modrive": build_modrive}


# ===========================================================================
# Fetch: a POOL of fingerprint-coherent curl_cffi sessions, routed THROUGH the governor.
# ===========================================================================


class ImporterFetcher:
    """One curl_cffi Session per concurrency slot (a single shared session is not thread-safe under
    the governor's to_thread fetch). The governor's per-host bucket bounds the aggregate rate, so
    the pool widens parallelism WITHOUT out-pacing the host (the bucket is the limiter)."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch_ssr_page(self, url: str, headers: dict, *, page: int = 1, slot: int = 0) -> str:
        """Synchronous GET of one server-rendered HTML SRP page on pool session `slot`. `page` rides
        as /page/N/ for page>1 (MODRIVE WordPress pagination). Returns raw HTML (JSON-LD embedded).
        Raises on non-200 so the breaker sees throttling."""
        session = self._sessions[slot]
        if page and page > 1:
            full = url.rstrip("/") + f"/page/{page}/"
        else:
            full = url
        resp = session.get(full, headers=headers, impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {full}")
        return resp.content.decode("utf-8", "replace")

    def fetch_modrive(self, url: str, *, page: int = 1, slot: int = 0) -> str:
        """Synchronous GET of one MODRIVE SSR page (/page/N/) on pool session `slot`. Raw HTML."""
        return self.fetch_ssr_page(url, MOD_HEADERS, page=page, slot=slot)

    async def fetch_async(self, governed_fetch, url: str, **kw) -> str:
        """Lease a pool slot, fetch THROUGH the governor on that slot, release it. `governed_fetch`
        is governor().wrap_fetch_text(sync_callable); the governor paces the host then runs the
        synchronous fetch off the event loop with `slot` forwarded untouched."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, slot=slot, **kw)
        finally:
            self._free.put_nowait(slot)


# ===========================================================================
# DB layer — ensure the importer entity, bulk-insert vehicles + edges + NEW events,
# all idempotent ON CONFLICT (BULK unnest). Mirrors group_vo_chains chain-as-owner path.
# ===========================================================================


async def ensure_importer_entity(conn: asyncpg.Connection, m: Member) -> str:
    """Idempotently ensure the importer's entity + platform_meta exist. Returns the importer entity
    ulid. kind='importador', source_group='long_tail_web', role='standalone_pos', province NULL
    (national; '00' in cdp_code). is_tier1=FALSE, defense_tier=t0_open (unwalled own surface)."""
    code = importer_cdp_code(m.domain)
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               sells_cars, defense_tier, source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,$3::entity_kind,$4,$5,NULL,$6,'none'::waf_kind,FALSE,'active','platform_label',
               TRUE,'t0_open'::defense_tier,$7::source_group,$8::entity_role,$9, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, defense_tier = EXCLUDED.defense_tier,
               source_group = EXCLUDED.source_group, role = EXCLUDED.role,
               kind = EXCLUDED.kind, legal_name = EXCLUDED.legal_name, website = EXCLUDED.website""",
        eulid, code, IMPORTER_KIND, m.legal_name, m.trade_name, m.domain,
        GROUP_SOURCE_GROUP, GROUP_ROLE, m.key)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, m.key, m.domain)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,$2,$3::jsonb,FALSE,FALSE,$4)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, m.data_surface,
        json.dumps({"endpoint": m.endpoint, "host": m.host, "method": "GET",
                    "owner_model": "importer", "page_size": m.page_size,
                    "surface_intent": m.surface_intent,
                    "engine": "curl_cffi/chrome131_impersonate"}),
        m.family)
    return eulid


# The bulk statements — ONE round-trip per table per window (unnest multi-row upsert), byte-for-byte
# the same idempotency the marketplace/group connectors use. A re-run adds 0 rows and 0 events.

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


def resolve_cage_rows(vehicles: list[Vehicle], importer_cdp: str, importer_name: str,
                      domain: str, seen_ids: set, harvested_cageable: set,
                      stats: dict) -> list[CageRow]:
    """Resolve every parsed vehicle to its owner — pure CPU, no SQL. Importer-as-owner: every car is
    owned by the importer entity itself (national, province NULL). Cross-page dedup on listing_ref;
    the cageable truth is the distinct (owner_cdp, deep_link) pair (like-with-like vs DB edges)."""
    rows: list[CageRow] = []
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
        harvested_cageable.add((importer_cdp, v.deep_link))
        rows.append(CageRow(owner_cdp=importer_cdp, owner_kind=IMPORTER_KIND,
                            owner_name=importer_name, owner_province=None,
                            owner_muni=None, source_ref=domain, vehicle=v))
    return rows


async def ingest_window(conn: asyncpg.Connection, m: Member, importer_ulid: str, importer_cdp: str,
                        vehicles: list[Vehicle], seen_ids: set, harvested_cageable: set,
                        stats: dict) -> None:
    """BULK-ingest a window of parsed cars in ONE transaction with set-based SQL. The importer owns
    every car, so cars cage straight under importer_ulid. Vehicles split existing/new (one SELECT),
    bulk-touch + bulk-insert, edges bulk-upsert (RETURNING counts new edges), NEW events fire for
    genuinely new vehicles only. Idempotency/delta/VAM semantics are byte-identical to
    coches_net_wholesale / group_vo_chains_wholesale."""
    cage = resolve_cage_rows(vehicles, importer_cdp, m.trade_name, m.domain, seen_ids,
                             harvested_cageable, stats)
    if not cage:
        return

    async with conn.transaction():
        # ---- attach owner ulid to each car; dedup within the window by (owner_ulid, deep_link).
        cars: dict[tuple[str, str], CageRow] = {}
        for r in cage:
            key = (importer_ulid, r.vehicle.deep_link)
            cars.setdefault(key, r)

        car_keys = list(cars.keys())
        if not car_keys:
            return
        v_entity = [k[0] for k in car_keys]
        v_links = [k[1] for k in car_keys]
        existing: dict[tuple[str, str], str] = {
            (row["entity_ulid"], row["deep_link"]): row["vehicle_ulid"]
            for row in await conn.fetch(
                """SELECT vehicle_ulid, entity_ulid, deep_link FROM vehicle
                   WHERE (entity_ulid, deep_link) IN (
                     SELECT * FROM unnest($1::text[], $2::text[]))""",
                v_entity, v_links)
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
            ins = [(vehicle_ulid_for[k], k[0], k[1], cars[k].vehicle) for k in new_keys]
            await conn.execute(
                _BULK_INSERT_VEHICLES,
                [x[0] for x in ins], [x[1] for x in ins], [x[2] for x in ins],
                [x[3].title for x in ins], [x[3].make for x in ins], [x[3].model for x in ins],
                [x[3].year for x in ins], [x[3].km for x in ins], [x[3].price for x in ins],
                [x[3].fuel for x in ins], [x[3].transmission for x in ins],
                [x[3].photo_url for x in ins], [x[3].listing_ref for x in ins])
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

        # ---- EDGES: importer<->vehicle. RETURNING (xmax=0) counts genuinely new edges.
        e_vehicles = [vehicle_ulid_for[k] for k in car_keys]
        e_urls = [cars[k].vehicle.deep_link for k in car_keys]
        e_refs = [cars[k].vehicle.listing_ref for k in car_keys]
        e_prices = [cars[k].vehicle.price for k in car_keys]
        edge_rows = await conn.fetch(_BULK_UPSERT_EDGES, e_vehicles, e_urls, e_refs,
                                     e_prices, importer_ulid)
        stats["edges_created"] += sum(1 for row in edge_rows if row["inserted"])

        # ---- NEW delta events — only for genuinely new vehicles, price-drop preserved.
        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                v = cars[k].vehicle
                payload = {"price": v.price, "title": v.title, "platform": m.trade_name}
                if v.prev_price is not None and v.price is not None and v.prev_price > v.price:
                    payload["price_drop"] = {"from": v.prev_price, "to": v.price,
                                             "amount": v.prev_price - v.price}
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities, ev_payloads)
            stats["new_events"] += len(confirmed_new)


# ===========================================================================
# Per-member orchestration
# ===========================================================================


async def harvest_member(conn: asyncpg.Connection, member_name: str, geo: GeoResolver,
                         max_pages: int, concurrency: int) -> dict:
    """Drain ONE importer member end to end: ensure the importer entity, drain its data-layer
    through the governor, BULK-cage every window, write the recipe, run the VAM quorum, record the
    S-HEALTH heartbeat. Returns the member's stats dict."""
    builder = MEMBER_BUILDERS[member_name]
    m = builder()
    fetcher = ImporterFetcher(pool_size=concurrency)
    gov = governor()

    stats = {
        "member": member_name, "source_key": m.key, "owner_model": "importer",
        "pages_fetched": 0, "items_seen": 0, "cars_caged": 0, "new_cars": 0,
        "edges_created": 0, "new_events": 0, "price_drops_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "no_link_skipped": 0,
        "concurrency": concurrency, "max_pages": max_pages,
    }
    harvested_cageable: set[tuple[str, str]] = set()

    if await is_open(conn, m.key):
        print(f"[group_importador:{member_name}] breaker OPEN for {m.key}; skipping drain "
              f"(graceful degradation, site still serves last snapshot).")
        return {**stats, "skipped": True, "reason": "breaker_open"}

    governed = gov.wrap_fetch_text(fetcher.fetch_modrive)

    def fetch_one(p):
        return fetcher.fetch_async(governed, m.endpoint, page=p)

    def parse_one(text):
        return parse_modrive_page(text)

    fetch_error: str | None = None
    last_http: int | None = None
    importer_ulid = await ensure_importer_entity(conn, m)
    importer_cdp = importer_cdp_code(m.domain)
    edges_before = await conn.fetchval(
        "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", importer_ulid)

    print(f"[group_importador:{member_name}] importer entity ready: {importer_cdp} (ulid={importer_ulid}) "
          f"kind=importador group=long_tail_web role=standalone_pos owner_model=importer")
    print(f"[group_importador:{member_name}] governor paces host {m.host}; CONCURRENT drain "
          f"window={concurrency} pages, target={max_pages} pages (~{m.page_size} cars/page).")

    seen_ids: set[str] = set()
    stop = False
    next_page = 1
    while next_page <= max_pages and not stop:
        window = list(range(next_page, min(next_page + concurrency, max_pages + 1)))
        next_page = window[-1] + 1
        results = await asyncio.gather(*(fetch_one(p) for p in window), return_exceptions=True)

        window_vehicles: list[Vehicle] = []
        pages_in_window = 0
        cageable_before_window = len(harvested_cageable)
        for page, data in zip(window, results):
            if isinstance(data, Exception):
                fetch_error = str(data)
                last_http = fetcher.last_status
                print(f"[group_importador:{member_name}] page {page} fetch failed ({data}); "
                      f"stopping drain honestly.")
                stop = True
                break
            try:
                vehicles, declared = parse_one(data)
            except Exception as ex:  # a parse failure is recipe drift the breaker must catch.
                fetch_error = f"parse error on page {page}: {ex}"
                last_http = fetcher.last_status
                print(f"[group_importador:{member_name}] {fetch_error}; stopping.")
                stop = True
                break
            if stats["declared_full"] is None and declared is not None:
                stats["declared_full"] = declared
            if not vehicles:
                print(f"[group_importador:{member_name}] page {page}: no items; stopping (boundary).")
                stop = True
                break
            window_vehicles.extend(vehicles)
            pages_in_window += 1

        if window_vehicles:
            await ingest_window(conn, m, importer_ulid, importer_cdp, window_vehicles, seen_ids,
                                harvested_cageable, stats)
            stats["pages_fetched"] += pages_in_window
            print(f"[group_importador:{member_name}] window {window[0]}-{window[0]+pages_in_window-1}: "
                  f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                  f"edges={stats['edges_created']} drops={stats['price_drops_captured']}")
            # SSR JSON-LD ItemList is a FIXED featured block: page/N/ repeats page 1's id-set, so
            # once a whole window adds no NEW cageable car the own-site boundary is reached — stop
            # honestly rather than re-fetching the same 19 cars forever.
            if len(harvested_cageable) == cageable_before_window and not stop:
                print(f"[group_importador:{member_name}] window added 0 new cars "
                      f"(own-site ItemList exhausted); stopping (boundary).")
                stop = True

    recipe_path = write_recipe(importer_cdp, m.recipe)
    stats["recipe_path"] = str(recipe_path)
    print(f"[group_importador:{member_name}] recipe written: {recipe_path}")

    # VAM count quorum — THREE orthogonal like-with-like paths, all "distinct cageable cars":
    #   db_edges           = platform_listing rows for this importer  (DB write truth)
    #   db_join_vehicles   = distinct vehicles via the edge join       (DB read truth)
    #   harvested_cageable = distinct (owner_cdp, deep_link) pulled    (harvest truth)
    db_edges = await conn.fetchval(
        "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", importer_ulid)
    db_join_vehicles = await conn.fetchval(
        """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
           JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
           JOIN entity e ON e.entity_ulid = v.entity_ulid
           WHERE pl.platform_entity_ulid=$1""", importer_ulid)
    harvested_cageable_n = len(harvested_cageable)
    verdict = await record_count_verdict(
        conn, subject_type="platform_slice", subject_key=importer_cdp,
        claim="distinct cageable cars (harvest) == platform_listing edges == join-reachable vehicles",
        paths={"db_edges": db_edges, "db_join_vehicles": db_join_vehicles,
               "harvested_cageable": harvested_cageable_n}, tolerance=0.0)
    stats["verdict"] = verdict
    stats["db_edges"] = db_edges
    stats["db_join_vehicles"] = db_join_vehicles
    stats["harvested_cageable"] = harvested_cageable_n
    stats["harvested_distinct_ids"] = len(seen_ids)
    stats["edges_new_this_run"] = db_edges - (edges_before or 0)
    stats["platform_code"] = importer_cdp
    stats["platform_ulid"] = importer_ulid

    run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
    run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
    outcome = await record_run(conn, m.key, ok=run_ok, rows=stats["cars_caged"],
                               error=run_error, http_status=last_http)
    stats["health_status"] = outcome.status
    stats["breaker_state"] = outcome.breaker_state
    if not run_ok:
        stats["repair_action"] = await auto_repair(
            conn, m.key, run_error or "harvest failed", phase="scrape", http_status=last_http)
    return stats


async def harvest(members: list[str], max_pages: int = DEFAULT_MAX_PAGES,
                  concurrency: int = DEFAULT_CONCURRENCY) -> list[dict]:
    """Drain each requested importer member sequentially against ONE shared connection (the per-host
    governor keeps each member's host paced; members hit different hosts so they never contend)."""
    conn = await asyncpg.connect(DSN)
    try:
        geo = await GeoResolver.load(conn)
        out = []
        for name in members:
            out.append(await harvest_member(conn, name, geo, max_pages, concurrency))
        return out
    finally:
        await conn.close()


def _print_report(all_stats: list[dict]) -> None:
    for stats in all_stats:
        name = stats.get("member")
        if stats.get("skipped"):
            print(f"\n[group_importador:{name}] SKIPPED: {stats.get('reason')}")
            continue
        print("\n" + "=" * 66)
        print(f"IMPORTADOR WHOLESALE HARVEST — {name.upper()} — REPORT")
        print("=" * 66)
        print(f"  importer cdp_code     : {stats.get('platform_code')}")
        print(f"  group / kind / role   : long_tail_web / importador / standalone_pos (tier t0_open, family {name})")
        print(f"  owner model           : importer (importer owns every car)")
        print(f"  declared full (source): {stats.get('declared_full')} (SSR Product.AggregateOffer.offerCount)")
        print(f"  concurrency / target  : {stats.get('concurrency')} pages in flight / {stats.get('max_pages')} pages")
        print(f"  pages fetched         : {stats['pages_fetched']}")
        print(f"  items seen            : {stats['items_seen']}")
        print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page)")
        print(f"  no-link skipped       : {stats['no_link_skipped']}")
        print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
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
        print("=" * 66)


def _force_utf8_stdout() -> None:
    """Windows consoles/pipes default to cp1252, which cannot encode em-dashes or the accented car
    titles this connector prints (Híbrido, Diésel, Automática) — a raw print() then crashes the
    whole drain mid-flight. Reconfigure stdout/stderr to UTF-8 (errors='replace'). Idempotent."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass


def main() -> None:
    _force_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="importador wholesale harvester (MODRIVE SSR JSON-LD ItemList; populates kind=importador)")
    parser.add_argument("--members", nargs="+", default=["modrive"],
                        choices=sorted(MEMBER_BUILDERS.keys()),
                        help="which importer members to harvest; default modrive.")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"pages to harvest per member; default {DEFAULT_MAX_PAGES}.")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=f"pages fetched in parallel per window; default {DEFAULT_CONCURRENCY}.")
    args = parser.parse_args()
    all_stats = asyncio.run(harvest(args.members, args.pages, args.concurrency))
    _print_report(all_stats)


if __name__ == "__main__":
    main()
