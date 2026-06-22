"""VECTOR 4b — axesor.es CNAE-4511/4520 dealer census (official mercantile directory).

axesor.es publishes a free, server-rendered company file (``/Informes-Empresas/{id}/…``)
for every Spanish mercantile entity, each carrying a JSON-LD ``Organization`` block
(name, ``taxID`` = CIF, full ``PostalAddress`` + ``GeoCoordinates``) plus an HTML row
``CNAE</th><td>4511 …``. The directory is browsable geographically:
``/directorio-informacion-empresas/empresas-de-{Provincia}`` lists that province's
municipalities, and each ``…/informacion-empresas-de-{Municipio}/{page}`` paginates the
companies registered there. There is **no CNAE pre-filter** in the directory, so the only
honest way to a CNAE-scoped census is: walk the geographic frontier -> fetch each ficha ->
keep only the ones whose CNAE is automotive sales (4511 light motor vehicles, 4520 repair).

Why it matters (orthogonality, §2): like BORME this source's capture mechanism is
*legal/fiscal* (mercantile registry mirror), not commercial — a dealer's presence here does
not correlate with its online footprint, so it anchors the exhaustiveness denominator and
yields entities the marketplace censuses never see. Unlike BORME it ships the **CIF** and a
**precise CNAE** per company, so the kind is exact (4511 -> compraventa, 4520 -> garaje)
rather than an objeto-social guess.

Transport: free to a Chrome TLS fingerprint (curl_cffi chrome131). robots.txt (verified
2026-06-22) allows ``/directorio-informacion-empresas/`` and ``/Informes-Empresas/``; the
disallowed ``/buscar/``, ``/IE/`` etc. are never touched. Pages are clean UTF-8.

Bounded for proof runs via env:
  * CARDEEP_AXESOR_MAX_PROV    — provinces to walk (default 2; full = 52)
  * CARDEEP_AXESOR_MAX_FICHAS  — hard cap on total ficha fetches (default 200)
  * CARDEEP_AXESOR_MAX_MUNI    — municipalities per province (default 8; full = all)
  * CARDEEP_AXESOR_MAX_PAGES   — listing pages per municipality (default 3; full = the
                                 last page number the listing itself advertises)
  * CARDEEP_AXESOR_SLEEP       — polite delay between requests (default 0.25 s)

Isolates cleanly if axesor is unreachable (returns []), exactly like borme_cnae.

Run via the canonical pipeline:  python -m pipeline.discover axesor_cnae
"""
from __future__ import annotations

import json
import logging
import os
import re
import time

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

log = logging.getLogger(__name__)

SOURCE_KEY = "axesor_cnae"

_HOST = "https://www.axesor.es"
_PROV_URL = _HOST + "/directorio-informacion-empresas/empresas-de-{prov}"

# Automotive-sales CNAE codes we keep, mapped to the cardeep kind. Everything else is
# dropped at parse time (the directory has no CNAE pre-filter).
#   4511 — Venta de automóviles y vehículos de motor ligeros  -> compraventa
#   4520 — Mantenimiento y reparación de vehículos de motor    -> garaje
_KEEP_CNAE: dict[str, str] = {"4511": "compraventa", "4520": "garaje"}

# The 52 province directory slugs, scraped live from /directorio-informacion-empresas
# (verified 2026-06-22). Closed set — Spain has exactly 52 provinces — so embedding it is
# safer and cheaper than re-deriving the root each run.
_PROVINCES: tuple[str, ...] = (
    "Alava", "Albacete", "Alicante", "Almeria", "Asturias", "Avila", "Badajoz",
    "Baleares", "Barcelona", "Burgos", "Caceres", "Cadiz", "Cantabria", "Castellon",
    "Ceuta", "Ciudad-Real", "Cordoba", "Cuenca", "Girona", "Granada", "Guadalajara",
    "Guipuzcoa", "Huelva", "Huesca", "Jaen", "La-Coruna", "La-Rioja", "Las-Palmas",
    "Leon", "Lleida", "Lugo", "Madrid", "Malaga", "Melilla", "Murcia", "Navarra",
    "Orense", "Palencia", "Pontevedra", "Salamanca", "Santa-Cruz-De-Tenerife",
    "Segovia", "Sevilla", "Soria", "Tarragona", "Teruel", "Toledo", "Valencia",
    "Valladolid", "Vizcaya", "Zamora", "Zaragoza",
)

_LDJSON_RE = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S)
# CNAE is a server-rendered HTML detail row: CNAE</th><td …>4511 Venta de …</td>
_CNAE_RE = re.compile(r'CNAE</th>\s*<td[^>]*>\s*(\d{3,4})\b', re.S)
# Ficha links inside a listing page: /Informes-Empresas/{id}/{SLUG}.html
_FICHA_RE = re.compile(r'/Informes-Empresas/(\d+)/([^"\'<>\s]+?\.html)')
# Municipality sub-listings advertised by a province root.
_MUNI_RE = re.compile(
    r'/directorio-informacion-empresas/empresas-de-[A-Za-z\-]+'
    r'/informacion-empresas-de-([A-Za-z0-9\-]+)/\d+')


def _http_get(url: str, *, timeout: int = 30, retries: int = 3) -> str | None:
    """GET via a Chrome TLS fingerprint. Returns decoded text, or None on 404 / give-up.

    A 404 is a definitive "not there" (dead ficha / page past the last) — no retries.
    Transient errors back off. The page is UTF-8 (verified); decode is lossless-tolerant.
    """
    from curl_cffi import requests as creq

    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            r = creq.get(url, impersonate="chrome131", timeout=timeout)
            if r.status_code == 404:
                return None
            if r.status_code != 200:
                last_err = RuntimeError(f"HTTP {r.status_code}")
                time.sleep(1.0 * (attempt + 1))
                continue
            return r.content.decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001 — transient network blip; retry
            last_err = e
            time.sleep(1.0 * (attempt + 1))
    log.warning("axesor_cnae: GET gave up url=%s (%s)", url, last_err)
    return None


def _clean(v) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def _organization_block(html: str) -> dict | None:
    """The first JSON-LD block whose @type is Organization (the company's own card)."""
    for block in _LDJSON_RE.findall(html):
        try:
            d = json.loads(block)
        except json.JSONDecodeError:
            continue
        if not isinstance(d, dict):
            continue
        t = d.get("@type")
        if t == "Organization" or (isinstance(t, list) and "Organization" in t):
            return d
    return None


def _province_from_postcode(postcode: str | None) -> str | None:
    """INE 2-digit province from a 5-digit postcode (authoritative)."""
    if postcode and len(postcode) >= 2 and postcode[:2].isdigit():
        cc = postcode[:2]
        if "01" <= cc <= "52":
            return cc
    return None


def _to_float(v) -> float | None:
    if v in (None, ""):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parse_axesor_ficha(html: str) -> dict | None:
    """Pure parser: an axesor ficha HTML -> normalized record, or None.

    Returns None when the ficha is not an automotive-sales company (CNAE not in
    {4511, 4520}) or when the Organization JSON-LD is missing — i.e. the caller keeps
    only what this returns. The returned dict carries everything ``fetch`` needs:
    ``cnae, kind, name, cif, street, locality, region, postcode, lat, lon``.

    No network. Deterministic. Unit-tested against real fixtures.
    """
    cnae_m = _CNAE_RE.search(html)
    cnae = cnae_m.group(1) if cnae_m else None
    if cnae not in _KEEP_CNAE:
        return None  # pharmacy / construction / real-estate / … — dropped honestly

    org = _organization_block(html)
    if not org:
        return None  # no machine-readable company card -> useless for the seal

    addr = org.get("address") or {}
    if isinstance(addr, list):
        addr = addr[0] if addr else {}
    geo = org.get("geo") or {}
    if isinstance(geo, list):
        geo = geo[0] if geo else {}

    name = _clean(org.get("name"))
    if not name:
        return None  # an unnamed entity cannot be sealed

    return {
        "cnae": cnae,
        "kind": _KEEP_CNAE[cnae],
        "name": name,
        "cif": _clean(org.get("taxID")),
        "street": _clean(addr.get("streetAddress")),
        "locality": _clean(addr.get("addressLocality")),
        "region": _clean(addr.get("addressRegion")),
        "postcode": _clean(addr.get("postalCode")),
        "lat": _to_float(geo.get("latitude")),
        "lon": _to_float(geo.get("longitude")),
    }


def _ficha_urls(listing_html: str) -> list[str]:
    """Distinct ficha URLs found in a listing page, in document order."""
    seen: dict[str, None] = {}
    for cid, slug in _FICHA_RE.findall(listing_html):
        url = f"{_HOST}/Informes-Empresas/{cid}/{slug}"
        seen.setdefault(url, None)
    return list(seen)


def _municipality_slugs(prov_html: str) -> list[str]:
    """Distinct municipality slugs a province root advertises (document order)."""
    seen: dict[str, None] = {}
    for slug in _MUNI_RE.findall(prov_html):
        seen.setdefault(slug, None)
    return list(seen)


def _last_page(listing_html: str, muni_slug: str) -> int:
    """Highest page number the listing advertises for *muni_slug* (>=1)."""
    nums = re.findall(
        rf'informacion-empresas-de-{re.escape(muni_slug)}/(\d+)', listing_html)
    return max((int(n) for n in nums), default=1)


class AxesorCnaeAdapter(SourceAdapter):
    """axesor.es geographic walk -> CNAE-4511/4520 dealer census.

    Frontier: province roots -> municipality sub-listings (paginated) -> ficha URLs.
    Each ficha is fetched and parsed; only CNAE 4511/4520 are kept. All breadth knobs
    are env-bounded so the orchestrator can run a small proof before the full sweep.
    """

    source_key = SOURCE_KEY

    def __init__(
        self,
        provinces: list[str] | None = None,
        *,
        max_prov: int | None = None,
        max_fichas: int | None = None,
        max_muni: int | None = None,
        max_pages: int | None = None,
        sleep_s: float | None = None,
    ) -> None:
        self._provinces = provinces or list(_PROVINCES)
        self._max_prov = max_prov if max_prov is not None else \
            int(os.environ.get("CARDEEP_AXESOR_MAX_PROV", "2"))
        self._max_fichas = max_fichas if max_fichas is not None else \
            int(os.environ.get("CARDEEP_AXESOR_MAX_FICHAS", "200"))
        self._max_muni = max_muni if max_muni is not None else \
            int(os.environ.get("CARDEEP_AXESOR_MAX_MUNI", "8"))
        self._max_pages = max_pages if max_pages is not None else \
            int(os.environ.get("CARDEEP_AXESOR_MAX_PAGES", "3"))
        self._sleep = sleep_s if sleep_s is not None else \
            float(os.environ.get("CARDEEP_AXESOR_SLEEP", "0.25"))
        self._entities: list[DiscoveredEntity] | None = None
        self._isolated: str | None = None
        self._fichas_seen = 0
        self.excluded_count = 0  # fetched fichas dropped (non-auto / parse miss); read by discover

    # -- frontier --------------------------------------------------------

    def _collect_ficha_urls(self) -> list[str]:
        """Walk the geographic frontier, returning distinct ficha URLs (capped).

        Order matters under a small ``max_fichas`` proof cap: the **paginated municipality
        listings** are walked FIRST (they enumerate every registered company in document
        order — deep, stable, representative), and the province root's ~35 *sample* fichas
        (a rotating, non-representative subset of big-name landing pages) only top up the
        budget afterwards. Doing the root first would burn the whole proof cap on samples
        that almost never contain an automotive dealer.
        """
        urls: dict[str, None] = {}
        root_samples: dict[str, None] = {}
        provinces = self._provinces[: self._max_prov] if self._max_prov else self._provinces
        for prov in provinces:
            if len(urls) >= self._max_fichas:
                break
            prov_html = _http_get(_PROV_URL.format(prov=prov))
            if self._sleep:
                time.sleep(self._sleep)
            if not prov_html:
                log.warning("axesor_cnae: province root unreachable prov=%s", prov)
                continue
            # Stash the root's sample fichas for later top-up (not consumed yet).
            for u in _ficha_urls(prov_html):
                root_samples.setdefault(u, None)
            munis = _municipality_slugs(prov_html)
            if self._max_muni:
                munis = munis[: self._max_muni]
            for muni in munis:
                if len(urls) >= self._max_fichas:
                    break
                last = self._walk_municipality(prov, muni, urls)
                log.info("axesor_cnae: %s/%s walked up to page %d (cum fichas %d)",
                         prov, muni, last, len(urls))
        # Top up with province-root sample fichas only if budget remains.
        for u in root_samples:
            if len(urls) >= self._max_fichas:
                break
            urls.setdefault(u, None)
        return list(urls)[: self._max_fichas]

    def _walk_municipality(self, prov: str, muni: str, urls: dict[str, None]) -> int:
        """Paginate one municipality listing, adding ficha URLs. Returns last page hit."""
        base = (f"{_HOST}/directorio-informacion-empresas/empresas-de-{prov}"
                f"/informacion-empresas-de-{muni}")
        first = _http_get(f"{base}/1")
        if self._sleep:
            time.sleep(self._sleep)
        if not first:
            return 0
        for u in _ficha_urls(first):
            urls.setdefault(u, None)
        advertised = _last_page(first, muni)
        last = min(advertised, self._max_pages) if self._max_pages else advertised
        page = 2
        while page <= last:
            if len(urls) >= self._max_fichas:
                break
            html = _http_get(f"{base}/{page}")
            if self._sleep:
                time.sleep(self._sleep)
            if not html:
                break  # 404 = past the real last page; stop walking
            for u in _ficha_urls(html):
                urls.setdefault(u, None)
            page += 1
        return page - 1

    # -- build -----------------------------------------------------------

    def _build(self) -> list[DiscoveredEntity]:
        ficha_urls = self._collect_ficha_urls()
        out: list[DiscoveredEntity] = []
        excluded = 0
        for url in ficha_urls:
            html = _http_get(url)
            self._fichas_seen += 1
            if self._sleep:
                time.sleep(self._sleep)
            if not html:
                excluded += 1
                continue
            rec = parse_axesor_ficha(html)
            if not rec:
                excluded += 1  # not CNAE 4511/4520, or no Organization card
                continue
            # Province: prefer the listing's OWN postcode (authoritative INE 2-digit);
            # fall back to addressRegion name, which geo.province_code(name) resolves.
            province = _province_from_postcode(rec.get("postcode")) or rec.get("region")
            out.append(DiscoveredEntity(
                kind=rec["kind"],
                source_key=self.source_key,
                source_ref=url,
                legal_name=rec["name"],
                trade_name=rec["name"],
                cif=rec.get("cif"),
                cnae=rec["cnae"],
                province_name=province,
                municipality_name=rec.get("locality"),  # MUST be populated for the seal
                address=rec.get("street"),
                postcode=rec.get("postcode"),
                lat=rec.get("lat"),
                lon=rec.get("lon"),
                website=None,  # axesor profile is NOT the dealer's site -> never set (dedup)
                extra={"source_group": "official_directory", "vector": 4,
                       "registry": "axesor", "ficha_url": url},
            ))
        self.excluded_count = excluded
        return out

    def _load(self) -> list[DiscoveredEntity]:
        if self._entities is not None:
            return self._entities
        try:
            self._entities = self._build()
        except Exception as e:  # noqa: BLE001
            self._isolated = f"axesor source error: {e!r}"
            self._entities = []
        if not self._entities and self._fichas_seen == 0 and self._isolated is None:
            self._isolated = "no axesor listing reachable (offline/blocked?)"
        return self._entities

    def declared_count(self) -> int | None:
        # No independent count oracle: the directory exposes no CNAE-filtered total, so we
        # honestly assert none (the VAM gate then compares fetched vs db-ingested only).
        return None

    def fetch(self) -> list[DiscoveredEntity]:
        rows = self._load()
        if self._isolated:
            print(f"[axesor_cnae] ISOLATED — {self._isolated}")
            return []
        print(f"[axesor_cnae] fichas_fetched={self._fichas_seen} kept={len(rows)} "
              f"excluded_non_auto={self.excluded_count}")
        return rows
