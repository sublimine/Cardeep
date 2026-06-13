"""Das WeltAuto (VW Group certified-used) WHOLESALE harvester — an OEM-VO portal, end to end.

www.dasweltauto.es is the manufacturer certified-used portal for the Volkswagen Group in
Spain (Volkswagen + SEAT + Škoda + CUPRA + Audi second-hand stock its dealer network
certifies). Like es.renew.auto (Renault Group), it is NOT a car-specialist marketplace
(coches.net/autoscout24/motor.es) nor a generalist classifieds (wallapop): it is an
OEM-VO PORTAL — a single brand-owner publishing the certified-used inventory of its own
dealer network. That is the same source_group ('oem_vo_portal'), the same platform entity
kind ('oem_vo_portal'), and the OWNER's explicit demand: "los demás con su sistema" —
beyond the giant marketplaces, work the OEM certified-used portals too.

The surface is an AEM (Adobe Experience Manager, vw-dwa3 clientlib) site backed by
Motorflash's used-car feed (motorflash.com/filter image proxy, motorflash.min.js facet
widgets). Unlike renew's clean .data JSON loader, Das WeltAuto's official site is
SSR HTML — but each result card carries a FULLY-SPECCED JSON object embedded right in the
markup as two HTML attributes:
    data-configuration='{VehicleManufacturer, Model{Name,Year}, Vehicle{VehicleId,Milage,
                         RegistrationDate}, Engine{FuelType}, Gear{NumberType},
                         Budget{Price{price}}, Exterior{Color}, ...}'   -> THE CAR
    data-partner='{InformationBnr, InformationName, InformationCity, InformationZIP}'  -> THE DEALER
No browser, no proxy, no cookie warm-up — just a Chrome TLS fingerprint (curl_cffi) and a
GET. The www.dasweltauto.es origin returns 403 to a naïve fetch (WAF on the public host)
but serves cleanly to a chrome131 impersonation (defense_tier=t1_soft: a soft TLS/UA wall,
no JS challenge). Verified live 2026-06-12.

Enumeration is PER-PROVINCE, not one national paginator. The route
/esp/coches-de-segunda-mano-en-{provincia}?pagina=N is the real, deep paginator (Madrid
drains to 1,043 distinct cars over 47 pages); the bare national /coches-de-segunda-mano
route IGNORES ?pagina (always page 1). The last page CLAMP-REPEATS (a far ?pagina=999
returns the same tail as the true last page), so the stop signal is "a page adds zero NEW
VehicleIds", NOT "a page is empty" — exactly the cross-page dedup the bulk cage already does.

This module mirrors pipeline.platform.renew_wholesale EXACTLY (same dual-membership model,
same bulk cage, same governor/health/VAM wiring). It proves a SECOND OEM-VO portal flows
through the ONE architecture, not a fork of it:

  Das WeltAuto (the OEM-VO portal) -> entity, kind='oem_vo_portal' (+ platform_meta)  [THE PLATFORM]
  each SELLING DEALER (data-partner)-> entity, kind='compraventa'   (geo-resolved via ZIP)
  each CAR                          -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the portal             -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the selling dealer); platform membership is plural (this edge). The
same physical car can carry BOTH a Das WeltAuto edge and a coches.net edge without ever
changing its owning dealer.

Multi-axis classification (migrations/0016):
  defense_tier = 't1_soft'         (soft TLS/UA wall on the origin; no JS challenge to curl_cffi)
  source_group = 'oem_vo_portal'   (the same OEM-VO group renew opened)
  role         = 'platform'
  kind         = 'oem_vo_portal'   (the platform entity's ontology kind, migrations/0005)
  family       = 'vw_group'        (ties co-defended VW-Group OEM-VO sibling surfaces)

PROOF SLICE, NOT THE FULL NATIONAL HARVEST. The portal declares ~5k+ cars nationally
(>8,000 advertised on the marketing copy; the live per-province sum is the true denominator).
Here we cap at MAX_PROVINCES provinces x MAX_PAGES pages and log the cap honestly. The
declared per-province totals are recorded for the VAM verdict's slice arithmetic.

Engine: a GET against www.dasweltauto.es province routes routed THROUGH the per-host governor
(the same single choke point coches.net/renew/AS24 use). The synchronous curl_cffi GET runs
in a worker thread so the event loop is never blocked, and no host is fetched faster than its
bucket.

Run: python -m pipeline.platform.dasweltauto_wholesale --provinces 3 --pages 8
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import html as html_module
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

DSN = "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
DSN = os.environ.get("CARDEEP_DSN", DSN)

# ---------------------------------------------------------------------------
# Das WeltAuto platform identity (OEM-VO portal, migrations/0005 + 0016).
# ---------------------------------------------------------------------------
DWA_DOMAIN = "dasweltauto.es"
DWA_WEBSITE = "dasweltauto.es"
DWA_LEGAL_NAME = "Volkswagen Group España (Das WeltAuto)"
DWA_TRADE_NAME = "Das WeltAuto"
DWA_SOURCE_KEY = "dasweltauto_wholesale"
DWA_WAF = "other"                 # soft TLS/UA wall on the origin (403 to naïve, OK to chrome131).
DWA_DEFENSE_TIER = "t1_soft"      # soft wall, no JS challenge -> tier 1.
DWA_SOURCE_GROUP = "oem_vo_portal"
DWA_ROLE = "platform"
DWA_KIND = "oem_vo_portal"        # the platform ENTITY's ontology kind (NOT 'plataforma').
DWA_FAMILY = "vw_group"           # ties co-defended VW-Group OEM-VO sibling surfaces by family axis.

# The working request (verified live 2026-06-12).
_BASE = "https://www.dasweltauto.es"
# Per-province listing route; ?pagina=N is the deep paginator. {prov} = the site's province slug.
PROVINCE_PATH = "/esp/coches-de-segunda-mano-en-{prov}"
_PDP_BASE = "https://www.dasweltauto.es"  # data-url is a relative /esp/oferta/... PDP path.
_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.dasweltauto.es/esp/",
}
_IMPERSONATE = "chrome131"
_TIMEOUT = 40

# Province sentinel '00' = national (same convention as renew/coches.net/AS24). geo_province
# has NO '00', so the platform ENTITY stores province_code = NULL; '00' lives only inside the
# cdp_code string (free text, no FK). We never pollute geo_province with it.
PLATFORM_PROVINCE_SENTINEL = "00"

# PROOF SLICE caps. Per-province paginate until no NEW VehicleIds (the real stop), bounded by
# MAX_PAGES per province; iterate up to MAX_PROVINCES provinces. NOT the full national set.
DEFAULT_MAX_PAGES = 8
DEFAULT_MAX_PROVINCES = 3

# The site's province URL slugs (scraped live from the homepage's province links 2026-06-12).
# These are the ENUMERATION entry points only — the authoritative geo anchor for every car is
# its data-partner ZIP (zip[:2] = INE province code), so a car always attributes to the right
# province even if the slug it was found under differs. Ordered by likely stock density (the
# big metros first) so a capped proof slice covers the richest inventory.
PROVINCE_SLUGS = [
    "madrid", "barcelona", "valencia", "sevilla", "malaga", "zaragoza", "murcia",
    "alicante", "vizcaya", "coruna", "asturias", "pontevedra", "granada", "cadiz",
    "navarra", "valladolid", "guipuzcoa", "tarragona", "cordoba", "girona", "almeria",
    "illes_balears", "sta_c_tenerife", "toledo", "leon", "castellon", "badajoz",
    "huelva", "jaen", "burgos", "salamanca", "lleida", "albacete", "lugo", "ourense",
    "ciudad_real", "alava", "la_rioja", "cantabria", "guadalajara", "cuenca", "huesca",
    "segovia", "palencia", "avila", "teruel",
]

# Each result card embeds the car as data-configuration JSON and the dealer as data-partner JSON.
# Capture the PDP url + both JSON blobs in one shot. The attributes are single-quoted in the
# markup, so the JSON's own double quotes never collide with the attribute delimiter.
_CARD_RE = re.compile(
    r"data-url=\"(?P<url>/esp/oferta/[^\"]+)\"\s+"
    r"data-configuration='(?P<cfg>\{.*?\})'\s+"
    r"data-partner='(?P<partner>\{.*?\})'",
    re.S,
)
# transmission detection from Gear.NumberType free text (e.g. "6 Cambio manual", "DSG automático").
_AUTO_RE = re.compile(r"autom", re.I)
_MANUAL_RE = re.compile(r"manual", re.I)
# km from "21.380 km" -> 21380.
_KM_RE = re.compile(r"[\d.]+")


def dwa_platform_cdp_code() -> str:
    """The Das WeltAuto platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:dasweltauto.es'), province segment '00' (national). Mirrors
    renew_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{DWA_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL embedded card JSON — field names inspected live, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class DealerRef:
    """The selling dealer parsed from a single card's data-partner blob.

    Das WeltAuto attaches the dealer per card: InformationBnr (the stable VW-Group dealer
    number — the cross-source/source_ref key), InformationName, InformationCity,
    InformationZIP. The geo anchor is the ZIP (first 2 digits = INE province code) +
    InformationCity (resolves the municipality). Bnr is the stable per-dealer id."""
    bnr: str
    name: str | None
    province_code: str | None
    city: str | None
    postal_code: str | None


@dataclass
class Vehicle:
    """A car parsed from a single Das WeltAuto result card (data-configuration)."""
    deep_link: str
    listing_ref: str           # Das WeltAuto native VehicleId (Vehicle.VehicleId)
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    seal: str | None           # SealofQuality (e.g. "WeltAuto") — gold for OEM-cert delta.


def _to_int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _prov_from_postal(postal) -> str | None:
    """Spanish postal codes are 5 digits; the first 2 ARE the INE province code (28xxx=Madrid,
    08xxx=Barcelona, 15xxx=A Coruña). Zero-pad and range-check (01..52)."""
    if not postal:
        return None
    s = str(postal).strip()
    if len(s) < 2 or not s[:2].isdigit():
        return None
    p = s[:2]
    if not ("01" <= p <= "52"):
        return None
    return p


def _km_from_text(milage) -> int | None:
    """Vehicle.Milage is free text like '21.380 km'. Strip to digits, range-guard."""
    if not milage or not isinstance(milage, str):
        return None
    m = _KM_RE.search(milage)
    if not m:
        return None
    km = _to_int(m.group(0).replace(".", "").replace(" ", ""))
    if km is None or km < 0 or km > 5_000_000:
        return None
    return km


def _year_from_card(cfg: dict) -> int | None:
    """Model.Year (preferred) or Production.Year, range-guarded."""
    for path in (("Model", "Year"), ("Production", "Year")):
        node = cfg
        for k in path:
            node = (node or {}).get(k) if isinstance(node, dict) else None
        y = _to_int(node)
        if y is not None and 1900 <= y <= 2100:
            return y
    return None


def _transmission_from_gear(gear: dict) -> str | None:
    """Gear.NumberType is free text ('6 Cambio manual', 'DSG automático'). Map to a clean label."""
    txt = (gear or {}).get("NumberType") if isinstance(gear, dict) else None
    if not txt:
        return None
    if _AUTO_RE.search(txt):
        return "Automático"
    if _MANUAL_RE.search(txt):
        return "Manual"
    return txt.strip() or None


def parse_card_dealer(partner: dict) -> DealerRef | None:
    """Parse the SELLING dealer from a card's data-partner blob. Requires the stable Bnr;
    cards without one (rare) are skipped (no stable identity to anchor)."""
    if not isinstance(partner, dict):
        return None
    bnr = partner.get("InformationBnr")
    if not bnr:
        return None
    postal = partner.get("InformationZIP")
    prov = _prov_from_postal(postal)
    return DealerRef(
        bnr=str(bnr),
        name=(partner.get("InformationName") or "").strip() or None,
        province_code=prov,
        city=(partner.get("InformationCity") or "").strip() or None,
        postal_code=str(postal) if postal else None,
    )


def parse_card_vehicle(url: str, cfg: dict) -> Vehicle:
    """Parse the car from a Das WeltAuto result card's data-configuration (REAL field map)."""
    veh = cfg.get("Vehicle") or {}
    model = cfg.get("Model") or {}
    engine = cfg.get("Engine") or {}
    budget = cfg.get("Budget") or {}

    price = None
    price_node = (budget.get("Price") or {}) if isinstance(budget, dict) else {}
    amount = price_node.get("price")
    try:
        price = float(amount) if amount not in (None, "") else None
    except (TypeError, ValueError):
        price = None

    make = cfg.get("VehicleManufacturer")
    model_name = model.get("Name")
    title = model_name or " ".join(p for p in (make, (cfg.get("Carline") or {}).get("Name")) if p) or None

    fuel = ((engine.get("FuelType") or {}).get("Main") or None) if isinstance(engine, dict) else None
    if isinstance(fuel, str):
        fuel = fuel.strip() or None

    deep_link = (_PDP_BASE + url) if url.startswith("/") else url

    return Vehicle(
        deep_link=deep_link,
        listing_ref=str(veh.get("VehicleId") or ""),
        title=title,
        make=make,
        model=model_name,
        year=_year_from_card(cfg),
        km=_km_from_text(veh.get("Milage")),
        price=price,
        fuel=fuel,
        transmission=_transmission_from_gear(cfg.get("Gear")),
        photo_url=None,  # filled by the page-level image map (image lives outside the card attrs).
        seal=cfg.get("SealofQuality") or None,
    )


def parse_cards(html_text: str) -> list[tuple[str, dict, dict]]:
    """Extract every (pdp_url, car_cfg, dealer_partner) from a province listing page's HTML.

    The card JSON is embedded in single-quoted HTML attributes; HTML-unescape first so any
    &amp;/&quot; in the markup become literal before json.loads. A card whose JSON fails to
    parse is skipped (defensive — never let one malformed card abort the whole page)."""
    out: list[tuple[str, dict, dict]] = []
    for m in _CARD_RE.finditer(html_text):
        url = m.group("url")
        try:
            cfg = json.loads(html_module.unescape(m.group("cfg")))
            partner = json.loads(html_module.unescape(m.group("partner")))
        except (json.JSONDecodeError, ValueError):
            continue
        out.append((url, cfg, partner))
    return out


def _photo_map(html_text: str) -> dict[str, str]:
    """Map VehicleId -> first hosted image URL by scanning the page once.

    The image lives OUTSIDE the data-* attributes (inside the card's <img>/CSS), proxied via
    images.motorflash.com/filter?path=<...>. We anchor each image to its card by the shared
    VehicleId that appears in the PDP path of the surrounding anchor. This is a best-effort
    enrichment: a car with no resolvable image simply carries photo_url=None (never blocks)."""
    photos: dict[str, str] = {}
    # Each card block is roughly: data-url="/esp/oferta/<slug>/<VehicleId>" ... <img ... filter?path=...>
    for m in re.finditer(
            r"data-url=\"/esp/oferta/[^\"]+?/(?P<vid>\d+)\".{0,4000}?"
            r"(?P<img>https://images\.motorflash\.com/filter\?path=[^\"'\\ )]+)",
            html_text, re.S):
        vid = m.group("vid")
        if vid not in photos:
            photos[vid] = html_module.unescape(m.group("img"))
    return photos


# ---------------------------------------------------------------------------
# Fetch: a GET routed THROUGH the governor (same per-host choke point as renew/coches.net).
# ---------------------------------------------------------------------------


class DwaFetcher:
    """A POOL of fingerprint-coherent curl_cffi GET sessions for the Das WeltAuto province routes.

    Same concurrency-vs-coherence model as RenewFetcher: a single curl_cffi Session is NOT safe
    to call from several threads at once, and the governor runs each fetch in its own worker
    thread (asyncio.to_thread). The fix is a bounded POOL — one Session per concurrency slot,
    each its own Chrome fingerprint + cookie jar. The governor's per-host bucket bounds the
    AGGREGATE rate across every session, so the pool widens parallelism WITHOUT out-pacing the
    host (the choke point is the bucket, never the session count)."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch_page(self, url: str, *, page: int = 1, slot: int = 0) -> str:
        """The synchronous GET on pool session `slot` (runs in a worker thread).

        Handed to governor().wrap_fetch_text: the governor derives the host from `url`, waits on
        the per-host bucket, then runs THIS off the event loop. `slot` rides as a kwarg the
        governor forwards untouched, so each in-flight request GETs on its own leased,
        never-shared curl_cffi session (thread-safe). Returns the decoded HTML. Raises on a
        non-200 so the breaker sees a throttle/wall (never masks a 403 challenge or empty body).

        `?pagina=N` is the deep paginator; page 1 omits it (the bare route IS page 1)."""
        params = {} if page <= 1 else {"pagina": page}
        session = self._sessions[slot]
        resp = session.get(url, params=params, headers=_HEADERS,
                           impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url} (page {page})")
        # The card JSON uses \\uXXXX escapes for accents, so the bytes are valid UTF-8; decode
        # explicitly so the few raw accented bytes (if any) and the escapes both survive.
        return resp.content.decode("utf-8", errors="replace")

    async def fetch_page_async(self, governed_fetch, url: str, *, page: int) -> str:
        """Lease a pool slot, fetch `page` THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, page=page, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer (mirrors renew_wholesale: ensure platform, bulk-upsert dealer/vehicle, link edge,
# emit delta, all idempotent ON CONFLICT). Multi-axis 0016 classification set.
# ---------------------------------------------------------------------------

DWA_PLATFORM_RECIPE = {
    "version": 1,
    "source": "Das WeltAuto (www.dasweltauto.es)",
    "scope": "platform-wholesale (AEM/Motorflash SSR HTML, per-province paginated listing)",
    "engine": "curl_cffi+chrome131_impersonate+ssr_html_embedded_card_json(GET)",
    "access": ("OPEN to a Chrome TLS fingerprint (no proxy, no browser, no cookie warm-up). The "
               "www.dasweltauto.es origin returns 403 to a naïve fetch (soft TLS/UA wall) but "
               "serves cleanly to chrome131 impersonation -> defense_tier=t1_soft, no JS challenge."),
    "data_surface": "next_data",   # SSR-embedded structured card JSON (closest valid enum; intent below).
    "surface_intent": "ssr_html_embedded_card_json",
    "endpoint": "GET https://www.dasweltauto.es/esp/coches-de-segunda-mano-en-{provincia}?pagina=N",
    "request": {
        "headers": "Accept text/html, Accept-Language es-ES, Referer /esp/",
        "enumeration_entry": "per-province slug routes (homepage province links); ZIP[:2] is the authoritative geo anchor",
    },
    "enumeration": ("PER-PROVINCE: /esp/coches-de-segunda-mano-en-{provincia}?pagina=1..N (23 cards/page). "
                    "The bare national /coches-de-segunda-mano route IGNORES ?pagina. The last page "
                    "CLAMP-REPEATS, so the stop signal is 'a page adds 0 NEW VehicleIds', not 'empty page'. "
                    "Madrid drains to 1,043 distinct cars over 47 pages (verified live)."),
    "card_path": ("each result card embeds data-configuration='{...car...}' + data-partner='{...dealer...}' "
                  "as single-quoted HTML attributes; \\uXXXX-escaped accents -> valid UTF-8 JSON."),
    "platform_entity": ("kind=oem_vo_portal, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=FALSE, defense_tier=t1_soft, source_group=oem_vo_portal, role=platform, "
                        "family=vw_group"),
    "dual_membership": ("vehicle.entity_ulid=SELLING DEALER (compraventa); "
                        "platform_listing edge=platform<->vehicle"),
    "field_map": {
        "deep_link": "https://www.dasweltauto.es{data-url} (data-url=/esp/oferta/{slug}/{VehicleId})",
        "listing_ref": "Vehicle.VehicleId (Das WeltAuto native ad id)",
        "make": "VehicleManufacturer",
        "model": "Model.Name",
        "year": "Model.Year (fallback Production.Year)",
        "km": "Vehicle.Milage ('21.380 km' -> 21380)",
        "price": "Budget.Price.price (EUR)",
        "fuel": "Engine.FuelType.Main (Gasolina/Diésel/Eléctrico/...)",
        "transmission": "Gear.NumberType (free text -> Manual/Automático)",
        "photo_url": "images.motorflash.com/filter?path=<dasweltauto hosted jpg> (page-level, anchored by VehicleId)",
        "seal": "SealofQuality (e.g. 'WeltAuto' — OEM certification mark)",
        "dealer": "data-partner {InformationBnr(stable VW dealer no.), InformationName, InformationCity, InformationZIP}",
        "location": "InformationZIP[:2] = INE province code; InformationCity -> municipality (INE-resolved)",
    },
    "caveats": {
        "page_size": "23 cards/page (route-controlled, not a request param).",
        "last_page_clamp": "?pagina beyond the last page repeats the last page's tail — dedup by VehicleId to stop.",
        "national_route_no_paging": "/esp/coches-de-segunda-mano ignores ?pagina; province routes are the deep paginator.",
        "geo_anchor": "the per-card data-partner ZIP is authoritative — a car attributes by ITS zip, not the slug it was found under.",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the Das WeltAuto platform entity + platform_meta exist. Returns the
    platform entity_ulid. kind='oem_vo_portal' (the platform ontology kind), is_tier1=FALSE
    (soft wall, no hard WAF), multi-axis 0016 classification set explicitly, data_surface
    ='next_data' (SSR-embedded structured card JSON; the precise intent rides in surface_detail)."""
    code = dwa_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               defense_tier, source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,$3,$4,$5,NULL,$6,$7::waf_kind,FALSE,'active','platform_label',
               $8::defense_tier,$9::source_group,$10::entity_role,$11, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, website_waf = EXCLUDED.website_waf,
               defense_tier = EXCLUDED.defense_tier, source_group = EXCLUDED.source_group,
               role = EXCLUDED.role, legal_name = EXCLUDED.legal_name, kind = EXCLUDED.kind""",
        eulid, code, DWA_KIND, DWA_LEGAL_NAME, DWA_TRADE_NAME, DWA_WEBSITE, DWA_WAF,
        DWA_DEFENSE_TIER, DWA_SOURCE_GROUP, DWA_ROLE, DWA_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, DWA_SOURCE_KEY, DWA_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'next_data',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"endpoint": _BASE + PROVINCE_PATH, "host": host_of(_BASE),
                           "method": "GET", "page_size": 23,
                           "enumeration": "per_province_pagina",
                           "card_attrs": ["data-configuration", "data-partner"],
                           "surface_intent": "ssr_html_embedded_card_json",
                           "engine": "curl_cffi/chrome131_impersonate"}),
        DWA_FAMILY)
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    Dealer identity is per-physical-installation, not per-vehicle.  Das WeltAuto emits the
    InformationBnr in at least two formats for the same physical dealership depending on the
    certified brand (VW/SEAT/SKODA/CUPRA/Audi): a 'C'-prefixed variant (e.g. C311K) and a
    '0'-prefixed variant (e.g. 0311K), and occasionally a third pure-numeric format.  Using
    ``address=f"bnr:{d.bnr}"`` as a discriminant caused each Bnr variant to hash to a
    distinct cdp_code, fragmenting one physical dealer into 2-3 CARDEEP entities.

    The stable, per-installation key is name + municipality_code (derived from InformationZIP
    and InformationCity, which ARE stable for a given physical location).  The Bnr is
    preserved as source_ref in entity_source for cross-source traceability without polluting
    the identity hash.

    Two distinct dealers that share both name and municipality are extremely rare in practice;
    if they ever collide the entity_cluster reconciliation step will surface the conflict via
    separate source_refs (Bnrs) attached to the same entity."""
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni, address=None)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# Default concurrency: pages fetched in parallel per sliding window WITHIN a province. The
# governor's per-host bucket is the real limiter, so this only needs to be wide enough to keep
# the bucket saturated. Modest (the origin is a soft-walled HTML host, not a JSON gateway).
DEFAULT_CONCURRENCY = 4


@dataclass
class _CageRow:
    """One fully-parsed, geo-anchored car ready for the bulk cage — the in-memory result of the
    parse+resolve phase, before any SQL. Carries everything the batched upserts need so the DB
    phase touches no per-item Python logic, only set-based statements."""
    bnr: str
    dealer_cdp: str
    dealer_name: str | None
    dealer_province: str
    dealer_muni: str | None
    vehicle: Vehicle


# The bulk statements — ONE round-trip per table per window (unnest-based multi-row upsert),
# byte-for-byte the same idempotency the row-by-row path uses. A re-run of an already-harvested
# window adds 0 rows and 0 events. Dealers carry the 0016 axes (oem_vo_portal/standalone_pos).

_BULK_UPSERT_DEALERS = """
INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
        province_code, municipality_code, is_tier1, status, kind_source,
        sells_cars, source_group, role, first_discovered_source, last_seen)
SELECT u.entity_ulid, u.cdp_code, 'compraventa', u.name, u.name,
       u.province_code, u.municipality_code, FALSE, 'active', 'platform_label',
       TRUE, 'oem_vo_portal'::source_group, 'standalone_pos'::entity_role, $7, now()
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


def _parse_window(pages: list[tuple[int, str]], geo: GeoResolver, seen_ids: set,
                  harvested_cageable: set, stats: dict) -> tuple[list[_CageRow], int]:
    """Parse + geo-resolve every card across the window IN PAGE ORDER — pure CPU, no SQL.

    Returns (cage_rows, new_ids_this_window). The new-id count is the PER-PROVINCE stop signal:
    when a province window adds zero new VehicleIds, that province is drained (the last page
    clamp-repeats). `seen_ids`/`harvested_cageable`/`stats` are mutated with deterministic
    page-order semantics so the VAM truth is batching-invariant."""
    rows: list[_CageRow] = []
    new_ids = 0
    for _page, html_text in pages:
        cards = parse_cards(html_text)
        photos = _photo_map(html_text)
        for url, cfg, partner in cards:
            stats["items_seen"] += 1
            veh = cfg.get("Vehicle") or {}
            item_id = str(veh.get("VehicleId") or "")
            if item_id and item_id in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue  # cross-page / cross-province dedup (last-page clamp + multi-prov dealers)
            if item_id:
                seen_ids.add(item_id)
                new_ids += 1

            d = parse_card_dealer(partner)
            if d is None:
                stats["no_dealer_skipped"] += 1
                continue
            stats["dealer_items"] += 1

            # Geo gate — same province-range guard the dealer upsert applies, in memory so a bad
            # province is skipped without ever touching the DB (no FK risk).
            if not d.province_code:
                stats["geo_skipped"] += 1
                continue
            if not (d.province_code.isdigit() and "01" <= d.province_code <= "52"):
                stats["geo_skipped"] += 1
                continue
            muni = geo.municipality_code(d.province_code, d.city)
            dealer_cdp = cdp_code_dealer(d, muni)

            v = parse_card_vehicle(url, cfg)
            if not v.deep_link:
                continue
            if item_id and item_id in photos:
                v.photo_url = photos[item_id]
            harvested_cageable.add((d.bnr, v.deep_link))
            if v.seal:
                stats["seals_captured"] += 1
            rows.append(_CageRow(
                bnr=d.bnr, dealer_cdp=dealer_cdp, dealer_name=d.name,
                dealer_province=d.province_code, dealer_muni=muni, vehicle=v))
    return rows, new_ids


async def _ingest_window(conn: asyncpg.Connection, geo: GeoResolver, platform_ulid: str,
                         pages: list[tuple[int, str]], seen_ids: set,
                         harvested_cageable: set, stats: dict) -> int:
    """BULK-ingest a whole concurrent page-window in ONE transaction with set-based SQL.

    Mirrors renew_wholesale._ingest_window EXACTLY: ONE round-trip per table per window (unnest
    multi-row upserts). The delta/VAM/platform_listing semantics are preserved: same ON CONFLICT
    idempotency, same cageable truth, same NEW-event rule (emitted only for genuinely new
    vehicles). A re-run of an already-harvested window adds 0 rows and 0 events. Returns the
    number of NEW VehicleIds seen this window — the per-province drain stop signal."""
    cage, new_ids = _parse_window(pages, geo, seen_ids, harvested_cageable, stats)
    if not cage:
        return new_ids

    async with conn.transaction():
        # ---- (2) DEALERS: dedup by cdp_code within the window, bulk-upsert, resolve ulids.
        dealers: dict[str, _CageRow] = {}
        for r in cage:
            dealers.setdefault(r.dealer_cdp, r)  # first occurrence wins (deterministic)
        d_ulids = [ulid() for _ in dealers]
        d_cdps = list(dealers.keys())
        d_names = [dealers[c].dealer_name for c in d_cdps]
        d_provs = [dealers[c].dealer_province for c in d_cdps]
        d_munis = [dealers[c].dealer_muni for c in d_cdps]
        d_refs = [dealers[c].bnr for c in d_cdps]
        await conn.execute(_BULK_UPSERT_DEALERS, d_ulids, d_cdps, d_names, d_provs,
                           d_munis, d_refs, DWA_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_DEALER_SOURCES, d_cdps, d_refs, DWA_SOURCE_KEY)
        cdp_to_ulid: dict[str, str] = {
            row["cdp_code"]: row["entity_ulid"]
            for row in await conn.fetch(
                "SELECT cdp_code, entity_ulid FROM entity "
                "WHERE cdp_code = ANY($1::text[])", d_cdps)
        }

        # ---- attach resolved dealer_ulid to each cage row; dedup cars within the window by
        # (dealer_ulid, deep_link) so the same ad seen twice in one window is one car.
        cars: dict[tuple[str, str], _CageRow] = {}
        for r in cage:
            du = cdp_to_ulid.get(r.dealer_cdp)
            if du is None:
                continue
            key = (du, r.vehicle.deep_link)
            if key not in cars:
                cars[key] = r

        # ---- (3) VEHICLES: one SELECT splits existing vs new. Existing -> bulk touch.
        # New -> Python-minted ulid + bulk insert.
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

        # ---- (4) EDGES: one batched upsert; RETURNING (xmax=0) counts genuinely new edges.
        e_vehicles = [vehicle_ulid_for[k] for k in car_keys]
        e_urls = [cars[k].vehicle.deep_link for k in car_keys]
        e_refs = [cars[k].vehicle.listing_ref for k in car_keys]
        e_prices = [cars[k].vehicle.price for k in car_keys]
        edge_rows = await conn.fetch(_BULK_UPSERT_EDGES, e_vehicles, e_urls, e_refs,
                                     e_prices, platform_ulid)
        stats["edges_created"] += sum(1 for row in edge_rows if row["inserted"])

        # ---- (5) NEW delta events — only for genuinely new vehicles. SealofQuality preserved.
        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                v = cars[k].vehicle
                payload = {"price": v.price, "title": v.title, "platform": DWA_TRADE_NAME}
                if v.seal:
                    payload["seal"] = v.seal
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities,
                               ev_payloads)
            stats["new_events"] += len(confirmed_new)
    return new_ids


async def _drain_province(conn: asyncpg.Connection, geo: GeoResolver, platform_ulid: str,
                          fetcher: DwaFetcher, governed_fetch, slug: str, max_pages: int,
                          concurrency: int, seen_ids: set, harvested_cageable: set,
                          stats: dict) -> tuple[str | None, int | None]:
    """Drain ONE province by sliding-window pagination until a window adds 0 NEW VehicleIds.

    Returns (fetch_error, last_http). Each window fetches up to `concurrency` pages in parallel
    through the governor (the host bucket paces the aggregate), then BULK-ingests the window in
    page order. The province STOPS when a window yields zero new ids (the last page clamp-repeats)
    or a page errors (the breaker must catch a throttle/wall). The bare page-1 route is the entry."""
    url = _BASE + PROVINCE_PATH.format(prov=slug)
    fetch_error: str | None = None
    last_http: int | None = None
    next_page = 1
    while next_page <= max_pages:
        window = list(range(next_page, min(next_page + concurrency, max_pages + 1)))
        next_page = window[-1] + 1
        results = await asyncio.gather(
            *(fetcher.fetch_page_async(governed_fetch, url, page=p) for p in window),
            return_exceptions=True,
        )
        window_pages: list[tuple[int, str]] = []
        stop = False
        for page, data in zip(window, results):
            if isinstance(data, Exception):
                fetch_error = str(data)
                last_http = fetcher.last_status
                print(f"[dasweltauto_wholesale] {slug} page {page} fetch failed ({data}); stopping province.")
                stop = True
                break
            window_pages.append((page, data))
        new_ids = 0
        if window_pages:
            new_ids = await _ingest_window(conn, geo, platform_ulid, window_pages, seen_ids,
                                           harvested_cageable, stats)
            stats["pages_fetched"] += len(window_pages)
            first_p, last_p = window_pages[0][0], window_pages[-1][0]
            print(f"[dasweltauto_wholesale] {slug} pages {first_p}-{last_p}: new_ids={new_ids} "
                  f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                  f"edges={stats['edges_created']}")
        if stop:
            break
        if new_ids == 0:
            # The window added no new VehicleIds -> this province is fully drained (last page
            # clamp-repeats). Stop cleanly (NOT an error — this is the expected terminus).
            break
    return fetch_error, last_http


async def harvest(max_provinces: int = DEFAULT_MAX_PROVINCES,
                  max_pages: int = DEFAULT_MAX_PAGES,
                  concurrency: int = DEFAULT_CONCURRENCY,
                  provinces: list[str] | None = None) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    fetcher = DwaFetcher(pool_size=concurrency)
    target_slugs = (provinces or PROVINCE_SLUGS)[:max(1, max_provinces)]
    stats = {
        "pages_fetched": 0, "items_seen": 0, "dealer_items": 0,
        "no_dealer_skipped": 0, "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "seals_captured": 0,
        "dup_ids_collapsed": 0, "dealers_distinct": 0, "concurrency": concurrency,
        "provinces_drained": 0, "provinces_target": target_slugs,
    }
    # Harvest-side truth for the VAM: distinct CAGEABLE cars = distinct (bnr, deep_link) pairs
    # that survived dealer-parse + geo-resolution. Like-with-like vs db_edges.
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if the breaker is OPEN (a recent ban/throttle still cooling), skip the drain
    # gracefully — the API keeps serving the last snapshot.
    if await is_open(conn, DWA_SOURCE_KEY):
        print(f"[dasweltauto_wholesale] breaker OPEN for {DWA_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, API still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": DWA_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = dwa_platform_cdp_code()
        print(f"[dasweltauto_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid}) "
              f"kind={DWA_KIND} group={DWA_SOURCE_GROUP} tier={DWA_DEFENSE_TIER}")
        print(f"[dasweltauto_wholesale] governor paces host {host_of(_BASE)} (per-host token bucket).")
        print(f"[dasweltauto_wholesale] PER-PROVINCE drain: {len(target_slugs)} province(s) "
              f"{target_slugs}, window={concurrency} pages, <= {max_pages} pages/province.")

        # seen_ids is GLOBAL across provinces: the same VW dealer can list a car under several
        # province routes (rare), and the last-page clamp repeats ids — global dedup keeps the
        # cageable truth honest and stops a province when it stops adding genuinely new cars.
        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        for slug in target_slugs:
            ferr, lhttp = await _drain_province(
                conn, geo, platform_ulid, fetcher, governed_fetch, slug, max_pages,
                concurrency, seen_ids, harvested_cageable, stats)
            stats["provinces_drained"] += 1
            if ferr is not None:
                # A fetch error on one province stops the whole drain honestly (the breaker must
                # catch a throttle/wall before it spreads across every province route).
                fetch_error, last_http = ferr, lhttp
                break

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, DWA_PLATFORM_RECIPE)
        print(f"[dasweltauto_wholesale] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths that all measure
        # "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for Das WeltAuto (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join     (DB read truth)
        #   harvested_cageable = distinct (bnr, deep_link) pulled         (harvest truth)
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

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks Das WeltAuto, trips
        # the breaker on a ban, and auto-repairs. OK when >=1 page fetched, no fetch error stopped
        # the drain, and the VAM did not refute.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, DWA_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, DWA_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[dasweltauto_wholesale] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("DAS WELTAUTO (OEM-VO PORTAL) WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  group / kind          : oem_vo_portal / oem_vo_portal (tier t1_soft, family vw_group)")
    print(f"  provinces drained     : {stats.get('provinces_drained')} of {len(stats.get('provinces_target', []))} targeted")
    print(f"  concurrency (window)  : {stats.get('concurrency')} pages in flight")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  dealer items          : {stats['dealer_items']}")
    print(f"  no-dealer skipped     : {stats['no_dealer_skipped']}")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page/province clamp)")
    print(f"  geo skipped (bad prov): {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for Das WeltAuto = {stats.get('db_edges')})")
    print(f"  OEM seals captured    : {stats['seals_captured']}")
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
    """Windows consoles/pipes default to cp1252, which cannot encode the Σ sign, arrows,
    em-dashes, or the accented car titles this connector prints (Híbrido, Diésel,
    Automática) — a raw print() then crashes the whole drain mid-flight. Reconfigure
    stdout/stderr to UTF-8 (errors='replace') so progress logging can never abort the
    harvest. Idempotent, no-op where already UTF-8."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass


def main() -> None:
    _force_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="Das WeltAuto OEM-VO portal wholesale harvester (per-province SSR-card drain)")
    parser.add_argument("--provinces", type=int, default=DEFAULT_MAX_PROVINCES,
                        help=f"number of province slugs to drain (in stock-density order); default {DEFAULT_MAX_PROVINCES}")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"max pages per province (23 cards/page); default {DEFAULT_MAX_PAGES}")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"pages fetched in parallel per sliding window; default {DEFAULT_CONCURRENCY}. "
                              f"The governor's per-host bucket is the real limiter."))
    parser.add_argument("--slug", action="append", default=None,
                        help="explicit province slug(s) to drain (repeatable); overrides the default order")
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.provinces, args.pages, args.concurrency, args.slug))
    _print_report(stats)


if __name__ == "__main__":
    main()
