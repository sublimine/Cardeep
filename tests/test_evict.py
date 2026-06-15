"""Tests for pipeline/evict.py — BORRAR/DELETE stage.

SAFETY CONTRACT FOR THIS TEST SUITE
-------------------------------------
- ALL DB tests run inside a ROLLED-BACK transaction. No real data is deleted.
  Each test that touches the DB seizes a transaction savepoint and rolls it back
  by raising _TestRollback, leaving the real DB untouched.
- Raw-file tests use tmp_path (pytest fixture): synthetic files only.
  The real data/ directory under the repo root is NEVER touched.
- The --apply path is exercised against synthetic rows seeded inside a
  rolled-back transaction, so no real rows are affected.

Test coverage:
  1. Gate 1 — each failure mode (TRUSTWORTHY exists / no death evidence)
  2. Gate 2 — recipe missing / not committed / committed (mocked git)
  3. Gate 3 — avail>0 / g4_served=True / OPEN gestion / all clear
  4. check_preconditions — gate1 blocks / gate3 blocks
  5. evict_dealer dry_run=True — returns plan, calls no execute
  6. evict_dealer failing gate — returns without writes
  7. evict_dealer apply, all gates green (synthetic, rolled-back):
       entity.status='evicted', vehicles deleted, audit/ledger rows written
  8. audit_eviction immutability — UPDATE/DELETE raises 'append-only'
  9. Raw-file eviction — below/above threshold, other dealer untouched
"""
from __future__ import annotations

import asyncio
import os
import shutil
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import asyncpg
import pytest
import pytest_asyncio

from pipeline.evict import (
    DISK_EVICT_THRESHOLD_PCT,
    _DATA_DIR,
    _REPO_ROOT,
    _check_gate1,
    _check_gate2,
    _check_gate3,
    _evict_raw_files,
    check_preconditions,
    evict_dealer,
)

# ---------------------------------------------------------------------------
# DSN (same as migrate.py / evict.py)
# ---------------------------------------------------------------------------

_DSN = os.environ.get(
    "CARDEEP_DSN",
    "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep",
)

# Synthetic dealer identifiers — all must pass CHECK constraints:
#   cdp_code: ^CDP-ES-[0-9]{2}-[0-9A-HJKMNP-TV-Z]{8}$  (no I, L, O, U)
#   entity_ulid: ^[0-9A-HJKMNP-TV-Z]{26}$
#
# Crockford base32 alphabet (no I, L, O, U):
#   0123456789ABCDEFGHJKMNPQRSTVWXYZ

_SYNTH_CDP = "CDP-ES-28-SYNT0001"          # 'SYNT0001' — all valid chars
_SYNTH_CDP_2 = "CDP-ES-28-SYNT0002"
_SYNTH_ULID = "01TESTHDR1Q3E0D3X60P8W31TQ"  # 26 chars, valid Crockford alphabet

# Vehicles use real ULID format too
_SYNTH_VH_ULID_0 = "01TESTVH0000000000000000V0"
_SYNTH_VH_ULID_1 = "01TESTVH0000000000000000V1"


# ---------------------------------------------------------------------------
# Sentinel exception for rolling back test transactions
# ---------------------------------------------------------------------------

class _TestRollback(Exception):
    """Raised inside a rolled-back transaction to undo all test writes."""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def event_loop():
    """Module-scoped event loop for asyncio tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_conn():
    """Real asyncpg connection. Function-scoped (fresh per test)."""
    conn = await asyncpg.connect(_DSN)
    yield conn
    await conn.close()


# ---------------------------------------------------------------------------
# 1. Gate 1 — each failure mode (mocked conn)
# ---------------------------------------------------------------------------

class TestGate1:

    @pytest.mark.asyncio
    async def test_gate1_fails_when_trustworthy_exists(self) -> None:
        """Gate 1 fails when an active TRUSTWORTHY verdict exists."""
        conn = AsyncMock()
        # First fetchval: has_trustworthy=True; second: has_death_evidence=True
        conn.fetchval = AsyncMock(side_effect=[True, True])
        passed, reasons = await _check_gate1(conn, "CDP-ES-28-7Q2K9ABX")
        assert not passed
        assert any("TRUSTWORTHY" in r for r in reasons)

    @pytest.mark.asyncio
    async def test_gate1_fails_when_no_death_evidence(self) -> None:
        """Gate 1 fails when no REFUTED/UNVERIFIED verdict exists."""
        conn = AsyncMock()
        conn.fetchval = AsyncMock(side_effect=[False, False])
        passed, reasons = await _check_gate1(conn, "CDP-ES-28-7Q2K9ABX")
        assert not passed
        assert any("REFUTED" in r or "death" in r for r in reasons)

    @pytest.mark.asyncio
    async def test_gate1_passes_when_clean(self) -> None:
        """Gate 1 passes: no active TRUSTWORTHY, has death evidence."""
        conn = AsyncMock()
        conn.fetchval = AsyncMock(side_effect=[False, True])
        passed, reasons = await _check_gate1(conn, "CDP-ES-28-7Q2K9ABX")
        assert passed
        assert reasons == []


# ---------------------------------------------------------------------------
# 2. Gate 2 — recipe git check (mocked _resolve_recipe_path)
# ---------------------------------------------------------------------------

class TestGate2:
    """Gate 2 patches pipeline.evict._resolve_recipe_path and
    pipeline.evict._check_g3_git_subsignal (the imported references)."""

    @pytest.mark.asyncio
    async def test_gate2_fails_when_no_recipe_and_not_connector(self) -> None:
        """No recipe.yaml on disk AND recipe_kind != 'connector' → fail (no preserved recipe)."""
        conn = AsyncMock()
        conn.fetchval = AsyncMock(return_value="none")
        with patch("pipeline.evict._resolve_recipe_path", return_value=None):
            passed, reasons = await _check_gate2(conn, "CDP-ES-28-7Q2K9ABX")
        assert not passed
        assert any("no preserved recipe" in r for r in reasons)

    @pytest.mark.asyncio
    async def test_gate2_fails_when_recipe_not_committed_and_not_connector(self, tmp_path: Path) -> None:
        """recipe.yaml present but not at HEAD AND not connector-covered → fail."""
        fake_recipe = tmp_path / "recipe.yaml"
        fake_recipe.write_text("version: 1\n")
        conn = AsyncMock()
        conn.fetchval = AsyncMock(return_value="none")
        with (
            patch("pipeline.evict._resolve_recipe_path", return_value=fake_recipe),
            patch("pipeline.evict._check_g3_git_subsignal",
                  return_value=(None, "git_subsignal:recipe_not_committed_at_HEAD")),
        ):
            passed, reasons = await _check_gate2(conn, "CDP-ES-28-7Q2K9ABX")
        assert not passed

    @pytest.mark.asyncio
    async def test_gate2_passes_when_recipe_committed(self, tmp_path: Path) -> None:
        """Gate 2 passes when per_dealer recipe.yaml is confirmed at git HEAD."""
        fake_recipe = tmp_path / "recipe.yaml"
        fake_recipe.write_text("version: 1\n")
        conn = AsyncMock()
        conn.fetchval = AsyncMock(return_value="none")  # not reached (returns at git check)
        with (
            patch("pipeline.evict._resolve_recipe_path", return_value=fake_recipe),
            patch("pipeline.evict._check_g3_git_subsignal",
                  return_value=("abc123def456", "git_tracked_and_committed")),
        ):
            passed, reasons = await _check_gate2(conn, "CDP-ES-28-7Q2K9ABX")
        assert passed
        assert reasons == []

    @pytest.mark.asyncio
    async def test_gate2_passes_for_connector_coverage(self) -> None:
        """No per_dealer recipe.yaml, but recipe_kind='connector' → the committed connector
        module IS the preserved recipe → Gate 2 passes (the ~98.4% connector-covered case)."""
        conn = AsyncMock()
        conn.fetchval = AsyncMock(return_value="connector")
        with patch("pipeline.evict._resolve_recipe_path", return_value=None):
            passed, reasons = await _check_gate2(conn, "CDP-ES-28-7Q2K9ABX")
        assert passed
        assert reasons == []


# ---------------------------------------------------------------------------
# 3. Gate 3 — inventory zeroed, g4_served=False, no OPEN gestion items
# ---------------------------------------------------------------------------

class TestGate3:

    @pytest.mark.asyncio
    async def test_gate3_fails_when_available_vehicles_exist(self) -> None:
        """Gate 3 fails when available_count > 0."""
        conn = AsyncMock()
        # fetchval calls in order: avail_count=5, has_open_gestion=False
        conn.fetchval = AsyncMock(side_effect=[5, False])
        conn.fetchrow = AsyncMock(return_value={"g4_served": False})
        passed, reasons = await _check_gate3(conn, "CDP-ES-28-7Q2K9ABX")
        assert not passed
        assert any("available vehicle" in r for r in reasons)

    @pytest.mark.asyncio
    async def test_gate3_fails_when_g4_served_true(self) -> None:
        """Gate 3 fails when entity_completion.g4_served=True."""
        conn = AsyncMock()
        conn.fetchval = AsyncMock(side_effect=[0, False])
        conn.fetchrow = AsyncMock(return_value={"g4_served": True})
        passed, reasons = await _check_gate3(conn, "CDP-ES-28-7Q2K9ABX")
        assert not passed
        assert any("g4_served" in r for r in reasons)

    @pytest.mark.asyncio
    async def test_gate3_fails_when_open_gestion_item(self) -> None:
        """Gate 3 fails when OPEN gestion_item exists."""
        conn = AsyncMock()
        conn.fetchval = AsyncMock(side_effect=[0, True])
        conn.fetchrow = AsyncMock(return_value={"g4_served": False})
        passed, reasons = await _check_gate3(conn, "CDP-ES-28-7Q2K9ABX")
        assert not passed
        assert any("gestion" in r.lower() for r in reasons)

    @pytest.mark.asyncio
    async def test_gate3_passes_when_all_clear(self) -> None:
        """Gate 3 passes: avail=0, g4_served=False, no OPEN gestion items."""
        conn = AsyncMock()
        conn.fetchval = AsyncMock(side_effect=[0, False])
        conn.fetchrow = AsyncMock(return_value={"g4_served": False})
        passed, reasons = await _check_gate3(conn, "CDP-ES-28-7Q2K9ABX")
        assert passed
        assert reasons == []


# ---------------------------------------------------------------------------
# 4. check_preconditions — combined gate blocking
# ---------------------------------------------------------------------------

class TestCheckPreconditions:

    @pytest.mark.asyncio
    async def test_preconditions_gate1_blocks(self) -> None:
        """If Gate 1 fails (TRUSTWORTHY exists), check_preconditions returns False."""
        conn = AsyncMock()
        # Gate1 fetchvals: has_trustworthy=True, has_death_evidence=True
        # Gate2 fetchval: recipe_kind (recipe_path=None → connector check) = 'none'
        # Gate3 fetchvals: avail=0, open_gestion=False
        conn.fetchval = AsyncMock(side_effect=[True, True, "none", 0, False])
        conn.fetchrow = AsyncMock(return_value={"g4_served": False})

        with patch("pipeline.evict._resolve_recipe_path", return_value=None):
            passed, reasons = await check_preconditions(conn, "CDP-ES-28-7Q2K9ABX")

        assert not passed
        assert any("gate1" in r for r in reasons)

    @pytest.mark.asyncio
    async def test_preconditions_gate3_blocks_on_available_vehicles(self) -> None:
        """If Gate 3 fails (avail>0), check_preconditions blocks."""
        conn = AsyncMock()
        # Gate1: no trustworthy, has death evidence → passes
        # Gate3: avail=3 → blocks
        conn.fetchval = AsyncMock(side_effect=[False, True, 3, False])
        conn.fetchrow = AsyncMock(return_value={"g4_served": False})

        with (
            patch("pipeline.evict._resolve_recipe_path",
                  return_value=Path("/fake/recipe.yaml")),
            patch("pipeline.evict._check_g3_git_subsignal",
                  return_value=("abc123", "git_tracked_and_committed")),
        ):
            passed, reasons = await check_preconditions(conn, "CDP-ES-28-7Q2K9ABX")

        assert not passed
        assert any("available vehicle" in r for r in reasons)

    @pytest.mark.asyncio
    async def test_preconditions_all_gates_pass(self) -> None:
        """All gates pass returns (True, [])."""
        conn = AsyncMock()
        conn.fetchval = AsyncMock(side_effect=[False, True, 0, False])
        conn.fetchrow = AsyncMock(return_value={"g4_served": False})

        with (
            patch("pipeline.evict._resolve_recipe_path",
                  return_value=Path("/fake/recipe.yaml")),
            patch("pipeline.evict._check_g3_git_subsignal",
                  return_value=("abc123", "git_tracked_and_committed")),
        ):
            passed, reasons = await check_preconditions(conn, "CDP-ES-28-7Q2K9ABX")

        assert passed
        assert reasons == []


# ---------------------------------------------------------------------------
# 5. evict_dealer dry_run=True — returns plan, calls no execute
# ---------------------------------------------------------------------------

class TestEvictDryRun:

    @pytest.mark.asyncio
    async def test_dry_run_with_mocked_green_gates(self) -> None:
        """Dry-run with all gates passing: returns plan dict, no execute called."""
        conn = AsyncMock()
        # Gate1: no trustworthy, has death evidence
        conn.fetchval = AsyncMock(side_effect=[
            False,           # has_trustworthy (Gate1)
            True,            # has_death_evidence (Gate1)
            0,               # avail_count (Gate3 _GATE3_AVAIL_SQL)
            False,           # has_open_gestion (Gate3)
            # fetchrow for entity_ulid resolution is handled below
        ])
        conn.fetchrow = AsyncMock(side_effect=[
            {"g4_served": False},             # Gate3 g4_served
            {"entity_ulid": "01KTXWHDR1Q3E0D3X60P8W31TQ"},  # entity resolution
        ])
        # vehicles_to_delete count
        conn.fetchval = AsyncMock(side_effect=[False, True, 0, False, 7])

        with (
            patch("pipeline.evict._resolve_recipe_path",
                  return_value=Path("/fake/recipe.yaml")),
            patch("pipeline.evict._check_g3_git_subsignal",
                  return_value=("abc123def456", "git_tracked_and_committed")),
        ):
            result = await evict_dealer(conn, "CDP-ES-28-7Q2K9ABX", dry_run=True)

        assert result["dry_run"] is True
        assert result["evicted"] is False  # dry_run never sets evicted=True
        assert result["cdp_code"] == "CDP-ES-28-7Q2K9ABX"
        # No writes: execute must not have been called
        conn.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_dry_run_real_dealer_read_only(self, db_conn: asyncpg.Connection) -> None:
        """Dry-run against a real dealer: nothing in DB changes (gates will fail — that is OK).

        Transaction is NOT needed here because dry_run never writes.
        We just verify the return shape and that entity status is unchanged.
        """
        row = await db_conn.fetchrow(
            """
            SELECT e.cdp_code, e.entity_ulid, e.status::text AS status
            FROM entity e
            ORDER BY e.cdp_code
            LIMIT 1
            """
        )
        assert row is not None, "No entity rows found in DB"
        cdp_code = row["cdp_code"]
        status_before = row["status"]

        result = await evict_dealer(db_conn, cdp_code, dry_run=True)

        assert result["dry_run"] is True
        assert result["cdp_code"] == cdp_code
        assert "evicted" in result
        assert "vehicles_to_delete" in result

        # Entity status unchanged
        status_after = await db_conn.fetchval(
            "SELECT status::text FROM entity WHERE cdp_code = $1", cdp_code
        )
        assert status_before == status_after


# ---------------------------------------------------------------------------
# 6. evict_dealer failing gate — executes nothing
# ---------------------------------------------------------------------------

class TestEvictBlockedByGate:

    @pytest.mark.asyncio
    async def test_blocked_by_gate1_no_writes(self) -> None:
        """When Gate 1 fails, evict_dealer returns without any DB writes."""
        conn = AsyncMock()
        # Gate1: has_trustworthy=True (BLOCKS)
        conn.fetchval = AsyncMock(side_effect=[True, True, 0, False])
        conn.fetchrow = AsyncMock(return_value={"g4_served": False})

        with (
            patch("pipeline.evict._resolve_recipe_path",
                  return_value=Path("/fake/recipe.yaml")),
            patch("pipeline.evict._check_g3_git_subsignal",
                  return_value=("abc", "git_tracked_and_committed")),
        ):
            result = await evict_dealer(conn, "CDP-ES-28-7Q2K9ABX", dry_run=False)

        assert result["evicted"] is False
        assert any("TRUSTWORTHY" in r for r in result["reasons"])
        conn.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_blocked_by_gate3_no_writes(self) -> None:
        """When Gate 3 fails (avail>0), evict_dealer returns without writes."""
        conn = AsyncMock()
        # Gate1 passes, Gate3 avail=5 blocks
        conn.fetchval = AsyncMock(side_effect=[False, True, 5, False])
        conn.fetchrow = AsyncMock(return_value={"g4_served": False})

        with (
            patch("pipeline.evict._resolve_recipe_path",
                  return_value=Path("/fake/recipe.yaml")),
            patch("pipeline.evict._check_g3_git_subsignal",
                  return_value=("abc", "git_tracked_and_committed")),
        ):
            result = await evict_dealer(conn, "CDP-ES-28-7Q2K9ABX", dry_run=False)

        assert result["evicted"] is False
        assert any("available vehicle" in r for r in result["reasons"])
        conn.execute.assert_not_called()


# ---------------------------------------------------------------------------
# 7. evict_dealer --apply (synthetic dealer, rolled-back transaction)
# ---------------------------------------------------------------------------

class TestEvictApply:
    """Full apply path with a synthetic dealer row, rolled back after assertions.

    Synthetic values all pass DB CHECK constraints:
      cdp_code: CDP-ES-28-SYNT0001 → matches ^CDP-ES-[0-9]{2}-[0-9A-HJKMNP-TV-Z]{8}$
      entity_ulid: 01TESTHDR1Q3E0D3X60P8W31TQ → matches ^[0-9A-HJKMNP-TV-Z]{26}$
    """

    @pytest.mark.asyncio
    async def test_apply_evicts_entity_and_deletes_vehicles(
        self, db_conn: asyncpg.Connection
    ) -> None:
        """Apply: entity.status='evicted', vehicles deleted, audit + ledger rows written.

        All seeded rows are rolled back at the end — real DB is untouched.
        """
        try:
            async with db_conn.transaction():
                # Insert synthetic entity (kind + province must match existing enum/FK)
                await db_conn.execute(
                    """
                    INSERT INTO entity
                        (entity_ulid, cdp_code, kind, province_code, status)
                    VALUES
                        ($1, $2, 'compraventa'::entity_kind, '28', 'unverified'::entity_status)
                    ON CONFLICT (cdp_code) DO NOTHING
                    """,
                    _SYNTH_ULID,
                    _SYNTH_CDP,
                )

                # Insert two synthetic vehicles with status='gone' (avail=0 required by Gate3)
                for vh_ulid, i in [(_SYNTH_VH_ULID_0, 0), (_SYNTH_VH_ULID_1, 1)]:
                    await db_conn.execute(
                        """
                        INSERT INTO vehicle
                            (vehicle_ulid, entity_ulid, deep_link, status)
                        VALUES ($1, $2, $3, 'gone')
                        ON CONFLICT (entity_ulid, deep_link) DO NOTHING
                        """,
                        vh_ulid,
                        _SYNTH_ULID,
                        f"https://example.com/ev/{i}",
                    )

                # Insert a REFUTED verdict for Gate1 death evidence
                await db_conn.execute(
                    """
                    INSERT INTO verification_verdict
                        (subject_type, subject_key, claim, verdict, method_version)
                    VALUES ('entity_inventory', $1, 'inventory_count', 'REFUTED', 'vam-1')
                    """,
                    _SYNTH_ULID,
                )

                # Verify pre-conditions
                ent_status = await db_conn.fetchval(
                    "SELECT status::text FROM entity WHERE cdp_code = $1", _SYNTH_CDP
                )
                assert ent_status == "unverified"

                veh_count_pre = await db_conn.fetchval(
                    "SELECT COUNT(*) FROM vehicle WHERE entity_ulid = $1", _SYNTH_ULID
                )
                assert veh_count_pre == 2

                # Patch ALL 3 gates to green + raw-file eviction to no-op
                # so we exercise only the DB write path
                with (
                    patch("pipeline.evict._check_gate1", return_value=(True, [])),
                    patch("pipeline.evict._check_gate2", return_value=(True, [])),
                    patch("pipeline.evict._check_gate3", return_value=(True, [])),
                    patch("pipeline.evict._evict_raw_files", return_value=(0, 0)),
                    patch("pipeline.evict.shutil.disk_usage",
                          side_effect=OSError("test: no disk")),
                ):
                    result = await evict_dealer(
                        db_conn,
                        _SYNTH_CDP,
                        dry_run=False,
                        actor="test_suite",
                    )

                # --- Assertions on result dict ---
                assert result["evicted"] is True, f"Expected evicted=True, got: {result}"
                assert result["dry_run"] is False
                assert result["entity_ulid"] == _SYNTH_ULID
                assert result["reasons"] == []

                # --- Entity tombstoned ---
                ent_status_after = await db_conn.fetchval(
                    "SELECT status::text FROM entity WHERE cdp_code = $1", _SYNTH_CDP
                )
                assert ent_status_after == "evicted"

                evicted_at = await db_conn.fetchval(
                    "SELECT evicted_at FROM entity WHERE cdp_code = $1", _SYNTH_CDP
                )
                assert evicted_at is not None

                # --- Vehicles deleted ---
                veh_count_after = await db_conn.fetchval(
                    "SELECT COUNT(*) FROM vehicle WHERE entity_ulid = $1", _SYNTH_ULID
                )
                assert veh_count_after == 0

                # --- audit_eviction row written ---
                audit_row = await db_conn.fetchrow(
                    "SELECT * FROM audit_eviction WHERE cdp_code = $1", _SYNTH_CDP
                )
                assert audit_row is not None
                assert audit_row["actor"] == "test_suite"
                assert audit_row["vehicles_deleted"] == 2

                # --- capacity_ledger row written ---
                ledger_row = await db_conn.fetchrow(
                    "SELECT * FROM capacity_ledger WHERE cdp_code = $1", _SYNTH_CDP
                )
                assert ledger_row is not None
                assert ledger_row["vehicles_deleted"] == 2

                # ROLLBACK everything — raises to exit transaction block
                raise _TestRollback("rolling back test transaction — no real data affected")

        except _TestRollback:
            pass  # Expected: transaction rolled back, DB is clean

        # Post-rollback verification: synthetic entity must NOT exist
        ent_exists = await db_conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM entity WHERE cdp_code = $1)", _SYNTH_CDP
        )
        assert not ent_exists, "Rollback failed: synthetic entity still in DB"


# ---------------------------------------------------------------------------
# 8. audit_eviction immutability — UPDATE/DELETE raises
# ---------------------------------------------------------------------------

class TestAuditEvictionImmutability:
    """The BEFORE UPDATE/DELETE trigger must raise 'append-only' for audit_eviction."""

    # Use a cdp_code that passes the CHECK constraint: all Crockford chars
    _CDP_IMMUT1 = "CDP-ES-28-TSTMUT01"  # T, S, T, M, U? No: U is excluded
    # Let's use: TSTMT001
    _CDP_IMMUT1 = "CDP-ES-28-TSTMT001"
    _CDP_IMMUT2 = "CDP-ES-28-TSTMT002"

    @pytest.mark.asyncio
    async def test_update_raises_append_only(self, db_conn: asyncpg.Connection) -> None:
        """UPDATE on audit_eviction raises PostgresError with 'append-only'."""
        try:
            async with db_conn.transaction():
                await db_conn.execute(
                    """
                    INSERT INTO audit_eviction (cdp_code, reason, actor)
                    VALUES ($1, 'test immutability update', 'pytest')
                    """,
                    self._CDP_IMMUT1,
                )
                with pytest.raises(asyncpg.PostgresError) as exc_info:
                    await db_conn.execute(
                        "UPDATE audit_eviction SET reason='tampered' WHERE cdp_code=$1",
                        self._CDP_IMMUT1,
                    )
                assert "append-only" in str(exc_info.value).lower()
                raise _TestRollback("rollback update immutability test")
        except _TestRollback:
            pass

    @pytest.mark.asyncio
    async def test_delete_raises_append_only(self, db_conn: asyncpg.Connection) -> None:
        """DELETE on audit_eviction raises PostgresError with 'append-only'."""
        try:
            async with db_conn.transaction():
                await db_conn.execute(
                    """
                    INSERT INTO audit_eviction (cdp_code, reason, actor)
                    VALUES ($1, 'test immutability delete', 'pytest')
                    """,
                    self._CDP_IMMUT2,
                )
                with pytest.raises(asyncpg.PostgresError) as exc_info:
                    await db_conn.execute(
                        "DELETE FROM audit_eviction WHERE cdp_code=$1",
                        self._CDP_IMMUT2,
                    )
                assert "append-only" in str(exc_info.value).lower()
                raise _TestRollback("rollback delete immutability test")
        except _TestRollback:
            pass


# ---------------------------------------------------------------------------
# 9. Raw-file eviction — tmp_path only, never touches real data/
# ---------------------------------------------------------------------------

class TestEvictRawFiles:

    def test_no_eviction_below_threshold(self, tmp_path: Path) -> None:
        """No files deleted when disk usage is below DISK_EVICT_THRESHOLD_PCT."""
        cdp = "CDP-ES-28-RAWTEST1"
        raw_file = tmp_path / f"{cdp}_raw.json"
        raw_file.write_text('{"test": 1}')

        with (
            patch("pipeline.evict._DATA_DIR", tmp_path),
            patch("pipeline.evict.shutil.disk_usage") as mock_du,
        ):
            # 50% used — below 80% threshold
            mock_du.return_value = MagicMock(used=50, total=100, free=50)
            files_deleted, bytes_freed = _evict_raw_files(cdp)

        assert files_deleted == 0
        assert bytes_freed == 0
        assert raw_file.exists(), "File must NOT be deleted below threshold"

    def test_eviction_above_threshold(self, tmp_path: Path) -> None:
        """Files matching cdp_code are deleted when disk usage exceeds threshold."""
        cdp = "CDP-ES-28-RAWTEST2"
        raw_file = tmp_path / f"{cdp}_harvest.json"
        raw_file.write_text('{"vehicles": []}')
        original_size = raw_file.stat().st_size

        with (
            patch("pipeline.evict._DATA_DIR", tmp_path),
            patch("pipeline.evict.shutil.disk_usage") as mock_du,
        ):
            # 90% used — above 80% threshold
            mock_du.return_value = MagicMock(used=90, total=100, free=10)
            files_deleted, bytes_freed = _evict_raw_files(cdp)

        assert files_deleted == 1
        assert bytes_freed == original_size
        assert not raw_file.exists(), "File must be deleted above threshold"

    def test_eviction_does_not_touch_other_dealers(self, tmp_path: Path) -> None:
        """Files for other dealers are NOT deleted even above threshold."""
        cdp_target = "CDP-ES-28-RAWTEST3"
        cdp_other = "CDP-ES-28-RAWOTH01"

        target_file = tmp_path / f"{cdp_target}_raw.json"
        other_file = tmp_path / f"{cdp_other}_raw.json"
        target_file.write_text('{"target": 1}')
        other_file.write_text('{"other": 1}')

        with (
            patch("pipeline.evict._DATA_DIR", tmp_path),
            patch("pipeline.evict.shutil.disk_usage") as mock_du,
        ):
            mock_du.return_value = MagicMock(used=90, total=100, free=10)
            _evict_raw_files(cdp_target)

        assert not target_file.exists(), "Target dealer file must be deleted"
        assert other_file.exists(), "Other dealer file must NOT be deleted"
