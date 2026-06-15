# Verificación — Arquitectura de 4 Capas

No confiamos en ningún resultado. Cada claim que el pipeline produce pasa por
capas independientes antes de recibir el sello TRUSTWORTHY. Ninguna capa sola
es suficiente; la confianza emerge del acuerdo ortogonal entre ellas.

---

## Las 4 capas

| Capa | Nombre | Migración | Módulo | Trigger | Fuerza | Estado |
|------|--------|-----------|--------|---------|--------|--------|
| L1 | VAM (Veredicto de Conteo por Quórum) | 0004 | `pipeline/verify.py` | Post-ingest / post-discover | Count quorum optimista: modal ≥2 paths sin rival | IMPLEMENTADO |
| L2 | Deep Ledger | 0026 | DB constraints + `pipeline/ops/inquisition_schedule.py` | DB-enforced continuo + δ TTL cadencia | Hash-chain SHA-256 + quórum DB constraint | IMPLEMENTADO |
| L3 | Gestionador | 0031 | `pipeline/gestionador/detect.py` + `route.py` | Post-ingest + post-Inquisition | 7 detectores activos + máquina de estados | IMPLEMENTADO |
| L4 | Inquisition | 0032 | `pipeline/inquisition/` | Bridge desde L1 + cadencia δ + CLI | 5 lenses ortogonales, DB invariant, 139 tests | IMPLEMENTADO |

---

## Flujo de una claim

```
producer (ingest.py / discover.py / coverage_verify.py)
    |
    v
[L1 VAM] pipeline/verify.py
    record_count_verdict()
    ├── paths independientes → valor modal
    ├── quorum: modal ≥ 2 paths, sin rival ≥ 2
    └── verdict: TRUSTWORTHY | REFUTED | UNVERIFIED | QUARANTINED
         (los valores válidos en `verification_verdict_verdict_check`; no existe UNTRUSTWORTHY ni INCONCLUSIVE en esta tabla)
         |
         | INSERT verification_verdict
         v
[L2 Deep Ledger] DB constraints
    ├── chk_trustworthy_needs_quorum: quorum_n≥2, family_n≥2, origin_n≥2
    ├── verdict_audit: SHA-256 append-only (prev_hash || payload) — trigger trg_verdict_audit_append (AFTER INSERT on verification_verdict)
    ├── denominador Chapman/Chao2 (N real de dealers/vehículos)
    └── δ TTL: inquisition_schedule.py → re-emite claims expirados
         |
         | emit_claim_from_verdict() (bridge)
         v
[L4 Inquisition] pipeline/inquisition/prosecutor.py
    ├── Dispatch a lenses: A_requery / B_raw_recount / C_live_refetch* / D_cross_source / E_batch_hash
    ├── admit(): D(skeptic.state, producer) ≥ 2 (independencia)
    ├── within_tolerance(): EXACT o DRIFT (TAU_REL=0.005, TAU_ABS=50)
    ├── false-veto guard §5.5
    └── router.py: 13 reglas → lane (AUTO_FIX / QUARANTINE / RESEARCH / ESCALATE_GASTO / ESCALATE_OWNER)
         |
         | gestion_item INSERT
         v
[L3 Gestionador] pipeline/gestionador/
    ├── detect.py: 7 detectores activos (count_inflation, silent_cap, field_loss,
    │             staleness, fabrication, coverage_gap, price_trap)
    ├── route.py: open_or_refresh() MVCC-safe → estado OPEN → ROUTED → ...
    └── SLA por lane: AUTO_FIX=6h, RESEARCH=7d, QUARANTINE=48h
         |
         v
    verdict final en DB
    (inquisition_verdict + gestion_item + alert si aplica)
```

*Lens C = HARVEST-GATED: stub presente, no activo sin gasto HTTP.

---

## Independencia como invariante

El invariante de DB `trustworthy_needs_independence` codifica la regla
fundamental: un verdict TRUSTWORTHY no puede descansar en una sola fuente ni en
fuentes que comparten el mismo estado de origen.

- `independence.py::admit(skeptic, producer)` requiere `D(skeptic.state, producer) ≥ 2`
  antes de que un lens pueda votar sobre un claim.
- `independence.py::indep_score(asserting_skeptics, producer)` calcula el
  mínimo de pares ortogonales entre todos los skeptics que afirman.
- El constraint DB rechaza en INSERT cualquier verdict TRUSTWORTHY que no
  satisfaga este criterio, incluso si el código no lo verificó correctamente.

La independencia no es solo una regla de software: está grabada en el schema.

---

## €0 por diseño

Las capas L1, L2 y L3 son completamente €0: operan exclusivamente sobre DB
reads, DB writes, hash computation y Python determinista. L4 Inquisition también
es €0 en sus lenses A, B, D y E.

La única excepción es **Lens C** (`C_live_refetch`): re-fetch HTTP en vivo del
dealer. Lens C está implementada como stub en `lenses.py` y está marcada
HARVEST-GATED. No se activa sin un ciclo de harvest explícito autorizado.
Cuando es determinante para un veredicto, Inquisition abre un `gestion_item`
con lane RESEARCH para que la decisión quede registrada y sea auditada.

El scheduler (`pipeline/ops/scheduler.py`) ejecuta la lógica de cadencia €0
siempre; el scraping real que se dispara desde el heartbeat es lo que lleva
gasto de proxies.

---

## Documentos de referencia por capa

- [WF-VAM.md](WF-VAM.md) — L1: Veredicto de Conteo por Quórum
- [WF-DEEP-LEDGER.md](WF-DEEP-LEDGER.md) — L2: Quórum DB-Enforced + Audit Hash-Chain
- [WF-INQUISITION.md](WF-INQUISITION.md) — L4: 5 Lenses + Quórum Adversarial
- [WF-GESTIONADOR.md](WF-GESTIONADOR.md) — L3: Detección + Máquina de Estados
- [WF-CADENCE.md](WF-CADENCE.md) — Jobs de Cadencia: Heartbeat, Silencio, δ TTL
- [../AGENT-SKILL-TOOL-MATRIX.md](../AGENT-SKILL-TOOL-MATRIX.md) — Matriz de agentes, skills y herramientas por caso de uso
