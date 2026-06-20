"""Per-entity source route-around (vía #4)."""
from pipeline.engine.fetch import FetchError
from pipeline.engine import source_fallback as sf


def test_own_site_tried_before_hard_marketplace():
    cands = sf.build_candidates({
        "coches_net": "https://www.coches.net/dealer/x",
        "own_site": "https://midealer.es/stock",
    })
    ordered = [c.source_key for c in sf.order_candidates(cands)]
    assert ordered[0] == "own_site"
    assert ordered[-1] == "coches_net"
    # hard marketplace escalates to Tier-1, own site stays Tier-0
    by_key = {c.source_key: c for c in cands}
    assert by_key["coches_net"].tier == 1
    assert by_key["own_site"].tier == 0


def test_route_around_falls_through_to_next_source():
    cands = sf.build_candidates({
        "own_site": "https://midealer.es/stock",
        "autocasion": "https://www.autocasion.com/dealer/x",
    })

    def fetch_text(url, *, tier=0):
        if "midealer.es" in url:
            raise FetchError("own site down")
        return "<html>real inventory</html>"

    res = sf.fetch_first_available(cands, fetch_text=fetch_text)
    assert res.ok
    assert res.resolved_source == "autocasion"   # went around the dead own_site
    assert ("own_site", "error:own site down"[:80]) in [
        (s, e) for s, e in res.attempts if s == "own_site"]


def test_first_available_wins_no_further_calls():
    cands = sf.build_candidates({"own_site": "https://midealer.es/stock",
                                 "coches_net": "https://www.coches.net/x"})
    calls = []

    def fetch_text(url, *, tier=0):
        calls.append(url)
        return "<html>ok</html>"

    res = sf.fetch_first_available(cands, fetch_text=fetch_text)
    assert res.resolved_source == "own_site"
    assert len(calls) == 1  # stopped at first success, never hit coches.net


def test_all_sources_fail_returns_not_ok():
    cands = sf.build_candidates({"own_site": "https://a.es", "coches_net": "https://b.net"})

    def fetch_text(url, *, tier=0):
        raise FetchError("blocked")

    res = sf.fetch_first_available(cands, fetch_text=fetch_text)
    assert not res.ok
    assert res.resolved_source is None
    assert len(res.attempts) == 2  # both tried, both recorded
