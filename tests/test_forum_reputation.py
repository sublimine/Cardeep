"""Tests for pipeline/forum/reputation.py (08-forum-community F4, carta §4.5) — pure
decision functions only; the DB-touching ledger apply logic is covered end-to-end in
tests/test_forum_router.py against the live census.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pipeline.forum.reputation import (
    DOWNVOTE_PRIVILEGE_MIN_REP,
    FLAG_PRIVILEGE_MIN_REP,
    PEER_INFLATION_WINDOW_DAYS,
    REP_DAILY_CAP,
    VOTE_PRIVILEGE_MIN_REP,
    can_downvote,
    can_flag,
    can_vote,
    daily_cap_remaining,
    is_within_inflation_window,
    upvote_delta,
)

NOW = datetime(2026, 7, 18, tzinfo=timezone.utc)


class TestUpvoteDelta:
    def test_anchor_scores_more_than_no_anchor(self):
        assert upvote_delta(has_verified_anchor=True) > upvote_delta(has_verified_anchor=False)


class TestPrivilegeGates:
    def test_vote_privilege_threshold(self):
        assert can_vote(VOTE_PRIVILEGE_MIN_REP) is True
        assert can_vote(VOTE_PRIVILEGE_MIN_REP - 1) is False

    def test_downvote_privilege_threshold(self):
        assert can_downvote(DOWNVOTE_PRIVILEGE_MIN_REP) is True
        assert can_downvote(DOWNVOTE_PRIVILEGE_MIN_REP - 1) is False

    def test_flag_privilege_threshold(self):
        assert can_flag(FLAG_PRIVILEGE_MIN_REP) is True
        assert can_flag(FLAG_PRIVILEGE_MIN_REP - 1) is False

    def test_privilege_ordering_is_monotonic(self):
        # A user who can flag must also be able to downvote and vote (carta §4.5's
        # graduated-trust ladder, Discourse-pattern).
        assert FLAG_PRIVILEGE_MIN_REP > DOWNVOTE_PRIVILEGE_MIN_REP > VOTE_PRIVILEGE_MIN_REP


class TestInflationWindow:
    def test_no_prior_credit_is_not_within_window(self):
        assert is_within_inflation_window(None, NOW) is False

    def test_credit_yesterday_is_within_window(self):
        assert is_within_inflation_window(NOW - timedelta(days=1), NOW) is True

    def test_credit_exactly_at_window_edge_still_within(self):
        assert is_within_inflation_window(NOW - timedelta(days=PEER_INFLATION_WINDOW_DAYS - 0.001), NOW) is True

    def test_credit_past_window_is_not_within(self):
        assert is_within_inflation_window(NOW - timedelta(days=PEER_INFLATION_WINDOW_DAYS + 1), NOW) is False


class TestDailyCap:
    def test_no_credit_today_leaves_full_cap(self):
        assert daily_cap_remaining(0) == REP_DAILY_CAP

    def test_partial_credit_reduces_remaining(self):
        assert daily_cap_remaining(30) == REP_DAILY_CAP - 30

    def test_over_cap_never_goes_negative(self):
        assert daily_cap_remaining(REP_DAILY_CAP + 50) == 0
