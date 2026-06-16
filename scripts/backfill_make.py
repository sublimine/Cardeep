"""Backfill canonical make (audit P2 A-make-model-null-parse).

Two set-based passes using the canonical brand map (pipeline.identity.make_normalizer._CANON):
  1. NULL-RECOVERY  — vehicles with make IS NULL whose title's leading token is a known brand:
                      set make = canonical (model left NULL; title→model is too error-prone).
  2. CASING-CONSOLIDATION — vehicles whose make is a known brand in a non-canonical casing
                      (VOLKSWAGEN/Volkswagen → Volkswagen): collapse to the one canonical form.

Unknown brands are never touched (Law I: never guess). The durable prevention is normalize_make()
wired into pipeline/ingest.py (future writes are canonical); this backfill cleans the existing rows.

Run:  python scripts/backfill_make.py            # dry-run (counts + samples, no writes)
      python scripts/backfill_make.py --apply     # execute both passes
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import asyncpg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.identity.make_normalizer import _CANON

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

_MAP_VALUES = ",".join(f"('{k}','{c}')" for k, c in _CANON.items())  # keys/values are brand literals, no quotes

_NULL_RECOVERY_COUNT = f"""
SELECT count(*) FROM vehicle v
JOIN (VALUES {_MAP_VALUES}) m(k,c) ON lower(split_part(btrim(v.title),' ',1)) = m.k
WHERE v.make IS NULL AND v.title IS NOT NULL
"""
_CASING_COUNT = f"""
SELECT count(*) FROM vehicle v
JOIN (VALUES {_MAP_VALUES}) m(k,c) ON lower(v.make) = m.k
WHERE v.make IS NOT NULL AND v.make <> m.c
"""

# Pass 3 — MODEL-AS-MAKE RECOVERY (audit pass-4 D2): make is non-NULL but NOT a known brand
# (e.g. wallapop user typed a MODEL 'Golf' in the 'brand' field), and the title leads with a known
# brand -> set make = the title's brand. Mirrors normalize_make()'s Option-C policy: the title's
# leading-token brand is authoritative over a non-brand make. NOT EXISTS guard ensures we never
# touch a make that IS already a known brand (those are handled by the casing pass).
_MODEL_AS_MAKE_COUNT = f"""
SELECT count(*) FROM vehicle v
JOIN (VALUES {_MAP_VALUES}) m(k,c) ON lower(split_part(btrim(v.title),' ',1)) = m.k
WHERE v.make IS NOT NULL AND v.title IS NOT NULL AND v.make <> m.c
  AND NOT EXISTS (SELECT 1 FROM (VALUES {_MAP_VALUES}) m2(k2,c2) WHERE m2.k2 = lower(btrim(v.make)))
"""


async def main(apply: bool) -> None:
    conn = await asyncpg.connect(DSN)
    try:
        null_n = await conn.fetchval(_NULL_RECOVERY_COUNT)
        casing_n = await conn.fetchval(_CASING_COUNT)
        model_n = await conn.fetchval(_MODEL_AS_MAKE_COUNT)
        print(f"NULL-recovery candidates      : {null_n}")
        print(f"casing-consolidation candidates: {casing_n}")
        print(f"model-as-make candidates       : {model_n}")
        # Sample the null-recovery to eyeball precision (no false extractions).
        sample = await conn.fetch(f"""
            SELECT left(v.title,46) AS title, m.c AS would_set
            FROM vehicle v JOIN (VALUES {_MAP_VALUES}) m(k,c)
              ON lower(split_part(btrim(v.title),' ',1)) = m.k
            WHERE v.make IS NULL AND v.title IS NOT NULL LIMIT 8""")
        print("  null-recovery sample (title -> make):")
        for r in sample:
            print(f"    {r['title']!r:50} -> {r['would_set']}")

        msample = await conn.fetch(f"""
            SELECT v.make AS old_make, left(v.title,44) AS title, m.c AS would_set
            FROM vehicle v JOIN (VALUES {_MAP_VALUES}) m(k,c)
              ON lower(split_part(btrim(v.title),' ',1)) = m.k
            WHERE v.make IS NOT NULL AND v.title IS NOT NULL AND v.make <> m.c
              AND NOT EXISTS (SELECT 1 FROM (VALUES {_MAP_VALUES}) m2(k2,c2) WHERE m2.k2 = lower(btrim(v.make)))
            LIMIT 8""")
        print("  model-as-make sample (old_make | title -> make):")
        for r in msample:
            print(f"    {r['old_make']!r:14} | {r['title']!r:46} -> {r['would_set']}")

        if not apply:
            print("\nDRY-RUN — no writes. Re-run with --apply.")
            return

        # Inline VALUES (no temp table) — each UPDATE autocommits independently (safer for a
        # one-shot: the null-recovery commits before the casing pass starts).
        nr = await conn.execute(
            f"UPDATE vehicle v SET make = m.c FROM (VALUES {_MAP_VALUES}) m(k,c) "
            "WHERE v.make IS NULL AND v.title IS NOT NULL "
            "AND lower(split_part(btrim(v.title),' ',1)) = m.k")
        cc = await conn.execute(
            f"UPDATE vehicle v SET make = m.c FROM (VALUES {_MAP_VALUES}) m(k,c) "
            "WHERE v.make IS NOT NULL AND lower(v.make) = m.k AND v.make <> m.c")
        mam = await conn.execute(
            f"UPDATE vehicle v SET make = m.c FROM (VALUES {_MAP_VALUES}) m(k,c) "
            "WHERE v.make IS NOT NULL AND v.title IS NOT NULL "
            "AND lower(split_part(btrim(v.title),' ',1)) = m.k AND v.make <> m.c "
            f"AND NOT EXISTS (SELECT 1 FROM (VALUES {_MAP_VALUES}) m2(k2,c2) WHERE m2.k2 = lower(btrim(v.make)))")
        print(f"\nAPPLIED. null-recovery: {nr} | casing-consolidation: {cc} | model-as-make: {mam}")
        remaining = await conn.fetchval(
            "SELECT count(*) FROM vehicle WHERE make IS NULL AND model IS NULL")
        print(f"both-null remaining: {remaining}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main(apply="--apply" in sys.argv))
