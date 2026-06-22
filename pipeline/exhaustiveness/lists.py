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
    # Discovery vectors V3–V6 (pipeline/sources/{dork_municipal,borme_cnae,
    # graph_recursive,collapse_invisible}). DORK and REG are genuinely orthogonal
    # capture mechanisms (programmatic search of own domains; mercantile registry);
    # GRAPH (seeded from already-known sites) and COLLAPSE (resolution, not a new
    # observation) are dependent and kept OUT of the MSE list set on purpose.
    "dork_municipal": "DORK",
    "borme_cnae": "REG",
    "graph_recursive": "GRAPH",
    "collapse_invisible": "COLLAPSE",
}

# Orthogonal lists used by the MSE. MKT/GRAPH/COLLAPSE are intentionally excluded
# (digital-marketplace bias, graph-dependence, and resolution respectively).
ORTHOGONAL_LISTS: tuple[str, ...] = ("GEO", "CENSUS", "DGT", "ASSOC", "OEM", "DORK", "REG")

LIST_METADATA: dict[str, tuple[str, str]] = {
    "GEO": ("physical_presence", "Physical-presence catalogues (OSM, Overture, geo sweep)"),
    "CENSUS": ("marketplace_census", "Marketplace-as-census (autocasion exhaustive facet)"),
    "DGT": ("official_registry", "DGT authorised technical/sales centres"),
    "ASSOC": ("association_roll", "Trade-association membership (AEDRA/AECS/ACEVAS)"),
    "OEM": ("oem_network", "Manufacturer official VO networks"),
    "DORK": ("search_own_domain", "Municipal dorking — dealer-owned domains via search (V3)"),
    "REG": ("mercantile_registry", "BORME mercantile-registry automotive incorporations (V4)"),
    "GRAPH": ("graph_dependent", "Recursive corporate-graph crawl (V5, dependent — non-orthogonal)"),
    "COLLAPSE": ("resolution", "Invisible-vendor collapse (V6, resolution — not an MSE list)"),
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
