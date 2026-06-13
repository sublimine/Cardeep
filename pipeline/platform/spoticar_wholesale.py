"""spoticar (Stellantis ES certified-used) WHOLESALE harvester — a SECOND OEM-VO portal, end to end.

www.spoticar.es is the manufacturer certified-used portal for the Stellantis group in Spain
(Peugeot + Citroën + DS + Opel + Fiat + Jeep + Alfa Romeo + Abarth — the whole Stellantis VO
network). Like renew (Renault Group) it is NOT a car-specialist marketplace (coches.net/
autoscout24/motor.es) nor a generalist classifieds (wallapop): it is an OEM-VO PORTAL — a
single brand-owner publishing the certified-used inventory of its own dealer network. It is the
SECOND member of the 'oem_vo_portal' source_group, in the 'stellantis_vo' family, the sibling
of renew under the same ONE architecture.

The surface is a Drupal SPA backed by Elasticsearch. The SPA calls an internal JSON API at
GET /api/vehicleoffers/paginate/search?page=N: no browser, no proxy, no cookie warm-up, no auth —
just a Chrome TLS fingerprint (curl_cffi). Plain curl earns an AkamaiGHost 403; the chrome131
JA3 passes cleanly (defense_tier=t1_soft — a WAF is present but serving to curl_cffi). The
response carries {count:{value:6334}, hits:[{_source:{...}}]} — 12 cars/page, FLAT (no relevance
cap, no depth wall), walk page=1..~528 to enumerate the full ES public stock. Each hit._source
carries the car AND its selling Stellantis dealer via field_pdv_* fields (135 dealers in the
network) — dealer attribution is embedded per-car, NO PDP fetch needed. This is an OEM certified-
used portal: every car belongs to a Stellantis dealer (concesionario); there are NO private
sellers. Verified live 2026-06-12 (docs/architecture/tier1_recipes/spoticar_datalayer.md).

This module mirrors pipeline.platform.renew_wholesale EXACTLY (the OTHER OEM-VO portal: same
dual-membership model, same bulk cage, same governor/health/VAM wiring). It proves the OEM-VO
group flows through the ONE architecture, not a fork of it:

  spoticar (the OEM-VO portal) -> entity, kind='oem_vo_portal' (+ platform_meta)  [THE PLATFORM]
  each SELLING DEALER          -> entity, kind='compraventa'   (geo-resolved)
  each CAR                     -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the portal        -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the selling dealer); platform membership is plural (this edge). The same
physical car can carry BOTH a spoticar edge and a coches.net edge without ever changing its
owning dealer.

GEO anchor difference vs renew: renew dealers carry a postalCode (first 2 digits = INE province).
spoticar dealers carry NO postal code — instead field_pdv_geolocation = "lat,lng" + field_pdv_city.
The province therefore comes from the lat/lng via the ProvinceGeocoder (nearest labeled point);
the municipality is best-effort from the (fixed) city literal. dealerId = field_pdv_geo_id.

Encoding trap: the API serves brand/dealer/city text as latin-1 mojibake over the wire
(autom�tico = "automático", el�ctrico = "eléctrico", alcorc�n = "Alcorcón"). Re-encode every
human-text field: s.encode("latin-1").decode("utf-8"). The numeric field_* and carnum are clean.

Multi-axis classification (migrations/0016):
  defense_tier = 't1_soft'         (Akamai present but serving to curl_cffi; no JS challenge)
  source_group = 'oem_vo_portal'   (the group renew opened; spoticar is its second member)
  role         = 'platform'
  kind         = 'oem_vo_portal'   (the platform entity's ontology kind, migrations/0005)
  is_tier1     = TRUE              (the public site sits behind Akamai)
  family       = 'stellantis_vo'   (ties the Stellantis-group OEM-VO siblings on the family axis)

PROOF SLICE OR FULL. spoticar declares 6,334 cars (count.value). The set is small and FLAT, so
the FULL drain is in reach in a single run: --pages 528 walks the whole index. --pages/--limit
bound the run; --limit converts a target car count to a page count. The declared full count is
recorded for the VAM verdict's slice arithmetic.

Engine: a GET against www.spoticar.es/api/vehicleoffers/paginate/search routed THROUGH the
per-host governor (the same single choke point coches.net/renew/AS24 use). The synchronous
curl_cffi GET runs in a worker thread so the event loop is never blocked, and no host is fetched
faster than its bucket (www.spoticar.es inherits the conservative STEALTH class — t1_soft).

Run: python -m pipeline.platform.spoticar_wholesale --pages 528
"""
from __future__ import annotations

import argparse
import sys
import asyncio
import hashlib
import json
import math
import os
import re
from dataclasses import dataclass

import asyncpg
from curl_cffi import requests as cffi_requests

from pipeline.engine.governor import governor, host_of
from pipeline.geo import GeoResolver
from pipeline.geocode import ProvinceGeocoder
from pipeline.ids import ulid
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict
from services.api.codes import _base32, cdp_code

DSN = "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
DSN = os.environ.get("CARDEEP_DSN", DSN)

# ---------------------------------------------------------------------------
# spoticar platform identity (OEM-VO portal, migrations/0005 + 0016).
# ---------------------------------------------------------------------------
SPOTICAR_DOMAIN = "spoticar.es"
SPOTICAR_WEBSITE = "spoticar.es"
SPOTICAR_LEGAL_NAME = "Stellantis España (Spoticar)"
SPOTICAR_TRADE_NAME = "spoticar"
SPOTICAR_SOURCE_KEY = "spoticar_wholesale"
SPOTICAR_WAF = "akamai"             # AkamaiGHost 403s plain curl; serves to chrome131 -> is_tier1=TRUE.
SPOTICAR_DEFENSE_TIER = "t1_soft"   # WAF present but serving to curl_cffi (no JS challenge) -> tier 1 soft.
SPOTICAR_SOURCE_GROUP = "oem_vo_portal"
SPOTICAR_ROLE = "platform"
SPOTICAR_KIND = "oem_vo_portal"     # the platform ENTITY's ontology kind (NOT 'plataforma').
SPOTICAR_FAMILY = "stellantis_vo"   # ties the Stellantis-group OEM-VO siblings on the family axis.

# The working request (verified live 2026-06-12; recipe spoticar_datalayer.md TL;DR).
_BASE = "https://www.spoticar.es"
LIST_PATH = "/api/vehicleoffers/paginate/search"   # the internal ES-backed JSON paginate API.
ENDPOINT = _BASE + LIST_PATH
_HEADERS = {
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.spoticar.es/comprar-coches-de-ocasion",
}
_PDP_BASE = "https://www.spoticar.es"   # _source.url is a relative PDP path.
_IMPERSONATE = "chrome131"
_TIMEOUT = 40
PAGE_SIZE = 12  # the API serves a FIXED 12 cars/page (not overridable — recipe verified).

# Fuel/gearbox value repair. The accented Spanish labels (type_carburant, boite_vitesse) arrive
# with the accented byte already replaced by U+FFFD AT THE SOURCE (e.g. 'di�sel',
# 'autom�tico') — the latin-1 round-trip CANNOT recover them (verified live: the JSON itself
# carries the replacement char, not a recoverable mojibake byte). So instead of storing a lossy
# 'di�sel', map the CLEAN accent-free companion code (fuel_type: DIES/ESS/ELEC/HBD/HBDR) to
# its proper Spanish label, and normalize the finite two-value gearbox vocabulary deterministically.
# This is a fixed, verified vocabulary — no invention, just the clean source signal preferred.
_FUEL_CODE_LABEL = {
    "DIES": "Diésel", "ESS": "Gasolina", "ELEC": "Eléctrico",
    "HBD": "Híbrido", "HBDR": "Híbrido enchufable", "GPL": "GLP", "GNV": "GNC",
}
_GEARBOX_CLEAN = {"manual": "Manual", "automatico": "Automático", "automtico": "Automático"}


def _clean_fuel(fuel_code, fuel_label) -> str | None:
    """Prefer the clean accent-free fuel_type code (DIES/ESS/ELEC/...) mapped to its proper Spanish
    label; fall back to the (possibly U+FFFD-bearing) type_carburant label only if the code is
    unknown — never store a lossy replacement char when a clean signal exists."""
    code = _unwrap(fuel_code)
    if isinstance(code, str):
        mapped = _FUEL_CODE_LABEL.get(code.strip().upper())
        if mapped:
            return mapped
    label = _fix(_unwrap(fuel_label))
    return label


def _clean_gearbox(boite) -> str | None:
    """Normalize the finite gearbox vocabulary (manual / automático). The source may carry
    'autom�tico'; strip non-letters to key the clean map, else return the fixed string."""
    val = _unwrap(boite)
    if not isinstance(val, str):
        return None
    key = re.sub(r"[^a-z]", "", val.lower())
    return _GEARBOX_CLEAN.get(key, _fix(val))

# Province sentinel '00' = national (same convention as renew/coches.net/AS24). geo_province has
# NO '00', so the platform ENTITY stores province_code = NULL; '00' lives only inside the cdp_code
# string (free text, no FK). We never pollute geo_province with it.
PLATFORM_PROVINCE_SENTINEL = "00"

# Full-drain default. 6,334 cars / 12 per page = ~528 data pages (page 528 = 11 trailing hits;
# 529+ = 0). count.value + emptiness bound the run. A small slice (--pages 5) is a proof slice;
# --pages 528 is the full ES public stock.
DEFAULT_MAX_PAGES = 528
# Empty-page guard: the recipe warns pages 529-576 return 0 hits, >576 return phantom repeats.
# Stop on the first empty page (the true data boundary is 528); count.value is the hard bound.


def spoticar_platform_cdp_code() -> str:
    """The spoticar platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:spoticar.es'), province segment '00' (national). Mirrors
    renew_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{SPOTICAR_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Field helpers (the spoticar surface: single-element arrays + latin-1 mojibake).
# ---------------------------------------------------------------------------


def _unwrap(v):
    """Most _source fields arrive as single-element arrays — unwrap to the scalar."""
    return v[0] if isinstance(v, list) and v else v


def _fix(s):
    """Repair latin-1 mojibake on human-text fields (autom�tico -> automático, alcorc�n ->
    Alcorcón). The wire bytes were UTF-8 mis-decoded as latin-1 upstream; re-encode to recover.
    Numeric field_* and field_vo_carnum are clean and never passed here."""
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


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


def _parse_latlng(geoloc) -> tuple[float | None, float | None]:
    """field_pdv_geolocation is the string 'lat,lng' (e.g. '39.970016,-0.070215'). Split and
    parse; return (None, None) on any malformed/missing value so the geo gate skips it cleanly."""
    if not isinstance(geoloc, str) or "," not in geoloc:
        return (None, None)
    lat_s, _, lng_s = geoloc.partition(",")
    return (_to_float(lat_s.strip()), _to_float(lng_s.strip()))


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL response — field names inspected live 2026-06-12, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class DealerRef:
    """The selling Stellantis dealer parsed from a single car's field_pdv_* fields.

    spoticar attaches the full point-of-sale per car: field_pdv_geo_id (stable per-site id),
    field_pdv_title (name), field_pdv_city, and field_pdv_geolocation ('lat,lng'). Unlike renew
    (postalCode -> province) there is NO postal code; the province is geocoded from the lat/lng
    (nearest labeled point) and the municipality is best-effort from the city literal. geo_id is
    the stable per-dealer key for cross-source dedup and as the source_ref."""
    dealer_id: str
    name: str | None
    province_code: str | None
    city: str | None
    lat: float | None
    lng: float | None


@dataclass
class Vehicle:
    """A car parsed from a single spoticar search item."""
    deep_link: str
    listing_ref: str           # spoticar stable car id (field_vo_carnum) — also the dedup key.
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    vin: str | None            # REAL per-car VIN (field_vo_vin) — gold for cross-source dedup.


def _first_image(source: dict) -> str | None:
    """Pick a hosted image URL. spoticar carries images under several keys depending on the
    document; prefer the first absolute http(s) URL found in the common image fields."""
    for key in ("field_vo_image", "field_image", "images", "field_vo_photos", "image"):
        val = source.get(key)
        if isinstance(val, list):
            for item in val:
                u = _unwrap([item]) if not isinstance(item, (list, dict)) else None
                cand = item if isinstance(item, str) else (item.get("url") if isinstance(item, dict) else u)
                if isinstance(cand, str) and cand.startswith("http"):
                    return cand
        elif isinstance(val, str) and val.startswith("http"):
            return val
    return None


def parse_item_dealer(source: dict) -> DealerRef | None:
    """Parse the SELLING dealer from a car's field_pdv_* fields. Returns None when there is no
    stable dealer id (field_pdv_geo_id) — the car cannot be attributed to a concrete POS."""
    dealer_id = _unwrap(source.get("field_pdv_geo_id"))
    if not dealer_id:
        return None
    lat, lng = _parse_latlng(_unwrap(source.get("field_pdv_geolocation")))
    return DealerRef(
        dealer_id=str(dealer_id),
        name=_fix(_unwrap(source.get("field_pdv_title"))),
        province_code=None,                      # filled by the geocoder in _parse_window.
        city=_fix(_unwrap(source.get("field_pdv_city"))),
        lat=lat,
        lng=lng,
    )


def parse_item_vehicle(source: dict) -> Vehicle:
    """Parse the car from a spoticar search item (REAL field map, single-element arrays unwrapped)."""
    price = _to_float(_unwrap(source.get("field_vo_prix_base")))

    year = _to_int(_unwrap(source.get("field_vo_annee_modele")))
    if year is None:
        year = _to_int(_unwrap(source.get("field_vo_dpi")))
    if year is not None and not (1900 <= year <= 2100):
        year = None

    km = _to_int(_unwrap(source.get("field_vo_km")))
    if km is not None and (km < 0 or km > 5_000_000):
        km = None

    url = _unwrap(source.get("url")) or ""
    deep_link = (_PDP_BASE + url) if isinstance(url, str) and url.startswith("/") else (url or "")

    make = _fix(_unwrap(source.get("marque_no_accent")) or _unwrap(source.get("marque")))
    model = _fix(_unwrap(source.get("model")))
    version = _fix(_unwrap(source.get("version")))
    title = " ".join(p for p in (make, model, version) if p) or None

    # carnum is the stable per-car id AND the recipe's dedup key (ES_<pdv>_<refbase>). It is clean.
    carnum = _unwrap(source.get("field_vo_carnum"))
    listing_ref = str(carnum) if carnum else str(_unwrap(source.get("field_vo_refbase")) or "")

    # gearbox is boite_vitesse (Manual/Automático); the `transmission` field is the DRIVETRAIN
    # (delantera/trasera/total), NOT the gearbox — do not confuse the two. Both fuel and gearbox
    # are cleaned via the accent-free companion code/vocabulary (the accented label carries an
    # unrecoverable U+FFFD at the source).
    transmission = _clean_gearbox(source.get("boite_vitesse"))
    fuel = _clean_fuel(source.get("fuel_type"), source.get("type_carburant"))

    vin = _unwrap(source.get("field_vo_vin"))

    return Vehicle(
        deep_link=deep_link,
        listing_ref=listing_ref,
        title=title,
        make=make,
        model=model,
        year=year,
        km=km,
        price=price,
        fuel=fuel,
        transmission=transmission,
        photo_url=_first_image(source),
        vin=str(vin) if vin else None,
    )


# ---------------------------------------------------------------------------
# Fetch: a GET routed THROUGH the governor (same per-host choke point as renew/coches.net).
# ---------------------------------------------------------------------------


class SpoticarFetcher:
    """A POOL of fingerprint-coherent curl_cffi GET sessions for the spoticar paginate API.

    Same concurrency-vs-coherence model as RenewFetcher / CochesFetcher: a single curl_cffi
    Session is NOT safe to call from several threads at once, and the governor runs each fetch in
    its own worker thread (asyncio.to_thread). The fix is a bounded POOL — one Session per
    concurrency slot, each its own Chrome fingerprint + cookie jar. The governor's per-host bucket
    bounds the AGGREGATE rate across every session, so the pool widens parallelism WITHOUT
    out-pacing the host (the choke point is the bucket, never the session count).
    """

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch_page(self, url: str, *, page: int = 1, slot: int = 0) -> dict:
        """The synchronous GET on pool session `slot` (runs in a worker thread).

        Handed to governor().wrap_fetch_text: the governor derives the host from `url`, waits on
        the per-host bucket, then runs THIS off the event loop. `slot` rides as a kwarg the
        governor forwards untouched, so each in-flight request GETs on its own leased, never-shared
        curl_cffi session (thread-safe). NO sort/orderby param (the recipe root-caused that an
        added sort triggers origin 503 on deep pages). Raises on a non-200 so the breaker sees
        throttling (never masks a challenge/empty body)."""
        session = self._sessions[slot]
        resp = session.get(url, params={"page": page}, headers=_HEADERS,
                           impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url} (page {page})")
        # The API serves UTF-8 JSON; decode explicitly. (Some human-text VALUES inside are latin-1
        # mojibake — repaired per-field by _fix(); the JSON envelope itself is valid UTF-8.)
        return json.loads(resp.content.decode("utf-8", "replace"))

    async def fetch_page_async(self, governed_fetch, url: str, *, page: int) -> dict:
        """Lease a pool slot, fetch `page` THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, page=page, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer (mirrors renew_wholesale: ensure platform, bulk-upsert dealer/vehicle, link edge,
# emit delta, all idempotent ON CONFLICT). Multi-axis 0016 classification set.
# ---------------------------------------------------------------------------

SPOTICAR_PLATFORM_RECIPE = {
    "version": 1,
    "source": "spoticar (www.spoticar.es)",
    "scope": "platform-wholesale (Stellantis ES certified-used; Drupal SPA + Elasticsearch JSON API)",
    "engine": "curl_cffi+chrome131_impersonate+internal_es_json_api(GET)",
    "access": ("OPEN-via-fingerprint (AkamaiGHost 403 to plain curl; chrome131 TLS/JA3 passes "
               "cleanly). No proxy, no browser, no cookie warm-up, no auth, €0. Public site behind "
               "Akamai -> is_tier1=TRUE; the JSON API serves to curl_cffi -> defense_tier=t1_soft."),
    "data_surface": "internal_api",
    "surface_intent": "internal_es_json_api",
    "endpoint": "GET https://www.spoticar.es/api/vehicleoffers/paginate/search?page=N",
    "request": {
        "headers": "Accept */*, X-Requested-With XMLHttpRequest, Accept-Language es-ES, Referer /comprar-coches-de-ocasion",
        "params": "page=N only (NO sort/orderby — a sort param triggers AkamaiGHost 503 on deep pages)",
    },
    "enumeration": ("page=1..~528 (12 cars/page; page 528 = 11 trailing hits, 529+ = 0). "
                    "count.value (6334) + first-empty-page bound the run; dedup on field_vo_carnum. "
                    "lastPage=576 is a METADATA artefact, NOT the data boundary."),
    "denominator": "count.value (6334) == list/search countNumber == Σbrand-facets == Σdealer-facets == /api/count-published-vo",
    "platform_entity": ("kind=oem_vo_portal, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=TRUE, defense_tier=t1_soft, source_group=oem_vo_portal, role=platform, "
                        "family=stellantis_vo"),
    "dual_membership": ("vehicle.entity_ulid=SELLING DEALER (compraventa); "
                        "platform_listing edge=platform<->vehicle"),
    "field_map": {
        "deep_link": "_source.url (prefixed with https://www.spoticar.es)",
        "listing_ref": "_source.field_vo_carnum (ES_<pdv>_<refbase>; stable id + dedup key)",
        "vin": "_source.field_vo_vin (REAL per-car VIN — gold for cross-source dedup)",
        "make": "_source.marque_no_accent (fallback marque)",
        "model": "_source.model",
        "version": "_source.version",
        "year": "_source.field_vo_annee_modele (fallback field_vo_dpi)",
        "km": "_source.field_vo_km",
        "price": "_source.field_vo_prix_base (field_vo_pb_devise=eur)",
        "fuel": "_source.type_carburant (fallback fuel_type)",
        "transmission": "_source.boite_vitesse (gearbox; NOT _source.transmission which is drivetrain)",
        "dealer": "_source.field_pdv_* {field_pdv_geo_id, field_pdv_title, field_pdv_city, field_pdv_geolocation}",
        "location": ("field_pdv_geolocation='lat,lng' -> province via ProvinceGeocoder (nearest "
                     "labeled point); field_pdv_city -> municipality (INE-resolved, best-effort)"),
    },
    "caveats": {
        "page_size": "fixed 12 cars/page (not a request param).",
        "encoding": ("brand/dealer/city text is latin-1 mojibake over the wire (autom�tico, "
                     "alcorc�n); repair with s.encode('latin-1').decode('utf-8'). Numeric fields clean."),
        "no_sort": "adding sort/orderby triggers AkamaiGHost 503 on deep pages — harvest plain ?page=N only.",
        "geo": "no postal code on this surface; province is geocoded from field_pdv_geolocation lat/lng.",
        "no_private_sellers": "OEM certified-used portal — every car belongs to a Stellantis dealer.",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the spoticar platform entity + platform_meta exist. Returns the
    platform entity_ulid. kind='oem_vo_portal' (the platform ontology kind), is_tier1=TRUE (Akamai
    fronts the public site), multi-axis 0016 classification set explicitly, data_surface='internal_api'."""
    code = spoticar_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               defense_tier, source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,$3,$4,$5,NULL,$6,$7::waf_kind,TRUE,'active','platform_label',
               $8::defense_tier,$9::source_group,$10::entity_role,$11, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, website_waf = EXCLUDED.website_waf,
               defense_tier = EXCLUDED.defense_tier, source_group = EXCLUDED.source_group,
               role = EXCLUDED.role, legal_name = EXCLUDED.legal_name, kind = EXCLUDED.kind""",
        eulid, code, SPOTICAR_KIND, SPOTICAR_LEGAL_NAME, SPOTICAR_TRADE_NAME, SPOTICAR_WEBSITE,
        SPOTICAR_WAF, SPOTICAR_DEFENSE_TIER, SPOTICAR_SOURCE_GROUP, SPOTICAR_ROLE, SPOTICAR_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, SPOTICAR_SOURCE_KEY, SPOTICAR_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'internal_api',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"endpoint": ENDPOINT, "host": host_of(ENDPOINT),
                           "method": "GET", "page_size": PAGE_SIZE,
                           "denominator": "count.value",
                           "surface_intent": "internal_es_json_api",
                           "engine": "curl_cffi/chrome131_impersonate"}),
        SPOTICAR_FAMILY)
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    spoticar dealers have no bare domain on this surface -> identity = name + location + the stable
    field_pdv_geo_id (passed via `address` so two distinct POS that happen to share a name in one
    municipality never collapse to one entity)."""
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni, address=f"dealer:{d.dealer_id}")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# Default concurrency: pages fetched in parallel per sliding window. www.spoticar.es is NOT in the
# governor's JSON_API rate class — it inherits the conservative STEALTH default (0.7 req/s, the
# AS24-scar pace), the safe direction for a t1_soft WAF host whose true ceiling is unmeasured. The
# concurrency only needs to keep that (slow) bucket saturated; a small window is plenty.
DEFAULT_CONCURRENCY = 4


@dataclass
class _CageRow:
    """One fully-parsed, geo-anchored car ready for the bulk cage — the in-memory result of the
    parse+resolve phase, before any SQL. Carries everything the batched upserts need so the DB
    phase touches no per-item Python logic, only set-based statements."""
    dealer_id: str
    dealer_cdp: str
    dealer_name: str | None
    dealer_province: str
    dealer_muni: str | None
    vehicle: Vehicle


# The bulk statements — ONE round-trip per table per window (unnest-based multi-row upsert),
# byte-for-byte the same idempotency the row-by-row path uses. A re-run of an already-harvested
# window adds 0 rows and 0 events. Dealers carry the 0016 axes (oem_vo_portal/standalone_pos).

_BULK_UPSERT_DEALERS = """
INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
        province_code, municipality_code, is_tier1, status, kind_source,
        sells_cars, source_group, role, first_discovered_source, last_seen)
SELECT u.entity_ulid, u.cdp_code, 'compraventa', u.name, u.name,
       u.province_code, u.municipality_code, FALSE, 'active', 'platform_label',
       TRUE, 'oem_vo_portal'::source_group, 'standalone_pos'::entity_role, $7, now()
  FROM unnest($1::text[], $2::text[], $3::text[], $4::char(2)[], $5::char(5)[],
              $6::text[]) AS u(entity_ulid, cdp_code, name, province_code,
                               municipality_code, source_ref)
ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()
"""

_BULK_UPSERT_DEALER_SOURCES = """
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


def _parse_window(items_by_page: list[tuple[int, list]], geo: GeoResolver,
                  geocoder: ProvinceGeocoder, seen_ids: set, harvested_cageable: set,
                  stats: dict) -> list[_CageRow]:
    """Parse + geo-resolve every car across the window IN PAGE ORDER — pure CPU, no SQL.

    The EXACT per-item gate (cross-page dedup on field_vo_carnum, dealer-parse skip, geo skip,
    cageable truth), lifted out of the DB loop so the SQL phase is purely set-based. The province
    is GEOCODED from the dealer's lat/lng (nearest labeled point) — spoticar has no postal code on
    this surface. `seen_ids` / `harvested_cageable` / `stats` are mutated here with deterministic
    page-order semantics so the VAM truth is byte-identical regardless of batching."""
    rows: list[_CageRow] = []
    for _page, items in items_by_page:
        for item in items:
            source = item.get("_source") or {}
            stats["items_seen"] += 1
            # cross-page dedup on field_vo_carnum (the recipe's stable dedup key; default sort is
            # not stable across a long crawl, so the same car can reappear on a later page).
            carnum = _unwrap(source.get("field_vo_carnum"))
            item_id = str(carnum) if carnum else str(_unwrap(source.get("field_vo_refbase")) or "")
            if item_id and item_id in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue
            if item_id:
                seen_ids.add(item_id)

            d = parse_item_dealer(source)
            if d is None:
                stats["no_dealer_skipped"] += 1
                continue
            stats["dealer_items"] += 1

            # Geo gate — geocode the province from the dealer's lat/lng, then apply the same
            # province-range guard the dealer upsert enforces, done in memory so a bad/missing geo
            # is skipped without ever touching the DB (no FK risk).
            prov = geocoder.nearest_province(d.lat, d.lng) if d.lat is not None else None
            if not prov:
                stats["geo_skipped"] += 1
                continue
            if not (prov.isdigit() and "01" <= prov <= "52"):
                stats["geo_skipped"] += 1
                continue
            d = DealerRef(dealer_id=d.dealer_id, name=d.name, province_code=prov,
                          city=d.city, lat=d.lat, lng=d.lng)
            muni = geo.municipality_code(prov, d.city)
            dealer_cdp = cdp_code_dealer(d, muni)

            v = parse_item_vehicle(source)
            if not v.deep_link:
                continue
            harvested_cageable.add((d.dealer_id, v.deep_link))
            if v.vin:
                stats["vins_captured"] += 1
            rows.append(_CageRow(
                dealer_id=d.dealer_id, dealer_cdp=dealer_cdp, dealer_name=d.name,
                dealer_province=prov, dealer_muni=muni, vehicle=v))
    return rows


async def _ingest_window(conn: asyncpg.Connection, geo: GeoResolver, geocoder: ProvinceGeocoder,
                         platform_ulid: str, items_by_page: list[tuple[int, list]], seen_ids: set,
                         harvested_cageable: set, stats: dict) -> None:
    """BULK-ingest a whole concurrent page-window in ONE transaction with set-based SQL.

    Mirrors renew_wholesale._ingest_window EXACTLY: ONE round-trip per table per window (unnest
    multi-row upserts). The delta/VAM/platform_listing semantics are preserved: same ON CONFLICT
    idempotency, same cageable truth, same NEW-event rule (emitted only for genuinely new
    vehicles). A re-run of an already-harvested window adds 0 rows and 0 events.
    """
    cage = _parse_window(items_by_page, geo, geocoder, seen_ids, harvested_cageable, stats)
    if not cage:
        return

    async with conn.transaction():
        # ---- (2) DEALERS: dedup by cdp_code within the window, bulk-upsert, resolve ulids.
        dealers: dict[str, _CageRow] = {}
        for r in cage:
            dealers.setdefault(r.dealer_cdp, r)  # first occurrence wins (deterministic)
        d_ulids = [ulid() for _ in dealers]
        d_cdps = list(dealers.keys())
        d_names = [dealers[c].dealer_name for c in d_cdps]
        d_provs = [dealers[c].dealer_province for c in d_cdps]
        d_munis = [dealers[c].dealer_muni for c in d_cdps]
        d_refs = [dealers[c].dealer_id for c in d_cdps]
        await conn.execute(_BULK_UPSERT_DEALERS, d_ulids, d_cdps, d_names, d_provs,
                           d_munis, d_refs, SPOTICAR_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_DEALER_SOURCES, d_cdps, d_refs, SPOTICAR_SOURCE_KEY)
        cdp_to_ulid: dict[str, str] = {
            row["cdp_code"]: row["entity_ulid"]
            for row in await conn.fetch(
                "SELECT cdp_code, entity_ulid FROM entity "
                "WHERE cdp_code = ANY($1::text[])", d_cdps)
        }

        # ---- attach resolved dealer_ulid to each cage row; dedup cars within the window by
        # (dealer_ulid, deep_link) so the same ad seen twice in one window is one car.
        cars: dict[tuple[str, str], _CageRow] = {}
        for r in cage:
            du = cdp_to_ulid.get(r.dealer_cdp)
            if du is None:
                continue
            key = (du, r.vehicle.deep_link)
            if key not in cars:
                cars[key] = r

        # ---- (3) VEHICLES: one SELECT splits existing vs new. Existing -> bulk touch.
        # New -> Python-minted ulid + bulk insert.
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
                [x[3].photo_url for x in ins], [x[3].vin for x in ins])
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

        # ---- (5) NEW delta events — only for genuinely new vehicles. VIN preserved in payload.
        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                v = cars[k].vehicle
                payload = {"price": v.price, "title": v.title, "platform": SPOTICAR_TRADE_NAME}
                if v.vin:
                    payload["vin"] = v.vin
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities,
                               ev_payloads)
            stats["new_events"] += len(confirmed_new)


async def harvest(max_pages: int = DEFAULT_MAX_PAGES,
                  concurrency: int = DEFAULT_CONCURRENCY,
                  limit: int | None = None) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    # --limit converts a target car count to a page count (12 cars/page). The tighter of
    # --pages / --limit bounds the run.
    if limit is not None and limit > 0:
        limit_pages = max(1, math.ceil(limit / PAGE_SIZE))
        max_pages = min(max_pages, limit_pages)
    fetcher = SpoticarFetcher(pool_size=concurrency)
    stats = {
        "pages_fetched": 0, "items_seen": 0, "dealer_items": 0,
        "no_dealer_skipped": 0, "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "vins_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "dealers_distinct": 0,
        "concurrency": concurrency, "max_pages": max_pages, "private_skipped": 0,
    }
    # Harvest-side truth for the VAM: distinct CAGEABLE cars = distinct (dealer_id, deep_link)
    # pairs that survived dealer-parse + geo-resolution. Like-with-like vs db_edges.
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if spoticar's breaker is OPEN (a recent ban/throttle still cooling), skip the
    # drain gracefully — the API keeps serving the last snapshot.
    if await is_open(conn, SPOTICAR_SOURCE_KEY):
        print(f"[spoticar_wholesale] breaker OPEN for {SPOTICAR_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, API still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": SPOTICAR_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_page)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        geocoder = await ProvinceGeocoder.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = spoticar_platform_cdp_code()
        print(f"[spoticar_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid}) "
              f"kind={SPOTICAR_KIND} group={SPOTICAR_SOURCE_GROUP} tier={SPOTICAR_DEFENSE_TIER} "
              f"family={SPOTICAR_FAMILY}")
        print(f"[spoticar_wholesale] geocoder anchors: {geocoder.size()} labeled points (lat/lng -> province).")
        print(f"[spoticar_wholesale] governor paces host {host_of(ENDPOINT)} (per-host token bucket, STEALTH class).")
        print(f"[spoticar_wholesale] CONCURRENT drain: window={concurrency} pages in flight. "
              f"Target = {max_pages} pages (~{max_pages * PAGE_SIZE} cars; full ES stock = 6334).")

        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        # CONCURRENT sliding-window drain. Each window fetches up to `concurrency` pages in parallel
        # through the governor (the host bucket paces the aggregate), then the pages are INGESTED
        # sequentially in page order through the single asyncpg connection. A page that errors or
        # comes back empty stops the drain honestly (end of data — page 528 is the true boundary —
        # or a throttle the breaker must catch). count.value also bounds the run.
        stop = False
        next_page = 1
        while next_page <= max_pages and not stop:
            window = list(range(next_page, min(next_page + concurrency, max_pages + 1)))
            next_page = window[-1] + 1

            results = await asyncio.gather(
                *(fetcher.fetch_page_async(governed_fetch, ENDPOINT, page=p) for p in window),
                return_exceptions=True,
            )

            window_pages: list[tuple[int, list]] = []
            for page, data in zip(window, results):
                if isinstance(data, Exception):
                    fetch_error = str(data)
                    last_http = fetcher.last_status
                    print(f"[spoticar_wholesale] page {page} fetch failed ({data}); stopping drain honestly.")
                    stop = True
                    break
                if stats["declared_full"] is None:
                    cnt = data.get("count") or {}
                    stats["declared_full"] = _to_int(cnt.get("value"))
                items = data.get("hits") or []
                if not items:
                    print(f"[spoticar_wholesale] page {page}: no hits; stopping (data boundary reached).")
                    stop = True
                    break
                window_pages.append((page, items))

            if window_pages:
                await _ingest_window(conn, geo, geocoder, platform_ulid, window_pages, seen_ids,
                                     harvested_cageable, stats)
                stats["pages_fetched"] += len(window_pages)
                first_p, last_p = window_pages[0][0], window_pages[-1][0]
                print(f"[spoticar_wholesale] window pages {first_p}-{last_p}: "
                      f"hits={sum(len(it) for _, it in window_pages)} "
                      f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                      f"edges={stats['edges_created']} dealers_seen={len(harvested_cageable)}")

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, SPOTICAR_PLATFORM_RECIPE)
        print(f"[spoticar_wholesale] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths that all measure
        # "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for spoticar   (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join   (DB read truth)
        #   harvested_cageable = distinct (dealer_id, deep_link) pulled (harvest truth)
        # The declared full count (6334) is reported for honesty but is NOT a quorum path (it
        # measures the WHOLE portal, not necessarily this slice unless the full drain ran).
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

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks spoticar, trips the
        # breaker on a ban, and auto-repairs. OK when >=1 page fetched, no fetch error stopped the
        # drain, and the VAM did not refute.
        run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, SPOTICAR_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, SPOTICAR_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[spoticar_wholesale] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("SPOTICAR (OEM-VO PORTAL) WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  group / kind          : oem_vo_portal / oem_vo_portal (tier t1_soft, family stellantis_vo)")
    print(f"  declared full (source): {stats.get('declared_full')}")
    print(f"  concurrency (window)  : {stats.get('concurrency')} pages in flight")
    print(f"  target pages          : {stats.get('max_pages')}")
    print(f"  pages fetched         : {stats['pages_fetched']}")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  dealer items          : {stats['dealer_items']}")
    print(f"  no-dealer skipped     : {stats['no_dealer_skipped']}")
    print(f"  private skipped       : {stats['private_skipped']} (OEM portal — none expected)")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (cross-page, carnum dedup)")
    print(f"  geo skipped (bad geo) : {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for spoticar = {stats.get('db_edges')})")
    print(f"  VINs captured         : {stats['vins_captured']}")
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
        description="spoticar OEM-VO portal wholesale harvester (concurrent internal-ES-JSON drain)")
    parser.add_argument("--pages", type=int, default=DEFAULT_MAX_PAGES,
                        help=f"pages to harvest (size={PAGE_SIZE}); default {DEFAULT_MAX_PAGES} (full ES stock)")
    parser.add_argument("--limit", type=int, default=None,
                        help=("optional target car count; converted to a page count (12/page). "
                              "The tighter of --pages / --limit bounds the run."))
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"pages fetched in parallel per sliding window; default "
                              f"{DEFAULT_CONCURRENCY}. www.spoticar.es inherits the conservative "
                              f"STEALTH rate class — the governor's per-host bucket is the real limiter."))
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.pages, args.concurrency, args.limit))
    _print_report(stats)


if __name__ == "__main__":
    main()
