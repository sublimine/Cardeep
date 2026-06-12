"""'Unreachable' FAMILY harvester — the Tier-1 (real-browser) long-tail, end to end.

This is the THIRD long-tail family connector, sibling to
`pipeline.platform.family_dealerk_wholesale` (one byte-identical WordPress template)
and `pipeline.platform.family_generic_custom_wholesale` (bespoke per-dealer recipes).
Where those two harvest dealers whose own sites serve cleanly to a Tier-0 curl_cffi
GET, THIS module proves the HARDEST half of the mandate: the **'unreachable'**
family — 91 dealers across 86 own-site domains that the first probe
(`scripts/longtail_fingerprint.py`) marked dead/walled on a bare Tier-0 GET (DNS
dead, HTTP 403/202/503, or timeout). No Tier-0 recipe existed because the engine
that classified them never executed JS and gave up on the HTTP status code.

The family's DEFINING trait — and therefore its ONE shared recipe — is the
escalation `pipeline/engine/fetch.py` documents but does not build at Tier-0:

  Tier-0 (curl_cffi)  -> insufficient: the home page returns 403/202/JS-shell.
  Tier-1 (real browser) -> the recipe THIS family needs: a headless Chromium that
      (a) executes the page's challenge/JS, and
      (b) is judged on the RENDERED BODY, not the HTTP status — because a member of
          this family serves a FULL, parseable used-car listing under an HTTP 403
          honeypot status. The status is a lie; the body is the truth.

That status-blind body-content gate is the multiplier. ONE Tier-1 fetch technique
unlocks EVERY member of the family that a real browser can render — no per-dealer
escalation, no per-dealer engine. Re-verified adversarially 2026-06-13 across the
full 91-dealer cohort with a real Chromium (docs/_unreachable_*.json): the cohort
is overwhelmingly, genuinely walled (Cloudflare 107-byte blocks, "Robot Challenge
Screen", dead DNS, cert/connection errors) — the original 'unreachable' verdict is
CORRECT for ~99% of it. The member this recipe RECOVERS, where BOTH the original
Tier-0 probe AND a status-checking browser fail, is:

  hrmotor.com  — HR Motor (Lleida 25 / Madrid 28). Home page: HTTP 403 + 287 KB of
  real HTML. Listing `/coches-segunda-mano/`: HTTP 200, 772 KB, ~3,796 vehicles,
  byte-uniform `vercoche` cards, `/page/N/` pagination. The body-gate reads it; the
  status-gate (and the original probe) threw it away.

Ownership model (identical to the other two long-tail families — the long-tail half):
  the dealer            -> entity (already in DB; resolve by website host, touch)
  each car on its site  -> vehicle, OWNED BY that dealer (entity_ulid = dealer)

There is NO platform_listing edge: a dealer's own website is the PRIMARY source of
its own stock, not a third-party marketplace. Ownership is singular and direct.

This module mirrors `family_generic_custom_wholesale`'s spine EXACTLY — same governor
choke point, same GeoResolver load, same idempotent ON CONFLICT upserts, same
NEW-delta events, same VAM count quorum, same S-HEALTH heartbeat + breaker, same
family recipe write — so even the Tier-1 long-tail flows through the ONE proven
architecture, not a fork of it. The ONLY differences from the Tier-0 families:
  1. the fetch ENGINE is a real headless Chromium (a dedicated-thread sync-Playwright
     worker driven through the governor's asyncio.to_thread seam), and
  2. the fetch is accepted on a RENDERED-BODY gate, never on the HTTP status.

Run:  python -m pipeline.platform.family_unreachable_wholesale --dealers hrmotor.com
      python -m pipeline.platform.family_unreachable_wholesale --all --max-pages 6
"""
from __future__ import annotations

import argparse
import asyncio
import html as _htmllib
import json
import os
import queue
import re
import sys
import threading
from dataclasses import dataclass
from typing import Callable

import asyncpg

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
# harvested through this connector is attested by the same provenance key, and the
# connector is one file shared by the whole family (one recipe-spec per member).
# ---------------------------------------------------------------------------
FAMILY_KEY = "family_unreachable"
FAMILY_NAME = "'Unreachable' (Tier-1 browser-only own-site) dealer family"

# Tier-1 engine knobs. A real headless Chromium with a coherent Chrome UA + ES locale.
_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
_NAV_TIMEOUT_MS = 30000
_SETTLE_MS = 3500              # let challenge/JS settle after domcontentloaded
# The body-content gate. A page is ACCEPTED iff its rendered body is at least this
# big — REGARDLESS of HTTP status — because a family member serves a full listing
# under an HTTP 403 honeypot. A 107-byte Cloudflare block or a 39-byte JS shell
# falls below this floor and is correctly rejected.
_BODY_GATE_MIN_BYTES = 5000
DEFAULT_MAX_PAGES = 6         # proof-slice cap; the connector supports the full drain.


# ---------------------------------------------------------------------------
# Parsed shape (field names taken from the REAL card markup, not assumed).
# ---------------------------------------------------------------------------
@dataclass
class Vehicle:
    deep_link: str
    listing_ref: str | None
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    fuel: str | None
    photo_url: str | None


# ---------------------------------------------------------------------------
# Shared parsing helpers.
# ---------------------------------------------------------------------------
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
# `page.content()` re-serialises with the document encoding; accented bytes from a
# latin-1-declared page can arrive mojibaked (Di�sel/H�brido). Normalise the known
# Spanish fuel words to clean ASCII-folded forms so the DB value is stable.
_FUEL_CANON = {
    "gasolina": "Gasolina", "diésel": "Diesel", "diesel": "Diesel",
    "di�sel": "Diesel", "glp": "GLP", "gnc": "GNC",
    "híbrido": "Hibrido", "hibrido": "Hibrido", "h�brido": "Hibrido",
    "híbrido enchufable": "Hibrido enchufable", "hibrido enchufable": "Hibrido enchufable",
    "eléctrico": "Electrico", "electrico": "Electrico", "el�ctrico": "Electrico",
}


def _clean(s: str | None) -> str | None:
    if s is None:
        return None
    s = _htmllib.unescape(s)
    s = _TAG_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s).strip()
    return s or None


def _to_int(s: str | None) -> int | None:
    if not s:
        return None
    d = re.sub(r"[^\d]", "", s)
    return int(d) if d else None


def _euros_to_float(raw: str | None) -> float | None:
    """'7.990 €' / '7.990 �' -> 7990.0. Spanish thousands sep is '.'; cards show no
    cents. Strip every non-digit and read integer euros, guarding absurd tokens."""
    n = _to_int(raw)
    if n is None:
        return None
    val = float(n)
    if val < 100 or val > 5_000_000:
        return None
    return val


def _split_make_model(text: str | None) -> tuple[str | None, str | None]:
    text = _clean(text)
    if not text:
        return (None, None)
    parts = text.split()
    if len(parts) == 1:
        return (parts[0], None)
    return (parts[0], " ".join(parts[1:]))


def _canon_fuel(token: str | None) -> str | None:
    if not token:
        return None
    return _FUEL_CANON.get(token.strip().lower())


# ---------------------------------------------------------------------------
# Per-dealer parsers. Each reads ONE member's RENDERED layout, verified live
# 2026-06-13 against the real browser-rendered HTML. A parser takes
# (rendered_html, base_url) and returns list[Vehicle].
# ---------------------------------------------------------------------------
# HR Motor cards: one `<div class="vercoche ...` wrapper per car, carrying
# data-href=<PDP>; the PDP slug ends in the stable native id (`01tqx00000...`).
# The cash price is uniquely `class="h3 mb-0 font-semibold"` (the struck
# `line-through` is the pre-finance price; `desde N €/mes` is the monthly quote —
# both excluded). Specs are `rounded bg-aux` chips: km / year / CV / trans / fuel.
_HR_CARD = re.compile(r'<div class="vercoche')
_HR_HREF = re.compile(
    r'data-href="(https?://[^"]*/coches-segunda-mano/[^"]+?-([a-z0-9]{12,})/)"')
_HR_H2 = re.compile(r'<h2[^>]*title="([^"]*)"[^>]*>([^<]+)</h2>')
_HR_VERSION = re.compile(r'class="w-10/12 truncate[^"]*">\s*([^<]+?)\s*<')
_HR_CHIP = re.compile(r'class="rounded bg-aux[^"]*">\s*([^<]+?)\s*</span>')
_HR_PRICE = re.compile(r'class="h3 mb-0 font-semibold">\s*([0-9][0-9.\s]*)')
_HR_IMG = re.compile(r'<source[^>]+srcset="(https?://[^"]+?\.webp)"', re.I)
_HR_YEAR = re.compile(r'^(19|20)\d{2}$')


def parse_hrmotor(html_text: str, base: str) -> list[Vehicle]:
    """HR Motor (hrmotor.com) rendered listing. ONE parser for every HR Motor page.

    Cards are `vercoche` wrappers; the PDP `data-href` carries the native listing id
    in its trailing slug token. Title h2 = make + model head; the truncate div = the
    version. Spec chips (`rounded bg-aux`) hold km / year / CV / transmission / fuel
    in a site-stable but order-tolerant set, so we classify each chip by shape."""
    out: list[Vehicle] = []
    seen: set[str] = set()
    for frag in _HR_CARD.split(html_text)[1:]:
        hm = _HR_HREF.search(frag)
        if not hm:
            continue
        deep_link, listing_ref = hm.group(1), hm.group(2)
        if deep_link in seen:
            continue
        seen.add(deep_link)

        h2 = _HR_H2.search(frag)
        title_full = _clean(h2.group(1)) if h2 else None
        make, model = _split_make_model(_clean(h2.group(2)) if h2 else None)
        vm = _HR_VERSION.search(frag)
        version = _clean(vm.group(1)) if vm else None
        title = title_full or " ".join(b for b in (make, model, version) if b) or None

        year = km = None
        fuel = None
        for chip in (_clean(c) for c in _HR_CHIP.findall(frag)):
            if not chip:
                continue
            low = chip.lower()
            if low.endswith("km"):
                km = _to_int(chip)
            elif _HR_YEAR.match(chip):
                y = int(chip)
                if 1900 <= y <= 2100:
                    year = y
            else:
                f = _canon_fuel(chip)
                if f is not None:
                    fuel = f

        pm = _HR_PRICE.search(frag)
        price = _euros_to_float(pm.group(1) if pm else None)
        img = _HR_IMG.search(frag)
        out.append(Vehicle(
            deep_link=deep_link, listing_ref=listing_ref, title=title,
            make=make, model=model, year=year, km=km, price=price, fuel=fuel,
            photo_url=img.group(1) if img else None))
    return out


# ---------------------------------------------------------------------------
# Per-dealer recipe registry. Each RECOVERED member of the 'unreachable' family
# declares its OWN listing path, pagination template and parser. This registry IS
# the family's harvestable surface: ONE Tier-1 connector, N recovered members.
# `pages`: 'path' -> /page/N/ ; 'query' -> ?page=N ; 'single' -> one page.
# `prior_error` records WHY the original Tier-0 probe gave up (the wall the Tier-1
# body-gate had to clear), so the recovery is auditable.
# ---------------------------------------------------------------------------
@dataclass
class DealerRecipe:
    host: str
    listing_path: str
    parser: Callable[[str, str], list[Vehicle]]
    pages: str = "path"            # 'path' (/page/N/) | 'query' (?page=N) | 'single'
    prior_error: str = ""
    notes: str = ""


REGISTRY: dict[str, DealerRecipe] = {
    "hrmotor.com": DealerRecipe(
        host="hrmotor.com", listing_path="/coches-segunda-mano/",
        parser=parse_hrmotor, pages="path", prior_error="HTTP 403 (home honeypot)",
        notes=("Tier-0 probe saw HTTP 403 on '/' and quit. Tier-1 browser renders "
               "'/coches-segunda-mano/' at HTTP 200, 772 KB, ~3,796 vehicles; the "
               "home 403 is a honeypot status over a full body. Pagination /page/N/.")),
}


# ---------------------------------------------------------------------------
# Tier-1 fetch ENGINE — a real headless Chromium owned by ONE dedicated thread.
#
# Why a dedicated-thread sync-Playwright worker (not the async API): the spine is
# asyncpg/asyncio, and the governor's integration seam runs each fetch via
# `asyncio.to_thread(sync_callable, url)`. A sync-Playwright instance is bound to the
# thread that created it, so we give the browser its OWN long-lived thread and a
# request queue; `fetch(url)` is then a plain BLOCKING call that the governor can run
# off the event loop exactly like the curl_cffi families' `fetch`. One browser, one
# context, one cookie jar for the whole drain — the Tier-1 analogue of the Tier-0
# fingerprint-coherent session.
# ---------------------------------------------------------------------------
class BrowserFetcher:
    """A persistent headless Chromium driven through a single worker thread.

    `fetch(url)` returns the RENDERED HTML (status-blind body gate applied by the
    caller via `last_status`). Raises on a body that falls below the gate so the
    governor/breaker sees a genuine wall as a failure, never a silent empty body."""

    def __init__(self) -> None:
        self._q: queue.Queue = queue.Queue()
        self._ready = threading.Event()
        self._start_err: Exception | None = None
        self.last_status: int | None = None
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._ready.wait(90)
        if self._start_err is not None:
            raise self._start_err

    def _run(self) -> None:
        try:
            from playwright.sync_api import sync_playwright
        except Exception as e:  # noqa: BLE001
            self._start_err = RuntimeError(
                "Tier-1 engine needs Playwright + a Chromium build "
                "(pip install playwright && python -m playwright install chromium): "
                f"{e}")
            self._ready.set()
            return
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                ctx = browser.new_context(locale="es-ES", user_agent=_UA)
                self._ready.set()
                while True:
                    item = self._q.get()
                    if item is None:
                        break
                    url, reply = item
                    page = None
                    try:
                        page = ctx.new_page()
                        resp = page.goto(url, wait_until="domcontentloaded",
                                         timeout=_NAV_TIMEOUT_MS)
                        page.wait_for_timeout(_SETTLE_MS)
                        html = page.content()
                        status = resp.status if resp is not None else None
                        reply.put((status, html, None))
                    except Exception as e:  # noqa: BLE001
                        reply.put((None, None, e))
                    finally:
                        if page is not None:
                            try:
                                page.close()
                            except Exception:  # noqa: BLE001
                                pass
                browser.close()
        except Exception as e:  # noqa: BLE001
            self._start_err = e
            self._ready.set()

    def fetch(self, url: str) -> str:
        """Synchronous render of `url` -> HTML (runs off the event loop via the
        governor's to_thread). Status-blind: a body that clears the gate is returned
        even under a 403 honeypot; a body below the gate raises (a real wall)."""
        reply: queue.Queue = queue.Queue()
        self._q.put((url, reply))
        status, html, err = reply.get()
        self.last_status = status
        if err is not None:
            raise RuntimeError(f"browser fetch failed on {url}: {err}")
        if not html or len(html) < _BODY_GATE_MIN_BYTES:
            raise RuntimeError(
                f"body-gate reject on {url}: status={status} "
                f"bytes={len(html) if html else 0} (< {_BODY_GATE_MIN_BYTES}; wall)")
        return html

    def close(self) -> None:
        self._q.put(None)


# ---------------------------------------------------------------------------
# The family recipe — ONE asset shared by the family, carrying every member's spec.
# ---------------------------------------------------------------------------
def _build_family_recipe() -> dict:
    members = {}
    for host, rc in REGISTRY.items():
        members[host] = {
            "listing_path": rc.listing_path,
            "pagination": {
                "path": "/page/N/ until a page yields no new cards",
                "query": "?page=N until a page yields no new cards",
                "single": "single listing page",
            }[rc.pages],
            "parser": rc.parser.__name__,
            "prior_tier0_error": rc.prior_error,
            "notes": rc.notes,
        }
    return {
        "version": 1,
        "source": FAMILY_KEY,
        "family": FAMILY_NAME,
        "scope": ("long-tail dealer OWN-SITE inventory that is UNREACHABLE at Tier-0 "
                  "(curl_cffi GET); recovered with a Tier-1 real-browser render"),
        "engine": "playwright_chromium_headless(real browser, JS executed)",
        "access": ("Tier-1: a real headless Chromium executes the page's challenge/JS. "
                   "No proxy/residential egress used here — the recovered members serve "
                   "a full body that a plain Chromium renders; the residential-egress "
                   "anti-detect path (camoufox/BotBrowser) remains the documented next "
                   "rung for the still-walled majority (Cloudflare/DataDome/dead DNS)."),
        "data_surface": "dealer_site_html_rendered",
        "acceptance_gate": ("STATUS-BLIND body-content gate: a page is accepted iff its "
                            f"rendered body >= {_BODY_GATE_MIN_BYTES} bytes, REGARDLESS of "
                            "HTTP status — a family member serves a full used-car listing "
                            "under an HTTP 403 honeypot status. The status is a lie; the "
                            "body is the truth. This is what the original Tier-0 probe, "
                            "which gave up on the status code, could not see."),
        "fingerprint": ("FAMILY = 'unreachable at Tier-0'. Membership is the negative "
                        "fingerprint (Tier-0 GET returns dead DNS / HTTP 403/202/503 / "
                        "timeout) PLUS a Tier-1 render that clears the body-gate. The 91 "
                        "-dealer cohort is overwhelmingly, genuinely walled (re-verified "
                        "2026-06-13: Cloudflare blocks, Robot Challenge screens, dead DNS, "
                        "cert/connection errors); recovered members are curated here."),
        "ownership": "vehicle.entity_ulid = the DEALER itself (own-site stock; no marketplace edge)",
        "multiplier": ("ONE Tier-1 fetch technique (real-browser render + status-blind "
                       "body-gate) unlocks EVERY family member a browser can render — no "
                       "per-dealer engine, no per-dealer escalation. The connector spine "
                       "(cage/governor/health/VAM/delta) is shared with the Tier-0 "
                       "families, so the hardest long-tail flows through ONE architecture."),
        "members": members,
    }


# ---------------------------------------------------------------------------
# DB layer — idempotent upserts mirroring family_generic_custom_wholesale (no edge).
# ---------------------------------------------------------------------------
async def resolve_dealer_for_host(conn: asyncpg.Connection, host: str) -> dict | None:
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


async def upsert_dealer_by_host(conn: asyncpg.Connection, host: str) -> dict | None:
    """Return the owning dealer entity for `host`, stamping the family provenance.
    Preferred path: the dealer is already in the DB (matched by website host).
    Fallback: mint a minimal domain-keyed entity so the harvest still has a real
    owner (province NULL; the cdp_code carries the bare-domain identity)."""
    existing = await resolve_dealer_for_host(conn, host)
    if existing:
        await conn.execute("UPDATE entity SET last_seen = now() WHERE entity_ulid = $1",
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
# Per-dealer harvest: render-drain pages with the dealer's parser -> ingest.
# ---------------------------------------------------------------------------
def _page_url(base: str, path: str, scheme: str, page: int) -> str:
    if page <= 1:
        return base + path
    if scheme == "path":
        return f"{base}{path.rstrip('/')}/page/{page}/"
    if scheme == "query":
        sep = "&" if "?" in path else "?"
        return f"{base}{path}{sep}page={page}"
    return base + path  # 'single' never paginates


async def harvest_one_dealer(conn: asyncpg.Connection, governed_fetch,
                             fetcher: BrowserFetcher, rc: DealerRecipe,
                             max_pages: int, stats: dict) -> dict:
    bare = re.sub(r"^www\.", "", rc.host.lower())
    summary = {"host": bare, "vehicles": 0, "new": 0, "dealer_cdp": None,
               "pages": 0, "path": rc.listing_path, "prior_error": rc.prior_error,
               "first_status": None}

    base = f"https://www.{bare}"
    listing_url = base + rc.listing_path
    try:
        html_text = await governed_fetch(listing_url)
    except Exception:
        base = f"https://{bare}"
        listing_url = base + rc.listing_path
        try:
            html_text = await governed_fetch(listing_url)
        except Exception as e:
            summary["error"] = f"listing render failed (still walled): {e}"
            stats["dealers_failed"] += 1
            return summary
    summary["first_status"] = fetcher.last_status

    cards = rc.parser(html_text, base)
    if not cards:
        summary["error"] = "rendered listing yielded no cards (layout changed/empty)"
        stats["dealers_empty"] += 1
        return summary
    all_vehicles: list[Vehicle] = list(cards)
    summary["pages"] = 1

    if rc.pages in ("path", "query"):
        seen_links = {v.deep_link for v in cards}
        page = 2
        while page <= max_pages:
            url = _page_url(base, rc.listing_path, rc.pages, page)
            try:
                ph = await governed_fetch(url)
            except Exception:
                break
            pcards = rc.parser(ph, base)
            fresh = [c for c in pcards if c.deep_link not in seen_links]
            if not fresh:
                break
            for c in fresh:
                seen_links.add(c.deep_link)
            all_vehicles.extend(fresh)
            summary["pages"] = page
            page += 1

    dealer = await upsert_dealer_by_host(conn, bare)
    if dealer is None:
        summary["error"] = "could not resolve owning dealer"
        stats["dealers_failed"] += 1
        return summary
    summary["dealer_cdp"] = dealer["cdp_code"]

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
async def harvest(dealers: list[str] | None, run_all: bool, max_pages: int) -> dict:
    conn = await asyncpg.connect(DSN)
    stats = {
        "dealers_requested": 0, "dealers_harvested": 0,
        "dealers_empty": 0, "dealers_failed": 0, "dealers_unknown": 0,
        "cars_ingested": 0, "new_cars": 0, "new_events": 0,
        "harvested_pairs": set(), "summaries": [],
    }

    if await is_open(conn, FAMILY_KEY):
        print(f"[{FAMILY_KEY}] breaker OPEN; skipping drain (graceful degradation).")
        await conn.close()
        return {"skipped": True, "reason": "breaker_open", "source_key": FAMILY_KEY}

    # Resolve targets BEFORE spinning up the (expensive) browser engine.
    if run_all or not dealers:
        targets = list(REGISTRY.keys())
    else:
        targets = []
        for d in dealers:
            bare = re.sub(r"^www\.", "",
                          re.sub(r"^https?://", "", d.strip().lower())).split("/")[0]
            if bare in REGISTRY:
                targets.append(bare)
            else:
                print(f"[{FAMILY_KEY}] '{d}' not a recovered member of the "
                      f"'unreachable' family registry; skipping.")
                stats["dealers_unknown"] += 1
    stats["dealers_requested"] = len(targets)

    if not targets:
        print(f"[{FAMILY_KEY}] no recovered targets to harvest.")
        await conn.close()
        stats.pop("harvested_pairs", None)
        return stats

    fetcher = BrowserFetcher()  # Tier-1 engine: one Chromium, one context, one thread.
    gov = governor()
    governed_fetch = gov.wrap_fetch_text(fetcher.fetch)

    last_http: int | None = None
    try:
        # GeoResolver loaded for spine parity (the dealer is resolved from the DB, so no
        # geo inference is needed here, but loading it keeps the contract identical and
        # validates the geo tables exist).
        await GeoResolver.load(conn)

        print(f"[{FAMILY_KEY}] family={FAMILY_NAME}")
        print(f"[{FAMILY_KEY}] Tier-1 engine: headless Chromium (real browser, JS "
              f"executed), status-blind body-gate >= {_BODY_GATE_MIN_BYTES} bytes.")
        print(f"[{FAMILY_KEY}] governor paces each dealer host independently "
              f"(per-host token bucket). ONE recipe -> {len(targets)} recovered dealers.")

        for host in targets:
            rc = REGISTRY[host]
            summary = await harvest_one_dealer(
                conn, governed_fetch, fetcher, rc, max_pages, stats)
            stats["summaries"].append(summary)
            print(f"[{FAMILY_KEY}]   {summary['host']:24s} "
                  f"prior={summary.get('prior_error'):22s} "
                  f"render_status={summary.get('first_status')} "
                  f"pages={summary.get('pages')} vehicles={summary['vehicles']:3d} "
                  f"new={summary['new']:3d}" +
                  (f"  ERR={summary['error']}" if summary.get("error") else ""))
            last_http = fetcher.last_status

        recipe_path = write_recipe(FAMILY_KEY, _build_family_recipe())
        print(f"[{FAMILY_KEY}] family recipe written: {recipe_path}")

        # VAM count quorum (like-with-like) for this family slice:
        #   harvested_pairs    = distinct (dealer, deep_link) pulled this run (harvest truth)
        #   db_family_vehicles = vehicles in DB owned by the dealers this source attests,
        #                        scoped to the deep_links pulled this run (DB read truth)
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

        run_ok = (stats["dealers_harvested"] > 0 and verdict != "REFUTED")
        run_error = None if run_ok else f"VAM verdict {verdict}"
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
        fetcher.close()
        await conn.close()


def _print_report(stats: dict) -> None:
    if stats.get("skipped"):
        print(f"\n[{FAMILY_KEY}] SKIPPED: {stats.get('reason')}")
        return
    print("\n" + "=" * 70)
    print("'UNREACHABLE' FAMILY — TIER-1 BROWSER LONG-TAIL HARVEST REPORT")
    print("=" * 70)
    print(f"  family               : {FAMILY_NAME}")
    print(f"  dealers requested    : {stats['dealers_requested']}")
    print(f"  dealers harvested    : {stats['dealers_harvested']}")
    print(f"  empty inventory      : {stats['dealers_empty']}")
    print(f"  failed (still walled): {stats['dealers_failed']}")
    print(f"  cars ingested        : {stats['cars_ingested']} ({stats['new_cars']} new)")
    print(f"  NEW delta events     : {stats['new_events']}")
    print(f"  family dealers attested (entity_source): {stats.get('family_dealers_attested')}")
    print("  --- VAM count quorum (like-with-like, this slice) ---")
    print(f"  harvested_pairs      : {stats.get('harvested_pairs_n')}")
    print(f"  db_family_vehicles   : {stats.get('db_family_vehicles')}")
    print(f"  VAM verdict          : {stats.get('verdict')}")
    print(f"  health / breaker     : {stats.get('health_status')} / {stats.get('breaker_state')}")
    print(f"  recipe               : {stats.get('recipe_path')}")
    print("  --- the multiplier (ONE Tier-1 recipe -> N recovered dealers) ---")
    for s in stats.get("summaries", []):
        print(f"    {s['host']:24s} {s['vehicles']:3d} cars (new {s['new']:3d})  "
              f"render={s.get('first_status')}  cdp={s.get('dealer_cdp')}"
              + (f"  [{s['error']}]" if s.get("error") else ""))
    print("=" * 70)


def main() -> None:
    p = argparse.ArgumentParser(
        description="'Unreachable' Tier-1 browser long-tail family harvester "
                    "(one real-browser recipe -> N recovered dealers)")
    p.add_argument("--dealers", nargs="*", default=None,
                   help="explicit recovered hosts from the registry (e.g. hrmotor.com)")
    p.add_argument("--all", action="store_true",
                   help="harvest every recovered member of the family")
    p.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES,
                   help=f"max listing pages per dealer; default {DEFAULT_MAX_PAGES}")
    args = p.parse_args()
    stats = asyncio.run(harvest(args.dealers, args.all, args.max_pages))
    _print_report(stats)


if __name__ == "__main__":
    main()
