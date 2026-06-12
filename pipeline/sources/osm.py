"""OpenStreetMap adapter — long-tail auto points of sale across Spain.

Free, legal (ODbL), geocoded. Census F1 verified ~12,077 auto POIs:
shop=car (dealers/compraventas), shop=car_repair (garages), shop=car_parts.
Queries the Overpass API (tries several mirrors; the public instance is often
saturated). Province from addr:postcode (first 2 digits == INE province), city
from addr:city — both resolved at ingest.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
_UA = "CardeepBot/0.1 (market research; contact via repo)"

_QUERY = """
[out:json][timeout:180];
area["ISO3166-1"="ES"][admin_level=2]->.es;
(
  nwr["shop"="car"](area.es);
  nwr["shop"="car_repair"](area.es);
  nwr["shop"="car_parts"](area.es);
);
out center tags;
"""

_KIND = {"car": "compraventa", "car_repair": "garaje", "car_parts": "garaje"}


def _overpass() -> dict:
    body = urllib.parse.urlencode({"data": _QUERY}).encode()
    last_err = None
    for mirror in _MIRRORS:
        try:
            req = urllib.request.Request(mirror, data=body, headers={"User-Agent": _UA})
            with urllib.request.urlopen(req, timeout=200) as r:  # noqa: S310
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            last_err = e
            continue
    raise RuntimeError(f"all Overpass mirrors failed: {last_err}")


class OsmAdapter(SourceAdapter):
    source_key = "osm"

    def __init__(self) -> None:
        self._elements: list[dict] | None = None

    def _load(self) -> list[dict]:
        if self._elements is None:
            self._elements = _overpass().get("elements", [])
        return self._elements

    def declared_count(self) -> int | None:
        return len(self._load())

    def fetch(self) -> list[DiscoveredEntity]:
        out: list[DiscoveredEntity] = []
        for el in self._load():
            tags = el.get("tags", {}) or {}
            shop = tags.get("shop")
            name = tags.get("name")
            if not name:
                continue  # unnamed POI is noise, not a point of sale
            lat = el.get("lat") or (el.get("center") or {}).get("lat")
            lon = el.get("lon") or (el.get("center") or {}).get("lon")
            postcode = tags.get("addr:postcode")
            province = str(postcode)[:2] if postcode and str(postcode)[:2].isdigit() else None
            street = " ".join(p for p in (tags.get("addr:street"), tags.get("addr:housenumber")) if p) or None
            out.append(DiscoveredEntity(
                kind=_KIND.get(shop, "garaje"),
                source_key=self.source_key,
                source_ref=f"{el.get('type')}/{el.get('id')}",
                legal_name=name,
                trade_name=name,
                province_name=province,
                municipality_name=tags.get("addr:city"),
                address=street,
                postcode=str(postcode) if postcode else None,
                lat=lat,
                lon=lon,
                phone=tags.get("phone") or tags.get("contact:phone"),
                email=tags.get("email") or tags.get("contact:email"),
                website=tags.get("website") or tags.get("contact:website"),
                extra={"osm_shop": shop},
            ))
        return out
