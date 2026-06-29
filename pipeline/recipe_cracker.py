"""Recipe CRACKER — the autonomous try-all orchestrator (§02 country-autopilot, the missing core).

The harness (:mod:`pipeline.recipe_harness`) drives ONE extractor through the recipe-first
sample-verify-delete cycle. The cracker is the layer ABOVE it: for a single target (dealer /
platform) it walks the cost LADDER cheap->expensive, trying each rung until one VERIFIES, then
persists the winning recipe with the winning rung recorded — so the next run can warm-start there
(§9.4 ranking feedback). It is the piece the master plan calls the absent núcleo: today nothing
tries *all* the scraping alternatives for a target and keeps the one that works.

Built strictly ON the existing spine — it does NOT reinvent or touch it:
  * VERIFIED/FAILED is :func:`pipeline.recipe_harness.decide_status` verbatim (zero parse-loss ∧
    cars>=target ∧ VAM not-REFUTED);
  * the VAM quorum is :func:`pipeline.verify.record_count_verdict` (DB seal) or
    :meth:`RecipeHarness._offline_verdict` (DB-less mirror) — same paths, same shapes;
  * persistence is :func:`pipeline.recipe.write_recipe` (committed YAML);
  * sample-verify-DELETE is honoured per rung: each rung's crude is dropped before the next.

No silent failure: if no rung cracks, the result carries the per-rung reason (what each tried and
why it failed). ``fetch_fn`` is INJECTABLE so the pure suite drives fixtures and the real,
EGRESS-gated fetch stays out of the cracker. A new tool joins the ladder by registering an
``Extractor`` in :data:`RUNG_REGISTRY` — the orchestrator is never edited for it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Protocol

import asyncpg

from pipeline.recipe_harness import (
    RecipeHarness,
    Sample,
    decide_status,
    sample_paths,
)
from pipeline.recipe_schema import (
    STATUS_FAILED,
    STATUS_VERIFIED,
    Evidence,
    Recipe,
)
from pipeline.verify import record_count_verdict

# A rung's transport is whatever ``fetch_fn`` it is handed; the cracker stays agnostic to its
# signature (a rung knows how to call its own transport). Injectable -> fixtures in tests, the
# real egress-gated fetch in runtime.
FetchFn = Callable[..., Any]


# ---------------------------------------------------------------------------
# Rung protocol — one step of the ladder. A superset of the harness Extractor:
# ``cost`` orders the ladder and ``extract`` threads the injectable transport.
# ---------------------------------------------------------------------------
class Rung(Protocol):
    """A ladder step the cracker drives. ``cost`` is the §02 ladder position (cheap->expensive);
    ``recipe_template`` returns a DRAFT recipe; ``extract`` pulls a bounded :class:`Sample` using
    the injected ``fetch_fn``."""

    source: str
    cost: int

    def recipe_template(self, target: str) -> Recipe: ...

    def extract(self, target: str, fetch_fn: FetchFn) -> Sample: ...


# ---------------------------------------------------------------------------
# Result types — every rung attempt is recorded (the per-rung verdict trail).
# ---------------------------------------------------------------------------
@dataclass
class RungAttempt:
    """One rung's outcome: what it produced and the VERIFIED/FAILED verdict + reason."""
    rung: int          # index within the cost-sorted ladder (the ladder position)
    source: str
    status: str        # STATUS_VERIFIED | STATUS_FAILED
    reason: str
    declared: int | None
    fetched: int
    parsed: int
    verdict: str       # the VAM verdict string driving the decision


@dataclass
class CrackResult:
    """The outcome of cracking one target across the whole ladder.

    On success: ``status == VERIFIED``, ``winning_rung`` is the cost-sorted ladder index that
    cracked it, and ``recipe_path`` points at the persisted asset (which carries ``winning_rung``).
    On failure: ``status == FAILED`` and ``reason`` enumerates the per-rung failure (never silent).
    ``warm_started`` records whether §9.4 ranking feedback reordered the ladder for this run.
    """
    target: str
    status: str
    winning_rung: int | None
    winning_source: str | None
    reason: str
    recipe_path: str | None
    attempts: list[RungAttempt] = field(default_factory=list)
    warm_started: bool = False


# ---------------------------------------------------------------------------
# Extensible rung registry — add a tool == register an Extractor (no orchestrator edit).
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class RungSpec:
    """A registered rung: a zero-arg factory plus its ladder cost."""
    factory: Callable[[], Rung]
    cost: int


RUNG_REGISTRY: dict[str, RungSpec] = {}


def register_rung(name: str, factory: Callable[[], Rung], *, cost: int) -> None:
    """Register a rung under ``name`` at ladder position ``cost``. Whatever is registered is
    automatically assembled into :func:`default_ladder` / :func:`build_ladder` — the investigation
    or integration of a new tool (css, llm_local, ...) is a one-line registration, nothing else."""
    RUNG_REGISTRY[name] = RungSpec(factory=factory, cost=cost)


def build_ladder(extra_pairs: Iterable[tuple[int, Rung]] = ()) -> list[Rung]:
    """Assemble a ladder from :data:`RUNG_REGISTRY` (plus optional ``(cost, rung)`` extras),
    sorted cheap->expensive. Pure over the registry: callable in tests without any heavy import."""
    pairs: list[tuple[int, Rung]] = [(spec.cost, spec.factory()) for spec in RUNG_REGISTRY.values()]
    pairs.extend(extra_pairs)
    pairs.sort(key=lambda t: t[0])
    return [rung for _, rung in pairs]


# Existing extractors mapped onto the §02 ladder by transport+parse cost (rungs 0-3). Pure data;
# the heavy modules themselves are imported lazily in :func:`_legacy_pairs`.
_LEGACY_COST = {
    "coches_net": 0,    # json_api internal gateway — cheapest
    "autoscout24": 1,   # curl_cffi + __NEXT_DATA__ SSR
    "coches_com": 1,    # curl_cffi + __NEXT_DATA__ SSR
    "web_generic": 2,   # generic structured / jsonld web
    "autocasion": 3,    # SSR enumerate + GraphQL hydrate (dealerprobe slot)
}
_DEFAULT_LEGACY_COST = 3


@dataclass
class LegacyRung:
    """Adapts a pre-existing :class:`pipeline.recipe_harness.Extractor` (``.sample(ref, k)`` +
    ``.recipe_template(ref)``) onto the ``Rung`` shape WITHOUT touching it.

    HONESTY: the legacy extractors own their transport (curl_cffi / fetch_text) — the real,
    EGRESS-gated fetch. ``fetch_fn`` is accepted for protocol-uniformity but a legacy extractor
    fetches internally; the injectable fixture seam applies to the NEW rungs and to tests, not to
    extractors that predate it. So a legacy rung runs only behind the owner's EGRESS gate, never in
    the pure suite (which always passes an explicit fixture ladder).
    """
    extractor: Any
    cost: int
    k: int = 5

    @property
    def source(self) -> str:
        return self.extractor.source

    def recipe_template(self, target: str) -> Recipe:
        return self.extractor.recipe_template(target)

    def extract(self, target: str, fetch_fn: FetchFn) -> Sample:
        return self.extractor.sample(target, self.k)


def _legacy_pairs() -> list[tuple[int, Rung]]:
    """Build ``(cost, rung)`` pairs from the EXISTING extractors. Imported lazily: the pure suite
    passes an explicit ladder and never triggers this heavy import (curl_cffi, platform modules) —
    mirroring :meth:`RecipeRunner.replay`'s deferred import of the same registry."""
    from pipeline.recipe_extractors import EXTRACTORS

    pairs: list[tuple[int, Rung]] = []
    for name, ex_cls in EXTRACTORS.items():
        cost = _LEGACY_COST.get(name, _DEFAULT_LEGACY_COST)
        pairs.append((cost, LegacyRung(ex_cls(), cost=cost)))
    return pairs


def default_ladder() -> list[Rung]:
    """The production ladder: the EXISTING extractors (rungs 0-3) merged with any registered rungs
    (css / llm_local / future tools), sorted cheap->expensive."""
    return build_ladder(_legacy_pairs())


# ---------------------------------------------------------------------------
# The §02 new rungs (css cost 4, llm_local cost 7) wired into the registry. Each factory imports its
# heavy module LAZILY (lxml + the css derivation / llm-selector stack), so importing the cracker — or
# running the pure suite with an explicit fixture ladder — never pays that cost; only assembling
# default_ladder() / build_ladder() does. Both extractors implement the harness Extractor protocol,
# so the existing :class:`LegacyRung` adapter (Extractor -> Rung) wires them with no new machinery;
# their injectable transport is baked at construction (real engine here, a fixture in tests).
def _make_css_rung() -> Rung:
    """Factory for rung 4 (engine='css'): the adaptive CSS-selector extractor."""
    from pipeline.recipe_extract_css import CssAdaptiveExtractor
    return LegacyRung(CssAdaptiveExtractor(), cost=4)


def _make_llm_rung() -> Rung:
    """Factory for rung 7 (engine='llm_local'): the LLM-selector extractor, wired to the real €0
    LOCAL Ollama field-map inference (OWNER-GATED at runtime — needs a running Ollama daemon; the
    pure suite injects a mock instead). Constructing it does NOT call the model; only a real crack
    does, behind the egress/spend gate."""
    from pipeline.recipe_extract_llm import LlmFieldMapExtractor, ollama_field_map_fn
    return LegacyRung(LlmFieldMapExtractor(llm_fn=ollama_field_map_fn), cost=7)


# Adding a tool == one register_rung line; the orchestrator is never edited. default_ladder() now
# yields, sorted cheap->expensive: legacy 0-3 + css(4) + llm_local(7).
register_rung("css", _make_css_rung, cost=4)
register_rung("llm_local", _make_llm_rung, cost=7)


# ---------------------------------------------------------------------------
# §9.4 ranking feedback — read the winning rung a prior run recorded.
# ---------------------------------------------------------------------------
def winning_rung_of(recipe_dict: dict | None) -> int | None:
    """Read the persisted §9.4 ranking seed from a recipe dict (the warm-start input).

    The cracker stores ``winning_rung`` as a top-level key; :meth:`Recipe.from_dict` ignores
    unknown keys, so the schema is untouched. A production caller wires ``prior_fn`` as e.g.::

        prior_fn = lambda target: winning_rung_of(load_recipe_yaml(target))

    Returns None when absent/invalid -> the cracker cold-starts the full ladder.
    """
    if not isinstance(recipe_dict, dict):
        return None
    val = recipe_dict.get("winning_rung")
    return val if isinstance(val, int) and val >= 0 else None


def _attempt_order(n: int, warm: int | None) -> list[int]:
    """The order in which rungs are tried. Cold: 0..n-1 (cheap->expensive). Warm: the prior rung
    FIRST, then the full ladder from the bottom (so a warm MISS falls back to the whole ladder)."""
    base = list(range(n))
    if warm is None or not (0 <= warm < n):
        return base
    return [warm] + [i for i in base if i != warm]


def _failure_summary(target: str, attempts: list[RungAttempt]) -> str:
    """A non-silent FAILED reason: name every rung tried and why each one failed."""
    if not attempts:
        return f"no rung cracked {target!r}: the ladder was empty"
    per = "; ".join(f"rung{a.rung}({a.source}): {a.reason}" for a in attempts)
    return f"no rung cracked {target!r}: {per}"


def _persist_winner(
    rung: Rung, target: str, idx: int, *, declared: int | None, fetched: int, parsed: int,
    verdict: str, paths: dict[str, int], k: int, reason: str, now_iso: str | None,
    persist_fn: Callable[[str, dict], str | None] | None,
) -> str | None:
    """Build the winning recipe (with its VAM evidence) and persist it WITH the winning rung
    recorded. ``winning_rung`` rides as an extra top-level key — :func:`pipeline.recipe.write_recipe`
    round-trips it and :meth:`Recipe.from_dict` ignores it, so no schema is touched."""
    recipe = rung.recipe_template(target)
    recipe.status = STATUS_VERIFIED
    recipe.reason = reason
    recipe.evidence = Evidence(
        verified_at=now_iso, sample_k=k, declared=declared, fetched=fetched,
        parsed=parsed, vam_verdict=verdict, vam_paths=paths)

    payload = recipe.to_dict()
    payload["winning_rung"] = idx          # §9.4 ranking seed for the next warm-start
    payload["winning_source"] = rung.source

    key = recipe.cdp_code or f"{rung.source}__{target}"
    if persist_fn is not None:
        return persist_fn(key, payload)
    from pipeline.recipe import write_recipe  # lazy: keeps the module import-light

    return str(write_recipe(key, payload))


# ---------------------------------------------------------------------------
# The orchestrator.
# ---------------------------------------------------------------------------
async def crack_recipe(
    target: str,
    *,
    fetch_fn: FetchFn,
    ladder: list[Rung] | None = None,
    k: int = 5,
    conn: asyncpg.Connection | None = None,
    persist_fn: Callable[[str, dict], str | None] | None = None,
    prior_fn: Callable[[str], int | None] | None = None,
    now_iso: str | None = None,
) -> CrackResult:
    """Crack one ``target`` by walking the ladder cheap->expensive until a rung VERIFIES.

    Per rung: ``sample = rung.extract(target, fetch_fn)`` -> VAM verdict (DB seal when ``conn`` is
    given, else the offline mirror) -> :func:`decide_status`. The FIRST VERIFIED rung wins: its
    recipe is persisted with ``winning_rung`` recorded and the walk stops (costlier rungs untouched).
    If none verify -> :class:`CrackResult` FAILED carrying the per-rung reason.

    §9.4 warm-start: if ``prior_fn(target)`` yields a prior winning rung, that rung is tried FIRST;
    on a miss the walk falls back to the full ladder. ``fetch_fn`` is injectable (fixtures in tests;
    the real fetch is egress-gated and lives in the rungs, not here). The sample's crude is dropped
    after every rung (sample-verify-DELETE) so the cracker never accumulates bytes on disk.
    """
    rungs = list(ladder) if ladder is not None else default_ladder()
    rungs.sort(key=lambda r: r.cost)   # enforce the doctrine order regardless of input order

    warm_raw = prior_fn(target) if prior_fn is not None else None
    warm = warm_raw if (warm_raw is not None and 0 <= warm_raw < len(rungs)) else None
    order = _attempt_order(len(rungs), warm)

    attempts: list[RungAttempt] = []
    for idx in order:
        rung = rungs[idx]
        try:
            sample = rung.extract(target, fetch_fn)

            # VERIFY (VAM quorum over the sample's declared/fetched/parsed paths).
            paths = sample_paths(sample)
            if conn is not None:
                verdict = await record_count_verdict(
                    conn, subject_type="recipe_sample",
                    subject_key=f"{rung.source}:{target}",
                    claim="recipe sample parses without loss (fetched == parsed)",
                    paths=paths, tolerance=0.0, claim_kind="count")
            else:
                verdict = RecipeHarness._offline_verdict(paths)

            status, reason = decide_status(sample, k, verdict)

            # Capture the arithmetic, then DELETE the crude before moving to the next rung.
            declared, fetched, parsed_n = sample.declared, sample.fetched, len(sample.parsed)
            sample.parsed.clear()
        except Exception as exc:  # noqa: BLE001 — a raising rung must escalate, never abort the crack
            # A rung's transport can RAISE against a live target (a WAF block surfaces as FetchError,
            # a malformed page as a parse crash). The whole point of the ladder is that one rung's
            # failure ROUTES to the next; an uncaught raise here would abort the entire crack mid-walk
            # (the dry-run never hits this because fixtures return, they don't raise). Record it as a
            # non-silent FAILED attempt and escalate.
            attempts.append(RungAttempt(
                rung=idx, source=rung.source, status=STATUS_FAILED,
                reason=f"rung raised: {type(exc).__name__}: {exc}",
                declared=None, fetched=0, parsed=0, verdict="ERROR"))
            continue

        attempts.append(RungAttempt(
            rung=idx, source=rung.source, status=status, reason=reason,
            declared=declared, fetched=fetched, parsed=parsed_n, verdict=verdict))

        if status == STATUS_VERIFIED:
            recipe_path = _persist_winner(
                rung, target, idx, declared=declared, fetched=fetched, parsed=parsed_n,
                verdict=verdict, paths=paths, k=k, reason=reason, now_iso=now_iso,
                persist_fn=persist_fn)
            return CrackResult(
                target=target, status=STATUS_VERIFIED, winning_rung=idx,
                winning_source=rung.source, reason=reason, recipe_path=recipe_path,
                attempts=attempts, warm_started=warm is not None)

    return CrackResult(
        target=target, status=STATUS_FAILED, winning_rung=None, winning_source=None,
        reason=_failure_summary(target, attempts), recipe_path=None,
        attempts=attempts, warm_started=warm is not None)


# ---------------------------------------------------------------------------
# CLI — crack one target against the production ladder + DB (egress-gated at runtime).
# ---------------------------------------------------------------------------
async def _main(target: str, k: int) -> None:
    import os
    from datetime import datetime, timezone

    from pipeline.engine.fetch import fetch_text  # the real transport, used by the rungs

    dsn = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
    now = datetime.now(timezone.utc).isoformat()
    conn = await asyncpg.connect(dsn)
    try:
        res = await crack_recipe(target, fetch_fn=fetch_text, conn=conn, now_iso=now)
    finally:
        await conn.close()
    print(f"[recipe-cracker] target={target}")
    if res.status == STATUS_VERIFIED:
        print(f"  CRACKED at rung {res.winning_rung} ({res.winning_source}); recipe={res.recipe_path}")
    else:
        print(f"  FAILED: {res.reason}")
    for a in res.attempts:
        print(f"    rung{a.rung} {a.source}: {a.status} (fetched={a.fetched} parsed={a.parsed} "
              f"VAM={a.verdict}) — {a.reason}")


def main() -> None:
    import sys

    if len(sys.argv) < 2:
        print("usage: python -m pipeline.recipe_cracker <target> [k]")
        raise SystemExit(2)
    import asyncio

    target = sys.argv[1]
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    asyncio.run(_main(target, k))


if __name__ == "__main__":
    main()
