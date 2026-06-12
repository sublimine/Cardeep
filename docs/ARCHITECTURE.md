# CARDEEP — Arquitectura de datos y ciclo de vida (F2)

> La columna vertebral sobre la que escriben los workflows. Diseñada para el mandato:
> 100% de puntos de venta de ESPAÑA, inventario vivo con delta+historial, geo
> provincia→comarca→municipio, código único por dealer, Tier-1 separado, resiliencia.

## Motor
- **PostgreSQL 16** en Docker (`cardeep-pg`, puerto **5433**, volumen `cardeep_pg_data`).
  Separado físicamente de cualquier otro proyecto. DSN dev:
  `postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep`.
- **FastAPI + asyncpg** para la API viva (`services/api`).
- Migraciones SQL numeradas, aditivas, idempotentes (`IF NOT EXISTS`) y reversibles
  (`-- Rollback:` inline). Patrón de aplicación E2E: apply → verificar → rollback →
  verificar limpio → re-apply → contar filas preservadas → idempotencia.

## Doctrina de mutación (del CLAUDE.md §4.4)
- **INSERT** de lo nuevo + **DELETE/cierre** de lo desaparecido. Nunca UPDATE de filas
  **no mutadas**. Una fila cuyo dato real cambió (precio, foto) SÍ se actualiza —y se
  emite su evento—; las que no cambiaron solo refrescan `last_seen`.
- **Historial append-only** en `vehicle_event`: cada NEW/GONE/PRICE_CHANGE/PHOTO_CHANGE
  es una fila inmutable. El historial jamás se borra.

## Modelo (capas)

### Geo (backbone INE) — `migrations/0001`
```
geo_province     52 provincias  (code CHAR(2) PK, name, ccaa_code, ccaa_name)
geo_comarca      comarcas/agrupaciones (id PK, province_code FK, name)   [nullable en entidad]
geo_municipality ~8.131 municipios (code CHAR(5) PK, name, province_code FK, comarca_id FK, lat, lon)
```
Geo es la rejilla de organización del mandato ("por provincia, comarcas, ciudad").
`province_code` = 2 primeros dígitos del `municipality.code` (invariante INE).

### Entidad (punto de venta) — `migrations/0002`
```
entity
  entity_ulid    TEXT PK (ULID, ordenable por tiempo)
  cdp_code       TEXT UNIQUE  -- código único inmutable Cardeep, CDP-ES-{prov}-{b32}
  kind           TEXT  -- concesionario_oficial | compraventa | garaje | desguace | plataforma | cadena
  legal_name / trade_name
  cif            TEXT  -- verdad jurídica (registral), nullable
  cnae           TEXT  -- 4511/4520/4677..., nullable
  province_code / municipality_code / comarca_id  -- geo (FK)
  address / postcode / lat / lon / phone / email
  website        TEXT
  website_waf    TEXT  -- none|cloudflare|akamai|datadome|perimeterx|imperva  (routing F5)
  is_tier1       BOOLEAN  -- separación dura: plataformas de defensa dura
  status         TEXT  -- active | closed | unverified
  recipe_version INT   -- puntero a la receta en git (countries/ES/.../recipe.yaml)
  created_at / last_seen / first_discovered_source

entity_source   -- provenance multi-fuente (capture-recapture + dedup)
  entity_ulid FK, source_key, source_ref, seen_at   UNIQUE(entity_ulid, source_key)

entity_alias    -- variantes de nombre/dominio para dedup
  entity_ulid FK, alias, alias_kind  UNIQUE(entity_ulid, alias)
```
`cdp_code` es determinista sobre la identidad canónica (dominio > cif > nombre+municipio):
re-descubrir la misma entidad por otra fuente NO crea duplicado.

### Inventario (vehículo + delta) — `migrations/0003`
```
vehicle
  vehicle_ulid  TEXT PK
  entity_ulid   FK
  deep_link     TEXT  -- URL del vehículo;  UNIQUE(entity_ulid, deep_link)
  title / make / model / year / km / price / currency / fuel / transmission
  photo_url / photo_hash  -- pHash perceptual para Δfoto
  vin_ref       TEXT nullable
  recipe_version INT
  status        TEXT  -- available | gone
  first_seen / last_seen

vehicle_event   -- HISTORIAL append-only (el delta del mandato)
  event_ulid PK, vehicle_ulid FK, entity_ulid FK
  event_type  -- NEW | GONE | PRICE_CHANGE | PHOTO_CHANGE | KM_CHANGE
  old_value / new_value   -- JSON
  observed_at
```
Delta = diff snapshot↔snapshot por entidad: `NEW` = en cosecha nueva no servida;
`GONE` = servida que ya no aparece (status→gone + evento, no hard-delete);
`PRICE/PHOTO/KM_CHANGE` = fila mutada → update del campo + evento.

### Verdad y resiliencia — `migrations/0004`
```
verification_verdict   -- VAM (el juez de "terminado")
  subject_type/subject_key/claim/primary_value/primary_path/
  verifier_paths(JSON)/independent_values(JSON)/divergence/verdict/evidence/created_at
  CHECK verdict IN ('TRUSTWORTHY','REFUTED','UNVERIFIED')

source_health   -- watchdog por fuente (F7 auto-repair + alerta origen-exacto)
  source_key PK, last_ok, last_fail, consecutive_fails, status

alert   -- alertas con origen exacto
  id PK, origin, severity, message, payload(JSON), created_at, resolved_at
```

## API viva (contrato, F2 esqueleto → F6 completo)
- `GET /health` — liveness + conteos.
- `GET /entities/{cdp_code}` — entidad + inventario actual.
- `GET /entities/{cdp_code}/inventory` — stock vivo (status=available).
- `GET /entities/{cdp_code}/delta?since=` — eventos (altas/bajas/Δprecio/Δfoto).
- `GET /geo/{province_code}/entities` — entidades por provincia (rejilla del mandato).
- Envelope consistente `{ok, data, error, meta}`. Validación en el borde; INSERT-only.

## Separación Tier-1
`entity.is_tier1` + árbol de código/recetas `countries/ES/_tier1/` aparte del long-tail.
Una plataforma Tier-1 nunca comparte receta, store de crudo ni operación con el resto.
