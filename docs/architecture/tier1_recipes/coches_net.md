# coches.net — Tier-1 Harvest Recipe (FREE PATH, no proxy)

Status: HARVESTABLE via FREE path (curl_cffi, no browser, no proxy).
Platform: coches.net (Adevinta / Schibsted Spain Motor).
Declared inventory: ~248k. Live count observed: **272,706 cars** (`meta.totalResults`).
Verified: 2026-06-12.

## TL;DR — the working request

```
POST https://web.gw.coches.net/search
Content-Type: application/json
Accept: application/json, text/plain, */*
Origin: https://www.coches.net
Referer: https://www.coches.net/segunda-mano/
X-Schibsted-Tenant: coches
```

Body (categoryId 2500 = cars; pagination is a NESTED object):

```json
{
  "categoryId": 2500,
  "sortBy": "relevance",
  "sortOrder": "DESC",
  "pagination": { "page": 1, "size": 100 },
  "price": { "from": null, "to": null },
  "year":  { "from": null, "to": null },
  "km":    { "from": null, "to": null }
}
```

Returns HTTP 200 `application/json` with `{ items: [...], meta: { totalPages, totalResults } }`.
`size` up to at least 100 honored. Full inventory = ~2,728 requests at size=100.
Tool: `curl_cffi` `impersonate="chrome131"`. No cookies, no proxy, no JS challenge.

Runner: `scripts/coches_net_harvest.py` (`python scripts/coches_net_harvest.py <page>`).

## The hunt — how the endpoint was found

The intel-declared host `ms-mt--api-web.spain.advgo.net/search` is a **server-side-only
origin** (SSR). It is fronted by CloudFront and is NOT externally resolvable:

```
POST https://ms-mt--api-web.spain.advgo.net/search   -> 502, server: CloudFront,
  body: "CloudFront wasn't able to resolve the origin domain name."
```

This 502 is a DNS/origin error at the CDN edge, not an app rejection. From the browser
the same host throws `TypeError: Failed to fetch` (DNS/CORS). It is unreachable by design.

The SRP `https://www.coches.net/segunda-mano/` (200, server-rendered) embeds the full
state in inline globals (NOT `__NEXT_DATA__`):

- `window.__INITIAL_PROPS__` — contains `initialSearch` (the exact request payload,
  categoryId 2500) and `initialResults` (`items[30]`, `totalResults: 249351`).
- `window.__APP_CONFIG__` — `{hostname: "frontend-coches.mt-pro.motor-internal.com"}`.

The public API host was reconstructed from the JS bundle `https://s.ccdn.es/main.e06139af.js`,
prod config block:

```
API_SUBDOMAIN: "web."
API_DOMAIN:    "gw.coches.net"
```

=> public API base = **`web.gw.coches.net`**. (The `adit.gw.coches.net` "saitama"
gateway in the same bundle is only for ads/display, returns 404 on /search.)

Probing `https://web.gw.coches.net/search` (no trailing slash; the slash variant 404s)
with the `initialSearch` payload returned 200 + real listings.

### Pagination gotcha (root-caused, not papered over)

A top-level `"page"` int is **silently ignored** — pages 1/2/3 returned identical item
sets (100% overlap). The gateway expects pagination as a nested object
`"pagination": {"page": N, "size": M}`. Verified: page1 vs page2 = **0 overlap**;
`size=100` returns 100 items.

## Field map (per item)

`id, title, url, make, makeId, model, modelId, year, km, hp, fuelType, fuelTypeId,
bodyTypeId, transmissionTypeId, environmentalLabel, drivenWheelsId, isProfessional,
isCertified, isFinanced, hasUrge, offerType, phone, hidePhone, contractId, pack,
publishedDate, creationDate, provinceIds, mainProvince, location, resources, warranty`

- `price` (object): `{ amount, taxTypeId, hasTaxes, financedAmount?, financingInfo?{lender,instalment,terms,tae,entry}, priceDropData?{date,amountFromOriginal,percentageFromOriginal}, indicator?{average,rank}, hasReservation }`
- `seller` (object): `{ name, isProfessional, contractId, pack{legacyId,type}, ratings{scoreAverage,commentsNumber} }`  <- dealer attribution
- `location` (object): `{ provinceIds[], regionId, regionLiteral, mainProvince, mainProvinceId, cityId, cityLiteral }`

## Sample real cars pulled (FREE path)

| make / model | price (EUR) | dealer | contract | province |
|---|---|---|---|---|
| TESLA Model S | 29,900 | Movilcar | 77152 | Madrid |
| LAND-ROVER Defender | 53,900 | Movilcar | 77152 | Madrid |
| AUDI A4 | 26,990 | Autos Roso | 123326 | Sta. C. Tenerife |
| RENAULT Trafic | 18,990 | Gestican Automoviles Tenerife | 113652 | Sta. C. Tenerife |
| SEAT Ateca | 19,975 | Gestican Automoviles Tenerife | 113652 | Sta. C. Tenerife |

All `isProfessional: true`, full dealer name + contractId + ratings attached.

## Eight free vectors — outcome log

1. **Internal/open JSON API** — WON. `POST web.gw.coches.net/search` (categoryId 2500,
   nested `pagination`). 200 JSON, 272k cars, dealer attribution. curl_cffi, no proxy.
2. **Mobile app API** — not needed; web gateway already open. (`web.gw.coches.net` is
   the shared Adevinta gateway; the advgo SSR host is internal-only.)
3. **Sitemap of PDPs + JSON-LD** — not needed. (SRP JSON-LD = FAQ + breadcrumb only,
   no listings; the API made this unnecessary.)
4. **curl_cffi chrome131 impersonation** — WON. This is the transport that carries
   vector 1. 200 with no cookie warm-up.
5. **Stealth browser (camoufox/nodriver/etc.)** — not needed. Plain Playwright was used
   only as a *discovery* probe (fetch from page origin to confirm `web.gw.coches.net`);
   the final harvest needs no browser.
6. **BotBrowser/Byparr/FlareSolverr** — not needed; no Akamai/Kasada/DataDome challenge
   on the API host.
7. **Free datacenter proxy rotation** — not needed; no IP wall hit during probing.
8. **Header/cookie/referer warm-up** — minimal headers suffice (`Origin`, `Referer`,
   `X-Schibsted-Tenant: coches`). No session cookie required.

Conclusion: vector 1 (+4 as transport) yields the full inventory for free. Vectors 2,3,5,6,7,8
were unnecessary because the primary free path succeeded.
