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
