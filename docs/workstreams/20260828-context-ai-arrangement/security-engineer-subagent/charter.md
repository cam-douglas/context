---
schema_version: 1
task_id: 20260828-context-ai-arrangement
role_id: security-engineer-subagent
status: planning
revision: 1
created_at: 2026-08-28T08:40:00Z
updated_at: 2026-08-28T08:40:00Z
predecessor_handoff: docs/workstreams/20260828-context-ai-arrangement/software-engineer-subagent/handoff.md
---

# Role Charter: security-engineer-subagent

## 1. Role objective

### Mission

Independent privacy, license, and sidecar-exposure review. Block high/critical findings.

## 2. Inherited request and evidence

Tier 3. User audio. License matrix. Protected-file bootstrap gap.

## 3. Scope, non-goals, and ownership

Read-only. No implementation. No exploit PoCs.

## 4. Inherited requirements and vertical responsibilities

C-7, C-8, localhost binding, generation master switch.

## 5. Assumptions, open questions, and clarification decisions

`verified`: MusicGen weights are CC-BY-NC. `provisional`: HeartMuLa Apache-2.0 pending card re-check at use.

## 6. Skills, tools, and evidence sources

`docs/research/context-stack.md`. Policy hooks already deny secrets.

## 7. Outputs and storage paths

`artifacts/threat-model.md`, `artifacts/findings.md`

## 8. Horizontal quality coverage

Security/privacy owned. Product/UX reviewed for over-claiming.

## 9. Validation plan and gate criteria

PASS only with no open high/critical. CONDITIONAL allowed for owner bootstrap repair if it is not a product exploit.

## 10. Risks, blockers, and escalation triggers

Shipping NC weights. Binding sidecar on 0.0.0.0. Storing API keys in Max presets.

## 11. Failure handling and recovery

BLOCKED returns to Engineering.

## 12. Downstream role and handoff conditions

Growth, then Project Lead.
