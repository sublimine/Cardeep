"""Probe v2: find ADS_LIST_SEARCH usage, base URL assembly, and whether filters
go as query params or a transformed body."""
from curl_cffi import requests as r
import re

JS_URL = "https://s.ccdn.es/main.e06139af.js"
resp = r.get(JS_URL, impersonate="chrome131", timeout=60)
js = resp.text
print("bundle len", len(js))

# API base assembly
for kw in ["API_SUBDOMAIN", "API_DOMAIN", "gw.coches", "ADS_LIST_SEARCH"]:
    for mo in re.finditer(re.escape(kw), js):
        s = max(0, mo.start() - 80)
        e = min(len(js), mo.start() + 160)
        print(f"=== {kw} ===")
        print(js[s:e].replace("\n", " "))
        break  # first occurrence per keyword

# Find where ADS_LIST_SEARCH is consumed to build a request (look for the var that holds wC)
print("\n#### consumers of *_LIST_SEARCH ####")
for mo in re.finditer(r"ADS_LIST_SEARCH", js):
    s = max(0, mo.start() - 40)
    e = min(len(js), mo.start() + 200)
    print(js[s:e].replace("\n", " "))
    print("--")
