from curl_cffi import requests as cr
import socket
UA_APP="MilanunciosApp/Android"
def dns(host):
    try:
        ip=socket.gethostbyname(host); return ip
    except Exception as e:
        return f"NXDOMAIN ({type(e).__name__})"

print("=== DNS resolution of candidate app/api hosts ===")
hosts=[
 "api.milanuncios.com","app.milanuncios.com","m.milanuncios.com","mobile.milanuncios.com",
 "gateway.milanuncios.com","gw.milanuncios.com","web.gw.milanuncios.com","apigw.milanuncios.com",
 "api-mobile.milanuncios.com","search.milanuncios.com","api.mlu.com",
 "ms-mt--api-web.milanuncios.com","prod.adevinta.com",
 "web.gw.coches.net","mn.gw.coches.net","ma.gw.coches.net","adit.gw.coches.net",
 "api.adevinta.com","gateway.mobile.adevinta.com",
]
for hh in hosts:
    print(f"  {dns(hh):<40} {hh}")

def probe(method,url,host=None,extra=None,json=None):
    h={"User-Agent":UA_APP,"Accept":"application/json"}
    if extra: h.update(extra)
    try:
        r=cr.request(method,url, impersonate="chrome131", timeout=20, headers=h, json=json, allow_redirects=False)
        ct=r.headers.get("content-type","")
        body=r.content[:200]
        print(f"{r.status_code} ct={ct[:30]} len={len(r.content):>7} {method} {url}")
        if r.status_code<500 and r.status_code not in (403,404):
            print("    BODY:", body)
    except Exception as e:
        print(f"ERR {type(e).__name__} {str(e)[:60]} :: {url}")

print("\n=== probe coches.net gateway with milanuncios tenant variants ===")
TENANTS=["milanuncios","mn","ma","MILANUNCIOS","milanuncios-es","Milanuncios","mil"]
PAYLOAD={"categoryId":2500,"page":1,"sortBy":"relevance","sortOrder":"DESC"}
for t in TENANTS:
    try:
        r=cr.post("https://web.gw.coches.net/search", impersonate="chrome131", timeout=20, json=PAYLOAD,
            headers={"Accept":"application/json","Content-Type":"application/json","x-schibsted-tenant":t,
                     "Origin":"https://www.milanuncios.com","Referer":"https://www.milanuncios.com/"})
        print(f"  tenant={t:<16} -> {r.status_code} len={len(r.content)}")
    except Exception as e:
        print(f"  tenant={t:<16} -> ERR {type(e).__name__}")
