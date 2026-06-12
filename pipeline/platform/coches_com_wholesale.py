"""coches.com WHOLESALE harvester — the THIRD giant marketplace, end to end.

coches.com (Carossa / Grupo coches.com — an INDEPENDENT family, not Adevinta) is a
Tier-1 marketplace fronted by Imperva/Incapsula behind CloudFront (`x-cdn: Imperva`,
is_tier1=TRUE). Unlike coches.net's open POST JSON gateway, coches.com exposes NO open
search API — but its harvestable surface is the SSR `__NEXT_DATA__` blob, and the recipe
(docs/architecture/tier1_recipes/coches_com_datalayer.md) found a FASTER surface than the
per-PDP path the connector originally used: the SRP listing page carries the SAME complete
`classified` shape, but **20 full cars per request** instead of 1.

  THE FAST SURFACE (verified live 2026-06-12, curl_cffi chrome131, ZERO proxy):
    1. Page-1 unfiltered SRP /coches-segunda-mano/coches-ocasion.htm -> __NEXT_DATA__
       -> props.pageProps.seoData[key="all-makes"] = 93 makes with EXACT counts
       (Σ counts == classifieds.total == ~92,312). A clean MECE partition (every car has
       exactly one make), and NO make is >= 10,000 (max PEUGEOT 8,345).
    2. Per make M: GET /coches-segunda-mano/{slug(M)}.htm?page=N -> __NEXT_DATA__
       -> props.pageProps.classifieds.classifiedList[<=20] (+ .total).
       The data layer caps deep pagination at the 10,000th result (page 501 -> 403,
       Elasticsearch max_result_window) — so the UNFILTERED SRP reaches only 10.8%. The
       per-make partition keeps every result set < 10k, unlocking 100% at 20 cars/req.

Why upgrade: the original per-PDP path was ~92,259 sequential GETs (1 car each). This is
~4,620 GETs (20 cars each) across 93 INDEPENDENT make streams — embarrassingly parallel.
This module now mirrors pipeline.platform.coches_net_wholesale EXACTLY: a concurrent
sliding-window fetch (pool of curl_cffi sessions, one per slot) funneled through the ONE
per-host governor, and a BULK unnest ingest (one round-trip per table per window). It
proves a THIRD platform flows through ONE architecture, not a fork of it:

  coches.com (the marketplace)  -> entity, kind='plataforma'  (+ platform_meta)
  each SELLING DEALER           -> entity, kind='compraventa' (geo-resolved)
  each CAR                      -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the platform       -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the dealer); platform membership is plural (this edge). The same
physical car can carry an AS24 edge, a coches.net edge AND a coches.com edge without ever
changing its owning dealer.

COVERAGE. `--limit N` caps the cars caged this run (the bounded proof). `--all` drains the
WHOLE platform: every page of every make until each make's result set is exhausted. The
full drain is the SAME command with `--all` (or a large `--limit`); the make-partition
mechanism reaches 100% because Σ(make counts) == classifieds.total with no slice >= 10k.

Engine: a GET against each SRP page on www.coches.com routed THROUGH the per-host governor
(the same single choke point AS24/coches.net use). Each synchronous curl_cffi GET runs in a
worker thread on its own leased pool session so the event loop is never blocked and no two
coroutines share a session; the per-host bucket bounds the aggregate rate.

Run (bounded proof):  python -m pipeline.platform.coches_com_wholesale --limit 16000
Run (full drain):     python -m pipeline.platform.coches_com_wholesale --all
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import re
import sys
import unicodedata
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
# coches.com platform identity (00-TIER1-REGISTRY; recipe coches_com_datalayer.md).
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

# The fast surface (recipe TL;DR; verified live 2026-06-12). SRP = Search Results Page.
_SRP_HOST = "https://www.coches.com"
_SRP_ROOT = "https://www.coches.com/coches-segunda-mano"  # /{make-slug}.htm?page=N
_SRP_ALL = f"{_SRP_ROOT}/coches-ocasion.htm"  # page-1 unfiltered: seoData[all-makes] + total
_IMAGE_BASE = "https://images.coches.com/_ccom_/"  # imageList[0].name -> full URL.
_DEEP_PAGE_CAP = 500  # data-layer caps at the 10,000th result (page 501 -> 403). Never hit
#                       per make (max make < 10k -> <= 500 pages), but a guard against drift.
_CARDS_PER_PAGE = 20  # the SRP serves 20 fully-populated cars per request.

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

# Default proof cap: cars to CAGE this run (NOT the ~92,312 full set — full drain = --all).
# The original per-PDP slice caged ~4,490; the parallelized SRP surface targets a much
# larger bounded proof in-turn (drains several COMPLETE make partitions, not just a page).
DEFAULT_LIMIT = 16000

# Default concurrency: SRP pages fetched in parallel per sliding window. The governor's
# per-host bucket (www.coches.com paced conservatively, t1_soft stealth surface) is the
# real limiter, so this only needs to keep the bucket saturated — ~10 in-flight comfortably
# feeds the bucket without idle gaps. Higher just queues on the bucket.
DEFAULT_CONCURRENCY = 10

# The __NEXT_DATA__ SSR blob carries the full structured classifieds (vehicle + dealer).
_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)


def coches_platform_cdp_code() -> str:
    """The coches.com platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:coches.com'), province segment '00' (national). Mirrors
    coches_net_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{COCHES_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Make-slug derivation (recipe: VERIFIED across all 93 makes live 2026-06-12).
# ASCII-fold (NFKD strip accents) -> lowercase -> drop '&' and '.' -> spaces to '-' ->
# collapse repeated '-'. Resolves 92/93 makes directly to total==count; the edge LYNK & CO
# -> lynk-co is covered by drop-'&' + collapse-'-'. Belt-and-braces: the drain asserts
# classifieds.total == seoData count on page 1 of each make before walking the partition.
# ---------------------------------------------------------------------------
def make_slug(text: str) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    t = t.lower().replace("&", " ").replace(".", " ")
    t = re.sub(r"\s+", "-", t.strip())
    t = re.sub(r"-+", "-", t)
    return t


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL response — field names inspected live, not assumed).
# classifieds.classifiedList[i] verified 2026-06-12 against the live SRP; it is a SUPERSET
# of the PDP classified blob (adds imageList/showroomList/financing inline).
# ---------------------------------------------------------------------------


@dataclass
class DealerRef:
    """The selling dealer parsed from card.dealer + card.currentProvince.

    coches.com's dealer carries name + crmId (stable coches.com-canonical dealer key) +
    type + uuid (+ taxIdNumber on the PDP surface; ABSENT on the SRP card -> None). The geo
    anchor comes from the card's currentProvince.id (INE province code); the dealer object
    has no address/municipality on this surface, so province is the geo grain we have."""
    crm_id: str
    name: str | None
    cif: str | None
    dealer_type: str | None
    uuid: str | None
    province_code: str | None


@dataclass
class Vehicle:
    """A car parsed from a single coches.com SRP card (the classified blob)."""
    deep_link: str
    listing_ref: str           # card.visibleId (== ?id= in URL); also externalId
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
    """coches.com card.currentProvince.id IS the INE province code (28=Madrid,
    41=Sevilla — verified live). Zero-pad to 2 digits, reject out-of-range."""
    n = _to_int(province_id)
    if n is None or not (1 <= n <= 52):
        return None
    return f"{n:02d}"


def _name(obj) -> str | None:
    """card.make/model/version/fuel/transmission are {id, name} objects."""
    if isinstance(obj, dict):
        return obj.get("name")
    return None


def parse_card_dealer(card: dict) -> DealerRef | None:
    """Parse the SELLING DEALER from card.dealer + card.currentProvince.

    Only dealers with a crmId become entities (the stable per-dealer key used for
    cross-source dedup and as the source_ref). Geo comes from the card's currentProvince
    (the dealer object has no address on this surface)."""
    dealer = card.get("dealer") or {}
    crm_id = dealer.get("crmId")
    if not crm_id:
        return None
    prov = _prov2((card.get("currentProvince") or {}).get("id"))
    tax = dealer.get("taxIdNumber") or None  # absent on SRP card; often "" on PDP -> None
    return DealerRef(
        crm_id=str(crm_id),
        name=dealer.get("name"),
        cif=(tax.strip() or None) if isinstance(tax, str) else None,
        dealer_type=dealer.get("type"),
        uuid=dealer.get("uuid"),
        province_code=prov,
    )


def _card_image(card: dict) -> str | None:
    """The SRP card ships a ready `image` URL; fall back to imageList[0].name -> full URL."""
    img = card.get("image")
    if isinstance(img, str) and img:
        return img
    images = card.get("imageList")
    if isinstance(images, list):
        for im in images:
            if isinstance(im, dict) and im.get("name"):
                return _IMAGE_BASE + im["name"]
    return None


def canonical_deep_link(visible_id: str) -> str:
    """The CANONICAL, slug-free PDP deep link, keyed ONLY on visibleId.

    The car's stable identity on coches.com is its visibleId (== ?id= in the URL); the SEO
    slug prefix is cosmetic and volatile. The SRP card does NOT ship the slug, so a slugged
    link would drift from the sitemap-<loc> form the per-PDP path stored — splitting one car
    into two rows under the (dealer, deep_link) key. This canonical form is identical from
    ANY surface (PDP <loc>, SRP card, a future API), so re-runs and cross-surface harvests
    converge on ONE key. Verified live: coches.com serves ?id={visibleId} (200) and redirects
    it to the full SEO PDP for that exact car — a stable, working link."""
    visible = (visible_id or "").strip()
    return f"{_SRP_ALL}?id={visible}" if visible else _SRP_ALL


def parse_card_vehicle(card: dict) -> Vehicle:
    """Parse the car from a coches.com SRP card (REAL field map, verified live)."""
    price_obj = card.get("price") or {}
    amount = price_obj.get("amount")
    try:
        price = float(amount) if amount is not None else None
    except (TypeError, ValueError):
        price = None

    # priceOffer (the "precio contado"/financed offer) is the lower headline. When it is
    # below the list price, record it as a price-drop signal (the coches.com analogue of
    # coches.net's priceDropData — gold for delta).
    offer_obj = card.get("priceOffer") or {}
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

    reg = card.get("registration") or {}
    year = _to_int(reg.get("year"))
    if year is not None and not (1900 <= year <= 2100):
        year = None

    km = _to_int((card.get("mileage") or {}).get("amount"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    make = _name(card.get("make"))
    model = _name(card.get("model"))
    version = _name(card.get("version"))
    title = " ".join(p for p in (make, model, version) if p) or None

    return Vehicle(
        deep_link=canonical_deep_link(str(card.get("visibleId") or card.get("id") or "")),
        listing_ref=str(card.get("visibleId") or card.get("id") or ""),
        title=title,
        make=make,
        model=model,
        year=year,
        km=km,
        price=price,
        fuel=_name(card.get("fuel")),            # UTF-8: "Híbrido Gasolina", "Diésel"
        transmission=_name(card.get("transmission")),  # "Automática" / "Manual"
        photo_url=_card_image(card),
        price_drop=price_drop,
    )


def extract_classifieds(html: str) -> dict | None:
    """Pull props.pageProps.classifieds from an SRP's __NEXT_DATA__ blob (the 20-card list +
    total). Returns None if the surface is missing (Imperva interstitial / structure drift)."""
    m = _NEXT_DATA_RE.search(html)
    if not m:
        return None
    try:
        data = json.loads(m.group(1))
    except (ValueError, TypeError):
        return None
    cl = ((data.get("props") or {}).get("pageProps") or {}).get("classifieds")
    return cl if isinstance(cl, dict) else None


def extract_all_makes(html: str) -> tuple[list[dict], int | None]:
    """Pull seoData[key='all-makes'] -> [{text, count}, ...] AND classifieds.total from the
    page-1 unfiltered SRP. The make list is the MECE partition; total is the reconcile peg."""
    m = _NEXT_DATA_RE.search(html)
    if not m:
        return [], None
    try:
        data = json.loads(m.group(1))
    except (ValueError, TypeError):
        return [], None
    pp = (data.get("props") or {}).get("pageProps") or {}
    total = _to_int((pp.get("classifieds") or {}).get("total"))
    seo = pp.get("seoData")
    makes: list[dict] = []
    if isinstance(seo, list):
        block = next((b for b in seo
                      if isinstance(b, dict) and b.get("key") == "all-makes"), None)
        if block:
            for e in (block.get("list") or []):
                if isinstance(e, dict) and e.get("text") and e.get("count"):
                    makes.append({"text": e["text"], "count": _to_int(e["count"])})
    return makes, total


# ---------------------------------------------------------------------------
# Fetch: a GET routed THROUGH the governor (same per-host choke point as AS24).
# ---------------------------------------------------------------------------


class CochesComFetcher:
    """A POOL of fingerprint-coherent curl_cffi GET sessions for coches.com SRP pages.

    Concurrency vs. coherence (same contract coches_net's CochesFetcher proved): a single
    curl_cffi Session is NOT safe across threads, and the governor runs each fetch in its
    own worker thread (asyncio.to_thread) — so a concurrent drain with ONE shared session
    would race the session's internal state. The fix is a small bounded POOL: one Session
    per concurrency slot, each its own Chrome fingerprint + cookie jar (so any Imperva
    `incap_ses_*` minted on the first hit replays within that slot). Across slots it looks
    like a handful of independent browsers walking the SRP. The governor's per-host bucket
    still bounds the AGGREGATE rate across every session, so the pool widens parallelism
    WITHOUT out-pacing the host (the choke point is the bucket, never the session count).

    `last_status` reflects the most recent GET across the pool — sufficient for the breaker's
    http_status signal (a throttle shows as the same non-200 on any slot).
    """

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch(self, url: str, *, slot: int = 0) -> str:
        """The synchronous GET on pool session `slot` (runs in a worker thread).

        Decodes `resp.content` explicitly as UTF-8 (recipe: load-bearing — r.text mojibakes
        accents). `slot` rides as a kwarg the governor forwards untouched, so each in-flight
        request GETs on its own leased, never-shared session (thread-safe). `slot` defaults
        to 0 so a sequential single-session call (make discovery) still holds. Raises on a
        non-200 so the breaker sees a challenge/ban (never masks an Imperva interstitial)."""
        session = self._sessions[slot]
        resp = session.get(url, headers=_HEADERS, impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url}")
        return resp.content.decode("utf-8", "replace")

    async def fetch_async(self, governed_fetch, url: str) -> str:
        """Lease a pool slot, fetch `url` THROUGH the governor on that slot, release it.

        `governed_fetch` is governor().wrap_fetch_text(self.fetch): the governor derives the
        host, waits on the per-host bucket (the real limiter), then runs the synchronous GET
        off the event loop — passing `slot` through to fetch. The slot lease guarantees no
        two concurrent coroutines ever touch the same session."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer (mirrors coches_net_wholesale: ensure platform, bulk-upsert dealer/vehicle,
# link edge, emit delta, all idempotent ON CONFLICT).
# ---------------------------------------------------------------------------

COCHES_PLATFORM_RECIPE = {
    "version": 2,
    "source": "coches.com",
    "scope": "platform-wholesale (SRP __NEXT_DATA__, per-make partition, 20 cars/req)",
    "engine": "curl_cffi+chrome131_impersonate+srp_next_data(GET)+make_partition",
    "access": ("FREE path, ZERO proxy (Chrome TLS fingerprint; no browser, no cookie "
               "warm-up). Imperva/Incapsula behind CloudFront -> is_tier1=true; serving "
               "the SRP __NEXT_DATA__ to chrome131 today (decaying-open window)."),
    "data_surface": "next_data",
    "surface_intent": "ssr_next_data",
    "uncapped_surface": ("SRP listing __NEXT_DATA__ carries 20 full cars/req "
                         "(props.pageProps.classifieds.classifiedList) vs 1 car/PDP — ~20x. "
                         "Deep pagination caps at the 10,000th result (page 501 -> 403); the "
                         "make facet is a MECE partition (Sum counts == total, no make >= 10k) "
                         "so a per-make walk reaches 100% under the cap."),
    "make_catalogue": ("page-1 unfiltered SRP /coches-segunda-mano/coches-ocasion.htm -> "
                       "seoData[key=all-makes] = 93 makes with exact counts (Sum == classifieds.total)"),
    "make_url": "GET https://www.coches.com/coches-segunda-mano/{make-slug}.htm?page={1..ceil(count/20)}",
    "make_slug": ("NFKD ASCII-fold -> lowercase -> drop & and . -> spaces to - -> collapse "
                  "repeated - ; assert classifieds.total==seoData count on page 1 before drain"),
    "encoding": "r.content.decode('utf-8') — load-bearing; r.text mojibakes accents",
    "platform_entity": ("kind=plataforma, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=TRUE, defense_tier=t1_soft, source_group=marketplace_motor, "
                        "role=platform, family=independent"),
    "dual_membership": "vehicle.entity_ulid=SELLING DEALER (compraventa); platform_listing edge=platform<->vehicle",
    "field_map": {
        "path": "props.pageProps.classifieds.classifiedList[i]",
        "id": "card.id (stable VO UUID; cross-make dedup key)",
        "deep_link": ("CANONICAL slug-free https://www.coches.com/coches-segunda-mano/"
                      "coches-ocasion.htm?id={visibleId} — stable from any surface (SRP card "
                      "has no slug); coches.com 200-serves it and redirects to the SEO PDP"),
        "listing_ref": "card.visibleId (== ?id= ; also card.externalId)",
        "make": "card.make.name",
        "model": "card.model.name",
        "version": "card.version.name",
        "year": "card.registration.year (string -> int)",
        "km": "card.mileage.amount",
        "price": "card.price.amount (card.price.currency)",
        "price_offer": "card.priceOffer.amount (precio contado; drop signal when < price)",
        "fuel": "card.fuel.name (UTF-8: Híbrido Gasolina/Diésel/...)",
        "transmission": "card.transmission.name (Automática/Manual)",
        "photo_url": "card.image (ready URL) | https://images.coches.com/_ccom_/ + card.imageList[0].name",
        "dealer": "card.dealer {name, crmId, type, uuid, taxIdNumber(=CIF when present)}",
        "location": "card.currentProvince {id(=INE province code), name}",
    },
    "parallelization": ("93 independent make streams under ONE per-host governor bucket; a "
                        "concurrent sliding window of SRP pages keeps the bucket saturated."),
    "escalation_reserve": ("if Imperva flips to active JS challenge (interstitial / "
                           "_Incapsula_Resource / 403): camoufox/nodriver homepage warm-up "
                           "to mint incap_ses_*, export cookies to curl_cffi (vectors #5/#6). "
                           "The pvt JSON API (api-coches.pro.pvt.coches.com, X-App header + "
                           "anonymous JWT/fingerprint gate) is mapped but token-walled."),
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the coches.com platform entity + platform_meta exist.
    Returns the platform entity_ulid. Sets the multi-axis classification (0016):
    defense_tier=t1_soft, source_group=marketplace_motor, role=platform, family=independent.
    data_surface='next_data' (the SSR surface)."""
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
        eulid, json.dumps({"srp_root": _SRP_ROOT, "host": host_of(_SRP_HOST),
                           "method": "GET", "surface_intent": "ssr_next_data",
                           "classifieds_path": "props.pageProps.classifieds.classifiedList",
                           "make_partition": "seoData[all-makes]", "cards_per_page": _CARDS_PER_PAGE,
                           "declared_total_observed": 92312,
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


# The bulk statements. Each is ONE round-trip per table per window (unnest-based multi-row
# upsert), replacing per-row serialized statements. The ON CONFLICT clauses are byte-for-byte
# the same idempotency the per-row path used, so a re-run of an already-harvested partition
# adds 0 rows and 0 events.

_BULK_UPSERT_DEALERS = """
INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name, cif,
        province_code, municipality_code, is_tier1, status, kind_source,
        source_group, role, sells_cars, first_discovered_source, last_seen)
SELECT u.entity_ulid, u.cdp_code, 'compraventa', u.name, u.name, u.cif,
       u.province_code, u.municipality_code, FALSE, 'active', 'platform_label',
       $8::source_group, 'standalone_pos'::entity_role, TRUE, $7, now()
  FROM unnest($1::text[], $2::text[], $3::text[], $4::char(2)[], $5::char(5)[],
              $6::text[], $9::text[]) AS u(entity_ulid, cdp_code, name, province_code,
                               municipality_code, source_ref, cif)
ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
        cif = COALESCE(entity.cif, EXCLUDED.cif)
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


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


@dataclass
class _CageRow:
    """One fully-parsed, geo-anchored car ready for the bulk cage — the in-memory result of
    the parse+resolve phase, before any SQL. Carries everything the batched upserts need so
    the DB phase touches no per-item Python logic, only set-based statements."""
    crm_id: str
    dealer_cdp: str
    dealer_name: str | None
    dealer_cif: str | None
    dealer_province: str
    dealer_muni: str | None
    vehicle: Vehicle


def _parse_window(cards_in_order: list[tuple[str, list]], geo: GeoResolver,
                  seen_ids: set, harvested_cageable: set, stats: dict) -> list[_CageRow]:
    """Parse + geo-resolve every card across the window IN PAGE ORDER — pure CPU, no SQL.

    Applies the EXACT per-item gate the per-PDP path applied (cross-page/cross-make dedup on
    the stable card id, private/no-crm skip, geo skip, cageable truth), lifted out of the DB
    loop so the SQL phase is purely set-based. `seen_ids`/`harvested_cageable`/`stats` are
    mutated here with deterministic page-order semantics, so the VAM truth is identical to a
    row-by-row drain. `cards_in_order` = [(make_slug, [card, ...]), ...] in deterministic order."""
    rows: list[_CageRow] = []
    for _make_slug, cards in cards_in_order:  # slug is context only; deep_link is slug-free
        for card in cards:
            stats["cards_seen"] += 1
            card_id = str(card.get("id") or "")
            if card_id and card_id in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue  # cross-page / cross-make dedup (a car lives under one make)
            if card_id:
                seen_ids.add(card_id)

            d = parse_card_dealer(card)
            if d is None:
                stats["private_skipped"] += 1
                continue
            stats["dealer_items"] += 1

            # Geo gate — the exact same province-range guard upsert_dealer applied, done in
            # memory so a bad province is skipped without ever touching the DB (no FK risk).
            if not d.province_code:
                stats["geo_skipped"] += 1
                continue
            if not (d.province_code.isdigit() and "01" <= d.province_code <= "52"):
                stats["geo_skipped"] += 1
                continue
            muni = None  # the card has no municipality on this surface; province is the grain
            dealer_cdp = cdp_code_dealer(d, muni)

            v = parse_card_vehicle(card)
            if not v.deep_link:
                continue
            harvested_cageable.add((d.crm_id, v.deep_link))
            if v.price_drop:
                stats["price_drops_captured"] += 1
            rows.append(_CageRow(
                crm_id=d.crm_id, dealer_cdp=dealer_cdp, dealer_name=d.name,
                dealer_cif=d.cif, dealer_province=d.province_code, dealer_muni=muni,
                vehicle=v))
    return rows


async def _ingest_window(conn: asyncpg.Connection, geo: GeoResolver, platform_ulid: str,
                         cards_in_order: list[tuple[str, list]], seen_ids: set,
                         harvested_cageable: set, stats: dict) -> None:
    """BULK-ingest a whole concurrent SRP window in ONE transaction with set-based SQL.

    One round-trip per table per window (unnest multi-row upserts). The delta/VAM/
    platform_listing semantics are preserved EXACTLY: same ON CONFLICT idempotency, same
    cageable truth, same NEW-event rule (emitted only for genuinely new vehicles), same
    price-drop capture. A re-run of an already-harvested window adds 0 rows and 0 events.
    """
    cage = _parse_window(cards_in_order, geo, seen_ids, harvested_cageable, stats)
    if not cage:
        return

    async with conn.transaction():
        # ---- DEALERS: dedup by cdp_code within the window, bulk-upsert, resolve ulids.
        dealers: dict[str, _CageRow] = {}
        for r in cage:
            dealers.setdefault(r.dealer_cdp, r)  # first occurrence wins (deterministic)
        d_ulids = [ulid() for _ in dealers]
        d_cdps = list(dealers.keys())
        d_names = [dealers[c].dealer_name for c in d_cdps]
        d_provs = [dealers[c].dealer_province for c in d_cdps]
        d_munis = [dealers[c].dealer_muni for c in d_cdps]
        d_refs = [dealers[c].crm_id for c in d_cdps]
        d_cifs = [dealers[c].dealer_cif for c in d_cdps]
        await conn.execute(_BULK_UPSERT_DEALERS, d_ulids, d_cdps, d_names, d_provs,
                           d_munis, d_refs, COCHES_SOURCE_KEY, SOURCE_GROUP, d_cifs)
        await conn.execute(_BULK_UPSERT_DEALER_SOURCES, d_cdps, d_refs, COCHES_SOURCE_KEY)
        cdp_to_ulid: dict[str, str] = {
            row["cdp_code"]: row["entity_ulid"]
            for row in await conn.fetch(
                "SELECT cdp_code, entity_ulid FROM entity "
                "WHERE cdp_code = ANY($1::text[])", d_cdps)
        }

        # ---- attach resolved dealer_ulid; dedup cars within the window by (dealer, deep_link).
        cars: dict[tuple[str, str], _CageRow] = {}
        for r in cage:
            du = cdp_to_ulid.get(r.dealer_cdp)
            if du is None:
                continue  # dealer upsert race-impossible here, but stay defensive
            key = (du, r.vehicle.deep_link)
            if key not in cars:
                cars[key] = r

        # ---- VEHICLES: one SELECT splits existing vs new (idempotency truth). Existing
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
            confirmed_new = []
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
        else:
            confirmed_new = []

        stats["cars_caged"] += len(car_keys)
        stats["new_cars"] += len(confirmed_new)

        # ---- EDGES: one batched upsert; RETURNING (xmax=0) counts genuinely new edges.
        e_vehicles = [vehicle_ulid_for[k] for k in car_keys]
        e_urls = [cars[k].vehicle.deep_link for k in car_keys]
        e_refs = [cars[k].vehicle.listing_ref for k in car_keys]
        e_prices = [cars[k].vehicle.price for k in car_keys]
        edge_rows = await conn.fetch(_BULK_UPSERT_EDGES, e_vehicles, e_urls, e_refs,
                                     e_prices, platform_ulid)
        stats["edges_created"] += sum(1 for row in edge_rows if row["inserted"])

        # ---- NEW delta events — only for genuinely new vehicles, price-drop preserved.
        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                v = cars[k].vehicle
                payload = {"price": v.price, "title": v.title, "platform": COCHES_TRADE_NAME}
                if v.price_drop:
                    payload["price_drop"] = v.price_drop
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities,
                               ev_payloads)
            stats["new_events"] += len(confirmed_new)


@dataclass
class _MakePartition:
    """One make stream: its slug, declared count, and computed page span. The partition the
    drain walks page-by-page until the result set is exhausted (or --limit is reached)."""
    text: str
    slug: str
    count: int
    pages: int


async def discover_makes(governed_fetch, fetcher: CochesComFetcher) -> tuple[list[_MakePartition], int]:
    """Fetch the page-1 unfiltered SRP, read seoData[all-makes] + classifieds.total, derive
    each make's slug + page span. Returns (partitions sorted by descending count, declared
    total). Asserts the MECE invariant (Sum counts == total) and logs any drift honestly."""
    html = await fetcher.fetch_async(governed_fetch, _SRP_ALL)
    makes, total = extract_all_makes(html)
    if not makes:
        raise RuntimeError("seoData[all-makes] missing on page-1 SRP (Imperva block / drift)")
    partitions: list[_MakePartition] = []
    sum_counts = 0
    for m in makes:
        c = m["count"] or 0
        sum_counts += c
        partitions.append(_MakePartition(
            text=m["text"], slug=make_slug(m["text"]), count=c,
            pages=max(1, math.ceil(c / _CARDS_PER_PAGE))))
    partitions.sort(key=lambda p: p.count, reverse=True)
    declared = total if total is not None else sum_counts
    if total is not None and sum_counts != total:
        print(f"[coches_com_wholesale] WARN: Sum(make counts)={sum_counts} != "
              f"classifieds.total={total} (live drift); using total as declared.")
    else:
        print(f"[coches_com_wholesale] make partition verified MECE: "
              f"{len(partitions)} makes, Sum counts={sum_counts} == total={declared}.")
    return partitions, declared


def _make_page_url(slug: str, page: int) -> str:
    """The per-make SRP page URL. page==1 has no query; page>1 adds ?page=N (recipe)."""
    base = f"{_SRP_ROOT}/{slug}.htm"
    return base if page <= 1 else f"{base}?page={page}"


async def harvest(limit: int = DEFAULT_LIMIT, concurrency: int = DEFAULT_CONCURRENCY,
                  drain_all: bool = False) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    # One coherent curl_cffi session PER concurrency slot (a single shared session is not
    # thread-safe under the governor's to_thread fetch). The per-host bucket still bounds the
    # aggregate rate across the whole pool, so the pool widens parallelism WITHOUT out-pacing.
    fetcher = CochesComFetcher(pool_size=concurrency)
    cage_limit = None if drain_all else max(1, limit)
    stats = {
        "makes_discovered": 0, "pages_fetched": 0, "page_errors": 0,
        "cards_seen": 0, "no_classifieds": 0, "dealer_items": 0, "private_skipped": 0,
        "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0, "new_cars": 0,
        "edges_created": 0, "new_events": 0, "price_drops_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "dealers_distinct": 0,
        "makes_completed": 0, "concurrency": concurrency, "drain_all": drain_all,
        "cage_limit": cage_limit,
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
    # every SRP page passes through www.coches.com's token bucket, off the event loop. No
    # matter how many pages are in flight, the host is never hammered: the bucket is the
    # limiter (conservative t1_soft stealth pace), not Python's awaits.
    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = coches_platform_cdp_code()
        print(f"[coches_com_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid})")
        print(f"[coches_com_wholesale] governor paces host {host_of(_SRP_HOST)} (per-host token bucket).")

        # Phase 1 — discover the make partition (the MECE catalogue + declared total).
        try:
            partitions, declared_full = await discover_makes(governed_fetch, fetcher)
        except Exception as e:  # noqa: BLE001 — page-1 SRP unreachable/challenged: fail honestly
            fetch_error = str(e)
            last_http = fetcher.last_status
            print(f"[coches_com_wholesale] make discovery failed ({e}); aborting drain.")
            await record_run(conn, COCHES_SOURCE_KEY, ok=False, rows=0,
                             error=fetch_error, http_status=last_http)
            repair = await auto_repair(conn, COCHES_SOURCE_KEY, fetch_error,
                                       phase="discover", http_status=last_http)
            return {"skipped": True, "reason": "discovery_failed", "error": fetch_error,
                    "repair_action": repair, "platform_code": platform_code}

        stats["declared_full"] = declared_full
        stats["makes_discovered"] = len(partitions)
        target = "ALL cells" if drain_all else f"{cage_limit} cars (proof cap)"
        print(f"[coches_com_wholesale] {len(partitions)} makes; declared full = {declared_full}; "
              f"CONCURRENT drain window={concurrency} pages; cage target = {target}.")
        print(f"[coches_com_wholesale] CONCURRENT drain: window={concurrency} SRP pages in flight "
              f"(governor is the limiter).")

        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        seen_ids: set[str] = set()

        # Phase 2 — walk each make partition page-by-page, fetching a concurrent window of
        # SRP pages at a time (paced by the bucket) and BULK-ingesting each window in one tx.
        # Pages stream across make boundaries so the window is always full: we keep a queue of
        # (slug, page) jobs, refilling it from the next make as the current make's pages drain.
        stop = False
        for part in partitions:
            if stop:
                break
            page_cap = min(part.pages, _DEEP_PAGE_CAP)
            next_page = 1
            make_done = False
            while next_page <= page_cap and not stop and not make_done:
                window = list(range(next_page, min(next_page + concurrency, page_cap + 1)))
                next_page = window[-1] + 1

                # fan-out: fetch every page in this window concurrently, paced by the bucket.
                results = await asyncio.gather(
                    *(fetcher.fetch_async(governed_fetch, _make_page_url(part.slug, p))
                      for p in window),
                    return_exceptions=True,
                )

                # fan-in: collect cards IN PAGE ORDER (deterministic dedup/counts). A page
                # error stops the drain honestly (Imperva wall); an empty classifiedList is
                # this make's terminator (recipe: ferrari p3 -> 0 cards) — stop THIS make,
                # keep draining the next.
                window_cards: list[tuple[str, list]] = []
                for page, data in zip(window, results):
                    if isinstance(data, Exception):
                        stats["page_errors"] += 1
                        last_http = fetcher.last_status
                        # The recipe's wall signal: a run of page failures = Imperva escalation.
                        if stats["page_errors"] > 10 and stats["page_errors"] > stats["pages_fetched"]:
                            fetch_error = f"SRP fetch wall: {data}"
                            print(f"[coches_com_wholesale] page failures dominate "
                                  f"({stats['page_errors']} errors); stopping drain (Imperva wall?).")
                            stop = True
                            break
                        continue
                    cl = extract_classifieds(data)
                    if cl is None:
                        stats["no_classifieds"] += 1
                        continue
                    cards = cl.get("classifiedList") or []
                    stats["pages_fetched"] += 1
                    if not cards:
                        make_done = True  # this make's result set is exhausted (terminator)
                        continue
                    window_cards.append((part.slug, cards))

                if window_cards:
                    await _ingest_window(conn, geo, platform_ulid, window_cards, seen_ids,
                                         harvested_cageable, stats)

                if stats["pages_fetched"] and stats["pages_fetched"] % 50 == 0:
                    print(f"[coches_com_wholesale] make={part.text} "
                          f"pages={stats['pages_fetched']} caged_total={stats['cars_caged']} "
                          f"new={stats['new_cars']} edges={stats['edges_created']} "
                          f"errors={stats['page_errors']}")

                # Proof cap: stop once the run has caged enough distinct cars (full drain skips).
                if cage_limit is not None and len(harvested_cageable) >= cage_limit:
                    print(f"[coches_com_wholesale] cage target reached "
                          f"({len(harvested_cageable)} >= {cage_limit}); stopping proof slice.")
                    stop = True
                    break

            if make_done or (next_page > page_cap):
                stats["makes_completed"] += 1

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
        # The declared full count is reported for honesty but is NOT a quorum path (it
        # measures the WHOLE platform, not what this run caged — unless --all completes it).
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
        # trips the breaker on a ban, and auto-repairs. OK when >=1 car cageable, no fetch
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
    mode = "FULL DRAIN" if stats.get("drain_all") else "PROOF SLICE"
    print(f"COCHES.COM WHOLESALE HARVEST — {mode} REPORT (SRP per-make, 20 cars/req)")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  declared full (source): {stats.get('declared_full')}"
          f"{'' if stats.get('drain_all') else '  (NOT fully harvested — proof slice)'}")
    print(f"  makes discovered      : {stats['makes_discovered']} (MECE partition)")
    print(f"  makes completed       : {stats['makes_completed']} (result set exhausted)")
    print(f"  concurrency (window)  : {stats.get('concurrency')} SRP pages in flight")
    print(f"  cage target           : {stats.get('cage_limit') if not stats.get('drain_all') else 'ALL cells'}")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  page errors           : {stats['page_errors']}")
    print(f"  cards seen            : {stats['cards_seen']}")
    print(f"  no classifieds        : {stats['no_classifieds']}")
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
    parser = argparse.ArgumentParser(
        description="coches.com wholesale harvester (SRP per-make concurrent drain, 20 cars/req)")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                        help=(f"max distinct cars to CAGE this run (proof cap); default "
                              f"{DEFAULT_LIMIT}. Ignored when --all is set."))
    parser.add_argument("--all", action="store_true",
                        help=("drain the WHOLE platform: every page of every make until each "
                              "make's result set is exhausted (the full 92k+ harvest)."))
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"SRP pages fetched in parallel per sliding window; default "
                              f"{DEFAULT_CONCURRENCY}. The governor's per-host bucket is the "
                              f"real limiter — this only needs to keep the bucket saturated."))
    parser.add_argument("--pages", type=int, default=None,
                        help="alias: pages*20 cars cage cap (CLI parity with the older slice flag)")
    args = parser.parse_args()
    limit = args.limit
    if args.pages is not None:
        limit = args.pages * _CARDS_PER_PAGE
    stats = asyncio.run(harvest(limit, args.concurrency, drain_all=args.all))
    _print_report(stats)


if __name__ == "__main__":
    main()
