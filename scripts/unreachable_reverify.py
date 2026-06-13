"""Adversarial re-verification of the 'unreachable' long-tail family.

The prior probe (scripts/longtail_fingerprint.py) marked 92 domains 'unreachable'
on a FIRST-pass GET with a bare TLS fingerprint and no browser-coherent headers.
A 403 / 202 / 503 / Timeout under those conditions is NOT proof a site is offline —
it is proof the FIRST probe was bot-walled. Doctrine: verify the verdict before
trusting it.

This re-verifies the NON-DNS cohort (40 domains) with the SAME engine the real
harvester uses, but with the headers a real Chrome actually sends (Referer,
Accept-Language, Sec-Fetch-*, Upgrade-Insecure-Requests) and a single polite retry
for challenge codes. A domain that now returns 200 with real HTML is reachable —
the 'unreachable' label was a probe defect, and the dealer is harvestable.

Output: docs/_unreachable_reverify_result.json — per-domain {status, reachable,
bytes, title, inventory_hint}. Read-only public-data market research.
"""
from __future__ import annotations

import json
import re
import sys
import time

from curl_cffi import requests as cffi_requests

_IMPERSONATE = "chrome131"
_TIMEOUT = 25

# Browser-coherent headers — the half the first probe omitted. A real Chrome sends
# these on a top-level navigation; many WAFs gate precisely on their absence.
_BROWSER_HEADERS = {
    "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
               "image/avif,image/webp,image/apng,*/*;q=0.8"),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

# A cheap "does this page look like it lists cars" sniff (NOT a parser — just signal
# for which recovered domains are worth a real harvest recipe).
_INV_HINTS = ("/coches", "segunda-mano", "ocasion", "ocasión", "vehiculos",
              "vehículos", "km0", "seminuevos", "stock", "concesionario",
              "catalogo", "catálogo")
_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)


def _url_variants(website: str, domain: str) -> list[str]:
    """Try the recorded URL first, then https/http with and without www — a domain
    can be alive on a variant the first probe did not try."""
    seen, out = set(), []
    cands = [website]
    bare = re.sub(r"^www\.", "", domain.lower())
    for scheme in ("https", "http"):
        for host in (f"www.{bare}", bare):
            cands.append(f"{scheme}://{host}/")
    for u in cands:
        if u and u not in seen and u.startswith(("http://", "https://")):
            seen.add(u)
            out.append(u)
    return out


def probe(session, url: str) -> dict:
    """One GET with browser headers; one polite retry on a challenge code."""
    last = {"status": None, "error": None}
    for attempt in (1, 2):
        try:
            resp = session.get(url, headers=_BROWSER_HEADERS,
                               impersonate=_IMPERSONATE, timeout=_TIMEOUT,
                               allow_redirects=True)
            status = resp.status_code
            body = resp.text or ""
            last = {"status": status, "bytes": len(body), "error": None,
                    "final_url": str(resp.url)}
            if status == 200 and len(body) > 1500:
                low = body.lower()
                tm = _TITLE_RE.search(body)
                last["title"] = (tm.group(1).strip()[:120] if tm else None)
                last["inventory_hint"] = any(h in low for h in _INV_HINTS)
                last["reachable"] = True
                return last
            # challenge / queue codes — wait briefly and retry once.
            if status in (202, 429, 503) and attempt == 1:
                time.sleep(2.5)
                continue
            last["reachable"] = False
            return last
        except Exception as e:  # noqa: BLE001 — record, do not crash the sweep
            last = {"status": None, "error": f"{type(e).__name__}: {e}",
                    "reachable": False}
            if attempt == 1:
                time.sleep(1.5)
                continue
    return last


def main() -> None:
    targets = json.load(open("docs/_unreachable_reverify_targets.json",
                              encoding="utf-8"))
    session = cffi_requests.Session(impersonate=_IMPERSONATE)
    results = []
    recovered = 0
    for t in targets:
        domain, website = t["domain"], t["website"]
        rec = {"domain": domain, "name": t["name"],
               "prior_error": t["prior_error"], "website": website}
        best = None
        for url in _url_variants(website, domain):
            r = probe(session, url)
            if best is None or (r.get("reachable") and not best.get("reachable")):
                best = {**r, "url": url}
            if r.get("reachable"):
                best = {**r, "url": url}
                break
        rec.update(best or {})
        if rec.get("reachable"):
            recovered += 1
        results.append(rec)
        flag = "RECOVERED" if rec.get("reachable") else "still-walled"
        print(f"  [{flag:12s}] {domain:32s} prior={t['prior_error']:8s} "
              f"now={rec.get('status')} bytes={rec.get('bytes')} "
              f"inv={rec.get('inventory_hint')} title={rec.get('title')}")
    json.dump(results, open("docs/_unreachable_reverify_result.json", "w",
                            encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"\nRE-VERIFY: {recovered}/{len(targets)} formerly-'unreachable' domains "
          f"are LIVE with browser-coherent headers.")
    inv = [r for r in results if r.get("reachable") and r.get("inventory_hint")]
    print(f"  of those, {len(inv)} show an inventory hint on the home page.")


if __name__ == "__main__":
    main()
