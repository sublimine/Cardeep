"""SUBASTAS (car AUCTION / remarketing) group WHOLESALE harvester — the auction group, end to end.

This is the `subastas` source group: the B2B/B2C car AUCTION and remarketing platforms operating in
Spain. Beyond the Tier-1 marketplaces (coches.net/autoscout24/motor.es), the generalist classifieds
(wallapop/milanuncios) and the OEM-VO portals (audi/spoticar/renew/dasweltauto), an auction platform
is a SEPARATE surface: a remarketer that runs timed SALES (auctions / tenders) where the inventory is
fleet/leasing returns sold to professional buyers. It is its OWN source_group, kept apart.

THE GATE, DOCUMENTED HONESTLY (probed live 2026-06-13; docs/architecture/tier1_recipes/subastas_datalayer.md):
the five ES auction operators named in the mandate split cleanly into GATED vs PUBLIC:

  * Autorola (autorola.es)        — Angular SPA shell served from S3; the actual lots/auctions API is
                                    relative-pathed against a runtime base and bidding requires dealer
                                    APPROVAL ("become_approved_to_bid"). NO public lot data layer
                                    (the public site shows only aggregate auction COUNTS, e.g. "9841
                                    Vehículos ofrecidos", never per-lot stock). GATED.
  * BCA España (bca.com / es.bca-europe.com) — B2B only: "solo los profesionales del automóvil pueden
                                    participar … solo las empresas de automoción pueden comprar". The
                                    sale calendar renders but the lots are behind a buyer login. GATED.
  * Allane (allane.de / sixt-leasing) — DE-centric leasing remarketer; no public ES car-stock surface
                                    reachable. GATED.
  * Aucto (aucto.es)              — connection refused / not reachable from here. GATED (unreachable).
  * Ayvens / ALD remarketing (carmarket.ayvens.com) — PUBLIC. The Carmarket site is an Angular
                                    SPA whose data layer is a first-party GraphQL gateway
                                    (api-carmarket.ayvens.com/graphql/saleevents) the browser calls
                                    DIRECTLY. The subscription key it expects is sent CLIENT-SIDE
                                    (x-ald-subscription-key header, present in every browser request —
                                    NOT server-side), so the gateway is reachable key-free to a plain
                                    chrome131 fetch. THIS is the one auction operator that exposes
                                    public stock, in full.

So this connector connects AYVENS CARMARKET (the public member) and documents the gate on the rest —
exactly the mandate's instruction ("if all are gated, document the gate honestly and connect whichever
exposes public lots").

THE SURFACE (Ayvens Carmarket, verified live 2026-06-13):
  POST https://api-carmarket.ayvens.com/graphql/saleevents  -> 200 application/json.
  Headers (all client-side, captured from the live browser request, NOT fabricated):
    x-ald-subscription-key: <client key>   (the Apollo HttpLink auth; sent by the browser itself)
    x-tenant: ald                           (the Ayvens/ALD tenant)
    x-country: es                           (the SPANISH remarketing tenant — its WHOLE catalog)
  Two operations the SPA uses, both key-free to chrome131 with the headers above:
    * `LoadLots`   -> lots(order, take, skip, where) { items{...} aggregates{count} } — the paginated
                      lot list. `aggregates.count` is the EXACT denominator; take/skip drains every lot.
                      Each item: {id, make, model, version, mileage, fuelType, transmissionType,
                      firstRegistrationDate, mainImageUrl, images[], saleEventCountry, saleEventId,
                      fixedPrice, currency, state, endDateTimeUtc}.
    * `saleEvents` -> saleEvents{items{id,country,name,description,reference,type,state,lotsCount}} —
                      the sale-event catalog (the SELLER identities), one call for all sales.

  THE OLD SSR `ng-state` (carmarket.ayvens.com/es-es/lots) embedded only the CURRENTLY-OPEN sales'
  first SSR render window (~37-59 lots) — a tiny snapshot, NOT the catalog. Reading only that was the
  defect this connector fixes: it caged ~27 lots and re-runs added 0. The GraphQL gateway above IS the
  full public surface (no APIM wall: the key rides client-side), so we drain it completely.

  ES SCOPE: `x-country: es` is the SPANISH Ayvens REMARKETING TENANT — its complete sellable inventory
  (3,977 lots / 54 sale events, verified live), regardless of where each car physically sits. This is
  the mandate's "~3,977 ES vehicles across 14+ ES sale events". (A per-lot saleEventCountry=='es' filter
  would instead yield only the ~461 cars physically in Spain across 2 sales — NOT the tenant catalog;
  we deliberately scope to the tenant, the Spanish operator's whole book.)

THE DATA MODEL — the selling point is the SALE EVENT (the auction), mirroring the proven template's
dual-membership EXACTLY (pipeline.platform.coches_net_wholesale / oem_audi_wholesale):

  Ayvens Carmarket (the remarketing platform) -> entity, kind='plataforma'  (+ platform_meta)  [PLATFORM]
  each SALE EVENT (the ES auction sale)        -> entity, kind='subasta'    (national)         [SELLER]
  each LOT (car)                               -> vehicle, OWNED BY its sale event (entity_ulid=sale)
  the lot ON the platform                      -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the sale event — the concrete selling point a buyer bids at); platform
membership is plural (this edge). The SALE EVENT is the right "selling point" for an auction: there is
NO per-lot dealer and NO per-lot province on this surface (an auction lot belongs to a national
remarketing SALE, not a geo-anchored shop). We therefore attribute each car to its real selling point —
the auction sale (saleEventId + reference + name) — and store the sale entity as NATIONAL (province_code
NULL, sentinel '00' in the cdp_code only), the SAME convention the platform entities use. No province is
fabricated.

Multi-axis classification (migrations/0016):
  defense_tier = 't0_open'          (Ayvens GraphQL serves cleanly to chrome131; no WAF challenge)
  source_group = 'official_registry'(the mandate's nearest enum for the distinct AUCTION group; there is
                                     no dedicated 'auction' source_group value — official_registry is the
                                     closest, used for both the platform and its sale-event sellers)
  role         = 'platform' (the Ayvens platform) / 'registry' (each sale event seller)
  kind         = 'plataforma' (platform) / 'subasta' (each sale event)   [migrations/0005 ontology]
  is_tier1     = FALSE              (no WAF fronts the SSR surface)
  family       = 'ayvens_carmarket'(ties the Ayvens auction surface on the family axis)

THE FULL HARVEST. We drain the ENTIRE ES-tenant catalog: `aggregates.count` gives the exact total and
we page LoadLots (take/skip) until every lot is read, then reconcile (lots no longer in the live catalog
are retired to status='gone'/'removed' so no phantom stale lot is counted as live). The denominator is
`aggregates.count` (the gateway's own total) — not a guess.

Engine: POSTs against api-carmarket.ayvens.com routed THROUGH the per-host governor (the same single
choke point coches.net/audi use). The synchronous curl_cffi POST runs in a worker thread so the event
loop is never blocked, and no host is fetched faster than its bucket (api-carmarket.ayvens.com is in the
JSON_API rate class — a first-party JSON gateway built to serve the whole user base, MEASURED permissive
to a full 3,977-lot drain at one IP with zero throttle).

Run: python -m pipeline.platform.group_subastas_wholesale
"""
from __future__ import annotations

import argparse
import sys
import asyncio
import hashlib
import json
import os
import re
from dataclasses import dataclass

import asyncpg
from curl_cffi import requests as cffi_requests

from pipeline.engine.governor import governor, host_of
from pipeline.ids import ulid
from pipeline.delta_guard import should_emit_gone
from pipeline.ops.health import auto_repair, build_origin, fire_alert, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict
from services.api.codes import _base32, cdp_code

DSN = "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
DSN = os.environ.get("CARDEEP_DSN", DSN)

# ---------------------------------------------------------------------------
# Ayvens Carmarket platform identity (the public AUCTION member of the subastas group).
# ---------------------------------------------------------------------------
AYVENS_DOMAIN = "carmarket.ayvens.com"
AYVENS_WEBSITE = "carmarket.ayvens.com"
AYVENS_LEGAL_NAME = "Ayvens Carmarket (ALD Automotive remarketing)"
AYVENS_TRADE_NAME = "Ayvens Carmarket"
AYVENS_SOURCE_KEY = "group_subastas_wholesale"
AYVENS_WAF = "none"                  # SSR serves cleanly to chrome131 (no WAF challenge).
AYVENS_DEFENSE_TIER = "t0_open"      # open SSR surface; only the GraphQL gateway is APIM-keyed.
# The mandate: source_group fits best as a distinct auction group; there is NO dedicated 'auction'
# source_group enum value, so use 'official_registry' (the nearest enum), as instructed.
AYVENS_SOURCE_GROUP = "official_registry"
AYVENS_ROLE = "platform"             # the Ayvens platform's role (each sale event is role='registry').
AYVENS_KIND = "plataforma"           # the platform ENTITY's ontology kind.
AYVENS_FAMILY = "ayvens_carmarket"   # ties the Ayvens auction surface on the family axis.

# The working request (verified live 2026-06-13; recipe subastas_datalayer.md TL;DR). The first-party
# GraphQL gateway behind the Carmarket SPA — the SAME endpoint the browser's Apollo HttpLink posts to.
_API_BASE = "https://api-carmarket.ayvens.com"
GRAPHQL_PATH = "/graphql/saleevents"
ENDPOINT = _API_BASE + GRAPHQL_PATH
_PDP_BASE = "https://carmarket.ayvens.com/es-es/lot/"   # lot detail URL = base + lot id.

# The Apollo HttpLink auth the BROWSER itself sends (captured from the live request 2026-06-13). The key
# is CLIENT-SIDE (present in every browser request — it is NOT a server-side secret; the SPA ships it to
# authenticate the public gateway), x-tenant pins the ALD tenant, x-country pins the SPANISH remarketing
# tenant whose whole catalog we drain. No key is fabricated — these are the headers the public page uses.
_SUBSCRIPTION_KEY = "3b2cc62fd26c4e29a762db3de181266b"
_TENANT = "ald"
ES_COUNTRY = "es"                    # the x-country tenant AND the per-lot saleEventCountry token.
_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-ES,es;q=0.9",
    "Content-Type": "application/json",
    "Origin": "https://carmarket.ayvens.com",
    "Referer": "https://carmarket.ayvens.com/",
    "x-ald-subscription-key": _SUBSCRIPTION_KEY,
    "x-tenant": _TENANT,
    "x-country": ES_COUNTRY,
}
_IMPERSONATE = "chrome131"
_TIMEOUT = 45

# Page size for the LoadLots drain. The gateway tolerates large pages (measured: take=200 drained the
# full 3,977-lot catalog cleanly); 200 keeps the round-trip count low without straining the payload.
_PAGE_SIZE = 200
# Hard ceiling on pages, a runaway guard (3,977 / 200 ≈ 20 pages; 200 pages = 40,000 lots is far past
# any plausible catalog and bounds a pathological gateway loop).
_MAX_PAGES = 200

# The two GraphQL operations the SPA uses. LoadLots = the paginated lot list (items + aggregates.count,
# the exact denominator). saleEvents = the sale-event catalog (the SELLER identities). Field sets are
# the REAL ones captured from the live browser request + verified queryable (fixedPrice/currency/state).
_LOAD_LOTS_QUERY = """
query LoadLots($order: [LotOrderInput!], $take: Int, $skip: Int, $lotFilterInput: LotFilterInput) {
  lots(order: $order, take: $take, skip: $skip, where: $lotFilterInput) {
    items {
      id make model version saleEventCountry saleEventId mileage mileageUnit
      fuelType transmissionType firstRegistrationDate mainImageUrl images
      fixedPrice currency state endDateTimeUtc __typename
    }
    aggregates { count __typename }
    __typename
  }
}
""".strip()

_SALE_EVENTS_QUERY = """
query SaleEvents {
  saleEvents {
    items {
      id country name description reference type state lotsCount __typename
    }
    aggregates { count __typename }
    __typename
  }
}
""".strip()

# The lot filter the SPA's listing uses: exclude finished states (the live, sellable catalog). This is
# the source's own default — the count under it (3,977) is the live ES-tenant denominator.
_LOT_STATE_NIN = ["closed", "withdrawn", "sold"]
_LOT_ORDER = [{"make": "asc"}, {"model": "asc"}, {"version": "asc"}, {"mileage": "asc"}]

# Province sentinel '00' = national (same convention as the platform entities). geo_province has NO
# '00', so a NATIONAL entity stores province_code = NULL; '00' lives only inside the cdp_code string.
# An auction sale event has NO province on this surface — it is a national remarketing sale.
NATIONAL_PROVINCE_SENTINEL = "00"

# fuelType / transmissionType arrive as clean lowercase tokens; map to proper Spanish labels (the same
# finite, verified vocabulary the OEM connectors use — no invention, just the clean source signal).
_FUEL_LABEL = {
    "diesel": "Diésel", "petrol": "Gasolina", "gasoline": "Gasolina", "hybrid": "Híbrido",
    "electric": "Eléctrico", "plugin_hybrid": "Híbrido enchufable", "plug_in_hybrid": "Híbrido enchufable",
    "lpg": "GLP", "cng": "GNC", "hydrogen": "Hidrógeno", "bifuel": "Bifuel", "mild_hybrid": "Microhíbrido",
}
_TRANSMISSION_LABEL = {
    "manual": "Manual", "automatic": "Automático", "auto": "Automático",
    "semi_automatic": "Semiautomático", "semiautomatic": "Semiautomático",
}


def ayvens_platform_cdp_code() -> str:
    """The Ayvens Carmarket platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:carmarket.ayvens.com'), province segment '00' (national). Mirrors
    coches_platform_cdp_code()/audi_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{AYVENS_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{NATIONAL_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Field helpers
# ---------------------------------------------------------------------------


def _to_int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _to_float(v):
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _year_from_reg(reg) -> int | None:
    """firstRegistrationDate is an ISO date 'YYYY-MM-DD' (verified live). Take the year, range-check."""
    if not reg or not isinstance(reg, str):
        return None
    m = re.match(r"(\d{4})", reg.strip())
    if not m:
        return None
    y = int(m.group(1))
    return y if 1900 <= y <= 2100 else None


def _clean_fuel(v) -> str | None:
    if not isinstance(v, str):
        return None
    return _FUEL_LABEL.get(v.strip().lower(), v.strip())


def _clean_transmission(v) -> str | None:
    if not isinstance(v, str):
        return None
    return _TRANSMISSION_LABEL.get(v.strip().lower(), v.strip())


def _first_image(lot: dict) -> str | None:
    """Pick a hosted image. mainImageUrl carries a {size} template placeholder; substitute a concrete
    size so the stored URL is directly usable. Fall back to images[0]."""
    for u in (lot.get("mainImageUrl"), *(lot.get("images") or [])):
        if isinstance(u, str) and u.startswith("http"):
            return u.replace("{size}", "800x600")
    return None


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL response — field names inspected live 2026-06-13, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class SaleRef:
    """The SELLING auction SALE EVENT parsed from a lot's saleEventId + the SaleEventWithLots cache.

    An auction lot's selling point is the SALE (the timed auction/tender it sits in), not a geo-anchored
    dealer — this surface carries no per-lot dealer/province. sale_id is the stable per-sale id; name
    ('ESP - SUBASTA - 4035') and reference ('148986') and type ('openauto'/'tender') identify the sale."""
    sale_id: str
    name: str | None
    reference: str | None
    sale_type: str | None
    description: str | None
    lots_count: int | None


@dataclass
class Vehicle:
    """A car (lot) parsed from a single Ayvens LotWithSaleEvent item."""
    deep_link: str
    listing_ref: str           # Ayvens lot id (the stable dedup key, e.g. '2109467')
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None         # fixedPrice when the sale exposes one (tender/direct-buy); else None.
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    version: str | None


def parse_sale(lot: dict, sale_events: dict[str, dict]) -> SaleRef | None:
    """Parse the SELLING sale event for a lot from saleEventId + the SaleEventWithLots cache.
    Returns None only when there is no sale id (a lot with no concrete selling sale is uncageable)."""
    sale_id = lot.get("saleEventId")
    if not sale_id:
        return None
    sale_id = str(sale_id)
    sev = sale_events.get(sale_id) or {}
    inline = lot.get("saleEvent") or {}
    return SaleRef(
        sale_id=sale_id,
        name=sev.get("name") or inline.get("name"),
        reference=sev.get("reference"),
        sale_type=sev.get("type"),
        description=sev.get("description") or inline.get("description"),
        lots_count=_to_int(sev.get("lotsCount")),
    )


def parse_vehicle(lot: dict) -> Vehicle:
    """Parse the car (lot) from an Ayvens LotWithSaleEvent item (REAL field map)."""
    lot_id = str(lot.get("id") or "")
    deep_link = (_PDP_BASE + lot_id) if lot_id else ""

    make = lot.get("make")
    model = lot.get("model")
    version = lot.get("version")
    # make/model arrive UPPERCASE on the auction surface ('OPEL'/'MOKKA'); title-case for a clean title
    # while preserving the raw make/model in their own columns (downstream normalization handles codes).
    make_t = make.title() if isinstance(make, str) else make
    model_t = model.title() if isinstance(model, str) else model
    title = " ".join(p for p in (make_t, model_t) if p) or None
    if version and isinstance(title, str) and version not in title:
        title = f"{title} {version}".strip()

    km = _to_int(lot.get("mileage"))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    return Vehicle(
        deep_link=deep_link,
        listing_ref=lot_id,
        title=title,
        make=make_t,
        model=model_t,
        year=_year_from_reg(lot.get("firstRegistrationDate")),
        km=km,
        price=_to_float(lot.get("fixedPrice")),  # auction lots usually have NO public price -> None.
        fuel=_clean_fuel(lot.get("fuelType")),
        transmission=_clean_transmission(lot.get("transmissionType")),
        photo_url=_first_image(lot),
        version=version if isinstance(version, str) else None,
    )


# ---------------------------------------------------------------------------
# GraphQL response handling: parse the lots / sale-events payloads (the REAL shapes).
# ---------------------------------------------------------------------------


def parse_lots_payload(payload: dict) -> tuple[list[dict], int | None]:
    """From a LoadLots GraphQL response, return (items, aggregate_count).
    Raises on a GraphQL error or a missing `lots` block so the breaker sees the drift."""
    if not isinstance(payload, dict):
        raise RuntimeError("LoadLots: non-dict payload (gateway drift)")
    if payload.get("errors"):
        raise RuntimeError(f"LoadLots GraphQL errors: {json.dumps(payload['errors'])[:300]}")
    lots = ((payload.get("data") or {}).get("lots")) or None
    if not isinstance(lots, dict):
        raise RuntimeError("LoadLots: no `lots` block in payload (gateway drift)")
    items = [it for it in (lots.get("items") or []) if isinstance(it, dict)]
    count = _to_int((lots.get("aggregates") or {}).get("count"))
    return items, count


def parse_sale_events_payload(payload: dict) -> dict[str, dict]:
    """From a saleEvents GraphQL response, return {sale_id: sale_event_object}. The sale objects carry
    {id, country, name, description, reference, type, state, lotsCount} — the SELLER identity per sale.
    Raises on a GraphQL error so the breaker sees the drift (a sale-less drain is uncageable)."""
    if not isinstance(payload, dict):
        raise RuntimeError("saleEvents: non-dict payload (gateway drift)")
    if payload.get("errors"):
        raise RuntimeError(f"saleEvents GraphQL errors: {json.dumps(payload['errors'])[:300]}")
    block = ((payload.get("data") or {}).get("saleEvents")) or {}
    items = block.get("items") or []
    return {str(it.get("id")): it for it in items
            if isinstance(it, dict) and it.get("id")}


# ---------------------------------------------------------------------------
# Fetch: a POST routed THROUGH the governor (same per-host choke point as coches.net/audi).
# ---------------------------------------------------------------------------


class AyvensFetcher:
    """A POOL of fingerprint-coherent curl_cffi POST sessions for the Ayvens GraphQL gateway.

    Same concurrency-vs-coherence model as the proven fetchers: a single curl_cffi Session is NOT safe
    to call from several threads at once, and the governor runs each fetch in its own worker thread. The
    fix is a bounded POOL — one Session per concurrency slot, each its own Chrome fingerprint + cookie
    jar. The governor's per-host bucket bounds the AGGREGATE rate across every session, so the pool
    widens parallelism WITHOUT out-pacing the host (the choke point is the bucket, never the session
    count). `last_status` reflects the most recent POST across the pool — the breaker's http_status."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def post_graphql(self, url: str, *, body: dict, slot: int = 0) -> dict:
        """The synchronous GraphQL POST on pool session `slot` (runs in a worker thread).

        Handed to governor().wrap_fetch_text: the governor derives the host from `url`, waits on the
        per-host bucket, then runs THIS off the event loop. `slot` and `body` ride as kwargs the governor
        forwards untouched, so each in-flight request POSTs on its own leased, never-shared session
        (thread-safe). Returns the parsed JSON. Raises on a non-200 so the breaker sees a throttle."""
        session = self._sessions[slot]
        # The session is already pinned to _IMPERSONATE in __init__; do NOT re-pass impersonate here
        # (a per-call value would silently override the session fingerprint).
        resp = session.post(url, json=body, headers=_HEADERS, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url}: "
                               f"{resp.content[:200].decode('utf-8', 'replace')}")
        return resp.json()

    async def post_async(self, governed_post, url: str, *, body: dict) -> dict:
        """Lease a pool slot, POST THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_post(url, body=body, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer (mirrors the proven template: ensure platform, bulk-upsert sale-event sellers + vehicles,
# link edge, emit delta, all idempotent ON CONFLICT). Multi-axis 0016 classification set.
# ---------------------------------------------------------------------------

AYVENS_PLATFORM_RECIPE = {
    "version": 2,
    "source": "Ayvens Carmarket (ALD remarketing; carmarket.ayvens.com)",
    "group": "subastas (car auction / remarketing); source_group=official_registry",
    "scope": "platform-wholesale (full ES-tenant catalog; first-party GraphQL gateway LoadLots drain)",
    "engine": "curl_cffi+chrome131_impersonate+graphql(POST json)",
    "access": ("PUBLIC. api-carmarket.ayvens.com/graphql/saleevents is the first-party GraphQL gateway "
               "the Carmarket Angular SPA's Apollo HttpLink calls DIRECTLY. The subscription key it "
               "expects (x-ald-subscription-key) is sent CLIENT-SIDE — it is present in every browser "
               "request, NOT a server-side secret — so the gateway is reachable key-free to a plain "
               "chrome131 POST with that header (+ x-tenant: ald, x-country: es). No WAF challenge, no "
               "proxy/cookie warm-up. defense_tier=t0_open, website_waf=none, is_tier1=FALSE. (The old "
               "SSR `ng-state` on /es-es/lots embedded only a ~37-lot render window — a snapshot, not "
               "the catalog; reading only that was the prior defect.)"),
    "data_surface": "internal_api",
    "surface_intent": "graphql_gateway",
    "endpoint": "POST https://api-carmarket.ayvens.com/graphql/saleevents (operations LoadLots, saleEvents)",
    "request": {
        "headers": ("Content-Type application/json, Accept application/json, "
                    "x-ald-subscription-key <client key>, x-tenant ald, x-country es, "
                    "Origin/Referer https://carmarket.ayvens.com/"),
        "operations": ("LoadLots(order,take,skip,where) -> lots{items{...} aggregates{count}}; "
                       "saleEvents -> saleEvents{items{id,country,name,reference,type,state,lotsCount}}"),
    },
    "enumeration": ("fetch saleEvents ONCE (the seller catalog), then page LoadLots take=200/skip+=take "
                    "to aggregates.count, draining EVERY lot of the x-country=es tenant (the Spanish "
                    "remarketing operation's whole sellable book). Dedup on lot id. Filter "
                    "where.state nin [closed,withdrawn,sold] (the source's own live filter). Lots no "
                    "longer in the live catalog are reconciled to status=gone/removed (no phantom stale)."),
    "denominator": ("LoadLots aggregates.count under the live state filter — the gateway's EXACT total "
                    "for the ES tenant (3,977 verified live 2026-06-13). This is the VAM denominator."),
    "platform_entity": ("kind=plataforma, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=FALSE, defense_tier=t0_open, source_group=official_registry, "
                        "role=platform, family=ayvens_carmarket"),
    "seller_model": ("the SELLING POINT is the SALE EVENT (the auction). Each car -> entity "
                     "kind='subasta' (national; province NULL), canonical_key "
                     "name:'ayvens sale {reference|id}'|p00, source_ref=sale id; role='registry'. "
                     "NO per-lot dealer/province exists on this surface — an auction lot belongs to a "
                     "national remarketing SALE, not a geo-anchored shop. No province is fabricated."),
    "dual_membership": ("vehicle.entity_ulid=SELLING SALE EVENT (subasta); "
                        "platform_listing edge=platform<->vehicle"),
    "field_map": {
        "deep_link": "https://carmarket.ayvens.com/es-es/lot/{lots.items.id}",
        "listing_ref": "lots.items.id (stable lot id + dedup key)",
        "make": "lots.items.make (UPPERCASE on source; title-cased)",
        "model": "lots.items.model",
        "version": "lots.items.version",
        "year": "lots.items.firstRegistrationDate (YYYY-MM-DD -> YYYY)",
        "km": "lots.items.mileage",
        "price": "lots.items.fixedPrice (tender/direct-buy only; pure-auction lots have NO public price -> NULL)",
        "fuel": "lots.items.fuelType (diesel/petrol/... -> Spanish label)",
        "transmission": "lots.items.transmissionType (manual/automatic -> Manual/Automático)",
        "photo_url": "lots.items.mainImageUrl ({size} -> 800x600); fallback images[0]",
        "sale": "lots.items.saleEventId -> saleEvents.items {name, reference, type, description, lotsCount, country}",
        "tenant_scope": "x-country=es header (Spanish remarketing tenant; saleEventCountry is a per-car tally, NOT a gate)",
    },
    "gate_documented": {
        "autorola": "Angular SPA (S3 shell); lots/auctions API relative-pathed, bidding needs dealer approval. GATED.",
        "bca": "B2B only — solo profesionales del automóvil; lots behind buyer login. GATED.",
        "allane": "DE leasing remarketer; no public ES car-stock surface reachable. GATED.",
        "aucto": "connection refused / not reachable. GATED (unreachable).",
        "ayvens": "PUBLIC GraphQL gateway (client-side key) — the one auction operator exposing the full public ES catalog. CONNECTED.",
    },
    "caveats": {
        "full_catalog": "the GraphQL drain caps at aggregates.count (the gateway's exact total) — full catalog, not a slice.",
        "no_geo": "auction lots have NO per-lot province; the sale event is national (province NULL).",
        "no_price": "pure-auction lots expose no public price (bid-based); fixedPrice present only on tenders.",
        "tenant_scope": "ES = the x-country=es tenant (the Spanish operator's whole book); cars may sit in other countries physically.",
        "client_key": "the subscription key is sent CLIENT-SIDE by the browser (not a server secret); we reuse the public key, none fabricated.",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the Ayvens Carmarket platform entity + platform_meta exist. Returns the
    platform entity_ulid. kind='plataforma', is_tier1=FALSE (no WAF fronts the gateway), multi-axis
    0016 classification set explicitly, data_surface='internal_api' (first-party GraphQL gateway JSON)."""
    code = ayvens_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               defense_tier, source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,$3,$4,$5,NULL,$6,$7::waf_kind,FALSE,'active','platform_label',
               $8::defense_tier,$9::source_group,$10::entity_role,$11, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, website_waf = EXCLUDED.website_waf,
               defense_tier = EXCLUDED.defense_tier, source_group = EXCLUDED.source_group,
               role = EXCLUDED.role, legal_name = EXCLUDED.legal_name, kind = EXCLUDED.kind""",
        eulid, code, AYVENS_KIND, AYVENS_LEGAL_NAME, AYVENS_TRADE_NAME, AYVENS_WEBSITE,
        AYVENS_WAF, AYVENS_DEFENSE_TIER, AYVENS_SOURCE_GROUP, AYVENS_ROLE, AYVENS_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, AYVENS_SOURCE_KEY, AYVENS_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'internal_api',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"endpoint": ENDPOINT, "host": host_of(ENDPOINT),
                           "method": "POST", "country": ES_COUNTRY,
                           "operations": ["LoadLots", "saleEvents"],
                           "denominator": "LoadLots.aggregates.count",
                           "surface_intent": "graphql_gateway",
                           "engine": "curl_cffi/chrome131_impersonate"}),
        AYVENS_FAMILY)
    return eulid


# cdp_code() takes province_code for BOTH the CDP-code prefix AND the canonical key's province
# fallback. A national auction sale has NO geo_province row for '00', so we must NOT store '00' in
# entity.province_code (an FK to geo_province). The cdp_code STRING still carries '00' in its prefix
# (free text, no FK) — identical to how the platform entity is minted. _sale_cdp passes province '00'
# only into the code generator (the string), never into the entity row (which stores province NULL).


def _sale_cdp(s: SaleRef) -> str:
    """Mint the SALE EVENT seller's immutable cdp_code: national prefix '00' + canonical key
    name+address(sale id).

    An auction sale has no domain/CIF and no province — its identity is the platform + the stable sale
    reference (or id). We key it as a NATIONAL named entity: name 'Ayvens Carmarket subasta {ref|id}'
    anchored to province '00', with the sale id passed via `address` so two sales that share a display
    name can never collapse. Deterministic over (platform, sale) so re-runs are idempotent."""
    ref = s.reference or s.sale_id
    name = f"Ayvens Carmarket subasta {ref}"
    return cdp_code(province_code=NATIONAL_PROVINCE_SENTINEL, domain=None, name=name,
                    address=f"ayvenssale:{s.sale_id}")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

DEFAULT_CONCURRENCY = 1   # LoadLots pages take/skip sequentially (each page depends on the prior skip);
                          # 1 session is correct. The pool seam stays for fingerprint coherence if widened.


@dataclass
class _CageRow:
    """One fully-parsed car ready for the bulk cage — the in-memory result of the parse phase."""
    sale_cdp: str
    sale_id: str
    sale_name: str | None
    sale_ref: str | None
    sale_type: str | None
    vehicle: Vehicle


# The bulk statements — ONE round-trip per table per window (unnest-based multi-row upsert), byte-for-
# byte the same idempotency the row-by-row path uses. A re-run of an already-harvested window adds 0
# rows and 0 events. Sale-event sellers carry the 0016 axes (official_registry/registry, kind=subasta).

_BULK_UPSERT_SALES = """
INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
        province_code, is_tier1, status, kind_source,
        sells_cars, source_group, role, first_discovered_source, last_seen)
SELECT u.entity_ulid, u.cdp_code, 'subasta'::entity_kind, u.name, u.name,
       NULL, FALSE, 'active', 'platform_label',
       TRUE, 'official_registry'::source_group, 'registry'::entity_role, $4, now()
  FROM unnest($1::text[], $2::text[], $3::text[])
       AS u(entity_ulid, cdp_code, name)
ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()
"""

_BULK_UPSERT_SALE_SOURCES = """
INSERT INTO entity_source (entity_ulid, source_key, source_ref)
SELECT e.entity_ulid, $3, u.source_ref
  FROM unnest($1::text[], $2::text[]) AS u(cdp_code, source_ref)
  JOIN entity e ON e.cdp_code = u.cdp_code
ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()
"""

_BULK_INSERT_VEHICLES = """
INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model,
        year, km, price, fuel, transmission, photo_url, vin_ref, status)
SELECT u.vehicle_ulid, u.entity_ulid, u.deep_link, u.title, u.make, u.model,
       u.year, u.km, u.price, u.fuel, u.transmission, u.photo_url, u.vin_ref, 'available'
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[], $5::text[], $6::text[],
              $7::int[], $8::int[], $9::numeric[], $10::text[], $11::text[], $12::text[],
              $13::text[])
       AS u(vehicle_ulid, entity_ulid, deep_link, title, make, model,
            year, km, price, fuel, transmission, photo_url, vin_ref)
ON CONFLICT (entity_ulid, deep_link) DO NOTHING
"""

_BULK_TOUCH_VEHICLES = """
UPDATE vehicle v SET last_seen = now(), status = 'available'
  FROM unnest($1::text[]) AS u(vehicle_ulid)
 WHERE v.vehicle_ulid = u.vehicle_ulid
"""

_BULK_UPSERT_EDGES = """
INSERT INTO platform_listing (vehicle_ulid, platform_entity_ulid, listing_url,
        listing_ref, platform_price, status, first_seen, last_seen)
SELECT u.vehicle_ulid, $5, u.listing_url, u.listing_ref, u.platform_price,
       'listed', now(), now()
  FROM unnest($1::text[], $2::text[], $3::text[], $4::numeric[])
       AS u(vehicle_ulid, listing_url, listing_ref, platform_price)
ON CONFLICT (vehicle_ulid, platform_entity_ulid)
  DO UPDATE SET last_seen = now(), status = 'listed',
                platform_price = EXCLUDED.platform_price,
                listing_ref = EXCLUDED.listing_ref
RETURNING (xmax = 0) AS inserted
"""

_BULK_INSERT_EVENTS = """
INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type,
        old_value, new_value)
SELECT u.event_ulid, u.vehicle_ulid, u.entity_ulid, 'NEW', NULL, u.new_value::jsonb
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[])
       AS u(event_ulid, vehicle_ulid, entity_ulid, new_value)
"""


def _parse_lots(lots: list[dict], sale_events: dict[str, dict], seen_ids: set,
                harvested_cageable: set, stats: dict) -> list[_CageRow]:
    """Parse every lot of the ES (Spanish Ayvens) tenant — pure CPU, no SQL. Dedup on lot id; sale-event
    attribution. NO per-lot saleEventCountry gate: the ES scope is the x-country tenant (the Spanish
    operator's whole catalog), so every lot the gateway returns under that tenant IS in scope, wherever
    the car physically sits. (`saleEventCountry` is recorded for the per-country tally, never as a gate.)

    `seen_ids` / `harvested_cageable` / `stats` are mutated with deterministic order so the VAM truth
    (distinct (sale_cdp, deep_link) pairs) is exact regardless of batching."""
    rows: list[_CageRow] = []
    for lot in lots:
        stats["items_seen"] += 1
        country = (lot.get("saleEventCountry") or "").lower()
        if country == ES_COUNTRY:
            stats["es_physical_lots"] += 1   # tally only; NOT a gate.
        lot_id = str(lot.get("id") or "")
        if lot_id and lot_id in seen_ids:
            stats["dup_ids_collapsed"] += 1
            continue
        if lot_id:
            seen_ids.add(lot_id)

        s = parse_sale(lot, sale_events)
        if s is None:
            stats["no_sale_skipped"] += 1
            continue
        v = parse_vehicle(lot)
        if not v.deep_link:
            stats["no_link_skipped"] += 1
            continue
        stats["es_lots"] += 1
        if v.price is not None:
            stats["priced_lots"] += 1
        sale_cdp = _sale_cdp(s)
        harvested_cageable.add((sale_cdp, v.deep_link))
        rows.append(_CageRow(
            sale_cdp=sale_cdp, sale_id=s.sale_id, sale_name=s.name, sale_ref=s.reference,
            sale_type=s.sale_type, vehicle=v))
    return rows


async def _ingest_lots(conn: asyncpg.Connection, platform_ulid: str, lots: list[dict],
                       sale_events: dict[str, dict], seen_ids: set, harvested_cageable: set,
                       stats: dict) -> None:
    """BULK-ingest all parsed ES lots in ONE transaction with set-based SQL.

    Mirrors the template's _ingest_window EXACTLY: ONE round-trip per table (unnest multi-row upserts).
    Same ON CONFLICT idempotency, same cageable truth, same NEW-event rule (emitted only for genuinely
    new vehicles). A re-run adds 0 rows and 0 events."""
    cage = _parse_lots(lots, sale_events, seen_ids, harvested_cageable, stats)
    if not cage:
        return

    async with conn.transaction():
        # ---- (2) SALE-EVENT SELLERS: dedup by cdp_code, bulk-upsert, resolve ulids.
        sales: dict[str, _CageRow] = {}
        for r in cage:
            sales.setdefault(r.sale_cdp, r)  # first occurrence wins (deterministic)
        s_ulids = [ulid() for _ in sales]
        s_cdps = list(sales.keys())
        s_names = [f"Ayvens Carmarket subasta {sales[c].sale_ref or sales[c].sale_id}"
                   for c in s_cdps]
        s_refs = [sales[c].sale_id for c in s_cdps]
        await conn.execute(_BULK_UPSERT_SALES, s_ulids, s_cdps, s_names, AYVENS_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_SALE_SOURCES, s_cdps, s_refs, AYVENS_SOURCE_KEY)
        cdp_to_ulid: dict[str, str] = {
            row["cdp_code"]: row["entity_ulid"]
            for row in await conn.fetch(
                "SELECT cdp_code, entity_ulid FROM entity WHERE cdp_code = ANY($1::text[])", s_cdps)
        }

        # ---- attach resolved sale_ulid to each cage row; dedup cars within the batch by
        # (sale_ulid, deep_link) so the same lot seen twice is one car.
        cars: dict[tuple[str, str], _CageRow] = {}
        for r in cage:
            su = cdp_to_ulid.get(r.sale_cdp)
            if su is None:
                continue
            key = (su, r.vehicle.deep_link)
            if key not in cars:
                cars[key] = r

        # ---- (3) VEHICLES: one SELECT splits existing vs new. Existing -> bulk touch.
        car_keys = list(cars.keys())
        v_entity = [k[0] for k in car_keys]
        v_links = [k[1] for k in car_keys]
        existing: dict[tuple[str, str], str] = {
            (row["entity_ulid"], row["deep_link"]): row["vehicle_ulid"]
            for row in await conn.fetch(
                """SELECT vehicle_ulid, entity_ulid, deep_link FROM vehicle
                   WHERE (entity_ulid, deep_link) IN (
                     SELECT * FROM unnest($1::text[], $2::text[]))""",
                v_entity, v_links)
        }

        vehicle_ulid_for: dict[tuple[str, str], str] = {}
        new_keys: list[tuple[str, str]] = []
        touch_ulids: list[str] = []
        for key in car_keys:
            ex = existing.get(key)
            if ex is not None:
                vehicle_ulid_for[key] = ex
                touch_ulids.append(ex)
            else:
                vid = ulid()
                vehicle_ulid_for[key] = vid
                new_keys.append(key)

        if touch_ulids:
            await conn.execute(_BULK_TOUCH_VEHICLES, touch_ulids)

        if new_keys:
            ins = [(vehicle_ulid_for[k], k[0], k[1], cars[k].vehicle) for k in new_keys]
            await conn.execute(
                _BULK_INSERT_VEHICLES,
                [x[0] for x in ins], [x[1] for x in ins], [x[2] for x in ins],
                [x[3].title for x in ins], [x[3].make for x in ins], [x[3].model for x in ins],
                [x[3].year for x in ins], [x[3].km for x in ins], [x[3].price for x in ins],
                [x[3].fuel for x in ins], [x[3].transmission for x in ins],
                [x[3].photo_url for x in ins], [x[3].listing_ref for x in ins])
            landed = {
                (row["entity_ulid"], row["deep_link"]): row["vehicle_ulid"]
                for row in await conn.fetch(
                    """SELECT vehicle_ulid, entity_ulid, deep_link FROM vehicle
                       WHERE vehicle_ulid = ANY($1::text[])""",
                    [vehicle_ulid_for[k] for k in new_keys])
            }
            confirmed_new = []
            for k in new_keys:
                real = landed.get(k)
                if real is not None and real == vehicle_ulid_for[k]:
                    confirmed_new.append(k)
                elif real is not None:
                    vehicle_ulid_for[k] = real  # someone else won the race; adopt their ulid
                else:
                    row = await conn.fetchrow(
                        "SELECT vehicle_ulid FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2",
                        k[0], k[1])
                    if row is not None:
                        vehicle_ulid_for[k] = row["vehicle_ulid"]
        else:
            confirmed_new = []

        stats["cars_caged"] += len(car_keys)
        stats["new_cars"] += len(confirmed_new)

        # ---- (4) EDGES: one batched upsert; RETURNING (xmax=0) counts genuinely new edges.
        e_vehicles = [vehicle_ulid_for[k] for k in car_keys]
        e_urls = [cars[k].vehicle.deep_link for k in car_keys]
        e_refs = [cars[k].vehicle.listing_ref for k in car_keys]
        e_prices = [cars[k].vehicle.price for k in car_keys]
        edge_rows = await conn.fetch(_BULK_UPSERT_EDGES, e_vehicles, e_urls, e_refs,
                                     e_prices, platform_ulid)
        stats["edges_created"] += sum(1 for row in edge_rows if row["inserted"])

        # ---- (5) NEW delta events — only for genuinely new vehicles; sale identity in the payload.
        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                r = cars[k]
                v = r.vehicle
                payload = {"price": v.price, "title": v.title, "platform": AYVENS_TRADE_NAME,
                           "sale": {"id": r.sale_id, "reference": r.sale_ref,
                                    "name": r.sale_name, "type": r.sale_type}}
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities, ev_payloads)
            stats["new_events"] += len(confirmed_new)


async def _seen_vehicle_ulids(conn: asyncpg.Connection, platform_ulid: str,
                              harvested_cageable: set[tuple[str, str]]) -> set[str]:
    """Resolve the harvested (sale_cdp, deep_link) pairs to the vehicle ulids now on Ayvens edges.

    The harvest tracks cageable cars as (sale_cdp, deep_link); after ingest the truth lives in the DB.
    We read the vehicle ulids reachable from the Ayvens platform whose (sale entity, deep_link) matches
    a harvested pair — that exact set is "seen this run". Its complement among the pre-run edge vehicles
    is the aged-out set the reconcile retires. Set-based, ONE query."""
    if not harvested_cageable:
        return set()
    # Materialize ONCE so the two parallel arrays are guaranteed positionally coherent (a set's
    # iteration order is stable within a single pass but building both lists from the same snapshot
    # makes the (cdp, link) pairing immune to any future refactor that iterates twice).
    pairs = list(harvested_cageable)
    cdps = [c for (c, _d) in pairs]
    links = [d for (_c, d) in pairs]
    rows = await conn.fetch(
        """SELECT pl.vehicle_ulid
             FROM platform_listing pl
             JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
             JOIN entity e ON e.entity_ulid = v.entity_ulid
             JOIN unnest($2::text[], $3::text[]) AS h(cdp_code, deep_link)
               ON h.cdp_code = e.cdp_code AND h.deep_link = v.deep_link
            WHERE pl.platform_entity_ulid = $1""",
        platform_ulid, cdps, links)
    return {r["vehicle_ulid"] for r in rows}


async def harvest(concurrency: int = DEFAULT_CONCURRENCY) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    fetcher = AyvensFetcher(pool_size=concurrency)
    stats = {
        "pages_fetched": 0, "items_seen": 0, "es_lots": 0, "es_physical_lots": 0,
        "no_sale_skipped": 0, "no_link_skipped": 0, "priced_lots": 0,
        "new_sales": 0, "cars_caged": 0, "new_cars": 0, "edges_created": 0, "new_events": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "sales_distinct": 0,
        "aggregate_count": None, "es_sales_seen": 0, "retired_vehicles": 0, "retired_listings": 0,
        "gone_suppressed": 0,
        "concurrency": concurrency,
    }
    # Harvest-side truth for the VAM: distinct CAGEABLE cars = distinct (sale_cdp, deep_link) pairs.
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if the breaker is OPEN (a recent ban/throttle still cooling), skip gracefully.
    if await is_open(conn, AYVENS_SOURCE_KEY):
        print(f"[group_subastas_wholesale] breaker OPEN for {AYVENS_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, last snapshot still served).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": AYVENS_SOURCE_KEY}

    gov = governor()
    # The governor's wrap_fetch_text forwards arbitrary kwargs (slot, body) to the wrapped callable
    # untouched, so it governs a POST exactly as it governs a GET — same per-host bucket, same off-loop
    # worker thread. We hand it fetcher.post_graphql so every GraphQL POST is paced by the host bucket.
    governed_post = gov.wrap_fetch_text(fetcher.post_graphql)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = ayvens_platform_cdp_code()
        print(f"[group_subastas_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid}) "
              f"kind={AYVENS_KIND} group={AYVENS_SOURCE_GROUP} tier={AYVENS_DEFENSE_TIER} "
              f"family={AYVENS_FAMILY}")
        print(f"[group_subastas_wholesale] governor paces host {host_of(ENDPOINT)} "
              f"(per-host token bucket, JSON_API class — first-party GraphQL gateway).")
        print(f"[group_subastas_wholesale] PUBLIC member = Ayvens Carmarket (x-country={ES_COUNTRY} "
              f"tenant); gated members (Autorola/BCA/Allane/Aucto) documented in the recipe.")

        seen_ids: set[str] = set()
        sales_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='subasta' AND first_discovered_source=$1",
            AYVENS_SOURCE_KEY)}
        # The vehicle ulids on Ayvens edges BEFORE this run — for the aged-out reconcile at the end.
        vehicles_before = {r["vehicle_ulid"] for r in await conn.fetch(
            "SELECT vehicle_ulid FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)}

        # ---- (1) Fetch the sale-event catalog ONCE: the SELLER identities (name/ref/type/lotsCount).
        sale_events: dict[str, dict] = {}
        try:
            se_payload = await fetcher.post_async(governed_post, ENDPOINT,
                                                  body={"query": _SALE_EVENTS_QUERY})
            sale_events = parse_sale_events_payload(se_payload)
            stats["pages_fetched"] += 1
            print(f"[group_subastas_wholesale] sale-event catalog: {len(sale_events)} sale events.")
        except Exception as e:
            fetch_error = str(e)
            last_http = fetcher.last_status
            print(f"[group_subastas_wholesale] saleEvents fetch failed ({e}); stopping honestly.")

        # ---- (2) Drain EVERY lot of the ES tenant: page LoadLots take/skip to aggregates.count.
        if fetch_error is None:
            skip = 0
            page = 0
            try:
                while page < _MAX_PAGES:
                    body = {
                        "operationName": "LoadLots",
                        "variables": {
                            "order": _LOT_ORDER,
                            "lotFilterInput": {"and": [{"state": {"nin": _LOT_STATE_NIN}}]},
                            "take": _PAGE_SIZE, "skip": skip,
                        },
                        "query": _LOAD_LOTS_QUERY,
                    }
                    payload = await fetcher.post_async(governed_post, ENDPOINT, body=body)
                    stats["pages_fetched"] += 1
                    page += 1
                    items, count = parse_lots_payload(payload)
                    if count is not None and stats["aggregate_count"] is None:
                        stats["aggregate_count"] = count
                        stats["declared_full"] = count   # the gateway's exact total = the denominator.
                        print(f"[group_subastas_wholesale] LoadLots aggregate count (ES tenant): {count}")
                    if not items:
                        break
                    await _ingest_lots(conn, platform_ulid, items, sale_events, seen_ids,
                                       harvested_cageable, stats)
                    print(f"[group_subastas_wholesale] page {page}: +{len(items)} items "
                          f"(skip={skip}); caged so far={stats['cars_caged']} "
                          f"new={stats['new_cars']} edges={stats['edges_created']}")
                    skip += _PAGE_SIZE
                    total = stats["aggregate_count"]
                    if total is not None and skip >= total:
                        break
                if page >= _MAX_PAGES:
                    print(f"[group_subastas_wholesale] WARNING: hit _MAX_PAGES={_MAX_PAGES} guard.")
            except Exception as e:
                fetch_error = fetch_error or str(e)
                last_http = fetcher.last_status
                print(f"[group_subastas_wholesale] LoadLots drain failed ({e}); partial-then-honest stop.")

        # distinct sale events caged across this run = distinct sale_cdp in the harvested cageable set.
        stats["es_sales_seen"] = len({sale_cdp for (sale_cdp, _dl) in harvested_cageable})

        # ---- (3) Reconcile aged-out lots: any Ayvens vehicle NOT seen this run is retired so no
        # phantom stale lot is counted as live. Only runs on a clean full drain (never on a partial
        # fetch_error, which would falsely retire the whole catalog on a transient gateway blip).
        # SAFETY DEPENDENCY (do not break on refactor): the `fetch_error is None` guard is sound ONLY
        # because the SINGLE try/except wrapping the LoadLots `while` above captures BOTH network errors
        # AND _ingest_lots DB errors — so a mid-drain failure (network OR ingest) sets fetch_error and
        # skips this reconcile. If that try/except is ever split, this guard must be revisited or a
        # partial ingest could wrongly retire the un-fetched tail.
        # B2.3: delta guard — blocks GONE sweep on silent partial drains (harvest-ratio check).
        # declared_full = aggregate_count from the GraphQL gateway (the gateway's exact denominator).
        # previous_available = all platform_listing rows before this run (fetched above as vehicles_before).
        _gone_allow, _gone_reason = should_emit_gone(
            harvested=stats["cars_caged"],
            declared=stats["declared_full"],
            previous_available=len(vehicles_before),
        )
        if not _gone_allow:
            stats["gone_suppressed"] = len(vehicles_before)
            print(f"[group_subastas_wholesale] GONE sweep suppressed: {_gone_reason}")
            await fire_alert(
                conn,
                origin=build_origin(AYVENS_SOURCE_KEY, "gone_guard"),
                severity="warning",
                message=f"GONE sweep suppressed (Ayvens/Carmarket): {_gone_reason}",
                payload={"harvested": stats["cars_caged"],
                         "declared": stats["declared_full"],
                         "previous_available": len(vehicles_before)},
            )
        elif fetch_error is None and stats["cars_caged"] > 0:
            seen_vehicle_ulids = {vehicle_ulid_seen
                                  for vehicle_ulid_seen in await _seen_vehicle_ulids(
                                      conn, platform_ulid, harvested_cageable)}
            stale = list(vehicles_before - seen_vehicle_ulids)
            if stale:
                async with conn.transaction():
                    rl = await conn.fetch(
                        """UPDATE platform_listing SET status='removed', last_seen=now()
                            WHERE platform_entity_ulid=$1 AND vehicle_ulid = ANY($2::text[])
                              AND status <> 'removed' RETURNING vehicle_ulid""",
                        platform_ulid, stale)
                    rv = await conn.fetch(
                        """UPDATE vehicle SET status='gone'
                            WHERE vehicle_ulid = ANY($1::text[]) AND status <> 'gone'
                            RETURNING vehicle_ulid""", stale)
                    stats["retired_listings"] = len(rl)
                    stats["retired_vehicles"] = len(rv)
                print(f"[group_subastas_wholesale] reconciled aged-out: retired "
                      f"{stats['retired_listings']} listings / {stats['retired_vehicles']} vehicles.")

        sales_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='subasta' AND first_discovered_source=$1",
            AYVENS_SOURCE_KEY)}
        stats["new_sales"] = len(sales_after - sales_before)
        stats["sales_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, AYVENS_PLATFORM_RECIPE)
        print(f"[group_subastas_wholesale] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths.
        db_edges = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)
        db_join_vehicles = await conn.fetchval(
            """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               JOIN entity d ON d.entity_ulid = v.entity_ulid
               WHERE pl.platform_entity_ulid=$1""", platform_ulid)
        harvested_cageable_n = len(harvested_cageable)
        verdict = await record_count_verdict(
            conn, subject_type="platform_slice", subject_key=platform_code,
            claim="distinct cageable cars (harvest) == platform_listing edges == join-reachable vehicles",
            paths={"db_edges": db_edges, "db_join_vehicles": db_join_vehicles,
                   "harvested_cageable": harvested_cageable_n},
            tolerance=0.0)
        stats["verdict"] = verdict
        stats["db_edges"] = db_edges
        stats["db_join_vehicles"] = db_join_vehicles
        stats["harvested_cageable"] = harvested_cageable_n
        stats["harvested_distinct_ids"] = len(seen_ids)
        stats["platform_code"] = platform_code
        stats["platform_ulid"] = platform_ulid
        stats["recipe_path"] = str(recipe_path)

        # S-HEALTH heartbeat: record THIS run's outcome.
        run_ok = fetch_error is None and stats["cars_caged"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else
                                    (f"VAM verdict {verdict}" if stats["cars_caged"] > 0
                                     else "no lots caged"))
        outcome = await record_run(
            conn, AYVENS_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, AYVENS_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[group_subastas_wholesale] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("SUBASTAS GROUP (AYVENS CARMARKET) WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  group / kind          : official_registry / plataforma (sellers kind=subasta, family ayvens_carmarket)")
    print(f"  public member         : Ayvens Carmarket (Autorola/BCA/Allane/Aucto gated — see recipe)")
    print(f"  declared full (source): {stats.get('declared_full')} (LoadLots aggregate.count, ES tenant)")
    print(f"  sale events caged     : {stats.get('es_sales_seen')} (distinct this run)")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  es-physical tally     : {stats.get('es_physical_lots')} (saleEventCountry=='es'; tally, not a gate)")
    print(f"  no-sale skipped       : {stats['no_sale_skipped']}")
    print(f"  no-link skipped       : {stats['no_link_skipped']}")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')}")
    print(f"  tenant lots caged     : {stats['es_lots']} ({stats['priced_lots']} with a public price)")
    print(f"  sale-event sellers    : {stats['sales_distinct']} distinct ({stats['new_sales']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  aged-out retired      : {stats.get('retired_vehicles')} vehicles / "
          f"{stats.get('retired_listings')} listings")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for Ayvens = {stats.get('db_edges')})")
    print(f"  NEW delta events      : {stats['new_events']}")
    print("  --- VAM count quorum (like-with-like, this slice) ---")
    print(f"  harvested_cageable    : {stats.get('harvested_cageable')}")
    print(f"  db_edges              : {stats.get('db_edges')}")
    print(f"  db_join_vehicles      : {stats.get('db_join_vehicles')}")
    print(f"  VAM verdict           : {stats.get('verdict')}")
    print(f"  health status         : {stats.get('health_status')} / breaker {stats.get('breaker_state')}")
    print(f"  recipe                : {stats.get('recipe_path')}")
    print("=" * 64)


def _force_utf8_stdout() -> None:
    """Windows consoles/pipes default to cp1252, which cannot encode the Σ sign, arrows,
    em-dashes, or the accented car titles this connector prints (Híbrido, Diésel,
    Automática) — a raw print() then crashes the whole drain mid-flight. Reconfigure
    stdout/stderr to UTF-8 (errors='replace') so progress logging can never abort the
    harvest. Idempotent, no-op where already UTF-8."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass


def main() -> None:
    _force_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="subastas group wholesale harvester (Ayvens Carmarket GraphQL LoadLots drain)")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"POST sessions in the pool; default {DEFAULT_CONCURRENCY}. The LoadLots "
                              f"drain pages take/skip sequentially — the governor's per-host bucket is "
                              f"the limiter; the pool only widens fingerprint-coherent parallelism."))
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.concurrency))
    _print_report(stats)


if __name__ == "__main__":
    main()
