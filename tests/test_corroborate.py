"""Tests for pipeline/market/corroborate.py (M8, F4, 01-market-intelligence).

_month_bounds is a pure unit test. compute_corroboration is an integration test
against the live DB with synthetic fixtures in a rolled-back transaction (same
safety contract as tests/test_market_compute_stats.py / test_market_metrics_f2.py).
"""
from __future__ import annotations

import asyncio
import os
from datetime import date, datetime, timezone

import asyncpg
import pytest
import pytest_asyncio

from pipeline.ids import ulid
from pipeline.market.corroborate import _month_bounds, compute_corroboration
from tests.market_test_helpers import (
    _TestRollback,
    entity_ulid_of,
    seed_event,
    seed_vehicle,
    vam_verified_run_id,
)

_DSN = os.environ.get(
    "CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
)


class TestMonthBounds:
    def test_ordinary_month(self) -> None:
        assert _month_bounds("202606") == (date(2026, 6, 1), date(2026, 7, 1))

    def test_december_rolls_to_next_year(self) -> None:
        assert _month_bounds("202612") == (date(2026, 12, 1), date(2027, 1, 1))

    def test_january(self) -> None:
        assert _month_bounds("202601") == (date(2026, 1, 1), date(2026, 2, 1))


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


async def _seed_dgt_batch(conn: asyncpg.Connection, *, month: str) -> str:
    batch_id = ulid()
    await conn.execute(
        "INSERT INTO dgt_transfer_batch (batch_id, month, source_url, zip_sha256, "
        "n_rows_parsed, double_download_verified) VALUES ($1,$2,'https://test.invalid','deadbeef',0,TRUE)",
        batch_id, month,
    )
    return batch_id


async def _seed_dgt_row(
    conn: asyncpg.Connection, *, batch_id: str, fec: date, marca: str, modelo: str | None,
    cod_tipo: str, cod_provincia_dgt: str, province_code: str | None,
) -> None:
    await conn.execute(
        "INSERT INTO dgt_transfer (batch_id, fec_tramitacion, marca, modelo, cod_tipo, "
        "cod_provincia_dgt, country_code, province_code, clave_tramite) "
        "VALUES ($1,$2,$3,$4,$5,$6,'ES',$7,'2')",
        batch_id, fec, marca, modelo, cod_tipo, cod_provincia_dgt, province_code,
    )


@pytest.mark.integration
class TestComputeCorroboration:
    @pytest.mark.asyncio
    async def test_make_and_make_model_cohorts_computed_correctly(
        self, db_conn: asyncpg.Connection
    ) -> None:
        make = "__CARDEEP_TEST_DGT_MAKE__"
        model = "__CARDEEP_TEST_DGT_MODEL__"
        month = "202601"  # a month with no real production data, avoids collision
        try:
            async with db_conn.transaction():
                batch_id = await _seed_dgt_batch(db_conn, month=month)
                # 3 DGT turismo transfers in province 28, same make+model
                for _ in range(3):
                    await _seed_dgt_row(
                        db_conn, batch_id=batch_id, fec=date(2026, 1, 15),
                        marca=make, modelo=model, cod_tipo="40",
                        cod_provincia_dgt="M", province_code="28",
                    )
                # 1 non-turismo row (should be excluded by the cod_tipo filter)
                await _seed_dgt_row(
                    db_conn, batch_id=batch_id, fec=date(2026, 1, 15),
                    marca=make, modelo=model, cod_tipo="50",  # motorcycle
                    cod_provincia_dgt="M", province_code="28",
                )

                # 5 Cardeep GONE events, same make/model/province, within January
                run_id = await vam_verified_run_id(db_conn)
                for i in range(5):
                    vul = await seed_vehicle(
                        db_conn, run_id, make=make.lower(), model=model.lower(), fuel="gasolina",
                        year=2020, province_code="28", price=10000.0, status="gone",
                        first_seen=datetime(2026, 1, 10, tzinfo=timezone.utc),
                    )
                    eul = await entity_ulid_of(db_conn, vul)
                    await seed_event(
                        db_conn, vehicle_ulid=vul, entity_ulid=eul, event_type="GONE",
                        old_value={"price": 10000.0}, new_value=None,
                        observed_at=datetime(2026, 1, 20, tzinfo=timezone.utc),
                    )

                rows = await compute_corroboration(db_conn, batch_id, month)

                make_key = make.upper()
                model_key = model.upper()

                make_level = [r for r in rows if r["model"] is None and r["make"] == make_key]
                assert len(make_level) == 1
                assert make_level[0]["province_code"] == "28"
                assert make_level[0]["gone_count"] == 5
                assert make_level[0]["dgt_count"] == 3  # the motorcycle row excluded
                assert make_level[0]["ratio"] == pytest.approx(3 / 5)

                make_model_level = [
                    r for r in rows
                    if r["model"] == model_key and r["make"] == make_key
                ]
                assert len(make_model_level) == 1
                assert make_model_level[0]["gone_count"] == 5
                assert make_model_level[0]["dgt_count"] == 3

                raise _TestRollback("rollback corroboration fixture")
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_cohort_present_only_on_one_side_is_not_dropped(
        self, db_conn: asyncpg.Connection
    ) -> None:
        """A cohort with Cardeep GONE activity but ZERO DGT transfers (or vice
        versa) must still appear — never silently hidden by an inner join."""
        make = "__CARDEEP_TEST_DGT_ONESIDE__"
        month = "202602"
        try:
            async with db_conn.transaction():
                batch_id = await _seed_dgt_batch(db_conn, month=month)
                # Cardeep has GONE activity, DGT has NOTHING for this make.
                run_id = await vam_verified_run_id(db_conn)
                vul = await seed_vehicle(
                    db_conn, run_id, make=make.lower(), model="Whatever", fuel="gasolina",
                    year=2020, province_code="28", price=10000.0, status="gone",
                    first_seen=datetime(2026, 2, 10, tzinfo=timezone.utc),
                )
                eul = await entity_ulid_of(db_conn, vul)
                await seed_event(
                    db_conn, vehicle_ulid=vul, entity_ulid=eul, event_type="GONE",
                    old_value={"price": 10000.0}, new_value=None,
                    observed_at=datetime(2026, 2, 20, tzinfo=timezone.utc),
                )

                rows = await compute_corroboration(db_conn, batch_id, month)
                make_level = [r for r in rows if r["model"] is None and r["make"] == make.upper()]
                assert len(make_level) == 1
                assert make_level[0]["gone_count"] == 1
                assert make_level[0]["dgt_count"] == 0
                assert make_level[0]["ratio"] == 0.0

                raise _TestRollback("rollback one-side fixture")
        except _TestRollback:
            pass
