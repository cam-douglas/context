---
plan: phase_11_session_export
status: implemented
created: 2026-08-30
updated: 2026-08-30
owner: lead-agent
source_phase: docs/plans/phase_9_owner_stack_plan.md
workstream: docs/workstreams/20260830-als-json-session-export/manifest.md
---

# Phase 11: als-json session export + DawDreamer render

## 1. Objective

Export the engine’s arrangement into a cloned Ableton Live Set (and a lossless als-json tree) while preserving the user’s existing session, and render the same arrangement offline with DawDreamer.

## 2. Relation to project end-state

Closes the co-producer “populate the DAW” gap without rewriting the open Live Set from inside a VST.

## 3. Entry criteria

Phase 9 compose path writes WAV/MIDI. Owner explicitly requested `.als` export.

## 4. Scope

- Lossless `.als` ↔ JSON codec
- Clone source set or Live 11 DefaultLiveSet
- Additive Context tracks, clips, locators, tempo
- `/export` and compose write `*.als` + `*.als.json`
- DawDreamer 0.9.0 render worker

## 5. Non-goals

In-place overwrite of a user set. Logic/GarageBand/FL project rewrite. VST hosting legal clearance. Opening the written set inside Live (owner smoke).

## 6. Validation

`PYTHONPATH=src .venv/bin/python -m unittest tests.test_session_export tests.test_phase2_to_6 tests.test_http tests.test_compose tests.test_dsp tests.test_stack` — 46 tests OK.

## 7. Next Plan Generation Prompt

Read `/AGENTS.md`, core context, this completed plan, and current repository state. Generate exactly one next phase plan only if a later owner request requires it.
