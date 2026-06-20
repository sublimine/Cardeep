"""Egress proxy pool (cost-zero by default; aggressive when credentials exist).

The clearance cookie is bound to the egress IP, so the most aggressive posture
needs a pool of residential ES IPs to (a) survive IP-bound WAFs and (b) rotate
away from a burned IP. We DO NOT hardcode or pay for anything here: the pool reads
`CARDEEP_PROXIES` (comma-separated proxy URLs) from the environment. When it is
unset the pool is empty and every fetch goes out on the host IP — zero cost, zero
behavior change. The seam is ready so a residential ES credential drops in via env
with no code change (PENDING-CREDENTIAL).

Format of CARDEEP_PROXIES entries: `http://user:pass@host:port` (or `socks5://...`).
Rotation is round-robin; `sticky_for(key)` pins one proxy to a key (e.g. a host or
dealer) so a whole drain keeps one IP — required for cookie reuse.
"""
from __future__ import annotations

import itertools
import os
import threading

_ENV_VAR = "CARDEEP_PROXIES"


class ProxyPool:
    def __init__(self, proxies: list[str] | None = None) -> None:
        if proxies is None:
            raw = os.environ.get(_ENV_VAR, "")
            proxies = [p.strip() for p in raw.split(",") if p.strip()]
        self._proxies = list(proxies)
        self._cycle = itertools.cycle(self._proxies) if self._proxies else None
        self._sticky: dict[str, str] = {}
        self._lock = threading.Lock()

    @property
    def enabled(self) -> bool:
        return bool(self._proxies)

    def __len__(self) -> int:
        return len(self._proxies)

    def next(self) -> str | None:
        """Round-robin a proxy URL, or None when the pool is empty (host IP)."""
        if not self._cycle:
            return None
        with self._lock:
            return next(self._cycle)

    def sticky_for(self, key: str) -> str | None:
        """Pin one proxy to `key` for the life of the process (sticky session)."""
        if not self._proxies:
            return None
        with self._lock:
            if key not in self._sticky:
                self._sticky[key] = next(self._cycle)  # type: ignore[arg-type]
            return self._sticky[key]


# Process-wide default pool (reads env at import; cheap).
_default_pool: ProxyPool | None = None


def default_pool() -> ProxyPool:
    global _default_pool
    if _default_pool is None:
        _default_pool = ProxyPool()
    return _default_pool


def reset_default_pool() -> None:
    """Re-read the environment (tests / after setting CARDEEP_PROXIES)."""
    global _default_pool
    _default_pool = None
