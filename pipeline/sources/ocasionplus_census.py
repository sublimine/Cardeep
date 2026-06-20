"""OcasionPlus CENSUS adapter — Vector 1 (marketplace/chain-as-census), §1.

OcasionPlus is a national used-car chain; its ``sitemap.concesionarios.xml`` enumerates its
~120 physical branches, each with a server-rendered JSON-LD ``AutoDealer`` (name, telephone,
PostalAddress) — the SAME structure autocasion exposes, so the profile parse is reused.

Each branch is censused as a distinct geo-located entity (kind='compraventa'). The identity
layer's municipality guard keeps branches of the same chain distinct (Alicante ≠ Almería),
exactly as it does for Flexicar/Quadis — this is a chain census, not a single entity.

Run: python -m pipeline.discover ocasionplus_census
"""
from __future__ import annotations

import logging
import re

from pipeline.sources.autocasion_census import (
    _http_get,
    _province_from_postcode,
    parse_profile,
)
from pipeline.sources.base import DiscoveredEntity, SourceAdapter

log = logging.getLogger(__name__)

_SITEMAP = "https://www.ocasionplus.com/sitemap.concesionarios.xml"
_PREFIX = "https://www.ocasionplus.com/concesionarios/"


def branch_slugs_from_sitemap(xml: str) -> list[str]:
    out: list[str] = []
    for loc in re.findall(r"<loc>([^<]+)</loc>", xml):
        if "/concesionarios/" in loc:
            slug = loc.rstrip("/").rsplit("/", 1)[-1]
            if slug and slug != "concesionarios":
                out.append(slug)
    return out


class OcasionPlusCensusAdapter(SourceAdapter):
    source_key = "ocasionplus_census"

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
        prov = _province_from_postcode(rec.get("postcode"))
        return DiscoveredEntity(
            kind="compraventa", source_key=self.source_key, source_ref=slug,
            legal_name=rec["name"], trade_name=rec["name"],
            province_name=prov, municipality_name=rec.get("city"),
            address=f"ocasionplus:{slug}", postcode=rec.get("postcode"),
            phone=rec.get("phone"), website=None,
            extra={"source_group": "marketplace_census", "vector": 1,
                   "chain": "ocasionplus", "street": rec.get("street"),
                   "profile_url": _PREFIX + slug})

    def fetch(self) -> list[DiscoveredEntity]:
        out: list[DiscoveredEntity] = []
        for slug in self._slug_universe():
            try:
                html = _http_get(_PREFIX + slug)
            except Exception:  # noqa: BLE001
                self.excluded_count += 1
                continue
            rec = parse_profile(html)
            if not rec or not rec.get("name"):
                self.excluded_count += 1
                continue
            out.append(self.entity_from(slug, rec))
        return out
