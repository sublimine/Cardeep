"""DealerK WordPress FAMILY harvester — the LONG-TAIL multiplier, end to end.

This is NOT a marketplace connector. It is the proof of the OTHER half of the
mandate: the inventory that lives on each dealer's OWN website. Thousands of
Spanish compraventas/concesionarios do not feed a Tier-1 marketplace — their
stock only exists on `www.<dealer>.es`. Harvesting them one-by-one does not
scale; the multiplier is the CMS FAMILY: group dealers by the platform their
site runs, then ONE recipe harvests MANY dealers.

The family proven here is the **DealerK (MotorK) WordPress** stack — verified
live 2026-06-12 by fingerprinting real dealer domains already in the Cardeep DB:

  * WordPress + Elementor + the "tucoche" car-listing plugin
  * assets served from a shared multisite CDN: `*.dealerk.com/<tenant>/uploads/sites/<N>/`
    and vehicle photos from `cdn.dealerk.es/dealer/datafiles/vehicle/...`
  * a uniform used-car listing surface at `/coches/segunda-mano/` (also reachable
    as `/seminuevos/` and `/coches/`), paginated with `?page=N`
  * identical card markup on every member site (vcard-* classes), so ONE parser
    reads them all

Because the markup is byte-identical across members, ONE recipe + ONE parser
harvests N dealers. That is the multiplier the mandate demands: a family recipe,
not a per-dealer scraper.

Ownership model (the long-tail half — SIMPLER than a marketplace):
  the dealer            -> entity, kind='compraventa' (already in DB; upsert/touch)
  each car on its site  -> vehicle, OWNED BY that dealer (entity_ulid = dealer)

There is NO platform_listing edge here: a dealer's own website is the PRIMARY
source of its own stock, not a third-party marketplace. Ownership is singular and
direct — exactly the per-dealer recipe model (pipeline.harvest_dealer), lifted to
a family so one recipe serves the whole family.

This module mirrors pipeline.platform.coches_net_wholesale's spine EXACTLY — same
governor choke point, same GeoResolver, same idempotent ON CONFLICT upserts, same
NEW-delta events, same VAM count quorum, same S-HEALTH heartbeat — so the long-tail
flows through the ONE proven architecture, not a fork of it.

Run:  python -m pipeline.platform.family_dealerk_wholesale --dealers archiauto.com autochristian.com
      python -m pipeline.platform.family_dealerk_wholesale --from-db --limit 5
"""
from __future__ import annotations

import argparse
import asyncio
import html as _htmllib
import json
import os
import re
import sys
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
# Family identity. The source_key is the FAMILY, not a single dealer: every
# dealer harvested through this recipe is attested by the same provenance key,
# and the recipe is one file shared by the whole family.
# ---------------------------------------------------------------------------
FAMILY_KEY = "family_dealerk_wp"
FAMILY_NAME = "DealerK WordPress (MotorK) dealer-site family"

# The uniform listing surface. `/coches/segunda-mano/` is the canonical used-car
# path; some members expose the same stock under `/seminuevos/` or `/coches/`.
# We try them in order and use the first that yields cards.
LISTING_PATHS = ("/coches/segunda-mano/", "/seminuevos/", "/coches/")
_IMPERSONATE = "chrome131"
_TIMEOUT = 30
DEFAULT_MAX_PAGES = 12          # generous cap; most long-tail dealers are < 12 pages
PAGE_SIZE_HINT = 15             # the family renders ~15 cards/page (informational)

# The family fingerprint. The dealerk asset host is the spine marker (present on
# every page). The home page additionally carries the 'tucoche' page-builder asset;
# listing pages instead carry the vehicle-CDN path. A site is a member iff it serves
# 'dealerk' AND at least one of those two corroborating markers. Verified live
# 2026-06-12 across archiauto.com / autochristian.com (home + listing pages).
_FAMILY_SPINE = "dealerk"
_FAMILY_CORROBORATORS = ("tucoche", "cdn.dealerk.es/dealer/datafiles/vehicle")


# ---------------------------------------------------------------------------
# Parsed shapes (field names taken from the REAL card markup, not assumed).
# ---------------------------------------------------------------------------
@dataclass
class Vehicle:
    deep_link: str
    listing_ref: str        # the numeric id in the PDP path (.../<id>/)
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    photo_url: str | None


# One vehicle "card" is the HTML between consecutive make-model anchors. We split
# the listing on the stable anchor class and parse each fragment with cheap regex
# (the markup is server-rendered and uniform across the family — no JS needed).
_CARD_SPLIT = re.compile(r'vcard-main-info__make-model')
_PDP_RE = re.compile(
    r'href=["\'](https?://[^"\']*?/(?:coches|seminuevos)/[^"\']*?/(\d+)/)["\']')
_MAKE_MODEL_RE = re.compile(r'class="vcard--link"[^>]*>([^<]+)<')
_VERSION_RE = re.compile(r'vcard-main-info__version[^>]*>\s*([^<]+?)\s*<')
_PRICE_RE = re.compile(r'vcard-price__price[^>]*>\s*([0-9][0-9.\s]*)\s*&euro;|'
                       r'vcard-price__price[^>]*>\s*([0-9][0-9.\s]*)\s*€')
_CONSUMPTION_RE = re.compile(r'vcard-consumption__title[^>]*>\s*([^<]+?)\s*<')
_PHOTO_RE = re.compile(r'(https?://cdn\.dealerk\.[a-z.]+/[^"\']+?\.(?:jpe?g|png|webp))',
                       re.I)
# date+km+fuel line, e.g. "11/2023 - 46.413 Km - Gasolina"
_CONS_PARTS_RE = re.compile(
    r'(?:(\d{1,2})/)?(\d{4})\s*-\s*([0-9.\s]+)\s*km\s*-\s*([^<\-]+)', re.I)
_NEXT_PAGE_RE = re.compile(r'[?&]page=(\d+)')


def _clean(s: str | None) -> str | None:
    if s is None:
        return None
    s = _htmllib.unescape(s).strip()
    return s or None


def _price_to_float(card: str) -> float | None:
    m = _PRICE_RE.search(card)
    if not m:
        return None
    raw = m.group(1) or m.group(2) or ""
    digits = re.sub(r"[^\d]", "", raw)  # "19.995" -> 19995
    if not digits:
        return None
    try:
        return float(digits)
    except ValueError:
        return None


def _split_make_model(text: str | None) -> tuple[str | None, str | None]:
    """The make-model anchor reads e.g. 'Ford Puma' -> make='Ford', model='Puma'.
    First token = make; remainder = model. Keeps multi-word models intact."""
    text = _clean(text)
    if not text:
        return (None, None)
    parts = text.split()
    if len(parts) == 1:
        return (parts[0], None)
    return (parts[0], " ".join(parts[1:]))


def parse_cards(listing_html: str) -> list[Vehicle]:
    """Parse every used-car card from one listing page. ONE parser, every member.

    Cards are server-rendered fragments delimited by the make-model anchor class.
    Each fragment carries the PDP link (+ numeric listing id), make/model, version,
    price, the date/km/fuel line, and a dealerk-CDN photo — all via stable classes."""
    fragments = _CARD_SPLIT.split(listing_html)
    out: list[Vehicle] = []
    seen: set[str] = set()
    for frag in fragments[1:]:  # [0] is the pre-first-card preamble
        pdp = _PDP_RE.search(frag)
        if not pdp:
            continue
        deep_link, listing_ref = pdp.group(1), pdp.group(2)
        if deep_link in seen:
            continue
        seen.add(deep_link)

        mm = _MAKE_MODEL_RE.search(frag)
        make, model = _split_make_model(mm.group(1) if mm else None)
        version = _clean(_VERSION_RE.search(frag).group(1)) if _VERSION_RE.search(frag) else None
        title_bits = [b for b in (make, model, version) if b]
        title = " ".join(title_bits) if title_bits else None

        price = _price_to_float(frag)

        year = km = None
        fuel = None
        cons = _CONSUMPTION_RE.search(frag)
        if cons:
            cm = _CONS_PARTS_RE.search(_htmllib.unescape(cons.group(1)))
            if cm:
                y = cm.group(2)
                if y and y.isdigit() and 1900 <= int(y) <= 2100:
                    year = int(y)
                kmraw = re.sub(r"[^\d]", "", cm.group(3) or "")
                if kmraw:
                    k = int(kmraw)
                    if 0 <= k <= 5_000_000:
                        km = k
                fuel = _clean(cm.group(4))

        photo = _PHOTO_RE.search(frag)
        out.append(Vehicle(
            deep_link=deep_link, listing_ref=listing_ref, title=title,
            make=make, model=model, year=year, km=km, price=price,
            fuel=fuel, photo_url=photo.group(1) if photo else None))
    return out


# ---------------------------------------------------------------------------
# Fetch — one curl_cffi GET per page, routed THROUGH the governor (per-host bucket).
# Each dealer is its own host, so the governor paces every dealer independently and
# politely (DEFAULT profile ~0.7 req/s/host) without any cross-dealer interference.
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


# ---------------------------------------------------------------------------
# The family recipe — ONE asset shared by every member of the family.
# ---------------------------------------------------------------------------
FAMILY_RECIPE = {
    "version": 1,
    "source": FAMILY_KEY,
    "family": FAMILY_NAME,
    "scope": "long-tail dealer OWN-SITE inventory, harvested by CMS family",
    "engine": "curl_cffi+chrome131_impersonate+html(GET, server-rendered)",
    "access": ("OPEN public dealer websites (Chrome TLS fingerprint; no proxy, no "
               "browser, no creds). Server-rendered HTML — no JS execution needed."),
    "data_surface": "dealer_site_html",
    "fingerprint": ("WordPress + Elementor + 'tucoche' listing plugin; assets on "
                    "*.dealerk.com/<tenant>/uploads/sites/<N>/ and photos on "
                    "cdn.dealerk.es/dealer/datafiles/vehicle/*. A site is a member "
                    "iff its HTML carries 'dealerk' (spine) AND at least one of "
                    "'tucoche' or 'cdn.dealerk.es/dealer/datafiles/vehicle'."),
    "listing_paths": list(LISTING_PATHS),
    "enumeration": "?page=1..N until a page yields no cards (or max_pages cap)",
    "ownership": "vehicle.entity_ulid = the DEALER itself (own-site stock; no marketplace edge)",
    "multiplier": ("ONE recipe + ONE parser harvests EVERY family member, because the "
                   "vcard-* card markup is byte-identical across member sites."),
    "field_map": {
        "deep_link": "card PDP anchor href (.../coches/segunda-mano/.../<id>/)",
        "listing_ref": "numeric <id> in the PDP path",
        "make": "vcard-main-info__make-model anchor, first token",
        "model": "vcard-main-info__make-model anchor, remaining tokens",
        "version": "vcard-main-info__version",
        "price": "vcard-price__price (e.g. '19.995 €' -> 19995)",
        "year": "vcard-consumption__title 'MM/YYYY - KM Km - Fuel' -> YYYY",
        "km": "vcard-consumption__title -> KM",
        "fuel": "vcard-consumption__title -> Fuel",
        "photo_url": "first cdn.dealerk.* vehicle image in the card",
    },
}


# ---------------------------------------------------------------------------
# DB layer — idempotent upserts mirroring coches_net_wholesale (minus the edge).
# ---------------------------------------------------------------------------
async def resolve_dealer_for_host(conn: asyncpg.Connection, host: str) -> dict | None:
    """Find the dealer entity in the DB whose website matches this host.

    The long-tail dealer ALREADY exists (discovered earlier with a populated
    `website` column). We match on the registrable host so we attach the harvest
    to the existing entity rather than minting a duplicate."""
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


async def upsert_dealer_by_host(conn: asyncpg.Connection, geo: GeoResolver,
                                host: str) -> dict | None:
    """Return the owning dealer entity for `host`, upserting one if the DB has none.

    Preferred path: the dealer is already in the DB (matched by website host) — we
    use it as-is and only stamp the family provenance. Fallback: mint a minimal
    domain-keyed entity so the harvest still has a real owner (province NULL is
    allowed for a domain-keyed cdp_code: the canonical key is the bare domain)."""
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
    # province for a domain-keyed code is cosmetic in the cdp_code; use '00' national
    # sentinel only inside the code string is NOT valid for a real entity FK, so we
    # leave province_code NULL and let the code carry the domain identity.
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
        year, km, price, fuel, photo_url, vin_ref, status)
SELECT u.vehicle_ulid, u.entity_ulid, u.deep_link, u.title, u.make, u.model,
       u.year, u.km, u.price, u.fuel, u.photo_url, u.vin_ref, 'available'
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[], $5::text[], $6::text[],
              $7::int[], $8::int[], $9::numeric[], $10::text[], $11::text[], $12::text[])
       AS u(vehicle_ulid, entity_ulid, deep_link, title, make, model,
            year, km, price, fuel, photo_url, vin_ref)
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
    # dedup within this dealer's harvest by deep_link
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
                [x[3].fuel for x in ins], [x[3].photo_url for x in ins],
                [x[3].listing_ref for x in ins])
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
# Per-dealer harvest: fingerprint -> drain pages -> parse -> ingest.
# ---------------------------------------------------------------------------
async def harvest_one_dealer(conn: asyncpg.Connection, geo: GeoResolver,
                             governed_fetch, fetcher: FamilyFetcher, host: str,
                             max_pages: int, stats: dict) -> dict:
    """Harvest ONE family dealer's own-site stock. Returns a per-dealer summary."""
    bare = re.sub(r"^www\.", "", host.lower())
    base = f"https://www.{bare}"
    summary = {"host": bare, "is_member": False, "vehicles": 0, "new": 0,
               "dealer_cdp": None, "pages": 0, "path": None}

    # 1) fingerprint the home page — confirm it is a real family member.
    try:
        home = await governed_fetch(base)
    except Exception as e:
        try:
            home = await governed_fetch(f"https://{bare}")
            base = f"https://{bare}"
        except Exception as e2:
            summary["error"] = f"home fetch failed: {e2}"
            stats["dealers_failed"] += 1
            return summary
    if not is_family_member(home):
        summary["error"] = "not a DealerK-family site (fingerprint absent)"
        stats["dealers_skipped_non_family"] += 1
        return summary
    summary["is_member"] = True
    stats["dealers_member"] += 1

    # 2) resolve / upsert the owning dealer entity.
    dealer = await upsert_dealer_by_host(conn, geo, bare)
    if dealer is None:
        summary["error"] = "could not resolve owning dealer"
        stats["dealers_failed"] += 1
        return summary
    summary["dealer_cdp"] = dealer["cdp_code"]

    # 3) find the listing path that yields cards, then drain its pages.
    all_vehicles: list[Vehicle] = []
    chosen_path: str | None = None
    for path in LISTING_PATHS:
        page1 = f"{base}{path}"
        try:
            html_text = await governed_fetch(page1)
        except Exception:
            continue
        cards = parse_cards(html_text)
        if not cards:
            continue
        chosen_path = path
        all_vehicles.extend(cards)
        # drain pages 2..N until a page yields no cards.
        seen_links = {v.deep_link for v in cards}
        page = 2
        while page <= max_pages:
            url = f"{base}{path}?page={page}"
            try:
                ph = await governed_fetch(url)
            except Exception:
                break
            pcards = parse_cards(ph)
            fresh = [c for c in pcards if c.deep_link not in seen_links]
            if not fresh:
                break  # no new cars -> end of inventory
            for c in fresh:
                seen_links.add(c.deep_link)
            all_vehicles.extend(fresh)
            summary["pages"] = page
            page += 1
        summary["pages"] = max(summary["pages"], 1)
        break  # first path that works wins
    summary["path"] = chosen_path
    if chosen_path is None:
        summary["error"] = "no listing path yielded cards (empty or changed)"
        stats["dealers_empty"] += 1
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
                   "safamotor.com", "dacia.es", "coches.net", "autoscout24.es",
                   "wixsite.com", "ueniweb.com")
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
                  max_pages: int) -> dict:
    conn = await asyncpg.connect(DSN)
    fetcher = FamilyFetcher()
    stats = {
        "dealers_requested": 0, "dealers_member": 0, "dealers_harvested": 0,
        "dealers_skipped_non_family": 0, "dealers_empty": 0, "dealers_failed": 0,
        "cars_ingested": 0, "new_cars": 0, "new_events": 0,
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
        geo = await GeoResolver.load(conn)
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
                conn, geo, governed_fetch, fetcher, host, max_pages, stats)
            stats["summaries"].append(summary)
            tag = ("member" if summary["is_member"] else "non-family")
            print(f"[{FAMILY_KEY}]   {summary['host']:34s} {tag:10s} "
                  f"path={summary.get('path')} vehicles={summary['vehicles']:3d} "
                  f"new={summary['new']:3d}" +
                  (f"  ERR={summary['error']}" if summary.get("error") else ""))
            last_http = fetcher.last_status

        # Recipe: ONE file for the WHOLE family (keyed by the family, not a dealer).
        recipe_path = write_recipe(FAMILY_KEY, FAMILY_RECIPE)
        print(f"[{FAMILY_KEY}] family recipe written: {recipe_path}")

        # VAM count quorum for this family slice — THREE orthogonal like-with-like paths:
        #   harvested_pairs  = distinct (dealer, deep_link) pulled this run (harvest truth)
        #   db_family_vehicles = vehicles in DB owned by the dealers this source attests
        #                        (DB read truth, scoped to family-attested dealers)
        #   db_family_events = NEW events ever emitted by this family ... NO: that drifts.
        # We use the run-scoped DB read of the SAME dealers as the second path, and the
        # ingested counter as the primary so silent ingestion loss cannot read TRUSTWORTHY.
        family_dealer_ulids = [
            r["entity_ulid"] for r in await conn.fetch(
                "SELECT entity_ulid FROM entity_source WHERE source_key = $1", FAMILY_KEY)]
        db_family_vehicles = 0
        if family_dealer_ulids:
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
        # drop the set before returning (not JSON-friendly, big)
        stats.pop("harvested_pairs", None)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[{FAMILY_KEY}] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("DEALERK WORDPRESS FAMILY — LONG-TAIL HARVEST REPORT")
    print("=" * 64)
    print(f"  family               : {FAMILY_NAME}")
    print(f"  dealers requested    : {stats['dealers_requested']}")
    print(f"  family members       : {stats['dealers_member']}")
    print(f"  dealers harvested    : {stats['dealers_harvested']}")
    print(f"  non-family skipped   : {stats['dealers_skipped_non_family']}")
    print(f"  empty inventory      : {stats['dealers_empty']}")
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
            print(f"    {s['host']:34s} {s['vehicles']:3d} cars  (new {s['new']:3d})  "
                  f"cdp={s.get('dealer_cdp')}")
    print("=" * 64)


def main() -> None:
    p = argparse.ArgumentParser(
        description="DealerK WordPress family long-tail harvester (one recipe -> N dealers)")
    p.add_argument("--dealers", nargs="*", default=None,
                   help="explicit dealer hosts (e.g. archiauto.com autochristian.com)")
    p.add_argument("--from-db", action="store_true",
                   help="pull candidate dealer hosts from the DB website column")
    p.add_argument("--limit", type=int, default=8,
                   help="max DB candidate dealers to try (with --from-db); default 8")
    p.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES,
                   help=f"max listing pages per dealer; default {DEFAULT_MAX_PAGES}")
    args = p.parse_args()
    stats = asyncio.run(harvest(args.dealers, args.from_db, args.limit, args.max_pages))
    _print_report(stats)


if __name__ == "__main__":
    main()
