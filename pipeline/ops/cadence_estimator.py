"""F4 — per-source adaptive harvest cadence (00-marketplace-engine.md F4).

Closes the gap vs. Cho & Garcia-Molina (2003, "Estimating Frequency of Change"): the
static 4-tier harvest_interval_hours table (migration 0021: 24h/168h/720h/2160h) is blind
to how often a source's inventory actually changes. This module estimates each source's
own change rate from its OWN vehicle_event history and derives a re-visit interval from it.

Estimator (the paper's improved/Laplace-corrected MLE for a censored Poisson observation):
  Each successful harvest_run is a VISIT. A visit is CHANGED if any vehicle_event for that
  source's entities (via entity_source) falls in the same fixed window; UNCHANGED
  otherwise. Given n visited windows of length I with X unchanged, under a Poisson-process
  change model P(no change in a window) = exp(-lambda * I), so:

      lambda_hat = -ln( (X + 0.5) / (n + 1) ) / I

  The continuity correction (the paper's own device) avoids a degenerate lambda of 0
  (X == n, source never observed to change) or infinity (X == 0, changed every visit).

  computed_interval_hours = clamp(1 / lambda_hat, CADENCE_FLOOR_HOURS, CADENCE_CEIL_HOURS)
  — visit roughly once per estimated mean-time-between-changes, floored/ceilinged by the
  same safety bounds as the static tier table (never hammer more than daily, never abandon
  a source past 90 days — 00-marketplace-engine.md §5.3).

Windows that were NEVER visited contribute nothing to the sample: we cannot claim a source
was "unchanged" during a period we did not look at (this is exactly why a source whose
breaker was open for weeks must not silently corrupt its own cadence estimate).

The math (_mle_change_rate, _bucket_visited_and_changed, _clamp_interval_hours) is pure and
DB-free — see tests/test_cadence_estimator.py. estimate_change_rate() is the only DB-facing
function, reading harvest_run + vehicle_event/entity_source; apply_cadence_estimate() is the
only writer (source_health.observed_change_rate/computed_interval_hours/cadence_computed_at).
Neither ever changes cadence_mode — that is a deliberate, gradual, operator-driven flip
(scripts/enable_adaptive_cadence.py), never an automatic side effect of estimation.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import asyncpg

# Safety floor/ceiling (00-marketplace-engine.md §5.3): identical bounds to the static tier
# table's extremes (migration 0021: 24h fastest tier, 2160h = 90 days slowest).
CADENCE_FLOOR_HOURS = 24
CADENCE_CEIL_HOURS = 2160

# Minimum visited windows before an estimate is trusted; below this the sample is too thin
# (a source with a long static interval simply cannot accumulate many windows in a
# reasonable lookback) and the source stays on its static tier.
MIN_WINDOWS = 5
DEFAULT_LOOKBACK_DAYS = 60

# How the estimated mean-time-between-changes (1/lambda) maps to a re-visit interval.
# 1.0 = revisit approximately once per estimated inter-change interval — a middle ground
# between "wait for the whole MTBC" (freshest possible per request) and "revisit far more
# often than needed" (wasted requests); tunable without a migration since it only affects
# the WRITE-time computation.
REVISIT_FACTOR = 1.0


def _mle_change_rate(n_visited: int, n_unchanged: int, window_hours: float) -> float:
    """Cho & Garcia-Molina (2003) improved (Laplace-corrected) frequency estimator.

    ratio = (n_unchanged + 0.5) / (n_visited + 1): the "+0.5 / +1" continuity correction
    keeps the ratio strictly inside (0, 1) for EVERY possible (n_unchanged, n_visited) pair
    with n_visited >= 1 — including the two degenerate extremes a raw n_unchanged/n_visited
    fraction cannot handle: n_unchanged == 0 (ratio -> 0, raw fraction gives an undefined/
    infinite rate) and n_unchanged == n_visited (ratio < 1 strictly, so lambda is always
    positive — never exactly 0, since a finite sample can never PROVE a source has zero
    chance of changing). Returns the estimated change rate in changes-per-hour. Requires
    n_visited > 0 (the caller enforces MIN_WINDOWS before calling this).
    """
    ratio = (n_unchanged + 0.5) / (n_visited + 1)
    return -math.log(ratio) / window_hours


def _bucket_visited_and_changed(
    visit_times: list[datetime],
    change_times: list[datetime],
    window_start: datetime,
    window_hours: int,
    n_windows: int,
) -> tuple[int, int]:
    """Partition [window_start, window_start + n_windows*window_hours) into n_windows
    fixed-length buckets and classify each as visited/changed from raw timestamps.

    Returns (n_visited, n_unchanged). A bucket counts as VISITED if at least one timestamp
    in visit_times falls inside it; a visited bucket counts as unchanged only if ZERO
    timestamps in change_times also fall inside it. A bucket with no visit is excluded
    entirely from both counts — we cannot classify "unchanged" for a period never observed.
    Pure function: no DB, deterministic, the core of the estimator's TDD coverage.
    """
    window_delta = timedelta(hours=window_hours)
    visited_flags = [False] * n_windows
    changed_flags = [False] * n_windows

    def _bucket_index(ts: datetime) -> int | None:
        if ts < window_start:
            return None
        idx = int((ts - window_start) / window_delta)
        return idx if 0 <= idx < n_windows else None

    for ts in visit_times:
        idx = _bucket_index(ts)
        if idx is not None:
            visited_flags[idx] = True
    for ts in change_times:
        idx = _bucket_index(ts)
        if idx is not None:
            changed_flags[idx] = True

    n_visited = sum(visited_flags)
    n_unchanged = sum(1 for visited, changed in zip(visited_flags, changed_flags) if visited and not changed)
    return n_visited, n_unchanged


def _clamp_interval_hours(hours: float) -> int:
    """Floor/ceiling the computed interval (§5.3: never hammer, never abandon a source)."""
    return int(max(CADENCE_FLOOR_HOURS, min(CADENCE_CEIL_HOURS, round(hours))))


@dataclass(frozen=True)
class CadenceEstimate:
    """The F4 estimator's output for one source, ready to persist via apply_cadence_estimate."""
    source_key: str
    window_hours: int
    n_windows: int
    n_visited: int
    n_unchanged: int
    lambda_per_hour: float
    computed_interval_hours: int


async def estimate_change_rate(
    conn: asyncpg.Connection,
    source_key: str,
    *,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    min_windows: int = MIN_WINDOWS,
    window_hours: int | None = None,
    now: datetime | None = None,
) -> CadenceEstimate | None:
    """Estimate source_key's change rate from its own harvest_run + vehicle_event history.

    window_hours defaults to the source's CURRENT harvest_interval_hours (the granularity
    at which it was actually visited historically — using a finer window than the real
    visit cadence would just manufacture "never visited" buckets). Returns None when there
    is not enough sample (fewer than min_windows actually-visited windows) — the caller
    must leave the source on its static tier rather than act on a thin estimate.
    """
    now = now or datetime.now(timezone.utc)
    if window_hours is None:
        window_hours = await conn.fetchval(
            "SELECT harvest_interval_hours FROM source_health WHERE source_key=$1", source_key
        )
        if window_hours is None:
            return None  # source not registered at all — nothing to estimate

    window_start = now - timedelta(days=lookback_days)
    n_windows = int((lookback_days * 24) // window_hours)
    if n_windows < min_windows:
        return None  # the lookback is too short relative to this source's own cadence

    visit_rows = await conn.fetch(
        "SELECT started_at FROM harvest_run "
        "WHERE source_key=$1 AND ok=true AND started_at >= $2",
        source_key, window_start,
    )
    visit_times = [r["started_at"] for r in visit_rows]

    change_rows = await conn.fetch(
        """SELECT ve.observed_at
           FROM vehicle_event ve
           JOIN entity_source es ON es.entity_ulid = ve.entity_ulid
           WHERE es.source_key = $1 AND ve.observed_at >= $2""",
        source_key, window_start,
    )
    change_times = [r["observed_at"] for r in change_rows]

    n_visited, n_unchanged = _bucket_visited_and_changed(
        visit_times, change_times, window_start, window_hours, n_windows)
    if n_visited < min_windows:
        return None

    lam = _mle_change_rate(n_visited, n_unchanged, window_hours)
    mtbc_hours = (1.0 / lam) if lam > 0 else float(CADENCE_CEIL_HOURS)
    computed = _clamp_interval_hours(mtbc_hours * REVISIT_FACTOR)

    return CadenceEstimate(
        source_key=source_key,
        window_hours=window_hours,
        n_windows=n_windows,
        n_visited=n_visited,
        n_unchanged=n_unchanged,
        lambda_per_hour=lam,
        computed_interval_hours=computed,
    )


async def apply_cadence_estimate(conn: asyncpg.Connection, estimate: CadenceEstimate) -> None:
    """The single writer of observed_change_rate/computed_interval_hours/cadence_computed_at.

    Never touches cadence_mode — flipping a source to 'adaptive' is a deliberate, gradual,
    operator-driven rollout step (scripts/enable_adaptive_cadence.py), never an automatic
    side effect of computing an estimate. This lets the estimate be computed and observed
    for EVERY source before any of them actually change what the scheduler does.
    """
    await conn.execute(
        """UPDATE source_health
           SET observed_change_rate = $2,
               computed_interval_hours = $3,
               cadence_computed_at = now()
           WHERE source_key = $1""",
        estimate.source_key, estimate.lambda_per_hour, estimate.computed_interval_hours,
    )
