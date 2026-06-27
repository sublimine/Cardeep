"""Country-proof (red-team final): MunicipalityGeocoder.load must scope by country.

``pipeline/geocode.py`` ``MunicipalityGeocoder.load`` built its KNN index with
``SELECT ... FROM geo_municipality WHERE lat IS NOT NULL`` — country-blind — and
keyed the index by ``province_code`` alone. geo_municipality's PK is
``(country_code, code)`` (migration 0053) and a DE province ``'ZZ'`` legitimately
coexists with an ES province ``'ZZ'``. The blind load folded BOTH countries'
centroids into the same province bucket, so a query inside one country could match
a centroid that physically belongs to another — a cross-border reverse-geocode leak.

The fix mirrors ``GeoResolver.load(conn, country_code='ES')`` (pipeline/geo.py:151):
``MunicipalityGeocoder.load`` gains a ``country_code`` param (default 'ES') and filters
``WHERE country_code = $1``. ES behaviour is byte-identical (every centroid loaded today
is ES). This golden proves a non-ES centroid never enters the ES index, and vice-versa.

ISOLATION: runs ONLY against the dry-run (:5434). Honors CARDEEP_DSN (default :5434),
HARD-REFUSES :5433 (live) by DSN string. Self-seeds both countries inside a transaction
and ROLLS BACK — zero residue, no dependence on a populated census.
"""
from __future__ import annotations

import asyncio
import os

import pytest

from pipeline.geocode import MunicipalityGeocoder

_DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep")
pytestmark = pytest.mark.skipif("5433" in _DSN, reason="needs the :5434 dry-run; refuses live :5433")

# Synthetic province code that does not exist in the real INE census, so the test
# fully owns its province bucket regardless of what geo_municipality already holds.
_PROV = "ZZ"
_ES_MUNI = "ZZ001"   # ES code MUST start with province_code (municipality_province_prefix check)
_DE_MUNI = "ZZ777"   # DE has no prefix constraint; a DISTINCT code makes a leak unmistakable

# Far-apart centroids: a query at one is ~1860 km from the other — well past
# KNN_MAX_DISTANCE_KM (30 km), so a correctly-scoped index returns None for the
# foreign point while the blind index returns the foreign centroid at ~0 km.
_MADRID = (40.4168, -3.7038)
_BERLIN = (52.5200, 13.4050)


async def _seed(conn) -> None:
    for country in ("ES", "DE"):
        await conn.execute(
            "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
            "VALUES ($1,$2,'13',$3,$4) ON CONFLICT DO NOTHING",
            _PROV, f"prov-{country}-{_PROV}", f"ccaa-{country}", country,
        )
    await conn.execute(
        "INSERT INTO geo_municipality (code, name, province_code, lat, lon, country_code) "
        "VALUES ($1,$2,$3,$4,$5,'ES') ON CONFLICT DO NOTHING",
        _ES_MUNI, "muni-ES", _PROV, _MADRID[0], _MADRID[1],
    )
    await conn.execute(
        "INSERT INTO geo_municipality (code, name, province_code, lat, lon, country_code) "
        "VALUES ($1,$2,$3,$4,$5,'DE') ON CONFLICT DO NOTHING",
        _DE_MUNI, "muni-DE", _PROV, _BERLIN[0], _BERLIN[1],
    )


def test_municipality_geocoder_load_is_country_scoped() -> None:
    asyncio.run(_run())


async def _run() -> None:
    import asyncpg

    conn = await asyncpg.connect(_DSN)
    try:
        tr = conn.transaction()
        await tr.start()
        try:
            await _seed(conn)

            es_geo = await MunicipalityGeocoder.load(conn, country_code="ES")
            de_geo = await MunicipalityGeocoder.load(conn, country_code="DE")

            # White-box: each country's province bucket holds ONLY its own centroid.
            es_codes = es_geo._index.get(_PROV, ((), (), []))[2]
            de_codes = de_geo._index.get(_PROV, ((), (), []))[2]
            assert es_codes == [_ES_MUNI], (
                f"ES index for province {_PROV!r} must hold only {_ES_MUNI!r}; got {es_codes!r} "
                f"(a {_DE_MUNI!r} here is the cross-country leak)"
            )
            assert de_codes == [_DE_MUNI], (
                f"DE index for province {_PROV!r} must hold only {_DE_MUNI!r}; got {de_codes!r}"
            )

            # Behavioural: the ES geocoder matches the ES centroid at ~0 km ...
            code_es, dist_es = es_geo.nearest_municipality(_MADRID[0], _MADRID[1], _PROV)
            assert code_es == _ES_MUNI and dist_es < 1.0, (code_es, dist_es)

            # ... and REFUSES the DE (Berlin) point: the nearest ES centroid (Madrid) is
            # ~1860 km away, beyond the 30 km threshold -> None. Under the country-blind
            # bug the Berlin DE centroid lived in the ES bucket and returned _DE_MUNI @ ~0 km.
            code_de, dist_de = es_geo.nearest_municipality(_BERLIN[0], _BERLIN[1], _PROV)
            assert code_de is None, (
                f"CROSS-COUNTRY GEOCODE LEAK: ES index resolved a Berlin point to {code_de!r} "
                f"@ {dist_de:.0f} km; the DE centroid must not be in the ES index."
            )
        finally:
            await tr.rollback()
    finally:
        await conn.close()
