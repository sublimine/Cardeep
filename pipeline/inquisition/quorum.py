"""Quorum decision engine for the V3 Inquisition (§5.2–§5.6).

Key design decisions
--------------------
1. `within_tolerance` is a PURE UTILITY function exposed for lenses and tests.
   It does NOT re-evaluate tolerances inside `decide()`.  `decide()` trusts
   the pre-classified `skeptic.verdict` field because the lens that produced
   the skeptic already knew the regime when it ran.  This avoids a
   double-evaluation inconsistency if the lens used richer context.

2. The `asserted` parameter in `within_tolerance` is the claim's asserted value
   (the "v" in tol(v) = max(τ_rel·v, τ_abs)), matching the spec examples
   (§5.2: tol = max(0.005 × 278329, 50) = 1391).

3. §5.5 false-veto guard is applied BEFORE §5.4 step 1, but the result of step 1
   uses only *credible* hard refutations as Rh.  The raw count of admitted hard
   refuters (regardless of credibility) is still reported in `refute_hard_n`.

4. `indep_score` is always computed over admitted ASSERT skeptics; if Rule 1
   fires before we reach Rule 2, we still populate `indep_score` in the result.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from pipeline.inquisition.independence import admit, indep_score as _indep_score
from pipeline.inquisition.models import Regime, Skeptic, StateTuple, indep_distance

# ---------------------------------------------------------------------------
# Tolerance constants (§5.2)
# ---------------------------------------------------------------------------

TAU_REL: float = 0.005   # relative tolerance coefficient
TAU_ABS: float = 50.0    # absolute tolerance floor (units = vehicles)


# ---------------------------------------------------------------------------
# Tolerance function (§5.2)
# ---------------------------------------------------------------------------

def within_tolerance(
    measured: float,
    asserted: float,
    regime: Regime,
    *,
    tau_rel: float = TAU_REL,
    tau_abs: float = TAU_ABS,
) -> bool:
    """Return True iff *measured* is within tolerance of *asserted* under *regime*.

    EXACT regime: requires measured == asserted exactly (zero tolerance).
    DRIFT regime: requires |measured - asserted| ≤ max(tau_rel × asserted, tau_abs).

    Parameters
    ----------
    measured:  the value the skeptic observed.
    asserted:  the claim's asserted value (reference; defines the tolerance band).
    regime:    EXACT or DRIFT.
    tau_rel:   relative coefficient (default TAU_REL = 0.005).
    tau_abs:   absolute floor    (default TAU_ABS = 50.0).
    """
    if regime is Regime.EXACT:
        return measured == asserted
    # DRIFT
    tolerance = max(tau_rel * asserted, tau_abs)
    return abs(measured - asserted) <= tolerance


# ---------------------------------------------------------------------------
# QuorumResult — output DTO (matches inquisition_verdict columns)
# ---------------------------------------------------------------------------

@dataclass
class QuorumResult:
    """Result of the §5.4 quorum decision function.

    Field names mirror the inquisition_verdict table columns exactly.
    Not frozen so tests can construct and mutate freely.
    """
    verdict: str                  # 'TRUSTWORTHY' | 'REFUTED' | 'INCONCLUSIVE'
    decided_value: str | None     # v* if TRUSTWORTHY, else None
    indep_score: int              # INDEP metric (0 when < 2 asserting skeptics)
    assert_n: int                 # count of admitted ASSERT skeptics
    refute_soft_n: int            # count of admitted REFUTE_SOFT skeptics
    refute_hard_n: int            # count of admitted REFUTE_HARD skeptics (all, not just credible)
    abstain_n: int                # count of admitted ABSTAIN skeptics
    reason_code: str | None       # machine-readable reason; None for TRUSTWORTHY


# ---------------------------------------------------------------------------
# False-veto guard (§5.5)
# ---------------------------------------------------------------------------

def _credible_hard_refuters(
    hard_skeptics: list[Skeptic],
) -> list[Skeptic]:
    """Apply the §5.5 false-veto guard and return credible hard refuters.

    Rules:
      a) Any deterministic REFUTE_HARD (cap/checksum) is credible on its own.
      b) A lone non-deterministic REFUTE_HARD is NOT credible (demoted).
      c) Two or more non-deterministic REFUTE_HARD with D(s_i, s_j) ≥ 2
         between at least one pair are all credible.

    The guard protects against a single rogue lens triggering a hard veto
    when its finding has not been independently reproduced.
    """
    if not hard_skeptics:
        return []

    # Rule a: any deterministic hard refuter is immediately credible
    deterministic = [s for s in hard_skeptics if s.deterministic]
    if deterministic:
        return hard_skeptics  # all hard refuters become credible

    # Rule b/c: non-deterministic only
    non_det = hard_skeptics  # all non-deterministic at this point
    if len(non_det) < 2:
        return []  # lone non-deterministic → demote → not credible

    # Check if at least one pair has D ≥ 2
    for i, s_i in enumerate(non_det):
        for j in range(i + 1, len(non_det)):
            if indep_distance(s_i.state, non_det[j].state) >= 2:
                return non_det  # two independent hard refuters → credible

    # Multiple hard refuters but all correlated (D < 2 for every pair) → not credible
    return []


# ---------------------------------------------------------------------------
# Core quorum decision function (§5.4)
# ---------------------------------------------------------------------------

def decide(
    skeptics: list[Skeptic],
    producer: StateTuple,
    *,
    asserted_value: str,
    regime: Regime,
) -> QuorumResult:
    """Apply the §5.4 six-step quorum decision to a list of skeptics.

    Parameters
    ----------
    skeptics:       all skeptics (admitted and non-admitted).
    producer:       the StateTuple of the claim's producer.
    asserted_value: the claim value being verified.
    regime:         EXACT or DRIFT (controls tolerance in within_tolerance).

    Returns
    -------
    QuorumResult with verdict, decided_value, counts, indep_score, reason_code.
    """
    # ------------------------------------------------------------------
    # Step 0: partition skeptics into admitted vs. excluded
    # ------------------------------------------------------------------
    admitted = [s for s in skeptics if admit(s, producer)]

    assert_admitted:      list[Skeptic] = []
    soft_admitted:        list[Skeptic] = []
    hard_admitted:        list[Skeptic] = []
    abstain_admitted:     list[Skeptic] = []

    for s in admitted:
        if s.verdict == "ASSERT":
            assert_admitted.append(s)
        elif s.verdict == "REFUTE_SOFT":
            soft_admitted.append(s)
        elif s.verdict == "REFUTE_HARD":
            hard_admitted.append(s)
        elif s.verdict == "ABSTAIN":
            abstain_admitted.append(s)

    # Counts for reporting
    assert_n       = len(assert_admitted)
    refute_soft_n  = len(soft_admitted)
    refute_hard_n  = len(hard_admitted)   # raw count (all admitted hard refuters)
    abstain_n      = len(abstain_admitted)

    # ------------------------------------------------------------------
    # Compute INDEP over asserting skeptics (always; used in Rules 2 and report)
    # ------------------------------------------------------------------
    indep = _indep_score(assert_admitted, producer)

    # ------------------------------------------------------------------
    # §5.5 False-veto guard: determine *credible* hard refuters
    # ------------------------------------------------------------------
    credible_hard = _credible_hard_refuters(hard_admitted)
    rh = len(credible_hard)

    # ------------------------------------------------------------------
    # §5.4 Step 1: hard veto
    # ------------------------------------------------------------------
    if rh >= 1:
        reason = credible_hard[0].reason or "HARD_REFUTE"
        return QuorumResult(
            verdict="REFUTED",
            decided_value=None,
            indep_score=indep,
            assert_n=assert_n,
            refute_soft_n=refute_soft_n,
            refute_hard_n=refute_hard_n,
            abstain_n=abstain_n,
            reason_code=reason,
        )

    # ------------------------------------------------------------------
    # §5.4 Step 2: independence gate
    # ------------------------------------------------------------------
    if indep < 2:
        return QuorumResult(
            verdict="REFUTED",
            decided_value=None,
            indep_score=indep,
            assert_n=assert_n,
            refute_soft_n=refute_soft_n,
            refute_hard_n=refute_hard_n,
            abstain_n=abstain_n,
            reason_code="NO_INDEPENDENT_PATH",
        )

    # ------------------------------------------------------------------
    # §5.4 Step 3: modal ASSERT value
    # ------------------------------------------------------------------
    # A = multiset of measured_values from all admitted ASSERT skeptics
    A: list[str] = [
        s.measured_value for s in assert_admitted if s.measured_value is not None
    ]
    # Edge-case: no values (should not happen if assert_n > 0, but guard it)
    if not A:
        # Treat as INCONCLUSIVE — cannot compute modal value
        return QuorumResult(
            verdict="INCONCLUSIVE",
            decided_value=None,
            indep_score=indep,
            assert_n=assert_n,
            refute_soft_n=refute_soft_n,
            refute_hard_n=refute_hard_n,
            abstain_n=abstain_n,
            reason_code="SINGLE_ASSERT",
        )

    counts = Counter(A)
    v_star, n_star = counts.most_common(1)[0]

    # Rival: another value (≠ v*) that also has ≥ 2 supporters
    rival = any(v != v_star and cnt >= 2 for v, cnt in counts.items())

    rs = refute_soft_n
    ab = abstain_n

    # ------------------------------------------------------------------
    # §5.4 Step 4: TRUSTWORTHY condition
    # ------------------------------------------------------------------
    if n_star >= 2 and not rival and (rs + ab) < n_star:
        return QuorumResult(
            verdict="TRUSTWORTHY",
            decided_value=v_star,
            indep_score=indep,
            assert_n=assert_n,
            refute_soft_n=refute_soft_n,
            refute_hard_n=refute_hard_n,
            abstain_n=abstain_n,
            reason_code=None,
        )

    # ------------------------------------------------------------------
    # §5.4 Step 5: REFUTED (majority-refute or split quorum)
    # ------------------------------------------------------------------
    if rival or (rs + ab) >= n_star:
        reason_code = "SPLIT_QUORUM" if rival else "MAJORITY_REFUTE"
        return QuorumResult(
            verdict="REFUTED",
            decided_value=None,
            indep_score=indep,
            assert_n=assert_n,
            refute_soft_n=refute_soft_n,
            refute_hard_n=refute_hard_n,
            abstain_n=abstain_n,
            reason_code=reason_code,
        )

    # ------------------------------------------------------------------
    # §5.4 Step 6: INCONCLUSIVE (re-queue)
    # ------------------------------------------------------------------
    return QuorumResult(
        verdict="INCONCLUSIVE",
        decided_value=None,
        indep_score=indep,
        assert_n=assert_n,
        refute_soft_n=refute_soft_n,
        refute_hard_n=refute_hard_n,
        abstain_n=abstain_n,
        reason_code="SINGLE_ASSERT",
    )
