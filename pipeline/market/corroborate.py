"""corroborate.py — M8: DGT-vs-GONE cohort corroboration (F4, 01-market-intelligence).

"% de cohorte corroborada = transferencias DGT(provincia+marca+modelo+mes) /
GONE Cardeep(misma cohorte+mes)" (carta §4, M8 row). Published as a data-QUALITY
metric ("nuestra señal de retirada está corroborada al X% contra registro oficial
DGT"), never as per-unit proof (no VIN join is possible — DGT restricts the chassis
number since 2025-02-01; corroboration is COHORT-level, a limit honestly declared in
carta §3.2, not a shortfall of this implementation).

Two granularities computed (both real, neither fabricated to fill a gap):
  - make+province+month (``model IS NULL`` in dgt_corroboration) — make normalization
    (uppercase-trim) is reliable; always computable.
  - make+model+province+month — model matching is the carta's own declared "eslabón
    más débil" (§2 veredicto adversarial point 2): DGT's MODELO_ITV is free text with
    no shared dictionary with Cardeep's cleaned model field. An uppercase-trim join
    catches EXACT matches only (e.g. DGT "GOLF" vs Cardeep "Golf" -> matches; DGT
    "IBIZA FR" vs Cardeep "Ibiza" -> does NOT match). This under-counts corroboration
    at the model level — documented here and in the run's own notes, not silently
    inflated by fuzzy-matching this pilar was never asked to build (§8: LLM-assisted
    long-tail matching is future work, explicitly deferred, never invented ad hoc).

DGT rows are filtered to COD_TIPO='40' (TURISMO / passenger car) — Cardeep's census
is cars only; the raw DGT transferencias file covers every vehicle type (trucks,
motorcycles, trailers, tractors...) and comparing against an unfiltered DGT count
would inflate the denominator with vehicle types Cardeep never tracks (a real
finding of this phase, not anticipated in the carta's original schema sketch).

GONE events use the SAME coalesce-canon as F2's recent-activity metrics (M3/M4/M5/
M7/M9) — a GONE event on a vehicle the cluster resolver has never seen is a real
signal, not noise, per the identical fix already applied there.

Every cohort appearing on EITHER side is written (FULL OUTER JOIN semantics) — a
cohort with real GONE activity but zero DGT corroboration (or vice versa) is a
finding, not something to hide behind an inner join.
"""
from __future__ import annotations

import argparse
import asyncio
import os
from datetime import date

import asyncpg

from pipeline.ids import ulid
from pipeline.market.ingest_dgt import COD_TIPO_TURISMO

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

METHODOLOGY_VERSION = "v1"

_COALESCE_CANON_CTE = """
    active_run AS (
        SELECT cluster_run_id FROM vehicle_cluster_run
         WHERE vam_verified = TRUE ORDER BY run_at DESC LIMIT 1
    ),
    canon AS (
        SELECT vc.canonical_vehicle_ulid AS vehicle_ulid
          FROM vehicle_cluster vc, active_run ar
         WHERE vc.cluster_run_id = ar.cluster_run_id
           AND vc.vehicle_ulid = vc.canonical_vehicle_ulid
        UNION ALL
        SELECT v.vehicle_ulid
          FROM vehicle v, active_run ar
         WHERE NOT EXISTS (
                   SELECT 1 FROM vehicle_cluster vc2
                    WHERE vc2.cluster_run_id = ar.cluster_run_id
                      AND vc2.vehicle_ulid = v.vehicle_ulid
               )
    )
"""

_GONE_BY_MAKE_SQL = f"""
WITH {_COALESCE_CANON_CTE},
gone AS (
    SELECT e.province_code, upper(trim(v.make)) AS make_u
      FROM vehicle_event ve
      JOIN canon c ON c.vehicle_ulid = ve.vehicle_ulid
      JOIN vehicle v ON v.vehicle_ulid = ve.vehicle_ulid
      JOIN entity e ON e.entity_ulid = ve.entity_ulid
     WHERE ve.event_type = 'GONE'
       AND ve.observed_at >= $1::date AND ve.observed_at < $2::date
       AND v.make IS NOT NULL AND e.province_code IS NOT NULL
)
SELECT province_code, make_u, count(*) AS gone_count
  FROM gone GROUP BY province_code, make_u
"""

_GONE_BY_MAKE_MODEL_SQL = f"""
WITH {_COALESCE_CANON_CTE},
gone AS (
    SELECT e.province_code, upper(trim(v.make)) AS make_u, upper(trim(v.model)) AS model_u
      FROM vehicle_event ve
      JOIN canon c ON c.vehicle_ulid = ve.vehicle_ulid
      JOIN vehicle v ON v.vehicle_ulid = ve.vehicle_ulid
      JOIN entity e ON e.entity_ulid = ve.entity_ulid
     WHERE ve.event_type = 'GONE'
       AND ve.observed_at >= $1::date AND ve.observed_at < $2::date
       AND v.make IS NOT NULL AND v.model IS NOT NULL AND e.province_code IS NOT NULL
)
SELECT province_code, make_u, model_u, count(*) AS gone_count
  FROM gone GROUP BY province_code, make_u, model_u
"""

_DGT_BY_MAKE_SQL = """
    SELECT province_code, upper(trim(marca)) AS make_u, count(*) AS dgt_count
      FROM dgt_transfer
     WHERE batch_id = $1 AND cod_tipo = $2 AND province_code IS NOT NULL AND marca IS NOT NULL
     GROUP BY province_code, upper(trim(marca))
"""

_DGT_BY_MAKE_MODEL_SQL = """
    SELECT province_code, upper(trim(marca)) AS make_u, upper(trim(modelo)) AS model_u, count(*) AS dgt_count
      FROM dgt_transfer
     WHERE batch_id = $1 AND cod_tipo = $2 AND province_code IS NOT NULL
       AND marca IS NOT NULL AND modelo IS NOT NULL
     GROUP BY province_code, upper(trim(marca)), upper(trim(modelo))
"""


def _month_bounds(month_str: str) -> tuple[date, date]:
    """YYYYMM -> (first day of month, first day of NEXT month) — half-open range."""
    year, month = int(month_str[:4]), int(month_str[4:6])
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return start, end


async def compute_corroboration(
    conn: asyncpg.Connection, batch_id: str, month_str: str
) -> list[dict]:
    """Compute both granularities (make-level, make+model-level) for one month.

    Returns a list of row-dicts ready for insertion (province_code, make, model,
    gone_count, dgt_count, ratio) — model=None for make-level rows.
    """
    start, end = _month_bounds(month_str)

    gone_make_rows = await conn.fetch(_GONE_BY_MAKE_SQL, start, end)
    gone_make_model_rows = await conn.fetch(_GONE_BY_MAKE_MODEL_SQL, start, end)
    dgt_make_rows = await conn.fetch(_DGT_BY_MAKE_SQL, batch_id, COD_TIPO_TURISMO)
    dgt_make_model_rows = await conn.fetch(_DGT_BY_MAKE_MODEL_SQL, batch_id, COD_TIPO_TURISMO)

    def _merge(gone_rows, dgt_rows, key_fields: tuple[str, ...]) -> list[dict]:
        gone_idx = {tuple(r[k] for k in key_fields): r["gone_count"] for r in gone_rows}
        dgt_idx = {tuple(r[k] for k in key_fields): r["dgt_count"] for r in dgt_rows}
        all_keys = set(gone_idx) | set(dgt_idx)
        out = []
        for key in all_keys:
            gone_count = gone_idx.get(key, 0)
            dgt_count = dgt_idx.get(key, 0)
            ratio = (dgt_count / gone_count) if gone_count > 0 else None
            row = dict(zip(key_fields, key))
            row["gone_count"] = gone_count
            row["dgt_count"] = dgt_count
            row["ratio"] = ratio
            out.append(row)
        return out

    make_level = _merge(gone_make_rows, dgt_make_rows, ("province_code", "make_u"))
    for r in make_level:
        r["make"] = r.pop("make_u")
        r["model"] = None

    make_model_level = _merge(
        gone_make_model_rows, dgt_make_model_rows, ("province_code", "make_u", "model_u")
    )
    for r in make_model_level:
        r["make"] = r.pop("make_u")
        r["model"] = r.pop("model_u")

    return make_level + make_model_level


async def run_corroboration(conn: asyncpg.Connection, batch_id: str) -> str:
    """Full M8 run for the month of ``batch_id``. Returns the new run_id."""
    batch = await conn.fetchrow(
        "SELECT month FROM dgt_transfer_batch WHERE batch_id = $1", batch_id
    )
    if batch is None:
        raise RuntimeError(f"no dgt_transfer_batch found for batch_id={batch_id}")
    month_str = batch["month"]

    rows = await compute_corroboration(conn, batch_id, month_str)
    run_id = ulid()

    async with conn.transaction():
        await conn.execute(
            """
            INSERT INTO dgt_corroboration_run
                (run_id, batch_id, month, methodology_version, n_cohorts, notes)
            VALUES ($1,$2,$3,$4,$5,$6)
            """,
            run_id, batch_id, month_str, METHODOLOGY_VERSION, len(rows),
            "cohort = province+make(+model)+month; DGT filtered to COD_TIPO=TURISMO; "
            "GONE via coalesce-canon (never-clustered vehicles included, per F2's fix); "
            "model matching is uppercase-trim EXACT only (carta's declared weakest link).",
        )
        if rows:
            await conn.executemany(
                """
                INSERT INTO dgt_corroboration
                    (run_id, province_code, make, model, month, gone_count, dgt_count, ratio)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
                """,
                [
                    (run_id, r["province_code"], r["make"], r["model"], month_str,
                     r["gone_count"], r["dgt_count"], r["ratio"])
                    for r in rows
                ],
            )
    return run_id


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-id", required=True)
    args = parser.parse_args()

    conn = await asyncpg.connect(DSN, command_timeout=300)
    try:
        run_id = await run_corroboration(conn, args.batch_id)
        n = await conn.fetchval("SELECT count(*) FROM dgt_corroboration WHERE run_id = $1", run_id)
        print(f"run_id={run_id}")
        print(f"cohorts={n}")
        agg = await conn.fetchrow(
            "SELECT sum(gone_count) AS total_gone, sum(dgt_count) AS total_dgt "
            "FROM dgt_corroboration WHERE run_id = $1 AND model IS NULL",
            run_id,
        )
        print(f"make-level totals: gone={agg['total_gone']} dgt={agg['total_dgt']}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
