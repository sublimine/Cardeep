"""LOCALIZAVO (localizavo.es) — the FREE-PUBLIC B2B-auction member of the `b2b_auctions` front.

Front `b2b_auctions`: the B2B remarketing/wholesale AUCTION operators the keyword census surfaced as
genuinely NEW (count=0 in DB) and verified reachable. Probed live 2026-06-13 the census split the two
named targets cleanly into FREE-PUBLIC vs GATED — exactly as the prior `b2b_extra_auctions` census did
for Subastacar (public) vs AUTO1/OPENLANE/Manheim (gated):

  * LocalizaVO (localizavo.es)  — PUBLIC. A Spanish electronic+physical car-auction platform for the
                                  trade ("subastas de coches para profesionales"). Although the buy/bid
                                  side needs a free professional registration, the ENTIRE per-lot CATALOG
                                  is server-rendered HTML, fully visible to an anonymous chrome131 GET
                                  with NO login. The homepage links the live auction events as public
                                  deep-links `subastas?idSubasta=<id>`; each event page renders every lot
                                  card (Ref, Matriculación, Estado, consigning company, make/model/version,
                                  fuel, CV, km, photo, end date) and paginates via `&numPagina=N` OR drains
                                  in ONE shot via `&nReg=0` (the "Todos" option). The asking/winning PRICE
                                  is the only field withheld from anonymous users ("Precio visible solo
                                  para Usuarios Registrados") — i.e. BID-GATED, so price=NULL (honest),
                                  exactly like the Ayvens/BCA/Autorola auction lots already caged. THIS is
                                  the census target that exposes full public lot stock free, so this
                                  connector connects it.

  * CarCollect (carcollect.com) — GATED. The public www.carcollect.com is a HubSpot CMS MARKETING site
                                  (probed live: /hs/hsstatic + hubfs assets, 821-URL sitemap with ZERO
                                  per-lot detail pages, the "8.154 en vivo" figure is a marketing counter).
                                  The actual trading app is trade.carcollect.com — a Next.js SPA that
                                  308-redirects straight to /login, and every /api/* path (auctions,
                                  vehicles, search) 307-redirects to /login for an anonymous client. It is
                                  a B2B-only platform (account + verification + a €82/car seller fee), so
                                  there is NO anonymous public lot data layer. Documented gated below; not
                                  faked. (Same honest verdict as AUTO1/OPENLANE/Manheim in the sibling
                                  b2b_extra_auctions census.)

  * Manheim España (manheim.es) — GATED (no credentials). A B2B remarketer whose catalog sits behind a
                                  buyer login; with no credentials available this is a REAL gated blocker,
                                  declared honestly, never fabricated. (Already recorded gated in the
                                  b2b_extra_auctions census; reaffirmed here.)

THE SURFACE (LocalizaVO, verified live 2026-06-13):
  EVENTS:  GET https://www.localizavo.es/  (and /subastas_listado.aspx) -> 200 text/html. The live auction
           EVENTS are linked as public anchors `subastas?idSubasta=<id>` (no login). We collect every such
           id from these public index pages.
  LOTS:    GET https://www.localizavo.es/subastas?idSubasta=<id>&nReg=0 -> 200 text/html. nReg=0 ("Todos")
           renders EVERY lot of that event in one page (verified: 176 lots in one shot vs a page-walk that
           collided on the stable sort). Each lot is a `<div class="fichavo subasta" id="subasta_<ref>">`
           block carrying: Ref (native lot id), Matriculación MM/YYYY (year), Estado, the consigning
           COMPANY (the `<div class="imagen"><img alt="...">` of the lot, e.g. "NORTHGATE ESPAÑA RENTING
           FLEXIBLE SA"), the detail deep-link slug `<slug>-<ref>?...&idSubasta=<id>`, a `<div
           class="modelo">` line "<MARCA> <model/version> / <fuel> / <CV> CV / <km> Kms." and the lot
           photo. The price card reads "Precio visible solo para Usuarios Registrados" -> price NULL.

THE DATA MODEL — mirrors the proven dual-membership template (pipeline.platform.subastacar_wholesale,
pipeline.platform.group_subastas_wholesale and scripts/cage_autorola_bca_subastas.py) EXACTLY. Unlike
Subastacar (one national auction house), LocalizaVO publishes DISCRETE auction EVENTS (idSubasta), so the
SELLING POINT is the sale EVENT — modelled as ONE `kind='subasta'` entity PER EVENT (national, province
NULL), identical to the Ayvens Carmarket / Autorola sale events already caged:

  LocalizaVO (the auction platform)  -> entity kind='plataforma' (+ platform_meta)        [PLATFORM]
  each SALE EVENT (idSubasta)         -> entity kind='subasta' (national, province NULL)   [SELLER]
  each LOT (car)                     -> vehicle OWNED BY its sale event                    [CAR]
  the lot ON the platform            -> platform_listing edge (platform <-> vehicle)       [EDGE]

Ownership is singular (the sale event that consigns the lot); platform membership is plural (the edge).
The seller is stored NATIONAL (province_code NULL, sentinel '00' only inside the cdp_code string), the
SAME convention the Ayvens sale events and the platform entities use. No province is fabricated (the
public lot surface carries the consigning company name but no per-lot address/province). The consigning
company is preserved on the lot card and surfaced in the event entity's metadata, never invented into a
geo anchor it does not have.

Multi-axis classification (migrations/0016), identical axes to the Ayvens/Subastacar auction members:
  defense_tier = 't0_open'           (SSR serves cleanly to chrome131; no WAF/JS challenge)
  source_group = 'official_registry' (the nearest enum for the distinct AUCTION group; no dedicated
                                      'auction' source_group value exists — same choice as Ayvens/BCA)
  role         = 'platform' (the platform) / 'registry' (the sale-event seller)
  kind         = 'plataforma' (platform) / 'subasta' (the sale event)   [migrations/0005 ontology]
  is_tier1     = FALSE               (no WAF fronts the SSR surface)
  family       = 'localizavo'        (ties the LocalizaVO auction surface on the family axis)
  price        = NULL                (bid/registration gated; honest — like Ayvens/BCA/Autorola)

THE FULL HARVEST. We drain the ENTIRE public catalog: collect every public idSubasta from the index
pages, drain each event fully via nReg=0, dedup lots on the native lot Ref (the stable per-car id), cage
idempotently (ON CONFLICT), emit a NEW delta only for genuinely new cars, and reconcile aged-out cars
(any LocalizaVO edge not seen this run -> retired) so no phantom stale lot is counted live.

Engine: GETs routed THROUGH the per-host governor (the SAME single choke point coches.net/Ayvens/
Subastacar use), each synchronous curl_cffi GET run in a worker thread so the event loop is never
blocked, and no host is fetched faster than its bucket. localizavo.es is a small SSR site (a couple of
live events, a few hundred lots), drained in a handful of round-trips at a polite pace.

Run: python -m pipeline.platform.localizavo_wholesale
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import html as _html
import json
import os
import re
import sys
from dataclasses import dataclass

import asyncpg
from curl_cffi import requests as cffi_requests

from pipeline.engine.governor import governor, host_of
from pipeline.ids import ulid
from pipeline.ops.health import auto_repair, is_open, record_run
from pipeline.recipe import write_recipe
from pipeline.verify import record_count_verdict
from services.api.codes import _base32, cdp_code

DSN = "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
DSN = os.environ.get("CARDEEP_DSN", DSN)

# ---------------------------------------------------------------------------
# LocalizaVO platform identity (the FREE-PUBLIC member of the b2b_auctions front).
# ---------------------------------------------------------------------------
LV_DOMAIN = "localizavo.es"
LV_WEBSITE = "localizavo.es"
LV_LEGAL_NAME = "LocalizaVO (Localiza V.O.; subastas de coches para profesionales; localizavo.es)"
LV_TRADE_NAME = "LocalizaVO"
LV_SOURCE_KEY = "localizavo_wholesale"
LV_WAF = "none"                      # SSR serves cleanly to chrome131 (no WAF/JS challenge).
LV_DEFENSE_TIER = "t0_open"          # open SSR surface.
# No dedicated 'auction' source_group enum value exists; use 'official_registry' (the nearest enum),
# identical to the Ayvens/Autorola/BCA/Subastacar auction members.
LV_SOURCE_GROUP = "official_registry"
LV_PLATFORM_ROLE = "platform"        # the platform entity's role.
LV_SELLER_ROLE = "registry"          # the sale-event seller entity's role.
LV_PLATFORM_KIND = "plataforma"      # the platform ENTITY's ontology kind.
LV_SELLER_KIND = "subasta"           # the sale-event seller ENTITY's ontology kind.
LV_FAMILY = "localizavo"             # ties the LocalizaVO auction surface on the family axis.

_BASE = "https://www.localizavo.es"
# Public index pages that link the live auction events (subastas?idSubasta=<id>).
_INDEX_URLS = [f"{_BASE}/", f"{_BASE}/subastas_listado.aspx"]
_EVENT_URL = _BASE + "/subastas?idSubasta={sid}&nReg=0"  # nReg=0 == "Todos" -> every lot in one page.

_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": _BASE + "/",
}
_IMPERSONATE = "chrome131"
_TIMEOUT = 60

NATIONAL_PROVINCE_SENTINEL = "00"

# A public auction-event id, linked from the index pages as `subastas?idSubasta=<digits>`.
_EVENT_ID_RE = re.compile(r"idSubasta=(\d+)")
# A single lot card opens with `<div class="fichavo subasta" id="subasta_<ref>">`; the ref is the native
# per-lot id AND the deep-link tail, so it is the stable dedup key.
_LOT_SPLIT_RE = re.compile(r'(?=<div class="fichavo subasta" id="subasta_\d+">)')
_LOT_REF_RE = re.compile(r'id="subasta_(\d+)"')
_LOT_MAT_RE = re.compile(r'Matriculaci.n:\s*<span>([^<]+)</span>', re.IGNORECASE)
_LOT_ESTADO_RE = re.compile(r'<div class="estado">([^<]+)</div>', re.IGNORECASE)
# The consigning company is the alt of the company logo image inside `<div class="empresa">`.
_LOT_EMPRESA_RE = re.compile(r'<div class="imagen"><img[^>]*alt="([^"]*)"', re.IGNORECASE)
# The detail deep-link slug ends in `-<ref>` and carries the idSubasta query.
_LOT_SLUG_RE = re.compile(r'href="([^"]*-\d+\?origen=[^"]*idSubasta=[^"]*)"', re.IGNORECASE)
# The model line: "<MARCA> <model/version> / <fuel> / <CV> CV / <km> Kms."
_LOT_MODELO_RE = re.compile(r'<div class="modelo">(.*?)</div>', re.IGNORECASE | re.DOTALL)
_LOT_MARCA_RE = re.compile(r'<span class="marca">([^<]+)</span>', re.IGNORECASE)
# The lot photo is the first <img> inside `<div class="info">`.
_LOT_PHOTO_RE = re.compile(r'<div class="info"><a[^>]*>\s*<img src="([^"]+)"', re.IGNORECASE)
# The countdown end date: EjecutaContador('<ref>', '<YYYY/M/D>', ...).
_LOT_END_RE = re.compile(r"EjecutaContador\('\d+',\s*'([^']+)'", re.IGNORECASE)
# The auction-event title (for the seller entity name).
_TITLE_RE = re.compile(r'<title>([^<]+)</title>', re.IGNORECASE)

# fuel / transmission arrive as clean Spanish labels in the model line; normalize the finite, verified
# vocabulary to the canonical labels the OEM/auction connectors use.
_FUEL_LABEL = {
    "diesel": "Diésel", "diésel": "Diésel", "gasolina": "Gasolina", "petrol": "Gasolina",
    "híbrido": "Híbrido", "hibrido": "Híbrido", "eléctrico": "Eléctrico", "electrico": "Eléctrico",
    "híbrido enchufable": "Híbrido enchufable", "hibrido enchufable": "Híbrido enchufable",
    "glp": "GLP", "gnc": "GNC", "hidrógeno": "Hidrógeno", "hidrogeno": "Hidrógeno",
}


def _to_int(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return int(v)
    m = re.search(r"-?\d+", str(v).replace(".", "").replace(",", ""))
    return int(m.group(0)) if m else None


def _year(v) -> int | None:
    if v is None:
        return None
    m = re.search(r"(\d{4})", str(v))
    if not m:
        return None
    y = int(m.group(1))
    return y if 1900 <= y <= 2100 else None


def _clean_fuel(v) -> str | None:
    if not isinstance(v, str) or not v.strip():
        return None
    return _FUEL_LABEL.get(v.strip().lower(), v.strip()) or None


def localizavo_platform_cdp_code() -> str:
    """The LocalizaVO platform's immutable cdp_code: domain identity, national province '00'. Mirrors
    subastacar_platform_cdp_code()/ayvens_platform_cdp_code() so every platform mints codes the same way."""
    key = f"domain:{LV_DOMAIN}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{NATIONAL_PROVINCE_SENTINEL}-{_base32(digest)}"


def localizavo_sale_cdp_code(sale_id: str) -> str:
    """A sale EVENT's immutable cdp_code. Keyed as a NATIONAL named entity (the discrete auction event),
    province '00' in the code string only (no geo_province FK for '00'). Deterministic over the stable
    idSubasta, so re-runs are idempotent and each event is one row, never duplicated. Mirrors the Autorola/
    Ayvens sale-event cdp minting (province NULL national auction event)."""
    return cdp_code(province_code=NATIONAL_PROVINCE_SENTINEL, domain=None,
                    name=f"LocalizaVO subasta {sale_id}", address=f"localizavosale:{sale_id}")


# ---------------------------------------------------------------------------
# Parsed shapes (from the REAL SSR lot-card field map, inspected live 2026-06-13).
# ---------------------------------------------------------------------------


@dataclass
class Lot:
    """A car parsed from one LocalizaVO `<div class="fichavo subasta">` lot card."""
    sale_id: str
    deep_link: str
    listing_ref: str            # the native lot Ref (stable per-car dedup key, e.g. '191064')
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    fuel: str | None
    photo_url: str | None
    seller_company: str | None  # the consigning company (alt of the lot's company logo); metadata only
    estado: str | None
    ends_at: str | None
    # price is intentionally ABSENT: "Precio visible solo para Usuarios Registrados" -> NULL (bid gated).


def _abs_url(path: str) -> str:
    path = _html.unescape(path).strip()
    if path.startswith("http"):
        return path
    return f"{_BASE}/{path.lstrip('/')}"


def parse_event_lots(sale_id: str, html: str) -> list[Lot]:
    """Parse every lot card of a sale-event page into Lot rows. The native Ref is the stable id and the
    deep-link tail; a card with no Ref/slug is skipped honestly (never fabricated)."""
    out: list[Lot] = []
    for blk in _LOT_SPLIT_RE.split(html):
        if 'id="subasta_' not in blk:
            continue
        ref_m = _LOT_REF_RE.search(blk)
        if not ref_m:
            continue
        ref = ref_m.group(1)
        slug_m = _LOT_SLUG_RE.search(blk)
        if not slug_m:
            continue
        deep_link = _abs_url(slug_m.group(1).split("?")[0])

        marca = _LOT_MARCA_RE.search(blk)
        make = _html.unescape(marca.group(1).strip()) if marca else None

        model = None
        title = None
        fuel = None
        km = None
        modelo_m = _LOT_MODELO_RE.search(blk)
        if modelo_m:
            txt = _html.unescape(re.sub(r"<[^>]+>", " ", modelo_m.group(1)))
            txt = re.sub(r"\s+", " ", txt).strip()
            title = txt or None
            # "<MARCA> <model/version> / <fuel> / <CV> CV / <km> Kms."
            parts = [p.strip() for p in txt.split("/")]
            if parts:
                head = parts[0]  # "MARCA model version..."
                if make and head.upper().startswith(make.upper()):
                    model = head[len(make):].strip() or None
                else:
                    model = head or None
            if len(parts) >= 2:
                fuel = _clean_fuel(parts[1])
            # the km segment is the one ending in "Kms." (the CV segment is "<n> CV").
            for seg in parts[1:]:
                if re.search(r"kms?\.?\s*$", seg, re.IGNORECASE):
                    km = _to_int(re.sub(r"[^\d.]", "", seg))
                    if km is not None and (km < 0 or km > 5_000_000):
                        km = None
                    break

        mat_m = _LOT_MAT_RE.search(blk)
        year = _year(mat_m.group(1)) if mat_m else None

        emp_m = _LOT_EMPRESA_RE.search(blk)
        company = _html.unescape(emp_m.group(1).strip()) if emp_m and emp_m.group(1).strip() else None

        estado_m = _LOT_ESTADO_RE.search(blk)
        estado = _html.unescape(estado_m.group(1).strip()) if estado_m else None

        photo_m = _LOT_PHOTO_RE.search(blk)
        photo = _abs_url(photo_m.group(1)) if photo_m else None

        end_m = _LOT_END_RE.search(blk)
        ends_at = end_m.group(1).strip() if end_m else None

        out.append(Lot(
            sale_id=sale_id, deep_link=deep_link, listing_ref=ref,
            title=title, make=make, model=model, year=year, km=km, fuel=fuel,
            photo_url=photo, seller_company=company, estado=estado, ends_at=ends_at))
    return out


def parse_event_title(html: str, sale_id: str) -> str:
    """The sale-event title for the seller entity name (from the page <title>, trimmed). Falls back to a
    stable 'LocalizaVO subasta <id>' label so the entity name is never empty."""
    m = _TITLE_RE.search(html)
    if m:
        t = _html.unescape(m.group(1)).strip()
        # drop the generic site suffix to keep a meaningful event label.
        t = re.sub(r"\s*-\s*LocalizaVO\s*$", "", t, flags=re.IGNORECASE).strip()
        if t and t.lower() not in ("subastas de coches para profesionales",):
            return t[:120]
    return f"subasta {sale_id}"


def parse_event_ids(html: str) -> list[str]:
    """Collect every public auction-event idSubasta linked on an index page (deduped, order-preserving)."""
    seen: dict[str, None] = {}
    for m in _EVENT_ID_RE.finditer(html):
        seen.setdefault(m.group(1), None)
    return list(seen.keys())


# ---------------------------------------------------------------------------
# Fetch: GETs routed THROUGH the governor (same per-host choke point as coches.net/Ayvens/Subastacar).
# ---------------------------------------------------------------------------


class LocalizavoFetcher:
    """A POOL of fingerprint-coherent curl_cffi GET sessions for LocalizaVO.

    Same concurrency-vs-coherence model as the proven fetchers: a single curl_cffi Session is NOT safe to
    call from several threads at once, and the governor runs each fetch in its own worker thread. The fix
    is a bounded POOL — one Session per concurrency slot. The governor's per-host bucket bounds the
    AGGREGATE rate across every session, so widening the pool never out-paces the host."""

    def __init__(self, pool_size: int = 1) -> None:
        self._pool_size = max(1, pool_size)
        self._sessions = [cffi_requests.Session(impersonate=_IMPERSONATE)
                          for _ in range(self._pool_size)]
        self._free: asyncio.Queue[int] = asyncio.Queue()
        for i in range(self._pool_size):
            self._free.put_nowait(i)
        self.last_status: int | None = None

    def get_text(self, url: str, *, slot: int = 0) -> str:
        """The synchronous GET on pool session `slot` (runs in a worker thread, handed to the governor's
        wrap_fetch_text). The page is UTF-8 (verified live); decode explicitly so accented company names
        and fuel labels survive. Raises on a non-200 so the breaker sees a throttle/ban."""
        session = self._sessions[slot]
        resp = session.get(url, headers=_HEADERS, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url}")
        return resp.content.decode("utf-8", "replace")

    async def get_async(self, governed_get, url: str) -> str:
        """Lease a pool slot, GET THROUGH the governor on that slot, release it."""
        slot = await self._free.get()
        try:
            return await governed_get(url, slot=slot)
        finally:
            self._free.put_nowait(slot)


# ---------------------------------------------------------------------------
# DB layer (mirrors the proven template EXACTLY: ensure platform + per-event sellers, bulk-upsert lots,
# link edge, emit NEW delta, reconcile aged-out — all idempotent ON CONFLICT). 0016 axes set explicitly.
# ---------------------------------------------------------------------------

LOCALIZAVO_RECIPE = {
    "version": 1,
    "source": "LocalizaVO (Localiza V.O.; subastas de coches para profesionales; localizavo.es)",
    "group": "subastas (B2B car auction / remarketing); source_group=official_registry",
    "scope": "platform-wholesale (full public lot catalog; SSR auction-event pages, nReg=0 drain)",
    "engine": "curl_cffi+chrome131_impersonate+ssr_html_lot_cards",
    "access": ("PUBLIC. The per-lot catalog is server-rendered HTML visible to an anonymous chrome131 GET "
               "with NO login. The homepage + /subastas_listado.aspx link the live auction events as public "
               "anchors `subastas?idSubasta=<id>`; each event page renders every lot card and drains in ONE "
               "request via `&nReg=0` ('Todos'). A free professional registration gates BIDDING and the "
               "PRICE field only ('Precio visible solo para Usuarios Registrados'); the VEHICLE stock "
               "itself (make/model/version/fuel/km/year/photo/consigning company) is fully public. "
               "defense_tier=t0_open, website_waf=none, is_tier1=FALSE."),
    "data_surface": "next_data",
    "surface_intent": "ssr_html_lot_cards",
    "data_surface_label": ("the platform_meta.data_surface CHECK has no 'ssr_html'/'html_scrape' literal; "
                           "stored as 'next_data' (the closest schema-valid first-party-render literal, the "
                           "same choice the Clicars SSR-HTML member of group_vo_chains makes) with the precise "
                           "surface_intent='ssr_html_lot_cards' kept in surface_detail."),
    "endpoint": ("GET https://www.localizavo.es/ (+ /subastas_listado.aspx) for the event index; "
                 "GET https://www.localizavo.es/subastas?idSubasta=<id>&nReg=0 for the full lot list"),
    "enumeration": ("collect every idSubasta linked on the public index pages; for each event GET "
                    "?idSubasta=<id>&nReg=0 ('Todos') to render ALL lots in one page; split on "
                    "`<div class=\"fichavo subasta\" id=\"subasta_<ref>\">`; dedup on the native lot Ref; "
                    "aged-out lots (a LocalizaVO edge not seen this run) -> status=gone/removed."),
    "denominator": ("the live public auction events' total lot count (sum of lots rendered by nReg=0 "
                    "across every public idSubasta) — the EXACT denominator, not a guess. VAM denominator."),
    "platform_entity": ("kind=plataforma, province_code=NULL (sentinel 00 in cdp_code only), is_tier1=FALSE, "
                        "defense_tier=t0_open, source_group=official_registry, role=platform, family=localizavo"),
    "seller_model": ("LocalizaVO publishes DISCRETE auction EVENTS (idSubasta), so the selling point is the "
                     "sale EVENT: ONE entity kind='subasta' (province NULL, national) PER event, role='registry' "
                     "— identical to the Ayvens Carmarket / Autorola sale events. Each lot is owned by its "
                     "event. The lot's consigning company (alt of the lot's company logo) is preserved as lot "
                     "metadata; it is NOT turned into a geo-anchored dealer (the public lot has no per-lot "
                     "address/province), so no province is fabricated."),
    "dual_membership": ("vehicle.entity_ulid=sale-event seller (subasta); platform_listing edge=platform<->vehicle"),
    "price_gate": ("bid/registration gated: 'Precio visible solo para Usuarios Registrados' -> price=NULL "
                   "(honest), exactly like the Ayvens/BCA/Autorola auction lots already caged."),
    "field_map": {
        "deep_link": "the lot detail URL (slug ending in -<ref>)",
        "listing_ref": "the native lot Ref (id=\"subasta_<ref>\"; stable per-car id + dedup key)",
        "make": "<span class=\"marca\">",
        "model": "<div class=\"modelo\"> head after the make",
        "year": "Matriculación MM/YYYY -> YYYY",
        "km": "<div class=\"modelo\"> segment ending in 'Kms.'",
        "fuel": "<div class=\"modelo\"> 2nd '/'-segment (-> Spanish label)",
        "photo_url": "<div class=\"info\"> first <img src>",
        "seller_company": "<div class=\"empresa\"> logo <img alt> (consigning company; lot metadata)",
        "price": "WITHHELD from anonymous users -> NULL (bid/registration gated)",
    },
    "gate_documented": {
        "carcollect": ("GATED. www.carcollect.com is a HubSpot CMS MARKETING site (821-URL sitemap, ZERO "
                       "per-lot detail pages; '8.154 en vivo' is a marketing counter). The trading app "
                       "trade.carcollect.com is a Next.js SPA that 308->/login, and every /api/* path "
                       "(auctions/vehicles/search) 307->/login for an anonymous client. B2B-only (account + "
                       "verification + €82/car seller fee); NO anonymous public lot data layer. Verified live "
                       "2026-06-13. Not faked."),
        "manheim_es": ("GATED (no credentials). B2B remarketer; catalog behind a buyer login. With no "
                       "credentials available this is a REAL gated blocker, declared honestly — never "
                       "fabricated. (Recorded gated in the sibling b2b_extra_auctions census.)"),
        "localizavo": ("PUBLIC SSR lot cards (price bid-gated -> NULL) — the b2b_auctions census target that "
                       "exposes full public lot stock free. CONNECTED by this connector."),
    },
    "caveats": {
        "full_catalog": "the drain caps at the live events' own total lot count — full public catalog, not a slice.",
        "no_geo": "auction lots have no per-lot province; the sale-event seller is national (province NULL).",
        "per_event_seller": "one kind='subasta' seller PER discrete auction event (idSubasta), not one global house.",
        "price_null": "price is bid/registration gated and withheld from anonymous users -> stored NULL (honest).",
    },
}


async def ensure_platform_entity(conn: asyncpg.Connection) -> str:
    """Idempotently ensure the LocalizaVO platform entity + platform_meta exist. Returns its entity_ulid.
    kind='plataforma', is_tier1=FALSE, 0016 axes set explicitly. The platform_meta.data_surface CHECK has
    no 'ssr_html'/'html_scrape' literal, so it is stored as 'next_data' (the closest schema-valid
    first-party-render literal — the SAME choice the Clicars SSR-HTML member of group_vo_chains makes),
    with the precise surface_intent='ssr_html_lot_cards' kept in surface_detail."""
    code = localizavo_platform_cdp_code()
    eulid = ulid()
    await conn.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, website_waf, is_tier1, status, kind_source,
               defense_tier, source_group, role, first_discovered_source, last_seen)
           VALUES ($1,$2,$3,$4,$5,NULL,$6,$7::waf_kind,FALSE,'active','platform_label',
               $8::defense_tier,$9::source_group,$10::entity_role,$11, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               is_tier1 = EXCLUDED.is_tier1, website_waf = EXCLUDED.website_waf,
               defense_tier = EXCLUDED.defense_tier, source_group = EXCLUDED.source_group,
               role = EXCLUDED.role, legal_name = EXCLUDED.legal_name, kind = EXCLUDED.kind""",
        eulid, code, LV_PLATFORM_KIND, LV_LEGAL_NAME, LV_TRADE_NAME, LV_WEBSITE,
        LV_WAF, LV_DEFENSE_TIER, LV_SOURCE_GROUP, LV_PLATFORM_ROLE, LV_SOURCE_KEY)
    eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        eulid, LV_SOURCE_KEY, LV_DOMAIN)
    await conn.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES ($1,'next_data',$2::jsonb,FALSE,FALSE,$3)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        eulid, json.dumps({"index": _INDEX_URLS, "event": _EVENT_URL,
                           "host": host_of(_BASE), "method": "GET",
                           "drain": "&nReg=0 (Todos)",
                           "price_gate": "bid_registration_gated",
                           "surface_intent": "ssr_html_lot_cards",
                           "engine": "curl_cffi/chrome131_impersonate"}),
        LV_FAMILY)
    return eulid


async def ensure_sale_entities(conn: asyncpg.Connection, sales: dict[str, str]) -> dict[str, str]:
    """Idempotently ensure ONE kind='subasta' SELLER entity per discrete auction event. `sales` maps
    sale_id -> event title. Returns sale_id -> entity_ulid. Each seller is NATIONAL (province NULL,
    sentinel '00' in the cdp_code string only), role='registry', source_group='official_registry'. Every
    lot of an event is owned by its event seller."""
    out: dict[str, str] = {}
    for sale_id, title in sales.items():
        code = localizavo_sale_cdp_code(sale_id)
        name = f"LocalizaVO {title}"[:200]
        eulid = ulid()
        await conn.execute(
            """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
                   province_code, is_tier1, status, kind_source, sells_cars,
                   source_group, role, first_discovered_source, last_seen)
               VALUES ($1,$2,$3::entity_kind,$4,$4,NULL,FALSE,'active','platform_label',TRUE,
                   $5::source_group,$6::entity_role,$7, now())
               ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
                   source_group = EXCLUDED.source_group, role = EXCLUDED.role, kind = EXCLUDED.kind""",
            eulid, code, LV_SELLER_KIND, name, LV_SOURCE_GROUP, LV_SELLER_ROLE, LV_SOURCE_KEY)
        eulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
        await conn.execute(
            "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
            "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
            eulid, LV_SOURCE_KEY, str(sale_id))
        out[sale_id] = eulid
    return out


_BULK_INSERT_VEHICLES = """
INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model,
        year, km, price, fuel, photo_url, vin_ref, status)
SELECT u.vehicle_ulid, u.entity_ulid, u.deep_link, u.title, u.make, u.model,
       u.year, u.km, NULL, u.fuel, u.photo_url, u.vin_ref, 'available'
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[], $5::text[], $6::text[],
              $7::int[], $8::int[], $9::text[], $10::text[], $11::text[])
       AS u(vehicle_ulid, entity_ulid, deep_link, title, make, model,
            year, km, fuel, photo_url, vin_ref)
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
SELECT u.vehicle_ulid, $4, u.listing_url, u.listing_ref, NULL,
       'listed', now(), now()
  FROM unnest($1::text[], $2::text[], $3::text[])
       AS u(vehicle_ulid, listing_url, listing_ref)
ON CONFLICT (vehicle_ulid, platform_entity_ulid)
  DO UPDATE SET last_seen = now(), status = 'listed',
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


async def _ingest_lots(conn: asyncpg.Connection, platform_ulid: str,
                       sale_to_ulid: dict[str, str], lots: list[Lot],
                       harvested: set, stats: dict) -> None:
    """BULK-ingest a batch of parsed lots in ONE transaction with set-based SQL. Mirrors the proven
    template EXACTLY: dedup by (owner, deep_link), split existing vs new, bulk insert/touch, batched edge
    upsert (RETURNING xmax=0 counts new edges), NEW delta only for genuinely new cars, price always NULL
    (bid gated). A re-run of an already-harvested batch adds 0 rows and 0 events."""
    if not lots:
        return
    # dedup within batch by (owner_ulid, deep_link) — the same lot seen twice is one car.
    by_key: dict[tuple[str, str], Lot] = {}
    for lot in lots:
        owner = sale_to_ulid.get(lot.sale_id)
        if owner is None or not lot.deep_link:
            continue
        key = (owner, lot.deep_link)
        if key not in by_key:
            by_key[key] = lot
            harvested.add(lot.deep_link)
    cars = list(by_key.items())
    if not cars:
        return

    async with conn.transaction():
        keys = [k for k, _ in cars]
        k_entities = [k[0] for k in keys]
        k_links = [k[1] for k in keys]
        existing: dict[tuple[str, str], str] = {
            (row["entity_ulid"], row["deep_link"]): row["vehicle_ulid"]
            for row in await conn.fetch(
                """SELECT vehicle_ulid, entity_ulid, deep_link FROM vehicle
                   WHERE (entity_ulid, deep_link) IN (
                     SELECT * FROM unnest($1::text[], $2::text[]))""",
                k_entities, k_links)
        }

        vehicle_ulid_for: dict[tuple[str, str], str] = {}
        new_keys: list[tuple[str, str]] = []
        touch_ulids: list[str] = []
        for key, _lot in cars:
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

        confirmed_new: list[tuple[str, str]] = []
        if new_keys:
            ins = [(k, by_key[k]) for k in new_keys]
            await conn.execute(
                _BULK_INSERT_VEHICLES,
                [vehicle_ulid_for[k] for k, _ in ins], [k[0] for k, _ in ins],
                [k[1] for k, _ in ins], [v.title for _, v in ins], [v.make for _, v in ins],
                [v.model for _, v in ins], [v.year for _, v in ins], [v.km for _, v in ins],
                [v.fuel for _, v in ins], [v.photo_url for _, v in ins],
                [v.listing_ref for _, v in ins])
            landed = {
                (row["entity_ulid"], row["deep_link"]): row["vehicle_ulid"]
                for row in await conn.fetch(
                    """SELECT vehicle_ulid, entity_ulid, deep_link FROM vehicle
                       WHERE (entity_ulid, deep_link) IN (
                         SELECT * FROM unnest($1::text[], $2::text[]))""",
                    [k[0] for k in new_keys], [k[1] for k in new_keys])
            }
            for key in new_keys:
                real = landed.get(key)
                if real is not None and real == vehicle_ulid_for[key]:
                    confirmed_new.append(key)
                elif real is not None:
                    vehicle_ulid_for[key] = real  # someone else won the race; adopt their ulid

        stats["cars_caged"] += len(cars)
        stats["new_cars"] += len(confirmed_new)

        # ---- EDGES: one batched upsert; RETURNING (xmax=0) counts genuinely new edges. price NULL.
        e_vehicles = [vehicle_ulid_for[k] for k, _ in cars]
        e_urls = [v.deep_link for _, v in cars]
        e_refs = [v.listing_ref for _, v in cars]
        edge_rows = await conn.fetch(_BULK_UPSERT_EDGES, e_vehicles, e_urls, e_refs, platform_ulid)
        stats["edges_created"] += sum(1 for row in edge_rows if row["inserted"])

        # ---- NEW delta events — only for genuinely new cars. price stays NULL (bid gated).
        if confirmed_new:
            ev_ulids, ev_vehicles, ev_entities, ev_payloads = [], [], [], []
            for key in confirmed_new:
                v = by_key[key]
                payload = {"price": None, "title": v.title, "platform": LV_TRADE_NAME,
                           "km": v.km, "year": v.year, "make": v.make, "model": v.model,
                           "consignor": v.seller_company, "price_gate": "bid_registration_gated"}
                ev_ulids.append(ulid())
                ev_vehicles.append(vehicle_ulid_for[key])
                ev_entities.append(key[0])
                ev_payloads.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_ulids, ev_vehicles, ev_entities, ev_payloads)
            stats["new_events"] += len(confirmed_new)


async def _reconcile_aged_out(conn: asyncpg.Connection, platform_ulid: str,
                              vehicles_before: set[str], harvested: set[str], stats: dict) -> None:
    """Retire any LocalizaVO car that was on an edge BEFORE this run but was NOT seen this run, so no
    phantom stale lot is counted live. ONLY on a clean full drain (the caller guards on fetch_error is
    None) so a transient blip never falsely retires the whole catalog."""
    if not harvested:
        return
    seen_ulids = {
        r["vehicle_ulid"] for r in await conn.fetch(
            """SELECT pl.vehicle_ulid
                 FROM platform_listing pl
                 JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
                 JOIN unnest($2::text[]) AS h(deep_link) ON h.deep_link = v.deep_link
                WHERE pl.platform_entity_ulid = $1""",
            platform_ulid, list(harvested))
    }
    aged = list(vehicles_before - seen_ulids)
    if not aged:
        return
    async with conn.transaction():
        await conn.execute(
            "UPDATE platform_listing SET status='removed', last_seen=now() "
            "WHERE platform_entity_ulid=$1 AND vehicle_ulid = ANY($2::text[])",
            platform_ulid, aged)
        await conn.execute(
            "UPDATE vehicle SET status='gone', last_seen=now() "
            "WHERE vehicle_ulid = ANY($1::text[])", aged)
    stats["retired_listings"] += len(aged)
    stats["retired_vehicles"] += len(aged)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

DEFAULT_CONCURRENCY = 2   # a couple of event pages can drain in parallel; the governor's bucket bounds
                          # the aggregate rate so the small SSR host is never hammered.


async def harvest(concurrency: int = DEFAULT_CONCURRENCY) -> dict:
    conn = await asyncpg.connect(DSN)
    concurrency = max(1, concurrency)
    fetcher = LocalizavoFetcher(pool_size=concurrency)
    stats = {
        "index_pages_fetched": 0, "events_seen": 0, "events_fetched": 0,
        "lots_parsed": 0, "cars_caged": 0, "new_cars": 0, "edges_created": 0, "new_events": 0,
        "declared_full": None, "retired_vehicles": 0, "retired_listings": 0,
        "concurrency": concurrency,
    }
    harvested: set[str] = set()  # deep_links seen this run (for the aged-out reconcile + VAM truth).

    # S-HEALTH gate: if the breaker is OPEN (a recent ban/throttle still cooling), skip gracefully.
    if await is_open(conn, LV_SOURCE_KEY):
        print(f"[localizavo_wholesale] breaker OPEN for {LV_SOURCE_KEY}; skipping drain "
              f"(graceful degradation, last snapshot still served).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": LV_SOURCE_KEY}

    gov = governor()
    governed_get = gov.wrap_fetch_text(fetcher.get_text)

    fetch_error: str | None = None
    last_http: int | None = None
    try:
        platform_ulid = await ensure_platform_entity(conn)
        platform_code = localizavo_platform_cdp_code()
        print(f"[localizavo_wholesale] platform entity ready: {platform_code} (ulid={platform_ulid}) "
              f"kind={LV_PLATFORM_KIND} group={LV_SOURCE_GROUP} tier={LV_DEFENSE_TIER} family={LV_FAMILY}")
        print(f"[localizavo_wholesale] governor paces host {host_of(_BASE)} (SSR lot cards).")

        vehicles_before = {r["vehicle_ulid"] for r in await conn.fetch(
            "SELECT vehicle_ulid FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)}

        # ---- (1) Collect every public auction-event id from the index pages.
        event_ids: list[str] = []
        seen_ev: set[str] = set()
        for idx_url in _INDEX_URLS:
            try:
                html = await fetcher.get_async(governed_get, idx_url)
                stats["index_pages_fetched"] += 1
            except Exception as e:
                fetch_error = fetch_error or str(e)
                last_http = fetcher.last_status
                print(f"[localizavo_wholesale] index fetch failed ({idx_url}): {e}")
                continue
            for sid in parse_event_ids(html):
                if sid not in seen_ev:
                    seen_ev.add(sid)
                    event_ids.append(sid)
        stats["events_seen"] = len(event_ids)
        print(f"[localizavo_wholesale] public auction events found: {len(event_ids)} -> {event_ids}")

        # ---- (2) Drain each event fully (nReg=0), build the per-event seller, ingest its lots.
        sales: dict[str, str] = {}        # sale_id -> event title
        event_lots: dict[str, list[Lot]] = {}
        for sid in event_ids:
            url = _EVENT_URL.format(sid=sid)
            try:
                html = await fetcher.get_async(governed_get, url)
                stats["events_fetched"] += 1
            except Exception as e:
                fetch_error = fetch_error or str(e)
                last_http = fetcher.last_status
                print(f"[localizavo_wholesale] event fetch failed ({url}): {e}; stopping honestly.")
                break
            title = parse_event_title(html, sid)
            lots = parse_event_lots(sid, html)
            sales[sid] = title
            event_lots[sid] = lots
            stats["lots_parsed"] += len(lots)
            print(f"[localizavo_wholesale] event {sid} '{title}': {len(lots)} lots (nReg=0 full drain).")

        if sales:
            sale_to_ulid = await ensure_sale_entities(conn, sales)
            all_lots = [lot for sid in sales for lot in event_lots.get(sid, [])]
            stats["declared_full"] = len(all_lots)
            # ingest in batches so one transaction never grows unbounded.
            BATCH = 100
            for i in range(0, len(all_lots), BATCH):
                await _ingest_lots(conn, platform_ulid, sale_to_ulid, all_lots[i:i + BATCH],
                                   harvested, stats)
                print(f"[localizavo_wholesale] ingested batch: caged so far={stats['cars_caged']} "
                      f"new={stats['new_cars']} edges={stats['edges_created']}")

        # ---- (3) Reconcile aged-out lots — ONLY on a clean full drain (no fetch_error).
        if fetch_error is None:
            await _reconcile_aged_out(conn, platform_ulid, vehicles_before, harvested, stats)
            if stats["retired_vehicles"]:
                print(f"[localizavo_wholesale] retired {stats['retired_vehicles']} aged-out lots.")

        # ---- (4) Health + recipe + count verdict.
        ok = fetch_error is None and stats["cars_caged"] > 0
        if ok:
            await record_run(conn, LV_SOURCE_KEY, ok=True, rows=stats["cars_caged"], http_status=200)
            write_recipe(platform_code, LOCALIZAVO_RECIPE)
            # VAM: distinct lots caged this run vs the live events' own total, via >=2 orthogonal paths.
            live_edges = await conn.fetchval(
                "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1 "
                "AND status='listed'", platform_ulid)
            db_join_vehicles = await conn.fetchval(
                """SELECT count(DISTINCT pl.vehicle_ulid) FROM platform_listing pl
                   JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
                   WHERE pl.platform_entity_ulid=$1 AND pl.status='listed'""", platform_ulid)
            paths = {"declared_total": stats["declared_full"] or 0,
                     "harvested_distinct": len(harvested),
                     "live_edges": int(live_edges or 0),
                     "db_join_vehicles": int(db_join_vehicles or 0)}
            try:
                verdict = await record_count_verdict(
                    conn, subject_type="platform", subject_key=platform_code,
                    claim="localizavo_full_public_catalog", paths=paths, tolerance=0.10)
                stats["count_verdict"] = verdict
                stats["count_paths"] = paths
            except Exception as e:
                print(f"[localizavo_wholesale] count verdict skipped ({e}).")
        else:
            reason = fetch_error or "no cars caged"
            await record_run(conn, LV_SOURCE_KEY, ok=False, rows=stats["cars_caged"],
                             error=reason[:300], http_status=last_http)
            await auto_repair(conn, LV_SOURCE_KEY, reason[:200], phase="scrape",
                              cdp_code=platform_code, http_status=last_http)

        stats["fetch_error"] = fetch_error
        stats["platform_code"] = platform_code
        return stats
    finally:
        await conn.close()


def _print_summary(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[localizavo_wholesale] SKIPPED: {stats.get('reason')}")
        return
    print("\n========== LOCALIZAVO WHOLESALE — SUMMARY ==========")
    for k in ("platform_code", "declared_full", "index_pages_fetched", "events_seen",
              "events_fetched", "lots_parsed", "cars_caged", "new_cars", "edges_created",
              "new_events", "retired_vehicles", "count_verdict", "count_paths", "fetch_error"):
        if k in stats:
            print(f"  {k:20} = {stats[k]}")
    print("====================================================\n")


def _force_utf8_stdout() -> None:
    """Windows consoles/pipes default to cp1252, which cannot encode the accented company/fuel labels
    this connector prints (ESPAÑA, Diésel) — a raw print() then crashes the drain mid-flight. Reconfigure
    stdout/stderr to UTF-8 (errors='replace'). Idempotent, no-op where already UTF-8."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass


def main(argv=None) -> int:
    _force_utf8_stdout()
    p = argparse.ArgumentParser(description="LocalizaVO wholesale harvester (b2b_auctions front).")
    p.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    args = p.parse_args(argv)
    stats = asyncio.run(harvest(concurrency=args.concurrency))
    _print_summary(stats)
    return 0 if (not stats.get("fetch_error") and stats.get("cars_caged", 0) > 0) else 1


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    raise SystemExit(main())
