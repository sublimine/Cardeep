"""AutoScout24 CENSUS adapter — Vector 1, Tier-1 platform via its OPEN surface (§1).

AutoScout24.es is one of the big Tier-1 marketplaces, but its professional-dealer surface is
OPEN to a plain Chrome UA (SSR ``__NEXT_DATA__`` — verified live, reused by the recipe
harness): no DataDome on ``/lst`` or ``/profesionales/{slug}``. So AS24 can be censused
without the Tier-1 browser engine — a free, deliberate seller census of a major platform.

Enumeration: crawl the public ``/lst`` result pages across several sort orders, collecting the
distinct professional-dealer slugs each listing's ``seller.links.infoPage`` exposes (the more
sorts/pages, the broader the dealer coverage). Each dealer's ``/profesionales/{slug}`` page
carries the full dealer identity (company, postcode→province, city, street, homepage).

Identity dedups PERFECTLY against the as24 harvest dealers: the cdp is minted from
``domain=website + name=company + municipality + address=street + province`` — byte-identical
to ``pipeline.ingest.ingest_dealer``'s cdp_code — so a dealer already harvested collapses on
``ON CONFLICT (cdp_code)``; a new one mints fresh = the census's real contribution.

Run:  python -m pipeline.discover autoscout24_census   (or the batched runner for the full set)
"""
from __future__ import annotations

import logging

from pipeline.sources.autoscout24 import (
    _next_data,
    collect_dealer_slugs,
    fetch_page,
    parse_page_dealer,
)
from pipeline.sources.base import DiscoveredEntity, SourceAdapter

log = logging.getLogger(__name__)

SOURCE_KEY = "autoscout24_census"
# distinct public sort orders broaden which dealers surface in /lst (each sort exposes a
# different slice of the catalogue, hence different sellers).
_SORTS = ("age", "price", "mileage", "standard")


def enumerate_dealer_slugs(max_pages_per_sort: int = 20) -> dict[str, dict]:
    """Union of professional-dealer slugs across several /lst sort orders."""
    dealers: dict[str, dict] = {}
    for sort in _SORTS:
        try:
            part = collect_dealer_slugs(max_pages=max_pages_per_sort, sort=sort)
        except Exception as exc:  # noqa: BLE001 — one sort failing must not abort the whole census
            log.warning("autoscout24_census: sort %s failed (%s)", sort, exc)
            continue
        for slug, meta in part.items():
            dealers.setdefault(slug, meta)
    return dealers


def dealer_entity(slug: str) -> DiscoveredEntity | None:
    """Fetch one dealer's profile page and build its DiscoveredEntity (None if unparseable
    or the postcode is outside the Spanish INE province range)."""
    html = fetch_page(slug, 1)
    info = parse_page_dealer(_next_data(html))
    if info is None or not info.company_name:
        return None
    prov = info.province_code
    if not (prov and prov.isdigit() and "01" <= prov <= "52"):
        prov = None  # bad/foreign postcode -> let geo fallbacks try via city, else honest skip
    return DiscoveredEntity(
        kind="compraventa", source_key=SOURCE_KEY, source_ref=slug,
        legal_name=info.company_name, trade_name=info.company_name,
        province_name=prov, municipality_name=info.city,
        address=info.street, postcode=info.zip,
        website=info.website,  # homepageUrl -> domain cdp dedup with harvested as24 dealers
        extra={"source_group": "marketplace_census", "vector": 1,
               "platform": "autoscout24", "source_dealer_id": info.source_dealer_id,
               "profile_url": f"https://www.autoscout24.es/profesionales/{slug}"})


class AutoScout24CensusAdapter(SourceAdapter):
    source_key = SOURCE_KEY

    def __init__(self, max_pages_per_sort: int = 20, max_dealers: int | None = None) -> None:
        self._max_pages = max_pages_per_sort
        self._max_dealers = max_dealers
        self._slugs: list[str] | None = None
        self.excluded_count = 0

    def slug_universe(self) -> list[str]:
        if self._slugs is None:
            slugs = list(enumerate_dealer_slugs(self._max_pages).keys())
            self._slugs = slugs if self._max_dealers is None else slugs[: self._max_dealers]
        return self._slugs

    def declared_count(self) -> int | None:
        return len(self.slug_universe())

    def fetch(self) -> list[DiscoveredEntity]:
        out: list[DiscoveredEntity] = []
        for slug in self.slug_universe():
            try:
                e = dealer_entity(slug)
            except Exception:  # noqa: BLE001 — a dead/blocked profile is an expected outcome
                self.excluded_count += 1
                continue
            if e is None:
                self.excluded_count += 1
                continue
            out.append(e)
        return out
