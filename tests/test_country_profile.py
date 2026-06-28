"""Golden — Fase B foundation, PIECE 1+8: CountryProfile + countries/<CC>/country.toml.

COUNTRY-PACK-CONTRACT.md §2 (pieces 1 & 8) + §4 (physical form ``countries/<CC>/country.toml``)
+ stage-10 row: each country pack ships a ``country.toml`` manifest naming the country_code,
the subdivision validator that will replace ``complete.py:_PROVINCE_RE``, and the national-kinds
override of ``complete.py:_NATIONAL_KINDS``. This golden pins the loader + the ES data.

Scope guard (Fase B only): this is JUST the loader + the data. ``complete.py`` is NOT rewired to
consume the profile here (that is Fase A/E de-cegado, OI-5) — so ES G1 behaviour is untouched.
The cross-checks below assert the toml data is byte-identical to the live engine constants, so
when the rewire lands it is a no-op for ES.
"""
from __future__ import annotations

import sys
import os

import pytest

# Allow running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.country_profile import CountryProfile
from pipeline.complete import _PROVINCE_RE, _NATIONAL_KINDS


class TestLoadES:
    def test_country_code(self) -> None:
        assert CountryProfile.load("ES").country_code == "ES"

    def test_national_kinds(self) -> None:
        p = CountryProfile.load("ES")
        assert p.national_kinds == frozenset(
            {"subasta", "plataforma", "oem_vo_portal", "importador"}
        )

    def test_national_kinds_is_frozenset(self) -> None:
        assert isinstance(CountryProfile.load("ES").national_kinds, frozenset)


class TestSubdivisionValidator:
    """The ES subdivision validator = INE province grid 01–52."""

    @pytest.mark.parametrize("code", ["01", "28", "52"])
    def test_accepts_valid_ine_codes(self, code: str) -> None:
        assert CountryProfile.load("ES").matches_subdivision(code) is True

    @pytest.mark.parametrize("code", ["00", "53", "XX"])
    def test_rejects_invalid_codes(self, code: str) -> None:
        assert CountryProfile.load("ES").matches_subdivision(code) is False

    def test_regex_string_is_the_ine_pattern(self) -> None:
        assert CountryProfile.load("ES").subdivision_regex == r"^(0[1-9]|[1-4][0-9]|5[0-2])$"


class TestByteIdentityWithEngine:
    """The toml data must equal the LIVE engine constants, so the future rewire of
    complete.py to consume the profile is a no-op for ES (byte-identical G1)."""

    def test_subdivision_regex_matches_complete_province_re(self) -> None:
        assert CountryProfile.load("ES").subdivision_regex == _PROVINCE_RE.pattern

    def test_national_kinds_match_complete_constant(self) -> None:
        assert CountryProfile.load("ES").national_kinds == _NATIONAL_KINDS


class TestLoaderRobustness:
    def test_country_code_matches_requested(self) -> None:
        # The loaded profile's country_code must equal what was requested.
        assert CountryProfile.load("ES").country_code == "ES"

    def test_unknown_country_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            CountryProfile.load("ZZ")

    def test_immutable(self) -> None:
        p = CountryProfile.load("ES")
        with pytest.raises((AttributeError, TypeError)):
            p.country_code = "DE"  # type: ignore[misc]
