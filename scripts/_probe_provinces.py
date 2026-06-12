"""Enumerate per-province totalResults (provinceIds 1..52). Prove each is under the
relevance cap, and sum them as an independent coverage check vs the national 272k."""
from curl_cffi import requests as r
import json
import time

H = {
    "Content-Type": "application/json", "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.coches.net", "Referer": "https://www.coches.net/",
    "X-Schibsted-Tenant": "coches", "X-Adevinta-Channel": "web-desktop",
}
URL = "https://web.gw.coches.net/search"


def total(filters):
    body = {"pagination": {"page": 1, "size": 1},
            "sort": {"term": "relevance", "order": "desc"}, "filters": filters}
    for _ in range(3):
        try:
            resp = r.post(URL, json=body, headers=H, impersonate="chrome131", timeout=40)
            if resp.status_code == 200:
                return json.loads(resp.content.decode("utf-8")).get("meta", {}).get("totalResults")
            time.sleep(0.5)
        except Exception:
            time.sleep(0.5)
    return None


nat = total({"categoryId": 2500})
print("national categoryId=2500:", nat)

rows = []
ssum = 0
for p in range(1, 53):
    t = total({"categoryId": 2500, "provinceIds": [p]})
    rows.append((p, t))
    if isinstance(t, int):
        ssum += t

over = [(p, t) for p, t in rows if isinstance(t, int) and t > 10000]
print("\nper-province totals:")
for p, t in rows:
    flag = "  <-- OVER 10k (may need sub-partition)" if isinstance(t, int) and t > 10000 else ""
    print(f"  prov {p:2d}: {t}{flag}")
print(f"\nSUM of 52 provinces = {ssum}")
print(f"national declared   = {nat}")
print(f"sum/national        = {ssum/nat*100:.1f}%  (provinces with multi-province ads double-count)")
print(f"provinces over 10k  = {len(over)}: {[p for p,_ in over]}")
print(f"max single province = {max((t for _,t in rows if isinstance(t,int)))}")
