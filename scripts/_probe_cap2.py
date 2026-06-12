"""Find the exact pagination cap: drain province 30 (declared ~9231, presumably under
the cap) fully and count distinct ids — does distinct reach the declared total?
Also probe Madrid (56k) page-by-page to find where distinct plateaus = the cap."""
from curl_cffi import requests as r
import json
import time

H = {
    "Content-Type": "application/json", "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.coches.net", "Referer": "https://www.coches.net/",
    "X-Schibsted-Tenant": "coches", "X-Adevinta-Channel": "web-desktop",
}
URL = "https://web.gw.coches.net/search"


def search(filters, page, size, term="relevance", order="desc"):
    body = {"pagination": {"page": page, "size": size},
            "sort": {"term": term, "order": order}, "filters": filters}
    for _ in range(3):
        try:
            resp = r.post(URL, json=body, headers=H, impersonate="chrome131", timeout=60)
            if resp.status_code == 200:
                return json.loads(resp.content.decode("utf-8"))
            time.sleep(0.6)
        except Exception:
            time.sleep(0.6)
    return None


def drain(filters, label, size=100, hardstop=700):
    distinct = set()
    declared = None
    page = 1
    while page <= hardstop:
        d = search(filters, page, size)
        if d is None:
            print(f"  [{label}] page {page}: fail, stop")
            break
        items = d.get("items", [])
        declared = d.get("meta", {}).get("totalResults")
        if not items:
            print(f"  [{label}] page {page}: empty, stop")
            break
        before = len(distinct)
        for it in items:
            distinct.add(str(it.get("id")))
        added = len(distinct) - before
        if page % 20 == 0 or added == 0:
            print(f"  [{label}] page {page:4d}: distinct={len(distinct):6d} declared={declared} (+{added})")
        if added == 0 and page > 2:
            print(f"  [{label}] page {page}: 0 new ids (plateau) -> CAP reached at distinct={len(distinct)}")
            break
        page += 1
    print(f"  [{label}] DONE distinct={len(distinct)} declared={declared} "
          f"frac={len(distinct)/declared*100:.1f}% pages={page}")
    return len(distinct), declared


print("=== province 30 (declared ~9231) full drain ===")
drain({"categoryId": 2500, "provinceIds": [30]}, "prov30")

print("\n=== Madrid prov28 (declared ~56k) drain until plateau ===")
drain({"categoryId": 2500, "provinceIds": [28]}, "prov28", hardstop=700)
