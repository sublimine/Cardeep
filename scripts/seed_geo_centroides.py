"""Seed centroid lat/lon into geo_municipality from the bundled CSV.

Source: data/geo/municipios_centroides.csv
        (PopulateTools/ine-places, MIT-compatible, derived from official INE data)
        8,119 of 8,132 municipalities. The 13 remaining are recently created /
        split municipalities not yet in the upstream dataset; they keep lat = NULL.

Idempotent: only UPDATEs rows where the CSV value differs from what is already
stored (PG MVCC doctrine — no UPDATE of genuinely-non-mutated rows).

Usage:
    python -m scripts.seed_geo_centroides
"""
from __future__ import annotations

import asyncio
import csv
import os
from pathlib import Path

import asyncpg

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

_CSV_PATH: Path = (
    Path(__file__).resolve().parent.parent / "data" / "geo" / "municipios_centroides.csv"
)


def _load_centroides() -> dict[str, tuple[float, float]]:
    """Return {ine_code5: (lat, lon)} from the centroid CSV.

    location_id in the CSV is the INE 5-digit code without leading zeros
    (e.g. '1001' -> '01001'). lat and lon are stored as-is (WGS84 decimal
    degrees). Note: the CSV uses lon/lat column order — 'lat' is actually
    longitude and 'lon' is latitude in WGS84 convention (the column names in
    the upstream source are swapped). We normalise here so callers always get
    (lat_wgs84, lon_wgs84) = (y, x).
    """
    result: dict[str, tuple[float, float]] = {}
    with _CSV_PATH.open(encoding="latin-1", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            code = str(row["location_id"]).zfill(5)
            raw_lat = row["lat"].strip()
            raw_lon = row["lon"].strip()
            if not raw_lat or not raw_lon:
                continue
            # The CSV 'lat' column holds the longitude value and 'lon' holds
            # latitude — this is an upstream naming quirk in the ine-places gem.
            # After careful sample validation against known coordinates
            # (e.g. Madrid 01: lat_col=-3.69, lon_col=40.41 → clearly lon/lat),
            # we swap: real_lat = float(raw_lon), real_lon = float(raw_lat).
            real_lon = float(raw_lat)
            real_lat = float(raw_lon)
            result[code] = (real_lat, real_lon)
    return result


async def seed(conn: asyncpg.Connection) -> dict[str, int]:
    """Apply centroid data to geo_municipality.

    Returns counts: updated, skipped (already correct), missing (not in DB).
    """
    centroides = _load_centroides()
    print(f"Loaded {len(centroides)} centroids from CSV.")

    # Fetch current state — only codes present in the CSV
    codes = list(centroides.keys())
    rows = await conn.fetch(
        "SELECT code, lat, lon FROM geo_municipality WHERE code = ANY($1::char(5)[])",
        codes,
    )
    db_state: dict[str, tuple[float | None, float | None]] = {
        r["code"]: (r["lat"], r["lon"]) for r in rows
    }

    missing_in_db = set(centroides.keys()) - set(db_state.keys())
    if missing_in_db:
        print(f"  WARNING: {len(missing_in_db)} CSV codes not found in geo_municipality (ignored).")

    to_update: list[tuple[float, float, str]] = []
    skipped = 0
    for code, (lat, lon) in centroides.items():
        if code not in db_state:
            continue
        current_lat, current_lon = db_state[code]
        # Skip if already correct (PG MVCC doctrine: no UPDATE of non-mutated rows)
        if current_lat is not None and abs(current_lat - lat) < 1e-9 and abs(current_lon - lon) < 1e-9:
            skipped += 1
        else:
            to_update.append((lat, lon, code))

    if to_update:
        async with conn.transaction():
            await conn.executemany(
                "UPDATE geo_municipality SET lat = $1, lon = $2 WHERE code = $3",
                to_update,
            )
        print(f"  Updated: {len(to_update)}, Skipped (already correct): {skipped}")
    else:
        print(f"  Nothing to update — all {skipped} centroids already seeded.")

    return {
        "updated": len(to_update),
        "skipped": skipped,
        "missing_in_db": len(missing_in_db),
    }


async def main() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        counts = await seed(conn)
        # Verify coverage
        coverage = await conn.fetchrow(
            "SELECT count(*) AS total, count(lat) AS with_centroid FROM geo_municipality"
        )
        print(
            f"Coverage: {coverage['with_centroid']}/{coverage['total']} municipalities "
            f"have centroid ({coverage['with_centroid']/coverage['total']*100:.1f}%)."
        )
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
