# CARDEEP — Runbook operativo

> Estado vivo. Cada sección documenta un mecanismo real, no una aspiración.
> El Director revisa + actualiza tras cada cambio de arquitectura.

---

## Resolucion de entidad (F1 - beta)

### Que es

La resolucion de entidad (beta) es el pilar del estrato P (profesionales).
Responde a: "dos fichas distintas en la DB son el mismo dealer fisico?"

Beta opera SOLO sobre entidades P (kind IN compraventa, concesionario_oficial, garaje).
Nunca toca particulares (R) ni plataformas (C).

El resultado es `entity_resolution`: para cada entidad P, el `resolved_dealer_ulid`
canonico al que pertenece. Un dealer fisico = un `resolved_dealer_ulid`.
`S_obs` = `n_resolved_dealers` = el numero de dealers profesionales unicos derivados
(el numerador real del estrato P para Chao2).

Estado actual (run entity-resolution-fingerprint-v1, 2026-06-14):
- n_in = 59.502 entidades P
- S_obs = 52.156 dealers profesionales unicos
- n_merged = 7.346 (12.35% colapso)
- vam_verified = FALSE (pendiente gate del Director)

### Como corre

```bash
# Pre-requisito: migracion 0025 aplicada
# Pre-requisito: B7 (vehicle-identity-det-v1) ejecutado con datos de km>0

cd /path/to/cardeep
python -m pipeline.identity.resolve_entities
# O directamente:
python pipeline/identity/resolve_entities.py
```

Idempotente: borra el run anterior antes de escribir.
No toca la tabla `entity` ni ninguna fila existente.

### Como leer entity_resolution y v_resolved_dealer

```sql
-- Estadisticas del run activo
SELECT run_id, n_in, n_resolved_dealers, n_merged, vam_verified, notes
FROM entity_resolution_run
ORDER BY run_at DESC LIMIT 5;

-- Dealers derivados (solo aparece cuando hay un run vam_verified=TRUE)
SELECT entity_ulid, cdp_code, trade_name, kind, province_code,
       resolved_dealer_ulid, resolved_dealer_name, signal, probability
FROM v_resolved_dealer
LIMIT 50;

-- Sin gate VAM: leer directamente del run
SELECT er.entity_ulid, e.trade_name, e.kind, e.province_code,
       er.resolved_dealer_ulid, rd.trade_name AS canonical_name,
       er.signal, er.probability,
       COUNT(*) OVER (PARTITION BY er.resolved_dealer_ulid) AS cluster_size
FROM entity_resolution er
JOIN entity e  ON e.entity_ulid  = er.entity_ulid
JOIN entity rd ON rd.entity_ulid = er.resolved_dealer_ulid
WHERE er.run_id = 'entity-resolution-fingerprint-v1'
  AND er.signal <> 'none'
ORDER BY cluster_size DESC, er.resolved_dealer_ulid, e.trade_name
LIMIT 100;

-- S_obs verificado
SELECT n_resolved_dealers AS s_obs
FROM entity_resolution_run
WHERE run_id = 'entity-resolution-fingerprint-v1';
```

### Logica de negocio: como se decide que dos entidades son el mismo dealer

**Clave dominante -- huella de inventario (Jaccard):**
Por cada par de entidades P de fuentes distintas, se calcula el Jaccard de sus
conjuntos de canonical_vehicle_ulid (coches de ocasion, km>0, del run B7).
Si Jaccard >= 0.30 --> misma empresa fisica.

Solo se usan canonicals de ocasion (km>0) y con baja colision (<5 entidades P
distintas). Esto excluye el stock nuevo de catalogo (Seat Leon km=0 aparece
en 88 entidades = es el catalogo OEM, no el mismo dealer).

**Identificadores de refuerzo (donde existen):**
- Mismo telefono normalizado (9 digitos) + misma provincia --> arista.
- Mismo dominio de website + misma provincia --> arista.

**Guardar anti-sobre-fusion (critica):**
1. Telefono compartido por >= 3 entidades P = centralita / gestoria.
   Solo fusiona si ADEMAS hay un website limpio (no alto-colision) en la misma
   provincia. Sin huella Jaccard, la centralita sola no fusiona.
2. Cross-provincia sin huella Jaccard >= 0.30 --> BLOQUEADO.
   Ni telefono ni website solos pueden fundir entidades de provincias distintas.
3. Websites de alto-colision (compartido por >= 3 entidades) sin huella --> BLOQUEADO.

**Clausura transitiva:**
Union-Find determinista sobre las aristas aceptadas. Si A comparte huella con B
y B con C, los tres colapsan al mismo dealer canonico.

**Canonico determinista:**
1. Richness (mas campos no nulos: website, phone, municipality, address, cif, lat)
2. n_vehicles (mas coches = mejor representacion)
3. created_at (mas antiguo = mas establecido)
4. entity_ulid lexicografico (desempate final determinista)

### Parametros calibrables

| Constante | Valor | Significado |
|---|---|---|
| JACCARD_THETA | 0.30 | Umbral de Jaccard para huella de inventario |
| MAX_ENTITY_COLLISION_K | 5 | Max entidades P que comparten un canonical para usarlo |
| MAX_PHONE_COLLISION_K | 3 | Max entidades que comparten un telefono antes de considerarlo centralita |
| VEHICLE_CLUSTER_RUN | vehicle-identity-det-v1 | Run B7 que provee los canonicals |

Para recalibrar theta: correr el pipeline con JACCARD_THETA diferente y
verificar los 20 pares de muestra antes de hacer gate VAM.

### Gate VAM (Director)

El run esta marcado vam_verified=FALSE hasta que el Director revise:
1. Los 20 pares de muestra (evidencia de cross-source merge correcto)
2. Los top 15 clusters mas grandes (anti-sobre-fusion)
3. Que ningun cluster fusiona dealers genuinamente distintos

Cuando el Director aprueba:
```sql
UPDATE entity_resolution_run
SET vam_verified = TRUE
WHERE run_id = 'entity-resolution-fingerprint-v1';
```

A partir de ese momento `v_resolved_dealer` devuelve datos.

### Cierre con DIRCE (F2)

F2 calibra el prior fiscal: DIRCE (directorio empresas) interseccionado con
los dealers derivados de F1 --> phi (fraccion-ocasion) --> N_prof estimado.
La tabla `entity_resolution` es el insumo de F2; F1 debe tener gate VAM
antes de que F2 tenga sentido estadistico.

### Tests

```bash
cd /path/to/cardeep
pytest tests/test_resolve_entities.py -v
# Debe dar 42/42 verde
```

Cubre: normalizacion telefono/web, Jaccard, huella fusiona, telefono fusiona,
anti-colision NO fusiona centralita, cross-province bloqueado, transitividad,
seleccion de canonico, singleton.

---

## Verificación de cobertura post-harvest (CAMPAIGN B9)

### Qué es y qué dispara el gate

Después de cada harvest exitoso (`ok=True`), si el conector pasa `declared_total`
a `record_run()`, el gate de cobertura se ejecuta automáticamente:

```
conector.harvest()
  └── record_run(ok=True, declared_total=X, captured_distinct=Y, platform_ulid=Z)
        └── verify_coverage(conn, source_key, declared_total, captured_distinct, platform_ulid)
              ├── cuenta captured_db  (SQL sobre vehicle WHERE first_discovered_source = key)
              ├── cuenta db_edges     (SQL sobre platform_listing WHERE platform_entity_ulid = ulid)
              ├── coverage_pct = captured_db / declared_total
              ├── record_count_verdict(VAM quorum)
              ├── UPSERT source_coverage (idempotente)
              └── coverage_pct < floor → fire_alert + auto_repair
                  coverage_pct ≥ floor → resolve_alerts
```

El gate es `€0`: solo usa datos ya en la DB, no añade peticiones HTTP.
Es backward-compatible: conectores que no pasen `declared_total` siguen funcionando;
simplemente no se emite verdict de cobertura hasta que se cableen.

### Leer source_coverage de un vistazo

```sql
SELECT
    source_key,
    declared_total,
    captured_db,
    db_edges,
    round(coverage_pct * 100, 1) AS "cobertura_%",
    verdict,
    probed_at
FROM source_coverage
ORDER BY coverage_pct ASC NULLS LAST;
```

Responde de un vistazo: "¿cuánto de wallapop tenemos?"

### Qué significa cada campo y cada verdict

| Campo | Significado |
|-------|-------------|
| `declared_total` | Lo que la fuente DICE tener (totalResults, totalHits, etc.) |
| `captured_db` | Vehículos en nuestra DB atribuidos a esa fuente (vía `first_discovered_source`) |
| `db_edges` | Filas en `platform_listing` para esa plataforma (conteo estructural, orthogonal) |
| `coverage_pct` | `captured_db / declared_total`. 1.0 = cobertura total. Puede superar 1.0 si la fuente infra-declara. |
| `verdict` | Resultado del quórum VAM (3 vías) |

| Verdict | Significado |
|---------|-------------|
| `TRUSTWORTHY` | ≥2 vías ortogonales convergen dentro de la tolerancia (±30 %). Cobertura fiable. |
| `REFUTED` | Las vías divergen más allá de la tolerancia. Hay una inconsistencia que investigar. |
| `UNVERIFIED` | Solo 1 vía disponible (p.ej. `declared_total = 0` o `platform_ulid` ausente). Auditable pero no quórum. |

### Qué hacer ante una alerta `*:coverage`

Las alertas tienen origen exacto `<source_key>:coverage`, por ejemplo `wallapop_wholesale:coverage`.

#### Diagnóstico rápido

```sql
-- 1. Ver el estado actual
SELECT * FROM source_coverage WHERE source_key = 'wallapop_wholesale';

-- 2. Ver las últimas alertas de cobertura abiertas
SELECT origin, severity, message, payload, created_at
FROM alert
WHERE origin LIKE '%:coverage' AND resolved_at IS NULL
ORDER BY created_at DESC;

-- 3. Ver los intentos de reparación asociados
SELECT source_key, detected_reason, action, succeeded, attempted_at
FROM repair_attempt
WHERE source_key = 'wallapop_wholesale'
ORDER BY attempted_at DESC LIMIT 5;
```

#### Causas más frecuentes

| Síntoma | Causa probable |
|---------|----------------|
| `declared_total` subió, `captured_db` estable | La fuente añadió inventario nuevo; hay que re-harvestear |
| `captured_db` cayó, `declared_total` estable | Ban a media paginación o error de ingesta silencioso |
| `coverage_pct` > 0.0 pero < floor tras primer harvest | Floor mal calibrado para esta fuente (¿larga cola?) |
| `db_edges` difiere mucho de `captured_db` | Inconsistencia edge–vehicle; posible borrado parcial |
| `declared_total = None` | El conector no pasó `declared_total`; el gate no corrió (gap pendiente) |

#### Acciones

1. **Ban a media paginación**: revisar `source_breaker` + `harvest_run` para la fuente. Si el
   breaker está OPEN esperar el cooldown o hacer prueba manual.
2. **Declared subió**: lanzar un re-harvest manual del conector para recuperar el delta.
3. **Floor mal calibrado**: ajustar `coverage_floor` en `source_health`:
   ```sql
   UPDATE source_health SET coverage_floor = 0.75 WHERE source_key = 'wallapop_wholesale';
   ```
4. **Inconsistencia db_edges vs captured_db**: correr `refresh_global_counts()` y revisar
   vehículos huérfanos (sin `platform_listing`).

### Backfill manual (verify_coverage standalone)

Cuando un conector corrió sin pasar `declared_total` (gap registrado), se puede ejecutar
el gate a posteriori sin re-harvestear:

```python
import asyncio
import asyncpg
from pipeline.ops.coverage_verify import verify_coverage

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

async def backfill(source_key: str, declared_total: int, platform_ulid: str | None = None):
    conn = await asyncpg.connect(DSN)
    try:
        await verify_coverage(
            conn,
            source_key,
            declared_total=declared_total,
            platform_ulid=platform_ulid,
        )
        row = await conn.fetchrow(
            "SELECT * FROM source_coverage WHERE source_key = $1", source_key
        )
        print(dict(row))
    finally:
        await conn.close()

asyncio.run(backfill("wallapop_wholesale", 651_000))
```

### Re-emitir counts globales frescos

El helper `refresh_global_counts()` corrige el bug histórico de `global_count` stale:

```python
import asyncio
import asyncpg
from pipeline.ops.coverage_verify import refresh_global_counts

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

async def main():
    conn = await asyncpg.connect(DSN)
    try:
        counts = await refresh_global_counts(conn)
        print(counts)
    finally:
        await conn.close()

asyncio.run(main())
```

### Umbrales de cobertura por tier

| Tier | `coverage_floor` recomendado | Fuentes |
|------|------------------------------|---------|
| Tier-1 giant | 0.90 | wallapop, milanuncios, coches.net, AS24 |
| Plataforma media | 0.85 (default) | autocasion, faciliteacoches, etc. |
| Long-tail / OEM-VO | 0.80 | dealers individuales, ficheros OEM |

Para actualizar los floors de Tier-1:

```sql
UPDATE source_health
SET coverage_floor = 0.90
WHERE source_key IN (
    'wallapop_wholesale', 'milanuncios_wholesale',
    'coches_net_wholesale', 'as24_wholesale'
);
```

---

## Resilience loop (B3)

Ver `pipeline/ops/health.py` + `migrations/0013_resilience.sql`.

---

## Silence watchdog (B4)

Ver `pipeline/ops/silence_watchdog.py`.

---

## Scheduler de cadencia (B2)

Motor: `pipeline/ops/scheduler.py` (APScheduler `BlockingScheduler`, jobstore SQLAlchemy en PG,
timezone UTC) + `migrations/0021_harvest_cadence.sql`. Es el latido del sistema: lanza harvests DUE,
vigila silencios, re-verifica, y corre los detectores de gestión.

### Arrancar / inspeccionar

```bash
# Arrancar el scheduler (proceso de larga vida — un solo host; ver singleton lock).
python -m pipeline.ops.scheduler

# Dry-run: imprime qué fuentes están DUE y qué comando se lanzaría. NO ejecuta nada. Seguro siempre.
python -m pipeline.ops.scheduler --dry-run
```

**Singleton lock:** al arrancar, `_start_scheduler` toma `pg_try_advisory_lock(0x43415244)`. Si otro
scheduler ya corre en la misma DB, el segundo aborta limpio (evita doble-producción de harvests). Un
solo scheduler por base, siempre.

### Jobs registrados (cadencias + flags)

| Job id | Función | Cadencia (default) | Env override | Coste | Qué hace |
|--------|---------|--------------------|--------------|-------|----------|
| `heartbeat_tick` | `heartbeat_tick` | 15 min (`TICK_INTERVAL_MINUTES`) | — (constante) | harvest | Lanza las fuentes DUE (subprocess por fuente, breaker + timeout). |
| `silence_watchdog` | `silence_watchdog_job` | 1h | — (fijo) | €0 | Marca fuentes que dejaron de reportar (`now()-last > 2×interval`). |
| `inquisition_cadence` | `inquisition_cadence_job` | 6h (`INQUISITION_CADENCE_HOURS`) | — (constante) | €0 | Cola re-verificación de verdicts cuyo TTL de frescura caducó. |
| `inquisition_prosecute` | `inquisition_prosecute_job` | 6h (`INQUISITION_PROSECUTE_CADENCE_HOURS`) | flags¹ | €0 | Adjudica claims PENDING (drena siempre). Emisión de claims NUEVOS = opt-in `CARDEEP_INQUISITION_EMIT=1`, acotada por `INQUISITION_*_BATCH` (200). |
| `gestionador_detect` | `gestionador_detect_job` | 24h (`CARDEEP_GESTIONADOR_CADENCE_HOURS`) | sí | €0 | Detector price_trap (cohort robust-z). QUARANTINE-only, reversible. Ver §Gestionador. |
| `canonical_key_backfill` | `canonical_key_backfill_job` | 24h (`CARDEEP_CANONKEY_CADENCE_HOURS`) | sí | €0 | Rellena `entity.canonical_key` (pre-imagen de auditoría) auto-verificante. Ver §canonical_key. |

¹ La cadencia de `inquisition_prosecute` es constante (6h); lo env-overridable son los flags de
comportamiento: `CARDEEP_INQUISITION_EMIT` (opt-in emisión) y `CARDEEP_INQUISITION_{PROSECUTE,EMIT}_BATCH`.

Todos los jobs son `max_instances=1`, `coalesce=True`, `replace_existing=True` (un cambio de cadencia
toma efecto al reiniciar, sin limpiar el jobstore a mano). Ninguno levanta excepción: un error de DB
se loguea y el job sale para que el scheduler siga. Las cadencias marcadas "constante" se cambian en
código (`pipeline/ops/scheduler.py`), no por entorno.

---

## Gestionador — detector price_trap (audit P2 A-junk/A-zero-tiny)

Motor: `pipeline/gestionador/detect.py` (`detect_price_trap`) + `pipeline/gestionador/run.py` +
`pipeline/gestionador/route.py`. Detecta precios cohort-implausibles y los **pone en cuarentena**
(reversible) — nunca escribe `vehicle.price`, nunca borra.

### Estadístico

Robust-z sobre `ln(price)` por cohorte: `z = (ln price − mediana) / (1.4826·MAD)`. Cohorte =
`(make, model, year)` Tier-A (n≥15) con fallback `(make, year)` Tier-B (model NULL, n≥30). MAD (no
desviación típica): un solo monstruo de 9M€ no infla la escala ni esconde a sus hermanos.

- **HIGH**: `z ≥ +6 AND price ≥ 150.000` (los monstruos >1M€). Floor absoluto = co-guard Law I.
- **LOW**: `z ≤ −6 AND price < 0.25·mediana_cohorte` (depósito/financiación/placeholder).
- **MAD-floor 0.05**: cohortes casi-degeneradas (spread <5%) se SALTAN en ambos lados (Law I — una
  cohorte apretada nunca debe amplificar la desviación pequeña de un coche normal a un z espurio).

Blast-radius validado en DB viva: **347 HIGH / 18.808 LOW = 1,15%** del stock disponible. Muestras
reales: Nissan Qashqai 2024 @ 10.000.000€ (z=57), Mercedes Clase A @ 1€ (z=−120).

### Correr (dry-run review OBLIGATORIO antes de fiarse)

```bash
# Corre el detector + abre/refresca items de cuarentena. Imprime resumen {high, low, items}.
python -m pipeline.gestionador.run
```

> **Gate de despliegue:** el detector SE ENVÍA tras una revisión dry-run de UNA corrida del conjunto
> marcado antes de confiar en él en producción (revisar `gestion_item WHERE detector='price_trap'`).
> El job `gestionador_detect` está cableado pero INERTE hasta que el scheduler se despliegue.

**Rendimiento:** `run.py` sube `work_mem` (`CARDEEP_GESTIONADOR_WORK_MEM`, default 384MB) y fuerza
HASH joins (`enable_mergejoin/nestloop off`) — sin eso el planner elige MERGE (4 sorts de 1,66M filas)
y la pasada dura minutos; con ello corre en **~11s**. Es un job diario DB-only, no está en el hot-path.

### Leer / liberar cuarentenas

```sql
-- Coches en cuarentena por precio, con su evidencia de cohorte
SELECT subject_key AS vehicle_ulid, severity, measured->>'price' AS price,
       measured->>'robust_z' AS z, measured->>'cohort_median' AS median,
       measured->>'make' AS make, measured->>'model' AS model, measured->>'year' AS year
FROM gestion_item
WHERE detector='price_trap' AND quarantines AND closed_at IS NULL
ORDER BY (measured->>'robust_z')::float DESC;

-- Un coche en cuarentena queda OCULTO de servable_vehicle automáticamente (zero write a vehicle.price).
-- Liberar un falso positivo (re-aparece en servable_vehicle al instante):
UPDATE gestion_item SET state='WONT_FIX', closed_at=now(), closed_reason='manual release: legit price'
WHERE detector='price_trap' AND subject_key='<vehicle_ulid>' AND closed_at IS NULL;
```

El cierre a RESOLVED está proof-gated (trigger 0036: exige verdict TRUSTWORTHY con quorum_n≥2). Para
liberar manualmente un falso positivo se usa `WONT_FIX` (no requiere proof, es reversible).

---

## Inquisición — prosecución en cadencia (audit P2 D-inquisition)

Motor: `pipeline/inquisition/prosecutor.py`. El job `inquisition_prosecute` (6h) SIEMPRE drena claims
PENDING (`prosecute_pending`); a €0 → REFUTED honesto `NO_INDEPENDENT_PATH` → ESCALATE_OWNER. La
**emisión de claims nuevos** desde verdicts VAM es OPT-IN:

```bash
# Activar la emisión de claims nuevos (acotada por INQUISITION_EMIT_BATCH=200):
CARDEEP_INQUISITION_EMIT=1 python -m pipeline.ops.scheduler
```

A €0 la emisión masiva inundaría escalaciones que no se pueden auto-resolver — por eso default OFF.
El emisor re-keya verdicts `entity_inventory` a `inventory:<entity_ulid>` (Lens A mide el conteo REAL,
no provincias). Shapes no soportados (coverage/platform_slice) se SALTAN (nunca se fuerzan a 'count').

---

## canonical_key — forward-coverage (audit P2 B-canonical-key)

Motor: `pipeline/identity/canonical_key_backfill.py` + CLI `scripts/backfill_canonical_key.py`.
`entity.canonical_key` es la pre-imagen de AUDITORÍA de `cdp_code` (no es clave de dedup hot-path; esa
es `cdp_code`, el hash UNIQUE puesto en INSERT). Se rellena perezosamente, auto-verificante.

```bash
python scripts/backfill_canonical_key.py            # dry-run (reporte de cobertura, sin escrituras)
python scripts/backfill_canonical_key.py --apply    # rellena
```

Escribe una key SOLO cuando su recálculo re-hashea al `cdp_code` almacenado de la fila (una key
ERRÓNEA es imposible de escribir — el hash es el testigo). MVCC-limpio (solo UPDATE NULL→valor, nunca
reescribe una key puesta). El job `canonical_key_backfill` (24h) lo corre automáticamente al desplegar.
Cobertura actual: 365.573/391.944 (93,3%); el resto son dealers con nombre mutable que no re-matchean
(correctamente NULL).

---

## Migraciones (Flyway-style, una transacción por archivo)

Motor: `scripts/migrate.py`. Más reciente aplicada: **0040** (`servable_vehicle` price>0 guard).

```bash
python scripts/migrate.py status     # qué está aplicado / pendiente
python scripts/migrate.py up          # aplica las pendientes en orden (una transacción cada una)
python scripts/migrate.py verify      # compara checksum aplicado vs archivo en disco (drift)
python scripts/migrate.py repair      # re-sincroniza el ledger si un checksum derivó (sin re-aplicar)
```

Cada archivo lleva su bloque `-- Rollback:` (SQL comentado, byte-fiel) para revertir a mano si hace
falta. `verify` debe dar `N match, 0 drift` antes de cualquier despliegue.
