"""STABLE public API of the anti-detection engine — what discovery sessions use.

Discovery sessions that census coches.net / autoscout24 / milanuncios import from
HERE, not from the internals. This surface is the contract: its signatures are
kept backward-compatible. Internals (fingerprints, ban_detector, tier1, clearance
cache, proxy pool) may change freely behind it.

ENGINE_API_VERSION is bumped on any breaking change to this surface so a caller
can assert compatibility.

Quick start
-----------
    from pipeline.engine.api import open_session, fetch

    # one-off open-platform fetch (Tier-0, rotating fingerprint):
    html = fetch("https://www.autocasion.com/")

    # a hard Tier-1 marketplace (coches.net / autoscout24), browser-assisted:
    html = fetch("https://www.coches.net/segunda-mano/", tier1=True)

    # a reusable session for a whole drain (one fingerprint + cookie jar):
    s = open_session(tier1=True)
    for url in pages:
        html = s.fetch_text(url)        # Tier-0; escalates to Tier-1 on a block

    # close a dealer from whatever source answers first (route-around):
    from pipeline.engine.api import fetch_dealer
    res = fetch_dealer({"own_site": "...", "coches_net": "..."})
    if res.ok: use(res.html, res.resolved_source)
"""
from __future__ import annotations

from pipeline.engine.fetch import FetchEngine, FetchError, fetch_text
from pipeline.engine import source_fallback
from pipeline.engine.source_fallback import ResolveResult, SourceCandidate

ENGINE_API_VERSION = "1.0.0"

__all__ = [
    "ENGINE_API_VERSION",
    "open_session",
    "fetch",
    "fetch_dealer",
    "FetchEngine",
    "FetchError",
    "ResolveResult",
    "SourceCandidate",
]


def open_session(*, tier1: bool = False, headful: bool = False,
                 impersonate: str | None = None,
                 tier1_engines: tuple[str, ...] | None = None,
                 proxy: str | None = None, auto_proxy_refresh: bool = False,
                 polite_min: float = 0.7, polite_max: float = 1.4) -> FetchEngine:
    """Create a reusable fetch session (one coherent fingerprint + cookie jar).

    tier1=True enables automatic Tier-1 escalation (real browser + cookie-reuse)
    when Tier-0 hits a challenge/ban. headful is forced for Tier-1 by default
    (DataDome flags headless); leave it False to use the headful browser.
    auto_proxy_refresh=True harvests live free proxies (vía #2) into the egress
    pool before the drain (cost-zero, best-effort).
    """
    return FetchEngine(
        impersonate=impersonate,
        allow_tier1_escalation=tier1,
        tier1_engines=tier1_engines,
        tier1_headless=headful,
        proxy=proxy,
        auto_proxy_refresh=auto_proxy_refresh,
        polite_min=polite_min,
        polite_max=polite_max,
    )


def fetch(url: str, *, tier1: bool = False, headers: dict | None = None) -> str:
    """One-call fetch. tier1=True forces the browser-assisted Tier-1 path.

    Returns decoded HTML/text, or raises FetchError (never a challenge/block body).
    """
    if not tier1:
        return fetch_text(url, headers=headers)
    eng = open_session(tier1=True)
    return eng.fetch_text(url, tier=1, headers=headers)


def fetch_dealer(refs: dict[str, str], *,
                 session: FetchEngine | None = None) -> ResolveResult:
    """Close a dealer's inventory from the first source that answers (route-around).

    `refs` maps source_key -> url (e.g. {"own_site": "...", "coches_net": "..."}).
    Sources are tried by built-in priority (own site first, hard marketplaces last
    with Tier-1). Returns a ResolveResult; `.ok` is False only if ALL sources fail.
    """
    eng = session or open_session(tier1=True)
    candidates = source_fallback.build_candidates(refs)
    return source_fallback.fetch_first_available(candidates, fetch_text=eng.fetch_text)
