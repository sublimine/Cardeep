"""Offline tests for the continuous DISCOVERY scheduler registry (no DB).

Assert all five V2–V6 vectors are wired with sane cadences and that the
orthogonality flags agree with the exhaustiveness list taxonomy.
"""
from __future__ import annotations

import pytest

from pipeline.discover_schedule import DISCOVERY_REGISTRY
from pipeline.exhaustiveness import lists


@pytest.mark.unit
def test_all_five_vectors_registered():
    assert set(DISCOVERY_REGISTRY) == {
        "overture", "dork_municipal", "borme_cnae", "graph_recursive", "collapse_invisible"}


@pytest.mark.unit
def test_cadences_are_sane():
    for job in DISCOVERY_REGISTRY.values():
        assert job.cadence_hours > 0
        assert job.vector == job.source_key
    # BORME daily (delta of altas) must be the most frequent; dork quarterly the least.
    assert DISCOVERY_REGISTRY["borme_cnae"].cadence_hours == 24
    assert DISCOVERY_REGISTRY["dork_municipal"].cadence_hours >= 720


@pytest.mark.unit
def test_orthogonality_matches_taxonomy():
    # A job flagged orthogonal must map to an MSE list in lists.py, and vice-versa.
    for job in DISCOVERY_REGISTRY.values():
        bucket = lists.bucket_for(job.source_key)
        is_mse = bucket in lists.ORTHOGONAL_LISTS
        assert job.orthogonal == is_mse, f"{job.source_key}: flag {job.orthogonal} vs taxonomy {is_mse}"
