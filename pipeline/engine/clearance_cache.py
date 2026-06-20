"""Per-host clearance-cookie cache (multiplies the value of one browser solve).

Solving an active challenge in a real browser is the expensive step. Once solved,
the minted clearance cookie (`cf_clearance` / `datadome` / `_abck`) is valid for a
window — so a SECOND drain against the same host should NOT launch a browser
again, it should replay the cached cookie + UA from cheap curl_cffi. This cache
holds, per host, the (cookies, user_agent, expiry) of the last successful solve so
every FetchEngine in the process reuses it until it expires.

The reuse invariant still holds: we store the EXACT UA the browser presented and
hand it back with the cookies, so the caller pins them together. IP is the
caller's responsibility (sticky proxy); a cache hit under a different egress IP
may be rejected, which the cascade detects and re-solves.

In-memory, process-local, TTL-bounded. Not persisted (a restart re-solves — safe,
never serves a stale cookie). Thread-safe via a simple lock.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass

# Clearance cookies typically live tens of minutes; keep a conservative default
# so we never replay a cookie the WAF has already rotated out.
_DEFAULT_TTL = 25 * 60.0  # seconds

_lock = threading.Lock()


@dataclass(frozen=True)
class Clearance:
    cookies: dict
    user_agent: str
    expires_at: float


_store: dict[str, Clearance] = {}


def get(host: str, *, now: float | None = None) -> Clearance | None:
    """Return a non-expired clearance for `host`, or None."""
    t = now if now is not None else time.monotonic()
    with _lock:
        c = _store.get(host)
        if c is None:
            return None
        if c.expires_at <= t:
            _store.pop(host, None)
            return None
        return c


def put(host: str, cookies: dict, user_agent: str, *,
        ttl: float = _DEFAULT_TTL, now: float | None = None) -> None:
    """Cache a successful solve for `host`. Empty cookies are ignored (no solve)."""
    if not cookies:
        return
    t = now if now is not None else time.monotonic()
    with _lock:
        _store[host] = Clearance(cookies=dict(cookies), user_agent=user_agent or "",
                                 expires_at=t + ttl)


def invalidate(host: str) -> None:
    """Drop a host's clearance (e.g. the cached cookie just got rejected)."""
    with _lock:
        _store.pop(host, None)


def clear() -> None:
    """Wipe the whole cache (used by tests for isolation)."""
    with _lock:
        _store.clear()
