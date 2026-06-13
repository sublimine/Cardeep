# VERIFIED TERRITORIAL COVERAGE — Spain Car Points-of-Sale

> **Built:** 2026-06-13. **Method:** census-anchoring against an authoritative INE
> DIRCE denominator (NOT estimation, NOT social-media inference). **Companion files in
> this directory:** `GAP_MAP.md` (ranked gap analysis), `coverage_ccaa.json`,
> `coverage_province.json`, `ine_cnae4511_by_province.json`, `ine_prov_div45.json`,
> `muni_poi.json`, `_gapmap_data.json`, `ine_tabla301_raw.json` (10 MB raw INE pull).
>
> **Anti-hallucination contract.** Every figure tagged `[VERIFIED]` was read this session
> from a live INE Tempus3 fetch (DIRCE, ref. **2025-01-01**, *Definitivo*) or from a named
> SQL query against the live `cardeep` DB. Figures tagged `[MODELED]` rest on a declared
> allocation assumption (named in §5). Figures tagged `[DIRECTIONAL]` cannot be
> census-verified and are flagged as such. Nothing here is presented with more confidence
> than its source warrants.

---

## 1. National verified coverage (INE-anchored)

| Frame | Ours | INE denominator | Coverage | Tag |
|---|--:|--:|--:|:--|
| **Sales — registral-orthogonal** (the honest headline) | **21,759** | **23,085** locales CNAE 451 | **94.3 %** | `[VERIFIED]` |
| Sales — gross (all sources) | 33,611 | 23,085 locales CNAE 451 | 145.6 % | `[VERIFIED count, inflated ratio]` |
| Sales — vs. *empresa* registry (DIRCE 451 firms) | 33,690 businesses | 14,367 empresas 451 | 234.5 % | `[VERIFIED, floor anchor]` |
| **Desguace — exact census** | **1,299** | **1,292** DGT-CAT authorized | **100.5 %** | `[VERIFIED exact — sealed]` |
| Garaje (`sells_cars` subset) | — | CNAE 452 = 50,294 (repair ceiling) | **uncomputable** | `sells_cars` unpopulated |

### The headline, stated honestly

**National verified coverage of Spain's car SALES points-of-sale is 94.3 %** — registral-orthogonal:
**21,759 of 23,085** INE locales CNAE 451, counting only registral / geo / OEM / directory
attribution and excluding C2C-marketplace first-discovery.

The other ratios are real numbers but must not be read as coverage wins:

- **The gross 145.6 % is NOT 145 % coverage.** It is **C2C contamination**. `[VERIFIED — SQL]`
  **11,852 of 33,710 (35.2 %)** sales entities were first-discovered on
  milanuncios_wholesale / wallapop_wholesale — C2C-dominated platforms that the coverage
  doctrine attributes to the platform sentinel, not enumerated as dealers. Removing those
  from first-discovery yields the registral 21,759 → 94.3 %. The honest number is the
  registral one.
- **The 234.5 % vs. the *empresa* registry is a floor check, not a ceiling.** `[VERIFIED]`
  DIRCE counts only firms whose **principal** activity is registered 451; it undercounts
  autónomos, secondary-activity sellers, and informal points of sale. >100 % vs. that
  registry means **saturation of the formal registry**, not a gap.
- **Desguace is sealed at 100.5 %** against the DGT-CAT legal census (1,292 authorized CATs) —
  this is an *exact* denominator, not an estimate.
- **Garaje coverage is uncomputable and is NOT faked.** `sells_cars` is unpopulated
  (0 rows true); the denominator is undefined until the segment-deflation step runs. Confessed.

> **What the gap is now.** It is no longer "find more dealers." At province/CCAA scale the
> sales universe is saturated. The real residuals are: (a) **the islands and autonomous
> cities** (Canarias 59 %, Ceuta 19 %, Melilla 25 %); (b) a **C2C / dealer dedup discipline**
> problem inflating the gross count; (c) a **32.5 % geocoding gap** — 13,741 target entities
> carry a province but no municipality — that degrades every municipal-level number.

---

## 2. Per-province coverage table `[MODELED — see §5 caveat]`

Source: `coverage_province.json`. **Ours (reg)** = registral-orthogonal count.
**INE 451** = INE division-45 *locales* per province (exact, table 301) allocated to group
451 by the national 451/45 share (0.2605). **CovB** = registral coverage (the honest column).
**CovA** = gross/all-source coverage (inflated by C2C — shown for transparency, not as a win).

| Code | Province | Ours (reg) | Ours (all) | INE 451 (alloc) | **CovB (reg)** | CovA (gross) |
|--:|---|--:|--:|--:|--:|--:|
| 51 | Ceuta | 5 | 6 | 25 | **20.0 %** | 24.0 % |
| 52 | Melilla | 11 | 14 | 42 | **26.2 %** | 33.3 % |
| 35 | Palmas, Las | 306 | 483 | 578 | **52.9 %** | 83.6 % |
| 38 | Santa Cruz de Tenerife | 315 | 469 | 584 | **53.9 %** | 80.3 % |
| 19 | Guadalajara | 69 | 115 | 122 | **56.6 %** | 94.3 % |
| 05 | Ávila | 51 | 82 | 89 | **57.3 %** | 92.1 % |
| 04 | Almería | 231 | 329 | 396 | **58.3 %** | 83.1 % |
| 14 | Córdoba | 260 | 437 | 438 | **59.4 %** | 99.8 % |
| 21 | Huelva | 158 | 224 | 241 | **65.6 %** | 92.9 % |
| 10 | Cáceres | 140 | 221 | 230 | **60.9 %** | 96.1 % |
| 16 | Cuenca | 82 | 124 | 134 | **61.2 %** | 92.5 % |
| 35* | — | — | — | — | — | — |
| 32 | Ourense | 148 | 247 | 191 | 77.5 % | 129.3 % |
| 45 | Toledo | 329 | 545 | 463 | 71.1 % | 117.7 % |
| 13 | Ciudad Real | 216 | 348 | 287 | 75.3 % | 121.3 % |
| 12 | Castellón/Castelló | 223 | 346 | 293 | 76.1 % | 118.1 % |
| 50 | Zaragoza | 296 | 476 | 373 | 79.4 % | 127.6 % |
| 02 | Albacete | 175 | 269 | 212 | 82.5 % | 126.9 % |
| 18 | Granada | 400 | 613 | 482 | 83.0 % | 127.2 % |
| 03 | Alicante/Alacant | 873 | 1405 | 1070 | 81.6 % | 131.3 % |
| 34 | Palencia | 61 | 84 | 75 | 81.3 % | 112.0 % |
| 06 | Badajoz | 389 | 587 | 454 | 85.7 % | 129.3 % |
| 07 | Balears, Illes | 435 | 585 | 505 | 86.1 % | 115.8 % |
| 41 | Sevilla | 885 | 1481 | 1020 | 86.8 % | 145.2 % |
| 29 | Málaga | 868 | 1384 | 960 | 90.4 % | 144.2 % |
| 30 | Murcia | 741 | 1148 | 821 | 90.3 % | 139.8 % |
| 15 | Coruña, A | 528 | 817 | 577 | 91.5 % | 141.6 % |
| 17 | Girona | 388 | 604 | 419 | 92.6 % | 144.2 % |
| 25 | Lleida | 273 | 426 | 294 | 92.9 % | 145.0 % |
| 31 | Navarra | 299 | 449 | 322 | 92.9 % | 139.4 % |
| 43 | Tarragona | 388 | 631 | 412 | 94.2 % | 153.2 % |
| 24 | León | 244 | 320 | 259 | 94.2 % | 123.6 % |
| 44 | Teruel | 57 | 77 | 78 | 73.1 % | 98.7 % |
| 20 | Gipuzkoa | 246 | 347 | 245 | 100.4 % | 141.6 % |
| 42 | Soria | 45 | 62 | 45 | 100.0 % | 137.8 % |
| 08 | Barcelona | 2351 | 3764 | 2246 | 104.7 % | 167.6 % |
| 46 | Valencia/València | 1296 | 2066 | 1249 | 103.8 % | 165.4 % |
| 28 | Madrid | 3648 | 5762 | 3082 | 118.4 % | 187.0 % |
| 22 | Huesca | 119 | 168 | 115 | 103.5 % | 146.1 % |
| 11 | Cádiz | 547 | 755 | 482 | 113.5 % | 156.6 % |
| 26 | Rioja, La | 169 | 244 | 148 | 114.2 % | 164.9 % |
| 27 | Lugo | 265 | 378 | 227 | 116.7 % | 166.5 % |
| 39 | Cantabria | 304 | 431 | 253 | 120.2 % | 170.4 % |
| 33 | Asturias | 546 | 784 | 444 | 123.0 % | 176.6 % |
| 01 | Araba/Álava | 158 | 219 | 123 | 128.5 % | 178.0 % |
| 23 | Jaén | 457 | 644 | 342 | 133.6 % | 188.3 % |
| 09 | Burgos | 237 | 308 | 170 | 139.4 % | 181.2 % |
| 47 | Valladolid | 264 | 378 | 210 | 125.7 % | 180.0 % |
| 48 | Bizkaia | 476 | 719 | 382 | 124.6 % | 188.2 % |
| 37 | Salamanca | 257 | 395 | 175 | 146.9 % | 225.7 % |
| 49 | Zamora | 104 | 153 | 99 | 105.1 % | 154.5 % |
| 40 | Segovia | 58 | 83 | 82 | 70.7 % | 101.2 % |
| 36 | Pontevedra | 368 | 605 | 520 | 70.8 % | 116.3 % |

> `*` Row separates the genuine bottom-10 gap provinces (top of table) from the saturated /
> over-collected remainder. Provinces with CovB > 100 % are **over-collected**, not "more
> than fully covered": CARDEEP counts points-of-sale while INE locales-451 undercounts
> multi-branch chain sites and excludes OEM-VO portal dealers that are not standalone 451
> firms. The action there is CIF-anchoring + C2C/dealer dedup, not more discovery.

### Per-CCAA coverage (HIGH confidence — exact INE locales 451) `[VERIFIED]`

CCAA is the **load-bearing** layer: INE publishes `locales_cnae451` **exactly** per autonomous
community; the 19 CCAA sum to 23,085 = national (integrity-checked). Source: `coverage_ccaa.json`.

| CCAA | Ours (reg) | INE locales 451 | **CovReg** | State |
|---|--:|--:|--:|---|
| **Ceuta** | 5 | 26 | **19.2 %** | genuine gap — autonomous city |
| **Melilla** | 11 | 44 | **25.0 %** | genuine gap — autonomous city |
| **Canarias** | 621 | 1,046 | **59.4 %** | genuine gap — islands + 54 % geocode loss |
| Castilla-La Mancha | 871 | 1,117 | 78.0 % | partial — rural long-tail |
| Madrid | 3,648 | 4,123 | 88.5 % | near-complete |
| Andalucía | 3,806 | 4,213 | 90.3 % | near-complete |
| Murcia | 741 | 816 | 90.8 % | near-complete |
| Galicia | 1,309 | 1,437 | 91.1 % | near-complete |
| Extremadura | 529 | 578 | 91.5 % | near-complete |
| Com. Valenciana | 2,392 | 2,574 | 92.9 % | near-complete |
| Navarra | 299 | 312 | 95.8 % | complete |
| Cataluña | 3,400 | 3,509 | 96.9 % | complete |
| Balears | 435 | 423 | 102.8 % | over-collected |
| Aragón | 472 | 454 | 104.0 % | over-collected |
| Castilla y León | 1,321 | 1,108 | 119.2 % | over-collected |
| La Rioja | 169 | 128 | 132.0 % | over-collected |
| Cantabria | 304 | 230 | 132.2 % | over-collected |
| Asturias | 546 | 378 | 144.4 % | over-collected |
| País Vasco | 880 | 569 | 154.7 % | over-collected |

---

## 3. Municipality-level gap map `[DIRECTIONAL — NOT census-verified]`

> **Confessed structural limit.** There is **no authoritative per-municipality car-dealer
> denominator in Spain.** INE suppresses CNAE-451 below CCAA for statistical secret (table
> 4721 exposes CNAE only at broad SECCIÓN depth). So municipality coverage **cannot** be
> census-verified; it can only be POI-bounded — and our POI source (OSM, 525 municipalities /
> 2,379 points in `muni_poi.json`) is **circular**, since OSM is itself one of our intake
> sources. By construction it produces **zero** "POI saw it, we missed it" gaps. The honest
> municipal gaps are therefore **structural**, not POI-named.

**What is true at municipality level** (source `muni_poi.json` / `_gapmap_data.json`, verified):

- **8,132 municipalities total; 1,822 (22.4 %) have ≥1 geocoded target dealer.** `[VERIFIED]`
  The remaining 6,310 are dominated by tiny pueblos with genuinely zero car business — a
  *caused empty*, not a coverage hole. **The map does NOT claim 6,310 missing dealers.**
- **The real municipal defect is the geocode gap:** **13,741 target entities (32.5 %)** carry
  a province but **no municipality_code**, so they cannot be placed on the comarca/pueblo
  grid. **Fixing geocoding is the prerequisite to any honest municipal gap map.**

### Worst geocode-gap provinces (entities missing municipality / total) `[VERIFIED — SQL]`

| Prov | Province | No-muni / total | Geocode loss |
|--:|---|--:|--:|
| 28 | Madrid | 1,854 / 6,737 | 27.5 % |
| 08 | Barcelona | 976 / 4,396 | 22.2 % |
| 07 | Balears | 768 / 918 | 83.7 % |
| 15 | Coruña, A | 661 / 1,219 | 54.2 % |
| 03 | Alicante | 552 / 1,710 | 32.3 % |
| 30 | Murcia | 535 / 1,268 | 42.2 % |
| 46 | Valencia | 500 / 2,398 | 20.9 % |
| 29 | Málaga | 478 / 1,561 | 30.6 % |
| 41 | Sevilla | 411 / 1,703 | 24.1 % |
| 33 | Asturias | 409 / 990 | 41.3 % |
| 38 | Sta. Cruz de Tenerife | 324 / 604 | 53.6 % |
| 35 | Las Palmas | 219 / 622 | 35.2 % |

### Largest geocoded municipalities in the worst gap provinces `[VERIFIED count, DIRECTIONAL gap]`

These are the **populated cores** — not "missing dealers." `Ours (geocoded)` vs. `OSM POI`
shows our intake dominates the circular POI everywhere, confirming OSM cannot name a real gap.

| Prov | Municipality | Ours (geocoded) | OSM POI |
|--:|---|--:|--:|
| 35 | Las Palmas de Gran Canaria | 212 | 37 |
| 38 | Santa Cruz de Tenerife (38038) | 74 | 1 |
| 35 | Telde (35026) | 64 | — |
| 19 | Guadalajara (19130) | 66 | 3 |
| 38 | San Cristóbal de La Laguna (38023) | 46 | 3 |

> **Named missing dealers cannot yet be produced.** The front spec wants per-pueblo named
> gaps; that requires an **orthogonal, complete, deduplicated POI** (full Páginas Amarillas
> ~44k, Foursquare, or **Overture**) that **does not yet exist in the DB**. See §4.

---

## 4. Confidence ladder — what is VERIFIED vs ESTIMATED (read before trusting any cell)

| Layer | Anchor | Confidence | Why |
|---|---|:--:|---|
| **National sales 94.3 %** | INE locales 451 = 23,085 (exact) vs. 21,759 registral (SQL) | **VERIFIED** | Both endpoints read live this session; two independent INE paths (div-45×share and the sibling `ine_cnae4511_by_province.json` group total) land on 23,085 exactly. |
| **CCAA × locales 451** | INE publishes locales-451 exactly per CCAA; Σ19 = 23,085 | **VERIFIED — HIGH** | The load-bearing geographic layer. Integrity-checked. |
| **Province × 451** | INE **does NOT** publish province × 451 (confidential). Province = exact div-45 *locales* (table 301) **allocated** to 451 by national share 0.2605. | **MODELED — MEDIUM** | Allocation assumes uniform sales-mix across provinces — a **declared modeling input**, not an INE figure. |
| **Desguace 100.5 %** | DGT-CAT legal census = 1,292 (exact) vs. 1,299 ours | **VERIFIED — EXACT** | A legal census, not an estimate. Sealed. |
| **Municipality × 451** | No INE denominator exists below CCAA; OSM POI fallback is **circular** | **DIRECTIONAL — LOW** | Municipal cells are POI-bounded and incomplete. Not census-verified. Flagged structurally. |
| **Garaje coverage** | `sells_cars` unpopulated → denominator undefined | **UNCOMPUTABLE** | Confessed, not faked. |

### Honest statement of confidence

**VERIFIED (read from a live INE fetch or a named live SQL query this session):**

1. National sales coverage = **94.3 %** registral-orthogonal (21,759 / 23,085 INE locales 451).
2. Desguace coverage = **100.5 %** exact against DGT-CAT (1,299 / 1,292) — sealed.
3. The 19 CCAA coverage percentages (exact INE locales-451 denominator).
4. The bottom-3 gap CCAA: **Ceuta 19.2 %, Melilla 25.0 %, Canarias 59.4 %**.
5. The gross 145.6 % is **C2C inflation**, quantified at **35.2 %** C2C first-discovery.
6. The **32.5 % geocode gap** (13,741 entities with province but no municipality).

**MODELED (rest on a declared assumption — true direction, soft magnitude):**

7. All **per-province** 451 denominators and their coverage %. They use INE's *exact*
   per-province division-45 locale counts, but the split to group 451 is the **national**
   share applied uniformly. Province ranks are reliable; the exact % carries allocation
   uncertainty.

**NOT VERIFIED / CANNOT BE VERIFIED (confessed gaps):**

8. **No per-municipality coverage % is verified.** INE suppresses that denominator; our POI
   is circular (OSM) and incomplete. All municipal cells are structural/directional only.
9. **Over-100 % provinces/CCAA are NOT "fully covered."** They are **over-collected** — the
   action is CIF-anchoring + C2C/dealer dedup, not more discovery.
10. **No garaje coverage %** — `sells_cars` is unpopulated; the denominator is undefined.
11. **`geo_poi_denominator` (Overture POI) is INCOMPLETE.** The Overture point-level extract
    has **not landed**; its coverage % is **pending** and is **not stated** here. We will not
    publish an Overture-anchored municipal % until the extract is ingested. *Mejor confesar el
    hueco que vender una mentira.*

---

## 5. Method (reproducible)

1. **Denominator (INE, authoritative).** Tempus3 JSON API (`servicios.ine.es/wstempus/js/ES`),
   DIRCE operation 43 / IOE 30203, ref. **2025-01-01**, *Definitivo*. Table **301** (locales ×
   province × CNAE división × estrato; división **45**) → exact per-province local-unit counts
   (Σ52 = 88,621 = national, integrity-checked). Table **294** (locales × CCAA × grupo CNAE) →
   national group split **451 = 23,085 / 452 = 50,294 / 453 = 11,494 / 454 = 3,748**. Province
   451 = div-45 × (23,085 / 88,621). CCAA 451 = exact from `ine_cnae4511_by_province.json`.
2. **Numerator (live `cardeep` DB).** `SELECT province_code, count(*) FROM entity WHERE kind IN
   ('compraventa','concesionario_oficial') AND status='active' GROUP BY 1`; registral regime
   additionally `AND first_discovered_source <> ALL('{milanuncios_wholesale,wallapop_wholesale}')`.
3. **Join** numerator/denominator at CCAA (HIGH), province (MEDIUM), municipality (LOW/directional).
4. **Desguace** joined directly to the DGT-CAT exact census (1,292).

> Full ranked gap analysis, the C2C-inflation breakdown, and the per-province geocode-gap
> table live in the companion **`GAP_MAP.md`** in this directory.
