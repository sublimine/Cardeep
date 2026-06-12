import json
from curl_cffi import requests

PAYLOAD = {"categoryId":2500,"page":1,"sortBy":"relevance","sortOrder":"DESC",
           "price":{"from":None,"to":None},"year":{"from":None,"to":None},"km":{"from":None,"to":None}}

def post(host, tenant, origin, referer):
    url=f"https://{host}/search"
    h={"Accept":"application/json","Content-Type":"application/json",
       "x-schibsted-tenant":tenant,"Origin":origin,"Referer":referer,
       "Accept-Language":"es-ES,es;q=0.9"}
    try:
        r=requests.post(url, impersonate="chrome131", timeout=25, json=PAYLOAD, headers=h)
        print(f"[{r.status_code}] {url} tenant={tenant} len={len(r.content)} ct={r.headers.get('content-type')}")
        if r.status_code==200:
            try:
                j=r.json(); items=j.get('items',[])
                print(f"   *** items={len(items)} firstTitle={items[0]['title'] if items else None}")
            except Exception as e: print("   json err", e, r.text[:120])
        else:
            print("   body:", r.text[:160].replace("\n"," "))
        return r
    except Exception as e:
        print(f"[ERR] {url} {type(e).__name__}: {e}")

print("=== baseline: coches tenant (should 200 with items) ===")
post("web.gw.coches.net","coches","https://www.coches.net","https://www.coches.net/")
print("\n=== milanuncios tenant on SAME gateway ===")
for t in ["milanuncios","mn","milanuncios-es"]:
    post("web.gw.coches.net", t, "https://www.milanuncios.com","https://www.milanuncios.com/")
