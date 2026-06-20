"""Lens C — live re-fetch from the source portal (§3.3), now ACTIVE.

This is the MOST independent lens (StateTuple distance 4 vs any ingest producer:
source=live_portal, tool=browser, cache=live_T1, path=lens_c_live_refetch). It was
a hard stub because it needed a live fetch path with a SEPARATE egress identity —
which now exists: pipeline.engine (Tier-0 rotating fingerprints + Tier-1 headful
browser with cookie-reuse). Lens C re-fetches the claimed resource LIVE, through a
fingerprint independent of the ingest fleet, and recounts.

Honesty gate (no maquillaje): Lens C ASSERTs/REFUTEs ONLY when it can obtain a
reliable live count. It activates when the claim carries a fetchable evidence_uri
(an http(s) URL, optionally prefixed `count:` or `sitemap:`). When there is no
fetchable URL, or the live count cannot be extracted, it ABSTAINs with a precise
reason — absence of a live count is NOT a refutation (Law I). It will therefore
ABSTAIN on claims that don't yet carry a re-fetchable URL, and become a real second
(D=4) skeptic for those that do, without ever fabricating a TRUSTWORTHY.

The live fetcher is injected via `set_fetcher()` (tests) and defaults to the
engine's Tier-1-capable fetch, lazily, so importing this module pulls no browser.
"""
from __future__ import annotations

import re

import asyncpg

from pipeline.inquisition.models import Skeptic, StateTuple, regime_for
from pipeline.inquisition.quorum import within_tolerance

# Injectable live fetcher: url -> html. None => lazy engine default.
_FETCHER = None


def set_fetcher(fn) -> None:
    """Override the live fetcher (tests). Pass None to restore the engine default."""
    global _FETCHER
    _FETCHER = fn


def _default_fetcher(url: str, *, tier1: bool) -> str:
    from pipeline.engine.api import fetch
    return fetch(url, tier1=tier1)


def _fetch(url: str, *, tier1: bool) -> str:
    if _FETCHER is not None:
        return _FETCHER(url)
    return _default_fetcher(url, tier1=tier1)


_LIVE_STATE = StateTuple(source="live_portal", tool="browser",
                         cache="live_T1", path="lens_c_live_refetch")

# Generic stable-id / listing extractors. Counting DISTINCT ids avoids inflation.
_JSONLD_VEHICLE = re.compile(r'"@type"\s*:\s*"(?:Car|Vehicle|MotorizedVehicle|Product|Offer)"',
                             re.IGNORECASE)
_SITEMAP_LOC = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>", re.IGNORECASE)


def _parse_fetchable(evidence_uri: str | None) -> tuple[str, str] | None:
    """Return (mode, url) for a fetchable evidence_uri, else None.

    Forms: 'count:<url>' (count vehicle items), 'sitemap:<url>' (count <loc>),
    or a bare http(s) url (default: count vehicle items).
    """
    if not evidence_uri:
        return None
    if evidence_uri.startswith("count:") and "http" in evidence_uri:
        return ("count", evidence_uri.split("count:", 1)[1])
    if evidence_uri.startswith("sitemap:") and "http" in evidence_uri:
        return ("sitemap", evidence_uri.split("sitemap:", 1)[1])
    if evidence_uri.startswith(("http://", "https://")):
        return ("count", evidence_uri)
    return None


def _count_live(mode: str, html: str) -> int | None:
    if mode == "sitemap":
        ids = set(_SITEMAP_LOC.findall(html))
        return len(ids) if ids else None
    matches = _JSONLD_VEHICLE.findall(html)
    return len(matches) if matches else None


async def lens_c_live_refetch(conn: asyncpg.Connection, claim) -> Skeptic:
    subject_type = claim.subject_type
    if subject_type not in ("count", "inventory", "coverage", "kind", "delta"):
        return _abstain(f"lens_c_unsupported_subject_type:{subject_type}")

    target = _parse_fetchable(getattr(claim, "evidence_uri", None))
    if target is None:
        return _abstain("live_refetch_no_fetchable_uri")

    mode, url = target
    try:
        html = _fetch(url, tier1=True)
    except Exception as e:  # noqa: BLE001 - a live fetch failure is not a refutation
        return _abstain(f"live_fetch_failed:{type(e).__name__}")

    measured = _count_live(mode, html)
    if measured is None or measured == 0:
        return _abstain("live_count_unextractable")

    asserted = float(claim.asserted_value)
    regime = regime_for(subject_type)
    in_tol = within_tolerance(float(measured), asserted, regime)
    return Skeptic(
        lens="C_live_refetch",
        state=_LIVE_STATE,
        verdict="ASSERT" if in_tol else "REFUTE_SOFT",
        measured_value=str(int(measured)),
        confidence=0.92 if in_tol else None,
        reason=None if in_tol else "live_refetch_mismatch",
    )


def _abstain(reason: str) -> Skeptic:
    return Skeptic(
        lens="C_live_refetch",
        state=_LIVE_STATE,
        verdict="ABSTAIN",
        measured_value=None,
        confidence=None,
        reason=reason,
    )
