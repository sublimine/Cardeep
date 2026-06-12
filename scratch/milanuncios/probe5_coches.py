import re, json
from curl_cffi import requests

H = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}
r = requests.get("https://www.coches.net/segunda-mano/", impersonate="chrome131", timeout=25, headers=H)
print("coches SRP status", r.status_code, "len", len(r.content))
body = r.text
# find JS chunks
scripts = re.findall(r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']', body)
print("scripts found:", len(scripts))
# look for advgo / api references inline
for kw in ["advgo","ms-mt","x-adevinta","X-Adevinta","apiKey","api_key","x-schibsted","__NEXT_DATA__","searchId","tenant"]:
    print(f"  inline {kw!r}:", kw in body)
# save scripts list
with open("coches_scripts.txt","w") as f:
    f.write("\n".join(scripts))
print("\nsample scripts:")
for s in scripts[:15]:
    print("  ", s)
