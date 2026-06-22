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
    def test_seal_endpoint_envelope_has_both_segments(self, client):
        r = client.get("/geo/seal")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["ok"] is True
        segs = body["data"]["segments"]
        assert set(segs) >= {"venta", "desguace"}
        for seg in ("venta", "desguace"):
            assert len(segs[seg]["provinces"]) == 52

    def test_venta_distribution_sums_to_52(self, client):
        venta = client.get("/geo/seal").json()["data"]["segments"]["venta"]
        assert sum(venta["distribution"].values()) == 52

    def test_venta_national_coverage_is_canonical_band(self, client):
        """VENTA national coverage must be the canonical ~79%, never entity-level ~165% over-count."""
        cov = client.get("/geo/seal").json()["data"]["segments"]["venta"]["national"]["coverage_pct"]
        assert 60 <= cov <= 110, f"venta national coverage {cov} outside sane canonical band"

    def test_desguace_all_sellado_discovery(self, client):
        """DESGUACE discovery seal: found >= DGT census in every province → all SELLADO."""
        desg = client.get("/geo/seal").json()["data"]["segments"]["desguace"]
        assert desg["distribution"].get("SELLADO", 0) == 52

    def test_every_province_has_valid_verdict_and_consistent_coverage(self, client):
        # Mirror PostgreSQL ROUND() (half-away-from-zero); Python round() is banker's
        # and diverges by 0.1 on .5 boundaries (e.g. 100*53/16 = 331.25 -> 331.3 vs 331.2).
        from decimal import Decimal, ROUND_HALF_UP
        segs = client.get("/geo/seal").json()["data"]["segments"]
        for seg in segs.values():
            for p in seg["provinces"]:
                assert p["verdict"] in _VALID
                if p["denominator"]:
                    expected = float(
                        Decimal(100.0 * p["numerator"] / float(p["denominator"])).quantize(
                            Decimal("0.1"), rounding=ROUND_HALF_UP)
                    )
                    assert abs(p["coverage_pct"] - expected) < 0.05
