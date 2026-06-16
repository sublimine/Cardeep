"""Tests for GET /geo/seal — the SU-SEAL per-province seal endpoint (migration 0042).

FastAPI TestClient against the live DB (same pattern as test_api_canonical.py). Verifies the
endpoint serves v_province_seal with a coherent envelope: 52 provinces, valid verdicts, a
national coverage in the sane canonical band, and a distribution that sums to 52.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from services.api.main import app

_VALID = {"SELLADO", "PARCIAL", "GAP", "NO_DENOM"}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


class TestGeoSeal:
    def test_seal_endpoint_envelope(self, client):
        r = client.get("/geo/seal")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["ok"] is True
        d = body["data"]
        assert d["segment"] == "venta"
        assert len(d["provinces"]) == 52

    def test_distribution_sums_to_52(self, client):
        d = client.get("/geo/seal").json()["data"]
        assert sum(d["distribution"].values()) == 52

    def test_national_coverage_is_canonical_band(self, client):
        """National coverage must be the canonical ~79%, never the entity-level ~165% over-count."""
        d = client.get("/geo/seal").json()["data"]
        cov = d["national"]["coverage_pct"]
        assert 60 <= cov <= 110, f"national coverage {cov} outside sane canonical band"

    def test_every_province_has_valid_verdict_and_consistent_coverage(self, client):
        d = client.get("/geo/seal").json()["data"]
        for p in d["provinces"]:
            assert p["verdict"] in _VALID
            if p["denominator"]:
                expected = round(100.0 * p["numerator"] / p["denominator"], 1)
                assert abs(p["coverage_pct"] - expected) < 0.05
