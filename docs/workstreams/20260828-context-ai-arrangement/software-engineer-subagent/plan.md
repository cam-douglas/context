---
schema_version: 1
task_id: 20260828-context-ai-arrangement
role_id: software-engineer-subagent
status: draft
revision: 1
created_at: 2026-08-28T08:40:00Z
updated_at: 2026-08-28T08:40:00Z
---

# Role Plan: software-engineer-subagent

## 1. Entry criteria and inherited evidence

UI/UX spec may be in progress; schema work is independent and allowed in phase 0.

## 2. Scope, non-goals, and requirement coverage

| Requirement ID | Planned disposition | Expected evidence |
|---|---|---|
| C-4 | schema module | unittest pass |
| C-8 | no secrets in sidecar | inspection |

## 3. Dependencies

None for schema.

## 4. Files, interfaces, data, and external systems

`sidecar/src/context_sidecar/schema.py`

## 5. Ownership and concurrency

Sole writer for `sidecar/` during phase 0.

## 6. Ordered tasks

1. Schema + empty_arrangement helper.
2. Unit tests for valid/invalid plans.
3. Placeholder Max and fixtures READMEs.
4. Record evidence.

## 7. Tool and modality plan

Local Python unittest. No Live.

## 8. Horizontal full-stack checklist

Quality owned. Performance not_applicable at schema-only. Observability later.

## 9. Risk controls, rollback, and recovery

Schema-only; delete package if abandoned.

## 10. Validation steps and expected evidence

Unittest command below.

## 11. Outputs and storage paths

`sidecar/`, `evidence.md`, `handoff.md`

## 12. Gate criteria and downstream handoff

CONDITIONAL is acceptable if Live is unverified. Schema tests must pass.

## 13. Deviations and plan change log

Schema implemented during phase 0 before UI/UX gate because it is the shared contract.
