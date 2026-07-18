"""Tests for pipeline/arbitrage/geo.py (04-arbitrage.md F5 — geo-arbitrage).

SAFETY CONTRACT (same as tests/test_arbitrage_score.py): rolled-back transactions,
distinctive ``__CARDEEP_TEST_...__`` makes.
"""
from __future__ import annotations

import asyncio
import math
import os

import asyncpg
import pytest
import pytest_asyncio

from pipeline.arbitrage.geo import (
    GEO_CELL_MIN_N,
    GEO_GAP_SIGNIFICANCE_FACTOR,
    compute_geo_gaps,
    fetch_geo_cells,
    run_geo,
)
from pipeline.ids import ulid

_DSN = os.environ.get(
    "CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
)

_MAKE = "__CARDEEP_TEST_GEO__"
_MAKE_LOWN = "__CARDEEP_TEST_GEO_LOWN__"


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


async def _seed_vehicle(
    conn: asyncpg.Connection, *, make: str, model: str, year: int, province_code: str, price: float
) -> str:
    entity_ulid = ulid()
    vehicle_ulid = ulid()
    cdp_code = f"CDP-ES-{province_code}-TST{vehicle_ulid[-8:]}"
    await conn.execute(
        "INSERT INTO entity (entity_ulid, cdp_code, kind, province_code, status) "
        "VALUES ($1, $2, 'compraventa', $3, 'unverified')",
        entity_ulid, cdp_code, province_code,
    )
    await conn.execute(
        "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, make, model, year, price, status) "
        "VALUES ($1,$2,$3,$4,$5,$6,$7,'available')",
        vehicle_ulid, entity_ulid, f"https://example.test/{vehicle_ulid}", make, model, year, price,
    )
    return vehicle_ulid


class TestComputeGeoGaps:
    def test_two_cells_far_apart_produce_a_significant_gap(self):
        """MAD~0 (near-degenerate but at the floor) -> even a modest median gap is
        'significant' by construction; cheap/expensive ordering is correct."""
        cells = [
            {"country_code": "ES", "make": "Golf", "model": "TestModel", "year_band_start": 2020,
             "province_code": "28", "n": 20, "median_ln_price": 9.0, "mad_ln_price": 0.05, "median_price": 8000.0},
            {"country_code": "ES", "make": "Golf", "model": "TestModel", "year_band_start": 2020,
             "province_code": "08", "n": 20, "median_ln_price": 9.5, "mad_ln_price": 0.05, "median_price": 20000.0},
        ]
        gaps = compute_geo_gaps(cells)
        assert len(gaps) == 1
        g = gaps[0]
        assert g["province_cheap"] == "28"
        assert g["province_expensive"] == "08"
        assert g["gap_eur"] == pytest.approx(12000.0)

    def test_close_medians_within_uncertainty_produce_no_gap(self):
        cells = [
            {"country_code": "ES", "make": "Golf", "model": "TestModel", "year_band_start": 2020,
             "province_code": "28", "n": 20, "median_ln_price": 9.0, "mad_ln_price": 0.3, "median_price": 8000.0},
            {"country_code": "ES", "make": "Golf", "model": "TestModel", "year_band_start": 2020,
             "province_code": "08", "n": 20, "median_ln_price": 9.02, "mad_ln_price": 0.3, "median_price": 8200.0},
        ]
        gaps = compute_geo_gaps(cells)
        assert gaps == []

    def test_different_cohorts_never_paired(self):
        """Cells from DIFFERENT (make, model, year_band) cohorts are never compared,
        even with wildly different prices."""
        cells = [
            {"country_code": "ES", "make": "Golf", "model": "A", "year_band_start": 2020,
             "province_code": "28", "n": 20, "median_ln_price": 9.0, "mad_ln_price": 0.05, "median_price": 8000.0},
            {"country_code": "ES", "make": "Porsche", "model": "911", "year_band_start": 2020,
             "province_code": "08", "n": 20, "median_ln_price": 12.0, "mad_ln_price": 0.05, "median_price": 200000.0},
        ]
        assert compute_geo_gaps(cells) == []


@pytest.mark.integration
class TestFetchGeoCells:
    @pytest.mark.asyncio
    async def test_cell_clears_min_n_and_math_is_internally_consistent(
        self, db_conn: asyncpg.Connection
    ) -> None:
        assert GEO_CELL_MIN_N == 15
        try:
            async with db_conn.transaction():
                # Varied prices (not all-identical) so MAD clears COHORT_MAD_FLOOR — an
                # all-identical fixture would have MAD=0 and be correctly SKIPPED by the
                # Law-I floor guard (see test_degenerate_cell_below_mad_floor_is_suppressed).
                prices = [9000, 9200, 9400, 9600, 9800, 10000, 10000, 10200,
                          10200, 10400, 10600, 10800, 11000, 11200, 11400]
                for p in prices:
                    await _seed_vehicle(
                        db_conn, make=_MAKE, model="TestModel", year=2020,
                        province_code="28", price=float(p),
                    )
                cells = await fetch_geo_cells(db_conn, make_filter=[_MAKE])
                assert len(cells) == 1
                c = cells[0]
                assert c["n"] == 15
                assert c["province_code"] == "28"
                # sorted prices, 15 values (odd n): median is the 8th (0-indexed 7th) = 10200.
                assert c["median_price"] == pytest.approx(10200.0)
                raise _TestRollback()
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_degenerate_cell_below_mad_floor_is_suppressed(
        self, db_conn: asyncpg.Connection
    ) -> None:
        """All 15 prices identical -> MAD=0 < COHORT_MAD_FLOOR -> Law I skips the cell
        entirely (never a spurious 'gap' amplified from a near-zero denominator)."""
        try:
            async with db_conn.transaction():
                for _i in range(15):
                    await _seed_vehicle(
                        db_conn, make=_MAKE_LOWN, model="DegenModel", year=2020,
                        province_code="28", price=10000.0,
                    )
                cells = await fetch_geo_cells(db_conn, make_filter=[_MAKE_LOWN])
                assert [c for c in cells if c["model"] == "DegenModel"] == []
                raise _TestRollback()
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_below_min_n_cell_is_suppressed(self, db_conn: asyncpg.Connection) -> None:
        try:
            async with db_conn.transaction():
                for i in range(10):  # 10 < GEO_CELL_MIN_N(15)
                    await _seed_vehicle(
                        db_conn, make=_MAKE_LOWN, model="TestModel", year=2020,
                        province_code="28", price=10000.0 + i * 100,
                    )
                cells = await fetch_geo_cells(db_conn, make_filter=[_MAKE_LOWN])
                assert cells == [], "n=10<15 must be suppressed"
                raise _TestRollback()
        except _TestRollback:
            pass


@pytest.mark.integration
class TestRunGeo:
    @pytest.mark.asyncio
    async def test_writes_cells_and_significant_gap_across_two_provinces(
        self, db_conn: asyncpg.Connection
    ) -> None:
        try:
            async with db_conn.transaction():
                # Province 28: 15 cars, median 8000, hand-verified MAD (ln) = 0.2076 > floor.
                base_low = [5000, 5500, 6000, 6500, 7000, 7500, 8000, 8000, 8500, 9000,
                            9500, 10000, 10500, 11000, 12000]
                for p in base_low:
                    await _seed_vehicle(
                        db_conn, make=_MAKE, model="GapModel", year=2020, province_code="28", price=float(p)
                    )
                # Province 08: 15 cars, median 20000, hand-verified MAD (ln) = 0.1054 > floor.
                # Hand-verified significant: sigma_low=2462.77€, sigma_high=3124.15€,
                # threshold=1.5*sqrt(sigma_low^2+sigma_high^2)=5967.20€ < gap=12000€.
                base_high = [15000, 16000, 17000, 18000, 18500, 19000, 19500, 20000,
                             20000, 20500, 21500, 22500, 23500, 24500, 26000]
                for p in base_high:
                    await _seed_vehicle(
                        db_conn, make=_MAKE, model="GapModel", year=2020, province_code="08", price=float(p)
                    )

                run_id, checks = await run_geo(db_conn, make_filter=[_MAKE])
                assert checks["passed"] is True

                cells = await db_conn.fetch(
                    "SELECT * FROM geo_price_cell WHERE run_id=$1 AND model='GapModel'", run_id
                )
                assert len(cells) == 2

                gap = await db_conn.fetchrow(
                    "SELECT * FROM geo_price_gap WHERE run_id=$1 AND model='GapModel'", run_id
                )
                assert gap is not None
                assert gap["province_cheap"] == "28"
                assert gap["province_expensive"] == "08"
                assert float(gap["median_cheap"]) == pytest.approx(8000.0)
                assert float(gap["median_expensive"]) == pytest.approx(20000.0)
                assert float(gap["gap_eur"]) == pytest.approx(12000.0)

                raise _TestRollback()
        except _TestRollback:
            pass

        exists = await db_conn.fetchval("SELECT EXISTS(SELECT 1 FROM vehicle WHERE make=$1)", _MAKE)
        assert not exists, "rollback failed: synthetic geo vehicles leaked into real DB"
