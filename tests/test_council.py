"""Golden — Fase D last increment: the N2 ADVERSARIAL COUNCIL (``pipeline/autopilot/council.py``).

The council is the live increment of the auto-auditor's N2 (Credibilidad). It replaces the declared
stub with an adversarial review that runs N **orthogonal perspectives** (legal · denominator-
credibility · source-orthogonality · market-realism), each via an INJECTABLE/mockeable
``reviewer_fn`` (the real reviewer is the LLM-runtime — these tests mock it, NO network, NO DB).

What it REUSES (the doctrinal spine, VERIFIED first-hand):
  * ``inquisition.models.indep_distance`` + the D≥2 admission rule — the SAME independence primitive
    as ``inquisition.independence.admit``: a reviewer that differs from the proposer (the PLAN) in
    fewer than 2 ``StateTuple`` dimensions shares its blind-spot and COLLUDES, so it is excluded.
  * weakest-link aggregation (MIN) — the mirror of ``indep_score=min`` / the auditor ``confidence=min``.

THE DOCTRINE under test (the reason this is not green-washing). The council ENRICHES N2 with the
adversarial REASONING of the escalation, but it NEVER changes the doctrine: legal + denominator-
authority are IRREDUCIBLE owner decisions, so they ALWAYS escalate — a council "approve" on a live
country is structurally invalid (Law I — an agent without a human may reject/escalate with full
authority, never auto-approve the irreducible). The headline tests prove: reviewers that "approve"
legal → the council STILL escalates, and the wired N2 STILL escalates with score 1.0 (the live-gate
sentinel and the 2-axis model are intact).
"""
from __future__ import annotations

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.autopilot.auditor import (  # noqa: E402
    CountryPlan,
    Decision,
    PlanClaim,
    _audit_n2_credibility,
)
from pipeline.autopilot.council import (  # noqa: E402
    COUNCIL_MIN_INDEP,
    DEFAULT_PERSPECTIVES,
    DENOMINATOR_CREDIBILITY,
    LEGAL,
    MARKET_REALISM,
    PROPOSER_STATE,
    SOURCE_ORTHOGONALITY,
    CouncilVerdict,
    Perspective,
    ReviewerReport,
    ReviewOutcome,
    Stance,
    convene,
    default_reviewer,
)
from pipeline.inquisition.models import StateTuple, indep_distance  # noqa: E402

pytestmark = pytest.mark.unit

# ---------------------------------------------------------------------------
# Reviewer-provenance fixtures — distances measured against PROPOSER_STATE.
# PROPOSER_STATE = (pack_plan, pack, plan, PLAN). D = #dimensions that differ.
# ---------------------------------------------------------------------------
INDEP = StateTuple(source="reviewer_llm", tool="llm", cache="rev", path="adversarial")  # D=4 → admitted
PARTIAL = StateTuple(source="pack_plan", tool="pack", cache="snap", path="echo")        # D=2 → admitted (boundary)
COLLUDE = StateTuple(source="pack_plan", tool="pack", cache="plan", path="echo")        # D=1 → excluded
CLONE = StateTuple(source="pack_plan", tool="pack", cache="plan", path="PLAN")          # D=0 → excluded


def _plan(country_code: str = "XX") -> CountryPlan:
    """A minimal PLAN — the council passes it opaquely to the (mocked) reviewers."""
    return CountryPlan(
        country_code=country_code,
        orthogonal_lists=("osm", "dgt_cat", "aedra"),
        geo_counts=(),
        denominator_anchor=PlanClaim(
            subject_key="denominator:XX", subject_type="denominator",
            asserted_value="1000", paths={"db_geo_count": "1000"},
        ),
        projected_overlap={},
        external_anchor=None,
    )


def _spec_reviewer(spec: dict[str, tuple[Stance, float, StateTuple]]):
    """Build a deterministic reviewer_fn from a per-perspective {name: (stance, conf, state)} map."""

    def reviewer(perspective: Perspective, plan: CountryPlan) -> ReviewerReport:
        stance, conf, state = spec[perspective.name]
        return ReviewerReport(
            perspective=perspective.name, state=state, stance=stance,
            confidence=conf, rationale=f"mock:{perspective.name}:{stance.value}",
        )

    return reviewer


def _uniform(stance: Stance, conf: float = 0.9, state: StateTuple = INDEP):
    """A reviewer_fn that returns the same stance/confidence/state for every perspective."""
    return _spec_reviewer({p.name: (stance, conf, state) for p in DEFAULT_PERSPECTIVES})


_APPROVE_ALL = {p.name: (Stance.APPROVE, 0.9, INDEP) for p in DEFAULT_PERSPECTIVES}


# ===========================================================================
# The independence primitive the council reuses (anchor on the real distances)
# ===========================================================================

class TestProvenanceFixtures:
    def test_distances_against_proposer(self) -> None:
        assert indep_distance(INDEP, PROPOSER_STATE) == 4
        assert indep_distance(PARTIAL, PROPOSER_STATE) == 2
        assert indep_distance(COLLUDE, PROPOSER_STATE) == 1
        assert indep_distance(CLONE, PROPOSER_STATE) == 0
        assert COUNCIL_MIN_INDEP == 2  # mirror of inquisition.independence.admit (D≥2)


# ===========================================================================
# convene — runs every perspective, returns one outcome each
# ===========================================================================

class TestConveneShape:
    def test_runs_all_perspectives(self) -> None:
        cv = convene(_plan(), reviewer_fn=_uniform(Stance.ESCALATE))
        assert isinstance(cv, CouncilVerdict)
        assert tuple(o.perspective for o in cv.outcomes) == tuple(p.name for p in DEFAULT_PERSPECTIVES)
        assert all(isinstance(o, ReviewOutcome) for o in cv.outcomes)

    def test_default_perspectives_cover_the_four_orthogonal_lenses(self) -> None:
        names = {p.name for p in DEFAULT_PERSPECTIVES}
        assert names == {"legal", "denominator_credibility", "source_orthogonality", "market_realism"}
        # legal + denominator-authority are the irreducible owner gates.
        assert LEGAL.irreducible and DENOMINATOR_CREDIBILITY.irreducible
        assert not SOURCE_ORTHOGONALITY.irreducible and not MARKET_REALISM.irreducible


# ===========================================================================
# D≥2 — the collusion gate (espejo de admit(): reviewer vs proposer)
# ===========================================================================

class TestIndependenceAdmission:
    def test_d_ge_2_reviewer_is_admitted(self) -> None:
        cv = convene(_plan(), reviewer_fn=_uniform(Stance.ESCALATE, state=INDEP))
        assert set(cv.admitted) == {p.name for p in DEFAULT_PERSPECTIVES}
        assert cv.colluding == ()
        assert all(o.admitted and o.distance >= 2 for o in cv.outcomes)

    def test_boundary_d_equals_2_is_admitted(self) -> None:
        cv = convene(_plan(), reviewer_fn=_uniform(Stance.ESCALATE, state=PARTIAL))
        assert set(cv.admitted) == {p.name for p in DEFAULT_PERSPECTIVES}
        assert all(o.distance == 2 and o.admitted for o in cv.outcomes)

    def test_d_lt_2_reviewer_is_collusion_excluded(self) -> None:
        """A reviewer sharing ≥3 of the 4 dimensions with the proposer colludes → excluded."""
        cv = convene(_plan(), reviewer_fn=_uniform(Stance.APPROVE, state=COLLUDE))
        assert set(cv.colluding) == {p.name for p in DEFAULT_PERSPECTIVES}
        assert cv.admitted == ()
        for o in cv.outcomes:
            assert not o.admitted and o.distance == 1
            assert o.note and "COLLUS" in o.note

    def test_clone_reviewer_d0_excluded(self) -> None:
        cv = convene(_plan(), reviewer_fn=_uniform(Stance.APPROVE, state=CLONE))
        assert cv.admitted == ()
        assert all(o.distance == 0 and not o.admitted for o in cv.outcomes)


# ===========================================================================
# Weakest-link (MIN) — over ADMITTED reviewers only
# ===========================================================================

class TestWeakestLink:
    def test_confidence_is_min_over_admitted(self) -> None:
        spec = {
            "legal": (Stance.ESCALATE, 0.9, INDEP),
            "denominator_credibility": (Stance.ESCALATE, 0.4, INDEP),  # the weakest link
            "source_orthogonality": (Stance.APPROVE, 0.8, INDEP),
            "market_realism": (Stance.APPROVE, 0.7, INDEP),
        }
        cv = convene(_plan(), reviewer_fn=_spec_reviewer(spec))
        assert cv.confidence == pytest.approx(0.4)

    def test_colluding_reviewer_does_not_drag_weakest_link(self) -> None:
        """A colluding (excluded) reviewer's confidence — even an extreme low — must NOT count."""
        spec = {
            "legal": (Stance.ESCALATE, 0.1, COLLUDE),       # D<2 → excluded; 0.1 must be ignored
            "denominator_credibility": (Stance.ESCALATE, 0.6, INDEP),
            "source_orthogonality": (Stance.APPROVE, 0.8, INDEP),
            "market_realism": (Stance.APPROVE, 0.7, INDEP),
        }
        cv = convene(_plan(), reviewer_fn=_spec_reviewer(spec))
        assert "legal" in cv.colluding
        assert cv.confidence == pytest.approx(0.6)  # 0.1 excluded → min over admitted is 0.6

    def test_no_admitted_reviewers_yields_zero_confidence(self) -> None:
        cv = convene(_plan(), reviewer_fn=_uniform(Stance.APPROVE, state=COLLUDE))
        assert cv.confidence == 0.0  # no independent signal → weakest possible


# ===========================================================================
# THE DOCTRINE — irreducible perspectives ALWAYS escalate (Law I)
# ===========================================================================

class TestIrreducibleAlwaysEscalates:
    def test_irreducible_approve_is_floored_to_escalate(self) -> None:
        cv = convene(_plan(), reviewer_fn=_spec_reviewer(_APPROVE_ALL))
        by_name = {o.perspective: o for o in cv.outcomes}
        # legal + denominator: reviewer said APPROVE, council floors the EFFECTIVE stance to ESCALATE.
        assert by_name["legal"].report.stance is Stance.APPROVE
        assert by_name["legal"].effective_stance is Stance.ESCALATE
        assert by_name["denominator_credibility"].effective_stance is Stance.ESCALATE
        # non-irreducible perspectives keep their APPROVE.
        assert by_name["source_orthogonality"].effective_stance is Stance.APPROVE
        assert by_name["market_realism"].effective_stance is Stance.APPROVE

    def test_reviewers_approving_legal_still_escalates(self) -> None:
        """HEADLINE: every reviewer 'approves' → the council STILL escalates the irreducible."""
        cv = convene(_plan(), reviewer_fn=_spec_reviewer(_APPROVE_ALL))
        assert cv.decision is Stance.ESCALATE
        assert "legal" in cv.irreducible_escalated
        assert "denominator_credibility" in cv.irreducible_escalated

    def test_irreducible_escalates_even_when_its_reviewer_colludes(self) -> None:
        """Even if the legal reviewer colludes (excluded), legal still escalates by doctrine."""
        spec = dict(_APPROVE_ALL)
        spec["legal"] = (Stance.APPROVE, 0.9, COLLUDE)  # excluded, but doctrine still escalates legal
        cv = convene(_plan(), reviewer_fn=_spec_reviewer(spec))
        assert "legal" in cv.colluding
        assert "legal" in cv.irreducible_escalated
        assert cv.decision is Stance.ESCALATE

    def test_no_admitted_reviewers_still_escalates(self) -> None:
        cv = convene(_plan(), reviewer_fn=_uniform(Stance.APPROVE, state=COLLUDE))
        assert cv.decision is Stance.ESCALATE  # no independent review → fail-safe escalate


# ===========================================================================
# Fail-closed REJECT is Law-I-safe to delegate (a provable problem can be refuted)
# ===========================================================================

class TestRejectIsDelegable:
    def test_reject_on_non_irreducible_propagates(self) -> None:
        """A D≥2 reviewer that REFUTES market-realism → council REJECT (fail-closed, most severe)."""
        spec = dict(_APPROVE_ALL)
        spec["market_realism"] = (Stance.REJECT, 0.5, INDEP)
        cv = convene(_plan(), reviewer_fn=_spec_reviewer(spec))
        assert cv.decision is Stance.REJECT

    def test_reject_beats_escalate_in_severity(self) -> None:
        cv = convene(_plan(), reviewer_fn=_uniform(Stance.REJECT))
        assert cv.decision is Stance.REJECT


# ===========================================================================
# default_reviewer — the €0, no-network honest default (escalates)
# ===========================================================================

class TestDefaultReviewer:
    def test_default_reviewer_escalates_and_is_admitted(self) -> None:
        for p in DEFAULT_PERSPECTIVES:
            r = default_reviewer(p, _plan())
            assert r.stance is Stance.ESCALATE
            assert indep_distance(r.state, PROPOSER_STATE) >= COUNCIL_MIN_INDEP  # not collusion

    def test_default_council_escalates_with_full_confidence(self) -> None:
        cv = convene(_plan(), reviewer_fn=default_reviewer)
        assert cv.decision is Stance.ESCALATE
        assert cv.confidence == 1.0  # certain it must escalate (doctrine), never drags weakest-link
        assert set(cv.admitted) == {p.name for p in DEFAULT_PERSPECTIVES}


# ===========================================================================
# as_detail — JSON-able structured reasoning for the N2 LevelVerdict.detail
# ===========================================================================

class TestAsDetail:
    def test_as_detail_is_jsonable_and_complete(self) -> None:
        cv = convene(_plan(), reviewer_fn=_spec_reviewer(_APPROVE_ALL))
        detail = cv.as_detail()
        json.dumps(detail)  # must not raise
        assert detail["decision"] == "ESCALATE"
        assert detail["confidence"] == pytest.approx(0.9)
        assert set(detail["irreducible_escalated"]) >= {"legal", "denominator_credibility"}
        assert {pp["perspective"] for pp in detail["perspectives"]} == {
            p.name for p in DEFAULT_PERSPECTIVES
        }
        assert isinstance(detail["rationale"], str) and detail["rationale"]


# ===========================================================================
# WIRING into the auditor N2 — the council enriches; the gate stays ESCALA
# ===========================================================================

class TestN2Wiring:
    def test_n2_default_wires_council_and_escalates(self) -> None:
        n2 = _audit_n2_credibility(_plan())
        assert n2.decision is Decision.ESCALA
        assert n2.score == 1.0
        assert "OWNER" in (n2.reason_code or "")
        council = n2.detail["council"]
        assert isinstance(council, dict)            # no longer the "stub" string
        assert council["decision"] == "ESCALATE"

    def test_n2_still_escalates_when_reviewers_approve(self) -> None:
        """HEADLINE WIRING: inject reviewers that approve everything → N2 IGUAL escala (irreducible)."""
        n2 = _audit_n2_credibility(_plan(), reviewer_fn=_spec_reviewer(_APPROVE_ALL))
        assert n2.decision is Decision.ESCALA          # the live gate never auto-clears
        assert n2.score == 1.0
        council = n2.detail["council"]
        assert council["decision"] == "ESCALATE"
        assert "legal" in council["irreducible_escalated"]
        assert "denominator_credibility" in council["irreducible_escalated"]

    def test_n2_score_stays_one_even_with_low_confidence_council(self) -> None:
        """The N2 score is a DOCTRINE decision (=1.0), so a low-confidence council never drags the
        auditor's weakest-link confidence. The council confidence lives in the detail instead."""
        low = {p.name: (Stance.ESCALATE, 0.05, INDEP) for p in DEFAULT_PERSPECTIVES}
        n2 = _audit_n2_credibility(_plan(), reviewer_fn=_spec_reviewer(low))
        assert n2.score == 1.0
        assert n2.detail["council"]["confidence"] == pytest.approx(0.05)

    def test_n2_surfaces_reject_finding_but_still_escalates_the_gate(self) -> None:
        """Even a council that REJECTS a perspective is surfaced to the owner, yet the live gate
        itself escalates (the agent never unilaterally kills a live country — it escalates WITH the
        evidence; only its 'approve' is structurally invalid)."""
        spec = dict(_APPROVE_ALL)
        spec["market_realism"] = (Stance.REJECT, 0.3, INDEP)
        n2 = _audit_n2_credibility(_plan(), reviewer_fn=_spec_reviewer(spec))
        assert n2.decision is Decision.ESCALA          # gate stays ESCALA (live_gate sentinel)
        assert n2.detail["council"]["decision"] == "REJECT"  # the finding is surfaced, not hidden
