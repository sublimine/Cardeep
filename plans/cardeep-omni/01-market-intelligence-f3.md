# F3 — Router `services/api/routers/market.py` + corrección de `Api.tsx` — CERRADO Y VERIFICADO

> Ejecutado 2026-07-18. Depende de F1+F2 (sirve exactamente lo que esas fases
> computaron y publicaron — nunca agrega en caliente sobre `vehicle`/`vehicle_event`,
> per carta §5: "Solo lee `market_stat` del run publicado").

## 1. Alcance construido

- `services/api/routers/market.py` (nuevo): `GET /market/segments/{make}/{model}/stats`
  (M1/M3/M4/M5/M7/M9/M10) y `GET /market/provinces/demand` (M5, ranking).
- `services/api/main.py`: router registrado (`app.include_router(market.router)`).
- `services/api/cache.py`: `/market/` añadido a `CACHEABLE_PATH_PREFIXES` (mismo
  patrón que `/geo/`/`/entities/`/`/platforms/` — cambia solo cuando se publica un
  run nuevo, no por petición).
- `web/src/pages/Api.tsx`: catálogo de endpoints reescrito línea a línea, ejemplo de
  código (curl + respuesta) reescrito con datos reales.

## 2. Endpoints DELIBERADAMENTE ausentes (declarado, no un hueco oculto)

- **M2** (`/market/price-position/{vehicle_ulid}`) — es el alcance de **F5**. Crearlo
  ahora sin la lógica de ratio real sería exactamente el vicio de mock que este pilar
  existe para eliminar.
- **M8** (`/market/dgt-corroboration`) — es el alcance de **F4**. La tabla
  `dgt_corroboration` no existe todavía.
- **M6** (curva de valor por edad) — está en el diseño del router de la carta §5 pero
  **nunca fue asignada a ninguna fase F0-F5 en la propia carta §9** (F1=M1 solo,
  F2=M3/M4/M5/M7/M9/M10 explícito, F7=M6 SOLO longitudinal). Hueco de numeración de
  fases heredado de la carta, no introducido aquí. Declarado en el docstring del
  router y en los tests (`test_every_served_metric_key_is_authorized` verifica que
  M2/M6/M8 NUNCA aparecen en la respuesta). Pendiente de una fase futura.

## 3. Verificación — protocolo de contrato FastAPI (criterio F3 explícito)

`tests/test_market_router.py` — 11 tests contra la DB viva con el run real publicado
en F2 (`01KXS6Q4TJKCWM19KKQN2SJ2J1`), patrón `TestClient` (igual que
`test_api_pagination.py`):

- Segmento real conocido (Peugeot 208 2024 Gasolina) → 200, M1 presente con
  `p25≤p50≤p75`, envelope con `run_id`/`run_at`/`window_description`.
- Ningún metric_id fuera de `{M1,M3,M4,M5,M7,M9,M10}` — M2/M6/M8 verificados AUSENTES.
- Fallback nacional cuando no se pide provincia (`fallback_to_national=False`,
  `scope='nat'`).
- Provincia de baja muestra (Soria, `42`) → fallback honesto a nacional con
  `fallback_to_national=True` cuando la cohorte provincial no alcanza n≥8 — nunca un
  404, nunca un número provincial inventado.
- Segmento inexistente → 404 con envelope de error coherente.
- Falta de query param requerido (`year`/`fuel`) → 422 (FastAPI `Query(...)`).
- `/market/provinces/demand`: 200, lista ordenada descendente por tasa de absorción,
  cada fila con `n_available≥8` (piso anti-ruido de M5), envelope con `count`.

**11/11 PASSED** (5,02s — rápido porque son lookups por clave exacta, no escaneos).

## 4. OpenAPI refleja la realidad (criterio F3 explícito)

Verificado con `app.openapi()`: únicamente `GET /market/segments/{make}/{model}/stats`
y `GET /market/provinces/demand` aparecen bajo `/market`. Ningún endpoint fantasma.

## 5. `Api.tsx` — catálogo reescrito sin un solo endpoint ficticio

Catálogo anterior (`GET /v1/valuation/{vin}`, `GET /v1/history/{vin}`,
`GET /v1/market/{model}`, `GET /v1/deal-score/{listing}`, `GET /v1/inventory`,
`GET /v1/inventory/{id}`) — **ninguno existe**, confirmado por
`grep -rn "@router\.get" services/api/routers/` (26 endpoints reales enumerados,
0 coincidencias). Reemplazado por 6 endpoints REALES:
`GET /market/segments/{make}/{model}/stats`, `GET /market/provinces/demand`,
`GET /vehicles/{ulid}/history`, `GET /vehicles/{ulid}/lifetime`,
`GET /entities/{cdp_code}/inventory`, `GET /entities/{cdp_code}/delta`.

Ejemplo de código (curl + JSON de respuesta) reescrito con el endpoint real
`/market/segments/Peugeot/208/stats?year=2024&fuel=Gasolina` y los números REALES de
la corrida publicada en F2 (M1 n=7.026 p50=13.500; M3 mediana=10,2 días; M4 MDS=547,7;
M9 17,9% con recorte) — no un ejemplo inventado.

**Alcance deliberadamente NO tocado** (fuera del criterio "catálogo sin endpoints
ficticios"): el panel de consumo de tokens (`TOKEN_BALANCE`/`CONSUMPTION_DATA`/
`INITIAL_KEYS`/`PLANS`) sigue siendo una maqueta de producto — no existe un sistema
real de medición de tokens en el backend. Tocar eso es un sistema de billing
completo, fuera del alcance de esta carta (que solo exige el catálogo de endpoints
honesto). Declarado aquí explícitamente, no escondido.

## 6. Verificación de no-regresión

- `npx tsc --noEmit` sobre `web/`: **0 errores** (Api.tsx compila limpio).
- `tests/test_web_no_fabricated_data.py`: 4 passed, 1 skipped (preexistente, no
  relacionado) — sin regresión del gate anti-mock existente.
- Suite ampliada de tests de API existentes (`test_api_auth`, `test_api_canonical`,
  `test_api_gaps`, `test_api_pagination`, `test_api_ratelimit_cache`, `test_api_seal`):
  ver resultado en el commit — cero regresión por registrar `market.router` o añadir
  `/market/` a `CACHEABLE_PATH_PREFIXES`.

## Cierre F3

Los 3 criterios de la carta §9-F3 en verde: tests de contrato FastAPI por endpoint
incluidos 404/muestra-insuficiente ✓; OpenAPI generado refleja la realidad ✓;
`Api.tsx` reescrito sin un solo endpoint ficticio, revisado línea a línea ✓. Caché y
paginación siguen el mismo patrón que `entities.py`/`geo.py` (TTLCache module-level,
`try_cache_get`/`cache_set`).
