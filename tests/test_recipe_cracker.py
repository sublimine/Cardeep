"""Offline tests for the recipe CRACKER orchestrator (§02 country-autopilot, the missing core).

No DB, no network: every rung is a fake :class:`Extractor`-shaped object and the transport is
an injected ``fetch_fn`` returning canned counts. This drives the orchestrator's real logic
deterministically:

  * try-all escalation cheap->expensive over the ladder (sorted by ``cost``);
  * stop at the first VERIFIED rung WITHOUT probing the costlier ones;
  * record the winning rung (``winning_rung``) and persist a recipe that carries it;
  * on total failure, a per-rung reason (what each rung tried and why it failed) — never silent;
  * §9.4 ranking feedback: warm-start at a prior winning rung, falling back to the full ladder;
  * RUNG_REGISTRY extensibility: registering a new tool = it joins the ladder, untouched orchestrator.

The live VAM seal path (record_count_verdict) is async + DB-backed and has its own tests; here we
drive the DB-less branch (conn=None -> offline verdict), exactly like test_recipe_harness.py.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass

import pytest

from pipeline.recipe_cracker import (
    RUNG_REGISTRY,
    build_ladder,
    crack_recipe,
    register_rung,
)
from pipeline.recipe_harness import Sample
from pipeline.recipe_schema import (
    STATUS_FAILED,
    STATUS_VERIFIED,
    Parsing,
    Recipe,
    Transport,
)


@pytest.fixture(autouse=True)
def _isolate_recipe_writes(tmp_path, monkeypatch):
    """Gate (T0.3): every cracker test writes recipes into a tmp tree, NEVER the real
    countries/ES/recipes/. Without this, a VERIFIED crack with no ``persist_fn`` falls through to
    ``write_recipe()`` on the real tree — the r1__d.yaml / r3__d.yaml / llm_local__d.yaml pollution
    (fabricated declared:47 fixtures committed by accident). Structural + autouse, so no present or
    future cracker test can ever pollute the production recipe tree."""
    import pipeline.recipe as recipe_mod
    monkeypatch.setattr(recipe_mod, "ROOT", tmp_path)


# --- deterministic fakes ---------------------------------------------------
@dataclass
class _Canned:
    """What the injected ``fetch_fn`` hands a rung: the shape of one bounded sample.

    ``parsed`` valid cars out of ``fetched`` raw listings (``fetched - parsed`` is the parse loss).
    ``full_dealer`` admits ``declared`` into the VAM quorum (else a subset would falsely refute).
    """
    declared: int | None
    fetched: int
    parsed: int
    full_dealer: bool = False


class _FakeRung:
    """A ladder rung that pulls its sample SOLELY from the injected ``fetch_fn`` (no network).

    Records every ``target`` it is asked to extract in ``calls`` so a test can assert which rungs
    the orchestrator probed and which it (correctly) never touched.
    """

    def __init__(self, source: str, cost: int) -> None:
        self.source = source
        self.cost = cost
        self.calls: list[str] = []

    def recipe_template(self, target: str) -> Recipe:
        return Recipe(
            source=self.source, dealer_ref=target,
            transport=Transport(engine="http", base_url="https://x"),
            parsing=Parsing(engine="next_data"))

    def extract(self, target: str, fetch_fn) -> Sample:
        self.calls.append(target)
        c: _Canned = fetch_fn(self.source, target)  # the injectable transport seam
        parsed = [{"vin_ref": f"{self.source}-{i}", "deep_link": f"https://x/{self.source}/{i}"}
                  for i in range(c.parsed)]
        return Sample(declared=c.declared, fetched=c.fetched, parsed=parsed,
                      full_dealer=c.full_dealer)


def _fetch_from(table: dict[str, _Canned]):
    """Build a fake ``fetch_fn`` over a per-source canned table; records every (source, target)."""
    seen: list[tuple[str, str]] = []

    def _fetch(source: str, target: str) -> _Canned:
        seen.append((source, target))
        return table[source]

    _fetch.seen = seen  # type: ignore[attr-defined]
    return _fetch


# Canonical canned shapes producing each distinct decide_status outcome.
_CRACK = _Canned(declared=47, fetched=5, parsed=5)                       # zero loss -> VERIFIED
_PARSE_LOSS = _Canned(declared=10, fetched=5, parsed=3)                  # fetched>parsed -> FAILED
_EMPTY = _Canned(declared=None, fetched=0, parsed=0)                     # nothing -> FAILED
_REFUTED = _Canned(declared=99, fetched=5, parsed=5, full_dealer=True)   # declared rivals -> REFUTED
_UNDER = _Canned(declared=50, fetched=2, parsed=2)                       # parsed<k, no loss -> FAILED


# --- (1) cheap rung cracks: stop, never probe the costly rungs -------------
@pytest.mark.unit
def test_first_cheap_rung_that_cracks_wins_and_costly_rungs_are_not_probed(tmp_path, monkeypatch):
    # Real persistence into a temp tree so we PROVE the winning rung lands in the YAML asset.
    import pipeline.recipe as recipe_mod
    monkeypatch.setattr(recipe_mod, "ROOT", tmp_path)

    r0 = _FakeRung("r0", cost=0)   # fails (parse loss)
    r1 = _FakeRung("r1", cost=1)   # cracks
    r2 = _FakeRung("r2", cost=2)   # must NOT be probed
    r3 = _FakeRung("r3", cost=3)   # must NOT be probed
    fetch = _fetch_from({"r0": _PARSE_LOSS, "r1": _CRACK, "r2": _CRACK, "r3": _CRACK})

    res = asyncio.run(crack_recipe("dealer-1", fetch_fn=fetch, ladder=[r0, r1, r2, r3],
                                   now_iso="2026-06-28T00:00:00Z"))

    assert res.status == STATUS_VERIFIED
    assert res.winning_rung == 1
    assert res.winning_source == "r1"
    # escalation stopped at rung 1: the costlier rungs were never extracted.
    assert r2.calls == [] and r3.calls == []
    assert ("r2", "dealer-1") not in fetch.seen and ("r3", "dealer-1") not in fetch.seen
    # the persisted recipe asset carries the winning rung (the §9.4 ranking seed).
    import yaml
    written = yaml.safe_load(
        (tmp_path / "countries" / "ES" / "recipes" / "r1__dealer-1.yaml").read_text(encoding="utf-8"))
    assert written["status"] == STATUS_VERIFIED
    assert written["winning_rung"] == 1
    assert written["winning_source"] == "r1"
    assert written["evidence"]["parsed"] == 5


# --- (2) only the costly rung cracks: escalate 0->1->2->3 ------------------
@pytest.mark.unit
def test_escalates_through_whole_ladder_until_costly_rung_cracks():
    # Passed OUT OF ORDER on purpose: the orchestrator must sort by cost (cheap->expensive).
    r0 = _FakeRung("r0", cost=0)
    r1 = _FakeRung("r1", cost=1)
    r2 = _FakeRung("r2", cost=2)
    r3 = _FakeRung("r3", cost=3)
    fetch = _fetch_from({"r0": _PARSE_LOSS, "r1": _EMPTY, "r2": _REFUTED, "r3": _CRACK})

    res = asyncio.run(crack_recipe("d", fetch_fn=fetch, ladder=[r2, r0, r3, r1]))

    assert res.status == STATUS_VERIFIED
    assert res.winning_rung == 3
    # all four rungs were attempted, in cost order, with the right per-rung outcome.
    assert [a.rung for a in res.attempts] == [0, 1, 2, 3]
    assert [a.source for a in res.attempts] == ["r0", "r1", "r2", "r3"]
    assert res.attempts[0].status == STATUS_FAILED and "parse loss" in res.attempts[0].reason
    assert res.attempts[1].status == STATUS_FAILED and "empty sample" in res.attempts[1].reason
    assert res.attempts[2].status == STATUS_FAILED and "REFUTED" in res.attempts[2].reason
    assert res.attempts[3].status == STATUS_VERIFIED


# --- (3) nothing cracks: FAILED with a per-rung reason (no silent failure) --
@pytest.mark.unit
def test_no_rung_cracks_yields_failed_with_per_rung_reason():
    r0 = _FakeRung("r0", cost=0)
    r1 = _FakeRung("r1", cost=1)
    r2 = _FakeRung("r2", cost=2)
    r3 = _FakeRung("r3", cost=3)
    fetch = _fetch_from({"r0": _PARSE_LOSS, "r1": _EMPTY, "r2": _REFUTED, "r3": _UNDER})

    res = asyncio.run(crack_recipe("d", fetch_fn=fetch, ladder=[r0, r1, r2, r3]))

    assert res.status == STATUS_FAILED
    assert res.winning_rung is None
    assert res.winning_source is None
    assert res.recipe_path is None
    # every rung was tried and every failure reason is surfaced (the per-rung verdict).
    assert all(rung.calls == ["d"] for rung in (r0, r1, r2, r3))
    assert len(res.attempts) == 4
    assert "parse loss" in res.reason
    assert "empty sample" in res.reason
    assert "REFUTED" in res.reason
    assert "under target" in res.reason
    # each rung is named in the summary so the operator knows what was tried.
    for name in ("r0", "r1", "r2", "r3"):
        assert name in res.reason


# --- (4) §9.4 warm-start: begin at the prior winning rung, skip cheaper ----
@pytest.mark.unit
def test_warm_start_begins_at_prior_winning_rung_and_skips_cheaper():
    # r0 WOULD also crack; a cold start would win at 0. Warm-start at the prior rung (1) proves
    # the ranking feedback actually changed the order: rung 0 is never probed.
    r0 = _FakeRung("r0", cost=0)
    r1 = _FakeRung("r1", cost=1)
    r2 = _FakeRung("r2", cost=2)
    r3 = _FakeRung("r3", cost=3)
    fetch = _fetch_from({"r0": _CRACK, "r1": _CRACK, "r2": _CRACK, "r3": _CRACK})

    res = asyncio.run(crack_recipe("d", fetch_fn=fetch, ladder=[r0, r1, r2, r3],
                                   prior_fn=lambda target: 1))

    assert res.status == STATUS_VERIFIED
    assert res.winning_rung == 1
    assert res.warm_started is True
    assert r0.calls == []                 # cheaper rung skipped by warm-start
    assert r2.calls == [] and r3.calls == []


# --- (5) warm-start MISS: fall back to the full ladder ---------------------
@pytest.mark.unit
def test_warm_start_miss_falls_back_to_full_ladder():
    # Prior says rung 2, but rung 2 no longer cracks -> fall back to the whole ladder and win at 1.
    r0 = _FakeRung("r0", cost=0)
    r1 = _FakeRung("r1", cost=1)
    r2 = _FakeRung("r2", cost=2)
    r3 = _FakeRung("r3", cost=3)
    fetch = _fetch_from({"r0": _PARSE_LOSS, "r1": _CRACK, "r2": _EMPTY, "r3": _CRACK})

    res = asyncio.run(crack_recipe("d", fetch_fn=fetch, ladder=[r0, r1, r2, r3],
                                   prior_fn=lambda target: 2))

    assert res.status == STATUS_VERIFIED
    assert res.winning_rung == 1
    assert res.warm_started is True
    # warm rung tried FIRST, then the ladder from the bottom: order is [2, 0, 1].
    assert [a.rung for a in res.attempts] == [2, 0, 1]
    assert r3.calls == []                 # winner found before the costliest rung


# --- (6) RUNG_REGISTRY: register a new tool, it joins the ladder -----------
@pytest.fixture
def clean_registry():
    """Snapshot/restore the global RUNG_REGISTRY so a registry test never leaks into others."""
    snapshot = dict(RUNG_REGISTRY)
    try:
        yield
    finally:
        RUNG_REGISTRY.clear()
        RUNG_REGISTRY.update(snapshot)


@pytest.mark.unit
def test_registering_a_rung_adds_it_to_the_ladder_sorted_by_cost(clean_registry):
    # Adding a tool == registering an Extractor; the orchestrator is NOT edited.
    register_rung("llm_local", lambda: _FakeRung("llm_local", 7), cost=7)
    register_rung("css", lambda: _FakeRung("css", 4), cost=4)

    ladder = build_ladder()

    assert [r.cost for r in ladder] == [4, 7]            # cheap before expensive
    assert [r.source for r in ladder] == ["css", "llm_local"]


@pytest.mark.unit
def test_crack_runs_over_a_registry_built_ladder(clean_registry):
    register_rung("css", lambda: _FakeRung("css", 4), cost=4)
    register_rung("llm_local", lambda: _FakeRung("llm_local", 7), cost=7)
    fetch = _fetch_from({"css": _EMPTY, "llm_local": _CRACK})

    res = asyncio.run(crack_recipe("d", fetch_fn=fetch, ladder=build_ladder()))

    assert res.status == STATUS_VERIFIED
    assert res.winning_source == "llm_local"
    assert res.winning_rung == 1   # index within the cost-sorted ladder


# --- (7) a rung that RAISES (live WAF block / FetchError) is caught and escalated ----
@pytest.mark.unit
def test_rung_that_raises_is_recorded_failed_and_escalates(tmp_path, monkeypatch):
    """A live rung's extract can RAISE (FetchError against a WAF, a parse crash). That is a FAILED
    attempt to be RECORDED and ESCALATED past — never an abort of the whole crack. Against fixtures
    the cracker looks robust; against a live target the cheap rungs raise, so this is the path that
    decides whether the cracker survives the real world."""
    import pipeline.recipe as recipe_mod
    monkeypatch.setattr(recipe_mod, "ROOT", tmp_path)

    r0 = _FakeRung("r0", cost=0)   # raises (simulated WAF block / FetchError)
    r1 = _FakeRung("r1", cost=1)   # cracks

    def fetch(source: str, target: str):
        if source == "r0":
            raise RuntimeError("WAF blocked the request (simulated FetchError)")
        return _CRACK

    res = asyncio.run(crack_recipe("d", fetch_fn=fetch, ladder=[r0, r1],
                                   now_iso="2026-06-29T00:00:00Z"))

    assert res.status == STATUS_VERIFIED
    assert res.winning_rung == 1
    assert res.winning_source == "r1"
    # the raising rung is a non-silent FAILED attempt, not a crash; the walk escalated to r1.
    assert len(res.attempts) == 2
    assert res.attempts[0].rung == 0 and res.attempts[0].source == "r0"
    assert res.attempts[0].status == STATUS_FAILED
    assert "WAF blocked" in res.attempts[0].reason
    assert res.attempts[1].status == STATUS_VERIFIED


# --- (8) every rung raises: FAILED with a per-rung reason, never an uncaught crash ----
@pytest.mark.unit
def test_all_rungs_raising_yields_failed_not_crash():
    r0 = _FakeRung("r0", cost=0)
    r1 = _FakeRung("r1", cost=1)

    def fetch(source: str, target: str):
        raise RuntimeError(f"{source} blocked")

    res = asyncio.run(crack_recipe("d", fetch_fn=fetch, ladder=[r0, r1]))

    assert res.status == STATUS_FAILED
    assert res.winning_rung is None
    assert len(res.attempts) == 2
    assert all(a.status == STATUS_FAILED for a in res.attempts)
    # the per-rung reason names every rung that was tried (no silent failure).
    assert "r0" in res.reason and "r1" in res.reason
