"""Offline unit tests for the AutoScout24 census adapter (Vector 1, open Tier-1 surface)."""
from __future__ import annotations

import pytest

import pipeline.sources.autoscout24_census as mod
from pipeline.sources.autoscout24 import DealerInfo
from pipeline.sources.autoscout24_census import SOURCE_KEY, dealer_entity


def _fake_page(monkeypatch, info):
    monkeypatch.setattr(mod, "fetch_page", lambda slug, page: "<html></html>")
    monkeypatch.setattr(mod, "_next_data", lambda html: {})
    monkeypatch.setattr(mod, "parse_page_dealer", lambda data: info)


@pytest.mark.unit
def test_dealer_entity_identity_matches_ingest(monkeypatch):
    info = DealerInfo(source_dealer_id="123", company_name="Autos Pepe", slug="autos-pepe",
                      province_code="28", city="Madrid", street="Calle X 1", zip="28001",
                      website="https://autospepe.es")
    _fake_page(monkeypatch, info)
    e = dealer_entity("autos-pepe")
    assert e.source_key == SOURCE_KEY
    assert e.legal_name == "Autos Pepe"
    assert e.province_name == "28"
    assert e.municipality_name == "Madrid"
    assert e.address == "Calle X 1"            # street -> cdp dedup with ingest_dealer
    assert e.website == "https://autospepe.es"  # domain -> cdp dedup
    assert e.extra["platform"] == "autoscout24"


@pytest.mark.unit
def test_dealer_entity_rejects_foreign_postcode(monkeypatch):
    info = DealerInfo(source_dealer_id="9", company_name="Auto DE", slug="auto-de",
                      province_code="99", city=None, street=None, zip="99999", website=None)
    _fake_page(monkeypatch, info)
    e = dealer_entity("auto-de")
    assert e.province_name is None   # out-of-Spain postcode -> province dropped (honest skip later)


@pytest.mark.unit
def test_dealer_entity_none_without_company(monkeypatch):
    _fake_page(monkeypatch, None)
    assert dealer_entity("ghost") is None
