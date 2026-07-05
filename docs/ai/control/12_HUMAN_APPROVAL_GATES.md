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
