# Etapa 10 · Cerebro/Automatización — Biblia
> Estado adversarial: **NEEDS_REWORK** (`holds=false`). Fuente: Wave 1 (path:línea verificado; las afirmaciones marcadas `[VERIFIED]` se releyeron en código esta sesión, las marcadas `[VERIFIED Wave1]` heredan la recon de Ola 1). Stack vivo **CAÍDO** (Docker/PG:5433/API:8090/schedulers off): toda cifra de DB = punto-en-el-tiempo, no estado corriente.

> Navegación: [Misión](#misión) · [Existe HOY](#lo-que-existe-hoy-verificado) · [Motor](#motor-invariante-reusado-byte-idéntico-por-país) · [Pack país](#pack-por-país) · [Costuras→fix](#costuras-es-hardcoded--fix) · [Diseño A→Z](#diseño-genérico-az) · [Onboarding](#onboarding-de-país-nuevo) · [Sellado](#sellado--verificación-multi-vía--rollback) · [Veredicto adversarial](#veredicto-adversarial-roturas--resolución) · [Sub-proyectos 360](#sub-proyectos-institucionales-360-por-faceta) · [Nivel inalcanzable](#mejoras-a-nivel-inalcanzable-eur0-priorizadas) · [Riesgos](#riesgos--open-items)

---

## Misión
Ser el **cerebro** del motor: la capa que decide, escala y orquesta por encima del músculo determinista. Tres responsabilidades inseparables:

1. **Bus de decisiones** — generalizar el único punto de fuga del sistema (las escalaciones que hoy mueren en el humano) en una cadena gobernada determinista → IA local → Claude → humano, donde el humano solo recibe lo **irreversible**.
2. **Resolución 3-capas** — encarnar el modelo del `00-MASTER` (§Modelo de ejecución): el músculo decide lo barato, la IA local lo ambiguo acotado, Claude lo estratégico en ráfagas, y nadie adivina (§Anti-desvío: la duda **escala**, no improvisa).
3. **Máquina de estados `cover(country_code)`** — el orquestador que conduce un país de `REGISTERED` a `SEALED` ejecutando el subconjunto correcto de las 9 etapas por estado, drenando el bus, y dejando los gates `GASTO/PROD/LEGAL` en `PENDING-OWNER` **sin parar el loop**.

El norte de esta etapa: onboardar un país = `INSERT country_campaign(country_code=CC, state=REGISTERED)` y dejar que la máquina conduzca. La genericidad vive en la **maquinaria** y en el **método de investigar-y-personalizar**, nunca en literales.

---

## Lo que existe HOY (verificado)
El cerebro **determinista** (capas 1) ya existe y está probado por tests. Las capas 2 (IA local) y 3 (Claude orquestador) son **0 código** hoy: solo existen los contratos/slots dormantes. Honestidad cruda: lo que sigue es maquinaria real; el "cerebro" pensante aún no respira.

- **Gestionador V4 — registry de 9 detectores (7 live + 2 STUB)**, cada uno lee SOLO hechos de DB, €0, nunca re-cosecha. `[VERIFIED pipeline/gestionador/detect.py:926-936]` (lista `DETECTORS`), `[VERIFIED detect.py:940]` (`STUB_DETECTORS = {geo_resolution_drift, classifier_drift}`). El dato `AnomalyResult` (detector/subject/severity/score/measured/lane/quarantines/dedupe_key) `[VERIFIED Wave1 detect.py:114-126]`.
- **State-machine de gestión: 9 estados, 5 lanes con SLA, transiciones validadas**, upsert idempotente por `dedupe_key`, guard duro `RESOLVED ⇒ verdict TRUSTWORTHY con quorum_n>=2`. `[VERIFIED route.py:48-58]` (`VALID_TRANSITIONS`), `[VERIFIED route.py:28-34]` (`LANE_SLA`: AUTO_FIX 6h / RESEARCH 7d / QUARANTINE 48h / ESCALATE_GASTO None / ESCALATE_OWNER None), `[VERIFIED route.py:229-248]` (cierre = prueba real, no promesa).
- **Ledger append-only + dientes de cuarentena.** `gestion_item` + `gestion_transition` (auditoría inmutable) y las **vistas-gate** `servable_entity`/`servable_vehicle` que EXCLUYEN mecánicamente cualquier subject con item cuarentenante abierto (la API lee por la vista, no la tabla). `[VERIFIED migrations/0031_gestion.sql:146-168]` (vistas), `[VERIFIED 0031:104-106]` (`idx_gestion_quar`), `[VERIFIED migrations/0036_gestion_resolved_proof.sql:16-41]` (trigger `trg_gestion_resolved_proof` = invariante DB).
- **Router determinista veredicto→lane: tabla pura por lookup** (la misma mentira enruta igual, sin discreción de agente). PUNTO DE ESCALACIÓN CLAVE: hoy termina en humano. `[VERIFIED pipeline/inquisition/router.py:65-99]` (`_ROUTING_TABLE` sellada), `[VERIFIED router.py:84]` (`REFUTED/NO_INDEPENDENT_PATH → ESCALATE_OWNER`), `[VERIFIED router.py:93]` (`INCONCLUSIVE/* → ESCALATE_OWNER`).
- **Orquestación programada crash-safe.** APScheduler `BlockingScheduler` + `SQLAlchemyJobStore` (el job sobrevive a la muerte del proceso), single-producer por advisory lock, **8 jobs** registrados. `[VERIFIED pipeline/ops/scheduler.py:4]` (arquitectura), `[VERIFIED scheduler.py:913]` (`_SCHEDULER_SINGLETON_LOCK = 0x43415244`, ASCII 'CARD', host-singleton), `[VERIFIED scheduler.py:938/953/968/983/1002/1017/1032/1048]` (8× `add_job`).
- **Emisión acotada/opt-in** ya documentada: `[VERIFIED scheduler.py:102-103]` ("at €0 mass emission floods un-self-resolvable escalations"), `[VERIFIED scheduler.py:106]` (`INQUISITION_EMIT_BATCH = 200`). El bus DEBE heredar esto.
- **Gate de completitud por-entidad (prueba de SELLADO atómico):** G1 identity / G2 inventory / G3 recipe / G4 served / G5 delta(deferred); `derive_verdict → COMPLETED/INCOMPLETE/STALE`. `[VERIFIED pipeline/complete.py:473-497]` (`derive_verdict`: cualquier gate `None` o `False` ⇒ INCOMPLETE), `[VERIFIED Wave1 complete.py:107-148/155-228/235-290/382-445/452-466]` (G1..G5).
- **Capa-2 IA local: CERO en código.** Solo los DOS slots de enganche dormantes: el escalón `llm_local` del recipe ladder y el STUB `detect_classifier_drift` ("local LLM classifier nightly"). `[VERIFIED pipeline/recipe_schema.py:67]` (`engine: next_data | jsonld | css | llm_local`), `[VERIFIED detect.py:905-916]` (STUB: requiere `golden_set table` + harness, devuelve `[]`), `[VERIFIED detect.py:886-898]` (`detect_geo_resolution_drift` STUB).
- **Capa-3 Claude orquestador: CERO en código.** No existe `decision_request`, ni bus, ni loop de drenado, ni `cover(country_code)`. La escalación hoy termina en humano (`ESCALATE_OWNER`), no en Claude. `[VERIFIED Wave1]` grep `decision_request|decision_bus|def cover\(|REGISTERED|BOOTSTRAPPED|IN_COVERAGE` en `pipeline/` + `migrations/` = vacío.
- **Primitivas de país YA paramétricas reutilizables.** `[VERIFIED pipeline/paths.py:22]` (`DEFAULT_COUNTRY='ES'`), `[VERIFIED paths.py:30]` (`_CDP_COUNTRY_RE = r"^CDP-([A-Z]{2})-"`), `[VERIFIED paths.py:33-63]` (`recipe_root`/`recipes_flat_dir`/`census_dir`/`country_of_cdp`), `[VERIFIED services/api/codes.py:44-53]` (`mint_code(country_code=)`), `[VERIFIED codes.py:62-65]` (`canonical_key` country-blind por diseño).
- **Arnés de coexistencia de país YA existente** (la 2ª-vía ortogonal del sellado). `[VERIFIED tests/test_country_coexistence.py:199-204]` (hoy hace `pytest.skip` con el mensaje literal "complete.py:_CDP_CODE_RE still hard-codes '^CDP-ES-'"). Es decir: **el propio repo documenta la rotura como no resuelta.**

---

## Motor (invariante, reusado byte-idéntico por país)
Lo que es **idéntico byte-a-byte** en cada país. El motor de orquestación no sabe de países:

| Pieza | Invariante | Evidencia |
|---|---|---|
| State-machine gestión | 9 estados + transiciones + 5 lanes/SLA + upsert por `dedupe_key` + guard `RESOLVED⇒TRUSTWORTHY+quorum>=2` | `[VERIFIED route.py:48-58, 28-34, 229-248]` |
| Esquema ledger | `gestion_item`/`gestion_transition` + vistas-gate + trigger 0036; `subject_key` lleva `cdp_code`/`vehicle_ulid` de cualquier CC | `[VERIFIED 0031:146-168, 0036:16-41]` |
| Lógica de los 7 detectores live | El **algoritmo** (count_inflation, silent_cap, field_loss, staleness, fabrication, coverage_gap, price_trap) es puro; opera sobre `verification_verdict`/`vehicle`/`entity` | `[VERIFIED detect.py:926-936]` (⚠ sus **constantes** NO son invariantes — ver Costuras) |
| Inquisition / VAM | `quorum.decide()` (6 pasos), `_ROUTING_TABLE` sellada, lenses A–D, prosecutor/sampler/independence | `[VERIFIED router.py:65-99]`, `[VERIFIED Wave1 quorum.py:159-337]` |
| Orquestación | APScheduler + JobStore crash-safe, single-producer por advisory lock, lease/heartbeat (0054), familia de 8 jobs | `[VERIFIED scheduler.py:4, 913, 8×add_job]` |
| Evaluador G1–G5 | La **estructura** (máquina de gates + `derive_verdict`); cambian los parámetros que consume, no la lógica | `[VERIFIED complete.py:473-497]` |
| Vocabulario canónico de `kind` | Un dealer alemán se clasifica en los MISMOS kinds; el pack solo aporta el léxico local→canónico — **con la salvedad de que `entity_kind` es un ENUM de Postgres** (ver B6/MP6) | `[VERIFIED 0005:13-17]` |
| Invariantes transversales | `cdp_code = CDP-{CC}-{NN}-{8×base32}` · VAM cero-confianza · append-only · sample-verify-delete · dry-run→golden→Ferrari→CI · 100% = INTERVALO, nunca un entero | `[VERIFIED codes.py:44-53]` |
| **NUEVO motor (a construir, country-agnóstico desde el día 0)** | `decision_request` + `decision_event`, el contrato del bus, el loop de drenado de Claude, la máquina `cover(country_code)` + su tick-job | (diseño — abajo) |

---

## Pack por país
Lo que **cada país aporta** para esta etapa (derivado del Dossier de País, ver `COVER-NEW-COUNTRY.md`). Ninguna de las tablas nuevas lleva `'ES'`; el CC es columna/parámetro.

- **`countries/{CC}/country.toml`** (manifest declarativo **NUEVO, hoy inexistente** `[VERIFIED]`: no existe el fichero ni su cargador): `country_code`; **gramática de subdivisión** (ancho + alfabeto del slot `{NN}`, no solo un regex — ver B3/B4/MP5); validador de subdivisión que reemplaza `_PROVINCE_RE`; override de `national_kinds`; léxico `kind` local→canónico **+ manifiesto de migración** si exige un kind canónico genuinamente nuevo (B6/MP6); **umbrales de detector en la moneda del país** (`FAB_PRICE_CEIL/FLOOR/KM`, `PRICE_TRAP_FLOOR`/`HIGH_ABS_FLOOR` — MP2); **moneda ISO-4217** + política de normalización (MP1); override de cadencia/SLA por tier (MP7); física de paginación por portal (MP8); referencia al backbone geo; hints de tier de receta.
- **Anclas de denominador + censo externo del país** (reemplazo de `COVERAGE_ANCHORS` y de `triangulation.load_external_census()`): conteos ground-truth nacionales que alimentan TANTO `coverage_gap` COMO el sellador de intervalo (MP3/MP4). Ej. DE: KBA + ZDK + Gelbe Seiten.
- **El golden-set del clasificador de `kind`** (semilla para capa-2 / `detect_classifier_drift`): entidades hand-labeled para que la IA local mida precisión y el bus tenga un eval.
- **Golden + Ferrari de detector POR PAÍS** (MP9): fixture sintético en la moneda/escala nacional que prueba que los detectores NO disparan mass-quarantine; sin esto, CI (golden ES) queda verde mientras el país nuevo detona en producción.
- **Lista-semilla de fuentes** del país (`source_health`/discovery registry con `harvest_interval_hours`).
- **El árbol `countries/{CC}/`** (recipes, `census/`, subdivisions seed) y el **seed del backbone geo** vía adapter sobre `(country_code, code)`.
- **Prompts/hints de decisión específicos del país** para Claude (denominador nacional, ambigüedades geo conocidas): el contexto que el bus inyecta en cada `decision_request` de ese CC.

---

## Costuras ES-hardcoded → fix
La espina dorsal del veredicto: `country_code` se enhebró en el **esquema** (0052/0053) y en el prefijo `cdp_code`, pero **NO en la lógica**. Lo que el motor de esta etapa toca, costura a costura:

| location | issue | fix |
|---|---|---|
| `complete.py:89` | `_CDP_CODE_RE = r"^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$"` — G1 clava el segmento de país `ES`. 6º-blocker: rechaza cualquier `CDP-DE-*` aunque el esquema ya coexista. `[VERIFIED complete.py:89]` | Widenear a `r"^CDP-([A-Z]{2})-([0-9]{2})-..."` (el patrón ya existe verbatim en `paths.py:30`) y quitar el `xfail`. **Fix de motor UNA vez.** ⚠ NO basta para FR/IT: el ancho `[0-9]{2}` también es costura (B3/B4). |
| `complete.py:73` | `_PROVINCE_RE = r"^(0[1-9]|[1-4][0-9]|5[0-2])$"` — rango INE español 01-52. `[VERIFIED complete.py:73]` | Mover el validador al country-pack; `complete.py` recibe el regex/rango desde `country.toml` resuelto por `country_of_cdp(cdp_code)`. ES mantiene 01-52 declarado en su `.toml`. |
| `complete.py:305` y `:309` | `glob("countries/ES/**/{cdp}/recipe.yaml")` y `"countries/ES/recipes/{cdp}.yaml"` con `ES` literal, bypasseando `paths.py`. `[VERIFIED complete.py:305,309]` | Reemplazar por `paths.recipe_root(paths.country_of_cdp(cdp_code))` + `paths.recipes_flat_dir(...)`. El CC se deriva del `cdp_code`. `paths.py:33-52` ya expone estos helpers. `[VERIFIED]` |
| `complete.py:83-85` | `_NATIONAL_KINDS = {subasta, plataforma, oem_vo_portal, importador}` — set fijo de kinds con provincia NULL. `[VERIFIED complete.py:83-85]` | Default del motor + override opcional desde `country.toml` (`national_kinds`). No es seam roto hoy (vocabulario compartido), pero el hook evita re-litigar. |
| `pipeline/platform/*.py` — **CROSS-CUTTING** (owner: etapa identity, **BLOQUEA** cover(CC)) | Connectors acuñan `f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"` y **0 llaman `mint_code()`**. `[VERIFIED]` grep `mint_code\(` en `pipeline/platform/` = **sin matches**; `[VERIFIED pipeline/platform/wallapop_wholesale.py:225]` (patrón hardcoded). **Conteo real corregido** (ver nota): 47 ficheros `.py` en `platform/`, **31** hardcodean `f"CDP-ES-"` en todo `pipeline/`, **NO 63**. Una campaña `cover(DE)` que cosecha vía un platform connector seguiría acuñando `CDP-ES-`, rompiendo G1. | Enrutar los mints a `mint_code(province_code=..., digest=..., country_code=campaign.country_code)`. El `country_code` viaja desde la state-machine `cover(CC)` hasta el connector. Fix de motor UNA vez; salida ES byte-idéntica (`mint_code` default `'ES'`, fijado por golden). `[VERIFIED codes.py:44-53]` |

> **Nota de honestidad sobre el conteo (BLINDAJE anti-alucinación).** El insumo Wave-1 afirmaba "63 ficheros". Verificación propia esta sesión: `ls pipeline/platform/*.py` = **47**; `grep -rl 'f"CDP-ES-'` en `pipeline/` = **31**; `grep 'mint_code\('` en `pipeline/platform/` = **0 call-sites**. La **sustancia** de la rotura HOLDS (los connectors bypassean el minter paramétrico), pero la cifra exacta era un overcount: se corrige a los números verificados. El docstring `codes.py:46-49` que afirma "`CDP-{country}-` exists in exactly one place" es, a día de hoy, **ASPIRACIONAL/FALSO** `[VERIFIED]`.

---

## Diseño genérico A→Z
Tres piezas nuevas sobre el motor determinista ya probado, **sin reescribir ES** (salida byte-idéntica garantizada por `DEFAULT_COUNTRY='ES'` cableado en `paths.py:22` + `codes.py:24` + golden `[VERIFIED]`).

### 1) El bus de decisiones (`decision_request` + `decision_event`)
Generaliza el único punto de fuga: las lanes `ESCALATE_OWNER` (`router.py:84,93`) y `ESCALATE_GASTO` terminan hoy en humano `[VERIFIED]`. El bus inserta DOS escalones intermedios (IA local, Claude) **antes** del humano, y solo deja al humano lo irreversible.

**Esquema `decision_request`** (country-agnóstico, el CC es columna):

```
id · country_code · kind ENUM(RECIPE_TIER1_NEW | GEO_AMBIGUITY | DENOMINATOR_AMBIGUITY |
   VAM_DISCREPANCY | CLASSIFICATION_DOUBT | RECIPE_FIELD_EXTRACT | COVERAGE_SEAL_REVIEW)
subject_type · subject_key        -- mismas coordenadas que gestion_item
question TEXT · context JSONB      -- la evidencia que el motor YA ensambló
options JSONB                      -- candidatas con su score determinista cuando exista
reversibility ENUM(reversible|spend|prod|legal)  -- espeja la taxonomía de gates de la doctrina
decider ENUM(deterministic_fallback|local_ai|claude|human)
decision JSONB · rationale TEXT · confidence FLOAT
state ENUM(PENDING->CLAIMED->DECIDED->APPLIED->VERIFIED | REJECTED | ESCALATED_HUMAN)
gestion_item_id FK · verdict_id FK
dedupe_key UNIQUE(kind|subject_key|bucket)   -- idempotente igual que gestion_item
timestamps por estado
```

`decision_event` es el audit append-only espejo de `gestion_transition` (cero updates/deletes; la historia ES la prueba).

**Interfaz de producción (no se toca la tabla sellada del router):** se inserta un `triage()` puro **aguas abajo** de `_lookup_route` que, para `action='escalate'`, clasifica `reversibility` y bifurca:
- `reversible` + decidible → `emit_decision_request()`.
- `spend`/`prod`/`legal` → mantiene `ESCALATE_OWNER`/`ESCALATE_GASTO` (humano), preservando el freno de irreversibilidad de §Autonomía.

**Fuentes del bus:** `INCONCLUSIVE` y `NO_INDEPENDENT_PATH` (router), los dos STUB de `detect.py` al activarse (`classifier_drift → CLASSIFICATION_DOUBT`, `geo_resolution_drift → GEO_AMBIGUITY`), fallo de `RecipeHarness` en fuente Tier-1, y los checkpoints de `cover(CC)`.

### 2) La resolución 3-capas como cadena de deciders
`decision_request` se drena por **coste cognitivo creciente**:

1. **`deterministic_fallback`** (coste 0): si una regla pura decide, decide. Ya es el gestionador.
2. **`local_ai`**: un job nuevo `local_ai_drain` reclama `PENDING` de kind `CLASSIFICATION_DOUBT`/`RECIPE_FIELD_EXTRACT`, devuelve `decision+confidence`; si `confidence < umbral` **escala hacia arriba** (decider sube a `claude`, state sigue `PENDING`). Engancha EXACTAMENTE en los dos slots ya existentes: `recipe_schema.py:67` (`llm_local`) y el STUB `detect.py:905`. **Si NO hay modelo cargado, el job no existe y el request pasa directo a Claude** — €0 hoy; GPU/IA = palanca futura; el contrato del bus es el único desbloqueo.
3. **`claude`** (capa-3, único decididor estratégico): un drenado **PROGRAMADO** (cron del harness/loop) invoca a Claude con el **LOTE** de `PENDING` tier=claude como una sola ráfaga; Claude escribe `decision+rationale`, el motor aplica (`APPLIED`) y **RE-VERIFICA por VAM** (`VERIFIED` solo si el quórum confirma). **Claude NUNCA toca `spend`/`prod`/`legal` sin humano.**

### 3) La máquina de estados `cover(country_code)` (`country_campaign` + `country_campaign_event`)
Una fila por CC; estados `REGISTERED → BOOTSTRAPPED → IN_COVERAGE → SEALED`, con `REOPENED` por regresión (mismo patrón que `gestion_item RESOLVED→REOPENED`, `[VERIFIED route.py:55-56]`). **Cada transición la guarda un PREDICADO COMPUTABLE, no Claude:**

- `REGISTERED → BOOTSTRAPPED`: `country.toml` validado + **gramática de código congelada** (nuevo gate, ver SH5) + seed geo `count>0` + lista-semilla de fuentes cargada + dry-run verde.
- `BOOTSTRAPPED → IN_COVERAGE`: schedulers activos para el CC + primera cosecha aterrizada.
- `IN_COVERAGE → SEALED`: el predicado de sellado (abajo).

`cover(CC)` es el ORQUESTADOR que, por estado, sabe qué subconjunto de las 9 etapas correr y en qué orden, y qué `decision_request` esperar; avanza solo cuando el gate se cumple, y cualquier avance ambiguo se emite al bus (`kind=COVERAGE_SEAL_REVIEW`). Se conduce por un job nuevo `country_campaign_tick` añadido a la familia de los 8 ya existentes `[VERIFIED scheduler.py:8×add_job]`.

**Abstracción clave:** onboardar = `INSERT country_campaign(country_code=CC, state=REGISTERED)`; los `spend`/`prod`/`legal` se quedan `PENDING-OWNER` sin parar el loop (doctrina cardeep). El `country_code` viaja como parámetro desde la fila campaign hasta `paths.*`, `mint_code(country_code=)`, el validador de subdivisión y el contexto del bus — **un solo hilo, cero literales nuevos.**

---

## Onboarding de país nuevo
Pasos de biblia para esta etapa (el detalle de inteligencia de mercado vive en `COVER-NEW-COUNTRY.md` FASE 1):

1. **Autorar `countries/{CC}/country.toml`** (manifest NUEVO): `country_code`, gramática+validador de subdivisión, override `national_kinds`, léxico `kind` local→canónico (+ manifiesto de migración si hay kind nuevo), umbrales de detector en moneda local, moneda ISO-4217 + política de normalización, overrides de SLA/cadencia, física de paginación, refs a backbone geo / golden-set / censo externo / lista-semilla de fuentes.
2. **Aplicar migraciones country-checked** con `scripts/migrate.py` — el esquema YA es paramétrico (0052/0053 PK geo compuesta `(country_code,code)`; piloto DE coexistió byte-idéntico `[VERIFIED test_country_coexistence.py]`). Las tablas nuevas `decision_request`/`country_campaign` son additive+reversibles con bloque de rollback.
3. **[FIX DE MOTOR, UNA SOLA VEZ — no por-país]** Widenear las 3 costuras de `complete.py` (`_CDP_CODE_RE`, `_PROVINCE_RE`→inyectado, glob→`paths`), quitar el `xfail` de G1. **+ congelar la gramática del slot `{NN}` (B3/B4/MP5) ANTES de mintear.**
4. **[FIX DE MOTOR, UNA SOLA VEZ]** Enrutar los mints de `pipeline/platform/` a `mint_code(country_code=campaign.country_code)`; salida ES byte-idéntica (golden la fija).
5. **Sembrar** el backbone geo del CC vía adapter sobre `(country_code,code)` + la lista-semilla de fuentes en el registry con sus `harvest_interval_hours`. **+ cargar censo externo y anclas del país** (MP3/MP4).
6. **`INSERT country_campaign(country_code=CC, state=REGISTERED)`.** El job `country_campaign_tick` (genérico) recoge la fila nueva en el siguiente tick. No se toca el motor.
7. **Sembrar el golden-set del clasificador + el Ferrari de detector del país** (MP9). Si hay modelo local presente, capa-2 mide; si no, toda duda escala a Claude (capa-3) — €0, sin bloqueo.
8. **Dejar que la máquina conduzca:** el predicado lleva `REGISTERED→BOOTSTRAPPED→IN_COVERAGE→SEALED`. Claude drena el bus en ráfagas programadas; `spend`/`prod`/`legal` quedan `PENDING-OWNER` sin parar el loop.

---

## Sellado + verificación multi-vía + rollback
**SELLADO(CC)** en esta etapa = `country_campaign.state = SEALED`, latcheado por un predicado determinista que el `cover(CC)` tick computa SOLO cuando TODO se cumple a la vez:

- **(a)** `coverage_lower(CC) >= umbral certificado` CON el margen del intervalo (Ñ_hat con IC95; **NUNCA un entero** — espeja la cota MSE de ES). ⚠ Producida por la **máquina de intervalo** `exhaustiveness/seal.py`+`capture.py`, que el diseño OMITIÓ del pack — ver SH2/MP4.
- **(b)** todas las entidades servidas del CC con G1–G4 verdes (G5 donde exista 2ª cosecha) vía `complete.py` `[VERIFIED complete.py:473-497]`.
- **(c)** 0 `gestion_item` críticos/cuarentenantes abiertos para el CC `[VERIFIED 0031:104-106]`.
- **(d)** los veredictos VAM de los estratos sellados en `TRUSTWORTHY` con `quorum_n>=2` `[VERIFIED 0036:16-41]`.
- **(e)** 0 `decision_request` PENDING de kind bloqueante (`COVERAGE_SEAL_REVIEW` sin decidir) para el CC.

**Verificación por 2ª vía ortogonal:** el predicado lo **COMPUTA** `cover(CC)` (capa-1, desde la fila campaign), pero lo **VERIFICA** un camino independiente que NO lee la fila campaign: el inquisition **prosecutor** re-deriva la misma cobertura/quórum desde `verification_verdict` (`independent_values`), y `test_country_coexistence.py` prueba que ES sigue byte-idéntico — **un sellado que mueva ES es un sellado rechazado** `[VERIFIED test_country_coexistence.py:205-208]`. Las DOS recomputaciones deben coincidir dentro de tolerancia; además se emite `COVERAGE_SEAL_REVIEW` para que Claude adjudique ANTES de latchear (co-igual, no sello automático). Mismo principio que el guard `RESOLVED⇒TRUSTWORTHY+quorum>=2` (0036).

**Rollback:** todo additive+reversible. `country_campaign.state REOPENED` por regresión, exacto como `gestion_item RESOLVED→REOPENED` `[VERIFIED route.py:55-56]`. Cada migración lleva bloque de rollback (`[VERIFIED 0031:170-174, 0036:43-45]`). Las decisiones del bus son append-only: una decisión errónea se revierte con un nuevo evento `APPLIED→REJECTED`, jamás un delete. El **kill-switch reversible duro** es la cuarentena (`gestion_item.quarantines=TRUE`): saca al subject de toda vista servida sin tocar la tabla, y cerrar el item lo re-muestra — cero NULLs, cero DELETEs `[VERIFIED 0031:146-168]`.

> ⚠ **El rollback NO es universal** (ver SH5): en el eje de la **gramática del código** `cdp_code` es INMUTABLE; un país minteado con gramática equivocada NO se revierte sin huérfanar la historia append-only. Por eso el gate de **congelación de gramática** es pre-minteo, no post.

---

## Veredicto adversarial: roturas → resolución
El inquisidor (`holds=false`, `NEEDS_REWORK`) declaró **10 breaks + 10 missing_pack + 7 sealing_holes = 27 ítems**. Aquí cada uno, agrupado por causa raíz, con su resolución de diseño o su OPEN ITEM con causa y gating. **Cero ocultación.**

> **Despliegue profundo:** cada clúster de aquí se abre átomo-a-átomo en [§ Sub-proyectos institucionales (360 por faceta)](#sub-proyectos-institucionales-360-por-faceta) — **33 sub-proyectos** con deep-spec `(a→f)`, ficha `costura→fix→adversarial→sellado` y herramienta NEXT-LEVEL `€0` por faceta.

### Matriz de cobertura (los 27 ítems → clúster)
| Clúster | Ítems del inquisidor | Estado |
|---|---|---|
| A · G1 identity ES-lock | B1, SH1 | ✅ RESUELTO (fix motor) |
| B · Gramática del slot `{NN}` | B3 (FR), B4 (IT), MP5, SH5 | ⚠ RESUELTO con **OPEN ITEM gateado** (ancho de código = decisión irreversible owner) |
| C · Ceguera de moneda | B5 (MX), B7 (JP), MP1, MP2 | ✅ RESUELTO (fix motor + pack) |
| D · Pooling cross-country de cohortes | B8 (JP), B10 (EUR) | ✅ RESUELTO (JOIN + partición) |
| E · Anclas + censo externo + máquina de intervalo | B2 (DE), B6-anclas (MX), MP3, MP4, SH2 | ✅ RESUELTO (artefactos al pack; corrige omisión del diseño) |
| F · Extensión del ENUM `entity_kind` | B6-enum (MX), MP6 | ✅ RESUELTO (migración en bootstrap; corrige over-claim) |
| G · Seam de cadencia/SLA por país | MP7 | ✅ RESUELTO (seam nuevo, €0) |
| H · Piso de independencia del quórum | B9 (PT), MP10, SH6 | ⚠ RESUELTO sin debilitar VAM + **OPEN ITEM gateado** |
| I · G3 recipe depende de `llm_local` dormante | SH7 | ⚠ RESUELTO a €0 vía Claude + **OPEN ITEM** (render infra, owner stage 02) |
| J · Mint bypass cross-cutting | risk#1 | ✅ RESUELTO (fix motor; conteo corregido) |
| K · Método de verificación hueco | SH3, SH4, MP9 | ✅ RESUELTO (Ferrari de detector por país = la 2ª vía real) |
| L · Física de paginación silent_cap | MP8 | ✅ RESUELTO (pack-level) |

---

### Clúster A — G1 identity clavada en ES `[B1, SH1]`
**Rotura:** `complete.py:89 _CDP_CODE_RE = r"^CDP-ES-..."` `[VERIFIED]`. Hoy NINGÚN `CDP-DE-*` pasa G1 → `derive_verdict = INCOMPLETE` para siempre → ningún dealer extranjero se sella. El repo lo admite: `pytest.skip` "still hard-codes '^CDP-ES-'" `[VERIFIED test_country_coexistence.py:199-204]`.
**RESOLUCIÓN (✅ cierra para DE y todo CC alfabético-2):** widenear a `r"^CDP-([A-Z]{2})-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$"` — el patrón `^CDP-([A-Z]{2})-` ya existe verbatim en `paths.py:30` `[VERIFIED]` — y quitar el `xfail`. El check de coexistencia pasa a verde inmediato. **Fix de motor UNA vez.** Para DE esto es suficiente; para FR/IT NO basta (el ancho `[0-9]{2}` es el problema → Clúster B).

### Clúster B — La gramática del slot de subdivisión `{NN}` `[B3 FR, B4 IT, MP5, SH5]`
**Rotura:** el slot está fijado a **2 dígitos numéricos en rango 01-52**: `codes.py:53` emite `f"CDP-{cc}-{province_code}-..."` y `complete.py:73,89` lo validan como `[0-9]{2}` `[VERIFIED]`. No cabe:
- **FR:** departamentos 53-95 (fuera de rango), Córcega **2A/2B** (alfanumérico), ultramar **971-976** (3 dígitos).
- **IT:** sigla de **2 LETRAS** (MI/RM/TO) o código ISTAT **>99** (hasta 111).

El diseño lo trató como "swap de regex" — **FALSO**: es un cambio de **gramática del código inmutable** (ancho + alfabeto) que toca `mint_code`, `_CDP_CODE_RE` y la garantía golden byte-idéntica.

**RESOLUCIÓN de diseño (⚠ parcial):** la subdivisión pasa a ser una **gramática declarada por el country-pack**: una función `encode_subdivision(CC, native_id) → token` que mapea el id administrativo nativo a un **token de ancho fijo en el alfabeto Crockford-base32** (que ya admite alfanuméricos `[VERIFIED codes.py:26]`). Córcega `2A`/ISTAT `111`/ultramar `976` caben en un token base32 de ancho suficiente. El `country.toml` declara `subdivision_width` + `subdivision_encoding`.

**OPEN ITEM (gateado — irreversibilidad de §Autonomía):** decidir el **ancho universal del slot** es una decisión que toca la **forma del `cdp_code`** (invariante inmutable) y el **golden ES**. Dos caminos, ambos con coste:
- **(i) códigos de ancho variable por país** (ES mantiene su slot de 2; otros declaran el suyo): preserva el golden ES byte-idéntico, pero el `cdp_code` deja de tener longitud fija global.
- **(ii) migración a un slot universal más ancho** (p.ej. 3 base32): uniforma la forma, pero **rompe el golden ES** y exige re-mint masivo.

Esto es una **bifurcación arquitectónica irreversible** → se queda como `OPEN ITEM` con **gating de firma del owner** (decisión de arquitectura, no reversible: cambia el código inmutable). **Diseño recomendado:** camino (i) + el gate **`GRAMMAR_FREEZE`** en `REGISTERED→BOOTSTRAPPED` que congela `subdivision_width/encoding` ANTES del primer mint, porque (SH5) `cdp_code` es inmutable y la historia append-only: mintear con gramática equivocada huérfana el ledger. **No se transcribe como "resuelto"; se declara la bifurcación y su gate.**

### Clúster C — Ceguera de moneda `[B5 MX, B7 JP, MP1, MP2]`
**Rotura:** `detect_fabrication` usa techo ABSOLUTO en EUR implícito `[VERIFIED detect.py:70]` (`FAB_PRICE_CEIL = 5_000_000`) con `quarantines=True` `[VERIFIED Wave1 detect.py:600]`. La columna `currency CHAR(3) DEFAULT 'EUR'` EXISTE `[VERIFIED migrations/0003:14]` pero **ningún detector la lee**. Consecuencias:
- **JP:** ¥5M ≈ 30k EUR → **TODO** coche japonés > ~30k dispara `fabrication` → las vistas `servable_*` lo EXCLUYEN `[VERIFIED 0031:146-168]` → **el sellado se vuelve kill-switch de país entero**, y CI sigue verde (golden ES no cambia).
- **MX:** 5M MXN ≈ 230k EUR → el inventario premium se cuarentena. `PRICE_TRAP_FLOOR=300`/`HIGH_ABS_FLOOR=150_000` también EUR `[VERIFIED detect.py:91-105]`.

**RESOLUCIÓN (✅ cierra, €0):** (1) **fix de motor UNA vez** — `detect_fabrication`/`price_trap` leen `currency` y normalizan `price` a un numérario común (o particionan por moneda) antes de comparar; (2) **pack** — `FAB_PRICE_CEIL/FLOOR/KM` y los floors de `price_trap` se mueven de constantes de módulo a `country.toml` **en la moneda del país** (MP2). Cierra MX y JP. Puro código + `.toml`, sin €.

### Clúster D — Pooling cross-country de cohortes `[B8 JP, B10 EUR]`
**Rotura:** `price_trap` arma la cohorte con `GROUP BY make, model, year` `[VERIFIED detect.py:786]` SIN partición por país/moneda y SIN join a `entity.country_code`; `field_loss` toma baseline `FROM vehicle WHERE status=available` sin filtro de país `[VERIFIED Wave1 detect.py:349]`. Una cohorte "Toyota Corolla 2020" mezcla EUR+MXN+JPY → mediana/MAD de `ln(price)` multimodal → detector ciego o falsos. Incluso **dentro del EUR**, FR/IT/DE/PT difieren por VAT/bonus-malus/impuesto de matriculación → baseline contaminado en cuanto coexisten 2 países. Nota de esquema: `country_code` NO está en `vehicle` (2.311.202 filas, YAGNI) `[VERIFIED 0052:36-38]`.

**RESOLUCIÓN (✅ cierra, €0):** **fix de motor UNA vez** — añadir `JOIN entity ON vehicle.entity_ulid = entity.entity_ulid` y `GROUP BY ..., entity.country_code` en `price_trap` y `field_loss`. `country_code` es derivable vía entity `[VERIFIED 0052:36-38]`, así que NO hace falta tocar las 2,3M filas de `vehicle`. **Honestidad:** añade el coste de un JOIN a 2,3M filas por corrida; aceptable, y si pesa se denormaliza `country_code` a `vehicle` como optimización posterior (la nota 0052 lo dejó explícitamente como YAGNI, no como imposible). Esto distingue *country-blind* (lo que hay) de *country-correct* (lo que exige el sellado).

### Clúster E — Anclas, censo externo y la máquina de intervalo `[B2 DE, B6-anclas MX, MP3, MP4, SH2]`
**Rotura:** `coverage_gap` consume `COVERAGE_ANCHORS` hardcodeado a instituciones ESPAÑOLAS `[VERIFIED detect.py:78-83]` (DGT 1.292 desguace, FACONAUTO 2.018, Páginas Amarillas), y el sellador de intervalo triangula contra el censo ES `[VERIFIED seal.py:68-69]` (`If None, the CSV at countries/ES/census/ is auto-loaded`; `load_external_census()`). Con anclas ES, el detector y el intervalo certificado dan basura para DE (necesita KBA+ZDK+Gelbe Seiten) o MX. **SH2 — la pieza que el diseño OMITIÓ:** la máquina que produce el INTERVALO real es `exhaustiveness/seal.py`+`capture.py`, hardwired a estrata `province_code × segment ~ 52×4` `[VERIFIED capture.py:8]` y `kind→4 segmentos` ES `[VERIFIED capture.py:31]` — y estaba **ausente del country-pack del diseño**, que citó `complete.py` G1-G5 (gate por-entidad) como criterio, cuando ESA no es la máquina que genera el intervalo.

**RESOLUCIÓN (✅ cierra; integra la omisión):** se **añaden al country-pack** dos artefactos que el diseño olvidó: (1) `countries/{CC}/census/` + la tabla de anclas en `country.toml` (reemplazan `COVERAGE_ANCHORS` y `load_external_census()` — `paths.census_dir(country_code)` ya existe `[VERIFIED paths.py:50-52]`); (2) la **definición de estrata** `subdivisions × segment` parametrizada por el conteo de subdivisiones del país y su mapa de segmentos (hoy `52×4`). El sellador de intervalo es propiedad de **stage 07-quality-seal**; el cerebro (stage 10) lo **consume** como gate (a). Se corrige explícitamente la afirmación del diseño de que `complete.py` era "la máquina de sellado genérica": es el gate por-entidad, no el generador de intervalo.

### Clúster F — Extensión del ENUM `entity_kind` `[B6-enum MX, MP6]`
**Rotura:** `entity_kind` es un **ENUM de Postgres** `[VERIFIED 0005:13-17]` (concesionario_oficial, agente_oficial, compraventa, garaje, desguace, rent_a_car_vo, subasta, importador, oem_vo_portal, plataforma, cadena[DEPRECATED]). Un kind genuinamente nuevo (auction keiretsu JP, "lote"/"agencia de seminuevos" MX, kei-car) exige `ALTER TYPE entity_kind ADD VALUE` = **MIGRACIÓN**, NO un override en `country.toml`. El diseño afirmó "el country-pack solo aporta léxico local→canónico" — **over-claim**: solo holds cuando el kind nativo mapea a un canónico existente.

**RESOLUCIÓN (✅ cierra; corrige el over-claim):** el country-pack declara DOS cosas: (a) el léxico local→canónico (caso común: el "Autohaus" alemán → `concesionario_oficial`), y (b) un **manifiesto de migración** cuando el mercado exige un canónico genuinamente nuevo. El gate `REGISTERED→BOOTSTRAPPED` de `cover(CC)` ejecuta esa migración additive+reversible (`[VERIFIED 0005:87]` el rollback `DROP TYPE` existe como patrón). La verdad: la mayoría de kinds extranjeros mapean al vocabulario existente; el manifiesto cubre la minoría irreducible sin pretender que un ENUM se extiende declarativamente.

### Clúster G — Seam de cadencia/SLA por país `[MP7]`
**Rotura:** `LANE_SLA` `[VERIFIED route.py:28-34]`, `STALENESS_TTL` `[VERIFIED detect.py:51-62]` y los 8 jobs + el lock host-singleton `[VERIFIED scheduler.py:913]` son **globales**. El country-pack menciona "override de SLA por tier" pero el motor **NO tiene seam** para inyectarlo: hoy es aspiracional.

**RESOLUCIÓN (✅ cierra, €0; seam nuevo):** se añade un cargador `per-CC cadence/SLA` (`country.toml`) consumido por `route`/`detect`. El lock host-singleton **se queda** (es un mutex de host, no una dimensión de país — correcto que sea único); lo que itera por país es el nuevo `country_campaign_tick`, que ya recorre todas las filas `country_campaign`. Net-new seam, declarado como a-construir, sin €.

### Clúster H — Piso de independencia del quórum `[B9 PT, MP10, SH6]`
**Rotura:** el cierre `RESOLVED` exige `quorum_n>=2` con caminos INDEPENDIENTES `[VERIFIED route.py:243, 0036:28]`, y `INCONCLUSIVE/NO_INDEPENDENT_PATH → ESCALATE_OWNER` `[VERIFIED router.py:84,93]` → humano. En un mercado de cola fina (PT, o regiones MX/JP con un solo portal dominante) puede **no existir** un 2º camino independiente → el país entero cae al dead-end humano.

**RESOLUCIÓN de diseño (⚠ sin debilitar VAM):** **NO** se baja el piso de quórum — eso violaría la cero-confianza, núcleo de la doctrina (`ANTI-DRIFT §1.3`). En su lugar: (a) `KNOW_COUNTRY` ya exige **≥3 listas ortogonales de denominador** como gate de salida del Dossier `[VERIFIED COVER-NEW-COUNTRY.md:43,55]` — el país que no las consigue lo declara ANTES de proceder; (b) donde un estrato genuinamente tenga 1 sola vía, se enruta al **bus** (`VAM_DISCREPANCY`/`COVERAGE_SEAL_REVIEW`) con provenance explícita "single-source, lower-confidence" para adjudicación de Claude, **NUNCA auto-cierre como TRUSTWORTHY**; el sello de ese estrato es un **intervalo de menor confianza declarado**, no una certificación falsa.

**OPEN ITEM (gateado):** si un país no puede suministrar ≥2 vías ortogonales para una fracción material de estratos, su sello queda **acotado por abajo honestamente** y ese residual se queda `PENDING-OWNER` — no para el loop, no se maquilla (`00-MASTER` §Gates). El dead-end humano NO desaparece por arte de magia; se canaliza por el bus y se acota el sello. Honestidad cruda: el diseño original no ofrecía alternativa por país; esta es la integración.

### Clúster I — G3 recipe depende del `llm_local` dormante `[SH7]`
**Rotura:** G3 necesita una receta; el ladder `next_data|jsonld|css|llm_local` `[VERIFIED recipe_schema.py:67]` tiene `llm_local` **DORMANTE** (capa-2 = 0 código). Para un país cuyos portales dominantes exigen render JS más allá de `css`, no hay engine que produzca receta → G3 falla → INCOMPLETE → no sella.

**RESOLUCIÓN (⚠ a €0 vía Claude):** la extracción que el ladder determinista no resuelve se enruta al bus (`kind=RECIPE_TIER1_NEW`/`RECIPE_FIELD_EXTRACT`) → **Claude (capa-3) redacta la receta** — exactamente la fuente que el bus ya lista. El rung `llm_local` queda como optimización futura (palanca GPU/€>0), no como blocker. G3 es **alcanzable a €0** vía recetas autoría-Claude.
**OPEN ITEM (owner stage 02):** si un portal exige **infraestructura de render** (headless browser) que el harness de scraping no provee, eso es deuda de la **etapa 02-scrape**, no del cerebro; se marca aquí como **dependencia de sellado** y se delega a su owner. El cerebro no puede inventar capacidad de scraping que no existe.

### Clúster J — Mint bypass cross-cutting `[risk#1]`
**Rotura:** los connectors de `pipeline/platform/` acuñan `CDP-ES-` a mano (`[VERIFIED wallapop_wholesale.py:225]`) y **0 usan `mint_code()`** (`[VERIFIED]` grep `mint_code\(` = sin matches). Conteo corregido: 47 `.py`, 31 hardcodean `f"CDP-ES-"`, no 63.
**RESOLUCIÓN (✅ cierra):** enrutar los mints a `mint_code(country_code=campaign.country_code)`; salida ES byte-idéntica (golden). Owner: etapa identity; **BLOQUEA** `cover(CC)` porque una campaña no-ES vía platform connector acuñaría `CDP-ES-`. Dependencia declarada, fix de motor UNA vez.

### Clúster K — El método de verificación del diseño era hueco `[SH3, SH4, MP9]`
**Rotura:** el diseño "probaba" la genericidad de los detectores con "grep `CDP-ES` = 0 en `detect.py`". **La ausencia del literal NO es agnosticismo de país** `[VERIFIED]`: `COVERAGE_ANCHORS` (DGT/FACONAUTO) y `FAB_PRICE_CEIL` (EUR) son ES/EUR-shaped **sin** el substring `CDP-ES`. Y los detectores country-blind ARMAN el sellado contra el país nuevo: al onboardear no-EUR, `detect_fabrication` marca masivamente falsos positivos → `servable_*` ocultan el país entero → kill-switch — y **CI sigue verde** porque el golden ES no cambia.
**RESOLUCIÓN (✅ cierra; adoptada como estándar de la etapa):** la 2ª vía real NO es un grep de string sino un **golden + Ferrari de detector POR PAÍS** (MP9): un fixture sintético en la moneda/escala nacional que corre los 7 detectores live y **prueba que no hay mass-quarantine**. CI gana un golden por país; sin él, CI verde es **carente de significado** para el país nuevo. Esto materializa el `ANTI-DRIFT §Cómo se PRUEBA` (test + intento adversarial + vía independiente) a nivel de detector.

### Clúster L — Física de paginación de `silent_cap` `[MP8]`
**Rotura:** `SILENT_CAP_PAGE_SIZE=20` y `SILENT_CAP_ROUND_CEILINGS={500,1000,2000,5000}` `[VERIFIED detect.py:39-42]` son heurísticas de portales ES; mobile.de/lacentrale.fr/goo-net paginan distinto.
**RESOLUCIÓN (✅ cierra, pack-level):** mover estas constantes a una **spec de paginación por portal** en el pack (o portal-pack). Bajo esfuerzo; no toca el algoritmo de `silent_cap`, solo sus parámetros por fuente.

---

## Sub-proyectos institucionales (360 por faceta)
<a id="indice-subproyectos"></a>
> **Funnel:** nadie se pierde. Cada **clúster** del veredicto adversarial se abre aquí átomo-a-átomo. Doctrina del `00-MASTER` §Operación: *cada punto = proyecto paralelo, exprimido al máximo como proyecto independiente*. Esto es esa expansión: **33 sub-proyectos 360** — la descomposición COMPLETA —, cada uno con su **deep-spec `(a→f)`** (code_hints `[VERIFIED path:línea]` → mecanismo al átomo → costura ES→genérico+fix → riesgo adversarial DE/FR/IT/PT/no-UE/ruido → sellado multi-vía → herramienta NEXT-LEVEL `€0`).

> **Cómo leer cada entrada:** primero la **ficha rápida** (cinco líneas: costura/fix/adversarial/sellado/NEXT-LEVEL) para escanear; debajo, el **deep-spec 360** completo para el que ejecuta. Honestidad cruda preservada: cada open item viaja con su causa.

> **Cobertura COMPLETA (v2):** se integran las **33 facetas** de la descomposición (insumos verificados `g0..g6`). La síntesis v1 cubrió solo 24 (insumos `g0/g1/g2/g3/g6`) y dejó 9 declaradas-pendientes; **esta v2 cierra las 9 restantes** — *5* (umbrales de detector en moneda), *6* (cohorte `price_trap`), *12* (sesgo de la 2ª-vía/`TAU` del prosecutor), *13* (núcleo durable del scheduler + servicio Windows), *19* (`derive_verdict` + delta `g5_check.py`), *20* (estrata `provincia×segmento`), *26* (drenado del bus por Claude), *27* (FSM `cover(CC)`), *33* (Ferrari de detector por-CC) — con deep-dive `[VERIFIED]` propio. **Corrección de numeración (BLINDAJE):** la asignación autoritativa es round-robin (el insumo `g_i` aporta las facetas `i+1, i+8, i+15, i+22, i+29`); por eso `field_loss`=**7** (no 9), `silent_cap`=**9** (no 7), `lease/heartbeat`=**14** (no 13) y el ENUM `entity_kind`=**30** (antes sin número). Cero pérdida de lo construido; los gloses ES se preservan.

**Mapa por macro-grupo** (la lectura temática; la tabla siguiente va en orden numérico estable):
- **I · Cerebro determinista, bus, cadencia y orquestación — la cola que resuelve, escala y conduce**: facetas **1, 2, 3, 11, 13, 14, 15, 23, 24, 25, 26, 27**.
- **II · Identidad inmutable + backbone declarativo — `cdp_code` country-proof + `country.toml`**: facetas **16, 17, 29, 30, 31, 32**.
- **III · Detectores country-correct — no *country-blind***: facetas **4, 5, 6, 7, 8, 9, 33**.
- **IV · Quórum, intervalo y sello — VAM cero-confianza, 100%=intervalo**: facetas **10, 12, 18, 19, 20, 21, 22, 28**.

### Índice de sub-proyectos
| # | Sub-proyecto | Qué cierra | v1 |
|---|---|---|---|
| [1](#faceta-1) | State-machine del gestionador (cola que resuelve sin Claude) | La cola que cierra sin Claude: 9 estados + guard RESOLVED⇒TRUSTWORTHY+quorum≥2. | Infra · cola determinista |
| [2](#faceta-2) | Ledger append-only + dientes de cuarentena (servable views) | El kill-switch reversible: la vista servable oculta el subject sin un solo DELETE. | Infra · ledger |
| [3](#faceta-3) | Framework de cadencia de detectores (run_all + registry + STUB activation) | El arnés never-raises / QUARANTINE-only / registry-driven: country-blind, no country-correct. | Infra · arnés |
| [4](#faceta-4) | Moneda + contexto-pais de los hechos de vehiculo (substrato de particion) | El substrato (currency, country_code) bajo todo hecho de precio antes de comparar. | Clúster C |
| [5](#faceta-5) | Pack de umbrales de detector de valor por-pais (fabrication/price_trap) | Las magnitudes de mercado (5M/150k/300 EUR) de constante de módulo a country.toml tipado por-CC. | Clúster C |
| [6](#faceta-6) | Particion de cohorte de price_trap (cohortes country/currency-correctas) | La cohorte country/currency-correcta: (country_code, currency) en el GROUP BY, comparación intra-moneda. | Clúster D |
| [7](#faceta-7) | Pooling cross-pais de field_loss + staleness (baseline/TTL) | Baseline/TTL country-blind ≠ country-correct: partición del estimador field_loss/staleness por-CC. | Clúster D |
| [8](#faceta-8) | Anclas ground-truth de coverage_gap por-pais | El piso de inventario por kind: censo institucional ES → ancla por-CC. | Clúster E |
| [9](#faceta-9) | Fisica de paginacion de silent_cap por-portal/pais | El tope silencioso por-portal: page_size + techos redondos inyectados por fuente. | Clúster L |
| [10](#faceta-10) | Motor de quorum + precision-gate + piso de independencia por-pais | indep≥2 sin debilitar VAM: proveer una 2ª vía real, jamás relajar el gate. | Clúster H |
| [11](#faceta-11) | Router sellado de veredicto + catalogo de FUENTES del bus (el punto de fuga) | La tabla sellada intacta; enumerar y enchufar a un bus durable lo que hoy muere en humano. | Infra · router |
| [12](#faceta-12) | Maquinaria de inquisicion (lenses/prosecutor/sampler) + prosecutor como 2a-via de sellado | El prosecutor como 2ª-vía genuina: tolerancias inyectadas + tri-agreement ER, sin sesgo ES heredado. | Clúster E/H |
| [13](#faceta-13) | Scheduler durable: nucleo crash-safe + mutex single-producer + activacion | El daemon durable: advisory-lock single-producer + servicio Windows versionado (el stack hoy CAÍDO). | Infra · liveness |
| [14](#faceta-14) | Capa de lease/heartbeat (observabilidad de liveness del orquestador) | Liveness del orquestador: dead-man externo + restart supervisado + shard por-(rol,CC). | Infra · liveness |
| [15](#faceta-15) | Pack de cadencia (8 jobs) + emision acotada/opt-in (anti-flood) | Los 8 jobs + emisión opt-in/acotada (anti-flood a €0). | Clúster G |
| [16](#faceta-16) | Gate G1 de identidad: ensanche del 6o-blocker (ES-lock de complete.py) | El 6º-blocker: ^CDP-ES- → ^CDP-([A-Z]{2})- y quitar el xfail. | Clúster A |
| [17](#faceta-17) | Redisreno de la gramatica del cdp_code (subdivision FR/IT alfa/3-digitos) | Ancho+alfabeto del slot {NN}: 2A/2B, 971-976, ISTAT>99 no caben en [0-9]{2}. | Clúster B |
| [18](#faceta-18) | Gates G2/G3/G4 de completitud (inventario/receta/servido) + ladder de extraccion | El ladder next_data→…→llm_local (rung dormante) + G5 inexistente + glob ES-locked. | Clúster I |
| [19](#faceta-19) | derive_verdict + prueba de delta G5 (el hueco g5_check.py) | El gate G5 ausente (g5_check.py inexistente): la ley de conservación D_after=D_before+NEW-GONE como contrato. | Clúster I |
| [20](#faceta-20) | Sellador de intervalo: estratificacion + matriz de captura | La matriz de captura: estrata provincia×segmento ES-shaped → grano de subdivisión por-CC. | Clúster E |
| [21](#faceta-21) | Sellador de intervalo: triangulacion contra censo externo por-pais | El 2º mecanismo del sello: panel de anclas, el desacuerdo es distrust. | Clúster E |
| [22](#faceta-22) | Sellador de intervalo: estimadores MSE + roll-up nacional + veredicto de sello | El intervalo nacional honesto: se certifica la cota inferior, nunca el punto. | Clúster E |
| [23](#faceta-23) | Bus de decisiones: esquema + contrato (decision_request/decision_event) | El contrato del bus: country_code día-0 + dedupe_key idempotente para reuso cross-país. | Infra · bus |
| [24](#faceta-24) | Interfaz triage() + clasificador de reversibilidad + freno de Autonomia | El freno de §Autonomía: reversible→bus, spend/prod/legal→humano (fail-closed). | Infra · freno |
| [25](#faceta-25) | Capa-2 decider IA local (local_ai_drain + confidence-gate + cierre de STUBs + golden-set) | El tier ausente: llama.cpp+gramática enchufa en los 2 slots sin tocar el motor. | Clúster I |
| [26](#faceta-26) | Capa-3 orquestador Claude: drenado en rafagas + apply + re-verificacion VAM | El cerebro pensante: drenado en ráfagas + apply + re-verificación VAM (apply→VERIFIED gateado). | Infra · cerebro |
| [27](#faceta-27) | Maquina de estados cover(country_code) + predicados + tick-job | El orquestador de onboarding: cover(CC) FSM REGISTERED→SEALED guard-gated + tick-job. | Infra · FSM |
| [28](#faceta-28) | Predicado de sellado + 2a-via ortogonal + COVERAGE_SEAL_REVIEW | El predicado SEALED = AND de 5 sub-criterios + 2ª-vía prosecutor + atestación. | Infra · sello |
| [29](#faceta-29) | Cargador del country-pack (manifest country.toml + loader cacheado por-CC) | El backbone declarativo: country.toml + loader fail-fast cacheado por-CC. | Infra · backbone |
| [30](#faceta-30) | Gobernanza de extension del ENUM entity_kind (no es override declarativo) | Un kind nuevo = ALTER TYPE = MIGRACIÓN, no un override declarativo en .toml. | Clúster F |
| [31](#faceta-31) | Threading de pais en los mints de plataforma (CDP-ES- -> mint_code(country_code=)) | 31 fugas f"CDP-ES-", 0 usan mint_code(): un solo hogar del prefijo + guard CI. | Clúster J |
| [32](#faceta-32) | Gate de congelacion de gramatica (anti-irreversibilidad del codigo inmutable) | Anti-irreversibilidad: congelar la gramática de {NN} ANTES del primer mint. | Clúster B |
| [33](#faceta-33) | Golden + Ferrari de detector POR PAIS (prueba CI anti silent-green) | La 2ª-vía real anti silent-green: Ferrari de detector por-CC, no un grep de string hueco. | Clúster K |

> Numeración autoritativa 1–33 (round-robin `g_i → i+1,i+8,i+15,i+22,i+29`). Todas las facetas con `facet_name` y deep-spec `[VERIFIED]`. Las 9 facetas que la síntesis v1 omitió (5,6,12,13,19,20,26,27,33) quedan integradas con su deep-dive completo.

---

<a id="faceta-1"></a>
### Faceta 1 · State-machine del gestionador (cola que resuelve sin Claude)
*La cola que cierra sin Claude: 9 estados + guard RESOLVED⇒TRUSTWORTHY+quorum≥2.*  ·  **v1:** Infra · cola determinista

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — La state-machine ya es country-blind (opera sobre subject_key de cualquier CC). La unica costura ES es LANE_SLA [route.py:28-34], constante de modulo con plazos 6h/7d/48h iberos y sin parametro country_code para inyectar override por-pais.
- **Fix exacto** — Declarar [lane_sla] por tier en country.toml (faceta 29); el loader cacheado entrega el dict y open_or_refresh resuelve sla por (lane, country_code). ES declara 6h/7d/48h en su manifest -> sla_due byte-identico. country_code se threadea desde country_campaign -> route_anomalies -> open_or_refresh. Cero cambio de esquema.
- **Riesgo adversarial** — PT/MX/JP monoportal: guard RESOLVED+quorum>=2 nunca satisfecho -> backlog infinito, nada cierra. LANE_SLA global aplica plazos espanoles a volatilidades ajenas. gestion_item VACIA = cero prueba de que el ON CONFLICT(dedupe_key) aguante colisiones concurrentes reales.
- **Sellado multi-vía** — Via1 golden: LANE_SLA del ES.toml == hardcode (5 deltas). Via2 ejercicio vivo bajo scheduler restart-supervisado: >=1 ciclo OPEN->RESOLVED real con verdict TRUSTWORTHY+quorum>=2 en gestion_transition (no sella con gestion_item vacia). Via3 concurrencia: N upserts del mismo dedupe_key -> 1 fila, 0 errores. Via4: RESOLVED con verdict REFUTED/quorum_n=1 rechazado por trg_gestion_resolved_proof Y por el mirror Python.
- **Herramienta NEXT-LEVEL** — transitions (pytransitions) — MIT — https://github.com/pytransitions/transitions [VERIFIED NEXT-LEVEL.md:595]. La biblia nombra route.py:48-58 VALID_TRANSITIONS como el piso en-repo (NEXT-LEVEL.md:596). Eleva el dict a FSM declarativa guard-gated: conditions= = predicado computable, GraphMachine = diagrama, solo-transicion-legal impuesta. €0 CPU.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) code_hints VERIFICADOS
- **9 estados** [VERIFIED pipeline/gestionador/route.py:48-58] `VALID_TRANSITIONS` = {OPEN, ROUTED, IN_PROGRESS, REVERIFYING, QUARANTINED, ESCALATED, RESOLVED, REOPENED, WONT_FIX}. WONT_FIX es terminal (`set()`); RESOLVED solo va a REOPENED (regresion). Conté 9 claves: byte-cierto.
- **Guard de transicion** [VERIFIED route.py:63-80] `assert_valid_transition` lanza `ValueError` si el destino no esta en `ALL_STATES`, si la inicial no apunta a OPEN, o si el par from->to no esta permitido. Determinista, sin discrecion.
- **LANE_SLA** [VERIFIED route.py:28-34] dict de modulo: AUTO_FIX 6h, RESEARCH 7d, QUARANTINE 48h, ESCALATE_GASTO None, ESCALATE_OWNER None. Es **constante de modulo** — no recibe `country_code` por ningun parametro.
- **Upsert idempotente** [VERIFIED route.py:87-190] `open_or_refresh`: `INSERT INTO gestion_item ... ON CONFLICT (dedupe_key) DO UPDATE` que **solo** refresca measured/severity/score; si `closed_at IS NOT NULL` reabre a REOPENED y limpia closed_at/closed_reason. `RETURNING id, state, (xmax = 0) AS is_new` distingue alta de refresco con un solo round-trip (MVCC-safe).
- **Guard RESOLVED** [VERIFIED route.py:229-248] dentro de `transition`: RESOLVED exige `verdict_id` no nulo, que el verdict exista, y que sea `verdict == 'TRUSTWORTHY' AND quorum_n >= 2`. Es el fail-fast espejo del trigger DB.
- **trigger DB** [VERIFIED migrations/0036_gestion_resolved_proof.sql presente] `trg_gestion_resolved_proof` es la garantia dura en PG; el docstring route.py:225-228 lo nombra explicitamente.
- **auto-route** [VERIFIED route.py:318-324] `_routing_lane_to_first_state`: quarantines->QUARANTINED; lane in {ESCALATE_GASTO, ESCALATE_OWNER}->ESCALATED; else ROUTED.
- **append-only** [VERIFIED route.py:331-354] `_append_transition` = INSERT puro en gestion_transition (nunca UPDATE/DELETE).

#### (b) El mecanismo al atomo
Cada anomalia (`AnomalyResult`, detect.py:114-127) llega con `lane`, `quarantines`, `dedupe_key`. `route_anomalies` (route.py:289-315) hace por item: (1) `open_or_refresh` -> upsert por dedupe_key; (2) re-lee el estado; (3) si quedo en OPEN, lo auto-avanza al primer estado del lane via `transition`. El cierre RESOLVED es la unica puerta con prueba: **no hay close sin recheck** — verdict TRUSTWORTHY+quorum>=2, doblemente garantizado (trigger 0036 + mirror Python). La maquina es **pura y country-blind**: opera sobre `subject_key` (que lleva cdp_code o vehicle_ulid de cualquier CC) sin leer pais.

#### (c) Costura ES->generico + fix exacto
La costura **no** esta en la state-machine (ya es generica) sino en **LANE_SLA como constante de modulo** [route.py:28-34]: los plazos 6h/7d/48h son de mercado espanol y no hay seam para inyectarlos por-CC.
**Fix:** el `country.toml` (faceta 29) declara `[lane_sla]` por tier; el loader cacheado entrega el dict y `open_or_refresh` resuelve `sla_delta = LANE_SLA_for(anomaly.lane, country_code)`. ES declara 6h/7d/48h en su propio manifest -> `LANE_SLA.get` produce datetime byte-identico al hardcode. Cambio quirurgico: el `country_code` viaja desde la fila `country_campaign` (faceta 27) -> `route_anomalies(..., country_code=)` -> `open_or_refresh`. Cero cambio de esquema (la columna `sla_due` ya es TIMESTAMPTZ nullable).

#### (d) Riesgo adversarial concreto
- **PT / region MX-JP monoportal (cola fina):** el guard RESOLVED+quorum>=2 nunca se satisface (no hay 2a via independiente, faceta 10) -> ningun item cierra -> **backlog infinito**, la cola crece sin drenar.
- **Escala multi-pais:** LANE_SLA global aplica deadlines iberos a volatilidades ajenas -> SLA de 48h de cuarentena puede ser absurdo en un mercado de rotacion lenta o demasiado laxo en uno volatil.
- **gestion_item VACIA:** la maquina jamas corrio bajo carga real (solo tests) -> cero evidencia de que el `ON CONFLICT (dedupe_key)` aguante colisiones concurrentes reales (dos detectores disparando el mismo subject en paralelo) sin churn ni deadlock.

#### (e) Criterio de sellado + verificacion multi-via
- **Via 1 (golden byte-identity):** `LANE_SLA` cargado del ES.toml == hardcode actual (test que compara los 5 deltas).
- **Via 2 (ejercicio vivo):** bajo el scheduler restart-supervisado (faceta 13), `country_campaign_tick` genera gestion_item REALES; se exige >=1 ciclo completo OPEN->...->RESOLVED con verdict TRUSTWORTHY+quorum>=2 observado en gestion_transition. No es sellado mientras gestion_item este vacia.
- **Via 3 (concurrencia):** test que dispara N `open_or_refresh` concurrentes del mismo dedupe_key -> exactamente 1 fila, 0 errores, transiciones append-only coherentes.
- **Via 4 (guard DB co-igual):** intentar RESOLVED con verdict REFUTED o quorum_n=1 -> rechazado por trg_gestion_resolved_proof **y** por el mirror Python (ambos caminos probados).

#### (f) Herramienta NEXT-LEVEL
**transitions (pytransitions)** — MIT, https://github.com/pytransitions/transitions [VERIFIED NEXT-LEVEL.md:595]. La biblia lo asigna nominalmente a cover(CC) pero **nombra route.py:48-58 `VALID_TRANSITIONS` como el piso en-repo** [NEXT-LEVEL.md:596] — misma clase de mecanismo. Eleva el dict hecho a mano a una FSM declarativa guard-gated: `conditions=`/`unless=` = el predicado computable que gatea cada transicion (p.ej. el guard RESOLVED), `GraphMachine` auto-renderiza el diagrama del funnel, y la libreria impone solo-transicion-legal (cero salto ilegal) mientras la DB sigue siendo la verdad (persistencia via `on_enter`). Verificacion (NEXT-LEVEL.md:598): transicion ilegal rechazada por la libreria; grafo GraphMachine == contrato de estados. €0, CPU puro.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-2"></a>
### Faceta 2 · Ledger append-only + dientes de cuarentena (servable views)
*El kill-switch reversible: la vista servable oculta el subject sin un solo DELETE.*  ·  **v1:** Infra · ledger

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — El esquema es generico dia-0 (subject_key TEXT lleva cdp_code/vehicle_ulid de cualquier CC) y la cuarentena es reversible via closed_at (jamas DELETE). La costura no es de extraccion sino de gobernanza: falta (a) politica de quien cuarentena a escala-pais y (b) un freno + testigo del kill-switch de pais entero que hoy puede apagar MX/JP en silencio con CI verde.
- **Fix exacto** — Anadir un guard de mass-quarantine antes de servir cover(CC): predicado ratio = count(servable_entity WHERE country=CC) / count(entity WHERE country=CC); si cae bajo un piso por una rafaga country-blind, NO servible -> emite decision_request COVERAGE_SEAL_REVIEW (faceta 23) en vez de blackout. La reversibilidad (closed_at re-muestra) y el append-only (_append_transition INSERT-only, route.py:331-354) ya existen; se conservan byte-identicos. Dead-man externo (Healthchecks) pinga el colapso de servable_*(CC).
- **Riesgo adversarial** — servable_* es kill-switch de PAIS ENTERO: fabrication/price_trap con techos EUR (facetas 4/5) disparan masivamente en MX/JP con quarantines=TRUE -> oculta todo el inventario mecanicamente, CI verde porque golden ES no cambia (faceta 33) -> apagon invisible hasta produccion. DE/FR/IT/PT igual mecanismo si un detector country-blind se ceba. Ruido: cuarentena en bucle (REOPENED sin cerrar) mantiene el pais oculto.
- **Sellado multi-vía** — (1) Prueba de reversibilidad: open quarantines=TRUE oculta, close re-muestra, count(entity) invariante. (2) Golden SQL servable_entity == entity EXCEPT cuarentenados-abiertos + test no-DELETE. (3) Guard mass-quarantine: fixture de N cuarentenas country-blind corta antes del blackout (ratio<piso => decision_request, no apagon). (4) Dead-man externo confirma colapso out-of-band.
- **Herramienta NEXT-LEVEL** — Healthchecks (BSD-3-Clause, EUR0) https://github.com/healthchecks/healthchecks [VERIFIED NEXT-LEVEL.md:560-566] — dead-man switch externo con reloj propio, un check por (rol,CC) nombra el pais apagado. Complemento: in-toto (Apache-2.0) https://github.com/in-toto/in-toto [VERIFIED NEXT-LEVEL.md:640-646] para tamper-evidence del ledger append-only.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### Mecanismo al atomo [VERIFIED]
- **gestion_item** (migrations/0031_gestion.sql:44-96): un ticket por (detector, subject, time-bucket). Los atomos que importan: `quarantines BOOLEAN NOT NULL DEFAULT FALSE` (:80) = LOS DIENTES; `closed_at TIMESTAMPTZ` (:89) = el eje de reversibilidad; `dedupe_key TEXT NOT NULL, UNIQUE (dedupe_key)` (:94-95) = idempotencia (una sola fila abierta por condicion recurrente); `verdict_id BIGINT REFERENCES verification_verdict(id)` (:84) = prueba de cierre.
- **gestion_transition** (0031:121-131): auditoria inmutable. `item_id BIGINT ... ON DELETE CASCADE` (:123), columnas from_state/to_state/actor/note/payload/at. NUNCA recibe UPDATE ni DELETE.
- **idx_gestion_quar** (0031:104-106): indice PARCIAL `(subject_type, subject_key) WHERE quarantines AND closed_at IS NULL` — convierte el gate de cuarentena en un lookup O(1).
- **servable_entity** (0031:146-156): `SELECT e.* FROM entity e WHERE NOT EXISTS (SELECT 1 FROM gestion_item g WHERE g.quarantines AND g.closed_at IS NULL AND g.subject_type='entity' AND g.subject_key = e.cdp_code)`. **servable_vehicle** identico contra `v.vehicle_ulid::TEXT` (:158-168). La API lee la VISTA, jamas la tabla: el instante en que abre un item cuarentenante, el subject desaparece de toda superficie servida — invariante de DB, no promesa (:139-144).
- **route.py:_append_transition** (331-354): INSERT-only puro en gestion_transition. `transition()` (197-282) hace UPDATE de gestion_item (no de la tabla de auditoria) y SIEMPRE invoca _append_transition. La reversibilidad: REOPENED limpia `closed_at = NULL, closed_reason = NULL` (route.py:267-268); cerrar el item (closed_at = now, :255-256) lo oculta sin borrarlo, reabrirlo lo re-muestra.
- [VERIFIED] el UNICO borrado en 0031 es el FK CASCADE (:123, sobre delete del item padre, que el flujo normal nunca ejecuta — los items se cierran via closed_at) y el bloque rollback DROP (:170-174). CERO DELETE de subjects, CERO NULLs destructivos. Es un kill-switch reversible por construccion.

#### Costura ES->generico
El esquema YA es generico y reversible: `subject_key` es TEXT y transporta cdp_code/vehicle_ulid de cualquier CC sin un solo cambio. La costura NO es de esquema sino de GOBERNANZA + OBSERVABILIDAD: (a) quien/que puede poner quarantines=TRUE a escala-pais, y (b) que la vista — un kill-switch de PAIS ENTERO — no se dispare en masa de forma silenciosa. La reversibilidad ya esta; lo que falta es el FRENO mecanico y el testigo externo del apagon.

#### Riesgo adversarial concreto
La vista es un apagon de pais entero: si fabrication/price_trap (techos EUR implicitos, facetas 4/5) disparan masivamente en MX/JP con quarantines=TRUE, servable_* oculta TODO el inventario del pais — y CI sigue VERDE porque el golden ES no cambia (no hay golden de detector por pais, faceta 33). El sellado se vuelve kill-switch y nadie lo ve hasta produccion. DE/FR/IT/PT: el mismo mecanismo si un detector country-blind se ceba (menos extremo, igual de invisible). Ruido: un detector con bug que cuarentena en bucle re-abre el item (REOPENED) sin cerrar -> backlog que mantiene el pais oculto indefinidamente.

#### Sellado + verificacion multi-via
1. **Reversibilidad mecanica**: abrir item quarantines=TRUE oculta el subject de servable_*; cerrarlo (closed_at) lo re-muestra; assert que count(entity) es invariante (cero filas borradas).
2. **Golden SQL**: servable_entity == entity EXCEPT {subjects con item cuarentenante abierto}; test de no-DELETE (el rollback solo DROPea; ningun path mutila la auditoria).
3. **Guard de mass-quarantine**: fixture que dispara N cuarentenas country-blind y verifica que el freno corta ANTES del blackout — si ratio servable(CC)/entity(CC) < piso, emite decision_request COVERAGE_SEAL_REVIEW (faceta 23) en vez de apagon silencioso.
4. **Dead-man externo**: confirma out-of-band si servable_*(CC) colapsa, con reloj propio que CI (golden-ES) y el watchdog in-process no tienen.

#### Herramienta NEXT-LEVEL
**Healthchecks** (BSD-3-Clause) https://github.com/healthchecks/healthchecks [VERIFIED NEXT-LEVEL.md:560-566]: dead-man switch EXTERNO con reloj propio que detecta el colapso/silencio que el watchdog in-process es ciego a ver (no puede detectar su propia muerte ni un blackout de servable_*). Un check por (rol,CC) nombra que pais se apago. Complemento tamper-evidence: **in-toto** (Apache-2.0) https://github.com/in-toto/in-toto [VERIFIED NEXT-LEVEL.md:640-646] para atestar criptograficamente que el ledger append-only no fue mutado — el audit ES la prueba, verificable por terceros sin confiar en nosotros.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-3"></a>
### Faceta 3 · Framework de cadencia de detectores (run_all + registry + STUB activation)
*El arnés never-raises / QUARANTINE-only / registry-driven: country-blind, no country-correct.*  ·  **v1:** Infra · arnés

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — El arnes run_all es estructuralmente agnostico (itera DETECTORS, salta STUB_DETECTORS, sin literal de pais [VERIFIED run.py:92-95]); la costura NO esta en el framework sino en las constantes ES/EUR de los 7 detectores live que ejecuta -> es country-BLIND, no country-CORRECT. Ademas los 2 STUB (geo_resolution_drift, classifier_drift) devuelven [] [VERIFIED detect.py:898,916].
- **Fix exacto** — Dejar run_all byte-identico; inyectar la country-correctness via los params de los detectores (otras facetas) + un fixture Ferrari por-CC (faceta 33) que pruebe 0 mass-quarantine; gatear la activacion de cada STUB tras existir su backing data (geo: sentinel_placement_rate tracking; classifier: golden_set por-CC), nunca activar un slot que no entrega cobertura.
- **Riesgo adversarial** — run_all aplica el mismo codigo a todo pais: en MX/JP fabrication/price_trap con techos EUR disparan masivos -> quarantines=TRUE -> servable_* oculta el pais, y el aislamiento por-detector loguea nada (medir mal no lanza excepcion). Los 2 STUB devuelven [] en silencio: cero deteccion de deriva geo/clasificador en el mercado nuevo. Invisible hasta prod porque CI usa golden ES.
- **Sellado multi-vía** — Sello: run_all sobre Ferrari por-CC con total_flagged en banda y 0 mass-quarantine; los 2 STUB devuelven anomalias reales sobre fixture con deriva sembrada O se declaran inertes en el manifest (no [] silencioso); test de aislamiento (detector que lanza -> flagged=-1, resto completa). Multi-via: dry_run_all(9) vs run_all(7 live) concuerdan en los live; gestion_item por actor='gestionador:<name>' == flagged; adversarial matar un detector y verificar continuidad.
- **Herramienta NEXT-LEVEL** — Evidently (Apache-2.0, EUR0) https://github.com/evidentlyai/evidently [VERIFIED NEXT-LEVEL.md:616-622] cierra el STUB classifier_drift emitiendo CLASSIFICATION_DOUBT en vez de []; complemento river (BSD-3-Clause) https://github.com/online-ml/river [VERIFIED NEXT-LEVEL.md:576-582] para cadencia auto-ajustable. Emisor opt-in/acotado (INQUISITION_EMIT) anti auto-DoS.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) Verificacion de code_hints [VERIFIED]
- [VERIFIED pipeline/gestionador/detect.py:926-936] `DETECTORS` = lista de 9 tuplas `(name, coroutine)` en orden de ejecucion: count_inflation, silent_cap, field_loss, staleness, fabrication, coverage_gap, price_trap, geo_resolution_drift, classifier_drift. Es la "single source of truth (consumed by dry_run_all AND run.run_all)".
- [VERIFIED detect.py:938-940] `STUB_DETECTORS: frozenset = {"geo_resolution_drift","classifier_drift"}` -> 7 live + 2 STUB.
- [VERIFIED detect.py:886-898] `detect_geo_resolution_drift` -> `return []` (STUB; exige columna/tabla sentinel_placement_rate que no existe).
- [VERIFIED detect.py:905-916] `detect_classifier_drift` -> `return []` (STUB; exige golden_set table + classifier eval pipeline, T08 5.1 no implementado).
- [VERIFIED pipeline/gestionador/run.py:68-116] `run_all`: itera `detect.DETECTORS`; `if name in detect.STUB_DETECTORS: skipped.append(name); continue` [:92-95]; cada detector en `try/except Exception` que registra `errors[name]` y `per[name]={"flagged":-1,...}` y **nunca aborta** la cadencia [:105-108] ("never let one detector abort the cadence").
- [VERIFIED run.py:98] rutea con `route_anomalies(conn, anomalies, actor=f"gestionador:{name}")`.
- [VERIFIED run.py:39,83-85] session-tuning: `work_mem=384MB` (`CARDEEP_GESTIONADOR_WORK_MEM`) + `enable_mergejoin=off` + `enable_nestloop=off` via `set_config(...,false)` (scope sesion, esta conn) para que el scan de cohorte (1.66M ln-prices) no derrame a disco.

#### (b) Mecanismo al atomo
Un registry unico consumido por DOS caminos: `dry_run_all` (diagnostico, sin writes, corre los 9) y `run.run_all` (vivo, rutea flags, **salta** los 2 STUB para no loguear falsa cobertura "ran, 0 found"). El contrato del arnes es triple: (1) **never-raises** -> aislamiento por-detector con flagged=-1; (2) **QUARANTINE-only / EUR0** -> solo DB reads + gestion_item upserts, jamas NULL/DELETE; (3) **registry-driven** -> anadir un detector es una fila en la tupla, su STUB-ness una entrada en el frozenset.

#### (c) Costura ES->generico + fix exacto
El arnes en si es **estructuralmente agnostico**: itera la registry y salta STUB sin un solo literal de pais. La costura NO esta en run_all sino en lo que ejecuta: los 7 detectores live cargan constantes ES/EUR (facetas 4/5/8/9). Por eso run_all es **country-BLIND, no country-CORRECT**: un detector que "corre bien" (no lanza excepcion) pero **mide mal** con constantes espanolas rutea falsos positivos a cuarentena y el aislamiento por-detector **no lo nota** (medir mal no lanza excepcion). **Fix:** (1) run_all queda byte-identico; (2) la country-correctness la inyectan los detectores (otras facetas) MAS un fixture golden/Ferrari por-CC (faceta 33) que pruebe que run_all NO mass-quarantena; (3) la activacion de cada STUB se **gatea** tras existir su backing data (geo: tracking sentinel_placement_rate; classifier: golden_set por-CC) — nunca activar un slot que no puede entregar cobertura.

#### (d) Riesgo adversarial concreto (DE/FR/IT/PT/no-UE/ruido)
run_all aplica el MISMO codigo a todo pais. En MX/JP, fabrication/price_trap con techos EUR disparan masivamente -> todos `quarantines=TRUE` -> `servable_*` oculta el pais entero, y el aislamiento por-detector **loguea nada** (cero excepciones: el detector "corrio bien"). Los 2 STUB devuelven `[]` en silencio: geo_resolution_drift y classifier_drift NO detectan deriva en el mercado nuevo (justo donde la deriva es maxima). El modo de fallo es invisible hasta produccion porque CI usa golden ES.

#### (e) Sellado + verificacion multi-via
- **Sello:** (i) run_all sobre fixture Ferrari por-CC (faceta 33) -> `total_flagged` dentro de banda esperada, 0 mass-quarantine; (ii) los 2 STUB o devuelven anomalias reales sobre un fixture con deriva sembrada, o se declaran **explicitamente inertes** en el country manifest (honesto, no `[]` silencioso); (iii) test de aislamiento: inyectar un detector que lanza -> `flagged=-1`, los demas completan; (iv) contrato never-raises/QUARANTINE-only intacto.
- **Multi-via:** 1a = `dry_run_all` (9 detectores, sin writes) vs `run_all` (7 live, con writes) deben concordar en los 7 live; 2a = conteo de gestion_item abiertos por `actor='gestionador:<name>'` == flagged por detector; 3a adversarial = matar un detector a proposito y verificar continuidad de la cadencia.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**Evidently** (Apache-2.0, EUR0) — https://github.com/evidentlyai/evidently [VERIFIED NEXT-LEVEL.md:616-622, cluster ops-automation-llm]. Cierra el STUB `detect_classifier_drift`: corre un `DataDriftPreset` sobre (ventana_referencia vs ventana_actual) de features del clasificador de kind; cuando la distribucion de tipos-de-dealer se desplaza (mercado/portal nuevo) **emite un `CLASSIFICATION_DOUBT` decision_request** en vez de devolver `[]`. Convierte un slot inerte del registry en un detector vivo country-aware. **Complemento:** **river** (BSD-3-Clause, EUR0) — https://github.com/online-ml/river [VERIFIED NEXT-LEVEL.md:576-582] para cadencia auto-ajustable (ADWIN/Page-Hinkley sobre la tasa-de-cambio por fuente -> mueve harvest_interval_hours). Disciplina obligatoria: el emisor debe ser **opt-in/acotado** (heredar INQUISITION_EMIT) para no auto-DoSear el bus.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-4"></a>
### Faceta 4 · Moneda + contexto-pais de los hechos de vehiculo (substrato de particion)
*El substrato (currency, country_code) bajo todo hecho de precio antes de comparar.*  ·  **v1:** Clúster C

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — vehicle.currency existe pero nace muerta (DEFAULT 'EUR', leida solo por la API para passthrough, jamas por un detector) y vehicle NO tiene country_code (0052:36-38 lo difiere como YAGNI por el coste de 2.3M filas; 0053 nunca lo materializa). Por tanto fabrication compara price contra un techo EUR escalar [detect.py:541-573] y price_trap agrupa cohortes por (make,model,year) sin particion de pais/moneda [detect.py:773-815]: el motor asume mono-moneda EUR / mono-pais ES en todo el plano de precios.
- **Fix exacto** — Dos decisiones acopladas: (1) poblar vehicle.currency real en el borde via parse_money(price-parser+Babel CLDR) y anadir currency al contrato CanonicalVehicle; (2) denormalizar country_code en vehicle con migracion additiva 'ALTER TABLE vehicle ADD COLUMN country_code CHAR(2) NOT NULL DEFAULT ES' (espejo de 0052:51-54, backfill implicito ES, one-shot 2.3M) en vez de un JOIN por-fila a entity por pasada; luego anadir country_code,currency al GROUP BY de price_trap y a la block-key de Signal-B (misma cohorte=misma moneda, aserto duro). ES byte-identico con currency='EUR'/country_code='ES' por default.
- **Riesgo adversarial** — No-UE es el break critico: FAB_PRICE_CEIL=5_000_000 EUR marca como fabricacion casi todo el inventario MXN (5M MXN~230k EUR) y deja pasar fraude JPY (5M JPY~30k EUR) => apagon de pais. Coexistencia DE/FR/IT: una cohorte multimoneda vuelve el MAD de ln(price) multimodal -> cero deteccion (outliers enmascarados) o cuarentena masiva de stock legitimo, y como price_trap dispara quarantines=TRUE oculta inventario del pais via servable_vehicle. Ruido: corrupcion 1000x (MX '1,234.56'->1.23456) parsea a float valido y pasa sanity. Coste: JOIN por-fila a entity sobre 2.3M por pasada degrada la cadencia €0 si no se denormaliza.
- **Sellado multi-vía** — Sellado = ningun precio entra a comparador sin (currency,country_code) resueltos, ninguna cohorte mezcla dos monedas, techo por-moneda, ES byte-identico. Multi-via: (1) golden de parse_money por locale + corpus ES sin drift; (2) invariante estructural 'ninguna cohorte/bloque Signal-B con 2 currency' (colision GBP/EUR imposible); (3) cross-source texto-visible vs priceCurrency JSON-LD (discrepancia=REFUTED); (4) Hypothesis adversarial 'parse_money idempotente nunca off-by-1000' + 'JPY normal sobrevive bajo techo JPY, EUR-junk sigue rechazado'.
- **Herramienta NEXT-LEVEL** — price-parser (BSD-3-Clause, €0) https://github.com/scrapinghub/price-parser [VERIFIED NEXT-LEVEL.md:503-509,:216] + Babel (CLDR, formatos por locale) + py-moneyed (Money tipado) + pycountry (LGPL-2.1, ISO 4217, set de divisas y PRICE_MAX por-moneda) [VERIFIED NEXT-LEVEL.md:530]. CPU puro, offline (CLDR embebido), intra-moneda por construccion (sin servicio FX). Eleva moneda de 'columna muerta+techo EUR soldado' a 'cada precio auto-describe su divisa y solo se compara contra su misma divisa'.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) Verificacion de code_hints [VERIFIED]
- **[VERIFIED migrations/0003_vehicles_events.sql:14]** `currency CHAR(3) NOT NULL DEFAULT 'EUR'` en `vehicle`. La columna EXISTE y nace muerta: ninguna logica de comparacion la lee.
- **[VERIFIED migrations/0052_country.sql:36-38]** decision de esquema explicita: *"(d) country_code on vehicle (2,311,202 rows) — vehicle.country is derivable via vehicle.entity_ulid -> entity.country_code, so FASE-0 keeps the geo backbone + entity as the single source of the country dimension (YAGNI; avoids a 2.3M-row rewrite)."* => `vehicle` NO lleva `country_code`; el pais de un vehiculo solo se obtiene por JOIN a `entity`.
- **[VERIFIED migrations/0053_country_onboarding.sql]** promueve el PK geo a `(country_code, code)` y reescribe 6 FKs, pero **sigue sin** anadir `country_code` a `vehicle` (item (d) de 0052 nunca se materializa). El substrato de particion por-vehiculo no existe en ningun punto del esquema.
- **[VERIFIED pipeline/gestionador/detect.py:70]** `FAB_PRICE_CEIL = 5_000_000` — techo absoluto en EUR implicito (constante de modulo, sin dimension moneda).
- **[VERIFIED pipeline/gestionador/detect.py:541-573]** `detect_fabrication` out-of-band: `WHERE ... v.price > $1` con `$1 = FAB_PRICE_CEIL`. El `JOIN entity e` (550, 563) trae SOLO `e.cdp_code`, **no** currency ni country. El precio se compara como escalar desnudo contra un techo EUR.
- **[VERIFIED pipeline/gestionador/detect.py:773-815]** `detect_price_trap`: CTE `base` (774-780) selecciona `price::float8`, `ln(price)`, `make,model,year` FROM `vehicle` sin filtro de pais ni columna currency; `GROUP BY make,model,year` (786). El JOIN a `entity` (826-834) ocurre **solo** para resolver `kind` de las filas ya marcadas — **nunca** para particionar por pais/moneda.
- **Matiz de honestidad sobre "NUNCA leida":** **[VERIFIED]** `services/api/routers/vehicles.py:87`, `platforms.py:54`, `entities.py:132` SELECCIONAN `v.currency` para **servirla** en la respuesta API (passthrough de display). El grep `\bcurrency\b` en `pipeline/` solo aparece en field-maps/fragmentos GraphQL de `pipeline/platform/*.py` (p.ej. `coches_com_wholesale.py:880`, `oem_ford_wholesale.py:559`) — prosa de receta, **no** logica de deteccion. Conclusion precisa: **ningun detector ni comparador consume `vehicle.currency`**; se echa a la respuesta pero jamas dirige una decision. La afirmacion del diseno "ningun detector lee currency" es [VERIFIED]; "currency NUNCA leida" es matizable (la sirve la API).

#### (b) El mecanismo al atomo
Cada fila de `vehicle` tiene un precio en una unidad monetaria implicitamente asumida EUR. Dos motores de deteccion comparan ese escalar:
1. **Techo absoluto** (`fabrication`): `price > 5_000_000` => fabricacion. Es una comparacion dimensional EUR contra un numero EUR.
2. **Cohorte robust-z** (`price_trap`): agrupa por `(make,model,year)`, calcula mediana y MAD sobre `ln(price)`, y marca outliers `|z|>=6`. La validez estadistica del MAD exige que **todos los precios de la cohorte esten en la misma moneda**; si no, `ln(price)` mezcla escalas y la distribucion se vuelve multimodal.
El substrato que falta es: *antes de cualquier comparacion, todo hecho de precio debe portar (moneda, pais)*. Hoy el pais solo se deriva por `vehicle.entity_ulid -> entity.country_code` (JOIN), y la moneda esta en una columna muerta.

#### (c) La costura ES->generico con su fix exacto
**Costura:** el motor asume una sola moneda (EUR) y un solo pais (ES) en todo el plano de precios. Para multi-pais hay que (1) poblar `vehicle.currency` de forma fiable en el borde de ingesta, y (2) dar a cada fila su pais sin un JOIN por-fila a `entity` sobre 2.3M filas en cada pasada.

**Fix exacto (dos decisiones acopladas):**
- **Poblado de moneda en el borde:** enrutar TODO parseo de precio por un `parse_money(text, LocaleProfile) -> (amount, currency)` con `price-parser` (extrae monto+divisa in-band) respaldado por datos CLDR de `Babel`, y escribir `vehicle.currency` real en ingesta (hoy queda 'EUR' por default). Anadir `currency` al contrato `CanonicalVehicle` (hoy `price` es float pelado).
- **Particion del hecho:** o (A) **denormalizar `country_code` en `vehicle`** (migracion additiva `ALTER TABLE vehicle ADD COLUMN country_code CHAR(2) NOT NULL DEFAULT 'ES'`, espejo exacto del patron 0052:51-54 — backfill implicito ES, 2.3M filas pero one-shot), o (B) **CTE de pais** que JOIN `entity` una sola vez por pasada y materialice `(vehicle_ulid, country_code, currency)` antes del scan de cohorte. La decision A es la correcta para el coste de query recurrente: un `country_code` indexado en `vehicle` evita un JOIN a 2.3M filas por cada corrida de `price_trap`/`fabrication`. El umbral por-moneda lo aporta la faceta 5 (pack); ESTA faceta entrega el substrato que ese umbral consume.
- **Particion de cohorte:** anadir `country_code, currency` al `GROUP BY` de `price_trap` (faceta 6 consume), y `currency` a la key del bloque Signal-B (misma cohorte = misma moneda, aserto duro pre-comparacion).
ES queda byte-identico: `currency='EUR'` y `country_code='ES'` por default reproducen el escalar EUR actual (golden de detector sin cambio).

#### (d) El riesgo adversarial concreto (DE/FR/IT/PT/no-UE/ruido)
- **No-UE (el break mas grave):** MXN 5.000.000 ~ 230k EUR; JPY 5.000.000 ~ 30k EUR. El techo `FAB_PRICE_CEIL=5_000_000` EUR marca como **fabricacion** casi todo el inventario premium europeo expresado en MXN y, peor, deja pasar fraude en JPY (donde 5M JPY es un coche barato). La moneda implicita EUR convierte el sellado en **apagon de pais** para MX/JP.
- **Cohorte multimoneda (DE/FR/IT coexistiendo):** una cohorte 'Toyota Corolla 2020' que mezcle EUR+otra moneda vuelve el MAD de `ln(price)` multimodal => o **cero deteccion** (el MAD inflado enmascara outliers reales) o **cuarentena masiva** de stock normal. Como `price_trap` dispara `quarantines=TRUE`, una cohorte contaminada puede ocultar inventario legitimo del pais entero via `servable_vehicle`.
- **Ruido de corrupcion 1000x:** un precio MX '1,234.56' parseado con convencion EU (punto=miles) -> 1.23456, o un JPY swithout decimals mal escalado, produce un escalar valido que PASA sanity pero esta off-by-1000 — corrupcion silenciosa que ni `fabrication` (cae bajo techo) ni `price_trap` (un solo punto) atrapan.
- **Coste a escala:** un JOIN por-fila a `entity` sobre 2.3M vehiculos en cada pasada de detector (la alternativa B sin denormalizar) es un coste de plan no trivial que degrada la cadencia €0.

#### (e) Criterio de sellado + verificacion multi-via
**Sellado:** ningun hecho de precio entra a un comparador sin `(currency, country_code)` resueltos; ninguna cohorte mezcla dos monedas; el techo de fabricacion es por-moneda (consumido de faceta 5); ES reproduce byte-identico el escalar EUR.
**Multi-via:**
1. **Via determinista (golden):** `parse_money('MX 1,234.56')==1234.56`, `parse_money('ES 1.234,56')==1234.56`, `parse_money('FR 1 234,56')==1234.56`, `parse_money('JP ¥1,234,000')==1234000` con `currency` capturada; y el corpus ES de cdp/price reproduce el escalar EUR actual sin drift.
2. **Via invariante estructural:** test que asevera que **ningun bloque Signal-B / ninguna cohorte de `price_trap` contiene dos `currency` distintas** — una colision GBP/EUR a +/-2% se vuelve estructuralmente imposible.
3. **Via independiente (cross-source):** el monto parseado del texto visible se cruza contra el `priceCurrency`/`price` del JSON-LD (metadato schema.org, eje ortogonal); discrepancia => REFUTED, no se sella.
4. **Via adversarial (Hypothesis):** generar separadores mixtos/ambiguos y precios JPY/MXN sobre el techo EUR; afirmar 'parse_money idempotente, nunca off-by-1000' y 'un JPY normal sobrevive bajo su techo JPY mientras EUR-junk sigue rechazado'.

#### (f) Herramienta NEXT-LEVEL que la eleva a nivel inalcanzable
**price-parser** (BSD-3-Clause, €0) — https://github.com/scrapinghub/price-parser — extrae monto+divisa de texto crudo manejando separadores de miles/decimal por locale; respaldado por **Babel** (CLDR, formatos number/currency por pais) y **py-moneyed** (Money tipado para aritmetica segura), con **pycountry** (LGPL-2.1, ISO 4217) como autoridad del set de divisas y del `PRICE_MAX` por-moneda en el manifest. [VERIFIED NEXT-LEVEL.md:503-509 "Currency-correct pricing: price-parser at the boundary" + :213-219 "locale-money-correctness" + :530 pycountry ISO 4217]. Las tres son CPU puro, offline (CLDR embebido en Babel), licencias permisivas; sin servicio FX porque las comparaciones son intra-moneda por construccion (currency en la block key). Eleva la dimension moneda de 'columna muerta + techo EUR soldado' a 'cada precio auto-describe su divisa y se compara solo contra su misma divisa', imposible de mantener a mano para N locales.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-5"></a>
### Faceta 5 · Pack de umbrales de detector de valor por-pais (fabrication/price_trap)
*Las magnitudes de mercado (5M/150k/300 EUR) de constante de módulo a country.toml tipado por-CC.*  ·  **v1:** Clúster C

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — Las magnitudes son constantes de modulo en detect.py [VERIFIED :69-75, :90-107]; el detector las lee del namespace del modulo. NINGUNA firma de detector recibe thresholds inyectados (detect_fabrication/detect_price_trap leen los globals directamente). No existe seam de consumo por-CC: el motor hoy no tiene punto de inyeccion. ES quedaria byte-identico declarando 5_000_000/1_000_000/150_000/0.25/300 en su manifest.
- **Fix exacto** — Definir un `CountryPack(BaseModel)` Pydantic con campos tipados `fab_price_ceil`, `fab_km_ceil`, `fab_year_ceil`, `price_trap_high_abs_floor`, `price_trap_low_median_frac`, `price_trap_floor_by_kind`, `price_trap_cohort_z`, etc.; el loader cacheado por-CC (faceta 29) lo materializa de countries/<CC>/country.toml; cada detector pasa de leer constantes a recibir el pack inyectado en su firma (detect_fabrication(conn, pack)). ES declara sus literales actuales en countries/ES/country.toml de modo que el golden no cambie. Validacion fail-fast: Pydantic rechaza ceil<floor, tipos mal o campos ausentes al arranque.
- **Riesgo adversarial** — Aunque faceta 4 normalice moneda, los NIVELES difieren por estructura fiscal/mercado. FAB_PRICE_CEIL=5M EUR calibrado a ES deja pasar fraude en un mercado mas barato (PT) o cuarentena stock legitimo en uno mas caro. PRICE_TRAP_HIGH_ABS_FLOOR=150k EUR: un Ferrari/Lamborghini legitimo en DE/IT supera 150k y, si ademas cae como outlier de cohorte, se marca HIGH falsamente; en PT/MX el piso 150k EUR casi nunca se alcanza, cegando el detector HIGH. PRICE_TRAP_FLOOR=300 (deposito/placeholder) en JPY/MXN no corresponde a ninguna senal real. Sin el pack, el primer pais no-ES detona en produccion con numeros espanoles -> mass-quarantine via servable_* (acopla faceta 2/33).
- **Sellado multi-vía** — Multi-via: (1) GOLDEN ES — el pack ES produce flag-set byte-identico al hardcode actual sobre el fixture Ferrari ES (cero regresion, test_country_golden). (2) FAIL-CLOSED Pydantic — un country.toml sin un umbral obligatorio => CI ROJO, jamas fallback silencioso al literal ES. (3) 2a VIA — el guard de drift cuenta 'umbrales-sin-declarar == 0' por-CC y cruza contra un grep de literales de magnitud en detect.py (debe quedar 0 tras la extraccion). (4) FERRARI por-CC (faceta 33) ejercita los umbrales del pack DE contra datos DE y prueba flag-rate acotado (no mass-fire).
- **Herramienta NEXT-LEVEL** — Pydantic (MIT, EUR0) https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587,:71] — CountryPack(BaseModel) con validators de coherencia (ceil>floor, rangos) y fail-fast en CI sin DB viva; convierte el pack de umbrales en CONTRATO TIPADO. Alt: Frictionless (MIT, :337), jsonschema.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### Mecanismo al atomo
Las magnitudes de mercado viven como CONSTANTES DE MODULO, no inyectadas. La ironia esta sellada en el propio codigo: el docstring promete '`All thresholds are module-level constants (never magic numbers in logic)`' [VERIFIED detect.py:20] y el bloque se rotula '`V4 §3 — "thresholds live in config, not code"`' [VERIFIED detect.py:31] — pero NO hay config: son literales Python.

- **fabrication** [VERIFIED detect.py:69-75]: `FAB_PRICE_FLOOR=0`, `FAB_PRICE_CEIL=5_000_000`, `FAB_YEAR_FLOOR=1900`, `FAB_YEAR_CEIL=2027`, `FAB_KM_CEIL=1_000_000`, `FAB_COLLAPSE_KAPPA=1.10`, `FAB_CV_DEGENERATE=0.01`. `detect_fabrication` compara el `price` escalar contra `FAB_PRICE_CEIL=5M` en EUR implicito.
- **price_trap** [VERIFIED detect.py:90-107]: `PRICE_TRAP_FLOOR` dict por kind (todos `300.0`), `PRICE_TRAP_COHORT_Z=6.0`, `MIN_A=15`, `MIN_B=30`, `PRICE_TRAP_MAD_FLOOR=0.05`, `PRICE_TRAP_HIGH_ABS_FLOOR=150_000.0`, `PRICE_TRAP_LOW_MEDIAN_FRAC=0.25`, `PRICE_TRAP_MAX_ROWS=5000`. La Law-I co-guard exige que un flag HIGH cumpla `price >= 150_000 EUR` Y `|z| >= 6`; un flag LOW exige `price < 0.25 * mediana_cohorte`.

**Separacion deliberada vs faceta 4:** la faceta 4 es el MECANISMO (resolver moneda/pais antes de comparar); esta faceta 5 es la MAGNITUD (el numero). Aunque la moneda se normalice, el NIVEL absoluto (5M, 150k, 300) sigue siendo estructura de mercado espanola. Ningun umbral de magnitud puede quedar como literal de modulo tras el onboarding.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-6"></a>
### Faceta 6 · Particion de cohorte de price_trap (cohortes country/currency-correctas)
*La cohorte country/currency-correcta: (country_code, currency) en el GROUP BY, comparación intra-moneda.*  ·  **v1:** Clúster D

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — La clave de cohorte es `(make, model, year)` / `(make, year)` — le falta la dimension `(country_code, currency)`. `vehicle.currency` EXISTE pero esta muerta (nunca se SELECTa); `vehicle.country_code` no existe en absoluto, solo en `entity` (via 0052). La particion correcta exige (a) denormalizar country_code en vehicle (~2.3M filas, coste de migracion) O (b) un JOIN `vehicle->entity` DENTRO de las CTE de cohorte que el SQL actual nunca hace. Con un corpus mono-pais, anadir `currency, country_code` al GROUP BY donde toda fila es ('EUR','ES') produce cohortes identicas -> golden ES byte-identico.
- **Fix exacto** — Anadir `currency` y el `country_code` resuelto (via JOIN a entity, o vehicle.country_code denormalizado) a AMBOS el `GROUP BY` de `med` y las claves de join de `mad`/`scored`, de modo que la cohorte sea `(country_code, currency, make, model, year)`. Comparacion intra-moneda por construccion (cero FX). Las co-guardas ratio (LOW_MEDIAN_FRAC) son currency-free; `HIGH_ABS_FLOOR=150_000` es absoluto EUR y DEBE migrar al pack por-CC (faceta 5), declarando ES su 150k en su .toml para salida byte-identica. Poblar `vehicle.currency` de forma fiable en ingesta con price-parser (parser de frontera) para que la clave de particion sea de confianza, no el DEFAULT 'EUR' muerto.
- **Riesgo adversarial** — En cuanto coexisten 2 paises la cohorte se contamina. Una cohorte 'Toyota Corolla 2020' que mezcla EUR (~18k), MXN (~360k numerico) y JPY (~3.000.000 numerico) vuelve ln(price) MULTIMODAL: la MAD se infla -> el robust-z colapsa hacia 0 -> el detector se CIEGA (fraude real con |z|<6 pasa) O, en la cola, un precio JPY legitimo lee |z|>6 contra una mediana EUR-dominante -> cuarentena masiva de stock normal. Como vehicle no tiene country_code (nota 0052), la particion correcta fuerza un JOIN a entity que reescribe el plan sobre ~1.66M filas. PT/colas finas: una cohorte por-moneda puede caer bajo MIN_A=15/MIN_B=30 -> no se forma cohorte -> deteccion cero silenciosa. No-UE es lo peor: la co-guarda `HIGH_ABS_FLOOR=150_000` EUR aplicada a JPY marca casi todo coche (un ¥3M normal > 150000 numerico) -> si quarantines=TRUE, el inventario premium/entero del pais se oculta.
- **Sellado multi-vía** — Multi-via: (1) Golden byte-identidad: re-correr detect_price_trap sobre el corpus ES con la query particionada donde toda fila es ('ES','EUR') -> set de flags identico al de hoy (patron test_country_golden). (2) Invariante de block-key: aseverar que ninguna cohorte mezcla 2 monedas (colision robust-z MXN/EUR estructuralmente imposible). (3) Test de techo por-moneda: un coche JPY normal bajo el abs-floor JPY sobrevive (sin flag) mientras la basura EUR sigue marcada — fixture por CC. (4) Fixture adversarial multimodal: inyectar una cohorte sintetica con 2 clusters de moneda y aseverar que el detector particionado recupera la MAD por-cluster (des-cegado) donde el pooled es ciego. (5) Piso de potencia: una cohorte bajo el MIN emite una nota 'cohort_too_thin', nunca un skip silencioso disfrazado de 'limpio'.
- **Herramienta NEXT-LEVEL** — price-parser (BSD-3-Clause) — https://github.com/scrapinghub/price-parser [VERIFIED NEXT-LEVEL.md:503-509, seccion 'Currency-correct pricing: price-parser at the boundary + Babel/py-moneyed for per-currency ceilings'; licencia tambien en tabla resumen :61]. Extrae monto+moneda de strings crudos en ingesta para poblar vehicle.currency de forma fiable; Babel (CLDR, bundled offline) resuelve el manejo decimal/miles por locale; py-moneyed da aritmetica currency-safe y un PRICE_MAX por-moneda en el CountryProfile. Meter currency en la clave de cohorte/bloque hace la comparacion cross-moneda estructuralmente imposible, sin servicio FX. EUR0, Python puro, offline.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) code_hints VERIFICADOS
- [VERIFIED detect.py:755] `async def detect_price_trap(conn)` — "Model-aware cohort price-anomaly detector (two-sided robust-z on ln price)"; un solo paso de cohorte.
- [VERIFIED detect.py:773-815] SQL: `base` lee `FROM vehicle WHERE status='available' AND price IS NOT NULL AND price>0 AND make IS NOT NULL AND year IS NOT NULL`; `med` hace `GROUP BY make, model, year` con `HAVING count(*) >= CASE WHEN model IS NOT NULL THEN $1 ELSE $2 END`; `mad` calcula `percentile_cont(0.5) ... abs(b.lp - m.med_lp)` (MAD de ln-price) con join NULL-safe `COALESCE(model,'§§NULL§§')`; `scored` calcula `z=(lp-med_lp)/(1.4826*mad_lp)`. NINGUNA columna `country_code` ni `currency` aparece en la query.
- [VERIFIED detect.py:775] `price::float8 AS price, ln(price::float8) AS lp` — el precio entra como ESCALAR DESNUDO, sin moneda.
- [VERIFIED detect.py:101-107] `PRICE_TRAP_COHORT_Z=6.0`, `MIN_A=15`, `MIN_B=30`, `MAD_FLOOR=0.05`, `HIGH_ABS_FLOOR=150_000.0`, `LOW_MEDIAN_FRAC=0.25`, `MAX_ROWS=5000`.
- [VERIFIED migrations/0003_vehicles_events.sql:14] `currency CHAR(3) NOT NULL DEFAULT 'EUR'` — la columna EXISTE pero la query NUNCA la SELECTa (columna muerta).
- [VERIFIED grep country_code migrations/ = solo 0052/0053] `vehicle` NO tiene `country_code`; solo `entity`/`geo` lo recibieron (0052). Particionar por pais EXIGE un JOIN vehicle->entity que el SQL hoy NO hace.

#### (b) Mecanismo al atomo
El detector forma UNA cohorte por `(make, model, year)` [Tier-A, dispara a n>=15] o `(make, year)` [Tier-B model-NULL, n>=30]. Dentro de la cohorte calcula la mediana y la MAD de ln(price) y marca una fila cuando `|robust-z| >= 6` con co-guardas Law I (HIGH ademas exige price>=150k; LOW ademas exige price<0.25*mediana). Usa MAD (no stddev) justo para que un unico outlier basura (9M EUR) no infle la escala (~50% breakdown). La cohorte ES la poblacion estadistica: TODAS las filas de ese (make,model,year) de la tabla `vehicle` entera se agrupan juntas. Como hoy la tabla es 100% ES/EUR, la cohorte es implicitamente mono-moneda y mono-mercado, y la mediana/MAD son unimodales y con sentido.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-7"></a>
### Faceta 7 · Pooling cross-pais de field_loss + staleness (baseline/TTL)
*Baseline/TTL country-blind ≠ country-correct: partición del estimador field_loss/staleness por-CC.*  ·  **v1:** Clúster D

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — field_loss y staleness son COUNTRY-BLIND por construccion: el baseline de null-rate (detect.py:342-350) no tiene `WHERE country_code=` y el `recent_sql` agrupa solo por `source_key` (:370); `STALENESS_TTL` (detect.py:51-63) es un dict de modulo keyado por kind sin seam por-CC. blind != correct: un solo `p0`/TTL para N paises es un estimador contaminado, no un estimador agnostico.
- **Fix exacto** — 1) field_loss: particionar el baseline por pais — `baseline_sql` pasa a `FROM vehicle v JOIN entity e ON e.entity_ulid=v.entity_ulid WHERE v.status='available' AND e.country_code=$1` (o `GROUP BY e.country_code`), un `p0` por CC; el `recent_sql` ya JOINea `entity_source`, anadir `JOIN entity e` y llevar `e.country_code` al GROUP BY, z-test de cada fuente contra el `p0` de SU pais. `entity.country_code` EXISTE [VERIFIED test_country_coexistence.py:280-284 + 0053]. 2) staleness: `STALENESS_TTL` inyectable por-CC desde country.toml (faceta 29), ES byte-identico declarado en su manifest; el `.get(kind, default)` se mantiene pero el dict viene del pack cargado, no de la constante. 3) ES byte-identico: con solo ES el pool por-CC == el pool global de hoy; lo fija el golden de detector por-pais (faceta 33).
- **Riesgo adversarial** — DE omite km en coches nuevos -> baseline pooled ES+DE da falso field_loss en DE o enmascara perdida real en ES; price->quarantines=True convierte el falso positivo en cuarentena de inventario extranjero (apagon via servable_*). STALENESS_TTL espanol (3d compraventa) aplica rotacion iberica a mercados de dinamica distinta -> falso staleness sistematico (ratio>3->quarantines) o ghosts; STORM_THRESHOLD=200 vuelve permanente el colapso source-level en mercados grandes y borra la senal por-entidad. El z-test sobre p0 multi-pais es estadisticamente invalido (poblaciones heterogeneas).
- **Sellado multi-vía** — SEALED exige: (a) `baseline_sql` con `WHERE e.country_code=$CC` y `n0 == count(available de ese CC)` (verificado por EXPLAIN + assert de conteo); (b) `STALENESS_TTL` cargado de country.toml, dict ES byte-identico al modulo (golden); (c) Ferrari/golden de detector por-CC (faceta 33) probando que field_loss/staleness NO disparan masivamente sobre datos del pais nuevo; (d) 2a-via: recompute SQL independiente de `p0`/ratios fuera del detector concuerda con el baseline del detector dentro de tolerancia float; (e) validez del z-test: `n0` por pais >= muestra minima. Multi-via: golden CI + shadow-run vivo en el pais nuevo (conteo de fires < umbral) + recompute SQL independiente.
- **Herramienta NEXT-LEVEL** — PRIMARIA: Evidently (Apache-2.0, EUR0) — https://github.com/evidentlyai/evidently [VERIFIED NEXT-LEVEL.md:619, tabla:75]. field_loss ES un detector de null-rate-drift hecho a mano con UN baseline pooled; Evidently computa drift por-segmento (share-of-nulls / missing-values) con PSI/Jensen-Shannon/Wasserstein/chi2 contra una ventana de REFERENCIA — reemplaza el z-test pooled por drift reference-vs-current per-country estadisticamente correcto sobre poblaciones heterogeneas, y emite un decision_request en vez de cuarentenar en masa. NOTA HONESTA: NEXT-LEVEL indexa Evidently nominalmente bajo el STUB classifier_drift (:616), pero la misma maquinaria DataDriftPreset(reference vs current) aplica 1:1 al baseline de null-rate de field_loss. SECUNDARIA: river (BSD-3-Clause, EUR0) — https://github.com/online-ml/river [VERIFIED:579, tabla:70]: detectores de cambio ONLINE (ADWIN/Page-Hinkley) para hacer STALENESS_TTL self-tuning por fuente/CC desde el stream de delta observado en vez de una constante iberica estatica (NEXT-LEVEL:576-582). Ambas EUR0/CPU.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) Verificacion de code_hints [VERIFIED]
- `detect.py:44-48` [VERIFIED]: `FIELD_LOSS_Z_CRIT=3.0`, `FIELD_LOSS_ABS_FLOOR=0.05`, `FIELD_LOSS_HARD_THRESH=0.30`, `FIELD_LOSS_PHOTO_THRESH=0.10` — constantes de modulo, sin dimension de pais.
- `detect.py:51-63` [VERIFIED]: `STALENESS_TTL` dict por kind (compraventa/concesionario_oficial 3d, plataforma 1d, garaje 7d, desguace 30d, particular 7d, rent_a_car_vo 7d, subasta 3d, importador 7d, oem_vo_portal 3d, `_entity` 90d). `:64-66` `STALENESS_RATIO_WARN=1.0`, `STALENESS_RATIO_CRIT=3.0`, `STALENESS_STORM_THRESHOLD=200`.
- `detect_field_loss` [VERIFIED `detect.py:333-434`]: el `baseline_sql` (`:342-350`) es `FROM vehicle WHERE status='available'` — **CERO filtro de pais**; `n0` (`:352`) es el total GLOBAL. El `recent_sql` (`:358-372`) hace `JOIN entity_source es` y `GROUP BY es.source_key` — agrupa por fuente, **no por pais**. El z-test es `_z_two_prop(x0_global, n0, x1, n1)` (`:393`) contra el `p0` global.
- `detect_staleness` [VERIFIED `detect.py:441-523`]: el `sql` (`:447-456`) es `FROM entity e WHERE e.last_seen IS NOT NULL AND e.status='active'` — **CERO filtro de pais**; `ttl = STALENESS_TTL.get(kind, STALENESS_TTL["garaje"])` (`:466`) lee la constante de modulo. Storm suppression `> STALENESS_STORM_THRESHOLD` colapsa a un item `ESCALATE_GASTO` source-level (`:483-500`).

#### (b) Mecanismo al atomo
**field_loss** computa UN baseline GLOBAL `p0 = x0_global/n0` sobre TODOS los `vehicle status='available'` (sin split de pais). Para cada `(source_key, field)` de los ultimos 7 dias calcula `p1` y un z-test de dos proporciones contra ese `p0` agregado. Dispara si `z>3.0 AND abs_delta>=0.05` (o `hard_fire`: price con `p1>0.30`). `price`->critical+`quarantines=True`+RESEARCH; `year`/`km`->warning; `photo_url`->info+AUTO_FIX (con piso abs 0.10).
**staleness**: por cada entidad activa con `last_seen`, `ratio = age/STALENESS_TTL[kind]`; dispara si `ratio>1.0`; `ratio>3.0`->critical+`quarantines=True`. La storm suppression colapsa >200 stale de un mismo kind en un solo item de fuente.

#### (c) Costura ES->generico
Ambos detectores **agregan TODOS los paises en un unico estimador**. El `p0` de field_loss no lleva `WHERE country_code=`; las tasas recientes agrupan solo por `source_key`. `STALENESS_TTL` es un dict de modulo keyado solo por kind, sin override por-CC. Anadir un 2o pais **contamina el `p0`** (mezcla estructuras de null ES/DE) y **aplica cadencias de rotacion ibericas** a mercados ajenos.

#### (d) Riesgo adversarial concreto
- **DE** omite legitimamente `km` en coches nuevos -> un `p0` agrupado ES+DE o (i) dispara falso field_loss en DE (la null-rate de `km` sube contra un `p0` ES-pesado) o (ii) el volumen DE arrastra `p0` arriba y **enmascara** perdida real de `km` en ES. Como `price`->`quarantines=True`, un falso field_loss **cuarentena inventario extranjero real** -> `servable_*` lo oculta (faceta 2).
- **TTL**: 3d de compraventa es rotacion iberica; un mercado de stock mas lento (o un portal que refresca `last_seen` distinto) produce **falso staleness sistematico** -> `ratio>3` -> `quarantines=True` -> apagon; un mercado mas rapido produce ghosts que nunca disparan. `STORM_THRESHOLD=200` colapsa a un `ESCALATE_GASTO`: para un mercado grande el storm es permanente y **borra la senal por-entidad**.
- **no-UE/ruido**: un mercado con fotos estructuralmente escasas envenena el baseline de `photo_url`; el z-test sobre un `p0` multi-pais es **estadisticamente invalido** (poblaciones heterogeneas).

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-8"></a>
### Faceta 8 · Anclas ground-truth de coverage_gap por-pais
*El piso de inventario por kind: censo institucional ES → ancla por-CC.*  ·  **v1:** Clúster E

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — COVERAGE_ANCHORS [detect.py:78-83] es un dict de modulo con el censo institucional ESPANOL (DGT 1292 / FACONAUTO 2018 / Paginas Amarillas 1662 y 29955). detect_coverage_gap lo consume directo. grep CDP-ES=0 NO prueba agnosticismo: son magic numbers ES sin el substring.
- **Fix exacto** — Mover anclas a country.toml [coverage_anchors] por kind; detect_coverage_gap recibe el dict inyectado del loader (faceta 29). ES declara 1292/2018/1662/29955 en su manifest -> salida byte-identica. RELGAP_INFO/WARN como default-con-override por-CC.
- **Riesgo adversarial** — DE con anclas ES compara el conteo aleman de desguaces contra 1292 desguaces espanoles -> critical sin sentido o info que silencia gaps reales. El sellado (faceta 28) hereda denominadores falsos. Un kind ausente/renombrado cae a covered.get(kind,0)=0 -> gap=ancla completa -> critical perpetuo.
- **Sellado multi-vía** — Via1 golden per-CC: ES.toml reproduce 1292/2018/1662/29955. Via2 Ferrari por-CC (faceta 33): coverage_gap con anclas DE contra datos DE-shaped no dispara critical espureo (reemplaza grep CDP-ES=0 por evidencia ejecutable). Via3 triangulacion: cada ancla en banda 0.7-1.4 vs censo externo (faceta 21); desacuerdo = distrust. Via4: ES byte-identity.
- **Herramienta NEXT-LEVEL** — Eurostat SBS (NACE G45) — Reutilizacion libre Decision 2011/833/EU — https://ec.europa.eu/eurostat/web/structural-business-statistics [VERIFIED NEXT-LEVEL.md:191]: conteo de establecimientos por pais auto-minado como panel de anclas (NEXT-LEVEL.md:188). Alternativa dia-uno: GLEIF LEI Golden Copy — CC0 1.0 — https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy [VERIFIED NEXT-LEVEL.md:175]. Ambas reemplazan instituciones ES por denominador per-CC verificable. €0.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) code_hints VERIFICADOS
- **COVERAGE_ANCHORS** [VERIFIED pipeline/gestionador/detect.py:78-83] dict de pisos por kind con **instituciones ESPANOLAS hardcodeadas**: `desguace: 1_292` (comentario "DGT official CAT registry (exact)"), `concesionario_oficial: 2_018` ("FACONAUTO franchised"), `compraventa: 1_662` ("Paginas Amarillas floor"), `garaje: 29_955` ("Paginas Amarillas").
- **Umbrales relgap** [VERIFIED detect.py:84-85] `COVERAGE_RELGAP_INFO = 0.10`, `COVERAGE_RELGAP_WARN = 0.40`.
- **Consumidor** [VERIFIED detect.py:699-748] `detect_coverage_gap`: cuenta entidades activas por kind (`SELECT kind, count(*) FROM entity WHERE status='active' GROUP BY kind`); para cada `(kind, anchor)` calcula `gap = max(0, anchor - c)`, `relgap = gap / max(anchor, 1)`; severidad: `c < anchor` -> **critical**, `relgap > WARN` -> warning, `relgap > INFO` -> info, else `continue`; `lane="RESEARCH"`, `quarantines=False` [VERIFIED detect.py:744, comentario "coverage_gap never quarantines (V4 §3.10)"], `dedupe_key=f"coverage_gap|{kind}|{bucket}"`.
- **Punto clave verificado:** 1292/2018/1662/29955 son **magic numbers de instituciones ES** sin el substring `CDP-ES`. Por tanto `grep CDP-ES = 0` **NO** prueba agnosticismo — la ausencia del literal no es agnosticismo.

#### (b) El mecanismo al atomo
El detector mide cobertura como **conteo vs piso conocido**: por cada kind con ancla, compara el `count(*)` de entidades activas contra el denominador nacional. Si esta por debajo del minimo conocido -> critical (estamos perdiendo puntos de venta que SABEMOS que existen). El `relgap` normaliza la brecha 0..1 para `score`. Es un detector RESEARCH (nunca cuarentena, nunca oculta): su salida es una senal de "falta inventario", no un kill-switch. Distinto del **censo de triangulacion del sellador** (faceta 21): aqui es el piso del DETECTOR, no el denominador externo del intervalo MSE.

#### (c) Costura ES->generico + fix exacto
La costura es **el dict entero**: `COVERAGE_ANCHORS` codifica el censo institucional espanol (DGT/FACONAUTO/Paginas Amarillas). Para DE las anclas son KBA + ZDK + Gelbe Seiten; FR/IT/PT/MX/JP sus registros nacionales.
**Fix:** mover las anclas a `country.toml` como `[coverage_anchors]` por kind; `detect_coverage_gap` recibe el dict inyectado desde el loader (faceta 29) en vez de leer la constante de modulo. ES declara `desguace=1292, concesionario_oficial=2018, compraventa=1662, garaje=29955` en su manifest -> salida byte-identica. Los umbrales `RELGAP_INFO/WARN` pueden quedar como default-con-override por-CC (estructura de mercado distinta).

#### (d) Riesgo adversarial concreto
- **DE con anclas ES:** coverage_gap compara el conteo aleman de desguaces contra **1292 desguaces espanoles** -> basura: o severidad critical sin sentido (Alemania tiene ~muchos mas) o info que silencia un gap real del pais nuevo.
- **Falsos denominadores heredados:** el sellado de cobertura (faceta 28 mira gestion_item criticos) hereda gaps inexistentes -> un pais puede "no sellar" porque coverage_gap grita critical contra un piso ajeno.
- **Ruido transfronterizo:** un kind que no existe en el pais nuevo (o cuyo nombre canonico difiere) cae a `covered.get(kind, 0)` -> gap = ancla completa -> critical perpetuo.

#### (e) Criterio de sellado + verificacion multi-via
- **Via 1 (golden per-CC):** un golden de anclas por pais; cargar ES.toml reproduce 1292/2018/1662/29955 exactos.
- **Via 2 (Ferrari por-CC, faceta 33):** fixture que corre `detect_coverage_gap` con anclas DE contra datos DE-shaped y **asevera que no dispara critical espureo**; reemplaza el `grep CDP-ES=0` hueco por evidencia ejecutable.
- **Via 3 (triangulacion cruzada):** cada ancla aterriza el conteo nacional contra el censo externo (faceta 21) en banda 0.7-1.4 o se marca; el **desacuerdo entre anclas** aflora como senal de distrust, no se promedia en silencio.
- **Via 4 (ES byte-identity):** el detector ES no cambia su salida tras el refactor (mismo conjunto de gestion_item).

#### (f) Herramienta NEXT-LEVEL
**Eurostat Structural Business Statistics (SBS, NACE G45 venta/reparacion de vehiculos)** — Reutilizacion libre (Decision 2011/833/EU; atribucion), https://ec.europa.eu/eurostat/web/structural-business-statistics [VERIFIED NEXT-LEVEL.md:191]. Surte un **conteo de establecimientos por pais auto-minado** como ancla por-CC sin escribir un adaptador nacional. La biblia lo enmarca como "Panel de anclas de triangulacion MULTIPLES auto-minadas" [NEXT-LEVEL.md:188]: convertir UNA ancla en un PANEL de denominadores independientes por mecanismo legal/fiscal distinto, donde el desacuerdo es senal de distrust.
**Alternativa dia-uno:** **GLEIF LEI Golden Copy** — CC0 1.0 Universal (dominio publico, comercial OK sin atribucion), https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy [VERIFIED NEXT-LEVEL.md:175]: una espina registral CC0 global que da una pata de conteo a DE/FR/IT/PT/MX/JP el dia uno, refrescada a diario. Ambas reemplazan las instituciones ES hardcodeadas por un denominador per-CC verificable. €0, licencia limpia.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-9"></a>
### Faceta 9 · Fisica de paginacion de silent_cap por-portal/pais
*El tope silencioso por-portal: page_size + techos redondos inyectados por fuente.*  ·  **v1:** Clúster L

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — Las 4 constantes (detect.py:39-42: PAGE_SIZE=20, MAX_PAGES=50, MAX_ROWS=1000, ROUND_CEILINGS={500,1000,2000,5000}) son de modulo y derivan de portales ES (docstring ancla el 1000 a AutoScout24, :275-276). La fisica de paginacion es por-PORTAL: hay que declararla por fuente en el pack del pais e inyectarla a detect_silent_cap por source_key.
- **Fix exacto** — Reemplazar las 4 constantes por un lookup por source_key del country-pack (faceta 29): cap_hit pasa a `h >= phys.max_pages*phys.page_size`, ceiling_hit a `int(h) in phys.round_ceilings`. ES declara 20/50/{500,1000,2000,5000} en su manifest (byte-identico). Sin fisica declarada -> fail-closed conservador (no asumir los numeros ES).
- **Riesgo adversarial** — Con la fisica ES, el cap real de mobile.de (otra paginacion) no se detecta -> cap silencioso DE inadvertido -> sobre-confianza de cobertura -> triangulacion contra N truncado. lacentrale/goo-net (FR/JP) igual: falso negativo o falso positivo si 1000 es pagina legitima. Ruido: portal con 1000 resultados reales dispara cuarentena critica falsa que oculta una entidad sana.
- **Sellado multi-vía** — (1) Cada fuente activa declara su fisica; 0 = constante ES (gate falla). (2) Golden ES reproduce disparos byte-identicos con fisica inyectada. (3) Fixture por-portal con (d,h) sinteticos detecta cap/ceiling con numeros del portal real. (4) Property-based (Hypothesis): invariantes 'cap solo si h llega al techo del portal' y 'sin fisica => no false-fire ES', contraejemplo congelado a fixture.
- **Herramienta NEXT-LEVEL** — Hypothesis (MPL-2.0, EUR0) https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:317-323] — property-based-recipe-fuzzing: genera el caso de portal/locale raro que el golden ES no ve, minimiza al contraejemplo y lo congela como regression-fixture. La 2a-via adversarial que certifica country-CORRECTness, no solo country-blindness.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### Mecanismo al atomo [VERIFIED]
- **Constantes** (detect.py:39-42): `SILENT_CAP_MAX_PAGES = 50`, `SILENT_CAP_PAGE_SIZE = 20`, `SILENT_CAP_MAX_ROWS = SILENT_CAP_MAX_PAGES * SILENT_CAP_PAGE_SIZE` (= 1000), `SILENT_CAP_ROUND_CEILINGS = {500, 1000, 2000, 5000}`.
- **detect_silent_cap** (detect.py:272-326): lee la ultima verdict por entidad — `SELECT DISTINCT ON (subject_key) ... FROM verification_verdict WHERE subject_type='entity_inventory' ORDER BY subject_key, created_at DESC` (:280-288). Extrae `d = iv['source_declared']`, `h = iv['harvested']` (:297-298). Dispara si `cap_hit = (h >= SILENT_CAP_MAX_ROWS) and (d > h)` (:303) **O** `ceiling_hit = (int(h) in SILENT_CAP_ROUND_CEILINGS) and (d > h)` (:304). Emite severity='critical', `quarantines=True` (:315,322), lane='AUTO_FIX' si cap_hit else 'RESEARCH' (:321), `dedupe_key=f"silent_cap|{subject_key}|{bucket}"` (:323), subtipo 'page_budget_cap'|'provider_ceiling' (:310).
- El docstring (:275-276) ancla el 1000 a *"the AS24 max-pages*size ceiling"* (AutoScout24) — un numero derivado de un portal concreto. Los round ceilings {500,1000,2000,5000} son heuristica de la fisica de portales ES.

#### Mecanismo conceptual
El detector caza el "tope silencioso": un portal que corta a N resultados fingiendo que es TODO (declarado d > cosechado h, con h clavado en un techo redondo o en el budget de paginas). La senal depende enteramente del tamano de pagina y de los techos redondos del portal — cada portal nacional tiene su propia fisica.

#### Costura ES->generico
Las 4 constantes son de modulo (globales). mobile.de, lacentrale.fr, goo-net.com (JP) paginan con page_size y techos redondos DISTINTOS. La costura: declarar la fisica de paginacion POR FUENTE en el pack de fuentes del pais (countries/{CC}/_platforms o el seed de source, faceta 29) y que detect_silent_cap la reciba inyectada por source_key, no como constante global. ES mantiene 20/50/{500,1000,2000,5000} declarados en su manifest (byte-identico).

#### Riesgo adversarial concreto
Con page_size=20 y techos {500,1000,2000,5000} de portales espanoles: (DE) el cap real de mobile.de (que pagina con otro tamano/techo) NO se detecta -> cap silencioso aleman pasa inadvertido -> sobre-confianza en cobertura DE -> el sellador triangula contra un N truncado sin saberlo. (FR/IT/JP) lacentrale/goo-net con techos propios: falso negativo (cap no visto) o falso positivo si el portal usa 1000 como pagina legitima. Ruido: un portal que devuelve EXACTAMENTE 1000 resultados reales (no truncados) dispara una cuarentena critica falsa (quarantines=True) -> oculta una entidad sana. No-UE (JP) goo-net con multiplos distintos: el set ES es estructuralmente ciego.

#### Sellado + verificacion multi-via
1. **Cobertura del pack**: cada fuente activa del pais declara su fisica de paginacion; 0 fuentes con fisica = constante ES heredada -> el gate de sellado falla.
2. **Golden ES**: con la fisica inyectada, detect_silent_cap reproduce byte-identicos los disparos actuales (no regresion).
3. **Fixture por-portal**: (d,h) sinteticos prueban que cap/ceiling se detectan con los numeros del portal REAL (mobile.de), no los ES.
4. **Property-based (2a via adversarial)**: genera (d,h,page_size,max_pages,ceilings) adversariales y verifica invariantes 'cap_hit solo si h alcanza el techo del portal' y 'sin fisica declarada => no false-fire con numeros ES'; minimiza al contraejemplo y lo congela como regression-fixture.

#### Herramienta NEXT-LEVEL
**Hypothesis** (MPL-2.0) https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:317-323, "property-based-recipe-fuzzing"]: sintetiza el caso de portal/locale raro (techos no-ES, page_size distinto, postcodes/divisas de otro mercado) que los golden ES no cubren, MINIMIZA al contraejemplo mas simple y lo congela como regression-fixture determinista. Es la 2a-via adversarial mecanica que prueba que el detector es country-CORRECT, no solo country-blind. Corre en el job db-tests/unit existente, CPU puro, sin red.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-10"></a>
### Faceta 10 · Motor de quorum + precision-gate + piso de independencia por-pais
*indep≥2 sin debilitar VAM: proveer una 2ª vía real, jamás relajar el gate.*  ·  **v1:** Clúster H

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — La matematica de quorum es generica y sin literal 'ES' [VERIFIED quorum.py:159-345, independence.py:12-69]; la costura es un parametro AUSENTE: no hay piso de independencia por-pais ni ruta-alternativa. El D>=2 (admit) e indep>=2 (Step2) son satisfacibles en ES multi-portal pero estructuralmente insatisfacibles en mercado monoportal -> indep_score devuelve 0 con <2 asserting [VERIFIED independence.py:58-59].
- **Fix exacto** — Declarar en country.toml una politica de independencia por-CC que NO relaja el D>=2 (invariante anti falso-TRUSTWORTHY, nota Director independence.py:35-46) sino que PROVEE un camino independiente adicional: ingerir una lista ortogonal de mecanismo-distinto (registral) como 2o skeptic-path. decide() queda byte-identico; el country-pack solo declara que rutas ortogonales existen.
- **Riesgo adversarial** — PT / regiones MX/JP monoportal no producen 2o camino independiente -> indep<2 -> cada claim REFUTED(NO_INDEPENDENT_PATH) [VERIFIED router.py:84 -> ESCALATE_OWNER] -> el pais no puede sellar jamas. Relajar el gate para 'arreglarlo' fabricaria falsos TRUSTWORTHY, la direccion prohibida (Law I default-REFUTED).
- **Sellado multi-vía** — Sello: ES byte-identico (golden, cero cambio de math); fixture mercado-fino con ruta ortogonal anadida -> claim verdadero alcanza indep>=2/TRUSTWORTHY, falso sigue REFUTED; la ruta ortogonal pasa admit() (D>=2 real); near-clone (D<2) no levanta indep. Multi-via: worked-examples spec 5.6 + recompute independiente del min pairwise + adversarial par correlacionado.
- **Herramienta NEXT-LEVEL** — GLEIF LEI Golden Copy (CC0 1.0, EUR0) https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy [VERIFIED NEXT-LEVEL.md:172-178]: lista registral global mecanismo-distinto que da a mercados finos el 2o camino independiente para indep>=2 sin adaptador de registro nacional. Via complementaria pyJedAI (Apache-2.0) https://github.com/AI-team-UoA/pyJedAI [VERIFIED NEXT-LEVEL.md:543-549].

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) Verificacion de code_hints [VERIFIED]
- [VERIFIED pipeline/inquisition/quorum.py:159-345] `decide()` de 6 pasos:
  - Step0 [:183] particiona admitidos via `admit(s, producer)`.
  - [:209] `indep = _indep_score(assert_admitted, producer)`.
  - 5.5 false-veto guard [:214] `_credible_hard_refuters(hard_admitted)` -> `rh`.
  - Step1 hard-veto [:220-231] `if rh>=1: REFUTED`.
  - Step2 **gate de independencia** [:236-246] `if indep<2: REFUTED reason="NO_INDEPENDENT_PATH"`.
  - Step3 modal ASSERT [:269-273] `v_star,n_star`; `rival = any(v!=v_star and cnt>=2)`.
  - Step4 TRUSTWORTHY [:281] `if n_star>=2 and not rival and (rs+ab)<n_star`; con precision gate [:287-301] `if precision is not None and not precision.passed: INCONCLUSIVE` (downgrade, **no** REFUTED).
  - Step5 [:320-331] `rival -> SPLIT_QUORUM` / `(rs+ab)>=n_star -> MAJORITY_REFUTE`.
  - Step6 [:336-345] INCONCLUSIVE SINGLE_ASSERT.
- [VERIFIED pipeline/inquisition/independence.py:12-19] `admit()`: `indep_distance(skeptic.state, producer) >= 2`.
- [VERIFIED independence.py:22-69] `indep_score()`: weakest-link = `min` de D pairwise sobre asserting; **`if len(asserting)<2: return 0`** [:58-59] -> fuerza Step2 REFUTED(NO_INDEPENDENT_PATH). Nota Director [:35-46]: ante ambiguedad de spec, la lectura estricta gana, "can only ever over-refute, never manufacture a false TRUSTWORTHY".
- [VERIFIED quorum.py:118-152] `_credible_hard_refuters`: (a) cualquier REFUTE_HARD deterministico es creible solo; (b) lone non-det demoted; (c) 2+ non-det con `indep_distance>=2` en un par -> creibles.
- [VERIFIED quorum.py:100-111] `PrecisionGate`: `passed: bool`, Wilson `ci_upper<=p0`; `None` -> no gating (cost-zero default; ausencia nunca bloquea).

#### (b) Mecanismo al atomo
Matematica de veredicto VAM pura. El requisito DURO: `indep>=2` = al menos 2 caminos asserting mutuamente independientes (D>=2 sobre el state-tuple de 4 dimensiones). Un solo asserting -> indep=0 -> REFUTED(NO_INDEPENDENT_PATH). El precision-gate SOLO degrada TRUSTWORTHY->INCONCLUSIVE ante FALLO explicito de muestreo (Wilson ci_upper>p0); su ausencia jamas bloquea un count-quorum.

#### (c) Costura ES->generico + fix exacto
La matematica es generica; **ningun literal lleva 'ES'**. La costura es un parametro AUSENTE: no hay piso de independencia por-pais ni politica de ruta-alternativa. En ES (muchos portales) indep>=2 es satisfacible; en mercado fino/monoportal es **estructuralmente insatisfacible**. **Fix:** declarar en country.toml una politica de independencia por-CC consumida por decide() que **NO relaja** el D>=2 (ese es el invariante que impide falsos TRUSTWORTHY — ver nota Director independence.py:35-46) sino que **provee un camino independiente adicional**: ingerir una lista ortogonal de mecanismo-distinto (registral) como 2o skeptic-path genuino, de modo que un monoportal gane un corroborador independiente real. El country-pack declara que rutas ortogonales existen; decide() queda byte-identico.

#### (d) Riesgo adversarial concreto
PT, o regiones MX/JP monoportal, no producen 2o camino independiente -> indep<2 -> CADA claim REFUTED(NO_INDEPENDENT_PATH) -> todo a ESCALATE_OWNER [VERIFIED router.py:84] -> el pais **no puede sellar jamas**. El cierre exige una independencia que el mercado no genera. "Arreglarlo" relajando el gate **fabricaria** falsos TRUSTWORTHY — la unica direccion en que la Inquisicion nunca debe derivar (Law I default-REFUTED).

#### (e) Sellado + verificacion multi-via
- **Sello:** (i) sobre ES, decide() byte-identico (golden) — cero cambio de math; (ii) sobre fixture de mercado fino, tras anadir la ruta ortogonal registral, un claim verdadero alcanza indep>=2 y TRUSTWORTHY, uno falso sigue REFUTED; (iii) la ruta ortogonal es mecanismo-distinto (baja correlacion con el portal dominante) — verificado porque `admit()` (D>=2) realmente la admite; (iv) un near-clone (D<2) **no** debe levantar indep (admit() lo rechaza).
- **Multi-via:** 1a = golden de los worked-examples del spec (5.6); 2a = recompute independiente del `min` pairwise; 3a adversarial = par de skeptics correlacionados -> indep<2 confirmado.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**GLEIF LEI Golden Copy** (CC0 1.0 Universal — dominio publico, comercial OK, sin atribucion; EUR0) — https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy [VERIFIED NEXT-LEVEL.md:172-178, cluster discovery-trust]. Una lista registral GLOBAL de mecanismo-distinto que **EXISTE para cualquier pais el dia uno** (entidad+pais+id de registro local), surtiendo a los mercados finos el 2o camino independiente que el `indep>=2` del quorum exige, **sin** escribir un adaptador de registro nacional (BORME/Handelsregister). Licencia CC0 = la mas limpia posible. **Via independiente complementaria:** **pyJedAI** (Apache-2.0, EUR0) — https://github.com/AI-team-UoA/pyJedAI [VERIFIED NEXT-LEVEL.md:543-549] como 2o motor ER arquitectonicamente independiente para certificacion 2-via.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-11"></a>
### Faceta 11 · Router sellado de veredicto + catalogo de FUENTES del bus (el punto de fuga)
*La tabla sellada intacta; enumerar y enchufar a un bus durable lo que hoy muere en humano.*  ·  **v1:** Infra · router

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — La _ROUTING_TABLE [router.py:65-99] es country-agnostica y esta SELLADA (43, 'sealed by Director 2026-06-15') y NO debe cambiar; la costura no es la tabla sino que 4 de sus salidas mueren en humano sin memoria: NO_INDEPENDENT_PATH->ESCALATE_OWNER (84) e INCONCLUSIVE/*->ESCALATE_OWNER (93), mas ESCALATE_GASTO emitido fuera del router por detect_staleness (detect.py:496) y health.py:372. El dedupe_key es subject-scoped (router.py:180): refresca por objeto pero no reusa ambiguedades equivalentes cross-pais.
- **Fix exacto** — Preservar _ROUTING_TABLE byte-identica (golden router_mapping_rows exhaustivo); insertar el triage de faceta 24 AGUAS ABAJO de _lookup_route, nunca dentro de la tabla. Enumerar y tipar el catalogo de fuentes de decision_request {router NO_INDEPENDENT_PATH, router INCONCLUSIVE, detect ESCALATE_GASTO, health ESCALATE_OWNER, classifier_drift->CLASSIFICATION_DOUBT, geo_drift->GEO_AMBIGUITY, recipe_harness tier1->RECIPE_TIER1_NEW, cover(CC) COVERAGE_SEAL_REVIEW} y conectarlas a un bus durable Postgres con claim idempotente FOR UPDATE SKIP LOCKED + retry/backoff + reanudacion crash-safe, heredando la emision acotada opt-in (CARDEEP_INQUISITION_EMIT).
- **Riesgo adversarial** — Un pais de cola fina (PT, o MX/JP monoportal) genera muchos INCONCLUSIVE/NO_INDEPENDENT_PATH e inunda ESCALATE_OWNER -el dead-end que el bus venia a vaciar- y sin emision acotada auto-DoSea a Claude. Si el triage toca la tabla sellada en vez de aguas abajo, se rompe 'misma mentira misma ruta' (el invariante auditable). El dedupe_key subject-scoped re-litiga la misma duda cross-pais N veces (rafaga x pais). _write_alert escribe filas alert que nadie mira con el stack CAIDO: las escalaciones criticas no alcanzan al operador fuera-de-banda.
- **Sellado multi-vía** — Sellado = _ROUTING_TABLE byte-identica (cero cambio), catalogo de fuentes 100% enumerado emitiendo a bus durable con claim exactamente-una-vez, emision opt-in heredada, cero escalacion sin memoria. Multi-via: (1) golden exhaustivo de router_mapping_rows (cambio=CI rojo); (2) crash-safe: matar worker a mitad de CLAIMED y verificar retoma exactamente-una-vez sin duplicar APPLIED; (3) conteo independiente decision_event(append-only)==transiciones esperadas por SQL; (4) cobertura adversarial: sembrar pais que dispare cada kind y confirmar 0 alert huerfanos, todo aterriza como decision_request, spend/prod/legal queda PENDING-OWNER sin parar el loop.
- **Herramienta NEXT-LEVEL** — Procrastinate (MIT, €0) https://github.com/procrastinate-org/procrastinate [VERIFIED NEXT-LEVEL.md:552-558] — cola durable Postgres-nativa que modela decision_request como estados de tarea con claim idempotente FOR UPDATE SKIP LOCKED + retry/backoff + reanudacion crash-safe sobre el PG existente; cierra 'lease best-effort sin takeover'. Complemento Apprise (BSD-2-Clause, €0) https://github.com/caronc/apprise [VERIFIED NEXT-LEVEL.md:704-710] — fan-out de la alerta critica del router a 100+ canales con routing por-pais para que ESCALATE_OWNER alcance al operador fuera-de-banda cuando la fila alert no la ve nadie.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) Verificacion de code_hints [VERIFIED]
- **[VERIFIED pipeline/inquisition/router.py:43]** la tabla se declara *"§7 — sealed by Director on 2026-06-15"*: es un contrato sellado, sin discrecion de agente.
- **[VERIFIED pipeline/inquisition/router.py:65-99]** `_ROUTING_TABLE: list[_RouteRow]` — lookup puro `(verdict, reason_match) -> (action, lane, quarantines, severity, score)`. Cubre TRUSTWORTHY (none), REFUTED (hard/soft), INCONCLUSIVE, QUARANTINED.
- **[VERIFIED pipeline/inquisition/router.py:84]** `_RouteRow("REFUTED", "NO_INDEPENDENT_PATH", "escalate", "ESCALATE_OWNER", False, "warning", 0.5)` — el dead-end #1.
- **[VERIFIED pipeline/inquisition/router.py:93]** `_RouteRow("INCONCLUSIVE", "*", "escalate", "ESCALATE_OWNER", False, "info", 0.5)` — el dead-end #2 (catch-all de todo INCONCLUSIVE).
- **[VERIFIED pipeline/inquisition/router.py:103-128]** `_lookup_route` resolucion ordenada: exact -> catch-all '*' del verdict -> fallback defensivo RESEARCH (nunca alcanzado, tabla exhaustiva).
- **[VERIFIED pipeline/inquisition/router.py:140-228]** `route_verdict`: action 'none' => `(none, None)` sin gestion_item; resto => `open_or_refresh`; critical => `_write_alert` (216-219).
- **[VERIFIED pipeline/inquisition/router.py:180]** `dedupe_key = f"inquisition:{subject_type}:{subject_key}"` — **subject-scoped** (un item abierto por objeto de datos, no por reason): re-prosecuciones REFRESCAN en vez de apilar.
- **Catalogo de fuentes (las salidas que hoy mueren en humano), VERIFIED:**
  - `ESCALATE_OWNER` del router: dos puntos exactos — `router.py:84` (NO_INDEPENDENT_PATH) y `router.py:93` (INCONCLUSIVE/*).
  - `ESCALATE_GASTO`: **[VERIFIED pipeline/gestionador/detect.py:496]** `lane="ESCALATE_GASTO"` lo emite `detect_staleness` en storm-suppression (no es del router). **[VERIFIED pipeline/gestionador/route.py:32-33]** `LANE_SLA` mapea `ESCALATE_GASTO/ESCALATE_OWNER -> None` (sin SLA, awaits human/budget) y **[VERIFIED route.py:322]** ambos son lanes terminales.
  - `ESCALATE_OWNER` de ops: **[VERIFIED pipeline/ops/health.py:372]** `ACTION_ESCALATE_OWNER` en el motor de salud.
  - Futuras (al activarse): los 2 STUB -> `classifier_drift->CLASSIFICATION_DOUBT`, `geo_drift->GEO_AMBIGUITY`; el fallo de RecipeHarness en fuente Tier-1; y los checkpoints de `cover(CC)` (COVERAGE_SEAL_REVIEW). **[VERIFIED prosecutor.py:420 / scheduler.py:622]** la emision de claims desde verdicts es **opt-in/acotada** (`CARDEEP_INQUISITION_EMIT`), pista de que el bus debe heredar ese freno (faceta 15).

#### (b) El mecanismo al atomo
La tabla es una funcion total `f(verdict, reason) -> ruta` con la propiedad invariante **"misma mentira, misma ruta"**: el determinismo auditable es el valor del router. Hoy 4 de sus salidas escalan a un humano (`ESCALATE_OWNER`), y el sistema circundante anade `ESCALATE_GASTO`. Cada una de esas escalaciones **muere en el humano sin memoria reutilizable**: no hay store que recuerde "esta forma de duda ya se adjudico asi". El `dedupe_key` subject-scoped impide apilar items por objeto, pero NO deduplica *ambiguedades equivalentes entre sujetos/paises*.

#### (c) La costura ES->generico con su fix exacto
**Costura:** la tabla es country-agnostica por construccion (mapea verdict+reason, sin literal ES) y NO debe cambiar. El problema no es la tabla: es que sus salidas terminan en un humano sin bus. La costura es *enumerar el catalogo de fuentes de decision y conectarlo a un bus durable AGUAS ABAJO, sin tocar la tabla sellada*.

**Fix exacto:**
- **Preservar `_ROUTING_TABLE` byte-identica** (golden `router_mapping_rows()` exhaustivo). El triage de la faceta 24 se inserta DESPUES de `_lookup_route`, nunca dentro de la tabla.
- **Catalogo enumerado y tipado** de fuentes de `decision_request`: `{router.NO_INDEPENDENT_PATH, router.INCONCLUSIVE/*, detect.ESCALATE_GASTO(staleness storm), health.ESCALATE_OWNER, classifier_drift->CLASSIFICATION_DOUBT, geo_drift->GEO_AMBIGUITY, recipe_harness.tier1_fail->RECIPE_TIER1_NEW, cover(CC).COVERAGE_SEAL_REVIEW}`. Cada fuente declara su `kind` ENUM del contrato del bus (faceta 23).
- **Bus durable** que reciba esas fuentes: las tareas de drenado (local_ai_drain, claude_drain, country_campaign_tick) se modelan como tareas durables sobre Postgres con claim idempotente `FOR UPDATE SKIP LOCKED`, retry/backoff y reanudacion crash-safe — no como loops bespoke.
ES queda igual: la tabla no cambia; solo se aprovecha lo que ya escala a humano para alimentar un bus con memoria.

#### (d) El riesgo adversarial concreto (DE/FR/IT/PT/no-UE/ruido)
- **Inundacion de cola fina (PT, MX/JP monoportal):** un pais que produzca muchos `INCONCLUSIVE` (geo ambigua) o `NO_INDEPENDENT_PATH` (sin 2o camino) **inunda `ESCALATE_OWNER`** — exactamente el dead-end que el bus venia a vaciar. Sin emision acotada hereda el riesgo de auto-DoS del scheduler.
- **Rotura del invariante sellado:** si el triage se inserta MAL (tocando `_ROUTING_TABLE` en vez de aguas abajo de `_lookup_route`), se rompe "misma mentira misma ruta" — el determinismo auditable colapsa y el router deja de ser certificable.
- **Re-litigio cross-pais:** el `dedupe_key` subject-scoped NO reusa ambiguedades equivalentes entre paises; sin un dedupe semantico, la misma forma de duda de denominador/geo se re-paga N veces (rafaga de Claude multiplicada por pais).
- **Alertas zombie con stack caido:** `_write_alert` (216) escribe filas `alert` in-DB que **nadie mira cuando el stack esta CAIDO** (estado real hoy); las escalaciones criticas no alcanzan al operador fuera-de-banda.

#### (e) Criterio de sellado + verificacion multi-via
**Sellado:** `_ROUTING_TABLE` byte-identica (cero cambio); catalogo de fuentes 100% enumerado y cada una emitiendo a un bus durable con claim exactamente-una-vez; emision acotada/opt-in heredada; cero escalacion que muera sin memoria reutilizable.
**Multi-via:**
1. **Golden de tabla sellada:** `router_mapping_rows()` exhaustivo congelado; cualquier cambio de fila => CI rojo (el triage NO altera ninguna ruta).
2. **Via durable (crash-safe):** matar el worker a mitad de un `decision_request` CLAIMED y verificar que otro lo retoma y completa **exactamente una vez** (sin duplicar APPLIED).
3. **Via independiente (conteo):** `count(decision_event append-only) == numero de transiciones esperado`, recomputado por SQL directo contra el log del worker.
4. **Via adversarial (cobertura del catalogo):** sembrar un pais que dispare cada `kind` de fuente y confirmar que **ninguna** escalacion termina en un `alert` huerfano — todas aterrizan como `decision_request` con su `kind` correcto; las `ESCALATE_GASTO/prod/legal` quedan PENDING-OWNER sin parar el loop.

#### (f) Herramienta NEXT-LEVEL que la eleva a nivel inalcanzable
**Procrastinate** (MIT, €0) — https://github.com/procrastinate-org/procrastinate — cola de tareas durable Postgres-nativa: modela `decision_request PENDING->CLAIMED->DECIDED->APPLIED->VERIFIED` como estados de tarea con **claim idempotente `FOR UPDATE SKIP LOCKED`**, retry con backoff exponencial por tipo, deferral, y un worker que reanuda a mitad de vuelo tras crash; corre sobre el PG existente (cero infra). [VERIFIED NEXT-LEVEL.md:552-558]. Cierra el riesgo declarado "lease best-effort, NO takeover" con reanudacion real de la unidad de trabajo. Complemento de salida: **Apprise** (BSD-2-Clause, €0) — https://github.com/caronc/apprise — fan-out de la alerta critica del router a 100+ canales (ntfy/email/webhook) con claves de routing por-pais, para que un `ESCALATE_OWNER`/lease-rancio alcance al operador fuera-de-banda cuando el stack esta caido y la fila `alert` no la ve nadie [VERIFIED NEXT-LEVEL.md:704-710].

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-12"></a>
### Faceta 12 · Maquinaria de inquisicion (lenses/prosecutor/sampler) + prosecutor como 2a-via de sellado
*El prosecutor como 2ª-vía genuina: tolerancias inyectadas + tri-agreement ER, sin sesgo ES heredado.*  ·  **v1:** Clúster E/H

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — La logica de lenses/quorum/prosecutor es pura y country-agnostica EN ESTRUCTURA, pero (a) la tolerance del claim esta hardcoded 0.005 [VERIFIED prosecutor.py:484]; (b) quorum within_tolerance depende de regime y de TAU calibrados a magnitudes ES; (c) los formatos de valor que los lenses comparan (separador decimal, moneda) asumen forma ES. Si Lens A/B/C/D miden con tolerancias ES, la 'recomputacion independiente' arrastra el mismo sesgo que pretende auditar.
- **Fix exacto** — (1) Inyectar `tolerance` y los TAU desde el CountryPack (faceta 29/5) en lugar del 0.005 hardcoded. (2) Garantizar que la 2a-via re-derive desde las medidas ORTOGONALES de los lenses (DB cruda) y, donde existan, desde independent_values de los skeptics — nunca desde primary_value del productor. (3) Anadir pyJedAI como TERCER camino ER genuinamente independiente para tri-agreement (net determinista / Splink / pyJedAI), de modo que el sello tenga una 2a/3a via que NO comparte estado con la 1a.
- **Riesgo adversarial** — En cola fina (PT, regiones MX/JP monoportal) re-prosecutar TRUSTWORTHY a EUR0 solo degrada a REFUTED:NO_INDEPENDENT_PATH [VERIFIED :513] — por eso esta gated-off; pero un pais que inunde verification_verdict con REFUTED/UNVERIFIED hace que prosecute_pending(limit=100) sea el cuello de la 2a-via. Si los lenses heredan tolerancias ES (TAU, 0.005), la 'independencia' es teatro: audita con la misma regla que cuestiona. Formatos no-ES (decimal coma, JPY sin decimales) rompen within_tolerance. DE/FR/IT: un valor legitimo fuera del rango de magnitud ES puede ser REFUTE_HARD espureo.
- **Sellado multi-vía** — Multi-via (NEXT-LEVEL pyJedAI): (1) TRI-AGREEMENT — net determinista (piso) + Splink (probabilistico) + pyJedAI (toolkit independiente) deben concordar dentro del intervalo ER-Evaluation por-pais, logueado por CC. (2) DIVERGENCIA -> auto-surface al VAM gate (auditoria auto-sanable), nunca sellado en silencio. (3) el prosecutor re-deriva cobertura/quorum SIN leer la fila campaign y debe coincidir con la 1a via dentro de tolerancia (doble recomputo, faceta 28). (4) REPRODUCIBILIDAD — configs+seeds pineados hacen de cada salida un artefacto golden en CI.
- **Herramienta NEXT-LEVEL** — pyJedAI (Apache-2.0, EUR0) https://github.com/AI-team-UoA/pyJedAI [VERIFIED NEXT-LEVEL.md:546,:66] — segundo/tercer camino ER independiente para certificacion de sello 2-via; corre offline como job de certificacion, fuera del path de serving; habilita tri-agreement determinista/Splink/pyJedAI. Alt: Python Record Linkage Toolkit, Splink (MIT, :401).

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### Mecanismo al atomo
El prosecutor corre una prosecucion ATOMICA por claim: `prosecute_claim` envuelve todo en `conn.transaction()` y revierte a PENDING en cualquier fallo (sin zombie PROSECUTING; anida como SAVEPOINT bajo un test) [VERIFIED prosecutor.py:115-134]. El batch poller `prosecute_pending(limit=100)` usa `idx_claim_pending` y no re-pollea DECIDED [VERIFIED :329-338].

**Doble rol (2a-via):** el puente de cosecha §9 `emit_claim_from_verdict` convierte una fila VAM `verification_verdict` en un `inquisition_claim` PENDING, re-keando `entity_inventory -> inventory:<entity_ulid>` (para que Lens A mida el conteo REAL) y `denominator`, y haciendo SKIP de coverage/platform_slice/family_slice (no las coacciona a 'count') [VERIFIED :407-454]. `emit_claims_from_verdicts` es OPT-IN: el scheduler solo lo llama con `CARDEEP_INQUISITION_EMIT=1` [VERIFIED :510], selecciona REFUTED/UNVERIFIED y deja TRUSTWORTHY gated-off por defecto porque re-prosecutarlo a EUR0 solo puede degradar a `REFUTED:NO_INDEPENDENT_PATH` [VERIFIED :513,:516-527]. La inquisicion despliega lenses A-D + sampler + independence + quorum.decide (6 pasos) [VERIFIED existen: lenses.py, _lens_a..d.py, sampler.py, independence.py, quorum.py:159].

**Gap honesto:** la independencia genuina la aportan los LENSES al re-MEDIR desde la DB cruda (Lens A = conteo real), NO la lectura de independent_values — el emit lee `primary_value`/`primary_path` (el valor del PRODUCTOR) [VERIFIED :431-432,:518] y la `tolerance` esta hardcoded a `0.005` [VERIFIED :484]. Quorum aplica `within_tolerance` gobernado por `regime` EXACT/DRIFT [VERIFIED quorum.py:174; tolerance presente en quorum.py/lenses.py/models.py/_lens_b.py/_lens_c.py].

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-13"></a>
### Faceta 13 · Scheduler durable: nucleo crash-safe + mutex single-producer + activacion
*El daemon durable: advisory-lock single-producer + servicio Windows versionado (el stack hoy CAÍDO).*  ·  **v1:** Infra · liveness

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — La clave de lock `0x43415244` es una constante global host-singleton (no parametrizada por CC); `require_prod_secrets` lee DSN de env globales. El motor es country-blind aqui por diseno (substrato de orquestacion), lo cual es correcto — PERO 'blind' debe volverse 'multi-tenant-aware' a nivel de ARTEFACTO de despliegue: NO hay descriptor de servicio Windows commiteado (la etapa 09 lo marca como NSSM-prosa en DEPLOY-DURABLE-DAEMONS.md §3), asi que 'el daemon sobrevive al reboot / corre bajo restart supervisado' es documentacion, no artefacto reproducible. El seam de activacion = convertir los jobs picklables dormantes en un servicio vivo, auto-reiniciable y versionado parametrizado por CARDEEP_COUNTRY.
- **Fix exacto** — Commitear un artefacto de servicio Windows versionado (ops/windows/cardeep-harvest.xml para WinSW, o una invocacion Shawl) parametrizado por %CARDEEP_COUNTRY%, espejando 1:1 la unit systemd de Linux (Restart=always == onFailure restart). Mantener el single-instance garantizado por el advisory lock en PG, NO por el supervisor (asi dos hosts siguen sin poder doble-producir). Anadir un dead-man externo por-(rol,CC) para que la muerte del host entero sea observable. ES queda byte-identico: el valor del lock, require_prod_secrets y los 8 intervalos no cambian; lo unico que se anade es el wrapper supervisado + el watchdog externo. Para particion real de carga por-CC multi-host (fuera de scope actual), el lock host-singleton necesitaria una clave por-shard derivada de CARDEEP_COUNTRY.
- **Riesgo adversarial** — El lock 0x43415244 es una UNICA clave host-singleton: a escala multi-pais en multiples hosts NO hay particion de carga por-CC — o un host produce todo (cuello) o dos hosts colisionan en la misma clave (uno hace SystemExit). Tras un SIGKILL del holder, el advisory lock queda huerfano la ventana hasta que Postgres reapa el socket de la sesion muerta; en esa ventana un restart choca con el lock 'vivo' y hace SystemExit -> TODA la cadencia muere para TODOS los paises (no solo el nuevo) hasta el reap. Sin la migracion 0054 aplicada el stale-check es inerte, asi que el orphan es invisible. Con el stack CAIDO hoy, el bus jamas drena y cover(CC) nunca tickea: el Cerebro entero es teorico hasta que el daemon arranca Y se mantiene vivo bajo supervision. DE/FR/IT/PT/no-UE estan igualmente afectados — es un riesgo de liveness del substrato, country-agnostico, pero clava CADA sello por-pais porque ningun predicado de sello puede evaluarse mientras el scheduler este muerto.
- **Sellado multi-vía** — Multi-via: (1) Test de reboot: reboot del host (o stop forzado del servicio) y confirmar arranque automatico + readquisicion limpia del lock. (2) Golden de paridad cross-OS: diff semantico entre el XML WinSW y la unit systemd (mismas env/paths/restart) — artefacto versionado, no prosa. (3) Adversarial process-kill: matar el PROCESO (no el servicio) y verificar restart automatico y que el nuevo proceso readquiere el lock sin que aparezca jamas un 2o productor. (4) Dead-man externo: detener el daemon y confirmar alerta out-of-band dentro de la grace window (reloj independiente). (5) Orphan-lease: simular SIGKILL y aseverar que el camino stale-lease (0054) aflora una linea CRITICAL diagnosticable en vez de un bucle SystemExit silencioso. (6) gestion_item-bajo-carga: la maquina durable debe ejercitarse bajo carga real (gestion_item esta VACIA hoy — probada por tests, jamas por carga viva) antes de que el bus herede sus estados.
- **Herramienta NEXT-LEVEL** — WinSW (MIT) — https://github.com/winsw/winsw [VERIFIED NEXT-LEVEL.md:568-574, seccion 'Artefacto de servicio Windows VERSIONADO (WinSW/Shawl) - cerrar el hueco NSSM-prosa'; licencia tambien en tabla resumen :69]. Envuelve cualquier proceso como servicio Windows desde un descriptor XML versionable (commit a ops/windows/), espejando las units systemd como codigo, parametrizado por CARDEEP_COUNTRY con Restart=always equivalente. Alternativa Shawl (Rust binario unico, MIT, https://github.com/mtkennerly/shawl). Complementos verificados en el mismo cluster: Healthchecks (BSD-3-Clause, https://github.com/healthchecks/healthchecks [:560-566]) como dead-man switch EXTERNO (quien vigila al vigilante), y Procrastinate (MIT, https://github.com/procrastinate-org/procrastinate [:552-558]) para dar a los drains semantica de TAREA durable (claim FOR UPDATE SKIP LOCKED + retry/backoff) que el combo advisory-lock+APScheduler no puede expresar. EUR0, sin servicio nuevo de cimiento.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) code_hints VERIFICADOS
- [VERIFIED scheduler.py:895] `def _start_scheduler() -> None` — "Start the durable BlockingScheduler. Blocks until SIGINT/SIGTERM."
- [VERIFIED scheduler.py:899-903] `require_prod_secrets((_RAW_DSN,'CARDEEP_DSN'),(DB_URL,'CARDEEP_DB_URL'),(_ASYNCPG_DSN,'CARDEEP_ASYNCPG_DSN'))` — fail-fast en prod si algun DSN aun lleva la credencial dev; no-op si CARDEEP_ENV unset/dev (dev/test byte-identico).
- [VERIFIED scheduler.py:913] `_SCHEDULER_SINGLETON_LOCK = 0x43415244` (ASCII 'CARD' = 1128354372) — clave host-singleton fija.
- [VERIFIED scheduler.py:914-915] `_lock_conn = psycopg2.connect(_RAW_DSN); _lock_conn.autocommit=True` — abierta toda la vida del proceso (comentario: do not close).
- [VERIFIED scheduler.py:919-924] `if not acquire_with_stale_retry(_lock_conn, lock): _lock_conn.close(); raise SystemExit('another cardeep scheduler already holds...')` — `pg_try_advisory_lock` atomico, retry SOLO si el lease del holder previo es rancio; "Best-effort stale check; inert without migration 0054".
- [VERIFIED scheduler.py:928] `record_heartbeat(_lock_conn, lock, holder='harvest')` — reclama el lease observable.
- [VERIFIED scheduler.py:930-933] `jobstores={'default': SQLAlchemyJobStore(url=DB_URL)}; BlockingScheduler(jobstores=jobstores, timezone='UTC')`.
- [VERIFIED scheduler.py:938-1058] familia de 8 add_job (heartbeat_tick, silence_watchdog, inquisition_cadence, inquisition_prosecute +30m stagger :990, gestionador_detect, canonical_key_backfill, lease_heartbeat, product_stats_refresh).
- [VERIFIED scheduler.py:1066-1071] `scheduler.start()` / `except (KeyboardInterrupt, SystemExit)` / `finally: scheduler.shutdown(wait=False)`.

#### (b) Mecanismo al atomo
La durabilidad tiene DOS patas independientes. (1) Durabilidad del JOB: el SQLAlchemyJobStore picklea cada job en Postgres, asi la muerte del proceso no pierde la agenda — al reinicio `replace_existing=True` re-fija cada job. (2) Seguridad single-producer: un advisory lock de SESION (0x43415244) retenido en una conexion dedicada abierta toda la vida del proceso; `pg_try_advisory_lock` es el mutex atomico, un holder vivo NUNCA es desplazado (cicatriz AS24: dos governors en un host 4x-martillearon y perdieron 138 dealers). El retry solo dispara si el lease del predecesor es rancio (crash). Al cerrar la conexion en exit, Postgres auto-libera. `require_prod_secrets` es la guarda de frontera que rehusa arrancar en prod con DSN dev. El lock es HOST-singleton, NO por-CC. REALIDAD CRITICA: el stack esta CAIDO hoy — los jobs estan registrados/picklables pero el daemon NO corre, asi que toda cadencia (y por tanto cualquier drenado futuro del bus) es INERTE hasta un restart supervisado.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-14"></a>
### Faceta 14 · Capa de lease/heartbeat (observabilidad de liveness del orquestador)
*Liveness del orquestador: dead-man externo + restart supervisado + shard por-(rol,CC).*  ·  **v1:** Infra · liveness

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — Costura INVERSA: el codigo ya es agnostico (cero ES), pero el lock es HOST-SINGLETON — `_SCHEDULER_SINGLETON_LOCK=0x43415244` (scheduler.py:913) es un entero fijo por host, sin shard por-(rol,CC). El lease (0054) observa un mutex que no tiene dimension de pais. Segunda costura: 0054 debe estar aplicada o la capa es inerte (UndefinedTable->warn, daemon byte-identico) y el orphan invisible.
- **Fix exacto** — 1) Generalizar la clave de UN constante de host a un shard por-(rol,CC): `lock_key = base ^ hash(role, country_code)` (o tabla de asignacion documentada), para que productores de cover(DE)/cover(ES) corran en hosts distintos sin colisionar y el lease nombre que (rol,CC) cayo. `scheduler.py:1036 args=[lock,"harvest"]` ya threadea el holder string — extender holder a `f"harvest:{CC}"` y el lock_key al shard por-CC; ES se queda en `0x43415244` legacy (deployment ES byte-identico). 2) Hacer la aplicacion de 0054 un predicado BOOTSTRAPPED de cover(CC) (faceta 27): un pais no sale de REGISTERED hasta que su tabla de lease existe y el daemon registro un heartbeat fresco — convirtiendo 'stack caido, lease inerte' en gate computable. 3) Emparejar con un dead-man switch EXTERNO porque el lease in-process no detecta la muerte del host entero.
- **Riesgo adversarial** — Stack CAIDO hoy: cero heartbeat, lease stale/ausente, bus y cover(CC) sin tickear (cerebro teorico). Tras SIGKILL del holder, lock huerfano + restart SystemExit (scheduler.py:921) -> toda la cadencia muere para todos los paises hasta el reap de PG. Multi-host no-UE: una sola clave 0x43415244 -> 2o host SystemExit permanente (un productor de 2o pais nunca arranca) o, en DBs separadas, cero garantia single-producer cross-host = AS24 doble-productor (138 dealers martilleados). El watchdog in-process es ciego a su propia muerte: host Windows 11 unico cae y nadie se entera.
- **Sellado multi-vía** — SEALED exige que el daemon REALMENTE corra bajo restart supervisado (no solo registrado): (a) prueba viva de que `_lease_heartbeat_job` bumpeo `last_heartbeat` dentro de TTL (`SELECT last_heartbeat ... age<6min`); (b) test kill-and-restart: SIGKILL del holder, confirmar que `check_and_clear_stale_lease` loggea CRITICAL y un restart supervisado re-adquiere limpio; (c) 0054 aplicada (la tabla existe); (d) shard por-CC probado distinto (dos CC sinteticos adquieren dos locks distintos sin colision); (e) el dead-man switch externo dispara cuando el host entero muere. Multi-via: unit tests de `is_lease_stale` (puro, DB-free) + test de integracion kill/restart + cross-check del watchdog externo ('down' de Healthchecks vs `SELECT last_heartbeat` concuerdan en el corte).
- **Herramienta NEXT-LEVEL** — PRIMARIA: Healthchecks (BSD-3-Clause, EUR0) — https://github.com/healthchecks/healthchecks [VERIFIED NEXT-LEVEL.md:563, tabla:68]. El lease es observabilidad IN-PROCESS — estructuralmente ciega a su propia muerte de proceso/host. Healthchecks es un dead-man switch EXTERNO con su propio reloj: cada heartbeat_tick pinga una URL de check unica; si el scheduler deja de pingar dentro de la grace window (2x cadencia, espeja el SILENCE_MULTIPLIER=2 existente) alerta fuera-de-banda (ntfy/webhook/email). Country-aware: un check por (rol,CC) nombra el productor caido — 'quien vigila al vigilante', el guard de liveness de nivel-superior que el sello 'daemons persistentes' (hoy prosa) no tiene (NEXT-LEVEL:560-566). EUR0 self-host. SECUNDARIA: WinSW (MIT, EUR0) — https://github.com/winsw/winsw [VERIFIED:571, tabla:69]: el sello exige restart SUPERVISADO en el host Windows 11 real, hoy solo prosa NSSM (DEPLOY-DURABLE-DAEMONS.md §3, sin artefacto). WinSW envuelve el daemon como servicio Windows versionado desde un XML commiteable (ops/windows/, %CARDEEP_COUNTRY%, Restart=always), espejando la unit systemd 1:1; el single-instance lo sigue garantizando el advisory lock, no el supervisor (NEXT-LEVEL:568-574). Alts NEXT-LEVEL: Shawl (Rust 1-binario), Procrastinate (tareas durables PG — cierra el 'lease best-effort, NO takeover' con reanudacion real de la unidad de trabajo, :552-558).

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) Verificacion de code_hints [VERIFIED]
- `lock_heartbeat.py:1-69` [VERIFIED]: docstring — locks `0x43415244` (harvest) y `0x43415244+1` (discovery); el advisory lock de SESION auto-libera en exit limpio, pero en crash duro/SIGKILL el backend PG mantiene la sesion muerta + su lock hasta que TCP keepalive/idle-reap dispara; ventana en que un restart pega `pg_try_advisory_lock==false` y `SystemExit`, orfanando el daemon. El modulo anade una capa de OBSERVABILIDAD (fila `scheduler_lease`, `last_heartbeat` bumped por timer); un sucesor lee el lease y distingue holder sano (beat reciente) de presunto-muerto (beat > TTL) -> orphan silencioso pasa a CRITICAL ruidoso. Explicitamente **NO** hace `pg_advisory_unlock` de sesion ajena (`:24-27`).
- `:88-89` [VERIFIED]: `_DEFAULT_HEARTBEAT_MIN=2`, `_DEFAULT_TTL_MIN=6` (3x heartbeat); overrides env `CARDEEP_LEASE_HEARTBEAT_MIN`/`CARDEEP_LEASE_TTL_MIN` (`:115-122`).
- `is_lease_stale` (`:141-163`) [VERIFIED]: predicado TTL puro; `None`->STALE (`:157-158`); frontera estricta `age>TTL` (`:162-163`).
- `record_heartbeat` (`:170-218`) [VERIFIED]: UPSERT best-effort `ON CONFLICT(lock_key)`; `started_at` se resetea SOLO cuando holder/pid cambian (sucesor) (`:201-205`); `UndefinedTable`->warn+False, **never raises** (`:212-218`).
- `check_and_clear_stale_lease` (`:259-302`) [VERIFIED]: diagnostico pre-acquire; log CRITICAL si stale; **NO** borra ni desbloquea (`:279-282`).
- `acquire_with_stale_retry` (`:309-338`) [VERIFIED]: `pg_try_advisory_lock`; si falla y el lease es stale, **retry UNA vez** (`:330-337`); `pg_try_advisory_lock` es el mutex atomico, jamas desplaza a un holder vivo (sin AS24 doble-productor, `:325-327`).
- `0054_scheduler_heartbeat.sql:28-34` [VERIFIED]: `CREATE TABLE IF NOT EXISTS scheduler_lease(lock_key BIGINT PK, holder TEXT, pid INT, started_at, last_heartbeat)`; additive/zero-risk; el daemon arranca byte-identico sin ella (`:15-19`).
- `scheduler.py:870-892` [VERIFIED]: `_lease_heartbeat_job(lock_key, holder)` — module-level picklable (el SQLAlchemy jobstore picklea jobs; una clausura sobre `_lock_conn` no se puede picklear), corre en su propia conexion autocommit efimera, `record_heartbeat`, best-effort.
- `scheduler.py:913` `_SCHEDULER_SINGLETON_LOCK=0x43415244=1128354372`; `:919` `acquire_with_stale_retry`; `:928` `record_heartbeat(..., holder="harvest")`; `:1032-1043` `add_job(_lease_heartbeat_job, minutes=heartbeat_interval_minutes(), args=[lock,"harvest"], misfire_grace_time=120)` [VERIFIED].

#### (b) Mecanismo al atomo
El mutex DURO sigue siendo el advisory lock de SESION (uno por host, clave 'CARD'). Encima, una fila `scheduler_lease` por `lock_key` lleva `last_heartbeat`, bumped cada 2 min por `_lease_heartbeat_job` en una conexion efimera **separada** (separada porque el jobstore picklea el job; el lease es dato plano, independiente de la sesion del lock). Un sucesor, antes de adquirir, corre `check_and_clear_stale_lease`: lee el lease; si `last_heartbeat > TTL=6min` (o NULL) loggea CRITICAL nombrando holder/pid muerto y devuelve True -> `acquire_with_stale_retry` reintenta `pg_try_advisory_lock` UNA vez. El retry es seguro: `pg_try_advisory_lock` es atomico, jamas toma un lock que una sesion VIVA retiene. "Auto-release" NO es takeover instantaneo — es "observable + retry en el siguiente arranque una vez PG reapa la sesion muerta".

#### (c) Costura ES->generico (INVERSA)
Esta capa ya es country-agnostica en codigo (cero literal ES). La costura es la **OPUESTA** a casi todas: el lock es **HOST-SINGLETON, no por-CC**. `0x43415244` ('CARD') es un entero fijo por host; **no hay shard de lease por-(rol,CC)**. A escala multi-pais en multiples hosts: o un host produce todo (cuello) o dos hosts sobre la misma DB colisionan en la unica clave. El lease es observabilidad sobre un mutex **sin dimension de pais/shard**. Ademas: 0054 debe estar APLICADA o la capa es inerte y el orphan invisible.

#### (d) Riesgo adversarial concreto
- El stack esta **CAIDO hoy** [VERIFIED scope + scheduler 'jobs registrados pero inertes']: hasta restart, cero heartbeat, todo lease stale-o-ausente, el bus/cover(CC) nunca tickea — el cerebro es teorico. Tras un SIGKILL del holder, el lock queda huerfano una ventana en que el restart pega `pg_try_advisory_lock==false` y `SystemExit` (`scheduler.py:921`) -> TODA la cadencia muere para TODOS los paises hasta que PG reapa la sesion.
- **Multi-host no-UE**: dos hosts, una DB, una clave -> el 2o host `SystemExit` permanente (falso orphan), un productor de 2o-pais nunca arranca; o, apuntando a DBs distintas, **cero garantia single-producer cross-host** -> AS24 doble-productor (la cicatriz que 4x-martilleo 138 dealers).
- El watchdog in-process es **ciego a su propia muerte de proceso**: si el daemon muere entero (host Windows 11 unico, riesgo real) las ~7 alertas zombie y el lease se congelan sin que nadie se entere hasta mirar a mano.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-15"></a>
### Faceta 15 · Pack de cadencia (8 jobs) + emision acotada/opt-in (anti-flood)
*Los 8 jobs + emisión opt-in/acotada (anti-flood a €0).*  ·  **v1:** Clúster G

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — Dos costuras: (1) los 8 intervalos son constantes globales [scheduler.py:95-116] sin dimension por-CC (15m/6h/24h/30m iberos); (2) la emision acotada/opt-in (CARDEEP_INQUISITION_EMIT + BATCH=200, scheduler.py:102-106) vive solo en el scheduler — el bus de decisiones (faceta 23) NO la hereda aun.
- **Fix exacto** — (a) Inyectar intervalos por-pais desde country.toml (harvest_interval_hours por fuente, faceta 29); el job lee el intervalo del loader por-CC. (b) El drain decision_request (faceta 26) reusa el patron EMIT/EMIT_BATCH: emision PENDING gateada + drenado acotado por lote. ES mantiene 15m/6h/24h/30m -> cadencia byte-identica.
- **Riesgo adversarial** — El scheduler lo advierte literalmente (102-106): a €0 la emision masiva inunda escalaciones no-auto-resolubles. Si el bus no hereda el opt-in, un pais sin capa-2 (faceta 25) escala cada duda a Claude -> rafaga inmanejable. Cadencia ES de 24h sobre mercado volatil cosecha rancio o sobre-cosecha (gasto/ban). Lock host-unico: sin particion por-CC a multi-host (cuello o colision).
- **Sellado multi-vía** — Via1: los 8 intervalos resolubles a country.toml; ES reproduce 15m/1h/6h/6h+30m/24h/24h/Nm/30m (golden). Via2 anti-flood: avalancha de PENDING -> el drain respeta EMIT_BATCH; opt-in apagado => 0 emision nueva. Via3 single-producer: 2o scheduler -> SystemExit por lock 0x43415244. Via4 vivo: los 8 jobs disparan bajo daemon (faceta 13), stagger +30m observado en traza.
- **Herramienta NEXT-LEVEL** — river — BSD-3-Clause — https://github.com/online-ml/river [VERIFIED NEXT-LEVEL.md:579]. Detectores de cambio online (ADWIN/Page-Hinkley) sobre el stream harvest_run de cada fuente -> cadencia auto-ajustable por-CC, EUR0 sobre PG. Cierra el gap que la biblia marca en scheduler.py:95-116 (NEXT-LEVEL.md:578). 2a-via ortogonal: ruptures (offline, BSD-2-Clause). Bandit por-fuente: MABWiser (Apache-2.0).

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) code_hints VERIFICADOS
- **Constantes de cadencia (constantes de modulo)** [VERIFIED pipeline/ops/scheduler.py:95-116]: `TICK_INTERVAL_MINUTES=15`, `INQUISITION_CADENCE_HOURS=6`, `INQUISITION_PROSECUTE_CADENCE_HOURS=6`, `INQUISITION_PROSECUTE_BATCH=200` (env), `INQUISITION_EMIT_BATCH=200` (env), `GESTIONADOR_DETECT_CADENCE_HOURS=24` (env), `CANONICAL_KEY_BACKFILL_CADENCE_HOURS=24` (env). `PRODUCT_STATS_REFRESH_MIN=30` [VERIFIED scheduler.py:851, env CARDEEP_STATS_REFRESH_MIN default "30"].
- **Emision OPT-IN/acotada** [VERIFIED scheduler.py:102-106] comentario literal: "at €0 mass emission floods un-self-resolvable escalations; prosecute-only (default) just drains whatever is PENDING." Emision NUEVA gateada por `CARDEEP_INQUISITION_EMIT=1`; prosecute-only por defecto.
- **Los 8 jobs** [VERIFIED scheduler.py:938-1058], todos con `max_instances=1, coalesce=True, replace_existing=True, misfire_grace_time` set:
  1. `heartbeat_tick` (938, interval 15m)
  2. `silence_watchdog_job` (953, 1h)
  3. `inquisition_cadence_job` (968, 6h)
  4. `inquisition_prosecute_job` (983, 6h, **stagger +30m** via `start_date=now+CADENCE_HOURS+30min` [VERIFIED scheduler.py:990])
  5. `gestionador_detect_job` (1002, 24h)
  6. `canonical_key_backfill_job` (1017, 24h)
  7. `_lease_heartbeat_job` (1032, `heartbeat_interval_minutes()`)
  8. `_refresh_product_stats_job` (1048, 30m)
  Conté 8 `add_job`: byte-cierto.

#### (b) El mecanismo al atomo
El scheduler es un `BlockingScheduler` con `SQLAlchemyJobStore` (faceta 13): cada job es una entrada durable con intervalo fijo. `max_instances=1` + el advisory lock host-singleton garantizan single-producer (cicatriz AS24). `coalesce=True` colapsa misfires (si el daemon estuvo caido, dispara una vez, no N). El **stagger +30m** [scheduler.py:987-990] hace que `inquisition_cadence` (encola) preceda a `inquisition_prosecute` (drena) cada ciclo de 6h. La **disciplina anti-flood** es central: a €0, emitir claims en masa inunda de escalaciones no-auto-resolubles; por eso la emision es opt-in y el drenado es acotado por batch=200.

#### (c) Costura ES->generico + fix exacto
Dos costuras: (1) **intervalos como constantes globales sin dimension por-CC** — un mercado volatil necesita cadencia distinta; (2) **el bus de decisiones (faceta 23) debe HEREDAR la emision acotada/opt-in** o un onboarding sin capa-2 escala cada duda a Claude.
**Fix:** (a) inyectar intervalos por-pais desde `country.toml` (`harvest_interval_hours` por fuente ya nombrado en el manifest de la faceta 29); el job lee el intervalo del loader por-CC. (b) el `decision_request` drain (faceta 26) reusa exactamente el patron `CARDEEP_INQUISITION_EMIT`/`EMIT_BATCH`: emision PENDING gateada y drenado acotado por lote, para que €0 no signifique inundar a Claude. ES mantiene 15m/6h/24h/30m en su manifest -> cadencia byte-identica.

#### (d) Riesgo adversarial concreto
- **El propio scheduler lo advierte** [scheduler.py:102-106]: "at €0 mass emission floods un-self-resolvable escalations". Si el bus NO hereda el opt-in, un onboarding de pais **sin capa-2** (faceta 25) escala cada duda de clasificacion/extraccion a Claude -> **rafaga de coste/tiempo inmanejable**.
- **Cadencia ES en mercado ajeno:** 24h de detect sobre un mercado volatil cosecha datos rancios; o demasiado frecuente -> gasto/superficie de ban innecesaria.
- **Single-producer a escala:** el lock es host-unico (faceta 13); a multi-host no hay particion por-CC -> o un host produce todo (cuello) o dos colisionan.

#### (e) Criterio de sellado + verificacion multi-via
- **Via 1 (intervalos trazables):** cada uno de los 8 intervalos resoluble a `country.toml`; ES reproduce 15m/1h/6h/6h+30m/24h/24h/Nm/30m exactos (golden de cadencia).
- **Via 2 (anti-flood probado):** test que inserta una avalancha de PENDING y confirma que el drain del bus respeta `EMIT_BATCH` (no desborda a Claude); el flag opt-in apagado => 0 emision nueva.
- **Via 3 (single-producer):** dos procesos scheduler -> el segundo recibe SystemExit por el advisory lock 0x43415244 (invariante preservado).
- **Via 4 (vivo):** los 8 jobs disparan realmente bajo daemon restart-supervisado (faceta 13); el stagger +30m observado en la traza (cadence precede prosecute).

#### (f) Herramienta NEXT-LEVEL
**river** — BSD-3-Clause, https://github.com/online-ml/river [VERIFIED NEXT-LEVEL.md:579]. La biblia marca scheduler.py:95-116 como "cadencias = constantes de modulo estaticas sembradas una vez; sin realimentacion del delta observado" [NEXT-LEVEL.md:578]. river aporta **detectores de cambio ONLINE (ADWIN, Page-Hinkley)** que corren incrementalmente sobre el stream de tasa-de-cambio (`harvest_run` filas cambiadas/run) de cada fuente: cuando una fuente se aplana sube `harvest_interval_hours`, cuando churnea lo baja -> cadencia **auto-ajustable por-CC**, EUR0 sobre PG, memoria sublineal. Materializa el "self-tuning por volatilidad como palanca futura" que la faceta declara. Verificacion (NEXT-LEVEL.md:582): (a) serie sintetica con cambio de regimen -> ADWIN dispara en el punto correcto; (b) 2a via ortogonal `ruptures` (offline, BSD-2-Clause) ubica el mismo change-point; (c) adversarial: churn ciclico dia/noche no debe oscilar el intervalo (anti-flapping). Alternativa de bandit por-fuente: MABWiser (Apache-2.0).

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-16"></a>
### Faceta 16 · Gate G1 de identidad: ensanche del 6o-blocker (ES-lock de complete.py)
*El 6º-blocker: ^CDP-ES- → ^CDP-([A-Z]{2})- y quitar el xfail.*  ·  **v1:** Clúster A

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — complete.py hard-codea ES en 3 costuras: _CDP_CODE_RE :89 (^CDP-ES-), _PROVINCE_RE :73 (01-52), y _resolve_recipe_path :305/:309 (glob 'countries/ES', bypasea paths.recipe_root). El patron ancho ya existe verbatim en paths.py:30 (^CDP-([A-Z]{2})-). El fix es de motor una vez: widening del CC + province-validator inyectado desde country.toml + recipe path por country_of_cdp.
- **Fix exacto** — (1) _CDP_CODE_RE :89 '^CDP-ES-' -> '^CDP-([A-Z]{2})-' (la cola [0-9]{2} sirve para DE). (2) _PROVINCE_RE :73 inyectado desde country.toml (ES declara 01-52). (3) _resolve_recipe_path :305/:309 'ES' -> paths.recipe_root(country_of_cdp(cdp_code)). (4) _NATIONAL_KINDS default-con-override. (5) Quitar el xfail de test_country_golden.py:287. DISTINTO de faceta 17 (gramatica FR/IT toca mint_code).
- **Riesgo adversarial** — Hoy ningun CDP-DE-* pasa G1 (xfail vivo test_country_golden.py:287) -> INCOMPLETE perpetuo -> ningun dealer extranjero sella pese a coexistir el esquema (piloto DE). DE 2-digitos cabe; FR/IT no (Corcega 2A/2B, depts 53-95, ultramar 971-976: faceta 17). Si se ensancha solo el CC y _PROVINCE_RE queda 01-52 hardcodeado, un Land DE >52 es rechazado: el province-validator debe viajar inyectado.
- **Sellado multi-vía** — (1) Quitar xfail :287 y test_accepts_foreign_country_segment PASA (CDP-DE-28 / CDP-FR-75 aceptados). (2) test_country_coexistence ES byte-identico (:107) intacto, CDP-DE coexiste. (3) Multi-via: golden ES con _PROVINCE_RE inyectado reproduce 01-52; manifest ISO 3166-2 reproduce caps ES sin regresion; CDP-DE-* pasa G1 e2e; _resolve_recipe_path resuelve countries/DE/** sin tocar ES.
- **Herramienta NEXT-LEVEL** — pycountry (LGPL-2.1, EUR0) https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:527-533] — ISO 3166-2 subdivision authority: el province-validator (01-52 ES-shape) se deriva de count+width de subdivisiones por pais en build-time (seal manifest), reproduce 52 (ES) y pina DE=16/FR=101/IT=107/MX=32/JP=47. Alt permisiva: iso3166 (MIT) + raw iso-codes JSON.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### Mecanismo al atomo [VERIFIED]
- **complete.py:89** `_CDP_CODE_RE = re.compile(r"^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$")` — hard-codea `CDP-ES`, exige provincia de 2 digitos y cola Crockford-base32 de 8 chars (clase `[0-9A-HJKMNP-TV-Z]` = sin I,L,O,U). check_g1 la aplica en :145.
- **complete.py:73** `_PROVINCE_RE = re.compile(r"^(0[1-9]|[1-4][0-9]|5[0-2])$")` — valida 01-52 (las provincias ES). check_g1:142 la aplica salvo national kinds.
- **complete.py:83-85** `_NATIONAL_KINDS = frozenset({"subasta","plataforma","oem_vo_portal","importador"})` — kinds que llevan provincia NULL legitima (el '00' vive solo en el cdp_code, no en province_code; comentario :75-82). check_g1:141 calcula `is_national = row.get("kind") in _NATIONAL_KINDS and prov_str is None`.
- **complete.py:_resolve_recipe_path** (293-313): glob `(root/"countries"/"ES").glob(f"**/{cdp_code}/recipe.yaml")` (:305) + fallback flat `root/"countries"/"ES"/"recipes"/f"{cdp_code}.yaml"` (:309) — 'ES' hard-codeado, BYPASEANDO paths.recipe_root.
- **El patron ancho YA existe verbatim** en paths.py:30 `_CDP_COUNTRY_RE = re.compile(r"^CDP-([A-Z]{2})-")` y paths.country_of_cdp (55-63) ya deriva el CC de cualquier codigo.
- **Prueba viva del blocker** [VERIFIED]: test_country_golden.py:278-292 `test_accepts_foreign_country_segment` esta marcado `pytest.xfail` (:287, strict) con el mensaje *"complete.py:_CDP_CODE_RE still hard-codes '^CDP-ES-' (hidden 6th blocker not yet widened to '^CDP-([A-Z]{2})-'). G1 would silently reject every foreign-country entity"* (:288-290) — AUTO-FLIPS a XPASS el instante en que se ensancha. test_country_coexistence.py ya prueba el minteo CDP-DE-* distinto + tail-identico (:156-189) y la byte-identidad ES (:107).

#### [VERIFIED — correccion a la faceta]
La faceta atribuye a test_country_coexistence.py un *skip 'still hard-codes CDP-ES'*. VERIFICADO que ese texto exacto es el **xfail de test_country_golden.py:282,288**, NO un skip de coexistence: test_country_coexistence solo tiene DB-skips por pg-inalcanzable / 0053-no-aplicado (:28-30). El blocker vivo es el xfail de golden.

#### Costura ES->generico (fix de MOTOR, una sola vez)
1. **_CDP_CODE_RE**: `^CDP-ES-` -> `^CDP-([A-Z]{2})-` (identico a paths.py:30; la cola `[0-9]{2}` SIRVE para DE, cuyas subdivisiones son de 2 digitos).
2. **_PROVINCE_RE**: el validador 01-52 viaja inyectado desde country.toml (ES declara 01-52 en su manifest).
3. **_resolve_recipe_path**: 'ES' -> `paths.recipe_root(country_of_cdp(cdp_code))`.
4. **_NATIONAL_KINDS**: default-con-override por pais.
Es DISTINTO de la faceta 17 (redisreno de gramatica FR/IT alfa/3-digitos): aqui el ancho `[0-9]{2}` BASTA para DE; FR/IT exigen cambiar mint_code, no solo el regex de G1.

#### Riesgo adversarial concreto
Hoy NINGUN CDP-DE-* pasa G1 (xfail vivo) -> derive_verdict=INCOMPLETE para siempre -> ningun dealer extranjero sella aunque el esquema ya coexista (probado por el piloto DE en coexistence). DE: provincia 2-digitos cabe en `[0-9]{2}`, solo falta ensanchar el CC. FR/IT: NO bastan (Corcega 2A/2B, depts 53-95, ultramar 971-976, ISTAT>99) — eso es faceta 17, no esta. Si se ensancha SOLO el CC pero se deja _PROVINCE_RE 01-52 hardcodeado, un Land DE cuyo codigo exceda 52 es rechazado -> por eso el province-validator DEBE viajar inyectado. Ruido: un cdp_code malformado de pais valido (CDP-DE-99-... con DE de 16 Lander) debe seguir fallando contra el rango DE declarado.

#### Sellado + verificacion multi-via
1. **Quitar el xfail** de test_country_golden.py:287 y que `test_accepts_foreign_country_segment` PASE (CDP-DE-28-... y CDP-FR-75-... aceptados por el regex ancho :291-292).
2. **No regresion ES**: test_country_coexistence ES byte-identico (:107) intacto; CDP-DE coexiste.
3. **Multi-via**: golden ES (_PROVINCE_RE inyectado reproduce 01-52 exacto); manifest ES derivado de ISO 3166-2 reproduce caps/width ES sin regresion; un CDP-DE-* pasa G1 end-to-end contra entity DE sintetica; _resolve_recipe_path resuelve countries/DE/** sin tocar ES.

#### Herramienta NEXT-LEVEL
**pycountry** (LGPL-2.1) https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:527-533, "ISO 3166-2 subdivision authority"]: el validador de provincia (hoy _PROVINCE_RE 01-52, ES-shape) se deriva de los datos de subdivision ISO 3166-2 por pais (count + code-width), alimentando un seal manifest por-CC en build/config-time (no hot-path, LGPL data-use no-issue). Reproduce el cap ES (52) y pina DE=16 / FR=101 / IT=107 / MX=32 / JP=47 contra una 2a fuente. Alternativa estricta-permisiva: iso3166 (MIT, countries-only) + el raw iso-codes subdivision JSON.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-17"></a>
### Faceta 17 · Redisreno de la gramatica del cdp_code (subdivision FR/IT alfa/3-digitos)
*Ancho+alfabeto del slot {NN}: 2A/2B, 971-976, ISTAT>99 no caben en [0-9]{2}.*  ·  **v1:** Clúster B

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — No es 'swap de regex': es cambiar la GRAMATICA (ancho+alfabeto) de un codigo INMUTABLE. mint_code [VERIFIED codes.py:44-53] acepta cualquier province_code pero G1 lo valida como [0-9]{2} 01-52 [VERIFIED complete.py:73,89 _CDP_CODE_RE hardcodea CDP-ES y [0-9]{2}]. paths.py:30 ya parsea el CC generico pero NO el slot {NN}. FR (2A/2B alfa, 971-976 3-digit, 53-95) e IT (sigla/ISTAT>99) no caben.
- **Fix exacto** — Spec de subdivision por-pais (ancho+alfabeto+centinela) en country.toml consumida por AMBOS mint_code (emision) y _CDP_CODE_RE/_PROVINCE_RE (validacion). ES: width=2, digitos, 01-52, centinela '00' -> byte-identico (golden). FR: width<=3, alfanumerico (2A/2B), incl. 971-976. Formato canonico CDP-{CC}-{NN}-{8} preservado; ancho acotado. Acopla con faceta 32: congelar+validar la gramatica ANTES del primer mint (codigo inmutable).
- **Riesgo adversarial** — Corsica 2A/2B (alfa), deptos FR 53-95 (>52), ultramar 971-976 (3 digitos), IT ISTAT>99: ninguno mintea ni pasa G1 bajo [0-9]{2}. Codigo inmutable -> gramatica equivocada no se corrige sin re-mintear, orfanando gestion/vehicle_event append-only + ledger (faceta 32). Dept 3-digit truncado a 2 colisiona departamentos.
- **Sellado multi-vía** — Sello: golden ES byte-identico (mint+validate); fixtures FR/IT (2A/2B, 971, ISTAT-110) minteamn y pasan G1 bajo su spec; round-trip mint_code(grammar)<->_CDP_CODE_RE(grammar) por CC; adversarial subdivision fuera de gramatica rechazada al mint (fail-closed) no truncada; anti-colision dos subdivisiones reales nunca al mismo {NN}.
- **Herramienta NEXT-LEVEL** — pycountry (LGPL-2.1, EUR0) https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:527-533]: ISO 3166-2 (Debian iso-codes) vuelve conteo/ancho/alfabeto de subdivisiones en DATA para un seal-manifest por-pais (cubre FR 2A/2B+971-976, IT). Uso build/config-time (no hot-path) -> LGPL non-issue; alternativa permisiva iso3166 (MIT) + raw iso-codes JSON. Empareja con Hypothesis (faceta 31).

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) Verificacion de code_hints [VERIFIED]
- [VERIFIED services/api/codes.py:44-53] `mint_code(*, province_code, digest, country_code="ES")` -> `f"CDP-{country_code}-{province_code}-{_base32(digest)}"`. **Acepta cualquier string** como province_code, pero el invariante asume `[0-9]{2}`. `DEFAULT_COUNTRY="ES"` [:24]. Es "the ONE home of the prefix literal".
- [VERIFIED codes.py:35-41] `_base32` = 8 chars Crockford (`0123456789ABCDEFGHJKMNPQRSTVWXYZ`, sin I,L,O,U).
- [VERIFIED pipeline/complete.py:73] `_PROVINCE_RE = re.compile(r"^(0[1-9]|[1-4][0-9]|5[0-2])$")` — Espana 01-52 EXACTO.
- [VERIFIED complete.py:89] `_CDP_CODE_RE = re.compile(r"^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$")` — hardcodea el literal `CDP-ES` **Y** constrine la subdivision a `[0-9]{2}` (solo digitos, 2 chars).
- [VERIFIED complete.py:83-85] `_NATIONAL_KINDS = {subasta, plataforma, oem_vo_portal, importador}`; el centinela '00' vive "only in the CDP-ES-00-* code, NOT in the province_code column" [:76-77].
- [VERIFIED pipeline/paths.py:30] `_CDP_COUNTRY_RE = re.compile(r"^CDP-([A-Z]{2})-")` — ya generico en el CC, pero **solo** parsea el CC, NO el slot {NN}.

#### (b) Mecanismo al atomo
La gramatica es `CDP-{CC}-{NN}-{8 Crockford-base32}`. El slot {NN} se **emite** por interpolacion (mint_code acepta cualquier string) pero se **valida** por G1 `_CDP_CODE_RE` como exactamente `[0-9]{2}` y por `_PROVINCE_RE` como 01-52. El codigo es **INMUTABLE** (codes.py:1-15 docstring) y es la dedup-identity persistida.

#### (c) Costura ES->generico + fix exacto
NO es un "swap de regex" como dice el country_pack: es cambiar la **GRAMATICA** (ancho+alfabeto) de un codigo inmutable. La faceta 16 (ensanche G1) solo ensancha el validador a `[0-9]{2}` generico — suficiente para paises de cola byte-identica (DE). Pero FR/IT exigen **alfabeto/ancho distinto**:
- FR: departamentos 53-95 (fuera de 01-52), **Corsica 2A/2B (ALFANUMERICO)**, ultramar 971-976 (**3 digitos**).
- IT: provincias por **sigla de 2 letras** o ISTAT > 99 (hasta ~111).
Ninguno cabe en `[0-9]{2}`. **Fix:** una **spec de subdivision por-pais** (ancho + alfabeto + centinela nacional) declarada en country.toml y consumida por AMBOS: mint_code (emision) y `_CDP_CODE_RE`/`_PROVINCE_RE` (validacion). ES declara width=2, alfabeto=digitos, rango 01-52, centinela '00' -> salida byte-identica (golden). FR declara width<=3, alfabeto alfanumerico (2A/2B), rangos incl. 971-976. El formato canonico `CDP-{CC}-{NN}-{8}` se preserva; solo varia la spec de {NN}. El ancho debe acotarse para que el codigo siga parseable. **Acopla con faceta 32 (gate de congelacion):** como el codigo es inmutable, la gramatica debe **congelarse+validarse ANTES del primer mint**.

#### (d) Riesgo adversarial concreto
Corsica 2A/2B (alfa), deptos FR 53-95 (>52), ultramar 971-976 (3 digitos), IT ISTAT>99: **NINGUNO** mintea ni pasa G1 bajo `[0-9]{2}`. Y como el codigo es inmutable, una gramatica equivocada **no se corrige sin re-mintear** -> orfana toda la historia append-only (gestion_item/gestion_transition/vehicle_event) y el ledger (faceta 32). Un dept de 3 digitos truncado a 2 **colisiona** departamentos distintos en el mismo {NN}.

#### (e) Sellado + verificacion multi-via
- **Sello:** (i) golden ES: todo CDP-ES-NN-XXXXXXXX existente mintea+valida byte-identico; (ii) fixtures FR/IT: 2A/2B, 971, ISTAT-110 minteamn **Y** pasan G1 bajo su grammar spec; (iii) round-trip: `mint_code(grammar)` re-parseado por `_CDP_CODE_RE(grammar)` de ese CC; (iv) adversarial: una subdivision fuera de la gramatica declarada se **rechaza al mint** (fail-closed), no se trunca en silencio; (v) anti-colision: dos subdivisiones reales distintas nunca mapean al mismo {NN}.
- **Multi-via:** 1a golden ES; 2a round-trip mint<->validate por CC; 3a adversarial de truncado/colision.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**pycountry** (LGPL-2.1, EUR0) — https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:527-533, cluster identity-vehicle]. Empaqueta el dataset Debian iso-codes (ISO 3166-2): el **conteo, ancho y alfabeto** de las subdivisiones de primer nivel de cada pais se vuelven **DATA**, alimentando un seal-manifest por-pais en vez de centinelas con forma-ES. Cubre FR 2A/2B + 971-976, provincias IT, etc. de forma autoritativa. **Caveat de licencia:** uso **build/config-time** (autorar la grammar spec, NO hot-path) -> LGPL data-use es non-issue; alternativa estricto-permisiva: `iso3166` (MIT, paises) + raw iso-codes JSON (subdivisiones). Empareja con Hypothesis (faceta 31) para probar que la gramatica se sostiene para todo input que el pack pueda producir.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-18"></a>
### Faceta 18 · Gates G2/G3/G4 de completitud (inventario/receta/servido) + ladder de extraccion
*El ladder next_data→…→llm_local (rung dormante) + G5 inexistente + glob ES-locked.*  ·  **v1:** Clúster I

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — Tres costuras: (1) _resolve_recipe_path [complete.py:305/309] hardcodea el glob 'countries/ES/**' y el flat 'countries/ES/recipes', bypaseando paths.recipe_root(country_of_cdp(...)) -> rompe la resolucion de receta para no-ES; (2) el ladder de extraccion next_data|jsonld|css|llm_local [recipe_schema.py:67] tiene el rung llm_local DORMANTE (0 IA local en pipeline/), asi que G3 [complete.py:235-290] no produce recipe_kind!='none' para sitios que exigen JS-render mas alla de css -> INCOMPLETE estructural por tecnologia, no por datos; (3) check_g5_stub [complete.py:452-466] referencia pipeline/g5_check.py que NO existe (Glob vacio), manteniendo derive_verdict en INCOMPLETE.
- **Fix exacto** — (1) Reemplazar el literal 'countries/ES' de _resolve_recipe_path por paths.recipe_root(country_of_cdp(cdp_code)) / paths.recipes_flat_dir(...) -el patron ancho ya existe verbatim en paths.py:30,55-63-; ES byte-identico (default ES). (2) Activar el rung estructurado €0 (extruct) para subir recall sin LLM y cablear auto-resintesis de field_map (Crawl4AI generate_schema, replay determinista) + render Tier-1 (patchright) para la cola larga JS-only, con escalada a Claude si parse_loss>0. (3) Construir g5_check.py country-agnostico (GONE subset prev, NEW interseccion vacia, odometro monotono, D_after=D_before+NEW-GONE) o declarar G5 pendiente honestamente; hoy el sello es G1-G4+frescura declarado como tal.
- **Riesgo adversarial** — Los portales de un pais nuevo que exigen llm_local/render dinamico nunca dan recipe_kind!='none' => G3 jamas pasa => el pais no sella por razon TECNOLOGICA aunque los datos esten (la cola larga JS-only es el cuello). El glob 'countries/ES' busca la receta de un CDP-DE-* bajo el arbol ES -> no la encuentra (esta en countries/DE/...) y la sub-senal git de G3 da basura. Con g5=None, derive_verdict retorna INCOMPLETE para CUALQUIER pais; declarar 'sellado' sin G5 seria maquillaje. Una receta que parsea pero mis-cuenta mantiene recipe_kind!='none' y pasa G3 degradando en silencio.
- **Sellado multi-vía** — Sellado = G2/G3/G4 resuelven por country_of_cdp(cdp_code) (cero literal ES), el ladder cubre el pais o declara su limite tecnologico honestamente, G5 construido o pendiente declarado, ES byte-identico. Multi-via: (1) golden de paridad ES (mismo verdict por-entidad tras el cambio a paths.*); (2) coexistencia: un CDP-DE-* con receta en countries/DE/ es ENCONTRADO por _resolve_recipe_path (hoy NO lo es), rojo->verde; (3) la receta auto-sintetizada se valida por el MISMO VAM ortogonal (declared vs fetched vs parsed), no se auto-aprueba; (4) adversarial: un sitio JS-only/anti-bot FALLA la re-sintesis y ESCALA (decision_request), nunca sella basura; sin schema.org cae al fill-rate, no a FALSE-VERIFIED.
- **Herramienta NEXT-LEVEL** — Crawl4AI JsonCssExtractionStrategy.generate_schema (Apache-2.0, €0) https://github.com/unclecode/crawl4ai [VERIFIED NEXT-LEVEL.md:237-243] — cierra el rung llm_local dormante: LLM local emite UNA vez un schema CSS reusable, extraccion determinista €0 en runtime, re-verifica con sample-verify-delete y escala a Claude si parse_loss>0. Complementos: extruct (BSD-3-Clause, €0) https://github.com/scrapinghub/extruct [VERIFIED NEXT-LEVEL.md:285-291] sube el recall estructurado €0 (JSON-LD+Microdata+RDFa+OpenGraph) elevando G3 antes de gastar token; patchright-python (Apache-2.0, €0) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python [VERIFIED NEXT-LEVEL.md:253-259] render Tier-1 para portales JS-only donde css no alcanza.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) Verificacion de code_hints [VERIFIED]
- **[VERIFIED pipeline/complete.py:92]** `_FIELD_INTEGRITY_FLOOR = 0.98`.
- **[VERIFIED pipeline/complete.py:155-228]** `check_g2`: `D = count(vehicle available)` (188-191), `D_valid = count(... deep_link IS NOT NULL)` (196-205), `field_integrity = d_valid/d_landed` (218); PASA si `d_landed>=1 AND field_integrity>=0.98` (221-228). `s_declared` reservado a None (210) — la VAM D=S no es columna; se difiere a β-complete.
- **[VERIFIED pipeline/complete.py:235-290]** `check_g3`: chequeo PRIMARIO DB `v_dealer_recipe.recipe_kind` (259-267); `recipe_kind=='none' => FAIL` (275-276); `'connector'|'per_dealer' => TRUE` (278). Sub-senal git (283-288) es **solo diagnostica** (G3 lo decide `recipe_kind`, no git).
- **[VERIFIED pipeline/complete.py:293-313]** `_resolve_recipe_path`: **glob hardcodeado** `(root / "countries" / "ES").glob(f"**/{cdp_code}/recipe.yaml")` (305) + fallback flat `countries/ES/recipes/<cdp_code>.yaml` (309). **Bypasea `paths.recipe_root(country_of_cdp(...))`** — el literal 'ES' rompe la resolucion para no-ES.
- **[VERIFIED pipeline/complete.py:382-445]** `check_g4`: `v_dealer_resolved` (397-405) + `served_count` con **LEFT JOIN `v_canonical_vehicle`** + COALESCE al `vehicle_ulid` crudo (423-431) — LEFT (no inner) para no fallar G4 en entidades cuyo inventario esta fuera del cluster vam_verified (subastas/rentacar).
- **[VERIFIED pipeline/complete.py:452-466]** `check_g5_stub` retorna `(None, "G5_deferred:second_harvest_not_yet_run")`; el docstring referencia `pipeline/g5_check.py::verify_delta_events` (457). **[VERIFIED Glob `pipeline/g5_check.py` = No files found]** — el modulo NO existe.
- **[VERIFIED pipeline/complete.py:473-497]** `derive_verdict`: `any(g is None) => INCOMPLETE` (489-490); con None de G5, ninguna entidad alcanza COMPLETED real.
- **[VERIFIED pipeline/recipe_schema.py:64-69]** `Parsing.engine: str = "next_data"` con ladder en docstring *"structured (extruct/__NEXT_DATA__, cost 0) -> css selectors -> llm_local"* (65-66) y enum `next_data | jsonld | css | llm_local` (67). El rung **`llm_local` esta dormante** (es solo un valor de enum; faceta 25 confirma 0 IA local en `pipeline/`).

#### (b) El mecanismo al atomo
El sellado por-entidad encadena gates DB-equivalentes:
- **G2** mide validez de inventario: `field_integrity = D_valid/D >= 0.98`, con `D` = filas available y `D_valid` = filas con `deep_link` no nulo.
- **G3** exige una receta durable: `v_dealer_recipe.recipe_kind != 'none'`, donde `recipe_kind` es `connector` (entidad sentinel-00 de plataforma, migracion 0029), `per_dealer` (AS24, `recipe_version` no nulo) o `none`. La receta nace del **ladder de extraccion** `next_data -> jsonld -> css -> llm_local`: si un sitio exige render JS mas alla de css, **ningun engine produce receta** porque `llm_local` esta dormante.
- **G4** prueba servibilidad: existe en `v_dealer_resolved` y `served_count>0` via `v_canonical_vehicle` (LEFT JOIN dedup cross-source).
- **G5** (vecina, deferred): prueba de delta — su modulo `g5_check.py` no existe, asi que `derive_verdict` mantiene INCOMPLETE estructural.

#### (c) La costura ES->generico con su fix exacto
**Costura 1 (resolucion de receta ES-locked):** `_resolve_recipe_path` (305/309) hardcodea `countries/ES` y bypasea `paths.py`. **Fix:** reemplazar el literal por `paths.recipe_root(country_of_cdp(cdp_code))` / `paths.recipes_flat_dir(country_of_cdp(cdp_code))` — el patron ancho ya existe verbatim en `paths.py:30,55-63`; ES queda byte-identico (default 'ES').

**Costura 2 (ladder con rung muerto):** G3 depende de un escalon `llm_local` que no existe en codigo. Para un pais cuyos portales exigen JS-render o auto-sintesis de receta mas alla de css, G3 falla por **razon tecnologica, no de datos**. **Fix:** activar el rung €0 estructurado primero (subir recall sin LLM) y, para la cola larga JS-only, cablear la auto-resintesis de `field_map` y el render Tier-1 — cerrando el peldano que hoy deja al sitio en FAILED honesto sin ruta de recuperacion.

**Costura 3 (G5 inexistente):** `g5_check.py` no existe (verificado). **Fix:** construir `g5_check.py` country-agnostico (GONE subset prev, NEW interseccion vacia, odometro monotono, `D_after=D_before+NEW-GONE`) y decidir si el sello de pais lo exige o lo declara pendiente honestamente. Hoy el sello es G1-G4+frescura, declarado como tal — sin maquillaje.

#### (d) El riesgo adversarial concreto (DE/FR/IT/PT/no-UE/ruido)
- **G3 por tecnologia ausente:** los portales de un pais nuevo que exigen `llm_local`/render dinamico nunca producen `recipe_kind != 'none'` => G3 jamas pasa => el pais **no sella por una razon tecnologica**, aunque los datos esten. La cola larga de 'webs cutres' JS-rendered es el cuello.
- **Glob ES bypaseando paths:** `_resolve_recipe_path` busca bajo `countries/ES` para un `CDP-DE-*`; la receta del dealer aleman (en `countries/DE/...`) **no se encuentra** => la sub-senal git de G3 da basura y, si alguna ruta dependiera de ella, rompe G3 para no-ES.
- **G5 stub => COMPLETED imposible:** con `g5=None`, `derive_verdict` retorna INCOMPLETE para CUALQUIER pais; declarar 'sellado' sin G5 sin decirlo seria maquillaje. Para todo pais nuevo el sello queda en G1-G4+frescura hasta una 2a cosecha + `g5_check`.
- **Ruido de receta-rot:** una receta que 'parsea' pero mis-cuenta (campos a NULL, estructura mutada) puede mantener `recipe_kind != 'none'` y pasar G3 mientras degrada en silencio — sin senal de drift.

#### (e) Criterio de sellado + verificacion multi-via
**Sellado:** G2/G3/G4 resuelven por `country_of_cdp(cdp_code)` (cero literal ES en la resolucion de receta); el ladder cubre el pais (rung estructurado €0 + ruta de recuperacion para JS-only) o se declara la limitacion tecnologica honestamente; G5 construido o pendiente declarado; ES byte-identico.
**Multi-via:**
1. **Golden de paridad ES:** los gates sobre el corpus ES reproducen el mismo verdict por-entidad (cero regresion) tras cambiar el glob a `paths.*`.
2. **Via de coexistencia:** un `CDP-DE-*` con receta en `countries/DE/...` es **encontrado** por `_resolve_recipe_path` (hoy NO lo es); test rojo->verde.
3. **Via independiente (ladder):** una receta auto-sintetizada se valida por el MISMO VAM ortogonal (declared del oraculo vs fetched vs parsed) que sella las recetas originales — la reparacion NO se auto-aprueba con su propio parser.
4. **Via adversarial (JS-only):** un sitio que cambio a anti-bot/JS-only debe FALLAR la re-sintesis y ESCALAR (`decision_request`), nunca sellar basura; y un sitio sin schema.org cae al contrato de fill-rate, no a FALSE-VERIFIED.

#### (f) Herramienta NEXT-LEVEL que la eleva a nivel inalcanzable
**Crawl4AI** (`JsonCssExtractionStrategy.generate_schema`) (Apache-2.0, €0) — https://github.com/unclecode/crawl4ai — cierra el rung `llm_local` dormante: ante un sitio sin receta, el LLM (local Qwen GGUF) emite **una vez** un schema CSS/XPath REUSABLE y la extraccion corre deterministica en runtime SIN LLM; re-verifica con el harness sample-verify-delete y escala a Claude solo si no alcanza `parse_loss==0` [VERIFIED NEXT-LEVEL.md:237-243]. Complementos: **extruct** (BSD-3-Clause, €0) — https://github.com/scrapinghub/extruct — sube el recall del peldano estructurado €0 (JSON-LD+Microdata+RDFa+OpenGraph) ANTES de gastar un token, levantando la tasa de G3 [VERIFIED NEXT-LEVEL.md:285-291]; y **patchright-python** (Apache-2.0, €0) — https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python — render Tier-1 Chrome-shaped para los portales JS-only donde css no alcanza, el escalon que hoy deja G3 clavado [VERIFIED NEXT-LEVEL.md:253-259]. Juntos convierten 'G3 falla por tecnologia ausente' en 'el ladder tiene un rung €0 ejecutable para cada forma de sitio'.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-19"></a>
### Faceta 19 · derive_verdict + prueba de delta G5 (el hueco g5_check.py)
*El gate G5 ausente (g5_check.py inexistente): la ley de conservación D_after=D_before+NEW-GONE como contrato.*  ·  **v1:** Clúster I

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — derive_verdict y check_g5_stub son country-agnostic: operan sobre cdp_code generico, sin literal ES [VERIFIED complete.py:473-497,:452-466]. El hueco es de COMPLETITUD (modulo g5_check.py ausente), no de pais. La ley de conservacion D_after=D_before+#NEW-#GONE es universal (no tiene parametro de pais), por lo que el fix es generico por construccion; el unico seam por-CC es la DECISION de si cover(CC) exige G5 para sellar o lo declara pendiente honestamente.
- **Fix exacto** — Construir pipeline/g5_check.py::verify_delta_events country-agnostic que, sobre la ventana de la 2a cosecha: (1) GONE subset prev_available; (2) NEW interseccion prev_links = vacio; (3) odometro monotono; (4) D_after == D_before + #NEW - #GONE. Codificar las 4 invariantes como CONTRATO EJECUTABLE fail-closed (Great Expectations/Pandera) que g5_check corre y que NIEGA g5_delta=True ante violacion. Solo entonces quitar el None->INCOMPLETE. cover(CC) decide por-CC si el sello exige G5 o lo declara pendiente (sin maquillar).
- **Riesgo adversarial** — Para cualquier pais nuevo el sello queda en G1-G4+frescura hasta la 2a cosecha — esto NO es bug, es honestidad; el riesgo es declarar 'sellado' sin G5 sin decirlo (maquillaje). DE/FR: si el portal rota inventario mas rapido/lento que ES, una ventana de 2a cosecha mal dimensionada hace NEW interseccion prev != vacio falsamente (re-listado con id nuevo) -> G5 falla por dinamica de mercado, no por datos. Odometro monotono: mercados con km en millas (no-UE) o reset fraudulento rompen la invariante. No-UE sin 2a cosecha programada (stack caido, faceta 13) -> G5 jamas corre.
- **Sellado multi-vía** — Multi-via: (1) CONTRATO fail-closed — cada invariante es una expectativa versionada; violacion => el build niega g5_delta. (2) GOLDEN ES — sobre un par de cosechas ES conocido las 4 invariantes pasan byte-identico. (3) PROPERTY-BASED (Hypothesis) — generar deltas NEW/GONE aleatorios y probar que la conservacion D_after=D_before+#NEW-#GONE se mantiene, y que un delta inyectado-roto FALLA. (4) 2a VIA — el conteo de vehicle_event (append-only) recomputado por SQL directo == el balance D_after-D_before.
- **Herramienta NEXT-LEVEL** — Great Expectations / Pandera (Apache-2.0 / MIT, EUR0) https://github.com/great-expectations/great_expectations [VERIFIED NEXT-LEVEL.md:167,:19] — contrato de datos ejecutable, versionado y fail-CLOSED que codifica las 4 invariantes de conservacion G5 como expectativas; convierte una precondicion estadistica oculta en invariante probado. Alt: Hypothesis (MPL-2.0, :320) para las pruebas property-based de la ley de conservacion.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### Mecanismo al atomo
G5 esta estructuralmente DEFERRED: `check_g5_stub(cdp_code)` devuelve SIEMPRE `(None, 'G5_deferred:second_harvest_not_yet_run')` [VERIFIED complete.py:452-466]. `derive_verdict` trata cualquier None como INCOMPLETE: `if any(g is None for g in all_gates): return 'INCOMPLETE'` [VERIFIED :488-490]; COMPLETED solo si `g1 ^ g2 ^ g3 ^ g4 ^ g5` y `is_fresh`; STALE si todos los gates fueron TRUE pero la frescura expiro [VERIFIED :482-497]. `compute_completion` persiste `g5_delta=False` y verdict=INCOMPLETE mientras G5 sea stub [VERIFIED :527-538]; `upsert_completion` usa INSERT..ON CONFLICT MVCC-safe y preserva `completed_at` como watermark [VERIFIED :564-625].

**Consecuencia atomica:** NINGUNA entidad de NINGUN pais alcanza COMPLETED real mientras G5 sea stub — el sello hoy es honestamente G1-G4+frescura, declarado como tal [VERIFIED docstring :51-52], NO maquillado.

**La prueba ausente:** G5 exige una 2a cosecha (segundo `ingest_dealer`) + el modulo `pipeline/g5_check.py::verify_delta_events(conn, cdp_code)` que NO existe [VERIFIED :54-57,:457], el cual debe verificar sobre `vehicle_event` de la ventana del 2o run: `GONE subset prev_available`, `NEW interseccion prev_links = vacio`, odometro monotono y la CONSERVACION `D_after == D_before + #NEW - #GONE` [VERIFIED :459-460].

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-20"></a>
### Faceta 20 · Sellador de intervalo: estratificacion + matriz de captura
*La matriz de captura: estrata provincia×segmento ES-shaped → grano de subdivisión por-CC.*  ·  **v1:** Clúster E

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — La geometria es 100% ES-shaped: '52 x 4' esta hardwired en el docstring, el grano provincia es CHAR(2) codigos INE 01-52, y `_SEGMENT` colapsa valores `entity_kind` especificos de ES en 4 segmentos ES. El DSN hardcodeado en :17 ademas clava :5433/cardeep. Para DE (16 Laender, o 400+ Kreise), FR (101 departements incl. Corsica 2A/2B + ultramar 971-976), IT (107 province), MX (32), JP (47) el NUMERO Y el ANCHO de codigo de las subdivisiones de primer nivel difieren, y el mapa kind->segment difiere (kinds nacionales distintos). Segun el header 0053 los CHECK INE `<prov2><muni3>` son ellos mismos locks de gramatica ES.
- **Fix exacto** — Conducir el grano/conteo/ancho de geo_unit desde datos de subdivision ISO 3166-2 (pycountry) hacia un seal manifest por-pais: geo_unit_level, geo_unit_width y KNOWN_REAL_MAX derivados del conteo de subdivisiones, reemplazando el centinela '52 x 4'. Declarar el mapa kind->segment por CC en country.toml (ES mantiene su mapa 9->4 para que el manifest ES reproduzca las estrata de hoy byte-identicas). Parametrizar el DSN (quitar el hardcode :17 -> env). Mantener intacta la captura sobre unidad-resuelta (dedup cross-source Splink) — ya es country-agnostica.
- **Riesgo adversarial** — capture.py esta hardwired a 52 provincias y a un mapa kind->segment ES. Para un pais con distinto conteo/forma de subdivisiones o con kinds nacionales distintos, la estratificacion es incorrecta -> el MSE estima sobre celdas mal definidas -> el intervalo certificado es incomputable o sesgado. Corsica FR (2A/2B alfanumerico) y ultramar (971-976, 3 digitos) ni siquiera caben en el grano provincia CHAR(2). Si un source_key foraneo cae por bucket_for al default (el bug documentado fail-open-hacia-MKT), la lista mas fuerte del pais DESAPARECE en silencio del MSE y coverage_lower sub-cuenta sin error. PT/colas finas: celdas (province x segment) demasiado dispersas para cualquier solapamiento -> estrata unidentified. No-UE MX/JP: no existe mapeo de grano provincia en absoluto. El diseno cito complete.py G1-G5 como criterio de sello pero ESTA es la maquina REAL del intervalo, y esta ausente del country-pack.
- **Sellado multi-vía** — Multi-via: (1) Golden de manifest: el manifest ES derivado de ISO 3166-2 debe reproducir el conteo/ancho de estrata ES de hoy y el mapa 9->4 (cero regresion ES). (2) Sanity por-pais: los conteos de subdivision DE/FR/IT/MX/JP deben casar valores conocidos independientemente (16/101/107/32/47), cross-checked contra una 2a fuente (iso3166 / ground truth). (3) Contrato de datos pre-sello (fail-closed): aseverar que todo source_key mapea a un bucket ortogonal real (sin caida silenciosa a MKT), que los codigos de region casan el ancho de la rejilla del pais, y que cada clase ortogonal tiene >=1 fuente — si no, el estrato se NIEGA a sellar. (4) Test de dedup de unidad: un dealer en 2 fuentes colapsa a una unidad resuelta por lista (sin inflado m=10). (5) Test de DSN: ningun import pasa contra un literal :5433 hardcodeado en CI.
- **Herramienta NEXT-LEVEL** — pycountry (ISO 3166-1/-2 + ISO 4217 currency data) (LGPL-2.1) — https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:527-533, seccion 'ISO 3166-2 subdivision authority for the geo_unit grain, width, and per-country over-merge caps (seal manifest)'; licencia tambien en tabla resumen :64]. pycountry empaqueta el dataset Debian iso-codes; el conteo y ancho-de-codigo de las subdivisiones de primer nivel de cada pais se vuelven DATOS que alimentan un seal manifest por-pais, haciendo las guardas/caps mecanicas country-proof en vez de centinelas Spain-shaped. Lookup en build/config-time (autoria del manifest, NO el hot path), asi el uso-de-datos LGPL es non-issue; alternativa strict-permissive iso3166 (MIT) + iso-codes JSON crudo. EUR0.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) code_hints VERIFICADOS
- [VERIFIED capture.py:1-9] docstring: "The capture unit is the *resolved* (cross-source deduped) entity (v_dealer_resolved.resolved_ulid)... Strata: province_code x segment (4 broad dealer types) ~ 52 x 4."
- [VERIFIED capture.py:15] `from pipeline.exhaustiveness.lists import bucket_for, orthogonal_buckets`.
- [VERIFIED capture.py:17] DSN HARDCODEADO `postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep` (fuga de config a parametrizar).
- [VERIFIED capture.py:19-29] `DEALER_KINDS` = 9 kinds ES (compraventa, concesionario_oficial, desguace, garaje, subasta, importador, cadena, rent_a_car_vo, oem_vo_portal).
- [VERIFIED capture.py:31-42] `_SEGMENT` mapea los 9 kinds -> 4 segmentos ES (compraventa, concesionario, desguace, otros); :45-46 `segment_for`.
- [VERIFIED capture.py:49-92] `_fetch_raw(conn, unit='resolved'|'splink')`: SQL selecciona `(capture_unit, province_code, kind, source_key)` desde `entity_source JOIN entity JOIN v_dealer_resolved`, con `COALESCE(re.province_code, e.province_code)` y `WHERE e.kind::text IN DEALER_KINDS`; el path splink usa `discovery_splink_cluster` (build_run_id) para overlaps mas ajustados.
- [VERIFIED migrations/0001_geo.sql:13,21,26] `province_code CHAR(2) REFERENCES geo_province(code)` (codigos INE) + CHECK `left(code,2)=province_code`.
- [VERIFIED 0053 header] geo PK promovido a compuesto (country_code, code); toda fila ES country_code='ES'; persisten 2 CHECK ES-shaped INE (<prov2><muni3>).

#### (b) Mecanismo al atomo
La primera sub-maquina del sellador construye la matriz de captura sobre la que corre captura-recaptura (MSE). Define las estrata como el producto cartesiano province_code (52 provincias INE espanolas) x segment (4 tipos amplios colapsados de los 9 kinds ES) ~ 200 celdas. La UNIDAD de captura es la entidad RESUELTA (v_dealer_resolved.resolved_ulid) — el dedup cross-source es esencial para que un dealer visto en OSM y en autocasion colapse a UNA fila de captura por lista ortogonal (arregla el viejo undercount m=10 de entity_ulids sin fusionar). Por cada (unit, province, segment, source_key) emite una fila de presencia; la capa orthogonal_buckets/bucket_for mapea source_key -> clase de lista ortogonal (REG/MKT/MAP/OEM...). El estimador MSE estima despues, por estrato, la poblacion oculta a partir del patron de solapamiento entre listas.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-21"></a>
### Faceta 21 · Sellador de intervalo: triangulacion contra censo externo por-pais
*El 2º mecanismo del sello: panel de anclas, el desacuerdo es distrust.*  ·  **v1:** Clúster E

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — El seam YA es parametrico en codigo (`census_dir(country_code)`, `load_external_census(country_code=DEFAULT_COUNTRY)` triangulation.py:36-50; `seal.compute(external_census=None)` auto-carga ES seal.py:68-69). Lo ES-especifico: (i) el filename `dirce_cnae451.csv` es nombre espanol reusado verbatim; (ii) el DATO — el CSV de todo pais no-ES no existe; (iii) la doctrina de UN solo censo (DIRCE para ES) cuyo equivalente es KBA/Destatis (DE), INSEE/SIV (FR), ISTAT/ACI (IT), INE-PT (PT) — y para MX/JP puede no existir denominador abierto.
- **Fix exacto** — 1) Hacer el filename del ancla un campo de manifest por-CC (`external_census_filename` en country.toml, faceta 29) o documentarlo como generico, para que `dirce_cnae451.csv` deje de ser un nombre espanol impuesto a datos KBA/INSEE. 2) Proveer, por CC, el extracto DIRCE-equivalente como `countries/<CC>/census/<file>` con columnas `province_code,segment,n_external` mapeadas al grano de subdivision del pais (estrata, faceta 20) y al vocabulario de segmento: DE=KBA/Destatis NACE G45.1; FR=INSEE SIRENE/SBS; IT=ISTAT/ACI; PT=INE-PT. El seam ya lo consume — solo falta el fichero de datos. 3) Para paises sin censo nacional unico, pasar de UN ancla a un PANEL de anclas cross-border (herramienta): el sello debe ser consistente con la banda MAYORITARIA, el desacuerdo entre anclas es senal de distrust, no promedio silencioso. 4) ES byte-identico: `census_dir()` sin arg y `DEFAULT_COUNTRY=ES` resuelven a `countries/ES/census` igual que hoy (lo fija el contrato de 8 tests test_exhaustiveness_triangulation_loaded.py).
- **Riesgo adversarial** — Sin CSV del pais, triangulate->no_anchor (triangulation.py:72-73): el intervalo certificado sin verificacion ortogonal, N_hat inflable por listas correlacionadas-no-modeladas sin deteccion (n_hat_high nunca dispara con n_external=None). DE/FR/IT: ancla mal segmentada (KBA en grano distinto al de los estrata) vuelve la banda 0.7-1.4 sin sentido -> sella inflado o falso-marca correcto. MX/JP/no-UE: sin censo empresarial abierto comparable, triangulacion permanentemente no_anchor -> el sello no tiene 2o mecanismo y 'certificable' es incomputable. Ancla unica: una cifra oficial sesgada/rancia mueve el sello nacional en silencio.
- **Sellado multi-vía** — SEALED exige: (a) `countries/<CC>/census/` con un extracto real provenance-tagged (NO fabricado) cuyo grano case con los estrata (faceta 20); (b) el verdict national `triangulate` es 'consistent' (ratio 0.7-1.4) — `no_anchor`/`n_hat_high`/`n_hat_low` bloquea el sello o lo degrada a 'certificado SIN triangulacion, declarado'; (c) `external_ref` por-estrato persistido para los identificados; (d) en paises sin censo unico, el PANEL de >=2 anclas independientes aterriza N_hat en banda y el desacuerdo aflora como distrust; (e) el contrato de 8 tests de triangulacion pasa ES byte-identico. Multi-via: banda ratio (captura-recaptura vs censo) + un ancla independiente (conteo GLEIF/LEI por region) como 2o mecanismo + tag de provenance [MEDIDO]/[ESTIMADO DECLARADO] en SOURCE.md impuesto por el contrato existente.
- **Herramienta NEXT-LEVEL** — PRIMARIA: Panel de anclas MULTIPLES -> Eurostat Structural Business Statistics (SBS, NACE G45) (Reutilizacion libre, Decision 2011/833/EU; atribucion; EUR0) — https://ec.europa.eu/eurostat/web/structural-business-statistics [VERIFIED NEXT-LEVEL.md:191, tabla:22]. Convierte la triangulacion de UN censo (DIRCE para ES) a un PANEL de anclas independientes por-pais (Eurostat SBS conteo de establecimientos NACE G45.1, conteos GLEIF/LEI, stats-offices nacionales), cada una un mecanismo legal/fiscal DISTINTO; el sello debe ser consistente con la banda MAYORITARIA y el desacuerdo es senal de distrust, no promedio silencioso (NEXT-LEVEL:188-194). Cubre el 'censo externo por-pais' de todo miembro UE dia-uno con open-data EUR0. SECUNDARIA (hueco MX/JP/no-UE): GLEIF LEI Golden Copy (CC0 1.0 Universal, EUR0) — https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy [VERIFIED:175, tabla:20]: registro CC0 global que da una lista/conteo registral ortogonal a CADA pais dia-uno sin adaptador de registro nacional — el denominador para DE/FR/IT/PT/MX/JP donde los DIRCE-equivalentes no existen o no estan cableados (NEXT-LEVEL:172-178). ELEVACION del seam (de cross-check a CERTIFICACION): 'Censo externo VINCULANTE como margen-conocido' via dga/SparseMSE (GPL>=2, EUR0) — https://cran.r-project.org/package=dga [VERIFIED:135, tabla:15]: inyectar el censo como TOTAL MARGINAL CONOCIDO/offset Poisson log(n_external) en el ajuste captura-recaptura, de modo que los estrata que fallan IDENT_CAP (uncertified) obtengan N fijado por mecanismo fiscal independiente, moviendo masa uncertified->certified sin inventar dato; el gate pasa a coverage_lower>=0.95 AND census-consistent (NEXT-LEVEL:132-138). De 'el modelo cree 95%' a 'un mecanismo fiscal CONFIRMA el denominador'. Todo EUR0/CPU; el CSV por-CC ya existe por contrato.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) Verificacion de code_hints [VERIFIED]
- `triangulation.py:1-17` [VERIFIED]: docstring — seam de triangulacion externa §2.7; ancla canonica ES = INE DIRCE (CNAE 4511/4531-4532/4520 talleres) + DGT centros autorizados; soltar CSV `province_code,segment,n_external` bajo `countries/<CC>/census/` (default `countries/ES/census/`).
- `:26-27` [VERIFIED]: `CENSUS_CSV_NAME = "dirce_cnae451.csv"` — "country-agnostic; only the directory differs per country".
- `:29-33` [VERIFIED]: `CENSUS_DIR = census_dir()`, `DEFAULT_CSV = CENSUS_DIR/CENSUS_CSV_NAME` — back-compat ES.
- `load_external_census(path=None, country_code=DEFAULT_COUNTRY)` (`:36-63`) [VERIFIED]: `p = path or (census_dir(country_code)/CENSUS_CSV_NAME)`; `if not p.exists(): return {}`; header `province_code,segment,n_external`; prov/seg vacios -> clave `None` (ancla nacional/all-segment).
- `triangulate(n_hat, n_external)` (`:66-82`) [VERIFIED]: `no_anchor` si `n_external` None/<=0; `ratio=n_hat/n_external`; `>1.4`->`n_hat_high`, `<0.7`->`n_hat_low`, else `consistent`.
- `status()` (`:84-88`) [VERIFIED]: "loaded N anchors" o "pending external census (drop CSV at ...)".
- `seal.py:57-69` [VERIFIED]: param `external_census`; si `None` auto-carga `triangulation.load_external_census()` (default ES). `:144-149` bloque `triangulation` del summary: `status` + `triangulate(n_hat_sum, external_census.get((None,None)))` (ancla nacional). `:179,:195` `external_ref` persistido por-estrato en `exhaustiveness_estimate`.

#### (b) Mecanismo al atomo
El N-hat de captura-recaptura (faceta 22) solo es creible si concuerda con un censo construido por un mecanismo DISTINTO. El seam YA es parametrico: `load_external_census(country_code)` resuelve `countries/<CC>/census/dirce_cnae451.csv` a `{(province,segment):N}`; `seal.compute` auto-carga el CSV ES cuando `external_census=None` (`seal.py:68-69`), y para el roll-up nacional llama `triangulate(n_hat_sum, external_census[(None,None)])` reportando verdict `consistent`/`n_hat_high`/`n_hat_low`/`no_anchor` segun la banda `0.7-1.4`. Por-estrato persiste el `external_ref`. Cero cifra fabricada: hasta soltar el extracto DIRCE/DGT real, `load` devuelve `{}` y la triangulacion es "pending"; el pipeline corre, el ancla solo esta ausente.

#### (c) Costura ES->generico
El seam YA es parametrico (`census_dir(country_code)`, directorio por-CC) — el codigo es generico. Lo ES-especifico es: (i) el NOMBRE del fichero `"dirce_cnae451.csv"` es un nombre espanol (DIRCE/CNAE) reusado verbatim para todo pais (cosmetico, pero el pais debe proveer un fichero con ese nombre exacto); (ii) el DATO: el CSV de cada pais no-ES **no existe**. El `country_code=DEFAULT_COUNTRY` (ES) y `CENSUS_DIR=census_dir()` mantienen ES byte-identico. La costura PROFUNDA: triangular contra UN censo (DIRCE para ES). El mecanismo-ancla es la estadistica empresarial espanola; el equivalente DE es KBA/Destatis, FR es INSEE SIRENE/SIV, IT es ISTAT/ACI, PT es INE-PT, y para MX/JP puede **no existir denominador abierto comparable**.

#### (d) Riesgo adversarial concreto
- Sin el CSV del pais, `triangulate` devuelve `no_anchor` (`triangulation.py:72-73`) -> el intervalo certificado **sin verificacion ortogonal** -> el N-hat puede estar inflado por listas correlacionadas-no-modeladas sin que nada lo detecte (el caso `n_hat_high` que la banda deberia cazar nunca dispara porque `n_external` es None).
- **DE/FR/IT**: un ancla mal segmentada (KBA cuenta talleres autorizados en un grano CNAE-equivalente distinto del de los estrata del sello) vuelve la banda sin sentido — o sella un N-hat inflado o falso-marca uno correcto como `n_hat_high`.
- **MX/JP / no-UE**: puede NO haber censo empresarial nacional abierto comparable a DIRCE. Entonces la triangulacion es permanentemente `no_anchor` y el sello carece de 2o mecanismo — la definicion misma de "el intervalo es certificable" es **incomputable** para ese pais. (Distinto de las anclas de coverage_gap de la faceta 8, que son pisos de detector, no el censo de triangulacion del sello — el scope lo marca explicito.)
- **ruido/sesgo de ancla unica**: depender de UN censo significa que una cifra oficial sesgada o rancia mueve en silencio el sello nacional; un humano elige un numero y lo llama techo.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-22"></a>
### Faceta 22 · Sellador de intervalo: estimadores MSE + roll-up nacional + veredicto de sello
*El intervalo nacional honesto: se certifica la cota inferior, nunca el punto.*  ·  **v1:** Clúster E

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — La matematica capture-recapture es generica. Costura ES = DEFAULT_THRESHOLD=0.95 [seal.py:27] constante de modulo. Los insumos (estrata faceta 20, censo faceta 21) son las dependencias por-CC; el estimador _seal_one/roll-up NO tiene literal ES mas alla del threshold.
- **Fix exacto** — threshold desde country.toml [seal].coverage_threshold; mantener intacto el split certified/uncertified [seal.py:84-95] y la certificacion lower-bound-only (n_obs/ci_high, ya genericos). ES declara 0.95 -> veredicto byte-identico. NO tocar _seal_one ni el roll-up (country-agnostic by construction).
- **Riesgo adversarial** — Pais de poca superposicion (DE/IT/PT solo GEO+OEM): estrata caen en unidentified -> denominador desconocido; plegarlos como cubierto inflaria la cobertura (el codigo lo evita seal.py:84-95, pero un parametro mal puesto -include_mkt/gate identified- los colaria). Sin estrata/censo por-CC (20/21) el roll-up no tiene insumos validos. MX/JP sin censo: triangulate -> 'no_anchor' -> N_hat inflado sin deteccion.
- **Sellado multi-vía** — Via1: sello = nat_cov_lower>=threshold con IC95, nunca el punto (espejo ES 37,72/42,69%). Via2: estimators_r.crosscheck(N_hat, run_mse, tol=0.25) — distrust gate YA existe [estimators_r.py:175-193]. Via3: test que asevera unidentified nunca entra a n_hat_sum. Via4: golden ES byte-identico tras inyectar threshold (monotonia, cero regresion).
- **Herramienta NEXT-LEVEL** — dga (Bayesian Model Averaging) — GPL(>=2) — https://cran.r-project.org/package=dga [VERIFIED NEXT-LEVEL.md:127] + SparseMSE — GPL(>=2) — https://cran.r-project.org/package=SparseMSE [VERIFIED NEXT-LEVEL.md:119]. Ambas por el bridge Rscript existente (estimators_r.py). dga quita la dependencia de UN modelo-BIC (posterior de N, cota del cuantil 2.5%). SparseMSE sella estrata de solapamiento-cero (K<3) donde el log-lineal Python da inf-CI. Cross-check tol=0.25 (estimators_r.py:175-193). €0, degrada graceful sin R.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) code_hints VERIFICADOS
- **_seal_one** [VERIFIED pipeline/exhaustiveness/seal.py:39-47]: `e = est.estimate_stratum(freqs)`; `cov_lower = e.coverage_lower`; `sealed = e.identified AND math.isfinite(cov_lower) AND cov_lower >= threshold`. El punto NUNCA certifica — solo la cota inferior.
- **threshold** [VERIFIED seal.py:27] `DEFAULT_THRESHOLD = 0.95` (constante de modulo).
- **compute** [VERIFIED seal.py:50-162]: auto-carga `external_census` via `triangulation.load_external_census()` si None (seal.py:68-69); `capture.read_patterns`; por estrato `_seal_one`; cross-check R opcional si `identified AND k_lists >= 3` (`estimators_r.run_mse` + `estimators_r.crosscheck`, seal.py:78-81).
- **Roll-up nacional HONESTO** [VERIFIED seal.py:84-107] comentario "anti-maquillaje": `identified` vs `unidentified`; `n_hat_sum = sum(N_hat de identified)` = denominador certificado; los unidentified **NO** se pliegan como "100% cubierto" (su denominador es DESCONOCIDO) -> se reportan aparte. `nat_se` combina half-widths **asumiendo independencia entre estrata (varianzas suman)** [seal.py:103]; `nat_cov_lower = n_obs_cert / nat_ci_high` [seal.py:107].
- **Veredicto de sello** [VERIFIED seal.py:138] `"sealed": bool(nat_cov_lower >= threshold)`.
- **Pooled cross-check** [VERIFIED seal.py:109-114, 150-160] fit nacional agrupado marcado "UNRELIABLE, cross-check only".
- **Persistencia** [VERIFIED seal.py:165-216] `_persist`: DELETE por build_run_id + INSERT por estrato + fila nacional (province_code NULL, segment NULL) en `exhaustiveness_estimate`.
- **Estimate** [VERIFIED estimators.py:37-59]: dataclass con n_obs, n_hat, ci_low, ci_high, method, k_lists, confidence, `identified` ("False => sparse overlap, N_hat not trustworthy").
- **Bridge R existente** [VERIFIED estimators_r.py]: `run_mse` (95-129) corre Rcapture+LCMCR via Rscript subprocess; `crosscheck` (175-193) implementa la regla §2.3 de doble-verificacion con `tol=0.25`; degrada graceful si no hay R (`r_available`).

#### (b) El mecanismo al atomo
Captura-recaptura estratificada: cada estrato (provincia x segmento, faceta 20) tiene un patron de captura `freqs` (tupla 0/1 por lista -> frecuencia). `estimate_stratum` ajusta el modelo (Chapman / log-lineal Fienberg por BIC / cota dependence-robust) y produce `N_hat`, `ci_high`, `coverage_lower = n_obs/ci_high`. El **roll-up suma N_hat de los estrata identified** y combina varianzas asumiendo independencia entre-estrato. La doctrina es **"intervalo, nunca un entero"**: se certifica `n_obs/ci_high` (la cota inferior conservadora), no el punto. El split certified/uncertified es el blindaje anti-maquillaje: lo que no tiene solapamiento suficiente no se cuenta como cubierto.

#### (c) Costura ES->generico + fix exacto
La matematica es **generica** (capture-recapture es agnostico). Las costuras por-pais son: (1) `DEFAULT_THRESHOLD=0.95` constante de modulo -> debe ser por-CC; (2) los **insumos** (estrata faceta 20, censo faceta 21) que esta faceta consume. El estimador en si **no** tiene literal ES mas alla del threshold.
**Fix:** `threshold` desde `country.toml` (`[seal] coverage_threshold`); mantener intacto el split certified/uncertified y la certificacion lower-bound-only (ya correctos y genericos). ES declara `0.95` -> veredicto byte-identico. NO tocar `_seal_one`/roll-up (son country-agnostic by construction).

#### (d) Riesgo adversarial concreto
- **Pais de poca superposicion entre listas (DE/IT/PT con solo GEO+OEM):** los estrata caen en `unidentified` -> denominador DESCONOCIDO -> plegarlos como "100% cubierto" **inflaria** la cobertura nacional. El codigo lo evita (seal.py:84-95 los reporta aparte), pero un **parametro mal puesto** (p.ej. forzar `include_mkt` o bajar el gate de identified) los colaria.
- **Sin estrata/censo por-CC (facetas 20/21):** el roll-up no tiene insumos validos -> el intervalo es incomputable o sesgado.
- **MX/JP sin denominador externo:** `triangulate` devuelve "no_anchor" -> el intervalo certificado se queda sin verificacion ortogonal -> `N_hat` puede estar inflado (listas correlacionadas no modeladas) sin que nada lo detecte.

#### (e) Criterio de sellado + verificacion multi-via
- **Via 1 (intervalo, no punto):** el sello es `nat_cov_lower >= threshold` con IC95 (espejo ES 37,72/42,69%); jamas el punto.
- **Via 2 (cross-check R ortogonal):** `estimators_r.crosscheck(N_hat_python, run_mse(freqs), tol=0.25)` — la cota de distrust YA existe [estimators_r.py:175-193]; mecanismo distinto (model-selection vs Python log-lineal).
- **Via 3 (split honesto):** test que asevera que los estrata `unidentified` **nunca** entran al `n_hat_sum` (el denominador certificado = solo identified).
- **Via 4 (golden ES):** el roll-up nacional ES byte-identico tras inyectar `threshold` desde toml; monotonia (cero regresion).

#### (f) Herramienta NEXT-LEVEL
**dga: Capture-Recapture Estimation using Bayesian Model Averaging** — GPL (>=2), https://cran.r-project.org/package=dga [VERIFIED NEXT-LEVEL.md:127] **+ SparseMSE: Multiple Systems Estimation for Sparse Capture Data** — GPL (>=2), https://cran.r-project.org/package=SparseMSE [VERIFIED NEXT-LEVEL.md:119]. **Ambas corren por el bridge Rscript que YA existe** (estimators_r.py, verificado). **dga** quita la dependencia de UN modelo elegido por BIC (estimators.py log-lineal greedy): produce un POSTERIOR de N por estrato e integra la incertidumbre de seleccion-de-modelo; la cota inferior del sello se toma del cuantil 2.5% del posterior promediado (estandar HRDAG, "numero que aguanta un interrogatorio adversarial"). **SparseMSE** (Chan-Silverman-Vincent 2019) sella el pais de fuentes delgadas: en estrata con pares de listas de **CERO solapamiento** (K<3, el fallo no-ES CRITICAL) recupera un intervalo finito donde el log-lineal Python degenera a observed-only/inf-CI. Verificacion (NEXT-LEVEL.md:122,130): cross-check vs Python log-lineal en estrata CON solapamiento dentro de tol=0.25; en solapamiento-cero confirmar intervalo finito; la mediana del posterior dga coincide con el punto log-lineal dentro de tol. dga + LCMCR + SparseMSE forman un TRIO de 2a-via (model-averaging / latente / sparse) sobre el mismo input `freqs`. €0, CPU, degrada graceful sin R.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-23"></a>
### Faceta 23 · Bus de decisiones: esquema + contrato (decision_request/decision_event)
*El contrato del bus: country_code día-0 + dedupe_key idempotente para reuso cross-país.*  ·  **v1:** Infra · bus

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — decision_request/country_campaign/cover() NO existen (grep=0, VERIFIED). Diseno-nuevo, no extraccion. La costura es de contrato: country_code columna dia-0 (ninguna lleva 'ES') y dedupe_key (kind|subject_key|bucket) idempotente espejando gestion_item, para habilitar reuso cross-pais (misma ambiguedad estructural se responde una vez entre paises).
- **Fix exacto** — Migracion que espeja 0031: decision_request con dedupe_key TEXT NOT NULL UNIQUE, country_code NOT NULL, kind/reversibility/decider/state como ENUM (CREATE TYPE additive), context/options JSONB, FKs opcionales a gestion_item(id)/verification_verdict(id), indices parciales. decision_event append-only (INSERT-only). emit_decision_request con ON CONFLICT(dedupe_key) DO UPDATE espejando route.py:open_or_refresh (87-190); revertir = APPLIED->REJECTED, jamas DELETE.
- **Riesgo adversarial** — Bus hereda gestion_item VACIA (jamas carga durable). Sin emision acotada (faceta 15) un pais EUR0 inunda decision_request de PENDING no-auto-resolubles -> rafaga Claude. dedupe_key mal disenado (con country_code) re-litiga ambiguedades identicas DE/FR/IT/PT N veces; bucket demasiado ancho colisiona decisiones distintas. Ruido: re-emision en bucle debe colapsar al mismo request (idempotencia).
- **Sellado multi-vía** — (1) Migracion additive+reversible (rollback DROP). (2) Idempotencia: misma duda 50x => 1 request + 50 decision_event. (3) Reuso cross-pais: misma forma DE+FR => 1 decision. (4) Exactly-once: matar worker en CLAIMED => retoma sin duplicar APPLIED; count(decision_event) == transiciones esperadas via SQL. (5) ES byte-identico (additive).
- **Herramienta NEXT-LEVEL** — Procrastinate (MIT, EUR0) https://github.com/procrastinate-org/procrastinate [VERIFIED NEXT-LEVEL.md:552-558] — tareas durables sobre el PG existente: claim FOR UPDATE SKIP LOCKED, retry backoff por tipo, worker que reanuda tras crash; modela PENDING->...->VERIFIED con exactly-once gratis, cierra 'lease best-effort sin takeover'. Alt: pgqueuer (MIT), DBOS Transact (MIT).

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### Estado actual [VERIFIED]
NUEVO confirmado esta sesion: `git grep decision_request` y `git grep country_campaign` en pipeline/migrations/services = **0 coincidencias**; `git grep "def cover("` en pipeline = **0**. Nada de esto existe todavia; la faceta es diseno-nuevo, no extraccion.

#### Plantilla EXISTENTE a espejar [VERIFIED]
- **gestion_item** (0031:44-96): `dedupe_key TEXT NOT NULL, UNIQUE (dedupe_key)` (:94-95); estado con CHECK enum-like (:74-77); indices PARCIALES por estado y por gate (:99-116).
- **gestion_transition** (0031:121-131): append-only puro (id IDENTITY, item_id FK CASCADE, from_state/to_state/actor/note/payload/at). Cero UPDATE/DELETE — "la historia ES la prueba" (0031:35-36).
- **route.py:open_or_refresh** (87-190): el upsert idempotente — `INSERT INTO gestion_item (...) VALUES (...) ON CONFLICT (dedupe_key) DO UPDATE SET measured/severity/score, reopen-if-closed` (:115-143), `RETURNING id, state, (xmax = 0) AS is_new` (:142) para distinguir insert de update sin un 2o round-trip.

#### Mecanismo al atomo (el contrato nuevo)
- **decision_request**: `country_code` NOT NULL DIA-0 (ninguna columna lleva 'ES'); `kind` ENUM (RECIPE_TIER1_NEW | GEO_AMBIGUITY | DENOMINATOR_AMBIGUITY | VAM_DISCREPANCY | CLASSIFICATION_DOUBT | RECIPE_FIELD_EXTRACT | COVERAGE_SEAL_REVIEW); subject_type/key; question; context JSONB; options; `reversibility` ENUM (reversible | spend | prod | legal); `decider` ENUM; decision; confidence; `state` PENDING -> CLAIMED -> DECIDED -> APPLIED -> VERIFIED | REJECTED | ESCALATED_HUMAN; FKs a gestion_item(id)/verification_verdict(id); `dedupe_key` UNIQUE.
- **decision_event**: espejo append-only de gestion_transition (INSERT-only, request_id FK, from_state/to_state/decider/rationale/at).

#### Costura ES->generico
El country_code es columna desde el dia 0, a diferencia de LANE_SLA/COVERAGE_ANCHORS que nacieron ES-hardcoded. La costura real es de DISENO, no de extraccion: el `dedupe_key` debe ser (kind | subject_key | bucket) idempotente IGUAL que gestion_item, para habilitar el REUSO CROSS-PAIS — misma forma de denominador o patron geo se responde UNA vez y se reusa entre paises, no se re-litiga N veces. Y la inmutabilidad: una decision erronea se revierte con APPLIED->REJECTED, jamas un DELETE.

#### Riesgo adversarial concreto
El bus hereda que gestion_item esta VACIA: nunca ejercitado a escala (solo tests, jamas carga durable real). Sin emision acotada/opt-in (faceta 15) un pais EUR0 inunda decision_request con PENDING no-auto-resolubles -> rafaga de Claude inmanejable. Si el dedupe_key se disena mal (incluye country_code donde no debe), ambiguedades identicas DE/FR/IT/PT se re-litigan N veces en vez de reusarse -> coste multiplicado por pais. Si el bucket es demasiado ancho, colisiona decisiones distintas (rompe el invariante "misma mentira misma ruta"). Ruido: un detector que re-emite la misma duda en bucle debe colapsar al MISMO decision_request (idempotencia), no abrir N filas.

#### Sellado + verificacion multi-via
1. **Migracion additive+reversible**: bloque rollback DROP, IF NOT EXISTS everywhere (espeja 0031:38).
2. **Idempotencia**: emitir la misma duda 50x => 1 fila decision_request + 50 filas decision_event (espejo exacto del invariante gestion).
3. **Reuso cross-pais**: misma forma estructural en DE y FR => 1 decision reusada (no 2).
4. **Exactly-once durable**: matar el worker a mitad de un CLAIMED y verificar que otro lo retoma y completa exactamente una vez (sin duplicar APPLIED); conteo decision_event (append-only) == nº de transiciones esperado, recomputado por SQL directo.
5. **ES byte-identico**: el bus es additive y no toca el flujo ES existente.

#### Herramienta NEXT-LEVEL
**Procrastinate** (MIT) https://github.com/procrastinate-org/procrastinate [VERIFIED NEXT-LEVEL.md:552-558]: bus + drains como TAREAS DURABLES sobre el PG ya existente (cero infra nueva): claim idempotente `FOR UPDATE SKIP LOCKED`, retry con backoff exponencial por tipo, y un worker que reanuda a mitad de vuelo tras un crash. Modela el ciclo PENDING->CLAIMED->DECIDED->APPLIED->VERIFIED con claim exactly-once gratis, cerrando el riesgo declarado "el lease es best-effort, NO takeover". Alternativas: pgqueuer (MIT, LISTEN/NOTIFY+SKIP LOCKED) si solo se quiere el claim durable; DBOS Transact (MIT) para workflows reanudables paso-a-paso.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-24"></a>
### Faceta 24 · Interfaz triage() + clasificador de reversibilidad + freno de Autonomia
*El freno de §Autonomía: reversible→bus, spend/prod/legal→humano (fail-closed).*  ·  **v1:** Infra · freno

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — Faceta NUEVA [VERIFIED grep: triage()/emit_decision_request/decision_request = 0]. La _ROUTING_TABLE sellada [VERIFIED router.py:65-99, 'sealed by Director 2026-06-15'] NO debe cambiar; triage va aguas abajo de _lookup_route [VERIFIED router.py:103-128] leyendo el action, no mutando la tabla. La dimension pais entra porque 'legal' difiere por CC (MX/JP != ES): el clasificador de reversibilidad debe leer la frontera legal/spend de country.toml.
- **Fix exacto** — router.py byte-identico (test exhaustivo verde); triage(route,context,country_pack) puro que clasifica reversibilidad (reversible|spend|prod|legal) con default fail-closed a la clase MAS restrictiva (desconocido->irreversible->humano); emit_decision_request escribe decision_request (faceta 23) con dedupe_key idempotente; spend/prod/legal SIEMPRE PENDING-OWNER sin parar el loop.
- **Riesgo adversarial** — Mis-clasificacion catastrofica en ambos sentidos: 'reversible' sobre algo spend/prod/legal deja a Claude/IA tocar lo irreversible sin humano (rompe §Autonomia); 'spend' sobre algo reversible re-inunda el dead-end humano. Frontera legal ES mis-clasifica MX/JP. Sin emision acotada/opt-in un pais EUR0 inunda decision_request de PENDING no-auto-resolubles.
- **Sellado multi-vía** — Sello: router table intacta (test exhaustivo byte-identico); golden tabla-driven (verdict,reason)->clase reversibilidad; test fail-closed (decision desconocida->humano); 2a via outcomes triage->humano == {spend,prod,legal} U no-clasificable; adversarial decision reversible cuyo apply toca spend/prod atrapada por contrato tipado pre-emit; frontera legal desde country.toml no literal.
- **Herramienta NEXT-LEVEL** — Pydantic (MIT, EUR0) https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:584-590]: taxonomia de reversibilidad + contrato decision_request como schema TIPADO fail-closed (ENUM con default a clase mas restrictiva) -> mis-clasificacion = fallo de tipo/CI, no escalacion silenciosa de lo irreversible. Complemento Procrastinate (MIT) https://github.com/procrastinate-org/procrastinate [VERIFIED NEXT-LEVEL.md:552-558]: cola durable PG con claim idempotente SKIP LOCKED + exactly-once para la reanudacion real (faceta 14).

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) Verificacion de code_hints [VERIFIED]
- [VERIFIED grep] `triage(`/`emit_decision_request`/`reversibility` en pipeline/inquisition = **0 ocurrencias**. `decision_request`/`country_campaign` en pipeline+services+migrations = **0**. -> esta faceta es **NUEVA**.
- [VERIFIED pipeline/inquisition/router.py:103-128] `_lookup_route(verdict, reason_code)` = lookup puro de tabla (exacto -> catch-all '*' -> fallback RESEARCH). Tabla **sellada** ("sealed by Director on 2026-06-15" [:43]).
- [VERIFIED router.py:140-228] `route_verdict(...)` = el punto de insercion aguas-abajo (llama `_lookup_route` [:171], abre gestion_item via `open_or_refresh` [:213], alerta critical [:216]).
- [VERIFIED router.py:84] `_RouteRow("REFUTED","NO_INDEPENDENT_PATH","escalate","ESCALATE_OWNER",False,"warning",0.5)`.
- [VERIFIED router.py:93] `_RouteRow("INCONCLUSIVE","*","escalate","ESCALATE_OWNER",False,"info",0.5)`.
- [VERIFIED quorum.py:236-246] fuente de `NO_INDEPENDENT_PATH`; [VERIFIED quorum.py:336-345] fuente de `INCONCLUSIVE/SINGLE_ASSERT`.

#### (b) Mecanismo al atomo
Hoy CADA ruta de escalacion muere en el humano (ESCALATE_OWNER) **sin memoria reutilizable**. `triage()` es una funcion **PURA** insertada AGUAS ABAJO de `_lookup_route`: para `action=='escalate'`, clasifica la **reversibilidad** de la decision (reversible | spend | prod | legal) y bifurca — reversible+decidible -> `emit_decision_request()` al bus (faceta 23); spend/prod/legal -> mantiene ESCALATE_OWNER/ESCALATE_GASTO (humano). Es la materializacion del freno de §Autonomia: el motor inserta los 2 escalones intermedios (IA local, Claude) ANTES del humano **solo** para lo reversible, y NUNCA deja tocar lo irreversible sin humano.

#### (c) Costura ES->generico + fix exacto
La `_ROUTING_TABLE` sellada **NO debe cambiar** (invariante "misma mentira -> misma ruta", determinismo auditable). triage va **estrictamente aguas abajo** — lee el `action` de la ruta, no muta la tabla. La dimension pais entra porque lo que es "legal" difiere por pais (frontera legal MX/JP != ES): el clasificador de reversibilidad debe consultar una frontera legal/spend por-CC desde country.toml. **Fix:** (a) router.py byte-identico (test exhaustivo `router_mapping_rows()` sigue verde); (b) `triage(route, context, country_pack) -> {emit | escalate_human}` puro que clasifica reversibilidad contra una taxonomia por-CC con **default fail-closed a la clase MAS restrictiva** (desconocido -> irreversible -> humano); (c) `emit_decision_request` escribe en `decision_request` (faceta 23) con `dedupe_key` idempotente; (d) spend/prod/legal SIEMPRE quedan PENDING-OWNER **sin parar el loop** (doctrina cardeep).

#### (d) Riesgo adversarial concreto
Una mala clasificacion es **catastrofica en ambos sentidos**: marcar 'reversible' algo spend/prod/legal deja a Claude/IA-local tocar lo irreversible sin humano (rompe el freno de §Autonomia); marcar 'spend' algo reversible **re-inunda** el dead-end humano que el bus venia a vaciar. Distinto pais = distinta frontera legal: una frontera "legal" calibrada a ES mis-clasifica decisiones MX/JP. Sin emision acotada/opt-in, un pais EUR0 inunda `decision_request` de PENDING no-auto-resolubles.

#### (e) Sellado + verificacion multi-via
- **Sello:** (i) router table intacta — test exhaustivo byte-identico; (ii) golden tabla-driven de triage: cada (verdict,reason)->clase de reversibilidad fija y testeada; (iii) test fail-closed: decision desconocida/no-mapeada -> humano (mas restrictivo); (iv) 2a via: el conjunto de outcomes triage->humano == exactamente {spend,prod,legal} U no-clasificable, recomputado independiente; (v) adversarial: una decision etiquetada reversible cuyo apply toca spend/prod la atrapa un contrato tipado ANTES de emit; (vi) por-CC: la frontera legal viene de country.toml, no de literal.
- **Multi-via:** 1a golden de clasificacion; 2a recompute del particionado reversible/irreversible; 3a adversarial de mis-clasificacion en ambos sentidos.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**Pydantic** (MIT, EUR0) — https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:584-590, cluster ops-automation-llm]. Modela la **taxonomia de reversibilidad + el contrato decision_request** como un **schema TIPADO fail-closed** (ENUM reversibility con validator de default a la clase mas restrictiva), de modo que una mis-clasificacion es un fallo de tipo/CI, **no** una escalacion silenciosa de lo irreversible en runtime. **Complemento:** **Procrastinate** (MIT, EUR0) — https://github.com/procrastinate-org/procrastinate [VERIFIED NEXT-LEVEL.md:552-558] = la cola de tareas durable Postgres-nativa a la que triage emite (claim idempotente `FOR UPDATE SKIP LOCKED`, retry/backoff, exactly-once PENDING->CLAIMED->DECIDED->APPLIED->VERIFIED), aportando la **reanudacion real** que el lease advisory admite que no tiene (faceta 14). Ambos EUR0 sobre el PG existente, cero infra nueva.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-25"></a>
### Faceta 25 · Capa-2 decider IA local (local_ai_drain + confidence-gate + cierre de STUBs + golden-set)
*El tier ausente: llama.cpp+gramática enchufa en los 2 slots sin tocar el motor.*  ·  **v1:** Clúster I

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — La capa-2 (IA local confidence-gated entre el determinista y Claude) NO existe en codigo: recipe_schema.py:67 tiene 'llm_local' como enum muerto; detect.py:886-898 (geo_resolution_drift) y 905-916 (classifier_drift) son STUBs que devuelven [] por falta de golden_set/tabla de tracking; STUB_DETECTORS los salta (detect.py:940); y grep openai|anthropic|ollama|llama_cpp|vllm|outlines|litellm en pipeline/ = 0 (VERIFIED: 0 IA local). Sin capa-2, toda duda de clasificacion/extraccion de cada pais escala directo a Claude.
- **Fix exacto** — Cuatro piezas, todas €0 y desbloqueadas solo por el contrato del bus (faceta 23): (1) llama.cpp sirviendo GGUF Q4 en CPU con GBNF nativo = el endpoint OpenAI-compatible que la matriz asume; (2) Outlines/GBNF para que el decider emita SOLO {make∈brand_table∪null, model, fuel∈enum, transmission∈enum} (anti-alucinacion por construccion); (3) job local_ai_drain que reclama PENDING CLASSIFICATION_DOUBT/RECIPE_FIELD_EXTRACT, devuelve decision+confidence y escala a Claude bajo umbral calibrado sin etiquetas (NannyML); (4) cerrar classifier_drift con detector de drift real (Evidently) y construir el golden-set por-CC (Argilla), que se llena gratis con cada decision de Claude VAM-VERIFIED (bus-as-eval). ES byte-identico: con modelo dormante el NormalizerLLM devuelve 'sin recuperacion' (fallback determinista).
- **Riesgo adversarial** — Con 0 IA local, cada duda de cada pais escala a Claude -> bus Claude-heavy, rafaga de coste/tiempo inmanejable en un onboarding (auto-DoS que el scheduler ya advierte a €0). Un golden ES no valida labels de kinds extranjeros (keiretsu de subastas JP, 'lote' MX, kei-car): sin golden por-CC, classifier_drift devuelve [] y la deriva del clasificador en el mercado nuevo es invisible. Un LLM sin decodificacion por gramatica inventa marcas/enums y contamina el eje de busqueda (viola Ley I mis-fill>under-fill). Sin eval-harness, promocionar el modelo local a un kind es un swap a ciegas que puede latchear errores.
- **Sellado multi-vía** — Sellado = endpoint local con gramatica (0 parse-fails), local_ai_drain con confidence-gate calibrado, classifier_drift vivo (no []) con golden por-CC, cero decision irreversible tocada por capa-2, ES byte-identico (fallback determinista con modelo dormante). Multi-via: (1) fuzz 10k bajo gramatica => 0 salidas fuera de enum, ABSTAIN siempre alcanzable; (2) shift sintetico => rendimiento estimado cae y umbral sube; cuando VAM etiqueta, el real cae dentro del IC sin-etiquetas; (3) drift sintetico => classifier_drift emite CLASSIFICATION_DOUBT, concuerda con KS-test independiente; (4) prompt/gramatica que baja F1 => CI rojo, solo TRUSTWORTHY+quorum>=2 promociona al golden.
- **Herramienta NEXT-LEVEL** — llama.cpp (MIT, €0) https://github.com/ggml-org/llama.cpp [VERIFIED NEXT-LEVEL.md:648-654] — endpoint OpenAI-compatible GGUF Q4 en CPU con GBNF nativo, 'Capa-2=0 lineas' -> endpoint corriendo. Stack de cierre €0: Outlines (Apache-2.0) https://github.com/dottxt-ai/outlines [:656-662] decodificacion restringida (incapaz de salir de brand_table/enum); Evidently (Apache-2.0) https://github.com/evidentlyai/evidently [:616-622] cierra el STUB classifier_drift emitiendo CLASSIFICATION_DOUBT; NannyML (Apache-2.0) https://github.com/NannyML/nannyml [:608-614] confidence-gate sin etiquetas; Argilla (Apache-2.0) https://github.com/argilla-io/argilla [:632-638] golden-set por-CC (profesor Claude->alumno local); RouteLLM (Apache-2.0) https://github.com/lm-sys/RouteLLM [:672-678] router barato-vs-fuerte antes de correr el modelo.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) Verificacion de code_hints [VERIFIED]
- **[VERIFIED pipeline/recipe_schema.py:67]** `engine: str = "next_data"  # next_data | jsonld | css | llm_local` — `llm_local` es **solo un valor de enum**, slot dormante; el docstring (65-66) lo situa al final del ladder de coste.
- **[VERIFIED pipeline/gestionador/detect.py:886-898]** `detect_geo_resolution_drift` STUB: `return []` (898); docstring "the sentinel_placement_rate column / tracking table does not yet exist" + "Requires: new migration adding geo placement tracking".
- **[VERIFIED pipeline/gestionador/detect.py:905-916]** `detect_classifier_drift` STUB: `return []` (916); docstring "Runs the local LLM classifier nightly against this set" (910) + "Requires: golden_set table + classifier evaluation pipeline. Both are T08 §5.1 items not yet implemented" (913-914).
- **[VERIFIED pipeline/gestionador/detect.py:926-936]** `DETECTORS` = 9 entradas (7 live + 2 STUB); **[VERIFIED :940]** `STUB_DETECTORS = frozenset({"geo_resolution_drift", "classifier_drift"})` — `run_all` los SALTA para no loguear "ran, 0 found" falso.
- **[VERIFIED grep `(?i)\b(openai|anthropic|ollama|llama_cpp|vllm|outlines|litellm|transformers|gguf)\b` en `pipeline/` = No matches found]** — **0 IA local en codigo**. Confirma la afirmacion del diseno "grep openai/anthropic/ollama en pipeline/ = 0 reales".

#### (b) El mecanismo al atomo
El diseno 3-capas dice: *determinista 24/7 -> IA local confidence-gated -> Claude orquestador*. La capa-2 es el tier que, para `kind` `CLASSIFICATION_DOUBT`/`RECIPE_FIELD_EXTRACT`, deberia reclamar PENDING del bus, **decidir con confidence** y escalar a Claude bajo umbral. Hoy ese tier **no existe**: no hay endpoint de modelo (0 IA local), `llm_local` es un enum muerto, y los dos detectores que dependen de IA local (`classifier_drift`, `geo_resolution_drift`) son STUBs que devuelven `[]` por falta de golden/tabla. El contrato del bus (faceta 23) es el **unico desbloqueo**: el dia que se deja caer un GGUF, capa-2 enchufa sin tocar el motor.

#### (c) La costura ES->generico con su fix exacto
**Costura:** sin capa-2, TODA duda de clasificacion/extraccion de CADA pais escala a Claude => el bus es Claude-heavy (coste/tiempo de rafaga alto). Y `classifier_drift` no puede medir deriva sin un golden por-pais (un golden ES no valida labels de kinds extranjeros).

**Fix exacto (4 piezas):**
1. **Runtime €0:** levantar el endpoint OpenAI-compatible que toda la matriz LLM asume — `llama.cpp` sirviendo GGUF Q4 en CPU, con GBNF nativo. Pasa "Capa-2 = 0 lineas" a "endpoint corriendo".
2. **Anti-alucinacion por construccion:** decodificacion restringida (`Outlines`/GBNF) para que el decider emita UNICAMENTE `{make ∈ brand_table∪null, model, fuel∈enum, transmission∈enum}` — fisicamente incapaz de inventar fuera del vocabulario del pack.
3. **`local_ai_drain` con confidence-gate:** job que reclama PENDING de `CLASSIFICATION_DOUBT`/`RECIPE_FIELD_EXTRACT`, devuelve `decision+confidence` y escala a Claude bajo umbral; el umbral se **calibra sin etiquetas** y se recalibra ante deriva.
4. **Cierre de STUBs + golden-set por-pais:** cablear un detector de drift real a `classifier_drift` (deja de devolver `[]`), y construir el golden-set por-CC como eval — que ademas se llena GRATIS con cada decision de Claude VERIFICADA por VAM (bus-as-eval retroactivo). El enganche en los DOS slots dormantes (`recipe_schema.llm_local` + `detect.classifier_drift`) es directo una vez existe el endpoint.
ES queda igual: con capa-2 dormante, el `NormalizerLLM` devuelve 'sin recuperacion' (fallback determinista) y el sistema es identico con o sin modelo.

#### (d) El riesgo adversarial concreto (DE/FR/IT/PT/no-UE/ruido)
- **Bus Claude-heavy:** con 0 IA local, cada duda de cada pais escala a Claude. Un onboarding sin capa-2 dispara una **rafaga de coste/tiempo inmanejable** (el riesgo de auto-DoS que el scheduler ya advierte a €0).
- **Golden ES no valida kinds extranjeros:** `classifier_drift` necesita un golden por-pais; un golden ES no etiqueta keiretsu de subastas JP, 'lote' MX, kei-car. Sin golden por-CC **no hay forma de medir** si el clasificador deriva en el mercado nuevo — el STUB devuelve `[]` y la deriva es invisible.
- **Alucinacion de vocabulario:** un LLM sin decodificacion por gramatica inventa marcas/enums (p.ej. emite una marca inexistente) y contamina el eje de busqueda — viola la Ley I (mis-fill > under-fill). Solo la decodificacion restringida lo hace imposible por construccion.
- **Promocion a ciegas:** sin eval-harness, sustituir Claude por el modelo local en un `kind` es un swap sin red — el modelo local puede degradar y latchear errores como decisiones.

#### (e) Criterio de sellado + verificacion multi-via
**Sellado:** endpoint local corriendo con gramatica (0 parse-fails); `local_ai_drain` con confidence-gate calibrado; `classifier_drift` vivo (no `[]`) con golden por-CC; cero decision irreversible tocada por capa-2; ES byte-identico (fallback determinista gana con modelo dormante).
**Multi-via:**
1. **Via gramatica (fuzz):** 10k generaciones bajo gramatica => 0 salidas fuera de esquema/enum; un enum desconocido jamas se emite y la clase ABSTAIN/UNKNOWN siempre es alcanzable (nunca fuerza encaje).
2. **Via confidence sin-etiquetas:** inyectar un shift de distribucion conocido y confirmar que el rendimiento estimado cae y el umbral sube (mas escaladas a Claude); cuando VAM ETIQUETA un lote, el rendimiento real cae dentro del IC del estimado sin-etiquetas.
3. **Via golden (cierre de STUB):** dataset con drift sintetico => `classifier_drift` emite `CLASSIFICATION_DOUBT`; sin drift => 0 emisiones; el veredicto de drift concuerda con un KS-test independiente.
4. **Via promocion (eval-harness):** un prompt/gramatica que baja F1 vs golden => CI rojo (cero-regresion); solo decisiones TRUSTWORTHY+quorum>=2 promocionan al golden (un ejemplo REFUTADO no contamina).

#### (f) Herramienta NEXT-LEVEL que la eleva a nivel inalcanzable
**llama.cpp** (MIT, €0) — https://github.com/ggml-org/llama.cpp — EL runtime de serving: levanta el endpoint OpenAI-compatible que toda la matriz asume, sirve GGUF Q4 en CPU a €0 con **GBNF nativo** (el piso del guardrail). Convierte "Capa-2 = 0 lineas" en endpoint corriendo [VERIFIED NEXT-LEVEL.md:648-654]. Stack de cierre, todo €0:
- **Outlines** (Apache-2.0) — https://github.com/dottxt-ai/outlines — decodificacion restringida portatil: el decider es **fisicamente incapaz** de emitir fuera de `brand_table`/enum [VERIFIED NEXT-LEVEL.md:656-662].
- **Evidently** (Apache-2.0) — https://github.com/evidentlyai/evidently — cierra el STUB `classifier_drift` (PSI/JS/Wasserstein/chi2): cuando la distribucion de tipos-de-dealer se desplaza, emite `CLASSIFICATION_DOUBT` en vez de `[]` [VERIFIED NEXT-LEVEL.md:616-622].
- **NannyML** (Apache-2.0) — https://github.com/NannyML/nannyml — estima rendimiento **sin etiquetas** (CBPE/DLE): fija y recalibra el confidence-gate por `kind` y dimensiona el lote de escalada [VERIFIED NEXT-LEVEL.md:608-614].
- **Argilla** (Apache-2.0) — https://github.com/argilla-io/argilla — datastore del golden-set por-CC: captura cada decision VAM-VERIFIED como label, gobierna el ciclo de vida (version/dedupe/split) y exporta el set de entrenamiento (profesor Claude -> alumno local) [VERIFIED NEXT-LEVEL.md:632-638].
- **RouteLLM** (Apache-2.0) — https://github.com/lm-sys/RouteLLM — router APRENDIDO barato-vs-fuerte que decide capa-2-vs-Claude ANTES de correr el modelo, minimizando la rafaga Claude-heavy [VERIFIED NEXT-LEVEL.md:672-678]. El contrato del bus es el unico desbloqueo: el dia del GGUF, capa-2 enchufa sin tocar el motor.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-26"></a>
### Faceta 26 · Capa-3 orquestador Claude: drenado en rafagas + apply + re-verificacion VAM
*El cerebro pensante: drenado en ráfagas + apply + re-verificación VAM (apply→VERIFIED gateado).*  ·  **v1:** Infra · cerebro

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — El patron apply->verify es country-agnostic (espeja transition con verdict_id [VERIFIED route.py:261-264]). El seam ES no esta en el orquestador sino aguas arriba: la clasificacion de reversibilidad (faceta 24) y el posible sesgo ES del prosecutor (faceta 12) que valida APPLIED->VERIFIED. El dimensionamiento del lote es global, sin dimension por-CC; una emision sin acotar (faceta 15) lo desborda.
- **Fix exacto** — (1) El drain reusa el guard RESOLVED como predicado APPLIED->VERIFIED: ninguna decision latchea sin recheck VAM efectivo (TRUSTWORTHY+quorum_n>=2). (2) Instrumentar el drain con Langfuse para coste/latencia por decision_request y por pais, y dimensionar el lote por presupuesto. (3) budget-STOP mecanico (LiteLLM) corta la rafaga si excede presupuesto (gate, no prosa). (4) RouteLLM decide barato(local)-vs-fuerte(Claude) para que solo lo dificil consuma rafaga. (5) lens 'fiscal' adversarial contra-desafia cada decision antes de APPLIED.
- **Riesgo adversarial** — Sin capa-2 (faceta 25), el lote de Claude crece con cada pais -> rafaga cara/lenta; mal dimensionado se trunca (decisiones sin tomar) o desborda el contexto. Una decision aplicada sin re-verificacion VAM efectiva (si el prosecutor hereda sesgo ES, faceta 12) latchea un error como VERIFIED. Claude tocando algo MAL clasificado como reversible (faceta 24) es irreversible — y la frontera legal difiere por pais (que es 'legal' en MX/JP no es lo de ES). Un pais EUR0 que inunda decision_request sin emision acotada (faceta 15) convierte la rafaga en DoS de coste.
- **Sellado multi-vía** — Multi-via: (1) GATE MECANICO APPLIED->VERIFIED — ninguna decision latchea sin quorum VAM TRUSTWORTHY+quorum_n>=2 (espejo 0036 [VERIFIED route.py:243-248]). (2) LANGFUSE — coste acumulado por pais consultable; cross-check coste Langfuse vs facturacion Anthropic (deben cuadrar). (3) ADVERSARIAL — una rafaga que excede presupuesto dispara el STOP de LiteLLM budget. (4) GOLDEN DE DECISIONES (promptfoo) — un prompt que baja F1 vs golden = CI ROJO; un ejemplo envenenado (refutado luego por VAM) NO entra al golden (solo TRUSTWORTHY+quorum>=2 promociona).
- **Herramienta NEXT-LEVEL** — Langfuse (MIT core Expat, EUR0) https://github.com/langfuse/langfuse [VERIFIED NEXT-LEVEL.md:691,:84] — observabilidad LLM + ledger de coste para las RAFAGAS de Claude (coste/latencia por decision_request y por pais); habilita el budget-STOP mecanico. Alt: promptfoo (MIT, :603) eval de regresion de decisiones; RouteLLM (Apache-2.0, :675) router barato-vs-fuerte.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### Mecanismo al atomo
Faceta NUEVA (el orquestador no existe aun). El drenado PROGRAMADO (cron del harness, faceta 15) invoca a Claude con el LOTE de PENDING tier=claude sobre decision_request (faceta 23) como UNA sola rafaga; Claude decide+rationale; el motor aplica `state=APPLIED` y RE-VERIFICA por VAM, latcheando `state=VERIFIED` SOLO si el quorum confirma.

**Espejo del invariante de cierre [VERIFIED route.py:197-282]:** el patron apply->verify replica el guard duro de RESOLVED: `transition` exige que para RESOLVED haya `verdict_id` con `verdict='TRUSTWORTHY'` Y `quorum_n >= 2`, si no lanza ValueError '`no real recheck = no closure`' [VERIFIED :229-248]; el trigger DB `trg_gestion_resolved_proof` (0036) es la garantia dura y este es el espejo fail-fast. La re-verificacion reusa `quorum.decide` [VERIFIED quorum.py:159] y `prosecute_claim` [VERIFIED prosecutor.py:115]. Claude NUNCA toca spend/prod/legal sin humano (freno §Autonomia, faceta 24). Un lens adversarial co-igual desafia cada decision ANTES de APPLIED.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-27"></a>
### Faceta 27 · Maquina de estados cover(country_code) + predicados + tick-job
*El orquestador de onboarding: cover(CC) FSM REGISTERED→SEALED guard-gated + tick-job.*  ·  **v1:** Infra · FSM

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — Todo es NUEVO (cero codigo existente). El seam es que el country_code debe threadearse como parametro REAL desde la fila campaign hasta cada literal ES-locked (paths, mint_code, validador de provincia, umbrales de detector, contexto del bus). El substrato (clave geo compuesta de 0053) esta listo; la FSM que lo conduce no. El patron a espejar (route.py VALID_TRANSITIONS) es un dict a mano sin guards ni diagrama — re-rollearlo a mano para cover(CC) es justo el 'reinventar lo que una herramienta resuelve' que la doctrina prohibe.
- **Fix exacto** — Modelar cover(CC) como una Machine declarativa de pytransitions: estados+transiciones declarados una vez, `conditions=`/`unless=` callables apuntando a los predicados ya disenados (geo seed>0, dry-run verde, schedulers activos, predicado de sellado), persistencia via `on_enter` -> UPDATE country_campaign.state, y GraphMachine para auto-renderizar el diagrama del funnel. La libreria impone solo-transicion-legal (sin salto ilegal, p.ej. REGISTERED->SEALED se rechaza), materializando ANTI-DRIFT §2.2 'un componente ejecuta solo el siguiente paso legal'. Los predicados spend/prod/legal resuelven a PENDING-OWNER sin parar el loop (doctrina cardeep). El mismo patron Machine sirve para el work_item del bus. ES byte-identico: cover('ES') sobre un corpus ya sellado es un no-op que re-deriva el mismo estado SEALED.
- **Riesgo adversarial** — Los predicados de transicion son NUEVOS y no probados en vivo; un predicado mal calibrado sella prematuro o atasca el onboarding para siempre. Si el country_code NO se threadea bien hasta los 63 mints de plataforma (faceta 31), una campana cover(DE) acuna codigos CDP-ES- -> rompe G1 (faceta 16) y la identidad DE. Sin el stack vivo (faceta 13) el tick nunca corre y la maquina nunca conduce — todo el onboarding es teorico. Un pais que genere muchas INCONCLUSIVE/ambiguas (cola fina, geo ambigua) inunda el bus que la campana alimenta. Para FR/IT el gate de congelacion de gramatica (faceta 32) DEBE disparar en REGISTERED->BOOTSTRAPPED antes de cualquier mint, o una gramatica de subdivision equivocada se vuelve irreversible. La arista REOPENED (regresion) debe dispararse al voltearse el predicado de sello, o un pais queda SEALED en silencio mientras su cobertura regresa.
- **Sellado multi-vía** — Multi-via: (1) Test de transicion ilegal: intentar REGISTERED->SEALED y aseverar que la libreria la rechaza; cada guard falso bloquea el avance. (2) Paridad de diagrama: el grafo renderizado por GraphMachine debe igualar el contrato de estados del 00-MASTER (diff de aristas + revision visual) — la maquina ES la spec, no prosa. (3) Interceptacion de sello adversarial: forzar un predicado de sello mal calibrado y confirmar que el checkpoint COVERAGE_SEAL_REVIEW al bus intercepta ANTES de latchear SEALED. (4) Test de thread-through: cover('DE') sobre un fixture DE debe producir codigos CDP-DE- de extremo a extremo (cero fuga CDP-ES-), probando que el country_code threadea hasta los mints. (5) Golden no-op ES: cover('ES') re-deriva SEALED con cero efectos secundarios (byte-identidad test_country_coexistence). (6) Prueba de tick vivo: el country_campaign_tick debe disparar de verdad bajo el daemon supervisado (acopla con faceta 13) — gestion_item esta VACIA, asi que la FSM debe ejercitarse bajo carga real, no solo tests.
- **Herramienta NEXT-LEVEL** — transitions (pytransitions) (MIT) — https://github.com/pytransitions/transitions [VERIFIED NEXT-LEVEL.md:592-598, seccion 'Maquina de estados cover(CC) sobre transitions (declarativa, guard-gated, diagramable)'; licencia tambien en tabla resumen :72]. FSM Python battle-tested: estados+transiciones declarativos, guards callable `conditions=`/`unless=` (exactamente el 'predicado computable' que gatea cada transicion), callbacks prepare/after, estados jerarquicos, y GraphMachine para auto-renderizar el diagrama del funnel. Persistir el estado en country_campaign.state (la DB sigue siendo verdad) mientras la libreria impone solo-transicion-legal. Alternativa python-statemachine (MIT, https://github.com/fgmacedo/python-statemachine); el dict route.py:48-58 actual es el piso en-repo (sin diagrama ni guards). EUR0.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) code_hints VERIFICADOS
- [VERIFIED grep] `country_campaign` = 0 refs y `def cover(` = 0 refs en pipeline/ services/ migrations/ -> la FSM, ambas tablas (country_campaign + country_campaign_event) y el driver son NUEVO (no existen).
- [VERIFIED route.py:48-58] `VALID_TRANSITIONS` dict con `RESOLVED -> {REOPENED}` (:55) y `REOPENED -> {ROUTED, IN_PROGRESS, WONT_FIX}` (:56) — la state-machine de gestion_item a espejar para REGISTERED->...->SEALED + REOPENED.
- [VERIFIED scheduler.py:938-1058] familia de 8 add_job: el hogar donde se anade `country_campaign_tick` (aditivo, mismas garantias single-producer + advisory-lock).
- [VERIFIED migrations/0053_country_onboarding.sql header] identidad geo promovida a compuesto (country_code, code); toda fila existente country_code='ES' (entity no-ES=0, geo_province=52, geo_municipality=8.132); 0052 anadio country_code a entity/geo_comarca/geo_municipality. El grano (country_code, code) que la campana threadea esta APLICADO.

#### (b) Mecanismo al atomo
cover(CC) es el orquestador de onboarding: una fila por pais en country_campaign moviendose REGISTERED -> BOOTSTRAPPED -> IN_COVERAGE -> SEALED (+ REOPENED por regresion), con un espejo append-only country_campaign_event (cero updates/deletes — misma disciplina append-only que gestion_transition). Cada transicion la gatea un PREDICADO COMPUTABLE, no Claude: REGISTERED->BOOTSTRAPPED exige toml-validado + geo>0 + fuentes + dry-run verde; BOOTSTRAPPED->IN_COVERAGE exige schedulers activos + 1a cosecha; IN_COVERAGE->SEALED exige el predicado de sellado (faceta 28). Un driver por-estado sabe que subconjunto de las 9 etapas correr. Un job nuevo country_campaign_tick (anadido a la familia del scheduler) avanza la maquina cada ciclo. El country_code viaja como un solo hilo desde la fila campaign -> paths.* -> mint_code -> el validador de subdivision -> el contexto del bus. Onboardar = INSERT country_campaign(CC, REGISTERED) y dejar conducir.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-28"></a>
### Faceta 28 · Predicado de sellado + 2a-via ortogonal + COVERAGE_SEAL_REVIEW
*El predicado SEALED = AND de 5 sub-criterios + 2ª-vía prosecutor + atestación.*  ·  **v1:** Infra · sello

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — Faceta NUEVA que ensambla piezas reales (seal.py:138, complete.py:473-497, 0031 servable/idx_gestion_quar, quorum.py:281-315, prosecutor.py:407-454, test_country_coexistence). country-parametrica por construccion, pero con 3 acoples ES a romper: (i) threshold/margen IC95 globales (seal.py DEFAULT_THRESHOLD=0.95) -> por-CC desde country.toml; (ii) la 2a-via (prosecutor) NO debe compartir TAU_REL/TAU_ABS ES-calibradas con la 1a-via o el doble-recomputo es teatro (faceta 12); (iii) el brazo byte-identity ES es el ancla anti-regresion correcta por diseno.
- **Fix exacto** — 1) Implementar `seal_predicate(cc) -> (sealed, sub_results)` puro que ANDea los 5 sub-criterios leidos por-CC (threshold de country.toml, gestion `WHERE country_code=cc`, VAM por cc, decision_request `WHERE country_code=cc AND state='PENDING' AND blocking`). Fail-closed: cualquier sub-criterio None/error -> NOT sealed. 2) Implementar `verify_seal(cc)` ortogonal que re-deriva coverage_lower y el conteo TRUSTWORTHY desde la `verification_verdict` CRUDA via el prosecutor (prosecutor.py:407/329) SIN leer country_campaign, + las aserciones byte-identity de test_country_coexistence; exigir `|campaign_cov_lower - prosecutor_cov_lower| <= tol` AND ES golden intacto. Desacoplar las tolerancias del prosecutor de las magnitudes ES (TAU inyectado del pack) para que la 2a-via sea genuinamente independiente. 3) Emitir COVERAGE_SEAL_REVIEW al bus (faceta 23) al pasar el predicado; latchear SEALED solo tras que Claude adjudique AND verify_seal concuerde; rechazar si el sello altera algun ES golden. 4) Anadir el replay contrafactual: persistir coverage_lower + ancho IC por build como serie temporal sobre la historia append-only (exhaustiveness_estimate 0048) y tratar SEALED como propiedad de convergencia de un intervalo que ENCOGE, no evento binario — para anticipar REOPENED.
- **Riesgo adversarial** — Predicado que agrega mal 1 de 5 sub-criterios sella incompleto o bloquea para siempre (contar uncertified como cubierto -seal.py:91-95 lo evita pero un parametro mal lo colaria-; o tratar INCOMPLETE-por-G5-deferred como bloqueo duro). 2a-via que comparte sesgo ES con la 1a (faceta 12) vuelve el doble-recomputo TEATRO (ambos yerran igual). Sin replay contrafactual el sello es binario y no anticipa REOPENED. Frontera 'bloqueante' spend/prod/legal difiere por pais (que es 'legal' en MX/JP) -> filtro global mis-gatea. no-UE: sin censo externo (faceta 21 no_anchor) coverage_lower carece de check ortogonal -> el sub-criterio 1 certifica un numero que nada confirma.
- **Sellado multi-vía** — La faceta ES el gate de sello, asi que su propio 'sealed' significa: (a) `seal_predicate(cc)` puro, fail-closed, unit-tested para cada rama-falsa bloqueante; (b) `verify_seal(cc)` recomputa desde verification_verdict independiente y las dos cifras coinciden dentro de tol (una inyeccion deliberada de sesgo ES en un brazo debe hacerlos DISCREPAR — test adversarial); (c) COVERAGE_SEAL_REVIEW llega al bus y la adjudicacion de Claude es requisito previo al latch (guard transitions/GraphMachine intercepta, NEXT-LEVEL:598); (d) ES byte-identity verde (test_country_coexistence) y todo sello que mueva ES es rechazado; (e) replay contrafactual sobre la serie historica reproduce el sello y muestra el intervalo encogiendo (saturacion), no derivando. Multi-via: predicado determinista (CI) + recomputo independiente del prosecutor (2a-via) + adjudicacion de Claude (3a, co-igual) + atestacion criptografica re-verificable por terceros (herramienta).
- **Herramienta NEXT-LEVEL** — PRIMARIA: in-toto + Sigstore/cosign/rekor (Apache-2.0, EUR0) — https://github.com/in-toto/in-toto [VERIFIED NEXT-LEVEL.md:143 y :640-647, tabla:16 y :78]. Hoy SEALED es solo una fila de DB. in-toto emite una atestacion que liga {country_code, intervalo [cota_inf,cota_sup], set exacto de migraciones, content-hashes de TODO input (census CSV, matriz de captura, membresias de lista, versiones de estimador, hashes modelo+gramatica+prompt), los verdicts VAM} -> {coverage_lower, CI, N_hat por estrato}, firmada (cosign keyless OIDC) y anclada en un transparency log rekor tamper-evident con prueba de inclusion. CUALQUIER tercero (auditor, regulador del pais, comprador) puede PROBAR 'este 80,5% salio de exactamente estos inputs y este codigo' sin screenshot, sin dashboard, sin confiar en nosotros; el sello deja de ser afirmacion y pasa a certificado no-repudiable. in-toto graduo en CNCF (2025-02-10). Verificacion: re-correr desde los content-hashes atestiguados -> coverage_lower BYTE-identico (gate reproducibilidad); alterar UNA fila del census -> la atestacion FALLA (2a-via adversarial); prueba de inclusion rekor chequeada en CI cada push (3a-via). Es el 'doble recomputo + 2a-via ortogonal' de la faceta elevado a certificacion externamente-verificable (NEXT-LEVEL:140-146,:640). SOPORTE: DVC (Apache-2.0, EUR0) — https://github.com/iterative/dvc [VERIFIED:151, tabla:17]: versionado content-addressed de los INPUTS para que cada build_run_id sea bit-reproducible (`dvc repro` reproduce coverage_lower identico; mismatch de checksum ABORTA), justo lo que hace del replay contrafactual/serie de saturacion una medicion real y no drift disfrazado (NEXT-LEVEL:148-154). Y Great Expectations/Pandera (Apache-2.0, EUR0) — https://github.com/great-expectations/great_expectations [VERIFIED:167, tabla:19]: contrato de datos PRE-sello para que cada estrato falle CERRADO, no abierto (caza el bug bucket_for-falla-abierto-a-MKT donde el roster extranjero desaparece del MSE y coverage_lower sub-cuenta) — la forma ejecutable de la disciplina fail-closed del predicado (NEXT-LEVEL:164-170). Para la adjudicacion COVERAGE_SEAL_REVIEW: promptfoo/Inspect (MIT, :603) vuelve el bus un gate de eval-de-decisiones cero-regresion. Todo EUR0/CPU.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) Verificacion de code_hints [VERIFIED] (faceta NUEVA que ENSAMBLA piezas reales)
- `seal.py:39-47` [VERIFIED]: `_seal_one` -> `sealed = e.identified AND isfinite(cov_lower) AND cov_lower>=threshold`. `:138` national `sealed = cov_lower>=threshold` (`cov_lower = n_obs_cert/nat_ci_high`, cota inferior conservadora, `:107`).
- `complete.py:473-497` [VERIFIED]: `derive_verdict` — `COMPLETED <=> g1 AND g2 AND g3 AND g4 AND g5 AND is_fresh`; cualquier `None` -> `INCOMPLETE`. G5 es stub (`check_g5_stub:452-466` devuelve `(None,reason)`) -> toda entidad INCOMPLETE mientras G5 deferred.
- `0031_gestion.sql:146-168` [VERIFIED]: `servable_entity`/`servable_vehicle` excluyen mecanicamente subjects con `gestion_item` cuarentenante abierto (`g.quarantines AND g.closed_at IS NULL`); el `idx_gestion_quar` (scope) sirve el sub-criterio '0 cuarentenantes abiertos'.
- `quorum.py:281-315` [VERIFIED]: `TRUSTWORTHY <=> n_star>=2 AND not rival AND (rs+ab)<n_star`, con precision-gate (Wilson `ci_upper<=p0`); precision fallida -> `INCONCLUSIVE` (no REFUTED). Sirve el sub-criterio 'veredictos VAM TRUSTWORTHY quorum>=2'.
- `prosecutor.py:407-454` [VERIFIED]: `emit_claim_from_verdict(verification_verdict_row)` re-deriva un `inquisition_claim` desde la fila CRUDA `verification_verdict` (`primary_value`/`primary_path` `:431-432`), el bridge §9 — independiente de la fila campaign. `prosecute_pending:329` poll de PENDING. Es la 2a-via que NO lee la campaign.
- `tests/test_country_coexistence.py:105-149` [VERIFIED]: prueba ES `cdp_code`/`canonical_key`/`paths` byte-identicos (`TestEsByteIdentityUnchangedByCoexistence`); `:151-209` DE coexiste (PK geo compuesta, txn reversible). Es el brazo 'ES byte-identity' del sello + la regla 'un sello que mueva ES es RECHAZADO'.
- Las tablas `country_campaign`/`country_campaign_event` y la FSM `cover(CC)` son faceta 27 (`grep country_campaign|def cover( = 0`); ESTA faceta es el PREDICADO SEALED + su doble-recomputo.

#### (b) Mecanismo al atomo
`SEALED` lo COMPUTA `cover(CC)` como un AND determinista de 5 sub-criterios, todos a la vez:
1. `coverage_lower >= threshold` con margen IC95 (la cifra certificada `n_obs_cert/nat_ci_high`, NUNCA el punto — `seal.py:107/138`);
2. G1-G4 verdes (`derive_verdict` sobre las entidades del pais, facetas 18/19) — honesto en que G5 esta deferred;
3. 0 `gestion_item` cuarentenante critico abierto (`idx_gestion_quar`; las vistas `servable_*` ya ocultan mecanicamente);
4. veredictos VAM TRUSTWORTHY con quorum>=2 (`quorum.py:281-315`);
5. 0 `decision_request` bloqueante PENDING (bus, faceta 23).

Crucial: el predicado lo COMPUTA `cover(CC)` pero lo VERIFICA una 2a-via que **NO lee la fila campaign**: el prosecutor re-deriva cobertura/quorum desde la `verification_verdict` CRUDA (`prosecutor.py:407-454` + `prosecute_pending:329`), y `test_country_coexistence` prueba ES byte-identico. Las DOS recomputaciones (campaign-side vs prosecutor-side) deben coincidir dentro de tolerancia — mismo principio que el guard DB `RESOLVED => TRUSTWORTHY+quorum>=2` (migracion 0036) y que el propio sello "nunca certificar sin recheck independiente". Luego se emite un `COVERAGE_SEAL_REVIEW` al bus para que Claude ADJUDIQUE el sello co-igualmente ANTES de latchear; un sello cuya aplicacion mueva ES es un sello RECHAZADO.

#### (c) Costura ES->generico
El predicado es NUEVO y country-parametrico por construccion (el `country_code` viaja desde la fila campaign por `paths.*`, el threshold del sello, el filtro `gestion_item`, el scope VAM y el contexto del bus). Riesgos de acople ES: (i) `threshold` y margen IC95 son constantes globales hoy (`seal.py DEFAULT_THRESHOLD=0.95`) — deben ser por-CC desde country.toml; (ii) la 2a-via (prosecutor) NO debe compartir tolerancias ES-calibradas (`TAU_REL`/`TAU_ABS`, supuestos de magnitud) con la 1a-via, o el 'doble recomputo' es teatro (arrastra el mismo sesgo ES que pretende auditar — faceta 12); (iii) el brazo byte-identity es ES-especifico por diseno (test_country_coexistence fija ES) y es el ancla anti-regresion correcta.

#### (d) Riesgo adversarial concreto
- Un predicado que agregue MAL cualquiera de los 5 sub-criterios sella un pais incompleto o lo bloquea para siempre (p.ej. contar estrata uncertified como cubierto — `seal.py` ya lo evita reportandolos aparte `:91-95`, pero un parametro mal puesto los colaria; o tratar el INCOMPLETE-por-G5-deferred como bloqueo duro cuando es pendiente-declarado).
- Si la 2a-via comparte estado/sesgo ES con la 1a (faceta 12), el 'doble recomputo' es **teatro**: ambos brazos concuerdan porque ambos yerran igual.
- Sin sellado contrafactual (replay temporal sobre la historia append-only), el sello es un evento binario que **no anticipa** la regresion que dispara REOPENED — el pais salta SEALED->REOPENED sin serie de aviso.
- **Frontera legal por-pais**: que cuenta como PENDING 'bloqueante' (spend/prod/legal, faceta 24) difiere por pais (que es 'legal' en MX/JP difiere), un filtro global mis-gatea el sello.
- **no-UE**: sin censo externo (faceta 21 `no_anchor`), `coverage_lower` carece de check ortogonal, el sub-criterio 1 se computa sobre un denominador no verificado — el sello certifica un numero que nada confirma.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-29"></a>
### Faceta 29 · Cargador del country-pack (manifest country.toml + loader cacheado por-CC)
*El backbone declarativo: country.toml + loader fail-fast cacheado por-CC.*  ·  **v1:** Infra · backbone

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — El manifest NO existe [find countries -name '*.toml' = 0]; countries/ES/ tiene solo 01..50/_platforms/_tier1/census/recipes. paths.py YA centraliza las raices FS por-CC (DEFAULT_COUNTRY='ES', byte-identico) y country_of_cdp deriva el CC [paths.py:30,55-63], PERO no hay seam de PARAMETROS: _PROVINCE_RE, LANE_SLA, COVERAGE_ANCHORS, umbrales, threshold siguen como literales de modulo ES.
- **Fix exacto** — (1) Crear countries/{CC}/country.toml: country_code, subdivision_validator (sustituye _PROVINCE_RE), national_kinds, kind_lexicon local->canonico, [lane_sla]/[cadence] overrides, geo_backbone ref, classifier_golden ref, [[sources]] con harvest_interval_hours. (2) loader load_country_pack(cc) cacheado por-CC, resuelto via paths.country_of_cdp, con validacion fail-fast al arranque. ES.toml declara province 01-52, SLA 6h/7d/48h, anclas 1292/2018/1662/29955, threshold 0.95 -> salida byte-identica.
- **Riesgo adversarial** — Fallback silencioso: sin manifest/validacion cada faceta inyectable cae a literales ES -> el pais nuevo corre con parametros espanoles (CI verde, prod roto). Un .toml mal validado (rango subdivision) propaga a G1 (16), sellador (20-22) y mints (31); por inmutabilidad del cdp_code (faceta 32) parte del dano es IRREVERSIBLE (re-mintear huerfana el ledger). Drift de registry: fuente sembrada sin entrada pasa silenciosa sin guard tipado.
- **Sellado multi-vía** — Via1 ES byte-identity: ES.toml reproduce el hardcode en cada consumidor (province regex, LANE_SLA, anclas, threshold). Via2 fail-fast: .toml malformado (rango invalido/campo ausente/ancho que no cabe) -> error al arranque/CI ROJO, nunca fallback silencioso. Via3: load_country_pack(cc) idempotente y cacheado por-CC. Via4 biyeccion: UNMAPPED del guard tipado == _gap_report SQL; source_health<->registry<->lock_key = 0 UNMAPPED/0 ORPHAN.
- **Herramienta NEXT-LEVEL** — Frictionless Framework (frictionless-py, Table Schema) — MIT — https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:337], nombrado por la biblia exactamente como 'Country-pack como CONTRATO de datos auto-verificado' (NEXT-LEVEL.md:334): valida tipos/regex/ANCHO-bytes per-pais ANTES del INSERT. Complemento: Pydantic — MIT — https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587]: CountryPack(BaseModel) + test de biyeccion source_health<->registry<->lock_key 0 UNMAPPED (NEXT-LEVEL.md:585,590). Frictionless = datos tabulares; Pydantic = manifest .toml escalar/regex. €0, CI sin DB viva.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) code_hints VERIFICADOS
- **El manifest NO existe** [VERIFIED `find countries -name '*.toml'` = 0]. `countries/ES/` contiene solo dirs de provincia `01..50` (con huecos 16/40/42/44 en el listado), `_platforms`, `_tier1`, `census`, `recipes` — **ningun `.toml`**.
- **paths.py ya centraliza las raices FS por-pais** [VERIFIED pipeline/paths.py]: `DEFAULT_COUNTRY = "ES"` [paths.py:22]; `recipe_root` (33-36), `recipes_flat_dir` (39-41), `data_root` (44-47), `census_dir` (50-52) **todas con default ES** (paths byte-identicos al literal pre-refactor); `country_of_cdp` (55-63) deriva el CC de un cdp_code via `_CDP_COUNTRY_RE = re.compile(r"^CDP-([A-Z]{2})-")` [paths.py:30], default a `DEFAULT_COUNTRY` para basura.
- **Consumidores que aun leen literales ES** [VERIFIED por referencias cruzadas]: `complete.py:73` `_PROVINCE_RE` (faceta 16), `detect.py:78-83` COVERAGE_ANCHORS / `detect.py:68-107` umbrales (facetas 5/8), `route.py:28-34` LANE_SLA (faceta 1).
- **Conclusion verificada:** existe el seam de **rutas** (paths.py) pero NO el seam de **parametros** (no hay manifest ni loader); cada parametro inyectable sigue como literal de modulo ES.

#### (b) El mecanismo al atomo
El country-pack es el **backbone declarativo** del que dependen casi todas las costuras inyectables. Hoy `paths.py` resuelve DONDE viven los datos de un pais (defaulteando a ES), pero no hay una pieza que diga COMO se comporta el motor para ese pais. El cargador propuesto es **un loader unico cacheado por-CC** (`@lru_cache` por country_code) que lee `countries/{CC}/country.toml`, lo valida fail-fast al arranque, y entrega un objeto tipado que el motor consume en cada costura: `_PROVINCE_RE` (faceta 16), `[lane_sla]` (faceta 1), `[coverage_anchors]` (faceta 8), umbrales detector (faceta 5), `[seal].coverage_threshold` (faceta 22), cadencias (faceta 15), ref al backbone geo, ref al golden-set del clasificador, lista-semilla de fuentes con `harvest_interval_hours`.

#### (c) Costura ES->generico + fix exacto
La costura es **la ausencia misma del manifest+loader**: sin el, cada faceta inyectable cae de vuelta a su literal ES silenciosamente.
**Fix:** (1) crear `countries/{CC}/country.toml` con el contrato: `country_code`, `subdivision_validator` (regex/rango que sustituye `_PROVINCE_RE`), `national_kinds` override, `kind_lexicon` local->canonico, overrides `[lane_sla]`/`[cadence]`, `geo_backbone` ref, `classifier_golden` ref, `[[sources]]` con `harvest_interval_hours`. (2) un loader `load_country_pack(cc)` cacheado por-CC, **resuelto via `paths.country_of_cdp`** (el seam de rutas ya existe), con **validacion fail-fast al arranque** (campos requeridos, tipos, rangos). ES queda **declarado en su `.toml` de forma que su salida sea byte-identica al hardcode actual** (province 01-52, LANE_SLA 6h/7d/48h, anclas 1292/2018/1662/29955, threshold 0.95).

#### (d) Riesgo adversarial concreto
- **Fallback silencioso:** si el manifest no existe o el loader no valida, cada faceta inyectable (province-validator, umbrales, anclas, SLA, fuentes) cae a sus literales ES -> **el pais nuevo corre con parametros espanoles silenciosamente** (el modo de fallo mas insidioso: CI verde, prod roto).
- **Propagacion irreversible:** un `.toml` mal validado (rango de subdivision incorrecto) propaga el error a G1 (faceta 16), al sellador (facetas 20-22) y a los **mints** (faceta 31) — y por inmutabilidad del cdp_code (faceta 32) **parte del dano es irreversible** (re-mintear huerfana el ledger append-only).
- **Drift de registry:** una fuente sembrada sin entrada de registry (o registry sin semilla) pasa silenciosa sin un guard tipado.

#### (e) Criterio de sellado + verificacion multi-via
- **Via 1 (ES byte-identity):** cargar `ES.toml` produce salida byte-identica al hardcode en CADA consumidor (province regex, LANE_SLA, anclas, threshold) — golden.
- **Via 2 (fail-fast):** un `.toml` malformado (rango invalido, campo requerido ausente, ancho de codigo que no cabe) -> **error al arranque/CI ROJO**, jamas fallback silencioso.
- **Via 3 (loader cacheado):** test de que `load_country_pack(cc)` es idempotente y cacheado por-CC (una lectura por pais).
- **Via 4 (biyeccion):** el conteo UNMAPPED del guard tipado == el del `_gap_report` SQL (--dry-run); `source_health <-> registry <-> lock_key` por pais activo = 0 UNMAPPED / 0 ORPHAN.

#### (f) Herramienta NEXT-LEVEL
**Frictionless Framework (frictionless-py, Table Schema)** — MIT, https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:337]. La biblia lo nombra **exactamente para esto**: "Country-pack como CONTRATO de datos auto-verificado" [NEXT-LEVEL.md:334]. Declara cada dataset del pack (backbone provincia/comarca/municipio, centroides, gazetteer CP, alias) como un Table Schema con tipos, regex de forma de codigo y, keystone, el **ANCHO en bytes per-pais**; valida el pack ANTES de cargar una sola fila -> un AGS-DE de 8 digitos, ISTAT-IT de 6, freguesia-PT de 6 o DOM-FR de 3 que no quepan FALLAN con mensaje claro en vez de reventar con "value too long for type character(5)" a mitad del seed.
**Complemento:** **Pydantic** — MIT, https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587]: modela `country.toml` como `CountryPack(BaseModel)` con validators de coherencia + un test de CI que asevera la biyeccion `source_health<->registry<->lock_key` (0 UNMAPPED/0 ORPHAN) [NEXT-LEVEL.md:585,590] — convierte un hueco silencioso de onboarding en un build ROJO mecanico. Frictionless gobierna los datos tabulares del pack; Pydantic gobierna el manifest escalar/regex `.toml`. Ambos €0, corren en CI sin DB viva (fixtures).

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-30"></a>
### Faceta 30 · Gobernanza de extension del ENUM entity_kind (no es override declarativo)
*Un kind nuevo = ALTER TYPE = MIGRACIÓN, no un override declarativo en .toml.*  ·  **v1:** Clúster F

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — entity_kind es ENUM Postgres (0005:13-17 define 11 valores; 0017_particular_kind.sql:21 anade el 12o 'particular' via ALTER TYPE). El pack aporta el lexico local->canonico y QUE kinds aplican, PERO un kind genuinamente nuevo (keiretsu JP, lote MX) exige ALTER TYPE ADD VALUE = MIGRACION, no un override .toml. Las constantes por-kind (STALENESS_TTL :51-63, PRICE_TRAP_FLOOR :90-100) deben cubrir cada valor activo o cae a default.
- **Fix exacto** — (1) country.toml declara kinds canonicos aplicables + mapa lexico local->canonico (validado). (2) Kind nuevo dispara migracion ALTER TYPE entity_kind ADD VALUE (espeja 0017_particular_kind.sql), como decision_request reversibility=prod (humano), NUNCA override .toml. (3) Guard tipado (Pydantic) en CI: todo kind del .toml pertenece al ENUM, y todo valor activo del ENUM tiene entrada en STALENESS_TTL y PRICE_TRAP_FLOOR (cierra el default-silencioso que ya viola agente_oficial/cadena en ES).
- **Riesgo adversarial** — Lote MX / keiretsu JP exigen ALTER TYPE; declararlos via .toml falla con error de ENUM (fail-closed). PEOR el silencioso: kind nuevo sin entrada en STALENESS_TTL/PRICE_TRAP_FLOOR cae a default -> staleness/price_trap mal calibrados sin error (bug ya vivo en ES con agente_oficial/cadena). DE/FR/IT/PT mapean a kinds existentes (riesgo default-silencioso si falta el dict). No-UE: kind genuinamente nuevo. Ruido: clasificador con kind no-canonico debe rechazarse.
- **Sellado multi-vía** — (1) country.toml valida contra esquema Pydantic en CI: 0 kinds fuera del ENUM, biyeccion kind<->constantes. (2) Test enumera enum_range(entity_kind) y asevera STALENESS_TTL + PRICE_TRAP_FLOOR cubren cada valor activo (cierra agente_oficial/cadena en ES); golden ES intacto. (3) Adversarial: kind no-en-ENUM => error tipo; kind .toml sin migracion => CI rojo. (4) Ruta de migracion probada (precedente 0017/0033).
- **Herramienta NEXT-LEVEL** — Pydantic (MIT, EUR0) https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:584-590] — guard de drift como CONTRATO TIPADO en CI: CountryPack(BaseModel) valida country.toml contra el esquema (kinds del ENUM) y asevera la biyeccion kind-activo<->constantes (0 UNMAPPED), convirtiendo el default-silencioso en build ROJO. Corre sin DB viva. Alt: jsonschema, Cerberus.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### Mecanismo al atomo [VERIFIED — con correccion de conteo]
- **migrations/0005_types_and_guards.sql:12-18** `CREATE TYPE entity_kind AS ENUM (...)` define **11 valores** [VERIFIED, NO 12 como dice el code_hint]: concesionario_oficial, agente_oficial, compraventa, garaje, desguace, rent_a_car_vo, subasta, importador, oem_vo_portal, plataforma, `cadena` (:16, DEPRECATED read-only, D-11).
- **migrations/0017_particular_kind.sql:21** `ALTER TYPE entity_kind ADD VALUE IF NOT EXISTS 'particular';` ANADE el 12o valor. => HOY el ENUM tiene **12** (11 base + particular via migracion). La faceta dice "0005:13-17, 12 valores" y lista 11 sin 'particular' — impreciso por partida doble: 0005 define 11, y el 12o real es 'particular' (no el que la faceta enumera). **ESTA migracion 0017 es la PRUEBA VIVA de la tesis de la faceta**: un kind nuevo = ALTER TYPE = MIGRACION, no un override en country.toml. Precedente REFORZADO por migrations/0033_evict.sql:22 `ALTER TYPE entity_status ADD VALUE IF NOT EXISTS 'evicted'` (mismo patron en otro ENUM).
- Es un ENUM Postgres, NO un set declarativo: una insercion de kind fuera del ENUM falla con error de tipo (fail-closed ruidoso).
- **Constantes indexadas por valor del ENUM** [VERIFIED]: detect.py:51-63 `STALENESS_TTL` tiene claves para 10 kinds + '_entity', **FALTAN agente_oficial y cadena**. detect.py:90-100 `PRICE_TRAP_FLOOR` tiene 9 kinds, **FALTAN agente_oficial, cadena y desguace**. => incluso DENTRO de ES, agente_oficial/cadena ya caen a default SILENCIOSAMENTE hoy. complete.py:83-85 `_NATIONAL_KINDS` es un subconjunto {subasta,plataforma,oem_vo_portal,importador}.

#### Costura ES->generico
El vocabulario canonico de kind es COMPARTIDO (un dealer aleman se clasifica en los MISMOS kinds; el pack solo aporta el lexico local->canonico). PERO el diseno asume erroneamente que el country-pack "solo aporta lexico declarativo". La costura real: un kind GENUINAMENTE nuevo (keiretsu de subastas JP, "lote"/agencia de seminuevos MX, kei-car) exige `ALTER TYPE entity_kind ADD VALUE` = MIGRACION, no un override .toml. Y las constantes por-kind (TTL, price-floor) deben tener entrada para CADA valor del ENUM activo o el default silencioso reaparece.

#### Riesgo adversarial concreto
El "lote" MX o el keiretsu de subastas JP necesitan ALTER TYPE = migracion; si el country-pack intenta declarar el kind nuevo via .toml, las inserciones fallan con error de ENUM (fail-closed ruidoso, recuperable). PEOR es el SILENCIOSO: un kind nuevo SIN entrada en STALENESS_TTL/PRICE_TRAP_FLOOR cae a default -> staleness/price_trap mal calibrados para ese kind sin un solo error (exactamente el bug que ya vive en ES con agente_oficial/cadena). DE/FR/IT/PT: probablemente mapean a los kinds existentes (riesgo de ENUM-extension bajo, pero riesgo de default-silencioso ALTO si un kind canonico del pais no esta en los dicts). No-UE (MX/JP): riesgo alto de kind genuinamente nuevo. Ruido: un clasificador que emite un kind no-canonico debe RECHAZARSE, no insertarse.

#### Sellado + verificacion multi-via
1. **Contrato tipado**: country.toml valida contra esquema en CI: 0 kinds fuera del ENUM; biyeccion kind-activo <-> dict-de-constantes completa.
2. **Multi-via**: test que enumera el ENUM (`SELECT enum_range(NULL::entity_kind)`) y asevera que cada valor activo del pais tiene entrada en STALENESS_TTL y PRICE_TRAP_FLOOR (cierra de paso el hueco agente_oficial/cadena ya presente en ES); golden ES intacto.
3. **Adversarial**: insertar un kind no-en-ENUM => error de tipo (fail-closed); declarar en .toml un kind sin migracion => CI rojo; source_key/kind duplicado entre packs => guard de disjuntez lo bloquea.
4. **Ruta de migracion probada**: la extension del ENUM ya tiene precedente ejecutable (0017_particular_kind.sql, 0033_evict.sql) — el sellado de un pais con kind nuevo EXIGE su migracion ALTER TYPE, declarada como decision_request reversibility=prod (humano), no un override.

#### Herramienta NEXT-LEVEL
**Pydantic** (MIT) https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:584-590, "Guard de drift de registry/semilla como CONTRATO TIPADO en CI"]: CountryPack(BaseModel) con validators de coherencia que (a) valida cada country.toml contra el esquema (todo kind declarado pertenece al ENUM entity_kind) y (b) asevera la biyeccion kind-activo <-> constantes por-kind (0 UNMAPPED / 0 ORPHAN). Convierte el hueco silencioso (kind sin TTL/floor cae a default) en un build ROJO mecanico. Corre en CI sin DB viva (fixtures), EUR0. Alternativas: jsonschema (validacion declarativa pura sin tipos Python), Cerberus.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-31"></a>
### Faceta 31 · Threading de pais en los mints de plataforma (CDP-ES- -> mint_code(country_code=))
*31 fugas f"CDP-ES-", 0 usan mint_code(): un solo hogar del prefijo + guard CI.*  ·  **v1:** Clúster J

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — CORRECCION: la faceta dice 63 ficheros; REAL [VERIFIED] = 47 .py en pipeline/platform/, 31 con literal de fuga f"CDP-ES-...", 0 con mint_code (confirma '0 usan mint_code'), 40 importan cdp_code (mints de dealer YA canonicos). La fuga es el mint de ENTIDAD-PLATAFORMA con centinela (autocasion_platform_cdp_code() :144 construye el prefijo con _base32 bypaseando mint_code), NO los mints de dealer. El docstring codes.py:48-49 'exactly one place' es HOY FALSO.
- **Fix exacto** — Fix de motor una vez: reemplazar cada f"CDP-ES-..." de centinela-plataforma por mint_code(province_code=SENTINEL, digest=digest, country_code=cc); threadear cc=campaign.country_code por el connector desde country_campaign; hacer verdadero el docstring 'exactly one place'; guard mecanico CI prohibiendo f"CDP-..." fuera de codes.py. ES byte-identico (mint_code default='ES', _base32 sin cambio, golden).
- **Riesgo adversarial** — cover(DE) cosechando via platform connector seguiria acunando CDP-ES-* -> rompe G1 (faceta 16) e identidad alemana. Transversal: BLOQUEA el minteo de cover(CC) para todo pais cosechado por plataforma. 31 sitios de fuga, cada uno independiente; cdp_code inmutable (faceta 32) -> un CDP-ES acunado para entidad DE es dano permanente (no se corrige sin orfanar el ledger).
- **Sellado multi-vía** — Sello: golden ES (centinela-plataforma + dealer byte-identico); guard grep/AST 0 literales f"CDP- fuera de codes.py (CI-rojo ante fuga); fixture DE -> cover(DE) por plataforma acuna CDP-DE-* y pasa G1; 2a via property test (forall cc) prefijo == f"CDP-{cc}-"; docstring 'exactly one place' como invariante verificado, no prosa.
- **Herramienta NEXT-LEVEL** — Hypothesis (MPL-2.0, EUR0) https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:317-323]: property test (forall country_code, province/centinela) mint_code emite CDP-{cc}-{NN}-{8} bien-formado y ES byte-identico; caza cualquier literal fugado, minimiza el contraejemplo y lo congela como golden (acopla faceta 17). Complemento piso: guard mecanico AST/grep CI (EUR0) que el literal f"CDP- vive solo en codes.py.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) Verificacion de code_hints [VERIFIED] — CORRECCION del conteo "63"
- [VERIFIED `ls pipeline/platform/*.py | wc -l` = **47**] ficheros .py (NO 63 como dice la faceta).
- [VERIFIED `grep -lE 'f["\']CDP-ES-' pipeline/platform/` = **31**] ficheros con un **literal de mint** `f"CDP-ES-..."` (el mint de la entidad-plataforma con centinela).
- [VERIFIED `grep -l mint_code pipeline/platform/` = **0**] ficheros llaman `mint_code()` directo -> **confirma** el "0 usan mint_code" de la faceta.
- [VERIFIED `grep -l 'from services.api.codes import' pipeline/platform/` = **40**] ficheros importan de `codes` y usan `cdp_code()`: los mints de **DEALER** YA enrutan por `cdp_code()` -> `mint_code()`.
- Ejemplo [VERIFIED pipeline/platform/autocasion_wholesale.py]: `from services.api.codes import _base32, cdp_code` [:73]; `PLATFORM_PROVINCE_SENTINEL="00"` [:132]; `autocasion_platform_cdp_code()` -> `return f"CDP-ES-{PLATFORM_PROVINCE_SENTINEL}-{_base32(digest)}"` [:144] (**LA FUGA** — construye el prefijo con `_base32`, bypaseando mint_code); `cdp_code_dealer()` -> `cdp_code(province_code=d.province_code, ...)` [:477] (**ya canonico**).
- [VERIFIED codes.py:48-49] docstring afirma "Every coder (this module plus the ~30 pipeline/platform mints) routes through here, so CDP-{country}- exists in exactly one place" -> **HOY FALSO**: los 31 mints-centinela construyen el prefijo directo, no via mint_code (grep mint_code=0).

> **Honestidad cruda:** la faceta dice "63 ficheros ... 63 con CDP-ES". El recuento REAL es 47 ficheros .py, **31** con el literal de fuga, **0** con mint_code. El framing tambien necesita matiz: la fuga es el **mint de entidad-plataforma con centinela** (estilo `autocasion_platform_cdp_code()`), NO los mints de dealer (que en 40 ficheros ya van por `cdp_code()`->`mint_code()`). Que los 31 sigan identico patron es [ASSUMED del docstring-espejo "Mirrors coches_net_platform_cdp_code() so all platforms mint codes the same way"], verificado solo en autocasion_wholesale.

#### (b) Mecanismo al atomo
Cada connector de plataforma acuna un codigo de **entidad-plataforma** con `f"CDP-ES-{SENTINEL='00'}-{_base32(digest)}"` hardcodeado, construyendo el prefijo inmutable **fuera** del unico hogar legitimo (`mint_code`). El `country_code` jamas llega al connector. Los codigos de dealer en los mismos ficheros SI van por `cdp_code()` (que acepta `country_code=`, default 'ES').

#### (c) Costura ES->generico + fix exacto
**Fix de MOTOR una vez:** (a) reemplazar cada literal `f"CDP-ES-..."` de centinela-plataforma por `mint_code(province_code=PLATFORM_PROVINCE_SENTINEL, digest=digest, country_code=cc)`; (b) threadear `cc=campaign.country_code` por el entrypoint del connector desde la fila `country_campaign`; (c) hacer **VERDADERO** el docstring "exactly one place" (un solo hogar del prefijo); (d) anadir un **guard mecanico de CI** que prohiba todo literal `f"CDP-...-"` fuera de codes.py. La salida ES queda byte-identica (mint_code default='ES', `_base32` sin cambio, fijado por golden). El `country_code` debe viajar: fila campaign -> connector -> mint.

#### (d) Riesgo adversarial concreto
Una campana `cover(DE)` que cosecha via un platform connector seguiria acunando **CDP-ES-*** -> rompe G1 (faceta 16) y la identidad del pais aleman. Es **transversal** y BLOQUEA el minteo de `cover(CC)` para TODO pais cosechado por plataforma. Con 31 sitios de fuga y 0 usando el helper, **cada fichero es una fuga independiente** del prefijo; y como cdp_code es inmutable (faceta 32), un CDP-ES acunado para una entidad DE es **dano permanente** (no se corrige sin orfanar el ledger).

#### (e) Sellado + verificacion multi-via
- **Sello:** (i) golden ES: cada codigo centinela-plataforma + dealer byte-identico; (ii) guard grep/AST: **0** literales `f"CDP-` fuera de codes.py (mecanico, CI-rojo ante fuga); (iii) fixture DE: una cosecha `cover(DE)` por plataforma acuna `CDP-DE-*` y pasa G1; (iv) 2a via: property test (forall cc) el prefijo acunado por el connector == `f"CDP-{cc}-"`; (v) el docstring "exactly one place" pasa de prosa a invariante verificado.
- **Multi-via:** 1a golden ES; 2a guard mecanico de literal; 3a property-based cross-country.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**Hypothesis** (MPL-2.0, EUR0) — https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:317-323, cluster extraction-scrape, property-based-recipe-fuzzing]. Un property test que para **TODO** country_code y TODO input de province/centinela, `mint_code` emite un `CDP-{cc}-{NN}-{8}` bien-formado y ES queda byte-identico — el fuzzer **caza cualquier literal fugado** o alfabeto de subdivision que rompa la gramatica (acopla con faceta 17), **minimiza** al contraejemplo mas simple y lo congela como golden de regresion. **Complemento (piso sin dependencia):** un **guard mecanico AST/grep en CI** (EUR0) que asevera que el literal del prefijo `f"CDP-` vive **solo** en codes.py — el invariante country-proof hecho ejecutable. Asi "un solo hogar del prefijo" deja de ser prosa y se vuelve gate.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-32"></a>
### Faceta 32 · Gate de congelacion de gramatica (anti-irreversibilidad del codigo inmutable)
*Anti-irreversibilidad: congelar la gramática de {NN} ANTES del primer mint.*  ·  **v1:** Clúster B

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — El cdp_code es INMUTABLE [codes.py:1] y mint_code [codes.py:44-53] es el unico hogar del prefijo pero acepta cualquier string como province_code: el invariante de ancho/alfabeto [0-9]{2} solo vive en validadores que lo consumen (complete.py:89 _CDP_CODE_RE, :73 _PROVINCE_RE 01-52), y paths.py:30 solo parsea el CC, no el NN. Todo el resto del onboarding es additive+reversible (migraciones con rollback, cuarentena reversible) PERO la gramatica del codigo NO: gestion_item/gestion_transition (0031:35-36 append-only, sin UPDATE/DELETE), vehicle_event (0003:32 'NEVER updated or deleted') y decision_event referencian el cdp_code; re-mintear por gramatica equivocada huerfana toda la historia. NO existe gate que congele el ancho/alfabeto/centinela antes del primer mint.
- **Fix exacto** — Insertar un gate de congelacion en el predicado REGISTERED->BOOTSTRAPPED de cover(CC) que ANTES del primer mint: (1) resuelve la spec de subdivision del pais desde ISO 3166-2 (pycountry): count+width de subdivisiones de primer nivel como DATO (DE 5-dig, FR ultramar '971'-'976' 3-dig, Corsica '2A/2B', IT sigla/ISTAT); (2) valida el country.toml contra un contrato tipado (frictionless Table Schema) que declara subdivision_width/alphabet/national_sentinel + regex, fail-fast si un codigo excede el ancho; (3) CONGELA la gramatica (atestacion in-toto tamper-evident) y solo entonces permite BOOTSTRAPPED. G1 deja de hardcodear [0-9]{2} y recibe el regex inyectado del manifest congelado. ES byte-identico (width=2, alphabet=[0-9], sentinel='00', validador 01-52 declarados en su .toml).
- **Riesgo adversarial** — FR/IT no caben en [0-9]{2}: Corsica '2A/2B' (alfanumerico), departamentos 53-95 (fuera del rango 52), ultramar 971-976 (3 digitos), provincias IT por sigla/ISTAT>99. Si Corsica se fuerza a un placeholder '00' o un departamento de 3 digitos se trunca a 2 y luego se descubre, re-mintear HUERFANA gestion_item/gestion_transition/vehicle_event/decision_event (todos append-only sin UPDATE/DELETE) y el FK entity_completion.cdp_code: dano IRRECUPERABLE. Un country.toml mal validado (faceta 29) que pase sin el gate propaga el error a G1, al sellador y a los mints, y por inmutabilidad parte del dano no se revierte. El diseno afirma 'onboarding reversible' -es falso en este eje.
- **Sellado multi-vía** — Sellado = existe un gate en REGISTERED->BOOTSTRAPPED que valida la spec de subdivision contra ISO 3166-2, la congela tamper-evident y bloquea el primer mint si no cuadra; G1 valida con el regex inyectado del manifest congelado, no con [0-9]{2} hardcodeado; ES byte-identico. Multi-via: (1) golden ES: manifest derivado de ISO 3166-2 reproduce caps/ancho/validador actuales y los 431k+ cdp_code ES re-minteados dan diff cero; (2) autoridad: conteos de subdivision DE/FR/IT/MX/JP (16/101/107/32/47) casan con ISO 3166-2 cross-checked contra 2a fuente; (3) fail-fast: un .toml con codigo que excede subdivision_width o alfabeto no permitido FALLA antes de cargar una fila; (4) tamper-evident: alterar un byte del ancho/alfabeto post-freeze hace fallar la verificacion de la atestacion -la irreversibilidad queda certificada, no prometida.
- **Herramienta NEXT-LEVEL** — pycountry (LGPL-2.1, €0) https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:527-532] — autoridad ISO 3166-2: count+width de subdivisiones de primer nivel por pais como DATO que congela la spec (build/config-time, LGPL no-issue; estricto-permisivo: iso3166 MIT + iso-codes raw JSON). Complementos: frictionless (MIT, €0) https://github.com/frictionlessdata/frictionless-py [:334-340] Table Schema que valida el country.toml (ANCHO en bytes per-pais) ANTES del INSERT/mint, fail-fast; in-toto (Apache-2.0, €0) https://github.com/in-toto/in-toto [:640-646] atestacion firmada tamper-evident de la gramatica congelada (irreversibilidad certificada, no prometida); lark (MIT, €0) https://github.com/lark-parser/lark [:277-283] EBNF del cdp_code como dato del pack.

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### (a) Verificacion de code_hints [VERIFIED]
- **[VERIFIED services/api/codes.py:1]** docstring *"Immutable Cardeep entity code (cdp_code) generator"*; **[:8]** formato `CDP-{country2}-{province2}-{8 x Crockford-base32 of sha256(key)}`.
- **[VERIFIED services/api/codes.py:44-53]** `mint_code(*, province_code, digest, country_code=DEFAULT_COUNTRY)` => `return f"CDP-{country_code}-{province_code}-{_base32(digest)}"`. Es el **unico hogar del prefijo**; pero **acepta cualquier string** como `province_code` — el invariante de ancho/alfabeto `[0-9]{2}` no esta impuesto AQUI, sino en los validadores que lo consumen.
- **[VERIFIED pipeline/complete.py:89]** `_CDP_CODE_RE = re.compile(r"^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$")` — el validador G1 asume **2 digitos** de subdivision (y prefijo ES literal); **[:73]** `_PROVINCE_RE = ^(0[1-9]|[1-4][0-9]|5[0-2])$` (01-52).
- **[VERIFIED pipeline/paths.py:30]** `_CDP_COUNTRY_RE = re.compile(r"^CDP-([A-Z]{2})-")` — parsea SOLO el `CC`, **no** el `NN`; el ancho/alfabeto de la subdivision no esta capturado en ningun parser generico.
- **[VERIFIED migrations/0031_gestion.sql:35-36]** *"gestion_transition is append-only; no rows are ever updated or deleted (the history IS the proof)"*; la tabla (121-131) no tiene ruta de UPDATE/DELETE en el codigo (route.py `_append_transition`). El rollback (170-174) solo DROPa la tabla entera.
- **[VERIFIED migrations/0003_vehicles_events.sql:32]** *"Append-only delta history. NEVER updated or deleted — the full timeline"* (`vehicle_event`).

#### (b) El mecanismo al atomo
El `cdp_code` es **inmutable por contrato**: es la identidad deterministica de la entidad, derivada de `sha256(canonical_key)` y prefijada por `CDP-{CC}-{NN}-`. Una vez acunado, todo el ledger append-only lo referencia: `gestion_item.subject_key` (cdp_code), `gestion_transition`, `vehicle_event`, `entity_completion.cdp_code` (FK). El slot `{NN}` (subdivision) tiene un **ancho y alfabeto** que hoy se asume `[0-9]{2}` (validado en `complete.py:89`, NO en `mint_code`). El resto del onboarding es additive+reversible (migraciones con bloque rollback — 0052:83-91, 0053:176-218; cuarentena reversible — faceta 2). PERO la gramatica del codigo **NO** lo es: si un pais se onboarda con `{NN}` equivocado y luego se descubre el error, corregirlo exige **re-mintear**, lo que **huerfana toda la historia append-only y el ledger** (gestion + vehicle_event + decision_event).

#### (c) La costura ES->generico con su fix exacto
**Costura:** el diseno afirma "onboarding reversible" — **es FALSO en el eje de la gramatica del codigo**. No hay gate que valide y CONGELE el ancho/alfabeto/centinela de subdivision antes del primer mint.

**Fix exacto:** insertar un **gate de congelacion** en el predicado `REGISTERED->BOOTSTRAPPED` de `cover(CC)` (faceta 27) que, ANTES de acunar el primer codigo del pais:
1. **Resuelve la spec de subdivision del pais desde una autoridad externa** (ISO 3166-2): cuenta y ancho de codigo de las subdivisiones de primer nivel se vuelven DATO, no sentinel ES. P.ej. DE Kreis 5-dig, FR ultramar '971'-'976' (3-dig), Corsica '2A/2B' (alfanumerico), IT por sigla/ISTAT.
2. **Valida el manifest del pais** (`country.toml`, faceta 29) contra un contrato tipado que declara `subdivision_width`, `subdivision_alphabet`, `national_sentinel` y el regex de forma — fallando fail-fast si un codigo excede el ancho declarado (en vez de reventar con 'value too long for character(N)' a mitad del seed).
3. **CONGELA** esa gramatica (la sella, tamper-evident) y solo entonces permite `BOOTSTRAPPED`. El validador G1 (`_CDP_CODE_RE`) deja de ser `[0-9]{2}` hardcodeado y pasa a recibir el regex inyectado desde el manifest congelado.
ES queda byte-identico: su `subdivision_width=2`, `alphabet=[0-9]`, `sentinel='00'`, validador `01-52` declarados en su `.toml` reproducen el hardcode actual (golden de cdp_code sin drift).

#### (d) El riesgo adversarial concreto (DE/FR/IT/PT/no-UE/ruido)
- **FR/IT no caben en `[0-9]{2}`:** Corsica `2A/2B` (alfanumerico), departamentos `53-95` (fuera del rango 52 de `_PROVINCE_RE`), ultramar `971-976` (3 digitos), provincias IT por sigla o ISTAT >99. NINGUNO es minteable sin redisenar el ancho/alfabeto (faceta 17).
- **Dano permanente por gramatica equivocada:** si Corsica se fuerza a un placeholder `'00'` o un departamento de 3 digitos se trunca a 2 y luego se descubre, **re-mintear huerfana** `gestion_item`/`gestion_transition`/`vehicle_event`/`decision_event` (todos append-only, sin UPDATE/DELETE) y el FK `entity_completion.cdp_code`. La historia se vuelve inconsistente de forma **irrecuperable**.
- **`.toml` mal validado se vuelve dano irreversible:** un manifest con `subdivision_width` incorrecto (faceta 29) que pase sin el gate de congelacion propaga el error a G1, al sellador y a los mints — y por inmutabilidad, parte del dano no se revierte.
- **Ruido de centinela nacional:** mezclar el `'00'` nacional (kinds plataforma/oem/subasta/importador) con una subdivision real de un pais cuyo esquema use '00' legitimamente colisiona la identidad nacional.

#### (e) Criterio de sellado + verificacion multi-via
**Sellado:** existe un gate en `REGISTERED->BOOTSTRAPPED` que valida la spec de subdivision contra ISO 3166-2, la congela (tamper-evident) y bloquea el primer mint si no cuadra; G1 valida con el regex inyectado del manifest congelado, no con `[0-9]{2}` hardcodeado; ES byte-identico.
**Multi-via:**
1. **Golden de no-regresion ES:** el manifest ES derivado de ISO 3166-2 reproduce los caps/ancho/validador actuales (01-52, width 2, sentinel '00') y los 431k+ `cdp_code` ES re-minteados dan diff cero.
2. **Via de autoridad (sanity por-pais):** los conteos/anchos de subdivision de DE/FR/IT/MX/JP derivados de ISO 3166-2 casan con valores conocidos (DE 16, FR 101 metropolitano+ultramar, IT 107, MX 32, JP 47), cross-check contra una 2a fuente (iso3166/Wikipedia).
3. **Via fail-fast (pack-malo):** un `country.toml` con un codigo que excede el `subdivision_width` declarado, o un alfabeto no permitido, FALLA la validacion antes de cargar una sola fila (test rojo si pasara).
4. **Via tamper-evident (congelacion):** la atestacion del freeze (gramatica + hashes del manifest) verifica intacta; alterar un byte del ancho/alfabeto post-freeze hace que la verificacion FALLE — la irreversibilidad queda certificada, no prometida.

#### (f) Herramienta NEXT-LEVEL que la eleva a nivel inalcanzable
**pycountry** (LGPL-2.1, €0) — https://github.com/pycountry/pycountry — autoridad ISO 3166-2: cuenta y ancho de codigo de las subdivisiones de primer nivel de CADA pais se vuelven DATO que alimenta la spec de subdivision congelada (el ancho CHAR(2) y los caps ES dejan de ser sentinels). Uso solo en build/config-time (autoria del manifest, no hot-path), asi que la LGPL es no-issue; estricto-permisivo: `iso3166` (MIT) + el JSON raw de iso-codes [VERIFIED NEXT-LEVEL.md:527-532]. Complementos: **frictionless** (MIT, €0) — https://github.com/frictionlessdata/frictionless-py — Table Schema que valida el `country.toml` (incl. el **ANCHO en bytes per-pais**) ANTES del INSERT/mint, fail-fast con mensaje claro en vez de 'value too long for character(N)' a mitad del seed [VERIFIED NEXT-LEVEL.md:334-340]; **in-toto** (Apache-2.0, €0) — https://github.com/in-toto/in-toto — atestacion firmada y tamper-evident de la gramatica congelada, de modo que la irreversibilidad sea un certificado verificable, no una promesa [VERIFIED NEXT-LEVEL.md:640-646]; y, para la gramatica formal del codigo, **lark** (MIT, €0) — https://github.com/lark-parser/lark — EBNF del `cdp_code` como dato del pack [VERIFIED NEXT-LEVEL.md:277-283].

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-33"></a>
### Faceta 33 · Golden + Ferrari de detector POR PAIS (prueba CI anti silent-green)
*La 2ª-vía real anti silent-green: Ferrari de detector por-CC, no un grep de string hueco.*  ·  **v1:** Clúster K

**Ficha rápida (costura → fix → adversarial → sellado → NEXT-LEVEL)**

- **Costura ES→genérico** — El golden ES prueba byte-identidad de ES pero NO prueba que los detectores sean country-CORRECT (solo country-blind). No hay fixture por-CC ni golden de UMBRALES por pais [VERIFIED detect.py:69-107 son constantes de modulo, no parametrizadas; :78-83 anclas ES]. run_all corre el mismo codigo para todos sin evidencia ejecutable de que los parametros del pais nuevo no provoquen mass-fire.
- **Fix exacto** — Un fixture FERRARI por-CC (countries/<CC>/ferrari/) + un golden de umbrales por pais que en CI ejercite los 7 detectores live contra datos sinteticos del pais nuevo y asserte flag-rate ACOTADO (los detectores NO disparan masivamente con los parametros del pack del pais). Hypothesis genera filas de vehicle del pais (moneda/niveles locales) y caza el caso que rompe; reemplaza el 'grep CDP-ES=0' por evidencia ejecutable. ES queda byte-identico (golden actual intacto).
- **Riesgo adversarial** — Es el modo de fallo silencioso MAS peligroso: el golden ES no cambia -> CI verde -> el pais nuevo entra a prod -> detect_fabrication marca todo coche>techo-EUR-implicito + price_trap se rompe por cohorte multimoneda, ambos quarantines=TRUE -> servable_* oculta el pais entero (faceta 2). DE de lujo (>150k EUR legitimo) dispara price_trap HIGH; MXN/JPY rompen el fabrication ceil; COVERAGE_ANCHORS ES dan coverage_gap basura para DE (compara contra 1292 desguaces ES). RUIDO: un portal que pagina con los techos redondos {500,1000,2000,5000} legitimamente dispara silent_cap falso. Sin Ferrari por-CC nada de esto se ve hasta produccion.
- **Sellado multi-vía** — Multi-via: (1) FIXTURE por-CC en CI — flag-rate de cada detector sobre datos del pais acotado bajo umbral (prueba country-CORRECT, no solo blind). (2) HYPOTHESIS adversarial — si fabrication/price_trap/coverage_gap disparan masivamente con params del pais => CI ROJO. (3) GOLDEN ES byte-identico (cero regresion, test_country_golden). (4) 2a VIA — el flag-rate del Ferrari DE cruza contra el pack DE (faceta 5): un umbral mal puesto en el .toml se delata como mass-fire en el fixture. (5) acopla faceta 2 — un fixture que dispare quarantines=TRUE masivo es kill-switch detectado en CI, no en prod.
- **Herramienta NEXT-LEVEL** — Hypothesis (MPL-2.0, EUR0) https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:320,:38] — fuzzing property-based que caza el caso por-pais que rompe los 7 detectores en CI; integra en el job db-tests/unit; pandera puede auto-derivar estrategias desde el schema Vehicle. Alt: Pandera/Great Expectations (contrato fail-closed por country-pack, :167), Evidently (drift, :619).

**Proyecto institucional 360 — deep-spec `(a→f)`**

#### Mecanismo al atomo
Hoy CI corre el golden ES y queda VERDE; ningun fixture ejercita los 7 detectores LIVE contra datos de un pais nuevo, asi que el pais nuevo detona SOLO en produccion (mass-quarantine). El registry es `DETECTORS` (7 live + 2 STUB) [VERIFIED detect.py:926-936] y `STUB_DETECTORS={geo_resolution_drift, classifier_drift}` [VERIFIED :940]. Los detectores leen umbrales-constante (faceta 5) [VERIFIED :69-107] que el golden ES NO ejercita contra datos no-ES.

**El 'grep' es hueco:** `COVERAGE_ANCHORS` son instituciones ESPANOLAS hardcodeadas — `1_292 'DGT official CAT'`, `2_018 'FACONAUTO'`, `1_662`/`29_955 'Paginas Amarillas'` [VERIFIED :78-83] — magic numbers ES SIN el substring 'CDP-ES'. El metodo de verificacion del diseno ('grep CDP-ES=0') NO los detecta: la ausencia del literal no prueba agnosticismo. run_all aplica el MISMO codigo a todos (country-blind), y blind != correct.

**Patron espejo disponible:** tests/test_country_golden.py (golden ES byte-identity) + tests/test_country_coexistence.py (CDP-DE coexiste); CI en .github/ con jobs unit/collect/frontend/secret ya existentes.

[↑ Índice de sub-proyectos](#indice-subproyectos)

---

## Mejoras a nivel inalcanzable (EUR0, priorizadas)
Todas €0; el GPU/LLM masivo es la palanca €>0 con firma del owner (`00-MASTER` §Gates). Priorizadas por ratio impacto/esfuerzo:

1. **`[S]` Dedup/cache de decisiones por hash de pregunta canónica.** Ambigüedades idénticas entre países (misma forma de denominador, mismo patrón geo) se responden UNA vez y se reusan; reduce la ráfaga de Claude a lo genuinamente nuevo. Hoy cada `ESCALATE_OWNER` muere en el humano sin memoria reutilizable `[VERIFIED router.py:84,93]`.
2. **`[S]` Sellado contrafactual.** Replay del predicado de sellado sobre snapshots históricos → tendencia "habría sellado" por estrato/CC; convierte el sellado de evento binario en serie temporal que anticipa regresiones. Hoy `complete.py` solo evalúa estado actual `[VERIFIED complete.py:473-497]`.
3. **`[M]` Tier de IA local como decider del bus, confidence-gated.** `local_ai_drain` reclama `CLASSIFICATION_DOUBT`/`RECIPE_FIELD_EXTRACT`, decide bajo umbral o escala. El contrato del bus es el único desbloqueo; el día que se deja caer un GGUF, capa-2 enchufa sin tocar el motor. Hoy solo slots dormantes `[VERIFIED recipe_schema.py:67, detect.py:905]`.
4. **`[M]` Cadencia self-tuning por-CC.** Los intervalos de los 8 jobs pasan de constantes globales `[VERIFIED scheduler.py:8×add_job]` a por-país, aprendidos de la volatilidad de `source_health`. Puro DB.
5. **`[M]` Bus adversarial co-igual.** Un 2º lens determinista "fiscal" auto-desafía cada decisión de Claude ANTES de `APPLIED`; si discrepa, levanta una contra-decisión. Verificación ortogonal de las **decisiones**, no solo de los datos (extiende la inquisición de datos a decisiones de orquestación).
6. **`[L]` Bus-como-eval-harness retroactivo.** Cada decisión de Claude VERIFICADA por VAM se promueve a golden del clasificador; el tráfico de decisiones construye gratis el golden-set de capa-2 y cierra el STUB `classifier_drift` con datos reales `[VERIFIED detect.py:905-916]`.

---

## Riesgos / open items
- **`[OPEN ITEM gateado]` Ancho del slot `cdp_code` (Clúster B).** Decisión arquitectónica **irreversible** (toca el código inmutable + golden ES): ancho-variable-por-país vs migración a slot universal. Gating: **firma del owner**. Bloquea sellado de FR/IT (no de DE). Sin un gate `GRAMMAR_FREEZE` pre-minteo, un país mal-minteado huérfana el ledger append-only `[VERIFIED 0031, 0036 append-only]`.
- **`[OPEN ITEM]` Piso de independencia por país (Clúster H).** Mercados de cola fina pueden no suministrar `quorum_n>=2` ortogonal `[VERIFIED route.py:243]`; el residual se acota honestamente y queda `PENDING-OWNER`. No se debilita VAM.
- **`[OPEN ITEM owner stage 02]` Render infra para G3 (Clúster I).** Portales JS-render-only sin capacidad de scraping → G3 INCOMPLETE. Dependencia de sellado delegada.
- **`[BLOQUEA cover(CC)]` Mint bypass (Clúster J).** Los connectors `pipeline/platform/` (31 hardcodean `CDP-ES-`, 0 usan `mint_code()` `[VERIFIED]`) deben enrutarse a `mint_code(country_code=)` antes de cualquier `cover(no-ES)`. Owner: identity.
- **`gestion_item` VACÍA hoy (L3 nunca ejercitada)** `[VERIFIED 0036:13]`: la state-machine está probada por tests, no por carga viva. El bus hereda esto: sin ejercitar a escala.
- **Stack CAÍDO** (Docker/PG:5433/API:8090/schedulers off): los 8 jobs están registrados pero INERTES hasta restart-OWNER `[VERIFIED scheduler.py:8×add_job]`; toda cadencia (y el drenado del bus) es código dormante hoy. Restart = acción supervisada (reversible).
- **Auto-DoS del bus a €0.** El scheduler ya advierte que "at €0 mass emission floods un-self-resolvable escalations" `[VERIFIED scheduler.py:102-103]`; el bus DEBE heredar emisión acotada/opt-in (`INQUISITION_EMIT_BATCH=200` `[VERIFIED scheduler.py:106]`) o se auto-DOSea a Claude.
- **Bus Claude-heavy sin capa-2.** Sin IA local presente, TODA duda de clasificación/extracción escala a Claude → coste/tiempo de ráfaga alto. Aceptable a €0, pero hay que dimensionar el lote.
- **G5 deferred** (`g5_check.py` inexistente `[VERIFIED complete.py:54-57]`): el SELLADO no incluye prueba real de delta hasta una 2ª cosecha; hoy el sello es G1-G4 + frescura, **declarado honestamente como tal, no maquillado**.
- **Predicados de transición de `cover(CC)` nuevos y no probados en vivo.** Un predicado mal calibrado podría sellar prematuro; mitigado por la 2ª-vía prosecutor + el checkpoint `COVERAGE_SEAL_REVIEW` a Claude antes de latchear.

---
> **Cierre honesto (BLINDAJE).** Esta etapa tiene el cerebro **determinista** real y probado, pero las capas pensantes (IA local, Claude orquestador, bus, `cover(CC)`) son **diseño, no código** hoy `[VERIFIED]`. De los 27 ítems adversariales: **22 cierran** con fix de motor/pack a €0; **5 quedan como OPEN ITEM con causa y gating declarados** (ancho de código irreversible, piso de independencia, render infra, mint bypass cross-stage, y la dependencia del intervalo en stage 07). Ninguna rotura se oculta. El motor NO es genérico aún por debajo del esquema; este capítulo es el plano de cómo lo será.
