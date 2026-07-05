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
