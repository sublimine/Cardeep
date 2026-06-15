# 05 — SERVE-API

Servir inventario y datos de entidades via API REST con rate limiting, cache in-process y paginacion controlada.

## Disparador

HTTP request entrante. Levantar el servidor:

```bash
uvicorn services.api.main:app --host 127.0.0.1 --port 8090
```

## Entradas

- HTTP request: method, path, query params
- Parametros de paginacion: `page` (default 1), `size` (default 50, max 200)
- DB cardeep-pg: read-only para todos los endpoints de datos

## Pasos atomo

1. **Rate limit check** — slowapi in-memory, 120/min global, 30/min para endpoints costosos (`inventory`, `geo-tree`, `geo-completeness`, `platform`). Retorna 429 con envelope personalizado si se excede el limite.

2. **Cache check** — `try_cache_get(request)`. Si hit: retornar respuesta cacheada con `meta.cache="hit"` sin tocar DB. Solo activo para paths cacheables: `/geo/`, `/entities/` (inventory), `/platforms/`.

3. **FastAPI dependency injection** — `deps.py` provee conn pool al DB y valida parametros de entrada.

4. **Router dispatch** — despacho al router correspondiente segun path:
   - `entities.py` → datos de dealer/entidad
   - `geo.py` → datos geograficos
   - `ops.py` → operaciones internas (health, alerts, sources)
   - `platforms.py` → plataformas de listado
   - `vehicles.py` → vehiculos individuales

5. **Query DB** — SELECT puro. Sin writes en el path de lectura.

6. **Envelope response** — estructura estandar:
   ```json
   {
     "ok": true,
     "data": [...],
     "error": null,
     "meta": { "page": 1, "size": 50, "returned": 42, "has_more": false }
   }
   ```

7. **Cache set** — `cache_set(request, response)` si la respuesta es 2xx y el path es cacheable. TTL=60s, maxsize=512 entradas (TTLCache cachetools).

## Gate de verificacion

| Parametro | Restriccion |
|-----------|-------------|
| `size` | rango [1, 200] — rechazado fuera de limites |
| Rate limit global | 120 req/min — 429 si excedido |
| Rate limit costosos | 30 req/min — aplica a `inventory`, `geo-tree`, `geo-completeness`, `platform` |
| Endpoints no cacheables | `/health`, `/alerts`, `/sources` — siempre fresh, nunca del cache |
| Writes en DB | Prohibidos en path de lectura |

## Routers disponibles

| Router | Endpoints principales |
|--------|----------------------|
| `entities.py` | `GET /entities/{cdp_code}`, `GET /entities/{cdp_code}/inventory`, `GET /entities/{cdp_code}/canonical`, `GET /entities/{cdp_code}/delta` |
| `geo.py` | `GET /geo/completeness`, `GET /geo/{province_code}/entities`, `GET /geo/{province_code}/municipalities/{muni_code}/entities`, `GET /geo/{province_code}/tree` |
| `ops.py` | `GET /health`, `GET /alerts`, `GET /sources` |
| `platforms.py` | `GET /platforms/{cdp_code}/inventory`, `GET /vehicles/{vehicle_ulid}/platforms` |
| `vehicles.py` | `GET /vehicles/{vehicle_ulid}`, `GET /vehicles/{vehicle_ulid}/history` |

## Fallo — routing de errores

| Codigo | Causa | Respuesta |
|--------|-------|-----------|
| 429 | Rate limit excedido | `{ok: false, error: "rate_limit_exceeded", meta: {detail, retry_after}}` |
| 500 | Error interno | `{ok: false, error: "internal_server_error", data: null}` + log |
| 503 | DB timeout | envelope con `retry-after` |

## Idempotencia

GET es idempotente por definicion. Cache TTL=60s evita storm de DB ante rafagas de lecturas identicas.

## Artefactos

- HTTP response con envelope estandar `{ok, data, error, meta}`
- `meta.cache`: `"hit"` o `"miss"` en la respuesta
- Sin escrituras a DB (path de lectura puro)

## Estado

IMPLEMENTADO — `services/api/main.py`, `services/api/ratelimit.py`, `services/api/cache.py`, `services/api/routers/`

Control de rate limit: `CARDEEP_API_RATELIMIT_ENABLED` (default `"1"`). Poner a `"0"` solo en entornos de desarrollo local.

## Coste

€0 total — reads de DB local, sin LLM, sin HTTP externo.
