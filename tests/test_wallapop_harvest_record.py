"""CRIT (green-review connectors): wallapop harvest() must RECORD a setup/fatal exception via
record_run(ok=False) and re-raise — never skip record_run and go monitoring-dark. Pure-mock,
no live DB / network.
"""
from __future__ import annotations

import asyncio
import unittest.mock as mock

import pytest

from pipeline.platform import wallapop_wholesale as wp


def test_harvest_records_failure_on_setup_exception():
    conn = mock.AsyncMock()
    with (
        mock.patch("asyncpg.connect", new=mock.AsyncMock(return_value=conn)),
        mock.patch.object(wp, "is_open", new=mock.AsyncMock(return_value=False)),  # breaker closed
        mock.patch.object(wp, "WallapopFetcher", new=mock.MagicMock()),
        mock.patch.object(wp, "governor", new=mock.MagicMock()),
        mock.patch.object(wp.GeoResolver, "load",
                          new=mock.AsyncMock(side_effect=RuntimeError("geo_province unreachable"))),
        mock.patch.object(wp, "record_run", new=mock.AsyncMock()) as rr,
        mock.patch.object(wp, "auto_repair", new=mock.AsyncMock()),
    ):
        with pytest.raises(RuntimeError):
            asyncio.run(wp.harvest())
    # The setup exception was recorded as a failure (not swallowed, not skipped).
    rr.assert_awaited_once()
    assert rr.call_args.kwargs.get("ok") is False
    assert "fatal" in (rr.call_args.kwargs.get("error") or "").lower()
