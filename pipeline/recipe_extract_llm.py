"""LLM-selector inventory extractor — the §02 cost-ladder rung 7 (``engine='llm_local'``).

The COSTLIEST rung, reached only when every structured data-layer rung (json_api / next_data /
jsonld, cost 0-2) AND the structural CSS-induction rung (:mod:`pipeline.recipe_extract_css`, cost 4)
have FAILED: an HTML so bespoke that no repeated per-vehicle card pattern can be induced — PDP links
a URL heuristic does not recognise, an irregular DOM. Here a language MODEL reasons over the
arbitrary HTML and INFERS a field-map (the CSS selectors that locate each vehicle field).

The model is INJECTED (``llm_fn``), so the rung is framework-only and the heavy/paid part stays at
the frontier: in runtime ``llm_fn`` is the real €0 LOCAL Ollama (:func:`ollama_field_map_fn`,
owner-gated — needs a running daemon) or a hosted flash model; in the pure suite it is a
deterministic mock. The real model never runs in a test.

NO BLIND TRUST (the cardinal anti-hallucination rule): the model's field-map is not believed, it is
EXERCISED. The inferred selectors are applied to the very HTML the model read; a vehicle counts only
if its selector resolves to a real node bearing a real signal (a PDP href + a parseable
price/year/km). If the field-map extracts NO grounded car, the sample is honestly EMPTY and the
harness marks the recipe FAILED (:func:`pipeline.recipe_harness.decide_status`) — the rung never
emits a car the HTML does not contain. Because this rung trusts the model (not ``classify_loc``) to
identify the PDP link, its validity bar is deliberately STRICTER than the css rung's: a record needs
a numeric vehicle signal (price/year/km), not a bare title, to count.

Reuse, not reinvention: the minimal CSS applier (:func:`pipeline.recipe_extract_css._select`) and the
make/model split (:func:`pipeline.recipe_extract_css._split_make_model`) are reused verbatim, and the
per-field value parsers come from the pure, unit-tested :mod:`pipeline.platform.dealerprobe`
classifiers — the model supplies only the WHERE (selectors), proven deterministic code supplies the
HOW (parse + range-check). Transport is injectable (``fetch_fn``) so tests run on synthetic HTML with
zero network; runtime fetches through the shared antidetection engine.
"""
from __future__ import annotations

import logging
from html import unescape
from typing import Any, Callable
from urllib.parse import urljoin

from lxml import html as lxml_html

# Mandated reuse: the per-field value parsers (range-checked, country-tolerant) and the minimal CSS
# applier + make/model lexicon split are the exact, already-proven primitives the css rung uses —
# re-deriving them here would be the reinvention §02 forbids. The model adds only selector inference.
from pipeline.platform.dealerprobe import _ssr_km, _ssr_price, _ssr_year
from pipeline.recipe_extract_css import _select, _split_make_model
from pipeline.recipe_harness import Sample
from pipeline.recipe_schema import Fingerprint, Pagination, Parsing, Recipe, Transport

log = logging.getLogger(__name__)

# The injected model contract: read arbitrary HTML + its base URL, return an inferred field-map
# (selectors, NOT data) or None when it cannot infer one. Shape:
#   {"container": "<css selector>" | None,        # the repeated per-vehicle block (None = whole doc)
#    "declared":  <int> | None,                   # the model's own total oracle (optional)
#    "fields":    {"url": "<sel>::attr(href)", "title": "<sel>",
#                  "price": "<sel>", "year": "<sel>", "km": "<sel>"}}
LlmFn = Callable[[str, str], "dict | None"]

_SKIP_HREF = ("#", "mailto:", "tel:", "javascript:", "whatsapp:", "sms:")
_VALUE_FIELDS = (("price", _ssr_price), ("year", _ssr_year), ("km", _ssr_km))


# ---------------------------------------------------------------------------
# Apply an inferred field-map to the HTML (dogfood: a selector that does not re-select a real,
# value-bearing node yields nothing — an honest miss, never a guess).
# ---------------------------------------------------------------------------
def _parse(html: str):
    if not html or not html.strip():
        return None
    try:
        return lxml_html.fromstring(html)
    except Exception:  # noqa: BLE001 — malformed bytes -> honest no-extraction, not a crash
        return None


def _extract_url(card, selector: str, base: str) -> str | None:
    """Resolve the model's url selector to a grounded absolute href. UNLIKE the css rung there is no
    ``classify_loc`` gate — the model is trusted to identify the PDP link (that IS its inference);
    the check here is GROUNDEDNESS: the selector must resolve to a real ``<a>`` bearing a real href
    in the HTML the model read, never a fabricated link."""
    for n in _select(card, selector):
        href = n.get("href")
        if not href:
            continue
        h = unescape(href).strip()
        if h and not h.lower().startswith(_SKIP_HREF):
            return urljoin(base, h)
    return None


def _extract_text(card, selector: str) -> str | None:
    for n in _select(card, selector):
        t = n.text_content().strip()
        if t:
            return t[:120]
    return None


def _extract_value(card, selector: str, valfn):
    for n in _select(card, selector):
        txt = (n.text or "").strip() or n.text_content().strip()
        v = valfn(txt)
        if v is not None:
            return v
    return None


def _extract_one(card, base: str, fields: dict) -> dict:
    url = _extract_url(card, fields["url"], base) if fields.get("url") else None
    title = _extract_text(card, fields["title"]) if fields.get("title") else None
    make, model = _split_make_model(title)
    v = {"url": url, "title": title, "make": make, "model": model,
         "year": None, "km": None, "price": None}
    for field, valfn in _VALUE_FIELDS:
        sel = fields.get(field)
        if sel:
            v[field] = _extract_value(card, sel, valfn)
    return v


def apply_field_map(html: str, base: str, fmap: Any) -> list[dict]:
    """Apply an inferred field-map to ``html``, one candidate vehicle per container node.

    Returns the raw candidates (validity is decided by :func:`_valid` downstream, so a parse loss —
    the model's container catching a non-vehicle node — surfaces honestly instead of being hidden).
    An empty/malformed field-map or one without a usable ``url`` selector yields ``[]``.
    """
    root = _parse(html)
    if root is None or not isinstance(fmap, dict):
        return []
    fields = fmap.get("fields")
    if not isinstance(fields, dict) or not fields.get("url"):
        return []  # no actionable per-vehicle link selector -> cannot action -> honest empty
    container = fmap.get("container")
    cards = _select(root, container) if container else [root]
    return [_extract_one(c, base, fields) for c in cards]


def _valid(v: dict) -> bool:
    """A sample-valid vehicle has a PDP url AND a numeric vehicle signal (price/year/km). Stricter
    than the css rung's bar (title alone does not count): this rung trusts the model — not a URL
    classifier — for the link, so it demands a hard signal to certify the node really is a car."""
    return bool(v.get("url")) and any(v.get(k) is not None for k in ("price", "year", "km"))


def _recipe_field_map(fmap: dict) -> dict[str, str]:
    """The durable selector asset for the persisted recipe (mirrors the css rung's field_map shape).
    make/model carry the title selector — the split is a downstream lexicon decision, not a DOM
    location."""
    fields = fmap.get("fields") or {}
    out: dict[str, str] = {}
    if fields.get("url"):
        out["url"] = fields["url"]
    if fields.get("title"):
        out["title"] = fields["title"]
        out["make"] = fields["title"]
        out["model"] = fields["title"]
    for f in ("price", "year", "km"):
        if fields.get(f):
            out[f] = fields[f]
    return out


# ---------------------------------------------------------------------------
# The harness Extractor (engine='llm_local').
# ---------------------------------------------------------------------------
def _engine_fetch(url: str, **_kw) -> str:
    """Default runtime transport: the shared antidetection engine (lazy-imported so this module
    imports with no network stack, and the unit tests inject a fixture ``fetch_fn`` instead). The
    browser-render tier that "unlocks" a JS-heavy bespoke page before the model reads it is an owner
    runtime decision; the framework only needs rendered HTML."""
    from pipeline.engine.fetch import fetch_text
    return fetch_text(url, tier=0)


class LlmFieldMapExtractor:
    """Harness Extractor for an arbitrary dealer listing cracked by an INJECTED LLM-selector model.

    Implements the :class:`pipeline.recipe_harness.Extractor` protocol (``source`` +
    ``recipe_template`` + ``sample``). ``sample`` asks the model for a field-map, applies + validates
    it, and stashes the inferred selectors per dealer; ``recipe_template`` emits them as
    ``Parsing(engine='llm_local', ...)`` so the cracker records the winning rung's selectors into the
    durable recipe (the next run can replay them without re-paying the model).
    """

    source = "web_llm"

    def __init__(self, llm_fn: LlmFn, fetch_fn: Callable[..., str] | None = None) -> None:
        if llm_fn is None:
            raise ValueError("LlmFieldMapExtractor requires an llm_fn (the injected model)")
        self._llm = llm_fn
        self._fetch = fetch_fn or _engine_fetch
        self._derived: dict[str, dict] = {}  # dealer_ref -> {container, field_map, declared}

    def recipe_template(self, dealer_ref: str) -> Recipe:
        d = self._derived.get(dealer_ref, {})
        return Recipe(
            source=self.source, dealer_ref=dealer_ref, kind="compraventa",
            transport=Transport(engine="browser", base_url=dealer_ref, impersonate="chrome",
                                 timeout_s=45),
            fingerprint=Fingerprint(user_agent="engine-managed"),
            pagination=Pagination(strategy="single_page", url_template=dealer_ref,
                                  declared_path="llm-inferred total", stop="empty_page"),
            parsing=Parsing(engine="llm_local", container_path=d.get("container"),
                            field_map=dict(d.get("field_map") or {})),
        )

    def sample(self, dealer_ref: str, k: int) -> Sample:
        html = self._fetch(dealer_ref)
        fmap = self._llm(html, dealer_ref) if (html and html.strip()) else None
        vehicles = apply_field_map(html or "", dealer_ref, fmap)
        sliced = vehicles[:k]
        parsed = [v for v in sliced if _valid(v)]
        if not parsed:
            # Honest empty: the model inferred nothing actionable, OR its field-map extracted no
            # grounded car -> no invented vehicle. The harness marks the recipe FAILED via
            # decide_status (empty / under-target), the correct recipe-first outcome.
            self._derived[dealer_ref] = {"container": None, "field_map": {}, "declared": None}
            return Sample(declared=None, fetched=len(sliced), parsed=[], full_dealer=False)
        declared = fmap.get("declared") if isinstance(fmap, dict) else None
        if not (isinstance(declared, int) and declared >= 0):
            declared = None
        self._derived[dealer_ref] = {
            "container": fmap.get("container"),
            "field_map": _recipe_field_map(fmap),
            "declared": declared,
        }
        full = declared is not None and declared <= len(sliced)
        return Sample(declared=declared, fetched=len(sliced), parsed=parsed, full_dealer=full)


# ---------------------------------------------------------------------------
# The real €0 LOCAL model arm — OWNER-GATED runtime (needs a running Ollama daemon). Never exercised
# by the pure suite, which injects a mock; it is the rung's production llm_fn, analogous to the css
# rung's _engine_fetch (real, behind the egress/spend gate).
# ---------------------------------------------------------------------------
_OLLAMA_URL = "http://localhost:11434/api/generate"
_OLLAMA_MODEL = "qwen2.5:7b"   # small local model strong at structured JSON; owner-swappable
_HTML_BUDGET = 24_000          # cap the prompt HTML so a huge page does not blow the context window
_LLM_PROMPT = (
    "You are a web-scraping selector inference engine. Given the HTML of a car-dealer inventory "
    "listing page, return ONLY a JSON object describing how to extract each vehicle, using CSS "
    "selectors in this minimal grammar: tag, .class, tag.class, descendant (space-separated), and "
    "tag.class::attr(href) for a link's href. Shape: "
    '{{"container": "<selector for one repeated vehicle block>", "declared": <total cars as int or null>, '
    '"fields": {{"url": "<link selector>::attr(href)", "title": "<selector>", "price": "<selector>", '
    '"year": "<selector>", "km": "<selector>"}}}}. '
    "If the page is not a vehicle listing, return {{}}. base_url={base_url}\n\nHTML:\n{html}"
)


def ollama_field_map_fn(html: str, base_url: str, *, url: str = _OLLAMA_URL,
                        model: str = _OLLAMA_MODEL) -> dict | None:
    """Real €0 LOCAL field-map inference via Ollama's generate API (OWNER-GATED: needs a running
    Ollama daemon at ``url``; never called by the pure suite). Returns the parsed field-map, or None
    on ANY failure — a model that cannot answer yields no field-map, not a guess (anti-hallucination).
    """
    import json
    import urllib.request

    body = json.dumps({
        "model": model,
        "prompt": _LLM_PROMPT.format(base_url=base_url, html=(html or "")[:_HTML_BUDGET]),
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
    }).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        inferred = json.loads(payload.get("response") or "{}")
    except Exception as exc:  # noqa: BLE001 — a model/daemon failure is an honest no-inference
        log.warning("ollama_field_map_fn: inference failed (%s) — no field-map", exc)
        return None
    return inferred if isinstance(inferred, dict) and inferred.get("fields") else None
