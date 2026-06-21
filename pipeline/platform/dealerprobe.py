"""DealerProbe — generic €0 own-site dealer auto-harvester (pure classifiers).

The recon workflow (wf_3fb0d564, 90 live dealer sites) proved that ~80% of detectable dealers
expose per-vehicle URLs via a dedicated sitemap, and that the sitemap names + per-vehicle URL
shapes come from a small recurring set. These PURE classifiers encode that — no per-dealer
REGISTRY (the limit that kills family_generic_custom), no JS. The async cascade (sitemap
discovery -> JSON-LD -> microdata -> SSR cards) and the cage/dedup live in the connector module;
here are only the deterministic, unit-tested decision functions.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

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


def classify_loc(url: str) -> str:
    """Classify a sitemap <loc> / link as 'per_vehicle' | 'category' | 'other'."""
    p = urlparse(url.lower())
    path = p.path.rstrip("/")
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
