"""Re-verify REFUTED source_coverage rows to unblock reconcile_gone where warranted.

WHY THIS EXISTS
---------------
``pipeline.delta.reconcile_gone`` (delta.py:188-201) is the delta-baja gate: it refuses
to retire not-re-seen vehicles for a source whose ``source_coverage`` row reads
``verdict='REFUTED'`` (or coverage below the caller's floor, or no row). REFUTED is the
gate's "do not trust this harvest" signal — while it stands, that source's bajas are never
recorded and stale stock accumulates.

There are two REASONS a source ends up REFUTED, and they need OPPOSITE handling:

  (a) GENUINE UNDER-COVERAGE  (coverage_pct << floor): the harvest captured far fewer cars
      than the source DECLARES (incomplete pagination, mid-drain ban, keyword tail unreached).
      REFUTED is CORRECT here — "better a hole than a lie". Forcing it out of REFUTED would
      let reconcile_gone retire 80-93% of REAL, un-captured stock as false-GONE on the
      served, append-only timeline. The fix is to COMPLETE THE HARVEST, not to override the
      verdict. These STAY REFUTED and are documented.

  (b) STALE OVER-COVERAGE SEAL  (coverage_pct > ceiling): captured MORE than declared. Per
      coverage_verify.py B9 v2 (_COVERAGE_CEILING=1.15 + the over_coverage_unverified
      override, lines 235-253) over-coverage MUST seal as UNVERIFIED (scope mismatch /
      declared under-scoped), NOT REFUTED. A REFUTED over-coverage row is a stale PRE-B9v2
      seal that the CURRENT gate logic would no longer emit. Re-running the REAL gate
      (verify_coverage) re-seals it UNVERIFIED and unblocks reconcile_gone for its live
      cars — with zero data risk, because reconcile_gone only gates on ``== 'REFUTED'``.

WHAT THIS SCRIPT DOES (no fabricated verdicts, ever)
----------------------------------------------------
For every ``source_coverage`` row currently sealed REFUTED:
  1. Re-counts captured_db LIVE (the same orthogonal DB path verify_coverage uses) and
     recomputes coverage_pct against the declared_total ALREADY on the row (the source's
     own oracle figure from its last harvest — re-harvesting is FORBIDDEN by the task, so
     this is the only honest declared figure available).
  2. CLASSIFIES the row: OVER-coverage (safe to re-verify -> unblocks) vs UNDER-coverage
     (genuine -> stays REFUTED) vs IN-BAND (would clear).
  3. DRY-RUN (default): predicts the verdict the REAL gate would emit, writes NOTHING.
  4. --apply: calls the REAL ``pipeline.ops.coverage_verify.verify_coverage`` for each row.
     verify_coverage recounts captured_db itself, recomputes the verdict from REAL evidence
     (record_count_verdict quorum) and applies the B9v2 over-coverage override. The verdict
     is NEVER forced — the gate decides. Under-coverage rows therefore re-seal REFUTED on
     their own (correct), over-coverage rows re-seal UNVERIFIED (unblocked).

It does NOT touch a single vehicle row and does NOT run any harvest (verify_coverage is the
€0 gate: DB-only, no extra HTTP — coverage_verify.py:13). The spend-bearing rungs of
auto_repair are scaffolded behind the P10 gate, never executed here (health.py:390-398).

REVERSIBILITY
-------------
Each re-verify (a) INSERTs a new ``verification_verdict`` row and supersedes the prior one,
and (b) UPSERTs the single ``source_coverage`` row (PRIMARY KEY source_key). Before applying,
this script CAPTURES and LOGS, per source, the prior ``source_coverage.verdict`` +
``verdict_id`` (and the prior active verification_verdict id). Rollback of one source is:
  UPDATE source_coverage SET verdict=<prior_verdict>, verdict_id=<prior_verdict_id>
    WHERE source_key=<sk>;
  -- and, if the new verification_verdict row must be undone:
  DELETE FROM verification_verdict WHERE id=<new_id>;
  UPDATE verification_verdict SET superseded_by=NULL WHERE id=<prior_active_vv_id>;
No vehicle rows are written, so the served vehicle timeline is untouched regardless.

Usage:
    python scripts/reverify_refuted_sources.py                 # DRY-RUN (default): report only
    python scripts/reverify_refuted_sources.py --apply         # re-run the REAL gate, write
    python scripts/reverify_refuted_sources.py --apply --over-only
        # re-verify ONLY the safe over-coverage rows (leave genuine under-coverage frozen)
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncpg

from pipeline.ops.coverage_verify import _COVERAGE_CEILING, _DEFAULT_FLOOR, verify_coverage

DSN = os.environ.get(
    "CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
)

# Coverage band classification (mirrors coverage_verify.py exactly):
#   coverage_pct < floor            -> UNDER  : genuine incomplete harvest, REFUTED is correct.
#   coverage_pct > _COVERAGE_CEILING-> OVER   : scope mismatch, B9v2 -> UNVERIFIED (safe unblock).
#   floor <= coverage_pct <= ceiling-> IN_BAND: would clear to a converging verdict.
BAND_UNDER = "UNDER"
BAND_OVER = "OVER"
BAND_IN_BAND = "IN_BAND"


# ---------------------------------------------------------------------------
# Live evidence gathering (orthogonal to the harvest counter — DB-only, €0).
# ---------------------------------------------------------------------------

_CURRENT_REFUTED = """
SELECT source_key, declared_total, captured_db, db_edges, coverage_pct, verdict, verdict_id
  FROM source_coverage
 WHERE verdict = 'REFUTED'
 ORDER BY source_key
"""

# Same captured_db path verify_coverage uses (coverage_verify.py:133-139): distinct
# AVAILABLE vehicles attributed to this source via entity_source.  Re-counted live so the
# dry-run prediction matches what --apply would compute.
_RECOUNT_CAPTURED_DB = """
SELECT count(DISTINCT v.vehicle_ulid)
  FROM vehicle v
  JOIN entity_source es ON es.entity_ulid = v.entity_ulid
 WHERE v.status = 'available' AND es.source_key = $1
"""

# Live available / gone the source owns — to show the concrete reconcile_gone impact.
_SOURCE_STATUS = """
SELECT count(*) FILTER (WHERE v.status = 'available') AS available,
       count(*) FILTER (WHERE v.status = 'gone')      AS gone,
       count(DISTINCT es.entity_ulid)                 AS entities
  FROM entity_source es
  LEFT JOIN vehicle v ON v.entity_ulid = es.entity_ulid
 WHERE es.source_key = $1
"""

# Per-source coverage floor (verify_coverage reads this; we read it for the same classification).
_SOURCE_FLOOR = "SELECT coverage_floor FROM source_health WHERE source_key = $1"

# The platform entity for db_edges (verify_coverage's secondary fallback uses this exact query).
_PLATFORM_ULID = """
SELECT e.entity_ulid FROM entity e
  JOIN entity_source es ON es.entity_ulid = e.entity_ulid
 WHERE es.source_key = $1 AND e.kind = 'plataforma'
 LIMIT 1
"""

# Prior active verification_verdict id (for reversibility logging).
_PRIOR_ACTIVE_VV = """
SELECT id FROM verification_verdict
 WHERE subject_type = 'source_coverage' AND subject_key = $1 AND superseded_by IS NULL
 ORDER BY created_at DESC LIMIT 1
"""

# After-apply read-back of the now-active verdict (the new row).
_NEW_ACTIVE_VV = _PRIOR_ACTIVE_VV


def _classify(coverage_pct: float | None, floor: float) -> str:
    """Classify a coverage ratio into UNDER / OVER / IN_BAND (same bands as the gate)."""
    if coverage_pct is None:
        return BAND_UNDER  # no ratio -> cannot confirm completeness -> treat as under (frozen)
    if coverage_pct > _COVERAGE_CEILING:
        return BAND_OVER
    if coverage_pct < floor:
        return BAND_UNDER
    return BAND_IN_BAND


async def _gather(conn: asyncpg.Connection) -> list[dict]:
    """Read every currently-REFUTED source_coverage row and attach live evidence."""
    refuted = await conn.fetch(_CURRENT_REFUTED)
    out: list[dict] = []
    for r in refuted:
        sk = r["source_key"]
        declared = r["declared_total"]
        captured_live = await conn.fetchval(_RECOUNT_CAPTURED_DB, sk) or 0
        status = await conn.fetchrow(_SOURCE_STATUS, sk)
        floor_raw = await conn.fetchval(_SOURCE_FLOOR, sk)
        floor = float(floor_raw) if floor_raw is not None else _DEFAULT_FLOOR
        platform_ulid = await conn.fetchval(_PLATFORM_ULID, sk)
        prior_vv_id = await conn.fetchval(_PRIOR_ACTIVE_VV, sk)

        # Recompute coverage_pct from LIVE captured_db vs the recorded declared_total
        # (the source's oracle figure). This is what verify_coverage will compute on --apply.
        cov_live: float | None = (
            (captured_live / declared) if (declared and declared > 0) else None
        )
        band = _classify(cov_live, floor)
        out.append(
            {
                "source_key": sk,
                "declared_total": declared,
                "captured_db_recorded": r["captured_db"],
                "captured_db_live": captured_live,
                "coverage_pct_recorded": (
                    float(r["coverage_pct"]) if r["coverage_pct"] is not None else None
                ),
                "coverage_pct_live": cov_live,
                "floor": floor,
                "ceiling": _COVERAGE_CEILING,
                "band": band,
                "available": status["available"] if status else 0,
                "gone": status["gone"] if status else 0,
                "entities": status["entities"] if status else 0,
                "platform_ulid": platform_ulid,
                "prior_verdict": r["verdict"],
                "prior_verdict_id": r["verdict_id"],
                "prior_active_vv_id": prior_vv_id,
            }
        )
    return out


def _predict(rec: dict) -> str:
    """Predict the verdict the REAL gate would seal, WITHOUT writing.

    Mirrors coverage_verify.verify_coverage's override logic:
      - coverage_pct > ceiling -> UNVERIFIED (B9v2 over_coverage_unverified override).
      - coverage_pct < floor   -> the under-coverage path; record_count_verdict sees
        captured_db vs declared diverge beyond tolerance=(1-floor) -> REFUTED.
      - in-band                -> converging; UNVERIFIED/TRUSTWORTHY (the row clears REFUTED).
    We only need to know whether the row LEAVES 'REFUTED' (== unblocks reconcile_gone),
    so the exact in-band sub-verdict (UNVERIFIED vs TRUSTWORTHY) is reported as 'NOT REFUTED'.
    """
    band = rec["band"]
    if band == BAND_OVER:
        return "UNVERIFIED"          # leaves REFUTED -> UNBLOCKS
    if band == BAND_IN_BAND:
        return "NOT REFUTED"         # leaves REFUTED -> UNBLOCKS
    return "REFUTED"                 # stays frozen (genuine under-coverage)


def _print_report(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """Print the classification table. Returns (safe_to_reverify, genuine_frozen)."""
    print("=" * 100)
    print("REFUTED source_coverage rows (what reconcile_gone is blocked on — delta.py:199)")
    print("=" * 100)
    if not records:
        print("  (none — no source is currently blocked by a REFUTED coverage verdict.)")
        return [], []

    safe: list[dict] = []
    frozen: list[dict] = []
    for rec in records:
        predicted = _predict(rec)
        cov_live = rec["coverage_pct_live"]
        cov_str = f"{cov_live:.4f}" if cov_live is not None else "None"
        action = (
            "RE-VERIFY -> UNBLOCKS"
            if predicted != "REFUTED"
            else "STAYS REFUTED (frozen)"
        )
        print(
            f"\n  source_key      : {rec['source_key']}"
            f"\n    band          : {rec['band']}"
            f"\n    declared      : {rec['declared_total']}"
            f"  captured_db(rec): {rec['captured_db_recorded']}"
            f"  captured_db(live): {rec['captured_db_live']}"
            f"\n    cov(recorded) : {rec['coverage_pct_recorded']}"
            f"  cov(live): {cov_str}"
            f"  floor: {rec['floor']}  ceiling: {rec['ceiling']}"
            f"\n    live stock    : available={rec['available']}  gone={rec['gone']}"
            f"  entities={rec['entities']}  (all bajas frozen while REFUTED)"
            f"\n    prior verdict : {rec['prior_verdict']} (verdict_id={rec['prior_verdict_id']},"
            f" active_vv_id={rec['prior_active_vv_id']})"
            f"\n    predicted     : {predicted}   => {action}"
        )
        if predicted != "REFUTED":
            safe.append(rec)
        else:
            frozen.append(rec)

    print("\n" + "-" * 100)
    print(f"  SAFE to re-verify (over-coverage / in-band -> unblocks): {len(safe)}")
    print(f"  GENUINE under-coverage (STAY REFUTED — fix the harvest): {len(frozen)}")
    return safe, frozen


def _print_frozen_doc(frozen: list[dict]) -> None:
    """Emit the NOT-VALIDATED.md documentation block for genuine partials.

    This script owns ONLY itself, so it does not write docs/runbook/NOT-VALIDATED.md.
    It prints the exact block to paste/record there per the design (document, do NOT force).
    """
    if not frozen:
        return
    print("\n" + "=" * 100)
    print("DOCUMENT (do NOT force) — paste into docs/runbook/NOT-VALIDATED.md")
    print("=" * 100)
    print(
        "## reconcile_gone bajas intentionally FROZEN (REFUTED coverage)\n"
        "\n"
        "These sources captured far fewer vehicles than they DECLARE. Their coverage verdict is\n"
        "REFUTED on purpose: reconcile_gone refuses to retire not-re-seen vehicles for them,\n"
        "because most 'not re-seen' rows are UN-CAPTURED, not GONE. Forcing the verdict would\n"
        "retire real stock as false-GONE on the served timeline. UNFREEZE = COMPLETE THE\n"
        "HARVEST (full pagination / lift the ban / reach the tail) until captured/declared >=\n"
        "floor; the next coverage_verify run then re-seals the verdict automatically. The\n"
        "REFUTED here is a FEATURE, not a bug.\n"
    )
    for rec in frozen:
        cov = rec["coverage_pct_live"]
        cov_str = f"{cov:.1%}" if cov is not None else "n/a"
        print(
            f"- {rec['source_key']}: captured {rec['captured_db_live']} / declared "
            f"{rec['declared_total']} = {cov_str} (floor {rec['floor']:.0%}). "
            f"Live available={rec['available']}, gone={rec['gone']} (bajas frozen)."
        )


async def _reverify_one(conn: asyncpg.Connection, rec: dict) -> dict:
    """Call the REAL gate for one source. Never forces a verdict — verify_coverage decides.

    verify_coverage opens its OWN transaction for the verdict + UPSERT writes, so it must be
    called on a connection that is NOT inside an open transaction (coverage_verify.py:92-93).
    We therefore call it per-source on a plain connection (no surrounding transaction).
    """
    await verify_coverage(
        conn,
        rec["source_key"],
        declared_total=rec["declared_total"],     # the source's recorded oracle figure
        platform_ulid=rec["platform_ulid"],       # exact db_edges path when present
        phase="reverify",
    )
    # Read back the now-active verdict + the new source_coverage seal for the report/rollback log.
    new_vv_id = await conn.fetchval(_NEW_ACTIVE_VV, rec["source_key"])
    sc = await conn.fetchrow(
        "SELECT verdict, verdict_id, coverage_pct FROM source_coverage WHERE source_key = $1",
        rec["source_key"],
    )
    return {
        "source_key": rec["source_key"],
        "new_verdict": sc["verdict"] if sc else None,
        "new_verdict_id": sc["verdict_id"] if sc else None,
        "new_coverage_pct": float(sc["coverage_pct"]) if sc and sc["coverage_pct"] is not None else None,
        "new_active_vv_id": new_vv_id,
        "prior_verdict": rec["prior_verdict"],
        "prior_verdict_id": rec["prior_verdict_id"],
        "prior_active_vv_id": rec["prior_active_vv_id"],
    }


def _print_rollback(results: list[dict]) -> None:
    """Print the per-source reversibility log (exact rollback SQL)."""
    if not results:
        return
    print("\n" + "=" * 100)
    print("REVERSIBILITY LOG (rollback SQL per source — no vehicle row was touched)")
    print("=" * 100)
    for r in results:
        changed = r["new_verdict"] != r["prior_verdict"]
        flag = "CHANGED" if changed else "unchanged"
        print(
            f"\n  {r['source_key']}: {r['prior_verdict']} -> {r['new_verdict']} [{flag}]"
            f"\n    -- restore source_coverage seal:"
            f"\n    UPDATE source_coverage SET verdict='{r['prior_verdict']}', "
            f"verdict_id={r['prior_verdict_id']} WHERE source_key='{r['source_key']}';"
        )
        if r["new_active_vv_id"] and r["new_active_vv_id"] != r["prior_active_vv_id"]:
            print(
                f"    -- undo the new verification_verdict row:"
                f"\n    DELETE FROM verification_verdict WHERE id={r['new_active_vv_id']};"
            )
            if r["prior_active_vv_id"]:
                print(
                    f"    UPDATE verification_verdict SET superseded_by=NULL "
                    f"WHERE id={r['prior_active_vv_id']};"
                )


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Re-verify REFUTED source_coverage rows to unblock reconcile_gone where warranted."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute the REAL gate (verify_coverage) and write. Default is dry-run (report only).",
    )
    parser.add_argument(
        "--over-only",
        action="store_true",
        help="On --apply, re-verify ONLY safe over-coverage/in-band rows; leave genuine "
        "under-coverage REFUTED frozen. (Under-coverage re-verify re-seals REFUTED anyway, "
        "but --over-only avoids even touching their timeline.)",
    )
    args = parser.parse_args()

    conn = await asyncpg.connect(DSN)
    try:
        records = await _gather(conn)
        safe, frozen = _print_report(records)
        _print_frozen_doc(frozen)

        if not args.apply:
            print("\n" + "=" * 100)
            print(
                "DRY-RUN (default) — no writes. The REAL gate decides every verdict; nothing is forced.\n"
                "Re-run with --apply to execute verify_coverage for the rows above.\n"
                "  --apply            : re-verify ALL refuted rows (under-coverage re-seals REFUTED on its own)\n"
                "  --apply --over-only: re-verify ONLY the safe over-coverage/in-band rows"
            )
            return

        # --apply: choose the target set. Under-coverage rows are safe to re-verify (the gate
        # re-seals them REFUTED honestly), but --over-only lets the operator avoid even writing
        # a fresh (identical) REFUTED verdict for them.
        targets = safe if args.over_only else records
        if args.over_only:
            print(
                f"\n--over-only: re-verifying {len(targets)} safe row(s); leaving "
                f"{len(frozen)} genuine under-coverage row(s) frozen."
            )
        else:
            print(f"\n--apply: re-verifying ALL {len(targets)} refuted row(s) via the real gate.")

        results: list[dict] = []
        for rec in targets:
            res = await _reverify_one(conn, rec)
            results.append(res)
            verdict_now = res["new_verdict"]
            unblocked = "UNBLOCKED" if verdict_now != "REFUTED" else "still REFUTED (correct)"
            print(
                f"  {res['source_key']:32} {res['prior_verdict']} -> {verdict_now}"
                f"  (cov={res['new_coverage_pct']})  reconcile_gone: {unblocked}"
            )

        _print_rollback(results)

        # Final ground-truth read-back: how many sources remain blocked by REFUTED.
        still = await conn.fetchval(
            "SELECT count(*) FROM source_coverage WHERE verdict = 'REFUTED'"
        )
        print(
            f"\nAPPLIED. source_coverage rows still REFUTED (reconcile_gone still blocked): {still}"
        )
        print(
            "  (Genuine under-coverage rows SHOULD remain REFUTED — that is the gate working, "
            "not a failure. Unfreeze them only by completing their harvest.)"
        )
    finally:
        await conn.close()


if __name__ == "__main__":
    # Force UTF-8 stdout so the report renders correctly on a Windows console whose default
    # codepage (cp1252) would otherwise mangle '€', em-dashes and arrows. No-op on UTF-8 hosts.
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass
    asyncio.run(main())
