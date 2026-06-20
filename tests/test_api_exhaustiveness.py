"""Tests for GET /geo/exhaustiveness — the national coverage CERTIFICATE (capture-recapture / MSE).

FastAPI TestClient against the live DB (same pattern as test_api_seal.py). Verifies the endpoint
serves v_exhaustiveness_seal with a coherent envelope: a grand-national headline certificate, the
four discovery segments, and the MSE invariant coverage_lower <= coverage_point everywhere. Honest
by construction: it asserts the lower-bound math, NOT a fabricated 100%.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from services.api.main import app

_SEGMENTS = {"compraventa", "concesionario", "desguace", "otros"}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


class TestGeoExhaustiveness:
    def test_envelope_and_certificate_kind(self, client):
        r = client.get("/geo/exhaustiveness")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["ok"] is True
        data = body["data"]
        assert data["certificate"] == "national_exhaustiveness_mse"
        assert isinstance(data["build_run_id"], str) and data["build_run_id"]

    def test_grand_national_headline_is_coherent(self, client):
        nat = client.get("/geo/exhaustiveness").json()["data"]["national"]
        assert nat is not None, "grand-national certificate row (segment+province NULL) missing"
        assert nat["k_lists"] >= 1 and nat["n_obs"] > 0
        assert isinstance(nat["sealed"], bool)
        # MSE invariant: the defensible lower bound never exceeds the point estimate.
        assert 0.0 <= nat["coverage_lower"] <= nat["coverage_point"] <= 1.0

    def test_four_segments_present_with_provinces(self, client):
        by_seg = client.get("/geo/exhaustiveness").json()["data"]["by_segment"]
        assert set(by_seg) >= _SEGMENTS
        for seg in _SEGMENTS:
            assert len(by_seg[seg]["provinces"]) >= 1

    def test_mse_lower_bound_invariant_holds_everywhere(self, client):
        """coverage_lower <= coverage_point in EVERY served row (national + per-province)."""
        data = client.get("/geo/exhaustiveness").json()["data"]
        rows = [data["national"]]
        for seg in data["by_segment"].values():
            if seg["national"]:
                rows.append(seg["national"])
            rows.extend(seg["provinces"])
        for row in rows:
            cl, cp = row.get("coverage_lower"), row.get("coverage_point")
            if cl is not None and cp is not None:
                assert 0.0 <= cl <= cp <= 1.0, f"MSE invariant broken: lower={cl} point={cp}"

    def test_not_falsely_sealed_when_coverage_below_threshold(self, client):
        """Anti-maquillaje: a row cannot be sealed=true while coverage_lower < its seal_threshold."""
        data = client.get("/geo/exhaustiveness").json()["data"]
        rows = [data["national"]]
        for seg in data["by_segment"].values():
            if seg["national"]:
                rows.append(seg["national"])
            rows.extend(seg["provinces"])
        for row in rows:
            cl, thr, sealed = row.get("coverage_lower"), row.get("seal_threshold"), row.get("sealed")
            if sealed and cl is not None and thr is not None:
                assert cl >= thr, f"row sealed but coverage_lower {cl} < threshold {thr}"
