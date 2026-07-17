# Carta de sub-proyecto — Pilar 02: Historial de vehículo ("Cardeep Report", estilo Carvertical/Carfax)

> Programa: cardeep-omni · Clave: `02-history-reports` · Fecha: 2026-07-17
> Fase: SYNTHESIS (arquitectura). Este documento es la fuente de verdad del pilar
> hasta que una fase de ejecución lo enmiende con evidencia nueva.
> Doctrina aplicada: antialucinación tolerancia cero — cada afirmación lleva
> [VERIFICADO] (leída en código/doc real, con archivo:línea) o [ASUMIDO]
> (declarada como suposición, jamás disfrazada de certeza).
> RECON base: 2026-07-16/17. Anclajes archivo:línea re-verificados uno a uno
> contra el fuente el 2026-07-17: main.py:146-150, 0003 (tablas 4-26/33-42,
> índices 44-46), 0023 (21-34/39-52/57, gate 16/31), 0002:4, 0004:5/34,
> 0009:16/23, 0032:29/59/90, vehicles.py:6/24/33-37, vite.config.ts:8-10,
> check.ts:1-2, cluster_vehicles.py:114-122/319-324, VehicleDetailModal.tsx:21/
> 61-65/154-157, API_CONTRACT.md (grep check|dossier → solo SQL CHECK),
> 00-PLATFORM-BLUEPRINT-E2E.md:34/184/193 (corregido off-by-one: 35→34),
> 04-COMPETITIVE-UX-AUDIT.md:107, iseecars.md:84/168.

---

## 1. Estado actual

Veredicto en una frase: este pilar tiene hoy **una fachada frontend Carfax-grade que es 100% maqueta sin un byte de dato real detrás**, y por separado **un activo real, funcional e infrautilizado** (el delta append-only por vehículo) que nadie ha convertido en producto de historial. Nada intermedio.

### Capa A — La fachada "Check/Dossier": vaporware heredado [VERIFICADO archivo por archivo]

- `web/src/pages/Check.tsx` (259 líneas): orquesta tabs "Autoficha"/"Informe completo". [VERIFICADO en RECON]
- `web/src/pages/check/CheckLanding.tsx` (508 líneas): formulario VIN/matrícula con selector de país. [VERIFICADO en RECON]
- `web/src/pages/check/CheckReport.tsx` (1.318 líneas): gráfico de kilometraje (recharts), `AlertCard`, `Timeline`, `ScoreGauge`, `SourceBadge`, secciones de specs/dimensiones/ITV/recalls/seguridad. [VERIFICADO en RECON]
- `web/src/pages/check/DossierReport.tsx` (353 líneas): identidad, técnica, matriculación, titularidad (propietarios + movimientos DGT), situación legal (embargo/robado/precintado/recall/renting/taxi), NCAP+RAPEX, ITV/APK con defectos, fiscal/BPM. [VERIFICADO en RECON]
- `web/src/types/check.ts` (267 líneas) y `web/src/types/dossier.ts` (190 líneas): tipos exhaustivos, Carfax-grade. [VERIFICADO en RECON]
- **La confesión está en el propio código**: `web/src/types/check.ts:1-2` dice literalmente *"Types aligned with workspace/internal/check/ Go types. Backend JSON field names must match exactly."* — pero `find . -name "*.go"` sobre el repo completo devuelve **CERO** archivos Go. El backend al que esos tipos se alinean **nunca existió en Cardeep** (prototipo Go descartado, coherente con el pipeline Go dormido de CARDEX). [VERIFICADO check.ts:1-2 leído en esta sesión + find del RECON]
- **Cero backend, probado por 3 vías independientes**:
  1. `services/api/main.py:146-150` registra exactamente 5 routers: `ops`, `entities`, `geo`, `vehicles`, `platforms`. No existe router `check` ni `dossier`. [VERIFICADO en esta sesión]
  2. `docs/API_CONTRACT.md` (contrato sellado, 17 rutas verificadas contra `/openapi.json` en RECON): grep case-insensitive de `check|dossier` → solo constraints SQL `CHECK` (líneas 597, 629, 733...). Ninguna ruta. [VERIFICADO en esta sesión]
  3. Infra: `docker-compose.yml` solo define cardeep-pg + api(:8090) + autopilot. Nada sirve `/api/v1/*`. [VERIFICADO en RECON]
- **La ruta de red es huérfana**: los hooks `useCheck.ts`/`useDossier.ts` usan `web/src/api/client.ts` (`fetch('/api/v1'+path)`), un cliente DISTINTO del real (`web/src/api/cardeep.ts`, que apunta a `VITE_API_BASE` → :8090). En dev, `web/vite.config.ts:8-10` proxea `/api` → `http://localhost:8506` — puerto que no aparece en ningún otro sitio del repo (ni compose, ni Dockerfile, ni scripts de `package.json`). **Nada lo sirve, nunca.** Un usuario real en `/check` solo puede recibir un error de red. [VERIFICADO vite.config.ts:8-10 en esta sesión; resto en RECON]
- `plans/frontend-definitivo/PROGRESO.md` (líneas 44-45, 88, 131) confirma de forma independiente que Check-Dossier está **pendiente de auditar** y que el único trabajo hecho fue migración de tokens CSS dark/light. Alguien confirmó que SE VE bien; nadie confirmó que FUNCIONA. [VERIFICADO en RECON]

### Capa B — El activo real: delta append-only por vehículo [VERIFICADO end-to-end]

- `migrations/0003_vehicles_events.sql:33-42` — tabla `vehicle_event`, **append-only** ("NEVER updated or deleted — the full timeline", línea 32): `event_type IN ('NEW','GONE','PRICE_CHANGE','PHOTO_CHANGE','KM_CHANGE')` (37-38), `old_value`/`new_value` JSONB (39-40), `observed_at` (41). Índices por vehículo, entidad+tiempo y tipo (44-46). [VERIFICADO en esta sesión]
- `migrations/0003:4-26` — tabla `vehicle`: `vin_ref` (19), `photo_hash` (18), `km` (12), `price` (13), `status IN ('available','gone')` (21-22), `first_seen`/`last_seen` (23-24), `UNIQUE (entity_ulid, deep_link)` (25). [VERIFICADO en esta sesión]
- `services/api/routers/vehicles.py:24` — `GET /vehicles/{vehicle_ulid}/history` REAL: paginado, rate-limited, sirve el stream de eventos oldest-first, y sirve historial incluso para alias no canónicos (líneas 33-37: "not an erasure of history"). [VERIFICADO en esta sesión]
- `web/src/pages/inventory/VehicleDetailModal.tsx:21,61-65,154-157` — pestaña `'historial'` real que llama `cardeep.vehicleHistory(vehicle.vehicle_ulid)` con manejo de error. Funciona end-to-end contra la API viva. [VERIFICADO en esta sesión]
- Los docs de visión ya declaran este delta como EL diferenciador: `docs/frontend/00-PLATFORM-BLUEPRINT-E2E.md:34` ("ficha de vehículo con historial gratis (estilo Carfax)"), `:184` ("PHOTO_CHANGE→KM_CHANGE→GONE como diferencial vs Carfax/Carvertical de pago. Sin registro, sin paywall"), `:193` ("Comparable: Carfax/Carvertical (lo damos gratis)"). Y `docs/frontend/04-COMPETITIVE-UX-AUDIT.md:107`: fila "Historial de vehículo integrado (DGT/ITV/cargas)" → "ROBAR: integrar/enlazar informe DGT-ES ('CARDEEP Report') — brecha enorme en ES". [VERIFICADO ambas en esta sesión]

### Capa C — Identidad de vehículo: dedup instantáneo SÍ, identidad de por vida NO [VERIFICADO]

- `migrations/0023_vehicle_cluster.sql` — overlay no destructivo de dedup cross-plataforma: `vehicle_cluster_run` (con gate `vam_verified`, línea 31), `vehicle_cluster` (con `match_signal` 'photo_url'|'firma'|'both', línea 44), vista `v_canonical_vehicle` (línea 57). Señal A = photo_url normalizada; señal B = firma (make,model,year,km)+precio±2%+provincia, con guardas anti-FP. [VERIFICADO en esta sesión]
- `pipeline/identity/cluster_vehicles.py:114-122,319-324` — `vin_ref` actúa SOLO como guardia secundaria (desbloquea merge de km=0/NULL si ambos comparten `vin_ref` no nulo idéntico). **No existe lógica alguna que re-identifique un mismo coche cuando pasa a `status='gone'` y reaparece meses después en otro dealer.** El propio delta de Cardeep NO encadena hoy la vida de un coche a través de sus re-anuncios. [VERIFICADO en esta sesión]
- `pipeline/sources/dgt_cat.py` — es el registro CATV de desguaces autorizados (ArcGIS): fuente de DESCUBRIMIENTO de entidades, cero relación con historial de titularidad/ITV. [VERIFICADO en RECON]

### Huecos estructurales confirmados

1. Ningún backend para VIN-decode, matrícula, titularidad, ITV, alertas legales, NCAP/RAPEX — los tipos TS lo modelan, cero código lo produce.
2. Ninguna integración con fuente oficial de historial (DGT, ITV autonómicas, aseguradoras, robo policial).
3. Ruta de red `/check` completamente huérfana (proxy dev :8506 sin servidor detrás; producción sin ruta).
4. El activo real (event timeline) escondido en un modal de inventario interno, sin marca ni posicionamiento.
5. Sin re-identificación de vehículo GONE→reaparición: sin ella no hay "vida en mercado" multi-dealer.
6. Cero tests del pilar (`tests/test_cdp_check_multicountry.py` es un falso positivo: SQL CHECK de `cdp_code`).
7. **Hueco de RECON declarado**: la cobertura REAL de `vin_ref` y `photo_hash` en la tabla `vehicle` (qué % de las filas los tienen no nulos) NO se ha verificado por SQL — el stack estaba parado en el último snapshot (Docker/DB caídos, 2026-06-27) y esta sesión no levantó la DB. Es la PRIMERA verificación de F0, porque de ese % depende la viabilidad del encadenado de por vida.

---

## 2. Investigación competitiva/adversarial

RESEARCH ejecutado: 19 referencias (12 del intel-audit existente en `plans/intel-audit/companies/`, leídas íntegras; 4 hallazgos nuevos verificados en vivo; 3 referencias estructurales). Criterios EXACTOS extraídos — no genéricos:

### Los comerciales (qué venden y con qué mecánica exacta)

| Referencia | Criterio exacto extraído |
|---|---|
| **CARFAX** (US/CA/EU) | 30-38 mil millones de registros, 131-177 mil fuentes. **History-Based Value**: valoración VIN-específica (no por año/trim genérico) ponderando 4 factores textuales — accidentes/daño (~500$ leve, ~2.100$ severo), servicio, nº propietarios, título — recalculada SEMANALMENTE por oferta/demanda/localización/estación; banner Great/Good/Fair Value = precio anuncio vs HBV. **Buyback Guarantee**: cubre 8 title brands concretos, exige brand emitido ≥60 días antes del informe, reclamación ≤1 año, pago = MIN(precio compra, 110% HBV). |
| **AutoCheck** (Experian) | **AutoCheck Score® 1-100 patentado (US 8,005,759)** + "Score Range" (banda esperada para misma edad+clase). Penaliza explícitamente: accidentes, km, title brands, odómetro roto, daño estructural/agua, lemon, robo-repo, uso taxi-policía. Predice probabilidad de seguir circulando a 5 años. Foso: datos exclusivos de subasta (Manheim/ADESA, 98,86% cobertura). |
| **carVertical** (LT, 37 países) | **AI Damage Detection**: infiere daños desde FOTOS cuando no constan en bases oficiales — parte+severidad+coste estimado EN RANGO (p.ej. 15.001-20.000€)+causa+fecha+país. **Market Price**: banda alta/baja + forecast de % de depreciación a 7 años + ventana óptima de compra/venta. **Safety**: sub-scores regionales (NHTSA/Euro NCAP/ANCAP), no score genérico. |
| **HPI Check / cap hpi** (UK) | **National Mileage Register propia: 369M+ lecturas desde 1992** (DVLA+V5+MOT+subastas+leasing+seguros). **Garantía económica de £30.000 sobre el dato** — solo en el check completo (£19,99), no en el Basic. Lección: el foso es la SERIE de kilometraje, y la confianza se vende con dinero detrás. |
| **ClearVin** (US) | **Rating A-F con 13 factores explícitos y nombrados**, incluidos 2 únicos: "Value Index" (retail vs MSRP) y "Value Depreciation" (ACV de subasta vs MSRP) — combina historial de daño CON señal de mercado en un solo grado. Foso: acceso Copart/IAA vía empresa hermana broker. |
| **autoDNA** (PL) | Decano B2C europeo, 26+ países; revende NMVTIS para US. "Last Enquiries + mapa" como señal social anti-fraude. Único caso de partenariado bidireccional Estado-privado: su tabla de riesgos está DENTRO del servicio gubernamental polaco gratuito desde 2020. |
| **Cartell.ie** (IE) | Agrega 5 fuentes nombradas (NVDF + NCT/Applus + HPI Ireland finance + Garda PULSE robo + siniestros aseguradoras IE+UK) por 15-30€. **Punto ciego universal confesado: para importados de UK, la historia PRE-importación es INVISIBLE.** |
| **STAT.vin** (referencia NEGATIVA) | Agregador barato ($4,90) de subasta salvage, trust score 34,8/100, quejas de datos inventados, disclaimer "find-replaced", opacidad societaria. **Qué NO hacer: vender como historial lo que no puedes respaldar.** |
| **GANVAM / INTEVES** (ES, referencia NEGATIVA para este pilar) | Su producto INTEVES es un **PASSTHROUGH puro del informe DGT sin dato propio** (8,67€+margen). Ocupa el nicho de intermediación institucional desde 1966 con relación DGT que Cardeep no tiene. Replicarlo = copiar la pieza MENOS defendible del ecosistema. |

### Los registros estatales (el plano de dato que Cardeep NO tiene)

| Referencia | Criterio exacto extraído |
|---|---|
| **NMVTIS** (US, DOJ/AAMVA) | El estándar regulatorio que sostiene a todo el duopolio US: **Anti Car Theft Act 1992 + 28 CFR Part 25 (§25.56)** obliga POR LEY a estados, aseguradoras y desguaces (≥5 vehículos/año) a reportar MENSUALMENTE 5 elementos exactos. Taxonomía normalizada de **~60 title brands** a los que se mapean los brands heterogéneos de 51 jurisdicciones — el patrón de normalización canónica que cualquier agregador multi-fuente debe replicar. El informe al consumidor se LIMITA deliberadamente a 5 indicadores. |
| **HistoVec** (FR, código abierto GPLv3) | **Privacidad por diseño**: NO hay búsqueda libre por matrícula; el titular genera el informe aportando datos de la carte grise (hay que POSEER el documento) y el comprador accede solo vía enlace compartido (key/uuid). AES256 + PII SHA256. Taxonomía jurídica de 4 oposiciones (OVE/OVEI/OTCI/OTCI-PV) + ~120 tipos de operación registral trazables campo a campo (D.1-V.9). |
| **RDW** (NL) | **API SODA/Socrata abierta: sin key, sin límite, CC0, actualización DIARIA** — el modelo de apertura más radical estudiado. **"Tellerstandoordeel"**: juicio antifraude de 4 valores (Logisch/Onlogisch/Geen oordeel/Niet geregistreerd) sobre la SERIE completa de odómetro, con código de motivo (00-07), operativo desde 2014 por responsabilidad legal. |
| **DGT — Informe de Vehículo** (ES) | La referencia local exacta. 7 modalidades; **Informe Reducido GRATIS = semáforo de exactamente 3 estados** (Sin incidencias / Con avisos / Con incidencias) con lista TAXATIVA de disparadores; Informe Completo 8,67€ con **12 secciones CONDICIONALES** (solo aparecen si hay anotación — el vacío ES información). **SIN API JSON pública** (solo PDF + SOAP con certificado); VIN restringido en datos abiertos desde 2025. |
| **UK MOT History API + DVLA VES** | El mejor ejemplo mundial de historial oficial como API: REST/JSON gratuita, **bulk semanal + deltas diarios**, límite 500.000 req/día / 15 req/s. **Taxonomía de defecto en 5 niveles: DANGEROUS/MAJOR/MINOR/ADVISORY/PRS.** Patrón UI DVLA: 2 semáforos paralelos (Tax/MOT) + paso de confirmación "¿es este el vehículo?" (make+colour) antes de revelar detalle. |
| **Historia Pojazdu / CEPiK** (PL) | "Diccionarios-frecuencia": censo del parque por atributo, gratis, vía API pública. |
| **KBA / ZFZR** (DE, referencia NEGATIVA) | El registro del mayor mercado de Europa exige **solicitud POSTAL + 5,10€ + ~8 SEMANAS** (§39 StVG) para terceros. Ni Alemania tiene consulta digital instantánea → hueco de mercado continental real. |

### El marco regulatorio en movimiento (crítico para NO construir lo equivocado)

| Referencia | Criterio exacto extraído |
|---|---|
| **Car-Pass ASBL** (BE) | Ley 11-jun-2004 + RD 26-ago-2006: TODO profesional del sector (talleres, chapa, asistencia, neumáticos) obligado a transmitir chasis+km+fecha; desde 2024 también el TIPO de trabajo. Certificado 11,10€ (gratis si <4 lecturas). Resultado declarado: el fraude de km "prácticamente desapareció" en Bélgica. |
| **Decisión Consejo UE Transporte, 5-dic-2025** | Los 27 ministros acordaron un sistema Car-Pass-style PANEUROPEO: base central de km alimentada obligatoriamente en cada ITV/mantenimiento + reporte TRIMESTRAL obligatorio de km desde fabricantes de coche conectado + criminalización de la manipulación de odómetro. Pendiente de Parlamento Europeo. Daño estimado del fraude: 5.600-9.600 M€/año. **Implicación directa: en pocos años el Estado europeo producirá gratis el dato de km fiable que hoy venden HPI/carVertical/autoDNA. Construir un motor de fraude de odómetro desde cero HOY es construir contra la marea.** |
| **EUCARIS** | Arquitectura hub-and-spoke SIN base central (soberanía nacional del dato), 32 países, >10M consultas/año — el "cableado" transfronterizo que ya usan DGT/RDW/CEPiK. |

### Síntesis adversarial

El foso de TODOS los jugadores es el mismo en su raíz: **acceso — por ley o por relación comercial exclusiva — a eventos institucionales del vehículo** (título/embargo, ITV con defectos y km certificado, siniestro total, robo, titularidad). Cardeep no tiene ni un byte de ese plano. Y a la inversa: **ninguno de los 19 estudiados hace "días-en-mercado + bajadas de precio + re-publicaciones por unidad física" de forma rigurosa** (carVertical roza el Market Price pero es un valor puntual, no una serie de comportamiento), y ningún registro estatal tiene NI QUIERE ese dato porque no es su misión. Ese eje ortogonal es el único donde Cardeep parte con ventaja real.

---

## 3. Objetivo Cardeep para este pilar — y el límite honesto

### El límite honesto, primero y sin maquillaje

**Cardeep NO puede competir hoy con Carfax/Carvertical en historial institucional, y este documento prohíbe fingir que sí.** No hay acceso a DGT (sin API JSON; SOAP con certificado + convenio INTV que no tenemos), ni a las 17 redes de ITV autonómicas, ni a aseguradoras, ni a bases de robo. Cualquier "Cardeep Report" que muestre titularidad, embargos, ITV o siniestros sería hoy dato inventado — exactamente el pecado de STAT.vin, y la violación frontal de la doctrina antialucinación del proyecto aplicada al producto. Además, la decisión UE del 5-dic-2025 desaconseja invertir en un motor propio de fraude de odómetro: esa infraestructura la va a producir el Estado.

### El objetivo real: "Vida en mercado" — el historial que NADIE tiene

Cardeep construirá el **historial de comportamiento de mercado por unidad física**, el único plano donde su dato es primario, verificable y sin competidor:

1. **Encadenar la vida del coche a través de sus re-anuncios** (GONE→reaparición en otro dealer meses después) — la pieza de ingeniería que hoy falta y que ningún competidor comercial hace a nivel europeo. El coche "rebotado" entre compraventas queda visible por primera vez.
2. **Servir la serie completa por unidad física**: días en mercado por episodio, nº y % de bajadas de precio, nº de re-publicaciones, nº de dealers distintos que lo han tenido, retrocesos del km declarado entre anuncios (la única señal de odómetro que Cardeep puede afirmar con dato propio: "el vendedor declaró menos km que el anuncio anterior" — es un hecho observado, no una inferencia).
3. **Gratis y sin paywall**, como declara `00-PLATFORM-BLUEPRINT-E2E.md:184` — el posicionamiento es "lo que Carfax cobra por adivinar sobre el mercado, Cardeep lo observó de primera mano".
4. **Handoff honesto al dato institucional**: enlazar/guiar al Informe DGT oficial (patrón LaCentrale→HistoVec, brecha declarada en `04-COMPETITIVE-UX-AUDIT.md:107`), claramente separado del dato Cardeep, sin revenderlo ni imitarlo. El convenio/acceso institucional (INTV, ITV, aseguradoras) queda como decisión de GASTO y legal del owner — fuera del alcance €0 de esta carta, registrado como fase condicionada (F5).

### Por qué puede superar a la referencia (en su eje)

- El dato ya existe y es append-only auditado (`vehicle_event`, 0003:32) — no hay que comprarlo ni scrapearlo de nuevo.
- El mecanismo de identidad instantánea cross-plataforma ya existe con gate de verificación (`vehicle_cluster` + `vam_verified`, 0023) — la re-identificación temporal es una EXTENSIÓN del patrón probado, no una invención.
- Ningún competidor puede reconstruir retroactivamente esta serie: requiere haber observado el mercado en continuo. Cada día de censo vivo agranda un foso que ni Carfax puede comprar.
- iSeeCars publica "Days on Market" medio por modelo (media usado 53,0 días; muestra >960.000 ventas, feb-2026) medido desde sus propios listados (`days_listed` — "Listed 34 days ago") [VERIFICADO `plans/intel-audit/companies/iseecars.md:84,168`]; Cardeep lo mediría sobre el censo multi-plataforma con dedup por unidad física y cadena de vida — metodológicamente superior en su nicho geográfico.

---

## 4. Criterios de evaluación CONCRETOS (cada número/badge del frontend traza aquí)

Regla madre: **ningún número se muestra si no es computable desde filas reales de `vehicle`/`vehicle_event`/`vehicle_cluster`/`platform_listing` con la fórmula exacta de esta tabla.** Prohibido cualquier score sintético sin ground truth (lección AutoCheck: su score 1-100 requiere décadas de outcome data que no tenemos — NO se imita en v1).

| # | Dato mostrado | Fórmula exacta | Fuente |
|---|---|---|---|
| C1 | **Días en mercado (episodio)** | `observed_at(GONE)` − `observed_at(NEW)` del mismo `vehicle_ulid`; si sigue `available`: `now()` − `observed_at(NEW)`. | `vehicle_event` |
| C2 | **Días en mercado (vida)** | Suma de C1 sobre todos los episodios de la cadena de vida (ver C7). Se muestra SOLO si la cadena está verificada (§7). | `vehicle_event` + cadena F1 |
| C3 | **Nº de bajadas de precio** | count de `PRICE_CHANGE` donde `new_value->>'price' < old_value->>'price'` (numérico). Las subidas se cuentan aparte, nunca se ocultan. | `vehicle_event` |
| C4 | **% de caída acumulada** | (primer precio observado − último precio observado) / primer precio, por episodio. Primer precio = `new_value` del evento `NEW` o el `old_value` del primer `PRICE_CHANGE` si `NEW` no registró precio — la fase F1 verifica cuál de las dos formas aplica leyendo el emisor de eventos real; hasta entonces esta alternativa queda declarada, no resuelta. | `vehicle_event` |
| C5 | **Nº de plataformas donde se anuncia** | count distinct de `platform_listing` activas del `vehicle_ulid` canónico + tamaño del cluster en `v_canonical_vehicle`. | `platform_listing` (0009) + `vehicle_cluster` (0023) |
| C6 | **Nº de dealers que lo han tenido** | count distinct `entity_ulid` a lo largo de la cadena de vida. | cadena F1 |
| C7 | **Re-publicaciones ("coche rebotado")** | nº de episodios NEW→GONE encadenados como misma unidad física por el motor F1. Badge "Rebotado" si ≥2 episodios con ≥2 dealers distintos. | cadena F1 |
| C8 | **Alerta km declarado retrocede** | (a) intra-anuncio: `KM_CHANGE` con `new < old` y delta > 1.000 km (umbral anti-ruido de corrección de typo, ajustable por config, nunca hardcodeado en UI); (b) inter-episodio: km del `NEW` del episodio N+1 < último km conocido del episodio N − 1.000. SIEMPRE con la evidencia (dos lecturas, dos fechas) visible. Se etiqueta "km declarado por el vendedor retrocedió", JAMÁS "odómetro manipulado" (eso es una acusación legal que no podemos sostener). | `vehicle_event` + cadena F1 |
| C9 | **Semáforo de 3 estados** (patrón DGT Reducido, lista TAXATIVA) | **Sin señales**: cero disparadores. **Con avisos**: ≥1 de {C3≥3 bajadas, C1>90 días, C7=2 episodios}. **Con señales fuertes**: ≥1 de {C8 activo, C7≥3 episodios, C6≥3 dealers}. Nada más dispara nada — la lista es cerrada, como la de DGT. | derivado C1-C8 |
| C10 | **Freshness** | `vehicle.last_seen` textual ("visto hace N horas/días"). | `vehicle` (0003:24) |
| C11 | **Chip de evidencia de identidad** | Por cada eslabón de la cadena: la señal que lo justificó (`photo_hash exacto` / `vin_ref exacto` / `firma+corroboración`) + confianza. Sin chip no hay eslabón mostrado. | motor F1 |
| C12 | **Secciones condicionales** (patrón DGT: el vacío es información) | Una sección solo se renderiza si tiene ≥1 dato real. "Este coche no presenta re-publicaciones" es un estado explícito, no una sección vacía. | todas |

Lo que **NO** se muestra en v1 (y por qué): score numérico global (sin ground truth), valoración de precio justo (pilar 01, no este), titularidad/ITV/legal (sin fuente — solo el handoff a DGT), estimación de daños por foto (carVertical-style: requiere modelo+dataset que no existen; candidato a fase futura, no se promete).

---

## 5. Modelo de datos + almacenamiento backend

### Se REUTILIZA (existente, verificado)

| Pieza | Ubicación verificada | Rol en el pilar |
|---|---|---|
| `vehicle` | `migrations/0003_vehicles_events.sql:4-26` | Unidad de anuncio: `vin_ref`, `photo_hash`, `km`, `price`, `status`, `first_seen`/`last_seen` |
| `vehicle_event` | `migrations/0003:33-42` | LA fuente primaria del pilar: serie append-only NEW/GONE/PRICE_CHANGE/PHOTO_CHANGE/KM_CHANGE |
| `vehicle_cluster_run` / `vehicle_cluster` / `v_canonical_vehicle` | `migrations/0023_vehicle_cluster.sql:21,39,57` | Identidad instantánea cross-plataforma + patrón de gate `vam_verified` que la re-identificación temporal replica |
| `platform_listing` | `migrations/0009_platform_listing.sql:16` | Presencia multi-plataforma (C5) |
| `entity` | `migrations/0002_entities.sql:4` | Dealer de cada episodio (C6), provincia para guardas anti-FP |
| `verification_verdict` / `alert` | `migrations/0004_verification_health.sql:5,34` | Gate VAM de los runs + alertas del protocolo §7 |
| `GET /vehicles/{ulid}/history` | `services/api/routers/vehicles.py:24` | Endpoint base que se EXTIENDE (no se duplica) |
| `cardeep.vehicleHistory` + pestaña historial | `web/src/api/cardeep.ts`, `VehicleDetailModal.tsx:61-65` | Cliente y consumo frontend ya cableados al backend real |
| Patrón resolver batch | `pipeline/identity/cluster_vehicles.py` | Molde del motor de re-identificación (union-find determinista, guardas anti-FP, run auditado) |
| `inquisition_claim`/`inquisition_skeptic`/`inquisition_verdict` | `migrations/0032_inquisition.sql:29,59,90` | Mecanismo existente para adjudicar cadenas ambiguas en la muestra de verificación (§7/§8) |

### Se CREA nuevo (nombres PROPUESTOS — no existen aún, se confirman en F1)

1. **Migración `vehicle_lifetime`** (nueva, siguiente número libre de la serie `migrations/`):
   - `lifetime_link_run`: espejo estructural de `vehicle_cluster_run` (0023:21-34) — `run_id`, `resolver`, `resolver_version`, `scope`, `blocking_rules JSONB`, `n_in`, `n_chains`, `n_linked`, **`vam_verified BOOLEAN DEFAULT FALSE`**, `vam_verdict_id REFERENCES verification_verdict(id)`.
   - `lifetime_link`: eslabón `(run_id, vehicle_ulid_from, vehicle_ulid_to, match_signal, match_probability, evidence JSONB)` — `match_signal IN ('vin_ref','photo_hash','firma_corroborada')`, evidencia = las lecturas exactas que justificaron el eslabón (para C11).
   - Vista `v_vehicle_lifetime`: cadena servible del último run `vam_verified=TRUE` (mismo patrón que `v_canonical_vehicle`, 0023:57).
   - Overlay NO destructivo: ni una fila de `vehicle` ni de `vehicle_event` se muta jamás (doctrina PG MVCC del proyecto: cero UPDATE de filas no mutadas).
2. **Módulo pipeline `pipeline/identity/link_lifetimes.py`** (nuevo): resolver batch GONE→NEW con ventana temporal y guardas (§7). Se ejecuta tras `cluster_vehicles`, opera sobre unidades canónicas.
3. **Endpoint `GET /vehicles/{ulid}/lifetime`** (nuevo, dentro del router EXISTENTE `vehicles.py` — no un router nuevo): cadena de vida + agregados C1-C10 precalculados. Se añade a `docs/API_CONTRACT.md` con el mismo rigor de las 17 rutas selladas.
4. **Frontend**: se RECABLEA `Check.tsx`/`CheckLanding.tsx` al cliente real (`cardeep.ts`) y se REESCRIBE `CheckReport.tsx` a las secciones C1-C12; `DossierReport.tsx`, `useCheck.ts`, `useDossier.ts` y `web/src/api/client.ts` se ELIMINAN (autoridad de reestructuración concedida por el mandato; el mock no se deja convivir con el real). Los tipos `check.ts`/`dossier.ts` se sustituyen por tipos alineados al contrato nuevo — se conserva solo lo que el informe real usa.
5. **Nada más.** Explícitamente NO se crean: tabla de titularidad, tabla ITV, tabla de recalls, cache de informes (el cómputo C1-C10 es una agregación sobre índices existentes — si el perfil de latencia lo exige, la decisión de cachear se toma en F2 con medición, no ahora).

---

## 6. Especificación de pantalla — en la piel del dealer

El usuario primario es el **tasador/comprador del dealer** (jefe de compras de una compraventa, comercial de VO de un concesionario que tasa un coche de entrada o caza stock en subasta/particular). Su pregunta real no es "¿tuvo un accidente?" (eso lo mira en el informe DGT que ya paga) — es: **"¿este coche está quemado en el mercado?"**.

### Sección "Vida en mercado" (dentro de la ficha de vehículo y del modal de inventario existente)

- **Cabecera-veredicto**: el semáforo C9 con su etiqueta en lenguaje de dealer: "Sin señales de mercado" / "Con avisos" / "Coche quemado en mercado" — y debajo, SIEMPRE, la lista exacta de disparadores activados (la lista taxativa de C9, nunca un veredicto sin causas).
- **Línea de vida** (timeline horizontal): cada episodio de venta como un tramo — dealer (nombre real de la `entity`), plataforma(s), precio de entrada→salida, días. Los saltos entre episodios marcados con el chip de evidencia C11 ("misma unidad: VIN coincide" / "misma unidad: foto idéntica"). En lenguaje del gremio: *"Entró en Compraventa X (Málaga) a 14.900 € — 47 días — salió a 13.400 €. Reapareció 3 meses después en Autos Y (Sevilla) a 14.500 €."*
- **Los cuatro números que un tasador lee en 5 segundos** (fila de stats): Días en mercado (vida) · Bajadas de precio (y % acumulado) · Dealers que lo han tenido · Plataformas activas ahora. Cada uno clicable → despliega las filas de `vehicle_event` que lo sustentan.
- **Alerta km** (solo si C8 activa): bloque destacado con las DOS lecturas y las DOS fechas, texto exacto: "El km declarado pasó de 87.400 (12-mar) a 79.000 (28-jun). Verifícalo en la documentación." — informativo, jamás acusatorio.
- **Handoff institucional**: bloque final claramente separado, con borde y rótulo distinto: "Historial oficial (DGT)" → explica qué contiene el Informe de Vehículo oficial (titularidad, cargas, ITV), su precio (8,67 €) y enlaza al trámite oficial. Copy honesto: "Cardeep no tiene acceso a este dato. Este informe lo emite la DGT." Cero imitación del dato.
- **Entrada por búsqueda** (`/check` rehecho): busca por matrícula/VIN **contra el censo Cardeep** (`vehicle.vin_ref`); si no hay match, la pantalla lo dice sin rodeos ("Este vehículo no ha pasado por el mercado online español observado por Cardeep desde [fecha de inicio del censo]") y ofrece el handoff DGT. Patrón DVLA: paso de confirmación "¿es este el coche?" (make+model+foto) antes de mostrar el informe. NOTA: la utilidad real de esta búsqueda depende de la cobertura de `vin_ref` (hueco F0); si la cobertura es baja, la entrada principal es desde la ficha de vehículo y la búsqueda se degrada honestamente.
- **Anti-plantilla** (regla de diseño del proyecto): sin card-grid genérico; la línea de vida es la pieza central editorial; tokens del design-system existente; ambos temas.

Lo que el dealer NO ve: scores inventados, "informe completo" con secciones vacías estilo mock actual, ni una sola sección de titularidad/legal/ITV con dato no-DGT.

---

## 7. Protocolo de verificación — cada dato por ≥2 vías independientes

El estándar antialucinación del proyecto, aplicado al producto. Un dato solo se sirve si dos caminos independientes coinciden; si discrepan, se suprime y se alerta.

| Dato | Vía 1 | Vía 2 | Regla de discrepancia |
|---|---|---|---|
| Días en mercado (C1) | Cadena `vehicle_event` (NEW→GONE, `observed_at`) | Columnas `vehicle.first_seen`/`last_seen` (0003:23-24), mantenidas por el camino de escritura del scraper, no por el log de eventos | Divergencia > 24h → suprimir C1 de ese vehículo + fila en `alert` (0004:34) |
| Bajadas de precio (C3/C4) | Eventos `PRICE_CHANGE` | `platform_listing.platform_price` por plataforma (0009:23) + `vehicle.price` actual | Si el último `new_value` del log ≠ precio actual de tabla → suprimir + alerta |
| Eslabón de vida (C2/C6/C7) | Señal primaria del eslabón (vin_ref exacto O photo_hash exacto) | Señal corroborante independiente (la otra de las dos, o firma make/model/year + km monótono no decreciente + coherencia temporal GONE<NEW) | **Sin 2 señales independientes el eslabón NO se muestra** — puede existir en `lifetime_link` con probabilidad baja para análisis interno, pero jamás llega al frontend |
| Alerta km (C8) | Evento `KM_CHANGE` (old/new JSONB) | Re-lectura del `deep_link` origen (si sigue vivo) o del snapshot del episodio siguiente | Solo se muestra con ambas lecturas persistidas en `evidence` |
| Cadena completa (gate de run) | Motor determinista `link_lifetimes.py` | **Gate VAM humano/Director**: `lifetime_link_run.vam_verified=FALSE` por defecto (patrón exacto de 0023:16,31) — NINGÚN run se sirve sin gate | La vista `v_vehicle_lifetime` solo expone el último run verificado |
| Muestra pre-lanzamiento | — | Auditoría manual: N=50 cadenas aleatorias verificadas eslabón a eslabón contra los `deep_link` originales (o sus snapshots) antes del primer `vam_verified=TRUE`; precisión exigida ≥ 95% o el run entero se rechaza | El resultado de la muestra se persiste vía `inquisition_claim`/`inquisition_verdict` (0032) para auditoría permanente |

Regla de presentación: todo dato servible lleva su evidencia recuperable (las filas de evento que lo generan, vía el endpoint); el frontend nunca muestra un agregado cuyo desglose no pueda desplegarse. "Mejor confesar un hueco que vender una mentira" — literal en el copy del producto ("Cardeep no tiene acceso a este dato").

---

## 8. Uso de LLM (doctrina €0 del CLAUDE.md: local/barato para lo masivo, caro solo para decidir)

**El camino crítico es 100% determinista, cero LLM** — coherente con la doctrina de indexado pasivo del proyecto (IA fuera del camino crítico):

- Matching de identidad (vin_ref/photo_hash/firma), cómputo C1-C10, semáforo C9: SQL + union-find determinista. Sin modelo.

**Modelo LOCAL/barato (masivo, tolerante a error, siempre con validación posterior determinista):**

- Normalización de texto de versión/acabado para reforzar la señal "firma" en eslabones dudosos (p.ej. "320d Pack M" ≡ "320 d paquete M") — salida solo como señal AUXILIAR, nunca suficiente por sí sola para un eslabón.
- Clasificación de descripciones de anuncio en flags observacionales ("vendo por avería", "único dueño", "libro de mantenimiento") — se muestran como "declarado por el vendedor", claramente etiquetadas, nunca como hecho verificado.
- Pre-triaje de pares candidatos GONE→NEW cuando el bloqueo determinista deja ambigüedad (reduce el volumen que llega a revisión).

**Modelo CARO (solo decidir, nunca producir dato):**

- Adjudicación de la muestra de verificación pre-gate (los 50 casos de §7): razonamiento profundo sobre si una cadena ambigua es el mismo coche, alimentando `inquisition_skeptic`/`inquisition_verdict` (0032). Es una decisión puntual con impacto de gate, no un proceso masivo.
- Revisión adversarial del diseño del resolver antes de sellar F1 (patrón ya probado en el proyecto: Sonnet construye, el modelo profundo gatea).

**Explícitamente prohibido**: LLM generando cualquier campo del informe servido al usuario; OCR de matrículas desde fotos (sensible legalmente y fuera de alcance); "AI Damage Detection" estilo carVertical (sin dataset, no se promete).

---

## 9. Fases de construcción (orden estricto; cada una con criterio de verificación real)

**F0 — Cimientos y demolición honesta** (bloquea todo lo demás)
- Levantar stack (compose) y verificar por SQL directo: % de `vehicle` con `vin_ref` no nulo, % con `photo_hash` no nulo, distribución de `vehicle_event` por tipo, nº de pares GONE→NEW candidatos en ventana 0-12 meses. Esto cierra el hueco declarado en §1 y dimensiona F1.
- Cuarentena del vaporware: `useCheck`/`useDossier`/`client.ts`/`DossierReport.tsx` eliminados; `Check.tsx`/`CheckLanding.tsx`/`CheckReport.tsx` quedan detrás de una ruta desactivada hasta F3 (no se sirve maqueta ni un día más); limpiar el proxy huérfano :8506 de `vite.config.ts`.
- ✅ Verificación: números de cobertura persistidos en el tracker del pilar con la query exacta que los produjo; `npm run build` del web verde sin los archivos borrados; grep de `8506` y `useDossier` → 0 resultados; suite de tests existente sin regresión.

**F1 — Motor de re-identificación de por vida** (`link_lifetimes.py` + migración `lifetime_link_run`/`lifetime_link`/`v_vehicle_lifetime`)
- TDD: fixtures sintéticas primero (cadenas verdaderas, falsos amigos cross-provincia, km retrocedido, gemelos de flota con misma foto de catálogo — el caso trampa nº1) → RED → implementación → GREEN. Guardas anti-FP de §7 como tests explícitos.
- Run real sobre la DB + revisión adversarial del diseño (modelo caro, §8) + muestra manual N=50 (§7) → solo entonces primer `vam_verified=TRUE`.
- ✅ Verificación: precisión ≥95% en la muestra; run auditado en `lifetime_link_run` con verdict enlazado; cero UPDATE sobre `vehicle`/`vehicle_event` (verificado por inspección de queries); migración aditiva+reversible con rollback documentado como en 0003/0023.

**F2 — API** (`GET /vehicles/{ulid}/lifetime` en `vehicles.py`)
- Agregados C1-C10 computados server-side con las fórmulas EXACTAS de §4; contrato añadido a `docs/API_CONTRACT.md` y verificado contra `/openapi.json` en vivo (mismo estándar que las 17 rutas selladas); rate-limit y paginación coherentes con `vehicles.py:6`.
- ✅ Verificación: tests de router (incluido vehículo sin cadena, alias no canónico — paridad con el contrato de `history` línea 35-37, y discrepancia dual-path → dato suprimido); curl real contra :8090; medición de latencia p95 — decisión de cache SOLO si la medición lo exige.

**F3 — Frontend "Vida en mercado"**
- Recableo de `Check.tsx`/`CheckLanding.tsx` a `cardeep.ts`; reescritura de `CheckReport.tsx` a las secciones de §6; upgrade de la pestaña historial del `VehicleDetailModal` para enlazar a la vida completa; handoff DGT.
- Sujeto al protocolo frontend del proyecto: nada se muestra al owner sin funcionar contra la API viva; estándar visual del design-system, ambos temas.
- ✅ Verificación: flujo real navegado (browser real) contra datos reales; cada número de la pantalla trazado a su criterio C# en la revisión (checklist literal); screenshots en breakpoints; cero fetch al cliente muerto; build+lint+tsc verdes.

**F4 — Blindaje de verificación continua**
- Implementar los cruces dual-path de §7 como job periódico + escritura en `alert` (0004); wiring al patrón de salud existente; muestreo continuo post-lanzamiento vía `inquisition_*`.
- ✅ Verificación: inyectar discrepancia sintética en staging → el dato desaparece del endpoint y la alerta salta con origen exacto; test de regresión que lo cubre.

**F5 — Dato institucional (CONDICIONADA a decisión de gasto/legal del owner — no bloquea F0-F4)**
- Explorar convenio DGT (INTV), relación con red ITV, y —si el alcance se abre a importados— RDW SODA (abierta, CC0). Cada fuente entra por el mismo protocolo §7 (2 vías) y con dossier legal/ToS previo, igual que el gate KNOW_COUNTRY del autopilot.
- ✅ Verificación: no aplica hasta desbloqueo; el criterio de entrada es contrato/acceso firmado, no scraping especulativo de un registro estatal.

---

## Resumen

El pilar 02 hoy es una fachada Carfax sin un byte real detrás (Check/Dossier, cliente y proxy huérfanos, tipos alineados a un backend Go que no existe) más un activo genuino enterrado: el delta append-only `vehicle_event` servido por `/vehicles/{ulid}/history`. La jugada no es imitar a Carfax —sin acceso institucional sería mentir, y GANVAM ya ocupa el passthrough DGT— sino construir el historial que nadie tiene: la **vida en mercado por unidad física** (re-identificación GONE→reaparición con doble señal y gate VAM, días en mercado, bajadas, rebotes entre dealers, km declarado que retrocede), 100% trazable a filas reales, con semáforo taxativo estilo DGT y handoff honesto al informe oficial. Camino crítico determinista, LLM barato solo para señales auxiliares y el modelo caro solo para gatear cadenas ambiguas; cinco fases con demolición del mock en F0 y verificación dual-path de cada dato antes de mostrarlo.
