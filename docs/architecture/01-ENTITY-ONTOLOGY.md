# CARDEEP — Entity Ontology & Taxonomy of Car Points-of-Sale · ESPAÑA

> **Pillar doc.** Defines EVERY kind of car point-of-sale in Spain to the last atom:
> precise boundaries, sub-types, discovery sources (from the F1 census), inventory
> model (where each type's stock physically lives), and how every type relates to the
> aggregator platforms. Closes with the IDENTITY/DEDUP model (`cdp_code`) that survives
> cross-source overlap and keeps physical branches distinct.
>
> **Status of the live system as of 2026-06-12 [VERIFIED against the running DB]:**
> 12.862 entities, 4 kinds only — `garaje` 7200, `compraventa` 2753,
> `concesionario_oficial` 1617, `desguace` 1292 — + 39.068 vehicles. The schema
> `migrations/0002` *allows* `plataforma` and `cadena` but **neither is populated**,
> and the inventory pipeline has **no platform entity at all**. The owner's critique is
> correct and reproduced by the data: the current taxonomy is impoverished, the
> attribution `kind` is mis-assigned at ingest, and platforms are not first-class.
> This document is the corrective ground truth that the schema migration and the
> discovery/ingest pipeline must converge to.
>
> Marking discipline: every claim is **[VERIFIED]** (read from repo/DB/live fetch this
> session) or **[ASSUMED]** (inferred, not opened). No placeholders.

---

## 0. Why an ontology at all (the failure it fixes)

A "point of sale of a car" in Spain is **not** one thing. The naïve model
(concesionario + compraventa) collapses ten economically distinct actors into two
buckets and silently mis-attributes the rest. Three concrete failures, all
**[VERIFIED]** in the current repo, prove the cost:

1. **Mis-typing at ingest.** `pipeline/ingest.py` line 52 hardcodes
   `kind = 'concesionario_oficial'` for **every** AutoScout24 "profesional" dealer it
   ingests. But an AS24 `/profesionales/{slug}` seller is frequently a *compraventa*,
   a *garaje that sells*, or a *rent-a-car selling ex-fleet* (e.g. `ok-cars`,
   `autohero-*`, `flexicar-*` all appear verbatim in `data/as24_dealers.json`
   **[VERIFIED]**). Every one of those is now falsely an "official dealership". The
   type is load-bearing for the mandate ("ordered by … with a unique code per dealer")
   and it is currently wrong.

2. **No platform as an entity.** The mandate is explicit: *"the giant marketplaces
   themselves"* are in scope, and *"the same car belongs to a platform AND its selling
   dealer."* The live model has neither a `platform` row nor any vehicle→platform edge.
   `vehicle` links only to one `entity` (the dealer). The dual membership the owner
   demands is **structurally impossible** in the current schema.

3. **Conflated chain vs branch.** `flexicar-grupo-barcelona`, `autohero-valencia`,
   `autohero-malaga`, `autohero-sevilla`, `domingo-alonso-ocasion` +
   `domingo-alonso-ocasion-tenerife` are all separate rows in
   `data/as24_dealers.json` **[VERIFIED]** — they are physical *branches* of a *chain*.
   Nothing in the model expresses "branch-of", so a query for "Flexicar's national
   stock" or "how many points of sale does AUTO1/Autohero operate" cannot be answered.

The ontology below makes type, platform-membership, and chain-membership all
first-class and machine-checkable.

---

## 1. The two universes (restated precisely)

The F1 census (`docs/research/SOURCES_ES.md` §1) splits the market into:

- **ENTITIES** = the *denominator*: physical (and a few purely-digital) actors that
  hold or broker car stock. Floor **~44k** verified, ceiling **~50–90k** with full
  CNAE-45 registral + Google Places. This document is the taxonomy of **this** set.
- **INVENTORY** = the *numerator*: the cars, reachable via (a) **aggregator platforms**
  and (b) **each entity's own web**.

The conceptual error the ontology corrects: **a platform is simultaneously an inventory
channel AND an entity.** It is a channel (you harvest cars through it) *and* a first-class
node in the entity graph (it holds inventory, has a defense posture, gets a `cdp_code`,
fires its own health alerts). Treating it only as a channel is what produced failure #2.

### 1.1 The entity is the unit of recipe, code, delta and resilience

Every entity — whatever its type — is the atomic unit on which the four mandate
systems hang:

| System | Per-entity object |
|---|---|
| Identity | one immutable `cdp_code` |
| Recipe | one versioned `recipe.yaml` (how to harvest *its* stock) |
| Delta | its own NEW/GONE/PRICE/PHOTO/KM event stream |
| Resilience | its source(s) in `source_health`; failure → alert with exact origin |

A type that does not hold or broker stock (e.g. an ITV station, an association) is
**not** an entity — it is a *discovery source* or a *geo-anchor*. The boundary "does
it sell/broker cars?" is the membership test for the entity universe. §3 enumerates the
non-entities explicitly so they are never mis-ingested.

---

## 2. The taxonomy — every entity type with hard boundaries

Eleven entity types, grouped into **physical retail**, **brokered/wholesale**,
**digital-first**, and the **platform** super-type. Each type below carries:
**Definition · Boundary tests (in/out) · Sub-types · Discovery sources (census-keyed) ·
Inventory model (where its stock lives) · Platform relationship.**

The `kind` enum that the schema must hold (superseding the current 6-value CHECK):

```
concesionario_oficial   agente_oficial         compraventa
garaje                   desguace               rent_a_car_vo
subasta                  importador             oem_vo_portal
plataforma               cadena(=organization, see §2.12 — modeled as a relation, not a leaf kind)
```

> **Decision (D-1):** `cadena` is **not** a leaf `kind`. A chain is an *organization*
> that owns N physical entities; modeling it as a sibling `kind` (current schema) forces
> a false either/or ("is Flexicar a *compraventa* or a *cadena*?"). The correct model is
> an `organization` row + an `entity.org_id` FK; each Flexicar branch keeps its true leaf
> kind (`compraventa`) AND points to the Flexicar org. See §2.12 and §6.4.

> **Decision (D-2):** `plataforma` **is** a leaf `kind` (a platform is a real entity that
> holds inventory), but it is additionally flagged `is_tier1` when its defense is hard,
> and it never shares recipe/raw-store/operation with the long-tail (`countries/ES/_tier1/`,
> census §2.2). Platform-ness is a *kind*; tier-1-ness is an orthogonal *defense flag*.

---

### 2.1 `concesionario_oficial` — Official franchised dealership

**Definition.** A business holding a franchise contract with one or more OEMs (marcas)
to sell **new** vehicles of those marcas, almost always with an attached authorized
workshop (servicio oficial) and a used/VO operation. The franchise is the defining
attribute, not the building.

**Boundary — IN:** sells new cars under an OEM franchise; appears in an OEM dealer
locator; FACONAUTO/brand-association member. **OUT:** sells only used cars with no
franchise → `compraventa`; authorized *workshop only*, no sales franchise →
`agente_oficial` or `garaje`; sells new cars of a marca it does **not** have a contract
with (grey/parallel import) → `importador`.

**Sub-types.** `monomarca` (single OEM) · `multimarca_oficial` (several franchises under
one CIF/group) · `flagship/store` (urban brand store, e.g. brand "City" formats) ·
`VN-only` vs `VN+VO` (some split VO into a sister `compraventa` CIF — see the
`comercial-anaca` / `comercial-anaca-vn` pair in `data/as24_dealers.json` **[VERIFIED]**,
two rows = the VN arm and the general arm of one group).

**Discovery sources (census §3.3).** OEM dealer-locator **JSON APIs without auth**
[VERIFIED in census §7]: Kia 242, MG 212, BYD 106; OEM **network sitemaps**: SEAT 166
subsites, Skoda 215, Toyota 98 groups, Dacia ~150-200, Peugeot 275. Associations:
FACONAUTO gateway (2.018 franchised dealers + 3.642 agentes), AMDA Madrid 147, Gremi
BCN. Cross-confirm: Páginas Amarillas "concesionarios" 11.202 (incl. multimarca noise).
Registral: CNAE **4511** + DGT transfers.

**Inventory model.** New-car stock is rarely web-exposed as a live feed (configurators,
not listings). The harvestable inventory is the **VO (used) stock**, which lives in two
places: (a) the dealer's own web/DMS, and (b) the **OEM VO central portal**
(`oem_vo_portal`, §2.9) where the same cars are re-listed dealer-attributed. New-vehicle
stock is, for v1, **out of inventory scope** (no reliable public live feed); the entity
is still fully catalogued.

> **VN is a DECLARED inventory-shape gap, not silence `[adversarial GAP-4]`.** A
> `concesionario_oficial`'s economically primary inventory is often VN (configurable new cars), yet
> the mandate is "extract ALL its stock". So VN is now a **first-class declared gap**, never a silent
> omission that lets a province read SEALED while every official dealer's new-car inventory is
> invisible:
> - A new `inventory_shape` value **`new_vehicle`** joins `{retail, auction, parts}`. An official
>   dealer is `NUMERATOR-SEALED` on its **VO** numerator with an explicit
>   `declared_gap{cause:'VN-no-live-feed', shape:'new_vehicle'}` recorded on the entity; the province
>   seal carries the VN gap **itemized** (MASTER_PLAN §6.2/§6.3), never reported as covered.
> - **km0 / pre-registration cars are VO for our purposes** — they ARE web-exposed (coches.com, AS24,
>   coches.net all list km0). They get `kind` unchanged, `inventory_shape='retail'`, a
>   `vehicle_spec.km0=true` flag, and are **harvested and sealed like any VO**. Only true VN
>   configurator stock (no public live listing) is the declared gap. This resolves the VN/VO boundary
>   blur the km0 segment creates.

**Platform relationship.** Strong. The same dealer + its VO stock is mirrored on AS24,
coches.net, coches.com, the OEM VO portal, and often Spoticar/Das WeltAuto/renew. One
physical concesionario ⇒ N platform memberships for the same cars (§4).

---

### 2.2 `agente_oficial` — Official brand agent / satellite point

**Definition.** A smaller authorized point operating *under* a concesionario_oficial's
franchise umbrella (the OEM's "agente"/"servicio") — sells new cars as an agent of the
main dealer, or services them, without holding the franchise contract itself. FACONAUTO
sizes this universe at **3.642 agentes** distinct from the 2.018 franchised dealers
[VERIFIED in census §3.2].

**Boundary — IN:** listed by an OEM as an *agente* / satellite, not a *concesionario*;
economically dependent on a parent dealer. **OUT:** independent franchise →
`concesionario_oficial`; pure workshop with no brand agency → `garaje`.

**Sub-types.** `agente_ventas` (sells new under agency) · `servicio_oficial`
(authorized service, may broker VO).

**Discovery sources.** Same OEM locators as §2.1 (they tag dealer vs agente), FACONAUTO.

**Inventory model.** Usually inherits the parent dealer's VO listing; rarely an
independent feed. Often best modeled as a branch (`org_id`) of its parent group (§6.4).

> **Numerator-seal rule for agente_oficial `[adversarial GAP-11]`.** 3,642 agentes (LARGER than the
> 2,018 franchised dealers — the second-biggest official population) must not be left with an
> undefined numerator seal or an undefined double-count relationship with their parent. The rule:
> - **Inherited stock → `caused-inherited`.** An agente whose cars surface under the parent dealer's
>   profile (no independent feed) is `NUMERATOR-SEALED` as **`caused-inherited`**: its cars are owned
>   by and counted against the **PARENT** entity (never double-counted), and the agente carries a
>   `served_via:<parent cdp_code>` pointer. The agente is a real POS (counts in the *denominator*)
>   but contributes **zero independent numerator rows** — so the parent's stock is not inflated.
> - **Independent feed → sealed on its own numerator** like any dealer (its own `vehicle` rows).
> - **Neither → `caused-zero`** (verified no independent online stock), TRUSTWORTHY.
> No agente double-counts the parent; none is left in the forbidden `unknown` state.

**Platform relationship.** Weak/derivative — its cars typically surface under the parent
concesionario's platform profile, not its own. Important for the *denominator* (a real
point of sale), light for the *numerator*.

> **Decision (D-3):** split `agente_oficial` out of `concesionario_oficial` because the
> census counts them separately (2.018 vs 3.642) and they differ in inventory autonomy.
> Collapsing them would double-count the franchised universe and lose the distinction the
> owner cares about ("from the giant platform to the lost mountain garage").

---

### 2.3 `compraventa` — Independent used-car trader

**Definition.** A business whose core activity is buying and selling **used** vehicles
(VO), with **no** OEM franchise. The classic independent lot. The largest *retail* type
by economic relevance and the messiest to bound.

**Boundary — IN:** sells used cars, no franchise, retail to public; CNAE **4519/4520**
adjacent, often **4511** mis-tagged. **OUT:** holds a franchise → `concesionario_oficial`;
sells primarily its own dismantled-vehicle parts → `desguace`; rents and sells ex-fleet
under a rental brand → `rent_a_car_vo`; buys/sells only wholesale to professionals via
auctions → `subasta`/B2B trader.

**Sub-types.** `independiente` (single lot) · `multimarca` · `chain_branch` (branch of a
used-car chain — Flexicar, OcasiónPlus, Clicars/Autohero; modeled via `org_id`, §2.12) ·
`gestor/intermediario` (brokers cars it does not stock — boundary with digital-first §2.8).

**Discovery sources (census §3.1/§3.4/§3.5).** Páginas Amarillas "compraventa" 1.662
[VERIFIED]; chains: Flexicar 283 sedes, OcasiónPlus 120, AUTO1/compramostucoche 107,
Crestanevada 32; AS24/coches.net dealer attribution; OSM `shop=car` 3.516; registral CNAE.

**Inventory model.** Stock lives primarily on its **own web (CMS/DMS family)** *and*
heavily on **aggregator platforms** (AS24, coches.net, wallapop PRO, milanuncios PRO).
For chains, on a **mono-dealer/mono-chain sitemap** (census §2.1: Flexicar, OcasiónPlus).

**Platform relationship.** The strongest of all types — the compraventa long-tail is
*defined* by its platform presence; many have no real own-web inventory and exist to the
data only through aggregators. This is why AS24 (278k, dealer-attributed) is the census's
#1 strategic asset for this type.

---

### 2.4 `garaje` — Workshop/garage that also sells cars

**Definition.** A repair workshop (taller mecánico/chapa) whose **primary** activity is
service, but which **also sells** a handful of used cars (taken in trade, consignment, or
owner stock). The "lost mountain garage" of the mandate.

**Boundary — IN:** registered as a taller (CCAA workshop registry, CNAE **4520**) AND has
any car-sale signal (listings, "venta" on site, AS24/wallapop presence). **OUT:** workshop
with **zero** sale signal → *non-entity* for Cardeep (a pure taller is not a point of sale;
it is at most a geo-anchor) — this filter is mandatory and currently **not applied**: the
live DB has 7200 `garaje` rows largely seeded from OSM `shop=car_repair` (7.847 POIs,
census §3.4) with **no sells-cars filter** [VERIFIED: `osm` is the largest source at
9.956 attestations]. Many of those 7200 are pure workshops that should be reclassified
out of the entity universe or flagged `sells_cars=false`.

**Sub-types.** `taller_con_venta` (services + sells) · `taller_consignacion` (sells on
consignment only). A pure `taller` is explicitly **not** a sub-type — it is a non-entity
(§3).

**Discovery sources.** CCAA workshop registries [VERIFIED]: Cataluña RASIC 12.155,
Castilla y León ~6.714, CETRAA gateway ~20.000; PA "talleres" 29.955; OSM
`shop=car_repair` 7.847. **All of these over-collect** — they list every workshop, not
only the selling subset. The garaje pipeline MUST gate on a sale signal.

**Inventory model.** Tiny, volatile stock; lives on the **own web (often none)** or a
**handful of aggregator listings**. Lowest cars-per-entity of any retail type.

**Platform relationship.** Sparse — a few listings on wallapop/milanuncios/AS24. Many
have no platform presence at all; for those the only inventory route is own-web (often
absent), so they may be entities with **zero** harvestable inventory (catalogued, not
harvested) — a legitimate, expected state.

> **Decision (D-4):** keep `garaje` as a kind but add an `entity.sells_cars BOOLEAN`
> gate and reclassify the OSM-seeded pure workshops. The denominator must not be inflated
> by 30k non-selling talleres (the census §6 already warns the "~30k" talleres figure is
> "subset that sells, to be filtered").

---

### 2.5 `desguace` — Scrapyard / authorized treatment facility (CAT)

**Definition.** A facility that dismantles end-of-life vehicles and sells **parts**, and
sometimes whole used/salvage vehicles. Legally a **CAT** (Centro Autorizado de
Tratamiento) under the DGT/end-of-life-vehicle regime.

**Boundary — IN:** in the DGT CAT census (the legal truth, **1.292** [VERIFIED, exact,
census §7]) OR a recognized desguace directory. **OUT:** sells whole used cars with no
dismantling → `compraventa`; pure parts e-commerce with no physical CAT → grey area, flag
`desguace_online`.

**Sub-types.** `cat_oficial` (in DGT census — the authoritative set) · `desguace_directorio`
(in commercial directories but not necessarily a DGT CAT — treat as *unverified* until
matched to a CAT) · `desguace_online` (parts marketplace).

**Discovery sources (census §3.5).** **DGT CAT FeatureServer = the truth, 1.292**
[VERIFIED]. Enrich: DesguacesDirecto 1.386 (clean sitemap), DesguacesOficiales ~2.049,
AEDRA 615, SIGRAUTO 595+25, Opisto 449, AETRAC (Cataluña) 107-130.

**Inventory model.** Two distinct stocks: **parts** (the primary, high-volume inventory —
on platforms like Opisto and own-web) and **whole salvage/used vehicles** (secondary). The
mandate is car points-of-sale, so the **car** inventory (whole vehicles) is the v1 target;
parts inventory is a documented v2 extension, not v1 scope.

**Platform relationship.** Distinct platform ecosystem (Opisto, Ovoko, RecOpart) separate
from the car-retail aggregators. A desguace's *parts* live on parts-platforms; its *whole
cars* (if any) may appear on car aggregators.

> **Decision (D-5):** the DGT-census CAT set (1.292) is the **only** `status='active'`
> desguace truth; directory desguaces beyond it are ingested as `status='unverified'`
> until cross-matched to a CAT by CIF/name+geo. Prevents the directory over-count (2.049)
> from polluting the legal denominator.

---

### 2.6 `rent_a_car_vo` — Rental company selling ex-fleet vehicles

**Definition.** A vehicle-rental company that periodically **sells its ex-fleet**
(de-fleeted, ~2 years / 30–90k km) directly to the public through a dedicated VO channel.
A first-class type because the *source* of the stock (own rental fleet) and the *cadence*
(fleet-renewal batches) are structurally different from a compraventa.

**Boundary — IN:** operates a rental brand AND runs a public ex-fleet sales channel.
**[VERIFIED 2026-06-12 live]:** OK Mobility (`okmobility.com/buy-car/used`, up to 36-month
warranty), Centauro (`centauro.net/...vehiculos-de-ocasion`, "2y avg / 30–90k km"), Record
Go (`recordgoocasion.es`, "procedentes de nuestra flota"); also Goldcar, Europcar Selección,
Sixt, Enterprise/Centauro. **OUT:** a rental company with no public used-sales channel →
*non-entity* (it's a fleet operator, not a point of sale).

**Sub-types.** `vendor_directo` (own VO storefront) · `vendor_via_chain` (de-fleets through
a third-party chain) · `vendor_via_auction` (de-fleets only B2B → its cars surface under
`subasta`, not retail).

**Discovery sources.** Brand VO portals (own web); cross-listed on aggregators —
**[VERIFIED]** OK Mobility appears as a `concesionario` on coches.net
(`coches.net/concesionario/okmobilitybarcelona/`) and as a seller "OK Cars 394" on
autocasionmallorca; AS24 `ok-cars`/`okmobility` slugs. No clean census source — discovered
by a curated brand list (~10-15 brands) + aggregator seller-name matching.

**Inventory model.** Stock lives on the **brand VO portal** (own web) and is **mirrored on
aggregators** under the rental brand's seller profile. Multi-site: a rental brand sells from
several physical delivery points / chain branches.

**Platform relationship.** Strong and *deceptive* — because they list on coches.net/AS24
under a "concesionario"/"profesional" seller, the naïve pipeline **mis-types them as
`concesionario_oficial`** (exactly failure #1). The ontology must catch the rental brand by
name-list and override the platform's seller-type label.

> **Decision (D-6):** `rent_a_car_vo` is its own kind, resolved by a **curated brand
> allow-list** applied *after* platform ingest to override the seller-type label the
> platform asserts. The platform's own "dealer type" field is **not trusted** for typing
> (it called OK Mobility a concesionario).

---

### 2.7 `subasta` — B2B / B2C vehicle auction house & platform

**Definition.** An auction operator whose "inventory" is **lots** offered for bidding,
sourced from fleets, renting, rent-a-car, banks (repos), insurers (siniestros), and OEMs.
Mostly **B2B** (professionals only) but some B2C.

**Boundary — IN:** runs vehicle auctions (physical centers and/or online); stock is
time-boxed lots, not fixed-price listings. **[VERIFIED 2026-06-12 live]:** BCA España
(~700 vehicles/week, professional-only, physical centers Azuqueca, Bellvei, La Luisiana,
Alicante), Autorola (10.198 vehicles "in process", 70k+ buyers), Adesa. **OUT:** fixed-price
retail to public → `compraventa`/`plataforma`; a fleet that *uses* auctions but doesn't run
them → its cars are *attributed* to the auction as the channel, the fleet is the seller.

**Sub-types.** `auction_b2b` (BCA, Autorola, Adesa — pros only) · `auction_b2c` (open to
public) · `auction_physical_center` (a BCA branch = a physical POS with a `cdp_code`) ·
`auction_online_platform` (Autorola = a platform-kind overlap, see relation below).

**Discovery sources.** Curated operator list (BCA, Autorola, Adesa, Hammer, Vavato/TBAuction,
SAFO, salvage operators); BCA physical centers as geo-located branches; Autorola/BCA
sale-calendar APIs for lots. No census row yet — **new discovery target this ontology adds.**

**Inventory model.** **Lots**, not listings: each lot has a vehicle, an auction window
(start/end), a current/closing price, a seller (fleet/renting/bank) and a location
(physical center). This is a *different shape* from the retail `vehicle` table — it needs an
`auction_lot` overlay (year, km, price, window, seller_ref, status ∈ live/sold/withdrawn).
The delta engine still applies (NEW lot / SOLD / WITHDRAWN / PRICE_CHANGE during bidding).

**Platform relationship.** A `subasta` operator that runs an **online** marketplace
(Autorola, BCA online) is *also* a `plataforma`-shaped entity (it aggregates third-party
stock). Modeled as `kind='subasta'` + `is_platform_like=true` (a flag), reusing the
platform inventory machinery (§2.10) but with the lot overlay. Physical BCA centers are
plain branches.

> **Decision (D-7):** auctions get a `kind='subasta'` AND an `auction_lot` inventory
> overlay distinct from retail `vehicle`. A retail-priced `vehicle` row cannot honestly
> represent a live bid; forcing it would corrupt the price-delta semantics. v1 may catalogue
> the operators + physical centers (denominator) and defer lot-harvest to v2 (numerator).

---

### 2.8 `importador` — Independent importer / grey-market trader

**Definition.** A business that imports vehicles (new or nearly-new) from other EU/non-EU
markets and sells them in Spain **without** holding the OEM's national franchise — parallel
/ grey-channel import, plus genuine specialist importers (US classics, JDM, etc.).

**Boundary — IN:** sells imported vehicles as its model, not under a Spanish franchise;
"importación"/"km0 importado"/"reimportación" signals. **OUT:** franchised dealer importing
through official channels → `concesionario_oficial`; a compraventa that occasionally has an
imported car → `compraventa` (importing is not its model).

**Sub-types.** `km0_importador` (nearly-new EU imports) · `especialista` (classics/JDM/US) ·
`reimportacion`.

**Discovery sources.** Aggregator seller-text signals ("importado", "reimportación"),
specialist directories, CNAE 4511 + import customs signals [ASSUMED — no clean census
source; discovered by text-classification over platform sellers]. Lowest-volume,
highest-ambiguity type.

**Inventory model.** Stock on **own web** + **aggregators** (same channels as compraventa),
flagged by import provenance in the listing text.

**Platform relationship.** Same as compraventa (lists on AS24/coches.net), distinguished
only by inventory provenance, resolved by listing-text classification (local LLM job per
the cost doctrine, ORQUESTACION §coste).

> **Decision (D-8):** `importador` is a kind but is the **last-priority** discovery target
> and is resolved by classifier (local LLM) over already-ingested platform sellers, not by a
> dedicated source. It is real but thin; over-investing in it before the long-tail is closed
> violates the ROI order (census §9).

---

### 2.9 `oem_vo_portal` — OEM central used-vehicle portal

**Definition.** A manufacturer-run **certified-used (VO)** portal that aggregates the VO
stock of that OEM's dealer network, dealer-attributed. Economically it is the OEM acting as
a *platform over its own network* — neither a single dealer nor a neutral aggregator.

**Boundary — IN:** OEM-branded VO program holding multi-dealer attributed stock.
**[VERIFIED census §3.3]:** renew (es.renew.auto, Renault/Dacia, 5.747, HTML SSR
dealer-attributed), Spoticar (6× Stellantis, 6.334, Akamai), Das WeltAuto (Grupo VW, ~10k:
SEAT 4.078 + VW 3.000 + Skoda 1.383 + Cupra 1.459), MB Certified 4.696, Nissan Ocasión
1.546, Hyundai Promise 420, Audi Selection:plus, BMW Premium Selection. **OUT:** a single
dealer's own VO page → that dealer; a neutral multi-OEM aggregator → `plataforma`.

**Sub-types.** `oem_vo_open` (renew, Das WeltAuto — HTML harvestable) · `oem_vo_hard`
(Spoticar/Akamai, MB/Audi browser-walled → tier-1-adjacent).

**Discovery sources.** The portals themselves (census §3.3); they double as **dealer-network
discovery** (each portal lists its participating dealers, attributing stock).

**Inventory model.** **Dealer-attributed aggregated stock** — the portal is the harvest
channel; each car maps to BOTH the OEM portal (as platform-membership) AND the selling
concesionario (the entity). This is the §4 dual-membership in its purest form: renew's 5.747
cars belong to renew (portal) AND to ~N Renault dealers.

**Platform relationship.** It **is** a platform sub-kind, scoped to one OEM's network.
Modeled as `kind='oem_vo_portal'` (a specialization of platform) so queries can separate
"OEM-channel VO" from "neutral-aggregator VO".

> **Decision (D-9):** `oem_vo_portal` is a distinct kind, not folded into `plataforma`,
> because its membership scope (one OEM's network) and its discovery value (it *is* a dealer
> census of that brand) differ fundamentally from a neutral aggregator. Folding it would lose
> the "free network census" the census flags as strategic finding #2.

---

### 2.10 `plataforma` — Neutral aggregator marketplace (first-class entity)

**Definition.** A neutral, multi-seller marketplace that aggregates the stock of many
independent entities (dealers, compraventas, garajes, rent-a-car, even private sellers). It
is a **first-class entity** — it holds inventory, has a defense posture, a `cdp_code`, a
recipe, and its own health/alerting — AND simultaneously the primary **channel** through
which other entities' stock is discovered.

**Boundary — IN:** aggregates ≥2 independent sellers' stock under one marketplace; not OEM-
scoped (that's §2.9). **[VERIFIED census §2]:** open — AS24 278.329, autocasion 121.985,
coches.com ~67.259, motorflash, motor.es 50.935; tier-1 — wallapop 753.652, milanuncios
666.901, coches.net 249.139, spoticar (also §2.9). **OUT:** single-seller "platform"
(OcasiónPlus, Flexicar, Clicars/Autohero — these are *chains* with a marketplace-style site,
modeled as `cadena`/`compraventa`, census §2.1 marks them "mono-dealer/mono-cadena").

**Sub-types.** `aggregator_open` (no hard wall — AS24, autocasion, coches.com, motorflash) ·
`aggregator_tier1` (hard defense — wallapop, milanuncios, coches.net; `is_tier1=true`,
physically separated, census §2.2) · `c2c_marketplace` (wallapop/milanuncios carry private
sellers too — those listings have no entity dealer; see §4.3).

**Discovery sources.** The platform itself (its counter, sitemap, or internal API) — census
§2 catalogues the exact data-layer surface per platform (AS24 `__NEXT_DATA__`, coches.net
`ms-mt--api-web…advgo.net`, wallapop `api.wallapop.com/api/v3/cars/search`).

**Inventory model.** The platform's inventory is the **union of all its sellers' stock**. It
does **not** own cars; it *hosts* them. So a platform's "inventory" is materialized as the
set of `vehicle` rows whose `platform_listing` edge points to it (§4). The platform entity
row carries the *channel* metadata (defense, recipe, counter); the cars hang off the selling
entity and are *linked* to the platform.

**Platform relationship.** It **is** the platform. The reflexive case. A car on AS24 sold by
"Flexicar Barcelona" creates: 1 platform entity (AS24), 1 dealer entity (Flexicar BCN
branch), 1 org (Flexicar), 1 vehicle (owned-by Flexicar BCN), 1 platform_listing edge
(vehicle↔AS24). All four mandate facts ("find it, extract stock, the platform itself, same
car ∈ platform AND dealer") satisfied.

> **Decision (D-10):** the platform is BOTH a `kind='plataforma'` entity row AND a channel.
> The vehicle is owned by the **selling dealer entity** (not the platform); platform
> membership is an **edge** (`platform_listing`), never ownership. This is the single most
> important modeling decision in the pillar — it is what makes "same car ∈ platform AND
> dealer" expressible (failure #2 fixed). See §4.

---

### 2.11 `oem_red` (network root) — does it exist as an entity? **No.**

An OEM *brand* (Kia España, SEAT) is **not** an entity (it sells no cars directly to the
public; it's the franchisor). Its **dealer locator** is a *discovery source*, and its **VO
portal** is the §2.9 entity. The brand itself is recorded as an `organization` of type
`oem` (§6.4) so the network's dealers can be grouped, but it has no `cdp_code` and no
inventory. Documented here to forbid mis-ingesting "Kia" as a point of sale.

---

### 2.12 `cadena` / organization — chains, groups, networks (a relation, not a leaf)

**Definition.** An organization owning/operating **multiple** physical entities: a used-car
chain (Flexicar, OcasiónPlus, Clicars/Autohero, Crestanevada), a multi-franchise dealer
group (Domingo Alonso, Quadis, etc.), a rent-a-car brand (OK Mobility), an OEM (Kia España),
or an auction operator (BCA across its 4 centers).

**Boundary — IN:** ≥2 physical points under common ownership/brand. **OUT:** a single-site
business → no org needed (or a degenerate org of size 1, not created).

**Sub-types of `organization.org_type`.** `chain_compraventa` · `dealer_group` ·
`rentacar_brand` · `oem` · `auction_operator` · `platform_operator`.

**Discovery sources.** Chain sitemaps (Flexicar 283 sedes, OcasiónPlus 263 children),
AS24 multi-branch slug families, FACONAUTO groups, brand sites.

**Inventory model.** An org owns **no inventory directly** — its branches do. Org-level
inventory = union over its branches' inventory (a query, not a stored set). Some chains
expose a single chain-wide sitemap (census §2.1, Flexicar/OcasiónPlus mono-cadena) — that's
one harvest channel feeding N branch entities.

**Platform relationship.** Orthogonal — an org's branches each have their own platform
memberships.

> **Decision (D-11):** model chains as `organization` + `entity.org_id` FK + a leaf `kind`
> on each branch (its true type), **superseding** the current `kind='cadena'` enum value.
> This fixes failure #3 and answers "X's national stock / # of points of sale" with a single
> `WHERE org_id = …`. The `cadena` enum value is **deprecated** (kept readable for migration,
> never newly assigned).

---

## 3. Non-entities — what is in the census but is NOT a point of sale

Explicitly enumerated so they are never ingested as entities (the §2.4 garaje failure shows
the cost of skipping this):

| Census actor | Why NOT an entity | Correct role |
|---|---|---|
| ITV stations (AECA-ITV ~418) | inspect, don't sell | **geo-anchor** for resolution |
| Associations (AEDRA, CETRAA, FACONAUTO, Gremi…) | represent members, sell nothing | **discovery source** (member lists) |
| OEM brand (Kia España, SEAT) | franchisor, no public sale | **organization** (`org_type=oem`), no `cdp_code` |
| Pure taller (no sale signal) | services only | **non-entity** (or geo-anchor); filtered by `sells_cars` |
| Registries (DGT, BORME, INE, RASIC) | enumerate, don't sell | **discovery source** / legal truth |
| Generic directories (PA, OSM, FSQ, Overture) | list, don't sell | **discovery source** + geo enrichment |
| Rental company w/ no VO channel | rents, no public sale | **non-entity** (fleet operator) |
| Parts-only e-commerce (no physical CAT) | parts, not cars | out of v1 scope (`desguace_online` flag) |

The membership predicate, formally: **an actor is a Cardeep entity ⇔ it offers car stock
(retail or auction lots) for acquisition by an external party.** Everything else is a source,
an anchor, or an organization.

---

## 4. The platform ⇄ entity relationship — dual membership ("same car ∈ platform AND dealer")

This is the relationship the owner singled out. The model:

```
organization (chain/group/brand/oem/operator)
   1│ owns
    ▼ N
entity (the SELLING point of sale — has the cdp_code, the kind, the geo)
   1│ owns (a car physically belongs to exactly ONE selling entity)
    ▼ N
vehicle (the car; owned by its selling entity)
   N│ is listed on
    ▼ M           ← platform_listing edge (the dual membership)
entity[kind=plataforma|oem_vo_portal] (the platform/portal it appears on)
```

### 4.1 Ownership vs membership (the invariant)

- A `vehicle` is **owned** by exactly one **selling entity** (the dealer/compraventa/
  rent-a-car). Ownership = `vehicle.entity_ulid`. This never points to a platform.
- A `vehicle` has **0..M platform memberships** via `platform_listing
  (vehicle_ulid, platform_entity_ulid, platform_listing_url, platform_listing_ref,
  first_seen, last_seen, status)`. The **same physical car** listed on AS24 *and*
  coches.net *and* renew = one `vehicle`, three `platform_listing` rows.

### 4.2 Cross-platform vehicle identity (when are two listings the same car?)

The same car appears on multiple platforms with different listing IDs. Match key, in
priority: **VIN** (rare in public data) > **`(make, model, year, km, price-band, photo_hash,
seller_cdp_code)`** fuzzy tuple > none (treat as distinct, accept slight over-count). The
`photo_hash` (already in `vehicle`, `migrations/0003`, pHash) is the strongest practical
cross-platform signal — the same dealer uploads the same photos everywhere. v1: match within
a single seller's stock across platforms (cheap, high-precision); cross-seller is out of
scope.

### 4.3 Private-seller (C2C) listings — the platform-only car

wallapop/milanuncios carry **private** sellers (no dealer entity). Such a listing has a
platform membership but **no owning entity**. Model: a sentinel per-platform "private seller"
entity (`kind=plataforma`, sub `c2c_private`, one synthetic entity per platform) owns all its
C2C cars, so the ownership invariant (every vehicle has exactly one owner) holds without
fabricating fake dealers. The mandate's denominator counts *real* points of sale; C2C cars
are inventory served, attributed to the platform, not to a phantom dealer.

### 4.4 Why the platform must be an entity, not just a channel (recap)

Because the mandate requires serving the platform itself (its own `cdp_code`, its
counter as inventory, its defense posture, its health alert when it breaks). A channel is
config; an entity is a served, coded, monitored, recipe-bearing node. The platform is both;
the entity row is what makes it *served*.

---

## 5. The inventory model per type (where each type's car stock physically lives)

| Kind | Primary stock location | Secondary | Harvest surface (census) | Cars/entity |
|---|---|---|---|---|
| `concesionario_oficial` | OEM VO portal (attributed) | own web/DMS | renew/Spoticar/DasWeltAuto + AS24/coches.net | med-high (VO) |
| `agente_oficial` | parent dealer's listing | — | inherited | low |
| `compraventa` | aggregator platforms | own web (CMS family) | AS24, coches.net, wallapop PRO | med |
| `garaje` | a few aggregator listings | own web (often none) | wallapop/AS24 (sparse) | very low / zero |
| `desguace` | parts platforms (Opisto…) | own web | DGT census (entity) / Opisto (parts) | whole-car: low |
| `rent_a_car_vo` | brand VO portal (own web) | aggregators (brand profile) | brand portal + coches.net/AS24 profile | med-high (batch) |
| `subasta` | auction lots (own platform) | physical center | Autorola/BCA sale-calendar API | high (lots) |
| `importador` | own web + aggregators | — | AS24/coches.net (text-flagged) | low-med |
| `oem_vo_portal` | dealer-attributed aggregate | — | renew (SSR), Das WeltAuto (BFF), Spoticar (Akamai) | high (network) |
| `plataforma` | union of sellers' stock (hosted) | — | platform API/sitemap (census §2) | very high |

**Three structural inventory shapes** (the schema must support all three):

1. **Retail listing** (`vehicle`, fixed price) — every retail type. *(exists today)*
2. **Auction lot** (`auction_lot`, time-boxed bid) — `subasta`. *(new overlay, §2.7)*
3. **Parts** (`part`, per-desguace) — `desguace` v2. *(documented, out of v1 scope)*

The delta engine (NEW/GONE/PRICE/PHOTO/KM, `migrations/0003`) generalizes to all three
(an auction lot's PRICE_CHANGE = a new bid; GONE = SOLD/WITHDRAWN).

---

## 6. Identity & dedup model — `cdp_code` that survives overlap and keeps branches distinct

The entire pillar rests on identity. The current generator
(`services/api/codes.py`, **[VERIFIED]**) is already well-designed; this section formalizes
its guarantees, names its edge cases, and specifies the additions the new types force.

### 6.1 The canonical key (current, verified) and what it gets right

`cdp_code = CDP-ES-{province2}-{base32(sha256(canonical_key))}`, deterministic, so
re-discovery via another source never mints a duplicate. Canonical key priority
(`canonical_key()`):

1. **bare domain** (`dealer.es`, no path) — strongest cross-source identity.
2. **CIF** — registral legal identity.
3. **name + municipality_code (+ address)** — for domain/CIF-less physical POS.

Two correctly-handled subtleties **[VERIFIED in code comments]**:

- A **path-bearing URL** (`hyundai.es/concesionarios/<slug>`) is **rejected** as identity
  and falls through to name+address — because many branches share one OEM portal path. This
  is exactly right and must be preserved for all new portal types (§2.9).
- **Address is appended** to the name+municipality key, so **two branches of the same company
  in one town stay distinct POS**. This is the "distinguish physical branches" guarantee.

### 6.2 The overlap problem the code already solves

The same entity surfaces from N sources (OSM + PA + AS24 + OEM locator). Because
`canonical_key` is source-independent (keyed on domain/CIF/name+geo, not on the source), all
N converge to **one** `cdp_code`; `entity_source` records N attestations (the
capture-recapture substrate, census §6). **[VERIFIED]:** `pipeline/discover.py::_upsert`
does `ON CONFLICT (cdp_code) DO UPDATE last_seen` + inserts `entity_source` — correct.

### 6.3 Edge cases the new taxonomy introduces (and the rule for each)

| Edge case | Risk | Rule |
|---|---|---|
| Rent-a-car branch listed under brand domain `okmobility.com` on every platform | bare-domain key collapses all branches into ONE entity | **D-12:** for multi-branch brands, the bare-domain key is **insufficient**; force the key to `name + municipality_code + address` (skip domain) when `org.org_type ∈ {rentacar_brand, chain_compraventa, dealer_group}`. Branch distinctness > domain convenience. |
| Platform entity itself (AS24) | needs a stable code but has no province | **D-13:** platform/portal/org-root entities get province sentinel `00` → `CDP-ES-00-{hash(domain)}`. They are national, not provincial. |
| VN arm + general arm of one group, same address (`comercial-anaca` / `…-vn`) | distinct CIFs but same site → 1 or 2? | If distinct CIF → 2 entities (CIF wins). If same CIF, same address → 1 entity, 2 aliases. **[VERIFIED data shows 2 AS24 slugs]** → resolve by CIF at registral enrichment. |
| Same dealer, different name spelling across sources | name-key mismatch → duplicate | `entity_alias` (name/domain/cif/phone variants) + normalization (`_normalize`) absorb spelling drift; periodic alias-merge job. *(table exists)* |
| Auction physical center vs the online operator | BCA-Alicante (POS) vs BCA.com (platform) | two entities: center = `subasta` branch (province-coded), operator-site = `plataforma`-like national (`00`), linked by `org_id` (BCA org). |
| C2C private listing | no dealer to key on | sentinel platform-private entity per platform (§4.3), not keyed per-seller. |

### 6.4 Schema additions this ontology requires (delta vs `migrations/0002`)

Stated as the *target*; the actual migration is a sibling pillar's job. This doc is the
contract it must satisfy.

```
-- (a) widen kind to the full taxonomy; deprecate 'cadena'
ALTER entity kind CHECK IN
  ('concesionario_oficial','agente_oficial','compraventa','garaje','desguace',
   'rent_a_car_vo','subasta','importador','oem_vo_portal','plataforma',
   'cadena' /* deprecated, read-only for migration */)

-- (b) organization layer (chains/groups/brands/operators)  [fixes failure #3]
organization(org_ulid PK, org_code UNIQUE, name,
             org_type IN ('chain_compraventa','dealer_group','rentacar_brand',
                          'oem','auction_operator','platform_operator'),
             website, created_at)
entity.org_id  FK -> organization(org_ulid)  NULL   -- branch-of

-- (c) platform membership edge (the dual membership)  [fixes failure #2]
platform_listing(vehicle_ulid FK, platform_entity_ulid FK -> entity,
                 listing_url, listing_ref, first_seen, last_seen,
                 status IN ('listed','removed'),
                 PRIMARY KEY (vehicle_ulid, platform_entity_ulid))

-- (d) sells-cars gate for the garaje filter  [fixes garaje over-count, D-4]
entity.sells_cars  BOOLEAN  DEFAULT NULL   -- NULL=unknown, FALSE=pure taller (non-entity)

-- (e) auction lot overlay  [the third inventory shape, D-7]
auction_lot(lot_ulid PK, entity_ulid FK -> entity[subasta],
            vehicle_descriptor JSONB, auction_open, auction_close,
            current_price, seller_ref, location_center_ulid FK -> entity,
            status IN ('live','sold','withdrawn'))

-- (f) platform-asserted seller-type is advisory, never authoritative  [D-6]
entity.kind_source TEXT  -- 'registral'|'oem_locator'|'curated_brandlist'|'classifier'|'platform_label'
                         -- precedence: registral/locator/brandlist > classifier > platform_label
```

### 6.5 Type-resolution precedence (how `kind` is decided when sources disagree)

The single rule that would have prevented failure #1:

```
1. registral CNAE (4511 franchise vs 4520 workshop vs 4519 trade)   [highest]
2. OEM dealer-locator membership            -> concesionario_oficial / agente_oficial
3. legal census membership                  -> desguace (DGT CAT)
4. curated brand allow-list                 -> rent_a_car_vo / subasta / importador-specialist
5. local-LLM classifier over listing text   -> importador / garaje-sells / compraventa
6. platform-asserted seller label           -> advisory ONLY, never overrides 1-5   [lowest]
```

`entity.kind_source` records which rung decided, so a later higher-precedence signal can
correct it deterministically (and re-emit nothing but a type correction — never a phantom
delta).

---

## 7. Coverage map — every type → its census discovery sources (traceability)

| Kind | Primary census sources (§ in SOURCES_ES.md) | Status |
|---|---|---|
| `concesionario_oficial` | OEM JSON APIs §3.3, FACONAUTO/AMDA/Gremi §3.2, PA §3.4, CNAE 4511 §3.1 | partial (1617 live) |
| `agente_oficial` | OEM locators (dealer/agente tag) §3.3, FACONAUTO §3.2 | **not yet split** |
| `compraventa` | PA §3.4, chains §3.5, AS24/coches.net §2, OSM §3.4 | partial (2753 live) |
| `garaje` | RASIC/CyL/CETRAA §3.1, PA §3.4, OSM §3.4 (+ sells_cars filter) | over-collected (7200, unfiltered) |
| `desguace` | **DGT CAT §3.1 (1.292 truth)**, AEDRA/Opisto/AETRAC §3.5 | done (1292 = DGT exact) |
| `rent_a_car_vo` | curated brand list + aggregator name-match §2 | **new (0 live)** |
| `subasta` | curated operator list (BCA/Autorola/Adesa) | **new (0 live)** |
| `importador` | classifier over platform sellers §2 | **new (0 live)** |
| `oem_vo_portal` | renew/Spoticar/DasWeltAuto/MB/Hyundai §3.3 | **new (0 live)** |
| `plataforma` | §2.1 open + §2.2 tier-1 (the platforms themselves) | **new (0 live as entities)** |
| `organization` | chain sitemaps §2.1/§3.5, OEM roots, operators | **new (0 live)** |

The "new (0 live)" rows are the concrete backlog this ontology hands to discovery: five
entity kinds + the organization layer + the platform-as-entity rows are defined here and
unimplemented in the running system.

---

## 8. Honest residuals (no whitewashing)

1. **`importador` has no clean source.** It is real but discovered only by classifier over
   already-ingested sellers. Acknowledged thin; lowest priority (D-8).
2. **Parts inventory (desguace) is deferred.** v1 catalogues desguaces + whole-car stock;
   the parts marketplace (Opisto/Ovoko) is a documented v2 shape (§5), not built.
3. **Auction lot harvest is v2.** v1 = operators + physical centers (denominator);
   lot-by-lot harvest with the time-boxed overlay is specified (§2.7/§6.4e) but deferred.
4. **Cross-platform same-car matching is single-seller only in v1** (§4.2). Cross-seller
   identity is out of scope and would risk over-merging.
5. **The live `garaje` 7200 is unfiltered.** Until `sells_cars` is populated, that count is
   an over-estimate of true selling garages (D-4). Stated, not hidden.
6. **C2C private-seller volume is huge** (wallapop 753k incl. private). v1 attributes C2C to
   the platform sentinel (§4.3); whether to fully enumerate private sellers is an owner call,
   not assumed here.

---

## 9. Summary — the eleven types, one line each

| Kind | One-line boundary |
|---|---|
| `concesionario_oficial` | holds an OEM new-car franchise |
| `agente_oficial` | authorized agent/satellite under a dealer's franchise |
| `compraventa` | independent used-car trader, no franchise |
| `garaje` | workshop that *also* sells cars (sells_cars=true) |
| `desguace` | CAT scrapyard (DGT-census = legal truth) |
| `rent_a_car_vo` | rental brand selling its ex-fleet to the public |
| `subasta` | auction operator; stock = time-boxed lots |
| `importador` | imports + sells without the national franchise |
| `oem_vo_portal` | OEM central certified-used portal (network-scoped platform) |
| `plataforma` | neutral multi-seller aggregator (first-class entity + channel) |
| `organization` | chain/group/brand/operator owning N entities (relation, not leaf) |

The model satisfies every clause of the mandate: every kind of point of sale defined with
hard boundaries (§2), the platform a first-class entity (§2.10), the same car a member of
both its platform and its dealer (§4), chains/branches distinguished (§2.12, §6.3),
tier-1 separated (D-2), and an identity model that survives cross-source overlap while
keeping physical branches distinct (§6).
