"""SU-D2: In-memory response cache for stable read endpoints.

Design
------
- Uses ``cachetools.TTLCache`` — a bounded, LRU-evicting TTL dict that is
  100 % in-process (no Redis, no infra coupling, €0).
- Cache key  = METHOD + PATH + sorted query string (deterministic).
- TTL        = CACHE_TTL_SECONDS (module constant, default 60 s).
- Max size   = CACHE_MAXSIZE entries (module constant, default 512).
  Prevents unbounded RAM growth on the host (limited free RAM).
- Only 2xx responses are cached; errors are never cached.
- A ``meta.cache`` indicator ("hit" | "miss") is injected into every
  response that passes through the cache layer so consumers can observe
  whether they received a cached copy.

Thread/async safety
-------------------
The FastAPI worker runs in a single OS process (uvicorn, single-worker).
``cachetools.TTLCache`` is NOT thread-safe, but because:
  a) FastAPI routes are async (cooperative concurrency, one GIL holder),
  b) the cache operations are O(1) and atomically within a single await,
the plain dict-like TTLCache is safe in this deployment model.
If multi-process uvicorn is ever used, promote to a shared-memory or
Redis-backed cache — document that decision here.

Usage
-----
    from services.api.cache import try_cache_get, cache_set

    cached = try_cache_get(request)
    if cached is not None:
        return cached
    response = ... # expensive DB call
    return cache_set(request, response)
"""
from __future__ import annotations

import json
from typing import Any

from cachetools import TTLCache
from fastapi import Request
from fastapi.responses import JSONResponse

# ---------------------------------------------------------------------------
# Module-level constants — single source of truth, no magic numbers inline.
# ---------------------------------------------------------------------------

CACHE_TTL_SECONDS: int = 60
"""Seconds before a cached entry is considered stale."""

CACHE_MAXSIZE: int = 512
"""Maximum number of entries in the cache. LRU eviction kicks in above this."""

# Endpoints whose responses change between harvests (not per-request).
# These are the only paths eligible for caching.
CACHEABLE_PATH_PREFIXES: tuple[str, ...] = (
    "/geo/",          # /geo/{province}/tree, /geo/completeness, /geo/{p}/entities,
                      # /geo/{p}/municipalities/{m}/entities
    "/entities/",     # /entities/{cdp}/inventory — changes only after harvest runs
    "/platforms/",    # /platforms/{cdp}/inventory — stable within a harvest window
    "/market/",       # /market/segments/.../stats, /market/provinces/demand — change
                      # only when a NEW market_stat_run is published (batch cadence,
                      # not per-request), 01-market-intelligence F3.
)

# Paths that MUST NOT be cached regardless of prefix match.
# /health has a freshness contract (liveness probe).
CACHE_EXCLUDED_PATHS: tuple[str, ...] = (
    "/health",
    "/alerts",        # alert state can change any time
    "/sources",       # source health is near-real-time monitoring data
)

# ---------------------------------------------------------------------------
# The shared cache instance — module singleton.
# ---------------------------------------------------------------------------

_cache: TTLCache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL_SECONDS)


def _cache_key(request: Request) -> str:
    """Build a deterministic string key from method + path + sorted query params.

    NOTE (audit P2 E-cache-key): this key has NO auth/tenant dimension. Safe under the current
    single shared CARDEEP_API_KEY (require_api_key runs before the body is read, so there is no
    anonymous bypass), but introducing per-tenant API keys WITHOUT adding the key/tenant-id to this
    key would let tenant A be served tenant B's cached body. Multi-tenant auth MUST extend this key.
    """
    method = request.method.upper()
    path = request.url.path
    # Sort query params for key stability regardless of client parameter order.
    qs = "&".join(
        f"{k}={v}"
        for k, v in sorted(request.query_params.multi_items())
    )
    return f"{method}:{path}?{qs}" if qs else f"{method}:{path}"


def is_cacheable(request: Request) -> bool:
    """Return True when this request is eligible for caching."""
    if request.method.upper() != "GET":
        return False
    path = request.url.path
    if any(path.startswith(exc) for exc in CACHE_EXCLUDED_PATHS):
        return False
    if path in CACHE_EXCLUDED_PATHS:
        return False
    return any(path.startswith(pfx) for pfx in CACHEABLE_PATH_PREFIXES)


def try_cache_get(request: Request) -> JSONResponse | None:
    """Return a cached JSONResponse with ``meta.cache = "hit"``, or None on miss.

    Returns None (miss) when:
      - The path is not cacheable.
      - The entry has expired (TTLCache handles this transparently).
      - The cache is empty for this key.
    """
    if not is_cacheable(request):
        return None
    key = _cache_key(request)
    entry = _cache.get(key)
    if entry is None:
        return None
    # Inject cache indicator into a copy of the payload — do NOT mutate the
    # stored entry, as it is shared across requests.
    payload: dict[str, Any] = dict(entry)
    meta = payload.get("meta")
    if isinstance(meta, dict):
        payload["meta"] = {**meta, "cache": "hit"}
    else:
        # meta is None or some other type — wrap it.
        payload["meta"] = {"cache": "hit"}
    return JSONResponse(payload)


def cache_set(request: Request, response: JSONResponse) -> JSONResponse:
    """Store *response* in the cache (if cacheable) and return a copy with
    ``meta.cache = "miss"`` added to the envelope.

    Only stores 2xx responses. Error responses (4xx, 5xx) are never cached.
    Mutates a copy of the body — the original *response* object is not changed.
    """
    # Decode the response body. JSONResponse stores bytes.
    try:
        payload: dict[str, Any] = json.loads(response.body)
    except Exception:
        # If body is somehow not valid JSON, pass through unchanged.
        return response

    # Only cache successful (ok=True) 2xx responses.
    if not (isinstance(payload.get("ok"), bool) and payload["ok"]):
        return response

    if is_cacheable(request):
        key = _cache_key(request)
        # Store the raw payload (no cache indicator) for future hit decoration.
        _cache[key] = payload

    # Return a new JSONResponse with cache indicator = "miss".
    miss_payload = dict(payload)
    meta = miss_payload.get("meta")
    if isinstance(meta, dict):
        miss_payload["meta"] = {**meta, "cache": "miss"}
    else:
        miss_payload["meta"] = {"cache": "miss"}
    return JSONResponse(miss_payload)


def cache_clear() -> None:
    """Empty the cache. Exposed for tests that need deterministic state."""
    _cache.clear()
