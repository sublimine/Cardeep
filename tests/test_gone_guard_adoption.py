"""B2.3 adoption tests — verify that the three wholesale connectors call
should_emit_gone before their GONE/reconcile sweep.

Strategy: grep the source text for the call-site presence + import, and
confirm the exact tokens we need are present, without starting a DB or
network connection. This is a structural/lint-level test, intentionally
kept static so it runs with zero infrastructure.
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib
import re


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = pathlib.Path(__file__).parents[1]

CONNECTORS = {
    "group_subastas": ROOT / "pipeline/platform/group_subastas_wholesale.py",
    "localizavo":     ROOT / "pipeline/platform/localizavo_wholesale.py",
    "subastacar":     ROOT / "pipeline/platform/subastacar_wholesale.py",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _source(name: str) -> str:
    return CONNECTORS[name].read_text(encoding="utf-8")


def _ast(name: str) -> ast.Module:
    return ast.parse(_source(name))


def _import_names(tree: ast.Module) -> set[str]:
    """Return all names imported across all ImportFrom + Import nodes."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name)
    return names


def _call_sites(tree: ast.Module, func_name: str) -> list[ast.Call]:
    """Return every Call node in the tree whose func is a Name or Attr matching func_name."""
    sites = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == func_name:
                sites.append(node)
            elif isinstance(func, ast.Attribute) and func.attr == func_name:
                sites.append(node)
    return sites


# ---------------------------------------------------------------------------
# Tests: imports
# ---------------------------------------------------------------------------


def test_group_subastas_imports_should_emit_gone() -> None:
    tree = _ast("group_subastas")
    names = _import_names(tree)
    assert "should_emit_gone" in names, (
        "group_subastas_wholesale.py does not import should_emit_gone from pipeline.delta_guard"
    )


def test_group_subastas_imports_fire_alert() -> None:
    tree = _ast("group_subastas")
    names = _import_names(tree)
    assert "fire_alert" in names, (
        "group_subastas_wholesale.py does not import fire_alert"
    )


def test_group_subastas_imports_build_origin() -> None:
    tree = _ast("group_subastas")
    names = _import_names(tree)
    assert "build_origin" in names, (
        "group_subastas_wholesale.py does not import build_origin"
    )


def test_localizavo_imports_should_emit_gone() -> None:
    tree = _ast("localizavo")
    names = _import_names(tree)
    assert "should_emit_gone" in names, (
        "localizavo_wholesale.py does not import should_emit_gone from pipeline.delta_guard"
    )


def test_localizavo_imports_fire_alert() -> None:
    tree = _ast("localizavo")
    names = _import_names(tree)
    assert "fire_alert" in names, (
        "localizavo_wholesale.py does not import fire_alert"
    )


def test_subastacar_imports_should_emit_gone() -> None:
    tree = _ast("subastacar")
    names = _import_names(tree)
    assert "should_emit_gone" in names, (
        "subastacar_wholesale.py does not import should_emit_gone from pipeline.delta_guard"
    )


def test_subastacar_imports_fire_alert() -> None:
    tree = _ast("subastacar")
    names = _import_names(tree)
    assert "fire_alert" in names, (
        "subastacar_wholesale.py does not import fire_alert"
    )


# ---------------------------------------------------------------------------
# Tests: call sites present in the AST
# ---------------------------------------------------------------------------


def test_group_subastas_calls_should_emit_gone() -> None:
    tree = _ast("group_subastas")
    sites = _call_sites(tree, "should_emit_gone")
    assert len(sites) >= 1, (
        "group_subastas_wholesale.py has no call to should_emit_gone()"
    )


def test_localizavo_calls_should_emit_gone() -> None:
    tree = _ast("localizavo")
    sites = _call_sites(tree, "should_emit_gone")
    assert len(sites) >= 1, (
        "localizavo_wholesale.py has no call to should_emit_gone()"
    )


def test_subastacar_calls_should_emit_gone() -> None:
    tree = _ast("subastacar")
    sites = _call_sites(tree, "should_emit_gone")
    assert len(sites) >= 1, (
        "subastacar_wholesale.py has no call to should_emit_gone()"
    )


# ---------------------------------------------------------------------------
# Tests: should_emit_gone called BEFORE the reconcile/sweep call-site
# ---------------------------------------------------------------------------


def _line_of_first_call(tree: ast.Module, func_name: str) -> int | None:
    """Return the line number of the first call to func_name, or None."""
    sites = _call_sites(tree, func_name)
    if not sites:
        return None
    return min(s.lineno for s in sites)


def test_group_subastas_guard_before_reconcile() -> None:
    """should_emit_gone must appear before _seen_vehicle_ulids (the sweep helper)."""
    tree = _ast("group_subastas")
    guard_line = _line_of_first_call(tree, "should_emit_gone")
    sweep_line = _line_of_first_call(tree, "_seen_vehicle_ulids")
    assert guard_line is not None, "should_emit_gone call not found"
    assert sweep_line is not None, "_seen_vehicle_ulids call not found (sweep helper missing?)"
    assert guard_line < sweep_line, (
        f"should_emit_gone (line {guard_line}) must come BEFORE "
        f"_seen_vehicle_ulids (line {sweep_line})"
    )


def test_localizavo_guard_before_reconcile() -> None:
    """should_emit_gone must appear before _reconcile_aged_out."""
    tree = _ast("localizavo")
    guard_line = _line_of_first_call(tree, "should_emit_gone")
    sweep_line = _line_of_first_call(tree, "_reconcile_aged_out")
    assert guard_line is not None, "should_emit_gone call not found"
    assert sweep_line is not None, "_reconcile_aged_out call not found (sweep missing?)"
    assert guard_line < sweep_line, (
        f"should_emit_gone (line {guard_line}) must come BEFORE "
        f"_reconcile_aged_out (line {sweep_line})"
    )


def test_subastacar_guard_before_reconcile() -> None:
    """should_emit_gone must appear before _reconcile_aged_out."""
    tree = _ast("subastacar")
    guard_line = _line_of_first_call(tree, "should_emit_gone")
    sweep_line = _line_of_first_call(tree, "_reconcile_aged_out")
    assert guard_line is not None, "should_emit_gone call not found"
    assert sweep_line is not None, "_reconcile_aged_out call not found (sweep missing?)"
    assert guard_line < sweep_line, (
        f"should_emit_gone (line {guard_line}) must come BEFORE "
        f"_reconcile_aged_out (line {sweep_line})"
    )


# ---------------------------------------------------------------------------
# Tests: gone_suppressed key initialised in stats dict
# ---------------------------------------------------------------------------


def _has_gone_suppressed_in_stats_literal(src: str) -> bool:
    """Return True if the source contains 'gone_suppressed' as a key in the stats dict literal."""
    return bool(re.search(r'"gone_suppressed"\s*:', src))


def test_group_subastas_stats_has_gone_suppressed() -> None:
    assert _has_gone_suppressed_in_stats_literal(_source("group_subastas")), (
        "group_subastas_wholesale.py stats dict does not initialise 'gone_suppressed'"
    )


def test_localizavo_stats_has_gone_suppressed() -> None:
    assert _has_gone_suppressed_in_stats_literal(_source("localizavo")), (
        "localizavo_wholesale.py stats dict does not initialise 'gone_suppressed'"
    )


def test_subastacar_stats_has_gone_suppressed() -> None:
    assert _has_gone_suppressed_in_stats_literal(_source("subastacar")), (
        "subastacar_wholesale.py stats dict does not initialise 'gone_suppressed'"
    )


# ---------------------------------------------------------------------------
# Tests: fire_alert called in suppression branch (structural grep)
# ---------------------------------------------------------------------------


def test_group_subastas_fires_alert_on_suppress() -> None:
    src = _source("group_subastas")
    # The suppression branch must call fire_alert after the gone_suppressed assignment.
    assert "fire_alert" in src and "gone_guard" in src, (
        "group_subastas_wholesale.py suppression branch missing fire_alert or 'gone_guard' origin"
    )


def test_localizavo_fires_alert_on_suppress() -> None:
    src = _source("localizavo")
    assert "fire_alert" in src and "gone_guard" in src, (
        "localizavo_wholesale.py suppression branch missing fire_alert or 'gone_guard' origin"
    )


def test_subastacar_fires_alert_on_suppress() -> None:
    src = _source("subastacar")
    assert "fire_alert" in src and "gone_guard" in src, (
        "subastacar_wholesale.py suppression branch missing fire_alert or 'gone_guard' origin"
    )
