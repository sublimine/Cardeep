"""Semantic block detection for the tiered fetch engine.

A 403 is not the only failure shape, and a 200 is not proof of success: WAFs
serve interstitial challenge pages with HTTP 200. The old engine treated 403 as
a hard non-retryable error and 200 as success — so a Cloudflare "Just a moment"
page (200) would be returned to the connector as if it were the inventory, and a
DataDome 403-challenge was indistinguishable from a real 404.

`classify()` looks at status + body + headers and returns one of:
  OK         — genuine content, serve it.
  CHALLENGE  — a JS/interstitial challenge (CF managed, DataDome, Akamai sensor,
               Turnstile). Escalating to a real browser CAN solve it.
  BANNED     — hard block / rate ban (IP or fingerprint burned). A browser on the
               SAME identity will likely also fail; rotate identity/proxy.
  NOT_FOUND  — genuine 404/410, the URL is simply gone. Do not escalate.

Markers are drawn from the public signatures of each WAF (cookie/header names and
the human-visible interstitial strings). Kept conservative: when unsure we return
CHALLENGE rather than OK, so a challenge page is never mistaken for content.
"""
from __future__ import annotations

import enum


class Verdict(enum.Enum):
    OK = "ok"
    CHALLENGE = "challenge"
    BANNED = "banned"
    NOT_FOUND = "not_found"


# Human-visible / structural markers of an active challenge interstitial. Lowercased.
_CHALLENGE_MARKERS = (
    # Cloudflare managed challenge / Turnstile / "Just a moment"
    "just a moment", "cf-chl-", "challenge-platform", "__cf_chl", "cf_chl_opt",
    "turnstile", "checking your browser", "ray id", "cf-mitigated",
    "enable javascript and cookies to continue",
    # DataDome
    "datadome", "geo.captcha-delivery.com", "captcha-delivery", "dd_cookie",
    "interstitial", "blocked by datadome",
    # Akamai bot manager (sensor / _abck)
    "_abck", "ak_bmsc", "bm-verify", "akamai", "reference&#32;#", "reference #",
    # PerimeterX / HUMAN
    "px-captcha", "_px", "perimeterx", "human challenge",
    # Generic
    "are you a robot", "verify you are human", "unusual traffic",
)

# Header names that signal a WAF is mediating the response (any value).
_CHALLENGE_HEADERS = (
    "cf-mitigated", "cf-chl-bypass", "x-datadome", "server-timing",
)

# Strings that mean a HARD ban rather than a solvable challenge.
_BAN_MARKERS = (
    "access denied", "you have been blocked", "rate limited",
    "too many requests", "your ip has been", "permanently banned",
)

# STRONG block phrases that identify an interstitial UNAMBIGUOUSLY, regardless of
# page size (some block pages ship 100KB+ of inert markup). A real inventory page
# never contains these, so there is no size gate on them.
_STRONG_BLOCK_MARKERS = (
    "pardon our interruption",            # PerimeterX / HUMAN
    "geo.captcha-delivery.com",           # DataDome captcha
    "blocked by datadome",
    "/_incapsula_resource",               # Imperva Incapsula
    "请开启javascript",                    # generic JS-wall
    "attention required! | cloudflare",
)


def _has(haystack: str, needles) -> bool:
    return any(n in haystack for n in needles)


def classify(status: int, body: str | None, headers: dict | None = None) -> Verdict:
    """Classify a fetched response. `headers` keys are matched case-insensitively."""
    body_l = (body or "").lower()
    hdrs = {k.lower(): str(v).lower() for k, v in (headers or {}).items()}

    if status in (404, 410):
        return Verdict.NOT_FOUND

    # Strong, size-independent block signatures take precedence over everything:
    # a "Pardon Our Interruption" (PerimeterX) page is a block even at 100KB / 200.
    if _has(body_l, _STRONG_BLOCK_MARKERS):
        return Verdict.CHALLENGE

    # Cloudflare explicitly tags mitigated responses in a header regardless of code.
    if hdrs.get("cf-mitigated") == "challenge":
        return Verdict.CHALLENGE

    # 403 / 429 / 503 are the classic WAF block codes — disambiguate by body.
    if status in (401, 403, 429, 503):
        if _has(body_l, _BAN_MARKERS) and not _has(body_l, _CHALLENGE_MARKERS):
            return Verdict.BANNED
        # A 403/503 with challenge furniture (or empty) is a solvable challenge.
        if _has(body_l, _CHALLENGE_MARKERS) or len(body_l) < 1500:
            return Verdict.CHALLENGE
        return Verdict.BANNED

    if status == 200:
        # A 200 can still be an interstitial OR a soft block page served with 200.
        # Flag only when markers are present AND the page is too small to be real
        # inventory, to avoid false positives on legit pages that merely mention
        # "ray id" etc. (a real listing page is hundreds of KB).
        small = len(body_l) < 30000
        if small and _has(body_l, _BAN_MARKERS) and not _has(body_l, _CHALLENGE_MARKERS):
            return Verdict.BANNED       # 200 "Access Denied / you have been blocked"
        if small and _has(body_l, _CHALLENGE_MARKERS):
            return Verdict.CHALLENGE
        if any(h in hdrs for h in _CHALLENGE_HEADERS) and "datadome" in body_l:
            return Verdict.CHALLENGE
        return Verdict.OK

    # Other 2xx/3xx — treat as OK (the fetch layer follows redirects already).
    if 200 <= status < 400:
        return Verdict.OK
    # Unknown 4xx/5xx not in retryable set — conservative: not a solvable challenge.
    return Verdict.BANNED


def is_blocked(status: int, body: str | None, headers: dict | None = None) -> bool:
    """True when the response is a challenge or a ban (i.e. not usable content)."""
    return classify(status, body, headers) in (Verdict.CHALLENGE, Verdict.BANNED)
