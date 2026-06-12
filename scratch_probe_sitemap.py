from curl_cffi import requests as cr
import sys

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

def probe(url, host=None):
    h={"User-Agent":UA,"Accept":"*/*"}
    if host: h["Host"]=host
    try:
        r=cr.get(url, impersonate="chrome131", timeout=20, headers=h, allow_redirects=False)
        body=r.content[:400]
        is_xml = b"<urlset" in r.content or b"<sitemapindex" in r.content or b"<?xml" in r.content[:200]
        print(f"{r.status_code:>3} xml={is_xml} len={len(r.content):>8} {url}")
        if r.status_code in (301,302,303,307,308):
            print(f"     -> Location: {r.headers.get('location')}")
        if is_xml:
            print("     XML HEAD:", body[:300])
        return r
    except Exception as e:
        print(f"ERR {url} :: {type(e).__name__} {e}")
        return None

print("=== robots.txt ===")
r=probe("https://www.milanuncios.com/robots.txt")
if r and r.status_code==200:
    txt=r.text
    print("---- robots body (first 2000) ----")
    print(txt[:2000])
    print("---- Sitemap lines ----")
    for line in txt.splitlines():
        if "sitemap" in line.lower():
            print("  ", line)

print("\n=== sitemap candidates ===")
cands=[
 "https://www.milanuncios.com/sitemap.xml",
 "https://www.milanuncios.com/sitemap_index.xml",
 "https://www.milanuncios.com/sitemap-index.xml",
 "https://www.milanuncios.com/sitemaps.xml",
 "https://www.milanuncios.com/sitemap.xml.gz",
 "https://www.milanuncios.com/sitemap/sitemap.xml",
 "https://www.milanuncios.com/sitemaps/sitemap.xml",
 "https://www.milanuncios.com/sitemap-coches.xml",
 "https://www.milanuncios.com/coches/sitemap.xml",
 "https://www.milanuncios.com/seo/sitemap.xml",
 "https://www.milanuncios.com/sitemap-motor.xml",
 "https://www.milanuncios.com/google-sitemap.xml",
 "https://sitemap.milanuncios.com/sitemap.xml",
 "https://www.milanuncios.com/sitemap_motor_index.xml",
 "https://www.milanuncios.com/anuncios-sitemap.xml",
]
for u in cands:
    probe(u)
