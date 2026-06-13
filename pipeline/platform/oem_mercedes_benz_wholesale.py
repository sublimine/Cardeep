"""mercedes_benz (Mercedes-Benz Certified ES certified-used) WHOLESALE harvester — an OEM-VO portal, end to end.

ocasion.mercedes-benz.es is the manufacturer certified-used portal for Mercedes-Benz in Spain
("Vehículos de ocasión Mercedes-Benz Certified"). Like renew (Renault Group), Das WeltAuto
(VW group), spoticar (Stellantis) and toyota_lexus, it is NOT a car-specialist marketplace
(coches.net/autoscout24/motor.es) nor a generalist classifieds (wallapop): it is an OEM-VO
PORTAL — a single brand-owner publishing the certified-used inventory of its own official-dealer
(concesionario oficial) network. It joins the 'oem_vo_portal' source_group, in the
'mercedes_benz_vo' family.

The surface is a server-rendered listing whose pagination is an internal AJAX endpoint:
POST https://ocasion.mercedes-benz.es/ajxvl with FormData {type:'vehiclelist', q, page:N, area:1}.
The endpoint returns JSON {success, data:{count, page, onlyOnePage}, html:<rendered cards>}: 12
cars per page of fully self-contained card markup, FLAT (no relevance cap, no depth wall). Walk
page=1..401 (page 401 = 4 trailing cars; 400*12+4 = 4804 == data.count) to enumerate the full ES
public stock. Each card carries the car AND its selling Mercedes-Benz dealer (concesionario
oficial): name + "<postalCode> <city>" + the stable dealerCode (the prefix of the
"<dealerCode>-<carCode>" vehicle identifier) — dealer attribution is embedded per-card, NO PDP
fetch needed. This is an OEM certified-used portal: every car belongs to a Mercedes-Benz dealer;
there are NO private sellers. Verified live 2026-06-13 (docs/architecture/tier1_recipes/
oem_mercedes_benz_datalayer.md).

WAF posture: t0_open. Plain urllib (no fingerprint) AND plain curl_cffi (no impersonate) both get
HTTP 200 — there is NO bot-blocking WAF and NO JS challenge. We still drive it with curl_cffi
impersonate='chrome131' for engine-coherence with the rest of the fleet, but the surface is
genuinely open. €0, no proxy, no browser, no auth. The ajxvl POST sets a UCSSID session cookie, so
each pool session warms the listing page once for cookie coherence.

This module mirrors pipeline.platform.spoticar_wholesale EXACTLY (the proven OEM-VO template: same
dual-membership model, same bulk cage, same governor/health/VAM wiring), differing only where the
surface differs (HTML-card parse instead of a JSON _source; postal-code geo like renew instead of
spoticar's lat/lng; POST /ajxvl pagination instead of a GET paginate API). It proves the OEM-VO
group flows through the ONE architecture, not a fork of it:

  mercedes_benz (the OEM-VO portal) -> entity, kind='oem_vo_portal' (+ platform_meta)  [THE PLATFORM]
  each SELLING DEALER               -> entity, kind='compraventa'   (postal-resolved)
  each CAR                          -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the portal             -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the selling dealer); platform membership is plural (this edge). The same
physical car can carry BOTH a mercedes_benz edge and a coches.net edge without ever changing its
owning dealer.

GEO anchor: the dealer line is "<postalCode> <city>" (e.g. "46470 Massanassa"). The province is
the postalCode's first 2 digits (INE), the authoritative anchor (better than spoticar, which had
no postal code) — same path as renew/toyota_lexus. The municipality is INE-resolved from the city
literal, best-effort.

Encoding: the ajxvl JSON body is UTF-8 with a leading BOM — decode with 'utf-8-sig'. The card text
is then CLEAN UTF-8 (accents render correctly: Coupé, Híbrido, A Coruña; 0 U+FFFD). There is NO
latin-1 mojibake on this surface, so (unlike spoticar) no per-field re-encode is needed — only
HTML-entity unescape (&nbsp;, &ntilde;, ...).

Multi-axis classification (migrations/0016):
  defense_tier = 't0_open'          (no WAF; serves HTTP 200 to plain urllib — genuinely open)
  source_group = 'oem_vo_portal'    (the OEM-VO group)
  role         = 'platform'
  kind         = 'oem_vo_portal'    (the platform entity's ontology kind, migrations/0005)
  is_tier1     = FALSE              (no WAF fronts the public site)
  family       = 'mercedes_benz_vo' (ties the Mercedes-Benz OEM-VO surface on the family axis)

PROOF SLICE OR FULL. mercedes_benz declares 4,804 cars (data.count). The set is FLAT, so the FULL
drain is in reach in a single run: --pages 401 walks the whole index. --pages/--limit bound the
run; --limit converts a target car count to a page count. The declared full count is recorded for
the VAM verdict's slice arithmetic.

Engine: a POST against ocasion.mercedes-benz.es/ajxvl routed THROUGH the per-host governor (the
same single choke point coches.net/renew/spoticar use). The synchronous curl_cffi POST runs in a
worker thread so the event loop is never blocked, and no host is fetched faster than its bucket
(ocasion.mercedes-benz.es inherits the conservative STEALTH class).

Run: python -m pipeline.platform.oem_mercedes_benz_wholesale --pages 401
"""
from __future__ import annotations

import argparse
import sys
import asyncio
import hashlib
import html as htmlmod
import json
import math
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

DSN = "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
DSN = os.environ.get("CARDEEP_DSN", DSN)

# ---------------------------------------------------------------------------
# mercedes_benz platform identity (OEM-VO portal, migrations/0005 + 0016).
# ---------------------------------------------------------------------------
MB_DOMAIN = "ocasion.mercedes-benz.es"
MB_WEBSITE = "ocasion.mercedes-benz.es"
MB_LEGAL_NAME = "Mercedes-Benz España (Mercedes-Benz Certified)"
MB_TRADE_NAME = "mercedes_benz"
MB_SOURCE_KEY = "mercedes_benz_wholesale"
MB_WAF = "none"                 # plain urllib AND plain curl_cffi both get HTTP 200 -> no WAF.
MB_DEFENSE_TIER = "t0_open"     # genuinely open; no JS challenge -> tier 0.
MB_SOURCE_GROUP = "oem_vo_portal"
MB_ROLE = "platform"
MB_KIND = "oem_vo_portal"       # the platform ENTITY's ontology kind (NOT 'plataforma').
MB_FAMILY = "mercedes_benz_vo"  # ties the Mercedes-Benz OEM-VO surface on the family axis.
MB_IS_TIER1 = False             # no WAF fronts the public site.

# The working request (verified live 2026-06-13; recipe oem_mercedes_benz_datalayer.md TL;DR).
_BASE = "https://ocasion.mercedes-benz.es"
LIST_PATH = "/ajxvl"            # the internal AJAX list endpoint (POST FormData -> JSON+html).
ENDPOINT = _BASE + LIST_PATH
_LISTING_PAGE = _BASE + "/vehicles?referrer=vehiclesearch&language=es-ES"  # for cookie warm-up.
_PDP_BASE = _BASE + "/"         # card hrefs are relative ("vehicle?...").
_Q = "referrer=vehiclesearch&language=es-ES"  # the 'q' the SPA always sends (es-ES, no filter).
_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "X-Requested-With": "XMLHttpRequest",
    "Accept-Language": "es-ES,es;q=0.9",
    "Origin": _BASE,
    "Referer": _LISTING_PAGE,
}
_IMPERSONATE = "chrome131"
_TIMEOUT = 40
PAGE_SIZE = 12  # the endpoint serves a FIXED 12 cars/page (not overridable — recipe verified).

# Full-drain default. 4,804 cars / 12 per page = ~401 data pages (page 401 = 4 trailing cars;
# 402+ = 0). data.count (4804) + emptiness bound the run. A small slice (--pages 5) is a proof
# slice; --pages 401 is the full ES public stock.
DEFAULT_MAX_PAGES = 401


def mercedes_benz_platform_cdp_code() -> str:
    """The mercedes_benz platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:ocasion.mercedes-benz.es'), province segment '00' (national). Mirrors
    spoticar_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{MB_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# Province sentinel '00' = national (same convention as renew/spoticar/coches.net). geo_province
# has NO '00', so the platform ENTITY stores province_code = NULL; '00' lives only inside the
# cdp_code string (free text, no FK). We never pollute geo_province with it.
PLATFORM_PROVINCE_SENTINEL = "00"


# ---------------------------------------------------------------------------
# Field helpers (the mercedes_benz surface: rendered HTML cards, clean UTF-8 + HTML entities).
# ---------------------------------------------------------------------------


def _unescape(s):
    """Resolve HTML entities (&nbsp; -> space, &ntilde; -> ñ, &euro; -> €) and collapse the
    non-breaking spaces the markup uses between number and unit. The card text is CLEAN UTF-8 (no
    latin-1 mojibake on this surface), so this is the ONLY text repair needed — no re-encode."""
    if not isinstance(s, str):
        return s
    return htmlmod.unescape(s.replace("&nbsp;", " ")).strip()


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


def _num(s):
    """Parse a Spanish-formatted integer from a label ('84.574 km' -> 84574, '49.900' -> 49900,
    '143 kW (194 CV)' -> 143). Strips the thousands dot and takes the FIRST run of digits."""
    if not isinstance(s, str):
        return None
    m = re.search(r"\d[\d.]*", s)
    if not m:
        return None
    return _to_int(m.group(0).replace(".", ""))


def _prov_from_postal(postal) -> str | None:
    """Spanish postal codes are 5 digits; the first 2 ARE the INE province code (28xxx=Madrid,
    46xxx=Valencia, 08xxx=Barcelona, 15xxx=A Coruña). Zero-pad and range-check (01..52). Same path
    as renew/toyota_lexus — the authoritative anchor on this surface."""
    if not postal:
        return None
    s = str(postal).strip()
    if len(s) < 2 or not s[:2].isdigit():
        return None
    p = s[:2]
    if not ("01" <= p <= "52"):
        return None
    return p


def _year_from_reg(reg) -> int | None:
    """The registration label is 'dd.mm.yyyy' (e.g. '27.11.2022'). Take the trailing year and
    range-check (1900..2100)."""
    if not isinstance(reg, str):
        return None
    m = re.search(r"(\d{4})\s*$", reg.strip())
    if not m:
        return None
    y = _to_int(m.group(1))
    return y if y is not None and 1900 <= y <= 2100 else None


# Fuel-label normalization. The card fuel cell is a clean Spanish label, but the certified-used
# stock uses compound labels for the electrified variants ('Híbrido enchufable - Gasolina',
# 'Híbrido enchufable - Diésel'). Keep the source label verbatim (it is clean + meaningful); this
# map is only a defensive canonicalizer for the finite vocabulary, never an inventor of values.
_FUEL_CANON = {
    "diesel": "Diésel", "diésel": "Diésel", "gasolina": "Gasolina",
    "eléctrico": "Eléctrico", "electrico": "Eléctrico",
}


def _clean_fuel(label) -> str | None:
    """Canonicalize the single-word fuel labels (Diesel -> Diésel); pass compound electrified
    labels through verbatim (they are already clean and information-bearing)."""
    if not isinstance(label, str) or not label.strip():
        return None
    key = label.strip().lower()
    return _FUEL_CANON.get(key, label.strip())


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL rendered card — field positions inspected live 2026-06-13).
# ---------------------------------------------------------------------------


@dataclass
class DealerRef:
    """The selling Mercedes-Benz dealer parsed from a single car's card.

    mercedes_benz embeds the point-of-sale per card: the dealer NAME + a "<postalCode> <city>"
    line, plus a dealerCode (the prefix of the "<dealerCode>-<carCode>" vehicle identifier).
    Unlike spoticar (no postal code) the province comes from the postalCode (INE first-2), and
    the municipality is best-effort from the city literal.

    NOTE: dealer_id (the dealerCode prefix) is NOT a stable per-installation key on this
    surface — it varies nearly per-car in practice.  It is retained as source_ref for
    lineage only.  The actual identity discriminant is name + postal_code + municipality
    (see cdp_code_dealer)."""
    dealer_id: str
    name: str | None
    province_code: str | None
    city: str | None
    postal_code: str | None


@dataclass
class Vehicle:
    """A car parsed from a single mercedes_benz listing card."""
    deep_link: str
    listing_ref: str           # the "<dealerCode>-<carCode>" identifier — stable id + dedup key.
    vehicle_id: str            # data-vehicle (the per-car numeric id; secondary dedup key).
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    vin: str | None            # NOT exposed on the list card (None here; PDP-only, not fetched).


def _split_cards(page_html: str) -> list[str]:
    """Split the ajxvl 'html' payload into per-car card fragments. Each card opens with
    <div id="resultListItemNNNN" — split on that boundary, keep only the card fragments."""
    parts = re.split(r'(?=<div id="resultListItem\d+")', page_html)
    return [p for p in parts if p.startswith('<div id="resultListItem')]


def parse_card_dealer(card: str) -> DealerRef | None:
    """Parse the SELLING dealer from a card's location item + the dealerCode prefix of the vehicle
    identifier. Returns None when there is no dealerCode (cannot attribute to a concrete POS)."""
    # dealerCode = the prefix of "<dealerCode>-<carCode>" in the identifier subheadline.
    ident = re.search(r"Identificador del veh[^&]*&nbsp;([\d-]+)", card)
    if not ident or "-" not in ident.group(1):
        return None
    dealer_code = ident.group(1).split("-", 1)[0].strip()
    if not dealer_code:
        return None
    # The location item: name span then "<postalCode> <city>" span.
    loc = re.search(
        r"result-box-location-item.*?<span>([^<]+)</span>.*?<span>([^<]+)</span>",
        card, re.S)
    name = _unescape(loc.group(1)) if loc else None
    postal = None
    city = None
    if loc:
        loc_line = _unescape(loc.group(2))  # e.g. "46470 Massanassa"
        m = re.match(r"\s*(\d{5})\s+(.*)$", loc_line)
        if m:
            postal, city = m.group(1), m.group(2).strip()
        else:
            city = loc_line or None
    return DealerRef(
        dealer_id=dealer_code,
        name=name,
        province_code=None,             # filled by _prov_from_postal in _parse_window.
        city=city,
        postal_code=postal,
    )


def parse_card_vehicle(card: str) -> Vehicle:
    """Parse the car from a mercedes_benz listing card (REAL field positions, HTML-entity clean)."""
    vid_m = re.search(r"resultListItem(\d+)", card)
    vehicle_id = vid_m.group(1) if vid_m else ""

    ident_m = re.search(r"Identificador del veh[^&]*&nbsp;([\d-]+)", card)
    listing_ref = ident_m.group(1).strip() if ident_m else vehicle_id

    # deep_link: the relative "vehicle?...&vehicle=<vid>&referrer=vehicles" href.
    pdp_m = re.search(r'href="(vehicle\?[^"]+)"', card)
    rel = pdp_m.group(1) if pdp_m else ""
    deep_link = (_PDP_BASE + rel) if rel else ""

    make_m = re.search(r'class="manufacturer">\s*([^<]+?)\s*</span>', card)
    make = _unescape(make_m.group(1)) if make_m else None
    model_m = re.search(r"</span><br>\s*([^<]+?)\s*</div>", card)
    model = _unescape(model_m.group(1)) if model_m else None
    title = " ".join(p for p in (make, model) if p) or None

    price_m = re.search(r"vehicle_price_headline[^>]*>\s*([\d.]+)", card)
    price = _to_float(_num(price_m.group(1))) if price_m else None

    # The 5 spec rows in FIXED order: body, registration date, power, km, fuel.
    attrs = re.findall(r"vc-vehicle-attribute-text[^>]*>([^<]{1,60})<", card)
    attrs = [_unescape(a) for a in attrs]
    reg = attrs[1] if len(attrs) > 1 else None
    km = _num(attrs[3]) if len(attrs) > 3 else None
    fuel = _clean_fuel(attrs[4]) if len(attrs) > 4 else None
    if km is not None and (km < 0 or km > 5_000_000):
        km = None
    year = _year_from_reg(reg)

    img_m = re.search(r'v-i-g-main-image[^>]*data-src="([^"]+)"', card)
    photo_url = img_m.group(1) if img_m else None

    return Vehicle(
        deep_link=deep_link,
        listing_ref=listing_ref,
        vehicle_id=vehicle_id,
        title=title,
        make=make,
        model=model,
        year=year,
        km=km,
        price=price,
        fuel=fuel,
        transmission=None,   # the list card carries no gearbox cell (PDP-only; not fetched).
        photo_url=photo_url,
        vin=None,            # VIN is not on the list card (PDP-only); never invented.
    )


# ---------------------------------------------------------------------------
# Fetch: a POST routed THROUGH the governor (same per-host choke point as renew/spoticar).
# ---------------------------------------------------------------------------


class MercedesBenzFetcher:
    """A POOL of fingerprint-coherent curl_cffi POST sessions for the ajxvl list endpoint.

    Same concurrency-vs-coherence model as SpoticarFetcher / RenewFetcher: a single curl_cffi
    Session is NOT safe to call from several threads at once, and the governor runs each fetch in
    its own worker thread (asyncio.to_thread). The fix is a bounded POOL — one Session per
    concurrency slot, each its own Chrome fingerprint + cookie jar (warmed once against the listing
    page so the UCSSID session cookie is present). The governor's per-host bucket bounds the
    AGGREGATE rate across every session, so the pool widens parallelism WITHOUT out-pacing the host.
    """

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._warmed = [False] * self._pool_size
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch_page(self, url: str, *, page: int = 1, slot: int = 0) -> dict:
        """The synchronous POST on pool session `slot` (runs in a worker thread).

        Handed to governor().wrap_fetch_text: the governor derives the host from `url`, waits on
        the per-host bucket, then runs THIS off the event loop. `slot` rides as a kwarg the
        governor forwards untouched, so each in-flight request POSTs on its own leased, never-shared
        curl_cffi session (thread-safe). Warms the listing page once per session for the UCSSID
        cookie. The ajxvl body is UTF-8 WITH A BOM — decode with 'utf-8-sig'. Raises on a non-200
        so the breaker sees throttling (never masks a challenge/empty body)."""
        session = self._sessions[slot]
        if not self._warmed[slot]:
            try:
                session.get(_LISTING_PAGE, headers={"Accept-Language": "es-ES,es;q=0.9"},
                            impersonate=_IMPERSONATE, timeout=_TIMEOUT)
            except Exception:
                pass  # warm-up is best-effort; the endpoint serves cold too (t0_open).
            self._warmed[slot] = True
        data = {"type": "vehiclelist", "q": _Q, "page": str(page), "area": "1"}
        resp = session.post(url, data=data, headers=_HEADERS,
                            impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url} (page {page})")
        # The body is UTF-8 with a leading BOM; 'utf-8-sig' strips it. Card text is then clean.
        return json.loads(resp.content.decode("utf-8-sig", "replace"))

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

MB_PLATFORM_RECIPE = {
    "version": 1,
    "source": "mercedes_benz (ocasion.mercedes-benz.es)",
    "scope": "platform-wholesale (Mercedes-Benz Certified ES certified-used; server-rendered listing + internal AJAX list endpoint)",
    "engine": "curl_cffi+chrome131_impersonate+internal_ajax_list_endpoint(POST)",
    "access": ("OPEN (t0_open; NO WAF — plain urllib AND plain curl_cffi both get HTTP 200; no JS "
               "challenge). chrome131 used only for fleet coherence. No proxy, no browser, no auth, "
               "€0. is_tier1=FALSE; defense_tier=t0_open."),
    "data_surface": "internal_api",
    "surface_intent": "internal_ajax_list_endpoint",
    "endpoint": "POST https://ocasion.mercedes-benz.es/ajxvl  (FormData type=vehiclelist, q, page=N, area=1)",
    "request": {
        "headers": "Accept application/json, X-Requested-With XMLHttpRequest, Origin/Referer the listing page, Accept-Language es-ES",
        "body": "type=vehiclelist & q=referrer=vehiclesearch&language=es-ES & page=N & area=1",
        "cookie": "warm the listing page once per session for the UCSSID cookie (served cold too).",
    },
    "response": "JSON (UTF-8 BOM -> decode utf-8-sig) {success, data:{count,page,onlyOnePage}, html:<rendered cards>}",
    "enumeration": ("page=1..401 (12 cars/page; page 401 = 4 trailing cars, 402+ = 0 cards). "
                    "data.count (4804) + first-empty-page bound the run; dedup on the per-car "
                    "vehicle id (data-vehicle / &vehicle=)."),
    "denominator": "data.count (4804) == the listing 'Encontrar N vehículos' headline.",
    "platform_entity": ("kind=oem_vo_portal, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=FALSE, defense_tier=t0_open, source_group=oem_vo_portal, role=platform, "
                        "family=mercedes_benz_vo"),
    "dual_membership": ("vehicle.entity_ulid=SELLING DEALER (compraventa); "
                        "platform_listing edge=platform<->vehicle"),
    "field_map": {
        "deep_link": "card href 'vehicle?<ident>+<make>+<model>&vehicle=<vid>&referrer=vehicles' (prefixed with the base)",
        "listing_ref": "the '<dealerCode>-<carCode>' identifier ('Identificador del vehículo') — stable id + dedup key",
        "vehicle_id": "data-vehicle / &vehicle= (per-car numeric id; secondary dedup key)",
        "make": "span.manufacturer",
        "model": "the title line after </span><br> (model + version)",
        "year": "registration-date spec row 'dd.mm.yyyy' -> trailing year",
        "km": "the km spec row ('84.574 km')",
        "price": "div.vehicle_price_headline ('49.900 €')",
        "fuel": "the fuel spec row (Diesel/Gasolina/Eléctrico/'Híbrido enchufable - Gasolina')",
        "transmission": "NOT on the list card (PDP-only; left NULL — never invented)",
        "vin": "NOT on the list card (PDP-only; left NULL — never invented)",
        "dealer": "result-box-location-item {name span, '<postalCode> <city>' span} + dealerCode (ident prefix)",
        "location": "postalCode[:2] = INE province code; city -> municipality (INE-resolved, best-effort)",
    },
    "caveats": {
        "page_size": "fixed 12 cars/page (not a request param).",
        "encoding": ("ajxvl body is UTF-8 with a BOM (decode utf-8-sig); card text is then CLEAN "
                     "UTF-8 (0 U+FFFD) — only HTML-entity unescape needed, NO latin-1 re-encode."),
        "pagination": "the page is server-rendered; pagination is the AJAX POST /ajxvl (a GET ?page=N on /vehicles does NOT page).",
        "no_vin_on_list": "VIN and gearbox are PDP-only — left NULL on the cage (never fetched, never invented).",
        "no_private_sellers": "OEM certified-used portal — every car belongs to a Mercedes-Benz dealer.",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the mercedes_benz platform entity + platform_meta exist. Returns the
    platform entity_ulid. kind='oem_vo_portal' (the platform ontology kind), is_tier1=FALSE (no
    WAF), multi-axis 0016 classification set explicitly, data_surface='internal_api'."""
    code = mercedes_benz_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               defense_tier, source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,$3,$4,$5,NULL,$6,$7::waf_kind,$8,'active','platform_label',
               $9::defense_tier,$10::source_group,$11::entity_role,$12, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, website_waf = EXCLUDED.website_waf,
               defense_tier = EXCLUDED.defense_tier, source_group = EXCLUDED.source_group,
               role = EXCLUDED.role, legal_name = EXCLUDED.legal_name, kind = EXCLUDED.kind""",
        eulid, code, MB_KIND, MB_LEGAL_NAME, MB_TRADE_NAME, MB_WEBSITE,
        MB_WAF, MB_IS_TIER1, MB_DEFENSE_TIER, MB_SOURCE_GROUP, MB_ROLE, MB_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, MB_SOURCE_KEY, MB_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'internal_api',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"endpoint": ENDPOINT, "host": host_of(ENDPOINT),
                           "method": "POST", "page_size": PAGE_SIZE,
                           "denominator": "data.count",
                           "surface_intent": "internal_ajax_list_endpoint",
                           "engine": "curl_cffi/chrome131_impersonate"}),
        MB_FAMILY)
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    Dealer identity is per-physical-installation, not per-car. The dealerCode prefix
    of the per-vehicle identifier ("<dealerCode>-<carCode>") looks like a stable dealer
    key but in practice varies almost car-by-car on this surface, causing one entity per
    vehicle (explosion ratio ~1.02 vehicles/entity, confirmed in DB: MOBILITY CENTRO =
    480 entities / 488 cars). It is retained only as source_ref for lineage.

    The conservative, never-fragmenting identity key is name + municipality_code (both
    stable for a physical point-of-sale). ``address`` is left None so the canonical key
    is purely name+municipality — a forward-fix must NEVER re-fragment a dealer, so the
    postal code is deliberately kept OUT of the hash (a card that fails to parse its
    postal would otherwise split off into a second entity). Separating two genuine
    same-name/same-municipality installations apart (by postal or other signals) is the
    job of the entity_cluster reconciliation step (B1.3), not the connector: the
    connector emits a conservative identity, the cluster refines it. This matches the
    das_weltauto OEM-VO connector, which uses the identical rule."""
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni, address=None)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# Default concurrency: pages fetched in parallel per sliding window. ocasion.mercedes-benz.es is
# NOT in the governor's JSON_API rate class — it inherits the conservative STEALTH default, the
# safe direction for a host whose true ceiling is unmeasured. The concurrency only needs to keep
# that (slow) bucket saturated; a small window is plenty.
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
                  seen_ids: set, harvested_cageable: set, stats: dict) -> list[_CageRow]:
    """Parse + geo-resolve every card across the window IN PAGE ORDER — pure CPU, no SQL.

    The EXACT per-item gate (cross-page dedup on the per-car vehicle id, dealer-parse skip, geo
    skip, cageable truth), lifted out of the DB loop so the SQL phase is purely set-based. The
    province is from the dealer's postalCode (INE first-2). `seen_ids` / `harvested_cageable` /
    `stats` are mutated here with deterministic page-order semantics so the VAM truth is
    byte-identical regardless of batching."""
    rows: list[_CageRow] = []
    for _page, cards in items_by_page:
        for card in cards:
            stats["items_seen"] += 1
            v = parse_card_vehicle(card)
            # cross-page dedup on the per-car vehicle id (stable; a long crawl can re-surface a car).
            item_id = v.vehicle_id or v.listing_ref
            if item_id and item_id in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue
            if item_id:
                seen_ids.add(item_id)

            d = parse_card_dealer(card)
            if d is None:
                stats["no_dealer_skipped"] += 1
                continue
            stats["dealer_items"] += 1

            # Geo gate — province from the postalCode, then the same province-range guard the
            # dealer upsert enforces, done in memory so a bad/missing geo is skipped without ever
            # touching the DB (no FK risk).
            prov = _prov_from_postal(d.postal_code)
            if not prov:
                stats["geo_skipped"] += 1
                continue
            if not (prov.isdigit() and "01" <= prov <= "52"):
                stats["geo_skipped"] += 1
                continue
            d = DealerRef(dealer_id=d.dealer_id, name=d.name, province_code=prov,
                          city=d.city, postal_code=d.postal_code)
            muni = geo.municipality_code(prov, d.city)
            dealer_cdp = cdp_code_dealer(d, muni)

            if not v.deep_link:
                continue
            harvested_cageable.add((d.dealer_id, v.deep_link))
            if v.vin:
                stats["vins_captured"] += 1
            rows.append(_CageRow(
                dealer_id=d.dealer_id, dealer_cdp=dealer_cdp, dealer_name=d.name,
                dealer_province=prov, dealer_muni=muni, vehicle=v))
    return rows


async def _ingest_window(conn: asyncpg.Connection, geo: GeoResolver,
                         platform_ulid: str, items_by_page: list[tuple[int, list]], seen_ids: set,
                         harvested_cageable: set, stats: dict) -> None:
    """BULK-ingest a whole concurrent page-window in ONE transaction with set-based SQL.

    Mirrors spoticar_wholesale._ingest_window EXACTLY: ONE round-trip per table per window (unnest
    multi-row upserts). The delta/VAM/platform_listing semantics are preserved: same ON CONFLICT
    idempotency, same cageable truth, same NEW-event rule (emitted only for genuinely new
    vehicles). A re-run of an already-harvested window adds 0 rows and 0 events.
    """
    cage = _parse_window(items_by_page, geo, seen_ids, harvested_cageable, stats)
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
                           d_munis, d_refs, MB_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_DEALER_SOURCES, d_cdps, d_refs, MB_SOURCE_KEY)
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
                payload = {"price": v.price, "title": v.title, "platform": MB_TRADE_NAME}
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
    # --limit converts a target car count to a page count (12 cars/page). The tighter of
    # --pages / --limit bounds the run.
    if limit is not None and limit > 0:
        limit_pages = max(1, math.ceil(limit / PAGE_SIZE))
        max_pages = min(max_pages, limit_pages)
    fetcher = MercedesBenzFetcher(pool_size=concurrency)
    stats = {
        "pages_fetched": 0, "items_seen": 0, "dealer_items": 0,
        "no_dealer_skipped": 0, "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "vins_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "dealers_distinct": 0,
        "concurrency": concurrency, "max_pages": max_pages, "private_skipped": 0,
    }
    # Harvest-side truth for the VAM: distinct CAGEABLE cars = distinct (dealer_id, deep_link)
    # pairs that survived dealer-parse + geo-resolution. Like-with-like vs db_edges.
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if mercedes_benz's breaker is OPEN (a recent ban/throttle still cooling), skip
    # the drain gracefully — the endpoint keeps serving the last snapshot.
    if await is_open(conn, MB_SOURCE_KEY):
        print(f"[mercedes_benz_wholesale] breaker OPEN for {MB_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, endpoint still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": MB_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = mercedes_benz_platform_cdp_code()
        print(f"[mercedes_benz_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid}) "
              f"kind={MB_KIND} group={MB_SOURCE_GROUP} tier={MB_DEFENSE_TIER} family={MB_FAMILY}")
        print(f"[mercedes_benz_wholesale] governor paces host {host_of(ENDPOINT)} (per-host token bucket, STEALTH class).")
        print(f"[mercedes_benz_wholesale] CONCURRENT drain: window={concurrency} pages in flight. "
              f"Target = {max_pages} pages (~{max_pages * PAGE_SIZE} cars; full ES stock = 4804).")

        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        # CONCURRENT sliding-window drain. Each window fetches up to `concurrency` pages in parallel
        # through the governor (the host bucket paces the aggregate), then the pages are INGESTED
        # sequentially in page order through the single asyncpg connection. A page that errors or
        # comes back with no cards stops the drain honestly (end of data — page 401 is the true
        # boundary — or a throttle the breaker must catch). data.count also bounds the run.
        stop = False
        next_page = 1
        while next_page <= max_pages and not stop:
            window = list(range(next_page, min(next_page + concurrency, max_pages + 1)))
            next_page = window[-1] + 1

            results = await asyncio.gather(
                *(fetcher.fetch_page_async(governed_fetch, ENDPOINT, page=p) for p in window),
                return_exceptions=True,
            )

            window_pages: list[tuple[int, list]] = []
            for page, data in zip(window, results):
                if isinstance(data, Exception):
                    fetch_error = str(data)
                    last_http = fetcher.last_status
                    print(f"[mercedes_benz_wholesale] page {page} fetch failed ({data}); stopping drain honestly.")
                    stop = True
                    break
                if stats["declared_full"] is None:
                    d = data.get("data") or {}
                    stats["declared_full"] = _to_int(d.get("count"))
                cards = _split_cards(data.get("html") or "")
                if not cards:
                    print(f"[mercedes_benz_wholesale] page {page}: no cards; stopping (data boundary reached).")
                    stop = True
                    break
                window_pages.append((page, cards))

            if window_pages:
                await _ingest_window(conn, geo, platform_ulid, window_pages, seen_ids,
                                     harvested_cageable, stats)
                stats["pages_fetched"] += len(window_pages)
                first_p, last_p = window_pages[0][0], window_pages[-1][0]
                print(f"[mercedes_benz_wholesale] window pages {first_p}-{last_p}: "
                      f"cards={sum(len(it) for _, it in window_pages)} "
                      f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                      f"edges={stats['edges_created']} dealers_seen={len(harvested_cageable)}")

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, MB_PLATFORM_RECIPE)
        print(f"[mercedes_benz_wholesale] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths that all measure
        # "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for mercedes_benz  (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join       (DB read truth)
        #   harvested_cageable = distinct (dealer_id, deep_link) pulled     (harvest truth)
        # The declared full count (4804) is reported for honesty but is NOT a quorum path (it
        # measures the WHOLE portal, not necessarily this slice unless the full drain ran).
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

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks mercedes_benz, trips
        # the breaker on a ban, and auto-repairs. OK when >=1 page fetched, no fetch error stopped
        # the drain, and the VAM did not refute.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, MB_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, MB_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[mercedes_benz_wholesale] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("MERCEDES-BENZ (OEM-VO PORTAL) WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  group / kind          : oem_vo_portal / oem_vo_portal (tier t0_open, family mercedes_benz_vo)")
    print(f"  declared full (source): {stats.get('declared_full')}")
    print(f"  concurrency (window)  : {stats.get('concurrency')} pages in flight")
    print(f"  target pages          : {stats.get('max_pages')}")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  dealer items          : {stats['dealer_items']}")
    print(f"  no-dealer skipped     : {stats['no_dealer_skipped']}")
    print(f"  private skipped       : {stats['private_skipped']} (OEM portal — none expected)")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page, vehicle-id dedup)")
    print(f"  geo skipped (bad geo) : {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for mercedes_benz = {stats.get('db_edges')})")
    print(f"  VINs captured         : {stats['vins_captured']} (list card has none — PDP-only)")
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
        description="mercedes_benz OEM-VO portal wholesale harvester (concurrent internal-AJAX-list drain)")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"pages to harvest (size={PAGE_SIZE}); default {DEFAULT_MAX_PAGES} (full ES stock)")
    parser.add_argument("--limit", type=int, default=None,
                        help=("optional target car count; converted to a page count (12/page). "
                              "The tighter of --pages / --limit bounds the run."))
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"pages fetched in parallel per sliding window; default "
                              f"{DEFAULT_CONCURRENCY}. ocasion.mercedes-benz.es inherits the conservative "
                              f"STEALTH rate class — the governor's per-host bucket is the real limiter."))
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.pages, args.concurrency, args.limit))
    _print_report(stats)


if __name__ == "__main__":
    main()
