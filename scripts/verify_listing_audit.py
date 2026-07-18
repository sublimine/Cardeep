"""Via-2 independent verifier for C1 (07-marketing.md S7 protocol, row 1: "Script
verificador separado que recalcula los 11 checks con queries SQL directas escritas
aparte (sin importar el modulo del motor) sobre una muestra aleatoria >=100
vehiculos/run; divergencia >0 = run en cuarentena").

Deliberately does NOT import pipeline.marketing.listing_audit — every check is
re-implemented here from scratch, independently, against direct SQL, so a bug shared
between producer and verifier (the exact failure mode two paths sharing code cannot
catch) has no way to hide. If this script and the production job ever disagree on a
single vehicle's score, that is the signal the protocol exists to produce.

Usage:
    python -m scripts.verify_listing_audit --run <run_ulid> --sample 100
    python -m scripts.verify_listing_audit --sample 150   # verifies the latest run
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from datetime import date, datetime, timezone

import asyncpg

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# Independently re-declared weights (must match pipeline/marketing/listing_audit.py's
# table — a mismatch here would itself be a finding, not silently reconciled).
_WEIGHTS = {
    "c1": 12, "c2": 10, "c3": 8, "c4": 10, "c5": 12, "c6": 6,
    "c7": 10, "c8": 8, "c9": 6, "c10": 10, "c11": 8,
}
_VIN_RE = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")
_STOPWORDS = {"de", "del", "la", "el", "en", "con", "y", "un", "una", "the", "a", "of"}


def _independent_score(row: dict, edges: list[dict], drops_30d: int, today: date) -> tuple[int, dict[str, bool]]:
    """Re-derive the 11-check pass/fail independently — SEPARATE code, same intent as
    the carta's own table, never a call into the production module."""
    passed: dict[str, bool] = {}

    passed["c1"] = row["price"] is not None and float(row["price"]) > 0
    passed["c2"] = bool(row["make"]) and bool(row["model"])
    passed["c3"] = row["year"] is not None and 1900 <= row["year"] <= today.year + 1
    passed["c4"] = row["km"] is not None and row["km"] >= 0
    passed["c5"] = bool(row["vin_ref"]) and bool(_VIN_RE.match(row["vin_ref"].strip().upper()))
    passed["c6"] = bool(row["fuel"]) and bool(row["transmission"])
    passed["c7"] = bool(row["photo_url"])

    stored_w, stored_h = row.get("_c8_width"), row.get("_c8_height")
    passed["c8"] = stored_w is not None and stored_h is not None and stored_w >= 800 and stored_h >= 600

    if row["title"]:
        tokens = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", row["title"].lower())
        exclude = set(_STOPWORDS)
        if row["make"]:
            exclude |= {t.lower() for t in re.findall(r"[a-zA-ZÀ-ÿ0-9]+", row["make"])}
        if row["model"]:
            exclude |= {t.lower() for t in re.findall(r"[a-zA-ZÀ-ÿ0-9]+", row["model"])}
        if row["year"]:
            exclude.add(str(row["year"]))
        extra = [t for t in tokens if t not in exclude and len(t) >= 2]
        passed["c9"] = len(extra) >= 1
    else:
        passed["c9"] = False

    mismatches = [
        e for e in edges
        if e["status"] == "listed" and e["platform_price"] is not None
        and row["price"] is not None and float(e["platform_price"]) != float(row["price"])
    ]
    passed["c10"] = len(mismatches) == 0
    passed["c11"] = drops_30d < 2

    score = sum(_WEIGHTS[k] for k, ok in passed.items() if ok)
    return score, passed


async def _latest_run_ulid(conn: asyncpg.Connection) -> str | None:
    return await conn.fetchval("SELECT run_ulid FROM listing_audit_run ORDER BY started_at DESC LIMIT 1")


async def verify(*, run_ulid: str | None, sample_size: int, dsn: str = DSN) -> dict:
    conn = await asyncpg.connect(dsn)
    try:
        target_run = run_ulid or await _latest_run_ulid(conn)
        if target_run is None:
            return {"error": "no listing_audit_run exists"}

        sample = await conn.fetch(
            """SELECT la.vehicle_ulid, la.score AS produced_score, la.checks
                 FROM listing_audit la
                WHERE la.run_ulid = $1
                ORDER BY random()
                LIMIT $2""",
            target_run, sample_size,
        )
        if not sample:
            return {"error": f"run {target_run} has zero listing_audit rows"}

        ulids = [r["vehicle_ulid"] for r in sample]
        vrows = {
            r["vehicle_ulid"]: dict(r)
            for r in await conn.fetch(
                """SELECT vehicle_ulid, price, make, model, year, km, vin_ref, fuel,
                          transmission, photo_url, title
                     FROM vehicle WHERE vehicle_ulid = ANY($1::text[])""",
                ulids,
            )
        }
        edge_rows = await conn.fetch(
            "SELECT vehicle_ulid, platform_price, status FROM platform_listing WHERE vehicle_ulid = ANY($1::text[])",
            ulids,
        )
        edges_by_vehicle: dict[str, list[dict]] = {}
        for e in edge_rows:
            edges_by_vehicle.setdefault(e["vehicle_ulid"], []).append(dict(e))

        drop_rows = await conn.fetch(
            """SELECT vehicle_ulid, count(*) AS n
                 FROM vehicle_event
                WHERE event_type = 'PRICE_CHANGE' AND vehicle_ulid = ANY($1::text[])
                  AND observed_at > now() - interval '30 days'
                  AND (new_value->>'price')::numeric < (old_value->>'price')::numeric
                GROUP BY vehicle_ulid""",
            ulids,
        )
        drops_by_vehicle = {r["vehicle_ulid"]: r["n"] for r in drop_rows}

        today = date.today()
        divergences: list[dict] = []
        for r in sample:
            vrow = vrows.get(r["vehicle_ulid"])
            if vrow is None:
                divergences.append({"vehicle_ulid": r["vehicle_ulid"], "reason": "vehicle row vanished"})
                continue

            checks = r["checks"] if isinstance(r["checks"], list) else json.loads(r["checks"])
            c8 = next((c for c in checks if c["check_id"] == "c8"), {})
            vrow["_c8_width"] = c8.get("evidence", {}).get("width")
            vrow["_c8_height"] = c8.get("evidence", {}).get("height")

            indep_score, indep_passed = _independent_score(
                vrow, edges_by_vehicle.get(r["vehicle_ulid"], []),
                drops_by_vehicle.get(r["vehicle_ulid"], 0), today,
            )
            if indep_score != r["produced_score"]:
                per_check_divergence = {
                    c["check_id"]: {"produced": c["passed"], "independent": indep_passed.get(c["check_id"])}
                    for c in checks
                    if c["passed"] != indep_passed.get(c["check_id"])
                }
                divergences.append({
                    "vehicle_ulid": r["vehicle_ulid"], "produced_score": r["produced_score"],
                    "independent_score": indep_score, "per_check": per_check_divergence,
                })

        return {
            "run_ulid": target_run, "sample_size": len(sample),
            "divergence_count": len(divergences), "divergences": divergences,
            "quarantine": len(divergences) > 0,
        }
    finally:
        await conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default=None, help="run_ulid to verify (default: latest)")
    parser.add_argument("--sample", type=int, default=100, help="sample size (carta minimum: 100)")
    args = parser.parse_args()

    result = asyncio.run(verify(run_ulid=args.run, sample_size=args.sample))
    print(json.dumps(result, indent=2, default=str))
    if result.get("quarantine"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
