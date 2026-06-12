"""Capture the REAL filtered-search XHR. SRP is SSR (first page in HTML), so we must
trigger pagination/filter to force the listing XHR. Record ALL POSTs to any gw host."""
import asyncio
import json
from camoufox.async_api import AsyncCamoufox

CAPTURED = []


def interesting(url, method):
    if method != "POST":
        return False
    if "mushroom" in url or "saitama" in url or "collect" in url:
        return False  # tracking/ads noise
    return "coches.net" in url or "advgo" in url or "advl" in url or "mpi-internal" in url


async def main():
    async with AsyncCamoufox(headless=True, humanize=True, locale="es-ES") as browser:
        page = await browser.new_page()

        async def on_request(req):
            if interesting(req.url, req.method):
                try:
                    pd = req.post_data
                except Exception:
                    pd = None
                CAPTURED.append({"url": req.url, "method": req.method,
                                 "headers": dict(req.headers), "post_data": pd})

        page.on("request", on_request)

        await page.goto("https://www.coches.net/madrid/segunda-mano/",
                        wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(4000)
        print("TITLE:", await page.title())

        # Force the listing XHR: scroll to bottom + click "next page" / load more.
        for _ in range(3):
            await page.mouse.wheel(0, 4000)
            await page.wait_for_timeout(1500)

        # Try clicking pagination link to page 2 (forces a fresh search XHR).
        clicked = False
        for sel in ['a[href*="pagina=2"]', 'a[href*="/p2"]', 'a[aria-label*="Siguiente"]',
                    'button:has-text("Siguiente")', '[data-testid*="pagination"] a']:
            try:
                el = await page.query_selector(sel)
                if el:
                    await el.click()
                    clicked = True
                    print("clicked", sel)
                    break
            except Exception:
                pass
        if not clicked:
            # navigate directly to page 2 URL form
            try:
                await page.goto("https://www.coches.net/madrid/segunda-mano/?pagina=2",
                                wait_until="domcontentloaded", timeout=60000)
                print("navigated to pagina=2")
            except Exception as e:
                print("p2 nav warn:", e)
        await page.wait_for_timeout(5000)

    print(f"\n=== {len(CAPTURED)} candidate listing POSTs ===")
    for c in CAPTURED:
        print("URL    :", c["url"])
        print("METHOD :", c["method"])
        if c["post_data"]:
            print("BODY   :", c["post_data"][:1500])
        hdr = {k: v for k, v in c["headers"].items() if k.lower().startswith("x-")
               or k.lower() in ("origin", "referer", "content-type")}
        print("HDRS   :", json.dumps(hdr, ensure_ascii=False))
        print("----")


asyncio.run(main())
