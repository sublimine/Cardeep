"""Self-verifying canonical_key forward-coverage (audit P2 B-canonical-key, forward-write portion).

entity.canonical_key is the AUDIT pre-image of cdp_code (migrations/0006 "the exact key cdp_code
hashed (audit)"); it is exposed by servable_entity for forensics but is NOT a hot-path dedup key —
cdp_code (the UNIQUE hash) is, and it is always set at INSERT. So canonical_key may be filled lazily.

Rather than thread cdp_pair() through ~70 hand-rolled `INSERT INTO entity` sites across ~40
connectors (immediate consistency with zero functional benefit for an audit column, at 70x the
risk), this is the single central, eventually-consistent mechanism: recompute the candidate key from
each row's STORED inputs and write canonical_key ONLY when the recompute re-hashes to the row's
stored cdp_code. A non-matching recompute leaves it NULL — a WRONG key is impossible to write (the
hash is the witness). Particulars are calibrated-recoverable; dealers are best-effort (mutable
municipality/name may not re-match — SAFE, just lower coverage). Run as a scheduler cadence
(pipeline/ops/scheduler.py canonical_key_backfill_job) so NEW entities are covered automatically.
"""
from __future__ import annotations

import asyncpg

from services.api.codes import cdp_pair

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


def candidate_kwargs(row):
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
    # Dealer (compraventa/garaje/desguace/concesionario): try every variant; the gate keeps matches.
    name = row["trade_name"] or row["legal_name"]
    muni = row["municipality_code"]
    sref = row["source_ref"]
    if row["website"]:
        yield {"province_code": prov, "domain": row["website"]}
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
        yield {"province_code": prov, "name": name}


async def backfill_canonical_keys(conn: asyncpg.Connection, *, apply: bool = True) -> dict:
    """Recompute + gate-write canonical_key for every NULL-canonical_key row (province NOT NULL).

    Writes canonical_key ONLY when a recomputed candidate re-hashes to the row's stored cdp_code
    (a wrong key cannot be written). Returns a summary dict {scanned, matched, by_kind, applied}.
    Idempotent: a second run finds only rows still NULL (the just-filled ones drop out of _SELECT).
    """
    rows = await conn.fetch(_SELECT)
    matched = 0
    by_kind: dict[str, int] = {}
    updates: list[tuple[str, str]] = []
    for row in rows:
        for kw in candidate_kwargs(row):
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
    return {"scanned": len(rows), "matched": matched, "by_kind": by_kind,
            "applied": bool(apply and updates)}
