"""Unit tests for the OcasionPlus native listing_ref extraction (vo_chains connector).

Pure string tests — no DB, no network.  The connector-layer green-review flagged the
OcasionPlus listing_ref as fragile (`url.rsplit('-', 1)[-1]` with no cleaning): a car URL
carrying a ?query, #fragment or trailing '/' would yield a DIFFERENT ref for the same car.

Vehicle identity is keyed on deep_link in ingest, so this never corrupted delta — but the
STORED native ref must still be stable (future cross-source identity / B7 may use it). These
tests pin that stability: query/fragment/trailing-slash variants of one car -> ONE ref.
"""
from __future__ import annotations

import pytest

from pipeline.platform.group_vo_chains_wholesale import _ocasionplus_listing_ref

_BASE = "https://www.ocasionplus.com/coches-segunda-mano/seat-leon-togx7qan"


class TestOcasionplusListingRef:
    @pytest.mark.parametrize(
        "url, expected",
        [
            (_BASE, "togx7qan"),                      # clean (backward-compatible)
            (_BASE + "/", "togx7qan"),                # trailing slash
            (_BASE + "?utm_source=newsletter", "togx7qan"),  # query string
            (_BASE + "#gallery", "togx7qan"),         # fragment
            (_BASE + "/?utm=x#frag", "togx7qan"),     # all three at once
        ],
    )
    def test_extracts_stable_tail(self, url: str, expected: str) -> None:
        assert _ocasionplus_listing_ref(url) == expected

    def test_same_car_variants_yield_one_ref(self) -> None:
        """The core property: query/fragment/slash variants of ONE car -> ONE ref (no churn)."""
        refs = {
            _ocasionplus_listing_ref(_BASE),
            _ocasionplus_listing_ref(_BASE + "/"),
            _ocasionplus_listing_ref(_BASE + "?utm=x"),
            _ocasionplus_listing_ref(_BASE + "#g"),
            _ocasionplus_listing_ref(_BASE + "/?a=1&b=2#frag"),
        }
        assert refs == {"togx7qan"}, f"variants must collapse to one ref, got {refs}"

    def test_no_hyphen_falls_back_to_clean_url(self) -> None:
        """No '-' tail -> the cleaned URL is the ref (stable + unique, never empty)."""
        assert _ocasionplus_listing_ref("https://x.com/abc123") == "https://x.com/abc123"
        # cleaned of query/slash even on the fallback path
        assert _ocasionplus_listing_ref("https://x.com/abc123/?q=1") == "https://x.com/abc123"

    def test_never_empty(self) -> None:
        """A trailing-hyphen URL must not produce an empty ref."""
        assert _ocasionplus_listing_ref("https://x.com/seat-leon-") != ""
