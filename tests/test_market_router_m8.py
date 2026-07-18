"""Contract tests for GET /market/dgt-corroboration (M8, F4, 01-market-intelligence).

Fixtures use the REAL corroboration run computed from the real June 2026 DGT batch
(01-market-intelligence-f4.md documents the exact run_id/numbers).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from services.api.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


class TestDgtCorroboration:
    def test_returns_200_with_national_data(self, client: TestClient) -> None:
        r = client.get("/market/dgt-corroboration")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert isinstance(body["data"], list)
        assert len(body["data"]) > 0

    def test_envelope_carries_run_metadata(self, client: TestClient) -> None:
        r = client.get("/market/dgt-corroboration")
        meta = r.json()["meta"]
        assert "run_id" in meta
        assert "month" in meta
        assert meta["month"] == "202606"

    def test_make_level_rows_have_null_model_by_default(self, client: TestClient) -> None:
        """Omitting `model` must return ONLY make-level aggregate rows (model=None
        in the DB), never a mix of make-level and make+model-level rows."""
        r = client.get("/market/dgt-corroboration", params={"province": "28"})
        items = r.json()["data"]
        assert len(items) > 0
        for item in items:
            assert item["model"] is None

    def test_filter_by_make_and_model(self, client: TestClient) -> None:
        r = client.get(
            "/market/dgt-corroboration",
            params={"province": "28", "make": "volkswagen", "model": "golf"},
        )
        assert r.status_code == 200
        items = r.json()["data"]
        for item in items:
            assert item["make"] == "VOLKSWAGEN"
            assert item["model"] == "GOLF"

    def test_every_row_has_ratio_or_null_never_fabricated(self, client: TestClient) -> None:
        r = client.get("/market/dgt-corroboration", params={"province": "28"})
        for item in r.json()["data"]:
            assert item["gone_count"] >= 0
            assert item["dgt_count"] >= 0
            if item["gone_count"] == 0:
                assert item["ratio"] is None
            else:
                assert item["ratio"] == pytest.approx(item["dgt_count"] / item["gone_count"])

    def test_make_filter_is_case_insensitive(self, client: TestClient) -> None:
        r_lower = client.get("/market/dgt-corroboration", params={"province": "28", "make": "seat"})
        r_upper = client.get("/market/dgt-corroboration", params={"province": "28", "make": "SEAT"})
        assert r_lower.json()["data"] == r_upper.json()["data"]
