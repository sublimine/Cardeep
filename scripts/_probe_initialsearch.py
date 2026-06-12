"""Throwaway probe: decode coches.net SRP __INITIAL_PROPS__ to read the REAL
initialSearch payload field names (the canonical filter shape the web sends)."""
from curl_cffi import requests as r
import json
import re

HTML = {
    "Accept": "text/html,application/xhtml+xml",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
}
resp = r.get("https://www.coches.net/segunda-mano/", headers=HTML,
             impersonate="chrome131", timeout=40)
t = resp.text
print("SRP status", resp.status_code, "len", len(t))

# Locate the assignment. Two known forms: JSON.parse("...") or = {...}.
m = re.search(r'window\.__INITIAL_PROPS__\s*=\s*', t)
print("assign idx", m.start() if m else None)
seg = t[m.end():m.end()+60]
print("after assign:", repr(seg[:60]))

# Scan a JS string literal starting at the first quote, honoring backslash escapes.
qpos = t.index('"', m.end())
out = []
j = qpos + 1
BS = chr(92)
while j < len(t):
    c = t[j]
    if c == BS:
        out.append(t[j:j+2])
        j += 2
        continue
    if c == '"':
        break
    out.append(c)
    j += 1
literal = "".join(out)
# literal is the inside of a JS double-quoted string -> decode escapes to real text.
decoded = json.loads('"' + literal + '"')
obj = json.loads(decoded)
isr = obj.get("initialSearch") or obj.get("props", {}).get("initialSearch")
if isr is None:
    # search nested
    def find_key(d, key):
        if isinstance(d, dict):
            if key in d:
                return d[key]
            for v in d.values():
                res = find_key(v, key)
                if res is not None:
                    return res
        elif isinstance(d, list):
            for v in d:
                res = find_key(v, key)
                if res is not None:
                    return res
        return None
    isr = find_key(obj, "initialSearch")
print("=== initialSearch field map ===")
print(json.dumps(isr, ensure_ascii=False, indent=1))
