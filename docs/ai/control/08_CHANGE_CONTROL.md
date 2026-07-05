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
