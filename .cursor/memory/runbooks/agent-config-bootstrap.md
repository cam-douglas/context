# Domain: Agent configuration bootstrap

## Purpose

Record the self-contained startup and validation procedure for the agent configuration tree.

## Procedure

- Before mutation, run `node .cursor/skills/launch-pipeline/scripts/preflight.mjs`.
- After Build or explicit Agent-mode implementation authorization, run the resolved `/scripts/bootstrap.sh`; from the configuration root, use `bash scripts/bootstrap.sh`.
- The script creates missing root documentation, workstream, agent, hook, and memory directories; seeds missing indexes; repairs the settings compatibility link when safe; and validates required files and policy configuration.
- It does not overwrite non-empty project content or create secrets.

## Validation

- Command exits successfully and prints `bootstrap complete` with the resolved repository root.
- `/settings.json` resolves to `/config/settings.json`.
- `docs/blueprints`, `docs/plans`, `docs/decisions`, `docs/handover`, and `docs/workstreams` exist.
- Root `AGENTS.md`, all six native role adapters, the canonical role catalog, templates, hooks, and policy files pass `.cursor/scripts/validate-agent-config.mjs`.
