import re
jt = open("coches_main.js",encoding="utf-8").read()

# the header constant object: ft={ADOBE_MC_VISITOR_ID:"X-Adevinta-AMCVID",...}
m = re.search(r'\{ADOBE_MC_VISITOR_ID:"X-Adevinta-AMCVID".{0,600}?\}', jt)
print("=== HEADER CONST TABLE ===")
print(m.group(0) if m else "NOT FOUND")

print("\n=== Captcha refs ===")
for m in re.finditer(r'.{30}[Cc]aptcha-?[A-Za-z]{2,20}.{30}', jt):
    print(repr(m.group(0)[:90]))

print("\n=== api host strings (advgo/api-web/spain) ===")
for kw in ["advgo","api-web","spain.adv","ms-mt","apiUrl","API_URL","baseURL","baseUrl","gateway"]:
    for m in re.finditer(re.escape(kw), jt):
        s=m.start(); print(f"  [{kw}] ...{jt[s-40:s+50]}...".replace(chr(10),' ')); break

# find any full https url in bundle that looks like an api
print("\n=== https api-ish urls in bundle ===")
urls = set(re.findall(r'https://[a-zA-Z0-9.\-]+/[a-zA-Z0-9./_\-]*', jt))
for u in sorted(urls):
    if any(k in u for k in ["api","search","advgo","mt","gateway","ms-"]):
        print("  ", u)
