"""Stable public API surface + proxy auto-refresh (vía #2/#4)."""
import inspect

from pipeline.engine import api
from pipeline.engine import proxies as proxy_mod


# ---- public API surface (the discovery-session contract) -------------------

def test_api_exports_stable_surface():
    for name in ["open_session", "fetch", "fetch_dealer", "FetchEngine",
                 "FetchError", "ENGINE_API_VERSION"]:
        assert hasattr(api, name), name
    assert api.ENGINE_API_VERSION == "1.0.0"


def test_open_session_returns_configured_engine():
    s = api.open_session(tier1=True, headful=False)
    assert s.__class__.__name__ == "FetchEngine"
    assert s._allow_tier1 is True
    # default chain is multi-engine (go-around)
    assert len(s._tier1_engines) >= 1


def test_fetch_signature_is_stable():
    sig = inspect.signature(api.fetch)
    assert list(sig.parameters) == ["url", "tier1", "headers"]


def test_fetch_dealer_uses_route_around(monkeypatch):
    # fetch_dealer must try sources by priority and return the first that answers.
    s = api.open_session()
    calls = []

    def fake_fetch_text(url, *, tier=0):
        calls.append(url)
        return "<html>ok</html>"

    monkeypatch.setattr(s, "fetch_text", fake_fetch_text)
    res = api.fetch_dealer({"coches_net": "https://c.net/x",
                            "own_site": "https://own.es/stock"}, session=s)
    assert res.ok
    assert res.resolved_source == "own_site"   # own site first
    assert len(calls) == 1


# ---- proxy auto-refresh (vía #4) -------------------------------------------

def test_pool_populate_and_staleness():
    pool = proxy_mod.ProxyPool([])
    assert pool.is_stale(ttl=600, now=1000) is True       # empty -> stale
    pool.populate(["http://a:1", "http://b:2"], now=1000)
    assert pool.enabled and len(pool) == 2
    assert pool.is_stale(ttl=600, now=1100) is False      # fresh
    assert pool.is_stale(ttl=600, now=1700) is True       # > ttl -> stale


def test_ensure_fresh_harvests_when_stale_only():
    pool = proxy_mod.ProxyPool([])
    harvested = {"n": 0}

    def harvester():
        harvested["n"] += 1
        return ["http://live:8080"]

    # empty -> harvests
    pool.ensure_fresh(ttl=600, harvester=harvester, now=1000)
    assert len(pool) == 1 and harvested["n"] == 1
    # fresh -> does NOT harvest again
    pool.ensure_fresh(ttl=600, harvester=harvester, now=1100)
    assert harvested["n"] == 1
    # stale -> harvests again
    pool.ensure_fresh(ttl=600, harvester=harvester, now=1700)
    assert harvested["n"] == 2


def test_ensure_fresh_empty_harvest_leaves_host_ip():
    pool = proxy_mod.ProxyPool([])
    pool.ensure_fresh(ttl=600, harvester=lambda: [], now=1000)
    assert not pool.enabled            # still host IP (cost-zero), no crash
    assert pool.next() is None
