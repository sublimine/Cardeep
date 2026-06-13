"""Probe AEDRA directory raw HTML to design the parser."""
from curl_cffi import requests as creq

H = {"Accept-Language": "es-ES,es;q=0.9"}


def get(url):
    r = creq.get(url, impersonate="chrome131", headers=H, timeout=40)
    return r.status_code, r.text


if __name__ == "__main__":
    sc, html = get("https://aedra.org/buscador-de-socios/")
    print("list status", sc, "len", len(html))
    # dump a window around first member card
    import re
    # find directory item blocks
    m = re.search(r"(asociados/[a-z0-9-]+/)", html)
    print("first asociado slug:", m.group(1) if m else None)
    # count member links on page 1
    slugs = re.findall(r'href="https://aedra\.org/asociados/([a-z0-9-]+)/"', html)
    print("page1 member slugs:", len(slugs), slugs[:5])
    # pagination max
    pages = re.findall(r"/buscador-de-socios/page/(\d+)/", html)
    print("max page:", max(int(p) for p in pages) if pages else None)
    # save snippet
    idx = html.find("asociados/")
    print("---SNIPPET---")
    print(html[idx-600:idx+400])
    # fetch one detail page
    if slugs:
        sc2, d = get(f"https://aedra.org/asociados/{slugs[0]}/")
        print("detail status", sc2, "len", len(d))
        # find website / address / phone in detail
        for pat in [r'href="(https?://(?!aedra\.org)[^"]+)"', r'(\d{5})\b', r'tel:(\d+)']:
            found = re.findall(pat, d)
            print(pat, "->", found[:6])
