"""hyundai (Hyundai Promise / Hyundai Ocasión ES certified-used) WHOLESALE harvester — end to end.

www.hyundai.es/seminuevos ('Hyundai Ocasión' / 'Hyundai Promise' — the brand's certified-used
programme) is the manufacturer-owned certified-used portal for Hyundai Motor España. Like
toyota_lexus (Toyota Group), spoticar (Stellantis) and renew (Renault Group) it is NOT a
car-specialist marketplace (coches.net/autoscout24/motor.es) nor a generalist classifieds
(wallapop): it is an OEM-VO PORTAL — a brand owner publishing the certified-used inventory of its
own official dealer network (concesionarios oficiales). It is the FOURTH member of the
'oem_vo_portal' source_group, in the new 'hyundai_vo' family, the sibling of toyota_lexus/spoticar/
renew under the same ONE architecture.

The seminuevos site is a custom OpenCart storefront. The vehicle list is NOT scraped from the
server-rendered HTML cards: the SPA calls an internal JSON endpoint —
GET /seminuevos/index.php?route=product/vehiculo/listado — that returns the WHOLE national stock
FLAT in a single response: {vehiculos:[{...}, ...]} (2,036 cars live 2026-06-13), no pagination,
no offset cursor, no relevance cap, no depth wall. No browser, no proxy, no cookie warm-up, no
auth: the host serves HTTP 200 application/json to curl_cffi chrome131 (defense_tier=t1_soft — a
WAF fronts the public host and 403s a stripped fetch, but the chrome131 TLS fingerprint passes
cleanly). Each `vehiculos[]` item carries the car (incl. REAL VIN = `bastidor`) AND the selling
dealer's NAME (`concesionario`) + phone (`telefono`) — but NO dealer location.

DEALER GEO comes from a SECOND internal JSON surface, fetched ONCE per run:
GET /concesionarios/index.php?route=api/installation/seminuevos -> {instalaciones:[{...}]} (155
official installations) carrying name + phone + zipcode + zone (province name) + city + lat/lon +
concesionario_id. Each car is joined to its installation by PHONE (primary, exact) then by a
normalized NAME match (fallback) — the listado name carries S.L./MOTOR/AUTOMOCION noise the
directory name omits. The province is then resolved from the installation's zipcode (first 2
digits = INE province, authoritative — the renew/toyota model), with lat/lon as the geocode
fallback. dealer_id = installation.concesionario_id. This is an OEM certified-used portal: every
car belongs to a Hyundai official dealer; there are NO private sellers. Verified live 2026-06-13
(docs/architecture/tier1_recipes/oem_hyundai_datalayer.md).

This module mirrors pipeline.platform.oem_toyota_lexus_wholesale EXACTLY (the proven OEM-VO
template: same dual-membership model, same bulk cage, same governor/health/VAM wiring). It proves
the OEM-VO group flows through the ONE architecture, not a fork of it:

  hyundai (the OEM-VO portal) -> entity, kind='oem_vo_portal' (+ platform_meta)  [THE PLATFORM]
  each SELLING DEALER         -> entity, kind='compraventa'   (geo-resolved)
  each CAR                    -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the portal       -> platform_listing edge (platform_entity <-> vehicle)

Ownership is singular (the selling dealer); platform membership is plural (this edge). The same
physical car can carry BOTH a hyundai edge and a coches.net edge without ever changing its owning
dealer.

GEO anchor difference vs toyota_lexus: Toyota embedded the dealer (incl. zip+geo) per car. Hyundai
splits it: the listado has NO dealer location, only name+phone. So we fetch the installations
directory ONCE, build a phone/name -> {zip, zone, city, lat, lon, concesionario_id} index, and
attribute each car through it. Province = installation.zipcode[:2] (authoritative); lat/lon is the
geocode fallback when the zip is missing/malformed.

Encoding trap: the listado AND installations serve human-text as latin-1 mojibake over the wire
(Corriente el�ctrica = "Corriente eléctrica", autom�tico = "automático", L�Aldea = "L'Aldea").
Re-encode every human-text field: s.encode("latin-1").decode("utf-8"). The numeric fields, the
vehiculo_id token and bastidor (VIN) are clean.

Lat/lon trap: the installations record carries BOTH a correct `lat`/`lon` pair AND a SWAPPED
`latitud`/`longitud` pair (the site's own JS compensates with `lat: parseFloat(inst['longitud'])`).
We read the CORRECT `lat`/`lon` keys (Spain: lat 36..44, lon -9..4) and ignore latitud/longitud.

Multi-axis classification (migrations/0016):
  defense_tier = 't1_soft'         (a WAF fronts the public host — 403s a stripped fetch — but
                                    serves to curl_cffi chrome131; no JS challenge)
  source_group = 'oem_vo_portal'   (the group renew opened; hyundai is its fourth member)
  role         = 'platform'
  kind         = 'oem_vo_portal'   (the platform entity's ontology kind, migrations/0005)
  is_tier1     = TRUE              (the public site sits behind a WAF)
  family       = 'hyundai_vo'      (ties the Hyundai-group OEM-VO siblings on the family axis)

PROOF SLICE OR FULL. The portal declares its full stock as the length of the listado `vehiculos`
list (2,036 cars live). The set is small and FLAT (one response), so the FULL drain is the default
in a single run. --limit bounds the run to a target car count (a proof slice); with no --limit the
whole national stock is caged. The declared full count is recorded for the VAM verdict.

Engine: a GET against www.hyundai.es/seminuevos/...route=product/vehiculo/listado (and one GET to
the concesionarios installations API) routed THROUGH the per-host governor (the same single choke
point coches.net/toyota_lexus/AS24 use). The synchronous curl_cffi GET runs in a worker thread so
the event loop is never blocked, and no host is fetched faster than its bucket.

Run: python -m pipeline.platform.oem_hyundai_wholesale
"""
from __future__ import annotations

import argparse
import sys
import asyncio
import hashlib
import json
import os
import re
import unicodedata
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
# hyundai platform identity (OEM-VO portal, migrations/0005 + 0016).
# ---------------------------------------------------------------------------
HY_DOMAIN = "hyundai.es"
HY_WEBSITE = "hyundai.es"
HY_LEGAL_NAME = "Hyundai Motor España (Hyundai Promise / Ocasión)"
HY_TRADE_NAME = "hyundai"
HY_SOURCE_KEY = "oem_hyundai_wholesale"
HY_WAF = "other"              # a WAF 403s a stripped fetch; serves to chrome131 -> is_tier1=TRUE.
HY_DEFENSE_TIER = "t1_soft"   # WAF present but serving to curl_cffi (no JS challenge) -> tier 1 soft.
HY_SOURCE_GROUP = "oem_vo_portal"
HY_ROLE = "platform"
HY_KIND = "oem_vo_portal"     # the platform ENTITY's ontology kind (NOT 'plataforma').
HY_FAMILY = "hyundai_vo"      # ties the Hyundai-group OEM-VO siblings on the family axis.

# The two working requests (verified live 2026-06-13; recipe oem_hyundai_datalayer.md TL;DR).
_BASE = "https://www.hyundai.es"
LISTADO_PATH = "/seminuevos/index.php?route=product/vehiculo/listado"   # the internal car-list JSON.
INSTALL_PATH = "/concesionarios/index.php?route=api/installation/seminuevos"  # the dealer-geo JSON.
ENDPOINT = _BASE + LISTADO_PATH
INSTALL_ENDPOINT = _BASE + INSTALL_PATH
# The detail-page token (vehiculo_id) ROTATES on every listado fetch (verified live: 0/2036 stable
# across two consecutive fetches) — it is an EPHEMERAL per-response session token, NOT a stable car
# id, so it must NEVER be the dedup key (it would re-cage the whole stock as 'new' every run). The
# STABLE per-car identity is the VIN (bastidor): 100% present, permanent. We anchor both the
# listing_ref and the deep_link on the VIN so re-runs are idempotent. The live rotating token is
# attached to the deep_link only as a resolvable query tail (#vid=) — informational, not identity.
_DETAIL_BASE = _BASE + "/seminuevos/index.php?route=product/vehiculo/detalle&vehiculo_id="
# The canonical, STABLE deep_link is VIN-anchored (a synthetic but resolvable identity URL): the
# detail page is reachable only via the rotating token, so the stable key is the VIN, not the URL.
_VIN_DEEP_LINK_BASE = _BASE + "/seminuevos/#vin="
_IMPERSONATE = "chrome131"
_TIMEOUT = 60
_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.hyundai.es/seminuevos/",
}

# Province sentinel '00' = national (same convention as toyota_lexus/spoticar/renew/coches.net).
# geo_province has NO '00', so the platform ENTITY stores province_code = NULL; '00' lives only
# inside the cdp_code string (free text, no FK). We never pollute geo_province with it.
PLATFORM_PROVINCE_SENTINEL = "00"


def hy_platform_cdp_code() -> str:
    """The hyundai platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:hyundai.es'), province segment '00' (national). Mirrors
    tl_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{HY_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Field helpers (the hyundai surface: flat JSON + latin-1 mojibake on human text).
# ---------------------------------------------------------------------------


def _fix(s):
    """Repair latin-1 mojibake on human-text fields (Corriente el�ctrica -> Corriente eléctrica,
    autom�tico -> automático, L�Aldea -> L'Aldea). The wire bytes were UTF-8 mis-decoded as
    latin-1 upstream; re-encode to recover. Numeric fields, the vehiculo_id token and bastidor
    (VIN) are clean and never passed here."""
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


def _parse_price(s) -> float | None:
    """Parse the Spanish-formatted price ('19.900' -> 19900.0; '25.500' -> 25500.0). The thousands
    dot is a GROUP separator (no decimals on this surface). Prefer the dedicated numeric
    importe_financiar when present; this handles the human importe string."""
    if isinstance(s, (int, float)):
        return float(s) if s > 0 else None
    if not isinstance(s, str):
        return None
    digits = re.sub(r"[^\d]", "", s)
    if not digits:
        return None
    val = float(digits)
    return val if val > 0 else None


def _parse_km(s) -> int | None:
    """Parse the kilometraje string ('15.000km' -> 15000; '0km' -> 0; '20km' -> 20). Strip the
    'km' suffix and the thousands dot, keep digits."""
    if s is None:
        return None
    digits = re.sub(r"[^\d]", "", str(s))
    if digits == "":
        return None
    km = int(digits)
    return km if 0 <= km <= 5_000_000 else None


def _parse_year(matriculacion) -> int | None:
    """Extract the registration YEAR from matriculacion ('30-12-2024' -> 2024). The format is
    DD-MM-YYYY; the trailing 4-digit group is the year."""
    if not isinstance(matriculacion, str):
        return None
    m = re.search(r"(\d{4})", matriculacion)
    if not m:
        return None
    year = int(m.group(1))
    return year if 1900 <= year <= 2100 else None


def _vehiculo_id(href) -> str:
    """Extract the stable 64-char vehiculo_id token from the href (the dedup key + deep_link tail).
    The href is '...&vehiculo_id=<token>&'; the token is opaque, clean, globally unique."""
    if not isinstance(href, str):
        return ""
    h = href.replace("&amp;", "&")
    m = re.search(r"vehiculo_id=([^&]+)", h)
    return m.group(1) if m else ""


_NAME_NOISE = re.compile(
    r"\b(S\s*L\s*U?|S\s*A\s*U?|S\s*C\s*P?|MOTOR|MOTORS|AUTOMOCION|AUTOMOCI[OÓ]N|"
    r"AUTOMOVILES|AUTOM[OÓ]VILES|CARS|CAR|CONCESIONARIO|OFICIAL|HYUNDAI|SERVICIOS|"
    r"REPARACIONES|AVANCE)\b")


def _norm_name(s) -> str:
    """Normalize a dealer name for the fallback join: ASCII-fold, upper, strip legal-form +
    generic-automotive noise tokens, collapse whitespace. 'GASMOVIL S.L.' and 'GASMOVIL' collapse;
    'MARCOS AUTOMOCION VALENCIA' -> 'MARCOS VALENCIA'."""
    s = _fix(s or "")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.upper()
    s = re.sub(r"[.,/]", " ", s)
    s = _NAME_NOISE.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _norm_phone(p) -> str:
    """Reduce a phone to its digit string for the exact join key. Empty -> ''."""
    return re.sub(r"\D", "", str(p or ""))


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL responses — field names inspected live 2026-06-13, not assumed).
# ---------------------------------------------------------------------------


@dataclass
class Installation:
    """One official Hyundai dealer installation from the concesionarios installations API.

    Carries the geo the listado lacks: zipcode (first 2 digits = INE province, authoritative),
    zone (province name literal), city, lat/lon (CORRECT keys — latitud/longitud are swapped),
    and concesionario_id (the stable per-dealer key). name + phone are the join keys back to a
    listado car."""
    dealer_id: str
    name: str | None
    phone_digits: str
    zip: str | None
    zone: str | None
    city: str | None
    lat: float | None
    lon: float | None


@dataclass
class DealerRef:
    """The selling official dealer attributed to a car after joining the listado name/phone to an
    Installation. dealer_id = the installation's concesionario_id (stable); the geo (province/
    city/lat/lon) is the installation's. When a car cannot be joined to any installation it has no
    concrete location and is geo-skipped (no FK risk), exactly like a missing-geo Toyota car."""
    dealer_id: str
    name: str | None
    province_code: str | None
    city: str | None
    zip: str | None
    lat: float | None
    lon: float | None


@dataclass
class Vehicle:
    """A car parsed from a single listado `vehiculos[]` item."""
    deep_link: str
    listing_ref: str           # the hyundai stable vehiculo_id token — also the dedup key.
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    vin: str | None            # REAL per-car VIN (bastidor) — gold for cross-source dedup.


def parse_installation(inst: dict) -> Installation | None:
    """Parse one dealer installation. Returns None without a stable concesionario_id. Reads the
    CORRECT lat/lon keys (not the swapped latitud/longitud)."""
    dealer_id = inst.get("concesionario_id") or inst.get("instalacion_id")
    if not dealer_id:
        return None
    return Installation(
        dealer_id=str(dealer_id),
        name=_fix(inst.get("name")),
        phone_digits=_norm_phone(inst.get("phone")),
        zip=str(inst.get("zipcode")).strip() if inst.get("zipcode") not in (None, "") else None,
        zone=_fix(inst.get("zone")),
        city=_fix(inst.get("city")),
        lat=_to_float(inst.get("lat")),   # CORRECT key (Spain lat ~36..44).
        lon=_to_float(inst.get("lon")),   # CORRECT key (Spain lon ~ -9..4).
    )


class DealerDirectory:
    """The installations directory indexed for car->dealer attribution.

    PRIMARY join: exact phone-digits match (the listado car's `telefono` == an installation's
    `phone`). FALLBACK join: normalized-name match, then a token-subset match (the listado name is
    noisier than the directory name). Built ONCE per run from the installations API."""

    def __init__(self, installations: list[Installation]) -> None:
        self._by_phone: dict[str, Installation] = {}
        self._by_name: dict[str, Installation] = {}
        self._name_tokens: list[tuple[frozenset, Installation]] = []
        for ins in installations:
            if ins.phone_digits and ins.phone_digits not in self._by_phone:
                self._by_phone[ins.phone_digits] = ins
            key = _norm_name(ins.name)
            if key:
                self._by_name.setdefault(key, ins)
                self._name_tokens.append((frozenset(key.split()), ins))

    def __len__(self) -> int:
        return len({id(v) for v in
                    list(self._by_phone.values()) + list(self._by_name.values())})

    def match(self, name, phone) -> Installation | None:
        ph = _norm_phone(phone)
        if ph and ph in self._by_phone:
            return self._by_phone[ph]
        key = _norm_name(name)
        if not key:
            return None
        exact = self._by_name.get(key)
        if exact is not None:
            return exact
        ctoks = frozenset(key.split())
        if not ctoks:
            return None
        for dtoks, ins in self._name_tokens:
            if ctoks <= dtoks or dtoks <= ctoks:
                return ins
        return None


def parse_item_vehicle(item: dict) -> Vehicle:
    """Parse the car from a listado `vehiculos[]` item (REAL field map, flat dict)."""
    price = _parse_price(item.get("importe_financiar") or item.get("importe"))
    year = _parse_year(item.get("matriculacion"))
    km = _parse_km(item.get("kilometraje"))

    make = "Hyundai"   # the portal is brand-pure (busqueda.marcas == ['91'] == Hyundai).
    model = _fix(item.get("modelo"))
    if isinstance(model, str) and model.strip().upper() == "OTROS":
        model = None   # 'OTROS' is the portal's catch-all bucket, not a real model name.
    version = _fix(item.get("version"))
    title = " ".join(p for p in (make, model, version) if p) or None

    vin_raw = item.get("bastidor")
    vin = str(vin_raw).strip() if vin_raw else None

    # STABLE identity = the VIN (the vehiculo_id token rotates every fetch — see _VIN_DEEP_LINK_BASE).
    # listing_ref + deep_link are VIN-anchored so a re-run touches the SAME vehicle row (idempotent).
    # The live rotating token rides as a resolvable tail on the deep_link (informational only). When
    # a VIN is somehow absent (never observed live — 100% present), fall back to the token so the car
    # is still cageable, accepting that that one car is non-idempotent across runs.
    vehiculo_id = _vehiculo_id(item.get("href"))
    if vin:
        deep_link = f"{_VIN_DEEP_LINK_BASE}{vin}"
        listing_ref = vin
    elif vehiculo_id:
        deep_link = _DETAIL_BASE + vehiculo_id
        listing_ref = vehiculo_id
    else:
        deep_link = ""
        listing_ref = ""

    fuel = _fix(item.get("combustible"))
    transmission = _fix(item.get("transmision"))

    photo = item.get("imagen")
    photo_url = photo if isinstance(photo, str) and photo.startswith("http") else None

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
        photo_url=photo_url,
        vin=str(vin) if vin else None,
    )


# ---------------------------------------------------------------------------
# Fetch: GETs routed THROUGH the governor (same per-host choke point as toyota_lexus/coches.net).
# ---------------------------------------------------------------------------


class HyundaiFetcher:
    """A curl_cffi GET session for the hyundai listado + installations JSON surfaces.

    Both surfaces are single FLAT fetches (no offset cursor) so a 1-session fetcher is enough; the
    governor still paces every GET through the per-host bucket and runs it off the event loop. The
    `slot` kwarg rides through the governor for signature-coherence with the pooled fetchers (it is
    a no-op here — one session)."""

    def __init__(self) -> None:
        self._session = cffi_requests.Session(impersonate=_IMPERSONATE)
        self.last_status: int | None = None

    def fetch_json(self, url: str, *, slot: int = 0) -> dict:
        """The synchronous GET (runs in a worker thread via the governor). Raises on a non-200 so
        the breaker sees throttling (never masks a challenge/empty body)."""
        resp = self._session.get(url, headers=_HEADERS, impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url}")
        return json.loads(resp.content.decode("utf-8", "replace"))

    async def fetch_json_async(self, governed_fetch, url: str) -> dict:
        return await governed_fetch(url, slot=0)


# ---------------------------------------------------------------------------
# DB layer (mirrors oem_toyota_lexus_wholesale: ensure platform, bulk-upsert dealer/vehicle, link
# edge, emit delta, all idempotent ON CONFLICT). Multi-axis 0016 classification set.
# ---------------------------------------------------------------------------

HY_PLATFORM_RECIPE = {
    "version": 1,
    "source": "hyundai (www.hyundai.es/seminuevos)",
    "scope": "platform-wholesale (Hyundai Promise / Ocasión ES certified-used; OpenCart + internal JSON API)",
    "engine": "curl_cffi+chrome131_impersonate+internal_opencart_json_api(GET)",
    "access": ("OPEN-via-fingerprint (a WAF 403s a stripped fetch; chrome131 TLS/JA3 passes "
               "cleanly). No proxy, no browser, no cookie warm-up, no auth, €0. Public site behind "
               "a WAF -> is_tier1=TRUE; the JSON API serves to curl_cffi -> defense_tier=t1_soft."),
    "data_surface": "internal_api",
    "surface_intent": "internal_opencart_json_api",
    "endpoint": "GET https://www.hyundai.es/seminuevos/index.php?route=product/vehiculo/listado",
    "dealer_geo_endpoint": "GET https://www.hyundai.es/concesionarios/index.php?route=api/installation/seminuevos",
    "request": {
        "headers": "Accept application/json, X-Requested-With XMLHttpRequest, Referer /seminuevos/",
        "params": "none (the listado returns the WHOLE national stock flat in one response)",
    },
    "enumeration": ("SINGLE flat GET -> {vehiculos:[...]} (2036 cars live; no pagination, no "
                    "offset cursor, no relevance cap, no depth wall). dedup on the VIN (bastidor) "
                    "— the vehiculo_id token ROTATES every fetch and must NOT be the dedup key. "
                    "The dealer-geo GET is fetched ONCE and joined per car."),
    "denominator": "len(vehiculos) (the listado list length == the portal's declared full stock)",
    "platform_entity": ("kind=oem_vo_portal, province_code=NULL (sentinel 00 in cdp_code only), "
                        "is_tier1=TRUE, defense_tier=t1_soft, source_group=oem_vo_portal, role=platform, "
                        "family=hyundai_vo"),
    "dual_membership": ("vehicle.entity_ulid=SELLING DEALER (compraventa); "
                        "platform_listing edge=platform<->vehicle"),
    "field_map": {
        "deep_link": "VIN-anchored canonical .../seminuevos/#vin={bastidor} (STABLE; the PDP token rotates)",
        "listing_ref": "vehiculos[].bastidor (the VIN — the STABLE per-car id + dedup key)",
        "vin": "vehiculos[].bastidor (REAL per-car VIN — gold for cross-source dedup; 100% present)",
        "make": "constant 'Hyundai' (brand-pure portal; busqueda.marcas==['91'])",
        "model": "vehiculos[].modelo ('OTROS' -> NULL, the portal catch-all bucket)",
        "version": "vehiculos[].version",
        "year": "vehiculos[].matriculacion (DD-MM-YYYY -> YYYY)",
        "km": "vehiculos[].kilometraje ('15.000km' -> 15000)",
        "price": "vehiculos[].importe_financiar (numeric) or importe ('19.900' -> 19900)",
        "fuel": "vehiculos[].combustible (latin-1 repaired)",
        "transmission": "vehiculos[].transmision (latin-1 repaired)",
        "dealer": "vehiculos[].concesionario (NAME) + telefono (PHONE) -> joined to installations API",
        "dealer_geo": ("installations API: {concesionario_id, name, phone, zipcode, zone, city, "
                       "lat, lon}. Join car->installation by PHONE (exact) then NAME (normalized + "
                       "token-subset). Province = zipcode[:2] (INE, authoritative); lat/lon fallback."),
    },
    "caveats": {
        "token_rotation": ("the detail-page vehiculo_id token ROTATES on every listado fetch "
                          "(0/2036 stable across consecutive fetches) — it is ephemeral, NOT a car "
                          "id. The VIN (bastidor) is the stable dedup key + deep_link anchor."),
        "single_flat_response": "the listado returns the WHOLE national stock in one GET — no pagination.",
        "split_dealer_geo": ("the listado has NO dealer location; geo comes from a SECOND JSON API "
                             "(installations) joined by phone/name. Cars that match no installation "
                             "are geo-skipped (no FK risk)."),
        "latlon_swap": ("installations carry a correct lat/lon AND a SWAPPED latitud/longitud; read "
                        "lat/lon (Spain lat 36..44, lon -9..4). The site's own JS compensates."),
        "encoding": ("car/dealer/fuel text is latin-1 mojibake (Corriente el�ctrica, autom�tico, "
                     "L�Aldea); repair with s.encode('latin-1').decode('utf-8'). vehiculo_id/VIN/"
                     "numeric clean."),
        "model_otros": "modelo=='OTROS' is a catch-all bucket, not a real model -> stored as NULL.",
        "no_private_sellers": "OEM certified-used portal — every car belongs to an official dealer.",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the hyundai platform entity + platform_meta exist. Returns the platform
    entity_ulid. kind='oem_vo_portal' (the platform ontology kind), is_tier1=TRUE (a WAF fronts the
    public site), multi-axis 0016 classification set explicitly, data_surface='internal_api'."""
    code = hy_platform_cdp_code()
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
        eulid, code, HY_KIND, HY_LEGAL_NAME, HY_TRADE_NAME, HY_WEBSITE,
        HY_WAF, HY_DEFENSE_TIER, HY_SOURCE_GROUP, HY_ROLE, HY_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, HY_SOURCE_KEY, HY_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'internal_api',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"endpoint": ENDPOINT, "host": host_of(ENDPOINT),
                           "method": "GET",
                           "dealer_geo_endpoint": INSTALL_ENDPOINT,
                           "denominator": "len(vehiculos)",
                           "surface_intent": "internal_opencart_json_api",
                           "engine": "curl_cffi/chrome131_impersonate"}),
        HY_FAMILY)
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    Hyundai dealers have no bare domain identity on this surface -> identity = name + location +
    the stable concesionario_id (passed via `address` so two distinct dealers that happen to share
    a name in one municipality never collapse to one entity)."""
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni, address=f"dealer:{d.dealer_id}")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


@dataclass
class _CageRow:
    """One fully-parsed, geo-anchored car ready for the bulk cage — the in-memory result of the
    parse+resolve phase, before any SQL."""
    dealer_id: str
    dealer_cdp: str
    dealer_name: str | None
    dealer_province: str
    dealer_muni: str | None
    vehicle: Vehicle


# The bulk statements — ONE round-trip per table (unnest-based multi-row upsert), byte-for-byte the
# same idempotency the row-by-row path uses. A re-run adds 0 rows and 0 events. Dealers carry the
# 0016 axes (oem_vo_portal/standalone_pos).

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


def _resolve_province(ins: Installation, geocoder: ProvinceGeocoder) -> str | None:
    """Resolve the dealer's INE province. PRIMARY: the installation zipcode's first 2 digits
    (authoritative, the renew/toyota model). FALLBACK: geocode from lat/lon (nearest labeled point)
    when the zip is missing/malformed. Returns a validated '01'..'52' code or None."""
    if ins.zip:
        digits = re.sub(r"\D", "", ins.zip)
        if len(digits) >= 2:
            prov = digits[:2]
            if "01" <= prov <= "52":
                return prov
    if ins.lat is not None and ins.lon is not None:
        prov = geocoder.nearest_province(ins.lat, ins.lon)
        if prov and prov.isdigit() and "01" <= prov <= "52":
            return prov
    return None


def _parse_all(vehiculos: list, directory: DealerDirectory, geo: GeoResolver,
               geocoder: ProvinceGeocoder, seen_ids: set, harvested_cageable: set,
               stats: dict) -> list[_CageRow]:
    """Parse + dealer-join + geo-resolve every car IN ORDER — pure CPU, no SQL.

    The EXACT per-item gate (dedup on the vehiculo_id token, dealer-join skip, geo skip, cageable
    truth), so the SQL phase is purely set-based. Each car is joined to its official dealer
    installation by phone (exact) then name (normalized + token-subset); the province is resolved
    zip-first then geocode-fallback from the matched installation. `seen_ids` / `harvested_cageable`
    / `stats` are mutated here with deterministic order semantics so the VAM truth is byte-identical
    regardless of batching."""
    rows: list[_CageRow] = []
    for item in vehiculos:
        if not isinstance(item, dict):
            continue
        stats["items_seen"] += 1
        v = parse_item_vehicle(item)
        # dedup on the stable vehiculo_id token (the listado is a single response, but a defensive
        # dedup keeps the cageable truth exact if the portal ever repeats an id).
        if v.listing_ref and v.listing_ref in seen_ids:
            stats["dup_ids_collapsed"] += 1
            continue
        if v.listing_ref:
            seen_ids.add(v.listing_ref)

        # Dealer-join gate: attribute the car to its official Hyundai installation.
        ins = directory.match(item.get("concesionario"), item.get("telefono"))
        if ins is None:
            stats["no_dealer_skipped"] += 1
            continue
        stats["dealer_items"] += 1

        # Geo gate — resolve the province (zip first, lat/lon fallback) from the matched
        # installation, then apply the same province-range guard the dealer upsert enforces, in
        # memory so a bad/missing geo is skipped without ever touching the DB (no FK risk).
        prov = _resolve_province(ins, geocoder)
        if not prov:
            stats["geo_skipped"] += 1
            continue
        # municipality: best-effort from the installation city literal (INE-resolved).
        muni = geo.municipality_code(prov, ins.city)
        d = DealerRef(dealer_id=ins.dealer_id, name=ins.name, province_code=prov,
                      city=ins.city, zip=ins.zip, lat=ins.lat, lon=ins.lon)
        dealer_cdp = cdp_code_dealer(d, muni)

        if not v.deep_link:
            continue
        harvested_cageable.add((d.dealer_id, v.deep_link))
        if v.vin:
            stats["vins_captured"] += 1
        rows.append(_CageRow(
            dealer_id=d.dealer_id, dealer_cdp=dealer_cdp, dealer_name=d.name,
            dealer_province=prov, dealer_muni=muni, vehicle=v))
    return rows


async def _ingest_all(conn: asyncpg.Connection, platform_ulid: str, cage: list[_CageRow],
                      stats: dict) -> None:
    """BULK-ingest the whole parsed cage in ONE transaction with set-based SQL.

    Mirrors oem_toyota_lexus_wholesale._ingest_window EXACTLY: ONE round-trip per table (unnest
    multi-row upserts). The delta/VAM/platform_listing semantics are preserved: same ON CONFLICT
    idempotency, same cageable truth, same NEW-event rule (emitted only for genuinely new
    vehicles). A re-run adds 0 rows and 0 events.
    """
    if not cage:
        return

    async with conn.transaction():
        # ---- (2) DEALERS: dedup by cdp_code, bulk-upsert, resolve ulids.
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
                           d_munis, d_refs, HY_SOURCE_KEY)
        await conn.execute(_BULK_UPSERT_DEALER_SOURCES, d_cdps, d_refs, HY_SOURCE_KEY)
        cdp_to_ulid: dict[str, str] = {
            row["cdp_code"]: row["entity_ulid"]
            for row in await conn.fetch(
                "SELECT cdp_code, entity_ulid FROM entity "
                "WHERE cdp_code = ANY($1::text[])", d_cdps)
        }

        # ---- attach resolved dealer_ulid to each cage row; dedup cars by (dealer_ulid, deep_link)
        # so the same ad attributed twice is one car.
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
                payload = {"price": v.price, "title": v.title, "platform": HY_TRADE_NAME}
                if v.vin:
                    payload["vin"] = v.vin
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities,
                               ev_payloads)
            stats["new_events"] += len(confirmed_new)


async def harvest(limit: int | None = None) -> dict:
    conn = await asyncpg.connect(DSN)
    fetcher = HyundaiFetcher()
    stats = {
        "pages_fetched": 0, "items_seen": 0, "dealer_items": 0,
        "no_dealer_skipped": 0, "geo_skipped": 0, "new_dealers": 0, "cars_caged": 0,
        "new_cars": 0, "edges_created": 0, "new_events": 0, "vins_captured": 0,
        "declared_full": None, "dup_ids_collapsed": 0, "dealers_distinct": 0,
        "installations_loaded": 0, "limit": limit, "private_skipped": 0,
    }
    # Harvest-side truth for the VAM: distinct CAGEABLE cars = distinct (dealer_id, deep_link) pairs
    # that survived dealer-join + geo-resolution. Like-with-like vs db_edges.
    harvested_cageable: set[tuple[str, str]] = set()

    # S-HEALTH gate: if the breaker is OPEN (a recent ban/throttle still cooling), skip the drain
    # gracefully — the API keeps serving the last snapshot.
    if await is_open(conn, HY_SOURCE_KEY):
        print(f"[oem_hyundai] breaker OPEN for {HY_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, API still serves last snapshot).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": HY_SOURCE_KEY}

    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch_json)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        geo = await GeoResolver.load(conn)
        geocoder = await ProvinceGeocoder.load(conn)
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = hy_platform_cdp_code()
        print(f"[oem_hyundai] platform entity ready: {platform_code} (ulid={platform_ulid}) "
              f"kind={HY_KIND} group={HY_SOURCE_GROUP} tier={HY_DEFENSE_TIER} family={HY_FAMILY}")
        print(f"[oem_hyundai] geocoder anchors: {geocoder.size()} labeled points (lat/lon -> province).")
        print(f"[oem_hyundai] governor paces host {host_of(ENDPOINT)} (per-host token bucket, STEALTH class).")

        seen_ids: set[str] = set()
        dealers_before = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

        # ---- (A) fetch the dealer-geo directory ONCE (the installations API), through the governor.
        try:
            inst_data = await fetcher.fetch_json_async(governed_fetch, INSTALL_ENDPOINT)
            stats["pages_fetched"] += 1
        except Exception as exc:  # noqa: BLE001 — surface the fetch error to the breaker.
            fetch_error = str(exc)
            last_http = fetcher.last_status
            print(f"[oem_hyundai] installations fetch failed ({exc}); stopping drain honestly.")
            inst_data = None

        directory = DealerDirectory([])
        if inst_data is not None:
            raw_inst = inst_data.get("instalaciones") or []
            installations = [i for i in (parse_installation(x) for x in raw_inst) if i is not None]
            directory = DealerDirectory(installations)
            stats["installations_loaded"] = len(installations)
            print(f"[oem_hyundai] dealer directory: {len(installations)} official installations "
                  f"loaded (phone+name index for car->dealer attribution).")

        # ---- (B) fetch the WHOLE national stock ONCE (the listado API), through the governor.
        vehiculos: list = []
        if fetch_error is None:
            try:
                listado = await fetcher.fetch_json_async(governed_fetch, ENDPOINT)
                stats["pages_fetched"] += 1
                vehiculos = listado.get("vehiculos") or []
                stats["declared_full"] = len(vehiculos)
                print(f"[oem_hyundai] listado: {len(vehiculos)} cars declared (full national stock, "
                      f"single flat response).")
            except Exception as exc:  # noqa: BLE001
                fetch_error = str(exc)
                last_http = fetcher.last_status
                print(f"[oem_hyundai] listado fetch failed ({exc}); stopping drain honestly.")

        # --limit bounds the run to a proof slice (the first N cars in listado order).
        if limit is not None and limit > 0:
            vehiculos = vehiculos[:limit]
            print(f"[oem_hyundai] --limit {limit}: capping this run to the first {len(vehiculos)} cars.")

        # ---- (C) parse + dealer-join + geo-resolve, then BULK-ingest in one transaction.
        if vehiculos:
            cage = _parse_all(vehiculos, directory, geo, geocoder, seen_ids,
                              harvested_cageable, stats)
            await _ingest_all(conn, platform_ulid, cage, stats)
            print(f"[oem_hyundai] ingest done: items={stats['items_seen']} "
                  f"dealer_items={stats['dealer_items']} caged={stats['cars_caged']} "
                  f"new={stats['new_cars']} edges={stats['edges_created']} "
                  f"no_dealer={stats['no_dealer_skipped']} geo_skip={stats['geo_skipped']} "
                  f"dealers_seen={len(harvested_cageable)}")

        dealers_after = {r["cdp_code"] for r in await conn.fetch(
            "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
        stats["new_dealers"] = len(dealers_after - dealers_before)
        stats["dealers_distinct"] = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
               JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
               WHERE pl.platform_entity_ulid = $1""", platform_ulid)

        recipe_path = write_recipe(platform_code, HY_PLATFORM_RECIPE)
        print(f"[oem_hyundai] recipe written: {recipe_path}")

        # VAM count quorum for the slice — THREE orthogonal like-with-like paths that all measure
        # "distinct cageable cars in this slice":
        #   db_edges           = platform_listing rows for hyundai   (DB write truth)
        #   db_join_vehicles   = distinct vehicles via the edge join  (DB read truth)
        #   harvested_cageable = distinct (dealer_id, deep_link) pulled (harvest truth)
        # The declared full count is reported for honesty but is NOT a quorum path (it measures the
        # WHOLE portal stock, not necessarily this slice unless the full drain ran).
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

        # S-HEALTH heartbeat: record THIS run's outcome so the watchdog tracks hyundai, trips the
        # breaker on a ban, and auto-repairs. OK when both surfaces fetched, no fetch error stopped
        # the drain, and the VAM did not refute.
        run_ok = fetch_error is None and stats["cars_caged"] > 0 and verdict != "REFUTED"
        run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
        outcome = await record_run(
            conn, HY_SOURCE_KEY, ok=run_ok, rows=stats["cars_caged"],
            error=run_error, http_status=last_http)
        stats["health_status"] = outcome.status
        stats["breaker_state"] = outcome.breaker_state
        if not run_ok:
            stats["repair_action"] = await auto_repair(
                conn, HY_SOURCE_KEY, run_error or "harvest failed",
                phase="scrape", http_status=last_http)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[oem_hyundai] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("HYUNDAI (OEM-VO PORTAL) WHOLESALE HARVEST — REPORT")
    print("=" * 64)
    print(f"  platform cdp_code     : {stats.get('platform_code')}")
    print(f"  group / kind          : oem_vo_portal / oem_vo_portal (tier t1_soft, family hyundai_vo)")
    print(f"  declared full (source): {stats.get('declared_full')} (listado length)")
    print(f"  installations loaded  : {stats.get('installations_loaded')} (dealer-geo directory)")
    print(f"  items seen            : {stats['items_seen']}")
    print(f"  dealer items          : {stats['dealer_items']}")
    print(f"  no-dealer skipped     : {stats['no_dealer_skipped']} (no installation match)")
    print(f"  private skipped       : {stats['private_skipped']} (OEM portal — none expected)")
    print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (vehiculo_id dedup)")
    print(f"  geo skipped (bad geo) : {stats['geo_skipped']}")
    print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
          f"({stats['new_dealers']} new this run)")
    print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
    print(f"  platform_listing edges: {stats['edges_created']} created "
          f"(db total for hyundai = {stats.get('db_edges')})")
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
        description="hyundai OEM-VO portal wholesale harvester (single-flat-response internal-JSON drain)")
    parser.add_argument("--limit", type=int, default=None,
                        help=("optional target car count (proof slice = the first N cars in listado "
                              "order). With no --limit the whole national stock is caged in one run."))
    args = parser.parse_args()
    stats = asyncio.run(harvest(args.limit))
    _print_report(stats)


if __name__ == "__main__":
    main()
