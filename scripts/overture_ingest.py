"""Overture Maps Places -> CARDEEP entity ingestor (B5.5).

Discovers Spanish car dealers / garages / junkyards from Overture Maps
(release 2026-04-15.0) that are NOT already present in the entity table.
Inserts only genuinely new entities (ON CONFLICT cdp_code → update last_seen).

Usage:
    python scripts/overture_ingest.py [--dry-run] [--limit N]

Flags:
    --dry-run   Print stats without writing to DB
    --limit N   Process at most N POIs (for testing)

Cost: €0 (Azure public bucket, no auth required).
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import asyncpg
import duckdb

# ---------------------------------------------------------------------------
# Make sure the project root is on sys.path so local imports work
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from pipeline.geo import GeoResolver
from pipeline.geocode import MunicipalityGeocoder, ProvinceGeocoder
from pipeline.ids import ulid
from services.api.codes import cdp_code

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("overture_ingest")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DSN = os.environ.get(
    "CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep"
)

_AZURE_CONN = (
    "DefaultEndpointsProtocol=https;"
    "AccountName=overturemapswestus2;"
    "EndpointSuffix=core.windows.net"
)

_OVERTURE_RELEASE = "2026-04-15.0"
_PARQUET_GLOB = (
    f"azure://release/{_OVERTURE_RELEASE}/theme=places/type=place/*.parquet"
)

# Spain bounding box (rectangular pre-filter; country=ES finalises)
_SPAIN_LON_MIN = -9.5
_SPAIN_LON_MAX = 4.5
_SPAIN_LAT_MIN = 35.5
_SPAIN_LAT_MAX = 44.0

# Categories that identify vehicle *sellers* -> kind='compraventa'
_SELLER_CATEGORIES: frozenset[str] = frozenset({
    "car_dealer",
    "used_car_dealer",
    "automotive_dealer",
    "truck_dealer",
    "truck_dealer_for_businesses",
    "commercial_vehicle_dealer",
    "motorcycle_dealer",
    "motorsport_vehicle_dealer",
    "car_broker",
    "car_auction",
    "auto_manufacturers_and_distributors",
})

# Categories that identify workshops / garages -> kind='garaje'
_REPAIR_CATEGORIES: frozenset[str] = frozenset({
    "automotive_repair",
    "auto_body_shop",
    "automotive_services_and_repair",
    "auto_electrical_repair",
    "auto_customization",
    "auto_restoration_services",
    "motorcycle_repair",
    "recreation_vehicle_repair",
    "motorsport_vehicle_repair",
    "automotive",  # generic; treated as garaje unless sells_cars flag comes from other source
})

# Junkyards -> kind='desguace'
_JUNKYARD_CATEGORIES: frozenset[str] = frozenset({"junkyard"})

# Auction -> kind='subasta'
_AUCTION_CATEGORIES: frozenset[str] = frozenset({"car_auction"})

# Only VEHICLE SELLERS + junkyards + auctions are swept. Repair workshops (automotive_repair,
# auto_body_shop, generic 'automotive') are NOT points of sale — the goal's "garaje" is an informal
# seller that SELLS cars, not a mechanic that repairs them. Ingesting workshops floods the dataset
# with ~21k non-selling POIs ("Talleres...", "Chapistería...") that carry no inventory.
# _REPAIR_CATEGORIES stays defined above only for _map_kind's defensive fallback; it is NOT swept.
_ALL_CATEGORIES = (
    _SELLER_CATEGORIES
    | _JUNKYARD_CATEGORIES
    | _AUCTION_CATEGORIES
)

# ---------------------------------------------------------------------------
# DuckDB extraction
# ---------------------------------------------------------------------------


@dataclass
class OverturePlace:
    """Minimal POI extracted from Overture parquet."""

    overture_id: str
    name: str
    category: str
    lat: float
    lon: float
    locality: Optional[str]
    postcode: Optional[str]
    address_freeform: Optional[str]
    website: Optional[str]
    confidence: float


def _build_duckdb_connection() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(database=":memory:")
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("INSTALL spatial; LOAD spatial;")
    con.execute(f"SET azure_storage_connection_string='{_AZURE_CONN}';")
    con.execute("SET enable_progress_bar=false;")
    return con


def _cat_list_sql(cats: frozenset[str]) -> str:
    return ", ".join(f"'{c}'" for c in sorted(cats))


def fetch_spain_automotive_pois(
    limit: Optional[int] = None,
) -> list[OverturePlace]:
    """Download and filter Spain automotive POIs from Overture via DuckDB."""
    con = _build_duckdb_connection()

    all_cats_sql = _cat_list_sql(_ALL_CATEGORIES)
    limit_clause = f"LIMIT {limit}" if limit else ""

    query = f"""
    SELECT
        id,
        names.primary            AS name,
        categories.primary       AS category,
        ST_Y(geometry)           AS lat,
        ST_X(geometry)           AS lon,
        addresses[1].locality    AS locality,
        addresses[1].postcode    AS postcode,
        addresses[1].freeform    AS address_freeform,
        websites[1]              AS website,
        confidence
    FROM read_parquet('{_PARQUET_GLOB}')
    WHERE bbox.xmin BETWEEN {_SPAIN_LON_MIN} AND {_SPAIN_LON_MAX}
      AND bbox.ymin BETWEEN {_SPAIN_LAT_MIN} AND {_SPAIN_LAT_MAX}
      AND addresses[1].country = 'ES'
      AND categories.primary IN ({all_cats_sql})
      AND names.primary IS NOT NULL
      AND names.primary != ''
    {limit_clause}
    """

    log.info("Querying Overture parquet (release %s) for Spain automotive POIs...",
             _OVERTURE_RELEASE)
    rows = con.execute(query).fetchall()
    log.info("Raw Overture rows fetched: %d", len(rows))

    places: list[OverturePlace] = []
    for row in rows:
        (oid, name, cat, lat, lon, locality, postcode, addr_freeform, website, conf) = row
        if not name or not lat or not lon:
            continue
        places.append(OverturePlace(
            overture_id=oid or "",
            name=name,
            category=cat or "",
            lat=float(lat),
            lon=float(lon),
            locality=locality or None,
            postcode=postcode or None,
            address_freeform=addr_freeform or None,
            website=website or None,
            confidence=float(conf) if conf is not None else 0.0,
        ))
    con.close()
    log.info("Valid POIs (name + coords): %d", len(places))
    return places


# ---------------------------------------------------------------------------
# Kind mapping
# ---------------------------------------------------------------------------


def _map_kind(category: str) -> str:
    if category in _JUNKYARD_CATEGORIES:
        return "desguace"
    if category in _AUCTION_CATEGORIES:
        return "subasta"
    if category in _SELLER_CATEGORIES:
        return "compraventa"
    # repair / automotive generic
    return "garaje"


def _sells_cars(category: str) -> bool:
    """True only for unambiguous vehicle sellers; garajes left NULL downstream."""
    return category in (_SELLER_CATEGORIES | _JUNKYARD_CATEGORIES | _AUCTION_CATEGORIES)


# ---------------------------------------------------------------------------
# Name normalization (mirrors pipeline.identity._normalize_name)
# ---------------------------------------------------------------------------

_LEGAL_SUFFIX_RE = re.compile(
    r"\b(s\s?l\s?u?|s\s?a\s?u?|s\s?c\s?p?|sociedad limitada|sociedad anonima)\b"
)


def _normalize_name(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9 ]+", " ", text.lower())
    text = _LEGAL_SUFFIX_RE.sub(" ", text)
    return re.sub(r"\s+", "", text)


def _bare_host(url: str | None) -> str | None:
    """Extract bare hostname from URL if it's a dealer's own domain (no path)."""
    if not url:
        return None
    u = re.sub(r"^https?://", "", url.lower().strip())
    u = re.sub(r"^www\.", "", u)
    u = u.split("?")[0].split("#")[0].rstrip("/")
    host, _, path = u.partition("/")
    return host if host and not path else None


# ---------------------------------------------------------------------------
# Existing-entity dedup index
# ---------------------------------------------------------------------------


@dataclass
class _DedupeKey:
    name_norm: str
    municipality_code: Optional[str]
    province_code: Optional[str]
    bare_host: Optional[str]


async def _build_existing_index(
    conn: asyncpg.Connection,
) -> tuple[set[str], set[str], dict[str, str]]:
    """Build three in-memory lookup structures from existing entity rows.

    Returns:
        cdp_codes_set: all existing cdp_codes (for conflict detection)
        host_set:      bare hostnames that already exist
        name_muni_set: set of "norm_name|muni5" keys
    """
    rows = await conn.fetch(
        "SELECT cdp_code, website, trade_name, legal_name, municipality_code "
        "FROM entity "
        "WHERE status != 'closed'"
    )
    cdp_set: set[str] = set()
    host_set: set[str] = set()
    name_muni_set: set[str] = set()

    for r in rows:
        cdp_set.add(r["cdp_code"])
        h = _bare_host(r["website"])
        if h:
            host_set.add(h)
        name = r["trade_name"] or r["legal_name"] or ""
        muni = r["municipality_code"]
        if name and muni:
            name_muni_set.add(f"{_normalize_name(name)}|{muni}")

    log.info(
        "Existing-entity index built: %d cdp_codes, %d hosts, %d name+muni keys",
        len(cdp_set), len(host_set), len(name_muni_set),
    )
    return cdp_set, host_set, name_muni_set


def _is_duplicate(
    place: OverturePlace,
    prov: Optional[str],
    muni: Optional[str],
    cdp_set: set[str],
    host_set: set[str],
    name_muni_set: set[str],
    code: str,
) -> bool:
    """Return True if this POI matches an existing entity."""
    # 1. Exact cdp_code (deterministic hash)
    if code in cdp_set:
        return True
    # 2. Bare host match
    h = _bare_host(place.website)
    if h and h in host_set:
        return True
    # 3. Normalized name + municipality
    if muni:
        key = f"{_normalize_name(place.name)}|{muni}"
        if key in name_muni_set:
            return True
    return False


# ---------------------------------------------------------------------------
# Geo resolution
# ---------------------------------------------------------------------------


async def _resolve_geo(
    place: OverturePlace,
    geo_resolver: GeoResolver,
    prov_geocoder: ProvinceGeocoder,
    muni_geocoder: MunicipalityGeocoder,
) -> tuple[Optional[str], Optional[str]]:
    """Resolve (province_code, municipality_code) for a POI.

    Cascade:
    1. GeoResolver: locality name -> province + municipality (fuzzy, gazetteer)
    2. lat/lon reverse-geocode via MunicipalityGeocoder (B4.3)
    3. Postcode -> municipality via PostcodeIndex (if available)
    """
    province_code: Optional[str] = None
    municipality_code: Optional[str] = None

    # Step 1: try name-based resolution from locality
    if place.locality:
        province_code = geo_resolver.province_code(place.locality)
        if province_code:
            municipality_code = geo_resolver.municipality_code(
                province_code, place.locality
            )

    # Step 2: lat/lon reverse-geocode for province (if not resolved)
    if not province_code:
        province_code = prov_geocoder.nearest_province(place.lat, place.lon)

    # Step 3: KNN municipality (B4.3, 30km threshold)
    if province_code and not municipality_code:
        muni_code, dist_km = muni_geocoder.nearest_municipality(
            place.lat, place.lon, province_code
        )
        if muni_code:
            municipality_code = muni_code

    return province_code, municipality_code


# ---------------------------------------------------------------------------
# DB insertion
# ---------------------------------------------------------------------------

_INSERT_SQL = """
INSERT INTO entity (
    entity_ulid, cdp_code, kind, trade_name,
    province_code, municipality_code,
    address, postcode, lat, lon,
    website, website_waf,
    is_tier1, status,
    first_discovered_source, kind_source, source_group,
    sells_cars, geocode_source,
    created_at, last_seen
)
VALUES (
    $1, $2, $3::entity_kind, $4,
    $5, $6,
    $7, $8, $9, $10,
    $11, 'none'::waf_kind,
    FALSE, 'unverified'::entity_status,
    'overture', 'platform_label'::kind_source, 'directory'::source_group,
    $12, 'overture_latlon',
    NOW(), NOW()
)
ON CONFLICT (cdp_code) DO UPDATE SET last_seen = NOW()
RETURNING (xmax = 0) AS is_new_row
"""


async def run(dry_run: bool = False, limit: Optional[int] = None) -> None:
    # ---- 1. Fetch Overture POIs ----
    places = fetch_spain_automotive_pois(limit=limit)

    total_pois = len(places)
    log.info("Total Spain automotive POIs from Overture: %d", total_pois)

    # ---- 2. Connect to DB and load geo indexes ----
    conn = await asyncpg.connect(_DSN)
    try:
        geo_resolver = await GeoResolver.load(conn)
        prov_geocoder = await ProvinceGeocoder.load(conn)
        muni_geocoder = await MunicipalityGeocoder.load(conn)
        existing_cdp, existing_hosts, existing_name_muni = await _build_existing_index(conn)

        # ---- 3. Process each POI ----
        stats = {
            "total": total_pois,
            "no_province": 0,
            "duplicate": 0,
            "inserted": 0,
            "conflict_updated": 0,
            "error": 0,
        }
        province_counts: dict[str, int] = {}
        inserted_sample: list[dict] = []

        for place in places:
            try:
                prov, muni = await _resolve_geo(
                    place, geo_resolver, prov_geocoder, muni_geocoder
                )

                if not prov:
                    stats["no_province"] += 1
                    continue

                # Compute deterministic cdp_code
                host = _bare_host(place.website)
                code = cdp_code(
                    province_code=prov,
                    domain=host,
                    name=place.name,
                    municipality_code=muni,
                )

                # Dedup check against in-memory index
                if _is_duplicate(place, prov, muni,
                                  existing_cdp, existing_hosts, existing_name_muni, code):
                    stats["duplicate"] += 1
                    continue

                kind = _map_kind(place.category)
                sells = _sells_cars(place.category)

                if dry_run:
                    stats["inserted"] += 1
                    province_counts[prov] = province_counts.get(prov, 0) + 1
                    if len(inserted_sample) < 15:
                        inserted_sample.append({
                            "name": place.name,
                            "kind": kind,
                            "category": place.category,
                            "lat": round(place.lat, 5),
                            "lon": round(place.lon, 5),
                            "province_code": prov,
                            "municipality_code": muni,
                            "locality": place.locality,
                            "website": place.website,
                            "cdp_code": code,
                        })
                    # Register in local dedup index so siblings don't re-insert
                    existing_cdp.add(code)
                    if host:
                        existing_hosts.add(host)
                    if muni:
                        existing_name_muni.add(f"{_normalize_name(place.name)}|{muni}")
                    continue

                # Real INSERT
                entity_ulid = ulid()
                row = await conn.fetchrow(
                    _INSERT_SQL,
                    entity_ulid,
                    code,
                    kind,
                    place.name,
                    prov,
                    muni,
                    place.address_freeform,
                    place.postcode,
                    place.lat,
                    place.lon,
                    place.website,
                    sells,
                )

                is_new = row["is_new_row"] if row else False
                if is_new:
                    stats["inserted"] += 1
                    province_counts[prov] = province_counts.get(prov, 0) + 1
                    # Update local dedup index to block duplicates within this batch
                    existing_cdp.add(code)
                    if host:
                        existing_hosts.add(host)
                    if muni:
                        existing_name_muni.add(f"{_normalize_name(place.name)}|{muni}")
                    if len(inserted_sample) < 15:
                        inserted_sample.append({
                            "name": place.name,
                            "kind": kind,
                            "category": place.category,
                            "lat": round(place.lat, 5),
                            "lon": round(place.lon, 5),
                            "province_code": prov,
                            "municipality_code": muni,
                            "locality": place.locality,
                            "website": place.website,
                            "cdp_code": code,
                        })
                else:
                    stats["conflict_updated"] += 1

            except Exception as exc:
                log.warning("Error processing POI '%s': %s", place.name, exc)
                stats["error"] += 1

        # ---- 4. Report ----
        log.info("=== OVERTURE INGEST COMPLETE ===")
        log.info("Total POIs from Overture (ES, automotive): %d", stats["total"])
        log.info("No province resolved: %d", stats["no_province"])
        log.info("Duplicate (skipped): %d", stats["duplicate"])
        log.info("Inserted (new): %d", stats["inserted"])
        log.info("Updated last_seen (existing): %d", stats["conflict_updated"])
        log.info("Errors: %d", stats["error"])

        geo_resolved = stats["total"] - stats["no_province"] - stats["error"]
        geo_pct = (geo_resolved / stats["total"] * 100) if stats["total"] else 0
        log.info("Geo resolution rate: %.1f%% (%d / %d)", geo_pct, geo_resolved, stats["total"])

        log.info("--- Top provinces by new discovery ---")
        for prov, count in sorted(province_counts.items(), key=lambda x: -x[1])[:15]:
            log.info("  %s: %d", prov, count)

        log.info("--- Sample of 15 new entities ---")
        for item in inserted_sample:
            log.info(
                "  [%s] %s | %s→%s | %s | %s",
                item["kind"],
                item["name"][:50],
                item.get("locality", ""),
                item.get("municipality_code", ""),
                item["province_code"],
                item.get("website", ""),
            )

        if dry_run:
            log.info("[DRY RUN] No writes made to DB.")

        print("\n=== OVERTURE INGEST SUMMARY ===")
        print(f"Release: {_OVERTURE_RELEASE}")
        print(f"Spain automotive POIs in Overture: {stats['total']}")
        print(f"  - car sellers (compraventa): "
              f"{sum(1 for p in places if _map_kind(p.category) == 'compraventa')}")
        print(f"  - garajes/repair: "
              f"{sum(1 for p in places if _map_kind(p.category) == 'garaje')}")
        print(f"  - desguaces: "
              f"{sum(1 for p in places if _map_kind(p.category) == 'desguace')}")
        print(f"Duplicates (already in DB): {stats['duplicate']}")
        print(f"No province resolved: {stats['no_province']}")
        print(f"NEW entities inserted: {stats['inserted']}")
        if not dry_run:
            print(f"Existing entities updated (last_seen): {stats['conflict_updated']}")
        print(f"Geo resolution rate: {geo_pct:.1f}%")
        print(f"Top 5 provinces by new discovery:")
        for prov, count in sorted(province_counts.items(), key=lambda x: -x[1])[:5]:
            print(f"  Province {prov}: {count} new")

    finally:
        await conn.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true",
                   help="Count new entities without writing to DB")
    p.add_argument("--limit", type=int, default=None,
                   help="Max POIs to process (for testing)")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(run(dry_run=args.dry_run, limit=args.limit))
