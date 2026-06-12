"""SEAT España official dealer network adapter.

Public site, no auth. The authoritative, geo-attributable dealer set comes from
the 51 province pages at /red-concesionarios/<province-slug> (enumerated from the
sitemap). Each province page links its dealers with the text
"Concesionarios SEAT en <Municipality> | <DealerName>", so name + municipality
parse from the link and the province comes from the page path.

Province is mapped to its INE 2-digit code from the page slug. The grouped
"islas-canarias" page is resolved per dealer from the municipality keyword
(Las Palmas -> 35, Tenerife -> 38). The 10 dealers that operate sales points in
two provinces are listed on both province pages and kept as one outlet-entity per
(dealer, province), deduplicated by (slug, province).

Verified live 2026-06-12: 51 province pages, 108 outlet rows, 98 unique dealers.
"""
from __future__ import annotations

import html
import re
import time
import urllib.request

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

_SITEMAP = "https://www.concesionarios.seat/sitemap.xml"
_PROVINCE_BASE = "https://www.concesionarios.seat/red-concesionarios/"
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/137 Safari/537.36"

# Province-page slug -> INE 2-digit province code.
_SLUG_TO_INE = {
    "alava": "01", "albacete": "02", "alicante": "03", "almeria": "04",
    "avila": "05", "badajoz": "06", "illes-balears": "07", "barcelona": "08",
    "burgos": "09", "caceres": "10", "cadiz": "11", "castellon": "12",
    "ciudad-real": "13", "cordoba": "14", "a-coruna": "15", "cuenca": "16",
    "girona": "17", "granada": "18", "guadalajara": "19", "guipuzcoa": "20",
    "huelva": "21", "huesca": "22", "jaen": "23", "leon": "24", "lleida": "25",
    "la-rioja": "26", "lugo": "27", "madrid": "28", "malaga": "29", "murcia": "30",
    "navarra": "31", "ourense": "32", "asturias": "33", "palencia": "34",
    "pontevedra": "36", "salamanca": "37", "cantabria": "39", "segovia": "40",
    "sevilla": "41", "soria": "42", "tarragona": "43", "teruel": "44",
    "toledo": "45", "valencia": "46", "valladolid": "47", "bizkaia": "48",
    "zamora": "49", "zaragoza": "50", "ceuta": "51", "melilla": "52",
}

# "islas-canarias" groups two provinces; resolve from the municipality keyword.
_CANARIAS_SLUG = "islas-canarias"
_CANARIAS_BY_MUNICIPALITY = (
    ("las palmas", "35"), ("lanzarote", "35"), ("fuerteventura", "35"),
    ("gran canaria", "35"),
    ("tenerife", "38"), ("la palma", "38"), ("gomera", "38"), ("hierro", "38"),
    ("santa cruz de tenerife", "38"),
)

_PROVINCE_SLUG_RE = re.compile(r"/red-concesionarios/([a-z0-9\-]+)</loc>")
_DEALER_LINK_RE = re.compile(r'\.dealer\.([a-z0-9\-]+)\.html">([^<]+)<')


def _get(url: str, tries: int = 4) -> str:
    """Fetch text with a small retry; the host occasionally drops the TLS handshake."""
    last: Exception | None = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": _UA})
            with urllib.request.urlopen(req, timeout=45) as r:  # noqa: S310 (trusted vendor host)
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001 (retry any transient network error)
            last = e
            time.sleep(1.5 * (i + 1))
    raise last  # type: ignore[misc]


def _clean(v) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def _parse_link_text(text: str) -> tuple[str | None, str | None]:
    """Split 'Concesionarios SEAT en <Municipality> | <DealerName>'.

    Returns (municipality, dealer_name). The municipality segment may list several
    towns separated by ',' or ' y '; the first is taken as the primary location.
    """
    t = html.unescape(text).strip()
    name = None
    municipality = None
    if "|" in t:
        left, right = t.split("|", 1)
        name = _clean(right)
    else:
        left = t
    m = re.search(r"\ben\s+(.*)$", left, flags=re.IGNORECASE)
    if m:
        towns = m.group(1)
        first = re.split(r"\s+y\s+|,", towns, maxsplit=1)[0]
        municipality = _clean(first)
    return municipality, name


def _canarias_province(municipality: str | None) -> str | None:
    """Resolve a Canary Islands dealer to its INE code (35/38) from the municipality."""
    low = (municipality or "").lower()
    for kw, code in _CANARIAS_BY_MUNICIPALITY:
        if kw in low:
            return code
    return None


class OemSeatAdapter(SourceAdapter):
    source_key = "oem_seat"

    def __init__(self) -> None:
        self._rows: list[dict] | None = None
        self.excluded_count = 0  # rows dropped because province could not be resolved

    def _province_slugs(self) -> list[str]:
        sitemap = _get(_SITEMAP)
        return sorted(set(_PROVINCE_SLUG_RE.findall(sitemap)))

    def _load(self) -> list[dict]:
        """One row per dealer link on each province page, deduplicated by (slug, province)."""
        if self._rows is not None:
            return self._rows
        rows: list[dict] = []
        seen: set[tuple[str, str]] = set()
        for slug in self._province_slugs():
            page = _get(f"{_PROVINCE_BASE}{slug}")
            for m in _DEALER_LINK_RE.finditer(page):
                dealer_slug = m.group(1)
                municipality, name = _parse_link_text(m.group(2))
                if slug == _CANARIAS_SLUG:
                    province = _canarias_province(municipality)
                else:
                    province = _SLUG_TO_INE.get(slug)
                if not province:
                    continue
                key = (dealer_slug, province)
                if key in seen:
                    continue
                seen.add(key)
                rows.append({
                    "dealer_slug": dealer_slug,
                    "province": province,
                    "province_slug": slug,
                    "municipality": municipality,
                    "name": name,
                })
        self._rows = rows
        return self._rows

    def declared_count(self) -> int | None:
        # in-scope (Spain) outlet count — the real denominator for the VAM gate
        return len(self._load())

    def fetch(self) -> list[DiscoveredEntity]:
        out: list[DiscoveredEntity] = []
        self.excluded_count = 0
        for r in self._load():
            province = r["province"]
            if not province:
                self.excluded_count += 1  # province unresolved, excluded transparently
                continue
            out.append(DiscoveredEntity(
                kind="concesionario_oficial",
                source_key=self.source_key,
                source_ref=f"{r['dealer_slug']}@{province}",
                legal_name=r["name"],
                trade_name=r["name"],
                province_name=province,            # 2-digit INE code; resolver accepts digit form
                municipality_name=r["municipality"],
                website=(f"https://www.concesionarios.seat/home/overview-dw.dealer."
                         f"{r['dealer_slug']}.html"),
                extra={"brand": "SEAT", "province_slug": r["province_slug"]},
            ))
        return out
