"""Offline unit tests for the adaptive CSS-selector rung (§4 ladder rung 4, ``engine='css'``).

Pure + fixture-driven: synthetic SSR listings (no JSON-LD), an injected ``fetch_fn`` (zero
network), and the harness's PURE verdict logic (no DB, no disk). Proves the rung (a) induces the
repeated card pattern and the per-field CSS selectors, (b) extracts the N vehicles through those
selectors, (c) reaches VERIFIED via the reused ``decide_status``, and (d) returns an HONEST empty
sample (no invented cars) when there is no repeated card pattern.
"""
from __future__ import annotations

import pytest

from pipeline.recipe_extract_css import CssAdaptiveExtractor, derive_css_recipe
from pipeline.recipe_harness import RecipeHarness, decide_status, sample_paths
from pipeline.recipe_schema import STATUS_FAILED, STATUS_VERIFIED

pytestmark = pytest.mark.unit

_BASE = "https://dealer.xx/stock"

# A country 'XX' SSR listing with 3 vehicle cards, NO JSON-LD/microdata. Nav + footer carry
# non-vehicle links (must be ignored). Specs sit in class-bearing spans inside each card.
_LISTING_XX = """<!doctype html><html lang="xx"><head><title>Stock XX</title></head>
<body>
  <header><nav>
    <a href="/inicio">Inicio</a><a href="/contacto">Contacto</a>
  </nav></header>
  <main>
    <h1>Vehiculos de ocasion - 3 vehiculos en stock</h1>
    <section class="results">
      <article class="vehicle-card">
        <a class="title" href="/coches-segunda-mano/bmw/x5/3-0d-2019-90000-17769">BMW X5 3.0d</a>
        <span class="precio">29.990 &euro;</span>
        <span class="anyo">2019</span>
        <span class="kms">90.000 km</span>
      </article>
      <article class="vehicle-card">
        <a class="title" href="/coches-segunda-mano/audi/a4/2-0-tdi-2018-60000-17770">Audi A4 2.0 TDI</a>
        <span class="precio">21.500 &euro;</span>
        <span class="anyo">2018</span>
        <span class="kms">60.000 km</span>
      </article>
      <article class="vehicle-card">
        <a class="title" href="/coches-segunda-mano/seat/leon/1-5-tsi-2020-30000-17771">Seat Leon 1.5 TSI</a>
        <span class="precio">18.900 &euro;</span>
        <span class="anyo">2020</span>
        <span class="kms">30.000 km</span>
      </article>
    </section>
    <a href="/coches-ocasion/">Ver todos los coches</a>
  </main>
</body></html>"""

# A page with NO per-vehicle card pattern: only nav, a blog post, and a category link.
_NO_CARDS = """<!doctype html><html><body>
  <header><nav>
    <a href="/inicio">Inicio</a><a href="/contacto">Contacto</a>
    <a href="/blog/como-comprar-coche-segunda-mano">Blog</a>
  </nav></header>
  <main><h1>Bienvenido</h1><p>Sin inventario online.</p>
    <a href="/coches-ocasion/">Ver coches</a>
  </main>
</body></html>"""

# A SINGLE vehicle (a real PDP link, but no REPEATED card structure to induce a pattern from).
_SINGLE = """<html><body><main>
  <article class="vehicle-card">
    <a class="title" href="/coches-segunda-mano/bmw/x5/3-0d-2019-90000-17769">BMW X5</a>
    <span class="precio">29.990 &euro;</span>
  </article>
</main></body></html>"""

# A structurally DIFFERENT listing: class-less <li> cards under a <ul>, price in <b>. Proves the
# derivation is structural (induced) — not hardcoded to the <article class="vehicle-card"> shape.
_LI_LISTING = """<html><body>
  <ul class="list">
    <li><a href="/stock/coche-bmw-serie3-2019-1001">BMW Serie 3</a> <b class="p">18.900 &euro;</b></li>
    <li><a href="/stock/coche-seat-leon-2018-1002">Seat Leon</a> <b class="p">14.500 &euro;</b></li>
  </ul>
</body></html>"""


def _fetch(html: str):
    """An injected transport that returns a fixed fixture for any URL (zero network)."""
    return lambda _url, **_kw: html


# --- derivation + extraction --------------------------------------------------------------------
def test_derive_induces_card_pattern_and_selectors():
    res = derive_css_recipe(_LISTING_XX, _BASE)
    assert res is not None
    container, fmap, vehicles, declared = res
    # the repeated card container is induced and scoped by its listing section
    assert container == "section.results article.vehicle-card"
    # each field's selector is auto-derived to the leaf element bearing the value
    assert fmap["price"] == "span.precio"
    assert fmap["year"] == "span.anyo"
    assert fmap["km"] == "span.kms"
    assert fmap["title"] == "a.title"
    assert fmap["url"].startswith("a.title")          # a.title::attr(href)
    assert fmap["make"] == "a.title" and fmap["model"] == "a.title"
    assert declared == 3
    assert len(vehicles) == 3


def test_extracts_all_vehicles_with_fields():
    _c, _f, vehicles, _d = derive_css_recipe(_LISTING_XX, _BASE)
    bmw = next(v for v in vehicles if v["url"].endswith("17769"))
    assert bmw["url"] == "https://dealer.xx/coches-segunda-mano/bmw/x5/3-0d-2019-90000-17769"
    assert bmw["price"] == 29990.0 and bmw["year"] == 2019 and bmw["km"] == 90000
    assert bmw["title"] == "BMW X5 3.0d"
    assert bmw["make"] == "BMW" and bmw["model"] == "X5 3.0d"
    seat = next(v for v in vehicles if v["url"].endswith("17771"))
    assert seat["price"] == 18900.0 and seat["make"] == "Seat" and seat["model"] == "Leon 1.5 TSI"


def test_derivation_is_structural_not_hardcoded():
    # class-less <li> cards, price in <b> — a different DOM shape, still induced correctly.
    container, fmap, vehicles, _d = derive_css_recipe(_LI_LISTING, "https://d.xx/")
    assert container == "ul.list li"
    assert fmap["price"] == "b.p"
    assert fmap["url"].startswith("a")
    assert len(vehicles) == 2
    assert vehicles[0]["price"] == 18900.0 and vehicles[0]["make"] == "BMW"
    assert all(v["url"].startswith("https://d.xx/stock/") for v in vehicles)


# --- the Extractor (engine='css') ---------------------------------------------------------------
def test_extractor_sample_full_dealer():
    ex = CssAdaptiveExtractor(fetch_fn=_fetch(_LISTING_XX))
    s = ex.sample(_BASE, k=5)
    assert s.fetched == 3 and len(s.parsed) == 3
    assert s.fetched - len(s.parsed) == 0          # zero parse loss
    assert s.declared == 3 and s.full_dealer is True


def test_recipe_template_carries_derived_css():
    ex = CssAdaptiveExtractor(fetch_fn=_fetch(_LISTING_XX))
    ex.sample(_BASE, k=5)                           # derive first (stashes selectors)
    r = ex.recipe_template(_BASE)
    assert r.parsing.engine == "css"
    assert r.parsing.container_path == "section.results article.vehicle-card"
    assert r.parsing.field_map["price"] == "span.precio"
    assert r.parsing.field_map["url"].startswith("a.title")
    assert r.source == "web_css" and r.transport.engine == "curl_cffi"


def test_reaches_verified_via_reused_harness_logic():
    # No DB, no disk: reuse the harness's PURE verdict + status logic (decide_status).
    ex = CssAdaptiveExtractor(fetch_fn=_fetch(_LISTING_XX))
    s = ex.sample(_BASE, k=5)
    paths = sample_paths(s)
    verdict = RecipeHarness._offline_verdict(paths)
    status, reason = decide_status(s, 5, verdict)
    assert status == STATUS_VERIFIED, reason
    assert paths == {"fetched": 3, "parsed": 3, "source_declared": 3}


# --- honest empty (no fabrication) --------------------------------------------------------------
def test_no_card_pattern_is_honest_empty():
    assert derive_css_recipe(_NO_CARDS, "https://dealer.xx/") is None
    ex = CssAdaptiveExtractor(fetch_fn=_fetch(_NO_CARDS))
    s = ex.sample("https://dealer.xx/", k=5)
    assert s.fetched == 0 and s.parsed == []
    status, reason = decide_status(s, 5, RecipeHarness._offline_verdict(sample_paths(s)))
    assert status == STATUS_FAILED and "empty sample" in reason
    # no selectors fabricated on the recipe
    r = ex.recipe_template("https://dealer.xx/")
    assert r.parsing.engine == "css"
    assert r.parsing.container_path is None and r.parsing.field_map == {}


def test_single_vehicle_no_repeat_is_honest_empty():
    # one PDP link, no repeated pattern -> the rung does NOT invent a one-car listing.
    assert derive_css_recipe(_SINGLE, "https://dealer.xx/") is None
    ex = CssAdaptiveExtractor(fetch_fn=_fetch(_SINGLE))
    s = ex.sample("https://dealer.xx/", k=5)
    assert s.fetched == 0 and s.parsed == []
