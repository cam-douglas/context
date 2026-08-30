# Decision: als-json + DawDreamer session export

Date: 2026-08-30

## Decision

The owner asked to wire **als-json** (Ableton session parse/write) and **DawDreamer** so Context can export arrangements back into a DAW session with integrity.

This supersedes the earlier lock “unofficial `.als` write remains forbidden” in `docs/decisions/2026-08-28-context-owner-stack-wiring.md` and `docs/decisions/2026-08-28-context-coproducer-capabilities.md`.

## Rules that still hold

- Never overwrite the user’s source `.als`. Export always writes a new file.
- Existing tracks, clips, devices, and locators in a cloned source set stay in place. Context adds new tracks named `Context …`.
- Sidecar stays on `127.0.0.1`.
- DawDreamer is an offline renderer, not a DAW. JUCE render runs in a subprocess so the HTTP thread cannot hang.
- File-drop WAV/MIDI remains the cross-DAW path for Logic, GarageBand, and FL.

## Status

Implemented in `sidecar/`. Live 11 File → Open of a written set is an owner smoke check, not yet verified in this session.
