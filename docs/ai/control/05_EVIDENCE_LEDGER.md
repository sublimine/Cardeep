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
