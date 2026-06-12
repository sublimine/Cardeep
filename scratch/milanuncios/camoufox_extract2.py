import asyncio, json
from camoufox.async_api import AsyncCamoufox

async def main():
    async with AsyncCamoufox(headless=True, os="windows", locale="es-ES", geoip=False, humanize=True) as browser:
        page = await browser.new_page()
        await page.goto("https://www.milanuncios.com/", wait_until="domcontentloaded", timeout=90000)
        await page.wait_for_timeout(7000)
        print("home title:", await page.title())
        # robust: wait for any coches link
        el=None
        for attempt in range(3):
            el = await page.query_selector('a[href*="coches-de-segunda-mano"]') or await page.query_selector('a[href*="/motor"]')
            if el: break
            await page.wait_for_timeout(3000)
        if not el:
            # fallback: set referer via goto from motor hub
            print("no link, trying /motor/ hard nav (warm)...")
            await page.goto("https://www.milanuncios.com/motor/", wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)
            el = await page.query_selector('a[href*="coches-de-segunda-mano"]')
        if el:
            await el.click()
        else:
            await page.goto("https://www.milanuncios.com/coches-de-segunda-mano/", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(9000)
        print("listing title:", await page.title(), "| walled:", "Pardon" in (await page.title()))

        props = await page.evaluate("""() => {
            try { return JSON.parse(JSON.stringify({
                ip: window.__INITIAL_PROPS__,
                cfg: window.__APP_CONFIG__
            })); } catch(e){ return {err:String(e)}; }
        }""")
        json.dump(props, open("mn_initial_props.json","w",encoding="utf-8"), ensure_ascii=False)
        print("saved props, size:", len(json.dumps(props)))

asyncio.run(main())
