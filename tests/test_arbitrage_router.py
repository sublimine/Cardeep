"""Contract tests for services/api/routers/arbitrage.py (04-arbitrage F2).

Runs against the LIVE cardeep-pg (same pattern as tests/test_market_router.py) —
reads the real ``arbitrage_run``/``deal_score`` rows written by the F1 job
(pipeline/arbitrage/score.py). If a fresh run changes the exact counts, the
existence/shape assertions below stay valid; only exact-count assertions would need
re-verification (none are asserted here for that reason).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from services.api.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


class TestDeals:
    def test_returns_200_with_expected_envelope_and_shape(self, client: TestClient) -> None:
        r = client.get("/arbitrage/deals", params={"size": 5})
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert body["error"] is None
        items = body["data"]
        assert isinstance(items, list)
        assert len(items) <= 5
        meta = body["meta"]
        assert "run_id" in meta and "run_at" in meta and "methodology_version" in meta
        assert "page" in meta and "size" in meta and "has_more" in meta
        if items:
            row = items[0]
            for key in (
                "vehicle_ulid", "make", "model", "year", "price", "deep_link",
                "dealer", "province_code", "z", "band", "savings_eur", "cohort",
                "days_on_market", "fresh", "last_seen",
            ):
                assert key in row, f"missing key {key!r} in deal row"
            assert row["band"] in ("chollo_fuerte", "bajo_mercado")
            assert row["savings_eur"] > 0
            assert row["cohort"]["n"] >= 1
            assert "cdp_code" in row["dealer"]

    def test_ordered_by_savings_eur_descending(self, client: TestClient) -> None:
        r = client.get("/arbitrage/deals", params={"size": 50})
        items = r.json()["data"]
        savings = [it["savings_eur"] for it in items]
        assert savings == sorted(savings, reverse=True)

    def test_band_filter_chollo_fuerte_only(self, client: TestClient) -> None:
        r = client.get("/arbitrage/deals", params={"band": "chollo_fuerte", "size": 30})
        items = r.json()["data"]
        assert len(items) > 0, "expected real chollo_fuerte rows in the live corpus"
        assert all(it["band"] == "chollo_fuerte" for it in items)

    def test_invalid_band_returns_400(self, client: TestClient) -> None:
        r = client.get("/arbitrage/deals", params={"band": "not_a_band"})
        assert r.status_code == 400
        assert r.json()["ok"] is False

    def test_min_savings_filter_respected(self, client: TestClient) -> None:
        r = client.get("/arbitrage/deals", params={"min_savings": 5000, "size": 30})
        items = r.json()["data"]
        assert all(it["savings_eur"] >= 5000 for it in items)

    def test_no_stale_vehicle_beyond_max_age_days(self, client: TestClient) -> None:
        """Anti-Zillow gate (§4.1): nothing served is older than FRESHNESS_MAX_DAYS,
        even though its deal_score row may still exist from an older run."""
        from datetime import datetime, timedelta, timezone

        r = client.get("/arbitrage/deals", params={"size": 100})
        items = r.json()["data"]
        cutoff = datetime.now(timezone.utc) - timedelta(days=7, hours=1)  # 1h slack for clock skew
        for it in items:
            last_seen = datetime.fromisoformat(it["last_seen"].replace("Z", "+00:00"))
            assert last_seen >= cutoff, f"vehicle {it['vehicle_ulid']} last_seen={it['last_seen']} exceeds 7d gate"


class TestDesync:
    def test_returns_200_with_expected_shape(self, client: TestClient) -> None:
        r = client.get("/arbitrage/desync", params={"size": 10})
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        items = body["data"]
        assert isinstance(items, list)
        if items:
            row = items[0]
            for key in ("vehicle_ulid", "make", "model", "dealer", "platform", "delta_eur", "delta_pct"):
                assert key in row
            assert row["delta_eur"] > 0
            assert "price" in row["dealer"] and "price" in row["platform"]

    def test_ordered_by_delta_eur_descending(self, client: TestClient) -> None:
        r = client.get("/arbitrage/desync", params={"size": 50})
        items = r.json()["data"]
        deltas = [it["delta_eur"] for it in items]
        assert deltas == sorted(deltas, reverse=True)


class TestMethodology:
    def test_returns_published_thresholds(self, client: TestClient) -> None:
        r = client.get("/arbitrage/methodology")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["deal_score"]["cohort"]["tier_a_min_n"] == 15
        assert data["deal_score"]["cohort"]["tier_b_min_n"] == 30
        assert data["deal_score"]["bands"]["price_trap_frontier_z"] == -6.0
        assert data["deal_score"]["bands"]["chollo_fuerte_max_z"] == -3.5
        assert data["deal_score"]["bands"]["bajo_mercado_max_z"] == -2.0
        assert data["deal_score"]["freshness"]["fresh_hours"] == 72
        assert data["desync"]["min_absolute_eur"] == 100
        assert data["time_arbitrage"]["min_cycles_per_cohort"] == 50
        assert data["time_arbitrage"]["min_observations_per_bucket"] == 30
        assert data["geo_arbitrage"]["cell_min_n"] == 15
        assert len(data["disclaimers"]) >= 1


class TestTimeCurves:
    def test_unknown_cohort_returns_honest_empty_state(self, client: TestClient) -> None:
        """A cohort that has never existed gets null/empty with a declared reason —
        never a fabricated number, never a 404 (the endpoint itself is valid)."""
        r = client.get("/arbitrage/time-curves/__NOPE_MAKE__/__NOPE_MODEL__", params={"year": 2020})
        assert r.status_code in (200, 503)
        if r.status_code == 200:
            data = r.json()["data"]
            assert data["cycle_stats"] is None
            assert data["cycle_stats_reason"] is not None
            assert data["buckets"] == []
            assert data["buckets_reason"] is not None
            assert "GONE" in data["disclaimer"] or "venta" in data["disclaimer"].lower()

    def test_response_shape_when_run_exists(self, client: TestClient) -> None:
        r = client.get("/arbitrage/time-curves/__NOPE_MAKE__/__NOPE_MODEL__", params={"year": 2020})
        if r.status_code == 503:
            pytest.skip("no arbitrage_decay_run yet in this environment")
        meta = r.json()["meta"]
        assert "run_id" in meta and "run_at" in meta and "methodology_version" in meta


class TestGeo:
    def test_unknown_cohort_returns_honest_empty_state(self, client: TestClient) -> None:
        r = client.get("/arbitrage/geo/__NOPE_MAKE__/__NOPE_MODEL__", params={"year": 2020})
        assert r.status_code in (200, 503)
        if r.status_code == 200:
            data = r.json()["data"]
            assert data["cells"] == []
            assert data["cells_reason"] is not None
            assert data["gaps"] == []
            assert "transacci" in data["disclaimer"].lower()
