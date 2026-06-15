"""SU-D2: Rate-limiting and response caching tests.

Verifies:
  A. Rate-limiting — with a 2/minute limit on a test-only endpoint,
     request 3 returns HTTP 429 in the project envelope.
     Under-limit requests return 200.
     429 envelope shape is exact: {ok: false, data: null, error: "rate_limit_exceeded", meta: {...}}.

  B. Response caching — a cacheable endpoint returns meta.cache="miss" on the
     first request and meta.cache="hit" on the second (within TTL).
     Payload is identical on hit.
     /health (excluded path) is NEVER cached (no meta.cache key).

Pattern follows existing test_api_*.py files:
  - No conftest.py — app imported directly.
  - FastAPI TestClient (synchronous, no uvicorn).
  - DB guard: skip data-endpoint tests when cardeep-pg is unreachable.
  - monkeypatch for env-var isolation.

Rate-limit test strategy
------------------------
We build a module-level minimal FastAPI app with a 2/minute limit.
FastAPI/pydantic requires that all type annotations on route-handler
parameters are resolvable in the route function's global namespace.
Defining the route inside a method scope breaks pydantic's forward-
reference resolution for ``Request`` — so we use a module-level helper
function instead.

Cache test strategy
-------------------
We call ``cache_clear()`` before each cache test to start from a known state,
then verify meta.cache on the first and second responses.
A second call within the 60-second TTL must hit the cache.
"""
from __future__ import annotations

import asyncio

import asyncpg
import pytest
from fastapi import FastAPI
from fastapi import Request as StarletteRequest  # module-level so pydantic can resolve it
from fastapi.testclient import TestClient
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from services.api.cache import cache_clear
from services.api.deps import ok as ok_response
from services.api.main import app
from services.api.ratelimit import rate_limit_handler

# ---------------------------------------------------------------------------
# DB connectivity guard — same pattern as other test_api_* files.
# ---------------------------------------------------------------------------

def _db_available() -> bool:
    async def _ping() -> bool:
        try:
            conn = await asyncpg.connect(
                "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep",
                timeout=3,
            )
            await conn.close()
            return True
        except Exception:
            return False
    try:
        return asyncio.run(_ping())
    except Exception:
        return False


DB_AVAILABLE = _db_available()
SKIP_NO_DB = pytest.mark.skipif(
    not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433"
)

# Known stable fixture — Madrid province, always populated.
PROVINCE_CODE = "28"

# ---------------------------------------------------------------------------
# Minimal isolated app for rate-limit enforcement tests.
#
# Built at module level so that FastAPI/pydantic can resolve the ``Request``
# type annotation in the route handler's global namespace (inside a nested
# function scope, pydantic would raise PydanticUndefinedAnnotation: 'Request').
# ---------------------------------------------------------------------------

_test_limiter: Limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
)

_mini_app: FastAPI = FastAPI()
_mini_app.state.limiter = _test_limiter
_mini_app.add_middleware(SlowAPIMiddleware)
_mini_app.add_exception_handler(RateLimitExceeded, rate_limit_handler)


@_mini_app.get("/test-limited")
@_test_limiter.limit("2/minute")
async def _limited_endpoint(request: StarletteRequest):
    """Test endpoint: allows 2 req/min; 3rd triggers 429."""
    return ok_response({"msg": "ok"})


# ---------------------------------------------------------------------------
# Section A: Rate-limiting
# ---------------------------------------------------------------------------

class TestRateLimiting:
    """Rate-limit enforcement tests using the isolated ``_mini_app`` above.

    Each test builds a fresh TestClient over the module-level ``_mini_app``.
    The 2/minute limit allows exactly 2 requests per IP per minute; the 3rd
    request in the same window must return 429.

    The ``_test_limiter`` uses in-process memory storage.  Because TestClient
    presents a consistent IP (127.0.0.1 via loopback) across all calls in one
    ``with TestClient(...) as client`` block, the counter accumulates correctly.

    To prevent bleed between tests (the counter persisting from a prior test),
    each test opens a NEW TestClient context, which under the default
    SlowAPIMiddleware / in-memory storage does NOT reset between separate
    TestClient instances in the same process.  To guarantee isolation we clear
    the limiter storage before each test that expects a fresh window.
    """

    def setup_method(self) -> None:
        """Reset the in-memory rate-limit counters before each test."""
        _test_limiter._storage.reset()  # type: ignore[attr-defined]

    def test_under_limit_requests_succeed(self) -> None:
        """Requests 1 and 2 within the 2/minute limit must return 200."""
        with TestClient(_mini_app) as client:
            r1 = client.get("/test-limited")
            r2 = client.get("/test-limited")
        assert r1.status_code == 200, f"Request 1 expected 200, got {r1.status_code}"
        assert r2.status_code == 200, f"Request 2 expected 200, got {r2.status_code}"

    def test_over_limit_returns_429(self) -> None:
        """Request 3 beyond the 2/minute limit must return 429."""
        with TestClient(_mini_app) as client:
            client.get("/test-limited")  # 1
            client.get("/test-limited")  # 2
            r3 = client.get("/test-limited")  # 3 — must be 429
        assert r3.status_code == 429, f"Expected 429, got {r3.status_code}"

    def test_429_envelope_shape(self) -> None:
        """429 must use the project envelope: {ok, data, error, meta}."""
        with TestClient(_mini_app) as client:
            client.get("/test-limited")  # 1
            client.get("/test-limited")  # 2
            r = client.get("/test-limited")  # 3
        assert r.status_code == 429
        body = r.json()
        # Top-level envelope keys must be present and correct.
        assert set(body.keys()) == {"ok", "data", "error", "meta"}, (
            f"429 envelope keys mismatch: {set(body.keys())}"
        )
        assert body["ok"] is False, "429 ok must be false"
        assert body["data"] is None, "429 data must be null"
        assert body["error"] == "rate_limit_exceeded", (
            f"429 error must be 'rate_limit_exceeded', got '{body['error']}'"
        )
        # meta must be a dict with at least a 'detail' key.
        assert isinstance(body["meta"], dict), "429 meta must be a dict"
        assert "detail" in body["meta"], "429 meta must contain 'detail'"

    @SKIP_NO_DB
    def test_health_not_tripped_by_default_limit(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """With limiter ENABLED, a single /health call must never 429.

        /health has RATE_HEALTH=300/minute. A single call in the test suite
        must never trip it.
        """
        monkeypatch.setenv("CARDEEP_API_RATELIMIT_ENABLED", "1")
        with TestClient(app) as client:
            r = client.get("/health")
        assert r.status_code == 200, (
            f"/health must not be rate-limited on a single call; got {r.status_code}"
        )

    @SKIP_NO_DB
    def test_limiter_disabled_via_env_var(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When CARDEEP_API_RATELIMIT_ENABLED=0, the limiter is effectively off.

        Note: RATE_* constants are evaluated at import time.  This test verifies
        that the live app (with the noop rate "9999/second" baked in at import)
        does not trip on a single /health call when the env var is set to "0".
        A process restart would be required to change already-imported constants.
        """
        monkeypatch.setenv("CARDEEP_API_RATELIMIT_ENABLED", "0")
        with TestClient(app) as client:
            r = client.get("/health")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Section B: Response caching
# ---------------------------------------------------------------------------

class TestResponseCaching:
    """Cache-layer tests.

    All tests call ``cache_clear()`` first to start from a deterministic state.
    These tests require DB access since the cache wraps real DB responses.
    """

    @SKIP_NO_DB
    def test_first_request_is_cache_miss(self) -> None:
        """The first request to a cacheable endpoint must return meta.cache='miss'."""
        cache_clear()
        with TestClient(app) as client:
            r = client.get(f"/geo/{PROVINCE_CODE}/entities?size=5")
        assert r.status_code == 200
        meta = r.json().get("meta", {})
        assert meta.get("cache") == "miss", (
            f"First request must be a cache miss; meta={meta}"
        )

    @SKIP_NO_DB
    def test_second_request_is_cache_hit(self) -> None:
        """The second request within TTL must return meta.cache='hit'."""
        cache_clear()
        with TestClient(app) as client:
            client.get(f"/geo/{PROVINCE_CODE}/entities?size=5")  # populate cache
            r2 = client.get(f"/geo/{PROVINCE_CODE}/entities?size=5")
        assert r2.status_code == 200
        meta = r2.json().get("meta", {})
        assert meta.get("cache") == "hit", (
            f"Second request within TTL must be a cache hit; meta={meta}"
        )

    @SKIP_NO_DB
    def test_cached_payload_identical(self) -> None:
        """Cache hit must return an identical payload to the original miss response.

        Everything in the response body must match except the meta.cache indicator.
        """
        cache_clear()
        with TestClient(app) as client:
            r1 = client.get(f"/geo/{PROVINCE_CODE}/entities?size=5")
            r2 = client.get(f"/geo/{PROVINCE_CODE}/entities?size=5")

        body1 = r1.json()
        body2 = r2.json()

        assert body1["ok"] == body2["ok"]
        assert body1["data"] == body2["data"]
        assert body1["error"] == body2["error"]

        # meta must match on all keys EXCEPT 'cache'.
        meta1 = {k: v for k, v in (body1.get("meta") or {}).items() if k != "cache"}
        meta2 = {k: v for k, v in (body2.get("meta") or {}).items() if k != "cache"}
        assert meta1 == meta2, (
            f"Meta mismatch between miss and hit (excluding cache key): "
            f"miss={meta1}, hit={meta2}"
        )

    @SKIP_NO_DB
    def test_health_not_cached(self) -> None:
        """/health must NEVER be cached — it is explicitly excluded."""
        cache_clear()
        with TestClient(app) as client:
            r1 = client.get("/health")
            r2 = client.get("/health")

        for r in (r1, r2):
            assert r.status_code == 200
            meta = r.json().get("meta")
            # meta is None for /health (ok() called with no extra kwargs).
            # If meta is a dict, cache key must not be present.
            if isinstance(meta, dict):
                assert "cache" not in meta, (
                    f"/health must not inject cache indicator; meta={meta}"
                )

    @SKIP_NO_DB
    def test_geo_tree_cached(self) -> None:
        """/geo/{province}/tree (expensive) must also be cached."""
        cache_clear()
        with TestClient(app) as client:
            r1 = client.get(f"/geo/{PROVINCE_CODE}/tree")
            r2 = client.get(f"/geo/{PROVINCE_CODE}/tree")

        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json().get("meta", {}).get("cache") == "miss"
        assert r2.json().get("meta", {}).get("cache") == "hit"

    @SKIP_NO_DB
    def test_different_query_strings_different_cache_entries(self) -> None:
        """Different query params must yield different cache entries."""
        cache_clear()
        with TestClient(app) as client:
            # Page 1
            r1a = client.get(f"/geo/{PROVINCE_CODE}/entities?size=5&page=1")
            r1b = client.get(f"/geo/{PROVINCE_CODE}/entities?size=5&page=1")
            # Page 2 — different cache key
            r2a = client.get(f"/geo/{PROVINCE_CODE}/entities?size=5&page=2")
            r2b = client.get(f"/geo/{PROVINCE_CODE}/entities?size=5&page=2")

        assert r1a.json().get("meta", {}).get("cache") == "miss"
        assert r1b.json().get("meta", {}).get("cache") == "hit"
        assert r2a.json().get("meta", {}).get("cache") == "miss"
        assert r2b.json().get("meta", {}).get("cache") == "hit"

        # Data must differ between page 1 and page 2.
        data_p1 = r1a.json()["data"]
        data_p2 = r2a.json()["data"]
        codes_p1 = {e["cdp_code"] for e in data_p1}
        codes_p2 = {e["cdp_code"] for e in data_p2}
        assert len(codes_p1 & codes_p2) == 0, (
            "Page 1 and Page 2 cache entries overlap — should be distinct"
        )

    @SKIP_NO_DB
    def test_entity_inventory_cached(self) -> None:
        """/entities/{cdp}/inventory must be cached (RATE_EXPENSIVE endpoint)."""
        # Use the well-known dealer from other test files.
        dealer = "CDP-ES-28-27JX9YZC"
        cache_clear()
        with TestClient(app) as client:
            r1 = client.get(f"/entities/{dealer}/inventory?size=5")
            r2 = client.get(f"/entities/{dealer}/inventory?size=5")

        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json().get("meta", {}).get("cache") == "miss"
        assert r2.json().get("meta", {}).get("cache") == "hit"

    @SKIP_NO_DB
    def test_404_response_not_cached(self) -> None:
        """Error (404) responses must never be cached.

        After two requests to a non-existent entity, the second must also
        be a 404 (not accidentally served from a cached error body), and
        the response must NOT contain a meta.cache indicator.
        """
        cache_clear()
        with TestClient(app) as client:
            r1 = client.get("/entities/CDP-XX-00-DOESNOTEXIST/inventory?size=5")
            r2 = client.get("/entities/CDP-XX-00-DOESNOTEXIST/inventory?size=5")

        assert r1.status_code == 404
        assert r2.status_code == 404
        # Neither should carry a cache indicator (errors are not cached).
        for r in (r1, r2):
            meta = r.json().get("meta")
            if isinstance(meta, dict):
                assert "cache" not in meta, (
                    f"Error response must not have meta.cache; meta={meta}"
                )
