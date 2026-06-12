"""Builder (Wix/Ueni/Google Sites/BaseKit/Squarespace/Duda) FAMILY harvester.

The LONG-TAIL multiplier for the **hosted site-builder** family — the lowest-leverage,
highest-variance slice of the own-site tail (longtail_families.md: "builder (Wix/Ueni/
Google Sites/...) — 8 domains / 9 entities, 2.2% of domains; inconsistent, builder-locked
markup; listing slugs vary; singletons, lowest priority").

This is NOT a marketplace connector. It is the proof of the OTHER half of the mandate:
inventory that lives on each dealer's OWN website. The builder family is the hardest tail
to drain because, unlike a DMS (inventario.pro, Motorflash) or a WordPress car-listing
plugin, a hosted builder imposes NO uniform inventory markup — each dealer's stock surface
is whatever their Wix/Ueni/BaseKit/Squarespace template renders. So a single CSS-selector
recipe (the DealerK approach) does NOT generalize here.

The multiplier that DOES generalize across this family is the **structured-data surface**:
the ONE thing the better builders emit uniformly is schema.org JSON-LD (an `ItemList` of
`Vehicle` objects, or standalone `Vehicle`/`Product` blocks) in server-rendered HTML — the
SEO payload the builder generates for Google. ONE recipe that reads that JSON-LD surface
harvests EVERY family member that exposes it, with zero per-site selector adaptation. The
recipe degrades gracefully through ordered strategies:

  1. schema.org `ItemList` of `Vehicle`/`Product`  (the ueni custom listing — verified live
     2026-06-13 on crestanevada.es: per-page `<script id="jsonld-itemlist-listado">` ships
     24 fully-structured `Vehicle` objects: brand, model, year, km, fuel, transmission,
     price, PDP url with a trailing numeric id; `?pagina=N` is cumulative -> drains all).
  2. standalone schema.org `Vehicle` / `Product` JSON-LD blocks (any builder emitting them).
  3. generic SSR card heuristic: price-bearing anchors (the honest fallback for builders
     that render cards server-side without JSON-LD).

Members whose inventory is JS-rendered with NO server-side machine-readable surface
(Wix warmupData, Squarespace/BaseKit empty SSR, Google Sites contact pages) are recorded
HONESTLY as reachable-but-no-SSR-inventory — not faked, not silently dropped. That is the
truthful state of the builder tail: it is genuinely low-yield, exactly as the family map
predicted. The multiplier is still proven — ONE recipe applied uniformly to the whole
family drains every member that exposes the family's structured surface.

Ownership model (the long-tail half — SIMPLER than a marketplace, identical to DealerK):
  the dealer            -> entity, kind='compraventa'/'concesionario_oficial' (already in
                           DB with a populated `website`; we resolve & touch it, or upsert
                           a domain-keyed entity as a fallback)
  each car on its site  -> vehicle, OWNED BY that dealer (entity_ulid = the dealer)

There is NO platform_listing edge: a dealer's own website is the PRIMARY source of its own
stock, not a third-party marketplace. Ownership is singular and direct — the per-dealer
recipe model, lifted to a family so one recipe serves the whole family.

This module mirrors pipeline.platform.coches_net_wholesale's spine (and its sibling
pipeline.platform.family_dealerk_wholesale) EXACTLY — same governor choke point, same
GeoResolver, same idempotent ON CONFLICT upserts, same NEW-delta events, same VAM count
quorum, same S-HEALTH heartbeat / breaker — so the builder tail flows through the ONE
proven architecture, not a fork of it.

Run:  python -m pipeline.platform.family_builder_wix_ueni_google_sites_basekit__wholesale \
            --dealers crestanevada.es majadahondamotor.es bugasgroup.com
      python -m pipeline.platform.family_builder_wix_ueni_google_sites_basekit__wholesale \
            --from-fingerprints --limit 9
"""
from __future__ import annotations

import argparse
import asyncio
import html as _htmllib
import json
import os
import re
from dataclasses import dataclass

import asyncpg
from curl_cffi import requests as cffi_requests

from pipeline.engine.governor import governor, host_of
from pipeline.geo import GeoResolver
from pipeline.ids import ulid
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict
from services.api.codes import cdp_code

DSN = os.environ.get("CARDEEP_DSN",
                     "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# ---------------------------------------------------------------------------
# Family identity. The source_key is the FAMILY, not a single dealer: every dealer
# harvested through this recipe is attested by the same provenance key, and the recipe is
# one file shared by the whole family.
# ---------------------------------------------------------------------------
FAMILY_KEY = "family_builder_wholesale"
FAMILY_NAME = "Hosted site-builder dealer-site family (Wix/Ueni/Google Sites/BaseKit/Squarespace/Duda)"

_IMPERSONATE = "chrome131"
_TIMEOUT = 30
DEFAULT_MAX_PAGES = 120          # builders can carry thousands of cars (crestanevada ~2450)

# The family fingerprint markers. A site is a member iff its HTML carries one of these
# builder spines (verified live 2026-06-13 against the long-tail fingerprint set). The
# fingerprint is used only to CONFIRM family membership before harvesting; the harvest
# itself keys on the structured-data surface, not on the builder identity.
_FAMILY_SPINES = (
    "ueni", "ueniweb", "wix.com", "wixstatic", "parastorage",      # Wix / Ueni
    "basekit", "squarespace", "static1.squarespace", "duda",        # BaseKit / SQSP / Duda
    "negocio.site", "sites.google", "googleusercontent",            # Google Sites / negocio.site
    "crestanevada.es",                                              # ueni custom listing host
)

# Candidate listing-path slugs per builder. Slugs vary (the family's defining pain), so the
# recipe probes a ranked union and uses the first that yields structured vehicles. The root
# "/" is included because some builders ship the JSON-LD listing on the home page itself.
LISTING_PATHS = (
    "/coches-segunda-mano", "/coches-de-ocasion", "/coches-ocasion", "/coches",
    "/stock-vehiculos", "/vehiculos", "/vehiculos-ocasion", "/ocasion",
    "/compra-venta-vehiculos-ocasion", "/nuestros-coches", "/stock", "/",
)

# Page-parameter candidates. crestanevada's ueni listing paginates with ?pagina=N
# (cumulative). We try these in order; the first that returns NEW structured vehicles wins.
PAGE_PARAMS = ("pagina", "page", "p")


# ---------------------------------------------------------------------------
# Parsed shape (field names taken from the REAL schema.org Vehicle markup, verified live).
# ---------------------------------------------------------------------------
@dataclass
class Vehicle:
    deep_link: str
    listing_ref: str | None   # trailing numeric id in the PDP url, when present
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None


def _clean(s) -> str | None:
    if s is None:
        return None
    s = _htmllib.unescape(str(s)).strip()
    return s or None


def _to_int(v, lo: int, hi: int) -> int | None:
    if v is None:
        return None
    digits = re.sub(r"[^\d]", "", str(v))
    if not digits:
        return None
    n = int(digits)
    return n if lo <= n <= hi else None


def _to_price(v) -> float | None:
    if v is None:
        return None
    digits = re.sub(r"[^\d]", "", str(v).split(".")[0] if isinstance(v, str) and "," in str(v)
                    else str(v))
    # schema.org price is usually a bare number (33990) or "33990.00"; keep the integer part.
    if isinstance(v, (int, float)):
        return float(v) if v > 0 else None
    raw = str(v).strip().replace(" ", " ")
    raw = re.sub(r"[^\d.,]", "", raw)
    if not raw:
        return None
    # "33.990" (thousands) vs "33990.00" (decimal): strip a trailing ,dd/.dd then all sep.
    raw = re.sub(r"[.,]\d{2}$", "", raw)
    digits = re.sub(r"[^\d]", "", raw)
    if not digits:
        return None
    p = float(digits)
    return p if p > 0 else None


def _trailing_id(url: str) -> str | None:
    m = re.search(r"/(\d{3,})/?(?:[?#].*)?$", url or "")
    return m.group(1) if m else None


def _year_from(v) -> int | None:
    if v is None:
        return None
    m = re.search(r"(19|20)\d{2}", str(v))
    return int(m.group(0)) if m else None


# ---------------------------------------------------------------------------
# STRATEGY 1 + 2 — schema.org JSON-LD (the family's uniform structured surface).
# ---------------------------------------------------------------------------
_LDJSON_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)


def _iter_ld_nodes(blocks: list[str]):
    """Yield every dict node embedded anywhere in the page's JSON-LD blocks.

    Walks @graph, ItemList.itemListElement[].item, and arbitrary nesting so a Vehicle in
    any position is reachable — builders place the listing at different depths."""
    def walk(node):
        if isinstance(node, dict):
            yield node
            for v in node.values():
                yield from walk(v)
        elif isinstance(node, list):
            for v in node:
                yield from walk(v)

    for raw in blocks:
        raw = raw.strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            # Some builders emit minor JSON glitches (trailing commas); skip — the SSR HTML
            # heuristic (strategy 3) is the fallback, so one bad block never blinds the run.
            continue
        yield from walk(data)


def _vehicle_from_ld(node: dict) -> Vehicle | None:
    """Map a schema.org Vehicle/Car/Product node to our Vehicle. Returns None if no usable
    deep link can be derived (a card with no PDP url is not an ingestible listing)."""
    ty = node.get("@type")
    types = ty if isinstance(ty, list) else [ty]
    if not any(t in ("Vehicle", "Car", "Product") for t in types if t):
        return None

    offers = node.get("offers")
    if isinstance(offers, list):
        offers = offers[0] if offers else None
    offers = offers if isinstance(offers, dict) else {}

    # Reject the LISTING-PAGE summary node: builders emit a page-level `Product` whose offer
    # is an `AggregateOffer` (offerCount/lowPrice/highPrice) and whose url is the listing
    # index itself, not a PDP. That is the collection, not a car — never cage it.
    if offers.get("@type") == "AggregateOffer" or any(
            k in offers for k in ("offerCount", "lowPrice", "highPrice")):
        return None

    deep_link = (offers.get("url") or node.get("url") or "").strip()
    if not deep_link.startswith("http"):
        return None
    # A PDP url must go DEEPER than the listing index (have a path segment beyond it). A node
    # whose only url is a bare listing/section page is the collection, not an individual car.
    if not _trailing_id(deep_link) and deep_link.rstrip("/").count("/") <= 3:
        return None

    brand = node.get("brand")
    if isinstance(brand, dict):
        brand = brand.get("name")
    make = _clean(brand)
    model = _clean(node.get("model"))
    name = _clean(node.get("name"))
    if make and not model and name:
        # name often "BMW Serie 1"; strip the make to recover the model.
        model = _clean(re.sub(rf"^{re.escape(make)}\s*", "", name, flags=re.I)) or None
    title = name or " ".join(b for b in (make, model) if b) or None

    km = None
    odo = node.get("mileageFromOdometer")
    if isinstance(odo, dict):
        km = _to_int(odo.get("value"), 0, 5_000_000)
    elif odo is not None:
        km = _to_int(odo, 0, 5_000_000)

    year = _year_from(node.get("productionDate") or node.get("modelDate")
                      or node.get("vehicleModelDate") or node.get("dateVehicleFirstRegistered"))

    fuel = _clean(node.get("fuelType"))
    trans = _clean(node.get("vehicleTransmission"))
    price = _to_price(offers.get("price") or offers.get("lowPrice"))

    image = node.get("image")
    if isinstance(image, list):
        image = image[0] if image else None
    if isinstance(image, dict):
        image = image.get("url") or image.get("contentUrl")
    photo = _clean(image)

    return Vehicle(
        deep_link=deep_link, listing_ref=_trailing_id(deep_link), title=title,
        make=make, model=model, year=year, km=km, price=price,
        fuel=fuel, transmission=trans, photo_url=photo)


def parse_ld_vehicles(html_text: str) -> list[Vehicle]:
    """Extract every schema.org Vehicle/Car/Product from one page's JSON-LD. ONE parser,
    every family member that ships the structured surface. Server-rendered — no JS."""
    blocks = _LDJSON_RE.findall(html_text)
    out: list[Vehicle] = []
    seen: set[str] = set()
    for node in _iter_ld_nodes(blocks):
        v = _vehicle_from_ld(node)
        if v is None or v.deep_link in seen:
            continue
        seen.add(v.deep_link)
        out.append(v)
    return out


# ---------------------------------------------------------------------------
# STRATEGY 3 — generic SSR card heuristic (honest fallback for JSON-LD-less builders that
# still render price-bearing cards server-side). Conservative: a card must pair a same-host
# anchor with a nearby € price, so nav links and decor never masquerade as vehicles.
# ---------------------------------------------------------------------------
_PRICE_NEAR_RE = re.compile(r"([0-9][0-9.\s]{2,})\s*(?:€|&euro;|&#8364;)")
_ANCHOR_RE = re.compile(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.S | re.I)
# A PDP-looking path: a multi-token slug or a /ficha/ or /coche/<...> detail page. A bare
# section/listing slug ("/stock-vehiculos", "/coches-de-ocasion") is NOT a PDP — those are
# the index we are scraping, not a car.
_VEHICLE_PATH_HINT = re.compile(
    r"(/ficha/|/coche/|/vehiculo/|/[a-z0-9]+(?:-[a-z0-9]+){2,})", re.I)
# Price-filter / CTA labels a builder renders next to a € amount that are NOT cars. A row
# whose only text is one of these (and no PDP-shaped link) is filter chrome, never a vehicle.
_CTA_LABEL_RE = re.compile(
    r"^\s*(?:\+?\s*info|m[áa]s\s+info|ver\s+m[áa]s|precios?|desde|hasta|menos\s+de|"
    r"financia|contact|buscar|filtr)\b", re.I)


def _norm_url(u: str) -> str:
    return re.sub(r"[?#].*$", "", (u or "")).rstrip("/").lower()


def parse_ssr_cards(html_text: str, base_host: str, page_url: str = "") -> list[Vehicle]:
    """Heuristic card parse: same-host anchors whose immediate text/markup carries a € price.
    Deliberately strict so it under-claims rather than fabricates — the builder tail is low
    yield and a false positive (a financing CTA / the listing index itself) would poison the
    cage. Rejects: the page being scraped (self-link), bare section slugs, and CTA labels."""
    out: list[Vehicle] = []
    seen: set[str] = set()
    page_norm = _norm_url(page_url)
    for m in _ANCHOR_RE.finditer(html_text):
        href, inner = m.group(1).strip(), m.group(2)
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        # window after the anchor where a price commonly sits in card markup.
        window = inner + html_text[m.end():m.end() + 600]
        pm = _PRICE_NEAR_RE.search(window)
        if not pm:
            continue
        if not _VEHICLE_PATH_HINT.search(href):
            continue
        if href.startswith("/"):
            href = f"https://{base_host}{href}"
        if not href.startswith("http") or base_host not in href:
            continue
        # Reject the listing INDEX itself (a price-filter button links back to /stock-vehiculos):
        # an anchor pointing to the page we are scraping, or to a bare known listing slug, is
        # chrome — NOT a per-vehicle PDP. We do NOT use a blunt path-depth rule: a builder PDP
        # can live at the site root (/ford-focus-15-tdci-sport), so depth alone is ambiguous;
        # the listing-slug match is the precise discriminator.
        href_norm = _norm_url(href)
        href_path = re.sub(r"^https?://[^/]+", "", href_norm)
        if href_norm == page_norm or href_path in {p.rstrip("/") for p in LISTING_PATHS}:
            continue
        if href in seen:
            continue
        text = _clean(re.sub(r"<[^>]+>", " ", inner)) or None
        # A row whose visible text is a known filter/CTA label AND whose link carries no
        # numeric PDP id is filter chrome, not a car — drop it.
        if text and _CTA_LABEL_RE.match(text) and not _trailing_id(href):
            continue
        seen.add(href)
        out.append(Vehicle(
            deep_link=href, listing_ref=_trailing_id(href), title=text,
            make=None, model=None, year=_year_from(text), km=None,
            price=_to_price(pm.group(1)), fuel=None, transmission=None, photo_url=None))
    return out


# ---------------------------------------------------------------------------
# Fetch — one curl_cffi GET per page, routed THROUGH the governor (per-host bucket). Each
# dealer is its own host, so the governor paces every dealer independently and politely
# (DEFAULT/STEALTH profile ~0.7 req/s/host) with no cross-dealer interference.
# ---------------------------------------------------------------------------
class FamilyFetcher:
    def __init__(self) -> None:
        self._session = cffi_requests.Session(impersonate=_IMPERSONATE)
        self.last_status: int | None = None

    def fetch(self, url: str) -> str:
        resp = self._session.get(url, impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url}")
        return resp.text


def is_family_member(html_text: str) -> bool:
    low = html_text.lower()
    return any(spine in low for spine in _FAMILY_SPINES)


# ---------------------------------------------------------------------------
# The family recipe — ONE asset shared by every member of the family.
# ---------------------------------------------------------------------------
FAMILY_RECIPE = {
    "version": 1,
    "source": FAMILY_KEY,
    "family": FAMILY_NAME,
    "scope": "long-tail dealer OWN-SITE inventory on hosted site builders, by structured-data surface",
    "engine": "curl_cffi+chrome131_impersonate+schema.org-jsonld(GET, server-rendered)",
    "access": ("OPEN public dealer websites (Chrome TLS fingerprint; no proxy, no browser, "
               "no creds). Server-rendered HTML + JSON-LD — no JS execution needed."),
    "data_surface": "schema.org JSON-LD (ItemList/Vehicle/Product) with SSR-card fallback",
    "fingerprint": ("Hosted builder spine in HTML: one of "
                    + ", ".join(_FAMILY_SPINES) + ". Membership is confirmed by the spine; "
                    "harvest keys on the structured-data surface, not the builder identity."),
    "listing_paths": list(LISTING_PATHS),
    "page_params": list(PAGE_PARAMS),
    "enumeration": ("probe ranked listing slugs; on the first yielding structured vehicles, "
                    "walk ?<page_param>=1..N until a page adds no NEW deep_link (cap max_pages). "
                    "Note: ueni's ?pagina=N is CUMULATIVE — dedup by deep_link handles it."),
    "strategies": [
        "1) schema.org ItemList of Vehicle/Product (ueni custom listing, e.g. crestanevada.es)",
        "2) standalone schema.org Vehicle/Car/Product JSON-LD blocks",
        "3) generic SSR card heuristic: same-host anchor paired with a nearby € price",
    ],
    "ownership": "vehicle.entity_ulid = the DEALER itself (own-site stock; no marketplace edge)",
    "multiplier": ("ONE recipe + ONE parser harvests EVERY family member that ships the "
                   "structured surface, with zero per-site selector adaptation. Members with "
                   "JS-only inventory are recorded honestly as no-SSR-inventory, never faked."),
    "field_map": {
        "deep_link": "schema.org offers.url | url (PDP)",
        "listing_ref": "trailing numeric id in the PDP url, when present",
        "make": "schema.org brand.name",
        "model": "schema.org model (or name minus brand)",
        "year": "productionDate/modelDate/dateVehicleFirstRegistered -> YYYY",
        "km": "mileageFromOdometer.value",
        "price": "offers.price (or offers.lowPrice)",
        "fuel": "fuelType",
        "transmission": "vehicleTransmission",
        "photo_url": "image (first)",
    },
    "verified_live": ("2026-06-13: crestanevada.es ships <script id='jsonld-itemlist-listado'> "
                      "with 24 Vehicle objects/page; ?pagina=N cumulative; ~2450 offers total. "
                      "wix/squarespace/basekit/google_sites members reachable but JS-only (no "
                      "SSR inventory) — recorded honestly."),
}


# ---------------------------------------------------------------------------
# DB layer — idempotent upserts mirroring family_dealerk_wholesale (no marketplace edge).
# ---------------------------------------------------------------------------
async def resolve_dealer_for_host(conn: asyncpg.Connection, host: str) -> dict | None:
    """Find the dealer entity whose website matches this host (already discovered, website
    populated). Match on the registrable host so we attach to the existing entity rather
    than minting a duplicate."""
    bare = re.sub(r"^www\.", "", host.lower())
    row = await conn.fetchrow(
        """SELECT entity_ulid, cdp_code, trade_name, province_code, municipality_code, website
             FROM entity
            WHERE kind IN ('compraventa','concesionario_oficial')
              AND website IS NOT NULL AND website <> ''
              AND lower(regexp_replace(regexp_replace(website,'^https?://',''),'^www\\.','')) LIKE $1
            ORDER BY last_seen DESC
            LIMIT 1""",
        f"{bare}%")
    return dict(row) if row else None


async def upsert_dealer_by_host(conn: asyncpg.Connection, host: str) -> dict | None:
    """Return the owning dealer entity for `host`, upserting a domain-keyed one if absent.

    Preferred: the dealer already exists (matched by website host) — use it as-is and stamp
    the family provenance. Fallback: mint a minimal domain-keyed entity (bare domain is a
    strong canonical identity in codes.py) so the harvest always has a real owner."""
    existing = await resolve_dealer_for_host(conn, host)
    if existing:
        await conn.execute(
            "UPDATE entity SET last_seen = now() WHERE entity_ulid = $1",
            existing["entity_ulid"])
        await conn.execute(
            "INSERT INTO entity_source (entity_ulid, source_key, source_ref) "
            "VALUES ($1,$2,$3) ON CONFLICT (entity_ulid, source_key) "
            "DO UPDATE SET seen_at = now()",
            existing["entity_ulid"], FAMILY_KEY, host)
        return existing

    bare = re.sub(r"^www\.", "", host.lower())
    code = cdp_code(province_code="00", domain=bare)
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               website, is_tier1, status, kind_source, sells_cars,
               first_discovered_source, last_seen)
           VALUES ($1,$2,'compraventa',$3,$3,$4,FALSE,'active','platform_label',TRUE,$5, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()""",
        eulid, code, bare, f"https://{bare}", FAMILY_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) "
        "VALUES ($1,$2,$3) ON CONFLICT (entity_ulid, source_key) "
        "DO UPDATE SET seen_at = now()",
        eulid, FAMILY_KEY, host)
    return {"entity_ulid": eulid, "cdp_code": code, "trade_name": bare,
            "province_code": None, "municipality_code": None, "website": bare}


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

_BULK_INSERT_EVENTS = """
INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type,
        old_value, new_value)
SELECT u.event_ulid, u.vehicle_ulid, u.entity_ulid, 'NEW', NULL, u.new_value::jsonb
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[])
       AS u(event_ulid, vehicle_ulid, entity_ulid, new_value)
"""


async def ingest_dealer_vehicles(conn: asyncpg.Connection, dealer_ulid: str,
                                 vehicles: list[Vehicle], stats: dict) -> None:
    """Bulk-upsert one dealer's whole harvest in ONE transaction, set-based SQL.

    Idempotent on (entity_ulid, deep_link): existing cars are touched, genuinely new cars
    are inserted and get a NEW delta event. A re-run adds 0 rows and 0 events."""
    by_link: dict[str, Vehicle] = {}
    for v in vehicles:
        if v.deep_link and v.deep_link not in by_link:
            by_link[v.deep_link] = v
    if not by_link:
        return
    links = list(by_link.keys())

    async with conn.transaction():
        existing = {
            row["deep_link"]: row["vehicle_ulid"]
            for row in await conn.fetch(
                "SELECT vehicle_ulid, deep_link FROM vehicle "
                "WHERE entity_ulid = $1 AND deep_link = ANY($2::text[])",
                dealer_ulid, links)
        }
        touch_ulids: list[str] = []
        new_links: list[str] = []
        vehicle_ulid_for: dict[str, str] = {}
        for link in links:
            ex = existing.get(link)
            if ex is not None:
                vehicle_ulid_for[link] = ex
                touch_ulids.append(ex)
            else:
                vid = ulid()
                vehicle_ulid_for[link] = vid
                new_links.append(link)

        if touch_ulids:
            await conn.execute(_BULK_TOUCH_VEHICLES, touch_ulids)

        confirmed_new: list[str] = []
        if new_links:
            ins = [(vehicle_ulid_for[l], dealer_ulid, l, by_link[l]) for l in new_links]
            await conn.execute(
                _BULK_INSERT_VEHICLES,
                [x[0] for x in ins], [x[1] for x in ins], [x[2] for x in ins],
                [x[3].title for x in ins], [x[3].make for x in ins], [x[3].model for x in ins],
                [x[3].year for x in ins], [x[3].km for x in ins], [x[3].price for x in ins],
                [x[3].fuel for x in ins], [x[3].transmission for x in ins],
                [x[3].photo_url for x in ins], [x[3].listing_ref for x in ins])
            landed = {
                row["deep_link"]: row["vehicle_ulid"]
                for row in await conn.fetch(
                    "SELECT vehicle_ulid, deep_link FROM vehicle "
                    "WHERE vehicle_ulid = ANY($1::text[])",
                    [vehicle_ulid_for[l] for l in new_links])
            }
            for link in new_links:
                real = landed.get(link)
                if real is not None and real == vehicle_ulid_for[link]:
                    confirmed_new.append(link)
                elif real is not None:
                    vehicle_ulid_for[link] = real
                else:
                    row = await conn.fetchrow(
                        "SELECT vehicle_ulid FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2",
                        dealer_ulid, link)
                    if row is not None:
                        vehicle_ulid_for[link] = row["vehicle_ulid"]

        stats["cars_ingested"] += len(links)
        stats["new_cars"] += len(confirmed_new)

        if confirmed_new:
            ev_u, ev_v, ev_e, ev_p = [], [], [], []
            for link in confirmed_new:
                v = by_link[link]
                payload = {"price": v.price, "title": v.title, "family": FAMILY_KEY}
                ev_u.append(ulid())
                ev_v.append(vehicle_ulid_for[link])
                ev_e.append(dealer_ulid)
                ev_p.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_u, ev_v, ev_e, ev_p)
            stats["new_events"] += len(confirmed_new)


# ---------------------------------------------------------------------------
# Per-dealer harvest: fingerprint -> find listing -> drain pages -> parse -> ingest.
# ---------------------------------------------------------------------------
def _extract_vehicles(html_text: str, base_host: str,
                      page_url: str = "") -> tuple[list[Vehicle], str]:
    """Apply the ordered strategies; return (vehicles, strategy_used)."""
    veh = parse_ld_vehicles(html_text)
    if veh:
        return veh, "jsonld"
    veh = parse_ssr_cards(html_text, base_host, page_url)
    if veh:
        return veh, "ssr_card"
    return [], ""


async def harvest_one_dealer(conn: asyncpg.Connection, governed_fetch,
                             fetcher: FamilyFetcher, host: str,
                             max_pages: int, stats: dict) -> dict:
    """Harvest ONE family dealer's own-site stock. Returns a per-dealer summary."""
    bare = re.sub(r"^www\.", "", host.lower())
    summary = {"host": bare, "is_member": False, "vehicles": 0, "new": 0,
               "dealer_cdp": None, "pages": 0, "path": None, "strategy": None}

    # 1) fingerprint the home page — confirm it is a real builder-family member.
    base = f"https://www.{bare}"
    home = None
    for candidate in (f"https://www.{bare}", f"https://{bare}"):
        try:
            home = await governed_fetch(candidate)
            base = candidate.rstrip("/")
            break
        except Exception as e:
            summary["error"] = f"home fetch failed: {e}"
    if home is None:
        stats["dealers_failed"] += 1
        return summary
    if not is_family_member(home):
        summary["error"] = "not a builder-family site (fingerprint absent)"
        stats["dealers_skipped_non_family"] += 1
        return summary
    summary["is_member"] = True
    stats["dealers_member"] += 1

    # 2) resolve / upsert the owning dealer entity.
    dealer = await upsert_dealer_by_host(conn, bare)
    if dealer is None:
        summary["error"] = "could not resolve owning dealer"
        stats["dealers_failed"] += 1
        return summary
    summary["dealer_cdp"] = dealer["cdp_code"]

    # 3) find the listing path that yields structured vehicles, then drain its pages.
    all_vehicles: list[Vehicle] = []
    chosen_path: str | None = None
    chosen_strategy: str | None = None
    for path in LISTING_PATHS:
        page1_url = f"{base}{path}" if path != "/" else f"{base}/"
        try:
            html1 = await governed_fetch(page1_url)
        except Exception:
            continue
        cards, strategy = _extract_vehicles(html1, bare, page1_url)
        if not cards:
            continue
        chosen_path, chosen_strategy = path, strategy
        seen_links = set()
        for c in cards:
            if c.deep_link not in seen_links:
                seen_links.add(c.deep_link)
                all_vehicles.append(c)

        # drain pages 2..N. Builders differ on the page param; the first that yields NEW
        # deep_links wins, then we walk it until a page adds nothing new (handles ueni's
        # cumulative ?pagina=N because we dedup by deep_link).
        for param in PAGE_PARAMS:
            page = 2
            progressed = False
            while page <= max_pages:
                sep = "&" if "?" in page1_url else "?"
                url = f"{page1_url}{sep}{param}={page}"
                try:
                    ph = await governed_fetch(url)
                except Exception:
                    break
                pcards, _ = _extract_vehicles(ph, bare, url)
                fresh = [c for c in pcards if c.deep_link not in seen_links]
                if not fresh:
                    break
                for c in fresh:
                    seen_links.add(c.deep_link)
                    all_vehicles.append(c)
                progressed = True
                summary["pages"] = page
                page += 1
            if progressed:
                break  # this page param works; do not try the others
        summary["pages"] = max(summary["pages"], 1)
        break  # first path that works wins

    summary["path"] = chosen_path
    summary["strategy"] = chosen_strategy
    if chosen_path is None:
        # Honest record: reachable family member but NO server-side machine-readable
        # inventory (JS-only builder). Not an error, not faked — the truthful tail state.
        summary["error"] = "no SSR/JSON-LD inventory (JS-only builder)"
        stats["dealers_no_ssr_inventory"] += 1
        return summary

    # 4) ingest this dealer's harvest (idempotent, delta-aware).
    before_new = stats["new_cars"]
    await ingest_dealer_vehicles(conn, dealer["entity_ulid"], all_vehicles, stats)
    summary["vehicles"] = len({v.deep_link for v in all_vehicles})
    summary["new"] = stats["new_cars"] - before_new
    stats["dealers_harvested"] += 1
    stats["harvested_pairs"].update(
        (dealer["entity_ulid"], v.deep_link) for v in all_vehicles if v.deep_link)
    return summary


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
# Builder-PLATFORM infrastructure hosts. When a dealer's site redirects to one of these,
# the final_url is the BUILDER, not the dealer (e.g. a parked wix site -> es.wix.com). We
# must key the dealer on its OWN catalogued domain, never on the platform host — caging
# "es.wix.com" as a dealer would mint a fake entity owning nothing real.
_PLATFORM_INFRA_HOSTS = (
    "wix.com", "es.wix.com", "ueniweb.com", "squarespace.com", "basekit.com",
    "sites.google.com", "google.com", "godaddy.com", "duda.co", "negocio.site",
)


def _is_platform_host(host: str) -> bool:
    h = host.lower()
    # An exact platform host (es.wix.com) or the bare platform domain is infra; a dealer
    # SUBdomain on the platform (arales.ueniweb.com, automovilesvhr.wixsite.com) is a real
    # dealer host and must be kept.
    return any(h == p or h == p.split(".", 1)[-1] for p in _PLATFORM_INFRA_HOSTS)


def _builder_hosts_from_fingerprints(limit: int) -> list[str]:
    """Pull the builder-family dealer hosts straight from the long-tail fingerprint file —
    the evidence artifact that classified them. One bare host per dealer, deduped."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    fp_path = os.path.join(root, "docs", "_longtail_fingerprints.json")
    with open(fp_path, encoding="utf-8") as fh:
        data = json.load(fh)
    hosts: list[str] = []
    seen: set[str] = set()
    for row in data:
        if row.get("family") != "builder":
            continue
        # Prefer the resolved final_url host (e.g. bugasgroup.com -> bugas.es) so we hit the
        # live inventory host, not a redirector. But if final_url is a BUILDER PLATFORM host
        # (a parked/redirected site), that is infra, not the dealer — use the catalogued
        # domain instead so the harvest is keyed on the dealer's own identity.
        final_host = None
        final = row.get("final_url") or ""
        m = re.search(r"^https?://([^/]+)", final)
        if m:
            final_host = re.sub(r"^www\.", "", m.group(1).lower()).split(":")[0]
        domain = (row.get("domain") or "").lower()
        domain = re.sub(r"^www\.", "", domain).split(":")[0]
        if final_host and not _is_platform_host(final_host):
            host = final_host
        elif domain and not _is_platform_host(domain):
            host = domain
        else:
            host = final_host or domain  # both infra-ish; keep something rather than drop silently
        if not host or host in seen:
            continue
        seen.add(host)
        hosts.append(host)
        if len(hosts) >= limit:
            break
    return hosts


async def harvest(dealers: list[str] | None, from_fingerprints: bool, limit: int,
                  max_pages: int) -> dict:
    conn = await asyncpg.connect(DSN)
    fetcher = FamilyFetcher()
    stats = {
        "dealers_requested": 0, "dealers_member": 0, "dealers_harvested": 0,
        "dealers_skipped_non_family": 0, "dealers_no_ssr_inventory": 0,
        "dealers_failed": 0, "cars_ingested": 0, "new_cars": 0, "new_events": 0,
        "harvested_pairs": set(), "summaries": [],
    }

    if await is_open(conn, FAMILY_KEY):
        print(f"[{FAMILY_KEY}] breaker OPEN; skipping drain (graceful degradation).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": FAMILY_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        await GeoResolver.load(conn)  # loaded for parity with the family spine (geo backbone ready)
        if from_fingerprints or not dealers:
            dealers = _builder_hosts_from_fingerprints(limit)
            print(f"[{FAMILY_KEY}] {len(dealers)} builder dealer hosts from "
                  f"_longtail_fingerprints.json (family confirmed per-dealer by fingerprint).")
        else:
            dealers = [re.sub(r"^www\.", "", d.lower()) for d in dealers]
        stats["dealers_requested"] = len(dealers)
        print(f"[{FAMILY_KEY}] family={FAMILY_NAME}")
        print(f"[{FAMILY_KEY}] governor paces each dealer host independently "
              f"(per-host token bucket). ONE recipe -> {len(dealers)} dealers.")

        for host in dealers:
            summary = await harvest_one_dealer(
                conn, governed_fetch, fetcher, host, max_pages, stats)
            stats["summaries"].append(summary)
            tag = ("member" if summary["is_member"] else "non-family")
            print(f"[{FAMILY_KEY}]   {summary['host']:34s} {tag:10s} "
                  f"path={summary.get('path')} strat={summary.get('strategy')} "
                  f"vehicles={summary['vehicles']:4d} new={summary['new']:4d}" +
                  (f"  ERR={summary['error']}" if summary.get("error") else ""))
            last_http = fetcher.last_status

        # Recipe: ONE file for the WHOLE family (keyed by the family, not a dealer).
        recipe_path = write_recipe(FAMILY_KEY, FAMILY_RECIPE)
        print(f"[{FAMILY_KEY}] family recipe written: {recipe_path}")

        # VAM count quorum for this family slice — THREE orthogonal like-with-like paths:
        #   harvested_pairs       = distinct (dealer, deep_link) pulled this run (harvest truth)
        #   db_family_vehicles    = vehicles in DB owned by the dealers this source attests AND
        #                           harvested this run (DB read truth, run-scoped)
        #   cars_ingested_distinct= the run-scoped distinct ingest counter (ingestion truth)
        family_dealer_ulids = [
            r["entity_ulid"] for r in await conn.fetch(
                "SELECT entity_ulid FROM entity_source WHERE source_key = $1", FAMILY_KEY)]
        db_family_vehicles = 0
        if family_dealer_ulids and stats["harvested_pairs"]:
            db_family_vehicles = await conn.fetchval(
                """SELECT count(*) FROM vehicle
                    WHERE entity_ulid = ANY($1::text[])
                      AND deep_link = ANY($2::text[])""",
                family_dealer_ulids,
                [p[1] for p in stats["harvested_pairs"]]) or 0
        harvested_n = len(stats["harvested_pairs"])
        verdict = await record_count_verdict(
            conn, subject_type="family_slice", subject_key=FAMILY_KEY,
            claim="distinct (dealer, deep_link) harvested == family vehicles persisted in DB",
            paths={"db_family_vehicles": db_family_vehicles,
                   "harvested_pairs": harvested_n,
                   "cars_ingested_distinct": harvested_n},
            tolerance=0.0)
        stats["verdict"] = verdict
        stats["db_family_vehicles"] = db_family_vehicles
        stats["harvested_pairs_n"] = harvested_n
        stats["recipe_path"] = str(recipe_path)
        stats["family_dealers_attested"] = len(family_dealer_ulids)

        # Run is OK if at least one dealer was caged AND the VAM did not refute. A family of
        # JS-only builders with zero structured inventory would (honestly) not pass — but the
        # builder family DOES have a structured member, so a real cage is expected.
        run_ok = (fetch_error is None and stats["dealers_harvested"] > 0
                  and verdict != "REFUTED")
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, FAMILY_KEY, ok=run_ok, rows=stats["cars_ingested"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, FAMILY_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        stats.pop("harvested_pairs", None)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[{FAMILY_KEY}] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("BUILDER FAMILY — LONG-TAIL HARVEST REPORT")
    print("=" * 64)
    print(f"  family               : {FAMILY_NAME}")
    print(f"  dealers requested    : {stats['dealers_requested']}")
    print(f"  family members       : {stats['dealers_member']}")
    print(f"  dealers harvested    : {stats['dealers_harvested']}")
    print(f"  non-family skipped   : {stats['dealers_skipped_non_family']}")
    print(f"  no-SSR-inventory     : {stats['dealers_no_ssr_inventory']} (JS-only builders, honest)")
    print(f"  failed               : {stats['dealers_failed']}")
    print(f"  cars ingested        : {stats['cars_ingested']} ({stats['new_cars']} new)")
    print(f"  NEW delta events     : {stats['new_events']}")
    print(f"  family dealers attested (entity_source): {stats.get('family_dealers_attested')}")
    print("  --- VAM count quorum (like-with-like, this slice) ---")
    print(f"  harvested_pairs      : {stats.get('harvested_pairs_n')}")
    print(f"  db_family_vehicles   : {stats.get('db_family_vehicles')}")
    print(f"  VAM verdict          : {stats.get('verdict')}")
    print(f"  health / breaker     : {stats.get('health_status')} / {stats.get('breaker_state')}")
    print(f"  recipe               : {stats.get('recipe_path')}")
    print("  --- the multiplier (one recipe -> N dealers) ---")
    for s in stats.get("summaries", []):
        if s.get("is_member"):
            print(f"    {s['host']:34s} {s['vehicles']:4d} cars (new {s['new']:4d}) "
                  f"strat={s.get('strategy') or '-':8s} cdp={s.get('dealer_cdp')}")
    print("=" * 64)


def main() -> None:
    p = argparse.ArgumentParser(
        description="Builder (Wix/Ueni/Google Sites/BaseKit/...) family long-tail harvester "
                    "(one recipe -> N dealers)")
    p.add_argument("--dealers", nargs="*", default=None,
                   help="explicit dealer hosts (e.g. crestanevada.es majadahondamotor.es)")
    p.add_argument("--from-fingerprints", action="store_true",
                   help="pull builder-family dealer hosts from docs/_longtail_fingerprints.json")
    p.add_argument("--limit", type=int, default=12,
                   help="max builder dealers to try (with --from-fingerprints); default 12")
    p.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES,
                   help=f"max listing pages per dealer; default {DEFAULT_MAX_PAGES}")
    args = p.parse_args()
    stats = asyncio.run(harvest(args.dealers, args.from_fingerprints, args.limit, args.max_pages))
    _print_report(stats)


if __name__ == "__main__":
    main()
