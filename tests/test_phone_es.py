"""P06 CAPA-0: pure-stdlib Spanish phone normalizer (E.164) — the €0 replacement for the absent
``phonenumbers`` install gate.

Two ``_normalize_phone`` copies already exist in pipeline/identity (resolve_entities min-7,
cross_source_dedup min-9), neither validating the Spanish shape (9 national digits starting 6/7/8/9):
both blindly take the last 9 digits, so an extension or a malformed 10-digit string yields a fragile
key that can FALSE-merge two distinct dealers. This authority validates the shape, so a phone is only a
cross-source hard key when it is a real Spanish number — every vector is checked against the official
numbering plan (mobile 6/7, geographic/landline/special 8/9; national part always 9 digits).
"""
import pytest

from pipeline.identity.phone_es import normalize_es_phone, phone_match_key

pytestmark = pytest.mark.unit


class TestNormalizeE164:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("612345678", "+34612345678"),
            ("+34 612 345 678", "+34612345678"),
            ("0034612345678", "+34612345678"),
            ("+34612345678", "+34612345678"),
            ("911234567", "+34911234567"),       # Madrid landline (9)
            ("+34 91 123 45 67", "+34911234567"),
            ("712345678", "+34712345678"),       # 7-prefix mobile
            ("812345678", "+34812345678"),       # 8-prefix
        ],
    )
    def test_valid_to_e164(self, raw, expected):
        assert normalize_es_phone(raw) == expected

    @pytest.mark.parametrize(
        "raw",
        [
            "1234567",            # 7 digits, too short for a Spanish number
            "12345",              # too short
            "512345678",          # 9 digits but starts with 5 (not a valid leading digit)
            "341234567",          # 9 digits starting 3 — not Spanish-shaped
            "6123456789",         # 10 digits — malformed
            "612345678100",       # number + extension
            "",
            "   ",
            None,
            "abc",
        ],
    )
    def test_invalid_returns_none(self, raw):
        assert normalize_es_phone(raw) is None


class TestMatchKey:
    def test_returns_9_digit_national(self):
        assert phone_match_key("+34 612 345 678") == "612345678"
        assert phone_match_key("0034911234567") == "911234567"

    def test_prefix_variants_collapse(self):
        assert phone_match_key("+34612345678") == phone_match_key("612345678") == "612345678"

    @pytest.mark.parametrize("bad", ["1234567", "6123456789", "512345678", "", None])
    def test_invalid_returns_none(self, bad):
        assert phone_match_key(bad) is None
