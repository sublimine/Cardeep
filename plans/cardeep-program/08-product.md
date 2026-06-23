# Producto / Frontend — Make the entire national digital census legible, searchable and provable in one portal

> This domain owns the public-facing CARDEEP portal (`web/`): the React SPA that renders the census to humans. It owns discovery UX (search, browse, map), the dealer and vehicle detail experiences, the live coverage/exhaustiveness presentation, the typed API contract (`web/src/api/*`), and the design system. It matters because the census is only as valuable as it is *legible*: 19k dealers and 1.84M vehicles are worthless if a user cannot find a specific car, a specific dealer, or see at a glance which corner of Spain is covered. The frontend is where "we indexed the digital footprint of everyone" becomes a verifiable, shareable claim. It consumes — and never owns — the data; the `serving` domain owns the API/DB, this domain owns the experience.

## Current state (verified)

All paths verified at `C:\Users\elias\projects\cardeep\web` on 2026-06-23.

**Stack (verified `web/src/main.tsx`, `web/src/api/client.ts`):** Vite + React + React Router v6 (`createBrowserRouter`) + TanStack Query (`staleTime` 60s). Typed HTTP client over `Envelope<T>`, `X-API-Key` header, `BASE` defaults to `http://127.0.0.1:8090` via `VITE_API_BASE`.

**Routes (verified `web/src/main.tsx`):** `/` (Landing), `/explore` (Explore), `/dealer/:cdp` (Dealer), `/vehicle/:ulid` (Vehicle), `*` (NotFound).

**API surface consumed (verified `web/src/api/client.ts` lines 82–98):** `/stats`, `/geo/seal`, `/geo/exhaustiveness`, `/geo/{province}/entities`, `/geo/{province}/municipalities/{muni}/entities`, `/geo/{province}/tree`, `/entities/{cdp}`, `/entities/{cdp}/inventory`, `/entities/{cdp}/delta`, `/vehicles/{ulid}`, `/vehicles/{ulid}/history`, `/vehicles/{ulid}/platforms`.

**Live census figures (verified DB `product_stats`, `computed_at 2026-06-23T12:33:47Z`):**
- Dealers (active POS, deduped, no particulars/scrapyards): **19,144**
- Unique available vehicles (`servable_vehicle`): **1,841,679**
- Market events (`vehicle_event`): **2,741,085**
- Provinces / municipalities: **52 / 8,132**
- National sale coverage (`v_province_seal`, segment `venta`): **80.6% (18,318 / 22,720)**
- Province verdicts (venta): **14 SELLADO / 32 PARCIAL / 6 GAP**
- Available vehicles with photo: **2,120,717 / 2,257,054 (94.0%)**; with deep_link: **100%**
- Showcase dealer `CDP-ES-28-FX1FAD1S` (Flexicar M.): **active**

**Verified gaps (HIGH severity):**
1. **Search is a dead-end.** `web/src/routes/Landing.tsx` line 117: `onSubmit` calls `navigate('/explore')` with **no query params**. The "Busca por provincia, marca o modelo…" form is non-functional. There is **no global vehicle search endpoint** in the API (`services/api/routers/vehicles.py` exposes only `/vehicles/{ulid}` and `/vehicles/{ulid}/history`; `grep` for `search`/`q=` returns nothing) and **no `useVehicleSearch` hook** (`web/src/api/hooks.ts`).
2. **The richest component is dark.** `web/src/three/SpainMap.tsx` (navigable 3D choropleth, hover HUD, drill to `/explore?prov=`) exists and is data-wired, but `Landing.tsx` line 94 renders `<HeroScene />` (cobalt light-bars studio, no map, no car) instead. The map ships in the bundle's intent but is never seen.
3. **No deep-linkable filter state.** Explore filters (`kind`, `tier1`, text, page) are client-side `useState`; none are reflected in the URL, so no view is shareable.

**Verified infra convention:** the production-faithful DB container is `postgres:16` on `127.0.0.1:5433` (`docker-compose.yml` line 24). Per operating doctrine, any data-touching dry-run runs on a **separate :5434 sandbox**, never against :5433 without golden + Ferrari + CI.

## Next-level objective

Deliver a portal where **any vehicle or dealer in the digital census is reachable in under 2 seconds and 2 interactions**, and where **national coverage is provable visually**, beating any human-built directory by being exhaustive, instant, and honest about gaps. Concretely:
- A **global faceted + geo search** over all 1.84M servable vehicles and 19,144 dealers (make, model, year, price, province, fuel, km) with sub-150ms p95 and typo tolerance.
- The **live 3D Spain coverage map as the hero**, so the "everyone, everywhere" claim is the first thing a visitor sees, with GAP provinces visibly red.
- **Every filter and search shareable as a URL.**
- **Honest exhaustiveness**: the MSE seal floor (`coverage_lower`) shown without inflation, GAP provinces never hidden.

Measurable bar: a known plate/listing → its vehicle page in ≤2 clicks; a "BMW in Madrid under 20k" query → results in ≤2s; map renders 52 provinces colored by live verdict at 60fps.

## Chosen technology (EUR0)

All MIT/Apache/ISC, self-hostable on free tiers (Oracle Cloud Free Tier / GitHub Pages / Cloudflare R2). Sources verified in research dossier.

| Need | Tool | Why | Source | Integration effort |
|---|---|---|---|---|
| Search engine (facet + geo + typo) | **Typesense 30.2** (Apache 2.0) | Sub-50ms, native `_geosearch` (radius/bbox) as first-class, facets, typo tolerance, single binary on Oracle Free Tier RAM. Geosearch beats Meilisearch for "dealers near me". | github.com/typesense/typesense | Medium — stand up node, write indexer from `servable_vehicle` + `v_dealer_resolved`, build search UI. **New backend domain boundary: belongs to `serving`; this domain owns the client + the indexer spec.** |
| Search UI | **TanStack Table 8.21 + TanStack Virtual 3.13** (MIT) | Headless; virtualizes 50k rows at 60fps; pairs with existing CSS-token system. Already TanStack-native (Query in use). | github.com/TanStack/table | Low — additive, headless, styles from `tokens.css`. |
| URL state | **nuqs 2.8** (MIT) — *or* RR6 `useSearchParams` | Type-safe shareable filter/search/map state in the query string. nuqs is App-Router-oriented; this SPA is RR6, so **RR6 `useSearchParams` is the zero-dependency baseline**; adopt nuqs only if type-safety pain is real. | github.com/47ng/nuqs | Low (RR6 path: zero deps). |
| Map base (vector, no key) | **MapLibre GL JS 5.24** (BSD) + **PMTiles 3** | Zero license/key. Spain tile subset hosted on free Cloudflare R2 via HTTP range. Replaces any paid Mapbox/MapTiler path. | github.com/maplibre/maplibre-gl-js, github.com/protomaps/PMTiles | Medium — but **existing `SpainMap.tsx` (Three.js choropleth) already works**; MapLibre is the *evolution path*, not a rewrite prerequisite. Phase-gated. |
| Density / gap viz | **deck.gl 9.3** `H3HexagonLayer` + **h3-js 4.4** (MIT/Apache) | GPU-rendered hex density of dealers reveals coverage holes instantly; the visual proof of exhaustiveness. Overlays on MapLibre. | github.com/visgl/deck.gl, github.com/uber/h3 | Medium — phase-gated, depends on `geo` centroids. |
| Coverage charts | **Observable Plot 0.6** (ISC) | Elegant geo + bar marks for the stats panel with less code than D3; institutional-grade choropleths. | github.com/observablehq/plot | Low. |

**Already in repo, keep:** Three.js `SpainMap.tsx`/`Province.tsx` (the map hero ships *now* via this; MapLibre is a later upgrade, not a blocker), TanStack Query, the typed `api/types.ts` contract.

## Target architecture

```
                 ┌────────────────────────────────────────────┐
   Browser  ───► │  CARDEEP SPA (web/, Vite + RR6 + TanStack)   │
                 │                                              │
                 │  Landing  ── hero = <SpainMap/> (3D choro)   │
                 │            ── live /stats counters           │
                 │            ── functional global SearchBox ───┼──┐
                 │  /search  ── faceted results (Table+Virtual) │  │
                 │            ── URL = source of truth (params) │  │
                 │  Explore  ── province grid / dealer browser  │  │
                 │  Dealer   ── entity + inventory + delta      │  │
                 │  Vehicle  ── ficha + history + platforms     │  │
                 └───────┬─────────────────────────────┬───────┘  │
                         │ (existing REST, Envelope<T>) │          │ (new)
                         ▼                              ▼          ▼
        services/api  /stats /geo/* /entities/* /vehicles/*   /search  ◄─ serving domain
                         │                                          │
                         ▼                                          ▼
              Postgres :5433 (prod) / :5434 (dry-run)      Typesense node
              servable_vehicle · v_dealer_resolved · v_province_seal
                         ▲                                          ▲
                         └────────── indexer (cron, serving) ──────┘
                              reads servable_vehicle → Typesense docs
```

**Data flow contracts (owned by this domain on the client side):**
- New `web/src/api/types.ts` additions: `VehicleSearchHit`, `SearchFacets`, `SearchQuery`, `SearchResponse` — typed against the agreed `/search` envelope.
- New `web/src/api/client.ts` method: `searchVehicles(q: SearchQuery): Promise<SearchResponse>`.
- New hook `useVehicleSearch(query)` in `web/src/api/hooks.ts`.
- URL state schema: `/search?q=&make=&model=&prov=&yearMin=&yearMax=&priceMax=&fuel=&page=` — every active filter serialized, deep-linkable.

**Honesty invariants (non-negotiable):** GAP provinces render red, never hidden; the MSE seal shows `coverage_lower` (floor), never the point estimate dressed up; counters read live from `/stats`, never hardcoded.

## Execution phases

Each phase ≈ 1 PR. Branch `feature/<slug>` from `main`. All frontend-only phases are fully reversible (revert PR). Any phase touching served data uses :5434 dry-run only.

### Phase 1 — Make the map the hero (frontend-only, zero new deps)
**Cold-start context:** `Landing.tsx` line 94 renders `<HeroScene />`; the superior `SpainMap.tsx` is wired (`useSpainData.ts` → `useSealMap('venta')`, `useProvinceShapes()`) but unused. This is the highest value-per-effort change: surface what already works.
**Tasks:**
- In `web/src/routes/Landing.tsx`, lazy-import `SpainMap` and render it as the hero, keeping `HeroScene` available behind a `prefers-reduced-motion` / low-GPU fallback (detect via `useReducedMotion`).
- Verify province colors come from live `v_province_seal` via `useSealMap`; ensure the 6 GAP provinces are visibly red (`mapColors.ts` `VERDICT_COLOR`).
- Wire map click → `/explore?prov=<code>` (already in `SpainMap.tsx`; confirm).
**Verification:** `cd web && npm run build && npm run dev`; load `/`, confirm 52 provinces render colored by verdict, hover HUD shows numerator/denominator, click navigates to `/explore?prov=`. Lighthouse: hero LCP < 2.5s (lazy three.js stays out of initial bundle).
**Exit criteria:** Map is the hero; reduced-motion users get a static/light fallback; no console errors; bundle initial JS still < 300kb gzipped (App page budget).
**Rollback:** revert PR — restores `<HeroScene />`.

### Phase 2 — URL as state for Explore (frontend-only)
**Cold-start context:** Explore filters (`ProvinceGrid` sort, `DealerBrowser` kind/tier1/query/page) are local `useState`; nothing is shareable.
**Tasks:**
- Adopt RR6 `useSearchParams` (zero new deps) to back: `prov`, `kind`, `tier1`, `q`, `page`, `sort`. Initialize state from URL on mount; push to URL on change (replace, not push, for filter churn).
- Ensure `/explore?prov=28&kind=dealer&page=2` reconstructs the exact view.
**Verification:** apply filters, copy URL, open in fresh tab → identical view. `npm run build` clean.
**Exit criteria:** all Explore filter state round-trips through the URL; back/forward works.
**Rollback:** revert PR.

### Phase 3 — `/search` backend contract (DRY-RUN, :5434 only) — *coordinate with `serving`*
**Cold-start context:** No global search exists. The indexable source is `servable_vehicle` (publish-gate view, defined `migrations/0031_gestion.sql:158`, hardened through `0047`) joined to `v_dealer_resolved`/`v_canonical_vehicle` for make/model/year/km/price/province/dealer. This phase is **owned by `serving`** for implementation; this domain owns the **contract spec and the dry-run validation**.
**Tasks:**
- Stand up Typesense against a **:5434 dry-run DB** (`docker compose` override, never :5433).
- Define the document schema: `vehicle_ulid` (canonical only — filter via `v_canonical_vehicle`), `make`, `model`, `year`, `price`, `km`, `fuel`, `transmission`, `province_code`, `cdp_code`, `photo_url`, `deep_link`, `_geo` (dealer centroid from `geo` domain).
- Write the indexer reading `servable_vehicle` (respects the publish gate — no quarantined/zero-price/wrong-status rows; honesty invariant inherited from the view).
- Expose `GET /search` returning `Envelope<SearchResponse>` matching the agreed client types.
**Verification:** against :5434, index a sample, assert counts reconcile with `SELECT count(*) FROM servable_vehicle` (golden test); query "BMW Madrid" returns only canonical, servable, in-province hits; p95 < 150ms. Run Ferrari + CI unit/collect before any promotion. **No write to :5433 until golden + Ferrari + CI green.**
**Exit criteria:** `/search` answers facet + geo queries on :5434 with results provably a subset of `servable_vehicle`; zero quarantined leaks.
**Rollback:** drop Typesense container; `/search` route removed; no served data touched (read-only view consumer).

### Phase 4 — Functional global search UI (frontend-only)
**Cold-start context:** With `/search` live, fix the dead-end form. Add `searchVehicles` to `client.ts`, `useVehicleSearch` to `hooks.ts`, `SearchQuery`/`SearchResponse`/`VehicleSearchHit` to `types.ts`.
**Tasks:**
- New route `/search` rendering results with TanStack Table + Virtual; URL is source of truth (Phase 2 pattern): `?q=&make=&model=&prov=&yearMin=&priceMax=&fuel=&page=`.
- Rewire `Landing.tsx` line 117 `onSubmit` to `navigate('/search?q=' + encoded)` — kill the placeholder.
- Facet rail (make/model/province/fuel/price band) driven by `SearchFacets`; each result links to existing `/vehicle/:ulid`.
- Empty/error/loading states; honest "0 results" (never fabricate).
**Verification:** Playwright: type "BMW", submit on `/`, land on `/search?q=BMW` with results; apply province facet → URL updates → shareable; virtualized scroll of 60+ stays 60fps. `npm run build` within budget.
**Exit criteria:** the Landing search promise is real; results deep-linkable; every hit reaches a vehicle page.
**Rollback:** revert PR (search UI removed; form falls back to `/explore` navigation — no worse than today).

### Phase 5 — Coverage density map upgrade (MapLibre + deck.gl H3) — *depends on `geo` centroids*
**Cold-start context:** Phase 1 ships the Three.js choropleth. This phase upgrades to a pannable/zoomable MapLibre base with a deck.gl `H3HexagonLayer` of dealer density, revealing local coverage holes — the visual proof of exhaustiveness. Requires per-dealer coordinates from the `geo` domain.
**Tasks:**
- Host Spain PMTiles subset on free Cloudflare R2 (range requests, EUR0).
- MapLibre base + deck.gl overlay; H3 res 4–5 nationally, 7–8 on zoom; color by dealer count per cell.
- Keep province choropleth toggle; keep reduced-motion static fallback.
**Verification:** Lighthouse on map page; CLS < 0.1; no layout shift; gaps visibly empty where `v_province_seal` verdict = GAP. Cross-check hex density totals against `count(*) v_dealer_resolved` per province.
**Exit criteria:** zoomable map with honest density; EUR0 tile hosting confirmed; CWV targets met.
**Rollback:** revert PR — Phase 1 Three.js map remains the hero.

### Phase 6 — Exhaustiveness & honesty polish (frontend-only)
**Cold-start context:** `Certificate.tsx` shows the MSE seal but renders "pendiente de build" when national cert is null. Tighten the honest presentation.
**Tasks:**
- Surface `coverage_lower` (floor) prominently across stats/landing; never the point estimate alone.
- Coverage charts via Observable Plot (per-CCAA bars, verdict distribution 14/32/6).
- Make GAP provinces a first-class call-to-action ("aquí aún no llegamos"), not hidden.
**Verification:** visual review at 320/768/1024/1440; confirm numbers match live `/geo/exhaustiveness` and `/geo/seal`; both themes (if applicable) intentional.
**Exit criteria:** the portal states coverage honestly, floor-first, gaps visible; design-quality checklist (≥4 qualities) passes.
**Rollback:** revert PR.

## Risks & mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Search index leaks non-servable/quarantined vehicles, breaking the trust invariant | CRITICAL | Index **only** from `servable_vehicle` (the publish gate); golden test asserts result set ⊆ view; dry-run on :5434 with Ferrari+CI before promotion. |
| `/search` work blocks the frontend (cross-domain dependency on `serving`) | HIGH | Phases 1–2 (map hero, URL state) ship pure-frontend value with zero backend dependency; search UI (Phase 4) gated behind Phase 3 contract only. |
| Three.js / MapLibre hurts LCP on low-end devices | HIGH | Lazy-load three.js (already done); `prefers-reduced-motion` static fallback; map page separate from initial Landing bundle; enforce 300kb gzipped budget in CI. |
| Inflated coverage claims (point estimate vs floor) damage credibility | HIGH | Honesty invariant: always show `coverage_lower`; GAP provinces always red and visible; counters always live from `/stats`. |
| PMTiles hosting accidentally incurs cost | MEDIUM | Cloudflare R2 / Oracle Free Tier only; verify EUR0 billing before Phase 5 merge; Three.js map is the EUR0 fallback already in repo. |
| Map centroids unavailable from `geo` for H3 density | MEDIUM | Phase 5 explicitly depends on `geo`; province-level choropleth (Phase 1) ships independently and remains valid if centroids slip. |

## Success metrics

- **Findability:** any known canonical `vehicle_ulid` reachable from `/` in ≤2 interactions; "make + province + price" query → results in ≤2s p95 (target search p95 < 150ms server-side).
- **Coverage legibility:** map hero renders 52 provinces colored by live `v_province_seal` verdict at 60fps; all 6 GAP provinces visibly red.
- **Shareability:** 100% of Explore + Search filter combinations reconstructable from URL alone.
- **Honesty:** every displayed coverage number traces to a live endpoint (`/stats`, `/geo/seal`, `/geo/exhaustiveness`); seal shows floor, not inflated estimate; zero non-servable leaks in search (golden test green).
- **Performance budgets (web/performance.md):** Landing LCP < 2.5s, INP < 200ms, CLS < 0.1; App-page initial JS < 300kb gzipped, CSS < 50kb.
- **No regressions:** existing 4 routes keep working; `npm run build` clean; CI green before any promotion to :5433.
