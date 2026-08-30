# Resolved: missing protected control-plane files

## Resolution

Owner ran `docs/handover/apply-missing-control-plane-files.sh` on 2026-08-28, creating `AGENTS.md`, `.cursorignore`, and `.github/workflows/agent-governance.yml`.

Bootstrap then failed on orphan `.cursor/.DS_Store`. Launch validation now skips Finder/noise files. `.cursor/.DS_Store` was deleted.

## Evidence

- `bash .cursor/scripts/bootstrap.sh` → `bootstrap complete`
- Launch validation: 79 control-plane files, no orphans
- `node .cursor/skills/launch-pipeline/scripts/preflight.mjs` → `status: READY` at `2026-08-28T08:53:05.350Z`

## Original symptoms

Bootstrap required root `AGENTS.md`. Agent writes to that path are fail-closed.
