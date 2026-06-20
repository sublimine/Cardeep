"""Offline unit tests for the V6 collapse-invisible SourceAdapter.

No network/DB: assert E.164 normalization, CIF checksum, and the term-frequency
collapse logic (singletons dropped, rare shared keys kept, generic switchboard
discarded, valid CIF always collapses) by injecting a fake entity set.
"""
from __future__ import annotations

import pytest

from pipeline.sources import collapse_invisible as ci
from pipeline.sources.collapse_invisible import CollapseInvisibleAdapter


@pytest.mark.unit
@pytest.mark.parametrize("raw,expected", [
    ("+34 600 123 456", "+34600123456"),
    ("0034911112233", "+34911112233"),
    ("600123456", "+34600123456"),
    ("12345", None),               # too short
    ("+34 500 000 000", None),     # invalid Spanish leading digit
    (None, None),
])
def test_phone_e164(raw, expected):
    assert ci.normalize_phone_es(raw) == expected


@pytest.mark.unit
@pytest.mark.parametrize("cif,ok", [("A58818501", True), ("B00000001", False), ("notacif", False)])
def test_cif_checksum(cif, ok):
    assert ci.cif_control_ok(cif) is ok


def _ent(ulid, name, phone=None, cif=None, prov="28"):
    return {"entity_ulid": ulid, "legal_name": name, "trade_name": name, "cif": cif,
            "phone": phone, "email": None, "website": None, "province_code": prov,
            "municipality_code": "28079", "lat": None, "lon": None}


@pytest.mark.unit
def test_tf_collapse_logic(monkeypatch):
    rare = "+34600111222"     # shared by 2 -> same owner, kept
    generic = "+34910000000"  # shared by 8 -> switchboard, discarded
    valid_cif = "A58818501"
    ents = (
        [_ent(f"r{i}", f"Rare {i}", phone=rare) for i in range(2)]
        + [_ent(f"g{i}", f"Generic {i}", phone=generic) for i in range(8)]
        + [_ent("s1", "Solo", phone="+34655999888")]            # singleton -> nothing to collapse
        + [_ent(f"c{i}", f"CIF firm {i}", cif=valid_cif) for i in range(3)]
    )
    monkeypatch.setattr(ci, "_run_async", lambda coro: ents)
    monkeypatch.setattr(ci, "_dbscan_confirms", lambda coords, eps_km=0.6: False)
    monkeypatch.setenv("CARDEEP_COLLAPSE_PHONE_MAX", "6")

    a = CollapseInvisibleAdapter()
    rows = a.fetch()
    refs = {e.source_ref for e in rows}
    # rare phone cluster + valid-CIF cluster collapse; generic + singleton do not
    assert f"phone:{rare}" in refs
    assert f"cif:{valid_cif}" in refs
    assert f"phone:{generic}" not in refs
    assert a._stats["phone_clusters"] == 1
    assert a._stats["cif_clusters"] == 1
    cif_row = next(e for e in rows if e.source_ref == f"cif:{valid_cif}")
    assert cif_row.cif == valid_cif
    assert cif_row.extra["vector"] == 6
    assert cif_row.extra["cluster_size"] == 3
