"""Orthogonal-list taxonomy: maps live source_keys to capture-recapture lists.

Two source_keys belong to the same MSE list iff they share a capture mechanism
(and are therefore NOT independent). The buckets below are deliberately coarse:
capture-recapture demands *orthogonal* capture processes, so all digital
marketplaces collapse into one MKT list (they scrape similar dealer feeds), while
physical-geo, official-registry, association-membership and OEM-network are kept
separate because each discovers dealers by a genuinely different mechanism.

Buckets (orthogonality classes):
  GEO     physical-presence catalogues (OSM volunteers, Overture, geo sweep)
  CENSUS  marketplace-as-census (autocasion exhaustive facet census)
  DGT     official administrative registry (DGT authorised centres)
  ASSOC   trade-association membership rolls (AEDRA, AECS, ACEVAS, ...)
  OEM     manufacturer official VO networks (oem_*, brand wholesale)
  MKT     digital classified marketplaces (wallapop, milanuncios, coches.net, ...)

GEO, CENSUS, DGT, ASSOC, OEM are treated as orthogonal MSE lists. MKT is the
non-orthogonal "presence" signal: it is recorded for diagnostics but, because the
project itself is largely seeded from marketplaces, it is excluded from the MSE
list set by default to avoid the dominant-list bias (configurable).
"""

from __future__ import annotations

# Exact source_key -> bucket overrides (checked before prefix rules).
_EXACT: dict[str, str] = {
    "osm": "GEO",
    "overture": "GEO",
    "geo_sweep": "GEO",
    "autocasion_census": "CENSUS",
    "dgt_cat": "DGT",
    "aedra": "ASSOC",
    "aecs": "ASSOC",
    "acevas": "ASSOC",
}

# Orthogonal lists used by the MSE. MKT is intentionally excluded (see module doc).
ORTHOGONAL_LISTS: tuple[str, ...] = ("GEO", "CENSUS", "DGT", "ASSOC", "OEM")

LIST_METADATA: dict[str, tuple[str, str]] = {
    "GEO": ("physical_presence", "Physical-presence catalogues (OSM, Overture, geo sweep)"),
    "CENSUS": ("marketplace_census", "Marketplace-as-census (autocasion exhaustive facet)"),
    "DGT": ("official_registry", "DGT authorised technical/sales centres"),
    "ASSOC": ("association_roll", "Trade-association membership (AEDRA/AECS/ACEVAS)"),
    "OEM": ("oem_network", "Manufacturer official VO networks"),
    "MKT": ("digital_marketplace", "Digital classified marketplaces (non-orthogonal)"),
}


def bucket_for(source_key: str) -> str:
    """Return the orthogonality bucket for a source_key."""
    if source_key in _EXACT:
        return _EXACT[source_key]
    if source_key.startswith("oem_") or source_key.startswith("mercedes"):
        return "OEM"
    if "oficial" in source_key or source_key.endswith("_new_stock"):
        return "OEM"
    # everything else that is a scraped wholesale/marketplace feed
    return "MKT"


def orthogonal_buckets(include_mkt: bool = False) -> tuple[str, ...]:
    """The ordered list of buckets used as MSE lists."""
    if include_mkt:
        return ORTHOGONAL_LISTS + ("MKT",)
    return ORTHOGONAL_LISTS
