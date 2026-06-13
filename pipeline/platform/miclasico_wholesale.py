"""Miclasico WHOLESALE harvester — the Spanish classic-car classifieds, end to end.

Miclasico (miclasico.com) is Spain's largest native classic/collector-car classifieds
(DJ-Classifieds on Joomla, UIkit SSR HTML, Vue islands, no WAF challenge to chrome131 —
defense_tier t0_open). Verified live 2026-06-13: ~990 classic cars (category se_cats=1).

OWNER DECISION (2026-06-13): classic/collector marketplaces are IN SCOPE and MERGED into
the normal market as kind='compraventa' — NO special type, NO new source_group, like any
other used-car seller. This connector caches the Spanish classic inventory exactly that way.

DATA SURFACE — two stages, because Miclasico (unlike Car & Classic) exposes NO single JSON
payload; it is plain DJ-Classifieds HTML:

  1) LISTING (`/anuncios?se=1,p1&se_cats=1,p1&start=N`, 9 cards/page, start steps of 9):
     each card yields the ad id, make (from the href slug), title, price, and (when the
     card description carries it) year + transmission. Pagination is `start=N`; the last
     populated start (~981) bounds the drain (~990 cars).

  2) PDP (`/anuncios/ad/{make}/{slug}-{id}`): the per-car page carries the structured
     LOCATION (`Ubicación` panel -> a city/province name) plus exact map coordinates
     ({lat,lng} in the uk-map JSON), the gallery photos, and the H1 title. The PDP is
     fetched per car ONLY to geo-anchor the province (the listing card has no location) and
     to pick the first gallery image. Both stages run THROUGH the per-host governor.

CAGING — source-truthful, owner-aligned. Miclasico does NOT expose a stable per-seller id on
either surface (the 'Anunciante' block is a free-text contact, not an account id), so there
is NO per-dealer identity to mint — we DO NOT fabricate one. Following the proven coches.net
pattern for anonymised sellers, every ES classic car is owned by ONE synthetic 'compraventa'
bucket entity PER PROVINCE (canonical_key 'name:compraventas clasicos miclasico|p{province}'),
geo-resolved from the PDP location (name first, then lat/lng -> province). A car whose
location cannot be anchored falls to the '00' national bucket so NO real car is ever dropped.

This module mirrors pipeline.platform.carandclassic_wholesale / coches_net_wholesale: same
dual-membership model, same caging, same governor/health/VAM wiring.

  Miclasico (the marketplace)   -> entity, kind='plataforma'  (+ platform_meta)
  each per-province compraventa  -> entity, kind='compraventa' (geo-resolved bucket)
  each CAR                       -> vehicle, OWNED BY its bucket (entity_ulid=owner)
  the car ON the platform        -> platform_listing edge (platform <-> vehicle)

Run: python -m pipeline.platform.miclasico_wholesale --pages 110
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
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
import os

DSN = os.environ.get("CARDEEP_DSN", DSN)

# ---------------------------------------------------------------------------
# Miclasico platform identity. DJ-Classifieds/Joomla SSR HTML, no WAF -> t0_open.
# ---------------------------------------------------------------------------
MC_DOMAIN = "miclasico.com"
MC_WEBSITE = "miclasico.com"
MC_TRADE_NAME = "Miclasico"
MC_SOURCE_KEY = "miclasico_wholesale"
MC_WAF = None  # no WAF challenge to chrome131 (defense_tier t0_open)

_BASE = "https://www.miclasico.com"
# se=1,p1 = section 1 (sell), se_cats=1,p1 = category 1 (classic CARS, excludes motos=26).
LIST_URL = "https://www.miclasico.com/anuncios?se=1,p1&se_cats=1,p1"
_IMPERSONATE = "chrome131"
_TIMEOUT = 45
_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

PLATFORM_PROVINCE_SENTINEL = "00"
PAGE_STEP = 9  # DJ-Classifieds paginates `start=N` in steps of 9.

# Default: drain the whole ES surface. ~990 cars / 9 = ~110 pages.
DEFAULT_MAX_PAGES = 115
# PDP fetches dominate; keep concurrency modest (the governor's bucket is the real limiter).
DEFAULT_CONCURRENCY = 6

BUCKET_KIND = "compraventa"
BUCKET_NAME_PREFIX = "Compraventas clasicos Miclasico"
BUCKET_PROVINCE_FALLBACK = "00"

# ---- HTML extraction patterns (anchored on the real DJ-Classifieds markup) ----
_CARD_RE = re.compile(
    r'<a class="el-item[^"]*" href="(/anuncios/ad/([a-z0-9-]+)/[a-z0-9-]+-(\d+))"[^>]*>(.*?)</a>',
    re.S)
_TITLE_RE = re.compile(r"<h3[^>]*>(.*?)</h3>", re.S)
_PRICE_RE = re.compile(r"price_val'>([^<]+)<")
_DESC_RE = re.compile(r'panel uk-margin-top">([^<]*(?:venta|MANUAL|AUTOM|de \d{4})[^<]*)<', re.I)
_IMG_RE = re.compile(r'src="([^"]+)"')
_YEAR_RE = re.compile(r"de (\d{4})")
_TRANS_RE = re.compile(r"(MANUAL|AUTOM[AÁ]TIC[OA])", re.I)
_START_RE = re.compile(r"[?&]start=(\d+)")
# PDP patterns
_PDP_LOC_RE = re.compile(
    r'Ubicaci[oó]n\s*</h2>.*?<div class="uk-panel uk-margin">\s*([^<]+?)\s*</div>', re.S)
_PDP_LATLNG_RE = re.compile(r'"lat":([\d.-]+),"lng":([\d.-]+)')
_PDP_H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
_PDP_GALLERY_RE = re.compile(r'(https://www\.miclasico\.com/images/djclassifieds/item/\d+/[^\s"]+)')

_TRANSMISSION = {"manual": "Manual", "automatico": "Automático", "automatica": "Automático",
                 "automático": "Automático", "automática": "Automático"}


def mc_platform_cdp_code() -> str:
    """The Miclasico platform's immutable cdp_code (canonical_key 'domain:miclasico.com',
    province segment '00'). Mirrors every other platform's minting."""
    key = f"domain:{MC_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Parsed shapes.
# ---------------------------------------------------------------------------


@dataclass
class CardRef:
    """A listing card parsed from the search grid (cheap, no PDP fetch)."""
    ad_id: str
    make_slug: str
    deep_link: str
    title: str | None
    price: float | None
    year: int | None
    transmission: str | None


@dataclass
class Vehicle:
    """A fully-resolved car (card + PDP enrichment)."""
    deep_link: str
    listing_ref: str
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    price: float | None
    transmission: str | None
    photo_url: str | None
    province: str | None   # INE province code resolved from the PDP location


def _price_eur(raw: str | None) -> float | None:
    """Parse a DJ-Classifieds price string '17.000' / '128.000' -> float EUR.
    The thousands separator is '.', there are no decimals on this surface."""
    if not raw:
        return None
    digits = re.sub(r"[^\d]", "", raw)
    if not digits:
        return None
    try:
        return float(digits)
    except ValueError:
        return None


def _to_int_year(raw) -> int | None:
    if raw is None:
        return None
    try:
        y = int(raw)
    except (TypeError, ValueError):
        return None
    return y if 1900 <= y <= 2100 else None


def _title_make_model(title: str | None, make_slug: str) -> tuple[str | None, str | None]:
    """Split a card title 'Toyota LAND CRUISER HDJ 100' into (make, model). The make is the
    first token (matching the href slug); the rest is the model. Title-cased lightly."""
    if not title:
        return (make_slug.replace("-", " ").title() if make_slug else None, None)
    parts = title.strip().split(None, 1)
    make = parts[0]
    model = parts[1].strip() if len(parts) > 1 else None
    return make, (model or None)


def parse_cards(html: str) -> list[CardRef]:
    """Parse every listing card on a search page into a CardRef (no PDP fetch)."""
    out: list[CardRef] = []
    for href, make_slug, ad_id, inner in _CARD_RE.findall(html):
        inner_flat = re.sub(r"\s+", " ", inner)
        tm = _TITLE_RE.search(inner_flat)
        pm = _PRICE_RE.search(inner_flat)
        dm = _DESC_RE.search(inner_flat)
        desc = dm.group(1) if dm else ""
        ym = _YEAR_RE.search(desc)
        trm = _TRANS_RE.search(desc)
        out.append(CardRef(
            ad_id=ad_id,
            make_slug=make_slug,
            deep_link=_BASE + href,
            title=(tm.group(1).strip() if tm else None),
            price=_price_eur(pm.group(1) if pm else None),
            year=_to_int_year(ym.group(1) if ym else None),
            transmission=_TRANSMISSION.get((trm.group(1).lower() if trm else ""), None),
        ))
    return out


def parse_pdp(html: str, geo: GeoResolver) -> tuple[str | None, str | None, str | None, str | None]:
    """Parse the PDP for (province_code, h1_title, first_photo, transmission_hint).

    Province resolution, in order of confidence:
      1) the 'Ubicación' panel name -> GeoResolver.province_code (handles a bare province or
         a unique city) / resolve_city_global (a city unique nationally).
      2) the map {lat,lng} -> nearest-province is NOT attempted here (no province polygon
         table on this backbone); lat/lng is captured for future use but name resolution is
         the authoritative path. None -> the caller buckets under '00'.
    """
    loc_m = _PDP_LOC_RE.search(html)
    province = None
    if loc_m:
        name = re.sub(r"\s+", " ", loc_m.group(1)).strip()
        # Try province name first (e.g. 'Barcelona' is both a province and its capital),
        # then a nationally-unique city.
        province = geo.province_code(name)
        if province is None:
            province, _muni = geo.resolve_city_global(name)
    h1_m = _PDP_H1_RE.search(html)
    h1 = re.sub(r"\s+", " ", h1_m.group(1)).strip() if h1_m else None
    photo_m = _PDP_GALLERY_RE.search(html)
    photo = photo_m.group(1) if photo_m else None
    return province, h1, photo, None


# ---------------------------------------------------------------------------
# Fetch: a pool of governed curl_cffi GET sessions (list pages + PDPs).
# ---------------------------------------------------------------------------


class MCFetcher:
    """A POOL of fingerprint-coherent curl_cffi GET sessions for Miclasico. One Session per
    concurrency slot (a shared session races under the governor's to_thread fetch). The
    governor's per-host bucket bounds the AGGREGATE rate across the pool."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch_text(self, url: str, *, slot: int = 0) -> str:
        """The synchronous GET on pool session `slot` (runs in a worker thread). Returns the
        UTF-8-decoded HTML. Raises on a non-200 so the breaker catches a challenge/empty body."""
        session = self._sessions[slot]
        resp = session.get(url, headers=_HEADERS, impersonate=_IMPERSONATE,
                           timeout=_TIMEOUT, allow_redirects=True)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url}")
        return resp.content.decode("utf-8", errors="replace")

    async def fetch_async(self, governed_fetch, url: str) -> str:
        """Lease a pool slot, fetch THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer (mirrors carandclassic_wholesale: bulk-upsert province buckets + vehicles +
# edges + delta, idempotent ON CONFLICT).
# ---------------------------------------------------------------------------

MC_PLATFORM_RECIPE = {
    "version": 1,
    "source": "miclasico.com",
    "scope": "platform-wholesale (DJ-Classifieds listing grid + per-car PDP)",
    "engine": "curl_cffi+chrome131_impersonate+html_parse",
    "access": "OPEN SSR HTML (chrome131; no proxy, no browser, no WAF — defense_tier t0_open)",
    "data_surface": "sitemap",  # schema-valid literal closest to an HTML listing-grid drain
    "surface_intent": "html_listing_grid+pdp",
    "endpoint": "GET https://www.miclasico.com/anuncios?se=1,p1&se_cats=1,p1&start=N",
    "request": {"headers": "Accept text/html, Accept-Language es-ES",
                "pagination": "start=N in steps of 9 (DJ-Classifieds); ~990 cars / 9 = ~110 pages"},
    "enumeration": "start=0,9,18,...; stop on the first empty page (last populated start ~981)",
    "platform_entity": "kind=plataforma, province_code=NULL (sentinel 00 in cdp_code only), is_tier1=FALSE",
    "dual_membership": "vehicle.entity_ulid=per-province compraventa BUCKET; platform_listing edge=platform<->vehicle",
    "caging": ("no stable per-seller id on either surface -> per-province 'compraventa' bucket "
               "(canonical_key 'name:compraventas clasicos miclasico|p{province}', '00' national "
               "fallback); owner order: classic marketplace MERGED as compraventa, no new type"),
    "field_map": {
        "deep_link": "card href (/anuncios/ad/{make}/{slug}-{id})",
        "listing_ref": "ad id (the trailing -{id})",
        "make": "href make slug / title first token",
        "model": "title minus make",
        "title": "card <h3> / PDP <h1>",
        "price": "card span.price_val ('.' thousands sep -> EUR)",
        "year": "card description 'de {YYYY}' (when present)",
        "transmission": "card description MANUAL/AUTOMATICO (when present)",
        "photo_url": "PDP first gallery image",
        "location": "PDP 'Ubicación' panel name -> province; map {lat,lng} captured",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the Miclasico platform entity + platform_meta exist. is_tier1=FALSE
    (no WAF), source_group=marketplace_motor (a car-specialist classifieds), data_surface=
    'sitemap' (the schema-valid literal closest to an HTML listing-grid drain)."""
    code = mc_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,'plataforma',$3,$3,NULL,$4,$5,FALSE,'active','platform_label',
               'marketplace_motor','platform',$6, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               source_group = EXCLUDED.source_group, role = EXCLUDED.role""",
        eulid, code, MC_TRADE_NAME, MC_WEBSITE, MC_WAF, MC_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, MC_SOURCE_KEY, MC_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like)
           VALUES ($1,'sitemap',$2::jsonb,FALSE,FALSE)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail""",
        eulid, json.dumps({"endpoint": LIST_URL, "host": host_of(LIST_URL),
                           "method": "GET", "pagination": "start=N step 9",
                           "surface_intent": "html_listing_grid+pdp",
                           "engine": "curl_cffi/chrome131_impersonate"}))
    return eulid


def cdp_code_bucket(province_code: str) -> str:
    """Mint the per-province compraventa bucket cdp_code (canonical_key
    'name:compraventas clasicos miclasico|p{province}'). Deterministic over (platform,
    province) -> idempotent across re-runs. '00' fallback stores province_code=NULL."""
    return cdp_code(province_code=province_code, name=BUCKET_NAME_PREFIX)


_BULK_UPSERT_BUCKETS = """
INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
        province_code, is_tier1, status, kind_source,
        source_group, role, sells_cars, first_discovered_source, last_seen)
SELECT u.entity_ulid, u.cdp_code, 'compraventa'::entity_kind, u.name, u.name,
       u.province_code, FALSE, 'active', 'platform_label',
       NULL, NULL, TRUE, $5, now()
  FROM unnest($1::text[], $2::text[], $3::text[], $4::char(2)[])
       AS u(entity_ulid, cdp_code, name, province_code)
ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()
"""

_BULK_UPSERT_BUCKET_SOURCES = """
INSERT INTO entity_source (entity_ulid, source_key, source_ref)
SELECT e.entity_ulid, $3, u.source_ref
  FROM unnest($1::text[], $2::text[]) AS u(cdp_code, source_ref)
  JOIN entity e ON e.cdp_code = u.cdp_code
ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()
"""

_BULK_INSERT_VEHICLES = """
INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model,
        year, price, transmission, photo_url, vin_ref, status)
SELECT u.vehicle_ulid, u.entity_ulid, u.deep_link, u.title, u.make, u.model,
       u.year, u.price, u.transmission, u.photo_url, u.vin_ref, 'available'
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[], $5::text[], $6::text[],
              $7::int[], $8::numeric[], $9::text[], $10::text[], $11::text[])
       AS u(vehicle_ulid, entity_ulid, deep_link, title, make, model,
            year, price, transmission, photo_url, vin_ref)
ON CONFLICT (entity_ulid, deep_link) DO NOTHING
"""

_BULK_TOUCH_VEHICLES = """
UPDATE vehicle v SET last_seen = now(), status = 'available'
  FROM unnest($1::text[]) AS u(vehicle_ulid)
 WHERE v.vehicle_ulid = u.vehicle_ulid
"""

_BULK_UPSERT_EDGES = """
INSERT INTO platform_listing (vehicle_ulid, platform_entity_ulid, listing_url,
        listing_ref, platform_price, status, segment, first_seen, last_seen)
SELECT u.vehicle_ulid, $5, u.listing_url, u.listing_ref, u.platform_price,
       'listed', 'used', now(), now()
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


def _province_name(prov: str | None, prov_names: dict[str, str]) -> str:
    if not prov:
        return "ES"
    return prov_names.get(prov, prov)


@dataclass
class _CageRow:
    owner_cdp: str
    owner_name: str | None
    owner_province: str | None
    source_ref: str
    vehicle: Vehicle


async def _resolve_window(fetcher: "MCFetcher", governed_fetch, geo: GeoResolver,
                          cards: list[CardRef], seen_ids: set, stats: dict) -> list[Vehicle]:
    """Fetch each card's PDP (concurrently, governed) and build a fully-resolved Vehicle.

    The PDP fetch is the per-car geo-anchor (the listing card has no location). A PDP that
    fails is NOT dropped — the car is still caged under the '00' national bucket (a real car
    must be served even if its province is momentarily unreachable)."""
    fresh = []
    for c in cards:
        if c.ad_id in seen_ids:
            stats["dup_ids_collapsed"] += 1
            continue
        seen_ids.add(c.ad_id)
        fresh.append(c)
    if not fresh:
        return []

    async def resolve(card: CardRef) -> Vehicle:
        province = None
        h1 = photo = None
        try:
            pdp_html = await fetcher.fetch_async(governed_fetch, card.deep_link)
            province, h1, photo, _ = parse_pdp(pdp_html, geo)
        except Exception:
            stats["pdp_failed"] += 1  # geo unreachable -> national bucket, car still served
        if province is None:
            stats["loc_unresolved"] += 1
        make, model = _title_make_model(h1 or card.title, card.make_slug)
        return Vehicle(
            deep_link=card.deep_link,
            listing_ref=card.ad_id,
            title=(h1 or card.title),
            make=make,
            model=model,
            year=card.year,
            price=card.price,
            transmission=card.transmission,
            photo_url=photo,
            province=province,
        )

    return list(await asyncio.gather(*(resolve(c) for c in fresh)))


async def _ingest_vehicles(conn: asyncpg.Connection, prov_names: dict[str, str],
                           platform_ulid: str, vehicles: list[Vehicle],
                           harvested_cageable: set, stats: dict) -> None:
    """BULK-ingest a batch of fully-resolved vehicles in ONE transaction (set-based SQL).
    Same idempotency/delta/VAM semantics as the carandclassic path."""
    if not vehicles:
        return
    # Build cage rows (province bucket per car).
    cage: list[_CageRow] = []
    for v in vehicles:
        if not v.deep_link:
            continue
        bucket_prov = v.province or BUCKET_PROVINCE_FALLBACK
        owner_cdp = cdp_code_bucket(bucket_prov)
        pname = _province_name(v.province, prov_names)
        harvested_cageable.add((owner_cdp, v.deep_link))
        cage.append(_CageRow(
            owner_cdp=owner_cdp,
            owner_name=f"{BUCKET_NAME_PREFIX} {pname}",
            owner_province=v.province,
            source_ref=f"mc:{bucket_prov}",
            vehicle=v))
    if not cage:
        return

    async with conn.transaction():
        owners: dict[str, _CageRow] = {}
        for r in cage:
            owners.setdefault(r.owner_cdp, r)
        d_ulids = [ulid() for _ in owners]
        d_cdps = list(owners.keys())
        d_names = [owners[c].owner_name for c in d_cdps]
        d_provs = [owners[c].owner_province for c in d_cdps]
        d_refs = [owners[c].source_ref for c in d_cdps]
        await conn.execute(_BULK_UPSERT_BUCKETS, d_ulids, d_cdps, d_names, d_provs, MC_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_BUCKET_SOURCES, d_cdps, d_refs, MC_SOURCE_KEY)
        cdp_to_ulid = {
            row["cdp_code"]: row["entity_ulid"]
            for row in await conn.fetch(
                "SELECT cdp_code, entity_ulid FROM entity WHERE cdp_code = ANY($1::text[])", d_cdps)
        }

        cars: dict[tuple[str, str], _CageRow] = {}
        for r in cage:
            du = cdp_to_ulid.get(r.owner_cdp)
            if du is None:
                continue
            key = (du, r.vehicle.deep_link)
            cars.setdefault(key, r)

        car_keys = list(cars.keys())
        v_entity = [k[0] for k in car_keys]
        v_links = [k[1] for k in car_keys]
        existing = {
            (row["entity_ulid"], row["deep_link"]): row["vehicle_ulid"]
            for row in await conn.fetch(
                "SELECT vehicle_ulid, entity_ulid, deep_link FROM vehicle "
                "WHERE (entity_ulid, deep_link) IN (SELECT * FROM unnest($1::text[], $2::text[]))",
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
                [x[3].year for x in ins], [x[3].price for x in ins],
                [x[3].transmission for x in ins], [x[3].photo_url for x in ins],
                [x[3].listing_ref for x in ins])
            landed = {
                (row["entity_ulid"], row["deep_link"]): row["vehicle_ulid"]
                for row in await conn.fetch(
                    "SELECT vehicle_ulid, entity_ulid, deep_link FROM vehicle "
                    "WHERE vehicle_ulid = ANY($1::text[])",
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

        e_vehicles = [vehicle_ulid_for[k] for k in car_keys]
        e_urls = [cars[k].vehicle.deep_link for k in car_keys]
        e_refs = [cars[k].vehicle.listing_ref for k in car_keys]
        e_prices = [cars[k].vehicle.price for k in car_keys]
        edge_rows = await conn.fetch(_BULK_UPSERT_EDGES, e_vehicles, e_urls, e_refs,
                                     e_prices, platform_ulid)
        stats["edges_created"] += sum(1 for row in edge_rows if row["inserted"])

        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                v = cars[k].vehicle
                payload = {"price": v.price, "title": v.title, "platform": MC_TRADE_NAME}
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities, ev_payloads)
            stats["new_events"] += len(confirmed_new)


async def harvest(max_pages: int = DEFAULT_MAX_PAGES,
                  concurrency: int = DEFAULT_CONCURRENCY,
                  start_page: int = 0) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    fetcher = MCFetcher(pool_size=concurrency)
    stats = {
        "pages_fetched": 0, "cards_seen": 0, "dup_ids_collapsed": 0,
        "pdp_failed": 0, "loc_unresolved": 0, "new_buckets": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "buckets_distinct": 0,
        "concurrency": concurrency, "declared_full": None,
    }
    harvested_cageable: set[tuple[str, str]] = set()

    if await is_open(conn, MC_SOURCE_KEY):
        print(f"[miclasico_wholesale] breaker OPEN for {MC_SOURCE_KEY}; skipping drain.")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": MC_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_text)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        prov_names = {r["code"]: r["name"]
                      for r in await conn.fetch("SELECT code, name FROM geo_province")}
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = mc_platform_cdp_code()
        print(f"[miclasico_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid})")
        print(f"[miclasico_wholesale] governor paces host {host_of(LIST_URL)} (per-host token bucket).")
        print(f"[miclasico_wholesale] drain: up to {max_pages} list pages "
              f"(start step {PAGE_STEP}), PDP-enriched, window={concurrency}.")

        seen_ids: set[str] = set()
        buckets_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa' "
            "AND first_discovered_source=$1", MC_SOURCE_KEY)}

        page_idx = max(0, start_page)
        while page_idx < max_pages:
            start = page_idx * PAGE_STEP
            list_url = f"{LIST_URL}&start={start}"
            try:
                html = await fetcher.fetch_async(governed_fetch, list_url)
            except Exception as exc:
                fetch_error = str(exc)
                last_http = fetcher.last_status
                print(f"[miclasico_wholesale] list page start={start} failed ({exc}); stopping honestly.")
                break
            cards = parse_cards(html)
            if not cards:
                print(f"[miclasico_wholesale] start={start}: no cards; end of catalog.")
                break
            stats["cards_seen"] += len(cards)
            stats["pages_fetched"] += 1

            vehicles = await _resolve_window(fetcher, governed_fetch, geo, cards, seen_ids, stats)
            await _ingest_vehicles(conn, prov_names, platform_ulid, vehicles,
                                   harvested_cageable, stats)
            print(f"[miclasico_wholesale] start={start}: cards={len(cards)} "
                  f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                  f"edges={stats['edges_created']} loc_unresolved={stats['loc_unresolved']}")
            page_idx += 1

        stats["declared_full"] = stats["cards_seen"]  # the surface has no global counter; cards drained.

        buckets_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa' "
            "AND first_discovered_source=$1", MC_SOURCE_KEY)}
        stats["new_buckets"] = len(buckets_after - buckets_before)
        stats["buckets_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, MC_PLATFORM_RECIPE)
        print(f"[miclasico_wholesale] recipe written: {recipe_path}")

        db_edges = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)
        db_join_vehicles = await conn.fetchval(
            """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid=$1""", platform_ulid)
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
        stats["platform_code"] = platform_code
        stats["platform_ulid"] = platform_ulid
        stats["recipe_path"] = str(recipe_path)

        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, MC_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, MC_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[miclasico_wholesale] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("MICLASICO WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  list pages fetched    : {stats['pages_fetched']}")
    print(f"  cards seen            : {stats['cards_seen']}")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')}")
    print(f"  PDP fetch failed      : {stats['pdp_failed']} (car still caged under '00')")
    print(f"  location unresolved   : {stats['loc_unresolved']} (-> '00' national bucket; never dropped)")
    print(f"  province buckets      : {stats['buckets_distinct']} distinct "
          f"({stats['new_buckets']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for Miclasico = {stats.get('db_edges')})")
    print(f"  NEW delta events      : {stats['new_events']}")
    print("  --- VAM count quorum (like-with-like, this slice) ---")
    print(f"  harvested_cageable    : {stats.get('harvested_cageable')}")
    print(f"  db_edges              : {stats.get('db_edges')}")
    print(f"  db_join_vehicles      : {stats.get('db_join_vehicles')}")
    print(f"  VAM verdict           : {stats.get('verdict')}")
    print(f"  health status         : {stats.get('health_status')} / breaker {stats.get('breaker_state')}")
    print(f"  recipe                : {stats.get('recipe_path')}")
    print("=" * 64)


def _force_utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass


def main() -> None:
    _force_utf8_stdout()
    parser = argparse.ArgumentParser(description="Miclasico wholesale harvester (HTML grid + PDP)")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"max list pages (start step {PAGE_STEP}); default {DEFAULT_MAX_PAGES} (~990 cars)")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=f"PDP fetches in flight; default {DEFAULT_CONCURRENCY} (governor is the real limiter)")
    parser.add_argument("--start-page", type=int, default=0,
                        help="first list page index (0-based; skip already-harvested pages)")
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.pages, args.concurrency, args.start_page))
    _print_report(stats)


if __name__ == "__main__":
    main()
