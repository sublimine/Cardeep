# E2E Fase 1 — DESCUBRIR

## Objetivo

Dada una fuente del censo, producir entidades reales (puntos de venta: concesionarios,
compraventas, garajes, desguaces) con coordenadas INE y codigo unico `cdp_code`, e
ingerirlas idempotentemente en la tabla `entity`.

## Disparador

```
python -m pipeline.discover [--source <adapter>] [--province XX]
```

Tambien invocado por `pipeline/ops/scheduler.py` en cadencia configurada.

## Entradas

### Adaptadores de fuente (`ADAPTERS` dict en `pipeline/discover.py`)

| Clave | Fuente | Descripcion |
|---|---|---|
| `dgt_cat` | DGT CATV | Desguaces del censo oficial DGT |
| `oem_kia` | KIA ES | Red oficial de concesionarios KIA |
| `oem_mg` | MG ES | Red oficial de concesionarios MG |
| `oem_byd` | BYD ES | Red oficial de concesionarios BYD |
| `oem_skoda` | Skoda ES | Red oficial de concesionarios Skoda |
| `oem_dacia` | Dacia ES | Red oficial de concesionarios Dacia |
| `oem_hyundai` | Hyundai ES | Red oficial de concesionarios Hyundai |
| `oem_mercedes` | Mercedes ES | Red oficial de concesionarios Mercedes |
| `oem_seat` | SEAT ES | Red oficial de concesionarios SEAT |
| `osm` | OpenStreetMap | Nodos OSM con tag `shop=car` / `amenity=car_repair` |

### Tabla geo INE

Referencia interna de municipios espanoles con `province_code` (01–52) y `municipality_code`.
Usada para resolver nombre de localidad a codigo INE canonico.

### DSN de base de datos

Variable de entorno `CARDEEP_DSN` o default:
```
postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep
```

## Pasos atomo

### Paso 1 — Inicializar adaptador de fuente

```python
adapter = SourceAdapter.__init__(source_key)
```

Carga configuracion del adaptador: URL base, autenticacion si aplica, parametros de
paginacion, y mapeo de campos de la respuesta a `DiscoveredEntity`.

### Paso 2 — Iterar entidades candidatas de la fuente

Loop geo INE: por cada provincia (filtrada si se paso `--province`), por cada municipio,
solicitar entidades candidatas a la fuente. El adaptador devuelve un iterable de
`DiscoveredEntity` con los campos crudos de la fuente.

La iteracion usa `pipeline/engine/fetch.py` (curl_cffi chrome131, retry 4x, polite 0.7–1.4s)
y `pipeline/engine/governor.py` (token bucket 0.7 req/s, burst 3) para respetar rate limits.

### Paso 3 — Geocodificacion

```python
geo = geocoder.resolve(entity.locality, entity.province_name)
```

Resolucion de nombre de localidad a `(lat, lon, municipality_code, province_code)`.
Fallback por `cdp_code` si el nombre no resuelve: se ingiere con `municipality_code = NULL`
(honesto), no se descarta.

Modulo: `pipeline/geocode.py` (referenciado desde `discover.py`).

### Paso 4 — Upsert en tabla `entity`

```python
_upsert(conn, geo, entity, geocoder=None)
```

Construye `cdp_code` por orden de confianza:
1. Dominio web del dealer (mayor especificidad)
2. CIF fiscal
3. Nombre + municipio
4. Nombre + provincia (fallback mas amplio)

Ejecuta:
```sql
INSERT INTO entity (cdp_code, source_key, name, lat, lon, province_code, municipality_code,
                    status, last_seen, ...)
VALUES (...)
ON CONFLICT (cdp_code) DO UPDATE SET
    last_seen = now(),
    source_key = EXCLUDED.source_key,
    lat = COALESCE(EXCLUDED.lat, entity.lat),
    lon = COALESCE(EXCLUDED.lon, entity.lon)
```

### Paso 5 — Gate VAM post-discover

```python
await record_count_verdict(
    conn,
    subject_type="source",
    subject_key=source_key,
    claim="entity count == declared count",
    paths={"db_ingested": in_db, "fetched": len(entities), "source_declared": declared},
    tolerance=0.0)
```

Registra el conteo de entidades ingeridas como quorum VAM de tres vias ortogonales:
`db_ingested` (SELECT COUNT en entity_source), `fetched` (iterable del adaptador),
`source_declared` (adapter.declared_count()). La fuente es TRUSTWORTHY cuando el valor
modal tiene ≥2 paths de acuerdo y ningun rival rival alcanza ≥2.

Modulo: `pipeline/verify.py`.

### Paso 6 — Commit atomico por batch

Cada batch de entidades se commitea de forma atomica. Un fallo en el batch N no
revierte los batches N-1 ya commiteados. El batch fallido genera una alerta con
`phase='discover'` y `subject_key=source_key`.

## Gate de verificacion

| Condicion | Accion si falla |
|---|---|
| VAM quorum ≥2 vias sobre conteo de entidades: TRUSTWORTHY | No avanza a SCRAPE; verdict queda como `REFUTED` o `UNVERIFIED` (no `UNTRUSTWORTHY` — ese valor no existe en el CHECK constraint de `verification_verdict`) |
| `cdp_code` bien formado (no vacio, no colision por ambiguedad) | Entidad se marca `status='cdp_collision'`; excluida |
| `province_code` in "01"–"52" | Entidad se ingiere con `province_code = NULL`; reportada |
| Tasa de geo-resolucion >= umbral configurado por fuente | Alerta `GEO_RESOLUTION_LOW`; no bloquea |

## Artefactos

| Artefacto | Tabla / Ruta | Descripcion |
|---|---|---|
| Entidades descubiertas | `entity` | Una fila por punto de venta unico |
| Proveniencia multi-fuente | `entity_source` | Relacion entidad-fuente para dedup y capture-recapture |
| Veredicto VAM | `verification_verdict` | `subject_type='source'`, `subject_key=source_key` |
| Alerta de fallo | `alert` | Si la fuente es inalcanzable o VAM falla |

## Fallo y routing

| Tipo de fallo | Comportamiento |
|---|---|
| Fuente HTTP inalcanzable (tras 4 reintentos) | `fire_alert(source_key, phase='discover')` → `gestion_item` lane RESEARCH; se continua con otras fuentes |
| VAM REFUTED / UNVERIFIED | Entidades ingeridas permanecen con `status='unverified'` (default del schema); no avanzan a SCRAPE (nota: el valor `UNTRUSTWORTHY` no existe — el CHECK de `verification_verdict` solo admite `TRUSTWORTHY`, `REFUTED`, `UNVERIFIED`, `QUARANTINED`) |
| Geocodificacion < umbral | Alerta informativa; el discover continua |
| Drift de esquema en respuesta de la fuente | Alerta `SCHEMA_DRIFT`; adaptador se desactiva para esa fuente hasta revision |

El barrido global nunca aborta por el fallo de una fuente individual.

## Idempotencia

```sql
INSERT INTO entity (...) ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()
```

Re-descubrir la misma entidad:
- No produce duplicados
- Refresca `last_seen`
- Actualiza geo si antes era NULL y ahora se resuelve
- Preserva `status` actual (no lo regresa a 'discovered' si ya esta en fase superior)

## Estado

IMPLEMENTADO — `pipeline/discover.py`

Los 10 adaptadores listados en la tabla de entradas estan activos y han producido datos
en corridas de produccion anteriores.

## €0 vs gasto

**€0.** Sin LLM, sin proxies premium, sin APIs de pago.

Solo HTTP ligero con curl_cffi (browser fingerprint gratuito) + PostgreSQL local.
Las fuentes del censo son publicas (DGT, OEM, OSM) o de acceso abierto.
El governor de rate limit protege de bans sin necesitar infraestructura de pago.
