# 02 — EXECUTION MODES

## 1. Purpose

Execution modes define what the AI executor is allowed to do during a task.

Every task must declare exactly one mode.

## 2. Mode: AUDIT_ONLY

### Purpose

Read, inspect, map and document.

### Allowed

- read files;
- inspect structure;
- create docs/ai/audits/*;
- create docs/ai/findings/*;
- create evidence entries;
- create risk entries;
- propose tasks.

### Forbidden

- modifying production code;
- modifying tests;
- modifying migrations;
- modifying dependencies;
- changing behavior;
- deleting files.

### Required Output

- audit document;
- findings;
- unknowns;
- risks;
- recommended next tasks.

## 3. Mode: TEST_ONLY

### Purpose

Add or improve tests without modifying production logic.

### Allowed

- create tests;
- modify tests;
- add fixtures;
- add test documentation;
- run test commands.

### Forbidden

- modifying production logic;
- modifying migrations;
- changing public API behavior;
- changing dependency files unless explicitly approved.

### Required Output

- tests added/modified;
- command results;
- coverage of targeted behavior;
- failures documented.

## 4. Mode: SAFE_PATCH

### Purpose

Make a small low-risk code change with direct validation.

### Allowed

- small targeted bug fix;
- small typing fix;
- small parsing fix;
- small guard condition;
- small documentation correction tied to code.

### Forbidden

- broad refactors;
- schema changes;
- API contract changes;
- ingest/delta/dedup/verify behavior changes without explicit task approval;
- dependency changes;
- production deployment changes.

### Required Output

- explanation of change;
- tests;
- validation command;
- before/after behavior;
- rollback note.

## 5. Mode: RFC_REQUIRED

### Purpose

Handle risky changes by writing a proposal first.

### Required For

- ingest behavior changes;
- gone guard changes;
- delta lifecycle changes;
- dedup/identity changes;
- verification/VAM changes;
- database schema changes;
- API contract changes;
- scheduler/job orchestration changes;
- scraping Tier-1 changes;
- production/deploy changes;
- security/auth changes;
- dependency changes with operational impact.

### Allowed

- create RFC document;
- inspect code;
- inspect tests;
- inspect migrations;
- propose alternatives.

### Forbidden

- implementing the change before approval.

### Required Output

- RFC;
- risk analysis;
- test plan;
- rollback plan;
- human decision needed.

## 6. Mode: MIGRATION_REQUIRED

### Purpose

Govern database schema changes.

### Required For

- creating table;
- altering table;
- dropping table;
- adding/removing column;
- modifying index;
- modifying constraints;
- modifying views/materialized views;
- changing enum/state model.

### Allowed

Only after approved RFC:

- add migration;
- add rollback instructions if system supports them;
- add tests;
- update schema documentation.

### Forbidden

- destructive migration without explicit approval;
- silent schema drift;
- modifying existing applied migrations unless explicitly instructed and safe for local-only history.

### Required Output

- migration file;
- schema impact;
- data migration impact;
- rollback plan;
- validation command.

## 7. Mode: PRODUCTION_GATE

### Purpose

Assess or change production readiness.

### Covers

- Docker;
- deployment;
- workers;
- scheduler;
- logs;
- metrics;
- alerts;
- secrets;
- backups;
- rate limits;
- scaling;
- cost;
- infrastructure.

### Allowed

- audit production configs;
- create production gap report;
- propose architecture;
- add non-invasive docs;
- create safe config examples if allowed.

### Forbidden

- changing deployment behavior without approval;
- committing real secrets;
- disabling safety checks;
- weakening rate limits;
- bypassing robots/legal constraints.

## 8. Mode: PRODUCT_GATE

### Purpose

Assess commercial/product readiness.

### Covers

- API value;
- data quality;
- trust claims;
- coverage claims;
- pricing;
- MVP definition;
- customer-facing claims;
- competitor positioning.

### Allowed

- create product audit;
- map commercial gaps;
- propose MVP;
- identify unsupported claims.

### Forbidden

- changing product claims in public docs without approval;
- presenting unverified data as sellable.

## 9. Mode Escalation

If a task starts as AUDIT_ONLY but discovers a required code change, it must not patch.

It must:

1. record finding;
2. create proposed task;
3. mark as RFC_REQUIRED if critical;
4. stop.

## 10. Mode Violation

If the executor violates mode constraints, the task must be marked NEEDS_REVIEW and the operator must inspect git diff before continuing.
