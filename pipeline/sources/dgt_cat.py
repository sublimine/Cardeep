"""DGT CATV adapter — the official national registry of authorized scrapyards (CATs).

Source of truth for the desguace segment. Open ArcGIS FeatureServer, no auth.
Verified live 2026-06-12: returnCountOnly = 1292.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

_BASE = ("https://services3.arcgis.com/TXNiwnLDifb5lMaR/arcgis/rest/services/"
         "CATV/FeatureServer/0")
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/137 Safari/537.36"


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 (trusted gov host)
        return json.loads(r.read().decode("utf-8"))


def _clean(v) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


class DgtCatAdapter(SourceAdapter):
    source_key = "dgt_cat"

    def __init__(self) -> None:
        self._declared: int | None = None

    def declared_count(self) -> int | None:
        if self._declared is None:
            q = urllib.parse.urlencode({"where": "1=1", "returnCountOnly": "true", "f": "json"})
            self._declared = _get(f"{_BASE}/query?{q}").get("count")
        return self._declared

    def fetch(self) -> list[DiscoveredEntity]:
        q = urllib.parse.urlencode({
            "where": "1=1", "outFields": "*", "resultRecordCount": 10000, "f": "json",
        })
        data = _get(f"{_BASE}/query?{q}")
        out: list[DiscoveredEntity] = []
        for feat in data.get("features", []):
            a = feat.get("attributes", {})
            out.append(DiscoveredEntity(
                kind="desguace",
                source_key=self.source_key,
                source_ref=str(a.get("ID") or a.get("OBJECTID")),
                legal_name=_clean(a.get("Centro_autorizado_de_Tratamient")),
                trade_name=_clean(a.get("Centro_autorizado_de_Tratamient")),
                province_name=_clean(a.get("Provincia")),
                municipality_name=_clean(a.get("Municipio")),
                address=_clean(a.get("Dirección")),
                postcode=_clean(a.get("Código_postal")),
                lat=a.get("Latitud"),
                lon=a.get("Longitud"),
                phone=_clean(a.get("Teléfono_1")),
                email=_clean(a.get("Correo_electrónico")),
                website=_clean(a.get("WEB")),
                extra={"codigo_centro": _clean(a.get("Codigo_centro")),
                       "comunidad": _clean(a.get("Comunidad"))},
            ))
        return out
