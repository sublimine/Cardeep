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
from pipeline.engine.fetch import fetch_text
from pipeline.platform import coches_com_wholesale as ccom
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


def _ccom_valid(v: "ccom.Vehicle") -> bool:
    """A coches.com card is sample-valid iff it carries the two identity fields (deep_link +
    listing_ref) that dedup/delta key on."""
    return bool(v.listing_ref) and bool(v.deep_link)


class CochesComExtractor:
    """Recipe-first wrapper over :mod:`pipeline.platform.coches_com_wholesale`.

    coches.com's SRP is an OPEN Tier-0 ``__NEXT_DATA__`` surface: page-1 carries
    ``classifieds.total`` + a 20-card ``classifiedList``. The bounded sample parses k cards
    with the module's already-verified ``parse_card_vehicle`` (reuse, NOT a 2nd scraper).
    ``dealer_ref`` is the platform identity (platform-as-entity); the full per-make drain
    lives in the wholesale module (VPS) — the harness only proves+persists the recipe here."""

    source = "coches_com"
    _SAMPLE_URL = ccom._SRP_ALL  # page-1 VO SRP: classifieds.total + classifiedList

    def recipe_template(self, dealer_ref: str) -> Recipe:
        return Recipe(
            source=self.source, dealer_ref=dealer_ref, kind="plataforma",
            transport=Transport(engine="curl_cffi", base_url=ccom._SRP_HOST,
                                 impersonate=ccom._IMPERSONATE, timeout_s=30),
            fingerprint=Fingerprint(user_agent="engine-managed"),
            pagination=Pagination(
                strategy="page_param",
                url_template=ccom._SRP_ROOT + "/{make_slug}.htm?page={page}",
                page_size=20,
                declared_path="props.pageProps.classifieds.total",
                stop="declared_reached"),
            parsing=Parsing(
                engine="next_data",
                container_path="props.pageProps.classifieds.classifiedList",
                field_map={
                    "deep_link": "canonical_deep_link(visibleId)",
                    "listing_ref": "visibleId",
                    "make": "make.name",
                    "model": "model.name",
                    "year": "registration.year",
                    "km": "mileage.amount",
                    "price": "price.amount",
                    "photo_url": "image|imageList[0].name",
                }),
        )

    def sample(self, dealer_ref: str, k: int) -> Sample:
        """Pull a bounded k-card sample from page-1 of the open SRP (recipe-first: never drain
        the whole platform just to verify the recipe — that is the VPS job)."""
        html = fetch_text(self._SAMPLE_URL, tier=0)
        cl = ccom.extract_classifieds_any(html)
        if not cl:  # Imperva interstitial / structure drift -> honest empty sample (FAILED)
            return Sample(declared=None, fetched=0, parsed=[], full_dealer=False)
        cards = cl.get("classifiedList") or []
        declared = ccom._to_int(cl.get("total"))
        sliced = cards[:k]
        fetched = len(sliced)
        parsed = [asdict(ccom.parse_card_vehicle(c)) for c in sliced
                  if _ccom_valid(ccom.parse_card_vehicle(c))]
        full_dealer = declared is not None and declared <= fetched
        return Sample(declared=declared, fetched=fetched, parsed=parsed, full_dealer=full_dealer)


EXTRACTORS = {
    "autoscout24": AutoScout24Extractor,
    "web_generic": GenericWebExtractor,
    "coches_com": CochesComExtractor,
}
