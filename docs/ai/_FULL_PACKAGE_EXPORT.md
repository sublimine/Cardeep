# CARDEEP AI GOVERNANCE PACK — FULL PACKAGE EXPORT

Este archivo agrega las tres fases integradas. Los archivos canónicos son los separados en `docs/ai/`.



---

# FILE: INSTALL.md

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


---

# FILE: docs/ai/README.md

# Cardeep AI Governance Workspace

Este directorio contiene el sistema de gobierno para auditar, entender y desarrollar Cardeep con Claude Code.

## Orden de lectura

1. `control/00_MISSION_CONTRACT.md`
2. `control/01_OPERATING_RULES.md`
3. `CARDEEP_MASTER_BLUEPRINT.md`
4. `tasks/TASK_QUEUE.yml`
5. `loops/LOOP_001_STATIC_AUDIT.md`
6. `prompts/`

## Fase actual

Este pack instala el sistema operativo de comprensión y desarrollo gobernado.

No certifica que Cardeep funcione.

Primero se ejecuta el sellado de contexto: TASK-000 a TASK-015.


---

# FILE: docs/ai/CARDEEP_MASTER_BLUEPRINT.md

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


---

# FILE: docs/ai/tasks/TASK_QUEUE.yml

# CARDEEP GOVERNED TASK QUEUE
# Claude Code must execute exactly one READY task per loop iteration.

meta:
  project: "Cardeep"
  queue_version: "1.0"
  owner: "human_operator"
  executor: "claude_code"
  operating_model: "one_READY_task_per_iteration"
  default_mode: "AUDIT_ONLY"
  default_forbidden_files:
    - "pipeline/**"
    - "services/**"
    - "migrations/**"
    - "scripts/**"
    - "tests/**"
    - "requirements.txt"
    - "requirements-dev.txt"
    - "docker-compose.yml"
    - "Dockerfile"
    - "README.md"
    - "PLAN.md"
    - "PROGRESO.md"
    - "RUNBOOK.md"
  status_values: [READY, IN_PROGRESS, DONE, BLOCKED, NEEDS_REVIEW, RFC_REQUIRED, WAITING_FOR_HUMAN, FAILED_VALIDATION, PARTIAL_DONE]
  modes: [AUDIT_ONLY, TEST_ONLY, SAFE_PATCH, RFC_REQUIRED, MIGRATION_REQUIRED, PRODUCTION_GATE, PRODUCT_GATE]

tasks:

  TASK-000:
    title: "Verify AI governance files exist"
    status: READY
    mode: AUDIT_ONLY
    risk: LOW
    objective: "Verify that the docs/ai governance structure exists and is internally consistent."
    allowed_files:
      - "docs/ai/reports/GOVERNANCE_INSTALL_CHECK.md"
      - "docs/ai/findings/FINDINGS.md"
      - "docs/ai/control/05_EVIDENCE_LEDGER.md"
    forbidden_files: ["pipeline/**", "services/**", "migrations/**", "scripts/**", "tests/**", "README.md", "PLAN.md", "PROGRESO.md", "RUNBOOK.md"]
    inspect:
      - "docs/ai/control/00_MISSION_CONTRACT.md"
      - "docs/ai/control/01_OPERATING_RULES.md"
      - "docs/ai/control/02_EXECUTION_MODES.md"
      - "docs/ai/control/03_DEFINITION_OF_DONE.md"
      - "docs/ai/control/04_STATUS_TAXONOMY.md"
      - "docs/ai/control/05_EVIDENCE_LEDGER.md"
      - "docs/ai/control/06_RISK_REGISTER.md"
      - "docs/ai/control/07_DECISION_LOG.md"
      - "docs/ai/control/08_CHANGE_CONTROL.md"
      - "docs/ai/control/09_GIT_POLICY.md"
      - "docs/ai/control/10_REPORTING_PROTOCOL.md"
      - "docs/ai/control/11_NO_GO_ZONES.md"
      - "docs/ai/control/12_HUMAN_APPROVAL_GATES.md"
    validation: ["git status --short", "git diff --name-only"]
    acceptance:
      - "Governance files are present or missing files are listed."
      - "No production code changed."
      - "A governance install check report exists."
    on_failure:
      - "Mark BLOCKED if docs/ai/control does not exist."
      - "Mark NEEDS_REVIEW if forbidden files were modified."

  TASK-001:
    title: "Create verified repository map"
    status: READY
    mode: AUDIT_ONLY
    risk: LOW
    objective: "Create a complete static repository map with folder purpose, entrypoints, critical modules, scripts, tests, docs, configs and unknowns."
    allowed_files: ["docs/ai/audits/00_REPO_MAP.md", "docs/ai/findings/UNKNOWN_UNVERIFIED.md", "docs/ai/findings/FINDINGS.md", "docs/ai/control/05_EVIDENCE_LEDGER.md"]
    forbidden_files: ["pipeline/**", "services/**", "migrations/**", "scripts/**", "tests/**", "README.md", "PLAN.md", "PROGRESO.md", "RUNBOOK.md"]
    inspect: [".", ".github/workflows/", ".claude/", "countries/", "docs/", "migrations/", "ops/", "pipeline/", "plans/", "portal/", "scripts/", "services/", "tests/", "web/", "requirements.txt", "requirements-dev.txt", "pytest.ini", "docker-compose.yml", "Dockerfile", ".env.example"]
    validation: ["find . -maxdepth 3 -type f | sort | sed 's#^./##' | head -500", "git status --short", "git diff --name-only"]
    acceptance: ["Every top-level folder classified.", "Every known execution entrypoint listed.", "Every unknown marked NO_VERIFIED.", "No production code changed."]
    output_required: ["Repository folder map.", "Entrypoint map.", "Critical module list.", "Unknowns list."]

  TASK-002:
    title: "Audit documentation claims versus repository structure"
    status: READY
    mode: AUDIT_ONLY
    risk: MEDIUM
    objective: "Extract claims from README.md, PLAN.md, PROGRESO.md, RUNBOOK.md and docs, then compare them against static code evidence where possible."
    allowed_files: ["docs/ai/audits/DOCS_VS_CODE_AUDIT.md", "docs/ai/findings/CONTRADICTIONS.md", "docs/ai/findings/GATED.md", "docs/ai/findings/UNKNOWN_UNVERIFIED.md", "docs/ai/findings/FINDINGS.md", "docs/ai/control/05_EVIDENCE_LEDGER.md", "docs/ai/control/06_RISK_REGISTER.md"]
    forbidden_files: ["README.md", "PLAN.md", "PROGRESO.md", "RUNBOOK.md", "pipeline/**", "services/**", "migrations/**", "tests/**"]
    inspect: ["README.md", "PLAN.md", "PROGRESO.md", "RUNBOOK.md", "docs/", "pipeline/", "services/", "migrations/", "tests/"]
    validation: ["git diff --name-only"]
    acceptance:
      - "A table exists with Documented Promise, Source Document, Code Evidence, Runtime Evidence, Verdict, Risk, Next Task."
      - "Claims of 100% coverage, real-time, delta complete and production readiness are classified."
      - "No source document is edited."
    verdict_values: [VERIFIED_STATIC, VERIFIED_RUNTIME, PARTIAL, NO_VERIFIED, CONTRADICTION, ASPIRATIONAL, BROKEN, GATED]

  TASK-003:
    title: "Runtime baseline without repairs"
    status: READY
    mode: AUDIT_ONLY
    risk: MEDIUM
    objective: "Establish what can run locally without changing code or dependencies. Do not repair failures in this task."
    allowed_files: ["docs/ai/reports/RUNTIME_BASELINE.md", "docs/ai/findings/BROKEN.md", "docs/ai/findings/UNKNOWN_UNVERIFIED.md", "docs/ai/control/05_EVIDENCE_LEDGER.md", "docs/ai/control/06_RISK_REGISTER.md"]
    forbidden_files: ["pipeline/**", "services/**", "migrations/**", "scripts/**", "tests/**", "requirements.txt", "requirements-dev.txt", "docker-compose.yml", "Dockerfile"]
    commands_optional:
      - "python --version"
      - "pip --version"
      - "python -m pytest --collect-only -q"
      - "python -m pytest -q"
      - "docker compose config"
      - "docker compose up -d cardeep-pg"
      - "python scripts/migrate.py up"
      - "uvicorn services.api.main:app --host 127.0.0.1 --port 8090"
      - "python -m pipeline.ops.scheduler --help"
    validation: ["git diff --name-only"]
    acceptance: ["Runtime status known or explicitly blocked.", "Command outputs recorded.", "No repairs attempted.", "No code modified."]
    on_failure:
      - "Record command failure exactly."
      - "Mark task DONE if baseline was captured, even if commands failed."
      - "Mark BLOCKED only if environment prevents all meaningful commands."

  TASK-004:
    title: "Audit migrations and schema evolution"
    status: READY
    mode: AUDIT_ONLY
    risk: HIGH
    objective: "Reconstruct database schema and migration history from migrations and migration runner."
    allowed_files: ["docs/ai/audits/02_DATA_MODEL_AUDIT.md", "docs/ai/audits/MIGRATIONS_AUDIT.md", "docs/ai/findings/FINDINGS.md", "docs/ai/findings/CONTRADICTIONS.md", "docs/ai/findings/TECH_DEBT.md", "docs/ai/control/05_EVIDENCE_LEDGER.md", "docs/ai/control/06_RISK_REGISTER.md"]
    forbidden_files: ["migrations/**", "scripts/**", "pipeline/**", "services/**", "tests/**"]
    inspect: ["migrations/", "scripts/migrate.py", "docs/runbook/", "README.md", "RUNBOOK.md"]
    validation: ["ls -1 migrations | sort", "git diff --name-only"]
    acceptance: ["Latest migration identified.", "Runbook migration target compared to actual latest migration.", "Tables, indexes, constraints and views summarized.", "Critical table risks listed.", "No migration edited."]
    critical_focus: ["entity", "entity_source", "vehicle", "vehicle_event", "alert", "verification_verdict", "source health", "clusters", "platform listings", "serving views"]

  TASK-005:
    title: "Audit ingestion lifecycle"
    status: READY
    mode: AUDIT_ONLY
    risk: CRITICAL
    objective: "Audit ingestion behavior statically: dealer/entity upsert, vehicle upsert, events, last_seen, gone handling, alerts and verification interaction."
    allowed_files: ["docs/ai/audits/03_INGEST_AUDIT.md", "docs/ai/findings/FINDINGS.md", "docs/ai/findings/TECH_DEBT.md", "docs/ai/findings/UNKNOWN_UNVERIFIED.md", "docs/ai/control/05_EVIDENCE_LEDGER.md", "docs/ai/control/06_RISK_REGISTER.md", "docs/ai/tasks/TASK_QUEUE.yml"]
    forbidden_files: ["pipeline/ingest.py", "pipeline/harvest_dealer.py", "pipeline/recipe.py", "pipeline/delta.py", "migrations/**", "tests/**"]
    inspect: ["pipeline/ingest.py", "pipeline/harvest_dealer.py", "pipeline/recipe.py", "pipeline/delta.py", "tests/", "migrations/"]
    validation: ["git diff --name-only"]
    acceptance: ["Functions/classes identified.", "Inputs/outputs identified.", "Tables touched identified.", "Events generated identified.", "Error handling documented.", "Tests existing/missing listed.", "No production code changed."]
    required_sections: ["Purpose", "Entrypoints", "Data flow", "Tables touched", "Lifecycle states", "Events", "Gone guard", "Alerts", "Verification interaction", "Idempotency", "Failure modes", "Tests", "Risks", "Production score"]

  TASK-006:
    title: "Audit delta and gone guard"
    status: READY
    mode: AUDIT_ONLY
    risk: CRITICAL
    objective: "Audit delta and gone handling, including append-only connectors, false gone protection and event generation."
    allowed_files: ["docs/ai/audits/04_DELTA_GONE_AUDIT.md", "docs/ai/findings/FINDINGS.md", "docs/ai/findings/BROKEN.md", "docs/ai/findings/GATED.md", "docs/ai/control/05_EVIDENCE_LEDGER.md", "docs/ai/control/06_RISK_REGISTER.md", "docs/ai/tasks/TASK_QUEUE.yml"]
    forbidden_files: ["pipeline/delta.py", "pipeline/delta_guard.py", "pipeline/evict.py", "pipeline/ingest.py", "migrations/**", "tests/**"]
    inspect: ["pipeline/delta.py", "pipeline/delta_guard.py", "pipeline/evict.py", "pipeline/ingest.py", "tests/", "migrations/"]
    validation: ["git diff --name-only"]
    acceptance: ["Delta types mapped.", "Gone conditions mapped.", "False gone risks documented.", "Tests existing/missing identified.", "Any critical behavior change proposed as RFC_REQUIRED, not implemented."]

  TASK-007:
    title: "Audit verification stack"
    status: READY
    mode: AUDIT_ONLY
    risk: CRITICAL
    objective: "Audit VAM, verification verdicts, TTL, source independence, Inquisition, Gestionador and ledger claims."
    allowed_files: ["docs/ai/audits/05_VERIFICATION_AUDIT.md", "docs/ai/findings/FINDINGS.md", "docs/ai/findings/GATED.md", "docs/ai/findings/CONTRADICTIONS.md", "docs/ai/control/05_EVIDENCE_LEDGER.md", "docs/ai/control/06_RISK_REGISTER.md", "docs/ai/tasks/TASK_QUEUE.yml"]
    forbidden_files: ["pipeline/verify.py", "pipeline/verify_ttl.py", "pipeline/inquisition/**", "pipeline/gestionador/**", "migrations/**", "tests/**"]
    inspect: ["pipeline/verify.py", "pipeline/verify_ttl.py", "pipeline/inquisition/", "pipeline/gestionador/", "docs/architecture/10-VERIFICATION-STACK.md", "migrations/", "tests/"]
    validation: ["git diff --name-only"]
    acceptance: ["Trust states mapped.", "Quorum rules mapped.", "TTL behavior mapped.", "Independence logic mapped.", "Ledger and Inquisition implementation status classified.", "Zero-count trustworthy regression risk checked."]

  TASK-008:
    title: "Audit dedup and identity"
    status: READY
    mode: AUDIT_ONLY
    risk: CRITICAL
    objective: "Audit dealer identity, vehicle identity, source identity, clustering and dedup behavior."
    allowed_files: ["docs/ai/audits/DEDUP_IDENTITY_AUDIT.md", "docs/ai/findings/FINDINGS.md", "docs/ai/findings/TECH_DEBT.md", "docs/ai/control/05_EVIDENCE_LEDGER.md", "docs/ai/control/06_RISK_REGISTER.md", "docs/ai/tasks/TASK_QUEUE.yml"]
    forbidden_files: ["pipeline/ids.py", "pipeline/identity/**", "pipeline/**dedup**", "migrations/**", "tests/**"]
    inspect: ["pipeline/ids.py", "pipeline/identity/", "pipeline/", "migrations/", "tests/"]
    validation: ["git diff --name-only"]
    acceptance: ["Dealer identity flow mapped.", "Vehicle identity flow mapped.", "Cluster/dedup tables identified.", "Overmerge and undermerge risks documented.", "Tests existing/missing identified."]

  TASK-009:
    title: "Audit source connectors and create source matrix"
    status: READY
    mode: AUDIT_ONLY
    risk: HIGH
    objective: "Create a source-by-source matrix for all connectors, classifying fetch method, parser, pagination, JS/browser needs, auth/proxy/rate-limit assumptions, tests and status."
    allowed_files: ["docs/ai/audits/06_SCRAPING_SOURCES_AUDIT.md", "docs/ai/audits/SOURCE_MATRIX.md", "docs/ai/findings/GATED.md", "docs/ai/findings/BROKEN.md", "docs/ai/findings/FINDINGS.md", "docs/ai/control/05_EVIDENCE_LEDGER.md", "docs/ai/control/06_RISK_REGISTER.md", "docs/ai/tasks/TASK_QUEUE.yml"]
    forbidden_files: ["pipeline/sources/**", "pipeline/platform/**", "countries/**", "scripts/**", "tests/**", "requirements.txt"]
    inspect: ["pipeline/sources/", "pipeline/platform/", "countries/ES/", "scripts/", "tests/", "requirements.txt", "docs/research/"]
    validation: ["git diff --name-only"]
    acceptance: ["Each connector/source classified.", "Tier-1 vs long-tail separation assessed.", "GATED dependencies recorded.", "No connector code changed."]

  TASK-010:
    title: "Audit API surface and serving contract"
    status: READY
    mode: AUDIT_ONLY
    risk: HIGH
    objective: "Audit FastAPI application, routers, endpoints, schemas, caching, rate limiting, DB dependencies and serving semantics."
    allowed_files: ["docs/ai/audits/07_API_AUDIT.md", "docs/ai/findings/FINDINGS.md", "docs/ai/findings/TECH_DEBT.md", "docs/ai/control/05_EVIDENCE_LEDGER.md", "docs/ai/control/06_RISK_REGISTER.md", "docs/ai/tasks/TASK_QUEUE.yml"]
    forbidden_files: ["services/api/**", "tests/**", "pipeline/**"]
    inspect: ["services/api/", "tests/", "docs/runbook/", "README.md"]
    validation: ["git diff --name-only"]
    acceptance: ["Endpoint list created.", "Input/output contracts summarized.", "Verification/trust exposure checked.", "Pagination/filter/cache/rate limit behavior mapped.", "API production risks listed."]

  TASK-011:
    title: "Audit scheduler and operations"
    status: READY
    mode: AUDIT_ONLY
    risk: HIGH
    objective: "Audit scheduler, ops scripts, health, heartbeat, locks, coverage checks, watchdogs, alerts and repair workflows."
    allowed_files: ["docs/ai/audits/08_SCHEDULER_OPS_AUDIT.md", "docs/ai/findings/FINDINGS.md", "docs/ai/findings/GATED.md", "docs/ai/control/05_EVIDENCE_LEDGER.md", "docs/ai/control/06_RISK_REGISTER.md", "docs/ai/tasks/TASK_QUEUE.yml"]
    forbidden_files: ["pipeline/ops/**", "ops/**", "scripts/**", "tests/**"]
    inspect: ["pipeline/ops/", "ops/", "scripts/", "docs/runbook/", "tests/"]
    validation: ["git diff --name-only"]
    acceptance: ["Jobs listed.", "Entrypoints listed.", "Locks/heartbeat mapped.", "Failure recovery mapped.", "Operational gaps listed."]

  TASK-012:
    title: "Audit tests and CI"
    status: READY
    mode: AUDIT_ONLY
    risk: HIGH
    objective: "Classify the full test suite and CI workflows. Identify critical paths lacking tests."
    allowed_files: ["docs/ai/audits/09_TEST_COVERAGE_AUDIT.md", "docs/ai/findings/FINDINGS.md", "docs/ai/findings/TECH_DEBT.md", "docs/ai/tasks/TASK_QUEUE.yml", "docs/ai/control/05_EVIDENCE_LEDGER.md", "docs/ai/control/06_RISK_REGISTER.md"]
    forbidden_files: ["tests/**", ".github/workflows/**", "pytest.ini", "requirements-dev.txt", "pipeline/**", "services/**"]
    inspect: ["tests/", ".github/workflows/", "pytest.ini", "requirements-dev.txt"]
    validation: ["python -m pytest --collect-only -q", "git diff --name-only"]
    acceptance: ["Tests categorized by subsystem.", "CI workflows categorized.", "Critical missing tests listed.", "Collect-only result recorded if command runs."]

  TASK-013:
    title: "Create production gap report"
    status: READY
    mode: PRODUCTION_GATE
    risk: HIGH
    objective: "Evaluate production readiness without modifying production configuration."
    allowed_files: ["docs/ai/audits/10_PRODUCTION_AUDIT.md", "docs/ai/reports/PRODUCTION_GAP_REPORT.md", "docs/ai/findings/GATED.md", "docs/ai/findings/FINDINGS.md", "docs/ai/control/06_RISK_REGISTER.md", "docs/ai/tasks/TASK_QUEUE.yml"]
    forbidden_files: ["Dockerfile", "docker-compose.yml", ".env.example", "ops/**", "pipeline/ops/**", "scripts/**", "services/**", "migrations/**"]
    inspect: ["Dockerfile", "docker-compose.yml", ".env.example", "docs/runbook/", "ops/", "pipeline/ops/", "services/api/", "scripts/"]
    validation: ["docker compose config", "git diff --name-only"]
    acceptance: ["Cheap production architecture defined.", "Serious production architecture defined.", "Backups, logs, metrics, alerts, secrets and scaling gaps listed.", "No deployment file changed."]

  TASK-014:
    title: "Create product and commercial audit"
    status: READY
    mode: PRODUCT_GATE
    risk: HIGH
    objective: "Evaluate whether Cardeep is currently a technical project, infrastructure, API, SaaS, data asset, internal tool or sellable product."
    allowed_files: ["docs/ai/audits/11_PRODUCT_AUDIT.md", "docs/ai/reports/PRODUCTIZATION_GAP_REPORT.md", "docs/ai/findings/GATED.md", "docs/ai/findings/CONTRADICTIONS.md", "docs/ai/control/06_RISK_REGISTER.md", "docs/ai/tasks/TASK_QUEUE.yml"]
    forbidden_files: ["README.md", "PLAN.md", "PROGRESO.md", "RUNBOOK.md", "portal/**", "web/**", "services/**", "pipeline/**"]
    inspect: ["README.md", "PLAN.md", "PROGRESO.md", "docs/", "services/api/", "portal/", "web/"]
    validation: ["git diff --name-only"]
    acceptance: ["Commercial category assigned.", "Sellable MVP boundary proposed.", "Unsupported claims listed.", "Money path and self-deception path identified.", "No public docs changed."]

  TASK-015:
    title: "Build module scorecard"
    status: READY
    mode: AUDIT_ONLY
    risk: MEDIUM
    objective: "Consolidate all audit findings into a scorecard by subsystem."
    allowed_files: ["docs/ai/reports/MODULE_SCORECARD.md", "docs/ai/reports/EXECUTIVE_STATUS.md", "docs/ai/tasks/TASK_QUEUE.yml"]
    forbidden_files: ["pipeline/**", "services/**", "migrations/**", "scripts/**", "tests/**"]
    inspect: ["docs/ai/audits/", "docs/ai/findings/", "docs/ai/control/06_RISK_REGISTER.md"]
    validation: ["git diff --name-only"]
    acceptance: ["Each subsystem scored 0-10.", "Each score justified by evidence.", "Runtime-unverified modules capped appropriately.", "Top 10 risks listed.", "Next 10 actions listed."]

  TASK-016:
    title: "Add characterization tests for ingest"
    status: BLOCKED
    mode: TEST_ONLY
    risk: HIGH
    blocked_reason: "Requires completion of TASK-005 ingest audit."
    objective: "Add tests for current ingest behavior without changing production logic."
    allowed_files: ["tests/test_ingest_characterization.py", "tests/fixtures/**", "docs/ai/findings/FINDINGS.md", "docs/ai/control/05_EVIDENCE_LEDGER.md"]
    forbidden_files: ["pipeline/ingest.py", "pipeline/delta.py", "migrations/**", "services/**"]
    validation: ["python -m pytest tests/test_ingest_characterization.py -q"]
    acceptance: ["Tests document current behavior.", "Production logic unchanged.", "Failures documented if current behavior is broken."]

  TASK-017:
    title: "Add characterization tests for delta/gone"
    status: BLOCKED
    mode: TEST_ONLY
    risk: HIGH
    blocked_reason: "Requires completion of TASK-006 delta/gone audit."
    objective: "Add tests for current delta/gone behavior without changing production logic."
    allowed_files: ["tests/test_delta_gone_characterization.py", "tests/fixtures/**", "docs/ai/findings/FINDINGS.md", "docs/ai/control/05_EVIDENCE_LEDGER.md"]
    forbidden_files: ["pipeline/delta.py", "pipeline/delta_guard.py", "pipeline/evict.py", "pipeline/ingest.py", "migrations/**"]
    validation: ["python -m pytest tests/test_delta_gone_characterization.py -q"]
    acceptance: ["False gone scenarios tested.", "Append-only scenarios tested where possible.", "Production logic unchanged."]

  TASK-018:
    title: "Add verification regression tests"
    status: BLOCKED
    mode: TEST_ONLY
    risk: HIGH
    blocked_reason: "Requires completion of TASK-007 verification audit."
    objective: "Add regression tests for VAM/trust behavior, especially zero-count and quorum cases."
    allowed_files: ["tests/test_verification_regressions.py", "tests/fixtures/**", "docs/ai/findings/FINDINGS.md", "docs/ai/control/05_EVIDENCE_LEDGER.md"]
    forbidden_files: ["pipeline/verify.py", "pipeline/verify_ttl.py", "pipeline/inquisition/**", "pipeline/gestionador/**", "migrations/**"]
    validation: ["python -m pytest tests/test_verification_regressions.py -q"]
    acceptance: ["Zero-count not trustworthy covered.", "Single-source unverified covered.", "Quorum pass/fail covered.", "Production logic unchanged."]

  TASK-019:
    title: "RFC for ingest/delta hardening"
    status: BLOCKED
    mode: RFC_REQUIRED
    risk: CRITICAL
    blocked_reason: "Requires TASK-005, TASK-006, TASK-016 and TASK-017."
    objective: "Create RFC for any required changes to ingest/delta/gone behavior discovered by audits and tests."
    allowed_files: ["docs/ai/rfcs/RFC_INGEST_DELTA_HARDENING.md", "docs/ai/control/07_DECISION_LOG.md", "docs/ai/tasks/TASK_QUEUE.yml"]
    forbidden_files: ["pipeline/**", "migrations/**", "tests/**"]
    validation: ["git diff --name-only"]
    acceptance: ["RFC created.", "No implementation performed.", "Human approval required."]

  TASK-020:
    title: "RFC for production architecture"
    status: BLOCKED
    mode: RFC_REQUIRED
    risk: HIGH
    blocked_reason: "Requires TASK-013 production gap report."
    objective: "Create RFC proposing cheap production and serious production architecture."
    allowed_files: ["docs/ai/rfcs/RFC_PRODUCTION_ARCHITECTURE.md", "docs/ai/control/07_DECISION_LOG.md", "docs/ai/tasks/TASK_QUEUE.yml"]
    forbidden_files: ["Dockerfile", "docker-compose.yml", "ops/**", "pipeline/**", "services/**", "scripts/**", "migrations/**"]
    validation: ["git diff --name-only"]
    acceptance: ["RFC created.", "No deployment files changed.", "Human approval required."]

  TASK-021:
    title: "RFC for product MVP"
    status: BLOCKED
    mode: RFC_REQUIRED
    risk: HIGH
    blocked_reason: "Requires TASK-014 product audit and TASK-015 scorecard."
    objective: "Create RFC defining the first sellable MVP boundary and what claims are allowed."
    allowed_files: ["docs/ai/rfcs/RFC_PRODUCT_MVP.md", "docs/ai/control/07_DECISION_LOG.md", "docs/ai/tasks/TASK_QUEUE.yml"]
    forbidden_files: ["README.md", "PLAN.md", "PROGRESO.md", "portal/**", "web/**", "services/**", "pipeline/**"]
    validation: ["git diff --name-only"]
    acceptance: ["MVP boundary defined.", "Unsupported claims excluded.", "No public product docs changed.", "Human approval required."]


---

# FILE: docs/ai/tasks/TASK_TEMPLATE.yml

# Use this template for every new task.
# Do not create vague tasks.
# Every task must declare mode, risk, allowed_files, forbidden_files, validation and acceptance.

TASK-XXX:
  title: ""
  status: READY
  mode: AUDIT_ONLY
  risk: LOW

  objective: >
    [Precise objective. One task only. No mixed audit + implementation unless explicitly intended.]

  background: >
    [Why this task exists. Reference prior findings, evidence IDs or audits.]

  allowed_files:
    - "docs/ai/..."

  forbidden_files:
    - "pipeline/**"
    - "services/**"
    - "migrations/**"
    - "scripts/**"
    - "tests/**"
    - "requirements.txt"
    - "requirements-dev.txt"
    - "docker-compose.yml"
    - "Dockerfile"
    - "README.md"
    - "PLAN.md"
    - "PROGRESO.md"
    - "RUNBOOK.md"

  inspect:
    - ""

  commands_optional:
    - ""

  validation:
    - "git status --short"
    - "git diff --name-only"

  acceptance:
    - ""
    - ""

  evidence_required: true

  update_required:
    - "docs/ai/findings/FINDINGS.md"
    - "docs/ai/control/05_EVIDENCE_LEDGER.md"
    - "docs/ai/control/06_RISK_REGISTER.md"
    - "docs/ai/tasks/TASK_QUEUE.yml"

  stop_conditions:
    - "Forbidden file must be modified."
    - "Critical behavior change is needed."
    - "Migration is needed."
    - "Tests fail unexpectedly."
    - "Task scope is too broad."
    - "Human approval is required."

  on_success:
    - "Mark DONE only if acceptance criteria are met."

  on_failure:
    - "Mark BLOCKED, NEEDS_REVIEW, FAILED_VALIDATION or RFC_REQUIRED."
    - "Do not hide failures."


---

# FILE: docs/ai/rfcs/RFC_TEMPLATE.md

# RFC-XXXX — [TITLE]

## 1. Status

Status:
PROPOSED / APPROVED / REJECTED / SUPERSEDED / IMPLEMENTED / ABANDONED

Date:
YYYY-MM-DD

Author:
AI executor / human operator

Reviewer:
Human operator

Decision Required:
YES / NO

---

## 2. Executive Summary

[Explain the change in 5-10 lines. No marketing language. No vague claims.]

---

## 3. Problem Statement

What problem is this RFC solving?

Include:

- observed behavior;
- expected behavior;
- why current behavior is insufficient;
- what risk exists if nothing changes.

---

## 4. Evidence

Every claim must be backed by evidence.

| Evidence ID | Type | Path / Command / Output | Claim Supported | Confidence |
|---|---|---|---|---|
| EVIDENCE-XXXX | FILE/FUNCTION/TEST/COMMAND/DB_QUERY/DOC | ... | ... | VERIFIED_STATIC / VERIFIED_RUNTIME / PARTIAL / NO_VERIFIED |

---

## 5. Current Behavior

Describe the current implementation.

Include:

- files;
- functions/classes;
- data flow;
- tables;
- states;
- errors;
- tests;
- runtime status.

---

## 6. Proposed Change

Describe exactly what should change.

Include:

- files to modify;
- files not to modify;
- expected behavior;
- new tests;
- updated docs;
- migration impact;
- API impact;
- operational impact.

---

## 7. Scope

### In Scope

-

### Out of Scope

-

---

## 8. Affected Areas

Check all that apply:

- [ ] Ingest
- [ ] Delta
- [ ] Gone guard
- [ ] Dedup/identity
- [ ] Verification/VAM
- [ ] API contract
- [ ] Scheduler/ops
- [ ] Source connector
- [ ] Scraping/browser/proxy
- [ ] Database schema
- [ ] Migration
- [ ] Docker/deploy
- [ ] Secrets/security
- [ ] Tests
- [ ] Public documentation
- [ ] Product/commercial claims

---

## 9. Risk Assessment

| Risk | Severity | Likelihood | Blast Radius | Mitigation |
|---|---|---|---|---|
| ... | LOW/MEDIUM/HIGH/CRITICAL | LOW/MEDIUM/HIGH | ... | ... |

---

## 10. Data Impact

Does this change affect data?

- Existing rows:
- New rows:
- Historical events:
- Identity/canonical IDs:
- Dedup clusters:
- Trust/verdicts:
- API output:
- Backfill needed:
- Corruption risk:

If no data impact, state:

```text
No data impact identified.
```

---

## 11. Migration Impact

Does this require a DB migration?

- YES / NO / UNKNOWN

If YES:

- migration filename proposal;
- table changes;
- index changes;
- constraint changes;
- rollback plan;
- data migration plan.

If NO:

```text
No migration required.
```

---

## 12. API Impact

Does this change API behavior?

- YES / NO / UNKNOWN

If YES:

- endpoints affected;
- request changes;
- response changes;
- compatibility;
- versioning;
- client impact.

---

## 13. Operational Impact

Include:

- scheduler impact;
- worker impact;
- concurrency;
- rate limits;
- source health;
- logs;
- metrics;
- alerts;
- backup/restore;
- cost.

---

## 14. Security / Legal / Compliance Impact

Include:

- secrets;
- credentials;
- auth;
- PII;
- scraping legality;
- robots/ToS uncertainty;
- data retention;
- external source restrictions.

If uncertain:

```text
LEGAL_REVIEW_REQUIRED
```

---

## 15. Alternatives Considered

### Alternative A — Do Nothing

Pros:
-

Cons:
-

### Alternative B — Minimal Patch

Pros:
-

Cons:
-

### Alternative C — Larger Refactor

Pros:
-

Cons:
-

---

## 16. Recommended Option

Recommended option:
A / B / C / Other

Reason:
-

---

## 17. Test Plan

Required tests:

- unit:
- integration:
- regression:
- API:
- DB/migration:
- scheduler:
- source fixture:
- smoke:

Commands:

```bash
python -m pytest [target] -q
```

---

## 18. Validation Plan

Validation before merge:

1.
2.
3.

Validation after deployment:

1.
2.
3.

---

## 19. Rollback Plan

How to revert safely?

- Code rollback:
- Migration rollback:
- Data rollback:
- Config rollback:
- Operational rollback:

If rollback is not simple, mark:

```text
ROLLBACK_RISK_HIGH
```

---

## 20. Implementation Tasks

Create child tasks only after approval.

| Task ID | Title | Mode | Risk | Status |
|---|---|---|---|---|
| TASK-XXXX | ... | TEST_ONLY / SAFE_PATCH / MIGRATION_REQUIRED | ... | BLOCKED |

---

## 21. Approval

Human decision:

```text
APPROVED / REJECTED / REQUEST_MORE_INFO
```

Approval notes:

-

Date:

-


---

# FILE: docs/ai/control/00_MISSION_CONTRACT.md

# 00 — MISSION CONTRACT

## 1. Purpose

This document defines the institutional operating contract for AI-assisted development inside the Cardeep repository.

The purpose is not to make fast changes.

The purpose is to transform Cardeep into a system that is:

- understandable;
- auditable;
- testable;
- operable;
- safe to evolve;
- technically defensible;
- commercially assessable;
- production-preparable.

## 2. Core Mission

The AI executor must help improve Cardeep through controlled, evidence-based work.

The executor must not behave as an autonomous product owner, architect, or uncontrolled refactoring agent.

The executor must operate under these principles:

1. Truth before optimism.
2. Evidence before claims.
3. Tests before confidence.
4. Small changes before broad refactors.
5. Documentation before critical modification.
6. RFC before dangerous changes.
7. Human approval before schema, ingest, delta, dedup, verification, scheduler, Tier-1 scraping, production or API contract changes.
8. No destructive operations.
9. No hidden assumptions.
10. No DONE status without validation.

## 3. Repository Context

Cardeep appears to include multiple high-risk technical domains:

- data ingestion;
- external source discovery;
- scraping and fetching;
- platform connectors;
- inventory lifecycle;
- delta detection;
- gone detection;
- deduplication;
- verification/trust systems;
- API serving;
- scheduler and operations;
- database migrations;
- tests;
- documentation;
- commercial/product claims.

Because of this, the repository must be treated as a critical system, not a simple application.

## 4. Primary Objective

The primary objective is to create a controlled path from current repository state to a more reliable, testable, production-ready and product-evaluable system.

The work must progress in this order:

1. Map what exists.
2. Separate documentation from implementation.
3. Identify critical paths.
4. Identify broken, partial, gated and unverified areas.
5. Add missing tests.
6. Harden safe modules.
7. Propose RFCs for risky modules.
8. Improve production readiness.
9. Improve product readiness.
10. Remove or quarantine misleading claims.

## 5. What The AI Executor May Do

The executor may:

- read files;
- map modules;
- generate documentation under docs/ai/;
- create audits;
- create findings;
- create risk records;
- create task queue entries;
- create tests when explicitly allowed;
- perform small safe patches when explicitly allowed;
- run validation commands;
- report failures honestly;
- create RFCs for dangerous changes.

## 6. What The AI Executor Must Not Do Without Explicit Approval

The executor must not:

- rewrite architecture;
- delete files;
- modify migrations;
- modify database schema;
- change ingest behavior;
- change delta/gone behavior;
- change dedup logic;
- change verification/VAM/trust logic;
- alter API contracts;
- alter scheduler behavior;
- add new scraping dependencies;
- add proxy/browser automation systems;
- modify production/deploy behavior;
- change authentication/security;
- change pricing/product claims;
- update public documentation claims;
- mark features production-ready without runtime verification.

## 7. Evidence Standard

Every important claim must be linked to evidence.

Allowed evidence types:

- file path;
- function/class name;
- line range if available;
- migration filename;
- test filename;
- command output;
- log output;
- API response;
- database query result;
- runtime observation;
- CI result;
- documented claim clearly marked as documented-only.

Claims without evidence must be marked as NO_VERIFIED.

## 8. Confidence Labels

Every audit claim must use one of the following labels:

- VERIFIED_STATIC
- VERIFIED_RUNTIME
- PARTIAL
- NO_VERIFIED
- BROKEN
- CONTRADICTION
- GATED
- ASSUMED

## 9. Runtime Honesty

If a command was not executed, the executor must not imply runtime verification.

Examples:

Incorrect:
"The tests pass."

Correct:
"NO_VERIFIED_RUNTIME: tests were not executed."

Incorrect:
"The API works."

Correct:
"VERIFIED_STATIC: API entrypoint exists. NO_VERIFIED_RUNTIME: API was not started."

## 10. Final Governance Rule

The AI executor is not allowed to optimize for appearing productive.

It must optimize for:

- correctness;
- traceability;
- safety;
- reversibility;
- evidence;
- maintainability.


---

# FILE: docs/ai/control/01_OPERATING_RULES.md

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


---

# FILE: docs/ai/control/02_EXECUTION_MODES.md

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


---

# FILE: docs/ai/control/03_DEFINITION_OF_DONE.md

# 03 — DEFINITION OF DONE

## 1. Purpose

This document defines when a task can be considered completed.

No task is DONE simply because files were edited.

A task is DONE only when evidence, validation and scope control are complete.

## 2. Universal Done Criteria

A task can be marked DONE only if all conditions are true:

1. The task scope was followed.
2. Only allowed files were modified.
3. No forbidden files were modified.
4. All required outputs were produced.
5. Evidence was recorded.
6. Findings were updated if needed.
7. Risk register was updated if needed.
8. Validation commands were executed or inability documented.
9. Tests passed if tests were required.
10. No new untracked critical risk was introduced.
11. git diff was inspected.
12. Acceptance criteria were met.

## 3. Audit Task Done Criteria

For AUDIT_ONLY tasks:

- no production code changed;
- audit document exists;
- module purpose documented;
- entrypoints identified;
- inputs and outputs identified;
- data structures/tables identified if applicable;
- dependencies identified;
- errors/edge cases identified;
- tests existing/missing identified;
- risks recorded;
- unknowns marked NO_VERIFIED;
- runtime claims avoided unless executed.

## 4. Test Task Done Criteria

For TEST_ONLY tasks:

- tests created or improved;
- production logic unchanged;
- tests target specific behavior;
- tests fail for meaningful reason before fix if applicable;
- tests pass after expected changes if applicable;
- command output recorded;
- coverage limitations documented.

## 5. Safe Patch Done Criteria

For SAFE_PATCH tasks:

- bug or issue has evidence;
- patch is minimal;
- relevant test exists;
- test passes;
- no unrelated refactor;
- behavior change described;
- rollback simple;
- risk acceptable.

## 6. RFC Task Done Criteria

For RFC_REQUIRED tasks:

- RFC document created;
- problem described with evidence;
- current behavior described;
- proposed behavior described;
- alternatives listed;
- risks listed;
- tests planned;
- rollback planned;
- human approval explicitly required;
- no implementation performed.

## 7. Migration Task Done Criteria

For MIGRATION_REQUIRED tasks:

- approved RFC exists;
- migration file created;
- schema impact documented;
- data impact documented;
- index/constraint impact documented;
- rollback approach documented;
- validation command run;
- tests updated if applicable;
- no existing applied migration modified unless approved.

## 8. Production Gate Done Criteria

For PRODUCTION_GATE tasks:

- production component mapped;
- secrets handling reviewed;
- logs/metrics/alerts reviewed;
- failure recovery reviewed;
- scaling limits reviewed;
- cost risks reviewed;
- backup/restore reviewed;
- gaps documented;
- no production behavior changed without approval.

## 9. Product Gate Done Criteria

For PRODUCT_GATE tasks:

- product claim mapped to evidence;
- customer value clarified;
- unsupported claims identified;
- MVP boundary defined;
- sellability risks documented;
- technical dependencies mapped;
- no public claim updated without approval.

## 10. Invalid DONE States

A task cannot be DONE if:

- tests were required but not run;
- forbidden files were modified;
- evidence is missing;
- runtime behavior is claimed but not executed;
- failures were ignored;
- scope expanded silently;
- critical change was made without RFC;
- output is only a narrative without actionable findings.

## 11. Allowed Non-DONE Terminal States

Use these when DONE is not valid:

- BLOCKED
- NEEDS_REVIEW
- RFC_REQUIRED
- PARTIAL
- FAILED_VALIDATION
- WAITING_FOR_HUMAN


---

# FILE: docs/ai/control/04_STATUS_TAXONOMY.md

# 04 — STATUS TAXONOMY

## 1. Purpose

This document defines the vocabulary used to describe evidence, implementation state and task state.

The purpose is to avoid vague terms like "done", "works", "good", "solid", or "production-ready" without proof.

## 2. Evidence Confidence Labels

### VERIFIED_STATIC

The claim is supported by reading repository files.

Examples:

- file exists;
- function exists;
- migration exists;
- test file exists;
- documented code path exists.

Limit:

This does not prove runtime behavior.

### VERIFIED_RUNTIME

The claim is supported by executing a command, test, API call, migration, script or runtime observation.

Examples:

- pytest passed;
- API started;
- migration applied;
- script executed;
- database query returned expected result.

### PARTIAL

Some evidence exists, but the implementation is incomplete, limited or not universal.

Example:

A connector supports one platform path but not all required source paths.

### NO_VERIFIED

The claim cannot be verified with available evidence.

Use this when:

- no file evidence;
- no runtime evidence;
- missing credentials;
- missing DB;
- missing snapshot;
- unclear behavior;
- external dependency inaccessible.

### BROKEN

Evidence shows the feature does not work, test fails, code path errors, or implementation contradicts expected behavior.

### CONTRADICTION

Documentation, code, tests or observed behavior disagree.

Example:

README says a feature exists, but code only contains a stub.

### GATED

The claim depends on external condition.

Common gates:

- cost;
- proxies;
- credentials;
- production infra;
- browser automation;
- source access;
- private datasets;
- DB snapshot;
- rate limits;
- manual operation;
- legal review.

### ASSUMED

The executor is making a clearly marked assumption.

ASSUMED must be avoided where possible and never used as final proof.

## 3. Implementation State Labels

### BUILT

The feature has concrete implementation in code.

### WIRED

The feature is connected to an execution path.

### TESTED

The feature has relevant tests.

### RUNTIME_VALIDATED

The feature has been executed successfully.

### DOCUMENTED_ONLY

The feature appears in docs but no implementation was found.

### STUB

The feature has placeholder code but not real behavior.

### LEGACY

The feature appears old, unused, superseded or inconsistent with current architecture.

### DEAD_CODE_CANDIDATE

The code may be unused but needs proof before removal.

### INFRA_IMPLEMENTED

Infrastructure exists but product behavior may not be complete.

### PRODUCTIZED

The feature is usable by an external customer through stable interface, documentation and operational guarantees.

## 4. Task State Labels

### READY

Task can be executed now.

### IN_PROGRESS

Task is currently being executed.

### DONE

Task meets Definition of Done.

### BLOCKED

Task cannot proceed due to missing dependency, missing credentials, failing environment or unclear requirement.

### NEEDS_REVIEW

Human review is required.

### RFC_REQUIRED

Task affects critical area and requires RFC before implementation.

### WAITING_FOR_HUMAN

Task requires explicit human decision.

### FAILED_VALIDATION

Task was attempted but validation failed.

### PARTIAL_DONE

Some outputs were produced but completion criteria were not met.

## 5. Risk Severity Labels

### LOW

Limited blast radius. Documentation-only or isolated non-critical change.

### MEDIUM

Could affect behavior but not core data integrity.

### HIGH

Could affect ingestion, data quality, API behavior, scheduler, production or customer-facing output.

### CRITICAL

Could corrupt data, create false trust, break inventory lifecycle, damage production, expose secrets or invalidate commercial claims.

## 6. Production Readiness Labels

### LAB_ONLY

Useful for experimentation but not production.

### DEV_READY

Works in developer environment with manual setup.

### STAGING_CANDIDATE

Can run in controlled non-production environment.

### PRODUCTION_CANDIDATE

Has tests, observability, rollback, config, secrets handling and operational documentation.

### PRODUCTION_READY

Runtime-validated under expected load and failure conditions, with monitoring, alerting, backup/restore, rollback and operational ownership.

The executor must not mark anything PRODUCTION_READY without runtime validation.


---

# FILE: docs/ai/control/05_EVIDENCE_LEDGER.md

# 05 — EVIDENCE LEDGER

## 1. Purpose

The Evidence Ledger records proof behind technical claims.

It prevents unsupported conclusions and makes future work traceable.

Every important claim must have an evidence entry.

## 2. Evidence Entry Format

```markdown
## EVIDENCE-0001 — [Short Title]

Date:
YYYY-MM-DD

Recorded by:
AI executor / human operator

Claim:
[Exact technical claim]

Evidence Type:
- FILE
- FUNCTION
- CLASS
- MIGRATION
- TEST
- COMMAND
- LOG
- API_RESPONSE
- DB_QUERY
- DOCUMENTED_CLAIM
- RUNTIME_OBSERVATION

Evidence:
- Path:
- Function/Class:
- Approx lines:
- Command:
- Output:
- Related test:
- Related migration:

Confidence:
- VERIFIED_STATIC
- VERIFIED_RUNTIME
- PARTIAL
- NO_VERIFIED
- BROKEN
- CONTRADICTION
- GATED
- ASSUMED

Runtime Status:
- EXECUTED
- NOT_EXECUTED
- NOT_APPLICABLE
- BLOCKED

Impact:
[Why this evidence matters]

Limitations:
[What this evidence does not prove]

Related Findings:
- FINDING-XXXX

Related Tasks:
- TASK-XXXX
```

## 3. Initial Ledger

## EVIDENCE-0000 — Governance System Created

Date:
TODO

Recorded by:
AI executor

Claim:
A governance documentation structure exists under docs/ai/control.

Evidence Type:
FILE

Evidence:
- Path: docs/ai/control/

Confidence:
VERIFIED_STATIC

Runtime Status:
NOT_APPLICABLE

Impact:
Creates controlled foundation for AI-assisted development.

Limitations:
Does not prove repository correctness, tests, runtime behavior or production readiness.

Related Findings:
None yet.

Related Tasks:
Bootstrap task.

## 4. Rules

1. Do not delete evidence entries.
2. If an entry becomes obsolete, mark it superseded.
3. Do not overwrite historical evidence.
4. Use new evidence entries for new observations.
5. Separate documented claims from code evidence.
6. Separate static evidence from runtime evidence.
7. Never claim runtime verification from static evidence.


---

# FILE: docs/ai/control/06_RISK_REGISTER.md

# 06 — RISK REGISTER

## 1. Purpose

The Risk Register records technical, operational, data, legal and product risks discovered during audit or implementation.

Risks must be tracked before they become hidden assumptions.

## 2. Risk Entry Format

```markdown
## RISK-0001 — [Short Title]

Status:
OPEN / MITIGATED / ACCEPTED / TRANSFERRED / CLOSED

Severity:
LOW / MEDIUM / HIGH / CRITICAL

Category:
- ARCHITECTURE
- DATA
- INGESTION
- SCRAPING
- DEDUP
- VERIFICATION
- API
- DATABASE
- MIGRATION
- OPERATIONS
- SECURITY
- LEGAL
- COST
- PRODUCT
- COMMERCIAL
- DOCUMENTATION
- TESTING

Description:
[What the risk is]

Evidence:
- File:
- Function:
- Migration:
- Test:
- Command:
- Document:

Impact:
[What can go wrong]

Likelihood:
LOW / MEDIUM / HIGH

Blast Radius:
[What areas are affected]

Mitigation:
[How to reduce risk]

Owner:
HUMAN / AI_EXECUTOR / TBD

Related Tasks:
- TASK-XXXX

Related RFCs:
- RFC-XXXX

Review Date:
YYYY-MM-DD
```

## 3. Initial Risk Categories For Cardeep

## RISK-0000 — Runtime Not Yet Verified

Status:
OPEN

Severity:
HIGH

Category:
OPERATIONS / TESTING

Description:
Repository behavior cannot be considered verified until tests, migrations, API startup, scheduler and selected pipelines are executed.

Evidence:
- Static repository inspection only.
- Runtime commands not yet recorded in Evidence Ledger.

Impact:
Claims about working behavior may be false if runtime validation fails.

Likelihood:
MEDIUM

Blast Radius:
Entire system.

Mitigation:
Create tasks for environment bootstrap, test execution, migration validation and smoke tests.

Owner:
HUMAN + AI_EXECUTOR

Related Tasks:
TODO

Related RFCs:
None.

Review Date:
TODO

## RISK-0001 — Documentation May Be Ahead Or Behind Code

Status:
OPEN

Severity:
HIGH

Category:
DOCUMENTATION / PRODUCT

Description:
Project documentation may describe features, coverage or production status not fully matched by implementation or runtime validation.

Evidence:
TODO: audit README, PLAN, PROGRESO, RUNBOOK, docs/architecture against code.

Impact:
Can mislead development priorities, product claims and commercial positioning.

Likelihood:
HIGH

Blast Radius:
Architecture, product, sales, roadmap.

Mitigation:
Create documentation-vs-code audit table and mark each claim VERIFIED, PARTIAL, NO_VERIFIED, CONTRADICTION, ASPIRATIONAL, BROKEN or GATED.

Owner:
AI_EXECUTOR

Related Tasks:
TODO

Related RFCs:
None.

Review Date:
TODO

## RISK-0002 — Critical Data Lifecycle Corruption

Status:
OPEN

Severity:
CRITICAL

Category:
INGESTION / DELTA / DATA

Description:
Errors in ingestion, delta detection, gone guard or deduplication could mark live listings as gone, duplicate vehicles, overmerge vehicles or serve stale data.

Evidence:
TODO: audit pipeline/ingest.py, pipeline/delta.py, gone guard, dedup modules and tests.

Impact:
Invalid inventory data, false availability, commercial trust failure.

Likelihood:
UNKNOWN

Blast Radius:
Core product.

Mitigation:
Audit lifecycle modules, add tests before patching, require RFC for behavior changes.

Owner:
AI_EXECUTOR + HUMAN

Related Tasks:
TODO

Related RFCs:
Required before critical behavior changes.

Review Date:
TODO

## RISK-0003 — Scraping Claims May Be Gated

Status:
OPEN

Severity:
HIGH

Category:
SCRAPING / COST / LEGAL / OPERATIONS

Description:
Full source coverage may depend on proxies, sessions, browser automation, rate limits, source access, anti-bot evasion, credentials or paid infrastructure.

Evidence:
TODO: audit pipeline/sources, pipeline/platform, requirements, runbooks and progress docs.

Impact:
System may not drain inventories reliably or legally at intended scale.

Likelihood:
HIGH

Blast Radius:
Coverage, cost, product claims.

Mitigation:
Classify each source as WORKING_STATIC, TESTED_RUNTIME, PARTIAL, GATED, BROKEN or DOCUMENTED_ONLY.

Owner:
AI_EXECUTOR

Related Tasks:
TODO

Related RFCs:
Required for proxy/browser/Tier-1 changes.

Review Date:
TODO


---

# FILE: docs/ai/control/07_DECISION_LOG.md

# 07 — DECISION LOG

## 1. Purpose

The Decision Log records architectural, technical, product and operational decisions.

It prevents repeated debates and preserves reasoning.

## 2. Decision Entry Format

```markdown
## DECISION-0001 — [Short Title]

Date:
YYYY-MM-DD

Status:
PROPOSED / ACCEPTED / REJECTED / SUPERSEDED

Context:
[Why this decision exists]

Decision:
[What was decided]

Rationale:
[Why this was chosen]

Alternatives Considered:
1.
2.
3.

Consequences:
Positive:
-

Negative:
-

Risks:
-

Evidence:
-

Related Tasks:
- TASK-XXXX

Related RFCs:
- RFC-XXXX

Supersedes:
None / DECISION-XXXX
```

## 3. Initial Decisions

## DECISION-0000 — AI Work Must Be Governed By docs/ai

Date:
TODO

Status:
ACCEPTED

Context:
Cardeep is complex enough that open-ended AI code changes create unacceptable risk.

Decision:
All AI-assisted development must be governed through docs/ai control documents, task queue, findings, evidence ledger and RFCs.

Rationale:
This creates traceability, safer execution and controlled scope.

Alternatives Considered:
1. Direct prompts without governance.
2. One large blueprint prompt.
3. Manual-only development.

Consequences:
Positive:
- Safer AI execution.
- Better audit trail.
- Less risk of destructive changes.
- Easier human review.

Negative:
- Slower initial setup.
- More documentation overhead.

Risks:
- Governance docs may become stale if not updated.
- Executor may ignore rules if prompts are weak.

Evidence:
- Mission contract and operating rules.

Related Tasks:
Bootstrap tasks.

Related RFCs:
None.

Supersedes:
None.


---

# FILE: docs/ai/control/08_CHANGE_CONTROL.md

# 08 — CHANGE CONTROL

## 1. Purpose

This document defines how changes are proposed, approved, implemented and validated.

The purpose is to prevent uncontrolled modifications to critical parts of Cardeep.

## 2. Change Classes

## CLASS 0 — Documentation Control

Examples:
- docs/ai updates;
- audit reports;
- findings;
- task queue;
- evidence ledger.

Approval:
Not required if task allows it.

Risk:
LOW

Validation:
git diff --name-only

## CLASS 1 — Tests Only

Examples:
- add unit tests;
- add fixtures;
- add regression tests.

Approval:
Task-level approval required.

Risk:
LOW to MEDIUM

Validation:
pytest targeted tests

Restriction:
No production logic changes.

## CLASS 2 — Safe Patch

Examples:
- small bug fix;
- small parser correction;
- non-critical guard;
- typo affecting non-critical behavior.

Approval:
Task-level approval required.

Risk:
MEDIUM

Validation:
targeted tests + relevant smoke command

Restriction:
No schema, API contract, ingest/delta/dedup/verification/scheduler/Tier-1 behavior changes unless explicitly scoped.

## CLASS 3 — Critical Behavior Change

Examples:
- ingestion lifecycle;
- delta classification;
- gone detection;
- dedup/identity;
- verification/VAM;
- scheduler orchestration;
- API response contract;
- scraper behavior at scale.

Approval:
RFC required + explicit human approval.

Risk:
HIGH to CRITICAL

Validation:
tests + smoke + rollback plan

## CLASS 4 — Schema/Migration Change

Examples:
- table changes;
- indexes;
- constraints;
- materialized views;
- enum/state changes;
- data migration.

Approval:
RFC required + explicit human approval.

Risk:
HIGH to CRITICAL

Validation:
migration apply + rollback or mitigation + tests

## CLASS 5 — Production/Infrastructure Change

Examples:
- Docker;
- deploy;
- secrets;
- workers;
- scheduler in production;
- monitoring;
- backups;
- scaling;
- rate limits.

Approval:
RFC required + explicit human approval.

Risk:
HIGH to CRITICAL

Validation:
environment-specific.

## 3. Change Process

1. Identify class.
2. Check task mode.
3. Check allowed_files/forbidden_files.
4. Gather evidence.
5. If class >= 3, create RFC.
6. Wait for approval.
7. Implement minimal change.
8. Run validation.
9. Record evidence.
10. Update findings/risk/task status.
11. Report diff.

## 4. Mandatory Stop Conditions

Stop immediately if:

- forbidden file must be modified;
- critical module requires change but no RFC exists;
- tests fail unexpectedly;
- migration history is unclear;
- command requires secrets not provided;
- source access requires credentials/proxies;
- legal/compliance uncertainty appears;
- task scope is too broad;
- repository state is dirty in unrelated files.

## 5. Rollback Expectations

Every change must be reversible.

For docs:
- revert file changes.

For tests:
- revert test files.

For code:
- revert patch commit or diff.

For migrations:
- require explicit rollback or mitigation plan.

For production:
- require deployment rollback procedure.

No critical change is acceptable without a rollback story.


---

# FILE: docs/ai/control/09_GIT_POLICY.md

# 09 — GIT POLICY

## 1. Purpose

This document defines safe Git behavior for AI-assisted work.

## 2. Before Work

Before modifying files, run:

```bash
git status --short
```

Record whether the working tree is clean.

If the working tree contains unrelated human changes, do not overwrite them.

## 3. During Work

The executor must:

- avoid broad formatting changes;
- avoid unrelated edits;
- avoid deleting files;
- avoid moving files unless task explicitly requires it;
- keep diffs small;
- check diff before reporting completion.

## 4. After Work

Run:

```bash
git diff --name-only
git diff --stat
```

If tests were required, run targeted tests.

If docs-only, report that no runtime validation was required.

## 5. Forbidden Git Operations

The AI executor must not run:

```bash
git reset --hard
git clean -fd
git push
git checkout -- .
git rebase
git merge
git commit
```

unless explicitly instructed by the human operator.

## 6. Commit Policy

The AI executor should not commit by default.

The human operator decides when to commit.

If asked to suggest commit messages, use:

```text
type(scope): concise summary
```

Examples:

```text
docs(ai): add governance control framework
test(delta): add regression coverage for gone transitions
fix(api): correct dealer stats null handling
```

## 7. Diff Review Requirement

Every task report must include:

- changed files;
- why each file changed;
- whether change was allowed;
- validation run;
- risk remaining.


---

# FILE: docs/ai/control/10_REPORTING_PROTOCOL.md

# 10 — REPORTING PROTOCOL

## 1. Purpose

This document defines how the AI executor must report work.

Reports must be concise but complete.

## 2. Required Task Completion Report

Every task must end with:

```markdown
# Task Report — TASK-XXXX

## Status
DONE / PARTIAL_DONE / BLOCKED / NEEDS_REVIEW / RFC_REQUIRED / FAILED_VALIDATION

## Mode
AUDIT_ONLY / TEST_ONLY / SAFE_PATCH / RFC_REQUIRED / MIGRATION_REQUIRED / PRODUCTION_GATE / PRODUCT_GATE

## Scope Followed
YES / NO

## Files Inspected
-

## Files Modified
-

## Forbidden Files Touched
YES / NO

## Evidence Added
-

## Findings Added
-

## Risks Added
-

## Commands Executed
-

## Validation Result
PASSED / FAILED / NOT_RUN / NOT_APPLICABLE

## Remaining Unknowns
-

## Next Recommended Task
-
```

## 3. Audit Report Requirements

Audit reports must include:

1. module purpose;
2. entrypoints;
3. inputs;
4. outputs;
5. data structures/tables touched;
6. dependencies;
7. runtime requirements;
8. error handling;
9. tests existing;
10. tests missing;
11. risks;
12. contradictions;
13. production readiness score;
14. recommendations.

## 4. Failure Reporting

Failures must not be hidden.

Use:

```markdown
## Failure

Command:
[command]

Observed Result:
[output]

Expected Result:
[expected]

Impact:
[what this blocks]

Next Action:
[recommended]
```

## 5. No Marketing Language

Reports must not use vague claims such as:

- robust;
- enterprise-grade;
- production-ready;
- complete;
- scalable;
- secure;
- reliable;

unless proven with evidence.

Preferred language:

- VERIFIED_STATIC;
- VERIFIED_RUNTIME;
- PARTIAL;
- GATED;
- NO_VERIFIED;
- BROKEN;
- CONTRADICTION.

## 6. Executive Summary Rule

Every large report may include an executive summary, but it cannot replace evidence.

The summary must point to detailed findings.


---

# FILE: docs/ai/control/11_NO_GO_ZONES.md

# 11 — NO-GO ZONES

## 1. Purpose

This document identifies areas that must not be modified casually.

## 2. Absolute No-Go Without Approval

The executor must not modify the following without explicit task approval:

- migrations/
- pipeline/ingest.py
- pipeline/delta.py
- pipeline/evict.py
- pipeline/verify.py
- pipeline/verify_ttl.py
- pipeline/identity/
- dedup modules
- pipeline/ops/scheduler.py
- services/api/ routers and response contracts
- pipeline/sources/ Tier-1 connectors
- pipeline/platform/
- requirements.txt
- docker-compose.yml
- deployment files
- production scripts
- authentication/security files
- pricing/product claims
- public README/PLAN/PROGRESO/RUNBOOK

## 3. RFC No-Go Areas

The following require RFC before implementation:

### 3.1. Database

- schema changes;
- index changes;
- constraints;
- table drops;
- materialized views;
- data migrations.

### 3.2. Data Lifecycle

- new listing lifecycle states;
- gone logic;
- last_seen logic;
- event generation;
- vehicle identity;
- dealer identity;
- dedup scoring.

### 3.3. Verification

- quorum;
- TTL;
- trust states;
- source health;
- ledger;
- verdict logic;
- alert thresholds.

### 3.4. Scraping

- proxies;
- browser automation;
- anti-bot handling;
- rate limits;
- source-specific bypass logic;
- session handling;
- fingerprinting;
- paid scraping infra.

### 3.5. API

- response schemas;
- endpoint semantics;
- filtering behavior;
- auth/rate limit behavior;
- cache behavior.

### 3.6. Production

- deploy topology;
- scheduler behavior;
- worker concurrency;
- secrets;
- logging;
- metrics;
- alerting;
- backups;
- scaling.

## 4. No-Go Due To Legal/Compliance Risk

The executor must not implement or suggest:

- bypassing access controls;
- evading explicit technical restrictions;
- credential sharing;
- scraping behind login without authorization;
- ignoring robots/legal constraints;
- using leaked/private datasets;
- storing personal data without purpose/legal review.

For scraping legality, mark LEGAL_REVIEW_REQUIRED where uncertain.

## 5. No-Go Due To Product Risk

The executor must not update public-facing claims to say:

- 100% coverage;
- real-time complete inventory;
- verified market truth;
- production-ready;
- enterprise-grade;
- legally safe;
- competitor-equivalent;

unless runtime evidence and product approval exist.


---

# FILE: docs/ai/control/12_HUMAN_APPROVAL_GATES.md

# 12 — HUMAN APPROVAL GATES

## 1. Purpose

Some changes are too risky for autonomous execution.

This document defines when the AI executor must stop and request human approval.

## 2. Approval Required

Human approval is required for:

1. modifying migrations;
2. modifying ingest lifecycle;
3. modifying delta/gone behavior;
4. modifying dedup/identity logic;
5. modifying verification/trust logic;
6. modifying scheduler orchestration;
7. modifying API contracts;
8. modifying production/deploy configuration;
9. adding dependencies;
10. introducing browser scraping/proxies;
11. changing secrets handling;
12. deleting files;
13. large refactors;
14. public documentation claim changes;
15. product/commercial positioning changes.

## 3. Approval Request Format

When approval is needed, create a report:

```markdown
# Approval Request — [Title]

## Change Requested
[What needs to change]

## Why Approval Is Required
[Which gate is triggered]

## Evidence
[Files/functions/tests/docs]

## Risk
[What could go wrong]

## Alternatives
1.
2.
3.

## Recommendation
[Preferred option]

## Validation Plan
[How to verify]

## Rollback Plan
[How to revert]

## Decision Needed
APPROVE / REJECT / REQUEST_MORE_INFO
```

## 4. No Implied Approval

The following are not approval:

- vague positive comments;
- "continue";
- "sounds good";
- "do what you think";
- "fix it";
- "make it production".

Approval must explicitly mention the task or RFC.

Example valid approval:

```text
Approved: RFC-003. Implement Option B only. Do not modify migrations beyond 0073. Run pytest tests/test_ingest_gone.py.
```

## 5. Emergency Stop

If a task reveals possible data corruption, secret exposure, destructive migration risk, legal scraping risk or production breakage, stop immediately and mark task CRITICAL_NEEDS_REVIEW.


---

# FILE: docs/ai/loops/LOOP_001_STATIC_AUDIT.md

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


---

# FILE: docs/ai/loops/LOOP_002_TEST_HARDENING.md

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


---

# FILE: docs/ai/loops/LOOP_003_SAFE_PATCHES.md

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


---

# FILE: docs/ai/loops/LOOP_004_PRODUCTION_READINESS.md

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


---

# FILE: docs/ai/loops/LOOP_005_PRODUCTIZATION.md

# LOOP 005 — PRODUCTIZATION

## Purpose

Convert technical reality into a sellable, honest product boundary.

## Allowed Task Modes

- PRODUCT_GATE
- RFC_REQUIRED
- AUDIT_ONLY

## Forbidden

- editing public marketing claims without approval;
- claiming 100% coverage without evidence;
- claiming real-time without runtime proof;
- claiming legal safety without review;
- claiming production readiness without production evidence;
- building frontend before API/data quality is proven.

## Instruction For Claude Code

```text
/loop
Read:
- docs/ai/audits/11_PRODUCT_AUDIT.md
- docs/ai/reports/PRODUCTIZATION_GAP_REPORT.md
- docs/ai/reports/MODULE_SCORECARD.md
- docs/ai/rfcs/RFC_PRODUCT_MVP.md if it exists
- docs/ai/tasks/TASK_QUEUE.yml

Execute the next READY productization task.

Rules:
- Map every product claim to evidence.
- Mark unsupported claims as NO_VERIFIED or GATED.
- Define what can be sold safely now.
- Define what must not be promised.
- Do not edit public docs unless a task explicitly allows it.
- If commercial decision is required, stop and request human decision.

At the end:
- update productization report;
- update task queue;
- update risk register;
- report remaining blockers.
```


---

# PROMPT FILE: docs/ai/prompts/00_bootstrap/00_goal_create_governance_structure.txt

```text
/goal
Actúa como auditor técnico institucional y ejecutor controlado dentro del repositorio Cardeep.

Objetivo de esta tarea:
Crear un sistema de gobierno interno para trabajar sobre el repo sin cambios destructivos.

Reglas obligatorias:
- No modifiques código productivo.
- No modifiques migraciones.
- No ejecutes refactors.
- No borres archivos.
- No cambies dependencias.
- No edites README/PLAN/PROGRESO todavía.
- Crea únicamente documentación de control dentro de docs/ai/.
- Toda afirmación técnica debe marcarse como VERIFIED_STATIC, VERIFIED_RUNTIME, PARTIAL, NO_VERIFIED, BROKEN, CONTRADICTION o GATED.
- Si no puedes verificar algo, escribe NO_VERIFIED.
- Si detectas riesgo, regístralo.
- Si una tarea requiere tocar ingest, delta, dedup, verify, scheduler, API contract, migrations o scraping Tier-1, márcala como RFC_REQUIRED.

Crea esta estructura:
docs/ai/control/
docs/ai/tasks/
docs/ai/audits/
docs/ai/rfcs/
docs/ai/findings/
docs/ai/loops/
docs/ai/reports/

Crea estos archivos iniciales:
docs/ai/control/00_MISSION_CONTRACT.md
docs/ai/control/01_OPERATING_RULES.md
docs/ai/control/02_EXECUTION_MODES.md
docs/ai/control/03_DEFINITION_OF_DONE.md
docs/ai/control/04_STATUS_TAXONOMY.md
docs/ai/control/05_EVIDENCE_LEDGER.md
docs/ai/control/06_RISK_REGISTER.md
docs/ai/control/07_DECISION_LOG.md
docs/ai/control/08_CHANGE_CONTROL.md
docs/ai/control/09_GIT_POLICY.md
docs/ai/control/10_REPORTING_PROTOCOL.md
docs/ai/control/11_NO_GO_ZONES.md
docs/ai/control/12_HUMAN_APPROVAL_GATES.md

Entrega:
- Lista de archivos creados.
- Confirmación de que no se tocó código productivo.
- Resultado de git diff --name-only.
```


---

# PROMPT FILE: docs/ai/prompts/00_bootstrap/01_goal_fill_governance_docs.txt

```text
/goal
Rellena los documentos de gobierno en docs/ai/control/ usando el contenido institucional proporcionado por el operador humano.

Reglas:
- Solo puedes modificar docs/ai/control/.
- No modifiques pipeline/, services/, migrations/, tests/, scripts/, requirements.txt, docker-compose.yml, README.md, PLAN.md, PROGRESO.md ni RUNBOOK.md.
- Mantén los documentos en Markdown.
- No inventes estado real del repo.
- No afirmes que algo funciona si no se ha ejecutado.
- Diferencia siempre entre evidencia estática y evidencia runtime.
- Añade secciones TODO donde falte información real.
- Si un documento referencia tareas futuras, no las ejecutes.

Validación:
- Ejecuta git diff --name-only.
- El diff solo debe contener docs/ai/control/*.
- Reporta cualquier desviación.

Entrega:
1. Archivos modificados.
2. Confirmación de que solo se tocó docs/ai/control/.
3. Riesgos detectados.
4. Próximo paso recomendado.
```


---

# PROMPT FILE: docs/ai/prompts/01_loops/00_loop_master_next_ready_task.txt

```text
/loop
Lee:
- docs/ai/CARDEEP_MASTER_BLUEPRINT.md
- docs/ai/control/00_MISSION_CONTRACT.md
- docs/ai/control/01_OPERATING_RULES.md
- docs/ai/control/02_EXECUTION_MODES.md
- docs/ai/control/03_DEFINITION_OF_DONE.md
- docs/ai/tasks/TASK_QUEUE.yml

Ejecuta únicamente la siguiente tarea con status READY.

Una sola tarea por iteración.
Respeta mode, allowed_files, forbidden_files, validation y acceptance.
Actualiza findings, evidence ledger, risk register y TASK_QUEUE.yml.
No avances si aparece RFC_REQUIRED, NEEDS_REVIEW o FAILED_VALIDATION.
No modifiques código productivo salvo que la tarea lo permita explícitamente.
```


---

# PROMPT FILE: docs/ai/prompts/01_loops/loop_001_static_audit.txt

```text
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
```


---

# PROMPT FILE: docs/ai/prompts/01_loops/loop_002_test_hardening.txt

```text
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
```


---

# PROMPT FILE: docs/ai/prompts/01_loops/loop_003_safe_patches.txt

```text
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
```


---

# PROMPT FILE: docs/ai/prompts/01_loops/loop_004_production_readiness.txt

```text
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
```


---

# PROMPT FILE: docs/ai/prompts/01_loops/loop_005_productization.txt

```text
# LOOP 005 — PRODUCTIZATION

## Purpose

Convert technical reality into a sellable, honest product boundary.

## Allowed Task Modes

- PRODUCT_GATE
- RFC_REQUIRED
- AUDIT_ONLY

## Forbidden

- editing public marketing claims without approval;
- claiming 100% coverage without evidence;
- claiming real-time without runtime proof;
- claiming legal safety without review;
- claiming production readiness without production evidence;
- building frontend before API/data quality is proven.

## Instruction For Claude Code

```text
/loop
Read:
- docs/ai/audits/11_PRODUCT_AUDIT.md
- docs/ai/reports/PRODUCTIZATION_GAP_REPORT.md
- docs/ai/reports/MODULE_SCORECARD.md
- docs/ai/rfcs/RFC_PRODUCT_MVP.md if it exists
- docs/ai/tasks/TASK_QUEUE.yml

Execute the next READY productization task.

Rules:
- Map every product claim to evidence.
- Mark unsupported claims as NO_VERIFIED or GATED.
- Define what can be sold safely now.
- Define what must not be promised.
- Do not edit public docs unless a task explicitly allows it.
- If commercial decision is required, stop and request human decision.

At the end:
- update productization report;
- update task queue;
- update risk register;
- report remaining blockers.
```
```


---

# PROMPT FILE: docs/ai/prompts/02_audits/00_goal_repo_map_audit.txt

```text
/goal
Audit the repository structure statically.

Read:
- README.md
- PLAN.md
- PROGRESO.md
- RUNBOOK.md
- docs/
- pipeline/
- services/
- migrations/
- scripts/
- tests/
- .github/workflows/
- docker-compose.yml
- requirements.txt
- requirements-dev.txt
- pytest.ini

Do not modify code, tests, migrations, dependencies, README, PLAN, PROGRESO or RUNBOOK.

Create:
- docs/ai/audits/00_REPO_MAP.md

The report must include:
1. top-level folder map;
2. module map;
3. entrypoint map;
4. config/env map;
5. test map;
6. migration map;
7. scripts map;
8. API map;
9. ops/scheduler map;
10. unknowns;
11. suspected legacy/dead code candidates;
12. critical modules;
13. immediate risks.

Every important statement must cite file path evidence.
Mark runtime behavior as NO_VERIFIED_RUNTIME unless executed.
```


---

# PROMPT FILE: docs/ai/prompts/02_audits/01_goal_runtime_baseline.txt

```text
/goal
Establish a runtime baseline without repairing anything.

Rules:
- Do not modify files.
- Do not install new dependencies unless already part of documented setup and explicitly safe.
- Do not change code.
- Do not change tests.
- Do not change migrations.
- Do not edit configs.
- Record exact command outputs.

Attempt these commands if environment allows:
- python --version
- pip --version
- python -m pytest --collect-only -q
- python -m pytest -q
- docker compose config
- docker compose up -d cardeep-pg
- python scripts/migrate.py up
- uvicorn services.api.main:app --host 127.0.0.1 --port 8090
- python -m pipeline.ops.scheduler --help

Create:
- docs/ai/reports/RUNTIME_BASELINE.md

For each command record:
- command;
- result;
- output summary;
- pass/fail;
- blocker;
- impact;
- next task.

Do not fix failures in this task.
```


---

# PROMPT FILE: docs/ai/prompts/02_audits/02_goal_docs_vs_code_audit.txt

```text
/goal
Audit documentation claims against code evidence.

Read:
- README.md
- PLAN.md
- PROGRESO.md
- RUNBOOK.md
- docs/
- pipeline/
- services/
- migrations/
- tests/
- scripts/

Do not edit source documents.
Do not edit production code.
Do not edit tests.

Create:
- docs/ai/audits/DOCS_VS_CODE_AUDIT.md
- docs/ai/findings/CONTRADICTIONS.md
- docs/ai/findings/GATED.md

Build a table:
Documented Promise | Source Document | Code Evidence | Runtime Evidence | Verdict | Risk | Next Task

Classify these claims:
- 100% points of sale;
- full inventory;
- real-time inventory;
- complete delta;
- API by entity;
- API by geo;
- recipe versioning;
- raw eviction;
- Tier-1 separation;
- VAM quorum;
- Deep Ledger;
- Inquisition;
- Gestionador;
- source health;
- scheduler;
- production readiness;
- commercial readiness.

Allowed verdicts:
VERIFIED_STATIC, VERIFIED_RUNTIME, PARTIAL, NO_VERIFIED, CONTRADICTION, ASPIRATIONAL, BROKEN, GATED.
```


---

# PROMPT FILE: docs/ai/prompts/02_audits/03_goal_ingest_audit.txt

```text
/goal
Audit pipeline ingestion lifecycle statically.

Read:
- pipeline/ingest.py
- pipeline/harvest_dealer.py
- pipeline/recipe.py
- pipeline/delta.py
- migrations/
- tests/

Do not modify code.
Do not modify tests.
Do not modify migrations.

Create:
- docs/ai/audits/03_INGEST_AUDIT.md

Report sections:
1. Purpose.
2. Entrypoints.
3. Main functions/classes.
4. Input data structures.
5. Output data structures.
6. Tables touched.
7. Entity/dealer upsert behavior.
8. Vehicle upsert behavior.
9. Event generation.
10. last_seen behavior.
11. Gone behavior.
12. Alert behavior.
13. Verification/VAM interaction.
14. Idempotency.
15. Error handling.
16. Silent failure risks.
17. Tests existing.
18. Tests missing.
19. Production readiness score 0-10.
20. Required next tasks.

Any recommendation to change behavior must be RFC_REQUIRED.
```


---

# PROMPT FILE: docs/ai/prompts/02_audits/04_goal_delta_gone_audit.txt

```text
/goal
Audit delta and gone behavior statically.

Read:
- pipeline/delta.py
- pipeline/delta_guard.py
- pipeline/evict.py
- pipeline/ingest.py
- tests/
- migrations/

Do not modify code.
Do not modify tests.
Do not modify migrations.

Create:
- docs/ai/audits/04_DELTA_GONE_AUDIT.md

Report:
1. Delta model.
2. Events detected.
3. NEW detection.
4. PRICE_CHANGE detection.
5. KM_CHANGE detection.
6. PHOTO_CHANGE detection.
7. GONE detection.
8. Append-only connector behavior.
9. False gone protection.
10. Re-ingest/idempotency.
11. Event duplication risks.
12. Tests existing.
13. Tests missing.
14. Data corruption risks.
15. Production readiness score.
16. RFCs required.

Do not implement fixes.
```


---

# PROMPT FILE: docs/ai/prompts/02_audits/05_goal_verification_vam_audit.txt

```text
/goal
Audit the verification and trust stack.

Read:
- pipeline/verify.py
- pipeline/verify_ttl.py
- pipeline/inquisition/
- pipeline/gestionador/
- docs/architecture/10-VERIFICATION-STACK.md
- migrations/
- tests/

Do not modify code.
Do not modify tests.
Do not modify migrations.

Create:
- docs/ai/audits/05_VERIFICATION_AUDIT.md

Report:
1. Trust model.
2. Verdict states.
3. Quorum logic.
4. Source independence.
5. TTL.
6. REFUTED behavior.
7. TRUSTWORTHY behavior.
8. UNVERIFIED behavior.
9. Zero-count certification risk.
10. Deep Ledger implementation status.
11. Inquisition implementation status.
12. Gestionador implementation status.
13. Source health interaction.
14. API exposure.
15. Tests existing.
16. Tests missing.
17. Production readiness score.
18. Required RFCs.

Mark documentation-only claims as DOCUMENTED_CLAIM.
```


---

# PROMPT FILE: docs/ai/prompts/02_audits/06_goal_dedup_identity_audit.txt

```text
/goal
Audit identity and deduplication.

Read:
- pipeline/ids.py
- pipeline/identity/
- all pipeline files with dedup in name
- migrations/
- tests/

Do not modify code.
Do not modify tests.
Do not modify migrations.

Create:
- docs/ai/audits/DEDUP_IDENTITY_AUDIT.md

Report:
1. Dealer identity.
2. Entity identity.
3. Source identity.
4. Vehicle identity.
5. Canonical IDs.
6. Cluster model.
7. Dedup scoring.
8. Blocking keys.
9. Merge criteria.
10. Overmerge risks.
11. Undermerge risks.
12. Unmerge/recovery support.
13. Tests existing.
14. Tests missing.
15. Production readiness score.
16. Required next tasks.

Any threshold/merge logic change must be RFC_REQUIRED.
```


---

# PROMPT FILE: docs/ai/prompts/02_audits/07_goal_source_connector_matrix.txt

```text
/goal
Create a complete source connector matrix.

Read:
- pipeline/sources/
- pipeline/platform/
- countries/ES/
- scripts/
- tests/
- requirements.txt
- docs/

Do not modify connector code.
Do not modify tests.
Do not modify dependencies.

Create:
- docs/ai/audits/06_SCRAPING_SOURCES_AUDIT.md
- docs/ai/audits/SOURCE_MATRIX.md

For each source/connector include:
- source name;
- type;
- module path;
- fetch method;
- parser method;
- pagination;
- JS/browser requirement;
- auth requirement;
- proxy requirement;
- retries;
- backoff;
- block detection;
- rate limiting;
- tests;
- runtime status;
- status classification;
- production score;
- legal/compliance note.

Status values:
VERIFIED_STATIC, VERIFIED_RUNTIME, PARTIAL, BROKEN, GATED, DOCUMENTED_ONLY, NO_VERIFIED.

Do not claim any source drains completely unless runtime evidence exists.
```


---

# PROMPT FILE: docs/ai/prompts/02_audits/08_goal_api_audit.txt

```text
/goal
Audit the FastAPI serving layer.

Read:
- services/api/
- tests/
- docs/runbook/
- README.md

Do not modify API code.
Do not modify tests.
Do not modify public docs.

Create:
- docs/ai/audits/07_API_AUDIT.md

Report:
1. API entrypoint.
2. Routers.
3. Endpoints.
4. Request parameters.
5. Response schemas.
6. DB dependencies.
7. Pagination.
8. Filtering.
9. Caching.
10. Rate limiting.
11. Error handling.
12. Trust/verification exposure.
13. Data freshness exposure.
14. Security/auth.
15. Performance risks.
16. Tests existing.
17. Tests missing.
18. Production readiness score.
19. Product readiness score.

Any API contract change must be RFC_REQUIRED.
```


---

# PROMPT FILE: docs/ai/prompts/02_audits/09_goal_scheduler_ops_audit.txt

```text
/goal
Audit scheduler and operational workflows.

Read:
- pipeline/ops/
- ops/
- scripts/
- docs/runbook/
- tests/

Do not modify code.
Do not modify scripts.
Do not modify configs.

Create:
- docs/ai/audits/08_SCHEDULER_OPS_AUDIT.md

Report:
1. Scheduler entrypoints.
2. Jobs.
3. Job intervals.
4. Locks.
5. Heartbeats.
6. Retries.
7. Backoff.
8. Failure recovery.
9. Alerts.
10. Source health.
11. Coverage gates.
12. Watchdogs.
13. Manual repair scripts.
14. Concurrency.
15. DB load risk.
16. Tests existing.
17. Tests missing.
18. Production readiness score.

Any orchestration change must be RFC_REQUIRED.
```


---

# PROMPT FILE: docs/ai/prompts/02_audits/10_goal_migration_data_model_audit.txt

```text
/goal
Audit migrations and reconstruct the data model.

Read:
- migrations/
- scripts/migrate.py
- README.md
- RUNBOOK.md
- docs/runbook/
- pipeline/
- services/api/

Do not modify migrations.
Do not modify code.
Do not modify docs outside docs/ai.

Create:
- docs/ai/audits/02_DATA_MODEL_AUDIT.md
- docs/ai/audits/MIGRATIONS_AUDIT.md

Report:
1. Migration order.
2. Latest migration.
3. Runbook mismatch.
4. Tables.
5. Columns.
6. Indexes.
7. Constraints.
8. Foreign keys.
9. Views/materialized views.
10. Critical state fields.
11. Event model.
12. Verification model.
13. Dedup/cluster model.
14. API serving model.
15. Growth risks.
16. Missing indexes.
17. Missing constraints.
18. Corruption risks.
19. Rollback status.
20. Production readiness score.

Any schema change must be MIGRATION_REQUIRED and RFC_REQUIRED.
```


---

# PROMPT FILE: docs/ai/prompts/02_audits/11_goal_test_ci_audit.txt

```text
/goal
Audit tests and CI.

Read:
- tests/
- .github/workflows/
- pytest.ini
- requirements-dev.txt
- requirements.txt

Do not modify tests.
Do not modify CI.
Do not modify dependencies.

Create:
- docs/ai/audits/09_TEST_COVERAGE_AUDIT.md

If environment allows, run:
- python -m pytest --collect-only -q

Report:
1. Test files by subsystem.
2. Unit tests.
3. Integration tests.
4. DB tests.
5. API tests.
6. Source connector tests.
7. Dedup tests.
8. Delta/gone tests.
9. Verification tests.
10. Scheduler tests.
11. CI workflows.
12. Collect-only status.
13. Known failures.
14. Missing critical tests.
15. Recommended TEST_ONLY tasks.

Do not fix tests in this task.
```


---

# PROMPT FILE: docs/ai/prompts/02_audits/12_goal_production_gap_audit.txt

```text
/goal
Create production readiness audit.

Read:
- Dockerfile
- docker-compose.yml
- .env.example
- services/api/
- pipeline/ops/
- scripts/
- ops/
- docs/runbook/
- README.md

Do not modify deployment files.
Do not modify code.
Do not modify env files.

Create:
- docs/ai/audits/10_PRODUCTION_AUDIT.md
- docs/ai/reports/PRODUCTION_GAP_REPORT.md

Report:
1. Deployment model.
2. API process.
3. Worker/scheduler process.
4. PostgreSQL.
5. Migrations.
6. Secrets.
7. Logs.
8. Metrics.
9. Alerts.
10. Backups.
11. Restore.
12. Rate limits.
13. Concurrency.
14. Source health.
15. Failure recovery.
16. Scaling vertical.
17. Scaling horizontal.
18. Cost risks.
19. Legal/compliance gates.
20. Cheap production architecture.
21. Serious production architecture.
22. Production readiness score.

Do not implement production changes.
```


---

# PROMPT FILE: docs/ai/prompts/02_audits/13_goal_product_startup_audit.txt

```text
/goal
Audit Cardeep as product/startup.

Read:
- README.md
- PLAN.md
- PROGRESO.md
- docs/
- services/api/
- portal/
- web/
- docs/ai/audits/
- docs/ai/reports/MODULE_SCORECARD.md if exists

Do not modify public docs.
Do not modify API.
Do not modify frontend.

Create:
- docs/ai/audits/11_PRODUCT_AUDIT.md
- docs/ai/reports/PRODUCTIZATION_GAP_REPORT.md

Report:
1. What Cardeep is today.
2. What Cardeep promises to be.
3. What is actually sellable.
4. What is not sellable.
5. Target customers.
6. Competitor category.
7. Data asset value.
8. API value.
9. SaaS readiness.
10. Internal tool value.
11. Coverage claim risk.
12. Freshness claim risk.
13. Verification claim risk.
14. Legal/compliance risk.
15. Pricing hypothesis.
16. MVP boundary.
17. Money path.
18. Self-deception path.
19. Decision: CONTINUE / CUT_SCOPE / PIVOT / REBUILD.
20. Next 10 actions.

Use brutal, evidence-based language.
No optimism without evidence.
```


---

# PROMPT FILE: docs/ai/prompts/03_rfc/00_goal_rfc_critical_task_template.txt

```text
/goal
Ejecuta una tarea crítica bajo control RFC.

Tarea:
[PEGAR ID Y DESCRIPCIÓN DE LA TAREA]

Reglas:
- No implementes todavía.
- Primero crea un RFC en docs/ai/rfcs/.
- El RFC debe incluir:
  - problema;
  - evidencia;
  - comportamiento actual;
  - cambio propuesto;
  - alternativas;
  - riesgos;
  - impacto en datos;
  - impacto en migraciones;
  - impacto en API;
  - impacto en tests;
  - plan de validación;
  - plan de rollback;
  - archivos afectados;
  - criterio de aceptación;
  - decisión requerida.

No modifiques código productivo hasta que el RFC sea aprobado explícitamente por el operador humano.

Entrega:
- Ruta del RFC creado.
- Resumen de riesgos.
- Decisión humana requerida.
- Confirmación de que no se tocó código productivo.
```


---

# PROMPT FILE: docs/ai/prompts/03_rfc/01_goal_rfc_ingest_delta_hardening.txt

```text
/goal
Create an RFC for ingest, delta and gone hardening.

Read:
- docs/ai/CARDEEP_MASTER_BLUEPRINT.md
- docs/ai/control/*
- docs/ai/audits/03_INGEST_AUDIT.md
- docs/ai/audits/04_DELTA_GONE_AUDIT.md
- docs/ai/findings/FINDINGS.md
- docs/ai/control/06_RISK_REGISTER.md

Do not modify production code.
Do not modify tests.
Do not modify migrations.

Create:
- docs/ai/rfcs/RFC_INGEST_DELTA_HARDENING.md

The RFC must cover:
- current ingest lifecycle;
- current delta behavior;
- gone guard;
- false gone risks;
- event generation;
- idempotency;
- append-only connector behavior;
- tests required before implementation;
- rollback plan;
- exact files that would be touched;
- exact files that must not be touched.

End by requesting human approval.
```


---

# PROMPT FILE: docs/ai/prompts/03_rfc/02_goal_rfc_verification_vam_hardening.txt

```text
/goal
Create an RFC for verification/VAM hardening.

Read:
- docs/ai/audits/05_VERIFICATION_AUDIT.md
- docs/ai/findings/FINDINGS.md
- docs/ai/findings/GATED.md
- docs/ai/control/05_EVIDENCE_LEDGER.md
- docs/ai/control/06_RISK_REGISTER.md
- pipeline/verify.py
- pipeline/verify_ttl.py
- docs/architecture/10-VERIFICATION-STACK.md
- tests/

Do not modify production code.
Do not modify tests.
Do not modify migrations.

Create:
- docs/ai/rfcs/RFC_VERIFICATION_VAM_HARDENING.md

The RFC must cover:
- quorum rules;
- independence logic;
- zero-count trustworthy prevention;
- TTL expiry;
- REFUTED/TRUSTWORTHY/UNVERIFIED states;
- Deep Ledger status;
- Inquisition status;
- Gestionador status;
- source health interaction;
- API exposure of trust state;
- required regression tests;
- rollback plan.

End with human approval required.
```


---

# PROMPT FILE: docs/ai/prompts/03_rfc/03_goal_rfc_production_architecture.txt

```text
/goal
Create an RFC for production architecture.

Read:
- docs/ai/audits/10_PRODUCTION_AUDIT.md
- docs/ai/reports/PRODUCTION_GAP_REPORT.md
- docker-compose.yml
- Dockerfile
- .env.example
- pipeline/ops/
- services/api/
- scripts/
- docs/runbook/

Do not modify deployment files.
Do not modify code.
Do not modify migrations.

Create:
- docs/ai/rfcs/RFC_PRODUCTION_ARCHITECTURE.md

The RFC must include two options:

Option A — cheap production:
- single VPS;
- PostgreSQL;
- API process;
- scheduler/worker process;
- local logs;
- daily backup;
- basic health checks;
- limited concurrency.

Option B — serious production:
- managed/hardened PostgreSQL;
- API service;
- worker pool;
- queue;
- scheduler coordination;
- metrics;
- logs;
- alerts;
- secrets manager;
- backups and restore tests;
- source health;
- rate limits;
- staging;
- CI/CD;
- cost controls.

For each option include:
- architecture diagram in text;
- components;
- monthly cost estimate placeholder;
- risks;
- operational complexity;
- failure modes;
- migration path;
- rollback plan.

End with human decision required.
```


---

# PROMPT FILE: docs/ai/prompts/03_rfc/04_goal_rfc_product_mvp.txt

```text
/goal
Create an RFC defining Cardeep's first sellable MVP.

Read:
- docs/ai/audits/11_PRODUCT_AUDIT.md
- docs/ai/reports/PRODUCTIZATION_GAP_REPORT.md
- docs/ai/reports/MODULE_SCORECARD.md
- README.md
- PLAN.md
- PROGRESO.md
- services/api/
- docs/

Do not modify public docs.
Do not modify API.
Do not modify frontend.
Do not modify product claims.

Create:
- docs/ai/rfcs/RFC_PRODUCT_MVP.md

The RFC must answer:
- What is Cardeep today?
- What can be sold safely?
- What cannot be sold yet?
- Who is the first customer?
- What data package is credible?
- What coverage claims are allowed?
- What freshness claims are allowed?
- What verification claims are allowed?
- What must be marked GATED?
- What must be removed from pitch?
- What is the first paid MVP?
- What technical work blocks selling?
- What legal/compliance work blocks selling?

End with a clear decision:
CONTINUE / CUT_SCOPE / PIVOT / REBUILD.
```


---

# PROMPT FILE: docs/ai/prompts/04_tests/00_goal_ingest_characterization_tests.txt

```text
/goal
Add characterization tests for current ingest behavior.

Mode:
TEST_ONLY

Read:
- docs/ai/audits/03_INGEST_AUDIT.md
- pipeline/ingest.py
- tests/

Allowed to modify:
- tests/test_ingest_characterization.py
- tests/fixtures/
- docs/ai/findings/FINDINGS.md
- docs/ai/control/05_EVIDENCE_LEDGER.md

Forbidden:
- pipeline/ingest.py
- pipeline/delta.py
- migrations/
- services/

Goal:
Create tests that document current behavior without changing production logic.

Test scenarios:
1. new vehicle insert;
2. existing vehicle update;
3. price change event;
4. km change event;
5. photo change event;
6. idempotent re-ingest;
7. gone transition if supported;
8. malformed item handling if supported;
9. dealer/entity source update.

Run:
python -m pytest tests/test_ingest_characterization.py -q

If tests fail due to current behavior, do not patch. Record finding.
```


---

# PROMPT FILE: docs/ai/prompts/04_tests/01_goal_delta_gone_tests.txt

```text
/goal
Add characterization tests for delta and gone behavior.

Mode:
TEST_ONLY

Read:
- docs/ai/audits/04_DELTA_GONE_AUDIT.md
- pipeline/delta.py
- pipeline/delta_guard.py
- pipeline/evict.py
- tests/

Allowed:
- tests/test_delta_gone_characterization.py
- tests/fixtures/
- docs/ai/findings/FINDINGS.md
- docs/ai/control/05_EVIDENCE_LEDGER.md

Forbidden:
- pipeline/delta.py
- pipeline/delta_guard.py
- pipeline/evict.py
- pipeline/ingest.py
- migrations/

Test scenarios:
1. no change;
2. price change;
3. km change;
4. photo change;
5. missing listing;
6. append-only connector behavior;
7. false gone prevention;
8. duplicate event prevention.

Run:
python -m pytest tests/test_delta_gone_characterization.py -q

Do not modify production logic.
```


---

# PROMPT FILE: docs/ai/prompts/04_tests/02_goal_verification_regression_tests.txt

```text
/goal
Add regression tests for verification/VAM.

Mode:
TEST_ONLY

Read:
- docs/ai/audits/05_VERIFICATION_AUDIT.md
- pipeline/verify.py
- pipeline/verify_ttl.py
- tests/

Allowed:
- tests/test_verification_regressions.py
- tests/fixtures/
- docs/ai/findings/FINDINGS.md
- docs/ai/control/05_EVIDENCE_LEDGER.md

Forbidden:
- pipeline/verify.py
- pipeline/verify_ttl.py
- pipeline/inquisition/
- pipeline/gestionador/
- migrations/

Test scenarios:
1. zero-count cannot be trustworthy;
2. single source is unverified;
3. quorum pass;
4. quorum fail;
5. refuted state;
6. TTL expiry;
7. source independence distinction;
8. stale verdict supersede if supported.

Run:
python -m pytest tests/test_verification_regressions.py -q

Do not modify production logic.
```


---

# PROMPT FILE: docs/ai/prompts/04_tests/03_goal_api_contract_tests.txt

```text
/goal
Add API contract tests.

Mode:
TEST_ONLY

Read:
- docs/ai/audits/07_API_AUDIT.md
- services/api/
- tests/

Allowed:
- tests/test_api_contract_characterization.py
- tests/fixtures/
- docs/ai/findings/FINDINGS.md
- docs/ai/control/05_EVIDENCE_LEDGER.md

Forbidden:
- services/api/
- pipeline/
- migrations/

Test scenarios:
1. health endpoint;
2. invalid params;
3. empty result;
4. pagination if supported;
5. filters if supported;
6. rate limit if supported;
7. cache behavior if supported;
8. verified/trust field if exposed.

Run:
python -m pytest tests/test_api_contract_characterization.py -q

Do not modify API implementation.
```


---

# PROMPT FILE: docs/ai/prompts/05_safe_patch/00_goal_safe_patch_template.txt

```text
/goal
Apply a SAFE_PATCH for the specific issue below.

Issue:
[PASTE FINDING ID AND SUMMARY]

Evidence:
[PASTE EVIDENCE ID / TEST FAILURE / FILE PATH]

Allowed files:
[LIST EXACT FILES]

Forbidden files:
- migrations/
- unrelated modules
- public docs
- dependencies
- any file not listed as allowed

Rules:
- Minimal patch only.
- No refactor.
- No scope expansion.
- No architecture change.
- No behavior change outside the issue.
- Add or update test if needed.
- Run targeted validation.
- If the fix touches ingest/delta/dedup/verification/API contract/scheduler/schema, stop and create RFC instead.

Required output:
1. What changed.
2. Why it changed.
3. Test run.
4. Result.
5. git diff --name-only.
6. Remaining risk.
```


---

# PROMPT FILE: docs/ai/prompts/06_review/00_goal_review_last_task_diff.txt

```text
/goal
Review the last task diff as a strict technical reviewer.

Do not modify files.

Inspect:
- git status --short
- git diff --name-only
- git diff --stat
- git diff

Check:
1. Did the task respect allowed_files?
2. Were forbidden files touched?
3. Did the task expand scope?
4. Are claims backed by evidence?
5. Are runtime claims actually executed?
6. Were tests required?
7. Were tests run?
8. Is TASK_QUEUE.yml updated correctly?
9. Are findings/evidence/risk updated?
10. Should this be accepted, reverted or sent to NEEDS_REVIEW?

Create:
- docs/ai/reports/LAST_TASK_REVIEW.md

Do not change production code.
```


---

# PROMPT FILE: docs/ai/prompts/06_review/01_goal_validate_task_queue_integrity.txt

```text
/goal
Validate TASK_QUEUE.yml integrity.

Do not modify production code.

Read:
- docs/ai/tasks/TASK_QUEUE.yml
- docs/ai/control/02_EXECUTION_MODES.md
- docs/ai/control/03_DEFINITION_OF_DONE.md
- docs/ai/control/08_CHANGE_CONTROL.md

Check:
1. Every task has ID, title, status, mode, risk, objective.
2. Every task has allowed_files.
3. Every task has forbidden_files.
4. Every task has validation.
5. Every task has acceptance criteria.
6. No critical task is marked READY before prerequisites.
7. BLOCKED tasks include blocked_reason.
8. RFC_REQUIRED tasks do not allow production modifications.
9. TEST_ONLY tasks do not allow production code modifications.
10. SAFE_PATCH tasks are sufficiently narrow.

Create:
- docs/ai/reports/TASK_QUEUE_INTEGRITY_CHECK.md

If needed, modify only:
- docs/ai/tasks/TASK_QUEUE.yml

Report changes.
```


---

# PROMPT FILE: docs/ai/prompts/06_review/02_goal_create_executive_status.txt

```text
/goal
Create an executive technical status report from docs/ai.

Read:
- docs/ai/audits/
- docs/ai/findings/
- docs/ai/control/06_RISK_REGISTER.md
- docs/ai/reports/
- docs/ai/tasks/TASK_QUEUE.yml

Do not modify production code.

Create:
- docs/ai/reports/EXECUTIVE_STATUS.md

Report:
1. Current truth level.
2. Runtime verification status.
3. Critical risks.
4. Strongest modules.
5. Weakest modules.
6. Gated areas.
7. Broken areas.
8. Unknowns.
9. Production readiness.
10. Product readiness.
11. Next 10 actions.

Use evidence labels:
VERIFIED_STATIC, VERIFIED_RUNTIME, PARTIAL, NO_VERIFIED, BROKEN, CONTRADICTION, GATED.
```


---

# PROMPT FILE: docs/ai/prompts/07_scorecards/00_goal_module_scorecard.txt

```text
/goal
Build the Cardeep module scorecard.

Read:
- docs/ai/audits/
- docs/ai/reports/RUNTIME_BASELINE.md
- docs/ai/findings/
- docs/ai/control/05_EVIDENCE_LEDGER.md
- docs/ai/control/06_RISK_REGISTER.md

Do not modify production code.

Create:
- docs/ai/reports/MODULE_SCORECARD.md

Score each area 0-10:
1. Repository organization.
2. Documentation accuracy.
3. Data model.
4. Migrations.
5. Ingest.
6. Delta/gone.
7. Dedup/identity.
8. Verification/VAM.
9. Source connectors.
10. Tier-1 scraping.
11. API.
12. Scheduler/ops.
13. Tests.
14. CI.
15. Observability.
16. Production readiness.
17. Product readiness.
18. Commercial readiness.

Rules:
- No score above 6 without runtime validation.
- No score above 7 without meaningful tests.
- No score above 8 without observability and operational recovery.
- Every score must cite evidence.
- Separate architecture score from implementation score.
- Separate implementation score from runtime score.
- Separate runtime score from product/commercial score.

End with:
- Continue / Cut scope / Pivot / Rebuild.
- Next 10 actions in exact order.
```


---

# PROMPT FILE: docs/ai/prompts/07_scorecards/01_goal_release_readiness.txt

```text
/goal
Evaluate release readiness.

Read:
- docs/ai/reports/MODULE_SCORECARD.md
- docs/ai/reports/RUNTIME_BASELINE.md
- docs/ai/reports/PRODUCTION_GAP_REPORT.md
- docs/ai/reports/PRODUCTIZATION_GAP_REPORT.md
- docs/ai/control/06_RISK_REGISTER.md
- docs/ai/tasks/TASK_QUEUE.yml
- tests/
- services/api/
- pipeline/

Do not modify code.

Create:
- docs/ai/reports/RELEASE_READINESS.md

Classify release readiness for:
1. internal developer use;
2. internal data validation;
3. private beta API;
4. paid pilot;
5. public product;
6. production system.

For each:
- status;
- blockers;
- risks;
- required tasks;
- evidence.

Allowed statuses:
- NOT_READY
- LAB_READY
- INTERNAL_READY
- PRIVATE_BETA_CANDIDATE
- PAID_PILOT_CANDIDATE
- PRODUCTION_CANDIDATE
- PRODUCTION_READY

Do not mark PRODUCTION_READY without runtime validation, tests, observability, backups and operational recovery.
```
