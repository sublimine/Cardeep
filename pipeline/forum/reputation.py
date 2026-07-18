"""Reputation ledger constants + pure decision logic (carta §4.5).

``reputation_event`` (migrations/0095_forum.sql) is an append-only ledger — same doctrine
as ``vehicle_event``/``fleet_ops_event`` ("NEVER updated or deleted"). The DB-touching
apply logic lives in ``services/api/routers/forum.py`` (it needs a live connection for the
anti-inflado dedup lookup and the daily cap); this module holds the constants and the pure
decision functions so they can be unit-tested without a database.

Values marked [ASUMIDO] in the carta (§4.5): the research for this campaign did not extract
Stack Overflow's exact reputation table (+5/+10/+15/-2/-1) — a previous draft cited it
without a verified source, and this carta's own header degrades that citation. The numbers
below are this pilar's own hypothesis, adjustable, NOT presented as SO's real table.
"""
from __future__ import annotations

from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Reputation deltas (carta §4.5, all [ASUMIDO] — no verified public source for these
# exact numbers, unlike the vote-ranking formulas in ranking.py which ARE sourced).
# ---------------------------------------------------------------------------

REP_UPVOTE_ANCHOR: int = 10       # upvote received on a post with a VERIFIED anchor
REP_UPVOTE_NO_ANCHOR: int = 4     # upvote received on a post without one
REP_WANTED_CLOSED_BOUGHT: int = 15  # a wanted_listing closed as 'bought_via_cardeep'
REP_DOWNVOTE_RECEIVED: int = -2   # downvote received
REP_DOWNVOTE_CAST: int = -1      # "the power to harm costs something" — casting a downvote

REP_DAILY_CAP: int = 100  # per user, per day, from VOTE-driven deltas only (closures exempt)

# ---------------------------------------------------------------------------
# Privilege thresholds (carta §4.5 — adaptation of Discourse's TL-level PATTERN; the
# exact TL1-TL4 numeric thresholds are Discourse's own and NOT reused verbatim here,
# only the STRUCTURE: privileges gated by measured behaviour, moderation always manual).
# ---------------------------------------------------------------------------

VOTE_PRIVILEGE_MIN_REP: int = 10
DOWNVOTE_PRIVILEGE_MIN_REP: int = 50
FLAG_PRIVILEGE_MIN_REP: int = 100

# Anti-inflado (carta §4.5, eBay §2.3 EXACT: dedup same buyer's repeat feedback within the
# same calendar week) — adapted here as "same voter -> same author pair counts once per
# 7 days for REPUTATION" (the vote itself always counts for the post's own rank_score,
# carta §7.4 invariant: never conflate the ledger's anti-abuse dedup with the public vote
# count).
PEER_INFLATION_WINDOW_DAYS: int = 7


def is_within_inflation_window(last_credited_at: datetime | None, now: datetime) -> bool:
    """True if a reputation credit for this (voter, author) pair was already granted
    within the anti-inflado window — the caller should skip crediting again."""
    if last_credited_at is None:
        return False
    return now - last_credited_at < timedelta(days=PEER_INFLATION_WINDOW_DAYS)


def upvote_delta(has_verified_anchor: bool) -> int:
    return REP_UPVOTE_ANCHOR if has_verified_anchor else REP_UPVOTE_NO_ANCHOR


def can_vote(rep: int) -> bool:
    return rep >= VOTE_PRIVILEGE_MIN_REP


def can_downvote(rep: int) -> bool:
    return rep >= DOWNVOTE_PRIVILEGE_MIN_REP


def can_flag(rep: int) -> bool:
    return rep >= FLAG_PRIVILEGE_MIN_REP


def daily_cap_remaining(credited_today: int) -> int:
    """How many more vote-driven reputation points may be credited today (>=0)."""
    return max(0, REP_DAILY_CAP - credited_today)
