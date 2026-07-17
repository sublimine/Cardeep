# 09 — Terminal de trading estilo TradingView (técnico + fundamental)

> Carta de sub-proyecto institucional. Pilar `09-trading-terminal` del programa cardeep-omni.
> Fecha: 2026-07-17 · HEAD verificado: `7d494dc` (2026-07-16, "feat(web): rebuild Inventory on real dealer data, glass UI, and a 3D garage view") · Autor de síntesis: Fable 5 (fase PENSAR, cero código ejecutado).
> Doctrina: cada afirmación es [VERIFICADO] (leída en código/doc real, con archivo:línea) o [ASUMIDO] (declarado como tal, nunca disfrazado). Donde el recon previo quedó stale contra HEAD, esta carta lo corrige y lo señala.
> Pasada 2 (2026-07-17): re-verificación integral de TODAS las citas archivo:línea contra HEAD `7d494dc` — todas confirmadas salvo una corrección factual (§1.4: 18 endpoints, no 16) — y fusión de la segunda pasada de RESEARCH (15 referencias) en §2, §3, §4 y §7 con proveniencia A/B etiquetada.
> Pasada 3 (2026-07-17, sesión independiente): HEAD sin mover (`7d494dc`); re-verificados uno a uno los anclajes de carga — `intelligence.ts:266/:282`, `Market.tsx:26/:210/:619-631`, `App.tsx:18-19/:86-87`, `Shell.tsx:20/:170/:555`, `0003:33-46`, `0002:13-15`, `0023:31`, `0004:34`, `entities.py:171`, `vehicles.py:24`, `ops.py:26/:48/:91/:101/:156`, blueprint `:210`, `package.json:34/:37/:43`, 16 ficheros `terminal/`, 53 indicadores, 14 consumidores de `api/cardeep` en `inventory/`, última migración `0072` — cero divergencias. El recon entrante de esta pasada traía dos datos stale (14 ficheros; "solo 3 consumidores de landing") ya corregidos en §1.1/§1.3: esta carta prevalece sobre ese recon.

---

## 1. Estado actual

**Veredicto: existen DOS terminales muertos (100% datos sintéticos, fuera del nav, un solo commit de vida cada uno), CERO capa de agregación de mercado en backend, y un motor matemático de indicadores real y testeado enterrado dentro del cadáver. El pilar es net-new en su núcleo (índice de precio + fundamental), con UNA pieza rescatable.**

### 1.1 Frontend — dos implementaciones paralelas, ambas huérfanas — [VERIFICADO]
- `/market` → `web/src/pages/Market.tsx` (992 líneas, `wc -l` esta sesión) — terminal DeFi antiguo, autocontenido, acento violeta (`Market.tsx:26` — `const UP = '#a78bfa', DN = '#f87171'`; más violeta en `:210,:619,:627,:631`), datos hardcodeados + generador RNG sembrado propio. Cero código compartido con Terminal.tsx.
- `/terminal` → `web/src/pages/Terminal.tsx` (581 líneas) + carpeta `web/src/pages/terminal/` (**16 ficheros**, contados por `ls` esta sesión — el recon decía 14, corregido): `market.ts` (universo hardcodeado de ~18 instrumentos y 6 mercados UE ficticios), `indicators.ts` (1.747 líneas, **53 indicadores técnicos reales** — `grep -c "id: '"` = 53 — con `indicators.test.ts` de 433 líneas), `tools.ts` (967 líneas, 95 herramientas de dibujo), `drawings.tsx` (502 líneas, motor de dibujo real), `intelligence.ts` (312 líneas), `MarketChart.tsx`, `glass.tsx`, `theme.ts`, `ui.tsx`, `Watchlist.tsx`, `Depth.tsx`, `Arbitrage.tsx`, `Intel.tsx`, `IntelModules.tsx`, `Tape.tsx`.
- Ambas rutas nacieron en UN commit (`788201d`, 2026-06-23, "chore(wip): session-close checkpoint") y jamás se tocaron después (`git log --follow`, verificado en recon). Siguen registradas en `web/src/App.tsx:18-19` (imports) y `:86-87` (routes) pero **excluidas a propósito** de `NAV_GROUPS` (`web/src/layout/Shell.tsx:20`) — decisión registrada en `plans/frontend-definitivo/PROGRESO.md:19-27` ("el terminal DeFi viejo, excluido a propósito según el log — no un hueco"). Curiosidad verificada: el Shell YA tiene lógica especial para la ruta — `Shell.tsx:170,555` cambia el acento activo a "neutral cyan" cuando `location.pathname.startsWith('/terminal')`.
- Restos de violeta confinados a estos ficheros retirados: `PROGRESO.md:51-55` confirma que el pase de marca violeta→azul los dejó sin tocar deliberadamente; `glass.tsx:4,39` conserva "violet mesh tint". **Cualquier fragmento que se rescate exige limpieza de marca (cobalt `#3B82F6`).**

### 1.2 El artefacto tóxico — [VERIFICADO]
`web/src/pages/terminal/intelligence.ts:266` — `NEWS_SOURCES = ['Autovista', 'INDICATA', 'JATO Dynamics', 'DAT', 'Schwacke', 'Eurotax', 'ACEA', 'Spotcar']` — y `:282` `carNews()`: fabrica titulares por plantilla de string y los **atribuye aleatoriamente a proveedores de datos REALES del sector**. Es contenido inventado con atribución de marca real: el artefacto de mayor riesgo reputacional del pilar. **Se destruye entero, no se reutiliza ni como esqueleto** (§9, Fase 0).

### 1.3 Datos: 100% sintéticos en ambos terminales — [VERIFICADO], con corrección al recon
- Grep del recon confirmado: CERO referencias a `web/src/api/cardeep.ts` (cliente tipado del FastAPI vivo), cero `fetch(`, en todo `Market.tsx` y toda la carpeta `terminal/`. Series OHLC generadas por RNG congruencial sembrado.
- **CORRECCIÓN al recon (stale contra HEAD `7d494dc`):** el recon afirmaba que los únicos consumidores del cliente real eran 3 componentes de landing. FALSO hoy: `grep -rln "api/cardeep" web/src` (esta sesión) devuelve la suite completa `web/src/pages/inventory/` (14 ficheros: `useDealerInventory.ts`, `derive.ts`+test, `VehicleGrid/Table/DetailModal`, `garage/GarageScene.tsx`, etc.) más `pages/landing/Bento.tsx`, `LandingHero.tsx`, `TrustStrip.tsx`. **Consecuencia positiva:** ya existe un patrón de consumo real de API en producción (hooks + derive testeado) que el terminal nuevo debe imitar, no inventar.
- Las páginas sucesoras sancionadas por el owner (`Inteligencia.tsx:16` — "// ── Constants & mock data", `Analitica.tsx:13` — "// ── Types & mock data", `Arbitrage.tsx` sin import de cardeep) siguen siendo mock. El pilar 09 NO puede apoyarse en ellas como "ya resuelto".

### 1.4 Backend real disponible — [VERIFICADO, enumeración completa de rutas esta sesión]
La API viva (`services/api/`) expone exactamente **18 endpoints GET** en 5 routers (4 entities + 6 geo + 4 ops + 2 platforms + 2 vehicles — `grep -c "@router.get"` re-contado en pasada 2; `ls services/api/routers/`, **no existe `market.py`**):
- `ops.py`: `/health` (:26), `/stats` (:48, con vía precomputada — `:91` `source="precomputed"`), `/alerts` (:101, tabla `alert` de `migrations/0004_verification_health.sql:34`), `/sources` (:156, tabla `source_health`).
- `entities.py`: `/entities/{cdp}/canonical` (:30), `/entities/{cdp}` (:53), `/entities/{cdp}/inventory` (:94), **`/entities/{cdp}/delta` (:171, cluster-aware — agrega member_ulids)**.
- `vehicles.py`: **`/vehicles/{ulid}/history` (:24, "Full event history NEW→PRICE_CHANGE→GONE, oldest first")**, `/vehicles/{ulid}` (:71).
- `geo.py`: `/geo/completeness|seal|exhaustiveness`, `/geo/{province}/entities`, `/geo/{province}/municipalities/{muni}/entities`, `/geo/{province}/tree` (:32-398).
- `platforms.py`: `/platforms/{cdp}/inventory` (:25), `/vehicles/{ulid}/platforms` (:89).

El sustrato de datos del pilar existe y late: `migrations/0003_vehicles_events.sql:4-26` — tabla `vehicle` con `make, model, year, km, price NUMERIC(12,2), fuel, transmission, status('available','gone'), first_seen, last_seen`; `:33-42` — `vehicle_event` append-only con `event_type IN ('NEW','GONE','PRICE_CHANGE','PHOTO_CHANGE','KM_CHANGE')`, `old_value/new_value JSONB`, `observed_at`. La geo NO vive en `vehicle`: cuelga de `entity` (`migrations/0002_entities.sql:13-15` — `province_code CHAR(2)`, `municipality_code CHAR(5)`, `comarca_id`). Poblada de verdad por `pipeline/delta.py` y los scrapers de plataforma (recon).

### 1.5 Lo que NO existe — [VERIFICADO por grep de migraciones + enumeración de routers]
- **Cero capa de agregación de precio**: `grep "CREATE TABLE" migrations/*.sql` no arroja ninguna tabla `market_*`/`price_*`/`*index*`/`*news*` (0001→0072 barridas). No hay router `/market/*`. El blueprint §3.5 cita `/market/stats` y `/market/velocity` como si existieran — **no existen** (contradicción doc-vs-código; esta carta la registra).
- **Cero fuente fundamental**: ningún pipeline/tabla/scraper de noticias del sector en `pipeline/` ni `services/`. El único artefacto es la fabricación `carNews()` (§1.2).
- Etiqueta del blueprint corregida: `docs/frontend/00-PLATFORM-BLUEPRINT-E2E.md:210` marca §3.5 como `[NOW core / NEAR screener]` — leído literal esta sesión. Ese "NOW" es aspiracional: contra `7d494dc` no hay nada construido sobre dato real. Tratarlo como visión, no como estado.

### 1.6 Infraestructura reutilizable confirmada — [VERIFICADO]
- `web/package.json:37` `lightweight-charts ^5.2.0` · `:43` `recharts ^2.12.7` · `:34` `framer-motion ^12.38.0` — el charting engine ya está instalado.
- `web/src/data/catalog.ts` (2.128 líneas, auto-generado): catálogo real marca/modelo/submodelo con logos/colores, ya consumido por `terminal/market.ts`.
- `services/api/cache.py`, `ratelimit.py`, `stats.py` — patrones de cache/rate-limit del API existente (citados como infraestructura en la carta hermana 08, ficheros listados en `services/api/`).

---

## 2. Investigación competitiva/adversarial

Proveniencia: DOS pasadas de RESEARCH de esta campaña — **pasada A** (12 referencias, primera síntesis) y **pasada B** (15 referencias, 2026-07-17, la entregada a esta pasada). Los criterios son EXACTOS, extraídos de esas pasadas; **no re-verificados con navegador en esta sesión de síntesis** — se marcan [RESEARCH A/B] y la Fase 0 (§9) exige re-contrastar los que condicionen fórmulas congeladas. Donde ambas pasadas cubren la misma referencia, se consolidan; donde discrepan en precisión, se dice cuál aporta qué.

### 2.1 Cómo resuelven "técnico + fundamental" los terminales de referencia
- **TradingView** [RESEARCH A+B]: Charting Library con contrato de **"datafeed API"** — el consumidor conecta SU PROPIA fuente OHLCV al widget, no la de TradingView; es el patrón de integración exacto de un terminal Cardeep contra su agregación propia. Financials = exactamente 4 categorías fijas (Income Statement, Balance Sheet, Cash Flow, Ratios); "Fundamental Graphs" superpone cualquier métrica como serie temporal SOBRE el precio; el Stock Screener fusiona en LA MISMA tabla columnas técnicas (RSI, EMA, Keltner...) y fundamentales; la Watchlist avanzada anida pestañas Noticias/Fundamentales/Técnicos POR símbolo — patrón trasladable a dealer/entidad. Pine Script corre server-side con cuotas de cómputo (>150k scripts comunitarios); Strategy Tester reporta net profit/max drawdown/win rate/profit factor/equity curve. 50+ drawing tools en exactamente 7 categorías — el Terminal.tsx muerto declara 95 herramientas, MÁS que la referencia real: sobreconstrucción sin dato debajo. **Lección exacta: "técnico + fundamental" = columnas combinables de un mismo screener y series superponibles en un mismo chart, no dos apps.**
- **Bloomberg Terminal** [RESEARCH A+B]: >30.000 funciones por mnemónico de 2-4 letras + GO (no menús); **GP (Graph Price) + CACS superponen eventos corporativos/fundamentales (earnings, dividendos, M&A) SOBRE la misma línea temporal del gráfico técnico** — el fundamental no vive en pestaña aparte, se inyecta como anotación anclada al timestamp; GIP correlaciona chart intradía con timestamps de noticias (cómo reaccionó el precio a un anuncio concreto); NSE COS/BBEA = feeds PRE-FILTRADOS por tipo. **Lección exacta: la noticia vive anclada al chart; el fundamental nunca es un firehose sin tipar.**
- **LSEG Workspace (ex-Refinitiv Eikon)** [RESEARCH B]: único competidor real de Bloomberg (~20% de cuota tras la compra de Refinitiv por LSEG en 27.000M$); se diferencia por acceso EXCLUSIVO al wire de noticias Reuters + LSEG Digest (IA de alertas) + CodeBook (Python nativo). **Lección: en un terminal profesional, "fundamental" = wire de noticias propietario y VERIFICABLE — exactamente la pata que Cardeep no puede originar y no debe fingir (§3, límite).**
- **Koyfin / Stock Rover / Simply Wall St** [RESEARCH A]: terminales creíbles de equipo pequeño (~$374/año vs ~$24.000 Bloomberg). **Lección: el listón alcanzable existe si el dato es real.**

### 2.2 Cómo se construye un índice de precio serio sobre activo heterogéneo/ilíquido (arquetipos)
- **S&P/Case-Shiller** [RESEARCH A+B]: repeat-sales ponderado (Case & Shiller 1987) en 3 pasos EXACTOS — (1) OLS de la diferencia de log-precio sobre dummies de tiempo; (2) el residuo² del paso 1 se regresa sobre constante + intervalo entre ventas para obtener pesos que corrigen heterocedasticidad; (3) re-estimación del paso 1 ponderada por los valores predichos del paso 2. Suavizado final: media móvil de 3 meses. Solo entran activos vendidos ≥2 veces. **Nunca asking price.**
- **FHFA HPI** [RESEARCH B]: repeat-sales geométrico ponderado sobre datos purchase-only de préstamos GSE (excluye refinanciaciones tasadas para evitar sesgo) — "calidad constante" se logra exigiendo que LA MISMA unidad se venda dos veces. **Confirma que repeat-sales es el estándar institucional para activos heterogéneos e ilíquidos… y a la vez por qué NO es trasplantable a coches: un coche casi nunca aparece dos veces en el mismo censo observado (§3, límite).**
- **Zillow ZHVI / Neural Zestimate** [RESEARCH A+B]: la vía HEDÓNICA — red neuronal sobre cientos de atributos por unidad + micro-regiones, adoptada precisamente porque la mayoría de unidades venden UNA sola vez (panel repeat-sales demasiado disperso, la situación exacta de los coches); una red unificada reemplazó ~1.000 modelos locales (~20% más precisa en periodo de alta volatilidad); error mediano publicado (~7,49%) SEPARADO por régimen en-mercado vs fuera-de-mercado. Y el precedente UX más directo del pilar entero: la tabla **"Price and Tax History"** por ficha individual — `fecha | importe | $/unidad | %Δ vs evento anterior | etiqueta de evento (Listado/Cambio de precio/Pendiente/Vendido) | fuente MLS | agente` — **espejo 1:1 del modelo `vehicle_event` (NEW/GONE/PRICE_CHANGE/PHOTO_CHANGE/KM_CHANGE) que Cardeep YA tiene poblado.**
- **Redfin Estimate** [RESEARCH B]: cadencia de refresco DIARIA en activos on-market (más lenta off-market) y **publica su error mediano auto-reportado SEGMENTADO: 2,09-3,02% on-market vs 6,45-8,69% off-market**. Disciplina de transparencia que C5 y §7-V4 adoptan literal: precisión por régimen, visible en el producto, nunca una cifra única.
- **BLS CPI "Used Cars & Trucks"** [RESEARCH A+B]: desde enero 2024 el ajuste por kilometraje usa **curva de decaimiento EXPONENCIAL en función de la edad del vehículo** (sustituyó al supuesto lineal); ni el índice oficial del gobierno de EE.UU. observa transacciones directamente — se nutre de J.D. Power Valuation Services/KBB/Black Book.

### 2.3 Los análogos automotrices directos
- **Manheim MMR / MUVVI (Cox Automotive)** [RESEARCH A+B]: ventana móvil de 13 meses; recálculo CADA NOCHE; exclusión explícita de outliers — la pasada A precisa el umbral (>2,6σ de la media en PRECIO o KILOMETRAJE) y la pasada B solo confirma la exclusión sin cifra: **el 2,6σ se re-verifica contra fuente primaria en Fase 0 antes de congelar C4**; ponderación por recencia y volumen; **MMR Range = intervalo de confianza del 70% (banda, no punto)**; Adjusted MMR = Base + pila explícita de ajustes (km, condición, región, color, opciones), ~85% del volumen con ajuste VIN-específico automático; MUVVI ajusta por mix + kilometraje + estacionalidad (pasada A: Census X-13, 20 market classes fijas, base enero 1997 = 100) — **nunca un promedio bruto, siempre corregido por composición**. Insumo: SOLO hammer price de subasta MAYORISTA (~5M transacciones/año — no censo, no retail).
- **CarGurus IMV + Deal Rating** [RESEARCH A+B]: recálculo DIARIO sobre +1M listings activos; comp-set = marca+modelo+trim+año+km+opciones+historial; bandas EXACTAS — Great ≥10% bajo IMV, Good 5-10% bajo, Fair dentro de unos pocos %, High 5-10% sobre, Overpriced >10% sobre; **término de MOMENTO** (si el mercado sube, el IMV se desplaza al alza — primera derivada, no promedio de comps estáticos). **El patrón retail de "cada anuncio posicionado contra fair-value vivo" (adoptado en C7), no un número aislado.**
- **Edmunds TMV** [RESEARCH B]: verificación HUMANA en el bucle — gestores de precio de Edmunds contactan concesionarios reales para confirmar precios de CIERRE reales (no de anuncio); ajusta por incentivos fabricante→distribuidor y gastos de destino/publicidad; serie histórica desde 1990.
- **KBB Fair Purchase Price / Fair Market Range** [RESEARCH B]: blend de >250 fuentes (ventas de concesionario, subastas, privadas, matriculaciones); recálculo SEMANAL — no tiempo real, pese al marketing — con **revisión y validación manual explícita cada semana por analistas y estadísticos nombrados como responsables**. Junto a Edmunds y Manheim: **todo incumbente serio mantiene una capa de validación humana sobre el algoritmo** — el hueco que §3 declara para Cardeep.
- **classic.com CMB** [RESEARCH A]: recálculo DIARIO por nodo marca→modelo→GENERACIÓN→variante→trim→carrocería→transmisión; ponderado volumen+recencia; **EXCLUSIVAMENTE ventas cerradas**, con disclaimer público explícito: el benchmark NO es la valoración de un coche concreto. Chart de 6 ejes simultáneos.
- **Hagerty Price Guide Indexes** [RESEARCH A]: 11 índices renderizados como índice bursátil pero cadencia TRIMESTRAL porque el insumo es juicio de tasador. **Trade-off explícito frecuencia↔autoridad en mercado ilíquido.**

### 2.4 Gobernanza de índice y fundamental REAL
- **S&P Dow Jones Indices** [RESEARCH B]: metodología PUBLICADA en PDF versionado y fechado; ponderación por float ajustado con reglas explícitas (exclusiones, Additional Weight Factor para índices con cap); fechas fijas y separadas de rebalancing reference date vs effective date; comité de gobernanza. **Cualquier índice que Cardeep venda como "verificado" replica esto: reglas transparentes, versionadas, auditables — jamás caja negra (§7-V7).**
- **VWAP/OHLC estándar de microestructura** [RESEARCH B]: Typical Price = (H+L+C)/3; VWAP = Σ(TP×Volumen)/ΣVolumen — la aproximación canónica usada explícitamente "porque la mayoría de plataformas trabajan con datos OHLC de barra, no con trades a nivel tick". Es exactamente la situación de Cardeep (eventos delta discretos, sin tape); C3 la resuelve con mediana-de-asks diaria (más robusta a outliers que una media ponderada por un "volumen" que aquí no es transaccional) y documenta la elección.
- **SMMT / KBA / DGT / ACEA** [RESEARCH B]: organismos oficiales de matriculación, agregados a nivel UE por ACEA; cadencia publicada (SMMT: 4º día laborable de cada mes, por fabricante y tipo de vehículo). **La fuente FUNDAMENTAL real, citable y verificable por terceros que sustituye al patrón fabricado de `carNews()` (§1.2) — la Fase 5 se construye sobre esto, no sobre agregación genérica.**

### 2.5 El veredicto adversarial que gobierna este pilar
Las referencias de índice de máximo rigor (Case-Shiller, FHFA, MUVVI, MMR, CMB) indexan **precio de transacción confirmada, jamás precio de anuncio**. La tabla `vehicle_event` de Cardeep captura transiciones del ANUNCIO — un `GONE` es ambiguo (vendido / retirado / re-listado en otra plataforma). En términos de microestructura: Cardeep tiene hoy un **order book (cotizaciones/asks) censal**, no un **trade tape (operaciones ejecutadas)**. La metáfora "candle = precio" de TradingView promete implícitamente lo segundo. **Cualquier vela que se rotule "precio" a secas hereda el pecado de `carNews()`: vender como verificado lo que es estimado.** Segundo filo (pasada B): todo incumbente serio mantiene validación humana sobre su algoritmo (KBB con analistas semanales nombrados, Edmunds confirmando cierres con dealers reales), y el VAM de Cardeep verifica identidad/dedup de entidad (gate `vam_verified`, `migrations/0023_vehicle_cluster.sql:31` — [VERIFICADO]), NO la corrección de un índice de precio que aún no existe. Este veredicto doble condiciona §3, §4 y §7 enteros.

---

## 3. Objetivo Cardeep para este pilar y por qué puede superar a la referencia

**Objetivo:** el terminal de mercado del coche usado español — charts de precio/stock/rotación por `make·model·provincia` sobre el delta REAL (`vehicle_event`), con screener técnico+fundamental fusionado (patrón TradingView), deal-rating por anuncio contra fair-value vivo (patrón CarGurus), y un panel fundamental construido sobre lo que SOLO Cardeep tiene: la estructura del mercado entero (censo de dealers, stock, entradas/salidas, mix de plataformas). En el idioma del dealer: *"¿a cuánto está el 320d en Málaga hoy, hacia dónde va, y este anuncio concreto está caro o barato?"*

**Dónde Cardeep supera estructuralmente a la referencia** (se sigue de arquitectura verificada, no aspiracional):
1. **Cobertura**: MUVVI = ~5M transacciones/año SOLO subasta mayorista; CarGurus IMV, Edmunds TMV y KBB calculan desde LOS ANUNCIOS/DATOS DE SU PROPIO SILO mono-fuente; classic.com = nicho clásicos. Cardeep = censo vivo del 100% de listings observados con dedup cross-plataforma (`migrations/0023_vehicle_cluster.sql` + `0027_canonical_dedup.sql` — [VERIFICADO], delta por vehículo): el MISMO coche anunciado a la vez en AutoScout24+Coches.net+Motorflash se reconcilia en UNA entidad. Ninguna referencia cruza plataformas competidoras deduplicando: un índice mono-plataforma dobla-cuenta; el de Cardeep no. Y el precedente UX más cercano (la "Price and Tax History" de Zillow, §2.2) se nutre de un feed MLS/IDX unificado que en vivienda YA existe — **en coches usados no existe ningún MLS unificado: el motor de dedup de Cardeep está construyendo de facto el MLS que falta.** Ventaja genuina y no reclamada por ninguna de las referencias estudiadas.
2. **Granularidad geográfica**: MUVVI usa 20 clases nacionales; CarGurus "tu región". Cardeep baja a provincia→comarca→municipio (`geo_province/geo_comarca/geo_municipality`, `migrations/0001`+`0002:13-15`, con endpoints `/geo/*` ya vivos). Nadie del research llega ahí.
3. **Historial por unidad**: `/vehicles/{ulid}/history` ya sirve la línea temporal completa NEW→PRICE_CHANGE→GONE por coche — el equivalente al "chart del instrumento individual" (MMR) ya tiene su dato crudo servido.

**Límite honesto (innegociable, del §2.5) — tres frentes, sin maquillaje:**
1. **Anuncios, no ventas.** Cardeep NO puede hoy igualar el rigor metodológico de las referencias en la definición de "precio": indexa ANUNCIOS. El terminal se construye asumiéndolo y declarándolo EN EL PRODUCTO (no solo en doc interna): toda serie se rotula "precio de anuncio (mediana)" / "Índice de oferta", nunca "precio de venta". La brecha se cierra en dos etapas declaradas: (a) inferencia probabilística de venta con confianza mostrada (§4.C5), (b) fuente registral de transacción confirmada (cambios de titularidad DGT u otra) — **hoy inexistente en el código [VERIFICADO: cero cruce DGT en migraciones/pipeline], hueco conocido, fase futura fuera de esta carta.** Además, el camino repeat-sales (Case-Shiller/FHFA) queda descartado por estructura (un coche casi nunca se revende dentro del censo observado): la ruta es cohorte-de-comparables (IMV) primero y hedónica (Zillow) después, y la segunda exige un workstream ML que hoy no ha empezado — tener mejor materia prima no produce automáticamente un índice mejor.
2. **Fundamental/noticias: edge CERO hoy.** Bloomberg y LSEG se diferencian por wires propietarios que Cardeep no puede originar; el censo+delta no ayuda aquí. El panel fundamental v1 se construye sobre datos censales propios (que nadie más tiene) y las noticias solo entran cuando exista ingesta real con URL verificable de fuentes oficiales (SMMT/KBA/DGT/ACEA, §2.4; §9 Fase 5).
3. **Sin capa de validación humana sobre el índice.** Todo incumbente serio la tiene (KBB semanal, Edmunds llamando a dealers, §2.3); el VAM de Cardeep verifica identidad/dedup de entidad (`0023:31` `vam_verified`), no la corrección del futuro índice — [VERIFICADO por ausencia: cero código de validación de índice en el repo]. Mientras esa capa no exista, el mensaje "observado y verificado, no estimado" solo es legítimo en la mitad censal-delta, jamás en la capa de índice; V1-V4 (§7) son el sustituto automatizado mínimo y V7 su gobernanza.

---

## 4. Criterios de evaluación CONCRETOS (qué se muestra y cómo se calcula)

Nada aleatorio: cada número/badge/sección del frontend traza a un criterio C# de esta tabla. Si un dato no puede calcularse según su criterio, la UI muestra "muestra insuficiente" — jamás un valor fabricado.

**C1 — Símbolo (instrumento).** Clave = `make · model · province_code`, con agregados jerárquicos: `make·model·ES` (nacional), `make·ES`, índice provincial compuesto `CDX-{province}`, índice nacional `CDX-ES`. `make/model` normalizados contra `web/src/data/catalog.ts` (la taxonomía ya existente); geo vía join `vehicle.entity_ulid → entity.province_code` (`0002:13`). Un símbolo SOLO existe (aparece en búsqueda/screener) si supera C2.

**C2 — Muestra mínima renderizable.** Un bucket de un símbolo se renderiza si: ≥ 30 anuncios activos el día del bucket Y ≥ 5 eventos en la ventana del bucket. Por debajo: la vela no se dibuja y el panel lo dice ("muestra insuficiente: N activos"). Umbral inspirado en la disciplina de Wilson/Reddit del research (no fiarse de muestras pequeñas); el valor 30/5 es decisión de diseño de esta carta, ajustable en Fase 1 con datos reales, nunca silenciosamente.

**C3 — Vela (OHLC honesto sobre asking).** Cadencia del dato crudo = 1 agregado diario. Bucket de vela = semana ISO (o día para rangos ≤ 30d con velas de línea). Para cada día d y símbolo s: `median_price(s,d)` = mediana del `vehicle.price` de anuncios `status='available'` ese día, tras exclusión C4. Vela semanal: O = mediana del primer día con dato, H = max de medianas diarias, L = min, C = mediana del último día. Mediana elegida frente al patrón VWAP/Typical-Price (§2.4) deliberadamente: sin trade-tape no hay volumen transaccional que ponderar, y la mediana es robusta a outliers residuales. Rótulo obligatorio en UI: **"€ mediana de anuncio"** — nunca "precio" a secas (§2.5).

**C4 — Exclusión de outliers.** Se excluye del cálculo C3 todo anuncio cuyo `price` O `km` se desvíe > 2,6σ de la media de su símbolo en ventana 90d (regla atribuida a Manheim MUVVI por la pasada A del research; la pasada B confirma la exclusión explícita de outliers pero NO el umbral — **se adopta provisionalmente y se re-verifica contra fuente primaria en Fase 0 antes de congelar**). Los excluidos se cuentan y son auditables (columna `outliers_excluded` en la tabla de agregación, §5).

**C5 — Volumen y rotación.** Barra de volumen = nº de eventos `NEW` del símbolo en el bucket (entradas de stock). Serie secundaria "salidas" = nº `GONE`. **Días en mercado (DOM) P50** = mediana de `gone_at − first_seen` de los vehículos con `GONE` en el bucket. "Venta probable (inferida)" = `GONE` + sin reaparición en el cluster cross-plataforma (`vehicle_cluster`) en 14 días + último precio dentro de ±25% de la mediana del símbolo; SIEMPRE rotulada "inferida", con la tasa de falsos positivos medida en Fase 4 publicada junto al dato (patrón Zillow: precisión por régimen, visible).

**C6 — Presión de precio.** Badge por símbolo = % de anuncios activos con ≥ 1 `PRICE_CHANGE` a la baja en 30d (numerador y denominador del mismo día de cálculo). Flecha/semántica: > 25% = "mercado bajo presión". Deriva 100% de `vehicle_event.event_type='PRICE_CHANGE'` con `old_value/new_value` JSONB comparados.

**C7 — Deal-rating por anuncio (patrón CarGurus).** Para un vehículo concreto: posición de su `price` frente a la mediana C3 de su símbolo ajustada por km (regresión lineal precio~km del símbolo en 90d, patrón MUVVI): ≤ −10% "por debajo de mercado", −10..+5% "en mercado", +5..+15% "por encima", > +15% "muy por encima". Siempre acompañado de N del comp-set; si N < 30, no se emite rating (C2).

**C8 — Fundamental censal (lo que nadie más tiene).** Panel por símbolo, todo derivado de tablas existentes: nº dealers con stock del símbolo (COUNT DISTINCT `entity_ulid`), stock total activo, altas/bajas de dealers con ese modelo (30d), mix plataforma-vs-web-propia (`platform_listing`), concentración (share del top-5 dealers). Cada cifra con su query trazable (§7).

**C9 — Indicadores técnicos.** Los 53 indicadores de `indicators.ts` se aplican SOLO sobre series que cumplan C2/C3 (mediana diaria como "close"). Los que exigen semántica de trade-tape real (p. ej. los basados en volumen de transacción) se re-etiquetan a la semántica censal (volumen = altas C5) o se desactivan — decisión indicador a indicador en Fase 3, documentada en el propio código.

**C10 — Noticias/fundamental externo.** Un titular SOLO se muestra si existe fila en la tabla de ingesta real (§5) con `source_url` vivo, `title` cotejado contra el HTML de origen y `published_at` real. Cero fabricación, cero atribución no verificada. Hasta que exista esa ingesta (Fase 5), el panel de noticias NO EXISTE en la UI — no se rellena con placeholder.

---

## 5. Modelo de datos + almacenamiento backend

### 5.1 Se reutiliza (existente, verificado)
- **`vehicle`** (`migrations/0003:4-26`) — snapshot vivo: `make, model, year, km, price, fuel, status, first_seen, last_seen`. Fuente del corte diario de activos (C3) y del deal-rating (C7).
- **`vehicle_event`** (`0003:33-42`) — el delta append-only: TODO el eje temporal del terminal sale de aquí (C3 backfill, C5, C6). Índices ya existentes `idx_event_type`, `idx_event_entity_time` (`0003:44-46`).
- **`entity`** (`0002`) — `province_code/municipality_code/comarca_id` (`0002:13-15`): la pata geo del símbolo C1.
- **`geo_province`/`geo_comarca`/`geo_municipality`** (`0001`) + endpoints `/geo/*` — jerarquía territorial servida.
- **`vehicle_cluster`** + **`canonical_dedup`** (presentes en el barrido de 47 tablas de la carta 08; el dedup cross-plataforma que hace única la cobertura §3.1) — insumo de la inferencia de venta C5.
- **`platform_listing`** + router `platforms.py` — mix plataforma/web propia (C8).
- **`alert`** (`0004:34`) + `source_health` + `/alerts`,`/sources` (`ops.py:101,156`) — salud del dato que alimenta el sello de frescura del terminal (§6).
- **Infra API**: `services/api/cache.py`, `ratelimit.py`, patrón precomputado de `/stats` (`ops.py:91`) — el router nuevo los adopta, no reinventa.
- **Frontend**: cliente `web/src/api/cardeep.ts` + el patrón hooks/derive testeado de `web/src/pages/inventory/` (HEAD `7d494dc`); `catalog.ts`; `lightweight-charts ^5.2.0` ya instalado; motor `indicators.ts` + su suite de tests (rescatado tras limpieza de marca).

### 5.2 Se crea nuevo (no existe hoy — verificado por grep de 0001→0072)
Nombres propuestos por esta carta; numeración de migración a confirmar contra el máximo vigente en el momento de ejecución (última observada: `0072_vehicle_cluster_country_proof.sql`):
- **`market_symbol`** — registro de símbolos C1: `symbol_key TEXT PK, make, model, province_code CHAR(2) NULL, level ('model_prov'|'model_nat'|'make_nat'|'index'), is_active BOOL, first_bucket DATE`. Poblada por job, no a mano.
- **`market_bucket_daily`** — la tabla central: `symbol_key FK, bucket_date DATE, active_count INT, median_price NUMERIC, p25_price, p75_price, median_km INT, new_count INT, gone_count INT, price_change_down_count INT, price_change_up_count INT, outliers_excluded INT, dom_p50_days NUMERIC NULL, computed_at TIMESTAMPTZ, PRIMARY KEY(symbol_key, bucket_date)`. Append/upsert idempotente por job diario + backfill histórico desde `vehicle_event`.
- **`market_sale_inference`** (Fase 4) — `vehicle_ulid FK, gone_at, inference ('probable_sale'|'delisted'|'relisted'), confidence NUMERIC, evidence JSONB, audited BOOL, audit_result TEXT NULL`. La columna de auditoría existe desde el día 1: la tasa de FP publicada (C5) sale de aquí.
- **`sector_news`** (Fase 5) — `news_ulid PK, source_name, source_url TEXT NOT NULL, title, published_at, fetched_at, content_hash, verified_at TIMESTAMPTZ NULL, symbol_keys TEXT[]`. La restricción de C10 es de esquema: sin `source_url` no hay fila.
- **Job de agregación**: módulo nuevo en `pipeline/` (patrón hermano de `pipeline/delta.py`), corrida diaria + backfill. Sin servicio nuevo: mismo proceso/scheduler existente.
- **Router `services/api/routers/market.py`**: `/market/symbols?q=` (búsqueda C1), `/market/{symbol_key}/ohlc?range=`, `/market/{symbol_key}/stats` (C5-C8), `/market/{symbol_key}/rating/{vehicle_ulid}` (C7). Cache agresiva (los buckets solo cambian 1 vez/día) siguiendo `cache.py`.

**Hueco conocido declarado:** no se ha verificado en esta sesión el volumen real de filas de `vehicle_event` ni su distribución temporal (DB parada según memoria de proyecto). El plan de backfill (Fase 1) DEBE empezar midiendo eso; los umbrales C2 se recalibran con la medición, nunca antes.

---

## 6. Especificación de pantalla/sección en el frontend

Ruta: `/terminal` (se reutiliza la ruta viva de `App.tsx:87`; `/market` y `Market.tsx` mueren — §9 Fase 0). Entra en `NAV_GROUPS` bajo INTELIGENCIA solo al cerrar Fase 3. Lenguaje del dealer real, no jerga bursátil: "stock", "rotación", "días en venta", "mercado" — las velas son la metáfora visual, el texto es de compraventa.

- **Barra de mando (arriba):** buscador de símbolo con lenguaje natural del dealer — teclea "320d málaga" y resuelve contra `market_symbol` + `catalog.ts` (debounce, patrón blueprint §3.5). Selector de rango 30d/90d/1a/todo. Sello de frescura: "datos a {computed_at}" + estado de fuentes (verde/ámbar desde `/sources`) — el dealer ve SI el dato está fresco, siempre.
- **Chart central (lightweight-charts):** velas semanales "€ mediana de anuncio" (C3, rótulo permanente en el eje — la honestidad §3 es un elemento de UI, no una nota al pie), volumen de altas (C5) debajo, marcadores de evento sobre la vela (📉 nº bajadas de precio del bucket). Overlays de indicadores (C9) del motor rescatado. Bandas P25-P75 como área — el dealer ve el rango donde vive el mercado, no solo la mediana.
- **Panel derecho — "El mercado de este coche" (C8):** cifras censales en frases de dealer: "43 profesionales tienen 320d en Málaga · 187 unidades · P50 61 días en venta · 31% ha bajado precio este mes · el top-5 concentra el 38% del stock". Cada cifra clicable → drill-down a la lista real de dealers/anuncios (deep-link, mandato del proyecto).
- **Cinta de eventos (derecha, abajo):** feed real de `/entities/{cdp}/delta` + buckets: "hoy: 12 altas, 9 salidas (5 venta probable*), 7 bajadas de precio" — el asterisco lleva a la explicación de la inferencia con su tasa de acierto medida (C5).
- **Ficha de anuncio (al pinchar un coche):** su historial completo (`/vehicles/{ulid}/history`) dibujado SOBRE el chart del símbolo — el patrón GIP de Bloomberg: la vida de este coche contra su mercado — + deal-rating C7 con comp-set N visible.
- **Screener (Fase 3b):** tabla única con columnas técnicas (Δ% 30d, presión C6, DOM) y fundamentales censales (stock, dealers, concentración) combinables — el patrón exacto del Stock Screener de TradingView aplicado a coches. Filas → símbolo; export CSV.
- **Watchlist:** localStorage v1 (€0, como fija el blueprint §3.5), lista de símbolos con mini-sparkline y presión.
- **Lo que NO hay:** panel de noticias hasta Fase 5 (C10); portfolio/balance/nada bursátil-DeFi (rechazado por el owner — `PROGRESO.md` log 2026-06-30); las 95 herramientas de dibujo se reducen al set útil para este dato (líneas, medición, anotación) — 95 tools sin trade-tape era decorado.
- Marca: cobalt `#3B82F6`/charcoal, cero violeta (gate de grep en Fase 0), glass del sistema actual (el de `inventory/`, no el `glass.tsx` violeta del cadáver).

---

## 7. Protocolo de verificación (2 vías independientes por dato mostrado)

El estándar antialucinación del proyecto aplicado al producto: ningún número llega al dealer sin haberse confirmado por dos caminos que no compartan código.

- **V1 — Paridad SQL↔API (cada release):** script de auditoría (`scripts/`) que recalcula, con SQL directo contra Postgres (sin pasar por el job ni el router), `median_price/active_count/new_count/gone_count` para un golden-set de ≥ 20 símbolos × 10 fechas, y lo compara byte a byte contra la respuesta de `/market/{symbol}/ohlc`. Divergencia = build rojo.
- **V2 — Recomputación por motor ajeno (Fase 1 y cada cambio de fórmula):** export CSV crudo de `vehicle`/`vehicle_event` del golden-set y recomputación de C3-C6 con DuckDB/pandas (código independiente del job de `pipeline/`). Dos implementaciones, un resultado — o no se publica.
- **V3 — UI↔API (cada release):** Playwright lee el número RENDERIZADO (vela, badge de presión, cifras del panel censal) y lo compara contra el JSON del endpoint en la misma sesión. Lo que el dealer ve = lo que la API dice, probado, no asumido.
- **V4 — Auditoría muestral de la inferencia (Fase 4, recurrente):** de cada cohorte de "venta probable", muestra aleatoria de ≥ 50 vehículos re-visitados con navegador real (Obscura/Playwright) contra la plataforma de origen: ¿sigue anunciado en otro sitio? La tasa de FP medida se escribe en `market_sale_inference.audit_result` y ES la cifra que la UI publica junto al dato (C5). Sin auditoría fresca (≤ 30d), el badge degrada a "sin verificar" automáticamente.
- **V5 — Noticias (Fase 5):** doble vía por titular: (a) fila en `sector_news` con `content_hash` del fetch original, (b) re-fetch del `source_url` en el momento de servir cotejando título; si el origen murió o cambió, el ítem se marca y no se muestra. Atribución de fuente = literal del origen, jamás generada.
- **V6 — Gate anti-mock permanente (CI):** grep-gate en CI: cero imports de `terminal/market.ts`/`intelligence.ts` (muertos), cero `seedRng`/generadores sembrados, cero literal de `NEWS_SOURCES` fabricado en `web/src/`. El pecado de `carNews()` queda estructuralmente imposible de reintroducir.
- **V7 — Metodología publicada y versionada (patrón S&P DJI, §2.4; desde Fase 1):** cada fórmula C1-C10 vive en un documento de metodología versionado y FECHADO en `docs/` (nombre a fijar en Fase 1), enlazado desde la propia UI del terminal ("cómo se calcula esto"). Todo cambio de fórmula = nueva versión fechada + re-corrida obligatoria de V2 sobre el golden-set. Un índice "verificado" con metodología secreta es un oxímoron: la gobernanza es parte del producto, no un anexo.

---

## 8. Uso de LLM (doctrina €0 del CLAUDE.md: local/barato para lo masivo, caro solo para decidir)

- **Cero LLM en el camino crítico del dato.** C1-C9 son SQL/aritmética determinista pura. Un índice de precio con un LLM en medio sería inauditable — prohibido por diseño. (Coherente con el mandato de memoria: "AI out of critical path".)
- **Local/barato (masivo), si hace falta:** (a) normalización de variantes sucias de `make/model` de scrapers hacia claves de `catalog.ts` SOLO en la cola larga donde regex/fuzzy determinista falle — con salida siempre validada contra el catálogo cerrado (el LLM propone, el diccionario dispone); (b) en Fase 5: clasificación de noticias por tema/relevancia y dedup de titulares casi idénticos; (c) etiquetado de `symbol_keys` en noticias. Todo batch, offline, re-ejecutable, nunca en request-path.
- **Modelo caro (justificado, único caso):** el "informe semanal de mercado" opcional (Fase 6+, fuera de esta carta si no gana su sitio): síntesis en lenguaje de dealer SOBRE cifras ya verificadas, donde cada frase enlaza al stat consultable que la respalda (patrón de esta doctrina: la prosa cita al dato, no lo sustituye). Generación 1 vez/semana, coste acotado, etiquetado "análisis generado". Ninguna decisión de qué símbolo existe, qué outlier se excluye o qué venta se infiere pasa por LLM: eso es determinista (C1-C7).

---

## 9. Fases de construcción (orden estricto; cada fase cierra con build+test+revisión real antes de abrir la siguiente)

**Fase 0 — Demolición controlada + rescate + re-verificación adversarial.**
Borrar `Market.tsx` + ruta/import `/market` (`App.tsx:18,:86`); borrar `intelligence.ts` entero (con `carNews()` y `NEWS_SOURCES`) y los paneles que solo él alimentaba (`Intel.tsx`, `IntelModules.tsx`); cuarentena del resto de `terminal/` fuera del build; rescate explícito de `indicators.ts`+`indicators.test.ts`+`MarketChart.tsx`+`drawings.tsx` (reducido) con limpieza de marca (violeta→cobalt). Re-contrastar con navegador real los criterios [RESEARCH A/B] que condicionan fórmulas congeladas (MUVVI 2,6σ — solo pasada A, obligatorio antes de C4; MMR nightly y banda 70%; bandas exactas del deal-rating IMV; segmentación de error de Redfin). Corregir la etiqueta `[NOW core]` de `00-PLATFORM-BLUEPRINT-E2E.md:210` a estado real.
*Criterio de cierre:* `npm run build` verde; suite `indicators.test.ts` verde tras el trasplante; grep violeta (`#a78bfa|#8b5cf6|#c4b5fd|#7c3aed`) = 0 en ficheros vivos; grep `carNews|NEWS_SOURCES|seedRng` = 0 en `web/src/`; ruta `/market` inexistente (Playwright 404→redirect); revisión de código real de lo rescatado.

**Fase 1 — Medición + agregación backend (el corazón).**
Medir volumen/distribución real de `vehicle_event` (hueco declarado §5.2). Migración `market_symbol`+`market_bucket_daily`; job diario en `pipeline/` + backfill histórico completo; calibración de C2 con datos medidos, documentada.
*Criterio de cierre:* V2 ejecutado (DuckDB independiente, golden-set 20×10, match exacto); conteos de buckets cruzados contra SQL directo (V1 embrión); job idempotente probado (doble corrida = cero filas duplicadas); tests pytest del job; revisión.

**Fase 2 — Router `/market/*`.**
`market.py` con los 4 endpoints (§5.2), cache/rate-limit según patrones de `cache.py`/`ratelimit.py`, envelope de respuesta idéntico al del API existente.
*Criterio de cierre:* suite pytest de router (incl. símbolo inexistente, C2 insuficiente → respuesta explícita, cache headers); V1 completo automatizado como script repetible; OpenAPI correcto; revisión.

**Fase 3 — Terminal v2 en frontend (dato real, cero mock).**
Chart + buscador + panel censal + cinta de eventos + ficha-sobre-chart (§6), consumiendo `api/cardeep.ts` extendido, imitando el patrón hooks/derive de `inventory/`. 3b: screener + watchlist.
*Criterio de cierre:* V3 (Playwright renderizado↔JSON) verde; V6 (gate anti-mock) en CI; build; visual light+dark en 320/768/1440; grep `fetch(`-directo = 0 (todo por el cliente tipado); revisión con ojo de marca (protocolo del owner: nada prematuro entra al nav — el nav se toca AL FINAL de esta fase, no antes).

**Fase 4 — Inferencia de venta + deal-rating.**
`market_sale_inference` + lógica C5 sobre `vehicle_cluster`; C7 con regresión precio~km; badges en UI con N y confianza visibles.
*Criterio de cierre:* V4 ejecutado (≥ 50 auditados con navegador real, tasa FP escrita en tabla y renderizada); degradación "sin verificar" probada con test de reloj; revisión.

**Fase 5 — Fundamental externo real (noticias).**
Ingesta de fuentes reales del sector (RSS/prensa con URL) → `sector_news`; clasificación con LLM local (§8); panel de noticias ancladas al timestamp del chart (patrón GIP).
*Criterio de cierre:* V5 doble vía por ítem; 100% de filas con `source_url` re-fetchable; cero titular sin origen vivo; revisión.

**Fase 6 — Endurecimiento + entrada al nav + cierre documental.**
Entrada en `NAV_GROUPS`; muerte definitiva de todo resto en cuarentena; gates V1/V3/V6 fijados en CI; runbook del job; actualización del blueprint y de esta carta a estado "construido".
*Criterio de cierre:* auditoría final de regresiones repo-wide; CI verde con los tres gates; navegación real grabada (Playwright) del flujo dealer completo búsqueda→chart→ficha→deal-rating.

---

## Resumen

El pilar 09 tiene hoy dos terminales muertos 100% sintéticos (con un artefacto tóxico que fabrica noticias atribuidas a proveedores reales — se destruye en Fase 0) y, debajo, el único sustrato que importa: `vehicle`+`vehicle_event` reales servidos por API viva, sin capa de agregación. La ventaja estructural de Cardeep es real — censo deduplicado cross-plataforma (el MLS que en coches no existe y Cardeep construye de facto) + granularidad provincia/comarca que ninguna referencia (MUVVI, IMV, CMB) alcanza — pero los límites son innegociables y van rotulados en el producto: se indexan anuncios, no ventas (inferencia de venta auditada y publicada hasta que exista fuente registral), cero pata fundamental hoy, y sin capa de validación humana del índice. Se rescata el motor de 53 indicadores testeado, se construye `market_bucket_daily`+router `/market/*` deterministas (cero LLM en el camino crítico) con metodología versionada y publicada (V7, patrón S&P DJI), y cada número del frontend traza a un criterio C1-C10 verificado por dos vías independientes antes de tocar la retina del dealer.
