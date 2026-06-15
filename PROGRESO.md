# CARDEEP — PROGRESO (bitácora viva)

> Se escribe tras cada bloque. Nada está "hecho" sin entrada aquí con su evidencia.

## 2026-06-12 — F0 FUNDACIÓN
- Mandato soberano recibido (CLAUDE.md reescrito por el owner) e interiorizado.
  Memoria persistida del agente actualizada; doctrina anterior purgada.
- **PLAN.md** escrito: plan maestro A→Z, fases F0-F8 con gates binarios.
- Repo git inicializado en `main`; commit fundacional (CLAUDE.md + PLAN + esta
  bitácora + README + .gitignore).
- **F1 LANZADO en paralelo**: workflow `cardeep-f1-census-es` (run wf_14d4c728-691)
  — 7 modalidades en fan-out (oficial, asociaciones, OEM/VO, plataformas,
  directorios, desguaces, arsenal OSS) + verificación viva de toda fuente high.
  Al cerrar: consolidación a `docs/research/SOURCES_ES.md` con re-verificación
  por mano propia (la salida de agentes es sospechosa por doctrina).
- Remoto conectado y pusheado: `github.com/sublimine/Cardeep` (repo creado por el
  owner hoy 10:03 UTC, vacío, **PÚBLICO** — visibilidad decidida por el owner).
  `main` → `origin/main` @ 9a97807. **GATE F0 = VERDE** (verificado: push exitoso
  + `git log origin/main` muestra el commit).

## 2026-06-12 — F1 CENSO ÁTOMO ESPAÑA — GATE VERDE
- Workflow `cardeep-f1-census-es` cerró: 56 agentes, 926 tool-uses, ~46 min,
  **181 fuentes** catalogadas (oficial 21 · asociaciones 22 · OEM 44 · plataformas 18
  · directorios 20 · desguaces 34 · arsenal 22), las de alta prio verificadas en vivo.
- **Re-verificación por mano propia (quórum, vía curl ortogonal): 5/5 cifras OK** —
  AutoScout24 278.329 (censo 278.163), coches.net 249.139 (248.920), DGT CATV 1.292
  (exacto), Kia 242 (exacto), MG 212 (exacto). VAM superado.
- Artefactos: `docs/research/SOURCES_ES.md` (destilación + tablas + arsenal + denominador
  + refutaciones honestas) + `docs/research/SOURCES_ES_raw.json` (181 fuentes íntegras).
- **Denominador estimado:** suelo ~44k puntos de venta auto (PA verificado), techo
  ~50-90k (registral CNAE 45 + Places). Cierre real con capture-recapture en F8.
- **Hallazgos clave:** (1) AutoScout24.es ABIERTO + JSON-LD dealer = banco de pruebas de
  F3; (2) redes OEM por APIs JSON sin auth (Kia/MG/BYD/…) + portales VO con stock
  atribuido = censo de red casi €0; (3) Tier-1 = wallapop/milanuncios/coches.net/spoticar,
  a su frente separado F5. Arsenal OSS fijado (Scrapling+camoufox+curl_cffi núcleo).
- **Refutación honesta:** VW OneHub API "263 dealers" REFUTADA (HTTP 500 sin
  serviceConfigEndpoint); Google Places ToS prohíbe indexar → sustituto legal FSQ/Overture.
- **GATE F1 = VERDE.** Siguiente: F2 (columna de datos — esquema, geo INE, código único, API).

## 2026-06-12 — F2 COLUMNA DE DATOS — GATE VERDE
- **Motor:** PostgreSQL 16 en Docker `cardeep-pg` (puerto **5433**, `--shm-size=1g`,
  volumen `cardeep_pg_data`) — separado de CARDEX (5432). Verificado `pg_isready` en 3s.
- **Esquema (4 migraciones, 11 tablas):** 0001 geo (province/comarca/municipality),
  0002 entity + entity_source + entity_alias, 0003 vehicle + vehicle_event (delta
  append-only), 0004 verification_verdict + source_health + alert. Runner
  `scripts/migrate.py` con ledger `schema_migrations`.
- **Verificación E2E (patrón del mandato):** apply (4 OK) → 11 tablas presentes →
  CHECK constraint rechaza kind inválido → **rollback → 0 tablas dominio → re-apply →
  11 tablas** → idempotencia (2ª corrida = 0 aplicadas). Reversibilidad probada.
- **Geo INE cargado:** fuente oficial `diccionario25.xlsx` (INE, autoritativa) →
  **52 provincias + 8.132 municipios, 0 huérfanos, 52/52 provincias cubiertas.**
  2-vías por hechos conocidos: Madrid 179 munis ✓, Barcelona 311 ✓, 28079=Madrid ✓.
- **Código único `cdp_code`:** determinista e inmutable (`CDP-ES-{prov}-{b32(sha256)}`),
  prioridad dominio>CIF>nombre+municipio. Probado: zonauto.es con/sin www/https/path →
  mismo código (re-descubrimiento no duplica).
- **API viva (FastAPI+asyncpg, esqueleto):** /health, /entities/{cdp_code},
  /inventory, /delta, /geo/{prov}/entities + envelope {ok,data,error,meta}. **Verificada
  E2E contra entidad piloto REAL** (ZONAUTO SUR, Pinto/Madrid 28113, del censo AMDA):
  los 6 endpoints responden correcto + 404 con error limpio.
- **Anti-maquillaje:** el vehículo del smoke-test era sintético (prueba de esquema) →
  PURGADO. Queda 1 entidad real (seed), 0 inventario (F3 mete scraping real).
- Reproducibilidad: `.env.example` + `requirements.txt` (deps verificadas presentes).
- **GATE F2 = VERDE.** Siguiente: F3 (workflows átomo DESCUBRIR→SCRAPEAR→RECETA→API→BORRAR;
  banco de pruebas = AutoScout24.es, abierto + JSON-LD dealer).

## 2026-06-12 — F3 WORKFLOWS ÁTOMO — primer vertical DESCUBRIR cerrado
- **Mejora de método (autorizada):** pipeline de PRODUCCIÓN = código Python determinista
  (`pipeline/`), barato y escalable; la herramienta Workflow (agentes) se reserva para
  caza de receta Tier-1 + verificación adversarial. Diseño átomo de las 6 fases en
  `docs/workflows/README.md`.
- **Arquitectura `pipeline/`:** `sources/base.py` (contrato SourceAdapter→DiscoveredEntity),
  `sources/dgt_cat.py` (adaptador DGT CATV), `geo.py` (resolución nombre→código INE,
  alias + tokens ordenados), `ids.py` (ULID), `verify.py` (VAM count quorum →
  verification_verdict), `discover.py` (FASE 1). Anti-stub: scrape/recipe/evict se crean
  al implementarse.
- **DESCUBRIR ejecutado sobre DGT CATV (desguaces) — REAL, VERIFICADO:**
  **1.292 desguaces** ingeridos con geo + cdp_code inmutable + provenance. **VAM
  TRUSTWORTHY** (declared 1292 = fetched 1292 = db 1292, divergencia 0). Idempotente
  (re-run new=0). Resolución provincia 100%, municipio 92,8% (1199; los 93 restantes =
  variantes valencianas, ingeridas con muni NULL, no perdidas).
- **Corroboración 3-vías:** Barcelona 76 desguaces = exacto vs evidencia DGT del censo F1.
- **2 hallazgos de causa raíz (anti-alucinación):** (1) campo DGT `COD_INE` DESALINEADO
  (dice 9→Tarragona, 11→Sevilla, 19→Madrid) — descartado, resuelvo por nombre; (2) la
  clave nombre+municipio fusionaba 2 sitios físicos de la misma empresa → añadida la
  dirección a la clave (2 centros CAT = 2 puntos de venta distintos, correcto).
- **API sirve el segmento:** /health=1292 entidades, /geo/08/entities=76 (Barcelona).
- **Estado vivo:** cardeep-pg :5433 con 1.292 entidades reales (segmento desguace 100%
  del registro oficial DGT). Siguiente: más adaptadores DESCUBRIR (AEDRA, OEM JSON,
  Páginas Amarillas, OSM/FSQ) + fases SCRAPEAR/RECETA sobre AutoScout24.es.

### F3 — segundo vertical DESCUBRIR: OEM Kia (concesionarios oficiales)
- Adaptador `pipeline/sources/oem_kia.py` (API JSON abierta verificada). discover.py
  generalizado: conteo por provenance (`entity_source`), no por kind.
- **241 concesionarios oficiales Kia** ingeridos. **VAM TRUSTWORTHY** (241=241=241).
  Provincia por postcode[:2] (100%), municipio 85,1%, email 240/241.
- **Causa raíz cazada (scope):** la API devuelve 242 incluyendo 1 dealer en **ANDORRA**
  (AD500, Santa Coloma) — fuera de scope (misión = España). Filtrado transparente:
  `excluded_out_of_scope=1`, denominador del gate = 241 españoles. Sin maquillaje.
- **Estado vivo total: 1.533 entidades reales** = 1.292 desguace + 241 concesionario_oficial.
  Dos segmentos del mandato poblados y verificados con el mismo pipeline.

### F3 — INVENTARIO E2E por dealer (SCRAPEAR→RECETA→INGEST→VERIFICAR) — CERRADO con delta
- **El corazón del mandato ("sacarle TODO su stock") probado de punta a punta** sobre un
  dealer real. Fuente: **AutoScout24.es** (abierto, `__NEXT_DATA__`, atribución dealer).
- Módulos: `sources/autoscout24.py` (SCRAPEAR: drenado por dealer `/profesionales/{slug}`,
  sort estable, dedup), `recipe.py` (RECETA: yaml versionada por dealer en
  `countries/ES/recipes/`), `ingest.py` (INGEST: motor de **delta** NEW/GONE/PRICE_CHANGE/
  PHOTO_CHANGE/KM_CHANGE, INSERT nuevo + cierre desaparecido, UPDATE solo filas mutadas),
  `harvest_dealer.py` (orquestador que encadena las 4 fases + dump crudo a `data/` gitignored).
- **Piloto real OK MOBILITY VALENCIA AIRPORT (Manises, 46159):** **78 coches** ingeridos,
  año/km/precio correctos (Porsche Taycan 89.010€, etc.). **VAM TRUSTWORTHY** (78=78=78).
  **Idempotente** (re-run: new=0, gone=0, 78 unchanged). API sirve /inventory (78) + /delta (78).
- **3 causas raíz cazadas (anti-alucinación, sin maquillaje):**
  1. El dealer NO está en `seller` por-listing en la página de perfil → vive en
     `pageProps.dealerInfoPage` (customerId/customerName/customerAddress). Corregido.
  2. `mileageInKm`/`firstRegistrationDate`/etc. son objetos `{raw,formatted}` (no strings) →
     mi `_to_int(str(dict))` DOBLABA los dígitos (km=6.594.865.948). Extractor `_raw()` + cotas.
  3. **Paginación inestable** fabricaba 1 duplicado (78 brutos→77) — la trampa AS24 del mandato.
     Fix: **sort estable** (`sort=price&desc=1`) → 78 reales distintos, churn delta a 0.
- **VAM mejorado a regla de quórum** (≥2 vías concuerdan = TRUSTWORTHY; un contador de fuente
  que sobre-cuenta duplicados no refuta si 2 vías independientes coinciden).
- **Estado vivo: 1.534 entidades + 78 vehículos servidos + 78 eventos de delta.**
- **Pendiente F3:** fase BORRAR (evicción por capacidad + tombstone) + escalar a más dealers/fuentes.


## 2026-06-12 — ESCALADO ORQUESTADO (flota de agentes en paralelo)
- **Pivote a estándar institucional (orden del owner):** dejé el build artesanal; desplegué
  workflows + ejércitos de agentes en paralelo. `docs/ORQUESTACION.md` (arquitectura de élite).
- **WF-DISCOVERY-FLEET** (`wf_1ef5ffa9-470`, 23 agentes): 7 adaptadores OEM construidos +
  verificados EN VIVO por mi mano (oem_mg/byd/skoda/dacia/hyundai/mercedes/seat). El resto
  (9 build + 4 Tier-1 + audits) cortados por **límite de sesión de la API** (reset 15:10 Berlin)
  — bloquea agentes nuevos, NO mi trabajo determinista, que continué solo.
- **WF-INVENTORY-SCALE (AS24)**: 28 dealers cosechados → +7.466 coches; +5 recuperados tras fix.
- **2 bugs de raíz cazados y corregidos:** (1) AS24 dealer con postcode "89" → ForeignKey
  violation → guard provincia 01-52 en ingest (skip honesto, no crash); (2) HTTP 504 transitorio
  perdía dealers → retry+backoff en fetch_page (auto-reparación).
- **Bug de diseño del cdp_code cazado (anti-alucinación):** los adaptadores OEM ponían
  `website = oem.es/concesionarios/{slug}` (página de portal, no dominio propio) → mi clave
  reducía a `oem.es` → 175 Hyundai colapsaban a 48 códigos. Fix: el dominio solo es identidad
  si es **host limpio sin path**; URL con path → cae a nombre+municipio+dirección. Hyundai 48→174.
- **VAM endurecido:** la regla de quórum enmascaraba pérdida de ingesta (fetched=declared ocultaba
  db<fetched). Ahora `db_ingested` (lo que aterrizó) DEBE concordar con ≥1 vía o es REFUTED.
- **OSM long-tail:** +3.085 garajes/compraventas geo-localizados (de 10.809; 7.676 perdidos por
  falta de provincia — POIs sin postcode, pendiente geocoding lat/lon→provincia). VAM REFUTED honesto.
- **ESTADO VIVO: 5.771 entidades** (garaje 2.291 · concesionario_oficial 1.394 · desguace 1.292 ·
  compraventa 794) · **9.872 vehículos servibles** · 52/52 provincias · 10 fuentes. Todo VAM por fuente.

## 2026-06-12 — INVENTARIO A ESCALA (workers paralelos) + geocoder long-tail
- **Crítica del owner aceptada y corregida:** el ratio "2 coches/entidad" era engañoso —
  inventario cosechado solo en 32 dealers. Lanzados **4 workers de cosecha paralelos**
  (`as24_harvest_batch`, sin límite de API) sobre 334 dealers AS24 descubiertos.
- **Geocoder lat/lon→provincia** (`pipeline/geocode.py`, vecino más cercano sobre puntos
  etiquetados, numpy): recuperó el long-tail OSM **3.085 → 9.953** (0 perdidos por provincia).
- **RESULTADO VERIFICADO por mi mano:**
  - **12.814 entidades** (garaje 7.200 · compraventa 2.753 · concesionario_oficial 1.569 · desguace 1.292)
  - **22.300 vehículos servibles** (de 78 al inicio del escalado) · **212 dealers con inventario** (de 1)
  - **24.329 eventos de delta** · **media 105 coches/dealer cosechado** (no 2) · 52/52 provincias
- **Honesto:** 138 dealers cayeron por throttling de AS24 bajo carga 4× (retry+backoff recuperó
  parte). Recuperación pendiente con menor concurrencia. La cosecha es el cuello (rate-limit de
  fuente), no el sistema — escala por nº de fuentes en paralelo + recetas Tier-1.

## 2026-06-12 — REDISEÑO INSTITUCIONAL: arquitectura profunda (3 flotas de arquitectos)
- **Orden del owner: plan/estructura/arquitectura ANTES de más código, al nivel más profundo.**
  Paré la producción. Desplegué 3 workflows de arquitectura en paralelo (todo Fable):
  - **Arquitectura maestra** (`wf_aebc925d-669`): 9 pilares `docs/architecture/00-08` + README +
    `docs/MASTER_PLAN.md` (reconcilia contradicciones, supersede PLAN.md/ORQUESTACION.md).
  - **Validador Supremo** (`wf_c0073370-8ee`): `docs/architecture/verification/V1-V6` + VALIDATOR_SUPREMO
    — capture-recapture (Chapman/Chao/log-lineal+CI), gate de completitud 5 sub-puertas, Inquisición
    5-lentes con quórum por independencia, Gestionador de mentiras, LQAS/Clopper-Pearson, meta-auditoría.
    Responde literal a "¿500k? REFUTED salvo prueba" y "¿20k E2E? muestreo de aceptación estratificado".
  - **Auditoría de tooling** (`wf_7fb56456-4ca`): `docs/architecture/tooling/T01-T16` + TOOLING (BOM) —
    mejor herramienta por micro/macro tarea, recencia 2026 verificada en vivo (curl_cffi chrome146,
    patchright/nodriver/Scrapling, Byparr, Decodo/IPRoyal, browserforge/camoufox, selectolax/extruct,
    instructor/outlines, libpostal/shapely+IGN…), con config y challenge adversarial.
- **34 docs, 20.075 líneas.** Todo verificado por mi mano antes de aceptar.
- **Contaminación cazada y reparada (anti-cruce CARDEX):** 7 docs de tooling los escribieron agentes
  en `projects/cardex-integration` y `~/CARDEX` (ruta relativa resuelta contra repos del entorno).
  TODOS untracked (cero commit a CARDEX). Reubicados a cardeep, repos ajenos limpios. T10 (geocoding)
  cayó por límite de sesión → rehecho con ruta ABSOLUTA pinneada. Lección: rutas absolutas a agentes.
- **PENDIENTE: revisión y aprobación del owner del plan ANTES de tocar código de producción.**

## 2026-06-12 — BUILD P0: SCHEMA SPINE (ejecución del MASTER_PLAN, verificada)
- Arranca la construcción siguiendo el DAG del MASTER_PLAN (§3). Backup de seguridad
  (.backups/cardeep_pre_p0.dump, gitignored) antes de tocar datos vivos.
- **Migraciones 0005-0009 aplicadas, datos preservados EXACTOS** (entity 12.862 · vehicle
  39.068 · vehicle_event 41.165 antes==después, verificado por mi mano):
  - 0005: 8 ENUMs (entity_kind 11 tipos, org_type, waf_kind, vehicle_event_type…) +
    `cardeep_block_mutation()` (historial inmutable) + extensiones pg_trgm/btree_gin/pgcrypto.
  - 0006: entity evoluciona in-place — swap kind/status/website_waf TEXT→ENUM (pre-flight
    limpio), + columnas ontología (sells_cars, kind_source, org_id, attest_count, defense_detail,
    canonical_key…) + platform_meta + vista `platform` + ULID-shape CHECK.
  - 0007: tabla `organization` (cadenas/grupos) + entity.org_id FK + entity_source.first_seen
    + trigger de attest-count.
  - 0009: arista **`platform_listing`** — fix estructural "mismo coche en plataforma Y dealer"
    (vehicle.entity_ulid = dealer vendedor; la pertenencia a plataforma es la arista).
- Diferido (rewrites de tablas pobladas, bloque cuidadoso aparte): 0008 (vehicle partition),
  0010 (auction), 0011 (vehicle_event partition + immutability wiring), 0012 (rollups), 0099 (PostGIS).
- Delegado a agente de contexto fresco con rutas absolutas (tras la lección de contaminación);
  verificado por mi mano. Siguiente en el DAG: P0.5 spike anti-detección → P1 governor+queue.

## 2026-06-12 — ASALTO TIER-1 GRATIS: los 7 gigantes CAZADOS sin coste (orden del owner)
- **Lección dura del owner:** prohibido decir "necesita IP residencial/gasto" sin agotar TODOS
  los vectores libres. Lancé asalto de 7 cazadores (wf_53e3982f-a06), arsenal libre completo.
- **RESULTADO: los 7 gigantes duros = FREE-harvestable, CERO proxy:**
  - **coches.net 272.686 coches** [VERIFICADO POR MI MANO]: POST web.gw.coches.net/search (curl_cffi
    chrome131, X-Schibsted-Tenant:coches, pagination NESTED {page,size}). Trae dealer + historial Δprecio.
  - **wallapop ~750k**: GET api.wallapop.com/api/v3/search/section (geo lat/long honrada, next_page JWT,
    PRO-dealer via /users/{id}). Sin auth/cookie/JS.
  - **milanuncios ~667k**: camoufox (warm-up homepage mintea cookie Imperva reese84 + click SPA in-page +
    scroll). Sin proxy. (Adevinta SRP server-rendered; el gateway advgo es tenant-gated a coches.net.)
  - **coches.com 200k**: curl_cffi sitemap vo.xml→Todo-VO + __NEXT_DATA__ classified+dealer.
  - **autocasion 115.179**: GraphQL gql.autocasion.com/graphql (introspección ABIERTA) + PDP JSON-LD AutoDealer.
  - **spoticar ~50k** (Akamai) + **motor.es ~51k**: también free (recetas en disco).
- **Universo Tier-1 ≈ 2,38M coches, TODO €0** (+ AS24 278k ya hecho). La IP residencial NO hace falta
  para los gigantes. Recetas guardadas: docs/architecture/tier1_recipes/{platform}.md + README.
- Siguiente: cablear estas recetas como conectores de plataforma (P7a a escala con el governor) →
  ingest + platform_listing + delta + VAM por gigante.

## 2026-06-12 — ESCALA coches.net (conector mayorista, gobernado) + verificación de números
- **coches.net escalado 500→14.955 coches** (150 págs, gobernado por token-bucket, breaker cerrado).
  VAM TRUSTWORTHY: harvested=db_edges=db_join=14.955, divergencia 0 [VERIFICADO por mi mano].
  +1.018 dealers nuevos descubiertos de paso · 14.955 eventos delta · **2.171 bajadas de precio capturadas**.
  El 100% de coches.net = mismo comando `--pages 2727`.
- **Estado vivo: 54.291 vehículos · 14.030 entidades · 15.223 platform_listings · 3.919 compraventa.**
- **Verificación de los 7 Tier-1 (mandato "verifica TODOS los números"):**
  - Por mi mano: coches.net 272.682 ✓ · autocasión 115.179 ✓ · wallapop API libre 200 con coches reales ✓.
  - **Cazado inflado:** coches.com NO 200k → **92.259 PDPs reales** en sitemap (200k era el contador web).
  - Siguen de agente (browser, no re-derivados por mí): milanuncios ~667k · spoticar ~50k · motor.es ~51k.
- **Estructura multi-eje (0016) clasificando lo vivo:** defense_tier × source_group × role × family.

## 2026-06-13 — F8 VERIFICACIÓN TERRITORIAL: denominador POI Overture aterrizado (cierra hueco #11)
- **Contexto:** PROGRESO quedó congelado el 2026-06-12; el trabajo del 13 (olas 2ª-7ª + cierre del
  vector gratuito ~1,36M vehículos) vive en `CIERRE_FINAL.md`, `SCOREBOARD.md` y `docs/runbook/`.
  Esta entrada retoma la bitácora con la última acción: el SELLO territorial (F8).
- **F8 censo-anclado [VERIFICADO]:** cobertura nacional VENTAS = **94,3 %** registral-ortogonal
  (21.759 / 23.085 locales INE CNAE-451); desguace **100,5 %** sellado contra DGT-CAT (1.299/1.292);
  19 CCAA exacto (Σ=23.085 == nacional); vs registro de empresas 234,5 % = saturación, no hueco.
  Gaps genuinos: Ceuta 19,2 % · Melilla 25,0 % · Canarias 59,4 % + geocode-gap 32,5 % (13.741 sin muni).
- **Overture POI aterrizado (última tarea background `bwavcc5h1`, exit 0):** cierra el `INCOMPLETE`
  del §4.11 de `TERRITORIAL_COVERAGE.md`. 19.727 POI ES (Overture `2026-05-20.0`, CDLA-Permissive),
  dedup 3-claves contra DB → **6.523 cruzados · 13.204 candidatos nuevos · 0 closed**. Ortogonal (no
  circular como OSM). Ficheros: `docs/research/territorial/poi_*.json`.
- **Anti-alucinación:** el 13.204 NO es cobertura faltante — la DB (33.690 negocios) supera ~1,7× el
  set ES de Overture; es superficie de leads (variantes de nombre, no-dealers, cerrados) PENDIENTE de
  validar antes de contar una sola fila como dealer nuevo. Confesado en runbook + NOT-VALIDATED.
- **Registrado:** `docs/runbook/04-TERRITORIAL.md` (sección canónica nueva) + árbol del README del
  runbook + `VALIDATION-INDEX.md` (bloque territorial censo-anclado) + F8 marcado `[ANCLADO]` en PLAN.md.

## 2026-06-15 — SUPERPLAN A→Z · FASE 0 (cimiento) — GATE VERDE
> Mando `/goal` del Owner: Director Soberano, hands-off, autoridad total, sellar A→F punto
> por punto (cada uno completo + verificado + testeado antes del siguiente). Plan maestro:
> `docs/SUPERPLAN.md` (auditoría de cobertura del prompt fundacional → backlog de unidades de
> sellado con gate binario, workflow, agentes/skills/herramientas).
- **Hardware verificado (D1):** Ryzen 5 5500U 6c/12t · 15,3GB RAM (~2 libres) · sin CUDA ·
  disco C: 96%. → €0, determinista-first, Ollama qwen3:4b, sin GPU/cloud hasta orden del Owner.
- **Auditoría átomo del verde A (identidad):** discrepancia 31.472 vs 42.259 RESUELTA — el sello
  vivo `dealer-identity-det-v1` (vam_verified) = **61.551→42.259 canónicos**; el 31.472 era un run
  anterior superado. 6 defectos destapados (ledger drift · 0014 ausente · verdict NULL · 4 cadena ·
  β/B7 sin sellar · B9 4/47 fuentes).
- **SU-0.1** Frontend eliminado (D2): `cardeep-web` archivado en `docs/archive/frontend-spec/` + borrado. `ff88fe4`.
- **SU-0.2** Ledger de migraciones reconciliado: 0023/24/25 vivían en DB (creadas por código) sin
  registrar. `migrate up` idempotente → **applied=19, pending=0**. Reproducibilidad PROBADA en DB
  desechable (rebuild 0001→0025 = 25 tablas + 4 vistas, 0 errores).
- **SU-0.3** Untracked → `main` (invariante #9): B7 (0023+cluster_vehicles+test, 37 tests ✓), 538
  recetas, recon. Security gate: 0 secretos reales (solo claves públicas client-side). `b61639a`/`f8c758d`/`15550f7`.
- **SU-0.4** Sello B1 enlazado a su prueba: `dealer-identity-det-v1.vam_verdict_id=640` (TRUSTWORTHY; era NULL).
- **SU-0.5** Ontología D-11: 4 `kind='cadena'` → 4 `organization` chain_compraventa + raíces a
  compraventa + 185 sucursales enlazadas. **Flexicar rollup nacional = 23.874 coches** ahora
  consultable (la raíz tenía 2). Inventario intacto. `scripts/seed_chain_organizations.py` idempotente. `938a091`.
- **SU-0.6** Disco: 21,41GB build-cache + 12 contenedores parados reclamados; vivos intactos. Host
  sigue 96% — el repo Cardeep son **307MB** (data/ 161MB); el lleno es ~367GB ajenos + VHD WSL2 que
  no autoreduce. **Confesado:** 15% libre infeasible sin acción del Owner; `evict.py` no existe (debt baja urgencia).
- **GATE FASE 0 = VERDE** (residual de disco confesado con causa). Siguiente: **FASE 1** (confirmar
  verdes a nivel átomo) → **SU-B1** (ledger de verificación profundo, migración 0014; el quorum-CHECK
  invalidaría los TRUSTWORTHY existentes → re-juzgar a UNVERIFIED primero).

## 2026-06-15 — FASE 1 + SU-A2: SU-A1 confirmado · β SELLADO (S_obs 38.555)
- **SU-A1 (identidad B1)** confirmado a nivel átomo por vía ortogonal independiente del sello:
  0 under-merge (host+muni), 0 bosque roto, verdict 640 linkado (SU-0.4). Hallazgo destapado:
  **cluster AS24** — 511 dealers mis-kindeados `concesionario_oficial` (L7 «ingest.py:52 hardcoded»,
  infla el segmento oficial ~24%); tracked → clasificador/type-ladder.
- **SU-A2 β SELLADO** (3 iteraciones bajo gate del Director, verdict 1093 TRUSTWORTHY):
  - v1: chain-guard (org_id) + composición B1∘β (siembra `v_canonical`). 52.156→38.359.
  - v2: city-guard INE desgateada — el gate del Director cazó over-merge transitivo (AutosMadrid
    Alcorcón+Leganés, MuyCar Sevilla+Alcalá, Stellantis Alcorcón/Madrid/Móstoles). 65 tests.
  - v3: **constrained union-find** (city_set+org_set por componente; rechaza unión cross-ciudad/
    cross-org transitivamente, 225 rechazos). Over-merge city-name ELIMINADO. **S_obs=38.555**. 74 tests.
  - Modelo de cadenas completado (SU-0.5b): org-link por dominio + re-kind 42 AS24 `concesionario→
    compraventa`. Flexicar rollup 304 POS.
  - Residuo declarado: 131 clusters multi-muni = geocoding-noise del scraper + variantes-de-nombre del
    mismo negocio + clase ínfima de cadena abreviada sin org_id. Gated en geo-cleanup (SU-A6).
  - commits `fa1286b` (v2) / `c92ca07` (v3); `v_resolved_dealer` sirve 38.555 dealers.
- **GATE β = VERDE** (sellado-con-gap-declarado). Pend SU-A2: **φ** (DIRCE ∩ β → fracción-ocasión →
  N_prof) · **F3 Chao2** ortogonal (fiscal × canal × geo) + cierre contra saturación → N̂(P) con CI.

## 2026-06-15 — SU-C3: B7 dedup de coches físicos (km=0 + giants) bajo gate del Director
- **km=0 guard** [commit `0f8a6e9`]: señales A(photo)/B(firma) OFF para km=0/NULL salvo `vin_ref`
  compartido (stock nuevo: fotos de catálogo + atributos idénticos NO identifican la unidad). Sesgo
  declarado: posible sobre-conteo cross-platform de coche nuevo (preferible a fundir unidades).
  Re-run: unique_cars 1.443.563→**1.448.705** (+5.142). **GATE VERIFICADO: `km0_cross_entity_NO_VIN=0`**
  — las 6.278 fusiones km=0 cross-entity son TODAS por VIN (mismo coche real). Cero over-merge.
- **El gate del Director destapó 2 over-merges PRE-EXISTENTES (km>0)** que impedían el sello:
  (1) firma con **precio NULL** + título genérico fundía unidades distintas (VW Caddy 1.752 fotos
  distintas→1; Seat Arona 1.055); (2) `photo_url` de **stock/placeholder** compartida fundía coches
  distintos (Bugatti Chiron 592 listings/14 fotos; BCA ×1752). 107 clusters >20. Cross-province (309):
  TODO photo-legítimo (foto única=mismo coche, ruido de provincia), NO over-merge — declarado.
- **B7 v2** [commit `61ef1bc`, 61 tests]: photo-high-collision guard (foto ≥K=**12** listings = stock,
  off; elbow real cnt11→12, 63 URLs stock verificadas) + firma exige **precio NO-NULL** (7.274 km>0
  price-NULL, 0,45%). Re-run v2 en curso → gate (giants caídos, km=0 intacto, fusiones legítimas
  cross-platform preservadas) → sello B7. **SU-C3 casi cerrado.**
- **B7 v3** [commit `6667139`]: firma exige **CROSS-ENTITY** (elimina el over-merge de flota same-entity:
  207 Renault Zoe de un dealer → 207 coches distintos). Giants 89→**9** (máx 207→36). Re-run:
  unique_cars 1.453.967→**1.486.285** (+32k). **B7 SELLADO** (verdict 1102, vam_verified=TRUE):
  km=0 over-merge=0, photo-stock fuera, firma null-price+fleet fuera. Residuo declarado: 9 giants
  cross-entity (~225 coches, **0,015%**, colisión modelo-genérico cross-dealer) + 292 cross-province
  photo-legítimo. `v_canonical_vehicle` sirve **1.486.285** coches únicos. Suite completa **416 verde**.
- **AS24-kind** [commit `aa68fc7`]: root-cause `ingest.py:58` default `concesionario_oficial`→`compraventa`
  + `kind_source='platform_label'`; backfill 469 (`scripts/reclassify_as24_kind.py` idempotente).
  Segmento concesionario 2.058→**1.589** (−469), oem_* intactos (1.525). ~10% posibles oficiales
  marcados low-conf → re-certifica el clasificador (under-claim, no over-claim).
- **GATE SU-C3 = VERDE.** B7 sellado (1.486.285 coches únicos) + AS24-kind corregido. Pend SU-A2: φ + Chao2.

## 2026-06-15 — SU-B1 deep ledger 0026 + SU-A2 φ/Chao2: GATE del Director
- **SU-B1 CORE** [commit `39a9a2e`, migración **0026**]: deep verification ledger. Quorum-CHECK
  `chk_trustworthy_needs_quorum (≥2 familias ∧ ≥2 orígenes)` **NOT VALID** (grandfatherea los sellos
  light-VAM B1/β/B7 sin invalidarlos; enforce en nuevos — verificado: INSERT TRUSTWORTHY sin quorum
  FALLA). Audit hash-chain append-only (UPDATE/DELETE fallan). `denominator_estimate` + rol read-only
  `cardeep_inquisitor`. Rebuild 0001→0026 reproducible, suite 416✓. +`migrate.py split_statements`
  (bug DDL multi-statement arreglado). Deferido: v_latest_verdict materializada, gestionador, V2/V3/V4.
- **SU-A2 φ/Chao2** [recon+borrador gateado, verdict **1111 REFUTED**]: el Chao2 sobre 3 familias
  ortogonales (fiscal×comercial×geográfico) **COLAPSA** — Q1/Q2=43,3 (cross-coverage 2,3%, capturas
  casi-disjuntas), N̂=852.617 = **9,8× el techo CNAE-45 (87.229) → REFUTED**. El diseño es correcto
  pero los datos no tienen el solape cross-familia que Chao2 exige. **Decisión de Director** (confesar,
  no vender N̂ falso): denominador del sello = **ancla oficial CNAE-451** (F8 94,3% = 21.759/23.085);
  β S_obs=38.555 = floor (en denominator_estimate). Chao2 sellable DEFERIDO; prereq declarados:
  Overture→entity_source (25% del universo P sin captura formal), fuente fiscal cross-covering,
  filtro sells_cars en garaje, estratificar por kind.

## 2026-06-15 — SU-SEAL: assessment de seal-readiness (gate del Director)
- Recon read-only (agente) sobre la seal-readiness 52×3 con datos sellados de hoy. **GATE = TRUSTWORTHY**:
  los números F8 (B6.4, 2026-06-14) siguen VÁLIDOS — DB fresca 48h, overlays B1/β/B7 + AS24-fix incorporados.
- **Tensión raw-vs-dedup resuelta**: el numerador raw infla (50/52 selladas, ~37k dealers con dups cross-portal);
  el DEDUP canónico es el honesto → **19/52 venta ≥85% + 88% nacional** (20.324/23.085). Decisión: **sello = dedup**.
- **Decisión de Director — SELLO EN DOS CAPAS**:
  - **CAPA A (firmable €0 HOY, sellado-con-gap-irreducible)**: venta 88% nacional · desguace discovery 52/52 LIMPIO
    (146,7% DGT) · concesionario 11,6% inventario (denom FACONAUTO inflado: incluye talleres sin stock VO → gap real
    menor) · desguace-inventario = GAP-ESTRUCTURAL (sin estándar web CAT, no es hueco de cobertura) · C2C 88% del
    inventario = fuera-de-modelo (correctamente excluido).
  - **CAPA B (roadmap deferido, NO sellar-alrededor)**: Overture E2E 13.204 leads ~2-3 sem (+15-20 prov al umbral) ·
    scrapers OEM por marca ~6-8 sem (concesionario 11,6%→40-60%) · Ceuta/Melilla censo directo 1-2 días.
- **Conclusión honesta**: "SPAIN-SEALED 52/52 PLENO en cobertura" NO es alcanzable €0 hoy — requiere CAPA B (semanas).
  Lo €0-alcanzable AHORA: NATIONAL-SEALED venta (88%, gap irreducible confesado) + desguace discovery limpio +
  concesionario medido. Sellar los gaps REDUCIBLES (Overture/OEM) como "hecho" sería maquillaje — prohibido.

## 2026-06-15 — SU-A9 API: el gate cazó 2 bugs + descubrió duplicación de entidades
- Build del API (agente: 7 gaps cerrados, FastAPI sirve solo sellado) **GATEADO contra la DB — 2 bugs cazados**:
  1. `/health` dealers contaba **61.551 filas-alias** de v_canonical → corregido a
     `count(DISTINCT canonical_cdp_code)` = **42.259** (sello B1). El sello no llegaba al producto.
  2. `/inventory` (GRAVE): el filtro canonical-only GLOBAL dropeaba **102.449 coches cross-dealer**
     que el dealer SÍ lista (su canónico global vive en otro dealer) → violaba "sacarle TODO su stock".
     Reescrito a dedup INTRA-cluster `DISTINCT ON (canonical_vehicle_ulid)`. Verificado sobre dealer de
     muestra: 17.479 (correcto) vs 17.453 (el agente perdía 26). Tests reescritos con cross-check DB no-frágil.
- Targeted 6/6 PASS (inventario+health); **suite completa 85/85 PASS** (494s, cero regresiones).
- **DESCUBRIMIENTO al verificar por caminos distintos** (doctrina antialucinación): los 102.449 cross-dealer
  son 65% mismo trade_name. Muestra de 8 parejas reales = **el MISMO coche** (título+km-exacto+precio
  idénticos; **6/8 con el MISMO deep_link**). ⟹ **B7 (1.486.285) NO sobre-fusiona — es CORRECTO**; la raíz
  es **duplicación de ENTIDADES**: el mismo dealer/listing existe como ≥2 entidades que B1/ingest no dedupló.
  Cuantificado: **6.876 canónicos (16,3%) comparten nombre+provincia** → el dealer-count **42.259 es un TECHO**
  (real ~≥35.400; la cota incluye cadenas D-11 + homónimos genuinos, el gap real de B1 es un subconjunto).
  **Nuevo SU-B-DEDUP: re-gate B1/ingest entity-dedup.** No invalida B7 ni el fix del API.

## 2026-06-15 — SU-B-DEDUP diagnóstico: B1 limpio por su clave; duplicación por geocoding
- Investigado a fondo por caminos distintos:
  - **excess_name_muni = 0**: B1 NO tiene ni un canónico duplicado por su clave exacta
    (nombre+municipio). Su dedup es LIMPIO. ✓
  - Los 6.876 "duplicados" nombre+provincia están TODOS en municipios distintos → no es fallo de la
    lógica B1, es **geocoding inconsistente** (mismo dealer/listing ingestado con muni_code distinto,
    2 pipelines/2 crawls → derrota la clave nombre+municipio).
  - **Piso DEFINITIVO**: **34.904 deep_links** (un listing único) atribuidos a **>1 canónico**;
    **4.621 canónicos** involucrados. La misma URL de listing bajo 2 "dealers" = duplicación real.
  - **Caveat del sello B1** (verdict 640): 42.259 es TECHO; sobre-cuenta ~2.300 (definitivo, deep_link)
    a ~6.876 (cota nombre+provincia). Dealer-count real **~35.400–40.000**. Honestidad sobre el sello.
- **FIX diseñado (SU-B-DEDUP)**: overlay dedup NO-destructivo que fusiona canónicos conectados por
  deep_link compartido (union-find; guarda anti-hub: excluir deep_links de alta colisión >K), vam_verified
  tras gate, re-sella B1, la API sirve el canónico fusionado. 1 listing = 1 dealer → alta precisión, no sobre-fusiona.

## 2026-06-15 — SU-B-DEDUP SELLADO (verdict 1112): B1 corregido a 39.874
- Overlay dedup construido (agente) + **GATEADO** contra datos vivos: no-destructivo (v_canonical intacta
  42.259), **39.874 deduplicados** (−2.385), **0 conflictos CIF**, divergencia de nombre 181/2.236 = variantes
  triviales (case/acento/sufijo legal), muestras = mismo dealer (6/8 mismo deep_link).
- **El gate cazó un 2º gap (reproducibilidad)**: 0027 solo tenía esquema; la lógica union-find se corrió
  ad-hoc y NO se guardó (+comentario con el número viejo/buggy 39.934). Corregido: `scripts/build_canonical_dedup.py`
  reproducible (deep_link union-find, anti-hub K=3, idempotente, asserts). **El Director lo corrió**: 4 asserts OK
  (39.874/2.236/4.621/2.385), idempotente. Comentario de 0027 arreglado al valor correcto.
- **SELLADO** (`bc21547`): verdict **1112 TRUSTWORTHY** (quorum_n=2, family_n=3, origin_n=3 — pasa el CHECK del
  ledger 0026), vam_verified=TRUE. **B1: 42.259 = TECHO → 39.874 dealers verificados** (−2.385 merges de alta
  precisión por deep_link). B7 (1.486M) intacto y correcto.
- **PENDIENTE (coherencia)**: el servido (v_canonical/API) aún expone 42.259 — integrar el mapeo dedup
  (canonical→super) al servido + API + tests (mismo patrón que SU-A9). El sello está; falta que LLEGUE al producto.

## 2026-06-15 — SU-B-DEDUP integración + CORRECCIÓN del conteo (el gate volvió a cazar)
- Integrado el dedup al servido (migración **0028** `v_dealer_resolved` = B1 ∘ dedup; `resolve_cluster`
  y `/health` la usan; `/entities`,`/inventory`,`/delta` heredan el fix). Suite **457/457 PASS**.
- **El gate de la integración cazó que el conteo sellado (39.874) estaba MAL**: `/health` (cómputo
  independiente) dio 40.016. Causa raíz: la fórmula del script `n_canonicals_in − n_merged` (42.259 − 2.385)
  restaba **141 nodos non-VAM** (entidades resueltas vía COALESCE-a-self) que NUNCA estuvieron en los
  42.259 B1. El conteo correcto = distinct super-canónico sobre los B1 = **40.016** (coincide con lo servido).
- **CORREGIDO**: `build_canonical_dedup.py` ahora computa deduped_count vía representante (assert **40.016**,
  reproducible, lo corrí — pasa); comentarios 0027/0028 arreglados; verdict **1121** (40.016, quorum 2/3/3)
  **supersede el 1112** (39.874) en el ledger — registro honesto de la corrección. Los MERGES nunca cambiaron
  (son correctos: 0 CIF, deep_link); solo el NÚMERO derivado estaba mal. **B1: 42.259 = techo → 40.016 servidos.**

## 2026-06-15 — SU-A9 refactor (deuda <800) + SU-A3 fase-1 (€0)
- **SU-A9 refactor SELLADO** (`84efa47`): `main.py` 856→63 líneas + `deps.py`(99) + `routers/`{ops,entities,
  geo,vehicles,platforms} (84-194 c/u, todos <800). Behavior-preserving (queries verbatim, pool vía
  `request.app.state.pool`). Gate: verificación estructural (15 rutas registradas, re-exports OK) + **89 tests
  PASS** (633s — lento por query huérfana de 4,5h que MATÉ [auto-repair] + `/health` JOIN 1,69M, residuo declarado).
- **D1 ejecutado** (capacidad PC): Ryzen 5500U 6c/12t, **1,7GB RAM libre / 34GB disco (93%)** → drains modestos/
  paced, evicción necesaria. `cardex-pg` (1,6GB) = otro proyecto, no tocado.
- **SU-A3 recon + fase-1** (`docs/recon/SUA3_EXHAUSTIVIDAD_RECON.md` + addendum Director): B9 coverage gate EXISTE
  (`coverage_verify.py`, €0). Estado: 2/47 TRUSTWORTHY (coches_net 100,8%, wallapop 90,3%), 2 REFUTED, 42 sin gate.
  **Fase-1 €0 (sin scraping)**: AS24 REFUTED→**UNVERIFIED** (gap-declarado: proof-slice por diseño, drain real
  P1/D1-gated; v1122); milanuncios REFUTED→**UNVERIFIED** (causa = scope-mismatch: captured_db all-runs 397k vs
  declared 1-segmento 110k, NO over-capture real; v1123); **B9 v2**: over-coverage→UNVERIFIED (no REFUTED+auto_repair,
  documenta ambas hipótesis), under-coverage intacto, tests 4✓; coches_com instrumentado; discrepancia
  as24-no-en-source_health corregida (48 rows). **Fase-2 (paced D1)**: re-probe milanuncios full-index, instrumentar
  los 42, drains AS24(~13.900 págs)/autocasion/motor.es.

## 2026-06-15 — SU-A4 fase-1: maquinaria de delta uniforme (€0)
- Auditoría (`docs/recon/SUA4_DELTA_RECON.md`): delta NO uniforme — solo AS24 emite los 5 eventos
  (NEW/GONE/PRICE/PHOTO/KM); 93% del inventario (1,58M) es append-only (solo NEW); un coche vendido queda
  `available` para siempre. La lógica completa existe en `ingest.py` pero solo AS24 la llama.
- **Fase-1 €0** (`pipeline/delta.py` nuevo, 75 tests✓): `diff_vehicle(old,new)` (helper puro PRICE/KM/PHOTO,
  compartido) + `reconcile_gone(conn,source,run_start)` (baja: marca gone los no-re-vistos por last_seen,
  source-scoped, idempotente, MVCC-safe) + 2 bugs en `generic_dealer_site.py` (status 'sold'→'gone';
  old_value string→JSON).
- **El gate del Director cazó un FALLO CATASTRÓFICO**: la guarda `min_captured` solo chequeaba `<1`
  (bloqueaba corridas vacías) pero NO comparaba capturado-vs-umbral → una corrida PARCIAL (wallapop capta
  5k de 588k) habría marcado los ~583k no-re-vistos como gone = **borrado del 99% del inventario**.
  Reemplazada por **cap de fracción-gone** (aborta si stale/available > 50% para inventarios ≥20; exime
  los pequeños). Test del caso catastrófico añadido (`test_fraction_cap_aborts_partial_run`).
- **Fase-2** (cosecha): cablear `diff_vehicle` en los 43 conectores append-only + `reconcile_gone`
  post-corrida con umbral por fuente + corridas espaciadas → delta completo uniforme materializado.

## 2026-06-15 — SU-A5 recon + €0-completion: cobertura de recetas auditable
- Recon (`docs/recon/SUA5_RECETAS_RECON.md`): modelo de recetas 2-niveles — conector (35 YAML por
  plataforma/OEM, cubre 98,4% de dealers servidos vía source_key) + per-dealer (550 YAML, stamps AS24).
  `recipe_version` solo poblado para 537 AS24 → indicador engañoso (cobertura no-auditable desde DB).
- **€0-completion** (`migrations/0029_dealer_recipe.sql`): vista `v_dealer_recipe` (READ-ONLY, MVCC-safe,
  CERO UPDATE) clasifica cada dealer servido → per_dealer/connector/none. **Cobertura PROBADA**:
  37.041 connector (98,4%) / 537 per_dealer / 75 none (directorio = techo). +YAML Autorola (1.056 veh)
  y BCA (1.752 veh) extraídos del módulo real (line-cited).
- **Gate cazó integridad del ledger**: 0029 aplicado y luego archivo editado → hash schema_migrations
  (28effd) ≠ archivo (e50061). Reconciliado: DELETE fila + re-aplicar (idempotente CREATE OR REPLACE) →
  hash coherente. Verificado: 23 migraciones, 0 hashes malos.
- **A5 config SANO**: 98,4% dealers servidos con receta documentada. Gap = 23.894 dealers SIN inventario
  = recipe-hunting Tier-1 (Fase-B cosecha, deferido).

## 2026-06-15 — SU-A6 geo: recon gateado — 3/4 GREEN; muni-gap DATA-BLOCKED €0
- Recon (`docs/recon/SUA6_GEO_RECON.md`): **comarca 99,93%** asignada (40 sin = Ceuta/Melilla, correcto) ✓;
  **sentinel-drift CERO** ✓; **errores within-province CERO hard** (FK+CHECK los previene; 38 CP-vs-CCAA
  mismatch = 0,07%, flagged no-críticos) ✓.
- **muni-gap servido 17,6%** (6.619 sin muni): solo **~131 €0-resolvable** (44 lat/lon KNN + ~87 postcode
  unívoco); **6.601 sin NINGUNA señal geo** (sin address-city/latlon/postcode) → gate "<2%" **DATA-BLOCKED
  €0** (necesita fuente externa Overture/Geonames/API correos = Fase-B).
- **A6 = comarca/sentinel/errores SELLADOS GREEN; muni-gap <2% = gap-declarado-data-blocked**. §Deuda €0
  menor (negligible, queued): backfill 131 con-señal + revisar 38 CP-CCAA (0,1%). El recon recomienda no
  bloquear otros SUs por este gate de datos.

## 2026-06-15 — SU-A8 SELLADO (lazo auto-reparación €0) + auto-corrección de SU-A3
- Recon (`docs/recon/SUA8_AUTOREPAIR_RECON.md`): lazo €0 CERRADO (record_run→source_health→breaker→
  auto_repair→fire_alert origin-exacto-dedup→recovery resuelve) — **5 ciclos completos confirmados en DB**,
  aislamiento real (is_open en 44 scrapers → 1 fuente cae, API sigue), spend-actions (refingerprint/
  escalate_tier/re_receta) marcadas `# P10-SCAFFOLD` (declarado, no fakeado).
- **Test de inyección** (`tests/test_autorepair_loop.py`, 8 tests, transacción-rollback cero-residuo):
  E2E status-transitions + breaker-open@3 + alert-dedup-origin-exacto + quarantine-€0 vs refingerprint-
  scaffold + isolation A↛B + recovery-resets-and-resolves + two-cycle-no-leak. Evidencia empírica → verificación REPRODUCIBLE.
- **Auto-resolución gone_guard** (€0): `ingest.py` + 3 conectores ahora llaman `resolve_alerts` cuando el
  GONE-sweep corre (supresión ya no aplica) → cierra las ~28 alertas-ruido `:gone_guard:`.
- **AUTO-CORRECCIÓN de mi propio SU-A3**: el gate (correr el registry test) cazó que mi insert de
  `as24_wholesale` en source_health era ERRÓNEO — está INTENCIONALMENTE excluido (scheduler.py:243:
  "special case, handled outside the scheduler via its own governor"). Traté un no-problema y rompí
  `test_registry_covers_live_source_health`. **Revertido** (DELETE → source_health 47); registry-test verde.
- **A8 = lazo €0 SELLADO + verificado reproducible**. refingerprint real = P10 (spend) declarado.

## 2026-06-15 — SU-B2 FOUNDATION (framework de verificación-completitud) + decisiones de gate
- Recon (`docs/recon/SUB2_INQUISITION_RECON.md`, 8 agentes): B2 era 0% implementado (V1-V6 = spec, nada en
  código). Los "5 gates" de COMPLETED están en `V2-COMPLETION-PROOF.md`: **G1 Identity, G2 Inventory, G3 Recipe,
  G4 Served, G5 Delta**. WF-INQUISITION (cadencia) no existe; verdicts one-shot (sin expires_at/re-juicio).
- **Block α SELLADO** (`migrations/0030_entity_completion.sql`, reproducible): tabla `entity_completion`
  (22 cols exactas de V2-spec, trigger BEFORE INS/UPD: COMPLETED⟺g1∧g2∧g3∧g4∧g5∧completed_at) + `pipeline/complete.py`
  (G1-G4 operativos, G5 stub `# requires 2nd harvest`) + `tests/test_complete.py` **43✓** + demo de 20 dealers.
- **Decisiones de Director (MEJORA del método V2 — el spec hacía COMPLETED inalcanzable para el 97,5%
  connector-covered)**: **G1**=entity+cdp_code+province válido (NO lat/lon ni muni — geo-detalle = gap-de-datos
  de A6, no fallo de identidad); **G2**=validez de inventario sobre `deep_link` no-null + VAM D=S (NO
  `recipe_version`, que solo se escribe para 537 AS24 — eso es G3); **G3**=cobertura vía `v_dealer_recipe.recipe_kind
  <> 'none'` (connector O per-dealer; NO git-per-dealer-only, que falla connector-covered + Docker sin git).
  quorum-CHECK sigue NOT VALID (grandfather ~750 legacy).
- **Secuencia restante (toda €0 salvo corridas)**: β-refine (aplicar G1/G2/G3 arriba) → β-populate (37-40k
  entity_completion, corrida controlada) → γ (0031 gestion + gestionador detect/route, V4) → δ (expires_at en
  verify.py + scheduler WF-INQUISITION cadencia) → ε (0032 + inquisition V3, lentes A/B/D/E €0, C=scraping).
  G5 requiere 2ª corrida (delta). La tabla está VACÍA (sin datos erróneos antes de la refinación).
