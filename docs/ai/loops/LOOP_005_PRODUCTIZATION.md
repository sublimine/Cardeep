# LOOP 005 — PRODUCTIZATION

## Purpose

Convert technical reality into a sellable, honest product boundary.

## Allowed Task Modes

- PRODUCT_GATE
- RFC_REQUIRED
- AUDIT_ONLY

## Forbidden

- editing public marketing claims without approval;
- claiming 100% coverage without evidence;
- claiming real-time without runtime proof;
- claiming legal safety without review;
- claiming production readiness without production evidence;
- building frontend before API/data quality is proven.

## Instruction For Claude Code

```text
/loop
Read:
- docs/ai/audits/11_PRODUCT_AUDIT.md
- docs/ai/reports/PRODUCTIZATION_GAP_REPORT.md
- docs/ai/reports/MODULE_SCORECARD.md
- docs/ai/rfcs/RFC_PRODUCT_MVP.md if it exists
- docs/ai/tasks/TASK_QUEUE.yml

Execute the next READY productization task.

Rules:
- Map every product claim to evidence.
- Mark unsupported claims as NO_VERIFIED or GATED.
- Define what can be sold safely now.
- Define what must not be promised.
- Do not edit public docs unless a task explicitly allows it.
- If commercial decision is required, stop and request human decision.

At the end:
- update productization report;
- update task queue;
- update risk register;
- report remaining blockers.
```
