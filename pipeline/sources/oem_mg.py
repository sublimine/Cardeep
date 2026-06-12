"""MG Motor España official store network adapter.

Open unauthenticated JSONFeed FeatureCollection (verified live 2026-06-12: 212
features). The feed is intentionally minimal: each feature carries only
geometry.coordinates [lon, lat] and properties {category, name, id,
specialStoreType}. There is NO postcode/zipCode, address, phone or website in
this feed (the spec's organizationName/zipCode fields do not exist in the live
response — confirmed against the real payload), so:

  * province_name is left None — no postcode exists to derive an INE code from.
    The discover pipeline recovers the province from an unambiguous municipality
    name via GeoResolver.resolve_city_global (street/area names that are not a
    unique national municipality are skipped honestly at ingest).
  * municipality_name is parsed from the store name, which embeds the location:
    "MG <LOCATION> - <OPERATOR>" (separators: en/em dash, pipe, or a
    space-adjacent hyphen). A leading "CANARIAS" region prefix is stripped so the
    real municipality (e.g. La Orotava, Las Chafiras) surfaces.
  * trade_name is the full store name; legal_name is the operator (the company
    after the separator) when present.

All features are Spain by construction (site=mgMotorsSpain); coordinates confirm
mainland + Canary/Balearic islands, so there is no out-of-scope exclusion here.
"""
from __future__ import annotations

import json
import re
import unicodedata
import urllib.request

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

_URL = "https://www.mgmotor.eu/data/map.json?site=mgMotorsSpain"
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/137 Safari/537.36"

# Org separator: en/em dash, pipe, or a hyphen that is adjacent to a space.
# A bare hyphen (e.g. "A-42") is deliberately NOT a separator.
_ORG_SEP = re.compile(r"\s*[–—|]\s*|\s+-\s*|\s*-\s+")
# Region labels that are not a municipality; the real city follows them.
_REGION_PREFIX = {"canarias"}


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 (trusted vendor host)
        return json.loads(r.read().decode("utf-8"))


def _clean(v) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def _to_float(v) -> float | None:
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return None


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _split_store_name(name: str) -> tuple[str | None, str | None]:
    """Parse "MG <LOCATION> - <OPERATOR>" into (municipality, operator).

    Returns (None, None) only if nothing usable remains.
    """
    s = re.sub(r"\s+", " ", name).strip()
    base = re.sub(r"^MG\s+", "", s, flags=re.IGNORECASE).strip()

    # Region prefix joined by a bare hyphen, e.g. "CANARIAS-LA OROTAVA-SMALLCARS".
    m = re.match(r"^([^\s\-]+)-(.+)$", base)
    if m and _norm(m.group(1)) in _REGION_PREFIX:
        base = m.group(2).strip()
        # re-expose the trailing operator that was also joined by a bare hyphen
        base = re.sub(r"-([^\s\-]+)$", r" - \1", base)

    segs = [p.strip() for p in _ORG_SEP.split(base) if p.strip()]
    if not segs:
        return (None, None)
    # Drop a leading region prefix that survived as its own segment.
    if len(segs) > 1 and _norm(segs[0]) in _REGION_PREFIX:
        segs = segs[1:]
    location = segs[0]
    operator = " - ".join(segs[1:]) if len(segs) > 1 else None
    return (location or None, operator)


class OemMgAdapter(SourceAdapter):
    source_key = "oem_mg"

    def __init__(self) -> None:
        self._features: list[dict] | None = None

    def _load(self) -> list[dict]:
        if self._features is None:
            data = _get(_URL)
            feats = data.get("features")
            self._features = feats if isinstance(feats, list) else []
        return self._features

    def declared_count(self) -> int | None:
        return len(self._load())

    def fetch(self) -> list[DiscoveredEntity]:
        out: list[DiscoveredEntity] = []
        for feat in self._load():
            props = feat.get("properties", {}) or {}
            name = _clean(props.get("name"))
            if not name:
                continue
            municipality, operator = _split_store_name(name)
            coords = (feat.get("geometry") or {}).get("coordinates") or []
            lon = _to_float(coords[0]) if len(coords) >= 2 else None
            lat = _to_float(coords[1]) if len(coords) >= 2 else None
            store_type = (props.get("specialStoreType") or {}).get("value")
            out.append(DiscoveredEntity(
                kind="concesionario_oficial",
                source_key=self.source_key,
                source_ref=_clean(props.get("id")),
                legal_name=operator or name,    # operating company when parseable
                trade_name=name,                # full MG store name as shown publicly
                province_name=None,             # no postcode in feed; recovered from city at ingest
                municipality_name=municipality,
                lat=lat,
                lon=lon,
                website=None,                   # not exposed per store in this feed
                extra={"brand": "MG", "store_type": _clean(store_type)},
            ))
        return out
