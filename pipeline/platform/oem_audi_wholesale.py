"""Audi Selection :plus (Audi ES certified-used) WHOLESALE harvester — an OEM-VO portal, end to end.

www.audi.es/es/buscador-de-stock-de-ocasion is the manufacturer certified-used portal for Audi
in Spain ("Audi Selection :plus"). Like renew (Renault Group), Das WeltAuto (VW Group) and
spoticar (Stellantis) it is NOT a car-specialist marketplace (coches.net/autoscout24/motor.es)
nor a generalist classifieds (wallapop): it is an OEM-VO PORTAL — a single brand-owner publishing
the certified-used inventory of its OWN official dealer network (concesionarios oficiales Audi).
It is a member of the 'oem_vo_portal' source_group, in the 'audi_vo' family.

Audi is part of the VW Group whose generic multi-brand certified-used portal (Das WeltAuto)
already lives in the cage under family 'vw_group'. THIS module is Audi's OWN dedicated single-brand
portal — the "Audi Selection :plus" buscador — a SEPARATE surface with its own dealer network and
its own data layer. It is the brand-specific OEM-VO portal, sibling-by-group to Das WeltAuto, not
a re-harvest of it (Das WeltAuto enumerates by province slug over an AEM HTML SSR surface; Audi
Selection :plus enumerates over a clean first-party JSON gateway, with the FULL Audi-brand ES used
network behind it).

The surface is a OneAudi/NEMO (AEM) SPA whose VTP (Vehicle Trading Platform) feature-app calls
Audi's GLOBAL Stock Car Search (SCS) JSON API at GET scs.audi.de/api/v2/search/filter/{market}/{lang}.
For Spain used cars the market is 'esuc' (ES Used Cars), language 'es'. The API is FULLY OPEN: even
plain python-urllib with NO TLS impersonation gets HTTP 200 — no WAF (no server/cf-ray header), no
proxy, no browser, no cookie warm-up. The ONLY gate is a PUBLIC STATIC `token` header (FJ54W6H)
embedded verbatim in the page's envConfig (without it the API answers 401). This is NOT a
credential — it is a public per-market API key. defense_tier=t0_open, website_waf=none, is_tier1=
FALSE. The response carries {totalCount:3798, vehicleBasic:[{...}]}: page via from/size (size up to
100 honored — we drain at size=96), FLAT (no relevance cap, no depth wall — from=0..3796 walks the
whole index cleanly; from>=totalCount returns HTTP 400, the clean boundary). Each vehicleBasic item
carries the car AND its selling Audi dealer via the embedded `dealer` object (id, name, city,
street, zipCode, geoLocation) — dealer attribution is per-car, NO PDP fetch needed. This is an OEM
certified-used portal: every car belongs to an official Audi dealer (concesionario oficial); there
are NO private sellers. Verified live 2026-06-13 (docs/architecture/tier1_recipes/oem_audi_datalayer.md).

This module mirrors pipeline.platform.spoticar_wholesale EXACTLY (the proven OEM-VO template: same
dual-membership model, same bulk cage, same governor/health/VAM wiring). It proves the OEM-VO group
flows through the ONE architecture, not a fork of it:

  audi (the OEM-VO portal)     -> entity, kind='oem_vo_portal' (+ platform_meta)  [THE PLATFORM]
  each SELLING DEALER          -> entity, kind='compraventa'   (geo-resolved via ZIP)
  each CAR                     -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the portal        -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the selling dealer); platform membership is plural (this edge). The same
physical car can carry BOTH an audi edge and a coches.net edge without ever changing its owning
dealer.

GEO anchor: Audi dealers carry a clean `dealer.zipCode` (5-digit; first 2 digits = INE province
code, e.g. 48940 -> 48 Bizkaia) — the SAME authoritative anchor Das WeltAuto uses. We resolve the
province from ZIP[:2] (range-checked 01..52), with the dealer's geoLocation lat/lon as a fallback
(ProvinceGeocoder nearest labeled point) when the ZIP is missing/out-of-range. The municipality is
best-effort from dealer.city. dealerId = dealer.id (the stable Audi dealer number, e.g. '05346').

Encoding trap: SCS serves some human-text fields as latin-1 mojibake over the wire ('Aut�nomos' =
"Autónomos", the '�' euro/currency glyph). Re-encode human-text fields: s.encode('latin-1').
decode('utf-8'). The numeric and code fields are clean.

Multi-axis classification (migrations/0016):
  defense_tier = 't0_open'         (fully open — plain urllib gets 200; only a public token header)
  source_group = 'oem_vo_portal'   (the group renew opened)
  role         = 'platform'
  kind         = 'oem_vo_portal'   (the platform entity's ontology kind, migrations/0005)
  is_tier1     = FALSE             (no WAF fronts the SCS gateway)
  family       = 'audi_vo'         (ties Audi's single-brand OEM-VO surface on the family axis)

PROOF SLICE OR FULL. audi declares 3,798 cars (totalCount). The set is small and FLAT, so the FULL
drain is in reach in a single run: with size=96 the whole index is ~40 requests. --pages/--limit
bound the run; --limit converts a target car count to a page count. The declared full count is
recorded for the VAM verdict's slice arithmetic.

Engine: a GET against scs.audi.de/api/v2/search/filter/esuc/es routed THROUGH the per-host governor
(the same single choke point coches.net/renew use). The synchronous curl_cffi GET runs in a worker
thread so the event loop is never blocked, and no host is fetched faster than its bucket
(scs.audi.de is registered in the JSON_API rate class — a first-party gateway built for the whole
brand user base, like renew).

Run: python -m pipeline.platform.oem_audi_wholesale --pages 40
"""
from __future__ import annotations

import argparse
import sys
import asyncio
import hashlib
import json
import math
import os
from dataclasses import dataclass

import asyncpg
from curl_cffi import requests as cffi_requests

from pipeline.engine.governor import governor, host_of
from pipeline.geo import GeoResolver
from pipeline.geocode import ProvinceGeocoder
from pipeline.ids import ulid
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict
from services.api.codes import _base32, cdp_code

DSN = "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
DSN = os.environ.get("CARDEEP_DSN", DSN)

# ---------------------------------------------------------------------------
# audi platform identity (OEM-VO portal, migrations/0005 + 0016).
# ---------------------------------------------------------------------------
AUDI_DOMAIN = "audi.es"
AUDI_WEBSITE = "audi.es"
AUDI_LEGAL_NAME = "Audi España (Audi Selection :plus)"
AUDI_TRADE_NAME = "audi"
AUDI_SOURCE_KEY = "oem_audi_wholesale"
AUDI_WAF = "none"                # SCS is unwalled (no server/cf-ray header; plain urllib gets 200).
AUDI_DEFENSE_TIER = "t0_open"    # fully open — only a public static `token` header gates the API.
AUDI_SOURCE_GROUP = "oem_vo_portal"
AUDI_ROLE = "platform"
AUDI_KIND = "oem_vo_portal"      # the platform ENTITY's ontology kind (NOT 'plataforma').
AUDI_FAMILY = "audi_vo"          # ties Audi's single-brand OEM-VO surface on the family axis.

# The working request (verified live 2026-06-13; recipe oem_audi_datalayer.md TL;DR). The SCS
# global gateway; market 'esuc' (ES Used Cars), language 'es'. The token is the page's public
# envConfig api key (scs.apiKey) carried as a `token` HEADER, NOT a query param.
_BASE = "https://scs.audi.de"
_MARKET = "esuc"
_LANG = "es"
LIST_PATH = f"/api/v2/search/filter/{_MARKET}/{_LANG}"   # the SCS first-party JSON search API.
ENDPOINT = _BASE + LIST_PATH
_TOKEN = "FJ54W6H"               # public static SCS api key (scs.apiKey in the page envConfig).
_SORT = "prices.retail:asc"      # the live buscador's default sort; stable for a flat full walk.
_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.audi.es/",
    "Origin": "https://www.audi.es",
    "token": _TOKEN,
}
_PDP_BASE = ""                   # vehicleBasic.weblink is already an absolute entry.audi.com URL.
_IMPERSONATE = "chrome131"
_TIMEOUT = 40
PAGE_SIZE = 96   # SCS honors size up to 100 (verified). 96/page drains the 3798-car index in ~40 reqs.

# Province sentinel '00' = national (same convention as renew/spoticar/dasweltauto). geo_province
# has NO '00', so the platform ENTITY stores province_code = NULL; '00' lives only inside the
# cdp_code string (free text, no FK). We never pollute geo_province with it.
PLATFORM_PROVINCE_SENTINEL = "00"

# Full-drain default. 3,798 cars / 96 per page = ~40 data pages (page index 39 from=3744 = 54
# trailing cars; from>=3798 returns HTTP 400). totalCount + the 400 boundary bound the run. A small
# slice (--pages 3) is a proof slice; --pages 40 is the full ES public stock.
DEFAULT_MAX_PAGES = 45  # ceil(3798/96)=40 + head-room; the HTTP-400 boundary stops the walk honestly.


def audi_platform_cdp_code() -> str:
    """The audi platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:audi.es'), province segment '00' (national). Mirrors
    spoticar_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{AUDI_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Field helpers (the SCS surface: nested {code,description} objects + some latin-1 mojibake).
# ---------------------------------------------------------------------------


def _fix(s):
    """Repair latin-1 mojibake on human-text fields ('Aut�nomos' -> Autónomos). The wire bytes
    were UTF-8 mis-decoded as latin-1 upstream; re-encode to recover. Numeric/code fields are clean
    and never passed here."""
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def _desc(obj):
    """A SCS attribute is a {code, description} object; return the human description (mojibake-
    repaired). Tolerates a bare string or None."""
    if isinstance(obj, dict):
        return _fix(obj.get("description"))
    return _fix(obj)


# Fuel/gearbox value repair. The accented Spanish DESCRIPTIONS (fuel.description,
# gearType.description) arrive with the accented byte already replaced by U+FFFD AT THE SOURCE
# (verified live 2026-06-13: the raw curl_cffi .json() value is already 'Di�sel' BEFORE any
# local decode — the wire JSON itself carries the replacement char, NOT a recoverable latin-1
# byte, so an encode('latin-1') round-trip cannot recover it). So instead of storing a lossy
# 'Di�sel', map the CLEAN accent-free companion CODE (fuel.code D/B/H/E; gearType.code
# gear-type.automatic/manual) to its proper Spanish label. This is the SAME source trap and the
# SAME fix spoticar_wholesale uses — a fixed, verified vocabulary, no invention, just the clean
# source signal preferred. Vocabulary enumerated over the FULL ES stock (4 fuel codes, 3 gearbox).
_FUEL_CODE_LABEL = {
    "D": "Diésel", "B": "Gasolina", "H": "Híbrido", "E": "Eléctrico",
    "G": "GLP", "C": "GNC", "W": "Hidrógeno",
}
_GEARTYPE_CODE_LABEL = {
    "gear-type.automatic": "Automático",
    "gear-type.manual": "Manual",
}


def _clean_fuel(fuel) -> str | None:
    """Prefer the clean accent-free fuel.code (D/B/H/E) mapped to its proper Spanish label; fall
    back to the (possibly U+FFFD-bearing) description only if the code is unknown — never store a
    lossy replacement char when a clean signal exists."""
    if isinstance(fuel, dict):
        code = fuel.get("code")
        if isinstance(code, str):
            mapped = _FUEL_CODE_LABEL.get(code.strip().upper())
            if mapped:
                return mapped
        return _desc(fuel)
    return _fix(fuel)


def _clean_transmission(gear_type) -> str | None:
    """Normalize the finite gearbox vocabulary (Manual / Automático). Prefer the clean gearType.code
    (gear-type.automatic/manual). When the code is 'gear-type.null' the description still carries a
    recoverable ASCII discriminator ('Cambio manual' vs 'Cambio autom�tico DSG') — key off the
    lossy description's clean ASCII letters (strip the U+FFFD and accents) so 'autom' -> Automático
    and 'manual' -> Manual without ever storing a replacement char."""
    if not isinstance(gear_type, dict):
        return _fix(gear_type)
    code = gear_type.get("code")
    if isinstance(code, str):
        mapped = _GEARTYPE_CODE_LABEL.get(code.strip().lower())
        if mapped:
            return mapped
    # gear-type.null (or an unknown code): derive from the lossy description's clean ASCII.
    desc = gear_type.get("description")
    if isinstance(desc, str):
        ascii_only = "".join(ch for ch in desc.lower() if ch.isascii() and ch.isalpha())
        if "autom" in ascii_only:
            return "Automático"
        if "manual" in ascii_only:
            return "Manual"
        return _fix(desc)
    return None


def _to_int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _to_float(v):
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _prov_from_postal(postal) -> str | None:
    """Spanish postal codes are 5 digits; the first 2 ARE the INE province code (28xxx=Madrid,
    48xxx=Bizkaia). Zero-pad-tolerant; range-check (01..52)."""
    if not postal:
        return None
    s = str(postal).strip()
    if len(s) < 2 or not s[:2].isdigit():
        return None
    p = s[:2]
    if not ("01" <= p <= "52"):
        return None
    return p


def _retail_price(typed_prices) -> float | None:
    """typedPrices is a list of {type, amount, currencyCode}. Prefer the 'retail' price (the actual
    selling price shown on the card); fall back to 'regular' only if retail is absent."""
    if not isinstance(typed_prices, list):
        return None
    by_type = {}
    for p in typed_prices:
        if isinstance(p, dict) and p.get("type"):
            by_type[p["type"]] = _to_float(p.get("amount"))
    return by_type.get("retail") or by_type.get("regular")


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL response — field names inspected live 2026-06-13, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class DealerRef:
    """The selling Audi dealer parsed from a single car's embedded `dealer` object.

    SCS attaches the full point-of-sale per car: dealer.id (stable Audi dealer number),
    dealer.name, dealer.city, dealer.zipCode, dealer.geoLocation {lat,lon}. The province is taken
    from ZIP[:2] (authoritative INE anchor) with the geoLocation as a fallback; the municipality is
    best-effort from the city literal. id is the stable per-dealer key for cross-source dedup and as
    the source_ref."""
    dealer_id: str
    name: str | None
    province_code: str | None
    city: str | None
    lat: float | None
    lng: float | None


@dataclass
class Vehicle:
    """A car parsed from a single SCS vehicleBasic item."""
    deep_link: str
    listing_ref: str           # audi stable car id (carId, e.g. ESP05346128322740) — the dedup key.
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    vin: str | None            # SCS does not expose a VIN on the listing surface -> always None.


def _first_image(source: dict) -> str | None:
    """Pick a hosted image URL. Prefer used.pictureUrls[0] (the dealer photos), else pictures[0].url,
    else None (a fallback-logo placeholder is NOT a real photo and is skipped)."""
    used = source.get("used") or {}
    pics = used.get("pictureUrls")
    if isinstance(pics, list):
        for u in pics:
            if isinstance(u, str) and u.startswith("http"):
                return u
    for p in source.get("pictures") or []:
        if isinstance(p, dict):
            u = p.get("url")
            if isinstance(u, str) and u.startswith("http") and p.get("type") != "fallback":
                return u
    return None


def parse_item_dealer(source: dict) -> DealerRef | None:
    """Parse the SELLING dealer from a car's embedded `dealer` object. Returns None when there is no
    stable dealer id — the car cannot be attributed to a concrete POS."""
    dealer = source.get("dealer") or {}
    dealer_id = dealer.get("id")
    if not dealer_id:
        return None
    geo = dealer.get("geoLocation") or {}
    return DealerRef(
        dealer_id=str(dealer_id),
        name=_fix(dealer.get("name")),
        province_code=_prov_from_postal(dealer.get("zipCode")),  # authoritative; geo is the fallback.
        city=_fix(dealer.get("city")),
        lat=_to_float(geo.get("lat")),
        lng=_to_float(geo.get("lon")),
    )


def parse_item_vehicle(source: dict) -> Vehicle:
    """Parse the car from a SCS vehicleBasic item (REAL field map, nested {code,description})."""
    price = _retail_price(source.get("typedPrices"))

    year = _to_int(source.get("modelYear"))
    if year is not None and not (1900 <= year <= 2100):
        year = None

    used = source.get("used") or {}
    km = _to_int(used.get("mileage"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    weblink = source.get("weblink") or ""
    deep_link = weblink if isinstance(weblink, str) else ""

    make = "Audi"   # single-brand portal: every car is an Audi (brand.code='aa').
    # symbolicCarline.description = "Audi A1 Sportback"; strip the leading make for a clean model.
    model = _desc(source.get("symbolicCarline")) or _desc(source.get("model"))
    if isinstance(model, str) and model.lower().startswith("audi "):
        model = model[5:]
    version = _desc(source.get("trimline"))
    title = " ".join(p for p in (make, model) if p) or None
    if version and isinstance(title, str) and version not in title:
        title = f"{title} {version}".strip()

    # carId is the stable per-car id AND the dedup key (e.g. ESP05346128322740). It is clean.
    carnum = source.get("carId") or source.get("decodedCarId") or source.get("id")
    listing_ref = str(carnum) if carnum else ""

    # fuel/transmission: the accented DESCRIPTIONS carry an unrecoverable U+FFFD at the source, so
    # prefer the clean accent-free CODE mapped to a proper Spanish label (mirrors spoticar).
    transmission = _clean_transmission(source.get("gearType"))  # gear-type.manual -> "Manual" (NOT gearBox=ratios).
    fuel = _clean_fuel(source.get("fuel"))                       # fuel.B -> "Gasolina".

    return Vehicle(
        deep_link=deep_link,
        listing_ref=listing_ref,
        title=title,
        make=make,
        model=model,
        year=year,
        km=km,
        price=price,
        fuel=fuel,
        transmission=transmission,
        photo_url=_first_image(source),
        vin=None,
    )


# ---------------------------------------------------------------------------
# Fetch: a GET routed THROUGH the governor (same per-host choke point as renew/spoticar).
# ---------------------------------------------------------------------------


class AudiFetcher:
    """A POOL of fingerprint-coherent curl_cffi GET sessions for the SCS search API.

    Same concurrency-vs-coherence model as SpoticarFetcher / RenewFetcher: a single curl_cffi
    Session is NOT safe to call from several threads at once, and the governor runs each fetch in
    its own worker thread (asyncio.to_thread). The fix is a bounded POOL — one Session per
    concurrency slot, each its own Chrome fingerprint + cookie jar. The governor's per-host bucket
    bounds the AGGREGATE rate across every session, so the pool widens parallelism WITHOUT
    out-pacing the host (the choke point is the bucket, never the session count).
    """

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch_page(self, url: str, *, page: int = 0, slot: int = 0) -> dict:
        """The synchronous GET on pool session `slot` (runs in a worker thread).

        Handed to governor().wrap_fetch_text: the governor derives the host from `url`, waits on
        the per-host bucket, then runs THIS off the event loop. `slot` rides as a kwarg the governor
        forwards untouched, so each in-flight request GETs on its own leased, never-shared curl_cffi
        session (thread-safe). `page` is the 0-based PAGE index — converted here to the from offset
        (from = page*PAGE_SIZE). Raises on a non-200 so the breaker sees throttling (never masks a
        challenge/empty body). NOTE: from>=totalCount yields HTTP 400 — the clean data boundary; the
        caller treats a 400 at/after the expected tail as the end of data, not a failure."""
        session = self._sessions[slot]
        params = {"from": page * PAGE_SIZE, "size": PAGE_SIZE, "sort": _SORT}
        resp = session.get(url, params=params, headers=_HEADERS,
                           impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url} (from {page * PAGE_SIZE})")
        return json.loads(resp.content.decode("utf-8", "replace"))

    async def fetch_page_async(self, governed_fetch, url: str, *, page: int) -> dict:
        """Lease a pool slot, fetch `page` THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, page=page, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer (mirrors spoticar_wholesale: ensure platform, bulk-upsert dealer/vehicle, link edge,
# emit delta, all idempotent ON CONFLICT). Multi-axis 0016 classification set.
# ---------------------------------------------------------------------------

AUDI_PLATFORM_RECIPE = {
    "version": 1,
    "source": "audi (Audi Selection :plus, www.audi.es/es/buscador-de-stock-de-ocasion)",
    "scope": "platform-wholesale (Audi ES certified-used; OneAudi/NEMO SPA + global SCS JSON API)",
    "engine": "curl_cffi+chrome131_impersonate+scs_json_api(GET)",
    "access": ("FULLY OPEN. scs.audi.de answers HTTP 200 to plain python-urllib (no TLS "
               "impersonation), no WAF (no server/cf-ray header), no proxy, no browser, no cookie "
               "warm-up, €0. The ONLY gate is a PUBLIC STATIC `token` header (FJ54W6H, the page's "
               "envConfig scs.apiKey) — without it the API returns 401. Not a credential. "
               "defense_tier=t0_open, website_waf=none, is_tier1=FALSE."),
    "data_surface": "internal_api",
    "surface_intent": "scs_stock_car_search_json_api",
    "endpoint": "GET https://scs.audi.de/api/v2/search/filter/esuc/es?from=N&size=96&sort=prices.retail:asc",
    "request": {
        "headers": "Accept application/json, token FJ54W6H (public SCS api key), Referer https://www.audi.es/, Origin https://www.audi.es",
        "params": "from=offset, size<=100 (we use 96), sort=prices.retail:asc",
        "market_lang": "market=esuc (ES Used Cars), language=es",
    },
    "enumeration": ("from=0,96,192,... (size=96; the last page is the trailing tail). totalCount "
                    "(3798) + the HTTP-400 returned once from>=totalCount bound the run. FLAT — no "
                    "relevance cap, no depth wall. Dedup on carId."),
    "denominator": "totalCount (3798) == SCS header echo == sum of carline-facet counts (groups.carline)",
    "platform_entity": ("kind=oem_vo_portal, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=FALSE, defense_tier=t0_open, source_group=oem_vo_portal, role=platform, "
                        "family=audi_vo"),
    "dual_membership": ("vehicle.entity_ulid=SELLING DEALER (compraventa); "
                        "platform_listing edge=platform<->vehicle"),
    "field_map": {
        "deep_link": "vehicleBasic.weblink (absolute entry.audi.com PDP URL)",
        "listing_ref": "vehicleBasic.carId (e.g. ESP05346128322740; stable id + dedup key)",
        "vin": "NOT exposed on the listing surface -> NULL",
        "make": "constant 'Audi' (brand.code='aa'; single-brand portal)",
        "model": "vehicleBasic.symbolicCarline.description (leading 'Audi ' stripped; fallback model.description)",
        "version": "vehicleBasic.trimline.description",
        "year": "vehicleBasic.modelYear",
        "km": "vehicleBasic.used.mileage",
        "price": "vehicleBasic.typedPrices[type=retail].amount (fallback type=regular); EUR",
        "fuel": "vehicleBasic.fuel.description",
        "transmission": "vehicleBasic.gearType.description (Manual/Automático; NOT gearBox which is gear ratios)",
        "dealer": "vehicleBasic.dealer {id (stable Audi dealer no.), name, city, street, zipCode, geoLocation}",
        "location": ("dealer.zipCode[:2] = INE province code (authoritative); dealer.geoLocation "
                     "lat/lon -> province via ProvinceGeocoder as fallback; dealer.city -> municipality"),
    },
    "caveats": {
        "page_size": "size honored up to 100; we use 96. from>=totalCount returns HTTP 400 (clean boundary).",
        "token": "the `token` header is REQUIRED (401 without it); it is a public static api key, not a secret.",
        "encoding": ("some human-text fields are latin-1 mojibake over the wire ('Aut�nomos'); repair "
                     "with s.encode('latin-1').decode('utf-8'). Numeric/code fields are clean."),
        "geo": "dealer.zipCode[:2] is authoritative; geoLocation lat/lon is the fallback anchor.",
        "no_private_sellers": "OEM certified-used portal — every car belongs to an official Audi dealer.",
        "vw_group_note": ("Audi is VW-Group, but THIS is Audi's OWN single-brand 'Selection :plus' "
                          "portal — a SEPARATE surface from the multi-brand Das WeltAuto (family vw_group)."),
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the audi platform entity + platform_meta exist. Returns the platform
    entity_ulid. kind='oem_vo_portal' (the platform ontology kind), is_tier1=FALSE (no WAF fronts
    the SCS gateway), multi-axis 0016 classification set explicitly, data_surface='internal_api'."""
    code = audi_platform_cdp_code()
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
        eulid, code, AUDI_KIND, AUDI_LEGAL_NAME, AUDI_TRADE_NAME, AUDI_WEBSITE,
        AUDI_WAF, AUDI_DEFENSE_TIER, AUDI_SOURCE_GROUP, AUDI_ROLE, AUDI_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, AUDI_SOURCE_KEY, AUDI_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'internal_api',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"endpoint": ENDPOINT, "host": host_of(ENDPOINT),
                           "method": "GET", "page_size": PAGE_SIZE,
                           "market": _MARKET, "language": _LANG,
                           "denominator": "totalCount",
                           "surface_intent": "scs_stock_car_search_json_api",
                           "engine": "curl_cffi/chrome131_impersonate"}),
        AUDI_FAMILY)
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    Audi dealers have no bare domain on this surface -> identity = name + location + the stable
    dealer.id (passed via `address` so two distinct POS that happen to share a name in one
    municipality never collapse to one entity)."""
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni, address=f"dealer:{d.dealer_id}")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# Default concurrency: pages fetched in parallel per sliding window. scs.audi.de IS in the
# governor's JSON_API rate class (a first-party gateway built for the whole brand user base, like
# renew). The concurrency only needs to keep that bucket saturated; a small window is plenty.
DEFAULT_CONCURRENCY = 4


@dataclass
class _CageRow:
    """One fully-parsed, geo-anchored car ready for the bulk cage — the in-memory result of the
    parse+resolve phase, before any SQL."""
    dealer_id: str
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


def _parse_window(items_by_page: list[tuple[int, list]], geo: GeoResolver,
                  geocoder: ProvinceGeocoder, seen_ids: set, harvested_cageable: set,
                  stats: dict) -> list[_CageRow]:
    """Parse + geo-resolve every car across the window IN PAGE ORDER — pure CPU, no SQL.

    The EXACT per-item gate (cross-page dedup on carId, dealer-parse skip, geo skip, cageable
    truth), lifted out of the DB loop so the SQL phase is purely set-based. The province is taken
    from the dealer's ZIP[:2] (authoritative) with the geoLocation lat/lon as a fallback.
    `seen_ids` / `harvested_cageable` / `stats` are mutated here with deterministic page-order
    semantics so the VAM truth is byte-identical regardless of batching."""
    rows: list[_CageRow] = []
    for _page, items in items_by_page:
        for source in items:
            stats["items_seen"] += 1
            # cross-page dedup on carId (the stable dedup key; a flat sorted walk can in principle
            # repeat a car across a window boundary if the index shifts mid-crawl).
            carnum = source.get("carId") or source.get("decodedCarId") or source.get("id")
            item_id = str(carnum) if carnum else ""
            if item_id and item_id in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue
            if item_id:
                seen_ids.add(item_id)

            d = parse_item_dealer(source)
            if d is None:
                stats["no_dealer_skipped"] += 1
                continue
            stats["dealer_items"] += 1

            # Geo gate — ZIP[:2] is authoritative; fall back to geocoding the lat/lon (nearest
            # labeled point) when the ZIP is missing/out-of-range. Then apply the same
            # province-range guard the dealer upsert enforces, done in memory so a bad/missing geo
            # is skipped without ever touching the DB (no FK risk).
            prov = d.province_code
            if not prov and d.lat is not None:
                prov = geocoder.nearest_province(d.lat, d.lng)
            if not prov or not (prov.isdigit() and "01" <= prov <= "52"):
                stats["geo_skipped"] += 1
                continue
            d = DealerRef(dealer_id=d.dealer_id, name=d.name, province_code=prov,
                          city=d.city, lat=d.lat, lng=d.lng)
            muni = geo.municipality_code(prov, d.city)
            dealer_cdp = cdp_code_dealer(d, muni)

            v = parse_item_vehicle(source)
            if not v.deep_link:
                stats["no_link_skipped"] += 1
                continue
            harvested_cageable.add((d.dealer_id, v.deep_link))
            if v.vin:
                stats["vins_captured"] += 1
            rows.append(_CageRow(
                dealer_id=d.dealer_id, dealer_cdp=dealer_cdp, dealer_name=d.name,
                dealer_province=prov, dealer_muni=muni, vehicle=v))
    return rows


async def _ingest_window(conn: asyncpg.Connection, geo: GeoResolver, geocoder: ProvinceGeocoder,
                         platform_ulid: str, items_by_page: list[tuple[int, list]], seen_ids: set,
                         harvested_cageable: set, stats: dict) -> None:
    """BULK-ingest a whole concurrent page-window in ONE transaction with set-based SQL.

    Mirrors spoticar_wholesale._ingest_window EXACTLY: ONE round-trip per table per window (unnest
    multi-row upserts). The delta/VAM/platform_listing semantics are preserved: same ON CONFLICT
    idempotency, same cageable truth, same NEW-event rule (emitted only for genuinely new
    vehicles). A re-run of an already-harvested window adds 0 rows and 0 events.
    """
    cage = _parse_window(items_by_page, geo, geocoder, seen_ids, harvested_cageable, stats)
    if not cage:
        return

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
        d_refs = [dealers[c].dealer_id for c in d_cdps]
        await conn.execute(_BULK_UPSERT_DEALERS, d_ulids, d_cdps, d_names, d_provs,
                           d_munis, d_refs, AUDI_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_DEALER_SOURCES, d_cdps, d_refs, AUDI_SOURCE_KEY)
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
                [x[3].photo_url for x in ins], [x[3].vin for x in ins])
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

        # ---- (5) NEW delta events — only for genuinely new vehicles.
        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                v = cars[k].vehicle
                payload = {"price": v.price, "title": v.title, "platform": AUDI_TRADE_NAME}
                if v.vin:
                    payload["vin"] = v.vin
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities,
                               ev_payloads)
            stats["new_events"] += len(confirmed_new)


async def harvest(max_pages: int = DEFAULT_MAX_PAGES,
                  concurrency: int = DEFAULT_CONCURRENCY,
                  limit: int | None = None) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    # --limit converts a target car count to a page count (PAGE_SIZE cars/page). The tighter of
    # --pages / --limit bounds the run.
    if limit is not None and limit > 0:
        limit_pages = max(1, math.ceil(limit / PAGE_SIZE))
        max_pages = min(max_pages, limit_pages)
    fetcher = AudiFetcher(pool_size=concurrency)
    stats = {
        "pages_fetched": 0, "items_seen": 0, "dealer_items": 0,
        "no_dealer_skipped": 0, "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "vins_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "dealers_distinct": 0,
        "concurrency": concurrency, "max_pages": max_pages, "private_skipped": 0,
        "no_link_skipped": 0,
    }
    # Harvest-side truth for the VAM: distinct CAGEABLE cars = distinct (dealer_id, deep_link)
    # pairs that survived dealer-parse + geo-resolution. Like-with-like vs db_edges.
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if audi's breaker is OPEN (a recent ban/throttle still cooling), skip the
    # drain gracefully — the API keeps serving the last snapshot.
    if await is_open(conn, AUDI_SOURCE_KEY):
        print(f"[oem_audi_wholesale] breaker OPEN for {AUDI_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, API still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": AUDI_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        geocoder = await ProvinceGeocoder.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = audi_platform_cdp_code()
        print(f"[oem_audi_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid}) "
              f"kind={AUDI_KIND} group={AUDI_SOURCE_GROUP} tier={AUDI_DEFENSE_TIER} "
              f"family={AUDI_FAMILY}")
        print(f"[oem_audi_wholesale] geocoder anchors: {geocoder.size()} labeled points (lat/lon -> province fallback).")
        print(f"[oem_audi_wholesale] governor paces host {host_of(ENDPOINT)} (per-host token bucket, JSON_API class).")
        print(f"[oem_audi_wholesale] CONCURRENT drain: window={concurrency} pages in flight. "
              f"Target = {max_pages} pages (size={PAGE_SIZE}; full ES stock = 3798).")

        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        # CONCURRENT sliding-window drain. Each window fetches up to `concurrency` PAGES (0-based)
        # in parallel through the governor (the host bucket paces the aggregate), then the pages are
        # INGESTED sequentially in page order through the single asyncpg connection. A page that
        # errors stops the drain honestly: an HTTP 400 at/after the expected tail is the data
        # boundary (from>=totalCount); any other error is a throttle the breaker must catch. An
        # empty page also stops the drain. totalCount bounds the run.
        stop = False
        next_page = 0
        while next_page < max_pages and not stop:
            window = list(range(next_page, min(next_page + concurrency, max_pages)))
            next_page = window[-1] + 1

            results = await asyncio.gather(
                *(fetcher.fetch_page_async(governed_fetch, ENDPOINT, page=p) for p in window),
                return_exceptions=True,
            )

            window_pages: list[tuple[int, list]] = []
            for page, data in zip(window, results):
                if isinstance(data, Exception):
                    last_http = fetcher.last_status
                    # HTTP 400 once from>=totalCount is the CLEAN boundary, not a failure: it means
                    # we asked past the end of a fully-drained index. Treat it as a normal stop.
                    expected_tail = (stats["declared_full"] is not None
                                     and page * PAGE_SIZE >= stats["declared_full"])
                    if last_http == 400 and expected_tail:
                        print(f"[oem_audi_wholesale] page {page} (from={page*PAGE_SIZE}) HTTP 400 past "
                              f"totalCount={stats['declared_full']}; data boundary reached.")
                    else:
                        fetch_error = str(data)
                        print(f"[oem_audi_wholesale] page {page} fetch failed ({data}); stopping drain honestly.")
                    stop = True
                    break
                if stats["declared_full"] is None:
                    stats["declared_full"] = _to_int(data.get("totalCount"))
                items = data.get("vehicleBasic") or []
                if not items:
                    print(f"[oem_audi_wholesale] page {page}: no items; stopping (data boundary reached).")
                    stop = True
                    break
                window_pages.append((page, items))

            if window_pages:
                await _ingest_window(conn, geo, geocoder, platform_ulid, window_pages, seen_ids,
                                     harvested_cageable, stats)
                stats["pages_fetched"] += len(window_pages)
                first_p, last_p = window_pages[0][0], window_pages[-1][0]
                print(f"[oem_audi_wholesale] window pages {first_p}-{last_p}: "
                      f"items={sum(len(it) for _, it in window_pages)} "
                      f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                      f"edges={stats['edges_created']} dealers_seen={len({d for d,_ in harvested_cageable})}")

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, AUDI_PLATFORM_RECIPE)
        print(f"[oem_audi_wholesale] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths that all measure
        # "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for audi      (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join  (DB read truth)
        #   harvested_cageable = distinct (dealer_id, deep_link) pulled (harvest truth)
        # The declared full count (3798) is reported for honesty but is NOT a quorum path.
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

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks audi, trips the
        # breaker on a ban, and auto-repairs. OK when >=1 page fetched, no fetch error stopped the
        # drain, and the VAM did not refute.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, AUDI_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, AUDI_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[oem_audi_wholesale] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("AUDI SELECTION :PLUS (OEM-VO PORTAL) WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  group / kind          : oem_vo_portal / oem_vo_portal (tier t0_open, family audi_vo)")
    print(f"  declared full (source): {stats.get('declared_full')}")
    print(f"  concurrency (window)  : {stats.get('concurrency')} pages in flight")
    print(f"  target pages          : {stats.get('max_pages')}")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  dealer items          : {stats['dealer_items']}")
    print(f"  no-dealer skipped     : {stats['no_dealer_skipped']}")
    print(f"  no-link skipped       : {stats['no_link_skipped']}")
    print(f"  private skipped       : {stats['private_skipped']} (OEM portal — none expected)")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page, carId dedup)")
    print(f"  geo skipped (bad geo) : {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for audi = {stats.get('db_edges')})")
    print(f"  VINs captured         : {stats['vins_captured']} (SCS listing has no VIN — expected 0)")
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
        description="audi Selection :plus OEM-VO portal wholesale harvester (concurrent SCS-JSON drain)")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"pages to harvest (size={PAGE_SIZE}); default {DEFAULT_MAX_PAGES} (full ES stock)")
    parser.add_argument("--limit", type=int, default=None,
                        help=("optional target car count; converted to a page count (size/page). "
                              "The tighter of --pages / --limit bounds the run."))
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"pages fetched in parallel per sliding window; default "
                              f"{DEFAULT_CONCURRENCY}. scs.audi.de is in the JSON_API rate class — "
                              f"the governor's per-host bucket is the real limiter."))
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.pages, args.concurrency, args.limit))
    _print_report(stats)


if __name__ == "__main__":
    main()
