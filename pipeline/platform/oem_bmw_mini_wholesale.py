"""oem_bmw_mini (BMW + MINI ES certified-used) WHOLESALE harvester — a THIRD/FOURTH OEM-VO portal, end to end.

www.bmwpremiumselection.es is the manufacturer certified-used portal for BMW in Spain
("BMW Premium Selection"); www.mininext.es is the sibling portal for MINI ("MINI Next"). Both are
run on the SAME Motorflash dealer-stock backend (identical per-car card markup, identical
?pagina=N dealer paginator). Like renew (Renault Group), Das WeltAuto (VW Group) and spoticar
(Stellantis) they are NOT car-specialist marketplaces (coches.net/autoscout24/motor.es) nor
generalist classifieds (wallapop): they are OEM-VO PORTALS — a single brand-owner publishing the
certified-used inventory of its own official dealer network (concesionarios oficiales). They join
the 'oem_vo_portal' source_group, in a new 'bmw_group_vo' family, siblings under the same ONE
architecture as renew/spoticar/dasweltauto.

THE SURFACE (data-layer way, uncapped). Both sites are a server-rendered Motorflash listing. The
DEALER ROSTER is published in each brand's sitemap.xml (BMW 51 dealers, MINI 47). Each dealer has
a deep, server-rendered listing paginator: GET /concesionarios/{prov}/{dealer}[/]?pagina=N. Every
car on a listing page is rendered as a CARD of hidden <input> fields (anuncio_id, precio,
marcaVehiculo, modeloVehiculo, kilometros, bastidorVehiculo=VIN, fechamatriculacion, gtm_url,
gtm_name, gtm_category, tracy_fuelType, tracy_gearing, tracy_yearOfRegistration, img, and for MINI
also concesionario/provincia). The whole per-car payload — INCLUDING the real VIN — is embedded in
the listing card: NO PDP fetch needed. 12 cars/page, FLAT per dealer (no relevance cap, no depth
wall); the dealer's id_total_resultados bounds its walk. Σ over the roster = the full ES public
stock for that brand. The brand's sitemap-ofertas.xml (BMW: 2,495 PDP URLs) is a cross-check
denominator. Verified live 2026-06-13 (docs/architecture/tier1_recipes/oem_bmw_mini_datalayer.md).

ACCESS. The public site is fronted by a CDN/WAF that 403s some bot egress (plain WebFetch is
walled); curl_cffi impersonate="chrome131" serves cleanly with no proxy, no browser, no cookie
warm-up, no auth (defense_tier=t1_soft, is_tier1=TRUE — a WAF is present but serving to curl_cffi).

This module mirrors pipeline.platform.spoticar_wholesale EXACTLY (the proven OEM-VO template: same
dual-membership model, same bulk cage, same governor/health/VAM wiring). It proves the OEM-VO group
flows through the ONE architecture, not a fork of it:

  bmwpremiumselection / mininext (the OEM-VO portal) -> entity, kind='oem_vo_portal'   [THE PLATFORM]
  each SELLING DEALER (concesionario oficial)        -> entity, kind='compraventa'
  each CAR                                            -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
  the car ON the portal                              -> platform_listing edge (platform <-> vehicle)

Ownership is singular (the selling dealer); platform membership is plural (this edge). The same
physical car can carry BOTH a bmwpremiumselection edge and a coches.net edge without ever changing
its owning dealer.

GEO anchor: the SELLING DEALER's province is encoded in the listing/PDP URL path
(/concesionarios/{province-slug}/{dealer-slug}/...). The province-slug resolves to the INE province
code via GeoResolver.province_code (a couple of brand slugs are normalized first:
'sta-c-tenerife'->Santa Cruz de Tenerife, 'guipuzcoa'->Gipuzkoa). The dealer NAME is the
concesionario_<id> field when present (MINI) else the de-slugified dealer-slug (BMW). The
dealer-slug is the stable per-dealer key (source_ref + cdp_code address anchor).

Encoding trap: brand/dealer/title text is latin-1 mojibake over the wire (a�o = "año",
H�brido = "Híbrido", autom�tico = "automático"). Re-encode every human-text field:
s.encode("latin-1").decode("utf-8"). The numeric inputs (precio, kilometros), the VIN and the
URL path are clean. The fuel/gearbox labels additionally carry a U+FFFD AT THE SOURCE on some
pages (Di�sel/El�ctrico) the latin-1 round-trip can't recover — so they are normalized through a
fixed clean vocabulary keyed on accent-stripped tokens (no invention, the clean signal preferred).

Multi-axis classification (migrations/0016):
  defense_tier = 't1_soft'         (WAF present, 403s plain bot egress; serving to curl_cffi; no JS challenge)
  source_group = 'oem_vo_portal'   (the group renew opened; this is its 3rd/4th member)
  role         = 'platform'
  kind         = 'oem_vo_portal'   (the platform entity's ontology kind, migrations/0005)
  is_tier1     = TRUE              (the public site sits behind a WAF/CDN)
  family       = 'bmw_group_vo'    (ties the BMW-group OEM-VO siblings on the family axis)

ONE MODULE, BOTH BRANDS. --brand bmw | mini | both (default both). Each brand is its own platform
entity (its own cdp_code, its own dealer roster, its own VAM slice). 'both' harvests them
back-to-back through the same governor/health/connection.

PROOF SLICE OR FULL. A full run walks every dealer in the roster to its id_total_resultados.
--dealers bounds the roster (a few dealers = a proof slice; the full roster = the full brand
stock). --limit converts a target car count to a dealer/page budget. The brand's declared total
(Σ id_total_resultados over the roster) is recorded for the VAM verdict's slice arithmetic.

Engine: a GET against the dealer listing routed THROUGH the per-host governor (the same single
choke point coches.net/renew/spoticar use). The synchronous curl_cffi GET runs in a worker thread
so the event loop is never blocked, and no host is fetched faster than its bucket (the two hosts
inherit the conservative STEALTH class — t1_soft).

Run: python -m pipeline.platform.oem_bmw_mini_wholesale --brand both
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
import re
import unicodedata
from dataclasses import dataclass

import asyncpg
from curl_cffi import requests as cffi_requests

from pipeline.engine.governor import governor, host_of
from pipeline.geo import GeoResolver
from pipeline.ids import ulid
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict
from services.api.codes import _base32, cdp_code

DSN = "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
DSN = os.environ.get("CARDEEP_DSN", DSN)

# ---------------------------------------------------------------------------
# Per-brand platform identity (OEM-VO portal, migrations/0005 + 0016). Both brands ride the SAME
# Motorflash backend; only the host, names and trailing-slash rule differ.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BrandSpec:
    key: str                 # 'bmw' | 'mini'
    domain: str              # bare domain (cdp_code identity + entity_source ref)
    base: str                # https origin
    legal_name: str
    trade_name: str
    source_key: str
    make_label: str          # the expected marcaVehiculo prefix ('BMW' | 'MINI')
    dealer_trailing_slash: bool  # BMW dealer pages REQUIRE a trailing slash; MINI 404s on one.


BMW = BrandSpec(
    key="bmw",
    domain="bmwpremiumselection.es",
    base="https://www.bmwpremiumselection.es",
    legal_name="BMW Ibérica (BMW Premium Selection)",
    trade_name="bmw_premium_selection",
    source_key="oem_bmw_premium_selection_wholesale",
    make_label="BMW",
    dealer_trailing_slash=True,
)
MINI = BrandSpec(
    key="mini",
    domain="mininext.es",
    base="https://www.mininext.es",
    legal_name="BMW Ibérica (MINI Next)",
    trade_name="mini_next",
    source_key="oem_mini_next_wholesale",
    make_label="MINI",
    dealer_trailing_slash=False,
)
BRANDS = {BMW.key: BMW, MINI.key: MINI}

# Shared classification axes (identical backend / posture for both brands).
WAF = "other"               # a CDN/WAF 403s plain bot egress; no Akamai/Cloudflare server header.
DEFENSE_TIER = "t1_soft"    # WAF present but serving to curl_cffi (no JS challenge) -> tier 1 soft.
SOURCE_GROUP = "oem_vo_portal"
ROLE = "platform"
KIND = "oem_vo_portal"      # the platform ENTITY's ontology kind (NOT 'plataforma').
FAMILY = "bmw_group_vo"     # ties the BMW-group OEM-VO siblings on the family axis.

_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
}
_IMPERSONATE = "chrome131"
_TIMEOUT = 40
PAGE_SIZE = 12  # the Motorflash listing serves a FIXED 12 cars/page (not overridable — verified).

# Province sentinel '00' = national (same convention as renew/spoticar/coches.net). geo_province has
# NO '00', so the platform ENTITY stores province_code = NULL; '00' lives only inside the cdp_code
# string (free text, no FK). We never pollute geo_province with it.
PLATFORM_PROVINCE_SENTINEL = "00"

# A small dealer can be harvested in 1 page; a large one in dozens. The roster bounds the run; each
# dealer is walked to ceil(id_total_resultados / 12) pages. Over-pagination CLAMPS to the last page
# and REPEATS cards (Motorflash phantom-repeat), so we bound by the declared total + dedup on
# anuncio_id — never trust emptiness alone (it never empties).
MAX_DEALER_PAGES = 200  # hard ceiling per dealer (no real dealer approaches this) — a safety stop.

# Province-slug normalization for the few brand slugs GeoResolver can't resolve verbatim. The slug
# lives in the /concesionarios/{slug}/... URL path; '-' -> ' ' then this map, then GeoResolver.
_PROVINCE_SLUG_FIX = {
    "sta-c-tenerife": "santa cruz de tenerife",
    "sta-cruz-tenerife": "santa cruz de tenerife",
    "guipuzcoa": "gipuzkoa",
}

# Fuel/gearbox clean vocabulary. The Motorflash labels arrive latin-1 mojibake AND some carry a
# U+FFFD already substituted AT THE SOURCE (Di�sel/El�ctrico) the latin-1 round-trip cannot recover.
# So normalize through a fixed vocabulary keyed on the ACCENT-STRIPPED token — the clean signal
# preferred, no lossy replacement char stored. This is a finite, verified vocabulary (no invention).
_FUEL_CLEAN = {
    "diesel": "Diésel", "gasolina": "Gasolina", "electrico": "Eléctrico",
    "hibrido": "Híbrido", "hibridoenchufable": "Híbrido enchufable",
    "hibridoelectrogasolina": "Híbrido", "hibridoelectrodiesel": "Híbrido",
    "hibridos": "Híbrido", "glp": "GLP", "gnc": "GNC",
}
_GEAR_CLEAN = {"automatico": "Automático", "manual": "Manual"}


def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def _clean_fuel(*candidates) -> str | None:
    """Map the (mojibake/U+FFFD-bearing) fuel label to a clean Spanish label via the accent-stripped
    vocabulary. Tries each candidate (the tracy_fuelType last segment, the gtm_category last
    segment); the U+FFFD is stripped by keeping only letters before the lookup."""
    for raw in candidates:
        val = _fix(raw)
        if not isinstance(val, str) or not val.strip():
            continue
        # take the most specific token (last '/'-segment if a path-like value slipped through)
        token = val.split("/")[-1].strip()
        key = re.sub(r"[^a-z]", "", _strip_accents(token).lower())
        mapped = _FUEL_CLEAN.get(key)
        if mapped:
            return mapped
    # fall back to a repaired literal if it has no replacement char, else None (never store U+FFFD)
    for raw in candidates:
        val = _fix(raw)
        if isinstance(val, str) and val.strip() and "�" not in val:
            return val.split("/")[-1].strip()
    return None


def _clean_gearbox(raw) -> str | None:
    """Normalize the finite gearbox vocabulary. Source values look like 'Cambio automático' /
    'Cambio manual' (the accented form may carry U+FFFD)."""
    val = _fix(raw)
    if not isinstance(val, str) or not val.strip():
        return None
    key = re.sub(r"[^a-z]", "", _strip_accents(val).lower())
    for vocab_key, label in _GEAR_CLEAN.items():
        if vocab_key in key:
            return label
    return None


# ---------------------------------------------------------------------------
# Field helpers (the Motorflash surface: hidden-input card fields + latin-1 mojibake).
# ---------------------------------------------------------------------------


def _fix(s):
    """Repair latin-1 mojibake on human-text fields (a�o -> año, H�brido -> Híbrido). The wire bytes
    were UTF-8 mis-decoded as latin-1 upstream; re-encode to recover. Numeric inputs, VIN and URL
    path are clean and never passed here."""
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
        return int(str(v).replace(".", "").replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def _to_float(v):
    if v is None:
        return None
    try:
        return float(str(v).replace(".", "").replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def _deslug(slug: str) -> str:
    """De-slugify a dealer/province URL token into a human name ('a-coruna' -> 'a coruna',
    'burgocar' -> 'burgocar'). Used as the dealer NAME fallback (BMW cards omit concesionario_<id>)
    and as the province-name lookup key."""
    return (slug or "").replace("-", " ").replace("_", " ").strip()


def _province_from_slug(slug: str, geo: GeoResolver) -> str | None:
    """Resolve a /concesionarios/{slug}/... province-slug to its INE province code. Apply the
    brand-slug fix map first, then GeoResolver.province_code (normalized name lookup)."""
    if not slug:
        return None
    fixed = _PROVINCE_SLUG_FIX.get(slug.lower(), _deslug(slug))
    return geo.province_code(fixed)


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL listing card markup — field names inspected live 2026-06-13).
# ---------------------------------------------------------------------------


@dataclass
class DealerRef:
    """The selling official dealer (concesionario oficial) parsed from the listing URL path + card.

    The dealer-slug (URL path segment) is the stable per-dealer key; the province comes from the
    province-slug in the same path. The dealer NAME is the concesionario_<id> field when present
    (MINI) else the de-slugified dealer-slug (BMW). Two distinct dealers never collapse because the
    cdp_code address anchor carries the unique dealer-slug."""
    dealer_slug: str
    name: str | None
    province_code: str | None
    city: str | None


@dataclass
class Vehicle:
    """A car parsed from a single Motorflash listing card."""
    deep_link: str
    listing_ref: str           # anuncio_id — stable car id AND the dedup key.
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    vin: str | None            # REAL per-car VIN (bastidorVehiculo) — gold for cross-source dedup.


# Card-field regexes. The hidden inputs come in two shapes:
#   plain:  name="precio" value="49500"               (one per card)
#   id'd :  id="gtm_url_<anuncio_id>" ... value="..."  (one per car, suffixed by the id)
# Attribute spacing is irregular over the wire (name ="x", value="y") — the regexes tolerate \s*.
_RE_ANUNCIO_ID = re.compile(r'name\s*=\s*["\']anuncio_id["\']\s+value\s*=\s*["\'](\d+)["\']')
_RE_VIN = re.compile(r'bastidorVehiculo["\']?\s*value\s*=\s*["\']([A-Z0-9]{11,20})["\']')


def _plain(seg: str, name: str) -> str | None:
    m = re.search(r'name\s*=\s*["\']' + re.escape(name) + r'["\']\s+value\s*=\s*["\']([^"\']*)["\']', seg)
    return m.group(1) if m else None


def _idfield(seg: str, prefix: str, cid: str) -> str | None:
    m = re.search(r'id\s*=\s*["\']' + re.escape(prefix) + "_" + re.escape(cid)
                  + r'["\'][^>]*value\s*=\s*["\']([^"\']*)["\']', seg)
    return m.group(1) if m else None


def parse_cards(html: str, brand: BrandSpec, dealer_slug: str, province_slug: str,
                geo: GeoResolver) -> list[tuple[DealerRef, Vehicle]]:
    """Parse every car CARD on a dealer listing page into (DealerRef, Vehicle) pairs.

    The page is split into per-anuncio_id windows; each car's fields are pulled from its window.
    The dealer is shared across the page (same dealer-slug/province), but the concesionario_<id>
    name is read per card (MINI) and falls back to the de-slugified dealer-slug (BMW)."""
    pairs: list[tuple[DealerRef, Vehicle]] = []
    starts = [m.start() for m in _RE_ANUNCIO_ID.finditer(html)]
    ids = [m.group(1) for m in _RE_ANUNCIO_ID.finditer(html)]
    if not starts:
        return pairs
    bounds = starts + [len(html)]
    prov = _province_from_slug(province_slug, geo)

    for i, cid in enumerate(ids):
        seg = html[max(0, bounds[i] - 600):bounds[i + 1]]

        price = _to_float(_plain(seg, "precio"))
        make = _fix(_plain(seg, "marcaVehiculo"))
        model = _fix(_plain(seg, "modeloVehiculo"))
        km = _to_int(_plain(seg, "kilometros"))
        if km is not None and (km < 0 or km > 5_000_000):
            km = None

        vin_m = _RE_VIN.search(seg)
        vin = vin_m.group(1) if vin_m else None

        # year: prefer the clean tracy_yearOfRegistration; else parse fechamatriculacion (DD / MM / YYYY).
        year = _to_int(_idfield(seg, "tracy_yearOfRegistration", cid))
        if year is None:
            reg = _plain(seg, "fechamatriculacion") or _idfield(seg, "tl_fechamatriculacion", cid)
            ym = re.search(r"(\d{4})", reg or "")
            year = _to_int(ym.group(1)) if ym else None
        if year is not None and not (1900 <= year <= 2100):
            year = None

        url = _idfield(seg, "gtm_url", cid) or _idfield(seg, "url", cid) or ""
        deep_link = (brand.base + url) if isinstance(url, str) and url.startswith("/") else (url or "")

        # title: the human name (gtm_name carries 'BMW X1 del año 2026 por…'); prefer the tracy
        # productName joined with make, else the gtm_name, else make+model.
        prod = _fix(_idfield(seg, "tracy_productName", cid))
        gtm_name = _fix(_idfield(seg, "gtm_name", cid) or _idfield(seg, "name", cid))
        if prod and make:
            title = f"{make} {prod}"
        elif gtm_name:
            title = gtm_name
        else:
            title = " ".join(p for p in (make, model) if p) or None

        fuel = _clean_fuel(_idfield(seg, "tracy_fuelType", cid), _idfield(seg, "gtm_category", cid))
        transmission = _clean_gearbox(_idfield(seg, "tracy_gearing", cid))
        photo = _idfield(seg, "img", cid) or _idfield(seg, "gtm_img", cid)

        dealer_name = _fix(_idfield(seg, "concesionario", cid)) or _deslug(dealer_slug).title()
        dealer_city = _fix(_idfield(seg, "provincia", cid))  # MINI carries a city/province literal

        if not deep_link or not cid:
            continue
        pairs.append((
            DealerRef(dealer_slug=dealer_slug, name=dealer_name, province_code=prov, city=dealer_city),
            Vehicle(deep_link=deep_link, listing_ref=str(cid), title=title, make=make, model=model,
                    year=year, km=km, price=price, fuel=fuel, transmission=transmission,
                    photo_url=photo if isinstance(photo, str) and photo.startswith("http") else None,
                    vin=str(vin) if vin else None),
        ))
    return pairs


def _dealer_total(html: str) -> int | None:
    """The dealer's declared stock count (id_total_resultados) — bounds its page walk."""
    m = re.search(r'id_total_resultados[^>]*value\s*=\s*["\']?(\d+)', html)
    return _to_int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# Fetch: a GET routed THROUGH the governor (same per-host choke point as renew/spoticar).
# ---------------------------------------------------------------------------


class MotorflashFetcher:
    """A POOL of fingerprint-coherent curl_cffi GET sessions for the Motorflash dealer listings.

    Same concurrency-vs-coherence model as SpoticarFetcher/RenewFetcher: a single curl_cffi Session
    is NOT safe to call from several threads at once, and the governor runs each fetch in its own
    worker thread. The fix is a bounded POOL — one Session per concurrency slot, each its own Chrome
    fingerprint + cookie jar. The governor's per-host bucket bounds the AGGREGATE rate across every
    session, so the pool widens parallelism WITHOUT out-pacing the host."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def fetch_text(self, url: str, *, page: int = 1, slot: int = 0) -> str:
        """The synchronous GET on pool session `slot` (runs in a worker thread).

        Handed to governor().wrap_fetch_text: the governor derives the host from `url`, waits on the
        per-host bucket, then runs THIS off the event loop. `slot` rides as a kwarg the governor
        forwards untouched, so each in-flight request GETs on its own leased, never-shared curl_cffi
        session (thread-safe). The ?pagina param is carried in the url already. Raises on a non-200
        so the breaker sees throttling (never masks a challenge/empty body)."""
        session = self._sessions[slot]
        resp = session.get(url, headers=_HEADERS, impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url}")
        return resp.content.decode("utf-8", "replace")

    async def fetch_text_async(self, governed_fetch, url: str, *, page: int) -> str:
        """Lease a pool slot, fetch `url` THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_fetch(url, page=page, slot=slot)
        finally:
            self._free.put_nowait(slot)


def _list_url(brand: BrandSpec, dealer_path: str, page: int) -> str:
    """Build the dealer-listing URL for a given page. dealer_path is '/concesionarios/{prov}/{slug}'.
    BMW requires a trailing slash before the query; MINI 404s on one."""
    base = brand.base + dealer_path + ("/" if brand.dealer_trailing_slash else "")
    return f"{base}?pagina={page}"


async def fetch_roster(fetcher: MotorflashFetcher, brand: BrandSpec) -> list[tuple[str, str]]:
    """Pull the dealer roster from the brand's sitemap.xml. Returns [(province_slug, dealer_slug)].
    Only /concesionarios/{prov}/{dealer} roots (2 path segments) are dealers; deeper URLs are cars
    or facet pages and are skipped."""
    sm_url = brand.base + "/sitemap.xml"
    html = await fetcher.fetch_text_async(
        governor().wrap_fetch_text(fetcher.fetch_text), sm_url, page=1)
    dealers: list[tuple[str, str]] = []
    seen = set()
    for loc in re.findall(r"<loc>([^<]+)</loc>", html):
        m = re.match(r"https?://[^/]+/concesionarios/([a-z0-9-]+)/([a-z0-9-]+)/?$", loc.strip())
        if m:
            key = (m.group(1), m.group(2))
            if key not in seen:
                seen.add(key)
                dealers.append(key)
    return dealers


# ---------------------------------------------------------------------------
# DB layer (mirrors spoticar_wholesale: ensure platform, bulk-upsert dealer/vehicle, link edge,
# emit delta, all idempotent ON CONFLICT). Multi-axis 0016 classification set.
# ---------------------------------------------------------------------------


def platform_cdp_code(brand: BrandSpec) -> str:
    """The brand platform's immutable cdp_code. Built from the bare domain identity
    (canonical_key 'domain:<domain>'), province segment '00' (national). Mirrors
    spoticar_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{brand.domain}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"


def _platform_recipe(brand: BrandSpec) -> dict:
    return {
        "version": 1,
        "source": f"{brand.trade_name} ({brand.base})",
        "scope": f"platform-wholesale ({brand.make_label} ES certified-used; Motorflash dealer-stock backend)",
        "engine": "curl_cffi+chrome131_impersonate+motorflash_dealer_listing(GET html cards)",
        "access": ("OPEN-via-fingerprint (a CDN/WAF 403s plain bot egress; chrome131 TLS/JA3 passes "
                   "cleanly). No proxy, no browser, no cookie warm-up, no auth, €0. Public site behind "
                   "a WAF/CDN -> is_tier1=TRUE; serves to curl_cffi -> defense_tier=t1_soft."),
        "data_surface": "json_ld",
        "surface_intent": "server_rendered_listing_cards (hidden-input projection; PDPs carry schema.org JSON-LD Car)",
        "endpoint": f"GET {brand.base}/concesionarios/{{prov}}/{{dealer}}"
                    + ("/" if brand.dealer_trailing_slash else "") + "?pagina=N",
        "enumeration": ("dealer roster from /sitemap.xml; per dealer walk ?pagina=1..ceil(total/12) "
                        "(12 cards/page, FLAT). id_total_resultados bounds each dealer; dedup on "
                        "anuncio_id. Over-pagination CLAMPS+repeats (phantom) — never trust emptiness. "
                        "Σ id_total_resultados over roster = full brand ES stock."),
        "denominator": ("Σ dealer id_total_resultados (roster) == distinct anuncio_id harvested; "
                        + (f"cross-check {brand.base}/sitemap-ofertas.xml ({{N}} PDP URLs)"
                           if brand.key == "bmw" else "sitemap-ofertas.xml is a BMW mirror for MINI — not used")),
        "platform_entity": ("kind=oem_vo_portal, province_code=NULL (sentinel 00 in cdp_code only), "
                            "is_tier1=TRUE, defense_tier=t1_soft, source_group=oem_vo_portal, "
                            "role=platform, family=bmw_group_vo"),
        "dual_membership": ("vehicle.entity_ulid=SELLING DEALER (compraventa, concesionario oficial); "
                            "platform_listing edge=platform<->vehicle"),
        "field_map": {
            "deep_link": "card gtm_url_<id> (prefixed with origin)",
            "listing_ref": "card anuncio_id (stable id + dedup key)",
            "vin": "card bastidorVehiculo (REAL per-car VIN — gold for cross-source dedup)",
            "make": "card marcaVehiculo",
            "model": "card modeloVehiculo (+ tracy_productName for the version)",
            "year": "card tracy_yearOfRegistration (fallback fechamatriculacion DD / MM / YYYY)",
            "km": "card kilometros",
            "price": "card precio (EUR)",
            "fuel": "card tracy_fuelType / gtm_category last segment -> clean vocabulary",
            "transmission": "card tracy_gearing ('Cambio automático'/'Cambio manual')",
            "photo_url": "card img_<id>",
            "dealer": "URL path /concesionarios/{province-slug}/{dealer-slug}; name=concesionario_<id> (MINI) else de-slugified dealer-slug (BMW)",
            "location": "province-slug -> ProvinceCode via GeoResolver.province_code (slug fix map first)",
        },
        "caveats": {
            "page_size": "fixed 12 cards/page.",
            "trailing_slash": ("BMW dealer pages REQUIRE a trailing slash; MINI 404s on one — "
                               "brand-specific."),
            "over_pagination": "pages beyond the last CLAMP and REPEAT cards (phantom) — bound by id_total_resultados + dedup on anuncio_id.",
            "encoding": ("title/dealer/fuel text is latin-1 mojibake (a�o, H�brido, autom�tico); "
                         "repair with s.encode('latin-1').decode('utf-8'). Fuel/gearbox additionally "
                         "carry U+FFFD at source -> normalized via a clean accent-stripped vocabulary."),
            "mini_sitemap_ofertas": "mininext.es/sitemap-ofertas.xml mirrors BMW PDPs (misconfig) — NOT a MINI surface.",
            "no_private_sellers": "OEM certified-used portal — every car belongs to an official dealer.",
        },
    }


async def ensure_platform_entity(conn: asyncpg.Connection, brand: BrandSpec) -> str:
    """Idempotently ensure the brand platform entity + platform_meta exist. Returns the platform
    entity_ulid. kind='oem_vo_portal', is_tier1=TRUE (a WAF fronts the public site), multi-axis 0016
    classification set explicitly, data_surface='html'."""
    code = platform_cdp_code(brand)
    eulid = ulid()
    endpoint = (brand.base + "/concesionarios/{prov}/{dealer}"
                + ("/" if brand.dealer_trailing_slash else "") + "?pagina=N")
    host = host_of(brand.base + "/")
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
        eulid, code, KIND, brand.legal_name, brand.trade_name, brand.domain,
        WAF, DEFENSE_TIER, SOURCE_GROUP, ROLE, brand.source_key)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, brand.source_key, brand.domain)
    # data_surface='json_ld': the per-car payload is structured data embedded in the page — BMW PDPs
    # carry real schema.org JSON-LD <Car> blocks, and the listing cards are a structured hidden-input
    # projection of the same fields. 'json_ld' is the constraint-valid surface kind closest to this
    # embedded-structured-data nature (migrations: data_surface ∈ next_data/graphql/json_ld/
    # internal_api/sitemap/es_facet/app_api); the precise 'server_rendered_listing_cards' intent is
    # recorded in surface_detail.surface_intent.
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'json_ld',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"endpoint": endpoint, "host": host, "method": "GET",
                           "page_size": PAGE_SIZE, "denominator": "Σ id_total_resultados",
                           "surface_intent": "server_rendered_listing_cards",
                           "engine": "curl_cffi/chrome131_impersonate"}),
        FAMILY)
    return eulid


def cdp_code_dealer(d: DealerRef, muni: str | None) -> str:
    """Mint the dealer's immutable cdp_code via the canonical generator.

    These dealers have no bare domain on this surface -> identity = name + location + the stable
    dealer-slug (passed via `address` so two distinct dealers sharing a name in one province never
    collapse to one entity)."""
    return cdp_code(province_code=d.province_code, domain=None, name=d.name,
                    municipality_code=muni, address=f"dealer:{d.dealer_slug}")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# Default concurrency: pages fetched in parallel per dealer. The hosts are NOT in the governor's
# JSON_API rate class — they inherit the conservative STEALTH default, the safe direction for a
# t1_soft WAF host whose true ceiling is unmeasured. The concurrency only needs to keep that (slow)
# bucket saturated; a small window is plenty.
DEFAULT_CONCURRENCY = 4


@dataclass
class _CageRow:
    """One fully-parsed, geo-anchored car ready for the bulk cage."""
    dealer_slug: str
    dealer_cdp: str
    dealer_name: str | None
    dealer_province: str
    dealer_muni: str | None
    vehicle: Vehicle


# The bulk statements — ONE round-trip per table per dealer-window (unnest-based multi-row upsert),
# byte-for-byte the same idempotency the row-by-row path uses. A re-run adds 0 rows and 0 events.

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


def _parse_dealer_pages(pages: list[str], brand: BrandSpec, dealer_slug: str, province_slug: str,
                        geo: GeoResolver, seen_ids: set, harvested_cageable: set,
                        stats: dict) -> list[_CageRow]:
    """Parse + geo-resolve every car across a dealer's fetched pages — pure CPU, no SQL.

    The EXACT per-item gate (cross-page dedup on anuncio_id, geo skip, cageable truth), lifted out
    of the DB loop so the SQL phase is purely set-based. `seen_ids`/`harvested_cageable`/`stats` are
    mutated here with deterministic page-order semantics so the VAM truth is byte-identical
    regardless of batching."""
    rows: list[_CageRow] = []
    for html in pages:
        for d, v in parse_cards(html, brand, dealer_slug, province_slug, geo):
            stats["items_seen"] += 1
            if v.listing_ref and v.listing_ref in seen_ids:
                stats["dup_ids_collapsed"] += 1
                continue
            if v.listing_ref:
                seen_ids.add(v.listing_ref)

            # Brand sanity: skip a card whose make is not this brand (cross-brand stock bleed on a
            # shared backend would otherwise mis-attribute a car to the wrong platform).
            if v.make and brand.make_label.lower() not in v.make.lower():
                stats["wrong_brand_skipped"] += 1
                continue

            prov = d.province_code
            if not prov or not (prov.isdigit() and "01" <= prov <= "52"):
                stats["geo_skipped"] += 1
                continue
            muni = geo.municipality_code(prov, d.city)
            dealer_cdp = cdp_code_dealer(d, muni)

            harvested_cageable.add((d.dealer_slug, v.deep_link))
            if v.vin:
                stats["vins_captured"] += 1
            rows.append(_CageRow(dealer_slug=d.dealer_slug, dealer_cdp=dealer_cdp,
                                 dealer_name=d.name, dealer_province=prov, dealer_muni=muni,
                                 vehicle=v))
    return rows


async def _ingest_dealer(conn: asyncpg.Connection, geo: GeoResolver, brand: BrandSpec,
                         platform_ulid: str, dealer_slug: str, province_slug: str,
                         pages: list[str], seen_ids: set, harvested_cageable: set,
                         stats: dict) -> None:
    """BULK-ingest a whole dealer's fetched pages in ONE transaction with set-based SQL.

    Mirrors spoticar_wholesale._ingest_window EXACTLY: ONE round-trip per table per dealer (unnest
    multi-row upserts). The delta/VAM/platform_listing semantics are preserved: same ON CONFLICT
    idempotency, same cageable truth, same NEW-event rule (emitted only for genuinely new
    vehicles). A re-run of an already-harvested dealer adds 0 rows and 0 events."""
    cage = _parse_dealer_pages(pages, brand, dealer_slug, province_slug, geo, seen_ids,
                               harvested_cageable, stats)
    if not cage:
        return

    async with conn.transaction():
        # ---- DEALERS: dedup by cdp_code, bulk-upsert, resolve ulids.
        dealers: dict[str, _CageRow] = {}
        for r in cage:
            dealers.setdefault(r.dealer_cdp, r)
        d_ulids = [ulid() for _ in dealers]
        d_cdps = list(dealers.keys())
        d_names = [dealers[c].dealer_name for c in d_cdps]
        d_provs = [dealers[c].dealer_province for c in d_cdps]
        d_munis = [dealers[c].dealer_muni for c in d_cdps]
        d_refs = [dealers[c].dealer_slug for c in d_cdps]
        await conn.execute(_BULK_UPSERT_DEALERS, d_ulids, d_cdps, d_names, d_provs,
                           d_munis, d_refs, brand.source_key)
        await conn.execute(_BULK_UPSERT_DEALER_SOURCES, d_cdps, d_refs, brand.source_key)
        cdp_to_ulid: dict[str, str] = {
            row["cdp_code"]: row["entity_ulid"]
            for row in await conn.fetch(
                "SELECT cdp_code, entity_ulid FROM entity WHERE cdp_code = ANY($1::text[])", d_cdps)
        }

        # ---- attach resolved dealer_ulid; dedup cars by (dealer_ulid, deep_link).
        cars: dict[tuple[str, str], _CageRow] = {}
        for r in cage:
            du = cdp_to_ulid.get(r.dealer_cdp)
            if du is None:
                continue
            key = (du, r.vehicle.deep_link)
            if key not in cars:
                cars[key] = r

        # ---- VEHICLES: one SELECT splits existing vs new.
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

        # ---- EDGES: one batched upsert; RETURNING (xmax=0) counts genuinely new edges.
        e_vehicles = [vehicle_ulid_for[k] for k in car_keys]
        e_urls = [cars[k].vehicle.deep_link for k in car_keys]
        e_refs = [cars[k].vehicle.listing_ref for k in car_keys]
        e_prices = [cars[k].vehicle.price for k in car_keys]
        edge_rows = await conn.fetch(_BULK_UPSERT_EDGES, e_vehicles, e_urls, e_refs,
                                     e_prices, platform_ulid)
        stats["edges_created"] += sum(1 for row in edge_rows if row["inserted"])

        # ---- NEW delta events — only for genuinely new vehicles. VIN preserved in payload.
        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for k in confirmed_new:
                v = cars[k].vehicle
                payload = {"price": v.price, "title": v.title, "platform": brand.trade_name}
                if v.vin:
                    payload["vin"] = v.vin
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[k])
                ev_entities.append(k[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities, ev_payloads)
            stats["new_events"] += len(confirmed_new)


async def _walk_dealer(conn, geo, brand, platform_ulid, fetcher, governed_fetch, province_slug,
                       dealer_slug, concurrency, seen_ids, harvested_cageable, stats,
                       page_budget: int | None) -> tuple[str | None, int | None]:
    """Walk ONE dealer: fetch page 1 (read id_total_resultados), then the remaining pages in
    concurrent windows up to ceil(total/12), ingest in page order. Returns (fetch_error, http) so
    the caller's breaker sees a real throttle. Bounded by id_total_resultados (NOT emptiness — the
    listing clamps+repeats past the end)."""
    dealer_path = f"/concesionarios/{province_slug}/{dealer_slug}"
    try:
        first = await fetcher.fetch_text_async(governed_fetch, _list_url(brand, dealer_path, 1), page=1)
    except Exception as e:  # noqa: BLE001 — surface the throttle to the breaker
        return (str(e), fetcher.last_status)

    total = _dealer_total(first)
    if total is None or total <= 0:
        # no count rendered (or genuinely empty dealer) — ingest page 1 anyway (defensive) and stop.
        await _ingest_dealer(conn, geo, brand, platform_ulid, dealer_slug, province_slug, [first],
                             seen_ids, harvested_cageable, stats)
        stats["pages_fetched"] += 1
        stats["dealers_walked"] += 1
        return (None, None)

    stats["declared_full"] += total
    last_page = min(MAX_DEALER_PAGES, math.ceil(total / PAGE_SIZE))
    if page_budget is not None:
        last_page = min(last_page, max(1, page_budget))

    # ingest page 1 first (already fetched), then windows of 2..last_page.
    await _ingest_dealer(conn, geo, brand, platform_ulid, dealer_slug, province_slug, [first],
                         seen_ids, harvested_cageable, stats)
    stats["pages_fetched"] += 1

    next_page = 2
    fetch_error = None
    last_http = None
    while next_page <= last_page and fetch_error is None:
        window = list(range(next_page, min(next_page + concurrency, last_page + 1)))
        next_page = window[-1] + 1
        results = await asyncio.gather(
            *(fetcher.fetch_text_async(governed_fetch, _list_url(brand, dealer_path, p), page=p)
              for p in window),
            return_exceptions=True)
        good_pages = []
        for p, data in zip(window, results):
            if isinstance(data, Exception):
                fetch_error = str(data)
                last_http = fetcher.last_status
                break
            good_pages.append(data)
        if good_pages:
            await _ingest_dealer(conn, geo, brand, platform_ulid, dealer_slug, province_slug,
                                 good_pages, seen_ids, harvested_cageable, stats)
            stats["pages_fetched"] += len(good_pages)
    stats["dealers_walked"] += 1
    return (fetch_error, last_http)


async def harvest_brand(conn: asyncpg.Connection, geo: GeoResolver, brand: BrandSpec,
                        fetcher: MotorflashFetcher, governed_fetch, max_dealers: int | None,
                        concurrency: int, limit: int | None) -> dict:
    """Harvest one brand end to end: ensure platform, pull roster, walk each dealer, VAM + health."""
    stats = {
        "brand": brand.key, "pages_fetched": 0, "items_seen": 0, "dealers_walked": 0,
        "no_dealer_skipped": 0, "geo_skipped": 0, "wrong_brand_skipped": 0, "new_dealers": 0,
        "cars_caged": 0, "new_cars": 0, "edges_created": 0, "new_events": 0, "vins_captured": 0,
        "declared_full": 0, "dup_ids_collapsed": 0, "dealers_distinct": 0, "private_skipped": 0,
        "roster_size": 0, "concurrency": concurrency,
    }
    harvested_cageable: set[tuple[str, str]] = set()
    seen_ids: set[str] = set()

    platform_ulid = await ensure_platform_entity(conn, brand)
    platform_code = platform_cdp_code(brand)
    print(f"[oem_bmw_mini:{brand.key}] platform entity ready: {platform_code} (ulid={platform_ulid}) "
          f"kind={KIND} group={SOURCE_GROUP} tier={DEFENSE_TIER} family={FAMILY}")

    roster = await fetch_roster(fetcher, brand)
    stats["roster_size"] = len(roster)
    if max_dealers is not None and max_dealers > 0:
        roster = roster[:max_dealers]
    # --limit -> a per-dealer page budget (cars / 12 / dealers, at least 1 page each).
    page_budget = None
    if limit is not None and limit > 0 and roster:
        page_budget = max(1, math.ceil(limit / PAGE_SIZE / len(roster)))
    print(f"[oem_bmw_mini:{brand.key}] roster: {stats['roster_size']} dealers "
          f"(walking {len(roster)}); host={host_of(brand.base + '/')}; STEALTH bucket; "
          f"window={concurrency} pages/dealer; page_budget={page_budget or 'full'}")

    dealers_before = {r["cdp_code"] for r in await conn.fetch(
        "SELECT cdp_code FROM entity WHERE kind='compraventa'")}

    fetch_error: str | None = None
    last_http: int | None = None
    for province_slug, dealer_slug in roster:
        err, http = await _walk_dealer(
            conn, geo, brand, platform_ulid, fetcher, governed_fetch, province_slug, dealer_slug,
            concurrency, seen_ids, harvested_cageable, stats, page_budget)
        if err:
            fetch_error, last_http = err, http
            print(f"[oem_bmw_mini:{brand.key}] dealer {province_slug}/{dealer_slug} fetch failed "
                  f"({err}); continuing roster (per-dealer failure is isolated).")
        else:
            print(f"[oem_bmw_mini:{brand.key}] {province_slug}/{dealer_slug}: "
                  f"caged_total={stats['cars_caged']} new={stats['new_cars']} "
                  f"edges={stats['edges_created']} vins={stats['vins_captured']} "
                  f"dealers_seen={len({s for s, _ in harvested_cageable})}")

    dealers_after = {r["cdp_code"] for r in await conn.fetch(
        "SELECT cdp_code FROM entity WHERE kind='compraventa'")}
    stats["new_dealers"] = len(dealers_after - dealers_before)
    stats["dealers_distinct"] = await conn.fetchval(
        """SELECT count(DISTINCT v.entity_ulid) FROM platform_listing pl
           JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
           WHERE pl.platform_entity_ulid = $1""", platform_ulid)

    recipe = _platform_recipe(brand)
    recipe_path = write_recipe(platform_code, recipe)
    print(f"[oem_bmw_mini:{brand.key}] recipe written: {recipe_path}")

    # VAM count quorum for the slice — THREE orthogonal like-with-like paths.
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
    stats.update(verdict=verdict, db_edges=db_edges, db_join_vehicles=db_join_vehicles,
                 harvested_cageable=harvested_cageable_n, harvested_distinct_ids=len(seen_ids),
                 platform_code=platform_code, platform_ulid=platform_ulid,
                 recipe_path=str(recipe_path),
                 dealers_attributed_in_run=len({s for s, _ in harvested_cageable}))

    run_ok = fetch_error is None and stats["pages_fetched"] > 0 and verdict != "REFUTED"
    run_error = fetch_error or (None if run_ok else f"VAM verdict {verdict}")
    outcome = await record_run(conn, brand.source_key, ok=run_ok, rows=stats["cars_caged"],
                               error=run_error, http_status=last_http)
    stats["health_status"] = outcome.status
    stats["breaker_state"] = outcome.breaker_state
    if not run_ok:
        stats["repair_action"] = await auto_repair(
            conn, brand.source_key, run_error or "harvest failed", phase="scrape",
            http_status=last_http)
    return stats


async def harvest(brands: list[str], max_dealers: int | None = None,
                  concurrency: int = DEFAULT_CONCURRENCY, limit: int | None = None) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    out: dict = {"brands": {}}
    try:
        geo = await GeoResolver.load(conn)
        gov = governor()
        for bkey in brands:
            brand = BRANDS[bkey]
            if await is_open(conn, brand.source_key):
                print(f"[oem_bmw_mini:{brand.key}] breaker OPEN for {brand.source_key}; skipping "
                      f"drain (graceful degradation).")
                out["brands"][bkey] = {"skipped": True, "reason": "breaker_open",
                                       "source_key": brand.source_key}
                continue
            fetcher = MotorflashFetcher(pool_size=concurrency)
            governed_fetch = gov.wrap_fetch_text(fetcher.fetch_text)
            out["brands"][bkey] = await harvest_brand(
                conn, geo, brand, fetcher, governed_fetch, max_dealers, concurrency, limit)
        return out
    finally:
        await conn.close()


def _print_report(out: dict) -> None:
    for bkey, stats in out.get("brands", {}).items():
        if stats.get("skipped"):
            print(f"\n[oem_bmw_mini:{bkey}] SKIPPED: {stats.get('reason')}")
            continue
        print("\n" + "=" * 64)
        print(f"OEM-VO PORTAL WHOLESALE HARVEST — {bkey.upper()} — REPORT")
        print("=" * 64)
        print(f"  platform cdp_code     : {stats.get('platform_code')}")
        print(f"  group / kind          : oem_vo_portal / oem_vo_portal (tier t1_soft, family bmw_group_vo)")
        print(f"  declared full (Σtotal): {stats.get('declared_full')}")
        print(f"  roster size           : {stats.get('roster_size')} dealers")
        print(f"  dealers walked        : {stats.get('dealers_walked')}")
        print(f"  concurrency (window)  : {stats.get('concurrency')} pages/dealer")
        print(f"  pages fetched         : {stats['pages_fetched']}")
        print(f"  items seen            : {stats['items_seen']}")
        print(f"  wrong-brand skipped   : {stats['wrong_brand_skipped']}")
        print(f"  private skipped       : {stats['private_skipped']} (OEM portal — none expected)")
        print(f"  dup ids collapsed     : {stats.get('dup_ids_collapsed')} (anuncio_id dedup)")
        print(f"  geo skipped (bad geo) : {stats['geo_skipped']}")
        print(f"  dealers attributed    : {stats['dealers_distinct']} distinct "
              f"({stats['new_dealers']} new this run)")
        print(f"  cars caged            : {stats['cars_caged']} ({stats['new_cars']} new)")
        print(f"  platform_listing edges: {stats['edges_created']} created "
              f"(db total = {stats.get('db_edges')})")
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="BMW Premium Selection + MINI Next OEM-VO portal wholesale harvester "
                    "(Motorflash dealer-listing-card drain)")
    parser.add_argument("--brand", choices=["bmw", "mini", "both"], default="both",
                        help="which brand portal to harvest (default both).")
    parser.add_argument("--dealers", type=int, default=None,
                        help="optional cap on dealers walked per brand (proof slice). Default: full roster.")
    parser.add_argument("--limit", type=int, default=None,
                        help="optional target car count; converted to a per-dealer page budget.")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help=(f"pages fetched in parallel per dealer; default {DEFAULT_CONCURRENCY}. "
                              f"Both hosts inherit the conservative STEALTH rate class — the "
                              f"governor's per-host bucket is the real limiter."))
    args = parser.parse_args()
    brands = ["bmw", "mini"] if args.brand == "both" else [args.brand]
    out = asyncio.run(harvest(brands, args.dealers, args.concurrency, args.limit))
    _print_report(out)


if __name__ == "__main__":
    main()
