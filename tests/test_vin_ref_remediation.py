"""Regression guard for migrations/0083_vin_ref_remediation.sql (04-arbitrage F6).

CRITICAL FINDING (F6 audit, 2026-07-18): 2,479,113 of 2,670,828 vehicles carried a
non-null ``vin_ref`` that was NOT a well-formed 17-character VIN — source-native
listing ids stored under the wrong column name (traced live to
pipeline/sources/autoscout24.py:208, since fixed). This test is the permanent guard:
once a vehicle carries a non-null vin_ref, it MUST be a real VIN shape, never a
listing id — a structural invariant this project's downstream VIN-matching consumers
(02-history-reports' link_lifetimes.py::_normalize_vin) already defend against at
READ time; this test guards it at the DATA level so the column itself stays honest.

DB-touching, live cardeep-pg (read-only assertions, no writes, no rollback needed).
"""
from __future__ import annotations

import os
import re

import asyncpg
import pytest

_DSN = os.environ.get(
    "CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
)

# Standard VIN charset: A-Z0-9 excluding I, O, Q (avoid 1/0 confusion) — same shape
# tests/test_link_lifetimes.py::_normalize_vin already enforces at read time.
_VIN_SHAPE = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")


@pytest.mark.integration
class TestVinRefShape:
    @pytest.mark.asyncio
    async def test_no_non_vin_shaped_values_remain(self) -> None:
        """Every non-null vin_ref in the live census must be a well-formed 17-char VIN.

        This is the exact query used to size migrations/0083 before writing it
        (2,479,113 offenders measured, 41,510 kept) — re-run here as a permanent
        regression gate so a future harvester reintroducing the
        vin_ref=listing_id anti-pattern is caught, not silently re-contaminating
        the column.
        """
        conn = await asyncpg.connect(_DSN)
        try:
            offenders = await conn.fetch(
                "SELECT vehicle_ulid, vin_ref FROM vehicle "
                "WHERE vin_ref IS NOT NULL AND upper(vin_ref) !~ '^[A-HJ-NPR-Z0-9]{17}$' "
                "LIMIT 20"
            )
            total_offenders = await conn.fetchval(
                "SELECT count(*) FROM vehicle "
                "WHERE vin_ref IS NOT NULL AND upper(vin_ref) !~ '^[A-HJ-NPR-Z0-9]{17}$'"
            )
        finally:
            await conn.close()

        assert total_offenders == 0, (
            f"{total_offenders} vehicle(s) carry a non-VIN-shaped vin_ref (contamination "
            f"regressed) — sample: {[dict(r) for r in offenders]}"
        )

    @pytest.mark.asyncio
    async def test_kept_vins_are_genuinely_well_formed(self) -> None:
        """Sanity check the INVERSE: every remaining non-null vin_ref really does
        match the VIN shape in Python too (guards against a SQL/Python regex
        divergence hiding a bug in either direction)."""
        conn = await asyncpg.connect(_DSN)
        try:
            rows = await conn.fetch(
                "SELECT vin_ref FROM vehicle WHERE vin_ref IS NOT NULL LIMIT 5000"
            )
        finally:
            await conn.close()

        if not rows:
            pytest.skip("no non-null vin_ref rows exist yet")

        non_matching = [r["vin_ref"] for r in rows if not _VIN_SHAPE.match(r["vin_ref"].upper())]
        assert non_matching == [], f"non-VIN-shaped values found in sample: {non_matching[:10]}"
