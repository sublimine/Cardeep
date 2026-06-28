"""Adaptive CSS-selector inventory extractor — the §4 cost ladder rung 4 (``engine='css'``).

This is the rung the cracker reaches for an SSR dealer site that server-renders its
inventory as repeated listing cards but exposes **no** schema.org JSON-LD/microdata — the
exact pages :class:`pipeline.recipe_extract_web.GenericWebExtractor` is forced to mark FAILED.
Instead of a per-dealer selector REGISTRY (the trap that kills hand-rolled connectors), this
rung **auto-derives** the selectors from the DOM, scrapling-style: it induces the repeated
card container structurally, then locates each field inside a card by SIGNAL (a per-vehicle
``<a>`` -> url; numeric-text classifiers -> price/year/km; the card's prominent text -> title,
and make/model split from it). The derived selectors are emitted on the recipe template
(``Parsing.engine='css'`` + ``field_map``) so the cracker grabs them and a replay re-selects
the same nodes — the selectors ARE the durable asset.

Reuse, not reinvention: the per-vehicle URL classifier and the numeric field value-parsers come
verbatim from :mod:`pipeline.platform.dealerprobe` (the pure, unit-tested SSR classifiers). What
is genuinely new here, and absent from ``parse_ssr_cards`` (a fixed regex window), is the
DOM-structural derivation of real CSS selectors — the missing rung.

Honesty (frontier doctrine): a page with no repeated per-vehicle card pattern yields ``None``
from :func:`derive_css_recipe` and an EMPTY sample from the extractor — never an invented car.
The harness then marks that recipe FAILED with a precise reason (``decide_status``), the correct
recipe-first outcome. Transport/fetch is injectable (``fetch_fn``) so tests run on synthetic
HTML fixtures with zero network, and runtime fetches through the shared antidetection engine.
"""
from __future__ import annotations

import logging
import re
from collections import Counter
from html import unescape
from urllib.parse import urljoin

from lxml import html as lxml_html

# Mandated reuse of the pure dealerprobe classifiers (per-vehicle URL signal + numeric value
# parsers). Importing the underscore value-parsers is deliberate: they are the exact, range-checked
# extractors the SSR rung already proved, and re-deriving them here would be the reinvention the
# §4 design forbids.
from pipeline.platform.dealerprobe import (
    _ssr_km,
    _ssr_price,
    _ssr_year,
    classify_loc,
)
from pipeline.recipe_harness import Sample
from pipeline.recipe_schema import Fingerprint, Pagination, Parsing, Recipe, Transport

log = logging.getLogger(__name__)

# A digit-led count phrase the listing prints near its results ("3 vehículos", "120 coches",
# "85 viaturas"). Multi-country tolerant — the declared oracle is optional, never fabricated.
_COUNT_HINT = re.compile(
    r"(\d{1,6})\s*(?:veh[ií]culos?|coches?|cars?|vehicles?|viaturas?|carros?|auto(?:s|m[oó]veis)?)\b",
    re.I)
_SKIP_HREF = ("#", "mailto:", "tel:", "javascript:", "whatsapp:", "sms:")
_HEADING_TAGS = ("h1", "h2", "h3", "h4", "h5")

# Make lexicon (normalized upper-case) used only to SPLIT a derived title into make/model. It is a
# signal, never a fabricator: an unmatched title yields make=model=None, the honest outcome.
_MAKES = (
    "ABARTH", "ALFA ROMEO", "ALPINE", "ASTON MARTIN", "AUDI", "BENTLEY", "BMW", "BYD", "CADILLAC",
    "CHEVROLET", "CHRYSLER", "CITROEN", "CUPRA", "DACIA", "DODGE", "DS", "FERRARI", "FIAT", "FORD",
    "GENESIS", "HONDA", "HYUNDAI", "INFINITI", "ISUZU", "IVECO", "JAGUAR", "JEEP", "KIA",
    "LAMBORGHINI", "LANCIA", "LAND ROVER", "LEXUS", "LOTUS", "MASERATI", "MAZDA", "MERCEDES",
    "MERCEDES-BENZ", "MG", "MINI", "MITSUBISHI", "NISSAN", "OPEL", "PEUGEOT", "POLESTAR",
    "PORSCHE", "RENAULT", "ROVER", "SAAB", "SEAT", "SKODA", "SMART", "SSANGYONG", "SUBARU",
    "SUZUKI", "TESLA", "TOYOTA", "VOLKSWAGEN", "VOLVO", "VW",
)
_MAKES_NORM = frozenset(_MAKES)
_TWO_WORD_MAKES = frozenset(m for m in _MAKES if " " in m)


# ---------------------------------------------------------------------------
# DOM helpers (identity-based; lxml elements compare/hash by identity).
# ---------------------------------------------------------------------------
def _is_elem(node) -> bool:
    return isinstance(getattr(node, "tag", None), str)


def _classes(node) -> set[str]:
    return set((node.get("class") or "").split()) if _is_elem(node) else set()


def _signature(node) -> tuple[str, frozenset]:
    return (node.tag, frozenset(_classes(node)))


def _node_selector(node) -> str:
    """A compound selector for one element: ``tag`` or ``tag.classA.classB`` (classes sorted for
    determinism). Class-based when available — the self-healing, text/attribute-anchored shape
    scrapling favours over a brittle positional XPath."""
    cls = sorted(_classes(node))
    return node.tag + ("." + ".".join(cls) if cls else "")


def _dedup(nodes: list) -> list:
    seen: set[int] = set()
    out = []
    for n in nodes:
        if id(n) not in seen:
            seen.add(id(n))
            out.append(n)
    return out


def _same(a: list, b: list) -> bool:
    return [id(x) for x in a] == [id(y) for y in b]


# ---------------------------------------------------------------------------
# Minimal CSS applier — supports exactly the grammar this rung EMITS, so extraction
# eats its own dogfood: a derived selector that does not re-select its node yields nothing
# (an honest miss), never a guess.
#   compound: tag | .class | tag.class[.class...] | tag[attr]   (trailing ::attr(x) ignored)
#   combinator: descendant (whitespace)
# ---------------------------------------------------------------------------
def _parse_compound(token: str) -> tuple[str | None, frozenset, str | None]:
    token = token.split("::", 1)[0]
    base, sep, after = token.partition("[")
    attr = after.rstrip("]") or None if sep else None
    parts = base.split(".")
    tag = parts[0] or None
    classes = frozenset(p for p in parts[1:] if p)
    return tag, classes, attr


def _node_match(node, tag: str | None, classes: frozenset, attr: str | None) -> bool:
    if not _is_elem(node):
        return False
    if tag and node.tag != tag:
        return False
    if classes and not classes <= _classes(node):
        return False
    if attr and node.get(attr) is None:
        return False
    return True


def _select(root, selector: str) -> list:
    """Every node matching ``selector`` among the DESCENDANTS of ``root`` (CSS descendant
    semantics — the scope element itself is never returned)."""
    ctx = [root]
    for token in selector.split():
        tag, classes, attr = _parse_compound(token)
        nxt = []
        for scope in ctx:
            for n in scope.iterdescendants():
                if _node_match(n, tag, classes, attr):
                    nxt.append(n)
        ctx = _dedup(nxt)
    return ctx


# ---------------------------------------------------------------------------
# Per-vehicle anchor signal (reuses dealerprobe.classify_loc verbatim).
# ---------------------------------------------------------------------------
def _per_vehicle_url(href: str | None, base: str) -> str | None:
    """Absolute URL iff ``href`` points at a single vehicle (PDP), else None."""
    if not href:
        return None
    h = unescape(href).strip()
    if not h or h.lower().startswith(_SKIP_HREF):
        return None
    absu = urljoin(base, h)
    return absu if classify_loc(absu) == "per_vehicle" else None


def _anchor_nodes(root, base: str) -> list[tuple]:
    out = []
    for n in root.iter():
        if _is_elem(n) and n.tag == "a":
            u = _per_vehicle_url(n.get("href"), base)
            if u:
                out.append((n, u))
    return out


def _path_root_to(node) -> list:
    return list(reversed(list(node.iterancestors()))) + [node]


def _deepest_common_ancestor(nodes: list):
    paths = [_path_root_to(n) for n in nodes]
    dca = paths[0][0]
    for tier in zip(*paths):
        if all(x is tier[0] for x in tier):
            dca = tier[0]
        else:
            break
    return dca


def _card_for(anchor, dca):
    """The element on the anchor's root->anchor path that is the DIRECT child of the listing
    container ``dca`` — i.e. the repeated card wrapping that anchor."""
    path = _path_root_to(anchor)
    i = path.index(dca)
    return path[i + 1] if i + 1 < len(path) else anchor


# ---------------------------------------------------------------------------
# Field derivation inside one card.
# ---------------------------------------------------------------------------
def _anchor_in(card, base: str):
    for n in card.iterdescendants():
        if _is_elem(n) and n.tag == "a":
            u = _per_vehicle_url(n.get("href"), base)
            if u:
                return n, u
    return None, None


def _title_node(card, anchor):
    for n in card.iterdescendants():
        if _is_elem(n) and n.tag in _HEADING_TAGS and n.text_content().strip():
            return n
    return anchor


def _find_value_node(card, valfn):
    """The tightest descendant of ``card`` whose text triggers ``valfn`` (e.g. ``_ssr_price``).

    Prefers a node whose OWN text matches (the leaf bearing the value) and, among those, the one
    with the fewest descendants — so the derived selector is ``span.price``, not ``article.card``.
    Falls back to ``text_content`` matching for a value wrapped in an inner tag."""
    best = None
    best_size = 1 << 30
    for n in card.iterdescendants():
        if not _is_elem(n):
            continue
        t = (n.text or "").strip()
        if t and valfn(t) is not None:
            size = sum(1 for _ in n.iterdescendants())
            if size < best_size:
                best, best_size = n, size
    if best is not None:
        return best
    for n in card.iterdescendants():
        if not _is_elem(n):
            continue
        t = n.text_content().strip()
        if t and valfn(t) is not None:
            size = sum(1 for _ in n.iterdescendants())
            if size < best_size:
                best, best_size = n, size
    return best


def _derive_field_map(card, base: str) -> dict[str, str]:
    """Auto-derive a relative CSS selector for each vehicle field present in a card."""
    fmap: dict[str, str] = {}
    anchor, _u = _anchor_in(card, base)
    if anchor is not None:
        fmap["url"] = _node_selector(anchor) + "::attr(href)"
        title_sel = _node_selector(_title_node(card, anchor))
        fmap["title"] = title_sel
        # make/model carry the SAME element selector (the node bearing the brand+model text); the
        # split is a downstream lexicon decision, not a different DOM location.
        fmap["make"] = title_sel
        fmap["model"] = title_sel
    for field, valfn in (("price", _ssr_price), ("year", _ssr_year), ("km", _ssr_km)):
        n = _find_value_node(card, valfn)
        if n is not None:
            fmap[field] = _node_selector(n)
    return fmap


def _container_selector(root, dca, cards: list) -> tuple[str, list]:
    """A selector that re-selects exactly the card nodes, scoped by the listing container when
    that disambiguates (``section.results article.card``). Returns (selector, selected_nodes)."""
    card_sel = _node_selector(cards[0])
    candidates = []
    if _is_elem(dca) and dca is not root:
        candidates.append(_node_selector(dca) + " " + card_sel)
    candidates.append(card_sel)
    if "." in card_sel:
        candidates.append(cards[0].tag)  # tag-only last resort
    for cand in candidates:
        sel = _select(root, cand)
        if _same(sel, cards):
            return cand, sel
    # No candidate selects EXACTLY the cards (e.g. an irregular DOM). Keep the most specific one
    # and extract from whatever it yields; never fabricate by falling back to an empty match.
    first = _select(root, candidates[0])
    return candidates[0], (first if first else cards)


# ---------------------------------------------------------------------------
# Value extraction THROUGH the derived selectors (dogfood).
# ---------------------------------------------------------------------------
def _split_make_model(title: str | None) -> tuple[str | None, str | None]:
    if not title:
        return None, None
    toks = title.split()
    if not toks:
        return None, None
    if len(toks) >= 2 and f"{toks[0]} {toks[1]}".upper() in _TWO_WORD_MAKES:
        return f"{toks[0]} {toks[1]}", (" ".join(toks[2:]) or None)
    if toks[0].upper() in _MAKES_NORM:
        return toks[0], (" ".join(toks[1:]) or None)
    return None, None


def _extract_url(card, selector: str, base: str) -> str | None:
    for n in _select(card, selector):
        u = _per_vehicle_url(n.get("href"), base)
        if u:
            return u
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


def _extract_vehicle(card, fmap: dict[str, str], base: str) -> dict:
    url = _extract_url(card, fmap["url"], base) if fmap.get("url") else None
    title = _extract_text(card, fmap["title"]) if fmap.get("title") else None
    make, model = _split_make_model(title)
    return {
        "url": url,
        "title": title,
        "make": make,
        "model": model,
        "year": _extract_value(card, fmap["year"], _ssr_year) if fmap.get("year") else None,
        "km": _extract_value(card, fmap["km"], _ssr_km) if fmap.get("km") else None,
        "price": _extract_value(card, fmap["price"], _ssr_price) if fmap.get("price") else None,
    }


def _valid(v: dict) -> bool:
    # A sample-valid vehicle has a PDP url and at least one extracted signal (price/year/km/title).
    return bool(v.get("url")) and any(
        v.get(k) is not None and v.get(k) != "" for k in ("price", "year", "km", "title"))


def _parse(html: str):
    if not html or not html.strip():
        return None
    try:
        return lxml_html.fromstring(html)
    except Exception:  # noqa: BLE001 — malformed bytes -> honest no-derivation, not a crash
        return None


# ---------------------------------------------------------------------------
# Public derivation entry point (pure; ideal for direct unit testing).
# ---------------------------------------------------------------------------
def derive_css_recipe(html: str, base: str):
    """Induce the repeated card pattern + per-field CSS selectors from a listing's HTML.

    Returns ``(container_selector, field_map, vehicles, declared)`` when a repeated per-vehicle
    card pattern is found, else ``None`` (no pattern -> the honest empty outcome). ``vehicles`` are
    extracted THROUGH the derived selectors, so they prove the selectors actually work.
    """
    root = _parse(html)
    if root is None:
        return None
    anchors = _anchor_nodes(root, base)
    if len(anchors) < 2:  # a repeated card pattern needs >= 2 per-vehicle cards
        return None
    dca = _deepest_common_ancestor([a for a, _ in anchors])
    cards = _dedup([_card_for(a, dca) for a, _ in anchors])
    # Keep only the dominant repeated signature (drops a stray non-card direct child).
    sig_counts = Counter(_signature(c) for c in cards)
    top_sig, _n = sig_counts.most_common(1)[0]
    cards = [c for c in cards if _signature(c) == top_sig]
    if len(cards) < 2:
        return None
    fmap = _derive_field_map(cards[0], base)
    if not fmap.get("url"):  # no actionable per-vehicle link -> cannot action -> honest empty
        return None
    container, selected = _container_selector(root, dca, cards)
    nodes = selected if (selected and len(selected) >= len(cards)) else cards
    vehicles = [_extract_vehicle(c, fmap, base) for c in nodes]
    m = _COUNT_HINT.search(html)
    declared = int(m.group(1)) if m else None
    return container, fmap, vehicles, declared


# ---------------------------------------------------------------------------
# The harness Extractor (engine='css').
# ---------------------------------------------------------------------------
def _engine_fetch(url: str, **_kw) -> str:
    """Default runtime transport: the shared antidetection engine (lazy-imported so this module
    imports with no network stack and the unit tests inject a fixture ``fetch_fn`` instead)."""
    from pipeline.engine.fetch import fetch_text
    return fetch_text(url, tier=0)


class CssAdaptiveExtractor:
    """Harness Extractor for an SSR dealer listing with no JSON-LD (``dealer_ref`` == listing URL).

    Implements the :class:`pipeline.recipe_harness.Extractor` protocol (``source`` +
    ``recipe_template`` + ``sample``). ``sample`` auto-derives the selectors and stashes them per
    dealer; ``recipe_template`` emits them as ``Parsing(engine='css', ...)`` so the cracker records
    the winning rung's selectors into the durable recipe.
    """

    source = "web_css"

    def __init__(self, fetch_fn=None) -> None:
        self._fetch = fetch_fn or _engine_fetch
        self._derived: dict[str, dict] = {}  # dealer_ref -> {container, field_map, declared}

    def recipe_template(self, dealer_ref: str) -> Recipe:
        d = self._derived.get(dealer_ref, {})
        return Recipe(
            source=self.source, dealer_ref=dealer_ref, kind="compraventa",
            transport=Transport(engine="curl_cffi", base_url=dealer_ref, impersonate="chrome",
                                 timeout_s=30),
            fingerprint=Fingerprint(user_agent="engine-managed"),
            pagination=Pagination(strategy="single_page", url_template=dealer_ref,
                                  declared_path="page text: N vehículos", stop="empty_page"),
            parsing=Parsing(engine="css", container_path=d.get("container"),
                            field_map=dict(d.get("field_map") or {})),
        )

    def sample(self, dealer_ref: str, k: int) -> Sample:
        html = self._fetch(dealer_ref)
        res = derive_css_recipe(html or "", dealer_ref)
        if res is None:
            # Honest empty: no repeated card pattern -> no selectors, no invented cars. The harness
            # marks the recipe FAILED ("empty sample") via decide_status.
            self._derived[dealer_ref] = {"container": None, "field_map": {}, "declared": None}
            return Sample(declared=None, fetched=0, parsed=[], full_dealer=False)
        container, field_map, vehicles, declared = res
        self._derived[dealer_ref] = {"container": container, "field_map": field_map,
                                     "declared": declared}
        sliced = vehicles[:k]
        parsed = [v for v in sliced if _valid(v)]
        full = declared is not None and declared <= len(sliced)
        return Sample(declared=declared, fetched=len(sliced), parsed=parsed, full_dealer=full)
