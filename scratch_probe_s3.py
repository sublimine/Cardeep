from curl_cffi import requests as cr
import socket
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

# The /sitemap.xml returns S3-style AccessDenied. Find the real CDN/bucket host.
def head(url):
    try:
        r=cr.get(url, impersonate="chrome131", timeout=20, headers={"User-Agent":UA}, allow_redirects=False)
        srv=r.headers.get("server",""); xamz=[k for k in r.headers if k.lower().startswith("x-amz")]
        print(f"{r.status_code} server={srv:<20} amz={xamz} len={len(r.content)} {url}")
        if len(r.content)<500: print("    ", r.content[:250])
        return r
    except Exception as e:
        print(f"ERR {type(e).__name__} {str(e)[:50]} :: {url}")

print("=== inspect the S3 AccessDenied headers on www host ===")
head("https://www.milanuncios.com/sitemap.xml")

print("\n=== candidate CDN / static / bucket hosts ===")
cands=[
 "https://static.milanuncios.com/sitemap.xml",
 "https://cdn.milanuncios.com/sitemap.xml",
 "https://assets.milanuncios.com/sitemap.xml",
 "https://img.milanuncios.com/sitemap.xml",
 "https://www.milanuncios.com/sitemap/coches.xml",
 "https://www.milanuncios.com/robots-sitemap.xml",
 "https://prod-milanuncios-sitemaps.s3.amazonaws.com/sitemap.xml",
 "https://milanuncios-sitemaps.s3.amazonaws.com/sitemap.xml",
 "https://milanuncios-sitemap.s3.eu-west-1.amazonaws.com/sitemap.xml",
]
for u in cands:
    try: socket.gethostbyname(u.split("/")[2])
    except Exception as e:
        print(f"NXDOMAIN :: {u}"); continue
    head(u)

print("\n=== try sitemap with googlebot UA (sometimes gated by UA) ===")
GB="Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
for u in ["https://www.milanuncios.com/sitemap.xml","https://www.milanuncios.com/robots.txt",
          "https://www.milanuncios.com/coches-de-segunda-mano/"]:
    try:
        r=cr.get(u, impersonate="chrome131", timeout=20, headers={"User-Agent":GB,"Accept":"*/*"}, allow_redirects=False)
        c=r.content
        print(f"{r.status_code} len={len(c):>7} walled={b'reese84' in c or b'Pardon' in c} xml={b'<urlset' in c or b'<sitemapindex' in c} {u}")
        if b"<sitemapindex" in c or b"<urlset" in c: print("    XML:", c[:300])
    except Exception as e:
        print(f"ERR {type(e).__name__} :: {u}")
