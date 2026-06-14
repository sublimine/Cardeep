# CARDEEP — Runbook operativo

> Estado vivo. Cada sección documenta un mecanismo real, no una aspiración.
> El Director revisa + actualiza tras cada cambio de arquitectura.

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

Ver `pipeline/ops/scheduler.py` + `migrations/0021_harvest_cadence.sql`.
