# 2026-08-28 continuation

## Context launch

- Owner named the product Context and authorized Build.
- First mutation: `bash .cursor/scripts/bootstrap.sh` failed on missing root `AGENTS.md`.
- Write to `AGENTS.md` denied by fail-closed policy. Owner repair: `docs/handover/apply-missing-control-plane-files.sh`.
- Materialized blueprint, phase 0 plan, workstream, research corpus, sidecar schema (4 tests OK), Max/fixtures placeholders, and all six role charters/plans/handoffs.
- Independent PM review: CONDITIONAL ([product-manager-subagent](1eaf2352-6552-4abf-b682-4f45595406fd)).
- Independent Security review: CONDITIONAL ([security-engineer-subagent](c96b164a-7881-451e-bfb0-33e11c389b43)). No high/critical.
- Project Lead: CONDITIONAL. Next human action is the owner repair, then bootstrap + preflight.

## Granular intent (same day)

- Owner required prompt-driven, track-aware, project-wide context; drop-in modify; reference + reverence/abstraction; extra knobs (scope, amount, wet, locks, focus).
- Decision: `docs/decisions/2026-08-28-context-granular-intent.md`.
- Sidecar: `context_sidecar.intent` + `tests/test_intent.py`.
- Earlier “no V1 generation UI” rule is superseded for the prompt surface only; MusicGen remains blocked.

## Bootstrap READY

- Owner created `AGENTS.md`, `.cursorignore`, and `agent-governance.yml`.
- Bootstrap then failed because `.cursor/.DS_Store` was an orphan. `validate-launch.mjs` now skips Finder/noise files; `.DS_Store` deleted.
- Evidence: bootstrap complete; preflight `READY` at 2026-08-28T08:53:05.350Z; 79 classified files.
- Blocker moved to `blockers-fixed/control-plane-bootstrap.md`.

## Phase 1 plan (same day)

- Owner asked to update the plan with their instructions so they can build from there.
- Rewrote Cursor plan `forma_ai_arrangement_7cc830f7.plan.md`: Context name, owner journeys, full chrome, architecture, phase map. Stale Forma/bootstrap-blocked text removed.
- Wrote `docs/plans/phase_1_liveapi_harness_plan.md` with owner contract (journeys, knobs, `IntentRequest` fields) and ordered harness tasks.
- Phase 1 ships chrome and echo; does not generate music. Next implementation: fixtures, HTTP, LiveAPI snapshot/writer, device, runbook.
- Active plan in STATE now points at phase 1. Do not generate phase 2 until phase 1 is verified.

## Co-producer capabilities (same day)

- Owner added loop-to-song, tension/transitions, symbolic variation, mix audits, auto-ducking, room corrector, CLAP search, texture synth, Demucs, LOM session populate, dawdreamer rehearsal.
- Decision: `docs/decisions/2026-08-28-context-coproducer-capabilities.md`. Requirements C-15–C-24.
- Locks kept: no unofficial `.als` write (LOM + Live save); no commercial MusicGen/AudioLDM 2; dawdreamer is not a DAW.

## Build implementation (same day)

- Phase 1: fixtures, HTTP, snapshot/writer, device chrome, Max Project, runbook. 31 then 44 tests OK.
- Phases 2–6: analysis, mix audit, loop-to-song, gated adapters, DSP plans, MIDI/stem export.
- Phase 7: `docs/plans/final_implementation_checklist.md`.
- Live C-5 clip-create + Undo remains UNVERIFIED.
- Cursor plan file was not edited.

## Owner actions (same day)

- This Mac has Live 11 Suite 11.3.43 and Max 9.0.4 (not Live 12).
- Completed: sidecar smoke, `.env.example`, model cache dir, librosa 0.11 + pedalboard 0.9.24 in `sidecar/.venv`, Max Project copies, claims audit.
- Still owner-only: interactive C-5 in Live, Save as M4L device, legal/publish.
- Handoff: `docs/workstreams/20260828-context-ai-arrangement/delivery/owner-handoff.md`.

## Max trial (same day)

- Owner blocked on Step 3: standalone Max 9.0.4 cannot save M4L devices (trial).
- Workaround: Live 11 Suite bundled Max 8.5.8 at `Ableton Live 11 Suite.app/Contents/App-Resources/Max/Max.app`. Create Max Audio Effect in Live, Edit from Live, open `Context.maxpat`, save from that window. Do not use `/Applications/Max.app`.
- Owner could not load repo `Context.amxd` in Live (it is patcher JSON). Recovery: use the Max Audio Effect already on the track; save a User Library preset from Live’s device header. Do not drag repo/Documents `Context.amxd` into Live.

## Live device still inert (same day)

- Owner: plugin open in Live, buttons do nothing. Two causes: (1) File → Open `Context.maxpat` is a detached window, on-track device stays empty; (2) Apply called Live 12 `create_audio_clip` / `create_midi_clip`, which Live 11.3.43 does not have.
- Remediation: `context_harness.js` now writes a Session MIDI clip via `clip_slots N create_clip`, names it Context, tries `duplicate_clip_to_arrangement`, and uses an absolute js path. Runbook path is type-in-device, not File → Open.
- Blocker: `.cursor/memory/blockers/live-harness-apply-inert.md`. C-5 still UNVERIFIED.

## JUCE host pivot (same day)

- Owner: Max is not working; turn the project into a standalone VST.
- Decision: `docs/decisions/2026-08-28-context-juce-host-primary.md`. File-drop only; no Live Set rewrite.
- Built JUCE 8.0.8 AU + VST3 + Standalone via `scripts/build-plugin.sh`. Installed to `~/Library/Audio/Plug-Ins/`.
- Smoke: `CONTEXT_SMOKE_APPLY=1` wrote `~/Documents/Context Drops/Context.mid` and `Context.wav`.
- Workstream: `docs/workstreams/20260828-context-vst-host/`. Plan: `docs/plans/phase_8_juce_host_plan.md`.

## Blank drop files (same day)

- Owner: Apply generated files but they were blank. Cause: `Context.wav` was `fixtures/silence.wav`; MIDI was one C3; sidecar `/export` could also copy `empty.mid`.
- Fix: Apply writes an 8-note audible phrase (and captured host audio when the insert heard signal). Smoke: WAV peak 9157, MIDI 8 note-ons.
- Owner: output still blank. Drop folder was empty; Live insert likely wrote quiet 8s capture or they replayed the old silent clip. Second fix: always write a loud C-major scale with a new timestamped filename; capture only as Context-host-* if RMS > 0.05. Smoke: Context-20260828-195316.wav peak 21300 / RMS 12922.
- Owner: "make a house loop" produced a 1s blank clip. On disk `Context.wav` was still `fixtures/silence.wav` (176444 bytes, 1.00s); Live was on the old Context AU. Deleted that WAV. Wrote `HOUSE-LOOP.wav` (7.79s, peak 29162) to Desktop and Documents. Shipped **Context 2** (new AU/VST3 codes) and removed old Context.component/vst3.
- Owner: it ONLY makes house loops. Cause: `looksLikeHouse` matched "loop"/"beat"/"drum". Replaced with prompt parser + style engine (house only if "house"). Sidecar `compose.py` + `/compose` + plugin DropWriter. Tests: `tests.test_compose` OK.
- Owner: sidecar should run in the background while the plug-in is open. `SidecarSupervisor` starts `sidecar/scripts/run-sidecar.sh` when the editor opens if health is down; keeps it while any Context 2 instance is loaded; kills only a process it started when the last instance is removed. Bind remains 127.0.0.1. Standalone smoke: health ok in ~3s, sidecar stopped after quit.
- Owner: sidecar still down in Live. Live was already running; ChildProcess from the AU did not keep 8765 up (and last-instance kill may have torn it down). Installed LaunchAgent `com.context.sidecar` (KeepAlive), health `{"ok": true}` now. Plugin kickstarts the agent instead of owning a child.
- Owner: still defaulting to house. Evidence: Desktop `HOUSE-LOOP.wav` mtime 20:07 while current DropWriter never writes that name — Live still had house-only Context 2 in memory. `/intent` now also composes; Apply reads the text field; files are `{style}-{prompt}.wav`; stale HOUSE-LOOP deleted unless style is house. Shipped **Context 3** (Ctx3) and removed Context 2 bundles.
- Owner: install and wire the provided tech stack. Installed mido/pretty_midi/music21/pydub/pyroomacoustics into sidecar/.venv (librosa/scipy/pedalboard already present). Compose now uses music21 scales, pretty_midi, pedalboard. Analysis uses librosa+scipy. AudioLDM 2 still blocked. No .als write. Heavy models not vendored.
