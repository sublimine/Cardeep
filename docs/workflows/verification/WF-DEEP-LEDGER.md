# WF-DEEP-LEDGER — Quórum DB-Enforced + Audit Hash-Chain (L2)

## Objetivo

Garantizar mediante constraints de base de datos y una cadena de hash
append-only que ningún verdict TRUSTWORTHY sea escrito sin quórum demostrable, y
que el historial de verdicts sea inmutable y auditable.

---

## Disparador

- **DB constraint continuo**: `chk_trustworthy_needs_quorum` se evalúa en cada
  INSERT y UPDATE sobre `verification_verdict`. No requiere invocación explícita.
- **δ TTL cadencia**: `python -m pipeline.ops.inquisition_schedule` busca
  veredictos con `expires_at < now() AND superseded_by IS NULL` y los
  relanza como claims PENDING en Inquisition L4.

---

## Entradas

| Fuente | Descripción |
|--------|-------------|
| `verification_verdict` | Tabla escrita por VAM L1; L2 la protege mediante constraints |
| `verdict_audit` | Tabla append-only; cada fila referencia el hash de la anterior |
| Denominador Chapman/Chao2 | Estimación estadística de N real (dealers/vehículos) para calcular coverage% |

---

## Pasos átomo

### 1. DB constraint `chk_trustworthy_needs_quorum`

```sql
CHECK (
    verdict != 'TRUSTWORTHY'
    OR (quorum_n >= 2 AND family_n >= 2 AND origin_n >= 2)
)
```

Este constraint se evalúa por el motor de PG en cada INSERT/UPDATE. Si un
producer intenta escribir un verdict TRUSTWORTHY sin satisfacer los tres
umbrales, la transacción aborta con `IntegrityError` antes de que el dato
persista.

### 2. Audit hash-chain (append-only) — tabla real `verdict_audit`

El trigger `cdp_audit_append` (AFTER INSERT en `verification_verdict`) anexa una fila a
`verdict_audit` — **NO hay INSERT manual**:

```
payload_hash = sha256(subject_type|subject_key|claim|verdict|primary_value
                      |verifier_paths|independent_values|quorum_n|family_n)
chain_hash   = sha256(COALESCE(prev_chain_hash,'GENESIS') || '|' || payload_hash)
```

Columnas: `seq, verdict_id, subject_type, subject_key, claim, verdict, quorum_n, family_n,
payload_hash, prev_hash, chain_hash, created_at`. El trigger `cdp_audit_immutable`
(BEFORE UPDATE OR DELETE) **prohíbe** toda mutación → la cadena es físicamente append-only.
El hash NO cubre `expires_at`/`superseded_by` (por eso la cadencia δ puede setearlos sin
romper la cadena). Una cadena rota (chain_hash que no encadena) es detectable por scan lineal.

### 3. Denominador Chapman/Chao2

El denominador estima N real de la población (dealers o vehículos) a partir de
capturas en múltiples fuentes independientes. Se usa para calcular coverage%
real vs. capturado. El cálculo reside en la capa estadística del pipeline y
escribe su resultado en la tabla de estadísticas de cobertura.

### 4. δ TTL cadencia (`inquisition_schedule.py`)

```python
# Busca verdicts expirados
SELECT * FROM verification_verdict
WHERE expires_at < now()
  AND superseded_by IS NULL
-- usa idx_verdict_expiry (partial index sobre expires_at IS NOT NULL)

# Por cada expirado:
open_or_refresh(conn, lane='RESEARCH', ...)
# → gestion_item RESEARCH → prosecute_pending en siguiente ventana
```

---

## Gate de verificación

| Gate | Mecanismo | Fallo |
|------|-----------|-------|
| Quórum mínimo | `chk_trustworthy_needs_quorum` (PG constraint) | `IntegrityError` → rollback |
| Integridad hash | Cadena SHA-256 verificable secuencialmente | Alert crítico + escalate_owner |
| Rol restringido | `cardeep_inquisitor`: solo `SELECT` en `verification_verdict` | Permiso denegado en PG |

El rol `cardeep_inquisitor` no puede escribir verdicts, por diseño. Solo los
módulos con credenciales del role productor pueden insertar o actualizar.

---

## Artefactos

| Artefacto | Descripción |
|-----------|-------------|
| `verification_verdict` | Quórum enforced en cada fila por constraint PG |
| `verdict_audit` | Tabla append-only; cada fila encadena SHA-256 con la anterior |
| Estadísticas de cobertura | Denominador Chapman/Chao2 escrito en tabla de coverage |

---

## Fallo → routing

| Fallo | Consecuencia |
|-------|-------------|
| Constraint violation | `psycopg2.IntegrityError` → rollback → log con `subject_key` y `claim_kind` → `fire_alert()` con origen exacto |
| Hash chain broken | Alert crítico → `escalate_owner` via `gestion_item` |
| δ TTL job exception | Log + `fire_alert(source_key:inquisition_schedule)` + continue (no bloquea el tick) |

---

## Idempotencia

- `verdict_audit`: append-only, no se modifica nunca. Re-ejecutar el mismo claim
  produce una nueva fila de cadena, no sobrescribe.
- `inquisition_schedule.py`: `open_or_refresh()` es idempotente por
  `dedupe_key UNIQUE`. Si el `gestion_item` RESEARCH ya existe, refresca el
  timestamp sin crear duplicado.

---

## Estado

IMPLEMENTADO — migration `0026`, tabla `verdict_audit`, constraint
`chk_trustworthy_needs_quorum`, `pipeline/ops/inquisition_schedule.py`,
índice `idx_verdict_expiry`.

---

## €0 vs gasto

€0 total — DB constraints evaluados por PG, SHA-256 computado en DB o en
Python puro, `inquisition_schedule.py` hace solo DB reads + upserts. Sin HTTP,
sin LLM, sin proxies.
