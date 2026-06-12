"""autocasion WHOLESALE harvester — the THIRD giant marketplace, end to end.

autocasion.com (Grupo Luike / Vocento) is a Tier-1 motor marketplace whose public
surfaces are FREE to a Chrome TLS fingerprint (curl_cffi chrome131): Cloudflare is
permissive (no JS challenge), so it is is_tier1=TRUE but defense_tier='t1_soft'
(a WAF that serves to curl_cffi, not a hard sensor). Verified live 2026-06-12
(docs/architecture/tier1_recipes/autocasion.md): ~115k cars, dealer attribution
via PDP JSON-LD AutoDealer.

Unlike coches.net's single open JSON API, autocasion needs a THREE-surface chain
(all FREE, all routed through the per-host governor):

  1. ENUMERATE  — SSR results page  GET www.autocasion.com/coches-ocasion?page=N
                  -> regex `-ref(\\d+)` yields the PDP url + native ad id per card.
  2. HYDRATE    — GraphQL            POST gql.autocasion.com/graphql/ ad(adId:N){...}
                  -> the full structured car (make/model/year/price/km/fuel/trans/prov).
  3. ATTRIBUTE  — PDP JSON-LD        GET www.autocasion.com{pdp_url}
                  -> offers.offeredBy = AutoDealer (name, /profesional slug, address,
                     postcode) — the dealer-attribution surface (advertiser is null on
                     the GraphQL ad() resolver, so the dealer MUST come from the PDP).

This module mirrors pipeline.platform.coches_net_wholesale EXACTLY (same dual-
membership model, same caging, same governor/health/VAM wiring). It proves a THIRD
platform flows through ONE architecture, not a fork of it:

  autocasion (the marketplace)  -> entity, kind='plataforma'  (+ platform_meta)
  each SELLING DEALER           -> entity, kind='compraventa' (geo-resolved)
  each CAR                      -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the platform       -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the dealer); platform membership is plural (this edge). The
same physical car can carry an AS24, a coches.net AND an autocasion edge without
ever changing its owning dealer.

PROOF SLICE, NOT THE FULL HARVEST. autocasion declares ~115k results (GraphQL
search.paginatedAds.total). Draining all of it (~4,800 SSR pages @ ~24 cards) needs
the full governed run (spend/rate budget, page-window stability). Here we cap at
--pages (default ~180 pages x ~24 = ~4,300 cars) and log the cap honestly. The
declared full count is recorded for the VAM verdict's slice arithmetic.

Engine: GET (SSR/PDP) + POST (GraphQL) against autocasion's two hosts, BOTH routed
THROUGH the per-host governor (the same single choke point AS24/coches.net use).
The synchronous curl_cffi calls run in worker threads so the event loop is never
blocked, and no host is fetched faster than its bucket.

Run: python -m pipeline.platform.autocasion_wholesale --pages 180
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
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
# autocasion platform identity (00-TIER1-REGISTRY; recipe autocasion.md).
# ---------------------------------------------------------------------------
AC_DOMAIN = "autocasion.com"
AC_WEBSITE = "autocasion.com"
AC_TRADE_NAME = "Autocasion"
AC_SOURCE_KEY = "autocasion_wholesale"
AC_WAF = "cloudflare"  # Cloudflare-permissive (serves to curl_cffi) -> t1_soft.

# Multi-axis classification the platform entity carries (migrations/0016).
AC_DEFENSE_TIER = "t1_soft"          # WAF present but serving to curl_cffi.
AC_SOURCE_GROUP = "marketplace_motor"  # car-specialist marketplace.
AC_ROLE = "platform"

# The working request surfaces (recipe TL;DR; verified live 2026-06-12).
SSR_HOST = "https://www.autocasion.com"
SSR_RESULTS = SSR_HOST + "/coches-ocasion"          # GET ?page=N -> -ref(\d+) enumeration
GQL_ENDPOINT = "https://gql.autocasion.com/graphql/"  # POST ad(adId:N){...} hydration
_PDP_BASE = SSR_HOST                                  # PDP url is a relative path

# SSR card -> PDP url + native ad id. `-ref{ID}` is autocasion's native listing id.
_REF_RE = re.compile(r'href="(/coches-[^"]*-ref(\d+))"')

# PDP JSON-LD Product block (one per page; offers.offeredBy = AutoDealer).
_LDJSON_RE = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S)

_IMPERSONATE = "chrome131"
_TIMEOUT = 40
_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
_HTML_HEADERS = {"User-Agent": _UA, "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"}
_GQL_HEADERS = {
    "User-Agent": _UA,
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://www.autocasion.com",
    "Referer": "https://www.autocasion.com/coches-segunda-mano",
}

# GraphQL ad() projection — the full structured car (advertiser is null here; dealer
# comes from the PDP JSON-LD). Field names inspected live, NOT assumed.
_AD_QUERY = (
    "{ ad(adId:%d){ id title name price finalPrice kilometers year month km0 "
    "certificated url slug fuel{name} transmission{name} brand{name} family{name} "
    "province{name} } }")
# GraphQL search() counter — true total/pages (ads[] is gated null; counter only).
_SEARCH_QUERY = (
    "query S($p:[SearchParamInput],$page:Int,$ipp:Int){"
    "search(params:$p,page:$page,itemsPerPage:$ipp){paginatedAds{total pages itemsPerPage}}}")

# Province sentinel '00' = national (same convention as AS24/coches.net). geo_province
# has NO '00', so the platform ENTITY stores province_code = NULL; '00' lives only
# inside the cdp_code string (free text, no FK).
PLATFORM_PROVINCE_SENTINEL = "00"

DEFAULT_MAX_PAGES = 180   # ~180 SSR pages x ~24 cards = ~4,300 cars (proof slice).
SSR_ITEMS_PER_PAGE = 24   # autocasion SSR pages carry ~24-26 cards (recipe verified).


def autocasion_platform_cdp_code() -> str:
    """The autocasion platform's immutable cdp_code. Built from the bare domain
    identity (canonical_key 'domain:autocasion.com'), province segment '00' (national).
    Mirrors coches_net_platform_cdp_code() so all platforms mint codes the same way."""
    key = f"domain:{AC_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL response — field names inspected live, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class DealerRef:
    """The selling dealer parsed from a PDP's JSON-LD `offers.offeredBy` (AutoDealer).

    autocasion's GraphQL ad() resolver returns advertiser=null, so the dealer comes
    ONLY from the public PDP JSON-LD. The geo anchor is the PostalAddress: the Spanish
    postcode's first two digits ARE the INE province code (28933 -> 28 Madrid), and
    addressLocality resolves the municipality. The `/profesional/{slug}` @id is the
    stable per-dealer id used for cross-source dedup and as the source_ref."""
    slug: str                  # stable id from offeredBy.@id (/profesional/<slug>)
    name: str | None
    province_code: str | None  # postalCode[:2] (INE province) or resolved from city
    city: str | None
    postcode: str | None
    phone: str | None
    street: str | None


@dataclass
class Vehicle:
    """A car parsed from the GraphQL ad() hydration + PDP JSON-LD."""
    deep_link: str
    listing_ref: str           # autocasion native ad id (== -ref{ID})
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


def _prov_from_cp(postcode) -> str | None:
    """Spanish postcode's first two digits ARE the INE province code (01..52).
    28933 -> '28' (Madrid), 07180 -> '07' (Balears). Verified live."""
    if not postcode:
        return None
    s = re.sub(r"\D", "", str(postcode))
    if len(s) < 2:
        return None
    p = s[:2]
    if not ("01" <= p <= "52"):
        return None
    return p


def _slug_from_dealer_id(dealer_id) -> str | None:
    """offeredBy.@id is 'https://www.autocasion.com/profesional/<slug>'. The slug is
    the stable per-dealer identity (== the dealer's profesional page)."""
    if not dealer_id:
        return None
    m = re.search(r"/profesional/([^/?#]+)", str(dealer_id))
    return m.group(1) if m else None


def parse_ssr_refs(html: str) -> list[tuple[str, str]]:
    """Extract (pdp_url, ad_id) pairs from one SSR results page, de-duped in order.
    Pages past the last clamp to the final page, so the CALLER stops when the id-set
    stops changing (id-dedup across pages, not page position)."""
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for url, rid in _REF_RE.findall(html):
        if rid in seen:
            continue
        seen.add(rid)
        out.append((url, rid))
    return out


def parse_ad(ad: dict, pdp_url: str) -> Vehicle:
    """Parse the car from the GraphQL ad() payload (REAL field map)."""
    price = None
    amount = ad.get("price")
    if amount is not None:
        try:
            price = float(amount)
        except (TypeError, ValueError):
            price = None

    year = _to_int(ad.get("year"))
    if year is not None and not (1900 <= year <= 2100):
        year = None
    km = _to_int(ad.get("kilometers"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    url = ad.get("url") or pdp_url or ""
    deep_link = (_PDP_BASE + url) if url.startswith("/") else url

    make = (ad.get("brand") or {}).get("name")
    model = (ad.get("family") or {}).get("name")
    title = ad.get("title") or " ".join(p for p in (make, model) if p) or None

    return Vehicle(
        deep_link=deep_link,
        listing_ref=str(ad.get("id") or ""),
        title=title,
        make=make,
        model=model,
        year=year,
        km=km,
        price=price,
        fuel=(ad.get("fuel") or {}).get("name"),
        transmission=(ad.get("transmission") or {}).get("name"),
        photo_url=None,  # filled from the PDP JSON-LD (ad() image is gated null)
    )


def _is_product(node: dict) -> bool:
    t = node.get("@type")
    return t == "Product" or (isinstance(t, list) and "Product" in t)


def parse_pdp_ldjson(html: str) -> dict | None:
    """Return the first JSON-LD Product block on a PDP, or None.

    A JSON-LD <script> block can be a single object, a top-level ARRAY of objects,
    or an object carrying an @graph array (verified live: some PDPs ship a list, e.g.
    the Hyundai i40 page). We flatten every candidate node and return the first that
    is a Product. `json.loads` decodes the embedded \\uXXXX escapes to real accented
    strings (AUTOS MADRID MÓSTOLES) — no manual charset juggling needed."""
    for block in _LDJSON_RE.findall(html):
        try:
            obj = json.loads(block)
        except (json.JSONDecodeError, ValueError):
            continue
        # Flatten the block into candidate dict nodes (object | list | @graph).
        candidates: list = []
        if isinstance(obj, dict):
            candidates.append(obj)
            graph = obj.get("@graph")
            if isinstance(graph, list):
                candidates.extend(g for g in graph if isinstance(g, dict))
        elif isinstance(obj, list):
            candidates.extend(g for g in obj if isinstance(g, dict))
        for node in candidates:
            if _is_product(node):
                return node
    return None


def parse_pdp_dealer(ld: dict, geo: GeoResolver) -> DealerRef | None:
    """Parse the SELLING DEALER from a PDP JSON-LD Product's offers.offeredBy.

    Only AutoDealer professional sellers with a /profesional slug become entities.
    Province = postcode[:2] (INE), falling back to a global city resolution when the
    postcode is absent/invalid; municipality from addressLocality."""
    offers = ld.get("offers") or {}
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    seller = offers.get("offeredBy") or {}
    stype = seller.get("@type")
    is_dealer = stype == "AutoDealer" or (isinstance(stype, list) and "AutoDealer" in stype)
    if not is_dealer:
        return None
    slug = _slug_from_dealer_id(seller.get("@id"))
    if not slug:
        return None
    addr = seller.get("address") or {}
    if isinstance(addr, list):
        addr = addr[0] if addr else {}
    postcode = addr.get("postalCode")
    city = addr.get("addressLocality")
    prov = _prov_from_cp(postcode)
    if prov is None and city:
        # postcode missing/invalid: resolve province from a globally-unique city name.
        prov, _ = geo.resolve_city_global(city)
    phone = seller.get("telephone") or None
    return DealerRef(
        slug=str(slug),
        name=seller.get("name"),
        province_code=prov,
        city=city,
        postcode=str(postcode) if postcode else None,
        phone=phone.strip() if isinstance(phone, str) else None,
        street=(addr.get("streetAddress") or None),
    )


def pdp_photo(ld: dict) -> str | None:
    img = ld.get("image")
    if isinstance(img, list) and img:
        return img[0] if isinstance(img[0], str) else None
    if isinstance(img, str):
        return img
    return None


# ---------------------------------------------------------------------------
# Fetch: GET (SSR/PDP) + POST (GraphQL), one callable routed THROUGH the governor.
# ---------------------------------------------------------------------------


class AutocasionFetcher:
    """A fingerprint-coherent curl_cffi session for autocasion's three surfaces.

    One session == one Chrome fingerprint == one cookie jar for the whole drain, so
    the paginated harvest looks like one browser. A homepage warm-up mints Cloudflare
    cookies before any GraphQL POST. The governor wraps `fetch` to pace requests by
    the host bucket (gql.autocasion.com and www.autocasion.com are SEPARATE buckets);
    this class only performs the actual HTTP.
    """

    def __init__(self) -> None:
        self._session = cffi_requests.Session(impersonate=_IMPERSONATE)
        self.last_status: int | None = None
        # Light warm-up: mint Cloudflare cookies on www before the GraphQL POST origin.
        try:
            self._session.get(SSR_HOST + "/", headers=_HTML_HEADERS,
                              impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        except Exception:  # noqa: BLE001 — warm-up is best-effort hardening, not required.
            pass

    def fetch(self, url: str, *, method: str = "GET", gql: dict | None = None) -> str:
        """Perform the HTTP for `url` and return decoded UTF-8 text/JSON-string.

        `url` is passed so the governor can derive the host and pace the bucket. GET
        is the SSR/PDP surface (HTML); a `gql` payload triggers a GraphQL POST. Raises
        on a non-200 so the breaker catches throttling (never masks a challenge)."""
        if method == "POST":
            resp = self._session.post(url, json=gql, headers=_GQL_HEADERS,
                                      impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        else:
            resp = self._session.get(url, headers=_HTML_HEADERS,
                                     impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url}")
        # Decode explicitly so accented dealer/city/fuel names survive curl_cffi's guess.
        return resp.content.decode("utf-8", "replace")


# ---------------------------------------------------------------------------
# DB layer (mirrors coches_net_wholesale: ensure platform, upsert dealer/vehicle,
# link edge, emit delta, all idempotent ON CONFLICT).
# ---------------------------------------------------------------------------

AC_PLATFORM_RECIPE = {
    "version": 1,
    "source": "autocasion.com",
    "scope": "platform-wholesale (SSR enumerate -> GraphQL ad() hydrate -> PDP JSON-LD dealer)",
    "engine": "curl_cffi+chrome131_impersonate+graphql(POST)+ssr/pdp(GET)",
    "access": ("FREE: Cloudflare-permissive to a Chrome TLS fingerprint (no proxy, no "
               "browser, no captcha). is_tier1=TRUE (Tier-1 motor brand) but "
               "defense_tier=t1_soft (WAF serves to curl_cffi). GraphQL introspection open."),
    "data_surface": "graphql",
    "surface_intent": "graphql+json_ld",
    "endpoints": {
        "enumerate": "GET https://www.autocasion.com/coches-ocasion?page=N",
        "hydrate": "POST https://gql.autocasion.com/graphql/  ad(adId:N){...}",
        "dealer": "GET https://www.autocasion.com{pdp_url}  (JSON-LD offers.offeredBy=AutoDealer)",
    },
    "enumeration": ("SSR results pages 1..N (regex -ref(\\d+) -> pdp_url + native id); "
                    "GraphQL search.paginatedAds.total/pages = the live counter (~115k/4800)"),
    "platform_entity": ("kind=plataforma, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=TRUE, defense_tier=t1_soft, source_group=marketplace_motor, role=platform"),
    "dual_membership": "vehicle.entity_ulid=SELLING DEALER (compraventa); platform_listing edge=platform<->vehicle",
    "field_map": {
        "listing_ref": "ad.id | ld.offers.itemOffered.identifier (native -ref{ID})",
        "deep_link": "https://www.autocasion.com + ad.url",
        "make": "ad.brand.name | ld.offers.itemOffered.manufacturer",
        "model": "ad.family.name | ld.offers.itemOffered.model",
        "title": "ad.title | ld.name",
        "year": "ad.year | ld.offers.itemOffered.productionDate",
        "km": "ad.kilometers | ld.offers.itemOffered.mileageFromOdometer.value",
        "price": "ad.price | ld.offers.price (EUR)",
        "fuel": "ad.fuel.name",
        "transmission": "ad.transmission.name | ld.offers.itemOffered.vehicleTransmission",
        "photo_url": "ld.image[0] (ad.image is gated null)",
        "dealer": "ld.offers.offeredBy {name, @id(/profesional/slug), telephone, @type=AutoDealer}",
        "location": "ld.offers.offeredBy.address {postalCode(->province=CP[:2]), addressLocality(->municipality)}",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the autocasion platform entity + platform_meta exist.
    Returns the platform entity_ulid. is_tier1=TRUE (Tier-1 brand) but the multi-axis
    classification is explicit: defense_tier=t1_soft, source_group=marketplace_motor,
    role=platform (migrations/0016). data_surface='graphql' (schema-valid value)."""
    code = autocasion_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               defense_tier, source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,'plataforma',$3,$3,NULL,$4,$5,TRUE,'active','platform_label',
               $6,$7,$8,$9, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, website_waf = EXCLUDED.website_waf,
               defense_tier = EXCLUDED.defense_tier, source_group = EXCLUDED.source_group,
               role = EXCLUDED.role""",
        eulid, code, AC_TRADE_NAME, AC_WEBSITE, AC_WAF,
        AC_DEFENSE_TIER, AC_SOURCE_GROUP, AC_ROLE, AC_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, AC_SOURCE_KEY, AC_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'graphql',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({
            "enumerate": SSR_RESULTS, "hydrate": GQL_ENDPOINT,
            "gql_host": host_of(GQL_ENDPOINT), "ssr_host": host_of(SSR_RESULTS),
            "surface_intent": "graphql+json_ld", "items_per_page": SSR_ITEMS_PER_PAGE,
            "engine": "curl_cffi/chrome131_impersonate"}),
        "autocasion")
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    autocasion dealers have no bare domain on this surface -> identity = name +
    location + the stable /profesional slug (passed via `address` so two distinct
    profesional pages that share a name in one municipality never collapse to one)."""
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni, address=f"profesional:{d.slug}")


async def upsert_dealer(conn: asyncpg.Connection, geo: GeoResolver, d: DealerRef) -> str | None:
    """Upsert the selling dealer entity (kind='compraventa', sells_cars=TRUE, geo-resolved).
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
               province_code, municipality_code, postcode, phone, address, is_tier1,
               status, kind_source, sells_cars, role, first_discovered_source, last_seen)
           VALUES ($1,$2,'compraventa',$3,$3,$4,$5,$6,$7,$8,FALSE,'active','platform_label',
               TRUE,'standalone_pos',$9, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()""",
        eulid, code, d.name, d.province_code, muni, d.postcode, d.phone, d.street,
        AC_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, AC_SOURCE_KEY, d.slug)
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
    payload = {"price": v.price, "title": v.title, "platform": AC_TRADE_NAME}
    await conn.execute(
        "INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type, "
        "old_value, new_value) VALUES ($1,$2,$3,'NEW',NULL,$4::jsonb)",
        ulid(), vulid, dealer_ulid, json.dumps(payload))


async def capture_price_drop(conn: asyncpg.Connection, platform_ulid: str, vulid: str,
                             dealer_ulid: str, v: Vehicle) -> bool:
    """If the platform_price on the edge changed vs the last seen value, record a
    PRICE_CHANGE delta event (autocasion has no explicit priceDropData like coches.net,
    so the drop is detected by comparing the prior edge price to the current price).
    Returns True if a price-change event was recorded."""
    prior = await conn.fetchval(
        "SELECT platform_price FROM platform_listing "
        "WHERE vehicle_ulid=$1 AND platform_entity_ulid=$2", vulid, platform_ulid)
    if prior is None or v.price is None:
        return False
    if float(prior) == float(v.price):
        return False
    await conn.execute(
        "INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type, "
        "old_value, new_value) VALUES ($1,$2,$3,'PRICE_CHANGE',$4::jsonb,$5::jsonb)",
        ulid(), vulid, dealer_ulid,
        json.dumps({"price": float(prior)}),
        json.dumps({"price": float(v.price), "platform": AC_TRADE_NAME}))
    return True


# ---------------------------------------------------------------------------
# Per-ref hydrate -> dealer -> cage. ONE car, end to end, fully guarded. This is the
# proven cage path extracted verbatim so BOTH the flat wholesale drain and the
# make-partition facet drain (pipeline.platform.autocasion_facet) share it byte-for-byte
# — same GraphQL ad() hydrate, same PDP JSON-LD dealer, same per-car transaction, same
# delta NEW / PRICE_CHANGE rules, same ON CONFLICT idempotency. `seen_ids` and
# `harvested_cageable` are passed in so a caller can keep ONE global dedup set across
# pages AND partitions (the live-set-shift + cross-slice-overlap guard).
# ---------------------------------------------------------------------------


async def process_ref(conn: asyncpg.Connection, geo: GeoResolver, platform_ulid: str,
                      governed_fetch, pdp_url: str, ad_id: str,
                      seen_ids: set[str], harvested_cageable: set[tuple[str, str]],
                      stats: dict) -> int | None:
    """Hydrate + attribute + cage ONE ad. Returns fetcher.last_status on a fetch error
    (so the caller can feed the breaker), else None. Updates stats and the global sets
    in place. A single bad ad/PDP NEVER aborts the drain (resilience doctrine)."""
    stats["refs_seen"] += 1
    if ad_id in seen_ids:
        stats["dup_ids_collapsed"] += 1
        return None   # id-dedup across pages AND partitions (live-set-shift guard)
    seen_ids.add(ad_id)

    # Step 2 — hydrate the car (GraphQL ad()).
    try:
        ad_raw = await governed_fetch(
            GQL_ENDPOINT, method="POST", gql={"query": _AD_QUERY % int(ad_id)})
        ad = ((json.loads(ad_raw).get("data") or {}).get("ad")) or None
    except Exception:  # noqa: BLE001 — one ad failing is not fatal.
        stats["fetch_errors"] += 1
        return "fetch"
    if not ad:
        stats["fetch_errors"] += 1
        return None
    stats["ads_hydrated"] += 1
    v = parse_ad(ad, pdp_url)
    if not v.deep_link:
        return None

    # Step 3 — dealer attribution (PDP JSON-LD).
    try:
        pdp_html = await governed_fetch(_PDP_BASE + pdp_url)
    except Exception:  # noqa: BLE001
        stats["fetch_errors"] += 1
        return "fetch"
    stats["pdp_fetched"] += 1
    try:
        ld = parse_pdp_ldjson(pdp_html)
        if ld is None:
            stats["private_skipped"] += 1
            return None
        d = parse_pdp_dealer(ld, geo)
        if d is None:
            stats["private_skipped"] += 1   # private seller / no AutoDealer
            return None
        if v.photo_url is None:
            v.photo_url = pdp_photo(ld)

        async with conn.transaction():
            dealer_ulid = await upsert_dealer(conn, geo, d)
            if dealer_ulid is None:
                stats["geo_skipped"] += 1
                return None
            harvested_cageable.add((d.slug, v.deep_link))
            vulid, veh_new = await upsert_vehicle(conn, dealer_ulid, v)
            stats["cars_caged"] += 1
            if not veh_new:
                if await capture_price_drop(conn, platform_ulid, vulid, dealer_ulid, v):
                    stats["price_changes_captured"] += 1
            if veh_new:
                stats["new_cars"] += 1
                await emit_new_event(conn, vulid, dealer_ulid, v)
                stats["new_events"] += 1
            edge_new = await link_platform(conn, platform_ulid, vulid, v)
            if edge_new:
                stats["edges_created"] += 1
    except Exception as e:  # noqa: BLE001 — one bad car never sinks the drain.
        stats["parse_errors"] += 1
        print(f"[autocasion] car {ad_id} parse/cage failed ({e!r}); skipping.")
    return None


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


async def harvest(max_pages: int = DEFAULT_MAX_PAGES, limit: int | None = None) -> dict:
    conn = await asyncpg.connect(DSN)
    fetcher = AutocasionFetcher()  # one fingerprint + cookie jar for the whole drain
    stats = {
        "pages_fetched": 0, "refs_seen": 0, "ads_hydrated": 0, "pdp_fetched": 0,
        "private_skipped": 0, "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "price_changes_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "fetch_errors": 0,
        "parse_errors": 0, "dealers_distinct": 0,
    }
    # Harvest-side truth for the VAM: distinct CAGEABLE cars = distinct (slug, deep_link)
    # pairs that survived dealer-parse + geo-resolution. Like-with-like vs db_edges.
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if autocasion's breaker is OPEN (a recent ban/throttle still
    # cooling), skip the drain gracefully — the system keeps serving the last snapshot.
    if await is_open(conn, AC_SOURCE_KEY):
        print(f"[autocasion_wholesale] breaker OPEN for {AC_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, last snapshot still served).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": AC_SOURCE_KEY}

    # GOVERNOR: the single per-host choke point. wrap_fetch_text takes our fetch
    # callable; EVERY request (SSR/GraphQL/PDP) passes through its host's token bucket,
    # off the event loop. gql.autocasion.com and www.autocasion.com are SEPARATE buckets.
    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = autocasion_platform_cdp_code()
        print(f"[autocasion_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid})")
        print(f"[autocasion_wholesale] governor paces hosts {host_of(SSR_RESULTS)} + "
              f"{host_of(GQL_ENDPOINT)} (per-host token buckets).")
        print(f"[autocasion_wholesale] PROOF SLICE cap = {max_pages} SSR pages "
              f"(~{max_pages * SSR_ITEMS_PER_PAGE} cars). NOT the full ~115k set.")

        # Counter (GraphQL search) — true total/pages for the slice arithmetic.
        try:
            counter_raw = await governed_fetch(
                GQL_ENDPOINT, method="POST",
                gql={"query": _SEARCH_QUERY, "variables": {"p": [], "page": 1, "ipp": SSR_ITEMS_PER_PAGE}})
            pag = (((json.loads(counter_raw).get("data") or {}).get("search") or {})
                   .get("paginatedAds") or {})
            stats["declared_full"] = _to_int(pag.get("total"))
        except Exception as e:  # noqa: BLE001 — counter is informational, not fatal.
            print(f"[autocasion_wholesale] counter probe failed ({e}); continuing.")

        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        for page in range(1, max_pages + 1):
            # Step 1 — enumerate ad ids from the SSR results page.
            try:
                html = await governed_fetch(f"{SSR_RESULTS}?page={page}")
            except Exception as e:  # noqa: BLE001
                fetch_error = str(e)
                last_http = fetcher.last_status
                print(f"[autocasion_wholesale] SSR page {page} failed ({e}); stopping drain honestly.")
                break
            stats["pages_fetched"] += 1
            refs = parse_ssr_refs(html)
            if not refs:
                print(f"[autocasion_wholesale] page {page}: no refs; stopping.")
                break

            new_on_page = 0
            for pdp_url, ad_id in refs:
                if limit is not None and stats["cars_caged"] >= limit:
                    break  # hard cap reached mid-page; stop hydrating further ads.
                if ad_id not in seen_ids:
                    new_on_page += 1
                # Hydrate + attribute + cage ONE ad through the shared, proven cage path.
                err = await process_ref(conn, geo, platform_ulid, governed_fetch,
                                         pdp_url, ad_id, seen_ids, harvested_cageable, stats)
                if err == "fetch":
                    last_http = fetcher.last_status

            print(f"[autocasion_wholesale] page {page}: refs={len(refs)} new={new_on_page} "
                  f"caged_total={stats['cars_caged']} edges={stats['edges_created']}")
            if limit is not None and stats["cars_caged"] >= limit:
                print(f"[autocasion_wholesale] --limit {limit} reached "
                      f"({stats['cars_caged']} caged); stopping.")
                break
            if new_on_page == 0:
                print(f"[autocasion_wholesale] page {page}: all ids already seen (clamped end); stopping.")
                break

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, AC_PLATFORM_RECIPE)
        print(f"[autocasion_wholesale] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths that
        # all measure "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for autocasion (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join     (DB read truth)
        #   harvested_cageable = distinct (slug, deep_link) pulled        (harvest truth)
        # The declared full count (~115k) is reported for honesty, NOT a quorum path.
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

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks autocasion,
        # trips the breaker on a ban, and auto-repairs. OK when >=1 page fetched, no fetch
        # error stopped the drain, and the VAM did not refute.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, AC_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, AC_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[autocasion_wholesale] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("AUTOCASION WHOLESALE HARVEST — PROOF SLICE REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  declared full (source): {stats.get('declared_full')}  (NOT harvested — proof slice)")
    print(f"  SSR pages fetched     : {stats['pages_fetched']}")
    print(f"  refs seen             : {stats['refs_seen']}")
    print(f"  ads hydrated (gql)    : {stats['ads_hydrated']}")
    print(f"  PDPs fetched          : {stats['pdp_fetched']}")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page)")
    print(f"  private/no-dealer skip: {stats['private_skipped']}")
    print(f"  geo skipped (bad prov): {stats['geo_skipped']}")
    print(f"  fetch errors (ad/pdp) : {stats['fetch_errors']}")
    print(f"  parse errors (skipped): {stats['parse_errors']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for autocasion = {stats.get('db_edges')})")
    print(f"  price changes captured: {stats['price_changes_captured']}")
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
    parser = argparse.ArgumentParser(description="autocasion wholesale proof-slice harvester")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"SSR pages to harvest (~{SSR_ITEMS_PER_PAGE} cars/page); "
                             f"default {DEFAULT_MAX_PAGES} (proof slice)")
    parser.add_argument("--limit", type=int, default=None,
                        help="hard cap on cars caged this run (stops early once reached)")
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.pages, args.limit))
    _print_report(stats)


if __name__ == "__main__":
    main()
