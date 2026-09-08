# STATE.md

## Current Objective

- Persist stays stock. Stopped Job `6a9f83aa259f8e97255edca6` (ERROR OOMKilled 137). Poll newest running `context-musicgen-stage-a-caption-lora` for `cam-douglas` until COMPLETED/ERROR/CANCELED. Do not start Stage B. Do not set `CONTEXT_MUSICGEN_ADAPTER`.

## Current Status

- Switched off the OOM Job. Replacement Stage A Job is being submitted by the parent. This VM still has no `HF_TOKEN`, so `hf jobs list --name context-musicgen-stage-a-caption-lora` is 401. Discover/poll every 120s. Persist stock.

## Project Phase

- Phase 11 session export — implemented locally

## Active Plan

- `docs/plans/phase_11_session_export_plan.md`

## Active Workstream

- `docs/workstreams/20260830-als-json-session-export/manifest.md`

## Active Role and Gate

- Owner: File → Open a written `*.als` from Application Support `Context/Plugin` or an `/export` folder.

## Predecessor Handoff

- `docs/workstreams/20260830-als-json-session-export/delivery/owner-handoff.md`

## Pending Remediation

- None in the sidecar export path. Live File → Open is unverified.

## Owner Decision

- 2026-08-30: session export via als-json is authorized. Do not overwrite the source set. Production publish not authorized.

## Active Instructions

- `/instructions/PROJECT_PLANNING.md`
- `/instructions/ROLES.md`
- `/instructions/LAUCH.md`

## Active Items

- Sidecar running on 127.0.0.1:8765 (PID refreshed after HTTP fix)
- Plugin Release arm64 **Context 14** (`com.context.audio14`)
- This Mac: Live 11 Suite 11.3.43

## Files in Active Use

- `plugin/src/SampleLibraryPanel.cpp`
- `plugin/src/PluginEditor.cpp`
- `sidecar/src/context_sidecar/search.py`
- `sidecar/src/context_sidecar/http.py`
- `sidecar/src/context_sidecar/progress.py`
- `sidecar/src/context_sidecar/generation.py`
- `sidecar/src/context_sidecar/compose.py`
- `plugin/src/PromptPolicy.h`
- `plugin/src/SampleLibraryPanel.cpp`
- `sidecar/src/context_sidecar/als_json.py`
- `sidecar/src/context_sidecar/session_export.py`
- `docs/decisions/2026-08-30-als-json-session-export.md`
- `docs/plans/phase_11_session_export_plan.md`

## Open Blockers

- `.cursor/memory/blockers/hf-job-monitor-missing-token.md`
- `.cursor/memory/blockers/live-harness-apply-inert.md` (Max path; superseded as primary host)

## Attempts Performed

- Installed DawDreamer 0.9.0. Implemented lossless ALS↔JSON, additive merge, subprocess render.

## Decisions and Assumptions

- Prompt ranks: SYSTEM = RULES (hard) > NEGATIVE (hard reject) > REQUEST (suggestion). The request cannot override the gate.
- Export clones Live's DefaultLiveSet when no `source_als` is given.
- Compose writes `.als` without DawDreamer render (fast path). `/export` renders by default.
- Live may repair unofficial clip XML; owner smoke is the remaining gate.

## Current Working State

- HF Job monitor artifacts: `/tmp/hf-job-monitor/` (tmux `hf-job-monitor`). Persist/plugin untouched.

## Next Actions

- Discover newest `context-musicgen-stage-a-caption-lora` Job ID (never `6a9f83aa`). Poll 120s. On ERROR ping with log tail. On COMPLETED verify `adapter_model.safetensors`. Do not apply persist.

## Last Updated

- 2026-09-08 — Abandoned Job `6a9f83aa` OOMKilled 137; retargeted to replacement Stage A Job by name; still auth gated.
