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
