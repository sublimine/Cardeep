import asyncio, json, re
from camoufox.async_api import AsyncCamoufox

async def main():
    async with AsyncCamoufox(headless=True, os="windows", locale="es-ES", geoip=False, humanize=True) as browser:
        page = await browser.new_page()
        await page.goto("https://www.milanuncios.com/", wait_until="domcontentloaded", timeout=90000)
        await page.wait_for_timeout(7000)
        el=None
        for _ in range(4):
            el = await page.query_selector('a[href*="coches-de-segunda-mano"]')
            if el: break
            await page.wait_for_timeout(2500)
        if el: await el.click()
        else: await page.goto("https://www.milanuncios.com/coches-de-segunda-mano/", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(9000)
        print("title:", await page.title())

        cars = await page.evaluate(r"""() => {
          const cards=[...document.querySelectorAll('article.ma-AdCardV2, article[data-testid="AD_CARD"]')];
          const clean = s => s ? s.replace(/\s+/g,' ').trim() : null;
          return cards.map(c=>{
            const link=c.querySelector('a[href*=".htm"]');
            const txt=c.innerText||'';
            const price=(txt.match(/([\d.]+)\s*€/)||[])[1];
            const km=(txt.match(/([\d.]+)\s*kms?/)||[])[1];
            const year=(txt.match(/\b(19|20)\d{2}\b/)||[])[0];
            const fuel=(txt.match(/\b(diesel|gasolina|h[íi]brido|el[ée]ctrico|gas)\b/i)||[])[0];
            const warranty=(txt.match(/Garant[íi]a\s+\d+\s*meses[^)]*\)/i)||[])[0];
            const titleEl=c.querySelector('h2,h3,[class*="title" i]');
            return {
              title: clean(titleEl?titleEl.textContent:null) || clean((txt.split('\n')[0]||'')),
              price_eur: price, year, km, fuel, warranty,
              url: link?('https://www.milanuncios.com'+link.getAttribute('href').split('?')[0]):null
            };
          }).filter(x=>x.url);
        }""")
        json.dump(cars, open("mn_cars_clean.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"HARVESTED {len(cars)} cars")
        for c in cars[:8]:
            print(f"  {c['title']} | {c['price_eur']}€ | {c['year']} | {c['km']}km | {c['fuel']} | {c['url']}")
        tot = await page.evaluate(r"""() => (document.body.innerText.match(/([\d.]+)\s*anuncios/i)||[])[0]""")
        print("TOTAL:", tot)

asyncio.run(main())
