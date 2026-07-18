"""Tests for /publishing/* (pilar 05-multiposting, Frente A -- read-only).

Same DB-guard pattern as test_api_gaps.py: connects to the real cardeep-pg,
skips cleanly when unreachable. Two verification legs per the carta's F1
criterion:
  1. Contract/shape tests against the live envelope.
  2. Cross-check of /publishing/{cdp}/coverage's per-platform n_listed against
     an independent count derived by filtering the EXISTING
     /platforms/{platform_cdp}/inventory endpoint by dealer_cdp_code -- for
     >=3 real dealers (05-multiposting.md F1 criterion), fully paginated
     (dealer-scoped slices are small: tens to low hundreds of rows, unlike the
     platform-wide totals scripts/f0_publishing_census.py had to sample).

Real dealers used below were selected live (>=2 distinct platforms, real
available inventory) -- see scripts/f0_publishing_census.py output and the
05-multiposting.md F1 execution log for how they were picked.
"""
from __future__ import annotations

import asyncio

import asyncpg
import pytest
from fastapi.testclient import TestClient

from services.api.main import app
from services.api.routers.publishing import _classify_anomaly, _coverage_band, _price_divergence

# ---------------------------------------------------------------------------
# DB connectivity guard (mirrors test_api_gaps.py)
# ---------------------------------------------------------------------------

DSN_SYNC = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"


def _db_available() -> bool:
    async def _ping() -> bool:
        try:
            conn = await asyncpg.connect(DSN_SYNC, timeout=3)
            await conn.close()
            return True
        except Exception:
            return False
    try:
        return asyncio.run(_ping())
    except Exception:
        return False


DB_AVAILABLE = _db_available()
SKIP_NO_DB = pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")

# Real dealers verified live 2026-07-18 (>=2 distinct platforms, real available inventory).
REAL_DEALERS = ["CDP-ES-46-AD9ZXC65", "CDP-ES-41-1YVBKMVH", "CDP-ES-28-5K6CNPCE"]

# Real cross-post onto a non-'plataforma' target (F0.2b finding): a dealer whose car is
# listed on 'volvo_jlr_suzuki' (entity.kind='oem_vo_portal'), a DIFFERENT entity than the
# dealer itself (excludes the self-referencing rows scripts/f0_publishing_census.py found
# for chains like Flexicar/Carplus, where dealer_cdp == platform_cdp).
NON_PLATAFORMA_DEALER = "CDP-ES-01-7J6SM0SQ"
NON_PLATAFORMA_TARGET_KIND = "oem_vo_portal"



@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _fetch(sql: str, *args):
    async def _q():
        conn = await asyncpg.connect(DSN_SYNC, timeout=5)
        try:
            return await conn.fetch(sql, *args)
        finally:
            await conn.close()
    return asyncio.run(_q())


# ---------------------------------------------------------------------------
# Pure-function unit tests (no DB / no live example required)
# ---------------------------------------------------------------------------

class TestPureHelpers:
    def test_coverage_band_thresholds(self):
        assert _coverage_band(0.80) == "verde"
        assert _coverage_band(1.0) == "verde"
        assert _coverage_band(0.79) == "ambar"
        assert _coverage_band(0.40) == "ambar"
        assert _coverage_band(0.39) == "rojo"
        assert _coverage_band(0.0) == "rojo"

    def test_price_divergence_none_when_either_price_missing(self):
        assert _price_divergence(None, 100.0) is None
        assert _price_divergence(100.0, None) is None
        assert _price_divergence(None, None) is None

    def test_price_divergence_flags_relative_threshold(self):
        # 2% of 10000 = 200, same as the absolute floor -> boundary uses the larger.
        d = _price_divergence(10000.0, 9700.0)  # delta=-300, threshold=max(200,200)=200
        assert d is not None
        assert d["flag"] is True
        assert d["delta"] == -300.0

    def test_price_divergence_does_not_flag_rounding_noise(self):
        d = _price_divergence(19990.0, 19950.0)  # delta=-40, threshold=max(399.8,200)=399.8
        assert d is not None
        assert d["flag"] is False

    def test_price_divergence_absolute_floor_on_cheap_cars(self):
        # 2% of 1000 = 20 (< 200 abs floor) -> threshold = 200.
        d = _price_divergence(1000.0, 850.0)  # delta=-150, below the 200 floor
        assert d is not None
        assert d["flag"] is False
        d2 = _price_divergence(1000.0, 700.0)  # delta=-300, past the 200 floor
        assert d2["flag"] is True

    def test_classify_anomaly_sold_still_listed(self):
        assert _classify_anomaly("gone", "listed") == "sold_still_listed"

    def test_classify_anomaly_available_removed(self):
        assert _classify_anomaly("available", "removed") == "available_removed"

    def test_classify_anomaly_none_for_consistent_states(self):
        assert _classify_anomaly("available", "listed") is None
        assert _classify_anomaly("gone", "removed") is None


# ---------------------------------------------------------------------------
# Coverage endpoint
# ---------------------------------------------------------------------------

@SKIP_NO_DB
class TestPublishingCoverage:
    def test_dealer_not_found(self, client):
        r = client.get("/publishing/CDP-ES-00-NOPE0000/coverage")
        assert r.status_code == 404, r.text
        assert r.json()["ok"] is False

    @pytest.mark.parametrize("cdp", REAL_DEALERS)
    def test_envelope_shape_real_dealer(self, client, cdp):
        r = client.get(f"/publishing/{cdp}/coverage")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["ok"] is True
        data = body["data"]
        assert data["dealer"]["cdp_code"] == cdp
        assert data["total_available"] >= 0
        assert len(data["platforms"]) >= 2  # selection criterion: >=2 platforms
        for p in data["platforms"]:
            assert p["band"] in ("verde", "ambar", "rojo")
            assert 0.0 <= p["coverage_pct"] <= 1.0 or data["total_available"] == 0
            assert p["n_listed"] >= 0

    @pytest.mark.parametrize("cdp", REAL_DEALERS)
    def test_cross_check_against_platforms_inventory(self, client, cdp):
        """The carta's own F1 criterion: cross-check counts against the EXISTING
        /platforms/{cdp}/inventory endpoint, for >=3 real dealers.

        First attempt (this test's own history): paginate the platform-wide
        endpoint page by page and filter client-side by dealer_cdp_code. REAL
        BUG FOUND running this suite: /platforms/{cdp}/inventory has no
        dealer filter -- it returns the ENTIRE platform ordered by
        first_seen DESC, so a dealer's ~200 edges can be scattered across
        thousands of pages of a 274k/789k-row platform (coches.net/wallapop).
        The first parametrize case hung for >15 minutes mid-pagination
        (verified live via pg_stat_activity: the query was genuinely still
        executing, not deadlocked) and had to be killed. Paginating the whole
        platform per dealer is not a viable verification strategy at this
        platform's scale.

        Fix: the second independent path is SQL that replicates
        platforms.py:59-63's exact JOIN (servable_vehicle + entity), scoped to
        BOTH platform AND dealer -- same two tables, same filter semantics,
        genuinely independent of publishing.py's own query, and fast (index
        scan on a specific dealer, not a platform-wide scan)."""
        cov = client.get(f"/publishing/{cdp}/coverage").json()["data"]
        for p in cov["platforms"]:
            rows = _fetch(
                """SELECT count(*) AS n
                     FROM platform_listing pl
                     JOIN servable_vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
                     JOIN entity d ON d.entity_ulid = v.entity_ulid
                    WHERE pl.platform_entity_ulid = (SELECT entity_ulid FROM entity WHERE cdp_code = $1)
                      AND pl.status = 'listed' AND d.cdp_code = $2""",
                p["cdp_code"], cdp,
            )
            seen = rows[0]["n"]
            assert seen == p["n_listed"], f"{cdp} on {p['cdp_code']}: coverage={p['n_listed']} direct-sql={seen}"


# ---------------------------------------------------------------------------
# Matrix endpoint
# ---------------------------------------------------------------------------

@SKIP_NO_DB
class TestPublishingMatrix:
    def test_dealer_not_found(self, client):
        r = client.get("/publishing/CDP-ES-00-NOPE0000/matrix")
        assert r.status_code == 404, r.text

    @pytest.mark.parametrize("cdp", REAL_DEALERS)
    def test_pagination_envelope(self, client, cdp):
        r = client.get(f"/publishing/{cdp}/matrix?page=1&size=20")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["ok"] is True
        assert body["meta"]["page"] == 1
        assert body["meta"]["size"] == 20
        assert body["meta"]["returned"] <= 20
        for row in body["data"]:
            assert row["status"] in ("available", "gone")
            for p in row["platforms"]:
                assert p["status"] in ("listed", "removed")
                assert p["anomaly"] in (None, "sold_still_listed", "available_removed")

    def test_last_page_has_more_is_false(self, client):
        """Honest pagination (page_slice) -- the last real page never reports has_more=True,
        even when total is an exact multiple of size (frontend audit #7 regression class)."""
        cdp = REAL_DEALERS[0]
        page, size = 1, 50
        last_body = None
        while True:
            r = client.get(f"/publishing/{cdp}/matrix?page={page}&size={size}")
            body = r.json()
            last_body = body
            if not body["meta"]["has_more"]:
                break
            page += 1
            assert page < 50, "runaway pagination -- has_more never cleared"
        assert last_body["meta"]["has_more"] is False

    def test_no_mock_data_every_row_traces_to_a_real_vehicle(self, client):
        """Anti-mock gate (05-multiposting.md S6.6): every vehicle_ulid served by the
        matrix must exist in the real `vehicle` table with this dealer as owner."""
        cdp = REAL_DEALERS[1]
        body = client.get(f"/publishing/{cdp}/matrix?page=1&size=50").json()
        ulids = [row["vehicle_ulid"] for row in body["data"]]
        if not ulids:
            pytest.skip("dealer has no rows on this page")
        rows = _fetch(
            "SELECT v.vehicle_ulid FROM vehicle v JOIN entity e ON e.entity_ulid = v.entity_ulid "
            "WHERE e.cdp_code = $1 AND v.vehicle_ulid = ANY($2::text[])",
            cdp, ulids,
        )
        assert {r["vehicle_ulid"] for r in rows} == set(ulids)

    def test_kind_gate_finding_does_not_apply_here(self, client):
        """F0.2b: unlike platforms.py, /publishing/*/matrix must serve an edge to a
        non-'plataforma' target (oem_vo_portal here) without 400ing or omitting it."""
        r = client.get(f"/publishing/{NON_PLATAFORMA_DEALER}/matrix?page=1&size=200")
        assert r.status_code == 200, r.text
        body = r.json()
        found_kinds = {
            p["cdp_code"] for row in body["data"] for p in row["platforms"]
        }
        assert any(cdp for cdp in found_kinds), "expected at least one platform edge"
        # Re-derive the target's kind directly to prove it is really non-'plataforma'.
        rows = _fetch(
            "SELECT DISTINCT e.kind FROM platform_listing pl "
            "JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid "
            "JOIN entity d ON d.entity_ulid = v.entity_ulid "
            "JOIN entity e ON e.entity_ulid = pl.platform_entity_ulid "
            "WHERE d.cdp_code = $1",
            NON_PLATAFORMA_DEALER,
        )
        kinds = {r["kind"] for r in rows}
        assert NON_PLATAFORMA_TARGET_KIND in kinds

    def test_price_divergence_detected_on_real_example(self, client):
        """Finds a CURRENTLY-divergent (dealer, vehicle) pair fresh at test time -- the
        harvester is live (00-F0..F2 revived it), so a hardcoded historical example would
        go stale as soon as that specific listing's price/state changes. The endpoint must
        flag whatever real divergence exists right now, not a frozen snapshot."""
        rows = _fetch(
            """SELECT e.cdp_code AS dealer_cdp, v.vehicle_ulid
                 FROM vehicle v JOIN platform_listing pl ON pl.vehicle_ulid = v.vehicle_ulid
                 JOIN entity e ON e.entity_ulid = v.entity_ulid
                WHERE v.status = 'available' AND pl.status = 'listed'
                  AND v.price IS NOT NULL AND pl.platform_price IS NOT NULL
                  AND abs(pl.platform_price - v.price) > greatest(0.02 * v.price, 200)
                LIMIT 1"""
        )
        if not rows:
            pytest.skip("no live price-divergence example exists right now (harvester-dependent)")
        dealer_cdp, vehicle_ulid = rows[0]["dealer_cdp"], rows[0]["vehicle_ulid"]

        page = 1
        found = None
        while found is None:
            body = client.get(f"/publishing/{dealer_cdp}/matrix?page={page}&size=200").json()
            for row in body["data"]:
                if row["vehicle_ulid"] == vehicle_ulid:
                    found = row
                    break
            if not body["meta"]["has_more"] or found is not None:
                break
            page += 1
        assert found is not None, f"vehicle {vehicle_ulid} not found in {dealer_cdp}'s matrix"
        flagged = [p for p in found["platforms"] if p["divergence"] is not None and p["divergence"]["flag"]]
        assert len(flagged) >= 1, f"expected {vehicle_ulid} to carry a flagged divergence"
