import socket, json
from curl_cffi import requests

hosts=["web.gw.milanuncios.com","gw.milanuncios.com","mn.gw.coches.net","web.gw.mn.com",
       "ms-mt--api-web.milanuncios.com","api-web.milanuncios.com","web.gw.motos.net",
       "search.milanuncios.com","mt-search.milanuncios.com","adit.gw.milanuncios.com"]
print("=== DNS ===")
live=[]
for h in hosts:
    try:
        ip=socket.gethostbyname(h); print(f"  {h} -> {ip}"); live.append(h)
    except Exception: print(f"  {h} -> NXDOMAIN")

PAYLOAD={"categoryId":2500,"page":1,"sortBy":"relevance","sortOrder":"DESC",
         "price":{"from":None,"to":None},"year":{"from":None,"to":None},"km":{"from":None,"to":None}}
print("\n=== POST /search on live milanuncios gw candidates ===")
for h in live:
    try:
        r=requests.post(f"https://{h}/search", impersonate="chrome131", timeout=15, json=PAYLOAD,
            headers={"Accept":"application/json","Content-Type":"application/json","x-schibsted-tenant":"milanuncios",
                     "Origin":"https://www.milanuncios.com","Referer":"https://www.milanuncios.com/"})
        print(f"  [{r.status_code}] {h}/search len={len(r.content)} :: {r.text[:80]}")
    except Exception as e:
        print(f"  [ERR] {h} {type(e).__name__}")

print("\n=== retry coches gw with alt milanuncios tenant strings ===")
for t in ["MILANUNCIOS","Milanuncios","ma","mn-es","milanuncios.com","motos"]:
    r=requests.post("https://web.gw.coches.net/search", impersonate="chrome131", timeout=15, json=PAYLOAD,
        headers={"Accept":"application/json","Content-Type":"application/json","x-schibsted-tenant":t,
                 "Origin":"https://www.milanuncios.com","Referer":"https://www.milanuncios.com/"})
    print(f"  [{r.status_code}] tenant={t} len={len(r.content)}")
