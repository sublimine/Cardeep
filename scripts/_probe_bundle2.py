"""Probe v3 fixed: hosts, base-url builders, and search verb."""
from curl_cffi import requests as r
import re

JS_URL = "https://s.ccdn.es/main.e06139af.js"
js = r.get(JS_URL, impersonate="chrome131", timeout=60).text

# all *.gw.coches.net subdomain literals
hosts = set(re.findall(r'"[a-z0-9.\-]*gw\.coches\.net"', js))
print("gw hosts:", hosts)
subs = set(re.findall(r'API_GW_SUBDOMAIN[A-Z_]*:"[^"]*"', js))
print("gw subdomains:")
for s in sorted(subs):
    print("  ", s)
allsub = set(re.findall(r'API_[A-Z_]*SUBDOMAIN[A-Z_]*:"[^"]*"', js))
print("all subdomain consts:")
for s in sorted(allsub):
    print("  ", s)

print("\n#### post/get near 'search' ####")
for verb in [r"\.post\(", r"\.get\("]:
    for mo in re.finditer(verb, js):
        s = mo.start()
        ctx = js[s-140:s+180].replace("\n", " ")
        if "search" in ctx.lower() or "SEARCH" in ctx:
            print(verb, "::", ctx)
            print("--")
