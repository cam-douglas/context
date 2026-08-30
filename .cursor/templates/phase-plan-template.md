---
plan: phase_<N>_<slug>
status: draft
created: YYYY-MM-DD
updated: YYYY-MM-DD
owner: lead-agent
source_phase: <path-or-none>
workstream: docs/workstreams/<task-id>/manifest.md
---

# Phase <N>: <Title>

## 1. Objective

## 2. Relation to project end-state

## 3. Entry criteria and inherited evidence

## 4. Scope

## 5. Non-goals

## 6. Current-state audit

## 7. Assumptions, constraints, risks, and decisions

## 8. Dependencies

## 9. Architecture and affected systems

## 10. Files and paths in scope

## 11. Supporting documents to create or update

## 12. Ordered implementation tasks

For each task include:

- objective
- dependencies
- exact files/systems
- implementation notes
- validation evidence
- completion state

## 13. Adaptive role and delegation map

Every canonical role from `/instructions/ROLES.md` must be listed as required or skipped with a reason. For required roles, include charter, role plan, predecessor, owned paths, evidence path, gate criteria, and handoff path.

| Role ID | Required or skipped | Reason | Predecessor | Owned paths | Gate evidence | Status |
|---|---|---|---|---|---|---|

## 14. Test and validation matrix

| Requirement | Validation method | Expected evidence | Status |
|---|---|---|---|

## 15. Security, privacy, reliability, accessibility, and performance checks

## 16. Environment-variable registry

Never include values.

| Variable name | Purpose | Scope/environment | Required by phase | Source/provider | Status |
|---|---|---|---|---|---|

## 17. Deferred human-action queue

Record actions but do not request them unless they are strict blockers.

| Action | Why agent cannot perform it | Earliest required phase | Blocking now? | Final-checklist destination |
|---|---|---|---|---|

## 18. Rollback and recovery

## 19. Acceptance criteria

## 20. Completion evidence

## 21. Deviations and follow-ups

## 22. Next Plan Generation Prompt

Read `/AGENTS.md`, the complete core agent context, `/instructions/PROJECT_PLANNING.md`, `/instructions/ROLES.md`, the original `docs/plans/phase_0_foundations_plan.md`, this completed phase plan, the active workstream manifest and role handoffs, all completion evidence, current repository state, active blockers, and relevant decisions. Confirm this phase and every required role gate are fully implemented and validated. Then generate exactly one exhaustive next phase plan at `docs/plans/phase_<NEXT_NUMBER>_<DESCRIPTIVE_SLUG>_plan.md`. Derive it from the phase-0 roadmap and verified current state, preserve unresolved requirements, include all required plan sections and adaptive role decisions, defer non-blocking human actions to the final phase, and do not implement the next phase until the plan is written.
