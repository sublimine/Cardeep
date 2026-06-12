import re
from curl_cffi import requests

H = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

# Is the homepage a reese84 interstitial?
r = requests.get("https://www.milanuncios.com/", impersonate="chrome131", timeout=25, headers=H)
body = r.text
print("homepage status", r.status_code, "len", len(body))
for kw in ["reese84","incapsula","_Incapsula","robotsRemoved","onProtectionInitialized","librarym","Pardon Our Interruption","challenge"]:
    print(f"  {kw!r}:", kw in body)
print("title:", re.search(r'<title>([^<]*)</title>', body).group(1) if re.search(r'<title>([^<]*)</title>', body) else None)

print("\n=== librarym.js ===")
r2 = requests.get("https://www.milanuncios.com/librarym.js", impersonate="chrome131", timeout=25, headers={"Accept":"*/*","Referer":"https://www.milanuncios.com/"})
print("status", r2.status_code, "len", len(r2.content), "ct", r2.headers.get('content-type'))
b2 = r2.text
for kw in ["reese84","incapsula","Incapsula","___utmvc","setRequestHeader","/_Incapsula_Resource"]:
    print(f"  {kw!r}:", kw in b2)

print("\n=== listing path /coches-de-segunda-mano/ ===")
r3 = requests.get("https://www.milanuncios.com/coches-de-segunda-mano/", impersonate="chrome131", timeout=25, headers=H, allow_redirects=True)
print("status", r3.status_code, "len", len(r3.content), "server", r3.headers.get('server'))
b3 = r3.text
for kw in ["geetest","reese84","incapsula","captcha","__NEXT_DATA__","ms-mt","advgo"]:
    print(f"  {kw!r}:", kw in b3.lower())
