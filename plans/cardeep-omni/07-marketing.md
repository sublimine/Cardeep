# Carta de sub-proyecto — Pilar 07: Marketing ("Marketing de otro nivel")

> Programa: cardeep-omni · Clave: `07-marketing` · Fecha: 2026-07-17
> Fase: SYNTHESIS (arquitectura). Este documento es la fuente de verdad del pilar
> hasta que una fase de ejecución lo enmiende con evidencia nueva.
> Doctrina aplicada: antialucinación tolerancia cero — cada afirmación lleva
> [VERIFICADO] (leída en código/doc real, con archivo:línea, re-verificada 2026-07-17)
> o [RESEARCH] (extraída de la investigación competitiva adversarial, fuente externa)
> o [ASUMIDO] (suposición declarada, jamás disfrazada de certeza).
> Pilar NET-NEW **a nivel de código y esquema**: cero páginas, routers, tablas o servicios de
> marketing implementados (§1). A nivel de planificación, la suite completa `00`–`09` de
> cardeep-omni quedó escrita en esta misma campaña de síntesis (verificado por `ls` 2026-07-17);
> esta carta está coordinada con sus hermanas — fronteras selladas en §3.3 y F6 con
> `05-multiposting.md` (publicación saliente) y `06-unified-crm-chat.md` (inbox/CRM).
> Re-auditoría integral de las citas archivo:línea de esta carta: 2026-07-17 (segunda pasada,
> lecturas directas del working tree — todas las citas confirmadas).

---

## 1. Estado actual

Veredicto en una frase: **no existe ningún pilar de marketing en Cardeep** — ni página dedicada, ni servicio backend, ni esquema de datos. Todo lo que hoy toca el tema es (a) reporting read-only 100% mock sobre el negocio del dealer, o (b) generadores de contenido **falsificados en el cliente** que simulan capacidades de IA inexistentes.

### 1.1 Superficie de producto: mock y falsificación [VERIFICADO archivo por archivo]

- `web/src/pages/Analitica.tsx` (515 líneas) — única página con la etiqueta "marketing" (L463: *"Ventas, marketing, stock y canales — una sola vista."*). Todos sus datos son constantes hardcodeadas: `SALES_DATA` (L21-42), `KPI_VALUES` (L46-50), `TOP_MODELS` (L52-58), `STOCK_SEGMENTS` (L60-66), `CHANNELS` (L68-73: coches.net/AutoScout24/Web propia/Particular con leads/ventas/CPL fijos), `FUNNEL_STAGES` (L75-80), `REGION_SALES` (L82-88). Cero `fetch`/import de `../api/cardeep`. El propio comentario L14-15 confiesa el marco: *"Analítica = datos propios del dealer (05-MONETIZATION-MAP.md)"*. [VERIFICADO]
- `web/src/pages/Assistant.tsx` (470 líneas) — lo más cercano a marketing de contenidos, y es **atrezzo puro**: `botReply()` (L78-118) es regex + interpolación de strings; el modo `listing` (L95-102) rellena una plantilla fija en español ("…¡Oportunidad única al mejor precio del mercado!"); el modo `image` (L112-115) hace `Math.floor(Math.random() * CAR_IMAGES.length)` sobre 5 URLs de Unsplash hardcodeadas (`CAR_IMAGES`, L70-76) ignorando el texto del usuario, y presenta el resultado como "Imagen generada". Latencia de IA simulada con `setTimeout`. **Esto es una falsificación visual de una capacidad que no existe** — viola la doctrina antialucinación del propio proyecto aplicada al producto. [VERIFICADO]
- `web/src/pages/Inbox.tsx` — modela conversaciones multi-plataforma (`sourcePlatform: 'mobile.de'|'autoscout24'|'manual'`) pero renderiza siempre `MOCK_CONVS` (4 conversaciones hardcodeadas, L14-19) vía el fallback `data?.conversations ?? MOCK_CONVS` (L88-89). `web/src/hooks/useInbox.ts` (L16-23) pide `/inbox` a través de `web/src/api/client.ts` — el cliente LEGACY (`fetch('/api/v1'+path)` con Bearer, `client.ts:76`) que el propio `cardeep.ts:3-4` declara REEMPLAZADO. El endpoint `/inbox` **no existe** en el backend real. El reply lleva `send_via: 'email'` hardcodeado (`useInbox.ts:34`) sin proveedor detrás. [VERIFICADO]
- `portal/app/marketing.html` (3.728 líneas, `wc -l` 2026-07-17) — pantalla suelta de la plantilla de terceros TailAdmin, nunca portada a la SPA. `plans/frontend-definitivo/UNIFICATION.md` documenta la decisión de absorberla como vistas de informe en Dashboard/Analítica. No hay `Marketing.tsx` en `web/src/pages/` (verificado por `ls`). [VERIFICADO]

### 1.2 Backend real: cero marketing, pero la MATERIA PRIMA existe [VERIFICADO]

- Routers reales (`grep @router` 2026-07-17): `vehicles.py` (2 endpoints), `entities.py` (4, incl. `/canonical`), `geo.py` (6), `ops.py` (4), `platforms.py` (2, incl. `/vehicles/{ulid}/platforms`). **Total 18 endpoints — ninguno de campañas, leads, email, feeds, SEO ni publicación.** [VERIFICADO]
- Cliente web vivo `web/src/api/cardeep.ts` (L161-174): exactamente 8 métodos (`stats`, `geoSeal`, `provinceEntities`, `entity`, `entityInventory`, `entityDelta`, `vehicleHistory`, `vehiclePlatforms`) — todos de inteligencia de mercado. [VERIFICADO]
- `migrations/`: ninguna tabla de campaign/lead/ad_spend orientada al dealer. La única "campaign" es `country_campaign` (`0067_country_campaign.sql:39`) — ledger interno del orquestador de países del pipeline, sin relación con marketing. [VERIFICADO]
- **La materia prima sí está**: `vehicle` (`0003_vehicles_events.sql:4-26` — `deep_link`, `title`, `make`, `model`, `year`, `km`, `price NUMERIC(12,2)`, `currency`, `fuel`, `transmission`, `photo_url`, `photo_hash`, `vin_ref`, `status`, `first_seen`/`last_seen`), `vehicle_event` append-only (`0003:33-42` — NEW/GONE/PRICE_CHANGE/PHOTO_CHANGE/KM_CHANGE), `platform_listing` (`0009_platform_listing.sql:16-30` — arista coche↔plataforma con `listing_url`, `platform_price`, `listing_fingerprint`, `status`, `removed_at`), `vehicle_cluster`/`vehicle_cluster_run` (`0023`, dedup físico cross-plataforma), eje geo completo (`0001`: `geo_province`/`geo_comarca`/`geo_municipality`). [VERIFICADO]

### 1.3 Contradicción documental activa [VERIFICADO]

`docs/frontend/00-PLATFORM-BLUEPRINT-E2E.md` §3.10 (L277-289) describe "Cross-posting + Inbox unificado `/pro/publish` `/pro/inbox`" como "[NOW estado / NEAR motor]" y afirma que `publish_job` + `platform_credentials` + `inbox_thread/message` están en "migraciones 0033-0035". **FALSO**: las migraciones reales `0033_evict.sql` (capacity_ledger/audit_eviction), `0034_truncate_guards.sql` y `0035_append_only_row_guards.sql` son guardas de integridad del pipeline — cero relación con publicación o mensajería (verificado por `ls`+grep de CREATE TABLE). Las rutas `/pro/publish`/`/pro/inbox` no existen en `web/src/App.tsx` (rutas reales L60-101) y no hay `PublishPanel` en `web/src`. **Ese §3.10 queda DESAUTORIZADO como base de cita; esta carta lo supersede para este pilar.**

### 1.4 Huecos estructurales (recon, confirmados)

1. Sin gestión de campañas (Google/Meta/portales verticales): creación, presupuesto, targeting — nada.
2. Sin SEO/estructura de ficha: ni schema.org VehicleListing, ni auditoría de calidad de anuncio — pese a que el dato de mercado para hacerlo mejor que nadie YA existe (`vehiclePlatforms`, `geoSeal`).
3. Sin motor real de contenido (copy/imagen): el Assistant es simulación cliente-side.
4. Sin cross-posting real: ni `publish_job`, ni OAuth, ni cola — solo observación pasiva vía scraping. **Territorio del pilar hermano `05-multiposting.md`** (carta propia, misma campaña), no de este.
5. Sin inbox real: `/inbox` no existe en backend; mock permanente. **Territorio del pilar hermano `06-unified-crm-chat.md`** (su F3 erradica el patrón `?? MOCK_*`), no de este.
6. Sin email/SMS marketing, redes sociales, retargeting/píxeles, ni atribución/ROI real (el CPL de Analítica es un número inventado).
7. Sin documento de planificación previo — esta carta parte de cero; la única decisión heredada que respetar es la de `plans/frontend-definitivo/05-MONETIZATION-MAP.md` (L10-12: lo del dealer = gratis; lo del MERCADO = se vende en Capa 0/1/2 → Starter/Scale/Enterprise; y L69-72: la Analítica sobre datos propios es gratis, benchmarks de sector pasan a Capa 1). [VERIFICADO]

---

## 2. Investigación competitiva/adversarial

RESEARCH ejecutado sobre 19 referencias. El hallazgo estructural: el pilar ganador en 2026 no es un producto sino **cuatro capas** que la ola de M&A está consolidando bajo un mismo techo — (1) distribución/syndication, (2) CDP de demanda de primera parte, (3) generación de contenido con IA, (4) mensajería/inbox unificado. Prueba: Cox absorbió Fullpath (abril 2026) para unir HomeNet+vAuto+Dealer.com con el CDP; Impel pagó >$100M por Outsell; Reynolds fusionó Gubagoo+Fullpath en "Curator". Nadie gana compitiendo en una sola capa. [RESEARCH]

Criterios EXACTOS extraídos (no genéricos) — estos son los listones que cualquier cosa que construyamos debe medir:

| Referencia | Criterio exacto | [RESEARCH] |
|---|---|---|
| **Google Vehicle Ads** (feed spec, developers.google.com/vehicle-listings) | Campos obligatorios: `vin` (válido NHTSA), `store_code`, `dealership_name`, `dealership_address`, `price` (ISO 4217), `condition` (new/used), `make`, `model`, `trim` (obligatorio cuando existe), `year` (YYYY), `mileage` (entero+unidad, solo usados). Refresco recomendado cada 4h, mínimo diario. Imágenes ≥800×600px sin overlays/watermarks/logos. **El precio del feed debe coincidir EXACTAMENTE con el de la landing del dealer o hay rechazo de política.** | ✓ |
| **Meta Automotive Inventory Ads** | Base: `id`/`title`/`price`/`currency`/`availability`/`condition`/URL/`image_link` + auto: `state_of_vehicle`, `make`, `model`, `body_style`, `vin`, `mileage`, `year`, `exterior_color`, `transmission`, `fuel_type`. Formatos CSV/TSV/XML, cabeceras en inglés. | ✓ |
| **schema.org / rich result Google** | Jerarquía Thing>Product>Vehicle>Car; `Offer` envuelve `Car` vía `itemOffered`. Mínimo del rich result "Vehicle Listing": `itemCondition` + `mileageFromOdometer`; recomendados: VIN/brand/model/vehicleModelDate/fuelType/driveWheelConfiguration/numberOfDoors/vehicleTransmission/color/vehicleEngine. | ✓ |
| **CarStory (CDK)** | Un VIN-decoder estándar solo describe ~65% de un vehículo de forma fiable; CarStory rompe el techo cruzando contra un "VIN Vault" de +200M VINs vendidos — completa la descripción con datos de venta real, no specs de fábrica. | ✓ |
| **vAuto Provision / ProfitTime GPS** | Repricing CONTINUO por oferta/demanda local en vivo; cada unidad de stock tratada como inversión con score de potencial de beneficio, no solo días-en-lote. | ✓ |
| **Fullpath CDP** | Resolución de identidad: de media el 10% de los datos de clientes de un dealer están duplicados, hasta 42% en extremos; fusiona CRM+DMS+web+llamadas+Ads en un perfil único. | ✓ |
| **Podium "Jerry"** | SLA cuantificado: responde leads (texto/llamada/webchat/social/email) en **36 segundos de media**, con sync bidireccional real al CRM. | ✓ |
| **automotiveMastermind** | Behavior Prediction Score 0-100 por prospecto; impacto declarado: hasta 15 ventas de conquista incrementales/mes, hasta 15% lift de retención por fin de leasing. | ✓ |
| **PureCars Signal Pro** | Grafo de identidad cross-device (IP+teléfono) que ata ~80% de las compras al touchpoint exacto — atribución falseable, frente al 0% real del mock de Analitica.tsx. | ✓ |
| **HomeNet (Cox)** | Syndication a miles de destinos (Autotrader, Cars.com, CarGurus, Facebook Marketplace, Walmart.com…) vía normalización de feed por sitio — infraestructura de formato + relación comercial. | ✓ |
| **Spyne** | Pipeline fotográfico 100% automatizado: app guía ángulos → segmentación IA → fondo de estudio + sombra sintética → spin 360. | ✓ |
| **coches.net PRO (Adevinta)** | Los packs monetizan la CADENCIA de reposicionamiento (Advance = refresco cada 6 días, Expert = cada 3 + Demand Radar), no el volumen bruto de anuncios. | ✓ |
| **AutoScout24 AutoMatch** | Reenvío algorítmico de consultas C2C a dealers cercanos con stock similar (uplift declarado "hasta 15% más leads") + "downtime forecast": predicción de días-hasta-venta por anuncio. | ✓ |
| **Shift Digital** | Moat de PROCESO: gestionar el cumplimiento de programas co-op de los OEM como condición para liberar fondos de marketing — regulatorio, no de dato. | ✓ |

Lectura adversarial honesta: de las 4 capas, **tres son estructuralmente inalcanzables** para los activos actuales de Cardeep — distribución (exige contratos de feed con portales; y el flujo de Cardeep es el OPUESTO: LEE de coches.net/AutoScout24, no ESCRIBE hacia ellos), CDP de demanda (Fullpath unifica datos del CLIENTE del dealer; el censo de Cardeep es del lado de la OFERTA — clases de datos ortogonales; el VAM no resuelve identidad de comprador), y mensajería (exige OAuth con plataformas — cero relación con censo/delta/VAM). La ÚNICA cabeza de puente real está en la capa 3 (contenido/feed) cruzada con el censo. [RESEARCH + VERIFICADO contra el código en §1]

---

## 3. Objetivo Cardeep para este pilar — y el límite honesto

### 3.1 La ventaja estructural real (única, y sin explotar)

El censo cross-plataforma dedupado + VAM es un insumo de la MISMA naturaleza que el "VIN Vault" de CarStory (histórico de mercado que completa la descripción más allá del VIN-decode) — y potencialmente superior en España, porque:
1. Es **LIVE** (delta `vehicle_event` en vivo), no histórico estático. [VERIFICADO que el mecanismo existe: `0003:33-42`]
2. Es **cross-plataforma dedupado** (`vehicle_cluster`, `platform_listing.listing_fingerprint`) — CarStory opera sobre un solo origen. [VERIFICADO `0009:24`, `0023`]
3. Lleva un modelo de valoración verificado encima (VAM, sello geo `v_province_seal` servido por `/geo/seal`). [VERIFICADO `geo.py:105`]
4. **El trabajo de normalización que exige el feed spec de Google/Meta (vin, make, model, year, mileage, price, condition) es, campo por campo, el que la tabla `vehicle` ya computa para el censo** (`0003:9-22`) — el coste marginal de un feed compliant es bajo. [VERIFICADO]

### 3.2 Objetivo (secuenciado por honestidad de activos)

**Objetivo A — "El anuncio perfecto, con pruebas" (cabeza de puente, defendible):** el mejor auditor + generador de anuncios de coche de España, donde cada afirmación del anuncio está anclada en el censo verificado. Ningún competidor local puede escribir *"un 6% por debajo de la mediana de 23 comparables verificados en tu provincia, presente en 2 de 4 plataformas relevantes"* — Cardeep sí, con provenance. Aquí **superamos** a la referencia (CarStory) en grounding local; es el mismo principio antialucinación del proyecto convertido en producto.

**Objetivo B — "Radar de canales real" (sustituir el atrezzo por observación verificada):** el panel CHANNELS falso de Analítica se convierte en distribución OBSERVADA real: en qué plataformas está cada coche del dealer (`platform_listing`), divergencia de precio por plataforma (violación directa de la política de Google), cobertura de canal, y días-hasta-GONE por plataforma (nuestro análogo del "downtime forecast" de AutoScout24, calculado sobre eventos reales). Esto es inteligencia pasiva — no requiere ni un solo contrato.

**Objetivo C — feeds listos para gastar:** exportación de feeds compliant (Google Vehicle Ads CSV, Meta AIA CSV, schema.org JSON-LD) generados del inventario propio del dealer, validados contra el spec exacto de §2. El dealer los conecta él mismo a Merchant Center/Commerce Manager — Cardeep no gestiona el gasto publicitario.

### 3.3 Límite honesto (sin maquillaje)

- **NO construimos** (en este pilar, con estos activos): gestión de campañas con presupuesto en Google/Meta, CDP de demanda, email/SMS marketing, redes sociales, retargeting/píxeles, ni atribución de ROI real. Cada una exige activos (contratos, OAuth, datos de demanda del dealer) que Cardeep no posee. Prometerlas hoy sería mentir.
- **Cross-posting real e inbox real NO son de este pilar**: son territorio de las cartas hermanas `05-multiposting.md` (publicación saliente, incluida su propia evaluación de viabilidad ToS/API por portal) y `06-unified-crm-chat.md` (inbox/canales, email primero, WhatsApp gateado a gasto). Este pilar los CONSUME cuando existan (F6 = integración, no construcción) y jamás los simula con UI fake mientras tanto.
- El pilar completo tal como lo definen Cox/Impel/Reynolds NO es alcanzable con el censo — se declara y punto. Lo alcanzable y superior es la sub-capa contenido/feed/observación con grounding verificado.
- Conciliación con `05-MONETIZATION-MAP.md` [VERIFICADO L10-19]: la auditoría de anuncio y el radar de canales usan datos del MERCADO → **Capa 1 (Scale)** con teaser gratis; el feed export usa datos PROPIOS del dealer → gratis en generación básica, validación cruzada contra mercado (divergencia de precio) = Capa 1; alertas proactivas de divergencia/estancamiento = Capa 2 (Enterprise).

---

## 4. Criterios de evaluación CONCRETOS (cada número del frontend se traza aquí)

Regla dura: **ningún número, badge o sección del frontend puede existir sin fila en esta tabla.** Nada aleatorio, nada inventado. Si el denominador no alcanza el mínimo, la UI muestra "sin datos suficientes (N=x)" — nunca un número fabricado.

### C1 — Puntuación de anuncio (0-100), determinista

Suma ponderada de checks binarios/graduales sobre `vehicle` + `platform_listing`, derivados 1:1 del feed spec de Google/Meta y del rich result de schema.org (§2):

| # | Check | Fuente | Puntos |
|---|---|---|---|
| c1 | `price` presente y > 0 | `vehicle.price` | 12 |
| c2 | `make` y `model` presentes | `vehicle.make/model` | 10 |
| c3 | `year` presente (YYYY válido) | `vehicle.year` | 8 |
| c4 | `km` presente (obligatorio en usados según Google) | `vehicle.km` | 10 |
| c5 | `vin_ref` presente (obligatorio en Google Vehicle Ads) | `vehicle.vin_ref` | 12 |
| c6 | `fuel` y `transmission` presentes (recomendados schema.org) | `vehicle.fuel/transmission` | 6 |
| c7 | Foto presente | `vehicle.photo_url IS NOT NULL` | 10 |
| c8 | Foto ≥800×600 (criterio Google exacto) | dimensiones reales de `photo_url` (HEAD/descarga, ver §7) | 8 |
| c9 | Título ≥ umbral de riqueza (make+model+year+1 atributo más) | parse determinista de `vehicle.title` | 6 |
| c10 | **Coherencia de precio cross-plataforma**: `platform_listing.platform_price` == `vehicle.price` en toda arista `status='listed'` | `0009:23` | 10 |
| c11 | Sin señal de estancamiento: sin PRICE_CHANGE a la baja repetido (≥2) en 30 días con status aún `available` | `vehicle_event` | 8 |

Total = 100. Cada check devuelve su evidencia (valor leído + query). El score se persiste con la lista de checks fallados, nunca solo el agregado.

### C2 — Posición de precio del anuncio (para grounding del copy y badge)

`price_position_pct = (vehicle.price − mediana(comparables)) / mediana(comparables) × 100`
- Comparables: `vehicle` con `status='available'`, mismo `make`+`model`, `year` ±1, `km` ±20%, misma `geo_province` (vía `entity.province_code`), **dedupados por `vehicle_cluster`** para no contar el mismo coche físico N veces. [VERIFICADO que cada pieza existe: `0003`, `0002:13-15` (`entity.province_code CHAR(2) REFERENCES geo_province(code)`, leído directo), `0023`]
- **Mínimo N=8 comparables**; si N<8 se amplía a provincias limítrofes y se declara el ámbito; si sigue N<8 → "sin comparables suficientes (N=x)". Jamás se muestra un % sin su N y su ámbito.
- Dependencia declarada: la capa estadística de mercado es territorio del pilar `01-market-intelligence` (su F por percentiles). Este pilar **consume** ese cómputo cuando exista; hasta entonces, C2 se implementa como query acotada al inventario del dealer + comparables (volumen pequeño), sin duplicar la capa de agregación general.

### C3 — Cobertura de canales (radar)

`coverage_pct(dealer) = distinct(vehicle con ≥1 platform_listing status='listed') / count(vehicle status='available') × 100` — por dealer y por plataforma. Fuente: `platform_listing` JOIN `vehicle`. Semáforo: ≥80% verde, 50-79% ámbar, <50% rojo (umbral de producto, ajustable; nunca aleatorio).

### C4 — Divergencia de precio por plataforma

Lista de aristas donde `platform_listing.platform_price IS NOT NULL AND platform_price <> vehicle.price` (status `listed`). Cada fila muestra: plataforma, precio propio, precio observado, Δ€ y Δ%, y `last_seen` de la observación. Etiqueta explícita: *"incumple la política de coincidencia exacta de precio de Google Vehicle Ads"* (criterio §2).

### C5 — Días-hasta-baja por plataforma (análogo "downtime forecast", versión honesta)

Para vehículos con evento GONE: `dias = fecha(GONE en vehicle_event) − vehicle.first_seen`. Agregado por plataforma (vía `platform_listing`) y por segmento make/model. Se publica la **mediana observada con su N**, no una "predicción" — no vendemos forecast sin modelo validado; cuando el pilar 01 entregue days-to-sell con backtest, este criterio se eleva a predictivo.

### C6 — Validez de feed

`feed_valid_pct = items que pasan TODOS los campos obligatorios del spec destino / items totales × 100`, por destino (Google/Meta/JSON-LD). Cada item inválido lista el campo exacto que falla y su criterio de §2. Un feed con <100% se puede descargar igualmente pero con el informe de fallos delante — sin maquillaje.

### C7 — Copy grounded (gate de afirmaciones)

Toda descripción generada (F5) lleva un `claims[]` adjunto: cada afirmación factual (precio relativo, km, nº de comparables, presencia en plataformas) mapeada a la query y valor que la respalda. **Una afirmación sin respaldo = generación rechazada.** (Patrón inspirado en la cadena claim→skeptic→verdict del stack de verificación existente — tablas `inquisition_claim`/`inquisition_skeptic`/`inquisition_verdict`, `0032_inquisition.sql` [VERIFICADO existencia por grep; detalle interno a releer en ejecución].)

---

## 5. Modelo de datos + almacenamiento backend

### 5.1 Se REUTILIZA (existente, verificado — cero duplicación)

| Activo | Dónde | Rol en este pilar |
|---|---|---|
| `vehicle` | `migrations/0003_vehicles_events.sql:4-26` | Fuente única de la ficha: los 11 checks de C1 y todos los campos del feed (C6) salen de aquí. |
| `vehicle_event` | `0003:33-42` | C5 (GONE), c11 (PRICE_CHANGE), frescura del feed. |
| `platform_listing` | `0009_platform_listing.sql:16-30` | C3 (cobertura), C4 (divergencia `platform_price`), enlaces `listing_url` reales. |
| `vehicle_cluster` / `vehicle_cluster_run` | `0023_vehicle_cluster.sql` | Dedup de comparables en C2 (no contar 3 veces el mismo coche físico). |
| `entity` + `geo_province`/`geo_municipality` | `0002_entities.sql`, `0001_geo.sql` | Ámbito geográfico de comparables (C2) y datos del dealer para el feed (`store_code`≈`cdp_code`, dirección). |
| `alert` | `0004_verification_health.sql:34` | Precedente/candidato para alertas Capa 2 (divergencia de precio, estancamiento). Releer su esquema en ejecución antes de extender; si su semántica es pipeline-only, se crea tabla propia. |
| `product_stats` (patrón) | `0055_product_stats.sql` | **Patrón a imitar** para caches precomputadas: tabla exacta refrescada off-request por scheduler, con `computed_at` expuesto. Las agregaciones C3/C5 por dealer siguen este molde, no cómputo en request. |
| API FastAPI viva | `services/api/routers/*` (18 endpoints verificados) | Los endpoints nuevos se añaden como router nuevo `marketing.py` junto a los 5 existentes, mismo envelope `{ok,data,error,meta}` (contrato visible en `web/src/api/cardeep.ts:9-14`). |
| Cliente web | `web/src/api/cardeep.ts` | Se EXTIENDE (nuevos métodos tipados). El cliente legacy `client.ts` NO se toca ni se usa. |
| `PremiumGate` | `web/src/components/PremiumGate.tsx` (props `feature/userPlan/what`, L8-21) | Gating Capa 1/2 según §3.3. |

### 5.2 Se CREA nuevo (nombres propuestos — NO existen hoy; migración adicional, aditiva y reversible como manda el estilo de `0003`/`0009`/`0055`)

| Tabla nueva | Contenido | Justificación |
|---|---|---|
| `listing_audit_run` | run de auditoría: `run_ulid`, `entity_ulid`, `started_at`, `finished_at`, `vehicles_audited`, `engine_version` | Auditar es un proceso versionado y re-ejecutable — mismo patrón run+resultado de `vehicle_cluster_run` (`0023`). |
| `listing_audit` | por vehículo: `run_ulid`, `vehicle_ulid`, `score SMALLINT`, `checks JSONB` (los 11 de C1 con evidencia), `computed_at` | Persistir score + evidencia; el frontend lee esto, jamás recalcula en cliente. |
| `feed_export` | `export_ulid`, `entity_ulid`, `target CHECK (target IN ('google_vehicle_ads','meta_aia','schema_org_jsonld'))`, `item_count`, `valid_count`, `invalid_report JSONB`, `content_hash`, `created_at` | Trazabilidad de cada feed generado (C6) + hash para verificación de integridad (§7). El fichero en sí se sirve/descarga, no se guarda en DB (doctrina de capacidad — cf. `capacity_ledger`, `0033_evict.sql`). |
| `adcopy_generation` | `gen_ulid`, `vehicle_ulid`, `input_snapshot JSONB` (datos del coche + comparables usados, con hash), `claims JSONB` (C7), `output_text`, `model_used`, `status CHECK (status IN ('grounded','rejected'))`, `created_at` | Cada copy con su provenance completo; lo rechazado también se persiste (auditoría del gate). |

Numeración de migración: la última real es `0072_vehicle_cluster_country_proof.sql` (verificado por `ls` 2026-07-17) → esta migración será **≥0073, a confirmar contra `ls migrations/` en el momento de ejecución** (otros pilares pueden aterrizar antes).

**Hueco conocido (declarado, no rellenado):** el volumen real de filas en `platform_listing` con `platform_price` no-nulo y la densidad de `vin_ref`/`photo_url` en `vehicle` NO se verificaron por SQL en esta síntesis (stack DB no consultado en esta fase). Son las dos primeras queries de F0 — determinan cuánta señal real tienen C4 y c5/c7-c8 desde el día uno.

### 5.3 Servicios

- `services/api/routers/marketing.py` (NUEVO): `GET /entities/{cdp}/listing-audit` · `GET /entities/{cdp}/channel-radar` · `GET /entities/{cdp}/feed/{target}` (descarga) · `POST /vehicles/{ulid}/adcopy` (F5).
- Job de cadencia (patrón `refresh_product_stats` citado en `0055:24-27`): refresco de `listing_audit` y agregados del radar off-request.

---

## 6. Especificación de pantalla/sección en el frontend

Nueva página `web/src/pages/Marketing.tsx`, ruta protegida `marketing` en `web/src/App.tsx` (bloque L78-99) + entrada en el nav de `web/src/layout/Shell.tsx`. En el lenguaje del dealer — un jefe de ventas de una compraventa de 40 coches en Alicante, no un "marketing manager" de SaaS:

**Cabecera** — *"Tus anuncios, auditados contra el mercado real"*. KPI fila: nota media de anuncio (C1, media del inventario), coches con precio incoherente entre plataformas (C4, contador), cobertura de canales (C3, %). Cada KPI con tooltip *"cómo se calcula"* enlazando el criterio.

**Bloque 1 — "Arregla estos primero"** (gratis, datos propios): lista de sus coches ordenada por score C1 ascendente. Cada fila: foto, título, score con desglose de checks fallados en lenguaje llano — *"Sin VIN: Google no te lo acepta"*, *"Foto pequeña (640×480): mínimo 800×600"*, *"En coches.net está a 18.900€ pero tú lo tienes a 19.400€ — Google rechaza el feed por esto"*. Botón "ver anuncio en la plataforma" → `platform_listing.listing_url` real (mandato deep-links).

**Bloque 2 — "Radar de canales"** (Capa 1, `PremiumGate feature="channel-radar"`): tabla por plataforma — coches tuyos visibles (C3), divergencias de precio (C4), mediana de días-hasta-baja de coches como los tuyos en esa plataforma con su N (C5). Teaser gratis: la fila agregada; el desglose por plataforma/modelo, tras el gate.

**Bloque 3 — "Feed listo para anunciarte"** (generación gratis; validación de mercado = Capa 1): tres tarjetas — Google Vehicle Ads, Meta, Datos estructurados (schema.org) — cada una con % de validez (C6), lista de coches excluidos y por qué campo exacto, y botón de descarga. Texto honesto: *"Cardeep genera el fichero; la campaña la creas y pagas tú en tu cuenta de Google/Meta."* Sin humo.

**Bloque 4 — "Descripción con pruebas"** (Capa 1): reemplaza el modo `listing` del Assistant. El dealer elige un coche de SU inventario (no texto libre); recibe el copy con las afirmaciones subrayadas y su fuente al pasar el ratón (*"−6% vs mediana: 23 comparables verificados, provincia de Alicante, hoy"* — C2/C7). Si no hay comparables suficientes, el copy se genera SIN afirmación de precio y lo dice.

**Demoliciones ligadas (misma autoridad de reestructuración):** (a) `Assistant.tsx` modo `image` — se ELIMINA (la etiqueta "Imagen generada" sobre Unsplash aleatorio es una mentira de producto); (b) `Assistant.tsx` modo `listing` — redirige al Bloque 4; (c) panel `CHANNELS` de `Analitica.tsx` (L68-73) — se sustituye por el dato real del radar o, mientras no exista, por un empty-state honesto; (d) `Inbox.tsx` fallback `?? MOCK_CONVS` (L89) — su erradicación es propiedad del pilar 06 (F3 de `06-unified-crm-chat.md`, regla "prohibido `?? MOCK_*`"); si al llegar la F0 de este pilar 06-F3 aún no ha aterrizado, este pilar lo retira él mismo con empty-state honesto y lo declara en el tracker de 06 — quien llegue primero lo mata, nadie lo hace dos veces.

---

## 7. Protocolo de verificación (2 vías independientes por dato mostrado)

Estándar antialucinación aplicado al producto: ningún dato llega al dealer sin confirmarse por dos caminos que no compartan el bug.

| Dato | Vía 1 (producción) | Vía 2 (independiente) |
|---|---|---|
| Score C1 | Motor de auditoría (Python, `listing_audit`) | Script verificador separado que recalcula los 11 checks con queries SQL directas escritas aparte (sin importar el módulo del motor) sobre una muestra aleatoria ≥100 vehículos/run; divergencia >0 = run en cuarentena. |
| Dimensiones de foto (c8) | Lectura de dimensiones al descargar `photo_url` en el job | Segunda medición con librería distinta (p. ej. Pillow vs parse de cabecera del formato) sobre la muestra; y verificación manual visual de 10 casos en la revisión de fase. |
| Posición de precio C2 | Query de comparables del endpoint | Recomputación por camino distinto: export CSV de los comparables del snapshot (`adcopy_generation.input_snapshot`) y mediana recalculada en un runner separado; además, spot-check humano de 5 casos abriendo los `deep_link` reales de los comparables. |
| Cobertura C3 / divergencia C4 | JOIN `platform_listing`×`vehicle` | Contraste contra el endpoint ya existente `/vehicles/{ulid}/platforms` (`platforms.py:89`) vehículo a vehículo en la muestra — dos rutas de código distintas hasta la misma verdad; y visita manual a N `listing_url` para confirmar precio observado vigente. |
| Días-hasta-baja C5 | Agregado sobre `vehicle_event` GONE | Re-derivación desde `platform_listing.removed_at`/`last_seen` (campo distinto, tabla distinta, `0009:27-28`); las dos distribuciones deben ser consistentes dentro de la ventana de cadencia del scraping — si no, se reporta la discrepancia, no se elige la bonita. |
| Validez de feed C6 | Validador propio (spec §2 codificado en tests) | Validador EXTERNO: subida del fichero de prueba a Google Merchant Center (diagnóstico de feed) / Rich Results Test de Google para el JSON-LD / debugger de feed de Meta. **El criterio de "válido" lo dicta la plataforma destino, no nuestro validador.** |
| Claims del copy C7 | Gate en generación (claims[] contra queries) | Test post-hoc automático: parser extrae todo numeral/afirmación del `output_text` y lo casa contra `claims[]`; numeral sin claim = `status='rejected'` retroactivo + alerta. Muestreo humano en cada revisión de fase. |
| Frescura | `computed_at` en cada cache (patrón `product_stats`) | El frontend MUESTRA la edad del dato ("calculado hace 3h") — el usuario final es la segunda línea de verificación, como en `0055:6-7`. |

Regla de fallo: si las dos vías divergen, el dato NO se muestra (se muestra el estado "en verificación") y se abre incidencia. Nunca gana la vía "que da mejor número".

---

## 8. Uso de LLM (doctrina "gasta con cabeza" del CLAUDE.md del repo)

| Tarea | Motor | Justificación |
|---|---|---|
| Checks C1 (presencia, formatos, coherencia de precio) | **SQL/Python puro, cero LLM** | Determinista al 100%. Usar un LLM aquí sería incompetencia. |
| Dimensiones/calidad básica de foto (c8) | **Librería de imagen, cero LLM** | Leer cabeceras es determinista. |
| Parse de riqueza de título (c9) y extracción de equipamiento desde `title` | **Regex/parser primero; LLM LOCAL/barato solo para el residuo** que el parser no cubra, en batch off-request, con salida validada contra vocabulario cerrado | Volumen alto (inventario del dealer completo), valor por item bajo → barato y masivo, nunca modelo caro. |
| Generación de feeds C6 | **Plantillas deterministas, cero LLM** | Un feed spec es un contrato: se cumple con código, no con probabilidad. |
| Redacción final del copy (F5) | **Modelo caro, SOLO aquí, y acotado**: bajo demanda (clic del dealer), un vehículo por vez, con TODOS los hechos ya resueltos por SQL e inyectados — el LLM solo redacta, no calcula ni recuerda nada | Es el único punto donde la calidad de lenguaje mueve valor. Cacheable por `(vehicle_ulid, hash(input_snapshot))`: si ni el coche ni sus comparables cambiaron, cero re-gasto. **Prohibido**: pasar el LLM caro en batch por el censo (2,3M coches) — el copy es solo del inventario propio del dealer que lo pide. |
| Gate de claims C7 | **Parser determinista** para casar numerales; LLM local barato opcional como segunda opinión de detección de afirmaciones no-numéricas | El veredicto de rechazo lo da el matching determinista, nunca el LLM. |
| Generación de imágenes | **NINGUNO.** Fuera de alcance | El coche real ya tiene foto real (`vehicle.photo_url`). Generar imágenes de coches que se venden como reales sería fabricar evidencia — exactamente lo que este pilar viene a demoler del Assistant. El pipeline tipo Spyne (fondo de estudio sobre foto REAL) queda anotado como futuro hardware-gated, no prometido. |

---

## 9. Fases de construcción (orden, con criterio de verificación por fase)

Autoridad asumida: reemplazar/reestructurar código existente donde haga falta (Assistant/Analitica/Inbox), siempre reversible y declarado.

**F0 — Recon SQL + demolición del atrezzo.**
Medir por SQL directo: densidad de `vin_ref`/`photo_url`/`platform_price`, nº de aristas `platform_listing` listed, nº de GONE con arista de plataforma (cierra el hueco de §5.2). Eliminar el modo `image` de `Assistant.tsx`; retirar `?? MOCK_CONVS` de `Inbox.tsx:89` con empty-state honesto; etiquetar el panel CHANNELS de Analítica como ilustrativo hasta su sustitución en F4.
*Verificación:* cifras del recon persistidas en `plans/cardeep-omni/07-notes/F0-RECON.md` con las queries literales; grep confirma cero `Math.random` en Assistant y cero `MOCK_CONVS` como fallback; `npm run build` verde; revisión visual de las 3 pantallas.

**F1 — Motor de auditoría de anuncio (C1) + migración + endpoint.**
Migración `≥0073` (`listing_audit_run`/`listing_audit`, aditiva+rollback documentado como en `0055`); motor Python con los 11 checks; job de cadencia patrón `refresh_product_stats`; `GET /entities/{cdp}/listing-audit` en router nuevo `marketing.py` con envelope estándar.
*Verificación:* TDD — tests de cada check con fixtures golden (coche perfecto=100, degradaciones conocidas=puntos exactos); protocolo §7 vía-2 (script recomputador independiente, muestra ≥100, divergencia 0); revisión de código real (code-review) antes de merge.

**F2 — Comparables y posición de precio (C2), coordinado con pilar 01.**
Si la capa estadística de 01 ya existe: consumirla. Si no: query acotada al inventario del dealer (mediana + N + ámbito), sin construir la capa general aquí (se declara la deuda y el punto de sustitución).
*Verificación:* recomputación por export CSV independiente (§7); spot-check humano de 5 casos con `deep_link` abiertos; test del umbral N<8 → respuesta "sin comparables suficientes", jamás número.

**F3 — Feeds C6 (Google/Meta/JSON-LD) + `feed_export`.**
Plantillas deterministas desde `vehicle`+`entity`; validador propio codificando §2 campo a campo; endpoint de descarga.
*Verificación:* suite de tests campo-por-campo contra el spec; **validación externa obligatoria**: JSON-LD por Rich Results Test, CSV por diagnóstico de Merchant Center/Meta sobre feed de prueba — el pase externo es el criterio, no el interno; `invalid_report` legible verificado a mano sobre 10 coches con defectos reales de F0.

**F4 — Frontend `Marketing.tsx` + sustitución del CHANNELS mock.**
Página de §6 con bloques 1-3 cableados a los endpoints reales vía `cardeep.ts` extendido; `PremiumGate` según §3.3; panel CHANNELS de Analítica sustituido por el radar real.
*Verificación:* grep = cero arrays de datos hardcodeados en `Marketing.tsx`; cada número de la pantalla trazado a su criterio C* en la revisión (checklist uno a uno); Playwright screenshot en 320/768/1440; frescura (`computed_at`) visible; build+lint verdes.

**F5 — Copy grounded (C7) + `adcopy_generation`.**
Pipeline: SQL resuelve hechos → snapshot+claims → LLM caro redacta → gate determinista casa numerales → `grounded` o `rejected`. Bloque 4 de la UI; el modo `listing` del Assistant redirige aquí.
*Verificación:* suite adversarial — inputs con datos ausentes deben producir copy SIN la afirmación correspondiente; inyección de un claim falso en test debe dar `rejected`; muestreo humano de 20 generaciones; coste por generación medido y registrado (presupuesto declarado al owner antes de activar en producción — frontera de GASTO, requiere su OK).

**F6 — Integración con pilares 05/06 (consumo, no construcción).**
El spike de viabilidad de publicación (ToS/API por portal, GO/NO-GO del owner) pertenece al pilar 05; los canales de mensajería, al 06. Cuando 05 aterrice: el radar de canales (Bloque 2) enlaza estado OBSERVADO (este pilar) con estado PUBLICADO (05) por vehículo, y el feed C6 se ofrece como insumo del motor de publicación. Cuando 06 aterrice: los leads generados por campañas creadas con los feeds C6 se atribuyen en su CRM (primer paso hacia atribución real, hoy declarada inalcanzable en §3.3). La corrección oficial del blueprint §3.10 es propiedad del pilar 06 (su fase de saneamiento documental ya la incluye); este pilar solo verifica que quedó hecha — la deuda de §1.3 se salda una vez, no tres.
*Verificación:* revisión cruzada carta↔carta al cierre de cada pilar hermano (checklist de fronteras: cero tablas duplicadas, cero UI duplicada); grep del blueprint sin la cita falsa 0033-0035 tras el cierre de 06; enlace funcional radar↔publicación probado sobre un dealer real cuando ambos pilares estén vivos.

Regresión transversal: al cierre de cada fase, suite completa del repo verde + barrido de que ningún pilar hermano (01/03/08/09) consuma lo tocado.

---

## Resumen

El pilar 07 no existe hoy en ninguna capa: lo que aparenta marketing en Cardeep es mock (Analítica) o falsificación cliente-side (Assistant/Inbox), verificado archivo:línea. La investigación (19 referencias) demuestra que el pilar completo son 4 capas y que 3 (distribución, CDP de demanda, mensajería) son inalcanzables con los activos actuales — se declara sin maquillaje; distribución y mensajería quedan además en manos de los pilares hermanos 05/06, con fronteras selladas para no duplicar ni una tabla. La cabeza de puente real y defendible es una sola: contenido/feed/observación **anclados en el censo cross-plataforma dedupado + VAM**, que ningún competidor local tiene. Se construye en 7 fases (F0-F6): demoler el atrezzo, auditoría determinista de anuncio, posición de precio con N declarado, feeds compliant validados por la plataforma destino, radar de canales real, copy con gate de afirmaciones e integración con 05/06 — cada dato confirmado por 2 vías independientes antes de llegar al dealer.
