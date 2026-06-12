import json
from curl_cffi import requests

# Candidate Adevinta/milanuncios API hosts
CANDIDATES = [
    ("coches.net advgo", "https://ms-mt--api-web.spain.advgo.net/search"),
    ("ma generic advgo", "https://ms-mt--api-web.spain.advgo.net/ma/search"),
    ("milanuncios api host guess1", "https://api.milanuncios.com/search"),
    ("milanuncios ms-mt", "https://ms-mt--api-web.spain.advgo.net/api/v1/search"),
]

def post(name, url, payload):
    try:
        r = requests.post(url, impersonate="chrome131", timeout=20,
                          json=payload,
                          headers={
                              "Accept":"application/json, text/plain, */*",
                              "Content-Type":"application/json;charset=UTF-8",
                              "Accept-Language":"es-ES,es;q=0.9",
                              "Origin":"https://www.coches.net",
                              "Referer":"https://www.coches.net/",
                          })
        print(f"[{r.status_code}] POST {name} {url} len={len(r.content)} ct={r.headers.get('content-type')}")
        print("   body head:", r.text[:300].replace("\n"," "))
        return r
    except Exception as e:
        print(f"[ERR] POST {name} {url} -> {type(e).__name__}: {e}")
        return None

# minimal/empty payload to detect endpoint existence (502/400 = exists)
for name, url in CANDIDATES:
    post(name, url, {"pagination":{"page":1,"size":2},"sort":{"order":"desc","term":"relevance"},"filters":{"isFinanced":False}})
