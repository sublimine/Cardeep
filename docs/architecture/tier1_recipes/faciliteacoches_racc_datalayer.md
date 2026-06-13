# faciliteacoches.com + cochesocasion.racc.es — data-layer recipes

Two genuinely-NEW car-selling channels surfaced from the keyword census (count=0 in DB), both
verified reachable FREE with `curl_cffi chrome131` (no proxy, no browser, no cookie warm-up) on
2026-06-13. Connector: `pipeline/platform/faciliteacoches_racc_wholesale.py` (two members, one
architecture — mirrors `group_vo_chains_wholesale.py`).

Dedup baseline (before build): `entity` had 0 rows for `faciliteacoches`/`caixabank`; the 10 "racc"
substring hits were all false positives (`tracción`, `raccoon`) on other domains. No `source_key`
collision. Both channels confirmed NEW.

---

## 1. faciliteacoches.com — CaixaBank/ARVAL VO+renting aggregator

- **Host / stack**: `www.faciliteacoches.com`, Next.js App Router on **Vercel**, no WAF challenge → `t0_open`.
- **Platform**: kind=`plataforma`, source_group=`marketplace_motor`, role=`platform`, family=`faciliteacoches`.
  cdp_code `CDP-ES-00-9PXHGJBY` (`domain:faciliteacoches.com`).
- **Owner model — PER-SHOP** (geo-anchored selling point): each car's RSC object carries
  `shopData` (the PHYSICAL shop where the car sits — `{id_mf,name,province,region,cp,city}`) and
  `dealerData` (the parent OEM/dealer group — constant across a group's cars). Geo anchors to the
  SHOP's `cp` (first 2 digits = INE province) + `city`; `dealerData` kept as `dealer_group` provenance.
  Fallback: shop→dealer→platform bucket (a car is never dropped).
- **Enumeration**: the SRP `/es/es/coches/ocasion/compra` resolves results via a **deferred RSC
  server promise** — `?page=N`, `?pg=N`, `?pagina=N` and the province/brand path routes (`/madrid`,
  `/all/audi`) ALL return the same default ~39-car window. The browser pages via a Next.js **server
  action** (not header-reachable; tried `RSC:1` / `Next-Router-State-Tree` → empty/no-op).
  **Canonical full index = the sitemap** `https://faciliteacoches.com/peninsula-baleares/sitemap/coches-ficha.xml`
  → **21,989** car PDP `<loc>` entries. We drain PDP-by-PDP; each PDP `/es/es/ficha/{slug}-{id_mf}`
  re-emits the same RSC car object **plus a "similar cars" block** (~10 extra attributed cars per
  PDP), so a window of 12 PDPs yields ~130 distinct cars across ~75 distinct shops.
- **Native id**: `id_mf` (the PDP slug tail). **Price-drop**: `prevPrice` vs `price` → delta event.
- **Data surface**: parsed from `self.__next_f.push([1,"…"])` flight chunks → JSON-decode → balanced-
  brace scan for objects starting `{"site":"es"` carrying `"id_mf"`. `shopData`/`dealerData` may be an
  unresolved `"$…"` string ref → treated as absent (graceful degrade). data_surface stored `next_data`.

## 2. cochesocasion.racc.es — RACC auto-club VO portal

- **Host / stack**: `cochesocasion.racc.es`, WordPress (`themes/cochesbbb`), Apache/PHP 8.3, no WAF → `t0_open`.
  (`www.cochesocasion.racc.es` does NOT resolve; use the bare host.)
- **Platform**: kind=`plataforma`, source_group=`association`, role=`platform`, family=`racc`.
  cdp_code `CDP-ES-00-58C3W3P9` (`domain:cochesocasion.racc.es`).
- **Owner model — PER-DEALER-BY-NAME** (national): the SRP card carries the car but NOT the seller;
  the **PDP JSON-LD** `@type:Car offers.seller` (Organization `name`, e.g. "Grupo M-AUTOMOCION") is
  the dealer. The surface exposes NO per-car province/address (national inventory aggregation via
  `fotos.inventario.pro`), so the dealer is anchored **national** (entity province_code NULL; `00`
  segment in cdp_code, keyed by normalized seller name). A car with no PDP seller → portal bucket.
- **Enumeration**: GET `?pg=N` paginates **server-side cleanly** (disjoint card sets per page; 12
  cards/page; `total_pages` from `pagination__pages-left "de 79"`). The WP ajax
  `admin-ajax.php?action=get_search_result` declares `total` (≈939–948) / `total_pages` / `current_page`.
  (`?page`/`?pagina`/`/page/N/` are ignored — only `?pg=N` works.)
- **Native id**: PDP `vehicleIdentificationNumber` (VIN); falls back to the card `addToCompare({id})`
  compare-id. **Card fields**: `h5.car-card__title` (Make Model), `h6.car-card__subtitle` (version),
  `Matriculación` (year), `Kilometraje` (km), `.car-card__title.mb-0` (price €), `.card-icon-grid__label`
  (fuel + transmission), `img.car-card__image` (photo). data_surface stored `json_ld`.
- **Future per-branch geo**: the PDP carries a `concessionarie-map-item` block (dealer map) — a deeper
  probe could geo-anchor the dealer; not fabricated here.

---

## Caging (both members, byte-identical to the proven template)

platform entity (kind=plataforma) + `platform_meta` · per-shop/per-dealer `compraventa` owner
(geo-resolved or national) · `vehicle` OWNED BY its owner · `platform_listing` edge platform↔vehicle ·
NEW `vehicle_event` (price-drop preserved) · all idempotent ON CONFLICT (BULK unnest). VAM count
quorum: `db_edges == db_join_vehicles == harvested_cageable` (distinct `(owner_cdp, deep_link)`).
