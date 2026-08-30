---
schema_version: 1
task_id: 20260828-context-ai-arrangement
role_id: software-engineer-subagent
status: planning
revision: 1
created_at: 2026-08-28T08:40:00Z
updated_at: 2026-08-28T08:40:00Z
predecessor_handoff: docs/workstreams/20260828-context-ai-arrangement/ui-ux-developer-subagent/handoff.md
---

# Role Charter: software-engineer-subagent

## 1. Role objective

### Mission

Implement the smallest foundation that locks the sidecar contract and later the Max LiveAPI harness. Phase 0 is schema and tests only.

## 2. Inherited request and evidence

Blueprint architecture. Schema started at `sidecar/src/context_sidecar/schema.py`.

## 3. Scope, non-goals, and ownership

- In scope now: sidecar schema, tests, package metadata, Max folder placeholder
- Later: HTTP sidecar, `v8` writer, freeze packaging
- Owned write paths: `sidecar/`, `max/context/`, `fixtures/`
- Prohibited: protected governance files, secrets, production deploy, MusicGen weights

## 4. Inherited requirements and vertical responsibilities

C-2, C-3, C-4, C-5, C-8.

## 5. Assumptions, open questions, and clarification decisions

`provisional`: stdlib unittest until pytest is pinned. HTTP comes in phase 1.

## 6. Skills, tools, and evidence sources

Python 3, unittest. Max/Live not available in this environment unless verified.

## 7. Outputs and storage paths

`sidecar/` tests, `artifacts/technical-design.md` in later phase.

## 8. Horizontal quality coverage

Client/server/data owned for sidecar. Experience implemented later. Security defaults: localhost, no keys.

## 9. Validation plan and gate criteria

`PYTHONPATH=src python -m unittest tests/test_schema.py` passes.

## 10. Risks, blockers, and escalation triggers

Cannot validate LiveAPI without Live. Phase 1 gate.

## 11. Failure handling and recovery

Keep schema backward-compatible or bump `schema_version`.

## 12. Downstream role and handoff conditions

Hand off to Security after phase-0 tests pass and no secrets are added.
