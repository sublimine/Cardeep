"""Offline unit tests for the V3 municipal-dorking SourceAdapter.

No network, no DB: assert the domain filtering (marketplaces/socials out, own
dealer domains in), URL canonicalization, and the search-result -> DiscoveredEntity
mapping by injecting a fake municipality list and a stub search backend.
"""
from __future__ import annotations

import pytest

from pipeline.sources import dork_municipal as dm
from pipeline.sources.dork_municipal import DorkMunicipalAdapter


@pytest.mark.unit
@pytest.mark.parametrize("url,expected", [
    ("https://www.tallerareauto.com/contacto", "tallerareauto.com"),
    ("http://Autoback.ES", "autoback.es"),
    ("https://chollocars.net", "chollocars.net"),
    ("notaurl", "notaurl"),
])
def test_registrable_domain(url, expected):
    assert dm._registrable_domain(url) == expected


@pytest.mark.unit
def test_dealer_domain_filter():
    assert dm._is_dealer_domain("tallerareauto.com")
    assert dm._is_dealer_domain("autoback.es")
    # marketplaces / directories / socials / infra are not the dealer's own site
    for noise in ("coches.net", "www.wallapop.com", "facebook.com", "paginasamarillas.es",
                  "google.com", "boe.es", "milanuncios.com"):
        assert not dm._is_dealer_domain(dm._registrable_domain(noise))
    assert not dm._is_dealer_domain(None)
    assert not dm._is_dealer_domain("nodot")


@pytest.mark.unit
def test_build_maps_results_to_entities(monkeypatch):
    a = DorkMunicipalAdapter()
    # one municipality, deterministic
    monkeypatch.setattr(dm, "_run_async", lambda coro: [
        {"code": "28092", "name": "Móstoles", "province_code": "28", "lat": 40.3, "lon": -3.8},
    ])
    monkeypatch.setattr(a, "_pick_engine", lambda: setattr(a, "_engine", "searxng") or None)
    # stub the per-query search: mix of a real dealer domain, a marketplace, and a dup
    monkeypatch.setattr(a, "_query", lambda base, q: [
        "https://tallerareauto.com/x", "https://www.coches.net/y",
        "https://tallerareauto.com/z",  # duplicate domain -> collapsed
        "https://autoback.es",
    ])
    monkeypatch.setenv("CARDEEP_DORK_DELAY", "0")
    rows = a.fetch()
    domains = sorted({e.website for e in rows})
    assert domains == ["https://autoback.es", "https://tallerareauto.com"]
    for e in rows:
        assert e.source_key == "dork_municipal"
        assert e.province_name == "28"
        assert e.municipality_name == "Móstoles"
        assert e.extra["vector"] == 3
    assert a.declared_count() is None


@pytest.mark.unit
def test_isolation_when_no_engine(monkeypatch):
    a = DorkMunicipalAdapter()
    monkeypatch.setattr(dm, "_run_async", lambda coro: [
        {"code": "28092", "name": "Móstoles", "province_code": "28", "lat": 40.3, "lon": -3.8}])
    monkeypatch.setattr(a, "_pick_engine",
                        lambda: setattr(a, "_isolated", "no search engine reachable") or None)
    monkeypatch.setenv("CARDEEP_DORK_DELAY", "0")
    assert a.fetch() == []
