"""P2/Q9 (green-review): harvest_dealer must ALERT on every failure path with the exact origin,
never crash silently. Unexpected bugs are alerted AND re-raised (visible, not swallowed).
Pure-mock — no live DB, no real scrape, no filesystem writes.
"""
from __future__ import annotations

import asyncio
import unittest.mock as mock

import pytest

from pipeline import harvest_dealer


def test_scrape_exception_fires_dealer_alert_and_returns():
    # P2: a scrape exception used to crash the process before any DB/alert. Now it fires a
    # dealer-specific alert and returns (the dealer is skipped, monitoring sees it).
    conn = mock.AsyncMock()
    with (
        mock.patch("asyncpg.connect", new=mock.AsyncMock(return_value=conn)),
        mock.patch.object(harvest_dealer, "scrape_dealer", side_effect=RuntimeError("403 blocked")),
        mock.patch("pipeline.ops.health.fire_alert", new=mock.AsyncMock()) as fa,
    ):
        asyncio.run(harvest_dealer.run("badslug"))   # must NOT raise
    fa.assert_awaited_once()
    origin = fa.call_args.args[1]
    assert "scrape" in origin and "badslug" in origin
    assert fa.call_args.kwargs.get("severity") == "error"


def test_ingest_error_fires_alert_and_returns():
    # Q9: an ingest-level error (bad province / no dealer) was print-only. Now it alerts.
    conn = mock.AsyncMock()
    harvest_obj = mock.MagicMock()
    harvest_obj.dealer = mock.MagicMock()   # truthy → past the no-dealer guard
    harvest_obj.vehicles = []
    with (
        mock.patch("asyncpg.connect", new=mock.AsyncMock(return_value=conn)),
        mock.patch.object(harvest_dealer, "scrape_dealer", return_value=harvest_obj),
        mock.patch("pathlib.Path.mkdir"), mock.patch("pathlib.Path.write_text"),
        mock.patch.object(harvest_dealer.GeoResolver, "load",
                          new=mock.AsyncMock(return_value=mock.MagicMock())),
        mock.patch.object(harvest_dealer, "ingest_dealer",
                          new=mock.AsyncMock(return_value={"error": "province 99 out of Spain range"})),
        mock.patch("pipeline.ops.health.fire_alert", new=mock.AsyncMock()) as fa,
    ):
        asyncio.run(harvest_dealer.run("someslug"))
    fa.assert_awaited_once()
    assert "ingest" in fa.call_args.args[1]


def test_unexpected_error_alerts_then_reraises():
    # A bug (not a known operational outcome) must be ALERTED then RE-RAISED — visible AND not
    # swallowed by the catch-all.
    conn = mock.AsyncMock()
    harvest_obj = mock.MagicMock()
    harvest_obj.dealer = mock.MagicMock()
    harvest_obj.vehicles = []
    with (
        mock.patch("asyncpg.connect", new=mock.AsyncMock(return_value=conn)),
        mock.patch.object(harvest_dealer, "scrape_dealer", return_value=harvest_obj),
        mock.patch("pathlib.Path.mkdir"), mock.patch("pathlib.Path.write_text"),
        mock.patch.object(harvest_dealer.GeoResolver, "load",
                          new=mock.AsyncMock(side_effect=KeyError("boom"))),
        mock.patch("pipeline.ops.health.fire_alert", new=mock.AsyncMock()) as fa,
    ):
        with pytest.raises(KeyError):
            asyncio.run(harvest_dealer.run("someslug"))
    fa.assert_awaited_once()
    assert "harvest" in fa.call_args.args[1]
