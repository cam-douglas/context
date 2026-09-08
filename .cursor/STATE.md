# STATE.md

## Current Objective

- Persist stays stock. Poll Hugging Face Job `6a9f9c85259f8e97255ee0b7` until COMPLETED/ERROR/CANCELED. Do not apply persist. Do not submit jobs.

## Current Status

- 14h monitor of Job `6a9f9c85259f8e97255ee0b7` ended `timeout_14h`. 420 tmux polls plus extras, all `no_token` / HTTP 401. Stage, exception, logs, and `adapter_model.safetensors` were never readable. Persist/plugin untouched. Prior Job `6a9f97ec` prepared 600 rows then trainer saw `num_samples=0` because dreamboothing uses strict `min < duration < max` (`max=9s`) and clips were truncated to exactly 9s. This Job writes 8s clips.

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

- HF Job monitor artifacts: `/tmp/hf-job-6a9f9c85259f8e97255ee0b7/` (tmux `hf-job-6a9f9c`). Adapter target `cam-douglas/context-musicgen-small-stage-a-caption-lora`. Persist/plugin untouched.

## Next Actions

- Inspect Job `6a9f9c85259f8e97255ee0b7` from a Hub-logged-in session. On ERROR return the real exception plus last useful log lines. On COMPLETED confirm `adapter_model.safetensors`. Do not apply persist. Do not submit jobs.

## Last Updated

- 2026-09-08 — Job `6a9f9c85259f8e97255ee0b7` monitor ended `timeout_14h` with no Hub login; stage unknown.
