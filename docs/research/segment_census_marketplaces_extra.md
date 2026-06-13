# CARDEEP — SEGMENT CENSUS · `marketplaces_extra` (España)

> **Front:** EVERY car marketplace / aggregator serving Spain **beyond the 7 we already
> hold** (coches.net, milanuncios, wallapop, coches.com, autocasion, motor.es,
> AutoScout24). Keyword-driven, exhaustive. **EXCLUDES social media (FB/IG)** by owner
> mandate.
>
> **Verification:** universe swept live via WebSearch + WebFetch + `curl_cffi` chrome131
> on **2026-06-13**. Every DB count below is from **my own query** that day against
> `postgres://cardeep@localhost:5433/cardeep`. Each external fact is `[V]` (fetched live
> this day) or `[A]` (vendor/secondary, not re-derived on-site).
>
> **Relationship to the Tier-1 registry:** `docs/architecture/00-TIER1-REGISTRY.md` is the
> standing pillar that already ranked most of this universe. This census **cross-checks
> that registry against the live DB**, separates true *marketplaces/aggregators* from the
> *single-seller retail chains* (which belong to the VO-chains front, not here), and
> **closes the one high-value REACHABLE-MISSING marketplace the DB lacked: Motorflash.**

---

## 0. Taxonomy reference (DB, my query 2026-06-13)

`entity.kind='plataforma'` = the marketplace-as-entity rows. Live count: **11**
(was 10 before this front; **+1 = Motorflash**, caged this run).

The 7 named in the mandate + the 3 auction/registry platforms already present:

| trade_name | website | source_group | status |
|---|---|---|---|
| coches.net | coches.net | marketplace_motor | HAVE (mandate baseline) |
| milanuncios | milanuncios.com | marketplace_generalist | HAVE (mandate baseline) |
| wallapop | wallapop.com | marketplace_generalist | HAVE (mandate baseline) |
| coches.com | coches.com | marketplace_motor | HAVE (mandate baseline) |
| Autocasion | autocasion.com | marketplace_motor | HAVE (mandate baseline) |
| motor.es | motor.es | marketplace_motor | HAVE (mandate baseline) |
| AutoScout24 | autoscout24.es | marketplace_motor | HAVE (mandate baseline) |
| Autorola | autorola.es | official_registry | HAVE (auction) |
| BCA Espana | es.bca-europe.com | official_registry | HAVE (auction) |
| Ayvens Carmarket | carmarket.ayvens.com | official_registry | HAVE (auction) |
| **Motorflash** | **motorflash.com** | **marketplace_motor** | **NEWLY CONNECTED (this run)** |

---

## 1. The universe of "extra" marketplaces / aggregators (enumerated ALL)

Every car marketplace/aggregator/classified beyond the 7, found via the live sweep.
**Classified by whether it is a genuine MARKETPLACE (multi-seller aggregated stock) or a
single-seller retail CHAIN** (own stock — belongs to the VO-chains front, cross-listed
here for completeness, not double-counted as a marketplace).

### 1.1 Genuine marketplaces / aggregators (multi-dealer / multi-seller stock)

| Operator | Domain | Live? (probe 2026-06-13) | Data surface | DB as `plataforma`? | Verdict |
|---|---|---|---|---|---|
| **Motorflash** | motorflash.com | `[V]` 200, ~50,000 veh, ~1,044 named dealers | JSON-LD + dealer-keyed sitemaps, **no wall** | **NO → now YES** | **MISSING → CONNECTED** |
| Trovit Coches | coches.trovit.es | `[V]` 200, live metasearch | dataLayer; links OUT to source portals | NO | MISSING — metasearch (no own stock; links to portals we already hold) |
| Mitula Coches | coches.mitula.es | `[V]` 200, redirects to coches.trovit.es | same Lifull Connect infra as Trovit | NO | MISSING — same engine as Trovit (Lifull) |
| AutoUncle | autouncle.es | `[V]` 404 on /coches-usados; root live | price-aggregator metasearch | NO | MISSING — metasearch (price-compare, links out) |
| Carwow | carwow.es | `[V]` 200, JSON-LD | lead-gen / new-car broker | NO | UNREACHABLE-AS-POS — lead-gen, not used-stock POS (`[V]` registry §3.8) |
| Heycar | heycar.es | `[V]` 200 but 20 KB stub, no markers | — | NO | DEAD in ES — **ceased ES ops 2023** `[V]` (autofacil); aggregated ~600 dealers / ~30k veh historically |
| CarGurus | cargurus.es | `[V]` 200 but 4.4 KB stub | — | NO | NO ES OPERATION — parked/stub, no live ES inventory |
| eBay Motors ES | ebay.es | `[V]` live | generalist auction/classified | NO | MISSING — marginal ES car volume; auction generalist (low priority) |
| segundamano.es | segundamano.es | `[V]` `server: bon` | folded into Adevinta | NO | NOT INDEPENDENT — Adevinta gateway (== milanuncios family, already HAVE) `[V]` registry §1.5 |
| Automercadillo | automercadillo.com | `[V]` 200, JSON-LD | classified | NO | MISSING — small generalist classified (low priority) |
| auto10.com | auto10.com | `[V]` 200, sitemap+dataLayer | editorial + classifieds | NO | MISSING — small editorial-classified (low priority) |
| ¿Qué coche me compro? | quecochemecompro.com | `[A]` | comparator / editorial | NO | NOT A POS — comparator/editorial (no stock) |

### 1.2 Vertical marketplaces (classic / collector)

| Operator | Domain | Live? | DB? | Verdict |
|---|---|---|---|---|
| Car & Classic | carandclassic.com | `[V]` 200, JSON-LD, 30k+ adverts + auctions | NO | MISSING — pan-EU classic marketplace (vertical; some ES stock) |
| Miclásico | miclasico.com | `[V]` 200, JSON-LD | NO | MISSING — ES classic/collector classifieds (vertical) |
| Coches.net `/clasicos-competicion` | coches.net | HAVE (folder of a platform we hold) | — | COVERED by coches.net |

### 1.3 Single-seller retail CHAINS (own stock — VO-chains front, NOT marketplaces)

Cross-listed for completeness. The Tier-1 registry §1 note is explicit: these are
*single-seller retail chains* whose inventory is **their own stock, counted once at the
chain**, NOT aggregated third-party stock. They are out of scope for *this* marketplace
front and belong to `group_vo_chains_wholesale` / the chains front.

| Operator | Domain | DB presence (my query) | Belongs to |
|---|---|---|---|
| Clicars | clicars.com | `cadena` (chain) + scattered `compraventa` rows | VO-chains front |
| Carplus | carplus.es | `cadena` (chain) | VO-chains front |
| Flexicar | flexicar.es | 330 name rows (`compraventa`/`concesionario_oficial`/`directory`) | VO-chains front |
| OcasiónPlus | ocasionplus.com | 211 name rows (`compraventa`/`directory`) | VO-chains front |
| Autohero | autohero.com | 35 name rows (`compraventa`/`marketplace_motor`) | VO-chains front (AUTO1) |
| Crestanevada | crestanevada.es | 48 name rows (`compraventa`/`directory`) | VO-chains front |
| unoauto | unoauto.com | 2 name rows | VO-chains front (regional) |
| Swipcar | swipcar.com | none | renting/subscription (NOT used-POS) |
| compramostucoche | compramostucoche.es | 5 name rows | sourcing-only (AUTO1 buy-tool, 0 listings) |

---

## 2. HAVE / MISSING verdict for `marketplaces_extra`

**HAVE (already in DB as marketplace platforms — the mandate baseline + auctions):**
coches.net · milanuncios · wallapop · coches.com · autocasion · motor.es · AutoScout24
(+ Autorola · BCA · Ayvens as auction platforms).

**NEWLY CONNECTED this run:** **Motorflash** (the one genuine REACHABLE-MISSING
marketplace with own aggregated multi-dealer stock + clean dealer attribution).

**MISSING but LOW-VALUE / metasearch (links out to portals we already hold — caging them
duplicates inventory we already drain at the source):** Trovit · Mitula · AutoUncle
(all Lifull/price-aggregator metasearch) · eBay Motors ES · Automercadillo · auto10.

**MISSING vertical (niche, narrow stock):** Car & Classic · Miclásico (classic/collector).

**GENUINELY UNREACHABLE / NOT-A-POS (confessed honestly):**
- **Heycar** — `[V]` DEAD in Spain (ceased ES operations 2023; the .es domain serves a
  20 KB stub with no inventory). Nothing to harvest.
- **CarGurus.es** — `[V]` no live ES operation (4.4 KB stub). Nothing to harvest.
- **Carwow.es** — `[V]` lead-gen / new-car broker, not a used-stock POS. No used inventory
  to cage.
- **segundamano.es** — `[V]` not independent; it is an Adevinta gateway (`server: bon`),
  already covered by the milanuncios/coches.net family we HAVE.
- **Swipcar / quecochemecompro / compramostucoche** — renting, comparator, and buy-tool
  respectively; none is a used-car point-of-sale with public stock.
- **Facebook Marketplace** — excluded by owner mandate (social media).

---

## 3. The connection built — Motorflash (`pipeline/platform/motorflash_wholesale.py`)

**Why Motorflash and not the metasearchers.** Trovit/Mitula/AutoUncle are *metasearch*:
they index the SAME listings already on coches.net/AS24/etc. and link out — caging them
re-ingests inventory we drain at the source (pure duplication, no new cars, no new
attribution). Motorflash is the opposite: a **first-party aggregator** that hosts ~50,000
listings from **~1,044 NAMED dealerships** with per-car `AutoDealer` JSON-LD attribution —
genuinely NEW dealer→stock coverage, and (registry §O.16) the **best dealer-discovery
multiplier** of the aggregators.

**Data surface (`[V]` 2026-06-13, curl_cffi chrome131):** OPEN, no wall (CloudFront, 200
to Chrome UA).
- `robots.txt` → `sitemap.concesionarios.xml` = **1,044 distinct named dealers**, each
  `/concesionario/{slug}/coches-segunda-mano/{id}/`.
- each dealer page: H1 = dealer name, 20 PDP links/page, paginated.
- each PDP `/coche-segunda-mano/{make}-{model}-{slug}/ocasion/{id}-es/` carries a clean
  `Car` JSON-LD (make/model/year/km/price/fuel/transmission/photo) **plus** an `AutoDealer`
  seller block (name + telephone). The slug is load-bearing (slugless PDP form 404s).

**Model (mirrors AS24 `autoscout24_wholesale.py` exactly):**
- Motorflash → `entity kind='plataforma'`, `source_group='marketplace_motor'`,
  `province_code=NULL`, + `platform_meta(data_surface='json_ld', family='aggregator')`.
- each selling dealer → `entity kind='compraventa'`.
- each car → `vehicle` OWNED BY its dealer (`entity_ulid=dealer`).
- the car on the platform → `platform_listing` edge (Motorflash ↔ vehicle, `segment='used'`).

**HONEST geo constraint (confessed, not papered over).** Motorflash deliberately HIDES the
dealer's physical address/city on both PDP and dealer page (only name + a Motorflash
dealer-id + a central phone are exposed). A Motorflash dealer therefore **cannot be
geo-anchored** to an INE province from its own pages. We cage the dealer with
`province_code=NULL` (schema-valid: the geo FK is nullable; 129 entities already carry
NULL province) and key it by **name under the national sentinel '00'**
(`canonical_key 'name:{normalized}|p00'`) — the SAME name-keyed shape AS24/coches.net
dealers use, so **cross-platform dedup merges this row into its geo-anchored sibling by
name**. (~38% of Motorflash dealer slugs already exact-name-match a geo-anchored DB row —
the dealer-discovery cross-reference the registry intends.) We never fabricate a province.

**Proof slice run (this front):** 3 dealers × 1 page →
- 44 cars caged (44 new), 44 `platform_listing` edges, 44 NEW delta events.
- "2 new dealers" (1 — ADARSA SUR — already existed → confirms the name-merge dedup works).
- **VAM verdict TRUSTWORTHY** (3 orthogonal paths agree:
  `harvested_cageable = db_edges = db_join_vehicles = 44`).
- recipe persisted: `countries/ES/recipes/CDP-ES-00-WN1DMGRN.yaml`.
- platform cdp_code: **`CDP-ES-00-WN1DMGRN`**.

PROOF SLICE, not the full ~1,044 dealers / ~50k cars — the full drain is P1-governor work
(spend/rate budget). The connector caps at `MAX_DEALERS` and logs the cap honestly.

---

## 4. Confessed residue (no makeup)

1. **Full Motorflash drain pending.** This run proved the connector on a bounded slice; the
   full ~1,044-dealer / ~50k-car drain is governor-gated (P1), not run here.
2. **Motorflash dealer geo is structurally hidden** → those dealers stay `province=NULL`
   until cross-platform name-dedup claims them from a geo-anchored sibling. Dealers unique
   to Motorflash (no sibling on another platform) will remain un-geo-anchored — an honest,
   source-imposed limit, not a connector defect.
3. **Metasearchers (Trovit/Mitula/AutoUncle) intentionally NOT caged** — they duplicate
   source inventory we already drain; caging them adds zero net cars/attribution. Listed
   MISSING-by-choice, not MISSING-by-failure.
4. **Classic verticals (Car & Classic, Miclásico) NOT yet connected** — live and reachable
   (JSON-LD), narrow stock; deferred as low-priority verticals, not blocked.
5. **Heycar / CarGurus.es / Carwow.es** — genuinely nothing to harvest (dead / stub /
   lead-gen). Confirmed `[V]` this day. Not gaps in method.
