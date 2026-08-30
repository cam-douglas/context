---
schema_version: 1
task_id: 20260828-context-ai-arrangement
role_id: security-engineer-subagent
status: draft
revision: 1
created_at: 2026-08-28T08:40:00Z
updated_at: 2026-08-28T08:40:00Z
---

# Role Plan: security-engineer-subagent

## 1. Entry criteria and inherited evidence

Engineering phase-0 handoff plus license research.

## 2. Scope, non-goals, and requirement coverage

| Requirement ID | Planned disposition | Expected evidence |
|---|---|---|
| C-7 | confirm NC block | findings |
| C-8 | inspect new files | scan notes |

## 3. Dependencies

Engineering evidence.

## 4. Files, interfaces, data, and external systems

Sidecar, docs, handover scripts.

## 5. Ownership and concurrency

Read-only.

## 6. Ordered tasks

1. Threat model: local audio, localhost IPC, future adapters.
2. License review against research table.
3. Inspect diffs for secrets.
4. Verdict.

## 7. Tool and modality plan

Read-only inspection. No pentest.

## 8. Horizontal full-stack checklist

Security owned. Integrations reviewed as none authorized.

## 9. Risk controls, rollback, and recovery

Cannot waive high/critical.

## 10. Validation steps and expected evidence

File inspection timestamps and paths.

## 11. Outputs and storage paths

`artifacts/threat-model.md`, `artifacts/findings.md`, `handoff.md`

## 12. Gate criteria and downstream handoff

No high/critical. Owner bootstrap repair is residual operational risk, not a product vuln.

## 13. Deviations and plan change log

None.
