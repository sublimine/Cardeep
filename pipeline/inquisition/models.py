"""Core domain types for the V3 Inquisition engine (SU-B2 ε2).

Terminology
-----------
- StateTuple: the 4-dimensional identity of a source observation (§4).
- Lens:       the *method* used to produce a skeptic report.
- Skeptic:    one independent observer carrying a verdict on a claim.
- Regime:     EXACT (zero tolerance) or DRIFT (live-count tolerance).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


# ---------------------------------------------------------------------------
# Lens — the observational method used by a skeptic
# ---------------------------------------------------------------------------

Lens = Literal[
    "A_requery",
    "B_raw_recount",
    "C_live_refetch",
    "D_cross_source",
    "E_batch_hash",
]

# ---------------------------------------------------------------------------
# SkepticVerdict — per-skeptic outcome
# ---------------------------------------------------------------------------

SkepticVerdict = Literal["ASSERT", "REFUTE_SOFT", "REFUTE_HARD", "ABSTAIN"]


# ---------------------------------------------------------------------------
# Regime — tolerance model for a claim (§5.2)
# ---------------------------------------------------------------------------

class Regime(Enum):
    """Tolerance regime applied during quorum evaluation.

    EXACT: any deviation between measured and asserted is a refutation.
           Used for registral/official/cif/kind/coverage/denominator claims.

    DRIFT: live-count tolerance tol(v) = max(τ_rel·v, τ_abs).
           Used for count/inventory claims whose live values drift legitimately.
    """
    EXACT = "EXACT"
    DRIFT = "DRIFT"


# Regime per subject_type. MUST cover every subject_type the 0032 CHECK allows
# (count, entity_field, inventory, coverage, kind, delta, denominator) so the
# prosecutor never hits the unknown-type path for a valid claim.
#
# EXACT regime (any deviation is a refutation):
#   - 'kind'        → entity category tag, deterministic
#   - 'coverage'    → §5.6 example explicitly labels this EXACT
#   - 'denominator' → reference denominator for ratios; official, no drift expected
#   - 'entity_field'→ a field value (cif/phone/…) either matches source bytes or not (§5.2)
#   - 'delta'       → NEW/GONE/Δprice are discrete events; Lens E hash is byte-exact
#   - 'registral'/'official'/'cif' → forward-compat (not yet in the 0032 CHECK), zero tolerance
#
# DRIFT regime (tol(v) = max(τ_rel·v, τ_abs), legitimate live fluctuation):
#   - 'count'      → live platform inventory count; fluctuates by ±thousands per hour
#   - 'inventory'  → synonym for live stock count

_EXACT_TYPES: frozenset[str] = frozenset(
    {"registral", "official", "cif", "kind", "coverage", "denominator",
     "entity_field", "delta"}
)
_DRIFT_TYPES: frozenset[str] = frozenset({"count", "inventory"})


def regime_for(subject_type: str) -> Regime:
    """Return the tolerance regime for a given subject_type.

    Raises ValueError for unknown subject types so callers fail loud.
    """
    if subject_type in _EXACT_TYPES:
        return Regime.EXACT
    if subject_type in _DRIFT_TYPES:
        return Regime.DRIFT
    raise ValueError(
        f"Unknown subject_type {subject_type!r}. "
        f"Expected one of: {sorted(_EXACT_TYPES | _DRIFT_TYPES)}"
    )


# ---------------------------------------------------------------------------
# StateTuple — 4-dimensional source identity (§4)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StateTuple:
    """Immutable 4-tuple that identifies the provenance of one observation.

    Dimensions (§4):
        source: the data origin portal/DB (e.g. 'autoscout24', 'coches.net')
        tool:   the extraction tool (e.g. 'curl_cffi', 'sql', 'browser')
        cache:  the snapshot label (e.g. 'snap_T0', 'live_T1')
        path:   the access path/method (e.g. 'ingest', 'recount.sql', 'xsrc')
    """
    source: str
    tool: str
    cache: str
    path: str


def indep_distance(a: StateTuple, b: StateTuple) -> int:
    """Count the number of dimensions in which a and b differ.

    D(a, b) ∈ {0, 1, 2, 3, 4}  (§4 definition).
    A pair qualifies as independent for admission iff D(s, P) ≥ 2.
    """
    return sum([
        a.source != b.source,
        a.tool != b.tool,
        a.cache != b.cache,
        a.path != b.path,
    ])


# ---------------------------------------------------------------------------
# Skeptic — one observer with a verdict on a claim
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Skeptic:
    """An independent skeptic reporting a verdict on a claim.

    Fields
    ------
    lens:             the observational method employed (Lens).
    state:            the 4-dimensional provenance tuple (StateTuple).
    verdict:          the skeptic's outcome classification.
    measured_value:   the value the skeptic observed (str or None).
                      For ASSERT/REFUTE_SOFT this is a numeric string.
                      For REFUTE_HARD and ABSTAIN may be None.
    confidence:       optional confidence ∈ [0.0, 1.0].
    reason:           human-readable explanation (required for REFUTE_HARD).
    deterministic:    True when the hard refutation is byte-deterministic
                      (e.g. capped at a known platform ceiling like 1000 or 2000).
                      A single deterministic REFUTE_HARD vetoes without a second
                      witness (§5.5b).
    """
    lens: Lens
    state: StateTuple
    verdict: SkepticVerdict
    measured_value: str | None
    confidence: float | None
    reason: str | None
    deterministic: bool = False
