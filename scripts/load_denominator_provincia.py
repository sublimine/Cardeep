"""Load the per-province VENTA denominator into denominator_estimate (audit SU-A2 / SU-SEAL).

Until now denominator_estimate held ONLY the national P_all floor (38,555). The per-province
denominator — the official DIRCE CNAE-451 (car-sales) registral count — was computed and VERIFIED
in docs/recon/B6_venta_sello.md but never persisted, so A2's denominator and the per-province seal
could not be queried from the DB. This loads it.

Method (verified in the recon, no new data acquired here):
    den_venta(province) = round( cnae45_locales(province) × ratio_451/45_national )
    ratio_451/45 = 23085 / 88621 = 0.2605   (DIRCE 2025: group 451 / division 45, national)
    cnae45_locales = DIRCE 2025 table 301, data/official/denominador_cnae45_provincia_2024.csv

The DIRCE registral count is a CEILING on the consumer-facing dealer universe (it counts every
legally-registered CNAE-451 establishment, including wholesale/dormant), so method='registral_ceiling'
is the honest label — the seal's coverage = served_numerator / this ceiling.

Idempotent: replaces exactly the segment='venta' rows (DELETE+INSERT in one transaction). The
national P_all source_floor row is untouched. MVCC-clean for a small reference table.

Run:  python scripts/load_denominator_provincia.py            # dry-run (report, no writes)
      python scripts/load_denominator_provincia.py --apply
"""
from __future__ import annotations

import asyncio
import csv
import json
import os
import sys
from pathlib import Path

import asyncpg

ROOT = Path(__file__).resolve().parent.parent
# Defaults to live production (:5433) for a real load; CARDEEP_DSN overrides it so the
# loader can be exercised against the :5434 dry-run without ever touching production.
DSN = os.environ.get("CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep")
CSV_PATH = ROOT / "data" / "official" / "denominador_cnae45_provincia_2024.csv"

# DIRCE 2025 national: group 451 (4511 sale + 4519 other vehicles) / division 45 (sale+repair).
RATIO_451_45 = 23085 / 88621
SOURCES = [
    "DIRCE 2025 tabla 301 (locales CNAE45 por provincia)",
    "DIRCE 2025 tabla 294/39372 (grupo 451 por CCAA, nacional=23085)",
]
EVIDENCE = "data/official/denominador_cnae45_provincia_2024.csv + docs/recon/B6_venta_sello.md"

# This DIRCE denominator is ES-sourced (the 52 ES provinces). denominator_estimate carries
# country_code since migration 0053 and feeds the SERVED seals (v_province_seal /
# v_exhaustiveness_seal), so the load MUST scope its pre-check, DELETE and INSERT to ES — a
# country-blind DELETE would wipe another tenant's denominators and silently break its seal.
COUNTRY = "ES"


def _load_rows() -> list[tuple[str, int, int]]:
    """Return [(province_code, cnae45_locales, den_venta), ...] for the 52 provinces."""
    out: list[tuple[str, int, int]] = []
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            pc = row["province_code"].strip()
            cnae45 = int(row["cnae45_locales_2024"])
            den_venta = round(cnae45 * RATIO_451_45)
            out.append((pc, cnae45, den_venta))
    return out


async def load(conn: asyncpg.Connection, *, apply: bool) -> dict[str, int]:
    """Load the per-province VENTA denominator against a provided connection.

    Separated from connection management so the loader can be driven against the :5434
    dry-run inside a rolled-back transaction (isolation-safe testing). Returns counts:
    provinces (in the CSV), existing (segment='venta' rows replaced), loaded (rows now).
    """
    rows = _load_rows()
    sum_cnae45 = sum(r[1] for r in rows)
    sum_den = sum(r[2] for r in rows)
    print(f"provinces: {len(rows)}  | sum cnae45: {sum_cnae45}  | sum den_venta: {sum_den}  "
          f"(DIRCE 451 national 2025: 23085)  | ratio: {RATIO_451_45:.4f}")
    if len(rows) != 52:
        raise SystemExit(f"ABORT: expected 52 provinces, got {len(rows)} — refusing to load a partial set.")

    # Validate every province_code exists in geo_province FOR THIS COUNTRY before writing
    # (the composite FK (country_code, province_code) would reject otherwise; a country-blind
    # pre-check could pass on a province that only exists under another tenant and then fail
    # at INSERT). A clean pre-check gives an honest report and never half-applies.
    valid = {r["code"] for r in await conn.fetch(
        "SELECT code FROM geo_province WHERE country_code = $1", COUNTRY)}
    bad = [pc for pc, _, _ in rows if pc not in valid]
    if bad:
        raise SystemExit(f"ABORT: province_code(s) not in geo_province[{COUNTRY}]: {bad}")

    existing = await conn.fetchval(
        "SELECT count(*) FROM denominator_estimate "
        "WHERE segment = 'venta' AND country_code = $1", COUNTRY)
    print(f"existing segment='venta' rows ({COUNTRY}): {existing}  (will be replaced)")

    if not apply:
        print("DRY-RUN -- no writes. Sample:")
        for pc, c, d in rows[:5]:
            print(f"   {pc}: cnae45={c} -> den_venta(registral_ceiling)={d}")
        return {"provinces": len(rows), "existing": existing, "loaded": 0}

    async with conn.transaction():
        await conn.execute(
            "DELETE FROM denominator_estimate WHERE segment = 'venta' AND country_code = $1",
            COUNTRY,
        )
        await conn.executemany(
            """INSERT INTO denominator_estimate
                   (segment, province_code, method, n1, point_est, ci_low, ci_high,
                    sources_used, evidence_uri, country_code)
               VALUES ('venta', $1, 'registral_ceiling', $2, $3, $3, $3, $4, $5, $6)""",
            [(pc, cnae45, den, json.dumps(SOURCES), EVIDENCE, COUNTRY)
             for pc, cnae45, den in rows],
        )
    loaded = await conn.fetchval(
        "SELECT count(*) FROM denominator_estimate "
        "WHERE segment = 'venta' AND country_code = $1", COUNTRY)
    db_sum = await conn.fetchval(
        "SELECT sum(point_est) FROM denominator_estimate "
        "WHERE segment = 'venta' AND country_code = $1", COUNTRY)
    print(f"APPLIED. segment='venta' rows now {loaded} ({COUNTRY}), sum(point_est)={db_sum} "
          f"(national P_all floor + other-country denominators untouched).")
    return {"provinces": len(rows), "existing": existing, "loaded": loaded}


async def main(apply: bool) -> None:
    conn = await asyncpg.connect(DSN)
    try:
        await load(conn, apply=apply)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main(apply="--apply" in sys.argv))
