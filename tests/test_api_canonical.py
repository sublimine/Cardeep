"""Tests for CAMPAIGN B1.5 — canonical cluster resolution endpoints.

Uses FastAPI TestClient (synchronous, no server needed).
Real cdp_codes from the live DB are used; tests require the DB to be reachable.
"""
from __future__ import annotations

import asyncio

import asyncpg
import pytest
from fastapi.testclient import TestClient

from services.api.main import DSN, app

# ---------------------------------------------------------------------------
# Known test fixtures (verified against cardeep-pg :5433, run splink-b13-run2)
# ---------------------------------------------------------------------------
ALIAS_CODE = "CDP-ES-50-N675XHMM"       # non-canonical member
CANONICAL_CODE = "CDP-ES-50-8SX3KPR5"   # canonical (cluster representative)
CLUSTER_SIZE = 2


@pytest.fixture(scope="module")
def client():
    """Spin up a TestClient with a real asyncpg pool.

    The pool is created synchronously by running the lifespan in a background
    event loop — TestClient drives the ASGI app without needing uvicorn.
    """
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# /entities/{cdp_code}/canonical
# ---------------------------------------------------------------------------

class TestGetEntityCanonical:
    def test_alias_resolves_to_canonical(self, client):
        """Alias code must resolve to the canonical, is_canonical=False."""
        r = client.get(f"/entities/{ALIAS_CODE}/canonical")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        d = body["data"]
        assert d["input_cdp_code"] == ALIAS_CODE
        assert d["canonical_cdp_code"] == CANONICAL_CODE
        assert d["is_canonical"] is False
        assert d["n_members"] == CLUSTER_SIZE
        assert ALIAS_CODE in d["members"]
        assert CANONICAL_CODE in d["members"]

    def test_canonical_reports_itself(self, client):
        """Canonical code must report is_canonical=True."""
        r = client.get(f"/entities/{CANONICAL_CODE}/canonical")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        d = body["data"]
        assert d["input_cdp_code"] == CANONICAL_CODE
        assert d["canonical_cdp_code"] == CANONICAL_CODE
        assert d["is_canonical"] is True
        assert d["n_members"] == CLUSTER_SIZE

    def test_nonexistent_returns_404(self, client):
        r = client.get("/entities/CDP-XX-00-DOESNOTEXIST/canonical")
        assert r.status_code == 404
        assert r.json()["ok"] is False


# ---------------------------------------------------------------------------
# /entities/{cdp_code}  (modified — now cluster-aware)
# ---------------------------------------------------------------------------

class TestGetEntity:
    def test_alias_returns_canonical_entity_row(self, client):
        """Querying an alias must return the CANONICAL entity row, not the alias row."""
        r = client.get(f"/entities/{ALIAS_CODE}")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        d = body["data"]
        # The served entity must be the canonical
        assert d["cdp_code"] == CANONICAL_CODE
        assert d["canonical_cdp_code"] == CANONICAL_CODE
        assert d["queried_cdp_code"] == ALIAS_CODE
        assert d["n_aliases"] == CLUSTER_SIZE - 1
        # available_inventory is an integer (aggregated)
        assert isinstance(d["available_inventory"], int)

    def test_canonical_returns_itself(self, client):
        r = client.get(f"/entities/{CANONICAL_CODE}")
        assert r.status_code == 200
        d = r.json()["data"]
        assert d["cdp_code"] == CANONICAL_CODE
        assert d["canonical_cdp_code"] == CANONICAL_CODE
        assert d["queried_cdp_code"] == CANONICAL_CODE
        assert d["n_aliases"] == CLUSTER_SIZE - 1

    def test_nonexistent_returns_404(self, client):
        r = client.get("/entities/CDP-XX-00-DOESNOTEXIST")
        assert r.status_code == 404

    def test_envelope_shape(self, client):
        r = client.get(f"/entities/{CANONICAL_CODE}")
        body = r.json()
        assert set(body.keys()) == {"ok", "data", "error", "meta"}
        assert body["error"] is None


# ---------------------------------------------------------------------------
# /entities/{cdp_code}/inventory  (modified — now cluster-aware)
# ---------------------------------------------------------------------------

class TestGetInventory:
    def test_alias_returns_cluster_inventory(self, client):
        """Inventory for alias and canonical must be identical (same cluster)."""
        r_alias = client.get(f"/entities/{ALIAS_CODE}/inventory")
        r_canon = client.get(f"/entities/{CANONICAL_CODE}/inventory")
        assert r_alias.status_code == 200
        assert r_canon.status_code == 200
        alias_ids = {v["vehicle_ulid"] for v in r_alias.json()["data"]}
        canon_ids = {v["vehicle_ulid"] for v in r_canon.json()["data"]}
        assert alias_ids == canon_ids, "alias and canonical must return the same vehicle set"

    def test_no_duplicate_vehicles(self, client):
        """vehicle_ulid must be unique in the result."""
        r = client.get(f"/entities/{CANONICAL_CODE}/inventory")
        items = r.json()["data"]
        ulids = [v["vehicle_ulid"] for v in items]
        assert len(ulids) == len(set(ulids)), "duplicate vehicle_ulids returned"

    def test_count_meta(self, client):
        r = client.get(f"/entities/{CANONICAL_CODE}/inventory")
        body = r.json()
        assert body["meta"]["count"] == len(body["data"])

    def test_nonexistent_returns_404(self, client):
        r = client.get("/entities/CDP-XX-00-DOESNOTEXIST/inventory")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Regression: existing endpoints must still work
# ---------------------------------------------------------------------------

class TestRegressionExistingEndpoints:
    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "live"

    def test_delta_alias(self, client):
        """Delta endpoint still works for original cdp_code (not cluster-aware)."""
        r = client.get(f"/entities/{ALIAS_CODE}/delta")
        assert r.status_code == 200
        assert r.json()["ok"] is True
