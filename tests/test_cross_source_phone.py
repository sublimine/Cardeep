"""P06 CAPA-0: cross_source_dedup._normalize_phone now delegates to the validated phone_es authority.

Locks the strict behaviour (was untested): a valid Spanish number yields its 9-digit national key
(identical to the legacy output), and anything malformed yields None (the legacy 'last 9 digits'
would have produced a fragile key that could false-merge distinct dealers).
"""
import pytest

from pipeline.identity.cross_source_dedup import _normalize_phone

pytestmark = pytest.mark.unit


class TestCrossSourceNormalizePhone:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("+34 612 345 678", "612345678"),
            ("0034612345678", "612345678"),
            ("911234567", "911234567"),
        ],
    )
    def test_valid_keys_match_legacy(self, raw, expected):
        assert _normalize_phone(raw) == expected

    @pytest.mark.parametrize("bad", ["6123456789", "512345678", "1234567", "", None])
    def test_malformed_now_rejected(self, bad):
        # The legacy 'last 9 digits' accepted several of these as fragile keys; the validated
        # authority rejects them — strictly fewer false-positive phone edges.
        assert _normalize_phone(bad) is None
