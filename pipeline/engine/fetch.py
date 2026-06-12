"""FASE 2 (engine) — the tiered fetch ENGINE. Replaces the urllib pattern.

Tier-0 (this module): curl_cffi with full browser impersonation — a real Chrome
TLS/JA3 + HTTP2 fingerprint, kept COHERENT at the session level (one Session ->
one fingerprint -> one cookie jar) so a paginated drain looks like one browser,
not N disconnected stdlib requests. This is what 02-SCRAPING-ENGINE.md calls the
curl_cffi-class engine for OPEN platforms (AS24, autocasion, coches.com...).

Why this replaces urllib: AutoScout24 (and most platforms) gate on the *client
fingerprint*, not just the UA string. urllib emits a Python TLS handshake that a
modern WAF flags instantly; curl_cffi emits Chrome's. The Anthropic UA is blocked
by AS24, a Chrome UA over a Chrome TLS fingerprint passes (verified live 2026-06-12).

Tier-1 hook (NOT built here, documented for P1): platforms behind an active
challenge (Akamai sensor, Cloudflare managed challenge, GeeTest, DataDome) need a
real browser engine — camoufox / BotBrowser with residential ES egress — to mint
the session token the API/SPA then accepts. The seam is `fetch_text(..., tier=...)`:
when `tier >= 1` is requested this module raises NotImplementedError pointing at
the camoufox path, so the caller chooses the engine explicitly and a Tier-1 target
can never silently fall back to the (insufficient) Tier-0 fetch.
"""
from __future__ import annotations

import random
import time

from curl_cffi import requests as cffi_requests

# Latest stable Chrome profile curl_cffi ships. If a newer build adds a higher
# chromeNNN, bump here in one place (fingerprint coherence is a single knob).
_IMPERSONATE = "chrome131"

_DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
_DEFAULT_HEADERS = {
    "User-Agent": _DEFAULT_UA,
    "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
               "image/avif,image/webp,*/*;q=0.8"),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

_RETRYABLE = {429, 500, 502, 503, 504}
_TIMEOUT = 40
_MAX_RETRIES = 4
_BACKOFF_BASE = 2.0          # seconds; grows 2,4,8,16 with full jitter
_POLITE_MIN = 0.7            # min delay between successful fetches on a session
_POLITE_MAX = 1.4


class FetchError(RuntimeError):
    """Raised when a URL cannot be retrieved after the retry budget."""


class FetchEngine:
    """A fingerprint-coherent fetch session (Tier-0).

    One engine == one Chrome fingerprint == one cookie jar. Reuse the SAME engine
    for every page of a single drain so the platform sees one continuous browser.
    """

    def __init__(self, *, impersonate: str = _IMPERSONATE,
                 polite_min: float = _POLITE_MIN, polite_max: float = _POLITE_MAX) -> None:
        self._session = cffi_requests.Session(impersonate=impersonate)
        self._polite_min = polite_min
        self._polite_max = polite_max
        self._last_fetch_at: float | None = None
        self.impersonate = impersonate
        self.last_status: int | None = None
        self.fetch_count = 0

    def _polite_wait(self) -> None:
        if self._last_fetch_at is None:
            return
        elapsed = time.monotonic() - self._last_fetch_at
        gap = random.uniform(self._polite_min, self._polite_max)
        if elapsed < gap:
            time.sleep(gap - elapsed)

    def fetch_text(self, url: str, *, tier: int = 0, headers: dict | None = None) -> str:
        """Retrieve `url` as decoded text. Tier-0 only.

        Retries the retryable statuses (429/5xx) and transient network errors with
        exponential backoff + full jitter, honoring Retry-After when present. Raises
        FetchError on a non-retryable status or budget exhaustion (never returns a
        challenge/empty body silently — the caller must see the failure).
        """
        if tier != 0:
            raise NotImplementedError(
                f"tier={tier} requested: Tier-1 (camoufox/BotBrowser + residential "
                "egress) is the documented P1 hook, not built in fetch.py. Route "
                "challenge-walled platforms through the Tier-1 engine explicitly.")

        merged = dict(_DEFAULT_HEADERS)
        if headers:
            merged.update(headers)

        last_err: Exception | None = None
        for attempt in range(_MAX_RETRIES):
            self._polite_wait()
            try:
                resp = self._session.get(url, headers=merged, timeout=_TIMEOUT)
                self.last_status = resp.status_code
                self._last_fetch_at = time.monotonic()
                if resp.status_code == 200:
                    self.fetch_count += 1
                    return resp.text
                if resp.status_code in _RETRYABLE:
                    last_err = FetchError(f"HTTP {resp.status_code} on {url}")
                    self._backoff(attempt, resp.headers.get("Retry-After"))
                    continue
                # non-retryable (403/404/410...) — fail loud, do not mask
                raise FetchError(f"HTTP {resp.status_code} on {url} (non-retryable)")
            except FetchError:
                raise
            except Exception as e:  # noqa: BLE001 — transient network/TLS blip
                last_err = e
                self._last_fetch_at = time.monotonic()
                self._backoff(attempt, None)
        raise FetchError(f"exhausted {_MAX_RETRIES} retries for {url}: {last_err}")

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
        _default_engine = FetchEngine()
    return _default_engine


def fetch_text(url: str, *, tier: int = 0, headers: dict | None = None) -> str:
    """Fetch `url` -> decoded text using the process default Tier-0 engine.

    The public entry point that replaces the urllib pattern across the pipeline.
    """
    return _engine().fetch_text(url, tier=tier, headers=headers)
