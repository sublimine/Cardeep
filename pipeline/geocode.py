"""Lat/lon -> INE province and municipality by nearest labeled point.

Provides two geocoders:

- ProvinceGeocoder: lat/lon -> province_code. Uses entity centroids already in
  DB (existing). Provinces are large contiguous regions so nearest-centroid is
  accurate without boundary polygons.

- MunicipalityGeocoder: (lat, lon, province_code) -> municipality_code (5-digit
  INE). Uses official centroid coordinates seeded into geo_municipality (B4.3,
  migration 0022). KNN is scoped within the given province so cross-province
  false positives are impossible. Anti-spurious guard: if the nearest centroid is
  further than KNN_MAX_DISTANCE_KM the call returns None ("better a hole than a
  lie" — doctrine inherited from B4.2 ambiguity guard).

  Threshold rationale: 30 km. The largest Spanish municipalities by area have
  a typical radius of 15-20 km (Lorca ~1,676 km², radius ~23 km; Cáceres
  ~1,750 km², radius ~24 km). A 30 km threshold gives a comfortable margin for
  sparse rural provinces (e.g. Soria, Cuenca) where the nearest centroid can be
  genuinely 20-25 km away, while blocking obviously wrong assignments where the
  entity falls in a different province but province_code was derived from an
  imprecise source.

- PostcodeIndex: postcode -> municipality_code using the INE Nomenclátor gazetteer
  already present at data/geo/nomenclator_entidades_ine.csv. Any postcode that
  maps to more than one distinct municipality returns None (ambiguity doctrine).

Dependencies: numpy only (already installed). No new packages.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import asyncpg

# ---------------------------------------------------------------------------
# Tuning constant
# ---------------------------------------------------------------------------

# Maximum distance (km) between query point and nearest municipality centroid
# before the result is rejected as unreliable.
# 30 km is defensible for Spain: even the largest municipalities by area rarely
# exceed a 24 km radius, and entity coordinates generally fall INSIDE the
# municipality they belong to. Assignments beyond 30 km would almost certainly
# cross into a neighbouring municipality.
KNN_MAX_DISTANCE_KM: float = 30.0

_NOMENCLATOR_PATH: Path = (
    Path(__file__).resolve().parent.parent / "data" / "geo" / "nomenclator_entidades_ine.csv"
)

# Earth radius in km (WGS84 mean)
_EARTH_RADIUS_KM: float = 6371.0


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two WGS84 points."""
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    return 2 * _EARTH_RADIUS_KM * math.asin(math.sqrt(a))


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
            "WHERE lat IS NOT NULL AND lon IS NOT NULL AND province_code IS NOT NULL"
        )
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


class MunicipalityGeocoder:
    """KNN reverse-geocode (lat, lon, province_code) -> municipality_code.

    Loaded once per session from geo_municipality centroids (seeded in B4.3).
    Lookup is O(n_municipalities_in_province) per call; for the largest province
    (Madrid, ~179 municipalities) this is trivially fast with numpy.

    The province_code constraint is MANDATORY: it prevents cross-province false
    positives and keeps the index small per lookup.

    Returns None when:
    - province_code is unknown or has no centroid data
    - No municipality has a seeded centroid in that province
    - Nearest centroid is farther than KNN_MAX_DISTANCE_KM
    """

    def __init__(
        self,
        index: dict[str, tuple[np.ndarray, np.ndarray, list[str]]],
    ) -> None:
        # index[province_code] = (lats_array, lons_array, [code5, ...])
        self._index = index

    @classmethod
    async def load(cls, conn: asyncpg.Connection) -> "MunicipalityGeocoder":
        """Build the in-memory KNN index from geo_municipality centroids."""
        rows = await conn.fetch(
            "SELECT code, province_code, lat, lon "
            "FROM geo_municipality "
            "WHERE lat IS NOT NULL AND lon IS NOT NULL "
            "ORDER BY province_code, code"
        )
        # Group by province
        prov_data: dict[str, list[tuple[float, float, str]]] = {}
        for r in rows:
            prov_data.setdefault(r["province_code"], []).append(
                (float(r["lat"]), float(r["lon"]), r["code"])
            )

        index: dict[str, tuple[np.ndarray, np.ndarray, list[str]]] = {}
        for prov, entries in prov_data.items():
            lats = np.array([e[0] for e in entries])
            lons = np.array([e[1] for e in entries])
            codes = [e[2] for e in entries]
            index[prov] = (lats, lons, codes)

        return cls(index)

    def nearest_municipality(
        self,
        lat: float | None,
        lon: float | None,
        province_code: str | None,
    ) -> tuple[str | None, float]:
        """Return (municipality_code, distance_km) for the nearest centroid in *province_code*.

        Returns (None, distance_km) when:
        - inputs are missing or non-numeric
        - province has no centroid data
        - nearest centroid exceeds KNN_MAX_DISTANCE_KM
        """
        if lat is None or lon is None or not province_code:
            return (None, float("inf"))
        try:
            la, lo = float(lat), float(lon)
        except (TypeError, ValueError):
            return (None, float("inf"))

        entry = self._index.get(province_code)
        if entry is None:
            return (None, float("inf"))

        lats, lons, codes = entry
        if len(codes) == 0:
            return (None, float("inf"))

        # Equirectangular approximation for argmin (fast, monotonic for small areas).
        # Province width is at most ~300 km, well within the safe range for this approx.
        cos_lat = math.cos(math.radians(la))
        dlat = lats - la
        dlon = (lons - lo) * cos_lat
        idx = int(np.argmin(dlat * dlat + dlon * dlon))

        # Exact haversine for the winner only (threshold check needs real km).
        dist_km = _haversine_km(la, lo, float(lats[idx]), float(lons[idx]))
        if dist_km > KNN_MAX_DISTANCE_KM:
            return (None, dist_km)

        return (codes[idx], dist_km)

    def province_count(self) -> int:
        """Number of provinces with at least one centroid loaded."""
        return len(self._index)

    def centroid_count(self) -> int:
        """Total number of centroids loaded across all provinces."""
        return sum(len(codes) for _, _, codes in self._index.values())


class PostcodeIndex:
    """Map Spanish postcodes to municipality_code via the INE Nomenclátor.

    Postcodes that span more than one municipality are ambiguous and return None
    ("better a hole than a lie" — same doctrine as B4.2 ambiguity guard).

    Loaded from data/geo/nomenclator_entidades_ine.csv (already present in repo).
    """

    def __init__(
        self,
        unambiguous: dict[str, str],
        ambiguous: set[str],
    ) -> None:
        # unambiguous[postcode] = municipality_code5
        self._unambiguous = unambiguous
        # ambiguous: postcodes that map to >1 municipality
        self._ambiguous = ambiguous

    @classmethod
    def load(cls, path: Path = _NOMENCLATOR_PATH) -> "PostcodeIndex":
        """Build the CP -> municipality_code index from the Nomenclátor CSV."""
        from collections import defaultdict

        cp_to_munis: dict[str, set[str]] = defaultdict(set)

        if not path.exists():
            return cls({}, set())

        with path.open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                cp = row.get("codigo_postal", "").strip()
                mid = row.get("municipio_id", "").strip()
                if not cp or len(mid) != 5:
                    continue
                cp_to_munis[cp].add(mid)

        unambiguous: dict[str, str] = {}
        ambiguous: set[str] = set()
        for cp, munis in cp_to_munis.items():
            if len(munis) == 1:
                unambiguous[cp] = next(iter(munis))
            else:
                ambiguous.add(cp)

        return cls(unambiguous, ambiguous)

    def resolve(self, postcode: str | None) -> str | None:
        """Return municipality_code for *postcode*, or None if ambiguous / unknown."""
        if not postcode:
            return None
        cp = postcode.strip()
        if cp in self._ambiguous:
            return None
        return self._unambiguous.get(cp)

    def size_unambiguous(self) -> int:
        return len(self._unambiguous)

    def size_ambiguous(self) -> int:
        return len(self._ambiguous)
