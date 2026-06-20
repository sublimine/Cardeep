"""P08-S2: diff_vehicle PHOTO branch is content-aware via pHash Hamming, with URL fallback.

Pure (no infra). Verifies the new behaviour and that the legacy URL path is preserved exactly
when perceptual hashes are absent (backward compatibility for the 26 connectors not yet hashing).
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from pipeline.delta import diff_vehicle
from pipeline.delta_photo import is_phash

# 16-hex pHashes. _A and _A2 differ in 4 bits (<=10 -> same photo); _B differs from _A in many.
_A = "ffffffff00000000"
_A2 = "fffffff000000000"   # 4-bit Hamming from _A (recompression / CDN re-encode)
_B = "0f0f0f0ff0f0f0f0"    # far from _A (re-photographed car)


def _veh(**kw) -> SimpleNamespace:
    base = {"price": None, "km": None, "photo_url": None, "photo_hash": None}
    base.update(kw)
    return SimpleNamespace(**base)


def _photo_events(events):
    return [e for e in events if e["event_type"] == "PHOTO_CHANGE"]


@pytest.mark.unit
def test_phash_close_is_not_a_change_even_when_url_rotated():
    # CDN rotated the URL but the image is the same (pHash within tolerance) -> NO PHOTO_CHANGE.
    old = {"photo_url": "https://cdn/a-v1.jpg", "photo_hash": _A}
    new = _veh(photo_url="https://cdn/a-v2.jpg", photo_hash=_A2)
    assert _photo_events(diff_vehicle(old, new)) == []


@pytest.mark.unit
def test_phash_far_is_a_change_even_when_url_identical():
    # Same URL, but the car was re-photographed (pHash far apart) -> PHOTO_CHANGE.
    old = {"photo_url": "https://cdn/a.jpg", "photo_hash": _A}
    new = _veh(photo_url="https://cdn/a.jpg", photo_hash=_B)
    evs = _photo_events(diff_vehicle(old, new))
    assert len(evs) == 1
    assert evs[0]["old_value"]["phash"] == _A and evs[0]["new_value"]["phash"] == _B


@pytest.mark.unit
def test_url_fallback_when_phash_absent():
    # No phash on either side -> legacy URL comparison (backward-compatible).
    old = {"photo_url": "https://cdn/a.jpg"}
    assert _photo_events(diff_vehicle(old, _veh(photo_url="https://cdn/b.jpg")))  # changed
    assert _photo_events(diff_vehicle(old, _veh(photo_url="https://cdn/a.jpg"))) == []  # same


@pytest.mark.unit
def test_malformed_phash_falls_back_to_url_safely():
    # A junk phash must NOT crash; it falls back to the URL path.
    old = {"photo_url": "https://cdn/a.jpg", "photo_hash": "not-a-hash"}
    new = _veh(photo_url="https://cdn/b.jpg", photo_hash="zzzz")
    assert _photo_events(diff_vehicle(old, new))  # url differs -> change via fallback


@pytest.mark.unit
def test_is_phash_guard():
    assert is_phash(_A) and is_phash("0" * 16)
    assert not is_phash("xyz") and not is_phash(None) and not is_phash("zzzzzzzzzzzzzzzz")
    assert not is_phash("fff")  # wrong length
