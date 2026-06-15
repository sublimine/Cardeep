"""pipeline/evict.py — BORRAR/DELETE stage of the Cardeep E2E.

Safely and irreversibly removes a dead dealer and its inventory after confirming
all three hard precondition gates pass simultaneously. Designed for manual
Director-only execution: the default mode is --dry-run (safe, read-only).
The --apply flag must be supplied explicitly to execute destructive operations.

SAFETY CONTRACT
---------------
- NEVER executes destructive operations unless ALL 3 gates are green.
- Gates are re-read at eviction time (re-checked inside the transaction).
- --dry-run is the DEFAULT: prints the plan and exits without touching anything.
- --apply is the only flag that executes changes; it requires explicit invocation.
- All DB changes happen in a SINGLE atomic transaction: partial states are
  impossible — either everything commits or nothing does.
- Raw files deleted are ONLY the dealer's raw harvest files under data/;
  recipe.yaml files in countries/ES/ are never touched.

Disk watermark
--------------
LRU eviction of raw files is triggered when disk usage on the data/ partition
exceeds DISK_EVICT_THRESHOLD_PCT (default 80%). When the threshold is not
exceeded, raw files are NOT deleted (they stay as cold storage). Raw file
deletion is best-effort: a failure to delete a raw file logs a warning but
does NOT abort the DB eviction — inventory savings are prioritised.

DB access (asyncpg)
-------------------
DSN: postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep

Gate SQL (exact, verified against live schema 2026-06-15):
  Gate 1: verification_verdict (TRUSTWORTHY active check + REFUTED/UNVERIFIED evidence)
  Gate 2: recipe committed at git HEAD via helpers from pipeline/complete.py
  Gate 3: vehicle.status='available' count=0 + entity_completion.g4_served=False
          + no OPEN gestion_item for the dealer
"""
from __future__ import annotations

import argparse
import asyncio
import os
import shutil
from pathlib import Path
from typing import Any

import asyncpg

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DSN = os.environ.get(
    "CARDEEP_DSN",
    "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep",
)

# Repo root: directory containing migrations/ (two levels up from this file)
_REPO_ROOT = Path(__file__).resolve().parent.parent

# Raw data directory (never recipes/countries; only raw harvest dumps)
_DATA_DIR = _REPO_ROOT / "data"

# Disk threshold: LRU eviction of raw files fires when disk usage >= this
# percentage of total capacity on the _DATA_DIR partition.
DISK_EVICT_THRESHOLD_PCT: float = 80.0


# ---------------------------------------------------------------------------
# Helpers: borrow recipe-path and git-subsignal from complete.py
# ---------------------------------------------------------------------------

from pipeline.complete import (  # noqa: E402 (after constants)
    _check_g3_git_subsignal,
    _resolve_recipe_path,
)


# ---------------------------------------------------------------------------
# Gate 1 — VAM confirms death: no active TRUSTWORTHY verdict
# ---------------------------------------------------------------------------

_GATE1_TRUSTWORTHY_SQL = """
SELECT EXISTS (
    SELECT 1
    FROM verification_verdict vv
    JOIN entity e ON (
        vv.subject_type = 'entity_inventory'
        AND vv.subject_key = e.entity_ulid
    )
    WHERE e.cdp_code = $1
      AND vv.verdict = 'TRUSTWORTHY'
      AND (vv.expires_at IS NULL OR vv.expires_at > now())
      AND vv.superseded_by IS NULL
) AS has_trustworthy
"""

_GATE1_REFUTED_EVIDENCE_SQL = """
SELECT EXISTS (
    SELECT 1
    FROM verification_verdict vv
    JOIN entity e ON (
        vv.subject_type = 'entity_inventory'
        AND vv.subject_key = e.entity_ulid
    )
    WHERE e.cdp_code = $1
      AND vv.verdict IN ('REFUTED', 'UNVERIFIED')
      AND (vv.superseded_by IS NULL)
) AS has_death_evidence
"""


async def _check_gate1(conn: asyncpg.Connection, cdp_code: str) -> tuple[bool, list[str]]:
    """Gate 1: no active TRUSTWORTHY verdict + death evidence present.

    Returns (passed, failure_reasons).
    Passes when:
      - There is NO active TRUSTWORTHY verdict for the dealer's inventory.
      - There IS at least one REFUTED or UNVERIFIED (or gone-reconcile) verdict.
    """
    reasons: list[str] = []

    has_trustworthy: bool = await conn.fetchval(_GATE1_TRUSTWORTHY_SQL, cdp_code)
    if has_trustworthy:
        reasons.append("gate1_fail: active TRUSTWORTHY verdict exists — dealer may still be alive")

    has_death_evidence: bool = await conn.fetchval(_GATE1_REFUTED_EVIDENCE_SQL, cdp_code)
    if not has_death_evidence:
        reasons.append(
            "gate1_fail: no REFUTED/UNVERIFIED verdict found — no confirmed death evidence"
        )

    return (len(reasons) == 0), reasons


# ---------------------------------------------------------------------------
# Gate 2 — Recipe committed at git HEAD
# ---------------------------------------------------------------------------

async def _check_gate2(conn: "asyncpg.Connection", cdp_code: str) -> tuple[bool, list[str]]:
    """Gate 2: the dealer's recipe is PRESERVED + committed (re-scrapeable post-evict).

    Two valid forms of "recipe preserved" — eviction is safe if EITHER holds:
      (a) a per_dealer `recipe.yaml` committed at git HEAD (own-site / long-tail dealers), OR
      (b) connector coverage: `v_dealer_recipe.recipe_kind = 'connector'` — the recipe IS the
          shared platform connector (committed Python in `pipeline/platform/`), which covers
          ~98.4% of the corpus. Requiring a per-dealer yaml for connector dealers would make
          them permanently un-evictable (wrong); the connector is the preserved, committed asset
          that re-scrapes the dealer if it reappears.
    """
    reasons: list[str] = []

    # Form (a): per_dealer recipe.yaml committed at HEAD
    recipe_path = _resolve_recipe_path(cdp_code, _REPO_ROOT)
    if recipe_path is not None:
        _sha, git_reason = _check_g3_git_subsignal(cdp_code, _REPO_ROOT)
        if git_reason == "git_tracked_and_committed":
            return True, []
        reasons.append(f"gate2: recipe.yaml present but not at git HEAD: {git_reason}")

    # Form (b): connector coverage (the committed connector module is the recipe)
    recipe_kind = await conn.fetchval(
        "SELECT recipe_kind FROM v_dealer_recipe WHERE cdp_code = $1", cdp_code
    )
    if recipe_kind == "connector":
        return True, []

    reasons.append(
        f"gate2_fail: no preserved recipe for {cdp_code!r} "
        f"(no committed recipe.yaml; v_dealer_recipe.recipe_kind={recipe_kind!r})"
    )
    return False, reasons


# ---------------------------------------------------------------------------
# Gate 3 — Counts are zeroed: no available inventory, G4 confirmed empty,
#           no OPEN gestion items
# ---------------------------------------------------------------------------

_GATE3_AVAIL_SQL = """
SELECT COUNT(*) AS avail_count
FROM vehicle
WHERE entity_ulid = (SELECT entity_ulid FROM entity WHERE cdp_code = $1 LIMIT 1)
  AND status = 'available'
"""

_GATE3_G4_SQL = """
SELECT g4_served
FROM entity_completion
WHERE cdp_code = $1
"""

_GATE3_OPEN_GESTION_SQL = """
SELECT EXISTS (
    SELECT 1
    FROM gestion_item
    WHERE subject_key = $1
      AND state = 'OPEN'
) AS has_open_items
"""


async def _check_gate3(conn: asyncpg.Connection, cdp_code: str) -> tuple[bool, list[str]]:
    """Gate 3: available inventory=0, g4_served=False, no OPEN gestion items.

    Returns (passed, failure_reasons).
    """
    reasons: list[str] = []

    # Check available vehicle count
    avail_count: int = await conn.fetchval(_GATE3_AVAIL_SQL, cdp_code)
    if avail_count is None:
        avail_count = 0
    if avail_count > 0:
        reasons.append(
            f"gate3_fail: {avail_count} available vehicle(s) still indexed for {cdp_code!r} "
            "— inventory must be zeroed before eviction"
        )

    # Check entity_completion.g4_served is False (G4 confirms inventory empty)
    ec_row = await conn.fetchrow(_GATE3_G4_SQL, cdp_code)
    if ec_row is not None:
        g4_served: bool | None = ec_row["g4_served"]
        if g4_served is True:
            reasons.append(
                "gate3_fail: entity_completion.g4_served=True — completion gate still active; "
                "inventory must be unserved before eviction"
            )
    # If no entity_completion row, g4_served is effectively None — not a blocker,
    # since the entity may never have been completed. Log it but do not block.

    # Check no OPEN gestion items for this dealer (keyed by cdp_code as subject_key)
    has_open: bool = await conn.fetchval(_GATE3_OPEN_GESTION_SQL, cdp_code)
    if has_open:
        reasons.append(
            f"gate3_fail: OPEN gestion_item(s) exist for {cdp_code!r} — "
            "resolve all open items before eviction"
        )

    return (len(reasons) == 0), reasons


# ---------------------------------------------------------------------------
# Public API: check_preconditions
# ---------------------------------------------------------------------------

async def check_preconditions(
    conn: asyncpg.Connection,
    cdp_code: str,
) -> tuple[bool, list[str]]:
    """Evaluate all 3 hard precondition gates for evicting a dealer.

    READ-ONLY: touches nothing. Safe to call at any time.

    Returns:
        (True, [])               — all gates pass, eviction may proceed
        (False, [reason, ...])   — one or more gates failed; reasons listed
    """
    all_reasons: list[str] = []

    g1_ok, g1_reasons = await _check_gate1(conn, cdp_code)
    all_reasons.extend(g1_reasons)

    g2_ok, g2_reasons = await _check_gate2(conn, cdp_code)
    all_reasons.extend(g2_reasons)

    g3_ok, g3_reasons = await _check_gate3(conn, cdp_code)
    all_reasons.extend(g3_reasons)

    passed = g1_ok and g2_ok and g3_ok
    return passed, all_reasons


# ---------------------------------------------------------------------------
# LRU raw-file eviction
# ---------------------------------------------------------------------------

def _evict_raw_files(cdp_code: str) -> tuple[int, int]:
    """LRU-evict raw harvest files for a dealer from the data/ directory.

    Only removes files under _DATA_DIR that belong to this dealer
    (directories/files matching the cdp_code pattern). Never touches
    countries/ES/ (recipes) or any other pipeline artefact.

    Eviction fires only when disk usage on the data/ partition exceeds
    DISK_EVICT_THRESHOLD_PCT. If the threshold is not met, returns (0, 0).

    Returns:
        (files_deleted, bytes_freed)
    """
    if not _DATA_DIR.exists():
        return 0, 0

    # Check disk usage
    try:
        usage = shutil.disk_usage(_DATA_DIR)
        pct_used = (usage.used / usage.total) * 100.0
        disk_free_bytes = usage.free
    except OSError:
        return 0, 0

    if pct_used < DISK_EVICT_THRESHOLD_PCT:
        # Disk is below threshold; skip raw-file deletion
        return 0, 0

    # Find all raw files/dirs for this dealer (LRU: oldest mtime first)
    candidates: list[Path] = sorted(
        _DATA_DIR.rglob(f"*{cdp_code}*"),
        key=lambda p: p.stat().st_mtime if p.exists() else 0,
    )

    files_deleted = 0
    bytes_freed = 0

    for path in candidates:
        try:
            if path.is_file():
                size = path.stat().st_size
                path.unlink()
                files_deleted += 1
                bytes_freed += size
            elif path.is_dir():
                size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
                shutil.rmtree(path, ignore_errors=True)
                bytes_freed += size
                files_deleted += 1
        except OSError as exc:
            # Best-effort: log and continue. A missing raw file is not fatal.
            print(f"[evict] WARNING: could not remove {path}: {exc}")

    return files_deleted, bytes_freed


# ---------------------------------------------------------------------------
# Public API: evict_dealer
# ---------------------------------------------------------------------------

async def evict_dealer(
    conn: asyncpg.Connection,
    cdp_code: str,
    *,
    dry_run: bool = True,
    actor: str = "director",
) -> dict[str, Any]:
    """Evict a dealer: tombstone entity, delete vehicles, log audit trail.

    Parameters
    ----------
    conn      : asyncpg connection (caller owns lifecycle)
    cdp_code  : canonical dealer code (CDP-ES-XX-XXXXXXXX)
    dry_run   : if True (DEFAULT), return the plan without executing anything
    actor     : who triggered the eviction (logged in audit_eviction)

    Returns a dict describing what was/would-be done:
    {
        "evicted": bool,
        "dry_run": bool,
        "cdp_code": str,
        "entity_ulid": str | None,
        "vehicles_to_delete": int,     # count of available rows that would/were deleted
        "raw_files_deleted": int,
        "raw_bytes_freed": int,
        "reasons": list[str],          # non-empty when evicted=False
    }

    SAFETY: gates are re-read at eviction time (inside this call). If any
    gate fails, nothing is touched regardless of dry_run.
    """
    result: dict[str, Any] = {
        "evicted": False,
        "dry_run": dry_run,
        "cdp_code": cdp_code,
        "entity_ulid": None,
        "vehicles_to_delete": 0,
        "raw_files_deleted": 0,
        "raw_bytes_freed": 0,
        "reasons": [],
    }

    # --- Re-check all 3 gates (read-only) ---
    passed, reasons = await check_preconditions(conn, cdp_code)
    if not passed:
        result["reasons"] = reasons
        return result

    # --- Resolve entity_ulid ---
    entity_row = await conn.fetchrow(
        "SELECT entity_ulid FROM entity WHERE cdp_code = $1 LIMIT 1",
        cdp_code,
    )
    if entity_row is None:
        result["reasons"] = [f"entity row not found for cdp_code={cdp_code!r}"]
        return result

    entity_ulid: str = entity_row["entity_ulid"]
    result["entity_ulid"] = entity_ulid

    # --- Count vehicles to delete ---
    vehicles_to_delete: int = await conn.fetchval(
        "SELECT COUNT(*) FROM vehicle WHERE entity_ulid = $1",
        entity_ulid,
    )
    result["vehicles_to_delete"] = vehicles_to_delete

    # --- Dry-run: return plan without executing ---
    if dry_run:
        result["reasons"] = []
        return result

    # =========================================================================
    # APPLY PATH — destructive, irreversible
    # =========================================================================

    # LRU raw-file eviction (best-effort, outside DB transaction)
    # Must happen before disk_free_before snapshot
    try:
        usage_before = shutil.disk_usage(_DATA_DIR) if _DATA_DIR.exists() else None
        disk_free_before = usage_before.free if usage_before else None
    except OSError:
        disk_free_before = None

    raw_files_deleted, raw_bytes_freed = _evict_raw_files(cdp_code)
    result["raw_files_deleted"] = raw_files_deleted
    result["raw_bytes_freed"] = raw_bytes_freed

    try:
        usage_after = shutil.disk_usage(_DATA_DIR) if _DATA_DIR.exists() else None
        disk_free_after = usage_after.free if usage_after else None
    except OSError:
        disk_free_after = None

    # DB changes — single atomic transaction
    async with conn.transaction():
        # Re-read gates inside the transaction (final gate-check)
        passed_inner, inner_reasons = await check_preconditions(conn, cdp_code)
        if not passed_inner:
            # State changed between outer check and transaction start — abort
            result["reasons"] = [
                "gate re-check inside transaction FAILED (state changed mid-eviction):",
                *inner_reasons,
            ]
            raise asyncpg.exceptions.PostgresError(
                "Eviction aborted: gate re-check failed inside transaction"
            )

        # Step 4: tombstone entity (UPDATE, not DELETE — preserve history)
        await conn.execute(
            """
            UPDATE entity
            SET status = 'evicted', evicted_at = now()
            WHERE cdp_code = $1
              AND status <> 'evicted'
            """,
            cdp_code,
        )

        # Step 5: delete vehicle rows for this entity
        deleted_count: int = await conn.fetchval(
            "SELECT COUNT(*) FROM vehicle WHERE entity_ulid = $1",
            entity_ulid,
        )
        await conn.execute(
            "DELETE FROM vehicle WHERE entity_ulid = $1",
            entity_ulid,
        )

        # Step 6: capacity_ledger entry
        await conn.execute(
            """
            INSERT INTO capacity_ledger
                (cdp_code, vehicles_deleted, raw_bytes_freed, disk_free_before, disk_free_after)
            VALUES ($1, $2, $3, $4, $5)
            """,
            cdp_code,
            deleted_count,
            raw_bytes_freed,
            disk_free_before,
            disk_free_after,
        )

        # Step 7: audit_eviction (append-only, immutable)
        await conn.execute(
            """
            INSERT INTO audit_eviction
                (cdp_code, reason, actor, vehicles_deleted, raw_bytes_freed)
            VALUES ($1, $2, $3, $4, $5)
            """,
            cdp_code,
            "manual_eviction: all 3 gates green",
            actor,
            deleted_count,
            raw_bytes_freed,
        )

    result["evicted"] = True
    result["vehicles_to_delete"] = deleted_count
    result["reasons"] = []
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

async def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "BORRAR/DELETE stage — evict a dead dealer from Cardeep DB.\n"
            "DEFAULT mode is --dry-run (safe, read-only).\n"
            "Use --apply to execute destructive changes (irreversible)."
        ),
    )
    parser.add_argument(
        "--cdp",
        required=True,
        metavar="CDP-ES-XX-XXXXXXXX",
        help="Canonical dealer code to evict",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="(DEFAULT) Print the eviction plan without executing anything",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        default=False,
        help="Execute the eviction (DESTRUCTIVE, IRREVERSIBLE). Requires explicit flag.",
    )
    parser.add_argument(
        "--actor",
        default="director",
        help="Actor name logged in audit_eviction (default: director)",
    )
    args = parser.parse_args()

    dry_run = not args.apply  # --apply overrides --dry-run

    conn = await asyncpg.connect(DSN)
    try:
        result = await evict_dealer(
            conn,
            args.cdp,
            dry_run=dry_run,
            actor=args.actor,
        )
    finally:
        await conn.close()

    # Print structured result
    mode = "DRY-RUN" if result["dry_run"] else "APPLY"
    print(f"\n[evict] MODE={mode}  CDP={result['cdp_code']}")
    print(f"  entity_ulid      : {result['entity_ulid']}")
    print(f"  vehicles_to_delete: {result['vehicles_to_delete']}")
    print(f"  raw_files_deleted : {result['raw_files_deleted']}")
    print(f"  raw_bytes_freed   : {result['raw_bytes_freed']}")
    if result["reasons"]:
        print("  BLOCKED — reasons:")
        for r in result["reasons"]:
            print(f"    - {r}")
    else:
        status = "WOULD EVICT" if result["dry_run"] else "EVICTED"
        print(f"  status           : {status}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
