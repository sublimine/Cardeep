# LOOP 001 — STATIC AUDIT

## Purpose

Run static audit tasks one by one.

## Allowed Task Modes

- AUDIT_ONLY
- PRODUCT_GATE
- PRODUCTION_GATE if no config is modified

## Forbidden

- code changes;
- test changes;
- migration changes;
- dependency changes;
- public documentation edits;
- refactors.

## Instruction For Claude Code

```text
/loop
Read:
- docs/ai/CARDEEP_MASTER_BLUEPRINT.md
- docs/ai/control/00_MISSION_CONTRACT.md
- docs/ai/control/01_OPERATING_RULES.md
- docs/ai/control/02_EXECUTION_MODES.md
- docs/ai/control/03_DEFINITION_OF_DONE.md
- docs/ai/tasks/TASK_QUEUE.yml

Execute the next READY task with mode AUDIT_ONLY, PRODUCT_GATE or PRODUCTION_GATE.

Execute one task only.

Do not modify production code.
Do not modify tests.
Do not modify migrations.
Do not modify public README/PLAN/PROGRESO/RUNBOOK.
Update only allowed docs/ai files.

At the end:
- update task status;
- update findings;
- update evidence ledger;
- update risk register;
- report git diff --name-only;
- report commands executed;
- report remaining unknowns.
```

## Exit Criteria

Static audit loop is complete when:

- repo map exists;
- docs-vs-code audit exists;
- migration audit exists;
- ingest audit exists;
- delta/gone audit exists;
- verification audit exists;
- dedup/identity audit exists;
- source matrix exists;
- API audit exists;
- scheduler/ops audit exists;
- test/CI audit exists;
- production audit exists;
- product audit exists.
