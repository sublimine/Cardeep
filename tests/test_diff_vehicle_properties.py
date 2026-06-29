"""T1.3-ext — property invariants of the delta core (diff_vehicle), the heart of the "tiempo real".

diff_vehicle compares a DB snapshot vs a freshly scraped record and emits PRICE/KM/PHOTO change
events. Over the WHOLE input space (Hypothesis), the invariants the served delta depends on:
  * NO FALSE POSITIVES — re-seeing the same car (equal valid values) emits nothing;
  * a change is emitted IFF the (sanitised) value actually differs;
  * NULL->valid promotion fills (a field first absent then published is a change);
  * junk (price<=0 / >€5M, km<0 / >=1.5M) emits NOTHING (sanitised away).
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from hypothesis import given
from hypothesis import strategies as st

from pipeline.delta import diff_vehicle

pytestmark = pytest.mark.unit


def _new(price=None, km=None, photo_url=None, photo_hash=None):
    return SimpleNamespace(price=price, km=km, photo_url=photo_url, photo_hash=photo_hash)


@given(price=st.one_of(st.none(), st.integers(1, 5_000_000)),
       km=st.one_of(st.none(), st.integers(0, 1_499_999)),
       photo=st.one_of(st.none(), st.text(min_size=1, max_size=20)))
def test_no_event_when_new_equals_old(price, km, photo):
    old = {"price": price, "km": km, "photo_url": photo}
    new = _new(price=price, km=km, photo_url=photo)
    assert diff_vehicle(old, new) == []   # re-seeing the same car invents no delta


@given(old_p=st.integers(1, 5_000_000), new_p=st.integers(1, 5_000_000))
def test_price_change_iff_value_differs(old_p, new_p):
    evs = [e for e in diff_vehicle({"price": old_p, "km": None, "photo_url": None}, _new(price=new_p))
           if e["event_type"] == "PRICE_CHANGE"]
    if float(old_p) != float(new_p):
        assert len(evs) == 1 and evs[0]["new_value"]["price"] == float(new_p)
    else:
        assert evs == []


@given(new_p=st.integers(1, 5_000_000))
def test_null_to_valid_price_fills(new_p):
    evs = diff_vehicle({"price": None, "km": None, "photo_url": None}, _new(price=new_p))
    assert any(e["event_type"] == "PRICE_CHANGE" and e["old_value"]["price"] is None for e in evs)


@given(junk=st.one_of(st.integers(max_value=0), st.integers(min_value=5_000_001)))
def test_junk_price_emits_no_change(junk):
    evs = diff_vehicle({"price": 1000, "km": None, "photo_url": None}, _new(price=junk))
    assert all(e["event_type"] != "PRICE_CHANGE" for e in evs)


@given(old_k=st.integers(0, 1_499_999), new_k=st.integers(0, 1_499_999))
def test_km_change_iff_value_differs(old_k, new_k):
    evs = [e for e in diff_vehicle({"price": None, "km": old_k, "photo_url": None}, _new(km=new_k))
           if e["event_type"] == "KM_CHANGE"]
    assert (len(evs) == 1) if old_k != new_k else (evs == [])


def test_photo_change_on_url_change_only():
    assert any(e["event_type"] == "PHOTO_CHANGE"
               for e in diff_vehicle({"price": None, "km": None, "photo_url": "a.jpg"},
                                     _new(photo_url="b.jpg")))
    assert all(e["event_type"] != "PHOTO_CHANGE"
               for e in diff_vehicle({"price": None, "km": None, "photo_url": "a.jpg"},
                                     _new(photo_url="a.jpg")))
