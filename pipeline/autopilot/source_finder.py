"""AUTO-SOURCE-FINDER (auto-pack pieza 6) — country source auto-discovery.

The missing piece of the auto-pack: given a country, propose the ORTHOGONAL
sources its census should be built from. It fires per-bucket search queries
(through an INJECTED ``search_fn`` — never the network here), harvests the
candidate domains, classifies each into one of the 7 orthogonal capture buckets
of ``pipeline/exhaustiveness/lists.py`` (GEO/CENSUS/DGT/ASSOC/OEM/DORK/REG) and
emits a PROPOSED adapter config per candidate.

THE DOCTRINE THIS MODULE ENFORCES (the load-bearing CHECKPOINT)
---------------------------------------------------------------
"Is this source authoritative / orthogonal?" is a JUDGEMENT, not a mechanical
fact (a wrong authority silently biases the whole census; a falsely-independent
source inflates the MSE). So this finder NEVER auto-approves a source:

  * every :class:`SourceCandidate` carries a heuristic ``confidence`` AND
    ``needs_audit=True``. The confidence is capped strictly below 1.0
    (:data:`CONFIDENCE_CAP`) — the finder structurally cannot certify a source.
  * the finder PROPOSES; the auto-auditor (N1 orthogonality / N2 credibility,
    ``pipeline/autopilot/auditor.py``) GATES. N2 ALWAYS escalates authority +
    legality to the owner (``01-ARCHITECTURE.md`` §"frontera honesta").
  * orthogonality coverage (">= 3 orthogonal buckets", mirroring N1's
    ">= 3 listas denominador realmente independientes") is REPORTED by
    :func:`assess_orthogonality`; insufficiency is flagged, never assumed met.

The marketplace doctrine is preserved: many marketplaces collapse onto the SINGLE
orthogonal CENSUS spine (``lists.py``: digital marketplaces share a capture
mechanism). The finder proposes each marketplace as ``CENSUS`` with
``needs_audit``; picking THE census spine and collapsing the rest to the
non-orthogonal MKT signal is the auditor's call. Coverage counts DISTINCT buckets,
so N marketplaces still count as one orthogonal list — the dominant-list-bias
guard, by construction.

NETWORK ISOLATION
-----------------
``find_sources`` is pure given its ``search_fn``; the classification core is
deterministic and accent/locale tolerant. The live SearXNG/DDG search (mirroring
``pipeline/sources/dork_municipal.py``) is the separate :func:`web_search_fn`
seam below; it is never exercised by the tests and never wired live by the
finder — gating/wiring it belongs to the orchestrator phase.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Callable, Iterable, Mapping, Sequence

from pipeline.exhaustiveness.lists import ORTHOGONAL_LISTS, bucket_for

# ===========================================================================
# Tunables (declared, not magic)
# ===========================================================================
#: Minimum DISTINCT orthogonal buckets for an MSE-credible pack (mirrors N1).
MIN_ORTHOGONAL_BUCKETS: int = 3

#: Confidence is a heuristic, NOT an approval. Capped strictly below 1.0 so the
#: finder can never present a source as certified-authoritative: that is N2's
#: escalated judgement, never the finder's.
CONFIDENCE_CAP: float = 0.9
CONFIDENCE_FLOOR: float = 0.10

#: Each in-content keyword match for a bucket is worth this much, up to
#: ``MAX_COUNTED_HITS`` matches (so noise can't run confidence to certainty).
SIGNAL_WEIGHT: float = 0.22
MAX_COUNTED_HITS: int = 3

#: The query that surfaced a hit is a PRIOR (the search intent), not proof. It is
#: deliberately weaker than two independent content signals, so page CONTENT can
#: override the query origin (the judgement, not the echo).
ORIGIN_PRIOR: float = 0.34

#: Tie-break / output order: most authoritative & specific first, residual last.
_PRIORITY: tuple[str, ...] = ("DGT", "REG", "ASSOC", "OEM", "CENSUS", "GEO", "DORK")

#: The 6 buckets that name a SPECIFIC discoverable source. DORK (own-domain
#: dealer site) is the RESIDUAL: it wins only when no specific bucket fires,
#: exactly like ``lists.bucket_for`` defaulting unknown feeds to a catch bucket.
_SPECIFIC: tuple[str, ...] = ("DGT", "REG", "ASSOC", "OEM", "CENSUS", "GEO")


# ===========================================================================
# Search-intent query templates per orthogonal bucket ({country} interpolated).
# Mixed ES/EN terms keep the finder country-generic. The orchestrator may pass a
# localized country NAME as ``country_code`` to sharpen recall.
# ===========================================================================
BUCKET_QUERIES: dict[str, tuple[str, ...]] = {
    "DGT": (
        "official register authorised vehicle dealers {country}",
        "registro oficial concesionarios vehiculos {country}",
        "government list licensed car dealers {country}",
    ),
    "ASSOC": (
        "national association car dealers {country}",
        "asociacion concesionarios automocion {country}",
        "federation motor traders members {country}",
    ),
    "CENSUS": (
        "buy used cars {country} marketplace",
        "compraventa coches ocasion {country}",
        "used car classifieds {country}",
    ),
    "OEM": (
        "official dealer network locator {country}",
        "concesionarios oficiales red {country}",
        "manufacturer authorised dealers {country}",
    ),
    "REG": (
        "mercantile registry company automotive {country}",
        "registro mercantil empresas automocion {country}",
        "official company gazette motor trade {country}",
    ),
    "GEO": (
        "openstreetmap car dealership {country}",
        "directory car dealers map {country}",
    ),
    "DORK": (
        "concesionario coches {country}",
        "taller mecanico {country}",
    ),
}


# ===========================================================================
# Classification signals (accent/locale tolerant; matched against normalized text).
# Specific-bucket signals are intentionally precise so they do not cross-fire;
# DORK carries the generic dealer vocabulary because it is the residual.
# ===========================================================================
_SIGNALS: dict[str, tuple[str, ...]] = {
    "DGT": (
        "registro oficial", "official register", "ministerio", "ministry",
        "gobierno", "government", "autoriz", "homolog", "boletin oficial",
        "administracion", "gob.", "gov.",
    ),
    "REG": (
        "borme", "registro mercantil", "mercantile registry", "companies house",
        "company register", "company registry", "handelsregister",
        "business register", "cnae", "gazette",
    ),
    "ASSOC": (
        "asociaci", "association", "federaci", "federation", "gremio", "patronal",
        "verband", "federazione", "miembros", "asociados", "members", "guild",
    ),
    "OEM": (
        "concesionario oficial", "concesionarios oficiales", "official dealer",
        "authorised dealer", "authorized dealer", "dealer locator",
        "find a dealer", "red de concesionarios", "official network", "oem",
    ),
    "CENSUS": (
        "ocasion", "segunda mano", "used cars", "used car", "classified",
        "anuncios clasificados", "marketplace", "compraventa", "coches usados",
        "vehiculos de ocasion", "buy used",
    ),
    "GEO": (
        "openstreetmap", "overture", "map of", "directorio", "directory of",
        "points of interest", "poi", "yellow pages", "paginas amarillas",
        "places database",
    ),
    "DORK": (
        "concesionario", "compraventa", "taller", "garaje", "desguace",
        "automoviles", "automovil", "motor", "coches", "autos", "cars",
        "vehicles",
    ),
}

#: Pure noise: search engines, socials, app stores, encyclopaedias. NOT
#: marketplaces (those are CENSUS candidates) and NOT government domains.
_NOISE_SUBSTR: tuple[str, ...] = (
    "google.", "bing.", "duckduckgo.", "yahoo.", "baidu.", "yandex.", "ecosia.",
    "facebook.", "instagram.", "twitter.", "x.com", "youtube.", "linkedin.",
    "tiktok.", "pinterest.", "reddit.", "wikipedia.", "wikimedia.", "wikidata.",
    "play.google", "apps.apple", "t.me", "whatsapp.", "archive.org",
)

#: Per-bucket recipe-rung / adapter-strategy PROPOSAL. These map onto the engine's
#: ``css`` / ``llm_local`` recipe rungs (00-ARCHITECTURE Phase C); the auditor and
#: recipe-harness phase resolve the concrete rung. Descriptive, never wired here.
_ADAPTER_RUNG: dict[str, str] = {
    "DGT": "registry_list",
    "REG": "registry_api",
    "ASSOC": "css_roster",
    "OEM": "dealer_locator",
    "CENSUS": "census_facet",
    "GEO": "geo_overlay",
    "DORK": "dork_municipal",
}

#: ``DiscoveredEntity.kind`` prior implied by a bucket. BLANK where the bucket is
#: genuinely mixed-segment (registry / association / geo): the split is never
#: fabricated — it is the same honest degradation as the denominator extractor.
_KIND_PRIOR: dict[str, str] = {
    "DGT": "",
    "REG": "",
    "ASSOC": "",
    "OEM": "concesionario_oficial",
    "CENSUS": "compraventa",
    "GEO": "",
    "DORK": "compraventa",
}


# ===========================================================================
# Immutable value objects
# ===========================================================================
@dataclass(frozen=True)
class SearchHit:
    """One normalized search result from the injected ``search_fn``."""

    url: str
    title: str = ""
    snippet: str = ""


@dataclass(frozen=True)
class AdapterConfig:
    """A PROPOSED source-adapter config for a discovered candidate.

    A proposal the auto-auditor must gate; never wired live by the finder.
    ``adapter`` names the recipe rung the engine would attempt (defaults onto the
    ``css`` -> ``llm_local`` rungs)."""

    source_key: str
    bucket: str
    kind: str            # DiscoveredEntity kind prior ("" when mixed-segment)
    adapter: str         # recipe rung / adapter strategy proposal
    base_url: str
    notes: str = ""


@dataclass(frozen=True)
class SourceCandidate:
    """A PROPOSED, un-audited source. ``needs_audit`` is always True."""

    domain: str
    bucket: str               # assigned orthogonal bucket (one of ORTHOGONAL_LISTS)
    confidence: float         # heuristic in [FLOOR, CAP] — NOT an approval
    needs_audit: bool         # ALWAYS True: finder proposes, auditor gates
    origin_bucket: str        # which bucket-query surfaced it (the search intent)
    query: str                # the exact query that surfaced it
    evidence: str             # the title/snippet that justified the classification
    proposed_config: AdapterConfig


@dataclass(frozen=True)
class OrthogonalityReport:
    """Coverage verdict over a candidate set (the >=3-orthogonal CHECKPOINT)."""

    buckets_covered: tuple[str, ...]
    n_orthogonal: int
    meets_threshold: bool
    insufficient: bool
    missing: tuple[str, ...]
    reason: str


#: The contract of the injected search seam: query -> iterable of results, each a
#: SearchHit, a mapping with url/title/snippet, or a bare url string.
SearchFn = Callable[[str], Iterable["SearchHit | Mapping[str, str] | str"]]


# ===========================================================================
# Text + domain helpers (pure)
# ===========================================================================
def _norm(text: str) -> str:
    """Lowercase + strip diacritics so accent-free signals match accented text
    (``ocasion`` matches ``ocasión``, ``asociaci`` matches ``asociación``)."""
    decomposed = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def registrable_domain(url: str) -> str | None:
    """Best-effort registrable domain (host minus scheme/userinfo/port/``www.``).
    Mirrors ``dork_municipal._registrable_domain`` so the substrate is identical."""
    try:
        import urllib.parse

        netloc = urllib.parse.urlsplit(
            url if "://" in url else "http://" + url
        ).netloc.lower()
    except Exception:  # noqa: BLE001 — a malformed URL is simply not a domain
        return None
    netloc = netloc.split("@")[-1].split(":")[0]
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc or None


def _is_noise(domain: str) -> bool:
    return any(sub in domain for sub in _NOISE_SUBSTR)


def _domain_slug(domain: str) -> str:
    """Domain -> a source_key-shaped slug (``mercedes.xx`` -> ``mercedes_xx``)."""
    return re.sub(r"[^a-z0-9]+", "_", _norm(domain)).strip("_")


def _normalize_hits(
    raw: Iterable["SearchHit | Mapping[str, str] | str"],
) -> list[SearchHit]:
    """Coerce whatever the injected ``search_fn`` returns into ``SearchHit``s."""
    out: list[SearchHit] = []
    for item in raw or []:
        if isinstance(item, SearchHit):
            out.append(item)
        elif isinstance(item, Mapping):
            url = str(item.get("url") or item.get("link") or "").strip()
            if not url:
                continue
            out.append(
                SearchHit(
                    url=url,
                    title=str(item.get("title") or "").strip(),
                    snippet=str(item.get("snippet") or item.get("content") or "").strip(),
                )
            )
        elif isinstance(item, str) and item.strip():
            out.append(SearchHit(url=item.strip()))
    return out


# ===========================================================================
# Classification (pure heuristic — the JUDGEMENT, declared as needs_audit)
# ===========================================================================
def _signal_hits(text: str, domain_slug: str) -> dict[str, int]:
    """Count per-bucket keyword evidence in ``text``, plus one extra signal when
    the project's own taxonomy (``lists.bucket_for``) recognizes the domain slug
    as an orthogonal bucket (e.g. an ``oem_*``/``mercedes*`` OEM domain)."""
    hits = {b: 0 for b in _PRIORITY}
    for bucket, signals in _SIGNALS.items():
        for sig in signals:
            if sig in text:
                hits[bucket] += 1
    taxon = bucket_for(domain_slug)
    if taxon in hits:
        hits[taxon] += 1
    return hits


def _argmax(scores: Mapping[str, float], origin_bucket: str) -> str:
    """Highest score wins; ties prefer the query origin, else _PRIORITY order."""
    best = max(scores.values())
    tied = [b for b, s in scores.items() if s == best]
    if origin_bucket in tied:
        return origin_bucket
    return min(tied, key=_PRIORITY.index)


def classify_candidate(
    origin_bucket: str, domain: str, title: str = "", snippet: str = ""
) -> tuple[str, float] | None:
    """Classify one candidate into an orthogonal bucket with a heuristic
    confidence, or ``None`` when it shows no dealer/automotive relevance at all.

    A SPECIFIC bucket (DGT/REG/ASSOC/OEM/CENSUS/GEO) always wins over the residual
    DORK; CONTENT can override the query ORIGIN prior. The returned confidence is
    bounded to ``[CONFIDENCE_FLOOR, CONFIDENCE_CAP]`` — it is a proposal strength,
    never a certification. Pure / deterministic.
    """
    text = _norm(f"{domain} {title} {snippet}")
    hits = _signal_hits(text, _domain_slug(domain))

    score = {b: SIGNAL_WEIGHT * min(hits[b], MAX_COUNTED_HITS) for b in _PRIORITY}
    if origin_bucket in score:
        score[origin_bucket] += ORIGIN_PRIOR

    specific = {b: score[b] for b in _SPECIFIC if score[b] > 0.0}
    if specific:
        winner = _argmax(specific, origin_bucket)
    elif score["DORK"] > 0.0:
        winner = "DORK"
    else:
        return None  # no automotive relevance -> not a candidate (drop, not guess)

    confidence = min(CONFIDENCE_CAP, max(CONFIDENCE_FLOOR, round(score[winner], 4)))
    return winner, confidence


# ===========================================================================
# Proposed adapter config (the per-candidate output)
# ===========================================================================
def propose_source_key(bucket: str, domain: str) -> str:
    """A deterministic, bucket-tagged ``source_key`` proposal. OEM keys are built
    to ROUND-TRIP through ``lists.bucket_for`` (-> OEM); the other buckets carry an
    explicit ``<bucket>_`` prefix (``bucket_for`` only knows live keys, so a novel
    discovered key is for the auditor to bless, not for ``bucket_for`` to ratify)."""
    slug = _domain_slug(domain)
    if bucket == "OEM":
        return slug if bucket_for(slug) == "OEM" else f"oem_{slug}"
    prefix = f"{bucket.lower()}_"
    return slug if slug.startswith(prefix) else f"{prefix}{slug}"


def propose_adapter(bucket: str, domain: str) -> AdapterConfig:
    """Emit the PROPOSED adapter config for a classified candidate."""
    return AdapterConfig(
        source_key=propose_source_key(bucket, domain),
        bucket=bucket,
        kind=_KIND_PRIOR.get(bucket, ""),
        adapter=_ADAPTER_RUNG.get(bucket, "llm_local"),
        base_url=f"https://{domain}",
        notes=(
            f"PROPOSAL ({bucket}/{_ADAPTER_RUNG.get(bucket, 'llm_local')}); recipe "
            "rung defaults css->llm_local; authority+orthogonality gated by "
            "auditor N1/N2 (needs_audit)."
        ),
    )


def _evidence(hit: SearchHit) -> str:
    return " - ".join(p for p in (hit.title.strip(), hit.snippet.strip()) if p)


# ===========================================================================
# The finder (pure given search_fn)
# ===========================================================================
def find_sources(
    country_code: str,
    *,
    search_fn: SearchFn,
    queries: Mapping[str, Sequence[str]] = BUCKET_QUERIES,
    max_hits_per_query: int = 10,
) -> list[SourceCandidate]:
    """Discover + classify candidate sources for ``country_code``.

    For each orthogonal bucket's query templates: interpolate ``{country}``, call
    the INJECTED ``search_fn``, harvest non-noise candidate domains, and classify
    each (CONTENT may override the query ORIGIN). Candidates are de-duplicated by
    domain keeping the highest confidence, then returned in a deterministic order
    (bucket authority, then confidence desc, then domain). NO network here.

    Every candidate is ``needs_audit=True``: the finder PROPOSES, the auditor
    gates. Coverage of the >=3-orthogonal floor is reported by
    :func:`assess_orthogonality`.
    """
    cc = (country_code or "").strip()
    by_domain: dict[str, SourceCandidate] = {}

    for origin_bucket, templates in queries.items():
        for template in templates:
            query = template.format(country=cc)
            for hit in _normalize_hits(search_fn(query))[:max_hits_per_query]:
                domain = registrable_domain(hit.url)
                if not domain or _is_noise(domain):
                    continue
                verdict = classify_candidate(
                    origin_bucket, domain, hit.title, hit.snippet
                )
                if verdict is None:
                    continue
                bucket, confidence = verdict
                candidate = SourceCandidate(
                    domain=domain,
                    bucket=bucket,
                    confidence=confidence,
                    needs_audit=True,
                    origin_bucket=origin_bucket,
                    query=query,
                    evidence=_evidence(hit),
                    proposed_config=propose_adapter(bucket, domain),
                )
                prev = by_domain.get(domain)
                if prev is None or confidence > prev.confidence:
                    by_domain[domain] = candidate

    candidates = list(by_domain.values())
    candidates.sort(key=lambda c: (_PRIORITY.index(c.bucket), -c.confidence, c.domain))
    return candidates


def assess_orthogonality(candidates: Iterable[SourceCandidate]) -> OrthogonalityReport:
    """Report DISTINCT orthogonal-bucket coverage vs the >=3 floor (mirrors N1).

    Many marketplaces still count as ONE bucket (CENSUS) — the dominant-list-bias
    guard. Insufficiency is flagged and the missing buckets named; it is never
    silently assumed met. This is a REPORT for the auditor, not an approval.
    """
    covered = sorted(
        {c.bucket for c in candidates if c.bucket in ORTHOGONAL_LISTS},
        key=_PRIORITY.index,
    )
    n_orthogonal = len(covered)
    meets = n_orthogonal >= MIN_ORTHOGONAL_BUCKETS
    missing = tuple(b for b in ORTHOGONAL_LISTS if b not in covered)
    covered_str = ", ".join(covered) or "none"
    if meets:
        reason = (
            f"{n_orthogonal} orthogonal capture bucket(s) covered ({covered_str}); "
            f">= {MIN_ORTHOGONAL_BUCKETS} required for MSE independence: threshold "
            "met (each source still gated by auditor N1/N2)."
        )
    else:
        reason = (
            f"{n_orthogonal} orthogonal capture bucket(s) covered ({covered_str}); "
            f">= {MIN_ORTHOGONAL_BUCKETS} required: INSUFFICIENT — missing "
            f"{', '.join(missing)}."
        )
    return OrthogonalityReport(
        buckets_covered=tuple(covered),
        n_orthogonal=n_orthogonal,
        meets_threshold=meets,
        insufficient=not meets,
        missing=missing,
        reason=reason,
    )


# ===========================================================================
# LIVE search seam — SearXNG -> DDG, mirroring dork_municipal. NEVER touched by
# tests; the orchestrator wires/gates it. Isolated so the finder stays pure.
# ===========================================================================
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "Chrome/146.0 Safari/537.36"
)


def web_search_fn(query: str, *, searxng_url: str | None = None, timeout: int = 25):  # pragma: no cover - live network path
    """Build a default ``search_fn`` result list from a self-hosted/public SearXNG
    JSON endpoint, falling back to DuckDuckGo HTML — the same €0, account-less
    substrate as ``pipeline/sources/dork_municipal.py``. Returns ``SearchHit``s.

    LIVE network. Never exercised by the unit tests; the orchestrator owns wiring,
    rate-limiting and the PROD/LEGAL gates around it.
    """
    import os

    import requests

    base = searxng_url or os.environ.get("CARDEEP_SEARXNG_URL")
    if base:
        try:
            r = requests.get(
                base.rstrip("/") + "/search",
                params={"q": query, "format": "json", "safesearch": "0"},
                headers={"User-Agent": _UA},
                timeout=timeout,
            )
            r.raise_for_status()
            return [
                SearchHit(
                    url=it.get("url", ""),
                    title=it.get("title", ""),
                    snippet=it.get("content", ""),
                )
                for it in r.json().get("results", [])
                if it.get("url")
            ]
        except Exception:  # noqa: BLE001 — instance down: fall back to DDG
            pass

    import urllib.parse

    r = requests.post(
        "https://html.duckduckgo.com/html/",
        data={"q": query},
        headers={"User-Agent": _UA},
        timeout=timeout,
    )
    r.raise_for_status()
    hits: list[SearchHit] = []
    for href in re.findall(r'href="(/l/\?[^"]+)"', r.text):
        m = re.search(r"[?&]uddg=([^&]+)", href)
        if m:
            hits.append(SearchHit(url=urllib.parse.unquote(m.group(1))))
    hits += [SearchHit(url=u) for u in re.findall(r'href="(https?://[^"]+)"', r.text)]
    return hits


__all__ = [
    "MIN_ORTHOGONAL_BUCKETS",
    "CONFIDENCE_CAP",
    "CONFIDENCE_FLOOR",
    "BUCKET_QUERIES",
    "SearchHit",
    "AdapterConfig",
    "SourceCandidate",
    "OrthogonalityReport",
    "SearchFn",
    "registrable_domain",
    "classify_candidate",
    "propose_source_key",
    "propose_adapter",
    "find_sources",
    "assess_orthogonality",
    "web_search_fn",
]
