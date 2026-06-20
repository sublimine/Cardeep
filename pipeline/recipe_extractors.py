"""Source-specific extractors for the recipe harness.

Each extractor is a thin bridge that (a) declares a DRAFT :class:`Recipe` describing how
the source is scraped, and (b) pulls a bounded :class:`Sample` for the harness to verify.
The heavy lifting is REUSED from the existing, already-verified source modules — an
extractor is glue, not a second scraper.
"""
from __future__ import annotations

from dataclasses import asdict

from pipeline.recipe_harness import Sample
from pipeline.recipe_schema import (
    Fingerprint,
    Pagination,
    Parsing,
    Recipe,
    Transport,
)
from pipeline.recipe_extract_web import GenericWebExtractor
from pipeline.sources import autoscout24 as as24


def _valid(v: as24.Vehicle) -> bool:
    """A parsed vehicle is sample-valid iff it carries the two load-bearing identity
    fields (the deep link and the source vin/ref). Everything else may be legitimately
    absent on a given listing; these two are what dedup + delta key on."""
    return bool(v.vin_ref) and bool(v.deep_link)


class AutoScout24Extractor:
    """Wraps :mod:`pipeline.sources.autoscout24` (open Tier-0, SSR ``__NEXT_DATA__``)."""

    source = "autoscout24"

    def recipe_template(self, dealer_ref: str) -> Recipe:
        return Recipe(
            source=self.source,
            dealer_ref=dealer_ref,
            kind="compraventa",
            transport=Transport(
                engine="http",
                base_url=as24._BASE,
                impersonate=None,
                timeout_s=40),
            fingerprint=Fingerprint(user_agent=as24._UA),
            pagination=Pagination(
                strategy="page_param",
                url_template="/profesionales/{slug}?atype=C&sort=price&desc=1&page={page}",
                page_size=20,
                declared_path="numberOfResults",
                stop="declared_reached"),
            parsing=Parsing(
                engine="next_data",
                container_path="listings",
                field_map={
                    "deep_link": "host + listing.url",
                    "vin_ref": "listing.id",
                    "make": "listing.vehicle.make",
                    "model": "listing.vehicle.model",
                    "year": "listing.firstRegistrationDate|tracking.firstRegistration -> YYYY",
                    "km": "listing.vehicle.mileageInKm|tracking.mileage",
                    "price": "listing.prices.public.priceRaw|tracking.price",
                    "fuel": "listing.vehicle.fuelCategory|fuel",
                    "transmission": "listing.vehicle.transmissionType|transmission",
                    "photo_url": "listing.images[0]",
                }),
        )

    def sample(self, dealer_ref: str, k: int) -> Sample:
        """Pull a bounded k-listing sample from page 1 (recipe-first: never drain the
        whole dealer just to verify the recipe). ``fetched`` is how many raw listings we
        attempted to parse (the k-slice); ``parsed`` are the valid vehicles among them."""
        html = as24.fetch_page(dealer_ref, 1)
        data = as24._next_data(html)
        declared_raw = as24._find(data, "numberOfResults")
        declared = int(declared_raw) if declared_raw is not None else None
        listings = as24._find_listings(data)
        sliced = listings[:k]
        fetched = len(sliced)
        parsed = [asdict(as24.parse_listing_vehicle(raw)) for raw in sliced
                  if _valid(as24.parse_listing_vehicle(raw))]
        # full_dealer: the k-slice contains the dealer's ENTIRE inventory (small dealer)
        # -> only then may `declared` join the VAM quorum (else a subset would falsely refute).
        full_dealer = declared is not None and declared <= fetched
        return Sample(declared=declared, fetched=fetched, parsed=parsed, full_dealer=full_dealer)


EXTRACTORS = {
    "autoscout24": AutoScout24Extractor,
    "web_generic": GenericWebExtractor,
}
