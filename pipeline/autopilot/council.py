"""Fase D — the N2 ADVERSARIAL COUNCIL (the last increment of the auto-auditor).

The auditor's N2 (Credibilidad) used to be a declared stub that escalated by fiat. This module is
its live body: an adversarial council that, given the PLAN, runs N **orthogonal perspectives**
(legal · denominator-credibility · source-orthogonality · market-realism), each delivered by an
INJECTABLE/mockeable ``reviewer_fn``. The real reviewer is the LLM-runtime; the council itself stays
PURE and network-free, so it is fully unit-testable with mocked reviewers.

It reuses the doctrinal spine instead of inventing a second one:

* **D≥2 admission** — ``inquisition.models.indep_distance`` and the same ``D≥2`` rule as
  ``inquisition.independence.admit``. A reviewer is a witness only if it differs from the proposer
  (the PLAN, :data:`PROPOSER_STATE`) in ≥2 of the 4 ``StateTuple`` dimensions. A reviewer that
  shares ≥3 dimensions sits inside the proposer's blind-spot — it would rubber-stamp the very frame
  it should challenge — so it COLLUDES and is excluded from the aggregation (mirror of the
  Inquisition refusing a near-clone skeptic a quorum vote).
* **weakest-link (MIN)** — the council confidence is the minimum reviewer confidence over the
  ADMITTED reviewers, the mirror of ``indep_score=min`` and the auditor's ``confidence=min``.

THE DOCTRINE (why this enriches without changing the verdict). The council aggregates the adversarial
REASONING behind N2's escalation, but it never changes the doctrine. Legal and denominator-authority
are IRREDUCIBLE owner decisions: an agent without a human may REJECT or ESCALATE with full authority,
but its "approve" over a live country is structurally invalid (Law I). So for an irreducible
perspective the council can never settle below ESCALATE — a reviewer's APPROVE is recorded and then
FLOORED to ESCALATE. Fail-closed REJECT, by contrast, is safe to delegate (a provable problem can be
refuted), so it is the one outcome more severe than ESCALATE that the council may reach on its own.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Sequence

from pipeline.inquisition.models import StateTuple, indep_distance

if TYPE_CHECKING:  # type-only — importing CountryPlan at runtime would be circular (auditor→council).
    from pipeline.autopilot.auditor import CountryPlan


# ---------------------------------------------------------------------------
# The proposer + the admission threshold (espejo de inquisition.independence)
# ---------------------------------------------------------------------------

# The PLAN under review is the proposer. Mirrors auditor._plan_producer's 4-tuple identity, with a
# pack-level ``path`` (the whole PLAN, not one number). A reviewer is admitted iff it differs from
# this in ≥2 dimensions — the SAME D≥2 condition as inquisition.independence.admit.
PROPOSER_STATE = StateTuple(source="pack_plan", tool="pack", cache="plan", path="PLAN")
COUNCIL_MIN_INDEP = 2  # D≥2 — a reviewer below this colludes with the proposer.


# ---------------------------------------------------------------------------
# Stance — one reviewer's (and the council's) outcome on a perspective
# ---------------------------------------------------------------------------

class Stance(str, Enum):
    """A review outcome. Severity order mirrors the auditor's Decision precedence.

    APPROVE:  the reviewer finds no concern (NEVER a valid settled outcome on an irreducible gate).
    ESCALATE: owner decision required (the only valid outcome on an irreducible gate by default).
    REJECT:   a provable disqualifying problem (fail-closed — Law-I-safe to delegate).
    """

    APPROVE = "APPROVE"
    ESCALATE = "ESCALATE"
    REJECT = "REJECT"


# REJECT (fail-closed) dominates ESCALATE (owner) dominates APPROVE — mirror of auditor._RANK.
_STANCE_RANK: dict[Stance, int] = {Stance.APPROVE: 0, Stance.ESCALATE: 1, Stance.REJECT: 2}


def _most_severe(stances: Sequence[Stance]) -> Stance:
    """Weakest-link in stance space: the most severe stance (== the minimum-score link)."""
    return max(stances, key=lambda s: _STANCE_RANK[s])


# ---------------------------------------------------------------------------
# Perspective — one orthogonal adversarial lens
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Perspective:
    """One orthogonal review angle.

    ``irreducible`` marks the owner-authority gates (legal, denominator-authority) the council may
    never auto-approve: an APPROVE on these is floored to ESCALATE (Law I).
    """

    name: str
    irreducible: bool


LEGAL = Perspective("legal", irreducible=True)
DENOMINATOR_CREDIBILITY = Perspective("denominator_credibility", irreducible=True)
SOURCE_ORTHOGONALITY = Perspective("source_orthogonality", irreducible=False)
MARKET_REALISM = Perspective("market_realism", irreducible=False)

# The four orthogonal perspectives N2 convenes (architecture: "council adversarial + JUICIO").
DEFAULT_PERSPECTIVES: tuple[Perspective, ...] = (
    LEGAL,
    DENOMINATOR_CREDIBILITY,
    SOURCE_ORTHOGONALITY,
    MARKET_REALISM,
)


# ---------------------------------------------------------------------------
# Reviewer report + the injectable reviewer function
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ReviewerReport:
    """One reviewer's verdict on one perspective.

    ``state`` is the reviewer's own provenance — the council measures ``indep_distance(state,
    proposer)`` to decide admission. The real LLM reviewer sets ``state`` from the independent
    evidence/method it used; a reviewer that cannot source anything beyond the PLAN itself reports a
    near-proposer state and is correctly excluded as collusion.
    """

    perspective: str
    state: StateTuple
    stance: Stance
    confidence: float
    rationale: str


# (perspective, plan) -> report. INJECTABLE: the real impl calls the LLM-runtime; tests mock it.
ReviewerFn = Callable[[Perspective, "CountryPlan"], ReviewerReport]


@dataclass(frozen=True)
class ReviewOutcome:
    """One perspective's outcome after admission + the irreducible floor."""

    perspective: str
    irreducible: bool
    report: ReviewerReport
    distance: int               # D(report.state, proposer)
    admitted: bool              # D ≥ COUNCIL_MIN_INDEP
    effective_stance: Stance    # report.stance, floored to ESCALATE if irreducible APPROVE
    note: str | None            # collusion / floor annotation for the audit trail


@dataclass(frozen=True)
class CouncilVerdict:
    """The council's aggregate finding — pure reasoning, surfaced into the N2 LevelVerdict.detail."""

    decision: Stance
    confidence: float                       # weakest-link MIN over admitted reviewers (0.0 if none)
    outcomes: tuple[ReviewOutcome, ...]
    admitted: tuple[str, ...]
    colluding: tuple[str, ...]
    irreducible_escalated: tuple[str, ...]  # the perspectives that escalate by doctrine
    rationale: str

    def as_detail(self) -> dict[str, Any]:
        """A JSON-able dict for the auditor's N2 ``LevelVerdict.detail`` (enriched reasoning)."""
        return {
            "decision": self.decision.value,
            "confidence": self.confidence,
            "admitted": list(self.admitted),
            "colluding": list(self.colluding),
            "irreducible_escalated": list(self.irreducible_escalated),
            "rationale": self.rationale,
            "perspectives": [
                {
                    "perspective": o.perspective,
                    "irreducible": o.irreducible,
                    "stance": o.report.stance.value,
                    "effective_stance": o.effective_stance.value,
                    "confidence": o.report.confidence,
                    "distance": o.distance,
                    "admitted": o.admitted,
                    "note": o.note,
                    "rationale": o.report.rationale,
                }
                for o in self.outcomes
            ],
        }


# ---------------------------------------------------------------------------
# default_reviewer — the €0, no-network honest default
# ---------------------------------------------------------------------------

def default_reviewer(perspective: Perspective, plan: "CountryPlan") -> ReviewerReport:
    """The default the auditor uses when no LLM reviewer is injected.

    There is no adversarial LLM-runtime wired in a €0 dry-run, so the honest outcome is ESCALATE: the
    council cannot CLEAR a perspective without a real independent reviewer. Its provenance is fully
    independent of the proposer (D=4), so the escalation is a genuine doctrine signal — admitted, not
    collusion — and its confidence is 1.0 (it is certain it must escalate; this never drags the
    auditor's weakest-link, exactly like the N2 score=1.0 doctrine).
    """
    return ReviewerReport(
        perspective=perspective.name,
        state=StateTuple(source="doctrine", tool="council", cache="static", path=perspective.name),
        stance=Stance.ESCALATE,
        confidence=1.0,
        rationale=(
            f"No adversarial LLM reviewer wired (€0 dry-run); '{perspective.name}' escalates by "
            f"doctrine (Law I — the live gate is never auto-cleared)."
        ),
    )


# ---------------------------------------------------------------------------
# convene — run the perspectives, admit on D≥2, weakest-link, apply the doctrine
# ---------------------------------------------------------------------------

def _floor_irreducible(stance: Stance, irreducible: bool) -> tuple[Stance, str | None]:
    """Law I: an irreducible perspective can never settle on APPROVE → floor it to ESCALATE."""
    if irreducible and stance is Stance.APPROVE:
        return Stance.ESCALATE, "IRREDUCIBLE_APPROVE_FLOORED_TO_ESCALATE"
    return stance, None


def _review_one(perspective: Perspective, plan: "CountryPlan", reviewer_fn: ReviewerFn,
                proposer: StateTuple) -> ReviewOutcome:
    report = reviewer_fn(perspective, plan)
    distance = indep_distance(report.state, proposer)
    admitted = distance >= COUNCIL_MIN_INDEP
    if not admitted:
        # Collusion: the reviewer shares the proposer's blind-spot → it carries no independent signal.
        return ReviewOutcome(
            perspective.name, perspective.irreducible, report, distance, False,
            report.stance, f"COLLUSION_D{distance}_LT_{COUNCIL_MIN_INDEP}",
        )
    effective, note = _floor_irreducible(report.stance, perspective.irreducible)
    return ReviewOutcome(
        perspective.name, perspective.irreducible, report, distance, True, effective, note,
    )


def _aggregate_decision(outcomes: Sequence[ReviewOutcome]) -> Stance:
    """Most-severe ADMITTED effective stance, with the doctrinal floor.

    Floor = ESCALATE when any irreducible perspective is present (its APPROVE is invalid) OR when no
    reviewer was admitted (no independent review → fail-safe escalate). REJECT from an admitted
    reviewer still wins (fail-closed is Law-I-safe to delegate).
    """
    admitted = [o for o in outcomes if o.admitted]
    has_irreducible = any(o.irreducible for o in outcomes)
    floor = Stance.ESCALATE if (has_irreducible or not admitted) else Stance.APPROVE
    return _most_severe([o.effective_stance for o in admitted] + [floor])


def _rationale(decision: Stance, confidence: float, outcomes: Sequence[ReviewOutcome],
               irreducible_escalated: Sequence[str]) -> str:
    parts = [
        f"Council {decision.value} (weakest-link confidence={confidence:.2f}).",
    ]
    if irreducible_escalated:
        parts.append(
            "Irreducible owner gates escalate by doctrine (Law I): "
            + ", ".join(irreducible_escalated) + "."
        )
    admitted = [
        f"{o.perspective}[{o.effective_stance.value}"
        + (f"←{o.report.stance.value}" if o.effective_stance is not o.report.stance else "")
        + "]"
        for o in outcomes if o.admitted
    ]
    parts.append("Admitted: " + (", ".join(admitted) if admitted else "none") + ".")
    colluding = [o.perspective for o in outcomes if not o.admitted]
    if colluding:
        parts.append("Excluded (D<2 collusion): " + ", ".join(colluding) + ".")
    return " ".join(parts)


def convene(
    plan: "CountryPlan",
    *,
    reviewer_fn: ReviewerFn,
    perspectives: Sequence[Perspective] = DEFAULT_PERSPECTIVES,
    proposer: StateTuple = PROPOSER_STATE,
) -> CouncilVerdict:
    """Convene the adversarial council over ``plan`` and return its :class:`CouncilVerdict`.

    Each perspective is reviewed by ``reviewer_fn``; reviewers are admitted on D≥2 vs ``proposer``
    (collusion excluded); the confidence is the weakest-link MIN over admitted reviewers; and the
    decision is the most-severe admitted stance under the irreducible-escalate floor (Law I).
    """
    outcomes = tuple(_review_one(p, plan, reviewer_fn, proposer) for p in perspectives)

    admitted_names = tuple(o.perspective for o in outcomes if o.admitted)
    colluding_names = tuple(o.perspective for o in outcomes if not o.admitted)
    confidence = min((o.report.confidence for o in outcomes if o.admitted), default=0.0)
    decision = _aggregate_decision(outcomes)
    irreducible_escalated = tuple(p.name for p in perspectives if p.irreducible)
    rationale = _rationale(decision, confidence, outcomes, irreducible_escalated)

    return CouncilVerdict(
        decision=decision,
        confidence=confidence,
        outcomes=outcomes,
        admitted=admitted_names,
        colluding=colluding_names,
        irreducible_escalated=irreducible_escalated,
        rationale=rationale,
    )
