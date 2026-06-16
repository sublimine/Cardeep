"""Ingest-boundary numeric field sanity — reject UNAMBIGUOUS junk in price / km / year
(audit P2 A-junk-sentinel-prices + A-km-year-outliers).

Calibrated against the live data (2026-06-15, re-tightened 2026-06-16 after a served-surface
coherence audit):
  - price: the REAL used-market ceiling in this corpus is ~€3.6M (Bugatti Chiron €3.5-3.6M, Aston
    Valkyrie €3.3M, Lamborghini Countach LPI €2.65M — all verified legit live). The old €10M ceiling
    let through 34 served sentinels — a Nissan Qashqai at €10,000,000, trucks at €9,999,999 ("all-9s"
    price-on-request sentinel), a Fiat 500L at €10M — i.e. a visible lie at the served surface. The
    ceiling is now €5M: above every real hypercar (€3.6M) with margin, below the €9.99M/€10M sentinels.
    <=0 is an "ask for price" placeholder. Both -> None. (A €3.33M Renault Kadjar — model-implausible
    mid-range junk — is DELIBERATELY left to the model-aware price_trap detector, not this flat gate;
    a flat threshold cannot tell a €3.33M Kadjar from a €3.5M Chiron without model awareness.)
  - km: physically impossible above ~1.5M (artifacts were digit-concatenations up to 5,000,000 km and a
    repeated 5,000,000 sentinel); negative is invalid. -> None.
  - year: a future year beyond next model-year is a parse artifact ('SEAT Ibiza 2098', 'Clase GLC 2060',
    field-misalignment); pre-1900 is implausible (genuine classics start ~1900). -> None. Bound is
    dynamic (current year + 1) so it never goes stale.
  - year×km CROSS (audit 2026-06-16): each field can pass its own gate yet be jointly IMPOSSIBLE — a
    year>=current (age ~0) with huge km (VW Caravelle 2026 @ 600,000 km; VW Passat 2026 @ 420,000 km —
    both served). 36 such impossible-age rows (year>=2026 ∧ km>300k) were cleaned to year=km=NULL: NULL
    BOTH, because which field is the parse error is PRICE-dependent and ambiguous (€3,500/600k = old van,
    YEAR wrong; €100k/500k CUPRA Born = new car, KM wrong) — no single-field NULL is safe. SYSTEMATIC
    gap (scoped, not hacked at depth): a cross-field gate `(current_year - year) <= 0 AND km > ~300k ->
    NULL both` wired at ingest; the 150k-300k band is left out (model-year-vs-registration fuzz makes it
    ambiguous). This flat per-field module is the wrong home for the model/price-aware disambiguation.

The car/row STAYS servable; only the impossible field reads as unknown instead of distorting every
km/age/price distribution. DELIBERATELY NOT handled here (Law I — under-correct over mis-correct), and
a flat threshold CANNOT handle it: model-implausible price junk in the legit-hypercar band — a
mass-market make at €2-4M (Renault Kadjar @ €3,333,333, Ford @ €3.8M, verified served 2026-06-16)
sitting beside a genuine €3.6M Bugatti Chiron. A flat ceiling that nulls one nulls the other.
  KNOWN GAP (audit 2026-06-16): this HIGH model-implausible band is currently caught by NEITHER gate —
  the flat ceiling (€5M) is above it, and the `price_trap` detector targets the LOW band (~€49-999
  monthly-payment-as-price), not the high band. ~30 served rows (0.002%); tracked, not hacked.
  The fix needs care: a NAIVE "price > 10×median(make+model)" detector was tested read-only and
  over-caught 601 rows with catastrophic false positives — it flagged a real €3.65M Ferrari LaFerrari
  (its median is €200 because LOW-junk listings poison it), a real €55k BMW M3 (median €200), etc. So
  the robust detector must NOT trust a raw median: filter the low-junk first (or use a high percentile /
  MAD on a cleaned distribution) before flagging high outliers. A hasty version nulls real hypercars —
  worse than the 0.002% it fixes. Deferred to a focused, carefully-calibrated unit (Law I).
"""
from __future__ import annotations

from datetime import datetime

# Verified ceiling: real used-market max ~€3.6M (Bugatti Chiron); >€5M is unambiguously a sentinel/
# parse error (Qashqai @ €10M, trucks @ €9,999,999). €5M keeps every real hypercar, kills the sentinels.
PRICE_MAX = 5_000_000
# A car above ~1.5M km is a digit-concatenation artifact (legit high-mileage commercials stay under ~1M).
KM_MAX = 1_500_000
# Genuine vehicles start ~1900; future years beyond next model-year are parse artifacts.
YEAR_MIN = 1900


def sanitize_price(price):
    """Return *price* unchanged, or None if it is unambiguous junk (<=0 or > €5M)."""
    if price is None:
        return None
    try:
        p = float(price)
    except (TypeError, ValueError):
        return None
    if p <= 0 or p > PRICE_MAX:
        return None
    return price


def sanitize_km(km):
    """Return *km* unchanged, or None if physically impossible (<0 or > 1.5M km)."""
    if km is None:
        return None
    try:
        k = int(km)
    except (TypeError, ValueError):
        return None
    if k < 0 or k > KM_MAX:
        return None
    return km


def sanitize_year(year):
    """Return *year* unchanged, or None if a parse artifact (< 1900 or > next model-year)."""
    if year is None:
        return None
    try:
        y = int(year)
    except (TypeError, ValueError):
        return None
    if y < YEAR_MIN or y > datetime.now().year + 1:
        return None
    return year


def sanitize_year_km(year, km):
    """Cross-field impossible-age gate (audit P8). Each field can pass its own gate yet be JOINTLY
    impossible: a ~0-1-year-old vehicle cannot have accumulated huge km. Returns (year, km) unchanged,
    or (None, None) when jointly impossible — NULL BOTH, because which field is the parse error
    (year wrong vs km wrong) is ambiguous and price-dependent, so nulling one would guess wrong. The
    car/row STAYS servable; only the impossible pair reads as unknown instead of distorting every
    age/km distribution.

    Conservative (Law I — under-correct over mis-correct): only the UNAMBIGUOUS band, beyond any
    legitimate intensive-commercial use (extreme long-haul peaks ~150-200k km/yr):
      - age <= 0 (current model-year or newer) AND km > 300,000  -> impossible in < 1 year;
      - age <= 1 (<= 1 model-year old)          AND km > 500,000  -> impossible in < ~1.5 years.
    The 150k-500k band on a 1-year car is DELIBERATELY left (model-year-vs-registration fuzz +
    intensive-commercial legitimacy) — see the module docstring's year x km CROSS note.
    """
    if year is None or km is None:
        return year, km
    try:
        y = int(year)
        k = int(km)
    except (TypeError, ValueError):
        return year, km
    age = datetime.now().year - y
    if (age <= 0 and k > 300_000) or (age <= 1 and k > 500_000):
        return None, None
    return year, km
