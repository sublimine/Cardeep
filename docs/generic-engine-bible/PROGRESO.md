# PROGRESO — Campaña Motor Genérico (autónomo · hands-off · resume anchor)
> Doctrina: trabajo autónomo persiste estado a disco. Este archivo + los .md de la biblia = punto de reanudación. Un yo futuro (o sesión nueva) lee ESTO primero y continúa sin perder el hilo. Última actualización: 2026-06-27.

## Estado por ola
- ✅ **Recon de contexto** (12 agentes) — `tasks/wj00d90av.output` + `scratchpad/cardeep-CONTEXTO-INTEGRAL-2026-06-27.md`.
- ✅ **Auditoría `INGENIERIA_CARDEEP.md`** (11 agentes) — `scratchpad/AUDITORIA-INGENIERIA-CARDEEP-2026-06-27.md`.
- ✅ **Ola 1** (10 diseños + 10 adversariales) — `scratchpad/wave1-stages/*.json`. Veredicto: **TODOS NEEDS_REWORK** (motor country-blind; honesto).
- ✅ **Ola 1.5** (10 modelos LLM) — `tasks/wgk2sj5mr.output` → `LLM-ROUTING-MATRIX.md`.
- ✅ **Ola 2** (13 capítulos v1) — `stages/01..10.md` + matriz + pack + spine. *(2 "fallos" eran de retorno estructurado; archivos SÍ escritos — verificado en disco.)*
- ✅ **Spine re-run** + **COUNTRY-PROOF** spec.
- ✅ **REMEDIATION-BLUEPRINT** (keystone, bible→build): plan PR-por-PR (PR-0..PR-7, irreversibles primero) con goldens cross-country + gates `dry-run:5434→golden→Ferrari→CI` + rollback. LEVERAGE: `paths.py`/`triangulation` ya paramétricos + goldens `test_country_golden`/`test_country_coexistence` YA en disco. Stack CAÍDO → goldens corren al reiniciar DB. PENDING-OWNER: gate de congelación de gramática `cdp_code` (FR DOM 971-976 / IT ISTAT >99).
- ✅ **Ola 2.5** (re-verificación adversarial, 4 lentes): **train-completeness = NEEDS_REWORK** — el blueprint estaba incompleto. Gaps reales hallados: **Signal A `photo_url` country-blind (HIGH, irreversible, sin guard ni golden; anti-FP es `print` post-write)**, edge-4 fuzzy, resolver β (`resolve_entities`), `canonical_dedup` deep_link (alimenta `v_dealer_resolved` servido), `cross_source_dedup`. Output: `tasks/w5lmwepi1.output`.
- ✅ **Hardening del blueprint + guard** (`a03707`): `COUNTRY-PROOF` con **guard dual** (`v_dealer_resolved` + `v_canonical_vehicle`) + censo completo de costuras (aristas 1-4, Signal A+B, anti-FP, β, `canonical_dedup` Layer-2, `cross_source`) + **golden Signal A** (foto compartida ES-28/DE-28). `REMEDIATION-BLUEPRINT` tren ampliado a **6 PRs** {1,2,4,7,8,9}, ambos guards verdes = condición de siembra. Honestidad: **F7 CHAR→VARCHAR NO es aditivo** (choca PK compuesta 0053); anti-FP es `print` post-write; β no servido (precondición); F8 normalización no-latina (eje distinto, gated país no-latino).

## Convergencia honesta de los keystones (NO sellados — sin maquillaje)
DISEÑADOS + endurecidos por **1 ciclo fix→re-verify**. NO sellados: el sello real exige **correr los goldens contra la DB viva** (gated por DB CAÍDA → restart owner) + posiblemente 1-2 ciclos más de re-verify de diseño. Estado honesto = "100% de lo reversible-en-diseño hecho; verificación funcional PENDING-DB".

## EJECUCIÓN CONTINUA (mandato Stop-hook: llevar TODO a nivel inalcanzable)
Sin pausa: **tandas encadenadas hasta cerrar el mandato**; la ventana se gestiona con el tamaño de la tanda, no parando.
- ✅ **Ola 3** (mejora a nivel inalcanzable): 6 clusters minaron **94 mejoras** con herramienta battle-tested €0 (`scratchpad/ola3/*.json`). El sintetizador-agente murió por **LÍMITE DE SESIÓN**; **recuperado SIN agente** → `NEXT-LEVEL.md` ensamblado de los JSON vía Python (token-cero de modelo). Verificar URLs/licencias a fuente antes de adoptar.

## EJECUCIÓN CONTINUA — límite reseteado, autopista abierta
Reanudado a fondo. Relleno 360 de los 283 sub-proyectos en **tandas de etapas** (deep-dive por faceta → capítulos **v2 profundos** navegables, no fragmentos sueltos).
- ✅ **Relleno tanda 1** (`wk82t17sj`): v2 PROFUNDOS verificados en disco — `04-identity` 806 ln/41 sub · `05-vehicle` 1559/210 · `07-quality-seal` 1671/189 (3-7× más profundos que v1; cada faceta = subsección 360).
- ✅ **Relleno tanda 2** (`wbv34x7i1`): v2 profundos verificados — `01-discover` 1470 ln/52 · `02-scrape` 1709/215 · `03-extract` 1628/220. **(6/10 etapas en v2 profundo)**
- ✅ **Relleno tanda 3** (`witic28ux`): `06-geo` 1788 ln/203 · `08-serve` 1749/35. **(8/10 en v2 profundo)**
- ✅ **Relleno tanda 4 — FINAL** (`wlpr93o1z` + recovery `whktsgek0`): `09-orchestrate` 1214 ln/182 · `10-automation` 1720/198. **5 chunks rate-limited (server-side) recuperados** (supervisión activa: leído el `failures`).
- ✅ **RELLENO COMPLETO — 10/10 etapas en v2 profundo (15.314 líneas, cada faceta = sub-proyecto 360).**
- ✅ **Push HECHO**: rama `feature/generic-engine-bible` en GitHub (sublimine/Cardeep), 23 ficheros (SOLO la biblia), WIP del owner intacto. PR: https://github.com/sublimine/Cardeep/pull/new/feature/generic-engine-bible
- Cierre restante: re-verify de keystones (loop fix→re-verify) + validar a fuente las 94 tools de `NEXT-LEVEL.md` + correr goldens cross-country (DB ya viva).
- Después: re-verify de keystones (loop fix→re-verify) · verificar a fuente las 94 tools de `NEXT-LEVEL.md` · correr goldens al reiniciar DB.
## 🟢 STACK VIVO (restaurado por mí 2026-06-27)
DB `cardeep-pg` :5433 (entity **450.647** · vehicle **2.378.534** · vehicle_event **2.959.229** · mig máx **0055**) · API uvicorn :8090 (`/health` live·db:ok, `/stats` dealers **19.144** honesto precompute) · scheduler vivo (lock 1128354372, 8 jobs: heartbeat 15min + **product_stats refresh** + silence + inquisition + gestionador + lease-heartbeat). Cifras [ASSUMED] de la biblia → ahora **[VERIFIED]** contra DB viva (kind: particular 359.151·compraventa 76.160·garaje 10.021·desguace 2.785·concesionario 2.300). Los goldens cross-country corren ya al implementarse. PENDIENTE de aplicar (gated): **0056** v_servable_dealer (mig máx en DB = 0055).

**Gates / decisiones (actualizado por el owner 2026-06-27):** ✅ **restart DB hecho** (lo hice yo: PG vivo, entity 450.647) · **GPU/VPS = local-primero** (owner: primero funciona aquí, luego VPS) · **legal = DESCARTADO** (owner: "me la suda; no tienen por qué saber lo interno") · **push GitHub = AUTORIZADO** ("impecable y limpio", al cerrar el relleno) · ÚNICO residual de diseño: **gramática `cdp_code` FR/IT** (anchos `2A/2B`, DOM `971-976`, ISTAT >99).
- ✅ **Descomposición** (`wktjzztxt` + recuperación de 01): **283 sub-proyectos en las 10 etapas** → `INSTITUTIONAL-BACKLOG.md` + `scratchpad/institutional-decomp/*.json`. `01-discover` devolvió stub `"probe"` → **recuperado: 40 facetas** (cadena auto-reparada).
- ✅ **PoS institucional** (`w174ibacw`): `POS-DETECTION-AND-TIERS.md` (264 líneas, verificado en fuente). **CAVEAT:** el redactor recibió 1/6 facetas (truncado `slice` mío); recuperó por verificación directa. OPEN: integrar breaks de facetas 2-6 (`tasks/w174ibacw.output`).
- ⏳ **Pendiente (batched hands-off):** profundización 360 de los 243 sub-proyectos en TANDAS prioritizadas por riesgo (spine country-blind + keystones primero) · integrar facetas 2-6 PoS · normalizar `[VERIFICADO]`→`[VERIFIED]` · **Ola 2.5** re-verificación adversarial · **Ola 3** mejora nivel-inalcanzable + minado de herramientas. **ESCALA:** 243 facetas = programa multi-ventana; el backlog enumerado YA es la estructuración institucional de cada micro-punto.

## Artefactos en disco (`docs/generic-engine-bible/`)
`README.md` · `00-MASTER.md` · `ANTI-DRIFT-HARDENING.md` · `COVER-NEW-COUNTRY.md` · `COUNTRY-PACK-CONTRACT.md` · `LLM-ROUTING-MATRIX.md` · `COUNTRY-PROOF-INVARIANT.md` · `SPINE-COUNTRY-THREADING.md` · `stages/01-discover…10-automation.md` · este `PROGRESO.md`.

## Hallazgo central (no perder)
**Espina rota:** `country_code` llega al ESQUEMA (`0052/0053`) y a `mint_code`, pero NO a la LÓGICA → pipeline/serving/orquestación **country-BLIND** (false-merge transfronterizo, sellado sin dimensión país, API mezcla países, locks globales, `complete.py:89 ^CDP-ES-`, anchos `CHAR(2)/CHAR(5)`, rangos `01-52`, bandas EUR, `Accept-Language es-ES`, 31 conectores `CDP-ES-`). Remediación unificada en `SPINE-COUNTRY-THREADING.md`; guard mecánico en `COUNTRY-PROOF-INVARIANT.md`.

## Protocolo hands-off / tokens (autónomo)
- **Tandas** ~2 etapas (~12-20 agentes) por ola; nunca el bloque entero → no revienta la ventana.
- **Siempre 1 ola en vuelo** → la cadena de eventos no muere (cada aterrizaje me re-invoca).
- **No se lee el % en vivo** (no es herramienta del modelo). Si el techo corta: todo en disco; al reset / próxima notificación se retoma. **Cero pérdida.**
- Workflows resumibles con `resumeFromRunId` (misma sesión); fuera de sesión, re-derivar desde este archivo.

## Reanudación (un yo futuro lee esto y ejecuta)
1. Lee este `PROGRESO.md` + `00-MASTER.md`.
2. Mira "Pendiente" arriba.
3. Si hay descomposición sin ejecutar: split de `tasks/wktjzztxt.output` a `scratchpad/institutional-decomp/<stage>.json` y lanza la **siguiente tanda** institucional (~2 etapas) → faceta-360 (átomo+adversarial+country-proof+verificación) → capítulo institucional v2.
4. QC en disco multi-vía (`[VERIFIED]` count, red-flags, estructura) ANTES de declarar nada hecho.
5. **Nunca** declarar 100% con gates PENDING-OWNER (prod-write) abiertos: estado honesto = "100% de lo reversible, N ítems PENDING-OWNER".
