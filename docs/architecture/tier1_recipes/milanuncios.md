# TIER-1 RECIPE · Milanuncios (Adevinta Spain)

> Status: **HARVESTABLE via FREE path** (camoufox stealth browser, no proxy, no paid IP).
> Verified 2026-06-12 from a Windows host (non-ES egress) with project python + curl_cffi 0.15.0 + camoufox v135.0.1-beta.24.
> Declared inventory: ~666,901 motor (census). Live SRP counter shows the **10.000-ad display cap** per filtered view.

---

## TL;DR — the working recipe

Milanuncios is double-walled at the HTML edge (Imperva `reese84` "Pardon Our Interruption" on cold
navigation + GeeTest `405` on the raw listing path). **The data layer is NOT a separate JSON/GraphQL
API reachable by curl** — unlike coches.net, milanuncios renders listings **server-side into the SRP
HTML**. The win is a **warm-session stealth browser that navigates IN-PAGE (SPA click), never by cold
`goto`**:

1. Launch **camoufox** (hardened Firefox), `os="windows"`, `locale="es-ES"`, `humanize=True`, `headless=True`.
2. **Warm up** on `https://www.milanuncios.com/` (`domcontentloaded`, wait ~7 s). This mints a valid
   `reese84` cookie and passes the Imperva sensor. The homepage renders fully (title
   `MILANUNCIOS: segunda mano, anuncios gratis...`).
3. **Click the in-page link** `a[href*="coches-de-segunda-mano"]` (an SPA route transition).
   The listing renders un-walled: title `Coches de segunda mano | Milanuncios`.
   > A hard `page.goto("…/coches-de-segunda-mano/")` re-trips the wall. **In-page clicks pass; cold
   > document navigations get "Pardon Our Interruption".** This is the load-bearing trick.
4. **Scroll** (`mouse.wheel`, ~8–15 passes) to lazy-load the virtualized card list (3 → 23 → 42 cards
   on page 1).
5. **Scrape `article.ma-AdCardV2` cards** from the DOM (`page.evaluate`). Each card's `innerText`
   carries make/model, price, year, km, fuel, warranty, location, and the dealer blurb;
   `a[href*=".htm"]` gives the PDP URL.

### Real cars pulled (sample, 2026-06-12)

| Make/model | Price | Year | Km | Fuel | Dealer / location |
|---|---|---|---|---|---|
| MERCEDES-BENZ Citan 1.3 113 96kW Tourer | 33.759 € | 2024 | 62.537 | gasolina | **Cadimar V.I. – Grupo Angal** (concesionario oficial Mercedes-Benz), Jerez de la Frontera (Cádiz) |
| BMW Serie 1 116d | 23.990 € | 2023 | 41.390 | diesel | dealer, Vigo (Pontevedra), garantía 12 m |
| PORSCHE Macan S Diesel | 34.500 € | 2015 | 143.000 | diesel | **VOJJCARS** dealer, Mejorada del Campo (Madrid) |
| NISSAN Pulsar 1.5dCi 110CV Tekna | 6.300 € | 2014 | 212.000 | diesel | — |

A full-scroll page-1 harvest yielded **42 cards** with clean price/year/km/fuel. Artifacts in
`scratch/milanuncios/mn_cars*.json`.

---

## Defense map (verified)

| Surface | Probe | Result |
|---|---|---|
| `GET /` (homepage) | curl_cffi chrome131 | **200 but it is the `reese84` interstitial** — title `Pardon Our Interruption`, loads `/librarym.js` (838 KB, contains `reese84`), `window.onProtectionInitialized`, `reeseSkipExpirationCheck`. Imperva Advanced Bot Protection. |
| `GET /coches-de-segunda-mano/` | curl_cffi chrome131 | **405**, 96 KB body, contains `geetest` + `captcha`. Adevinta `server: bon`. |
| Homepage in vanilla **Playwright MCP** | navigate | **WALLED** (`Pardon Our Interruption`) — non-stealth Chromium is detected even after JS runs; a `reese84` cookie is minted but the sensor flags automation. |
| Homepage in **camoufox** | goto + wait | **PASSES** — real homepage renders. |
| Listing via **camoufox cold `goto`** | goto | **WALLED**. |
| Listing via **camoufox in-page click** (warm) | click | **PASSES** — real SRP, 1.27 MB, 42 cards. |
| PDP (`*.htm`) via **camoufox cold `goto`** (warm cookies) | goto | **WALLED** — PDPs must also be reached by in-page click, not `goto`. |

WAF stack: **Imperva/Incapsula `reese84`** (interstitial + sensor) layered over the **Adevinta `bon`
gateway + GeeTest** on the listing route. Geo-sensitive (non-ES egress trips harder, per census).
Confirmed harvestable from a **non-ES** host with camoufox; `geoip`/ES residential would only harden the cookie.

---

## Why the curl/API path does NOT work for milanuncios (but DOES for coches.net)

The Adevinta family shares ad/telemetry infra (`adit.gw.coches.net`, site code **`ma`** for
milanuncios, `application:"milanuncios"`), **but the vehicle-search gateway is per-tenant and milanuncios
does not expose a browser-callable search JSON API** the way coches.net does:

- coches.net browser calls **`POST https://web.gw.coches.net/search`** (Spring gateway) and it returns
  30 cars/page of JSON. **This works server-side from plain curl_cffi with no proxy** (see the coches.net
  recipe below — it is the canonical "Adevinta recipe").
- The legacy host `ms-mt--api-web.spain.advgo.net/search` is **dead** today: CloudFront `502`
  ("The request could not be satisfied") to curl AND `net::ERR_FAILED` in-browser. The real coches.net
  endpoint migrated to `web.gw.coches.net`.
- `web.gw.coches.net/search` with `x-schibsted-tenant: milanuncios` (and every variant tried: `mn`, `ma`,
  `MILANUNCIOS`, `milanuncios-es`, `motos`, …) → **`403`**. The gateway is tenant-gated to `coches`.
- No milanuncios search-gateway host resolves: `web.gw.milanuncios.com`, `gw.milanuncios.com`,
  `api.milanuncios.com`, `*.advgo.net` variants → **NXDOMAIN**. `mn.gw.coches.net` resolves but
  `/search` → `404`.
- Inside the warmed milanuncios SPA there is **no client-side `/search` XHR** — the listing is
  server-rendered, so there is no JSON endpoint to replay. The data must be scraped from the rendered DOM.

**Conclusion:** milanuncios's free path is the **stealth-browser DOM scrape**, not an API replay.

---

## coches.net "Adevinta recipe" (verified, FREE, curl-only — captured here because it is the shared-infra reference)

```python
from curl_cffi import requests
PAYLOAD = {"categoryId":2500,"page":1,"sortBy":"relevance","sortOrder":"DESC",
           "price":{"from":None,"to":None},"year":{"from":None,"to":None},"km":{"from":None,"to":None}}
r = requests.post("https://web.gw.coches.net/search", impersonate="chrome131", timeout=25,
    json=PAYLOAD,
    headers={"Accept":"application/json","Content-Type":"application/json",
             "x-schibsted-tenant":"coches",
             "Origin":"https://www.coches.net","Referer":"https://www.coches.net/"})
# -> 200, {"items":[...30 cars...],"meta":{}}, NO proxy, NO browser
```

- Endpoint: `POST https://web.gw.coches.net/search` (host resolves to CloudFront 143.204.55.47; origin = Spring Boot gateway).
- **Only required custom header: `x-schibsted-tenant: coches`** (+ standard `Accept`/`Content-Type`/`Origin`/`Referer`). No bearer, no captcha token needed today.
- `categoryId:2500` = cars. Paginate with `"page":N`; `sortBy` ∈ {relevance, price, …}; filters `price/year/km {from,to}`.
- Response field map per ad: `id, title, url, price.amount, km, year, make, model, fuelType, hp,
  seller.{name,isProfessional,contractId,ratings}, isProfessional, location.{provinceIds,cityLiteral},
  resources[].url, publishedDate`. Dealer attribution is first-class (`seller.name`, `isProfessional`).
- Header constant table extracted from `s.ccdn.es/main.*.js` (for completeness — not all needed):
  `X-Adevinta-Channel`, `X-Schibsted-Tenant`, `Captcha-Token`, `Captcha-Origin`, `X-D-token` (Imperva),
  `X-Adevinta-Page-Url`, `X-Adevinta-Referer`, `X-Adevinta-Bearer`.

This recipe drains **coches.net** (and is the template to probe **fotocasa/segundamano** tenants).
It does **not** open milanuncios (tenant-gated 403).

---

## Reproducible milanuncios harvest script

`scratch/milanuncios/camoufox_harvest_final.py` (verified). Core:

```python
import asyncio, json
from camoufox.async_api import AsyncCamoufox

async def main():
    async with AsyncCamoufox(headless=True, os="windows", locale="es-ES",
                             geoip=False, humanize=True) as browser:
        page = await browser.new_page()
        # 1. WARM UP — mint reese84, pass Imperva
        await page.goto("https://www.milanuncios.com/", wait_until="domcontentloaded", timeout=90000)
        await page.wait_for_timeout(7000)
        # 2. IN-PAGE CLICK into the SRP (NOT a cold goto)
        el = None
        for _ in range(4):
            el = await page.query_selector('a[href*="coches-de-segunda-mano"]')
            if el: break
            await page.wait_for_timeout(2500)
        await el.click()
        await page.wait_for_timeout(8000)            # title -> "Coches de segunda mano | Milanuncios"
        # 3. SCROLL to lazy-load the virtualized card list
        last = 0
        for i in range(15):
            await page.mouse.wheel(0, 5000); await page.wait_for_timeout(1100)
            n = await page.evaluate("()=>document.querySelectorAll('article.ma-AdCardV2').length")
            if n == last and i > 4: break
            last = n
        # 4. SCRAPE cards from the DOM
        cars = await page.evaluate(r"""()=>[...document.querySelectorAll('article.ma-AdCardV2')].map(c=>{
            const a=c.querySelector('a[href*=".htm"]'); const t=c.innerText||'';
            return {
              title: (t.split('\n').find(l=>/[A-Za-z]{3,}/.test(l)&&!/Destacado|Precio/.test(l))||'').trim(),
              price_eur:(t.match(/([\d.]+)\s*€/)||[])[1]||null,
              year:(t.match(/\b(19|20)\d{2}\b/)||[])[0]||null,
              km:(t.match(/([\d.]+)\s*kms?/)||[])[1]||null,
              fuel:((t.match(/\b(diesel|gasolina|h[íi]brido|el[ée]ctrico|gas)\b/i)||[])[0]||'').toLowerCase()||null,
              warranty:(t.match(/Garant[íi]a\s+\d+\s*meses[^)]*\)/i)||[])[0]||null,
              url:a?('https://www.milanuncios.com'+a.getAttribute('href').split('?')[0]):null
            };
        }).filter(x=>x.url&&x.price_eur)""")
        json.dump(cars, open("mn_cars_final.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)

asyncio.run(main())
```

### Field map (per `article.ma-AdCardV2`)
- `title` — make + model (skip the `Destacado`/badge line; take first heading line).
- `price_eur` — `([\d.]+)\s*€` (cash price; financed price may co-appear).
- `year`, `km`, `fuel` — from card `innerText`.
- `warranty` — `Garantía N meses` when present (strong dealer signal).
- `location` — `Ciudad (Provincia)` line.
- `url` — `/{make}-de-segunda-mano/{slug}-{adId}.htm`; `adId` is the trailing 6–9 digits.
- Dealer name appears inside the card description blurb (e.g. `Cadimar V.I. - Grupo Angal`,
  `VOJJCARS`); professional ads carry warranty + financing language. PDP would give clean
  `seller`/phone but must be opened by **in-page click**, not `goto`.

### Scaling notes
- **Pagination:** SRP uses `?pg=N` (seen in GA beacons: `…/segunda-mano/?pg=2`). Drive it by clicking the
  pager in-page, or by SPA navigation — keep the warm session; never cold-`goto` a deep page.
- **Display cap:** any single filtered view caps at **10.000 ads**. To reach the full ~667k, **shard the
  query space** (by province `filteredProvinces=`, make, price band, year band) so each shard stays under
  the 10k cap — the standard Adevinta-cap workaround.
- One warmed browser context can paginate + filter for a long session on a single `reese84`; rotate
  context (fresh warm-up) when the cookie ages or the wall reappears.
- Headless camoufox passed here; `headless=False` (or xvfb) and `humanize=True` further reduce wall risk
  under heavy crawling.

---

## The 8 free vectors — exact outcomes

| # | Vector | Outcome |
|---|---|---|
| 1 | Internal/open JSON or GraphQL API | **No browser-callable milanuncios search API exists.** Listing is server-rendered (no client `/search` XHR in the warm SPA). The shared `web.gw.coches.net/search` gateway is **tenant-gated → 403** for every milanuncios tenant string. Legacy `ms-mt--api-web.spain.advgo.net/search` is **dead (CloudFront 502)**. ✗ for milanuncios (✓ for coches.net, documented above). |
| 2 | Mobile app API | No `*.milanuncios.com`/advgo search host resolves (NXDOMAIN on api/gw/search/mt-search subdomains). Shared infra is only ad/telemetry (`adit.gw.coches.net`, site `ma`). No reachable mobile search endpoint found. ✗ |
| 3 | Sitemap of PDPs + JSON-LD/`__NEXT_DATA__` | `robots.txt` empty / no public sitemap. Listing path `405`. PDP JSON-LD exists but PDPs are wall-gated on cold `goto`. SRP has 2 JSON-LD blocks (Breadcrumb + an aggregate `Vehicle count:10000`) — no per-ad array. ✗ as a standalone curl path. |
| 4 | curl_cffi chrome131 (TLS impersonation) | Homepage → reese84 interstitial (`Pardon Our Interruption`). Listing → `405` GeeTest. ✗ (wall not bypassed by TLS alone). |
| 5 | **Stealth browser (camoufox)** | **✓ SUCCESS.** Warm-up passes Imperva; in-page click passes the listing wall; DOM scrape yields real cars (42 on page 1). **This is the working free path.** (Vanilla Playwright MCP = WALLED; camoufox required.) |
| 6 | BotBrowser/Byparr/FlareSolverr-successors | Not needed — camoufox already passes Imperva+GeeTest via warm-up + in-page navigation. Available as fallback for heavier crawl if reese84 hardens. (not exercised) |
| 7 | FREE datacenter proxy rotation (requests-ip-rotator / cloudproxy) | Not needed for the harvest itself (camoufox pulled cars from a single non-ES IP). Would only address IP-rate walls during bulk crawl; the wall here is fingerprint/JS, not IP-rate. (not exercised) |
| 8 | Header/cookie/referer warm-up sequences | **✓ Core of the win.** The reese84 cookie minted on the homepage **plus the in-page (SPA) referer transition** is exactly what unlocks the SRP. Cold navigation with the same cookie still walls — the warm in-page referer is load-bearing. |

**Verdict:** milanuncios is **HARVESTABLE on a FREE path** (vector 5 + vector 8). No paid residential IP
or spend required for the probe; ES residential egress would only further reduce wall risk under bulk load.

---

## Artifacts (scratch/milanuncios/)
- `camoufox_harvest_final.py` — verified end-to-end harvest.
- `mn_cars_final.json` — 42 cars, page 1.
- `mn_cars.json`, `mn_cars_clean.json` — earlier harvests with full dealer blurbs.
- `mn_listing.html` — un-walled SRP (1.27 MB) for offline parsing.
- `coches_642_response.json` — coches.net `web.gw.coches.net/search` 200 response (30 cars, field reference).
- `coches_main.js` — coches.net bundle (header-constant + gateway-host extraction).
