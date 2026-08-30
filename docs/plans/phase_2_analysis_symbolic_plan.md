---
plan: phase_2_analysis_symbolic
status: implementing
created: 2026-08-28
updated: 2026-08-28
owner: lead-agent
source_phase: docs/plans/phase_1_liveapi_harness_plan.md
workstream: docs/workstreams/20260828-context-ai-arrangement/manifest.md
---

# Phase 2: Analysis, symbolic core, mix audits

## 1. Objective

Add read-only analysis: tempo/key/energy/section candidates, mix masking audits, `build` section label, optional genre target, and symbolic MIDI helpers. No Live writes. No generation weights.

## 2. Relation to project end-state

Feeds phase 3 loop-to-song and phase 5 ducking with diagnostics.

## 3. Entry criteria and inherited evidence

Phase 1 sidecar tests 31 OK. C-5 Live write UNVERIFIED.

## 4. Scope

- `POST /analyze` → `AnalysisReport`
- librosa optional; stdlib/wave fallback
- Mix masking report
- `build` in SECTION_LABELS
- Optional `genre_target` on intent
- pretty_midi/music21 optional; stdlib MIDI parse for variation prep

## 5. Non-goals

Apply writes, Demucs, generation, pedalboard apply, `.als` write.

## 6. Current-state audit

HTTP has `/health` and `/intent` only.

## 7. Assumptions

Analysis is offline in the sidecar. Missing librosa does not fail the suite.

## 8. Dependencies

Phase 1 schemas and HTTP server.

## 9. Architecture

`context_sidecar.analysis` + `mix_audit` + `/analyze`.

## 10. Files

- `sidecar/src/context_sidecar/analysis.py`
- `sidecar/src/context_sidecar/mix_audit.py`
- `sidecar/src/context_sidecar/midi_symbolic.py`
- `sidecar/tests/test_analysis.py`

## 11. Supporting documents

This plan; STATE after verification.

## 12. Ordered implementation tasks

1. Schema `build` + optional genre. Evidence: existing tests still pass.
2. Analyze host/drop-in/reference paths. Evidence: unittest.
3. Mix audit from two stems or bands. Evidence: unittest.
4. Wire `/analyze`. Evidence: HTTP test.

## 13. Adaptive role map

| Role ID | Required or skipped | Reason | Predecessor | Owned paths | Gate evidence | Status |
|---|---|---|---|---|---|---|
| product-manager-subagent | required | C-18 | phase 1 | PRD | analyze is read-only | pending |
| ui-ux-developer-subagent | skipped | Inspect already specified; no new chrome required this phase | PM | — | skip: inspect exists | done |
| software-engineer-subagent | required | analysis | PM | sidecar | tests | pending |
| security-engineer-subagent | required | file_path local only | Eng | review | no network | pending |
| growth-marketing-subagent | skipped | no claims change | — | — | skip | done |
| project-lead-subagent | required | reconcile | Sec | delivery | verdict | pending |

## 14. Validation matrix

| Requirement | Method | Evidence | Status |
|---|---|---|---|
| C-3 | unittest | AnalysisReport on fixture | pending |
| C-18 | unittest | masking hits | pending |

## 15. Security

Local files only. No shell interpolation.

## 16. Environment variables

None new.

## 17. Deferred human actions

Live still required for C-5.

## 18. Rollback

Revert analysis modules and `/analyze`.

## 19. Acceptance

`/analyze` returns report; mix hits listed; no writes; tests pass.

## 20. Completion evidence

`analyze_audio`, mix audit, `genre_target`, MIDI variation helpers, `/analyze` and `/mix-audit` wired. Covered by `tests/test_phase2_to_6.py`. librosa/CLAP/music21 remain optional imports.

## 21. Deviations

librosa/CLAP/music21 are optional imports.

## 22. Next Plan Generation Prompt

Read `/AGENTS.md`, the complete core agent context, `/instructions/PROJECT_PLANNING.md`, `/instructions/ROLES.md`, `docs/plans/phase_0_foundations_plan.md`, this completed phase plan, the workstream, evidence, and decisions. Confirm this phase is implemented and validated. Then generate exactly one next phase plan at `docs/plans/phase_3_ableton_writer_plan.md`. Do not implement that phase until the plan is written.
