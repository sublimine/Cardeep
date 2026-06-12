import asyncio, json, re
from camoufox.async_api import AsyncCamoufox

async def main():
    async with AsyncCamoufox(headless=True, os="windows", locale="es-ES", geoip=False, humanize=True) as browser:
        page = await browser.new_page()
        xhr=[]
        async def on_resp(resp):
            u=resp.url
            if resp.request.method=="POST" and any(k in u for k in ["/search","api-web","ms-mt","listing","/find","/results"]):
                try: t=await resp.text()
                except: t="<err>"
                xhr.append((resp.status,u,t[:200]))
        page.on("response", on_resp)

        print("[1] homepage warm-up (mint reese84)...")
        await page.goto("https://www.milanuncios.com/", wait_until="networkidle", timeout=90000)
        await page.wait_for_timeout(6000)
        print("    homepage title:", await page.title())
        print("    cookies:", [c['name'] for c in await page.context.cookies() if 'reese' in c['name'].lower() or 'datadome' in c['name'].lower()])

        # try IN-PAGE navigation: click the coches link instead of hard nav
        print("[2] try clicking 'Motor' / coches link in-page...")
        clicked=False
        for sel in ['a[href*="coches-de-segunda-mano"]','a[href*="/motor"]','a[href*="coches"]']:
            try:
                el = await page.query_selector(sel)
                if el:
                    await el.click(); clicked=True
                    print("    clicked", sel)
                    break
            except Exception as e: 
                pass
        if not clicked:
            print("    no in-page link, hard nav...")
            await page.goto("https://www.milanuncios.com/coches-de-segunda-mano/", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(9000)
        title = await page.title()
        print("    listing title:", title, "| url:", page.url)

        html = await page.content()
        print("    html len:", len(html))
        # is it the wall or real listings?
        walled = "Pardon Our Interruption" in title or "Pardon Our Interruption" in html
        print("    WALLED:", walled)
        if not walled:
            # extract __NEXT_DATA__ or JSON-LD or ad cards
            print("    has __NEXT_DATA__:", "__NEXT_DATA__" in html)
            cards = re.findall(r'aria-label="([^"]{8,80})"', html)
            print("    sample aria labels:", cards[:8])
            open("mn_listing.html","w",encoding="utf-8").write(html)
            # try extract listing JSON
            m=re.search(r'__NEXT_DATA__[^>]*>(\{.*?\})</script>', html, re.S)
            if m:
                open("mn_next_data.json","w",encoding="utf-8").write(m.group(1))
                print("    saved __NEXT_DATA__ len", len(m.group(1)))
        print("\n[XHR search-ish]:")
        for s in xhr: print("   ",s[0],s[1],s[2][:80])
        json.dump(xhr, open("mn_warm_xhr.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)

asyncio.run(main())
