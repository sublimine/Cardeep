"""F4 — flip specific sources to cadence_mode='adaptive' (00-marketplace-engine.md F4).

Deliberate, explicit, source-by-source rollout — NEVER a blanket default. A source is only
listed here after scripts/backtest_adaptive_cadence.py shows it clears the PRODUCTION
MIN_WINDOWS gate (pipeline.ops.cadence_estimator.MIN_WINDOWS) with a real, computed
backtest result (never the exploratory/relaxed-threshold pass, which is illustrative only).

Requires the source to already have a non-null computed_interval_hours (i.e.
pipeline.ops.scheduler.cadence_estimate_job — or a manual estimate_change_rate +
apply_cadence_estimate call — has already run for it at least once); refuses to flip a
source with no estimate on record, since 'adaptive' + NULL computed_interval_hours falls
back to the static tier anyway (see _due_sources()) but that is not what a deliberate
rollout should silently do.

Usage:
    python -m scripts.enable_adaptive_cadence --dry-run                 # show what would change
    python -m scripts.enable_adaptive_cadence --apply                   # apply the rollout list
    python -m scripts.enable_adaptive_cadence --apply --source-key X    # flip one extra source
"""
from __future__ import annotations

import argparse
import asyncio
import os

import asyncpg

DSN = os.environ.get("CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep")

# The rollout list, F4 first cut (2026-07): the 7 sources that cleared the production
# MIN_WINDOWS=5 gate in the 90-day backtest (scripts/backtest_adaptive_cadence.py,
# 2026-07-17 run) — all Tier-1/high-frequency 24h sources. Every one of them backtested to
# an EXACT 0.00h staleness delta (their estimated change rate converges to the SAME 24h
# cadence they already run at) — this rollout is provably safe (byte-identical scheduling
# behavior today) while making the mechanism live and ready to compress the moment any of
# these sources' real change pattern slows down. See 00-marketplace-engine.md F4 for the
# full honest finding (no compression is measurable YET for the long-tail 168h/720h/2160h
# tiers — their post-outage sample is too thin; that is a declared gap, not a claim).
ROLLOUT_SOURCE_KEYS: tuple[str, ...] = (
    "autocasion_wholesale",
    "coches_com_wholesale",
    "coches_net_wholesale",
    "dealerprobe_ownsite",
    "milanuncios_wholesale",
    "motor_es_wholesale",
    "wallapop_wholesale",
)


async def _enable(conn: asyncpg.Connection, source_key: str, *, apply: bool) -> dict:
    row = await conn.fetchrow(
        "SELECT cadence_mode, computed_interval_hours, harvest_interval_hours "
        "FROM source_health WHERE source_key=$1",
        source_key,
    )
    if row is None:
        return {"source_key": source_key, "status": "NOT_FOUND"}
    if row["computed_interval_hours"] is None:
        return {
            "source_key": source_key, "status": "REFUSED_NO_ESTIMATE",
            "detail": "no computed_interval_hours on record — run cadence_estimate_job first",
        }
    if row["cadence_mode"] == "adaptive":
        return {"source_key": source_key, "status": "ALREADY_ADAPTIVE",
                "computed_interval_hours": row["computed_interval_hours"]}

    if apply:
        await conn.execute(
            "UPDATE source_health SET cadence_mode='adaptive' WHERE source_key=$1", source_key,
        )
    return {
        "source_key": source_key,
        "status": "ENABLED" if apply else "WOULD_ENABLE",
        "static_harvest_interval_hours": row["harvest_interval_hours"],
        "computed_interval_hours": row["computed_interval_hours"],
    }


async def run(source_keys: tuple[str, ...], *, apply: bool) -> list[dict]:
    conn = await asyncpg.connect(DSN)
    try:
        return [await _enable(conn, key, apply=apply) for key in source_keys]
    finally:
        await conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="F4 — flip sources to cadence_mode='adaptive'.")
    parser.add_argument("--apply", action="store_true", help="Actually write the change (default: dry-run).")
    parser.add_argument("--source-key", action="append", default=[], help="Add an extra source_key (repeatable).")
    args = parser.parse_args()

    source_keys = ROLLOUT_SOURCE_KEYS + tuple(args.source_key)
    results = asyncio.run(run(source_keys, apply=args.apply))

    print("=" * 72)
    print(f"F4 ADAPTIVE CADENCE ROLLOUT — {'APPLY' if args.apply else 'DRY-RUN'}")
    print("=" * 72)
    for r in results:
        print(r)
    print("=" * 72)


if __name__ == "__main__":
    main()
