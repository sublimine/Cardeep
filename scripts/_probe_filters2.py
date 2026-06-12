"""Probe the REAL payload shape: {pagination, sort:{order,term}, filters:{...}}.
Discover the filter keys for category, province, price band. Watch totalResults move."""
from curl_cffi import requests as r
import json

H = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.coches.net",
    "Referer": "https://www.coches.net/",
    "X-Schibsted-Tenant": "coches",
    "X-Adevinta-Channel": "web-desktop",
    "X-Adevinta-Page-Url": "https://www.coches.net/madrid/segunda-mano/",
    "X-Adevinta-Referer": "https://www.coches.net/madrid/segunda-mano/",
}
URL = "https://web.gw.coches.net/search"


def hit(filters, sort=None):
    body = {
        "pagination": {"page": 1, "size": 1},
        "sort": sort or {"order": "desc", "term": "relevance"},
        "filters": filters,
    }
    resp = r.post(URL, json=body, headers=H, impersonate="chrome131", timeout=40)
    if resp.status_code != 200:
        return f"HTTP{resp.status_code} {resp.text[:80]}"
    d = json.loads(resp.content.decode("utf-8"))
    m = d.get("meta", {})
    return m.get("totalResults")


# The captured real call:
print("captured {offerTypeIds:[10]}        :", hit({"offerTypeIds": [10]}))
print("empty filters {}                    :", hit({}))
print("categoryId only                     :", hit({"categoryId": 2500}))
print("+ provinceIds[28]                   :", hit({"categoryId": 2500, "provinceIds": [28]}))
print("+ provinceId 28 scalar              :", hit({"categoryId": 2500, "provinceId": 28}))
print("+ provinces[28]                     :", hit({"categoryId": 2500, "provinces": [28]}))
print("+ location.provinceIds[28]          :", hit({"categoryId": 2500, "location": {"provinceIds": [28]}}))
print("+ price{from,to} 0-1500             :", hit({"categoryId": 2500, "price": {"from": 0, "to": 1500}}))
print("+ priceRange 0-1500                 :", hit({"categoryId": 2500, "priceRange": {"from": 0, "to": 1500}}))
print("offerTypeIds[10]+cat+prov28         :", hit({"offerTypeIds": [10], "categoryId": 2500, "provinceIds": [28]}))
