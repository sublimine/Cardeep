# 00 · OVERVIEW — cómo se scrapea el país END-TO-END

> El recorrido de un coche desde que existe en una web ajena hasta que la API de Cardeep lo
> sirve con su delta. Pipeline canónico: **DESCUBRIR → SCRAPEAR → RECETA → API → DELTA**.
> Esta página es el mapa; el detalle del motor está en [01-ARCHITECTURE.md](01-ARCHITECTURE.md),
> la separación de fuentes en [02-GROUP-SEPARATION.md](02-GROUP-SEPARATION.md), y cada conector
> en su `platforms/<slug>.md`.

---

## 1. La misión en una frase

Servir el **100 % de los puntos de venta de coches de España** en una API viva, con
**delta + historial**, donde cada número está **validado por ≥2 caminos ortogonales** y
persistido en `verification_verdict`. Nada se sirve "a ojo": un coche entra solo si una fila
de veredicto TRUSTWORTHY lo avala y el conector re-ejecuta idempotente.

Estado vivo de la cosecha (esta sesión, `SELECT count(*)`):

| tabla | vivo | tabla | vivo |
|---|---:|---|---:|
| `entity` | 368.301 | `vehicle` | 1.485.133 |
| `platform_listing` | 1.438.443 | `verification_verdict` | 587 (577 TRUSTWORTHY / 10 REFUTED) |
| `geo_province` | 52 | `geo_comarca` | 323 |
| `geo_municipality` | 8.132 | muni con comarca | 8.130 (99,98 %) |

---

## 2. El pipeline, fase por fase

```
DESCUBRIR ──▶ SCRAPEAR ──▶ RECETA ──▶ API ──▶ DELTA
 (qué existe)  (cómo se      (se      (se      (qué
               saca)         persiste) sirve)   cambió)
```

### 2.1 DESCUBRIR — qué fuentes existen

El país no es una lista plana de webs: es un grafo de **fuentes clasificadas por naturaleza**
(Tier-1 marketplaces, portales OEM-VO, cadenas, rent-a-car, subastas, long-tail own-site). El
eje de clasificación vive en `migrations/0016_tiering_groups.sql` (`source_group`, `kind`,
`defense_tier`) y se explica en [02-GROUP-SEPARATION.md](02-GROUP-SEPARATION.md). El
descubrimiento puebla `entity` (el punto de venta) y `entity_source` (la procedencia
capture-recapture), acuñando para cada entidad un `cdp_code` inmutable y determinista
(`services/api/codes.py`).

### 2.2 SCRAPEAR — cómo se saca el stock

Cada fuente expone una **superficie de datos** distinta (gateway JSON, GraphQL, SSR HTML,
JSON-LD, sitemap). El motor de fetch (`pipeline/engine/fetch.py`, `curl_cffi
impersonate=chrome131`) emite el fingerprint TLS/JA3 de Chrome real y se escala a navegador
(camoufox/Playwright) **solo ante un challenge tipado** ("optimism is free; escalation is on
evidence"). TODO fetch pasa por el **governor** (`pipeline/engine/governor.py`): un
token-bucket por host, el único choke point de rate, que impide repetir la cicatriz AS24
(138 dealers caídos por throttling agregado). Dos clases de rate: **STEALTH** (0,7 req/s,
default, techo no medido) y **JSON_API** (12 req/s, gateways first-party).

### 2.3 RECETA — cómo se persiste

El stock cosechado se materializa en el esquema bajo el modelo de **doble membresía**:

- **Ownership** — `vehicle.entity_ulid` apunta SIEMPRE al dealer/punto de venta vendedor.
  Un coche tiene exactamente **1 dueño**.
- **Membership** — `platform_listing (vehicle_ulid, platform_entity_ulid, …)` es la arista
  plural: el mismo coche físico puede colgar de coches.net *y* wallapop *y* un portal OEM-VO
  sin cambiar de dueño (0..M aristas por coche).

La ingesta es idempotente (`ON CONFLICT`): re-run = 0 coches nuevos si nada cambió. Cada
conector escribe además su `FAMILY_RECIPE`/config y registra su run en S-HEALTH
(`harvest_run`, `source_health`, `source_breaker`).

### 2.4 API — cómo se sirve

FastAPI sobre PostgreSQL (`services/api/main.py`), envelope consistente `{ok, data, error,
meta}`. Sirve la entidad + su inventario, el delta de eventos, el árbol geo
`país→provincia→comarca→ciudad`, la completitud nacional, y el inventario de cualquier
plataforma vía `platform_listing` con atribución de dealer. Confirmado vivo (veredicto
`api_serves` id=583, todos los endpoints 200).

### 2.5 DELTA — qué cambió

`vehicle_event` es un log append-only (trigger `cardeep_block_mutation` prohíbe UPDATE/DELETE)
con enum `vehicle_event_type` (`NEW, GONE, REAPPEARED, PRICE_CHANGE, PHOTO_CHANGE, KM_CHANGE,
STATUS_CHANGE, SPEC_CHANGE`). Cada pasada genera el delta sobre el snapshot anterior; la API lo
sirve por `/entities/{cdp_code}/delta?since=ISO`. El historial nunca se reescribe.

---

## 3. La puerta de "validado" (VAM)

Una unidad entra al runbook **solo** si:

1. Existe fila `verification_verdict` **TRUSTWORTHY** (≥2 caminos ortogonales, `divergence`
   dentro de tolerancia, invariante de landed-count: el conteo DB debe estar entre los que
   coinciden).
2. El conector re-ejecuta **idempotente** (re-run = 0 nuevos).
3. El número concuerda por **≥2 caminos DB** (`db_edges == db_join_vehicles == db_distinct_refs`).

Si falta una, va a [NOT-VALIDATED.md](NOT-VALIDATED.md), nunca al cuerpo. El ledger vivo de
TODO lo que sí pasó la puerta está en [VALIDATION-INDEX.md](VALIDATION-INDEX.md).

---

## 4. Mapa de lectura

| Quiero entender… | Voy a… |
|---|---|
| El motor (governor, fetch, schema, geo, VAM, S-HEALTH, API, dedup) | [01-ARCHITECTURE.md](01-ARCHITECTURE.md) |
| Por qué Tier-1 ≠ OEM-VO ≠ cadenas ≠ rentacar ≠ subastas ≠ long-tail | [02-GROUP-SEPARATION.md](02-GROUP-SEPARATION.md) |
| Un grupo y sus miembros | `groups/<grupo>.md` |
| Un conector concreto (data-layer, micro-acciones, receta, VAM, CLI) | `platforms/<slug>.md` |
| Qué está validado, con su id + count + CLI | [VALIDATION-INDEX.md](VALIDATION-INDEX.md) |
| Qué se intentó y NO entró (y por qué) | [NOT-VALIDATED.md](NOT-VALIDATED.md) |
