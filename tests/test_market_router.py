"""Contract tests for services/api/routers/market.py (F3, CAMPAIGN 01-market-intelligence).

Fixtures below use REAL segments confirmed present in the F2 production run
(01-market-intelligence-f2.md) — same pattern as tests/test_api_pagination.py's
hardcoded real CDP codes. If a fresher published run changes these numbers, the
exact-value assertions may need re-verification against the live DB (the
existence/shape assertions do not depend on exact figures and stay valid).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from services.api.main import app

# National-scope segment confirmed >=8 in the F1 cross-check sample AND present in
# every F2 metric that has a national fallback (re-verified against the live
# published run before this test file was written — see F3 report).
KNOWN_MAKE = "Peugeot"
KNOWN_MODEL = "208"
KNOWN_YEAR = 2024
KNOWN_FUEL = "Gasolina"


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


class TestSegmentStats:
    def test_known_segment_returns_200_with_metrics(self, client: TestClient) -> None:
        r = client.get(
            f"/market/segments/{KNOWN_MAKE}/{KNOWN_MODEL}/stats",
            params={"year": KNOWN_YEAR, "fuel": KNOWN_FUEL},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert body["error"] is None
        data = body["data"]
        assert data["make"] == KNOWN_MAKE
        assert data["model"] == KNOWN_MODEL
        assert "metrics" in data
        assert "M1" in data["metrics"], "M1 must be present for a segment with n>=8 nationally"
        m1 = data["metrics"]["M1"]
        assert m1["n"] >= 8
        assert "p25" in m1 and "p50" in m1 and "p75" in m1
        assert m1["p25"] <= m1["p50"] <= m1["p75"]

    def test_envelope_carries_run_metadata(self, client: TestClient) -> None:
        r = client.get(
            f"/market/segments/{KNOWN_MAKE}/{KNOWN_MODEL}/stats",
            params={"year": KNOWN_YEAR, "fuel": KNOWN_FUEL},
        )
        meta = r.json()["meta"]
        assert "run_id" in meta
        assert "run_at" in meta
        assert "window_description" in meta

    def test_every_served_metric_key_is_authorized(self, client: TestClient) -> None:
        """M2/M6/M8 must NEVER appear — they are not this phase's scope (see router
        module docstring: M2=F5, M6=declared gap, M8=F4)."""
        r = client.get(
            f"/market/segments/{KNOWN_MAKE}/{KNOWN_MODEL}/stats",
            params={"year": KNOWN_YEAR, "fuel": KNOWN_FUEL},
        )
        metrics = r.json()["data"]["metrics"]
        assert set(metrics.keys()).issubset({"M1", "M3", "M4", "M5", "M7", "M9", "M10"})
        assert "M2" not in metrics
        assert "M6" not in metrics
        assert "M8" not in metrics

    def test_national_fallback_flag_when_no_province_requested(self, client: TestClient) -> None:
        r = client.get(
            f"/market/segments/{KNOWN_MAKE}/{KNOWN_MODEL}/stats",
            params={"year": KNOWN_YEAR, "fuel": KNOWN_FUEL},
        )
        m1 = r.json()["data"]["metrics"]["M1"]
        assert m1["scope"] == "nat"
        assert m1["fallback_to_national"] is False  # no province was requested at all

    def test_nonexistent_segment_returns_404(self, client: TestClient) -> None:
        r = client.get(
            "/market/segments/__NO_SUCH_MAKE_XYZ__/__NO_SUCH_MODEL__/stats",
            params={"year": 2024, "fuel": "Gasolina"},
        )
        assert r.status_code == 404
        body = r.json()
        assert body["ok"] is False
        assert body["error"] is not None

    def test_missing_required_query_param_is_422(self, client: TestClient) -> None:
        r = client.get(f"/market/segments/{KNOWN_MAKE}/{KNOWN_MODEL}/stats")
        assert r.status_code == 422  # year/fuel are required Query(...)

    def test_province_with_insufficient_sample_falls_back_to_national(
        self, client: TestClient
    ) -> None:
        """A province unlikely to individually clear n>=8 for this exact segment
        (Soria, one of Spain's lowest-population provinces) must fall back to the
        national row with fallback_to_national=True — never a 404, never a fake
        provincial number."""
        r = client.get(
            f"/market/segments/{KNOWN_MAKE}/{KNOWN_MODEL}/stats",
            params={"year": KNOWN_YEAR, "fuel": KNOWN_FUEL, "province": "42"},  # Soria
        )
        assert r.status_code == 200
        m1 = r.json()["data"]["metrics"]["M1"]
        assert m1["scope"] in ("prov", "nat")
        if m1["scope"] == "nat":
            assert m1["fallback_to_national"] is True


class TestProvincesDemand:
    def test_returns_200_with_ranked_list(self, client: TestClient) -> None:
        r = client.get("/market/provinces/demand")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        items = body["data"]
        assert isinstance(items, list)
        assert len(items) > 0

    def test_items_are_sorted_descending_by_absorption_rate(self, client: TestClient) -> None:
        r = client.get("/market/provinces/demand")
        items = r.json()["data"]
        rates = [i["absorption_rate"] for i in items if i["absorption_rate"] is not None]
        assert rates == sorted(rates, reverse=True)

    def test_every_row_has_province_code_and_n(self, client: TestClient) -> None:
        r = client.get("/market/provinces/demand")
        items = r.json()["data"]
        for item in items:
            assert item["province_code"] is not None
            assert item["n_available"] >= 8  # M5's own MIN_COHORT_N floor

    def test_envelope_carries_run_metadata(self, client: TestClient) -> None:
        r = client.get("/market/provinces/demand")
        meta = r.json()["meta"]
        assert "run_id" in meta
        assert "count" in meta
        assert meta["count"] == len(r.json()["data"])
