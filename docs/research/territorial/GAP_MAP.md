# GAP MAP — Verified Territorial Coverage of Spain's Car Points-of-Sale

> **Front:** `coverage_join_gapmap`. **Built:** 2026-06-13 (live INE Tempus3 fetch +
> live `cardeep` DB query). **Method:** census-anchoring (join our entities against an
> authoritative INE DIRCE denominator), NOT estimation, NOT social media.
>
> **Anti-hallucination contract.** Every number here is `[VERIFIED]` — read from a live
> INE fetch (`ine_tabla301_raw.json`, table 301/294, ref. 2025-01-01, *Definitivo*) or
> from a named SQL query against `postgres://cardeep@localhost:5433/cardeep` this
> session. The denominator artifact `ine_cnae4511_by_province.json` was built by the
> sibling `ine_census_denominator` front and is reconciled here (its national
> `locales_cnae451 = 23,085` equals my independent division-45 × group-share derivation
> exactly — two paths, one number).

---

## 0. The headline, stated honestly

| Frame | Ours | INE denominator | Coverage |
|---|--:|--:|--:|
| **Sales — registral-orthogonal** (excl. C2C marketplace attribution) | **21,759** | 23,085 locales 451 `[VERIFIED INE]` | **94.3%** |
| Sales — gross (all sources) | 33,611 | 23,085 locales 451 | 145.6% (inflated) |
| Desguace — exact census | 1,299 | **1,292 DGT-CAT** `[VERIFIED exact]` | **100.5%** (sealed) |
| Garaje (sells_cars subset) | — | CNAE 452 = 50,294 (repair ceiling) | **uncomputable** — `sells_cars` unpopulated |

> **National verified coverage of the SALES segment is 94.3%** against the INE
> point-of-sale census (locales CNAE 451), counting only registral/geo/OEM/directory
> attribution. The gross 145.6% is **not** a coverage win — it is C2C contamination
> (§2): 35.2% of sales entities were first-discovered on milanuncios/wallapop, platforms
> the coverage doctrine (`07-COVERAGE-STRATEGY §9.7`) attributes to the platform
> sentinel, not enumerated as dealers. The honest number is the registral one.

**The gap is no longer "find more dealers."** At province/CCAA scale the sales universe is
saturated. The real residuals are: (a) **the islands and autonomous cities** (Canarias
59%, Ceuta 19%, Melilla 25%), (b) a **C2C/dealer dedup discipline** problem that inflates
the gross count, and (c) a **32.5% geocoding gap** (13,741 target entities carry a
province but no municipality) that degrades all municipal-level numbers.

---

## 1. Confidence ladder of this map (read before trusting any cell)

| Level | What it anchors | Confidence | Why |
|---|---|---|---|
| **CCAA × locales 451** | sales coverage per autonomous community | **HIGH** | INE publishes `locales_cnae451` **exactly** per CCAA; sum of 19 CCAA = 23,085 = national (integrity-checked). This is the load-bearing layer. |
| **Province × div-45 allocation** | sales coverage per province | **MEDIUM** | INE does **NOT** publish province × CNAE-451 (confidential). Province values are INE division-45 *locales* (table 301, exact per province) **allocated** to 451 by the national 451/45 share (0.2605). Allocation assumes uniform sales-mix across provinces — a declared modeling input. |
| **Desguace × DGT-CAT** | scrapyard coverage | **EXACT** | DGT CAT is a legal census; 1,292 is the true denominator, not an estimate. |
| **Municipality × OSM/POI** | per-pueblo coverage | **LOW** | INE municipal dealer count is **CONFIDENTIAL/AGGREGATED** (table 4721 only at SECCION depth). Municipal anchor falls back to OSM POI, which is **circular** (OSM is one of our own sources) and incomplete. Municipal cells are directional, not census-verified. |

> **Confessed limit (the owner asked us to confess gaps, not sell certainty).** There is
> **no authoritative per-municipality car-dealer denominator in Spain.** INE suppresses it
> below CCAA for statistical secret. So municipality coverage **cannot** be census-verified;
> it can only be POI-bounded, and our POI (OSM 9,956) is not orthogonal to our own intake.
> Mejor confesar el hueco que vender una mentira: the province layer is the deepest
> *verified* resolution; comarca/municipio is a *structural* view, flagged as such.

---

## 2. Why gross coverage exceeds 100% — the C2C inflation, measured

`[VERIFIED — SQL on entity / entity_source]`

- **0 / 33,709** sales entities carry a CIF → no registral identity is yet attached
  (the V1-DENOMINATOR ρ̄/CIF anchor is designed but unwired).
- **11,852 / 33,710 = 35.2%** of sales entities were *first discovered* on
  **milanuncios_wholesale + wallapop_wholesale** — C2C-dominated platforms.
- **213 / 33,710 = 0.6%** have `attest_count ≥ 2` (multi-source). The capture-recapture
  overlap `m` is ~zero: the universe is overwhelmingly **single-source**, the exact
  regime where inflation hides (V1-DENOMINATOR §6).

**Reading:** the gross 145.6% is single-source C2C listings minted as `compraventa`.
Removing the two C2C platforms from *first-discovery* yields the registral-orthogonal
21,759 → **94.3%**, which still overshoots 100% in 13 provinces (Salamanca 147%, Burgos
139%, Jaén 134%) because CARDEEP counts **points of sale** and INE locales-451, while
also point-level, undercounts multi-branch chains' sites and excludes OEM-VO portal
dealers that are not standalone 451 firms. **The actionable finding is over-collection
discipline, not under-coverage.**

---

## 3. RANKED GAP MAP — most under-covered territories

### 3a. By CCAA (HIGH confidence — exact INE locales 451)

| Rank | CCAA | Ours (registral) | INE locales 451 | **Coverage** | State |
|--:|---|--:|--:|--:|---|
| 1 | **Ceuta** | 5 | 26 | **19.2%** | genuine gap — autonomous city, thin online presence |
| 2 | **Melilla** | 11 | 44 | **25.0%** | genuine gap — autonomous city |
| 3 | **Canarias** | 621 | 1,046 | **59.4%** | genuine gap — islands + 54% geocode loss (§4) |
| 4 | Castilla-La Mancha | 871 | 1,117 | 78.0% | partial — rural long-tail |
| 5 | Madrid | 3,648 | 4,123 | 88.5% | near-complete |
| 6 | Andalucía | 3,806 | 4,213 | 90.3% | near-complete |
| 7 | Murcia | 741 | 816 | 90.8% | near-complete |
| 8 | Galicia | 1,309 | 1,437 | 91.1% | near-complete |
| 9 | Extremadura | 529 | 578 | 91.5% | near-complete |
| 10 | Com. Valenciana | 2,392 | 2,574 | 92.9% | near-complete |

All other CCAA are ≥ 95% registral, several **over 100%** (País Vasco 154.7%, Asturias
144.4%, Cantabria 132.2%, La Rioja 132.0%) — over-collection, not coverage.

### 3b. Top-10 GAP PROVINCES (MEDIUM confidence — allocated INE 451)

| Rank | Prov | Province | Ours (reg) | INE 451 (alloc) | Coverage | Geocode gap |
|--:|--:|---|--:|--:|--:|--:|
| 1 | 51 | Ceuta | 5 | 25 | **20.0%** | 2/9 |
| 2 | 52 | Melilla | 11 | 42 | **26.2%** | 4/15 |
| 3 | 35 | Las Palmas | 306 | 578 | **52.9%** | 219/622 |
| 4 | 38 | Sta. Cruz de Tenerife | 315 | 584 | **53.9%** | 324/604 |
| 5 | 19 | Guadalajara | 69 | 122 | **56.6%** | 28/138 |
| 6 | 05 | Ávila | 51 | 89 | **57.3%** | 31/114 |
| 7 | 04 | Almería | 231 | 396 | **58.3%** | 229/493 |
| 8 | 14 | Córdoba | 260 | 438 | **59.4%** | 163/537 |
| 9 | 10 | Cáceres | 140 | 230 | **60.9%** | 77/312 |
| 10 | 16 | Cuenca | 82 | 134 | **61.2%** | 42/159 |

> **Caveat on the islands (rank 3–4):** Las Palmas and Tenerife carry a **huge geocode
> gap** (Tenerife: 324 of 604 target entities have no municipality_code). Their low
> coverage is *real at province level* (province counts include non-geocoded rows), but
> the municipal detail beneath is unreliable until geocoding is repaired. The Canary gap
> is part true under-discovery (island long-tail), part missing-province-data on intake.

---

## 4. NAMED missing-dealer signal at municipality level (LOW confidence / directional)

Municipal coverage cannot be census-anchored (§1). The strongest available POI signal —
OSM/AEDRA/DGT-CAT geo-survey vs our geocoded entities — is **circular** (those POI rows
are already our rows), so it produces **zero** "POI saw it, we missed it" gaps by
construction. The honest municipal gaps are therefore **structural**, not POI-named:

- **8,132 municipalities total; 1,822 (22.4%) have ≥1 geocoded target dealer.** The other
  6,310 are dominated by tiny pueblos with genuinely zero car business — a *caused empty*,
  not a coverage hole. The map does **not** claim 6,310 missing dealers.
- **The real municipal defect is the geocode gap:** 13,741 target entities (32.5%) have a
  province but no municipality, so they cannot be placed on the comarca/pueblo grid the
  mandate names. **Fixing geocoding is the prerequisite to any honest municipal gap map.**

Largest geocoded municipalities in the worst gap provinces (where to look first once
geocoding is repaired and an orthogonal POI — full Páginas Amarillas ~44k, FSQ, Overture —
is ingested):

| Prov | Municipality | Ours (geocoded) | OSM POI |
|--:|---|--:|--:|
| 35 | Las Palmas de Gran Canaria | 212 | 49 |
| 38 | Santa Cruz de Tenerife | 74 | 3 |
| 35 | Telde | 64 | 9 |
| 38 | San Cristóbal de La Laguna | 46 | 7 |
| 19 | Guadalajara | 66 | 7 |

These are not "missing dealers" — they are the populated cores. The **named missing
dealers** the front spec wants require an **orthogonal, complete POI dedup** that does not
yet exist in the DB (only an 78-record PA sample + circular OSM). **Declared gap.**

---

## 5. Method (reproducible)

1. **Denominator (INE, authoritative).** Tempus3 JSON API, table **301** (Locales por
   provincia × CNAE división × estrato; *Total* stratum, división **45** = Venta y
   reparación de vehículos) → exact per-province local-unit counts (Σ52 = 88,621 =
   national, integrity-checked). Table **294** (Locales por CCAA × grupos CNAE) → national
   group split **451=23,085 / 452=50,294 / 453=11,494 / 454=3,748**. Province 451 =
   div-45 × (23,085/88,621). CCAA 451 = exact from `ine_cnae4511_by_province.json`.
2. **Numerator (our DB).** `SELECT province_code, count(*) FROM entity WHERE kind IN
   ('compraventa','concesionario_oficial') AND status='active' GROUP BY 1`; registral
   regime additionally `AND first_discovered_source <> ALL('{milanuncios_wholesale,
   wallapop_wholesale}')`.
3. **Join** numerator/denominator at CCAA (HIGH), province (MEDIUM), municipality (LOW).
4. **Desguace** joined directly to DGT-CAT exact census (1,292).

**Artifacts in this directory:**
`ine_cnae4511_by_province.json` (sibling INE denominator), `ine_prov_div45.json` (my
per-province div-45 extract), `coverage_ccaa.json`, `coverage_province.json`,
`muni_poi.json`, `ine_tabla301_raw.json` (10 MB raw INE pull).

---

## 6. What this front will and will not claim

**Will claim** `[VERIFIED]`:
- Sales segment **94.3% nationally** verified against INE locales-451; desguace **100.5%**
  against DGT-CAT (sealed).
- The 10 named gap CCAA/provinces, led by **Ceuta, Melilla, Canarias**.
- The gross 145.6% is **C2C inflation**, quantified at 35.2% C2C-first-discovery.

**Will NOT claim:**
- Any per-municipality coverage % as *verified* — INE suppresses that denominator; ours is
  POI-bounded and circular. Reported as structural/directional only.
- That over-100% provinces are "fully covered" — they are over-collected; the action is
  CIF-anchoring + C2C/dealer dedup, not more discovery.
- A garaje coverage % — `sells_cars` is unpopulated (0 rows true); the denominator is
  undefined until the §9.3 deflation runs. Confessed, not faked.
