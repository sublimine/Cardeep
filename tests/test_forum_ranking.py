"""Tests for pipeline/forum/ranking.py (08-forum-community F4, carta §4.1/§9).

Carta's own verification requirement: "test unitarios de la formula §4.1 con vectores
calculados a mano FUERA del código (doble camino para cada numero: log10 y gravedad
computados independientemente)". Every expected value below is written out as its own
``math.log10``/``** GRAVITY`` expression in the test — never by calling ``vote_term`` or
``rank_score`` to produce the expectation, only to produce the actual.
"""
from __future__ import annotations

import math

import pytest

from pipeline.forum.ranking import ANCHOR_BOOST, ANCHOR_CAP, GRAVITY, rank_score, vote_term


class TestVoteTerm:
    def test_zero_net_is_zero(self):
        assert vote_term(0) == 0.0

    def test_positive_net_matches_log10_by_hand(self):
        # V = sign(10) * log10(max(1, |10|)) = log10(10) = 1.0 exactly
        assert vote_term(10) == pytest.approx(1.0)

    def test_negative_net_matches_negative_log10_by_hand(self):
        # V = sign(-5) * log10(5) = -log10(5), hand-computed = -0.6989700043...
        assert vote_term(-5) == pytest.approx(-0.6989700043360189)

    def test_hundred_votes_matches_log10_by_hand(self):
        assert vote_term(100) == pytest.approx(2.0)

    def test_magnitude_damps_logarithmically(self):
        # "el voto 100 vale menos que el 10" — the DELTA from 10->100 must be smaller
        # than a naive linear scaling would predict (Reddit "hot" doctrine, carta §2.1).
        v10 = vote_term(10)
        v100 = vote_term(100)
        assert v100 - v10 == pytest.approx(1.0)  # log10(100)-log10(10) = 1, not 90


class TestRankScore:
    def test_hand_computed_vector_1_positive_net_no_anchor_fresh(self):
        # V = log10(10) = 1.0; rank = (1.0 + 0.4*0) / (0+2)**1.8
        expected = (math.log10(10) + 0.0) / (0 + 2) ** 1.8
        assert rank_score(net_votes=10, verified_anchor_count=0, hours_age=0) == pytest.approx(expected)
        assert rank_score(net_votes=10, verified_anchor_count=0, hours_age=0) == pytest.approx(0.2871745887492588)

    def test_hand_computed_vector_2_negative_net_two_anchors_aged(self):
        # V = -log10(5); rank = (V + 0.4*2) / (5+2)**1.8
        expected = (-math.log10(5) + 0.4 * 2) / (5 + 2) ** 1.8
        assert rank_score(net_votes=-5, verified_anchor_count=2, hours_age=5) == pytest.approx(expected)
        assert rank_score(net_votes=-5, verified_anchor_count=2, hours_age=5) == pytest.approx(0.0030428031860595386)

    def test_hand_computed_vector_3_anchor_cap_enforced(self):
        # 5 raw anchors must cap at ANCHOR_CAP=3: rank = (0 + 0.4*3) / (1+2)**1.8
        expected = (0.0 + 0.4 * 3) / (1 + 2) ** 1.8
        assert rank_score(net_votes=0, verified_anchor_count=5, hours_age=1) == pytest.approx(expected)
        assert rank_score(net_votes=0, verified_anchor_count=5, hours_age=1) == pytest.approx(0.16609745861540234)
        # capped count must equal the uncapped-at-exactly-3 case
        assert rank_score(0, 5, 1) == pytest.approx(rank_score(0, 3, 1))

    def test_hand_computed_vector_4_hundred_votes_fresh(self):
        expected = (math.log10(100) + 0.0) / (0 + 2) ** 1.8
        assert rank_score(net_votes=100, verified_anchor_count=0, hours_age=0) == pytest.approx(expected)
        assert rank_score(net_votes=100, verified_anchor_count=0, hours_age=0) == pytest.approx(0.5743491774985175)

    def test_gravity_decays_score_as_thread_ages(self):
        # HN doctrine (carta §2.1): "la relevancia decae polinomialmente" — same votes,
        # older thread, must score strictly lower.
        fresh = rank_score(net_votes=20, verified_anchor_count=1, hours_age=1)
        old = rank_score(net_votes=20, verified_anchor_count=1, hours_age=48)
        assert old < fresh

    def test_anchor_boost_strictly_increases_score(self):
        no_anchor = rank_score(net_votes=5, verified_anchor_count=0, hours_age=10)
        with_anchor = rank_score(net_votes=5, verified_anchor_count=1, hours_age=10)
        assert with_anchor > no_anchor

    def test_negative_hours_age_rejected(self):
        with pytest.raises(ValueError):
            rank_score(net_votes=1, verified_anchor_count=0, hours_age=-1)

    def test_constants_match_carta_exact_values(self):
        assert ANCHOR_BOOST == 0.4
        assert GRAVITY == 1.8
        assert ANCHOR_CAP == 3
