"""Flexicar CENSUS adapter — Vector 1 (chain-as-census), §1.

Flexicar is a national used-car chain; ``sitemap.xml`` lists its ~149 delegaciones under
``/delegaciones-flexicar/{slug}/``. The branch pages are thin (no clean AutoDealer JSON-LD):
the city is the page <h1> / URL slug and the phone is a ``tel:`` link. Each branch is
censused as a distinct entity 'Flexicar {City}', geo-resolved by city name (province via the
canonical ``resolve_city_global`` fallback in ``discover._upsert``) — the municipality guard
keeps the chain's branches distinct.

Run: python -m pipeline.discover flexicar_census
"""
from __future__ import annotations

import logging
import re

from pipeline.sources.autocasion_census import _http_get, _norm_phone_es
from pipeline.sources.base import DiscoveredEntity, SourceAdapter

log = logging.getLogger(__name__)

_SITEMAP = "https://www.flexicar.es/sitemap.xml"
_PREFIX = "https://www.flexicar.es/delegaciones-flexicar/"


def branch_slugs_from_sitemap(xml: str) -> list[str]:
    out: list[str] = []
    for loc in re.findall(r"<loc>([^<]+delegaciones-flexicar/[^<]+)</loc>", xml):
        slug = loc.rstrip("/").rsplit("/", 1)[-1]
        if slug and slug != "delegaciones-flexicar":
            out.append(slug)
    return out


def _city_from_slug(slug: str) -> str:
    # 'alcala-de-henares', 'alcorcon-2' -> 'Alcala De Henares', 'Alcorcon' (drop branch index)
    base = re.sub(r"-\d+$", "", slug)
    return base.replace("-", " ").strip().title()


def _clean_city(raw: str | None) -> str | None:
    """Flexicar h1s carry a neighborhood suffix ('Zaragoza - Venta del Olivar') that no
    municipality gazetteer resolves. Keep the municipality (the part before ' - ') so the
    canonical city->province resolution succeeds; the full label is kept in extra/name."""
    if not raw:
        return None
    return re.split(r"\s*[-–]\s*", raw, maxsplit=1)[0].strip() or None


def parse_branch_page(html: str, slug: str) -> dict:
    h1 = re.search(r"<h1[^>]*>\s*([^<]{2,60})", html)
    full = (h1.group(1).strip() if h1 else None) or _city_from_slug(slug)
    city = _clean_city(full) or _city_from_slug(slug)
    tel = re.search(r"tel:([+\d][\d\s]{6,18})", html)
    phone = _norm_phone_es(tel.group(1)) if tel else None
    return {"city": city, "full_label": full, "phone": phone}


class FlexicarCensusAdapter(SourceAdapter):
    source_key = "flexicar_census"

    def __init__(self, max_dealers: int | None = None) -> None:
        self._max = max_dealers
        self._slugs: list[str] | None = None
        self.excluded_count = 0

    def _slug_universe(self) -> list[str]:
        if self._slugs is None:
            slugs = branch_slugs_from_sitemap(_http_get(_SITEMAP, timeout=30))
            self._slugs = slugs if self._max is None else slugs[: self._max]
        return self._slugs

    def declared_count(self) -> int | None:
        return len(self._slug_universe())

    def entity_from(self, slug: str, rec: dict) -> DiscoveredEntity:
        city = rec.get("city") or _city_from_slug(slug)
        return DiscoveredEntity(
            kind="compraventa", source_key=self.source_key, source_ref=slug,
            legal_name=f"Flexicar {city}", trade_name=f"Flexicar {city}",
            province_name=None,                 # resolved via resolve_city_global in _upsert
            municipality_name=city,
            address=f"flexicar:{slug}", phone=rec.get("phone"), website=None,
            extra={"source_group": "marketplace_census", "vector": 1,
                   "chain": "flexicar", "profile_url": _PREFIX + slug})

    def fetch(self) -> list[DiscoveredEntity]:
        out: list[DiscoveredEntity] = []
        for slug in self._slug_universe():
            try:
                html = _http_get(_PREFIX + slug + "/")
            except Exception:  # noqa: BLE001
                self.excluded_count += 1
                continue
            out.append(self.entity_from(slug, parse_branch_page(html, slug)))
        return out
