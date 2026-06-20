"""Fingerprint pool + rotation (Tier-0 anti-detection).

A WAF allow-LISTS known-good client fingerprints; it does NOT block-list them.
So the rule is hard: every fingerprint we present must be a REAL, coherent
browser profile (TLS/JA3 + HTTP2 settings + User-Agent + client hints all from
the SAME shipped browser build). We NEVER hand-randomize JA3 — a random TLS
ClientHello that no real browser emits falls outside the allow-list and is the
fastest way to get burned.

What this module adds over the old single hardcoded `chrome131`:
  * a POOL of recent, real impersonation profiles curl_cffi actually ships,
  * per-profile COHERENT headers (Chrome client-hints only on Chrome, never on
    Firefox/Safari — a mismatch is itself a detection signal),
  * a rotation policy: one profile per session by default, with the ability to
    rotate to a *different* profile when a host burns the current one.

Coherence invariant (enforced by `_PROFILES` construction + tests): the UA
version string matches the impersonate target, and Chrome-only `Sec-Ch-Ua*`
headers appear only on Chrome-family profiles.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass(frozen=True)
class FingerprintProfile:
    """One coherent, real browser fingerprint.

    `impersonate` is the curl_cffi target (drives TLS/JA3 + HTTP2 settings).
    `headers` are the family-coherent default headers merged on every request.
    """
    key: str
    impersonate: str          # curl_cffi impersonate target (must be a shipped one)
    family: str               # "chrome" | "firefox" | "safari"
    user_agent: str
    headers: dict = field(default_factory=dict)


def _chrome_headers(ua: str, version: str) -> dict:
    return {
        "User-Agent": ua,
        "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
                   "image/avif,image/webp,image/apng,*/*;q=0.8"),
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Ch-Ua": f'"Chromium";v="{version}", "Google Chrome";v="{version}", "Not?A_Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }


def _firefox_headers(ua: str) -> dict:
    # Firefox does NOT send Sec-Ch-Ua client hints — including them would be an
    # immediate UA/fingerprint mismatch. It does send a distinct Accept.
    return {
        "User-Agent": ua,
        "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
                   "image/avif,image/webp,*/*;q=0.8"),
        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }


def _safari_headers(ua: str) -> dict:
    # Safari sends neither Sec-Ch-Ua nor the Sec-Fetch-User header the same way;
    # keep it minimal and coherent with WebKit.
    return {
        "User-Agent": ua,
        "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
        "Accept-Language": "es-ES,es;q=0.9",
    }


_CHROME = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36"
_FIREFOX = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{v}.0) Gecko/20100101 Firefox/{v}.0"
_SAFARI = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"


def _chrome_profile(impersonate: str, version: str) -> FingerprintProfile:
    ua = _CHROME.format(v=version)
    return FingerprintProfile(key=impersonate, impersonate=impersonate,
                              family="chrome", user_agent=ua,
                              headers=_chrome_headers(ua, version))


def _firefox_profile(impersonate: str, version: str) -> FingerprintProfile:
    ua = _FIREFOX.format(v=version)
    return FingerprintProfile(key=impersonate, impersonate=impersonate,
                              family="firefox", user_agent=ua,
                              headers=_firefox_headers(ua))


def _safari_profile(impersonate: str) -> FingerprintProfile:
    ua = _SAFARI
    return FingerprintProfile(key=impersonate, impersonate=impersonate,
                              family="safari", user_agent=ua,
                              headers=_safari_headers(ua))


# Ordered by preference (newest Chrome first). Every target below is verified to
# be shipped by curl_cffi 0.15.x (see tests/test_fingerprints.py which asserts
# each impersonate is in curl_cffi's known set — so a curl_cffi upgrade that
# drops a target fails loudly instead of banning us silently).
_CHROME_POOL: tuple[FingerprintProfile, ...] = (
    _chrome_profile("chrome146", "146"),
    _chrome_profile("chrome142", "142"),
    _chrome_profile("chrome136", "136"),
    _chrome_profile("chrome131", "131"),
)
# Cross-family diversity, reserved for escalation-on-ban (a host that burns every
# Chrome profile may still accept a Firefox/Safari shape). Kept out of the default
# rotation so the homogeneous Chrome header model stays trivially coherent.
_DIVERSITY_POOL: tuple[FingerprintProfile, ...] = (
    _firefox_profile("firefox147", "147"),
    _safari_profile("safari260"),
)

_ALL: tuple[FingerprintProfile, ...] = _CHROME_POOL + _DIVERSITY_POOL
_BY_KEY = {p.key: p for p in _ALL}

# The profile the legacy single-fingerprint path used; kept as a stable default
# so the AS24-verified behavior is reproducible when rotation is disabled.
DEFAULT_PROFILE_KEY = "chrome131"


def get_profile(key: str) -> FingerprintProfile:
    """Return the profile for an impersonate key, or raise if unknown."""
    try:
        return _BY_KEY[key]
    except KeyError as e:
        raise KeyError(f"unknown fingerprint profile {key!r}; "
                       f"known: {sorted(_BY_KEY)}") from e


def all_profiles() -> tuple[FingerprintProfile, ...]:
    return _ALL


class FingerprintPool:
    """Hands out coherent fingerprints with a no-immediate-repeat rotation.

    `pick()` returns a profile; `rotate(burned)` returns a DIFFERENT profile than
    the burned one (escalating into the diversity pool once the Chrome pool is
    exhausted), so a host that bans Chrome146 gets Chrome142, then a Firefox shape,
    never the same burned fingerprint twice in a row.
    """

    def __init__(self, *, rng: random.Random | None = None,
                 chrome_only: bool = True) -> None:
        self._rng = rng or random.Random()
        self._base = list(_CHROME_POOL if chrome_only else _ALL)
        self._escalation = list(_DIVERSITY_POOL)

    def pick(self) -> FingerprintProfile:
        return self._rng.choice(self._base)

    def rotate(self, burned: FingerprintProfile,
               already_tried: set[str] | None = None) -> FingerprintProfile | None:
        """Return a fresh profile != burned and not in already_tried.

        Tries the base (Chrome) pool first, then the diversity pool. Returns None
        when every known profile has been tried (the host is unreachable at Tier-0
        and the caller must escalate to a real browser).
        """
        tried = set(already_tried or set())
        tried.add(burned.key)
        for profile in self._base + self._escalation:
            if profile.key not in tried:
                return profile
        return None
