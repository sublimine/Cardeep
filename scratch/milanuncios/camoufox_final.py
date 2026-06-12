import asyncio, json, re
from camoufox.async_api import AsyncCamoufox

async def main():
    async with AsyncCamoufox(headless=True, os="windows", locale="es-ES", geoip=False, humanize=True) as browser:
        page = await browser.new_page()
        await page.goto("https://www.milanuncios.com/", wait_until="domcontentloaded", timeout=90000)
        await page.wait_for_timeout(7000)
        el=None
        for _ in range(4):
            el=await page.query_selector('a[href*="coches-de-segunda-mano"]')
            if el: break
            await page.wait_for_timeout(2500)
        await el.click(); await page.wait_for_timeout(8000)
        for i in range(8):
            await page.mouse.wheel(0,4000); await page.wait_for_timeout(1200)
        n=await page.evaluate("()=>document.querySelectorAll('article.ma-AdCardV2').length")
        # grab a card href, navigate via goto (warm cookies already set)
        href=await page.evaluate("()=>{const a=document.querySelector('article.ma-AdCardV2 a[href*=\".htm\"]');return a?a.getAttribute('href'):null;}")
        print("cards loaded after scroll:", n, "| PDP href:", href)
        await page.goto("https://www.milanuncios.com"+href.split('?')[0], wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(6000)
        print("PDP title:", await page.title(), "| walled:", "Pardon" in (await page.title()))
        pdp=await page.evaluate(r"""()=>{
          const ld=[...document.querySelectorAll('script[type=\"application/ld+json\"]')].map(s=>s.textContent);
          const t=document.body.innerText;
          return {ld, price:(t.match(/([\d.]+)\s*€/)||[])[0],
                  seller:(t.match(/(Profesional|Particular|Concesionario)[^\n]{0,50}/i)||[])[0],
                  phone:/(\b\d{9}\b)/.test(t)};
        }""")
        veh=[b for b in pdp["ld"] if b and ('"Vehicle"' in b or '"Product"' in b or '"Car"' in b)]
        print("PDP price:", pdp["price"], "| seller:", pdp["seller"])
        if veh: print("PDP JSON-LD:", re.sub(r'\s+',' ',veh[0])[:500])
        json.dump({"cards_after_scroll":n,"pdp":pdp}, open("mn_final.json","w",encoding="utf-8"), ensure_ascii=False)

asyncio.run(main())
