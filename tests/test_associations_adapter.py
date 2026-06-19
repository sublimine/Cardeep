"""Offline unit tests for the association census SourceAdapters (AEDRA/ACEVAS/AECS).

No DB, no network: these assert the local committed JSON parses into well-formed
DiscoveredEntity rows and that declared_count == len(fetch()), which is the
invariant the VAM count-quorum gate in pipeline.discover relies on.
"""
from __future__ import annotations

import pytest

from pipeline.sources.associations import AcevasAdapter, AecsAdapter, AedraAdapter

# Expected member counts (verified against the committed JSON, 2026-06).
_EXPECTED = {
    AedraAdapter: ("aedra", "desguace", 615),
    AcevasAdapter: ("acevas", "concesionario_oficial", 99),
    AecsAdapter: ("aecs", "concesionario_oficial", 74),
}


@pytest.mark.unit
@pytest.mark.parametrize("adapter_cls", list(_EXPECTED))
def test_declared_count_matches_fetch(adapter_cls):
    src_key, _kind, expected = _EXPECTED[adapter_cls]
    a = adapter_cls()
    rows = a.fetch()
    assert a.source_key == src_key
    assert a.declared_count() == len(rows) == expected


@pytest.mark.unit
@pytest.mark.parametrize("adapter_cls", list(_EXPECTED))
def test_rows_are_wellformed(adapter_cls):
    _src, kind, _n = _EXPECTED[adapter_cls]
    for e in adapter_cls().fetch():
        assert e.kind == kind
        assert e.legal_name, "every association member must carry a name"
        assert e.source_key == _EXPECTED[adapter_cls][0]
        # provenance metadata the canonical pipeline propagates
        assert e.extra.get("source_group") == "association"
        assert e.extra.get("kind_source") == "legal_census"


@pytest.mark.unit
def test_acevas_latlon_parsed_as_float():
    # ACEVAS ships lat/lon as strings; the adapter must coerce to float|None.
    rows = AcevasAdapter().fetch()
    with_coords = [e for e in rows if e.lat is not None]
    assert with_coords, "ACEVAS sample is expected to carry some geocoded members"
    for e in with_coords:
        assert isinstance(e.lat, float) and isinstance(e.lon, float)
