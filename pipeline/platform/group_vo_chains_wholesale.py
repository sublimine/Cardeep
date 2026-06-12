"""vo_chains WHOLESALE harvester — big national USED-CAR CHAINS selling from their OWN sites.

This is a SEPARATE source_group ('chain'): national used-car chains that run their own
storefront with large self-owned stock (5k-20k+ cars each). The car a buyer purchases has a
real selling point — the chain BRANCH (a physical compraventa) where stock exists per-branch,
or the chain COMPANY itself when the surface does not attribute a car to a branch. Either way
the selling point is caged as the entity and every car is OWNED BY it, exactly as a
marketplace's dealer owns its cars.

This connector opens TWO members with the cleanest data-layer surfaces (probed live 2026-06-13):

  1. FLEXICAR (flexicar.es) — kind='cadena', source_group='chain', role='chain'.
     The platform/chain entity is the brand. Each car attributes to its REAL SELLING BRANCH
     (one of 186 physical compraventa branches), so this is the per-branch owner model
     (mirrors coches_net_wholesale's per-dealer caging):
       Flexicar (the chain)          -> entity, kind='cadena'      (+ platform_meta)
       each selling BRANCH           -> entity, kind='compraventa' (geo-resolved from the branch)
       each CAR                      -> vehicle, OWNED BY its branch (entity_ulid=branch)
       the car on the chain site     -> platform_listing edge (chain_entity <-> vehicle)
     Surface: an OPEN first-party REST/JSON API. `GET https://services.flexicar.es/api/v1/vehicles
     ?page=N&size=24` returns paginated JSON {total, pages, hasNext, results[]}. `total=23874`
     live; `size` is hard-capped at 24 (>24 → HTTP 400 "size must not be greater than 24"). Each
     result carries id (native listing_ref), brand, model, version, year, km, price, previousPrice
     (price-drop delta), fuel, transmission, slug (deep-link), image, AND carDealershipSlug — the
     branch that sells it. The 186-branch directory (`__NEXT_DATA__.props.pageProps.dealerships`,
     each {value(slug), province, zipCode, location, latitude}) geo-anchors every branch. No proxy,
     no browser, no cookie warm-up — a Chrome TLS fingerprint over the JSON host (t0_open).

  2. OCASIONPLUS (ocasionplus.com) — kind='cadena', source_group='chain', role='chain'.
     The platform/chain entity IS the singular selling point on this surface: the per-car branch
     ('centro') is NOT exposed on the search-results data-layer, so we do NOT fabricate a per-branch
     owner the source withholds. The chain owns every car (owner entity == platform entity), exactly
     like OK Mobility in group_rentacar_vo_wholesale:
       OcasionPlus (the chain)       -> entity, kind='cadena' (+ platform_meta)  [SELLING POINT]
       each CAR                      -> vehicle, OWNED BY the chain (entity_ulid=chain)
       the car on the chain site     -> platform_listing edge (chain_entity <-> vehicle)
     Surface: a Next.js App-Router SSR page that emits a schema.org JSON-LD `ItemList` of 20
     `Vehicle` objects per page, each with brand, model, vehicleTransmission, fuelType,
     productionDate (year), mileageFromOdometer (km), offers.price (EUR) and offers.url (the
     per-car deep link whose tail is the native listing_ref). `?page=N` paginates server-side
     (verified: distinct car sets per page). `offers.offerCount=14052` declares the full stock.
     t0_open (x-powered-by Next.js, no Cloudflare/WAF; chrome131 serves cleanly).

BOTH members flow through the ONE proven architecture (same governor choke point, same GeoResolver,
same idempotent ON CONFLICT BULK unnest ingest, same NEW-delta events, same VAM count quorum, same
S-HEALTH heartbeat/breaker) — it mirrors coches_net_wholesale (per-branch owner) and
group_rentacar_vo_wholesale (chain-as-owner) EXACTLY. This connector simply runs both owner models
behind one orchestrator so the whole vo_chains group is one file, not a fork per chain.

PROOF SLICE, NOT THE FULL HARVEST. Flexicar declares ~23,874 cars (995 pages × 24); OcasionPlus
~14,052 (~703 pages × 20). The full drain is the full governed run; here each member caps at
MAX_PAGES (logged honestly) and the declared full count is recorded for the VAM slice arithmetic.

Run: python -m pipeline.platform.group_vo_chains_wholesale --pages 6
     python -m pipeline.platform.group_vo_chains_wholesale --members flexicar --pages 10
     python -m pipeline.platform.group_vo_chains_wholesale --members ocasionplus --pages 8
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
from dataclasses import dataclass, field

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
# vo_chains group identity (the 0016 multi-axis classification).
# ---------------------------------------------------------------------------
GROUP_SOURCE_GROUP = "chain"        # source_group: the group this connector opens.
GROUP_ROLE = "chain"                # entity_role for the chain platform entity.
CHAIN_KIND = "cadena"               # entity_kind for the chain brand entity.
BRANCH_KIND = "compraventa"         # entity_kind for a per-branch selling point.

_IMPERSONATE = "chrome131"
_TIMEOUT = 40
PLATFORM_PROVINCE_SENTINEL = "00"   # national segment for a chain's cdp_code (mirrors marketplaces).

DEFAULT_MAX_PAGES = 6
DEFAULT_CONCURRENCY = 6


def _to_int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _prov_from_zip(zipcode) -> str | None:
    """A Spanish 5-digit postal code's first two digits ARE the INE province code
    (15xxx -> 15 A Coruña, 28xxx -> 28 Madrid). Returns a zero-padded '01'..'52' or None."""
    if zipcode is None:
        return None
    digits = re.sub(r"[^\d]", "", str(zipcode))
    if len(digits) < 2:
        return None
    p = digits[:2]
    return p if "01" <= p <= "52" else None


# ===========================================================================
# Parsed shapes
# ===========================================================================


@dataclass
class Branch:
    """A Flexicar selling branch (one of 186 physical compraventa points). Geo comes from the
    branch's own zipCode (INE province) + location (municipality); the branch slug is the stable
    per-branch key carried on every car (carDealershipSlug)."""
    slug: str
    name: str | None
    province_code: str | None
    city: str | None
    zipcode: str | None


@dataclass
class Vehicle:
    """A car parsed from a chain's data-layer item (REAL field map per member)."""
    deep_link: str
    listing_ref: str            # native ad/stock id (Flexicar id; OcasionPlus slug-tail)
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    prev_price: float | None    # previous price -> price-drop delta
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    branch_slug: str | None     # the selling branch (Flexicar); None when the chain owns the car


@dataclass
class CageRow:
    """One fully-parsed, owner-resolved car ready for the bulk cage. ONE shape serves both owner
    models. Per-branch chain (Flexicar) -> owner_kind='compraventa' with a geo-resolved branch;
    chain-as-owner (OcasionPlus) -> owner_kind='cadena' (the chain entity itself owns the car)."""
    owner_cdp: str
    owner_kind: str             # 'compraventa' (branch) | 'cadena' (chain owns directly)
    owner_name: str | None
    owner_province: str | None  # INE code; NULL when not resolvable (chain-owner national)
    owner_muni: str | None
    source_ref: str             # branch slug | chain domain
    vehicle: Vehicle


# ===========================================================================
# FLEXICAR member (per-branch owner model; OPEN JSON REST API)
# ===========================================================================

FLEXI_DOMAIN = "flexicar.es"
FLEXI_LEGAL_NAME = "Flexicar"
FLEXI_TRADE_NAME = "Flexicar"
FLEXI_SOURCE_KEY = "group_vo_chains_flexicar"
FLEXI_FAMILY = "flexicar"
FLEXI_API = "https://services.flexicar.es/api/v1/vehicles"
FLEXI_SRP = "https://www.flexicar.es/coches-segunda-mano/"
FLEXI_PAGE_SIZE = 24            # hard cap: size>24 -> HTTP 400 (verified live).
FLEXI_HEADERS = {
    "Accept": "application/json",
    "Origin": "https://www.flexicar.es",
    "Referer": "https://www.flexicar.es/",
}
# fuel/transmission already arrive as clean ES labels (Gasolina/Diésel/Híbrido, Manual/Automático).


def chain_cdp_code(domain: str) -> str:
    """A chain's immutable cdp_code, built from the bare domain identity
    (canonical_key 'domain:<domain>') with the national province segment '00'. Mirrors
    coches_platform_cdp_code() so every chain mints codes the same way."""
    key = f"domain:{domain}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


def parse_flexicar_branches(next_data: dict, geo: GeoResolver) -> dict[str, Branch]:
    """Build slug -> Branch from __NEXT_DATA__.props.pageProps.dealerships (186 branches). Geo is
    the branch's own zipCode (INE province) + location (municipality) — every branch carries its
    real address, so attribution is exact, never fabricated."""
    out: dict[str, Branch] = {}
    deals = (next_data.get("props", {}).get("pageProps", {}).get("dealerships") or [])
    for d in deals:
        slug = d.get("value")
        if not slug:
            continue
        prov = _prov_from_zip(d.get("zipCode"))
        if prov is None:
            # fall back to the province name (provinceSlug/province) through the resolver.
            prov = geo.province_code(d.get("province")) or geo.province_code(d.get("provinceSlug"))
        city = d.get("location")
        out[slug] = Branch(slug=slug, name=d.get("name"), province_code=prov,
                           city=city, zipcode=str(d.get("zipCode") or "") or None)
    return out


def parse_flexicar_vehicle(item: dict) -> Vehicle | None:
    """Parse one Flexicar API result into a Vehicle, or None if it lacks a deep link/id."""
    slug = item.get("slug")
    vid = item.get("id")
    if not slug or vid is None:
        return None
    deep_link = f"https://www.flexicar.es/coches-segunda-mano/{slug}"
    year = _to_int(item.get("year"))
    if year is not None and not (1900 <= year <= 2100):
        year = None
    km = _to_int(item.get("km"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None
    price = item.get("price")
    try:
        price = float(price) if price is not None else None
    except (TypeError, ValueError):
        price = None
    prev = item.get("previousPrice")
    try:
        prev = float(prev) if prev is not None else None
    except (TypeError, ValueError):
        prev = None
    make = item.get("brand")
    model = item.get("model")
    version = item.get("version")
    title = " ".join(p for p in (make, model, version) if p) or None
    photo = item.get("image")
    if not photo:
        imgs = item.get("images")
        if isinstance(imgs, list) and imgs:
            photo = imgs[0]
    return Vehicle(
        deep_link=deep_link, listing_ref=str(vid), title=title, make=make, model=model,
        year=year, km=km, price=price, prev_price=prev, fuel=item.get("fuel"),
        transmission=item.get("transmission"), photo_url=photo,
        branch_slug=item.get("carDealershipSlug"))


# ===========================================================================
# OCASIONPLUS member (chain-as-owner model; SSR JSON-LD ItemList)
# ===========================================================================

OP_DOMAIN = "ocasionplus.com"
OP_LEGAL_NAME = "OcasionPlus"
OP_TRADE_NAME = "OcasionPlus"
OP_SOURCE_KEY = "group_vo_chains_ocasionplus"
OP_FAMILY = "ocasionplus"
OP_SRP = "https://www.ocasionplus.com/coches-segunda-mano"
OP_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.ocasionplus.com/",
}
OP_PAGE_SIZE = 20  # the JSON-LD ItemList carries 20 Vehicle objects per SRP page.

_LD_RE = re.compile(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S)
# OcasionPlus transmission codes in the JSON-LD: AUTO/MANUAL -> human label.
_OP_TRANS = {"AUTO": "Automático", "MANUAL": "Manual"}


def _op_year(production_date) -> int | None:
    """productionDate is an ISO datetime ('2021-04-30T00:00:00.000Z'); the year is the prefix."""
    if not production_date or not isinstance(production_date, str):
        return None
    m = re.match(r"(\d{4})", production_date)
    if not m:
        return None
    y = int(m.group(1))
    return y if 1900 <= y <= 2100 else None


def parse_ocasionplus_page(html: str) -> tuple[list[Vehicle], int | None]:
    """Parse an OcasionPlus SRP page -> (vehicles, declared_total). The JSON-LD `ItemList` holds
    20 `Vehicle` items; the `Product`/`AggregateOffer` block declares offerCount (full stock)."""
    declared: int | None = None
    vehicles: list[Vehicle] = []
    for block in _LD_RE.findall(html):
        try:
            d = json.loads(block)
        except (ValueError, TypeError):
            continue
        # full-stock count lives on the page-level Product's AggregateOffer.
        if d.get("@type") == "Product":
            offers = d.get("offers") or {}
            if isinstance(offers, dict) and offers.get("@type") == "AggregateOffer":
                declared = _to_int(offers.get("offerCount")) or declared
        if d.get("@type") != "ItemList":
            continue
        for el in d.get("itemListElement", []):
            if not isinstance(el, dict) or el.get("@type") != "Vehicle":
                continue
            offers = el.get("offers") or {}
            url = offers.get("url") or el.get("url")
            if not url:
                continue
            # the deep-link tail after the last '-' is the native stable listing_ref.
            listing_ref = url.rsplit("-", 1)[-1] if "-" in url else url
            price = offers.get("price")
            try:
                price = float(price) if price is not None else None
            except (TypeError, ValueError):
                price = None
            brand = (el.get("brand") or {})
            make = brand.get("name") if isinstance(brand, dict) else (brand or None)
            mileage = el.get("mileageFromOdometer") or {}
            km = _to_int(mileage.get("value")) if isinstance(mileage, dict) else None
            if km is not None and (km < 0 or km > 5_000_000):
                km = None
            trans = el.get("vehicleTransmission")
            vehicles.append(Vehicle(
                deep_link=url, listing_ref=str(listing_ref),
                title=el.get("model") or el.get("name"),
                make=make, model=el.get("model"),
                year=_op_year(el.get("productionDate")), km=km, price=price,
                prev_price=None, fuel=el.get("fuelType"),
                transmission=_OP_TRANS.get(trans, trans), photo_url=el.get("image"),
                branch_slug=None))
    return vehicles, declared


# ===========================================================================
# Member descriptor — binds a chain's identity, owner model and fetch/parse contract.
# ===========================================================================


@dataclass
class Member:
    key: str                    # source_key
    domain: str
    legal_name: str
    trade_name: str
    family: str
    owner_model: str            # 'branch' (per-branch owner) | 'chain' (chain owns directly)
    data_surface: str           # platform_meta data_surface literal (schema-valid)
    surface_intent: str         # the precise intent kept in surface_detail
    endpoint: str               # the harvested data-layer URL (for meta/recipe)
    host: str                   # the host the governor paces
    page_size: int
    recipe: dict
    # runtime parse helpers wired per member
    branches: dict[str, Branch] = field(default_factory=dict)


FLEXICAR_RECIPE = {
    "version": 1,
    "source": "flexicar.es",
    "group": "chain",
    "scope": "vo_chains wholesale (Flexicar OPEN JSON REST API, per-page paginated)",
    "engine": "curl_cffi+chrome131_impersonate+json_api(GET)",
    "access": ("OPEN first-party REST/JSON API (Chrome TLS fingerprint; no proxy, no browser, no "
               "cookie warm-up). services.flexicar.es/api/v1 is unwalled -> defense_tier t0_open."),
    "data_surface": "internal_api",
    "surface_intent": "json_api",
    "endpoint": "GET https://services.flexicar.es/api/v1/vehicles?page=N&size=24",
    "enumeration": ("page=1..pages, size=24 (HARD cap; size>24 -> HTTP 400). Response "
                    "{total, pages, hasNext, results[]} drives the full drain (total=23874 live)."),
    "platform_entity": ("kind=cadena, province_code=NULL (sentinel 00 in cdp_code), is_tier1=FALSE, "
                        "defense_tier=t0_open, source_group=chain, role=chain, family=flexicar"),
    "ownership": ("PER-BRANCH: each car attributes to its REAL selling branch (one of 186 physical "
                  "compraventa, carDealershipSlug). vehicle.entity_ulid=branch; platform_listing "
                  "edge=chain<->vehicle. Branch geo from __NEXT_DATA__.dealerships (zipCode INE prov "
                  "+ location municipality + lat/lon)."),
    "field_map": {
        "deep_link": "https://www.flexicar.es/coches-segunda-mano/{result.slug}",
        "listing_ref": "result.id (Flexicar native stock id)",
        "make": "result.brand", "model": "result.model", "version": "result.version",
        "year": "result.year", "km": "result.km", "price": "result.price",
        "prev_price": "result.previousPrice (price-drop delta)",
        "fuel": "result.fuel (clean ES label)", "transmission": "result.transmission",
        "photo_url": "result.image (else result.images[0])",
        "branch": "result.carDealershipSlug -> __NEXT_DATA__.pageProps.dealerships[value=slug]",
        "branch_geo": "dealership {zipCode(=INE prov), location(municipality), province, latitude}",
    },
    "caveats": {
        "page_size": "size is hard-capped at 24; size>24 returns HTTP 400 'size must not be greater than 24'.",
        "branch_dir": ("the 186-branch directory is in the SSR __NEXT_DATA__ of the listing page, NOT the "
                       "API; load it once at run start to geo-resolve every carDealershipSlug."),
        "members": ("group 'chain' also includes Clicars (services widget + storage data.json facets — "
                    "stock API needs a deeper XHR probe), OcasionPlus (this connector's member 2), "
                    "Carplus/Aurgi/GpsAutos/Crandon as further members under this same architecture."),
    },
}

OCASIONPLUS_RECIPE = {
    "version": 1,
    "source": "ocasionplus.com",
    "group": "chain",
    "scope": "vo_chains wholesale (OcasionPlus Next.js SSR JSON-LD ItemList, per-page paginated)",
    "engine": "curl_cffi+chrome131_impersonate+ssr_jsonld_itemlist(GET)",
    "access": ("OPEN server-rendered HTML carrying schema.org JSON-LD (Chrome TLS fingerprint; no "
               "proxy, no browser, no cookie warm-up). x-powered-by Next.js, no WAF -> t0_open."),
    "data_surface": "json_ld",
    "surface_intent": "ssr_jsonld_itemlist",
    "endpoint": "GET https://www.ocasionplus.com/coches-segunda-mano?page=N",
    "enumeration": ("?page=1..N; the JSON-LD ItemList holds 20 Vehicle objects/page; the page-level "
                    "Product.offers.offerCount declares the full stock (14052 live)."),
    "platform_entity": ("kind=cadena, province_code=NULL (sentinel 00 in cdp_code), is_tier1=FALSE, "
                        "defense_tier=t0_open, source_group=chain, role=chain, family=ocasionplus"),
    "ownership": ("CHAIN-AS-OWNER: the per-car branch ('centro') is NOT on the SRP data-layer, so the "
                  "chain is the singular selling point and OWNS every car (vehicle.entity_ulid=chain). "
                  "platform_listing edge=chain<->vehicle. owner entity == platform entity. Per-branch "
                  "attribution is a future detail-page pass (the PDP carries centro/provincia)."),
    "field_map": {
        "deep_link": "ItemList.itemListElement[].offers.url (per-car PDP)",
        "listing_ref": "deep-link tail after last '-' (stable native id, e.g. 'togx7qan')",
        "make": "Vehicle.brand.name", "model": "Vehicle.model", "title": "Vehicle.model/name",
        "year": "Vehicle.productionDate (ISO -> YYYY)",
        "km": "Vehicle.mileageFromOdometer.value", "price": "Vehicle.offers.price (EUR)",
        "fuel": "Vehicle.fuelType", "transmission": "Vehicle.vehicleTransmission (AUTO/MANUAL)",
        "photo_url": "Vehicle.image",
    },
    "caveats": {
        "pagination": "?page=N paginates server-side (verified distinct car sets per page); ?pagina=N is ignored.",
        "no_per_branch_geo": ("the SRP ItemList does not attribute a car to a 'centro'; the chain owns the car "
                              "and is anchored national (province NULL). The PDP carries centro/provincia for a "
                              "later per-branch pass — never fabricated here."),
        "members": "see Flexicar recipe; both are members of source_group='chain'.",
    },
}


def build_flexicar(geo_loaded_branches: dict[str, Branch] | None = None) -> Member:
    return Member(
        key=FLEXI_SOURCE_KEY, domain=FLEXI_DOMAIN, legal_name=FLEXI_LEGAL_NAME,
        trade_name=FLEXI_TRADE_NAME, family=FLEXI_FAMILY, owner_model="branch",
        data_surface="internal_api", surface_intent="json_api", endpoint=FLEXI_API,
        host=host_of(FLEXI_API), page_size=FLEXI_PAGE_SIZE, recipe=FLEXICAR_RECIPE,
        branches=geo_loaded_branches or {})


def build_ocasionplus() -> Member:
    return Member(
        key=OP_SOURCE_KEY, domain=OP_DOMAIN, legal_name=OP_LEGAL_NAME,
        trade_name=OP_TRADE_NAME, family=OP_FAMILY, owner_model="chain",
        data_surface="json_ld", surface_intent="ssr_jsonld_itemlist", endpoint=OP_SRP,
        host=host_of(OP_SRP), page_size=OP_PAGE_SIZE, recipe=OCASIONPLUS_RECIPE)


MEMBER_BUILDERS = {"flexicar": build_flexicar, "ocasionplus": build_ocasionplus}


# ===========================================================================
# Fetch: a POOL of fingerprint-coherent curl_cffi sessions, routed THROUGH the governor.
# ===========================================================================


class ChainFetcher:
    """One curl_cffi Session per concurrency slot (a single shared session is not thread-safe under
    the governor's to_thread fetch). The governor's per-host bucket bounds the aggregate rate, so the
    pool widens parallelism WITHOUT out-pacing the host (the bucket is the limiter)."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch_flexicar(self, url: str, *, page: int = 1, size: int = FLEXI_PAGE_SIZE,
                       slot: int = 0) -> str:
        """Synchronous GET of one Flexicar API page on pool session `slot` (runs in a worker thread).
        Returns the raw JSON text. Raises on non-200 so the breaker sees throttling."""
        session = self._sessions[slot]
        full = f"{url}?page={page}&size={size}"
        resp = session.get(full, headers=FLEXI_HEADERS, impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {full}")
        return resp.content.decode("utf-8", "replace")

    def fetch_ocasionplus(self, url: str, *, page: int = 1, slot: int = 0) -> str:
        """Synchronous GET of one OcasionPlus SRP page on pool session `slot`. `page` rides as
        ?page=N. Returns raw HTML (the JSON-LD is embedded). Raises on non-200."""
        session = self._sessions[slot]
        full = f"{url}?page={page}" if page and page > 1 else url
        resp = session.get(full, headers=OP_HEADERS, impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {full}")
        return resp.content.decode("utf-8", "replace")

    async def fetch_async(self, governed_fetch, sync_callable, url: str, **kw) -> str:
        """Lease a pool slot, fetch THROUGH the governor on that slot, release it. `governed_fetch`
        is governor().wrap_fetch_text(sync_callable); the governor paces the host then runs the
        synchronous fetch off the event loop with `slot` forwarded untouched."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, slot=slot, **kw)
        finally:
            self._free.put_nowait(slot)


# ===========================================================================
# DB layer — ensure the chain entity, bulk-upsert per-branch owners (when applicable),
# bulk-insert vehicles + edges + NEW events, all idempotent ON CONFLICT (BULK unnest).
# ===========================================================================


async def ensure_chain_entity(conn: asyncpg.Connection, m: Member) -> str:
    """Idempotently ensure the chain's entity + platform_meta exist. Returns the chain entity ulid.
    kind='cadena', source_group='chain', role='chain', province NULL (national; '00' in cdp_code).
    is_tier1=FALSE, defense_tier=t0_open (both members are unwalled first-party surfaces)."""
    code = chain_cdp_code(m.domain)
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
               kind = EXCLUDED.kind, legal_name = EXCLUDED.legal_name""",
        eulid, code, CHAIN_KIND, m.legal_name, m.trade_name, m.domain,
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
                    "owner_model": m.owner_model, "page_size": m.page_size,
                    "surface_intent": m.surface_intent,
                    "engine": "curl_cffi/chrome131_impersonate"}),
        m.family)
    return eulid


def cdp_code_branch(b: Branch, muni: str | None) -> str:
    """Mint a Flexicar branch's immutable cdp_code via the canonical generator. The branch has no
    bare domain (it lives under flexicar.es) -> identity = name + location + the stable branch slug
    (passed via `address` so two branches sharing a name in one municipality never collapse)."""
    return cdp_code(province_code=b.province_code, domain=None, name=b.name,
                    municipality_code=muni, address=f"branch:{b.slug}")


# The bulk statements — ONE round-trip per table per window (unnest multi-row upsert), byte-for-byte
# the same idempotency the marketplace/group connectors use. A re-run of an already-harvested window
# adds 0 rows and 0 events.

_BULK_UPSERT_OWNERS = """
INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
        province_code, municipality_code, is_tier1, status, kind_source,
        sells_cars, defense_tier, source_group, role, first_discovered_source, last_seen)
SELECT u.entity_ulid, u.cdp_code, 'compraventa'::entity_kind, u.name, u.name,
       u.province_code, u.municipality_code, FALSE, 'active', 'platform_label',
       TRUE, 't0_open'::defense_tier, 'chain'::source_group, 'standalone_pos'::entity_role, $8, now()
  FROM unnest($1::text[], $2::text[], $3::text[], $4::char(2)[], $5::char(5)[],
              $6::text[], $7::text[]) AS u(entity_ulid, cdp_code, name, province_code,
                               municipality_code, source_ref, _slug)
ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()
"""

_BULK_UPSERT_OWNER_SOURCES = """
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


def resolve_cage_rows(vehicles: list[Vehicle], m: Member, chain_ulid: str, geo: GeoResolver,
                      chain_cdp: str, seen_ids: set, harvested_cageable: set,
                      stats: dict) -> list[CageRow]:
    """Resolve every parsed vehicle to its owner — pure CPU, no SQL. Per-branch chain (Flexicar)
    routes a car to its geo-resolved selling branch; chain-as-owner (OcasionPlus) routes it to the
    chain entity itself. Cross-page dedup on listing_ref. The cageable truth is the distinct
    (owner_cdp, deep_link) pair (like-with-like vs the DB edge count)."""
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

        if m.owner_model == "branch":
            branch = m.branches.get(v.branch_slug) if v.branch_slug else None
            if branch is None or not branch.province_code:
                # the branch directory should cover every slug; if a car references an unknown or
                # un-geocoded branch, cage it under the CHAIN entity (national) rather than dropping
                # a real car for want of a clean branch anchor — never fabricate a branch.
                stats["branch_unresolved"] += 1
                harvested_cageable.add((chain_cdp, v.deep_link))
                rows.append(CageRow(owner_cdp=chain_cdp, owner_kind=CHAIN_KIND,
                                    owner_name=m.trade_name, owner_province=None,
                                    owner_muni=None, source_ref=m.domain, vehicle=v))
                continue
            muni = geo.municipality_code(branch.province_code, branch.city)
            owner_cdp = cdp_code_branch(branch, muni)
            stats["branch_attributed"] += 1
            harvested_cageable.add((owner_cdp, v.deep_link))
            rows.append(CageRow(owner_cdp=owner_cdp, owner_kind=BRANCH_KIND,
                                owner_name=branch.name, owner_province=branch.province_code,
                                owner_muni=muni, source_ref=f"branch:{branch.slug}", vehicle=v))
        else:
            # chain-as-owner: the chain entity owns the car directly.
            harvested_cageable.add((chain_cdp, v.deep_link))
            rows.append(CageRow(owner_cdp=chain_cdp, owner_kind=CHAIN_KIND,
                                owner_name=m.trade_name, owner_province=None,
                                owner_muni=None, source_ref=m.domain, vehicle=v))
    return rows


async def ingest_window(conn: asyncpg.Connection, m: Member, chain_ulid: str, chain_cdp: str,
                        geo: GeoResolver, vehicles: list[Vehicle], seen_ids: set,
                        harvested_cageable: set, cdp_to_ulid: dict[str, str], stats: dict) -> None:
    """BULK-ingest a window of parsed cars in ONE transaction with set-based SQL. Per-branch owners
    are bulk-upserted (kind=compraventa) and mapped cdp->ulid; chain-owned cars cage straight under
    the chain ulid. Then vehicles split existing/new (one SELECT), bulk-touch + bulk-insert, edges
    bulk-upsert (RETURNING counts new edges), NEW events fire for genuinely new vehicles only.
    Idempotency/delta/VAM semantics are byte-identical to coches_net_wholesale."""
    cage = resolve_cage_rows(vehicles, m, chain_ulid, geo, chain_cdp, seen_ids,
                             harvested_cageable, stats)
    if not cage:
        return

    async with conn.transaction():
        # ---- OWNERS: dedup per-branch owners by cdp_code; the chain cdp resolves to chain_ulid.
        branch_owners: dict[str, CageRow] = {}
        for r in cage:
            if r.owner_kind == BRANCH_KIND and r.owner_cdp not in cdp_to_ulid:
                branch_owners.setdefault(r.owner_cdp, r)
        if branch_owners:
            cdps = list(branch_owners.keys())
            ulids = [ulid() for _ in cdps]
            names = [branch_owners[c].owner_name for c in cdps]
            provs = [branch_owners[c].owner_province for c in cdps]
            munis = [branch_owners[c].owner_muni for c in cdps]
            refs = [branch_owners[c].source_ref for c in cdps]
            slugs = refs  # placeholder column in the unnest signature
            await conn.execute(_BULK_UPSERT_OWNERS, ulids, cdps, names, provs, munis, refs,
                               slugs, m.key)
            await conn.execute(_BULK_UPSERT_OWNER_SOURCES, cdps, refs, m.key)
            for row in await conn.fetch(
                    "SELECT cdp_code, entity_ulid FROM entity WHERE cdp_code = ANY($1::text[])", cdps):
                cdp_to_ulid[row["cdp_code"]] = row["entity_ulid"]
        cdp_to_ulid[chain_cdp] = chain_ulid

        # ---- attach owner ulid to each car; dedup within the window by (owner_ulid, deep_link).
        cars: dict[tuple[str, str], CageRow] = {}
        for r in cage:
            ou = cdp_to_ulid.get(r.owner_cdp)
            if ou is None:
                continue
            key = (ou, r.vehicle.deep_link)
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

        # ---- EDGES: chain<->vehicle. RETURNING (xmax=0) counts genuinely new edges.
        e_vehicles = [vehicle_ulid_for[k] for k in car_keys]
        e_urls = [cars[k].vehicle.deep_link for k in car_keys]
        e_refs = [cars[k].vehicle.listing_ref for k in car_keys]
        e_prices = [cars[k].vehicle.price for k in car_keys]
        edge_rows = await conn.fetch(_BULK_UPSERT_EDGES, e_vehicles, e_urls, e_refs,
                                     e_prices, chain_ulid)
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


async def _load_flexicar_branches(fetcher: ChainFetcher, governed_srp, geo: GeoResolver) -> dict[str, Branch]:
    """Fetch the Flexicar listing SSR once (through the governor) and parse the 186-branch directory
    from __NEXT_DATA__. Returns slug -> Branch (geo-resolved). Empty dict on any failure (cars then
    cage under the chain entity rather than dropping)."""
    try:
        html = await fetcher.fetch_async(governed_srp, fetcher.fetch_ocasionplus, FLEXI_SRP, page=1)
    except Exception:
        return {}
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
    if not m:
        return {}
    try:
        nd = json.loads(m.group(1))
    except (ValueError, TypeError):
        return {}
    return parse_flexicar_branches(nd, geo)


async def harvest_member(conn: asyncpg.Connection, member_name: str, geo: GeoResolver,
                         max_pages: int, concurrency: int) -> dict:
    """Drain ONE chain member end to end: ensure the chain entity, drain its data-layer concurrently
    through the governor, BULK-cage every window, write the recipe, run the VAM quorum, record the
    S-HEALTH heartbeat. Returns the member's stats dict."""
    builder = MEMBER_BUILDERS[member_name]
    fetcher = ChainFetcher(pool_size=concurrency)
    gov = governor()

    # build the member (Flexicar needs its branch directory loaded first).
    if member_name == "flexicar":
        governed_srp = gov.wrap_fetch_text(fetcher.fetch_ocasionplus)  # plain GET wrapper for the SRP
        branches = await _load_flexicar_branches(fetcher, governed_srp, geo)
        m = build_flexicar(branches)
    else:
        m = build_ocasionplus()

    stats = {
        "member": member_name, "source_key": m.key, "owner_model": m.owner_model,
        "pages_fetched": 0, "items_seen": 0, "cars_caged": 0, "new_cars": 0,
        "edges_created": 0, "new_events": 0, "price_drops_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "no_link_skipped": 0,
        "branch_attributed": 0, "branch_unresolved": 0,
        "branches_known": len(m.branches), "concurrency": concurrency, "max_pages": max_pages,
    }
    harvested_cageable: set[tuple[str, str]] = set()

    if await is_open(conn, m.key):
        print(f"[group_vo_chains:{member_name}] breaker OPEN for {m.key}; skipping drain "
              f"(graceful degradation, site still serves last snapshot).")
        return {**stats, "skipped": True, "reason": "breaker_open"}

    # the governed fetch callable per surface (Flexicar=JSON API, OcasionPlus=SSR HTML).
    if m.owner_model == "branch":
        governed = gov.wrap_fetch_text(fetcher.fetch_flexicar)
        def fetch_one(p):
            return fetcher.fetch_async(governed, fetcher.fetch_flexicar, m.endpoint,
                                       page=p, size=m.page_size)
        def parse_one(text):
            data = json.loads(text)
            results = data.get("results") or []
            declared = _to_int(data.get("total"))
            return [v for v in (parse_flexicar_vehicle(it) for it in results) if v], declared
    else:
        governed = gov.wrap_fetch_text(fetcher.fetch_ocasionplus)
        def fetch_one(p):
            return fetcher.fetch_async(governed, fetcher.fetch_ocasionplus, m.endpoint, page=p)
        def parse_one(text):
            return parse_ocasionplus_page(text)

    fetch_error: str | None = None
    last_http: int | None = None
    chain_ulid = await ensure_chain_entity(conn, m)
    chain_cdp = chain_cdp_code(m.domain)
    cdp_to_ulid: dict[str, str] = {chain_cdp: chain_ulid}
    edges_before = await conn.fetchval(
        "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", chain_ulid)

    print(f"[group_vo_chains:{member_name}] chain entity ready: {chain_cdp} (ulid={chain_ulid}) "
          f"kind=cadena group=chain role=chain owner_model={m.owner_model} "
          f"branches_known={len(m.branches)}")
    print(f"[group_vo_chains:{member_name}] governor paces host {m.host}; CONCURRENT drain "
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
        for page, data in zip(window, results):
            if isinstance(data, Exception):
                fetch_error = str(data)
                last_http = fetcher.last_status
                print(f"[group_vo_chains:{member_name}] page {page} fetch failed ({data}); "
                      f"stopping drain honestly.")
                stop = True
                break
            try:
                vehicles, declared = parse_one(data)
            except Exception as ex:  # a parse failure is recipe drift the breaker must catch.
                fetch_error = f"parse error on page {page}: {ex}"
                last_http = fetcher.last_status
                print(f"[group_vo_chains:{member_name}] {fetch_error}; stopping.")
                stop = True
                break
            if stats["declared_full"] is None and declared is not None:
                stats["declared_full"] = declared
            if not vehicles:
                print(f"[group_vo_chains:{member_name}] page {page}: no items; stopping (boundary).")
                stop = True
                break
            window_vehicles.extend(vehicles)
            pages_in_window += 1

        if window_vehicles:
            await ingest_window(conn, m, chain_ulid, chain_cdp, geo, window_vehicles, seen_ids,
                                harvested_cageable, cdp_to_ulid, stats)
            stats["pages_fetched"] += pages_in_window
            print(f"[group_vo_chains:{member_name}] window {window[0]}-{window[0]+pages_in_window-1}: "
                  f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                  f"edges={stats['edges_created']} branch_attr={stats['branch_attributed']} "
                  f"drops={stats['price_drops_captured']}")

    recipe_path = write_recipe(chain_cdp, m.recipe)
    stats["recipe_path"] = str(recipe_path)
    print(f"[group_vo_chains:{member_name}] recipe written: {recipe_path}")

    # VAM count quorum — THREE orthogonal like-with-like paths, all "distinct cageable cars":
    #   db_edges           = platform_listing rows for this chain   (DB write truth)
    #   db_join_vehicles   = distinct vehicles via the edge join     (DB read truth)
    #   harvested_cageable = distinct (owner_cdp, deep_link) pulled  (harvest truth)
    db_edges = await conn.fetchval(
        "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", chain_ulid)
    db_join_vehicles = await conn.fetchval(
        """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
           JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
           JOIN entity e ON e.entity_ulid = v.entity_ulid
           WHERE pl.platform_entity_ulid=$1""", chain_ulid)
    harvested_cageable_n = len(harvested_cageable)
    verdict = await record_count_verdict(
        conn, subject_type="platform_slice", subject_key=chain_cdp,
        claim="distinct cageable cars (harvest) == platform_listing edges == join-reachable vehicles",
        paths={"db_edges": db_edges, "db_join_vehicles": db_join_vehicles,
               "harvested_cageable": harvested_cageable_n}, tolerance=0.0)
    stats["verdict"] = verdict
    stats["db_edges"] = db_edges
    stats["db_join_vehicles"] = db_join_vehicles
    stats["harvested_cageable"] = harvested_cageable_n
    stats["harvested_distinct_ids"] = len(seen_ids)
    stats["edges_new_this_run"] = db_edges - (edges_before or 0)
    stats["platform_code"] = chain_cdp
    stats["platform_ulid"] = chain_ulid
    # distinct selling owners (branches + the chain) reachable via the edge join.
    stats["owners_distinct"] = await conn.fetchval(
        """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
           JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
           WHERE pl.platform_entity_ulid=$1""", chain_ulid)

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
    """Drain each requested chain member sequentially against ONE shared connection (the per-host
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
            print(f"\n[group_vo_chains:{name}] SKIPPED: {stats.get('reason')}")
            continue
        print("\n" + "=" * 66)
        print(f"VO_CHAINS WHOLESALE HARVEST — {name.upper()} — REPORT")
        print("=" * 66)
        print(f"  chain cdp_code        : {stats.get('platform_code')}")
        print(f"  group / kind / role   : chain / cadena / chain (tier t0_open, family {name})")
        print(f"  owner model           : {stats.get('owner_model')} "
              f"({'per-branch compraventa' if stats.get('owner_model')=='branch' else 'chain owns cars'})")
        print(f"  branches known        : {stats.get('branches_known')}")
        print(f"  declared full (source): {stats.get('declared_full')}")
        print(f"  concurrency / target  : {stats.get('concurrency')} pages in flight / {stats.get('max_pages')} pages")
        print(f"  pages fetched         : {stats['pages_fetched']}")
        print(f"  items seen            : {stats['items_seen']}")
        print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page)")
        print(f"  no-link skipped       : {stats['no_link_skipped']}")
        print(f"  branch attributed     : {stats.get('branch_attributed')} "
              f"(unresolved -> chain bucket: {stats.get('branch_unresolved')})")
        print(f"  owners attributed     : {stats.get('owners_distinct')} distinct selling points")
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="vo_chains wholesale harvester (Flexicar JSON API + OcasionPlus SSR JSON-LD)")
    parser.add_argument("--members", nargs="+", default=["flexicar", "ocasionplus"],
                        choices=sorted(MEMBER_BUILDERS.keys()),
                        help="which chain members to harvest; default both.")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"pages to harvest per member; default {DEFAULT_MAX_PAGES}.")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=f"pages fetched in parallel per window; default {DEFAULT_CONCURRENCY}.")
    args = parser.parse_args()
    all_stats = asyncio.run(harvest(args.members, args.pages, args.concurrency))
    _print_report(all_stats)


if __name__ == "__main__":
    main()
