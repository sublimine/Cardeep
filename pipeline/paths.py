"""Country-scoped filesystem roots — the single place that knows where a country's
recipes, raw harvest dumps and census CSVs live.

Today every path literal is hard-coded as ``countries/ES/...`` / ``data/ES/...`` in
4+ call-sites (recipe.py, harvest_dealer.py, triangulation.py). This module
centralizes those roots behind helpers that DEFAULT to ``ES`` so the resolved paths
are byte-identical to the pre-refactor literals; passing a different ``country_code``
is the only thing that changes the directory. Nothing here touches cdp_code minting
or the dedup key — it is purely path derivation.

Every helper accepts an optional ``root`` override so callers that already expose a
monkeypatch-able ROOT (e.g. ``recipe.ROOT`` in test_recipe.py) keep that seam intact:
the helper resolves against the caller's ROOT rather than hard-binding _REPO_ROOT.
"""
from __future__ import annotations

import re
from pathlib import Path

# The default (and, today, only) tenant. Every helper defaults to this so ES paths
# are unchanged; a second country is onboarded by passing a different code.
DEFAULT_COUNTRY = "ES"

# Repo root. pipeline/paths.py lives one level under the repo root (pipeline/), so
# parent.parent is the repo root — identical to recipe.ROOT / harvest_dealer.ROOT
# (Path(__file__).resolve().parent.parent) and to triangulation's parents[2].
_REPO_ROOT = Path(__file__).resolve().parent.parent

# 'CDP-XX-' country segment parser. The cdp_code shape is CDP-<CC>-<NN>-<8 base32>.
_CDP_COUNTRY_RE = re.compile(r"^CDP-([A-Z]{2})-")


def recipe_root(country_code: str = DEFAULT_COUNTRY, *, root: Path | None = None) -> Path:
    """``<repo>/countries/<country_code>`` — the per-country recipe/census tree root."""
    base = root if root is not None else _REPO_ROOT
    return base / "countries" / country_code


def recipes_flat_dir(country_code: str = DEFAULT_COUNTRY, *, root: Path | None = None) -> Path:
    """``<repo>/countries/<country_code>/recipes`` — flat per-dealer recipe YAMLs."""
    return recipe_root(country_code, root=root) / "recipes"


def data_root(country_code: str = DEFAULT_COUNTRY, *, root: Path | None = None) -> Path:
    """``<repo>/data/<country_code>`` — ephemeral, gitignored raw harvest dumps."""
    base = root if root is not None else _REPO_ROOT
    return base / "data" / country_code


def census_dir(country_code: str = DEFAULT_COUNTRY, *, root: Path | None = None) -> Path:
    """``<repo>/countries/<country_code>/census`` — external triangulation CSVs."""
    return recipe_root(country_code, root=root) / "census"


def country_of_cdp(cdp_code: str) -> str:
    """Derive the 2-letter country code from a cdp_code's ``CDP-XX-`` segment.

    Lets callers route a code to its country tree with no DB lookup. Defaults to
    ``DEFAULT_COUNTRY`` for anything that does not match (legacy/garbage input), so
    every existing CDP-ES- code resolves to 'ES' and the path is unchanged.
    """
    m = _CDP_COUNTRY_RE.match(cdp_code or "")
    return m.group(1) if m else DEFAULT_COUNTRY
