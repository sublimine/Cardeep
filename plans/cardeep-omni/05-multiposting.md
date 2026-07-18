# Carta de sub-proyecto — Pilar 05: Multipublicación automática de anuncios

> Programa: cardeep-omni · Clave: `05-multiposting` · Fecha: 2026-07-17
> Fase: **F0-F2 EJECUTADAS y CERRADAS (2026-07-18) — ver §10.** Frente A (estado de
> publicación, solo lectura) real y servido. F3-F7 (Frente B/C: auth-consumo, feeds, AS24,
> Radar, coches.net/Wallapop/Milanuncios) siguen SYNTHESIS — gated, no ejecutadas.
> Este documento es la fuente de verdad del pilar hasta que una fase de ejecución
> posterior lo enmiende con evidencia nueva.
> Doctrina aplicada: antialucinación tolerancia cero — cada afirmación lleva
> [VERIFICADO] (leída en código/DB/doc real, con archivo:línea) o [ASUMIDO]
> (declarada como suposición, jamás disfrazada de certeza).
> RECON base: 2026-07-16 (commit `7d494dc`); re-verificación selectiva de todas las
> citas archivo:línea de este documento: 2026-07-17 (lecturas directas del working tree).

---

## 1. Estado actual

**Veredicto en una frase [VERIFICADO, auditoría en 3 capas: graphify AST + vault + código crudo]:
CERO código de publicación saliente existe hoy.** Todo lo que existe apunta en la dirección
OPUESTA (cosecha INBOUND desde las plataformas hacia Cardeep), más una mención de diseño
aspiracional desalineada con el código real. Este pilar es **net-new al 100%**.

### 1.1 Base de datos — solo la arista inbound

- `migrations/0009_platform_listing.sql:16-30` — `platform_listing` es la ÚNICA tabla
  relacionada con plataformas. Modela membresía cruzada descubierta por la cosecha
  ("este coche, propiedad de un dealer vendedor, también aparece anunciado en la plataforma X"),
  no una acción del dealer. Columnas reales: `vehicle_ulid`, `platform_entity_ulid`,
  `listing_url`, `listing_ref`, `platform_price NUMERIC(12,2)`, `listing_fingerprint`,
  `status listing_status DEFAULT 'listed'`, `first_seen`, `last_seen`, `removed_at`.
  PK `(vehicle_ulid, platform_entity_ulid)`. Índice parcial por fingerprint (líneas 36-37). [VERIFICADO]
- No existe columna ni tabla de cola de publicación, credenciales de plataforma, ni job de
  publicación en ninguna de las **66 migraciones existentes** (`0001`→`0072_vehicle_cluster_country_proof.sql`,
  numeración con huecos — cifra canónica fijada en `00-MASTER.md` C-13, re-contada aquí por
  `ls migrations/*.sql | wc -l` 2026-07-17). [VERIFICADO]
  **Addendum F0 (2026-07-18, re-conteo en la ejecución de este documento):** la cifra "66" sigue
  siendo la correcta COMO CIERRE de Bloque 0 (C-13 ya la fijó bien; no se repite el error de "72").
  Pero el programa avanzó: `ls migrations/*.sql | wc -l` da hoy **72 archivos**, última
  `0078_dgt_corroboration.sql` — Bloque 1 consumió 0073-0078 (`0073_auth.sql`=AUTH-0,
  `0074_market_stat.sql`+`0077_dgt_transfer.sql`+`0078_dgt_corroboration.sql`=01-market-intelligence,
  `0075_lifetime_link.sql`=02-history-reports, `0076_adaptive_cadence.sql`=00-marketplace-engine).
  Consecuencia directa sobre §5.2 de este documento: la reserva original de esta carta
  (`0073_dealer_account`→`0076_feed_export`) **choca por completo** con lo anterior — exactamente
  el escenario que `00-MASTER.md` C-6 anticipa ("ninguna carta posee un número"). Ver corrección
  en §5.2.
- `graphify explain "platform_listing"` → degree=1: el nodo solo conecta con su propia
  migración; ningún módulo Python escribe outbound sobre él. [VERIFICADO en RECON]

### 1.2 API — 100% lectura

- `services/api/routers/platforms.py` expone exactamente **2 endpoints, ambos GET**:
  `/platforms/{cdp_code}/inventory` (línea 25, `RATE_EXPENSIVE` + caché) y
  `/vehicles/{vehicle_ulid}/platforms` (línea 89, `RATE_DEFAULT`). Cero POST/PUT/DELETE
  en el archivo completo (leído entero, 132 líneas). [VERIFICADO]
- `services/api/main.py:146-150` registra solo 5 routers: `ops`, `entities`, `geo`,
  `vehicles`, `platforms`. No existe router de publish/syndication/inbox/auth. [VERIFICADO]
- Grep repo-completo: cero ocurrencias de `inbox`, `publish_job`, `platform_credentials`
  en `services/` y `pipeline/`; cero archivos `auth*.py` en todo el repo. [VERIFICADO en RECON]

### 1.3 Autenticación — el prerrequisito duro NO existe

- El backend **no tiene sistema de auth de dealer/tenant en absoluto**: ni router, ni
  archivo, ni tabla `user`/`tenant`/`account` en las 66 migraciones existentes. [VERIFICADO en RECON,
  listado de routers re-verificado 2026-07-17: `entities.py, geo.py, ops.py, platforms.py, vehicles.py`]
- `web/src/auth/AuthContext.tsx:48` llama `GET /auth/me` y `:74` llama `POST /auth/login` —
  **endpoints que no existen en el backend real**. El frontend funciona hoy solo por el
  `DEV_BYPASS` visible en el mismo archivo (líneas 33-35). [VERIFICADO por lectura directa]

### 1.4 Frontend — plantilla CRM desconectada, no producto

- `web/src/App.tsx` monta un shell protegido con 20+ páginas (Kanban, Contacts, Deals,
  Inbox, Calendar, Finance, Invoices, Chat...) detrás de `ProtectedRoute`. [VERIFICADO en RECON]
- `web/src/pages/Inbox.tsx:14-19` — `MOCK_CONVS` hardcodeado con conversaciones de
  `'mobile.de'` (plataforma alemana, **fuera del alcance España** de Cardeep) y `'autoscout24'`;
  contactos ficticios ("Maria Santos", "Anna Weber"). [VERIFICADO por lectura directa]
- `web/src/hooks/useInbox.ts` apunta a `GET /inbox`, endpoint inexistente. [VERIFICADO]
- No existe `/pro/publish`, `/pro/inbox` real, `PublishPanel` ni `DealerShell` en todo
  `web/` (grep case-insensitive repo-completo, cero resultados). [VERIFICADO en RECON]

### 1.5 Deriva doc-vs-código — corregir ANTES de citar

- `docs/frontend/00-PLATFORM-BLUEPRINT-E2E.md:277-289` (§3.10 "Cross-posting + Inbox
  unificado") etiqueta el pilar `[NOW estado / NEAR motor]` y afirma que `publish_job` +
  `platform_credentials` + `inbox_thread/message` llegan con "migraciones 0033-0035".
  **Ambas afirmaciones están desalineadas con el código real** [VERIFICADO 2026-07-17]:
  1. La etiqueta "NOW estado" no tiene ningún endpoint/componente que la respalde (§1.2, §1.4).
  2. Los números 0033-0035 YA ESTÁN CONSUMIDOS por `0033_evict.sql`,
     `0034_truncate_guards.sql`, `0035_append_only_row_guards.sql` (listado re-verificado).
     **El próximo número libre real es `0073`.**
- La nota espejo `docs/second-brain/gf/3.10 Cross-posting...md` es extracto automático de
  graphify del mismo párrafo — NO es evidencia independiente. [VERIFICADO en RECON]
- La corrección de este documento es la primera tarea de F0 (§9).

### 1.6 Infraestructura adyacente reutilizable (construida para otra cosa)

- `pipeline/engine/tier1/browser.py:1-37` — `solve_challenge()` con Camoufox (default,
  MPL-2.0) / nodriver (opt-in, AGPL con warning de licencia explícito en el docstring);
  patrón cookie-reuse con pin de UA/TLS/IP. Hoy solo se usa en dirección LECTURA;
  adaptarlo a login+submit de formulario es técnicamente plausible pero [ASUMIDO] hasta
  probarlo, y con riesgo ToS declarado en §3. [VERIFICADO el módulo; ASUMIDA la adaptación]
- `pipeline/engine/governor.py:1-25` — token bucket por host asyncio-safe, nacido de la
  cicatriz real "138 dealers cayeron por throttling de AS24". Gobierna velocidad INBOUND;
  el patrón (no la instancia) es reutilizable para el rate-limit outbound. [VERIFICADO]
- `pipeline/platform/_core/contract.py:14-47` — `PlatformSpec` (dataclass frozen) modela
  identidad de plataforma con campo `requires_creds: bool = False` (línea 35) — pensado
  para cosecha, no para credenciales de publicación del dealer. [VERIFICADO]
- Cosechadores inbound existentes por plataforma objetivo: `coches_net_wholesale.py`,
  `wallapop_wholesale.py`, `milanuncios_wholesale.py` (graphify query, 704 nodos, todos
  inbound). Conocen la ESTRUCTURA de anuncio de cada portal — insumo para el motor de
  mapeo de campos de §5, aunque en dirección inversa. [VERIFICADO en RECON]

### 1.7 Huecos estructurales confirmados

1. Modelo de datos outbound: sin `publish_job`, sin credenciales, sin inbox real.
2. API outbound: cero endpoints de escritura hacia plataformas externas.
3. Auth dealer/tenant: inexistente — prerrequisito duro de todo el pilar.
4. Adaptador por plataforma: cero (ni API oficial ni automatización de navegador en escritura).
5. UI real: cero; `Inbox.tsx` es mock con datos fuera de alcance.
6. Motor de mapeo vehicle/entity → formato de anuncio de cada plataforma destino: cero.
7. Almacén seguro de credenciales + flujo de conexión: cero.
8. Rate-limit/anti-abuso outbound: cero (el governor actual es inbound).
9. Doc de visión §3.10 desalineado en 2 puntos verificados (§1.5).

---

## 2. Investigación competitiva/adversarial

RESEARCH ejecutado sobre 14 referencias. Criterios EXACTOS extraídos — no genéricos.
Hallazgo adversarial central: **el cuello de botella del pilar no es de ingeniería sino de
ACCESO de escritura** — de las 4 plataformas nombradas en el pilar, solo UNA tiene API de
escritura pública.

### 2.1 AutoScout24 / SMG Automotive — la única puerta abierta documentada

- Repo GitHub público `smg-automotive/autoscout24-api-specs` con OpenAPI versionado
  (`openapi.yaml`, `openapi-listing-distribution.yaml`, etc.) — la referencia de mayor
  fidelidad porque el schema es auditable, no marketing.
- **Cross-Listing API** — taxonomía exacta que cualquier integrador debe replicar:
  `BodyType` 44+ valores · `FuelType` 13 · `EmissionStandard` 17 (Euro 1-6 variantes) ·
  `EnergyLabel` A-G · `ConditionType` 5 (new/used/demonstration/oldtimer/pre-registered) ·
  `SellerType` (professional/private) · `EquipmentSearchAttribute` 60+ características.
  Identidad obligatoria: `vehicleIdentificationNumber`, `certificationNumber`, `sellerVehicleId`.
- **Listing Creation API** (`listing-creation.api.autoscout24.com`): **solo escritura** —
  sin endpoint de lectura pública. Consecuencia de ingeniería: verificar que el anuncio
  quedó vivo exige lógica propia de read-back (esto alimenta directamente el protocolo §7).

### 2.2 Google Vehicle Listings — el estándar de feed con semántica más dura

(developers.google.com/vehicle-listings, spec leída en el research)
- Campos obligatorios exactos: `vin` (válido según estándar NHTSA), `store_code`,
  `dealership_name`, `dealership_address`, `price` (ISO 4217), `condition` (new/used),
  `make`, `model`, `year` (YYYY), `trim`, `mileage`+unidad (solo usados).
- Semántica de **reemplazo TOTAL** en cada subida: todo vehículo/dealer ausente del feed
  se retira de Google en horas.
- **Circuit breaker anti-catástrofe**: si una subida reduciría el inventario >30% respecto
  a la versión anterior, esa versión NO se procesa. (Adoptamos este guard tal cual — §4.6, §7.)
- Cadencia recomendada: cada 4 horas; los datos caducan a los 3 días sin refresco.

### 2.3 Meta / Facebook Automotive Inventory Ads

- Feed CSV/TSV/XML(RSS/ATOM). Obligatorios: `vehicle_id`, `make`, `model`, `year`,
  `body_style`, `price`, `currency`, `condition`, `availability`, `image_link`.
  Recomendados: `vin`, `mileage`, `trim`. Descripción ≤ 5.000 caracteres.
- La falta de un campo obligatorio puede rechazar la subida COMPLETA o ignorar el ítem —
  la validación pre-envío es determinista y no negociable (§7, §8).

### 2.4 coches.net PRO — el líder español (fuente interna ya auditada)

(`plans/intel-audit/companies/coches-net.md` L100-109, releída en el research)
- Multipublicación a coches.net + Milanuncios + web propia + >40 portales; exportación
  XML/XLS; integración obligatoria de JATO Dynamics para specs/equipamiento.
- **CERO API pública.** Frase textual auditada: "único software que permite publicar en
  Coches.net". El acceso de escritura al líder español está CERRADO — solo vía su software
  PRO o integradores B2B homologados.
- **Cadencia de re-posicionamiento (bump) atada al tier**: cada 3 días (Pack Expert),
  cada 6 días (Pack Advance), mensual (Pack Reference). Lección: la multipublicación madura
  no es "publicar una vez", es republicar con cadencia calculada.
- **Price Radar** (todos los packs desde nov-2024): precio de mercado en tiempo real +
  desviación vs media + previsión de tiempo de venta + detección de "activos tóxicos",
  INLINE sobre el anuncio al publicar/gestionar. **Demand Radar** (solo Expert): rotación
  media + oferta existente + evolución oferta/demanda. **Patrón estructural clave: el líder
  NO separa "publicar" de "inteligencia de precio" — las fusiona en la misma pantalla.**

### 2.5 Hubs españoles de multipublicación (la vía indirecta)

- **Inventario.pro**: 18 años, >130.000 coches únicos/mes; traducción de formato universal
  (JSON/XML/CSV) al estándar de cada portal; batch hasta 4×/día para unos flujos y API de
  reserva **bidireccional en tiempo real** para otros (Wallapop). Pieza de ingeniería
  crítica: **deduplicación de reservas cross-canal** — cada reserva entrante por cualquier
  canal se refleja instantáneamente en el inventario central, para no vender dos veces el
  mismo coche físico publicado en N portales. Un multipublicador ingenuo no resuelve esto.
- **maxterauto**: envía/actualiza/elimina stock hacia Coches.net, Wallapop, Carwow.
  Hallazgo adversarial: su documentación técnica está gated tras login de desarrollador —
  sus claims de API **no son verificables independientemente** sin cuenta.
- **Dealcar.io**: todo-en-uno (CRM+stock+multipublicación+web+firma digital) para
  compraventas de 10-150 coches, con propagación sincronizada de precio y baja.
- **AutoPult** (DE): usa la API OFICIAL de AS24 para publicar en mobile.de/AS24/Kleinanzeigen —
  prueba de que la ruta API-oficial-AS24 es viable como producto comercial.

### 2.6 El mercado maduro (EE.UU.) y los estándares

- **HomeNet (Cox Automotive)**: la mayor red de sindicación de inventario de EE.UU.
  **Cox "Power of Three"/Bridge ID**: la multipublicación NO se vende como producto suelto
  sino como capa de un conglomerado verticalmente integrado (KBB valoración + vAuto pricing +
  HomeNet sindicación + VinSolutions CRM) con SSO compartido.
- **STAR** (starstandard.org): 36 BODs XML; en enero 2026 publicó su "Retail Automotive
  Domain Model" (JSON/OpenAPI) — **ni el mercado 10× más maduro tiene todavía un estándar
  único de sindicación**; el organismo sectorial sigue construyéndolo en 2026.
- **RESO Web API** (benchmark cross-vertical, inmobiliario): REST+OData+JSON, OAuth2,
  Data Dictionary canónico (`ListingKey`, `StandardStatus`, `ListPrice`), ~93% de ~500 MLS
  certificadas. Es la vara de lo que SÍ es un estándar resuelto — el automóvil no lo tiene.
- **ADF/XML**: los leads SÍ convergieron en formato abierto; la sindicación completa de
  anuncios, no. Cardeep no debe esperar a un estándar que no va a llegar a tiempo.

### 2.7 La capa "automática" de frontera que NADIE ofrece en España

- Merchandising con IA (CarCutter, Car Studio AI, autofox, Dealerslink AI): retoque/fondo
  por IA + descripciones generadas desde equipamiento, con ahorro reportado ~65% del tiempo
  por vehículo. **Ningún jugador español estudiado (coches.net PRO, Inventario.pro,
  maxterauto, Dealcar) lo ofrece nativo.** Es el hueco de diferenciación de la palabra
  "automática" del nombre del pilar (§8 lo asigna a LLM local/barato).

---

## 3. Objetivo Cardeep para este pilar — y el límite honesto

### 3.1 El límite honesto, primero y sin maquillaje [ASUMIDO tras research, declarado]

Cardeep **NO tiene ventaja estructural en el núcleo de la distribución saliente**. El cuello
de botella es de ACCESO/PARTNERSHIP, no de datos: coches.net cierra la escritura a su propio
software PRO e integradores homologados; Wallapop y Milanuncios no tienen API pública de
escritura descubierta. Los hubs establecidos (Inventario.pro: 18 años, >130k coches/mes)
tienen una posición de partnership que ningún activo de datos acorta por sí solo. Y la pieza
más dura del dominio — dedup de reservas en tiempo real cross-canal — es infraestructura de
escritura/eventos que habría que construir desde cero (el dedup actual de Cardeep dedupe
anuncios de TERCEROS para censo, no reservas salientes propias).

**Consecuencia arquitectónica: el pilar se parte en tres frentes con techos distintos,
y solo se promete lo que cada frente puede cumplir sin acceso negociado.**

### 3.2 Frente A — "Estado de publicación" (donde Cardeep GANA hoy, sin permiso de nadie)

Ningún competidor puede decirle al dealer, con censo real deduplicado de TODOS los portales,
dónde está y dónde NO está su inventario, con qué divergencias de precio y qué anomalías.
Cardeep sí, HOY, con datos que ya existen (`platform_listing` + `vehicle` + dedup 0023):

- Matriz inventario × plataforma con deep link real por celda.
- Divergencia de precio entre el anuncio del dealer y el mismo coche en cada portal.
- Anomalías: "vendido pero sigue publicado" / "disponible pero desaparecido del portal".
- Semáforo de cobertura por plataforma.

Esto es defendible porque nace del activo único (censo cross-portal + delta + dedup + VAM)
y no requiere ni una credencial. **Es el "NOW" real que el blueprint §3.10 prometía sin
respaldo — aquí se construye de verdad.**

### 3.3 Frente B — Distribución saliente SOLO por las puertas abiertas

- **AS24 Listing Creation API**: única API de escritura pública de las 4 plataformas del
  pilar. Adaptador propio, con read-back de verificación (la API es write-only — §2.1).
- **Feeds estándar abiertos** (Google Vehicle Listings + Meta AIA): generación de feed es
  ingeniería pura, sin partnership. Le da al dealer distribución real (Google Surfaces +
  Facebook Marketplace) que los multipublicadores españoles tratan como secundaria.
- Aquí el objetivo es **paridad pragmática**, no superioridad: hacemos lo que AutoPult
  demuestra viable, con la disciplina de verificación de Cardeep.

### 3.4 Frente C — coches.net / Wallapop / Milanuncios (gated, fuera de control de ingeniería)

Tres vías, por orden de preferencia, TODAS dependientes de decisión de negocio del owner:
1. Partnership de integrador B2B con cada portal (la vía de Inventario.pro/maxterauto).
2. Revender a través de un hub ya homologado (Cardeep como cerebro, hub como manguera).
3. Automatización de navegador (Camoufox, §1.6) — técnicamente plausible, [ASUMIDO],
   con riesgo ToS/anti-fraude real (publicar en masa dispara sus sistemas anti-spam) y
   riesgo de bloqueo de cuenta DEL DEALER, no de Cardeep. **No se construye sin OK
   explícito del owner y sin piloto con cuenta de sacrificio.** Esta carta lo deja
   especificado pero NO lo programa.

### 3.5 La ventaja acotada y real: fusionar inteligencia con publicación

El Price Radar del líder (§2.4) se calcula sobre UN portal (el suyo, sesgado a su audiencia).
El **Radar Cardeep** — percentil de precio y rotación calculados sobre el censo canónico
cross-portal deduplicado — es estructuralmente más preciso, y se muestra INLINE en la misma
superficie de publicación (el patrón que el líder validó). Esa fusión es lo que puede superar
a la referencia. Sigue siendo [ASUMIDO] hasta F6: hoy no hay una línea de código que la
materialice, y su valor de distribución depende de que los frentes A/B den al dealer una
razón para estar en la pantalla.

---

## 4. Criterios de evaluación CONCRETOS (qué se muestra y cómo se calcula)

Regla de oro heredada de la doctrina del repo: **ningún número/badge/sección sin criterio
trazable a este documento; si el dato no existe, la UI muestra "sin dato", jamás un
placeholder.** Los umbrales marcados (decisión de producto) son ajustables pero viven en
un solo archivo de constantes, nunca inline.

### 4.1 Cobertura por plataforma (semáforo de cabecera)

- **Cálculo**: para el dealer `D` y la plataforma `P`:
  `cobertura(D,P) = count(DISTINCT pl.vehicle_ulid WHERE pl.status='listed' AND v.entity_ulid=D AND pl.platform_entity_ulid=P AND v.status='available') / count(v disponible de D)`
  sobre `platform_listing pl JOIN servable_vehicle v` (mismo JOIN que
  `platforms.py:59-63` ya usa, verificado).
- **Umbrales** (decisión de producto): verde ≥ 80% · ámbar 40-79% · rojo < 40%.
- **Trazabilidad**: cada celda del semáforo enlaza a la lista de coches que faltan.

### 4.2 Divergencia de precio por anuncio

- **Cálculo**: `Δ = pl.platform_price − v.price` (ambas columnas existen: 0009:23 y vehicle).
- **Badge "precio distinto"** cuando `|Δ| > max(2% de v.price, 200 €)` (umbral de producto,
  elegido para ignorar redondeos y capturar divergencias reales).
- Se muestran SIEMPRE ambos precios con su fuente y su `last_seen` — nunca solo el delta.

### 4.3 Anomalías de estado (los badges rojos)

- **"Vendido pero sigue publicado"**: `v.status='gone' AND pl.status='listed'`.
- **"Disponible pero retirado del portal"**: `v.status='available' AND pl.removed_at IS NOT NULL`.
- Ambas son consultas directas sobre columnas verificadas (0009:25-28); cero heurística.

### 4.4 Días publicado / frescura

- **Cálculo**: `pl.last_seen − pl.first_seen` por arista; badge "anuncio viejo" cuando supera
  la mediana de rotación del segmento (segmento = make+model+year±1+banda de km, calculado
  desde `vehicle_event` GONE — misma base que el pilar 01). Si la mediana del segmento no es
  computable (n < 30 eventos GONE), el badge NO se muestra (regla "sin dato").
  **Enmienda F1 (2026-07-18):** la banda de km se DESCARTA como cómputo propio. `01-market-
  intelligence` ya publica exactamente esta métrica — `market_stat` `metric_id='M3'`
  (`pipeline/market/metrics_f2.py`, mediana de `GONE.observed_at − vehicle.first_seen` por
  segmento make+model+year±1+fuel+province, run+gate real, publicado
  `01KXS6Q4TJKCWM19KKQN2SJ2J1`). `00-MASTER.md` C-1/C-12 prohíben un segundo cómputo
  independiente de mediana-por-cohorte; construir una variante con banda de km habría sido
  exactamente esa segunda implementación que el programa entero existe para evitar. Este
  pilar por tanto **consume M3 en vivo** (JOIN por make+model+year+fuel+province_code del
  dealer contra el run publicado más reciente) en vez de derivarlo. El umbral n≥30 de esta
  carta se aplica como filtro LOCAL adicional sobre el `n` que M3 ya trae (más estricto que
  el `MIN_COHORT_N=8` con el que M3 fue calculado) — no es una re-derivación, es un criterio
  de producto de este pilar sobre un número ajeno ya verificado.

### 4.5 Estado de publicación outbound (Frente B, desde F5)

- Máquina de estados de `publish_job` (tabla nueva, §5):
  `queued → submitting → submitted → live | failed | rejected → delisted`.
- **Criterio duro**: el estado `live` SOLO se muestra cuando el read-back de §7.3 pasó.
  Un 2xx de la API sin read-back se muestra como `submitted (pendiente de confirmar)`.
- Cada job muestra: plataforma, timestamp por transición, y el error literal de la
  plataforma en `failed/rejected` (sin traducir a mensajes vagos).

### 4.6 Salud de feeds (Google/Meta, desde F4)

- Por feed: timestamp de última generación · nº de filas · % de completitud de campos
  obligatorios según la spec exacta (§2.2/§2.3, campo a campo) · resultado del guard
  interno: **si la nueva versión reduce filas >30% vs la anterior, se BLOQUEA la
  publicación del feed y se muestra alerta** (espejo del circuit breaker de Google).
- Un coche excluido del feed muestra POR QUÉ (qué campo obligatorio le falta).

### 4.7 Radar Cardeep inline (desde F6)

- **Posición de precio**: percentil del precio del coche del dealer dentro de su segmento
  en el censo canónico (`v_canonical_vehicle`, migración 0023 — dedup para no contar 3 veces
  el mismo coche en 3 portales) restringido a provincia o radio.
- **Rotación del segmento**: mediana de `(GONE.observed_at − NEW.observed_at)` de
  `vehicle_event` para el segmento.
- Se muestra: percentil + mediana + n del segmento. **Si n < 30, se muestra el rango
  provincial superior o "muestra insuficiente" — nunca un percentil sobre 4 coches.**
- Doble vía de cálculo obligatoria antes de mostrar (§7.5).

---

## 5. Modelo de datos + almacenamiento backend

### 5.1 Se REUTILIZA (existente y verificado, nombres reales)

| Pieza existente | Ubicación [VERIFICADO] | Rol en este pilar |
|---|---|---|
| `platform_listing` | `migrations/0009_platform_listing.sql:16-30` | Fuente del Frente A completo (cobertura, divergencia, anomalías). NO se muta su semántica: sigue siendo la arista inbound descubierta por cosecha. |
| `vehicle` + `vehicle_event` | `migrations/0003_vehicles_events.sql` | Inventario del dealer + base de rotación (GONE) para §4.4/§4.7. |
| `entity` (kind `plataforma` / dealers) | `migrations/0002_entities.sql` | Identidad de plataformas destino y dealers. `platforms.py:46-50` ya valida `kind='plataforma'`. |
| `v_canonical_vehicle` / `vehicle_cluster` | `migrations/0023_vehicle_cluster.sql` | Censo deduplicado para el Radar (§4.7) — no contar N veces el mismo coche físico. |
| `servable_vehicle` (publish-gate interno) | vistas del publish-gate (referidas en `platforms.py:60`) | Solo inventario servible entra en cobertura y feeds. |
| Endpoints `platforms.py` | `services/api/routers/platforms.py:25,89` | Capa de lectura base; los endpoints nuevos del Frente A siguen su patrón exacto (caché, rate-limit, `ok/err`, paginación `page_slice`). |
| `PlatformSpec` | `pipeline/platform/_core/contract.py:14-47` | Se EXTIENDE (campo nuevo de capacidades outbound: `supports_publish_api`, `feed_formats`) en vez de crear un segundo contrato paralelo. |
| Patrón governor | `pipeline/engine/governor.py:1-25` | Se instancia un bucket outbound POR PLATAFORMA DESTINO (instancia nueva, jamás compartir estado con el governor inbound — publicar despacio protege la cuenta del dealer). |
| `browser.py` (Camoufox) | `pipeline/engine/tier1/browser.py:1-37` | SOLO si el Frente C-vía-3 se autoriza (gated, §3.4). No se toca antes. |

### 5.2 Se CREA (nombres propuestos; verificado que NO colisionan — grep repo-completo
cero resultados para estos identificadores en RECON; re-verificar colisión en build)

Numeración: **desde `0073`** (última existente `0072_vehicle_cluster_country_proof.sql`,
re-verificado 2026-07-17). La reserva "0033-0035" del blueprint queda anulada por §1.5.

**CORRECCIÓN F0 (2026-07-18) — la reserva de arriba choca por completo y queda anulada,
exactamente el escenario que `00-MASTER.md` C-6 predijo:**
- `0073` ya es `0073_auth.sql` (AUTH-0, ejecutado 2026-07-17/18 — fusión de 03-F1+05-F3+
  06-F1-tenancy+08-F1). `0074`-`0076` ya son de 01-market-intelligence/02-history-reports/
  00-marketplace-engine. El próximo número libre real hoy es **`0079`** (`ls migrations/*.sql
  | sort | tail -1` → `0078_dgt_corroboration.sql`), y seguirá subiendo mientras 04-arbitrage
  y otros frentes de Bloque 2 corran en paralelo — **quien ejecute F3/F4/F5 de este pilar
  DEBE re-verificar `max(ls migrations/)+1` en el momento exacto de crear cada migración, no
  usar los números de esta tabla**. Los nombres de tabla (`platform_credential`,
  `publish_job`+`publish_job_event`, `feed_export`+`feed_export_run`) siguen vigentes; solo
  el número de archivo cambia.
- **`dealer_account`/`dealer_user` (lo que este documento reservaba para `0073`) NO SE
  CONSTRUYE — está SUPERSEDIDO por AUTH-0**, que ya existe y resuelve exactamente el mismo
  prerrequisito con un esquema más general: `app_user` (roles dealer/particular/staff,
  argon2id) + `dealer_membership` (user↔`entity` N:M, permite multi-rooftop) +
  `user_session` + `user_notification` (`migrations/0073_auth.sql`,
  `services/api/routers/auth.py`). `AuthContext.tsx:48,74` ya llama `/auth/me`/`/auth/login`
  contra este backend REAL (`DEV_BYPASS` ya desmontado). Cuando F3 de este pilar se ejecute,
  su trabajo real es CONSUMIR `dealer_membership`/`app_user.tenantId` (igual que
  03-garage-fleet F1 ya hace en `pages/inventory/`), nunca crear un segundo esquema de tenant
  — exactamente el mandato de `00-MASTER.md` C-3 ("cada carta afectada CONSUME este esquema,
  no crea el suyo"). Este documento's F3 (§9) queda por tanto reducido a: security-review de
  que el flujo `/pro/*` usa `dealer_membership` correctamente + UI de conexión de
  plataformas — no migración nueva de tenant.

- ~~**`0073_dealer_account.sql`** — `dealer_account` (tenant: FK a `entity` del dealer,
  estado, plan) + `dealer_user` (email, password_hash — argon2, jamás en claro —, rol).
  Es el prerrequisito de TODO el shell `/pro/*`; hoy no existe auth alguna (§1.3).
  Convierte en reales los endpoints `/auth/login` y `/auth/me` que
  `web/src/auth/AuthContext.tsx:48,74` ya llama contra el vacío.~~ **(supersedido, ver
  corrección arriba — no se construye)**
- **`0074_platform_credential.sql`** — `platform_credential`
  (`dealer_account` × `platform_entity_ulid`, `kind` ∈ {api_key, oauth, session},
  secreto **cifrado at-rest** (pgcrypto o cifrado de aplicación — decidir en F5 con
  security review), `status`, `last_verified_at`). Nunca texto plano; nunca en logs.
- **`0075_publish_job.sql`** — `publish_job` (dealer, vehicle_ulid, plataforma destino,
  `state` de §4.5, payload_snapshot JSONB del anuncio enviado, `external_ref` devuelto por
  la plataforma, `readback_verified_at`) + **`publish_job_event` append-only**
  (transiciones con timestamp y error literal), replicando el patrón `vehicle_event` y
  respetando los guards append-only del repo (`0035_append_only_row_guards.sql` existe
  precisamente para ese patrón).
- **`0076_feed_export.sql`** — `feed_export` (dealer, formato ∈ {google_vehicle_listings,
  meta_aia}, config) + `feed_export_run` (timestamp, row_count, checksum, campo
  `blocked_by_drop_guard BOOLEAN` — el guard del 30% de §4.6, `completeness JSONB` por campo).
- **`inbox_thread` / `inbox_message`** — **DIFERIDO y declarado como hueco conocido**: no
  existe evidencia verificada de API de mensajería accesible en ninguna de las 4 plataformas
  objetivo (el research no la encontró; maxterauto gated). Diseñarlas hoy sería especular.
  Se abren cuando el Frente C tenga un canal real de mensajes. El mock `Inbox.tsx` actual
  se retira o se deja explícitamente detrás de un flag "demo" (decisión en F2).

### 5.3 Servicios nuevos (código, no tablas)

- `services/api/routers/auth.py` — login/me/logout (F3).
- `services/api/routers/publishing.py` — Frente A (matriz de cobertura, divergencias,
  anomalías) + Frente B (CRUD de `publish_job`, estado de feeds). Mismo patrón que
  `platforms.py` (deps `require_api_key` → sesión de dealer, `ok/err`, caché donde aplique).
- `pipeline/publish/` — paquete nuevo espejo de `pipeline/platform/`:
  `_core/` (contrato de adaptador outbound, validador de campos por spec, governor outbound),
  `as24.py` (adaptador API oficial), `feeds/google.py`, `feeds/meta.py`.
  Los adaptadores gated del Frente C, si algún día se autorizan, viven aquí con el mismo contrato.

---

## 6. Especificación de pantalla — en la piel del dealer real

Ruta: **`/pro/publicaciones`** dentro del shell `/pro/*` (que F3 hace real). Lenguaje del
dealer español: "coches", "portales", "anuncios" — jamás "listings", "SKUs" ni jerga SaaS.
Se construye sobre el design system existente del repo (tokens + `Card`), no otra plantilla.

### 6.1 Cabecera — "Tu stock en los portales"

- Semáforo de cobertura por portal (§4.1): logo del portal + % + verde/ámbar/rojo.
  Al lado, el total: "82 de tus 97 coches están en algún portal".
- Cada cifra clica → filtra la tabla a los coches que faltan en ese portal.

### 6.2 Tabla principal — un coche por fila, un portal por columna

- Fila: foto miniatura, marca/modelo/versión, precio del dealer, días en stock.
- Celda coche×portal, estados posibles (todos de §4, nada más):
  - **Publicado** — check + enlace directo al anuncio real (deep link de `listing_url`,
    doctrina deep-links del proyecto) + "visto hace N h" (`last_seen`).
  - **Precio distinto** — ámbar: "aquí lo tienes a 18.900 €, en el portal sale a 19.400 €".
  - **Vendido pero sigue publicado** — rojo: el coche está `gone` y el anuncio vivo.
    Acción sugerida: "márcalo como retirado" (y en Frente B: botón de despublicar real).
  - **No publicado** — gris. En Frente B, si el portal es AS24/feed: botón "Publicar aquí".
  - **Por confirmar** — cuando las dos vías de §7 discrepan; nunca se disfraza de verde.
- Sin datos de cosecha frescos para un portal (>N días): la columna entera muestra
  "datos de hace N días", no estados en falso presente.

### 6.3 Panel lateral — "Radar Cardeep" (desde F6)

- Al seleccionar un coche: "Tu precio está en el percentil 78 de los 214 BMW 320d
  2019-2021 similares a la venta en tu provincia (todos los portales, sin duplicados).
  Coches como este se venden en una mediana de 34 días."
- Cada frase lleva su n y su fecha de cálculo. Si n < 30: "muestra insuficiente en tu
  provincia — te enseño el dato nacional" (§4.7).

### 6.4 Publicación saliente (desde F5) — "Publicar" sin humo

- Botón "Publicar en AutoScout24" (único portal con vía directa; los demás aparecen como
  "próximamente — requiere acuerdo con el portal", VERDAD antes que marketing).
- Panel de job: progreso por transición real de `publish_job_event` (no barra decorativa),
  error literal de la plataforma si falla, y estado final "Publicado y comprobado" SOLO
  tras read-back (§7.3) — antes de eso: "Enviado, comprobando…".
- Sección "Feeds": "Tu stock en Google" / "Tu stock en Facebook Marketplace" — estado del
  feed (§4.6), URL del feed, y aviso bloqueante si el guard del 30% saltó.

### 6.5 Conexión de portales (desde F5)

- "Conectar AutoScout24": formulario de credencial API → se valida contra la API real antes
  de guardar (`last_verified_at`); estado "conectado/caducado/fallando" siempre visible.

### 6.6 Lo que NO habrá (anti-mock, vinculante)

- Ni un dato inventado: cero `MOCK_*` en la página (criterio de F2: grep = 0).
- Ni inbox de mensajes hasta que exista canal real (§5.2) — no se enseña una bandeja
  vacía cosplayando producto.
- Ni portales fuera de alcance España (el `mobile.de` del mock actual desaparece).

---

## 7. Protocolo de verificación — 2 vías independientes por dato mostrado

El mismo estándar antialucinación del proyecto, aplicado al producto: **nada se etiqueta
"verificado" ante el dealer sin dos caminos independientes en verde; discrepancia → estado
"por confirmar" visible, jamás resolución silenciosa.**

1. **Estado "Publicado" (Frente A)** — vía 1: arista `platform_listing` de la última
   cosecha (`last_seen`). Vía 2: re-fetch vivo del `listing_url` (HTTP 200 + match de
   `listing_fingerprint`) disparado bajo demanda al abrir el detalle o en refresco
   programado. Verde solo con ambas; si el re-fetch da 404/redirect, la celda pasa a
   "por confirmar" y se encola re-cosecha.
2. **Divergencia de precio** — vía 1: `platform_price` de la cosecha. Vía 2: el precio
   extraído en el re-fetch de la vía anterior, o en su defecto dos corridas de cosecha
   consecutivas independientes con el mismo valor. Se muestra el timestamp de cada fuente.
3. **"Publicado" outbound (Frente B, AS24)** — vía 1: respuesta 2xx de la API con
   `external_ref`. Vía 2 (obligatoria porque la API es write-only, §2.1): **read-back** —
   fetch de la URL pública del anuncio + match de fingerprint contra el
   `payload_snapshot` del job. `readback_verified_at` se sella solo entonces; hasta
   entonces el estado es `submitted`, nunca `live`.
4. **Feeds** — vía 1: row_count del archivo generado vs COUNT SQL de la query fuente
   ejecutada por separado (no el mismo cursor). Vía 2: el informe de ingesta de la propia
   plataforma (diagnóstico de Google Merchant / Meta catalog) cuando esté conectado;
   mientras no lo esté, se declara en UI "validado internamente, sin confirmación del
   portal" — el hueco se dice, no se tapa. Guard del 30% en ambos casos.
5. **Radar (percentil/rotación)** — vía 1: cálculo sobre el censo deduplicado
   (`v_canonical_vehicle`). Vía 2: recuento independiente sobre `platform_listing` crudo
   (pre-dedup) que acota el percentil por arriba y por abajo. Si las cotas divergen más
   allá de la tolerancia (±5 puntos de percentil, umbral de producto), se muestra el RANGO,
   no un punto.
6. **Regla transversal de UI**: todo número lleva `fuente + calculado_en`; el tooltip
   enseña las dos vías. El estado "verificado" es un badge ganado, no el default.

---

## 8. Uso de LLM — doctrina €0 del CLAUDE.md del repo

("modelos LLM locales para lo masivo y barato; la inteligencia cara, solo para decidir")

### 8.1 Local/barato (masivo, en el camino caliente permitido)

- **Mapeo de equipamiento/versión** al vocabulario de cada plataforma destino (texto libre
  del anuncio → enums `EquipmentSearchAttribute` de AS24, `body_style` de Meta):
  clasificación acotada a vocabulario cerrado — modelo local con salida restringida +
  validación determinista posterior contra el enum (un valor fuera de vocabulario se
  rechaza, no se "corrige" a ojo).
- **Generación de borradores de descripción** de anuncio desde datos estructurados
  (make/model/year/km/equipamiento) — el hueco de mercado de §2.7. SIEMPRE borrador:
  el dealer aprueba antes de publicar; límite duro de 5.000 caracteres (Meta) validado
  fuera del LLM.
- **Clasificación de errores de plataforma** (respuestas de rechazo → categorías de retry:
  transitorio / campo inválido / credencial caducada / bloqueo) — parsing barato con
  fallback determinista por código HTTP.

### 8.2 Modelo caro — SOLO decidir, nunca en el camino por-publicación

- **Diseño-time, one-off**: revisión adversarial de la tabla de mapeo campo-a-campo
  Cardeep→AS24/Google/Meta antes de sellarla (una vez por versión de spec), y arbitraje
  en lote de los casos de equipamiento ambiguos del backfill inicial (acotado, con budget).
- **Explícitamente PROHIBIDO**: LLM caro en el hot path de cada publicación o cada
  render de la pantalla. La validación pre-envío es 100% determinista (schemas exactos de
  §2.1-§2.3); el Radar es 100% SQL. Un anuncio jamás se publica porque "el modelo lo vio bien".

---

## 9. Fases de construcción (orden estricto; ninguna fase abre sin cerrar la anterior)

> Autoridad asumida para reemplazar/reestructurar código existente donde haga falta
> (el mock `Inbox.tsx` y el contrato del shell `/pro/*` incluidos). Cada fase termina en
> build + tests + revisión real (code-reviewer; security-reviewer obligatorio donde hay
> auth/credenciales, por las reglas del propio repo) — nunca "deploy y ya".

- **F0 — Verdad en tierra + corrección de deriva.** Corregir
  `docs/frontend/00-PLATFORM-BLUEPRINT-E2E.md` §3.10 (etiqueta NOW sin respaldo; números
  0033-0035 → 0073+) con referencia a esta carta; censo SQL de `platform_listing` por
  plataforma × dealers con inventario. *Verificación:* cada número reproducido por 2 vías
  (SQL directo + endpoint `platforms.py` existente); diff del doc commiteado; el espejo
  second-brain se regenera vía graphify (no se edita a mano).
- **F1 — API del Frente A.** `publishing.py` de solo lectura: matriz de cobertura,
  divergencias, anomalías (§4.1-4.4), siguiendo el patrón exacto de `platforms.py`.
  *Verificación:* pytest (casos: dealer sin inventario, plataforma inexistente, coche gone,
  paginación); cross-check de counts contra `/platforms/{cdp}/inventory` en ≥3 dealers
  reales; spot-check manual de 20 deep links vivos; review.
- **F2 — Pantalla `/pro/publicaciones` (solo lectura).** §6.1-6.3 sin Radar; retirada o
  flag-demo del mock `Inbox.tsx` (decisión en la fase, documentada). *Verificación:* build
  verde; grep `MOCK_` en la página = 0; checklist número-a-criterio (cada dato en pantalla
  → sección §4 de esta carta); revisión visual contra el design system; estados
  "sin dato"/"por confirmar" demostrados con datos reales degradados.
  **Corrección de ruta (F2, 2026-07-18):** el prefijo `/pro/*` de §6 era aspiracional — el
  `App.tsx` real no tiene NINGÚN namespace `/pro/` en ninguna ruta (AUTH-0 resolvió el auth
  sin introducirlo; todas las rutas protegidas son planas: `/dashboard`, `/inbox`, etc.).
  La ruta real construida es **`/publicaciones`** (plana, bajo el mismo `Shell`/
  `ProtectedRoute` que el resto de la app) — coherente con lo que existe, no con lo que el
  blueprint imaginaba.
- **F3 — Auth dealer/tenant — SUPERSEDIDA por AUTH-0 (ver corrección §5.2, F0 2026-07-18).**
  `auth.py`/`AuthContext.tsx`/`DEV_BYPASS` ya son reales HOY (ejecutado 2026-07-17/18, fuera
  de este pilar). Lo que queda de F3 para este pilar: verificar que `/publicaciones` respeta
  el tenant scoping de `dealer_membership` (un dealer jamás ve la matriz de otro — ya
  garantizado por diseño, F1 exige `cdp_code` explícito) y, si acaso, UI de conexión de
  plataformas. Ninguna migración nueva de auth.
- **F4 — Feeds Google + Meta (número real: `max(ls migrations/)+1` en el momento de
  ejecutar F4, NUNCA `0076` — ya consumido por `0076_adaptive_cadence.sql` de 00, ver §5.2).**
  Generadores en `pipeline/publish/feeds/`
  + validador campo-a-campo contra las specs exactas (§2.2/§2.3) + guard del 30%.
  *Verificación:* tests de schema por campo obligatorio (incluido el caso "campo ausente
  rechaza el ítem/feed"); doble vía de row_count (§7.4); test del guard (fixture que cae
  31% → bloqueado; 29% → pasa); validación del archivo con el validador oficial de la
  plataforma si existe, y si no, declararlo en el informe de fase como hueco.
- **F5 — Adaptador AS24 + `publish_job` + credenciales (números reales a re-verificar con
  `max(ls migrations/)+1` al ejecutar — `0074`/`0075` ya pertenecen a 01/02, ver §5.2).**
  Contrato de adaptador outbound en `pipeline/publish/_core/`, `as24.py` contra el OpenAPI
  público, governor outbound (instancia nueva), almacén cifrado de credenciales, endpoints
  de job + UI §6.4-6.5. *Verificación:* contract-tests generados desde el spec OpenAPI del
  repo público de SMG; read-back implementado y testeado (job no llega a `live` sin él —
  test que lo fuerza); **security review de credenciales** (cifrado at-rest, cero secretos
  en logs, test de log-scrubbing); prueba real contra sandbox/cuenta de AS24 si el owner
  la provisiona — si no hay cuenta, la fase se sella como "contract-verified, pendiente de
  credencial real" y ASÍ se reporta (hueco declarado, no maquillado).
- **F6 — Radar Cardeep inline (§4.7 + §6.3).** SQL de percentil/rotación sobre
  `v_canonical_vehicle` + `vehicle_event`; fusión en el panel. *Verificación:* doble vía
  dedup-vs-crudo (§7.5) sobre ≥5 segmentos con n conocido; caso n<30 demostrado; sanity
  del percentil contra recuento manual de un segmento pequeño hecho a mano.
- **F7 — Frente C (GATED, no programado).** Partnership/hub/browser-automation para
  coches.net, Wallapop, Milanuncios. Bloqueada por decisión de negocio del owner (§3.4);
  el pre-trabajo de ingeniería (contrato de adaptador de F5) queda listo para enchufar.
  *Criterio de apertura:* acceso real firmado (API de partner, contrato de hub, u OK
  explícito del owner para el piloto de navegador con cuenta de sacrificio). Sin eso,
  esta fase no consume ni una hora.

---

## 10. Ejecución F0-F2 (2026-07-18) — Frente A cerrado, solo-lectura

> Ejecutado dentro de BLOQUE 2 (`PROGRESO.md`), en paralelo con 03-garage-fleet F1-F4 y
> 04-arbitrage F1-F6 (mismo repo, misma DB viva `cardeep-pg`, mismo API server `:8090`) —
> tres commits atómicos independientes, sin colisión de archivos gracias a la tabla de
> ownership de `00-MASTER.md` §5.1 y a la disciplina append-only en `cardeep.ts`/`main.py`.

### 10.1 F0 — Verdad en tierra + corrección de deriva

- Censo real de `platform_listing` ejecutado (`scripts/f0_publishing_census.py`, re-
  ejecutable): **2.430.136 aristas totales, 1.938.891 `listed`, 43 plataformas**;
  **380.852 dealers con inventario disponible, 378.057 (99,27%) con ≥1 arista `listed`**.
  Verificado por 2 vías: SQL directo (`platform_listing JOIN servable_vehicle JOIN entity`,
  el MISMO join que `platforms.py:59-63`) y el endpoint `GET /platforms/{cdp}/inventory`
  YA existente — 7 plataformas pequeñas paginadas a COMPLETITUD (BCA España, Autorola,
  Miclasico, Car & Classic, RACC, Subastacar, LocalizaVO: conteo exacto, 0 discrepancia);
  9 plataformas grandes muestreadas (primera página, prueba de subconjunto — paginar
  Wallapop/coches.net/AS24 enteras a través del rate-limiter compartido con las otras 2
  sesiones paralelas se declaró inviable, no se maquilló como completo).
- **Hallazgo real no anticipado por la carta (F0.2b):** `platforms.py:49-50` exige
  `entity.kind == 'plataforma'` y devuelve 400 si no — pero **96.941 aristas reales**
  (25 entidades: 14 `oem_vo_portal` como `mercedes_benz`/`audi`/`hyundai`/`toyota_lexus`,
  4 `cadena` como Flexicar/Clicars/OcasionPlus/Carplus, 6 `rent_a_car_vo` como Arval/OK
  Mobility, 1 `importador`) usan ese endpoint sin poder ser consultadas por él. Verificado
  con un caso de tres partes distintas real: dealer `CDP-ES-01-7J6SM0SQ` (un concesionario
  cualquiera) tiene un coche cross-posteado en `volvo_jlr_suzuki` (`oem_vo_portal`) — un
  cross-posting genuino, no un self-loop de identidad. Declarado para quien posea
  `platforms.py`; el router nuevo de este pilar (§10.2) NO reproduce ese gate.
- Corrección de cifra de migraciones: "66" (§1.1) seguía siendo correcta como cierre de
  Bloque 0; hoy son **72 archivos reales**, última `0078_dgt_corroboration.sql` — Bloque 1
  consumió `0073`(AUTH-0)-`0078`(01/00), colisionando por completo con la reserva original
  de §5.2 de este documento. Corregido en §5.2/§9 (F3 supersedido por AUTH-0; F4/F5 re-
  verifican `max(ls migrations/)+1` en el momento real de ejecutar, nunca los números aquí
  escritos). Blueprint §3.10 re-verificado: sin deriva nueva desde el barrido de Bloque 0.
- §4.4 enmendado: reutiliza `market_stat` `metric_id='M3'` de 01-market-intelligence (ya
  publicado, `run_id=01KXS6Q4TJKCWM19KKQN2SJ2J1`) en vez de una segunda mediana-por-cohorte
  con banda de km — evita la tercera implementación que `00-MASTER.md` C-1/C-12 prohíben.

### 10.2 F1 — API del Frente A

- `services/api/routers/publishing.py` (nuevo, 2 endpoints, patrón exacto de
  `platforms.py`): `GET /publishing/{cdp}/coverage` (semáforo §4.1, solo plataformas con
  ≥1 arista) y `GET /publishing/{cdp}/matrix` (paginado, fusiona §4.1-§4.4: divergencia de
  precio, anomalías, frescura vía M3). Registrado en `main.py`.
- **23 tests nuevos** (`tests/test_api_publishing.py`): 8 unitarios de funciones puras
  (`_coverage_band`, `_price_divergence`, `_classify_anomaly` — extraídas para ser
  testeables sin depender de que la DB viva contenga hoy un ejemplo positivo) + 15 de
  contrato/DB reales. **0 regresión** confirmada en 13 archivos de test de impacto:
  `test_api_gaps`, `test_api_exhaustiveness`, `test_api_pagination`, `test_api_auth`,
  `test_api_canonical`, `test_api_seal`, `test_api_ratelimit_cache`,
  `test_platform_persistence_core`, `test_platform_mint_country_routing`,
  `test_country_isolation_vin_xplatform`, `test_engine_api_proxies`, `test_api_lifetime`,
  además del propio `test_api_publishing`.
- Cross-check de counts contra `/platforms/{cdp}/inventory` en **3 dealers reales**
  (Valdisa `CDP-ES-46-AD9ZXC65`, Concesur `CDP-ES-41-1YVBKMVH`, Autos Juanjo
  `CDP-ES-28-5K6CNPCE`). **Bug real cazado en el propio proceso de verificación**: el
  primer diseño del test paginaba la plataforma ENTERA vía HTTP filtrando por dealer en el
  cliente — `/platforms/{cdp}/inventory` no filtra por dealer server-side, así que las
  ~200 aristas de un dealer pueden estar dispersas entre miles de páginas de una plataforma
  de 274k/789k filas. Colgó >15 minutos contra `coches.net` antes de matarse; verificado en
  vivo por `pg_stat_activity` que era una consulta real en curso (`ParallelBitmapScan`), no
  un deadlock. Corregido: la segunda vía pasa a ser SQL directa replicando el JOIN exacto de
  `platforms.py` pero acotado por dealer — rápida, exacta, igual de independiente.
  Divergencia de precio verificada contra un ejemplo real vivo (buscado dinámicamente en
  cada corrida, no hardcodeado, porque el motor de cosecha está vivo y los datos cambian).
  Hallazgo F0.2b re-verificado en `matrix` con el dealer `CDP-ES-01-7J6SM0SQ`: la arista
  `oem_vo_portal` se sirve sin 400. `sold_still_listed` verificado SOLO por unidad — 0
  instancias reales existen hoy (`vehicle.status='gone'`=546.157;
  `platform_listing.status='removed'`=491.245; de los 546.157 `gone`, exactamente 491.245
  tienen alguna arista, y las 491.245 `removed` coinciden 1:1 — el harvester ya sincroniza
  ambos estados en el mismo paso, así que la anomalía es real pero no observable hoy).
  Spot-check de deep links: no ejecutado como paso manual aparte — los mismos `listing_url`
  cross-checados arriba (SQL vs endpoint) son URLs reales de la cosecha viva, no fixtures.

### 10.3 F2 — Pantalla `/publicaciones` (solo lectura)

- `web/src/pages/Publicaciones.tsx` (nueva) + `web/src/api/cardeep.ts` (sección propia,
  append-only, tipos + `publishingCoverage`/`publishingMatrix`) + ruta `/publicaciones` en
  `App.tsx` + entrada de nav "Publicaciones" en el grupo OPERACIÓN de `Shell.tsx` (commit
  atómico al cierre, per regla del master de nav/rutas). Dealer scope =
  `useAuthContext().user.tenantId` — la MISMA convención que 03-garage-fleet F1 ya
  estableció para `pages/inventory/` (verificado leyendo su diff en vivo durante esta
  ejecución), nunca un cdp hardcodeado.
- Cabecera de cobertura por plataforma (semáforo verde/ámbar/rojo) + tabla vehículo×portal
  con celdas: Publicado (check + deep link + "visto hace Nh" + reloj si `old_listing`),
  Precio distinto (ámbar, ambos precios mostrados), Vendido pero sigue publicado (rojo),
  Retirado del portal, No publicado (gris). `grep MOCK_ web/src/pages/Publicaciones.tsx` = 0.
- **C-10 (regla del primer llegado) aplicada sobre `Inbox.tsx`**: 06-unified-crm-chat no ha
  aterrizado (Bloque 3, sin empezar). `MOCK_CONVS` (mobile.de/autoscout24, contactos
  ficticios) retirado; `?? MOCK_CONVS` → `?? []`; empty-state honesto que distingue
  "Bandeja aún no conectada" (hoy, `/inbox` no existe en el backend) de "Sin
  conversaciones" (tras F4 de 06). `useInbox.ts`/hooks NO se tocaron. Registrado en el
  encabezado de `06-unified-crm-chat.md` para que 06 no lo redescubra como sorpresa.
- Corrección de ruta: `/pro/publicaciones` (§6) era aspiracional — `App.tsx` real no tiene
  namespace `/pro/*` en ninguna parte; la ruta construida es `/publicaciones` (plana).
- Verificación: `npx tsc --noEmit` limpio + `vite build` verde (3599 módulos, sin nuevos
  errores atribuibles a este pilar — el árbol compartido tenía en el momento de esta
  ejecución trabajo en curso no comiteado de 03/04/09 en otros archivos, verificado archivo
  por archivo que ningún error pertenece a `Publicaciones.tsx`/`cardeep.ts`/`App.tsx`/
  `Shell.tsx`/`Inbox.tsx`). Checklist número-a-criterio: cada dato mostrado traza a §4 de
  esta carta (cobertura→§4.1, divergencia→§4.2, anomalías→§4.3, frescura→§4.4).

### 10.4 Alcance NO tocado (gated, fuera de este mandato)

F3 (auth — supersedida, ver §5.2/§9), F4 (feeds Google/Meta), F5 (adaptador AS24 +
credenciales), F6 (Radar Cardeep), F7 (Frente C — coches.net/Wallapop/Milanuncios). Ni una
línea de código outbound, ni una credencial, ni un adaptador de plataforma se construyó en
esta ejecución — el pilar sigue siendo, más allá del Frente A ahora real, exactamente el
net-new que §1 describe.

---

## Resumen

El pilar es net-new absoluto: hoy solo existe la dirección inbound (`platform_listing`,
0009) y un mock CRM desconectado, con el doc de visión §3.10 desalineado del código en dos
puntos verificados. La estrategia honesta parte el pilar en tres frentes: (A) "estado de
publicación" cross-portal — donde el censo deduplicado de Cardeep gana HOY sin pedir permiso
a nadie; (B) distribución saliente solo por puertas abiertas (API oficial de AS24 + feeds
estándar de Google/Meta), con read-back obligatorio porque la API de AS24 es write-only;
(C) coches.net/Wallapop/Milanuncios gated a partnership — el cuello real del pilar es de
acceso, no de ingeniería, y esta carta no lo maquilla. La ventaja defendible es una y
acotada: fusionar el Radar de precio/rotación cross-portal (mejor señal que el Price Radar
mono-portal del líder) en la propia superficie de publicación, tras auth de dealer (0073+)
que hoy no existe y se construye primero.
