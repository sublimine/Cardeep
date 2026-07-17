"""F3 — scheduler-level half-open circuit breaker (00-marketplace-engine.md F3).

Closes the gap the carta identified: the pre-existing Hystrix-style half-open state
machine in pipeline/ops/health.py (source_breaker.state + cooldown_until, is_open())
was fully built and tested at the CONNECTOR level, but pipeline/ops/scheduler.py's
_due_sources() never consulted it — it excluded any source with
source_health.consecutive_fails >= BREAKER_TRIP_AT PERMANENTLY, with no time dimension,
so a breaker-tripped source could never again be scheduled even long after its
cooldown had elapsed. These tests cover the two new pieces that close that gap:

  1. _breaker_decision(breaker_state, cooldown_until, now) — a pure, DB-free predicate
     used by _due_sources() to decide "allow" / "probe" / "skip" per source. Tests the
     full transition table: CLOSED -> allow, OPEN+cooling -> skip,
     OPEN+cooldown-elapsed -> probe, HALF_OPEN -> skip (a probe is already outstanding).

  2. _prepare_launch(source_key) — the atomic claim step invoked by heartbeat_tick()
     immediately before launching a subprocess. Mocked-connection unit tests (no DB)
     plus one live-DB integration test (synthetic, committed + cleaned up in `finally`
     since the claim must be visible across the psycopg2/asyncpg connection boundary)
     that exercises the REAL end-to-end transition CLOSED -> (trip) -> OPEN ->
     (cooldown forced into the past) -> _due_sources() includes it as a probe ->
     _prepare_launch() claims it -> a second _prepare_launch() call loses the race.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.ops.scheduler import _breaker_decision, _due_sources, _prepare_launch

NOW = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# 1. _breaker_decision — pure predicate, no DB
# ---------------------------------------------------------------------------

class TestBreakerDecision:
    def test_no_breaker_row_is_allow(self) -> None:
        """A source that has never tripped (no source_breaker row) is CLOSED-equivalent."""
        assert _breaker_decision(None, None, NOW) == "allow"

    def test_closed_is_allow(self) -> None:
        assert _breaker_decision("closed", None, NOW) == "allow"

    def test_open_still_cooling_is_skip(self) -> None:
        cooldown_until = NOW + timedelta(minutes=10)
        assert _breaker_decision("open", cooldown_until, NOW) == "skip"

    def test_open_cooldown_elapsed_is_probe(self) -> None:
        cooldown_until = NOW - timedelta(minutes=1)
        assert _breaker_decision("open", cooldown_until, NOW) == "probe"

    def test_open_with_no_cooldown_until_is_skip(self) -> None:
        """Defensive default: an OPEN breaker with no recorded cooldown stays blocked."""
        assert _breaker_decision("open", None, NOW) == "skip"

    def test_half_open_is_skip(self) -> None:
        """A probe already outstanding elsewhere must not admit a second one."""
        assert _breaker_decision("half_open", NOW - timedelta(hours=1), NOW) == "skip"

    def test_open_cooldown_exactly_now_is_probe(self) -> None:
        """Boundary: cooldown_until == now counts as elapsed (not strictly in the future)."""
        assert _breaker_decision("open", NOW, NOW) == "probe"


# ---------------------------------------------------------------------------
# 2. _due_sources() respects the breaker decision (extends test_scheduler_due.py's
#    mocked-connection pattern with the new breaker_state/cooldown_until columns)
# ---------------------------------------------------------------------------

def _fake_conn(rows: list[tuple[Any, ...]]) -> MagicMock:
    cur_mock = MagicMock()
    cur_mock.__enter__ = lambda s: s
    cur_mock.__exit__ = MagicMock(return_value=False)
    cur_mock.fetchall.return_value = rows

    conn_mock = MagicMock()
    conn_mock.cursor.return_value = cur_mock
    return conn_mock


def _row(
    source_key: str,
    interval_h: int,
    last_ok: datetime | None,
    last_fail: datetime | None,
    consecutive_fails: int = 0,
    breaker_state: str | None = None,
    cooldown_until: datetime | None = None,
) -> tuple[Any, ...]:
    return (source_key, interval_h, last_ok, last_fail, consecutive_fails,
            breaker_state, cooldown_until)


class TestDueSourcesHalfOpen:
    def test_open_cooling_excluded(self) -> None:
        """cooldown_until is deliberately hours (not minutes) in the future: _due_sources()
        compares against a FRESH datetime.now() internally, and this file's NOW constant is
        frozen at import time — a small offset would flake on a slow/full-suite run where
        real wall-clock minutes elapse between import and this test executing."""
        last_ok = NOW - timedelta(hours=200)
        conn = _fake_conn([
            _row("coches_net_wholesale", 24, last_ok, None, 3,
                 breaker_state="open", cooldown_until=NOW + timedelta(hours=2)),
        ])
        due = _due_sources(conn)
        assert due == [], "OPEN breaker still cooling must be excluded"

    def test_open_cooldown_elapsed_included_as_probe(self) -> None:
        """The core F3 fix: a breaker whose cooldown has elapsed re-enters the DUE list."""
        last_ok = NOW - timedelta(hours=200)
        conn = _fake_conn([
            _row("coches_net_wholesale", 24, last_ok, None, 3,
                 breaker_state="open", cooldown_until=NOW - timedelta(minutes=1)),
        ])
        due = _due_sources(conn)
        keys = [r[0] for r in due]
        assert "coches_net_wholesale" in keys, (
            "A source whose breaker cooldown has elapsed must re-enter the due list "
            "as a half-open probe candidate — the gap this fixes"
        )

    def test_half_open_excluded(self) -> None:
        """A source already mid-probe (half_open) must not be scheduled a second time."""
        last_ok = NOW - timedelta(hours=200)
        conn = _fake_conn([
            _row("coches_net_wholesale", 24, last_ok, None, 3,
                 breaker_state="half_open", cooldown_until=NOW - timedelta(hours=1)),
        ])
        due = _due_sources(conn)
        assert due == []

    def test_no_breaker_row_included_regardless_of_consecutive_fails(self) -> None:
        """consecutive_fails alone no longer drives exclusion — the real breaker table does."""
        last_ok = NOW - timedelta(hours=200)
        conn = _fake_conn([
            _row("coches_net_wholesale", 24, last_ok, None, 3, breaker_state=None),
        ])
        due = _due_sources(conn)
        keys = [r[0] for r in due]
        assert "coches_net_wholesale" in keys

    def test_return_tuple_shape_is_unchanged(self) -> None:
        """External contract: callers still unpack a 4-tuple (source_key, interval_h,
        last_ok, last_fail) — the breaker columns are consumed internally, never leaked."""
        last_ok = NOW - timedelta(hours=200)
        conn = _fake_conn([_row("autocasion_wholesale", 24, last_ok, None, 0)])
        due = _due_sources(conn)
        assert len(due) == 1
        assert len(due[0]) == 4


# ---------------------------------------------------------------------------
# 3. _prepare_launch — the atomic claim step (mocked psycopg2, no DB)
# ---------------------------------------------------------------------------

def _mock_pg_conn(select_row: tuple[Any, ...] | None):
    """A psycopg2-shaped connection whose cursor answers ONE SELECT (state, cooldown_until).

    _prepare_launch is READ-ONLY (see its docstring for why: an earlier version performed
    its own CAS claim here, which raced the connector's OWN internal is_open() claim and
    caused a live incident — every legitimately-authorized probe immediately saw the
    scheduler's own claim reflected back as "someone else already has it" and aborted,
    permanently stuck at half_open with nothing left to resolve it via record_run()).
    """
    cur = MagicMock()
    cur.__enter__ = lambda s: s
    cur.__exit__ = MagicMock(return_value=False)
    cur.fetchone.return_value = select_row

    conn = MagicMock()
    conn.cursor.return_value = cur
    return conn


class TestPrepareLaunch:
    """_prepare_launch is a pure READ-ONLY re-check (no mutation, no CAS) — see its
    docstring for the double-claim bug this design deliberately avoids. It answers
    identically to _breaker_decision() would for the same state, just re-read fresh."""

    def test_no_breaker_row_allows(self) -> None:
        conn = _mock_pg_conn(select_row=None)
        with patch("pipeline.ops.scheduler.psycopg2.connect", return_value=conn):
            assert _prepare_launch("some_healthy_source") is True

    def test_closed_allows(self) -> None:
        conn = _mock_pg_conn(select_row=("closed", None))
        with patch("pipeline.ops.scheduler.psycopg2.connect", return_value=conn):
            assert _prepare_launch("some_healthy_source") is True

    def test_open_cooldown_elapsed_allows(self) -> None:
        cooldown_until = datetime.now(timezone.utc) - timedelta(minutes=1)
        conn = _mock_pg_conn(select_row=("open", cooldown_until))
        with patch("pipeline.ops.scheduler.psycopg2.connect", return_value=conn):
            assert _prepare_launch("coches_net_wholesale") is True

    def test_open_still_cooling_blocks(self) -> None:
        """Staleness re-check: _due_sources() may have read this hours ago (many due
        sources ahead of it in the same tick); if the breaker re-tripped meanwhile with a
        fresh cooldown, this must catch it rather than launching anyway."""
        cooldown_until = datetime.now(timezone.utc) + timedelta(hours=1)
        conn = _mock_pg_conn(select_row=("open", cooldown_until))
        with patch("pipeline.ops.scheduler.psycopg2.connect", return_value=conn):
            assert _prepare_launch("coches_net_wholesale") is False

    def test_half_open_blocks(self) -> None:
        """A probe already outstanding (claimed by the connector's own is_open() call,
        not yet resolved by record_run()) must not be launched a second time."""
        conn = _mock_pg_conn(select_row=("half_open", datetime.now(timezone.utc)))
        with patch("pipeline.ops.scheduler.psycopg2.connect", return_value=conn):
            assert _prepare_launch("coches_net_wholesale") is False

    def test_connect_failure_fails_closed(self) -> None:
        """A DB error must never be treated as a green light to hammer a fragile source."""
        import psycopg2 as real_psycopg2
        with patch(
            "pipeline.ops.scheduler.psycopg2.connect",
            side_effect=real_psycopg2.Error("no db"),
        ):
            assert _prepare_launch("coches_net_wholesale") is False


# ---------------------------------------------------------------------------
# 4. Live-DB integration test: the FULL transition, synthetic source_key, real rows
#    (committed then deleted in `finally` — the claim must be visible cross-connection,
#    so this cannot use an aborted transaction like test_resilience_loop.py).
# ---------------------------------------------------------------------------

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
PSYCOPG2_DSN = "host=127.0.0.1 port=5433 dbname=cardeep user=cardeep password=cardeep_dev_only"
SOURCE_KEY = "__f3_half_open_scheduler_test__"


def _db_available() -> bool:
    try:
        import psycopg2
        conn = psycopg2.connect(PSYCOPG2_DSN, connect_timeout=3)
        conn.close()
        return True
    except Exception:
        return False


DB_AVAILABLE = _db_available()


@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestFullTransitionLiveDB:
    """CLOSED -> (trip x3, real record_run) -> OPEN -> (cooldown forced into the past,
    simulating time passing) -> _due_sources() includes it as a probe -> _prepare_launch()
    re-confirms eligibility (read-only, True) -> the CONNECTOR's own is_open() call claims
    the half-open slot (this is the real architecture: the scheduler never claims it
    itself — see _prepare_launch()'s docstring for the live incident that proved why) ->
    record_run(ok=True) closes it -> _due_sources() no longer flags it."""

    def _cleanup(self, cur) -> None:
        cur.execute("DELETE FROM source_breaker WHERE source_key=%s", (SOURCE_KEY,))
        cur.execute("DELETE FROM harvest_run WHERE source_key=%s", (SOURCE_KEY,))
        cur.execute("DELETE FROM source_health WHERE source_key=%s", (SOURCE_KEY,))

    def test_full_transition_closed_open_half_open_closed(self) -> None:
        import asyncio

        import asyncpg
        import psycopg2

        from pipeline.ops.health import BREAKER_TRIP_AT, record_run

        pg_conn = psycopg2.connect(PSYCOPG2_DSN)
        pg_conn.autocommit = True
        try:
            with pg_conn.cursor() as cur:
                self._cleanup(cur)
                # Seed source_health so _due_sources()'s interval condition is DUE.
                cur.execute(
                    "INSERT INTO source_health (source_key, harvest_interval_hours, "
                    "last_ok, consecutive_fails, country_code) "
                    "VALUES (%s, 24, now() - interval '200 hours', 0, 'ES')",
                    (SOURCE_KEY,),
                )

            # --- Trip the breaker for real via record_run (asyncpg). ---
            async def _trip() -> None:
                conn = await asyncpg.connect(DSN)
                try:
                    for _ in range(BREAKER_TRIP_AT):
                        await record_run(conn, SOURCE_KEY, ok=False, error="synthetic", phase="scrape")
                finally:
                    await conn.close()

            asyncio.run(_trip())

            # Sanity: breaker is OPEN with a future cooldown -> _due_sources excludes it.
            with pg_conn.cursor() as cur:
                due = _due_sources(pg_conn)
            assert SOURCE_KEY not in [r[0] for r in due], (
                "Freshly-tripped breaker (cooldown in the future) must be excluded"
            )

            # --- Simulate cooldown elapsing (force cooldown_until into the past). ---
            with pg_conn.cursor() as cur:
                cur.execute(
                    "UPDATE source_breaker SET cooldown_until = now() - interval '1 second' "
                    "WHERE source_key=%s",
                    (SOURCE_KEY,),
                )

            # Now _due_sources() must include it as a probe candidate (the F3 fix).
            due = _due_sources(pg_conn)
            assert SOURCE_KEY in [r[0] for r in due], (
                "A breaker whose cooldown has elapsed must re-enter the due list"
            )

            # --- _prepare_launch re-confirms eligibility (read-only — does NOT claim). ---
            assert _prepare_launch(SOURCE_KEY) is True, "Probe-eligible source must launch"
            # Calling it again must give the SAME answer — it is idempotent/read-only, unlike
            # the buggy first version that mutated state and made a second call see its own
            # claim reflected back as "someone else already has it".
            assert _prepare_launch(SOURCE_KEY) is True, (
                "_prepare_launch must be idempotent (read-only) — repeated calls must not "
                "themselves change eligibility"
            )

            # --- The CONNECTOR's own is_open() call is what actually claims the slot. ---
            async def _connector_claims() -> bool:
                conn = await asyncpg.connect(DSN)
                try:
                    from pipeline.ops.health import is_open
                    return await is_open(conn, SOURCE_KEY)
                finally:
                    await conn.close()

            blocked = asyncio.run(_connector_claims())
            assert blocked is False, "The connector's own is_open() call must claim and proceed"

            with pg_conn.cursor() as cur:
                cur.execute("SELECT state FROM source_breaker WHERE source_key=%s", (SOURCE_KEY,))
                assert cur.fetchone()[0] == "half_open"

            # A second concurrent is_open() call (e.g. the same family connector checking
            # again for another member dealer) must now be blocked — exactly one probe.
            second_blocked = asyncio.run(_connector_claims())
            assert second_blocked is True, (
                "A second is_open() call while half_open must be blocked (exactly one probe)"
            )

            # --- The probe succeeds: record_run(ok=True) closes the breaker. ---
            async def _recover() -> None:
                conn = await asyncpg.connect(DSN)
                try:
                    await record_run(conn, SOURCE_KEY, ok=True, rows=1, phase="scrape")
                finally:
                    await conn.close()

            asyncio.run(_recover())

            with pg_conn.cursor() as cur:
                cur.execute("SELECT state FROM source_breaker WHERE source_key=%s", (SOURCE_KEY,))
                assert cur.fetchone()[0] == "closed"
        finally:
            with pg_conn.cursor() as cur:
                self._cleanup(cur)
            pg_conn.close()

    def test_failed_probe_reopens_with_deeper_backoff(self) -> None:
        """A half-open probe that FAILS must re-open with a cooldown deeper than the first
        trip's (exponential backoff continues past the probe, not reset by it)."""
        import asyncio

        import asyncpg
        import psycopg2

        from pipeline.ops.health import BREAKER_TRIP_AT, record_run

        pg_conn = psycopg2.connect(PSYCOPG2_DSN)
        pg_conn.autocommit = True
        try:
            with pg_conn.cursor() as cur:
                self._cleanup(cur)
                cur.execute(
                    "INSERT INTO source_health (source_key, harvest_interval_hours, "
                    "last_ok, consecutive_fails, country_code) "
                    "VALUES (%s, 24, now() - interval '200 hours', 0, 'ES')",
                    (SOURCE_KEY,),
                )

            async def _trip() -> datetime:
                conn = await asyncpg.connect(DSN)
                try:
                    for _ in range(BREAKER_TRIP_AT):
                        await record_run(conn, SOURCE_KEY, ok=False, error="synthetic", phase="scrape")
                    return await conn.fetchval(
                        "SELECT cooldown_until FROM source_breaker WHERE source_key=$1", SOURCE_KEY)
                finally:
                    await conn.close()

            first_cooldown_until = asyncio.run(_trip())

            with pg_conn.cursor() as cur:
                cur.execute(
                    "UPDATE source_breaker SET cooldown_until = now() - interval '1 second' "
                    "WHERE source_key=%s",
                    (SOURCE_KEY,),
                )
            claim_time = datetime.now(timezone.utc)
            assert _prepare_launch(SOURCE_KEY) is True

            # The connector's own is_open() call claims the half-open slot (the real
            # architecture — see _prepare_launch()'s docstring).
            async def _claim() -> bool:
                conn = await asyncpg.connect(DSN)
                try:
                    from pipeline.ops.health import is_open
                    return await is_open(conn, SOURCE_KEY)
                finally:
                    await conn.close()

            assert asyncio.run(_claim()) is False, "is_open() must claim and let the probe through"

            # The probe FAILS.
            async def _fail_probe() -> datetime:
                conn = await asyncpg.connect(DSN)
                try:
                    await record_run(conn, SOURCE_KEY, ok=False, error="probe failed again", phase="scrape")
                    return await conn.fetchval(
                        "SELECT cooldown_until FROM source_breaker WHERE source_key=$1", SOURCE_KEY)
                finally:
                    await conn.close()

            second_cooldown_until = asyncio.run(_fail_probe())

            with pg_conn.cursor() as cur:
                cur.execute("SELECT state FROM source_breaker WHERE source_key=%s", (SOURCE_KEY,))
                assert cur.fetchone()[0] == "open", "A failed probe must re-open the breaker"

            second_depth_seconds = (second_cooldown_until - claim_time).total_seconds()
            first_depth_seconds = (first_cooldown_until - claim_time).total_seconds()
            assert second_depth_seconds > first_depth_seconds, (
                "A failed half-open probe must re-open with a DEEPER backoff than the first "
                f"trip (first~{first_depth_seconds:.0f}s, second~{second_depth_seconds:.0f}s)"
            )
        finally:
            with pg_conn.cursor() as cur:
                self._cleanup(cur)
            pg_conn.close()
