"""P04 recipe-first: el extractor de web propia (GenericWebExtractor) debe estar REGISTRADO
y funcionar end-to-end por el harness (EXTRACT muestra -> VERIFY VAM -> PERSIST receta -> DELETE).

Antes: EXTRACTORS solo tenia 'autoscout24'; el GenericWebExtractor existia pero NO estaba
registrado -> RecipeRunner.replay y el harness no podian usarlo para dealers con web propia.
Fix: registrar 'web_generic'. Asi "cada dealer/entidad con huella digital (web propia)"
valida su extraccion por VAM y guarda su receta/config. Todo offline (fetch mockeado, sin DB)."""
from __future__ import annotations

import asyncio

import pytest

from pipeline.recipe_extract_web import GenericWebExtractor
from pipeline.recipe_harness import RecipeHarness
from pipeline.recipe_schema import STATUS_VERIFIED

# Fixture: pagina de dealer con 3 coches en schema.org JSON-LD + el conteo declarado en texto.
_FIXTURE_HTML = (
    '<html><head>'
    '<script type="application/ld+json">'
    '[{"@type":"Car","name":"Seat Leon 1.5 TSI","offers":{"@type":"Offer","price":"14900"},"url":"https://d.test/leon"},'
    '{"@type":"Car","name":"VW Golf GTI","offers":{"price":"22500"},"url":"https://d.test/golf"},'
    '{"@type":"Vehicle","name":"Audi A3 Sportback","offers":{"price":"19900"},"url":"https://d.test/a3"}]'
    '</script></head><body>3 vehiculos en stock</body></html>'
)


@pytest.mark.unit
def test_web_generic_is_registered():
    from pipeline.recipe_extractors import EXTRACTORS
    assert EXTRACTORS.get("web_generic") is GenericWebExtractor


@pytest.mark.unit
def test_generic_web_recipe_first_verified(monkeypatch):
    # mock del transporte: el sample no toca la red, parsea el fixture JSON-LD.
    monkeypatch.setattr("pipeline.recipe_extract_web.fetch_text",
                        lambda url, **kw: _FIXTURE_HTML)
    # mock del persist: capturamos la receta sin escribir a disco (sin side effects).
    captured: dict = {}
    monkeypatch.setattr(
        "pipeline.recipe_harness.write_recipe",
        lambda slug, d: (captured.update(slug=slug, recipe=d) or "/tmp/_test_recipe.yaml"))

    harness = RecipeHarness(GenericWebExtractor(), conn=None, now_iso="2026-06-20T00:00:00Z")
    res = asyncio.run(harness.run("https://d.test/", k=3))

    assert res.status == STATUS_VERIFIED, f"esperado VERIFIED, fue {res.status}: {res.reason}"
    assert res.fetched == 3 and res.parsed == 3  # extraccion sin perdida
    assert res.verdict == "TRUSTWORTHY"           # 3==3==3 (fetched/parsed/declared) full_dealer
    # la receta/config quedo construida y persistida (capturada) con estado VERIFIED
    assert captured["recipe"]["status"] == STATUS_VERIFIED
    assert captured["recipe"]["source"] == "web_generic"
    assert captured["recipe"]["evidence"]["parsed"] == 3


@pytest.mark.unit
def test_empty_sample_is_failed_not_fake_success(monkeypatch):
    # web sin JSON-LD (web "cutre" JS-rendered) -> muestra vacia -> FAILED honesto, no exito falso.
    monkeypatch.setattr("pipeline.recipe_extract_web.fetch_text",
                        lambda url, **kw: "<html><body>no structured data</body></html>")
    monkeypatch.setattr("pipeline.recipe_harness.write_recipe",
                        lambda slug, d: "/tmp/_test_recipe.yaml")
    harness = RecipeHarness(GenericWebExtractor(), conn=None, now_iso="2026-06-20T00:00:00Z")
    res = asyncio.run(harness.run("https://empty.test/", k=3))
    assert res.status != STATUS_VERIFIED
    assert res.parsed == 0
