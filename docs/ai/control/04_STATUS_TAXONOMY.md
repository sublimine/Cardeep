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
