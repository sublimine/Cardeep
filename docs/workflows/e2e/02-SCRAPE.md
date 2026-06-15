# 02-SCRAPE — Scraping de inventario de un dealer

Ejecuta el ciclo de fetch-parse-record para extraer el inventario completo de un dealer
dado su `cdp_code` y su `recipe.yaml` resuelto.

---

## Disparador

- **Scheduler automático**: `pipeline/ops/scheduler.py` — `heartbeat_tick()` cada 15 min.
  Selecciona sources por `last_ok` atrasado, prioridad FIFO, evalúa circuit breaker antes
  de encolar.
- **Manual**: `python -m pipeline.harvest_dealer --cdp CDP-ES-XX-XXXXXXXX --source autoscout24`

---

## Entradas

| Entrada | Descripción |
|---|---|
| `cdp_code` | Identificador canónico del dealer |
| `recipe.yaml` resuelto | `v_dealer_recipe.recipe_kind <> 'none'` — gate G3 de `complete.py` |
| Conector de plataforma | `pipeline/platform/{platform}_wholesale.py` o `_facet.py` |
| `engine/fetch.py` | Motor HTTP con impersonation y retry |
| `engine/governor.py` | Token bucket de rate-limit por host |

---

## Pasos átomo

1. **Circuit breaker check**: `is_open(conn, source_key)` — abortar si estado OPEN.
2. **Resolver recipe**: leer `v_dealer_recipe` → obtener `recipe_kind` y `recipe_ref` (la vista devuelve `entity_ulid, cdp_code, source_key, recipe_kind, recipe_ref`; los campos `engine`, `enumeration`, `field_map` no son columnas de la vista sino contenido del `recipe.yaml` en disco o del conector de plataforma).
3. **Governor acquire**: `governor.acquire(host)` — token bucket 0.7 req/s, burst 3,
   spacing mínimo `DEFAULT_MIN_SPACING_S ≈ 1.43 s`, jitter `±0.25 s`.
4. **Fetch páginas**: `fetch.py` con `curl_cffi` impersonando Chrome 131 (`_DEFAULT_UA`).
   Retry ×4 (`_MAX_RETRIES=4`) con backoff exponencial `2^n s` (`_BACKOFF_BASE=2.0`).
   Polite sleep `0.7–1.4 s` (`_POLITE_MIN / _POLITE_MAX`) entre requests.
   HTTP retryables: `_RETRYABLE = {429, 500, 502, 503, 504}`. Timeout global: `_TIMEOUT=40 s`.
5. **Parsear payload**: aplicar `field_map` de `recipe.yaml` → lista de vehículos
   normalizados (dict con `deep_link`, `vin_ref`, `make`, `model`, `year`, `km`, `price`,
   `fuel`, `transmission`, `photo_url`).
6. **Registrar run**: `record_run(conn, source_key, ok=True, declared_total=X,
   captured_distinct=Y)` → fila en `harvest_run` + update de `source_health`.
7. **Coverage gate**: `verify_coverage(conn, source_key, declared_total=X,
   captured_distinct=Y)` — `_COVERAGE_TOLERANCE=0.30`, floor `_DEFAULT_FLOOR=0.85`,
   ceiling `_COVERAGE_CEILING=1.15`.
8. **Pasar a INGEST**: llamar `ingest_dealer(conn, geo, harvest, source_key)` —
   ver `04-INGEST.md`.

---

## Gate de verificación

| Condición | Umbral | Acción si falla |
|---|---|---|
| Coverage floor | `captured_distinct / declared_total >= 0.85` | alert + lane RESEARCH |
| Coverage ceiling | `captured_distinct / declared_total <= 1.15` | alert (sobre-cobertura = señal de error) |
| Circuit breaker | `consecutive_fails < BREAKER_TRIP_AT=3` | source excluida de scheduler |

---

## Artefactos

- `harvest_run` — fila por ejecución (`source_key`, `started_at`, `ok`, `rows`, `error`, `http_status`; no tiene columnas `declared_total`/`captured_distinct` — esos valores se pasan a `verify_coverage()` como args de `record_run()` pero no se persisten en `harvest_run`)
- `source_health` — last_ok / last_fail / consecutive_fails actualizados
- `vehicle` — filas insertadas / actualizadas (ver `04-INGEST.md`)

---

## Fallo → routing

| Fallo | Acción |
|---|---|
| HTTP 429 / 5xx persistente (>= trip_at) | `fire_alert(source_key, phase='scrape', severity='warning')` + `auto_repair('escalate_tier')` si Tier-0, `auto_repair('re_receta')` si recipe corrupta |
| Coverage bajo floor | alert severity='warning' + `gestion_item` lane RESEARCH |
| `consecutive_fails >= 3` | circuit breaker → OPEN, cooldown 900 s |

---

## Idempotencia

- `harvest_run`: insert append-only por `(source_key, started_at)`; no hay UPSERT — cada corrida produce una fila nueva.
- `vehicle`: `INSERT ON CONFLICT (entity_ulid, deep_link) DO UPDATE` — re-ejecución safe (la constraint única real en la tabla `vehicle` es `UNIQUE (entity_ulid, deep_link)`, no `(source_key, external_id)`).

---

## Estado

**HARVEST-GATED** — Los 44 conectores en `pipeline/platform/` están IMPLEMENTADOS.
La ejecución real contra dealers en producción requiere gasto (proxies premium para Tier-1,
camoufox/BotBrowser para dealers con bot-detection activa). El motor `fetch.py` + `governor.py`
están operativos para Tier-0 (open HTTP) sin gasto adicional.

Nota Tier-1 stub: `fetch.py` dispara `raise NotImplementedError` si `tier >= 1` — el camino
camoufox/BotBrowser está diseñado pero no activado.

---

## €0 vs gasto

| Componente | Coste |
|---|---|
| `fetch.py` Tier-0 (curl_cffi, sin proxy premium) | €0 |
| `governor.py`, parseo, `record_run` | €0 |
| Proxies premium Tier-1 (dealers con bot-detection) | GASTO |
| camoufox / BotBrowser para milanuncios y similares | GASTO |
