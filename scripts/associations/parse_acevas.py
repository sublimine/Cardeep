"""Parse ACEVAS (VW/Audi/Skoda dealers) Super Store Finder XML into JSON."""
from __future__ import annotations

import html as _html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "docs", "research", "associations", "acevas_raw.xml")
OUT = os.path.join(ROOT, "docs", "research", "associations", "acevas_members.json")


def tag(block, name):
    m = re.search(rf"<{name}>(.*?)</{name}>", block, re.DOTALL)
    if not m:
        return None
    v = _html.unescape(m.group(1)).replace("&#44;", ",").strip()
    return v or None


def main():
    t = open(RAW, encoding="utf-8").read()
    items = re.findall(r"<item>(.*?)</item>", t, re.DOTALL)
    out = []
    brand_tags = ["Skoda", "Volkswagen", "Audi", "VW_Industriales", "SEAT", "Cupra"]
    for it in items:
        name = tag(it, "location")
        if not name:
            continue
        brands = []
        for b in brand_tags:
            if re.search(rf"<{b}>true</{b}>", it):
                brands.append(b)
        out.append({
            "name": name,
            "address_raw": tag(it, "address"),
            "zip": tag(it, "zip"),
            "province": tag(it, "state"),
            "lat": tag(it, "latitude"),
            "lon": tag(it, "longitude"),
            "phone": tag(it, "telephone"),
            "email": tag(it, "email"),
            "website": tag(it, "website") or tag(it, "exturl"),
            "brands": brands,
        })
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"WROTE {OUT}: {len(out)} dealers")
    ws = sum(1 for d in out if d.get("website"))
    addr = sum(1 for d in out if d.get("address_raw"))
    print(f"  with website: {ws} | with address: {addr}")
    for d in out[:5]:
        print(" ", {k: d[k] for k in ("name", "province", "zip", "website")})


if __name__ == "__main__":
    main()
