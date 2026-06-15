"""Independence gating for the V3 Inquisition engine (§4).

Two functions:
  admit()      — decides whether a single skeptic is independent of the producer.
  indep_score()— computes the weakest-link INDEP metric over all asserting skeptics.
"""
from __future__ import annotations

from pipeline.inquisition.models import Skeptic, StateTuple, indep_distance


def admit(skeptic: Skeptic, producer: StateTuple) -> bool:
    """Return True iff the skeptic is sufficiently independent of the producer.

    Admission condition (§4): D(skeptic.state, producer) ≥ 2.
    A skeptic that differs in fewer than 2 dimensions adds no independent signal
    and must be excluded from quorum counting.
    """
    return indep_distance(skeptic.state, producer) >= 2


def indep_score(asserting_skeptics: list[Skeptic], producer: StateTuple) -> int:
    """Compute the weakest-link independence score over all ASSERT-verdict skeptics.

    Definition (§4):
        INDEP = min over all pairs (s_i, s_j) of D(s_i, s_j)
        where s_i and s_j are skeptics that have issued an ASSERT verdict
        *and* are admitted (D(s, P) ≥ 2).

    Special case: if fewer than 2 asserting skeptics are present, return 0.
    Rationale: a single asserting skeptic has no pair to evaluate; INDEP is
    undefined in the spec and Rule 2 of §5.4 requires INDEP ≥ 2 — returning 0
    ensures Rule 2 fires and the claim is REFUTED(NO_INDEPENDENT_PATH).

    DIRECTOR DECISION (resolves a §4 internal inconsistency — keep, do NOT relax):
    §4's formula says "min over all asserting pairs" while its inline comment says
    "the agreeing set" (the v*-supporting subset). These disagree only when asserts
    SPLIT across values. We compute over ALL asserting skeptics (the stricter
    reading): the agreeing-set reading is a SUPERSET filter, so its INDEP is always
    ≥ this one — meaning the agreeing-set reading can turn a REFUTED into a
    TRUSTWORTHY (a non-agreeing near-clone stops dragging INDEP down). That is the
    one direction the Inquisition must never drift (Law I: default-REFUTED, "better
    to confess a gap than sell a lie"). When the spec is ambiguous, the safe reading
    wins: this can only ever over-refute, never manufacture a false TRUSTWORTHY.
    All spec worked examples (§4, §5.6) have unanimous asserts, so both readings
    agree there; the divergence is purely in the split-assert edge, resolved safe.

    Parameters
    ----------
    asserting_skeptics:
        List of skeptics that have already been confirmed as admitted AND
        that carry verdict == 'ASSERT'.  The caller is responsible for
        pre-filtering by admission status.
    producer:
        The StateTuple of the claim's producer (used only for context;
        pair-distance is measured between skeptics, not vs. producer).
    """
    if len(asserting_skeptics) < 2:
        return 0

    min_dist = 4  # maximum possible distance
    for i, s_i in enumerate(asserting_skeptics):
        for j in range(i + 1, len(asserting_skeptics)):
            s_j = asserting_skeptics[j]
            dist = indep_distance(s_i.state, s_j.state)
            if dist < min_dist:
                min_dist = dist

    return min_dist
