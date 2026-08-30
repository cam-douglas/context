---
plan: phase_1_liveapi_harness
status: implemented_unverified_live
created: 2026-08-28
updated: 2026-08-28
owner: lead-agent
source_phase: docs/plans/phase_0_foundations_plan.md
workstream: docs/workstreams/20260828-context-ai-arrangement/manifest.md
---

# Phase 1: LiveAPI harness

## 1. Objective

Prove Context can sit on a Live track, see the open set, take a prompt, talk to the local sidecar, and write one audio clip and one MIDI clip that Live Undo can revert. Ship the owner chrome (prompt, host follow, drop-in, reference, reverence, abstraction, and the granular knobs) even if the sidecar only echoes `IntentRequest`. Do not yet generate new music.

## 1a. Owner product contract (do not drop)

These journeys and knobs are already accepted. Phase 1 implements the surfaces and the localhost contract. Musical intelligence stays in later phases.

**Journeys**

- **Track follow.** Device on Drums. Prompt “add a bridge” or “expand on this riff”. Sidecar sees host-track input plus the full set. Preview, then Apply. Live Undo reverts.
- **Drop-in.** Drop a sample or loop. Prompt “add an instrument”, “remove a layer”, or “add this effect”. Preview, Audition (wet), or Apply.
- **Reference.** Drop any audio into Reference. Reverence = closeness to the reference. Abstraction = freedom versus the prompt. Preview, then Apply.
- **Project scope.** Scope can be this track, the selection, or the whole set. Locks protect tracks/clips that must not change.
- **Fail closed.** Sidecar down disables Prompt run, Analyze, and Apply.

**Rules**

- Analyze, preview, and audition never write the set. Only Apply writes.
- Default Apply creates new clips. Do not overwrite locks.
- On a drum host track, prefer drum-appropriate actions unless the prompt or scope says otherwise (P-8). Echo `inferred_role` even if preference logic is a stub.
- Do not claim Logic/GarageBand/FL arrangement. Do not label a MusicGen backend.

**Intent payload the device must send** (`sidecar/src/context_sidecar/intent.py`)

- `schema_version`, non-empty `prompt`
- `mode`: `track_follow` | `drop_in` | `reference` | `project`
- `scope`: `this_track` | `selection` | `set`
- `host_track` `{id, name, inferred_role}`
- `project` snapshot: `tempo_bpm`, `musical_key`, `playhead_beats`, `tracks[]`
- `knobs`: `reverence`, `abstraction`, `amount`, `wet` in `[0, 1]`
- `focus.kind`: `playhead` | `loop` | `selected_clip` | `host_clip`
- `locks`: list of non-empty ids
- `tempo_key_lock`, `variation`, optional `target_section`
- `drop_in.file_path` only in `drop_in` mode; `reference.file_path` only in `reference` mode

## 2. Relation to project end-state

This is the first runtime slice of the owner product: a prompt-driven instrument/effect with project context. Later phases add analysis, full arrangement writes, license-gated generation, DSP, and cross-DAW.

## 3. Entry criteria and inherited evidence

- Phase 0 verified. Preflight READY `2026-08-28T08:53:05.350Z`.
- Intent and arrangement schemas pass (`test_schema.py`, `test_intent.py`).
- Owner requirements in `docs/decisions/2026-08-28-context-granular-intent.md` and the PRD.
- Design spec lists the panel anatomy.

## 4. Scope

- Max Project + unfrozen Max audio-effect device under `max/context/`
- `v8` LiveAPI `ProjectSnapshot` + `host_track` (inferred role from track name)
- Sidecar HTTP on 127.0.0.1: `GET /health`, `POST /intent` (validate and echo `IntentRequest` plus `empty_arrangement` preview)
- Device chrome matching the design spec, all ten rows:
  1. Header + sidecar health
  2. Host strip (role, scope, focus)
  3. Prompt + Run
  4. Drop-in well (path field acceptable if drag-drop is not yet wired)
  5. Reference well + reverence + abstraction (knobs disabled until a reference path is set)
  6. Amount, wet, tempo/key lock, variation/replace, locks
  7. Inspect (tempo, key, energy placeholder, section candidates placeholder, host role)
  8. Preview JSON / summary
  9. Audition (must not write) and Apply
  10. Status line with the design-spec copy
- Fixture silent WAV + minimal MIDI
- Apply writes those fixtures via `Track.create_audio_clip` and `Track.create_midi_clip`
- Empty-prompt and sidecar-down fail closed
- Manual Live checklist documented

## 5. Non-goals

Demucs, MusicGen, AudioLDM 2, Stable Audio, CLAP search UI, pedalboard ducking, room corrector, dawdreamer, frozen store build, RNBO/JUCE, writing `.als`, real-time generative audio on the audio thread, overwriting arbitrary existing clips, full loop-to-song or “add a bridge” musical intelligence.

Those belong to phases 2–6 in the Cursor plan and `docs/decisions/2026-08-28-context-coproducer-capabilities.md`. Do not pull them into this harness.

## 6. Current-state audit

- `max/context/README.md` is a placeholder only
- Sidecar has schema/intent, no HTTP server
- No fixtures binaries
- Live is not available in CI

## 7. Assumptions, constraints, risks, and decisions

- Live 12.2+ with Max 9 `v8` is the target. If only Max 8 `js` is present, use `js` + `live.thisdevice` and record the deviation.
- Device type: Max **audio effect** so it hears the host track; LiveAPI still sees the set.
- `CONTEXT_SIDECAR_PORT` defaults to `8765` when unset.
- Risk: frozen/record-enabled tracks reject clip create. Surface the error; do not claim success.
- Risk: owner machine must have Live + Max for Live for the write test.

## 8. Dependencies

Sidecar must be running before Run/Apply. Fixtures must exist before Apply. Phase 0 schemas must remain valid.

## 9. Architecture and affected systems

```text
Context.amxd (plugin~ / plugout~ + live.UI + v8)
  -> HTTP 127.0.0.1:CONTEXT_SIDECAR_PORT
context_sidecar.http
  -> validate_intent(IntentRequest)
  -> echo IntentRequest + empty_arrangement preview
Apply
  -> LiveAPI Track.create_audio_clip / create_midi_clip
```

## 10. Files and paths in scope

- `max/context/` (Max Project, `Context.amxd`, `code/liveapi_snapshot.js`, `code/liveapi_writer.js`)
- `sidecar/src/context_sidecar/http.py` (or equivalent)
- `sidecar/tests/test_http.py`
- `fixtures/silence.wav` (generated, not copyrighted)
- `fixtures/empty.mid` (generated)
- `docs/runbooks/context-liveapi-harness.md` (manual Live checklist)
- Phase 0 contracts: do not break `schema.py` / `intent.py`

## 11. Supporting documents to create or update

- `docs/runbooks/context-liveapi-harness.md`
- Engineering evidence/handoff under the workstream
- `.cursor/STATE.md` after verification

## 12. Ordered implementation tasks

1. **Fixtures**
   - Dependencies: none
   - Files: `fixtures/`
   - Notes: generate 1s silent stereo WAV and a one-bar empty MIDI with stdlib or a tiny script committed
   - Evidence: files exist and are readable
   - State: pending

2. **Sidecar HTTP**
   - Dependencies: intent schema
   - Files: `sidecar/src/context_sidecar/http.py`, `sidecar/tests/test_http.py`
   - Notes: stdlib `http.server` is enough. Bind `127.0.0.1` only. `GET /health` → `{"ok": true}`. `POST /intent` validates JSON with `validate_intent` and returns `{"intent": ..., "preview": empty_arrangement()}` or 400. Reject empty prompt.
   - Evidence: `PYTHONPATH=src python -m unittest tests.test_http -v` (or file-path equivalent) passes
   - State: pending

3. **LiveAPI snapshot**
   - Dependencies: Live 12
   - Files: `max/context/code/liveapi_snapshot.js`
   - Notes: after `live.thisdevice` bang, walk `live_set` tracks/clips/tempo; infer role from track name (drums/bass/etc.); fill `ProjectSnapshot` + `host_track` from `this_device` canonical path
   - Evidence: documented JSON example from a test set, or console dump in the runbook
   - State: pending

4. **Writer**
   - Dependencies: fixtures, snapshot
   - Files: `max/context/code/liveapi_writer.js`
   - Notes: Apply calls `create_audio_clip(abs_path, position)` on an audio track and `create_midi_clip(start, length)` on a MIDI track. Prefer creating or targeting unlocked tracks. Never write if sidecar-down or prompt empty.
   - Evidence: Live checklist — two clips appear; Undo removes them
   - State: pending

5. **Device chrome**
   - Dependencies: HTTP, snapshot, writer
   - Files: `max/context/Context.amxd` (unfrozen)
   - Notes: implement all ten design-spec rows. Send every `IntentRequest` field listed in section 1a. Drop-in/reference may be typed paths in phase 1. Audition must play or no-op without writing clips. Apply uses fixtures only. Status copy from the design spec.
   - Evidence: screenshot or runbook steps covering empty prompt, sidecar down, Run echo, Apply, Undo
   - State: pending

6. **Packaging**
   - Dependencies: chrome works
   - Notes: keep unfrozen in git. Do not freeze for distribution yet.
   - Evidence: README updated
   - State: pending

## 13. Adaptive role and delegation map

| Role ID | Required or skipped | Reason | Predecessor | Owned paths | Gate evidence | Status |
|---|---|---|---|---|---|---|
| `product-manager-subagent` | required | Journeys C-10–C-14 already specified; confirm harness acceptance | phase 0 PM | PRD | harness meets P-1/P-4 | pending |
| `ui-ux-developer-subagent` | required | Device chrome | PM | design spec + amxd layout | states in matrix | pending |
| `software-engineer-subagent` | required | HTTP, Max, fixtures | UX | `sidecar/`, `max/context/`, `fixtures/` | tests + runbook | pending |
| `security-engineer-subagent` | required | localhost bind, file_path | Eng | review | 127.0.0.1; no secrets | pending |
| `growth-marketing-subagent` | skipped | No new public claims or launch this phase | — | — | skip: internal harness | pending |
| `project-lead-subagent` | required | Reconcile phase 1 | Security | delivery notes | verdict | pending |

Growth skip is valid: no audience, claims, or measurement change beyond the existing allowlist.

## 14. Test and validation matrix

| Requirement | Validation method | Expected evidence | Status |
|---|---|---|---|
| C-2 sidecar health | HTTP unittest + device disable | `/health` 200; UI fail closed | pending |
| C-10 prompt | HTTP 400 on empty; UI Run disabled | tests + runbook | pending |
| C-11 snapshot | LiveAPI dump | JSON has tracks + host_track | pending |
| C-12 drop-in | device field sent only in drop_in mode | HTTP 400 if missing/wrong mode | pending |
| C-13 reference knobs | reverence/abstraction in payload; knobs disabled until reference path | tests + runbook | pending |
| C-14 granular knobs | scope, amount, wet, locks, focus, tempo/key lock, variation, target section, audition vs apply exist | runbook | pending |
| P-1 audition | Audition does not create clips | runbook | pending |
| P-4 fail closed | sidecar down disables Run/Apply | runbook | pending |
| P-8 host role | inferred_role from track name (drums if name matches) | snapshot dump | pending |
| C-5 write + undo | Live manual | two clips; Undo | pending |
| C-7 C-8 | inspection | no weights, no secrets | pending |

## 15. Security, privacy, reliability, accessibility, and performance checks

- Bind 127.0.0.1 only (SEC-004).
- `file_path` non-empty string (SEC-003); phase 1 Apply uses only repo fixtures or user-typed paths, never shell interpolation.
- No network model calls.
- Accessibility: labels on wells and knobs; health is text plus dot.
- Reliability: Apply errors on frozen/record-enabled tracks.

## 16. Environment-variable registry

| Variable name | Purpose | Scope/environment | Required by phase | Source/provider | Status |
|---|---|---|---|---|---|
| `CONTEXT_SIDECAR_PORT` | listen port, default 8765 | local | 1 | operator | name only |

## 17. Deferred human-action queue

| Action | Why agent cannot perform it | Earliest required phase | Blocking now? | Final-checklist destination |
|---|---|---|---|---|
| Install Live 12 + Max for Live | App license | 1 | yes for write evidence | yes |
| Confirm clip-create on owner machine | Physical Live | 1 | yes for C-5 VERIFIED | yes |
| Steinberg / Apple / JUCE | Legal | 6 | no | yes |

## 18. Rollback and recovery

Stop the sidecar process. Delete unfrozen Max Project copies under `~/Documents/Max */Max for Live Devices` if Live duplicated them. Revert `sidecar/` HTTP files. Do not freeze a broken device.

## 19. Acceptance criteria

- Sidecar HTTP tests pass without Live
- Device fails closed when sidecar is down or prompt is empty
- Snapshot JSON includes host track and at least one other track when present
- Apply creates one audio and one MIDI clip from fixtures on a non-frozen test set
- Live Undo removes those clips
- Audition does not write
- All owner knobs exist and are sent: reverence, abstraction, amount, wet, scope, focus, locks, tempo/key lock, variation, optional target section
- Drop-in and reference paths are sent only in their modes
- Status copy matches the design spec
- No MusicGen weights, no secrets, device remains unfrozen in git

## 20. Completion evidence

Sidecar unit tests: 31 OK (`unittest discover`, 2026-08-28). HTTP binds `127.0.0.1`. Fixtures generated. Max Project + unfrozen `Context.amxd` (patcher JSON), `liveapi_snapshot.js`, `liveapi_writer.js`, `context_device.js`, `sidecar_client.js`, runbook written.

C-5 Live clip-create + Undo: **UNVERIFIED** (Live 12 not available in this environment). Recorded in the runbook and final checklist.

## 21. Deviations and follow-ups

If Live is unavailable, mark C-5 `UNVERIFIED` and still ship HTTP + chrome + runbook. Do not call phase 1 complete until the owner-machine write test runs or the limitation is recorded in the final checklist.

## 22. Next Plan Generation Prompt

Read `/AGENTS.md`, the complete core agent context, `/instructions/PROJECT_PLANNING.md`, `/instructions/ROLES.md`, the original `docs/plans/phase_0_foundations_plan.md`, this completed phase plan, the active workstream manifest and role handoffs, all completion evidence, current repository state, active blockers, and relevant decisions. Confirm this phase and every required role gate are fully implemented and validated. Then generate exactly one exhaustive next phase plan at `docs/plans/phase_2_analysis_symbolic_plan.md`. Derive it from the phase-0 roadmap and verified current state, preserve unresolved requirements, include all required plan sections and adaptive role decisions, defer non-blocking human actions to the final phase, and do not implement the next phase until the plan is written.
