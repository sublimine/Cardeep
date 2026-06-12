"""Framework (Next/Astro/Nuxt/Angular) dealer-site FAMILY harvester — the LONG-TAIL
multiplier for JS-framework own-sites, end to end.

This is NOT a marketplace connector. It is the long-tail half of the mandate for the
dealers whose stock lives on a JS-rendered SPA built on a single shared dealer-site
SaaS ("web-builder"). The family map (docs/architecture/longtail_families.md) groups
17 own-site domains as `framework` — nextjs x9, astro x5, angular x2, nuxt x1 — and
flags that "nextjs/nuxt sites often expose a JSON/data API worth probing individually
before writing HTML recipes." Probing them live (2026-06-13) revealed something even
cleaner than a private API:

  * Every member runs the SAME dealer-site SaaS — photos served from a shared CDN
    (`storage.googleapis.com/vehicle-multipost-multimedia`, `.../vehicles-prd/...`)
    and the dealer logo from `firebasestorage.googleapis.com/v0/b/web-builder/...`.
    That shared web-builder host is the spine fingerprint, present on every page.
  * Although the listing surface is a JS-rendered SPA (App-Router RSC, no
    `__NEXT_DATA__`, query-param pagination ignored), the platform emits TWO
    server-rendered, no-JS structured surfaces that need no browser:
      1. `sitemap.xml` — the COMPLETE inventory: every used-car detail URL
         (`/<make>-<model>-...-de-segunda-mano-<uuid>`). Verified to match the
         page's declared `numberOfItems` exactly (inmocoches 133, lgautomocion 149,
         vallolidmotor 54, furgogandia 22).
      2. Each detail page carries a schema.org JSON-LD `Car` object with the FULL
         record: offers.price (EUR), mileageFromOdometer.value (km), productionDate
         (year), brand, model, name (title), vehicleEngine.fuelType,
         vehicleTransmission (M/A), image, vehicleIdentificationNumber (a stable
         platform UUID = native listing_ref).

So the recipe is: fingerprint the home/listing page -> drain sitemap.xml for every
car URL -> parse each detail page's JSON-LD `Car`. ONE recipe + ONE parser harvests
EVERY member, because the sitemap shape and the JSON-LD schema are byte-identical
across the family — that is the multiplier the mandate demands.

Ownership model (the long-tail half — SIMPLER than a marketplace, identical to the
DealerK family connector):
  the dealer            -> entity (already in DB; matched by website host; upsert/touch)
  each car on its site  -> vehicle, OWNED BY that dealer (entity_ulid = dealer)

There is NO platform_listing edge here: a dealer's OWN website is the PRIMARY source
of its own stock, not a third-party marketplace. Ownership is singular and direct.

This module mirrors pipeline.platform.family_dealerk_wholesale's spine EXACTLY — same
governor choke point, same GeoResolver, same idempotent ON CONFLICT bulk upserts, same
NEW-delta events, same VAM count quorum, same S-HEALTH heartbeat/breaker — so the
long-tail flows through the ONE proven architecture, not a fork of it.

Run:  python -m pipeline.platform.family_framework_next_astro_nuxt_angular__wholesale \
          --dealers inmocoches.com lgautomocion.com vallolidmotor.es furgogandia.com
      python -m pipeline.platform.family_framework_next_astro_nuxt_angular__wholesale --from-db --limit 6
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from dataclasses import dataclass

import asyncpg
from curl_cffi import requests as cffi_requests

from pipeline.engine.governor import governor
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
# harvested through this recipe is attested by the same provenance key, and the
# recipe is one file shared by the whole family.
# ---------------------------------------------------------------------------
FAMILY_KEY = "family_framework_webbuilder"
FAMILY_NAME = ("JS-framework dealer-site family (Next/Astro/Nuxt/Angular on the shared "
               "'web-builder' SaaS)")

_IMPERSONATE = "chrome131"
_TIMEOUT = 30
DEFAULT_MAX_CARS = 400          # generous per-dealer cap; long-tail dealers are < 400 cars

# The family fingerprint. The shared web-builder/SaaS hosts are the spine markers,
# present on every member page (the dealer logo + vehicle photos are served from them).
# A site is a member iff its listing HTML carries the web-builder host AND a vehicle
# media bucket. Verified live 2026-06-13 across inmocoches.com / lgautomocion.com /
# vallolidmotor.es / furgogandia.com.
_FAMILY_SPINE = "firebasestorage.googleapis.com/v0/b/web-builder"
_FAMILY_CORROBORATORS = (
    "storage.googleapis.com/vehicle-multipost-multimedia",  # primary photo bucket
    "storage.googleapis.com/vehicles-prd",                  # alt photo bucket (furgogandia)
    "vehicle-multipost-multimedia",
    "vehicles-prd",
)

# The used-car listing slugs this family converges on (informational — the sitemap is
# the authoritative enumeration; the listing page is only fingerprinted). Observed live:
# /coches-de-segunda-mano (the dominant one), /stock, /comprar-vehiculos, /vehiculos.
LISTING_PATHS = ("/coches-de-segunda-mano", "/stock", "/comprar-vehiculos",
                 "/vehiculos", "/coches", "/")

# Sitemap candidates (the platform serves /sitemap.xml; some emit an index of sub-maps).
SITEMAP_PATHS = ("/sitemap.xml", "/sitemap-0.xml", "/sitemap_index.xml")

_UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
# A used-car detail URL: ...-de-segunda-mano-<uuid> (the canonical own-site PDP slug).
_CAR_LOC_RE = re.compile(r"<loc>\s*([^<\s]+?-de-segunda-mano-" + _UUID + r")\s*</loc>",
                         re.I)
_SUBSITEMAP_RE = re.compile(r"<loc>\s*([^<\s]+?\.xml)\s*</loc>", re.I)
_LD_RE = re.compile(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S)
# schema.org vehicle subtypes the platform emits for the per-car Product object.
_VEHICLE_LD_TYPES = {"Car", "Vehicle", "BusOrCoach", "Motorcycle", "MotorizedBicycle",
                     "Product", "IndividualProduct"}
# vehicleTransmission is a single-letter code on this platform: M=Manual, A=Automático.
_TRANSMISSION = {"M": "Manual", "A": "Automático",
                 "manual": "Manual", "automatic": "Automático",
                 "automatico": "Automático", "automático": "Automático"}


# ---------------------------------------------------------------------------
# Parsed shape (field names taken from the REAL detail-page JSON-LD, not assumed).
# ---------------------------------------------------------------------------
@dataclass
class Vehicle:
    deep_link: str
    listing_ref: str        # the platform UUID (vehicleIdentificationNumber / slug tail)
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
    if not isinstance(s, str):
        return None
    s = s.strip()
    return s or None


def _to_int(v) -> int | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return int(v)
    digits = re.sub(r"[^\d]", "", str(v))
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None


def _to_float(v) -> float | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    digits = re.sub(r"[^\d]", "", str(v))
    if not digits:
        return None
    try:
        return float(digits)
    except ValueError:
        return None


def _uuid_tail(url: str) -> str | None:
    m = re.search(_UUID + r"\b", url)
    return m.group(0) if m else None


def _iter_ld_objects(html_text: str):
    """Yield every parsed JSON-LD object on a page (handles arrays + @graph)."""
    for block in _LD_RE.findall(html_text):
        block = block.strip()
        if not block:
            continue
        try:
            obj = json.loads(block)
        except Exception:
            continue
        candidates = obj if isinstance(obj, list) else [obj]
        for c in candidates:
            if not isinstance(c, dict):
                continue
            if isinstance(c.get("@graph"), list):
                for g in c["@graph"]:
                    if isinstance(g, dict):
                        yield g
            else:
                yield c


def parse_detail(html_text: str, fallback_url: str) -> Vehicle | None:
    """Parse ONE used-car from its detail page's schema.org JSON-LD `Car` object.

    ONE parser, every member. The platform emits a uniform vehicle Product object with
    offers.price, mileageFromOdometer.value, productionDate, brand, model, name (title),
    vehicleEngine.fuelType, vehicleTransmission, image, vehicleIdentificationNumber.
    Returns None if the page carries no vehicle JSON-LD (e.g. a sold/410 PDP)."""
    ld = None
    for obj in _iter_ld_objects(html_text):
        if obj.get("@type") in _VEHICLE_LD_TYPES and (
                obj.get("offers") or obj.get("vehicleIdentificationNumber")
                or obj.get("mileageFromOdometer") or obj.get("productionDate")):
            ld = obj
            break
    if ld is None:
        return None

    deep_link = _clean(ld.get("url")) or fallback_url
    vin = _clean(ld.get("vehicleIdentificationNumber")) or _clean(ld.get("sku"))
    listing_ref = vin or _uuid_tail(deep_link) or _uuid_tail(fallback_url) or deep_link

    make = _clean(ld.get("brand") if isinstance(ld.get("brand"), str)
                  else (ld.get("brand") or {}).get("name") if isinstance(ld.get("brand"), dict)
                  else None)
    model = _clean(ld.get("model") if isinstance(ld.get("model"), str)
                   else (ld.get("model") or {}).get("name") if isinstance(ld.get("model"), dict)
                   else None)
    title = _clean(ld.get("name")) or " ".join(p for p in (make, model) if p) or None

    year = _to_int(ld.get("productionDate"))
    if year is None:
        reg = _clean(ld.get("dateVehicleFirstRegistered"))
        if reg and len(reg) >= 4:
            year = _to_int(reg[:4])
    if year is not None and not (1900 <= year <= 2100):
        year = None

    km = None
    odo = ld.get("mileageFromOdometer")
    if isinstance(odo, dict):
        km = _to_int(odo.get("value"))
    elif odo is not None:
        km = _to_int(odo)
    if km is not None and not (0 <= km <= 5_000_000):
        km = None

    price = None
    offers = ld.get("offers")
    if isinstance(offers, list) and offers:
        offers = offers[0]
    if isinstance(offers, dict):
        price = _to_float(offers.get("price"))

    fuel = None
    eng = ld.get("vehicleEngine")
    if isinstance(eng, dict):
        fuel = _clean(eng.get("fuelType")) or _clean(eng.get("engineType"))
    fuel = fuel or _clean(ld.get("fuelType"))

    trans_raw = _clean(ld.get("vehicleTransmission"))
    transmission = _TRANSMISSION.get(trans_raw) if trans_raw else None
    if transmission is None and trans_raw:
        transmission = _TRANSMISSION.get(trans_raw.lower(), trans_raw)

    photo = None
    img = ld.get("image")
    if isinstance(img, list) and img:
        photo = _clean(img[0] if isinstance(img[0], str)
                       else (img[0] or {}).get("url") if isinstance(img[0], dict) else None)
    elif isinstance(img, str):
        photo = _clean(img)
    elif isinstance(img, dict):
        photo = _clean(img.get("url"))

    return Vehicle(deep_link=deep_link, listing_ref=listing_ref, title=title,
                   make=make, model=model, year=year, km=km, price=price,
                   fuel=fuel, transmission=transmission, photo_url=photo)


# ---------------------------------------------------------------------------
# Fetch — one curl_cffi GET per URL, routed THROUGH the governor (per-host bucket).
# Each dealer is its own host, so the governor paces every dealer independently and
# politely (DEFAULT profile) without any cross-dealer interference.
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
    if _FAMILY_SPINE not in low:
        return False
    return any(token in low for token in _FAMILY_CORROBORATORS)


def extract_car_urls(sitemap_xml: str) -> list[str]:
    """Every used-car detail URL in a sitemap (or sub-sitemap)."""
    out, seen = [], set()
    for u in _CAR_LOC_RE.findall(sitemap_xml):
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


# ---------------------------------------------------------------------------
# The family recipe — ONE asset shared by every member of the family.
# ---------------------------------------------------------------------------
FAMILY_RECIPE = {
    "version": 1,
    "source": FAMILY_KEY,
    "family": FAMILY_NAME,
    "scope": "long-tail dealer OWN-SITE inventory, harvested by JS-framework SaaS family",
    "engine": "curl_cffi+chrome131_impersonate+sitemap+jsonld(GET, server-rendered)",
    "access": ("OPEN public dealer websites (Chrome TLS fingerprint; no proxy, no browser, "
               "no creds). The listing UI is a JS SPA, but sitemap.xml and per-PDP "
               "schema.org JSON-LD are server-rendered — no JS execution needed."),
    "data_surface": "dealer_site_sitemap+jsonld",
    "fingerprint": ("shared dealer-site SaaS: dealer logo on "
                    "firebasestorage.googleapis.com/v0/b/web-builder/* and vehicle photos "
                    "on storage.googleapis.com/vehicle-multipost-multimedia/* (or "
                    "/vehicles-prd/*). A site is a member iff its listing HTML carries the "
                    "web-builder host (spine) AND a vehicle photo bucket (corroborator)."),
    "subfamilies": "nextjs (App-Router RSC), astro, nuxt, angular — all on the same SaaS",
    "listing_paths": list(LISTING_PATHS),
    "enumeration": ("sitemap.xml -> every '<loc>...-de-segunda-mano-<uuid></loc>' "
                    "(the COMPLETE inventory; matches the page's numberOfItems). "
                    "Query-param pagination is client-side only and is NOT used."),
    "ownership": "vehicle.entity_ulid = the DEALER itself (own-site stock; no marketplace edge)",
    "multiplier": ("ONE recipe + ONE parser harvests EVERY family member, because the "
                   "sitemap shape and the per-PDP schema.org Car JSON-LD are byte-identical "
                   "across member sites."),
    "field_map": {
        "deep_link": "JSON-LD Car.url (== the sitemap <loc>)",
        "listing_ref": "JSON-LD Car.vehicleIdentificationNumber (platform UUID; == slug tail)",
        "title": "JSON-LD Car.name",
        "make": "JSON-LD Car.brand",
        "model": "JSON-LD Car.model",
        "year": "JSON-LD Car.productionDate (fallback dateVehicleFirstRegistered[:4])",
        "km": "JSON-LD Car.mileageFromOdometer.value",
        "price": "JSON-LD Car.offers.price (EUR)",
        "fuel": "JSON-LD Car.vehicleEngine.fuelType",
        "transmission": "JSON-LD Car.vehicleTransmission (M=Manual, A=Automático)",
        "photo_url": "JSON-LD Car.image[0]",
    },
}


# ---------------------------------------------------------------------------
# DB layer — idempotent upserts mirroring family_dealerk_wholesale (no platform edge).
# ---------------------------------------------------------------------------
async def resolve_dealer_for_host(conn: asyncpg.Connection, host: str) -> dict | None:
    """Find the dealer entity in the DB whose website matches this host.

    The long-tail dealer ALREADY exists (discovered earlier with a populated `website`
    column). We match on the registrable host so we attach the harvest to the existing
    entity rather than minting a duplicate."""
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
    """Return the owning dealer entity for `host`, upserting one if the DB has none.

    Preferred path: the dealer is already in the DB (matched by website host) — we use
    it as-is and only stamp the family provenance. Fallback: mint a minimal domain-keyed
    entity so the harvest still has a real owner."""
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

    # Fallback: domain-keyed entity (bare host is a strong identity in codes.py).
    bare = re.sub(r"^www\.", "", host.lower())
    code = cdp_code(province_code="00", domain=bare)
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               website, is_tier1, status, kind_source, sells_cars,
               first_discovered_source, last_seen)
           VALUES ($1,$2,'compraventa',$3,$3,$4,FALSE,'active','platform_label',TRUE,$5, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()""",
        eulid, code, bare, bare, FAMILY_KEY)
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

    Idempotent on (entity_ulid, deep_link): existing cars are touched, genuinely new
    cars are inserted and get a NEW delta event. A re-run adds 0 rows and 0 events."""
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

        stats["cars_caged"] += len(links)
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
# Per-dealer harvest: fingerprint -> drain sitemap -> parse each PDP -> ingest.
# ---------------------------------------------------------------------------
async def _find_listing_html(governed_fetch, base: str) -> str | None:
    """Fetch the first listing path that returns 200, for fingerprinting."""
    for path in LISTING_PATHS:
        try:
            return await governed_fetch(f"{base}{path}")
        except Exception:
            continue
    return None


async def _drain_sitemap(governed_fetch, base: str, max_cars: int) -> list[str]:
    """Return every used-car detail URL from the dealer's sitemap (full inventory).
    Follows a sitemap index one level deep when the root sitemap lists sub-sitemaps."""
    urls: list[str] = []
    seen: set[str] = set()
    for sm in SITEMAP_PATHS:
        try:
            xml = await governed_fetch(f"{base}{sm}")
        except Exception:
            continue
        direct = extract_car_urls(xml)
        for u in direct:
            if u not in seen:
                seen.add(u)
                urls.append(u)
        if not direct:
            # maybe an index of sub-sitemaps; follow them one level.
            for sub in _SUBSITEMAP_RE.findall(xml):
                try:
                    sub_xml = await governed_fetch(sub)
                except Exception:
                    continue
                for u in extract_car_urls(sub_xml):
                    if u not in seen:
                        seen.add(u)
                        urls.append(u)
                if len(urls) >= max_cars:
                    break
        if urls:
            break
    return urls[:max_cars]


async def harvest_one_dealer(conn: asyncpg.Connection, governed_fetch,
                             fetcher: FamilyFetcher, host: str, max_cars: int,
                             stats: dict) -> dict:
    """Harvest ONE family dealer's own-site stock. Returns a per-dealer summary."""
    bare = re.sub(r"^www\.", "", host.lower())
    base = f"https://www.{bare}"
    summary = {"host": bare, "is_member": False, "vehicles": 0, "new": 0,
               "dealer_cdp": None, "car_urls": 0, "pdp_parsed": 0}

    # 1) fingerprint a listing page — confirm it is a real family member.
    listing = await _find_listing_html(governed_fetch, base)
    if listing is None:
        # retry on the apex host (some sites do not serve www.)
        base = f"https://{bare}"
        listing = await _find_listing_html(governed_fetch, base)
    if listing is None:
        summary["error"] = "no listing page reachable"
        stats["dealers_failed"] += 1
        return summary
    if not is_family_member(listing):
        summary["error"] = "not a web-builder-family site (fingerprint absent)"
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

    # 3) drain the sitemap for the COMPLETE inventory of car detail URLs.
    car_urls = await _drain_sitemap(governed_fetch, base, max_cars)
    summary["car_urls"] = len(car_urls)
    if not car_urls:
        summary["error"] = "sitemap yielded no car URLs"
        stats["dealers_empty"] += 1
        return summary

    # 4) parse each PDP's JSON-LD into a Vehicle.
    vehicles: list[Vehicle] = []
    for url in car_urls:
        try:
            pdp = await governed_fetch(url)
        except Exception:
            stats["pdp_fetch_errors"] += 1
            continue
        v = parse_detail(pdp, url)
        if v is not None and v.deep_link:
            vehicles.append(v)
    summary["pdp_parsed"] = len(vehicles)
    if not vehicles:
        summary["error"] = "no PDP yielded a vehicle JSON-LD"
        stats["dealers_empty"] += 1
        return summary

    # 5) ingest this dealer's harvest (idempotent, delta-aware).
    before_new = stats["new_cars"]
    await ingest_dealer_vehicles(conn, dealer["entity_ulid"], vehicles, stats)
    summary["vehicles"] = len({v.deep_link for v in vehicles})
    summary["new"] = stats["new_cars"] - before_new
    stats["dealers_harvested"] += 1
    stats["harvested_pairs"].update(
        (dealer["entity_ulid"], v.deep_link) for v in vehicles if v.deep_link)
    return summary


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
async def candidate_hosts_from_db(conn: asyncpg.Connection, limit: int) -> list[str]:
    """Pull dealer website hosts from the DB as harvest candidates (own-domain only).
    We do NOT pre-fingerprint here — harvest_one_dealer confirms family membership."""
    rows = await conn.fetch(
        """SELECT website FROM entity
            WHERE kind IN ('compraventa','concesionario_oficial')
              AND website IS NOT NULL AND website <> ''
            ORDER BY last_seen DESC""")
    hosts: list[str] = []
    seen: set[str] = set()
    skip_suffix = ("toyota.es", "citroen.es", "mercedes-benz.es", "peugeot.es",
                   "nissan.es", "renault.es", "bmw.es", "opel.es", "honda.es",
                   "dacia.es", "coches.net", "autoscout24.es", "wixsite.com",
                   "ueniweb.com", "linktr.ee", "porsche.com")
    for r in rows:
        w = r["website"].strip().lower()
        w = re.sub(r"^https?://", "", w)
        w = re.sub(r"^www\.", "", w)
        host = w.split("/")[0].split("?")[0]
        if not host or host in seen:
            continue
        if host.count(".") > 2:
            continue
        if any(host.endswith("." + s) or host == s for s in skip_suffix):
            continue
        seen.add(host)
        hosts.append(host)
        if len(hosts) >= limit:
            break
    return hosts


async def harvest(dealers: list[str] | None, from_db: bool, limit: int,
                  max_cars: int) -> dict:
    conn = await asyncpg.connect(DSN)
    fetcher = FamilyFetcher()
    stats = {
        "dealers_requested": 0, "dealers_member": 0, "dealers_harvested": 0,
        "dealers_skipped_non_family": 0, "dealers_empty": 0, "dealers_failed": 0,
        "pdp_fetch_errors": 0, "cars_caged": 0, "new_cars": 0, "new_events": 0,
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
        await GeoResolver.load(conn)  # warm the resolver cache (parity with the family spine)
        if from_db or not dealers:
            dealers = await candidate_hosts_from_db(conn, limit)
            print(f"[{FAMILY_KEY}] {len(dealers)} candidate dealer hosts from DB "
                  f"(family confirmed per-dealer by fingerprint).")
        stats["dealers_requested"] = len(dealers)
        print(f"[{FAMILY_KEY}] family={FAMILY_NAME}")
        print(f"[{FAMILY_KEY}] governor paces each dealer host independently "
              f"(per-host token bucket). ONE recipe -> {len(dealers)} dealers.")

        for host in dealers:
            summary = await harvest_one_dealer(
                conn, governed_fetch, fetcher, host, max_cars, stats)
            stats["summaries"].append(summary)
            tag = ("member" if summary["is_member"] else "non-family")
            print(f"[{FAMILY_KEY}]   {summary['host']:34s} {tag:10s} "
                  f"sitemap_cars={summary['car_urls']:4d} parsed={summary['pdp_parsed']:4d} "
                  f"vehicles={summary['vehicles']:4d} new={summary['new']:4d}" +
                  (f"  ERR={summary['error']}" if summary.get("error") else ""))
            last_http = fetcher.last_status

        # Recipe: ONE file for the WHOLE family (keyed by the family, not a dealer).
        recipe_path = write_recipe(FAMILY_KEY, FAMILY_RECIPE)
        print(f"[{FAMILY_KEY}] family recipe written: {recipe_path}")

        # VAM count quorum for this family slice — like-with-like paths:
        #   harvested_pairs    = distinct (dealer, deep_link) pulled this run (harvest truth)
        #   db_family_vehicles = vehicles in DB owned by family-attested dealers, scoped to
        #                        the deep_links pulled this run (DB read truth)
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
                   "cars_caged_distinct": harvested_n},
            tolerance=0.0)
        stats["verdict"] = verdict
        stats["db_family_vehicles"] = db_family_vehicles
        stats["harvested_pairs_n"] = harvested_n
        stats["recipe_path"] = str(recipe_path)
        stats["family_dealers_attested"] = len(family_dealer_ulids)

        run_ok = (fetch_error is None and stats["dealers_harvested"] > 0
                  and verdict != "REFUTED")
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, FAMILY_KEY, ok=run_ok, rows=stats["cars_caged"],
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
    print("FRAMEWORK (Next/Astro/Nuxt/Angular) FAMILY — LONG-TAIL HARVEST REPORT")
    print("=" * 64)
    print(f"  family               : {FAMILY_NAME}")
    print(f"  dealers requested    : {stats['dealers_requested']}")
    print(f"  family members       : {stats['dealers_member']}")
    print(f"  dealers harvested    : {stats['dealers_harvested']}")
    print(f"  non-family skipped   : {stats['dealers_skipped_non_family']}")
    print(f"  empty inventory      : {stats['dealers_empty']}")
    print(f"  failed               : {stats['dealers_failed']}")
    print(f"  pdp fetch errors     : {stats['pdp_fetch_errors']}")
    print(f"  cars caged           : {stats['cars_caged']} ({stats['new_cars']} new)")
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
            print(f"    {s['host']:34s} {s['vehicles']:4d} cars  (new {s['new']:4d})  "
                  f"cdp={s.get('dealer_cdp')}")
    print("=" * 64)


def main() -> None:
    p = argparse.ArgumentParser(
        description="Framework (Next/Astro/Nuxt/Angular) long-tail family harvester "
                    "(one recipe -> N dealers; sitemap + schema.org JSON-LD)")
    p.add_argument("--dealers", nargs="*", default=None,
                   help="explicit dealer hosts (e.g. inmocoches.com lgautomocion.com)")
    p.add_argument("--from-db", action="store_true",
                   help="pull candidate dealer hosts from the DB website column")
    p.add_argument("--limit", type=int, default=8,
                   help="max DB candidate dealers to try (with --from-db); default 8")
    p.add_argument("--max-cars", type=int, default=DEFAULT_MAX_CARS,
                   help=f"max cars per dealer; default {DEFAULT_MAX_CARS}")
    args = p.parse_args()
    stats = asyncio.run(harvest(args.dealers, args.from_db, args.limit, args.max_cars))
    _print_report(stats)


if __name__ == "__main__":
    main()
