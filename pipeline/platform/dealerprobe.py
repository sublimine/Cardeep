"""DealerProbe — generic €0 own-site dealer auto-harvester (pure classifiers).

The recon workflow (wf_3fb0d564, 90 live dealer sites) proved that ~80% of detectable dealers
expose per-vehicle URLs via a dedicated sitemap, and that the sitemap names + per-vehicle URL
shapes come from a small recurring set. These PURE classifiers encode that — no per-dealer
REGISTRY (the limit that kills family_generic_custom), no JS. The async cascade (sitemap
discovery -> JSON-LD -> microdata -> SSR cards) and the cage/dedup live in the connector module;
here are only the deterministic, unit-tested decision functions.
"""
from __future__ import annotations

import html as _html
import json
import re
from urllib.parse import urljoin, urlparse

# --- sitemap-name classifier ------------------------------------------------------------------
# Tokens seen live in real car sitemaps. Chosen to avoid dangerous substrings (e.g. NOT bare
# "car" — it lives inside "category"; NOT "cat" — inside "catalogo" only as a full token).
_CAR_SITEMAP_TOKENS = (
    "vehica", "stock_listing", "listing", "usate", "nuove", "vehicul", "vehicles",
    "coches", "product", "inventario", "catalogo", "precios", "buy",
)
# A bare index is not a leaf of cars.
_SITEMAP_INDEX_RE = re.compile(r"sitemap[_-]index")


def is_vehicle_sitemap(name: str) -> bool:
    """True iff this child-sitemap name/URL carries per-vehicle entries (not pages/posts/index)."""
    base = name.strip().lower().rstrip("/").split("/")[-1]
    if not base:
        return False
    if _SITEMAP_INDEX_RE.search(base):
        return False
    return any(tok in base for tok in _CAR_SITEMAP_TOKENS)


# --- <loc> classifier -------------------------------------------------------------------------
# A path segment is a "car surface" iff it STARTS WITH one of these (full-segment, not substring,
# so a blog slug like 'como-comprar-coche-segunda-mano' does NOT count).
_CAR_SEG_PREFIXES = (
    "coches", "coche-", "vehicul", "vehiculo", "ocasion", "segunda-mano",
    "stock", "producto", "product", "buy", "listado", "inventario", "catalogo",
)
# Last segments that are LISTING roots (category), never a single unit.
_LISTING_LAST = {
    "coches", "coches-ocasion", "coches-de-ocasion", "coches-segunda-mano", "coches-nuevos",
    "vehiculos", "vehiculos-ocasion", "vehiculos-de-ocasion", "segunda-mano", "ocasion",
    "stock", "catalogo", "inventario", "producto", "productos",
}
_UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
_DETAIL_QUERY_RE = re.compile(r"(?:vehiculo|vehicle|coche|anuncio|id|ref)=")


_ASSET_EXT_RE = re.compile(
    r"\.(?:jpg|jpeg|png|gif|webp|svg|bmp|ico|avif|css|js|mjs|pdf|xml|json|txt|"
    r"woff2?|ttf|eot|mp4|webm|mp3|zip|rss)(?:$|\?)")


def classify_loc(url: str) -> str:
    """Classify a sitemap <loc> / link as 'per_vehicle' | 'category' | 'other'."""
    p = urlparse(url.lower())
    path = p.path.rstrip("/")
    # 0. static assets (images/css/js/docs) are never inventory — a car-named image path
    # (/wp-content/.../coches-de-ocasion-4.webp) must not pollute the frontier.
    if _ASSET_EXT_RE.search(path):
        return "other"
    segs = [s for s in path.split("/") if s]

    # 1. query-encoded detail page (legacy detalles.php?vehiculo=...) — strongest signal.
    if p.query and _DETAIL_QUERY_RE.search(p.query):
        return "per_vehicle"

    # 2. no car surface anywhere in the path -> not inventory.
    has_car = any(any(seg.startswith(pre) for pre in _CAR_SEG_PREFIXES) for seg in segs)
    if not has_car:
        return "other"

    last = segs[-1] if segs else ""

    # 3. per-vehicle markers (any hit wins):
    if _UUID_RE.search(path):
        return "per_vehicle"                      # /buy/<uuid>, DealCar.io
    if re.search(r"\d{4,}", last):
        return "per_vehicle"                      # id or year-bearing unit slug
    if len(segs) >= 4:
        return "per_vehicle"                      # deep per-config path (/coches/nuevos/opel/corsa/5p/2024)
    if "-" in last and last not in _LISTING_LAST:
        return "per_vehicle"                      # make-model unit slug (nissan-qashqai, audi-a3)

    # 4. has a car surface but no unit marker -> a listing/category root or a make/city facet.
    return "category"


# --- JSON-LD + microdata vehicle parsers ------------------------------------------------------
# Standard schema.org extraction (independent of any family connector to keep this module pure —
# no async imports). Returns NORMALIZED vehicle dicts so the cascade treats every signal alike.
_LD_RE = re.compile(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I)
_VEHICLE_LD_TYPES = {"Car", "Vehicle", "MotorizedVehicle", "Motorcycle", "BusOrCoach", "MotorizedBicycle"}
_ITEM_VEHICLE_RE = re.compile(r'itemtype=["\'][^"\']*schema\.org/(?:Vehicle|Car)["\']', re.I)


def _clean(s) -> str | None:
    if s is None:
        return None
    s = str(s).strip()
    return s or None


def _to_int(v) -> int | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return int(v)
    m = re.search(r"\d+", str(v))
    return int(m.group(0)) if m else None


def _to_float(v) -> float | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = re.sub(r"[^\d,.]", "", str(v))
    if not s:
        return None
    if "," in s and "." in s:          # 1.234,56 -> 1234.56 (EU thousands+decimal)
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:                     # 24500,50 -> 24500.50
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _iter_ld_objects(html_text: str):
    """Yield every JSON-LD object on a page (handles arrays + @graph), error-safe."""
    for block in _LD_RE.findall(html_text):
        block = block.strip()
        if not block:
            continue
        try:
            obj = json.loads(block)
        except Exception:
            continue
        for c in (obj if isinstance(obj, list) else [obj]):
            if not isinstance(c, dict):
                continue
            if isinstance(c.get("@graph"), list):
                for g in c["@graph"]:
                    if isinstance(g, dict):
                        yield g
            else:
                yield c


def _name_of(v):
    """brand/model can be a str or a {name:...} object."""
    if isinstance(v, str):
        return _clean(v)
    if isinstance(v, dict):
        return _clean(v.get("name"))
    return None


def _vehicle_from_ld(obj: dict) -> dict | None:
    if not isinstance(obj, dict):
        return None
    types = obj.get("@type")                        # JSON-LD @type may be a str OR a list
    types = types if isinstance(types, list) else [types]
    if not any(t in _VEHICLE_LD_TYPES for t in types):
        return None
    # require a real vehicle signal, not a bare typed stub
    if not any(obj.get(k) for k in ("offers", "mileageFromOdometer", "productionDate",
                                    "dateVehicleFirstRegistered", "vehicleIdentificationNumber", "model")):
        return None
    make = _name_of(obj.get("brand"))
    model = _name_of(obj.get("model"))
    title = _clean(obj.get("name")) or " ".join(p for p in (make, model) if p) or None
    year = _to_int(obj.get("productionDate"))
    if year is None:
        reg = _clean(obj.get("dateVehicleFirstRegistered"))
        if reg and len(reg) >= 4:
            year = _to_int(reg[:4])
    if year is not None and not (1900 <= year <= 2100):
        year = None
    odo = obj.get("mileageFromOdometer")
    km = _to_int(odo.get("value")) if isinstance(odo, dict) else _to_int(odo)
    if km is not None and not (0 <= km <= 5_000_000):
        km = None
    offers = obj.get("offers")
    if isinstance(offers, list) and offers:
        offers = offers[0]
    price = _to_float(offers.get("price")) if isinstance(offers, dict) else None
    return {"url": _clean(obj.get("url")),
            "ref": _clean(obj.get("vehicleIdentificationNumber")) or _clean(obj.get("sku")),
            "title": title, "make": make, "model": model, "year": year, "km": km, "price": price}


def parse_jsonld_vehicles(html: str) -> list[dict]:
    """Every schema.org Car/Vehicle on a page (listing or detail), normalized."""
    out = []
    for obj in _iter_ld_objects(html):
        v = _vehicle_from_ld(obj)
        if v:
            out.append(v)
    return out


def _microdata_prop(html: str, name: str) -> str | None:
    """itemprop value: prefer content="...", else inner text. (single-block heuristic)"""
    m = re.search(r'itemprop=["\']' + name + r'["\'][^>]*\bcontent=["\']([^"\']+)["\']', html, re.I)
    if m:
        return m.group(1).strip()
    m = re.search(r'itemprop=["\']' + name + r'["\'][^>]*>\s*([^<]+?)\s*<', html, re.I)
    return m.group(1).strip() if m else None


def parse_microdata_vehicles(html: str) -> list[dict]:
    """schema.org microdata Vehicle/Car. Single-block heuristic (the common own-site detail page);
    multi-unit microdata listings are rare and fall through to the SSR-card signal."""
    if not _ITEM_VEHICLE_RE.search(html or ""):
        return []
    make = _microdata_prop(html, "brand")
    name = _microdata_prop(html, "name")
    year = _to_int(_microdata_prop(html, "modelDate") or _microdata_prop(html, "productionDate")
                   or _microdata_prop(html, "dateVehicleFirstRegistered"))
    km = _to_int(_microdata_prop(html, "mileageFromOdometer"))
    price = _to_float(_microdata_prop(html, "price"))
    m = re.search(r'itemprop=["\']url["\'][^>]*\bhref=["\']([^"\']+)["\']', html, re.I)
    url = m.group(1).strip() if m else None
    if not any([make, name, price]):
        return []
    return [{"url": url, "ref": None, "title": _clean(name) or make, "make": _clean(make),
             "model": None, "year": year, "km": km, "price": price}]


# --- SSR-card extractor (fallback signal) -----------------------------------------------------
# When neither a car-sitemap nor JSON-LD/microdata is usable, the inventory still server-renders
# as listing cards: a per-vehicle link + price/km/year inline. Generic = pull every per-vehicle
# link (classify_loc) and read the specs from that card's HTML window. No per-dealer selectors.
_HREF_RE = re.compile(r'<a\b[^>]*\bhref=["\']([^"\']+)["\']', re.I)
# Currency marker tolerates the mojibake replacement char (�): latin-encoded pages served
# without a correct charset decode '€' to '�', and HTML entities (&euro; / &#8364;). Thousands
# separator may be '.', ' ' or ',' (grupobeniautos shows 14,990€).
_SSR_PRICE_RE = re.compile(
    r'(\d{1,3}(?:[.\s,]\d{3})+|\d{4,6})\s*(?:€|eur|�|&euro;|&#8364;)', re.I)
_SSR_KM_RE = re.compile(r'(\d{1,3}(?:[.\s]?\d{3})*)\s*km', re.I)
_SSR_YEAR_RE = re.compile(r'\b(19[89]\d|20[0-2]\d)\b')
_SKIP_HREF = ("#", "mailto:", "tel:", "javascript:", "whatsapp:")


def _ssr_price(frag: str) -> float | None:
    m = _SSR_PRICE_RE.search(frag)
    return _to_float(re.sub(r"[.\s,]", "", m.group(1))) if m else None  # strip thousands seps


def _ssr_km(frag: str) -> int | None:
    m = _SSR_KM_RE.search(frag)
    if not m:
        return None
    n = _to_int(re.sub(r"[.\s]", "", m.group(1)))
    return n if n is not None and 0 <= n <= 5_000_000 else None


def _ssr_year(frag: str) -> int | None:
    m = _SSR_YEAR_RE.search(frag)
    return int(m.group(1)) if m else None


def _per_vehicle_hrefs(html_text: str, base_url: str):
    """Yield (position, absolute_url) for every <a> whose target classify_loc()s as per_vehicle."""
    for m in _HREF_RE.finditer(html_text):
        href = _html.unescape(m.group(1)).strip()
        if not href or href.lower().startswith(_SKIP_HREF):
            continue
        absu = urljoin(base_url, href)
        if classify_loc(absu) == "per_vehicle":
            yield m.start(), absu


def extract_vehicle_links(html_text: str, base_url: str) -> list[str]:
    """Every distinct per-vehicle URL linked on a listing page (the PDP frontier)."""
    out, seen = [], set()
    for _pos, u in _per_vehicle_hrefs(html_text, base_url):
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def parse_ssr_cards(html_text: str, base_url: str) -> list[dict]:
    """Per-vehicle links + the price/km/year inline in each card's HTML window. make/model are
    left to the PDP (JSON-LD/microdata) — here we secure the frontier + cheap inline specs."""
    hits = list(_per_vehicle_hrefs(html_text, base_url))
    out, seen = [], set()
    for i, (pos, u) in enumerate(hits):
        if u in seen:
            continue
        seen.add(u)
        end = hits[i + 1][0] if i + 1 < len(hits) else min(len(html_text), pos + 800)
        frag = html_text[pos:end]
        out.append({"url": u, "ref": None, "title": None, "make": None, "model": None,
                    "year": _ssr_year(frag), "km": _ssr_km(frag), "price": _ssr_price(frag)})
    return out
