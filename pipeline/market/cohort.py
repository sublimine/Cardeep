"""Shared cohort/percentile helper — the canonical median-by-cohort implementation.

00-MASTER.md resolution C-1/C-12: this pilar (01-market-intelligence) is the FIRST to
build a percentile/median/window helper, so it factors it here ONCE. Pilares 03
(garage-fleet K9/K10/K11), 04 (arbitrage cohort helper), 06/07/09 import from this
module instead of re-deriving their own median-by-cohort logic. A second independent
percentile/median implementation anywhere else in the codebase is a duplication bug,
not a design choice (00-MASTER.md C-1).

``percentile_cont`` is a pure-Python reimplementation of PostgreSQL's
``percentile_cont(q) WITHIN GROUP (ORDER BY x)`` (continuous, linear-interpolation
percentile) — used as the OFFLINE cross-check leg of the verification protocol
(01-market-intelligence.md §7, row 1: "Recomputo offline en Python puro ... sobre un
dump muestral del mismo segmento"). It must stay numerically identical to Postgres'
formula, not merely "a reasonable percentile" — the whole point is an independent
recomputation that can catch a SQL bug.
"""
from __future__ import annotations

from typing import Any, NamedTuple, Sequence

import asyncpg

# Anti-ruido de cohorte (patrón iSeeCars, adoptado en toda la carta 01-market-intelligence
# para M1/M3/M4/M5/M7/M9/M10): por debajo de este tamaño de muestra NUNCA se publica un
# número — la fila se suprime (o cae a un fallback de mayor agregación, p.ej. nacional).
MIN_COHORT_N: int = 8

# Versión de metodología del cómputo de mercado (bump cuando cambie una fórmula M*, un
# corte, o una regla de exclusión — el cambio de METODOLOGÍA lo gatea un modelo caro
# per §8 de la carta, no se hace en silencio).
METHODOLOGY_VERSION: str = "v1"

# Ventana ±1 año del "banda de año" de M1 (carta §4, fila M1): el segmento se ancla en un
# año "anchor" y agrupa vehicle.year IN (anchor-1, anchor, anchor+1). Documentado aquí
# como constante compartida en vez de un número mágico repetido en cada query.
YEAR_BAND_RADIUS: int = 1


def percentile_cont(sorted_values: Sequence[float], q: float) -> float:
    """Pure-Python reimplementation of PostgreSQL's ``percentile_cont(q)``.

    ``sorted_values`` MUST already be sorted ascending (caller's responsibility — this
    function does not sort, so a mis-sorted input silently returns a wrong percentile
    instead of failing loud; callers in this codebase always sort immediately before
    calling, see ``compute_stats.py``).

    Formula (matches PostgreSQL's ordered-set aggregate exactly, 1-indexed RN):
        RN = 1 + q * (N - 1)
        CRN = floor(RN)
        FRN = RN - CRN
        result = x[CRN] + FRN * (x[CRN+1] - x[CRN])   (0-indexed: x[CRN-1], x[CRN])
    with the boundary CRN >= N clamped to the last element (q=1.0 case).
    """
    n = len(sorted_values)
    if n == 0:
        raise ValueError("percentile_cont: empty input")
    if n == 1:
        return float(sorted_values[0])
    if not (0.0 <= q <= 1.0):
        raise ValueError(f"percentile_cont: q must be in [0,1], got {q}")

    rn = 1 + q * (n - 1)
    crn = int(rn)  # floor, since rn >= 1 > 0
    frn = rn - crn

    if crn >= n:
        return float(sorted_values[-1])

    lo = float(sorted_values[crn - 1])
    hi = float(sorted_values[crn]) if crn < n else lo
    return lo + frn * (hi - lo)


def median(sorted_values: Sequence[float]) -> float:
    """p50 via ``percentile_cont`` — the single canonical median implementation."""
    return percentile_cont(sorted_values, 0.5)


def divergence_pct(a: float, b: float) -> float:
    """Relative divergence between two values, as a percentage of the larger magnitude.

    Symmetric-ish and zero-safe: when both are 0, divergence is 0 (identical); when only
    one is 0, divergence is 100% (cannot express a percentage relative to 0 meaningfully,
    so the two are simply "fully divergent"). Used by the SQL-vs-Python cross-check
    (tolerance <0.5%, §7 of the carta) and by the run-over-run ±3% publication gate.
    """
    if a == 0 and b == 0:
        return 0.0
    denom = max(abs(a), abs(b))
    if denom == 0:
        return 100.0
    return abs(a - b) / denom * 100.0


def year_band(anchor_year: int, radius: int = YEAR_BAND_RADIUS) -> tuple[int, int]:
    """Return the inclusive ``(low, high)`` year window for a M1-style ±radius band."""
    return anchor_year - radius, anchor_year + radius


# ---------------------------------------------------------------------------
# F2 — dynamic window handling (01-market-intelligence-f0.md gate: real span=35
# days at F0 measurement time, < the 90/45/30d nominal windows the carta names).
# ---------------------------------------------------------------------------

# Nominal (target) windows per metric, per carta §4. NEVER used directly on a young
# corpus — always passed through ``effective_window_days`` first, which clamps to the
# actual observed history so the product never claims a 90-day view of a 35-day system.
NOMINAL_WINDOW_DAYS_M3: int = 90   # days-to-retirada rolling window
NOMINAL_WINDOW_DAYS_M4: int = 45   # Market Days Supply (vAuto standard)
NOMINAL_WINDOW_DAYS_M5: int = 30   # provincial absorption rate
NOMINAL_WINDOW_DAYS_M9: int = 30   # seller price-pressure window
# M7 momentum needs TWO non-overlapping windows (60d canonical) — handled separately
# via ``m7_half_window_days`` below, not a single nominal constant.
M7_NOMINAL_HALF_DAYS: int = 30


async def get_span_days(conn: asyncpg.Connection) -> float:
    """Real observed span of vehicle_event.observed_at, in days (float, sub-day precision).

    Queried FRESH on every call (never cached/hardcoded) — the whole point of the F0 gate
    is that this number grows over time and each run must react to the CURRENT reality,
    not the 35-day figure measured when F0 was written.
    """
    row = await conn.fetchrow("SELECT min(observed_at) AS mn, max(observed_at) AS mx FROM vehicle_event")
    if row is None or row["mn"] is None or row["mx"] is None:
        return 0.0
    return (row["mx"] - row["mn"]).total_seconds() / 86400.0


def effective_window_days(nominal_days: int, span_days: float) -> float:
    """The window a metric ACTUALLY uses today: min(nominal, observed span).

    A young corpus (span < nominal) gets an honestly-reduced window instead of a fake
    90/45/30-day claim (01-market-intelligence-f0.md §3 gate). Once the corpus ages past
    the nominal window, this simply returns the nominal value unchanged — the reduction
    is temporary by construction, not a permanent product decision.
    """
    if span_days <= 0:
        return float(nominal_days)
    return min(float(nominal_days), span_days)


def m7_half_window_days(span_days: float, nominal_half: int = M7_NOMINAL_HALF_DAYS) -> float:
    """Half-window size for M7's early/late comparison.

    Canonical M7 wants two non-overlapping ``nominal_half``-day windows (60d total). When
    the observed span can't cover that (span < 2*nominal_half), each half is shrunk to
    span/2 — a smaller, honestly-labelled comparison — rather than silently reusing full
    30-day windows that would overlap or reach before the corpus existed.
    """
    if span_days >= 2 * nominal_half:
        return float(nominal_half)
    return span_days / 2.0


class SegmentStat(NamedTuple):
    """Canonical per-row shape for every F2 metric written to ``market_stat``.

    Distinct from F1's ``M1Row`` (kept untouched to avoid regressing the already-verified
    M1 path) but structurally a superset: F2 metrics are scalar (``value_num`` +
    ``value_extra`` for a secondary figure) rather than a p25/p50/p75 distribution, except
    M10 which reuses p25/p50/p75 to describe a platform-count distribution (documented at
    its call site).
    """
    scope: str  # 'prov' | 'nat'
    make: str | None
    model: str | None
    fuel: str | None
    province_code: str | None
    year: int | None
    n: int
    p25: float | None = None
    p50: float | None = None
    p75: float | None = None
    value_num: float | None = None
    value_extra: dict[str, Any] | None = None
