"""coches.net free-vector harvester — POST web.gw.coches.net/search via curl_cffi.

No proxy, no browser. Public-data market research over public listings.
"""
import json
import sys
from curl_cffi import requests

ENDPOINT = "https://web.gw.coches.net/search"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.coches.net",
    "Referer": "https://www.coches.net/segunda-mano/",
    "X-Schibsted-Tenant": "coches",
}


def build_payload(page=1, size=30):
    # categoryId 2500 = cars (turismos). Pagination is a NESTED object;
    # a top-level "page" int is silently ignored by the gateway.
    return {
        "categoryId": 2500,
        "sortBy": "relevance",
        "sortOrder": "DESC",
        "pagination": {"page": page, "size": size},
        "price": {"from": None, "to": None},
        "year": {"from": None, "to": None},
        "km": {"from": None, "to": None},
    }


def harvest(page=1, size=30):
    r = requests.post(ENDPOINT, json=build_payload(page, size), headers=HEADERS,
                      impersonate="chrome131", timeout=40)
    print("status:", r.status_code, "ct:", r.headers.get("content-type"))
    r.raise_for_status()
    d = r.json()
    meta = d.get("meta", {})
    print("totalResults:", meta.get("totalResults"), "totalPages:", meta.get("totalPages"),
          "items:", len(d.get("items", [])))
    return d


if __name__ == "__main__":
    page = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    d = harvest(page)
    json.dump(d, open(f"data/coches_net_page{page}.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    # print 3 real cars with dealer attribution
    for it in d["items"][:3]:
        s = it.get("seller") or {}
        print(f"  {it['make']} {it['model']} | {it['price']} EUR | "
              f"prof={it.get('isProfessional')} | dealer={s.get('name')} "
              f"(contract {s.get('contractId')}, {(it.get('location') or {}).get('mainProvince')})")
