"""Resolve province/municipality names to INE codes against the geo backbone.

Builds an in-memory index once per run. Matching is accent/case insensitive,
order-insensitive (token-sorted, so "La Rioja" == "Rioja, La"), handles
bilingual INE names, and carries a curated alias table for island/variant
province names that no normalization can bridge (e.g. Menorca -> Balears).
"""
from __future__ import annotations

import re
import unicodedata

import asyncpg


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _sorted_key(text: str) -> str:
    return " ".join(sorted(_norm(text).split()))


# Province-name variants that normalization alone cannot bridge -> INE province code.
_PROVINCE_ALIASES = {
    "alava": "01", "araba": "01",
    "menorca": "07", "mallorca": "07", "ibiza": "07", "eivissa": "07",
    "formentera": "07", "islas baleares": "07", "illes balears": "07",
    "a coruna": "15", "la coruna": "15",
    "guipuzcoa": "20", "gipuzkoa": "20",
    "las palmas": "35", "gran canaria": "35", "fuerteventura": "35", "lanzarote": "35",
    "la rioja": "26",
    "vizcaya": "48", "bizkaia": "48",
    "gerona": "17", "lerida": "25", "orense": "32",
    "tenerife": "38", "santa cruz de tenerife": "38",
    "castellon": "12", "castello": "12",
}


class GeoResolver:
    def __init__(self) -> None:
        self._muni: dict[str, dict[str, str]] = {}     # prov_code -> {muni key: code5}
        self._prov: dict[str, str] = {}                # province key -> code2
        self._city_global: dict[str, set[tuple[str, str]]] = {}  # muni key -> {(prov, code5)}

    def _index_prov(self, name: str, code: str) -> None:
        self._prov.setdefault(_norm(name), code)
        self._prov.setdefault(_sorted_key(name), code)
        for part in re.split(r"[/,]", name):
            p = _norm(part)
            if p:
                self._prov.setdefault(p, code)

    @classmethod
    async def load(cls, conn: asyncpg.Connection) -> "GeoResolver":
        self = cls()
        for r in await conn.fetch("SELECT code, name FROM geo_province"):
            self._index_prov(r["name"], r["code"])
        for k, v in _PROVINCE_ALIASES.items():
            self._prov.setdefault(k, v)
        for r in await conn.fetch("SELECT code, name, province_code FROM geo_municipality"):
            d = self._muni.setdefault(r["province_code"], {})
            keys = {_norm(r["name"]), _sorted_key(r["name"])}
            for part in re.split(r"[/,]", r["name"]):
                p = _norm(part)
                if p:
                    keys.add(p)
            for k in keys:
                d.setdefault(k, r["code"])
                self._city_global.setdefault(k, set()).add((r["province_code"], r["code"]))
        return self

    def resolve_city_global(self, city: str | None) -> tuple[str | None, str | None]:
        """Resolve a bare city name to (province_code, municipality_code) only when it
        maps to exactly one municipality nationally (unambiguous). Else (None, None)."""
        if not city:
            return (None, None)
        hits = self._city_global.get(_norm(city)) or self._city_global.get(_sorted_key(city))
        if hits and len(hits) == 1:
            prov, code = next(iter(hits))
            return (prov, code)
        return (None, None)

    def province_code(self, name_or_code: str | None) -> str | None:
        if not name_or_code:
            return None
        s = str(name_or_code).strip()
        if s.isdigit():
            c = s.zfill(2)
            return c if c in self._muni else None
        return self._prov.get(_norm(s)) or self._prov.get(_sorted_key(s))

    def municipality_code(self, province_code: str | None, muni_name: str | None) -> str | None:
        if not province_code or not muni_name:
            return None
        d = self._muni.get(province_code, {})
        return d.get(_norm(muni_name)) or d.get(_sorted_key(muni_name))
