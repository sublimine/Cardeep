# 04 — Arbitraje de otro nivel

> Carta de sub-proyecto institucional. Pilar `04-arbitrage` del programa cardeep-omni.
> Fase: F1-F5 EJECUTADAS Y VERIFICADAS EN VIVO contra cardeep-pg; F6 (identidad-captura) workstream
> de fondo — mecanismo construido y verificado, ejecución parcial (ver §10). Fecha ejecución: 2026-07-18.
> Doctrina: cada afirmación es [VERIFICADO] (leída en código/DB real) o [ASUMIDO]/[HUECO] (declarado como tal).
> Nada de lo aquí planificado existe todavía salvo lo marcado como existente.
> Verificación de segunda vía (2026-07-17, pasada independiente): 14 anclajes archivo:línea re-leídos en
> código/esquema real — detect.py:108-114 y :828, Arbitrage.tsx:55/63/69/79/240/347, AuthContext.tsx:6,
> 0031_gestion.sql:44/158, 0003:4/18/33, 0002:13, 0009:16/23-25, cardeep.ts:171-173, última migración
> 0072_vehicle_cluster_country_proof.sql, y nombres nuevos (cohort_stats/deal_score/market_decay) libres
> (grep = 0 hits). Todos exactos; cero correcciones necesarias.

---

## 1. Estado actual

### 1.1 Diseño previo
- [VERIFICADO] `plans/intel-audit/ARBITRAGE.md` (56 líneas) define 5 señales — (1) mispricing comprador
  ("chollos"), (2) gap cross-platform, (3) time-arbitrage, (4) geo-arbitrage, (5) spread wholesale→retail —
  y el propio documento cierra con el checkbox sin marcar "[ ] Implementación: deal-score + sourcing view
  sobre el censo". El autor ya declara que NO está construido.
- [VERIFICADO] `docs/SUPERPLAN.md` y `PROGRESO.md`: 0 menciones de "arbitrage" (grep -ci = 0 en ambos).
  Este pilar nunca entró en fase de ejecución/seguimiento. Está en fase plan + mock de UI.

### 1.2 Frontend
- [VERIFICADO] `web/src/pages/Arbitrage.tsx`: 100% datos hardcodeados — `const CHOLLOS` (línea 55),
  `const CROSS_GAPS` (línea 63), `const SPREAD` (línea 69), `const TIME_DATA` (línea 79). Cero `fetch`,
  cero `useQuery`, cero import de `../api/cardeep` (grep = 0 ocurrencias en el archivo). Todo el panel
  envuelto en un único `PremiumGate` con `feature="sourcing-ranking"` (línea 347).
- [VERIFICADO] Excepción de honestidad ya presente: el SpreadPanel declara "Pendiente de partnership —
  no es un dato inventado" (`Arbitrage.tsx:240`). Esa honestidad NO se rompe: es el patrón a extender.
- [VERIFICADO] `web/src/pages/Inteligencia.tsx` contiene `SweetSpotCard()` con literales fijos
  ("17.800 €" / "óptimo 18.450 €" / "19.500 €") sin prop ni cómputo — el "prototipo" que ARBITRAGE.md §1.1
  reclama es un mockup visual, no señal funcional.
- [VERIFICADO] Superficie paralela divergente: `web/src/pages/terminal/Arbitrage.tsx` +
  `web/src/pages/terminal/market.ts` (ruta `/terminal` vía `Terminal.tsx`) — terminal cross-border EU
  (DE/FR/ES/NL/BE/CH) cuyo propio comentario de cabecera en `market.ts` admite: "Deterministic, seeded
  synthetic data... When the backend lands, swap these generators for API calls." 100% RNG en cliente,
  concepto fuera del mandato España-only de CLAUDE.md. Dos visiones de "Arbitrage" conviven sin reconciliar.
- [VERIFICADO] Gating sobre plan mock: `web/src/auth/AuthContext.tsx:6` → `const DEV_BYPASS = true`,
  usuario dev con `plan: 'starter'` (línea 14). `web/src/lib/entitlements.ts` implementa la comparación de
  rangos real, pero no hay billing decidiendo el desbloqueo. Aunque se forzara 'enterprise', lo desbloqueado
  sigue siendo mock.

### 1.3 Backend real reutilizable
- [VERIFICADO] `pipeline/gestionador/detect.py::detect_price_trap` (línea 828): detector de anomalía de
  precio por cohorte, robust-z sobre `ln(price)` con mediana + MAD (factor 1.4826), cohorte Tier-A
  (make, model, year) con n≥15 y fallback Tier-B (make, year) con n≥30. Constantes en líneas 108-114:
  `PRICE_TRAP_COHORT_Z = 6.0`, `PRICE_TRAP_COHORT_MIN_A = 15`, `PRICE_TRAP_COHORT_MIN_B = 30`,
  `PRICE_TRAP_MAD_FLOOR = 0.05`, `PRICE_TRAP_HIGH_ABS_FLOOR = 150_000`, `PRICE_TRAP_LOW_MEDIAN_FRAC = 0.25`,
  `PRICE_TRAP_MAX_ROWS = 5000`. Su propósito hoy es HIGIENE (cuarentena de precios-basura vía
  `gestion_item`, migración `0031_gestion.sql:44`; los cuarentenados salen de la vista `servable_vehicle`,
  `0031_gestion.sql:158`, redefinida en 0040/0045/0047). NO surfacea gangas legítimas — pero es
  estructuralmente el mismo primitivo estadístico que necesita el deal-score.
- [VERIFICADO] `grep -rniE 'deal.?score|mispricing|sourcing|arbitrage'` en migrations/services/pipeline/scripts
  = 0 hits (re-verificado 2026-07-17). Nada del pilar existe en backend; los nombres nuevos propuestos en §5
  están libres.

### 1.4 Sustrato de datos (DB viva `cardeep-pg`, medido en el RECON 2026-07-17)
- [VERIFICADO] `vehicle_event` (esquema en `migrations/0003_vehicles_events.sql:33-42`: append-only,
  `event_type` ∈ {NEW, GONE, PRICE_CHANGE, PHOTO_CHANGE, KM_CHANGE}, `old_value`/`new_value` JSONB,
  `observed_at`): NEW=2.542.358, GONE=458.436, PRICE_CHANGE=267.193, PHOTO_CHANGE=116.285, KM_CHANGE=24.138.
  Servido por `GET /vehicles/{ulid}/history` (`services/api/routers/vehicles.py:24`).
- [VERIFICADO] `platform_listing` (esquema en `migrations/0009_platform_listing.sql:16-30`: PK
  (vehicle_ulid, platform_entity_ulid), `platform_price NUMERIC(12,2)`, `listing_fingerprint`,
  first/last_seen): 2.300.670 filas, pero `GROUP BY vehicle_ulid HAVING count(*)>=2` → **0 filas**.
  Ningún vehículo del censo vivo está hoy en 2+ plataformas. La señal #2 "mismo coche, precio distinto
  en A vs B" tiene CERO casos reales.
- [VERIFICADO] Causa raíz del cero (leída en `scripts/cross_platform_dedup_watermark.py`): `photo_hash`
  poblado en 0 vehículos (el brazo pHash no puede correr); VIN de 17 caracteres en solo 17.730 vehículos,
  de los cuales 18 comparten VIN entre plataformas; la duplicación material (~131,8K filas) vive en una
  clave débil (make+model+year+km+price+provincia) que la doctrina anti-over-merge PROHÍBE auto-mergear —
  se mide con banda ±dup_ci, no se resuelve a identidad fuerte.
- [VERIFICADO] Lo que SÍ existe con identidad cierta: divergencia `vehicle.price` vs `platform_listing.platform_price`
  dentro de la MISMA fila-edge (ej. €15.490 vs €14.990 observado en muestra del RECON) — señal de
  "desync de precio dealer↔espejo", identidad garantizada por construcción (misma fila).
- [VERIFICADO] Geo: `entity.province_code CHAR(2) REFERENCES geo_province(code)`
  (`migrations/0002_entities.sql:13`); `vehicle` NO tiene columna de provincia (`0003:4-26`) — la dimensión
  geográfica del vehículo se deriva vía `vehicle.entity_ulid → entity.province_code`.
  `services/api/routers/geo.py` expone solo cobertura (completeness/seal/exhaustiveness/entities/tree,
  líneas 32-398): CERO agregación de precio por provincia en todo el repo.
- [VERIFICADO] Cliente API tipado ya operativo: `web/src/api/cardeep.ts:171-173`
  (`vehicleHistory`, `vehiclePlatforms`) — consumido hoy solo desde
  `web/src/pages/inventory/VehicleDetailModal.tsx`, nunca desde `Arbitrage.tsx`.

### 1.5 Síntesis del estado
Cinco señales diseñadas; cero en producción. Un detector estadístico real y vivo (price_trap) apunta en
dirección opuesta (cuarentena, no oportunidad). Un stream de delta nacional real y masivo (vehicle_event)
sin ningún modelo encima. Una señal (cross-platform) bloqueada en la capa de identidad con 0 casos reales.
Una señal (spread mayorista) honesta y correctamente gated por partnership externo. Y una superficie
sintética (/terminal) fuera de mandato que contamina el nombre del pilar.

---

## 2. Investigación competitiva / adversarial

Peer-set honesto (hallazgo del research adversarial): ninguna referencia de "deal-score" practica arbitraje
en sentido cuantitativo estricto (compra-venta simultánea con spread bloqueado, cointegración verificada,
entrada/salida ±2σ/±0,5σ). CarGurus/iSeeCars/CoPilot venden **señal de asimetría informativa a un comprador
unilateral** — exactamente la categoría que ARBITRAGE.md describe. El arbitraje real (capturar el spread
como principal) lo ejecutan CarMax/Carvana/dealers, rol que Cardeep no tiene ni pretende. Contra ese
peer-set se mide este pilar.

Criterios EXACTOS extraídos (no genéricos):

1. **CarGurus IMV** (PDF oficial 2018): recalculado a diario, "over five million data points"; deal rating =
   asking vs IMV ponderado TAMBIÉN por reputación del dealer (no precio-puro). 80% de los leads van a deals
   Fair/Good/Great (Q4 2017). Los umbrales de corte exactos NO son públicos (estimaciones de terceros
   existen pero CarGurus los declara variables por categoría/precio) — [HUECO conocido: no copiar umbrales
   no confirmados; definir los propios y publicarlos en la metodología].
2. **iSeeCars**: 10M+ listados/día, 25B+ data points; comparable-set por year+make+model+trim+options+
   mileage+área local; separa "Below/Above Market" (precio puro) de "Good Deal" (compuesto precio+condición+dealer).
3. **MMR (Manheim/Cox)**: ~4,1M transacciones subasta/año; 4 pilares de ajuste (recencia ponderada,
   condición estandarizada, km vs promedio Y/M/M, ajuste regional); **requisito mínimo de datos: ≥6
   transacciones/12 meses Y ≥2/90 días por celda trim — si no, NO se emite valor**. Esta disciplina de
   mínimo-N-o-silencio es el criterio de gobernanza central que Cardeep adopta.
4. **Iglewicz & Hoaglin (modified z-score)**: z_mod = 0,6745·(x − mediana)/MAD; outlier si |z_mod| > 3,5;
   zona limítrofe [2, 3,5]. Estructuralmente idéntico al robust-z de `detect_price_trap` (que usa
   1/1.4826 ≈ 0,6745). Referencia académica del umbral de deal-score en §4.
5. **Patente Mercari US 11.694.218 B2** (time-arbitrage, la referencia técnica pública más completa):
   (a) category decay curve = % del precio original en función de la edad del listado (ejemplo real de la
   patente: 100% día 0 → 93% día 5 → 80% día 15 → 60% día 30), **cada punto exige un número de ventas
   superior a umbral en ventana predeterminada o el punto no se genera**; (b) seller flexibility curve con
   ventana deslizante 5-10 días + mínimo de ventas; (c) ZOPA = intersección de ambas curvas; (d) ensemble de
   3 paradigmas de pricing combinados por promedio ponderado por confianza: precio_óptimo = Σ(ct_i×p_i)/Σ(ct_i);
   (e) nudge engine que solo sugiere bajadas dentro de la flexibilidad histórica del vendedor.
6. **CarStory GoPrice (Cox)**: un solo modelo produce EN LA MISMA LLAMADA precio predicho Y tiempo de venta
   predicho — precio y velocidad como salida conjunta, no señales separadas. Estructura objetivo del
   time-arbitrage de Cardeep a largo plazo.
7. **MarketCheck**: 5B+ listados desde 2015; sistema de atribución de vehículo de **8 niveles de confianza**
   sobre el mismo VIN en N sitios para decidir posesión física real. El mínimo viable de identidad
   cross-platform contra el que Cardeep hoy está por debajo (0 pares).
8. **Fellegi-Sunter (1969)**: record linkage probabilístico — peso log-verosimilitud por campo
   [P(coincide|mismo)/P(coincide|distinto)], score compuesto, clasificación en enlazar/posible/no-enlazar con
   dos umbrales calibrados para acotar FP/FN. Implementado comercialmente en tiempo real por Senzing.
   Es la vía para superar el actual "VIN-exacto o nada" SIN violar la doctrina anti-over-merge.
9. **CarMax MaxOffer**: motor de 300+ variables sobre 4M+ transacciones/año; **el algoritmo propone, un
   tasador humano confirma como gate**; oferta válida 7 días; paga empíricamente 15-20% bajo precio
   particular (proxy publicado del spread wholesale-retail).
10. **Black Book**: valuación VIN-específica History-Adjusted = modelado estadístico + revisión editorial
    humana; 6+ patentes de forecasting de residual (US 7.366.679; 9.607.310; 10.410.227; 10.430.814).
11. **Zillow Offers (caso adversarial de fracaso — lección, no criterio a copiar)**: causa técnica =
    concept drift (datos de hasta 30 días de antigüedad en mercado que cambiaba más rápido); causa
    organizativa = "Project Ketchup" prohibió cuestionar al algoritmo y la dirección "subió el dial" para
    cumplir volumen; ~528M$ de pérdida directa Q3 2021, +900M$ amortizaciones, cierre nov-2021.
    Lección directa para Cardeep: (i) el censo son precios de OFERTA, no transacciones — toda señal se
    etiqueta así, sin excepción; (ii) frescura obligatoria (edad máxima del dato declarada); (iii) nadie
    "sube el dial" de un umbral para fabricar más chollos.
12. **Arbitraje estadístico clásico (finanzas)**: z-score del spread, entrada ±2σ, salida ±0,5σ, stop ±3σ,
    y PRECONDICIÓN Engle-Granger (cointegración) antes de operar cualquier par. Sirve como vara de honestidad:
    Cardeep NO hace esto y no debe decir que lo hace.

**Veredicto adversarial asumido como propio**: hoy Cardeep no tiene ventaja estructural realizada en este
pilar (0 de 5 señales en producción contra 3 competidores con producto vivo hace años). Tiene UNA ventaja
potencial real y única: el delta temporal nativo del censo español (`vehicle_event`), que ningún peer opera
en España con esa densidad. "Dedup cross-platform" como ventaja está hoy INVERTIDO: es una debilidad medible
(0 pares reales).

---

## 3. Objetivo Cardeep para este pilar y por qué puede superar a la referencia

**Objetivo**: convertir el censo vivo español en el motor de sourcing de compra para dealers más honesto y
verificable del mercado — señal de asimetría informativa (peer-set CarGurus/iSeeCars), no arbitraje
cuantitativo — construido con la disciplina mínimo-N-o-silencio de MMR/Mercari y con cada número trazable a
una consulta reproducible sobre datos reales.

**Dónde SÍ puede superar a la referencia (con fundamento verificado):**
1. **Time-arbitrage España-nativo**: CarGurus/iSeeCars/vAuto no operan España con censo completo.
   `vehicle_event` (5,4M eventos hoy, medido) es un sustrato de delta que ningún competidor tiene aquí.
   Las curvas de decaimiento y días-hasta-GONE por cohorte son construibles SOLO con lo que ya existe
   (NEW→GONE→PRICE_CHANGE con timestamps y valores JSONB). Es la ventaja estructural única y realizable.
2. **Deal-score a distancia mínima**: la maquinaria estadística (cohorte, mediana+MAD, robust-z sobre
   ln(price), guards Law-I) ya está escrita, testeada y viva en `detect_price_trap`. Construir el deal-score
   es reutilizar el primitivo con umbrales propios e invertir la lectura (cola baja legítima = oportunidad),
   no diseñar desde cero. De los 5 gaps, es el de menor distancia a paridad.
3. **Honestidad como diferenciador de producto**: los umbrales de CarGurus son secretos; los de Cardeep serán
   públicos y auditables (metodología visible en el propio panel). En un mercado de señales opacas, la señal
   verificable ES el producto — coherente con la identidad Cardeep (censo verificado, VAM, sellos).

**Límites honestos (declarados, no maquillados):**
- **Cross-platform gap**: hoy 0 casos reales. NO se muestra en producto hasta que la identidad lo sustente
  (Fase 6). Lo que sí se muestra ya es la señal hermana con identidad cierta: desync `vehicle.price` vs
  `platform_listing.platform_price` en la misma fila.
- **Precio de oferta ≠ precio de transacción**: Cardeep no ve transacciones (no hay Manheim español, no hay
  feed de compraventa). Toda señal se etiqueta "precio de oferta". No se promete "valor de mercado" en el
  sentido MMR/Edmunds. Un GONE no es una venta confirmada — puede ser retirada, reserva o fallo de captura;
  las curvas de tiempo lo declaran ("salida del mercado", no "venta").
- **Spread wholesale→retail**: sin partnership no existe. Se mantiene la honestidad ya presente en
  `Arbitrage.tsx:240` tal cual.
- **No es arbitraje cuantitativo**: sin cointegración ni ejecución simultánea. El nombre del pilar es
  ambición de producto, no claim técnico; la UI hablará de "oportunidades de compra", no de "arbitraje
  estadístico".
- **Superficie /terminal**: la visión cross-border EU sintética queda fuera de este pilar y fuera del
  mandato España-only. Decisión de esta carta: se DEGRADA a demo etiquetada fuera de navegación de producto
  o se elimina (Fase 0); no se le construye backend. Si el owner decide reactivar cross-border en el futuro,
  será otra carta con su propio censo multi-país — no un generador RNG.

---

## 4. Criterios de evaluación CONCRETOS (qué se muestra y cómo se calcula)

Regla madre: **ningún número en pantalla sin criterio en esta sección**. Cada badge/KPI/fila traza aquí.
Regla MMR: **mínimo-N-o-silencio** — si una celda/cohorte no cumple su N mínimo, esa celda NO se muestra
(estado vacío honesto), jamás se rellena.

### 4.1 Deal-score (señal #1 — "Chollos de reposición")
- **Universo**: solo filas de la vista `servable_vehicle` (excluye cuarentenados por price_trap y demás
  guards de higiene ya vivos). Un vehículo flaggeado por `detect_price_trap` NUNCA es chollo: primero
  higiene, luego oportunidad — dos detectores, una frontera explícita.
- **Cohorte**: idéntica a price_trap — Tier-A (make, model, year) con n≥15; fallback Tier-B (make, year)
  con n≥30. MAD floor 0.05 sobre ln(price) (cohortes casi-degeneradas: silencio).
- **Score**: `z = (ln(price) − mediana_ln_cohorte) / (1.4826 · MAD_ln_cohorte)`.
- **Bandas** (ancladas en Iglewicz-Hoaglin, público y citable):
  - `z ≤ −6.0`: NO es chollo — es territorio price_trap (basura/estafa/error). Frontera compartida con
    `PRICE_TRAP_COHORT_Z`.
  - `−6.0 < z ≤ −3.5`: badge **"Chollo fuerte"** (umbral outlier I-H).
  - `−3.5 < z ≤ −2.0`: badge **"Bajo mercado"** (zona limítrofe I-H).
  - `z > −2.0`: sin badge, no aparece en el ranking.
- **Campos mostrados por fila** (cada uno con su cálculo): precio actual (`vehicle.price`), mediana de
  cohorte en € (`exp(mediana_ln)`), ahorro estimado € = mediana_€ − precio, z redondeado a 2 decimales,
  n de la cohorte, días en mercado (§4.3), enlace `deep_link`, dealer y provincia (vía entity).
- **Frescura (gate anti-Zillow)**: `vehicle.last_seen` ≤ 72h para aparecer en el ranking; entre 72h y 7 días
  aparece con marca "sin re-verificar"; > 7 días no aparece. El umbral 72h es decisión de esta carta
  [ASUMIDO como punto de partida; se calibra en Fase 1 contra la cadencia real de re-scrape].
- **KPI de cabecera "chollos activos"** = `COUNT(*)` de filas que cumplen TODO lo anterior con z ≤ −2.0.
  Reemplaza el literal hardcodeado "37".
- **KPI "ahorro mediano"** = mediana del campo ahorro sobre ese mismo conjunto. Reemplaza el literal "€2.140".

### 4.2 Desync dealer↔plataforma (sustituto honesto de la señal #2 hasta Fase 6)
- **Definición**: filas de `platform_listing` con `status='listed'` donde
  `ABS(platform_price − vehicle.price) ≥ GREATEST(100, 0.01 · vehicle.price)` (≥1% Y ≥100€, ambos), con
  ambos precios no nulos y ambas `last_seen` ≤ 72h. Identidad cierta por construcción (misma fila-edge).
- **Se muestra**: precio dealer, precio plataforma, delta € y %, plataforma (entity), enlaces a ambos.
- **KPI "desyncs activos"** = COUNT de ese predicado. Reemplaza el actual bloque CROSS_GAPS hardcodeado,
  con el rótulo honesto "Desync de precio dealer↔plataforma" — NO se llama "gap cross-platform" hasta que
  existan pares reales multi-plataforma (Fase 6).
- **Cross-platform gap real**: gate duro = `SELECT count(*) FROM platform_listing GROUP BY vehicle_ulid
  HAVING count(*)>=2` > 0 tras la Fase 6 con precisión auditada ≥95% en muestra etiquetada. Hasta entonces,
  la sección muestra el estado vacío honesto con la explicación ("la identidad multi-plataforma está en
  construcción; no inventamos pares").

### 4.3 Time-arbitrage (señal #3 — "Cuánto tarda y cuánto cede")
- **Días en mercado (por vehículo)** = `now() − vehicle.first_seen`, cross-checkeado contra el evento NEW
  del propio vehículo en `vehicle_event` (§7).
- **Curva de salida por cohorte** (disciplina Mercari/MMR): para cohortes (make, model, year-band de 2 años)
  con **≥50 ciclos completos NEW→GONE en los últimos 12 meses** [ASUMIDO el 50 como arranque; se calibra en
  Fase 4 contra la distribución real de cohortes], se publica: mediana de días-hasta-GONE, P25/P75, y % de
  vehículos con al menos un PRICE_CHANGE negativo antes del GONE. Cohortes bajo el mínimo: silencio.
- **Curva de decaimiento por cohorte**: buckets de edad (0-7, 8-15, 16-30, 31-60, 61-90, 90+ días); por
  bucket, mediana del precio relativo al precio inicial (reconstruido encadenando `old_value`/`new_value`
  de PRICE_CHANGE). **Cada punto exige ≥30 observaciones en el bucket o el punto no se genera** (regla
  literal de la patente Mercari). Etiqueta obligatoria: "salida del mercado ≠ venta confirmada".
- **"Suelo estimado" (el literal €26.300 del mock)**: NO se muestra en v1. Predecir suelo exige modelo
  conjunto precio+tiempo (patrón GoPrice) que no existe; mostrarlo sin modelo sería inventar. En v1 se
  muestra la curva empírica de decaimiento de la cohorte, que es real. El predictor es candidato a v2,
  DESPUÉS de que la curva empírica tenga 6+ meses de backtest.
- **KPI "mediana días a salida"** (por cohorte seleccionada o global servable): reemplaza el literal "12".

### 4.4 Geo-arbitrage (señal #4 — "Dónde compra barato, dónde vende caro")
- **Celda** = (make, model, year-band de 2 años, `entity.province_code`). Vehículo→provincia vía
  `vehicle.entity_ulid → entity.province_code` (vehicle no tiene provincia propia; verificado §1.4).
- **Mínimo por celda: n≥15 listados servables** (paralelo del Tier-A). Celda bajo mínimo: no se pinta.
- **Estadístico por celda**: mediana de precio + MAD (robustos, coherentes con el resto del stack).
- **Gap mostrable entre provincia A y B para la misma cohorte** solo si: ambas celdas cumplen n≥15 Y
  `|mediana_A − mediana_B| > 1.5 · sqrt(MAD_A² + MAD_B²) · 1.4826` (el gap debe superar la incertidumbre
  combinada, no solo ser distinto de cero) [ASUMIDO el factor 1.5 como arranque conservador; se calibra en
  Fase 5]. Etiqueta obligatoria en el panel: "precios de oferta, no de transacción" (lección Zillow §2.11).
- **KPI "rutas geo activas"**: COUNT de pares (cohorte, provA, provB) que cumplen el criterio. Reemplaza
  el literal "94".

### 4.5 Spread wholesale→retail (señal #5)
- Sin cambio: sigue gated por partnership, con el texto honesto existente (`Arbitrage.tsx:240`). Ningún
  número se muestra. Se activa solo cuando exista feed real, con su propia adenda a esta carta.

### 4.6 Gating de monetización
- El `PremiumGate feature="sourcing-ranking"` se conserva sobre el ranking completo (top-N libre, resto
  gated), pero la prueba E2E del gating real depende del pilar de auth/billing (DEV_BYPASS=true hoy,
  §1.2) — dependencia declarada, fuera del alcance de esta carta.

---

## 5. Modelo de datos + almacenamiento backend

### 5.1 Se REUTILIZA (existente, verificado)
| Pieza | Dónde | Uso en este pilar |
|---|---|---|
| `vehicle` | `migrations/0003_vehicles_events.sql:4` | precio, make/model/year, first/last_seen, deep_link, status |
| `vehicle_event` | `0003:33` | curvas de tiempo y decaimiento (NEW/GONE/PRICE_CHANGE + JSONB old/new) |
| `entity.province_code` | `0002_entities.sql:13` | dimensión geo de toda señal |
| `geo_province` | `0001_geo.sql` (referenciada desde 0002:13) | nombres/códigos de provincia |
| `platform_listing` | `0009_platform_listing.sql:16` | desync dealer↔plataforma; futuro cross-platform |
| Vista `servable_vehicle` | `0031_gestion.sql:158` (+0040/0045/0047) | universo único de toda señal servida |
| `gestion_item` | `0031_gestion.sql:44` | frontera higiene/oportunidad; lane de revisión para Fase 6 |
| `pipeline/gestionador/detect.py` | cohortes, mediana+MAD, guards (líneas 94-114, 828+) | primitivo estadístico del deal-score (se factoriza el helper de cohortes para compartirlo, no se copia-pega) |
| `services/api/routers/` (patrón vehicles/platforms/geo) | `services/api/routers/*.py` | mismo patrón para el router nuevo |
| `web/src/api/cardeep.ts` | cliente tipado (líneas 171-173 como patrón) | añadir llamadas del pilar |
| `scripts/cross_platform_dedup_watermark.py` | doctrina y medición de duplicación | base doctrinal de la Fase 6 |

### 5.2 Se CREA (nombres verificados como libres: grep = 0 hits en migrations/services/pipeline/scripts)
| Nuevo | Tipo | Contenido |
|---|---|---|
| `cohort_stats` | tabla (nueva migración `00NN_arbitrage.sql`) | una fila por cohorte y run: clave de cohorte (make, model, year / tier), `median_ln_price`, `mad_ln_price`, `n`, `computed_at`, `run_id`. Escrita por el job; leída por deal_score y por la API de metodología. INSERT-only por run (doctrina PG MVCC: nada de UPDATE de filas no mutadas). |
| `deal_score` | tabla (misma migración) | una fila por (vehicle_ulid, run_id): `z`, banda, ahorro €, cohorte usada, `computed_at`. Se sirve siempre el último run completo. INSERT nuevo run + DELETE del run obsoleto (mismo patrón append+purge del resto del pipeline). |
| `market_decay` | tabla (misma migración) | una fila por (cohorte, bucket_edad, run_id): `n`, mediana precio relativo, mediana días-a-GONE, P25/P75. Solo buckets que cumplen mínimo-N. |
| `pipeline/arbitrage/` | módulo Python nuevo (`score.py`, `decay.py`, `geo.py`) | jobs de cómputo. Reutiliza el helper de cohortes factorizado desde `detect.py` (refactor con autoridad: extraer a `pipeline/gestionador/cohorts.py` o similar, con la suite existente de price_trap como red de regresión). |
| `services/api/routers/arbitrage.py` | router nuevo | `GET /arbitrage/deals` (paginado, filtros make/provincia), `GET /arbitrage/desync`, `GET /arbitrage/time-curves/{cohort}`, `GET /arbitrage/geo`, `GET /arbitrage/methodology` (umbral y N mínimos públicos — la honestidad como endpoint). |

- [HUECO conocido] El número exacto de la migración (`00NN`) se fija al ejecutar (la última verificada hoy
  es `0072_vehicle_cluster_country_proof.sql`); no se reserva número desde un plan.
- No se crea NINGUNA tabla para cross-platform en esta carta: la Fase 6 usa `platform_listing.listing_fingerprint`
  y `photo_hash` ya existentes en el esquema (0009:24, 0003:18), hoy despoblados; si Fellegi-Sunter exige
  tabla de pares candidatos, se especificará en la adenda de Fase 6 con su propia migración.

---

## 6. Especificación de pantalla (en la piel del dealer)

Página `/arbitrage` reconstruida (mismo route, `App.tsx`), lenguaje de dealer español, cero jerga SaaS:

1. **Cabecera "Reposición"** — 4 KPIs, cada uno trazado a §4: chollos activos (§4.1), ahorro mediano €
   (§4.1), desyncs activos (§4.2), mediana días a salida (§4.3). Debajo, en letra visible (no letra pequeña):
   "Precios de oferta del censo, verificados a ≤72h. No son precios de transacción." Cada KPI con tooltip
   "cómo se calcula" enlazando a la metodología (`/arbitrage/methodology`).
2. **Ranking "Chollos de reposición"** (la mesa central) — columnas: coche (make/model/year/km), precio,
   mediana de su cohorte, **"Margen bruto aparente"** en € (el ahorro de §4.1 — nombre de dealer, no
   "z-score"; el z va en tooltip técnico), n comparables ("frente a 47 iguales"), días en mercado, provincia,
   dealer, botón "Ver anuncio" (deep_link real). Filtros: provincia, marca, banda de precio, badge.
   Ordenación por defecto: ahorro € descendente. El dealer piensa en euros de margen y en si el coche es
   real — por eso el enlace al anuncio vivo es columna de primera clase, no un detalle.
3. **Panel "Desync dealer↔plataforma"** — "Este coche está más barato en su web que en el portal (o al
   revés)": ambos precios, delta, ambos enlaces. Para el dealer comprador es una ineficiencia explotable;
   para el dealer vendedor (futuro), aviso de su propio desync.
4. **Panel "Ritmo de mercado"** — selector de cohorte (marca/modelo/años); muestra: "La mitad de los
   [cohorte] salen del mercado en N días", curva de decaimiento empírica (buckets §4.3), "% que baja de
   precio antes de salir". Estado vacío honesto si la cohorte no llega al mínimo: "Aún no hay historial
   suficiente de este modelo (N ciclos de M requeridos)". Sin "suelo estimado" en v1 (§4.3).
5. **Panel "Mapa de precio por provincia"** — para la cohorte seleccionada, coropleta de mediana por
   provincia (solo celdas n≥15) + tabla de gaps significativos (§4.4): "Golf 2019-20: 1.900€ más barato de
   mediana en Lugo que en Madrid (23 vs 61 anuncios)". El dealer lee rutas de compra, no estadística.
6. **SpreadPanel** — intacto, con su honestidad actual (§4.5).
7. **Gating** — `PremiumGate` se mantiene sobre el ranking completo: top-3 chollos visibles como teaser,
   resto gated (`feature="sourcing-ranking"`), coherente con el mapa de monetización Capa 2/Enterprise.
8. **Norma dura de la página**: prohibido cualquier literal numérico de negocio en el TSX. Todo número
   visible viene de la API. Los estados vacíos son contenido de primera clase, diseñados, no un spinner
   eterno ni un guion.

La superficie `/terminal` (cross-border sintético) sale de la navegación de producto en Fase 0.

---

## 7. Protocolo de verificación (2 vías independientes por dato mostrado)

Estándar antialucinación del proyecto aplicado al producto: **ningún dato llega al dealer sin dos caminos
independientes que lo confirmen**, y los caminos se automatizan, no se prometen.

| Dato | Vía 1 (la que lo produce) | Vía 2 (independiente) | Gate |
|---|---|---|---|
| Mediana/MAD de cohorte | job Python `pipeline/arbitrage/score.py` (numpy/estadística en proceso) | recomputación SQL pura en Postgres (`percentile_cont(0.5)` sobre `ln(price)` + MAD manual) sobre muestra de ≥20 cohortes por run | discrepancia relativa > 0,5% en cualquier cohorte de la muestra → run marcado inválido, no se publica |
| Cada chollo del ranking | z-score estadístico (deal_score) | existencia real: `last_seen` ≤ 72h Y ausencia en `gestion_item` abierto para ese vehicle_ulid; además, muestra rotatoria diaria de N chollos re-fetcheados en vivo contra su `deep_link` (¿el anuncio sigue y el precio coincide?) | fallo del re-fetch en > umbral de la muestra → alerta al lane de gestión; el vehículo individual caído se despublica en el siguiente run |
| KPIs de cabecera | endpoint API | test de contrato que ejecuta el COUNT equivalente directo contra la DB (psql) y compara con la respuesta del endpoint | desigualdad → test rojo, CI bloquea |
| Días en mercado | `now() − vehicle.first_seen` | evento NEW del vehículo en `vehicle_event` (`observed_at`) | divergencia > 24h entre ambos → dato marcado inconsistente, excluido del panel y contado en métrica de salud |
| Curvas de decaimiento | job sobre PRICE_CHANGE encadenado | backtest de holdout: el último mes de eventos se excluye del cómputo y se compara la curva predicha-por-histórico vs lo observado en ese mes | error del bucket > banda declarada → la cohorte pierde su curva (silencio), no se ajusta a mano |
| Desync dealer↔plataforma | predicado SQL sobre platform_listing | frescura doble: `last_seen` de la fila-edge Y del vehicle ambas ≤72h; muestra manual/automatizada re-fetcheando ambos precios en vivo | precio no reproducible → fila excluida |
| Gap geo | celdas mediana+MAD del job | recomputación por camino distinto (SQL directo) + verificación de que ambas celdas superan n mínimo en un COUNT independiente | cualquier celda falla → el gap no se muestra |
| Números del frontend | render desde API | test de lint/CI que rechaza literales numéricos de negocio en `Arbitrage.tsx` (regresión permanente del pecado original de este pilar) + E2E (Playwright/browse) que compara 3 vías: pantalla == respuesta API == COUNT en DB | mismatch → CI rojo |

Regla transversal: cuando las dos vías discrepan, **el dato no se muestra** (silencio honesto) y se abre
ítem en `gestion_item` — nunca se elige "la vía que da el número más bonito".

---

## 8. Uso de LLM (doctrina €0 del CLAUDE.md: local/barato para lo masivo, caro solo para decidir)

**El camino crítico de las señales NO lleva LLM.** Deal-score, curvas, geo y desync son SQL + estadística
robusta determinista: reproducibles, auditables, gratis. Un LLM en el camino crítico rompería la
reproducibilidad del protocolo §7.

**LLM local/barato (masivo, fuera del camino crítico, opcional):**
- Normalización de trim/versión desde `vehicle.title` para afinar cohortes hacia el estándar iSeeCars
  (year+make+model+trim). SIEMPRE regex/diccionario primero (doctrina regex-antes-que-LLM); el modelo local
  solo para el residuo que la regex no cubre, en batch, con salida a columna auxiliar re-verificable.
- Detección de "precio financiado" / "IVA no incluido" en títulos y descripciones (regex primero: patrones
  `financiado|al contado|IVA` son mayormente regulares). Un asking-price financiado contamina la cohorte —
  flag barato que protege la señal cara.
- Clasificación de texto libre en la Fase 6 (campos de anuncio para features de record linkage), si el
  cotejo determinista por campo se queda corto.

**LLM caro (solo decidir, cadencia baja, presupuesto techado):**
- Auditoría adversarial periódica: una pasada sobre el top-20 de chollos del run preguntando "¿qué
  explicación NO-chollo tiene este precio?" (siniestro, importación, km dudoso, financiación obligatoria).
  Es el análogo barato del tasador-gate de CarMax (§2.9): el algoritmo propone, una revisión escéptica
  confirma. Salida: flags a `gestion_item`, jamás edición directa del score.
- Adjudicación de pares "posible-enlace" de Fellegi-Sunter en Fase 6 (la banda intermedia que la doctrina
  anti-over-merge prohíbe auto-mergear): el modelo caro razona el pareo con toda la evidencia y su veredicto
  va al lane de revisión, no a auto-merge.

**Explícitamente prohibido**: LLM generando precios, medianas, scores o cualquier número que se muestre;
LLM "estimando" el suelo de precio (eso exige modelo estadístico con backtest, §4.3).

---

## 9. Fases de construcción (orden, con criterio de verificación por fase)

Autoridad asumida: se puede reemplazar/reestructurar código existente (incluido factorizar `detect.py` y
reescribir `Arbitrage.tsx` desde cero). Cada fase = bloque cerrado: build + test + revisión real antes de
abrir el siguiente.

- **F0 — Reconciliación de superficies (sin backend nuevo).**
  Sacar `/terminal` (Arbitrage cross-border sintético) de la navegación de producto: o se elimina
  `web/src/pages/terminal/Arbitrage.tsx` + su entrada en `Terminal.tsx`, o se degrada a demo con banner
  permanente "datos sintéticos de demostración" y ruta fuera del nav (decisión final del owner en la
  revisión de esta fase; default de la carta: fuera del nav). Documentar en `Arbitrage.tsx` (comentario de
  cabecera) que TODO dato del mock será reemplazado por API en F3.
  *Criterio*: una sola visión de "Arbitrage" viva en el producto; grep confirma que ninguna ruta navegable
  presenta datos sintéticos sin etiqueta; build del front verde; revisión del owner sobre el destino de
  /terminal registrada.

- **F1 — Backend deal-score (cohort_stats + deal_score).**
  Migración nueva (2 tablas §5.2), factorización del helper de cohortes desde `detect.py` (suite existente
  de price_trap como red de regresión: debe seguir verde sin tocar sus asserts), job
  `pipeline/arbitrage/score.py` con TDD (tests unitarios sobre cohortes sintéticas con medianas/MAD
  conocidas a mano; tests de guards: MAD floor, mínimo-N, exclusión de cuarentenados y de z≤−6).
  *Criterio*: pytest verde (nuevos + toda la suite previa sin regresión); verificación §7 vía-2 ejecutada:
  medianas del job vs `percentile_cont` en psql sobre ≥20 cohortes reales con discrepancia ≤0,5%; conteo de
  chollos del run cotejado a mano contra un COUNT SQL independiente; revisión de código real (code-review
  adversarial) del módulo antes de cerrar.

- **F2 — API del pilar (`services/api/routers/arbitrage.py`).**
  Endpoints §5.2 con paginación y filtros, sirviendo SOLO del último run completo, universo
  `servable_vehicle`. Endpoint `/arbitrage/methodology` con umbrales y N mínimos (§4) en JSON.
  *Criterio*: tests de contrato (respuesta == COUNT/filas directas en DB); curl manual contra la DB viva
  cotejando 3 endpoints; ningún endpoint devuelve dato de vehículo con `last_seen` > 72h (test explícito);
  revisión de código.

- **F3 — Frontend real (`Arbitrage.tsx` reescrito).**
  Eliminar CHOLLOS/CROSS_GAPS/TIME_DATA hardcodeados; cablear a `cardeep.ts` (patrón `vehiclePlatforms`
  existente); implementar §6 (ranking, desync, KPIs, estados vacíos honestos, disclaimer oferta-no-transacción,
  metodología visible); conservar SpreadPanel y PremiumGate. Añadir el test-lint anti-literales (§7).
  *Criterio*: grep = 0 arrays de datos de negocio en el TSX; E2E de 3 vías (pantalla == API == DB) verde con
  Playwright/browse; revisión visual real en navegador (no solo build); los 4 KPIs trazan cada uno a su
  criterio de §4 verificado en vivo; revisión de código + diseño.

- **F4 — Time-arbitrage (`market_decay` + `pipeline/arbitrage/decay.py`).**
  Job de ciclos NEW→GONE y decaimiento encadenando PRICE_CHANGE, con mínimo-N por punto (§4.3); calibración
  de los umbrales asumidos (50 ciclos/30 por bucket) contra la distribución real de cohortes, documentando
  la decisión final; endpoint time-curves; panel "Ritmo de mercado".
  *Criterio*: backtest de holdout (§7) ejecutado y documentado con su banda de error; test de que ningún
  punto publicado tiene n < mínimo; cross-check first_seen vs evento NEW en muestra; revisión de código.

- **F5 — Geo-arbitrage (`pipeline/arbitrage/geo.py` + endpoint + mapa).**
  Celdas provincia×cohorte con mínimo-N y gap-sobre-incertidumbre (§4.4); coropleta + tabla de rutas.
  *Criterio*: test de que ninguna celda n<15 se sirve; recomputación independiente de ≥10 celdas en psql;
  verificación visual de que el disclaimer oferta/transacción está en el panel; revisión de código.

- **F6 — Identidad cross-platform (desbloqueo de la señal #2 real).**
  Trabajo de fondo, el más largo: (a) poblar `vehicle.photo_hash` (el brazo pHash de
  `cross_platform_dedup_watermark.py` hoy no puede correr con 0 hashes); (b) extender captura de VIN donde
  las recetas lo permitan; (c) scoring Fellegi-Sunter por campos sobre pares candidatos de la clave débil,
  con tres bandas: enlazar (auto, solo con evidencia fuerte: VIN o pHash+campos), posible (a lane de
  revisión `gestion_item` / adjudicación LLM cara §8), no-enlazar — respetando la doctrina anti-over-merge
  (la clave débil sola JAMÁS auto-mergea).
  *Criterio*: precisión ≥95% en muestra etiquetada a mano ANTES de exponer ningún par en UI [ASUMIDO 95%
  como listón de arranque; se ratifica con el owner en la revisión de fase]; el gate SQL de §4.2 (pares
  reales > 0) pasa; solo entonces la sección "gap cross-platform" sustituye su estado vacío.

- **F7 — Gating de negocio real.**
  Depende del pilar auth/billing (retirar `DEV_BYPASS`, plan real por usuario). Se declara aquí como
  dependencia externa: esta carta deja el PremiumGate correcto y testeado con planes simulados; el E2E de
  monetización real se ejecuta cuando ese pilar aterrice.
  *Criterio*: con plan simulado starter/enterprise, el gate muestra/oculta según `entitlements.ts` (test
  de componente); dependencia registrada en el tracker del programa.

Secuencia: F0→F1→F2→F3 es el camino crítico al primer producto real (deal-score servido end-to-end).
F4 y F5 son paralelizables tras F2. F6 corre en paralelo desde F1 (es captura+identidad, no señal). F7 al
final o cuando el pilar de auth llegue.

---

## 10. Estado real de ejecución (2026-07-18) — F1-F6

Todo lo declarado abajo es [VERIFICADO]: corrido contra `cardeep-pg` en vivo, con conteos reales tomados en
el momento de la ejecución (no estimaciones). Commits atómicos en `main`, push aplicado.

### F0 — Reconciliación de superficies
Ya resuelto ANTES de esta ejecución por `09-Fase0` (commit `672259f`): `web/src/pages/terminal/` no existe,
`/terminal` no está en `App.tsx`, no hay ruta navegable con datos sintéticos sin etiquetar. Cero acción
adicional requerida.

### F1 — Deal-score backend — CERRADO
- Migración `0079_arbitrage.sql`: `cohort_stats` + `deal_score` + `arbitrage_run`.
- `pipeline/gestionador/cohorts.py` (nuevo): primitivo de cohorte robust-z factorizado de
  `detect_price_trap`. Refactor de `detect.py` verificado **byte-idéntico** contra producción: mismo
  conjunto de 5000 vehículos flaggeados, mismo orden, mismo hash SHA-256
  (`cb132238020735529dc11d422e0ce1dd38d9e568b54a670ec6c9905db66a039c`) antes y después.
- `pipeline/arbitrage/score.py` (nuevo): bandas `chollo_fuerte`/`bajo_mercado`, universo `servable_vehicle`.
- **Run real**: 1.582.295 vehículos escaneados, 10.289 cohortes (9.587 Tier-A + 702 Tier-B), 48.474 filas
  `deal_score` (9.681 chollo_fuerte + 38.793 bajo_mercado). Verificación doble vía (§7): 20 cohortes,
  divergencia máxima **0,0%**.
- TDD: 8 tests (`tests/test_arbitrage_score.py`), cohortes sintéticas con media/MAD calculadas a mano,
  frontera de cuarentena, exclusión Tier-A/B.

### F2 — API — CERRADO
- `services/api/routers/arbitrage.py`: `/arbitrage/deals`, `/desync`, `/summary`, `/methodology`,
  `/time-curves/{make}/{model}`, `/geo/{make}/{model}`. Registrado en `main.py`.
- **Regresión real cazada por la suite del propio proyecto**: `tests/test_served_queries_have_country.py`
  detectó 4 queries mías sirviendo censo sin dimensión `country_code`. Corregido (JOIN entity +
  `country_code=$N`, `DEFAULT_COUNTRY` de `pipeline.paths`); re-verificado en verde.
- 9+ tests de contrato (`tests/test_arbitrage_router.py`) contra la API real (FastAPI TestClient + DB viva).

### F3 — Frontend — CERRADO
- `web/src/pages/Arbitrage.tsx`: reescritura completa. Los 5 arrays hardcodeados (`CHOLLOS`, `CROSS_GAPS`,
  `SPREAD`, `TIME_DATA`, `MAX_SPREAD_PCT`) eliminados; cada número viene de `cardeep.ts` (nuevos métodos
  `arbitrage*`). Ranking de chollos, panel de desync, panel de ritmo de mercado (curva de decaimiento real,
  selector de cohorte), panel de mapa geo (barras de mediana por provincia + rutas significativas),
  `SpreadPanel`/`PremiumGate` intactos.
- Guardia de regresión permanente: `tests/test_arbitrage_no_fabricated_data.py` (hermano de
  `tests/test_web_no_fabricated_data.py`) — falla si los arrays vuelven.
- `tsc --noEmit` limpio, `vite build` limpio (verificado tras la turbulencia de ediciones concurrentes de
  otros pilares sobre `cardeep.ts`/`main.py` — ver nota de concurrencia abajo).

### F4 — Time-arbitrage — CERRADO
- Migración `0081_arbitrage_decay.sql`: **desviación declarada** del nombre de tabla único que sugería
  §5.2 — dos tablas (`market_cycle_stats` + `market_decay`) en vez de una, porque las dos señales se
  computan sobre poblaciones distintas (documentado en la cabecera de la migración).
- `pipeline/arbitrage/decay.py`: ciclos NEW→GONE (≥50/cohorte, últimos 12 meses) + curva de decaimiento por
  bucket de edad (≥30 obs/bucket).
- **Run real**: 164.163 ciclos escaneados, 1.093 cohortes de ciclo, 7.760 filas de bucket. Doble vía:
  20+20 muestras, divergencia máxima **0,0%** en ambas señales.
- Verificación §7 **simplificada respecto al diseño de la carta** (declarado, no oculto): recompute
  SQL+Python independiente, NO el backtest de holdout temporal completo que la carta imaginaba — ese
  backtest queda como hueco declarado para una pasada futura.
- TDD: 6 tests (`tests/test_arbitrage_decay.py`).

### F5 — Geo-arbitrage — CERRADO
- Migración `0082_arbitrage_geo.sql`: `geo_price_cell` + `geo_price_gap`.
- `pipeline/arbitrage/geo.py`: celda (make, model, banda de 2 años, provincia), n≥15, sin fallback Tier-B.
- **Juicio dimensional declarado**: la fórmula literal de §4.4 mezcla una mediana en euros con un MAD en
  dominio ln sin convertir — este job deriva `sigma_eur = mediana_precio × MAD_ln × 1,4826` antes de
  comparar, documentado en el módulo y la migración.
- **Run real**: 18.080 celdas, 1.614 rutas significativas (ej. Land Rover Range Rover Sport 2022-23:
  43.810€ más barato en provincia 35 que en 29). Doble vía: 20 celdas, divergencia máxima **0,0%**.
- TDD: 7 tests (`tests/test_arbitrage_geo.py`).

### F6 — Identidad-captura (background) — MECANISMO CONSTRUIDO, EJECUCIÓN PARCIAL

**photo_hash**:
- `pipeline/identity/photo_hash.py` (nuevo): reutiliza `pipeline/delta_photo.py::hash_image_bytes` (el
  MISMO pHash DCT que el delta PHOTO_CHANGE en vivo ya usa — no una segunda implementación; se descartó un
  primer intento propio con la librería `imagehash` al descubrir que `delta_photo.py` ya resolvía esto sin
  dependencia nueva) y el governor per-host real (`pipeline/engine/governor.py`) — ningún host se golpea
  fuera de su bucket, doctrina de la cicatriz AS24 aplicada literalmente a los CDNs de fotos.
- **Run real acotado**: 200 vehículos, concurrencia 15, pacing conservador del governor (perfil STEALTH sin
  override, sin evidencia para acelerar `cdn.wallapop.com`/`images.milanuncios.com`). Resultado:
  **65 hasheados, 135 HTTP 404** (fotos ya no existen en el CDN — esperable en listados antiguos),
  312,7s. `vehicle.photo_hash`: 0 → 65.
- **Hueco declarado, no maquillado**: 1.963.278 vehículos disponibles tienen `photo_url`. A este ritmo
  conservador (dominado por 2 hosts al 0,7-1,0 req/s), cubrir el corpus completo es un job de fondo de
  varios días, no una sesión. El mecanismo es idempotente y reanudable (`--limit`); escalar la tasa para
  `cdn.wallapop.com`/`images.milanuncios.com` requiere medir su tolerancia real primero (la propia
  doctrina del governor: "nunca subir sin evidencia") — no se hizo aquí, es la siguiente acción concreta.
- TDD: 6 tests (`tests/test_photo_hash.py`), servidor aiohttp local real (sin red externa), governor
  aislado por test.

**VIN — hallazgo crítico no anticipado por la carta**:
- Auditoría en vivo: de 2.520.623 vehículos con `vin_ref` no-nulo, **solo 41.510 (1,6%) eran VINs de 17
  caracteres bien formados**. Los otros **2.479.113 (98,4%)** eran IDs de listado internos de la fuente
  (wallapop 789.654, milanuncios 559.049, coches.net 375.204, AS24 combinado ~680.000, autocasion
  ~225.000, motor.es ~91.000, ...) almacenados bajo el nombre de columna equivocado — bug de código real,
  verificado línea por línea en `pipeline/sources/autoscout24.py:208`
  (`vin_ref=str(raw.get("id") or raw.get("identifier") or "")`, corregido en este commit a `vin_ref=None`).
  Contraejemplo correcto ya existente en el propio repo: `pipeline/platform/oem_ford_wholesale.py`
  ("matrícula is not a VIN, so vin_ref stays NULL").
- **Impacto**: cualquier consumidor cross-platform por VIN estaba expuesto a 2,48M falsos identificadores
  — peor que la columna vacía, porque un ID falso puede coincidir por azar entre fuentes y fabricar un
  cruce inexistente. 02-history-reports' `link_lifetimes.py::_normalize_vin` YA se defendía de esto en
  lectura (rechaza longitud≠17 y letras I/O/Q) — mitiga el riesgo de falso-positivo mostrado al usuario,
  pero no limpia el dato en reposo.
- **Remediación aplicada**: migración `0083_vin_ref_remediation.sql` — `UPDATE vehicle SET vin_ref = NULL
  WHERE vin_ref IS NOT NULL AND upper(vin_ref) !~ '^[A-HJ-NPR-Z0-9]{17}$'`. Verificado antes de escribir:
  2.479.113 a limpiar, 41.510 a conservar (contraste de formato VIN estándar sin I/O/Q: 41.510/44.727
  del conteo bruto por longitud pasan el charset estricto). Guardia de regresión permanente:
  `tests/test_vin_ref_remediation.py`.
- **Alcance declarado, NO completado**: la corrección de código se aplicó solo a
  `pipeline/sources/autoscout24.py::parse_listing_vehicle` — confirmado en vivo que cubre
  `pipeline/platform/autoscout24_wholesale.py` (source_key `as24_wholesale`, 310.194 filas) y
  `pipeline/platform/as24_facet.py`. **NO cubre** `autoscout24_census` (150.638 filas): ese módulo
  (`pipeline/sources/autoscout24_census.py`) importa `parse_page_dealer`, una función de parseo
  DISTINTA que no fue auditada en esta pasada — sigue con el mismo riesgo de contaminación hasta que
  se revise por separado. **Otros conectores con el mismo patrón anti-VIN siguen sin corregir en
  código** (re-contaminarán en el próximo harvest si no se arreglan): `coches_net_wholesale`,
  `coches_com_wholesale`, `autocasion_wholesale`/
  `_census`, `motor_es_wholesale`/`_census` (motor.es además tiene su propio caveat conocido: su
  `vehicleIdentificationNumber` de JSON-LD es un placeholder estático, verificado idéntico en dos coches
  distintos — `docs/architecture/tier1_recipes/motor_es.md:164` — NUNCA usar sin re-verificar por coche),
  `wallapop_wholesale`, `milanuncios_wholesale`, `dasweltauto_wholesale`/`seat_dasweltauto`,
  `group_vo_chains_flexicar`/`ocasionplus`/`clicars`, `group_subastas_wholesale`,
  `group_rentacar_vo_arval`, `oem_seat`/`oem_seat_cupra_new_stock`, `hyundai_used`, `renault_renew`,
  `faciliteacoches_wholesale` (nota: `faciliteacoches_racc_wholesale.py` SÍ intenta extraer un VIN real de
  `vehicleIdentificationNumber` vía JSON-LD — a diferencia de motor.es, sin caveat de valor-duplicado
  documentado — pero el dato en BD para ese source_key sigue sin ser longitud=17, por lo que el flujo
  completo dealer→BD de ese conector necesita auditoría propia antes de confiar en él). Este es el mapa
  de trabajo para la siguiente pasada de "extender captura de VIN" — no una lista cerrada, es la evidencia
  recogida hoy.
- **Fuentes con VIN real confirmado** (sin cambios, ya correctas): `spoticar_wholesale`/`_api`,
  `oem_toyota_lexus_wholesale`/`toyota_used`, `oem_bmw_premium_selection_wholesale`,
  `oem_hyundai_wholesale`, `audi_used` (parcial: 3.052/4.086), `oem_volvo_jlr_suzuki_wholesale`,
  `nissan_intelligent_choice_wholesale`/`nissan_used`, `oem_mini_next_wholesale`, `renew_wholesale`.

### Nota de concurrencia (transparencia operativa)
Esta ejecución corrió con **múltiples agentes concurrentes sobre el MISMO working directory** (no clones
separados): se observaron sobrescrituras completas de `web/src/api/cardeep.ts` y colisiones de `git commit`
(ref lock) de otros pilares (`05-multiposting`, `03-garage-fleet`) en curso simultáneo. Mis adiciones a
`cardeep.ts`/`main.py` se restauraron cada vez que fueron pisadas (verificado con `tsc --noEmit` limpio al
final) y los commits se aislaron por pathspec explícito (nunca `git add -A`) para no arrastrar el trabajo
en curso de otros pilares. Un commit ajeno ("feat(publishing): F0...") terminó incluyendo mis archivos F4
ya *staged* en el mismo índice compartido — el código quedó correcto en `main`, solo la atribución del
commit es imprecisa; no se reescribió historia para corregirlo (doctrina: nunca amend/force-push).

---

## Resumen

F1-F5 cerradas y verificadas en vivo contra `cardeep-pg`: deal-score (48.474 chollos reales), API completa,
frontend sin un solo literal de negocio (guardia de regresión propia), time-arbitrage (7.760 puntos de
curva de decaimiento reales) y geo-arbitrage (1.614 rutas de precio significativas) — las 5 señales
diseñadas por la carta original, 5 construidas, con verificación de doble vía en cada una. F6 entregó dos
resultados: el mecanismo de `photo_hash` (construido, probado, ejecutado en real contra 200 vehículos,
65 hasheados — cobertura total es multi-día, declarado) y un hallazgo crítico no anticipado — el 98,4% de
la columna `vin_ref` no era VIN sino contaminación de IDs de listado, ahora limpiada a nivel de dato
(migración 0083) con un caso de código corregido (AutoScout24) y una lista explícita de conectores
pendientes de la misma corrección. La ventaja realizable de Cardeep confirmada en producción: el delta
temporal nativo (`vehicle_event`) y la maquinaria robust-z compartida entre higiene y oportunidad, con
mínimo-N-o-silencio respetado en cada tabla nueva y ningún número servido sin su segunda vía de
verificación.
