"""DealerProbe async engine — concurrent-fetch invariants (perf re-architecture).

The PDP fetch went from sequential to concurrent (curl_cffi.AsyncSession + per-host semaphore).
These tests pin the invariants the design panel flagged as CRITICAL/HIGH so the speedup never
costs correctness or politeness:
  1. parity   — concurrent parse yields the SAME vehicles in the SAME (frontier) order
  2. per-host — never more than pdp_conc live connections to one host (politeness / no ban)
  3. status   — live/dead/walled decided in SEQUENTIAL discovery, immune to concurrent PDP races
  4. isolation— one broken PDP is dropped, never tumbles the whole dealer
  5. ssl-retry— _afetch retries with verify=False on a curl TLS error (kept from the sync engine)
"""
import asyncio

import pytest

from pipeline.platform.dealerprobe_wholesale import _afetch, probe_dealer

pytestmark = pytest.mark.unit


def _run(c):
    return asyncio.run(c)


def _pdp(price, url):
    return (f'<script type="application/ld+json">{{"@type":"Car","name":"Car {price}",'
            f'"brand":"Seat","model":"Leon","offers":{{"price":"{price}"}},"url":"{url}"}}</script>')


def _make_gf(pages, tracker=None, raise_on=None, delay=0.0):
    """Fake async fetch over a {url: body|None} map. Sets state['last_status']; optionally tracks
    concurrent in-flight calls, raises for a url substring, and sleeps to let concurrency build."""
    state = {"last_status": None}

    async def gf(url):
        if tracker is not None:
            tracker["cur"] += 1
            tracker["max"] = max(tracker["max"], tracker["cur"])
        try:
            if delay:
                await asyncio.sleep(delay)
            if raise_on and raise_on in url:
                raise RuntimeError("boom in PDP")
            body = pages.get(url)
            state["last_status"] = 200 if body is not None else 404
            return body
        finally:
            if tracker is not None:
                tracker["cur"] -= 1

    return gf, state


def _sitemap_pages(n):
    locs = [f"https://x.es/coches/seat-leon-2019-{90000+i}-{100+i}" for i in range(n)]
    sm = "<urlset>" + "".join(f"<url><loc>{u}</loc></url>" for u in locs) + "</urlset>"
    pages = {
        "https://x.es/robots.txt": "Sitemap: https://x.es/sitemap.xml\n",
        "https://x.es/sitemap.xml": sm,
    }
    for i, u in enumerate(locs):
        pages[u] = _pdp(10000 + i, u)
    return pages, locs


def test_concurrent_parse_preserves_order_and_set():
    pages, locs = _sitemap_pages(6)
    gf, state = _make_gf(pages)
    summary, host, vehicles = _run(probe_dealer(gf, state, "x.es", cap=400, pdp_conc=4, pdp_delay=0))
    assert summary["status"] == "live" and host == "x.es"
    assert [v["url"] for v in vehicles] == locs          # gather preserves frontier order
    assert [int(v["price"]) for v in vehicles] == [10000 + i for i in range(6)]


def test_per_host_concurrency_capped():
    pages, _ = _sitemap_pages(10)
    tracker = {"cur": 0, "max": 0}
    gf, state = _make_gf(pages, tracker=tracker, delay=0.01)
    _run(probe_dealer(gf, state, "x.es", cap=400, pdp_conc=3, pdp_delay=0))
    assert tracker["max"] == 3                            # never exceeds the per-host semaphore


def test_status_live_despite_403_on_pdps():
    # discovery succeeds (200) -> frontier; PDPs all 403. status must stay 'live' (frozen pre-PDP),
    # never 'walled' — the concurrent PDPs must NOT corrupt the classification.
    pages, locs = _sitemap_pages(4)
    for u in locs:
        pages[u] = None                                  # PDP 404/403-ish -> no vehicle
    gf, state = _make_gf(pages)
    summary, _, vehicles = _run(probe_dealer(gf, state, "x.es", cap=400, pdp_conc=4, pdp_delay=0))
    assert summary["status"] == "live" and vehicles == []


def test_status_walled_when_discovery_403():
    async def gf(url):
        state["last_status"] = 403
        return None
    state = {"last_status": None}
    summary, _, vehicles = _run(probe_dealer(gf, state, "dead.es", cap=400, pdp_conc=4, pdp_delay=0))
    assert summary["status"] == "walled" and vehicles == []


def test_one_broken_pdp_does_not_kill_dealer():
    pages, locs = _sitemap_pages(8)
    gf, state = _make_gf(pages, raise_on=locs[3])         # the 4th PDP raises
    summary, _, vehicles = _run(probe_dealer(gf, state, "x.es", cap=400, pdp_conc=4, pdp_delay=0))
    assert summary["status"] == "live"
    assert len(vehicles) == 7                             # 8 - 1 broken, dealer survives
    assert all(v["url"] != locs[3] for v in vehicles)


def test_transient_pdp_failure_is_retried_and_recovered():
    # a PDP that fails (None) the FIRST time but succeeds the SECOND must be recovered — this is the
    # transient reset/timeout that concurrency causes (conc=1 fetches 100%, conc=6 dropped ~10%).
    pages, locs = _sitemap_pages(5)
    flaky = locs[2]
    seen = {"n": 0}

    async def gf(url):
        state["last_status"] = 200
        if url == flaky:
            seen["n"] += 1
            if seen["n"] == 1:                       # first hit on the flaky PDP -> transient fail
                state["last_status"] = None
                return None
        return pages.get(url)

    state = {"last_status": None}
    summary, _, vehicles = _run(probe_dealer(gf, state, "x.es", cap=400, pdp_conc=4, pdp_delay=0))
    assert summary["status"] == "live"
    assert len(vehicles) == 5                         # the flaky PDP recovered on retry, none lost
    assert any(v["url"] == flaky for v in vehicles)


def test_afetch_retries_with_verify_false_on_tls_error():
    class _CurlError(Exception):
        pass

    class _FakeSession:
        def __init__(self):
            self.verify_args = []

        async def get(self, url, timeout=None, verify=True):
            self.verify_args.append(verify)
            if verify:
                raise _CurlError("SSL certificate problem: self signed certificate")
            return type("R", (), {"status_code": 200, "text": "<html>ok</html>"})()

    sess, state = _FakeSession(), {"last_status": None}
    body = _run(_afetch(sess, "https://badcert.es/c/1", state))
    assert body == "<html>ok</html>"
    assert sess.verify_args == [True, False]              # first default, then retry verify=False
    assert state["last_status"] == 200
