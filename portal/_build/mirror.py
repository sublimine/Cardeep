#!/usr/bin/env python3
"""Mirror íntegro de un demo estático (BFS): HTML + CSS + JS + imgs + fuentes,
conservando la estructura relativa para servir idéntico en local.
Uso: mirror.py <PREFIX_URL> <LOCAL_DIR> <START_URL> [<START_URL> ...]
Solo descarga recursos bajo PREFIX_URL. Reescribe nada (enlaces relativos intactos)."""
import sys, os, re, urllib.request, urllib.parse
PREFIX=sys.argv[1]; LOCAL=sys.argv[2]; STARTS=sys.argv[3:]
UA={"User-Agent":"Mozilla/5.0 (compatible; cardeep-mirror)"}
PREF_PATH=urllib.parse.urlsplit(PREFIX).path
seen=set(); q=list(STARTS); saved=0; failed=[]
def localpath(url):
    p=urllib.parse.unquote(urllib.parse.urlsplit(url).path)
    rel=p[len(PREF_PATH):] if p.startswith(PREF_PATH) else p.lstrip("/")
    if rel=="" or rel.endswith("/"): rel+="index.html"
    return os.path.join(LOCAL, *[s for s in rel.split("/") if s not in ("",".","..")])
def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=40) as r:
        return r.read(), (r.headers.get_content_type() or "")
def extract(text, base, css=False):
    urls=set()
    if css:
        urls|=set(re.findall(r'url\(\s*[\'"]?([^\'")]+)', text))
        urls|=set(re.findall(r'@import\s+[\'"]([^\'"]+)', text))
    else:
        urls|=set(re.findall(r'(?:href|src|data-src)\s*=\s*[\'"]([^\'"]+)[\'"]', text))
        urls|=set(re.findall(r'url\(\s*[\'"]?([^\'")]+)', text))
    out=set()
    for u in urls:
        if u.startswith(("data:","javascript:","mailto:","tel:","#")): continue
        full=urllib.parse.urljoin(base, u.split("#")[0].split("?")[0])
        if full.startswith(PREFIX): out.add(full)
    return out
while q and saved<3000:
    url=q.pop(0)
    if url in seen: continue
    seen.add(url)
    try: data,ct=fetch(url)
    except Exception as e: failed.append((url,str(e)[:50])); continue
    lp=localpath(url); os.makedirs(os.path.dirname(lp) or ".",exist_ok=True)
    with open(lp,"wb") as f: f.write(data)
    saved+=1
    low=url.lower()
    if "html" in ct or low.endswith((".html",".htm")):
        for nu in extract(data.decode("utf-8","ignore"), url):
            if nu not in seen: q.append(nu)
    elif "css" in ct or low.endswith(".css"):
        for nu in extract(data.decode("utf-8","ignore"), url, css=True):
            if nu not in seen: q.append(nu)
print("SAVED",saved,"FAILED",len(failed))
for f in failed[:25]: print("  FAIL",f[0][-70:],f[1])
