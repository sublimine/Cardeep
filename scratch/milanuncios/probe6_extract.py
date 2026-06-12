import re, json
from curl_cffi import requests

H = {"Accept":"text/html,*/*;q=0.8","Accept-Language":"es-ES,es;q=0.9","Accept-Encoding":"gzip, deflate, br"}
r = requests.get("https://www.coches.net/segunda-mano/", impersonate="chrome131", timeout=25, headers=H)
body = r.text

print("=== ms-mt context (inline HTML) ===")
for m in re.finditer(r'.{80}ms-mt.{120}', body):
    print(repr(m.group(0)[:220]))
print("\n=== advgo/api host context ===")
for m in re.finditer(r'.{40}(advgo\.net|api-web|spain\.advgo).{80}', body):
    print(repr(m.group(0)[:180]))

# Pull the main JS bundle and scan it
print("\n=== fetch main.js bundle ===")
js = requests.get("https://s.ccdn.es/main.e06139af.js", impersonate="chrome131", timeout=40,
                  headers={"Accept":"*/*","Referer":"https://www.coches.net/"})
print("bundle status", js.status_code, "len", len(js.content))
jt = js.text
with open("coches_main.js","w",encoding="utf-8") as f:
    f.write(jt)
for kw in ["advgo","ms-mt--api-web","/search","X-Adevinta","x-adevinta-channel","x-schibsted","apiBaseUrl","tenant"]:
    idxs = [m.start() for m in re.finditer(re.escape(kw), jt)]
    print(f"  {kw!r}: {len(idxs)} hits", ("e.g. ...%s..." % jt[idxs[0]-50:idxs[0]+60].replace(chr(10),' ')) if idxs else "")
