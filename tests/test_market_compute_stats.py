"""Integration tests for pipeline/market/compute_stats.py (M1, CAMPAIGN 01-market-intelligence F1).

SAFETY CONTRACT (same as tests/test_evict.py): every DB-touching test runs inside a
ROLLED-BACK transaction (savepoint via nested asyncpg transaction). Synthetic rows use
distinctive makes ('__CARDEEP_TEST_*__') that cannot collide with real inventory, and
are attached to the SAME (only) vam_verified cluster_run_id so they resolve through
v_canonical_vehicle exactly like production data — then the whole transaction is rolled
back, leaving the real corpus untouched.

Fixture math (hand-verified, see tests/test_market_cohort.py for the pure-function
proof): 10 prices [100,200,...,1000] -> p25=325, p50=550, p75=775, n=10.
"""
from __future__ import annotations

import asyncio
import os

import asyncpg
import pytest
import pytest_asyncio

from pipeline.ids import ulid
from pipeline.market.cohort import MIN_COHORT_N
from pipeline.market.compute_stats import fetch_m1, run_compute

_DSN = os.environ.get(
    "CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
)

_MAKE_10 = "__CARDEEP_TEST_MAKE_N10__"       # n=10 in one province -> 'prov' row fires
_MAKE_LOWN = "__CARDEEP_TEST_MAKE_LOWN__"    # n=5 -> suppressed everywhere (n<8)
_MAKE_NAT = "__CARDEEP_TEST_MAKE_NAT__"      # 5+5 split across 2 provinces -> only 'nat' fires

_PRICES_10 = [100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0]


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


async def _vam_verified_run_id(conn: asyncpg.Connection) -> str:
    row = await conn.fetchrow(
        "SELECT cluster_run_id FROM vehicle_cluster_run WHERE vam_verified = TRUE "
        "ORDER BY run_at DESC LIMIT 1"
    )
    assert row is not None, "no vam_verified vehicle_cluster_run exists — F0 precondition violated"
    return row["cluster_run_id"]


async def _seed_vehicle(
    conn: asyncpg.Connection,
    cluster_run_id: str,
    *,
    make: str,
    model: str,
    fuel: str,
    year: int,
    province_code: str,
    price: float,
) -> str:
    """Insert one synthetic entity+vehicle+vehicle_cluster row (self-canonical) and
    return the vehicle_ulid. All FKs valid, passes servable_vehicle + v_canonical_vehicle."""
    entity_ulid = ulid()
    vehicle_ulid = ulid()
    cdp_code = f"CDP-ES-{province_code}-TST{vehicle_ulid[-8:]}"
    await conn.execute(
        "INSERT INTO entity (entity_ulid, cdp_code, kind, province_code, status) "
        "VALUES ($1, $2, 'compraventa'::entity_kind, $3, 'unverified'::entity_status)",
        entity_ulid, cdp_code, province_code,
    )
    await conn.execute(
        "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, make, model, year, "
        "fuel, price, status) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,'available')",
        vehicle_ulid, entity_ulid, f"https://example.test/{vehicle_ulid}",
        make, model, year, fuel, price,
    )
    await conn.execute(
        "INSERT INTO vehicle_cluster (cluster_run_id, vehicle_ulid, canonical_vehicle_ulid, "
        "match_signal, cluster_size) VALUES ($1,$2,$2,'test',1)",
        cluster_run_id, vehicle_ulid,
    )
    return vehicle_ulid


@pytest.mark.integration
class TestFetchM1:
    @pytest.mark.asyncio
    async def test_n10_segment_matches_hand_calculated_percentiles(
        self, db_conn: asyncpg.Connection
    ) -> None:
        try:
            async with db_conn.transaction():
                run_id = await _vam_verified_run_id(db_conn)
                for price in _PRICES_10:
                    await _seed_vehicle(
                        db_conn, run_id, make=_MAKE_10, model="TestModel",
                        fuel="gasolina", year=2020, province_code="28", price=price,
                    )

                rows, n_in = await fetch_m1(db_conn, make_filter=[_MAKE_10])

                assert n_in == 10
                prov_rows = [r for r in rows if r.scope == "prov"]
                assert len(prov_rows) == 1, f"expected exactly one provincial cohort, got {prov_rows}"
                row = prov_rows[0]
                assert row.make == _MAKE_10
                assert row.model == "TestModel"
                assert row.fuel == "gasolina"
                assert row.province_code == "28"
                assert row.year == 2020
                assert row.n == 10
                assert row.p25 == pytest.approx(325.0)
                assert row.p50 == pytest.approx(550.0)
                assert row.p75 == pytest.approx(775.0)

                # A national row must ALSO exist (same 10 cars, no province restriction —
                # the carta's national fallback is computed unconditionally, not only
                # when the provincial one is missing).
                nat_rows = [r for r in rows if r.scope == "nat"]
                assert len(nat_rows) == 1
                assert nat_rows[0].n == 10
                assert nat_rows[0].p50 == pytest.approx(550.0)

                raise _TestRollback("rollback n10 fixture")
        except _TestRollback:
            pass

        # Post-rollback: synthetic make must not exist in the real corpus.
        exists = await db_conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM vehicle WHERE make = $1)", _MAKE_10
        )
        assert not exists, "rollback failed: synthetic n10 vehicles leaked into the real DB"

    @pytest.mark.asyncio
    async def test_n_below_min_cohort_is_suppressed_everywhere(
        self, db_conn: asyncpg.Connection
    ) -> None:
        """n=5 < MIN_COHORT_N=8: the carta's hard rule ('n<8 -> jamas un numero') must
        suppress the row at the SQL level (HAVING), not merely hide it in the API layer."""
        try:
            async with db_conn.transaction():
                run_id = await _vam_verified_run_id(db_conn)
                for price in _PRICES_10[:5]:
                    await _seed_vehicle(
                        db_conn, run_id, make=_MAKE_LOWN, model="TestModel",
                        fuel="gasolina", year=2020, province_code="28", price=price,
                    )

                rows, n_in = await fetch_m1(db_conn, make_filter=[_MAKE_LOWN])

                assert n_in == 5
                assert rows == [], f"n=5 < MIN_COHORT_N={MIN_COHORT_N} must yield ZERO rows, got {rows}"

                raise _TestRollback("rollback lown fixture")
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_national_fallback_fires_when_each_province_is_below_min(
        self, db_conn: asyncpg.Connection
    ) -> None:
        """5 cars in province 28 + 5 in province 08 (each < 8, so BOTH provincial rows
        are suppressed) but the combined national cohort (n=10) clears the bar — the
        carta §6 fallback ("si n<8 en tu provincia, dato nacional") must fire."""
        try:
            async with db_conn.transaction():
                run_id = await _vam_verified_run_id(db_conn)
                for price in _PRICES_10[:5]:
                    await _seed_vehicle(
                        db_conn, run_id, make=_MAKE_NAT, model="NatModel",
                        fuel="diesel", year=2021, province_code="28", price=price,
                    )
                for price in _PRICES_10[5:]:
                    await _seed_vehicle(
                        db_conn, run_id, make=_MAKE_NAT, model="NatModel",
                        fuel="diesel", year=2021, province_code="08", price=price,
                    )

                rows, n_in = await fetch_m1(db_conn, make_filter=[_MAKE_NAT])

                assert n_in == 10
                prov_rows = [r for r in rows if r.scope == "prov"]
                assert prov_rows == [], f"both provinces have n=5<8, no 'prov' row should fire: {prov_rows}"

                nat_rows = [r for r in rows if r.scope == "nat"]
                assert len(nat_rows) == 1
                assert nat_rows[0].n == 10
                assert nat_rows[0].p25 == pytest.approx(325.0)
                assert nat_rows[0].p50 == pytest.approx(550.0)
                assert nat_rows[0].p75 == pytest.approx(775.0)

                raise _TestRollback("rollback nat fixture")
        except _TestRollback:
            pass


@pytest.mark.integration
class TestRunCompute:
    @pytest.mark.asyncio
    async def test_run_compute_writes_run_and_rows_unpublished_by_default(
        self, db_conn: asyncpg.Connection
    ) -> None:
        try:
            async with db_conn.transaction():
                run_id_fixture = await _vam_verified_run_id(db_conn)
                for price in _PRICES_10:
                    await _seed_vehicle(
                        db_conn, run_id_fixture, make=_MAKE_10, model="TestModel",
                        fuel="gasolina", year=2020, province_code="28", price=price,
                    )

                new_run_id = await run_compute(db_conn, make_filter=[_MAKE_10])

                run_row = await db_conn.fetchrow(
                    "SELECT published, n_in, methodology_version, metrics_computed "
                    "FROM market_stat_run WHERE run_id = $1", new_run_id
                )
                assert run_row is not None
                assert run_row["published"] is False, "F1 must NEVER auto-publish a run"
                assert run_row["n_in"] == 10
                assert run_row["metrics_computed"] == ["M1"]

                stat_rows = await db_conn.fetch(
                    "SELECT metric_id, make, n, p25, p50, p75 FROM market_stat WHERE run_id = $1",
                    new_run_id,
                )
                assert len(stat_rows) == 2  # one 'prov' + one 'nat' row for this segment
                for r in stat_rows:
                    assert r["metric_id"] == "M1"
                    assert r["n"] == 10
                    assert float(r["p50"]) == pytest.approx(550.0)

                raise _TestRollback("rollback run_compute fixture")
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_run_compute_crosscheck_recorded_in_checks(
        self, db_conn: asyncpg.Connection
    ) -> None:
        try:
            async with db_conn.transaction():
                run_id_fixture = await _vam_verified_run_id(db_conn)
                for price in _PRICES_10:
                    await _seed_vehicle(
                        db_conn, run_id_fixture, make=_MAKE_10, model="TestModel",
                        fuel="gasolina", year=2020, province_code="28", price=price,
                    )

                new_run_id = await run_compute(db_conn, make_filter=[_MAKE_10])

                import json
                checks_raw = await db_conn.fetchval(
                    "SELECT checks FROM market_stat_run WHERE run_id = $1", new_run_id
                )
                checks = json.loads(checks_raw) if isinstance(checks_raw, str) else checks_raw
                assert checks["sampled"] >= 1
                assert checks["passed"] is True
                assert checks["max_divergence_pct"] < 0.5

                raise _TestRollback("rollback crosscheck fixture")
        except _TestRollback:
            pass
