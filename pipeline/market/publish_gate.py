"""Publication gate for market_stat runs — carta §7 row 3 (CAP HPI ±3% + human close).

"cualquier métrica que se mueva >3% intersemanal se marca en rojo y exige cierre
manual del Director (gate humano) antes de published=TRUE — mismo patrón que
vam_verified en 0023."

Bootstrapping: the FIRST run ever has no prior PUBLISHED run to compare against, so
there is nothing to diverge from — the gate auto-passes for that specific case
(documented here, not a silent loophole; every subsequent run DOES get compared).
"""
from __future__ import annotations

from typing import Any, NamedTuple

import asyncpg

from pipeline.market.cohort import divergence_pct

GATE_THRESHOLD_PCT: float = 3.0


class GateResult(NamedTuple):
    has_baseline: bool          # False only for the bootstrap (no prior published run)
    compared: int               # number of matching segments checked
    anomalies: list[dict[str, Any]]
    max_divergence_pct: float

    @property
    def clean(self) -> bool:
        """True iff there is nothing blocking an automatic publish: either no baseline
        exists yet (bootstrap), or every compared segment is within GATE_THRESHOLD_PCT."""
        return (not self.has_baseline) or (len(self.anomalies) == 0)


async def get_latest_published_run(conn: asyncpg.Connection) -> str | None:
    row = await conn.fetchrow(
        "SELECT run_id FROM market_stat_run WHERE published = TRUE ORDER BY run_at DESC LIMIT 1"
    )
    return row["run_id"] if row else None


def _value_of(row: asyncpg.Record, value_col: str, p50_col: str) -> float | None:
    v = row[value_col]
    if v is not None:
        return float(v)
    p = row[p50_col]
    return float(p) if p is not None else None


async def compare_runs(
    conn: asyncpg.Connection, new_run_id: str, prev_run_id: str
) -> GateResult:
    """Compare every segment present in BOTH runs (matched on metric+segment key).

    Uses ``value_num`` when present, falling back to ``p50`` (M1/M10's distribution
    metrics don't populate value_num) — one comparable number per row either way.
    A segment present in only one of the two runs (a cohort that newly cleared or
    newly dropped below n>=8) is NOT an anomaly by this gate's definition — it has no
    "before" or "after" value to diverge; it is simply new/retired sample coverage.
    """
    rows = await conn.fetch(
        """
        SELECT n.metric_id, n.make, n.model, n.year, n.fuel, n.province_code,
               n.value_num AS new_value_num, n.p50 AS new_p50,
               p.value_num AS prev_value_num, p.p50 AS prev_p50
          FROM market_stat n
          JOIN market_stat p
            ON p.run_id = $2
           AND p.metric_id = n.metric_id
           AND p.make            IS NOT DISTINCT FROM n.make
           AND p.model           IS NOT DISTINCT FROM n.model
           AND p.year            IS NOT DISTINCT FROM n.year
           AND p.fuel            IS NOT DISTINCT FROM n.fuel
           AND p.province_code   IS NOT DISTINCT FROM n.province_code
         WHERE n.run_id = $1
        """,
        new_run_id, prev_run_id,
    )
    anomalies: list[dict[str, Any]] = []
    max_div = 0.0
    compared = 0
    for r in rows:
        new_v = _value_of(r, "new_value_num", "new_p50")
        prev_v = _value_of(r, "prev_value_num", "prev_p50")
        if new_v is None or prev_v is None:
            continue
        compared += 1
        div = divergence_pct(new_v, prev_v)
        max_div = max(max_div, div)
        if div > GATE_THRESHOLD_PCT:
            anomalies.append({
                "metric_id": r["metric_id"], "make": r["make"], "model": r["model"],
                "year": r["year"], "fuel": r["fuel"], "province_code": r["province_code"],
                "prev_value": prev_v, "new_value": new_v, "divergence_pct": div,
            })
    return GateResult(has_baseline=True, compared=compared, anomalies=anomalies, max_divergence_pct=max_div)


async def evaluate_gate(conn: asyncpg.Connection, new_run_id: str) -> GateResult:
    """Full gate evaluation for ``new_run_id``: finds the latest published run (if
    any) and compares. Bootstrap case (no prior published run) returns a clean,
    ``has_baseline=False`` result — see module docstring."""
    prev_run_id = await get_latest_published_run(conn)
    if prev_run_id is None:
        return GateResult(has_baseline=False, compared=0, anomalies=[], max_divergence_pct=0.0)
    return await compare_runs(conn, new_run_id, prev_run_id)


async def publish_run(
    conn: asyncpg.Connection, run_id: str, *, director_confirmed_anomalies: bool = False
) -> GateResult:
    """Evaluate the gate and, if clean (or explicitly confirmed by the Director despite
    anomalies), flip ``published=TRUE``. Never mutates market_stat rows — only the run's
    own gate columns (same lifecycle as vehicle_cluster_run.vam_verified).

    Raises RuntimeError if the gate is dirty and ``director_confirmed_anomalies`` is
    False — publishing NEVER happens silently past a red gate.
    """
    result = await evaluate_gate(conn, run_id)
    if not result.clean and not director_confirmed_anomalies:
        raise RuntimeError(
            f"publish_run: gate is RED for {run_id} — {len(result.anomalies)} segment(s) "
            f"moved >{GATE_THRESHOLD_PCT}% vs the current published run (max "
            f"{result.max_divergence_pct:.2f}%). Director must review and pass "
            f"director_confirmed_anomalies=True explicitly to override. Anomalies: "
            f"{result.anomalies[:5]}"
        )
    await conn.execute(
        "UPDATE market_stat_run SET published = TRUE, published_at = now() WHERE run_id = $1",
        run_id,
    )
    return result
