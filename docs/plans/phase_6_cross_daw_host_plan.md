---
plan: phase_6_cross_daw_host
status: implemented_file_drop
created: 2026-08-28
updated: 2026-08-28
owner: lead-agent
source_phase: docs/plans/phase_5_pedalboard_dsp_plan.md
workstream: docs/workstreams/20260828-context-ai-arrangement/manifest.md
---

# Phase 6: Cross-DAW host and export

## 1. Objective

MIDI type-1 + stem file-drop export. Same sidecar contract. No `.als`. No GarageBand arrange claim.

## 10. Files

`sidecar/src/context_sidecar/export.py`, `plugin/README.md`.

## 17. Deferred human actions

Steinberg VST3, Apple signing, JUCE/RNBO licenses.

## 20. Completion evidence

`export_session` copies MIDI + WAV and sets `wrote_als: false`.

## 22. Next prompt

Generate `docs/plans/phase_7_harden_handoff_plan.md`.
