"""Offline tests for the recipe harness (§4 recipe-first / sample-verify-delete).

No DB, no network: a fake Extractor feeds canned samples so the harness's pure logic
(quorum paths, VERIFIED/FAILED decision, recipe round-trip, sample deletion) is asserted
deterministically. The live VAM seal path (record_count_verdict) has its own DB-backed
quorum tests; here we drive the DB-less branch (conn=None -> offline verdict).
"""
from __future__ import annotations

import asyncio

import pytest

from pipeline.recipe_harness import (
    RecipeHarness,
    Sample,
    decide_status,
    sample_paths,
)
from pipeline.recipe_schema import (
    STATUS_FAILED,
    STATUS_VERIFIED,
    Recipe,
    Transport,
)


# --- a deterministic fake source ------------------------------------------
class _FakeExtractor:
    source = "fake"

    def __init__(self, sample: Sample) -> None:
        self._sample = sample

    def recipe_template(self, dealer_ref: str) -> Recipe:
        return Recipe(source=self.source, dealer_ref=dealer_ref,
                      transport=Transport(engine="http", base_url="https://x"))

    def sample(self, dealer_ref: str, k: int) -> Sample:
        return self._sample


def _veh(i: int) -> dict:
    return {"vin_ref": f"v{i}", "deep_link": f"https://x/{i}", "make": "Seat"}


# --- sample_paths ----------------------------------------------------------
@pytest.mark.unit
def test_sample_paths_subset_excludes_declared():
    # A deliberate k-slice of a big dealer must NOT feed `declared` into the quorum,
    # or a perfectly faithful recipe would be REFUTED for sampling a subset.
    s = Sample(declared=47, fetched=5, parsed=[_veh(i) for i in range(5)], full_dealer=False)
    assert sample_paths(s) == {"fetched": 5, "parsed": 5}


@pytest.mark.unit
def test_sample_paths_full_dealer_includes_declared():
    s = Sample(declared=3, fetched=3, parsed=[_veh(i) for i in range(3)], full_dealer=True)
    assert sample_paths(s) == {"fetched": 3, "parsed": 3, "source_declared": 3}


# --- decide_status ---------------------------------------------------------
@pytest.mark.unit
def test_verified_when_no_parse_loss_and_not_refuted():
    s = Sample(declared=47, fetched=5, parsed=[_veh(i) for i in range(5)], full_dealer=False)
    status, reason = decide_status(s, k=5, verdict="TRUSTWORTHY")
    assert status == STATUS_VERIFIED
    assert "zero parse loss" in reason


@pytest.mark.unit
def test_failed_on_parse_loss():
    s = Sample(declared=47, fetched=5, parsed=[_veh(i) for i in range(3)], full_dealer=False)
    status, reason = decide_status(s, k=5, verdict="TRUSTWORTHY")
    assert status == STATUS_FAILED
    assert "parse loss" in reason


@pytest.mark.unit
def test_failed_on_empty_sample():
    s = Sample(declared=0, fetched=0, parsed=[], full_dealer=False)
    status, reason = decide_status(s, k=5, verdict="UNVERIFIED")
    assert status == STATUS_FAILED
    assert "empty sample" in reason


@pytest.mark.unit
def test_failed_when_vam_refutes():
    s = Sample(declared=3, fetched=3, parsed=[_veh(i) for i in range(3)], full_dealer=True)
    status, reason = decide_status(s, k=5, verdict="REFUTED")
    assert status == STATUS_FAILED
    assert "REFUTED" in reason


@pytest.mark.unit
def test_unverified_verdict_still_passes_when_clean():
    # UNVERIFIED means "cannot quorum-certify", NOT "disagreement" -> a clean sample passes.
    s = Sample(declared=47, fetched=5, parsed=[_veh(i) for i in range(5)], full_dealer=False)
    status, _ = decide_status(s, k=5, verdict="UNVERIFIED")
    assert status == STATUS_VERIFIED


# --- recipe round-trip -----------------------------------------------------
@pytest.mark.unit
def test_recipe_round_trips_through_dict():
    r = Recipe(source="autoscout24", dealer_ref="foo-123", cdp_code="ES-28-ABC")
    r.status = STATUS_VERIFIED
    rebuilt = Recipe.from_dict(r.to_dict())
    assert rebuilt.source == "autoscout24"
    assert rebuilt.dealer_ref == "foo-123"
    assert rebuilt.cdp_code == "ES-28-ABC"
    assert rebuilt.status == STATUS_VERIFIED


@pytest.mark.unit
def test_recipe_rejects_unknown_status():
    with pytest.raises(ValueError):
        Recipe(source="x", dealer_ref="y", status="MAYBE")


# --- harness end-to-end (offline branch) -----------------------------------
@pytest.mark.unit
def test_harness_offline_verifies_and_deletes_sample(tmp_path, monkeypatch):
    # Persist into a temp recipes dir so the test never writes the real countries/ES tree.
    import pipeline.recipe as recipe_mod
    monkeypatch.setattr(recipe_mod, "ROOT", tmp_path)

    parsed = [_veh(i) for i in range(5)]
    s = Sample(declared=47, fetched=5, parsed=parsed, full_dealer=False)
    harness = RecipeHarness(_FakeExtractor(s), conn=None, now_iso="2026-06-20T00:00:00Z")
    res = asyncio.run(harness.run("foo-123", k=5))

    assert res.status == STATUS_VERIFIED
    assert res.verdict == "TRUSTWORTHY"   # offline: fetched==parsed -> exact agreement
    assert res.parsed == 5
    # sample-verify-DELETE: the in-memory sample list is emptied after the cycle.
    assert parsed == []
    # recipe persisted as YAML and round-trips back to VERIFIED.
    import yaml
    written = yaml.safe_load((tmp_path / "countries" / "ES" / "recipes" / "fake__foo-123.yaml").read_text(encoding="utf-8"))
    assert written["status"] == STATUS_VERIFIED
    assert written["evidence"]["parsed"] == 5


@pytest.mark.unit
def test_harness_offline_fails_on_disagreement(tmp_path, monkeypatch):
    import pipeline.recipe as recipe_mod
    monkeypatch.setattr(recipe_mod, "ROOT", tmp_path)
    # fetched != parsed -> offline verdict REFUTED -> FAILED with reason.
    s = Sample(declared=10, fetched=5, parsed=[_veh(i) for i in range(3)], full_dealer=False)
    harness = RecipeHarness(_FakeExtractor(s), conn=None, now_iso="2026-06-20T00:00:00Z")
    res = asyncio.run(harness.run("bar-9", k=5))
    assert res.status == STATUS_FAILED
    assert res.verdict == "REFUTED"
