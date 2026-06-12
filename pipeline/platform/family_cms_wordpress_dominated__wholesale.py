"""WordPress-dominated CMS FAMILY harvester — the long-tail multiplier, end to end.

This is the SECOND family connector (after family_dealerk_wholesale.py) and it
proves the same thesis on the LARGEST long-tail family: the inventory that lives
on each dealer's OWN WordPress website. Per docs/architecture/longtail_families.md,
the `cms (WordPress-dominated)` family is the #1 own-site population — 157 domains
serving 179 dealers (42.5% of the long tail). Harvesting them one recipe at a time
does not scale; the multiplier is the CMS FAMILY: group dealers by the platform
their site runs, then ONE recipe harvests MANY dealers.

Unlike DealerK — where the byte-identical vcard markup let ONE parser read every
member — the WordPress family is "WordPress-dominated" but theme-VARIED: most
dealers run a CUSTOM WP theme, not one standard plugin. So this connector is built
as the mandate describes (longtail_families.md §"#1 family"): a generic WP
skeleton + a small per-theme adaptation layer. It carries TWO harvest strategies,
tried in order per dealer, all behind ONE family recipe + ONE provenance key:

  STRATEGY A — Vehica REST (the clean multiplier; verified live 2026-06-13).
    The "Vehica" WP car-dealer plugin powers a sub-family of these dealers and
    exposes a first-party PUBLIC JSON gateway at  /wp-json/vehica/v1/cars  that
    returns the WHOLE inventory in ONE call (resultsCount + results[] with a
    structured attributes[] block: Marca/Modelo/Año/Kilómetros/Combustible/
    "Precio al contado"). BYTE-IDENTICAL across every Vehica dealer -> ONE parser
    reads them all, no JS, no pagination. This is the JSON-API half of the family.

  STRATEGY B — server-rendered HTML cards (the volume tail; per-theme override).
    Non-Vehica WP dealers render their stock as SSR card blocks under a ranked
    listing slug ( /coches first per the family's live slug frequency ). The card
    selector varies by theme, so a small THEME OVERRIDE table maps a CSS marker
    (`ga-car-card`, `sc_cars_item`, ...) to its field extractors. Adding a theme is
    one table entry — the "thin per-site selector override" the mandate calls for.

Ownership model (the long-tail half — SIMPLER than a marketplace, identical to
family_dealerk_wholesale): a dealer's OWN website is the PRIMARY source of its own
stock, not a third-party marketplace, so ownership is singular and direct:

  the dealer            -> entity, kind='compraventa'/'concesionario_oficial'
                           (already in DB from discovery; upsert/touch + stamp family)
  each car on its site  -> vehicle, OWNED BY that dealer (entity_ulid = dealer)

There is NO platform_listing edge here (no marketplace). This module mirrors
pipeline.platform.family_dealerk_wholesale's spine EXACTLY — same governor choke
point, same GeoResolver, same idempotent ON CONFLICT upserts, same NEW-delta
events, same VAM count quorum, same S-HEALTH heartbeat + breaker — so the long-tail
flows through the ONE proven architecture, not a fork of it.

Run:
  python -m pipeline.platform.family_cms_wordpress_dominated__wholesale \
      --dealers autosraul.com automovilesjfz.com automovileslacanal.com gestiauto.es
  python -m pipeline.platform.family_cms_wordpress_dominated__wholesale --from-db --limit 8
"""
from __future__ import annotations

import argparse
import asyncio
import html as _htmllib
import json
import re
import os
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
# Family identity. The source_key is the FAMILY, not a single dealer: every dealer
# harvested through this recipe is attested by the same provenance key, and the
# recipe is one file shared by the whole family.
# ---------------------------------------------------------------------------
FAMILY_KEY = "family_cms_wp"
FAMILY_NAME = "WordPress-dominated dealer-site family (CMS long-tail #1)"

_IMPERSONATE = "chrome131"
_TIMEOUT = 30
DEFAULT_MAX_PAGES = 25          # HTML strategy cap; Vehica returns all in one call

# Ranked listing-path slugs, in live-frequency order (longtail_families.md §1):
#   /coches (229) > /vehiculos (49) > /catalogo (17) > /ocasion (17) >
#   /vehiculos-ocasion (14) > /stock (12) > /km0 (9) > /seminuevos (9) >
#   /coches-segunda-mano (7) > /coches-ocasion (7)
# A dealer's listing index is the FIRST of these that the site exposes. We also
# accept the dealer's own discovered index path (passed in or from the DB).
LISTING_SLUGS = (
    "/coches", "/vehiculos", "/catalogo", "/ocasion", "/vehiculos-ocasion",
    "/stock", "/km0", "/seminuevos", "/coches-segunda-mano", "/coches-ocasion",
    "/coches/segunda-mano", "/vehiculos-de-ocasion", "/coches-de-ocasion",
)

# Vehica plugin REST gateway — byte-identical across every Vehica dealer.
VEHICA_CARS_ENDPOINT = "/wp-json/vehica/v1/cars"

# Family spine: every member runs WordPress. The corroborator is "exposes a car
# inventory surface" — either the Vehica REST gateway, or SSR car cards under a
# listing slug. A bare WP blog with no inventory is NOT a member (no cards/endpoint).
_WP_MARKERS = ("wp-content", "wp-json", "wp-includes", "/wp-content/themes/")


# ---------------------------------------------------------------------------
# Parsed shape — one normalized vehicle, regardless of which strategy produced it.
# Field names taken from the REAL surfaces (Vehica attributes / card markup), not
# assumed.
# ---------------------------------------------------------------------------
@dataclass
class Vehicle:
    deep_link: str
    listing_ref: str | None      # native id (Vehica car id) when the surface exposes one
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    photo_url: str | None


def _clean(s: str | None) -> str | None:
    if s is None:
        return None
    s = _htmllib.unescape(s).strip()
    return s or None


def _digits_to_int(raw: str | None, lo: int, hi: int) -> int | None:
    if raw is None:
        return None
    d = re.sub(r"[^\d]", "", str(raw))
    if not d:
        return None
    try:
        n = int(d)
    except ValueError:
        return None
    return n if lo <= n <= hi else None


def _price_to_float(raw) -> float | None:
    """Accept a number, or a string like '12.900 €' / 'Al contado: 12.900 €'."""
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        v = float(raw)
        return v if v > 0 else None
    d = re.sub(r"[^\d]", "", str(raw))
    if not d:
        return None
    try:
        v = float(d)
    except ValueError:
        return None
    return v if v > 0 else None


def _split_make_model(text: str | None) -> tuple[str | None, str | None]:
    """Title 'CITROEN C4 PICASSO' -> make='CITROEN', model='C4 PICASSO'.
    First token = make; remainder = model. Keeps multi-word models intact."""
    text = _clean(text)
    if not text:
        return (None, None)
    parts = text.split()
    if len(parts) == 1:
        return (parts[0], None)
    return (parts[0], " ".join(parts[1:]))


# ---------------------------------------------------------------------------
# STRATEGY A — Vehica REST gateway parser. ONE parser reads EVERY Vehica dealer.
# The endpoint returns the WHOLE inventory in one call: {resultsCount, results:[
#   {id, name, url, slug, description, attributes:[{name, type, value, displayValue}]}]}.
# Attributes carry make/model/year/km/fuel/price by their Spanish `name`.
# ---------------------------------------------------------------------------
def _vehica_attr(attrs: list[dict], *names: str) -> dict | None:
    wanted = {n.lower() for n in names}
    for a in attrs or []:
        nm = (a.get("name") or "").strip().lower()
        # match on a normalized name (Año / Kilómetros carry accents)
        norm = _htmllib.unescape(nm)
        if norm in wanted or any(w in norm for w in wanted):
            return a
    return None


def _vehica_taxonomy_name(attr: dict | None) -> str | None:
    if not attr:
        return None
    val = attr.get("value")
    if isinstance(val, list) and val and isinstance(val[0], dict):
        return _clean(val[0].get("name"))
    return _clean(attr.get("displayValue") if isinstance(attr.get("displayValue"), str) else None)


def _vehica_number(attr: dict | None) -> int | None:
    if not attr:
        return None
    val = attr.get("value")
    if isinstance(val, (int, float)):
        return int(val)
    return _digits_to_int(attr.get("displayValue"), 0, 100_000_000)


def _vehica_price(attr: dict | None) -> float | None:
    """Vehica price attr: value = {currency_key: 12900} (or '' when unset)."""
    if not attr:
        return None
    val = attr.get("value")
    if isinstance(val, dict):
        for v in val.values():
            p = _price_to_float(v)
            if p is not None:
                return p
    return _price_to_float(val)


def parse_vehica(payload: dict) -> list[Vehicle]:
    """Parse the full Vehica /wp-json/vehica/v1/cars response. ONE parser, every
    Vehica member — the JSON-API multiplier."""
    out: list[Vehicle] = []
    seen: set[str] = set()
    for it in payload.get("results") or []:
        url = _clean(it.get("url"))
        if not url or url in seen:
            continue
        seen.add(url)
        attrs = it.get("attributes") or []
        title = _clean(it.get("name"))
        make = _vehica_taxonomy_name(_vehica_attr(attrs, "marca"))
        model = _vehica_taxonomy_name(_vehica_attr(attrs, "modelo"))
        if not make and title:
            make, model_fallback = _split_make_model(title)
            model = model or model_fallback
        year = _vehica_number(_vehica_attr(attrs, "ano", "año"))
        if year is not None and not (1900 <= year <= 2100):
            year = None
        km = _vehica_number(_vehica_attr(attrs, "kilometros", "kilómetros"))
        if km is not None and not (0 <= km <= 5_000_000):
            km = None
        fuel = _vehica_taxonomy_name(_vehica_attr(attrs, "combustible"))
        price = _vehica_price(_vehica_attr(attrs, "precio al contado"))
        if price is None:
            price = _vehica_price(_vehica_attr(attrs, "precio"))
        out.append(Vehicle(
            deep_link=url, listing_ref=str(it.get("id")) if it.get("id") is not None else None,
            title=title, make=make, model=model, year=year, km=km, price=price,
            fuel=fuel, photo_url=None))
    return out


# ---------------------------------------------------------------------------
# STRATEGY B — server-rendered HTML cards, with a per-THEME selector override.
# Each theme contributes ONE entry: a marker substring that identifies it, a card
# splitter, and field regexes. Adding a theme is one table row — the "thin per-site
# selector override" the mandate calls for. Verified live 2026-06-13.
# ---------------------------------------------------------------------------
@dataclass
class CardTheme:
    key: str
    marker: str                       # substring that proves this theme is in use
    card_split: re.Pattern            # split listing HTML into per-card fragments
    link_re: re.Pattern               # detail link (deep_link) inside a fragment
    title_re: re.Pattern              # title text inside a fragment
    price_re: re.Pattern              # price text inside a fragment
    spec_re: re.Pattern | None        # repeated spec tokens (year/km/fuel), in order
    page_template: str                # how to build page N (".../page/{n}/" or "?paged={n}")


_EURO = r'(?:&euro;|€|\xe2\x82\xac|\?)'   # '?' tolerates mojibake'd euro in latin-1 dumps

# Theme: gestiauto.es custom theme — `ga-car-card`. The detail link is the title
# anchor (the image-link puts href BEFORE the class, so we read the h3 anchor whose
# href reliably follows the class). Specs are ordered spans: year(4-digit), fuel,
# transmission, "NNN CV", doors, seats, "N Kms".
_THEME_GA = CardTheme(
    key="ga-car-card",
    marker="ga-car-card",
    card_split=re.compile(r'<article class="ga-car-card">'),
    link_re=re.compile(r'ga-car-card__title">\s*<a href="([^"]+)"', re.S),
    title_re=re.compile(r'ga-car-card__title">\s*<a[^>]*>\s*([^<]+?)\s*</a>', re.S),
    price_re=re.compile(r'ga-car-card__price-pill[^>]*>\s*<span>\s*(?:Desde:|Al contado:)?\s*'
                        r'([0-9][0-9.\s]*)\s*' + _EURO),
    spec_re=re.compile(r'ga-car-card__spec-text[^>]*>\s*([^<]+?)\s*<'),
    page_template="{base}/page/{n}/",
)

# Theme: tomellosomotor.com (Carz/ThemeREX `sc_cars_item`). Each card opens with the
# `sc_cars_item_thumb` image block; the title is the `sc_cars_item_title` h5 anchor;
# price is the first `cars_price_data cars_price1` span (cars_price2 is the monthly
# quota); year/km/fuel are `sc_cars_item_param_text` spans.
_THEME_SC = CardTheme(
    key="sc_cars_item",
    marker="sc_cars_item",
    card_split=re.compile(r'<div class="[^"]*sc_cars_item_thumb[^"]*"'),
    link_re=re.compile(r'sc_cars_item_title[^"]*"><a href="([^"]+)"'),
    title_re=re.compile(r'sc_cars_item_title[^"]*"><a[^>]*>\s*([^<]+?)\s*</a>', re.S),
    price_re=re.compile(r'cars_price_data cars_price1">\s*([0-9][0-9.\s]*)\s*' + _EURO),
    spec_re=re.compile(r'sc_cars_item_param_text">\s*([^<]+?)\s*<'),
    page_template="{base}/page/{n}/",
)

CARD_THEMES = (_THEME_GA, _THEME_SC)


def _parse_card_specs(theme: CardTheme, frag: str) -> tuple[int | None, int | None, str | None]:
    """Pull (year, km, fuel) from a card fragment's ordered spec tokens, when the
    theme exposes them. Year = a bare 4-digit; km = a token containing 'km'; fuel =
    a known fuel word. Robust to spec ordering across theme variants."""
    if theme.spec_re is None:
        return (None, None, None)
    toks = [_clean(t) for t in theme.spec_re.findall(frag)]
    year = km = None
    fuel = None
    fuels = ("diesel", "diésel", "gasolina", "hibrido", "híbrido", "electrico",
             "eléctrico", "glp", "gnc", "gas")
    for t in toks:
        if t is None:
            continue
        low = t.lower()
        if year is None and re.fullmatch(r"(19|20)\d{2}", t):
            year = int(t)
            continue
        if km is None and "km" in low:
            km = _digits_to_int(t, 0, 5_000_000)
            continue
        if fuel is None and any(f in low for f in fuels):
            fuel = t
    return (year, km, fuel)


def parse_html_cards(theme: CardTheme, listing_html: str, base_host: str) -> list[Vehicle]:
    """Parse every car card from one listing page using a theme's selectors. ONE
    parser per theme, shared by every dealer on that theme."""
    fragments = theme.card_split.split(listing_html)
    out: list[Vehicle] = []
    seen: set[str] = set()
    for frag in fragments[1:]:          # [0] is the pre-first-card preamble
        lm = theme.link_re.search(frag)
        if not lm:
            continue
        deep_link = _htmllib.unescape(lm.group(1)).strip()
        if not deep_link.startswith("http"):
            deep_link = f"https://{base_host}{deep_link}"
        if deep_link in seen:
            continue
        seen.add(deep_link)
        tm = theme.title_re.search(frag)
        title = _clean(tm.group(1)) if tm else None
        make, model = _split_make_model(title)
        price = None
        pm = theme.price_re.search(frag)
        if pm:
            price = _price_to_float(pm.group(1))
        year, km, fuel = _parse_card_specs(theme, frag)
        out.append(Vehicle(
            deep_link=deep_link, listing_ref=None, title=title, make=make,
            model=model, year=year, km=km, price=price, fuel=fuel, photo_url=None))
    return out


def detect_theme(listing_html: str) -> CardTheme | None:
    low = listing_html.lower()
    for theme in CARD_THEMES:
        if theme.marker in low:
            return theme
    return None


# ---------------------------------------------------------------------------
# Fetch — one curl_cffi GET per URL, routed THROUGH the governor (per-host bucket).
# Each dealer is its own host, so the governor paces every dealer independently and
# politely (STEALTH default ~0.7 req/s/host) without cross-dealer interference.
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


def is_wordpress(html_text: str) -> bool:
    low = html_text.lower()
    return any(m in low for m in _WP_MARKERS)


# ---------------------------------------------------------------------------
# The family recipe — ONE asset shared by every member of the family.
# ---------------------------------------------------------------------------
FAMILY_RECIPE = {
    "version": 1,
    "source": FAMILY_KEY,
    "family": FAMILY_NAME,
    "scope": "long-tail dealer OWN-SITE inventory, harvested by CMS (WordPress) family",
    "engine": "curl_cffi+chrome131_impersonate; Vehica REST JSON, else server-rendered HTML cards",
    "access": ("OPEN public dealer websites (Chrome TLS fingerprint; no proxy, no "
               "browser, no creds). Vehica REST returns full inventory server-side; "
               "HTML card themes are server-rendered — no JS execution needed."),
    "data_surface": "dealer_site (vehica_rest_json | wordpress_html_cards)",
    "fingerprint": ("WordPress (wp-content / wp-json). Member iff it exposes a car "
                    "inventory surface: the Vehica plugin REST gateway "
                    "/wp-json/vehica/v1/cars, OR server-rendered car cards under a "
                    "ranked listing slug."),
    "strategy_a_vehica": {
        "endpoint": VEHICA_CARS_ENDPOINT,
        "shape": "{resultsCount, results:[{id, name, url, slug, attributes:[...]}]}",
        "note": "returns the WHOLE inventory in one call; no pagination, no JS",
        "field_map": {
            "deep_link": "results[].url",
            "listing_ref": "results[].id (native Vehica car id)",
            "title": "results[].name",
            "make": "attributes[name=Marca].value[0].name",
            "model": "attributes[name=Modelo].value[0].name",
            "year": "attributes[name=Año].value (number)",
            "km": "attributes[name=Kilómetros].value (number)",
            "fuel": "attributes[name=Combustible].value[0].name",
            "price": "attributes[name=Precio al contado].value{currency:€amount}",
        },
    },
    "strategy_b_html_cards": {
        "listing_slugs_ranked": list(LISTING_SLUGS),
        "pagination": "/page/N/ (or ?paged=N) until a page yields no NEW cards",
        "theme_overrides": [t.key for t in CARD_THEMES],
        "note": ("WordPress is theme-VARIED; each theme is ONE override entry "
                 "(card splitter + field selectors). Adding a theme is one row."),
    },
    "ownership": "vehicle.entity_ulid = the DEALER itself (own-site stock; no marketplace edge)",
    "multiplier": ("ONE recipe + ONE Vehica parser harvests EVERY Vehica dealer "
                   "(byte-identical JSON); the HTML half adds a thin per-theme "
                   "selector override so one skeleton serves the volume tail."),
}


# ---------------------------------------------------------------------------
# DB layer — idempotent upserts mirroring family_dealerk_wholesale (no edge).
# ---------------------------------------------------------------------------
async def resolve_dealer_for_host(conn: asyncpg.Connection, host: str) -> dict | None:
    """Find the dealer entity in the DB whose website matches this host. The
    long-tail dealer ALREADY exists (discovered with a populated `website`). Match
    on the registrable host so we attach the harvest to the existing entity."""
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

    Preferred: the dealer is already in the DB (matched by website host) — use it
    as-is and stamp the family provenance. Fallback: mint a minimal domain-keyed
    entity so the harvest still has a real owner (the bare domain is a strong
    identity in codes.py; province_code left NULL)."""
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
                payload = {"price": v.price, "title": v.title, "family": FAMILY_KEY}
                ev_u.append(ulid())
                ev_v.append(vehicle_ulid_for[link])
                ev_e.append(dealer_ulid)
                ev_p.append(json.dumps(payload))
            await conn.execute(_BULK_INSERT_EVENTS, ev_u, ev_v, ev_e, ev_p)
            stats["new_events"] += len(confirmed_new)


# ---------------------------------------------------------------------------
# Per-dealer harvest: fingerprint -> Vehica REST (A) OR HTML cards (B) -> ingest.
# ---------------------------------------------------------------------------
def _bare(host: str) -> str:
    return re.sub(r"^www\.", "", host.lower()).split("/")[0]


async def _harvest_vehica(governed_fetch, base: str, bare: str) -> list[Vehicle] | None:
    """STRATEGY A. Try the Vehica REST gateway; returns vehicles, or None if the
    site is not a Vehica member (endpoint absent / non-JSON)."""
    for prefix in (base, f"https://{bare}"):
        url = f"{prefix}{VEHICA_CARS_ENDPOINT}"
        try:
            raw = await governed_fetch(url)
        except Exception:
            continue
        raw_s = raw.lstrip()
        if not raw_s.startswith("{"):
            continue
        try:
            payload = json.loads(raw)
        except (ValueError, json.JSONDecodeError):
            continue
        if "results" not in payload:
            continue
        return parse_vehica(payload)
    return None


# How many ranked slugs to probe before committing to the richest. A dealer often
# exposes its inventory under several slugs where some are PARTIAL teaser pages
# (e.g. /coches shows 4 featured cars while /vehiculos lists all 12). Picking the
# FIRST non-empty slug would cage a partial page, so we probe the ranked candidates
# and commit to the one with the MOST page-1 cards — the real full index. Bounded to
# keep request volume polite (the governor still paces every probe).
_SLUG_PROBE_BUDGET = 6


async def _harvest_html(governed_fetch, base: str, bare: str, given_path: str | None,
                        max_pages: int) -> tuple[list[Vehicle], str | None, str | None, int]:
    """STRATEGY B. Probe the ranked listing slugs, commit to the RICHEST index (the
    full listing, never a partial teaser), then drain its pages. Returns
    (vehicles, chosen_path, theme_key, pages)."""
    slugs: list[str] = []
    if given_path:
        slugs.append(given_path if given_path.startswith("/") else f"/{given_path}")
    slugs.extend(s for s in LISTING_SLUGS if s not in slugs)

    # 1) probe candidates; remember each slug's page-1 card yield + its theme.
    best: tuple[int, str, "CardTheme", list[Vehicle]] | None = None
    probed = 0
    for path in slugs:
        if probed >= _SLUG_PROBE_BUDGET and best is not None:
            break
        page1 = f"{base}{path}/"
        try:
            html_text = await governed_fetch(page1)
        except Exception:
            continue
        probed += 1
        theme = detect_theme(html_text)
        if theme is None:
            continue
        cards = parse_html_cards(theme, html_text, bare)
        if not cards:
            continue
        if best is None or len(cards) > best[0]:
            best = (len(cards), path, theme, cards)

    if best is None:
        return ([], None, None, 0)

    # 2) drain the winner's pages (the richest index is the real full listing).
    _, path, theme, cards = best
    all_vehicles = list(cards)
    seen = {v.deep_link for v in cards}
    pages = 1
    page = 2
    while page <= max_pages:
        page_url = theme.page_template.format(base=f"{base}{path}", n=page)
        try:
            ph = await governed_fetch(page_url)
        except Exception:
            break
        pcards = parse_html_cards(theme, ph, bare)
        fresh = [c for c in pcards if c.deep_link not in seen]
        if not fresh:
            break
        for c in fresh:
            seen.add(c.deep_link)
        all_vehicles.extend(fresh)
        pages = page
        page += 1
    return (all_vehicles, path, theme.key, pages)


async def harvest_one_dealer(conn: asyncpg.Connection, geo: GeoResolver,
                             governed_fetch, fetcher: FamilyFetcher, host: str,
                             given_path: str | None, max_pages: int, stats: dict) -> dict:
    """Harvest ONE WordPress-family dealer's own-site stock. Per-dealer summary."""
    bare = _bare(host)
    base = f"https://www.{bare}"
    summary = {"host": bare, "is_member": False, "strategy": None, "vehicles": 0,
               "new": 0, "dealer_cdp": None, "pages": 0, "path": None, "theme": None}

    # 1) fingerprint the home page — confirm it is reachable WordPress.
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
    if not is_wordpress(home):
        summary["error"] = "not a WordPress site (fingerprint absent)"
        stats["dealers_skipped_non_family"] += 1
        return summary

    # 2) STRATEGY A — Vehica REST (the clean JSON multiplier), then B — HTML cards.
    vehicles: list[Vehicle] = []
    strategy = chosen_path = theme_key = None
    pages = 0
    vveh = await _harvest_vehica(governed_fetch, base, bare)
    if vveh is not None and len(vveh) > 0:
        vehicles = vveh
        strategy = "vehica_rest"
        chosen_path = VEHICA_CARS_ENDPOINT
        pages = 1
    else:
        hveh, chosen_path, theme_key, pages = await _harvest_html(
            governed_fetch, base, bare, given_path, max_pages)
        if hveh:
            vehicles = hveh
            strategy = "html_cards"

    if not vehicles:
        summary["error"] = ("WordPress, but no inventory surface yielded cars "
                            "(no Vehica REST; no known card theme on listing slugs)")
        stats["dealers_empty"] += 1
        return summary

    summary["is_member"] = True
    summary["strategy"] = strategy
    summary["path"] = chosen_path
    summary["theme"] = theme_key
    summary["pages"] = pages
    stats["dealers_member"] += 1
    stats[f"strategy_{strategy}"] = stats.get(f"strategy_{strategy}", 0) + 1

    # 3) resolve / upsert the owning dealer entity.
    dealer = await upsert_dealer_by_host(conn, geo, bare)
    if dealer is None:
        summary["error"] = "could not resolve owning dealer"
        stats["dealers_failed"] += 1
        return summary
    summary["dealer_cdp"] = dealer["cdp_code"]

    # 4) ingest this dealer's harvest (idempotent, delta-aware).
    before_new = stats["new_cars"]
    await ingest_dealer_vehicles(conn, dealer["entity_ulid"], vehicles, stats)
    summary["vehicles"] = len({v.deep_link for v in vehicles})
    summary["new"] = stats["new_cars"] - before_new
    stats["dealers_harvested"] += 1
    stats["harvested_pairs"].update(
        (dealer["entity_ulid"], v.deep_link) for v in vehicles if v.deep_link)
    return summary


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
async def candidate_hosts_from_db(conn: asyncpg.Connection, limit: int) -> list[str]:
    """Pull dealer website hosts from the DB as harvest candidates (own-domain only).
    We do NOT pre-fingerprint here — harvest_one_dealer confirms WordPress + an
    inventory surface per-dealer."""
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
                   "wixsite.com", "ueniweb.com", "hyundai.es", "kia.com",
                   "tesla.com", "seat.es")
    for r in rows:
        w = (r["website"] or "").strip().lower()
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
                  max_pages: int, dealer_paths: dict[str, str] | None = None) -> dict:
    conn = await asyncpg.connect(DSN)
    fetcher = FamilyFetcher()
    stats = {
        "dealers_requested": 0, "dealers_member": 0, "dealers_harvested": 0,
        "dealers_skipped_non_family": 0, "dealers_empty": 0, "dealers_failed": 0,
        "cars_ingested": 0, "new_cars": 0, "new_events": 0,
        "harvested_pairs": set(), "summaries": [],
    }
    dealer_paths = dealer_paths or {}

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
                  f"(WordPress + inventory surface confirmed per-dealer).")
        stats["dealers_requested"] = len(dealers)
        print(f"[{FAMILY_KEY}] family={FAMILY_NAME}")
        print(f"[{FAMILY_KEY}] governor paces each dealer host independently "
              f"(per-host token bucket). ONE recipe -> {len(dealers)} dealers.")

        for host in dealers:
            summary = await harvest_one_dealer(
                conn, geo, governed_fetch, fetcher, host,
                dealer_paths.get(_bare(host)), max_pages, stats)
            stats["summaries"].append(summary)
            tag = (summary["strategy"] or "non-member")
            print(f"[{FAMILY_KEY}]   {summary['host']:30s} {tag:12s} "
                  f"vehicles={summary['vehicles']:3d} new={summary['new']:3d} "
                  f"pages={summary['pages']}" +
                  (f"  theme={summary['theme']}" if summary.get("theme") else "") +
                  (f"  ERR={summary['error']}" if summary.get("error") else ""))
            last_http = fetcher.last_status

        # Recipe: ONE file for the WHOLE family (keyed by the family, not a dealer).
        recipe_path = write_recipe(FAMILY_KEY, FAMILY_RECIPE)
        print(f"[{FAMILY_KEY}] family recipe written: {recipe_path}")

        # VAM count quorum for this family slice — like-with-like, run-scoped:
        #   harvested_pairs  = distinct (dealer, deep_link) pulled this run (harvest truth)
        #   db_family_vehicles = those same pairs read back from the DB (persist truth)
        #   cars_ingested_distinct = the same harvested distinct count (ingest path)
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
    print("\n" + "=" * 66)
    print("WORDPRESS-DOMINATED FAMILY — LONG-TAIL HARVEST REPORT")
    print("=" * 66)
    print(f"  family               : {FAMILY_NAME}")
    print(f"  dealers requested    : {stats['dealers_requested']}")
    print(f"  family members       : {stats['dealers_member']}")
    print(f"  dealers harvested    : {stats['dealers_harvested']}")
    print(f"    via Vehica REST    : {stats.get('strategy_vehica_rest', 0)}")
    print(f"    via HTML cards     : {stats.get('strategy_html_cards', 0)}")
    print(f"  non-WordPress skipped: {stats['dealers_skipped_non_family']}")
    print(f"  no inventory surface : {stats['dealers_empty']}")
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
            print(f"    {s['host']:30s} {s['vehicles']:3d} cars  (new {s['new']:3d})  "
                  f"[{s.get('strategy')}]  cdp={s.get('dealer_cdp')}")
    print("=" * 66)


def _parse_dealer_args(raw: list[str] | None) -> tuple[list[str], dict[str, str]]:
    """Accept either 'host' or 'host=/listing-path' tokens, so a dealer with a
    non-default listing slug can pass its index explicitly."""
    if not raw:
        return ([], {})
    hosts: list[str] = []
    paths: dict[str, str] = {}
    for tok in raw:
        if "=" in tok:
            h, _, p = tok.partition("=")
            bare = re.sub(r"^www\.", "", h.strip().lower())
            hosts.append(bare)
            paths[bare] = p.strip()
        else:
            hosts.append(tok.strip())
    return (hosts, paths)


def main() -> None:
    p = argparse.ArgumentParser(
        description="WordPress-dominated family long-tail harvester (one recipe -> N dealers)")
    p.add_argument("--dealers", nargs="*", default=None,
                   help="explicit dealer hosts (e.g. autosraul.com gestiauto.es); "
                        "optionally host=/listing-path to pin a non-default slug")
    p.add_argument("--from-db", action="store_true",
                   help="pull candidate dealer hosts from the DB website column")
    p.add_argument("--limit", type=int, default=8,
                   help="max DB candidate dealers to try (with --from-db); default 8")
    p.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES,
                   help=f"max listing pages per dealer (HTML strategy); default {DEFAULT_MAX_PAGES}")
    args = p.parse_args()
    hosts, paths = _parse_dealer_args(args.dealers)
    stats = asyncio.run(harvest(hosts or None, args.from_db, args.limit,
                                args.max_pages, dealer_paths=paths))
    _print_report(stats)


if __name__ == "__main__":
    main()
