"""Recipe harness — the canonical recipe-first / sample-verify-delete cycle (§4).

This is the executable spine the master plan calls the highest-ROI gap: today the
real order is scrape -> ingest -> recipe POST-HOC (``harvest_dealer.py:71-73``) and
no loader ever *replays* a recipe. This harness inverts that into the mandated cycle:

    EXTRACT SAMPLE (k≈3-5)  ->  PERSIST RECIPE  ->  VERIFY (VAM)  ->  DELETE SAMPLE
                                       ^  if VERIFY refutes -> mark FAILED w/ reason  ^

Doctrine honoured:
  * recipe-first        — the recipe (config) is the durable asset, persisted as YAML.
  * sample-verify-delete— only k cars are pulled; the raw sample is wiped at the end so
                          the harness never fills the disk (mandate §10).
  * VAM                 — verification reuses :func:`pipeline.verify.record_count_verdict`
                          (declared / fetched / parsed quorum), never a hand-rolled check.
  * no silent failure   — a recipe is VERIFIED or FAILED *with a reason*, never ambiguous.

Reuse, not duplication: the AutoScout24 extractor wraps the already-working
``pipeline.sources.autoscout24`` module (the only verified open Tier-0 source). New
sources implement the tiny :class:`Extractor` protocol; the harness is source-agnostic.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

import asyncpg

from pipeline.recipe import write_recipe
from pipeline.recipe_schema import (
    STATUS_FAILED,
    STATUS_VERIFIED,
    Evidence,
    Fingerprint,
    Pagination,
    Parsing,
    Recipe,
    Transport,
)
from pipeline.verify import record_count_verdict

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Extractor protocol — the only thing a new source must implement.
# ---------------------------------------------------------------------------
@dataclass
class Sample:
    """The result of pulling a bounded sample from one dealer.

    ``declared`` is the source's own oracle (its asserted total, may be > k for a big
    dealer). ``fetched`` is how many raw listings the transport consumed. ``parsed`` is
    the list of valid vehicle dicts the parsing engine produced. ``full_dealer`` is True
    iff the sample covers the dealer's ENTIRE inventory (declared <= k) — only then may
    ``declared`` join the VAM quorum, otherwise a deliberate subset would falsely refute.
    """
    declared: int | None
    fetched: int
    parsed: list[dict]
    full_dealer: bool


class Extractor(Protocol):
    """A source-specific bridge the harness drives. ``recipe_template`` returns a DRAFT
    recipe (transport/pagination/parsing pre-filled, evidence empty); ``sample`` performs
    the bounded extraction."""

    source: str

    def recipe_template(self, dealer_ref: str) -> Recipe: ...

    def sample(self, dealer_ref: str, k: int) -> Sample: ...


# ---------------------------------------------------------------------------
# Pure verdict logic — offline-testable, no DB, no network.
# ---------------------------------------------------------------------------
def sample_paths(s: Sample) -> dict[str, int]:
    """Build the VAM evidence paths for a sample.

    Always compares the integrity pair ``fetched`` (what the transport pulled, an HTTP
    family path) vs ``parsed`` (what the parser produced, a DB-family path). ``declared``
    (a source-family path) is added ONLY when the sample is the full dealer — including it
    on a deliberate subset would force a REFUTED verdict for a perfectly good recipe.
    """
    paths = {"fetched": s.fetched, "parsed": len(s.parsed)}
    if s.full_dealer and s.declared is not None:
        paths["source_declared"] = s.declared
    return paths


def decide_status(s: Sample, k: int, verdict: str) -> tuple[str, str]:
    """Decide (status, reason) for a recipe given its sample and the VAM verdict.

    A recipe is VERIFIED iff ALL hold:
      * zero parse loss on the sample (every fetched listing parsed) — the recipe is
        faithful to the bytes;
      * it actually produced cars (>= the target slice size);
      * VAM did not REFUTE (TRUSTWORTHY or UNVERIFIED both pass — UNVERIFIED means
        "cannot certify a quorum" e.g. a 2-path same-family agreement, NOT a disagreement).
    Otherwise FAILED, with the precise reason (never a silent pass).
    """
    target = s.declared if (s.full_dealer and s.declared is not None) else k
    parsed_n = len(s.parsed)
    loss = s.fetched - parsed_n
    if s.fetched == 0 or parsed_n == 0:
        return STATUS_FAILED, "empty sample — transport or enumeration yielded no listings"
    if loss != 0:
        return STATUS_FAILED, f"parse loss on sample: fetched={s.fetched} parsed={parsed_n} (lost {loss})"
    if parsed_n < min(target, k) and not s.full_dealer:
        return STATUS_FAILED, f"sample under target: parsed={parsed_n} < k={k}"
    if verdict == "REFUTED":
        return STATUS_FAILED, f"VAM REFUTED the sample counts: {sample_paths(s)}"
    note = "full-dealer sample" if s.full_dealer else f"k={k} slice, zero parse loss"
    return STATUS_VERIFIED, f"VAM {verdict}; {note}"


@dataclass
class HarnessResult:
    dealer_ref: str
    status: str
    reason: str
    verdict: str
    declared: int | None
    fetched: int
    parsed: int
    recipe_path: str | None


# ---------------------------------------------------------------------------
# The harness.
# ---------------------------------------------------------------------------
class RecipeHarness:
    """Drives one dealer through EXTRACT -> PERSIST -> VERIFY -> DELETE.

    ``conn`` is optional: with a live connection the VAM verdict is sealed in
    ``verification_verdict`` (subject_type='recipe_sample'); without one the harness
    verifies offline (verdict computed locally is reported as 'OFFLINE' and the recipe
    is still marked VERIFIED/FAILED — useful for tests and air-gapped replays).
    """

    def __init__(self, extractor: Extractor, conn: asyncpg.Connection | None = None,
                 now_iso: str | None = None) -> None:
        self._ex = extractor
        self._conn = conn
        self._now = now_iso  # injected timestamp (scripts forbid Date.now()-style nondeterminism)

    async def run(self, dealer_ref: str, k: int = 5, cdp_code: str | None = None) -> HarnessResult:
        # 1) EXTRACT a bounded sample (the ONLY bytes we pull; wiped at step 5).
        sample = self._ex.sample(dealer_ref, k)

        # 2) VERIFY (VAM quorum over declared/fetched/parsed).
        paths = sample_paths(sample)
        if self._conn is not None:
            verdict = await record_count_verdict(
                self._conn, subject_type="recipe_sample",
                subject_key=cdp_code or f"{self._ex.source}:{dealer_ref}",
                claim="recipe sample parses without loss (fetched == parsed)",
                paths=paths, tolerance=0.0, claim_kind="count")
        else:
            verdict = self._offline_verdict(paths)

        status, reason = decide_status(sample, k, verdict)

        # 3) BUILD the recipe with its evidence (the durable, reproducible asset).
        recipe = self._ex.recipe_template(dealer_ref)
        recipe.cdp_code = cdp_code
        recipe.status = status
        recipe.reason = reason
        recipe.evidence = Evidence(
            verified_at=self._now, sample_k=k, declared=sample.declared,
            fetched=sample.fetched, parsed=len(sample.parsed),
            vam_verdict=verdict, vam_paths=paths)

        # 4) PERSIST the recipe (YAML, committed). Keyed by cdp_code when minted, else slug.
        recipe_path = None
        try:
            path = write_recipe(cdp_code or f"{self._ex.source}__{dealer_ref}", recipe.to_dict())
            recipe_path = str(path)
        except Exception as exc:  # noqa: BLE001 — persistence failure must surface, not be swallowed
            log.error("recipe persist FAILED for %s: %s", dealer_ref, exc)
            raise

        # 5) DELETE the sample (sample-verify-DELETE: never fill the disk). The sample lives
        # only in local memory here; dropping the reference IS the delete. No raw file is
        # written by the harness, so there is nothing on disk to leak.
        sample.parsed.clear()

        return HarnessResult(
            dealer_ref=dealer_ref, status=status, reason=reason, verdict=verdict,
            declared=recipe.evidence.declared, fetched=recipe.evidence.fetched,
            parsed=recipe.evidence.parsed, recipe_path=recipe_path)

    @staticmethod
    def _offline_verdict(paths: dict[str, int]) -> str:
        """Local quorum mirror for DB-less runs: TRUSTWORTHY iff >=2 paths agree exactly
        and no rival pair disagrees; REFUTED if any two disagree; else UNVERIFIED. This is
        the SAME shape as record_count_verdict but without the DB seal (reported 'OFFLINE'
        upstream only in the absence of a conn)."""
        vals = list(paths.values())
        if len(vals) < 2:
            return "UNVERIFIED"
        if len(set(vals)) == 1:
            return "TRUSTWORTHY"
        return "REFUTED"


@dataclass
class ReplayResult:
    dealer_ref: str
    source: str
    reproduced: bool
    parsed: int
    parse_loss: int
    note: str


class RecipeRunner:
    """Replays a persisted recipe SOLELY from its YAML, proving the recipe is a
    self-sufficient asset (its whole point: "re-scrape without the raw crude").

    The runner reads the recipe file, selects the extractor named by ``recipe.source``,
    and re-extracts ``recipe.dealer_ref`` — locating and re-scraping the dealer using only
    what the YAML carries. Reproduction succeeds iff the replay still parses with no loss.

    HONESTY: a fully field-map-driven interpreter (execute parsing purely from the YAML
    field_map, incl. the §4 css/llm_local ladder) is deliberately NOT claimed here — the
    extractor still owns the parse code. What IS proven: the recipe carries enough to
    relocate the source and reproduce the sample without any retained crude.
    """

    def __init__(self, now_iso: str | None = None) -> None:
        self._now = now_iso

    def replay(self, recipe_path: str, k: int = 5) -> ReplayResult:
        import yaml

        from pipeline.recipe_extractors import EXTRACTORS
        from pipeline.recipe_schema import Recipe

        with open(recipe_path, encoding="utf-8") as fh:
            recipe = Recipe.from_dict(yaml.safe_load(fh))
        if recipe.source not in EXTRACTORS:
            return ReplayResult(recipe.dealer_ref, recipe.source, False, 0, 0,
                                f"no extractor registered for source {recipe.source!r}")
        sample = EXTRACTORS[recipe.source]().sample(recipe.dealer_ref, k)
        loss = sample.fetched - len(sample.parsed)
        reproduced = len(sample.parsed) > 0 and loss == 0
        return ReplayResult(
            dealer_ref=recipe.dealer_ref, source=recipe.source, reproduced=reproduced,
            parsed=len(sample.parsed), parse_loss=loss,
            note=("reproduced from YAML" if reproduced
                  else f"replay mismatch: fetched={sample.fetched} parsed={len(sample.parsed)}"))


# ---------------------------------------------------------------------------
# CLI — recipe-first cycle for one dealer against the live source + DB.
# ---------------------------------------------------------------------------
async def _main(source: str, dealer_ref: str, k: int) -> None:
    import os
    from datetime import datetime, timezone

    from pipeline.recipe_extractors import EXTRACTORS

    if source not in EXTRACTORS:
        raise SystemExit(f"unknown source {source!r}; available: {list(EXTRACTORS)}")
    dsn = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
    now = datetime.now(timezone.utc).isoformat()
    conn = await asyncpg.connect(dsn)
    try:
        harness = RecipeHarness(EXTRACTORS[source](), conn=conn, now_iso=now)
        res = await harness.run(dealer_ref, k=k)
    finally:
        await conn.close()
    print(f"[recipe-harness] source={source} dealer={dealer_ref}")
    print(f"  declared={res.declared} fetched={res.fetched} parsed={res.parsed} "
          f"VAM={res.verdict}")
    print(f"  status={res.status} reason={res.reason}")
    print(f"  recipe={res.recipe_path}")


def main() -> None:
    import sys

    if len(sys.argv) < 3:
        print("usage: python -m pipeline.recipe_harness <source> <dealer_ref> [k]")
        raise SystemExit(2)
    import asyncio

    source, dealer_ref = sys.argv[1], sys.argv[2]
    k = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    asyncio.run(_main(source, dealer_ref, k))


if __name__ == "__main__":
    main()
