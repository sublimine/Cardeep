import re
jt = open("coches_main.js",encoding="utf-8").read()
# search path constants near 'listing' / 'search' usage with api-web
print("=== '/api-web' usages ===")
for m in re.finditer(r'.{20}/api-web[a-zA-Z0-9/_\-{}.]{0,60}', jt):
    print(repr(m.group(0)[:110]))
print("\n=== listing/search endpoint path literals ===")
for kw in ['"/search"',"/listing","/results","/srp","/vehicles","/ads","mtweb","mt-search","/v1/","/v2/","getSearch","searchListing"]:
    for m in re.finditer(re.escape(kw), jt):
        s=m.start(); print(f"  [{kw}] ...{jt[s-45:s+45]}...".replace(chr(10),' ')); break
print("\n=== gw.coches.net / API_SUBDOMAIN usage ===")
for kw in ["gw.coches.net","API_SUBDOMAIN","API_DOMAIN","web.gw","cnet-content"]:
    for m in re.finditer(re.escape(kw), jt):
        s=m.start(); print(f"  [{kw}] ...{jt[s-30:s+60]}...".replace(chr(10),' ')); break
