"""Per-entity source route-around (vía #4): close a dealer's coverage anyway.

If one source for a dealer is hard (e.g. coches.net behind DataDome), the dealer's
inventory usually exists somewhere else too: their OWN website (discovered by other
vectors), or another marketplace where they also publish. This module fetches a
dealer's inventory from an ORDERED list of candidate sources and returns the first
that yields genuine content — so the dealer's coverage closes without depending on
any single hard source.

Priority by default puts the dealer's own site first (cheapest, no marketplace WAF,
and the most complete/authoritative), then secondary marketplaces, then the hard
Tier-1 marketplace last. Each candidate fetch goes through the tiered FetchEngine,
so Tier-1 escalation (headful browser, vía #1) still applies per candidate.

This does NOT replace coches.net — vía #1 already wins it — it guarantees a dealer
is never blocked on a single source.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from pipeline.engine.fetch import FetchError


@dataclass(frozen=True)
class SourceCandidate:
    source_key: str       # 'own_site' | 'autocasion' | 'coches_net' | ...
    url: str
    tier: int = 0         # Tier-1 escalation per candidate when needed
    priority: int = 100   # lower = tried first


@dataclass
class ResolveResult:
    resolved_source: str | None
    url: str | None
    html: str | None
    attempts: list = field(default_factory=list)  # (source_key, ok|error)

    @property
    def ok(self) -> bool:
        return self.html is not None


def order_candidates(candidates: list[SourceCandidate]) -> list[SourceCandidate]:
    """Own site first, hard marketplaces last (stable by priority then order)."""
    return sorted(candidates, key=lambda c: c.priority)


def fetch_first_available(candidates: list[SourceCandidate], *,
                          fetch_text) -> ResolveResult:
    """Try each candidate in priority order; return the first that yields content.

    `fetch_text(url, *, tier=...)` is the tiered fetcher (a FetchEngine.fetch_text
    or the module-level fetch_text). A candidate that raises FetchError is recorded
    and skipped — we go around it to the next source, never stop.
    """
    result = ResolveResult(resolved_source=None, url=None, html=None)
    for cand in order_candidates(candidates):
        try:
            html = fetch_text(cand.url, tier=cand.tier)
        except FetchError as e:
            result.attempts.append((cand.source_key, f"error:{str(e)[:80]}"))
            continue
        result.attempts.append((cand.source_key, "ok"))
        result.resolved_source = cand.source_key
        result.url = cand.url
        result.html = html
        return result
    return result  # all sources failed (result.ok is False)


# Default per-entity priorities: own site is authoritative + WAF-free; the hard
# Tier-1 marketplace is the last resort (and only needs Tier-1 escalation there).
DEFAULT_PRIORITIES = {
    "own_site": 10,
    "autocasion": 20,
    "coches_com": 25,
    "motor_es": 30,
    "wallapop": 40,
    "coches_net": 90,    # hard (DataDome) — last, with tier=1
    "autoscout24": 90,   # hard (DataDome) — won live, but still last
    "milanuncios": 95,   # HARDEST (PerimeterX press-and-hold): free browser vías
                         # exhausted (nodriver+camoufox+CDP hold all blocked) — route
                         # AROUND it. Tried last; coverage closes via own_site/others.
}


def build_candidates(refs: dict[str, str]) -> list[SourceCandidate]:
    """Build prioritized candidates from a dealer's known source refs {source: url}."""
    out: list[SourceCandidate] = []
    for source_key, url in refs.items():
        prio = DEFAULT_PRIORITIES.get(source_key, 60)
        tier = 1 if prio >= 90 else 0  # hard marketplaces escalate to Tier-1
        out.append(SourceCandidate(source_key=source_key, url=url, tier=tier, priority=prio))
    return out
