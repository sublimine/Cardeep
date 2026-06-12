# CARDEEP — 00 · The Definitive Tier-1 Platform Registry (Spain)

> Pillar document. The exhaustive, live-verified registry of **every car
> platform / marketplace serving Spain** — the giants, the OEM used-car portals,
> the multi-branch retail chains, the B2B/auction houses, and the niche/regional
> players. For each: real on-site inventory, owner/group, the **full defense
> stack**, the **data-layer surface** to attack (internal API / GraphQL / sitemap
> of PDPs / `__NEXT_DATA__`), the dealer-attribution model, and the verdict
> *free-harvestable-now* vs *needs-residential-proxy*.
>
> The owner demanded **the list of ALL Tier-1 of Spain before any attack**. This
> is that list, and more: it ranks the whole inventory universe and separates
> **TIER-1 (hard defense — own front, `countries/ES/_tier1/`)** from **OPEN**
> absolutely, per the mandate.
>
> **Supersedes** the platform table in `docs/research/SOURCES_ES.md §2` (18 sources,
> snapshot 2026-06-12) — this registry is a fresh live sweep (Chrome-UA fetch +
> WebSearch, 2026-06-12) that **re-derives every counter**, **adds platforms the
> census missed** (Ayvens Carmarket, VGRS, compramostucoche, MB-Certified central
> portal, BMW Premium Selection central, segundamano=Adevinta, Spoticar Direct),
> and **corrects census facts that drifted** (autocasion now exposes GraphQL;
> coches.com counter is 200k not 67k; Flexicar/Autohero now ship JSON-LD; the
> Das WeltAuto census URL now 404s).
>
> Anchor reality (read before designing): `docs/research/SOURCES_ES.md` (census),
> `docs/ARCHITECTURE.md` (data layer: `entity.is_tier1`, `entity.website_waf`,
> `recipe_version`), `docs/architecture/02-SCRAPING-ENGINE.md` (the fetch engine /
> per-defense routing this registry feeds).
>
> Every external claim is `[VERIFIED]` (fetched live this day, Chrome-UA, headers
> read) or `[ASSUMED]` (inferred / vendor-claimed, not re-derived on-site). No
> placeholders, no stubs.

---

## 0. How to read this registry

**Counter drift is law.** Every inventory number for a live platform is a photo of
**2026-06-12**; platform counters move daily. The number is re-derived at harvest
time; here it sets the *rank and the order of attack*, nothing more.

**"Tier-1" is a defense classification, not a size classification.** A platform is
TIER-1 iff it puts a **real bot wall** between us and its data (Akamai sensor,
Cloudflare managed challenge, GeeTest, Imperva active, DataDome). A 700k-listing
giant that serves HTML to a plain Chrome-UA `curl` is **OPEN** and is attacked in
the long-tail engine; a 50k OEM portal behind Akamai is **TIER-1** and lives in
`countries/ES/_tier1/`. This is exactly the `entity.is_tier1` boolean of
`ARCHITECTURE.md` and the per-defense router of `02-SCRAPING-ENGINE.md`.

**The unit of attack is the data-layer surface, not the HTML page.** For each
platform the dossier names the cheapest *structured* surface — an internal search
API (JSON), a GraphQL endpoint, an Elasticsearch faceted query, a sitemap of PDP
URLs, or the `__NEXT_DATA__` / JSON-LD already embedded in the SSR HTML. We never
drain HTML pagination when a JSON surface exists (the lesson of
`02-SCRAPING-ENGINE.md §0`).

**Verification method (this sweep).** A stdlib Chrome-UA client fetched each root
+ listing surface, recording HTTP status, defense headers (`server`, `cf-ray`,
`x-cdn`/`x-iinfo`, `set-cookie`, `via`), challenge bodies on 4xx, the in-body
inventory counter, and data-layer markers (`__NEXT_DATA__`, JSON-LD `@type`,
GraphQL, Algolia, internal `/api/...search` paths). This is a **census fact-check
client, not the production fetcher** — the production engine uses the TLS-impersonating
arsenal of `02-SCRAPING-ENGINE.md` (Scrapling / curl_cffi / camoufox / BotBrowser).
The Chrome-UA probe is deliberately *weak*: anything it gets through is, a fortiori,
trivially OPEN; anything that 403s it may still be OPEN to a real browser fingerprint
and is marked accordingly.

---

## 1. The ranked universe (by live ES inventory)

Inventory = used-car listings actually addressable on the platform serving Spain.
`is_tier1` per the defense classification above. "Free now" = our weak Chrome-UA
probe already retrieved structured data today (so curl_cffi alone will drain it).

| # | Platform | ES inventory (live, 2026-06-12) | Owner / group | Defense (verified) | `is_tier1` | Free now? |
|--:|---|--:|---|---|:--:|:--:|
| 1 | **Wallapop** (Motor) | **~750,000** `[V, census title]` | Wallapop S.L. (Naver-backed) | CloudFront + app-signed API | **TIER-1** | ⚠ API needs device headers |
| 2 | **Milanuncios** | ~666,901 motor (Madrid-scoped partial) `[V census]` | Adevinta Spain | Adevinta `bon` gw + **GeeTest** | **TIER-1** | ✗ needs browser+solver |
| 3 | **AutoScout24.es** | **278,584** `[V mi-curl]` | AutoScout24 AG (Hellman&Friedman) | CloudFront/nginx, **no challenge** | OPEN | ✅ |
| 4 | **coches.net** | **248,648** `[V mi-curl]` | Adevinta Spain | CloudFront + Lambda@Edge (SRP open, sitemap/PDP 405) | **TIER-1** | ⚠ SRP yes, advgo API yes, sitemap no |
| 5 | **coches.com** | **200,388** `[V mi-curl]` | Grupo coches.com (Carossa) | **Imperva** active behind CloudFront (serving today) | **TIER-1** | ⚠ sitemap+PDP yes *for now* |
| 6 | **autocasion.com** | **123,198** `[V mi-curl]` | Grupo Luike / Vocento | Cloudflare (permissive) + **GraphQL** | OPEN | ✅ |
| 7 | **motor.es** | ~50,935 `[V census]` | Motorpress / editorial | Cloudflare (permissive), PDP robots-walled | OPEN | ✅ listings |
| 8 | **Spoticar.es** | ~50,000 claim `[A]` | Stellantis | **Akamai** 403 (homepage+sitemap) | **TIER-1** | ✗ hardest wall |
| 9 | **Flexicar** | **~23,760** real (25k banner) `[V mi-curl]` | Flexicar (Astara-adjacent) | nginx/GCloud, no wall, Next.js+JSON-LD | OPEN | ✅ |
| 10 | **OcasiónPlus** | **~13,676** `[V mi-curl]` | OcasiónPlus | CloudFront/Next.js, no wall | OPEN | ✅ |
| 11 | **Das WeltAuto** | **~7,000** `[A vendor, re-derived]` | VW Group España | central portal serves Chrome-UA; per-dealer subsites | OPEN | ✅ central + subsites |
| 12 | **MB Certified** (ocasion.mercedes-benz.es) | ~4,696 `[A census]` | Mercedes-Benz España | none on probe (Matomo only) | OPEN | ✅ (verify search XHR) |
| 13 | **renew** (Renault/Dacia) | **~5,290** (Re 4,270 + Da 1,020) `[V search]` | Renault Retail Group | CloudFront/nginx, **Elasticsearch facet API** | OPEN | ✅ |
| 14 | **Autohero.es** | **~2,477** `[V mi-curl]` | AUTO1 Group SE | CloudFront, no wall, JSON-LD | OPEN | ✅ |
| 15 | **Clicars** | **~1,600** `[V mi-curl]` | AUTO1 Group SE | Cloudflare (permissive), JSON-LD+AutoDealer | OPEN | ✅ |
| 16 | **Crestanevada** | ~1,000 claim `[A]` | Crestanevada (Granada) | Apache/PHP, no wall, JSON-LD | OPEN | ✅ |
| 17 | **unoauto.com** | ~5,000 claim `[A]` ⚠ stale sitemap | UnoAuto (Valencia) | nginx/PHP, no wall | OPEN | ⚠ validate freshness |
| 18 | **BMW Premium Selection** (central) | per-dealer aggregate `[A]` | BMW Ibérica | none on probe, JSON-LD | OPEN | ✅ central + dealer dir |
| 19 | **Audi Selection:plus** | decentralized per-dealer `[V]` | Audi España / VGRS | per-dealer subsites; central buscador 503 | OPEN | ✅ per-subsite |
| 20 | **VGRS** (vwgroupretail.es) | VW-group used aggregate `[A]` | VW Group Retail Spain | (probe pending) | OPEN | ⚠ verify |
| 21 | **Spoticar Direct** | reconditioned online stock `[A]` | Stellantis | behind Akamai (same as Spoticar) | **TIER-1** | ✗ |
| 22 | **Motorflash** | mid-size aggregator `[A]` | Motorflash | CloudFront, no wall, dealer-keyed sitemaps | OPEN | ✅ (best dealer-discovery) |
| 23 | **compramostucoche.es** | 0 listings (instant-offer tool) `[V]` | AUTO1 Group SE | CloudFront/PHP, no wall | n/a | — sourcing only |
| — | **Ayvens Carmarket** | B2B auction lots (112–500/sale) `[V search]` | Ayvens (SG/ALD) | CloudFront site open; **buy gated to pros** | **TIER-1** | ⚠ catalog readable, buy login |
| — | **BCA España / BCA-Europe** | ~700 veh/week, ~5k "Semana Loca" `[A]` | Constellation Automotive | **Cloudflare 403** managed challenge | **TIER-1** | ✗ |
| — | **Autorola** | ~200k/yr flow, 70k dealers `[A vendor]` | Autorola Group (DK) | CloudFront SPA; **B2B login-gated** | **TIER-1** | ✗ |
| — | **CarNext** | EU remarketing `[A]` | (Constellation/ex-LeasePlan) | **Cloudflare 403** | **TIER-1** | ✗ |

> **Sub-brands rolled up, not double-counted:** OcasiónPlus/Flexicar/Clicars/Autohero/
> Crestanevada are *single-seller retail chains* — their inventory is their own stock,
> not aggregated third-party stock, so it is counted once at the chain. The marketplaces
> (rows 1–7) aggregate the *same physical cars* sold by the dealers the chains and OEM
> portals also list — **the union, not the sum, is the real Spanish stock**; dedup across
> platforms happens at the `vehicle` layer by `(entity, deep_link)` + VIN/ref + photo
> hash (`ARCHITECTURE.md §Inventario`). Ranking here is per-platform addressable count.

### 1.1 The headline strategic reads

1. **The free 1.1M.** Sum of the OPEN, free-now platforms (AS24 278k + autocasion 123k +
   coches.com 200k + motor.es 51k + Flexicar 24k + OcasiónPlus 14k + Das WeltAuto 7k +
   renew 5k + Autohero 2.5k + Clicars 1.6k + Crestanevada 1k + OEM portals) is **>700,000
   listings drainable today with curl_cffi alone, €0 proxies.** That is the F3→F4 prize and
   it dwarfs the Tier-1 walled set in value/effort. **Attack OPEN first.**
2. **AutoScout24 remains the GOLD attribution source** — 278k listings, each PDP carrying
   `AutoDealer` + `PostalAddress` JSON-LD, and (new this sweep) a `__NEXT_DATA__` blob =
   the cleanest dealer→stock map in the country, OPEN. Confirmed entry point of the pipeline.
3. **coches.com counter is 200,388, not ~67k.** The census's 67k was the *VO sitemap PDP
   count*; the live listing counter is 200k. Imperva is active (`x-cdn: Imperva`, `x-iinfo`,
   `incap_ses_` cookie) but **still serving sitemaps + PDPs + `__NEXT_DATA__` to a plain
   Chrome UA today.** This is a *decaying-open* window — harvest before Imperva escalates to
   active challenge. Treat as TIER-1 in code placement (own recipe, watch for the wall) but
   harvest now with the cheap engine.
4. **autocasion exposes GraphQL** (`graphql` marker in body, this sweep) — a structured
   surface the census missed. If the GraphQL schema is introspectable or the SRP query is
   replayable, it beats HTML parsing outright. Highest-priority recipe upgrade.
5. **The Adevinta family is one wall.** coches.net + milanuncios + segundamano + fotocasa all
   sit behind the same Adevinta `bon`/Lambda@Edge stack. `segundamano.es` returned
   `server: bon` this sweep = **it is now an Adevinta gateway, not an independent platform**
   (it historically folded into vibbo/milanuncios). **One Tier-1 recipe, the "Adevinta
   recipe," drains the whole family** via the `ms-mt--api-web.spain.advgo.net/search` POST API.
6. **The OEM "Selection" portals are decentralized.** Audi Selection:plus and Das WeltAuto
   have **no single national stock URL** — stock lives on per-dealer subsites
   (`audiselectionplus.{dealer}.es`, `dasweltauto.{dealer}.es`). This is a *discovery*
   problem (enumerate the dealer subsites) before it is a *harvest* problem. The central MB
   Certified, BMW PS, renew and Spoticar portals **are** national aggregators — different
   topology, different recipe.

---

## 2. Per-platform attack dossiers

Each dossier: **identity → defense (verified) → data-layer surface → dealer attribution →
verdict & recipe seed → residual risk.** Inventory numbers are the 2026-06-12 photo.

---

### TIER-1 — own front (`countries/ES/_tier1/`), separated absolutely

#### T1.1 — Wallapop (Motor)  ·  ~750,000  ·  `is_tier1=true`
- **Identity.** `es.wallapop.com/coches-segunda-mano`. C2C giant + **Wallapop PRO** (4,500+
  professional dealerships). Largest single car count in Spain. Owner Wallapop S.L.
- **Defense `[VERIFIED]`.** CloudFront fronting a **Next.js** app (`/app/search` returns
  `__NEXT_DATA__`, 200 to Chrome UA). `robots.txt` = `Disallow: /` + explicit bot blocklist.
  The **public web shell is open**; the API is the gate.
- **Data-layer surface `[VERIFIED]`.** Two API behaviours observed:
  - `api.wallapop.com/api/v3/cars/search?latitude=&longitude=&distance=&category_ids=100&...`
    → **200 but empty body (122–123 bytes)** even with full geo+pagination params. It exists
    and is reachable but **requires the device/signature headers** Wallapop's app sends
    (`X-DeviceOS`, `X-AppVersion`, `DeviceToken`/MPID, and likely a request signature).
  - `api.wallapop.com/api/v3/search?...` (the *general* search) → **403 CloudFront** ("ERROR
    / request blocked"). Header-gated / signed.
  → The recipe must reproduce the app's header set (capture from a real session) on the
    `cars/search` v3 endpoint, then paginate by geo grid over Spain.
- **Dealer attribution.** Via **Wallapop PRO**: PRO listings carry the dealership identity;
  C2C listings are private sellers (no entity, still inventory). Map PRO sellers → `entity`.
- **Verdict & recipe seed.** TIER-1. Recipe = `cars/search` v3 with captured app headers +
  geo-grid sweep (lat/long tiles covering ES) + per-PRO-seller resolution. Engine: curl_cffi
  with the cloned header profile; escalate to a real device-header capture if signing is enforced.
- **Residual risk `[ASSUMED]`.** If `cars/search` enforces a rotating request signature, this
  becomes a mobile-app reverse-engineering task (capture signing from app traffic). Flag for F5.

#### T1.2 — Milanuncios  ·  ~666,901 motor (partial)  ·  `is_tier1=true`
- **Identity.** `milanuncios.com/coches-de-segunda-mano/`. Massive C2C + dealer. Adevinta Spain.
- **Defense `[VERIFIED census]`.** Adevinta gateway (`server: bon`) + CloudFront + Lambda@Edge.
  Homepage 200 to curl, but the **listing path returns HTTP 405** with a **96 KB GeeTest
  challenge body** (28× `geetest`, recaptcha). **Geo-sensitive** — requests from outside ES
  trip the wall harder. No public sitemap (`robots.txt` empty).
- **Data-layer surface.** Shares the **Adevinta search infra** with coches.net/fotocasa. The
  attack is the **Adevinta internal search API** (see coches.net dossier) + **GeeTest solving**
  or **residential ES proxies** + headless browser for the challenge handshake.
- **Dealer attribution.** Professional sellers carry dealer identity on the ad; mixed with C2C.
- **Verdict & recipe seed.** TIER-1, hardest of the open-ish giants. Recipe = ES-residential
  browser (camoufox/BotBrowser) + GeeTest solver, OR the Adevinta API if the milanuncios
  variant of the advgo endpoint is reachable with a solved token. **Share the "Adevinta recipe."**
- **Residual risk.** GeeTest v4 + geo-gating = needs paid residential ES egress; gate on spend.

#### T1.3 — coches.net  ·  248,648  ·  `is_tier1=true`
- **Identity.** `coches.net/segunda-mano/`. Largest pure-play SP car classifieds with full
  **profesional (dealer) attribution**. Adevinta Spain. `/concesionario/{slug}/` dealer pages.
- **Defense `[VERIFIED]`.** CloudFront + Lambda@Edge bot wall (`LambdaGeneratedResponse`).
  **SRP (`/segunda-mano/`) returns 200 to Chrome UA** (counter 248,648 in body), but the
  **sitemap-index path and detail `.aspx` pages return HTTP 405** with a JS challenge body
  (geetest/hcaptcha/recaptcha). JSON-LD on SRP present but listing JSON not exposed inline.
- **Data-layer surface `[VERIFIED census]`.** The **gold surface is the internal search API**:
  `ms-mt--api-web.spain.advgo.net/search` (**POST JSON**; returns 502 on malformed probe =
  endpoint exists). This is the same Adevinta API milanuncios/fotocasa use. Replaying its
  POST payload (filters, pagination, sort) yields structured listings **without touching the
  405-walled sitemap/PDP**. This is the canonical "attack the data layer, not HTML" win.
- **Dealer attribution.** Strong — `/concesionario(s)/*` dealer directory + per-listing
  profesional. Map to `entity` directly.
- **Verdict & recipe seed.** TIER-1. Recipe = POST to `…advgo.net/search` with the captured
  web payload + correct headers (curl_cffi TLS); fall back to camoufox for token bootstrap if
  the API requires a session cookie minted by the JS challenge. **The Adevinta recipe.**
- **Residual risk.** If advgo enforces a Lambda@Edge-minted token, bootstrap it with one
  browser hit per session, then drain by API.

#### T1.4 — coches.com  ·  200,388  ·  `is_tier1=true` (decaying-open)
- **Identity.** `coches.com/coches-segunda-mano/`. Dealer-sourced VO+VN aggregator. Carossa group.
- **Defense `[VERIFIED]`.** **Imperva/Incapsula active** (`x-cdn: Imperva`, `x-iinfo`,
  `incap_ses_*`/`visid_incap_*` cookies) behind CloudFront — **but currently serving sitemaps,
  PDPs, and `__NEXT_DATA__` to a plain Chrome UA.** `robots.txt: Disallow /`.
- **Data-layer surface `[VERIFIED]`.** Three usable surfaces, all live today:
  - **`__NEXT_DATA__`** in SRP HTML (Next.js) — listing JSON inline.
  - **Public sitemap index** `sitemap.xml → vn.xml / vo.xml / renting.xml → Todo-VO-{0..n}.xml`
    = direct PDP URLs with `?id=` (the census's ~67k figure was *this* sitemap's URL count).
  - **PDP JSON-LD** (`Car/Offer/Product/Brand/Place`) with dealer attribution.
- **Dealer attribution.** Present (`Place` + dealer name on PDP).
- **Verdict & recipe seed.** TIER-1 in code placement (Imperva can flip to active challenge
  any day) but **harvest NOW with the cheap engine** (curl_cffi). Recipe = sitemap walk →
  PDP JSON-LD, or `__NEXT_DATA__` off the SRP. Set a `source_health` tripwire on the first
  Imperva 403 so the engine auto-escalates to camoufox.
- **Residual risk.** Imperva escalation. The whole value is in harvesting before the window closes.

#### T1.5 — Spoticar.es + Spoticar Direct  ·  ~50,000 claim  ·  `is_tier1=true`
- **Identity.** `spoticar.es/comprar-coches-de-ocasion`. Stellantis multi-brand official-used
  network (Peugeot/Citroën/Opel/DS/Fiat/Jeep), **200+ sales points**, each unit tied to an
  official Stellantis dealer → **highest-quality dealer attribution** of the OEM portals.
  **Spoticar Direct** = newer national reconditioned-online stock (same infra/wall).
- **Defense `[VERIFIED]`.** **AkamaiGHost → HTTP 403 "Access Denied"** on homepage, listing
  path *and* `/sitemap.xml` to plain curl — blocks before any content. The hardest wall in the
  census. `robots.txt` empty.
- **Data-layer surface `[ASSUMED]`.** Behind Akamai there is an internal stock API the SPA calls
  (Stellantis "phygital" stack). Capture it from a real browser session; do not expect HTML.
- **Dealer attribution.** Best-in-class — each car → named Stellantis official dealer.
- **Verdict & recipe seed.** TIER-1, top of the hard-wall queue. Recipe = full-fingerprint
  browser (BotBrowser) + **Akamai sensor data** (residential ES proxy), capture the SPA's
  stock XHR, then replay. Gate on spend.
- **Residual risk.** Akamai Bot Manager Premier = needs the paid sensor; F5 spend-gated only.

#### T1.6 — Ayvens Carmarket  ·  B2B auction (112–500 veh/sale)  ·  `is_tier1=true`
- **Identity.** `carmarket.ayvens.com/es-es/`. Ayvens (Société Générale / ex-ALD+LeasePlan)
  online **B2B remarketing** of ex-renting/fleet vehicles. "A car sold every minute, >2M sold."
- **Defense `[VERIFIED]`.** Public marketing/catalog pages serve 200 to Chrome UA (CloudFront +
  JSON-LD); **per-sale lot pages exist at `…/sales/{id}/`** and country filter
  `…/country/spain/`. **Buying is gated to vetted professionals (login).**
- **Data-layer surface `[VERIFIED partial]`.** The **sale-calendar + lot catalog is partially
  public** (`/sales/{id}/` enumerate "N vehículos" per lot). The full per-vehicle expertise
  data is behind the trade login.
- **Dealer attribution.** Seller = fleet/leasing co (Ayvens itself + financial partners), not a
  retail dealer. Models as a `plataforma`/B2B entity, vehicles flagged `channel=auction`.
- **Verdict & recipe seed.** TIER-1 (auction subclass). Recipe = crawl the public sale calendar
  + lot pages for the *catalog* (make/model/km/expertise summary); full bid/price needs a pro
  account (out of free scope, flag as **needs B2B credentials**).
- **Residual risk.** Auction data is ephemeral (lots open/close); snapshot cadence must match
  sale windows. Legal: B2B ToS for professional buyers.

#### T1.7 — BCA España / BCA-Europe  ·  ~700/week, ~5k peak  ·  `is_tier1=true`
- **Identity.** `bca.com/es/`, `es.bca-europe.com/`. Constellation Automotive Group (No.1 EU
  remarketing, 1.8M veh/yr). 4 physical centres (Azuqueca, Bellvei, La Luisiana, Alicante).
- **Defense `[VERIFIED]`.** **Cloudflare managed-challenge 403** ("Attention Required!") on
  both `bca.com/es/` and `es.bca-europe.com/` to Chrome UA + `__cf_bm` cookie. Hard wall.
- **Data-layer surface `[ASSUMED]`.** The buyer catalog (`/buyer/facetedSearch/salecalendar`)
  is behind the CF challenge *and* a buyer login. Internal faceted-search JSON API exists.
- **Dealer attribution.** Seller = fleet/OEM/captive finance; auction channel.
- **Verdict & recipe seed.** TIER-1 (auction). Recipe = camoufox/BotBrowser to pass CF managed
  challenge + **buyer account** for the catalog API. **Needs B2B credentials**; free-now = ✗.
- **Residual risk.** Login-gated B2B; treat as credentials-required, low priority vs OPEN giants.

#### T1.8 — Autorola  ·  ~200k/yr flow, 70k dealers  ·  `is_tier1=true`
- **Identity.** `autorola.es`. Danish online remarketing leader; ex-renting/fleet/finance stock.
- **Defense `[VERIFIED]`.** Root + `/business/index` + `/buyer/index` serve a **CloudFront/S3
  SPA shell (200, ~19 KB, no counter, no data-layer markers)** — the data is entirely behind
  a **B2B login**. Not a public wall; a login wall.
- **Data-layer surface `[ASSUMED]`.** Authenticated internal API after dealer login.
- **Verdict & recipe seed.** TIER-1 (auction, login-gated). **Needs B2B credentials.** Free-now ✗.
  Low priority for the public index; high value only if a dealer account is provisioned.

#### T1.9 — CarNext  ·  EU remarketing  ·  `is_tier1=true`
- **Identity.** `carnext.com/es-es/`. Pan-EU used/remarketing (Constellation orbit, ex-LeasePlan).
- **Defense `[VERIFIED]`.** **Cloudflare 403** managed challenge to Chrome UA. ES catalog depth
  uncertain (may be thin/redirecting post-consolidation — confess gap, see §3).
- **Verdict.** TIER-1, low ES priority until catalog depth confirmed. Free-now ✗.

---

### OPEN — long-tail engine (`countries/ES/recipes/`), curl_cffi-class

#### O.1 — AutoScout24.es  ·  278,584  ·  OPEN  ·  **GOLD**
- **Identity.** `autoscout24.es/lst`. Pan-EU marketplace, ES inventory dealer-dominated.
- **Defense `[VERIFIED]`.** nginx + CloudFront, **no DataDome/Akamai/challenge**. `/lst` returns
  full SSR HTML to plain Chrome UA (619 KB). `robots.txt` permits listing pages. Gates only on
  the *Anthropic UA string* — any Chrome UA passes (`SOURCES_ES.md §2.1`).
- **Data-layer surface `[VERIFIED]`.** Three, all inline in the SSR HTML: **`__NEXT_DATA__`**
  (Next.js — listing + dealer JSON), **JSON-LD** (3 blocks: `Car/Product/Offer/Organization/
  PostalAddress`), and the `numberOfResults` counter (278,584 this sweep). **No `sitemap.xml`
  (404)** — crawl via `/lst` pagination + `/anuncios/{slug}` PDPs, *but prefer parsing
  `__NEXT_DATA__` off each SRP page over scraping rendered HTML.*
- **Dealer attribution.** **Strongest in the country** — every PDP carries dealer `Organization`
  + `PostalAddress` (62 `dealer` refs/PDP). This is the primary dealer→stock map.
- **Verdict & recipe seed.** OPEN, **F3 entry point** (already chosen in `SOURCES_ES.md §9`).
  Recipe = curl_cffi → `/lst?...&page=N` → parse `__NEXT_DATA__` → emit (dealer, vehicles).
  Handle the live-set-shifts-across-pages hazard (`02-SCRAPING-ENGINE.md §0`) via stable sort
  + dedup by listing id, not page position.
- **Residual risk.** Pagination instability on a live set (mitigated by id-dedup). Best value/effort.

#### O.2 — autocasion.com  ·  123,198  ·  OPEN  ·  **GraphQL**
- **Identity.** `autocasion.com/coches-segunda-mano`. Dealer-focused classifieds. Grupo Luike/Vocento.
- **Defense `[VERIFIED]`.** Cloudflare (`server: cloudflare`, `cf-ray`, `cf-cache-status DYNAMIC`)
  **currently passing plain Chrome UA, no JS challenge**. `robots.txt: Disallow /` yet declares
  two sitemaps (`actualidad/sitemap_index.xml`, `uploads/sitemap.xml`).
- **Data-layer surface `[VERIFIED]`.** **GraphQL marker present in body this sweep** — a
  structured query surface the census missed. Plus PDP JSON-LD (`Car/Offer/Product/PostalAddress/
  EngineSpecification/Brand`, 58 `dealer`/30 `profesional` markers). PDP pattern
  `/coches-segunda-mano/{marca}-ocasion/{slug}-ref{ID}`.
- **Dealer attribution.** Strong (profesional + PostalAddress).
- **Verdict & recipe seed.** OPEN, high priority. **Recipe upgrade = probe the GraphQL endpoint**
  (introspect schema / replay the SRP query) — if replayable it beats HTML+JSON-LD parsing.
  Fallback = JSON-LD off PDPs reached via the declared sitemaps. Engine: curl_cffi.
- **Residual risk.** Cloudflare hardening; GraphQL may require an auth token or persisted-query id.

#### O.3 — motor.es  ·  50,935  ·  OPEN (listings only)
- **Identity.** `motor.es/segunda-mano/coches/`. Editorial-site classifieds aggregator. Next.js.
- **Defense `[VERIFIED]`.** Cloudflare (`cf-cache-status BYPASS`), passing Chrome UA. **`robots.txt
  disallows `/vercoche/*`** (the actual PDP path) — PDPs are robots-walled; *listing pages are
  crawlable*. Declared `sitemap_vo.xml` holds only 2,620 SEO category/province URLs, **not PDPs**.
- **Data-layer surface `[VERIFIED]`.** JSON-LD on listing pages; PDP detail is robots-disallowed
  (respect it or treat as grey-zone). Listing-level harvest only.
- **Dealer attribution.** Present on listings (aggregator of dealer inventory). Useful **cross-
  reference for dealer coverage** more than a primary stock source.
- **Verdict & recipe seed.** OPEN (listings). Recipe = listing-page JSON-LD walk; **do not crawl
  `/vercoche/` (robots).** Engine: curl_cffi. Secondary value (cross-check).

#### O.4 — Flexicar  ·  ~23,760  ·  OPEN (chain, single-seller)
- **Identity.** `flexicar.es/coches-segunda-mano/`. National used-car franchise (**175+ stores**,
  60k+ veh/yr ES+PT, €1.1B 2025). Own/franchise stock.
- **Defense `[VERIFIED]`.** nginx + Google Cloud, Next.js (`x-nextjs-cache`), **no wall.** Counter
  25.000 banner / **23.760 real** this sweep. **JSON-LD now present** (census said none — site
  re-platformed). PDPs `/coches-ocasion/{slug}_{id}/`; sitemap dominated by SEO landing pages.
- **Data-layer surface `[VERIFIED]`.** `__NEXT_DATA__` + JSON-LD inline. Parse the Next.js data,
  not the SEO sitemap.
- **Dealer attribution.** Mono-chain (Flexicar), per-store location in PDP → 175+ entities.
- **Verdict & recipe seed.** OPEN. Recipe = `__NEXT_DATA__` off SRP + per-store mapping. curl_cffi.

#### O.5 — OcasiónPlus  ·  ~13,676  ·  OPEN (chain)
- **Identity.** `ocasionplus.com/coches-segunda-mano`. National used-car retailer, **~120 stores**.
- **Defense `[VERIFIED]`.** CloudFront + Next.js, **no wall**. Counter 13.676 this sweep. JSON-LD
  present. Rich `sitemap.xml` = 263 child sitemaps (per-brand + per-province) enumerating real
  PDPs `/coches-segunda-mano/{slug}-{km}km-{year}-{id}`.
- **Data-layer surface `[VERIFIED]`.** Sitemap → PDP JSON-LD (`Product/Organization/ContactPoint`).
- **Dealer attribution.** Mono-chain (OcasiónPlus). Seller = OcasiónPlus.
- **Verdict & recipe seed.** OPEN. Recipe = sitemap walk → PDP JSON-LD. curl_cffi.

#### O.6 — Das WeltAuto  ·  ~7,000  ·  OPEN (OEM network, hybrid topology)
- **Identity.** `dasweltauto.es`. VW Group official used network (VW/SEAT/Škoda/Cupra/VWCV).
  Also surfaces as `volkswagen.es/.../approved.html` (VW Approved).
- **Defense `[VERIFIED]`.** **Census URL `/esp/buscar-coches-de-ocasion.html` now 404s** — the
  path rotated. **Root `dasweltauto.es/` serves 200 to Chrome UA** (Symfony PHP, `symfony`
  session cookie). Current listing path = `/esp/coches-ocasion`. Search results JS-rendered.
- **Data-layer surface `[VERIFIED/ASSUMED]`.** Central portal = a BFF the SPA calls (census noted
  `gsl.feature-app.io` BFF for the real stock; the `/provincia/` pages are SEO doorways, NOT SSR
  listings). **Plus per-dealer subsites `dasweltauto.{dealer}.es`** (e.g. `dasweltauto.leioawagen.es`)
  with their own `/coches-buscador-avanzado` — a *decentralized* second surface.
- **Dealer attribution.** By VW-network dealer (subsite = dealer identity).
- **Verdict & recipe seed.** OPEN but **two-topology**: (a) central portal → capture the
  `feature-app.io`/BFF stock XHR; (b) **enumerate per-dealer subsites** (discovery via VW dealer
  locator / `concesionarios.seat`) → harvest each. Don't confuse the SEO doorway with data.
- **Residual risk.** BFF param discovery; subsite enumeration completeness.

#### O.7 — renew (Renault / Dacia)  ·  ~5,290  ·  OPEN  ·  **Elasticsearch facets**
- **Identity.** `es.renew.auto`. Renault Retail Group official used (Renault 4,270 + Dacia 1,020).
- **Defense `[VERIFIED]`.** nginx + CloudFront, **no wall**, JSON-LD. Listings show dealer name
  (e.g. "AUTOSAE, S.A.U (ARANJUEZ)", "GABELLA MOTOR, S.L.").
- **Data-layer surface `[VERIFIED]`.** **Faceted query params are raw Elasticsearch fields** —
  `/vehiculos.html?brand.label.raw=DACIA&model.label.raw=SANDERO` etc. → the SRP is backed by an
  **Elasticsearch index queryable by URL facets**; the `productId` PDP pattern is
  `/vehiculos/detalle.html?productId=VEH_{id}_{plate}`. This is a clean, faceted JSON surface.
- **Dealer attribution.** **Strong** — dealer name + location per listing → Renault/Dacia network.
- **Verdict & recipe seed.** OPEN, high-quality. Recipe = drive the faceted `/vehiculos.html`
  endpoint (paginate facets) → PDP. curl_cffi. Excellent dealer-attribution OEM source.

#### O.8 — Autohero.es  ·  ~2,477  ·  OPEN (AUTO1 retail)
- **Identity.** `autohero.com/es/search/`. AUTO1 Group online used retailer, own reconditioned stock.
- **Defense `[VERIFIED]`.** CloudFront, **no wall**. Counter 2.477 / 3.000-banner this sweep.
  **JSON-LD now present** (census said thin SPA). PDPs `/es/details/{slug}` (client-rendered) +
  internal search API.
- **Data-layer surface `[VERIFIED/ASSUMED]`.** JSON-LD inline + AUTO1 internal search API the SPA
  calls. Sitemap thin (SEO). Prefer the internal API or JSON-LD.
- **Dealer attribution.** Mono-seller (Autohero/AUTO1).
- **Verdict & recipe seed.** OPEN. Recipe = internal search API capture or JSON-LD. curl_cffi.

#### O.9 — Clicars  ·  ~1,600  ·  OPEN (AUTO1 retail)
- **Identity.** `clicars.com/coches-segunda-mano-ocasion`. AUTO1 online used retailer, ~1,100 cars
  on a 40,000 m² Madrid site. Counter 1.595–1.604 this sweep.
- **Defense `[VERIFIED]`.** Cloudflare (`cf-cache-status DYNAMIC`) **passing Chrome UA**; PDPs +
  sitemap serve. `robots.txt` sitemap 302→`storage.googleapis.com/clicars-storage-prod-public/`
  (9,043 URLs are model/version SEO pages, **not** 9k live units — real stock ~1,600).
- **Data-layer surface `[VERIFIED]`.** Rich PDP JSON-LD (**4 blocks incl `AutoDealer` +
  `PostalAddress` + `AggregateRating`**). Best JSON-LD of the chains.
- **Dealer attribution.** Mono-seller (Clicars) but emits `AutoDealer` cleanly.
- **Verdict & recipe seed.** OPEN. Recipe = live-listing crawl → PDP JSON-LD (ignore SEO sitemap
  inflation). curl_cffi.

#### O.10 — MB Certified  ·  ~4,696  ·  OPEN (OEM central portal)
- **Identity.** `ocasion.mercedes-benz.es` (central) + `…/vehiclesearch`. Mercedes-Benz España
  official used. Distinct from per-dealer MB sites (`mercedesocasion.com`, `mobilityocasion.com`…).
- **Defense `[VERIFIED]`.** Root 200 to Chrome UA, **no wall** (Matomo `_pk_` cookies only).
- **Data-layer surface `[ASSUMED]`.** `/vehiclesearch` SPA → internal stock API (capture XHR).
- **Dealer attribution.** Per MB official dealer (network).
- **Verdict & recipe seed.** OPEN. Recipe = capture `/vehiclesearch` stock XHR → replay. curl_cffi.

#### O.11 — BMW Premium Selection (central)  ·  per-dealer aggregate  ·  OPEN
- **Identity.** `bmwpremiumselection.es` + `/concesionarios/` dealer directory. BMW Ibérica.
- **Defense `[VERIFIED]`.** 200 to Chrome UA, **no wall**, JSON-LD present.
- **Data-layer surface `[ASSUMED]`.** Central buscador + dealer directory; stock likely aggregated
  via a search API, with per-dealer BMW PS subsites (e.g. `bmwocasionbarcelona.com/bmwpremiumselection`)
  as a second surface (QUADIS etc.).
- **Dealer attribution.** Doubles as a **dealer list** (`/concesionarios/`).
- **Verdict & recipe seed.** OPEN. Recipe = central search API + dealer-directory enumeration.

#### O.12 — Audi Selection:plus  ·  decentralized  ·  OPEN (per-dealer)
- **Identity.** Audi España official used. **No single national stock URL** — central
  `audi.es/.../buscador-de-stock-de-ocasion/` returned **503** this sweep (unstable SPA). Stock
  lives on **per-dealer subsites** `audiselectionplus.{dealer}.es` (Madrid, Barcelona, Levante,
  Leioa, Sevilla Wagen…) and the VGRS portal (O.13).
- **Defense `[VERIFIED]`.** Central buscador 503; per-dealer subsites serve normally.
- **Data-layer surface `[ASSUMED]`.** Each subsite `/buscador` + `/coches-de-ocasion` → HTML/JSON.
- **Dealer attribution.** Subsite = dealer.
- **Verdict & recipe seed.** OPEN, **discovery-first**: enumerate `audiselectionplus.*` subsites
  (from Audi dealer locator) → harvest each. Per-dealer recipe family.

#### O.13 — VGRS (vwgroupretail.es / exclusive.vwgroupretail.es)  ·  VW-group used  ·  OPEN `[verify]`
- **Identity.** VW Group Retail Spain's own used-stock portal aggregating Audi/VW/SEAT used
  (`/coches-ocasion/audi`, `exclusive.vwgroupretail.es/ocasion-audi-selection-plus/`). New find
  this sweep (not in census).
- **Defense `[ASSUMED]`.** Probe pending — treat OPEN until shown otherwise.
- **Verdict.** OPEN candidate; **verify counter + data-layer in F3 recon** (confessed gap §3).

#### O.14 — Crestanevada  ·  ~1,000  ·  OPEN (single dealer group)
- **Identity.** `crestanevada.es/coches-segunda-mano`. Large single used-car group (Granada,
  multi-site). €46.9M.
- **Defense `[VERIFIED]`.** Apache/2.4 + PHP, **no wall**, `ci_session` cookie, JSON-LD present
  (census said none — re-checked, JSON-LD now in body). `sitemap.xml` 4,791 URLs (mostly
  city/brand landing pages).
- **Data-layer surface `[VERIFIED]`.** JSON-LD inline; PDP deeper than landing pages.
- **Verdict & recipe seed.** OPEN, low strategic value (one group) but clean direct stock. curl_cffi.

#### O.15 — unoauto.com  ·  ~5,000 claim  ·  OPEN ⚠ stale
- **Identity.** `unoauto.com`. Regional used retailer (Valencia), own stock.
- **Defense `[VERIFIED census]`.** nginx + PHP/8.3, **no wall**. `product.xml` sitemap (5,820
  `/oferta/{slug}-ref{ID}`) **but sampled PDPs returned 404 — sitemap stale/path rotated.**
- **Verdict & recipe seed.** OPEN but **validate freshness before bulk crawl**. Low priority.

#### O.16 — Motorflash  ·  mid-size aggregator  ·  OPEN  ·  **best dealer-discovery**
- **Identity.** `motorflash.com/coches-segunda-mano/`. Dealer-inventory aggregator that **powers
  many OEM microsites** (Audi Selection:plus dealer sites, H-Promise pages run on Motorflash).
- **Defense `[VERIFIED census]`.** CloudFront, 200 to curl, **no wall**.
- **Data-layer surface `[VERIFIED census]`.** **Segmented sitemaps keyed by dealer**:
  `sitemap.concesionarios.xml` (dealer pages `/concesionario/{name}/coches-segunda-mano/{id}/`),
  `.segunda-mano.xml`, `.km0.xml`, `.seminuevos.xml`, `.nuevos.xml`, `.industriales.xml`.
- **Dealer attribution.** **Explicit named-dealer directory** — strongest *dealer-discovery*
  source among aggregators (maps units → named dealerships directly).
- **Verdict & recipe seed.** OPEN. Recipe = walk `sitemap.concesionarios.xml` for the dealer
  census + per-dealer stock pages. **Use early as a dealer-discovery multiplier.** curl_cffi.

#### O.17 — compramostucoche.es  ·  0 listings  ·  sourcing-only
- **Identity.** `compramostucoche.es`. AUTO1 Group **instant-offer / buy-your-car** tool.
- **Defense `[VERIFIED]`.** CloudFront/PHP, 200, no wall — **but no public listings** (it *buys*
  cars; the stock resurfaces on Autohero/Clicars/AUTO1 B2B).
- **Verdict.** Not a POS marketplace. Value = **supply signal** (which cars enter the AUTO1
  funnel) + their store directory as a lead list. Exclude from inventory; note in entity sourcing.

---

## 3. Confessed gaps & honest residue (no makeup)

1. **Wallapop API signing `[OPEN QUESTION]`.** `cars/search` v3 returns 200-but-empty without app
   headers; whether it enforces a *rotating signature* (vs just static headers) is unconfirmed.
   If signed → mobile-app RE task. **Must be settled before sizing the Wallapop harvest.**
2. **VGRS (O.13) not yet probed.** Found via search this sweep; counter + defense + data-layer
   unverified. Probe in F3 recon. May overlap entirely with Audi Selection:plus + Das WeltAuto.
3. **CarNext ES depth `[OPEN]`.** Cloudflare-403'd; post-consolidation the ES catalog may be thin
   or redirecting into Ayvens/BCA. Confirm it is a live ES platform vs a redirect before investing.
4. **OEM portal stock totals are mostly `[ASSUMED]`** (Spoticar ~50k, Das WeltAuto ~7k, MB ~4.7k,
   BMW PS aggregate) — re-derive on-site when the recipe lands. Only renew (5,290), Hyundai
   Promise (420 `[V]`), Flexicar (23,760), OcasiónPlus (13,676), Autohero (2,477), Clicars (1,600)
   were counter-verified live this sweep.
5. **Per-dealer OEM subsite enumeration is incomplete.** Audi Selection:plus, Das WeltAuto, BMW PS
   each fan out to dozens of per-dealer subsites; the *full list* of subsites is a discovery task
   (dealer locators + `motorflash.concesionarios` sitemap) not yet enumerated here.
6. **Hyundai Promise** (`hyundai.es/seminuevos/`, 420 veh `[V]`), **Nissan Ocasión**, **Toyota/Lexus
   Selected**, **Kia**, **Ford/Opel** official used portals exist but each lives at an OEM-specific
   path (my guessed URLs 404'd); they belong to the **OEM modality** of `SOURCES_ES.md §3.3`
   (entity/dealer-discovery layer) more than the Tier-1 *platform* pillar. Catalogued there; listed
   here for completeness. **Hyundai Promise verified OPEN (CloudFront, 420 counter).**
7. **Facebook Marketplace** is a real ES car-sales channel by volume but has **no public structured
   surface** (login + GraphQL behind Meta's wall + ToS prohibition). Out of scope as a harvest
   target; flagged as a known-uncovered channel, not a gap in *this* registry's method.
8. **Niche/dead, confirmed `[VERIFIED]`:** `heycar.com/es` = DEAD ("heycar dice adiós", 0 ES stock);
   `gocar.es` = parked domain; `segundamano.es` = folded into Adevinta (`server: bon`, not
   independent); `nettiauto` = Finnish, marginal ES; `carwow.es`/`carfax` = lead-gen / history-report
   (not used-stock POS); `hrmotor.es` = connection refused this sweep (domain may have moved —
   verify). `GarantiPRO/Mobius` = warranty B2B, 0 listings. **Excluded from inventory.**
9. **Counter drift caveat (restated).** Every live number is the 2026-06-12 photo; re-derive at harvest.

---

## 4. Attack order (what this registry tells F3–F5 to do)

1. **OPEN giants first, €0:** AutoScout24 (`__NEXT_DATA__`, GOLD attribution) → coches.com
   (decaying-open, harvest before Imperva flips) → autocasion (probe GraphQL) → motor.es (listings).
   ~650k listings with curl_cffi, no proxies.
2. **OEM/chain OPEN, €0:** renew (ES-facet API) + Flexicar + OcasiónPlus + Autohero + Clicars +
   Das WeltAuto + MB Certified + BMW PS + Hyundai Promise + Crestanevada. Clean single/network
   attribution. **Motorflash early as the dealer-discovery multiplier.**
3. **Per-dealer OEM subsite enumeration:** Audi Selection:plus, Das WeltAuto, BMW PS subsites
   (discovery via dealer locators + Motorflash concesionarios sitemap).
4. **TIER-1 walled, gated on spend/credentials (`countries/ES/_tier1/`, separated):**
   - **Adevinta family one recipe:** coches.net + milanuncios (+ segundamano/fotocasa) via the
     `…advgo.net/search` POST API + GeeTest/residential for milanuncios.
   - **Wallapop:** `cars/search` v3 with cloned app headers (settle signing question first).
   - **Akamai/CF hard walls (last, spend-gated):** Spoticar/Spoticar Direct (Akamai sensor),
     BCA/CarNext (CF managed challenge + B2B login), Ayvens Carmarket (public catalog now,
     B2B login for full data), Autorola (B2B login only).

Every platform above maps to a row in `entity` with `is_tier1`, `website_waf`, and a
`recipe_version` pointer; the Tier-1 set never shares recipe, raw store, or operation with the
OPEN set, per `ARCHITECTURE.md §Separación Tier-1`.
