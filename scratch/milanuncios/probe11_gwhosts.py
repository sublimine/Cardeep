from curl_cffi import requests
import socket

hosts = [
    "web.gw.coches.net",
    "gw.coches.net",
    "adit.gw.coches.net",
    "gw.milanuncios.com",
    "web.gw.milanuncios.com",
    "api.milanuncios.com",
    "ms-mt--api-web.spain.advgo.net",
    "ms-mt--api-gateway-web.spain.advgo.net",
    "api-web.spain.advgo.net",
]
print("=== DNS resolve ===")
for h in hosts:
    try:
        ip = socket.gethostbyname(h)
        print(f"  {h} -> {ip}")
    except Exception as e:
        print(f"  {h} -> NXDOMAIN/{type(e).__name__}")

print("\n=== GET probe each resolvable gw root ===")
for h in ["web.gw.coches.net","gw.coches.net","ms-mt--api-web.spain.advgo.net"]:
    for path in ["/", "/api-web", "/api-web/search", "/mt-search-edge-api/search"]:
        url=f"https://{h}{path}"
        try:
            r=requests.get(url, impersonate="chrome131", timeout=12,
                headers={"Accept":"application/json","Origin":"https://www.coches.net","Referer":"https://www.coches.net/","X-Schibsted-Tenant":"coches","X-Adevinta-Channel":"web"})
            print(f"  [{r.status_code}] {url} len={len(r.content)} ct={r.headers.get('content-type')} :: {r.text[:90].strip()[:90]}")
        except Exception as e:
            print(f"  [ERR] {url} {type(e).__name__}")
