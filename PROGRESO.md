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

