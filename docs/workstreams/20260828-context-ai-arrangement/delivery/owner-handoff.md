# Owner handoff: Context

Date: 2026-08-28

## What is done without you

- Sidecar, schemas, analysis, arrange, gated adapters, DSP plans, file-drop export.
- 44 sidecar tests + `scripts/owner-smoke.sh` (`/health` and `/intent` on 127.0.0.1:8765).
- Optional librosa + pedalboard in `sidecar/.venv`.
- `.env.example` and empty `.cache/context-models`.
- Max Project copied into your Max 8/9 folders.
- Claims audit: no MusicGen device label, no `.als` writer.

## What only you can finish

1. **C-5 in Live** — Do **not** File → Open the maxpat. Click **Edit** on the Max Audio Effect **on the track**, type `js /Users/camdouglas/context/max/context/code/context_harness.js`, connect a button → `apply` → js, add a MIDI track, click Apply, look at **Session View**. Details: `docs/runbooks/context-liveapi-harness.md`.
2. **Save as Max for Live Device** in Max 9 if you want a binary `.amxd` in the User Library. Do not freeze until C-5 passes.
3. **Legal later** — Steinberg, Apple signing, JUCE/RNBO, Stable Audio Open. Do not publish to a plugin store yet.

## Do not do

- Do not set `CONTEXT_ENABLE_GENERATION=1` until a reviewed adapter exists.
- Do not add MusicGen or AudioLDM 2 weights.
- Do not commit `.env` or API keys.
