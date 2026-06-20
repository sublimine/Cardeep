"""P04 recipe-first MULTI-STEP: autocasion (SSR enumera -ref{id} -> GraphQL ad() hidrata).

Reusa pipeline.platform.autocasion_wholesale.parse_ssr_refs + parse_ad (NO un 2o scraper).
Offline: fake AutocasionFetcher (sin warm-up de red) que devuelve el SSR en GET y el ad JSON en POST.
"""
from __future__ import annotations

import asyncio
import json
import re

import pytest

from pipeline.platform import autocasion_wholesale as ac
from pipeline.recipe_extractors import AutocasionExtractor
from pipeline.recipe_harness import RecipeHarness
from pipeline.recipe_schema import STATUS_VERIFIED

_SSR = (
    '<html><body>'
    '<a href="/coches-seat-leon-ref4001">Seat</a>'
    '<a href="/coches-volkswagen-golf-ref4002">VW</a>'
    '<a href="/coches-audi-a3-ref4003">Audi</a>'
    '</body></html>'
)
_ADS = {
    "4001": {"id": 4001, "url": "/coches-seat-leon-ref4001", "price": 14900, "year": 2020,
             "kilometers": 50000, "brand": {"name": "Seat"}, "family": {"name": "Leon"},
             "title": "Seat Leon 1.5 TSI", "fuel": {"name": "Gasolina"},
             "transmission": {"name": "Manual"}},
    "4002": {"id": 4002, "url": "/coches-volkswagen-golf-ref4002", "price": 22500, "year": 2021,
             "kilometers": 30000, "brand": {"name": "Volkswagen"}, "family": {"name": "Golf"}},
    "4003": {"id": 4003, "url": "/coches-audi-a3-ref4003", "price": 19900, "year": 2019,
             "kilometers": 70000, "brand": {"name": "Audi"}, "family": {"name": "A3"}},
}


class _FakeFetcher:
    last_status = 200

    def __init__(self) -> None:  # sin warm-up de red
        pass

    def fetch(self, url, *, method: str = "GET", gql=None) -> str:
        if method == "POST":
            m = re.search(r"(\d{3,})", (gql or {}).get("query", ""))
            ad = _ADS.get(m.group(1)) if m else None
            return json.dumps({"data": {"ad": ad}})
        return _SSR


@pytest.mark.unit
def test_autocasion_is_registered():
    from pipeline.recipe_extractors import EXTRACTORS
    assert EXTRACTORS.get("autocasion") is AutocasionExtractor


@pytest.mark.unit
def test_autocasion_recipe_first_verified(monkeypatch):
    monkeypatch.setattr(ac, "AutocasionFetcher", _FakeFetcher)
    captured: dict = {}
    monkeypatch.setattr(
        "pipeline.recipe_harness.write_recipe",
        lambda slug, d: (captured.update(slug=slug, recipe=d) or "/tmp/_t.yaml"))

    harness = RecipeHarness(AutocasionExtractor(), conn=None, now_iso="2026-06-20T00:00:00Z")
    res = asyncio.run(harness.run("autocasion.com", k=3))

    assert res.status == STATUS_VERIFIED, f"esperado VERIFIED, fue {res.status}: {res.reason}"
    assert res.fetched == 3 and res.parsed == 3
    assert res.verdict == "TRUSTWORTHY"  # {fetched:3, parsed:3} concuerdan (declared None)
    assert captured["recipe"]["source"] == "autocasion"


@pytest.mark.unit
def test_autocasion_empty_ssr_is_failed(monkeypatch):
    class _Empty(_FakeFetcher):
        def fetch(self, url, *, method="GET", gql=None) -> str:
            return "<html><body>sin refs</body></html>"

    monkeypatch.setattr(ac, "AutocasionFetcher", _Empty)
    monkeypatch.setattr("pipeline.recipe_harness.write_recipe", lambda slug, d: "/tmp/_t.yaml")
    harness = RecipeHarness(AutocasionExtractor(), conn=None, now_iso="2026-06-20T00:00:00Z")
    res = asyncio.run(harness.run("autocasion.com", k=3))
    assert res.status != STATUS_VERIFIED
    assert res.parsed == 0
