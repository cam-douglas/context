---
plan: phase_0_foundations
status: verified_foundations
created: 2026-08-28
updated: 2026-08-28
owner: lead-agent
source_phase: none
workstream: docs/workstreams/20260828-context-ai-arrangement/manifest.md
---

# Phase 0: Context foundations

## 1. Objective

Establish the repository, contracts, license matrix, arrangement schema, **intent/project-context schema**, and role pipeline so later phases can implement the prompt-driven Max for Live instrument/effect without inventing product intent.

## 2. Relation to project end-state

Phase 0 does not ship Context to producers. It makes phase 1 (LiveAPI harness) possible and records the full map through owner handoff.

## 2a. Whole-project phase map

Owner 2026-08-28 added co-producer capabilities (`docs/decisions/2026-08-28-context-coproducer-capabilities.md`). The map is:

0. Foundations — this file; verified.
1. LiveAPI harness — `docs/plans/phase_1_liveapi_harness_plan.md` (next implementation).
2. Analysis, symbolic core, read-only mix audits (librosa, CLAP, music21, pretty_midi).
3. Ableton writer: loop-to-song, locators, automation, colors, variation via LOM (not `.als`).
4. License-gated generation, CLAP sample search, Demucs stems. No MusicGen / AudioLDM 2 in the commercial path.
5. Pedalboard auto-staging, room-corrector curve, dawdreamer offline VST rehearsal.
6. Cross-DAW VST3/AU host: MIDI/stem file-drop. No GarageBand arrange.
7. Harden, freeze `.amxd`, owner handoff, final checklist.

Detailed `phase_N_*.md` files after 1 are written only after the prior phase is verified.

## 3. Entry criteria and inherited evidence

- Owner named the product Context and authorized Build.
- Launch research captured in `docs/research/context-stack.md` and `docs/blueprints/2026-08-28_context.md`.
- Bootstrap ran as the first mutation and failed on missing protected `AGENTS.md`.

## 4. Scope

- Control-plane repair path for the owner
- Blueprint, workstream, research, decisions
- Sidecar package skeleton, arrangement schema, and intent/knob/project snapshot tests
- Max Project directory placeholder
- Role charters and plans
- Environment-variable registry (names only)

## 5. Non-goals

Max patching, LiveAPI clip writes, Demucs install, generative models, RNBO/JUCE export, production publish.

## 6. Current-state audit

This working tree had `.cursor/` only. Bootstrap created `docs/` indexes. Application source did not exist. Root `AGENTS.md`, `.cursorignore`, and `.github/workflows/agent-governance.yml` are missing and agent-blocked.

## 7. Assumptions, constraints, risks, and decisions

- Name is Context (`docs/decisions/2026-08-28-context-product-name.md`).
- Ableton-first; cross-DAW later.
- MusicGen weights stay out of the commercial path. Prompt UI is required (`docs/decisions/2026-08-28-context-granular-intent.md`).
- Risk: bootstrap remains `BLOCKED` until the owner repair script runs.

## 8. Dependencies

Owner repair → bootstrap success → preflight not `BLOCKED`. Product docs and sidecar skeleton do not wait on Live.

## 9. Architecture and affected systems

See blueprint section 10. Phase 0 materializes `sidecar/` and `max/context/README.md` only.

## 10. Files and paths in scope

- `docs/blueprints/2026-08-28_context.md`
- `docs/plans/phase_0_foundations_plan.md`
- `docs/workstreams/20260828-context-ai-arrangement/`
- `docs/research/context-stack.md`
- `docs/handover/apply-missing-control-plane-files.sh`
- `sidecar/`
- `max/context/`
- `fixtures/`
- `.cursor/STATE.md`, continuation, blocker

## 11. Supporting documents to create or update

Role charters/plans under the workstream. Later phase plans are not created now.

## 12. Ordered implementation tasks

1. Run bootstrap; on AGENTS.md failure, provide owner repair. Evidence: blocker + script.
2. Write blueprint, research, name decision, manifest. Evidence: files exist.
3. Sidecar arrangement + intent schema tests. Evidence: `test_schema.py` and `test_intent.py` pass.
4. Max Project placeholder README. Evidence: path exists.
5. Role charters and plans. Evidence: six role directories.
6. After owner repair: rerun bootstrap and preflight. Evidence: exit 0.

## 13. Adaptive role and delegation map

| Role ID | Required or skipped | Reason | Predecessor | Owned paths | Gate evidence | Status |
|---|---|---|---|---|---|---|
| `product-manager-subagent` | required | New product contract | lead | workstream PM dir | charter/plan/evidence/handoff | in_progress |
| `ui-ux-developer-subagent` | required | Device UI | PM | workstream UX dir | same | pending |
| `software-engineer-subagent` | required | Sidecar/Max | UX | `sidecar/`, `max/context/` | tests | pending |
| `security-engineer-subagent` | required | Tier 3 | Eng | workstream Sec dir | license/privacy review | pending |
| `growth-marketing-subagent` | required | Claims/GTM | Sec | workstream Growth dir | claims spec | pending |
| `project-lead-subagent` | required | Reconciliation | Growth | delivery/ | owner-handoff draft | pending |

## 14. Test and validation matrix

| Requirement | Validation method | Expected evidence | Status |
|---|---|---|---|
| C-4 schema | unit tests | sidecar tests pass | done |
| C-10–C-13 intent | unit tests | `test_intent.py` 6 OK | done |
| C-7 license | inspect research doc | MusicGen marked blocked | done |
| C-8 no secrets | file inspection | no values in docs | in_progress |
| Bootstrap | owner repair + rerun | exit 0; preflight READY | done |

## 15. Security, privacy, reliability, accessibility, and performance checks

Local-only V1. No network adapters on. Sidecar bind to localhost. Accessibility specified in UI/UX phase, not coded here.

## 16. Environment-variable registry

| Variable name | Purpose | Scope/environment | Required by phase | Source/provider | Status |
|---|---|---|---|---|---|
| `CONTEXT_SIDECAR_PORT` | localhost port | local | 1 | operator | name only |
| `CONTEXT_MODEL_CACHE_DIR` | optional weight cache | local | 4 | operator | name only |
| `CONTEXT_ENABLE_GENERATION` | adapter master switch, default 0 | local | 4 | operator | name only |
| `ELEVENLABS_API_KEY` | future adapter | local/secret manager | deferred | ElevenLabs | not requested |

## 17. Deferred human-action queue

| Action | Why agent cannot perform it | Earliest required phase | Blocking now? | Final-checklist destination |
|---|---|---|---|---|
| Run `docs/handover/apply-missing-control-plane-files.sh` | Protected-file policy | 0 | no (done) | yes |
| Live 12 + Max for Live install | License/app ownership | 1 | no | yes |
| Steinberg / Apple / JUCE licenses | Legal/account | 6 | no | yes |
| Cloud API accounts | Billing/terms | 4+ | no | yes |

## 18. Rollback and recovery

Delete phase-0 application files if abandoned. Do not delete `.cursor/`. Owner repair script is idempotent.

## 19. Acceptance criteria

- Blueprint, manifest, research, name decision exist
- Sidecar arrangement and intent schema tests pass
- All six roles have charter and plan
- Blocker records the bootstrap gap
- No secrets committed

## 20. Completion evidence

Bootstrap READY after owner repair plus `.DS_Store` ignore. Sidecar `test_schema.py` (4) and `test_intent.py` (6) pass. Live device work remains phase 1.

## 21. Deviations and follow-ups

Product planning continued after bootstrap failure because the failure is a protected-file permission, not a product unknown. Live device work stays in phase 1.

## 22. Next Plan Generation Prompt

Read `/AGENTS.md`, the complete core agent context, `/instructions/PROJECT_PLANNING.md`, `/instructions/ROLES.md`, the original `docs/plans/phase_0_foundations_plan.md`, this completed phase plan, the active workstream manifest and role handoffs, all completion evidence, current repository state, active blockers, and relevant decisions. Confirm this phase and every required role gate are fully implemented and validated. Then generate exactly one exhaustive next phase plan at `docs/plans/phase_1_liveapi_harness_plan.md`. Derive it from the phase-0 roadmap and verified current state, preserve unresolved requirements, include all required plan sections and adaptive role decisions, defer non-blocking human actions to the final phase, and do not implement the next phase until the plan is written.
