"""Self-verifying €0 backfill of entity.municipality_code for the geo-resolvable gap (audit P2 SU-A6).

The muni-gap is 6,777 non-particular entities with NULL municipality_code. Of these, ~141 carry a €0
geo signal (30 with lat/lon, 111 with an unambiguous postcode); the other ~6,636 have NO geo signal and
are genuinely DATA-blocked (need Overture/external geocoding — out of €0 scope).

This resolves ONLY the €0-signal subset, using the local geocoders (no network, no spend):
  - lat/lon  -> MunicipalityGeocoder (KNN over geo_municipality centroids, province-constrained,
               rejects matches beyond KNN_MAX_DISTANCE_KM → "better a hole than a lie")
  - postcode -> PostcodeIndex (INE Nomenclátor; ambiguous postcodes return None → no lie)

SELF-VERIFYING: a resolved code is written ONLY when it (a) exists in geo_municipality and (b) its
province prefix matches the entity's province_code. A non-matching/invalid resolution is skipped (NULL
stays NULL — a wrong municipality is never written). MVCC-clean: only NULL→value UPDATEs.

Run:  python scripts/backfill_municipality_geo.py            # dry-run (report, no writes)
      python scripts/backfill_municipality_geo.py --apply
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import asyncpg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.geocode import MunicipalityGeocoder, PostcodeIndex

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

_SELECT = """
SELECT entity_ulid, province_code, lat, lon, postcode
  FROM entity
 WHERE municipality_code IS NULL AND kind <> 'particular' AND province_code IS NOT NULL
   AND (postcode IS NOT NULL OR (lat IS NOT NULL AND lon IS NOT NULL))
"""


async def main(apply: bool) -> None:
    conn = await asyncpg.connect(DSN)
    try:
        geo = await MunicipalityGeocoder.load(conn)
        cp = PostcodeIndex.load()
        # Valid municipality codes (for the self-verify gate) — pull once.
        valid = {r["code"] for r in await conn.fetch("SELECT code FROM geo_municipality")}

        rows = await conn.fetch(_SELECT)
        updates: list[tuple[str, str]] = []
        by_method = {"latlon": 0, "postcode": 0}
        skipped = {"latlon_far_or_none": 0, "postcode_ambiguous_or_unknown": 0,
                   "resolved_invalid_or_wrong_province": 0}
        for r in rows:
            prov = r["province_code"]
            code: str | None = None
            method = None
            if r["lat"] is not None and r["lon"] is not None:
                code, dist = geo.nearest_municipality(r["lat"], r["lon"], prov)
                if code is not None:
                    method = "latlon"
                else:
                    skipped["latlon_far_or_none"] += 1
            if code is None and r["postcode"]:
                code = cp.resolve(r["postcode"])
                if code is not None:
                    method = "postcode"
                elif r["lat"] is None:
                    skipped["postcode_ambiguous_or_unknown"] += 1
            if code is None:
                continue
            # SELF-VERIFY gate: code must be a real municipality AND belong to the entity's province.
            if code not in valid or code[:2] != prov:
                skipped["resolved_invalid_or_wrong_province"] += 1
                continue
            updates.append((code, r["entity_ulid"]))
            by_method[method] += 1

        if apply and updates:
            await conn.executemany(
                "UPDATE entity SET municipality_code=$1 "
                "WHERE entity_ulid=$2 AND municipality_code IS NULL",
                updates)

        print(f"resolvable rows scanned (NULL muni, non-particular, has geo signal): {len(rows)}")
        print(f"resolved + self-verified: {len(updates)}  (latlon {by_method['latlon']}, "
              f"postcode {by_method['postcode']})")
        print(f"skipped: {skipped}")
        if apply:
            remaining = await conn.fetchval(
                "SELECT count(*) FROM entity WHERE municipality_code IS NULL AND kind<>'particular'")
            print(f"APPLIED. muni-gap (non-particular) now {remaining} "
                  f"(was 6777; {6777 - remaining} filled; rest = no-geo-signal DATA-blocked).")
        else:
            print("DRY-RUN — no writes.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main(apply="--apply" in sys.argv))
