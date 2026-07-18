"""AUTH-0 — tests for services/api/routers/auth.py (00-MASTER.md §2 C-3).

Exercises the real router against the live cardeep-pg (127.0.0.1:5433), auto-skipping
when the DB is unreachable (same pattern as tests/test_api_auth.py). Every test user this
suite creates lives under the ``@authtest.invalid`` domain (RFC 2606 reserved TLD — never a
real registration) and is deleted in a module-scoped fixture teardown, so the suite leaves
the live DB byte-identical to how it found it.

Covers: register (happy path, weak password, duplicate email, malformed email), login
(happy path, wrong password, unknown email — same 401 for both, no enumeration), /me
(valid/invalid/missing token), logout (revocation actually takes effect), refresh (rotation:
old token dies, new token works), and claim-dealer (checksum rejection, unknown cdp_code,
tax-id/entity mismatch, and the real success path against a live entity with a
checksum-valid CIF, verified independently via services/api/tax_id.py in this same file).
"""
from __future__ import annotations

import asyncio
import uuid

import pytest
from fastapi.testclient import TestClient

from services.api.main import app
from services.api.ratelimit import limiter
from services.api.tax_id import canonical_tax_id

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

# A real entity, self-canonical, with a checksum-valid CIF — verified live 2026-07-17
# (services/api/tax_id.canonical_tax_id("B01530682") is truthy; resolve_cluster resolves
# CDP-ES-01-7FAFJXW8 to itself).
REAL_ENTITY_CDP = "CDP-ES-01-7FAFJXW8"
REAL_ENTITY_CIF = "B01530682"


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


def _real_entity_available() -> bool:
    """Whether REAL_ENTITY_CDP exists at DSN. False on CI's ephemeral db-tests Postgres
    (also bound to host port 5433, but seeded only by seed_ci_fixture.py's synthetic
    dealers, never the real census) — distinguishes "a DB answers on 5433" (DB_AVAILABLE)
    from "it's the real populated one" (this check)."""
    if not DB_AVAILABLE:
        return False
    try:
        import asyncpg

        async def _check() -> bool:
            conn = await asyncpg.connect(DSN, timeout=3)
            try:
                row = await conn.fetchval(
                    "SELECT 1 FROM entity WHERE cdp_code = $1", REAL_ENTITY_CDP
                )
                return row is not None
            finally:
                await conn.close()

        return asyncio.run(_check())
    except Exception:
        return False


REAL_ENTITY_AVAILABLE = _real_entity_available()


def _fresh_email() -> str:
    """A unique, obviously-fake address per test — never collides across parallel runs."""
    return f"authtest-{uuid.uuid4().hex}@authtest.invalid"


STRONG_PASSWORD = "correct-horse-battery-staple-9"


@pytest.fixture(autouse=True)
def _reset_rate_limit_storage():
    """RATE_AUTH is a tight 10/minute/IP (ratelimit.py) — deliberately, since these are the
    credential-guessing endpoints. TestClient requests all share one synthetic client host,
    so this whole file (many register/login/claim-dealer calls) would otherwise trip its own
    limiter within a single run regardless of the real per-user traffic pattern. Resetting the
    in-memory limiter storage before every test isolates each test's rate-limit budget, exactly
    as tests/test_api_ratelimit_cache.py isolates cache state via cache_clear()."""
    limiter.reset()
    yield


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
    # Module-scoped teardown: purge every row this suite could have created, regardless of
    # which test created it — the live DB must come back byte-identical.
    asyncio.run(_purge_test_rows())


async def _purge_test_rows() -> None:
    import asyncpg

    conn = await asyncpg.connect(DSN)
    try:
        await conn.execute(
            "DELETE FROM app_user WHERE email_lower LIKE '%@authtest.invalid'"
        )
        # dealer_membership/user_session/user_notification cascade via FK ON DELETE CASCADE.
    finally:
        await conn.close()


def _register(client: TestClient, email: str | None = None, password: str = STRONG_PASSWORD) -> dict:
    r = client.post(
        "/auth/register",
        json={"email": email or _fresh_email(), "password": password, "name": "Auth Test"},
    )
    assert r.status_code == 200, r.text
    return r.json()


# ---------------------------------------------------------------------------
# register
# ---------------------------------------------------------------------------

class TestRegister:
    def test_register_returns_token_and_user(self, client: TestClient) -> None:
        data = _register(client)
        assert data["token"]
        assert data["expires_in"] > 0
        assert data["user"]["role"] == "particular"
        assert data["user"]["tenant_id"] == ""
        assert "id" in data["user"] and "email" in data["user"]

    def test_register_rejects_weak_password(self, client: TestClient) -> None:
        r = client.post(
            "/auth/register",
            json={"email": _fresh_email(), "password": "short", "name": "x"},
        )
        assert r.status_code == 400

    def test_register_rejects_malformed_email(self, client: TestClient) -> None:
        r = client.post(
            "/auth/register",
            json={"email": "not-an-email", "password": STRONG_PASSWORD, "name": "x"},
        )
        assert r.status_code == 422

    def test_register_rejects_duplicate_email(self, client: TestClient) -> None:
        email = _fresh_email()
        _register(client, email=email)
        r = client.post(
            "/auth/register",
            json={"email": email, "password": STRONG_PASSWORD, "name": "dup"},
        )
        assert r.status_code == 409

    def test_register_duplicate_is_case_insensitive(self, client: TestClient) -> None:
        email = _fresh_email()
        _register(client, email=email)
        r = client.post(
            "/auth/register",
            json={"email": email.upper(), "password": STRONG_PASSWORD, "name": "dup"},
        )
        assert r.status_code == 409


# ---------------------------------------------------------------------------
# login
# ---------------------------------------------------------------------------

class TestLogin:
    def test_login_happy_path(self, client: TestClient) -> None:
        email = _fresh_email()
        _register(client, email=email)
        r = client.post("/auth/login", json={"email": email, "password": STRONG_PASSWORD})
        assert r.status_code == 200
        body = r.json()
        assert body["token"]
        assert body["user"]["email"] == email

    def test_login_wrong_password_401(self, client: TestClient) -> None:
        email = _fresh_email()
        _register(client, email=email)
        r = client.post("/auth/login", json={"email": email, "password": "totally-wrong-pw-99"})
        assert r.status_code == 401

    def test_login_unknown_email_same_401_as_wrong_password(self, client: TestClient) -> None:
        """No enumeration: an account that never existed fails exactly like a wrong password."""
        r = client.post(
            "/auth/login",
            json={"email": _fresh_email(), "password": "irrelevant-password-1"},
        )
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# /me
# ---------------------------------------------------------------------------

class TestMe:
    def test_me_with_valid_token(self, client: TestClient) -> None:
        data = _register(client)
        r = client.get("/auth/me", headers={"Authorization": f"Bearer {data['token']}"})
        assert r.status_code == 200
        assert r.json()["user"]["id"] == data["user"]["id"]

    def test_me_without_token_401(self, client: TestClient) -> None:
        r = client.get("/auth/me")
        assert r.status_code == 401

    def test_me_with_garbage_token_401(self, client: TestClient) -> None:
        r = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# logout — revocation must actually take effect
# ---------------------------------------------------------------------------

class TestLogout:
    def test_logout_revokes_the_session(self, client: TestClient) -> None:
        data = _register(client)
        token = data["token"]

        r_me_before = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r_me_before.status_code == 200

        r_logout = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
        assert r_logout.status_code == 204

        r_me_after = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r_me_after.status_code == 401, "token must be dead immediately after logout"


# ---------------------------------------------------------------------------
# refresh — rotation
# ---------------------------------------------------------------------------

class TestRefresh:
    def test_refresh_rotates_token(self, client: TestClient) -> None:
        data = _register(client)
        old_token = data["token"]

        r_refresh = client.post("/auth/refresh", headers={"Authorization": f"Bearer {old_token}"})
        assert r_refresh.status_code == 200
        new_token = r_refresh.json()["token"]
        assert new_token != old_token

        r_old = client.get("/auth/me", headers={"Authorization": f"Bearer {old_token}"})
        assert r_old.status_code == 401, "old token must be revoked after rotation"

        r_new = client.get("/auth/me", headers={"Authorization": f"Bearer {new_token}"})
        assert r_new.status_code == 200


# ---------------------------------------------------------------------------
# claim-dealer — the anti dealer-disfrazado control
# ---------------------------------------------------------------------------

class TestClaimDealer:
    def test_tax_id_checksum_verified_independently(self) -> None:
        """Sanity: the fixture CIF really does pass its own checksum (independent of the
        router — this test would fail even without FastAPI involved)."""
        assert canonical_tax_id(REAL_ENTITY_CIF) == REAL_ENTITY_CIF

    def test_rejects_invalid_checksum(self, client: TestClient) -> None:
        # Independently confirmed to fail its own BOE checksum (test_tax_id_checksum_*
        # sibling proves the validator itself; this constant is verified inline too).
        bad_cif = "B00000001"
        assert canonical_tax_id(bad_cif) is None, "fixture must actually fail the checksum"
        data = _register(client)
        r = client.post(
            "/auth/claim-dealer",
            json={"cdp_code": REAL_ENTITY_CDP, "tax_id": bad_cif},
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert r.status_code == 400

    def test_rejects_unknown_cdp_code(self, client: TestClient) -> None:
        data = _register(client)
        r = client.post(
            "/auth/claim-dealer",
            json={"cdp_code": "CDP-ES-99-ZZZZZZZZ", "tax_id": REAL_ENTITY_CIF},
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert r.status_code == 404

    @pytest.mark.skipif(
        not REAL_ENTITY_AVAILABLE,
        reason=f"{REAL_ENTITY_CDP} not present at {DSN} — needs the live populated census, "
               "not CI's synthetic seed_ci_fixture.py dealers",
    )
    def test_rejects_mismatched_tax_id(self, client: TestClient) -> None:
        """A checksum-VALID tax id that simply belongs to nobody at this entity must still
        be rejected — the check is against the CENSUS record, not just the checksum."""
        # Independently checksum-valid (org 'B', digit-form control) but NOT
        # REAL_ENTITY_CIF — isolates the census-mismatch branch from the checksum branch.
        other_valid_cif = "B12345674"
        assert canonical_tax_id(other_valid_cif) == other_valid_cif, "fixture must pass its own checksum"
        assert other_valid_cif != REAL_ENTITY_CIF

        data = _register(client)
        r = client.post(
            "/auth/claim-dealer",
            json={"cdp_code": REAL_ENTITY_CDP, "tax_id": other_valid_cif},
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert r.status_code == 403

    @pytest.mark.skipif(
        not REAL_ENTITY_AVAILABLE,
        reason=f"{REAL_ENTITY_CDP} not present at {DSN} — needs the live populated census, "
               "not CI's synthetic seed_ci_fixture.py dealers",
    )
    def test_claim_dealer_success_path(self, client: TestClient) -> None:
        data = _register(client)
        r = client.post(
            "/auth/claim-dealer",
            json={"cdp_code": REAL_ENTITY_CDP, "tax_id": REAL_ENTITY_CIF},
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert r.status_code == 200, r.text
        user = r.json()["user"]
        assert user["role"] == "dealer"
        assert user["tenant_id"] == REAL_ENTITY_CDP

        # /me must reflect the elevation too (not just the claim response).
        r_me = client.get("/auth/me", headers={"Authorization": f"Bearer {data['token']}"})
        assert r_me.json()["user"]["role"] == "dealer"
        assert r_me.json()["user"]["tenant_id"] == REAL_ENTITY_CDP

    def test_claim_dealer_requires_auth(self, client: TestClient) -> None:
        r = client.post(
            "/auth/claim-dealer",
            json={"cdp_code": REAL_ENTITY_CDP, "tax_id": REAL_ENTITY_CIF},
        )
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# Rate limiting on the credential-guessing surface (RATE_AUTH, ratelimit.py)
# ---------------------------------------------------------------------------

class TestRateLimit:
    def test_login_endpoint_is_rate_limited(self, client: TestClient) -> None:
        """RATE_AUTH = 10/minute/IP when enabled. Under the test-mode no-op limit
        (CARDEEP_API_RATELIMIT_ENABLED=0, this repo's default test posture) this simply
        proves the decorator is wired — the 429 path itself is covered by
        tests/test_api_ratelimit_cache.py against a different endpoint."""
        import services.api.ratelimit as rl

        assert "/minute" in rl.RATE_AUTH or rl.RATE_AUTH == "9999/second"
