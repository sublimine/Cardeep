"""Regression test for the CMS-WordPress family confirmed-empty-window false failure.

Root cause (source_health family_cms_wp consecutive_fails=3, status=down since
2026-06-21): a scheduled `--from-db` run whose candidate window — ordered by
`last_seen DESC` — contained ZERO harvestable family members (mostly non-WordPress
sites plus WordPress sites running themes outside the override table) harvested 0
cars. All three VAM quorum paths were 0, and because the connector did NOT flag the
zero as observation-measured, `record_count_verdict` returned UNVERIFIED (the
EXACT_ZERO rule in pipeline/verify.py). `run_ok` then read that as a hard FAIL,
even though the run had positively fingerprinted every candidate host and cleanly
confirmed none was a harvestable member.

This is the SAME bug already fixed in the sibling family connector
(family_dealerk_wholesale.window_was_observed). The fix here mirrors it: a run that
positively OBSERVED at least one candidate host (member, confirmed non-family, or
member with empty inventory) measured the emptiness by observation, so a
confirmed-empty window certifies TRUSTWORTHY-0 instead of a false UNVERIFIED
failure. A real total outage (every host hard-failed, or none requested) is NOT
observed and must keep failing honestly.

The extractor itself is verified live-working (gestiauto.es via the ga-car-card
HTML theme, autosraul.com via the Vehica REST gateway): this regression is purely
the verdict/health classification of a legitimately empty scheduler window.
"""
from pipeline.platform.family_cms_wordpress_dominated__wholesale import (
    window_was_observed,
)


def _stats(*, member=0, non_family=0, empty=0, failed=0, requested=0) -> dict:
    return {
        "dealers_member": member,
        "dealers_skipped_non_family": non_family,
        "dealers_empty": empty,
        "dealers_failed": failed,
        "dealers_requested": requested,
    }


def test_confirmed_empty_window_is_observed():
    # Every candidate fetched cleanly and was a non-WordPress / non-member site ->
    # we SAW the window and confirmed it empty. This must count as observed.
    stats = _stats(non_family=8, requested=8)
    assert window_was_observed(stats) is True


def test_single_member_window_is_observed():
    stats = _stats(member=2, non_family=6, requested=8)
    assert window_was_observed(stats) is True


def test_empty_inventory_member_is_observed():
    # A real WordPress family member that exposed no known inventory surface is
    # still an observation of the window.
    stats = _stats(empty=3, requested=3)
    assert window_was_observed(stats) is True


def test_total_outage_is_not_observed():
    # Every requested dealer hard-failed to fetch -> we observed nothing -> the
    # empty result is NOT measured and must not certify as TRUSTWORTHY-0.
    stats = _stats(failed=8, requested=8)
    assert window_was_observed(stats) is False


def test_no_candidates_is_not_observed():
    # An empty candidate list observed nothing.
    stats = _stats(requested=0)
    assert window_was_observed(stats) is False
