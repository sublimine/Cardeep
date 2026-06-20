"""motor.es CENSUS adapter — Vector 1 (marketplace-as-census), §1.

Enumerates the professional sellers in motor.es's own dealer directory
(``/concesionarios/`` — paginated, ~536 dealers) as first-class entities, the same
seller-census discipline applied to autocasion. The directory is FREE to a Chrome UA and,
crucially, carries the **province in the URL path** (``/concesionarios/{prov}/{slug}/``), so
every dealer is geo-resolvable from enumeration alone — no per-dealer fetch is needed for
the core census.

Identity dedups at the cdp_code level against ``motor_es_wholesale`` dealers: the cdp is
minted from ``domain=None + name + municipality + address='concesionario:{prov}/{slug}'`` —
the same inputs ``motor_es_wholesale.cdp_code_dealer`` uses — so a dealer already known via
inventory harvest collapses on ``ON CONFLICT (cdp_code)`` instead of duplicating; one the
wholesale never saw mints a fresh cdp = the census's real new contribution.

Run via the canonical pipeline:  python -m pipeline.discover motor_es_census
"""
from __future__ import annotations

import logging
import re

from pipeline.sources.autocasion_census import (  # generic helpers (DRY)
    _http_get,
    _norm_phone_es,
    _province_from_postcode,
)
from pipeline.sources.base import DiscoveredEntity, SourceAdapter

log = logging.getLogger(__name__)

_BASE = "https://www.motor.es"
_DIR = "https://www.motor.es/concesionarios/"
_DIR_PAGE = "https://www.motor.es/concesionarios/{page}"
# dealer link: /concesionarios/{prov_slug}/{dealer_slug}/  — prov_slug is one of the 52 below.
_DEALER_RE = re.compile(r'/concesionarios/([a-z0-9\-]+)/([a-z0-9\-]+)/')
# anchor text right after the dealer href, e.g. >Ankara Motor (Alicante)<
_ANCHOR_NAME_RE = (
    r'/concesionarios/{prov}/{slug}/"[^>]*>\s*([^<]{{2,80}}?)\s*<')

# motor.es province slug -> INE 2-digit code (closed set; motor.es uses its own slug forms).
_PROV_INE = {
    "alava": "01", "albacete": "02", "alicante": "03", "almeria": "04", "asturias": "33",
    "avila": "05", "badajoz": "06", "baleares": "07", "barcelona": "08", "burgos": "09",
    "caceres": "10", "cadiz": "11", "cantabria": "39", "castellon": "12", "ceuta": "51",
    "ciudad-real": "13", "cordoba": "14", "a-coruna": "15", "la-coruna": "15", "cuenca": "16",
    "girona": "17", "gerona": "17", "granada": "18", "guadalajara": "19", "guipuzcoa": "20",
    "gipuzkoa": "20", "huelva": "21", "huesca": "22", "jaen": "23", "leon": "24",
    "lleida": "25", "lerida": "25", "lugo": "27", "madrid": "28", "malaga": "29",
    "melilla": "52", "murcia": "30", "navarra": "31", "ourense": "32", "orense": "32",
    "palencia": "34", "las-palmas": "35", "pontevedra": "36", "la-rioja": "26",
    "salamanca": "37", "santa-cruz-de-tenerife": "38", "tenerife": "38", "segovia": "40",
    "sevilla": "41", "soria": "42", "tarragona": "43", "teruel": "44", "toledo": "45",
    "valencia": "46", "valladolid": "47", "vizcaya": "48", "bizkaia": "48", "zamora": "49",
    "zaragoza": "50",
}


def _clean_name(raw: str | None, prov_slug: str) -> str | None:
    """Strip the trailing ' (Province)' suffix the directory anchor appends, so the name
    matches the seller.name motor_es_wholesale mints with (cdp dedup alignment)."""
    if not raw:
        return None
    name = re.sub(r"\s*\([^)]*\)\s*$", "", raw).strip()
    return name or None


def parse_directory_page(html: str) -> dict[tuple[str, str], str | None]:
    """Return {(prov_slug, dealer_slug): anchor_name} for every dealer on a directory page,
    excluding province index links (slug segment empty / non-dealer)."""
    out: dict[tuple[str, str], str | None] = {}
    for prov_slug, slug in _DEALER_RE.findall(html):
        if prov_slug not in _PROV_INE:
            continue  # not a province directory segment -> not a dealer link
        if slug in _PROV_INE or slug.isdigit():
            continue  # nested province / pager number, not a dealer
        key = (prov_slug, slug)
        if key in out:
            continue
        m = re.search(_ANCHOR_NAME_RE.format(prov=re.escape(prov_slug), slug=re.escape(slug)), html)
        out[key] = _clean_name(m.group(1) if m else None, prov_slug)
    return out


def parse_dealer_page(html: str) -> dict | None:
    """Extract the dealer's identity+contact from its /concesionarios/{prov}/{slug}/ page
    (motor.es uses itemprop microdata + an <h1> name, not a clean AutoDealer JSON-LD).

    The clean name is the page <h1> (with the ' (PROVINCE)' suffix stripped); city, postcode,
    street and phone come from itemprop microdata. None if the name cannot be recovered.
    """
    def ip(name: str) -> str | None:
        m = (re.search(r'itemprop=["\']' + name + r'["\'][^>]*>([^<]{1,80})', html)
             or re.search(r'itemprop=["\']' + name + r'["\'][^>]*content=["\']([^"\']{1,80})', html))
        return m.group(1).strip() if m else None

    h1 = re.search(r'<h1[^>]*>\s*([^<]{2,80})', html)
    raw_name = h1.group(1).strip() if h1 else None
    name = re.sub(r"\s*\([^)]*\)\s*$", "", raw_name).strip() if raw_name else None
    if not name:
        return None
    return {
        "name": name,
        "street": ip("streetAddress"),
        "city": ip("addressLocality"),
        "postcode": ip("postalCode"),
        "phone": _norm_phone_es(ip("telephone")),
    }


class MotorEsCensusAdapter(SourceAdapter):
    """Enumerates professional sellers from the motor.es dealer directory.

    ``fetch()`` enriches each dealer from its profile page (city/phone needed for cdp dedup
    and clustering); for the full ~536-dealer run prefer the concurrent batched runner
    ``scripts.census_motor_es_batched`` (the sequential fetch here honours the SourceAdapter
    contract and is fine for capped/sampled runs).
    """

    source_key = "motor_es_census"

    def __init__(self, max_pages: int = 40, max_dealers: int | None = None) -> None:
        self._max_pages = max_pages
        self._max_dealers = max_dealers
        self._dealers: dict[tuple[str, str], str | None] | None = None
        self.excluded_count = 0

    def _crawl(self) -> dict[tuple[str, str], str | None]:
        if self._dealers is not None:
            return self._dealers
        found: dict[tuple[str, str], str | None] = {}
        empty_streak = 0
        for page in range(1, self._max_pages + 1):
            url = _DIR if page == 1 else _DIR_PAGE.format(page=page)
            try:
                html = _http_get(url, timeout=30)
            except Exception as exc:  # noqa: BLE001 — stop honestly, do not silently truncate
                log.warning("motor_es_census: directory page %d failed (%s) — stop", page, exc)
                break
            page_dealers = parse_directory_page(html)
            new = {k: v for k, v in page_dealers.items() if k not in found}
            if not new:
                empty_streak += 1
                if empty_streak >= 2:  # two consecutive no-new pages == end of directory
                    break
            else:
                empty_streak = 0
                found.update(new)
        self._dealers = found
        return found

    def declared_count(self) -> int | None:
        return len(self._crawl())

    def entity_from(self, prov_slug: str, slug: str, rec: dict) -> DiscoveredEntity:
        """Build the DiscoveredEntity for one enriched dealer (shared with the batched
        runner). Province from the URL prov_slug (authoritative), confirmed by postcode."""
        prov = _PROV_INE.get(prov_slug) or _province_from_postcode(rec.get("postcode"))
        return DiscoveredEntity(
            kind="compraventa", source_key=self.source_key,
            source_ref=f"{prov_slug}/{slug}",
            legal_name=rec["name"], trade_name=rec["name"],
            province_name=prov, municipality_name=rec.get("city"),
            # cdp identity matched to motor_es_wholesale.cdp_code_dealer
            address=f"concesionario:{prov_slug}/{slug}",
            postcode=rec.get("postcode"), phone=rec.get("phone"), website=None,
            extra={"source_group": "marketplace_census", "vector": 1,
                   "prov_slug": prov_slug, "dealer_slug": slug,
                   "street": rec.get("street"),
                   "profile_url": f"{_BASE}/concesionarios/{prov_slug}/{slug}/"})

    def fetch(self) -> list[DiscoveredEntity]:
        out: list[DiscoveredEntity] = []
        dealers = list(self._crawl().items())
        if self._max_dealers is not None:
            dealers = dealers[: self._max_dealers]
        for (prov_slug, slug), _anchor in dealers:
            url = f"{_BASE}/concesionarios/{prov_slug}/{slug}/"
            try:
                html = _http_get(url)
            except Exception:  # noqa: BLE001 — dead/blocked dealer page is an expected outcome
                self.excluded_count += 1
                continue
            rec = parse_dealer_page(html)
            if not rec:
                self.excluded_count += 1
                continue
            out.append(self.entity_from(prov_slug, slug, rec))
        return out
