"""H9 (green-review): prosecute_pending must ABORT on a connection-level error, not swallow it.

The loop's bare `except Exception` previously caught asyncpg.InterfaceError /
PostgresConnectionError too — so a dropped connection mid-batch ticked 'errors' and continued
with a DEAD connection, failing every remaining claim silently. The fix re-raises
connection-level errors (aborting the batch) while still swallowing genuine per-claim errors.

Pure-mock (no live DB) → always runs, deterministic.
"""
from __future__ import annotations

import asyncio
import unittest.mock as mock

import asyncpg
import pytest

from pipeline.inquisition import prosecutor


def test_prosecute_pending_reraises_connection_error():
    conn = mock.AsyncMock()
    conn.fetch = mock.AsyncMock(return_value=[{"claim_id": "c1"}, {"claim_id": "c2"}])
    with mock.patch.object(
        prosecutor, "prosecute_claim",
        new=mock.AsyncMock(side_effect=asyncpg.InterfaceError("connection is closed")),
    ):
        with pytest.raises(asyncpg.InterfaceError):
            asyncio.run(prosecutor.prosecute_pending(conn, limit=10))


def test_prosecute_pending_reraises_postgres_connection_error():
    conn = mock.AsyncMock()
    conn.fetch = mock.AsyncMock(return_value=[{"claim_id": "c1"}])
    with mock.patch.object(
        prosecutor, "prosecute_claim",
        new=mock.AsyncMock(side_effect=asyncpg.exceptions.ConnectionDoesNotExistError("gone")),
    ):
        with pytest.raises(asyncpg.PostgresConnectionError):
            asyncio.run(prosecutor.prosecute_pending(conn, limit=10))


def test_prosecute_pending_swallows_per_claim_error_and_continues():
    # A NON-connection error stays per-claim: counted in 'errors', the loop continues to the end.
    conn = mock.AsyncMock()
    conn.fetch = mock.AsyncMock(return_value=[{"claim_id": "c1"}, {"claim_id": "c2"}])
    with mock.patch.object(
        prosecutor, "prosecute_claim",
        new=mock.AsyncMock(side_effect=ValueError("bad claim data")),
    ):
        out = asyncio.run(prosecutor.prosecute_pending(conn, limit=10))
    assert out["errors"] == 2  # both claims errored, the batch did NOT abort
