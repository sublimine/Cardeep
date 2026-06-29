"""Property-based invariants (T1.3, plans/road-to-13) — Hypothesis over the engine's load-bearing
PURE invariants, replacing example-goldens with universal claims over the whole input space.

Two invariant families, both DB-free:
  * COVER(CC) campaign state machine (pipeline/autopilot/state.py): the validator MUST agree with
    the transition graph for EVERY (from, to) pair; the lifecycle is strictly linear forward; SEALED
    is terminal; unknown states always reject.
  * cdp_code identity (services/api/codes.py): deterministic; country-paramétric format; distinct
    identities → distinct codes; and THE country-proof invariant — country_code never enters
    canonical_key (the immutable dedup pre-image), so threading a 2nd country can never re-key an
    existing ES entity.

Non-vacuity is PROVEN by the mutation checks recorded in plans/road-to-13/PROGRESO.md (muting the
graph, or leaking country into canonical_key, makes the relevant property fail with a counterexample).
The oracles here (the hardcoded linear lifecycle; the cross-country key equality) are INDEPENDENT of
the code under test, so a mutation is actually caught.
"""
from __future__ import annotations

import hashlib
import re

import pytest
from hypothesis import given
from hypothesis import strategies as st

from pipeline.autopilot import state as sm
from services.api.codes import _base32, canonical_key, cdp_code, cdp_pair

pytestmark = pytest.mark.unit

# The lifecycle as an INDEPENDENT oracle (hardcoded, NOT read from VALID_TRANSITIONS) so a mutation
# of the graph is genuinely caught by the linear-walk property.
_LINEAR = [sm.REGISTERED, sm.KNOW_COUNTRY, sm.BOOTSTRAPPED, sm.IN_COVERAGE, sm.SEALED]


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------
@given(st.sampled_from(_LINEAR), st.sampled_from(_LINEAR))
def test_validator_agrees_with_graph_for_every_pair(a, b):
    """assert_valid_transition raises IFF the edge is NOT in the graph — for every state pair."""
    if b in sm.VALID_TRANSITIONS[a]:
        sm.assert_valid_transition(a, b)  # legal -> must not raise
    else:
        with pytest.raises(sm.CampaignTransitionError):
            sm.assert_valid_transition(a, b)


def test_lifecycle_is_strictly_linear_forward_to_terminal():
    """Following next_state from REGISTERED yields EXACTLY the linear lifecycle and halts at SEALED
    (bounded loop: it must terminate, never cycle)."""
    walk = [sm.REGISTERED]
    cur = sm.REGISTERED
    for _ in range(len(_LINEAR) + 3):
        nxt = sm.next_state(cur)
        if nxt is None:
            break
        walk.append(nxt)
        cur = nxt
    assert walk == _LINEAR
    assert sm.next_state(sm.SEALED) is None  # terminal


@given(st.sampled_from(_LINEAR))
def test_no_legal_edge_goes_backward(a):
    """Every legal edge advances strictly forward in the lifecycle (no regression, no self-loop)."""
    for b in sm.VALID_TRANSITIONS[a]:
        assert _LINEAR.index(b) > _LINEAR.index(a)


@given(st.text(min_size=1).filter(lambda s: s not in sm.ALL_STATES))
def test_unknown_states_always_reject(bogus):
    with pytest.raises(sm.CampaignTransitionError):
        sm.assert_valid_transition(sm.REGISTERED, bogus)   # unknown target
    with pytest.raises(sm.CampaignTransitionError):
        sm.assert_valid_transition(bogus, sm.SEALED)       # unknown source


@given(st.sampled_from(_LINEAR))
def test_initial_transition_only_to_registered(s):
    if s == sm.INITIAL_STATE:
        sm.assert_valid_transition(None, s)  # birth -> REGISTERED is the only legal initial edge
    else:
        with pytest.raises(sm.CampaignTransitionError):
            sm.assert_valid_transition(None, s)


# ---------------------------------------------------------------------------
# cdp_code identity
# ---------------------------------------------------------------------------
_cc = st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=2, max_size=2)
_prov = st.text(alphabet="0123456789", min_size=2, max_size=2)
_name = st.text(min_size=1, max_size=40)
_muni = st.text(alphabet="0123456789", min_size=5, max_size=5)
_CODE_RE = re.compile(r"^CDP-[A-Z]{2}-[0-9A-Z]{2,8}-[0-9A-HJKMNP-TV-Z]{8}$")


@given(_cc, _prov, _name, _muni)
def test_cdp_code_is_deterministic(cc, prov, name, muni):
    a = cdp_code(province_code=prov, name=name, municipality_code=muni, country_code=cc)
    b = cdp_code(province_code=prov, name=name, municipality_code=muni, country_code=cc)
    assert a == b


@given(_cc, _prov, _name, _muni)
def test_cdp_code_matches_generic_country_format(cc, prov, name, muni):
    code = cdp_code(province_code=prov, name=name, municipality_code=muni, country_code=cc)
    assert _CODE_RE.match(code), code
    assert code.startswith(f"CDP-{cc}-")


@given(_prov, _name, _muni, _cc, _cc)
def test_country_never_enters_canonical_key(prov, name, muni, cc1, cc2):
    """THE country-proof identity invariant: country_code is NOT part of the immutable dedup
    pre-image, so the SAME identity yields the SAME canonical_key under ANY country — threading a
    second country can never re-key an existing ES entity (codes.py:62-65)."""
    k1 = canonical_key(name=name, municipality_code=muni, province_code=prov, country_code=cc1)
    k2 = canonical_key(name=name, municipality_code=muni, province_code=prov, country_code=cc2)
    assert k1 == k2


@given(_cc, _prov, _name, _name, _muni)
def test_distinct_identities_get_distinct_codes(cc, prov, n1, n2, muni):
    """Different canonical identities (same province) hash to different codes (sha256 injectivity in
    practice) — guards against an accidental code collapse that would merge two real dealers."""
    k1, c1 = cdp_pair(province_code=prov, name=n1, municipality_code=muni, country_code=cc)
    k2, c2 = cdp_pair(province_code=prov, name=n2, municipality_code=muni, country_code=cc)
    if k1 != k2:
        assert c1 != c2


def test_es_cdp_code_is_byte_identical_to_historical():
    """ES output stays byte-identical to the historical CDP-ES-{prov}-{base32} (no regression)."""
    key = canonical_key(name="Talleres Pepe", municipality_code="28079", province_code="28")
    expect = f"CDP-ES-28-{_base32(hashlib.sha256(key.encode('utf-8')).digest())}"
    got = cdp_code(province_code="28", name="Talleres Pepe", municipality_code="28079")
    assert got == expect
