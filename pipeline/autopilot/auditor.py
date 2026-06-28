"""Fase D — the 5-level AUTO-AUDITOR: "someone who audits the pack who is NOT the owner".

``plans/country-autopilot/01-ARCHITECTURE.md`` (the N0..N4 table + the HONEST FRONTIER) +
``docs/generic-engine-bible/COUNTRY-PACK-CONTRACT.md`` §5 (the validation checklist = verifiable
predicates). The auditor runs five levels over a PROPOSED ``countries/<CC>/`` pack + its PLAN and
returns a pure :class:`PackAuditVerdict`. Persistence (``country_pack_audit_verdict``) is a LATER
increment — there is NO migration here; the auditor only computes a Verdict object.

The levels (each reuses already-built machinery — nothing is re-implemented):
  * **N0 Estructura** — deterministic linter of contract §5: the 8 pieces present & well-formed in
    ``countries/<CC>/`` (``country.toml`` valid via :meth:`CountryProfile.load_dir`, geo backbone
    non-empty, ≥1 recipe, census csv + ``SOURCE.md``, taxonomy, roster declared). PASS = APRUEBA,
    any structural fault = RECHAZA (fail-closed).
  * **N1 Ortogonalidad** — reuses ``lists.bucket_for`` / ``ORTHOGONAL_LISTS`` (the orthogonal-list
    taxonomy) and ``verify._path_family`` (family/origin signal). ≥3 distinct orthogonal buckets and
    no source falling to the ``MKT`` default → APRUEBA. A source the taxonomy cannot classify
    (``MKT`` default) is classification-uncertain → ESCALA. <3 orthogonal lists → RECHAZA.
  * **N2 Credibilidad** — ALWAYS ESCALA: legal/ToS and denominator-authority are structurally owner
    decisions (a wrong denominator silently biases the whole census). The adversarial council
    (``council.convene`` — D≥2 orthogonal perspectives, weakest-link) ENRICHES the escalation with
    its reasoning but never changes the doctrine (Law I — a council "approve" over a live country is
    invalid). N2 is the live-gate sentinel.
  * **N3 VAM-quórum** — reuses the Inquisition engine: ``quorum.decide`` (quorum ≥2) over the PLAN's
    numbers, with ``verify._path_family`` defining the orthogonal voices and ``router._lookup_route``
    mapping the verdict to a lane. It can only OVER-REFUTE — it never fabricates TRUSTWORTHY.
  * **N4 Cobertura proyectada** — reuses ``estimators.estimate_stratum`` (the MSE seal estimator) in
    projection mode over the roster's projected overlap. Not-identified / inconsistent-triangulation
    / projected coverage below the seal → ESCALA. It never fail-closes (under-coverage is an owner
    judgment, not a lie).

THE HONEST FRONTIER (the answer to the owner's vision). The auditor AUTO-APPROVES build + dry-run
ONLY. ``APRUEBA`` never authorises a live "go": legal/ToS, prod-cutover, spend, denominator-
authority and live-counts ALWAYS escalate. It is safe to delegate the REJECTION (fail-closed never
sells a lie, Law I); it is NOT safe to delegate the "go" over a live country. So the system
auto-develops + auto-audits everything up to the irreducible gates, and "start the real country"
stays structurally with the owner. The verdict makes this explicit on two axes: ``decision`` is the
BUILD recommendation (APRUEBA/RECHAZA/ESCALA over N0/N1/N3/N4); ``live_gate`` is N2 and is ALWAYS
ESCALA. Confidence = MIN (weakest link), the mirror of ``indep_score=min`` and ``coverage_lower``.
"""
from __future__ import annotations

import math
import warnings
from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping, Sequence

if TYPE_CHECKING:  # asyncpg is only needed for the optional persistence writer's type hint —
    import asyncpg  # the auditor's logic stays pure (no hard asyncpg dependency at import time).

from pipeline.autopilot.council import ReviewerFn, convene, default_reviewer
from pipeline.country_profile import CountryProfile
from pipeline.exhaustiveness.estimators import estimate_stratum
from pipeline.exhaustiveness.lists import ORTHOGONAL_LISTS, bucket_for
from pipeline.exhaustiveness.seal import DEFAULT_THRESHOLD as SEAL_THRESHOLD
from pipeline.inquisition.models import Regime, Skeptic, StateTuple, regime_for
from pipeline.inquisition.quorum import decide
from pipeline.inquisition.router import _lookup_route
from pipeline.verify import _path_family

# Relative gap above which a projected N̂ and an external census anchor are "inconsistent" (N4).
TRIANGULATION_TOL: float = 0.10


# ---------------------------------------------------------------------------
# Decision — the three outcomes of every level and of the overall verdict
# ---------------------------------------------------------------------------

class Decision(str, Enum):
    """The auditor's three outcomes (architecture §El AUDITOR).

    APRUEBA: auto-approved — but ONLY build + dry-run (never a live "go").
    RECHAZA: fail-closed rejection (Law I — a provably broken/refuted pack never ships).
    ESCALA:  PENDIENTE-OWNER — the auditor cannot safely decide; the owner must.
    """

    APRUEBA = "APRUEBA"
    RECHAZA = "RECHAZA"
    ESCALA = "ESCALA"


# Precedence for combining decisions: RECHAZA (fail-closed) dominates ESCALA dominates APRUEBA.
_RANK: dict[Decision, int] = {Decision.APRUEBA: 0, Decision.ESCALA: 1, Decision.RECHAZA: 2}
_SCORE_FOR: dict[Decision, float] = {Decision.APRUEBA: 1.0, Decision.ESCALA: 0.5, Decision.RECHAZA: 0.0}


# ---------------------------------------------------------------------------
# PLAN — the PROPOSED country (the auditor's pure input; NOT persisted)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PlanClaim:
    """One number the auditor re-prosecutes through the Inquisition quorum (N3).

    paths maps a path NAME (e.g. ``db_geo_count``, ``registral_census``) to its measured value as a
    string. ``verify._path_family`` collapses paths that share a collector family, so only genuinely
    orthogonal voices count toward the ≥2 quorum.
    """

    subject_key: str
    subject_type: str          # maps to a tolerance regime via ``regime_for`` (denominator→EXACT, count→DRIFT)
    asserted_value: str
    paths: Mapping[str, str]


@dataclass(frozen=True)
class CountryPlan:
    """The proposed pack's roster + numbers + projected overlap (autopilot ``PROPONER`` output)."""

    country_code: str
    orthogonal_lists: tuple[str, ...]                       # roster source_keys (N1 + N4 lists)
    geo_counts: tuple[PlanClaim, ...]                       # N3 geo-count claims
    denominator_anchor: PlanClaim | None                   # N3 denominator claim
    projected_overlap: Mapping[tuple[int, ...], int]       # N4 projected MSE capture matrix
    external_anchor: float | None = None                   # N4 triangulation cross-check (optional)


# ---------------------------------------------------------------------------
# Verdict DTOs (pure objects — mirror the future country_pack_audit_verdict)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LevelVerdict:
    """One level's sub-verdict."""

    level: str                 # 'N0'..'N4'
    name: str
    decision: Decision
    score: float               # [0,1] — this level's confidence (weakest-link input)
    reason_code: str | None
    detail: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PackAuditVerdict:
    """The auditor's output. ``decision`` is the BUILD recommendation; ``live_gate`` (= N2) is the
    always-on owner gate for going live. Read together: APRUEBA + live_gate=ESCALA means
    "build it and dry-run it; do NOT go live without me"."""

    country_code: str
    decision: Decision
    confidence: float
    reason_code: str | None
    levels: tuple[LevelVerdict, ...]
    live_gate: Decision

    def level(self, level: str) -> LevelVerdict:
        """Return the sub-verdict for ``level`` ('N0'..'N4')."""
        for lv in self.levels:
            if lv.level == level:
                return lv
        raise KeyError(f"no such level: {level!r}")


# ---------------------------------------------------------------------------
# N0 — Structure linter (deterministic, fail-closed)
# ---------------------------------------------------------------------------

def _reject_n0(reason_code: str, detail_msg: str) -> LevelVerdict:
    return LevelVerdict("N0", "Estructura", Decision.RECHAZA, 0.0, reason_code, {"fault": detail_msg})


def _nonempty_file(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def _audit_n0_structure(country_code: str, pack_dir: Path, plan: CountryPlan) -> LevelVerdict:
    """Lint the 8 physical pieces of the pack (contract §5). PASS = APRUEBA, any fault = RECHAZA."""
    pack = Path(pack_dir)

    # Piece 1+8 — country.toml valid + country_code coherent across manifest, request and plan.
    try:
        profile = CountryProfile.load_dir(pack)
    except FileNotFoundError as exc:
        return _reject_n0("MISSING_OR_INVALID_COUNTRY_TOML", str(exc))
    except ValueError as exc:
        return _reject_n0("INVALID_COUNTRY_TOML", str(exc))
    if profile.country_code != country_code:
        return _reject_n0(
            "COUNTRY_CODE_MISMATCH", f"manifest {profile.country_code!r} != requested {country_code!r}"
        )
    if plan.country_code != country_code:
        return _reject_n0(
            "COUNTRY_CODE_MISMATCH", f"plan {plan.country_code!r} != requested {country_code!r}"
        )

    # Piece 2 — geo backbone present & non-empty.
    backbone = pack / "geo" / "backbone.csv"
    if not _nonempty_file(backbone):
        return _reject_n0("MISSING_GEO_BACKBONE", str(backbone))

    # Piece 3 — ≥1 recipe committed under recipes/.
    recipes_dir = pack / "recipes"
    if not (recipes_dir.is_dir() and any(recipes_dir.rglob("*.yaml"))):
        return _reject_n0("MISSING_RECIPE", str(recipes_dir))

    # Piece 5 — census csv + SOURCE.md provenance + taxonomy.
    census_dir = pack / "census"
    if not (census_dir.is_dir() and any(census_dir.glob("*.csv"))):
        return _reject_n0("MISSING_CENSUS_CSV", str(census_dir))
    if not (census_dir / "SOURCE.md").is_file():
        return _reject_n0("MISSING_CENSUS_SOURCE_MD", str(census_dir / "SOURCE.md"))
    if not (pack / "taxonomy.yaml").is_file():
        return _reject_n0("MISSING_TAXONOMY", str(pack / "taxonomy.yaml"))

    # Roster declared (presence only — the ≥3 orthogonality QUALITY gate is N1's job).
    if not plan.orthogonal_lists:
        return _reject_n0("MISSING_ROSTER", "plan.orthogonal_lists is empty")

    return LevelVerdict(
        "N0", "Estructura", Decision.APRUEBA, 1.0, None,
        {
            "country_code": profile.country_code,
            "subdivision_regex": profile.subdivision_regex,
            "geo_backbone": str(backbone),
            "n_lists_declared": len(plan.orthogonal_lists),
        },
    )


# ---------------------------------------------------------------------------
# N1 — Orthogonality (deterministic + agent hook)
# ---------------------------------------------------------------------------

def _audit_n1_orthogonality(plan: CountryPlan) -> LevelVerdict:
    """≥3 distinct orthogonal buckets, all cleanly classified → APRUEBA; an unclassifiable source
    (MKT default) → ESCALA; <3 orthogonal lists → RECHAZA (the MSE cannot triangulate)."""
    roster = plan.orthogonal_lists
    buckets = {src: bucket_for(src) for src in roster}
    uncertain = tuple(src for src in roster if buckets[src] == "MKT")
    distinct_orthogonal = sorted({b for b in buckets.values() if b in ORTHOGONAL_LISTS})
    families = sorted({_path_family(src) for src in roster})
    origins = sorted(set(roster))
    detail: dict[str, Any] = {
        "buckets": buckets,
        "distinct_orthogonal": distinct_orthogonal,
        "families": families,        # verify._path_family signal (≥2 families / ≥2 origins)
        "origins": origins,
        "uncertain": uncertain,
    }

    if uncertain:
        # Classification incierta of a new source → an agent must classify it (stub: escalate).
        return LevelVerdict(
            "N1", "Ortogonalidad", Decision.ESCALA, 0.5, "UNCERTAIN_SOURCE_CLASSIFICATION", detail
        )
    if len(distinct_orthogonal) < 3:
        return LevelVerdict(
            "N1", "Ortogonalidad", Decision.RECHAZA, 0.0, "INSUFFICIENT_ORTHOGONAL_LISTS", detail
        )
    return LevelVerdict("N1", "Ortogonalidad", Decision.APRUEBA, 1.0, None, detail)


# ---------------------------------------------------------------------------
# N2 — Credibility (ALWAYS escalates — the live-gate sentinel)
# ---------------------------------------------------------------------------

def _audit_n2_credibility(plan: CountryPlan, *, reviewer_fn: ReviewerFn | None = None) -> LevelVerdict:
    """SIEMPRE ESCALA — the live-gate sentinel. Legal/ToS and denominator-authority are irreducible
    owner decisions. The adversarial council (``council.convene``) ENRICHES this escalation with the
    D≥2 perspective reasoning, but it NEVER changes the doctrine: a council "approve" over a live
    country is structurally invalid (Law I), so the level decision is pinned to ESCALA and surfaces
    the council's full finding — including any fail-closed REJECT — to the owner rather than
    auto-resolving the live gate.

    The score is 1.0: the level is fully CERTAIN it must escalate (the escalation is correct), so it
    never spuriously drags the weakest-link confidence — a doctrine decision, not a build-quality
    signal. The council's own weakest-link confidence lives in the detail. ``reviewer_fn`` is the
    injection point for the real LLM-runtime reviewer (default: the €0 no-network ``default_reviewer``)."""
    council = convene(plan, reviewer_fn=reviewer_fn or default_reviewer)
    return LevelVerdict(
        "N2", "Credibilidad", Decision.ESCALA, 1.0, "OWNER_LEGAL_AND_DENOMINATOR_AUTHORITY",
        {
            "council": council.as_detail(),
            "owner_gates": ("LEGAL_TOS", "DENOMINATOR_AUTHORITY", "SPEND", "PROD_CUTOVER", "LIVE_COUNTS"),
        },
    )


# ---------------------------------------------------------------------------
# N3 — VAM quorum (reuses the Inquisition engine over the PLAN numbers)
# ---------------------------------------------------------------------------

# Producer of the PLAN's numbers — the subject under prosecution (the pack's own assertion).
def _plan_producer(subject_key: str) -> StateTuple:
    return StateTuple(source="pack_plan", tool="pack", cache="plan", path=subject_key)


def _family_representatives(paths: Mapping[str, str]) -> dict[str, str]:
    """Collapse paths to one representative value per collector family (verify._path_family).

    Same-family paths share a capture mechanism, so they are a single orthogonal voice (Law I:
    unproven independence must not grant a quorum). Intra-family disagreement collapses to the modal.
    """
    by_family: dict[str, list[str]] = {}
    for name, value in paths.items():
        by_family.setdefault(_path_family(name), []).append(str(value))
    return {fam: Counter(vals).most_common(1)[0][0] for fam, vals in by_family.items()}


def _lane_to_decision(verdict: str, reason_code: str | None) -> Decision:
    """Map an Inquisition verdict to a build decision via the sealed router table (router.py §7).

    TRUSTWORTHY → APRUEBA (quorum-certified). ESCALATE_OWNER (NO_INDEPENDENT_PATH, INCONCLUSIVE) →
    ESCALA (the €0 frontier: a live count without an independent 2nd path is the owner's, not a
    refutation). Everything else REFUTED-with-evidence (RESEARCH/QUARANTINE/AUTO_FIX) → RECHAZA
    (fail-closed: never auto-build on a contradicted number).
    """
    if verdict == "TRUSTWORTHY":
        return Decision.APRUEBA
    if _lookup_route(verdict, reason_code).lane == "ESCALATE_OWNER":
        return Decision.ESCALA
    return Decision.RECHAZA


def _prosecute_number(claim: PlanClaim) -> tuple[Decision, float, str, str]:
    """Re-prosecute one PLAN number through ``decide`` (quorum ≥2). Returns (decision, score,
    reason, raw_verdict). Only over-refutes — TRUSTWORTHY arises solely from a genuine quorum."""
    reps = _family_representatives(claim.paths)
    skeptics: list[Skeptic] = [
        Skeptic(
            lens="A_requery",
            state=StateTuple(source=family, tool="vam_path", cache="plan", path=family),
            verdict="ASSERT",
            measured_value=value,
            confidence=None,
            reason=None,
        )
        for family, value in reps.items()
    ]
    try:
        regime = regime_for(claim.subject_type)
    except ValueError:
        regime = Regime.EXACT  # unknown subject_type → safest (over-refutes), mirrors prosecutor.py

    result = decide(
        skeptics, _plan_producer(claim.subject_key),
        asserted_value=claim.asserted_value, regime=regime,
    )
    decision = _lane_to_decision(result.verdict, result.reason_code)
    if decision is Decision.APRUEBA:
        score = min(1.0, result.indep_score / 2.0)  # mirror of indep_score
    else:
        score = _SCORE_FOR[decision]
    reason = f"{result.reason_code or result.verdict}:{claim.subject_key}"
    return decision, score, reason, result.verdict


def _audit_n3_vam_quorum(plan: CountryPlan) -> LevelVerdict:
    claims: list[PlanClaim] = list(plan.geo_counts)
    if plan.denominator_anchor is not None:
        claims.append(plan.denominator_anchor)
    if not claims:
        return LevelVerdict(
            "N3", "VAM-quórum", Decision.ESCALA, 0.5, "NO_NUMBERS_TO_PROSECUTE", {"claims": 0}
        )

    rows = [(_prosecute_number(c), c.subject_key) for c in claims]
    decisions = [r[0][0] for r in rows]
    overall = max(decisions, key=lambda d: _RANK[d])
    score = min(r[0][1] for r in rows)
    reason = next((r[0][2] for r in rows if r[0][0] is not Decision.APRUEBA), None)
    detail = {
        "claims": [
            {"subject": key, "decision": dec.value, "verdict": raw, "reason": rc}
            for ((dec, _sc, rc, raw), key) in rows
        ]
    }
    return LevelVerdict("N3", "VAM-quórum", overall, score, reason, detail)


# ---------------------------------------------------------------------------
# N4 — Projected coverage (reuses the MSE seal estimator in projection mode)
# ---------------------------------------------------------------------------

def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x)) if math.isfinite(x) else 0.0


def _audit_n4_projected_coverage(plan: CountryPlan) -> LevelVerdict:
    """Project the roster's overlap through ``estimate_stratum`` (the seal estimator). Not-identified
    / inconsistent-triangulation / coverage below the seal → ESCALA. Never fail-closes (RECHAZA)."""
    overlap = plan.projected_overlap
    if not overlap:
        return LevelVerdict("N4", "Cobertura proyectada", Decision.ESCALA, 0.0, "NO_PROJECTION", {})

    with warnings.catch_warnings():
        # estimate_stratum's log-linear fit warns on near-perfect projected overlap; expected here.
        warnings.simplefilter("ignore")
        est = estimate_stratum(dict(overlap))

    cov = _clamp01(est.coverage_lower)
    detail: dict[str, Any] = {
        "identified": est.identified,
        "k_lists": est.k_lists,
        "n_obs": est.n_obs,
        "n_hat": round(est.n_hat, 1),
        "coverage_lower": round(cov, 4),
        "seal_threshold": SEAL_THRESHOLD,
        "method": est.method,
    }

    if not est.identified:
        return LevelVerdict("N4", "Cobertura proyectada", Decision.ESCALA, 0.0, "MSE_NOT_IDENTIFIED", detail)

    if plan.external_anchor is not None:
        anchor = plan.external_anchor
        rel = abs(est.n_hat - anchor) / anchor if anchor else float("inf")
        detail["external_anchor"] = anchor
        detail["triangulation_rel_gap"] = round(rel, 4)
        if rel > TRIANGULATION_TOL:
            return LevelVerdict(
                "N4", "Cobertura proyectada", Decision.ESCALA, cov, "INCONSISTENT_TRIANGULATION", detail
            )

    if cov < SEAL_THRESHOLD:
        return LevelVerdict(
            "N4", "Cobertura proyectada", Decision.ESCALA, cov, "PROJECTED_COVERAGE_BELOW_SEAL", detail
        )
    return LevelVerdict("N4", "Cobertura proyectada", Decision.APRUEBA, cov, None, detail)


# ---------------------------------------------------------------------------
# Combine + public entry point
# ---------------------------------------------------------------------------

def _combine_build(build_levels: Sequence[LevelVerdict]) -> tuple[Decision, str | None]:
    """Fold the BUILD levels (N0/N1/N3/N4) with RECHAZA > ESCALA > APRUEBA. N2 is excluded — it is
    the always-on live gate, not a build blocker (the gates park, they do not stop)."""
    for lv in build_levels:
        if lv.decision is Decision.RECHAZA:
            return Decision.RECHAZA, lv.reason_code
    for lv in build_levels:
        if lv.decision is Decision.ESCALA:
            return Decision.ESCALA, lv.reason_code
    return Decision.APRUEBA, None


def audit_pack(country_code: str, pack_dir: Path | str, plan: CountryPlan) -> PackAuditVerdict:
    """Audit a proposed country pack across the 5 levels and return a :class:`PackAuditVerdict`.

    Parameters
    ----------
    country_code : ISO-3166 alpha-2 of the country under audit (must match the manifest and plan).
    pack_dir     : path to the proposed ``countries/<CC>/`` tree (may be a staged / temp dir).
    plan         : the PROPOSED :class:`CountryPlan` (roster + numbers + projected overlap).

    The returned verdict's ``decision`` is the BUILD recommendation (build + dry-run only on
    APRUEBA); ``live_gate`` is N2 and is ALWAYS ESCALA. ``confidence`` is the weakest-link MIN over
    all five levels. Nothing is persisted (no migration — a later increment owns that).
    """
    pack = Path(pack_dir)
    n0 = _audit_n0_structure(country_code, pack, plan)
    n1 = _audit_n1_orthogonality(plan)
    n2 = _audit_n2_credibility(plan)
    n3 = _audit_n3_vam_quorum(plan)
    n4 = _audit_n4_projected_coverage(plan)
    levels = (n0, n1, n2, n3, n4)

    decision, reason = _combine_build((n0, n1, n3, n4))
    confidence = min(lv.score for lv in levels)  # weakest link, including N2 (which scores 1.0)

    return PackAuditVerdict(
        country_code=country_code,
        decision=decision,
        confidence=confidence,
        reason_code=reason,
        levels=levels,
        live_gate=n2.decision,
    )


# ---------------------------------------------------------------------------
# Persistence (Fase D increment) — the append-only country_pack_audit_verdict
# ledger (migration 0069). OPTIONAL by design: audit_pack stays a PURE function;
# the caller decides whether to persist. This writer NEVER mutates the verdict and
# NEVER changes a ruling — it only appends the computed sub-verdicts to the ledger.
# ---------------------------------------------------------------------------

_PERSIST_VERDICT_SQL = """
    INSERT INTO country_pack_audit_verdict
        (country_code, level, sub_verdict, score, reason_code, decision)
    VALUES ($1, $2, $3, $4, $5, $6)
"""

# Sentinel level name for the pack-level summary row (the per-level rows use 'N0'..'N4').
_OVERALL_LEVEL = "OVERALL"


def _normalize_cc(country_code: str) -> str:
    """ISO alpha-2, stripped + upper-cased (CHAR(2) in the schema). Mirrors state._normalize_cc;
    inlined to keep the auditor self-contained (state.py is owned by another increment)."""
    cc = (country_code or "").strip().upper()
    if len(cc) != 2:
        raise ValueError(f"country_code must be 2 chars (ISO), got {country_code!r}")
    return cc


async def persist_verdict(
    conn: asyncpg.Connection,
    country_code: str,
    verdict: PackAuditVerdict,
) -> int:
    """Append the auditor's sub-verdicts (one row per level N0..N4) + one OVERALL summary row to the
    ``country_pack_audit_verdict`` ledger (migration 0069), and return the number of rows written
    (== ``len(verdict.levels) + 1``).

    This is the OPTIONAL persistence half of Fase D and a PURE SIDE-EFFECT: it does NOT mutate the
    verdict and does NOT touch :func:`audit_pack`'s logic — the caller decides whether to persist.

    Append-only (the history IS the proof, mirroring ``country_campaign_transition`` and
    ``inquisition_verdict``): every call INSERTs a fresh batch, so re-auditing the same country ADDS
    rows and never overwrites. The caller owns the asyncpg transaction boundary (exactly like
    ``state.register`` / ``state.transition``), so a dry-run can roll the whole batch back.

    Column mapping (see migration 0069 header): each level row carries its own ``sub_verdict`` /
    ``score`` / ``reason_code``; the OVERALL row carries the pack ``decision`` / ``confidence`` /
    ``reason_code``; and the pack's overall ``decision`` is denormalised onto EVERY row of the run.
    ``score`` is bound as :class:`~decimal.Decimal` because asyncpg requires it for a NUMERIC column.
    """
    cc = _normalize_cc(country_code)
    overall_decision = verdict.decision.value

    written = 0
    for lv in verdict.levels:
        await conn.execute(
            _PERSIST_VERDICT_SQL,
            cc, lv.level, lv.decision.value, Decimal(str(lv.score)), lv.reason_code, overall_decision,
        )
        written += 1

    await conn.execute(
        _PERSIST_VERDICT_SQL,
        cc, _OVERALL_LEVEL, overall_decision, Decimal(str(verdict.confidence)),
        verdict.reason_code, overall_decision,
    )
    written += 1
    return written
