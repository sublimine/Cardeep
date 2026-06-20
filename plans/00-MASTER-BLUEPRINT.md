# CARDEEP — BLUEPRINT MAESTRO A→Z (cerrado al átomo)

> **Fecha:** 2026-06-20 · **HEAD de referencia:** `9a9c34c` (main, repo en movimiento) ·
> **Estado:** APROBADO-CON-CAMBIOS (doble revisión adversarial pasada; fixes incorporados abajo) ·
> **Procedencia:** workflow de 16 agentes (14 investigación SOTA real con gh/web/docs + 2 revisores
> adversariales), 2,1M tokens, 519 tool-uses. Detalle por punto en `plans/P01.md … P14.md`.

## 0. Misión y encuadre (vinculante)

Indexar y servir en una API el inventario de coches del **100% de los puntos de venta de España
CON HUELLA DIGITAL** (web propia **o** ficha en un marketplace), con delta vivo
(altas/bajas/Δprecio/Δfoto/Δtexto cuanto antes), **receta versionada y re-ejecutable por entidad**,
**código único** (`cdp_code`), geo provincia→comarca→municipio, y **demostrabilidad estadística**
(cobertura por estrato con intervalo de confianza).

**Lo que NO es (corrección del owner):** si una entidad no tiene NADA online, no hay inventario que
extraer → **fuera de scope, sin fantasías** (nada de inferir vendedores invisibles por OCR de
matrículas). El trabajo es encontrar, indexar, extraer y enjaular **lo que SÍ existe en internet pero
está desordenado y desubicado — de absolutamente todos.** Cada uno de los 14 puntos se resuelve como
**proyecto institucional individual**. Doctrina: **VAM cero-confianza** (ningún número sin quórum ≥2
vías ortogonales), `main` = verdad, "antes un hueco que una mentira", **€0 hasta tener A→Z** (el gasto
es decisión final del owner).

## 1. Estado real as-is (verificado contra la DB viva, no nominal)

La auditoría corrigió el baseline: el sistema está **más construido** de lo que la memoria decía. Nota
global **~6/10**, con el valor concentrado en cerrar descubrimiento + demostrabilidad.

| Punto | As-is real | Veredicto |
|---|---|---|
| P01 Descubrimiento | **~7/10** (¡no 4/10! `discovery_capture` existe y está poblada: 377.534 filas, 7 listas ortogonales, MSE corriendo) | Elevar: faltan CT-logs/Common-Crawl y seller-census |
| P02 Exhaustividad/MSE | 2/10 → en construcción HOY (rpy2 cerrado, 2 modelos) | Construir: el "95% sellado" es **hueco** (93,5% floor) |
| P03 Antidetección | 4.5/10 (construida, no usada en cosecha; **nodriver AGPL default, sin LICENSE en repo**) | Elevar + neutralizar licencia |
| P04 Receta ejecutable | 3/10 (se serializa, no se ejecuta) | Reemplazar (RecipeRunner field-map) |
| P05 Conectores | 6/10 (**bug vivo: coches.net agendado crashea hoy**) | Hotfix + unificar |
| P06 Identidad/Splink | 8/10 (β mejor pero NO servida; cross-source FALSE) | Servir + record-linkage SOTA |
| P07 Datos/substrato | 8/10 (invariantes mecánicos; **sin particionar**, cdp_code sin CONSTRAINT) | Particionar + evidence-store |
| P08 Delta vivo | ~30% (motor OK; **GONE no cableado en 43 conectores; Δfoto muerto**) | Cablear en 1 punto |
| P09 VAM/Inquisición | 5.5/10 (**mentira EXACT_ZERO viva: 0==0 → TRUSTWORTHY**) | Cerrar la mentira + capa de precisión |
| P10 Orquestación | 8/10 €0 (auto-reparación scaffolded; **no late solo; cosecha parada 15-jun**) | Cerrar lazo auto-re-receta |
| P11 API/producto | 8/10 (falta endpoint del **certificado de cobertura**) | Servir el certificado |
| P12 Frontend/inteligencia | mapa 3D OK; **capa de valoración (Indicata/GANVAM) reservada, no construida** | Construir inteligencia |
| P13 Infra/CI | CI solo `--collect-only` (**no corre los 1066 tests**) | CI real + seed snapshot |
| P14 Gobierno legal | AGPL sin resolver; legalidad scraping sin abordar | Transversal, blindar |

**Cobertura honesta hoy:** servida ~79% (denominador registral estimado) · estadística MSE 25-58%
(solo 14 estratos realmente sellados) · **el cuello real es operativo: la cosecha lleva parada desde
2026-06-15.** El "100% demostrable" es hoy INDEMOSTRABLE hasta cerrar P01+P02+P06.

## 2. DAG canónico de ejecución (IDs P01–P14, aristas verificadas en código)

> Nomenclatura normalizada (corrige el `P0.1`/`§6`/`P-Splink` de los agentes). `X ← Y` = X depende de Y.

```
OLA-0  (irreversible/contaminante PRIMERO — daño activo hoy):
   P05-S0  hotfix crash coches_net_facet:295  (+ test de firma en el MISMO PR)
   P09-S1  cerrar la mentira EXACT_ZERO en verify.py  (flag measured_by_observation)
   [GATE]  rearranque verificado de la cosecha: harvest_run real produce >0 NEW y last_ok!=NULL en 24h

OLA-1  (fundaciones, paralelas; P14 arranca como carril de CI continuo):
   P07  substrato (particionado 0008/0011, evidence-store, cdp_code)   ← (ninguna)
   P02-S1/S2  denominador externo DIRCE/CNAE-451 + población finita     ← input INE
   P03-S1/S2/S3  lazo ban-semántico + record_ban distribuido + AGPL-neutral (patchright)

OLA-2:
   P01 descubrimiento      ← P03 (seller-census bajo DataDome), P06 (unidad de captura)
   P06 identidad/Splink    ← P01 (universo), P07 (cdp_code FK-able) · DUEÑO único de la migración cdp_code→CONSTRAINT
   P04 receta              ← P01, P03, P06, P09
   P05 resto (conectores)  ← P07, P04, P06, P03

OLA-3:
   P02 MSE          ← P01 (discovery_capture, VERIFICADO), P06 (capture unit), DIRCE
   P08 delta vivo   ← P05 (cablear en 1 punto _persistence), P06, P07, P03, P09 (quórum Δfoto), P10
   P09 resto (precisión) ← P03, P04, P02, P06, P01

OLA-4:
   P10 orquestación ← P03, P04, P05, P08, P09
   P11 API          ← P02 (v_exhaustiveness_seal), P06 (cdp_code dedup), P07, P10

OLA-5  (producto/cierre):
   P12 frontend/inteligencia ← P07, P08, P11, P01, P02, P06
   P13 infra/CI              ← P07 (seed), P02 (certificado), P10 (métricas), P11 (envelope)
   P14 (hojas legales)       ← transversal; gates de CI desde Ola-1

CICLO de co-diseño (no bloquea): P01 ⇄ P02  → tratar como LOOP ITERATIVO:
   ola de descubrimiento → recálculo MSE → criterio de parada por asíntota de la curva de acumulación.
```

**Grupos paralelos de arranque (zonas de código disjuntas, verificado):**
- **Ola-0:** `P05-S0` (coches_net_facet.py) ∥ `P09-S1` (verify.py) — ficheros distintos.
- **Ola-1:** `P07` migraciones ∥ `P03` engine (fetch/governor/ban_detector) ∥ `P14-S1` gitleaks CI ∥ `P14-S3` SBOM.
- **Ola-2:** los vectores nuevos de P01 son **mutuamente paralelos** (cada `sources/*.py` nuevo bajo el contrato `SourceAdapter`: CT-domains, Common-Crawl, FSQ, seller-census) ∥ P04 ficheros nuevos ∥ P06 codes/pgvector.
- **Frontend (P12) e infra (P13)** avanzan en paralelo a casi todo el backend si los endpoints van mockeados.

## 3. Secuencia de choque inmediata (Ola-0 — empezar por aquí)

1. **`P05-S0`** — `coches_net_facet.py:295` llama `_ingest_window` con 7 args; la firma exige 8
   (`prov_names` añadido en `9e36df9`). El harvester **canónico y AGENDADO** de coches.net **crashea
   hoy** (`scheduler.py:150-151` lo agenda). Fix: obtener `prov_names` vía `GeoResolver` (no pasar
   `None`) **+ test de regresión de firma en el mismo PR**.
2. **`P09-S1`** — `verify.py:135-151`: un claim con `db_ingested=0 ∧ fetched=0` da `TRUSTWORTHY`
   (un cero por ausencia se certifica como verdad; 10 recetas reales lo sufren). Fix: flag
   `measured_by_observation` — un cero solo cuenta como ASSERT si fue medido. **Antes** de cualquier
   paso que consuma `TRUSTWORTHY` (P04-S4, P10-S3, P11-S1).
3. **`[GATE] rearranque de cosecha`** — tras el hotfix, exigir: un `harvest_run` real de coches.net
   produce `>0 vehicle_event NEW` y `last_ok != NULL` en 24h. Sin esto, todo aguas abajo se construye
   sobre un pipeline que no late.

## 4. Fixes de revisión incorporados (puerta de finalización)

| # | Hallazgo | Resolución aplicada en el blueprint |
|---|---|---|
| C1 | P05-S0 crash en prod | Ola-0, primero y aislado, con test de firma en el mismo PR |
| C2 | P09-S1 mentira EXACT_ZERO | Ola-0, antes de cualquier consumidor de TRUSTWORTHY |
| C3 | AGPL nodriver (riesgo existencial si se expone la API) | P03-S3 + P14-S3 PRIMERO; **patchright (Apache-2.0) primario**; BotBrowser tiene núcleo propietario (no "MIT"); **añadir LICENSE al repo** |
| H1 | P02-S4 fantasía (DR-ML sin solapamiento = extrapolación) | El N̂ model-based se marca **ASUMIDO**, NO forma quórum solo; el sello separa "medido por captura" vs "estimado por modelo" |
| H2 | FSQ migró de S3 público a token/Iceberg (oct-2025) | P01-S5 reescrito: acceso vía HuggingFace dataset o Iceberg con token, NO S3 público (Overture sí sigue S3) |
| H3 | Colisión: 3 puntos reclaman migración `0050` para cdp_code→CONSTRAINT | **Dueño único = P06** (tras dedup Splink que garantiza 0 duplicados); P07/P11 la consumen |
| H4 | Nomenclatura de dependencias inconsistente | Normalizada a P01–P14 (§2) |
| E1 | Aristas faltantes | Añadidas: **P08 ← P09** (quórum en Δfoto), **P14 ← P05** (data-contracts en el `_persistence` unificado) |
| T1 | `drpop` (R, CRAN) ya empaqueta el DR-ML | Usar `drpop` directo en lugar de reimplementar (anti-atajo) |
| T2 | pHash duplicado entre P06-S7 y P08 | **Un solo módulo** `delta_photo.py` (P08) que P06 consume |
| T3 | Certificado "en cada push" sobre-vende (MSE vía R no es ~0ms) | Emitir el certificado **nightly/por-release**, no por-push |
| T4 | `ai.txt`/TDM no es estándar consolidado | Honrar `robots.txt` RFC-9309 + opt-out por ToS; `ai.txt` marcado [ASUMIDO] |

### ⚠ DECISIÓN DE ARQUITECTURA QUE TE TOCA (no la resuelvo solo)
**P07-S5 evidence-store WORM vs mandato "crudo efímero / sample-verify-DELETE".** El agente propuso
guardar cada HTML/foto crudo bajo SeaweedFS WORM **indestructible**, que **contradice** tu doctrina
(crudo efímero) y el **RGPD art.17** (datos personales de autónomos bajo Legal-Hold = imposible
borrar). **Default seguro que dejo fijado** (reversible): el evidence-store guarda **solo metadatos de
delta demostrable** (hash + thumbnail + diff), nunca el HTML crudo completo bajo WORM. Confírmame si
prefieres (a) este default, o (b) WORM completo asumiendo el riesgo legal.

## 5. Huecos del objetivo A→Z añadidos como trabajo (los detectó la revisión)

1. **Inventario de desguaces** — discovery 147% pero **inventario 0/52**. Añadir vertical a P05/P04
   (portales de despiece) **o** declarar honestamente "desguace = entidad sin inventario servible".
2. **Rearranque de cosecha** — el cuello real (parada desde 15-jun). Es el `[GATE]` de Ola-0.
3. **Fase BORRAR del E2E** — el mandato exige purga del crudo; ningún punto la tenía (y P07-WORM la
   contradecía). Resuelta con el default §4.
4. **Servir entidad SIN inventario** — 11.017 dealers (88%) sin web. P11 debe definir el contrato
   "entidad-sólo" (estado válido, no hueco de datos) para no inflar falsos NEW ni falsear cobertura.
5. **Reconciliación del denominador que "baila"** — 4 cifras (79%/88%/94,3%/25-58%) → **1 número
   certificado**. Extensión de P02-S7/S8.
6. **Spend-gate del muestreador de precisión (P09)** — ligar su presupuesto de re-fetch al cost-router
   de P03-S6/P13 (no gastar sin autorización).

## 6. Beyond-SOTA (la ambición verificada como creíble, no tibia)

- **P02:** quórum de **4 familias de estimadores estructuralmente ortogonales** + criterio de PARADA
  **iNEXT** trasplantado de ecología → un censo **auto-certificante** por asíntota.
- **P09:** muestreo de aceptación **ciego, re-colectado por camino ortogonal**, con IC Wilson+SPRT →
  un **fiscal estadístico fila-a-fila**, no un validador de schema.
- **P01:** el descubrimiento tratado como problema **CERRABLE** por asíntota de la curva de
  acumulación + IC de captura-recaptura por estrato.

## 7. Índice de sub-proyectos (100 pasos, detalle en `plans/PXX.md`)

| ID | Sub-proyecto | Pasos | Ola | SOTA ancla |
|---|---|---|---|---|
| **P01** | Descubrimiento multivector | 7 | 2 | Amass · Common Crawl columnar · FSQ OS Places · MERAI |
| **P02** | Exhaustividad / MSE | 8 | 1→3 | dga · LCMCR · Rcapture · drpop · iNEXT |
| **P03** | Adquisición / antidetección | 6 | 1 | curl_cffi · patchright · Hyper-SDK · browserforge |
| **P04** | Receta ejecutable | 8 | 2 | extruct · Crawl4AI · Outlines/BAML · LLM-local |
| **P05** | Conectores unificados | 8 | 0+2 | Scrapy · asyncpg COPY · Protocol/base · contract-test |
| **P06** | Identidad / record-linkage | 8 | 2 | Splink v4 · MERAI · pgvector · stdnum |
| **P07** | Datos / substrato | 7 | 1 | PG17 partman · pgvector · evidence-store · atlas |
| **P08** | Delta vivo | 6 | 3 | PDQ/pHash · CLIP · CDC · changedetection |
| **P09** | VAM / precisión | 7 | 0+3 | scipy SPRT/Wilson · DataComPy · NannyML/Frouros · ODCS |
| **P10** | Orquestación / auto-repair | 5 | 4 | APScheduler · pyrate-limiter PG · Prometheus/SigNoz |
| **P11** | API / producto | 10 | 4 | FastAPI/Litestar · Granian · Redis · certificado IC |
| **P12** | Frontend / inteligencia | 6 | 5 | deck.gl · DuckDB-WASM · IMV/hedonic valuation |
| **P13** | Infra / CI / coste | 7 | 5 | seeded snapshot CI · cost-router · IaC · observabilidad |
| **P14** | Gobierno legal/calidad | 7 | 1→5 | gitleaks · SBOM/syft · robots RFC-9309 · data-contracts |

## 8. Protocolo de ejecución hands-off (lo que lee el `/loop`)

**Cada ciclo:** `git pull` → leer este `00-MASTER` (DAG) + `PROGRESO.md` (cola) + estado real
(git log, tests) → elegir el **siguiente paso LISTO** según las olas (§2) → ejecutarlo a DONE como
proyecto institucional (investiga SOTA si aplica, **TDD**, workflows, sin atajos) → **VERIFICAR** por
vía independiente (tests+build verdes, números por ≥2 vías VAM, revisión adversarial de lo crítico) →
persistir en `PROGRESO.md` + commit (Conventional Commits) en `feat/<descriptor>` → continuar.

**Parada obligatoria (escribe el bloqueo + opciones y NO auto-procedas):** (a) **gasto** (proxies/
compute/API de pago), (b) **irreversible** (force-push, borrado remoto, prod, efecto externo),
(c) **legal** (la decisión P07-WORM §4; exponer API con dep AGPL sin neutralizar), (d) **bloqueo real**
tras agotar todas las vías. Parar ahí es correcto, no es fallo.

**Invariante de scope (gate de P01):** sin huella digital previa, no se mintea entidad.

---
_Blueprint cerrado al átomo. El descubrimiento + la demostrabilidad son la columna; todo lo demás la
sirve. Cardeep no estará terminado cuando scrapee bien, sino cuando enseñe el mapa de España con su
cobertura y su intervalo de confianza al lado._
