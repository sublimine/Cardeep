import re
jt = open("coches_main.js",encoding="utf-8").read()

# config object around SECURED_API_ROUTE
i = jt.find("SECURED_API_ROUTE")
print("=== CONFIG around SECURED_API_ROUTE ===")
print(jt[i-700:i+700])
print("\n\n=== API_INTERNAL_URL block ===")
j = jt.find("API_INTERNAL_URL")
print(jt[j-300:j+400])
