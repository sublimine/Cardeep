"""FASE 2 (engine) — the tiered fetch ENGINE. Replaces the urllib pattern.

Tier-0: curl_cffi with full browser impersonation — a real Chrome TLS/JA3 + HTTP2
fingerprint, kept COHERENT at the session level (one Session -> one fingerprint ->
one cookie jar) so a paginated drain looks like one browser, not N disconnected
stdlib requests. This is the curl_cffi-class engine for OPEN platforms (AS24,
autocasion, coches.com...).

What P2 added on top of the original single-fingerprint Tier-0:
  * REAL fingerprint rotation over a floor of recent, coherent profiles
    (pipeline/engine/fingerprints.py) — never a hand-randomized JA3, always a
    real shipped browser shape. One profile per session; rotate on ban.
  * SEMANTIC block detection (pipeline/engine/ban_detector.py) — a 403 is not the
    only failure and a 200 is not proof of success (WAFs serve 200 interstitials).
  * A real Tier-1 browser layer (pipeline/engine/tier1/) that solves an active
    challenge ONCE (nodriver primary [AGPL-3.0!], Camoufox secondary) and mints a
    clearance cookie, which Tier-0 then REUSES with the same UA+fingerprint+IP —
    the cheap engine serves thousands of requests behind one browser solve.

Backward compatibility (the 37 connectors depend on this seam): the public
signatures are unchanged — `FetchEngine()`, `engine.fetch_text(url, *, tier=0,
headers=None) -> str`, the module-level `fetch_text(...)`, and `FetchError`.
Tier-1 escalation is OPT-IN per engine (`allow_tier1_escalation`, default False)
or via explicit `tier>=1`, so a connector that does not ask for it gets the exact
Tier-0 fail-loud semantics it always had — only now a detected challenge/ban
raises instead of silently returning the interstitial body.
"""
from __future__ import annotations

import random
import time

from curl_cffi import requests as cffi_requests

from pipeline.engine import ban_detector
from pipeline.engine.ban_detector import Verdict
from pipeline.engine.fingerprints import (
    DEFAULT_PROFILE_KEY,
    FingerprintPool,
    FingerprintProfile,
    get_profile,
)

_RETRYABLE = {429, 500, 502, 503, 504}
_TIMEOUT = 40
_MAX_RETRIES = 4
_BACKOFF_BASE = 2.0          # seconds; grows 2,4,8,16 with full jitter
_POLITE_MIN = 0.7            # min delay between successful fetches on a session
_POLITE_MAX = 1.4

# Default Tier-1 engine. nodriver is AGPL-3.0 (see tier1/browser.py LICENSE
# WARNING). Switch to "camoufox" to avoid AGPL network-copyleft.
_TIER1_ENGINE = "nodriver"


class FetchError(RuntimeError):
    """Raised when a URL cannot be retrieved after the retry budget."""


class FetchEngine:
    """A fingerprint-coherent fetch session with optional Tier-1 escalation.

    One engine == one Chrome fingerprint == one cookie jar. Reuse the SAME engine
    for every page of a single drain so the platform sees one continuous browser.

    Rotation: by default the engine PICKS a recent coherent profile from the pool
    at construction (so different drains look like different real browsers); pass
    `impersonate=` to pin a specific one (e.g. to reproduce a recipe). On a ban it
    rotates to a DIFFERENT coherent profile, never the burned one.

    Tier-1: when `allow_tier1_escalation=True` (or `fetch_text(tier=1)`), a
    detected challenge that survives fingerprint rotation is handed to a real
    browser, whose minted cookies are injected back into THIS session and reused.
    """

    def __init__(self, *, impersonate: str | None = None,
                 polite_min: float = _POLITE_MIN, polite_max: float = _POLITE_MAX,
                 allow_tier1_escalation: bool = False,
                 tier1_engine: str = _TIER1_ENGINE,
                 proxy: str | None = None,
                 rng: random.Random | None = None) -> None:
        self._pool = FingerprintPool(rng=rng)
        if impersonate is None:
            self._profile: FingerprintProfile = self._pool.pick()
        else:
            self._profile = get_profile(impersonate)
        self._tried_profiles: set[str] = {self._profile.key}
        self._proxy = proxy            # PENDING-CREDENTIAL when None (host IP)
        self._session = self._new_session(self._profile)
        self._polite_min = polite_min
        self._polite_max = polite_max
        self._last_fetch_at: float | None = None
        self._allow_tier1 = allow_tier1_escalation
        self._tier1_engine = tier1_engine
        self._tier1_cookies: dict = {}
        # Public attributes preserved for callers (governor, connectors, tests).
        self.impersonate = self._profile.impersonate
        self.last_status: int | None = None
        self.last_tier: int = 0
        self.last_verdict: Verdict | None = None
        self.fetch_count = 0

    # ---- session construction / fingerprint coherence ---------------------

    def _new_session(self, profile: FingerprintProfile):
        kwargs = {"impersonate": profile.impersonate}
        if self._proxy:
            kwargs["proxies"] = {"http": self._proxy, "https": self._proxy}
        return cffi_requests.Session(**kwargs)

    def _swap_profile(self, profile: FingerprintProfile) -> None:
        """Rebind the session to a different coherent fingerprint (on ban)."""
        self._profile = profile
        self._tried_profiles.add(profile.key)
        self._session = self._new_session(profile)
        self.impersonate = profile.impersonate
        # Re-apply any minted Tier-1 cookies to the fresh session.
        self._apply_cookies(self._tier1_cookies)

    def _apply_cookies(self, cookies: dict) -> None:
        for name, value in (cookies or {}).items():
            try:
                self._session.cookies.set(name, value)
            except Exception:  # noqa: BLE001 - cookie jar set is best-effort
                pass

    def _polite_wait(self) -> None:
        if self._last_fetch_at is None:
            return
        elapsed = time.monotonic() - self._last_fetch_at
        gap = random.uniform(self._polite_min, self._polite_max)
        if elapsed < gap:
            time.sleep(gap - elapsed)

    # ---- public fetch -----------------------------------------------------

    def fetch_text(self, url: str, *, tier: int = 0, headers: dict | None = None) -> str:
        """Retrieve `url` as decoded text.

        tier=0: Tier-0 curl_cffi (rotating coherent fingerprint). On a detected
        challenge/ban it escalates ONLY if this engine was built with
        allow_tier1_escalation=True; otherwise it fails loud (never returns the
        interstitial body).
        tier>=1: force the Tier-1 browser-assisted path (solve challenge in a real
        browser, mint cookies, then serve via Tier-0 cookie-reuse).
        """
        merged = dict(self._profile.headers)
        if headers:
            merged.update(headers)

        if tier >= 1:
            return self._fetch_tier1(url, headers=merged)

        return self._fetch_tier0(url, headers=merged, allow_escalation=self._allow_tier1)

    # ---- Tier-0 with retry + semantic block detection ---------------------

    def _fetch_tier0(self, url: str, *, headers: dict, allow_escalation: bool) -> str:
        last_err: Exception | None = None
        for attempt in range(_MAX_RETRIES):
            self._polite_wait()
            try:
                resp = self._session.get(url, headers=headers, timeout=_TIMEOUT)
                self.last_status = resp.status_code
                self._last_fetch_at = time.monotonic()
                verdict = ban_detector.classify(
                    resp.status_code, resp.text, dict(resp.headers))
                self.last_verdict = verdict

                if resp.status_code == 200 and verdict == Verdict.OK:
                    self.fetch_count += 1
                    self.last_tier = 0
                    return resp.text

                if verdict == Verdict.NOT_FOUND:
                    raise FetchError(f"HTTP {resp.status_code} on {url} (not found)")

                if verdict in (Verdict.CHALLENGE, Verdict.BANNED):
                    # A WAF is in the way. Try a coherent fingerprint rotation
                    # once (cheap); if escalation is allowed and rotation fails,
                    # hand off to the real browser.
                    rotated = self._rotate_and_retry(url, headers, verdict)
                    if rotated is not None:
                        return rotated
                    if allow_escalation:
                        return self._fetch_tier1(url, headers=headers)
                    raise FetchError(
                        f"HTTP {resp.status_code} on {url}: {verdict.value} "
                        f"(fingerprint {self._profile.key}; Tier-1 escalation off)")

                if resp.status_code in _RETRYABLE:
                    last_err = FetchError(f"HTTP {resp.status_code} on {url}")
                    self._backoff(attempt, resp.headers.get("Retry-After"))
                    continue
                # non-retryable, non-WAF (e.g. 400) — fail loud, do not mask
                raise FetchError(f"HTTP {resp.status_code} on {url} (non-retryable)")
            except FetchError:
                raise
            except Exception as e:  # noqa: BLE001 — transient network/TLS blip
                last_err = e
                self._last_fetch_at = time.monotonic()
                self._backoff(attempt, None)
        raise FetchError(f"exhausted {_MAX_RETRIES} retries for {url}: {last_err}")

    def _rotate_and_retry(self, url: str, headers: dict, verdict: Verdict) -> str | None:
        """Swap to a fresh coherent fingerprint and retry once. None if no luck."""
        nxt = self._pool.rotate(self._profile, already_tried=self._tried_profiles)
        if nxt is None:
            return None
        self._swap_profile(nxt)
        # Use the new profile's coherent headers (caller overrides preserved).
        retry_headers = dict(self._profile.headers)
        for k, v in headers.items():
            # keep caller-supplied non-fingerprint headers (e.g. Referer, X-*)
            if k.lower() not in {h.lower() for h in self._profile.headers}:
                retry_headers[k] = v
        try:
            self._polite_wait()
            resp = self._session.get(url, headers=retry_headers, timeout=_TIMEOUT)
            self.last_status = resp.status_code
            self._last_fetch_at = time.monotonic()
            v2 = ban_detector.classify(resp.status_code, resp.text, dict(resp.headers))
            self.last_verdict = v2
            if resp.status_code == 200 and v2 == Verdict.OK:
                self.fetch_count += 1
                self.last_tier = 0
                return resp.text
        except Exception:  # noqa: BLE001 - rotation retry is best-effort
            return None
        return None

    # ---- Tier-1: real browser solve + cookie-reuse ------------------------

    def _fetch_tier1(self, url: str, *, headers: dict) -> str:
        """Solve a challenge in a real browser, mint cookies, serve via Tier-0.

        After the browser mints the clearance cookie, we reuse it from curl_cffi
        with the SAME identity. The reuse invariant is strict: a cookie minted
        under one UA/IP dies if replayed under another. We therefore pin the
        session UA to the browser's UA for the served request.
        """
        from pipeline.engine.tier1 import Tier1Error, solve_challenge

        try:
            result = solve_challenge(url, engine=self._tier1_engine, proxy=self._proxy)
        except Tier1Error as e:
            raise FetchError(f"Tier-1 solve failed for {url}: {e}") from e

        self._tier1_cookies = dict(result.cookies)
        self._apply_cookies(self._tier1_cookies)
        self.last_tier = 1

        # Pin the served request to the browser's exact UA (reuse invariant).
        served_headers = dict(headers)
        if result.user_agent:
            served_headers["User-Agent"] = result.user_agent

        browser_ok = bool(result.html) and ban_detector.classify(200, result.html) == Verdict.OK
        try:
            self._polite_wait()
            resp = self._session.get(url, headers=served_headers, timeout=_TIMEOUT)
            self.last_status = resp.status_code
            self._last_fetch_at = time.monotonic()
            verdict = ban_detector.classify(resp.status_code, resp.text, dict(resp.headers))
            self.last_verdict = verdict
            if resp.status_code == 200 and verdict == Verdict.OK:
                self.fetch_count += 1
                return resp.text
        except Exception as e:  # noqa: BLE001 — served request raised (network/TLS)
            # Reuse couldn't even complete. Return the browser's content ONLY if it
            # is genuinely clean (a real solve), never a block page.
            if browser_ok:
                self.fetch_count += 1
                return result.html
            raise FetchError(f"Tier-1 cookie-reuse fetch failed for {url}: {e}") from e

        # Served a non-OK verdict. Distinguish two cases (fail-loud doctrine):
        #  * BANNED  -> identity/IP is burned. The browser ran on the SAME burned
        #    IP, so its HTML is almost certainly the block page too — do NOT trust
        #    it. Fail loud; the fix is a residential ES proxy (PENDING-CREDENTIAL).
        #  * CHALLENGE -> the cheap reuse hasn't caught up but the browser DID mint
        #    a real solve; if its HTML is genuinely clean content, serve that.
        if self.last_verdict == Verdict.CHALLENGE and browser_ok:
            self.fetch_count += 1
            return result.html
        hint = ""
        if self.last_verdict == Verdict.BANNED and self._proxy is None:
            from pipeline.engine.tier1.browser import PENDING_CREDENTIAL_PROXY
            hint = f" [{PENDING_CREDENTIAL_PROXY}]"
        raise FetchError(
            f"Tier-1 for {url}: cookie-reuse still blocked "
            f"(status={self.last_status}, verdict="
            f"{self.last_verdict.value if self.last_verdict else None}){hint}")

    @staticmethod
    def _backoff(attempt: int, retry_after: str | None) -> None:
        if retry_after and str(retry_after).isdigit():
            time.sleep(min(float(retry_after), 30.0))
            return
        delay = _BACKOFF_BASE * (2 ** attempt)
        time.sleep(min(delay, 30.0) * random.uniform(0.5, 1.0))  # full jitter


# Module-level convenience: a process-wide default engine for one-off fetches.
# For a multi-page drain, instantiate your OWN FetchEngine and reuse it so the
# whole drain shares one fingerprint + cookie jar.
_default_engine: FetchEngine | None = None


def _engine() -> FetchEngine:
    global _default_engine
    if _default_engine is None:
        # Pin the process default to the legacy profile for reproducibility; a
        # drain that wants rotation/Tier-1 builds its own FetchEngine.
        _default_engine = FetchEngine(impersonate=DEFAULT_PROFILE_KEY)
    return _default_engine


def fetch_text(url: str, *, tier: int = 0, headers: dict | None = None) -> str:
    """Fetch `url` -> decoded text using the process default Tier-0 engine.

    The public entry point that replaces the urllib pattern across the pipeline.
    Tier-1 escalation on the process default is opt-in via an explicit tier>=1.
    """
    return _engine().fetch_text(url, tier=tier, headers=headers)
