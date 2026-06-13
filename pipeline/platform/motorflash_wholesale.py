"""Motorflash WHOLESALE harvester — the dealer-aggregator marketplace front.

Motorflash (motorflash.com) is the mid-size OPEN aggregator the 00-TIER1-REGISTRY
flags as the *best dealer-discovery multiplier* of the Spanish marketplace universe:
a single OPEN site that aggregates ~50,000 used-car listings from ~1,000 named
dealerships and powers many OEM microsites (Audi Selection:plus, H-Promise pages).
It is a genuine MARKETPLACE (multi-dealer aggregated stock) — distinct from the
single-seller retail chains (Autohero/Clicars/OcasionPlus/Flexicar) which cage
their own stock once at the chain. This is the `marketplaces_extra` front's
highest-value REACHABLE-MISSING platform.

This module proves the dual-membership model end to end for Motorflash:

  Motorflash (the marketplace)  -> entity, kind='plataforma'  (+ platform_meta)
  each SELLING DEALER           -> entity, kind='compraventa'
  each CAR                      -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the platform       -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the dealer); platform membership is plural (this edge). The
same physical car can also carry coches.net / AS24 edges without changing owner.

HONEST GEO CONSTRAINT (confessed, not papered over). Motorflash is a lead-gen
aggregator: it deliberately HIDES the dealer's physical address/city on both the
PDP and the dealer page (only the dealer NAME + a Motorflash dealer-id + a central
Motorflash phone are exposed). A Motorflash dealer therefore CANNOT be geo-anchored
to an INE province from its own pages. We cage the dealer with province_code=NULL
(schema-valid; the geo FK is nullable) and let CROSS-PLATFORM DEDUP merge it later
by name against the geo-anchored copy that AS24/coches.net already minted (the
registry's exact intent: Motorflash as a dealer-discovery CROSS-REFERENCE, ~38% of
its dealer names already exist geo-anchored in the DB). Province stays NULL until a
geo-anchored sibling claims it — we never fabricate a province.

DATA SURFACE (verified 2026-06-13, curl_cffi chrome131):
  - robots.txt declares `sitemap.concesionarios.xml` (~1,000 named dealers, each
    `/concesionario/{slug}/coches-segunda-mano/{id}/`) — the dealer index.
  - each dealer page: H1 = dealer name, lists 20 PDP links/page, paginated.
  - each PDP `/coche-segunda-mano/{make}-{model}-{slug}/ocasion/{id}-es/` carries a
    clean `Car` JSON-LD (make/model/year/km/price/fuel/transmission/photo) PLUS an
    `AutoDealer` seller block (name + telephone). No wall (CloudFront, 200 to Chrome).

PROOF SLICE, NOT THE FULL ~50k. Draining all ~1,000 dealers needs the governor's
spend/rate budget (P1). Here we cap at MAX_DEALERS dealers and log the cap honestly.

Engine: pipeline.engine.fetch (curl_cffi Chrome impersonation), paced by the P1
governor's per-host token bucket. Identity minting via services.api.codes.cdp_code.

Run: python -m pipeline.platform.motorflash_wholesale [max_dealers] [pages_per_dealer]
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
from dataclasses import dataclass

import asyncpg

from pipeline.engine.fetch import FetchEngine
from pipeline.engine.governor import governor, host_of
from pipeline.geo import GeoResolver
from pipeline.ids import ulid
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict
from services.api.codes import _base32, cdp_code

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

_BASE = "https://www.motorflash.com"
MF_DOMAIN = "motorflash.com"
MF_WEBSITE = "motorflash.com"
MF_TRADE_NAME = "Motorflash"
MF_SOURCE_KEY = "motorflash_wholesale"
CONCESIONARIOS_SITEMAP = f"{_BASE}/sitemap.concesionarios.xml"

# Province sentinel '00' = national (platform entity only; see AS24 dossier O.1).
PLATFORM_PROVINCE_SENTINEL = "00"

# PROOF SLICE caps. NOT the full ~1,000 dealers / ~50k cars (P1 governor).
DEFAULT_MAX_DEALERS = 12
DEFAULT_PAGES_PER_DEALER = 2  # 20 PDP/page -> ~40 listings/dealer cap

# Motorflash listing/dealer URL grammar (verified live 2026-06-13).
_RE_DEALER_URL = re.compile(
    r"/concesionario/([a-z0-9\-]+)/coches-segunda-mano/(\d+)/")
# Full PDP path WITH slug — the slug is load-bearing (slugless form 404s), so we
# capture the whole path and the id together, never reconstruct the URL from the id.
_RE_PDP_PATH = re.compile(
    r"(/coche-segunda-mano/[^\"'\s]+/ocasion/(\d+)-es/)")
_RE_LD_JSON = re.compile(
    r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', re.S)
_RE_H1 = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
_RE_TAGS = re.compile(r"<[^>]+>")


# ---------------------------------------------------------------------------
# Identity helpers
# ---------------------------------------------------------------------------


def mf_platform_cdp_code() -> str:
    """The Motorflash platform's immutable cdp_code. Built from the bare domain
    identity (canonical_key 'domain:motorflash.com'), province segment '00'."""
    import hashlib

    key = f"domain:{MF_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


@dataclass
class DealerRef:
    """A Motorflash selling dealer parsed from the concesionarios sitemap + page."""
    mf_dealer_id: str          # Motorflash native dealer id (stable source_ref)
    slug: str                  # url slug (fallback name source)
    name: str | None           # H1 / JSON-LD AutoDealer name (display + identity)


@dataclass
class Vehicle:
    """A used car parsed from a Motorflash PDP's `Car` JSON-LD."""
    deep_link: str
    listing_ref: str           # Motorflash native listing id
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    dealer_name: str | None    # AutoDealer.name from the PDP (attribution cross-check)


# ---------------------------------------------------------------------------
# Parsers (pure, no I/O — unit-testable)
# ---------------------------------------------------------------------------


def _clean_text(raw: str | None) -> str | None:
    if not raw:
        return None
    txt = _RE_TAGS.sub("", raw)
    txt = (txt.replace("&oacute;", "o").replace("&aacute;", "a")
              .replace("&eacute;", "e").replace("&iacute;", "i")
              .replace("&uacute;", "u").replace("&ntilde;", "n")
              .replace("&amp;", "&"))
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt or None


def parse_dealer_index(sitemap_xml: str) -> list[DealerRef]:
    """Parse the concesionarios sitemap into a de-duplicated dealer list.
    The sitemap header row `/concesionarios/` (no id) is ignored."""
    seen: dict[str, DealerRef] = {}
    for slug, mf_id in _RE_DEALER_URL.findall(sitemap_xml):
        if mf_id in seen:
            continue
        seen[mf_id] = DealerRef(mf_dealer_id=mf_id, slug=slug, name=None)
    return list(seen.values())


def parse_dealer_name(dealer_html: str) -> str | None:
    """Dealer display name = the H1 of its stock page (e.g. 'M. CONDE')."""
    m = _RE_H1.search(dealer_html)
    return _clean_text(m.group(1)) if m else None


def _ld_blocks(html: str) -> list[dict]:
    out: list[dict] = []
    for blk in _RE_LD_JSON.findall(html):
        try:
            d = json.loads(blk)
        except Exception:  # noqa: BLE001 — a malformed block must not abort the page
            continue
        out.extend(d if isinstance(d, list) else [d])
    return out


def _to_int(val) -> int | None:
    if val is None:
        return None
    if isinstance(val, dict):
        val = val.get("value")
    try:
        return int(float(str(val).replace(".", "").replace(",", "")))
    except (ValueError, TypeError):
        return None


def _to_float(val) -> float | None:
    if val is None:
        return None
    try:
        return float(str(val).replace(",", "."))
    except (ValueError, TypeError):
        return None


def pdp_links(dealer_html: str) -> list[tuple[str, str]]:
    """All distinct (full_pdp_path, listing_id) pairs linked on a dealer stock page.
    The slug is load-bearing — the slugless PDP form 404s — so we keep the whole path."""
    seen: dict[str, str] = {}
    for path, listing_id in _RE_PDP_PATH.findall(dealer_html):
        seen.setdefault(listing_id, path)
    return [(path, lid) for lid, path in seen.items()]


def parse_pdp_vehicle(pdp_html: str, pdp_url: str, listing_ref: str) -> Vehicle | None:
    """Parse the `Car` JSON-LD off a PDP into a Vehicle. Returns None if absent."""
    car: dict | None = None
    for o in _ld_blocks(pdp_html):
        if isinstance(o, dict) and o.get("@type") in ("Car", "Vehicle"):
            car = o
            break
    if car is None:
        return None
    brand = car.get("brand")
    make = brand.get("name") if isinstance(brand, dict) else (brand if isinstance(brand, str) else None)
    model = car.get("model")
    if isinstance(model, dict):
        model = model.get("name")
    offers = car.get("offers") or {}
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    seller = offers.get("seller") if isinstance(offers, dict) else None
    dealer_name = seller.get("name") if isinstance(seller, dict) else None
    image = car.get("image")
    if isinstance(image, list):
        image = image[0] if image else None
    if isinstance(image, dict):
        image = image.get("url")
    return Vehicle(
        deep_link=pdp_url,
        listing_ref=listing_ref,
        title=_clean_text(car.get("name")),
        make=make,
        model=model if isinstance(model, str) else None,
        year=_to_int(car.get("vehicleModelDate")),
        km=_to_int(car.get("mileageFromOdometer")),
        price=_to_float(offers.get("price")) if isinstance(offers, dict) else None,
        fuel=car.get("fuelType"),
        transmission=car.get("vehicleTransmission"),
        photo_url=image if isinstance(image, str) else None,
        dealer_name=_clean_text(dealer_name),
    )


# ---------------------------------------------------------------------------
# DB caging (idempotent)
# ---------------------------------------------------------------------------


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the Motorflash platform entity + platform_meta exist."""
    code = mf_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, is_tier1, status, kind_source, source_group,
               first_discovered_source, last_seen)
           VALUES ($1,$2,'plataforma',$3,$3,NULL,$4,FALSE,'active','platform_label',
                   'marketplace_motor',$5, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()""",
        eulid, code, MF_TRADE_NAME, MF_WEBSITE, MF_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, MF_SOURCE_KEY, MF_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'json_ld',$2::jsonb,FALSE,TRUE,'aggregator')
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail""",
        eulid, json.dumps({"endpoint": "/concesionario/{slug}/coches-segunda-mano/{id}/",
                           "pdp": "/coche-segunda-mano/{slug}/ocasion/{id}-es/",
                           "host": _BASE, "engine": "curl_cffi/chrome_impersonate",
                           "dealer_index": "sitemap.concesionarios.xml"}))
    return eulid


def dealer_cdp_code(d: DealerRef) -> str:
    """Mint the dealer's immutable cdp_code. Motorflash hides geo, so identity is the
    dealer NAME under the national sentinel province '00' -> canonical_key
    'name:{normalized}|p00'. This is the SAME name-keyed shape AS24/coches.net dealers
    use, so cross-platform dedup can later merge this un-geo-anchored row into its
    geo-anchored sibling by name. These are PROFESSIONAL dealers, not particulares —
    we deliberately do NOT use the particular:{platform}:{id} key (that would mislabel
    a compraventa as a private seller)."""
    name = d.name or d.slug.replace("-", " ")
    return cdp_code(province_code=PLATFORM_PROVINCE_SENTINEL, name=name)


async def upsert_dealer(conn: asyncpg.Connection, d: DealerRef) -> str:
    """Upsert the selling dealer (kind='compraventa', province NULL — see module
    docstring). Returns the dealer entity_ulid. Always succeeds (no geo gate)."""
    code = dealer_cdp_code(d)
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, is_tier1, status, kind_source, source_group,
               sells_cars, first_discovered_source, last_seen)
           VALUES ($1,$2,'compraventa',$3,$3,NULL,NULL,FALSE,'active','platform_label',
                   'marketplace_motor',TRUE,$4, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()""",
        eulid, code, d.name or d.slug.replace("-", " "), MF_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, MF_SOURCE_KEY, d.mf_dealer_id)
    return eulid


async def upsert_vehicle(conn: asyncpg.Connection, dealer_ulid: str, v: Vehicle) -> tuple[str, bool]:
    """Upsert the vehicle OWNED BY the dealer. Idempotent on (entity_ulid, deep_link)."""
    row = await conn.fetchrow(
        "SELECT vehicle_ulid FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2",
        dealer_ulid, v.deep_link)
    if row is not None:
        vulid = row["vehicle_ulid"]
        await conn.execute(
            "UPDATE vehicle SET last_seen=now(), status='available' WHERE vehicle_ulid=$1", vulid)
        return vulid, False
    vulid = ulid()
    await conn.execute(
        """INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model,
               year, km, price, fuel, transmission, photo_url, status)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,'available')
           ON CONFLICT (entity_ulid, deep_link) DO NOTHING""",
        vulid, dealer_ulid, v.deep_link, v.title, v.make, v.model, v.year, v.km, v.price,
        v.fuel, v.transmission, v.photo_url)
    real = await conn.fetchval(
        "SELECT vehicle_ulid FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2",
        dealer_ulid, v.deep_link)
    return real, (real == vulid)


async def link_platform(conn: asyncpg.Connection, platform_ulid: str, vehicle_ulid: str,
                        v: Vehicle) -> bool:
    """INSERT the platform_listing edge (Motorflash <-> vehicle). Idempotent."""
    inserted = await conn.fetchval(
        """INSERT INTO platform_listing (vehicle_ulid, platform_entity_ulid, listing_url,
               listing_ref, platform_price, status, segment, first_seen, last_seen)
           VALUES ($1,$2,$3,$4,$5,'listed','used', now(), now())
           ON CONFLICT (vehicle_ulid, platform_entity_ulid)
             DO UPDATE SET last_seen = now(), status = 'listed',
                           platform_price = EXCLUDED.platform_price,
                           listing_ref = EXCLUDED.listing_ref
           RETURNING (xmax = 0) AS inserted""",
        vehicle_ulid, platform_ulid, v.deep_link, v.listing_ref, v.price)
    return bool(inserted)


async def emit_new_event(conn: asyncpg.Connection, vulid: str, dealer_ulid: str, v: Vehicle) -> None:
    await conn.execute(
        "INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type, "
        "old_value, new_value) VALUES ($1,$2,$3,'NEW',NULL,$4::jsonb)",
        ulid(), vulid, dealer_ulid, json.dumps({"price": v.price, "title": v.title,
                                                "platform": MF_TRADE_NAME}))


MF_PLATFORM_RECIPE = {
    "version": 1,
    "source": "motorflash",
    "scope": "platform-wholesale (dealer-index aggregator)",
    "engine": "curl_cffi+chrome_impersonate+json_ld",
    "access": "OPEN (CloudFront, no wall; Chrome UA over Chrome TLS). is_tier1=false",
    "data_surface": "json_ld",
    "enumeration": "sitemap.concesionarios.xml -> /concesionario/{slug}/.../{id}/ (paginated) -> PDP Car JSON-LD",
    "platform_entity": "kind=plataforma, source_group=marketplace_motor, province_code=NULL",
    "geo_constraint": "dealer geo HIDDEN by Motorflash; dealers caged province NULL, merged by cross-platform dedup",
    "dual_membership": "vehicle.entity_ulid=SELLING DEALER (compraventa); platform_listing edge=platform<->vehicle",
    "field_map": {
        "deep_link": "PDP url /coche-segunda-mano/{slug}/ocasion/{id}-es/",
        "listing_ref": "PDP id (motorflash native)",
        "make": "Car.brand.name",
        "model": "Car.model",
        "year": "Car.vehicleModelDate",
        "km": "Car.mileageFromOdometer.value",
        "price": "Car.offers.price",
        "fuel": "Car.fuelType",
        "transmission": "Car.vehicleTransmission",
        "photo_url": "Car.image[0]",
        "dealer": "Car.offers.seller {AutoDealer name, telephone} + page H1 + concesionarios sitemap slug/id",
    },
}


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def _dealer_url(d: DealerRef, page: int) -> str:
    base = f"{_BASE}/concesionario/{d.slug}/coches-segunda-mano/{d.mf_dealer_id}/"
    return base if page <= 1 else f"{base}{page}/"


def _abs(path: str) -> str:
    return path if path.startswith("http") else f"{_BASE}{path}"


async def harvest(max_dealers: int = DEFAULT_MAX_DEALERS,
                  pages_per_dealer: int = DEFAULT_PAGES_PER_DEALER) -> dict:
    conn = await asyncpg.connect(DSN)
    engine = FetchEngine()
    stats = {
        "dealers_fetched": 0, "dealer_pages": 0, "pdps_fetched": 0,
        "listings_seen": 0, "no_car_ld": 0, "dealers_distinct": set(),
        "new_dealers": 0, "cars_caged": 0, "new_cars": 0, "edges_created": 0,
        "new_events": 0, "declared_full": None,
    }
    harvested_cageable: set[str] = set()  # distinct deep_links pulled (harvest truth)

    if await is_open(conn, MF_SOURCE_KEY):
        print(f"[motorflash_wholesale] breaker OPEN for {MF_SOURCE_KEY}; skipping drain.")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": MF_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(engine.fetch_text)
    fetch_error: str | None = None
    last_http: int | None = None

    try:
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = mf_platform_cdp_code()
        print(f"[motorflash_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid})")
        print(f"[motorflash_wholesale] governor paces host {host_of(_BASE)} (per-host token bucket).")

        # 1) dealer index from the concesionarios sitemap.
        try:
            sitemap = await governed_fetch(CONCESIONARIOS_SITEMAP)
        except Exception as e:  # noqa: BLE001
            fetch_error = str(e)
            last_http = getattr(engine, "last_status", None)
            print(f"[motorflash_wholesale] sitemap fetch failed ({e}); aborting.")
            sitemap = ""
        all_dealers = parse_dealer_index(sitemap)
        stats["declared_full"] = len(all_dealers)
        dealers = all_dealers[:max_dealers]
        print(f"[motorflash_wholesale] dealer index: {len(all_dealers)} distinct; "
              f"PROOF SLICE = {len(dealers)} dealers x {pages_per_dealer} pages "
              f"(NOT the full set — P1 governed).")

        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        seen_listing_ids: set[str] = set()

        for d in dealers:
            # collect this dealer's (pdp_path, id) pairs across its paginated stock pages.
            dealer_links: list[tuple[str, str]] = []
            dealer_name = d.name
            for page in range(1, pages_per_dealer + 1):
                try:
                    html = await governed_fetch(_dealer_url(d, page))
                except Exception as e:  # noqa: BLE001
                    fetch_error = str(e)
                    last_http = getattr(engine, "last_status", None)
                    print(f"[motorflash_wholesale] dealer {d.slug} p{page} failed ({e}); skipping.")
                    break
                stats["dealer_pages"] += 1
                if page == 1:
                    dealer_name = parse_dealer_name(html) or d.slug.replace("-", " ")
                    d.name = dealer_name
                links = pdp_links(html)
                if not links:
                    break  # no more stock pages
                dealer_links.extend(links)
            # de-dup by listing id, preserving first path seen
            uniq: dict[str, str] = {}
            for path, lid in dealer_links:
                uniq.setdefault(lid, path)
            dealer_links = [(path, lid) for lid, path in uniq.items()]
            if not dealer_links:
                continue
            stats["dealers_fetched"] += 1

            dealer_ulid = await upsert_dealer(conn, d)

            for pdp_path, listing_id in dealer_links:
                stats["listings_seen"] += 1
                if listing_id in seen_listing_ids:
                    continue
                seen_listing_ids.add(listing_id)
                pdp_url = _abs(pdp_path)
                try:
                    pdp_html = await governed_fetch(pdp_url)
                except Exception as e:  # noqa: BLE001
                    fetch_error = str(e)
                    last_http = getattr(engine, "last_status", None)
                    print(f"[motorflash_wholesale] PDP {listing_id} failed ({e}); skipping.")
                    continue
                stats["pdps_fetched"] += 1
                v = parse_pdp_vehicle(pdp_html, pdp_url, listing_id)
                if v is None or not v.deep_link:
                    stats["no_car_ld"] += 1
                    continue

                async with conn.transaction():
                    harvested_cageable.add(v.deep_link)
                    vulid, veh_new = await upsert_vehicle(conn, dealer_ulid, v)
                    stats["cars_caged"] += 1
                    if veh_new:
                        stats["new_cars"] += 1
                        await emit_new_event(conn, vulid, dealer_ulid, v)
                        stats["new_events"] += 1
                    if await link_platform(conn, platform_ulid, vulid, v):
                        stats["edges_created"] += 1

            print(f"[motorflash_wholesale] dealer {dealer_name!r}: "
                  f"listings={len(dealer_links)} caged_total={stats['cars_caged']} "
                  f"edges={stats['edges_created']}")

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, MF_PLATFORM_RECIPE)
        print(f"[motorflash_wholesale] recipe written: {recipe_path}")

        # VAM count quorum (like-with-like, this slice): three orthogonal paths that
        # all measure "distinct cageable cars in this slice".
        db_edges = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)
        db_join_vehicles = await conn.fetchval(
            """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid=$1""", platform_ulid)
        harvested_n = len(harvested_cageable)
        verdict = await record_count_verdict(
            conn, subject_type="platform_slice", subject_key=platform_code,
            claim="distinct cageable cars (harvest) == platform_listing edges == join-reachable vehicles",
            paths={"db_edges": db_edges, "db_join_vehicles": db_join_vehicles,
                   "harvested_cageable": harvested_n},
            tolerance=0.0)
        stats.update({"verdict": verdict, "db_edges": db_edges,
                      "db_join_vehicles": db_join_vehicles, "harvested_cageable": harvested_n,
                      "platform_code": platform_code, "platform_ulid": platform_ulid,
                      "recipe_path": str(recipe_path)})

        run_ok = fetch_error is None and stats["dealer_pages"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, MF_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, MF_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    print("\n" + "=" * 64)
    print("MOTORFLASH WHOLESALE HARVEST — PROOF SLICE REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  dealer index (full)   : {stats.get('declared_full')}  (NOT all harvested — proof slice)")
    print(f"  dealers fetched       : {stats.get('dealers_fetched')}")
    print(f"  dealer pages          : {stats.get('dealer_pages')}")
    print(f"  PDPs fetched          : {stats.get('pdps_fetched')}")
    print(f"  listings seen         : {stats.get('listings_seen')}")
    print(f"  PDPs w/o Car JSON-LD  : {stats.get('no_car_ld')}")
    print(f"  dealers attributed    : {stats.get('dealers_distinct')} distinct "
          f"({stats.get('new_dealers')} new this run)")
    print(f"  cars caged            : {stats.get('cars_caged')} ({stats.get('new_cars')} new)")
    print(f"  platform_listing edges: {stats.get('edges_created')} created "
          f"(db total for MF = {stats.get('db_edges')})")
    print(f"  NEW delta events      : {stats.get('new_events')}")
    print("  --- VAM count quorum (like-with-like, this slice) ---")
    print(f"  harvested_cageable    : {stats.get('harvested_cageable')}")
    print(f"  db_edges              : {stats.get('db_edges')}")
    print(f"  db_join_vehicles      : {stats.get('db_join_vehicles')}")
    print(f"  VAM verdict           : {stats.get('verdict')}")
    print(f"  recipe                : {stats.get('recipe_path')}")
    print("=" * 64)


def _force_utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass


if __name__ == "__main__":
    _force_utf8_stdout()
    md = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MAX_DEALERS
    ppd = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PAGES_PER_DEALER
    result = asyncio.run(harvest(md, ppd))
    if result.get("skipped"):
        print(f"[motorflash_wholesale] skipped: {result.get('reason')}")
    else:
        _print_report(result)
