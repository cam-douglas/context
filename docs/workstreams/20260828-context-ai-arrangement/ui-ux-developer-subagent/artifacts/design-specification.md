# Context device design specification

Host: Max for Live device that is both an **insert effect** (hears the host track) and a **session writer**. Not a web app.

Owner revision: prompt, drop-in, reference, reverence, abstraction, plus later co-producer surfaces. See `docs/decisions/2026-08-28-context-granular-intent.md` and `docs/decisions/2026-08-28-context-coproducer-capabilities.md`.

## Anatomy

1. Header: Context, sidecar health (dot + text).
2. Host strip: inferred role (e.g. Drums), scope (this track / selection / set), focus (playhead / loop / selected clip / host clip).
3. Prompt: single-line field plus Run. Examples as placeholder, not buttons that invent extra product modes.
4. Drop-in well: sample or loop. Visible when mode is drop-in or when a file is present.
5. Reference well: any audio. Reverence and Abstraction knobs (0–1) enabled when a reference is loaded.
6. Granular row: Amount, Wet, Tempo/key lock, Variation/Replace, Locks (count + “protect selected”).
7. Inspect: tempo, key, energy, section candidates, host role.
8. Preview: proposed sections, tracks, clip counts, and which locked items were left untouched.
9. Apply / Audition: Audition plays in-device (wet). Apply writes to the set. Both disabled without a valid preview. Apply disabled when sidecar is down.
10. Status: one line.

Later phases (do not block phase 1):

11. Genre target when staging a loop to a song.
12. Mix audit list (frequency, stems, suggested carve). Apply remains separate.
13. Local sample search field (CLAP).
14. Stem-split controls after a file is imported.
15. Optional room-sweep well.
16. Export MIDI/stems. Never a control labelled write `.als`.

## Copy

- Sidecar down: "Context sidecar is not running on localhost. Start it, then retry."
- Empty prompt: "Type what to do next, then run."
- Apply success: "Wrote clips into the arrangement. Undo in Live to revert."
- Apply failure: "Could not write every clip. Undo in Live if the arrangement looks partial."
- Empty source: "Play or select material on this track, or drop a loop."
- Reference missing knobs: knobs disabled until a reference is loaded.

Do not claim Logic or GarageBand project arrangement. Do not label a MusicGen or AudioLDM 2 backend. Do not offer “export Ableton project file” as a `.als` writer.

## Accessibility

High-contrast live.UI. Meaning not color-only. Knobs have numeric readouts. Drop wells have text labels, not icon-only. Large targets in the Live device width.
