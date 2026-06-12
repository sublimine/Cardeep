import re
jt = open("coches_main.js",encoding="utf-8").read()

# How is API host assembled? look for API_SUBDOMAIN+API_DOMAIN concatenation
print("=== host assembly (API_SUBDOMAIN / SECURED_ROOT) ===")
for m in re.finditer(r'API_SUBDOMAIN[^,;]{0,80}', jt):
    print(repr(m.group(0)[:100]))
# search for the request path used with the gw — look for 'mt-search' or version path adjacent to api-web or vehicles
print("\n=== 'search' path with version ===")
for m in re.finditer(r'["\'/][a-z\-]*search[a-z\-/]*["\'/]', jt):
    print(repr(m.group(0)))
print("\n=== 'vehicles' literal contexts ===")
for m in re.finditer(r'.{25}vehicles.{35}', jt):
    t=m.group(0)
    if '"' in t or '/' in t: print(repr(t[:80]))
