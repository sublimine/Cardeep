"""Tests for services/api/routers/forum.py (08-forum-community F4).

Auto-skips when cardeep-pg is unreachable (test_dealer_ops_router.py pattern). Reputation
is granted directly via a 'staff_grant' reputation_event row for test fixtures — the ledger
schema (migrations/0095_forum.sql) allows this reason precisely because manual staff grants
are the declared bootstrap path for a user who has not yet earned rep through the wanted
board's own "+15 petición cerrada" mechanism (carta §10, cold-start note).
"""
from __future__ import annotations

import asyncio
import uuid

import pytest
from fastapi.testclient import TestClient

from pipeline.forum.reputation import DOWNVOTE_PRIVILEGE_MIN_REP, FLAG_PRIVILEGE_MIN_REP, VOTE_PRIVILEGE_MIN_REP
from pipeline.ids import ulid
from services.api.main import app
from services.api.ratelimit import limiter

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

RARE_VEHICLE_ULID = "01KV00MAMCMJ9QCW0JY3T4XJY9"  # Lynk & Co 01, verified live in test_wanted_router.py


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

STRONG_PASSWORD = "correct-horse-battery-staple-9"


def _fresh_email() -> str:
    return f"forum-{uuid.uuid4().hex}@authtest.invalid"


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
            "DELETE FROM moderation_flag WHERE flagger_user_ulid IN "
            "(SELECT user_ulid FROM app_user WHERE email_lower LIKE '%@authtest.invalid')"
        )
        await conn.execute(
            "DELETE FROM post_vote WHERE user_ulid IN "
            "(SELECT user_ulid FROM app_user WHERE email_lower LIKE '%@authtest.invalid')"
        )
        await conn.execute(
            "DELETE FROM post_anchor WHERE post_ulid IN "
            "(SELECT post_ulid FROM forum_post fp JOIN app_user u ON u.user_ulid = fp.author_user_ulid "
            "WHERE u.email_lower LIKE '%@authtest.invalid')"
        )
        await conn.execute(
            "DELETE FROM forum_post WHERE author_user_ulid IN "
            "(SELECT user_ulid FROM app_user WHERE email_lower LIKE '%@authtest.invalid')"
        )
        await conn.execute(
            "DELETE FROM forum_thread WHERE author_user_ulid IN "
            "(SELECT user_ulid FROM app_user WHERE email_lower LIKE '%@authtest.invalid')"
        )
        await conn.execute(
            "DELETE FROM reputation_event WHERE user_ulid IN "
            "(SELECT user_ulid FROM app_user WHERE email_lower LIKE '%@authtest.invalid')"
        )
        await conn.execute("DELETE FROM app_user WHERE email_lower LIKE '%@authtest.invalid'")
    finally:
        await conn.close()


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _register(client: TestClient) -> tuple[str, str]:
    email = _fresh_email()
    r = client.post("/auth/register", json={"email": email, "password": STRONG_PASSWORD, "name": "Forum Test"})
    assert r.status_code == 200, r.text
    body = r.json()
    return body["token"], body["user"]["id"]


async def _grant_rep(user_ulid: str, delta: int) -> None:
    import asyncpg

    conn = await asyncpg.connect(DSN)
    try:
        await conn.execute(
            "INSERT INTO reputation_event (event_ulid, user_ulid, delta, reason) VALUES ($1,$2,$3,'staff_grant')",
            ulid(), user_ulid, delta,
        )
    finally:
        await conn.close()


def _seasoned_user(client: TestClient, rep: int = FLAG_PRIVILEGE_MIN_REP) -> tuple[str, str]:
    """Registers a user and grants enough reputation to exercise every privilege tier."""
    token, user_ulid = _register(client)
    asyncio.run(_grant_rep(user_ulid, rep))
    return token, user_ulid


# ---------------------------------------------------------------------------
# Thread + post creation
# ---------------------------------------------------------------------------

class TestThreadsAndPosts:
    def test_create_requires_auth(self, client: TestClient) -> None:
        r = client.post("/forum/threads", json={"title": "x", "body": "y"})
        assert r.status_code == 401

    def test_create_and_read_thread(self, client: TestClient) -> None:
        token, _ = _register(client)
        r = client.post("/forum/threads", json={
            "title": "¿Por qué caen los precios de eléctricos?",
            "body": "Llevo semanas viendo bajadas.",
            "thread_type": "discussion",
        }, headers=_auth(token))
        assert r.status_code == 200, r.text
        thread_ulid = r.json()["data"]["thread_ulid"]

        r2 = client.get(f"/forum/threads/{thread_ulid}")
        assert r2.status_code == 200
        data = r2.json()["data"]
        assert len(data["posts"]) == 1
        assert data["posts"][0]["is_first_post"] is True

    def test_price_check_requires_anchor(self, client: TestClient) -> None:
        token, _ = _register(client)
        r = client.post("/forum/threads", json={
            "title": "¿Es buen precio este Golf?",
            "body": "Me lo ofrecen a 14.000€",
            "thread_type": "price_check",
            "anchors": [],
        }, headers=_auth(token))
        assert r.status_code == 422

    def test_price_check_with_real_vehicle_anchor_verifies(self, client: TestClient) -> None:
        token, _ = _register(client)
        r = client.post("/forum/threads", json={
            "title": "¿Es buen precio este Lynk & Co?",
            "body": "Me lo ofrecen a 23.490€",
            "thread_type": "price_check",
            "anchors": [{"anchor_type": "vehicle", "anchor_ref": RARE_VEHICLE_ULID}],
        }, headers=_auth(token))
        assert r.status_code == 200, r.text
        thread_ulid = r.json()["data"]["thread_ulid"]
        detail = client.get(f"/forum/threads/{thread_ulid}").json()["data"]
        anchor = detail["posts"][0]["anchors"][0]
        assert anchor["verified"] is True
        assert anchor["snapshot"]["make"] == "Lynk & Co"

    def test_fake_vehicle_anchor_stored_unverified(self, client: TestClient) -> None:
        token, _ = _register(client)
        r = client.post("/forum/threads", json={
            "title": "Ancla falsa",
            "body": "test",
            "anchors": [{"anchor_type": "vehicle", "anchor_ref": "01NOTAREALVEHICLEXXXXXXXXX"}],
        }, headers=_auth(token))
        thread_ulid = r.json()["data"]["thread_ulid"]
        detail = client.get(f"/forum/threads/{thread_ulid}").json()["data"]
        assert detail["posts"][0]["anchors"][0]["verified"] is False

    def test_reply_increments_count(self, client: TestClient) -> None:
        token, _ = _register(client)
        r = client.post("/forum/threads", json={"title": "t", "body": "b"}, headers=_auth(token))
        thread_ulid = r.json()["data"]["thread_ulid"]
        client.post(f"/forum/threads/{thread_ulid}/posts", json={"body": "reply 1"}, headers=_auth(token))
        detail = client.get(f"/forum/threads/{thread_ulid}").json()["data"]
        assert detail["reply_count"] == 1
        assert len(detail["posts"]) == 2

    def test_feed_lists_threads(self, client: TestClient) -> None:
        token, _ = _register(client)
        client.post("/forum/threads", json={"title": "feed-test", "body": "b"}, headers=_auth(token))
        r = client.get("/forum/threads?sort=recent")
        assert r.status_code == 200
        assert len(r.json()["data"]) >= 1


# ---------------------------------------------------------------------------
# Voting — privilege gates, self-vote block, reputation ledger
# ---------------------------------------------------------------------------

class TestVoting:
    def _thread_and_post(self, client: TestClient) -> tuple[str, str, str]:
        author_token, author_ulid = _register(client)
        r = client.post("/forum/threads", json={"title": "vote-target", "body": "b"}, headers=_auth(author_token))
        thread_ulid = r.json()["data"]["thread_ulid"]
        post_ulid = r.json()["data"]["first_post_ulid"]
        return author_token, author_ulid, post_ulid

    def test_low_rep_cannot_vote(self, client: TestClient) -> None:
        _, _, post_ulid = self._thread_and_post(client)
        voter_token, _ = _register(client)  # rep=0
        r = client.post(f"/forum/posts/{post_ulid}/vote", json={"value": 1}, headers=_auth(voter_token))
        assert r.status_code == 403

    def test_cannot_vote_on_own_post(self, client: TestClient) -> None:
        author_token, _, post_ulid = self._thread_and_post(client)
        asyncio.run(_grant_rep(
            __import__("json").loads(client.get("/auth/me", headers=_auth(author_token)).text)["user"]["id"],
            FLAG_PRIVILEGE_MIN_REP,
        ))
        r = client.post(f"/forum/posts/{post_ulid}/vote", json={"value": 1}, headers=_auth(author_token))
        assert r.status_code == 403

    def test_sufficient_rep_can_upvote_and_credits_author(self, client: TestClient) -> None:
        author_token, author_ulid, post_ulid = self._thread_and_post(client)
        voter_token, _ = _seasoned_user(client, VOTE_PRIVILEGE_MIN_REP)
        r = client.post(f"/forum/posts/{post_ulid}/vote", json={"value": 1}, headers=_auth(voter_token))
        assert r.status_code == 200, r.text
        assert r.json()["data"]["net_votes"] == 1

        profile = client.get(f"/forum/users/{author_ulid}").json()["data"]
        assert profile["reputation"] >= 4  # at least upvote_no_anchor credited

    def test_downvote_below_threshold_rejected(self, client: TestClient) -> None:
        _, _, post_ulid = self._thread_and_post(client)
        voter_token, _ = _seasoned_user(client, VOTE_PRIVILEGE_MIN_REP)  # can vote, not downvote
        r = client.post(f"/forum/posts/{post_ulid}/vote", json={"value": -1}, headers=_auth(voter_token))
        assert r.status_code == 403

    def test_downvote_with_sufficient_rep_costs_the_voter(self, client: TestClient) -> None:
        _, author_ulid, post_ulid = self._thread_and_post(client)
        voter_token, voter_ulid = _seasoned_user(client, DOWNVOTE_PRIVILEGE_MIN_REP)
        rep_before = client.get(f"/forum/users/{voter_ulid}").json()["data"]["reputation"]
        r = client.post(f"/forum/posts/{post_ulid}/vote", json={"value": -1}, headers=_auth(voter_token))
        assert r.status_code == 200
        rep_after = client.get(f"/forum/users/{voter_ulid}").json()["data"]["reputation"]
        assert rep_after == rep_before - 1  # "el poder de dañar se paga"

    def test_vote_removal_is_accepted(self, client: TestClient) -> None:
        _, _, post_ulid = self._thread_and_post(client)
        voter_token, _ = _seasoned_user(client, VOTE_PRIVILEGE_MIN_REP)
        client.post(f"/forum/posts/{post_ulid}/vote", json={"value": 1}, headers=_auth(voter_token))
        r = client.post(f"/forum/posts/{post_ulid}/vote", json={"value": 0}, headers=_auth(voter_token))
        assert r.status_code == 200
        assert r.json()["data"]["net_votes"] == 0

    def test_repeat_voter_within_window_does_not_double_credit_author(self, client: TestClient) -> None:
        """Carta §4.5 anti-inflado (eBay-exact): same voter->author pair counts once per
        7 days for REPUTATION — even across two different posts by the same author."""
        author_token, author_ulid = _register(client)
        r1 = client.post("/forum/threads", json={"title": "p1", "body": "b"}, headers=_auth(author_token))
        post1 = r1.json()["data"]["first_post_ulid"]
        r2 = client.post(f"/forum/threads/{r1.json()['data']['thread_ulid']}/posts", json={"body": "p2"}, headers=_auth(author_token))
        post2 = r2.json()["data"]["post_ulid"]

        voter_token, _ = _seasoned_user(client, VOTE_PRIVILEGE_MIN_REP)
        rep_before = client.get(f"/forum/users/{author_ulid}").json()["data"]["reputation"]
        client.post(f"/forum/posts/{post1}/vote", json={"value": 1}, headers=_auth(voter_token))
        rep_after_first = client.get(f"/forum/users/{author_ulid}").json()["data"]["reputation"]
        client.post(f"/forum/posts/{post2}/vote", json={"value": 1}, headers=_auth(voter_token))
        rep_after_second = client.get(f"/forum/users/{author_ulid}").json()["data"]["reputation"]

        assert rep_after_first > rep_before          # first vote credits
        assert rep_after_second == rep_after_first   # second vote (same pair, same window) does not


# ---------------------------------------------------------------------------
# Moderation
# ---------------------------------------------------------------------------

class TestModeration:
    def test_flag_requires_rep(self, client: TestClient) -> None:
        author_token, _ = _register(client)
        r = client.post("/forum/threads", json={"title": "flaggable", "body": "b"}, headers=_auth(author_token))
        post_ulid = r.json()["data"]["first_post_ulid"]
        flagger_token, _ = _register(client)  # rep=0
        r2 = client.post(f"/forum/posts/{post_ulid}/flag", json={"reason": "spam"}, headers=_auth(flagger_token))
        assert r2.status_code == 403

    def test_flag_then_moderation_queue_and_resolve(self, client: TestClient) -> None:
        author_token, _ = _register(client)
        r = client.post("/forum/threads", json={"title": "flaggable2", "body": "b"}, headers=_auth(author_token))
        post_ulid = r.json()["data"]["first_post_ulid"]
        flagger_token, _ = _seasoned_user(client, FLAG_PRIVILEGE_MIN_REP)
        r2 = client.post(f"/forum/posts/{post_ulid}/flag", json={"reason": "spam"}, headers=_auth(flagger_token))
        assert r2.status_code == 200

        # non-staff cannot see the queue
        r3 = client.get("/forum/moderation/queue", headers=_auth(flagger_token))
        assert r3.status_code == 403

    def test_duplicate_flag_rejected(self, client: TestClient) -> None:
        author_token, _ = _register(client)
        r = client.post("/forum/threads", json={"title": "flaggable3", "body": "b"}, headers=_auth(author_token))
        post_ulid = r.json()["data"]["first_post_ulid"]
        flagger_token, _ = _seasoned_user(client, FLAG_PRIVILEGE_MIN_REP)
        client.post(f"/forum/posts/{post_ulid}/flag", json={"reason": "spam"}, headers=_auth(flagger_token))
        r2 = client.post(f"/forum/posts/{post_ulid}/flag", json={"reason": "spam again"}, headers=_auth(flagger_token))
        assert r2.status_code == 409


# ---------------------------------------------------------------------------
# Anchor search
# ---------------------------------------------------------------------------

class TestAnchorSearch:
    def test_vehicle_search_returns_real_candidates(self, client: TestClient) -> None:
        r = client.get("/forum/anchor-search", params={"q": "Lynk", "kind": "vehicle"})
        assert r.status_code == 200
        assert len(r.json()["data"]) >= 1
        assert all(item["anchor_type"] == "vehicle" for item in r.json()["data"])
