"""Regression test for the DealerK-family confirmed-empty-window false failure.

Root cause (source_health consecutive_fails=5, breaker down since 2026-06-21):
a scheduled `--from-db` run whose candidate window contained ZERO live family
members harvested 0 cars. All three VAM quorum paths were 0, and because the
connector did NOT flag the zero as observation-measured, `record_count_verdict`
returned UNVERIFIED (EXACT_ZERO rule). `run_ok` then read that as a hard FAIL,
even though the run had positively fingerprinted every candidate host and
cleanly confirmed none was a family member.

The fix: a run that positively OBSERVED at least one candidate host (i.e. not
every requested dealer hard-failed to fetch) measured the emptiness by
observation, so a confirmed-empty window certifies TRUSTWORTHY-0 instead of a
false UNVERIFIED failure. A real total outage (every host failed, or none
requested) is NOT observed and must keep failing honestly.
"""
from pipeline.platform.family_dealerk_wholesale import window_was_observed


def _stats(*, member=0, non_family=0, empty=0, failed=0, requested=0) -> dict:
    return {
        "dealers_member": member,
        "dealers_skipped_non_family": non_family,
        "dealers_empty": empty,
        "dealers_failed": failed,
        "dealers_requested": requested,
    }


def test_confirmed_empty_window_is_observed():
    # Every candidate fetched cleanly and was a non-family site -> we SAW the
    # window and confirmed it empty. This must count as observed.
    stats = _stats(non_family=8, requested=8)
    assert window_was_observed(stats) is True


def test_single_member_window_is_observed():
    stats = _stats(member=2, non_family=6, requested=8)
    assert window_was_observed(stats) is True


def test_empty_inventory_member_is_observed():
    # A real family member that served an empty listing is still an observation.
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
