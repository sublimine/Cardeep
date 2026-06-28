"""Offline golden for the §02 cost-LADDER integration: the css (rung 4) and llm_local (rung 7)
rungs wired into the cracker, and the orchestrator escalating cheap->expensive across them.

Two layers, all pure (no DB, no network, NO real LLM):

  A) the llm_local rung in isolation — its INJECTED model (``llm_fn``, a deterministic mock here;
     Ollama/Gemini in runtime) infers a field-map, the rung APPLIES + VALIDATES it, and reaches
     VERIFIED through the harness's reused verdict logic. Three honesty tests prove the rung does
     NOT trust the model blindly: a no-inference, a hallucinated-selector and a wrong-container
     field-map each yield an HONEST empty sample -> FAILED, never a fabricated car.

  B) the cracker ESCALATING over the real wired ladder (an explicit fixture ladder, the documented
     pure-suite shape): an SSR page with no data-layer escalates past the structured rungs to the
     css rung and VERIFIES there; a bespoke HTML that css structurally CANNOT induce (proven by
     ``derive_css_recipe(...) is None``) escalates one rung further to llm_local, whose injected
     mock cracks it. The real LLM never runs — the rung is driven by the mock and a fixture fetch.

The live VAM seal (record_count_verdict) is async + DB-backed with its own tests; here conn is None
so the cracker uses the offline verdict mirror, exactly like test_recipe_cracker.py.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass

import pytest

from pipeline.recipe_cracker import LegacyRung, crack_recipe
from pipeline.recipe_extract_css import CssAdaptiveExtractor, derive_css_recipe
from pipeline.recipe_extract_llm import LlmFieldMapExtractor
from pipeline.recipe_harness import RecipeHarness, Sample, decide_status, sample_paths
from pipeline.recipe_schema import (
    STATUS_FAILED,
    STATUS_VERIFIED,
    Parsing,
    Recipe,
    Transport,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Fixtures (synthetic HTML; zero network).
# ---------------------------------------------------------------------------
_SSR_BASE = "https://dealer.ssr/stock"

# An SSR listing with 3 vehicle cards and NO JSON-LD/microdata: the data-layer rungs (json_api /
# next_data / jsonld) find nothing, but the css rung structurally induces the repeated card.
_SSR_LISTING = """<!doctype html><html lang="xx"><head><title>Stock</title></head>
<body>
  <header><nav><a href="/inicio">Inicio</a><a href="/contacto">Contacto</a></nav></header>
  <main>
    <h1>Ocasion - 3 vehiculos en stock</h1>
    <section class="results">
      <article class="vehicle-card">
        <a class="title" href="/coches-segunda-mano/bmw/x5/3-0d-2019-90000-17769">BMW X5 3.0d</a>
        <span class="precio">29.990 &euro;</span><span class="anyo">2019</span><span class="kms">90.000 km</span>
      </article>
      <article class="vehicle-card">
        <a class="title" href="/coches-segunda-mano/audi/a4/2-0-tdi-2018-60000-17770">Audi A4 2.0 TDI</a>
        <span class="precio">21.500 &euro;</span><span class="anyo">2018</span><span class="kms">60.000 km</span>
      </article>
      <article class="vehicle-card">
        <a class="title" href="/coches-segunda-mano/seat/leon/1-5-tsi-2020-30000-17771">Seat Leon 1.5 TSI</a>
        <span class="precio">18.900 &euro;</span><span class="anyo">2020</span><span class="kms">30.000 km</span>
      </article>
    </section>
  </main>
</body></html>"""

_BESPOKE_BASE = "https://dealer.bespoke/inventory"

# A BESPOKE listing css cannot crack: the PDP links (/inventory/item/<id>) carry no car-surface
# segment, so classify_loc rejects them -> css finds <2 per-vehicle anchors -> derive returns None.
# The structure IS there (repeated div.car blocks), but only an LLM reasoning semantically over the
# arbitrary DOM identifies it. This is the exact page the §02 ladder reserves for rung 7.
_BESPOKE = """<!doctype html><html><head><title>Inventory</title></head>
<body>
  <header><nav><a href="/home">Home</a><a href="/about">About</a></nav></header>
  <main>
    <div class="inventory">
      <div class="car">
        <a class="detail" href="/inventory/item/12345">Mercedes C200</a>
        <h3 class="name">Mercedes C200</h3>
        <span class="cost">24.500 &euro;</span><span class="yr">2019</span><span class="mi">45.000 km</span>
      </div>
      <div class="car">
        <a class="detail" href="/inventory/item/12346">Volkswagen Golf</a>
        <h3 class="name">Volkswagen Golf</h3>
        <span class="cost">17.900 &euro;</span><span class="yr">2020</span><span class="mi">28.000 km</span>
      </div>
      <div class="car">
        <a class="detail" href="/inventory/item/12347">Toyota Corolla</a>
        <h3 class="name">Toyota Corolla</h3>
        <span class="cost">19.500 &euro;</span><span class="yr">2021</span><span class="mi">15.000 km</span>
      </div>
    </div>
  </main>
</body></html>"""

# The field-map the mock model "infers" for the bespoke page: container + per-field CSS selectors
# (the §02 rung-7 contract is LLM-as-selector, not LLM-as-data). ``declared`` is the model's own
# total oracle (admits the full-dealer quorum). The rung APPLIES these and validates the output.
_BESPOKE_FIELD_MAP = {
    "container": "div.car",
    "declared": 3,
    "fields": {
        "url": "a.detail::attr(href)",
        "title": "h3.name",
        "price": "span.cost",
        "year": "span.yr",
        "km": "span.mi",
    },
}


def _fetch(html: str):
    """A construction-injected transport returning a fixed fixture for any URL (zero network)."""
    return lambda _url, **_kw: html


def _mock_llm(returns):
    """A deterministic stand-in for the runtime model (Ollama/Gemini): records every call so a test
    can prove the rung actually invoked the injected model, and returns a canned field-map."""
    calls: list[tuple[str, str]] = []

    def _fn(html: str, base: str):
        calls.append((html, base))
        return returns

    _fn.calls = calls  # type: ignore[attr-defined]
    return _fn


# ---------------------------------------------------------------------------
# A) the llm_local rung in isolation — mock model + output validation.
# ---------------------------------------------------------------------------
def test_llm_rung_cracks_bespoke_html_that_css_cannot_induce():
    # PROOF the llm rung is genuinely the harder rung: the structural css rung returns None here.
    assert derive_css_recipe(_BESPOKE, _BESPOKE_BASE) is None

    llm = _mock_llm(_BESPOKE_FIELD_MAP)
    ex = LlmFieldMapExtractor(llm_fn=llm, fetch_fn=_fetch(_BESPOKE))
    s = ex.sample(_BESPOKE_BASE, k=5)

    assert s.fetched == 3 and len(s.parsed) == 3
    assert s.fetched - len(s.parsed) == 0           # zero parse loss
    assert len(llm.calls) == 1                       # the injected model actually ran

    # reuse the harness PURE verdict + status logic (no DB, no disk) -> VERIFIED
    verdict = RecipeHarness._offline_verdict(sample_paths(s))
    status, reason = decide_status(s, 5, verdict)
    assert status == STATUS_VERIFIED, reason

    # the extracted cars are GROUNDED in the HTML the model read (not invented)
    mercedes = next(v for v in s.parsed if v["url"].endswith("12345"))
    assert mercedes["url"] == "https://dealer.bespoke/inventory/item/12345"
    assert mercedes["price"] == 24500.0 and mercedes["year"] == 2019 and mercedes["km"] == 45000
    assert mercedes["make"] == "Mercedes" and mercedes["model"] == "C200"


def test_llm_recipe_template_carries_the_inferred_field_map():
    llm = _mock_llm(_BESPOKE_FIELD_MAP)
    ex = LlmFieldMapExtractor(llm_fn=llm, fetch_fn=_fetch(_BESPOKE))
    ex.sample(_BESPOKE_BASE, k=5)                     # infer first (stashes the field-map)
    r = ex.recipe_template(_BESPOKE_BASE)
    assert r.parsing.engine == "llm_local"
    assert r.parsing.container_path == "div.car"
    assert r.parsing.field_map["price"] == "span.cost"
    assert r.parsing.field_map["url"] == "a.detail::attr(href)"
    assert r.parsing.field_map["make"] == "h3.name"  # make/model carry the title selector
    assert r.source == "web_llm" and r.transport.engine == "browser"


def test_llm_rung_no_inference_is_honest_empty():
    # the model could not infer a field-map (returns None) -> no invented car, honest FAILED.
    llm = _mock_llm(None)
    ex = LlmFieldMapExtractor(llm_fn=llm, fetch_fn=_fetch(_BESPOKE))
    s = ex.sample(_BESPOKE_BASE, k=5)
    assert s.fetched == 0 and s.parsed == []
    status, reason = decide_status(s, 5, RecipeHarness._offline_verdict(sample_paths(s)))
    assert status == STATUS_FAILED and "empty sample" in reason
    r = ex.recipe_template(_BESPOKE_BASE)
    assert r.parsing.container_path is None and r.parsing.field_map == {}


def test_llm_rung_hallucinated_selectors_extract_nothing_failed():
    # the model returns selectors that match NO node -> applying them yields nothing -> the rung
    # does not trust them blindly -> honest empty -> FAILED (no fabricated car).
    llm = _mock_llm({"container": "div.does-not-exist",
                     "fields": {"url": "a.ghost::attr(href)", "price": "span.ghost"}})
    ex = LlmFieldMapExtractor(llm_fn=llm, fetch_fn=_fetch(_BESPOKE))
    s = ex.sample(_BESPOKE_BASE, k=5)
    assert s.fetched == 0 and s.parsed == []
    status, _ = decide_status(s, 5, RecipeHarness._offline_verdict(sample_paths(s)))
    assert status == STATUS_FAILED


def test_llm_rung_wrong_container_validates_output_failed():
    # the model points the container at a NON-vehicle block (nav). The url selector resolves to a
    # real node, but the record carries no vehicle signal (no price/year/km) -> it is INVALID. The
    # rung validates the OUTPUT; it does not emit a car just because a selector matched.
    llm = _mock_llm({"container": "nav", "fields": {"url": "a::attr(href)", "title": "a"}})
    ex = LlmFieldMapExtractor(llm_fn=llm, fetch_fn=_fetch(_BESPOKE))
    s = ex.sample(_BESPOKE_BASE, k=5)
    assert len(s.parsed) == 0
    status, _ = decide_status(s, 5, RecipeHarness._offline_verdict(sample_paths(s)))
    assert status == STATUS_FAILED


# ---------------------------------------------------------------------------
# B) the cracker escalating over the real wired ladder (css + llm_local).
# ---------------------------------------------------------------------------
@dataclass
class _DataLayerMiss:
    """A cheap data-layer rung (json_api / next_data / jsonld stand-in) that finds NO structured
    data on an SSR page -> honest empty sample. Owns its (trivial) transport, like the production
    legacy rungs that fetch internally; the cracker's fetch_fn is unused."""

    source: str
    cost: int

    def recipe_template(self, target: str) -> Recipe:
        return Recipe(source=self.source, dealer_ref=target,
                      transport=Transport(engine="curl_cffi", base_url=target),
                      parsing=Parsing(engine="next_data"))

    def extract(self, target: str, fetch_fn) -> Sample:
        return Sample(declared=None, fetched=0, parsed=[], full_dealer=False)


def _wired_ladder(*, css_html: str, llm_html: str, llm_fn):
    """The real §02 ladder for the pure suite: structured rungs (fixture misses) + the REAL css and
    llm_local extractors, fixture-fed via construction (the documented explicit-fixture-ladder shape;
    LegacyRung is the existing Extractor->Rung adapter)."""
    return [
        _DataLayerMiss("json_api", 0),
        _DataLayerMiss("next_data", 1),
        _DataLayerMiss("jsonld", 2),
        LegacyRung(CssAdaptiveExtractor(fetch_fn=_fetch(css_html)), cost=4),
        LegacyRung(LlmFieldMapExtractor(llm_fn=llm_fn, fetch_fn=_fetch(llm_html)), cost=7),
    ]


def _capture():
    """An in-memory persist_fn (no disk): records (key, payload) and returns a stand-in path."""
    seen: list[tuple[str, dict]] = []

    def _persist(key: str, payload: dict) -> str:
        seen.append((key, payload))
        return f"memory://{key}"

    _persist.seen = seen  # type: ignore[attr-defined]
    return _persist


_UNUSED_FETCH = lambda *a, **k: None  # noqa: E731 — every wired rung owns its transport


def test_crack_escalates_past_data_layer_to_css_and_verifies():
    llm = _mock_llm(_BESPOKE_FIELD_MAP)       # would also crack — must NOT be probed (css wins first)
    ladder = _wired_ladder(css_html=_SSR_LISTING, llm_html=_SSR_LISTING, llm_fn=llm)
    persist = _capture()

    res = asyncio.run(crack_recipe(_SSR_BASE, fetch_fn=_UNUSED_FETCH, ladder=ladder,
                                   persist_fn=persist, now_iso="2026-06-28T00:00:00Z"))

    assert res.status == STATUS_VERIFIED
    assert res.winning_source == "web_css"
    assert res.winning_rung == 3              # cost-sorted ladder index (costs 0,1,2,4,7)
    # escalation: the three data-layer rungs FAILED, css VERIFIED, the costly llm rung untouched.
    assert [a.source for a in res.attempts] == ["json_api", "next_data", "jsonld", "web_css"]
    assert all(a.status == STATUS_FAILED for a in res.attempts[:3])
    assert res.attempts[3].status == STATUS_VERIFIED
    assert llm.calls == []                     # the LLM (and any real model) was never invoked

    # the persisted recipe carries the css engine + the §9.4 winning-rung seed.
    assert len(persist.seen) == 1
    key, payload = persist.seen[0]
    assert key == "web_css__" + _SSR_BASE
    assert payload["parsing"]["engine"] == "css"
    assert payload["parsing"]["container_path"] == "section.results article.vehicle-card"
    assert payload["winning_rung"] == 3 and payload["winning_source"] == "web_css"
    assert payload["status"] == STATUS_VERIFIED


def test_crack_escalates_to_llm_when_only_llm_cracks():
    # css fetches the SAME bespoke HTML and structurally FAILS to induce it; only the llm rung's
    # injected mock cracks it. The cracker climbs the full ladder to rung 7.
    assert derive_css_recipe(_BESPOKE, _BESPOKE_BASE) is None   # css genuinely cannot crack this

    llm = _mock_llm(_BESPOKE_FIELD_MAP)
    ladder = _wired_ladder(css_html=_BESPOKE, llm_html=_BESPOKE, llm_fn=llm)
    persist = _capture()

    res = asyncio.run(crack_recipe(_BESPOKE_BASE, fetch_fn=_UNUSED_FETCH, ladder=ladder,
                                   persist_fn=persist, now_iso="2026-06-28T00:00:00Z"))

    assert res.status == STATUS_VERIFIED
    assert res.winning_source == "web_llm"
    assert res.winning_rung == 4
    # every cheaper rung was tried in cost order, each FAILED honestly, llm_local VERIFIED.
    assert [a.source for a in res.attempts] == [
        "json_api", "next_data", "jsonld", "web_css", "web_llm"]
    assert res.attempts[3].source == "web_css" and res.attempts[3].status == STATUS_FAILED
    assert "empty sample" in res.attempts[3].reason     # css honest empty (could not induce)
    assert res.attempts[4].status == STATUS_VERIFIED
    assert len(llm.calls) == 1                           # the injected model was the one that cracked it

    key, payload = persist.seen[0]
    assert key == "web_llm__" + _BESPOKE_BASE
    assert payload["parsing"]["engine"] == "llm_local"
    assert payload["parsing"]["container_path"] == "div.car"
    assert payload["parsing"]["field_map"]["price"] == "span.cost"
    assert payload["winning_rung"] == 4 and payload["winning_source"] == "web_llm"
