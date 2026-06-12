"""coches.com WHOLESALE harvester — the THIRD giant marketplace, end to end.

coches.com (Carossa / Grupo coches.com — an INDEPENDENT family, not Adevinta) is a
Tier-1 marketplace fronted by Imperva/Incapsula behind CloudFront (`x-cdn: Imperva`,
is_tier1=TRUE). Unlike coches.net's open POST JSON gateway, coches.com exposes NO open
search API — its harvestable surface is the SSR `__NEXT_DATA__` blob on every PDP. The
recipe (docs/architecture/tier1_recipes/coches_com.md) records the free path, proven
live 2026-06-12 with curl_cffi chrome131, ZERO proxy:

  1. Enumerate: sitemap.xml -> sitemap/vo.xml -> sitemap/coches/Todo-VO-{0..3}.xml,
     yielding 92,259 PDP `?id=` URLs (CORRECTED real count; 4 shards: 25k/25k/25k/17,259).
  2. Fetch each PDP, decode `r.content` (NOT r.text — curl_cffi mis-guesses the charset
     and mojibakes accents), regex `__NEXT_DATA__`, read props.pageProps.data.classified
     -> the vehicle, and classified.dealer -> the selling dealer.

This module mirrors pipeline.platform.coches_net_wholesale EXACTLY (same dual-membership
model, same caging, same governor/health/VAM wiring). It proves a THIRD platform flows
through ONE architecture, not a fork of it:

  coches.com (the marketplace)  -> entity, kind='plataforma'  (+ platform_meta)
  each SELLING DEALER           -> entity, kind='compraventa' (geo-resolved)
  each CAR                      -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the platform       -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the dealer); platform membership is plural (this edge). The same
physical car can carry an AS24 edge, a coches.net edge AND a coches.com edge without ever
changing its owning dealer.

PROOF SLICE, NOT THE FULL HARVEST. coches.com exposes 92,259 PDP URLs. Draining all of
them is the same command with a larger --limit; here we cap at --limit (~3,000-5,000 PDPs)
and log the cap honestly. The declared full count (sitemap URL total) is recorded for the
VAM verdict's slice arithmetic.

Engine: a GET against each PDP on www.coches.com routed THROUGH the per-host governor (the
same single choke point AS24/coches.net use). The synchronous curl_cffi GET runs in a
worker thread so the event loop is never blocked, and no host is fetched faster than its
bucket. Sitemap enumeration runs through the same governed fetch.

Run: python -m pipeline.platform.coches_com_wholesale --limit 4000
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
# coches.com platform identity (00-TIER1-REGISTRY; recipe coches_com.md).
# ---------------------------------------------------------------------------
COCHES_DOMAIN = "coches.com"
COCHES_WEBSITE = "coches.com"
COCHES_TRADE_NAME = "coches.com"
COCHES_SOURCE_KEY = "coches_com_wholesale"
COCHES_WAF = "imperva"  # Imperva/Incapsula behind CloudFront -> is_tier1=TRUE.

# Multi-axis classification (0016): t1_soft (WAF serving curl_cffi today), a
# car-specialist marketplace, acting as a platform in the market graph.
DEFENSE_TIER = "t1_soft"
SOURCE_GROUP = "marketplace_motor"
ENTITY_ROLE = "platform"
PLATFORM_FAMILY = "independent"  # NOT Adevinta/Schibsted — its own recipe family.

# Enumeration: the sitemap chain (recipe vector #3; verified live 2026-06-12).
SITEMAP_INDEX = "https://www.coches.com/sitemap.xml"
SITEMAP_VO = "https://www.coches.com/sitemap/vo.xml"
_PDP_HOST = "https://www.coches.com"
_IMAGE_BASE = "https://images.coches.com/_ccom_/"  # imageList[0].name -> full URL.

# Headers sufficient for the free path (recipe; chrome131 supplies UA + TLS/JA3 + h2).
_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Referer": "https://www.coches.com/coches-segunda-mano/",
}
_IMPERSONATE = "chrome131"
_TIMEOUT = 40

# Province sentinel '00' = national (same convention as AS24/coches.net). geo_province
# has NO '00', so the platform ENTITY stores province_code = NULL; '00' lives only inside
# the cdp_code string (free text, no FK). We never pollute geo_province with it.
PLATFORM_PROVINCE_SENTINEL = "00"

# PROOF SLICE cap. ~4,000 PDPs (NOT the ~92,259 full set — full drain = full governed run
# = the same command with a larger --limit). One GET per PDP (no pagination object).
DEFAULT_LIMIT = 4000

# The __NEXT_DATA__ SSR blob carries the full structured classified (vehicle + dealer).
_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)
_LOC_RE = re.compile(r"<loc>(.*?)</loc>")


def coches_platform_cdp_code() -> str:
    """The coches.com platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:coches.com'), province segment '00' (national). Mirrors
    coches_net_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{COCHES_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL response — field names inspected live, not assumed).
# props.pageProps.data.classified verified 2026-06-12 against 5 live PDPs.
# ---------------------------------------------------------------------------


@dataclass
class DealerRef:
    """The selling dealer parsed from classified.dealer + classified.currentProvince.

    coches.com's dealer carries name + crmId (stable coches.com-canonical dealer key) +
    type + uuid + taxIdNumber (CIF/NIF when present, often ""). The geo anchor comes from
    the classified's currentProvince.id (INE province code); the dealer object has no
    address/municipality on this surface, so province is the geo grain we have."""
    crm_id: str
    name: str | None
    cif: str | None
    dealer_type: str | None
    uuid: str | None
    province_code: str | None


@dataclass
class Vehicle:
    """A car parsed from a single coches.com PDP's classified blob."""
    deep_link: str
    listing_ref: str           # classified.visibleId (== ?id= in URL); also externalId
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    price_drop: dict | None     # synthesized from price vs priceOffer (the "precio contado")


def _to_int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _prov2(province_id) -> str | None:
    """coches.com classified.currentProvince.id IS the INE province code (28=Madrid,
    41=Sevilla — verified live). Zero-pad to 2 digits, reject out-of-range."""
    n = _to_int(province_id)
    if n is None or not (1 <= n <= 52):
        return None
    return f"{n:02d}"


def _name(obj) -> str | None:
    """classified.make/model/version/fuel/transmission are {id, name} objects."""
    if isinstance(obj, dict):
        return obj.get("name")
    return None


def parse_classified_dealer(cls: dict) -> DealerRef | None:
    """Parse the SELLING DEALER from classified.dealer + classified.currentProvince.

    Only dealers with a crmId become entities (the stable per-dealer key used for
    cross-source dedup and as the source_ref). Geo comes from the classified's
    currentProvince (the dealer object has no address on this surface)."""
    dealer = cls.get("dealer") or {}
    crm_id = dealer.get("crmId")
    if not crm_id:
        return None
    prov = _prov2((cls.get("currentProvince") or {}).get("id"))
    tax = dealer.get("taxIdNumber") or None  # often "" -> normalize to None
    return DealerRef(
        crm_id=str(crm_id),
        name=dealer.get("name"),
        cif=(tax.strip() or None) if isinstance(tax, str) else None,
        dealer_type=dealer.get("type"),
        uuid=dealer.get("uuid"),
        province_code=prov,
    )


def _first_image(cls: dict) -> str | None:
    images = cls.get("imageList")
    if not isinstance(images, list):
        return None
    for img in images:
        if isinstance(img, dict) and img.get("name"):
            return _IMAGE_BASE + img["name"]
    return None


def parse_classified_vehicle(cls: dict, url: str) -> Vehicle:
    """Parse the car from a coches.com classified blob (REAL field map, verified live)."""
    price_obj = cls.get("price") or {}
    amount = price_obj.get("amount")
    try:
        price = float(amount) if amount is not None else None
    except (TypeError, ValueError):
        price = None

    # priceOffer (the "precio contado"/financed offer) is the lower headline. When it is
    # below the list price, record it as a price-drop signal (the coches.com analogue of
    # coches.net's priceDropData — gold for delta).
    offer_obj = cls.get("priceOffer") or {}
    offer_amount = offer_obj.get("amount")
    price_drop = None
    try:
        offer = float(offer_amount) if offer_amount is not None else None
    except (TypeError, ValueError):
        offer = None
    if price is not None and offer is not None and offer < price:
        price_drop = {
            "list_price": price,
            "offer_price": offer,
            "amountFromOriginal": round(price - offer, 2),
            "percentageFromOriginal": round((price - offer) / price * 100, 2) if price else None,
            "source": "priceOffer",
        }

    reg = cls.get("registration") or {}
    year = _to_int(reg.get("year"))
    if year is not None and not (1900 <= year <= 2100):
        year = None

    km = _to_int((cls.get("mileage") or {}).get("amount"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    make = _name(cls.get("make"))
    model = _name(cls.get("model"))
    version = _name(cls.get("version"))
    title = " ".join(p for p in (make, model, version) if p) or None

    return Vehicle(
        deep_link=url,
        listing_ref=str(cls.get("visibleId") or ""),
        title=title,
        make=make,
        model=model,
        year=year,
        km=km,
        price=price,
        fuel=_name(cls.get("fuel")),            # UTF-8: "Híbrido Gasolina", "Diésel"
        transmission=_name(cls.get("transmission")),  # "Automática" / "Manual"
        photo_url=_first_image(cls),
        price_drop=price_drop,
    )


def extract_classified(html: str) -> dict | None:
    """Pull props.pageProps.data.classified from a PDP's __NEXT_DATA__ blob.
    Returns None if the surface is missing (Imperva interstitial / structure drift)."""
    m = _NEXT_DATA_RE.search(html)
    if not m:
        return None
    try:
        data = json.loads(m.group(1))
    except (ValueError, TypeError):
        return None
    cls = (((data.get("props") or {}).get("pageProps") or {})
           .get("data") or {}).get("classified")
    return cls if isinstance(cls, dict) and cls else None


# ---------------------------------------------------------------------------
# Fetch: a GET routed THROUGH the governor (same per-host choke point as AS24).
# ---------------------------------------------------------------------------


class CochesComFetcher:
    """A fingerprint-coherent curl_cffi GET session for coches.com sitemaps + PDPs.

    One session == one Chrome fingerprint == one cookie jar for the whole drain, so the
    sitemap walk + the PDP harvest look like one continuous browser (and any Imperva
    `incap_ses_*` cookie minted on the first hit is replayed on the rest). The governor
    wraps `fetch` to pace requests by the host bucket; this class only performs the GET.
    """

    def __init__(self) -> None:
        self._session = cffi_requests.Session(impersonate=_IMPERSONATE)
        self.last_status: int | None = None

    def fetch(self, url: str) -> str:
        """GET `url` and return the UTF-8 decoded body (sitemap XML or PDP HTML).

        Decodes `resp.content` explicitly as UTF-8 (recipe: load-bearing — r.text
        mojibakes accents). Raises on a non-200 so the breaker sees a challenge/ban
        (never masks an Imperva interstitial as success)."""
        resp = self._session.get(url, headers=_HEADERS, impersonate=_IMPERSONATE,
                                  timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url}")
        return resp.content.decode("utf-8", "replace")


# ---------------------------------------------------------------------------
# DB layer (mirrors coches_net_wholesale: ensure platform, upsert dealer/vehicle,
# link edge, emit delta, all idempotent ON CONFLICT).
# ---------------------------------------------------------------------------

COCHES_PLATFORM_RECIPE = {
    "version": 1,
    "source": "coches.com",
    "scope": "platform-wholesale (sitemap PDP enumeration + __NEXT_DATA__ SSR)",
    "engine": "curl_cffi+chrome131_impersonate+sitemap_walk+next_data(GET)",
    "access": ("FREE path, ZERO proxy (Chrome TLS fingerprint; no browser, no cookie "
               "warm-up). Imperva/Incapsula behind CloudFront -> is_tier1=true; serving "
               "sitemaps + PDPs + __NEXT_DATA__ to chrome131 today (decaying-open window)."),
    "data_surface": "next_data",
    "surface_intent": "ssr_next_data",
    "enumeration": ("sitemap.xml -> sitemap/vo.xml -> sitemap/coches/Todo-VO-{0..3}.xml; "
                    "92,259 PDP ?id= URLs (4 shards: 25k/25k/25k/17,259), verified live"),
    "pdp": "GET https://www.coches.com/coches-segunda-mano/{slug}.htm?id={visibleId}",
    "encoding": "r.content.decode('utf-8') — load-bearing; r.text mojibakes accents",
    "platform_entity": ("kind=plataforma, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=TRUE, defense_tier=t1_soft, source_group=marketplace_motor, "
                        "role=platform, family=independent"),
    "dual_membership": "vehicle.entity_ulid=SELLING DEALER (compraventa); platform_listing edge=platform<->vehicle",
    "field_map": {
        "path": "props.pageProps.data.classified",
        "deep_link": "the PDP <loc> URL (carries ?id=visibleId)",
        "listing_ref": "classified.visibleId (== ?id= ; also classified.externalId)",
        "make": "classified.make.name",
        "model": "classified.model.name",
        "version": "classified.version.name",
        "year": "classified.registration.year (string -> int)",
        "km": "classified.mileage.amount",
        "price": "classified.price.amount (classified.price.currency)",
        "price_offer": "classified.priceOffer.amount (precio contado; drop signal when < price)",
        "fuel": "classified.fuel.name (UTF-8: Híbrido Gasolina/Diésel/...)",
        "transmission": "classified.transmission.name (Automática/Manual)",
        "photo_url": "https://images.coches.com/_ccom_/ + classified.imageList[0].name",
        "dealer": "classified.dealer {name, crmId, type, uuid, taxIdNumber(=CIF when present)}",
        "location": "classified.currentProvince {id(=INE province code), name}",
    },
    "escalation_reserve": ("if Imperva flips to active JS challenge (interstitial / "
                           "_Incapsula_Resource / 403): camoufox/nodriver homepage warm-up "
                           "to mint incap_ses_*, export cookies to curl_cffi (vectors #5/#6)."),
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the coches.com platform entity + platform_meta exist.
    Returns the platform entity_ulid. Mirrors coches.net but sets the multi-axis
    classification (0016): defense_tier=t1_soft, source_group=marketplace_motor,
    role=platform, family=independent. data_surface='next_data' (the SSR surface)."""
    code = coches_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               defense_tier, source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,'plataforma',$3,$3,NULL,$4,$5,TRUE,'active','platform_label',
               $6::defense_tier,$7::source_group,$8::entity_role,$9, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, website_waf = EXCLUDED.website_waf,
               defense_tier = EXCLUDED.defense_tier, source_group = EXCLUDED.source_group,
               role = EXCLUDED.role""",
        eulid, code, COCHES_TRADE_NAME, COCHES_WEBSITE, COCHES_WAF,
        DEFENSE_TIER, SOURCE_GROUP, ENTITY_ROLE, COCHES_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, COCHES_SOURCE_KEY, COCHES_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'next_data',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"sitemap_index": SITEMAP_INDEX, "host": host_of(_PDP_HOST),
                           "method": "GET", "surface_intent": "ssr_next_data",
                           "classified_path": "props.pageProps.data.classified",
                           "pdp_urls_declared": 92259,
                           "engine": "curl_cffi/chrome131_impersonate"}),
        PLATFORM_FAMILY)
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    Prefer the CIF (a hard cross-source identity) when present; otherwise identity =
    name + location + the stable crmId (passed via `address` so two distinct contracts
    that happen to share a name in one province never collapse to one entity). coches.com
    dealers have no bare domain on this surface, so domain is never the key here."""
    if d.cif:
        return cdp_code(province_code=d.province_code, cif=d.cif)
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni, address=f"crm:{d.crm_id}")


async def upsert_dealer(conn: asyncpg.Connection, geo: GeoResolver, d: DealerRef) -> str | None:
    """Upsert the selling dealer entity (kind='compraventa', geo-resolved).
    Returns the dealer entity_ulid, or None if it cannot be geo-anchored. Sets
    source_group=marketplace_motor + role=standalone_pos (it is a POS discovered via the
    marketplace), sells_cars=TRUE."""
    if not d.province_code:
        return None
    if not (d.province_code.isdigit() and "01" <= d.province_code <= "52"):
        return None
    # The dealer object has no municipality on this surface; province is the geo grain.
    muni = None
    code = cdp_code_dealer(d, muni)
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name, cif,
               province_code, municipality_code, is_tier1, status, kind_source,
               source_group, role, sells_cars, first_discovered_source, last_seen)
           VALUES ($1,$2,'compraventa',$3,$3,$4,$5,$6,FALSE,'active','platform_label',
               $7::source_group,'standalone_pos'::entity_role,TRUE,$8, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               cif = COALESCE(entity.cif, EXCLUDED.cif)""",
        eulid, code, d.name, d.cif, d.province_code, muni, SOURCE_GROUP, COCHES_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, COCHES_SOURCE_KEY, d.crm_id)
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
    """Emit the delta NEW event (same shape as pipeline.ingest). The coches.com
    price-offer drop (priceOffer < price) is captured here — it is gold for delta."""
    payload = {"price": v.price, "title": v.title, "platform": COCHES_TRADE_NAME}
    if v.price_drop:
        payload["price_drop"] = v.price_drop
    await conn.execute(
        "INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type, "
        "old_value, new_value) VALUES ($1,$2,$3,'NEW',NULL,$4::jsonb)",
        ulid(), vulid, dealer_ulid, json.dumps(payload))


# ---------------------------------------------------------------------------
# Enumeration: walk the sitemap chain into a deduped PDP URL list.
# ---------------------------------------------------------------------------


async def enumerate_pdp_urls(governed_fetch, limit: int) -> tuple[list[str], int]:
    """Walk sitemap.xml -> vo.xml -> Todo-VO-{0..3}.xml and return up to `limit` distinct
    PDP URLs plus the DECLARED full count (total PDP <loc> across all shards). Each fetch
    goes through the governor (same host bucket as the PDP harvest)."""
    index_xml = await governed_fetch(SITEMAP_INDEX)
    vo_url = next((u for u in _LOC_RE.findall(index_xml) if u.rstrip("/").endswith("/vo.xml")),
                  SITEMAP_VO)
    vo_xml = await governed_fetch(vo_url)
    shard_urls = [u for u in _LOC_RE.findall(vo_xml) if "Todo-VO-" in u]

    pdp_urls: list[str] = []
    seen: set[str] = set()
    declared_full = 0
    for shard in shard_urls:
        shard_xml = await governed_fetch(shard)
        locs = _LOC_RE.findall(shard_xml)
        declared_full += len(locs)
        for loc in locs:
            if loc in seen:
                continue
            seen.add(loc)
            if len(pdp_urls) < limit:
                pdp_urls.append(loc)
        # Keep walking ALL shards to learn the true declared_full, even once the slice
        # is full — the VAM verdict needs the honest total, and the shards are cheap (4).
    return pdp_urls, declared_full


def _visible_id_of(url: str) -> str | None:
    m = re.search(r"[?&]id=([^&]+)", url)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


async def harvest(limit: int = DEFAULT_LIMIT) -> dict:
    conn = await asyncpg.connect(DSN)
    fetcher = CochesComFetcher()  # one fingerprint + cookie jar for the whole drain
    stats = {
        "pdp_urls_enumerated": 0, "pdps_fetched": 0, "pdp_errors": 0,
        "no_classified": 0, "dealer_items": 0, "private_skipped": 0, "geo_skipped": 0,
        "new_dealers": 0, "cars_caged": 0, "new_cars": 0, "edges_created": 0,
        "new_events": 0, "price_drops_captured": 0, "declared_full": None,
        "dup_ids_collapsed": 0, "dealers_distinct": 0,
    }
    # Harvest-side truth for the VAM: distinct CAGEABLE cars = distinct (crm_id, deep_link)
    # pairs that survived dealer-parse + geo-resolution. Like-with-like vs db_edges.
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if coches.com's breaker is OPEN (a recent ban/throttle still cooling),
    # skip the drain gracefully — the system keeps serving the last snapshot.
    if await is_open(conn, COCHES_SOURCE_KEY):
        print(f"[coches_com_wholesale] breaker OPEN for {COCHES_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, last snapshot still served).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": COCHES_SOURCE_KEY}

    # GOVERNOR: the single per-host choke point. wrap_fetch_text takes our GET callable;
    # every sitemap + every PDP passes through www.coches.com's token bucket, off the event
    # loop. No matter how many drains run, the host is never hammered.
    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = coches_platform_cdp_code()
        print(f"[coches_com_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid})")
        print(f"[coches_com_wholesale] governor paces host {host_of(_PDP_HOST)} (per-host token bucket).")

        # Phase 1 — enumerate the sitemap chain into a bounded PDP work list.
        try:
            pdp_urls, declared_full = await enumerate_pdp_urls(governed_fetch, limit)
        except Exception as e:  # noqa: BLE001 — sitemap unreachable/challenged: fail honestly
            fetch_error = str(e)
            last_http = fetcher.last_status
            print(f"[coches_com_wholesale] sitemap enumeration failed ({e}); aborting drain.")
            outcome = await record_run(conn, COCHES_SOURCE_KEY, ok=False, rows=0,
                                       error=fetch_error, http_status=last_http)
            repair = await auto_repair(conn, COCHES_SOURCE_KEY, fetch_error,
                                       phase="enumerate", http_status=last_http)
            return {"skipped": True, "reason": "enumeration_failed", "error": fetch_error,
                    "health_status": outcome.status, "breaker_state": outcome.breaker_state,
                    "repair_action": repair, "platform_code": platform_code}

        stats["declared_full"] = declared_full
        stats["pdp_urls_enumerated"] = len(pdp_urls)
        print(f"[coches_com_wholesale] enumerated {declared_full} PDP URLs (full set); "
              f"PROOF SLICE cap = {limit} PDPs ({len(pdp_urls)} queued).")

        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        seen_ids: set[str] = set()

        # Phase 2 — fetch each PDP, parse classified, cage the car + dealer + edge.
        for n, url in enumerate(pdp_urls, 1):
            try:
                html = await governed_fetch(url)
            except Exception as e:  # noqa: BLE001 — a single PDP can 403/timeout transiently
                stats["pdp_errors"] += 1
                last_http = fetcher.last_status
                # The recipe's wall signal: a run of PDP failures = Imperva escalation.
                # Stop the drain honestly once failures dominate (>20 and >50% of fetched).
                if stats["pdp_errors"] > 20 and stats["pdp_errors"] > stats["pdps_fetched"]:
                    fetch_error = f"PDP fetch wall: {e}"
                    print(f"[coches_com_wholesale] PDP failures dominate "
                          f"({stats['pdp_errors']} errors); stopping drain (Imperva wall?).")
                    break
                continue

            stats["pdps_fetched"] += 1
            cls = extract_classified(html)
            if cls is None:
                stats["no_classified"] += 1
                continue

            visible_id = str(cls.get("visibleId") or "") or _visible_id_of(url) or ""
            if visible_id and visible_id in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue
            if visible_id:
                seen_ids.add(visible_id)

            d = parse_classified_dealer(cls)
            if d is None:
                stats["private_skipped"] += 1
                continue
            stats["dealer_items"] += 1

            async with conn.transaction():
                dealer_ulid = await upsert_dealer(conn, geo, d)
                if dealer_ulid is None:
                    stats["geo_skipped"] += 1
                    continue
                v = parse_classified_vehicle(cls, url)
                if not v.deep_link:
                    continue
                harvested_cageable.add((d.crm_id, v.deep_link))
                vulid, veh_new = await upsert_vehicle(conn, dealer_ulid, v)
                stats["cars_caged"] += 1
                if v.price_drop:
                    stats["price_drops_captured"] += 1
                if veh_new:
                    stats["new_cars"] += 1
                    await emit_new_event(conn, vulid, dealer_ulid, v)
                    stats["new_events"] += 1
                edge_new = await link_platform(conn, platform_ulid, vulid, v)
                if edge_new:
                    stats["edges_created"] += 1

            if n % 250 == 0:
                print(f"[coches_com_wholesale] {n}/{len(pdp_urls)} PDPs "
                      f"caged_total={stats['cars_caged']} edges={stats['edges_created']} "
                      f"errors={stats['pdp_errors']}")

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, COCHES_PLATFORM_RECIPE)
        print(f"[coches_com_wholesale] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths that all
        # measure "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for coches.com (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join     (DB read truth)
        #   harvested_cageable = distinct (crm, deep_link) pulled        (harvest truth)
        # The declared full count (92,259) is reported for honesty but is NOT a quorum path
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

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks coches.com,
        # trips the breaker on a ban, and auto-repairs. OK when >=1 PDP cageable, no fetch
        # wall stopped the drain, and the VAM did not refute.
        run_ok = (fetch_error is None and stats["cars_caged"] > 0 and verdict != "REFUTED")
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, COCHES_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, COCHES_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[coches_com_wholesale] SKIPPED: {stats.get('reason')} "
              f"{stats.get('error') or ''}")
        return
    print("\n" + "=" * 64)
    print("COCHES.COM WHOLESALE HARVEST — PROOF SLICE REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  declared full (source): {stats.get('declared_full')}  (NOT harvested — proof slice)")
    print(f"  PDP urls enumerated   : {stats['pdp_urls_enumerated']} (queued this slice)")
    print(f"  PDPs fetched          : {stats['pdps_fetched']}")
    print(f"  PDP errors            : {stats['pdp_errors']}")
    print(f"  no __NEXT_DATA__      : {stats['no_classified']}")
    print(f"  dealer items          : {stats['dealer_items']}")
    print(f"  private/no-crm skipped: {stats['private_skipped']}")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')}")
    print(f"  geo skipped (bad prov): {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for coches.com = {stats.get('db_edges')})")
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
    parser = argparse.ArgumentParser(description="coches.com wholesale proof-slice harvester")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                        help=f"max PDPs to harvest this slice; default {DEFAULT_LIMIT} (proof slice)")
    parser.add_argument("--pages", type=int, default=None,
                        help="alias: pages*1000 PDPs (kept for CLI parity with the other connectors)")
    args = parser.parse_args()
    limit = args.limit
    if args.pages is not None:
        limit = args.pages * 1000
    stats = asyncio.run(harvest(limit))
    _print_report(stats)


if __name__ == "__main__":
    main()
