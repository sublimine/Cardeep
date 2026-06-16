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

## Acción
- **FIJAR (verificados, alto valor):** CRIT #1 wallapop (except-wrap) + CRIT #2 coches_com (declared_total forward).
- **TEMA 1 sistémico** → aplicar el except-wrap a coches_net/autoscout24/subastas/autocasion (mecánico, per-SOURCE_KEY).
- **TEMA 3 scoping** → análisis del módulo `coverage_verify.py` compartido (captured_db per-run) — contexto fresco.
- **TEMA 4** → Flexicar fetcher (claro) + los MED de anti-detección (last_http, supplement-stop) → contexto fresco.
- Verdict por hallazgo: la mayoría REAL (evidencia viva); ninguno descartado aún como falso — verificar al fijar.
