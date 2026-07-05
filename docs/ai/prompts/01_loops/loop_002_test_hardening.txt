# LOOP 002 — TEST HARDENING

## Purpose

Add characterization and regression tests before changing critical logic.

## Allowed Task Modes

- TEST_ONLY

## Forbidden

- production code changes;
- migration changes;
- API contract changes;
- dependency changes unless approved;
- changing test expectations to hide broken behavior.

## Instruction For Claude Code

```text
/loop
Read:
- docs/ai/CARDEEP_MASTER_BLUEPRINT.md
- docs/ai/tasks/TASK_QUEUE.yml
- docs/ai/audits/09_TEST_COVERAGE_AUDIT.md
- docs/ai/control/03_DEFINITION_OF_DONE.md

Execute the next READY task with mode TEST_ONLY.

Rules:
- Add or modify tests only.
- Do not modify production logic.
- If production logic appears broken, write a finding and stop.
- Do not patch product code in this loop.
- Run targeted pytest command listed in the task.
- If tests fail because current behavior is broken, mark FAILED_VALIDATION or NEEDS_REVIEW.
- Do not mark DONE unless tests exist and validation result is recorded.

At the end:
- update TASK_QUEUE.yml;
- update findings;
- update evidence ledger;
- report test command output;
- report git diff --name-only.
```

## Priority Test Areas

1. ingest lifecycle;
2. delta/gone;
3. VAM verification;
4. dedup identity;
5. API contract;
6. scheduler locks;
7. source parser fixtures.
