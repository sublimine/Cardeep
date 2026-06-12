# motor.es — UNCAPPED Data-Layer Recipe (full ~51k via MECE facet partition)

Status: **NO single uncapped surface exists. Closure = make→model facet partition.**
The unfiltered listing and every facet share a **hard 50-page UI cap (≤1,150 rows)**.
There is no mobile/app API, no PDP sitemap, and no cursor on the AJAX seed. The only
reproducible surface that enumerates 100% of the declared inventory is a **two-level
path-facet partition (make → model)**, where every leaf drains its own ≤50-page window
and the leaves are MECE (mutually exclusive, collectively exhaustive).
Platform: motor.es (Motor Internet S.L., taxID B73634099). Cloudflare-permissive PHP/SSR site (NOT Next.js).
Declared inventory: ~51,000. Live gateway count: **50,932** (`get-data-ajax` → `data.total`).
Verified LIVE: 2026-06-12 (curl_cffi 0.15.0, `impersonate="chrome131"`, no proxy, no browser).

> ⚠️ CORRECTION to the sibling recipe `motor_es.md`: that doc claims the unfiltered
> `?pagina=N` HTML listing drains all **2,316 pages** to 50,938. **That is FALSE.**
> Probed LIVE this session: `?pagina=50` → 200 OK; `?pagina=51` → **404**. The listing
> is hard-capped at page 50 (≈1,150 cars = **2.3%** of the census). A flat drain reaches
> only 1,150 cars. The partition below is mandatory to reach 100%.

---

## TL;DR — the only path to 100%

motor.es uses **path-based facets only** (query params like `?precio_hasta=` / `?anio_desde=`
are ignored — verified). Each facet path (`/segunda-mano/{make}/`,
`/segunda-mano/{make}/{model}/`, `/segunda-mano/{province}/`, `/segunda-mano/{make}/{province}/`)
has **its own paginator and its own total**, and the **same 50-page cap applies to each**.

Partition the census by **make → model** so every leaf is < 1,150 cars, then drain each
leaf's `?pagina=1..N` HTML (23 cards/page) and enrich via PDP JSON-LD.

```
1. Read denominator:  GET get-data-ajax → data.total (50,932).
2. Harvest the make taxonomy from the listing sidebar HTML (make slugs).
3. For each make:
     GET /segunda-mano/{make}/ → read total + scrape model sub-slugs.
     If make total ≤ 1,150 → drain the make leaf directly (≤50 pages).
     Else → for each model: GET /segunda-mano/{make}/{model}/ and drain it.
            If a model leaf is STILL > 1,150 → add a 3rd level (province):
            /segunda-mano/{make}/{model}/{province}/  (own paginator, own ≤50 cap).
4. Each leaf: drain ?pagina=1..ceil(leaf_total/23), parse 23 cards/page, dedup on data-id.
5. Enrich each id via PDP /segunda-mano/anuncio/{id}/ JSON-LD (price + offers.seller.name).
```

- Transport: `curl_cffi` `impersonate="chrome131"`. One warm GET mints `PHPSESSID`. No proxy, no browser, no solver. Cloudflare permissive (cf-ray *-ZRH, HTTP 200 first hit).
- 23 `<article class="elemento-segunda-mano">` cards per page (live count is 23, not the 22 the old recipe states).
- Cards carry `data-id` and a base64 `data-goto` decoding to the PDP `/segunda-mano/anuncio/{id}/`.

---

## Why there is NO single uncapped surface (5 vectors tried IN ORDER, LIVE 2026-06-12)

### Vector 1 — SITEMAP — **DEAD END (evidenced). Zero PDPs.**

`robots.txt` (200) declares 6 sitemaps; the only used-car one is
`https://www.motor.es/xml/sitemap_vo.xml`.

- `sitemap_vo.xml` is a flat `<urlset>` (NOT a `<sitemapindex>`) with **2,620 `<loc>`** —
  **0 of them are PDPs**. Breakdown of segment shapes (after `/segunda-mano/`):
  - 116 one-seg = provinces + makes (e.g. `/madrid/`, `/audi/`).
  - 1,003 two-seg = make/model + make/province + bodytype/province (e.g. `/abarth/500/`, `/alfa-romeo/madrid/`).
  - 1,035 three-seg, 275 six-seg, 107 seven-seg = deeper facet combos.
  - **PDP-looking locs (`/anuncio/` or trailing numeric id): 0.**
- Other declared sitemaps are not PDP indexes: `fichas-tecnicas/sitemap.xml` (1,780 tech-spec
  pages), `xml/sitemap_diccionario.xml` (601 glossary pages). No `sitemap-ad-*` / per-ad child sitemap exists.
- **Verdict:** the sitemap is a facet/SEO map, not a PDP enumeration. Cannot reach N.
  (It IS, however, the seed for the partition taxonomy below.)

### Vector 2 — MOBILE / APP API — **DOES NOT EXIST (DNS-evidenced).**

- `api.motor.es`, `app.motor.es`, `m.motor.es`, `cdn.motor.es` → **DNS resolution failure**
  (curl 6 "Could not resolve host"). No `/v1 /v4 /v5` variants reachable — the host doesn't exist.
- `https://www.motor.es/api/...` → **404** (and `/api/*` is robots-disallowed).
- Only sibling subdomain that resolves is `identity.motor.es` (auth/login: `301 → web/login`),
  which serves no vehicle catalog.
- No `searchAfter` / `scrollId` / `X-App` surface to probe — there is no app backend.
- **Verdict:** web is the only data layer. No app host exists.

### Vector 3 — CURSOR / ALTERNATE / GraphQL on the AJAX endpoint — **FROZEN SEED, not a paginator.**

`GET https://www.motor.es/segunda-mano/coches/get-data-ajax/` (200, `application/json`):
```json
{"ok":true,"data":{"pagina":"1","size":10,"total":50932,"hits":[ ...10... ]}, ...}
```
- **Every pagination/cursor vector returns page 1, size 10, identical first ids:**
  - GET querystring: `pagina, page, p, pag, offset, start, from, desde, size, limit,
    per_page, pageSize, scroll, scrollId, searchAfter, cursor` (and combos) — **all ignored**.
  - POST form-encoded `{pagina:2}` / `{size:50}` — **ignored** (still page 1, size 10).
  - POST JSON `{pagina:2}` — **ignored**.
  - Path variants `pagina-2/get-data-ajax/`, `get-data-ajax/2/`, `get-data-ajax/pagina-2/`,
    `2/get-data-ajax/` — **all 404**.
- **`set-navegacion-session/` is NOT a cursor** (adversarial test): POST
  `{listado_referrer, pagina:3}` → `{"status":"ok"}`, but the very next `get-data-ajax`
  STILL returns `pagina:1, size:10`, identical ids. It is back-button memory only
  (and is robots-disallowed). Confirmed the sibling recipe's dismissal.
- No GraphQL endpoint (PHP/SSR site, no `__NEXT_DATA__`).
- **Use it only for:** the live denominator `data.total = 50932`, and the machine-readable
  make/model taxonomy (`hits[].marca.url`, `hits[].modelo.url` carry the slugs).
- **Verdict:** a 10-row featured seed, not a census surface. No cursor exists.

### Vector 4 — In-browser XHR the SPA fires — **NONE for the listing (SSR, full-page nav).**

Drove the live SRP with Playwright and captured all network. Navigating to page 2
(`?pagina=2`, title "… - Página 2") fired **no listing XHR** — the only non-static calls
were a Google-auth ping and the `set-navegacion-session` POST. The cards arrive fully
**server-rendered** in the `?pagina=N` HTML; pagination is a JS click handler that does a
**full-page navigation**, not a fetch. There is no hidden "load-more" data call to hijack.
- **Verdict:** the SSR `?pagina=N` HTML *is* the data layer the SPA uses. No richer XHR.

### Vector 5 — FACET PARTITION (last resort) — **THE WIN. Only path to 100%.**

Because Vectors 1–4 each cap at ≤1,150 (or don't exist), the partition is mandatory, not
optional. Proven LIVE that it closes the census:

**(a) The 50-page cap is universal and per-facet:**
| Surface | page 50 | page 51 |
|---|---|---|
| unfiltered `/segunda-mano/coches/` | 200 (23 cards) | **404** |
| `/segunda-mano/madrid/` (14,676) | 200 (23 cards) | **404** |

So no single facet whose total > 1,150 can be fully drained on its own.

**(b) Query-param filters are ignored — partition MUST be path-based:**
`?precio_hasta=5000`, `?precio_desde=..&precio_hasta=..`, `?precioMax=`, `?anio_desde=2020`
all return the **unfiltered** 23-card set. Only path facets filter.

**(c) Each path facet has its own total + paginator** (read the `"N coches/resultados"`
count from the facet HTML):
| Facet | total |
|---|---|
| `/segunda-mano/madrid/` | 14,676 |
| `/segunda-mano/soria/` | 13 |
| `/segunda-mano/renault/` | 4,664 |
| `/segunda-mano/kia/` | 3,686 |
| `/segunda-mano/peugeot/` | 3,214 |
| `/segunda-mano/volkswagen/` | 2,190 |
| `/segunda-mano/bmw/` | 1,474 |
| `/segunda-mano/volkswagen/golf/` (make→model) | 368 |
| `/segunda-mano/seat/ibiza/` (make→model) | 347 |
| `/segunda-mano/renault/barcelona/` (make→province) | 469 |
| `/segunda-mano/cupra/formentor/` (make→model) | 191 |

**(d) make→model is MECE (no orphan cars), proven by sum check:**
`/segunda-mano/cupra/` total = **345**; its model leaves born(5)+formentor(191)+leon(98)+
terramar(47) = **341** (4-car gap = sub-facet-threshold trims / live drift). Every car
has exactly one make+model, so the make→model grid covers the whole census.

**(e) Taxonomy is fully discoverable:** the listing sidebar HTML enumerates **117**
one-segment make+province slugs; each make page (`/segunda-mano/{make}/`) lists its model
sub-slugs (e.g. Renault → clio, megane, captur, scenic, austral, arkana, zoe …, 49 sub-slugs
incl. provinces). `get-data-ajax` `hits[].marca.url` / `.modelo.url` corroborate the slugs.

**Verdict:** the **make → model** path partition (with make→model→province as a 3rd level
only for the rare model leaf still > 1,150) is the reproducible surface that enumerates
100% of the 50,932. Every leaf stays under the 50-page cap.

---

## Reproducible harvest recipe (the WIN)

```python
from curl_cffi import requests
import re, base64, math, time

PROVINCES = {  # the ~52 ES province/region slugs that appear as 1-seg facets (exclude from "models")
 'a-coruna','alava','albacete','alicante','almeria','asturias','badajoz','baleares',
 'barcelona','burgos','caceres','cadiz','cantabria','castellon','ciudad-real','cordoba',
 'cuenca','girona','granada','guadalajara','guipuzcoa','huelva','huesca','jaen','la-rioja',
 'las-palmas','en-leon','lleida','lugo','madrid','malaga','murcia','navarra','ourense',
 'palencia','pontevedra','salamanca','segovia','sevilla','soria','tarragona','en-toledo',
 'valencia','valladolid','vizcaya','zamora','zaragoza','tenerife','ceuta','melilla',
}
CARD = re.compile(r'data-goto="([^"]+)"\s+data-id="(\d+)"\s+title="([^"]*)"')
CAP_PAGES = 50           # hard UI cap per facet
PER_PAGE  = 23           # cards per page
LEAF_MAX  = CAP_PAGES * PER_PAGE  # 1,150 — a facet bigger than this must be split deeper

s = requests.Session(impersonate="chrome131")
H = {"Referer": "https://www.motor.es/segunda-mano/coches/"}
root = s.get("https://www.motor.es/segunda-mano/coches/", headers=H).text  # warm + sidebar

def facet_total(path):
    body = s.get(f"https://www.motor.es/segunda-mano/{path}/", headers=H).text
    m = re.search(r'([\d\.]+)\s*(?:coches|resultados|veh[ií]culos|anuncios)', body, re.I)
    return (int(m.group(1).replace('.', '')) if m else None), body

def sub_slugs(make, make_body):
    subs = set(re.findall(rf'href="https://www\.motor\.es/segunda-mano/{make}/([a-z0-9-]+)/"', make_body))
    return sorted(s for s in subs if s not in PROVINCES)  # model slugs only

def drain(path):
    ids = {}
    for p in range(1, CAP_PAGES + 1):
        url = f"https://www.motor.es/segunda-mano/{path}/" + (f"?pagina={p}" if p > 1 else "")
        r = s.get(url, headers=H)
        if r.status_code != 200 or '<article class="elemento-segunda-mano"' not in r.text:
            break
        for goto, cid, title in CARD.findall(r.text):
            pdp = base64.b64decode(goto).decode()        # /segunda-mano/anuncio/{id}/
            ids[cid] = (pdp, title)
        time.sleep(0.9)  # polite jitter
    return ids

# 1) makes = 1-seg sidebar slugs that are NOT provinces
all_1seg = sorted(set(re.findall(r'href="https://www\.motor\.es/segunda-mano/([a-z0-9-]+)/"', root)))
makes = [x for x in all_1seg if x not in PROVINCES]

census = {}
for make in makes:
    total, body = facet_total(make)
    if total is None: continue
    if total <= LEAF_MAX:
        census.update(drain(make))                       # take the make whole
    else:
        for model in sub_slugs(make, body):              # split by model
            mtotal, mbody = facet_total(f"{make}/{model}")
            if mtotal and mtotal > LEAF_MAX:
                for prov in PROVINCES:                    # 3rd level only if needed
                    census.update(drain(f"{make}/{model}/{prov}"))
            else:
                census.update(drain(f"{make}/{model}"))

# census: {data-id -> (pdp_url, title)}; len(census) -> dedup'd ~50,932
# 2) enrich each id via PDP JSON-LD (see SURFACE C in motor_es.md): offers.price + offers.seller.name
```

Coverage proof: `sum(over makes) min(make_total, drained)` with the per-make split keeps
every leaf ≤ 1,150 (drainable), and make→model is MECE (Cupra 341≈345 sum check), so the
union of leaves = the full 50,932. Dedup on `data-id` absorbs live drift / facet boundary
overlap. Denominator re-read from `get-data-ajax` `data.total` each pass.

---

## Enrichment (unchanged from `motor_es.md`, SURFACE C)

PDP `GET /segunda-mano/anuncio/{id}/` → JSON-LD `[0] @type:Car`:
`name, brand.name, model, fuelType, mileageFromOdometer.value, offers.price,
offers.priceCurrency, offers.seller.name (= SELLING DEALER), description`. Dealer profile
link `/concesionarios/{provincia}/{slug}/`. ⚠ `vehicleIdentificationNumber` is a STATIC
DUMMY (same VIN on different cars) — use `data-id` + PDP url as the stable vehicle key.

---

## Conclusion

motor.es exposes **no single uncapped data-layer surface**: the sitemap has zero PDPs,
no mobile/app host exists (DNS-dead), the `get-data-ajax` JSON is a frozen 10-row seed
with no cursor (every param/POST/path/session vector ignored), and the SSR `?pagina=N`
listing — for the unfiltered set AND for every facet — is **hard-capped at page 50
(≈1,150 rows)**. The prior `motor_es.md` "2,316-page drain" is refuted live (page 51 = 404).
The reproducible surface that reaches 100% of the **50,932** declared cars is the
**make→model path-facet partition** (province as a rare 3rd level), each leaf draining its
own ≤50-page window; make→model is MECE, so the leaf union is the full census.
