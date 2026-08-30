---
schema_version: 1
task_id: 20260828-context-ai-arrangement
role_id: product-manager-subagent
status: draft
revision: 1
created_at: 2026-08-28T08:40:00Z
updated_at: 2026-08-28T08:40:00Z
---

# Role Plan: product-manager-subagent

## 1. Entry criteria and inherited evidence

Manifest, blueprint, research corpus, and name decision exist.

## 2. Scope, non-goals, and requirement coverage

| Requirement ID | Planned disposition | Expected evidence |
|---|---|---|
| C-1–C-9 | specify acceptance | `artifacts/product-requirements.md` |

## 3. Dependencies

None beyond inherited docs.

## 4. Files, interfaces, data, and external systems

Arrangement JSON schema in `sidecar/src/context_sidecar/schema.py`.

## 5. Ownership and concurrency

Lead writes returned artifacts. No source edits.

## 6. Ordered tasks

1. Confirm user/problem/outcome against the launch request.
2. Write PRD with journeys, edges, non-goals, metrics (unknown baselines labeled unknown).
3. Record evidence from blueprint and schema tests.
4. Handoff to UI/UX.

## 7. Tool and modality plan

Read-only file inspection. No Figma/analytics.

## 8. Horizontal full-stack checklist

Product owned. Experience reviewed. Client/server/data reviewed as sidecar+device. Security reviewed. Growth reviewed. Delivery reviewed as local-only V1.

## 9. Risk controls, rollback, and recovery

Do not expand into generation or cross-DAW arrangement control.

## 10. Validation steps and expected evidence

PRD traces every C-ID. Schema tests remain green.

## 11. Outputs and storage paths

`artifacts/product-requirements.md`, `evidence.md`, `handoff.md`

## 12. Gate criteria and downstream handoff

PASS if UI/UX can specify preview/apply/error without inventing product rules.

## 13. Deviations and plan change log

None.
