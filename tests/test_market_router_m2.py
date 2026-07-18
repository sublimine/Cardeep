"""Contract tests for GET /market/price-position/{vehicle_ulid} (M2, F5,
01-market-intelligence). Fixtures are REAL vehicle_ulids from the live DB,
re-verified against the published market_stat run before this file was written
(see 01-market-intelligence-f5.md for the exact query used to find them).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from services.api.main import app

# Real vehicle, Peugeot 208 2024 Gasolina, province 41 (Sevilla) — that province HAS
# its own M1 row (n=687), so this exercises the PROVINCIAL scope (not the national
# fallback). price=11790.00, provincial p50=13390 -> ratio=0.8805... < 0.92.
KNOWN_VEHICLE_ULID = "01KTZ8N8VMC28V7YXG9RNRN9T8"
KNOWN_EXPECTED_RATIO = 11790.0 / 13390.0

NO_PRICE_VEHICLE_ULID = "01KVS6V18B5AH7YD6SF337QXQ2"


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


class TestPricePosition:
    def test_known_vehicle_returns_correct_ratio_and_band(self, client: TestClient) -> None:
        r = client.get(f"/market/price-position/{KNOWN_VEHICLE_ULID}")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        data = body["data"]
        assert data["vehicle_ulid"] == KNOWN_VEHICLE_ULID
        assert data["price"] == pytest.approx(11790.0)
        pos = data["position"]
        assert pos["ratio"] == pytest.approx(KNOWN_EXPECTED_RATIO, abs=1e-4)
        assert pos["band"] == "below_market"  # ratio ~0.8805 < 0.92
        assert pos["scope"] == "prov"
        assert pos["fallback_to_national"] is False
        assert pos["segment_p50"] == pytest.approx(13390.0)

    def test_cuts_are_published_in_the_response(self, client: TestClient) -> None:
        """Carta §4 M2 row: thresholds are PUBLISHED, not a black box (explicit
        contrast with CarGurus' undisclosed Deal Rating thresholds)."""
        r = client.get(f"/market/price-position/{KNOWN_VEHICLE_ULID}")
        cuts = r.json()["data"]["position"]["cuts"]
        assert cuts["below_market_lt"] == 0.92
        assert cuts["above_market_gt"] == 1.08

    def test_band_boundaries_are_exclusive_correctly(self) -> None:
        from services.api.routers.market import _price_position_band
        assert _price_position_band(0.91) == "below_market"
        assert _price_position_band(0.92) == "at_market"  # boundary itself is "at market"
        assert _price_position_band(1.0) == "at_market"
        assert _price_position_band(1.08) == "at_market"  # boundary itself is "at market"
        assert _price_position_band(1.09) == "above_market"

    def test_nonexistent_vehicle_returns_404(self, client: TestClient) -> None:
        r = client.get("/market/price-position/01NOSUCHVEHICLEULIDXXXXXXX")
        assert r.status_code == 404
        assert r.json()["ok"] is False

    def test_vehicle_with_no_price_degrades_honestly(self, client: TestClient) -> None:
        r = client.get(f"/market/price-position/{NO_PRICE_VEHICLE_ULID}")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["position"] is None
        assert "reason" in data

    def test_envelope_carries_run_metadata(self, client: TestClient) -> None:
        r = client.get(f"/market/price-position/{KNOWN_VEHICLE_ULID}")
        meta = r.json()["meta"]
        assert "run_id" in meta
        assert "run_at" in meta
