"""Free-proxy harvesting: scoring + parsing (mocked) — vía #2/#3."""
from pipeline.engine import free_proxies as fp


def test_score_orders_tier1_above_fast_alive_above_dead():
    dead = fp.ProxyHealth("http://d", alive=False)
    alive_slow = fp.ProxyHealth("http://s", alive=True, latency_ms=5000)
    alive_fast = fp.ProxyHealth("http://f", alive=True, latency_ms=200)
    tier1 = fp.ProxyHealth("http://t", alive=True, latency_ms=3000, tier1_ok=True)
    ranked = sorted([dead, alive_slow, alive_fast, tier1],
                    key=lambda h: h.score, reverse=True)
    assert ranked[0].url == "http://t"      # Tier-1 pass dominates
    assert ranked[-1].url == "http://d"     # dead last
    assert alive_fast.score > alive_slow.score
    assert dead.score == 0.0


def test_fetch_candidates_parses_and_dedups(monkeypatch):
    class _R:
        def __init__(self, text): self.status_code = 200; self.text = text
    calls = {"n": 0}

    def fake_get(url, **kw):
        calls["n"] += 1
        if "proxyscrape" in url and "socks5" not in url:
            return _R("http://1.1.1.1:80\n2.2.2.2:8080\n")   # bare ip:port -> http://
        if "socks5" in url:
            return _R("3.3.3.3:1080\n")
        if "geonode" in url:
            return _R('{"data":[{"ip":"4.4.4.4","port":"3128","protocols":["http"]}]}')
        return _R("1.1.1.1:80\n5.5.5.5:80\n")   # github raw (dup of 1.1.1.1)

    monkeypatch.setattr(fp.cffi_requests, "get", fake_get)
    cands = fp.fetch_candidates()
    assert "http://1.1.1.1:80" in cands
    assert "http://2.2.2.2:8080" in cands
    assert "socks5://3.3.3.3:1080" in cands
    assert "http://4.4.4.4:3128" in cands
    assert "http://5.5.5.5:80" in cands
    # 1.1.1.1 appears in two sources but must be de-duped
    assert cands.count("http://1.1.1.1:80") == 1


def test_harvest_alive_sorts_by_score(monkeypatch):
    monkeypatch.setattr(fp, "fetch_candidates", lambda **_kw: ["http://a", "http://b", "http://c"])

    def fake_health(proxy, *, timeout=8.0, tier1_url=None, **_kw):
        table = {
            "http://a": fp.ProxyHealth("http://a", True, 4000, "1.1.1.1", False),
            "http://b": fp.ProxyHealth("http://b", True, 500, "2.2.2.2", True),  # tier1 ok
            "http://c": fp.ProxyHealth("http://c", False),
        }
        return table[proxy]

    monkeypatch.setattr(fp, "health_check", fake_health)
    alive = fp.harvest_alive(max_candidates=3, max_workers=3)
    assert [h.url for h in alive] == ["http://b", "http://a"]  # tier1 first, dead dropped
