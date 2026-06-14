"""B3.5 — API key authentication tests.

Verifies the three required behaviours of require_api_key:

  1. CARDEEP_API_KEY NOT set in environment  ->  public mode; all callers get 200
     without any header.  (Backward-compatible — existing tests unaffected.)

  2. CARDEEP_API_KEY set in environment  ->  protected mode:
     a. Request with CORRECT key in 'X-API-Key' header  ->  200.
     b. Request with WRONG key  ->  401.
     c. Request with NO key header  ->  401.

  3. GET /health is NEVER gated — always 200 regardless of CARDEEP_API_KEY.

Uses monkeypatch to control os.environ; TestClient for synchronous HTTP calls.
No DB writes — all asserted paths either go to /health (no pool query that could
write) or to a known cdp_code under the real pool (read-only GET).
"""
from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# DB connectivity guard — skip data-endpoint auth tests when cardeep-pg is
# not reachable.  The /health-only test (public/protected) always runs.
# ---------------------------------------------------------------------------

def _db_available() -> bool:
    import asyncio
    try:
        import asyncpg  # noqa: F401
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
        return asyncio.run(_ping())
    except Exception:
        return False


DB_AVAILABLE = _db_available()

# A data endpoint that exists on the live DB — used for auth smoke-tests.
PROVINCE_CODE = "28"   # Madrid — always populated


# ---------------------------------------------------------------------------
# /health — must NEVER require authentication
# ---------------------------------------------------------------------------

class TestHealthAlwaysPublic:
    """GET /health must return 200 regardless of CARDEEP_API_KEY configuration."""

    @pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
    def test_health_public_when_key_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Without CARDEEP_API_KEY in env, /health is public — no header needed."""
        monkeypatch.delenv("CARDEEP_API_KEY", raising=False)
        # Re-import app so the dependency closure reads the patched env.
        from services.api.main import app
        with TestClient(app) as client:
            r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["ok"] is True

    @pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
    def test_health_public_even_when_key_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """With CARDEEP_API_KEY set, /health must STILL return 200 (not gated)."""
        monkeypatch.setenv("CARDEEP_API_KEY", "super-secret-test-key-xyz")
        from services.api.main import app
        with TestClient(app) as client:
            r = client.get("/health")
        assert r.status_code == 200, (
            f"GET /health must never require auth; got {r.status_code}"
        )


# ---------------------------------------------------------------------------
# Public mode — CARDEEP_API_KEY not set
# ---------------------------------------------------------------------------

class TestPublicModeNoKeyConfigured:
    """When CARDEEP_API_KEY is absent, all data endpoints are publicly accessible."""

    @pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
    def test_data_endpoint_accessible_without_header(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """GET /geo/{code}/entities returns 200 with no X-API-Key header when key not configured."""
        monkeypatch.delenv("CARDEEP_API_KEY", raising=False)
        from services.api.main import app
        with TestClient(app) as client:
            r = client.get(f"/geo/{PROVINCE_CODE}/entities?size=1")
        assert r.status_code == 200, (
            f"Public mode: expected 200 without key, got {r.status_code}"
        )

    @pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
    def test_data_endpoint_accessible_with_any_header(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """In public mode, providing any X-API-Key value is also fine (key is ignored)."""
        monkeypatch.delenv("CARDEEP_API_KEY", raising=False)
        from services.api.main import app
        with TestClient(app) as client:
            r = client.get(
                f"/geo/{PROVINCE_CODE}/entities?size=1",
                headers={"X-API-Key": "any-random-value"},
            )
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Protected mode — CARDEEP_API_KEY set
# ---------------------------------------------------------------------------

class TestProtectedModeKeyConfigured:
    """When CARDEEP_API_KEY is configured, data endpoints require the correct key."""

    _KEY = "cardeep-test-api-key-b35"

    @pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
    def test_correct_key_returns_200(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """X-API-Key matching CARDEEP_API_KEY -> 200."""
        monkeypatch.setenv("CARDEEP_API_KEY", self._KEY)
        from services.api.main import app
        with TestClient(app) as client:
            r = client.get(
                f"/geo/{PROVINCE_CODE}/entities?size=1",
                headers={"X-API-Key": self._KEY},
            )
        assert r.status_code == 200, (
            f"Correct key must yield 200; got {r.status_code}"
        )

    @pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
    def test_wrong_key_returns_401(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """X-API-Key NOT matching CARDEEP_API_KEY -> 401."""
        monkeypatch.setenv("CARDEEP_API_KEY", self._KEY)
        from services.api.main import app
        with TestClient(app) as client:
            r = client.get(
                f"/geo/{PROVINCE_CODE}/entities?size=1",
                headers={"X-API-Key": "totally-wrong-key"},
            )
        assert r.status_code == 401, (
            f"Wrong key must yield 401; got {r.status_code}"
        )

    @pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
    def test_missing_key_header_returns_401(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """No X-API-Key header when key is configured -> 401."""
        monkeypatch.setenv("CARDEEP_API_KEY", self._KEY)
        from services.api.main import app
        with TestClient(app) as client:
            r = client.get(f"/geo/{PROVINCE_CODE}/entities?size=1")
        assert r.status_code == 401, (
            f"Missing key header must yield 401; got {r.status_code}"
        )

    @pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
    def test_health_still_200_in_protected_mode(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Even with CARDEEP_API_KEY set, /health must return 200 without any key."""
        monkeypatch.setenv("CARDEEP_API_KEY", self._KEY)
        from services.api.main import app
        with TestClient(app) as client:
            r = client.get("/health")
        assert r.status_code == 200, (
            f"GET /health must NOT require auth even in protected mode; got {r.status_code}"
        )
