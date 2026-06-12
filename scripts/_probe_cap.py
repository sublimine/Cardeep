"""Prove the relevance pagination cap and enumerate per-province totals.
(1) National relevance: how deep can we page before items dry up / repeat?
(2) Sum of per-province totalResults vs 272k (coverage by independent path)."""
from curl_cffi import requests as r
import json

H = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.coches.net",
    "Referer": "https://www.coches.net/",
    "X-Schibsted-Tenant": "coches",
    "X-Adevinta-Channel": "web-desktop",
}
URL = "https://web.gw.coches.net/search"


def search(filters, page, size, sort=("relevance", "desc")):
    body = {
        "pagination": {"page": page, "size": size},
        "sort": {"term": sort[0], "order": sort[1]},
        "filters": filters,
    }
    resp = r.post(URL, json=body, headers=H, impersonate="chrome131", timeout=60)
    if resp.status_code != 200:
        return None, f"HTTP{resp.status_code} {resp.text[:80]}"
    d = json.loads(resp.content.decode("utf-8"))
    return d, None


# (1) PROVE THE CAP: national relevance, walk deep pages, watch item count + id drift.
print("=== national relevance deep-page probe (size=100) ===")
cat = {"categoryId": 2500}
seen_first_ids = {}
prev_ids = None
for page in [1, 10, 50, 100, 150, 200, 300, 500, 1000, 1550, 1600, 2000, 2700]:
    d, err = search(cat, page, 100)
    if err:
        print(f"page {page:5d}: {err}")
        continue
    items = d.get("items", [])
    ids = [str(it.get("id")) for it in items]
    total = d.get("meta", {}).get("totalResults")
    firstid = ids[0] if ids else None
    dup = (firstid in seen_first_ids)
    seen_first_ids.setdefault(firstid, page)
    print(f"page {page:5d}: items={len(items):3d} total={total} first_id={firstid} "
          f"{'<-REPEAT of page '+str(seen_first_ids[firstid]) if dup else ''}")
