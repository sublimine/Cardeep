from curl_cffi import requests as cr
import json as J

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
HDRS={"User-Agent":UA,"Accept":"application/json, text/plain, */*","Accept-Language":"es-ES,es;q=0.9",
      "Origin":"https://www.milanuncios.com","Referer":"https://www.milanuncios.com/"}

def g(url, extra=None):
    h=dict(HDRS)
    if extra: h.update(extra)
    try:
        r=cr.get(url, impersonate="chrome131", timeout=20, headers=h, allow_redirects=False)
        print(f"GET  {r.status_code} ct={r.headers.get('content-type','')[:28]:<28} len={len(r.content):>7} {url}")
        if r.status_code not in (403,404) and len(r.content)<2000:
            print("     ", r.content[:300])
        return r
    except Exception as e:
        print(f"GET  ERR {type(e).__name__} {str(e)[:50]} :: {url}")

def p(url, payload, extra=None):
    h=dict(HDRS); h["Content-Type"]="application/json"
    if extra: h.update(extra)
    try:
        r=cr.post(url, impersonate="chrome131", timeout=20, headers=h, json=payload, allow_redirects=False)
        print(f"POST {r.status_code} ct={r.headers.get('content-type','')[:28]:<28} len={len(r.content):>7} {url}")
        if r.status_code not in (403,404) and len(r.content)<2000:
            print("     ", r.content[:300])
        return r
    except Exception as e:
        print(f"POST ERR {type(e).__name__} {str(e)[:50]} :: {url}")

print("=== mn.gw.coches.net / ma.gw.coches.net endpoint sweep ===")
HOSTS=["https://mn.gw.coches.net","https://ma.gw.coches.net"]
PATHS=["/search","/v1/search","/v2/search","/listings/search","/ad/search","/ads/search",
       "/motor/search","/cars/search","/api/search","/realestate/search","/health","/","/status",
       "/v1/listings","/listing/search","/searchads","/search/ads"]
PAYLOAD={"categoryId":2500,"page":1,"sortBy":"relevance","sortOrder":"DESC"}
for host in HOSTS:
    for pa in PATHS:
        g(host+pa)
    print("  -- POST /search variants --")
    p(host+"/search", PAYLOAD)
    p(host+"/search", PAYLOAD, {"x-schibsted-tenant":"milanuncios"})
    p(host+"/search", PAYLOAD, {"x-schibsted-tenant":"mn"})
    print()
