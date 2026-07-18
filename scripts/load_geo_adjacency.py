"""Load the Spanish province land-border adjacency graph into geo_province_adjacency.

08-forum-community F2 ("Se busca" board, carta §4.4 geo match component) needs a static
province-to-province adjacency table. This data was originally embedded as an INSERT
inside migrations/0093_wanted.sql, which broke CI's "migrate up from empty" invariant
(country-proof-invariant and bring-up-smoke jobs run migrations against a truly empty
Postgres with NO seed step before or after -- see .github/workflows/ci.yml's explicit
"DO NOT add a census/geo seed step" comment on the country-proof job): the INSERT's own
FOREIGN KEY into geo_province (populated only by scripts/load_geo.py, never by a
migration) failed with ForeignKeyViolationError on any fresh database. The DATA now lives
here, following the exact same pattern as scripts/load_geo.py and
scripts/seed_geo_centroides.py (idempotent, INSERT ... ON CONFLICT DO NOTHING,
--country-parametrized); the SCHEMA (CREATE TABLE geo_province_adjacency) stays in
migrations/0093_wanted.sql, since DDL is the migration's job and static reference data
that depends on another loader's rows is this script's job.

Source data verified by TWO independent paths (carta §5.2 requirement), unchanged from
the original migration's own verification (see migrations/0093_wanted.sql history for the
full methodology): (1) cartographic -- computed from a real IGN-derived province-boundary
polygon dataset (codeforgermany/click_that_hood, spain-provinces.geojson) via shapely
polygon-touch detection, stable across buffer tolerances 0-550m (111 pairs); (2) graph
consistency -- sum of per-province degrees = 222 = 2 x 111 pairs. Manually cross-checked
against well-known Spanish geography (Madrid 5 neighbours, Zaragoza 8, Cuenca 7, Toledo 6).
The 5 island/exclave provinces (Balears, Las Palmas, Santa Cruz de Tenerife, Ceuta,
Melilla) correctly resolve to ZERO land neighbours.

Usage:
    python -m scripts.load_geo_adjacency [--country ES]
"""
from __future__ import annotations

import argparse
import asyncio
import os

import asyncpg

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

_DEFAULT_COUNTRY = "ES"

# (province_code, adjacent_province_code) -- both directions stored explicitly (222 rows
# = 2 x 111 real land-border pairs), matching geo_province_adjacency's own PK shape.
ADJACENCY_PAIRS: list[tuple[str, str]] = [
    ("01", "09"), ("09", "01"),
    ("01", "20"), ("20", "01"),
    ("01", "26"), ("26", "01"),
    ("01", "31"), ("31", "01"),
    ("01", "48"), ("48", "01"),
    ("02", "03"), ("03", "02"),
    ("02", "13"), ("13", "02"),
    ("02", "16"), ("16", "02"),
    ("02", "18"), ("18", "02"),
    ("02", "23"), ("23", "02"),
    ("02", "46"), ("46", "02"),
    ("03", "46"), ("46", "03"),
    ("04", "18"), ("18", "04"),
    ("04", "30"), ("30", "04"),
    ("05", "10"), ("10", "05"),
    ("05", "28"), ("28", "05"),
    ("05", "37"), ("37", "05"),
    ("05", "40"), ("40", "05"),
    ("05", "45"), ("45", "05"),
    ("05", "47"), ("47", "05"),
    ("06", "10"), ("10", "06"),
    ("06", "13"), ("13", "06"),
    ("06", "14"), ("14", "06"),
    ("06", "21"), ("21", "06"),
    ("06", "41"), ("41", "06"),
    ("06", "45"), ("45", "06"),
    ("08", "25"), ("25", "08"),
    ("08", "43"), ("43", "08"),
    ("09", "26"), ("26", "09"),
    ("09", "34"), ("34", "09"),
    ("09", "40"), ("40", "09"),
    ("09", "42"), ("42", "09"),
    ("09", "47"), ("47", "09"),
    ("09", "48"), ("48", "09"),
    ("10", "37"), ("37", "10"),
    ("10", "45"), ("45", "10"),
    ("11", "21"), ("21", "11"),
    ("11", "41"), ("41", "11"),
    ("12", "43"), ("43", "12"),
    ("12", "44"), ("44", "12"),
    ("12", "46"), ("46", "12"),
    ("13", "14"), ("14", "13"),
    ("13", "16"), ("16", "13"),
    ("13", "23"), ("23", "13"),
    ("13", "45"), ("45", "13"),
    ("14", "18"), ("18", "14"),
    ("14", "41"), ("41", "14"),
    ("15", "27"), ("27", "15"),
    ("15", "36"), ("36", "15"),
    ("16", "19"), ("19", "16"),
    ("16", "28"), ("28", "16"),
    ("16", "44"), ("44", "16"),
    ("16", "45"), ("45", "16"),
    ("16", "46"), ("46", "16"),
    ("17", "08"), ("08", "17"),
    ("17", "25"), ("25", "17"),
    ("19", "28"), ("28", "19"),
    ("19", "40"), ("40", "19"),
    ("19", "42"), ("42", "19"),
    ("19", "44"), ("44", "19"),
    ("19", "50"), ("50", "19"),
    ("20", "31"), ("31", "20"),
    ("20", "48"), ("48", "20"),
    ("21", "41"), ("41", "21"),
    ("22", "25"), ("25", "22"),
    ("22", "31"), ("31", "22"),
    ("22", "50"), ("50", "22"),
    ("23", "14"), ("14", "23"),
    ("23", "18"), ("18", "23"),
    ("24", "27"), ("27", "24"),
    ("24", "34"), ("34", "24"),
    ("24", "47"), ("47", "24"),
    ("24", "49"), ("49", "24"),
    ("25", "43"), ("43", "25"),
    ("25", "50"), ("50", "25"),
    ("26", "31"), ("31", "26"),
    ("26", "42"), ("42", "26"),
    ("26", "50"), ("50", "26"),
    ("28", "40"), ("40", "28"),
    ("28", "45"), ("45", "28"),
    ("29", "11"), ("11", "29"),
    ("29", "14"), ("14", "29"),
    ("29", "18"), ("18", "29"),
    ("29", "41"), ("41", "29"),
    ("30", "02"), ("02", "30"),
    ("30", "03"), ("03", "30"),
    ("30", "18"), ("18", "30"),
    ("31", "50"), ("50", "31"),
    ("32", "24"), ("24", "32"),
    ("32", "27"), ("27", "32"),
    ("32", "49"), ("49", "32"),
    ("33", "24"), ("24", "33"),
    ("33", "27"), ("27", "33"),
    ("33", "39"), ("39", "33"),
    ("34", "47"), ("47", "34"),
    ("36", "27"), ("27", "36"),
    ("36", "32"), ("32", "36"),
    ("37", "47"), ("47", "37"),
    ("37", "49"), ("49", "37"),
    ("39", "09"), ("09", "39"),
    ("39", "24"), ("24", "39"),
    ("39", "34"), ("34", "39"),
    ("39", "48"), ("48", "39"),
    ("40", "47"), ("47", "40"),
    ("42", "40"), ("40", "42"),
    ("42", "50"), ("50", "42"),
    ("43", "44"), ("44", "43"),
    ("43", "50"), ("50", "43"),
    ("44", "46"), ("46", "44"),
    ("44", "50"), ("50", "44"),
    ("47", "49"), ("49", "47"),
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """CLI args: ``--country`` (ISO-3166 alpha-2, default ES) stamped on every row."""
    parser = argparse.ArgumentParser(
        description="Load the province land-border adjacency graph into geo_province_adjacency."
    )
    parser.add_argument(
        "--country", default=_DEFAULT_COUNTRY,
        help="ISO-3166 alpha-2 country_code stamped on every adjacency row (default ES).",
    )
    return parser.parse_args(argv)


async def main(country: str = _DEFAULT_COUNTRY) -> None:
    conn = await asyncpg.connect(DSN)
    try:
        await conn.executemany(
            "INSERT INTO geo_province_adjacency (country_code, province_code, adjacent_province_code) "
            "VALUES ($1, $2, $3) ON CONFLICT (country_code, province_code, adjacent_province_code) DO NOTHING",
            [(country, a, b) for a, b in ADJACENCY_PAIRS],
        )
        n = await conn.fetchval(
            "SELECT count(*) FROM geo_province_adjacency WHERE country_code = $1", country
        )
        # 2-way check: every edge's province must exist in geo_province (FK already
        # guarantees this at INSERT time -- this just surfaces the count for triage).
        provinces_with_edges = await conn.fetchval(
            "SELECT count(DISTINCT province_code) FROM geo_province_adjacency WHERE country_code = $1",
            country,
        )
        print(f"adjacency_edges={n} (source pairs={len(ADJACENCY_PAIRS)}) "
              f"provinces_with_edges={provinces_with_edges}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main(parse_args().country))
