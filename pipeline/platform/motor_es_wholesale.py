"""motor.es WHOLESALE harvester — a Tier-1 marketplace, end to end.

motor.es (Motor Internet S.L., Lorca/Murcia — recipe docs/architecture/tier1_recipes/
motor_es.md) is a car-specialist classifieds aggregator: ~51k used cars, fronted by a
PERMISSIVE Cloudflare over a PHP/SSR backend. The free path is proven (verified live
2026-06-12): plain curl_cffi impersonate=chrome131 gets HTTP 200 on the listing
paginator, the internal JSON AJAX endpoint, and the PDPs — no proxy, no browser, no
solver. is_tier1=TRUE because the brand sits behind a WAF (Cloudflare), even though that
WAF happens to serve curl_cffi (classify defense_tier=t1_soft).

This module mirrors pipeline.platform.coches_net_wholesale EXACTLY (same dual-membership
model, same caging, same governor/health/VAM wiring). It proves a THIRD platform flows
through the ONE architecture, not a fork of it:

  motor.es (the marketplace)    -> entity, kind='plataforma'  (+ platform_meta)
  each SELLING DEALER           -> entity, kind='compraventa' (geo-resolved)
  each CAR                      -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the platform       -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the dealer); platform membership is plural (this edge). The same
physical car can carry BOTH an AS24/coches.net edge and a motor.es edge without ever
changing its owning dealer.

THE SURFACE (recipe, verified live):
  - SURFACE A (census paginator): GET /segunda-mano/coches/?pagina=N -> 22 SSR cards/page,
    each carrying data-id, a base64 data-goto (the PDP url), title, location (lugar), and
    contado/financiado price. ~2,316 pages drain the full 50,938 census. Zero id overlap
    between pages (verified pages 1/2/5).
  - SURFACE B (denominator): GET /segunda-mano/coches/get-data-ajax/ -> JSON {data.total}
    (the live census counter) + a rich seed-10. Used ONLY for the declared-full number; it
    is NOT a paginator (always page 1, size 10).
  - SURFACE C (dealer attribution): GET /segunda-mano/anuncio/{id}/ -> JSON-LD[0] @type:Car
    (price EUR, make, model, km, fuel, offers.seller.name = THE SELLING DEALER) plus a
    /concesionarios/{provincia}/{slug}/ link (the stable per-dealer identity). The card
    alone carries NO dealer name/id (verified: only 9/23 cards even had a phone, none a
    name), so reliable attribution REQUIRES the PDP — that is the honest cost paid here.

PROOF SLICE, NOT THE FULL HARVEST. motor.es declares ~50,938 cars (Surface B total). The
full drain (~2,316 listing pages + ~51k PDP enrichments) is the same command with more
--pages. Here we cap at --pages and enrich each card's PDP, capping cars at --limit, and
log the cap honestly. The declared full count is recorded for the VAM verdict's slice math.

Engine: pipeline.engine.fetch (curl_cffi Chrome impersonation), every fetch routed THROUGH
the per-host governor (the SAME single choke point AS24/coches use). The synchronous
curl_cffi GET runs in a worker thread so the event loop is never blocked, and no host is
fetched faster than its bucket.

Run: python -m pipeline.platform.motor_es_wholesale --pages 200 --limit 4000
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import html as html_mod
import json
import os
import re
from dataclasses import dataclass

import asyncpg

from pipeline.engine.fetch import FetchEngine
from pipeline.engine.governor import governor, host_of
from pipeline.geo import GeoResolver
from pipeline.ids import ulid
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict
from services.api.codes import _base32, cdp_code

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# ---------------------------------------------------------------------------
# motor.es platform identity (recipe motor_es.md; verified live 2026-06-12).
# ---------------------------------------------------------------------------
MOTOR_DOMAIN = "motor.es"
MOTOR_WEBSITE = "motor.es"
MOTOR_TRADE_NAME = "motor.es"
MOTOR_LEGAL_NAME = "Motor Internet S.L."
MOTOR_SOURCE_KEY = "motor_es_wholesale"
MOTOR_WAF = "cloudflare"  # permissive CF over PHP -> is_tier1=TRUE, defense_tier=t1_soft.

# Multi-axis classification (migrations/0016): a Tier-1 car marketplace platform.
MOTOR_DEFENSE_TIER = "t1_soft"          # WAF present but serving curl_cffi.
MOTOR_SOURCE_GROUP = "marketplace_motor"
MOTOR_ROLE = "platform"

_BASE = "https://www.motor.es"
LIST_PATH = "/segunda-mano/coches/"
AJAX_URL = f"{_BASE}/segunda-mano/coches/get-data-ajax/"
_LIST_HEADERS = {"Referer": f"{_BASE}/segunda-mano/coches/"}
_AJAX_HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"{_BASE}/segunda-mano/coches/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}

# Province sentinel '00' = national (same convention as AS24/coches.net). geo_province has
# NO '00', so the platform ENTITY stores province_code = NULL; '00' lives only inside the
# cdp_code string (free text, no FK). We never pollute geo_province with it.
PLATFORM_PROVINCE_SENTINEL = "00"

# PROOF SLICE caps. Default ~200 pages * 22 = ~4,400 cards, capped at 4,000 caged cars.
# NOT the full ~51k set (full drain = the same command with more --pages).
DEFAULT_MAX_PAGES = 200
DEFAULT_LIMIT = 4000
CARDS_PER_PAGE = 22  # verified: 22 <article class="elemento-segunda-mano"> per listing page.

# Regex spine over the SSR card HTML (recipe SURFACE A; field names inspected live).
_CARD_RE = re.compile(
    r'<article class="elemento-segunda-mano".*?</article>', re.S)
_GOTO_RE = re.compile(r'data-goto="([^"]+)"')
_ID_RE = re.compile(r'data-id="(\d+)"')
_TITLE_RE = re.compile(r'data-goto="[^"]+"\s+data-id="\d+"\s+title="([^"]*)"')
_LUGAR_RE = re.compile(r'class="lugar">([^<]+)<')
_PRECIO_CONTADO_RE = re.compile(
    r'class="precio-contado"[^>]*>.*?class="precio"[^>]*><strong\s*>\s*([0-9.\s]+)', re.S)

# PDP JSON-LD spine (recipe SURFACE C; the @type:Car block is authoritative).
_LDJSON_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
_CONCESIONARIO_RE = re.compile(r'/concesionarios/([a-z0-9\-]+)/([a-z0-9\-]+)/')

# "Alcalá de Henares (Madrid)" -> ("Alcalá de Henares", "Madrid").
_LUGAR_SPLIT_RE = re.compile(r'^(.*?)\s*\(([^)]+)\)\s*$')


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL response — field names inspected live, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class CardRef:
    """A car parsed from a single SSR listing card (SURFACE A)."""
    listing_id: str
    pdp_url: str
    title: str | None
    city: str | None          # from lugar "City (Province)"
    province_name: str | None  # from lugar parenthetical
    card_price: float | None   # contado price from the card (fallback for PDP)


@dataclass
class DealerRef:
    """The selling dealer parsed from a PDP (SURFACE C).

    Identity = the /concesionarios/{provincia}/{slug}/ pair (the stable per-dealer key on
    motor.es; verified live). The dealer NAME is offers.seller.name. The province comes
    from the concesionario path's first segment; the city comes from the card's lugar
    (the PDP has no clean municipality field)."""
    slug: str                 # the concesionario slug (stable id within a province)
    prov_slug: str            # the concesionario province segment (e.g. 'madrid')
    name: str | None          # offers.seller.name
    province_code: str | None  # resolved INE province code
    city: str | None          # from the card lugar


@dataclass
class Vehicle:
    """A car parsed from a PDP JSON-LD @type:Car block (SURFACE C)."""
    deep_link: str
    listing_ref: str
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
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


def _decode_goto(goto: str) -> str | None:
    """Decode the base64 data-goto into the canonical PDP url (verified live)."""
    try:
        url = base64.b64decode(goto).decode("utf-8", "ignore").strip()
    except Exception:  # noqa: BLE001 — malformed base64: skip the card honestly
        return None
    return url if url.startswith("http") else None


def _euro_to_float(raw: str | None) -> float | None:
    """'36.900 ' -> 36900.0 (Spanish thousands separator '.', no decimals on these prices)."""
    if not raw:
        return None
    digits = re.sub(r"[^\d]", "", raw)
    if not digits:
        return None
    try:
        return float(digits)
    except (TypeError, ValueError):
        return None


def parse_card(block: str) -> CardRef | None:
    """Parse one SSR listing card (SURFACE A). Returns None if id/PDP cannot be derived."""
    mid = _ID_RE.search(block)
    mgoto = _GOTO_RE.search(block)
    if not mid or not mgoto:
        return None
    pdp = _decode_goto(mgoto.group(1))
    if not pdp:
        return None
    mt = _TITLE_RE.search(block)
    title = html_mod.unescape(mt.group(1)) if mt else None
    city = province = None
    ml = _LUGAR_RE.search(block)
    if ml:
        lugar = html_mod.unescape(ml.group(1)).strip()
        ms = _LUGAR_SPLIT_RE.match(lugar)
        if ms:
            city = ms.group(1).strip() or None
            province = ms.group(2).strip() or None
        else:
            city = lugar or None
    mp = _PRECIO_CONTADO_RE.search(block)
    return CardRef(
        listing_id=mid.group(1),
        pdp_url=pdp,
        title=title,
        city=city,
        province_name=province,
        card_price=_euro_to_float(mp.group(1)) if mp else None,
    )


def _parse_cards(html: str) -> list[CardRef]:
    out: list[CardRef] = []
    for block in _CARD_RE.findall(html):
        c = parse_card(block)
        if c is not None:
            out.append(c)
    return out


def _ld_car_block(html: str) -> dict | None:
    """Return the JSON-LD @type:Car dict from a PDP (block [0]); None if absent."""
    for raw in _LDJSON_RE.findall(html):
        try:
            d = json.loads(raw)
        except Exception:  # noqa: BLE001 — one malformed block must not kill the PDP
            continue
        t = d.get("@type")
        if t == "Car" or (isinstance(t, list) and "Car" in t):
            return d
    return None


def parse_pdp_dealer(html: str, card: CardRef) -> DealerRef | None:
    """Parse the SELLING DEALER from a PDP (SURFACE C): offers.seller.name +
    /concesionarios/{prov}/{slug}/. Returns None if no concesionario slug is present
    (no stable dealer identity -> cannot cage honestly)."""
    car = _ld_car_block(html)
    name = None
    if car is not None:
        offers = car.get("offers") or {}
        seller = offers.get("seller") or {} if isinstance(offers, dict) else {}
        name = seller.get("name") if isinstance(seller, dict) else None
    mc = _CONCESIONARIO_RE.search(html)
    if not mc:
        return None
    prov_slug, slug = mc.group(1), mc.group(2)
    return DealerRef(
        slug=slug,
        prov_slug=prov_slug,
        name=name,
        province_code=None,  # resolved by the caller against GeoResolver
        city=card.city,
    )


def parse_pdp_vehicle(html: str, card: CardRef) -> Vehicle:
    """Parse the car from a PDP JSON-LD @type:Car block (SURFACE C), with the card as a
    fallback for fields the JSON-LD omits (price/title)."""
    car = _ld_car_block(html) or {}
    brand = car.get("brand") or {}
    make = brand.get("name") if isinstance(brand, dict) else (brand or None)
    model = car.get("model")
    if isinstance(model, dict):
        model = model.get("name")

    km = None
    odo = car.get("mileageFromOdometer")
    if isinstance(odo, dict):
        km = _to_int(odo.get("value"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    price = None
    offers = car.get("offers") or {}
    if isinstance(offers, dict):
        try:
            price = float(offers["price"]) if offers.get("price") is not None else None
        except (TypeError, ValueError):
            price = None
    if price is None:
        price = card.card_price

    # JSON-LD productionDate/dateVehicleFirstRegistered is not consistently present; the
    # card's nombre-section <li>year</li> is the live source, but year is non-essential to
    # caging. Leave None when the PDP omits it rather than fabricate.
    year = None
    for key in ("dateVehicleFirstRegistered", "productionDate", "modelDate"):
        val = car.get(key)
        if val:
            m = re.search(r"(\d{4})", str(val))
            if m:
                year = _to_int(m.group(1))
                break
    if year is not None and not (1900 <= year <= 2100):
        year = None

    image = car.get("image")
    if isinstance(image, list):
        image = image[0] if image else None
    if isinstance(image, dict):
        image = image.get("url")

    title = car.get("name") or card.title

    return Vehicle(
        deep_link=card.pdp_url,
        listing_ref=card.listing_id,
        title=title,
        make=make,
        model=model,
        year=year,
        km=km,
        price=price,
        fuel=car.get("fuelType"),
        transmission=None,  # not exposed as a clean field on this surface
        photo_url=image if isinstance(image, str) else None,
    )


def motor_platform_cdp_code() -> str:
    """The motor.es platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:motor.es'), province segment '00' (national). Mirrors
    as24/coches so all platforms mint codes the same way."""
    key = f"domain:{MOTOR_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    motor.es dealers expose no bare domain on this surface -> identity = name + location +
    the stable concesionario slug (passed via `address` so two distinct concesionarios that
    share a name in one municipality never collapse to one entity)."""
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni,
                    address=f"concesionario:{d.prov_slug}/{d.slug}")


# ---------------------------------------------------------------------------
# DB layer (mirrors coches_net_wholesale: ensure platform, upsert dealer/vehicle,
# link edge, emit delta, all idempotent ON CONFLICT).
# ---------------------------------------------------------------------------

MOTOR_PLATFORM_RECIPE = {
    "version": 1,
    "source": "motor.es",
    "scope": "platform-wholesale (SSR ?pagina=N census + PDP JSON-LD dealer attribution)",
    "engine": "curl_cffi+chrome131_impersonate+ssr_html+json_ld",
    "access": ("OPEN/FREE (Chrome TLS fingerprint; no proxy, no browser, no solver). Public "
               "site is Cloudflare-fronted but permissive (200 to curl_cffi) -> is_tier1=true, "
               "defense_tier=t1_soft."),
    "data_surface": "json_ld",
    "surface_intent": "ssr_html_census + json_ld_pdp",
    "endpoint": "GET https://www.motor.es/segunda-mano/coches/?pagina=N + /segunda-mano/anuncio/{id}/",
    "request": {
        "list_headers": "Referer: /segunda-mano/coches/",
        "denominator": "GET /segunda-mano/coches/get-data-ajax/ -> data.total (live census counter)",
    },
    "enumeration": "SURFACE A ?pagina=1..N, 22 cards/page (zero id overlap); ~2,316 pages for 50,938 cars",
    "platform_entity": ("kind=plataforma, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=TRUE, defense_tier=t1_soft, source_group=marketplace_motor, role=platform"),
    "dual_membership": "vehicle.entity_ulid=SELLING DEALER (compraventa); platform_listing edge=platform<->vehicle",
    "field_map": {
        "deep_link": "base64-decode(card data-goto) = /segunda-mano/anuncio/{id}/ canonical PDP",
        "listing_ref": "card data-id (motor.es native listing id)",
        "make": "PDP JSON-LD[0] Car.brand.name",
        "model": "PDP JSON-LD[0] Car.model",
        "km": "PDP JSON-LD[0] Car.mileageFromOdometer.value (KMT)",
        "price": "PDP JSON-LD[0] Car.offers.price (EUR); fallback card precio-contado",
        "fuel": "PDP JSON-LD[0] Car.fuelType",
        "photo_url": "PDP JSON-LD[0] Car.image[0]",
        "dealer_name": "PDP JSON-LD[0] Car.offers.seller.name",
        "dealer_identity": "PDP /concesionarios/{provincia}/{slug}/ (stable per-dealer key)",
        "location": "card lugar 'City (Province)' -> city + province (INE-resolved)",
    },
    "caveats": {
        "vin": "JSON-LD vehicleIdentificationNumber is a STATIC dummy (same on distinct cars) — ignored.",
        "card_dealer": "SSR card carries NO dealer name/id -> dealer attribution REQUIRES the PDP.",
        "ajax_paginator": "get-data-ajax is first-10 only; used for the denominator, NOT pagination.",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the motor.es platform entity + platform_meta exist.
    Returns the platform entity_ulid. is_tier1=TRUE (Cloudflare-fronted), and the multi-axis
    classification (defense_tier/source_group/role, migrations/0016) is set explicitly."""
    code = motor_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               defense_tier, source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,'plataforma',$3,$4,NULL,$5,$6,TRUE,'active','platform_label',
               $7::defense_tier,$8::source_group,$9::entity_role,$10, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, website_waf = EXCLUDED.website_waf,
               defense_tier = EXCLUDED.defense_tier, source_group = EXCLUDED.source_group,
               role = EXCLUDED.role, legal_name = EXCLUDED.legal_name""",
        eulid, code, MOTOR_LEGAL_NAME, MOTOR_TRADE_NAME, MOTOR_WEBSITE, MOTOR_WAF,
        MOTOR_DEFENSE_TIER, MOTOR_SOURCE_GROUP, MOTOR_ROLE, MOTOR_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, MOTOR_SOURCE_KEY, MOTOR_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'json_ld',$2::jsonb,FALSE,FALSE,'motor_es')
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"list_endpoint": f"{_BASE}{LIST_PATH}?pagina=N",
                           "pdp_endpoint": f"{_BASE}/segunda-mano/anuncio/{{id}}/",
                           "host": host_of(_BASE), "method": "GET",
                           "cards_per_page": CARDS_PER_PAGE,
                           "surface_intent": "ssr_html_census+json_ld_pdp",
                           "engine": "curl_cffi/chrome131_impersonate"}))
    return eulid


async def upsert_dealer(conn: asyncpg.Connection, geo: GeoResolver, d: DealerRef) -> str | None:
    """Upsert the selling dealer entity (kind='compraventa', geo-resolved).
    Returns the dealer entity_ulid, or None if it cannot be geo-anchored."""
    if not d.province_code:
        return None
    if not (d.province_code.isdigit() and "01" <= d.province_code <= "52"):
        return None
    muni = geo.municipality_code(d.province_code, d.city)
    code = cdp_code_dealer(d, muni)
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, municipality_code, is_tier1, status, kind_source,
               sells_cars, source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,'compraventa',$3,$3,$4,$5,FALSE,'active','platform_label',TRUE,
               'marketplace_motor'::source_group,'standalone_pos'::entity_role,$6, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()""",
        eulid, code, d.name, d.province_code, muni, MOTOR_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, MOTOR_SOURCE_KEY, f"{d.prov_slug}/{d.slug}")
    return eulid


async def upsert_vehicle(conn: asyncpg.Connection, dealer_ulid: str, v: Vehicle) -> tuple[str, bool]:
    """Upsert the vehicle OWNED BY the dealer (entity_ulid=dealer).
    Returns (vehicle_ulid, was_new). Idempotent on (entity_ulid, deep_link)."""
    row = await conn.fetchrow(
        "SELECT vehicle_ulid FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2",
        dealer_ulid, v.deep_link)
    if row is not None:
        vulid = row["vehicle_ulid"]
        await conn.execute(
            "UPDATE vehicle SET last_seen=now(), status='available' WHERE vehicle_ulid=$1", vulid)
        return vulid, False
    vulid = ulid()
    await conn.execute(
        """INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model,
               year, km, price, fuel, transmission, photo_url, vin_ref, status)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,'available')
           ON CONFLICT (entity_ulid, deep_link) DO NOTHING""",
        vulid, dealer_ulid, v.deep_link, v.title, v.make, v.model, v.year, v.km, v.price,
        v.fuel, v.transmission, v.photo_url, v.listing_ref)
    real = await conn.fetchval(
        "SELECT vehicle_ulid FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2",
        dealer_ulid, v.deep_link)
    return real, (real == vulid)


async def link_platform(conn: asyncpg.Connection, platform_ulid: str, vehicle_ulid: str,
                        v: Vehicle) -> bool:
    """INSERT the platform_listing edge (platform <-> vehicle). Idempotent.
    Returns True if a NEW edge was created."""
    inserted = await conn.fetchval(
        """INSERT INTO platform_listing (vehicle_ulid, platform_entity_ulid, listing_url,
               listing_ref, platform_price, status, first_seen, last_seen)
           VALUES ($1,$2,$3,$4,$5,'listed', now(), now())
           ON CONFLICT (vehicle_ulid, platform_entity_ulid)
             DO UPDATE SET last_seen = now(), status = 'listed',
                           platform_price = EXCLUDED.platform_price,
                           listing_ref = EXCLUDED.listing_ref
           RETURNING (xmax = 0) AS inserted""",
        vehicle_ulid, platform_ulid, v.deep_link, v.listing_ref, v.price)
    return bool(inserted)


async def emit_new_event(conn: asyncpg.Connection, vulid: str, dealer_ulid: str, v: Vehicle) -> None:
    """Emit the delta NEW event (same shape as pipeline.ingest)."""
    await conn.execute(
        "INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type, "
        "old_value, new_value) VALUES ($1,$2,$3,'NEW',NULL,$4::jsonb)",
        ulid(), vulid, dealer_ulid, json.dumps(
            {"price": v.price, "title": v.title, "platform": MOTOR_TRADE_NAME}))


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def _configure_motor_host() -> None:
    """Pace www.motor.es on its own bucket. The recipe verified a permissive Cloudflare
    (6 listing pages in 1.3s, 8 PDPs in 2.0s, zero challenge), so motor.es earns a faster
    bucket than the AS24/coches scar default — but still polite (well below a flood) and on
    the same per-host choke point. A PDP-heavy drain (one PDP per car) needs throughput the
    0.5 req/s scar default would make impractically slow, and motor.es is t0/t1_soft-open."""
    gov = governor()
    gov.configure_host("www.motor.es", rate_per_sec=3.0, burst=6.0, min_spacing_s=0.25, jitter_s=0.15)
    gov.configure_host("motor.es", rate_per_sec=3.0, burst=6.0, min_spacing_s=0.25, jitter_s=0.15)


async def _declared_total(governed_fetch) -> int | None:
    """Read the live census denominator from SURFACE B (get-data-ajax data.total)."""
    try:
        body = await governed_fetch(AJAX_URL, headers=_AJAX_HEADERS)
        data = json.loads(body).get("data") or {}
        return _to_int(data.get("total"))
    except Exception:  # noqa: BLE001 — the denominator is honesty-only, never blocks the drain
        return None


async def harvest(max_pages: int = DEFAULT_MAX_PAGES, limit: int = DEFAULT_LIMIT) -> dict:
    conn = await asyncpg.connect(DSN)
    engine = FetchEngine()  # one fingerprint + cookie jar for the whole drain
    stats = {
        "pages_fetched": 0, "cards_seen": 0, "pdp_fetched": 0, "pdp_failed": 0,
        "no_dealer_skipped": 0, "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "declared_full": None,
        "dup_ids_collapsed": 0, "dealers_distinct": 0,
    }
    # Harvest-side truth for the VAM: distinct CAGEABLE cars = distinct (dealer-slug,
    # deep_link) pairs that survived dealer-parse + geo-resolution. Like-with-like vs
    # db_edges (raw card ids include cars whose PDP had no dealer/geo).
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if motor.es's breaker is OPEN (a recent ban/throttle still cooling),
    # skip the drain gracefully — the system keeps serving the last snapshot.
    if await is_open(conn, MOTOR_SOURCE_KEY):
        print(f"[motor_es_wholesale] breaker OPEN for {MOTOR_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, last snapshot still served).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": MOTOR_SOURCE_KEY}

    # GOVERNOR: the single per-host choke point. wrap_fetch_text takes the engine's GET;
    # every listing page AND every PDP passes through www.motor.es's token bucket, off the
    # event loop. No matter how many drains run, the host is never hammered.
    _configure_motor_host()
    gov = governor()
    governed_fetch = gov.wrap_fetch_text(engine.fetch_text)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = motor_platform_cdp_code()
        print(f"[motor_es_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid})")
        print(f"[motor_es_wholesale] governor paces host {host_of(_BASE)} (per-host token bucket).")
        stats["declared_full"] = await _declared_total(governed_fetch)
        print(f"[motor_es_wholesale] PROOF SLICE cap = {max_pages} pages / {limit} cars "
              f"(declared full ~{stats['declared_full']}; full drain = same command, more --pages).")

        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        stop = False
        for page in range(1, max_pages + 1):
            if stop:
                break
            url = f"{_BASE}{LIST_PATH}" if page == 1 else f"{_BASE}{LIST_PATH}?pagina={page}"
            try:
                listing_html = await governed_fetch(url, headers=_LIST_HEADERS)
            except Exception as e:  # noqa: BLE001 — throttle/transient: back off, report
                fetch_error = str(e)
                last_http = getattr(engine, "last_status", None)
                print(f"[motor_es_wholesale] page {page} fetch failed ({e}); stopping drain honestly.")
                break
            stats["pages_fetched"] += 1
            cards = _parse_cards(listing_html)
            if not cards:
                print(f"[motor_es_wholesale] page {page}: no cards; stopping.")
                break

            for card in cards:
                stats["cards_seen"] += 1
                if card.listing_id in seen_ids:
                    stats["dup_ids_collapsed"] += 1
                    continue  # cross-page dedup (newest-first head rotates as cars sell)
                seen_ids.add(card.listing_id)

                # Enrich: the dealer identity lives ONLY on the PDP (card has no dealer name/id).
                try:
                    pdp_html = await governed_fetch(card.pdp_url, headers=_LIST_HEADERS)
                except Exception as e:  # noqa: BLE001 — one bad PDP must not stop the drain
                    stats["pdp_failed"] += 1
                    last_http = getattr(engine, "last_status", None)
                    continue
                stats["pdp_fetched"] += 1

                d = parse_pdp_dealer(pdp_html, card)
                if d is None:
                    stats["no_dealer_skipped"] += 1
                    continue
                # Resolve the dealer province: prefer the card's parenthetical province name
                # (matches the dealer's selling location); fall back to the concesionario
                # path slug. Both go through the INE resolver (accent/alias aware).
                prov = geo.province_code(card.province_name) or geo.province_code(d.prov_slug)
                d.province_code = prov

                async with conn.transaction():
                    dealer_ulid = await upsert_dealer(conn, geo, d)
                    if dealer_ulid is None:
                        stats["geo_skipped"] += 1
                        continue
                    v = parse_pdp_vehicle(pdp_html, card)
                    if not v.deep_link:
                        continue
                    harvested_cageable.add((f"{d.prov_slug}/{d.slug}", v.deep_link))
                    vulid, veh_new = await upsert_vehicle(conn, dealer_ulid, v)
                    stats["cars_caged"] += 1
                    if veh_new:
                        stats["new_cars"] += 1
                        await emit_new_event(conn, vulid, dealer_ulid, v)
                        stats["new_events"] += 1
                    edge_new = await link_platform(conn, platform_ulid, vulid, v)
                    if edge_new:
                        stats["edges_created"] += 1

                if stats["cars_caged"] >= limit:
                    print(f"[motor_es_wholesale] reached --limit {limit} cars; stopping.")
                    stop = True
                    break

            print(f"[motor_es_wholesale] page {page}: cards={len(cards)} "
                  f"caged_total={stats['cars_caged']} edges={stats['edges_created']} "
                  f"pdp_fail={stats['pdp_failed']}")

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, MOTOR_PLATFORM_RECIPE)
        print(f"[motor_es_wholesale] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths that all
        # measure "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for motor.es (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join (DB read truth)
        #   harvested_cageable = distinct (dealer-slug, deep_link) pulled (harvest truth)
        # The declared full count (~51k) is reported for honesty but is NOT a quorum path
        # (it measures the WHOLE platform, not this slice).
        db_edges = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)
        db_join_vehicles = await conn.fetchval(
            """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               JOIN entity d ON d.entity_ulid = v.entity_ulid
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
        stats["harvested_distinct_ids"] = len(seen_ids)
        stats["platform_code"] = platform_code
        stats["platform_ulid"] = platform_ulid
        stats["recipe_path"] = str(recipe_path)

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks motor.es,
        # trips the breaker on a ban, and auto-repairs. OK when >=1 page fetched, no fetch
        # error stopped the drain, and the VAM did not refute.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, MOTOR_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, MOTOR_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[motor_es_wholesale] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("MOTOR.ES WHOLESALE HARVEST — PROOF SLICE REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  declared full (source): {stats.get('declared_full')}  (NOT harvested — proof slice)")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  cards seen            : {stats['cards_seen']}")
    print(f"  PDPs fetched          : {stats['pdp_fetched']} ({stats['pdp_failed']} failed)")
    print(f"  no-dealer skipped     : {stats['no_dealer_skipped']} (PDP had no concesionario)")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page)")
    print(f"  geo skipped (bad prov): {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for motor.es = {stats.get('db_edges')})")
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
    parser = argparse.ArgumentParser(description="motor.es wholesale proof-slice harvester")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"listing pages to enumerate ({CARDS_PER_PAGE} cards/page); "
                             f"default {DEFAULT_MAX_PAGES}")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                        help=f"max cars to cage this run; default {DEFAULT_LIMIT} (proof slice)")
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.pages, args.limit))
    _print_report(stats)


if __name__ == "__main__":
    main()
