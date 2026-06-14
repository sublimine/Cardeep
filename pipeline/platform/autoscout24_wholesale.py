"""AutoScout24 WHOLESALE harvester — the platform-as-entity proof.

AS24 is an OPEN giant marketplace (00-TIER1-REGISTRY O.1: is_tier1=FALSE,
data_surface=next_data, GOLD dealer attribution). This module harvests a BOUNDED
real slice of its /lst stream and proves the dual-membership model end to end:

  AS24 (the marketplace)        -> entity, kind='plataforma'  (+ platform_meta)
  each SELLING DEALER           -> entity, kind='compraventa' (geo-resolved)
  each CAR                      -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the platform       -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the dealer); platform membership is plural (this edge). The
same physical car can later gain coches.net/coches.com edges without changing owner.

PROOF SLICE, NOT THE FULL HARVEST. AS24 declares ~278k results; draining all of it
needs the governor (page-window stability, dedup-at-scale, spend/rate budget) of
P1. Here we cap at MAX_PAGES (~12 pages, ~240 cars) and log the cap honestly. The
declared full count is recorded for the VAM verdict's slice arithmetic.

Engine: pipeline.engine.fetch (curl_cffi Chrome impersonation). REUSES the AS24
__NEXT_DATA__ parsers from pipeline.sources.autoscout24 (parse_listing_vehicle,
_find_listings, _next_data) — this module adds the wholesale /lst path + the
platform caging, it does not re-implement listing parsing.

Run: python -m pipeline.platform.autoscout24_wholesale [max_pages]
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
from pipeline.sources.autoscout24 import (
    Vehicle,
    _find,
    _find_listings,
    _next_data,
    parse_listing_vehicle,
)
from pipeline.verify import record_count_verdict
from services.api.codes import _base32  # reuse the canonical Crockford-base32 encoder

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

_BASE = "https://www.autoscout24.es"
# AS24 platform identity (00-TIER1-REGISTRY O.1).
AS24_DOMAIN = "autoscout24.es"
AS24_WEBSITE = "autoscout24.es"
AS24_TRADE_NAME = "AutoScout24"
AS24_SOURCE_KEY = "as24_wholesale"
# Province sentinel '00' = national. geo_province has NO '00' (52 real provinces),
# so the platform ENTITY stores province_code = NULL to satisfy the geo FK; '00'
# lives only inside the cdp_code string (free text, no FK). This is the safe choice
# the mandate offered (insert NULL) — we never pollute geo_province with a sentinel.
PLATFORM_PROVINCE_SENTINEL = "00"

# PROOF SLICE cap. ~12 pages * 20 = ~240 cars. NOT the 278k full set (P1 governor).
DEFAULT_MAX_PAGES = 12
PAGE_SIZE = 20
# Stable sort is load-bearing: a non-stably-sorted live set fabricates dupes / drops
# across page boundaries. 'age' + desc gives a stable newest-first ordering window.
SORT = "age"


def as24_platform_cdp_code() -> str:
    """The AS24 platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:autoscout24.es'), province segment '00' (national)."""
    import hashlib

    key = f"domain:{AS24_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


@dataclass
class DealerRef:
    """The selling dealer parsed from a single /lst listing's inline `seller`."""
    source_dealer_id: str
    company_name: str | None
    slug: str | None
    province_code: str | None
    city: str | None
    street: str | None
    zip: str | None
    website: str | None


def _zip5(zip_raw) -> str | None:
    """AS24 serves zips without the leading zero (e.g. Barcelona 08xxx as '8xxx').
    Zero-pad to 5 so the province prefix (first 2) is correct."""
    if zip_raw is None:
        return None
    digits = re.sub(r"[^\d]", "", str(zip_raw))
    if not digits:
        return None
    return digits.zfill(5)[:5]


def _slug_from_infopage(href: str | None) -> str | None:
    if not href:
        return None
    m = re.search(r"/profesionales/([a-z0-9-]+)", href)
    return m.group(1) if m else None


def parse_listing_dealer(raw: dict) -> DealerRef | None:
    """Parse the SELLING DEALER from a /lst listing's inline seller + location.

    On /lst (unlike /profesionales/{slug}) the dealer identity is per-listing in
    `seller` (id, companyName, type, links.infoPage) and `location` (zip, city,
    street). Only professional Dealers become entities; private sellers are skipped.
    """
    seller = raw.get("seller") or {}
    if seller.get("type") != "Dealer":
        return None
    sid = seller.get("id")
    if not sid:
        return None
    loc = raw.get("location") or {}
    zip5 = _zip5(loc.get("zip"))
    prov = zip5[:2] if zip5 else None
    links = seller.get("links") or {}
    infopage = links.get("infoPage") if isinstance(links, dict) else None
    return DealerRef(
        source_dealer_id=str(sid),
        company_name=seller.get("companyName"),
        slug=_slug_from_infopage(infopage),
        province_code=prov,
        city=loc.get("city"),
        street=loc.get("street"),
        zip=zip5,
        website=None,  # /lst seller carries no homepage; identity is the dealer name+location
    )


def _lst_url(page: int) -> str:
    return f"{_BASE}/lst?atype=C&cy=E&sort={SORT}&desc=1&size={PAGE_SIZE}&page={page}"


# ---------------------------------------------------------------------------
# DB layer
# ---------------------------------------------------------------------------

AS24_PLATFORM_RECIPE = {
    "version": 1,
    "source": "autoscout24",
    "scope": "platform-wholesale (/lst stream)",
    "engine": "curl_cffi+chrome_impersonate+next_data",
    "access": "OPEN (Chrome UA over Chrome TLS fingerprint; SSR __NEXT_DATA__). is_tier1=false",
    "data_surface": "next_data",
    "enumeration": "/lst?atype=C&cy=E&sort=age&desc=1&size=20&page=N (stable sort; dedup by listing id)",
    "platform_entity": "kind=plataforma, province_code=NULL (sentinel 00 in cdp_code only)",
    "dual_membership": "vehicle.entity_ulid=SELLING DEALER (compraventa); platform_listing edge=platform<->vehicle",
    "field_map": {
        "deep_link": "listing.url (host-prefixed)",
        "listing_ref": "listing.id (AS24 native listing id)",
        "make": "listing.vehicle.make",
        "model": "listing.vehicle.model",
        "year": "listing.vehicle.firstRegistrationDate | tracking.firstRegistration",
        "km": "listing.vehicle.mileageInKm | tracking.mileage",
        "price": "listing.prices.public.priceRaw | tracking.price",
        "fuel": "listing.vehicle.fuelCategory|fuel",
        "transmission": "listing.vehicle.transmissionType|transmission",
        "photo_url": "listing.images[0] | ocsImagesA[0]",
        "dealer": "listing.seller {id, companyName, type=Dealer, links.infoPage->slug}",
        "location": "listing.location {zip(zero-padded->province2), city, street}",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the AS24 platform entity + platform_meta exist.
    Returns the platform entity_ulid."""
    code = as24_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, is_tier1, status, kind_source,
               first_discovered_source, last_seen)
           VALUES ($1,$2,'plataforma',$3,$3,NULL,$4,FALSE,'active','platform_label',$5, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()""",
        eulid, code, AS24_TRADE_NAME, AS24_WEBSITE, AS24_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, AS24_SOURCE_KEY, AS24_DOMAIN)
    # platform_meta 1:1 extension (data surface + live counter slot).
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like)
           VALUES ($1,'next_data',$2::jsonb,FALSE,FALSE)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail""",
        eulid, json.dumps({"endpoint": "/lst", "host": _BASE, "sort": SORT,
                           "size": PAGE_SIZE, "engine": "curl_cffi/chrome_impersonate"}))
    return eulid


async def upsert_dealer(conn: asyncpg.Connection, geo: GeoResolver, d: DealerRef) -> str | None:
    """Upsert the selling dealer entity (kind='compraventa', geo-resolved).
    Returns the dealer entity_ulid, or None if it cannot be geo-anchored."""
    if not d.province_code:
        return None
    # province must be a real Spanish INE province (01-52); a bad/foreign postcode
    # yields an out-of-range code that would violate the geo FK — skip honestly.
    if not (d.province_code.isdigit() and "01" <= d.province_code <= "52"):
        return None
    muni = geo.municipality_code(d.province_code, d.city)
    code = cdp_code_dealer(d, muni)
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, municipality_code, address, postcode, website, is_tier1,
               status, kind_source, sells_cars, first_discovered_source, last_seen)
           VALUES ($1,$2,'compraventa',$3,$3,$4,$5,$6,$7,$8,FALSE,'active','platform_label',TRUE,$9, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()""",
        eulid, code, d.company_name, d.province_code, muni, d.street, d.zip, d.website,
        AS24_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, AS24_SOURCE_KEY, d.source_dealer_id)
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.
    AS24 /lst dealers have no bare domain -> identity = name + location + address."""
    from services.api.codes import cdp_code

    return cdp_code(province_code=d.province_code, domain=d.website, name=d.company_name,
                    municipality_code=muni, address=d.street)


async def upsert_vehicle(conn: asyncpg.Connection, dealer_ulid: str, v: Vehicle) -> tuple[str, bool]:
    """Upsert the vehicle OWNED BY the dealer (entity_ulid=dealer).
    Returns (vehicle_ulid, was_new). Idempotent on (entity_ulid, deep_link)."""
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
               year, km, price, fuel, transmission, photo_url, vin_ref, status)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,'available')
           ON CONFLICT (entity_ulid, deep_link) DO NOTHING""",
        vulid, dealer_ulid, v.deep_link, v.title, v.make, v.model, v.year, v.km, v.price,
        v.fuel, v.transmission, v.photo_url, v.vin_ref)
    # resolve the real ulid (a concurrent/duplicate insert may have won the conflict)
    real = await conn.fetchval(
        "SELECT vehicle_ulid FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2",
        dealer_ulid, v.deep_link)
    return real, (real == vulid)


async def link_platform(conn: asyncpg.Connection, platform_ulid: str, vehicle_ulid: str,
                        v: Vehicle, listing_ref: str) -> bool:
    """INSERT the platform_listing edge (platform <-> vehicle). Idempotent.
    Returns True if a NEW edge was created."""
    inserted = await conn.fetchval(
        """INSERT INTO platform_listing (vehicle_ulid, platform_entity_ulid, listing_url,
               listing_ref, platform_price, status, first_seen, last_seen)
           VALUES ($1,$2,$3,$4,$5,'listed', now(), now())
           ON CONFLICT (vehicle_ulid, platform_entity_ulid)
             DO UPDATE SET last_seen = now(), status = 'listed',
                           platform_price = EXCLUDED.platform_price,
                           listing_ref = EXCLUDED.listing_ref
           RETURNING (xmax = 0) AS inserted""",
        vehicle_ulid, platform_ulid, v.deep_link, listing_ref, v.price)
    return bool(inserted)


async def emit_new_event(conn: asyncpg.Connection, vulid: str, dealer_ulid: str, v: Vehicle) -> None:
    """Emit the delta NEW event (same shape as pipeline.ingest)."""
    await conn.execute(
        "INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type, "
        "old_value, new_value) VALUES ($1,$2,$3,'NEW',NULL,$4::jsonb)",
        ulid(), vulid, dealer_ulid, json.dumps({"price": v.price, "title": v.title,
                                                "platform": AS24_TRADE_NAME}))


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


async def harvest(max_pages: int = DEFAULT_MAX_PAGES) -> dict:
    conn = await asyncpg.connect(DSN)
    engine = FetchEngine()  # one fingerprint + cookie jar for the whole drain
    stats = {
        "pages_fetched": 0, "listings_seen": 0, "dealer_listings": 0,
        "private_skipped": 0, "geo_skipped": 0, "dealers_distinct": set(),
        "new_dealers": 0, "cars_caged": 0, "new_cars": 0, "edges_created": 0,
        "new_events": 0, "declared_full": None, "dup_ids_collapsed": 0,
    }
    # Harvest-side truth for the VAM: distinct CAGEABLE cars = distinct
    # (dealer_source_id, deep_link) pairs that survived dealer-parse + geo-resolution.
    # This is the like-with-like counterpart to db_edges (raw listing ids include
    # private sellers + cross-page dupes, so they are NOT comparable to edges).
    harvested_cageable: set[tuple[str, str]] = set()
    # P4 S-HEALTH gate: if AS24's circuit breaker is OPEN (a recent ban/throttle still
    # cooling), skip the drain gracefully — the API keeps serving the last good snapshot
    # ("no se cae"). The breaker re-arms to half_open once its cooldown elapses (one probe).
    if await is_open(conn, AS24_SOURCE_KEY):
        print(f"[as24_wholesale] breaker OPEN for {AS24_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, API still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": AS24_SOURCE_KEY}

    # P1 GOVERNOR: the single choke point in front of engine.fetch. EVERY page fetch for
    # this host passes through the per-host token bucket, so no matter how many drains run
    # in parallel, AS24 is never fetched faster than its bucket (the 4x-scar fix, 04 §5).
    gov = governor()
    governed_fetch = gov.wrap_fetch_text(engine.fetch_text)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = as24_platform_cdp_code()
        print(f"[as24_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid})")
        print(f"[as24_wholesale] governor paces host {host_of(_BASE)} (per-host token bucket).")
        print(f"[as24_wholesale] PROOF SLICE cap = {max_pages} pages "
              f"(~{max_pages * PAGE_SIZE} cars). NOT the full ~278k set (full drain = P1 governed).")

        seen_listing_ids: set[str] = set()
        # dealers we INSERTED this run (to count new_dealers without a pre-count race)
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        for page in range(1, max_pages + 1):
            url = _lst_url(page)
            try:
                html = await governed_fetch(url)   # paced by the host bucket, off the event loop
            except Exception as e:  # noqa: BLE001 — throttle/transient: back off, report what we got
                fetch_error = str(e)
                last_http = getattr(engine, "last_status", None)
                print(f"[as24_wholesale] page {page} fetch failed ({e}); stopping drain honestly.")
                break
            stats["pages_fetched"] += 1
            data = _next_data(html)
            if stats["declared_full"] is None:
                n = _find(data, "numberOfResults")
                stats["declared_full"] = int(n) if n is not None else None
            listings = _find_listings(data)
            if not listings:
                print(f"[as24_wholesale] page {page}: no listings; stopping.")
                break

            for raw in listings:
                stats["listings_seen"] += 1
                listing_id = str(raw.get("id") or raw.get("identifier") or "")
                if listing_id and listing_id in seen_listing_ids:
                    stats["dup_ids_collapsed"] += 1
                    continue  # cross-page dedup on the live set (stable-sort hazard guard)
                if listing_id:
                    seen_listing_ids.add(listing_id)

                d = parse_listing_dealer(raw)
                if d is None:
                    stats["private_skipped"] += 1
                    continue
                stats["dealer_listings"] += 1

                async with conn.transaction():
                    dealer_ulid = await upsert_dealer(conn, geo, d)
                    if dealer_ulid is None:
                        stats["geo_skipped"] += 1
                        continue
                    v = parse_listing_vehicle(raw)
                    if not v.deep_link:
                        continue
                    # harvest-side cageable truth (like-with-like vs db_edges): one
                    # distinct car == one (dealer, deep_link) pair. Two AS24 ad ids for
                    # the same car at the same dealer collapse to one edge by design.
                    harvested_cageable.add((d.source_dealer_id, v.deep_link))
                    vulid, veh_new = await upsert_vehicle(conn, dealer_ulid, v)
                    stats["cars_caged"] += 1
                    if veh_new:
                        stats["new_cars"] += 1
                        await emit_new_event(conn, vulid, dealer_ulid, v)
                        stats["new_events"] += 1
                    edge_new = await link_platform(conn, platform_ulid, vulid, v, listing_id)
                    if edge_new:
                        stats["edges_created"] += 1

            print(f"[as24_wholesale] page {page}: listings={len(listings)} "
                  f"caged_total={stats['cars_caged']} edges={stats['edges_created']}")

        # distinct dealers + new dealers (post-run, authoritative from DB)
        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        # Persist the versioned recipe for the AS24 platform.
        recipe_path = write_recipe(platform_code, AS24_PLATFORM_RECIPE)
        print(f"[as24_wholesale] recipe written: {recipe_path}")

        # VAM count quorum for the slice. THREE ORTHOGONAL, LIKE-WITH-LIKE paths that
        # all measure "distinct cageable cars in this slice" (so they CAN agree —
        # raw listing ids include private sellers + cross-page dupes and are NOT the
        # edge count, which was the bug in the first cut):
        #   db_edges          = platform_listing rows for AS24       (DB write truth)
        #   db_join_vehicles  = distinct vehicles reachable via the edge join (DB read truth)
        #   harvested_cageable= distinct (dealer, deep_link) pulled  (harvest-side truth)
        # The declared full count (279k) is reported for honesty but is NOT a quorum
        # path: it measures the WHOLE platform, not this 12-page slice (apples/oranges).
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
        stats["harvested_distinct_ids"] = len(seen_listing_ids)
        stats["platform_code"] = platform_code
        stats["platform_ulid"] = platform_ulid
        stats["recipe_path"] = str(recipe_path)

        # P4 S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks AS24's
        # health, trips the breaker on a ban, and auto-repairs. A run is OK when at least
        # one page was fetched and no fetch error stopped the drain; a REFUTED VAM or a
        # fetch failure is a fail that feeds the breaker + the exact-origin alert.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        # B9 coverage gate: declared_full = numberOfResults from the first SSR page.
        # harvested_cageable = distinct (dealer_id, deep_link) pairs from the drain.
        outcome = await record_run(
            conn, AS24_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http,
            declared_total=stats.get("declared_full"),
            captured_distinct=stats.get("harvested_cageable"),
            platform_ulid=platform_ulid)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            # the failure is typed, alerted with the exact origin, and a repair is logged.
            stats["repair_action"] = await auto_repair(
                conn, AS24_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    print("\n" + "=" * 64)
    print("AS24 WHOLESALE HARVEST — PROOF SLICE REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  declared full (source): {stats.get('declared_full')}  (NOT harvested — proof slice)")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  listings seen         : {stats['listings_seen']}")
    print(f"  dealer listings       : {stats['dealer_listings']}")
    print(f"  private skipped       : {stats['private_skipped']}")
    print(f"  dup listing ids        : {stats.get('dup_ids_collapsed')} (cross-page, collapsed)")
    print(f"  geo skipped (bad zip) : {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for AS24 = {stats.get('db_edges')})")
    print(f"  NEW delta events      : {stats['new_events']}")
    print("  --- VAM count quorum (like-with-like, this slice) ---")
    print(f"  harvested_cageable    : {stats.get('harvested_cageable')}")
    print(f"  db_edges              : {stats.get('db_edges')}")
    print(f"  db_join_vehicles      : {stats.get('db_join_vehicles')}")
    print(f"  VAM verdict           : {stats.get('verdict')}")
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
    max_pages = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MAX_PAGES
    stats = asyncio.run(harvest(max_pages))
    _print_report(stats)


if __name__ == "__main__":
    main()
