"""The external triangulation anchor must actually be present and well-formed.

This is the wired-seam contract for the MSE seal: once
``countries/ES/census/dirce_cnae451.csv`` exists, ``load_external_census`` must
return a real census (>= 52 anchors, one per province at minimum) keyed on the
exact ``(province_code, segment)`` vocabulary the seal joins against, with
honest national roll-up rows. Provenance lives in
``countries/ES/census/SOURCE.md``.

If this file is regenerated, keep the invariants below true.
"""

from __future__ import annotations

import pathlib

import pytest

from pipeline.exhaustiveness import triangulation as T

# Segment vocabulary the seal strata use (pipeline/exhaustiveness/capture.py::_SEGMENT).
SEAL_SEGMENTS = {"compraventa", "concesionario", "desguace", "otros"}
ANCHOR_CSV = (
    pathlib.Path(__file__).resolve().parents[1]
    / "countries" / "ES" / "census" / "dirce_cnae451.csv"
)


@pytest.mark.unit
def test_anchor_csv_present():
    assert ANCHOR_CSV.exists(), (
        "triangulation anchor missing — expected countries/ES/census/dirce_cnae451.csv"
    )
    # SOURCE.md must travel with the CSV so estimates are never undeclared.
    assert (ANCHOR_CSV.parent / "SOURCE.md").exists(), (
        "SOURCE.md provenance file missing next to the anchor CSV"
    )


@pytest.mark.unit
def test_load_external_census_returns_at_least_52_anchors():
    census = T.load_external_census()
    assert len(census) >= 52, (
        f"expected >= 52 triangulation anchors, got {len(census)}"
    )


@pytest.mark.unit
def test_all_52_provinces_present():
    census = T.load_external_census()
    provinces = {prov for (prov, _seg) in census if prov is not None}
    expected = {f"{n:02d}" for n in range(1, 53)}  # 01..52
    assert provinces == expected, (
        f"province coverage incomplete: missing {sorted(expected - provinces)}"
    )


@pytest.mark.unit
def test_segments_are_within_seal_vocabulary():
    census = T.load_external_census()
    segments = {seg for (_prov, seg) in census if seg is not None}
    assert segments, "no per-segment anchors found"
    assert segments <= SEAL_SEGMENTS, (
        f"anchor segment(s) outside seal vocabulary: {segments - SEAL_SEGMENTS}"
    )
    # 'otros' has no honest external census -> it must NOT be fabricated.
    assert "otros" not in segments, (
        "'otros' anchor present but no honest external census exists for it"
    )


@pytest.mark.unit
def test_national_rollups_present_and_consistent():
    census = T.load_external_census()
    # National per-segment and all-segment anchors (blank province / segment).
    assert (None, "concesionario") in census
    assert census[(None, "concesionario")] == pytest.approx(5358.0)  # exact FACONAUTO
    assert (None, "desguace") in census
    assert census[(None, "desguace")] == pytest.approx(1292.0)  # exact DGT CAT
    assert (None, None) in census
    # All-segment ceiling = CNAE 451 (23085) + DGT CAT (1292).
    assert census[(None, None)] == pytest.approx(24377.0)


@pytest.mark.unit
def test_national_segment_sums_match_province_rows():
    census = T.load_external_census()
    for seg in ("compraventa", "concesionario", "desguace"):
        prov_sum = sum(
            v for (prov, s), v in census.items() if prov is not None and s == seg
        )
        national = census[(None, seg)]
        # concesionario/desguace national rows are the exact published totals
        # (5358 / 1292); the apportioned province rows sum to within rounding.
        assert prov_sum == pytest.approx(national, abs=2.0), (
            f"{seg}: province sum {prov_sum} != national {national}"
        )


@pytest.mark.unit
def test_all_anchor_values_non_negative():
    census = T.load_external_census()
    bad = {k: v for k, v in census.items() if v < 0}
    assert not bad, f"negative anchor value(s): {bad}"
