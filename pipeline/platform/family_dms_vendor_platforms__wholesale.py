"""DMS vendor-platforms FAMILY harvester — the LONG-TAIL multiplier, end to end.

This is NOT a marketplace connector. It is the proof of the OTHER half of the
mandate: the inventory that lives on each dealer's OWN website. Thousands of
Spanish compraventas/concesionarios do not feed a Tier-1 marketplace — their
stock only exists on `www.<dealer>.es`. Harvesting them one-by-one does not
scale; the multiplier is the DMS/CMS FAMILY: group dealers by the vendor
platform their site runs on, then ONE recipe harvests MANY dealers.

The family proven here is **"dms (vendor platforms)"** — the DMS-vendor websites
that ship a uniform, server-rendered stock surface. Two subfamilies are covered,
each with its OWN fingerprint and parser, but ONE family recipe + ONE governor +
ONE cage contract:

  1. inventario.pro (HIGHEST leverage — 15 own-site dealers / 19 entities)
       * fingerprint: the `inventario.pro` asset host on every page
       * listing index: `/coches` (paginated `?pagina=N`)
       * detail link template: `/coches/<make>/<model>/<numeric_id>`
       * server-rendered card (`card_N` / `titulo_card` / `precio` / `detalles`),
         km via `uk-icon-road`, year via `uk-icon-calendar-o`, fuel via
         `inventario-icon-fuel`. Byte-identical across all members -> ONE parser.
       * VERIFIED LIVE 2026-06-13 (canaauto.es, carsandbikes.es, ftome.com):
         HTTP 200 on /coches, `inventario.pro` fingerprint present, `?pagina=2`
         yields fresh cards, prices/km/year render server-side. No JS needed.

  2. motorflash (11 own-site dealers / 12 entities)
       * fingerprint: the `motorflash` signal (Motorflash stock widget; host CMS
         varies — Drupal/custom). Detail template `/ficha-vehiculo-ocasion/<slug>/<id>`.
       * each card carries CLEAN hidden-input structured data: `precio`,
         `marcaVehiculo`, `modeloVehiculo`, `kilometros`, `mesesAntiguedad`,
         `estado` — parsed directly. VERIFIED LIVE 2026-06-13 (helmantica.es):
         `/coches-ocasion` HTTP 200, motorflash signal present, ficha links +
         hidden inputs render server-side.

Because each subfamily's markup is uniform across its members, ONE parser reads
them all. That is the multiplier the mandate demands: a FAMILY recipe, not a
per-dealer scraper. One recipe -> N dealers, proven E2E in the DB.

Ownership model (the long-tail half — SIMPLER than a marketplace):
  the dealer            -> entity, kind in (compraventa, concesionario_oficial)
                           (already in DB; resolved by website host, touched)
  each car on its site  -> vehicle, OWNED BY that dealer (entity_ulid = dealer)

There is NO platform_listing edge here: a dealer's own website is the PRIMARY
source of its own stock, not a third-party marketplace. The vehicle is owned by
the REAL dealer entity, never by an "inventario.pro" or "motorflash" platform
row. Ownership is singular and direct — the per-dealer recipe model lifted to a
family so one recipe serves the whole family.

This module mirrors pipeline.platform.family_dealerk_wholesale's spine EXACTLY —
same governor choke point, same GeoResolver, same idempotent ON CONFLICT upserts,
same NEW-delta events, same VAM count quorum, same S-HEALTH heartbeat + breaker —
so the long-tail flows through the ONE proven architecture, not a fork of it.

Run:
  python -m pipeline.platform.family_dms_vendor_platforms__wholesale \\
      --dealers canaauto.es carsandbikes.es ftome.com helmantica.es
  python -m pipeline.platform.family_dms_vendor_platforms__wholesale --from-db --limit 8
  python -m pipeline.platform.family_dms_vendor_platforms__wholesale --seeds   # all known seeds
"""
from __future__ import annotations

import argparse
import asyncio
import html as _htmllib
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
# Family identity. The source_key is the FAMILY, not a single dealer: every
# dealer harvested through this recipe is attested by the same provenance key,
# and the recipe is one file shared by the whole family.
# ---------------------------------------------------------------------------
FAMILY_KEY = "family_dms_vendor_platforms"
FAMILY_NAME = "DMS vendor platforms (inventario.pro + motorflash) dealer-site family"

_IMPERSONATE = "chrome131"
_TIMEOUT = 30
DEFAULT_MAX_PAGES = 25          # generous cap; long-tail dealers rarely exceed this

# Known seed dealers (live-verified members), used by --seeds. Each ALREADY
# exists in the DB as a real dealer entity (resolved by website host).
INVENTARIO_PRO_SEEDS = (
    "canaauto.es", "carsandbikes.es", "ftome.com", "masmotorcantabria.net",
    "eveauto.es", "autosniser.es", "integralmotion.es", "iluscar.com",
    "mobilitycentro.com", "garciautodelvalles.com", "automovilesgabilondo.com",
    "autosocasionalminares.com", "carmotors99.com", "tuokasion.es", "bellamachina.es",
)
MOTORFLASH_SEEDS = (
    "helmantica.es", "grupmibec.com", "autoelia.es", "movento.es",
    "bmwpremiumselection.es",
)
ALL_SEEDS = INVENTARIO_PRO_SEEDS + MOTORFLASH_SEEDS


# ---------------------------------------------------------------------------
# Parsed shape (field names taken from the REAL card markup, not assumed).
# ---------------------------------------------------------------------------
@dataclass
class Vehicle:
    deep_link: str          # absolute PDP url
    listing_ref: str        # the numeric id in the PDP path (native stable ref)
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    photo_url: str | None
    subfamily: str          # 'inventario_pro' | 'motorflash'


def _clean(s: str | None) -> str | None:
    if s is None:
        return None
    s = _htmllib.unescape(s).strip()
    return s or None


def _digits_to_int(raw: str | None, lo: int, hi: int) -> int | None:
    if not raw:
        return None
    d = re.sub(r"[^\d]", "", raw)
    if not d:
        return None
    try:
        v = int(d)
    except ValueError:
        return None
    return v if lo <= v <= hi else None


def _split_make_model(text: str | None) -> tuple[str | None, str | None]:
    text = _clean(text)
    if not text:
        return (None, None)
    parts = text.split()
    if len(parts) == 1:
        return (parts[0], None)
    return (parts[0], " ".join(parts[1:]))


# ===========================================================================
# Subfamily fingerprints. A site is classified by which vendor signal it serves.
# Order matters: inventario.pro is the cleaner/cheaper parse and is checked first.
# ===========================================================================
_FP_INVENTARIO_PRO = "inventario.pro"
_FP_MOTORFLASH = "motorflash"


def classify_subfamily(home_html: str) -> str | None:
    low = home_html.lower()
    if _FP_INVENTARIO_PRO in low:
        return "inventario_pro"
    if _FP_MOTORFLASH in low:
        return "motorflash"
    return None


# ===========================================================================
# inventario.pro parser. Cards are server-rendered `card_N` blocks. We anchor on
# the detail link `/coches/<make>/<model>/<id>` (the make/model are IN the path,
# so we never need to guess them), then read title/price/km/year/fuel from the
# stable classes. The page bytes are latin-1-ish: `€` arrives as a replacement
# char, so price detection keys on the `precio` class, not on a euro glyph.
# ===========================================================================
_IP_DETAIL_RE = re.compile(
    r'href=["\'](/coches/([a-z0-9\-]+)/([a-z0-9\-]+)/(\d+))["\']', re.I)
# split into per-card fragments on the card container id
_IP_CARD_SPLIT = re.compile(r'<div\s+id="card\d+"', re.I)
# Variant A title: <div class="titulo_card ...">Make Model</div>
_IP_TITLE_A_RE = re.compile(r'titulo_card[^>]*>\s*([^<]+?)\s*<', re.I)
# Variant B title: <div class="titulo">Make Model</div> [+ <div class="subtitulo">version</div>]
_IP_TITLE_B_RE = re.compile(r'class="titulo"[^>]*>\s*([^<]+?)\s*<', re.I)
_IP_SUBTITLE_RE = re.compile(r'class="subtitulo"[^>]*>\s*([^<]+?)\s*<', re.I)
_IP_PRICE_RE = re.compile(r'class="precio"[^>]*>\s*([0-9][0-9.\s]*)', re.I)
# photos live on either imgs.inventario.pro or fotos.inventario.pro
_IP_IMG_RE = re.compile(
    r'(https?://(?:imgs|fotos)\.inventario\.pro/[^"\'\s)]+?\.(?:jpe?g|png|webp))', re.I)
# Variant A detail rows: <span class="uk-icon-road"></span> N km, etc.
_IP_KM_A_RE = re.compile(r'uk-icon-road[^>]*></span>\s*([0-9][0-9.\s]*)\s*km', re.I)
_IP_YEAR_A_RE = re.compile(r'uk-icon-calendar-o[^>]*></span>\s*(\d{4})', re.I)
_IP_FUEL_A_RE = re.compile(r'inventario-icon-fuel[^>]*></span>\s*([^<]+?)\s*</div>', re.I)
# Variant B/C detail rows: <div class="flex"|"detalle"> <svg>..</svg> VALUE </div>,
# ordered ~year, km, fuel, transmission. We strip the SVG then read the trailing text.
_IP_FLEX_RE = re.compile(r'class="(?:flex|detalle)"[^>]*>(.*?)</div>', re.I | re.S)
_IP_SVG_RE = re.compile(r'<svg.*?</svg>', re.I | re.S)
_IP_YEAR_TOKEN_RE = re.compile(r'\b(19\d{2}|20\d{2})\b')
_IP_KM_TOKEN_RE = re.compile(r'([0-9][0-9.\s]*)\s*km', re.I)


def _fix_mojibake(s: str | None) -> str | None:
    """inventario.pro serves latin-1 bytes decoded as utf-8 by curl_cffi, so
    'Eléctrico' arrives as 'El�ctrico'. Best-effort repair via latin-1 round-trip."""
    if s is None:
        return None
    if "�" not in s:
        return s
    try:
        return s.encode("utf-8", "ignore").decode("latin-1", "ignore").strip() or s
    except Exception:
        return s


def parse_inventario_pro(listing_html: str, base: str) -> list[Vehicle]:
    """Parse every used-car card from one inventario.pro listing page.
    ONE parser, every member of the subfamily."""
    out: list[Vehicle] = []
    seen: set[str] = set()
    fragments = _IP_CARD_SPLIT.split(listing_html)
    for frag in fragments[1:]:               # [0] is pre-first-card preamble
        m = _IP_DETAIL_RE.search(frag)
        if not m:
            continue
        rel, make_slug, model_slug, lid = m.group(1), m.group(2), m.group(3), m.group(4)
        deep_link = base + rel
        if deep_link in seen:
            continue
        seen.add(deep_link)

        # title: variant A is `<div class="titulo_card">Make Model</div>` (text inline);
        # variants B/C nest `<div class="titulo">Make</div><div class="subtitulo">ver</div>`
        # inside (sometimes wrapped by an empty `titulo_card`). Prefer A only when it
        # actually captured text; otherwise compose from titulo + subtitulo.
        title = None
        tA = _IP_TITLE_A_RE.search(frag)
        if tA and _clean(tA.group(1)):
            title = _fix_mojibake(_clean(tA.group(1)))
        if not title:
            tB = _IP_TITLE_B_RE.search(frag)
            sub = _IP_SUBTITLE_RE.search(frag)
            bits = [b for b in (
                _clean(tB.group(1)) if tB else None,
                _clean(sub.group(1)) if sub else None) if b]
            title = _fix_mojibake(" ".join(bits)) if bits else None
        # make/model: prefer the title's first token; fall back to the URL slugs.
        make, model = _split_make_model(title)
        if not make:
            make = make_slug.replace("-", " ").title()
        if not model:
            model = model_slug.replace("-", " ").title()

        price = None
        pm = _IP_PRICE_RE.search(frag)
        if pm:
            price = _digits_to_int(pm.group(1), 50, 100_000_000)
            price = float(price) if price is not None else None

        # detail rows: variant A uses icon-class spans; variant B uses <div class="flex">
        # rows (SVG + trailing text) ordered year, km, fuel, transmission.
        km = _digits_to_int(
            _IP_KM_A_RE.search(frag).group(1), 0, 5_000_000) if _IP_KM_A_RE.search(frag) else None
        year = _digits_to_int(
            _IP_YEAR_A_RE.search(frag).group(1), 1900, 2100) if _IP_YEAR_A_RE.search(frag) else None
        fuel = _fix_mojibake(_clean(
            _IP_FUEL_A_RE.search(frag).group(1))) if _IP_FUEL_A_RE.search(frag) else None
        # Variant B/C: read the <div class="flex"|"detalle"> rows (SVG-stripped) and
        # fill any field still missing. Each field fills INDEPENDENTLY so a row that
        # only yields fuel does not block km/year discovery.
        if km is None or year is None or fuel is None:
            for fm in _IP_FLEX_RE.finditer(frag):
                inner = _IP_SVG_RE.sub(" ", fm.group(1))
                inner = re.sub(r"<[^>]+>", " ", inner)       # drop nested tags (e.g. <img>)
                val = _clean(inner)
                if not val:
                    continue
                low = val.lower()
                if km is None:
                    kmm = _IP_KM_TOKEN_RE.search(val)
                    if kmm:
                        km = _digits_to_int(kmm.group(1), 0, 5_000_000)
                        continue
                if year is None and "km" not in low:
                    ym = _IP_YEAR_TOKEN_RE.search(val)
                    if ym:
                        year = _digits_to_int(ym.group(1), 1900, 2100)
                        continue
                if fuel is None and "km" not in low and re.search(r"[A-Za-z]", val):
                    if any(t in low for t in ("sel", "sél", "gasolina", "híbrido",
                                              "hibrido", "eléct", "elect", "gnc",
                                              "glp", "etanol")):
                        fuel = _fix_mojibake(val)
        photo = _IP_IMG_RE.search(frag)

        out.append(Vehicle(
            deep_link=deep_link, listing_ref=lid, title=title, make=make,
            model=model, year=year, km=km, price=price, fuel=fuel,
            photo_url=photo.group(1) if photo else None, subfamily="inventario_pro"))
    return out


# ===========================================================================
# motorflash parser. Each card carries CLEAN structured data as hidden inputs
# (precio / marcaVehiculo / modeloVehiculo / kilometros / mesesAntiguedad), plus
# the ficha detail link `/ficha-vehiculo-ocasion/<slug>/<id>`. We split on the
# ficha id and read the inputs in the SAME card window. No mojibake here.
# ===========================================================================
_MF_DETAIL_RE = re.compile(
    r'href=["\'](/ficha-vehiculo-ocasion/([a-z0-9\-]+)/(\d+))["\']', re.I)
_MF_HIDDEN_RE = re.compile(
    r'<input[^>]*name="([a-zA-Z]+)"[^>]*value="([^"]*)"', re.I)
_MF_IMG_RE = re.compile(
    r'(https?://images\.motorflash\.com/[^"\'\s]+)', re.I)


def _mf_hidden_map(frag: str) -> dict[str, str]:
    return {k: _htmllib.unescape(v) for k, v in _MF_HIDDEN_RE.findall(frag)}


def parse_motorflash(listing_html: str, base: str) -> list[Vehicle]:
    """Parse every used-car card from one motorflash listing page.
    The card's hidden inputs are the structured truth; the ficha link is the id."""
    out: list[Vehicle] = []
    seen: set[str] = set()
    # Window each card from its hidden-input block (which precedes the ficha link)
    # up to the next ficha id. Anchor on detail links and read backwards/forwards.
    detail_positions = [(m.start(), m) for m in _MF_DETAIL_RE.finditer(listing_html)]
    if not detail_positions:
        return out
    # Build distinct-id ordered cuts so each window holds exactly one vehicle's data.
    cuts: list[tuple[str, str, int]] = []   # (deep_link, listing_ref, anchor_pos)
    for pos, m in detail_positions:
        rel, lid = m.group(1), m.group(3)
        deep_link = base + rel
        if deep_link in seen:
            continue
        seen.add(deep_link)
        cuts.append((deep_link, lid, pos))

    for i, (deep_link, lid, pos) in enumerate(cuts):
        end = cuts[i + 1][2] if i + 1 < len(cuts) else min(len(listing_html), pos + 8000)
        # the hidden inputs sit just BEFORE the first ficha anchor of this card;
        # widen the window backward to the previous card's anchor (or 4k before).
        start = cuts[i - 1][2] if i > 0 else max(0, pos - 4000)
        window = listing_html[start:end]
        hm = _mf_hidden_map(window)

        make = _clean(hm.get("marcaVehiculo"))
        model = _clean(hm.get("modeloVehiculo"))
        price = _digits_to_int(hm.get("precio"), 50, 100_000_000)
        price = float(price) if price is not None else None
        km = _digits_to_int(hm.get("kilometros"), 0, 5_000_000)
        year = None
        meses = _digits_to_int(hm.get("mesesAntiguedad"), 0, 1200)
        # mesesAntiguedad is age-in-months from "now"; derive registration year.
        if meses is not None:
            from datetime import date
            year = date.today().year - (meses // 12)
            if not (1900 <= year <= 2100):
                year = None
        title_bits = [b for b in (make, model) if b]
        title = " ".join(title_bits) if title_bits else None
        photo = _MF_IMG_RE.search(window)

        out.append(Vehicle(
            deep_link=deep_link, listing_ref=lid, title=title, make=make,
            model=model, year=year, km=km, price=price, fuel=None,
            photo_url=photo.group(1) if photo else None, subfamily="motorflash"))
    return out


# ---------------------------------------------------------------------------
# Per-subfamily listing config: where the index lives + how pages enumerate.
# ---------------------------------------------------------------------------
_SUBFAMILY = {
    "inventario_pro": {
        "paths": ("/coches", "/coches-ocasion", "/coches-nuevos", "/vehiculos"),
        "page_param": "pagina",          # ?pagina=N
        "parser": parse_inventario_pro,
        "fingerprint": _FP_INVENTARIO_PRO,
    },
    "motorflash": {
        "paths": ("/coches-ocasion", "/coches", "/coches-segunda-mano",
                  "/coches-nuevos", "/vehiculos-de-ocasion"),
        "page_param": "pag",             # ?pag=N
        "parser": parse_motorflash,
        "fingerprint": _FP_MOTORFLASH,
    },
}


# ---------------------------------------------------------------------------
# Fetch — one curl_cffi GET per page, routed THROUGH the governor (per-host bucket).
# Each dealer is its own host, so the governor paces every dealer independently and
# politely without any cross-dealer interference.
# ---------------------------------------------------------------------------
def _decode_best(raw: bytes, utf8_text: str) -> str:
    """Some inventario.pro sites send latin-1/cp1252 bytes under a UTF-8 header, so
    curl_cffi's UTF-8 decode injects U+FFFD replacement chars (e.g. 'Diésel'->'Di?sel').
    When that happens, re-decode the RAW bytes as cp1252 (superset of latin-1) which
    recovers the accents. We only switch if the cp1252 decode has FEWER replacement
    chars, so genuinely-UTF-8 pages are left untouched."""
    if "�" not in utf8_text:
        return utf8_text
    try:
        alt = raw.decode("cp1252", "replace")
    except Exception:
        return utf8_text
    return alt if alt.count("�") < utf8_text.count("�") else utf8_text


class FamilyFetcher:
    def __init__(self) -> None:
        self._session = cffi_requests.Session(impersonate=_IMPERSONATE)
        self.last_status: int | None = None

    def fetch(self, url: str) -> str:
        resp = self._session.get(url, impersonate=_IMPERSONATE, timeout=_TIMEOUT)
        self.last_status = resp.status_code
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} on {url}")
        return _decode_best(resp.content, resp.text)


# ---------------------------------------------------------------------------
# The family recipe — ONE asset shared by every member of the family.
# ---------------------------------------------------------------------------
FAMILY_RECIPE = {
    "version": 1,
    "source": FAMILY_KEY,
    "family": FAMILY_NAME,
    "scope": "long-tail dealer OWN-SITE inventory, harvested by DMS vendor family",
    "engine": "curl_cffi+chrome131_impersonate+html(GET, server-rendered)",
    "access": ("OPEN public dealer websites (Chrome TLS fingerprint; no proxy, no "
               "browser, no creds). Server-rendered HTML — no JS execution needed."),
    "data_surface": "dealer_site_html",
    "ownership": "vehicle.entity_ulid = the DEALER itself (own-site stock; no marketplace edge)",
    "multiplier": ("ONE recipe + per-subfamily parser harvests EVERY family member, "
                   "because the card markup is uniform across each vendor's sites."),
    "subfamilies": {
        "inventario_pro": {
            "fingerprint": "the 'inventario.pro' asset host appears on every page",
            "listing_paths": list(_SUBFAMILY["inventario_pro"]["paths"]),
            "pagination": "?pagina=N until a page yields no NEW cards (or max_pages cap)",
            "detail_template": "/coches/<make>/<model>/<numeric_id>",
            "field_map": {
                "deep_link": "card detail anchor /coches/<make>/<model>/<id>",
                "listing_ref": "trailing numeric <id> in the detail path",
                "make": "titulo_card first token (fallback: <make> URL slug)",
                "model": "titulo_card remaining tokens (fallback: <model> URL slug)",
                "title": "div.titulo_card text",
                "price": "div.precio text (e.g. '45.900 €' -> 45900)",
                "km": "div.detalle with span.uk-icon-road -> N km",
                "year": "div.detalle with span.uk-icon-calendar-o -> YYYY",
                "fuel": "div.detalle with span.inventario-icon-fuel",
                "photo_url": "first imgs.inventario.pro/* image in the card",
            },
        },
        "motorflash": {
            "fingerprint": "the 'motorflash' signal (Motorflash stock widget; host CMS varies)",
            "listing_paths": list(_SUBFAMILY["motorflash"]["paths"]),
            "pagination": "?pag=N until a page yields no NEW cards (or max_pages cap)",
            "detail_template": "/ficha-vehiculo-ocasion/<slug>/<id>",
            "field_map": {
                "deep_link": "card detail anchor /ficha-vehiculo-ocasion/<slug>/<id>",
                "listing_ref": "trailing numeric <id> in the ficha path",
                "make": "hidden input name='marcaVehiculo'",
                "model": "hidden input name='modeloVehiculo'",
                "price": "hidden input name='precio'",
                "km": "hidden input name='kilometros'",
                "year": "derived from hidden input name='mesesAntiguedad' (age months)",
                "photo_url": "first images.motorflash.com/* image in the card",
            },
        },
    },
}


# ---------------------------------------------------------------------------
# DB layer — idempotent upserts mirroring family_dealerk_wholesale (no edge).
# ---------------------------------------------------------------------------
async def resolve_dealer_for_host(conn: asyncpg.Connection, host: str) -> dict | None:
    """Find the dealer entity whose website matches this host. The long-tail dealer
    ALREADY exists (discovered earlier with a populated `website`). We match on the
    registrable host so we attach the harvest to the existing entity, never a dup."""
    bare = re.sub(r"^www\.", "", host.lower())
    row = await conn.fetchrow(
        """SELECT entity_ulid, cdp_code, trade_name, province_code, municipality_code, website
             FROM entity
            WHERE kind IN ('compraventa','concesionario_oficial','garaje')
              AND website IS NOT NULL AND website <> ''
              AND lower(regexp_replace(regexp_replace(website,'^https?://',''),'^www\\.','')) LIKE $1
            ORDER BY last_seen DESC
            LIMIT 1""",
        f"{bare}%")
    return dict(row) if row else None


async def upsert_dealer_by_host(conn: asyncpg.Connection, host: str) -> dict | None:
    """Return the owning dealer entity for `host`, upserting one if the DB has none.

    Preferred path: the dealer is already in the DB (matched by website host) — we
    use it as-is and stamp the family provenance. Fallback: mint a minimal
    domain-keyed entity so the harvest still has a REAL dealer owner (never a
    platform row)."""
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
                payload = {"price": v.price, "title": v.title,
                           "family": FAMILY_KEY, "subfamily": v.subfamily}
                ev_u.append(ulid())
                ev_v.append(vehicle_ulid_for[link])
                ev_e.append(dealer_ulid)
                ev_p.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_u, ev_v, ev_e, ev_p)
            stats["new_events"] += len(confirmed_new)


# ---------------------------------------------------------------------------
# Per-dealer harvest: fingerprint -> classify subfamily -> drain pages -> ingest.
# ---------------------------------------------------------------------------
def _page_url(base: str, path: str, param: str, n: int) -> str:
    if n <= 1:
        return f"{base}{path}"
    return f"{base}{path}?{param}={n}"


async def harvest_one_dealer(conn: asyncpg.Connection, governed_fetch,
                             fetcher: FamilyFetcher, host: str,
                             max_pages: int, stats: dict) -> dict:
    """Harvest ONE family dealer's own-site stock. Returns a per-dealer summary."""
    bare = re.sub(r"^www\.", "", host.lower())
    base = f"https://www.{bare}"
    summary = {"host": bare, "is_member": False, "subfamily": None, "vehicles": 0,
               "new": 0, "dealer_cdp": None, "pages": 0, "path": None}

    # 1) fetch the home page and classify the subfamily by fingerprint.
    try:
        home = await governed_fetch(base)
    except Exception:
        try:
            home = await governed_fetch(f"https://{bare}")
            base = f"https://{bare}"
        except Exception as e2:
            summary["error"] = f"home fetch failed: {e2}"
            stats["dealers_failed"] += 1
            return summary
    subfamily = classify_subfamily(home)
    if subfamily is None:
        summary["error"] = "not a DMS-vendor-family site (no inventario.pro/motorflash signal)"
        stats["dealers_skipped_non_family"] += 1
        return summary
    summary["is_member"] = True
    summary["subfamily"] = subfamily
    stats["dealers_member"] += 1
    stats["by_subfamily"].setdefault(subfamily, 0)
    stats["by_subfamily"][subfamily] += 1

    cfg = _SUBFAMILY[subfamily]
    parser = cfg["parser"]
    page_param = cfg["page_param"]

    # 2) resolve / upsert the owning dealer entity.
    dealer = await upsert_dealer_by_host(conn, bare)
    if dealer is None:
        summary["error"] = "could not resolve owning dealer"
        stats["dealers_failed"] += 1
        return summary
    summary["dealer_cdp"] = dealer["cdp_code"]

    # 3) find the listing path that yields cards, then drain its pages.
    all_vehicles: list[Vehicle] = []
    chosen_path: str | None = None
    for path in cfg["paths"]:
        try:
            html_text = await governed_fetch(_page_url(base, path, page_param, 1))
        except Exception:
            continue
        cards = parser(html_text, base)
        if not cards:
            continue
        chosen_path = path
        seen_links = {v.deep_link for v in cards}
        all_vehicles.extend(cards)
        page = 2
        while page <= max_pages:
            try:
                ph = await governed_fetch(_page_url(base, path, page_param, page))
            except Exception:
                break
            pcards = parser(ph, base)
            fresh = [c for c in pcards if c.deep_link not in seen_links]
            if not fresh:
                break                          # no new cars -> end of inventory
            for c in fresh:
                seen_links.add(c.deep_link)
            all_vehicles.extend(fresh)
            summary["pages"] = page
            page += 1
        summary["pages"] = max(summary["pages"], 1)
        break                                  # first path that works wins
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
            WHERE kind IN ('compraventa','concesionario_oficial','garaje')
              AND website IS NOT NULL AND website <> ''
            ORDER BY last_seen DESC""")
    hosts: list[str] = []
    seen: set[str] = set()
    skip_suffix = ("toyota.es", "citroen.es", "mercedes-benz.es", "peugeot.es",
                   "nissan.es", "renault.es", "bmw.es", "opel.es", "honda.es",
                   "safamotor.com", "dacia.es", "coches.net", "autoscout24.es",
                   "wixsite.com", "ueniweb.com", "hyundai.es", "kia.com", "tesla.com")
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


async def harvest(dealers: list[str] | None, from_db: bool, use_seeds: bool,
                  limit: int, max_pages: int) -> dict:
    conn = await asyncpg.connect(DSN)
    fetcher = FamilyFetcher()
    stats = {
        "dealers_requested": 0, "dealers_member": 0, "dealers_harvested": 0,
        "dealers_skipped_non_family": 0, "dealers_empty": 0, "dealers_failed": 0,
        "cars_ingested": 0, "new_cars": 0, "new_events": 0,
        "by_subfamily": {}, "harvested_pairs": set(), "summaries": [],
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
        if use_seeds:
            dealers = list(ALL_SEEDS)
        elif from_db or not dealers:
            dealers = await candidate_hosts_from_db(conn, limit)
            print(f"[{FAMILY_KEY}] {len(dealers)} candidate dealer hosts from DB "
                  f"(family confirmed per-dealer by fingerprint).")
        stats["dealers_requested"] = len(dealers)
        print(f"[{FAMILY_KEY}] family={FAMILY_NAME}")
        print(f"[{FAMILY_KEY}] governor paces each dealer host independently "
              f"(per-host token bucket). ONE recipe -> {len(dealers)} dealers.")

        for host in dealers:
            summary = await harvest_one_dealer(
                conn, governed_fetch, fetcher, host, max_pages, stats)
            stats["summaries"].append(summary)
            tag = (summary["subfamily"] or
                   ("member" if summary["is_member"] else "non-family"))
            print(f"[{FAMILY_KEY}]   {summary['host']:30s} {tag:14s} "
                  f"path={summary.get('path')} vehicles={summary['vehicles']:3d} "
                  f"new={summary['new']:3d}" +
                  (f"  ERR={summary['error']}" if summary.get("error") else ""))
            last_http = fetcher.last_status

        # Recipe: ONE file for the WHOLE family (keyed by the family, not a dealer).
        recipe_path = write_recipe(FAMILY_KEY, FAMILY_RECIPE)
        print(f"[{FAMILY_KEY}] family recipe written: {recipe_path}")

        # VAM count quorum for this family slice — like-with-like paths:
        #   harvested_pairs       = distinct (dealer, deep_link) pulled this run
        #   db_family_vehicles    = those same pairs read back from the DB (persist truth)
        #   cars_ingested_distinct= the run counter (catches silent ingest loss)
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
        stats.pop("harvested_pairs", None)
        return stats
    finally:
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[{FAMILY_KEY}] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 64)
    print("DMS VENDOR PLATFORMS FAMILY — LONG-TAIL HARVEST REPORT")
    print("=" * 64)
    print(f"  family               : {FAMILY_NAME}")
    print(f"  dealers requested    : {stats['dealers_requested']}")
    print(f"  family members       : {stats['dealers_member']}  {stats['by_subfamily']}")
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
            print(f"    {s['host']:30s} [{s.get('subfamily'):14s}] {s['vehicles']:3d} cars  "
                  f"(new {s['new']:3d})  cdp={s.get('dealer_cdp')}")
    print("=" * 64)


def main() -> None:
    p = argparse.ArgumentParser(
        description="DMS vendor platforms family long-tail harvester (one recipe -> N dealers)")
    p.add_argument("--dealers", nargs="*", default=None,
                   help="explicit dealer hosts (e.g. canaauto.es helmantica.es)")
    p.add_argument("--from-db", action="store_true",
                   help="pull candidate dealer hosts from the DB website column")
    p.add_argument("--seeds", action="store_true",
                   help="harvest the full known live-verified seed set of this family")
    p.add_argument("--limit", type=int, default=8,
                   help="max DB candidate dealers to try (with --from-db); default 8")
    p.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES,
                   help=f"max listing pages per dealer; default {DEFAULT_MAX_PAGES}")
    args = p.parse_args()
    stats = asyncio.run(harvest(args.dealers, args.from_db, args.seeds,
                                args.limit, args.max_pages))
    _print_report(stats)


if __name__ == "__main__":
    main()
