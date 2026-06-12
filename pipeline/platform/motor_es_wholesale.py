"""motor.es WHOLESALE harvester — a Tier-1 marketplace, end to end. FULL-COVERAGE.

motor.es (Motor Internet S.L., taxID B73634099 — recipe docs/architecture/tier1_recipes/
motor_es_datalayer.md) is a car-specialist classifieds aggregator: ~51k used cars, fronted
by a PERMISSIVE Cloudflare over a PHP/SSR backend. The free path is proven (verified live
2026-06-12): plain curl_cffi impersonate=chrome131 gets HTTP 200 on the listing paginator,
the internal JSON AJAX endpoint, and the PDPs — no proxy, no browser, no solver.
is_tier1=TRUE because the brand sits behind a WAF (Cloudflare), even though that WAF happens
to serve curl_cffi (classify defense_tier=t1_soft).

This module mirrors pipeline.platform.coches_net_wholesale EXACTLY (same dual-membership
model, same caging, same governor/health/VAM wiring, same BATCH unnest ingest). It proves a
platform flows through the ONE architecture, not a fork of it:

  motor.es (the marketplace)    -> entity, kind='plataforma'  (+ platform_meta)
  each SELLING DEALER           -> entity, kind='compraventa' (geo-resolved)
  each CAR                      -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the platform       -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the dealer); platform membership is plural (this edge). The same
physical car can carry BOTH an AS24/coches.net edge and a motor.es edge without ever
changing its owning dealer.

THE FULL-COVERAGE SURFACE (recipe motor_es_datalayer.md, verified live 2026-06-12):
  motor.es has NO single uncapped surface. The unfiltered `?pagina=N` listing AND every
  facet share a HARD 50-page UI cap (≤1,150 rows) — verified live: madrid ?pagina=50 -> 200,
  ?pagina=51 -> 404. A flat drain reaches only ~1,150 cars (2.3% of the 50,932 census). The
  only reproducible surface that enumerates 100% is a TWO-LEVEL PATH-FACET PARTITION
  (make -> model), MECE (every car has exactly one make+model), where each leaf drains its
  own ≤50-page window. Province is a rare 3rd level only when a model leaf is still > 1,150.

  - SURFACE A (per-cell paginator): GET /segunda-mano/{make}[/{model}]/?pagina=N -> 22 SSR
    cards/page (23 <article> blocks, the 23rd is a 'tasacion' promo with NO data-id). Each
    real card carries data-id, a base64 data-goto (the PDP url), title, lugar, contado price.
  - SURFACE B (denominator + per-facet total): GET /segunda-mano/coches/get-data-ajax/ ->
    data.total (the live census counter, 50,932). Each facet HTML carries its own
    "N coches/resultados" count -> drives the per-cell partition decision.
  - SURFACE C (dealer attribution): GET /segunda-mano/anuncio/{id}/ -> JSON-LD[0] @type:Car
    (price EUR, make, model, km, fuel, offers.seller.name = THE SELLING DEALER) plus a
    /concesionarios/{provincia}/{slug}/ link (the stable per-dealer identity). The card alone
    carries NO dealer name/id, so reliable attribution REQUIRES the PDP — the honest cost.

PROOF vs FULL. The full ~50,932 drain is ONE command: `--full`. By default this runs a
BOUNDED-BUT-LARGE proof that drains several COMPLETE partition cells (whole makes / whole
make-model leaves), capping cars at --limit, so it proves the full-coverage mechanism end to
end without the full ~51k+PDP cost. The cell list is enumerated identically either way — the
only difference is how many cells the run consumes.

Engine: pipeline.engine.fetch (curl_cffi Chrome impersonation), every fetch routed THROUGH
the per-host governor (the SAME single choke point AS24/coches use). The synchronous
curl_cffi GET runs in a worker thread so the event loop is never blocked, and no host is
fetched faster than its bucket.

Run (bounded proof):  python -m pipeline.platform.motor_es_wholesale --max-cells 6 --limit 10000
Run (FULL ~51k):      python -m pipeline.platform.motor_es_wholesale --full
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
from curl_cffi import requests as cffi_requests

from pipeline.engine.governor import governor, host_of
from pipeline.geo import GeoResolver
from pipeline.ids import ulid
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict
from services.api.codes import _base32, cdp_code

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# ---------------------------------------------------------------------------
# motor.es platform identity (recipe motor_es_datalayer.md; verified live 2026-06-12).
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

# The ~52 ES province/region slugs that appear as 1-seg facets — they are NOT makes and NOT
# models. Used to filter the make taxonomy and the model sub-slugs (recipe verified live).
PROVINCE_SLUGS = frozenset({
    "a-coruna", "alava", "albacete", "alicante", "almeria", "asturias", "badajoz", "baleares",
    "barcelona", "burgos", "caceres", "cadiz", "cantabria", "castellon", "ciudad-real",
    "cordoba", "cuenca", "girona", "granada", "guadalajara", "guipuzcoa", "huelva", "huesca",
    "jaen", "la-rioja", "las-palmas", "en-leon", "lleida", "lugo", "madrid", "malaga",
    "murcia", "navarra", "ourense", "palencia", "pontevedra", "salamanca", "segovia",
    "sevilla", "soria", "tarragona", "en-toledo", "valencia", "valladolid", "vizcaya",
    "zamora", "zaragoza", "tenerife", "ceuta", "melilla",
})

# The 50-page UI cap is universal and per-facet (verified live: ?pagina=51 -> 404). A facet
# whose total exceeds LEAF_MAX must be split one level deeper to stay drainable.
CAP_PAGES = 50
CARDS_PER_PAGE = 22  # 23 <article> blocks/page, the 23rd is a 'tasacion' promo (no data-id).
LEAF_MAX = CAP_PAGES * CARDS_PER_PAGE  # 1,100 — a facet bigger than this is split deeper.

# PROOF caps. Default drains a handful of COMPLETE cells (whole makes/leaves), bounded by
# --max-cells and --limit. --full drops both caps and drains every cell (the ~51k census).
DEFAULT_MAX_CELLS = 6
DEFAULT_LIMIT = 10000

# Regex spine over the SSR card HTML (recipe SURFACE A; field names inspected live).
_CARD_RE = re.compile(
    r'<article class="elemento-segunda-mano".*?</article>', re.S)
_GOTO_RE = re.compile(r'data-goto="([^"]+)"')
_ID_RE = re.compile(r'data-id="(\d+)"')
_TITLE_RE = re.compile(r'data-goto="[^"]+"\s+data-id="\d+"\s+title="([^"]*)"')
_LUGAR_RE = re.compile(r'class="lugar">([^<]+)<')
_PRECIO_CONTADO_RE = re.compile(
    r'class="precio-contado"[^>]*>.*?class="precio"[^>]*><strong\s*>\s*([0-9.\s]+)', re.S)

# Per-facet total ("N coches" / "N resultados") and the one-seg taxonomy harvest.
_FACET_TOTAL_RE = re.compile(r'([\d\.]+)\s*(?:coches|resultados|veh[ií]culos|anuncios)', re.I)
_ONE_SEG_RE = re.compile(r'href="https://www\.motor\.es/segunda-mano/([a-z0-9-]+)/"')

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
    """Parse one SSR listing card (SURFACE A). Returns None if id/PDP cannot be derived
    (this is how the 23rd 'tasacion' promo block — no data-id — is dropped cleanly)."""
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


def _facet_total(html: str) -> int | None:
    """Read a facet's own result count from its listing HTML (recipe SURFACE B)."""
    m = _FACET_TOTAL_RE.search(html)
    if not m:
        return None
    return _to_int(m.group(1).replace(".", ""))


def _sub_slugs(make: str, make_html: str) -> list[str]:
    """The model sub-slugs under a make page (province slugs filtered out)."""
    subs = set(re.findall(
        rf'href="https://www\.motor\.es/segunda-mano/{re.escape(make)}/([a-z0-9-]+)/"',
        make_html))
    return sorted(s for s in subs if s not in PROVINCE_SLUGS)


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
# DB layer (mirrors coches_net_wholesale: ensure platform, BATCH-upsert dealer/vehicle,
# link edge, emit delta, all idempotent ON CONFLICT).
# ---------------------------------------------------------------------------

MOTOR_PLATFORM_RECIPE = {
    "version": 2,
    "source": "motor.es",
    "scope": "platform-wholesale (make->model path-facet partition; each leaf ?pagina=1..N + PDP JSON-LD)",
    "engine": "curl_cffi+chrome131_impersonate+ssr_html+json_ld",
    "access": ("OPEN/FREE (Chrome TLS fingerprint; no proxy, no browser, no solver). Public "
               "site is Cloudflare-fronted but permissive (200 to curl_cffi) -> is_tier1=true, "
               "defense_tier=t1_soft."),
    "data_surface": "json_ld",
    "surface_intent": "ssr_html_facet_partition + json_ld_pdp",
    "endpoint": "GET https://www.motor.es/segunda-mano/{make}[/{model}]/?pagina=N + /segunda-mano/anuncio/{id}/",
    "request": {
        "list_headers": "Referer: /segunda-mano/coches/",
        "denominator": "GET /segunda-mano/coches/get-data-ajax/ -> data.total (live census counter, 50,932)",
        "per_facet_total": "each facet HTML carries its own 'N coches/resultados' count",
    },
    "enumeration": ("NO single uncapped surface: unfiltered listing AND every facet share a HARD "
                    "50-page cap (~1,150 rows). Closure = make->model path-facet partition (MECE), "
                    "each leaf draining its own ?pagina=1..min(50,ceil(total/22)); province as a rare "
                    "3rd level when a model leaf is still > 1,150. Dedup on data-id across leaves."),
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
        "page_cap": "HARD 50-page cap per facet (madrid ?pagina=51 -> 404). Flat drain reaches only ~1,150/50,932.",
        "query_filters_ignored": "?precio_hasta=/?anio_desde= are IGNORED; only PATH facets filter. Partition MUST be path-based.",
        "vin": "JSON-LD vehicleIdentificationNumber is a STATIC dummy (same on distinct cars) — ignored.",
        "card_dealer": "SSR card carries NO dealer name/id -> dealer attribution REQUIRES the PDP.",
        "ajax_paginator": "get-data-ajax is a frozen 10-row seed; used for the denominator + taxonomy, NOT pagination.",
        "promo_card": "23 <article> blocks/page; the 23rd is a 'tasacion' promo with no data-id (dropped by parse_card).",
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
        eulid, json.dumps({"list_endpoint": f"{_BASE}/segunda-mano/{{make}}[/{{model}}]/?pagina=N",
                           "pdp_endpoint": f"{_BASE}/segunda-mano/anuncio/{{id}}/",
                           "host": host_of(_BASE), "method": "GET",
                           "cards_per_page": CARDS_PER_PAGE,
                           "enumeration": "make->model path-facet partition (MECE), ≤50 pages/leaf",
                           "surface_intent": "ssr_html_facet_partition+json_ld_pdp",
                           "engine": "curl_cffi/chrome131_impersonate"}))
    return eulid


# The bulk statements — ONE round-trip per table per cell (unnest-based multi-row upsert),
# byte-for-byte the same idempotency the row-by-row path used (a re-run adds 0 rows/events).

_BULK_UPSERT_DEALERS = """
INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
        province_code, municipality_code, is_tier1, status, kind_source,
        sells_cars, source_group, role, first_discovered_source, last_seen)
SELECT u.entity_ulid, u.cdp_code, 'compraventa', u.name, u.name,
       u.province_code, u.municipality_code, FALSE, 'active', 'platform_label',
       TRUE, 'marketplace_motor'::source_group, 'standalone_pos'::entity_role, $7, now()
  FROM unnest($1::text[], $2::text[], $3::text[], $4::char(2)[], $5::char(5)[],
              $6::text[]) AS u(entity_ulid, cdp_code, name, province_code,
                               municipality_code, source_ref)
ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()
"""

_BULK_UPSERT_DEALER_SOURCES = """
INSERT INTO entity_source (entity_ulid, source_key, source_ref)
SELECT e.entity_ulid, $3, u.source_ref
  FROM unnest($1::text[], $2::text[]) AS u(cdp_code, source_ref)
  JOIN entity e ON e.cdp_code = u.cdp_code
ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()
"""

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


@dataclass
class _CageRow:
    """One fully-parsed, geo-anchored car ready for the bulk cage — the in-memory result of
    the parse+resolve phase, before any SQL. Carries everything the batched upserts need so
    the DB phase touches no per-item Python logic, only set-based statements."""
    dealer_ref: str       # "{prov_slug}/{slug}" — the stable concesionario key (cageable id)
    dealer_cdp: str
    dealer_name: str | None
    dealer_province: str
    dealer_muni: str | None
    vehicle: Vehicle


async def _ingest_cell(conn: asyncpg.Connection, platform_ulid: str,
                       cage: list[_CageRow], stats: dict) -> None:
    """BULK-ingest one drained partition cell (its enriched, geo-anchored cars) in ONE
    transaction with set-based SQL — the EXACT coches_net contract.

    Replaces the row-by-row drain with ONE round-trip per table per cell (unnest multi-row
    upserts). The delta/VAM/platform_listing semantics are preserved EXACTLY: same ON CONFLICT
    idempotency, same cageable truth, same NEW-event rule (emitted only for genuinely new
    vehicles). A re-run of an already-harvested cell adds 0 rows and 0 events."""
    if not cage:
        return

    async with conn.transaction():
        # ---- (1) DEALERS: dedup by cdp_code within the cell, bulk-upsert, resolve ulids.
        dealers: dict[str, _CageRow] = {}
        for r in cage:
            dealers.setdefault(r.dealer_cdp, r)  # first occurrence wins (deterministic)
        d_ulids = [ulid() for _ in dealers]
        d_cdps = list(dealers.keys())
        d_names = [dealers[c].dealer_name for c in d_cdps]
        d_provs = [dealers[c].dealer_province for c in d_cdps]
        d_munis = [dealers[c].dealer_muni for c in d_cdps]
        d_refs = [dealers[c].dealer_ref for c in d_cdps]
        await conn.execute(_BULK_UPSERT_DEALERS, d_ulids, d_cdps, d_names, d_provs,
                           d_munis, d_refs, MOTOR_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_DEALER_SOURCES, d_cdps, d_refs, MOTOR_SOURCE_KEY)
        cdp_to_ulid: dict[str, str] = {
            row["cdp_code"]: row["entity_ulid"]
            for row in await conn.fetch(
                "SELECT cdp_code, entity_ulid FROM entity "
                "WHERE cdp_code = ANY($1::text[])", d_cdps)
        }

        # ---- attach the resolved dealer_ulid; dedup cars within the cell by
        # (dealer_ulid, deep_link) so the same ad seen twice is one car.
        cars: dict[tuple[str, str], _CageRow] = {}
        for r in cage:
            du = cdp_to_ulid.get(r.dealer_cdp)
            if du is None:
                continue  # dealer upsert race-impossible here, but stay defensive
            key = (du, r.vehicle.deep_link)
            if key not in cars:
                cars[key] = r

        # ---- (2) VEHICLES: one SELECT splits existing vs new (idempotency truth). Existing
        # -> bulk touch (last_seen/status). New -> Python-minted ulid + bulk insert.
        car_keys = list(cars.keys())
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
                vid = ulid()
                vehicle_ulid_for[key] = vid
                new_keys.append(key)

        if touch_ulids:
            await conn.execute(_BULK_TOUCH_VEHICLES, touch_ulids)

        confirmed_new: list[tuple[str, str]] = []
        if new_keys:
            ins = [(vehicle_ulid_for[k], k[0], k[1], cars[k].vehicle) for k in new_keys]
            await conn.execute(
                _BULK_INSERT_VEHICLES,
                [x[0] for x in ins], [x[1] for x in ins], [x[2] for x in ins],
                [x[3].title for x in ins], [x[3].make for x in ins], [x[3].model for x in ins],
                [x[3].year for x in ins], [x[3].km for x in ins], [x[3].price for x in ins],
                [x[3].fuel for x in ins], [x[3].transmission for x in ins],
                [x[3].photo_url for x in ins], [x[3].listing_ref for x in ins])
            # Confirm which minted ulids actually landed (ON CONFLICT DO NOTHING could drop
            # one if a concurrent writer inserted the same (entity,deep_link) first). Only a
            # confirmed-new vehicle is counted new + gets a NEW event — preserves idempotency.
            landed = {
                (row["entity_ulid"], row["deep_link"]): row["vehicle_ulid"]
                for row in await conn.fetch(
                    """SELECT vehicle_ulid, entity_ulid, deep_link FROM vehicle
                       WHERE vehicle_ulid = ANY($1::text[])""",
                    [vehicle_ulid_for[k] for k in new_keys])
            }
            for k in new_keys:
                real = landed.get(k)
                if real is not None and real == vehicle_ulid_for[k]:
                    confirmed_new.append(k)
                elif real is not None:
                    vehicle_ulid_for[k] = real  # someone else won the race; adopt their ulid
                else:
                    row = await conn.fetchrow(
                        "SELECT vehicle_ulid FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2",
                        k[0], k[1])
                    if row is not None:
                        vehicle_ulid_for[k] = row["vehicle_ulid"]

        stats["cars_caged"] += len(car_keys)
        stats["new_cars"] += len(confirmed_new)

        # ---- (3) EDGES: one batched upsert; RETURNING (xmax=0) counts genuinely new edges.
        e_vehicles = [vehicle_ulid_for[k] for k in car_keys]
        e_urls = [cars[k].vehicle.deep_link for k in car_keys]
        e_refs = [cars[k].vehicle.listing_ref for k in car_keys]
        e_prices = [cars[k].vehicle.price for k in car_keys]
        edge_rows = await conn.fetch(_BULK_UPSERT_EDGES, e_vehicles, e_urls, e_refs,
                                     e_prices, platform_ulid)
        stats["edges_created"] += sum(1 for row in edge_rows if row["inserted"])

        # ---- (4) NEW delta events — only for genuinely new vehicles.
        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                v = cars[k].vehicle
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(
                    {"price": v.price, "title": v.title, "platform": MOTOR_TRADE_NAME}))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities,
                               ev_payloads)
            stats["new_events"] += len(confirmed_new)


# ---------------------------------------------------------------------------
# Orchestration — the make->model facet partition (recipe motor_es_datalayer.md).
# ---------------------------------------------------------------------------

# Default concurrency for the PDP-enrichment fan-out within each cell. The governor's
# per-host bucket is the REAL limiter; this only needs to be wide enough to keep the bucket
# saturated while individual ~250ms PDP GETs are in flight. Mirrors coches_net's pool model.
DEFAULT_CONCURRENCY = 8


class MotorFetcher:
    """A POOL of fingerprint-coherent curl_cffi GET sessions for motor.es (listing + PDP).

    A single curl_cffi Session is NOT safe to call from several threads at once, and the
    governor runs each fetch in its own worker thread (asyncio.to_thread) — so a concurrent
    drain with ONE shared session would race the session's internal state. The fix is a small
    bounded POOL: one Session per concurrency slot, each its own Chrome fingerprint + cookie
    jar. The governor's per-host bucket still bounds the AGGREGATE rate across the whole pool,
    so widening the pool widens parallelism WITHOUT out-pacing the host. `last_status` reflects
    the most recent GET across the pool — sufficient for the breaker's http_status signal."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate="chrome131")
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch_text(self, url: str, *, headers: dict | None = None, slot: int = 0) -> str:
        """The synchronous GET on pool session `slot` (runs in a worker thread via the
        governor). Raises on a non-200 so the caller sees the failure (the breaker must
        catch throttling) — never masks a challenge/empty body."""
        session = self._sessions[slot]
        merged = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                 "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"),
                  "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"}
        if headers:
            merged.update(headers)
        resp = session.get(url, headers=merged, impersonate="chrome131", timeout=40)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url}")
        return resp.text

    async def fetch_async(self, governed_fetch, url: str, *, headers: dict | None = None) -> str:
        """Lease a pool slot, fetch THROUGH the governor on that slot, release it. The slot
        lease guarantees no two concurrent coroutines ever touch the same session."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, headers=headers, slot=slot)
        finally:
            self._free.put_nowait(slot)


def _configure_motor_host(rate_per_sec: float = 3.0) -> None:
    """Pace www.motor.es on its own bucket. The recipe verified a permissive Cloudflare
    (HTTP 200 first hit, no challenge), so motor.es earns a faster bucket than the AS24/coches
    scar default — but still polite and on the same per-host choke point. A PDP-heavy drain
    (one PDP per car) needs throughput the 0.5 req/s scar default would make impractically
    slow, and motor.es is t0/t1_soft-open. The aggregate rate is the governor's bucket, NOT
    the concurrency width."""
    gov = governor()
    gov.configure_host("www.motor.es", rate_per_sec=rate_per_sec, burst=rate_per_sec * 2,
                       min_spacing_s=0.05, jitter_s=0.05)
    gov.configure_host("motor.es", rate_per_sec=rate_per_sec, burst=rate_per_sec * 2,
                       min_spacing_s=0.05, jitter_s=0.05)


async def _declared_total(governed_fetch) -> int | None:
    """Read the live census denominator from SURFACE B (get-data-ajax data.total)."""
    try:
        body = await governed_fetch(AJAX_URL, headers=_AJAX_HEADERS)
        data = json.loads(body).get("data") or {}
        return _to_int(data.get("total"))
    except Exception:  # noqa: BLE001 — the denominator is honesty-only, never blocks the drain
        return None


async def _facet(fetcher: "MotorFetcher", governed_fetch, path: str) -> tuple[int | None, str]:
    """GET a facet listing; return (its own result total, its HTML). One warm GET per facet,
    leased on a pool slot through the governor."""
    body = await fetcher.fetch_async(governed_fetch, f"{_BASE}/segunda-mano/{path}/",
                                     headers=_LIST_HEADERS)
    return _facet_total(body), body


async def build_cells(fetcher: "MotorFetcher", governed_fetch, stats: dict) -> list[str]:
    """Enumerate the MECE partition cells (recipe Vector 5).

    1) makes = 1-seg sidebar slugs that are NOT provinces.
    2) For each make: read its total.
         total <= LEAF_MAX  -> the make is one cell (drainable whole).
         else               -> split by model; each model leaf is a cell. If a model leaf is
                               STILL > LEAF_MAX, add the province 3rd level (one cell/province).
    Returns the ordered list of leaf paths to drain. Every leaf stays under the 50-page cap,
    and make->model is MECE, so the union of cells = the full census. (Pure enumeration —
    drained identically by the bounded proof and the --full run; only the count differs.)"""
    root = await fetcher.fetch_async(governed_fetch, f"{_BASE}{LIST_PATH}", headers=_LIST_HEADERS)
    all_1seg = sorted(set(_ONE_SEG_RE.findall(root)))
    makes = [x for x in all_1seg if x not in PROVINCE_SLUGS]
    stats["makes_discovered"] = len(makes)

    cells: list[str] = []
    for make in makes:
        total, body = await _facet(fetcher, governed_fetch, make)
        if total is None:
            continue
        if total <= LEAF_MAX:
            cells.append(make)
            continue
        # split by model
        for model in _sub_slugs(make, body):
            mtotal, mbody = await _facet(fetcher, governed_fetch, f"{make}/{model}")
            if mtotal is None:
                # unknown total: still drain the leaf (≤50 pages bounds it)
                cells.append(f"{make}/{model}")
                continue
            if mtotal > LEAF_MAX:
                stats["province_split_leaves"] += 1
                for prov in sorted(PROVINCE_SLUGS):
                    cells.append(f"{make}/{model}/{prov}")
            else:
                cells.append(f"{make}/{model}")
    stats["cells_enumerated"] = len(cells)
    return cells


async def drain_cell(fetcher: "MotorFetcher", governed_fetch, path: str,
                     seen_ids: set[str], stats: dict) -> list[CardRef]:
    """Drain ONE partition cell: ?pagina=1..min(50, ceil(total/22)). Parse each page's cards,
    dedup on data-id ACROSS cells (the recipe's drift/overlap absorber). Returns the NEW
    CardRefs this cell contributed (deduped), to be PDP-enriched and caged.

    Listing pages are read IN ORDER (a sequential walk is required to detect the cell's last
    page / the 50-cap 404 cleanly), each through the governor on a leased pool slot."""
    new_cards: list[CardRef] = []
    for p in range(1, CAP_PAGES + 1):
        url = f"{_BASE}/segunda-mano/{path}/" + (f"?pagina={p}" if p > 1 else "")
        try:
            html = await fetcher.fetch_async(governed_fetch, url, headers=_LIST_HEADERS)
        except Exception:  # noqa: BLE001 — a 404 past the cell's last page ends it cleanly
            break
        stats["pages_fetched"] += 1
        cards = _parse_cards(html)
        if not cards:
            break  # past the cell's last real page (or the 50-cap 404 caught above)
        for card in cards:
            stats["cards_seen"] += 1
            if card.listing_id in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue  # cross-cell dedup (facet overlap / live drift)
            seen_ids.add(card.listing_id)
            new_cards.append(card)
    return new_cards


async def harvest(max_cells: int = DEFAULT_MAX_CELLS, limit: int = DEFAULT_LIMIT,
                  full: bool = False, concurrency: int = DEFAULT_CONCURRENCY,
                  rate_per_sec: float = 3.0) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    fetcher = MotorFetcher(pool_size=concurrency)  # one coherent session per concurrency slot
    stats = {
        "makes_discovered": 0, "cells_enumerated": 0, "province_split_leaves": 0,
        "cells_drained": 0, "pages_fetched": 0, "cards_seen": 0, "pdp_fetched": 0,
        "pdp_failed": 0, "no_dealer_skipped": 0, "geo_skipped": 0, "new_dealers": 0,
        "cars_caged": 0, "new_cars": 0, "edges_created": 0, "new_events": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "dealers_distinct": 0,
        "full": full, "concurrency": concurrency,
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

    # GOVERNOR: the single per-host choke point. wrap_fetch_text takes the fetcher's GET;
    # every listing page AND every PDP passes through www.motor.es's token bucket, off the
    # event loop. No matter how wide the pool, the host is never hammered — the bucket
    # (rate_per_sec) is the aggregate limiter, not the concurrency width.
    _configure_motor_host(rate_per_sec=rate_per_sec)
    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_text)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = motor_platform_cdp_code()
        print(f"[motor_es_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid})")
        print(f"[motor_es_wholesale] governor paces host {host_of(_BASE)} (per-host token bucket).")
        stats["declared_full"] = await _declared_total(governed_fetch)

        # Enumerate the MECE partition (identical for proof and --full).
        try:
            cells = await build_cells(fetcher, governed_fetch, stats)
        except Exception as e:  # noqa: BLE001 — taxonomy fetch failed: stop honestly
            fetch_error = str(e)
            last_http = fetcher.last_status
            print(f"[motor_es_wholesale] partition enumeration failed ({e}); stopping.")
            cells = []

        if full:
            cells_to_drain = cells
            print(f"[motor_es_wholesale] FULL drain: {len(cells)} cells -> the entire "
                  f"~{stats['declared_full']} census (make->model MECE partition).")
        else:
            cells_to_drain = cells[:max(0, max_cells)]
            print(f"[motor_es_wholesale] PROOF: draining {len(cells_to_drain)} of {len(cells)} "
                  f"COMPLETE cells (<= {limit} cars; declared full ~{stats['declared_full']}; "
                  f"full drain = same command + --full).")

        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        stop = False
        for path in cells_to_drain:
            if stop:
                break
            # Drain the whole cell's card list (≤50 pages), deduped on data-id across cells.
            try:
                new_cards = await drain_cell(fetcher, governed_fetch, path, seen_ids, stats)
            except Exception as e:  # noqa: BLE001 — a cell-level fetch error stops honestly
                fetch_error = str(e)
                last_http = fetcher.last_status
                print(f"[motor_es_wholesale] cell '{path}' fetch failed ({e}); stopping drain honestly.")
                break
            stats["cells_drained"] += 1

            # ENRICH the cell's NEW cards CONCURRENTLY: the dealer identity lives ONLY on the
            # PDP, so each card needs one PDP GET. Fan out the PDP fetches across the pool
            # (the governor's bucket bounds the aggregate rate), then parse+resolve IN CARD
            # ORDER so dedup/stats/cageable truth stay deterministic. A failed PDP is skipped,
            # never fatal. The whole cell is then ingested in ONE bulk transaction.
            pdp_results = await asyncio.gather(
                *(fetcher.fetch_async(governed_fetch, c.pdp_url, headers=_LIST_HEADERS)
                  for c in new_cards),
                return_exceptions=True,
            )
            cage: list[_CageRow] = []
            for card, pdp_html in zip(new_cards, pdp_results):
                if isinstance(pdp_html, Exception):  # one bad PDP must not stop the drain
                    stats["pdp_failed"] += 1
                    last_http = fetcher.last_status
                    continue
                stats["pdp_fetched"] += 1

                d = parse_pdp_dealer(pdp_html, card)
                if d is None:
                    stats["no_dealer_skipped"] += 1
                    continue
                # Resolve the dealer province: prefer the card's parenthetical province name
                # (the dealer's selling location); fall back to the concesionario path slug.
                prov = geo.province_code(card.province_name) or geo.province_code(d.prov_slug)
                if not prov or not (prov.isdigit() and "01" <= prov <= "52"):
                    stats["geo_skipped"] += 1
                    continue
                d.province_code = prov
                muni = geo.municipality_code(prov, d.city)
                dealer_cdp = cdp_code_dealer(d, muni)

                v = parse_pdp_vehicle(pdp_html, card)
                if not v.deep_link:
                    continue
                dealer_ref = f"{d.prov_slug}/{d.slug}"
                harvested_cageable.add((dealer_ref, v.deep_link))
                cage.append(_CageRow(
                    dealer_ref=dealer_ref, dealer_cdp=dealer_cdp, dealer_name=d.name,
                    dealer_province=prov, dealer_muni=muni, vehicle=v))

                if not full and len(harvested_cageable) >= limit:
                    print(f"[motor_es_wholesale] reached --limit {limit} cars; "
                          f"finishing this cell's ingest then stopping.")
                    stop = True
                    break

            # BULK-ingest the whole cell in ONE transaction (set-based SQL, full contract).
            await _ingest_cell(conn, platform_ulid, cage, stats)
            print(f"[motor_es_wholesale] cell '{path}': new_cards={len(new_cards)} "
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

        # VAM count quorum — THREE orthogonal like-with-like paths that all measure "distinct
        # cageable cars caged so far" (DB write truth / DB read truth / harvest truth). The
        # declared full (~51k) is reported for honesty but is NOT a quorum path (it measures
        # the WHOLE platform, not what THIS run drained).
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
        # trips the breaker on a ban, and auto-repairs. OK when >=1 cell drained, no fetch
        # error stopped the drain, and the VAM did not refute.
        run_ok = fetch_error is None and stats["cells_drained"] > 0 and verdict != "REFUTED"
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
    mode = "FULL CENSUS" if stats.get("full") else "PROOF (bounded cells)"
    print(f"MOTOR.ES WHOLESALE HARVEST — {mode} REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  declared full (source): {stats.get('declared_full')}")
    print(f"  concurrency (PDP pool): {stats.get('concurrency')}")
    print(f"  makes discovered      : {stats.get('makes_discovered')}")
    print(f"  cells enumerated      : {stats.get('cells_enumerated')} "
          f"({stats.get('province_split_leaves')} model leaves needed a province split)")
    print(f"  cells drained         : {stats.get('cells_drained')}")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  cards seen            : {stats['cards_seen']}")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-cell)")
    print(f"  PDPs fetched          : {stats['pdp_fetched']} ({stats['pdp_failed']} failed)")
    print(f"  no-dealer skipped     : {stats['no_dealer_skipped']} (PDP had no concesionario)")
    print(f"  geo skipped (bad prov): {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for motor.es = {stats.get('db_edges')})")
    print(f"  NEW delta events      : {stats['new_events']}")
    print("  --- VAM count quorum (like-with-like, this run) ---")
    print(f"  harvested_cageable    : {stats.get('harvested_cageable')}")
    print(f"  db_edges              : {stats.get('db_edges')}")
    print(f"  db_join_vehicles      : {stats.get('db_join_vehicles')}")
    print(f"  VAM verdict           : {stats.get('verdict')}")
    print(f"  health status         : {stats.get('health_status')} / breaker {stats.get('breaker_state')}")
    print(f"  recipe                : {stats.get('recipe_path')}")
    print("=" * 64)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="motor.es wholesale harvester (make->model facet partition, full-coverage)")
    parser.add_argument("--full", action="store_true",
                        help="drain ALL partition cells = the entire ~51k census in one command")
    parser.add_argument("--max-cells", type=int, default=DEFAULT_MAX_CELLS,
                        help=f"PROOF mode: complete cells to drain; default {DEFAULT_MAX_CELLS} "
                             f"(ignored with --full)")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                        help=f"PROOF mode: max cars to cage this run; default {DEFAULT_LIMIT} "
                             f"(ignored with --full)")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"PDP-enrichment fan-out width per cell; default {DEFAULT_CONCURRENCY}. "
                              f"The governor's per-host bucket is the real limiter — this only "
                              f"needs to keep the bucket saturated."))
    parser.add_argument("--rate", type=float, default=3.0,
                        help=("aggregate req/s for www.motor.es (the governor bucket). Default 3.0 "
                              "(polite for the permissive Cloudflare). The host is never fetched "
                              "faster than this regardless of --concurrency."))
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.max_cells, args.limit, args.full,
                                args.concurrency, args.rate))
    _print_report(stats)


if __name__ == "__main__":
    main()
