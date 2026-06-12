"""Probe: enumerate every API path literal in the bundle that could be the search
endpoint, plus the service module that posts the search payload."""
from curl_cffi import requests as r
import re

js = r.get("https://s.ccdn.es/main.e06139af.js", impersonate="chrome131", timeout=60).text

# All path-like string literals containing 'search' (case-insensitive).
paths = set(re.findall(r'"/[A-Za-z0-9_/\-]*[Ss]earch[A-Za-z0-9_/\-]*"', js))
print("search path literals:")
for p in sorted(paths):
    print("  ", p)

# Look for a version segment near gw.coches usage or near the search service.
# Find the search service: a function building "...search" URL with method POST.
print("\n#### endpoint builder contexts (concat with search path) ####")
# common minified pattern: someBase.concat("/search") or `${base}/search`
for mo in re.finditer(r'concat\("/search', js):
    print(js[mo.start()-160:mo.start()+60].replace("\n", " "))
    print("--")
for mo in re.finditer(r'/search/v\d', js):
    print("VERSIONED:", js[mo.start()-40:mo.start()+40])

# Search for the wholesale 'ms-search' or 'mt-search' service host
hosts = set(re.findall(r'[a-z0-9.\-]+\.coches\.net', js))
print("\nall coches.net hosts:")
for h in sorted(hosts):
    print("  ", h)
