"""AS24 (AutoScout24-ES) FACET-PARTITION harvester — breaks the /lst 200-page (~4k) cap.

The flat /lst search (autoscout24_wholesale) exposes only ~200 pages / ~4,000 cars, far below the
declared ~278k. AS24 /lst, however, honors `pricefrom`/`priceto` + `sort=price` (verified live:
band 0-2000=498, 2000-4000=2215, 4000-6000=4018). So the catalog is drained by PARTITIONING into
price bands, each under the cap, paged with a STABLE price sort (deterministic — a band drains to its
exact last page). Same idea as coches_net_facet (province + price bands); here price bands are the
clean axis (province on AS24 is a zip+radius, which doesn't map to administrative provinces).

This module reuses autoscout24_wholesale's parser + ingest (block 2, the per-band drain); block 1
here is the PURE partitioning engine: the adaptive band planner + the faceted URL builder.

Run (block 2):  python -m pipeline.platform.as24_facet [max_bands]
"""
from __future__ import annotations

from collections.abc import Callable

from pipeline.platform.autoscout24_wholesale import PAGE_SIZE, _BASE

# A single /lst search caps at ~200 pages * PAGE_SIZE. Keep a band comfortably under that so its
# last page is reachable; bands at/over this are subdivided.
FACET_CAP = 200 * PAGE_SIZE  # 4000

# Price domain to cover (EUR). Almost all listings fall well under 10M; the open top band catches any
# tail above PRICE_MAX. Bisection floor: never split a band narrower than this (avoids infinite
# recursion on a price point with > CAP identical-priced listings — accepted as a rare, declared gap).
PRICE_MAX = 1_000_000
_MIN_BAND_WIDTH = 100


def _facet_url(page: int, price_from: int, price_to: int | None) -> str:
    """A price-banded /lst URL with a STABLE price sort. price_to=None -> open-ended top band
    (priceto empty) so the tail above the last bound is still caught."""
    to = "" if price_to is None else str(price_to)
    return (f"{_BASE}/lst?atype=C&cy=E&sort=price&desc=0&size={PAGE_SIZE}&page={page}"
            f"&pricefrom={price_from}&priceto={to}")


def plan_price_bands(
    count_of: Callable[[int, int], int],
    lo: int = 0,
    hi: int = PRICE_MAX,
    min_width: int = _MIN_BAND_WIDTH,
) -> list[tuple[int, int]]:
    """Adaptive partition of [lo, hi) into contiguous price bands each with <= FACET_CAP listings.

    count_of(price_from, price_to) -> AutoScout24 numberOfResults for that band. If a band is already
    under the cap (or hit the min-width floor), keep it whole; otherwise bisect by price and recurse.
    Result is gap-free and contiguous: bands[i].to == bands[i+1].from, covering exactly [lo, hi).
    """
    total = count_of(lo, hi)
    if total <= FACET_CAP or (hi - lo) <= min_width:
        return [(lo, hi)]
    mid = (lo + hi) // 2
    return (plan_price_bands(count_of, lo, mid, min_width)
            + plan_price_bands(count_of, mid, hi, min_width))
