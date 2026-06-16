# Green-review del núcleo €0 — triage verificado (2026-06-16)

Caza-bugs adversarial (workflow `wymb8ywor`, 6 revisores especialistas) sobre delta /
health / verify / scheduler / evict / inquisition. **21 hallazgos brutos: 5 CRITICAL,
9 HIGH, 6 MEDIUM, 1 LOW.** Cada uno **re-verificado a mano contra código + DB vivos** antes
de actuar — "no confiamos en ningún resultado" aplica también a los agentes. Resultado:
**varios falsos positivos** (sobre todo la falacia "UPDATE de fila mutada = churn MVCC").

Regla MVCC del proyecto = *no UPDATE de filas NO mutadas*. Un `UPDATE` de una fila
**genuinamente mutada** crea UNA versión de tupla sin importar cuántas columnas tenga el
`SET` — eso NO es violación. El churn real es el **no-op** (reescribir una fila a su valor
actual sin guarda `WHERE`).

## CRITICAL (5)

| # | Ubicación | Veredicto | Estado |
|---|---|---|---|
| 1 | `delta.py:321` _BULK_REFRESH "MVCC churn" | **FALSO POSITIVO** — la fila entra en `up_v` solo si `diff_vehicle` detectó cambio (`if not events: continue`); un UPDATE de fila mutada = 1 tupla, escribir columnas iguales NO multiplica tuplas muertas. Docstring "only rows that changed" es correcto. | sin cambio |
| 2 | `evict.py:462` DELETE→cascade vehicle_event | **REAL** — FK `ON DELETE CASCADE` + trigger `immutable` → eviction aborta para cualquier dealer con eventos (1,7 M filas). | ✅ FIJADO `f0deb74` (tombstone a 'gone') + test regresión |
| 3 | `evict.py:421` borrado de archivos pre-txn | **REAL** — archivos perdidos si la txn aborta (pérdida silenciosa). | ✅ FIJADO `f0deb74` (split medir/borrar, borrar post-commit) |
| 4 | `verify.py:60` tolerance no escrita al INSERT | **FALSO POSITIVO** — `drift_ok` exige `top_n>=2` (cluster exacto) → `cdp_modal_cluster(values,0)=top_n>=2` → la CheckViolation es inalcanzable; no escribir tolerance hace el CHECK más estricto, no más laxo. | sin cambio |
| 5 | `_lens_d.py:300` denominator TRUSTWORTHY fabricado | **REAL pero LATENTE + DIFERIDO** — Lens A y D leen `point_est` de la MISMA fila `denominator_estimate` (1 sola fila); independencia estructural, no real. PERO 0 claims `denominator` en vuelo + A2 está data-gated/diferido. | ⏳ PENDIENTE (fix seguro: Lens D abstiene para denominator hasta witness live independiente) |

## HIGH (9) — triage

| # | Ubicación | Veredicto | Estado |
|---|---|---|---|
| H1 | `delta.py:84` `_MARK_GONE` sin guarda `status='available'` → doble GONE event en carrera | **REAL** (idempotencia/carrera; sin UNIQUE en vehicle_event) | ⏳ PENDIENTE (fix: `AND status='available'` + check rowcount antes del INSERT event) |
| H2 | `health.py:253` verify_coverage/reconcile_gone tras commit de la txn | **REAL parcial** (ventana de estado parcial + carrera `prior_last_ok`) | ⏳ PENDIENTE (advisory lock por source_key) |
| H3 | `delta.py:201` reconcile_gone per-row sin txn envolvente | **REAL** (atomicidad: estado parcial en crash) | ⏳ PENDIENTE (envolver el sweep en una txn) |
| H4 | `evict.py:179` Gate3 chequea solo available, DELETE toca todos | **RESUELTO** por el fix #2 (ya no hay DELETE; tombstone con `WHERE status<>'gone'` no cascadea) | ✅ moot |
| H5 | `evict.py:446` UPDATE entity reescribe fila entera | **FALSO POSITIVO** — fila mutada (status) + guarda `WHERE status<>'evicted'`. | sin cambio |
| H6 | `verify.py:185` supersession UPDATE a histórico | **NO-BUG** — filas genuinamente mutadas (`superseded_by` NULL→id), guarda `superseded_by IS NULL`. Transición de estado legítima. | sin cambio |
| H7 | `scheduler.py:435` exit code del subprocess descartado | **REAL** (silent failure: connector que crashea antes de su record_run → sin update de salud, breaker no salta) | ⏳ PENDIENTE (record_run(ok=False) en exit!=0 vía conn aparte) |
| H8 | `_lens_a.py:23` Lens A toma source del producer | **FRAGILIDAD, no bug** — admission excluye correctamente; no fabrica. Zona inquisición diferida. | nota |
| H9 | `prosecutor.py:378` prosecute_pending traga errores de conexión | **REAL** (sigue con conn muerta tras error de conexión → resto falla silencioso) | ⏳ PENDIENTE (re-raise PostgresConnectionStatusError/InterfaceError) |

## MEDIUM (6) — triage

| # | Ubicación | Veredicto | Estado |
|---|---|---|---|
| M1 | `health.py:203` source_breaker reescrito en cada ok=True aunque ya closed | **REAL** (no-op UPDATE de fila no-mutada = churn) | ⏳ PENDIENTE (guarda WHERE en el ON CONFLICT) |
| M2 | `health.py:227` `opened_at=now()` en cada fallo | **REAL** (semántica: debe ser primer-trip; rompe escalado por tiempo) | ⏳ PENDIENTE (`COALESCE(opened_at, now())`) |
| M3 | `evict.py:298` OSError de disk_usage tragado | **RESUELTO** por el fix #3 (ahora loguea en `_measure_raw_files`) | ✅ moot |
| M4 | `verify.py:185` carrera de supersession concurrente | **REAL-menor** (dos writers concurrentes pueden suprimirse mutuamente; baja frecuencia) | ⏳ PENDIENTE (FOR UPDATE / advisory lock por subject) |
| M5 | `scheduler.py:386` TimeoutExpired sin record en DB | **REAL** (mismo origen que H7) | ⏳ PENDIENTE (junto con H7) |
| M6 | `prosecutor.py:292` step7 UPDATE sin guarda status | **MENOR** (dentro de txn, PENDING→PROSECUTING garantizado) | nota |

## LOW (1)

| L1 | `silence_watchdog.py:153` UPDATE alert genera tuplas muertas | **NOTA** — el propio agente admite "fila mutada, no viola la regla". `updated_at` sería una mejora. | nota |

## Resumen de acción

- **FIJADO (1 commit `f0deb74`):** los 2 CRITICAL reales de evict (#2/#3) + folds M3/H4.
- **FALSOS POSITIVOS / NO-BUG (6):** #1, #4, H5, H6, H8, M6, L1 — verificados y dejados intactos (con razón).
- **REAL PENDIENTE (10):** #5(latente), H1, H2, H3, H7, H9, M1, M2, M4, M5 — fix notes arriba.
  Prioridad de continuación: **M1+M2** (health, pequeños, alto valor) → **H1+H3** (reconcile_gone:
  guarda + txn) → **H7+M5** (subprocess silent-failure) → **H9** (prosecute conn) → **H2/M4** (carreras,
  advisory lock) → **#5** (Lens D abstiene; zona diferida).

> Patrón validado: 2 de 5 CRITICAL eran falsos positivos. La verificación a mano fue obligatoria.
