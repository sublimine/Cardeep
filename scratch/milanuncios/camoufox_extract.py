import asyncio, json
from camoufox.async_api import AsyncCamoufox

async def main():
    async with AsyncCamoufox(headless=True, os="windows", locale="es-ES", geoip=False, humanize=True) as browser:
        page = await browser.new_page()
        await page.goto("https://www.milanuncios.com/", wait_until="networkidle", timeout=90000)
        await page.wait_for_timeout(5000)
        el = await page.query_selector('a[href*="coches-de-segunda-mano"]')
        await el.click()
        await page.wait_for_timeout(8000)
        title = await page.title()
        print("listing title:", title)

        # Extract the initial props object
        props = await page.evaluate("""() => {
            const out = {};
            for (const k of ['__INITIAL_PROPS__','__INITIAL_CONTEXT_VALUE__','__APP_CONFIG__']) {
                try { out[k] = window[k]; } catch(e){ out[k] = '<err '+e+'>'; }
            }
            return out;
        }""")
        json.dump(props, open("mn_initial_props.json","w",encoding="utf-8"), ensure_ascii=False, default=str)
        # find the ads array
        def walk(o, path=""):
            found=[]
            if isinstance(o, dict):
                # heuristic: list of objects each with price+title-ish
                for k,v in o.items():
                    if isinstance(v,list) and v and isinstance(v[0],dict):
                        keys=set(v[0].keys())
                        if keys & {'price','priceInfo','title','adId','id'} and len(v)>=5:
                            found.append((path+"."+k, len(v), list(keys)[:20]))
                    found += walk(v, path+"."+k)
            elif isinstance(o,list):
                for i,v in enumerate(o[:3]):
                    found += walk(v, path+f"[{i}]")
            return found
        hits = walk(props)
        print("\n=== candidate ad arrays ===")
        for p,n,ks in hits:
            print(f"  {p}  (n={n})  keys={ks}")
        # dump APP_CONFIG api host
        ac = props.get("__APP_CONFIG__",{})
        if isinstance(ac,dict):
            print("\n=== APP_CONFIG keys ===", list(ac.keys())[:30])
            for k,v in ac.items():
                if isinstance(v,str) and ("http" in v or "gw." in v or "api" in v.lower()):
                    print(f"   {k} = {v}")

asyncio.run(main())
