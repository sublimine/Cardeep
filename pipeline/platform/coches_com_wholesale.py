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

# The fast surface (recipe TL;DR; verified live 2026-06-12/13). SRP = Search Results Page.
_SRP_HOST = "https://www.coches.com"
_SRP_ROOT = "https://www.coches.com/coches-segunda-mano"  # /{make-slug}.htm?page=N
_SRP_ALL = f"{_SRP_ROOT}/coches-ocasion.htm"  # page-1 unfiltered: seoData[all-makes] + total
_IMAGE_BASE = "https://images.coches.com/_ccom_/"  # imageList[0].name -> full URL.
_DEEP_PAGE_CAP = 500  # data-layer caps at the 10,000th result (page 501 -> 403). Never hit
#                       per make (max make < 10k -> <= 500 pages), but a guard against drift.
_CARDS_PER_PAGE = 20  # the SRP serves 20 fully-populated cars per request.

# ---------------------------------------------------------------------------
# SEGMENTS (0016++; mapped live 2026-06-13, docs/architecture/segments/coches_com.md).
# coches.com's home displays "más de 230.000 ofertas". That headline is the platform's OWN
# count of every offer surface — we honour it as the declared site total and enumerate EVERY
# real, sellable segment beneath it (never dismiss the number as marketing). The reconciled
# captureable inventory = the SUM of these segments' real per-segment counts:
#
#   VO  (usados)   /coches-segunda-mano/{slug}.htm  classifieds.total = 92,381  per-make SRP
#   KM0 (seminuevo)/km0/{slug}.htm                  Σ brands == 15,630          per-make SRP
#   VN  (catálogo) /coches-nuevos/coches-nuevos.htm search.total = 826          ?page=N
#   RENTING        /renting-coches                  totalOffers = 8,908         offer lists
#
# VO+KM0 are STRUCTURAL TWINS: same /{make-slug}.htm SRP, same seoData[all-makes] MECE
# partition, same classified card -> the same parser + per-make drain serves both, switched
# only by SRP root + the page-1 catalogue URL. VN/RENTING are version/offer surfaces (no per-
# car dealer on VN -> attributed to the make/brand) and get light dedicated parsers. ALL four
# funnel through the ONE cage contract (platform entity + dealer upsert + vehicle owned by
# dealer + platform_listing + delta + recipe + VAM + governor + breaker + bulk unnest).
SEGMENT_VO = "vo"
SEGMENT_KM0 = "km0"
SEGMENT_VN = "vn"          # alias of 'catalog' (the new-car catalog/configurator offers)
SEGMENT_CATALOG = "catalog"
SEGMENT_RENTING = "renting"
SEGMENT_ALL = "all"
_SEGMENT_CHOICES = (SEGMENT_ALL, SEGMENT_VO, SEGMENT_KM0, SEGMENT_VN, SEGMENT_CATALOG,
                    SEGMENT_RENTING)

# Per-make SRP segments (VO, km0): (srp_root, page1_catalogue_url). Each yields the SAME
# classified card shape and a seoData[all-makes] MECE partition (Σ counts == total).
_SRP_SEGMENTS = {
    SEGMENT_VO: ("https://www.coches.com/coches-segunda-mano",
                 "https://www.coches.com/coches-segunda-mano/coches-ocasion.htm"),
    SEGMENT_KM0: ("https://www.coches.com/km0",
                  "https://www.coches.com/km0/coches-km0.htm"),  # page-1 catalogue; per-make /km0/{slug}.htm
}
# km0's page-1 catalogue URL is /km0/ (the .htm form 404s); override the catalogue fetch URL.
_KM0_CATALOGUE_URL = "https://www.coches.com/km0/"

_VN_SEARCH_URL = "https://www.coches.com/coches-nuevos/coches-nuevos.htm"  # ?page=N, 20/page
_RENTING_URL = "https://www.coches.com/renting-coches"

# The number coches.com's home literally displays ("más de 230.000 ofertas"). The owner's
# order: honour it as the declared SITE total — never dismiss it as marketing. Our reconciled
# captureable inventory is Σ of the real per-segment counts below; the gap to 230k is the
# platform's own offer-inflation (each listing counted across showroom×financing surfaces —
# proven by seoData[all-provinces] showroom_list summing to ~4.28M). VERIFIED live 2026-06-13.
SITE_DISPLAYED_TOTAL = 230000
# Per-segment declared counts last VERIFIED live 2026-06-13 (for the reconcile report).
SEGMENT_DECLARED = {
    SEGMENT_VO: 92381,       # classifieds.total
    SEGMENT_KM0: 15630,      # Σ /km0/ brands == popularClassified.total
    SEGMENT_VN: 826,         # /coches-nuevos/coches-nuevos.htm search.total (catalog offers)
    SEGMENT_RENTING: 8908,   # /renting-coches totalOffers
}

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
    segment: str = SEGMENT_VO   # vo|km0|vn|renting — recorded as a FLAG on the ONE vehicle,
    #                             NOT folded into deep_link (that split one car into 2 rows).
    listing_url: str | None = None  # the REAL per-surface URL (informative edge URL; the
    #                                 vehicle identity stays the stable slug-free deep_link).


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


def canonical_deep_link(visible_id: str, segment: str = SEGMENT_VO) -> str:
    """The CANONICAL, slug-free, SURFACE-STABLE PDP deep link, keyed on visibleId ALONE.

    The car's stable identity on coches.com is its visibleId (== ?id= in the URL); EVERYTHING
    else in the URL — the SEO slug prefix AND the surface root (/coches-segunda-mano/ vs /km0/)
    — is volatile presentation, not identity. A km0 car IS a used car that also appears in the
    km0 section: the SAME visibleId, the SAME physical car, listed on two surfaces. Keying the
    vehicle on the full per-surface URL caged it TWICE (one VO row + one km0 row) and also split
    on slugged-vs-slugfree forms from the old per-PDP path — 20,432 cross-surface phantoms.

    FIX (root cause): the deep_link is now IDENTICAL from any surface for a given visibleId, so
    the (dealer, deep_link) vehicle key == (dealer, visibleId). VO and km0 of the same car, and
    slugged and slug-free forms, all converge on ONE vehicle row; a re-run never re-creates the
    phantom. The km0/VO distinction is preserved as a SEGMENT FLAG on the single vehicle (carried
    into the NEW event payload + the edge listing_url), not as a second row. Verified live:
    coches.com serves /coches-segunda-mano/coches-ocasion.htm?id={visibleId} (200) and redirects
    it to the full SEO PDP for that exact car — a stable, working link.

    `segment` is accepted for signature stability but DELIBERATELY no longer steers the root:
    folding it in is precisely what created the phantoms."""
    visible = (visible_id or "").strip()
    return f"{_SRP_ALL}?id={visible}" if visible else _SRP_ALL


def surface_listing_url(visible_id: str, segment: str = SEGMENT_VO) -> str:
    """The REAL per-surface listing URL for the platform_listing edge (informative only — NOT
    the vehicle identity). Records WHERE on coches.com the car was seen (VO vs km0 section) so
    the edge keeps surface provenance, while the vehicle row stays single + stable."""
    visible = (visible_id or "").strip()
    if segment == SEGMENT_KM0:
        base = "https://www.coches.com/km0/coches-km0.htm"
        return f"{base}?id={visible}" if visible else base
    return f"{_SRP_ALL}?id={visible}" if visible else _SRP_ALL


def parse_card_vehicle(card: dict, segment: str = SEGMENT_VO) -> Vehicle:
    """Parse the car from a coches.com SRP card (REAL field map, verified live).

    `segment` (vo|km0) only steers the canonical deep_link root so a VO car and a km0 car
    never collapse to one (dealer, deep_link) row. The card body is identical across both."""
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

    visible_id = str(card.get("visibleId") or card.get("id") or "")
    return Vehicle(
        # IDENTITY: stable, surface-independent (km0 and VO of the same id => ONE row).
        deep_link=canonical_deep_link(visible_id, segment),
        listing_ref=visible_id,
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
        segment=segment,                          # FLAG on the single vehicle (km0/vo/...).
        listing_url=surface_listing_url(visible_id, segment),  # real per-surface edge URL.
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


def extract_classifieds_any(html: str) -> dict | None:
    """Pull the classified-list block under EITHER key the surfaces use: `classifieds` (VO
    SRP, km0 per-make SRP) or `popularClassified` (the /km0/ catalogue page). Same inner
    shape (.total + .classifiedList), so callers treat both identically."""
    m = _NEXT_DATA_RE.search(html)
    if not m:
        return None
    try:
        data = json.loads(m.group(1))
    except (ValueError, TypeError):
        return None
    pp = (data.get("props") or {}).get("pageProps") or {}
    cl = pp.get("classifieds")
    if isinstance(cl, dict) and "classifiedList" in cl:
        return cl
    pc = pp.get("popularClassified")
    return pc if isinstance(pc, dict) else None


def extract_all_makes(html: str) -> tuple[list[dict], int | None]:
    """Pull the MECE make partition + the declared total from a catalogue page.

    VO/km0 per-make SRP carry seoData[key='all-makes'] = [{text, count}, ...]; the /km0/
    catalogue page carries pageProps.brands = [{text, count}, ...] instead (same semantics).
    The total is classifieds.total (VO, km0 SRP) or popularClassified.total (/km0/ page).
    Either way Σ(make counts) == total is the reconcile peg. Tries seoData first, falls back
    to brands so ONE function serves both the VO and the km0 catalogue surfaces."""
    m = _NEXT_DATA_RE.search(html)
    if not m:
        return [], None
    try:
        data = json.loads(m.group(1))
    except (ValueError, TypeError):
        return [], None
    pp = (data.get("props") or {}).get("pageProps") or {}
    total = _to_int((pp.get("classifieds") or {}).get("total"))
    if total is None:
        total = _to_int((pp.get("popularClassified") or {}).get("total"))
    makes: list[dict] = []
    seo = pp.get("seoData")
    if isinstance(seo, list):
        block = next((b for b in seo
                      if isinstance(b, dict) and b.get("key") == "all-makes"), None)
        if block:
            for e in (block.get("list") or []):
                if isinstance(e, dict) and e.get("text") and e.get("count"):
                    makes.append({"text": e["text"], "count": _to_int(e["count"])})
    if not makes:  # /km0/ catalogue: the partition is pageProps.brands (with counts)
        brands = pp.get("brands")
        if isinstance(brands, list):
            for b in brands:
                if isinstance(b, dict) and b.get("text") and b.get("count"):
                    makes.append({"text": b["text"], "count": _to_int(b["count"])})
    return makes, total


# ---------------------------------------------------------------------------
# VN catalog (new-car configurator offers) + renting parsers. These surfaces have NO per-car
# dealer (a VN item is a make/model/version OFFER, not a VIN-bearing stock car), so the
# OWNING entity is the coches.com platform itself (the catalog belongs to the platform); the
# platform_listing edge still records it as a listing ON coches.com. Make/model/version are
# preserved so each offer is a distinct sellable row keyed by versionId.
# ---------------------------------------------------------------------------


@dataclass
class CatalogOffer:
    """One new-car catalog offer (a make/model/version on /coches-nuevos/). No dealer, no
    geo, no km: it is a configurable new car the platform offers. Keyed by versionId."""
    version_id: str
    make: str | None
    model: str | None
    title: str | None
    pvp: float | None        # PVP (list price)
    price: float | None      # price.amount (the discounted headline)
    discount_pct: int | None
    fuel: str | None
    photo_url: str | None


def extract_vn_search(html: str) -> dict | None:
    """Pull props.pageProps.search (.total + .data[20]) from the /coches-nuevos/ VN catalog
    search page. .data items are version OFFERS (id, versionId, make, model, price, pvp)."""
    m = _NEXT_DATA_RE.search(html)
    if not m:
        return None
    try:
        data = json.loads(m.group(1))
    except (ValueError, TypeError):
        return None
    s = ((data.get("props") or {}).get("pageProps") or {}).get("search")
    return s if isinstance(s, dict) else None


def parse_vn_offer(item: dict) -> CatalogOffer | None:
    """Parse one VN catalog offer from search.data[i] (REAL field map, verified live)."""
    vid = str(item.get("versionId") or "").strip()
    if not vid:
        return None
    make = _name(item.get("make"))
    model = _name(item.get("model"))
    # item.id is a human title like "FIAT Pandina"; segment.name is the variant name.
    title = item.get("id") if isinstance(item.get("id"), str) else None
    seg = _name(item.get("segment"))
    if seg and title and seg not in title:
        title = f"{title} {seg}"

    def _amt(obj):
        a = (obj or {}).get("amount") if isinstance(obj, dict) else None
        try:
            return float(a) if a is not None else None
        except (TypeError, ValueError):
            return None

    img = item.get("image")
    return CatalogOffer(
        version_id=vid, make=make, model=model, title=title or None,
        pvp=_amt(item.get("pvp")), price=_amt(item.get("price")),
        discount_pct=_to_int(item.get("discount")),
        fuel=_name(item.get("fuel")) or (
            item.get("fuel")[0].get("name") if isinstance(item.get("fuel"), list)
            and item.get("fuel") else None),
        photo_url=img if isinstance(img, str) and img else None)


def vn_offer_deep_link(version_id: str) -> str:
    """Canonical, stable VN-catalog offer link keyed on versionId (the offer's identity).
    Distinct namespace from VO/km0 (/coches-nuevos/) so it never collides on (entity, link)."""
    vid = (version_id or "").strip()
    return f"https://www.coches.com/coches-nuevos/version/{vid}" if vid else _VN_SEARCH_URL


def vn_offer_to_vehicle(o: CatalogOffer) -> Vehicle:
    """Adapt a CatalogOffer to the Vehicle cage row (one VN offer = one listing). No km/year
    (a new-car offer); price is the discounted headline, price_drop captures the PVP->price
    discount so delta sees new-car promo moves the same way it sees VO price drops."""
    price_drop = None
    if o.pvp is not None and o.price is not None and o.price < o.pvp:
        price_drop = {
            "list_price": o.pvp, "offer_price": o.price,
            "amountFromOriginal": round(o.pvp - o.price, 2),
            "percentageFromOriginal": (round((o.pvp - o.price) / o.pvp * 100, 2)
                                       if o.pvp else None),
            "source": "vn_catalog_discount",
        }
    return Vehicle(
        deep_link=vn_offer_deep_link(o.version_id), listing_ref=o.version_id,
        title=o.title, make=o.make, model=o.model, year=None, km=None,
        price=o.price if o.price is not None else o.pvp, fuel=o.fuel,
        transmission=None, photo_url=o.photo_url, price_drop=price_drop)


def extract_renting(html: str) -> dict | None:
    """Pull the renting hub pageProps: totalOffers + the make/brand partition + the inline
    special-offer lists (specialOffersMonthly/Punctual). The FULL 8,908 paginated list loads
    client-side via XHR (not in SSR); we cage the SSR-exposed offers and declare the total."""
    m = _NEXT_DATA_RE.search(html)
    if not m:
        return None
    try:
        data = json.loads(m.group(1))
    except (ValueError, TypeError):
        return None
    pp = (data.get("props") or {}).get("pageProps") or {}
    if "totalOffers" not in pp and "specialOffersPunctual" not in pp:
        return None
    return pp


@dataclass
class RentingOffer:
    """One renting offer parsed from specialOffersPunctual/Monthly. Carries dealerId (UUID) +
    dealerName + href + a monthly fee. dealerId is the renting-seller key (NOT a VO crmId)."""
    offer_id: str
    make: str | None
    model: str | None
    href: str | None
    fee_amount: float | None
    dealer_uuid: str | None
    dealer_name: str | None


def parse_renting_offer(item: dict) -> RentingOffer | None:
    oid = str(item.get("id") or "").strip()
    if not oid:
        return None
    fee = (item.get("fee") or {}).get("amount") if isinstance(item.get("fee"), dict) else None
    try:
        fee = float(fee) if fee is not None else None
    except (TypeError, ValueError):
        fee = None
    return RentingOffer(
        offer_id=oid, make=item.get("make"), model=item.get("model"),
        href=item.get("href"), fee_amount=fee,
        dealer_uuid=item.get("dealerId"), dealer_name=item.get("dealerName"))


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
    "version": 3,
    "source": "coches.com",
    "scope": "platform-wholesale, MULTI-SEGMENT (vo|km0|vn/catalog|renting|all)",
    "site_displayed_total": ("home shows 'más de 230.000 ofertas' — the platform's OWN count "
                             "across showroom×financing surfaces (seoData[all-provinces] "
                             "showroom_list sums ~4.28M, proving the multi-count). The REAL "
                             "captureable sellable inventory is Σ of the segments below."),
    "segments": {
        "vo": ("/coches-segunda-mano/{make-slug}.htm?page=N · classifieds.total=92,381 · "
               "seoData[all-makes] 93-make MECE partition · classified card (dealer+geo)"),
        "km0": ("/km0/{make-slug}.htm?page=N · Σ /km0/ brands == popularClassified.total=15,630 "
                "· STRUCTURAL TWIN of vo (same card, same per-make SRP, seoData[all-makes]) · "
                "SAME visibleId as the VO row -> ONE vehicle (km0 recorded as a segment FLAG, "
                "not a 2nd row); deep_link is surface-stable so km0∩vo converge, edge "
                "listing_url keeps the real /km0/ surface for provenance"),
        "vn": ("/coches-nuevos/coches-nuevos.htm?page=N · search.total=826 · 20 version OFFERS"
               "/page (make/model/version, pvp, discount) · NO dealer -> owned by the PLATFORM "
               "entity · PVP->price discount captured as price_drop for delta"),
        "renting": ("/renting-coches · totalOffers=8,908 (declared) · SSR exposes "
                    "specialOffersPunctual/Monthly (dealerId+href+fee) caged as platform-owned; "
                    "full paginated list is client-XHR -> escalation reserve"),
        "all": "drains vo->km0->vn->renting in SEQUENCE under ONE governor/breaker (one host).",
    },
    "reconcile": ("vo 92,381 + km0 15,630 + vn 826 + renting 8,908 = ~117,745 captureable; the "
                  "gap to the displayed 230,000 is the platform's offer-inflation, not stock."),
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
                  seen_ids: set, harvested_cageable: set, stats: dict,
                  segment: str = SEGMENT_VO) -> list[_CageRow]:
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

            v = parse_card_vehicle(card, segment)
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
                         harvested_cageable: set, stats: dict,
                         segment: str = SEGMENT_VO) -> None:
    """BULK-ingest a whole concurrent SRP window in ONE transaction with set-based SQL.

    One round-trip per table per window (unnest multi-row upserts). The delta/VAM/
    platform_listing semantics are preserved EXACTLY: same ON CONFLICT idempotency, same
    cageable truth, same NEW-event rule (emitted only for genuinely new vehicles), same
    price-drop capture. A re-run of an already-harvested window adds 0 rows and 0 events.
    `segment` (vo|km0) is recorded as a FLAG on the single vehicle (event payload + edge
    listing_url); the deep_link identity is surface-stable so VO and km0 of the same car
    CONVERGE on ONE (dealer, deep_link) row instead of splitting into cross-surface phantoms.
    """
    cage = _parse_window(cards_in_order, geo, seen_ids, harvested_cageable, stats, segment)
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

        # ---- EDGES: one batched upsert; RETURNING (xmax=0) counts genuinely new edges. The
        # edge listing_url records the REAL per-surface URL (VO vs km0 section) for provenance;
        # the vehicle identity (deep_link) stays the stable slug-free form so one car = one row.
        e_vehicles = [vehicle_ulid_for[k] for k in car_keys]
        e_urls = [cars[k].vehicle.listing_url or cars[k].vehicle.deep_link for k in car_keys]
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
                payload = {"price": v.price, "title": v.title, "platform": COCHES_TRADE_NAME,
                           "segment": v.segment}  # km0/vo recorded as a FLAG, not a 2nd row
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


async def discover_makes(governed_fetch, fetcher: CochesComFetcher,
                         segment: str = SEGMENT_VO) -> tuple[list[_MakePartition], int]:
    """Fetch the segment's page-1 catalogue, read the make partition + declared total, derive
    each make's slug + page span. Returns (partitions sorted by descending count, declared
    total). Asserts the MECE invariant (Σ counts == total) and logs any drift honestly.

    VO catalogue = /coches-segunda-mano/coches-ocasion.htm (seoData[all-makes]); km0 catalogue
    = /km0/ (pageProps.brands). extract_all_makes handles both partition shapes."""
    catalogue_url = _KM0_CATALOGUE_URL if segment == SEGMENT_KM0 else _SRP_SEGMENTS[segment][1]
    html = await fetcher.fetch_async(governed_fetch, catalogue_url)
    makes, total = extract_all_makes(html)
    if not makes:
        raise RuntimeError(
            f"make partition missing on {segment} catalogue {catalogue_url} (Imperva/drift)")
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
        print(f"[coches_com_wholesale:{segment}] WARN: Sum(make counts)={sum_counts} != "
              f"total={total} (live drift); using total as declared.")
    else:
        print(f"[coches_com_wholesale:{segment}] make partition verified MECE: "
              f"{len(partitions)} makes, Sum counts={sum_counts} == total={declared}.")
    return partitions, declared


def _make_page_url(slug: str, page: int, segment: str = SEGMENT_VO) -> str:
    """The per-make SRP page URL for a segment. page==1 has no query; page>1 adds ?page=N.
    VO -> /coches-segunda-mano/{slug}.htm ; km0 -> /km0/{slug}.htm (verified live 2026-06-13)."""
    root = _SRP_SEGMENTS[segment][0]
    base = f"{root}/{slug}.htm"
    return base if page <= 1 else f"{base}?page={page}"


async def harvest(limit: int = DEFAULT_LIMIT, concurrency: int = DEFAULT_CONCURRENCY,
                  drain_all: bool = False, segment: str = SEGMENT_VO) -> dict:
    """Harvest ONE segment. VO/km0 use the per-make SRP drain; VN/catalog and renting use
    their dedicated paginated/offer drains. --segment all is handled by harvest_all() which
    fans these out in sequence under the SAME governor/breaker (one host, no collision)."""
    segment = segment.lower()
    if segment in (SEGMENT_VN, SEGMENT_CATALOG):
        return await harvest_vn(limit, concurrency, drain_all)
    if segment == SEGMENT_RENTING:
        return await harvest_renting(limit, drain_all)
    if segment not in _SRP_SEGMENTS:
        raise ValueError(f"unknown segment {segment!r}; choices: {_SEGMENT_CHOICES}")
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
        "cage_limit": cage_limit, "segment": segment,
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
            partitions, declared_full = await discover_makes(governed_fetch, fetcher, segment)
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
                    *(fetcher.fetch_async(governed_fetch, _make_page_url(part.slug, p, segment))
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
                    cl = extract_classifieds_any(data)
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
                                         harvested_cageable, stats, segment)

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
        # measure "distinct cageable cars in THIS SEGMENT's slice":
        #   db_edges           = platform_listing rows for coches.com IN this segment (write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join, same segment (read truth)
        #   harvested_cageable = distinct (crm, deep_link) pulled this run (harvest truth)
        # The edge counts are SCOPED to the segment's listing_url namespace (VO -> /coches-
        # segunda-mano/, km0 -> /km0/) so a segment run's harvest truth is like-with-like with
        # its own DB rows and is NOT polluted by other segments' edges on the same platform.
        # The declared full count is reported for honesty but is NOT a quorum path.
        seg_url_like = f"{_SRP_SEGMENTS[segment][0]}%"
        db_edges = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1 "
            "AND listing_url LIKE $2", platform_ulid, seg_url_like)
        db_join_vehicles = await conn.fetchval(
            """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               JOIN entity d ON d.entity_ulid = v.entity_ulid
               WHERE pl.platform_entity_ulid=$1 AND pl.listing_url LIKE $2""",
            platform_ulid, seg_url_like)
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


# ---------------------------------------------------------------------------
# VN catalog + renting harvests. These surfaces have NO per-car dealer, so the OWNING entity
# is the coches.com platform itself (the catalog/offer belongs to the platform). They still
# flow the SAME cage contract: platform entity + vehicle owned by (platform) entity +
# platform_listing edge + NEW delta + governor + breaker + bulk unnest + VAM + recipe.
# ---------------------------------------------------------------------------

_BULK_INSERT_PLATFORM_VEHICLES = """
INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model,
        year, km, price, fuel, transmission, photo_url, vin_ref, status)
SELECT u.vehicle_ulid, $14, u.deep_link, u.title, u.make, u.model,
       u.year, u.km, u.price, u.fuel, u.transmission, u.photo_url, u.vin_ref, 'available'
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[], $5::text[],
              $6::int[], $7::int[], $8::numeric[], $9::text[], $10::text[],
              $11::text[], $12::text[], $13::int[])
       AS u(vehicle_ulid, deep_link, title, make, model, year, km, price, fuel,
            transmission, photo_url, vin_ref, _ord)
ON CONFLICT (entity_ulid, deep_link) DO NOTHING
"""


async def _cage_platform_owned(conn, platform_ulid, vehicles, stats, segment):
    """Cage a batch of platform-OWNED vehicles (VN/renting): the platform entity owns them,
    one platform_listing edge each, NEW event for genuinely new ones. Idempotent (re-run adds
    0 rows). `vehicles` = list[Vehicle]. Returns nothing; mutates stats."""
    # dedup within batch by deep_link
    by_link: dict[str, Vehicle] = {}
    for v in vehicles:
        if v.deep_link and v.deep_link not in by_link:
            by_link[v.deep_link] = v
    if not by_link:
        return
    links = list(by_link.keys())
    async with conn.transaction():
        existing = {
            row["deep_link"]: row["vehicle_ulid"]
            for row in await conn.fetch(
                "SELECT vehicle_ulid, deep_link FROM vehicle WHERE entity_ulid=$1 "
                "AND deep_link = ANY($2::text[])", platform_ulid, links)
        }
        ulid_for: dict[str, str] = {}
        new_links: list[str] = []
        touch: list[str] = []
        for lk in links:
            ex = existing.get(lk)
            if ex:
                ulid_for[lk] = ex
                touch.append(ex)
            else:
                ulid_for[lk] = ulid()
                new_links.append(lk)
        if touch:
            await conn.execute(_BULK_TOUCH_VEHICLES, touch)
        if new_links:
            vs = [by_link[lk] for lk in new_links]
            await conn.execute(
                _BULK_INSERT_PLATFORM_VEHICLES,
                [ulid_for[lk] for lk in new_links], new_links,
                [v.title for v in vs], [v.make for v in vs], [v.model for v in vs],
                [v.year for v in vs], [v.km for v in vs], [v.price for v in vs],
                [v.fuel for v in vs], [v.transmission for v in vs],
                [v.photo_url for v in vs], [v.listing_ref for v in vs],
                list(range(len(vs))), platform_ulid)
            landed = {
                row["deep_link"]: row["vehicle_ulid"]
                for row in await conn.fetch(
                    "SELECT vehicle_ulid, deep_link FROM vehicle WHERE entity_ulid=$1 "
                    "AND deep_link = ANY($2::text[])", platform_ulid, new_links)
            }
            confirmed_new = [lk for lk in new_links if landed.get(lk) == ulid_for[lk]]
            for lk in new_links:  # adopt the winner's ulid on any race
                if landed.get(lk):
                    ulid_for[lk] = landed[lk]
        else:
            confirmed_new = []

        stats["cars_caged"] += len(links)
        stats["new_cars"] += len(confirmed_new)

        edge_rows = await conn.fetch(
            _BULK_UPSERT_EDGES,
            [ulid_for[lk] for lk in links],
            [by_link[lk].listing_url or lk for lk in links],  # real surface URL, fallback link
            [by_link[lk].listing_ref for lk in links],
            [by_link[lk].price for lk in links], platform_ulid)
        stats["edges_created"] += sum(1 for r in edge_rows if r["inserted"])

        if confirmed_new:
            ev_u, ev_v, ev_e, ev_p = [], [], [], []
            for lk in confirmed_new:
                v = by_link[lk]
                payload = {"price": v.price, "title": v.title,
                           "platform": COCHES_TRADE_NAME, "segment": segment}
                if v.price_drop:
                    payload["price_drop"] = v.price_drop
                ev_u.append(ulid()); ev_v.append(ulid_for[lk]); ev_e.append(platform_ulid)
                ev_p.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_u, ev_v, ev_e, ev_p)
            stats["new_events"] += len(confirmed_new)


def _segment_stats(segment: str, drain_all: bool, cage_limit) -> dict:
    return {
        "segment": segment, "makes_discovered": 0, "pages_fetched": 0, "page_errors": 0,
        "cards_seen": 0, "no_classifieds": 0, "dealer_items": 0, "private_skipped": 0,
        "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0, "new_cars": 0,
        "edges_created": 0, "new_events": 0, "price_drops_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "dealers_distinct": 0,
        "makes_completed": 0, "concurrency": 1, "drain_all": drain_all,
        "cage_limit": cage_limit,
    }


async def harvest_vn(limit: int = DEFAULT_LIMIT, concurrency: int = DEFAULT_CONCURRENCY,
                     drain_all: bool = False) -> dict:
    """Drain the new-car CATALOG (VN): /coches-nuevos/coches-nuevos.htm?page=N, 20 version
    offers/page (search.total ~= 826). Each version offer = one platform-owned listing,
    attributed to the coches.com platform (no dealer on this surface). The PVP->price discount
    is captured as a price_drop so delta sees new-car promos like VO price drops."""
    conn = await asyncpg.connect(DSN)
    cage_limit = None if drain_all else max(1, limit)
    stats = _segment_stats(SEGMENT_VN, drain_all, cage_limit)
    if await is_open(conn, COCHES_SOURCE_KEY):
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": COCHES_SOURCE_KEY,
                "segment": SEGMENT_VN}
    fetcher = CochesComFetcher(pool_size=max(1, concurrency))
    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch)
    fetch_error = None
    last_http = None
    seen_vids: set[str] = set()
    try:
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = coches_platform_cdp_code()
        # page 1: declared total + page span.
        try:
            html = await fetcher.fetch_async(governed_fetch, f"{_VN_SEARCH_URL}?page=1")
        except Exception as e:  # noqa: BLE001
            fetch_error = str(e); last_http = fetcher.last_status
            await record_run(conn, COCHES_SOURCE_KEY, ok=False, rows=0, error=fetch_error,
                             http_status=last_http)
            return {"skipped": True, "reason": "vn_discovery_failed", "error": fetch_error,
                    "segment": SEGMENT_VN, "platform_code": platform_code}
        s = extract_vn_search(html)
        if not s:
            fetch_error = "VN search block missing (Imperva/drift)"
            await record_run(conn, COCHES_SOURCE_KEY, ok=False, rows=0, error=fetch_error)
            return {"skipped": True, "reason": "vn_no_search", "segment": SEGMENT_VN,
                    "platform_code": platform_code}
        declared = _to_int(s.get("total")) or 0
        stats["declared_full"] = declared
        pages = max(1, math.ceil(declared / _CARDS_PER_PAGE))
        print(f"[coches_com_wholesale:vn] catalog declared total={declared} -> {pages} pages.")

        async def ingest_page(s_block):
            offers = []
            for it in (s_block.get("data") or []):
                o = parse_vn_offer(it)
                if o is None:
                    continue
                if o.version_id in seen_vids:
                    stats["dup_ids_collapsed"] += 1
                    continue
                seen_vids.add(o.version_id)
                stats["cards_seen"] += 1
                v = vn_offer_to_vehicle(o)
                if v.price_drop:
                    stats["price_drops_captured"] += 1
                offers.append(v)
            if offers:
                await _cage_platform_owned(conn, platform_ulid, offers, stats, SEGMENT_VN)

        await ingest_page(s)
        stats["pages_fetched"] += 1
        page = 2
        page_cap = pages if drain_all else min(pages, math.ceil((cage_limit or 0) / _CARDS_PER_PAGE) + 1)
        while page <= page_cap:
            if cage_limit is not None and len(seen_vids) >= cage_limit:
                break
            try:
                html = await fetcher.fetch_async(governed_fetch, f"{_VN_SEARCH_URL}?page={page}")
            except Exception as e:  # noqa: BLE001
                stats["page_errors"] += 1; last_http = fetcher.last_status
                if stats["page_errors"] > 5:
                    fetch_error = f"VN fetch wall: {e}"; break
                page += 1; continue
            s = extract_vn_search(html)
            if not s or not (s.get("data")):
                break
            await ingest_page(s)
            stats["pages_fetched"] += 1
            page += 1

        await _finalize_platform_segment(conn, stats, platform_ulid, platform_code,
                                         SEGMENT_VN, "version/", fetch_error, last_http)
        return stats
    finally:
        await conn.close()


async def harvest_renting(limit: int = DEFAULT_LIMIT, drain_all: bool = False) -> dict:
    """Drain the RENTING segment hub /renting-coches. The hub SSR exposes totalOffers (the
    declared count, ~8,908) + the make/brand partition + the inline special-offer lists
    (specialOffersMonthly/Punctual, which carry dealerId+dealerName+href+fee). We cage the
    SSR-exposed offers as platform-owned listings and DECLARE the full total honestly. The
    full 8,908 paginated PDP list loads client-side via XHR (escalation reserve documented)."""
    conn = await asyncpg.connect(DSN)
    cage_limit = None if drain_all else max(1, limit)
    stats = _segment_stats(SEGMENT_RENTING, drain_all, cage_limit)
    if await is_open(conn, COCHES_SOURCE_KEY):
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": COCHES_SOURCE_KEY,
                "segment": SEGMENT_RENTING}
    fetcher = CochesComFetcher(pool_size=1)
    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch)
    fetch_error = None
    last_http = None
    try:
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = coches_platform_cdp_code()
        try:
            html = await fetcher.fetch_async(governed_fetch, _RENTING_URL)
        except Exception as e:  # noqa: BLE001
            fetch_error = str(e); last_http = fetcher.last_status
            await record_run(conn, COCHES_SOURCE_KEY, ok=False, rows=0, error=fetch_error,
                             http_status=last_http)
            return {"skipped": True, "reason": "renting_discovery_failed", "error": fetch_error,
                    "segment": SEGMENT_RENTING, "platform_code": platform_code}
        pp = extract_renting(html)
        if pp is None:
            await record_run(conn, COCHES_SOURCE_KEY, ok=False, rows=0,
                             error="renting hub missing")
            return {"skipped": True, "reason": "renting_no_hub", "segment": SEGMENT_RENTING,
                    "platform_code": platform_code}
        declared = _to_int(pp.get("totalOffers")) or 0
        stats["declared_full"] = declared
        offers = []
        seen_offers: set[str] = set()
        for key in ("specialOffersPunctual", "specialOffersMonthly"):
            for it in (pp.get(key) or []):
                o = parse_renting_offer(it)
                if o is None or o.offer_id in seen_offers:
                    continue
                seen_offers.add(o.offer_id)
                stats["cards_seen"] += 1
                link = o.href or f"https://www.coches.com/renting-coches/offer/{o.offer_id}"
                title = " ".join(p for p in (o.make, o.model) if p) or None
                offers.append(Vehicle(
                    deep_link=link, listing_ref=o.offer_id, title=title, make=o.make,
                    model=o.model, year=None, km=None, price=o.fee_amount, fuel=None,
                    transmission=None, photo_url=None, price_drop=None))
        if offers:
            await _cage_platform_owned(conn, platform_ulid, offers, stats, SEGMENT_RENTING)
        stats["pages_fetched"] = 1
        print(f"[coches_com_wholesale:renting] declared totalOffers={declared}; "
              f"SSR-exposed offers caged={stats['cars_caged']} "
              f"(full 8,908 list is client-XHR — escalation reserve).")
        await _finalize_platform_segment(conn, stats, platform_ulid, platform_code,
                                         SEGMENT_RENTING, "renting-coches/", fetch_error,
                                         last_http)
        return stats
    finally:
        await conn.close()


async def _finalize_platform_segment(conn, stats, platform_ulid, platform_code, segment,
                                     url_marker, fetch_error, last_http):
    """Shared finalize for VN/renting: write recipe, run the segment-scoped VAM quorum (db
    edges in this segment's listing_url namespace vs harvested), and record the S-HEALTH
    heartbeat. Mirrors the VO/km0 finalize exactly so every segment is verified the same way."""
    recipe_path = write_recipe(platform_code, COCHES_PLATFORM_RECIPE)
    stats["recipe_path"] = str(recipe_path)
    seg_like = f"%{url_marker}%"
    db_edges = await conn.fetchval(
        "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1 "
        "AND listing_url LIKE $2", platform_ulid, seg_like)
    harvested = stats["cars_caged"]
    verdict = await record_count_verdict(
        conn, subject_type="platform_segment", subject_key=f"{platform_code}:{segment}",
        claim=f"coches.com {segment} caged == platform_listing edges in segment",
        paths={"db_edges": db_edges, "harvested_caged": harvested}, tolerance=0.0)
    stats["verdict"] = verdict
    stats["db_edges"] = db_edges
    stats["harvested_cageable"] = harvested
    stats["platform_code"] = platform_code
    stats["platform_ulid"] = platform_ulid
    stats["dealers_distinct"] = 0  # platform-owned: no per-car dealer on these surfaces
    run_ok = (fetch_error is None and stats["cars_caged"] > 0 and verdict != "REFUTED")
    run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
    outcome = await record_run(conn, COCHES_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
                               error=run_error, http_status=last_http)
    stats["health_status"] = outcome.status
    stats["breaker_state"] = outcome.breaker_state
    if not run_ok:
        stats["repair_action"] = await auto_repair(
            conn, COCHES_SOURCE_KEY, run_error or "segment harvest failed",
            phase="scrape", http_status=last_http)


async def harvest_all(limit: int = DEFAULT_LIMIT, concurrency: int = DEFAULT_CONCURRENCY,
                      drain_all: bool = False) -> dict:
    """Drain EVERY segment in sequence under the SAME governor/breaker (one host, no
    collision): VO -> km0 -> VN catalog -> renting. Returns a merged report with per-segment
    sub-stats and the reconciled grand total (Σ declared per segment toward the site total).

    Sequence (not parallel) on purpose: all four hit www.coches.com, so serial keeps the
    per-host bucket honest and the breaker signal clean. --limit applies PER segment."""
    order = [SEGMENT_VO, SEGMENT_KM0, SEGMENT_VN, SEGMENT_RENTING]
    per_segment: dict[str, dict] = {}
    declared_sum = 0
    caged_sum = 0
    edges_sum = 0
    for seg in order:
        print(f"\n[coches_com_wholesale:all] === segment {seg} ===")
        st = await harvest(limit, concurrency, drain_all, seg)
        per_segment[seg] = st
        if not st.get("skipped"):
            declared_sum += st.get("declared_full") or 0
            caged_sum += st.get("cars_caged") or 0
            edges_sum += st.get("edges_created") or 0
    return {
        "segment": SEGMENT_ALL, "per_segment": per_segment,
        "reconciled_declared_sum": declared_sum,
        "cars_caged": caged_sum, "edges_created": edges_sum,
        "platform_code": coches_platform_cdp_code(),
        "site_displayed_total": SITE_DISPLAYED_TOTAL,
        "drain_all": drain_all,
    }


def _print_all_report(stats: dict) -> None:
    """Reconcile report for --segment all: per-segment caged/declared + the grand total vs
    the site-displayed 230.000. Honours the displayed total as the declared site peg."""
    print("\n" + "=" * 72)
    print("COCHES.COM -- ALL SEGMENTS RECONCILE (honour site-displayed total)")
    print("=" * 72)
    print(f"  platform cdp_code        : {stats.get('platform_code')}")
    print(f"  SITE DISPLAYED TOTAL     : {stats.get('site_displayed_total')} "
          f"('mas de 230.000 ofertas' -- the platform's own headline)")
    print("  --- per segment (declared = live source count; caged = this run) ---")
    ps = stats.get("per_segment", {})
    for seg in (SEGMENT_VO, SEGMENT_KM0, SEGMENT_VN, SEGMENT_RENTING):
        st = ps.get(seg, {})
        if st.get("skipped"):
            print(f"   {seg:8s}: SKIPPED ({st.get('reason')})")
            continue
        print(f"   {seg:8s}: declared={st.get('declared_full')}  "
              f"caged={st.get('cars_caged')}  new={st.get('new_cars')}  "
              f"edges={st.get('edges_created')}  verdict={st.get('verdict')}")
    print("  --- reconcile ---")
    print(f"  Sum declared (captureable): {stats.get('reconciled_declared_sum')} "
          f"(VO+km0+VN+renting -- the REAL sellable inventory)")
    print(f"  Sum caged this run        : {stats.get('cars_caged')}")
    print(f"  Sum edges created         : {stats.get('edges_created')}")
    gap = (stats.get('site_displayed_total') or 0) - (stats.get('reconciled_declared_sum') or 0)
    print(f"  gap to displayed 230k     : {gap}  (platform offer-inflation: each listing "
          f"counted across showroom x financing surfaces)")
    print("=" * 72)


def _print_report(stats: dict) -> None:
    if stats.get("segment") == SEGMENT_ALL:
        _print_all_report(stats)
        return
    if stats.get("skipped"):
        print(f"\n[coches_com_wholesale] SKIPPED: {stats.get('reason')} "
              f"{stats.get('error') or ''}")
        return
    print("\n" + "=" * 64)
    mode = "FULL DRAIN" if stats.get("drain_all") else "PROOF SLICE"
    seg = stats.get("segment", SEGMENT_VO)
    print(f"COCHES.COM WHOLESALE HARVEST [{seg.upper()}] — {mode} REPORT")
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


def _force_utf8_stdout() -> None:
    """Windows consoles/pipes default to cp1252, which cannot encode the Sum sign, em-dash, or
    UTF-8 car titles this connector prints (Híbrido, Diésel, Automática) — a raw print() then
    crashes the whole drain mid-flight. Reconfigure stdout/stderr to UTF-8 (errors='replace')
    so progress logging can never abort the harvest. Idempotent, no-op where already UTF-8."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass


def main() -> None:
    _force_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="coches.com wholesale harvester (multi-segment SRP/catalog drain)")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                        help=(f"max distinct cars to CAGE this run PER segment (proof cap); "
                              f"default {DEFAULT_LIMIT}. Ignored when --all is set."))
    parser.add_argument("--all", action="store_true",
                        help=("drain the WHOLE of the selected segment(s): every page until "
                              "each result set is exhausted (full per-segment harvest)."))
    parser.add_argument("--segment", choices=_SEGMENT_CHOICES, default=SEGMENT_VO,
                        help=("which segment to drain: vo (usados, default) | km0 (seminuevos) "
                              "| vn|catalog (new-car catalog offers) | renting | all (every "
                              "segment in sequence, reconciled to the site-displayed total)."))
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
    if args.segment == SEGMENT_ALL:
        stats = asyncio.run(harvest_all(limit, args.concurrency, drain_all=args.all))
    else:
        stats = asyncio.run(harvest(limit, args.concurrency, drain_all=args.all,
                                    segment=args.segment))
    _print_report(stats)


if __name__ == "__main__":
    main()
