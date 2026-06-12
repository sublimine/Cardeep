import sys
from curl_cffi import requests

ES_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

def probe(url, **kw):
    try:
        r = requests.get(url, impersonate="chrome131", timeout=25, headers=ES_HEADERS, **kw)
        print(f"[{r.status_code}] {url}  len={len(r.content)}  server={r.headers.get('server')}  ct={r.headers.get('content-type')}")
        return r
    except Exception as e:
        print(f"[ERR] {url} -> {type(e).__name__}: {e}")
        return None

print("=== Homepage ===")
r = probe("https://www.milanuncios.com/")
if r is not None:
    body = r.text
    # find api hosts
    import re
    hosts = set(re.findall(r'https://([a-z0-9.\-]+\.(?:advgo\.net|milanuncios\.com|adevinta\.com|mpcdn\.net))', body))
    print("HOSTS:", sorted(hosts)[:40])
    # find __NEXT_DATA__ / build info
    print("has __NEXT_DATA__:", "__NEXT_DATA__" in body)
    print("has buildId:", "buildId" in body)
    for kw in ["advgo", "api-web", "/api/", "graphql", "geetest", "datadome", "px-cloud", "perimeterx"]:
        print(f"  contains {kw!r}:", kw in body.lower())
