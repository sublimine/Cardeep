import asyncio, json
from camoufox.async_api import AsyncCamoufox

CAPTURED = []

async def main():
    async with AsyncCamoufox(headless=True, os="windows", locale="es-ES",
                             geoip=False, humanize=True) as browser:
        page = await browser.new_page()

        async def on_request(req):
            u = req.url
            if any(k in u for k in ["/search","gw.","advgo","api-web","listing","/ms-mt"]) and req.method=="POST":
                try: body = req.post_data
                except: body = None
                CAPTURED.append({"url":u,"method":req.method,"headers":dict(req.headers),"body":body})

        async def on_response(resp):
            u = resp.url
            if any(k in u for k in ["/search","gw.","advgo","api-web","/ms-mt"]) and resp.request.method=="POST":
                try:
                    txt = await resp.text()
                except Exception as e:
                    txt = f"<err {e}>"
                for c in CAPTURED:
                    if c["url"]==u and "status" not in c:
                        c["status"]=resp.status; c["resp_head"]=txt[:400]; c["resp_len"]=len(txt)
                        if resp.status==200 and txt.strip().startswith("{"):
                            open("mn_search_response.json","w",encoding="utf-8").write(txt)
                        break

        page.on("request", on_request)
        page.on("response", on_response)

        print("[1] warm-up homepage...")
        await page.goto("https://www.milanuncios.com/", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(8000)
        print("    title:", await page.title())

        print("[2] listing page...")
        try:
            await page.goto("https://www.milanuncios.com/coches-de-segunda-mano/", wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print("    nav err:", e)
        await page.wait_for_timeout(10000)
        print("    title:", await page.title())
        print("    url:", page.url)
        # scroll to trigger lazy search
        try:
            await page.mouse.wheel(0, 3000); await page.wait_for_timeout(4000)
        except: pass

        print("\n[CAPTURED POSTs]:")
        for c in CAPTURED:
            print(f"  [{c.get('status','?')}] {c['url']}")
            print("     tenant:", c['headers'].get('x-schibsted-tenant'))
            print("     body:", (c.get('body') or '')[:160])
        json.dump(CAPTURED, open("mn_captured.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)

asyncio.run(main())
