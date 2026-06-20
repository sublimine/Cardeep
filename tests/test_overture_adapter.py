"""Offline unit tests for the Overture (V2 geo-grid) SourceAdapter.

No network, no DuckDB: the row-shaping logic is exercised by injecting a fake
result set into the adapter, so we assert the contract the VAM gate and the
INE geo-resolver rely on — kind mapping, country filtering, postcode->province,
and clean self-isolation when the source is unreachable.
"""
from __future__ import annotations

import pytest

from pipeline.sources.overture import OvertureAdapter

_FAKE_ROWS = [
    {"id": "p1", "name": "Talleres La Sierra", "category": "automotive_repair_shop",
     "lon": -3.7, "lat": 40.4, "street": "Calle Mayor 1", "locality": "Madrid",
     "postcode": "28013", "region": "Madrid", "country": "ES",
     "phone": "+34910000000", "website": "https://t.example", "email": None},
    {"id": "p2", "name": "Autos del Sur", "category": "car_dealer",
     "lon": -5.9, "lat": 37.3, "street": None, "locality": "Sevilla",
     "postcode": "41001", "region": "Sevilla", "country": "ES",
     "phone": None, "website": None, "email": None},
    # Portugal over-capture from the bbox: must be dropped by the country filter.
    {"id": "p3", "name": "Auto Lisboa", "category": "car_dealer",
     "lon": -9.1, "lat": 38.7, "street": None, "locality": "Lisboa",
     "postcode": "1000", "region": "Lisboa", "country": "PT",
     "phone": None, "website": None, "email": None},
    # Nameless POI: noise, must be skipped.
    {"id": "p4", "name": "  ", "category": "car_dealer", "lon": -3.7, "lat": 40.4,
     "street": None, "locality": None, "postcode": None, "region": None,
     "country": "ES", "phone": None, "website": None, "email": None},
]


@pytest.mark.unit
def test_rows_map_to_discovered_entities(monkeypatch):
    a = OvertureAdapter()
    monkeypatch.setattr(a, "_load", lambda: _FAKE_ROWS)
    a._rows = _FAKE_ROWS
    a._release = "2026-06-17.0"
    out = a.fetch()
    # Portugal + nameless dropped -> 2 Spanish, named POIs remain.
    assert len(out) == 2
    by_name = {e.trade_name: e for e in out}

    repair = by_name["Talleres La Sierra"]
    assert repair.kind == "garaje"  # repair shop is not a sales kind
    assert repair.source_key == "overture"
    assert repair.source_ref == "p1"
    assert repair.province_name == "28"  # first 2 postcode digits
    assert repair.municipality_name == "Madrid"
    assert repair.extra["vector"] == 2
    assert repair.extra["overture_release"] == "2026-06-17.0"

    dealer = by_name["Autos del Sur"]
    assert dealer.kind == "compraventa"  # car_dealer -> sales
    assert dealer.province_name == "41"


@pytest.mark.unit
def test_isolation_yields_empty(monkeypatch):
    a = OvertureAdapter()
    a._isolated = "no reachable Overture release"
    a._rows = []
    monkeypatch.setattr(a, "_load", lambda: [])
    assert a.fetch() == []
    assert a.declared_count() is None
