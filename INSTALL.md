# Cardeep AI Governance Pack — Install Guide

## Qué es este paquete

Este paquete instala una capa institucional de gobierno para desarrollar Cardeep con Claude Code sin improvisación.

Incluye:

- `docs/ai/control/*`: contrato de misión, reglas, estados, risk register, evidence ledger, gates humanos.
- `docs/ai/CARDEEP_MASTER_BLUEPRINT.md`: plano maestro del sistema y fases de ejecución.
- `docs/ai/tasks/TASK_QUEUE.yml`: cola de tareas gobernada.
- `docs/ai/tasks/TASK_TEMPLATE.yml`: plantilla para nuevas tareas.
- `docs/ai/rfcs/RFC_TEMPLATE.md`: plantilla RFC crítica.
- `docs/ai/loops/*`: bucles controlados.
- `docs/ai/prompts/*`: prompts separados por uso para `/goal` y `/loop`.
- `docs/ai/_FULL_PACKAGE_EXPORT.md`: export completo integrado.

## Instalación por ZIP

Desde la raíz del repo Cardeep:

```bash
git checkout -b ai/governance-blueprint
unzip cardeep_ai_governance_pack.zip -d .
git status --short
git diff --stat
git add docs/ai INSTALL.md
git commit -m "docs(ai): add governed development blueprint"
```

## Instalación por patch

```bash
git checkout -b ai/governance-blueprint
git apply cardeep_ai_governance.patch
git status --short
git diff --stat
git add docs/ai INSTALL.md
git commit -m "docs(ai): add governed development blueprint"
```

## Primer comando en Claude Code

Lee `docs/ai/prompts/01_loops/00_loop_master_next_ready_task.txt`.

## Orden real

1. Instalar governance pack.
2. Ejecutar TASK-000.
3. Ejecutar TASK-001 a TASK-015.
4. Revisar `MODULE_SCORECARD.md`.
5. Decidir `CONTINUE / CUT_SCOPE / PIVOT / REBUILD`.
6. Solo después empezar `TEST_ONLY`, `SAFE_PATCH`, `RFC_REQUIRED`, `PRODUCTION_GATE`, `PRODUCT_GATE`.

## Regla operativa

Cardeep no se desarrolla por intuición. Se desarrolla por evidencia, task queue, tests, RFCs y ejecución controlada.
