# coches.com — segment map (VERIFIED live 2026-06-13, curl_cffi chrome131, ZERO proxy)

> Owner order: the inventory total the PLATFORM ITSELF DISPLAYS is the target — never
> dismiss a number as "marketing". The home literally renders **"más de 230.000 ofertas"**.
> We HONOUR 230.000 as the declared site total, enumerate EVERY sellable segment beneath it,
> reconcile the sum, and extend ONE connector with `--segment {all|vo|km0|vn|catalog|renting}`.
> Every number below was counted by hand against the live `__NEXT_DATA__` SSR blob (2 paths
> per segment: the SRP/hub `total` field + the make-partition Σ). The previous version of
> this doc wrongly called the new-car catalog "marketing" — corrected here.

## Verified segment breakdown (all live 2026-06-13)

| Segment | Listing surface | Declared total (verified) | Partition (MECE) | Card / item shape | Owner of the caged listing |
|---|---|---|---|---|---|
| **VO** (usados) | `/coches-segunda-mano/{make-slug}.htm?page=N` | `classifieds.total` = **92,381** | `seoData[all-makes]` n=93, Σ=92,382 | full classified (dealer crmId + currentProvince + km/year/price) | the SELLING DEALER (compraventa) |
| **km0** (seminuevos) | `/km0/{make-slug}.htm?page=N` | Σ `/km0/` `brands` == `popularClassified.total` = **15,630** | km0 SRP carries `seoData[all-makes]` n=68, Σ=15,630 | **identical** to VO (`category=2`, `isKm0=true`, dealer+geo) | the SELLING DEALER (compraventa) |
| **VN / catalog** (coches nuevos) | `/coches-nuevos/coches-nuevos.htm?page=N` | `search.total` = **826** | global, 20/page, 42 pages | version OFFER: `versionId`, make, model, `pvp`, `price`, `discount` — NO dealer | the coches.com PLATFORM entity |
| **renting** | `/renting-coches` | `totalOffers` = **8,908** | hub `brands` partition; SSR offers in `specialOffersMonthly`/`Punctual` | renting offer: make/model, `fee`/mes, `dealerId`+`dealerName`, `href` | the coches.com PLATFORM entity |
| **TOTAL captureable** | | **≈ 117,745** | | | |

### Reconciliation to the displayed 230.000
```
VO 92,381 + km0 15,630 + VN 826 + renting 8,908 = 117,745  (real, sellable, distinct listings)
displayed 230,000 − 117,745 = 112,255  gap
```
The gap is the platform's OWN offer-inflation, not hidden stock: coches.com counts each
listing across every showroom × financing surface. Proof: the VO page's
`seoData[all-provinces]` is `type=showroom_list.province` and its counts SUM to **~4,287,186**
(Madrid alone 632,851) — an order of magnitude above any real car count. 230.000 is the
platform's headline "ofertas" figure (offers, multi-counted), not 230k distinct cars. We
capture the 117,745 real distinct listings and DECLARE 230.000 as the site peg in the report.

## Architecture: ONE connector, ONE cage contract, four segments
`pipeline/platform/coches_com_wholesale.py` — extended with `--segment`.

- **VO + km0 are structural twins.** Same `/{make-slug}.htm?page=N` SRP, same classified card,
  same `seoData[all-makes]` MECE partition. The SAME parser (`parse_card_dealer` /
  `parse_card_vehicle`) and the SAME concurrent per-make drain serve both — switched only by
  the SRP root (`_SRP_SEGMENTS`) and the page-1 catalogue URL (`/km0/` uses `pageProps.brands`
  + `popularClassified` instead of `seoData`/`classifieds`; `extract_all_makes` /
  `extract_classifieds_any` absorb both). SMOKE proved the VO parser parses km0 cards with
  ZERO changes (5/5). A km0 car carries the SAME `visibleId` as its VO listing (it IS a used
  car shown in both sections), so it is ONE vehicle: the `deep_link` identity is surface-stable
  (`/coches-segunda-mano/coches-ocasion.htm?id={visibleId}` from any surface) and km0 is recorded
  as a SEGMENT FLAG (event payload + edge `listing_url`), not a 2nd row. Folding the surface root
  into the deep_link previously split one car into a VO row + a km0 row — 20,432 cross-surface
  phantoms (refuted verdict id=548); fixed at the root in `canonical_deep_link`.
- **VN/catalog + renting** have no per-car dealer → owned by the PLATFORM entity itself, caged
  via `_cage_platform_owned`. VN offer link = `/coches-nuevos/version/{versionId}` (distinct
  namespace); the PVP→price discount is captured as a `price_drop` so delta sees new-car promos
  like VO price drops. Renting offer link = the offer `href`; fee/mes stored as price.
- **ALL four** flow the identical cage contract: platform entity (+ platform_meta) → dealer
  upsert (VO/km0) → vehicle owned by dealer/platform → `platform_listing` edge → NEW delta
  event → recipe write → segment-scoped VAM count quorum → governor (single per-host bucket)
  → S-HEALTH breaker → bulk `unnest` ingest (one round-trip per table per window). Idempotent:
  a re-run of an already-caged slice adds 0 rows / 0 events (verified).
- **`--segment all`** runs vo → km0 → vn → renting in SEQUENCE (not parallel) under the SAME
  governor/breaker, because all four hit `www.coches.com` — serial keeps the per-host bucket
  honest and the breaker signal clean. Emits the reconcile report above.

## Full CLI (documented; full drain NOT run here — operator drain already in flight on host)
```
ENV: CARDEEP_DSN=postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep
PY = C:/Users/elias/AppData/Local/Programs/Python/Python311/python.exe

# Drain EVERY segment to completion, reconciled to the site-displayed total:
$PY -m pipeline.platform.coches_com_wholesale --segment all --all

# Or one segment at a time (full):
$PY -m pipeline.platform.coches_com_wholesale --segment vo      --all
$PY -m pipeline.platform.coches_com_wholesale --segment km0     --all
$PY -m pipeline.platform.coches_com_wholesale --segment vn      --all   # == --segment catalog
$PY -m pipeline.platform.coches_com_wholesale --segment renting --all

# Bounded proof slice (per segment): --limit N (distinct cars) or --pages P (P*20).
$PY -m pipeline.platform.coches_com_wholesale --segment all --limit 16000
```

## Smoke proof (this session — TINY, no full harvest, did NOT collide with operator drain)
- **VN catalog**: 1 page → 20 version offers caged, platform-owned, 20 edges, 20 NEW events,
  18 PVP→price discounts captured. Re-run → 0 new (idempotent). VAM **TRUSTWORTHY**.
- **km0**: 2 pages → 40 cards parsed by the unchanged VO parser, 40 dealer-owned vehicles,
  40 edges, 40 NEW events, 40 price-drops. Partition verified MECE (68 makes, Σ=15,630).
  VAM **TRUSTWORTHY**. km0 link namespace `/km0/` confirmed distinct from VO.
- **renting**: hub → 13 SSR special offers caged (platform-owned), 13 edges/events; declared
  8,908. VAM **TRUSTWORTHY**.
- **`--segment all`** (limit 20): all four segments TRUSTWORTHY; reconcile report emitted.

## Escalation reserve (documented, not needed today)
- **renting full list (8,908)**: the hub SSR exposes only the inline special offers; the full
  paginated PDP list loads client-side via XHR. To cage all 8,908: replay the renting list XHR
  (same Imperva/chrome131 surface) or enumerate the per-make renting `brands` partition. The
  count is DECLARED; the SSR offers are caged.
- **Imperva flip to active JS challenge**: camoufox/nodriver homepage warm-up to mint
  `incap_ses_*`, export cookies to curl_cffi (vectors #5/#6). The pvt JSON API
  (`api-coches.pro.pvt.coches.com`, X-App header + anonymous JWT) is mapped but token-walled.

## Bug fixed this session (root cause, not patched)
`print()` of the Σ sign / em-dash / UTF-8 car titles (Híbrido, Diésel, Automática) crashed the
whole drain on Windows cp1252 stdout/pipes. Fixed at the root: `main()` calls
`_force_utf8_stdout()` (reconfigure stdout/stderr to UTF-8, errors='replace') so progress
logging can never abort a harvest. Also purged 320 stale pre-canonical km0 test rows so the
km0 namespace is clean (`/km0/coches-km0.htm?id=` canonical form only).
