"""Tiered fetch cascade: Tier-0 rotation -> block detection -> Tier-1 cookie-reuse.

All doubles — no network, no real browser. Verifies the 37-connector contract is
intact (signatures/attributes) and the escalation logic is correct.
"""
import inspect

import pytest

from pipeline.engine import clearance_cache
from pipeline.engine import fetch as fetchmod
from pipeline.engine.fetch import FetchEngine, FetchError


@pytest.fixture(autouse=True)
def _isolate_clearance_cache():
    # The clearance cache is process-global; clear it around every test so a
    # cached solve from one test cannot leak into another's queued responses.
    clearance_cache.clear()
    yield
    clearance_cache.clear()


_OK_BODY = "<html><body>" + "x" * 40000 + "</body></html>"
_CF_BODY = "<title>Just a moment...</title> cf-chl- Checking your browser ray id"


class _Resp:
    def __init__(self, status, text, headers=None):
        self.status_code = status
        self.text = text
        self.headers = headers or {}


class _FakeSession:
    """Returns queued responses in order; records cookies set."""
    def __init__(self, queue):
        self._queue = list(queue)
        self.cookies = _FakeJar()
        self.gets = []

    def get(self, url, headers=None, timeout=None):
        self.gets.append(url)
        if not self._queue:
            raise AssertionError("no more queued responses")
        return self._queue.pop(0)


class _FakeJar:
    def __init__(self):
        self.store = {}

    def set(self, name, value):
        self.store[name] = value


def _engine_with(queue, **kw):
    eng = FetchEngine(impersonate="chrome131", polite_min=0.0, polite_max=0.0, **kw)
    fake = _FakeSession(queue)
    eng._session = fake
    # rotation must keep using a fake session, not a real curl_cffi one
    eng._new_session = lambda profile: fake  # type: ignore[assignment]
    return eng, fake


def test_public_signature_is_unchanged():
    sig = inspect.signature(FetchEngine.fetch_text)
    assert list(sig.parameters) == ["self", "url", "tier", "headers"]
    modsig = inspect.signature(fetchmod.fetch_text)
    assert list(modsig.parameters) == ["url", "tier", "headers"]


def test_legacy_attributes_present():
    eng, _ = _engine_with([_Resp(200, _OK_BODY)])
    assert hasattr(eng, "impersonate")
    assert hasattr(eng, "last_status")
    assert hasattr(eng, "fetch_count")
    out = eng.fetch_text("https://x.test/")
    assert out == _OK_BODY
    assert eng.last_status == 200
    assert eng.fetch_count == 1
    assert eng.last_tier == 0


def test_clean_200_returns_body():
    eng, fake = _engine_with([_Resp(200, _OK_BODY)])
    assert eng.fetch_text("https://x.test/") == _OK_BODY
    assert fake.gets == ["https://x.test/"]


def test_challenge_with_escalation_off_then_rotation_recovers():
    # first profile blocked, rotated profile succeeds — no browser needed
    eng, _ = _engine_with([_Resp(200, _CF_BODY), _Resp(200, _OK_BODY)],
                          allow_tier1_escalation=False)
    assert eng.fetch_text("https://x.test/") == _OK_BODY


def test_challenge_survives_rotation_escalation_off_raises():
    # every rotation also blocked, escalation off -> fail loud (no silent body)
    blocked = [_Resp(200, _CF_BODY)] * 8
    eng, _ = _engine_with(blocked, allow_tier1_escalation=False)
    with pytest.raises(FetchError):
        eng.fetch_text("https://x.test/")


def test_not_found_raises_without_escalation():
    eng, _ = _engine_with([_Resp(404, "gone")])
    with pytest.raises(FetchError):
        eng.fetch_text("https://x.test/404")


def test_tier1_cookie_reuse(monkeypatch):
    # Browser solve mints a clearance cookie; curl_cffi reuse then serves OK.
    from pipeline.engine.tier1 import BrowserResult

    def fake_solve(url, **kw):
        return BrowserResult(html=_OK_BODY, cookies={"cf_clearance": "TOKEN"},
                             user_agent="UA-FROM-BROWSER", final_url=url,
                             engine="nodriver")

    monkeypatch.setattr("pipeline.engine.tier1.solve_challenge", fake_solve)
    # served curl_cffi reuse returns clean 200
    eng, fake = _engine_with([_Resp(200, _OK_BODY)])
    out = eng.fetch_text("https://walled.test/", tier=1)
    assert out == _OK_BODY
    assert eng.last_tier == 1
    # the minted cookie was injected into the session jar (reuse invariant)
    assert fake.cookies.store.get("cf_clearance") == "TOKEN"


def test_tier1_falls_back_to_browser_html_if_reuse_blocked(monkeypatch):
    from pipeline.engine.tier1 import BrowserResult

    def fake_solve(url, **kw):
        return BrowserResult(html=_OK_BODY, cookies={"datadome": "X"},
                             user_agent="UA", final_url=url, engine="camoufox")

    monkeypatch.setattr("pipeline.engine.tier1.solve_challenge", fake_solve)
    # curl_cffi reuse STILL blocked -> use the genuine browser HTML
    eng, _ = _engine_with([_Resp(403, _CF_BODY)])
    out = eng.fetch_text("https://walled.test/", tier=1)
    assert out == _OK_BODY


def test_tier1_banned_reuse_fails_loud_not_blockpage(monkeypatch):
    # Real-world coches.net case: served reuse is BANNED and the browser ran on
    # the SAME burned IP, so its HTML is the block page. Must FAIL LOUD, never
    # return the block page as content. Error should hint at the pending proxy.
    from pipeline.engine.tier1 import BrowserResult

    block_page = "<html><body>Access Denied: you have been blocked " + "z" * 3000 + "</body></html>"

    def fake_solve(url, **kw):
        return BrowserResult(html=block_page, cookies={"datadome": "X"},
                             user_agent="UA", final_url=url, engine="nodriver")

    monkeypatch.setattr("pipeline.engine.tier1.solve_challenge", fake_solve)
    eng, _ = _engine_with([_Resp(403, "Access Denied you have been blocked " + "z" * 3000)])
    with pytest.raises(FetchError) as ei:
        eng.fetch_text("https://walled.test/", tier=1)
    assert "proxy" in str(ei.value).lower()


def test_tier1_solve_failure_raises_fetcherror(monkeypatch):
    from pipeline.engine.tier1 import Tier1Error

    def boom(url, **kw):
        raise Tier1Error("no browser")

    monkeypatch.setattr("pipeline.engine.tier1.solve_challenge", boom)
    eng, _ = _engine_with([_Resp(200, _OK_BODY)])
    with pytest.raises(FetchError):
        eng.fetch_text("https://walled.test/", tier=1)


def test_tier1_chain_goes_around_a_failing_engine(monkeypatch):
    # nodriver fails -> the chain falls through to camoufox, which succeeds.
    # "If you hit a block, go around it, never stop."
    from pipeline.engine.tier1 import BrowserResult, Tier1Error

    calls = []

    def fake_solve(url, *, engine, **kw):
        calls.append(engine)
        if engine == "nodriver":
            raise Tier1Error("nodriver blocked")
        return BrowserResult(html=_OK_BODY, cookies={"datadome": "OK"},
                             user_agent="UA", final_url=url, engine="camoufox")

    monkeypatch.setattr("pipeline.engine.tier1.solve_challenge", fake_solve)
    eng, _ = _engine_with([_Resp(200, _OK_BODY)])  # camoufox cookie-reuse serves OK
    out = eng.fetch_text("https://walled.test/", tier=1)
    assert out == _OK_BODY
    assert calls == ["nodriver", "camoufox"]  # tried nodriver first, went around


def test_clearance_cache_reused_without_relaunching_browser(monkeypatch):
    # First engine solves and caches the clearance; a SECOND engine on the same
    # host reuses the cached cookie via curl_cffi and never launches a browser.
    from pipeline.engine.tier1 import BrowserResult

    solves = []

    def fake_solve(url, *, engine, **kw):
        solves.append(engine)
        return BrowserResult(html=_OK_BODY, cookies={"cf_clearance": "C1"},
                             user_agent="UA-X", final_url=url, engine=engine)

    monkeypatch.setattr("pipeline.engine.tier1.solve_challenge", fake_solve)

    eng1, _ = _engine_with([_Resp(200, _OK_BODY)])
    assert eng1.fetch_text("https://walled.test/a", tier=1) == _OK_BODY
    assert len(solves) == 1  # one browser solve

    eng2, fake2 = _engine_with([_Resp(200, _OK_BODY)])
    assert eng2.fetch_text("https://walled.test/b", tier=1) == _OK_BODY
    assert len(solves) == 1  # NO second browser launch — cache hit
    assert fake2.cookies.store.get("cf_clearance") == "C1"  # cached cookie applied


def test_proxy_pool_sticky_from_env(monkeypatch):
    from pipeline.engine import proxies as proxy_mod

    monkeypatch.setenv("CARDEEP_PROXIES",
                       "http://u:p@es1.proxy:8000, http://u:p@es2.proxy:8000")
    proxy_mod.reset_default_pool()
    pool = proxy_mod.default_pool()
    assert pool.enabled and len(pool) == 2
    a = pool.sticky_for("dealer:42")
    assert pool.sticky_for("dealer:42") == a  # sticky: same key -> same IP
    proxy_mod.reset_default_pool()


def test_proxy_pool_empty_is_host_ip(monkeypatch):
    from pipeline.engine import proxies as proxy_mod

    monkeypatch.delenv("CARDEEP_PROXIES", raising=False)
    proxy_mod.reset_default_pool()
    pool = proxy_mod.default_pool()
    assert not pool.enabled
    assert pool.next() is None  # cost-zero: goes out on host IP
    proxy_mod.reset_default_pool()
