"""Ingest-boundary numeric field sanity — reject UNAMBIGUOUS junk in price / km / year
(audit P2 A-junk-sentinel-prices + A-km-year-outliers).

Calibrated against the live data (2026-06-15):
  - price: legit used-market ceiling ~€2.2M (Lamborghini Countach, Aston Valour), so >€10M is always a
    parse/typo error (Peugeot 206 at €999,999,999; VW Tiguan at €250M); <=0 is an "ask for price"
    placeholder. Both -> None.
  - km: physically impossible above ~1.5M (artifacts were digit-concatenations up to 5,000,000 km and a
    repeated 5,000,000 sentinel); negative is invalid. -> None.
  - year: a future year beyond next model-year is a parse artifact ('SEAT Ibiza 2098', 'Clase GLC 2060',
    field-misalignment); pre-1900 is implausible (genuine classics start ~1900). -> None. Bound is
    dynamic (current year + 1) so it never goes stale.

The car/row STAYS servable; only the impossible field reads as unknown instead of distorting every
km/age/price distribution. DELIBERATELY NOT handled (Law I — under-correct over mis-correct): mid-range
model-implausible price junk (a 2005 Peugeot 407 at €2M beside a legit €2.2M hypercar) and low-side
deposit placeholders — those need the model-aware price_trap detector, not a flat threshold.
"""
from __future__ import annotations

from datetime import datetime

# Verified ceiling: legit used-market max ~€2.2M; >€10M is unambiguously a typo/parse error.
PRICE_MAX = 10_000_000
# A car above ~1.5M km is a digit-concatenation artifact (legit high-mileage commercials stay under ~1M).
KM_MAX = 1_500_000
# Genuine vehicles start ~1900; future years beyond next model-year are parse artifacts.
YEAR_MIN = 1900


def sanitize_price(price):
    """Return *price* unchanged, or None if it is unambiguous junk (<=0 or > €10M)."""
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
