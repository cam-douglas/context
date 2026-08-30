---
plan: phase_9_owner_stack
status: implemented
created: 2026-08-28
updated: 2026-08-30
owner: lead-agent
source_phase: docs/plans/phase_8_juce_host_plan.md
workstream: docs/workstreams/20260828-context-stack-wiring/manifest.md
---

# Phase 9: Owner stack wiring

## Objective

Install and wire the owner-provided scientific / MIDI / DSP stack into the running sidecar so Apply is no longer stdlib-only oscillators.

## Non-goals

`.als` write, weight downloads, commercial API calls, Skia/WebGL/FMOD/Wwise, TensorFlow Magenta models (MelodyRNN/MusicVAE). Magenta music format is in via `note-seq`.

## Evidence

- Installed in `sidecar/.venv`: librosa, scipy, numpy, pedalboard, mido, pretty_midi, music21, note-seq, pydub, pyroomacoustics, soundfile.
- Compose uses music21 scales, note-seq quantize, mido MIDI write, pretty_midi fallback, pedalboard render, then a pyroomacoustics room IR on the written WAV.
- Analysis uses librosa + scipy when present.
- `/health` reports `probe()`.
