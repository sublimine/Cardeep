from curl_cffi import requests as cr
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
def probe(url):
    h={"User-Agent":UA,"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
       "Accept-Language":"es-ES,es;q=0.9"}
    try:
        r=cr.get(url, impersonate="chrome131", timeout=25, headers=h, allow_redirects=True)
        c=r.content
        walled = b"Pardon Our Interruption" in c or b"reese84" in c or b"librarym.js" in c
        geetest = b"geetest" in c.lower() or b"captcha" in c.lower()
        xml = b"<urlset" in c or b"<sitemapindex" in c
        ld = c.count(b'application/ld+json')
        htm_links = c.count(b'.htm')
        print(f"{r.status_code} len={len(c):>8} walled={walled} geetest={geetest} xml={xml} ldjson={ld} dotHtm={htm_links} {url}")
        return r
    except Exception as e:
        print(f"ERR {type(e).__name__} {e} :: {url}")
        return None

cands=[
 "https://www.milanuncios.com/anuncios/sitemap-xml-php.htm",
 "https://www.milanuncios.com/anuncios/sitemap-xml.htm",
 "https://www.milanuncios.com/anuncios-en-lugo/sitemap-xml-php.htm",
 "https://www.milanuncios.com/anuncios-en-caceres/sitemap-xml.htm",
 "https://www.milanuncios.com/coches-de-segunda-mano/sitemap-xml.htm",
 "https://www.milanuncios.com/coches-de-segunda-mano/sitemap-xml-php.htm",
 "https://www.milanuncios.com/sitemap.htm",
 "https://www.milanuncios.com/mapa-web/",
 "https://www.milanuncios.com/mapa-del-sitio/",
]
for u in cands: probe(u)
