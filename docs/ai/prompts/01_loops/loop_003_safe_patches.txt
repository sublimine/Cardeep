# LOOP 003 — SAFE PATCHES

## Purpose

Apply small, isolated fixes after audits and tests.

## Allowed Task Modes

- SAFE_PATCH

## Forbidden

- broad refactors;
- schema changes;
- migration changes;
- ingest/delta/dedup/verification behavior changes without RFC;
- API contract changes without RFC;
- production config changes without RFC;
- adding dependencies without approval.

## Instruction For Claude Code

```text
/loop
Read:
- docs/ai/CARDEEP_MASTER_BLUEPRINT.md
- docs/ai/control/08_CHANGE_CONTROL.md
- docs/ai/tasks/TASK_QUEUE.yml
- relevant audit file
- relevant test file

Execute the next READY task with mode SAFE_PATCH.

Rules:
- Patch must be minimal.
- Patch must correspond to a finding.
- Patch must have a test or explicit validation.
- Do not expand scope.
- If fix requires critical behavior change, stop and create RFC instead.
- Run targeted tests.
- Do not mark DONE if tests fail.

At the end:
- update task status;
- update evidence ledger;
- update risk register;
- update findings;
- report before/after behavior;
- report git diff --name-only;
- report test results.
```

## Safe Patch Examples

Allowed:
- typo in non-critical helper;
- parser guard for missing optional field;
- null-safe formatting;
- docs/ai correction;
- test fixture correction.

Not allowed without RFC:
- changing gone logic;
- changing dedup thresholds;
- changing verification states;
- changing DB schema;
- changing API response shape;
- changing scheduler frequency.
