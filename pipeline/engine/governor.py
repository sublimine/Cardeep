"""P1 — the per-HOST rate governor. THE bottleneck, mechanized (04-ORCHESTRATION §5,
06-RESILIENCE-OPS §7.1).

The scar this exists to make impossible: "138 dealers cayeron por throttling de AS24
bajo carga 4x. La cosecha es el cuello (rate-limit de fuente), no el sistema."
Four naive parallel workers were each polite (time.sleep per worker) but the AGGREGATE
against one host was a hammer, because nothing coordinated them. The fix is a single
token bucket PER HOST, shared across every concurrent task in the process: no matter how
many workers run, the aggregate request rate to a host cannot exceed that host's bucket.

Model
-----
One asyncio-safe token bucket per registrable host. Tokens refill continuously at
`rate` per second up to `burst` depth. `acquire(host)` awaits until a token is available
for that host, draws it, and (with a small jitter floor) guarantees a minimum spacing
between consecutive grants — so even a burst-empty bucket paces requests like a human,
not a flat-out loop. Buckets are independent: AS24 throttling never slows Kia (law #5
isolation, 06 §7.3).

Concurrency model
-----------------
Single-process, in-memory, asyncio. The bucket math is guarded by an asyncio.Lock per
host so concurrent coroutines draw tokens atomically. This is correct and crash-safe for
ONE process (P1). The documented upgrade hook for MULTI-process / multi-machine (P2,
04 §5.1) is a Redis-backed GCRA/token-bucket Lua script keyed by host — `acquire` becomes
an atomic Redis call and the per-host `asyncio.Lock` becomes a Redis key. The PUBLIC API
(`acquire`, `slot`, `wrap_fetch_text`) does not change when that lands: callers are
already written against the choke point, so the storage swap is invisible to them.

Integration (the single choke point)
-------------------------------------
`wrap_fetch_text(engine_or_fetch)` returns an async callable that, for every URL, derives
the host, `await acquire(host)`, then runs the (synchronous) curl_cffi fetch in a thread
so the event loop is never blocked. NOTHING fetches a host faster than its bucket because
the only path to the fetch engine for governed code is through this wrapper.
"""
from __future__ import annotations

import asyncio
import random
import time
from contextlib import asynccontextmanager
from urllib.parse import urlsplit

from pipeline.engine.fetch import FetchEngine, fetch_text as _raw_fetch_text

# Default profile. AS24's scar set the doctrine: a single host must be paced WELL below
# the rate that earned the ban. ~0.7 req/s steady with a tiny burst and a hard min-spacing
# floor (+jitter) is the conservative human-shaped pace 06 §7.2 mandates for any host whose
# true ceiling is not yet measured. Per-host overrides arrive from source_health.tuning (P2).
DEFAULT_RATE_PER_SEC = 0.7          # steady refill: ~1 request every 1.43 s
DEFAULT_BURST = 3.0                 # bucket depth (tokens) — small head-room, never a flood
DEFAULT_MIN_SPACING_S = 1.0 / DEFAULT_RATE_PER_SEC   # floor between grants on one host
DEFAULT_JITTER_S = 0.25             # +U(0, jitter) on each grant: no lock-step probing


# ---------------------------------------------------------------------------
# RATE CLASSES — per-host pacing doctrine, by what the host actually IS.
# ---------------------------------------------------------------------------
# The governor's job is to never out-pace a host's true ceiling. That ceiling is NOT one
# number: a public JSON search API built to serve millions of users tolerates 10-20 req/s
# without blinking, while a fragile HTML/stealth surface behind an active WAF earns a ban
# the moment you push past a human cadence. Pacing BOTH at the AS24-scar rate (0.7 req/s)
# was correct safety for the fragile hosts but left the JSON APIs crawling at a tiny
# fraction of what they happily allow — the harvest's real bottleneck.
#
# So pacing is keyed to a CLASS, not a global default:
#
#   STEALTH  (default, 0.7 req/s) — unknown / HTML / stealth / WAF-walled hosts whose true
#            ceiling is unmeasured. The AS24 scar lives here: pace WELL below the rate that
#            earned the ban, human-shaped, tiny burst. NEVER raise these without evidence.
#
#   JSON_API (12 req/s, burst 24) — first-party JSON gateways engineered for high traffic
#            (mobile-app / SPA backends serving the whole user base). These tolerate an
#            order of magnitude more than a stealth HTML scrape. The min-spacing floor and
#            jitter still apply (no lock-step probing) — just at the higher rate, so the
#            aggregate is fast but never a flat-out lockstep loop.
#
# To add a host: pick its class, add ONE line to _HOST_RATE_CLASSES below. Do not invent a
# fourth knob per host — classes keep the table honest and auditable. A host with a measured
# ceiling that differs from its class can still get a bespoke configure_host() override; the
# classes are the documented, safe defaults.

# JSON-API tier: first-party gateways built to serve millions. ~12 req/s steady, burst 24
# (half a second of head-room), min-spacing ~0.03 s floor (+jitter) so even an empty bucket
# paces ~33 req/s worst-case micro-bursts, not an unbounded flood. Jitter shrinks with the
# rate so it stays a fraction of the spacing (no lock-step, no idle gaps).
JSON_API_RATE_PER_SEC = 12.0
JSON_API_BURST = 24.0
JSON_API_MIN_SPACING_S = 0.03
JSON_API_JITTER_S = 0.02

# host -> rate-class profile. The single, auditable place pacing policy lives.
# Anything NOT in this table inherits the STEALTH default (0.7 req/s) — the safe direction:
# an unrecognized host is treated as fragile until proven otherwise, never the reverse.
_JSON_API_PROFILE = {
    "rate_per_sec": JSON_API_RATE_PER_SEC,
    "burst": JSON_API_BURST,
    "min_spacing_s": JSON_API_MIN_SPACING_S,
    "jitter_s": JSON_API_JITTER_S,
}
_HOST_RATE_CLASSES: dict[str, dict] = {
    # coches.net's internal search gateway — unwalled first-party JSON API, the SPA/mobile
    # backend behind www.coches.net. Serves the whole user base; tolerates JSON_API pacing.
    "web.gw.coches.net": _JSON_API_PROFILE,
    # wallapop's public mobile-app JSON API — built for an enormous mobile install base.
    "api.wallapop.com": _JSON_API_PROFILE,
    # autocasion's GraphQL gateway — first-party JSON API serving the site's whole frontend.
    "gql.autocasion.com": _JSON_API_PROFILE,
    # renew (Renault Group OEM-VO portal) — its AEM+Elasticsearch .data single-fetch loader is
    # a first-party JSON gateway built to serve the brand's whole user base; tolerates JSON_API
    # pacing (open, no WAF challenge to curl_cffi — defense_tier=t0_open).
    "es.renew.auto": _JSON_API_PROFILE,
}


def host_of(url: str) -> str:
    """Registrable host for `url`, lower-cased, port-stripped. The bucket key.

    Note: this returns the netloc host (e.g. 'www.autoscout24.es'). Grouping a shared
    infra family (Adevinta bon: coches.net/milanuncios/fotocasa) under ONE bucket — 06
    §7.1 — is a host->family alias map layered on top; absent an alias the host itself is
    the safe (stricter, never laxer) default. The alias map is a P2 tuning concern and
    does not change this contract.
    """
    netloc = urlsplit(url).netloc.lower()
    if "@" in netloc:                       # strip any userinfo
        netloc = netloc.rsplit("@", 1)[1]
    if netloc.startswith("["):              # IPv6 literal [::1]:8080
        return netloc.split("]")[0] + "]"
    return netloc.split(":")[0] or netloc


class _Bucket:
    """One continuous token bucket + min-spacing floor for a single host."""

    __slots__ = ("rate", "burst", "min_spacing", "jitter", "_tokens", "_last_refill",
                 "_last_grant", "_lock")

    def __init__(self, rate: float, burst: float, min_spacing: float, jitter: float) -> None:
        self.rate = rate
        self.burst = burst
        self.min_spacing = min_spacing
        self.jitter = jitter
        self._tokens = burst                       # start full: first request is immediate
        self._last_refill = time.monotonic()
        self._last_grant = 0.0
        self._lock = asyncio.Lock()

    def _refill(self, now: float) -> None:
        elapsed = now - self._last_refill
        if elapsed > 0:
            self._tokens = min(self.burst, self._tokens + elapsed * self.rate)
            self._last_refill = now

    async def acquire(self) -> float:
        """Block until a token is available AND min-spacing has elapsed; draw it.

        Returns the wall-clock seconds this call waited (0.0 if immediate) — telemetry
        for proving the choke point and for AIMD tuning later.
        """
        waited = 0.0
        async with self._lock:                     # atomic token math per host (asyncio)
            while True:
                now = time.monotonic()
                self._refill(now)
                # spacing floor: never grant two requests to one host closer than
                # min_spacing (+ jitter) apart, even if tokens are available.
                spacing_gap = self.min_spacing - (now - self._last_grant) if self._last_grant else 0.0
                if self._tokens >= 1.0 and spacing_gap <= 0:
                    self._tokens -= 1.0
                    self._last_grant = now
                    return waited
                # compute the shortest sleep that could satisfy both constraints.
                need_token = 0.0 if self._tokens >= 1.0 else (1.0 - self._tokens) / self.rate
                sleep_for = max(need_token, spacing_gap)
                if sleep_for <= 0:
                    sleep_for = 0.001
                sleep_for += random.uniform(0.0, self.jitter)
                waited += sleep_for
                await asyncio.sleep(sleep_for)


class RateGovernor:
    """Per-host token-bucket governor. THE single choke point in front of every fetch.

    Crash-safe for one process (in-memory buckets). Multi-process upgrade hook: swap the
    per-host `_Bucket` for a Redis GCRA Lua script keyed by host (P2, 04 §5.1) — the
    public API below is the stable seam and does not change.
    """

    def __init__(self, *, rate_per_sec: float = DEFAULT_RATE_PER_SEC,
                 burst: float = DEFAULT_BURST,
                 min_spacing_s: float | None = None,
                 jitter_s: float = DEFAULT_JITTER_S) -> None:
        self._default_rate = rate_per_sec
        self._default_burst = burst
        self._default_spacing = min_spacing_s if min_spacing_s is not None else (1.0 / rate_per_sec)
        self._default_jitter = jitter_s
        self._buckets: dict[str, _Bucket] = {}
        self._overrides: dict[str, dict] = {}
        self._registry_lock = asyncio.Lock()

    def configure_host(self, host: str, *, rate_per_sec: float | None = None,
                       burst: float | None = None, min_spacing_s: float | None = None,
                       jitter_s: float | None = None) -> None:
        """Set a per-host profile (e.g. AS24 born stricter from the scar). Takes effect
        the next time the host's bucket is created. In P2 these come from
        source_health.tuning; here they are an explicit, committed seed."""
        self._overrides[host.lower()] = {
            "rate": rate_per_sec, "burst": burst,
            "min_spacing": min_spacing_s, "jitter": jitter_s,
        }

    async def _bucket(self, host: str) -> _Bucket:
        b = self._buckets.get(host)
        if b is not None:
            return b
        async with self._registry_lock:
            b = self._buckets.get(host)
            if b is None:
                ov = self._overrides.get(host, {})
                rate = ov.get("rate") or self._default_rate
                burst = ov.get("burst") or self._default_burst
                spacing = ov.get("min_spacing")
                if spacing is None:
                    spacing = self._default_spacing
                jitter = ov.get("jitter")
                if jitter is None:
                    jitter = self._default_jitter
                b = _Bucket(rate, burst, spacing, jitter)
                self._buckets[host] = b
            return b

    async def acquire(self, host: str) -> float:
        """Await a token for `host`. Returns the seconds waited. THE throttle (§5)."""
        bucket = await self._bucket(host)
        return await bucket.acquire()

    @asynccontextmanager
    async def slot(self, host: str):
        """`async with governor.slot(host): ...` — acquire a token for the duration of a
        guarded fetch. Yields the seconds waited acquiring the slot."""
        waited = await self.acquire(host)
        try:
            yield waited
        finally:
            # Token-bucket model: a token is spent on acquire and refills over time; there
            # is nothing to release. The context manager exists for call-site clarity and
            # as the seam where a leased-concurrency model (P2) would return its lease.
            pass

    def wrap_fetch_text(self, fetch_callable=None, *, engine: FetchEngine | None = None):
        """Return an async `fetch(url, **kw)` that routes EVERY fetch through this governor.

        This is the integration point: hand harvest code this wrapper instead of the raw
        `fetch_text`, and no host can be fetched faster than its bucket. The underlying
        synchronous curl_cffi fetch runs in a worker thread (asyncio.to_thread) so the
        event loop — and thus every other host's governor — is never blocked while one
        host's request is in flight.

        Precedence: explicit `fetch_callable` > `engine.fetch_text` > module `fetch_text`.
        """
        if fetch_callable is None:
            fetch_callable = engine.fetch_text if engine is not None else _raw_fetch_text

        async def governed_fetch(url: str, **kwargs) -> str:
            host = host_of(url)
            await self.acquire(host)
            return await asyncio.to_thread(fetch_callable, url, **kwargs)

        return governed_fetch


# Process-wide default governor: the single shared bottleneck for the whole process.
# Born with AS24 stricter than default, exactly because 4x flat-out earned the ban.
_default_governor: RateGovernor | None = None


def governor() -> RateGovernor:
    global _default_governor
    if _default_governor is None:
        g = RateGovernor()

        # --- STEALTH class (conservative, the AS24 scar stays) -----------------------
        # These hosts are HTML/stealth/WAF-walled with an UNMEASURED ceiling. They are
        # paced WELL below the rate that earned the ban — never raised without evidence.
        # The scar's lesson, encoded: AS24 hosts paced below the banned rate.
        g.configure_host("www.autoscout24.es", rate_per_sec=0.5, burst=2.0, min_spacing_s=2.0)
        g.configure_host("autoscout24.es", rate_per_sec=0.5, burst=2.0, min_spacing_s=2.0)
        # coches.com (Carossa) is Imperva-fronted (is_tier1=TRUE) but serving PDPs/sitemap
        # to a plain chrome131 impersonation today — a decaying-open window. The recipe
        # paces ~0.6-0.9 s/req on a single held IP; the governor floors it at the
        # conservative below-the-unknown-ceiling rate the AS24 scar mandated for any
        # Tier-1 HTML host. STAYS conservative (sitemap + PDP = fragile stealth surface).
        g.configure_host("www.coches.com", rate_per_sec=1.0, burst=3.0, min_spacing_s=0.8)
        # motor.es — HTML/stealth surface, unmeasured ceiling: STAYS on the conservative
        # default (no override needed; left here as an explicit reminder it must not move).
        # Das WeltAuto (VW Group OEM-VO portal) — AEM/Motorflash SSR HTML behind a SOFT TLS/UA
        # wall (origin 403s a naïve fetch, serves cleanly to chrome131; defense_tier=t1_soft, no
        # JS challenge). It is an HTML surface, NOT a JSON gateway, so it stays in the STEALTH
        # family: paced conservatively below an unmeasured ceiling (like coches.com), human-shaped.
        g.configure_host("www.dasweltauto.es", rate_per_sec=1.0, burst=3.0, min_spacing_s=0.8)
        # autocasion SSR/PDP host (www.autocasion.com) — HTML surface behind a Cloudflare
        # that is MEASURED permissive to a chrome131 fingerprint: the tier1 recipe probe
        # (autocasion_datalayer.md) hit it at scale — national counter, 184 make-facet
        # <title>s, MB x 52 provinces, multi-page drains — from ONE residential IP with
        # ZERO 429/403 and no JS challenge (cf-cache-status: DYNAMIC). So unlike the
        # unmeasured-ceiling stealth hosts above, autocasion has EVIDENCE it serves well
        # past a 0.7 req/s crawl. Paced to a still-conservative, human-shaped 2 req/s
        # (min-spacing 0.5 s + jitter) — an order of magnitude below what a permissive CF
        # edge serves, but enough that the PDP-attribution path (the make-partition drain's
        # bottleneck, two www GETs per car) is not strangled. STILL well below any ban
        # rate; the breaker + first-CF-tripwire escalation (recipe) remain the safety net.
        g.configure_host("www.autocasion.com", rate_per_sec=2.0, burst=4.0, min_spacing_s=0.5)

        # --- JSON_API class (fast, built-for-traffic first-party gateways) -----------
        # Apply the JSON-API rate class to every host registered in _HOST_RATE_CLASSES.
        # These are first-party JSON gateways engineered to serve the whole user base; the
        # AS24 stealth rate was strangling them at a fraction of what they happily allow.
        # The min-spacing/jitter floor still holds — fast, but never a lock-step loop.
        for host, profile in _HOST_RATE_CLASSES.items():
            g.configure_host(host, **profile)

        _default_governor = g
    return _default_governor


async def acquire(host: str) -> float:
    """Module convenience: acquire on the process-wide governor."""
    return await governor().acquire(host)


def governed_fetch_text(*, engine: FetchEngine | None = None):
    """Module convenience: the governed fetch callable on the process-wide governor.

    Usage in harvest code (the single choke point in front of engine.fetch):
        fetch = governed_fetch_text(engine=my_engine)
        html = await fetch(url)        # paced by the host's bucket, off the event loop
    """
    return governor().wrap_fetch_text(engine=engine)
