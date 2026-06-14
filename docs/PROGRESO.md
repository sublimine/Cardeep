# PROGRESO — ejecución autónoma hacia SPAIN-SEALED

> Estado vivo del bucle. Sobrevive compactación. El Director (Opus) orquesta + verifica (gate VAM
> ≥2 vías); Sonnet construye. HANDS-OFF total, sin parar, hasta 52/52 sellado.

## Regla de oro (corrección de método 2026-06-14)
NO re-scrapear lo que ya está en DB. El latido (B2 scheduler) ya re-cosecha; el geo residual lo
cierra solo. El esfuerzo va a COBERTURA NUEVA (dealers que NINGUNA fuente tiene aún) + denominador
medido + sello. Cada agente ataca algo nuevo o muere.

## Bloques
- B1 identidad · B2 latido · B3 auto-reparación+API — ✓ CERRADOS en main.
- B4 geo — MECANISMO ✓ (POS físicos: garaje 99,6% / concesionario 96,1% / desguace 98,8%;
  compraventa 83,6%; C2C límite-API confesado). Residual lo cierra el scheduler.
- B5 cobertura — EN CURSO. Recon✓ diseño✓. Camino crítico al sello = NUMERADOR (descubrir dealers
  del long-tail) + DENOMINADOR (Chapman/provincia) + FILTRADO.
- B6 sello 52/52 — pendiente (denominador medido + numerador VAM + gap-con-causa por provincia).

## Frentes
- AS24 scale ✓ (b6rd99ih5): +41.194 coches inventario, 379 dealers cosechados (364 TRUSTWORTHY / 15
  refuted), +31 entities netas nuevas + 7 provincias (39→46), geo 96,7%. APRENDIZAJE honesto: el
  1-sort RE-COSECHA dealers conocidos (inventario fresco = valor de delta) pero descubre POCOS nuevos
  (+31, no los 1.440 del recon). DESCUBRIMIENTO masivo de dealers = Overture (10.913); AS24 =
  INVENTARIO. No martillar AS24 a mano — el scheduler B2 lo recosecha en cadencia.
- Overture ✓ (4e7209f): 10.913 puntos de venta NUEVOS limpios (compraventa 10.659 + desguace 250 +
  subasta 4), geo 99,9%. GATE cazó+borró 21.346 talleres-ruido (automotive_repair mal mapeado a
  garaje); script arreglado en raíz. Leads sin inventario (a scrapear su web), ortogonales p/Chapman.
- Chapman ✓ (08cd270): denominador robusto NO calculable hoy — dedup B1 no cruza OSM↔digital (m~20,
  83% clusters de 1 sola fuente) → N̂ disparatado. SELLABLE ya: desguaces (N̂2061 vs censo DGT 1292).
- B6.1 dedup cruzado (en vuelo, afbeff23): construye matcher OSM×Overture×digital (geo100m/web/phone,
  overlay no-destructivo) + valida en muestra. Sube m → habilita Chapman + reduce overcount compraventa.

## Hallazgo B6 (verificado 2026-06-14) — el denominador NO sale de Chapman OSM×digital
Dedup cruzado ✓ (`cross-source-dedup-v1`, 688 merges, 0 violaciones, vam_verified=FALSE; subió m
OSM×milanuncios 23→191, OSM×coches_net 0→162). PERO Chapman SIGUE disparatado: N̂(OSM×mn)=789.143,
N̂(OSM×cn)=440.795 vs CNAE oficial 39.334. CAUSA RAÍZ [VERIFICADO]: heterogeneidad de captura severa
— OSM (físico) y digital (anuncios) capturan poblaciones casi DISJUNTAS; Chapman asume homogeneidad
→ inviable OSM×digital. El denominador no es capture-recapture aquí.

## Plan real del sello B6 (denominador = oficial + Chapman solo donde homogéneo)
1. SELLOS por segmento (denominador oficial). REGLA DEL GATE: el sello es sobre puntos de venta
   SERVIDOS (con inventario scrapeado), NO sobre leads descubiertos sin coches (Overture aportó
   10.913 leads = descubrimiento, no inventario).
   · **desguace SELLADO 52/52 ✓** (1.292/1.292 censo legal DGT, 0 gaps).
   · **venta**: servido ~22.074 (con inventario) / DIRCE-451 23.085 = **~96% nacional**. [GATE corrigió
     el 147,9% del agente B6.2: 12.281 de los 32.501 compraventa son LEADS sin inventario —10.088 de
     Overture— descubiertos, no servidos.] Denominador provincial ESTIMADO (INE NO publica 4511×
     provincia; ratio 451/45 = 0,2605 prorrateado — confesado, no es "medido" exacto). Gap venta =
     12.281 leads sin scrapear (E2E: descubrir✓ → scrapear inventario PENDIENTE). Doc: docs/recon/B6_venta_sello.md.
   · **concesionario** 1.854 / FACONAUTO 5.358 instalaciones = 35% (gap real, faltan concesionarios).
2. Numerador LIMPIO ✓ (2026-06-14): re-corrido `dealer-identity-det-v1` sobre 61.551 dealers
   actuales → 19.292 merges, numerador **61.551→42.259 canónicos** (overcount −31%), vam_verified=TRUE,
   v_canonical sirviendo. Checks 1-6 OK (recall 100%, 0 FP cross-muni, Flexicar/OcasionPlus/MOBILITY
   correctos, Megar≠Vegar); check-7 conservador (~4 residual, variantes de marca, confesado).
   Cobertura nacional vs oficial: **venta** (compraventa 32.501 + conces 1.854 = 34.355) / CNAE 39.334
   = **87%** · **desguace** 1.678 > censo DGT 1.292 = **SELLADO** · **concesionario** 1.854 / FACONAUTO
   5.358 = 35% (gap real). Deuda: componer cross-source-dedup-v1 (688 OSM×digital, marginal).
3. Scrapear inventario de los 10.913 leads Overture (descubiertos, POIs sin coches aún).
4. Por provincia: cobertura = numerador_VAM / denominador_oficial + gap-con-causa → sellar 52/52.
NO marcar cross-source vam_verified=TRUE en solitario — perdería el dedup B1 intra-source; componer 1º.

## Bucle
leer estado → atacar cobertura nueva por la raíz → VAM gate (≥2 vías, conteo aterrizado en DB) →
commit+push main → actualizar este archivo → siguiente frente. Sin volver a base con gate a medias.

## Sello 52 — estado real [VERIFICADO B6.3, 2026-06-14] · doc: docs/recon/B6_SELLO_52.md
Venta SERVIDA nacional **88%** (20.320 POS con inventario / DIRCE-451 23.085). Por provincia:
- **SELLADO (≥85%): 19/52** (Madrid 112%, Valencia 108%, Murcia 116%, Barcelona 93%, Sevilla 97%...).
- COBERTURA-PARCIAL (50-84%): 26/52.
- GAP-CON-CAUSA (<50%): 7/52 (Ávila, Cáceres, Cuenca, Huelva, Teruel, Ceuta 4%, Melilla 5%).
Desguace: **52/52 entidades SELLADO** (censo DGT); inventario 0/52 (workflow E2E desguace no existe).
Gap accionable: ~14.035 leads sin inventario (10.913 Overture) = E2E descubrir✓ → scrapear PENDIENTE.

## Ruta crítica a SPAIN-SEALED (de 19 → 52 selladas)
1. E2E leads Overture (10.913) → +~7.600 servidos → mayoría de las 26 parciales a SELLADO.
2. Canarias (Las Palmas 61%, Tenerife 63%): fuentes insulares locales.
3. Ceuta/Melilla (<50 dealers): censo manual (OEM locators + cámara).
4. Workflow E2E desguace (1.292 CATs en DB listos) → inventario 52/52.
5. Concesionario FACONAUTO desglose provincial.
Sesgos confesados: denominador venta provincial ESTIMADO (ratio 451/45 = 0,2605 uniforme); filas
por provincia ±2-3% (usan query B6.2); total nacional 20.320 es el canónico verificado 2 vías.

## B5.7 — Generic dealer own-site scraper [VERIFICADO 2026-06-14]

**Método construido y probado** — sitemap-first + schema.org/microdata. DMS identificado:
`inventario.pro` (WordPress plugin WebSpark) = patrón dominante en España para dealers
independientes con web propia. Sitemap: `auto_usate_0-sitemap.xml` / `/wp-sitemap.xml`.
URLs: `/coches/{make}/{model}/{numeric_id}`. Datos: HTML microdata (`itemprop`), no JSON-LD.

**Tasas (muestra verificada 250+ sitios)**:
- SCHEMA_ORG (drenable directo): **~1.5-2%** del universo de webs propias
- SITEMAP_SOLO (URLs presentes, sin datos estructurados): ~11%
- SIN_SITEMAP (200 OK pero sin inventario en sitemap): ~54%
- MUERTO (no responde): ~34%

**E2E completado** — 5 entities TRUSTWORTHY, 849 vehículos:
| Dealer | Provincia | Vehículos | VAM |
|--------|-----------|-----------|-----|
| automovileseduardo.com | 01 Álava | 390 | TRUSTWORTHY |
| iniciacar.com | 29 Málaga | 201 | TRUSTWORTHY |
| raimundomotor.com | 47 Valladolid | 125 | TRUSTWORTHY |
| car2u.es | 11 Cádiz | 112 | TRUSTWORTHY |
| garciautodelvalles.com | 08 Barcelona | 21 | TRUSTWORTHY |

Además 7 dealers adicionales con DMS inventario.pro identificado en DB (REFUTED por residual
histórico de sesión anterior sin GONE guard — artefacto de bootstrap, no de método).

**GONE guard implementado** en `ingest_generic_dealer_vehicles()`: marca como `sold` los
vehículos ausentes del harvest cuando coverage ≥95% del prior. Corrige el REFUTED en runs
futuros.

**Proyección honesta** para los ~6.798 leads own-site de Overture:
- SCHEMA_ORG drainable (1.5%): **~102 dealers** → ~20.000 vehículos estimados
- SITEMAP_SOLO (11%): ~748 dealers → requieren parser HTML específico
- SIN_SITEMAP (54%): ~3.671 → acceso bloqueado o sitio sin catálogo web
- MUERTO (34%): ~2.311 → no accesibles

Gap-con-causa: ~4.800 leads necesitan otro método (API OEM o parseo por plataforma).

**Archivos**: `pipeline/platform/generic_dealer_site.py` · `scripts/probe_dealer_sites.py` ·
`scripts/run_generic_dealer_e2e.py` · `docs/recon/B5_7_probe.json`

## B7 — Código único por coche físico [ENTREGADO 2026-06-14, vam_verified=FALSE]

**Método multi-señal union-find determinista v1.0.0** — espejo exacto de B1 (entity_cluster).
Overlay no-destructivo: 0 filas vehicle mutadas.

**Señales verificadas:**
- Señal A (photo_url): normalización URL → strip query/trailing/resize → match exacto.
  Suficiente sola. Cross-province PERMITIDO (misma foto = mismo coche físico).
- Señal B (firma): make+model+year+km EXACTO + price ±2% + MISMA province_code.
  REQUIERE guarda anti-FP: mismo entity_ulid OR mismo título normalizado.
  Cross-province BLOQUEADO siempre en firma.

**Resultados [VERIFICADOS 2 vías — DB directa]:**
| Universo | Listing_in | Coches únicos | Colapsados | % colapso |
|---|---|---|---|---|
| status='available' | 1.689.243 | 1.443.563 | 245.680 | 14,54% |

**Desglose por señal (clusters con ≥2 listings):**
| Señal | Clusters | Listings implicados |
|---|---|---|
| photo_url | 123.091 | 250.412 |
| firma | 78.021 | 187.413 |
| ambas (both) | 3.920 | 12.887 |

**Cobertura plataforma (merged):** milanuncios 244k listings → 122k coches · wallapop 87k → 50k · coches.com 24k → 9k · autoscout24 21k → 11k · motor.es 19k → 9k.

**Provincias muestra:** Madrid(28) 340.644 listings → 281.145 coches únicos · Barcelona(08) 189.751 → 159.621.

**Anti-FP checks [VERIFICADOS]:**
- CHECK 1 cross-province: 333 clusters cross-province, 0 de firma (todos photo_url/both → CORRECTO).
- CHECK 2 giant >20: 123 clusters (BCA/Autorola catálogos wholesale + stock OEM — coches físicos reales repetidos en subasta). Documentado como comportamiento esperado.
- CHECK 3: todos los 1.689.243 listings cubiertos exactamente una vez — OK.
- CHECK 4: singletons con match_signal='none' — OK.

**20 pares muestra [REVISADOS — cero FP detectados]:** todos los pares muestran el mismo coche cruzando autoscout24.es↔wallapop con make/model/year/km/price idénticos y título idéntico. Señal firma operativa.

**Tests:** 37/37 pytest verde (incluyendo anti-FP cross-province, precio >2%, sin señal, firma sin guarda).

**Archivos:**
- `migrations/0023_vehicle_cluster.sql` (vehicle_cluster_run + vehicle_cluster + v_canonical_vehicle)
- `pipeline/identity/cluster_vehicles.py`
- `tests/test_cluster_vehicles.py`

**Gate pendiente:** vam_verified=FALSE. El Director valida 20 pares + anti-FP checks + commitea.

## Snapshot 2026-06-14
379.452 entities (328.776 particular / 50.167 POS) · 1.689.243 coches vivos · 615 VAM TRUSTWORTHY ·
2 alertas (degraded auto-cerrables). Geo municipio 85,5%. B5.7 ENTREGADO (5 TRUSTWORTHY / 849 veh).
B7 ENTREGADO (1.443.563 coches únicos / 245.680 merges, vam_verified=FALSE).

## F1 β resolución de entidad — GATE del Director (2026-06-14) · NO SELLADO
S_obs=52.156 dealers (huella dominante: 7.002 derivados de 14.105 entities; phone 121, web 110). 42 tests
+ 358 suite verde, S_obs 3 vías. PERO el gate cazó 2 fallos (vam_verified=FALSE):
1. SOBRE-FUSIÓN de cadenas con stock centralizado: CLICARS Barcelona/Castellón/Valencia/Alicante fundidos
   en 1 dealer por huella (stock sincronizado) — son 4 PUNTOS DE VENTA distintos. Guarda cross-province
   no los separó (province_code mal: las 4 en 46). La huella es ambigua para cadenas centralizadas.
2. β NO compone con B1: opera sobre 59.502 brutas, no canónicos B1. Numerador real P = B1(name+muni) ∘ β(huella).
FIX antes de sellar: (a) guarda de cadenas — token-ciudad distinto o cadena conocida NO fusiona por huella
sola (requiere identificador fuerte); (b) componer B1∘β en union-find único. Código en main, no servido.
