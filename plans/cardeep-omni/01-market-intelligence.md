# Carta de sub-proyecto — Pilar 01: Inteligencia de mercado ("la biblia del automovilístico")

> Programa: cardeep-omni · Clave: `01-market-intelligence` · Fecha: 2026-07-17
> Fase: SYNTHESIS (arquitectura). Este documento es la fuente de verdad del pilar
> hasta que una fase de ejecución lo enmiende con evidencia nueva.
> Doctrina aplicada: antialucinación tolerancia cero — cada afirmación lleva
> [VERIFICADO] (leída en código/DB/doc real, con archivo:línea) o [ASUMIDO]
> (declarada como suposición, jamás disfrazada de certeza).
> RECON base: 2026-07-16 (stack vivo: `docker ps` → cardeep-pg Up; `curl :8090/health` → `{"status":"live","db":"ok"}`).
> Pasada de re-verificación de anclajes: 2026-07-17 — 18 endpoints (`@router.get` con línea exacta), migraciones `0002`/`0003`/`0009`/`0023`, conteos `wc -l` del código huérfano (corrige la cifra "~2.500 líneas" del RECON: son **7.597 medidas**) y reconciliación con la carta hermana `09-trading-terminal.md` (custodia del motor de indicadores).
> Segunda pasada RESEARCH (2026-07-17, tarde): integrado el barrido adversarial de 19 referencias — añade KBB/NADA, TrueCar, J.D. Power ALG, Carfax HBV, AUTO1, GT Motive/Cesvimap y criterios exactos adicionales de MMR/vAuto/CarGurus/Indicata/Cazana/GANVAM. Anclajes re-verificados en esta pasada por vía independiente: `wc -l` 7.597 ✓, última migración `0072_vehicle_cluster_country_proof.sql` ✓, `entities.py:83 available_inventory` ✓.

---

## 1. Estado actual

El pilar vive hoy en **dos capas totalmente desconectadas**: una capa de investigación real y sólida, y una superficie de producto que es 100% atrezzo. No hay ni un solo dato de mercado real llegando al usuario.

### Capa A — Investigación de mercado: REAL y densa [VERIFICADO]

- **693 empresas** descubiertas en `plans/intel-audit/UNIVERSE.json` (conteo verificado por script en RECON). [VERIFICADO]
- **109 auditorías al átomo** multi-fuente en `plans/intel-audit/companies/*.md` (109 ficheros contados con `ls`). [VERIFICADO]
- `plans/intel-audit/MATRIX.md` — 6.225 líneas, cabecera declara derivación de las 109 auditorías, 3.131 campos atómicos. [VERIFICADO cabecera + grep]
- `plans/intel-audit/PLACEMENT-MAP.md` — 4.095 líneas, 1.353 patrones de colocación por campo (grep confirma densidad real, no relleno). [VERIFICADO]
- `plans/intel-audit/CARDEEP-OFFERING.md` — estrategia de 3 capas (Baseline / Diferenciadores / Premium) + `ARBITRAGE.md`. [VERIFICADO existencia y contenido]

### Capa B — Superficie de producto: 100% MOCK [VERIFICADO archivo por archivo]

- `web/src/pages/Inteligencia.tsx` (499 líneas, leída completa en RECON): TODOS los datos son constantes hardcodeadas (`MODELS`, `MARKETS`, `RESIDUAL_DATA`, `DAYS_DATA`, `DELTA_DATA`, `REGIONS`, `kpiCards`). Cero `fetch`/`axios`/hook de datos (grep confirmado). El commit `6309e11` (2026-07-16, "rebuild Inteligencia on real design-system + gating") migró UI a `Card`+tokens y aplicó `PremiumGate` según `plans/frontend-definitivo/05-MONETIZATION-MAP.md` — pero su diffstat confirma que fue migración de UI/gating, **no de datos**. [VERIFICADO]
- `web/src/pages/landing/IntelligenceTeaser.tsx:` el propio comentario del código confiesa: *"No fabricated valuation calculator: there is no live valuation endpoint (verified against `services/api/routers`), and `Inteligencia.tsx` itself runs on illustrative data."* [VERIFICADO — confesión en código]
- `web/src/pages/Api.tsx` expone un **catálogo de endpoints ficticio** (`GET /v1/valuation/{vin}`, `GET /v1/market/{model}`, `GET /v1/deal-score/{listing}`) que NO existen: `ls services/api/routers/` → solo `entities.py`, `geo.py`, `ops.py`, `platforms.py`, `vehicles.py` (re-verificado 2026-07-17). [VERIFICADO]
- `web/src/pages/Arbitrage.tsx` (368 líneas) y `web/src/pages/Analitica.tsx` (515 líneas): mismo patrón — arrays `CHOLLOS`/`SALES_DATA` hardcodeados, helpers `AnimNum`/`Spark` duplicados copy-paste desde `Inteligencia.tsx`. [VERIFICADO]
- **Sistema paralelo huérfano** (**7.597 líneas medidas** por `wc -l` 2026-07-17 — el "~2.500" del RECON era una subestimación): `web/src/pages/Terminal.tsx` (581) + `web/src/pages/Market.tsx` (992) + carpeta `web/src/pages/terminal/` (16 ficheros, 6.024 líneas: `market.ts` 417, `intelligence.ts` 312, `Intel.tsx` 149, `indicators.ts` 1.747, `indicators.test.ts` 433, `tools.ts` 967, `drawings.tsx` 502, resto UI). Técnicamente elaborado (RSI, SMA, Net Landed Cost, Seller Desperation Index, arbitraje DE/FR/ES/NL/BE/CH) pero: (a) la cabecera de `market.ts` lo declara *"Deterministic, seeded synthetic data... swap these generators for API calls"* — es un PRNG (`seedRng`/`hash`) sobre 18 instrumentos inventados (`SEEDS`), sin I/O; (b) modela un mercado multi-país que NO corresponde al alcance real del pipeline (España-only, `CLAUDE.md` del repo); (c) `/terminal` y `/market` están **fuera del nav** (`web/src/layout/Shell.tsx` solo lista `/inteligencia` y `/arbitrage`; confirmado por `plans/frontend-definitivo/PROGRESO.md:124` — "Market/terminal DeFi quedan fuera de nav"). Es código muerto que duplica el problema de datos, **con UNA excepción**: `indicators.ts`+`indicators.test.ts` (motor matemático real de 53 indicadores, testeado) está declarado pieza rescatable por la carta hermana `09-trading-terminal.md` — su destino lo decide el pilar 09, no este. [VERIFICADO]

### Backend — la MATERIA PRIMA existe, la capa de analítica NO [VERIFICADO]

- `migrations/0003_vehicles_events.sql:4-26` — tabla `vehicle`: `make`, `model`, `year`, `km`, `price NUMERIC(12,2)`, `fuel`, `transmission`, `photo_hash`, `status IN ('available','gone')` (líneas 21-22), `first_seen`/`last_seen` (23-24). [VERIFICADO]
- `migrations/0003:33-42` — `vehicle_event` **append-only**: `event_type IN ('NEW','GONE','PRICE_CHANGE','PHOTO_CHANGE','KM_CHANGE')` (37-38), `old_value`/`new_value` JSONB, `observed_at`. Índices por entidad+tiempo y por tipo (44-46). **Esto ES la base real del delta vivo que la oferta promete.** [VERIFICADO]
- `migrations/0002_entities.sql:13-15` — `entity.province_code CHAR(2) REFERENCES geo_province(code)`, `municipality_code`, `comarca_id`: el eje geográfico para segmentar mercado ya existe. [VERIFICADO]
- `migrations/0009_platform_listing.sql:16-30` — arista coche↔plataforma (`platform_price` :23, `listing_fingerprint` :24, `status` :25, `removed_at` :28; PK `(vehicle_ulid, platform_entity_ulid)` :29): la presencia multi-plataforma del mismo coche es expresable hoy. [VERIFICADO]
- `migrations/0023_vehicle_cluster.sql` — dedup de unidad física cross-plataforma (`vehicle_cluster_run` con gate `vam_verified`, `vehicle_cluster`, vista `v_canonical_vehicle`): el mecanismo para NO contar 3 veces el mismo coche listado en 3 plataformas ya existe. [VERIFICADO]
- Endpoints reales que sirven la materia prima a nivel individuo: `vehicles.py:24,71` (`/vehicles/{ulid}/history`, `/vehicles/{ulid}`), `entities.py:94,171` (`/entities/{cdp}/inventory`, `/entities/{cdp}/delta`), `geo.py:32,105,168,260,331,398` (cobertura de ENTIDADES por geografía — no demanda/precio). [VERIFICADO por grep de `@router.get`, 2026-07-17]
- **Búsqueda exhaustiva de agregación estadística** en `services/`, `pipeline/`, `migrations/`: percentiles solo aparecen en `pipeline/gestionador/detect.py` (detección de dedup, no producto) y `pipeline/price_sanity.py` (QC de datos, no producto). **CERO** módulo que calcule distribución de precio por segmento/geo, days-to-sell, price-position, demanda regional, curva residual o arbitraje. No existe `valuation.py`, `market.py`, `pricing.py` ni `intelligence.py` en routers. [VERIFICADO]

### Huecos estructurales (del RECON, confirmados)

1. Sin capa de cómputo de analítica de mercado en backend (ni servicio ni pipeline).
2. Sin days-to-sell / market-days-supply real (derivable de GONE, nadie lo agrega).
3. Sin price-position (el diferenciador #1 según `CARDEEP-OFFERING.md`) calculado en ningún sitio.
4. Sin curva residual real — `RESIDUAL_DATA` son 5 puntos inventados.
5. Sin demanda por región — `REGIONS` son 5 valores fijos, pese a que `geo.py` ya tiene el eje provincial.
6. Sin endpoints API para nada de lo anterior; catálogo de `Api.tsx` ficticio.
7. `PLACEMENT-MAP.md` (1.353 patrones) nunca aplicado sistemáticamente; `05-MONETIZATION-MAP.md` es una traducción manual de 4 widgets, no el mapeo del catálogo canónico.
8. 7.597 líneas huérfanas medidas (Terminal/Market/terminal-folder) modelando un mercado cross-border inexistente.
9. Deep-audit de las 584 empresas restantes (fork abierto (a) en `plans/intel-audit/README.md`) y canonicalización fina de MATRIX (PLAN.md) — pendientes, no bloqueantes.
10. **Hueco de RECON declarado**: el volumen exacto de filas en `vehicle`/`vehicle_event` NO se verificó por SQL directo (solo API+DB vivas). Se cierra en F0 — es la primera tarea de este pilar.

---

## 2. Investigación competitiva/adversarial

RESEARCH ejecutado en dos barridos adversariales con solape (15 + 19 referencias; unión = 21 filas en la tabla). Criterios EXACTOS extraídos — no genéricos:

### Referencias y sus criterios operativos exactos

| Referencia | Criterio exacto extraído |
|---|---|
| **Manheim MMR** (Cox) | Precio derivado EXCLUSIVAMENTE de transacciones de subasta reales, actualización diaria. Factor de depreciación por milla + kilometraje medio SEPARADO por vehículo. "MMR Range" = intervalo de confianza formal (70% de ventas similares caen dentro), no rango arbitrario. Desde jul-2024: ajuste VIN-específico por opciones OEM (~85% del volumen Manheim). **Ventana look-back DINÁMICA**: arranca en 30 días y se extiende hasta reunir mínimo **6 transacciones en el último año Y 2 en los últimos 90 días por trim** — el precedente directo de la regla `n<8` de §4. Recalculado cada noche (22:00–02:30 ET L-V + corrida de domingo); excluye títulos salvage/colisión/lemon-law. |
| **Black Book** | Ventas de +60 casas de subasta (parte verificadas presencialmente). 4 valores por vehículo (wholesale/trade-in/private-party/retail) con subcategorías por condición. Actualización semanal. |
| **CAP HPI** (UK) | 160.000 transacciones trade + 700.000 anuncios retail DIARIOS → 10M valores / 2.300 gamas / 70.000 derivados / 20 años. Metodología co-desarrollada con University of Leeds (validación académica externa). 3 niveles de condición (Clean/Average/Below). **Quality gate híbrido: cualquier movimiento >3% sobre el valor se marca en rojo automáticamente y un editor humano debe cerrar cada alerta antes de publicar.** |
| **DAT / Schwacke** (DE) | DAT = valor de mercado spot (ventas reportadas + datos maestros de dealer). Schwacke = valor RESIDUAL, comparación MENSUAL por tipo/fabricante/modelo cruzando anuncios + consultas dealer + evaluación estadística de matriculaciones/inventario/transferencias. **Lección: precio spot y residual son productos DISTINTOS con metodologías distintas.** DAT es propiedad de las asociaciones sectoriales alemanas (VDA/VDIK/ZDK, no un vendor privado) con canal ortogonal de datos de taller (Werkstattdaten); DAT Report anual ininterrumpido desde 1974. Schwacke: vehículo de referencia estandarizado en condición/km medios, fórmula exacta = secreto comercial, cerrada a consumidores desde feb-2020 (solo B2B). |
| **Autovista / INDICATA** | Suite de 5 productos separados (Inventory Mgmt / Lead Gen / Forecasting / Market Tracker / RV Tracker) — "valor actual" y "valor residual futuro" nunca son un único número. Reentrenamiento continuo + benchmark contra transacciones reales. Cadencia **SEMANAL** de revisión de todo el stock del dealer + revisión mensual con customer success; métrica central = **stocking days** (caso Dales Central Motors: 51→40 días en 2 años); metodología explícitamente híbrida (~400 analistas humanos + IA — el modelo puro no les basta). |
| **Cazana/Percayso** (UK) | El análogo estructural MÁS CERCANO a Cardeep: +800k VRN únicas/día, +1.000M anuncios vivos+históricos desde 2012, +12.000 fuentes **cruzadas con registros oficiales (DVLA/SMMT/MOT)** — combina listado con dato regulatorio. Cardeep hoy NO hace esa fusión. Hoy (como Percayso Vehicle Intelligence): 500M+ transacciones históricas en **40 países incluida España** — el competidor maduro ya declara pisar el mercado local (profundidad real de su censo español desconocida [ASUMIDO sin medir], pero prohíbe asumir el terreno vacío). |
| **S&P Global Mobility / Polk** | Base = 100% de transacciones derivadas de REGISTRO OFICIAL de matriculación, con "algoritmos propietarios para determinar CUÁNDO un vehículo cambia de titularidad". **No infieren venta por desaparición de anuncio: la verifican contra registro.** 32 países, VIN decoder 70+ atributos, 30+ años. |
| **CarGurus IMV + Deal Rating** | +70 puntos de datos por anuncio, recálculo diario, ajuste regional (oferta/demanda/clima/economía) y **ajuste de MOMENTUM** (el IMV sigue la dirección del mercado — serie con inercia, no snapshot). Deal Rating (Great/Good/Fair/High/Overpriced) = precio-vs-IMV primario + reputación dealer secundario; umbrales NO públicos (caja negra deliberada). Recalculado DIARIAMENTE sobre 1M+ listings propios; empareja contra "actualmente listados Y recientemente vendidos". Limitación reconocida por ellos mismos: sin historial de accidentes/mantenimiento (territorio del pilar `02-history-reports.md`). |
| **iSeeCars** | +960.000 ventas de vehículos 1-5 años. **Usa días-listados-en-su-propia-web como PROXY de días en mercado — lo ADMITEN explícitamente como proxy, no venta confirmada.** Exclusiones estrictas: descarta pesados, descontinuados, y modelos con <4 de los últimos 5 años-modelo en producción (anti-ruido de bajo volumen). |
| **vAuto Live Market View / Provision + MDS** (Cox, fundador Dale Pollak) | El precedente filosófico MÁS cercano a M2: `vRank` = **ranking percentil del precio contra unidades idénticas EN VIVO** del mercado local (no transacciones históricas) + `Price to Market %` (ej. 101% vs 97%); considera equipamiento y odómetro. Limitación: opera SOLO dentro del stock del dealer suscrito, nunca cross-plataforma nacional. MDS = fórmula estándar de la industria: `inventario disponible ÷ tasa media de venta retail diaria (ventana móvil ~45 días)`. **Exactamente derivable de `vehicle_event` NEW/GONE que Cardeep YA tiene y NO computa.** |
| **DGT Microdatos de Transferencias** (ES) | ÚNICA fuente de verdad transaccional oficial y abierta para España: dataset público, MENSUAL, ZIP descargable SIN autenticación (verificado por fetch directo en RESEARCH). Contiene fecha y registro de cambio de titularidad; **NO incluye precio**; desde 2025-02-01 el campo bastidor/VIN quedó restringido a interés legítimo justificado. GANVAM lo usa oficialmente (plataforma "Libro Mantenimiento"). |
| **GANVAM** | Boletines = inferencia estadística sobre muestra voluntaria de empresas + colaboración DGT. No es censo. Cierre 2025 (verificado vía búsqueda en RESEARCH): **2.218.824** turismos VO vendidos (+4,2%), antigüedad media del VO vendido **11,3 años** (>15 años entre particulares), precio medio **€17.654**, ratio VO/VN **1,9:1**, **57,3%** del mercado >10 años — ancla de reconciliación macro de este pilar (ver §7). |
| **coches.net / Adevinta** | Barómetro mensual = referencia mediática por defecto en España, pero UNA sola plataforma, sin dedup cross-platform, precio de oferta (no de venta). |
| **AutoScout24** | Única ingeniería pública verificable: Random Forest para predicción de precio (sustituyó un modelo lineal "por no capturar precios de mundo real"), R→Java, microservicio AWS con Continuous Delivery (Scout24 Engineering + ThoughtWorks). |
| **KBB / NADA Guides** (Cox / J.D. Power) | El ancestro directo del framing "biblia" (NADA desde 1933; KBB la 'biblia' retail histórica). KBB: "Typical Listing Price" (asking representativo asumiendo reacondicionamiento completo) + "Fair Purchase Price" (punto medio del Fair Market Range), actualización **SEMANAL**, 120+ regiones geográficas EE.UU. Lección de cadencia: semanal ya es INFERIOR al estándar vivo (MMR/CarGurus = diario) — el run de este pilar es diario, no semanal. |
| **TrueCar TruePrice** | Verdad de transacción RETAIL: mediana de transacciones reales a nivel VIN en el área metro, últimos 30 días (extensible a 8 semanas por estabilidad), vía integración DMS directa (CDK Global, Reynolds & Reynolds) con 10.000+ dealers franquiciados. "Great Price" = **percentil 25 de transacciones recientes**. Badge de dealer certificado con SLAs: ≥90% del inventario con precio transparente, precio cotizado honrado 72h, respuesta a leads <30min. Terreno inaccesible sin integración DMS — refuerza el límite honesto §3.1. |
| **J.D. Power ALG** | Forecast de valor residual **24-60 meses ADELANTE** (no valor spot); informa ~40% de lanzamientos de VN en Norteamérica y casi todo el leasing de EE.UU.; Model 8.0 (EVs) incorpora telemetría real de batería vía Recurrent (~1.000M millas observacionales). Cardeep no tiene capa de forecasting ni fuente ortogonal — M6 fase 2 es trayectoria observada, jamás se venderá como forecast. |
| **Carfax History-Based Value** | Ajuste del valor genérico de mercado por historial ESPECÍFICO del VIN (accidentes/mantenimiento/nº propietarios; reclama 100.000+ fuentes / 20.000M registros). NO afiliado a KBB pese a la percepción común. Territorio del pilar `02-history-reports.md`, no de esta carta. |
| **AUTO1 Group / AutoHero / compramostucoche.es** | El listón real del arbitraje: base "Price Indicators" de ~6M transacciones mayoristas europeas CERRADAS en 10+ años + **flota logística propia** que ejecuta físicamente el arbitraje Sur→Centro/Norte; 60.000+ partners en 30+ países. Un "arbitraje" calculado solo sobre deltas de asking price, sin verdad de transacción ni capacidad de ejecución, es informativo, no competitivo — refuerza el descarte cross-border de §4 y acota la ambición del pilar `04-arbitrage.md`. |
| **GT Motive / Solera-Audatex + Cesvimap** (ES) | La categoría actuarial española: motor de coste de reparación y siniestro total usado en **11.500+ talleres y 80+ aseguradoras** (GT Motive/Audatex); Cesvimap (MAPFRE) = formador del estándar "valor venal" español (VN − depreciación por tablas Eurotax/DAT/Hacienda), cero dependencia de anuncios en vivo. Cardeep NO compite ahí (límite §3.5). |
| **MarketCheck** | Prueba de que el método operativo de Cardeep YA es playbook a escala: 84.000 concesionarios scrapeados + microsites OEM + clasificados, dedup a nivel VIN, 262M VIN únicos, 5.000M+ anuncios, actualización diaria, EE.UU./Canadá/UK. |

### Veredicto adversarial (honesto, sin maquillaje)

1. **Censo vivo + dedup cross-platform NO es método novedoso** — MarketCheck y Cazana lo operan a escala mayor. La ventaja de Cardeep aquí es **geográfica-temporal**: nadie lo hace exhaustivamente en España (ni coches.net, ni INDICATA, ni GANVAM). Ventaja de ejecución y cobertura regional, no de método.
2. **El delta GONE=vendido es el eslabón MÁS DÉBIL de la tesis** — la misma debilidad que iSeeCars admite. Las referencias con autoridad real (MMR, Polk, DGT) fundamentan la venta en un evento verificado por terceros, no en la desaparición de un anuncio (que puede ser retirada, expiración, cambio de plataforma o duplicado). Cardeep hoy NO cruza GONE contra la DGT.
3. **VAM** es equivalente al quality-gate de CAP HPI (±3% + editor humano) — requisito mínimo bien resuelto, no diferenciador.
4. **Lo que falta por completo es el negocio principal de las referencias más rentables** (CAP HPI, Schwacke, INDICATA RV Tracker, Black Book): valor residual futuro sobre datos reales. Cardeep tiene el INSUMO mejor que casi nadie (curvas de precio observables por unidad vía `vehicle_event`) y CERO producto encima.
5. **Days-to-sell / MDS**: trivialmente derivable de lo que ya existe, potencialmente MÁS preciso que vAuto (un solo dealer) o iSeeCars (una sola web) porque el GONE cross-platform captura la señal en todas las plataformas a la vez. Sin computar hoy.
6. **La categoría actuarial/peritación (DAT, Schwacke, GT Motive/Audatex, Cesvimap) es un negocio DISTINTO** — su autoridad se construye sobre datos de taller/siniestro y décadas de precedente legal como estándar de peritación, no sobre anuncios. Cardeep no tiene ni el dato ni el estatus institucional, y perseguirla sería un error de alcance: este pilar es inteligencia de mercado para comprador/vendedor/dealer, no peritación.
7. **El forecasting de residual con fuente ortogonal (ALG + telemetría Recurrent) y el ajuste por historial VIN (Carfax) son ejes donde las referencias tienen datos que Cardeep estructuralmente no posee** y no puede replicar por software — se declaran fuera de esta carta (el historial es territorio del pilar `02-history-reports.md`; el forecast no tiene camino corto).

---

## 3. Objetivo Cardeep para este pilar — y el límite honesto

### La ventaja estructural real (latente, no realizada)

Nadie identificado en la investigación ha construido esta combinación para España:

> **(a) Censo cross-platform exhaustivo a nivel de anuncio individual** — cosa que ni GANVAM ni la DGT tienen — **fusionado con (b) el registro oficial de transferencias de la DGT** — cosa que ni MarketCheck, ni CarGurus, ni iSeeCars, ni coches.net hacen.

Esa fusión convierte el "presuntamente vendido" (proxy débil) en "estadísticamente corroborado" (cohorte contrastada contra titularidad real). Mientras no exista en código, la ventaja es [ASUMIDO], no [VERIFICADO]. **Construirla es el objetivo central de este pilar.**

### Límites honestos (lo que NO vamos a fingir)

1. **No tenemos precio de transacción.** La DGT no publica precio y no hay subasta. Todo precio Cardeep es precio de OFERTA observado. Etiqueta obligatoria en producto: "precio anunciado", jamás "precio de venta". MMR/Black Book (subasta) y TrueCar (retail vía DMS) seguirán siendo superiores en verdad transaccional de precio — ese terreno no se disputa sin integración DMS/subasta, que no existe hoy.
2. **GONE ≠ venta a nivel de unidad.** Sin VIN abierto en microdatos DGT (restringido desde 2025-02-01), la corroboración es de COHORTE (provincia+marca+modelo+mes), no de coche individual. El producto lo dirá así.
3. **Residual/forecasting requiere profundidad histórica longitudinal.** El span real de `vehicle_event` se mide en F0; hasta conocerlo, la curva residual se construye cross-sectional (cohortes de edad en el snapshot vivo) con etiqueta honesta, no como forecast Schwacke-style.
4. **España-only.** Todo el universo cross-border DE/FR/NL/BE/CH del Terminal huérfano se elimina — modela un alcance que el pipeline no tiene.
5. **No competimos en peritación/actuarial.** El estándar legal de siniestro (DAT/Schwacke/GT Motive/Audatex/Cesvimap) se construye sobre datos de taller y precedente institucional de décadas — otra categoría de negocio, fuera de alcance a propósito.

### Objetivo operativo

Construir la **capa de cómputo de mercado** que hoy no existe (agregados desde `vehicle`+`vehicle_event`+`entity`+`v_canonical_vehicle`), servirla por API real, fusionarla con los microdatos DGT, y reconectar la superficie `/inteligencia`+`/arbitrage`+`/analitica` a ella — retirando todo el atrezzo. Al cierre: **ni un número de mercado en frontend que no salga de la base viva y no trace a un criterio de la sección 4.**

---

## 4. Criterios de evaluación concretos — qué se muestra y cómo se calcula

Regla del pilar: **ningún número/badge/sección en frontend sin fila en esta tabla**. Cada widget renderiza además su `n` (tamaño de muestra) y su ventana temporal — sin excepción.

| ID | Elemento en UI | Cálculo exacto | Fuente / referencia adversarial |
|---|---|---|---|
| M1 | Distribución de precio por segmento ("¿a cuánto está el mercado?") | `percentile_cont(0.25/0.5/0.75)` de `vehicle.price` sobre unidades CANÓNICAS (`v_canonical_vehicle` del último run `vam_verified=TRUE`; si no hay run verificado → dedup por `photo_hash`+firma declarado como "sin verificar"), `status='available'`, `price IS NOT NULL`, filtrado por `price_sanity`. Segmento = `make`+`model`+banda de año (±1)+`fuel`+`province_code` (vía `entity.province_code`). **Regla dura: `n < 8` → "muestra insuficiente (n=X)", jamás un número** (patrón anti-ruido de iSeeCars). | `0003:13`, `0023` (vista `v_canonical_vehicle`), `0002:13`; estándar CAP HPI/MMR |
| M2 | Posición de precio de un anuncio ("¿estoy caro o barato?") | `ratio = price / p50(M1 del segmento del coche)`. Bandas iniciales: `<0.92` = "por debajo de mercado", `0.92–1.08` = "en mercado", `>1.08` = "por encima". **Los cortes son decisión de diseño inicial [ASUMIDO], calibrables en F5 contra la distribución real observada — al contrario que CarGurus, los umbrales se PUBLICAN en la UI (transparencia como diferenciador frente a su caja negra).** | Análogos exactos: vAuto `vRank`/`Price to Market %` (percentil contra unidades vivas idénticas — el precedente filosófico directo) + CarGurus Deal Rating; comparte motor con K9 de `03-garage-fleet.md` (se construye UNA vez, aquí) |
| M3 | Rotación: "días hasta retirada" por segmento | mediana de `(GONE.observed_at − vehicle.first_seen)` sobre eventos GONE del segmento, ventana móvil 90 días. **Etiqueta obligatoria: "días hasta retirada del anuncio", NUNCA "días hasta venta"** — hasta que M8 corrobore la cohorte. | `0003:33-42`; honestidad tipo iSeeCars (proxy admitido) |
| M4 | Market Days Supply por segmento ("¿cuánto stock hay respecto a lo que sale?") | `COUNT(available del segmento) ÷ (COUNT(GONE del segmento en 45 días) / 45)`. Ventana 45 días = estándar vAuto. `GONE en ventana = 0` → "sin rotación observada", no división por cero ni número inventado. | Fórmula vAuto MDS exacta; `0003` |
| M5 | Demanda/absorción por provincia (mapa) | `tasa de absorción = COUNT(GONE en 30d) / COUNT(available)` por `province_code`, sobre canónicos. Se muestra como ranking provincial + mapa. | `0002:13`, `0003:37-38`; sustituye el `REGIONS` inventado |
| M6 | Curva de valor por edad ("¿cómo pierde valor este modelo?") | **Fase 1 (cross-sectional):** `p50(price)` por cohorte de edad (`year` actual − `vehicle.year`, cohortes 0-1/1-2/2-3/3-5/5-8 años) del mismo `make`+`model` nacional. Etiqueta: "precios anunciados hoy por antigüedad", NO "depreciación proyectada". **Fase 2 (longitudinal, gated por F0):** trayectorias reales `PRICE_CHANGE` por unidad. | `0003:11,13,33-42`; lección DAT/Schwacke (spot ≠ residual: dos productos) |
| M7 | Momentum de precio por segmento | `Δ% = (p50 ventana 30d actual − p50 ventana 30d anterior) / p50 anterior`, sobre precios anunciados del segmento. Flecha + %; `n < 8` en cualquiera de las dos ventanas → no se muestra. | Análogo del momentum de CarGurus IMV |
| M8 | Corroboración DGT ("verdad de mercado") | `% de cohorte corroborada = transferencias DGT(provincia+marca+modelo+mes) / GONE Cardeep(misma cohorte+mes)`. Se publica como métrica de CALIDAD del dato ("nuestra señal de retirada está corroborada al X% contra registro oficial DGT") y como factor de confianza de M3/M4/M5. | DGT Microdatos (dataset abierto mensual, verificado en RESEARCH); estándar Polk (venta contra registro, no contra desaparición) |
| M9 | Índice de presión del vendedor por segmento | `% de unidades available con ≥1 PRICE_CHANGE descendente en 30d` + mediana del recorte acumulado (`old_value→new_value` de eventos `PRICE_CHANGE`). | `0003:37-41`; reconvierte honesta y España-only la idea "Seller Desperation Index" del Terminal huérfano |
| M10 | Presencia multi-plataforma del segmento | distribución de `COUNT(platform_listing)` por unidad canónica del segmento (¿cuántos canales usa el mercado para este coche?). | `0009:16-30`, `platforms.py:89` |

**Descartes explícitos:** "valoración por VIN" (`/v1/valuation/{vin}` de `Api.tsx`) queda PROHIBIDA hasta que exista un modelo con validación real — el catálogo de `Api.tsx` se corrige en F3 para listar solo endpoints existentes. "Arbitraje cross-border" (NLC del Terminal) se ELIMINA: sin datos multi-país no hay producto. `Arbitrage.tsx` se redefine como "oportunidades intra-España" = anuncios reales con M2 `ratio < 0.92` y `n ≥ 8` — chollos calculados, no `CHOLLOS` hardcodeados.

---

## 5. Modelo de datos + almacenamiento backend

### Se REUTILIZA (existe, verificado)

| Objeto | Rol en este pilar | Evidencia |
|---|---|---|
| `vehicle` | universo de precios anunciados, atributos de segmentación (`make`,`model`,`year`,`km`,`fuel`,`price`,`status`,`first_seen`) | `migrations/0003:4-26` |
| `vehicle_event` | serie temporal append-only: GONE (rotación), PRICE_CHANGE (momentum/presión), NEW (oferta entrante) | `migrations/0003:33-46` |
| `entity` | eje geográfico (`province_code`,`municipality_code`,`comarca_id`) y de tipo (`kind`) | `migrations/0002:8,13-15` |
| `geo_province` / `geo_municipality` / `geo_comarca` | dimensiones geo (referenciadas por FK desde `entity`) | `migrations/0002:13-15` (FKs); origen `0001_geo.sql` |
| `platform_listing` | multi-canal por unidad (M10), precio por plataforma | `migrations/0009:16-30` |
| `vehicle_cluster_run` / `vehicle_cluster` / vista `v_canonical_vehicle` | deduplicación de unidad física (anti doble-conteo en TODAS las métricas), con gate `vam_verified` | `migrations/0023` |
| `pipeline/price_sanity.py` | filtro de calidad de precio previo a cualquier agregado (ya existe como QC) | RECON (grep median) |
| Routers `entities.py`/`vehicles.py`/`geo.py` | siguen sirviendo el nivel individuo; NO se tocan | grep `@router.get` 2026-07-17 |

### Se CREA nuevo (nombres propuestos — NO existen hoy; numeración tras `0072`, última verificada por `ls migrations/`)

| Objeto nuevo | Contenido | Notas de diseño |
|---|---|---|
| `migrations/0073_market_stat.sql` → tablas `market_stat_run` + `market_stat` | `market_stat_run`: una ejecución del cómputo (id, ventana, versión de metodología, `n_in`, checks pasados, `published BOOLEAN DEFAULT FALSE`). `market_stat`: filas de agregado (run_id, metric_id M1-M10, claves de segmento `make/model/year_band/fuel/province_code`, `n`, `p25/p50/p75` o valor, `window_start/window_end`, `computed_at`). | Espejo del patrón `vehicle_cluster_run` (run + gate antes de servir). **Doctrina MVCC del proyecto: INSERT de run nuevo + DELETE de runs caducados; JAMÁS UPDATE de filas de agregado.** Los endpoints sirven solo el último run `published=TRUE`. |
| `migrations/0074_dgt_transfer.sql` → tablas `dgt_transfer_batch` + `dgt_transfer` | Ingesta cruda de los microdatos mensuales DGT: batch (mes, URL origen, hash del ZIP, filas) + filas normalizadas (fecha transferencia, provincia, marca, modelo, campos disponibles). | **[ASUMIDO] el esquema exacto de columnas del microdato — se confirma leyendo el diccionario de datos real de la DGT en F4, jamás antes.** Sin VIN (restringido desde 2025-02-01). |
| `migrations/0075_dgt_corroboration.sql` → tabla `dgt_corroboration` | Resultado de la fusión M8 por cohorte (provincia+marca+modelo+mes): `gone_count`, `dgt_count`, `ratio`, run_id. | Cohorte, no unidad — límite honesto §3. |
| `services/api/routers/market.py` | `GET /market/segments/{make}/{model}/stats` (M1,M3,M4,M6,M7,M9,M10 con filtros `province`,`fuel`,`year`), `GET /market/price-position/{vehicle_ulid}` (M2), `GET /market/provinces/demand` (M5), `GET /market/dgt-corroboration` (M8). Paginación y caché con el mismo patrón que `entities.py`. | Solo lee `market_stat` del run publicado — nunca agrega en caliente sobre `vehicle` (protege la DB viva). |
| `pipeline/market/` (módulo nuevo: `compute_stats.py`, `ingest_dgt.py`, `corroborate.py`) | Jobs batch: cómputo M1-M10 → `market_stat`; descarga+parse mensual DGT → `dgt_transfer`; fusión → `dgt_corroboration`. | SQL determinista (percentile_cont), cero LLM en el camino crítico (§8). |

**Compromiso antialucinación:** ninguno de los 5 objetos nuevos se cita en ningún otro documento como existente hasta que su migración esté aplicada y verificada. Los números de migración 0073-0075 se re-verifican contra `ls migrations/` en el momento de crear cada una (otra rama puede haberlos consumido).

---

## 6. Especificación de pantalla/sección en frontend

Principio: el dealer no quiere "un dashboard de analytics" — quiere respuestas a las 5 preguntas que se hace cada mañana con el café. Cada bloque responde UNA pregunta, en su idioma, y enseña siempre `n` + ventana + fecha de cómputo (credibilidad = transparencia, el anti-CarGurus).

### `/inteligencia` — reconstruida sobre datos reales (sustituye el atrezzo actual)

1. **"¿A cuánto está el mercado?"** — buscador de segmento (marca→modelo→año→combustible→provincia). Devuelve la banda p25–p50–p75 real (M1) como barra horizontal con el rango, mediana destacada, `n` visible ("sobre 143 anuncios vivos verificados"). Si `n<8`: estado vacío honesto — "Aún no hay muestra suficiente en tu provincia; te enseñamos el dato nacional (n=1.204)".
2. **"¿Cuánto tarda en salir?"** — M3 (mediana de días hasta retirada) + M4 (MDS) del segmento, con la etiqueta literal "días hasta retirada del anuncio" y un tooltip que explica el proxy y el % de corroboración DGT (M8) de esa cohorte. El dealer ve honestidad, no humo.
3. **"¿El mercado sube o baja?"** — M7 momentum del segmento (flecha + Δ% 30d vs 30d anteriores) + M9 presión del vendedor ("el 22% de los anuncios de este segmento ha bajado precio este mes; recorte mediano −4,1%").
4. **"¿Dónde se mueve?"** — mapa provincial M5 (tasa de absorción 30d), ranking de provincias del segmento. Sustituye el `REGIONS` inventado.
5. **"¿Cómo pierde valor?"** — curva M6 por cohortes de edad, etiquetada "precios anunciados hoy por antigüedad" (fase cross-sectional) hasta que la longitudinal esté gated.

### `/arbitrage` — redefinida España-only

Lista de anuncios reales con M2 `ratio < 0.92` y `n ≥ 8`, ordenados por descuento vs mediana del segmento, con deep link al anuncio (mandato del proyecto: deep links siempre) y la banda M1 al lado para que el dealer JUZGUE, no crea. Cada fila: precio, mediana provincial, ratio, días publicado, nº plataformas (M10).

### Integración con Pilar 03 (garaje/flota)

La ficha de vehículo del dealer consume `GET /market/price-position/{vehicle_ulid}` (M2) — es el K9 de `03-garage-fleet.md`, servido por el motor de ESTE pilar. Una sola implementación de comparables para ambos pilares.

### Retiradas

- `Terminal.tsx` + `terminal/*` + `Market.tsx` (7.597 líneas huérfanas medidas, universo sintético cross-border): **demolición COORDINADA con el pilar 09** (F6). Este pilar elimina del árbol todo el universo de datos sintéticos (`market.ts` con sus `SEEDS`, `Market.tsx`, `Terminal.tsx`, `intelligence.ts` — este último es además el artefacto tóxico `carNews()` que la carta 09 destruye en su Fase 0). **Excepción de custodia:** `indicators.ts` + `indicators.test.ts` (motor de 53 indicadores real y testeado) y, si el pilar 09 lo reclama, `tools.ts`/`drawings.tsx`, NO los borra este pilar — su destino (rescate con limpieza de marca o borrado) lo decide `09-trading-terminal.md`, que los tiene declarados como única pieza rescatable. Lo único que ESTE pilar rescata es la IDEA del índice de presión (M9), reimplementada sobre datos reales.
- `Analitica.tsx`: sus `SALES_DATA` mock se sustituyen por M3/M5/M7 del segmento o la página se fusiona en `/inteligencia` (decisión en F6 según redundancia real).
- `Api.tsx`: catálogo reescrito para listar SOLO endpoints existentes (los actuales + `market.py` cuando esté servido).
- Gating `PremiumGate` según `plans/frontend-definitivo/05-MONETIZATION-MAP.md` se conserva sobre los widgets reales.

---

## 7. Protocolo de verificación — cada dato por ≥2 vías independientes

El mismo estándar antialucinación del proyecto, aplicado al producto:

| Dato | Vía 1 | Vía 2 (independiente del camino que lo produjo) | Gate |
|---|---|---|---|
| Agregados M1-M7, M9, M10 de un run | SQL del job `compute_stats.py` (`percentile_cont` en PG) | Recomputo offline en Python puro (numpy/statistics) sobre un dump muestral del mismo segmento — comparación con tolerancia 0 para `n` y `<0.5%` para percentiles | Run no se marca `published` si difieren |
| Recuento de universo de un run | `market_stat_run.n_in` | `SELECT COUNT(*)` directo con los mismos filtros, lanzado por el verificador (proceso distinto) + contraste con `available_inventory` (campo agregado en `entities.py:83`, servido por el endpoint `/entities/{cdp}` de `entities.py:53`) para entidades muestreadas | idem |
| Salto entre runs consecutivos | comparación automática run N vs N-1 | **regla CAP HPI adoptada: cualquier métrica que se mueva >3% intersemanal se marca en rojo y exige cierre manual del Director (gate humano) antes de `published=TRUE`** — mismo patrón que `vam_verified` en `0023` | bloqueo de publicación |
| Señal GONE (base de M3/M4/M5) | `vehicle_event.event_type='GONE'` | corroboración de cohorte contra `dgt_transfer` (M8); cohortes con ratio fuera de banda esperada se marcan para inspección de recetas (¿scraper cayéndose ≠ coches vendiéndose?) | factor de confianza visible en UI |
| Ingesta DGT | hash del ZIP + recuento de filas del batch | re-descarga independiente del mismo mes y comparación de hash; totales contrastados contra las cifras públicas que la propia DGT/prensa publican del mes | batch inválido no entra |
| Agregados nacionales (sanidad macro) | agregados propios del run publicado (precio mediano nacional de oferta, distribución de antigüedad del censo, volumen de retiradas) | reconciliación MENSUAL contra las cifras públicas de GANVAM (ancla 2025: 2.218.824 uds vendidas, precio medio €17.654, antigüedad media 11,3 años, 57,3% >10 años) — la desviación se DOCUMENTA con causa explícita (oferta≠venta, censo≠ventas, cobertura de fuentes); una desviación inexplicable retiene la publicación del run y abre investigación | informe de reconciliación mensual escrito, adjunto al run |
| Frontend sin atrezzo | revisión de código | **gate CI: grep que PROHÍBE arrays de datos hardcodeados en `web/src/pages/{Inteligencia,Arbitrage,Analitica}*` (patrón `const [A-Z_]+ *[:=] *\[` con lista blanca explícita) + test E2E que verifica que cada número renderizado proviene de una respuesta de red del API real** | CI rojo si reaparece un mock |
| Fixtures de verdad conocida | dataset seed determinista (coches sintéticos con distribución conocida) en CI | los jobs deben devolver EXACTAMENTE los percentiles/medianas precalculados a mano en el fixture | test rojo = no merge |

Regla transversal: **todo widget muestra `n`, ventana y timestamp del run** — el usuario final tiene siempre los metadatos para desconfiar, igual que este proyecto desconfía de sus propios números.

---

## 8. Uso de LLM — doctrina de gasto del CLAUDE.md ("modelos locales para lo masivo y barato; la inteligencia cara, solo para decidir")

**Confesión de arquitectura: este pilar es ~95% SQL determinista y estadística clásica. El LLM NO está en el camino crítico de ningún número mostrado al usuario** (coherente con la doctrina del proyecto de mantener la IA fuera del camino crítico de indexación).

| Trabajo | Modelo | Justificación |
|---|---|---|
| Cómputo M1-M10, percentiles, ventanas | **CERO LLM** — SQL/`percentile_cont` + Python determinista | Un LLM aquí sería incompetencia: es aritmética |
| Parse de microdatos DGT | **CERO LLM** — es un dataset estructurado con diccionario de datos oficial; parser determinista + tests | idem |
| Normalización de variantes `make`/`model` (ej. "VW"/"Volkswagen", "Serie 3"/"320d") para que los segmentos no se fragmenten | Diccionario determinista PRIMERO; LLM **local/barato** (patrón ya establecido en el proyecto) SOLO para la cola larga de variantes no cubiertas, con salida escrita AL diccionario (el LLM alimenta la tabla, nunca responde en caliente) | masivo+barato = local |
| Clasificar cohortes DGT↔Cardeep ambiguas (matching de nomenclaturas marca/modelo entre ambas fuentes) | LLM local/barato, batch, con muestreo de validación humana | masivo+barato = local |
| Cambios de METODOLOGÍA (redefinir un cálculo M*, recalibrar los cortes de M2, decidir exclusiones de segmento) | **Modelo caro (Fable 5/Opus) como gate adversarial**, patrón ya probado en el repo (Sonnet construye, Opus gatea contra DB viva) | decisión irreversible de cara al usuario = inteligencia cara |
| Investigar anomalías señaladas por el gate ±3% | Modelo caro, bajo demanda, una vez por alerta | diagnóstico, no volumen |
| Redacción de explicaciones/tooltips de metodología en producto | Una vez, en fase de construcción, revisado a mano | coste marginal cero en runtime |

---

## 9. Fases de construcción (orden estricto; cada una con su criterio de verificación)

**F0 — Verdad de volumen (cerrar el hueco #10 del RECON).**
Medir por SQL directo: filas de `vehicle` (por status), filas de `vehicle_event` (por tipo), span temporal real (`MIN/MAX(observed_at)`, `MIN(first_seen)`), % de `price IS NULL`, % de coches con `make`+`model`+`year` completos, nº de runs `vam_verified` en `vehicle_cluster_run`, cardinalidad de segmentos con `n≥8`.
*Verificación:* cada número por 2 vías (SQL directo + recuento paginado vía API donde exista endpoint); resultados escritos en `plans/cardeep-omni/01-market-intelligence-f0.md`. **Gate de diseño: si el span de `vehicle_event` es < 90 días, M3/M4/M7 arrancan con ventanas reducidas declaradas en UI; si los runs `vam_verified` son 0, M1-M10 arrancan sobre dedup `photo_hash`+firma con etiqueta "sin verificar" — la decisión se toma con el dato, no antes.*

**F1 — Migración `0073_market_stat` + job `compute_stats.py` con M1 (distribución de precio).**
*Verificación:* migración aplicada+rollback probado; fixture seed con percentiles precalculados a mano (test rojo→verde); recomputo Python vs SQL sobre 5 segmentos reales con divergencia <0.5%; run de prueba con `published=FALSE`.

**F2 — M3, M4, M5, M7, M9, M10 en el mismo job + gate de publicación.**
*Verificación:* fixtures propios por métrica (incluye caso GONE=0 → "sin rotación observada", caso `n<8` → fila suprimida); implementado y probado el gate ±3% intersemanal con cierre manual; primer run real `published=TRUE` tras pasar el protocolo §7 completo.

**F3 — Router `services/api/routers/market.py` + corrección de `Api.tsx`.**
*Verificación:* tests de contrato FastAPI (patrón de los routers existentes) por endpoint, incluidos 404/muestra-insuficiente; OpenAPI generado refleja la realidad; `Api.tsx` reescrito sin un solo endpoint ficticio (revisión línea a línea); caché y paginación con el mismo patrón que `entities.py`.

**F4 — Ingesta DGT (`0074` + `ingest_dgt.py`) y corroboración (`0075` + `corroborate.py`, M8).**
Primera tarea: descargar el diccionario de datos REAL de la DGT y confirmar el esquema (el [ASUMIDO] de §5 se cierra aquí).
*Verificación:* 1 mes ingerido con doble descarga+hash idéntico; totales contrastados contra cifras públicas del mes; ratio de corroboración por cohorte computado y documentado con honestidad cruda (si sale bajo, se publica bajo y se investiga — no se maquilla).

**F5 — M2 (price-position) + calibración de cortes.**
*Verificación:* endpoint `GET /market/price-position/{vehicle_ulid}` con tests; distribución real de ratios analizada y cortes 0.92/1.08 confirmados o recalibrados con gate adversarial de modelo caro (§8); consistencia cross-pilar verificada con K9 de `03-garage-fleet.md` (mismo motor, mismos resultados).

**F6 — Reconstrucción del frontend + demolición coordinada del atrezzo.**
`/inteligencia` y `/arbitrage` reconectadas a `market.py` (spec §6); `Terminal.tsx`+`Market.tsx`+universo sintético de `terminal/` eliminados del árbol **salvo la pieza en custodia del pilar 09** (`indicators.ts`+`indicators.test.ts`, y `tools.ts`/`drawings.tsx` si 09 los reclama — se mueven o se dejan quietos según decida esa carta, jamás se borran desde aquí); decisión Analitica (fusionar o reconectar) tomada y ejecutada; gate CI anti-mock activo.
*Verificación:* grep CI en verde (cero arrays de datos hardcodeados); E2E que intercepta red y verifica que cada número visible proviene del API; regresión visual en 320/768/1024/1440; `PremiumGate` intacto sobre widgets reales; build de producción verde.

**F7 — M6 longitudinal (curva de valor por trayectorias reales) — GATED por el span medido en F0.**
Solo arranca cuando el histórico longitudinal dé para cohortes con `n≥8` por tramo.
*Verificación:* comparación cross-sectional vs longitudinal documentada; etiquetado del producto actualizado solo si la longitudinal pasa el protocolo §7.

Cada fase cierra con el patrón ya probado del repo: **Sonnet construye, gate adversarial (Fable 5/Opus) contra DB viva antes de dar el bloque por sellado.** Ninguna fase se declara "hecha" sin su criterio de verificación en verde y escrito.

---

## Resumen

El pilar tiene una investigación competitiva real (693 empresas, 109 auditorías, 3.131 campos) y una materia prima única (`vehicle`+`vehicle_event` append-only sobre censo cross-platform), pero HOY el 100% de la superficie de inteligencia es atrezzo hardcodeado y no existe ni una línea de cómputo de mercado en backend. La ventaja estructural defendible no es el censo (MarketCheck/Cazana ya lo hacen fuera) sino la fusión inédita para España de censo-a-nivel-de-anuncio con los microdatos abiertos de transferencias de la DGT — que convierte el proxy débil "GONE=vendido" en señal corroborada contra registro oficial. El plan: 8 fases (F0-F7) que construyen `market_stat`+`market.py`+ingesta DGT con verificación de cada número por dos vías independientes, gate humano estilo CAP HPI para publicar, cero LLM en el camino crítico, y demolición de las 7.597 líneas de mercado sintético huérfano (coordinada con el pilar 09, que custodia el motor de indicadores real). Nada se muestra al dealer sin `n`, ventana y trazabilidad a un criterio M1-M10 de esta carta.
