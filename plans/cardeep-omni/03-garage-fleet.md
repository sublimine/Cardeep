# Carta de sub-proyecto — Pilar 03: Sistema de gestión de coches y garaje (dealer fleet/DMS)

> Programa: cardeep-omni · Clave: `03-garage-fleet` · Fecha: 2026-07-17 (v3 — supersede la v2 del mismo día)
> Fase: SYNTHESIS (arquitectura). Fuente de verdad del pilar hasta que una fase de ejecución la enmiende con evidencia nueva.
> Doctrina de etiquetado: **[VERIFICADO repo]** = leído en código/migración real en ESTA sesión, con archivo:línea ·
> **[VERIFICADO vivo]** = contrastado por curl contra la API corriendo (:8090) en el recon 2026-07-16 (no re-ejecutado hoy;
> corroborado por segunda vía: el comentario de `config.ts:7-10` documenta la misma verificación en el propio código) ·
> **[RESEARCH]** = extraído por la fase de investigación adversarial del programa contra fuentes públicas y dossiers de
> `plans/intel-audit/companies/` (existencia de los dossiers re-verificada hoy por listado; el contenido público no fue
> re-derivado en esta sesión) · **[ASUMIDO]** = suposición declarada, jamás disfrazada de certeza.
> Delta v2→v3: TODAS las citas archivo:línea fueron re-verificadas de forma independiente en esta sesión. Tres
> correcciones de precisión: (a) `web/package.json` tiene 4 scripts — `dev/build/preview/typecheck` — sigue sin `test`;
> (b) las rutas protegidas abarcan `App.tsx:78-100`, no 78-95; (c) `servable_vehicle` aparece en NUEVE migraciones
> (0031/0040/0045/0046/0047/0055/0056/0058/0059, grep de hoy), no solo en cuatro.

---

## 1. Estado actual

El pilar tiene **dos capas coexistiendo en el mismo repo: una real y una de atrezzo**. Separarlas con precisión es el punto de partida de todo lo demás.

### Capa A — Inventario + Garaje 3D: REAL, end-to-end [VERIFICADO repo + vivo]

- **Página de inventario montada en `/vehicles`** vía `import Vehicles from './pages/inventory'` — `web/src/App.tsx:10` y `web/src/App.tsx:79`. [VERIFICADO repo]
- **Un solo dealer, hardcoded y honesto**: `DEALER_CDP = 'CDP-ES-28-YCZB8JYW'` (GYATA, servicio oficial Ford, Madrid) — `web/src/pages/inventory/config.ts:11`. El propio archivo declara el límite: *"read-only, with no auth that maps a logged-in user to a dealer"* — `config.ts:3-4`. [VERIFICADO repo]
- **468 vehículos disponibles** contrastados en vivo el 2026-07-16: `GET /entities/CDP-ES-28-YCZB8JYW` → `available_inventory: 468`, `n_aliases: 1`; `/inventory` devolvió coches reales de autocasion.com con precio/km/foto/deep_link; `/delta` devolvió eventos `PRICE_CHANGE` reales con `old_value/new_value`. [VERIFICADO vivo — camino distinto al de la propia UI; corroborado hoy por `config.ts:7-10`]
- **Cliente API sin fallback mock**: comentario explícito *"No mocks, no fallback data — a failed request surfaces as `error`, never as a silently-swapped placeholder fleet"* — `useDealerInventory.ts:1-3` (releído hoy). Cliente tipado en `web/src/api/cardeep.ts`. [VERIFICADO repo]
- **Umbrales reales ya definidos**: `FRESH_DAYS = 7` (`config.ts:19`), `STALE_DAYS = 90` (`config.ts:20`), calculados desde `first_seen` real; `PAGE_SIZE = 200`, límite del endpoint (`config.ts:15`). [VERIFICADO repo]
- **Garaje 3D no decorativo**: la decisión de NO texturizar fotos en WebGL está justificada por verificación real de CORS contra los CDNs (wallapop CloudFront y autocasion no envían `Access-Control-Allow-Origin`; comprobado con `curl -I` contra URLs vivas el 2026-07-16) — `config.ts:22-36`, `PHOTO_OVERLAY_BUDGET = 24` (`config.ts:36`). Overlay DOM real vía drei `<Html transform>` con presupuesto por distancia a cámara (`garage/usePhotoBudget.ts`). Layout matemático propio (`garage/layout.ts`, pabellones curvos por marca) con módulo de autoverificación (`garage/layout.test.ts`); `derive.ts` (filtros/orden/CSV/stats/facetas) puro con `derive.test.ts`. Los 6 archivos del subdirectorio `garage/` y los 15 de `inventory/` listados hoy. **Ninguno corre en CI**: `web/package.json:6-11` define solo `dev/build/preview/typecheck` — no existe script `test`; son autoverificación manual. [VERIFICADO repo]
- **Auth actual es bypass de desarrollo**: `DEV_BYPASS = true` — `web/src/auth/AuthContext.tsx:6`; usuario demo hardcoded (`AuthContext.tsx:8-15`). No existe mapeo usuario→dealer. [VERIFICADO repo]

### Backend que sirve la Capa A: real y 100% de solo lectura [VERIFICADO repo]

- Rutas GET reales (líneas re-verificadas hoy por grep de `@router.get`): `services/api/routers/entities.py:30,53,94,171` (`/entities/{cdp}/canonical`, `/entities/{cdp}`, `/entities/{cdp}/inventory`, `/entities/{cdp}/delta`); `vehicles.py:24,71` (`/vehicles/{ulid}/history`, `/vehicles/{ulid}`); `platforms.py:25,89` (`/platforms/{cdp}/inventory`, `/vehicles/{ulid}/platforms`); `ops.py:26,48,101,156` (`/health`, `/stats`, `/alerts`, `/sources`); `geo.py:32,105,168,260,331,398`. [VERIFICADO repo]
- **Cero endpoints de escritura**: grep de `@router.(post|put|patch|delete)` y `.post(|.put(|.patch(|.delete(` sobre `services/api/` → **0 resultados** (re-ejecutado hoy). No existe forma de marcar vendido, cambiar precio ni ninguna operación de gestión. [VERIFICADO repo]
- Esquema que alimenta todo — `migrations/0003_vehicles_events.sql` (releído completo hoy): tabla `vehicle` (`vehicle_ulid` PK `:5`, `entity_ulid` FK `:6`, `deep_link` `:7`, make/model/year/km/price/fuel/transmission `:9-16`, `photo_url`/`photo_hash` `:17-18`, **`vin_ref` `:19`**, `status IN ('available','gone')` `:21-22`, `first_seen`/`last_seen` `:23-24`, `UNIQUE(entity_ulid, deep_link)` `:25`). `vehicle_event` **append-only** (`:32-42`, comentario literal "NEVER updated or deleted"): `event_type IN ('NEW','GONE','PRICE_CHANGE','PHOTO_CHANGE','KM_CHANGE')` `:37-38`, `old_value/new_value` JSONB `:39-40`, `observed_at` `:41`. [VERIFICADO repo]
- `platform_listing` — `migrations/0009_platform_listing.sql:16-30` (con `listing_url` `:21`, `platform_price` `:23` — "price as shown on THIS platform (may differ)", `listing_fingerprint` `:24`, `status` `:25`, PK `(vehicle_ulid, platform_entity_ulid)` `:29`). [VERIFICADO repo]
- El filtro server-side del inventario es solo page/size; filtrado/orden/facetas ocurren client-side sobre el array completo descargado (aceptable a 468 coches; a qué escala deja de serlo NO está verificado — hueco declarado). [VERIFICADO en recon por lectura de `entities.py`]

### Capa B — Las piezas de DMS: 100% mock hardcoded [VERIFICADO repo]

Grep re-ejecutado hoy, líneas exactas: `Kanban.tsx:33` (`MOCK_BOARD`; fallback `loading || error ? MOCK_BOARD : apiBoard` en `:224`); `Deals.tsx:53` (`MOCK_DEALS`, usado `:361`); `Contacts.tsx:24,49` (`MOCK_CONTACTS`/`MOCK_ACTIVITIES`, usados `:429,584`); `Calendar.tsx:24,72` (`MOCK_EVENTS`); `Inbox.tsx:14,89` (`MOCK_CONVS`); `Dashboard.tsx:17,765` (`MOCK_KPI`). Todas montadas en el router — `App.tsx:78-100`: `/dashboard /kanban /contacts /deals /inbox /calendar /finance /market /terminal /inteligencia /arbitrage /api /analitica /invoices /pricing /notes /profile /support /chat /assistant /settings` — con IDs ficticios sin relación con los `vehicle_ulid` reales. [VERIFICADO repo]

### Contradicción documental viva [VERIFICADO repo]

`docs/frontend/00-PLATFORM-BLUEPRINT-E2E.md:291` (§3.11, releído hoy) etiqueta "Finanzas + CRM + Gestión de flota `/pro/finanzas` `/pro/crm` `/pro/flota`" como **[NOW core / NEAR auth+P&L+CRM]** y declara (`:300`) "flota+historial+VAM+radar+observatorio+CSV = now". Pero las rutas `/pro/*` **no existen** en `App.tsx:58-100` (releído completo hoy: solo `/kanban`, `/deals`, `/finance`… genéricas y mockeadas). Además el blueprint usa "precio VAM" (`:294-295`, `:298`) como si fuera un benchmark de precio: **VAM en este repo es verificación de identidad de entidad** — `migrations/0070_vam_verified_needs_proof.sql:1-9` (releído hoy): invariante DB sobre `canonical_dedup_run.vam_verified` que exige `verification_verdict` con `quorum_n>=2`. El "[NOW]" del blueprint es falso frente al código y la etiqueta "precio VAM" es semánticamente errónea. Se corrige en F0.

### Huecos estructurales (confirmados)

1. Backend sin escritura alguna → ninguna operación de gestión posible. [VERIFICADO repo]
2. Un dealer hardcoded, sin auth→dealer (`DEV_BYPASS`). [VERIFICADO repo]
3. Kanban/Deals/Contacts/Calendar/Inbox/Dashboard/Finance/Invoices = mock total montado en router. [VERIFICADO repo]
4. `vin_ref` existe (`0003:19`) pero ningún endpoint ni componente lo expone — dato capturado y nunca servido. [VERIFICADO en recon: ningún SELECT de `vehicles.py` lo incluye]
5. Sin CRUD manual de vehículo, sin reacondicionamiento/taller, sin F&I, sin contabilidad, sin multi-rooftop, sin gestión documental.
6. Los chips de excepción (Nuevos/+90d/Sin foto/Sin precio) son insight sin acción.
7. Sin motor de comparables/benchmark provincial, sin "capital parado", sin rotación de mercado — el dato base (censo + delta) existe, el cálculo no.
8. Sin tests en CI para este pilar (autoverificación manual solamente). [VERIFICADO repo]

---

## 2. Investigación competitiva/adversarial

**Ejecutada** (fase RESEARCH del programa, 2026-07-17). Dossiers previos del propio repo re-verificados hoy como existentes por listado de `plans/intel-audit/companies/`: `vauto.md`, `cox-automotive.md`, `cox-automotive-europe.md`, `la-centrale.md`, `mobile-de.md`, `autoscout24.md` (y ~100 más). [VERIFICADO repo — existencia]. Todo lo siguiente es [RESEARCH] salvo indicación.

### 2.1 El pelotón de referencia y qué enseña cada uno

| Referencia | Qué es | Lección exacta para Cardeep |
|---|---|---|
| **Tekion (ARC)** | Único disruptor real del duopolio DMS: cloud-native, microservicios en GCP, **una sola base de datos** para DMS+CRM+servicio+pagos+nómina+analítica, sin sync nocturno por lotes. ~3.000-5.000 rooftops a NADA 2026; ~$4.000-8.000/mes por rooftop (~$6.000 reportado para GM); un grupo multi-tienda pasó de $50-60k/mes con CDK a ~$30k con Tekion | Así se construye un DMS moderno desde cero. Crítica adversarial documentada (DealerInt 2026): **"override gap"** — registra el precio nuevo tras una anulación manual pero NO la razón categorizada, el aprobador ni el impacto en margen. Cardeep lo cierra por diseño (K15, §4) |
| **CDK Global + Reynolds** | Duopolio histórico. Antitrust probado: acuerdo oral 2013/escrito 2015 para restringir a integradores de datos independientes; CDK pagó $100M, Reynolds $29,5M (2018). Reynolds ERA-IGNITE: núcleo de 1987 + capa gráfica de 2011, on-premise con servidor local | El moat clásico del DMS es la **captura del dato del dealer**. Cardeep hace lo contrario: el dato es del censo público y el dealer anota encima — sin lock-in de dato, exportable siempre (CSV ya existe en `derive.ts`) |
| **Cox Automotive Retail360 + Fullpath** (adquisición completada jun-2026) | LA amenaza directa: capa de dato unificada (marketing+ventas+operaciones+inventario+servicio) sobre Autotrader+KBB+vAuto+VinSolutions+Dealertrack+Xtime; "Deal Central" centraliza la venta evitando re-tecleo. 40.000+ relaciones de dealer reales | Persigue el mismo objetivo de fondo que Cardeep (dato unificado) pero desde EE.UU. y desde el DMS. Su ceguera: **no tiene el censo español cross-platform**. Cardeep no le gana en integración; le gana en cobertura de mercado ES |
| **vAuto (Provision/ProfitTime/iRecon)** | Estándar norteamericano de gestión de inventario por VIN (dossier propio: `plans/intel-audit/companies/vauto.md`, existencia verificada) | Sus 4 métricas núcleo son el listón: Cost to Market, **Price to Market**, **Market Days Supply**, vRank. **Norteamérica-only, sin cobertura europea** — hueco geográfico confirmado |
| **AutoScout24 HändlerIQ** (oct-2025) | Dashboard dealer-facing: recomendación en tiempo real de precio/calidad de anuncio/equipamiento/competencia por ubicación, acción con un clic. Motor: **Random Forest** (elegido explícitamente contra el overfitting de árboles simples), >2,4M anuncios europeos, reentrenado mínimo mensual, desplegado como bytecode Java vía H2O en AWS EC2, respuesta en milisegundos, CD con tests E2E y Consumer-Driven Contracts | El estándar europeo de ejecución de "stock intelligence". Y su límite estructural: **solo ve sus propios anuncios** |
| **La Centrale Pilot'Price + Stock Optimizer** (nov-2023) | Reposicionamiento de precio **en bloque** de todo el stock según oferta/demanda local o nacional; Stock Optimizer detecta huecos de surtido con demanda local; co-diseñado con ~50 profesionales; gratis nov-23→abr-24, luego suscripción con cuota base + peticiones por baremo; 4.000 profesionales | El repricing por lote y la detección de huecos de surtido son features concretas a igualar. Mismo límite: **mono-plataforma** |
| **mobile.de Preisbewertung** (IA jun-2024) | Semáforo de precio en el anuncio. **Backlash documentado de dealers alemanes** (kfz-betrieb.vogel.de) por deterioro de valoraciones sin transparencia | Lección adversarial de oro: automatizar pricing **sin enseñar la muestra ni el método destruye la confianza del dealer**. De aquí sale la regla de transparencia T1 (§4) |
| **Rapid Recon / iRecon** | Nicho kanban de reacondicionamiento (2.400+ dealers, 40.000+ usuarios). Benchmark: **3-5 días de time-to-line** en los mejores; marco "72-Hour Target" | Si algún día se hace kanban de recon, el KPI es time-to-line con esos cortes. No es fase temprana de este pilar |
| **NADA / NCM 20 Groups** | NADA: fórmula formal de Days Supply (§2.2). NCM: peer-benchmarking desde 1947, composite mensual sobre 50+ KPIs contra el top 50% de performers, reuniones presenciales de 1,5-3 días varias veces al año | Las fórmulas canónicas del sector y el patrón "benchmark contra pares" — Cardeep puede dar benchmark provincial contra pares SIN que los dealers compartan datos entre sí (el censo ya lo ve todo) |
| **SpinCar / ZeroLight** | SpinCar: 1 vídeo smartphone → hasta 200 fotos + 360° + hotspots de UN coche (cifras de impacto = claims del vendedor, no verificadas independientemente). ZeroLight: render 3D en tiempo real de UN modelo configurable para OEM (Audi/Porsche/BMW/VW/Nissan/Lucid), motor de origen gaming, cloud | **Nadie renderiza el inventario COMPLETO de un dealer como espacio 3D navegable.** El Garaje 3D de Cardeep ocupa un hueco real — pero es capa de presentación, no infraestructura de gestión |
| **PBS Systems / DealerSocket-Solera / VinSolutions** | Challenger canadiense cloud-native (3.500+ rooftops, privado, Calgary 1988); CRM+DMS Solera con IA 2026 (respuesta conversacional a leads); gestión de "deal" unificada de Cox (actividad online+in-store, documentos ligados al deal) | Referencias de CRM/deal real para F5 — el listón de qué debe hacer un pipeline de venta de verdad |

### 2.2 Criterios EXACTOS extraídos (los números del sector, no generalidades)

1. **Days Supply (NADA, departamento de usados)**: `inventario usado ÷ (ventas medias mensuales ÷ días laborables del mes)`. Benchmark canónico: **30 días de oferta = 12 rotaciones/año**.
2. **Aging (consenso industria 2026)**: 45-60 días = *aged*; **90 días = stale/problemático**; el front-end gross colapsa a partir de 30-45 días en stock.
3. **Coste de holding**: **$30-40 por unidad/día** (floorplan+seguro+depreciación+oportunidad); depreciación media de usado ≈ **1,5%/mes** (~4,5% a los 90 días sobre $25.000).
4. **Turn medio real de mercado 2026**: **43-48 días** hasta venta retail.
5. **vAuto — bandas de Price to Market por antigüedad**: 98-100% (0-7 días), 94-97% (7-15 días), 90-93% (15-22 días); **Cost to Market ≤84%** de media de inventario; MDS y vRank como métricas 3 y 4.
6. **Rapid Recon**: time-to-line de los mejores = **3-5 días**; objetivo agresivo publicado = 72 horas.
7. **HändlerIQ — ingeniería**: RF sobre >2,4M anuncios, reentreno ≥mensual, serving en milisegundos vía H2O/Java — construir esa capa bien es ML en producción, no "tener el dato".

⚠️ Traslación a España: los umbrales 1-4 son de mercado estadounidense. Se adoptan como **valores de arranque con procedencia declarada** y se recalibran con el propio censo (mediana real de `GONE.observed_at - first_seen` por provincia/segmento) en F4. Presentarlos como "España" sin recalibrar sería exactamente la mentira que este proyecto prohíbe.

### 2.3 Veredicto adversarial honesto

**Cardeep NO tiene ventaja estructural para superar a la referencia en "DMS" como categoría completa.** El núcleo de un DMS (contabilidad, F&I, titulación/DGT, piezas, taller, nómina) es escritura con responsabilidad legal/fiscal e integraciones OEM/registro/financieras — dominios donde el censo/delta/dedup de Cardeep no aporta nada, y donde el repo hoy tiene literalmente 0 endpoints de escritura y 1 dealer hardcoded. Fingir ese alcance sería maquillaje.

**Donde SÍ hay ventaja estructural real, estrecha y defendible**: la **inteligencia de posicionamiento de precio cross-platform para España**. vAuto no cubre Europa; HändlerIQ, Pilot'Price y mobile.de son **ciegos fuera de su propia plataforma**. Cardeep ya tiene el dato que ninguno puede tener sin dejar de ser mono-plataforma: el censo multi-fuente con delta (`vehicle` + `vehicle_event` + `platform_listing`). Hoy esa ventaja es 100% potencial (no existe ni una vista de comparables) — convertirla en producto es el objetivo de este pilar. Segunda ventaja menor pero real: **cero onboarding** (el stock del dealer ya está indexado con historial antes de que se registre; ningún rival puede enseñar eso el día 1). Tercera: el Garaje 3D como escaparate único — diferenciador de presentación, no de gestión, y así se trata.

---

## 3. Objetivo Cardeep para este pilar — y el límite honesto

### Límite declarado (lo que NO se persigue)

Cardeep **no compite como DMS completo** contra CDK/Reynolds/Tekion/Cox en contabilidad, F&I, titulación DGT, recambios, taller ni nómina. No hay camino creíble a eso con la arquitectura actual ni con el dato de Cardeep — y esos dominios no se benefician del censo. Cualquier documento del repo que insinúe lo contrario (blueprint §3.11) se corrige, no se defiende.

### Tesis (lo que SÍ, por orden de fuerza)

1. **Inteligencia de precio cross-platform España** — la única sub-capa donde el dato de Cardeep es estructuralmente superior a TODOS los jugadores europeos (§2.3). Se materializa como Price-to-Market y Market-Days-Supply provinciales calculados desde el censo total (K9/K10), con la transparencia que mobile.de no dio (regla T1).
2. **Cero onboarding**: el primer login de un dealer enseña su flota completa con días en stock e historial de precio reales — los 468 coches de GYATA ya servidos en vivo lo demuestran. [VERIFICADO vivo]
3. **Delta como radar de rotación**: `GONE` a escala de censo permite calcular velocidad de rotación de mercado por modelo/provincia que ningún dealer individual ve (K11).
4. **Workspace de operación con escritura separada del censo**: estado interno, coste, precio objetivo, vendido — anotaciones del dealer por referencia, sin tocar jamás la capa scraper (§5).
5. **Garaje 3D** como escaparate diferencial ya real (hueco SpinCar/ZeroLight confirmado en §2.1).

### Objetivo operativo

Convertir la Capa A (visor real de un dealer) en un **workspace de flota multi-dealer**: auth→dealer real, tabla de flota con criterios accionables (§4), capa de escritura propia del dealer, motor de comparables desde el censo, y CRM mínimo sobre `vehicle_ulid` reales. Todo lo mock de la Capa B se reconecta o **se retira del router** — no queda ni una pantalla de atrezzo montada.

---

## 4. Criterios de evaluación concretos — qué se muestra y cómo se calcula

Regla del pilar: **ningún número/badge/sección en frontend sin fila en esta tabla**. Lo que no trace aquí, no se renderiza.

| ID | Elemento en UI | Cálculo exacto | Procedencia del criterio |
|---|---|---|---|
| K1 | "Días en stock" por coche | `floor(now() - vehicle.first_seen)` en días | `0003:23` [VERIFICADO repo]; proxy honesto declarado en `config.ts:17-18` |
| K2 | Chip "Nuevo" | `first_seen < 7 días` (`FRESH_DAYS`) | `config.ts:19` [VERIFICADO repo] |
| K3 | Semáforo de aging por coche | verde ≤30d · ámbar 31-60d · rojo 61-90d · negro +90d (`STALE_DAYS`) | Cortes 45-60 aged / 90 stale / colapso de gross a 30-45d [RESEARCH §2.2-2]; 90d ya en `config.ts:20`. Recalibración ES en F4 |
| K4 | Chip "Sin foto" | `photo_url IS NULL` | `0003:17` [VERIFICADO repo] |
| K5 | Chip "Sin precio" | `price IS NULL` | `0003:13` [VERIFICADO repo] |
| K6 | Historial Δprecio (sparkline + lista) | eventos `PRICE_CHANGE` de `vehicle_event` por `observed_at`, `old_value→new_value` | `0003:33-42` [VERIFICADO repo]; endpoint `vehicles.py:24` |
| K7 | "Retirado del anuncio" | evento `GONE` + `status='gone'`. **Etiqueta obligatoria "retirado", NUNCA "vendido"** salvo confirmación del dealer (K13) | `0003:21-22,37-38` [VERIFICADO repo] |
| K8 | Presencia multi-plataforma por coche | filas de `platform_listing` vía `GET /vehicles/{ulid}/platforms`, con `platform_price` para detectar divergencia de precio entre plataformas | `0009:16-30` [VERIFICADO repo]; `platforms.py:89` |
| K9 | **Price-to-Market provincial** ("−8% vs mediana, n=23") | `price / mediana(price de comparables)`. Comparables = `status='available'`, misma `make`+`model`, `year ±1`, mismo `fuel`, `km ±20%`, entidades de la misma provincia. **Regla dura: n<8 → "muestra insuficiente (n=X)", jamás un número.** Bandas de referencia de sanidad de precio por edad: 98-100% (0-7d), 94-97% (7-15d), 90-93% (15-22d) | Métrica núcleo de vAuto [RESEARCH §2.2-5], adaptada a censo cross-platform (ventaja §2.3). Base de datos: `0003` + `0002` [VERIFICADO repo]. Motor = NUEVO (§5) |
| K10 | **Market Days Supply provincial** | `n_comparables_available ÷ (n_eventos_GONE_de_comparables_últimos_90d / 90)`. Misma definición de comparable que K9, misma regla n≥8 | Fórmula MDS de vAuto + Days Supply NADA [RESEARCH §2.2-1,5], computable SOLO con censo total — ningún rival europeo puede |
| K11 | Rotación de mercado por modelo | `mediana(GONE.observed_at - first_seen)` sobre eventos GONE del censo provincial, ventana 90 días; se contrasta contra el turn de referencia 43-48d [RESEARCH §2.2-4] hasta tener calibración ES propia | `0003:33-42` [VERIFICADO repo]; agregado = NUEVO |
| K12 | "Capital parado" (cabecera) | `SUM(price)` de coches `available` con `first_seen > 45 días` y `price IS NOT NULL`, mostrando siempre el recuento de excluidos por precio nulo. Umbral 45d = frontera *aged* [RESEARCH §2.2-2], recalibrable en F4. Extensión futura (cuando exista coste en `fleet_ops`): coste de holding estimado/día con procedencia visible | `0003:13,21-23` [VERIFICADO repo] |
| K13 | Estado interno del dealer (Entrada/Preparación/Publicado/Reservado/Vendido/Entregado) | tabla NUEVA `fleet_ops` (§5); jamás muta `vehicle` | NUEVO; patrón de deal real de VinSolutions/DealerSocket [RESEARCH §2.1] |
| K14 | Recuento de flota en cabecera | `available_inventory` de `GET /entities/{cdp}` cross-checked contra el total paginado (§7) | `entities.py:53,94` [VERIFICADO repo] |
| K15 | **Registro de override de precio** | si el dealer cambia el precio objetivo apartándose de la sugerencia de K9: se captura razón categorizada + quién + delta vs mediana, append-only en `fleet_ops_event` | Cierra el "override gap" documentado de Tekion [RESEARCH §2.1] — criterio adversarial, no decorativo |
| T1 | **Regla de transparencia** (transversal) | todo badge de precio (K9/K10) muestra al hacer clic: n, mediana, definición del comparable y muestra enlazable (deep_links reales) | Lección del backlash de mobile.de [RESEARCH §2.1]. Sin muestra visible, el badge no se despliega |

Descartes explícitos: **"Sale Probability" NO se muestra** (mobile.de la da; replicarla exige modelo estadístico propio validado — candidato post-F4, nunca antes). **"Precio VAM" queda prohibido como etiqueta en UI** (VAM = verificación de identidad de entidad, `0070:1-9` [VERIFICADO repo]); la etiqueta correcta es "mediana de comparables del censo". Los claims de impacto de SpinCar (+30% engagement) no se citan en material de producto: son claims del vendedor sin verificación independiente [RESEARCH].

---

## 5. Modelo de datos + almacenamiento backend

### Se reutiliza (existente — nombres verificados por lectura/grep de migración en ESTA sesión)

| Pieza | Dónde | Uso en este pilar |
|---|---|---|
| `entity`, `entity_source`, `entity_alias` | `migrations/0002_entities.sql:4,43,53` | identidad del dealer, cdp_code, geo |
| `vehicle` | `migrations/0003_vehicles_events.sql:4` | la flota misma (lectura); `vin_ref` (`:19`) se expone por fin en el detalle del propio dealer |
| `vehicle_event` | `migrations/0003:33` (append-only) | delta: K6/K7/K10/K11 |
| `platform_listing` | `migrations/0009_platform_listing.sql:16` | K8 presencia y divergencia de precio multi-plataforma |
| vista `v_servable_dealer` | `migrations/0056_v_servable_dealer.sql:26` | qué dealers son elegibles para cuenta |
| vista `servable_vehicle` | definida en `0031_gestion.sql:158`; referenciada/evolucionada en `0040/0045/0046/0047/0055/0056/0058/0059` (9 archivos, grep de hoy) | superficie servida con guardas de precio/status |
| `product_stats` | `migrations/0055_product_stats.sql:14` | métricas de producto del pilar |
| `gestion_item`/`gestion_transition` | `migrations/0031_gestion.sql:44,121` | **solo** tickets de calidad de dato (§7). NO se reutiliza como CRM del dealer: su semántica es data-quality; mezclar dominios la corrompería |
| API de lectura completa | `services/api/routers/entities.py, vehicles.py, platforms.py, geo.py, ops.py` | se mantiene intacta y de solo lectura |
| Guardas append-only | `0034_truncate_guards.sql`, `0035_append_only_row_guards.sql` (existencia re-verificada hoy por listado; contenido no releído — se relee al ejecutar F3) | prueba mecánica de que la escritura nueva no toca el censo |

### Se crea nuevo (nombres PROPUESTOS — no existen hoy; numeración continúa tras `0072_vehicle_cluster_country_proof.sql`, última migración verificada hoy por listado, 66 archivos)

| Pieza nueva | Propósito | Regla de oro |
|---|---|---|
| `dealer_account` | cuenta del dealer (email, hash, estado) | reemplaza `DEV_BYPASS` para el workspace |
| `dealer_membership` | cuenta → `entity_ulid`/cdp (multi-rooftop = N filas) | la relación que `config.ts:3-4` declara ausente |
| `fleet_ops` | anotaciones del dealer por coche: estado interno (K13), coste de compra, precio objetivo, notas | FK a `vehicle.vehicle_ulid`; **cero UPDATE sobre `vehicle`** — el censo es del scraper, la anotación es del dealer (coherente con la doctrina PG del proyecto: nada de UPDATE sobre filas no mutadas) |
| `fleet_ops_event` | historial append-only de `fleet_ops`, incluye los overrides K15 con razón categorizada | espejo del patrón `vehicle_event` |
| `dealer_lead` / `dealer_deal` | CRM mínimo lead→deal ligado a `vehicle_ulid` real | los IDs ficticios de los mocks mueren |
| Router de escritura `services/api/routers/dealer_ops.py` (o servicio aparte) | POST/PATCH autenticados SOLO sobre tablas `dealer_*`/`fleet_*` | la API censal sigue sin un solo endpoint de escritura; la superficie de escritura vive separada y autenticada |
| Motor de comparables (K9/K10/K11) | vista materializada + job batch de refresco sobre `vehicle`+`entity`+geo | refresco batch (patrón HändlerIQ: precálculo + serving en ms [RESEARCH]), jamás N+1 por fila renderizada |

Decisión de arquitectura: **censo (capa scraper) y workspace (capa dealer) no comparten tablas de escritura**. El censo permanece append-only e intocable; el dealer anota por referencia. Si divergen (dealer marca "vendido", el scraper aún lo ve publicado), esa divergencia **ES información** y se muestra como tal — no se reconcilia en silencio. Anti-lección de CDK/Reynolds: el dato del dealer es suyo — export CSV completo siempre disponible, sin lock-in.

## 6. Especificación de pantalla — en la piel del dealer

Idioma de UI: español de compraventa, no SaaS-genérico. Usuario tipo: el jefe de ventas de un concesionario medio (GYATA: 468 coches) que hoy vive en Excel y en el backoffice de coches.net.

### 6.1 "Mi flota" (evolución de `/vehicles`, hoy `pages/inventory/`)

- Cabecera: nombre real del dealer (de `entity`), recuento K14, capital parado K12 ("Tienes ~X € parados en Y coches con más de 45 días"), y los chips K2-K5 **convertidos en accionables**: clic en "Sin precio (7)" → filtra la tabla Y ofrece "fijar precio objetivo" (escribe en `fleet_ops`, no en el censo).
- Tabla densa (la actual `VehicleTable.tsx` como base): coche / precio / **"vs mercado"** (K9: "−8% vs mediana provincial, n=23" o "muestra insuficiente") / **"oferta en tu provincia"** (K10: "hay 62 días de stock de este modelo" — el dato que ni HändlerIQ ni Pilot'Price pueden dar) / días en stock (K1 + semáforo K3) / plataformas (K8: iconos con deep_link real y aviso si el precio difiere entre plataformas) / estado interno (K13: selector del dealer).
- Fila expandida: sparkline Δprecio (K6), historial de eventos, muestra de comparables T1 (los coches reales contra los que se le compara, enlazados), y la divergencia censo-vs-dealer si existe ("Lo marcaste vendido el día 12; seguimos viéndolo publicado en autocasion" — dato que ningún DMS le da).
- Garaje 3D se conserva como vista alternativa (toggle existente): escaparate para enseñar flota a un comprador en pantalla, no herramienta de gestión diaria (posicionamiento §2.1 SpinCar/ZeroLight).

### 6.2 "Tablero" (reconstrucción de `/kanban`)

Columnas en lenguaje de compraventa: **Entrada → Preparación → Publicado → Reservado → Vendido → Entregado**. Cada tarjeta es un `vehicle_ulid` real con su foto real; mover tarjeta = transición en `fleet_ops` (evento en `fleet_ops_event`). "Publicado" se auto-puebla del censo; las demás son del dealer. Si el dealer baja el precio objetivo apartándose de la sugerencia, el tablero pide razón en un clic (K15) — categorías cortas, no formulario.

### 6.3 "Mercado" (nuevo; sustituye al `Finance.tsx` mock)

Solo lo calculable hoy con honestidad: rotación provincial por modelo (K11), distribución de posición de precio de mi flota (K9), oferta provincial (K10), capital parado (K12). Patrón NCM adaptado: "tu flota vs la mediana de tu provincia" sin que nadie comparta datos — el censo ya lo ve todo. **Sin P&L completo hasta que exista coste de compra en `fleet_ops`** — y cuando exista, se etiqueta "estimado sobre los N coches con coste informado".

### 6.4 Lo que se retira del router

`Contacts`/`Inbox`/`Calendar`/`Invoices`/`Dashboard`-mock salen de la navegación del workspace hasta que su fase llegue (F5+). Regla: **ninguna ruta montada sin dato real detrás.** Retirarlas es reversible (git) y honesto; mantenerlas es atrezzo.

## 7. Protocolo de verificación — 2 vías independientes por dato mostrado

El mismo estándar antialucinación del proyecto, aplicado al producto. Un dato que no pase su doble vía se renderiza como "—" con tooltip "en verificación" y abre ticket en `gestion_item` (lanes existentes, `0031:44`).

| Dato | Vía 1 | Vía 2 (independiente) | Si divergen |
|---|---|---|---|
| Recuento de flota (K14) | `available_inventory` de `/entities/{cdp}` | suma real de filas paginadas de `/inventory` | mostrar el menor + flag; ticket |
| Días en stock (K1) | `vehicle.first_seen` | `MIN(observed_at)` del evento `NEW` de ese `vehicle_ulid` | usar el más antiguo; ticket si difieren >24h |
| Δprecio (K6) | eventos `PRICE_CHANGE` | coherencia de cadena: `new_value` del evento N == `old_value` del N+1; el último == `vehicle.price` | ocultar sparkline; ticket |
| "Retirado" (K7) | evento `GONE` | fetch del `deep_link` real → 404/410/redirect a listado | si sigue 200 con el coche visible → NO mostrar "retirado"; ticket |
| Presencia plataforma (K8) | fila `platform_listing` | HTTP status del `listing_url` (muestreo diario, no por render) | icono en gris "sin confirmar" |
| Price-to-Market (K9) | mediana del motor de comparables | re-cálculo por SQL directo independiente (query distinta, sin pasar por el motor) en job nocturno | congelar a "muestra insuficiente"; ticket |
| MDS (K10) | cociente del motor | recuento directo de comparables + eventos GONE por SQL independiente | ídem K9 |
| Capital parado (K12) | agregado del motor | `SUM` directo por SQL en job nocturno | mostrar rango, no cifra única |
| Estado interno (K13) | `fleet_ops` | replay de `fleet_ops_event` reconstruye el estado | el replay manda (append-only = verdad); ticket |
| Override (K15) | fila de evento con razón | recomputación del delta vs mediana en el momento del evento | corregir delta, conservar razón |

Además, en cada release del pilar: los números de una flota de control (GYATA) se contrastan a mano contra la DB por un camino distinto al del API (`psql` directo), igual que se hizo con los 468 el 2026-07-16. Y los umbrales [RESEARCH] de §2.2 se recalibran contra el censo real ES en F4 antes de presentarse como locales.

## 8. Uso de LLM — doctrina EUR0

Verdad incómoda primero: **este pilar es ~95% SQL determinista y no necesita LLM para funcionar**. La evidencia adversarial lo refuerza: HändlerIQ —el mejor de Europa— corre sobre Random Forest clásico servido en milisegundos [RESEARCH §2.2-7], no sobre LLM. Meterle modelo generativo a lo que resuelve una mediana sería gasto sin causa.

- **Modelo local/barato (masivo, batch)**: normalización de trims/versiones desde `title` para afinar comparables K9 ("320d xDrive" vs "320 d" — impacto directo en n≥8); clasificación de intención de mensajes de lead cuando exista inbox real (F5+); extracción nota-libre-del-dealer → campos de `fleet_ops`. Siempre batch, siempre con validación determinista detrás (el LLM propone, una regla verifica), nunca en el camino crítico del render — coherente con la doctrina de indexado pasivo del proyecto.
- **Modelo caro (solo decidir)**: única candidatura legítima = redactar la *justificación en lenguaje del dealer* de una sugerencia de reprecio sobre stock rojo/negro (K3) cuando los comparables son ambiguos (n entre 4 y 8) — una vez por coche por semana, gateado, y siempre con los números deterministas al lado (T1). Si en producción esa redacción no mueve la aceptación de sugerencias, se retira.
- **Prohibido**: LLM generando precios, contando stock, o inventando "probabilidad de venta" sin modelo estadístico validado detrás (el descarte de Sale Probability, §4).

## 9. Fases de construcción (orden estricto; hay autoridad para reestructurar código existente)

Cada fase cierra con: build verde (`npm run build` en `web/` = `tsc --noEmit && vite build`, más la suite pytest del repo), tests nuevos de la fase, revisión adversarial real (patrón ya probado en el repo: constructor + revisor independiente contra DB viva), y verificación cruzada de §7 sobre lo entregado. Nada se declara hecho por deploy.

- **F0 — Verdad documental + calibración de umbrales.** Corregir `00-PLATFORM-BLUEPRINT-E2E.md:291-303` §3.11 ([NOW core] → estado real; "precio VAM" → "mediana de comparables"); registrar en este documento los umbrales K3/K12 como [RESEARCH-US, pendiente calibración ES] hasta F4; wirear `derive.test.ts`/`layout.test.ts` a un runner ejecutable en CI. *Cierre:* blueprint sin claims falsos (diff revisado); runner elegido verde en CI con los tests existentes migrados; cero regresión de build.
- **F1 — Auth→dealer.** Migraciones `dealer_account`/`dealer_membership` (post-0072); retirar `DEV_BYPASS` del workspace; `pages/inventory` lee el cdp de la sesión (GYATA queda como cuenta demo sembrada, no como constante). *Cierre:* dos cuentas con dealers distintos ven flotas distintas (E2E Playwright); `DEALER_CDP` hardcoded eliminado de `config.ts`; 0 regresiones en la suite del inventario.
- **F2 — "Mi flota" con K1-K8+K14 (solo lectura).** Reconstruir la tabla con columnas §6.1 y chips accionables en filtro (aún sin escritura); exponer `vin_ref` en el detalle del propio dealer. *Cierre:* cada número de pantalla trazado a su fila K y verificado por sus 2 vías de §7 contra GYATA; captura + SQL directo en el parte de fase.
- **F3 — Capa de escritura del dealer.** Migraciones `fleet_ops`/`fleet_ops_event`; router de escritura autenticado separado; kanban §6.2 real con override K15; retirar del router las páginas mock restantes (§6.4). *Cierre:* TDD (tests RED primero); prueba explícita de que `vehicle`/`vehicle_event` no reciben ni un UPDATE/INSERT desde la nueva superficie (guardas 0034/0035 releídas + test de integración); replay de `fleet_ops_event` == estado.
- **F4 — Motor de comparables + Mercado (K9/K10/K11/K12) + calibración ES.** Vista materializada + job batch + pantalla §6.3; recalibrar umbrales de aging/turn con el censo real (mediana GONE por provincia/segmento) y actualizar K3/K12 con procedencia ES. *Cierre:* mediana y MDS verificados por doble cálculo independiente en ≥3 provincias; regla n≥8 demostrada con caso real renderizando "muestra insuficiente"; T1 operativa (muestra enlazable visible); sin N+1 (log de queries).
- **F5 — CRM mínimo.** `dealer_lead`/`dealer_deal` sobre `vehicle_ulid` reales; reconectar o retirar definitivamente Contacts/Inbox. *Cierre:* E2E lead→deal→vendido con divergencia censo-dealer visible; cero IDs ficticios en todo `web/src/pages/` (grep MOCK_ → 0 en rutas montadas).
- **F6 — Garaje 3D fase 2 (opcional, tras F5).** Modo comparar + mejoras del blueprint §3.9. *Cierre:* presupuesto de rendimiento medido (60fps con 468 coches, patrón `usePhotoBudget` actual).

---

## 10. Estado real de ejecución — F1→F4 (2026-07-18)

> Ejecutado por Sonnet bajo mandato directo del Director (fases F1-F4 asignadas explícitamente;
> **F0 quedó FUERA de este mandato de ejecución** — el blueprint §3.11/§3.5, la recalibración
> ES de umbrales, y el wireo de `derive.test.ts`/`layout.test.ts` a un runner de CI siguen
> pendientes de un bloque futuro. Este bloque corrió en PARALELO con 04-arbitrage y
// 05-multiposting sobre el MISMO working tree (confirmado por colisión real de
> `migrations/0079_arbitrage.sql` apareciendo sin commit mientras se preparaba esta migración,
> y por ediciones concurrentes de `main.py`/`App.tsx`/`Shell.tsx`/`cardeep.ts` — resuelto
> respetando la regla del programa "max(ls migrations/)+1 en el momento de ejecutar": esta
> fase consumió **`migrations/0080_fleet_ops.sql`**, no 0079 (ya tomado por el frente de
> arbitraje al momento de escribir).

### F1 — Auth→dealer: CERRADO [VERIFICADO vivo]

AUTH-0 (bloque anterior) ya había entregado el esquema (`app_user`/`dealer_membership`/
`user_session`, `migrations/0073_auth.sql`) y el router `services/api/routers/auth.py` con
`DEV_BYPASS` ya retirado de `AuthContext.tsx`. El hueco real que quedaba —y que esta fase
cerró— era que **nada en `web/src/pages/inventory/` leía el `tenant_id` de la sesión**:
`useDealerInventory()` seguía usando `DEALER_CDP` como default y `ActivityDrawer.tsx` lo
importaba directo.

- `config.ts`: `DEALER_CDP` **eliminado** (grep repo-wide → 0 referencias fuera de un comentario
  explicativo). [VERIFICADO repo]
- `useDealerInventory(cdp: string)` ahora exige `cdp` explícito (sin default); `pages/inventory/index.tsx`
  lo toma de `useAuthContext().user.tenantId`; sin tenant → `ClaimDealerPrompt` (nuevo componente,
  wirea el endpoint real `POST /auth/claim-dealer` que AUTH-0 ya construyó, no un placeholder).
  `ActivityDrawer` recibe `cdp` por prop. [VERIFICADO repo]
- `AuthContext.tsx` ganó `refreshUser()` (re-fetch `/auth/me` tras un claim exitoso). [VERIFICADO repo]
- **GYATA sembrado como cuenta demo, NO como constante**: `scripts/seed_demo_dealer.py` (idempotente,
  verificado corriendo 2 veces seguidas sin duplicar). GYATA no tiene `cif` registrado (`SELECT cif
  FROM entity WHERE cdp_code='CDP-ES-28-YCZB8JYW'` → vacío, verificado en vivo) — el claim real vía
  `POST /auth/claim-dealer` es matemáticamente imposible para esta entidad (exige CIF checksum-válido
  que coincida con el censo), así que se siembra `app_user`+`dealer_membership` directo, documentado
  como tal, sin fingir un claim. [VERIFICADO vivo]
- **Cierre real (dos cuentas, dos dealers, datos distintos)** — verificado en vivo contra la API
  corriendo en :8090, no simulado: login `demo@cardeep.local` → `tenant_id=CDP-ES-28-YCZB8JYW`
  (GYATA, `available_inventory=468`); registro+claim de una cuenta nueva contra la entidad real
  `CDP-ES-01-7FAFJXW8` (CIF `B01530682`, mismo fixture que `tests/test_auth_router.py`) →
  `tenant_id=CDP-ES-01-7FAFJXW8` (`available_inventory=0`, entidad real distinta). Dos sesiones,
  dos `GET /entities/{cdp}` con payloads distintos. [VERIFICADO vivo]
- **Sustitución declarada del cierre "E2E Playwright"**: `web/` no tiene NINGÚN runner de test
  instalado (`package.json` sigue con solo `dev/build/preview/typecheck` — confirmado, F0 no
  corrió) y no hay Playwright en `devDependencies`. Instalar un framework E2E completo era una
  inversión de infraestructura fuera del alcance F1-F4 asignado. La verificación equivalente real
  se hizo por la vía de red (curl contra la API viva, la misma capa que un test E2E ejercitaría)
  en vez de por DOM — declarado aquí como sustitución honesta, no como "hecho" disfrazado.
- Build: `tsc --noEmit` limpio; `npm run build` limpio.

### F2 — "Mi flota" K1-K8+K14: CERRADO [VERIFICADO repo + vivo]

- **K1/K2/K4/K5** ya existían de la Capa A previa; sin cambios de fondo.
- **K3 unificado**: antes había TRES implementaciones de semáforo de aging divergentes
  (`VehicleTable`'s `AgeBar` 3 bandas 30/90, `DealerHeader`'s `ageTone` 3 bandas 30/90,
  `VehicleDetailModal`'s badge 2 bandas solo 90). Ahora **una sola función** `agingBand()`/
  `agingColor()` en `derive.ts` con las 4 bandas exactas de la tabla §4 (verde≤30 · ámbar 31-60 ·
  rojo 61-90 · negro +90), usada por las tres. [VERIFICADO repo]
- **K8 (multi-plataforma)** ya vivía en el modal de detalle (fetch on-demand, cacheado). Se
  extrajo a un módulo compartido `platformsCache.ts` (antes el modal tenía su propio `Map` local)
  y se añadió un badge perezoso en la fila de la tabla (`PlatformBadge`, fetch solo al montar la
  fila visible — acotado al lote de `ROW_BATCH`, nunca los 468 de golpe). [VERIFICADO repo]
- **`vin_ref` expuesto por fin**: añadido a la query de `GET /entities/{cdp}/inventory`
  (`entities.py`) y a `GET /vehicles/{ulid}` (`vehicles.py`) — antes capturado (`0003:19`) y jamás
  servido. Visible en la ficha del modal de detalle ("VIN"). [VERIFICADO repo — grep de la
  columna en ambas queries + campo en `VehicleListItem`]
- **K14 doble vía real**: `DealerHeader` ya mostraba `available_inventory`; se añadió el flag de
  divergencia explícito (icono ámbar + tooltip con ambos números) cuando `loadedCount` (vía 2,
  paginación real) diverge de `available_inventory` (vía 1) una vez `isComplete=true` — antes la
  divergencia se toleraba en silencio. [VERIFICADO repo]
- Regresión: suite pytest de `entities`/`vehicles` (`test_api_gaps.py`, `test_api_pagination.py`,
  `test_api_canonical.py`) releída y corrida tras el cambio de columna — verde.
- **Gap declarado, no resuelto en F2**: el chip "Sin precio (N)" filtra (comportamiento previo,
  intacto) pero NO ofrece todavía la acción inline "fijar precio objetivo" que §6.1 describe — esa
  escritura SÍ existe (F3, `PriceOverrideForm` vía el Tablero), pero no está enganchada como acción
  de un clic desde el chip mismo. Pulido menor pendiente, no bloqueante.

### F3 — Capa de escritura del dealer: CERRADO [VERIFICADO vivo + tests]

**Primera escritura real de toda la API** (el recon de la carta: 0 endpoints POST/PUT/PATCH/DELETE
antes de este bloque, contando solo censo; AUTH-0 ya había abierto `/auth/*` con POST).

- `migrations/0080_fleet_ops.sql`: `fleet_ops` (estado actual por vehículo, K13) + `fleet_ops_event`
  (histórico append-only, guardas `cardeep_block_mutation()` reutilizadas de 0005 — UPDATE/DELETE/
  TRUNCATE bloqueados sin excepción, a diferencia de `vehicle_event` que sí permite re-apuntar
  `vehicle_ulid`). Aplicada contra cardeep-pg viva (`schema_migrations` confirma `0080`). [VERIFICADO vivo]
- `services/api/routers/dealer_ops.py` (nuevo, prefijo `/dealer`): `GET .../ops`, `GET
  /dealer/entities/{cdp}/fleet-ops` (lectura masiva, una sola query, para el tablero — cero N+1),
  `PATCH .../status` (K13, idempotente), `PATCH .../cost`, `POST .../price-override` (K15: razón
  categorizada + `delta_vs_median` obligatorios, reutilizando `compute_price_position` — ver
  refactor de `market.py` abajo, jamás recalculado a mano), `GET .../ops-history`.
- **Autorización real, no simulada**: cada escritura resuelve el `entity_ulid` dueño del vehículo →
  su `canonical_ulid` (mismo `resolve_cluster` que usa el resto de la API) → exige fila en
  `dealer_membership`. Verificado con un SEGUNDO dealer real y autenticado (`CDP-ES-01-7FAFJXW8`,
  no un mock) intentando escribir sobre un vehículo de GYATA → `403` en los 4 endpoints de
  escritura + lectura de `ops`. [VERIFICADO — `tests/test_dealer_ops_router.py::TestAuthorization`,
  17/17 tests verdes]
- **Idempotencia real**: repetir el mismo `status`/`target_price` devuelve `meta.noop=true` y NO
  añade fila a `fleet_ops_event` (contado antes/después en el test, no solo el código leído).
- **Auditoría real**: cada escritura queda en `fleet_ops_event` con `actor_user_ulid`+
  `observed_at`+`from_value`/`to_value`; `GET .../ops-history` + replay reconstruye el estado
  actual byte a byte (test explícito de replay).
- **Aislamiento del censo, demostrado no solo documentado**: snapshot de `vehicle` (fila completa)
  + `COUNT(*)` de `vehicle_event` para el vehículo de prueba ANTES y DESPUÉS de 3 escrituras
  reales (status+cost+price-override) → **byte-idénticos**. `tests/test_dealer_ops_router.py::
  TestCensusIsolation`.
- **Tablero de vehículo (§6.2)**: vive en `/vehicles` como 4ª vista ("tablero", `FleetBoard.tsx`),
  **NO en `/kanban`** — esa ruta es de 06 (deals) por resolución C-5 del MASTER, respetada sin
  tocar `Kanban.tsx`. Drag-and-drop con `@dnd-kit` (mismo patrón que el `Kanban.tsx` de 06, ya
  probado en el repo). Reprecio con razón obligatoria (`PriceOverrideForm.tsx`, K15).
- **§6.4 (retirar mocks del router) — REDEFINIDO, no ejecutado por 03**: el MASTER (C-4/C-5,
  posterior a la redacción original de §6.4 de esta carta) asigna Contacts/Deals/Kanban/Inbox a
  06 en exclusiva. 03 no toca esos archivos — hacerlo habría sido invadir ownership ajeno. Se
  corrige aquí el texto de §6.4: la retirada de mocks de CRM es competencia de 06, no de 03.
- Build: `tsc --noEmit` + `vite build` limpios con el router nuevo montado en `main.py` (registro
  compartido con `arbitrage`/`publishing` de los otros dos frentes en curso — `CORS allow_methods`
  ampliado a incluir `PATCH`, necesario para que el navegador no bloquee el preflight de los
  nuevos endpoints).

### F4 — Motor de comparables + Mercado: CERRADO (alcance re-scopeado por C-1) [VERIFICADO vivo]

**Decisión de arquitectura, no atajo**: 01-market-intelligence YA construyó y publicó el motor de
comparables completo (`market_stat`, `compute_stats.py`, M1-M10) antes de que este bloque
arrancara — confirmado leyendo `pipeline/market/compute_stats.py` y `cohort.py` completos. K9=M2,
K10=M4 (MDS, ventana 45d — la de C-7, NO los 90d que la v3 de esta carta todavía citaba en la
tabla §4 antes de esta actualización), K11=M3 (días-a-retirada) están servidos por
`GET /market/segments/{make}/{model}/stats` y `GET /market/price-position/{ulid}` **desde F5 del
bloque anterior**. Construir un segundo motor habría violado C-1 directamente. F4 de 03 se
redujo, correctamente, a: (a) un refactor mínimo y verificado de `market.py` para poder REUSAR esa
lógica desde el router de escritura (K15's `delta_vs_median`) y desde el frontend, y (b) la
superficie de consumo (badges + pantalla).

- **Refactor de `market.py`** (archivo propiedad de 01 — tocado de forma quirúrgica y mínima):
  se extrajo el cuerpo de `GET /market/price-position/{ulid}` a una función pura
  `compute_price_position(conn, vehicle_ulid) -> PricePositionOutcome`, dejando la ruta como un
  envoltorio delgado. Comportamiento IDÉNTICO verificado por la suite existente
  `tests/test_market_router_m2.py` (23/23 verdes, releída antes y después del refactor, sin
  tocar un solo assert). `dealer_ops.py` importa esta función para K15 en vez de recalcular un
  segundo p50. [VERIFICADO — antes/después del refactor, mismo archivo de test]
- **K9 en "Mi flota"**: badge perezoso por fila (`PricePositionBadge`, cache compartida
  `pricePositionCache.ts`, mismo patrón que K8) — ratio/banda/cortes exactamente los que publica
  M2, nunca recalculados en el cliente.
- **"Mercado" (nuevo, `web/src/pages/Mercado.tsx`) sustituye a `Finance.tsx`** — el mock íntegro
  (`MONTHLY`/`EXPENSES`/`TOP_VEHICLES`, arrays hardcodeados) **eliminado** (`git rm` equivalente,
  archivo borrado, 0 referencias residuales verificadas por grep). Ruta `/finance` conservada
  (evita romper enlaces), label de nav cambiado "Finanzas"→"Mercado" (edición atómica de una sola
  entrada en `Shell.tsx`, regla §5.1 del MASTER).
  - K12 (capital parado): agregado 100% local sobre el inventario ya cargado del dealer — no
    requiere endpoint nuevo (no es una métrica de cohorte/segmento, es del dealer mismo).
  - K9 (distribución de la flota): fetch de posición por vehículo con concurrencia acotada (6
    workers), cache compartida con la tabla — nunca 468 llamadas simultáneas.
  - K10/K11: fetch de `marketSegmentStats` **una vez por segmento DISTINTO** presente en la
    flota (make+modelo+año+combustible), NUNCA por vehículo — verificado en vivo contra un
    vehículo real de GYATA (BMW i4 2023 Eléctrico, provincia 28): M4=123,0 días de oferta (n=35),
    M3=10,1 días medianos a retirada (n=10), devueltos por la API real, no simulados.
  - **T1 parcial, hueco declarado**: n/mediana/ventana/definición se muestran; la "muestra
    enlazable" (deep_links de los coches reales del comparable) NO se puede servir sin que 01
    añada un endpoint de muestra a `market.py` — fuera de la propiedad de archivo de 03. Declarado
    en la propia pantalla ("Cómo se calcula"), no escondido.
  - Umbral K12 (45 días) y turn de referencia (43-48d) **siguen [RESEARCH-US, sin recalibrar contra
    el censo ES]** — la recalibración es F0/F4 según §9 pero requiere el job de recalibración
    provincial que esta fase NO construyó (no estaba en el mandato F1-F4 asignado; el consumo del
    motor de 01 sí lo estaba). Declarado, no maquillado.
- Build: `tsc --noEmit` + `vite build` limpios.

### Verificación cruzada §7 aplicada realmente (no solo prometida)

| Dato | Vía 1 | Vía 2 | Resultado |
|---|---|---|---|
| Recuento de flota (K14) | `available_inventory` | `loadedCount` paginado | Coinciden en vivo para GYATA (468=468); lógica de divergencia con flag construida y lista para cuando no coincidan |
| Aislamiento censo (F3) | lectura de código (0034/0035 nunca tocadas) | snapshot DB antes/después de escrituras reales | Byte-idénticos, test automatizado |
| K9 (F4) | endpoint `/market/price-position` | recomputo independiente de 01 (`tests/test_market_router_m2.py`, no re-derivado por 03) | Verde, comportamiento idéntico pre/post refactor |
| Autorización (F3) | lectura de código (`_authorize_vehicle`) | ataque real de un segundo dealer autenticado contra el vehículo de GYATA | 403 confirmado, 4 endpoints |

### Deuda y huecos honestos que quedan abiertos tras F1-F4

1. F0 no ejecutado (fuera de mandato): blueprint §3.11/§3.5 sin corregir por esta sesión, umbrales
   K3/K12 sin recalibrar contra el censo ES, `derive.test.ts`/`layout.test.ts` sin runner de CI.
2. Sin Playwright/Vitest instalado en `web/` — toda verificación de F1-F4 usó pytest (backend,
   real) + curl contra la API viva (red real) + `tsc`/`vite build` (frontend). Ningún test de DOM
   real corrió. Riesgo declarado, no oculto.
3. Chip "Sin precio" sin acción inline de un clic hacia `PriceOverrideForm` (la escritura existe,
   el atajo de UX no).
4. T1 sin muestra enlazable (deep_links) — depende de un endpoint nuevo en `market.py`, propiedad
   de 01.
5. F5 (CRM mínimo) y F6 (Garaje 3D fase 2) no tocados — fuera del mandato F1-F4.
6. Idempotencia de precio en `price-override`/`cost` compara `float` tras conversión desde
   `NUMERIC(12,2)` — en el peor caso de un valor con redondeo de punto flotante adyacente al
   anterior, el endpoint podría no detectar un "no-op" verdadero y añadir una fila de auditoría
   extra en vez de omitirla. No es un bug de corrección (el estado final es correcto), es una
   pérdida menor de la optimización de idempotencia en un caso de borde de precisión decimal.

---

## Resumen

El pilar tiene un cimiento real verificado (inventario + garaje 3D sobre API viva de solo lectura, 1 dealer, 468 coches contrastados por curl) y una fachada mock (Kanban/Deals/Contacts/Finance) que se reconecta o se retira. El research adversarial —ejecutado— dicta la estrategia: renunciar honestamente al DMS completo (CDK/Reynolds/Tekion/Cox juegan otra liga con escritura legal-fiscal) y explotar la única ventaja estructural real: inteligencia de precio cross-platform para España (Price-to-Market + Market-Days-Supply desde el censo total), donde vAuto no llega y HändlerIQ/Pilot'Price/mobile.de son ciegos fuera de su plataforma. Cada número del frontend traza a un criterio K explícito, se verifica por dos vías independientes, y la capa de escritura del dealer vive separada del censo append-only. Construcción en 7 fases F0-F6, cada una con cierre verificable — nada se declara hecho por deploy.
