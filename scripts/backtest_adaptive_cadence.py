"""F4 backtest — measure, don't cite (00-marketplace-engine.md F4 acceptance criterion).

For every source registered in source_health, this:
  1. Runs the PRODUCTION estimator (pipeline.ops.cadence_estimator.estimate_change_rate,
     MIN_WINDOWS=5) "as of" a chosen instant, using ONLY data before that instant (no
     peeking into the future) — reports which sources have enough sample to qualify.
  2. For qualifying sources, simulates two FIXED-cadence visit schedules over the same real
     history — one at the static harvest_interval_hours, one at the estimator's
     computed_interval_hours — and measures, against the source's REAL observed change
     events (vehicle_event via entity_source), the average STALENESS (time from a real
     change to the next scheduled visit under each regime) and the VISIT COUNT (request
     cost) each regime would have incurred. This is the real, computed comparison the carta
     requires — never the paper's cited 35% figure.
  3. Also runs an EXPLORATORY pass with a relaxed min_windows=2 across every source that did
     NOT qualify under (1), to characterize the mechanism's behavior on thinner samples —
     clearly marked LOW CONFIDENCE, illustrative only, never a rollout candidate.

Usage:
    python -m scripts.backtest_adaptive_cadence [--as-of ISO8601] [--lookback-days N]
"""
from __future__ import annotations

import argparse
import asyncio
import os
from datetime import datetime, timedelta, timezone

import asyncpg

from pipeline.ops.cadence_estimator import (
    DEFAULT_LOOKBACK_DAYS,
    MIN_WINDOWS,
    estimate_change_rate,
)

DSN = os.environ.get("CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep")


def _simulate_schedule(window_start: datetime, window_end: datetime, interval_hours: int) -> list[datetime]:
    """A fixed-cadence visit schedule: window_start, window_start+interval, ... < window_end."""
    visits = []
    t = window_start
    delta = timedelta(hours=interval_hours)
    while t < window_end:
        visits.append(t)
        t += delta
    return visits


def _avg_staleness_hours(change_times: list[datetime], visits: list[datetime]) -> float | None:
    """Mean time (hours) from each real change to the next scheduled visit at/after it.

    A change with no later visit in the schedule (past the last simulated visit) is
    excluded — we cannot claim a staleness measurement for a period the simulated
    schedule does not cover.
    """
    if not visits:
        return None
    staleness_hours = []
    sorted_visits = sorted(visits)
    for ts in change_times:
        # first visit >= ts
        lo, hi = 0, len(sorted_visits)
        while lo < hi:
            mid = (lo + hi) // 2
            if sorted_visits[mid] < ts:
                lo = mid + 1
            else:
                hi = mid
        if lo < len(sorted_visits):
            staleness_hours.append((sorted_visits[lo] - ts).total_seconds() / 3600.0)
    if not staleness_hours:
        return None
    return sum(staleness_hours) / len(staleness_hours)


async def _backtest_one(
    conn: asyncpg.Connection, source_key: str, harvest_interval_hours: int,
    computed_interval_hours: int, window_start: datetime, now: datetime,
) -> dict:
    change_rows = await conn.fetch(
        """SELECT ve.observed_at FROM vehicle_event ve
           JOIN entity_source es ON es.entity_ulid = ve.entity_ulid
           WHERE es.source_key = $1 AND ve.observed_at >= $2 AND ve.observed_at < $3""",
        source_key, window_start, now,
    )
    change_times = [r["observed_at"] for r in change_rows]

    static_visits = _simulate_schedule(window_start, now, harvest_interval_hours)
    adaptive_visits = _simulate_schedule(window_start, now, computed_interval_hours)

    return {
        "source_key": source_key,
        "n_real_changes_in_window": len(change_times),
        "static_interval_hours": harvest_interval_hours,
        "static_visit_count": len(static_visits),
        "static_avg_staleness_hours": _avg_staleness_hours(change_times, static_visits),
        "adaptive_interval_hours": computed_interval_hours,
        "adaptive_visit_count": len(adaptive_visits),
        "adaptive_avg_staleness_hours": _avg_staleness_hours(change_times, adaptive_visits),
    }


async def run_backtest(
    dsn: str = DSN, *, as_of: datetime | None = None, lookback_days: int = DEFAULT_LOOKBACK_DAYS,
) -> dict:
    now = as_of or datetime.now(timezone.utc)
    window_start = now - timedelta(days=lookback_days)

    conn = await asyncpg.connect(dsn)
    try:
        source_keys = [
            r["source_key"] for r in
            await conn.fetch("SELECT source_key FROM source_health ORDER BY source_key")
        ]

        qualified: list[dict] = []
        exploratory: list[dict] = []

        for source_key in source_keys:
            est = await estimate_change_rate(
                conn, source_key, lookback_days=lookback_days, min_windows=MIN_WINDOWS, now=now,
            )
            if est is not None:
                harvest_interval_hours = await conn.fetchval(
                    "SELECT harvest_interval_hours FROM source_health WHERE source_key=$1", source_key,
                )
                backtest = await _backtest_one(
                    conn, source_key, harvest_interval_hours, est.computed_interval_hours,
                    window_start, now,
                )
                backtest["n_visited_windows"] = est.n_visited
                backtest["n_unchanged_windows"] = est.n_unchanged
                backtest["lambda_per_hour"] = est.lambda_per_hour
                qualified.append(backtest)
                continue

            # Exploratory, relaxed threshold — LOW CONFIDENCE, illustrative only.
            est_relaxed = await estimate_change_rate(
                conn, source_key, lookback_days=lookback_days, min_windows=2, now=now,
            )
            if est_relaxed is not None:
                harvest_interval_hours = await conn.fetchval(
                    "SELECT harvest_interval_hours FROM source_health WHERE source_key=$1", source_key,
                )
                backtest = await _backtest_one(
                    conn, source_key, harvest_interval_hours, est_relaxed.computed_interval_hours,
                    window_start, now,
                )
                backtest["n_visited_windows"] = est_relaxed.n_visited
                backtest["n_unchanged_windows"] = est_relaxed.n_unchanged
                backtest["lambda_per_hour"] = est_relaxed.lambda_per_hour
                exploratory.append(backtest)

        return {
            "as_of": now.isoformat(),
            "lookback_days": lookback_days,
            "total_sources": len(source_keys),
            "qualified_production_min_windows": MIN_WINDOWS,
            "qualified": qualified,
            "exploratory_relaxed_min_windows_2": exploratory,
        }
    finally:
        await conn.close()


def _print_report(report: dict) -> None:
    print("=" * 78)
    print("F4 ADAPTIVE CADENCE BACKTEST")
    print(f"  as_of:          {report['as_of']}")
    print(f"  lookback_days:  {report['lookback_days']}")
    print(f"  total sources:  {report['total_sources']}")
    print(f"  qualified (production MIN_WINDOWS={report['qualified_production_min_windows']}): "
          f"{len(report['qualified'])}")
    print("=" * 78)

    for b in report["qualified"]:
        delta_staleness = None
        if b["static_avg_staleness_hours"] is not None and b["adaptive_avg_staleness_hours"] is not None:
            delta_staleness = b["adaptive_avg_staleness_hours"] - b["static_avg_staleness_hours"]
        print(f"\n[QUALIFIED] {b['source_key']}")
        print(f"  n_visited_windows={b['n_visited_windows']} n_unchanged={b['n_unchanged_windows']} "
              f"lambda/h={b['lambda_per_hour']:.6f}")
        print(f"  real changes observed in window: {b['n_real_changes_in_window']}")
        print(f"  STATIC   interval={b['static_interval_hours']}h  visits={b['static_visit_count']}  "
              f"avg_staleness={b['static_avg_staleness_hours']}")
        print(f"  ADAPTIVE interval={b['adaptive_interval_hours']}h  visits={b['adaptive_visit_count']}  "
              f"avg_staleness={b['adaptive_avg_staleness_hours']}")
        if delta_staleness is not None:
            pct = (delta_staleness / b["static_avg_staleness_hours"] * 100.0) if b["static_avg_staleness_hours"] else None
            print(f"  DELTA staleness (adaptive - static): {delta_staleness:+.2f}h"
                  + (f" ({pct:+.1f}%)" if pct is not None else ""))
        visit_delta = b["adaptive_visit_count"] - b["static_visit_count"]
        print(f"  DELTA visit count (adaptive - static): {visit_delta:+d}")

    print("\n" + "=" * 78)
    print(f"EXPLORATORY (relaxed min_windows=2, LOW CONFIDENCE, illustrative only, "
          f"NOT rollout-eligible): {len(report['exploratory_relaxed_min_windows_2'])}")
    print("=" * 78)
    for b in report["exploratory_relaxed_min_windows_2"]:
        delta_staleness = None
        if b["static_avg_staleness_hours"] is not None and b["adaptive_avg_staleness_hours"] is not None:
            delta_staleness = b["adaptive_avg_staleness_hours"] - b["static_avg_staleness_hours"]
        print(f"\n[EXPLORATORY] {b['source_key']} (n_visited={b['n_visited_windows']}, "
              f"n_unchanged={b['n_unchanged_windows']}) — LOW CONFIDENCE")
        print(f"  STATIC   interval={b['static_interval_hours']}h  visits={b['static_visit_count']}  "
              f"avg_staleness={b['static_avg_staleness_hours']}")
        print(f"  ADAPTIVE interval={b['adaptive_interval_hours']}h  visits={b['adaptive_visit_count']}  "
              f"avg_staleness={b['adaptive_avg_staleness_hours']}")
        if delta_staleness is not None:
            print(f"  DELTA staleness (adaptive - static): {delta_staleness:+.2f}h")
        visit_delta = b["adaptive_visit_count"] - b["static_visit_count"]
        print(f"  DELTA visit count (adaptive - static): {visit_delta:+d}")
    print("=" * 78)


def main() -> None:
    parser = argparse.ArgumentParser(description="F4 adaptive cadence backtest against real history.")
    parser.add_argument("--as-of", type=str, default=None, help="ISO8601 instant to backtest as of (default: now).")
    parser.add_argument("--lookback-days", type=int, default=DEFAULT_LOOKBACK_DAYS)
    args = parser.parse_args()

    as_of = datetime.fromisoformat(args.as_of).astimezone(timezone.utc) if args.as_of else None
    report = asyncio.run(run_backtest(as_of=as_of, lookback_days=args.lookback_days))
    _print_report(report)


if __name__ == "__main__":
    main()
