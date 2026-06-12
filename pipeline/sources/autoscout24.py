"""AutoScout24 España adapter — per-dealer inventory harvest.

Open source (verified live 2026-06-12): full SSR with __NEXT_DATA__ carrying every
listing on the page (vehicle + seller/dealer + location). A dealer's complete stock
is reachable at /profesionales/{slug} with numberOfResults + size-20 pagination.

This module IS the AS24 extraction recipe materialized in code; recipe.py persists
a versioned recipe.yaml pointer next to the dealer.
"""
from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass, field

_BASE = "https://www.autoscout24.es"
_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
_NEXT = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)
RECIPE_VERSION = 1


@dataclass
class DealerInfo:
    source_dealer_id: str
    company_name: str | None
    slug: str | None
    province_code: str | None
    city: str | None
    street: str | None
    zip: str | None
    website: str | None = None


@dataclass
class Vehicle:
    deep_link: str
    vin_ref: str
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None


@dataclass
class DealerHarvest:
    dealer: DealerInfo | None
    vehicles: list[Vehicle] = field(default_factory=list)
    declared_count: int | None = None
    pages_drained: int = 0
    raw_count: int = 0  # total listings seen before dedup (source may serve duplicates)


def fetch_page(slug: str, page: int) -> str:
    # stable sort is load-bearing: paginating a non-stably-sorted live set fabricates
    # duplicates / drops across page boundaries (AS24 SSR hazard).
    url = f"{_BASE}/profesionales/{slug}?atype=C&sort=price&desc=1&page={page}"
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310
        return r.read().decode("utf-8", "replace")


def _next_data(html: str) -> dict:
    m = _NEXT.search(html)
    return json.loads(m.group(1)) if m else {}


def _find(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = _find(v, key)
            if r is not None:
                return r
    if isinstance(obj, list):
        for v in obj:
            r = _find(v, key)
            if r is not None:
                return r
    return None


def _find_listings(obj) -> list:
    if isinstance(obj, dict):
        if isinstance(obj.get("listings"), list):
            return obj["listings"]
        for v in obj.values():
            r = _find_listings(v)
            if r:
                return r
    if isinstance(obj, list):
        for v in obj:
            r = _find_listings(v)
            if r:
                return r
    return []


def _to_int(v):
    if v is None:
        return None
    s = re.sub(r"[^\d]", "", str(v))
    return int(s) if s else None


def _year_from(reg: str | None):
    if reg and "-" in str(reg):
        try:
            return int(str(reg).split("-")[-1])
        except ValueError:
            return None
    return None


def _slug_from_infopage(href: str | None) -> str | None:
    if not href:
        return None
    m = re.search(r"/profesionales/([a-z0-9-]+)", href)
    return m.group(1) if m else None


def _raw(field):
    """Unwrap an AS24 {raw, formatted} object (profile schema) or pass through."""
    if isinstance(field, dict):
        return field.get("raw") if field.get("raw") is not None else field.get("formatted")
    return field


def _photo(raw: dict):
    images = raw.get("images") or raw.get("ocsImagesA") or []
    if not images:
        return None
    first = images[0]
    if isinstance(first, str):
        return first
    if isinstance(first, dict):
        for k in ("src", "href", "url"):
            if first.get(k):
                return first[k]
        # nested size variants e.g. {"small": {"href": ...}}
        for v in first.values():
            if isinstance(v, dict) and (v.get("href") or v.get("src")):
                return v.get("href") or v.get("src")
    return None


def parse_listing_vehicle(raw: dict) -> Vehicle:
    v = raw.get("vehicle", {}) or {}
    tr = raw.get("tracking", {}) or {}
    prices = raw.get("prices") or {}

    # km (bounded: a real car is < 5,000,000 km; anything else is a parse/data artifact)
    km = _to_int(_raw(v.get("mileageInKm")) or tr.get("mileage"))
    if km is not None and (km <= 0 or km > 5_000_000):
        km = None

    # year from firstRegistrationDate.raw "YYYY-MM-DD" or tracking.firstRegistration "MM-YYYY"
    reg = _raw(v.get("firstRegistrationDate"))
    year = None
    if reg and len(str(reg)) >= 4 and str(reg)[:4].isdigit():
        year = int(str(reg)[:4])
    else:
        year = _year_from(tr.get("firstRegistration"))
    if year is not None and not (1900 <= year <= 2100):
        year = None

    # price: prices.public.priceRaw | tracking.price | price.priceRaw
    price = None
    pub = (prices.get("public") or prices.get("dealer") or {}) if isinstance(prices, dict) else {}
    for cand in (pub.get("priceRaw"), tr.get("price") if str(tr.get("price") or "").isdigit() else None,
                 _find(raw.get("price", {}), "priceRaw")):
        if cand is not None:
            try:
                price = float(cand)
                break
            except (TypeError, ValueError):
                pass

    title_parts = [v.get("make"), v.get("model"), _raw(v.get("variant")) or v.get("modelVersionInput")]
    title = " ".join(p for p in title_parts if p) or None
    return Vehicle(
        deep_link=_BASE + raw["url"] if raw.get("url") else "",
        vin_ref=str(raw.get("id") or raw.get("identifier") or ""),
        title=title,
        make=v.get("make"),
        model=v.get("model"),
        year=year,
        km=km,
        price=price,
        fuel=_raw(v.get("fuelCategory")) or v.get("fuel"),
        transmission=_raw(v.get("transmissionType")) or v.get("transmission"),
        photo_url=_photo(raw),
    )


def parse_page_dealer(data: dict) -> DealerInfo | None:
    """On a /profesionales/{slug} page the dealer identity lives in
    props.pageProps.dealerInfoPage (not in each listing's seller)."""
    dip = _find(data, "dealerInfoPage")
    if not isinstance(dip, dict):
        return None
    sid = dip.get("customerId") or dip.get("sellId")
    if not sid:
        return None
    addr = dip.get("customerAddress") or {}
    zip_ = addr.get("zipCode")
    prov = str(zip_)[:2] if zip_ and str(zip_)[:2].isdigit() else None
    homepage = dip.get("homepageUrl") or None
    return DealerInfo(
        source_dealer_id=str(sid),
        company_name=dip.get("customerName") or dip.get("companyAddOn"),
        slug=dip.get("slug"),
        province_code=prov,
        city=addr.get("city"),
        street=addr.get("street"),
        zip=str(zip_) if zip_ else None,
        website=homepage,
    )


def harvest_dealer(slug: str, max_pages: int = 50) -> DealerHarvest:
    """SCRAPEAR: drain every page of a dealer until the declared count is reached."""
    out = DealerHarvest(dealer=None)
    seen: set[str] = set()
    page = 1
    while page <= max_pages:
        html = fetch_page(slug, page)
        data = _next_data(html)
        if out.declared_count is None:
            n = _find(data, "numberOfResults")
            out.declared_count = int(n) if n is not None else None
        if out.dealer is None:
            out.dealer = parse_page_dealer(data)
        listings = _find_listings(data)
        if not listings:
            break
        new_on_page = 0
        for raw in listings:
            out.raw_count += 1
            veh = parse_listing_vehicle(raw)
            if veh.deep_link and veh.deep_link not in seen:
                seen.add(veh.deep_link)
                out.vehicles.append(veh)
                new_on_page += 1
        out.pages_drained = page
        # stop when we've collected the declared count or the page added nothing new
        if out.declared_count is not None and len(out.vehicles) >= out.declared_count:
            break
        if new_on_page == 0:
            break
        page += 1
    return out
