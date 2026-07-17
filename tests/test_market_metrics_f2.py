"""Integration tests for pipeline/market/metrics_f2.py (M3/M4/M5/M7/M9/M10, F2).

SAFETY CONTRACT: identical to tests/test_market_compute_stats.py — every DB-touching
test runs inside a rolled-back transaction, synthetic makes/attributes never collide
with real inventory. See tests/market_test_helpers.py for the shared seeding helpers.

Hand-calculated fixture math (percentile_cont formula proven in
tests/test_market_cohort.py):
  values [1..10]      -> p25=3.25, p50=5.5, p75=7.75
  values [100..1000]   -> p25=325, p50=550, p75=775  (step 100, reused from F1)
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta, timezone

import asyncpg
import pytest
import pytest_asyncio

from pipeline.market.cohort import MIN_COHORT_N
from pipeline.market.metrics_f2 import fetch_m3, fetch_m4, fetch_m5, fetch_m7, fetch_m9, fetch_m10
from pipeline.market.compute_stats import fetch_m1
from tests.market_test_helpers import (
    _TestRollback,
    entity_ulid_of,
    seed_event,
    seed_platform_entity,
    seed_platform_listing,
    seed_vehicle,
    vam_verified_run_id,
)

_DSN = os.environ.get(
    "CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
)


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


# ---------------------------------------------------------------------------
# M3 — median days-to-retirada
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestFetchM3:
    @pytest.mark.asyncio
    async def test_median_days_matches_hand_calculated(self, db_conn: asyncpg.Connection) -> None:
        make = "__CARDEEP_TEST_M3__"
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                base_first_seen = datetime.now(timezone.utc) - timedelta(days=25)
                for days in range(1, 11):  # 1..10 -> median 5.5
                    vul = await seed_vehicle(
                        db_conn, run_id, make=make, model="M3Model", fuel="gasolina",
                        year=2024, province_code="28", price=10000.0, status="gone",
                        first_seen=base_first_seen,
                    )
                    eul = await entity_ulid_of(db_conn, vul)
                    await seed_event(
                        db_conn, vehicle_ulid=vul, entity_ulid=eul, event_type="GONE",
                        old_value={"price": 10000.0}, new_value=None,
                        observed_at=base_first_seen + timedelta(days=days),
                    )

                rows, n_in, window = await fetch_m3(db_conn, span_days=90.0, make_filter=[make])

                assert n_in == 10
                assert window == 90.0
                prov_rows = [r for r in rows if r.scope == "prov"]
                assert len(prov_rows) == 1
                assert prov_rows[0].n == 10
                assert prov_rows[0].value_num == pytest.approx(5.5, abs=0.01)

                raise _TestRollback("rollback M3 fixture")
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_below_min_cohort_suppressed(self, db_conn: asyncpg.Connection) -> None:
        make = "__CARDEEP_TEST_M3_LOWN__"
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                base_first_seen = datetime.now(timezone.utc) - timedelta(days=10)
                for days in range(1, 6):  # only 5 GONE events, n<8
                    vul = await seed_vehicle(
                        db_conn, run_id, make=make, model="M3Model", fuel="gasolina",
                        year=2024, province_code="28", price=10000.0, status="gone",
                        first_seen=base_first_seen,
                    )
                    eul = await entity_ulid_of(db_conn, vul)
                    await seed_event(
                        db_conn, vehicle_ulid=vul, entity_ulid=eul, event_type="GONE",
                        old_value={"price": 10000.0}, new_value=None,
                        observed_at=base_first_seen + timedelta(days=days),
                    )

                rows, n_in, _ = await fetch_m3(db_conn, span_days=90.0, make_filter=[make])
                assert n_in == 5
                assert rows == []

                raise _TestRollback("rollback M3 lown fixture")
        except _TestRollback:
            pass


# ---------------------------------------------------------------------------
# M4 — Market Days Supply
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestFetchM4:
    @pytest.mark.asyncio
    async def test_mds_computed_from_m1_availability_and_gone_window(
        self, db_conn: asyncpg.Connection
    ) -> None:
        make = "__CARDEEP_TEST_M4__"
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                # 10 AVAILABLE vehicles -> M1 n=10 (feeds M4 numerator)
                for i in range(10):
                    await seed_vehicle(
                        db_conn, run_id, make=make, model="M4Model", fuel="gasolina",
                        year=2024, province_code="28", price=10000.0 + i, status="available",
                    )
                # 9 GONE events within a 45-day window -> gone_n=9
                base_first_seen = datetime.now(timezone.utc) - timedelta(days=20)
                for i in range(9):
                    vul = await seed_vehicle(
                        db_conn, run_id, make=make, model="M4Model", fuel="gasolina",
                        year=2024, province_code="28", price=9000.0, status="gone",
                        first_seen=base_first_seen,
                    )
                    eul = await entity_ulid_of(db_conn, vul)
                    await seed_event(
                        db_conn, vehicle_ulid=vul, entity_ulid=eul, event_type="GONE",
                        old_value={"price": 9000.0}, new_value=None,
                        observed_at=base_first_seen + timedelta(days=5),
                    )

                m1_rows, _ = await fetch_m1(db_conn, make_filter=[make])
                m4_rows, window = await fetch_m4(db_conn, m1_rows, span_days=90.0, make_filter=[make])

                assert window == 45.0  # min(45, 90)
                prov_m4 = [r for r in m4_rows if r.scope == "prov"]
                assert len(prov_m4) == 1
                row = prov_m4[0]
                assert row.n == 10  # available_n from M1
                # MDS = available_n / (gone_n/window) = 10 / (9/45) = 50.0
                assert row.value_num == pytest.approx(50.0, abs=0.01)
                assert row.value_extra["gone_n"] == 9

                raise _TestRollback("rollback M4 fixture")
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_zero_gone_reports_no_rotation_observed(self, db_conn: asyncpg.Connection) -> None:
        make = "__CARDEEP_TEST_M4_NOGONE__"
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                for i in range(10):
                    await seed_vehicle(
                        db_conn, run_id, make=make, model="M4Model", fuel="gasolina",
                        year=2024, province_code="28", price=10000.0 + i, status="available",
                    )
                m1_rows, _ = await fetch_m1(db_conn, make_filter=[make])
                m4_rows, _ = await fetch_m4(db_conn, m1_rows, span_days=90.0, make_filter=[make])

                prov_m4 = [r for r in m4_rows if r.scope == "prov"]
                assert len(prov_m4) == 1
                assert prov_m4[0].value_num is None
                assert prov_m4[0].value_extra["status"] == "no_rotation_observed"

                raise _TestRollback("rollback M4 no-gone fixture")
        except _TestRollback:
            pass


# ---------------------------------------------------------------------------
# M5 — provincial absorption rate
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestFetchM5:
    @pytest.mark.asyncio
    async def test_absorption_rate_hand_calculated(self, db_conn: asyncpg.Connection) -> None:
        make = "__CARDEEP_TEST_M5__"
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                for i in range(20):  # n_avail = 20
                    await seed_vehicle(
                        db_conn, run_id, make=make, model="M5Model", fuel="gasolina",
                        year=2024, province_code="28", price=10000.0 + i, status="available",
                    )
                base_first_seen = datetime.now(timezone.utc) - timedelta(days=15)
                for i in range(5):  # n_gone = 5 within window
                    vul = await seed_vehicle(
                        db_conn, run_id, make=make, model="M5Model", fuel="gasolina",
                        year=2024, province_code="28", price=9000.0, status="gone",
                        first_seen=base_first_seen,
                    )
                    eul = await entity_ulid_of(db_conn, vul)
                    await seed_event(
                        db_conn, vehicle_ulid=vul, entity_ulid=eul, event_type="GONE",
                        old_value={"price": 9000.0}, new_value=None,
                        observed_at=base_first_seen + timedelta(days=2),
                    )

                rows, n_in, window = await fetch_m5(db_conn, span_days=90.0, make_filter=[make])

                assert n_in == 20
                assert window == 30.0  # min(30, 90)
                assert len(rows) == 1
                row = rows[0]
                assert row.province_code == "28"
                assert row.n == 20
                assert row.value_num == pytest.approx(5 / 20, abs=1e-9)

                raise _TestRollback("rollback M5 fixture")
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_below_min_cohort_province_suppressed(self, db_conn: asyncpg.Connection) -> None:
        make = "__CARDEEP_TEST_M5_LOWN__"
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                for i in range(3):  # n_avail = 3 < 8
                    await seed_vehicle(
                        db_conn, run_id, make=make, model="M5Model", fuel="gasolina",
                        year=2024, province_code="28", price=10000.0 + i, status="available",
                    )
                rows, n_in, _ = await fetch_m5(db_conn, span_days=90.0, make_filter=[make])
                assert n_in == 3
                assert rows == []

                raise _TestRollback("rollback M5 lown fixture")
        except _TestRollback:
            pass


# ---------------------------------------------------------------------------
# M7 — price momentum (entry price, early vs late half)
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestFetchM7:
    @pytest.mark.asyncio
    async def test_momentum_hand_calculated_ten_pct_increase(
        self, db_conn: asyncpg.Connection
    ) -> None:
        make = "__CARDEEP_TEST_M7__"
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                anchor_row = await db_conn.fetchrow("SELECT max(observed_at) AS mx FROM vehicle_event")
                anchor = anchor_row["mx"]

                early_prices = [100.0 * (i + 1) for i in range(10)]   # 100..1000, p50=550
                late_prices = [110.0 * (i + 1) for i in range(10)]    # 110..1100, p50=605

                for price in early_prices:
                    vul = await seed_vehicle(
                        db_conn, run_id, make=make, model="M7Model", fuel="gasolina",
                        year=2024, province_code="28", price=price, status="available",
                        first_seen=anchor - timedelta(days=45),
                    )
                    eul = await entity_ulid_of(db_conn, vul)
                    await seed_event(
                        db_conn, vehicle_ulid=vul, entity_ulid=eul, event_type="NEW",
                        old_value=None, new_value={"price": price},
                        observed_at=anchor - timedelta(days=45),
                    )
                for price in late_prices:
                    vul = await seed_vehicle(
                        db_conn, run_id, make=make, model="M7Model", fuel="gasolina",
                        year=2024, province_code="28", price=price, status="available",
                        first_seen=anchor - timedelta(days=10),
                    )
                    eul = await entity_ulid_of(db_conn, vul)
                    await seed_event(
                        db_conn, vehicle_ulid=vul, entity_ulid=eul, event_type="NEW",
                        old_value=None, new_value={"price": price},
                        observed_at=anchor - timedelta(days=10),
                    )

                rows, half = await fetch_m7(db_conn, span_days=90.0, make_filter=[make])

                assert half == 30.0  # min-half of 90d span -> nominal 30
                prov_rows = [r for r in rows if r.scope == "prov"]
                assert len(prov_rows) == 1
                row = prov_rows[0]
                assert row.value_extra["p50_early"] == pytest.approx(550.0)
                assert row.value_extra["p50_late"] == pytest.approx(605.0)
                assert row.value_num == pytest.approx(10.0, abs=0.01)  # +10%

                raise _TestRollback("rollback M7 fixture")
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_missing_early_half_suppresses_row(self, db_conn: asyncpg.Connection) -> None:
        make = "__CARDEEP_TEST_M7_NOEARLY__"
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                anchor_row = await db_conn.fetchrow("SELECT max(observed_at) AS mx FROM vehicle_event")
                anchor = anchor_row["mx"]
                # ONLY late-half entries (no early-half data at all for this make)
                for i in range(10):
                    price = 100.0 * (i + 1)
                    vul = await seed_vehicle(
                        db_conn, run_id, make=make, model="M7Model", fuel="gasolina",
                        year=2024, province_code="28", price=price, status="available",
                        first_seen=anchor - timedelta(days=10),
                    )
                    eul = await entity_ulid_of(db_conn, vul)
                    await seed_event(
                        db_conn, vehicle_ulid=vul, entity_ulid=eul, event_type="NEW",
                        old_value=None, new_value={"price": price},
                        observed_at=anchor - timedelta(days=10),
                    )

                rows, _ = await fetch_m7(db_conn, span_days=90.0, make_filter=[make])
                assert rows == [], "no early-half data -> momentum must never be fabricated"

                raise _TestRollback("rollback M7 no-early fixture")
        except _TestRollback:
            pass


# ---------------------------------------------------------------------------
# M9 — seller price-pressure
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestFetchM9:
    @pytest.mark.asyncio
    async def test_pct_with_cut_and_median_cut_hand_calculated(
        self, db_conn: asyncpg.Connection
    ) -> None:
        make = "__CARDEEP_TEST_M9__"
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                now = datetime.now(timezone.utc)
                # 10 available vehicles total (M1 population)
                vulids = []
                for i in range(10):
                    vul = await seed_vehicle(
                        db_conn, run_id, make=make, model="M9Model", fuel="gasolina",
                        year=2024, province_code="28", price=900.0, status="available",
                    )
                    vulids.append(vul)
                # 3 of them get a net price cut of exactly 10% (1000 -> 900)
                for vul in vulids[:3]:
                    eul = await entity_ulid_of(db_conn, vul)
                    await seed_event(
                        db_conn, vehicle_ulid=vul, entity_ulid=eul, event_type="PRICE_CHANGE",
                        old_value={"price": 1000.0}, new_value={"price": 900.0},
                        observed_at=now - timedelta(days=5),
                    )

                m1_rows, _ = await fetch_m1(db_conn, make_filter=[make])
                m9_rows, window = await fetch_m9(db_conn, m1_rows, span_days=90.0, make_filter=[make])

                assert window == 30.0
                prov_rows = [r for r in m9_rows if r.scope == "prov"]
                assert len(prov_rows) == 1
                row = prov_rows[0]
                assert row.n == 10
                assert row.value_num == pytest.approx(30.0, abs=0.01)  # 3/10 = 30%
                assert row.value_extra["median_cut_pct"] == pytest.approx(10.0, abs=0.01)

                raise _TestRollback("rollback M9 fixture")
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_no_price_changes_reports_zero_pressure(self, db_conn: asyncpg.Connection) -> None:
        make = "__CARDEEP_TEST_M9_NOCUT__"
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                for i in range(10):
                    await seed_vehicle(
                        db_conn, run_id, make=make, model="M9Model", fuel="gasolina",
                        year=2024, province_code="28", price=1000.0, status="available",
                    )
                m1_rows, _ = await fetch_m1(db_conn, make_filter=[make])
                m9_rows, _ = await fetch_m9(db_conn, m1_rows, span_days=90.0, make_filter=[make])

                prov_rows = [r for r in m9_rows if r.scope == "prov"]
                assert len(prov_rows) == 1
                assert prov_rows[0].value_num == 0.0
                assert prov_rows[0].value_extra["median_cut_pct"] is None

                raise _TestRollback("rollback M9 no-cut fixture")
        except _TestRollback:
            pass


# ---------------------------------------------------------------------------
# M10 — multi-platform presence distribution
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestFetchM10:
    @pytest.mark.asyncio
    async def test_platform_count_distribution_hand_calculated(
        self, db_conn: asyncpg.Connection
    ) -> None:
        make = "__CARDEEP_TEST_M10__"
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                platform_entities = [await seed_platform_entity(db_conn) for _ in range(10)]

                for i in range(1, 11):  # vehicle i gets i distinct platforms -> n_platforms=[1..10]
                    vul = await seed_vehicle(
                        db_conn, run_id, make=make, model="M10Model", fuel="gasolina",
                        year=2024, province_code="28", price=10000.0, status="available",
                    )
                    for j in range(i):
                        await seed_platform_listing(
                            db_conn, vehicle_ulid=vul,
                            platform_entity_ulid=platform_entities[j],
                            listing_url=f"https://platform{j}.test/{vul}",
                        )

                rows = await fetch_m10(db_conn, make_filter=[make])
                prov_rows = [r for r in rows if r.scope == "prov"]
                assert len(prov_rows) == 1
                row = prov_rows[0]
                assert row.n == 10
                assert row.p25 == pytest.approx(3.25, abs=0.01)
                assert row.p50 == pytest.approx(5.5, abs=0.01)
                assert row.p75 == pytest.approx(7.75, abs=0.01)

                raise _TestRollback("rollback M10 fixture")
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_no_platform_listings_defaults_to_zero(self, db_conn: asyncpg.Connection) -> None:
        make = "__CARDEEP_TEST_M10_ZERO__"
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                for _ in range(10):
                    await seed_vehicle(
                        db_conn, run_id, make=make, model="M10Model", fuel="gasolina",
                        year=2024, province_code="28", price=10000.0, status="available",
                    )
                rows = await fetch_m10(db_conn, make_filter=[make])
                prov_rows = [r for r in rows if r.scope == "prov"]
                assert len(prov_rows) == 1
                assert prov_rows[0].p50 == 0.0  # no platform_listing rows -> all zero

                raise _TestRollback("rollback M10 zero fixture")
        except _TestRollback:
            pass
