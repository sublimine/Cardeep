from curl_cffi import requests as cr
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
def head(url):
    try:
        r=cr.get(url, impersonate="chrome131", timeout=20, headers={"User-Agent":UA,"Accept":"*/*"}, allow_redirects=False)
        c=r.content
        code = ""
        if b"<Code>" in c:
            code=c.split(b"<Code>")[1].split(b"</Code>")[0].decode()
        is_xml_sitemap = b"<urlset" in c or b"<sitemapindex" in c
        print(f"{r.status_code} {code:<16} sitemap={is_xml_sitemap} len={len(c):>7} {url.replace('https://www.milanuncios.com','')}")
        if is_xml_sitemap: print("    >>> SITEMAP XML:", c[:400])
        return r
    except Exception as e:
        print(f"ERR {type(e).__name__} :: {url}")

# AccessDenied (vs NoSuchKey) on S3 behind CF often means: bucket lists denied but specific keys readable.
# Sweep plausible sitemap object keys served through the www CDN.
keys=[
 "/sitemap_index.xml.gz","/sitemap1.xml","/sitemap0.xml","/sitemap-0.xml",
 "/sitemaps/index.xml","/sitemaps/sitemap_index.xml","/sitemap/index.xml",
 "/sitemap/motor.xml","/sitemap/motor/sitemap.xml","/sitemaps/motor.xml",
 "/sitemap-coches-1.xml","/sitemap_coches.xml","/sitemap_motor.xml",
 "/sitemaps/coches.xml","/seo/sitemaps/sitemap.xml","/static/sitemap.xml",
 "/sitemap/sitemap-index.xml","/sitemapindex.xml","/sitemap.txt",
 "/sitemap_es.xml","/es/sitemap.xml","/sitemap/es/sitemap.xml",
]
for k in keys: head("https://www.milanuncios.com"+k)
