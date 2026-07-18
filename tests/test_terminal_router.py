"""Contract tests for /terminal/* (09-trading-terminal F2).

Fixtures are resolved LIVE against market_symbol at test time (not hardcoded row values) —
the F1 backfill's exact bucket contents can shift as new harvest days land, so these tests
assert STRUCTURE/CONTRACT (envelope shape, honest-degradation behaviour, C2 gating), never a
specific frozen number. Mirrors tests/test_market_router_m2.py's TestClient pattern.
"""
from __future__ import annotations

import asyncio
import os

import asyncpg
import pytest
from fastapi.testclient import TestClient

from pipeline.terminal.compute_buckets import OUTLIER_SIGMA_C4
from services.api.main import app
from services.api.routers.terminal import (
    MIN_ACTIVE_C2,
    _iso_week_key,
    _parse_symbol_key,
    _rows_to_bars,
)

_DSN = os.environ.get(
    "CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
)

# Same real vehicle used by tests/test_market_router_m2.py — proven to have a published M1
# row, which is all /terminal/{symbol}/rating/{ulid} needs (it delegates to compute_price_position).
KNOWN_VEHICLE_ULID = "01KTZ8N8VMC28V7YXG9RNRN9T8"


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


def _run_in_own_loop(coro_factory):
    """Run one coroutine in a DEDICATED, throwaway event loop rather than
    ``asyncio.get_event_loop()`` (which resolves to fragile, implicit per-thread "current
    loop" state — a real bug this session's own full-suite run caught: when this module runs
    in the SAME pytest session right after tests/test_terminal_compute_buckets.py or
    tests/test_terminal_infer_sales.py, both of which use pytest-asyncio's documented
    module-scoped ``event_loop`` fixture pattern, that fixture's teardown clears the thread's
    "current" event loop, so a later ``asyncio.get_event_loop()`` call here raised
    "RuntimeError: There is no current event loop in thread 'MainThread'" instead of
    resolving the fixture). A self-contained loop never depends on what a sibling module left
    behind, matching the same ``asyncio.new_event_loop()`` + ``loop.close()`` idiom those
    sibling modules already use for their own async fixtures."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro_factory())
    finally:
        loop.close()


@pytest.fixture(scope="module")
def real_active_symbol_key() -> str | None:
    """The symbol_key with the highest active_count in the live corpus, or None if F1's
    backfill has not populated any row yet (tests that need it are skipped, not faked)."""
    async def _fetch() -> str | None:
        conn = await asyncpg.connect(_DSN)
        try:
            row = await conn.fetchrow(
                "SELECT symbol_key FROM market_bucket_daily ORDER BY active_count DESC LIMIT 1"
            )
            return row["symbol_key"] if row else None
        finally:
            await conn.close()
    return _run_in_own_loop(_fetch)


@pytest.fixture(scope="module")
def known_vehicle_exists() -> bool:
    """KNOWN_VEHICLE_ULID is a REAL production vehicle_ulid (see module-level comment above)
    — the CI db-tests job's synthetic 25-row fixture (scripts/seed_ci_fixture.py) can never
    contain it, only the developer's live populated census can. Mirrors this same file's own
    real_active_symbol_key fixture: honest degradation (skip), never a fabricated stand-in
    ULID (project rule: never hardcode a fake "looks real" ID pretending to be production
    data)."""
    async def _fetch() -> bool:
        conn = await asyncpg.connect(_DSN)
        try:
            row = await conn.fetchval("SELECT 1 FROM vehicle WHERE vehicle_ulid = $1", KNOWN_VEHICLE_ULID)
            return row is not None
        finally:
            await conn.close()
    return _run_in_own_loop(_fetch)


class TestParseSymbolKey:
    def test_provincial_symbol_parses(self) -> None:
        assert _parse_symbol_key("BMW|Serie 3|28") == ("BMW", "Serie 3", "28")

    def test_national_symbol_parses_province_none(self) -> None:
        assert _parse_symbol_key("BMW|Serie 3|NAT") == ("BMW", "Serie 3", None)

    def test_malformed_key_raises(self) -> None:
        with pytest.raises(ValueError):
            _parse_symbol_key("not-a-valid-key")


class TestRowsToBars:
    def test_daily_mode_is_flat_ohlc_per_real_day(self) -> None:
        from datetime import date
        rows = [
            {"bucket_date": date(2026, 6, 12), "median_price": 20000.0, "new_count": 10},
            {"bucket_date": date(2026, 6, 13), "median_price": 21000.0, "new_count": 5},
        ]
        bars = _rows_to_bars(rows, daily=True)
        assert len(bars) == 2
        assert bars[0] == {"time": "2026-06-12", "open": 20000.0, "high": 20000.0, "low": 20000.0, "close": 20000.0, "volume": 10}

    def test_weekly_mode_aggregates_multiple_days_in_same_iso_week(self) -> None:
        from datetime import date
        # 2026-06-22 (Mon) and 2026-06-23 (Tue) are in the same ISO week.
        rows = [
            {"bucket_date": date(2026, 6, 22), "median_price": 20000.0, "new_count": 10},
            {"bucket_date": date(2026, 6, 23), "median_price": 22000.0, "new_count": 5},
        ]
        assert _iso_week_key(date(2026, 6, 22)) == _iso_week_key(date(2026, 6, 23))
        bars = _rows_to_bars(rows, daily=False)
        assert len(bars) == 1
        bar = bars[0]
        assert bar["open"] == 20000.0   # first day's median
        assert bar["close"] == 22000.0  # last day's median
        assert bar["high"] == 22000.0
        assert bar["low"] == 20000.0
        assert bar["volume"] == 15

    def test_null_median_price_day_is_skipped_not_zeroed(self) -> None:
        from datetime import date
        rows = [{"bucket_date": date(2026, 6, 12), "median_price": None, "new_count": 3}]
        assert _rows_to_bars(rows, daily=True) == []


class TestSymbolsSearch:
    def test_search_returns_envelope_shape(self, client: TestClient) -> None:
        r = client.get("/terminal/symbols", params={"q": "a"})
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert isinstance(body["data"], list)

    def test_search_requires_q_param(self, client: TestClient) -> None:
        r = client.get("/terminal/symbols")
        assert r.status_code == 422  # FastAPI validation error, q is required


class TestSymbolOhlc:
    def test_nonexistent_symbol_returns_404(self, client: TestClient) -> None:
        r = client.get("/terminal/__NOSUCH__|__NOSUCH__|NAT/ohlc")
        assert r.status_code == 404
        assert r.json()["ok"] is False

    def test_malformed_symbol_key_returns_400(self, client: TestClient) -> None:
        r = client.get("/terminal/not-a-valid-key/ohlc")
        assert r.status_code == 400

    def test_real_symbol_returns_bars_with_bar_shape(
        self, client: TestClient, real_active_symbol_key: str | None
    ) -> None:
        if real_active_symbol_key is None:
            pytest.skip("F1 backfill has not populated market_bucket_daily yet")
        r = client.get(f"/terminal/{real_active_symbol_key}/ohlc")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        for bar in body["data"]:
            assert set(bar.keys()) == {"time", "open", "high", "low", "close", "volume"}
        assert body["meta"]["symbol_key"] == real_active_symbol_key


class TestSymbolStats:
    def test_nonexistent_symbol_returns_404(self, client: TestClient) -> None:
        r = client.get("/terminal/__NOSUCH__|__NOSUCH__|NAT/stats")
        assert r.status_code == 404

    def test_real_symbol_stats_clears_c2_and_reports_censal_fields(
        self, client: TestClient, real_active_symbol_key: str | None
    ) -> None:
        if real_active_symbol_key is None:
            pytest.skip("F1 backfill has not populated market_bucket_daily yet")
        r = client.get(f"/terminal/{real_active_symbol_key}/stats")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["insufficient_sample"] is False
        assert data["active_count"] >= MIN_ACTIVE_C2
        assert "n_dealers" in data
        assert "price_pressure" in data
        assert data["price_pressure"]["window_days"] == 30
        assert "concentration_top5_pct" in data


class TestSymbolRating:
    def test_delegates_to_m2_and_adds_symbol_key(
        self, client: TestClient, known_vehicle_exists: bool
    ) -> None:
        if not known_vehicle_exists:
            pytest.skip(
                "KNOWN_VEHICLE_ULID is a real production vehicle (see module-level comment) "
                "not present in this DB — needs the live populated census, same category as "
                "tests/ci_local_only.txt section (1); the rest of this file self-seeds and "
                "stays CI-safe, see known_vehicle_exists fixture."
            )
        # Any syntactically valid symbol_key works — the rating computation itself
        # (compute_price_position) resolves the vehicle's OWN segment, ignoring the
        # symbol_key path param except to echo it back (see module docstring: this
        # endpoint is a thin wrapper, not a second comparable engine).
        r = client.get(f"/terminal/BMW|Serie 3|NAT/rating/{KNOWN_VEHICLE_ULID}")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["vehicle_ulid"] == KNOWN_VEHICLE_ULID
        assert data["symbol_key"] == "BMW|Serie 3|NAT"
        assert "position" in data

    def test_malformed_symbol_key_returns_400(self, client: TestClient) -> None:
        r = client.get(f"/terminal/bad-key/rating/{KNOWN_VEHICLE_ULID}")
        assert r.status_code == 400

    def test_nonexistent_vehicle_returns_404(self, client: TestClient) -> None:
        r = client.get("/terminal/BMW|Serie 3|NAT/rating/01NOSUCHVEHICLEULIDXXXXXXX")
        assert r.status_code == 404


class TestMethodology:
    def test_returns_c1_through_c8_documented(self, client: TestClient) -> None:
        r = client.get("/terminal/methodology")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["c4_outlier_exclusion"]["sigma_threshold"] == OUTLIER_SIGMA_C4
        assert "Manheim" in data["c4_outlier_exclusion"]["source"]
        for key in ("c1_symbol", "c2_min_sample", "c3_bar", "c5_rotation", "c6_price_pressure", "c7_deal_rating", "c8_censal"):
            assert key in data
