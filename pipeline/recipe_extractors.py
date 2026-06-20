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
import json

from pipeline.engine.fetch import fetch_text
from pipeline.platform import autocasion_wholesale as ac
from pipeline.platform import coches_com_wholesale as ccom
from pipeline.platform import coches_net_wholesale as ccn
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


def _ccn_valid(v: "ccn.Vehicle") -> bool:
    """A coches.net item is sample-valid iff it carries the two identity fields."""
    return bool(v.listing_ref) and bool(v.deep_link)


class CochesNetExtractor:
    """Recipe-first wrapper over :mod:`pipeline.platform.coches_net_wholesale`.

    coches.net's data layer is an OPEN first-party JSON gateway (POST web.gw.coches.net/search).
    The bounded sample POSTs page-1 (size=k) and parses k items with the module's verified
    ``parse_item_vehicle`` (reuse, NOT a 2nd scraper). ``dealer_ref`` is the platform identity;
    the full faceted drain (province x price band) stays in the wholesale/facet module (VPS)."""

    source = "coches_net"

    def recipe_template(self, dealer_ref: str) -> Recipe:
        return Recipe(
            source=self.source, dealer_ref=dealer_ref, kind="plataforma",
            transport=Transport(engine="curl_cffi", base_url=ccn.ENDPOINT,
                                 impersonate=ccn._IMPERSONATE, timeout_s=ccn._TIMEOUT),
            fingerprint=Fingerprint(user_agent="engine-managed"),
            pagination=Pagination(
                strategy="json_post_page",
                url_template=ccn.ENDPOINT,
                page_size=ccn.PAGE_SIZE,
                declared_path="meta.totalResults",
                stop="declared_reached"),
            parsing=Parsing(
                engine="json_api",
                container_path="items",
                field_map={
                    "deep_link": "_PDP_BASE + url",
                    "listing_ref": "id",
                    "make": "make",
                    "model": "model",
                    "year": "year",
                    "km": "km",
                    "price": "price.amount",
                    "fuel": "fuelType",
                    "transmission": "transmissionTypeId->map",
                    "photo_url": "resources[0]",
                }),
        )

    def sample(self, dealer_ref: str, k: int) -> Sample:
        """POST page-1 (size=k) to the open search gateway and parse the k items (recipe-first:
        a single bounded request, never the faceted full drain — that is the VPS job)."""
        fetcher = ccn.CochesFetcher(pool_size=1)
        data = fetcher.fetch_page(ccn.ENDPOINT, page=1, size=k)
        items = data.get("items") or []
        declared = ccn._to_int((data.get("meta") or {}).get("totalResults"))
        sliced = items[:k]
        fetched = len(sliced)
        parsed = [asdict(ccn.parse_item_vehicle(it)) for it in sliced
                  if _ccn_valid(ccn.parse_item_vehicle(it))]
        full_dealer = declared is not None and declared <= fetched
        return Sample(declared=declared, fetched=fetched, parsed=parsed, full_dealer=full_dealer)


def _ac_valid(v: "ac.Vehicle") -> bool:
    """An autocasion ad is sample-valid iff it carries the two identity fields."""
    return bool(v.listing_ref) and bool(v.deep_link)


class AutocasionExtractor:
    """Recipe-first wrapper over :mod:`pipeline.platform.autocasion_wholesale` (MULTI-STEP).

    autocasion is an OPEN Tier-0 surface (Cloudflare-permissive to a Chrome TLS fingerprint):
    SSR results enumerate ``-ref{id}`` links; each ad is hydrated via a GraphQL ``ad(adId)``
    POST. The bounded sample enumerates page-1, takes k refs, hydrates each with the module's
    verified ``parse_ad`` (reuse, NOT a 2nd scraper). dealer_ref is the platform identity; the
    full enumerate+hydrate drain stays in the wholesale module (VPS)."""

    source = "autocasion"

    def recipe_template(self, dealer_ref: str) -> Recipe:
        return Recipe(
            source=self.source, dealer_ref=dealer_ref, kind="plataforma",
            transport=Transport(engine="curl_cffi", base_url=ac.SSR_HOST,
                                 impersonate=ac._IMPERSONATE, timeout_s=ac._TIMEOUT),
            fingerprint=Fingerprint(user_agent="engine-managed"),
            pagination=Pagination(
                strategy="ssr_enumerate_then_gql_hydrate",
                url_template=ac.SSR_RESULTS + "?page={page}",
                page_size=ac.SSR_ITEMS_PER_PAGE if hasattr(ac, "SSR_ITEMS_PER_PAGE") else 30,
                declared_path="ssr id-set stops changing",
                stop="id_set_stable"),
            parsing=Parsing(
                engine="ssr_ref_re + graphql_ad",
                container_path="data.ad",
                field_map={
                    "deep_link": "_PDP_BASE + url",
                    "listing_ref": "id",
                    "make": "brand.name",
                    "model": "family.name",
                    "year": "year",
                    "km": "kilometers",
                    "price": "price",
                    "fuel": "fuel.name",
                    "transmission": "transmission.name",
                }),
        )

    def sample(self, dealer_ref: str, k: int) -> Sample:
        """Enumerate page-1 SSR refs, take k, hydrate each via the GraphQL ad() POST and parse
        (recipe-first: a bounded enumerate+hydrate, never the full drain — that is the VPS job)."""
        fetcher = ac.AutocasionFetcher()
        html = fetcher.fetch(ac.SSR_RESULTS, method="GET")
        refs = ac.parse_ssr_refs(html)[:k]
        fetched = len(refs)
        parsed = []
        for url, ad_id in refs:
            raw = fetcher.fetch(ac.GQL_ENDPOINT, method="POST",
                                gql={"query": ac._AD_QUERY % int(ad_id)})
            ad = (json.loads(raw).get("data") or {}).get("ad")
            if not ad:
                continue  # un ad que no hidrata = perdida (decide_status lo marca FAILED)
            v = ac.parse_ad(ad, url)
            if _ac_valid(v):
                parsed.append(asdict(v))
        return Sample(declared=None, fetched=fetched, parsed=parsed, full_dealer=False)


EXTRACTORS = {
    "autoscout24": AutoScout24Extractor,
    "web_generic": GenericWebExtractor,
    "coches_com": CochesComExtractor,
    "coches_net": CochesNetExtractor,
    "autocasion": AutocasionExtractor,
}
