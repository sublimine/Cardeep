"""Discover a large AutoScout24 dealer set by crawling /lst across multiple sort
orders (diversity), and persist the distinct slugs to data/as24_dealers.json so
parallel harvest workers can each take a slice.

Usage: python -m scripts.as24_discover_dealers [pages_per_sort]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from pipeline.sources.autoscout24 import collect_dealer_slugs

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "as24_dealers.json"
SORTS = ["age", "price", "mileage", "year", "power"]  # different orders surface different dealers


def main(pages: int) -> None:
    all_dealers: dict[str, dict] = {}
    for sort in SORTS:
        d = collect_dealer_slugs(max_pages=pages, sort=sort)
        before = len(all_dealers)
        all_dealers.update({k: v for k, v in d.items() if k not in all_dealers})
        print(f"sort={sort}: +{len(all_dealers) - before} new (total {len(all_dealers)})")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(all_dealers, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {len(all_dealers)} distinct dealers -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 20)
