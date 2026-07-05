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
