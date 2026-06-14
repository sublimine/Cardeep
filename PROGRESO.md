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
