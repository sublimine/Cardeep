import asyncio, json, re
from camoufox.async_api import AsyncCamoufox

async def main():
    async with AsyncCamoufox(headless=True, os="windows", locale="es-ES", geoip=False, humanize=True) as browser:
        page = await browser.new_page()
        # warm
        await page.goto("https://www.milanuncios.com/", wait_until="domcontentloaded", timeout=90000)
        await page.wait_for_timeout(7000)
        el=None
        for _ in range(4):
            el = await page.query_selector('a[href*="coches-de-segunda-mano"]')
            if el: break
            await page.wait_for_timeout(2500)
        await el.click(); await page.wait_for_timeout(8000)

        # scroll to lazy-load more cards, then count
        for i in range(6):
            await page.mouse.wheel(0, 4000); await page.wait_for_timeout(1500)
        n = await page.evaluate("() => document.querySelectorAll('article.ma-AdCardV2, article[data-testid=\"AD_CARD\"]').length")
        print("cards after scroll:", n)

        # grab one PDP via warm in-page click to confirm dealer attribution + JSON-LD
        first = await page.query_selector('article.ma-AdCardV2 a[href*=".htm"]')
        href = await first.get_attribute('href')
        print("opening PDP:", href)
        await first.click(); await page.wait_for_timeout(8000)
        print("PDP title:", await page.title(), "| walled:", "Pardon" in (await page.title()))
        pdp = await page.evaluate(r"""() => {
          const ld=[...document.querySelectorAll('script[type="application/ld+json"]')].map(s=>s.textContent);
          const txt=document.body.innerText;
          const seller=(txt.match(/(Concesionario|Profesional|Particular)[^\n]{0,60}/i)||[])[0];
          return {ld_count:ld.length, ld:ld.slice(0,3), seller_line:seller, url:location.href};
        }""")
        json.dump(pdp, open("mn_pdp.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
        print("PDP ld_count:", pdp["ld_count"], "| seller:", pdp["seller_line"])
        # show vehicle JSON-LD
        for blob in pdp["ld"]:
            if blob and '"Vehicle"' in blob or (blob and 'Product' in blob):
                print("LD-VEHICLE head:", re.sub(r'\s+',' ',blob)[:400]); break

asyncio.run(main())
