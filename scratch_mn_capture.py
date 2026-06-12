"""CARDEEP milanuncios data-layer capture.
Warm up -> in-page click into SRP -> capture ALL network + __NEXT_DATA__.
Goal: find the uncapped SPA data surface (XHR/GraphQL/_next/data) the prior recipe missed.
"""
import asyncio, json, os, re
from camoufox.async_api import AsyncCamoufox

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scratch", "milanuncios")
os.makedirs(OUT, exist_ok=True)

REQS = []          # all requests
JSON_RESP = []     # interesting json/xhr responses (meta only + small bodies)

async def main():
    async with AsyncCamoufox(headless=True, os="windows", locale="es-ES",
                             geoip=False, humanize=True) as browser:
        page = await browser.new_page()

        def on_request(req):
            REQS.append({"method": req.method, "url": req.url,
                         "rtype": req.resource_type})
        page.on("request", on_request)

        async def on_response(resp):
            try:
                ct = resp.headers.get("content-type", "")
                url = resp.url
                rt = resp.request.resource_type
                interesting = (rt in ("xhr", "fetch")) or ("json" in ct) or ("graphql" in url) or ("/api/" in url) or ("_next/data" in url)
                if not interesting:
                    return
                entry = {"url": url, "status": resp.status, "ct": ct, "rtype": rt}
                # capture small JSON bodies that might be the data layer
                if "json" in ct and resp.status == 200:
                    try:
                        body = await resp.body()
                        entry["len"] = len(body)
                        # keep a head sample if it looks like listings
                        head = body[:600].decode("utf-8", "replace")
                        if any(k in head.lower() for k in ("price", "precio", "ad", "listing", "anuncio", "vehicle", "results", "items", "total")):
                            entry["sample"] = head
                    except Exception as e:
                        entry["bodyerr"] = str(e)[:80]
                JSON_RESP.append(entry)
            except Exception:
                pass
        page.on("response", lambda r: asyncio.create_task(on_response(r)))

        # 1. WARM UP
        await page.goto("https://www.milanuncios.com/", wait_until="domcontentloaded", timeout=90000)
        await page.wait_for_timeout(7000)
        title_home = await page.title()
        print("HOME title:", title_home)

        # 2. IN-PAGE CLICK into the SRP
        el = None
        for _ in range(5):
            el = await page.query_selector('a[href*="coches-de-segunda-mano"]')
            if el:
                break
            await page.wait_for_timeout(2500)
        if not el:
            print("!! no SRP link found on homepage")
        else:
            await el.click()
            await page.wait_for_timeout(9000)
        title_srp = await page.title()
        print("SRP title:", title_srp)

        # 3. Scroll a bit to trigger any lazy data fetches (pagination XHR if any)
        for i in range(8):
            await page.mouse.wheel(0, 6000)
            await page.wait_for_timeout(1200)

        # 4. Extract __NEXT_DATA__ / build info / any inline data layer
        next_data = await page.evaluate(r"""() => {
            const out = {};
            const nd = document.getElementById('__NEXT_DATA__');
            out.has_next_data = !!nd;
            if (nd) out.next_data = nd.textContent;
            out.has_apollo = !!window.__APOLLO_STATE__;
            if (window.__APOLLO_STATE__) out.apollo_keys = Object.keys(window.__APOLLO_STATE__).slice(0,40);
            out.has_nuxt = !!window.__NUXT__;
            out.has_initial_state = !!window.__INITIAL_STATE__ || !!window.__PRELOADED_STATE__;
            // scan inline scripts for json-looking blobs with build ids / api urls
            const scripts = [...document.querySelectorAll('script')].map(s=>s.textContent||'').join('\n');
            out.buildId = (scripts.match(/"buildId":"([^"]+)"/)||[])[1] || null;
            out.api_hits = [...new Set((scripts.match(/https?:\/\/[a-z0-9.-]*(gw|api|search|graphql)[a-z0-9.\/-]*/gi)||[]))].slice(0,40);
            out.next_data_endpoints = [...new Set((scripts.match(/\/_next\/data\/[^"']+/g)||[]))].slice(0,10);
            out.card_count = document.querySelectorAll('article.ma-AdCardV2, article[class*="AdCard"]').length;
            // count of ld+json
            out.ldjson = [...document.querySelectorAll('script[type="application/ld+json"]')].map(s=>{
                try { const j = JSON.parse(s.textContent); return j['@type'] || Object.keys(j)[0]; } catch(e){ return 'parse_err'; }
            });
            return out;
        }""")

        # save __NEXT_DATA__ separately if present
        nd_txt = next_data.pop("next_data", None)
        if nd_txt:
            with open(os.path.join(OUT, "next_data.json"), "w", encoding="utf-8") as f:
                f.write(nd_txt)
            # parse top-level structure
            try:
                nd = json.loads(nd_txt)
                next_data["next_data_toplevel_keys"] = list(nd.keys())
                pp = nd.get("props", {}).get("pageProps", {})
                next_data["pageProps_keys"] = list(pp.keys())[:40]
                next_data["buildId_from_nd"] = nd.get("buildId")
                # hunt for ad arrays / totals
                def find_counts(obj, path="", depth=0, acc=None):
                    if acc is None: acc = []
                    if depth > 6: return acc
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if k.lower() in ("total","totalresults","totalcount","numads","numresults","count","resultscount") and isinstance(v,(int,str)):
                                acc.append((path+"/"+k, v))
                            if isinstance(v, list) and v and isinstance(v[0], dict) and len(v) >= 5:
                                acc.append((path+"/"+k+"[list]", len(v)))
                            find_counts(v, path+"/"+k, depth+1, acc)
                    elif isinstance(obj, list):
                        for i, v in enumerate(obj[:3]):
                            find_counts(v, path+f"/[{i}]", depth+1, acc)
                    return acc
                next_data["counts_found"] = find_counts(nd)[:40]
            except Exception as e:
                next_data["nd_parse_err"] = str(e)[:120]

        with open(os.path.join(OUT, "next_data_summary.json"), "w", encoding="utf-8") as f:
            json.dump(next_data, f, ensure_ascii=False, indent=2)
        print("\n=== __NEXT_DATA__ SUMMARY ===")
        print(json.dumps({k: v for k, v in next_data.items() if k != "api_hits"}, ensure_ascii=False, indent=2)[:3000])
        print("API HITS:", next_data.get("api_hits"))

        # save full SRP html for offline grep
        html = await page.content()
        with open(os.path.join(OUT, "srp.html"), "w", encoding="utf-8") as f:
            f.write(html)

    # dump network
    with open(os.path.join(OUT, "network_requests.json"), "w", encoding="utf-8") as f:
        json.dump(REQS, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT, "json_responses.json"), "w", encoding="utf-8") as f:
        json.dump(JSON_RESP, f, ensure_ascii=False, indent=2)

    print("\n=== NETWORK SUMMARY ===")
    print("total requests:", len(REQS))
    hosts = {}
    for r in REQS:
        m = re.match(r"https?://([^/]+)", r["url"])
        h = m.group(1) if m else "?"
        hosts[h] = hosts.get(h, 0) + 1
    for h, c in sorted(hosts.items(), key=lambda x: -x[1]):
        print(f"  {c:>4}  {h}")
    print("\n=== XHR/FETCH/JSON responses (data-layer candidates) ===")
    for e in JSON_RESP:
        flag = " <== SAMPLE" if "sample" in e else ""
        print(f"  {e['status']} {e.get('rtype','?'):<6} len={e.get('len','?')} {e['url'][:130]}{flag}")
    # print samples
    for e in JSON_RESP:
        if "sample" in e:
            print("\n--- SAMPLE", e["url"][:120])
            print(e["sample"][:500])

asyncio.run(main())
