"""Free proxy harvesting + health-check (cost-zero IP rotation, vía #2).

Vía #1 (headful browser on the host's residential IP) already wins coches.net, so
this is a RESILIENCE layer: when the host IP gets rate-burned at volume, rotate
egress through free proxies instead of stopping. We pull from free public sources,
health-check every candidate against a cheap target, keep only the live ones, and
feed them into the egress ProxyPool. Dead proxies are discarded.

Honest caveat: free proxies are flaky and short-lived; this is a best-effort
rotation pool, not a residential-grade guarantee. It is wired and active, and the
harvest is re-runnable to refresh. Cost is zero.

Sources (no key required):
  * proxyscrape free API   (HTTP/SOCKS lists, country filter)
  * geonode free list      (JSON, country/anonymity filter)
"""
from __future__ import annotations

import concurrent.futures
import json
import time
from dataclasses import dataclass

from curl_cffi import requests as cffi_requests

# Country we care about (egress should look ES for coherence with es-ES headers).
_COUNTRY = "ES"
_HEALTH_URL = "https://api.ipify.org?format=json"
_HEALTH_TIMEOUT = 8.0

_PROXYSCRAPE = (
    "https://api.proxyscrape.com/v4/free-proxy-list/get"
    "?request=display_proxies&protocol=http&proxy_format=protocolipport&format=text"
    f"&country={_COUNTRY}"
)
_PROXYSCRAPE_SOCKS = (
    "https://api.proxyscrape.com/v4/free-proxy-list/get"
    "?request=display_proxies&protocol=socks5&proxy_format=protocolipport&format=text"
    f"&country={_COUNTRY}"
)
_GEONODE = (
    "https://proxylist.geonode.com/api/proxy-list"
    f"?limit=100&page=1&sort_by=lastChecked&sort_type=desc&country={_COUNTRY}"
)
# Raw GitHub lists (country-mixed; filtered to ES later only when possible — these
# add volume so the ES health-check has more candidates to find a live one).
_GITHUB_RAW = (
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
)


@dataclass(frozen=True)
class ProxyHealth:
    url: str
    alive: bool
    latency_ms: int | None = None
    egress_ip: str | None = None
    tier1_ok: bool = False        # passed a real Tier-1 target (not just ipify)

    @property
    def score(self) -> float:
        """Higher is better. Dead=0; alive scored by latency, big bonus for Tier-1."""
        if not self.alive:
            return 0.0
        lat = self.latency_ms if self.latency_ms is not None else 10000
        base = max(0.0, 1.0 - min(lat, 10000) / 10000.0)  # 0..1, faster = higher
        return base + (1.0 if self.tier1_ok else 0.0)     # Tier-1 pass dominates


def fetch_candidates(timeout: float = 15.0) -> list[str]:
    """Pull candidate proxy URLs (http://ip:port) from free sources. Best-effort."""
    out: list[str] = []
    try:
        r = cffi_requests.get(_PROXYSCRAPE, impersonate="chrome131", timeout=timeout)
        if r.status_code == 200:
            for line in r.text.splitlines():
                line = line.strip()
                if line and "://" in line:
                    out.append(line)
                elif line:
                    out.append(f"http://{line}")
    except Exception:  # noqa: BLE001 - source down is non-fatal
        pass
    try:
        r = cffi_requests.get(_PROXYSCRAPE_SOCKS, impersonate="chrome131", timeout=timeout)
        if r.status_code == 200:
            for line in r.text.splitlines():
                line = line.strip()
                if line:
                    out.append(line if "://" in line else f"socks5://{line}")
    except Exception:  # noqa: BLE001
        pass
    try:
        r = cffi_requests.get(_GEONODE, impersonate="chrome131", timeout=timeout)
        if r.status_code == 200:
            data = json.loads(r.text).get("data", [])
            for row in data:
                ip, port = row.get("ip"), row.get("port")
                protos = row.get("protocols") or ["http"]
                if ip and port:
                    out.append(f"{protos[0]}://{ip}:{port}")
    except Exception:  # noqa: BLE001
        pass
    for src in _GITHUB_RAW:
        try:
            r = cffi_requests.get(src, impersonate="chrome131", timeout=timeout)
            if r.status_code == 200:
                for line in r.text.splitlines():
                    line = line.strip()
                    if line and ":" in line:
                        out.append(line if "://" in line else f"http://{line}")
        except Exception:  # noqa: BLE001
            pass
    # de-dup, preserve order
    seen: set[str] = set()
    return [p for p in out if not (p in seen or seen.add(p))]


def health_check(proxy: str, *, test_url: str = _HEALTH_URL,
                 timeout: float = _HEALTH_TIMEOUT,
                 tier1_url: str | None = None) -> ProxyHealth:
    """Verify a proxy carries traffic; capture egress IP + latency.

    When `tier1_url` is given, ALSO fetch a real Tier-1 target through the proxy and
    mark `tier1_ok` if it returns genuine (non-blocked) content — a far stronger
    signal than ipify (an alive proxy that a WAF already bans is useless to us).
    """
    from pipeline.engine import ban_detector

    t0 = time.monotonic()
    try:
        r = cffi_requests.get(test_url, impersonate="chrome131", timeout=timeout,
                              proxies={"http": proxy, "https": proxy})
        if r.status_code != 200:
            return ProxyHealth(proxy, False)
        ip = None
        try:
            ip = json.loads(r.text).get("ip")
        except Exception:  # noqa: BLE001
            ip = r.text.strip()[:40]
        latency = int((time.monotonic() - t0) * 1000)
        tier1_ok = False
        if tier1_url:
            try:
                r2 = cffi_requests.get(tier1_url, impersonate="chrome131",
                                       timeout=timeout,
                                       proxies={"http": proxy, "https": proxy})
                v = ban_detector.classify(r2.status_code, r2.text, dict(r2.headers))
                tier1_ok = (r2.status_code == 200 and v == ban_detector.Verdict.OK)
            except Exception:  # noqa: BLE001
                tier1_ok = False
        return ProxyHealth(proxy, True, latency, ip, tier1_ok)
    except Exception:  # noqa: BLE001 - dead proxy
        pass
    return ProxyHealth(proxy, False)


def harvest_alive(*, max_candidates: int = 60, max_workers: int = 20,
                  timeout: float = _HEALTH_TIMEOUT,
                  tier1_url: str | None = None) -> list[ProxyHealth]:
    """Fetch candidates, health-check in parallel, return live ones SCORED (best first).

    With `tier1_url`, alive proxies are also validated against a real Tier-1 target
    and ranked above plain-alive ones (score puts tier1_ok first, then latency).
    """
    candidates = fetch_candidates()[:max_candidates]
    if not candidates:
        return []
    alive: list[ProxyHealth] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(health_check, p, timeout=timeout, tier1_url=tier1_url): p
                for p in candidates}
        for fut in concurrent.futures.as_completed(futs):
            h = fut.result()
            if h.alive:
                alive.append(h)
    alive.sort(key=lambda h: h.score, reverse=True)  # best score first
    return alive


def refresh_pool_urls(**kw) -> list[str]:
    """Convenience: harvest and return just the alive proxy URLs (fastest first)."""
    return [h.url for h in harvest_alive(**kw)]
