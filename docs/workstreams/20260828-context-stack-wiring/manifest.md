---
schema_version: 1
task_id: 20260828-context-stack-wiring
title: Wire owner-provided sidecar stack
status: implemented_local
risk_tier: moderate
---

# Workstream: owner stack wiring

Required: software-engineer-subagent (implementation).
Skipped: product-manager (owner already specified the stack), ui-ux (no chrome change), security-engineer (no new bind, no secrets stored; residual: heavy-model enable flags), growth-marketing (no launch), project-lead (local wiring only).

Locks: 127.0.0.1 only, no unofficial `.als` write, no key values in git.
