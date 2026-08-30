# AGENTS.md

This is the native project-wide router for this repository.

On every substantive turn, read this file first, then read [`.cursor/AGENTS.md`](.cursor/AGENTS.md) and its complete core per-turn set. Canonical specialist behavior lives only in [`.cursor/instructions/ROLES.md`](.cursor/instructions/ROLES.md).

## Product lifecycle

For a raw idea, major change, resume, remediation, or closure, invoke `/launch-pipeline`. Do not ask the user to open control-plane files one by one.

## Control plane

- Operating contract: `.cursor/AGENTS.md`
- Instruction router: `.cursor/INSTRUCTIONS.md`
- Roles and stage gates: `.cursor/instructions/ROLES.md`
- Live state: `.cursor/STATE.md`
- Task artifacts: `docs/workstreams/`

## Startup

1. Read this file.
2. Read `.cursor/AGENTS.md`.
3. Run `node .cursor/skills/launch-pipeline/scripts/preflight.mjs`.
4. After Build or explicit Agent-mode implementation authorization, run `bash .cursor/scripts/bootstrap.sh`.
