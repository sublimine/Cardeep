"""T1.2 (second belt) — the cross_source_dedup overlay must NEVER serve a cross-country cluster.

The block-keys already carry country (first belt: every signal index is keyed (value, muni, country)),
but a post-clustering ASSERTION is the SECOND belt — mirroring
resolve_entities._assert_no_cross_country_clusters — so even a future edge-builder that forgot
country in a key fails CLOSED here instead of silently serving a cross-border merge. The DB
constraint (T1.2 execution, DB-gated) will be the third, mechanical belt.

PURE test over in-memory dicts (no DB).
"""
from __future__ import annotations

import pytest

from pipeline.identity.cross_source_dedup import (
    CrossCountryClusterError,
    _build_cluster_table,
)

pytestmark = pytest.mark.unit


def _ent(ulid, country):
    return {"entity_ulid": ulid, "country_code": country, "municipality_code": "28079",
            "trade_name": ulid, "cdp_code": ulid, "source_group": None, "created_at": None,
            "website": None, "phone": None, "address": None, "cif": None, "lat": None}


def test_cross_country_cluster_fails_closed():
    # A DEFECTIVE edge-builder produces an edge across countries (ES<->PT). The second belt MUST
    # reject the resulting cluster — never serve a cross-border merge.
    ents = [_ent("A", "ES"), _ent("B", "PT")]
    bad_pairs = [("A", "B", 0.99, "phone:bug-forgot-country")]
    with pytest.raises(CrossCountryClusterError):
        _build_cluster_table(ents, bad_pairs)


def test_single_country_merge_is_allowed():
    ents = [_ent("A", "ES"), _ent("B", "ES")]
    rows = _build_cluster_table(ents, [("A", "B", 0.99, "phone:ok")])
    assert len(rows) == 2
    assert len({r["canonical_ulid"] for r in rows}) == 1  # merged into one cluster


def test_singletons_of_distinct_countries_are_fine():
    # No edges -> each entity its own cluster -> no cross-country cluster -> no raise.
    ents = [_ent("A", "ES"), _ent("B", "PT")]
    rows = _build_cluster_table(ents, [])
    assert len({r["canonical_ulid"] for r in rows}) == 2
