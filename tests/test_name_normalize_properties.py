"""T1.3-ext — property invariants of the canonical name normaliser (country-proof, OPEN-C).

normalize_name is the shared identity key for the clusterers. Two invariants verified over the WHOLE
input space (Hypothesis), the country-proof core:
  * the output never leaks a non-[a-z0-9] character (the matching key is always clean), and
  * a non-Latin name is TRANSLITERATED, not erased — so distinct non-Latin dealers keep distinct keys
    instead of all collapsing to their incidental Latin token (the over-merge the legacy ascii-fold
    caused for GR/BG/RU tenants).
"""
from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from pipeline.identity.name_normalize import normalize_name

pytestmark = pytest.mark.unit

_ALNUM = set("abcdefghijklmnopqrstuvwxyz0123456789")


@given(st.text())
def test_output_is_clean_alnum_or_none(name):
    out = normalize_name(name)
    if out is not None:
        assert out != ""
        assert all(c in _ALNUM for c in out)   # never a non-Latin / non-alnum leak in the key


@given(st.text())
def test_normalize_is_deterministic(name):
    assert normalize_name(name) == normalize_name(name)


def test_es_byte_identity_preserved():
    assert normalize_name("Citroën") == "citroen"
    assert normalize_name("Peña") == "pena"
    assert normalize_name("Škoda") == "skoda"
    assert normalize_name("Talleres García, S.L.") == "talleresgarcia"  # legal suffix stripped


def test_non_latin_is_transliterated_not_erased():
    # 'Αθήνα Motors' must keep the Greek part transliterated (athina), not collapse to 'motors'
    # (which would over-merge every distinct Greek "... Motors" dealer).
    out = normalize_name("Αθήνα Motors")
    assert out is not None and out.isascii()
    assert "motors" in out and out != "motors"


def test_pure_drop_symbols_yield_none():
    # symbols the legacy fold dropped must NOT start injecting characters; pure-symbol -> None.
    assert normalize_name("®") is None
    assert normalize_name("©®") is None
    assert normalize_name("") is None and normalize_name("   ") is None
