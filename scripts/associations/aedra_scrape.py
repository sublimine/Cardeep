"""Scrape the AEDRA member directory (desguaces/CATs) to JSON.

List pages: name, province, phone, detail slug.
Detail pages: Google-Maps-embedded full address (street, postcode, municipality,
province) + external website if present.

Output: docs/research/associations/aedra_members.json
"""
from __future__ import annotations

import json
import os
import re
import sys
import time

from curl_cffi import requests as creq

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "docs", "research", "associations", "aedra_members.json")
H = {"Accept-Language": "es-ES,es;q=0.9"}
BASE = "https://aedra.org"


def get(url, tries=3):
    last = None
    for i in range(tries):
        try:
            r = creq.get(url, impersonate="chrome131", headers=H, timeout=45)
            if r.status_code == 200:
                return r.text
            last = f"HTTP {r.status_code}"
        except Exception as e:  # noqa: BLE001
            last = str(e)
        time.sleep(1.5 * (i + 1))
    print(f"  FAIL {url}: {last}", file=sys.stderr)
    return None


CARD_RE = re.compile(
    r'<h2 class="directorist-listing-title"><a href="https://aedra\.org/asociados/([a-z0-9-]+)/">([^<]+)</a></h2>.*?'
    r'(?:page_id=283[^"]*?/([a-z0-9-]+)/&directory_type|</ul>)',
    re.DOTALL,
)
TITLE_RE = re.compile(r'<h2 class="directorist-listing-title"><a href="https://aedra\.org/asociados/([a-z0-9-]+)/">([^<]+)</a></h2>')
PROV_RE = re.compile(r'page_id=283%2F([a-z0-9-]+)%2F&directory_type')
TEL_RE = re.compile(r'href="tel:(\d+)"')
MAPS_RE = re.compile(r'google\.com/maps/search/([^"\'<>]+)')
EXT_RE = re.compile(r'href="(https?://(?!aedra\.org)(?!www\.google)(?!maps\.google)[^"]+)"')


def parse_list(html: str):
    """Split list page into per-article blocks, extract name/slug/province/phone."""
    arts = re.split(r'<article class="directorist-listing-single', html)
    out = []
    for a in arts[1:]:
        t = TITLE_RE.search(a)
        if not t:
            continue
        slug, name = t.group(1), t.group(2).strip()
        prov_m = PROV_RE.search(a)
        tel_m = TEL_RE.search(a)
        out.append({
            "slug": slug,
            "name": name,
            "province_slug": prov_m.group(1) if prov_m else None,
            "phone": tel_m.group(1) if tel_m else None,
        })
    return out


def parse_detail(html: str):
    addr = None
    website = None
    m = MAPS_RE.search(html)
    if m:
        from urllib.parse import unquote
        addr = unquote(m.group(1)).replace("+", " ").strip()
    # external website: prefer one that is not social/maps
    for u in EXT_RE.findall(html):
        low = u.lower()
        if any(s in low for s in ("facebook.", "instagram.", "twitter.", "x.com",
                                  "linkedin.", "youtube.", "wa.me", "whatsapp",
                                  "addtoany", "wordpress.org", "gravatar")):
            continue
        website = u
        break
    return addr, website


def main():
    members = []
    page = 1
    seen_slugs = set()
    while page <= 60:
        url = BASE + "/buscador-de-socios/" if page == 1 else f"{BASE}/buscador-de-socios/page/{page}/"
        html = get(url)
        if not html:
            break
        rows = parse_list(html)
        if not rows:
            print(f"page {page}: 0 rows -> stop")
            break
        new = [r for r in rows if r["slug"] not in seen_slugs]
        for r in new:
            seen_slugs.add(r["slug"])
        members.extend(new)
        print(f"page {page}: {len(rows)} rows ({len(new)} new), total {len(members)}")
        if not new:
            break
        page += 1
        time.sleep(0.6)

    print(f"Collected {len(members)} list rows. Fetching details...")
    for i, m in enumerate(members):
        d = get(f"{BASE}/asociados/{m['slug']}/")
        if d:
            addr, website = parse_detail(d)
            m["address_raw"] = addr
            m["website"] = website
        if (i + 1) % 25 == 0:
            print(f"  details {i+1}/{len(members)}")
            with open(OUT, "w", encoding="utf-8") as f:
                json.dump(members, f, ensure_ascii=False, indent=1)
        time.sleep(0.4)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(members, f, ensure_ascii=False, indent=1)
    print(f"WROTE {OUT} ({len(members)} members)")
    with_site = sum(1 for m in members if m.get("website"))
    with_addr = sum(1 for m in members if m.get("address_raw"))
    print(f"  with website: {with_site} | with address: {with_addr}")


if __name__ == "__main__":
    main()
