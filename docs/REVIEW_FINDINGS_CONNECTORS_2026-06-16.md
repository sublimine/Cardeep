# Green-review de la capa de conectores — triage verificado (2026-06-16)

3er barrido adversarial (workflow `wfw5ejlm3`, 7 revisores especialistas) sobre 7 conectores
representativos (~9k líneas): coches_net / wallapop / milanuncios / coches_com / autoscout24 /
subastas / vo_chains. **24 hallazgos: 2 CRIT, 10 HIGH, 10 MED, 2 LOW**, varios con evidencia de DB
viva. Cada uno se verifica a mano antes de tocar.

## Temas dominantes

### TEMA 1 — `try/finally` sin `except` → record_run se salta ante excepción de setup → monitoring-dark
**SISTÉMICO.** Mismo class que la P2 de `harvest_dealer` (ya fijada). El `harvest()` de cada conector
envuelve el cuerpo en `try: … record_run(…) finally: conn.close()`. Una excepción antes del record_run
(GeoResolver.load, ensure_platform_entity, queries de setup) salta a `finally` → cero harvest_run, salud
no actualizada, breaker no salta, sin alerta. Fix uniforme: `except Exception as exc: await record_run(
conn, SOURCE_KEY, ok=False, error=str(exc)); await auto_repair(…); raise` antes del `finally`.
- **wallapop_wholesale.py:1267 (CRIT)** — VERIFICADO (try 1267 / record_run 1414 / finally 1427, sin except).
- coches_net_wholesale.py:929 (HIGH) · autoscout24_wholesale.py:336 (HIGH) · group_subastas_wholesale.py:929 (LOW)
  · autocasion_wholesale.py (mencionado) — mismo patrón.

### TEMA 2 — breaker-open early-return sin record_run → skip no observable
autoscout24 (HIGH), vo_chains (HIGH), milanuncios (MED). Matiz: un skip por breaker-open es degradación
intencional, no fallo. Decisión de diseño: ¿escribir una fila harvest_run 'skipped'? Útil para el dashboard
pero no es bug de corrección. Prioridad media → tracked.

### TEMA 3 — declared_total / coverage scoping (gate de cobertura + GONE)
- **coches_com VN/renting (CRIT)** — VERIFICADO: `_finalize_platform_segment` record_run sin declared_total →
  gate nunca dispara para esos segmentos.
- wallapop declared=651k vs ceiling real ~224k (HIGH) → coverage 34% < 0.9 → GONE nunca dispara.
- coches_com renting declared=8908 headline vs ~1034 paginable (HIGH) → denominador inflado.
- coches_com VO/km0 db_edges acumulativo vs harvested per-run (HIGH) → REFUTED espurio en multi-run.
- milanuncios declared per-run vs captured acumulativo (HIGH, live 150,78%) → apunta a `coverage_verify.captured_db`
  acumulativo (issue COMPARTIDO, no per-conector).
- vo_chains Carplus declared_full siempre None (HIGH) → gate cobertura+GONE desactivado.
- coches_net proof-slice 272k declared (MED) → alerta low_coverage espuria + auto_repair cada run.
  **Núcleo compartido:** `coverage_verify.captured_db` cuenta TODO el histórico vs declared per-run/slice →
  el scope no casa. Fix correcto = scopear captured a la ventana del run (`last_seen>=run_started_at`) o pasar
  `declared_total=None`/`db_edges` en slices. Requiere análisis del módulo compartido — tracked.

### TEMA 4 — connector-specifics
- **vo_chains Flexicar usa fetcher/headers de OcasionPlus (HIGH)** — Referer `ocasionplus.com` a `flexicar.es`;
  hoy pasa (CDN laxo) pero un check de referrer rompería la atribución por sucursal (23.874 coches). Bug real.
- autoscout24 last_http stale 200 en fallo de red (MED) → misclasifica el repair.
- wallapop flat-pass error no para el supplement sweep (MED) → 320 requests más contra host baneado.
- subastas should_emit_gone(declared=0) da respuesta errónea (MED, rescatado por check downstream).
- vo_chains ventana concurrente descarta páginas en error (MED) · OcasionPlus listing_ref frágil (MED).
- wallapop captured_distinct cuenta re-touched (LOW).

## Acción — PROGRESO

**FIJADOS + VERIFICADOS + PUSHEADOS (todos los de alto valor):**
- `dd93759` **CRIT #1** wallapop except-wrap (+ test mock) · **CRIT #2** coches_com VN/renting declared_total forward
  (+ renting denominador headline→paginable).
- `64a3627`/`071ec4e` **TEMA 1 COMPLETO** — except-wrap en los 5 conectores (wallapop CRIT, coches_net, autoscout24,
  subastas, autocasion). Ningún harvest monitoring-dark ante excepción de setup.
- `30db4c2` **TEMA 4 Flexicar (HIGH)** — `fetch_flexicar_srp` con FLEXI_HEADERS (Referer correcto; OcasionPlus intacto).
- `8e4b175` wallapop supplement-sweep para en error de flat-pass (no profundiza el ban) · `5101571` autoscout24
  resetea `last_status` (no 200 stale → repair bien clasificado).

**PENDIENTE (contexto fresco — nuance/riesgo/juicio):**
- **TEMA 3** declared_total scoping per-conector. **VERIFICADO 06-16 que el mecanismo del agente para coches_net
  estaba PARCIALMENTE MAL:** predijo "coverage 1.8% → alerta low_coverage cada run"; la realidad viva es
  `declared=271981 / captured=274144 = 100.8% → REFUTED` (sin alerta low_coverage). Causa real: `coverage_verify.
  captured_db` es **acumulativo** (cuenta TODO lo del facet full-drain, mismo source_key) vs el declared del
  proof-slice wholesale (DEFAULT_MAX_PAGES=5, ~500 caged). El proof-slice **no debería alimentar el gate** (el facet
  es el full-drain que sí). Fix candidato: wholesale pasa `declared_total=None`; **PERO** exige decidir qué conector
  alimenta coverage para un source_key compartido + el scoping de captured_db — análisis cuidadoso, NO fix apresurado.
  Igual milanuncios partial-run + coches_com VO/km0 db_edges acumulativo: **verificar cada mecanismo a mano** (los del
  agente pueden estar mal) antes de tocar; riesgo real de romper coverage-gating. → contexto fresco.
- **TEMA 2** breaker-skip sin record_run (autoscout24/vo_chains/milanuncios) → **juicio de diseño** (el skip es
  degradación intencional, no fallo; el propio agente dudó "arguably ok=True"). No es bug de corrección claro → diferido.
- **MEDs defensivos FIJADOS:** `f1f1de2` vo_chains ventana concurrente (conserva páginas hermanas en error transitorio,
  live OcasionPlus 500) · `dc10e13` delta_guard should_emit_gone(declared=0) self-consistente (+3 tests) · `c5ca3aa`
  milanuncios bands_capped → warning observable.
- **PENDIENTE genuino (contexto fresco/juicio):** TEMA 3 coverage-scoping (verificado nuancado, mecanismos del agente
  a re-verificar — riesgo coverage-gating) · vo_chains listing_ref frágil (URL live-verificada → design-risk, no bug
  activo) · TEMA 2 (juicio diseño).
- **Verdict de la capa:** de los hallazgos accionables/claros, TODOS fijados (2 CRIT + THEME 1×5 + Flexicar + 5 MED).
  El agente acertó en casi todos CON evidencia viva — salvo el mecanismo de coches_net TEMA 3 (parcialmente mal,
  cazado al verificar). La verificación a mano fue, otra vez, lo que separó señal de ruido.

## RESOLUCIÓN TEMA 3 (06-16) — el bug real era el OPUESTO de lo que el agente describió

Al investigar TEMA 3 a nivel átomo (leyendo `coverage_verify.py` + `verify.py::record_count_verdict` + el
estado vivo de `source_coverage`), el daño real NO era "low_coverage espuria cada run" (lo que predijo el agente)
sino su **opuesto**: **tres sources con cobertura SANA (autocasion 97,2% · coches_com 99,6% · coches_net 100,8%)
estaban marcadas `REFUTED`**, y `reconcile_gone` (delta.py:162) **SKIPea las bajas cuando el verdict es REFUTED**
→ las bajas de ~478k coches nunca se procesaban (rompe "delta completo").

**Causa raíz (dos fallos compuestos):**
1. `record_count_verdict`: `drift_ok = top_n >= 2 and divergence <= tolerance`. El `top_n>=2` exige ≥2 valores
   EXACTAMENTE iguales → para 2 paths continuos (`captured_db` vs `declared_total`, nunca idénticos) la tolerancia
   quedaba anulada → caía a REFUTED. **Pero** el invariante DB `chk_trustworthy_needs_quorum` SÍ exige quorum_n≥2
   (cluster exacto), así que la corrección no es "→TRUSTWORTHY" sino: drift dentro de tolerancia pero sin cluster
   exacto → **UNVERIFIED** (honesto: "no certificable por quórum", y NO REFUTED). Fix en `verify.py`.
2. `verify_coverage` metía `captured_distinct` (contador PER-RUN, proof-slice ~110) junto a `captured_db`
   (acumulativo ~274k) en los paths del verdict → spread espurio del 99,96% → REFUTED. **Excluido** del verdict
   (solo `captured_db` vs `declared_total`, ambos acumulativos). +tolerancia derivada del floor por-source
   (`1-floor`) para que verdict y alerta de under-coverage compartan umbral.

**Efecto verificado:** los 3 sanos pasan REFUTED→UNVERIFIED (re-corrido el gate en vivo, idempotente) →
`reconcile_gone` (que solo bloquea REFUTED) **desbloquea sus bajas**. milanuncios 150,8% sigue UNVERIFIED
(override>ceiling). as24 22,5% sigue REFUTED en run real (proof-slice = genuinamente incompleto, correcto).
84 tests afectados verde; suite completa verde. El claim del agente sobre wallapop ("651k vs 224k→34%") era
FALSO: captured 588011 = 90,3%. **Lección: la verificación a-nivel-átomo contra DB viva cazó que el agente
había caracterizado el bug AL REVÉS — diferir habría dejado vivo un fallo de producto (bajas).**

## RESOLUCIÓN TEMA 2 + listing_ref (06-16) — investigados a átomo, NO son bugs de corrección

**TEMA 2 (breaker-skip sin `record_run`) — NO es bug, declarado con prueba.** `is_open` (health.py:443)
recupera el breaker por TIEMPO, no por `record_run`: state='open' + cooldown vigente → True (skip); cooldown
vencido (`now() >= cooldown_until`, fijado al abrir en :233) → mueve a `half_open` + return False (deja pasar
exactamente una sonda); la sonda cierra (ok) o reabre (fail) vía `record_run`. **El skip-sin-record NO impide
la recuperación** (es time-driven) **ni la observabilidad** (el estado vive en `source_breaker` + la alerta de
apertura). Una fila `harvest_run 'skipped'` sería granularidad de dashboard, no corrección. Sin cambio.

**vo_chains OcasionPlus `listing_ref` frágil — cosmético, NO bug, pero CERRADO igual.** La identidad de vehículo
en ingest (`ingest.py:71,79`) se keya en **`deep_link`** (URL completa), NO en `listing_ref` → un ref frágil no
causaba churn ni colisión de delta. Aun así, el ref nativo ALMACENADO (que la identidad cross-source/B7 futura
podría usar) era frágil a `?query`/`#fragment`/trailing-`/`. **Cerrado**: helper `_ocasionplus_listing_ref`
(limpia query/fragment/slash ANTES del tail; backward-compatible para URLs limpias) + 8 tests
(`test_vo_chains_listing_ref.py`) que fijan la estabilidad (variantes de un coche → 1 ref). Solo OcasionPlus
usaba el `rsplit` crudo; Flexicar/Clicars/Carplus ya usan ids nativos.

**Capa de conectores CERRADA:** todos los hallazgos del 3er barrido están resueltos (fijados) o investigados-a-
átomo-y-declarados-no-bug-con-prueba (TEMA 2, listing_ref). Cero pendientes de "juicio/contexto fresco".
