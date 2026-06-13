"""Re-classify confirmed IMPORT OPERATORS miscataloged as compraventa -> kind='importador'.

The keyword census (docs/research/KEYWORD_CHANNEL_MAP.md §NUEVO-3) found two operators that were
discovered through marketplaces (coches.net, milanuncios, autocasion, motor.es, wallapop) and caged
as kind='compraventa', but whose OWN SITE proves they are IMPORTADORES (German-import dealers):

  * TrendCars  (trendcars.es)  — verified live 2026-06-13: title "Compra tu coche de segunda mano
    online, importación o nacional"; 30 import mentions on the home page. Province 28 (San Sebastián
    de los Reyes, muni 28123).
  * Carismatic (carismatic.es) — verified live 2026-06-13: 48 import mentions on the home page.
    Province 03 (Elche, muni 03065).

The kind on these entities is the ONLY thing wrong — their cars, edges, geo and codes are correct.
This script flips kind='compraventa' -> kind='importador' on exactly those entities, identified by a
strict name match scoped to their known provinces, and ONLY when the row is currently compraventa
(idempotent: a second run flips 0). It NEVER merges, deletes, or moves cars — fully reversible (the
inverse is one UPDATE back to compraventa). kind_source is set to 'manual' (a deliberate, evidence-
backed operator decision from the keyword census — the kind_source enum's honest fit for a human-
authored re-classification, distinct from the automated 'classifier' rung).

Run: python -m scripts.reclassify_importadores            # apply
     python -m scripts.reclassify_importadores --dry-run  # preview only
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys

import asyncpg

DSN = os.environ.get("CARDEEP_DSN",
                     "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# Each target: the strict name predicate + the province it MUST be in (so a same-named unrelated
# dealer elsewhere is never swept in). Both verified importadores on their own site 2026-06-13.
TARGETS = [
    {"label": "TrendCars (trendcars.es)",
     "name_like": ["%trendcars%", "%trend cars%"],
     "province": "28"},
    {"label": "Carismatic (carismatic.es)",
     "name_like": ["%carismatic%"],
     "province": "03"},
]


async def reclassify(dry_run: bool) -> dict:
    conn = await asyncpg.connect(DSN)
    summary = {"targets": [], "total_flipped": 0, "kind_before": None, "kind_after": None}
    try:
        before = await conn.fetchval("SELECT count(*) FROM entity WHERE kind='importador'")
        summary["kind_before"] = before
        for t in TARGETS:
            # find the CURRENTLY-compraventa rows that match this importer in its province.
            name_clauses = " OR ".join(
                f"lower(legal_name) LIKE ${i+2} OR lower(trade_name) LIKE ${i+2}"
                for i in range(len(t["name_like"])))
            params = [t["province"], *[p.lower() for p in t["name_like"]]]
            rows = await conn.fetch(
                f"""SELECT entity_ulid, cdp_code, legal_name, kind::text AS kind,
                        (SELECT count(*) FROM vehicle v WHERE v.entity_ulid=e.entity_ulid) AS vehicles,
                        (SELECT count(*) FROM platform_listing pl
                           JOIN vehicle v ON v.vehicle_ulid=pl.vehicle_ulid
                          WHERE v.entity_ulid=e.entity_ulid) AS edges
                   FROM entity e
                  WHERE province_code = $1 AND kind = 'compraventa' AND ({name_clauses})
                  ORDER BY cdp_code""",
                *params)
            flipped = []
            for r in rows:
                flipped.append({"cdp_code": r["cdp_code"], "legal_name": r["legal_name"],
                                "vehicles": r["vehicles"], "edges": r["edges"]})
                if not dry_run:
                    # flip ONLY the kind + provenance; cars/edges/geo/codes untouched. Idempotent
                    # via the kind='compraventa' guard in the WHERE (a re-run matches 0 rows).
                    await conn.execute(
                        "UPDATE entity SET kind='importador'::entity_kind, "
                        "kind_source='manual'::kind_source, last_seen=now() "
                        "WHERE entity_ulid=$1 AND kind='compraventa'",
                        r["entity_ulid"])
            summary["targets"].append({"label": t["label"], "matched": len(rows),
                                       "rows": flipped})
            summary["total_flipped"] += len(rows)
        after = await conn.fetchval("SELECT count(*) FROM entity WHERE kind='importador'")
        summary["kind_after"] = after
        return summary
    finally:
        await conn.close()


def _print(summary: dict, dry_run: bool) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass
    print("=" * 64)
    print(f"RECLASSIFY IMPORTADORES — {'DRY RUN (no writes)' if dry_run else 'APPLIED'}")
    print("=" * 64)
    print(f"  kind=importador before : {summary['kind_before']}")
    for t in summary["targets"]:
        print(f"  {t['label']}: {t['matched']} compraventa row(s) "
              f"{'to flip' if dry_run else 'flipped'} -> importador")
        for r in t["rows"]:
            print(f"      {r['cdp_code']} | {r['legal_name'][:42]:42} | "
                  f"veh={r['vehicles']} edges={r['edges']}")
    print(f"  total {'would flip' if dry_run else 'flipped'} : {summary['total_flipped']}")
    print(f"  kind=importador after  : {summary['kind_after']}")
    print("=" * 64)


def main() -> None:
    parser = argparse.ArgumentParser(description="Re-classify confirmed importadores compraventa->importador")
    parser.add_argument("--dry-run", action="store_true", help="preview matches without writing")
    args = parser.parse_args()
    summary = asyncio.run(reclassify(args.dry_run))
    _print(summary, args.dry_run)


if __name__ == "__main__":
    main()
