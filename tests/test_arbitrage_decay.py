"""Tests for pipeline/arbitrage/decay.py (04-arbitrage.md F4 — time-arbitrage).

SAFETY CONTRACT (same as tests/test_arbitrage_score.py): every DB-touching test runs
inside a ROLLED-BACK transaction, using distinctive ``__CARDEEP_TEST_...__`` makes.
"""
from __future__ import annotations

import asyncio
import json
import os
import statistics
from datetime import datetime, timedelta, timezone

import asyncpg
import pytest
import pytest_asyncio

from pipeline.arbitrage.decay import (
    MIN_CYCLES_PER_COHORT,
    MIN_OBS_PER_BUCKET,
    _bucket_day_range,
    fetch_cycle_stats,
    fetch_decay_buckets,
    run_decay,
)
from pipeline.ids import ulid

_DSN = os.environ.get(
    "CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
)

_MAKE_CYCLE = "__CARDEEP_TEST_DECAY_CYCLE__"
_MAKE_BUCKET = "__CARDEEP_TEST_DECAY_BUCKET__"
_MAKE_LOWN = "__CARDEEP_TEST_DECAY_LOWN__"


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


async def _seed_entity_vehicle(conn: asyncpg.Connection, *, make: str, model: str, year: int) -> tuple[str, str]:
    entity_ulid = ulid()
    vehicle_ulid = ulid()
    cdp_code = f"CDP-ES-28-TST{vehicle_ulid[-8:]}"
    await conn.execute(
        "INSERT INTO entity (entity_ulid, cdp_code, kind, province_code, status) "
        "VALUES ($1, $2, 'compraventa', '28', 'unverified')",
        entity_ulid, cdp_code,
    )
    await conn.execute(
        "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, make, model, year, status) "
        "VALUES ($1,$2,$3,$4,$5,$6,'available')",
        vehicle_ulid, entity_ulid, f"https://example.test/{vehicle_ulid}", make, model, year,
    )
    return entity_ulid, vehicle_ulid


async def _seed_event(
    conn: asyncpg.Connection, *, vehicle_ulid: str, entity_ulid: str, event_type: str,
    old_value: dict | None, new_value: dict | None, observed_at: datetime,
) -> None:
    await conn.execute(
        "INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type, "
        "old_value, new_value, observed_at) VALUES ($1,$2,$3,$4,$5::jsonb,$6::jsonb,$7)",
        ulid(), vehicle_ulid, entity_ulid, event_type,
        json.dumps(old_value) if old_value is not None else None,
        json.dumps(new_value) if new_value is not None else None,
        observed_at,
    )


class TestBucketDayRange:
    def test_all_six_buckets_are_contiguous_and_cover_zero_to_infinity(self):
        ranges = {label: _bucket_day_range(label) for label in
                  ("0-7", "8-15", "16-30", "31-60", "61-90", "90+")}
        assert ranges["0-7"] == (0.0, 7.0)
        assert ranges["90+"][1] > 1e6


@pytest.mark.integration
class TestFetchCycleStats:
    @pytest.mark.asyncio
    async def test_cohort_clears_min_and_matches_hand_computed_median_and_drop_rate(
        self, db_conn: asyncpg.Connection
    ) -> None:
        """50 vehicles (== MIN_CYCLES_PER_COHORT), days_to_gone = 1..50 (median=25.5).
        20 of them (the ones with days_to_gone <= 20) get one PRICE_CHANGE price DROP
        before GONE -> pct_price_drop_before_gone = 20/50 = 0.4 (hand-verified)."""
        assert MIN_CYCLES_PER_COHORT == 50
        try:
            async with db_conn.transaction():
                base = datetime.now(timezone.utc) - timedelta(days=200)
                for k in range(1, 51):
                    eid, vid = await _seed_entity_vehicle(db_conn, make=_MAKE_CYCLE, model="TestModel", year=2022)
                    new_at = base
                    gone_at = base + timedelta(days=k)
                    await _seed_event(
                        db_conn, vehicle_ulid=vid, entity_ulid=eid, event_type="NEW",
                        old_value=None, new_value={"price": 10000.0}, observed_at=new_at,
                    )
                    if k <= 20:
                        await _seed_event(
                            db_conn, vehicle_ulid=vid, entity_ulid=eid, event_type="PRICE_CHANGE",
                            old_value={"price": 10000.0}, new_value={"price": 9000.0},
                            observed_at=new_at + timedelta(hours=1),
                        )
                    await _seed_event(
                        db_conn, vehicle_ulid=vid, entity_ulid=eid, event_type="GONE",
                        old_value={"price": 9000.0 if k <= 20 else 10000.0}, new_value=None,
                        observed_at=gone_at,
                    )

                rows = await fetch_cycle_stats(db_conn, make_filter=[_MAKE_CYCLE])
                assert len(rows) == 1
                row = rows[0]
                assert row["n"] == 50
                assert row["median_days"] == pytest.approx(statistics.median(range(1, 51)), abs=0.01)
                assert row["pct_price_drop"] == pytest.approx(0.4, abs=1e-9)

                raise _TestRollback()
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_below_min_cycles_is_suppressed(self, db_conn: asyncpg.Connection) -> None:
        try:
            async with db_conn.transaction():
                base = datetime.now(timezone.utc) - timedelta(days=200)
                for k in range(1, 21):  # 20 < MIN_CYCLES_PER_COHORT(50)
                    eid, vid = await _seed_entity_vehicle(db_conn, make=_MAKE_LOWN, model="TestModel", year=2022)
                    await _seed_event(
                        db_conn, vehicle_ulid=vid, entity_ulid=eid, event_type="NEW",
                        old_value=None, new_value={"price": 10000.0}, observed_at=base,
                    )
                    await _seed_event(
                        db_conn, vehicle_ulid=vid, entity_ulid=eid, event_type="GONE",
                        old_value={"price": 10000.0}, new_value=None,
                        observed_at=base + timedelta(days=k),
                    )
                rows = await fetch_cycle_stats(db_conn, make_filter=[_MAKE_LOWN])
                assert rows == [], "n=20<50 must be suppressed by the SQL HAVING"
                raise _TestRollback()
        except _TestRollback:
            pass


@pytest.mark.integration
class TestFetchDecayBuckets:
    @pytest.mark.asyncio
    async def test_bucket_clears_min_and_relative_price_is_one_at_age_zero(
        self, db_conn: asyncpg.Connection
    ) -> None:
        """30 vehicles (== MIN_OBS_PER_BUCKET) each with only a NEW event (age=0, bucket
        '0-7'). relative_price = price/initial_price = 1.0 for every sample by
        construction -> median_relative_price must be exactly 1.0."""
        assert MIN_OBS_PER_BUCKET == 30
        try:
            async with db_conn.transaction():
                base = datetime.now(timezone.utc) - timedelta(days=5)
                for _i in range(30):
                    entity_ulid, vid = await _seed_entity_vehicle(
                        db_conn, make=_MAKE_BUCKET, model="TestModel", year=2022
                    )
                    await db_conn.execute(
                        "UPDATE vehicle SET first_seen=$1 WHERE vehicle_ulid=$2", base, vid
                    )
                    await _seed_event(
                        db_conn, vehicle_ulid=vid, entity_ulid=entity_ulid, event_type="NEW",
                        old_value=None, new_value={"price": 15000.0}, observed_at=base,
                    )

                rows = await fetch_decay_buckets(db_conn, make_filter=[_MAKE_BUCKET])
                bucket_07 = [r for r in rows if r["bucket_label"] == "0-7"]
                assert len(bucket_07) == 1
                assert bucket_07[0]["n"] == 30
                assert bucket_07[0]["median_relative_price"] == pytest.approx(1.0, abs=1e-9)

                raise _TestRollback()
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_below_min_observations_bucket_is_suppressed(
        self, db_conn: asyncpg.Connection
    ) -> None:
        try:
            async with db_conn.transaction():
                base = datetime.now(timezone.utc) - timedelta(days=25)
                for _i in range(10):  # 10 < MIN_OBS_PER_BUCKET(30)
                    entity_ulid, vid = await _seed_entity_vehicle(
                        db_conn, make=_MAKE_LOWN, model="BucketModel", year=2021
                    )
                    await db_conn.execute(
                        "UPDATE vehicle SET first_seen=$1 WHERE vehicle_ulid=$2", base, vid
                    )
                    await _seed_event(
                        db_conn, vehicle_ulid=vid, entity_ulid=entity_ulid, event_type="NEW",
                        old_value=None, new_value={"price": 12000.0}, observed_at=base,
                    )
                rows = await fetch_decay_buckets(db_conn, make_filter=[_MAKE_LOWN])
                assert [r for r in rows if r["model"] == "BucketModel"] == []
                raise _TestRollback()
        except _TestRollback:
            pass


@pytest.mark.integration
class TestRunDecay:
    @pytest.mark.asyncio
    async def test_writes_run_and_rows_with_passing_crosscheck(self, db_conn: asyncpg.Connection) -> None:
        try:
            async with db_conn.transaction():
                base = datetime.now(timezone.utc) - timedelta(days=200)
                for k in range(1, 51):
                    eid, vid = await _seed_entity_vehicle(db_conn, make=_MAKE_CYCLE, model="RunModel", year=2020)
                    await _seed_event(
                        db_conn, vehicle_ulid=vid, entity_ulid=eid, event_type="NEW",
                        old_value=None, new_value={"price": 20000.0}, observed_at=base,
                    )
                    await _seed_event(
                        db_conn, vehicle_ulid=vid, entity_ulid=eid, event_type="GONE",
                        old_value={"price": 20000.0}, new_value=None,
                        observed_at=base + timedelta(days=k),
                    )

                run_id, checks = await run_decay(db_conn, make_filter=[_MAKE_CYCLE])
                assert checks["cycle_stats"]["passed"] is True
                assert checks["cycle_stats"]["sampled"] >= 1

                row = await db_conn.fetchrow(
                    "SELECT * FROM market_cycle_stats WHERE run_id=$1 AND model='RunModel'", run_id
                )
                assert row is not None
                assert row["n_cycles"] == 50

                raise _TestRollback()
        except _TestRollback:
            pass

        exists = await db_conn.fetchval("SELECT EXISTS(SELECT 1 FROM vehicle WHERE make=$1)", _MAKE_CYCLE)
        assert not exists, "rollback failed: synthetic decay vehicles leaked into real DB"
