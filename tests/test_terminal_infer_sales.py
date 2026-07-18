"""Integration tests for pipeline/terminal/infer_sales.py (09-trading-terminal Fase 4).

SAFETY CONTRACT (mirrors tests/test_terminal_compute_buckets.py): every DB-touching test runs
inside a transaction that is ALWAYS rolled back. Synthetic makes/symbols are distinctively
prefixed so they cannot collide with real inventory.
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta, timezone

import asyncpg
import pytest
import pytest_asyncio

from pipeline.ids import ulid
from pipeline.terminal.infer_sales import (
    CONFIDENCE_DELISTED,
    CONFIDENCE_PROBABLE_SALE_NO_SIGNAL,
    CONFIDENCE_PROBABLE_SALE_WITH_SIGNAL,
    CONFIDENCE_RELISTED,
    run,
)
from tests.market_test_helpers import entity_ulid_of, seed_vehicle, vam_verified_run_id

_DSN = os.environ.get(
    "CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
)

_MAKE = "__CARDEEP_TERM_TEST_INFER__"


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


async def _seed_symbol_and_median(conn: asyncpg.Connection, *, make: str, model: str, province: str, median_price: float) -> str:
    symbol_key = f"{make}|{model}|{province}"
    await conn.execute(
        """
        INSERT INTO market_symbol (symbol_key, make, model, province_code, level, is_active, first_bucket, last_bucket)
        VALUES ($1, $2, $3, $4, 'model_prov', TRUE, CURRENT_DATE, CURRENT_DATE)
        ON CONFLICT (symbol_key) DO NOTHING
        """,
        symbol_key, make, model, province,
    )
    await conn.execute(
        """
        INSERT INTO market_bucket_daily
            (symbol_key, bucket_date, active_count, median_price, new_count, gone_count, n_events, computed_at)
        VALUES ($1, CURRENT_DATE, 30, $2, 5, 5, 10, now())
        ON CONFLICT (symbol_key, bucket_date) DO UPDATE SET median_price = EXCLUDED.median_price
        """,
        symbol_key, median_price,
    )
    return symbol_key


@pytest.mark.integration
class TestInferSalesPriceBand:
    @pytest.mark.asyncio
    async def test_gone_vehicle_in_price_band_is_probable_sale(self, db_conn: asyncpg.Connection) -> None:
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                symbol_key = await _seed_symbol_and_median(
                    db_conn, make=_MAKE, model="InBand", province="28", median_price=20000.0,
                )
                vulid = await seed_vehicle(
                    db_conn, run_id, make=_MAKE, model="InBand", fuel="gasolina", year=2020,
                    province_code="28", price=19000.0, status="gone",
                )
                summary = await run(db_conn)
                row = await db_conn.fetchrow(
                    "SELECT inference, confidence, symbol_key FROM market_sale_inference WHERE vehicle_ulid = $1", vulid
                )
                assert row is not None
                assert row["inference"] == "probable_sale"
                assert row["symbol_key"] == symbol_key
                # This corpus's lifetime_link engine has 0 edges (verified live 2026-07-18,
                # migrations/0090 header) — confidence must reflect the LOW-signal cap unless a
                # synthetic edge was seeded (it wasn't in this test).
                if not summary["engine_has_signal"]:
                    assert row["confidence"] == pytest.approx(CONFIDENCE_PROBABLE_SALE_NO_SIGNAL)
                else:
                    assert row["confidence"] == pytest.approx(CONFIDENCE_PROBABLE_SALE_WITH_SIGNAL)
                raise _TestRollback()
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_gone_vehicle_far_outside_band_is_delisted(self, db_conn: asyncpg.Connection) -> None:
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                await _seed_symbol_and_median(
                    db_conn, make=_MAKE, model="OutBand", province="28", median_price=20000.0,
                )
                vulid = await seed_vehicle(
                    db_conn, run_id, make=_MAKE, model="OutBand", fuel="gasolina", year=2020,
                    province_code="28", price=5000.0, status="gone",  # ratio 0.25, way below 0.75 floor
                )
                await run(db_conn)
                row = await db_conn.fetchrow(
                    "SELECT inference, confidence FROM market_sale_inference WHERE vehicle_ulid = $1", vulid
                )
                assert row is not None
                assert row["inference"] == "delisted"
                assert row["confidence"] == pytest.approx(CONFIDENCE_DELISTED)
                raise _TestRollback()
        except _TestRollback:
            pass


@pytest.mark.integration
class TestInferSalesLifetimeLinkEdge:
    @pytest.mark.asyncio
    async def test_vehicle_with_lifetime_link_edge_is_relisted(self, db_conn: asyncpg.Connection) -> None:
        """Seeds a SYNTHETIC vam_verified=TRUE lifetime_link_run + edge so v_vehicle_lifetime
        (which filters on the latest vam_verified run) picks it up — proves the 'relisted' path
        works even though the REAL corpus has 0 edges today (migrations/0090 header)."""
        try:
            async with db_conn.transaction():
                run_id = await vam_verified_run_id(db_conn)
                await _seed_symbol_and_median(
                    db_conn, make=_MAKE, model="Relisted", province="28", median_price=20000.0,
                )
                vulid_from = await seed_vehicle(
                    db_conn, run_id, make=_MAKE, model="Relisted", fuel="gasolina", year=2020,
                    province_code="28", price=19500.0, status="gone",
                )
                vulid_to = await seed_vehicle(
                    db_conn, run_id, make=_MAKE, model="Relisted", fuel="gasolina", year=2020,
                    province_code="08", price=19000.0, status="available",
                )
                synthetic_run_id = f"__test_lifetime_run_{ulid()}__"
                await db_conn.execute(
                    """
                    INSERT INTO lifetime_link_run
                        (run_id, resolver, resolver_version, scope, blocking_rules, n_in, n_chains, n_linked, vam_verified)
                    VALUES ($1, 'test', '0.0.0', 'test', '[]'::jsonb, 2, 1, 1, TRUE)
                    """,
                    synthetic_run_id,
                )
                await db_conn.execute(
                    """
                    INSERT INTO lifetime_link
                        (run_id, vehicle_ulid_from, vehicle_ulid_to, match_signal, match_probability, evidence)
                    VALUES ($1, $2, $3, 'vin_ref', 0.92, '{}'::jsonb)
                    """,
                    synthetic_run_id, vulid_from, vulid_to,
                )

                summary = await run(db_conn)
                assert summary["engine_has_signal"] is True

                row = await db_conn.fetchrow(
                    "SELECT inference, confidence, evidence FROM market_sale_inference WHERE vehicle_ulid = $1", vulid_from
                )
                assert row is not None
                assert row["inference"] == "relisted"
                assert row["confidence"] == pytest.approx(CONFIDENCE_RELISTED)
                # This test's plain asyncpg.connect() has no jsonb type codec registered (unlike
                # services/api/main.py's pool, which decodes jsonb via _init_connection) — evidence
                # comes back as a raw JSON string here, not a dict. json.loads it explicitly rather
                # than silently getting a TypeError on ["key"] indexing into a str (a real bug this
                # session's own test run caught on first execution).
                import json
                evidence = json.loads(row["evidence"])
                assert evidence["lifetime_link_edge_found"] is True
                raise _TestRollback()
        except _TestRollback:
            pass
