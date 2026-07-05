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
