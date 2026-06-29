"""T2.1 (execution, simulated in-memory — NO PG) — end-to-end re-cluster over synthetic fixtures.

The alternative path to verifying a DB-gated re-cluster WITHOUT the stack: simulate it in memory over
fixtures through the EXACT pure core the DB re-cluster drives (_build_deterministic_edges ->
_build_cluster_table). Proves the CIF edge produces the correct clustering end-to-end — branches of one
legal company merge across municipalities, distinct companies stay separate, the pre-existing name+muni
edges still work, and the country belt holds. The DB re-cluster (dry-run :5434 -> golden -> Ferrari)
remains the final gate; this verifies the logic it will execute.
"""
from __future__ import annotations

import pytest

from pipeline.identity.cluster_dealers import (
    _build_cluster_table,
    _build_deterministic_edges,
)

pytestmark = pytest.mark.unit


def _ent(ulid, *, name, muni, cif=None, phone=None, website=None, country="ES"):
    return {"entity_ulid": ulid, "trade_name": name, "municipality_code": muni,
            "country_code": country, "cif": cif, "phone": phone, "website": website,
            "cdp_code": ulid, "source_group": None, "first_seen": None, "address": None, "lat": None}


def _canonical_of(rows, ulid):
    return next(r["canonical_ulid"] for r in rows if r["entity_ulid"] == ulid)


def test_recluster_merges_branches_by_cif_across_municipalities():
    ents = [
        _ent("N1", name="Auto Norte SL", muni="28079", cif="B11111111"),
        _ent("N2", name="Comercial Norte", muni="08019", cif="B11111111"),  # same CIF, diff muni+name
        _ent("S1", name="Talleres Sur", muni="28079", cif="B22222222"),     # distinct CIF
    ]
    rows = _build_cluster_table(ents, _build_deterministic_edges(ents))
    # N1 + N2 (same legal company by CIF) -> ONE cluster, even across municipalities.
    assert _canonical_of(rows, "N1") == _canonical_of(rows, "N2")
    # S1 (distinct CIF) stays its own cluster.
    assert _canonical_of(rows, "S1") != _canonical_of(rows, "N1")
    assert len({r["canonical_ulid"] for r in rows}) == 2  # {Norte, Sur}


def test_recluster_still_merges_by_name_muni_alongside_cif():
    # the pre-existing name+muni edge keeps working next to the new CIF edge (no regression).
    ents = [
        _ent("A", name="Garaje Centro", muni="28079"),
        _ent("B", name="Garaje Centro", muni="28079"),  # same name+muni -> merge (edge 1)
        _ent("C", name="Garaje Centro", muni="08019"),  # different muni -> separate
    ]
    rows = _build_cluster_table(ents, _build_deterministic_edges(ents))
    assert _canonical_of(rows, "A") == _canonical_of(rows, "B")
    assert _canonical_of(rows, "C") != _canonical_of(rows, "A")


def test_recluster_country_belt_holds_end_to_end():
    # same CIF string under two countries must NOT merge (1st belt: country is in the CIF key); the
    # 2nd belt would catch any leak. End-to-end: they stay separate, no raise.
    ents = [
        _ent("E", name="X", muni="28079", cif="B33333333", country="ES"),
        _ent("P", name="Y", muni="28079", cif="B33333333", country="PT"),
    ]
    rows = _build_cluster_table(ents, _build_deterministic_edges(ents))
    assert _canonical_of(rows, "E") != _canonical_of(rows, "P")
