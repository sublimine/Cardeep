"""F6 (00-marketplace-engine.md) — uptime track record computed from engine_heartbeat_log.

Pure bucketing/window logic lives here with ZERO database-driver imports at module level, so it
can be imported safely from BOTH:
  - pipeline/ops/scheduler.py and one-off report scripts (sync psycopg2 context), and
  - services/api/routers/ops.py (async asyncpg context, GET /engine/status)
without pulling a blocking sync driver (psycopg2) into the async FastAPI process, or an asyncpg
dependency into a sync CLI. Each caller fetches beat_at timestamps with its OWN driver and passes
a plain ``list[datetime]`` in — the math itself (bucket_uptime) is 100% pure and is the unit-test
surface (no DB needed), mirroring the pattern already used by pipeline/ops/lock_heartbeat.py
(is_lease_stale) and pipeline/ops/engine_watchdog.py (classify_engine_status).

Honesty guard (anti-alucinación doctrine, CLAUDE.md). engine_heartbeat_log did not exist before
migration 0085 (F6 of this carta). A naive "30-day uptime" query run the day this ships would see
~90 days with ZERO ledger rows before today and, if that gap were counted as downtime, would
falsely report ~0% uptime for a motor that was in fact LATIENDO the whole time — simply
unobserved. clipped_window()/bucket_uptime() never do this: the requested window is always
clipped to [observed_since, now) and the caller is told whether the FULL requested window was
actually observed (``full_window_available``), so the API can render "solo N días observados de
M solicitados" instead of a fabricated bad number dressed up as a real track record.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence

# Same 15-minute granularity as the harvest tick (scheduler.py TICK_INTERVAL_MINUTES) — a LOCAL
# constant, not an import: this module must not share an import graph with what it measures (same
# reasoning as pipeline/ops/engine_watchdog.py's own local ENGINE_STALE_THRESHOLD_MINUTES).
DEFAULT_BUCKET_MINUTES: int = 15


def _as_aware_utc(ts: datetime) -> datetime:
    """Coerce a datetime to a tz-aware UTC instant (naive == already UTC)."""
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


# ---------------------------------------------------------------------------
# Window clipping — the anti-alucinación guard
# ---------------------------------------------------------------------------

def clipped_window(
    *,
    now: datetime,
    requested_days: int,
    observed_since: Optional[datetime],
) -> tuple[datetime, datetime, bool]:
    """Return (window_start, window_end, full_window_available) for a requested N-day lookback.

    ``window_end`` is always ``now``. ``window_start`` is ``now - requested_days`` UNLESS the
    ledger's observed history (``observed_since``, the earliest beat_at ever recorded for this
    lock_key) starts later — in which case ``window_start`` clips to ``observed_since`` and
    ``full_window_available`` is False, so the caller renders "solo N días observados de M
    solicitados" instead of silently reporting a lower percentage indistinguishable from real
    downtime.

    ``observed_since=None`` (no ledger rows yet, e.g. migration just applied) clips to a
    zero-width window at ``now`` — bucket_uptime() on that returns buckets_total=0 / uptime_pct
    =None ("no data yet"), never "0% uptime".
    """
    now_u = _as_aware_utc(now)
    requested_start = now_u - timedelta(days=requested_days)
    if observed_since is None:
        return now_u, now_u, False
    obs = _as_aware_utc(observed_since)
    if obs <= requested_start:
        return requested_start, now_u, True
    return obs, now_u, False


# ---------------------------------------------------------------------------
# Bucketing — the pure percentage-of-windows-with-a-beat computation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class UptimeReport:
    """Result of bucket_uptime(): bucket counts + percentage over the OBSERVED span only."""

    window_start: datetime
    window_end: datetime
    bucket_minutes: int
    buckets_total: int
    buckets_with_beat: int
    uptime_pct: Optional[float]  # None when buckets_total == 0 (nothing to compute — not 0%)


def bucket_uptime(
    beat_times: Sequence[datetime],
    *,
    window_start: datetime,
    window_end: datetime,
    bucket_minutes: int = DEFAULT_BUCKET_MINUTES,
) -> UptimeReport:
    """Partition [window_start, window_end) into fixed ``bucket_minutes`` windows and report the
    percentage that contain >=1 heartbeat.

    Pure — no DB, no I/O, no wall-clock read. ``beat_times`` may be unsorted and may contain
    timestamps outside [window_start, window_end) (a caller that over-fetches slightly is fine;
    out-of-range beats are ignored, never counted).

    A window with ``window_end <= window_start`` (e.g. the zero-width window
    ``clipped_window()`` returns when there is no observed history yet) reports
    buckets_total=0 / uptime_pct=None rather than dividing by zero or claiming 0%/100%.

    The final bucket may be shorter than ``bucket_minutes`` when the span is not an exact
    multiple — it is still counted as one full bucket in ``buckets_total``, never penalized or
    inflated for being short: the question answered is always "did the motor beat at least once
    during this real span", not "was every bucket exactly N minutes wide".
    """
    start = _as_aware_utc(window_start)
    end = _as_aware_utc(window_end)
    if end <= start:
        return UptimeReport(start, end, bucket_minutes, 0, 0, None)

    delta = timedelta(minutes=bucket_minutes)
    beats = sorted(
        _as_aware_utc(b) for b in beat_times if start <= _as_aware_utc(b) < end
    )

    buckets_total = 0
    buckets_with_beat = 0
    cursor = start
    beat_idx = 0
    n_beats = len(beats)
    while cursor < end:
        bucket_end = min(cursor + delta, end)
        buckets_total += 1
        has_beat = False
        while beat_idx < n_beats and beats[beat_idx] < bucket_end:
            # Invariant: beats < cursor were already consumed by prior buckets, so any beat not
            # yet consumed here is automatically >= cursor — this holds because beat_idx only
            # ever advances forward across buckets processed in increasing time order.
            has_beat = True
            beat_idx += 1
        if has_beat:
            buckets_with_beat += 1
        cursor = bucket_end

    pct = (100.0 * buckets_with_beat / buckets_total) if buckets_total else None
    return UptimeReport(start, end, bucket_minutes, buckets_total, buckets_with_beat, pct)


def uptime_report_to_dict(report: UptimeReport, *, requested_days: int, full_window_available: bool) -> dict:
    """Serialize an UptimeReport + its clipping metadata into the JSON shape GET /engine/status
    exposes. Isolated as its own function so the API route and any future report script (or a
    test) build byte-identical payloads.
    """
    return {
        "requested_days": requested_days,
        "full_window_available": full_window_available,
        "observed_from": report.window_start.isoformat(),
        "observed_to": report.window_end.isoformat(),
        "bucket_minutes": report.bucket_minutes,
        "buckets_total": report.buckets_total,
        "buckets_with_beat": report.buckets_with_beat,
        "uptime_pct": round(report.uptime_pct, 2) if report.uptime_pct is not None else None,
    }
