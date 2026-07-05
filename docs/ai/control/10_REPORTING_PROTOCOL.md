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
