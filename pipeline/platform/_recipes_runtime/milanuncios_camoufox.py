import asyncio, json
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
        # full scroll to load all cards on page 1
        last=0
        for i in range(15):
            await page.mouse.wheel(0,5000); await page.wait_for_timeout(1100)
            n=await page.evaluate("()=>document.querySelectorAll('article.ma-AdCardV2').length")
            if n==last and i>4: break
            last=n
        cars=await page.evaluate(r"""()=>{
          const cln=s=>s?s.replace(/ /g,' ').replace(/\s+/g,' ').trim():null;
          return [...document.querySelectorAll('article.ma-AdCardV2')].map(c=>{
            const a=c.querySelector('a[href*=".htm"]'); const t=c.innerText||'';
            return {
              title: cln((t.split('\n')[0]||'')),
              price_eur:(t.match(/([\d.]+)\s*€/)||[])[1]||null,
              year:(t.match(/\b(19|20)\d{2}\b/)||[])[0]||null,
              km:(t.match(/([\d.]+)\s*kms?/)||[])[1]||null,
              fuel:((t.match(/\b(diesel|gasolina|h[íi]brido|el[ée]ctrico|gas)\b/i)||[])[0]||'').toLowerCase()||null,
              warranty:(t.match(/Garant[íi]a\s+\d+\s*meses[^)]*\)/i)||[])[0]||null,
              url:a?('https://www.milanuncios.com'+a.getAttribute('href').split('?')[0]):null
            };
          }).filter(x=>x.url&&x.price_eur);
        }""")
        json.dump(cars, open("mn_cars_final.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"HARVESTED {len(cars)} cars (page 1, after full scroll)")
        for c in cars[:10]:
            print(f"  {c['title']} | {c['price_eur']} EUR | {c['year']} | {c['km']} km | {c['fuel']}")

asyncio.run(main())
