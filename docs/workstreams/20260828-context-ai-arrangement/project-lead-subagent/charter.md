---
schema_version: 1
task_id: 20260828-context-ai-arrangement
role_id: project-lead-subagent
status: planning
revision: 1
created_at: 2026-08-28T08:40:00Z
updated_at: 2026-08-28T08:40:00Z
predecessor_handoff: docs/workstreams/20260828-context-ai-arrangement/growth-marketing-subagent/handoff.md
---

# Role Charter: project-lead-subagent

## 1. Role objective

### Mission

Reconcile Context phase 0. Do not approve production. Surface the bootstrap owner action.

## 2. Inherited request and evidence

Full workstream plus blocker.

## 3. Scope, non-goals, and ownership

Read-only reconciliation. Lead materializes owner-handoff when asked at closure. Phase 0 only prepares readiness, not closure.

## 4. Inherited requirements and vertical responsibilities

Trace C-IDs. Confirm skips none. Confirm Security status.

## 5. Assumptions, open questions, and clarification decisions

Phase 0 cannot close while bootstrap is blocked.

## 6. Skills, tools, and evidence sources

Repo inspection, test results.

## 7. Outputs and storage paths

`artifacts/reconciliation-report.md` when gates exist.

## 8. Horizontal quality coverage

Delivery owned. All rows reviewed.

## 9. Validation plan and gate criteria

BLOCKED while protected files are missing. CONDITIONAL after docs+schema if owner repair is the only gap.

## 10. Risks, blockers, and escalation triggers

Governance files remain owner-only.

## 11. Failure handling and recovery

Do not invent PASS.

## 12. Downstream role and handoff conditions

User/operator. Choices: run repair, REQUEST_CHANGES, or DO_NOT_PROCEED.
