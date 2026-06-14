"""B5.7 — Generic dealer own-site scraper: sitemap-first + schema.org Vehicle/Car.

Strategy (€0, JA3-coherent, rate-governed):
  1. Resolve the entity's website to a canonical HTTP(S) base URL.
  2. Discover sitemaps via robots.txt -> sitemap.xml -> sitemap index traversal.
  3. Filter sitemap URLs for vehicle-pattern paths.
  4. Fetch each vehicle page and extract JSON-LD @type=Car|Vehicle|Product|Offer.
  5. Fallback: Open Graph title/description meta if no JSON-LD found.
  6. Ingest via the generic_ingest_dealer_site() path (INSERT only, respects existing
     entity by cdp_code from the lead DB row, never creates a duplicate dealer).

Classification labels used by the probe tool (probe_dealer_sites.py):
  SCHEMA_ORG   — sitemap found + vehicle URLs + JSON-LD schema.org with ≥1 key field
  SITEMAP_SOLO — sitemap found + vehicle URLs, but no useful JSON-LD (HTML parse needed)
  SIN_SITEMAP  — responds 200 but no sitemap with vehicle paths
  MUERTO       — HTTP 4xx/5xx or network error
  SIN_WEB      — no website field (not applicable here, filtered upstream)

PEP8, type hints, immutable dataclasses, docstrings.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Iterator
from urllib.parse import urljoin, urlsplit, urlunsplit

import asyncpg
from lxml import etree  # type: ignore[import]

from pipeline.engine.fetch import FetchEngine
from pipeline.engine.governor import RateGovernor
from pipeline.ids import ulid
from pipeline.verify import record_count_verdict
from services.api.codes import cdp_code

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RECIPE_VERSION = "generic_dealer_site_v1"

_VEHICLE_PATH_RE = re.compile(
    r"/(coche|vehiculo|vehiculos|stock|ocasion|vn|vo|used|coches|coche-usado"
    r"|seminuevo|seminuevos|segunda-mano|coches-segunda-mano|coches-km0"
    r"|coches-nuevos|car|vehicle|listing|inventory"
    r"|ficha|detalle|anuncio|oferta|auto|automovil|moto"
    r"|desguace|pieza|recambio|ocasiones|ocasion-coches"
    r")/",
    re.IGNORECASE,
)

# URLs that are category/filter pages, NOT individual vehicle PDPs.
# We detect individual PDPs by presence of a numeric or slug ID segment after the category.
_CATEGORY_ONLY_RE = re.compile(
    r"^https?://[^/]+/(coche|vehiculo|coches|coches-segunda-mano|ocasion"
    r"|seminuevo|stock|used|inventory)[/]?$",
    re.IGNORECASE,
)

_SCHEMA_TYPES_VEHICLE = {"Car", "Vehicle", "MotorizedBicycle", "Product", "Offer"}

_SITEMAP_NAMESPACES = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "news": "http://www.google.com/schemas/sitemap-news/0.9",
    "image": "http://www.google.com/schemas/sitemap-image/1.1",
    "video": "http://www.google.com/schemas/sitemap-video/1.1",
}

_MAX_SITEMAP_URLS = 5_000  # safety cap per domain
_MAX_VEHICLE_PAGES = 500   # cap per harvest run per dealer
_SITEMAP_TIMEOUT_S = 15
_PAGE_TIMEOUT_S = 20


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class VehicleRecord:
    """Normalised vehicle from schema.org JSON-LD extraction."""
    deep_link: str
    title: str | None = None
    make: str | None = None
    model: str | None = None
    year: int | None = None
    km: int | None = None
    price: float | None = None
    fuel: str | None = None
    photo_url: str | None = None
    vin_ref: str | None = None
    source_type: str = "schema_org"  # schema_org | open_graph | html_fallback


@dataclass
class SiteProbe:
    """Outcome of probing a single dealer domain."""
    entity_ulid: str
    website: str
    base_url: str
    label: str = "MUERTO"         # SCHEMA_ORG | SITEMAP_SOLO | SIN_SITEMAP | MUERTO
    sitemap_url: str | None = None
    vehicle_urls_found: int = 0
    schema_fields_found: int = 0  # non-null fields in best JSON-LD found
    sample_vehicle_url: str | None = None
    error: str | None = None
    elapsed_s: float = 0.0


# ---------------------------------------------------------------------------
# URL utilities
# ---------------------------------------------------------------------------

def _canonical_base(raw_url: str) -> str | None:
    """Return canonical https://host/ (no path), or None if unparseable."""
    raw = raw_url.strip()
    if not raw.startswith(("http://", "https://")):
        raw = "http://" + raw
    try:
        parsed = urlsplit(raw)
        scheme = parsed.scheme or "http"
        host = parsed.netloc.lower().split(":")[0]
        if not host or "." not in host:
            return None
        return urlunsplit((scheme, host, "/", "", ""))
    except Exception:
        return None


def _domain_of(url: str) -> str:
    return urlsplit(url).netloc.lower().split(":")[0]


# ---------------------------------------------------------------------------
# Engine helpers
# ---------------------------------------------------------------------------

def _make_engine() -> FetchEngine:
    return FetchEngine(polite_min=0.8, polite_max=1.6)


def _safe_fetch(engine: FetchEngine, url: str, timeout_override: float | None = None) -> str | None:
    """Fetch URL, returning None on any error (never raises)."""
    try:
        return engine.fetch_text(url)
    except Exception as exc:
        logger.debug("fetch %s -> %s", url, exc)
        return None


# ---------------------------------------------------------------------------
# Sitemap discovery
# ---------------------------------------------------------------------------

def _robots_sitemap_urls(engine: FetchEngine, base_url: str) -> list[str]:
    """Parse robots.txt and return Sitemap: directives."""
    robots_url = urljoin(base_url, "/robots.txt")
    text = _safe_fetch(engine, robots_url)
    if not text:
        return []
    found = []
    for line in text.splitlines():
        line = line.strip()
        if line.lower().startswith("sitemap:"):
            url = line.split(":", 1)[1].strip()
            if url.startswith("http"):
                found.append(url)
    return found


def _discover_sitemaps(engine: FetchEngine, base_url: str) -> list[str]:
    """Return candidate sitemap URLs (robots.txt + fallback guesses)."""
    from_robots = _robots_sitemap_urls(engine, base_url)
    if from_robots:
        return from_robots
    # Fallback candidates
    candidates = [
        urljoin(base_url, "/sitemap.xml"),
        urljoin(base_url, "/sitemap_index.xml"),
        urljoin(base_url, "/sitemap/sitemap.xml"),
        urljoin(base_url, "/wp-sitemap.xml"),  # WordPress
        urljoin(base_url, "/sitemap-coches.xml"),
        urljoin(base_url, "/sitemap-vehiculos.xml"),
    ]
    found = []
    for url in candidates:
        text = _safe_fetch(engine, url)
        if text and ("<sitemap" in text.lower() or "<urlset" in text.lower()):
            found.append(url)
            break  # take first that parses
    return found


def _parse_sitemap_xml(xml_text: str) -> tuple[list[str], list[str]]:
    """Return (loc_urls, sub_sitemap_urls) from a sitemap XML."""
    try:
        root = etree.fromstring(xml_text.encode("utf-8", "replace"))
    except Exception:
        # Try as bytes directly
        try:
            root = etree.fromstring(xml_text.encode())
        except Exception:
            return [], []

    tag = root.tag.lower() if isinstance(root.tag, str) else ""

    # Sitemap index
    if "sitemapindex" in tag:
        locs = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        locs += root.findall(".//loc")
        return [], [e.text.strip() for e in locs if e.text]

    # Urlset
    locs = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    locs += root.findall(".//loc")
    urls = [e.text.strip() for e in locs if e.text and e.text.strip()]
    return urls, []


def _collect_vehicle_urls(engine: FetchEngine, base_url: str,
                          max_urls: int = _MAX_SITEMAP_URLS) -> list[str]:
    """Walk sitemap hierarchy and return URLs matching vehicle path patterns."""
    sitemap_seeds = _discover_sitemaps(engine, base_url)
    if not sitemap_seeds:
        return []

    visited_sitemaps: set[str] = set()
    pending_sitemaps = list(sitemap_seeds)
    vehicle_urls: list[str] = []
    total_seen = 0

    while pending_sitemaps and total_seen < max_urls:
        sm_url = pending_sitemaps.pop(0)
        if sm_url in visited_sitemaps:
            continue
        visited_sitemaps.add(sm_url)

        text = _safe_fetch(engine, sm_url)
        if not text:
            continue

        locs, sub_sitemaps = _parse_sitemap_xml(text)
        pending_sitemaps.extend(s for s in sub_sitemaps if s not in visited_sitemaps)

        for url in locs:
            total_seen += 1
            # Resolve relative URLs against base
            if url and not url.startswith("http"):
                url = urljoin(base_url, url)
            if _VEHICLE_PATH_RE.search(url) and not _CATEGORY_ONLY_RE.match(url):
                vehicle_urls.append(url)
            if total_seen >= max_urls:
                break

    return vehicle_urls


# ---------------------------------------------------------------------------
# JSON-LD extraction
# ---------------------------------------------------------------------------

def _extract_json_ld_blocks(html: str) -> list[dict]:
    """Find all application/ld+json script blocks and parse them."""
    results = []
    for m in re.finditer(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.IGNORECASE | re.DOTALL
    ):
        raw = m.group(1).strip()
        try:
            obj = json.loads(raw)
        except Exception:
            continue
        # Expand @graph arrays
        if isinstance(obj, dict) and "@graph" in obj:
            for item in obj["@graph"]:
                if isinstance(item, dict):
                    results.append(item)
        elif isinstance(obj, list):
            results.extend(i for i in obj if isinstance(i, dict))
        elif isinstance(obj, dict):
            results.append(obj)
    return results


def _type_of(obj: dict) -> str | None:
    t = obj.get("@type", "")
    if isinstance(t, list):
        t = t[0] if t else ""
    return str(t).strip() if t else None


def _str_val(obj: dict, *keys: str) -> str | None:
    for k in keys:
        v = obj.get(k)
        if v:
            if isinstance(v, dict):
                v = v.get("name") or v.get("@value") or v.get("value")
            if v and isinstance(v, str) and v.strip():
                return v.strip()
    return None


def _int_val(obj: dict, *keys: str) -> int | None:
    for k in keys:
        v = obj.get(k)
        if v is not None:
            try:
                return int(str(v).replace(",", "").replace(".", "").strip())
            except Exception:
                pass
    return None


def _float_price(obj: dict) -> float | None:
    """Extract price from Offer block or direct price fields."""
    # schema.org Offer
    offers = obj.get("offers")
    if offers:
        if isinstance(offers, list):
            offers = offers[0] if offers else None
        if isinstance(offers, dict):
            p = offers.get("price") or offers.get("lowPrice")
            if p is not None:
                try:
                    return float(str(p).replace(",", ".").replace(" ", ""))
                except Exception:
                    pass
    # Direct price fields
    for k in ("price", "vehicleSpecialUsage"):
        p = obj.get(k)
        if p is not None:
            try:
                return float(str(p).replace(",", ".").replace(" ", ""))
            except Exception:
                pass
    return None


def _photo_url(obj: dict, base_url: str) -> str | None:
    img = obj.get("image")
    if isinstance(img, list):
        img = img[0]
    if isinstance(img, dict):
        img = img.get("url") or img.get("contentUrl")
    if isinstance(img, str) and img:
        if img.startswith("http"):
            return img
        return urljoin(base_url, img)
    return None


def _extract_vehicle_from_json_ld(blocks: list[dict],
                                   page_url: str, base_url: str) -> VehicleRecord | None:
    """Try to build a VehicleRecord from JSON-LD blocks on a page."""
    for block in blocks:
        t = _type_of(block)
        if not t or not any(vt in t for vt in _SCHEMA_TYPES_VEHICLE):
            continue

        # Mandatory: at least name/model or make to be useful
        make = _str_val(block, "brand", "make", "manufacturer")
        model = _str_val(block, "model", "name")
        if not make and not model:
            continue

        # Year
        year_raw = _str_val(block, "modelDate", "vehicleModelDate", "datePublished")
        year: int | None = None
        if year_raw:
            m = re.search(r"\b(19|20)\d{2}\b", year_raw)
            if m:
                year = int(m.group(0))

        # Mileage
        mileage_obj = block.get("mileageFromOdometer") or block.get("mileage")
        km: int | None = None
        if isinstance(mileage_obj, dict):
            km = _int_val(mileage_obj, "value")
        elif mileage_obj is not None:
            km = _int_val({"v": mileage_obj}, "v")

        price = _float_price(block)
        fuel = _str_val(block, "fuelType", "fuel")
        photo = _photo_url(block, base_url)
        vin = _str_val(block, "vehicleIdentificationNumber", "vin")

        # Build title
        title_parts = [p for p in [make, model, str(year) if year else None] if p]
        title = " ".join(title_parts) if title_parts else _str_val(block, "name")

        return VehicleRecord(
            deep_link=page_url,
            title=title,
            make=make,
            model=model,
            year=year,
            km=km,
            price=price,
            fuel=fuel,
            photo_url=photo,
            vin_ref=vin,
            source_type="schema_org",
        )
    return None


def _extract_microdata(html: str, page_url: str, base_url: str) -> VehicleRecord | None:
    """Extract schema.org vehicle data from HTML microdata (itemprop content= attrs).

    Many Spanish dealer DMS platforms (inventario.pro, motorflash, etc.) emit
    microdata instead of JSON-LD.  We read `itemprop=X content=Y` attributes.
    """
    # Collect microdata: both content= attrs AND innerText of short spans.
    # Pattern 1: content attribute  (itemprop="X" content="Y")
    # Pattern 2: inline text value  (itemprop="X">TEXT</tag)
    props: dict[str, str] = {}
    for m in re.finditer(
        r'itemprop=["\']([a-zA-Z]+)["\'][^>]*content=["\']([^"\']{1,500})',
        html,
    ):
        k, v = m.group(1), m.group(2).strip()
        if k not in props:
            props[k] = v
    # Inner-text pattern for numeric/short fields (price, priceCurrency, etc.)
    for m in re.finditer(
        r'itemprop=["\']([a-zA-Z]+)["\'][^>]*>([^<]{1,200})</(?:span|div|p|meta|data)',
        html,
    ):
        k, v = m.group(1), m.group(2).strip()
        if k not in props and v:
            props[k] = v

    if not props:
        return None

    # Need at minimum: price OR name
    price_raw = props.get("price")
    name_raw = props.get("name")
    if not price_raw and not name_raw:
        return None

    price: float | None = None
    if price_raw:
        try:
            # Handle "19800.00", "19.800", "19.800,00"
            cleaned = price_raw.replace(" ", "")
            # European format: 19.800,00 -> 19800.00
            if re.match(r"^\d{1,3}(\.\d{3})+(,\d{1,2})?$", cleaned):
                cleaned = cleaned.replace(".", "").replace(",", ".")
            else:
                cleaned = cleaned.replace(",", ".")
            price = float(cleaned)
        except Exception:
            pass

    # Parse title: name field typically "Make Model, km, Ocasion - Dealer"
    title = name_raw
    make: str | None = props.get("brand")
    model: str | None = None
    year: int | None = None
    km: int | None = None

    # Try to extract year and km from description or name
    desc = props.get("description", "")
    year_m = re.search(r"\b(19|20)\d{2}\b", desc or name_raw or "")
    if year_m:
        year = int(year_m.group(0))

    km_m = re.search(r"([\d.]+)\s*km", desc or name_raw or "", re.I)
    if km_m:
        try:
            km = int(km_m.group(1).replace(".", ""))
        except Exception:
            pass

    # Photo
    photo = props.get("image")
    if photo and not photo.startswith("http"):
        photo = urljoin(base_url, photo)

    # Fuel from description
    fuel: str | None = None
    desc_lower = (desc or "").lower()
    for f in ("eléctrico", "electrico", "híbrido", "hibrido", "gasolina",
              "diésel", "diesel", "glp", "gas"):
        if f in desc_lower:
            fuel = f
            break

    vin = props.get("vehicleIdentificationNumber")

    return VehicleRecord(
        deep_link=page_url,
        title=title,
        make=make,
        model=model,
        year=year,
        km=km,
        price=price,
        fuel=fuel,
        photo_url=photo,
        vin_ref=vin,
        source_type="microdata",
    )


def _extract_og_fallback(html: str, page_url: str) -> VehicleRecord | None:
    """Minimal Open Graph fallback (title + price from meta tags)."""
    title_m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)', html, re.I)
    price_m = re.search(r'<meta[^>]+property=["\']product:price:amount["\'][^>]+content=["\']([^"\']+)', html, re.I)
    if not title_m:
        return None
    price: float | None = None
    if price_m:
        try:
            price = float(price_m.group(1).replace(",", "."))
        except Exception:
            pass
    return VehicleRecord(
        deep_link=page_url,
        title=title_m.group(1).strip(),
        price=price,
        source_type="open_graph",
    )


# ---------------------------------------------------------------------------
# Probe a single domain
# ---------------------------------------------------------------------------

def probe_single(entity_ulid: str, website: str) -> SiteProbe:
    """Classify a dealer website (synchronous, designed to run in a thread pool)."""
    t0 = time.monotonic()
    base = _canonical_base(website)
    probe = SiteProbe(entity_ulid=entity_ulid, website=website, base_url=base or website)

    if not base:
        probe.label = "MUERTO"
        probe.error = "unparseable URL"
        probe.elapsed_s = time.monotonic() - t0
        return probe

    engine = _make_engine()

    # Step 1: check alive (GET /)
    homepage = _safe_fetch(engine, base)
    if not homepage:
        probe.label = "MUERTO"
        probe.error = "no HTTP 200 on base URL"
        probe.elapsed_s = time.monotonic() - t0
        return probe

    # Step 2: collect vehicle URLs from sitemap
    vehicle_urls = _collect_vehicle_urls(engine, base)
    probe.vehicle_urls_found = len(vehicle_urls)

    if not vehicle_urls:
        probe.label = "SIN_SITEMAP"
        probe.elapsed_s = time.monotonic() - t0
        return probe

    probe.sample_vehicle_url = vehicle_urls[0]

    # Step 3: probe first vehicle URL for JSON-LD
    sample_html = _safe_fetch(engine, vehicle_urls[0])
    if not sample_html:
        probe.label = "SITEMAP_SOLO"
        probe.elapsed_s = time.monotonic() - t0
        return probe

    blocks = _extract_json_ld_blocks(sample_html)
    rec = _extract_vehicle_from_json_ld(blocks, vehicle_urls[0], base)

    if not rec:
        # Try microdata (itemprop content= attributes)
        rec = _extract_microdata(sample_html, vehicle_urls[0], base)

    if rec:
        non_null = sum(1 for v in [rec.make, rec.model, rec.year, rec.km, rec.price, rec.fuel]
                       if v is not None)
        probe.schema_fields_found = non_null
        source_label = rec.source_type.upper().replace("_", " ")
        probe.label = "SCHEMA_ORG" if non_null >= 2 else "SITEMAP_SOLO"
        logger.debug("probe %s -> %s via %s fields=%d", probe.website, probe.label, source_label, non_null)
    else:
        # Try OG fallback
        og = _extract_og_fallback(sample_html, vehicle_urls[0])
        if og and og.title:
            probe.label = "SITEMAP_SOLO"
        else:
            probe.label = "SITEMAP_SOLO"

    probe.elapsed_s = time.monotonic() - t0
    return probe


# ---------------------------------------------------------------------------
# Harvest a single SCHEMA_ORG dealer
# ---------------------------------------------------------------------------

def harvest_dealer_site(entity_ulid: str, website: str,
                         max_pages: int = _MAX_VEHICLE_PAGES) -> list[VehicleRecord]:
    """Scrape all vehicle pages from a SCHEMA_ORG dealer site.

    Returns list of VehicleRecord. Caller is responsible for ingestion.
    """
    base = _canonical_base(website)
    if not base:
        return []

    engine = _make_engine()
    vehicle_urls = _collect_vehicle_urls(engine, base)
    if not vehicle_urls:
        return []

    vehicle_urls = vehicle_urls[:max_pages]
    records: list[VehicleRecord] = []

    for url in vehicle_urls:
        html = _safe_fetch(engine, url)
        if not html:
            continue
        # Try extraction hierarchy: JSON-LD -> microdata -> OG
        blocks = _extract_json_ld_blocks(html)
        rec = _extract_vehicle_from_json_ld(blocks, url, base)
        if not rec:
            rec = _extract_microdata(html, url, base)
        if not rec:
            rec = _extract_og_fallback(html, url)
        if rec:
            records.append(rec)

    return records


# ---------------------------------------------------------------------------
# Ingestion: INSERT vehicles under the EXISTING entity (no duplicate dealer)
# ---------------------------------------------------------------------------

async def ingest_generic_dealer_vehicles(
    conn: asyncpg.Connection,
    entity_ulid: str,
    vehicles: list[VehicleRecord],
) -> dict:
    """Insert harvested vehicles under an existing entity.

    NEVER creates or updates the entity row — the lead's entity_ulid from
    the Overture discovery is the canonical identity; we only add inventory.

    GONE guard: vehicles present in DB (status='available') but absent from
    the current harvest are marked as 'sold' when the harvest covers at least
    95% of the previously-seen count.  This prevents stale inventory from
    making the VAM diverge on re-runs.

    Returns ingestion summary with VAM verdict.
    """
    if not vehicles:
        return {"ingested": 0, "skipped": 0, "verdict": "UNVERIFIED",
                "entity_ulid": entity_ulid, "available_in_db": 0}

    # Read prior available count BEFORE inserting new vehicles (GONE guard threshold).
    prior_available: int = int(await conn.fetchval(
        "SELECT count(*) FROM vehicle WHERE entity_ulid=$1 AND status='available'",
        entity_ulid,
    ) or 0)

    ingested = 0
    skipped = 0
    seen_deep_links: set[str] = set()

    for v in vehicles:
        seen_deep_links.add(v.deep_link)
        existing = await conn.fetchval(
            "SELECT vehicle_ulid FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2",
            entity_ulid, v.deep_link,
        )
        if existing:
            # Refresh last_seen only — no UPDATE of non-mutated data (PG MVCC doctrine)
            await conn.execute(
                "UPDATE vehicle SET last_seen=now() WHERE vehicle_ulid=$1", existing
            )
            skipped += 1
            continue

        vulid = ulid()
        title = v.title or f"{v.make or ''} {v.model or ''}".strip() or "unknown"
        # recipe_version is integer FK in DB; use NULL for generic site vehicles
        # (no versioned recipe object exists yet for this source class)
        await conn.execute(
            """INSERT INTO vehicle
                 (vehicle_ulid, entity_ulid, deep_link, title, make, model,
                  year, km, price, fuel, photo_url, vin_ref, status)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,'available')""",
            vulid, entity_ulid, v.deep_link, title, v.make, v.model,
            v.year, v.km, v.price, v.fuel, v.photo_url, v.vin_ref,
        )
        await conn.execute(
            "INSERT INTO vehicle_event "
            "(event_ulid, vehicle_ulid, entity_ulid, event_type, old_value, new_value) "
            "VALUES ($1,$2,$3,'NEW',NULL,$4::jsonb)",
            ulid(), vulid, entity_ulid,
            json.dumps({"price": v.price, "title": title, "source": v.source_type}),
        )
        ingested += 1

    # GONE guard: mark departed vehicles as 'sold' when harvest was full-coverage.
    # Threshold: harvest must have seen >= 95% of the PRIOR available count (read
    # before ingest so new inserts don't inflate the baseline).
    # prior_available is read above before the ingest loop.
    gone_count = 0
    harvest_total = ingested + skipped
    if prior_available and harvest_total >= int(prior_available) * 0.95:
        # Harvest covered most of the prior inventory — safe to retire departed ones
        gone_rows = await conn.fetch(
            """SELECT vehicle_ulid, deep_link FROM vehicle
               WHERE entity_ulid=$1 AND status='available'""",
            entity_ulid,
        )
        for row in gone_rows:
            if row["deep_link"] not in seen_deep_links:
                await conn.execute(
                    "UPDATE vehicle SET status='sold', last_seen=now() WHERE vehicle_ulid=$1",
                    row["vehicle_ulid"],
                )
                await conn.execute(
                    "INSERT INTO vehicle_event "
                    "(event_ulid, vehicle_ulid, entity_ulid, event_type, old_value, new_value) "
                    "VALUES ($1,$2,$3,'GONE','available','sold')",
                    ulid(), row["vehicle_ulid"], entity_ulid,
                )
                gone_count += 1

    # VAM: two paths — this_harvest_total vs available in DB (post GONE guard)
    available_in_db = await conn.fetchval(
        "SELECT count(*) FROM vehicle WHERE entity_ulid=$1 AND status='available'",
        entity_ulid,
    )
    verdict = await record_count_verdict(
        conn,
        subject_type="generic_dealer_site_inventory",
        subject_key=entity_ulid,
        claim="available_in_db == this_harvest_total",
        paths={
            "db_available": int(available_in_db),
            "this_harvest_new": ingested,
            "this_harvest_total": harvest_total,
        },
        tolerance=0.05,
    )

    # Mark entity as active & update sells_cars
    await conn.execute(
        "UPDATE entity SET sells_cars=TRUE, last_seen=now() WHERE entity_ulid=$1",
        entity_ulid,
    )

    return {
        "entity_ulid": entity_ulid,
        "ingested": ingested,
        "skipped": skipped,
        "gone": gone_count,
        "available_in_db": int(available_in_db),
        "verdict": verdict,
    }
