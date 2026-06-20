"""Fingerprint pool coherence + rotation (anti-JA3-random invariant)."""
import random

import pytest
from curl_cffi.requests.impersonate import BrowserTypeLiteral
import typing

from pipeline.engine import fingerprints as fp

_KNOWN_TARGETS = set(typing.get_args(BrowserTypeLiteral))


def test_every_profile_impersonate_is_a_real_curl_cffi_target():
    # If a curl_cffi upgrade drops a target, this fails LOUDLY instead of banning
    # us silently with an unknown impersonate string.
    for p in fp.all_profiles():
        assert p.impersonate in _KNOWN_TARGETS, p.impersonate


def test_chrome_ua_version_matches_impersonate_target():
    for p in fp.all_profiles():
        if p.family != "chrome":
            continue
        version = p.impersonate.replace("chrome", "")
        assert f"Chrome/{version}.0.0.0" in p.user_agent
        # client hints must carry the SAME version (coherence)
        assert f'v="{version}"' in p.headers["Sec-Ch-Ua"]


def test_non_chrome_profiles_never_send_chrome_client_hints():
    # A Firefox/Safari UA paired with Chrome Sec-Ch-Ua is an instant mismatch.
    for p in fp.all_profiles():
        if p.family == "chrome":
            continue
        assert "Sec-Ch-Ua" not in p.headers
        assert "Sec-Ch-Ua-Platform" not in p.headers


def test_pick_returns_a_chrome_profile_by_default():
    pool = fp.FingerprintPool(rng=random.Random(0))
    assert pool.pick().family == "chrome"


def test_rotate_never_returns_the_burned_profile():
    pool = fp.FingerprintPool(rng=random.Random(1))
    burned = fp.get_profile("chrome146")
    nxt = pool.rotate(burned)
    assert nxt is not None
    assert nxt.key != "chrome146"


def test_rotate_escalates_into_diversity_pool_then_exhausts():
    pool = fp.FingerprintPool(rng=random.Random(2))
    tried: set[str] = set()
    seen = []
    cur = fp.get_profile("chrome146")
    for _ in range(20):
        nxt = pool.rotate(cur, already_tried=tried)
        if nxt is None:
            break
        seen.append(nxt.key)
        tried.add(nxt.key)
        cur = nxt
    # all known profiles get visited, including a non-chrome diversity one, then None
    assert any(fp.get_profile(k).family != "chrome" for k in seen)
    assert pool.rotate(cur, already_tried=set(k.key for k in fp.all_profiles())) is None


def test_get_profile_unknown_raises():
    with pytest.raises(KeyError):
        fp.get_profile("chrome999")
