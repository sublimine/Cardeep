# CARDEEP — MASTER BLUEPRINT FOR GOVERNED AI DEVELOPMENT

## 0. Document Status

Document name:
`CARDEEP_MASTER_BLUEPRINT.md`

Location:
`docs/ai/CARDEEP_MASTER_BLUEPRINT.md`

Purpose:
This document is the master blueprint that governs how Claude Code or any AI coding executor must audit, test, harden and develop the Cardeep repository.

This document does not certify that Cardeep works.

This document defines how to move from current repository state to a controlled, evidence-based, testable and production-preparable system.

---

## 1. Operating Premise

Cardeep must not be treated as a normal codebase.

Cardeep is a high-complexity data infrastructure project combining:

- discovery of automotive market entities;
- public and semi-public source acquisition;
- HTTP scraping;
- potential browser scraping;
- source-specific connectors;
- dealer identity;
- listing identity;
- vehicle identity;
- ingestion;
- normalization;
- deduplication;
- delta detection;
- gone detection;
- verification/trust scoring;
- API serving;
- scheduler/operations;
- migrations;
- tests;
- product claims;
- commercial assumptions.

Therefore, every improvement must be done through governed tasks.

The AI executor must never optimize for speed over control.

---

## 2. Core Doctrine

The development doctrine is:

```text
Truth first.
Then map.
Then tests.
Then safe hardening.
Then production readiness.
Then productization.
Then growth.
```

No feature should be added before the system has been mapped.

No critical behavior should be changed before tests exist.

No product claim should be strengthened before evidence exists.

No production claim should be made without runtime validation.

No scraping scale claim should be made without source-by-source proof.

---

## 3. Primary Goal

The primary goal is to transform Cardeep from a large repository with ambitious documented claims into a system that is:

1. statically mapped;
2. runtime validated;
3. test-covered in critical paths;
4. operationally understandable;
5. production-preparable;
6. commercially assessable;
7. safe to evolve with Claude Code.

---

## 4. Non-Goals

The following are explicitly not goals during the early governed phases:

1. Do not rewrite the architecture.
2. Do not add new major features.
3. Do not introduce new scraping bypass systems.
4. Do not modify migrations casually.
5. Do not optimize performance before correctness.
6. Do not improve public marketing claims.
7. Do not delete legacy code before proving it is dead.
8. Do not merge modules merely for aesthetic reasons.
9. Do not convert the project into SaaS before validating the data engine.
10. Do not build frontend polish before proving API/data quality.

---

## 5. Evidence Hierarchy

### 5.1. Highest Evidence

Runtime evidence:

- tests executed and passing;
- migration applied successfully;
- API started successfully;
- scheduler started successfully;
- command output captured;
- DB query result captured;
- connector run captured;
- smoke test captured;
- CI result captured.

Label:
`VERIFIED_RUNTIME`

### 5.2. Medium Evidence

Static evidence:

- file exists;
- function exists;
- class exists;
- migration exists;
- test exists;
- config exists;
- router exists;
- code path exists.

Label:
`VERIFIED_STATIC`

### 5.3. Weak Evidence

Documentation evidence:

- README claim;
- PLAN claim;
- PROGRESO entry;
- architecture document;
- runbook claim;
- issue description.

Label:
`DOCUMENTED_CLAIM`

Documentation evidence must never be treated as runtime proof.

### 5.4. No Evidence

If no file, code, test, command or runtime observation supports the claim:

Label:
`NO_VERIFIED`

---

## 6. Current Known Repository Shape

The repository must be mapped by Claude Code directly.

Expected map to verify:

```text
.
├── .claude/
├── .github/workflows/
├── .playwright-mcp/
├── .wf/
├── countries/ES/
├── data/
├── docs/
├── migrations/
├── ops/
├── pipeline/
├── plans/
├── portal/
├── scripts/
├── services/
├── tests/
├── web/
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── PLAN.md
├── PROGRESO.md
├── README.md
├── RUNBOOK.md
├── requirements.txt
├── requirements-dev.txt
└── pytest.ini
```

Claude Code must verify the exact current tree locally.

If the local tree differs from this blueprint, local tree wins.

Record mismatch in:

```text
docs/ai/findings/CONTRADICTIONS.md
```

---

## 7. Master System Model

Cardeep must be reconstructed as this end-to-end chain:

```text
Source Universe
    ↓
Discovery
    ↓
Source Fetch / Scraping
    ↓
Source Connector / Recipe
    ↓
Extraction
    ↓
Ingestion
    ↓
Normalization
    ↓
Identity / Deduplication
    ↓
Delta Detection
    ↓
Gone Detection
    ↓
Verification / Trust
    ↓
Storage
    ↓
API Serving
    ↓
Scheduler / Operations
    ↓
Monitoring / Alerts
    ↓
Repair / Remediation
    ↓
Product / Commercial Interface
```

Each stage must be mapped with:

- files;
- functions/classes;
- inputs;
- outputs;
- tables;
- tests;
- runtime commands;
- failure modes;
- gaps;
- production readiness score.

---

## 8. Master Audit Dimensions

Every major module must be audited using these dimensions.

### 8.1. Functional Role

Questions:

- What does the module do?
- Is it core or auxiliary?
- Is it runtime code, script, test, migration, docs or legacy?
- Is it wired into an entrypoint?
- Is it reachable from scheduler/API/scripts?

Required output:

```text
Functional role: [description]
Reachability: WIRED / UNWIRED / UNKNOWN
Runtime status: VERIFIED_RUNTIME / NO_VERIFIED_RUNTIME
```

### 8.2. Data Contract

Questions:

- What data does it receive?
- What data does it produce?
- What format?
- What schema?
- What table?
- What identifiers?
- What assumptions?

Required output:

```text
Inputs:
Outputs:
Tables:
Identifiers:
Assumptions:
```

### 8.3. Failure Handling

Questions:

- What errors are handled?
- What errors are swallowed?
- What errors are retried?
- What errors corrupt state?
- What errors cause false positives?
- What errors cause false negatives?
- What errors affect source health?

Required output:

```text
Handled failures:
Unhandled failures:
Silent failures:
Corruption risks:
Retry/backoff behavior:
```

### 8.4. Idempotency

Questions:

- Can the module be run twice safely?
- Does it duplicate records?
- Does it create repeated events?
- Does it overwrite historical data?
- Does it update last_seen correctly?
- Does it mark gone incorrectly?

Required output:

```text
Idempotent: YES / NO / PARTIAL / UNKNOWN
Evidence:
Risks:
Tests:
```

### 8.5. Observability

Questions:

- Does it log?
- Does it emit metrics?
- Does it create alerts?
- Does it expose health?
- Does it record audit trail?
- Can an operator diagnose failure?

Required output:

```text
Logs:
Metrics:
Alerts:
Health:
Auditability:
Gaps:
```

### 8.6. Test Coverage

Questions:

- Are there unit tests?
- Are there integration tests?
- Are there fixtures?
- Are critical paths tested?
- Are failures tested?
- Are regressions tested?
- Do tests run locally?

Required output:

```text
Existing tests:
Missing tests:
Runtime result:
Coverage quality:
```

### 8.7. Production Readiness

Score from 0 to 10.

Criteria:

- 0 = concept only;
- 1 = stub;
- 2 = static code but not wired;
- 3 = wired but untested;
- 4 = basic tests;
- 5 = works locally with manual steps;
- 6 = repeated local validation;
- 7 = staging candidate;
- 8 = production candidate with observability;
- 9 = production hardened;
- 10 = mature, monitored, scalable, recoverable.

No module can score above 6 without runtime validation.

No module can score above 7 without observability.

No module can score above 8 without backup/restore/rollback/failure testing.

---

## 9. Critical Areas

### 9.1. Ingestion

Expected locations:

```text
pipeline/ingest.py
pipeline/harvest_dealer.py
pipeline/recipe.py
pipeline/delta.py
pipeline/evict.py
```

Risks:

- duplicate vehicles;
- wrong dealer association;
- false GONE;
- missed changes;
- repeated events;
- overwritten state;
- stale last_seen;
- bad photos;
- incorrect source attribution.

Required audit:

- lifecycle states;
- event generation;
- idempotency;
- gone guard;
- alert generation;
- VAM interaction;
- test coverage.

Default mode:
`AUDIT_ONLY`

Any behavior change:
`RFC_REQUIRED`

### 9.2. Delta / Gone

Expected locations:

```text
pipeline/delta.py
pipeline/delta_guard.py
pipeline/evict.py
tests/*delta*
tests/*gone*
```

Risks:

- false removals;
- missed removals;
- stale inventory served as live;
- event explosion;
- inconsistent state;
- connector-specific semantics ignored.

Required audit:

- how NEW is detected;
- how PRICE_CHANGE is detected;
- how KM_CHANGE is detected;
- how PHOTO_CHANGE is detected;
- how GONE is detected;
- how append-only connectors are handled;
- whether gone sweep is universal or partial;
- test coverage.

Default mode:
`AUDIT_ONLY`

Behavior change:
`RFC_REQUIRED`

### 9.3. Verification / VAM / Trust

Expected locations:

```text
pipeline/verify.py
pipeline/verify_ttl.py
pipeline/inquisition/
pipeline/gestionador/
docs/architecture/10-VERIFICATION-STACK.md
migrations/*verification*
migrations/*verdict*
tests/*verify*
```

Risks:

- false TRUSTWORTHY;
- zero-count certification;
- stale trust;
- quorum illusion;
- same-source dependency counted as independent;
- trust state not reflected in API;
- ledger not actually enforcing anything.

Required audit:

- trust states;
- quorum rules;
- independence rules;
- TTL;
- refutation;
- source health;
- ledger;
- inquisition;
- gestionador;
- API exposure;
- test coverage.

Default mode:
`AUDIT_ONLY`

Behavior change:
`RFC_REQUIRED`

### 9.4. Dedup / Identity

Expected locations:

```text
pipeline/ids.py
pipeline/identity/
pipeline/dedup*
migrations/*cluster*
tests/*dedup*
tests/*identity*
```

Risks:

- overmerge different vehicles;
- undermerge duplicates;
- unstable canonical IDs;
- dealer identity collision;
- source identity collision;
- bad geo key;
- broken historical events.

Required audit:

- dealer identifiers;
- source identifiers;
- vehicle identifiers;
- canonical vehicle;
- cluster model;
- scoring;
- blocking keys;
- merge criteria;
- unmerge strategy;
- tests.

Default mode:
`AUDIT_ONLY`

Behavior change:
`RFC_REQUIRED`

### 9.5. Scraping / Source Connectors

Expected locations:

```text
pipeline/sources/
pipeline/platform/
countries/ES/
scripts/*harvest*
scripts/*source*
tests/*source*
tests/*autoscout*
```

Risks:

- source blocks;
- inconsistent HTML;
- JS rendering missing;
- rate limit bans;
- proxy cost;
- session fragility;
- terms/legal issues;
- partial coverage presented as full;
- connector silently returns zero;
- stale parsing logic.

Required audit for each source:

```text
Source name:
Type: official / directory / OEM / marketplace / dealer / long-tail / Tier-1
Fetch method:
Parser:
Pagination:
JS required:
Auth required:
Proxy required:
Rate limit:
Retries:
Backoff:
Block detection:
Tests:
Runtime verified:
Production score:
Legal/compliance note:
```

Default mode:
`AUDIT_ONLY`

Adding browser/proxy/anti-bot:
`RFC_REQUIRED`

### 9.6. API

Expected locations:

```text
services/api/
tests/test_api*
docs/runbook/
```

Risks:

- serving unverified data;
- inconsistent response schema;
- slow queries;
- missing pagination;
- weak filters;
- cache inconsistency;
- rate limit issues;
- no auth;
- leaking internal states;
- product claims unsupported by endpoint behavior.

Required audit:

- endpoints;
- routers;
- schemas;
- filters;
- pagination;
- caching;
- rate limiting;
- error responses;
- dependency injection;
- DB queries;
- verification state exposure;
- test coverage.

Default mode:
`AUDIT_ONLY`

Contract change:
`RFC_REQUIRED`

### 9.7. Scheduler / Ops

Expected locations:

```text
pipeline/ops/
ops/
scripts/
docs/runbook/
```

Risks:

- duplicate jobs;
- missing locks;
- no backpressure;
- no recovery;
- no heartbeat;
- no alerting;
- unbounded concurrency;
- source bans;
- DB overload;
- silent failure.

Required audit:

- jobs;
- schedule intervals;
- locking;
- heartbeat;
- retries;
- backoff;
- alerting;
- failure recovery;
- concurrency;
- operational commands.

Default mode:
`AUDIT_ONLY`

Behavior change:
`RFC_REQUIRED`

### 9.8. Database / Migrations

Expected locations:

```text
migrations/
scripts/migrate.py
tests/*migration*
docs/runbook/DEPLOY.md
```

Risks:

- migration drift;
- stale runbook;
- missing indexes;
- missing constraints;
- unsafe deletes;
- table bloat;
- event table growth;
- no rollback;
- inconsistent schema with code;
- no DB snapshot for tests.

Required audit:

- migration order;
- latest migration;
- schema entities;
- indexes;
- constraints;
- views/materialized views;
- rollback strategy;
- migration runner;
- tests;
- mismatch with runbooks.

Default mode:
`AUDIT_ONLY`

Schema change:
`MIGRATION_REQUIRED` + `RFC_REQUIRED`

### 9.9. Tests / CI

Expected locations:

```text
tests/
pytest.ini
requirements-dev.txt
.github/workflows/
```

Risks:

- collect-only CI;
- tests exist but fail;
- tests are shallow;
- no integration DB tests;
- no source fixtures;
- no regression tests for critical bugs;
- no coverage threshold;
- no smoke path.

Required audit:

- list test files;
- categorize tests;
- identify critical coverage;
- identify missing tests;
- run tests if possible;
- record failures;
- propose hardening tasks.

Default mode:
`AUDIT_ONLY`

Adding tests:
`TEST_ONLY`

### 9.10. Product / Commercial

Expected locations:

```text
README.md
PLAN.md
PROGRESO.md
docs/
portal/
web/
services/api/
```

Risks:

- project is infrastructure, not product;
- customer-facing value unclear;
- API not packaged;
- data confidence not externally visible;
- pricing unsupported;
- coverage claims unsupported;
- production operations not ready;
- legal risk in source acquisition;
- competitor comparison unrealistic.

Required audit:

- who customer is;
- what API sells;
- what data is unique;
- what claims are provable;
- what claims are gated;
- what MVP can be sold safely;
- what must be removed from pitch.

Default mode:
`PRODUCT_GATE`

---

## 10. Execution Phases

### PHASE 0 — Governance Install

Objective:
Install docs/ai control framework.

Allowed:
docs/ai only.

Forbidden:
production code, tests, migrations.

Exit criteria:

- control docs exist;
- task queue exists or is ready to add;
- no product code changed.

### PHASE 1 — Static Repo Truth Map

Objective:
Build a verified static map of the repository.

Outputs:

```text
docs/ai/audits/00_REPO_MAP.md
docs/ai/findings/UNKNOWN_UNVERIFIED.md
docs/ai/findings/CONTRADICTIONS.md
docs/ai/control/05_EVIDENCE_LEDGER.md
```

Required map:

1. root files;
2. docs;
3. pipeline modules;
4. source connectors;
5. platform connectors;
6. services API;
7. migrations;
8. scripts;
9. tests;
10. ops;
11. web/portal;
12. CI workflows;
13. env/config;
14. dependency graph;
15. entrypoints.

Exit criteria:

- every major folder classified;
- every known entrypoint listed;
- unknowns recorded;
- no production code changed.

### PHASE 2 — Runtime Baseline

Objective:
Determine what actually runs.

Outputs:

```text
docs/ai/reports/RUNTIME_BASELINE.md
docs/ai/findings/BROKEN.md
docs/ai/control/05_EVIDENCE_LEDGER.md
```

Commands to attempt only if environment allows:

```bash
python --version
pip --version
python -m pytest --collect-only -q
python -m pytest -q
docker compose config
docker compose up -d cardeep-pg
python scripts/migrate.py up
uvicorn services.api.main:app --host 127.0.0.1 --port 8090
python -m pipeline.ops.scheduler --help
```

Rules:

- do not hide failures;
- do not repair during baseline unless task allows;
- do not change dependencies during baseline;
- record exact output;
- if blocked by environment, mark BLOCKED.

### PHASE 3 — Critical Static Audits

Objective:
Audit critical modules without changing behavior.

Outputs:

```text
docs/ai/audits/03_INGEST_AUDIT.md
docs/ai/audits/04_DELTA_GONE_AUDIT.md
docs/ai/audits/05_VERIFICATION_AUDIT.md
docs/ai/audits/02_DATA_MODEL_AUDIT.md
docs/ai/audits/06_SCRAPING_SOURCES_AUDIT.md
docs/ai/audits/07_API_AUDIT.md
docs/ai/audits/08_SCHEDULER_OPS_AUDIT.md
```

### PHASE 4 — Test Hardening

Objective:
Add regression and characterization tests before changing critical logic.

Allowed:
tests only unless explicit task says otherwise.

Priority tests:

1. ingest idempotency;
2. price change event;
3. km change event;
4. photo change event;
5. gone guard;
6. append-only connector behavior;
7. delta diff;
8. dedup scoring boundaries;
9. VAM zero-count bug regression;
10. TTL trust expiry;
11. API does not serve unverified data incorrectly;
12. scheduler lock/heartbeat.

### PHASE 5 — Safe Patches

Objective:
Fix isolated issues discovered by tests/audits.

Allowed:
small code changes with tests.

Forbidden:
architecture rewrite, migrations, critical behavior changes without RFC.

### PHASE 6 — RFC Critical Changes

Objective:
Design changes for dangerous areas.

RFC-required areas:

- ingest lifecycle;
- gone guard;
- delta semantics;
- dedup/identity;
- verification;
- scheduler;
- migrations;
- API contracts;
- scraping Tier‑1;
- production infra.

### PHASE 7 — Production Readiness

Objective:
Make Cardeep operable.

Required audits:

1. Docker;
2. env/secrets;
3. migrations;
4. DB backup/restore;
5. worker/scheduler;
6. logs;
7. metrics;
8. alerts;
9. source health;
10. rate limits;
11. concurrency;
12. cost;
13. legal/compliance review flags.

### PHASE 8 — Productization

Objective:
Define what can actually be sold.

Questions:

- Is Cardeep a data asset?
- Is it an API?
- Is it an internal market intelligence engine?
- Is it a scraping infrastructure?
- Is it a SaaS?
- Is it a competitor to AutoAPI/Carapis/Indicata?
- Is it currently a product or a lab?

---

## 11. Definition of First Serious Milestone

The first serious milestone is not “production”.

The first serious milestone is:

```text
MILESTONE 1 — REPOSITORY TRUTH BASELINE
```

It is achieved when:

1. repo map exists;
2. runtime baseline exists;
3. migrations status known;
4. tests status known;
5. API startup status known;
6. scheduler status known;
7. ingest audit complete;
8. delta/gone audit complete;
9. verification audit complete;
10. scraping source matrix complete;
11. data model audit complete;
12. risk register populated;
13. task queue prioritized;
14. no critical claim remains unclassified.

---

## 12. Source Classification Matrix

Claude Code must build:

```text
docs/ai/audits/SOURCE_MATRIX.md
```

Format:

| Source | Type | Module | Fetch | Parser | Pagination | JS | Auth | Proxy | Block Detection | Tests | Runtime | Status | Risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

Status values:

- VERIFIED_RUNTIME
- VERIFIED_STATIC
- PARTIAL
- BROKEN
- GATED
- DOCUMENTED_ONLY
- NO_VERIFIED

Source types:

- OFFICIAL
- DIRECTORY
- OEM
- MARKETPLACE
- DEALER
- LONG_TAIL
- TIER_1
- GEO
- ENRICHMENT
- UNKNOWN

No source may be called production-ready unless runtime validated.

---

## 13. Data Model Reconstruction Required

Claude Code must create:

```text
docs/ai/audits/02_DATA_MODEL_AUDIT.md
```

It must include:

1. all tables from migrations;
2. purpose of each table;
3. critical columns;
4. indexes;
5. constraints;
6. foreign keys;
7. state columns;
8. enum/state models;
9. event tables;
10. alert tables;
11. verification tables;
12. source health tables;
13. cluster/dedup tables;
14. API serving views;
15. risks.

Special attention:

- vehicle table;
- entity table;
- entity_source;
- vehicle_event;
- alert;
- verification_verdict;
- source health;
- platform listings;
- clusters;
- completion;
- tenancy/tiering if present;
- materialized views if present.

---

## 14. Documentation vs Code Audit Required

Claude Code must create:

```text
docs/ai/audits/DOCS_VS_CODE_AUDIT.md
```

Table format:

| Documented Promise | Source Document | Code Evidence | Runtime Evidence | Verdict | Risk | Next Task |
|---|---|---|---|---|---|---|

Allowed verdicts:

- VERIFIED_STATIC
- VERIFIED_RUNTIME
- PARTIAL
- NO_VERIFIED
- CONTRADICTION
- ASPIRATIONAL
- BROKEN
- GATED

Priority claims to classify:

1. 100% points of sale in Spain.
2. Full inventory by entity.
3. Real-time inventory.
4. Delta complete.
5. API by entity.
6. API by geo.
7. Recipe versioned by dealer.
8. Raw evicted safely.
9. Tier‑1 fully separated.
10. VAM quorum >= 2.
11. No number trustworthy without quorum.
12. Auto-repair/gestionador.
13. Inquisition.
14. Deep Ledger.
15. Source health.
16. Coverage gates.
17. Local quickstart.
18. Scheduler durable.
19. Production readiness.
20. Commercial readiness.

---

## 15. Critical Test Plan

Claude Code must create:

```text
docs/ai/audits/09_TEST_COVERAGE_AUDIT.md
```

The audit must identify tests for:

### 15.1. Ingest

- new vehicle insert;
- existing vehicle update;
- price change event;
- km change event;
- photo change event;
- idempotent re-ingest;
- gone transition;
- gone guard protection;
- alert creation;
- dealer/entity source update;
- malformed input handling.

### 15.2. Delta

- no-change diff;
- price diff;
- km diff;
- photo diff;
- missing listing diff;
- append-only connector case;
- false gone prevention;
- event deduplication.

### 15.3. Verification

- quorum pass;
- quorum fail;
- single-source unverified;
- refuted;
- stale TTL;
- zero-count not trustworthy;
- source independence;
- source health impact.

### 15.4. Dedup

- exact match;
- fuzzy match;
- VIN if present;
- plate if present;
- make/model/year/km/price boundaries;
- overmerge prevention;
- undermerge detection;
- canonical selection.

### 15.5. API

- health endpoint;
- listing endpoint;
- dealer endpoint;
- geo filter;
- pagination;
- empty results;
- invalid params;
- rate limit if present;
- cache behavior if present;
- verified-only behavior if present.

### 15.6. Scheduler/Ops

- job registration;
- lock behavior;
- heartbeat;
- retry;
- source failure;
- alert path;
- no duplicate execution.

---

## 16. Production Architecture Targets

Claude Code must not implement production architecture immediately.

It must document two production targets.

### 16.1. Cheap Production Architecture

Goal:
Lowest-cost serious deployment for early validation.

Expected components:

- one VPS;
- PostgreSQL;
- API process;
- scheduler/worker process;
- local logs;
- daily DB backup;
- basic health checks;
- minimal metrics;
- limited concurrency;
- no aggressive Tier‑1 drain;
- no expensive proxies by default.

Risks:

- single point of failure;
- limited scraping scale;
- limited observability;
- manual recovery;
- source blocking;
- not enterprise.

### 16.2. Serious Production Architecture

Goal:
Professional deployment.

Expected components:

- managed PostgreSQL or hardened Postgres;
- separate API service;
- separate worker pool;
- queue system;
- scheduler coordination;
- metrics;
- logs;
- alerts;
- secrets manager;
- backups;
- restore tests;
- source health;
- rate-limit manager;
- proxy/session pool if legally approved;
- CI/CD;
- staging environment;
- smoke tests;
- cost controls.

Risks:

- cost;
- complexity;
- legal review;
- maintenance;
- connector churn.

---

## 17. Commercial Reality Gate

Cardeep cannot be called a sellable product until the following are true:

1. customer segment defined;
2. API/data package defined;
3. freshness SLA defined;
4. coverage known;
5. verification confidence exposed;
6. source limitations documented;
7. legal/compliance reviewed;
8. pricing hypothesis created;
9. data sample available;
10. onboarding path exists;
11. product documentation exists;
12. production operation plan exists.

Before that, Cardeep is best described as:

```text
A technical data infrastructure project / market intelligence engine under development.
```

Not yet:

```text
A finished SaaS.
A certified full-market API.
A production-grade verified automotive data product.
```

Unless runtime/product evidence proves otherwise.

---

## 18. Prioritization Rule

Do not prioritize visual UI or new features before:

1. repo truth map;
2. runtime baseline;
3. migrations validation;
4. ingest/delta tests;
5. verification audit;
6. source matrix;
7. API audit;
8. production gap report.

---

## 19. Claude Code Behavior Requirements

Claude Code must:

1. read this blueprint before executing tasks;
2. obey task mode;
3. execute one task at a time;
4. update task status;
5. update evidence ledger;
6. update findings;
7. update risks;
8. stop on critical gates;
9. never invent runtime success;
10. never modify forbidden files.

---

## 20. First Execution Instruction

After this file and `docs/ai/tasks/TASK_QUEUE.yml` exist, execute:

```text
/loop
Read docs/ai/CARDEEP_MASTER_BLUEPRINT.md and docs/ai/tasks/TASK_QUEUE.yml.
Execute only the next READY task.
One task per iteration.
Respect mode, allowed_files, forbidden_files and validation.
Update findings, evidence ledger, risk register and task status.
Stop if RFC_REQUIRED or human approval is needed.
```

---

## 21. Current Top-Level Diagnosis To Validate

This is a hypothesis, not certification.

Claude Code must validate or refute it:

```text
Cardeep appears to be a serious, ambitious automotive data infrastructure repository with real code, migrations, API, scheduler, source connectors and tests. However, the strongest claims — 100% Spain coverage, full real-time inventory, complete delta, production readiness and commercial sellability — must be treated as unverified until proven by runtime execution, source matrix, DB validation, tests and product packaging.
```

Label:
`HYPOTHESIS_PENDING_VALIDATION`

---

## 22. Final Rule

If a task makes the repository look better on paper but does not improve truth, tests, operability or product clarity, it is low priority.

The goal is not to create impressive documents.

The goal is to create a system that can survive technical due diligence.
