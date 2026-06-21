"""DealerProbe connector — generic €0 own-site dealer auto-harvester (cascade + cage).

Built on the pure, unit-tested classifiers in `dealerprobe.py` (sitemap / JSON-LD / microdata /
SSR). NO per-dealer REGISTRY — the recon proved 80% of inventory hangs off self-describing
signals. Cascade per domain: robots.txt -> sitemap discovery -> car sitemaps -> per-vehicle URL
frontier -> PDP fetch -> JSON-LD || microdata || SSR. The dealer is the OWNER (own-site stock,
no marketplace edge), source_key 'dealerprobe_ownsite'.

Component 4a (this commit): the async sitemap frontier — pure cascade logic, fetch injected, so
it is fully unit-testable offline. The cage/upsert + CLI land in 4b reusing the wholesale spine.
"""
from __future__ import annotations

import re
from collections.abc import Awaitable, Callable

from pipeline.platform.dealerprobe import classify_loc, is_vehicle_sitemap

DP_SOURCE_KEY = "dealerprobe_ownsite"

_LOC_RE = re.compile(r"<loc>\s*(.*?)\s*</loc>", re.I | re.S)
_ROBOTS_SITEMAP_RE = re.compile(r"(?im)^\s*sitemap:\s*(\S+)")
_SITEMAP_CANDIDATES = ("/sitemap.xml", "/sitemap_index.xml", "/sitemap-index.xml")
_MAX_SITEMAPS_FETCHED = 60          # guardrail: never chase an unbounded index tree


async def probe_sitemap_frontier(
    fetch: Callable[[str], Awaitable[str | None]],
    domain: str,
    cap: int = 500,
) -> list[str]:
    """Return up to `cap` per-vehicle detail URLs discovered through the dealer's car sitemaps.

    `fetch` is an injected async (url) -> body|None (the governor-wrapped curl in production, a
    fake in tests). Walks robots.txt -> declared sitemaps (or /sitemap.xml fallbacks), expands
    <sitemapindex> following ONLY car-named children (is_vehicle_sitemap) + nested indexes, and
    from each <urlset> keeps the <loc>s that classify_loc()s as per_vehicle. Order-preserving,
    de-duplicated, bounded by `cap` and a hard sitemap-fetch ceiling.
    """
    base = (domain if domain.startswith("http") else f"https://{domain}").rstrip("/")

    robots = await fetch(f"{base}/robots.txt")
    sitemaps = [m.group(1).strip() for m in _ROBOTS_SITEMAP_RE.finditer(robots)] if robots else []
    if not sitemaps:
        sitemaps = [base + c for c in _SITEMAP_CANDIDATES]

    queue = list(dict.fromkeys(sitemaps))
    seen_sm: set[str] = set()
    seen_url: set[str] = set()
    frontier: list[str] = []
    fetched = 0

    while queue and len(frontier) < cap and fetched < _MAX_SITEMAPS_FETCHED:
        sm = queue.pop(0)
        if sm in seen_sm:
            continue
        seen_sm.add(sm)
        xml = await fetch(sm)
        fetched += 1
        if not xml:
            continue
        locs = _LOC_RE.findall(xml)
        if "<sitemapindex" in xml.lower():
            for loc in locs:                       # an index of sub-sitemaps
                if loc not in seen_sm and (is_vehicle_sitemap(loc) or "index" in loc.lower()):
                    queue.append(loc)
        else:
            for loc in locs:                       # a urlset of pages
                if loc in seen_url:
                    continue
                if classify_loc(loc) == "per_vehicle":
                    seen_url.add(loc)
                    frontier.append(loc)
                    if len(frontier) >= cap:
                        break
    return frontier
