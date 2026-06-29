"""T2.1 — CIF/NIF as a dedup edge in dealer-identity clustering.

The fiscal id (CIF) is the strongest identity signal and it is LOADED but UNUSED as an edge today
(cluster_dealers._build_deterministic_edges keys on name/phone/website + muni + country, never cif).
A CIF identifies a legal company nation-wide, so two entities sharing a VALID cif+country are the
same company even across municipalities — an exact-match edge that, unlike the reverted geo-match,
can NEVER over-merge (identical CIF = same legal entity). Placeholder/garbage CIFs are rejected so
they cannot fuse distinct dealers.

PURE test of the edge logic over in-memory dicts. The RE-CLUSTER that applies this to the SERVED
clustering is DB-gated (dry-run :5434 -> golden cdp -> Ferrari, per the re-cluster lesson); this
proves only that the edge logic is correct and over-merge-safe.
"""
from __future__ import annotations

import pytest

from pipeline.identity.cluster_dealers import _build_deterministic_edges

pytestmark = pytest.mark.unit


def _ent(ulid, *, name=None, muni=None, country="ES", cif=None, phone=None, website=None):
    return {"entity_ulid": ulid, "trade_name": name, "municipality_code": muni,
            "country_code": country, "cif": cif, "phone": phone, "website": website}


def _has_edge(edges, a, b):
    return (a, b) in edges or (b, a) in edges


def test_same_cif_merges_across_municipalities():
    # Same legal company (one CIF), two branches in different municipalities, no shared
    # name/phone/website -> today NO edge; with the CIF edge they MUST merge.
    ents = [_ent("A", name="Auto Uno SL", muni="28079", cif="B12345678"),
            _ent("B", name="Razon Social Distinta", muni="08019", cif="B12345678")]
    assert _has_edge(_build_deterministic_edges(ents), "A", "B")


def test_distinct_cif_does_not_merge():
    ents = [_ent("A", name="X", muni="28079", cif="B12345678"),
            _ent("B", name="Y", muni="28079", cif="B87654321")]
    assert not _has_edge(_build_deterministic_edges(ents), "A", "B")


def test_same_cif_different_country_does_not_merge():
    # country-proof: identical CIF string but different country must never co-cluster.
    ents = [_ent("A", name="X", muni="28079", country="ES", cif="B12345678"),
            _ent("B", name="Y", muni="28079", country="PT", cif="B12345678")]
    assert not _has_edge(_build_deterministic_edges(ents), "A", "B")


def test_placeholder_cif_does_not_merge():
    # garbage / placeholder CIFs must NOT fuse distinct dealers.
    for junk in ("", "   ", "000000000", "N/A", "-", "XXXXXXXXX"):
        ents = [_ent("A", name="X", muni="28079", cif=junk),
                _ent("B", name="Y", muni="08019", cif=junk)]
        assert not _has_edge(_build_deterministic_edges(ents), "A", "B"), junk
