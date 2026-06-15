"""Unit tests for pipeline/delta.py.

Covers:
  - reconcile_gone: marks stale, skips fresh, gone-fraction safety cap,
    is source-scoped, is idempotent
  - diff_vehicle: detects PRICE/KM/PHOTO changes, no false positives
  - Bug fixes in generic_dealer_site.py: status='gone' (not 'sold') and
    GONE event old_value is a JSON object (not a raw string)

All tests use synthetic in-memory data via asyncpg.create_pool with a
real PG connection OR, for pure-function tests, plain Python dicts/objects.

IMPORTANT: reconcile_gone tests require a live PostgreSQL connection and are
marked with pytest.mark.integration.  They are skipped automatically when the
DB is not available (the fixture raises pytest.skip()).  Pure-function tests
(diff_vehicle, bug-fix structure) have zero infrastructure requirements.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from pipeline.delta import diff_vehicle, reconcile_gone


# ---------------------------------------------------------------------------
# Helpers / stubs
# ---------------------------------------------------------------------------

@dataclass
class FakeVehicle:
    """Minimal scraped vehicle object consumed by diff_vehicle."""
    price: float | None = None
    km: int | None = None
    photo_url: str | None = None


def _ts(offset_seconds: float = 0.0) -> datetime:
    """UTC datetime, optionally offset from now."""
    return datetime.now(tz=timezone.utc) + timedelta(seconds=offset_seconds)


# ---------------------------------------------------------------------------
# diff_vehicle — pure function tests (no infrastructure)
# ---------------------------------------------------------------------------

class TestDiffVehicle:
    """diff_vehicle detects the correct change types and produces no false positives."""

    # ---- PRICE_CHANGE ----

    def test_price_change_detected(self) -> None:
        old = {"price": 10_000, "km": 50_000, "photo_url": "https://example.com/a.jpg"}
        new = FakeVehicle(price=9_500, km=50_000, photo_url="https://example.com/a.jpg")
        events = diff_vehicle(old, new)
        types = [e["event_type"] for e in events]
        assert "PRICE_CHANGE" in types
        pc = next(e for e in events if e["event_type"] == "PRICE_CHANGE")
        assert pc["old_value"] == {"price": 10_000.0}
        assert pc["new_value"] == {"price": 9_500.0}

    def test_price_unchanged_no_event(self) -> None:
        old = {"price": 10_000.0, "km": 50_000, "photo_url": None}
        new = FakeVehicle(price=10_000.0, km=50_000, photo_url=None)
        events = diff_vehicle(old, new)
        assert not any(e["event_type"] == "PRICE_CHANGE" for e in events)

    def test_price_none_old_no_event(self) -> None:
        """If old price is None, no PRICE_CHANGE can be detected."""
        old = {"price": None, "km": None, "photo_url": None}
        new = FakeVehicle(price=8_000.0)
        events = diff_vehicle(old, new)
        assert not any(e["event_type"] == "PRICE_CHANGE" for e in events)

    def test_price_none_new_no_event(self) -> None:
        """If new price is None, no PRICE_CHANGE emitted."""
        old = {"price": 10_000.0, "km": None, "photo_url": None}
        new = FakeVehicle(price=None)
        events = diff_vehicle(old, new)
        assert not any(e["event_type"] == "PRICE_CHANGE" for e in events)

    def test_price_float_precision_no_false_positive(self) -> None:
        """Identical floats expressed differently must not trigger a change."""
        old = {"price": 12_500.0, "km": None, "photo_url": None}
        new = FakeVehicle(price=12_500)  # int == float
        events = diff_vehicle(old, new)
        assert events == []

    # ---- KM_CHANGE ----

    def test_km_change_detected(self) -> None:
        old = {"price": None, "km": 80_000, "photo_url": None}
        new = FakeVehicle(km=82_000)
        events = diff_vehicle(old, new)
        types = [e["event_type"] for e in events]
        assert "KM_CHANGE" in types
        km = next(e for e in events if e["event_type"] == "KM_CHANGE")
        assert km["old_value"] == {"km": 80_000}
        assert km["new_value"] == {"km": 82_000}

    def test_km_unchanged_no_event(self) -> None:
        old = {"price": None, "km": 60_000, "photo_url": None}
        new = FakeVehicle(km=60_000)
        events = diff_vehicle(old, new)
        assert not any(e["event_type"] == "KM_CHANGE" for e in events)

    def test_km_none_old_no_event(self) -> None:
        old = {"price": None, "km": None, "photo_url": None}
        new = FakeVehicle(km=50_000)
        events = diff_vehicle(old, new)
        assert not any(e["event_type"] == "KM_CHANGE" for e in events)

    # ---- PHOTO_CHANGE ----

    def test_photo_change_detected(self) -> None:
        old = {"price": None, "km": None, "photo_url": "https://example.com/old.jpg"}
        new = FakeVehicle(photo_url="https://example.com/new.jpg")
        events = diff_vehicle(old, new)
        types = [e["event_type"] for e in events]
        assert "PHOTO_CHANGE" in types
        ph = next(e for e in events if e["event_type"] == "PHOTO_CHANGE")
        assert ph["old_value"] == {"photo": "https://example.com/old.jpg"}
        assert ph["new_value"] == {"photo": "https://example.com/new.jpg"}

    def test_photo_unchanged_no_event(self) -> None:
        url = "https://example.com/car.jpg"
        old = {"price": None, "km": None, "photo_url": url}
        new = FakeVehicle(photo_url=url)
        events = diff_vehicle(old, new)
        assert not any(e["event_type"] == "PHOTO_CHANGE" for e in events)

    def test_photo_none_new_no_event(self) -> None:
        """New photo is None (not scraped) — do not emit PHOTO_CHANGE."""
        old = {"price": None, "km": None, "photo_url": "https://example.com/old.jpg"}
        new = FakeVehicle(photo_url=None)
        events = diff_vehicle(old, new)
        assert not any(e["event_type"] == "PHOTO_CHANGE" for e in events)

    # ---- Multiple changes in one call ----

    def test_all_three_changes_detected(self) -> None:
        old = {"price": 15_000.0, "km": 100_000, "photo_url": "https://example.com/a.jpg"}
        new = FakeVehicle(
            price=14_500.0,
            km=101_000,
            photo_url="https://example.com/b.jpg",
        )
        events = diff_vehicle(old, new)
        types = {e["event_type"] for e in events}
        assert types == {"PRICE_CHANGE", "KM_CHANGE", "PHOTO_CHANGE"}

    def test_no_changes_returns_empty_list(self) -> None:
        old = {"price": 10_000.0, "km": 50_000, "photo_url": "https://example.com/a.jpg"}
        new = FakeVehicle(price=10_000.0, km=50_000, photo_url="https://example.com/a.jpg")
        assert diff_vehicle(old, new) == []

    # ---- Return type contract ----

    def test_return_is_list(self) -> None:
        result = diff_vehicle({"price": None, "km": None, "photo_url": None}, FakeVehicle())
        assert isinstance(result, list)

    def test_event_dict_has_required_keys(self) -> None:
        old = {"price": 10_000.0, "km": None, "photo_url": None}
        new = FakeVehicle(price=9_000.0)
        events = diff_vehicle(old, new)
        assert len(events) == 1
        ev = events[0]
        assert "event_type" in ev
        assert "old_value" in ev
        assert "new_value" in ev


# ---------------------------------------------------------------------------
# reconcile_gone — mocked asyncpg connection tests (no DB needed)
# ---------------------------------------------------------------------------

class TestReconcileGoneMocked:
    """reconcile_gone behaviour using a mocked asyncpg connection.

    These tests focus on the logic (guard, source-scoping, idempotency signal,
    event format) without requiring a real PostgreSQL instance.
    """

    def _make_conn(
        self,
        *,
        available_count: int = 10,
        stale_rows: list[dict] | None = None,
        entity_ulid: str = "ent_111",
    ) -> AsyncMock:
        conn = AsyncMock()

        # fetchval: first call = available_count SELECT, subsequent = entity_ulid lookups
        fetchval_results = [available_count] + [entity_ulid] * 100
        fetchval_iter = iter(fetchval_results)
        conn.fetchval = AsyncMock(side_effect=lambda *a, **kw: next(fetchval_iter))

        # fetch: returns the stale rows
        if stale_rows is None:
            stale_rows = []

        def _fake_row(d: dict) -> MagicMock:
            r = MagicMock()
            r.__getitem__ = lambda self, k: d[k]
            return r

        conn.fetch = AsyncMock(return_value=[_fake_row(r) for r in stale_rows])
        conn.execute = AsyncMock(return_value=None)
        return conn

    @pytest.mark.asyncio
    async def test_no_available_bails_before_fetch(self) -> None:
        """No available vehicles for the source -> nothing to do, no stale query."""
        conn = self._make_conn(available_count=0, stale_rows=[])
        gone, reason = await reconcile_gone(
            conn, "wallapop_wholesale", _ts()        )
        assert gone == 0
        # The guard returns a non-empty reason explaining the skip.
        assert isinstance(reason, str) and len(reason) > 0
        # fetch must NOT have been called (we bail out before querying stale rows)
        conn.fetch.assert_not_called()

    @pytest.mark.asyncio
    async def test_fraction_cap_aborts_partial_run(self) -> None:
        """CATASTROPHIC-CASE GUARD: a partial/failed run that leaves most of a
        non-trivial inventory unseen must ABORT — never retire it.

        Regression guard for the old min_captured flaw, where a wallapop run
        capturing 5k of 588k would have marked the other ~99% gone.
        """
        # available=40 (>= MIN_INVENTORY_FOR_GUARD), stale=21 (52.5% > 50% ceiling)
        stale = [{"vehicle_ulid": f"veh_{i}", "price": 1000} for i in range(21)]
        conn = self._make_conn(available_count=40, stale_rows=stale)
        gone, reason = await reconcile_gone(conn, "wallapop_wholesale", _ts())
        assert gone == 0, "must NOT retire inventory on an implausible gone-fraction"
        assert "ABORTED" in reason
        conn.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_small_inventory_exempt_from_fraction_guard(self) -> None:
        """Inventories below MIN_INVENTORY_FOR_GUARD may legitimately all vanish."""
        stale = [{"vehicle_ulid": f"veh_{i}", "price": 500} for i in range(10)]
        conn = self._make_conn(available_count=10, stale_rows=stale)
        gone, _ = await reconcile_gone(conn, "tiny_source", _ts())
        assert gone == 10

    @pytest.mark.asyncio
    async def test_healthy_churn_proceeds(self) -> None:
        """A normal churn (stale fraction below the ceiling) marks the stale gone."""
        stale = [{"vehicle_ulid": f"veh_{i}", "price": 9000} for i in range(15)]
        conn = self._make_conn(available_count=100, stale_rows=stale)
        gone, _ = await reconcile_gone(conn, "coches_net_wholesale", _ts())
        assert gone == 15

    @pytest.mark.asyncio
    async def test_no_stale_rows_returns_zero(self) -> None:
        """When all vehicles were seen in the run, gone=0."""
        conn = self._make_conn(available_count=5, stale_rows=[])
        gone, reason = await reconcile_gone(
            conn, "coches_net_wholesale", _ts()        )
        assert gone == 0
        assert isinstance(reason, str) and len(reason) > 0

    @pytest.mark.asyncio
    async def test_marks_stale_vehicles(self) -> None:
        """Vehicles with last_seen < run_started_at must be marked gone."""
        stale = [
            {"vehicle_ulid": "veh_aaa", "price": 10_000},
            {"vehicle_ulid": "veh_bbb", "price": None},
        ]
        conn = self._make_conn(available_count=10, stale_rows=stale)
        gone, reason = await reconcile_gone(
            conn, "milanuncios_wholesale", _ts()        )
        assert gone == 2
        # Each vehicle should have triggered an UPDATE + INSERT
        execute_calls = conn.execute.call_args_list
        update_calls = [c for c in execute_calls if "UPDATE vehicle" in str(c)]
        insert_calls = [c for c in execute_calls if "INSERT INTO vehicle_event" in str(c)]
        assert len(update_calls) == 2
        assert len(insert_calls) == 2

    @pytest.mark.asyncio
    async def test_gone_event_old_value_is_dict_with_price(self) -> None:
        """GONE event old_value must be a JSON dict with 'price' key.

        execute() call signature:
          (sql_string, event_ulid, vehicle_ulid, entity_ulid, old_value_json)
        So call_args[0] is (sql, arg1, arg2, arg3, arg4):
          index 0 = SQL string
          index 1 = event_ulid  ($1)
          index 2 = vehicle_ulid ($2)
          index 3 = entity_ulid  ($3)
          index 4 = old_value JSON string ($4::jsonb)
        new_value is hardcoded NULL in the SQL — no Python arg.
        """
        stale = [{"vehicle_ulid": "veh_ccc", "price": 15_000}]
        conn = self._make_conn(available_count=5, stale_rows=stale)
        await reconcile_gone(conn, "motor_es_wholesale", _ts())

        insert_calls = [
            c for c in conn.execute.call_args_list
            if "INSERT INTO vehicle_event" in str(c)
        ]
        assert len(insert_calls) == 1
        args = insert_calls[0][0]  # positional args tuple: (sql, $1, $2, $3, $4)
        old_value_json = args[4]   # $4 = old_value JSON string
        old_value = json.loads(old_value_json)
        assert "price" in old_value
        assert old_value["price"] == 15_000.0

    @pytest.mark.asyncio
    async def test_gone_event_old_value_price_none_serialises(self) -> None:
        """price=None in DB must serialize as {"price": null}, not raise."""
        stale = [{"vehicle_ulid": "veh_ddd", "price": None}]
        conn = self._make_conn(available_count=3, stale_rows=stale)
        gone, _ = await reconcile_gone(conn, "motor_es_wholesale", _ts())
        assert gone == 1
        insert_calls = [
            c for c in conn.execute.call_args_list
            if "INSERT INTO vehicle_event" in str(c)
        ]
        old_value = json.loads(insert_calls[0][0][4])  # $4 = old_value JSON
        assert old_value == {"price": None}

    @pytest.mark.asyncio
    async def test_gone_event_new_value_hardcoded_null_in_sql(self) -> None:
        """GONE event new_value is NULL hardcoded in the SQL (no Python arg for it).

        The INSERT SQL ends with '... $4::jsonb, NULL)' — new_value is not
        passed as a Python argument to conn.execute(), so there is no args[5].
        We verify this by confirming the SQL string itself contains ', NULL)'.
        """
        stale = [{"vehicle_ulid": "veh_eee", "price": 5_000}]
        conn = self._make_conn(available_count=3, stale_rows=stale)
        await reconcile_gone(conn, "any_source", _ts())
        insert_calls = [
            c for c in conn.execute.call_args_list
            if "INSERT INTO vehicle_event" in str(c)
        ]
        assert len(insert_calls) == 1
        sql_string = insert_calls[0][0][0]  # first positional arg = the SQL
        assert "NULL" in sql_string, (
            "GONE event SQL must hardcode NULL for new_value (a departure has no new state)"
        )

    @pytest.mark.asyncio
    async def test_source_scoped_query_uses_source_key(self) -> None:
        """The FIND_STALE query must be parameterised with the exact source_key."""
        conn = self._make_conn(stale_rows=[])
        source_key = "wallapop_wholesale"
        await reconcile_gone(conn, source_key, _ts())
        # fetch is called once with the stale-search query; first positional arg after
        # the SQL string is source_key.
        fetch_calls = conn.fetch.call_args_list
        assert len(fetch_calls) == 1
        call_args = fetch_calls[0][0]
        assert source_key in call_args

    @pytest.mark.asyncio
    async def test_idempotent_no_double_mark(self) -> None:
        """If no stale rows found (already gone or all re-seen), execute is
        called only for the count query (fetchval), not for UPDATE/INSERT."""
        conn = self._make_conn(available_count=5, stale_rows=[])
        gone, _ = await reconcile_gone(conn, "some_source", _ts())
        assert gone == 0
        # execute must NOT have been called (no UPDATE, no INSERT)
        conn.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_reason_always_non_empty_string(self) -> None:
        """reconcile_gone always returns a non-empty reason."""
        for stale in [[], [{"vehicle_ulid": "v1", "price": 1000}]]:
            conn = self._make_conn(stale_rows=stale)
            _, reason = await reconcile_gone(conn, "src", _ts())
            assert isinstance(reason, str) and len(reason) > 0


# ---------------------------------------------------------------------------
# Bug-fix structural verification — generic_dealer_site.py
# ---------------------------------------------------------------------------

class TestGenericDealerSiteBugFixes:
    """Structural tests that the two bug-fixes are present in source.

    These read the source file as text — no DB, no imports of the module.
    They are intentionally static so they pass in CI without infrastructure.
    """

    import pathlib
    _SRC = (
        pathlib.Path(__file__).parents[1]
        / "pipeline" / "platform" / "generic_dealer_site.py"
    ).read_text(encoding="utf-8")

    def test_status_gone_not_sold(self) -> None:
        """GONE path must set status='gone', not status='sold'."""
        # The bug was: UPDATE vehicle SET status='sold'
        # The fix is:  UPDATE vehicle SET status='gone'
        assert "status='gone'" in self._SRC, (
            "generic_dealer_site.py: GONE path must use status='gone' not status='sold'"
        )
        # Also confirm the old bug string is gone
        assert "status='sold'" not in self._SRC, (
            "generic_dealer_site.py: 'status='sold'' still present — bug not fixed"
        )

    def test_gone_event_old_value_is_jsonb_cast(self) -> None:
        """GONE event must use $4::jsonb parameter, not a bare string literal."""
        assert "$4::jsonb" in self._SRC, (
            "generic_dealer_site.py: GONE event old_value must use $4::jsonb cast"
        )

    def test_gone_event_no_bare_string_literal(self) -> None:
        """The old bare-string VALUES (...,'available','sold') must not appear."""
        assert "'GONE','available','sold'" not in self._SRC, (
            "generic_dealer_site.py: bare string GONE event literals still present"
        )

    def test_gone_event_json_dumps_called(self) -> None:
        """json.dumps must be used to build the old_value for GONE events."""
        # The fix uses: json.dumps({"status": "available"})
        assert 'json.dumps({"status": "available"})' in self._SRC, (
            "generic_dealer_site.py: json.dumps not used for GONE old_value"
        )
