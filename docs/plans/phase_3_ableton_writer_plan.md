---
plan: phase_3_ableton_writer
status: implemented_unverified_live
created: 2026-08-28
updated: 2026-08-28
owner: lead-agent
source_phase: docs/plans/phase_2_analysis_symbolic_plan.md
workstream: docs/workstreams/20260828-context-ai-arrangement/manifest.md
---

# Phase 3: Ableton writer (loop-to-song)

## 1. Objective

Build a ~3-minute arrangement plan from a 4/8-bar loop plus genre, including locators, colors, automation, and symbolic variation actions. Live writes remain LOM-only.

## 2–11. Scope

`context_sidecar.arrange.loop_to_song`, `arrangement_write_actions`, `POST /arrange`. Non-goals: generation, `.als` write.

## 12. Tasks

1. Loop-to-song planner. Evidence: schema-valid plan with intro/build/drop.
2. LOM action list (clips, locators, colors, automation). Evidence: unittest.
3. JS `applyArrangement` for Live. Evidence: runbook (Live UNVERIFIED).

## 13. Roles

Engineering required. Growth skipped (no new public claims). Security: no `.als`.

## 14–19.

Acceptance: plan validates; actions include locator + color; no `.als`.

## 20. Completion evidence

`test_loop_to_song_validates` OK. Live apply of the full plan UNVERIFIED.

## 22. Next Plan Generation Prompt

Confirm this phase. Generate `docs/plans/phase_4_generation_adapters_plan.md` next. Do not implement until written.
