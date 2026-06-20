"""P04 recipe-first: extractor de coches.net (platform-as-entity, API JSON web.gw.coches.net/search).

Reusa pipeline.platform.coches_net_wholesale.parse_item_vehicle (NO un 2o scraper): POST page-1
size=k -> muestra -> VAM -> receta persistida. Todo OFFLINE (CochesFetcher.fetch_page + write_recipe mockeados).
"""
from __future__ import annotations

import asyncio

import pytest

from pipeline.platform import coches_net_wholesale as ccn
from pipeline.recipe_extractors import CochesNetExtractor
from pipeline.recipe_harness import RecipeHarness
from pipeline.recipe_schema import STATUS_VERIFIED

_RESP = {
    "items": [
        {"id": 4001, "url": "/coches-segunda-mano/seat-leon-4001", "make": "SEAT",
         "model": "Leon", "title": "SEAT Leon 1.5 TSI", "year": 2020, "km": 50000,
         "price": {"amount": 14900}, "fuelType": "Gasolina"},
        {"id": 4002, "url": "/coches-segunda-mano/vw-golf-4002", "make": "Volkswagen",
         "model": "Golf", "year": 2021, "km": 30000, "price": {"amount": 22500}},
        {"id": 4003, "url": "/coches-segunda-mano/audi-a3-4003", "make": "Audi",
         "model": "A3", "year": 2019, "km": 70000, "price": {"amount": 19900}},
    ],
    "meta": {"totalResults": 3},
}


@pytest.mark.unit
def test_coches_net_is_registered():
    from pipeline.recipe_extractors import EXTRACTORS
    assert EXTRACTORS.get("coches_net") is CochesNetExtractor


@pytest.mark.unit
def test_coches_net_recipe_first_verified(monkeypatch):
    monkeypatch.setattr(ccn.CochesFetcher, "fetch_page", lambda self, url, **kw: _RESP)
    captured: dict = {}
    monkeypatch.setattr(
        "pipeline.recipe_harness.write_recipe",
        lambda slug, d: (captured.update(slug=slug, recipe=d) or "/tmp/_test_recipe.yaml"))

    harness = RecipeHarness(CochesNetExtractor(), conn=None, now_iso="2026-06-20T00:00:00Z")
    res = asyncio.run(harness.run("coches.net", k=3))

    assert res.status == STATUS_VERIFIED, f"esperado VERIFIED, fue {res.status}: {res.reason}"
    assert res.fetched == 3 and res.parsed == 3
    assert res.verdict == "TRUSTWORTHY"  # 3==3==3 (fetched/parsed/declared), full_dealer
    assert captured["recipe"]["status"] == STATUS_VERIFIED
    assert captured["recipe"]["source"] == "coches_net"


@pytest.mark.unit
def test_coches_net_empty_is_failed(monkeypatch):
    # gateway sin items (DataDome interstitial / 0 resultados) -> muestra vacia -> FAILED honesto.
    monkeypatch.setattr(ccn.CochesFetcher, "fetch_page",
                        lambda self, url, **kw: {"items": [], "meta": {"totalResults": 0}})
    monkeypatch.setattr("pipeline.recipe_harness.write_recipe",
                        lambda slug, d: "/tmp/_test_recipe.yaml")
    harness = RecipeHarness(CochesNetExtractor(), conn=None, now_iso="2026-06-20T00:00:00Z")
    res = asyncio.run(harness.run("coches.net", k=3))
    assert res.status != STATUS_VERIFIED
    assert res.parsed == 0
