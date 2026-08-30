---
schema_version: 1
task_id: 20260828-context-ai-arrangement
role_id: ui-ux-developer-subagent
status: planning
revision: 1
created_at: 2026-08-28T08:40:00Z
updated_at: 2026-08-28T08:40:00Z
predecessor_handoff: docs/workstreams/20260828-context-ai-arrangement/product-manager-subagent/handoff.md
---

# Role Charter: ui-ux-developer-subagent

## 1. Role objective

### Mission

Specify the Context device UI: inspect, preview arrangement, apply, undo guidance, sidecar-down and license-blocked states.

## 2. Inherited request and evidence

PM contract and blueprint. Device is a Max for Live panel, not a web app.

## 3. Scope, non-goals, and ownership

- In scope: flows, states, accessibility in a DAW plugin (keyboard where Live allows, contrast, reduced motion)
- Non-goals: implementing Max UI, Figma library unless access is verified
- Write: read-only; lead materializes
- Prohibited: source edits, unverified Figma claims

## 4. Inherited requirements and vertical responsibilities

C-2, C-4, C-5 user-visible behavior.

## 5. Assumptions, open questions, and clarification decisions

`provisional`: live.UI / jsui in Max, not JUCE, for V1.

## 6. Skills, tools, and evidence sources

Mobbin/Figma only if authenticated. Otherwise specify in Markdown.

## 7. Outputs and storage paths

`artifacts/design-specification.md`, `artifacts/flow-and-state-matrix.md`

## 8. Horizontal quality coverage

Experience owned. Product reviewed. Security reviewed for error copy that must not leak paths with secrets. Growth reviewed for claim language.

## 9. Validation plan and gate criteria

Every PM journey has a state matrix row.

## 10. Risks, blockers, and escalation triggers

Live device height limits. No arrangement canvas in GarageBand — do not design that into V1.

## 11. Failure handling and recovery

BLOCKED if PM contract missing apply/undo rules.

## 12. Downstream role and handoff conditions

Hand off to `software-engineer-subagent`.
