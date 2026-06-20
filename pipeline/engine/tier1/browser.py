"""Tier-1 browser engines: solve an active challenge once, mint reusable cookies.

THE PATTERN (cookie-reuse): an active challenge (Cloudflare managed challenge /
Turnstile, DataDome, Akamai sensor) requires a real browser to execute the JS and
mint a clearance cookie (`cf_clearance`, `datadome`, `_abck`). Once minted, that
cookie can be replayed by the cheap curl_cffi Tier-0 engine for thousands of
requests — BUT ONLY if the replay keeps the SAME identity that solved it: same
User-Agent, same TLS/JA3 shape, same egress IP. If any of those differ, the WAF
invalidates the cookie on first reuse. This module returns the cookies AND the
exact User-Agent the browser presented, so the caller can pin them together.

ENGINES:
  * nodriver  — primary. Drives Chrome over CDP directly, with NO Playwright/
    Selenium shim, so it does not expose the automation-protocol fingerprint that
    fingerprint patches cannot hide. In an independent 651-verdict benchmark
    (ianlpaterson.com, 2026-05-13) it was the only tool with ZERO blocks.
        ┌──────────────────────────────────────────────────────────────────┐
        │  LICENSE WARNING — nodriver is AGPL-3.0 (network copyleft).        │
        │  If cardeep ever exposes a NETWORK SERVICE that uses nodriver,     │
        │  AGPL-3.0 can require publishing the derivative source. This is a  │
        │  LICENSING DECISION FOR THE OWNER, surfaced here on purpose and    │
        │  NOT hidden. Camoufox (MPL-2.0, far more permissive) is provided   │
        │  as a drop-in alternative; set engine="camoufox" to avoid AGPL.    │
        └──────────────────────────────────────────────────────────────────┘
  * camoufox — secondary. A patched-Firefox stealth browser (MPL-2.0). Use it to
    avoid AGPL, for Firefox-shaped targets, or as a fallback when nodriver fails.

PROXY: residential ES sticky egress is the transversal requirement for real
Tier-1 targets (the clearance cookie is bound to the solving IP). A `proxy` arg
is threaded through but, with no paid credential wired yet, callers pass None and
this is marked PENDING-CREDENTIAL. Cost stays zero until a proxy is provisioned.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field


class Tier1Error(RuntimeError):
    """Raised when a Tier-1 browser solve fails (engine missing, timeout, block)."""


@dataclass
class BrowserResult:
    """Outcome of a browser solve. Pin `cookies` + `user_agent` together on reuse."""
    html: str
    cookies: dict          # name -> value, ready to inject into a curl_cffi jar
    user_agent: str        # the EXACT UA the browser presented (reuse invariant)
    final_url: str
    engine: str            # "nodriver" | "camoufox"
    raw_cookies: list = field(default_factory=list)  # full cookie dicts (domain/path)


# Engines that exist but require a paid/credentialed dependency are isolated here
# so the cost-zero default never touches them.
PENDING_CREDENTIAL_PROXY = (
    "residential ES sticky proxy not provisioned -- Tier-1 against IP-bound WAFs "
    "(DataDome/Akamai live) needs it; running browser on host IP for now."
)


def solve_challenge(url: str, *, engine: str = "nodriver",
                    proxy: str | None = None, timeout: float = 45.0,
                    wait_after_load: float = 4.0, headless: bool = True) -> BrowserResult:
    """Solve a challenge at `url` with a real browser and return cookies + UA.

    Synchronous wrapper over the async engines (the fetch layer is sync). Raises
    Tier1Error on any failure — never returns a challenge page masquerading as
    content (the caller must see the failure, per the fail-loud doctrine).

    proxy: PENDING-CREDENTIAL. Pass None for cost-zero host-IP solving; pass a
    "http://user:pass@host:port" string once a residential ES proxy is wired.
    """
    if engine not in ("nodriver", "camoufox"):
        raise Tier1Error(f"unknown Tier-1 engine {engine!r}")
    try:
        return _run_coro(_solve_async(
            url, engine=engine, proxy=proxy, timeout=timeout,
            wait_after_load=wait_after_load, headless=headless))
    except Tier1Error:
        raise
    except Exception as e:  # noqa: BLE001 — normalize any engine-level failure
        raise Tier1Error(f"{engine} solve failed for {url}: {e}") from e


def _run_coro(coro):
    """Run an async solve on a managed loop, with a grace tick + warning silence.

    `asyncio.run` on Windows (ProactorEventLoop) closes the loop while the browser
    subprocess transports still hold pipe handles, so their __del__ later raises
    'I/O operation on closed pipe' ResourceWarnings — cosmetic noise, not a real
    failure. We run on our own loop, give pending transport callbacks a tick to
    drain, then close, and suppress the residual ResourceWarning.
    """
    import warnings

    loop = asyncio.new_event_loop()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            result = loop.run_until_complete(coro)
            loop.run_until_complete(asyncio.sleep(0.25))  # let subprocess pipes drain
            return result
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception:  # noqa: BLE001
            pass
        loop.close()


async def _solve_async(url: str, *, engine: str, proxy: str | None,
                       timeout: float, wait_after_load: float,
                       headless: bool) -> BrowserResult:
    if engine == "nodriver":
        return await _solve_nodriver(url, proxy=proxy, timeout=timeout,
                                     wait_after_load=wait_after_load, headless=headless)
    return await _solve_camoufox(url, proxy=proxy, timeout=timeout,
                                 wait_after_load=wait_after_load, headless=headless)


async def _solve_nodriver(url: str, *, proxy: str | None, timeout: float,
                          wait_after_load: float, headless: bool) -> BrowserResult:
    # AGPL-3.0 dependency — imported lazily so importing pipeline.engine never
    # pulls AGPL code unless a Tier-1 solve is actually requested.
    try:
        import nodriver as uc
    except ImportError as e:  # pragma: no cover - environment dependent
        raise Tier1Error("nodriver not installed (pip install nodriver)") from e

    browser = None
    try:
        browser_args = []
        if proxy:
            browser_args.append(f"--proxy-server={proxy}")
        browser = await uc.start(headless=headless, browser_args=browser_args or None)
        page = await asyncio.wait_for(browser.get(url), timeout=timeout)
        # Let the challenge JS run and the clearance cookie settle.
        await asyncio.sleep(wait_after_load)
        html = await page.get_content()
        ua = ""
        try:
            ua = await page.evaluate("navigator.userAgent")
        except Exception:  # noqa: BLE001 - UA read is best-effort
            ua = ""
        cookie_objs = await browser.cookies.get_all()
        cookies, raw = _normalize_nodriver_cookies(cookie_objs)
        final = getattr(page, "url", url) or url
        return BrowserResult(html=html, cookies=cookies, user_agent=ua or "",
                             final_url=final, engine="nodriver", raw_cookies=raw)
    finally:
        if browser is not None:
            try:
                browser.stop()
            except Exception:  # noqa: BLE001
                pass


async def _solve_camoufox(url: str, *, proxy: str | None, timeout: float,
                          wait_after_load: float, headless: bool) -> BrowserResult:
    try:
        from camoufox.async_api import AsyncCamoufox
    except ImportError as e:  # pragma: no cover
        raise Tier1Error("camoufox not installed (pip install camoufox[geoip])") from e

    proxy_cfg = {"server": proxy} if proxy else None
    async with AsyncCamoufox(headless=headless, proxy=proxy_cfg) as browser:
        page = await browser.new_page()
        await page.goto(url, timeout=int(timeout * 1000), wait_until="domcontentloaded")
        await asyncio.sleep(wait_after_load)
        html = await page.content()
        ua = await page.evaluate("() => navigator.userAgent")
        ctx_cookies = await page.context.cookies()
        cookies = {c["name"]: c["value"] for c in ctx_cookies}
        return BrowserResult(html=html, cookies=cookies, user_agent=ua or "",
                             final_url=page.url, engine="camoufox",
                             raw_cookies=list(ctx_cookies))


def _normalize_nodriver_cookies(cookie_objs) -> tuple[dict, list]:
    cookies: dict = {}
    raw: list = []
    for c in cookie_objs or []:
        name = getattr(c, "name", None)
        value = getattr(c, "value", None)
        if name is None and isinstance(c, dict):
            name, value = c.get("name"), c.get("value")
        if name is None:
            continue
        cookies[name] = value
        raw.append({
            "name": name, "value": value,
            "domain": getattr(c, "domain", None) if not isinstance(c, dict) else c.get("domain"),
            "path": getattr(c, "path", "/") if not isinstance(c, dict) else c.get("path", "/"),
        })
    return cookies, raw
