"""Integration tests for pipeline/terminal/compute_buckets.py (09-trading-terminal F1).

SAFETY CONTRACT (mirrors tests/test_market_compute_stats.py): every DB-touching test runs
inside a transaction that is ALWAYS rolled back (never committed). Synthetic makes are
distinctively prefixed (``__CARDEEP_TERM_TEST_...__``) so they cannot collide with real
inventory even if a rollback were somehow skipped. This job reads directly from
vehicle/vehicle_event/entity (no v_canonical_vehicle dependency, unlike 01's compute_stats.py
— 09's symbol is make+model+province, no dedup-cluster join needed for its own aggregation),
so tests use market_test_helpers.seed_vehicle/seed_event directly.
"""
from __future__ import annotations

import asyncio
import os
from datetime import date, datetime, timedelta, timezone

import asyncpg
import pytest
import pytest_asyncio

from pipeline.terminal.compute_buckets import (
    MIN_ACTIVE_C2,
    MIN_EVENTS_C2,
    OUTLIER_SIGMA_C4,
    compute_bucket_for_date,
    run_for_date,
    symbol_key_for,
)
from tests.market_test_helpers import entity_ulid_of, seed_event, seed_vehicle, vam_verified_run_id

_DSN = os.environ.get(
    "CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
)

_MAKE_C2_OK = "__CARDEEP_TERM_TEST_C2_OK__"
_MAKE_C2_LOW_ACTIVE = "__CARDEEP_TERM_TEST_C2_LOWACTIVE__"
_MAKE_C2_LOW_EVENTS = "__CARDEEP_TERM_TEST_C2_LOWEVENTS__"
_MAKE_OUTLIER = "__CARDEEP_TERM_TEST_OUTLIER__"
_MAKE_ASOF = "__CARDEEP_TERM_TEST_ASOF__"
_MAKE_GONE = "__CARDEEP_TERM_TEST_GONE__"

D0 = date(2099, 1, 10)  # far-future synthetic date — cannot collide with real bucket dates
D1 = date(2099, 1, 11)


class _TestRollback(Exception):
    pass


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_conn():
    conn = await asyncpg.connect(_DSN)
    yield conn
    await conn.close()


def _dt(d: date, hour: int = 12) -> datetime:
    return datetime(d.year, d.month, d.day, hour, tzinfo=timezone.utc)


async def _seed_active_cohort(
    conn: asyncpg.Connection, run_id: str, *, make: str, model: str, n: int,
    province_code: str = "28", price: float = 20000.0, km: int = 80000,
    first_seen: datetime, new_event_day: date | None,
) -> list[str]:
    """Seed n vehicles, each with a NEW event. If new_event_day is given, the NEW event
    lands on that day (counts toward that day's n_events); otherwise the NEW event is
    backdated silently before D0 (vehicle exists but contributes zero events on D0/D1)."""
    ulids = []
    for i in range(n):
        vulid = await seed_vehicle(
            conn, run_id, make=make, model=model, fuel="gasolina", year=2020,
            province_code=province_code, price=price, status="available", first_seen=first_seen,
        )
        # market_test_helpers.seed_vehicle has no km parameter (01-market-intelligence's M1
        # never needed it) — set it directly here rather than extending the shared helper for
        # a single 09-specific need. Without this, vehicle.km stays NULL for every synthetic
        # row, which silently defeats the C4 outlier test's km-deviation leg (a real bug this
        # session's own test run caught: sd_km computed over all-NULL values can never exceed
        # the sigma threshold, so no row is ever excluded via km regardless of the value passed
        # here — see the AND-logic test class below for the fix this produced).
        await conn.execute("UPDATE vehicle SET km = $1 WHERE vehicle_ulid = $2", km, vulid)
        eulid = await entity_ulid_of(conn, vulid)
        event_dt = _dt(new_event_day) if new_event_day else first_seen
        await seed_event(
            conn, vehicle_ulid=vulid, entity_ulid=eulid, event_type="NEW",
            old_value=None, new_value={"price": price, "title": None, "source": "test"},
            observed_at=event_dt,
        )
        ulids.append(vulid)
    return ulids


@pytest.mark.integration
class TestC2Gate:
    @pytest.mark.asyncio
    async def test_below_min_active_yields_no_row(self, db_conn: asyncpg.Connection) -> None:
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                n_below = MIN_ACTIVE_C2 - 1
                await _seed_active_cohort(
                    db_conn, run_id, make=_MAKE_C2_LOW_ACTIVE, model="M", n=n_below,
                    first_seen=_dt(D0), new_event_day=D0,
                )
                rows, _events = await compute_bucket_for_date(db_conn, D0)
                own = [r for r in rows if r.make == _MAKE_C2_LOW_ACTIVE]
                assert own == [], f"n={n_below} < MIN_ACTIVE_C2={MIN_ACTIVE_C2} must yield ZERO rows, got {own}"
                raise _TestRollback()
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_at_min_active_with_enough_events_yields_row(self, db_conn: asyncpg.Connection) -> None:
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                await _seed_active_cohort(
                    db_conn, run_id, make=_MAKE_C2_OK, model="M", n=MIN_ACTIVE_C2,
                    first_seen=_dt(D0), new_event_day=D0,
                )
                rows, events = await compute_bucket_for_date(db_conn, D0)
                own = [r for r in rows if r.make == _MAKE_C2_OK]
                assert len(own) == 2, f"expected prov+nat rows, got {own}"  # prov + nat
                prov = [r for r in own if r.province_code == "28"][0]
                assert prov.active_count == MIN_ACTIVE_C2
                ev = events[(_MAKE_C2_OK, "M", "28")]
                assert ev["new_count"] == MIN_ACTIVE_C2
                raise _TestRollback()
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_below_min_events_yields_no_row_despite_enough_active(
        self, db_conn: asyncpg.Connection
    ) -> None:
        """MIN_ACTIVE_C2 vehicles pre-existing (first_seen well before D1, zero events ON
        D1) plus a couple of PRICE_CHANGE events on D1 (< MIN_EVENTS_C2 total) — active
        count clears C2 gate #1 but events fails gate #2, so the bucket must not fire."""
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                vulids = await _seed_active_cohort(
                    db_conn, run_id, make=_MAKE_C2_LOW_EVENTS, model="M", n=MIN_ACTIVE_C2,
                    first_seen=_dt(D0), new_event_day=D0,  # events land on D0, not D1
                )
                # exactly MIN_EVENTS_C2 - 1 price-change events land ON D1
                n_events_d1 = MIN_EVENTS_C2 - 1
                for vulid in vulids[:n_events_d1]:
                    eulid = await entity_ulid_of(db_conn, vulid)
                    await seed_event(
                        db_conn, vehicle_ulid=vulid, entity_ulid=eulid, event_type="PRICE_CHANGE",
                        old_value={"price": 20000.0}, new_value={"price": 19500.0}, observed_at=_dt(D1),
                    )
                rows, events = await compute_bucket_for_date(db_conn, D1)
                own = [r for r in rows if r.make == _MAKE_C2_LOW_EVENTS]
                assert own == [], (
                    f"active_count clears C2 but n_events={n_events_d1} < MIN_EVENTS_C2="
                    f"{MIN_EVENTS_C2} must still suppress the row, got {own}"
                )
                raise _TestRollback()
        except _TestRollback:
            pass


@pytest.mark.integration
class TestAsOfPriceReconstruction:
    @pytest.mark.asyncio
    async def test_bucket_uses_price_as_of_day_not_current_price(
        self, db_conn: asyncpg.Connection
    ) -> None:
        """A PRICE_CHANGE landing AFTER the bucket day must NOT leak into that day's
        median — the whole point of AS-OF reconstruction (C3 honesty)."""
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                # MIN_ACTIVE_C2 vehicles at a stable baseline price, all NEW on D0.
                vulids = await _seed_active_cohort(
                    db_conn, run_id, make=_MAKE_ASOF, model="M", n=MIN_ACTIVE_C2,
                    price=20000.0, first_seen=_dt(D0), new_event_day=D0,
                )
                # ONE of them gets a price change to 999999 on D1 (the day AFTER).
                target = vulids[0]
                eulid = await entity_ulid_of(db_conn, target)
                await seed_event(
                    db_conn, vehicle_ulid=target, entity_ulid=eulid, event_type="PRICE_CHANGE",
                    old_value={"price": 20000.0}, new_value={"price": 999999.0}, observed_at=_dt(D1),
                )
                await db_conn.execute("UPDATE vehicle SET price = 999999.0 WHERE vehicle_ulid = $1", target)

                rows, _events = await compute_bucket_for_date(db_conn, D0)
                prov = [r for r in rows if r.make == _MAKE_ASOF and r.province_code == "28"][0]
                assert prov.median_price == pytest.approx(20000.0), (
                    f"D0's median must be unaffected by a D1 price change, got {prov.median_price}"
                )
                raise _TestRollback()
        except _TestRollback:
            pass


@pytest.mark.integration
class TestGoneHandling:
    @pytest.mark.asyncio
    async def test_gone_before_bucket_day_excluded_from_active(
        self, db_conn: asyncpg.Connection
    ) -> None:
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                vulids = await _seed_active_cohort(
                    db_conn, run_id, make=_MAKE_GONE, model="M", n=MIN_ACTIVE_C2 + 1,
                    first_seen=_dt(D0), new_event_day=D0,
                )
                gone_one = vulids[0]
                eulid = await entity_ulid_of(db_conn, gone_one)
                await seed_event(
                    db_conn, vehicle_ulid=gone_one, entity_ulid=eulid, event_type="GONE",
                    old_value=None, new_value=None, observed_at=_dt(D0, hour=23),
                )
                await db_conn.execute("UPDATE vehicle SET status='gone' WHERE vehicle_ulid=$1", gone_one)

                rows, _events = await compute_bucket_for_date(db_conn, D0)
                prov = [r for r in rows if r.make == _MAKE_GONE and r.province_code == "28"][0]
                assert prov.active_count == MIN_ACTIVE_C2, (
                    f"1 of {MIN_ACTIVE_C2 + 1} went GONE same-day -> active_count must be "
                    f"{MIN_ACTIVE_C2}, got {prov.active_count}"
                )
                raise _TestRollback()
        except _TestRollback:
            pass


@pytest.mark.integration
class TestOutlierExclusionAndLogic:
    @pytest.mark.asyncio
    async def test_price_only_deviation_is_not_excluded(self, db_conn: asyncpg.Connection) -> None:
        """Manheim's primary methodology (verified live against site.manheim.com's PDF this
        session): an outlier requires BOTH price AND mileage to exceed 2.6 sigma. A vehicle
        with an extreme price but NORMAL mileage must stay in the active/percentile set."""
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                n_base = MIN_ACTIVE_C2 - 1
                for _ in range(n_base):
                    await _seed_active_cohort(
                        db_conn, run_id, make=_MAKE_OUTLIER, model="M", n=1,
                        price=20000.0, km=80000, first_seen=_dt(D0), new_event_day=D0,
                    )
                # One vehicle: price WAY off (100k), km identical to the pack (80000, sd_km≈0).
                await _seed_active_cohort(
                    db_conn, run_id, make=_MAKE_OUTLIER, model="M", n=1,
                    price=100000.0, km=80000, first_seen=_dt(D0), new_event_day=D0,
                )
                rows, _events = await compute_bucket_for_date(db_conn, D0)
                prov = [r for r in rows if r.make == _MAKE_OUTLIER and r.province_code == "28"][0]
                assert prov.active_count == MIN_ACTIVE_C2, (
                    "sd_km==0 across the cohort means the AND-gate can never fire (km deviation "
                    "is undefined/zero) — the price-only extreme must NOT be excluded"
                )
                assert prov.outliers_excluded == 0
                raise _TestRollback()
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_both_price_and_km_deviation_is_excluded(self, db_conn: asyncpg.Connection) -> None:
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                n_base = MIN_ACTIVE_C2
                # Base cohort with SOME natural spread in both price and km so sd>0.
                for i in range(n_base):
                    await _seed_active_cohort(
                        db_conn, run_id, make=_MAKE_OUTLIER + "2", model="M", n=1,
                        price=20000.0 + i * 50, km=80000 + i * 100, first_seen=_dt(D0), new_event_day=D0,
                    )
                # One vehicle: BOTH price and km wildly off the pack.
                await _seed_active_cohort(
                    db_conn, run_id, make=_MAKE_OUTLIER + "2", model="M", n=1,
                    price=500000.0, km=900000, first_seen=_dt(D0), new_event_day=D0,
                )
                rows, _events = await compute_bucket_for_date(db_conn, D0)
                prov = [r for r in rows if r.make == _MAKE_OUTLIER + "2" and r.province_code == "28"][0]
                assert prov.outliers_excluded == 1, f"expected exactly 1 excluded outlier, got {prov.outliers_excluded}"
                assert prov.active_count == n_base
                raise _TestRollback()
        except _TestRollback:
            pass


@pytest.mark.integration
class TestIdempotentUpsert:
    @pytest.mark.asyncio
    async def test_rerun_same_day_does_not_duplicate_or_diverge(
        self, db_conn: asyncpg.Connection
    ) -> None:
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                await _seed_active_cohort(
                    db_conn, run_id, make=_MAKE_C2_OK + "_IDEMP", model="M", n=MIN_ACTIVE_C2,
                    first_seen=_dt(D0), new_event_day=D0,
                )
                n1, _ = await run_for_date(db_conn, D0)
                n2, _ = await run_for_date(db_conn, D0)
                assert n1 == n2
                count = await db_conn.fetchval(
                    "SELECT count(*) FROM market_bucket_daily WHERE symbol_key = $1",
                    symbol_key_for(_MAKE_C2_OK + "_IDEMP", "M", "28"),
                )
                assert count == 1, f"expected exactly 1 row after two runs (upsert), got {count}"
                raise _TestRollback()
        except _TestRollback:
            pass
