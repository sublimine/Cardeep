"""Pilot verification of the Tier-1 anti-detection engine on REAL entities.

Recipe-first: tiny samples, nothing persisted. Reports per target: final status,
which tier resolved it, the fingerprint used, and the block-detector verdict.

Usage:
    python -m scripts.pilot_tier1                 # Tier-0 open targets only (cost-zero, no browser)
    python -m scripts.pilot_tier1 --tier1         # also exercise the real-browser Tier-1 path
    python -m scripts.pilot_tier1 --engine camoufox --tier1   # MPL-2.0 engine (avoid AGPL nodriver)

No proxy is used (PENDING-CREDENTIAL). Tier-1 solves on the host IP.
"""
from __future__ import annotations

import argparse
import sys

from pipeline.engine.fetch import FetchEngine, FetchError

# Open Tier-0 targets (no active challenge expected) — verified-open marketplaces.
OPEN_TARGETS = [
    "https://www.autocasion.com/",
    "https://www.coches.com/",
]
# A target commonly behind Cloudflare/DataDome — only hit when --tier1 is passed.
WALLED_TARGETS = [
    "https://www.coches.net/",
]


def _report(label: str, eng: FetchEngine, html: str | None, err: str | None) -> None:
    n = len(html) if html else 0
    print(f"  [{label}]")
    print(f"     fingerprint : {eng.impersonate}")
    print(f"     last_status : {eng.last_status}")
    print(f"     last_tier   : {eng.last_tier}")
    print(f"     verdict     : {eng.last_verdict.value if eng.last_verdict else '-'}")
    print(f"     fetch_count : {eng.fetch_count}")
    print(f"     body_bytes  : {n}")
    if err:
        print(f"     ERROR       : {err}")
    elif html:
        snippet = " ".join(html.split())[:90]
        print(f"     sample      : {snippet!r}")
    print()


def run_tier0() -> None:
    print("== Tier-0 (curl_cffi, rotating coherent fingerprint, cost-zero) ==\n")
    for url in OPEN_TARGETS:
        eng = FetchEngine()  # rotation: one coherent fingerprint per session
        html = err = None
        try:
            html = eng.fetch_text(url)
        except FetchError as e:
            err = str(e)
        _report(url, eng, html, err)


def run_tier1(engine: str | None) -> None:
    # None -> full multi-engine chain (nodriver -> camoufox): the go-around posture.
    chain = (engine,) if engine else ("nodriver", "camoufox")
    print(f"== Tier-1 (real-browser chain={list(chain)}, cookie-reuse, host IP / no proxy) ==\n")
    for url in WALLED_TARGETS:
        eng = FetchEngine(allow_tier1_escalation=True, tier1_engines=chain)
        html = err = None
        try:
            html = eng.fetch_text(url, tier=1)  # forces browser-assisted path
        except FetchError as e:
            err = str(e)
        _report(url, eng, html, err)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier1", action="store_true",
                    help="exercise the real-browser Tier-1 path (downloads a browser if absent)")
    ap.add_argument("--engine", default=None, choices=["nodriver", "camoufox"],
                    help="pin a single Tier-1 engine; omit for the full chain")
    args = ap.parse_args()

    run_tier0()
    if args.tier1:
        if args.engine in (None, "nodriver"):
            print("NOTE: nodriver is AGPL-3.0 (network copyleft) -- see README_TIER1.md.\n")
        run_tier1(args.engine)
    return 0


if __name__ == "__main__":
    sys.exit(main())
