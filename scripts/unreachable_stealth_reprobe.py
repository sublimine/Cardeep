"""Stealth re-verification of the 92 'unreachable' long-tail domains.

The prior verdict (scripts/longtail_fingerprint.py + scripts/unreachable_reverify.py)
declared 91/92 of these dead/walled using a curl_cffi GET and a STATUS-checking basic
browser. The subastas/Autorola/BCA cases proved a non-JS / status-gated verdict LIES:
a real JS stealth browser with a coherent fingerprint, cookie-accept, JS settle and a
listing-path sweep cracks sites a bare probe calls "gated".

This re-tests EVERY domain with camoufox (anti-detect Firefox, real JS, humanised
fingerprint) on a STATUS-BLIND, RENDERED-BODY gate:

  1. DNS pre-check (socket.getaddrinfo): a domain that does not resolve on ANY host
     variant is genuinely dead (NXDOMAIN) — no browser fixes that. Recorded as
     bucket 'dns_dead'.
  2. For every domain that DOES resolve: launch camoufox, navigate the home page,
     wait for JS/challenge to settle, accept a cookie banner if present, then SWEEP a
     set of canonical Spanish used-car listing paths. A page is RECOVERED iff its
     rendered body clears a content gate (>= MIN_BYTES) AND shows car-listing signal
     (price tokens or vehicle deep-links), REGARDLESS of HTTP status (a 403 honeypot
     over a full listing is recovered; a 107-byte Cloudflare interstitial is not).
  3. A domain that resolves but never clears the gate under the stealth browser, and
     whose body is a persistent challenge/interstitial, is bucket 'hard_wall'.

Output: docs/_unreachable_stealth_result.json — per-domain verdict + evidence
(best path, status, bytes, price/deep-link counts, challenge fingerprint).

Read-only public-data market research. No login, no payment, own-site stock only.
"""
from __future__ import annotations

import json
import re
import socket
import sys
import time
from urllib.parse import urljoin, urlparse

from camoufox.sync_api import Camoufox

_NAV_TIMEOUT_MS = 18000
_SETTLE_MS = 3800
_MIN_BYTES = 6000          # body-content gate (status-blind)
_MIN_PRICES = 6           # car-listing signal: at least this many € price tokens
_MIN_DLINKS = 6           # OR this many plausible vehicle deep-links
_DOMAIN_BUDGET_S = 90     # hard wall-clock budget per domain (one slow host can't stall run)

# The home page is ALWAYS probed first; only if it renders (and is not a hard wall)
# do we sweep the listing paths. This avoids 17 timeouts on a connection-refused host.
_HOME_PATHS = ["/"]
# Canonical Spanish used-car listing paths, swept after a live home page.
_LISTING_PATHS = [
    "/coches-segunda-mano/", "/coches/segunda-mano/", "/coches/",
    "/vehiculos/", "/vehiculos-ocasion/", "/ocasion/", "/segunda-mano/",
    "/stock/", "/nuestro-stock/", "/coches-ocasion/", "/km0/", "/seminuevos/",
    "/vehiculos-segunda-mano/", "/catalogo/", "/turismos/", "/inventario/",
]

# Price tokens: 7.990 € / 7990€ / 12.500 EUR  (Spanish thousands sep '.')
_PRICE_RE = re.compile(r"\b\d{1,3}(?:\.\d{3})+\s*(?:€|eur)\b", re.I)
_PRICE_RE2 = re.compile(r"\b\d{4,6}\s*(?:€|eur)\b", re.I)
# Plausible vehicle deep-links (PDP slugs) on the dealer's own host.
_DLINK_RE = re.compile(
    r'href="([^"]*(?:/coche[s]?[-/]|/vehiculo[s]?[-/]|/ocasion/|/segunda-mano/)[^"]*)"',
    re.I)
# Hard-wall body fingerprints (Cloudflare / DataDome / generic challenge).
_WALL_SIGNS = (
    "just a moment", "checking your browser", "cf-browser-verification",
    "challenge-platform", "robot challenge screen", "attention required",
    "/cdn-cgi/challenge", "datadome", "captcha-delivery", "px-captcha",
    "perimeterx", "are you a human", "enable javascript and cookies",
    "request unsuccessful. incapsula", "_imperva",
)
_COOKIE_SELECTORS = [
    "#onetrust-accept-btn-handler",
    "button#didomi-notice-agree-button",
    "button[aria-label*='aceptar' i]",
    "button:has-text('Aceptar')",
    "button:has-text('ACEPTAR')",
    "button:has-text('Aceptar todo')",
    "button:has-text('Aceptar todas')",
    "button:has-text('De acuerdo')",
    "button:has-text('Entendido')",
    "a:has-text('Aceptar')",
    ".cookie-accept", ".cc-allow", "#cookie-accept",
]
_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)


def _host_variants(domain: str) -> list[str]:
    bare = re.sub(r"^www\.", "", domain.lower().strip())
    return [f"www.{bare}", bare]


def _dns_resolves(domain: str) -> str | None:
    """Return the first host variant that resolves, or None if NXDOMAIN on all."""
    for host in _host_variants(domain):
        try:
            socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
            return host
        except socket.gaierror:
            continue
        except Exception:
            # any other resolver hiccup: treat as resolvable, let the browser try
            return host
    return None


def _signal(html: str) -> dict:
    low = html.lower()
    prices = len(set(_PRICE_RE.findall(html))) + len(set(_PRICE_RE2.findall(html)))
    dlinks = len(set(_DLINK_RE.findall(html)))
    wall = next((w for w in _WALL_SIGNS if w in low), None)
    tm = _TITLE_RE.search(html)
    title = re.sub(r"\s+", " ", tm.group(1)).strip()[:120] if tm else None
    return {"bytes": len(html), "prices": prices, "dlinks": dlinks,
            "wall": wall, "title": title}


def _is_recovered(sig: dict) -> bool:
    if sig["bytes"] < _MIN_BYTES:
        return False
    if sig["wall"]:
        # a wall sign present AND no listing signal => not recovered
        if sig["prices"] < _MIN_PRICES and sig["dlinks"] < _MIN_DLINKS:
            return False
    return sig["prices"] >= _MIN_PRICES or sig["dlinks"] >= _MIN_DLINKS


def _accept_cookies(page) -> bool:
    for sel in _COOKIE_SELECTORS:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.click(timeout=2500)
                page.wait_for_timeout(900)
                return True
        except Exception:
            continue
    return False


def _render(browser, url: str, settle_ms: int, cookie_state: dict) -> dict:
    """Navigate one URL, settle JS, accept cookies once, return signal + status.
    Returns {'error': ...} on navigation failure (dead host / TLS / timeout)."""
    page = None
    try:
        page = browser.new_page()
        resp = page.goto(url, wait_until="domcontentloaded", timeout=_NAV_TIMEOUT_MS)
        page.wait_for_timeout(settle_ms)
        if not cookie_state["done"]:
            cookie_state["done"] = _accept_cookies(page)
            if cookie_state["done"]:
                page.wait_for_timeout(1100)
        html = page.content() or ""
        status = resp.status if resp is not None else None
        sig = _signal(html)
        sig["status"] = status
        return sig
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"[:160]}
    finally:
        if page is not None:
            try:
                page.close()
            except Exception:
                pass


def probe_domain(browser, domain: str, website: str) -> dict:
    host = _dns_resolves(domain)
    if host is None:
        return {"domain": domain, "bucket": "dns_dead",
                "evidence": "NXDOMAIN on www. and bare host (socket.getaddrinfo)"}

    started = time.monotonic()
    best = {"domain": domain, "bucket": "hard_wall", "host": host,
            "best_path": None, "status": None, "bytes": 0, "prices": 0,
            "dlinks": 0, "wall": None, "title": None}
    cookie_state = {"done": False}
    swept: list[dict] = []
    host_variants = [host] if host.startswith("www.") else [f"www.{host}", host]

    def consider(path: str, base: str, sig: dict) -> bool:
        """Record a rendered page; update best; return True if RECOVERED (stop)."""
        rec = {"path": path, "status": sig.get("status"), "bytes": sig.get("bytes", 0),
               "prices": sig.get("prices", 0), "dlinks": sig.get("dlinks", 0),
               "wall": sig.get("wall")}
        swept.append(rec)
        score = sig.get("prices", 0) * 2 + sig.get("dlinks", 0)
        best_score = best["prices"] * 2 + best["dlinks"]
        if sig.get("bytes", 0) >= _MIN_BYTES and score >= best_score:
            best.update({"best_path": path, "status": sig.get("status"),
                         "bytes": sig.get("bytes"), "prices": sig.get("prices"),
                         "dlinks": sig.get("dlinks"), "wall": sig.get("wall"),
                         "title": sig.get("title"), "base": base})
        if _is_recovered(sig):
            best.update({"bucket": "recovered", "best_path": path,
                         "status": sig.get("status"), "base": base})
            return True
        return False

    # --- Phase 1: home page on each host variant. A home page that errors on BOTH
    # variants means the site is dead from the public internet (no path sweep needed).
    home_alive_base = None
    home_wall = False
    for hv in host_variants:
        base = f"https://{hv}"
        sig = _render(browser, base + "/", _SETTLE_MS, cookie_state)
        if "error" in sig:
            swept.append({"path": "/", "host": hv, "error": sig["error"]})
            continue
        home_alive_base = base
        if sig.get("wall"):
            home_wall = True
        if consider("/", base, sig):
            best["evidence"] = (f"stealth render of / -> prices={best['prices']} "
                                f"dlinks={best['dlinks']} status={best['status']}")
            return best
        break  # one variant rendered; use it for the listing sweep

    if home_alive_base is None:
        best["bucket"] = "hard_wall"
        errs = [s.get("error") for s in swept if s.get("error")]
        best["evidence"] = ("resolves (DNS) but home page un-navigable on all host "
                            f"variants under stealth: {errs[:2]}")
        best["swept"] = swept
        return best

    # --- Phase 2: sweep listing paths on the live base, within the time budget.
    for path in _LISTING_PATHS:
        if time.monotonic() - started > _DOMAIN_BUDGET_S:
            swept.append({"path": path, "skipped": "domain budget exceeded"})
            break
        sig = _render(browser, home_alive_base + path, _SETTLE_MS, cookie_state)
        if "error" in sig:
            swept.append({"path": path, "error": sig["error"]})
            continue
        if consider(path, home_alive_base, sig):
            best["evidence"] = (f"stealth render of {path} -> prices={best['prices']} "
                                f"dlinks={best['dlinks']} status={best['status']} "
                                "(status-blind body gate)")
            best["swept"] = swept
            return best

    # --- Not recovered: classify the residual.
    any_body = any((s.get("bytes") or 0) >= _MIN_BYTES for s in swept)
    if home_wall or any(s.get("wall") for s in swept):
        best["bucket"] = "hard_wall"
        best["evidence"] = "resolves; persistent challenge/interstitial under stealth"
    elif not any_body:
        best["bucket"] = "hard_wall"
        best["evidence"] = "resolves; every rendered body sub-gate (server error/empty)"
    else:
        best["bucket"] = "no_listing"
        best["evidence"] = ("home page renders under stealth, but no own-site car-"
                            "listing signal found on home + canonical listing paths")
    best["swept"] = swept
    return best


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    targets = json.load(open("scratch/_unreachable_all86.json", encoding="utf-8"))
    out = "docs/_unreachable_stealth_result.json"
    # Resume: keep prior results for domains already processed, only probe the rest.
    prior = {}
    import os as _os
    if _os.path.exists(out):
        try:
            prior = {r["domain"]: r for r in json.load(open(out, encoding="utf-8"))}
        except Exception:
            prior = {}
    todo = [t for t in targets if t["domain"] not in prior]
    if prior:
        print(f"RESUME: {len(prior)} already done, {len(todo)} remaining", flush=True)

    # Pre-pass: DNS triage (cheap, no browser) so we only boot camoufox for resolvers.
    resolvable, dns_dead = [], []
    for t in todo:
        if _dns_resolves(t["domain"]) is None:
            dns_dead.append(t)
        else:
            resolvable.append(t)
    print(f"DNS triage: {len(resolvable)} resolve, {len(dns_dead)} NXDOMAIN "
          f"(of {len(todo)} remaining)", flush=True)

    results = list(prior.values())

    def _flush() -> None:
        json.dump(results, open(out, "w", encoding="utf-8"), indent=1,
                  ensure_ascii=False)

    for t in dns_dead:
        results.append({"domain": t["domain"], "name": t.get("name"),
                        "prior_error": t.get("error"), "bucket": "dns_dead",
                        "evidence": "NXDOMAIN on www. and bare host"})
        print(f"  [dns_dead   ] {t['domain']:34s} prior={t.get('error')}", flush=True)
    _flush()

    if resolvable:
        with Camoufox(headless=True, humanize=True, locale="es-ES",
                      os=("windows",)) as browser:
            for t in resolvable:
                r = probe_domain(browser, t["domain"], t.get("website") or "")
                r["name"] = t.get("name")
                r["prior_error"] = t.get("error")
                results.append(r)
                _flush()  # persist after every domain (crash-resumable)
                print(f"  [{r['bucket']:11s}] {t['domain']:34s} "
                      f"prior={str(t.get('error')):8s} path={r.get('best_path')} "
                      f"status={r.get('status')} bytes={r.get('bytes')} "
                      f"prices={r.get('prices')} dlinks={r.get('dlinks')} "
                      f"wall={r.get('wall')}", flush=True)

    _flush()
    from collections import Counter
    c = Counter(r["bucket"] for r in results)
    print(f"\nSTEALTH RE-VERIFY ({len(results)} domains): {dict(c)}", flush=True)
    rec = [r for r in results if r["bucket"] == "recovered"]
    print(f"  RECOVERED-FREE: {len(rec)}", flush=True)
    for r in rec:
        print(f"    {r['domain']:32s} {r['best_path']:26s} "
              f"prices={r['prices']} dlinks={r['dlinks']} status={r['status']}",
              flush=True)
    print(f"  -> {out}", flush=True)


if __name__ == "__main__":
    main()
