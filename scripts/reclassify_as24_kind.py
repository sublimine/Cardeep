"""Backfill: reclassify AS24 entities mis-kinded as concesionario_oficial → compraventa.

AutoScout24 is a mixed marketplace. The ingest connector (pipeline/ingest.py) used to
hardcode kind='concesionario_oficial' for every AS24 dealer ingested, regardless of
whether the dealer was an OEM franchisee or an independent compraventa. This script
corrects the 469 entities that received that false default.

What changes:
  - kind: 'concesionario_oficial' → 'compraventa'
  - kind_source: 'manual'       → 'platform_label'
    (platform_label is the existing enum value that best communicates
    "origin=marketplace listing, low confidence — subject to classifier override")

What does NOT change:
  - Entities with first_discovered_source != 'as24'  (other sources untouched)
  - Entities already at kind != 'concesionario_oficial'  (compraventa, garaje, etc.)
  - Entities whose kind='concesionario_oficial' came from an oem_* source (those are
    legitimate OEM concessionaires confirmed by franchise directories — not in scope)
  - cdp_code, entity_ulid, vehicle rows, vehicle_events, org_id: all immutable

Idempotent: a second run against an already-patched DB executes 0 UPDATEs.

Disclaimer on false positives: a small fraction (~10%) of AS24 entities may genuinely
be OEM concessionaires (brand-name dealers present on AS24 that also appear in franchise
directories). Those are demoted to 'compraventa' here but flagged with kind_source=
'platform_label' so the OEM-locator / classifier can re-elevate them if brand signals
are found. This is the correct direction: under-claim then re-certify, not over-claim.

Usage:  python scripts/reclassify_as24_kind.py
        CARDEEP_DSN=postgres://... python scripts/reclassify_as24_kind.py
"""
from __future__ import annotations

import asyncio
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import asyncpg

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")


async def main() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        # ── Snapshot BEFORE ────────────────────────────────────────────────────────
        before_total = await conn.fetchrow(
            "SELECT count(*) AS total FROM entity WHERE first_discovered_source='as24'"
        )
        before_breakdown = await conn.fetch(
            """
            SELECT kind, kind_source, count(*) AS n
            FROM entity
            WHERE first_discovered_source = 'as24'
            GROUP BY kind, kind_source
            ORDER BY count(*) DESC
            """
        )
        print("=== BEFORE ===")
        for row in before_breakdown:
            print(f"  kind={row['kind']!r:30s}  kind_source={row['kind_source']!r:20s}  n={row['n']}")

        # ── Guard: confirm oem_* concessionaires are untouched by this scope ──────
        oem_count_before = await conn.fetchval(
            "SELECT count(*) FROM entity WHERE kind='concesionario_oficial' AND first_discovered_source LIKE 'oem_%'"
        )

        # ── Core UPDATE (single statement, scoped tightly) ─────────────────────────
        async with conn.transaction():
            updated = await conn.execute(
                """
                UPDATE entity
                SET kind        = 'compraventa',
                    kind_source = 'platform_label'
                WHERE first_discovered_source = 'as24'
                  AND kind        = 'concesionario_oficial'
                  AND kind_source = 'manual'
                """,
            )
            # asyncpg returns "UPDATE <n>" as a string
            rows_updated = int(updated.split()[-1])

        print(f"\n=== UPDATE ===")
        print(f"  Rows changed: {rows_updated}")

        # ── Snapshot AFTER ─────────────────────────────────────────────────────────
        after_breakdown = await conn.fetch(
            """
            SELECT kind, kind_source, count(*) AS n
            FROM entity
            WHERE first_discovered_source = 'as24'
            GROUP BY kind, kind_source
            ORDER BY count(*) DESC
            """
        )
        after_official_as24 = await conn.fetchval(
            "SELECT count(*) FROM entity WHERE first_discovered_source='as24' AND kind='concesionario_oficial'"
        )
        oem_count_after = await conn.fetchval(
            "SELECT count(*) FROM entity WHERE kind='concesionario_oficial' AND first_discovered_source LIKE 'oem_%'"
        )

        print("\n=== AFTER ===")
        for row in after_breakdown:
            print(f"  kind={row['kind']!r:30s}  kind_source={row['kind_source']!r:20s}  n={row['n']}")

        print(f"\n=== VERIFICATION ===")
        print(f"  as24 + concesionario_oficial remaining  : {after_official_as24}  (expected: 0)")
        print(f"  oem_* concesionario_oficial BEFORE      : {oem_count_before}  (must be unchanged)")
        print(f"  oem_* concesionario_oficial AFTER       : {oem_count_after}  (expected: same as before)")

        if after_official_as24 != 0:
            print("\n  [ERROR] Some as24 concesionario_oficial rows remain — check kind_source mismatch")
            sys.exit(1)
        if oem_count_before != oem_count_after:
            print(f"\n  [ERROR] oem_* concesionario_oficial count changed: {oem_count_before} → {oem_count_after}")
            sys.exit(1)

        print(f"\n  [OK] Backfill complete. Rows updated: {rows_updated}.")
        if rows_updated == 0:
            print("  [INFO] 0 rows updated — script is idempotent (already applied or nothing to fix).")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
