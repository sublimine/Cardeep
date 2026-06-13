"""Probe generic/custom long-tail dealer own-sites for a parseable listing surface.

Read-only market research. For each candidate domain we:
  1. fetch the home page (curl_cffi chrome131),
  2. try a ranked list of inventory listing slugs,
  3. on the first slug that returns 200, sniff for price tokens / vehicle anchors
     and count likely vehicle-card occurrences,
so we can pick 3-5 REAL dealers whose bespoke HTML actually yields inventory and
hand-author a per-dealer card recipe for each (the generic/custom family has NO
shared template — each needs its own selector).
"""
from __future__ import annotations

import json
import re
import sys

from curl_cffi import requests as cffi_requests

IMPERSONATE = "chrome131"
TIMEOUT = 30

# Ranked inventory-listing slugs verified across the WordPress family doc, reused
# here as a discovery probe for bespoke sites (they converge on the same slugs).
SLUGS = [
    "/coches", "/vehiculos", "/coches-ocasion", "/vehiculos-ocasion",
    "/ocasion", "/stock", "/catalogo", "/seminuevos", "/km0",
    "/coches-segunda-mano", "/nuestro-stock", "/nuestrostock", "/vehiculos-de-ocasion",
    "/inventario", "/coches/", "/vehiculos/", "/listado", "/turismos",
    "/coches-de-ocasion", "/vo", "/vn", "/segunda-mano",
]

PRICE_RE = re.compile(r"\d[\d.\s]{2,}\s*(?:€|&euro;|EUR)", re.I)
EURO_NUM_RE = re.compile(r"(\d{1,3}(?:[.\s]\d{3})+)\s*(?:€|&euro;)")
# generic "looks like a car card / detail link" sniffers
DETAIL_HINT = re.compile(
    r"(coche|vehiculo|ficha|detalle|/vo/|/vn/|stock|ocasion)", re.I)


def fetch(sess, url):
    try:
        r = sess.get(url, impersonate=IMPERSONATE, timeout=TIMEOUT, allow_redirects=True)
        return r.status_code, r.text, str(r.url)
    except Exception as e:
        return None, f"ERR {type(e).__name__}: {e}", url


def sniff(html):
    prices = PRICE_RE.findall(html)
    euro_nums = EURO_NUM_RE.findall(html)
    # count anchors that look like detail links
    anchors = re.findall(r'href=["\']([^"\']+)["\']', html)
    detail_anchors = [a for a in anchors if DETAIL_HINT.search(a)]
    return {
        "html_len": len(html),
        "price_tokens": len(prices),
        "euro_thousands": len(euro_nums),
        "detail_anchor_hits": len(detail_anchors),
        "sample_prices": prices[:5],
        "sample_detail_anchors": detail_anchors[:6],
    }


def probe(domain):
    sess = cffi_requests.Session(impersonate=IMPERSONATE)
    out = {"domain": domain, "home": None, "listings": []}
    for base in (f"https://www.{domain}", f"https://{domain}"):
        st, html, final = fetch(sess, base)
        if st == 200:
            out["home"] = {"url": final, "status": st, **sniff(html)}
            base_final = re.sub(r"/$", "", final)
            break
    else:
        out["error"] = "home unreachable"
        return out

    root = re.match(r"(https?://[^/]+)", out["home"]["url"]).group(1)
    for slug in SLUGS:
        st, html, final = fetch(sess, root + slug)
        if st == 200 and len(html) > 4000:
            s = sniff(html)
            # only keep slugs that actually look like a listing (>=3 price tokens)
            if s["price_tokens"] >= 3 or s["euro_thousands"] >= 3:
                out["listings"].append({"slug": slug, "final": final, "status": st, **s})
    return out


def main():
    domains = sys.argv[1:]
    results = []
    for d in domains:
        print(f"[probe] {d} ...", file=sys.stderr)
        r = probe(d)
        results.append(r)
        nl = len(r.get("listings", []))
        best = max((x["price_tokens"] for x in r.get("listings", [])), default=0)
        print(f"    home={'ok' if r.get('home') else r.get('error')} "
              f"listing_slugs={nl} best_price_tokens={best}", file=sys.stderr)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
