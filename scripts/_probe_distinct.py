"""Measure the REAL accessible ceiling of national relevance pagination: drain many
pages, count DISTINCT ids. If distinct plateaus far below 272k, that's the cap."""
from curl_cffi import requests as r
import json
import time

H = {
    "Content-Type": "application/json", "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.coches.net", "Referer": "https://www.coches.net/",
    "X-Schibsted-Tenant": "coches", "X-Adevinta-Channel": "web-desktop",
}
URL = "https://web.gw.coches.net/search"


def search(page, size, term="relevance"):
    body = {"pagination": {"page": page, "size": size},
            "sort": {"term": term, "order": "desc"}, "filters": {"categoryId": 2500}}
    for _ in range(3):
        try:
            resp = r.post(URL, json=body, headers=H, impersonate="chrome131", timeout=60)
            if resp.status_code == 200:
                return json.loads(resp.content.decode("utf-8"))
            time.sleep(1)
        except Exception:
            time.sleep(1)
    return None


distinct = set()
SIZE = 100
last_total = None
maxpage = 2800
t0 = time.time()
for page in range(1, maxpage + 1):
    d = search(page, SIZE)
    if d is None:
        print(f"page {page}: fetch failed, stop")
        break
    items = d.get("items", [])
    last_total = d.get("meta", {}).get("totalResults")
    if not items:
        print(f"page {page}: empty, stop")
        break
    for it in items:
        distinct.add(str(it.get("id")))
    if page % 100 == 0:
        el = time.time() - t0
        print(f"page {page:5d}: distinct={len(distinct):6d} declared={last_total} "
              f"({page*SIZE} fetched, {el:.0f}s, {len(distinct)/el*60:.0f} dc/min)")

print(f"\nFINAL national relevance drain: distinct={len(distinct)} declared={last_total}")
print(f"accessible fraction = {len(distinct)/last_total*100:.1f}%")
