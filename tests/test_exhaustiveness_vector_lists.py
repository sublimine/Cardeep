"""Integration-taxonomy tests: the V2–V6 discovery vectors are registered into the
exhaustiveness list taxonomy with the correct orthogonality.

Only the list taxonomy (pipeline/exhaustiveness/lists.py) is asserted here — the
estimators are untouched. V2 (overture) folds into GEO; V3/V4 are new orthogonal
lists (DORK/REG); V5/V6 are deliberately NON-orthogonal (graph-dependence /
resolution) so they never inflate the MSE.
"""
from __future__ import annotations

import pytest

from pipeline.exhaustiveness import lists


@pytest.mark.unit
@pytest.mark.parametrize("source_key,bucket", [
    ("overture", "GEO"),            # V2 geo-grid is a physical-presence catalogue
    ("dork_municipal", "DORK"),     # V3 own-domain search
    ("borme_cnae", "REG"),          # V4 mercantile registry
    ("graph_recursive", "GRAPH"),   # V5 corporate graph
    ("collapse_invisible", "COLLAPSE"),  # V6 resolution
])
def test_bucket_for_vectors(source_key, bucket):
    assert lists.bucket_for(source_key) == bucket


@pytest.mark.unit
def test_v3_v4_are_orthogonal():
    assert "DORK" in lists.ORTHOGONAL_LISTS
    assert "REG" in lists.ORTHOGONAL_LISTS
    assert set(lists.orthogonal_buckets()) >= {"GEO", "CENSUS", "DGT", "ASSOC", "OEM", "DORK", "REG"}


@pytest.mark.unit
def test_v5_v6_are_not_orthogonal():
    # Graph is seeded from already-known sites (dependent); collapse is resolution.
    assert "GRAPH" not in lists.ORTHOGONAL_LISTS
    assert "COLLAPSE" not in lists.ORTHOGONAL_LISTS


@pytest.mark.unit
def test_metadata_present_for_new_lists():
    for lk in ("DORK", "REG", "GRAPH", "COLLAPSE"):
        assert lk in lists.LIST_METADATA
        cls, desc = lists.LIST_METADATA[lk]
        assert cls and desc
