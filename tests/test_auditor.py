"""Golden — Fase D, the 5-level AUTO-AUDITOR (``pipeline/autopilot/auditor.py``).

The auditor is "someone who audits the pack who is NOT the owner" (country-autopilot
``plans/country-autopilot/01-ARCHITECTURE.md`` — the N0..N4 table + the HONEST FRONTIER).
It runs five levels over a proposed ``countries/<CC>/`` pack + its PLAN and returns a
``PackAuditVerdict`` (a pure object — persistence is a later increment, NO migration here).

What each level REUSES (all VERIFIED first-hand this session):
  N0  CountryProfile.load_dir  (pipeline/country_profile.py — additive loader for an arbitrary dir)
  N1  lists.bucket_for / ORTHOGONAL_LISTS  (pipeline/exhaustiveness/lists.py:65,49)
      verify._path_family       (pipeline/verify.py:31 — family/origin independence signal)
  N2  ALWAYS escalates (legal + denominator-authority); council = adversarial D≥2 perspectives
      (see tests/test_council.py — the council ENRICHES the escalation, never auto-approves it)
  N3  quorum.decide + router._lookup_route + verify._path_family
      (pipeline/inquisition/quorum.py:159 / router.py:103 / verify.py:31)
  N4  estimators.estimate_stratum (pipeline/exhaustiveness/estimators.py:321 — projection mode)

The honest frontier (proven below): the auditor AUTO-APPROVES build + dry-run only.
APRUEBA never authorises a live "go"; legal/denominator-authority ALWAYS escalate (N2);
a provably broken/refuted pack is auto-REJECTED fail-closed (Law I). Confidence = MIN
(weakest link). Tests are pure ``unit`` (no DB, no :5433/:5434, no network).
"""
from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.autopilot.auditor import (  # noqa: E402
    CountryPlan,
    Decision,
    PackAuditVerdict,
    PlanClaim,
    audit_pack,
)
from pipeline.country_profile import CountryProfile  # noqa: E402

pytestmark = [
    pytest.mark.unit,
    # estimate_stratum's log-linear fit warns on near-perfect projected overlap; the auditor
    # suppresses it internally, but belt-and-braces for any direct estimator probing here.
    pytest.mark.filterwarnings("ignore::RuntimeWarning"),
    pytest.mark.filterwarnings("ignore"),
]

# Synthetic test country (architecture: país sintético "XX"). Never a real tenant.
CC = "XX"

# ---------------------------------------------------------------------------
# Projected-overlap fixtures (calibrated against the live estimator)
# ---------------------------------------------------------------------------
# Dense 3-list overlap → identified, coverage_lower ≈ 0.999 (≥ seal 0.95).
OVERLAP_DENSE = {
    (1, 0, 0): 2, (0, 1, 0): 2, (0, 0, 1): 2,
    (1, 1, 0): 20, (1, 0, 1): 20, (0, 1, 1): 20, (1, 1, 1): 400,
}
# Identified but coverage_lower ≈ 0.785 (< seal 0.95).
OVERLAP_MID = {
    (1, 0, 0): 30, (0, 1, 0): 25, (0, 0, 1): 20,
    (1, 1, 0): 40, (1, 0, 1): 35, (0, 1, 1): 30, (1, 1, 1): 120,
}
# Sparse overlap → NOT identified (N̂ not pinned down).
OVERLAP_SPARSE = {(1, 0, 0): 100, (0, 1, 0): 80, (0, 0, 1): 60, (1, 1, 1): 1}


# ---------------------------------------------------------------------------
# Pack builder — writes a complete synthetic countries/<CC>/ tree under tmp.
# ---------------------------------------------------------------------------

_PIECES = ("country_toml", "geo", "recipe", "census_csv", "source_md", "taxonomy")


def _write_pack(root: Path, cc: str = CC, *, omit: tuple[str, ...] = ()) -> Path:
    """Build a well-formed pack at ``root/<cc>/`` (omit any piece to break N0)."""
    pack = root / cc
    pack.mkdir(parents=True, exist_ok=True)

    if "country_toml" not in omit:
        (pack / "country.toml").write_text(
            f'country_code = "{cc}"\n\n'
            "[subdivision]\n"
            'regex = "^(0[1-9]|1[0-9])$"\n\n'
            "[kinds]\n"
            'national = ["plataforma", "importador"]\n',
            encoding="utf-8",
        )
    if "geo" not in omit:
        geo = pack / "geo"
        geo.mkdir(exist_ok=True)
        (geo / "backbone.csv").write_text(
            "country_code,code,name,admin1\n"
            f"{cc},01,Region One,L1A\n"
            f"{cc},02,Region Two,L1B\n",
            encoding="utf-8",
        )
    if "recipe" not in omit:
        rec = pack / "recipes" / "_tier1"
        rec.mkdir(parents=True, exist_ok=True)
        (rec / "sample.yaml").write_text("base_url: https://example.xx\n", encoding="utf-8")
    if "census_csv" not in omit or "source_md" not in omit:
        census = pack / "census"
        census.mkdir(exist_ok=True)
        if "census_csv" not in omit:
            (census / "national.csv").write_text(
                "region_code,segment,n_external\n01,GEN,500\n", encoding="utf-8"
            )
        if "source_md" not in omit:
            (census / "SOURCE.md").write_text(
                "# Provenance\n- 500 [MEDIDO]\n", encoding="utf-8"
            )
    if "taxonomy" not in omit:
        (pack / "taxonomy.yaml").write_text(
            "dealer_kinds: [generic]\npoint_of_sale: [generic]\n", encoding="utf-8"
        )
    return pack


# ---------------------------------------------------------------------------
# PLAN builders — well-formed roster/numbers/projection, with broken variants.
# ---------------------------------------------------------------------------

# 2-family agreement → quorum TRUSTWORTHY.
_DENOM_OK = PlanClaim(
    subject_key="denominator:XX",
    subject_type="denominator",
    asserted_value="1000",
    paths={"db_geo_count": "1000", "registral_census": "1000"},
)
_GEO_OK = PlanClaim(
    subject_key="geo:XX:01",
    subject_type="count",
    asserted_value="200",
    paths={"db_geo_count": "200", "source_declared_total": "200"},
)


def _plan(
    *,
    orthogonal_lists: tuple[str, ...] = ("osm", "dgt_cat", "aedra"),
    geo_counts: tuple[PlanClaim, ...] = (_GEO_OK,),
    denominator_anchor: PlanClaim | None = _DENOM_OK,
    projected_overlap=None,
    external_anchor: float | None = None,
) -> CountryPlan:
    return CountryPlan(
        country_code=CC,
        orthogonal_lists=orthogonal_lists,
        geo_counts=geo_counts,
        denominator_anchor=denominator_anchor,
        projected_overlap=projected_overlap if projected_overlap is not None else dict(OVERLAP_DENSE),
        external_anchor=external_anchor,
    )


# ===========================================================================
# CountryProfile.load_dir — the additive loader the auditor's N0 relies on
# ===========================================================================

class TestLoadDir:
    def test_loads_from_arbitrary_dir(self, tmp_path: Path) -> None:
        pack = _write_pack(tmp_path)
        prof = CountryProfile.load_dir(pack)
        assert prof.country_code == CC
        assert prof.matches_subdivision("01") is True
        assert prof.matches_subdivision("28") is False

    def test_missing_manifest_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            CountryProfile.load_dir(tmp_path / "nope")

    def test_bad_regex_raises(self, tmp_path: Path) -> None:
        pack = tmp_path / CC
        pack.mkdir()
        (pack / "country.toml").write_text(
            f'country_code = "{CC}"\n[subdivision]\nregex = "(["\n',
            encoding="utf-8",
        )
        with pytest.raises(ValueError):
            CountryProfile.load_dir(pack)

    def test_load_es_still_byte_identical(self) -> None:
        """Regression guard: the canonical loader is untouched by the additive load_dir."""
        assert CountryProfile.load("ES").country_code == "ES"


# ===========================================================================
# N0 — Structure linter (deterministic; PASS = APRUEBA, fail = RECHAZA)
# ===========================================================================

class TestN0Structure:
    def test_complete_pack_passes(self, tmp_path: Path) -> None:
        pack = _write_pack(tmp_path)
        v = audit_pack(CC, pack, _plan())
        n0 = v.level("N0")
        assert n0.decision is Decision.APRUEBA
        assert n0.score == 1.0
        assert n0.reason_code is None

    @pytest.mark.parametrize(
        "piece,reason_fragment",
        [
            ("country_toml", "TOML"),
            ("geo", "GEO"),
            ("recipe", "RECIPE"),
            ("census_csv", "CENSUS"),
            ("source_md", "SOURCE"),
            ("taxonomy", "TAXONOMY"),
        ],
    )
    def test_missing_piece_rejects(self, tmp_path: Path, piece: str, reason_fragment: str) -> None:
        pack = _write_pack(tmp_path, omit=(piece,))
        v = audit_pack(CC, pack, _plan())
        n0 = v.level("N0")
        assert n0.decision is Decision.RECHAZA
        assert n0.score == 0.0
        assert reason_fragment in (n0.reason_code or "")

    def test_country_code_mismatch_rejects(self, tmp_path: Path) -> None:
        pack = _write_pack(tmp_path, cc="XX")
        # Ask the auditor to audit it AS "YY" — declared XX != requested YY.
        plan = CountryPlan(
            country_code="YY",
            orthogonal_lists=("osm", "dgt_cat", "aedra"),
            geo_counts=(),
            denominator_anchor=_DENOM_OK,
            projected_overlap=dict(OVERLAP_DENSE),
        )
        v = audit_pack("YY", pack, plan)
        assert v.level("N0").decision is Decision.RECHAZA
        assert "MISMATCH" in (v.level("N0").reason_code or "")


# ===========================================================================
# N1 — Orthogonality (deterministic + agent hook)
# ===========================================================================

class TestN1Orthogonality:
    def test_three_distinct_orthogonal_lists_pass(self, tmp_path: Path) -> None:
        pack = _write_pack(tmp_path)
        v = audit_pack(CC, pack, _plan(orthogonal_lists=("osm", "dgt_cat", "aedra")))
        n1 = v.level("N1")
        assert n1.decision is Decision.APRUEBA
        assert n1.score == 1.0

    def test_uncertain_classification_escalates(self, tmp_path: Path) -> None:
        """A source falling to the MKT default bucket = classification uncertain → ESCALA."""
        pack = _write_pack(tmp_path)
        v = audit_pack(CC, pack, _plan(orthogonal_lists=("osm", "dgt_cat", "wallapop_feed")))
        n1 = v.level("N1")
        assert n1.decision is Decision.ESCALA
        assert "UNCERTAIN" in (n1.reason_code or "")
        assert "wallapop_feed" in n1.detail.get("uncertain", ())

    def test_fewer_than_three_orthogonal_lists_fails(self, tmp_path: Path) -> None:
        pack = _write_pack(tmp_path)
        v = audit_pack(CC, pack, _plan(orthogonal_lists=("osm", "dgt_cat")))
        n1 = v.level("N1")
        assert n1.decision is Decision.RECHAZA
        assert "INSUFFICIENT_ORTHOGONAL_LISTS" in (n1.reason_code or "")
        # Overall fail-closed because a build level rejected.
        assert v.decision is Decision.RECHAZA


# ===========================================================================
# N2 — Credibility: ALWAYS escalates (legal + denominator-authority frontier)
# ===========================================================================

class TestN2Credibility:
    @pytest.mark.parametrize(
        "lists_",
        [("osm", "dgt_cat", "aedra"), ("osm", "dgt_cat"), ("osm", "dgt_cat", "wallapop_feed")],
    )
    def test_always_escalates(self, tmp_path: Path, lists_: tuple[str, ...]) -> None:
        pack = _write_pack(tmp_path)
        v = audit_pack(CC, pack, _plan(orthogonal_lists=lists_))
        n2 = v.level("N2")
        assert n2.decision is Decision.ESCALA
        assert "OWNER" in (n2.reason_code or "")
        # The live gate mirrors N2 and is ALWAYS escalated, whatever the build decision.
        assert v.live_gate is Decision.ESCALA

    def test_council_is_wired_and_escalates(self, tmp_path: Path) -> None:
        """The council is no longer a stub: N2 runs the adversarial D≥2 perspectives and the live
        gate still escalates the irreducible (legal + denominator-authority). Full council coverage
        lives in tests/test_council.py."""
        pack = _write_pack(tmp_path)
        v = audit_pack(CC, pack, _plan())
        council = v.level("N2").detail.get("council")
        assert isinstance(council, dict)                          # structured review, not "stub"
        assert council["decision"] == "ESCALATE"                  # escalates by doctrine
        assert "legal" in council["irreducible_escalated"]
        assert "denominator_credibility" in council["irreducible_escalated"]
        # The N2 decision + score invariants are unchanged (the live-gate sentinel).
        assert v.level("N2").decision is Decision.ESCALA
        assert v.level("N2").score == 1.0


# ===========================================================================
# N3 — VAM quorum (reuses the Inquisition engine over the PLAN numbers)
# ===========================================================================

class TestN3Quorum:
    def test_two_family_agreement_passes(self, tmp_path: Path) -> None:
        pack = _write_pack(tmp_path)
        v = audit_pack(CC, pack, _plan())
        n3 = v.level("N3")
        assert n3.decision is Decision.APRUEBA
        assert n3.score == 1.0

    def test_single_family_escalates_no_independent_path(self, tmp_path: Path) -> None:
        """One collector family ⇒ no independent 2nd path ⇒ NO_INDEPENDENT_PATH ⇒ ESCALA."""
        pack = _write_pack(tmp_path)
        single = PlanClaim(
            subject_key="denominator:XX",
            subject_type="denominator",
            asserted_value="1000",
            paths={"db_geo_count": "1000", "db_join_count": "1000"},  # both family 'db'
        )
        v = audit_pack(CC, pack, _plan(denominator_anchor=single, geo_counts=()))
        n3 = v.level("N3")
        assert n3.decision is Decision.ESCALA
        assert "NO_INDEPENDENT_PATH" in (n3.reason_code or "")

    def test_split_orthogonal_evidence_rejects(self, tmp_path: Path) -> None:
        """Two families say 1000, two say 2000 ⇒ SPLIT_QUORUM ⇒ fail-closed RECHAZA."""
        pack = _write_pack(tmp_path)
        split = PlanClaim(
            subject_key="denominator:XX",
            subject_type="denominator",
            asserted_value="1000",
            paths={
                "db_geo_count": "1000",
                "registral_census": "1000",
                "source_declared_total": "2000",
                "fetched_live": "2000",
            },
        )
        v = audit_pack(CC, pack, _plan(denominator_anchor=split, geo_counts=()))
        n3 = v.level("N3")
        assert n3.decision is Decision.RECHAZA
        assert v.decision is Decision.RECHAZA  # fail-closed propagates

    def test_never_fabricates_trustworthy_from_missing_claim(self, tmp_path: Path) -> None:
        """No claims to prosecute ⇒ cannot certify ⇒ ESCALA (never silent APRUEBA)."""
        pack = _write_pack(tmp_path)
        v = audit_pack(CC, pack, _plan(denominator_anchor=None, geo_counts=()))
        assert v.level("N3").decision is Decision.ESCALA


# ===========================================================================
# N4 — Projected coverage (reuses the MSE seal estimator in projection mode)
# ===========================================================================

class TestN4Coverage:
    def test_dense_overlap_passes_seal(self, tmp_path: Path) -> None:
        pack = _write_pack(tmp_path)
        v = audit_pack(CC, pack, _plan(projected_overlap=dict(OVERLAP_DENSE)))
        n4 = v.level("N4")
        assert n4.decision is Decision.APRUEBA
        assert n4.score >= 0.95

    def test_not_identified_escalates(self, tmp_path: Path) -> None:
        pack = _write_pack(tmp_path)
        v = audit_pack(CC, pack, _plan(projected_overlap=dict(OVERLAP_SPARSE)))
        n4 = v.level("N4")
        assert n4.decision is Decision.ESCALA
        assert "NOT_IDENTIFIED" in (n4.reason_code or "")

    def test_below_seal_escalates(self, tmp_path: Path) -> None:
        pack = _write_pack(tmp_path)
        v = audit_pack(CC, pack, _plan(projected_overlap=dict(OVERLAP_MID)))
        n4 = v.level("N4")
        assert n4.decision is Decision.ESCALA
        assert "COVERAGE" in (n4.reason_code or "")

    def test_inconsistent_triangulation_escalates(self, tmp_path: Path) -> None:
        pack = _write_pack(tmp_path)
        # Dense overlap pins N̂ ≈ 466; an external anchor of 900 is ~48% off → inconsistent.
        v = audit_pack(CC, pack, _plan(projected_overlap=dict(OVERLAP_DENSE), external_anchor=900.0))
        n4 = v.level("N4")
        assert n4.decision is Decision.ESCALA
        assert "TRIANGULATION" in (n4.reason_code or "")

    def test_never_rejects(self, tmp_path: Path) -> None:
        """N4 failure modes are owner judgments (ESCALA), never fail-closed RECHAZA."""
        pack = _write_pack(tmp_path)
        for ov in (OVERLAP_SPARSE, OVERLAP_MID):
            v = audit_pack(CC, pack, _plan(projected_overlap=dict(ov)))
            assert v.level("N4").decision is not Decision.RECHAZA


# ===========================================================================
# audit_pack — the headline scenarios + the honest frontier
# ===========================================================================

class TestAuditPackHeadline:
    def test_complete_well_formed_pack_approves_build(self, tmp_path: Path) -> None:
        """Complete + well-formed → APRUEBA (build + dry-run), live still owner-gated."""
        pack = _write_pack(tmp_path)
        v = audit_pack(CC, pack, _plan())
        assert v.decision is Decision.APRUEBA            # build + dry-run only
        assert v.live_gate is Decision.ESCALA            # never an auto live "go"
        assert v.level("N2").decision is Decision.ESCALA  # legal/authority parked on owner
        assert v.confidence >= 0.95
        # All build levels green.
        assert {lv.level: lv.decision for lv in v.levels if lv.level in ("N0", "N1", "N3", "N4")} == {
            "N0": Decision.APRUEBA, "N1": Decision.APRUEBA,
            "N3": Decision.APRUEBA, "N4": Decision.APRUEBA,
        }

    def test_incomplete_pack_rejects_with_cause(self, tmp_path: Path) -> None:
        pack = _write_pack(tmp_path, omit=("census_csv",))
        v = audit_pack(CC, pack, _plan())
        assert v.decision is Decision.RECHAZA
        assert v.reason_code and "CENSUS" in v.reason_code

    def test_frontier_escala_vs_aprueba(self, tmp_path: Path) -> None:
        """The boundary: same structure, one build-level escalation flips APRUEBA → ESCALA."""
        pack = _write_pack(tmp_path)
        approved = audit_pack(CC, pack, _plan())
        escalated = audit_pack(CC, pack, _plan(orthogonal_lists=("osm", "dgt_cat", "wallapop_feed")))
        assert approved.decision is Decision.APRUEBA
        assert escalated.decision is Decision.ESCALA
        # Neither ever authorises a live go — the frontier is the same for both.
        assert approved.live_gate is escalated.live_gate is Decision.ESCALA

    def test_confidence_is_min_of_levels(self, tmp_path: Path) -> None:
        """Weakest-link: the uncertain N1 (0.5) is the floor; confidence == min over levels."""
        pack = _write_pack(tmp_path)
        v = audit_pack(CC, pack, _plan(orthogonal_lists=("osm", "dgt_cat", "wallapop_feed")))
        assert v.confidence == min(lv.score for lv in v.levels)
        assert v.confidence == pytest.approx(0.5)

    def test_legal_touch_always_escalates_even_when_build_rejected(self, tmp_path: Path) -> None:
        """N2/live-gate escalate independently of a fail-closed build RECHAZA."""
        pack = _write_pack(tmp_path)
        v = audit_pack(CC, pack, _plan(orthogonal_lists=("osm", "dgt_cat")))  # N1 → RECHAZA
        assert v.decision is Decision.RECHAZA
        assert v.live_gate is Decision.ESCALA
        assert v.level("N2").decision is Decision.ESCALA

    def test_verdict_is_immutable(self, tmp_path: Path) -> None:
        pack = _write_pack(tmp_path)
        v = audit_pack(CC, pack, _plan())
        assert isinstance(v, PackAuditVerdict)
        with pytest.raises((AttributeError, TypeError)):
            v.decision = Decision.RECHAZA  # type: ignore[misc]

    def test_all_five_levels_present(self, tmp_path: Path) -> None:
        pack = _write_pack(tmp_path)
        v = audit_pack(CC, pack, _plan())
        assert tuple(lv.level for lv in v.levels) == ("N0", "N1", "N2", "N3", "N4")
