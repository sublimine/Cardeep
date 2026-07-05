# LOOP 004 — PRODUCTION READINESS

## Purpose

Move from local/lab behavior toward operational readiness.

## Allowed Task Modes

- PRODUCTION_GATE
- RFC_REQUIRED
- TEST_ONLY for production smoke tests

## Forbidden

- changing deploy configs without RFC approval;
- committing secrets;
- disabling safety controls;
- increasing scraping aggressiveness;
- bypassing source restrictions;
- pretending production readiness without runtime proof.

## Instruction For Claude Code

```text
/loop
Read:
- docs/ai/reports/PRODUCTION_GAP_REPORT.md
- docs/ai/rfcs/RFC_PRODUCTION_ARCHITECTURE.md if it exists
- docs/ai/tasks/TASK_QUEUE.yml
- docs/ai/control/12_HUMAN_APPROVAL_GATES.md

Execute the next READY production-related task.

Rules:
- If config changes are needed, require approved RFC.
- If secrets are involved, stop.
- If infra cost or legal review is needed, mark GATED.
- If runtime cannot be validated locally, mark NO_VERIFIED_RUNTIME.
- Do not modify Docker/deploy files unless allowed by approved task.

At the end:
- update production gap report;
- update risk register;
- update task status;
- report commands and outputs.
```

## Required Production Checks

- Docker config;
- env vars;
- migrations;
- API startup;
- scheduler startup;
- worker model;
- logs;
- metrics;
- alerts;
- backup;
- restore;
- rate limits;
- concurrency;
- cost;
- source health;
- failure recovery.
