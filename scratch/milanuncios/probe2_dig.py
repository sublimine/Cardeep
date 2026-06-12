import re
from curl_cffi import requests

H = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

r = requests.get("https://www.milanuncios.com/", impersonate="chrome131", timeout=25, headers=H)
body = r.text
# all script srcs and link hrefs
scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', body)
print("=== SCRIPTS ===")
for s in scripts[:40]:
    print(" ", s)
# inline json config blobs
print("\n=== geetest context ===")
for m in re.finditer(r'.{60}geetest.{60}', body, re.I):
    print(" ", m.group(0).replace("\n"," "))
print("\n=== window. / __ globals ===")
for m in re.finditer(r'window\.[A-Z_a-z0-9]+\s*=', body):
    print(" ", m.group(0))
# any url with api/search/advgo
print("\n=== api-ish urls ===")
for u in set(re.findall(r'https?://[a-zA-Z0-9./_\-]+(?:api|search|advgo|gateway)[a-zA-Z0-9./_\-]*', body)):
    print(" ", u)
