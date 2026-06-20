"""Offline unit tests for the generic dealer-website inventory extractor (§4 cost-0 rung)."""
from __future__ import annotations

import pytest

from pipeline.recipe_extract_web import (
    find_stock_url,
    vehicles_from_jsonld,
    vehicles_from_microdata,
)

_JSONLD = """<html><script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
 {"@type":"Car","name":"Seat Ibiza 1.0","offers":{"@type":"Offer","price":"12900"},"url":"/c/1"},
 {"@type":"Vehicle","name":"VW Golf GTI","offers":{"price":"21900"},"url":"/c/2"},
 {"@type":"WebPage","name":"not a car"}]}</script></html>"""

_MICRO = """<div itemscope itemtype="https://schema.org/Car">
 <span itemprop="name">Renault Clio</span>
 <span itemprop="price" content="9500"></span>
 <a itemprop="url" href="/clio"></a></div>
<div itemscope itemtype="https://schema.org/Product">
 <span itemprop="name">Ford Focus</span></div>"""


@pytest.mark.unit
def test_jsonld_extracts_only_vehicles():
    vs = vehicles_from_jsonld(_JSONLD)
    names = {v["name"] for v in vs}
    assert "Seat Ibiza 1.0" in names and "VW Golf GTI" in names
    assert "not a car" not in names           # WebPage is not a vehicle
    assert any(v["price"] == "12900" for v in vs)


@pytest.mark.unit
def test_microdata_extracts_vehicles():
    vs = vehicles_from_microdata(_MICRO)
    names = {v["name"] for v in vs}
    assert "Renault Clio" in names and "Ford Focus" in names
    clio = next(v for v in vs if v["name"] == "Renault Clio")
    assert clio["price"] == "9500"


@pytest.mark.unit
def test_find_stock_url_resolves_relative():
    home = '<a href="/coches-segunda-mano">stock</a>'
    assert find_stock_url(home, "https://dealer.es") == "https://dealer.es/coches-segunda-mano"


@pytest.mark.unit
def test_find_stock_url_skips_marketplaces():
    home = '<a href="https://facebook.com/dealer/coches">fb</a><a href="/stock">real</a>'
    assert find_stock_url(home, "https://dealer.es") == "https://dealer.es/stock"
