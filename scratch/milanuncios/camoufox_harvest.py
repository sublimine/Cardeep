import asyncio, json
from camoufox.async_api import AsyncCamoufox

async def warm_click(page):
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

async def main():
    async with AsyncCamoufox(headless=True, os="windows", locale="es-ES", geoip=False, humanize=True) as browser:
        page = await browser.new_page()
        await warm_click(page)
        print("listing title:", await page.title())
        cars = await page.evaluate(r"""() => {
          const cards = [...document.querySelectorAll('article[data-testid="AD_CARD"], article.ma-AdCardV2')];
          return cards.map(c => {
            const q = s => { const e=c.querySelector(s); return e ? e.textContent.trim() : null; };
            const link = c.querySelector('a[href]');
            const priceEl = [...c.querySelectorAll('*')].find(e=>/€/.test(e.textContent) && e.children.length===0);
            return {
              title: q('[class*="title" i]') || q('h2') || q('h3'),
              price: priceEl ? priceEl.textContent.trim() : null,
              url: link ? link.getAttribute('href') : null,
              seller: q('[class*="seller" i]') || q('[class*="professional" i]') || q('[class*="Pro" i]'),
              location: q('[class*="location" i]') || q('[class*="province" i]'),
              specs: [...c.querySelectorAll('[class*="detail" i], [class*="attribute" i], [class*="spec" i]')].map(e=>e.textContent.trim()).filter(Boolean).slice(0,6),
            };
          });
        }""")
        # filter to real cars (has url + title)
        cars=[c for c in cars if c.get("url") and c.get("title")]
        json.dump(cars, open("mn_cars.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"\n=== HARVESTED {len(cars)} cars ===")
        for c in cars[:6]:
            print(json.dumps(c, ensure_ascii=False))
        # count total available
        total = await page.evaluate(r"""() => { const m=document.body.innerText.match(/([\d\.]+)\s*(anuncios|resultados|coches)/i); return m?m[0]:null; }""")
        print("\nTOTAL indicator:", total)

asyncio.run(main())
