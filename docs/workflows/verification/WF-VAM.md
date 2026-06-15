# WF-VAM — Veredicto de Conteo por Quórum (L1)

## Objetivo

Producir un veredicto de confianza (`TRUSTWORTHY` / `REFUTED` / `UNVERIFIED`; `QUARANTINED`
disponible en el CHECK) para cada conteo observable en el pipeline, mediante acuerdo modal
entre paths independientes, sin coste externo.

---

## Disparador

Llamado por `ingest.py`, `discover.py` y `coverage_verify.py` al final de cada
operación que produce un conteo verificable. No es un job de cadencia: se invoca
síncronamente como cierre de cada operación productora.

---

## Entradas

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `subject_type` | `str` | Qué tipo de entidad se verifica. Ejemplos usados en prod: `"source"`, `"entity_inventory"`. No hay CHECK constraint en `verification_verdict.subject_type` — es texto libre. |
| `subject_key` | `str` | `cdp_code` del dealer o `source_key` de la fuente |
| `claim` | `str` | Descripcion textual del claim (p.ej. `"entity count == declared count"`) |
| `paths` | `dict[str, int]` | `{path_name: count}` — rutas independientes con sus conteos. Firma real en `pipeline/verify.py` |
| `tolerance` | `float` | Tolerancia relativa (default 0.0 para count puro) |
| `claim_kind` | `str` | Uno de: `'count'`, `'field_fill'`, `'existence'`, `'freshness'`, `'coverage'`, `'denominator'` (según `verification_verdict_claim_kind_check`) |
| `expires_in` | `timedelta \| None` | TTL explícito; `timedelta(0)` produce `expires_at=NULL` (sello eterno); `None` usa `ttl_for(claim_kind)` |

---

## Pasos átomo

1. Invocar `await record_count_verdict(conn, *, subject_type, subject_key, claim: str, paths: dict[str, int], tolerance=0.0, claim_kind="count", expires_in: timedelta | None = None) -> str`
2. Calcular el valor modal de `paths`: todos los paths deben reportar el mismo
   número para que cuenten como acuerdo.
3. Comprobar quórum:
   - Contar cuántos paths coinciden con el valor modal (`modal_count`).
   - Comprobar que ningún valor rival tiene también ≥2 paths.
4. Asignar verdict según las reglas de gate (ver sección siguiente).
5. Calcular TTL: `expires_at = now() + ttl_for(claim_kind)` (server-side, vía `$N::interval`).
   Los claims grandfathered (B1, β, B7) se insertan con `expires_at = NULL` (eterno).
6. Ejecutar un `INSERT INTO verification_verdict (...)` **simple** (append-only; `verification_verdict` NO tiene `dedupe_key` ni UPSERT — cada llamada inserta una fila nueva; un verdict posterior supersede al previo vía `superseded_by`).

---

## Gate de verificación

| Verdict | Condición |
|---------|-----------|
| `TRUSTWORTHY` | `modal_count ≥ 2` y ningún rival tiene ≥ 2 paths, Y el path primario concuerda con al menos otro path |
| `REFUTED` | Existe un valor rival con ≥ 2 paths, O divergencia > tolerance |
| `UNVERIFIED` | Menos de 2 paths disponibles (no se puede calcular quorum) |

Nota: los valores `UNTRUSTWORTHY` e `INCONCLUSIVE` NO existen en `verification_verdict`. El CHECK constraint admite exactamente: `TRUSTWORTHY`, `REFUTED`, `UNVERIFIED`, `QUARANTINED`.

---

## TTL por claim_kind

El TTL no está codificado en esta tabla: se calcula con `ttl_for(claim_kind)` en
`pipeline/verify_ttl.py`. Los valores actuales son referencia; la fuente
canónica es ese módulo.

---

## Artefactos

- Fila en `verification_verdict` con campos:
  `subject_type, subject_key, verdict, claim, paths, claim_kind, expires_at, dedupe_key`

---

## Fallo → routing

- `REFUTED`: no bloquea el ingest. El pipeline registra el verdict y
  continúa. El bridge `emit_claim_from_verdict()` en
  `pipeline/inquisition/prosecutor.py` eleva el claim a Inquisition L4 para
  análisis adversarial.
- `UNVERIFIED`: se registra pero no dispara Inquisition automáticamente.
  La cadencia δ TTL de L2 lo relanzará cuando expire.
- Corrección: los nombres `UNTRUSTWORTHY` e `INCONCLUSIVE` no existen — son
  errores de documentación previos. Los valores reales son `REFUTED` y `UNVERIFIED`.
- Excepción en DB: rollback, log de error con `subject_key` y `claim_kind`,
  no re-intento automático en este ciclo.

---

## Idempotencia

`record_count_verdict` siempre hace INSERT simple (no ON CONFLICT) — la tabla
`verification_verdict` no tiene columna `dedupe_key` ni constraint única sobre ella.
La idempotencia funcional se gestiona via TTL: cuando un verdict expira, la cadencia
δ abre un `gestion_item` para re-verificación en lugar de actualizar el verdict previo.
Nota: `gestion_item` SÍ tiene `dedupe_key UNIQUE` — es el mecanismo de dedup del Gestionador,
no de `verification_verdict`.

---

## Estado

IMPLEMENTADO — `pipeline/verify.py`

---

## €0 vs gasto

€0 total. Operación puramente en DB: lectura de paths, cómputo modal en Python,
INSERT/UPDATE en PostgreSQL. Sin HTTP, sin LLM, sin proxies.
