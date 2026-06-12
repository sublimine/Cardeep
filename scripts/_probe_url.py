"""Probe: reconstruct the exact request URL + headers the SPA uses for listing search.
Find the http client base config and the 'X-Adevinta'/version headers."""
from curl_cffi import requests as r
import re

js = r.get("https://s.ccdn.es/main.e06139af.js", impersonate="chrome131", timeout=60).text

# Find REQUEST_HEADERS / version constants
for kw in ["X-Adevinta", "X-Schibsted", "x-adevinta", "apiVersion", "API_VERSION",
           "REQUEST_HEADERS", "X-Coches", "application/vnd"]:
    hits = [m.start() for m in re.finditer(re.escape(kw), js)]
    if hits:
        m = hits[0]
        print(f"=== {kw} ({len(hits)} hits) ===")
        print(js[m-60:m+160].replace("\n", " "))

# The full base url: look for "https://".concat or template with API_SUBDOMAIN
print("\n#### base url assembly ####")
for mo in re.finditer(r'API_SUBDOMAIN', js):
    seg = js[mo.start()-200:mo.start()+50]
    if "concat" in seg or "https" in seg or "${" in seg or "+" in seg:
        print(seg.replace("\n", " "))
        print("--")

# look for how the search request path is composed in the use-case
for mo in re.finditer(r'search_use_case|get_ads_list|adsListSearch|searchAds|ADS_LIST', js):
    pass

# Print the bytes around the only "/search/" literal AND its variable assignment,
# then find who reads that variable to build a url.
idx = js.find('ADS_LIST_SEARCH:"/search/"')
print("\nADS_LIST_SEARCH literal idx:", idx)
if idx > 0:
    print(js[idx-100:idx+300].replace("\n", " "))
