---
schema_version: 1
task_id: 20260828-context-ai-arrangement
role_id: ui-ux-developer-subagent
status: draft
revision: 1
created_at: 2026-08-28T08:40:00Z
updated_at: 2026-08-28T08:40:00Z
---

# Role Plan: ui-ux-developer-subagent

## 1. Entry criteria and inherited evidence

PM handoff PASS or CONDITIONAL with C-IDs.

## 2. Scope, non-goals, and requirement coverage

| Requirement ID | Planned disposition | Expected evidence |
|---|---|---|
| C-2 | sidecar-down error | state matrix |
| C-4 | preview before apply | design spec |
| C-5 | apply + undo copy | design spec |

## 3. Dependencies

PM artifacts.

## 4. Files, interfaces, data, and external systems

Arrangement JSON preview list. No Figma file yet.

## 5. Ownership and concurrency

Lead materializes. No Max files.

## 6. Ordered tasks

1. Device anatomy: header, inspect, section list, apply bar, status.
2. States: empty, analyzing, preview, applying, success, sidecar-down, license-blocked, undo hint.
3. Accessibility: 44px targets where possible, no essential info in color only.
4. Handoff.

## 7. Tool and modality plan

Markdown spec. Screenshot later from Live.

## 8. Horizontal full-stack checklist

Experience owned. Others reviewed or not_applicable for visual system tokens (none exist).

## 9. Risk controls, rollback, and recovery

Do not specify real-time generative meters as V1.

## 10. Validation steps and expected evidence

Trace C-2/C-4/C-5 to components.

## 11. Outputs and storage paths

`artifacts/design-specification.md`, `artifacts/flow-and-state-matrix.md`, `evidence.md`, `handoff.md`

## 12. Gate criteria and downstream handoff

PASS if Engineering can build the panel without inventing copy or states.

## 13. Deviations and plan change log

None.
