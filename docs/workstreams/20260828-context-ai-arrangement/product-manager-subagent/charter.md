---
schema_version: 1
task_id: 20260828-context-ai-arrangement
role_id: product-manager-subagent
status: planning
revision: 1
created_at: 2026-08-28T08:40:00Z
updated_at: 2026-08-28T08:40:00Z
predecessor_handoff: none
---

# Role Charter: product-manager-subagent

## 1. Role objective

### Mission

Turn the Context vision into a testable product contract so UI, engineering, and security do not invent scope.

## 2. Inherited request and evidence

- Workstream manifest: `docs/workstreams/20260828-context-ai-arrangement/manifest.md`
- Active plan: `docs/plans/phase_0_foundations_plan.md`
- Predecessor handoff: lead intake + `docs/blueprints/2026-08-28_context.md`
- Relevant decisions/blockers: product name Context; bootstrap blocker

## 3. Scope, non-goals, and ownership

- In scope: PRD, requirement IDs C-1–C-9, acceptance, non-goals, metrics
- Explicit non-goals: Max patching, UI pixels, implementation
- Owned/write paths or `read-only`: read-only; lead materializes artifacts
- Read-only paths: blueprint, research, plans, sidecar schema
- External-system scope: none
- Prohibited actions: production, spend, secret access, claiming unverified market size

## 4. Inherited requirements and vertical responsibilities

C-1 through C-9 from the blueprint. Preserve Ableton-first V1 and license constraints.

## 5. Assumptions, open questions, and clarification decisions

- `verified`: name is Context
- `provisional`: generation off in V1
- `blocking`: none for the product contract

## 6. Skills, tools, and evidence sources

`docs/research/context-stack.md`, official LOM/RNBO URLs already fetched. No analytics MCP verified.

## 7. Outputs and storage paths

`charter.md`, `plan.md`, `evidence.md`, `handoff.md`, `artifacts/product-requirements.md`

## 8. Horizontal quality coverage

- Product and user acceptance: owned
- UI/UX and accessibility: reviewed (handoff to UI/UX)
- Frontend/backend/data/API/integration impact: reviewed
- Security/privacy/compliance/abuse: reviewed
- Testing/observability/reliability/performance: reviewed
- Deployment/rollback/operations: not_applicable for V1 store publish
- Analytics/growth/consent: reviewed
- Documentation/handoff: owned

## 9. Validation plan and gate criteria

PASS only if requirements are unique, testable, and match the blueprint architecture.

## 10. Risks, blockers, and escalation triggers

License or LiveAPI impossibility would force a pivot. Phase 1 is the LiveAPI evidence gate.

## 11. Failure handling and recovery

Return BLOCKED if owner changes V1 to require MusicGen in-process or Logic arrangement control.

## 12. Downstream role and handoff conditions

Hand off to `ui-ux-developer-subagent` with C-IDs, journeys, and prohibited claims.
