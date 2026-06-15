"""CLI for the self-verifying canonical_key backfill (audit P2 B-canonical-key).

The recompute-and-gate logic lives in pipeline/identity/canonical_key_backfill.py (so the scheduler's
canonical_key_backfill_job can run the same code in-process). This is the operator CLI + reporting.

entity.canonical_key is the AUDIT pre-image of cdp_code: codes.cdp_code() computes the dedup pre-image
key then throws it away; cdp_pair() now exposes it. This recovers the key for rows where the recompute
re-hashes to the row's stored cdp_code — a non-matching recompute leaves it NULL (a WRONG key is
impossible to write; the hash is the witness). NULL-province + subasta rows are skipped.

Run:  python scripts/backfill_canonical_key.py            # dry-run (coverage report, no writes)
      python scripts/backfill_canonical_key.py --apply
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import asyncpg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.identity.canonical_key_backfill import backfill_canonical_keys

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"


async def main(apply: bool) -> None:
    conn = await asyncpg.connect(DSN)
    try:
        total = await conn.fetchval("SELECT count(*) FROM entity")
        filled_before = await conn.fetchval("SELECT count(canonical_key) FROM entity")
        summary = await backfill_canonical_keys(conn, apply=apply)
        print(f"NULL-canonical_key rows scanned (province NOT NULL): {summary['scanned']}")
        print(f"gate-matched (recompute == stored cdp_code): {summary['matched']}")
        for k, n in sorted(summary["by_kind"].items(), key=lambda x: -x[1]):
            print(f"    {k:22} {n}")
        if apply:
            filled_after = await conn.fetchval("SELECT count(canonical_key) FROM entity")
            print(f"\nAPPLIED. canonical_key filled {filled_before} -> {filled_after} of {total} "
                  f"({total - filled_after} still NULL: NULL-province + non-matching dealers + subasta).")
        else:
            print(f"\nDRY-RUN — no writes. {summary['matched']} would fill of {total} "
                  f"(filled now {filled_before}).")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main(apply="--apply" in sys.argv))
