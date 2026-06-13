"""rentacar_vo WHOLESALE harvester — rent-a-car companies selling their EX-FLEET used cars.

This is a SEPARATE source_group ('rentacar_vo'): rent-a-car operators that liquidate their
own used fleet through a dedicated used-stock storefront. The car a buyer purchases is a real
selling point — the rent-a-car COMPANY itself — so the company is caged as the entity and every
ex-fleet car is OWNED BY it, exactly as a marketplace's dealer owns its cars.

Each member is ONE company entity (kind='rent_a_car_vo', source_group='rentacar_vo') flowing
through the ONE wholesale architecture — not a fork of it:

  the rent-a-car COMPANY -> entity, kind='rent_a_car_vo' (+ platform_meta)   [SELLING POINT]
  each EX-FLEET CAR       -> vehicle, OWNED BY the company (entity_ulid=company)
  the car ON the storefront -> platform_listing edge (company_entity <-> vehicle)

Ownership and platform-membership coincide for a single-operator storefront: it has exactly ONE
selling entity (the company), so the owning entity and the platform entity are the SAME row. The
platform_listing edge still records the listing (url, ref, price) so the car carries the same
membership signal a marketplace car does, and the same physical car could in principle also carry
a coches.net/AS24 edge (the same operator may also list on coches.net) without changing its owner.

MEMBERS (verified LIVE 2026-06-13):

  * OK Mobility (okmobility.com/en/buy-car/used) — PRIMARY. Palma HQ (07). SSR HTML cards
    (a.own-car-card), ?page=N, id="total-cars"=172. defense_tier t1_soft (Opticks beacon on the
    public site; the listing HTML is unwalled). curl_cffi/chrome131 GET.

  * Centauro (ventas.centauro.net/coches-ocasion) — Alicante HQ (03). FULLY server-rendered
    storefront (NOT the React centauro.net/comprar-coche app, which loads from content-api
    client-side). Each car is a per-card <form> of hidden inputs (precio, precioNuevo, kilometros,
    marcaVehiculo, modeloVehiculo, mesesAntiguedad) + a /ficha-vehiculo-ocasion/{slug}/{id} link.
    ?pagina=N, 12 cars/page, page declares 28 coches. defense_tier t1_soft. curl_cffi/chrome131 GET.

  * Record Go (recordgoocasion.es/coches/segunda-mano) — Castellón HQ (12). DealerK/MotorK
    WordPress CMS (cdn.dealerk.es, vcard-* classes) — the SAME family the repo already harvests in
    family_dealerk_wholesale; that family's parse_cards reads it byte-for-byte. Single listing page,
    meta declares 18 coches. Per-car URL /coches/segunda-mano/{city}/{brand}/{model}/{fuel}/{trim}/{id}/.
    defense_tier t1_soft. curl_cffi/chrome131 GET.

GAPS (confessed, NOT fabricated — see docs/research/rentacar_vo_more_members.md):
  * Sixt ES — no Spanish used-car storefront (sitemap = ride/magazine only; /coches-ocasion 404;
    Sixt's "GW" used-car business is DE-only). No ES surface to harvest.
  * Europcar ES + Goldcar — ex-fleet sold only through the registration-gated B2B platform
    2ndmove.es -> b2b.2ndmove.eu (/es/register; professionals only; no public browsable stock).
    Their marketplace presence (motorflash/coches.net "europcar-second-hand") is already covered by
    the marketplace connectors; caging from there would double-count, so it is deferred.

This module mirrors pipeline.platform.coches_net_wholesale / oem_audi_wholesale EXACTLY (same
caging, same governor/health/VAM wiring): the rentacar_vo group flows through the ONE architecture.
Per-member geo is the company's registered HQ province (never fabricated per-branch).

Run: python -m pipeline.platform.group_rentacar_vo_wholesale --member all --pages 6
     python -m pipeline.platform.group_rentacar_vo_wholesale --member centauro
     python -m pipeline.platform.group_rentacar_vo_wholesale --member recordgo
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as _dt
import hashlib
import html as _htmllib
import json
import math
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Callable

import asyncpg
from curl_cffi import requests as cffi_requests

from pipeline.engine.governor import governor, host_of
from pipeline.geo import GeoResolver
from pipeline.ids import ulid
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict
from services.api.codes import _base32

DSN = "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
DSN = os.environ.get("CARDEEP_DSN", DSN)

_IMPERSONATE = "chrome131"
_TIMEOUT = 40

# Province sentinel '00' = national; the company entity always stores its REAL HQ province.
PLATFORM_PROVINCE_SENTINEL = "00"


# ---------------------------------------------------------------------------
# Parsed shapes
# ---------------------------------------------------------------------------
@dataclass
class Vehicle:
    """A car parsed from one rent-a-car used-stock card."""
    deep_link: str
    listing_ref: str            # company-internal car id — stable cross-run dedup key.
    title: str | None = None
    make: str | None = None
    model: str | None = None
    version: str | None = None
    year: int | None = None
    km: int | None = None
    price: float | None = None
    prev_price: float | None = None   # previous/new price -> price-drop delta.
    fuel: str | None = None
    transmission: str | None = None
    photo_url: str | None = None


def host_url_of(url: str) -> str:
    """Scheme+host origin of a URL (for the Origin header on POST members)."""
    m = re.match(r"(https?://[^/]+)", url)
    return m.group(1) if m else url


def _to_int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _eur_to_float(s: str | None) -> float | None:
    """ES-formatted thousands ('16.641') -> plain integer euros."""
    if not s:
        return None
    digits = re.sub(r"[^\d]", "", s)
    if not digits:
        return None
    try:
        return float(digits)
    except (TypeError, ValueError):
        return None


def _km_to_int(s: str | None) -> int | None:
    if not s:
        return None
    digits = re.sub(r"[^\d]", "", s)
    if not digits:
        return None
    n = int(digits)
    return n if 0 <= n <= 5_000_000 else None


def _split_make_model(name: str | None) -> tuple[str | None, str | None]:
    """First token = make; remainder = model. Two-token makes handled."""
    if not name:
        return None, None
    parts = name.split()
    if not parts:
        return None, None
    make = parts[0]
    TWO = {"land": "Land Rover", "alfa": "Alfa Romeo", "aston": "Aston Martin", "ds": "DS"}
    if len(parts) >= 2 and parts[0].lower() in TWO and TWO[parts[0].lower()].lower().endswith(parts[1].lower()):
        make = TWO[parts[0].lower()]
        model = " ".join(parts[2:]) or None
        return make, model
    model = " ".join(parts[1:]) or None
    return make, model


# ===========================================================================
# MEMBER: OK Mobility — SSR HTML card markup (a.own-car-card). PRIMARY.
# ===========================================================================
_OK_CARD_SPLIT = re.compile(r'(?=<a [^>]*class="own-car-card")')
_OK_RE_HREF = re.compile(r'href="(https://okmobility\.com/en/buy-car/used/[^"]+/\d+)"')
_OK_RE_CARID = re.compile(r'data-carid="(\d+)"')
_OK_RE_PROGICIEL = re.compile(r'data-carProgicielId="(\d+)"', re.I)
_OK_RE_IMG = re.compile(r'data-srcbg="([^"]+)"')
_OK_RE_NAME = re.compile(r'car-name"[^>]*>\s*([^<]+?)\s*<')
_OK_RE_MOTOR = re.compile(r'car-motorization">\s*([^<]+?)\s*<')
_OK_RE_SUMMARY = re.compile(r'car-summary">(.*?)</div>', re.S)
_OK_RE_SUMMARY_SPAN = re.compile(r'<span>\s*([^<|]+?)\s*</span>')
_OK_RE_PRICE = re.compile(r'paying-prices">.*?big-cipher-text">\s*([\d.,]+)', re.S)
_OK_RE_PREV = re.compile(r'deleted-small-cipher-text">\s*([\d.,]+)')
_OK_RE_TOTAL = re.compile(r'id="total-cars"[^>]*>\s*([\d.,]+)')


def _ok_parse_card(block: str) -> Vehicle | None:
    href = _OK_RE_HREF.search(block)
    cid = _OK_RE_CARID.search(block)
    if not href or not cid:
        return None
    pid = _OK_RE_PROGICIEL.search(block)
    img = _OK_RE_IMG.search(block)
    name = _OK_RE_NAME.search(block)
    motor = _OK_RE_MOTOR.search(block)
    year = km = fuel = trans = None
    summ = _OK_RE_SUMMARY.search(block)
    if summ:
        parts = [s.strip() for s in _OK_RE_SUMMARY_SPAN.findall(summ.group(1)) if s.strip()]
        if len(parts) >= 1:
            year = _to_int(parts[0])
            if year is not None and not (1900 <= year <= 2100):
                year = None
        if len(parts) >= 2:
            km = _km_to_int(parts[1])
        if len(parts) >= 3:
            fuel = parts[2] or None
        if len(parts) >= 4:
            trans = parts[3] or None
    title = name.group(1).strip() if name else None
    make, model = _split_make_model(title)
    price = _eur_to_float(_OK_RE_PRICE.search(block).group(1)) if _OK_RE_PRICE.search(block) else None
    prev = _eur_to_float(_OK_RE_PREV.search(block).group(1)) if _OK_RE_PREV.search(block) else None
    return Vehicle(
        deep_link=href.group(1), listing_ref=cid.group(1),
        title=title, make=make, model=model,
        version=motor.group(1).strip() if motor else None,
        year=year, km=km, price=price, prev_price=prev,
        fuel=fuel, transmission=trans,
        photo_url=img.group(1) if img else None)


def _ok_parse_page(html: str) -> tuple[list[Vehicle], int | None]:
    total_m = _OK_RE_TOTAL.search(html)
    declared = _to_int(total_m.group(1).replace(".", "").replace(",", "")) if total_m else None
    vehicles: list[Vehicle] = []
    for block in _OK_CARD_SPLIT.split(html):
        if "own-car-card" not in block or "data-carid" not in block:
            continue
        v = _ok_parse_card(block)
        if v is not None:
            vehicles.append(v)
    return vehicles, declared


# ===========================================================================
# MEMBER: Centauro — fully-SSR storefront (ventas.centauro.net). Each car is a
# per-card <form> of hidden inputs + a /ficha-vehiculo-ocasion/{slug}/{id} link.
# ===========================================================================
_CEN_BASE = "https://ventas.centauro.net"
_CEN_FORM_SPLIT = re.compile(r'(?=<input type="hidden" name="precio" value=)')
_CEN_RE_LINK = re.compile(r'href="(/ficha-vehiculo-ocasion/([^"/]+)/(\d+))"')
_CEN_RE_TOTAL = re.compile(r'([\d.]+)\s*coches', re.I)
_CEN_RE_IMG = re.compile(r'(https://images\.motorflash\.com/[^"\'\s]+|https://media\.staticmf\.com/[^"\'\s]+)')


def _cen_field(seg: str, name: str) -> str | None:
    m = re.search(r'name="' + re.escape(name) + r'" value="([^"]*)"', seg)
    return m.group(1).strip() if m and m.group(1).strip() else None


def _cen_year_from_months(months: str | None) -> int | None:
    """mesesAntiguedad = months since first registration -> approximate registration YEAR.
    The listing surface exposes age-in-months, not the registration date; we derive the year
    honestly (current_year - round(months/12)) and never claim a month/day the source withholds."""
    m = _to_int(months)
    if m is None or m < 0 or m > 600:
        return None
    yr = _dt.date.today().year - round(m / 12)
    return yr if 1990 <= yr <= _dt.date.today().year + 1 else None


def _cen_version_from_slug(slug: str, make: str | None, model: str | None) -> str | None:
    """The ficha slug is '{make}-{model}-{version}' kebab-cased. Strip the leading make+model
    tokens to recover the version line (e.g. 'kia-stonic-1-2-dpi-drive-62-kw-84-cv' -> '1.2 dpi
    drive 62 kw 84 cv'). Display-grade; we keep raw tokens, no canonical enforcement."""
    if not slug:
        return None
    tokens = slug.split("-")
    lead = []
    for src in (make, model):
        if src:
            for t in re.sub(r"[^a-z0-9]+", " ", src.lower()).split():
                lead.append(t)
    i = 0
    for t in lead:
        if i < len(tokens) and tokens[i].lower() == t:
            i += 1
    rest = tokens[i:]
    return " ".join(rest) if rest else None


def _cen_parse_page(html: str) -> tuple[list[Vehicle], int | None]:
    total_m = _CEN_RE_TOTAL.search(html)
    declared = _to_int(total_m.group(1).replace(".", "")) if total_m else None
    vehicles: list[Vehicle] = []
    seen: set[str] = set()
    for seg in _CEN_FORM_SPLIT.split(html)[1:]:
        link = _CEN_RE_LINK.search(seg)
        if not link:
            continue
        rel, slug, cid = link.group(1), link.group(2), link.group(3)
        if cid in seen:
            continue
        seen.add(cid)
        deep_link = _CEN_BASE + rel
        make = _cen_field(seg, "marcaVehiculo")
        model = _cen_field(seg, "modeloVehiculo")
        price = _eur_to_float(_cen_field(seg, "precio"))
        prev = _eur_to_float(_cen_field(seg, "precioNuevo"))
        km = _km_to_int(_cen_field(seg, "kilometros"))
        year = _cen_year_from_months(_cen_field(seg, "mesesAntiguedad"))
        version = _cen_version_from_slug(slug, make, model)
        title_bits = [b for b in (make, model, version) if b]
        title = " ".join(title_bits) if title_bits else None
        img = _CEN_RE_IMG.search(seg)
        # precioNuevo is the FACTORY-new price, not a prior listing price; a drop vs the
        # new-car price is the genuine ex-fleet discount, so we keep it as prev_price only
        # when it exceeds the current ask (a real, positive delta).
        prev_price = prev if (prev is not None and price is not None and prev > price) else None
        vehicles.append(Vehicle(
            deep_link=deep_link, listing_ref=cid, title=title,
            make=make, model=model, version=version, year=year, km=km,
            price=price, prev_price=prev_price,
            photo_url=img.group(1) if img else None))
    return vehicles, declared


# ===========================================================================
# MEMBER: Record Go — DealerK/MotorK WordPress (vcard-* markup). Reuses the
# repo's proven family_dealerk parser so ONE parser reads this CMS family.
# ===========================================================================
from pipeline.platform.family_dealerk_wholesale import (  # noqa: E402
    parse_cards as _dealerk_parse_cards,
)


def _recordgo_parse_page(html: str) -> tuple[list[Vehicle], int | None]:
    """Parse Record Go's listing page via the DealerK family parser, then map the family
    Vehicle shape onto this module's Vehicle (the surfaces are the same CMS markup)."""
    declared = None
    m = re.search(r'([\d.]+)\s*Coches\s+Segunda\s+mano', html, re.I) \
        or re.search(r'Descubre\s+nuestros\s+([\d.]+)\s+Coches', html, re.I)
    if m:
        declared = _to_int(m.group(1).replace(".", ""))
    out: list[Vehicle] = []
    for fv in _dealerk_parse_cards(html):
        out.append(Vehicle(
            deep_link=fv.deep_link, listing_ref=fv.listing_ref, title=fv.title,
            make=fv.make, model=fv.model, year=fv.year, km=fv.km,
            price=fv.price, fuel=fv.fuel, photo_url=fv.photo_url))
    return out, declared


# ===========================================================================
# MEMBER: Arval AutoSelect — JSON API (Azure portal API). PRIMARY by volume.
# Spain's largest ex-fleet seller; the storefront is a React app fed by the
# Announcements API, so we harvest the API JSON directly (no HTML scraping).
# ===========================================================================
def _arval_parse_page(payload: str) -> tuple[list[Vehicle], int | None]:
    """Parse one Arval Announcements API JSON page. `payload` is the raw JSON text
    (the MemberFetcher returns the response body as text for every member)."""
    try:
        doc = json.loads(payload)
    except (ValueError, TypeError):
        return [], None
    ann = doc.get("announcements") if isinstance(doc, dict) else None
    if not isinstance(ann, dict):
        return [], None
    declared = _to_int(ann.get("allAnnouncementsCount"))
    out: list[Vehicle] = []
    for car in ann.get("announcements") or []:
        if not isinstance(car, dict):
            continue
        cid = car.get("id")
        deep_link = car.get("offerUrl")
        if cid is None or not deep_link:
            continue
        details = car.get("details") or {}
        make = car.get("make") or None
        model = car.get("model") or None
        version = car.get("trim") or None
        # salePriceGross is the public ask; previousSalePriceGross > 0 is a real prior price.
        price = car.get("salePriceGross")
        price = float(price) if isinstance(price, (int, float)) and price > 0 else None
        prev = car.get("previousSalePriceGross")
        prev = float(prev) if isinstance(prev, (int, float)) and prev > 0 else None
        prev_price = prev if (prev is not None and price is not None and prev > price) else None
        title_bits = [b for b in (make, model, version) if b]
        out.append(Vehicle(
            deep_link=str(deep_link), listing_ref=str(cid),
            title=" ".join(title_bits) if title_bits else None,
            make=make, model=model, version=version,
            year=_to_int(details.get("registrationYear")),
            km=_to_int(details.get("mileage")),
            price=price, prev_price=prev_price,
            fuel=(details.get("fuelTypeLabel") or None),
            transmission=(details.get("gearbox") or None),
            photo_url=(car.get("mainImage") or None)))
    return out, declared


# ===========================================================================
# MEMBER: Northgate Ocasión — AEM catalogsearch JSON (single POST -> full array).
# The listing endpoint returns the whole stock array in one call; the React/AEM
# front paginates it client-side, so ONE POST drains the entire inventory.
# ===========================================================================
_NORTHGATE_BASE = "https://www.northgate.es"
_NG_FUEL_FIX = {"DIÉSEL": "Diésel", "DIESEL": "Diésel"}


def _northgate_parse_page(payload: str) -> tuple[list[Vehicle], int | None]:
    """Parse the Northgate catalogsearch JSON array (the full stock in one response)."""
    try:
        doc = json.loads(payload)
    except (ValueError, TypeError):
        return [], None
    if not isinstance(doc, list):
        return [], None
    out: list[Vehicle] = []
    for car in doc:
        if not isinstance(car, dict):
            continue
        cid = car.get("id")
        rel = car.get("url")
        if cid is None or not rel:
            continue
        deep_link = rel if str(rel).startswith("http") else _NORTHGATE_BASE + str(rel)
        make = car.get("brand") or None
        model = car.get("model") or None
        version = car.get("version") or None
        fuel = car.get("fuel") or None
        if fuel:
            fuel = _NG_FUEL_FIX.get(fuel.upper(), fuel.capitalize() if fuel.isupper() else fuel)
        imgs = car.get("imagePaths") or []
        photo = (imgs[0] if imgs and str(imgs[0]).startswith("http")
                 else (_NORTHGATE_BASE + imgs[0]) if imgs else None)
        title_bits = [b for b in (make, model, version) if b]
        out.append(Vehicle(
            deep_link=deep_link, listing_ref=str(cid),
            title=" ".join(title_bits) if title_bits else None,
            make=make, model=model, version=version,
            year=_to_int(car.get("year")), km=_km_to_int(car.get("km")),
            price=_eur_to_float(car.get("price")), fuel=fuel,
            photo_url=photo))
    return out, (len(out) or None)


# ---------------------------------------------------------------------------
# Member registry — identity + the surface contract for each company.
# ---------------------------------------------------------------------------
@dataclass
class Member:
    key: str                     # short selector key (okmobility/centauro/recordgo)
    domain: str                  # bare identity domain (canonical_key 'domain:<domain>')
    website: str
    legal_name: str
    trade_name: str
    source_key: str              # provenance / health key (group_rentacar_vo_<key>)
    family: str
    hq_province: str             # INE province of the registered HQ
    hq_city: str
    hq_municipality_name: str | None
    endpoint: str                # the listing surface URL
    page_param: str | None       # query param for pagination ('page' / 'pagina'); None = single page
    default_pages: int
    page_size_hint: int
    parse_page: Callable[[str], tuple[list[Vehicle], int | None]]
    referer: str
    declared_total: int | None   # source-declared full stock (for the report/recipe)
    recipe: dict
    role: str = "chain"
    defense_tier: str = "t1_soft"
    # --- optional transport overrides (JSON-API members) ---
    http_method: str = "GET"     # 'GET' or 'POST'
    post_data: dict | None = None  # urlencoded form body for POST members (Northgate)
    extra_query: str | None = None  # static query appended to every request (Arval pageSize)
    accept: str = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    data_surface: str = "sitemap"  # platform_meta.data_surface label


def _ok_recipe() -> dict:
    return {
        "version": 1, "source": "okmobility.com", "group": "rentacar_vo",
        "scope": "rentacar_vo wholesale (OK Mobility SSR HTML used-stock storefront, per-page paginated)",
        "engine": "curl_cffi+chrome131_impersonate+ssr_html_embedded_card_markup(GET)",
        "access": ("OPEN server-rendered HTML (Chrome TLS fingerprint; no proxy/browser/cookie). "
                   "'/en/' serves; '/es/' 404s. Opticks bot beacon on the public site -> t1_soft; "
                   "the listing HTML is unwalled."),
        "endpoint": "GET https://okmobility.com/en/buy-car/used?page=N",
        "enumeration": "?page=1..N (~35 cars/page); id=\"total-cars\" declares full stock (172 live)",
        "field_map": {
            "deep_link": "a.own-car-card href", "listing_ref": "data-carid",
            "make_model": "div.car-name", "version": "div.car-motorization",
            "summary": "div.car-summary spans [year|km|fuel|transmission]",
            "price": "div.big-cipher-text", "prev_price": "div.deleted-small-cipher-text",
            "photo_url": "div.car-image data-srcbg (cdn.okrentacar.es)"},
    }


def _cen_recipe() -> dict:
    return {
        "version": 1, "source": "centauro.net", "group": "rentacar_vo",
        "scope": "rentacar_vo wholesale (Centauro fully-SSR used-stock storefront, per-page paginated)",
        "engine": "curl_cffi+chrome131_impersonate+ssr_html_form_card_markup(GET)",
        "access": ("OPEN server-rendered HTML on ventas.centauro.net (the React centauro.net app at "
                   "/comprar-coche-segunda-mano/disponibilidad loads from content-api.centauro.net "
                   "client-side; the SSR ventas surface needs no API/browser). t1_soft."),
        "endpoint": "GET https://ventas.centauro.net/coches-ocasion/?pagina=N",
        "enumeration": "?pagina=1..N (12 cars/SSR page); page declares '<N> coches' (28 live)",
        "ownership": ("the rent-a-car COMPANY is the singular selling point -> it OWNS every ex-fleet "
                      "car; platform_listing edge records the listing. owner entity == platform entity."),
        "field_map": {
            "deep_link": "a href /ficha-vehiculo-ocasion/{make-model-version-slug}/{id}",
            "listing_ref": "trailing numeric id in the ficha URL (stable dedup key)",
            "make": "hidden input marcaVehiculo", "model": "hidden input modeloVehiculo",
            "version": "ficha URL slug minus make+model tokens",
            "price": "hidden input precio (int euros)",
            "prev_price": "hidden input precioNuevo (factory-new price -> ex-fleet discount delta)",
            "km": "hidden input kilometros",
            "year": "hidden input mesesAntiguedad -> current_year - round(months/12)",
            "photo_url": "images.motorflash.com / media.staticmf.com (Centauro own-stock CDN)"},
        "caveats": {
            "no_fuel_transmission": "not on the listing card (only on the PDP) -> left NULL, never faked.",
            "year_is_derived": "the surface exposes age-in-months, not a registration date; year is "
                               "derived (current_year - round(months/12)), month/day not claimed."},
    }


def _recordgo_recipe() -> dict:
    return {
        "version": 1, "source": "recordgoocasion.es", "group": "rentacar_vo",
        "scope": "rentacar_vo wholesale (Record Go DealerK/MotorK WordPress used-stock storefront)",
        "engine": "curl_cffi+chrome131_impersonate+dealerk_vcard_html(GET)",
        "access": ("OPEN server-rendered DealerK/MotorK WordPress (cdn.dealerk.es, vcard-* classes) "
                   "— the SAME CMS family family_dealerk_wholesale already harvests; its parser reads "
                   "this site byte-for-byte. t1_soft."),
        "endpoint": "GET https://www.recordgoocasion.es/coches/segunda-mano/",
        "enumeration": ("single listing page (no ?page; /page/2/ 404s). The Yoast "
                        "stock_listing_0-sitemap.xml is empty -> harvest the listing page. "
                        "meta declares 18 coches 'desde 10.200 €'"),
        "per_car_url": "/coches/segunda-mano/{city}/{brand}/{model}/{fuel}/{trim}/{id}/",
        "ownership": ("the rent-a-car COMPANY owns every ex-fleet car; platform_listing edge records "
                      "the listing. per-car city is in the URL (valencia/sevilla/malaga) but ownership "
                      "stays with the company, anchored to its Castellón HQ."),
        "field_map": {
            "deep_link": "vcard PDP anchor href (.../<id>/)", "listing_ref": "numeric id in the path",
            "make_model": "vcard-main-info__make-model", "version": "vcard-main-info__version",
            "price": "vcard-price__price", "year/km/fuel": "vcard-consumption__title 'MM/YYYY - KM Km - Fuel'",
            "photo_url": "cdn.dealerk.es vehicle image"},
    }


def _arval_recipe() -> dict:
    return {
        "version": 1, "source": "autoselect.arval.es", "group": "rentacar_vo",
        "scope": "rentacar_vo wholesale (Arval AutoSelect ex-fleet used-stock; JSON Announcements API)",
        "engine": "curl_cffi+chrome131_impersonate+json_api(GET)",
        "access": ("OPEN JSON. The React storefront (autoselect.arval.es) is fed by the Azure "
                   "portal API; we harvest the API JSON directly (Chrome TLS fingerprint; no "
                   "key/cookie/browser). t1_soft."),
        "endpoint": ("GET https://arval-prod-euw-appservice-portalapi.azurewebsites.net/api/"
                     "Announcements/4?pageNumber=N&pageSize=24"),
        "enumeration": ("?pageNumber=1..M&pageSize=24 (24 cars/page). "
                        "announcements.allAnnouncementsCount declares full stock (1172 live)."),
        "ownership": ("Arval (BNP Paribas) is the singular selling point -> owns every ex-fleet car; "
                      "platform_listing edge records the offer. owner entity == platform entity. "
                      "HQ Madrid; per-car 'location' (Madrid Loeches/Algete/Sevilla...) is the depot."),
        "field_map": {
            "deep_link": "offerUrl", "listing_ref": "id (int)",
            "make": "make", "model": "model", "version": "trim",
            "price": "salePriceGross", "prev_price": "previousSalePriceGross (>ask -> drop delta)",
            "km": "details.mileage", "year": "details.registrationYear",
            "fuel": "details.fuelTypeLabel", "transmission": "details.gearbox",
            "photo_url": "mainImage (arvalprodeuwsa.blob.core.windows.net)"},
    }


def _northgate_recipe() -> dict:
    return {
        "version": 1, "source": "northgate.es", "group": "rentacar_vo",
        "scope": "rentacar_vo wholesale (Northgate Ocasión ex-renting used-stock; AEM catalogsearch JSON)",
        "engine": "curl_cffi+chrome131_impersonate+json_post_full_array(POST)",
        "access": ("OPEN JSON. AEM catalogsearch servlet returns the WHOLE stock array in one POST "
                   "(the React/AEM front paginates client-side). Body 'type[]=' triggers the array; "
                   "'filter=\"\"' returns only facet metadata. t1_soft."),
        "endpoint": ("POST https://www.northgate.es/content/northgate/es/vehiculos-ocasion/"
                     "jcr:content.catalogsearch.html  (body: type[]=)"),
        "enumeration": "single POST -> full array (108 live); no server pagination needed.",
        "ownership": ("Northgate Renting is the singular selling point -> owns every ex-renting car; "
                      "platform_listing edge records the listing. owner entity == platform entity. "
                      "HQ Madrid; per-car 'province' is the centre that holds the car."),
        "field_map": {
            "deep_link": "url (/vehiculos-ocasion/catalogo/...-{id})", "listing_ref": "id",
            "make": "brand", "model": "model", "version": "version",
            "price": "price", "km": "km", "year": "year", "fuel": "fuel",
            "province": "province (per-car centre)", "photo_url": "imagePaths[0]"},
    }


MEMBERS: dict[str, Member] = {
    "okmobility": Member(
        key="okmobility", domain="okmobility.com", website="okmobility.com",
        legal_name="OK Mobility Group", trade_name="OK Mobility",
        source_key="group_rentacar_vo_okmobility", family="okmobility",
        hq_province="07", hq_city="Palma de Mallorca", hq_municipality_name=None,
        endpoint="https://okmobility.com/en/buy-car/used", page_param="page",
        default_pages=6, page_size_hint=35, parse_page=_ok_parse_page,
        referer="https://okmobility.com/en/buy-car/", declared_total=172, recipe=_ok_recipe()),
    "centauro": Member(
        key="centauro", domain="centauro.net", website="centauro.net",
        legal_name="Centauro Rent a Car", trade_name="Centauro",
        source_key="group_rentacar_vo_centauro", family="centauro",
        hq_province="03", hq_city="Alicante", hq_municipality_name="Alicante",
        endpoint="https://ventas.centauro.net/coches-ocasion/", page_param="pagina",
        default_pages=5, page_size_hint=12, parse_page=_cen_parse_page,
        referer="https://ventas.centauro.net/", declared_total=28, recipe=_cen_recipe()),
    "recordgo": Member(
        key="recordgo", domain="recordgoocasion.es", website="recordgoocasion.es",
        legal_name="Record Go Mobility", trade_name="Record Go Ocasión",
        source_key="group_rentacar_vo_recordgo", family="recordgo_dealerk",
        hq_province="12", hq_city="Castellón de la Plana", hq_municipality_name="Castelló de la Plana",
        endpoint="https://www.recordgoocasion.es/coches/segunda-mano/", page_param="page",
        default_pages=6, page_size_hint=15, parse_page=_recordgo_parse_page,
        referer="https://www.recordgoocasion.es/", declared_total=18, recipe=_recordgo_recipe()),
    "arval": Member(
        key="arval", domain="arval.es", website="autoselect.arval.es",
        legal_name="Arval Service Lease S.A.", trade_name="Arval AutoSelect",
        source_key="group_rentacar_vo_arval", family="arval_autoselect_jsonapi",
        hq_province="28", hq_city="Madrid", hq_municipality_name="Madrid",
        endpoint=("https://arval-prod-euw-appservice-portalapi.azurewebsites.net/"
                  "api/Announcements/4"),
        page_param="pageNumber", default_pages=60, page_size_hint=24,
        parse_page=_arval_parse_page, referer="https://autoselect.arval.es/",
        declared_total=1172, recipe=_arval_recipe(),
        http_method="GET", extra_query="pageSize=24",
        accept="application/json, text/plain, */*", data_surface="internal_api"),
    "northgate": Member(
        key="northgate", domain="northgate.es", website="northgate.es",
        legal_name="Northgate España Renting Flexible S.A.", trade_name="Northgate Ocasión",
        source_key="group_rentacar_vo_northgate", family="northgate_aem_jsonpost",
        hq_province="28", hq_city="Madrid", hq_municipality_name="Madrid",
        endpoint=("https://www.northgate.es/content/northgate/es/vehiculos-ocasion/"
                  "jcr:content.catalogsearch.html"),
        page_param=None, default_pages=1, page_size_hint=120,
        parse_page=_northgate_parse_page, referer="https://www.northgate.es/vehiculos-ocasion",
        declared_total=108, recipe=_northgate_recipe(),
        http_method="POST", post_data={"type[]": ""},
        accept="application/json, text/javascript, */*; q=0.01", data_surface="internal_api"),
}


def member_cdp_code(m: Member) -> str:
    """The member company's immutable cdp_code: canonical_key 'domain:<domain>' + HQ province
    segment. Mirrors ok_platform_cdp_code() so every selling point mints codes the same way."""
    key = f"domain:{m.domain}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{m.hq_province}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Fetch: a POOL of fingerprint-coherent curl_cffi GET sessions routed THROUGH the governor.
# ---------------------------------------------------------------------------
class MemberFetcher:
    def __init__(self, member: Member, pool_size: int = 1) -> None:
        self._member = member
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch_page(self, url: str, *, page: int = 1, slot: int = 0) -> str:
        session = self._sessions[slot]
        m = self._member
        full = url
        if page and page > 1 and m.page_param:
            sep = "&" if "?" in full else "?"
            full = f"{full}{sep}{m.page_param}={page}"
        elif page and m.page_param and m.http_method == "GET" and m.extra_query is not None:
            # JSON-API members (Arval) need the page param on page 1 too.
            sep = "&" if "?" in full else "?"
            full = f"{full}{sep}{m.page_param}={page}"
        if m.extra_query:
            sep = "&" if "?" in full else "?"
            full = f"{full}{sep}{m.extra_query}"
        headers = {
            "Accept": m.accept,
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Referer": m.referer,
        }
        if m.http_method == "POST":
            headers["X-Requested-With"] = "XMLHttpRequest"
            headers["Origin"] = host_url_of(m.endpoint)
            resp = session.post(full, headers=headers, data=(m.post_data or {}),
                                impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        else:
            resp = session.get(full, headers=headers, impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {full}")
        return resp.content.decode("utf-8", "replace")

    async def fetch_page_async(self, governed_fetch, url: str, *, page: int) -> str:
        slot = await self._free.get()
        try:
            return await governed_fetch(url, page=page, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer — ensure the company platform entity, bulk-upsert company-owned vehicles,
# link the edge, emit NEW deltas. Idempotent ON CONFLICT, byte-identical to OK Mobility.
# ---------------------------------------------------------------------------
async def ensure_platform_entity(conn: asyncpg.Connection, geo: GeoResolver, m: Member) -> str:
    """Idempotently ensure the company entity + platform_meta exist. Returns the entity ulid.
    kind='rent_a_car_vo', source_group='rentacar_vo', anchored to the registered HQ province
    (municipality resolved via the geo backbone where the HQ city is unambiguous)."""
    code = member_cdp_code(m)
    muni = None
    if m.hq_municipality_name:
        muni = geo.municipality_code(m.hq_province, m.hq_municipality_name)
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, municipality_code, website, website_waf, is_tier1, status, kind_source,
               sells_cars, defense_tier, source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,'rent_a_car_vo'::entity_kind,$3,$4,$5,$6,$7,NULL::waf_kind,FALSE,'active',
               'platform_label',TRUE,$8::defense_tier,'rentacar_vo'::source_group,$9::entity_role,$10, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, website_waf = EXCLUDED.website_waf,
               defense_tier = EXCLUDED.defense_tier, source_group = EXCLUDED.source_group,
               role = EXCLUDED.role, kind = EXCLUDED.kind, legal_name = EXCLUDED.legal_name,
               province_code = EXCLUDED.province_code,
               municipality_code = COALESCE(EXCLUDED.municipality_code, entity.municipality_code)""",
        eulid, code, m.legal_name, m.trade_name, m.hq_province, muni, m.website,
        m.defense_tier, m.role, m.source_key)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, m.source_key, m.domain)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,$2,$3::jsonb,FALSE,FALSE,$4)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, m.data_surface,
        json.dumps({"endpoint": m.endpoint, "host": host_of(m.endpoint), "method": m.http_method,
                    "enumeration": (f"?{m.page_param}=N" if m.page_param else "single_page"),
                    "surface_intent": "ssr_html_used_stock_storefront" if m.http_method == "GET"
                                      and m.data_surface == "sitemap" else "json_api_used_stock",
                    "engine": "curl_cffi/chrome131_impersonate"}),
        m.family)
    return eulid


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


def _parse_window(member: Member, pages: list[tuple[int, str]], seen_ids: set,
                  harvested_cageable: set, company_ulid: str, stats: dict) -> list[Vehicle]:
    """Parse every card across the window IN PAGE ORDER — pure CPU, no SQL. Cross-page dedup on
    the internal car id. The cageable truth is (company_ulid, deep_link)."""
    out: list[Vehicle] = []
    for _page, html in pages:
        vehicles, declared = member.parse_page(html)
        if stats["declared_full"] is None and declared is not None:
            stats["declared_full"] = declared
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
            harvested_cageable.add((company_ulid, v.deep_link))
            out.append(v)
    return out


async def _ingest_window(conn: asyncpg.Connection, member: Member, company_ulid: str,
                         pages: list[tuple[int, str]], seen_ids: set,
                         harvested_cageable: set, stats: dict) -> None:
    """BULK-ingest a whole page-window in ONE transaction with set-based SQL. The owner of every
    car is the single company entity; cars insert under company_ulid, the edge records the listing,
    the NEW event fires for genuinely new vehicles only. Idempotency/delta/VAM byte-identical."""
    cage = _parse_window(member, pages, seen_ids, harvested_cageable, company_ulid, stats)
    if not cage:
        return

    async with conn.transaction():
        cars: dict[tuple[str, str], Vehicle] = {}
        for v in cage:
            key = (company_ulid, v.deep_link)
            if key not in cars:
                cars[key] = v

        car_keys = list(cars.keys())
        v_links = [k[1] for k in car_keys]
        existing: dict[tuple[str, str], str] = {
            (row["entity_ulid"], row["deep_link"]): row["vehicle_ulid"]
            for row in await conn.fetch(
                """SELECT vehicle_ulid, entity_ulid, deep_link FROM vehicle
                   WHERE entity_ulid = $1 AND deep_link = ANY($2::text[])""",
                company_ulid, v_links)
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
            ins = [(vehicle_ulid_for[k], k[0], cars[k]) for k in new_keys]
            await conn.execute(
                _BULK_INSERT_VEHICLES,
                [x[0] for x in ins], [x[1] for x in ins], [x[2].deep_link for x in ins],
                [x[2].title for x in ins], [x[2].make for x in ins], [x[2].model for x in ins],
                [x[2].year for x in ins], [x[2].km for x in ins], [x[2].price for x in ins],
                [x[2].fuel for x in ins], [x[2].transmission for x in ins],
                [x[2].photo_url for x in ins], [x[2].listing_ref for x in ins])
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

        e_vehicles = [vehicle_ulid_for[k] for k in car_keys]
        e_urls = [cars[k].deep_link for k in car_keys]
        e_refs = [cars[k].listing_ref for k in car_keys]
        e_prices = [cars[k].price for k in car_keys]
        edge_rows = await conn.fetch(_BULK_UPSERT_EDGES, e_vehicles, e_urls, e_refs,
                                     e_prices, company_ulid)
        stats["edges_created"] += sum(1 for row in edge_rows if row["inserted"])

        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                v = cars[k]
                payload = {"price": v.price, "title": v.title, "platform": member.trade_name}
                if v.prev_price is not None and v.price is not None and v.prev_price > v.price:
                    payload["price_drop"] = {"from": v.prev_price, "to": v.price,
                                             "amount": v.prev_price - v.price}
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities, ev_payloads)
            stats["new_events"] += len(confirmed_new)


# ---------------------------------------------------------------------------
# Per-member orchestration
# ---------------------------------------------------------------------------
DEFAULT_CONCURRENCY = 4


async def harvest_member(conn: asyncpg.Connection, geo: GeoResolver, m: Member,
                         max_pages: int, concurrency: int, limit: int | None) -> dict:
    concurrency = max(1, concurrency)
    if not m.page_param:
        max_pages = 1
        concurrency = 1
    if limit is not None and limit > 0:
        limit_pages = max(1, math.ceil(limit / max(1, m.page_size_hint)))
        max_pages = min(max_pages, limit_pages)
    fetcher = MemberFetcher(m, pool_size=concurrency)
    stats = {
        "member": m.key, "pages_fetched": 0, "items_seen": 0, "cars_caged": 0, "new_cars": 0,
        "edges_created": 0, "new_events": 0, "price_drops_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "no_link_skipped": 0,
        "concurrency": concurrency, "max_pages": max_pages,
    }
    harvested_cageable: set[tuple[str, str]] = set()

    if await is_open(conn, m.source_key):
        print(f"[rentacar_vo:{m.key}] breaker OPEN for {m.source_key}; skipping drain "
              f"(graceful degradation).")
        return {"skipped": True, "reason": "breaker_open", "source_key": m.source_key, "member": m.key}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None

    company_ulid = await ensure_platform_entity(conn, geo, m)
    platform_code = member_cdp_code(m)
    muni = geo.municipality_code(m.hq_province, m.hq_municipality_name) if m.hq_municipality_name else None
    print(f"[rentacar_vo:{m.key}] company entity ready: {platform_code} (ulid={company_ulid}) "
          f"kind=rent_a_car_vo group=rentacar_vo role={m.role} tier={m.defense_tier} "
          f"family={m.family} hq_province={m.hq_province} muni={muni}")
    print(f"[rentacar_vo:{m.key}] governor paces host {host_of(m.endpoint)} (per-host token bucket).")
    print(f"[rentacar_vo:{m.key}] SSR drain: window={concurrency} pages. target={max_pages} "
          f"(~{m.page_size_hint} cars/page).")

    seen_ids: set[str] = set()
    edges_before = await conn.fetchval(
        "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", company_ulid)

    stop = False
    next_page = 1
    while next_page <= max_pages and not stop:
        window = list(range(next_page, min(next_page + concurrency, max_pages + 1)))
        next_page = window[-1] + 1
        results = await asyncio.gather(
            *(fetcher.fetch_page_async(governed_fetch, m.endpoint, page=p) for p in window),
            return_exceptions=True,
        )
        window_pages: list[tuple[int, str]] = []
        for page, data in zip(window, results):
            if isinstance(data, Exception):
                fetch_error = str(data)
                last_http = fetcher.last_status
                print(f"[rentacar_vo:{m.key}] page {page} fetch failed ({data}); stopping honestly.")
                stop = True
                break
            vehicles, _ = m.parse_page(data)
            if not vehicles:
                print(f"[rentacar_vo:{m.key}] page {page}: no cards; stopping (data boundary).")
                stop = True
                break
            window_pages.append((page, data))

        if window_pages:
            before_distinct = len(harvested_cageable)
            await _ingest_window(conn, m, company_ulid, window_pages, seen_ids,
                                 harvested_cageable, stats)
            stats["pages_fetched"] += len(window_pages)
            first_p, last_p = window_pages[0][0], window_pages[-1][0]
            print(f"[rentacar_vo:{m.key}] window pages {first_p}-{last_p}: "
                  f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                  f"edges={stats['edges_created']} drops={stats['price_drops_captured']}")
            # Clamp-repeat boundary: some SSR storefronts (e.g. Centauro) do not 404 or
            # return an empty page past the last one — they re-serve the last page's cards.
            # If a whole window added ZERO new distinct cars, the inventory is exhausted;
            # stop honestly rather than re-fetching the same tail up to max_pages.
            if len(harvested_cageable) == before_distinct:
                print(f"[rentacar_vo:{m.key}] window pages {first_p}-{last_p}: 0 new distinct "
                      f"cars (clamp-repeat boundary); stopping.")
                stop = True

    recipe_path = write_recipe(platform_code, m.recipe)
    print(f"[rentacar_vo:{m.key}] recipe written: {recipe_path}")

    # VAM count quorum — THREE orthogonal like-with-like paths.
    db_edges = await conn.fetchval(
        "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", company_ulid)
    db_join_vehicles = await conn.fetchval(
        """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
           JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
           JOIN entity e ON e.entity_ulid = v.entity_ulid
           WHERE pl.platform_entity_ulid=$1""", company_ulid)
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
    stats["edges_new_this_run"] = db_edges - (edges_before or 0)
    stats["platform_code"] = platform_code
    stats["platform_ulid"] = company_ulid
    stats["recipe_path"] = str(recipe_path)

    run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
    run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
    outcome = await record_run(
        conn, m.source_key, ok=run_ok, rows=stats["cars_caged"],
        error=run_error, http_status=last_http)
    stats["health_status"] = outcome.status
    stats["breaker_state"] = outcome.breaker_state
    if not run_ok:
        stats["repair_action"] = await auto_repair(
            conn, m.source_key, run_error or "harvest failed",
            phase="scrape", http_status=last_http)
    return stats


async def harvest(members: list[str], max_pages: int = 6,
                  concurrency: int = DEFAULT_CONCURRENCY, limit: int | None = None) -> dict:
    conn = await asyncpg.connect(DSN)
    try:
        geo = await GeoResolver.load(conn)
        out: dict = {"members": {}}
        for key in members:
            m = MEMBERS[key]
            pages = max_pages if max_pages else m.default_pages
            print("\n" + "-" * 64)
            print(f"MEMBER: {m.trade_name} ({m.key})  [{m.domain}]")
            print("-" * 64)
            res = await harvest_member(conn, geo, m, pages, concurrency, limit)
            out["members"][key] = res
        return out
    finally:
        await conn.close()


def _print_member(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[rentacar_vo:{stats.get('member')}] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print(f"RENTACAR_VO WHOLESALE — {stats.get('member','').upper()} — REPORT")
    print("=" * 64)
    print(f"  company cdp_code      : {stats.get('platform_code')}")
    print(f"  declared full (source): {stats.get('declared_full')}")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')}")
    print(f"  no-link skipped       : {stats['no_link_skipped']}")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total = {stats.get('db_edges')}, +{stats.get('edges_new_this_run')} this run)")
    print(f"  price drops captured  : {stats['price_drops_captured']}")
    print(f"  NEW delta events      : {stats['new_events']}")
    print("  --- VAM count quorum (like-with-like) ---")
    print(f"  harvested_cageable    : {stats.get('harvested_cageable')}")
    print(f"  db_edges              : {stats.get('db_edges')}")
    print(f"  db_join_vehicles      : {stats.get('db_join_vehicles')}")
    print(f"  VAM verdict           : {stats.get('verdict')}")
    print(f"  health / breaker      : {stats.get('health_status')} / {stats.get('breaker_state')}")
    print(f"  recipe                : {stats.get('recipe_path')}")
    print("=" * 64)


# ---------------------------------------------------------------------------
# DEFERRED member — reachable but browser-required (Angular-hydrated SPA).
# Caged as a rentacar_vo entity with its recipe, but the ex-fleet stock drain is
# deferred to a camoufox/Playwright hydrate pass. We register the SELLING POINT
# and its recipe honestly; we do NOT fabricate stock from the empty static HTML.
# ---------------------------------------------------------------------------
DEFERRED_MEMBERS: dict[str, Member] = {
    "athlon": Member(
        key="athlon", domain="athloncaroutlet.es", website="athloncaroutlet.es",
        legal_name="Athlon Car Lease Spain S.A.", trade_name="Athlon Car Outlet",
        source_key="group_rentacar_vo_athlon", family="athlon_irt_angular_hydrated",
        hq_province="08", hq_city="Santa Perpètua de Mogoda",
        hq_municipality_name="Santa Perpètua de Mogoda",
        endpoint="https://www.athloncaroutlet.es/buscar-coches/", page_param=None,
        default_pages=1, page_size_hint=114, parse_page=lambda _t: ([], 114),
        referer="https://www.athloncaroutlet.es/", declared_total=114,
        recipe={
            "version": 1, "source": "athloncaroutlet.es", "group": "rentacar_vo",
            "scope": "rentacar_vo wholesale (Athlon Car Outlet ex-renting used-stock; Angular IRT SPA)",
            "engine": "camoufox/playwright_hydrate+dom_card_parse (DEFERRED; not curl_cffi-reachable)",
            "access": ("Angular SPA (occasions.services.athlon.com) fed by the Athlon IRT API "
                       "(services.athlon.com/api/irt/secured/employee/athloncaroutletes/{facets,search}). "
                       "'facets' GET is unauth and declares 114; the 'search' POST uses an undocumented "
                       "query DSL and the listing HTML is client-rendered (absent from raw curl). "
                       "-> browser hydrate required. t2_js_challenge."),
            "endpoint": "GET https://www.athloncaroutlet.es/buscar-coches/ (hydrate, parse .cardetail)",
            "enumeration": "single hydrated page; facets declare 114 cars.",
            "deep_link": "https://www.athloncaroutlet.es/buscar-coches/{make}/{model}/{licensePlate}",
            "field_map": {
                "listing_ref": "license plate (e.g. 5294LYB) in the deep-link path",
                "make_model_version": ".cardetail text + img alt",
                "year": "MM-YYYY reg line", "km": "'NN.NNN Km' line",
                "energy_label": "ECO/C/cero line", "fuel": "Diesel/Gasolina line",
                "transmission": "AUT7/Manual line", "location": "depot line",
                "price": "'NN.NNN €' line", "photo_url": "media.services.irt.athlon.com AssetId"},
            "status": "DEFERRED — entity caged; stock drain pending camoufox hydrate pass.",
        },
        defense_tier="t2_js_challenge", http_method="GET", data_surface="internal_api"),
}


async def register_deferred(keys: list[str]) -> None:
    """Idempotently cage a DEFERRED member's selling-point entity + write its recipe, WITHOUT
    harvesting stock (the surface is browser-required). No fake cars, no false health verdict."""
    conn = await asyncpg.connect(DSN)
    try:
        geo = await GeoResolver.load(conn)
        for key in keys:
            m = DEFERRED_MEMBERS[key]
            company_ulid = await ensure_platform_entity(conn, geo, m)
            code = member_cdp_code(m)
            recipe_path = write_recipe(code, m.recipe)
            print(f"[rentacar_vo:{m.key}] DEFERRED entity caged: {code} (ulid={company_ulid}) "
                  f"tier={m.defense_tier} family={m.family}; recipe={recipe_path}")
            print(f"[rentacar_vo:{m.key}] stock drain DEFERRED (browser-required); "
                  f"declared stock={m.declared_total}. No cars fabricated.")
    finally:
        await conn.close()


def _force_utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass


def main() -> None:
    _force_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="rentacar_vo wholesale harvester (OK Mobility / Centauro / Record Go used-stock)")
    parser.add_argument("--member", default="all",
                        choices=["all", *MEMBERS.keys()],
                        help="which company to harvest; 'all' runs every member.")
    parser.add_argument("--pages", type=int, default=0,
                        help="SSR pages per member (0 = each member's own default).")
    parser.add_argument("--limit", type=int, default=None,
                        help="optional target car count; converted to a page cap.")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=f"pages fetched in parallel per window; default {DEFAULT_CONCURRENCY}.")
    parser.add_argument("--register-deferred", default=None,
                        choices=["all", *DEFERRED_MEMBERS.keys()],
                        help="cage a browser-required member's entity+recipe WITHOUT harvesting stock.")
    args = parser.parse_args()
    if args.register_deferred:
        keys = (list(DEFERRED_MEMBERS.keys()) if args.register_deferred == "all"
                else [args.register_deferred])
        asyncio.run(register_deferred(keys))
        return
    members = list(MEMBERS.keys()) if args.member == "all" else [args.member]
    out = asyncio.run(harvest(members, args.pages, args.concurrency, args.limit))
    for key in members:
        _print_member(out["members"][key])


if __name__ == "__main__":
    main()
