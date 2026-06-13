# CARDEEP — SEGMENT TAXONOMY · ESPAÑA (complete keyword → channel-family → operator map)

> **What this is:** the single consolidated taxonomy of *every place a used car is sold in
> Spain*, keyword-driven and operator-exhaustive. It merges the keyword census
> (`KEYWORD_CHANNEL_MAP.md`) with the five segment-census fronts run on **2026-06-13**
> (`marketplaces_extra`, `oem_new_stock`, `leasing_rentacar_exfleet`, `b2b_extra_auctions`,
> plus the keyword/state-vs-channel analysis). For every keyword, every channel-family and
> every operator it records the live status: **HAVE / MISSING / NEWLY-CONNECTED /
> UNREACHABLE / DEFERRED**.
>
> **Social media (Facebook Marketplace / Instagram) is DEFERRED — excluded by owner mandate.**
> It is a real used-car channel in Spain; it is intentionally out of scope for this taxonomy
> and noted as deferred wherever it surfaces, never silently dropped.
>
> **Verification basis:** keywords swept live via WebSearch + WebFetch + `curl_cffi`
> chrome131 on **2026-06-13**. Every DB count below is from **my own query** that day against
> `postgres://cardeep@localhost:5433/cardeep`. External facts are `[V]` (fetched live this
> day) or `[A]` (vendor/secondary, not re-derived on-site).
>
> **Source census files (the evidence behind each row):**
> - `docs/research/KEYWORD_CHANNEL_MAP.md` — keyword → channel, state-vs-channel analysis
> - `docs/research/segment_census_marketplaces_extra.md` — Motorflash + metasearch verdicts
> - `docs/research/segment_census_oem_new_stock.md` — OEM new-car / km0 stock
> - `docs/research/segment_census_leasing_rentacar_exfleet.md` — ex-fleet leasing/renting
> - `docs/research/segment_census_b2b_extra_auctions.md` — B2B / auction operators

---

## 0. Live DB taxonomy reference (my query, 2026-06-13)

`entity.kind` populated counts:
`particular` 326.443 · `compraventa` 31.529 · `garaje` 7.220 · `concesionario_oficial` 1.844 ·
`desguace` 1.645 · `subasta` 95 · `oem_vo_portal` 14 · **`plataforma` 13** · `rent_a_car_vo` 6 ·
`cadena` 4 · **`importador` 0 (VACÍO)** · **`agente_oficial` 0 (VACÍO)**.

`entity.source_group` (populated): `directory` 9.953 · `oem_vo_portal` 5.769 ·
`oem_dealer_network` 1.526 · `marketplace_motor` 1.323 · `desguace_network` 1.292 ·
`association` 409 · `chain` 189 · `official_registry` 99 · `rentacar_vo` 6 ·
`marketplace_generalist` 2 · (`NULL` on long-tail/particular rows).

`platform_listing` by segment: `used` 1.432.777 · **`new` 8.380** · `km0` 3.107 · `renting` 1.212.

**The 13 platform entities (`kind='plataforma'`), live cdp_codes:**

| trade_name | source_group | cdp_code | status |
|---|---|---|---|
| coches.net | marketplace_motor | CDP-ES-00-TKRV45RP | HAVE (Tier-1 baseline) |
| milanuncios | marketplace_generalist | CDP-ES-00-E382JYEH | HAVE (Tier-1 baseline) |
| wallapop | marketplace_generalist | CDP-ES-00-EMRH0TWQ | HAVE (Tier-1 baseline) |
| coches.com | marketplace_motor | CDP-ES-00-XM91J1NZ | HAVE (Tier-1 baseline) |
| Autocasion | marketplace_motor | CDP-ES-00-QY06GW0B | HAVE (Tier-1 baseline) |
| motor.es | marketplace_motor | CDP-ES-00-HSV4XZ2H | HAVE (Tier-1 baseline) |
| AutoScout24 | marketplace_motor | CDP-ES-00-VMCZWW5N | HAVE (Tier-1 baseline) |
| Autorola | official_registry | CDP-ES-00-RJ109M0T | HAVE (auction) |
| BCA Espana | official_registry | CDP-ES-00-WYJKTP6S | HAVE (auction) |
| Ayvens Carmarket | official_registry | CDP-ES-00-H1VCV020 | HAVE (auction) |
| **Motorflash** | marketplace_motor | **CDP-ES-00-WN1DMGRN** | **NEWLY-CONNECTED (this campaign)** |
| **Subastacar** | official_registry | **CDP-ES-00-S3K8PK50** | **NEWLY-CONNECTED (this campaign)** |
| **seat_cupra_new** | oem_dealer_network | **CDP-ES-00-5R30HVA7** | **NEWLY-CONNECTED (this campaign)** |

---

## 1. The "state-of-vehicle" keyword layer → FILTER, not a new channel

**Nuclear finding (confirmed across the sweep):** the majority of used-car keywords are
**vehicle states/attributes**, sold through the SAME already-censused channels (official
dealer, compraventa, OEM-VO portal). They are **inventory filters**, not operators — no new
channel-type is created by the keyword. Connecting them adds zero net operators.

| Keyword | What it surfaces | Real channel (already HAVE) | Verdict |
|---|---|---|---|
| `venta de coches` / `coches de ocasión` / `segunda mano` | coches.net, wallapop, milanuncios, AS24, autocasion + all dealers/compraventas | marketplace_* + compraventa + concesionario_oficial | **ROOT of the universe — [HAVE]** |
| `seminuevos` | dealers + VO portals (0–2 yr, <25.000 km) | concesionario_oficial / oem_vo_portal / compraventa | **[FILTER]** |
| `km0` / `kilómetro cero` | dealer that registers w/o use (<1.000 km); Gyata, Driveris, HR Motor, coches.net/km-0 | concesionario_oficial / cadena / compraventa | **[FILTER]** (also a distinct `segment=km0`: 3.107 edges) |
| `coche de gerencia` / `coche de dirección` | brand/dealer internal use (<10–15k km); Renault Retail, Movento | concesionario_oficial / oem_vo_portal | **[FILTER]** |
| `vehículo de demostración` / `demo` | dealer test car; coches.net/km-0/demostracion | concesionario_oficial / oem_vo_portal | **[FILTER]** |
| `coche de cortesía` | workshop courtesy car resold | concesionario_oficial / garaje | **[FILTER]** |
| `stock concesionario` / `vehículos disponibles` | immediate dealer inventory | concesionario_oficial / compraventa | **[FILTER]** |
| `ocasión garantizado` / `certificado` / `sello de ocasión` | OEM programs (Das WeltAuto, VW Approved, renew, Toyota 150-pt, Spoticar, H Promise, MB Certified) + Carfax | oem_vo_portal (all 14 anchored) | **[FILTER]** over existing channel |
| `outlet de coches` / `liquidación de stock` | clearance section of compraventas/chains (Yamovil, Canalcar, Carmotive…) | compraventa / cadena | **[FILTER]** |
| `coches baratos` / `ofertas` | same inventory, price-sorted | all | **[FILTER]** |
| regional: `cotxes d'ocasió` (cat) / `…Canarias` / `…Galicia` | same platforms geo-filtered + regional aggregators (Buscocoches, Catalunya Motor, Factoría de Automóviles) | marketplace_* (geo) + compraventa | **[FILTER]** geo |
| `furgonetas` / `comercial derivado de turismo` | light commercials on the same channels; Spoticar, OcasiónPlus, Crestanevada, Driveris, Terry Ocasión | (existing channels) | **[FILTER]** — cars-only scope; turismo-derived borderline |

---

## 2. Keywords that DO reveal a channel-family / operator

Each row below maps to one channel-family detailed in §3–§7. `[HAVE]` = anchored in DB ·
`[NEW]` = connected this campaign · `[MISSING]` = real operator not yet caged ·
`[NEW-TYPE]` = channel-type with no slot/empty kind · `[UNREACHABLE]` = no free vector.

| Keyword | Channel-family it surfaces | Status summary |
|---|---|---|
| `subasta de vehículos` (B2B) | B2B / auction platforms (§7) | partial — 3 HAVE + 1 NEW (Subastacar); rest GATED/UNREACHABLE |
| `compro tu coche` / `vendemos tu coche` / `tasación online` | buy-and-resell chains (their *buy* service is not a separate channel) | mostly HAVE as `compraventa`/`cadena`; service ≠ channel (see note) |
| `renting fin de contrato` / `coches de flota` / `vehículos de empresa` | ex-fleet leasing/renting VO (§6) | **NEW-TYPE populated** — Arval/Northgate NEW, Athlon caged; rest UNREACHABLE |
| `plataforma VO con financiación` | bank VO aggregator | **MISSING** — faciliteacoches.com (CaixaBank), 0 in DB |
| `coches importados` / `importación de Alemania` | import-to-order / German stock (§5) | **NEW-TYPE empty** — `kind=importador` = 0 entities; reachable, not yet caged |
| `coches clásicos` / `youngtimer` / `coche de colección` | classic/collector marketplaces (§5) | **NEW-TYPE no-slot** — scope decision pending owner |
| `concesionario online` / `entrega a domicilio` | digital-native retailers | **[HAVE]** as compraventa/cadena (delivery = attribute, not channel) |
| `coches nuevos` / `stock disponible` / `entrega inmediata` (OEM) | OEM official NEW-car + km0 stock (§4) | **NEW** — seat_cupra_new connected; rest reachable-MISSING |
| `coche de club` / `RACC ocasión` | auto-club VO portal | **MISSING** (minor) — cochesocasion.racc.es |
| (Facebook Marketplace / IG) | social-media classifieds | **DEFERRED — excluded by owner mandate (social media)** |

> **Note on "compro/vendemos tu coche":** OcasiónPlus, Crestanevada, Autofesa, AUTO1
> (compramostucoche), Driveris, Yamovil, Dursan, Sibuscascoche, Esmicoche are already in DB as
> `compraventa`/`cadena`. Their *instant-valuation buy service* is a sourcing funnel, not a
> separate selling channel — not modelled as its own channel-type. MODRIVE overlaps the
> importer family (§5).

---

## 3. Channel-family: MARKETPLACES / AGGREGATORS (`marketplace_extra`)

Beyond the 7 Tier-1 marketplaces already held. **HAVE = 10** (7 marketplaces + 3 auction
platforms). **NEWLY-CONNECTED = Motorflash** (+44 cars on the proof slice; **187 edges live
in DB now**, full ~1.044-dealer / ~50k-car drain governor-gated/pending).

### 3.1 Genuine marketplaces / aggregators

| Operator | Domain | Status | Note |
|---|---|---|---|
| coches.net · milanuncios · wallapop · coches.com · autocasion · motor.es · AutoScout24 | — | **HAVE** | Tier-1 baseline |
| Autorola · BCA · Ayvens Carmarket | — | **HAVE** | auction platforms (also §7) |
| **Motorflash** | motorflash.com | **NEWLY-CONNECTED** | `[V]` 200, ~50k veh, ~1.044 named dealers, JSON-LD, no wall. `kind=plataforma`, `source_group=marketplace_motor`, `CDP-ES-00-WN1DMGRN`. Connector `pipeline/platform/motorflash_wholesale.py`. Dealers caged as `compraventa` with `province=NULL`, name-keyed under sentinel '00' for cross-platform dedup; vehicles owned by dealer; `platform_listing segment='used'`. VAM TRUSTWORTHY. Proof slice 44 cars; live edges 187; full drain P1-governor-gated |
| Trovit Coches | coches.trovit.es | **MISSING-by-choice** | `[V]` 200 Lifull metasearch; links OUT to source portals we already drain — caging duplicates inventory |
| Mitula Coches | coches.mitula.es | **MISSING-by-choice** | `[V]` same Lifull Connect engine as Trovit (redirects to it) |
| AutoUncle | autouncle.es | **MISSING-by-choice** | `[V]` price-aggregator metasearch, links out |
| eBay Motors ES | ebay.es | **MISSING low-priority** | `[V]` live; marginal ES car volume, generalist auction |
| Automercadillo | automercadillo.com | **MISSING low-priority** | `[V]` 200 small generalist classified |
| auto10.com | auto10.com | **MISSING low-priority** | `[V]` 200 small editorial-classified |
| ¿Qué coche me compro? | quecochemecompro.com | **NOT-A-POS** | `[A]` comparator/editorial, no stock |

### 3.2 Vertical marketplaces (classic / collector) — see §5.2 for the channel-type call

| Operator | Domain | Status |
|---|---|---|
| Car & Classic | carandclassic.com | **MISSING vertical** — `[V]` 200, 30k+ adverts + auctions, pan-EU classic, deferred low-priority |
| Miclásico | miclasico.com | **MISSING vertical** — `[V]` 200 ES classic/collector classifieds, deferred low-priority |

### 3.3 UNREACHABLE / NOT-A-POS (confessed)

| Operator | Domain | Status |
|---|---|---|
| Heycar | heycar.es | **UNREACHABLE — dead in ES** `[V]` (ceased ops 2023; 20 KB stub, no inventory) |
| CarGurus | cargurus.es | **UNREACHABLE — no live ES operation** `[V]` (4.4 KB stub) |
| Carwow | carwow.es | **UNREACHABLE-AS-POS** `[V]` lead-gen / new-car broker, no used inventory |
| segundamano.es | segundamano.es | **NOT INDEPENDENT** `[V]` Adevinta gateway (== milanuncios family, already HAVE) |
| Swipcar | swipcar.com | **NOT-A-POS** — renting/subscription |
| compramostucoche | compramostucoche.es | **NOT-A-POS** — AUTO1 buy-tool, 0 listings, sourcing-only |
| Facebook Marketplace | facebook.com | **DEFERRED — excluded by owner mandate (social media)** |

### 3.4 Single-seller retail CHAINS (own stock — VO-chains front, NOT marketplaces)

Cross-listed only; their stock is own-stock counted once at the chain, not aggregated.
Belong to `group_vo_chains_wholesale` / the chains front, **[HAVE]** there:
Clicars · Carplus · Flexicar · OcasiónPlus · Autohero (AUTO1) · Crestanevada · unoauto.

---

## 4. Channel-family: OEM OFFICIAL NEW-CAR + km0 STOCK (`oem_new_stock`)

A genuinely new front: every existing OEM connector was `oem_vo_portal` (certified **used**).
There was **zero** OEM-official **new-car** coverage before this campaign. `source_group=
oem_dealer_network`, `segment='new'` on the edge.

**NEWLY-CONNECTED = seat_cupra_new** — SEAT + CUPRA official "Localizador de Stock" (VW-Group
VTP REST API). **2.229 brand-new cars** (Seat 1145 + CUPRA 1063 from full drain + 21 from a
fresh sort-rotation re-run), **163 distinct official dealers** (geo-resolved by dealer zip →
INE province), VAM TRUSTWORTHY. Connector `pipeline/platform/oem_seat_cupra_new_stock.py`,
recipe `countries/ES/recipes/CDP-ES-00-5R30HVA7.yaml`, `defense_tier=t0_open` (the `x-pattern`
header is the only gate; €0, no proxy/browser/token). **DB-wide `segment=new` grew 6.151 →
8.380** (verified live: 8.380 edges).

> Honest ceiling: 2.229 caged vs ~2.747 source-declared — the VTP search has no stable
> cursor; a single PRICE_SALE/ASC walk repeats ~half each page boundary. Closing the gap needs
> multi-sort / per-model facet union on `carid`. Declared, not hidden.

### Universe map (have / missing / reachability)

| Brand / group | Official new-stock surface | Status |
|---|---|---|
| **SEAT** | seat.es/localizador-stock (VTP `stesnwb`/`seatwebfe`) | **NEWLY-CONNECTED** (built) |
| **CUPRA** | cupra.com/es-es/localizador-stock (VTP `cuesnwb`/`cuprawebfe`) | **NEWLY-CONNECTED** (built) |
| Volkswagen | volkswagen.es/.../stock.html (feature-app `stock-resultados`) | **MISSING — reachable**, needs ES XHR capture |
| Audi | audi.es/buscador-de-stock-nuevo (`omnigraph.audi.com/graphql`) | **MISSING — reachable** (400 CSRF on bare GET → POST + anti-CSRF); ~4.000 new cars declared |
| Škoda | skodastock.com/resultados | **MISSING — reachable**, needs XHR capture |
| Renault / Dacia | renault.es/renault-webstore (`rvp-datahub…wrd-aws.com`) | **MISSING — reachable** (403 AccessDenied → signed path/params); ~4.000 permanent new-stock |
| Toyota / Lexus | toyota.es NSC (`kong-proxy…toyota-europe.com/dxp/dealers/api`) | **MISSING — reachable**; mirror existing USC/VO recipe |
| Stellantis (Peugeot/Citroën/Opel/DS/Fiat) | brand "compra online / stock" | **MISSING — reachable** (sibling of spoticar VO backend) |
| Hyundai | hyundai.com/es stock | **MISSING — reachable** (sibling of hyundai VO `internal_api`) |
| Kia | kia.com/es stock | **MISSING — reachable** (sibling of kia VO `internal_api`) |
| Ford | ford.es stock | **MISSING — reachable** (sibling of ford VO `internal_api`, Akamai t1_soft — JS-soft, not spend-gated) |

> Reachability summary: **genuinely free-unreachable on this front = NONE.** Every MISSING
> brand host is LIVE (returns 403/400/404 with a body, never connection-refused) and gates only
> on request shape — the exact class of gate `x-pattern` was. Same
> Playwright-capture → curl_cffi-replay method that built SEAT/CUPRA applies.

---

## 5. Channel-types REVEALED but NOT YET in the taxonomy (empty kind / no slot)

### 5.1 `importador` — kind EXISTS, **0 ENTITIES** (NEW-TYPE, empty)

`kind='importador'` is a real enum value with **zero rows** (verified live: 0). Real,
reachable operators (mostly German VO with ~10–20% saving):

| Operator | Domain | Surface | Status |
|---|---|---|---|
| Raceocasion | raceocasion.es | `[V]` 200, SSR stock | **MISSING — reachable** (curl_cffi) |
| MODRIVE | modrive.com/coches-segunda-mano | `[V]` 200, rich SSR stock | **MISSING — reachable** |
| Europa Automotive | europamotive.com | `[V]` 200, SSR shell, listing JS | **MISSING — reachable** |
| ImportyGarage / DeutscheCars / importarcochesalemania | — | (probe surface) | **MISSING — reachable** |
| TrendCars · Carismatic | — | already in DB as `compraventa` | **RECLASSIFY → importador** |

**Δ:** populate the empty `kind='importador'`; connector = compraventa-mono-owner pattern;
reachable €0 (curl_cffi).

### 5.2 Classic / collector marketplaces — **NEW-TYPE, NO SLOT** (scope pending owner)

No type in the taxonomy and no entities (`%clasico%`/`%classic%` returns only particulares +
one detailing garage). Operators: **ComprococheClasico** (comprococheclasico.es) ·
**AutoClassic24** (autoclassic24.com, global marketplace) · **JJDluxeGarage** ·
**Francisco Pueche** (pueche.com) · plus the verticals in §3.2 (Car & Classic, Miclásico).
**Owner scope decision pending:** if in-scope → new `kind`/`source_group=classic_marketplace`;
if not → declare explicitly excluded. Not built either way until the call is made.

### 5.3 Bank VO aggregator — **MISSING operator (NEW-OP)**

**faciliteacoches.com** — CaixaBank VO platform with financing, "tiendas oficiales" model
aggregating Arval + dealers. `[V]` 200 to curl_cffi chrome131 (403 to plain WebFetch; 764 KB
SSR, dealer attribution + price in HTML). **0 in DB.** `marketplace_motor`/aggregator with
dealer attribution → direct-harvest candidate.

### 5.4 Auto-club VO portal — **MISSING operator (minor)**

**cochesocasion.racc.es** (RACC) — auto-club acting as a VO aggregator. Minor missing operator.

---

## 6. Channel-family: EX-FLEET LEASING / RENTING VO (`leasing_rentacar_exfleet`)

Operators that **sell their own ex-fleet used cars** in Spain. DB family `source_group=
rentacar_vo`, `kind=rent_a_car_vo`. Was 3 members (OK Mobility, Centauro, Record Go);
**now 6** (verified live) after this campaign added **Arval AutoSelect, Northgate Ocasión,
Athlon Car Outlet**. (+1.280 cars connected: Arval 1.172 + Northgate 108; Athlon caged, stock
drain deferred.)

| Operator | Surface | Status | Cars |
|---|---|---|---|
| OK Mobility | okmobility.com/.../used | **HAVE** | 172 |
| Centauro | ventas.centauro.net/coches-ocasion | **HAVE** | 28 |
| Record Go | recordgoocasion.es/.../segunda-mano | **HAVE** | 18 |
| **Arval AutoSelect** | autoselect.arval.es | **NEWLY-CONNECTED** — JSON Announcements API (`…azurewebsites.net/api/Announcements/4`), `allAnnouncementsCount`=full stock, 85 price-drops, VAM TRUSTWORTHY, recipe `CDP-ES-28-CVV4S3CJ`. Largest ES ex-fleet seller (BNP Paribas) | **1.172** (verified owned) |
| **Northgate Ocasión** | northgate.es/vehiculos-ocasion | **NEWLY-CONNECTED** — AEM catalogsearch JSON POST returns the FULL 108-car array in one call, per-car province, VAM TRUSTWORTHY, recipe `CDP-ES-28-4XKXNTSY` | **108** (verified owned) |
| **Athlon Car Outlet** | athloncaroutlet.es/buscar-coches | **NEWLY-CONNECTED (entity) / DRAIN DEFERRED** — entity caged (`rentacar_vo`, `t2_js_challenge`) + recipe `CDP-ES-08-FSZ9HXWX`. 114-car stock is Angular-hydrated SPA (Athlon IRT API; `facets` GET works unauth, `search` POST is undocumented DSL, listing HTML client-rendered) → browser-required hydrate pass deferred. Zero cars fabricated (owned=0 today) | 0 (caged), 114 declared |
| Ayvens used-cars B2C | used-cars.ayvens.com | **UNREACHABLE-empty** — API authenticates but `count:0` for ES/FR/IT (B2C catalogue dormant); live channel is the B2B auction (Carmarket) already in DB | 0 |
| ALD Automotive | = Ayvens (rebrand) | **= Ayvens** | — |
| Alphabet (BMW) Used Cars | alphabet.com | **UNREACHABLE-free** — pro-registration-gated online auction, no public stock | n/a |
| LeasePlan / CarNext | (wound down) | **UNREACHABLE-free** — B2C retail shut 2021 (folded into BCA); pro auctions only | n/a |
| Hertz Ocasión | hertzocasion.es | **UNREACHABLE-free** — landing page only, sale by phone/email (carsalesspain2@hertz.com) | n/a |
| Sixt ES | — | **UNREACHABLE-free** — no ES used-car storefront (DE-only) | n/a |
| Europcar ES | — | **UNREACHABLE-free** — ex-fleet only via pro-gated 2ndmove.es / b2b.2ndmove.eu | n/a |
| Goldcar (Europcar grp) | — | **UNREACHABLE-free** — same disposal route as Europcar | n/a |
| Enterprise / Alamo / Avis | — | **UNREACHABLE-free** — no public ES browsable ex-fleet stock | n/a |

> Naming note: this `rentacar_vo` family now mixes touristic rent-a-car (OK/Centauro/Record)
> with operational leasing/renting (Arval/Northgate/Athlon). The keyword census flagged a
> conceptual `renting_vo` distinction (operational leasing ex-flota vs touristic rent-a-car);
> in the live schema both share `source_group='rentacar_vo'`. Distinction noted, not yet split.

---

## 7. Channel-family: B2B / AUCTION PLATFORMS (`b2b_extra_auctions`)

Beyond the 3 already held (Autorola, BCA, Ayvens Carmarket). Auction group lives under
`source_group='official_registry'` (no dedicated `auction` enum). **HAVE = 3.**
**NEWLY-CONNECTED = Subastacar** (+233 cars, 100% field completeness incl. price + VIN).

| Operator | Domain | Status |
|---|---|---|
| Autorola · BCA España · Ayvens Carmarket | — | **HAVE** |
| **Subastacar** | subastacar.com | **NEWLY-CONNECTED** — `[V]` 200, "238 resultados / 12 págs" SSR + schema.org `vehicle` JSON-LD with explicit `price`, NO login. Connector `pipeline/platform/subastacar_wholesale.py`, `CDP-ES-00-S3K8PK50`, `defense_tier=t0_open`. ONE national `kind='subasta'` entity owns all cars (no per-lot dealer/province on surface). **233 cars** (verified 233 edges), 100% field completeness (make/year/km/price/fuel/transmission/VIN/photo 233/233), VAM TRUSTWORTHY. Idempotent re-run. The ONLY operator in the entire B2B universe with a fully public free-vector stock surface |
| AUTO1.com | auto1.com | **MISSING — GATED** — `/es/cars` 302→`/es/merchant/signin`; ~30k-car stock behind professional login; API credentialed |
| OPENLANE (Adesa) | openlane.eu | **MISSING — GATED** — `/es/findcar` ~6 KB Angular SPA shell, no public data layer; dealer login |
| Manheim España | manheim.es | **MISSING — GATED** — `/vehiculos` 404 on public host; catalog behind buyer login. (Honest wall — no credentials) |
| Alcopa Auction ES | alcopa-auction.es | **MISSING — GATED** — listing host 405/WAF to plain fetch; B2B |
| Northgate Trade / VO | vo.northgate.es | **MISSING — GATED** — root 200 but listing paths 404; login-shaped |
| 2ndMove by Europcar | b2b.2ndmove.eu | **MISSING — GATED** — `[A]` B2B fleet |
| Tartiere B2B | tartiereb2b.com | **MISSING — GATED** — `[A]` dealer-group B2B |
| CarOnSale | caronsale.com | **MISSING — GATED** — Next.js app, login-gated stock |
| AutoProff | autoproff.com | **MISSING — GATED** — `[A]` B2B login, not ES-primary |
| Autobid.de (Auktion & Markt) | autobid.de | **MISSING — GATED** — `[A]` B2B login, DE-primary |
| Copart Spain | copart.es | **MISSING — GATED + salvage** — member-login auction for damaged vehicles (different vertical) |
| Veiko | veiko.es | **MISSING — partial SSR** — bidding/portal login-shaped (deferred, not a clean free catalog) |
| LocalizaVO | localizavo.es | **MISSING — partial SSR** — Localiza rent-a-car VO remarketing; login-shaped; overlaps §6 rentacar_vo (deferred) |
| CarCollect | carcollect.com/es | **MISSING — reachable** (per keyword census: 200, app JS; SSR/JS, leasing+dealers offer) |
| Aucto | aucto.es | **UNREACHABLE** — DNS does not resolve / connection refused |
| Ucars | ucars.es | **UNREACHABLE** — DNS does not resolve (ucars.com is an unrelated generic shell) |
| EpicAuctions | — | **UNREACHABLE** — no identifiable ES car-auction operator resolves under the name |
| Carmen | — | **UNREACHABLE** — no ES car-auction operator under the name (carmen.io unrelated) |
| Reezocar | reezocar.com | **OUT OF SCOPE** — French consumer car-import aggregator, not an ES B2B auction (`/used-cars` 404) |

> **Manheim** is a deliberate honest hole: real B2B operator, catalog behind a buyer login,
> no credentials → not reachable by a free vector. No stock fabricated.

---

## 8. Honest residue & Δ actionable (consolidated)

**Genuine holes / not-reachable-free (declared, not faked):**
- **B2B auctions GATED:** AUTO1, OPENLANE/Adesa, Manheim ES, Alcopa, 2ndMove, Tartiere,
  CarOnSale, AutoProff, Autobid, Northgate Trade, Copart (salvage) — all behind professional
  login; no free anonymous catalog. **UNREACHABLE:** Aucto, Ucars (dead DNS), EpicAuctions,
  Carmen (no real ES operator). **OUT OF SCOPE:** Reezocar.
- **Ex-fleet UNREACHABLE-free:** Ayvens B2C (count:0), Alphabet (pro-auction), LeasePlan/CarNext
  (wound down), Hertz (phone/email), Sixt (DE-only), Europcar/Goldcar (2ndmove pro-gate),
  Enterprise/Alamo/Avis (no public ES surface).
- **Athlon Car Outlet:** entity caged, 114-car drain DEFERRED (Angular SPA, browser-required).
- **Motorflash:** full ~1.044-dealer / ~50k-car drain governor-gated (proof slice done; 187 edges live).
- **OEM new-stock:** SEAT/CUPRA built; VW/Audi/Škoda/Renault/Toyota/Stellantis/Hyundai/Kia/Ford
  all reachable-MISSING (one-time XHR discovery each, €0).
- **Social media (Facebook Marketplace / Instagram):** **DEFERRED — excluded by owner mandate.**

**Δ to apply (for the Director):**
1. Populate `kind='importador'` (Raceocasion, MODRIVE, Europa Automotive, ImportyGarage,
   DeutscheCars) + reclassify TrendCars/Carismatic. — €0, reachable.
2. Connect **faciliteacoches.com** (CaixaBank VO aggregator, curl_cffi, dealer attribution).
3. Decide **classic-marketplace** scope; if in-scope, create `classic_marketplace` type and
   connect ComprococheClasico/AutoClassic24/JJDluxeGarage/Pueche (+ Car & Classic, Miclásico).
4. Build the reachable OEM new-stock siblings (VW/Audi/Škoda highest yield, then Renault Webstore,
   then Toyota NSC, then Stellantis/Hyundai/Kia/Ford).
5. Add **RACC ocasión** (minor auto-club VO operator).
6. Add reachable B2B auctions where a free vector exists (**CarCollect**); keep Manheim and the
   rest declared GATED until credentials/spend authorized.
7. Finish the deferred browser drains: **Athlon** (114) and **Motorflash** full (~50k).
8. Consider splitting `rentacar_vo` into touristic rent-a-car vs operational `renting_vo` leasing.

---

## 9. Campaign scorecard (net cars connected this taxonomy run)

| Front | Newly-connected operator(s) | Net cars | VAM |
|---|---|---|---|
| `marketplaces_extra` | Motorflash | +44 (proof slice; 187 edges live) | TRUSTWORTHY |
| `oem_new_stock` | seat_cupra_new (SEAT+CUPRA) | +2.229 (segment=new; DB-wide new 6.151→8.380) | TRUSTWORTHY |
| `leasing_rentacar_exfleet` | Arval AutoSelect + Northgate Ocasión (+ Athlon caged) | +1.280 (1.172+108; Athlon drain deferred) | TRUSTWORTHY |
| `b2b_extra_auctions` | Subastacar | +233 (100% field completeness) | TRUSTWORTHY |
| `keyword_census` | — (mapping pass; revealed renting_vo / importador-empty / classic-no-slot / faciliteacoches / RACC) | +0 | — |
| **TOTAL** | **5 operators connected across 4 fronts** | **≈ +3.786 cars** (counting Motorflash proof slice) | all TRUSTWORTHY |

> `platform`/`plataforma` entity count: **10 → 13** (Motorflash, Subastacar, seat_cupra_new).
> `rentacar_vo` members: **3 → 6** (Arval, Northgate, Athlon). `segment=new` edges:
> **6.151 → 8.380** live. All counts re-verified by direct DB query 2026-06-13.
</content>
</invoke>
