---
plan: phase_4_generation_adapters
status: implemented_gated
created: 2026-08-28
updated: 2026-08-28
owner: lead-agent
source_phase: docs/plans/phase_3_ableton_writer_plan.md
workstream: docs/workstreams/20260828-context-ai-arrangement/manifest.md
---

# Phase 4: License-gated generation, search, stems

## 1. Objective

Ship adapter seams: texture/transition synthesis, CLAP/filename search, Demucs split. Default off. Block MusicGen and AudioLDM 2.

## 4. Scope

`adapters.py`, `search.py`, `stems.py`, `/synthesize`, `/search`, `/stems`.

## 5. Non-goals

Vendoring weights. Commercial MusicGen/AudioLDM 2.

## 16. Environment variables

| Variable | Purpose | Phase | Status |
|---|---|---|---|
| CONTEXT_ENABLE_GENERATION | adapter master switch, default 0 | 4 | name only |
| CONTEXT_ENABLE_DEMUCS | local Demucs, default 0 | 4 | name only |
| CONTEXT_ENABLE_CLAP | optional CLAP backend | 4 | name only |
| CONTEXT_MODEL_CACHE_DIR | cache dir if owner installs weights | 4 | name only |

## 20. Completion evidence

Tests: blocked MusicGen, generation off, Demucs disabled, local search OK.

## 22. Next prompt

Generate `docs/plans/phase_5_pedalboard_dsp_plan.md`.
