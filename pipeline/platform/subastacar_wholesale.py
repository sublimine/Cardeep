"""SUBASTACAR (subastacar.com) — the FREE-PUBLIC member of the b2b_extra_auctions front.

Front `b2b_extra_auctions`: the B2B wholesale + remarketing AUCTION operators serving Spain BEYOND the
three already caged (Autorola / BCA / Ayvens). The mandate named AUTO1, Ucars, Adesa(=OPENLANE),
Manheim ES, Aucto, EpicAuctions, Reezocar, Carmen; the live census (docs/research/segment_census_
b2b_extra_auctions.md, probed 2026-06-13) split them cleanly into GATED vs FREE-PUBLIC:

  * AUTO1.com (auto1.com)        — the buy surface (/es/cars) 302-redirects to /es/merchant/signin: the
                                   whole 30,000-car wholesale stock is behind a PROFESSIONAL login. An
                                   API integration exists but is credentialed. GATED (login-walled).
  * OPENLANE / Adesa (openlane.eu) — /es/findcar is a ~6 KB Angular SPA shell with NO embedded data and
                                   NO public JSON/GraphQL endpoint in the shell; lots require a dealer
                                   login (it is a B2B-only remarketer). GATED (JS SPA + dealer login).
  * Manheim España (manheim.es)  — /vehiculos 404s on the public host; the catalog is behind a buyer
                                   login (B2B remarketer). GATED.
  * Alcopa Auction ES (alcopa-auction.es) — the listing host answers 405/WAF to a plain fetch; B2B. GATED.
  * Aucto (aucto.es)             — DNS does not resolve / connection refused from here. GATED (unreachable).
  * Ucars (ucars.es)             — DNS does not resolve; no reachable Spanish auction operator under the
                                   name (ucars.com is an unrelated generic shell). GATED (unreachable).
  * Reezocar (reezocar.com)      — a FRENCH consumer car-import/sourcing aggregator, not a Spanish B2B
                                   auction operator; the /used-cars path 404s. OUT OF SCOPE (not an ES
                                   auction platform) / no public ES stock surface.
  * "EpicAuctions" / "Carmen"    — no identifiable Spanish car-auction operator resolves under either
                                   name (carmen.io is unrelated). UNREACHABLE / not a real ES auction
                                   surface. Confessed honestly as a hole, not faked.

  * Subastacar (subastacar.com)  — PUBLIC. A Spanish used-car auction marketplace whose ENTIRE catalog
                                   is server-rendered HTML, fully visible to an anonymous chrome131
                                   fetch with NO login. The listing pages paginate via `?pagina=N`
                                   ("238 resultados en 12 Páginas", verified live 2026-06-13) and EACH
                                   detail page embeds a complete schema.org `vehicle` JSON-LD block:
                                   brand, model, VIN, mileageFromOdometer, dateVehicleFirstRegistered,
                                   vehicleEngine.fuelType, vehicleTransmission, bodyType, color, images[]
                                   AND offers.price (an explicit asking price — richer than the bid-gated
                                   Ayvens lot, whose price is NULL). THIS is the one extra auction operator
                                   in the mandate's list that exposes full public stock free, so this
                                   connector connects it; the rest are documented gated above.

THE SURFACE (Subastacar, verified live 2026-06-13):
  LISTING:  GET https://www.subastacar.com/coches-segunda-mano-ocasion/?pagina=N  -> 200 text/html.
            Server-rendered. Each page carries ~21 vehicle detail anchors of the shape
            /coches-segunda-mano-ocasion/comprar-<make>-<slug>-<year>/<hash>. The page label
            "<N> resultados en <P> Páginas" is the EXACT denominator (the site's own total). We page
            until a page yields zero NEW detail links (the natural end), bounded by a runaway guard.
  DETAIL:   GET <detail url> -> 200 text/html with a schema.org `vehicle` JSON-LD <script> the page
            ships for SEO. We parse THAT (not brittle DOM scraping): the structured, first-party field
            map the site itself publishes. price = offers.price; km = mileageFromOdometer.value;
            year = dateVehicleFirstRegistered; fuel = vehicleEngine.fuelType; vin =
            vehicleIdentificationNumber; make = brand.name; model = model; photos = image[].url.

THE DATA MODEL — mirrors the proven dual-membership template (pipeline.platform.group_subastas_wholesale
/ coches_net_wholesale) EXACTLY. Subastacar is a SINGLE auction marketplace (not a calendar of discrete
sale events like Ayvens), so the SELLING POINT is the platform-as-seller itself, modelled as ONE national
auction-house entity (kind='subasta'), the same way a national marketplace with no per-lot dealer is
attributed to a single national seller:

  Subastacar (the auction platform) -> entity kind='plataforma' (+ platform_meta)        [PLATFORM]
  Subastacar (as the SELLING house)  -> entity kind='subasta' (national, province NULL)   [SELLER]
  each LISTING (car)                 -> vehicle OWNED BY the national auction-house seller [CAR]
  the car ON the platform            -> platform_listing edge (platform <-> vehicle)       [EDGE]

Ownership is singular (the national auction house — there is no per-lot geo-anchored dealer on this
surface); platform membership is plural (the edge). The seller is stored NATIONAL (province_code NULL,
sentinel '00' only inside the cdp_code string), the SAME convention the Ayvens sale events and the
platform entities use. No province is fabricated.

Multi-axis classification (migrations/0016), identical axes to the Ayvens auction member:
  defense_tier = 't0_open'           (SSR serves cleanly to chrome131; no WAF/JS challenge)
  source_group = 'official_registry' (the mandate's nearest enum for the distinct AUCTION group; there is
                                      no dedicated 'auction' source_group value)
  role         = 'platform' (the platform) / 'registry' (the auction-house seller)
  kind         = 'plataforma' (platform) / 'subasta' (the auction house)   [migrations/0005 ontology]
  is_tier1     = FALSE               (no WAF fronts the SSR surface)
  family       = 'subastacar'        (ties the Subastacar auction surface on the family axis)

THE FULL HARVEST. We drain the ENTIRE public catalog: page the listing until no new detail link appears,
fetch each detail's JSON-LD, dedup on the listing hash (the stable per-car id in the URL), cage
idempotently (ON CONFLICT), emit a NEW delta only for genuinely new cars, and reconcile aged-out cars
(any Subastacar edge not seen this run -> retired) so no phantom stale listing is counted as live. The
denominator recorded is the site's own "<N> resultados" total — not a guess.

Engine: GETs routed THROUGH the per-host governor (the SAME single choke point coches.net/Ayvens use),
each synchronous curl_cffi GET run in a worker thread so the event loop is never blocked, and no host is
fetched faster than its bucket. www.subastacar.com is a small SSR site (a few hundred cars), drained in
~25 round-trips at a polite pace.

Run: python -m pipeline.platform.subastacar_wholesale
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass

import asyncpg
from curl_cffi import requests as cffi_requests

from pipeline.engine.governor import governor, host_of
from pipeline.ids import ulid
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict
from services.api.codes import _base32, cdp_code

DSN = "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
DSN = os.environ.get("CARDEEP_DSN", DSN)

# ---------------------------------------------------------------------------
# Subastacar platform identity (the FREE-PUBLIC member of the b2b_extra_auctions front).
# ---------------------------------------------------------------------------
SC_DOMAIN = "subastacar.com"
SC_WEBSITE = "subastacar.com"
SC_LEGAL_NAME = "Subastacar (subastas de coches; subastacar.com)"
SC_TRADE_NAME = "Subastacar"
SC_SOURCE_KEY = "subastacar_wholesale"
SC_WAF = "none"                      # SSR serves cleanly to chrome131 (no WAF/JS challenge).
SC_DEFENSE_TIER = "t0_open"          # open SSR surface.
# The mandate: no dedicated 'auction' source_group enum value exists; use 'official_registry' (the
# nearest enum), identical to the Ayvens/Autorola/BCA auction members.
SC_SOURCE_GROUP = "official_registry"
SC_PLATFORM_ROLE = "platform"        # the platform entity's role.
SC_SELLER_ROLE = "registry"          # the auction-house seller entity's role.
SC_PLATFORM_KIND = "plataforma"      # the platform ENTITY's ontology kind.
SC_SELLER_KIND = "subasta"           # the auction-house seller ENTITY's ontology kind.
SC_FAMILY = "subastacar"             # ties the Subastacar auction surface on the family axis.

_BASE = "https://www.subastacar.com"
_LISTING_PATH = "/coches-segunda-mano-ocasion/"
_LISTING_URL = _BASE + _LISTING_PATH

_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": _BASE + "/",
}
_IMPERSONATE = "chrome131"
_TIMEOUT = 45

# Pagination guard: the live catalog is ~12 pages / ~238 cars; 60 pages (~1,260 cars) is far past any
# plausible Subastacar catalog and bounds a pathological loop. We stop earlier on the natural end (a
# page that yields no NEW detail link).
_MAX_PAGES = 60

# A vehicle detail URL: /coches-segunda-mano-ocasion/comprar-<slug>/<hash>  (hash = stable per-car id).
_DETAIL_RE = re.compile(
    r"/coches-segunda-mano-ocasion/comprar-[a-z0-9_\-]+/([0-9a-f]{6,})", re.IGNORECASE)
# The site's own total: "<N> resultados en <P> Páginas" (UTF-8 may arrive mojibake; match loosely).
_TOTAL_RE = re.compile(r"(\d+)\s*resultados\s*en\s*(\d+)\s*[Pp]", re.IGNORECASE)

# fuelType / transmission arrive as clean Spanish labels in the JSON-LD already (Híbrido / Automático);
# normalize the finite, verified vocabulary to the canonical labels the OEM/auction connectors use.
_FUEL_LABEL = {
    "diesel": "Diésel", "diésel": "Diésel", "gasolina": "Gasolina", "petrol": "Gasolina",
    "híbrido": "Híbrido", "hibrido": "Híbrido", "eléctrico": "Eléctrico", "electrico": "Eléctrico",
    "híbrido enchufable": "Híbrido enchufable", "hibrido enchufable": "Híbrido enchufable",
    "glp": "GLP", "gnc": "GNC", "hidrógeno": "Hidrógeno",
}
_TRANSMISSION_LABEL = {
    "manual": "Manual", "automático": "Automático", "automatico": "Automático",
    "semiautomático": "Semiautomático", "semiautomatico": "Semiautomático",
}

NATIONAL_PROVINCE_SENTINEL = "00"


def subastacar_platform_cdp_code() -> str:
    """The Subastacar platform's immutable cdp_code: domain identity, national province '00'. Mirrors
    ayvens_platform_cdp_code()/coches_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{SC_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{NATIONAL_PROVINCE_SENTINEL}-{_base32(digest)}"


def subastacar_seller_cdp_code() -> str:
    """The national auction-house SELLER's immutable cdp_code. Keyed as a NATIONAL named entity (the
    single auction house), province '00' carried in the code string only (no geo_province FK for '00').
    Deterministic, so re-runs are idempotent and the seller is one row, never duplicated."""
    return cdp_code(province_code=NATIONAL_PROVINCE_SENTINEL, domain=None,
                    name="Subastacar subasta", address=f"domain:{SC_DOMAIN}")


# ---------------------------------------------------------------------------
# Field helpers
# ---------------------------------------------------------------------------


def _to_int(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return int(v)
    m = re.search(r"-?\d+", str(v).replace(".", "").replace(",", ""))
    return int(m.group(0)) if m else None


def _to_float(v):
    if v is None:
        return None
    try:
        return float(str(v).replace(".", "").replace(",", ".")) if isinstance(v, str) else float(v)
    except (TypeError, ValueError):
        return None


def _year(v) -> int | None:
    if v is None:
        return None
    m = re.search(r"(\d{4})", str(v))
    if not m:
        return None
    y = int(m.group(1))
    return y if 1900 <= y <= 2100 else None


def _clean_fuel(v) -> str | None:
    if not isinstance(v, str) or not v.strip():
        return None
    return _FUEL_LABEL.get(v.strip().lower(), v.strip())


def _clean_transmission(v) -> str | None:
    if not isinstance(v, str) or not v.strip():
        return None
    return _TRANSMISSION_LABEL.get(v.strip().lower(), v.strip())


# ---------------------------------------------------------------------------
# Parsed shape (from the REAL schema.org JSON-LD field map, inspected live 2026-06-13).
# ---------------------------------------------------------------------------


@dataclass
class Vehicle:
    """A car parsed from a Subastacar detail page's schema.org `vehicle` JSON-LD block."""
    deep_link: str
    listing_ref: str            # the URL hash (the stable per-car dedup key, e.g. '1968d19b3d')
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None         # offers.price (an explicit asking price; richer than bid-gated auctions)
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    version: str | None
    vin: str | None


def _strip_jsonld(raw: str) -> str:
    """Subastacar's JSON-LD ships with stray tabs/newlines and trailing commas before `}` / `]` (the
    site hand-templates it). Make it strict-JSON-parseable: drop the byte-order/replacement junk and
    remove trailing commas. This touches ONLY structural commas, never string content."""
    raw = raw.replace("�", "")  # drop U+FFFD replacement chars from mojibake bytes
    raw = re.sub(r",\s*([}\]])", r"\1", raw)  # trailing comma before } or ]
    return raw


def _extract_vehicle_ld(html: str) -> dict | None:
    """Pull the schema.org `vehicle` JSON-LD object out of a detail page. Returns the parsed dict, or
    None if the page carries no parseable vehicle block (we then skip that car honestly, never fake it)."""
    for m in re.finditer(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html,
            re.IGNORECASE | re.DOTALL):
        blob = m.group(1).strip()
        if '"vehicle"' not in blob.lower():
            continue
        try:
            obj = json.loads(_strip_jsonld(blob))
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and str(obj.get("@type", "")).lower() == "vehicle":
            return obj
    return None


def parse_vehicle(detail_url: str, listing_ref: str, html: str) -> Vehicle | None:
    """Parse a Subastacar car from its detail page's schema.org `vehicle` JSON-LD. Returns None when the
    block is absent/unparseable (the car is skipped honestly — never fabricated from a guess)."""
    ld = _extract_vehicle_ld(html)
    if ld is None:
        return None

    brand = ld.get("brand")
    make = brand.get("name") if isinstance(brand, dict) else (brand if isinstance(brand, str) else None)
    model = ld.get("model") if isinstance(ld.get("model"), str) else None

    engine = ld.get("vehicleEngine")
    fuel_raw = engine.get("fuelType") if isinstance(engine, dict) else None

    odo = ld.get("mileageFromOdometer")
    km = _to_int(odo.get("value") if isinstance(odo, dict) else odo)
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    # Price lives at the LD top level ('price') AND nested in offers.priceSpecification.price (verified
    # live: both carry the same asking price). Prefer the top-level scalar; fall back through the offer.
    price = _to_float(ld.get("price"))
    if price is None:
        offers = ld.get("offers")
        if isinstance(offers, list) and offers:
            offers = offers[0]
        if isinstance(offers, dict):
            price = _to_float(offers.get("price"))
            if price is None:
                spec = offers.get("priceSpecification")
                if isinstance(spec, dict):
                    price = _to_float(spec.get("price"))
    if price is not None and (price <= 0 or price > 100_000_000):
        price = None

    images = ld.get("image")
    photo = None
    if isinstance(images, list):
        for im in images:
            u = im.get("url") if isinstance(im, dict) else (im if isinstance(im, str) else None)
            if isinstance(u, str) and u.startswith("http"):
                photo = u
                break
    elif isinstance(images, str) and images.startswith("http"):
        photo = images

    name = ld.get("name") if isinstance(ld.get("name"), str) else None
    title = " ".join(p for p in (make, model) if p) or name

    return Vehicle(
        deep_link=detail_url,
        listing_ref=listing_ref,
        title=title,
        make=make,
        model=model,
        year=_year(ld.get("dateVehicleFirstRegistered") or ld.get("modelDate")),
        km=km,
        price=price,
        fuel=_clean_fuel(fuel_raw),
        transmission=_clean_transmission(ld.get("vehicleTransmission")),
        photo_url=photo,
        version=None,
        vin=ld.get("vehicleIdentificationNumber") if isinstance(
            ld.get("vehicleIdentificationNumber"), str) else None,
    )


# ---------------------------------------------------------------------------
# Listing parse: detail URLs + the site's own total.
# ---------------------------------------------------------------------------


def parse_listing(html: str) -> tuple[list[tuple[str, str]], int | None]:
    """From a listing page, return ([(detail_url, listing_ref)], declared_total). The detail anchors are
    deduped within the page (the site repeats each card's link in image + title); declared_total is the
    site's own "<N> resultados" figure (the exact denominator) or None if absent on this page."""
    seen: dict[str, str] = {}
    for m in _DETAIL_RE.finditer(html):
        ref = m.group(1)
        path = m.group(0)
        url = path if path.startswith("http") else (_BASE + path)
        seen.setdefault(ref, url)
    pairs = [(url, ref) for ref, url in seen.items()]
    tm = _TOTAL_RE.search(html)
    total = int(tm.group(1)) if tm else None
    return pairs, total


# ---------------------------------------------------------------------------
# Fetch: GETs routed THROUGH the governor (same per-host choke point as coches.net/Ayvens).
# ---------------------------------------------------------------------------


class SubastacarFetcher:
    """A POOL of fingerprint-coherent curl_cffi GET sessions for Subastacar.

    Same concurrency-vs-coherence model as the proven fetchers: a single curl_cffi Session is NOT safe
    to call from several threads at once, and the governor runs each fetch in its own worker thread. The
    fix is a bounded POOL — one Session per concurrency slot. The governor's per-host bucket bounds the
    AGGREGATE rate across every session, so widening the pool never out-paces the host."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def get_text(self, url: str, *, slot: int = 0) -> str:
        """The synchronous GET on pool session `slot` (runs in a worker thread, handed to the governor's
        wrap_fetch_text). Raises on a non-200 so the breaker sees a throttle/ban."""
        session = self._sessions[slot]
        resp = session.get(url, headers=_HEADERS, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url}")
        return resp.text

    async def get_async(self, governed_get, url: str) -> str:
        """Lease a pool slot, GET THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_get(url, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer (mirrors the proven template EXACTLY: ensure platform + national seller, bulk-upsert vehicles,
# link edge, emit NEW delta, reconcile aged-out — all idempotent ON CONFLICT). 0016 axes set explicitly.
# ---------------------------------------------------------------------------

SUBASTACAR_RECIPE = {
    "version": 1,
    "source": "Subastacar (subastas de coches; subastacar.com)",
    "group": "subastas (car auction / remarketing); source_group=official_registry",
    "scope": "platform-wholesale (full public catalog; SSR listing + per-car schema.org JSON-LD)",
    "engine": "curl_cffi+chrome131_impersonate+ssr_html+jsonld",
    "access": ("PUBLIC. The entire catalog is server-rendered HTML visible to an anonymous chrome131 "
               "GET with NO login. Listing /coches-segunda-mano-ocasion/?pagina=N paginates ('<N> "
               "resultados en <P> Páginas'); each detail page embeds a schema.org `vehicle` JSON-LD "
               "block (brand/model/VIN/mileage/year/fuel/transmission/offers.price/images). A 'solo "
               "profesionales' login exists for an iframe bidding portal, but the STOCK itself is fully "
               "public. defense_tier=t0_open, website_waf=none, is_tier1=FALSE."),
    "data_surface": "json_ld",
    "surface_intent": "jsonld",
    "endpoint": "GET https://www.subastacar.com/coches-segunda-mano-ocasion/?pagina=N (listing); "
                "GET <detail url> (schema.org vehicle JSON-LD)",
    "enumeration": ("page the listing ?pagina=N collecting detail anchors "
                    "(/coches-segunda-mano-ocasion/comprar-<slug>/<hash>), stop when a page yields no "
                    "NEW link (natural end) bounded by a runaway guard; dedup on the URL hash; fetch each "
                    "detail and parse its schema.org vehicle JSON-LD. Aged-out cars (a Subastacar edge "
                    "not seen this run) are reconciled to status=gone/removed (no phantom stale)."),
    "denominator": ("the site's own '<N> resultados en <P> Páginas' total (238 verified live "
                    "2026-06-13) — the EXACT denominator, not a guess. This is the VAM denominator."),
    "platform_entity": ("kind=plataforma, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=FALSE, defense_tier=t0_open, source_group=official_registry, "
                        "role=platform, family=subastacar"),
    "seller_model": ("Subastacar is a SINGLE auction marketplace (no calendar of discrete sale events), "
                     "so the selling point is the platform-as-auction-house: ONE national entity "
                     "kind='subasta' (province NULL), role='registry'. Every car is owned by it. No "
                     "per-lot dealer/province exists on this surface; no province is fabricated."),
    "dual_membership": ("vehicle.entity_ulid=national auction-house seller (subasta); "
                        "platform_listing edge=platform<->vehicle"),
    "field_map": {
        "deep_link": "the detail URL",
        "listing_ref": "the URL hash (stable per-car id + dedup key)",
        "make": "ld.brand.name",
        "model": "ld.model",
        "year": "ld.dateVehicleFirstRegistered (YYYY) | ld.modelDate",
        "km": "ld.mileageFromOdometer.value",
        "price": "ld.offers.price (explicit asking price)",
        "fuel": "ld.vehicleEngine.fuelType (-> Spanish label)",
        "transmission": "ld.vehicleTransmission (-> Manual/Automático)",
        "photo_url": "ld.image[0].url",
        "vin": "ld.vehicleIdentificationNumber",
    },
    "gate_documented": {
        "auto1": "buy surface /es/cars 302->/es/merchant/signin; 30k-car stock behind professional login. GATED.",
        "openlane_adesa": "/es/findcar is a ~6KB Angular SPA shell, no public data layer; B2B dealer login. GATED.",
        "manheim_es": "/vehiculos 404 on public host; catalog behind buyer login (B2B). GATED.",
        "alcopa": "listing host answers 405/WAF to a plain fetch; B2B. GATED.",
        "aucto": "DNS does not resolve / connection refused. GATED (unreachable).",
        "ucars": "ucars.es DNS does not resolve; no reachable ES auction operator under the name. UNREACHABLE.",
        "reezocar": "French consumer car-import aggregator, not an ES B2B auction; /used-cars 404s. OUT OF SCOPE.",
        "epicauctions_carmen": "no identifiable ES car-auction operator resolves under either name. UNREACHABLE (confessed).",
        "subastacar": "PUBLIC SSR + schema.org JSON-LD (with offers.price) — the one extra auction op exposing full public stock. CONNECTED.",
    },
    "caveats": {
        "full_catalog": "the drain caps at the site's own '<N> resultados' total — full catalog, not a slice.",
        "no_geo": "auction cars have no per-lot province; the seller is national (province NULL).",
        "single_seller": "one national auction-house seller (no per-lot dealer on this surface).",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the Subastacar platform entity + platform_meta exist. Returns its entity_ulid.
    kind='plataforma', is_tier1=FALSE, 0016 axes set explicitly, data_surface='ssr_html'."""
    code = subastacar_platform_cdp_code()
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
        eulid, code, SC_PLATFORM_KIND, SC_LEGAL_NAME, SC_TRADE_NAME, SC_WEBSITE,
        SC_WAF, SC_DEFENSE_TIER, SC_SOURCE_GROUP, SC_PLATFORM_ROLE, SC_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, SC_SOURCE_KEY, SC_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'json_ld',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"listing": _LISTING_URL, "host": host_of(_LISTING_URL),
                           "method": "GET", "pagination": "?pagina=N",
                           "denominator": "site '<N> resultados' total",
                           "surface_intent": "jsonld",
                           "engine": "curl_cffi/chrome131_impersonate"}),
        SC_FAMILY)
    return eulid


async def ensure_seller_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the single NATIONAL auction-house SELLER entity exists. Returns its
    entity_ulid. kind='subasta', province NULL (national; sentinel '00' in the cdp_code string only),
    role='registry', source_group='official_registry'. Every car is owned by this one seller."""
    code = subastacar_seller_cdp_code()
    eulid = ulid()
    name = "Subastacar subasta"
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, is_tier1, status, kind_source, sells_cars,
               source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,$3::entity_kind,$4,$4,NULL,FALSE,'active','platform_label',TRUE,
               $5::source_group,$6::entity_role,$7, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               source_group = EXCLUDED.source_group, role = EXCLUDED.role, kind = EXCLUDED.kind""",
        eulid, code, SC_SELLER_KIND, name, SC_SOURCE_GROUP, SC_SELLER_ROLE, SC_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, SC_SOURCE_KEY, SC_DOMAIN)
    return eulid


_BULK_INSERT_VEHICLES = """
INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model,
        year, km, price, fuel, transmission, photo_url, vin_ref, status)
SELECT u.vehicle_ulid, $13, u.deep_link, u.title, u.make, u.model,
       u.year, u.km, u.price, u.fuel, u.transmission, u.photo_url, u.vin_ref, 'available'
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[], $5::text[],
              $6::int[], $7::int[], $8::numeric[], $9::text[], $10::text[], $11::text[],
              $12::text[])
       AS u(vehicle_ulid, deep_link, title, make, model,
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


async def _ingest_vehicles(conn: asyncpg.Connection, platform_ulid: str, seller_ulid: str,
                           vehicles: list[Vehicle], harvested: set, stats: dict) -> None:
    """BULK-ingest a batch of parsed cars in ONE transaction with set-based SQL. Mirrors the template's
    _ingest_lots EXACTLY: dedup by deep_link, split existing vs new, bulk insert/touch, batched edge
    upsert (RETURNING xmax=0 counts new edges), NEW delta only for genuinely new cars. Re-run adds 0."""
    if not vehicles:
        return
    # dedup within batch by deep_link (the same car appearing twice is one car).
    by_link: dict[str, Vehicle] = {}
    for v in vehicles:
        if v.deep_link and v.deep_link not in by_link:
            by_link[v.deep_link] = v
            harvested.add(v.deep_link)
    cars = list(by_link.values())
    if not cars:
        return

    async with conn.transaction():
        links = [v.deep_link for v in cars]
        existing: dict[str, str] = {
            row["deep_link"]: row["vehicle_ulid"]
            for row in await conn.fetch(
                "SELECT vehicle_ulid, deep_link FROM vehicle "
                "WHERE entity_ulid=$1 AND deep_link = ANY($2::text[])", seller_ulid, links)
        }

        vehicle_ulid_for: dict[str, str] = {}
        new_links: list[str] = []
        touch_ulids: list[str] = []
        for v in cars:
            ex = existing.get(v.deep_link)
            if ex is not None:
                vehicle_ulid_for[v.deep_link] = ex
                touch_ulids.append(ex)
            else:
                vid = ulid()
                vehicle_ulid_for[v.deep_link] = vid
                new_links.append(v.deep_link)

        if touch_ulids:
            await conn.execute(_BULK_TOUCH_VEHICLES, touch_ulids)

        confirmed_new: list[str] = []
        if new_links:
            ins = [by_link[lk] for lk in new_links]
            await conn.execute(
                _BULK_INSERT_VEHICLES,
                [vehicle_ulid_for[v.deep_link] for v in ins], [v.deep_link for v in ins],
                [v.title for v in ins], [v.make for v in ins], [v.model for v in ins],
                [v.year for v in ins], [v.km for v in ins], [v.price for v in ins],
                [v.fuel for v in ins], [v.transmission for v in ins], [v.photo_url for v in ins],
                [v.vin for v in ins], seller_ulid)
            landed = {
                row["deep_link"]: row["vehicle_ulid"]
                for row in await conn.fetch(
                    "SELECT vehicle_ulid, deep_link FROM vehicle "
                    "WHERE entity_ulid=$1 AND deep_link = ANY($2::text[])", seller_ulid, new_links)
            }
            for lk in new_links:
                real = landed.get(lk)
                if real is not None and real == vehicle_ulid_for[lk]:
                    confirmed_new.append(lk)
                elif real is not None:
                    vehicle_ulid_for[lk] = real  # someone else won the race; adopt their ulid

        stats["cars_caged"] += len(cars)
        stats["new_cars"] += len(confirmed_new)

        # ---- EDGES: one batched upsert; RETURNING (xmax=0) counts genuinely new edges.
        e_vehicles = [vehicle_ulid_for[v.deep_link] for v in cars]
        e_urls = [v.deep_link for v in cars]
        e_refs = [v.listing_ref for v in cars]
        e_prices = [v.price for v in cars]
        edge_rows = await conn.fetch(_BULK_UPSERT_EDGES, e_vehicles, e_urls, e_refs,
                                     e_prices, platform_ulid)
        stats["edges_created"] += sum(1 for row in edge_rows if row["inserted"])

        # ---- NEW delta events — only for genuinely new cars.
        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for lk in confirmed_new:
                v = by_link[lk]
                payload = {"price": v.price, "title": v.title, "platform": SC_TRADE_NAME,
                           "km": v.km, "year": v.year, "vin": v.vin}
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[lk])
                ev_entities.append(seller_ulid)
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities, ev_payloads)
            stats["new_events"] += len(confirmed_new)


async def _reconcile_aged_out(conn: asyncpg.Connection, platform_ulid: str,
                              vehicles_before: set[str], harvested: set[str], stats: dict) -> None:
    """Retire any Subastacar car that was on an edge BEFORE this run but was NOT seen this run, so no
    phantom stale listing is counted as live. Resolves the harvested deep_links to their vehicle ulids;
    the complement among vehicles_before is the aged-out set. ONLY on a clean full drain (the caller
    guards on fetch_error is None) so a transient blip never falsely retires the whole catalog."""
    if not harvested:
        return
    seen_ulids = {
        r["vehicle_ulid"] for r in await conn.fetch(
            """SELECT pl.vehicle_ulid
                 FROM platform_listing pl
                 JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
                 JOIN unnest($2::text[]) AS h(deep_link) ON h.deep_link = v.deep_link
                WHERE pl.platform_entity_ulid = $1""",
            platform_ulid, list(harvested))
    }
    aged = list(vehicles_before - seen_ulids)
    if not aged:
        return
    async with conn.transaction():
        await conn.execute(
            "UPDATE platform_listing SET status='removed', last_seen=now() "
            "WHERE platform_entity_ulid=$1 AND vehicle_ulid = ANY($2::text[])",
            platform_ulid, aged)
        await conn.execute(
            "UPDATE vehicle SET status='gone', last_seen=now() "
            "WHERE vehicle_ulid = ANY($1::text[])", aged)
    stats["retired_listings"] += len(aged)
    stats["retired_vehicles"] += len(aged)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

DEFAULT_CONCURRENCY = 2   # the listing pages are sequential, but detail fetches within a page can run a
                          # couple at a time; the governor's bucket still bounds the aggregate rate.


async def harvest(concurrency: int = DEFAULT_CONCURRENCY) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    fetcher = SubastacarFetcher(pool_size=concurrency)
    stats = {
        "pages_fetched": 0, "detail_links_seen": 0, "details_fetched": 0,
        "no_ld_skipped": 0, "cars_caged": 0, "new_cars": 0, "edges_created": 0, "new_events": 0,
        "declared_full": None, "retired_vehicles": 0, "retired_listings": 0,
        "concurrency": concurrency,
    }
    harvested: set[str] = set()  # deep_links seen this run (for the aged-out reconcile + VAM truth).

    # S-HEALTH gate: if the breaker is OPEN (a recent ban/throttle still cooling), skip gracefully.
    if await is_open(conn, SC_SOURCE_KEY):
        print(f"[subastacar_wholesale] breaker OPEN for {SC_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, last snapshot still served).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": SC_SOURCE_KEY}

    gov = governor()
    governed_get = gov.wrap_fetch_text(fetcher.get_text)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        platform_ulid = await ensure_platform_entity(conn)
        seller_ulid = await ensure_seller_entity(conn)
        platform_code = subastacar_platform_cdp_code()
        print(f"[subastacar_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid}) "
              f"kind={SC_PLATFORM_KIND} group={SC_SOURCE_GROUP} tier={SC_DEFENSE_TIER} "
              f"family={SC_FAMILY}")
        print(f"[subastacar_wholesale] national auction-house seller ready (ulid={seller_ulid}) "
              f"kind={SC_SELLER_KIND}.")
        print(f"[subastacar_wholesale] governor paces host {host_of(_LISTING_URL)} (SSR + JSON-LD).")

        vehicles_before = {r["vehicle_ulid"] for r in await conn.fetch(
            "SELECT vehicle_ulid FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)}

        # ---- (1) Page the listing, collecting detail (url, ref) pairs; stop on the natural end.
        all_pairs: dict[str, str] = {}  # ref -> url, deduped across pages
        try:
            page = 1
            while page <= _MAX_PAGES:
                url = f"{_LISTING_URL}?pagina={page}"
                html = await fetcher.get_async(governed_get, url)
                stats["pages_fetched"] += 1
                pairs, total = parse_listing(html)
                if total is not None and stats["declared_full"] is None:
                    stats["declared_full"] = total
                    print(f"[subastacar_wholesale] site declares {total} resultados (the denominator).")
                new_on_page = 0
                for u, ref in pairs:
                    if ref not in all_pairs:
                        all_pairs[ref] = u
                        new_on_page += 1
                print(f"[subastacar_wholesale] listing page {page}: {len(pairs)} links "
                      f"(+{new_on_page} new; total collected={len(all_pairs)})")
                if new_on_page == 0:
                    break  # natural end: a page added nothing new.
                page += 1
            if page > _MAX_PAGES:
                print(f"[subastacar_wholesale] WARNING: hit _MAX_PAGES={_MAX_PAGES} guard.")
        except Exception as e:
            fetch_error = str(e)
            last_http = fetcher.last_status
            print(f"[subastacar_wholesale] listing pagination failed ({e}); partial-then-honest stop.")

        stats["detail_links_seen"] = len(all_pairs)

        # ---- (2) Fetch each detail, parse its JSON-LD, ingest in batches.
        if all_pairs:
            batch: list[Vehicle] = []
            BATCH = 40
            for ref, url in all_pairs.items():
                try:
                    html = await fetcher.get_async(governed_get, url)
                    stats["details_fetched"] += 1
                except Exception as e:
                    fetch_error = fetch_error or str(e)
                    last_http = fetcher.last_status
                    print(f"[subastacar_wholesale] detail fetch failed ({url}): {e}; stopping honestly.")
                    break
                v = parse_vehicle(url, ref, html)
                if v is None:
                    stats["no_ld_skipped"] += 1
                    continue
                batch.append(v)
                if len(batch) >= BATCH:
                    await _ingest_vehicles(conn, platform_ulid, seller_ulid, batch, harvested, stats)
                    print(f"[subastacar_wholesale] ingested batch: caged so far={stats['cars_caged']} "
                          f"new={stats['new_cars']} edges={stats['edges_created']}")
                    batch = []
            if batch:
                await _ingest_vehicles(conn, platform_ulid, seller_ulid, batch, harvested, stats)
                print(f"[subastacar_wholesale] ingested final batch: caged={stats['cars_caged']} "
                      f"new={stats['new_cars']} edges={stats['edges_created']}")

        # ---- (3) Reconcile aged-out cars — ONLY on a clean full drain (no fetch_error).
        if fetch_error is None:
            await _reconcile_aged_out(conn, platform_ulid, vehicles_before, harvested, stats)
            if stats["retired_vehicles"]:
                print(f"[subastacar_wholesale] retired {stats['retired_vehicles']} aged-out cars.")

        # ---- (4) Health + recipe + count verdict.
        ok = fetch_error is None and stats["cars_caged"] > 0
        if ok:
            await record_run(conn, SC_SOURCE_KEY, ok=True, rows=stats["cars_caged"],
                             http_status=200)
            write_recipe(platform_code, SUBASTACAR_RECIPE)
            # VAM: distinct cars caged this run vs the site's declared total.
            live_edges = await conn.fetchval(
                "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1 "
                "AND status='listed'", platform_ulid)
            paths = {"declared_total": stats["declared_full"] or 0,
                     "harvested_distinct": len(harvested),
                     "live_edges": int(live_edges or 0)}
            try:
                verdict = await record_count_verdict(
                    conn, subject_type="platform", subject_key=platform_code,
                    claim="subastacar_full_catalog", paths=paths, tolerance=0.10)
                stats["count_verdict"] = verdict
            except Exception as e:
                print(f"[subastacar_wholesale] count verdict skipped ({e}).")
        else:
            reason = fetch_error or "no cars caged"
            await record_run(conn, SC_SOURCE_KEY, ok=False, rows=stats["cars_caged"],
                             error=reason[:300], http_status=last_http)
            await auto_repair(conn, SC_SOURCE_KEY, reason[:200], phase="scrape",
                              cdp_code=platform_code, http_status=last_http)

        stats["fetch_error"] = fetch_error
        return stats
    finally:
        await conn.close()


def _print_summary(stats: dict) -> None:
    print("\n========== SUBASTACAR WHOLESALE — SUMMARY ==========")
    for k in ("declared_full", "pages_fetched", "detail_links_seen", "details_fetched",
              "no_ld_skipped", "cars_caged", "new_cars", "edges_created", "new_events",
              "retired_vehicles", "count_verdict", "fetch_error"):
        if k in stats:
            print(f"  {k:20} = {stats[k]}")
    print("====================================================\n")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Subastacar wholesale harvester (b2b_extra_auctions front).")
    p.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    args = p.parse_args(argv)
    stats = asyncio.run(harvest(concurrency=args.concurrency))
    _print_summary(stats)
    return 0 if not stats.get("fetch_error") and stats.get("cars_caged", 0) > 0 else 1


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    raise SystemExit(main())
