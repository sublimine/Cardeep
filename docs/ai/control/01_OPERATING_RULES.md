# 01 — OPERATING RULES

## 1. Absolute Rules

1. Do not invent.
2. Do not assume without marking ASSUMED.
3. Do not modify production code during audit-only tasks.
4. Do not delete files.
5. Do not rewrite modules wholesale.
6. Do not modify migrations without RFC and approval.
7. Do not modify critical logic without tests.
8. Do not trust README, PLAN, PROGRESO or docs as truth without code evidence.
9. Do not mark tasks DONE without validation.
10. Do not hide failures.

## 2. Critical Modules

The following areas are classified as critical:

- pipeline/ingest.py
- pipeline/delta.py
- pipeline/evict.py
- pipeline/verify.py
- pipeline/verify_ttl.py
- pipeline/identity/
- dedup-related modules
- migrations/
- services/api/
- pipeline/ops/scheduler.py
- pipeline/sources/
- pipeline/platform/
- Docker/deploy configuration
- requirements and dependency files
- production scripts
- API response contracts

Changes to these areas may require RFC depending on scope.

## 3. Default Working Mode

The default mode is AUDIT_ONLY.

No implementation is allowed unless a task explicitly declares:

- TEST_ONLY
- SAFE_PATCH
- MIGRATION_REQUIRED
- RFC_REQUIRED
- PRODUCTION_GATE

## 4. File Modification Rules

Each task must define:

- allowed_files;
- forbidden_files;
- expected_outputs;
- validation commands;
- acceptance criteria.

If allowed_files is missing, default to docs/ai/ only.

If forbidden_files is missing, do not touch:

- pipeline/
- services/
- migrations/
- scripts/
- tests/
- requirements.txt
- docker-compose.yml
- README.md
- PLAN.md
- PROGRESO.md
- RUNBOOK.md

## 5. Evidence Rules

Every finding must contain:

- claim;
- evidence;
- confidence;
- impact;
- recommended next action.

Example:

```markdown
## FINDING-0001

Claim:
pipeline/ingest.py updates vehicle status to gone under certain conditions.

Evidence:
- File: pipeline/ingest.py
- Function: [function name]
- Approx lines: [line range]

Confidence:
VERIFIED_STATIC

Runtime:
NO_VERIFIED_RUNTIME

Impact:
False gone events could corrupt inventory availability.

Next action:
Add targeted tests before changing gone logic.
```

## 6. Test Rules

No code change is acceptable unless one of these is true:

1. an existing relevant test was run and passed;
2. a new relevant test was added and passed;
3. the task is documentation-only;
4. the inability to test is explicitly documented and the task is marked NEEDS_REVIEW.

## 7. Command Reporting Rules

For every command executed, record:

- command;
- working directory;
- result;
- pass/fail;
- relevant output;
- whether it changes files.

## 8. No Silent Scope Expansion

The executor must not expand scope.

If a task says "audit ingest", the executor must not refactor ingest.

If a task says "add tests for delta", the executor must not change delta logic.

If a task says "update docs/ai", the executor must not edit public README.

## 9. Contradiction Handling

If documentation contradicts code:

- record in docs/ai/findings/CONTRADICTIONS.md;
- cite both sides;
- do not resolve silently;
- do not update public docs unless a task explicitly allows it.

## 10. Broken Behavior Handling

If broken behavior is detected:

- record in docs/ai/findings/BROKEN.md;
- create a task proposal;
- do not patch immediately unless the current task allows SAFE_PATCH;
- if critical, mark RFC_REQUIRED.

## 11. Gated Behavior Handling

If something depends on cost, infrastructure, proxies, data, browser automation, external services, database snapshots or credentials, mark GATED.

Do not present gated behavior as complete.

## 12. Completion Rule

A task can only be marked DONE if:

- scope was respected;
- files changed are allowed;
- validation was run or inability documented;
- findings updated;
- evidence recorded;
- no forbidden files were touched;
- acceptance criteria were met.

Otherwise mark:

- BLOCKED;
- NEEDS_REVIEW;
- RFC_REQUIRED;
- PARTIAL.
