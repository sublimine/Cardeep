# Post-Harvest Verification Gate — arquitectura institucional

> Cada vez que un dealer o plataforma da su inventario por COMPLETADO, se dispara —sola,
> sin intervención— una verificación de cobertura por ≥3 vías ortogonales, se sella un
> verdict auditable, y si la cobertura cae salta una alerta con origen exacto que se
> auto-repara. Es el cierre del lazo descubrir→scrapear→**verificar cobertura**→servir.

## 1. Invariante (no negociable)
Ningún harvest está "completo" hasta que su cobertura está MEDIDA contra lo que la fuente
DECLARA y SELLADA en un verdict. "Lo conté en la DB y dio X" no es verificación: es un solo
camino. Verificación = capturado vs **declarado-por-la-fuente** vs DB-edges vs coherencia,
convergiendo. Si divergen → REFUTED → alerta. (Doctrina VAM, elevada al agregado por-fuente.)

## 2. El seam [VERIFICADO en código]
`pipeline/ops/health.py::record_run(conn, source_key, *, ok, rows, error, http_status, ...)`
es la ÚNICA función que TODOS los conectores llaman al terminar su harvest (verificado:
wallapop L1394, milanuncios, coches_net, AS24, generic_dealer_site, scale_as24…). Por tanto
es el punto de enganche universal: automatizar aquí cubre toda la flota sin tocar 80 conectores.

Hoy `record_run` recibe `rows` (capturado) pero NO `declared_total` — el declarado vive en
`stats['declared_full']` y se imprime como telemetría, nunca se verifica (comentario L1347
"honesty, not a quorum path"). ESTA es la pieza que falta.

## 3. Componentes

### 3.1 Contrato extendido de `record_run`
Añadir kwargs opcionales (backward-compatible, COALESCE — un conector que no los pase no rompe):
```
record_run(conn, source_key, *, ok, rows, error, http_status,
           declared_total: int | None = None,     # lo que la fuente DICE tener
           captured_distinct: int | None = None,  # lo que harvesteamos (distinct)
           phase: str = 'scrape')
```
Al terminar con ok=True y declared_total presente → invoca `verify_coverage(...)` (3.2).

### 3.2 `pipeline/ops/coverage_verify.py::verify_coverage`
Verificación de cobertura por-fuente, ≥3 vías ORTOGONALES:
- **vía A — declared_total**: contador de la PROPIA fuente (externo a nuestra pipeline).
- **vía B — captured_db**: `count(vehicle WHERE status='available')` de esa fuente (nuestra DB).
- **vía C — db_edges**: `count(platform_listing)` de esa plataforma (estructura referencial).
- (vía D opcional — db_join_vehicles: join edge↔vehicle, coherencia.)
Calcula `coverage_pct = captured_db / declared_total`. Emite `record_count_verdict(
subject_type='source_coverage', subject_key=source_key, claim='captured == declared',
paths={declared_total, captured_db, db_edges}, tolerance=COVERAGE_TOLERANCE)`.

### 3.3 Tabla `source_coverage` (migración numerada)
`source_coverage(source_key PK, declared_total, captured_db, db_edges, coverage_pct,
verdict, verdict_id FK, probed_at)`. UPSERT idempotente en cada harvest → estado de cobertura
SIEMPRE fresco y auditable de un vistazo (`SELECT * FROM source_coverage`). Mata el hueco actual
(el verdict global quedaba stale tras re-scrapes; aquí se refresca en cada harvest por construcción).

### 3.4 Lazo de alerta + auto-reparación (reusa B3)
- coverage_pct ≥ umbral SELLADO → `resolve_alerts(origin)` (cierra alertas previas de cobertura).
- coverage_pct < umbral (p.ej. <0,85) → `fire_alert(build_origin(source_key,'coverage'),
  severity, payload={declared, captured, pct})` + `auto_repair(source_key, 'low_coverage')`.
  Origen EXACTO máquina-legible (`source_key:coverage`), nunca prosa.
- Umbrales por tier: Tier-1 plataformas grandes exigen ≥0,90; long-tail ≥0,80 (configurable
  en `source_health.coverage_floor`).

### 3.5 Re-emisión del agregado global
`global_count` verdict (vehicle_total, platform_listing_total) se re-emite en el mismo gate
o en el watchdog, para que NUNCA quede stale (el bug que el Director encontró: decía 1.332.980
con 1.689.243 reales).

## 4. Flujo end-to-end (automático)
```
conector.harvest()  →  record_run(ok=True, declared_total, captured_distinct)
                              │
                              ├─ persiste run en source_health
                              └─ verify_coverage():
                                     declared vs captured vs db_edges  (VAM ≥3 vías)
                                     → record_count_verdict(source_coverage)
                                     → UPSERT source_coverage (auditable)
                                     → cobertura<floor ? fire_alert+auto_repair : resolve_alerts
```
Cero intervención. Cada dealer/plataforma que cierra inventario sella su cobertura sola.

## 5. Integración con lo existente
- **B3** (fire_alert/resolve_alerts/auto_repair): reusados, sin duplicar.
- **B8** (probe de declarado standalone): se absorbe como el modo MANUAL/backfill del mismo
  `verify_coverage` (un harvest que no pasó declared puede probarse a posteriori).
- **VAM** (record_count_verdict, verification_verdict): el verdict de cobertura es un subject_type
  más, con la misma maquinaria de quórum y tolerancia.

## 6. Calidad / garantías
- Backward-compatible: conectores que no pasen declared siguen funcionando (sin verdict de cobertura
  hasta que se actualicen — gap registrado, no romper).
- Idempotente: UPSERT por source_key; re-ejecutable; sobrevive reinicio.
- €0: el declared lo calcula el conector en su probe (ya existe), no añade requests.
- Auditable: `source_coverage` responde "¿cuánto de wallapop tenemos?" en una query, por ≥2 vías.

## 7. Runbook (sello operativo) — va a docs/RUNBOOK.md
Sección "Verificación de cobertura": qué dispara el gate, cómo leer `source_coverage`, qué
significa cada verdict, qué hacer ante una alerta `*:coverage` (diagnóstico: declared subió /
captura cayó / ban a media paginación), y el comando de backfill manual.
