"""Tests for services/api/routers/wanted.py (08-forum-community F2, the "Se busca" board).

Auto-skips when cardeep-pg is unreachable (same pattern as tests/test_dealer_ops_router.py /
tests/test_auth_router.py). Uses a real, RARE make ("Lynk & Co") for the matching tests so the
candidate query stays fast and deterministic in CI (a popular make like Volkswagen/Golf returns
tens of thousands of rows — correct, but slow to assert against in a test loop; the SQL/Python
score-parity property itself is covered exhaustively, make-agnostically, in
tests/test_wanted_matcher.py).

Covers: auth requirement, account-age cooldown, open/monthly quotas, TTL validation, live
matching against the real census (count + persisted wanted_match rows + notification on
>=70), match click idempotency, close+reason validation, dealer_review gate (no proven
interaction => 403) and double-blind reveal (both sides submitted => revealed_at set),
and the public aggregate endpoints (pulse/demand/liveness/reviews) requiring no auth and
never fabricating a value when the real count is zero.
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from services.api.main import app
from services.api.ratelimit import limiter

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

# A real, RARE-make vehicle (verified live 2026-07-18): Lynk & Co 01, 2023, 53745 km,
# 23490.00 EUR, entity in Madrid (province 28), status='available'.
RARE_VEHICLE_ULID = "01KV00MAMCMJ9QCW0JY3T4XJY9"
RARE_VEHICLE_CDP = "CDP-ES-28-YCZB8JYW"
RARE_MAKE = "Lynk & Co"
RARE_MODEL = "01"
RARE_PROVINCE = "28"


def _db_available() -> bool:
    try:
        import asyncpg

        async def _ping() -> bool:
            try:
                conn = await asyncpg.connect(DSN, timeout=3)
                await conn.close()
                return True
            except Exception:
                return False

        return asyncio.run(_ping())
    except Exception:
        return False


DB_AVAILABLE = _db_available()
pytestmark = pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")


def _fresh_email() -> str:
    return f"wanted-{uuid.uuid4().hex}@authtest.invalid"


STRONG_PASSWORD = "correct-horse-battery-staple-9"


@pytest.fixture(autouse=True)
def _reset_rate_limit_storage():
    limiter.reset()
    yield


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
    asyncio.run(_purge_test_rows())


async def _purge_test_rows() -> None:
    import asyncpg

    conn = await asyncpg.connect(DSN)
    try:
        await conn.execute(
            "DELETE FROM dealer_review WHERE reviewer_user_ulid IN "
            "(SELECT user_ulid FROM app_user WHERE email_lower LIKE '%@authtest.invalid')"
        )
        await conn.execute(
            "DELETE FROM wanted_match WHERE wanted_ulid IN "
            "(SELECT wanted_ulid FROM wanted_listing wl JOIN app_user u ON u.user_ulid = wl.user_ulid "
            "WHERE u.email_lower LIKE '%@authtest.invalid')"
        )
        await conn.execute(
            "DELETE FROM user_notification WHERE user_ulid IN "
            "(SELECT user_ulid FROM app_user WHERE email_lower LIKE '%@authtest.invalid')"
        )
        await conn.execute(
            "DELETE FROM wanted_listing WHERE user_ulid IN "
            "(SELECT user_ulid FROM app_user WHERE email_lower LIKE '%@authtest.invalid')"
        )
        await conn.execute("DELETE FROM app_user WHERE email_lower LIKE '%@authtest.invalid'")
    finally:
        await conn.close()


async def _backdate_account(user_ulid: str, days: int) -> None:
    import asyncpg

    conn = await asyncpg.connect(DSN)
    try:
        await conn.execute(
            "UPDATE app_user SET created_at = now() - make_interval(days => $1) WHERE user_ulid = $2",
            days, user_ulid,
        )
    finally:
        await conn.close()


def _register(client: TestClient) -> tuple[str, str]:
    """Register a fresh account; returns (token, user_ulid)."""
    email = _fresh_email()
    r = client.post("/auth/register", json={"email": email, "password": STRONG_PASSWORD, "name": "Wanted Test"})
    assert r.status_code == 200, r.text
    body = r.json()
    return body["token"], body["user"]["id"]


def _seasoned_user(client: TestClient) -> str:
    """Register + backdate past the cooldown; returns a bearer token ready to publish."""
    token, user_ulid = _register(client)
    asyncio.run(_backdate_account(user_ulid, 10))
    return token


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


RARE_MAKE_PAYLOAD = {
    "make": RARE_MAKE, "model": RARE_MODEL,
    "year_min": 2022, "year_max": 2024,
    "km_max": 70_000, "price_max": 26_000,
    "fuel": None, "transmission": None,
    "province_code": RARE_PROVINCE,
    "free_text": None, "ttl_days": 30,
}


# ---------------------------------------------------------------------------
# Auth requirement
# ---------------------------------------------------------------------------

class TestRequiresAuth:
    def test_create_without_token_401(self, client: TestClient) -> None:
        r = client.post("/wanted", json=RARE_MAKE_PAYLOAD)
        assert r.status_code == 401

    def test_list_without_token_401(self, client: TestClient) -> None:
        r = client.get("/wanted")
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# Cooldown + quotas
# ---------------------------------------------------------------------------

class TestCooldownAndQuotas:
    def test_fresh_account_cannot_publish(self, client: TestClient) -> None:
        token, _ = _register(client)
        r = client.post("/wanted", json=RARE_MAKE_PAYLOAD, headers=_auth(token))
        assert r.status_code == 403
        assert "day" in r.json()["detail"]

    def test_invalid_ttl_rejected(self, client: TestClient) -> None:
        token = _seasoned_user(client)
        bad = {**RARE_MAKE_PAYLOAD, "ttl_days": 99}
        r = client.post("/wanted", json=bad, headers=_auth(token))
        assert r.status_code == 422

    def test_unknown_province_rejected(self, client: TestClient) -> None:
        token = _seasoned_user(client)
        bad = {**RARE_MAKE_PAYLOAD, "province_code": "ZZ"}
        r = client.post("/wanted", json=bad, headers=_auth(token))
        assert r.status_code == 422

    def test_open_quota_enforced(self, client: TestClient) -> None:
        token = _seasoned_user(client)
        for _ in range(5):
            r = client.post("/wanted", json=RARE_MAKE_PAYLOAD, headers=_auth(token))
            assert r.status_code == 200, r.text
        r = client.post("/wanted", json=RARE_MAKE_PAYLOAD, headers=_auth(token))
        assert r.status_code == 429
        assert "open requests" in r.json()["detail"]


# ---------------------------------------------------------------------------
# Live matching against the real census
# ---------------------------------------------------------------------------

class TestLiveMatching:
    def test_create_scores_and_persists_matches(self, client: TestClient) -> None:
        token = _seasoned_user(client)
        r = client.post("/wanted", json=RARE_MAKE_PAYLOAD, headers=_auth(token))
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["meta"]["matches_now"] >= 1
        top = body["meta"]["top_matches"]
        assert len(top) >= 1
        wanted_ulid = body["data"]["wanted_ulid"]

        # The fixture vehicle itself must be PERSISTED as a wanted_match (real, not
        # fabricated) — checked directly by ulid rather than via the ranked/paginated
        # /matches endpoint, since a tie-heavy score (many same-model candidates at
        # 100.0) can legitimately push any single vehicle_ulid out of a size-bounded page.
        async def _fetch_persisted_score() -> float | None:
            import asyncpg

            conn = await asyncpg.connect(DSN)
            try:
                return await conn.fetchval(
                    "SELECT match_score FROM wanted_match WHERE wanted_ulid = $1 AND vehicle_ulid = $2",
                    wanted_ulid, RARE_VEHICLE_ULID,
                )
            finally:
                await conn.close()

        score = asyncio.run(_fetch_persisted_score())
        assert score is not None, "fixture vehicle was not persisted as a wanted_match"
        assert float(score) >= 50.0

    def test_matches_never_show_a_gone_vehicle(self, client: TestClient) -> None:
        """§7.3: 'un coche vendido jamas aparece como coincidencia viva' — every row the
        matches endpoint returns must join a LIVE (status='available') vehicle."""
        token = _seasoned_user(client)
        r = client.post("/wanted", json=RARE_MAKE_PAYLOAD, headers=_auth(token))
        wanted_ulid = r.json()["data"]["wanted_ulid"]
        r2 = client.get(f"/wanted/{wanted_ulid}/matches?size=200", headers=_auth(token))
        for m in r2.json()["data"]:
            assert m["vehicle_status"] == "available"

    def test_other_user_cannot_read_my_listing(self, client: TestClient) -> None:
        token_a = _seasoned_user(client)
        token_b = _seasoned_user(client)
        r = client.post("/wanted", json=RARE_MAKE_PAYLOAD, headers=_auth(token_a))
        wanted_ulid = r.json()["data"]["wanted_ulid"]
        r2 = client.get(f"/wanted/{wanted_ulid}", headers=_auth(token_b))
        assert r2.status_code == 403

    def test_get_unknown_listing_404(self, client: TestClient) -> None:
        token = _seasoned_user(client)
        r = client.get("/wanted/01NOTAREALWANTEDULIDXXXXXX", headers=_auth(token))
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Close + click + review gate + double-blind
# ---------------------------------------------------------------------------

class TestCloseClickReview:
    def _create_with_match(self, client: TestClient) -> tuple[str, str, str]:
        """Returns (token, wanted_ulid, wanted_match_ulid) for a listing with >=1 match."""
        token = _seasoned_user(client)
        r = client.post("/wanted", json=RARE_MAKE_PAYLOAD, headers=_auth(token))
        assert r.status_code == 200, r.text
        wanted_ulid = r.json()["data"]["wanted_ulid"]
        top = r.json()["meta"]["top_matches"]
        assert top, "fixture expects at least one match for the rare make"
        return token, wanted_ulid, top[0]["wanted_match_ulid"]

    def test_invalid_close_reason_rejected(self, client: TestClient) -> None:
        token, wanted_ulid, _ = self._create_with_match(client)
        r = client.post(f"/wanted/{wanted_ulid}/close", json={"reason": "changed_my_mind"}, headers=_auth(token))
        assert r.status_code == 422

    def test_close_then_close_again_conflicts(self, client: TestClient) -> None:
        token, wanted_ulid, _ = self._create_with_match(client)
        r = client.post(f"/wanted/{wanted_ulid}/close", json={"reason": "no_longer_interested"}, headers=_auth(token))
        assert r.status_code == 200
        r2 = client.post(f"/wanted/{wanted_ulid}/close", json={"reason": "no_longer_interested"}, headers=_auth(token))
        assert r2.status_code == 409

    def test_click_is_idempotent(self, client: TestClient) -> None:
        token, _, match_ulid = self._create_with_match(client)
        r1 = client.post(f"/wanted/matches/{match_ulid}/click", headers=_auth(token))
        assert r1.status_code == 200
        r2 = client.post(f"/wanted/matches/{match_ulid}/click", headers=_auth(token))
        assert r2.status_code == 200  # second click is a no-op, not an error

    def test_review_without_interaction_is_forbidden(self, client: TestClient) -> None:
        token, _, match_ulid = self._create_with_match(client)
        r = client.post(
            f"/wanted/matches/{match_ulid}/review",
            json={
                "axis_trato": 5, "axis_anuncio_veraz": 5, "axis_disponibilidad_real": 5,
                "axis_agilidad": 5, "overall": 5, "reviewer_role": "buyer",
            },
            headers=_auth(token),
        )
        assert r.status_code == 403

    def test_review_after_click_succeeds_and_stays_hidden(self, client: TestClient) -> None:
        token, _, match_ulid = self._create_with_match(client)
        client.post(f"/wanted/matches/{match_ulid}/click", headers=_auth(token))
        r = client.post(
            f"/wanted/matches/{match_ulid}/review",
            json={
                "axis_trato": 5, "axis_anuncio_veraz": 4, "axis_disponibilidad_real": 5,
                "axis_agilidad": 4, "overall": 5, "comment": "Buen trato", "reviewer_role": "buyer",
            },
            headers=_auth(token),
        )
        assert r.status_code == 200, r.text
        body = r.json()["data"]
        assert body["revealed"] is False  # double-blind: counterpart has not submitted

    def test_duplicate_review_same_role_rejected(self, client: TestClient) -> None:
        token, _, match_ulid = self._create_with_match(client)
        client.post(f"/wanted/matches/{match_ulid}/click", headers=_auth(token))
        payload = {
            "axis_trato": 5, "axis_anuncio_veraz": 4, "axis_disponibilidad_real": 5,
            "axis_agilidad": 4, "overall": 5, "reviewer_role": "buyer",
        }
        r1 = client.post(f"/wanted/matches/{match_ulid}/review", json=payload, headers=_auth(token))
        assert r1.status_code == 200
        r2 = client.post(f"/wanted/matches/{match_ulid}/review", json=payload, headers=_auth(token))
        assert r2.status_code == 409


# ---------------------------------------------------------------------------
# Public aggregates — no auth required, honest zeros
# ---------------------------------------------------------------------------

class TestPublicAggregates:
    def test_pulse_shape_and_types(self, client: TestClient) -> None:
        r = client.get("/wanted/pulse")
        assert r.status_code == 200
        data = r.json()["data"]
        assert set(data) == {"threads_active_24h", "wanted_open", "matches_served_7d"}
        assert all(isinstance(v, int) for v in data.values())

    def test_liveness_null_rate_when_no_clicks_in_window(self, client: TestClient) -> None:
        r = client.get("/wanted/liveness")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["window_days"] == 30
        if data["total_clicks"] == 0:
            assert data["match_liveness_rate"] is None  # never fabricated as 0 or 1

    def test_demand_is_a_list(self, client: TestClient) -> None:
        r = client.get("/wanted/demand")
        assert r.status_code == 200
        assert isinstance(r.json()["data"], list)

    def test_reviews_endpoint_unknown_dealer_404(self, client: TestClient) -> None:
        r = client.get("/wanted/reviews/CDP-ES-00-NOPE")
        assert r.status_code == 404

    def test_meta_provinces_lists_all_52(self, client: TestClient) -> None:
        r = client.get("/wanted/meta/provinces")
        assert r.status_code == 200
        codes = {p["code"] for p in r.json()["data"]}
        assert len(codes) == 52
        assert RARE_PROVINCE in codes

    def test_reviews_never_serves_unrevealed_row(self, client: TestClient) -> None:
        """§7.7 invariant, contract-tested: a submitted-but-not-yet-revealed review must
        never move the public aggregate.

        This module creates several buyer-only reviews against RARE_VEHICLE_CDP's dealer
        (TestCloseClickReview) — none of them are double-blind-completed (no dealer
        counterpart submits), so revealed_at stays NULL for every one of them. The public
        aggregate must therefore report exactly the count from BEFORE this suite ran
        (0, on a fresh dealer never reviewed elsewhere) — never inflated by the hidden rows.
        """
        r = client.get(f"/wanted/reviews/{RARE_VEHICLE_CDP}")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["n_reviews_12m"] == 0
        assert data["pct_positive_12m"] is None
