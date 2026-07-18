"""Tests for pipeline/arbitrage/score.py (04-arbitrage.md F1 — deal-score backend).

SAFETY CONTRACT (same as tests/test_market_compute_stats.py): every DB-touching test
runs inside a ROLLED-BACK transaction. Synthetic rows use a distinctive make
('__CARDEEP_TEST_ARB__') that cannot collide with real inventory, then the whole
transaction is rolled back, leaving the real corpus untouched.

Fixture math (hand-verified independently in pure Python — see module docstring of
each test for the exact numbers): 20 "normal" prices [10000..19500 step 500] + two
outliers (6000, 3000) -> n=22 (clears Tier-A min=15). ``median_price`` is
percentile_cont(0.5) on the RAW price domain (arithmetic median: sorted prices'
middle pair is 14000/14500 -> 14250.0); ``median_ln_price``/``mad_ln_price`` are
computed independently in the ln domain (NOT exp() of the raw-price median — the two
domains interpolate differently for an even n, by construction, exactly as
detect_price_trap's original SQL already did before this module factored it out).
mad_ln_price=0.19110412297194834, z(6000)=-3.0524 (bajo_mercado band),
z(3000)=-5.4988 (chollo_fuerte band).
"""
from __future__ import annotations

import asyncio
import math
import os
import statistics

import asyncpg
import pytest
import pytest_asyncio

from pipeline.arbitrage.score import (
    DEAL_SCORE_BAJO_MERCADO_Z,
    DEAL_SCORE_CHOLLO_FUERTE_Z,
    DEAL_SCORE_FLOOR_Z,
    band_for_z,
    run_score,
)
from pipeline.gestionador.detect import PRICE_TRAP_COHORT_Z
from pipeline.ids import ulid

_DSN = os.environ.get(
    "CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
)

_MAKE = "__CARDEEP_TEST_ARB__"
_MAKE_LOWN = "__CARDEEP_TEST_ARB_LOWN__"
_MAKE_QUAR = "__CARDEEP_TEST_ARB_QUAR__"

_NORMAL_PRICES = [10000 + i * 500 for i in range(20)]
_OUTLIER_BAJO_MERCADO = 6000.0    # hand-verified z=-3.0524 -> 'bajo_mercado'
_OUTLIER_CHOLLO_FUERTE = 3000.0   # hand-verified z=-5.4988 -> 'chollo_fuerte'
# Raw-price-domain median (percentile_cont(0.5) ORDER BY price): sorted 22 prices'
# middle pair is (14000, 14500) -> arithmetic mean 14250.0.
_EXPECTED_MEDIAN_PRICE = 14250.0
_EXPECTED_MAD_LN = 0.19110412297194834


class _TestRollback(Exception):
    """Raised to unwind the outer transaction — see module docstring."""


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
    conn: asyncpg.Connection, *, make: str, model: str, year: int, province_code: str, price: float,
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
        "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, make, model, year, "
        "price, status) VALUES ($1,$2,$3,$4,$5,$6,$7,'available')",
        vehicle_ulid, entity_ulid, f"https://example.test/{vehicle_ulid}",
        make, model, year, price,
    )
    return vehicle_ulid


async def _quarantine(conn: asyncpg.Connection, vehicle_ulid: str) -> None:
    """Open a price_trap-style quarantining gestion_item for *vehicle_ulid* — the
    exact mechanism servable_vehicle checks (0031/0047_servable_price_ceiling.sql)."""
    await conn.execute(
        "INSERT INTO gestion_item (detector, subject_type, subject_key, severity, "
        "measured, lane, quarantines, dedupe_key) "
        "VALUES ('price_trap', 'vehicle', $1, 'critical', '{}'::jsonb, 'QUARANTINE', TRUE, $2)",
        vehicle_ulid, f"test_quarantine|{vehicle_ulid}",
    )


# ---------------------------------------------------------------------------
# Pure-function unit tests: band_for_z boundaries (no DB)
# ---------------------------------------------------------------------------

class TestBandForZ:
    def test_floor_boundary_is_excluded_price_trap_territory(self):
        assert DEAL_SCORE_FLOOR_Z == -PRICE_TRAP_COHORT_Z == -6.0
        assert band_for_z(-6.0) is None
        assert band_for_z(-6.0001) is None
        assert band_for_z(-100.0) is None

    def test_just_above_floor_is_chollo_fuerte(self):
        assert band_for_z(-5.9999) == "chollo_fuerte"

    def test_chollo_fuerte_upper_boundary_inclusive(self):
        assert DEAL_SCORE_CHOLLO_FUERTE_Z == -3.5
        assert band_for_z(-3.5) == "chollo_fuerte"
        assert band_for_z(-3.4999) == "bajo_mercado"

    def test_bajo_mercado_upper_boundary_inclusive(self):
        assert DEAL_SCORE_BAJO_MERCADO_Z == -2.0
        assert band_for_z(-2.0) == "bajo_mercado"
        assert band_for_z(-1.9999) is None

    def test_positive_and_zero_z_never_a_deal(self):
        assert band_for_z(0.0) is None
        assert band_for_z(5.0) is None


# ---------------------------------------------------------------------------
# Integration: run_score against the live DB, rolled back
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestRunScore:
    @pytest.mark.asyncio
    async def test_cohort_stats_and_deal_score_match_hand_computed_stats(
        self, db_conn: asyncpg.Connection
    ) -> None:
        try:
            async with db_conn.transaction():
                vids = []
                for price in _NORMAL_PRICES:
                    await _seed_vehicle(
                        db_conn, make=_MAKE, model="TestModel", year=2022,
                        province_code="28", price=price,
                    )
                vid_bajo = await _seed_vehicle(
                    db_conn, make=_MAKE, model="TestModel", year=2022,
                    province_code="28", price=_OUTLIER_BAJO_MERCADO,
                )
                vid_fuerte = await _seed_vehicle(
                    db_conn, make=_MAKE, model="TestModel", year=2022,
                    province_code="28", price=_OUTLIER_CHOLLO_FUERTE,
                )

                run_id, checks = await run_score(db_conn, make_filter=[_MAKE])

                # Dual-path verification (§7 row 1): the job's own recompute matched a
                # fresh independent SQL+Python recompute with zero tolerated drift.
                assert checks["passed"] is True
                assert checks["sampled"] >= 1
                assert checks["max_divergence_pct"] < 0.5

                cohort_row = await db_conn.fetchrow(
                    "SELECT * FROM cohort_stats WHERE run_id=$1 AND make=$2", run_id, _MAKE
                )
                assert cohort_row is not None
                assert cohort_row["n"] == 22
                assert cohort_row["tier"] == "A"
                assert float(cohort_row["median_price"]) == pytest.approx(_EXPECTED_MEDIAN_PRICE, abs=0.01)
                assert float(cohort_row["mad_ln_price"]) == pytest.approx(_EXPECTED_MAD_LN, rel=1e-6)

                deal_bajo = await db_conn.fetchrow(
                    "SELECT * FROM deal_score WHERE run_id=$1 AND vehicle_ulid=$2", run_id, vid_bajo
                )
                assert deal_bajo is not None
                assert deal_bajo["band"] == "bajo_mercado"
                assert float(deal_bajo["z"]) == pytest.approx(-3.0524143265938606, rel=1e-4)
                assert float(deal_bajo["savings_eur"]) == pytest.approx(
                    _EXPECTED_MEDIAN_PRICE - _OUTLIER_BAJO_MERCADO, abs=0.01
                )

                deal_fuerte = await db_conn.fetchrow(
                    "SELECT * FROM deal_score WHERE run_id=$1 AND vehicle_ulid=$2", run_id, vid_fuerte
                )
                assert deal_fuerte is not None
                assert deal_fuerte["band"] == "chollo_fuerte"
                assert float(deal_fuerte["z"]) == pytest.approx(-5.498836522903903, rel=1e-4)

                # None of the 20 "normal" (non-outlier) prices should have cleared the
                # bajo_mercado threshold (z > -2.0 for all of them — they define the median).
                normal_deal_count = await db_conn.fetchval(
                    "SELECT count(*) FROM deal_score WHERE run_id=$1 AND vehicle_ulid != ALL($2::text[])",
                    run_id, [vid_bajo, vid_fuerte],
                )
                assert normal_deal_count == 0

                raise _TestRollback("rollback arb-score fixture")
        except _TestRollback:
            pass

        exists = await db_conn.fetchval("SELECT EXISTS(SELECT 1 FROM vehicle WHERE make=$1)", _MAKE)
        assert not exists, "rollback failed: synthetic __CARDEEP_TEST_ARB__ vehicles leaked into real DB"

    @pytest.mark.asyncio
    async def test_below_tier_a_min_and_no_tier_b_fallback_is_suppressed(
        self, db_conn: asyncpg.Connection
    ) -> None:
        """n=10 < COHORT_MIN_TIER_A(15) and model is present (no Tier-B fallback fires
        for a model-having row) -> zero cohort_stats / deal_score rows for this make."""
        try:
            async with db_conn.transaction():
                for price in _NORMAL_PRICES[:10]:
                    await _seed_vehicle(
                        db_conn, make=_MAKE_LOWN, model="TestModel", year=2022,
                        province_code="28", price=price,
                    )

                run_id, _ = await run_score(db_conn, make_filter=[_MAKE_LOWN])

                cohort_row = await db_conn.fetchrow(
                    "SELECT * FROM cohort_stats WHERE run_id=$1 AND make=$2", run_id, _MAKE_LOWN
                )
                assert cohort_row is None, "n=10<15 must be suppressed at the SQL HAVING, not post-hoc"

                raise _TestRollback("rollback lown fixture")
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_quarantined_vehicle_excluded_from_universe(
        self, db_conn: asyncpg.Connection
    ) -> None:
        """§4.1 frontier: 'un vehículo flaggeado por detect_price_trap NUNCA es chollo'.
        A vehicle with an OPEN quarantining gestion_item is excluded from
        servable_vehicle, hence never scored by the deal-score job at all — even if its
        raw price would otherwise make it the cohort's own outlier."""
        try:
            async with db_conn.transaction():
                for price in _NORMAL_PRICES:
                    await _seed_vehicle(
                        db_conn, make=_MAKE_QUAR, model="TestModel", year=2022,
                        province_code="28", price=price,
                    )
                vid_quarantined = await _seed_vehicle(
                    db_conn, make=_MAKE_QUAR, model="TestModel", year=2022,
                    province_code="28", price=_OUTLIER_CHOLLO_FUERTE,
                )
                await _quarantine(db_conn, vid_quarantined)

                # Sanity: the quarantined vehicle really is invisible on servable_vehicle.
                still_servable = await db_conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM servable_vehicle WHERE vehicle_ulid=$1)",
                    vid_quarantined,
                )
                assert still_servable is False

                run_id, _ = await run_score(db_conn, make_filter=[_MAKE_QUAR])

                deal_row = await db_conn.fetchrow(
                    "SELECT * FROM deal_score WHERE run_id=$1 AND vehicle_ulid=$2",
                    run_id, vid_quarantined,
                )
                assert deal_row is None, "a quarantined vehicle must never surface as a chollo"

                # The 20 remaining (non-quarantined, non-outlier) vehicles form a tight
                # cohort with no z<=-2 candidates -> zero deal_score rows for this make at all.
                any_deal = await db_conn.fetchval(
                    "SELECT count(*) FROM deal_score WHERE run_id=$1 AND cohort_make=$2",
                    run_id, _MAKE_QUAR,
                )
                assert any_deal == 0

                raise _TestRollback("rollback quarantine fixture")
        except _TestRollback:
            pass
