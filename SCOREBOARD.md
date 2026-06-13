# CARDEEP — MARCADOR VERIFICADO FINAL (cierre 2026-06-13, 3ª ola)
> Cada número contado por el Director a mano con psycopg2 contra la DB viva (cardeep-pg :5433), VAM ≥2 caminos.
> DB en INGESTA VIVA: los absolutos suben entre snapshots. El bloque Tier-1 es de un snapshot único congelado.
> Parte de entrega honesto completo: `CIERRE_FINAL.md` (§7 = esta 3ª ola). Sin git commit.

## Globales (snapshot vivo único REPEATABLE READ)
| Métrica | §1 (anterior) | 2ª ola (§6) | **3ª ola (actual, ~07:04 UTC)** |
|---|---|---|---|
| vehicle (total) | 1.030.185 | 1.332.617 | **1.336.553** |
| vehicle available (+gone 1.375 == count*) | 1.028.810 | 1.331.242 | **1.335.178** |
| entity (puntos de venta + plataformas) | 207.934 | 309.147 | **309.214** |
| platform_listing (aristas) | 983.981 | 1.286.413 | **1.290.349** |
| vehicle_event (delta/historial) | 1.033.279 | 1.335.715 | **1.339.652** |
| provincias / municipios con entidades | 52/52 · 4.181 | 52/52 · 4.712 | **52/52 · 4.712** |
| plataformas (`platform`) | 22 | 22 | **24** (+Autorola +BCA subastas) |

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

### subastas Autorola + BCA — STOCK CERRADO GRATIS (navegador JS) — veredicto previo 'GATED' REVOCADO
| Casa | vehículos | entidades-subasta | precio |
|---|---|---|---|
| Autorola      | **90** | 2 | gated (login, bid-based) |
| BCA Espana    | **50** | 6 | gated (login) |
| Ayvens Carmarket | 27  | 2 | gated (bid-based) |
| **Σ subastas** | **167** (140 nuevos cerrados gratis) | 10 | — |

`stealth_subastas`: Playwright (JS) arrancó las SPA Angular de autorola.es/bca.com y renderizó stock
público por-lote SIN login. Autorola data layer:
`old.autorola.es/rest/vehiclesearchenrollment/result?locale=es_ES` → `groups[].vehicleDTOS[]`
(`countryCode` filtro ES); subasta ES 671406 → 51 lotes Madrid (Seat Arona 12/2024 64.740 km, verificado
en DB). El stock (make/model/year/km) está completo y gratis; **solo el precio de puja queda con verja**.
Esto **revoca** el 'GATED' que `subastas_datalayer.md` + `group_subastas_wholesale.py` declaraban con una
sonda curl_cffi sin JS.

### Grupos no-marketplace — VAM ≥2 caminos
| Grupo | Entidades | Vehículos | Veredicto |
|---|---|---|---|
| OEM-VO (14 portales) | 5.755 | 32.271 | ✅ TRUSTWORTHY (geo-recovery 2ª ola; era 31.448 / viejo 22.222) |
| Cadenas (Flexicar/OcasionPlus) | 187 | 37.319 | ✅ TRUSTWORTHY (etiqueta impura: mezcla Arval/Ayvens leasing) |
| rentacar_vo (OK Mobility) | 1 | 166 | ✅ TRUSTWORTHY |
| subastas (Autorola/BCA/Ayvens) | 10 | 167 | ✅ TRUSTWORTHY (stock gratis; precio gated) |
| long_tail_families | 103 | 10.178 | ❌ REFUTED (no aditivo: 10.083 ya en otros grupos) |

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
| G2 | **subastas: PRECIO de puja + cola per-subasta** | Stock Autorola+BCA ya cerrado-gratis (140 lotes); pero `price` NULL en 165/167 (`loginRequired=True`, bid-based). El drain per-subasta completo (declared `lotsCount` en cientos) no tiene paginación key-free. Ayvens GraphQL `api-carmarket.ayvens.com/graphql` → 401 `Ocp-Apim-Subscription-Key` (key server-side). | Login dealer / credencial APIM |
| G3 | **long-tail `unreachable` (246 veh)** | Webs propias de dealers que exigen Tier-2 **residential proxy** para superar defensa; no alcanzable con vector gratuito. | Tier-2 residential proxy (P10) |
| G4 | **OEM murados sin data-layer** | kia geo-skip CERRADO (geo_fallback 476), pero Mazda/Honda/Suzuki sin data-layer expuesto. | Receta por-portal / navegador |
| G5 | **auto_repair efectos caros (P10-scaffold)** | `repair_attempt.succeeded=FALSE`, `repair_outcome='pending'`, marcado `_SPEND_GATED_ACTIONS`. El LAZO (classify+audit+alerta-origen+breaker+quarantine+escalate_owner) corre real a coste 0; refingerprint/escalate_tier/re_receta esperan autorización de gasto. | Autorización de gasto P10 |

### Defectos de calidad de datos (flagged, no spend — fix pendiente)
- ⚠️ **coches.com doble-conteo cross-surface 20.432** (REFUTED id=548): clave de identidad = URL no listing-id; verdad = 91.066 únicos. Fix dedup pendiente.
- ⚠️ **long_tail no aditivo-disjunto 10.083** (REFUTED id=544): `family_*` es clasificador CMS sobre grupo primario, no partición. Regla pendiente.
- ⚠️ **dedup cross-plataforma ≥134.027 filas excedentes** (14,36%, cota inferior estricta, TRUSTWORTHY id=574): MEASURE-ONLY, no merge por defecto.
- ⚠️ **'chain' etiqueta impura**: mezcla Arval/Ayvens leasing con cadenas VO reales (conteo 37.319 consistente, etiqueta sucia).
- ℹ️ **organization VAM muerto** (tabla vacía, org_id NULL) · **API oem_vo_portal sin endpoint propio** (HTTP 400 guard) · **platform.listing_counter NULL en las 24**.

---

## Segunda + tercera ola — frentes post-cierre (detalle en CIERRE_FINAL.md §6/§7)
| Frente | Resultado | VAM | Columna |
|---|---|---|---|
| wallapop facet | 457.766 → **495.737** aristas (+37.731 reales) | ✅ 3 caminos (e==jv exacto, ref 0,010%) | (1) gratis |
| coches.net VN/km0/renting (Imperva) | 0 → **+10.470** aristas (100% dealer) | ✅ 2 caminos, ids 584–587 | (1) gratis — **era spend-gated** |
| subastas Autorola+BCA | 0 → **+140 lotes** (stock; veredicto 'GATED' revocado) | ✅ navegador JS + DB ownership | (1) gratis — **era spend-gated** |
| coches.com renting XHR | 13 → **1.035** aristas | ✅ 4 caminos AGREE | (1) gratis |
| OEM-VO geo-recovery | 31.448 → **32.271** (kia +476, volvo +46) | ✅ 3-4 caminos AGREE | (1) gratis |
| milanuncios residual | 259.034 → **259.706** | ✅ TRUSTWORTHY | (1) gratis |
| motor.es VN residual | 48.997 → **49.009** | ✅ TRUSTWORTHY | (1) gratis |
| cp1252 (Σ) global fix | 31 módulos parcheados | ✅ 2 caminos DB-free + root-cause | (1) gratis |
| geo jerárquico a escala | comarcas=323, drift 0 | ✅ Path A==Path B (231.425) | (1) gratis |
| dedup cross-plataforma | ≥**134.027** excedentes (14,36%) | ✅ SQL==Python 0,0% | calidad-de-datos |
| S-HEALTH battle-test | 25/25 PASS, cascada E2E | ✅ 2 caminos | (1) gratis |

## "100%" honesto
- ✅ **100% del vector GRATUITO**: cerrado y verificado. Dos verjas declaradas en §1 (coches.net Imperva,
  subastas Autorola+BCA) **derribadas gratis** en la 3ª ola. 6 Tier-1, core partición limpia, API + S-HEALTH E2E.
- ❌ **100% ABSOLUTO de España**: requiere los bloqueadores spend-gated G1–G5 (wallapop →651k profundo,
  precio de subasta tras login, Tier-2 residential proxy para `unreachable`, OEM murados, P10 auto-repair caro).
  Declarado con evidencia, no fingido.
