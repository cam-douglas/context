# Blocker: Context device appears to do nothing in Live

## Symptoms

- Max Audio Effect / Context chrome is open in Ableton Live 11 Suite.
- Run / Audition / Apply produce no clips and no obvious status change.

## Evidence

- This Mac is Live **11.3.43** with bundled Max **8.5.8**. Live 12 is not installed.
- `Track.create_audio_clip` and `Track.create_midi_clip` are Live 12 arrangement APIs. The first harness called those and threw on Live 11.
- `File → Open Context.maxpat` from Live-launched Max usually opens a **detached** window. The device still on the track stays the default `plugin~` / `plugout~` pass-through, so clicking Apply on the Live device does nothing.
- `js context_harness.js` failed when the script was not on the Max search path (`code/` vs patcher folder; `dependency_cache` bootpath was `~/context/max/context`).

## Attempts

- Wired `Context.maxpat` and asked the owner to File → Open it into the on-track editor (failed / still inert).
- Search-path instructions for `max/context/code` (easy to skip).

## Files

- `max/context/code/context_harness.js`
- `max/context/Context.maxpat`
- `docs/runbooks/context-liveapi-harness.md`

## Unknowns

- Whether the owner is clicking the Live device or a detached Max window.
- Whether a MIDI track exists in the set.
- Whether they are looking at Arrangement View (Session clips are invisible there unless duplicated).

## Status

**Superseded as the primary owner path** on 2026-08-28. The JUCE AU/VST3/Standalone host is the operating device. Keep this file until someone explicitly verifies or abandons Max C-5.

## Next actions

1. Prefer `docs/runbooks/context-juce-host.md`.
2. Max-only recovery remains: type the js object into the on-track Edit window (not File → Open).

## Resolution criteria

- Apply creates a Session MIDI clip named `Context`.
- Live Undo (`Cmd+Z`) removes it.
- Status line or Max Window reports the write.
- Then move this file to `blockers-fixed/`.
