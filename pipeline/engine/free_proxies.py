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
_GEONODE = (
    "https://proxylist.geonode.com/api/proxy-list"
    f"?limit=100&page=1&sort_by=lastChecked&sort_type=desc&country={_COUNTRY}"
)


@dataclass(frozen=True)
class ProxyHealth:
    url: str
    alive: bool
    latency_ms: int | None = None
    egress_ip: str | None = None


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
    # de-dup, preserve order
    seen: set[str] = set()
    return [p for p in out if not (p in seen or seen.add(p))]


def health_check(proxy: str, *, test_url: str = _HEALTH_URL,
                 timeout: float = _HEALTH_TIMEOUT) -> ProxyHealth:
    """Verify a proxy actually carries traffic; capture egress IP + latency."""
    t0 = time.monotonic()
    try:
        r = cffi_requests.get(test_url, impersonate="chrome131", timeout=timeout,
                              proxies={"http": proxy, "https": proxy})
        if r.status_code == 200:
            ip = None
            try:
                ip = json.loads(r.text).get("ip")
            except Exception:  # noqa: BLE001
                ip = r.text.strip()[:40]
            return ProxyHealth(proxy, True, int((time.monotonic() - t0) * 1000), ip)
    except Exception:  # noqa: BLE001 - dead proxy
        pass
    return ProxyHealth(proxy, False)


def harvest_alive(*, max_candidates: int = 60, max_workers: int = 20,
                  timeout: float = _HEALTH_TIMEOUT) -> list[ProxyHealth]:
    """Fetch candidates and return only the ones that pass health-check, alive."""
    candidates = fetch_candidates()[:max_candidates]
    if not candidates:
        return []
    alive: list[ProxyHealth] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(health_check, p, timeout=timeout): p for p in candidates}
        for fut in concurrent.futures.as_completed(futs):
            h = fut.result()
            if h.alive:
                alive.append(h)
    alive.sort(key=lambda h: h.latency_ms or 1 << 30)
    return alive


def refresh_pool_urls(**kw) -> list[str]:
    """Convenience: harvest and return just the alive proxy URLs (fastest first)."""
    return [h.url for h in harvest_alive(**kw)]
