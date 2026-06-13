# CARDEEP — MARCADOR VERIFICADO FINAL (cierre 2026-06-13, 7ª ola Δ-CANALES LANDED)
> Cada número contado por el Director a mano con psql directo contra la DB viva (cardeep-pg :5433), VAM ≥2 caminos.
> DB en INGESTA VIVA: los absolutos suben entre snapshots. El bloque Tier-1 es de un snapshot único congelado.
> Parte de entrega honesto completo: `CIERRE_FINAL.md` (§8 = 4ª ola; §9 = 5ª ola descubrimiento/expansión). Sin git commit.

## Globales (snapshot vivo único REPEATABLE READ)
| Métrica | 4ª ola (§8) | 5ª ola (DESCUBRIMIENTO) | **7ª ola (Δ-CANALES, actual)** |
|---|---|---|---|
| vehicle (total) | 1.353.104 | 1.492.160 | **1.495.710** |
| vehicle available (+gone 1.375 == count*) | 1.351.729 | 1.490.785 | **1.494.335** |
| entity (puntos de venta + plataformas) | 315.270 | 368.811 | **369.383** |
| platform_listing (aristas) | 1.306.900 | 1.445.469 | **1.449.019** |
| vehicle_event (delta/historial) | 1.356.203 | 1.495.282 | **1.498.858** |
| provincias / municipios con entidades | 52/52 · 4.757 | 52/52 · 5.025 | **52/52 · 4.974** |
| plataformas (`kind='plataforma'`) | 24† | 24† | **18 (kind='plataforma' estricto; +5 esta ola)** |
| **dealers distintos con own-site** (no-edge, no-plataforma) | — | 332 | **332** |
| **coches own-site** (no-edge, no-plataforma) | — | 46.691 | **46.691** |
| entidades con `website` poblado | — | 1.884 | **1.890** |

> † Las columnas previas contaban `platform` de forma laxa (24/27). El conteo estricto
> `kind='plataforma'` HOY es **18**, tras sumar 5 esta ola (Facilitea Coches, RACC, LocalizaVO,
> Car & Classic, Miclásico) sobre las 13 del censo por segmentos (6ª ola). Cifra re-contada en vivo.

> **Reconcile autoritativo (certificación, snapshot único 06:49:13 UTC):** vehicle_total=1.332.986
> (available 1.331.611 + gone 1.375 == count*); entity_total=1.332.986→**309.148** por 3 caminos idénticos
> `count(*)` == `Σ kind` == `Σ role` = 309.148. Re-verificado 07:04 UTC: la DB drenó +3.567 vehículos, el
> reconcile de 3 caminos sigue == exacto (309.214) y av+gone==count* sigue TRUE. La deriva absoluta es
> ingesta viva, NO descuadre.
>
> El salto absoluto refleja las olas 2ª/3ª + ingesta viva continua; NO es suma disjunta limpia. Siguen
> vigentes los avisos de doble-conteo coches.com (20.432 fantasmas REFUTED), long-tail no aditivo (10.083)
> y dedup cross-plataforma (≥134.027 filas excedentes, §6.G). La cifra deduplicada/sin-solape exige las
> correcciones de `CIERRE_FINAL.md §2`.

---

## (1) CERRADO-GRATIS — vector gratuito, verificado por ≥2 caminos
> Todo lo cosechable sin navegador de pago ni proxy residencial, contado y verificado en DB.

### Tier-1 marketplaces — VAM ≥2 caminos (aristas `platform_listing` live)
| Plataforma | aristas live | distinct ref | Dealer | Particular | Veredicto |
|---|---|---|---|---|---|
| wallapop    | **495.737** | (e==jv exacto; ref 0,010%) | 3.932 cv | 160.847 part | ✅ TRUSTWORTHY (faceto +37.731) |
| coches.net  | **274.138** | 272.884 (VO) + 10.470 (VN/km0/renting) | dealer | particular | ✅ TRUSTWORTHY |
| milanuncios | **259.706** | 259.033 | 135.250 | 123.784 | ✅ TRUSTWORTHY |
| coches.com  | **92.088** | 91.066 únicos | 92.088 | 0 | ⚠️ REFUTED VO (20.432 fantasmas cross-surface) |
| Autocasion  | **49.391** | = | dealer | 0 | ✅ TRUSTWORTHY |
| motor.es    | **49.009** | 49.009 | 49.009 | 0 | ✅ TRUSTWORTHY |

Path A (aristas-distinct) == Path B (vehicle-ownership join) EXACTO · 0 dup-explosion · 0 huérfanos.
Veredictos: `verification_verdict` ids 545–550 + 576 (wallapop) + 584–587 (coches.net segmentos).

### coches.net VN/km0/renting tras Imperva — CERRADO GRATIS (camoufox) — era hueco "Imperva ~10k"
| Segmento | aristas | dealers (kind=compraventa) | particulares |
|---|---|---|---|
| new     | **6.151** | 230 | 0 |
| km0     | **3.107** | 323 | 0 |
| renting | **1.212** | 45  | 0 |
| **Σ VN** | **10.470** | 100% dealer-owned | 0 |

VO (`used`) inmóvil = 263.668. coches.net total = 274.138. VAM 2 caminos (edge-distinct == JOIN
edge→vehicle→entity), 0 huérfanos. Veredictos ids 584/585/586/587 TRUSTWORTHY.

### subastas Autorola + BCA — STOCK ESCALADO A 2.808 COCHES CERRADOS GRATIS (navegador JS) — 'GATED' REVOCADO
| Casa | distinct vehicles | aristas | precio | Path A==Path B | year |
|---|---|---|---|---|---|
| BCA Espana (`01KTZW8SXGB2XWA2H10H7BJ9ET`) | **1.752** | 1.752 | NULL (bid-gated) | EXACTO, 0 huérfanos | 1.751/1.752 |
| Autorola (`01KTZW8SE8BF0HXA6BXM1PRVAR`)   | **1.056** | 1.056 | NULL (bid-gated) | EXACTO, 0 huérfanos | 1.056/1.056 |
| **Σ Autorola+BCA** | **2.808** | 2.808 | **0 con precio** | DISJUNTO (0 solape) | 2.807/2.808 |
| Ayvens Carmarket (`01KTZ289WAEJZ7NQ1AZXW25RJY`) | 27 | 27 | NULL | — | — |

`stealth_subastas`: Playwright (JS) arrancó las SPA Angular de autorola.es/bca.com y dren­ó el catálogo
COMPLETO de lotes SIN login (de 140 piloto en 3ª ola a 2.808 coches en 4ª). VAM 2 caminos EXACTO contado
AHORA: Path A (aristas-distinct) == Path B (ownership join), 0 aristas huérfanas. **CORRECCIÓN
anti-alucinación:** los conjuntos Autorola y BCA son **DISJUNTOS** (intersección=0), NO "dual-membership";
Σ 1.056+1.752=2.808 es suma limpia. El stock (make/model/year/km) está completo y gratis (2.807/2.808 con
year); **solo el precio de puja queda con verja** (`platform_price` NULL en las 2.808, `loginRequired=True`).

### Grupos no-marketplace — VAM ≥2 caminos
| Grupo | Entidades | Vehículos | Veredicto |
|---|---|---|---|
| OEM-VO (14 portales) | 5.755 | 32.271 | ✅ TRUSTWORTHY (geo-recovery 2ª ola; era 31.448 / viejo 22.222) |
| Cadenas (Flexicar/OcasionPlus) | 187 | 37.319 | ✅ TRUSTWORTHY (etiqueta impura: mezcla Arval/Ayvens leasing) |
| rentacar_vo (OK Mobility) | 1 | 166 | ✅ TRUSTWORTHY |
| subastas (Autorola/BCA/Ayvens) | 42 | 2.835 (2.808 A+B + 27 Ayvens) | ✅ TRUSTWORTHY (stock gratis; SOLO precio de puja gated) |
| long_tail_families | 103 | 10.178 | ❌ REFUTED (no aditivo: 10.083 ya en otros grupos) |
| unreachable (`family_unreachable`) | 1 (hrmotor) | 246 | ✅ CERRADO-GRATIS (enjaulado; 89 dominios restantes genuinamente muertos) |

CORE partición LIMPIA (oem_vo, chain, rentacar_vo): 0 solape entidad/vehículo. Veredictos: ids 540–544.

### OEM-VO detalle (14 portales, 32.271 coches, 5.755 entidades — geo-recovery 2ª ola)
spoticar · audi · toyota_lexus · hyundai · volvo_jlr_suzuki · nissan_intelligent_choice · seat_cupra ·
kia · renew · das_weltauto · ford · bmw_premium_selection · mercedes_benz · mini_next.
(Los coches cuelgan de las entidades DEALER, no de las 14 filas plataforma que poseen 0 vehículos directos.)

### Otros frentes cerrados-gratis (2ª/3ª ola)
- ✅ **coches.com renting XHR**: 13 → 1.035 aristas (VAM 4 caminos AGREE; totalOffers del hub = faceta headline, no paginable).
- ✅ **cp1252 (Σ) global fix**: 31 módulos `pipeline/platform/` parcheados con `_force_utf8_stdout()`, root-cause probado.
- ✅ **geo jerárquico a escala**: comarcas=323, muni-con-comarca 99,98%, drift 0 (Path A==Path B = 231.425).
- ✅ **S-HEALTH battle-test**: 25/25 PASS, cascada record→breaker→alerta-origen→auto_repair→recovery E2E, 0 residuo TEST.
- ✅ **trade_name vacío**: 41 'particular' backfilled → POST=0 blank (verificado en vivo).

---

## (2) SPEND-GATED — bloqueadores genuinos con verja (evidencia, NO fingidos)
> Lo que el vector gratuito NO alcanza. Cada uno con su evidencia y su criterio de aceptación.

| # | Bloqueador | Evidencia verificada | Puerta |
|---|---|---|---|
| G1 | **wallapop cola profunda → ~651k** | Cosechadas +37.731 (ahora 495.737 aristas). Oracle next_page JWT `pointers.ORGANIC.remaining_documents` baseline ≈651.328–651.372. El resto exige paginación por faceta/cursor profundo aún no completada (band-boundary collapse por dedup item-id). | Esfuerzo/tiempo de drenaje profundo |
| G2 | **subastas: PRECIO de puja (NO el stock)** | Stock Autorola+BCA ESCALADO a 2.808 coches cerrados-gratis (4ª ola); `platform_price` NULL en las **2.808** aristas (`loginRequired=True`, bid-based). El STOCK ya NO está con verja; solo el **precio de puja** lo está. Ayvens GraphQL → 401 `Ocp-Apim-Subscription-Key` (key server-side). | Login dealer / credencial APIM |
| G3 | **89 dominios `unreachable` genuinamente muertos** | RE-test stealth JS (camoufox): hrmotor.com (246 coches) **YA enjaulado gratis** (único recuperable). De los 92, restan **89 muertos genuinos**: 39 NXDOMAIN (`getaddrinfo` falla) + 50 muro-duro (CF/DataDome/SSL-roto/server-err) + 2 sin-stock-propio. Sin nada vivo que cosechar — ni vector gratuito ni de pago. | Nada (negocios/dominios muertos) |
| G4 | **OEM murados sin data-layer** | kia geo-skip CERRADO (geo_fallback 476), pero Mazda/Honda/Suzuki sin data-layer expuesto. | Receta por-portal / navegador |
| G5 | **auto_repair efectos caros (P10-scaffold)** | `repair_attempt.succeeded=FALSE`, `repair_outcome='pending'`, marcado `_SPEND_GATED_ACTIONS`. El LAZO (classify+audit+alerta-origen+breaker+quarantine+escalate_owner) corre real a coste 0; refingerprint/escalate_tier/re_receta esperan autorización de gasto. | Autorización de gasto P10 |

### Defectos de calidad de datos (flagged, no spend — fix pendiente)
- ⚠️ **coches.com doble-conteo cross-surface 20.432** (REFUTED id=548): clave de identidad = URL no listing-id; verdad = 91.066 únicos. Fix dedup pendiente.
- ⚠️ **long_tail no aditivo-disjunto 10.083** (REFUTED id=544): `family_*` es clasificador CMS sobre grupo primario, no partición. Regla pendiente.
- ⚠️ **dedup cross-plataforma ≥134.027 filas excedentes** (14,36%, cota inferior estricta, TRUSTWORTHY id=574): MEASURE-ONLY, no merge por defecto.
- ⚠️ **'chain' etiqueta impura**: mezcla Arval/Ayvens leasing con cadenas VO reales (conteo 37.319 consistente, etiqueta sucia).
- ℹ️ **organization VAM muerto** (tabla vacía, org_id NULL) · **API oem_vo_portal sin endpoint propio** (HTTP 400 guard) · **platform.listing_counter NULL en las 24**.

---

## 5ª ola — DESCUBRIMIENTO / EXPANSIÓN (detalle en CIERRE_FINAL.md §9)
> El "garaje perdido": puntos de venta ausentes de todo conector previo. +488 entidades commiteadas (DB-verificadas).
| Frente | Resultado | VAM | Columna |
|---|---|---|---|
| **discover_associations** | **+409 entidades / +327 coches** (`source_group='association'`; 0 dup, 0 huérfanos, 0 sin-provincia) | ✅ 2 caminos directos en DB | descubrimiento |
| **discover_geographic** | **+68 entidades / +0 coches** (`geo_sweep`; 68/68 con web, 36/52 provincias, 0 colisión host) | ✅ DB tally + `entity_source` | descubrimiento |
| **discover_directories** | **+0 entidades** (HONESTO: nada commiteado, cosecha nacional aún corriendo; test Álava stale rehusado) | ✅ `count(entity_source)`=0 | descubrimiento — NO commit |
| **chains_more** | **+2 entidades / +1.882 coches** (Clicars 1.470 distinct + Carplus 412) | ✅ 3 caminos (edges==join==owned) | descubrimiento |
| **rentacar_more** | **+2 entidades / +46 coches** (Centauro 28 + Record Go 18) | ✅ edges==join==harvested EXACTO | descubrimiento |
| **drain_all_ownsites** | **+7 entidades / +487 coches** (309 dominios, 7 family_slice @ 0,0 divergencia) | ✅ 7 veredictos firmados | descubrimiento |

## 2ª/3ª/4ª ola — frentes post-cierre (detalle en CIERRE_FINAL.md §6/§7/§8)
| Frente | Resultado | VAM | Columna |
|---|---|---|---|
| **subastas Autorola+BCA** | 140 lotes → **2.808 coches** (stock completo, disjunto, 0 con precio) | ✅ 2 caminos EXACTO (A==B, 0 huérfanos) | (1) gratis — solo PRECIO gated |
| **`unreachable` veredicto final** | 92 dominios → **1 enjaulado (hrmotor 246) + 89 muertos** | ✅ DB tally (1/246) + stealth JS, buckets suman 92 | residual genuino |
| wallapop facet | 457.766 → **495.737** aristas (+37.731 reales) | ✅ 3 caminos (e==jv exacto, ref 0,010%) | (1) gratis |
| coches.net VN/km0/renting (Imperva) | 0 → **+10.470** aristas (100% dealer) | ✅ 2 caminos, ids 584–587 | (1) gratis — **era spend-gated** |
| coches.com renting XHR | 13 → **1.035** aristas | ✅ 4 caminos AGREE | (1) gratis |
| OEM-VO geo-recovery | 31.448 → **32.271** (kia +476, volvo +46) | ✅ 3-4 caminos AGREE | (1) gratis |
| milanuncios residual | 259.034 → **259.706** | ✅ TRUSTWORTHY | (1) gratis |
| motor.es VN residual | 48.997 → **49.009** | ✅ TRUSTWORTHY | (1) gratis |
| cp1252 (Σ) global fix | 31 módulos parcheados | ✅ 2 caminos DB-free + root-cause | (1) gratis |
| geo jerárquico a escala | comarcas=323, drift 0 | ✅ Path A==Path B (231.425) | (1) gratis |
| dedup cross-plataforma | ≥**134.027** excedentes (14,36%) | ✅ SQL==Python 0,0% | calidad-de-datos |
| S-HEALTH battle-test | 25/25 PASS, cascada E2E | ✅ 2 caminos | (1) gratis |

## 6ª ola — CENSO POR SEGMENTOS (segment-census campaign, 2026-06-13)
> Taxonomía completa keyword→canal→operador en `docs/research/SEGMENT_TAXONOMY.md` (consolida los 5 fronts).
> 5 operadores NUEVOS conectados sobre 4 fronts; cada cifra re-contada por query directa a la DB viva HOY.
> Redes sociales (Facebook Marketplace/IG) DIFERIDAS por mandato del owner.

| Front | Operador NUEVO conectado | Net coches | VAM | Columna |
|---|---|---|---|---|
| `marketplaces_extra` | **Motorflash** (`CDP-ES-00-WN1DMGRN`, marketplace_motor) | +44 slice (187 aristas vivas; drain ~50k gobernado P1) | ✅ TRUSTWORTHY (3 caminos) | (1) gratis |
| `oem_new_stock` | **seat_cupra_new** (`CDP-ES-00-5R30HVA7`, oem_dealer_network, segment=new) | +2.229 (Seat 1145 + CUPRA 1063 + 21 sort-rotation; DB-wide new 6.151→**8.380**) | ✅ TRUSTWORTHY | (1) gratis (t0_open) |
| `leasing_rentacar_exfleet` | **Arval AutoSelect** (`CDP-ES-28-CVV4S3CJ`) + **Northgate Ocasión** (`CDP-ES-28-4XKXNTSY`) | +1.280 (1.172 + 108; Athlon `CDP-ES-08-FSZ9HXWX` enjaulado, drain 114 DIFERIDO browser-required) | ✅ TRUSTWORTHY | (1) gratis |
| `b2b_extra_auctions` | **Subastacar** (`CDP-ES-00-S3K8PK50`, official_registry) | +233 (100% completitud campo: make/year/km/price/fuel/trans/VIN/foto 233/233) | ✅ TRUSTWORTHY (233 vs 238) | (1) gratis (t0_open) |
| `keyword_census` | — (pasada de mapeo) | +0 | — | mapa |

- ✅ **plataformas (`kind='plataforma'`) 10 → 13** (Motorflash + Subastacar + seat_cupra_new) — verificado en vivo.
- ✅ **`rentacar_vo` miembros 3 → 6** (Arval + Northgate + Athlon sobre OK Mobility/Centauro/Record Go) — verificado.
- ✅ **`segment=new` aristas 6.151 → 8.380** (primer canal OEM-oficial de coche NUEVO; antes solo el slice de coches.net).
- ✅→ **TIPOS revelados — Δ RESUELTO en la 7ª ola (ver abajo):** lo que aquí estaba SIN poblar ya se cerró:
  `kind='importador'` **0 → 11 entidades / 187 coches** (MODRIVE + TrendCars/Carismatic reclasificados);
  **classic_marketplace** plegado al marketplace (Car & Classic 585 + Miclásico 693 aristas);
  **faciliteacoches.com** **CONECTADO** (788 coches) + **RACC ocasión** **CONECTADO** (96 coches).
  Pendientes-no-cerrados de este lote (declarado honesto): Raceocasion/Europa Automotive/ImportyGarage/DeutscheCars
  (importadores reachable aún sin caular).
- ❌ **Huecos honestos B2B GATED** (login profesional, sin vector gratis): AUTO1, OPENLANE/Adesa, Manheim ES,
  Alcopa, 2ndMove, Tartiere, CarOnSale, AutoProff, Autobid, Northgate Trade, Copart (salvage). **UNREACHABLE
  (DNS muerto/no-operador):** Aucto, Ucars, EpicAuctions, Carmen. **OUT OF SCOPE:** Reezocar (import francés).
- ❌ **Ex-flota UNREACHABLE-free:** Ayvens B2C (count:0), Alphabet (pro-auction), LeasePlan/CarNext (cerrado 2021),
  Hertz (tel/email), Sixt (DE-only), Europcar/Goldcar (2ndmove pro-gate), Enterprise/Alamo/Avis (sin superficie ES).
- ⚠️ **OEM new-stock reachable-MISSING** (one-time XHR discovery, €0 cada uno): VW-ES, Audi (~4.000), Škoda,
  Renault Webstore (~4.000), Toyota/Lexus NSC, Stellantis, Hyundai, Kia, Ford.

## 7ª ola — Δ-CANALES: tipos vacíos POBLADOS + operadores del Δ-list conectados (2026-06-13)
> Ejecuta el Δ-list de `SEGMENT_TAXONOMY.md §8` + los tipos vacíos/sin-slot de §5. Detalle: §10 de la taxonomía.
> Cada cifra re-contada por mis propias ≥2 (importador, faciliteacoches: 3) consultas DB que CONCUERDAN exacto HOY.

| Front | Operador NUEVO conectado | Net coches | Entidades | VAM | Columna |
|---|---|---|---|---|---|
| `importador` (§5.1 tipo VACÍO → POBLADO) | **MODRIVE** + TrendCars/Carismatic reclasificados | **+187** | **11** (`kind='importador'` 0→11) | ✅ TRUSTWORTHY (vehicles_owned=187 == edge_join=187; MODRIVE 19=19=19) | (1) gratis |
| `faciliteacoches_racc` (§5.3+§5.4 → CONECTADO) | **Facilitea Coches** (CaixaBank VO, `CDP-ES-00-9PXHGJBY`) + **RACC** (`CDP-ES-00-58C3W3P9`) | **+884** (788+96) | **251** (248 dealers + RACC + 2 plataformas) | ✅ TRUSTWORTHY (ambos: edges==join==harvested; 788=788=788, 96=96=96) | (1) gratis |
| `b2b_auctions` (§7 → CONECTADO) | **LocalizaVO** (`CDP-ES-00-HFR3D62Y`, official_registry) | **+318** | **3** | ✅ TRUSTWORTHY | (1) gratis |
| `renting_vo` (§6 Athlon DIFERIDO → DRENADO) | **Athlon Car Outlet** (`CDP-ES-08-FSZ9HXWX`, rentacar_vo) | **+52** (era 0, drain browser-required) | **1** | ✅ TRUSTWORTHY | (1) gratis |

- ✅ **`kind='importador'` 0 → 11 entidades / 187 coches** — el tipo vacío de §5.1 queda POBLADO
  (MODRIVE conectado + TrendCars/Carismatic reclasificados, como anticipaba el plan §5.1).
- ✅ **`kind='plataforma'` 13 → 18** — +5 (Facilitea Coches, RACC, LocalizaVO, Car & Classic, Miclásico).
- ✅ **`kind='subasta'` 95 → 97** · **`platform_listing segment='used'` 1.432.777 → 1.436.153** — verificado en vivo.
- ✅ **Classic-marketplace (§5.2 sin-slot) RESUELTO** — Car & Classic (585 aristas) + Miclásico (693
  aristas) enjaulados como `plataforma`/`marketplace_motor`, plegando el tipo al frente marketplace.
- ✅ **Net esta ola: 187 + 884 + 318 + 52 = 1.441 coches** (sin contar el slice classic), todos VAM TRUSTWORTHY, 0 fabricados.

## F8 — SELLO TERRITORIAL: censo vs cobertura (2026-06-13, censo-anclado)
> Cobertura medida contra denominador autoritativo (INE DIRCE registro legal + Overture POI ortogonal),
> NO estimación. Detalle: `docs/runbook/04-TERRITORIAL.md` + `docs/research/territorial/{TERRITORIAL_COVERAGE,GAP_MAP}.md`.

| Marco | Nuestro | Denominador | Cobertura | Tag |
|---|--:|--:|--:|:--|
| **Ventas (registral-ortogonal)** | 21.759 | 23.085 locales INE 451 | **94,3 %** | `[VERIFIED]` |
| Ventas bruto (C2C-inflado 35,2 %) | 33.611 | 23.085 | 145,6 % | `[count real, ratio inflado]` |
| vs registro de empresas | 33.690 | 14.367 empresas 451 | 234,5 % | `[VERIFIED, suelo = saturación]` |
| **Desguace (censo legal)** | 1.299 | 1.292 DGT-CAT | **100,5 %** | `[VERIFIED exacto — SELLADO]` |

- ✅ **POI Overture ortogonal ATERRIZADO** (cierra el hueco #11 `INCOMPLETE` de TERRITORIAL_COVERAGE §4.11):
  19.727 POI ES · **6.523 cruzados DB** · 13.204 candidatos · 0 closed. Sustituye el OSM circular por fuente independiente.
- ⏳ **13.204 candidatos = superficie de LEADS, NO cobertura faltante** (DB 33.690 negocios > ~1,7× el set ES de Overture): validación PENDIENTE antes de contar una sola fila.
- ❌ **Gaps CCAA genuinos:** Ceuta 19,2 % · Melilla 25,0 % · Canarias 59,4 %. Geocode-gap 32,5 % (13.741 entidades con provincia sin municipio).
- ⚠️ **Provincia × 451 = MODELED** (INE no publica bajo CCAA por secreto estadístico); el % por municipio no es censo-verificable.

## "100%" honesto (cierre definitivo 4ª ola + descubrimiento 5ª ola)
- ✅ **5ª ola DESCUBRIMIENTO LANDED**: +488 entidades de "garaje perdido" commiteadas y DB-verificadas
  (asociaciones +409, geo +68, cadenas +2, rent-a-car +2, own-site drain +7), con ~2.742 coches nuevos
  sobre esos rosters. Censo own-site = **332 dealers / 46.691 coches** fuera de marketplace. `discover_directories`
  = **0 honesto** (cosecha nacional aún corriendo). GAPS genuinos con evidencia: asociaciones WALLED
  (Faconauto/GANVAM/ANCOVE/ANCOPEL/AECS-zona, sin lista pública), long-tail geo sin censo exhaustivo (suelo
  ~44k exige dumps Foursquare/Overture + PA por rubro), ~211 dominios WP/generic sin receta, Google Places
  excluido por ToS (camino legal sustituido).
- ✅ **100% del STOCK del vector GRATUITO**: cerrado y verificado. Tres verjas declaradas (coches.net
  Imperva, subastas Autorola+BCA stock **escalado a 2.808**, hrmotor `unreachable`) **derribadas gratis**.
  6 Tier-1, core partición limpia, API + S-HEALTH E2E. Cada cifra contada AHORA por ≥2 caminos.
- ❌ **RESIDUAL GENUINO (declarado, no fingido):** SOLO el **precio de puja** de las 2.808 subastas
  (login-gated, stock ya libre), los **89 dominios `unreachable` genuinamente muertos** (39 NXDOMAIN +
  50 muro-duro/login-sin-stock-público + 2 sin-listado — stealth JS confirma muerte real, nada vivo que
  cosechar), wallapop→651k profundo, OEM murados sin data-layer, P10 auto-repair caro.
- ⚠️ **Correcciones anti-alucinación (4ª ola):** (1) subastas Autorola/BCA son **DISJUNTAS**, no
  "dual-membership" (intersección=0); (2) "sale_events=20" **no verificable** contra el esquema real
  (no existe tal tabla; `vehicle_event` registra 2.808 eventos NEW, 1 por coche).
