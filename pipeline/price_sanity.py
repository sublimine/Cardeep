"""Price sanity guard — reject UNAMBIGUOUS junk prices at the ingest boundary (audit P2 A-junk-sentinel-prices).

Calibrated against the live data (2026-06-15): the legit used-market ceiling is ~€2.2M (Lamborghini
Countach LPI 800-4, Aston Martin Valour), so anything above €10M is always a parse/typo error
(e.g. a Peugeot 206 listed at €999,999,999 or a VW Tiguan at €250M). Non-positive prices (€0 / negative)
are not real prices either ("ask for price" placeholders). Both are nulled — the car stays servable,
but its price reads as unknown instead of corrupting every average / percentile / cheapest ranking.

DELIBERATELY NOT handled here (Law I — under-correct over mis-correct): mid-range model-implausible
junk (a 2005 Peugeot 407 at €2M sits in the same band as a legit Lamborghini Countach at €2.2M) and
low-side deposit/fee placeholders (€1 / €50). Distinguishing those needs the model-aware price_trap
detector, not a flat threshold — a flat cut there would null a legit hypercar.
"""
from __future__ import annotations

# Verified ceiling: legit used-market max ~€2.2M; >€10M is unambiguously a typo/parse error.
PRICE_MAX = 10_000_000


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
