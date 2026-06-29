"""T4.3 — the DB-less VAM mirror (RecipeHarness._offline_verdict) must NOT certify zero.

verify.py's record_count_verdict has a zero_certifiable guard: two paths agreeing on 0 is the
ABSENCE of evidence, not a quorum, so the DB seal falls to UNVERIFIED. The offline mirror used by
the recipe-cracker when conn=None lacked that guard and returned TRUSTWORTHY for
{fetched:0, parsed:0} — a verdict that LIES in the attempt trail (decide_status still FAILs the
empty sample, so no recipe is persisted VERIFIED, but the recorded VAM verdict on the RungAttempt
read TRUSTWORTHY over a 0/0 sample). These tests pin the mirror to the same zero-certifiable rule
as the DB path, so the cracker's verdict trail can never claim a quorum over nothing.
"""
from __future__ import annotations

import pytest

from pipeline.recipe_harness import RecipeHarness

pytestmark = pytest.mark.unit

ov = RecipeHarness._offline_verdict


def test_zero_equals_zero_is_not_certifiable():
    # Two paths agreeing on 0 is the absence of evidence, not a quorum -> UNVERIFIED, never TRUSTWORTHY.
    assert ov({"fetched": 0, "parsed": 0}) == "UNVERIFIED"
    assert ov({"fetched": 0, "parsed": 0, "source_declared": 0}) == "UNVERIFIED"


def test_nonzero_agreement_is_trustworthy():
    assert ov({"fetched": 5, "parsed": 5}) == "TRUSTWORTHY"
    assert ov({"fetched": 5, "parsed": 5, "source_declared": 5}) == "TRUSTWORTHY"


def test_disagreement_is_refuted():
    assert ov({"fetched": 5, "parsed": 3}) == "REFUTED"
    assert ov({"fetched": 0, "parsed": 3}) == "REFUTED"


def test_single_path_is_unverified():
    assert ov({"fetched": 5}) == "UNVERIFIED"
    assert ov({}) == "UNVERIFIED"
