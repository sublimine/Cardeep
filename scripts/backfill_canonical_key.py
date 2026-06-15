"""Self-verifying backfill of entity.canonical_key (audit P2 B-canonical-key-column-empty).

entity.canonical_key is 100% NULL: codes.cdp_code() computes the dedup pre-image key then throws it
away. cdp_pair() now exposes it. This recovers the key for EXISTING rows by recomputing candidate keys
from STORED inputs and writing canonical_key ONLY when the recompute re-hashes to the row's stored
cdp_code — a non-matching recompute leaves it NULL (a WRONG key is impossible to write; the hash is the
witness). NULL-province + subasta rows are skipped (cdp_code requires province_code).

Particulars (~330k) are verified-recoverable (calibrated: coches.net seller_id=province; ml/wp
seller_id=source_ref). Dealers are best-effort (municipality_code/name are mutable post-mint, so the
recompute may not match — that's SAFE, just lower coverage). Coverage is reported, not pre-promised.

Run:  python scripts/backfill_canonical_key.py            # dry-run (coverage report, no writes)
      python scripts/backfill_canonical_key.py --apply
"""
from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

import asyncpg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from services.api.codes import cdp_pair

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

# source_key -> the particular_platform token canonical_key() normalizes.
_PARTICULAR_PLAT = {
    "coches_net_wholesale": "coches.net",
    "milanuncios_wholesale": "milanuncios",
    "wallapop_wholesale": "wallapop",
}

_SELECT = """
SELECT e.entity_ulid, e.cdp_code, e.kind::text AS kind, e.province_code, e.municipality_code,
       e.trade_name, e.legal_name, e.website, e.cif, e.address,
       es.source_key, es.source_ref
  FROM entity e
  LEFT JOIN LATERAL (
        SELECT source_key, source_ref FROM entity_source
         WHERE entity_ulid = e.entity_ulid ORDER BY seen_at ASC LIMIT 1) es ON true
 WHERE e.canonical_key IS NULL AND e.province_code IS NOT NULL
"""


def _candidate_kwargs(row):
    """Yield candidate cdp_pair kwargs for a row, in priority order. The re-hash gate decides."""
    prov = row["province_code"]
    if row["kind"] == "particular":
        plat = _PARTICULAR_PLAT.get(row["source_key"])
        if plat:
            sid = prov if plat == "coches.net" else row["source_ref"]
            if sid:
                yield {"province_code": prov, "particular_platform": plat,
                       "particular_seller_id": str(sid)}
        return
    # Dealer (compraventa/garaje/desguace/concesionario): try every variant; gate keeps only matches.
    name = row["trade_name"] or row["legal_name"]
    muni = row["municipality_code"]
    sref = row["source_ref"]
    if row["website"]:
        yield {"province_code": prov, "domain": row["website"]}            # -> domain:host (if bare)
    if row["cif"]:
        yield {"province_code": prov, "cif": row["cif"]}
    if name and muni:
        yield {"province_code": prov, "name": name, "municipality_code": muni}
        if sref:
            yield {"province_code": prov, "name": name, "municipality_code": muni,
                   "address": f"contract:{sref}"}
            yield {"province_code": prov, "name": name, "municipality_code": muni,
                   "address": f"wallapop_user:{sref}"}
    if name:
        yield {"province_code": prov, "name": name}                        # -> name|pPROV


async def main(apply: bool) -> None:
    conn = await asyncpg.connect(DSN)
    try:
        rows = await conn.fetch(_SELECT)
        matched, by_kind, updates = 0, {}, []
        for row in rows:
            for kw in _candidate_kwargs(row):
                try:
                    key, code = cdp_pair(**kw)
                except (ValueError, TypeError):
                    continue
                if code == row["cdp_code"]:               # THE gate — re-hash must match stored code
                    updates.append((key, row["entity_ulid"]))
                    matched += 1
                    by_kind[row["kind"]] = by_kind.get(row["kind"], 0) + 1
                    break
        if apply and updates:
            await conn.executemany(
                "UPDATE entity SET canonical_key=$1 WHERE entity_ulid=$2 AND canonical_key IS NULL",
                updates)
        total = await conn.fetchval("SELECT count(*) FROM entity")
        filled_before = await conn.fetchval("SELECT count(canonical_key) FROM entity")
        print(f"NULL-canonical_key rows scanned (province NOT NULL): {len(rows)}")
        print(f"gate-matched (recompute == stored cdp_code): {matched}")
        for k, n in sorted(by_kind.items(), key=lambda x: -x[1]):
            print(f"    {k:22} {n}")
        if apply:
            filled_after = await conn.fetchval("SELECT count(canonical_key) FROM entity")
            print(f"\nAPPLIED. canonical_key filled {filled_before} -> {filled_after} of {total} "
                  f"({total - filled_after} still NULL: NULL-province + non-matching dealers + subasta).")
        else:
            print(f"\nDRY-RUN — no writes. {matched} would fill of {total} (filled now {filled_before}).")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main(apply="--apply" in sys.argv))
