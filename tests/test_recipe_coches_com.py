"""P04 recipe-first: extractor de coches.com (platform-as-entity, SRP __NEXT_DATA__ abierto).

Reusa pipeline.platform.coches_com_wholesale.parse_card_vehicle (NO un 2o scraper): muestra k
cards de page-1 -> VAM -> receta persistida. Todo OFFLINE (fetch mockeado, write_recipe mockeado).
"""
from __future__ import annotations

import asyncio
import json

import pytest

from pipeline.recipe_extractors import CochesComExtractor
from pipeline.recipe_harness import RecipeHarness
from pipeline.recipe_schema import STATUS_VERIFIED

_CARDS = [
    {"visibleId": "100123", "make": {"name": "Seat"}, "model": {"name": "Leon"},
     "version": {"name": "1.5 TSI"}, "price": {"amount": 14900}, "registration": {"year": 2020},
     "mileage": {"amount": 50000}, "fuel": {"name": "Gasolina"},
     "transmission": {"name": "Manual"}, "image": "https://images.coches.com/x.jpg"},
    {"visibleId": "100124", "make": {"name": "Volkswagen"}, "model": {"name": "Golf"},
     "price": {"amount": 22500}, "registration": {"year": 2021}, "mileage": {"amount": 30000}},
    {"visibleId": "100125", "make": {"name": "Audi"}, "model": {"name": "A3"},
     "price": {"amount": 19900}, "registration": {"year": 2019}, "mileage": {"amount": 70000}},
]
_NEXT = {"props": {"pageProps": {"classifieds": {"total": 3, "classifiedList": _CARDS}}}}
_FIXTURE = ('<html><body><script id="__NEXT_DATA__" type="application/json">'
            + json.dumps(_NEXT) + '</script></body></html>')


@pytest.mark.unit
def test_coches_com_is_registered():
    from pipeline.recipe_extractors import EXTRACTORS
    assert EXTRACTORS.get("coches_com") is CochesComExtractor


@pytest.mark.unit
def test_coches_com_recipe_first_verified(monkeypatch):
    monkeypatch.setattr("pipeline.recipe_extractors.fetch_text", lambda url, **kw: _FIXTURE)
    captured: dict = {}
    monkeypatch.setattr(
        "pipeline.recipe_harness.write_recipe",
        lambda slug, d: (captured.update(slug=slug, recipe=d) or "/tmp/_test_recipe.yaml"))

    harness = RecipeHarness(CochesComExtractor(), conn=None, now_iso="2026-06-20T00:00:00Z")
    res = asyncio.run(harness.run("coches.com", k=3))

    assert res.status == STATUS_VERIFIED, f"esperado VERIFIED, fue {res.status}: {res.reason}"
    assert res.fetched == 3 and res.parsed == 3
    assert res.verdict == "TRUSTWORTHY"  # 3==3==3 (fetched/parsed/declared), full_dealer
    assert captured["recipe"]["status"] == STATUS_VERIFIED
    assert captured["recipe"]["source"] == "coches_com"


@pytest.mark.unit
def test_coches_com_imperva_interstitial_is_failed(monkeypatch):
    # surface sin __NEXT_DATA__ (Imperva 405/interstitial) -> muestra vacia -> FAILED honesto.
    monkeypatch.setattr("pipeline.recipe_extractors.fetch_text",
                        lambda url, **kw: "<html><body>Access denied (Imperva)</body></html>")
    monkeypatch.setattr("pipeline.recipe_harness.write_recipe",
                        lambda slug, d: "/tmp/_test_recipe.yaml")
    harness = RecipeHarness(CochesComExtractor(), conn=None, now_iso="2026-06-20T00:00:00Z")
    res = asyncio.run(harness.run("coches.com", k=3))
    assert res.status != STATUS_VERIFIED
    assert res.parsed == 0
