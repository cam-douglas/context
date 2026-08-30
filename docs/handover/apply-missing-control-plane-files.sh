#!/bin/sh
# Owner-run repair for missing protected control-plane files.
# Agent writes to AGENTS.md, .cursorignore, and agent-governance.yml are
# blocked by fail-closed hooks. Run this once from the repository root:
#   bash docs/handover/apply-missing-control-plane-files.sh
set -eu

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$REPO_ROOT"

write_if_missing() {
  path=$1
  if [ -s "$path" ]; then
    printf 'exists, skipped: %s\n' "$path"
    return 0
  fi
  mkdir -p "$(dirname -- "$path")"
  cat > "$path"
  printf 'created: %s\n' "$path"
}

write_if_missing "$REPO_ROOT/AGENTS.md" <<'EOF'
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
EOF

write_if_missing "$REPO_ROOT/.cursorignore" <<'EOF'
.DS_Store
.env
.env.*
!.env.example
node_modules/
.venv/
**/__pycache__/
*.pyc
sidecar/.venv/
max/**/codegen/
plugin/build/
*.amxd.bak
EOF

write_if_missing "$REPO_ROOT/.github/workflows/agent-governance.yml" <<'EOF'
name: agent-governance

on:
  push:
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: node .cursor/skills/launch-pipeline/scripts/preflight.mjs
      - run: node --test .cursor/hooks/policy.test.mjs
      - run: node --test .cursor/skills/launch-pipeline/scripts/preflight.test.mjs
      - run: node .cursor/scripts/validate-agent-config.mjs
      - run: node .cursor/skills/launch-pipeline/scripts/validate-launch.mjs
EOF

printf '\nOwner repair written. Next:\n'
printf '  bash .cursor/scripts/bootstrap.sh\n'
printf '  node .cursor/skills/launch-pipeline/scripts/preflight.mjs\n'
