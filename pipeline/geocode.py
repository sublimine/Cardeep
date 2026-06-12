"""Lat/lon -> INE province by nearest labeled point.

Many long-tail POIs (OSM) carry coordinates but no postcode and an ambiguous
city. We already hold thousands of entities with both coordinates AND a known
province (DGT scrapyards, OEM dealers). Provinces are large contiguous regions,
so the province of the nearest labeled point is an accurate classifier — free,
dependency-light (numpy), no boundary polygons needed.
"""
from __future__ import annotations

import numpy as np
import asyncpg


class ProvinceGeocoder:
    def __init__(self, lats: np.ndarray, lons: np.ndarray, provs: list[str]) -> None:
        self._lat = lats
        self._lon = lons
        # cos(latitude) correction so longitude degrees are scaled to real distance
        self._coslat = np.cos(np.radians(lats))
        self._provs = provs

    @classmethod
    async def load(cls, conn: asyncpg.Connection) -> "ProvinceGeocoder":
        rows = await conn.fetch(
            "SELECT lat, lon, province_code FROM entity "
            "WHERE lat IS NOT NULL AND lon IS NOT NULL AND province_code IS NOT NULL")
        lats = np.array([float(r["lat"]) for r in rows])
        lons = np.array([float(r["lon"]) for r in rows])
        provs = [r["province_code"] for r in rows]
        return cls(lats, lons, provs)

    def nearest_province(self, lat: float | None, lon: float | None) -> str | None:
        if lat is None or lon is None or len(self._provs) == 0:
            return None
        try:
            la, lo = float(lat), float(lon)
        except (TypeError, ValueError):
            return None
        # squared equirectangular distance (monotonic — fine for nearest-neighbor)
        dlat = self._lat - la
        dlon = (self._lon - lo) * self._coslat
        idx = int(np.argmin(dlat * dlat + dlon * dlon))
        return self._provs[idx]

    def size(self) -> int:
        return len(self._provs)
