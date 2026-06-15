# WF-INQUISITION — V3 Inquisition: 5 Lenses + Quórum (L4)

## Objetivo

Someter cada claim a escrutinio adversarial mediante lenses ortogonales
independientes, rechazando o confirmando el veredicto del producer mediante
quórum de skeptics, con routing determinista del resultado a la lane correcta.

---

## Disparador

- **Bridge desde VAM**: `emit_claim_from_verdict()` en
  `pipeline/inquisition/prosecutor.py` convierte un `verification_verdict` de L1
  (TRUSTWORTHY se re-prosecuta; REFUTED/UNVERIFIED se elevan) en un `inquisition_claim` PENDING.
- **Cadencia δ**: `inquisition_schedule.py` re-emite veredictos expirados como
  claims PENDING; `prosecute_pending()` los recoge en la siguiente ventana.
- **CLI manual**: `python -m pipeline.inquisition.prosecutor`

---

## Entradas

`ClaimEnvelope(frozen=True)` (`pipeline/inquisition/lenses.py`) — encapsula un claim leído de `inquisition_claim`:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `claim_id` | `str` | ULID del `inquisition_claim` |
| `subject_type` | `str` | uno de `count\|entity_field\|inventory\|coverage\|kind\|delta\|denominator` (CHECK 0032) — determina régimen y lenses §3.6 |
| `subject_key` | `str` | clave del sujeto (`province:28`, `kind:desguace`, `inventory:<cdp>`, …) |
| `asserted_value` | `str` | valor afirmado, string entero canónico (`"12345"`, nunca `"12345.0"`) |
| `producer_state` | `StateTuple` | ⟨source,tool,cache,path⟩ del producer (Law II — gate de independencia) |
| `tolerance` | `float` | tolerancia relativa (default 0.005) |
| `evidence_uri` | `str \| None` | URI a evidencia cruda (Lens B) / `hash:<hex>` (Lens E) |

---

## Pasos átomo (por claim)

### 1. `prosecute_claim(conn, claim_row) -> dict`

Atómico en `conn.transaction()`. Si falla cualquier paso intermedio, rollback
completo y el claim queda en estado `PENDING`.

### 2. Dispatch a lenses según `claim_kind`

| Lens | Identificador | Claim kinds | Regime | Confianza | Estado |
|------|--------------|-------------|--------|-----------|--------|
| A | `A_requery` | count / inventory / coverage / kind / denominator | DRIFT para count/inventory; EXACT para el resto | 0.90 | ACTIVO |
| B | `B_raw_recount` | count / inventory | DRIFT | 0.95 | ACTIVO |
| C | `C_live_refetch` | count / inventory | DRIFT | N/A | HARVEST-GATED (stub) |
| D | `D_cross_source` | count / coverage / kind / denominator | EXACT para kind/coverage/denominator; DRIFT para count | 0.80 | ACTIVO |
| E | `E_batch_hash` | inventory / delta | EXACT | 1.00 | ACTIVO |

Mapping de regime (`pipeline/inquisition/models.py`):
- `Regime.EXACT`: kind / coverage / denominator
- `Regime.DRIFT`: count / inventory

### 3. Gate de independencia por skeptic

Para cada lens que produce un veredicto (`SkepticVerdict`):

```python
# independence.py
admit(skeptic, producer)  # -> bool
# Condición: D(skeptic.state, producer) >= 2
# Si falla: el skeptic no puede votar sobre este claim
```

```python
indep_score(asserting_skeptics, producer)  # -> int
# Mínimo de pares ortogonales entre todos los skeptics que afirman ASSERT
# Lectura estricta: todos los asserting skeptics deben ser independientes
```

### 4. Evaluación de tolerancia (`quorum.py`)

```python
within_tolerance(measured, asserted, regime)  # -> bool
```

- **EXACT**: `measured == asserted` (sin margen)
- **DRIFT**: `|measured - asserted| <= max(TAU_REL * asserted, TAU_ABS)`
  donde `TAU_REL = 0.005` y `TAU_ABS = 50.0`

`SkepticVerdict` posibles: `ASSERT | REFUTE_SOFT | REFUTE_HARD | ABSTAIN`

### 5. False-veto guard §5.5

Antes de §5.4: un `REFUTE_HARD` solo VETA si (a) lo reproduce un 2º skeptic independiente
(D≥2 del primero) **O** (b) es byte-determinista (`deterministic=True`: cap header, checksum,
empty-delta). Un `REFUTE_HARD` solitario no-determinista NO veta — degrada a INCONCLUSIVE y
re-encola (la Inquisición desconfía de sus propios inquisidores: un refute caro debe ser
reproducible para matar un claim posiblemente verdadero). Aparte: un `ABSTAIN` cuenta como
refute para el quórum (Ley I) pero se registra por separado para routing; la ausencia de
Lens C (ABSTAIN) no veta, aunque sin C el INDEP suele quedar <2.

### 6. Routing (`router.py`) — 13 reglas

Prioridad de match: exact match → prefix match → catch-all.

| Patrón | Lane | Acción |
|--------|------|--------|
| `silent_cap` | AUTO_FIX | Corrección automática en 6h |
| `fabrication` | QUARANTINE | Aislamiento en 48h |
| `empty_delta` | QUARANTINE | Aislamiento en 48h |
| `coverage` | RESEARCH | Investigación en 7d |
| `NO_INDEPENDENT_PATH` | ESCALATE_OWNER | Sin SLA; requiere decisión manual |
| (catch-all) | RESEARCH | Investigación en 7d |

El `_RouteRow` es un `dataclass(frozen=True)`: inmutable una vez construido.

### 7. Emisión de artefactos

```python
# INSERT inquisition_verdict
# INSERT gestion_item (si router dispara lane)
# UPDATE verification_verdict SET superseded_by = nuevo_verdict_id
```

---

## Gate de verificación

| Gate | Mecanismo |
|------|-----------|
| `trustworthy_needs_independence` | DB invariant (0032): un verdict TRUSTWORTHY exige `indep_score >= 2 AND assert_n >= 2 AND refute_hard_n = 0` — imposible persistir una mentira de-confianza aun con prosecutor con bug |
| Quórum de skeptics | ≥2 asserting skeptics mutuamente independientes (INDEP≥2) para TRUSTWORTHY |
| False-veto guard §5.5 | Activo en `quorum.py` antes de la evaluación de quórum |
| Transaccionalidad | `prosecute_claim` atómico: todo o nada |

---

## Artefactos

| Artefacto | Tabla | Descripción |
|-----------|-------|-------------|
| Veredicto adversarial | `inquisition_verdict` | Una fila por claim juzgado |
| Item de gestión | `gestion_item` | Abierto si el router dispara una lane |
| Supersedido | `verification_verdict.superseded_by` | FK al nuevo verdict si reemplaza uno anterior |

---

## Fallo → routing

| Fallo | Consecuencia |
|-------|-------------|
| `prosecute_claim` exception | Rollback completo; claim queda en `PENDING` |
| Lens C ausente (HARVEST-GATED) | Inquisition opera con A/B/D/E; si C sería determinante, abre `gestion_item` lane `RESEARCH` |
| `admit()` rechaza todos los skeptics | `NO_INDEPENDENT_PATH` → `ESCALATE_OWNER` |

---

## Idempotencia

- `prosecute_pending(conn, *, limit, actor)` procesa solo claims en estado
  `PENDING`; marca `PROCESSING` al inicio de cada claim.
- Si falla, rollback restaura `PENDING`. No produce duplicados.
- `open_or_refresh()` en `route.py` es idempotente por `dedupe_key UNIQUE`.

---

## Estado

IMPLEMENTADO — `pipeline/inquisition/` (prosecutor.py, router.py, lenses.py,
quorum.py, independence.py, models.py, _lens_a.py, _lens_d.py). 139 tests
pasan. Lens C = HARVEST-GATED (stub en `lenses.py`).

---

## €0 vs gasto

| Componente | Coste |
|-----------|-------|
| Lenses A, B, D, E | €0 — DB queries y Python determinista |
| Router, quorum, independence | €0 |
| Lens C (`C_live_refetch`) | HARVEST-GATED — re-fetch HTTP en vivo |
