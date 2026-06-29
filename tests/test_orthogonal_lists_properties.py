"""T1.3-ext — property invariants of the MSE orthogonal-list taxonomy (lists.py).

Capture-recapture is only valid over ORTHOGONAL lists. Including the dominant digital-marketplace
signal (MKT), the graph-dependent vector (GRAPH) or the resolution vector (COLLAPSE) would inflate the
apparent overlap and FAKE coverage (an anti-maquillaje vector the científico flagged). These property
tests pin that taxonomy: every source maps to a known bucket, and the non-orthogonal buckets are never
in the default MSE list set.
"""
from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from pipeline.exhaustiveness.lists import (
    LIST_METADATA,
    bucket_for,
    orthogonal_buckets,
)

pytestmark = pytest.mark.unit


@given(st.text())
def test_bucket_for_always_returns_a_known_bucket(source_key):
    assert bucket_for(source_key) in LIST_METADATA


@given(st.text())
def test_bucket_for_is_deterministic(source_key):
    assert bucket_for(source_key) == bucket_for(source_key)


def test_default_mse_lists_exclude_non_orthogonal_buckets():
    lists = orthogonal_buckets(include_mkt=False)
    for excluded in ("MKT", "GRAPH", "COLLAPSE"):
        assert excluded not in lists, f"{excluded} must NOT be a default MSE list (would fake overlap)"


def test_generic_marketplace_is_mkt_and_excluded_by_default():
    assert bucket_for("wallapop_wholesale") == "MKT"
    assert bucket_for("milanuncios_wholesale") == "MKT"
    assert "MKT" not in orthogonal_buckets()       # dominant-list bias kept OUT


def test_include_mkt_is_opt_in_only():
    assert "MKT" in orthogonal_buckets(include_mkt=True)


def test_known_orthogonal_sources_map_correctly():
    assert bucket_for("overture") == "GEO"
    assert bucket_for("dgt_cat") == "DGT"
    assert bucket_for("borme_cnae") == "REG"        # V4 mercantile registry — orthogonal
    assert bucket_for("dork_municipal") == "DORK"   # V3 own-domain search — orthogonal
    assert bucket_for("oem_kia_wholesale") == "OEM"
    assert bucket_for("graph_recursive") == "GRAPH"      # dependent — excluded
    assert bucket_for("collapse_invisible") == "COLLAPSE"  # resolution — excluded
