"""TDD spec for the auto-pack DENOMINATOR extractor (Phase C, pieza 5).

``pipeline.autopilot.extract_denom`` turns two €0, free-reuse public sources into
a country census the MSE seal can triangulate against:

  (a) **Eurostat SBS** NACE **G45** (sale/repair of motor vehicles) — per-NUTS-region
      enterprise counts, TSV bulk format. The reliable, AUTO-extractable figure.
  (b) **GLEIF LEI Golden Copy** — registered legal entities per jurisdiction. An
      INDEPENDENT second mechanism, but all-industry: a corroboration, never a
      dealer denominator.

Doctrine pinned by these tests (the load-bearing invariant):
  * The **national all-segment** figure is auto-extractable and tagged ``[MEDIDO]``.
  * The **per-segment split** (compraventa/concesionario/desguace) is **NOT**
    auto-derivable from G45/GLEIF → it is a **CHECKPOINT** (needs_audit). The
    extractor emits the national/region all-segment anchors and **never fabricates
    the split**, degrading honestly exactly like the seal's ``no_anchor``.

Everything here is deterministic: inline fixtures, zero network. The real HTTP
fetch is a separate function, mocked out of these tests.
"""

from __future__ import annotations

import pathlib

import pytest

from pipeline.autopilot import extract_denom as D
from pipeline.exhaustiveness import triangulation as T

# --- inline fixtures (no network) -------------------------------------------------

# Eurostat SBS bulk TSV. Header: comma-joined dims + "\<TIME>" then tab-joined years.
# Noise rows are deliberate: other NACE (G46), other indicator (V13110), other
# country (YY), and an all-missing region (XX3) the parser must skip.
_EUROSTAT_ROWS = [
    ["freq,indic_sb,nace_r2,geo\\TIME_PERIOD", "2020", "2021", "2022"],
    ["A,V11110,G45,XX", "1180", "1200 e", "1250"],      # national (NUTS0)
    ["A,V11110,G45,XX1", "590", "600", "620 d"],        # region (flagged value)
    ["A,V11110,G45,XX2", "580", "590", "630"],          # region
    ["A,V11110,G45,XX3", ":", ":", ":"],                # region, all missing -> skip
    ["A,V11110,G46,XX", "9999", "9999", "9999"],        # wrong NACE -> ignore
    ["A,V13110,G45,XX", "4444", "4444", "4444"],        # wrong indicator -> ignore
    ["A,V11110,G45,YY", "7777", "7777", "7777"],        # wrong country -> ignore
]
EUROSTAT_SBS_TSV = "\n".join("\t".join(r) for r in _EUROSTAT_ROWS) + "\n"

# GLEIF LEI-CDF golden-copy subset. Active = RegistrationStatus ISSUED.
_GLEIF_ROWS = [
    "LEI,Entity.LegalName,Entity.LegalJurisdiction,Entity.LegalAddress.Country,"
    "Entity.LegalForm.EntityLegalFormCode,Registration.RegistrationStatus",
    "LEI000000000000000X1,Alpha Motors,XX,XX,ABCD,ISSUED",
    "LEI000000000000000X2,Beta Auto,XX,XX,ABCD,ISSUED",
    "LEI000000000000000X3,Gamma Cars,XX,XX,EFGH,LAPSED",       # inactive -> excluded
    "LEI000000000000000X4,Epsilon SA,XX-1,XX,ABCD,ISSUED",     # sub-jurisdiction XX-1
    "LEI000000000000000Y1,Delta Ltd,YY,YY,IJKL,ISSUED",        # other country -> excluded
]
GLEIF_CSV = "\n".join(_GLEIF_ROWS) + "\n"

CC = "XX"


# --- (a) Eurostat parsing ---------------------------------------------------------

@pytest.mark.unit
def test_parse_eurostat_picks_latest_year_national_and_regions():
    p = D.parse_eurostat_sbs_tsv(EUROSTAT_SBS_TSV, CC)
    assert p.year == "2022"
    assert p.national == 1250                       # XX @2022
    assert p.regions == {"XX1": 620, "XX2": 630}    # flags stripped, XX3 (missing) skipped


@pytest.mark.unit
def test_parse_eurostat_filters_nace_indicator_and_country():
    p = D.parse_eurostat_sbs_tsv(EUROSTAT_SBS_TSV, CC)
    # G46 (9999), V13110 (4444) and YY (7777) must never leak into the figures.
    assert 9999 not in ({p.national} | set(p.regions.values()))
    assert 4444 not in ({p.national} | set(p.regions.values()))
    assert "YY" not in p.regions and p.national != 7777


# --- (b) GLEIF parsing ------------------------------------------------------------

@pytest.mark.unit
def test_parse_gleif_counts_active_jurisdiction_entities_only():
    g = D.parse_gleif_csv(GLEIF_CSV, CC)
    # X1, X2 (XX, ISSUED) + X4 (XX-1, ISSUED). X3 LAPSED and Y1 (YY) excluded.
    assert g.total == 3
    assert g.by_legal_form.get("ABCD") == 3
    assert "EFGH" not in g.by_legal_form          # only LAPSED EFGH existed -> excluded


# --- full extraction --------------------------------------------------------------

@pytest.mark.unit
def test_extract_national_is_measured_and_regions_roll_up():
    r = D.extract_denominator(CC, sbs_tsv=EUROSTAT_SBS_TSV, gleif_csv=GLEIF_CSV)
    assert r.country_code == CC
    assert r.national_total == 1250
    assert r.national_tag == D.MEASURED
    assert sum(reg.n_external for reg in r.regions) == r.national_total
    assert {reg.region_code for reg in r.regions} == {"XX1", "XX2"}
    # GLEIF rides along as an independent crosscheck, not a denominator.
    assert r.gleif is not None and r.gleif.total == 3


@pytest.mark.unit
def test_segment_split_is_a_checkpoint_never_invented():
    r = D.extract_denominator(CC, sbs_tsv=EUROSTAT_SBS_TSV, gleif_csv=GLEIF_CSV)
    cps = {c.name: c for c in r.checkpoints}
    assert "segment_split" in cps
    assert cps["segment_split"].status == "needs_audit"
    # NOT ONE census row carries a segment: the split is judgment, not data.
    rows = r.census_rows()
    assert all(segment == "" for (_prov, segment, _n) in rows), (
        f"fabricated per-segment anchor(s): {[row for row in rows if row[1]]}"
    )


@pytest.mark.unit
def test_census_rows_have_national_and_region_all_segment_anchors():
    r = D.extract_denominator(CC, sbs_tsv=EUROSTAT_SBS_TSV, gleif_csv=GLEIF_CSV)
    rows = set(r.census_rows())
    assert ("", "", "1250") in rows                 # national all-segment (None, None)
    assert ("XX1", "", "620") in rows
    assert ("XX2", "", "630") in rows


# --- the seam: triangulation.load_external_census must read it without error -------

@pytest.mark.unit
def test_written_csv_is_consumed_by_load_external_census(tmp_path):
    r = D.extract_denominator(CC, sbs_tsv=EUROSTAT_SBS_TSV, gleif_csv=GLEIF_CSV)
    csv_path = tmp_path / D.DENOM_CSV_NAME
    r.write_census_csv(csv_path)

    census = T.load_external_census(path=csv_path, country_code=CC)
    # National all-segment anchor is the key the seal triangulates against.
    assert census[(None, None)] == pytest.approx(1250.0)
    # Region all-segment anchors present, keyed (region, None).
    assert census[("XX1", None)] == pytest.approx(620.0)
    assert census[("XX2", None)] == pytest.approx(630.0)
    # No per-segment anchors fabricated.
    assert not [k for k in census if k[1] is not None]
    # Non-negative, and it actually drives a triangulation verdict.
    assert all(v >= 0 for v in census.values())
    verdict = T.triangulate(1250.0, census[(None, None)])
    assert verdict["verdict"] == "consistent"


@pytest.mark.unit
def test_written_csv_loads_by_default_country_dir(tmp_path):
    # With a per-country root override, the default resolution (no explicit path)
    # finds the file under countries/XX/census/<DENOM_CSV_NAME>.
    from pipeline.paths import census_dir

    dest = census_dir(CC, root=tmp_path)
    dest.mkdir(parents=True, exist_ok=True)
    r = D.extract_denominator(CC, sbs_tsv=EUROSTAT_SBS_TSV, gleif_csv=GLEIF_CSV)
    r.write_census_csv(dest / D.DENOM_CSV_NAME)
    census = T.load_external_census(path=dest / D.DENOM_CSV_NAME, country_code=CC)
    assert census[(None, None)] == pytest.approx(1250.0)


# --- SOURCE.md provenance ---------------------------------------------------------

@pytest.mark.unit
def test_source_md_tags_every_figure_and_declares_the_checkpoint(tmp_path):
    r = D.extract_denominator(CC, sbs_tsv=EUROSTAT_SBS_TSV, gleif_csv=GLEIF_CSV)
    md_path = tmp_path / "SOURCE.md"
    r.write_source_md(md_path)
    md = md_path.read_text(encoding="utf-8")

    assert D.MEASURED in md                          # national figure is [MEDIDO]
    assert "Eurostat" in md and "G45" in md          # primary source named
    assert "GLEIF" in md                             # secondary mechanism named
    assert str(r.national_total) in md               # the figure itself is present
    # The split is declared as a checkpoint, not silently dropped or invented.
    assert "CHECKPOINT" in md
    assert "needs_audit" in md
    assert "split" in md.lower()


# --- determinism & honest hard-fail ----------------------------------------------

@pytest.mark.unit
def test_outputs_are_byte_deterministic(tmp_path):
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    ma, mb = tmp_path / "a.md", tmp_path / "b.md"
    D.extract_denominator(CC, sbs_tsv=EUROSTAT_SBS_TSV, gleif_csv=GLEIF_CSV).write_census_csv(a)
    D.extract_denominator(CC, sbs_tsv=EUROSTAT_SBS_TSV, gleif_csv=GLEIF_CSV).write_census_csv(b)
    D.extract_denominator(CC, sbs_tsv=EUROSTAT_SBS_TSV, gleif_csv=GLEIF_CSV).write_source_md(ma)
    D.extract_denominator(CC, sbs_tsv=EUROSTAT_SBS_TSV, gleif_csv=GLEIF_CSV).write_source_md(mb)
    assert a.read_bytes() == b.read_bytes()
    assert ma.read_bytes() == mb.read_bytes()


@pytest.mark.unit
def test_national_falls_back_to_region_sum_when_no_nuts0():
    # Drop the NUTS0 national row: national must roll up from measured regions.
    rows = [r for r in _EUROSTAT_ROWS if r[0] != "A,V11110,G45,XX"]
    tsv = "\n".join("\t".join(r) for r in rows) + "\n"
    res = D.extract_denominator(CC, sbs_tsv=tsv, gleif_csv=GLEIF_CSV)
    assert res.national_total == 1250               # 620 + 630
    assert res.national_tag == D.MEASURED


@pytest.mark.unit
def test_empty_eurostat_raises_rather_than_fabricating():
    empty = "freq,indic_sb,nace_r2,geo\\TIME_PERIOD\t2022\n"
    with pytest.raises(ValueError):
        D.extract_denominator(CC, sbs_tsv=empty, gleif_csv=GLEIF_CSV)
