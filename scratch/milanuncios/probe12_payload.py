import json
from curl_cffi import requests

PAYLOAD = {"categoryId":2500,"page":1,"sortBy":"relevance","sortOrder":"DESC",
           "price":{"from":None,"to":None},"year":{"from":None,"to":None},"km":{"from":None,"to":None}}

def post(url, origin, referer, extra=None):
    h = {"Accept":"application/json","Content-Type":"application/json",
         "Origin":origin,"Referer":referer,"Accept-Language":"es-ES,es;q=0.9"}
    if extra: h.update(extra)
    try:
        r = requests.post(url, impersonate="chrome131", timeout=25, json=PAYLOAD, headers=h)
        print(f"[{r.status_code}] {url} len={len(r.content)} ct={r.headers.get('content-type')}")
        t = r.text
        if r.status_code==200 and ('{' in t):
            try:
                j=r.json()
                print("   JSON keys:", list(j.keys())[:15] if isinstance(j,dict) else type(j))
            except: print("   not json:", t[:150])
        else:
            print("   body:", t[:200].replace("\n"," "))
        return r
    except Exception as e:
        print(f"[ERR] {url} {type(e).__name__}: {e}")

print("=== advgo direct ===")
post("https://ms-mt--api-web.spain.advgo.net/search", "https://www.coches.net", "https://www.coches.net/")
print("=== coches.net /api/search proxy ===")
post("https://www.coches.net/api/search", "https://www.coches.net", "https://www.coches.net/")
print("=== advgo with trailing slash ===")
post("https://ms-mt--api-web.spain.advgo.net/search/", "https://www.coches.net", "https://www.coches.net/")
