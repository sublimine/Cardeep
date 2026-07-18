"""rank_score — the forum feed's ranking formula (carta §4.1, exact).

    V          = sign(net) * log10(max(1, |net|))     net = upvotes - downvotes
    rank_score = (V + ANCHOR_BOOST*A) / (h + 2)^GRAVITY
      A = number of VERIFIED anchors on the post (entity/vehicle exists and responds via
          the API at render time — carta §4.2), capped at ANCHOR_CAP
      h = hours since the thread's created_at
      ANCHOR_BOOST = 0.4 (config, [ASUMIDO] product hypothesis — carta §4.1)

Traceability (carta §4.1): the log-damped vote term is Reddit's "hot" formula (§2.1,
exact); the (h+2)^1.8 gravity denominator is Hacker News's formula (§2.1, exact,
GRAVITY=1.8). ONLY the ANCHOR_BOOST*A term is this pilar's own addition, deliberately
isolated in its own named constant so it can be tuned or removed without touching the two
borrowed, publicly-documented formulas.

This module is PURE — no DB, no I/O — so tests/test_forum_ranking.py can hand-compute
log10/gravity independently (carta §9 F4 verification requirement: "vectores calculados a
mano FUERA del código, doble camino para cada número") without importing this same code
to check itself.
"""
from __future__ import annotations

import math

ANCHOR_BOOST: float = 0.4
GRAVITY: float = 1.8
ANCHOR_CAP: int = 3


def vote_term(net_votes: int) -> float:
    """V = sign(net) * log10(max(1, |net|)). net=0 -> 0.0 (log10(1) with sign(0)=0)."""
    if net_votes == 0:
        return 0.0
    sign = 1.0 if net_votes > 0 else -1.0
    return sign * math.log10(max(1, abs(net_votes)))


def rank_score(net_votes: int, verified_anchor_count: int, hours_age: float) -> float:
    """Carta §4.1 formula, exact. ``verified_anchor_count`` is capped at ANCHOR_CAP here
    (callers pass the raw count; capping is this formula's job, not the caller's)."""
    if hours_age < 0:
        raise ValueError("hours_age must be >= 0")
    a = min(max(verified_anchor_count, 0), ANCHOR_CAP)
    v = vote_term(net_votes)
    return (v + ANCHOR_BOOST * a) / (hours_age + 2) ** GRAVITY
