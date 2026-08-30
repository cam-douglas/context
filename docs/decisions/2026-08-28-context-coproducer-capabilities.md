# Decision: Context is an intelligent co-producer, not a preset wrapper

- Status: accepted
- Date: 2026-08-28
- Owner: user/operator

## Decision

Context pairs deep audio analysis (librosa, CLAP), symbolic music work (pretty_midi, music21), license-gated generation adapters, and offline studio DSP (pedalboard; dawdreamer as a headless renderer) so the device acts as a **co-producer inside the DAW**. This expands the product beyond prompt-driven clip writes. It does not collapse the sidecar into the Live audio thread, and it does not replace verified write/license locks.

The four capability groups below are product requirements. They map onto phases 2–6. Phase 1 remains the LiveAPI harness.

## 1. Arrangement and structure

- **Loop-to-song staging.** Insert a 4- or 8-bar loop (audio or MIDI), choose a genre target (for example Melodic Techno or Pop), and build a full ~3-minute arrangement: intro, verse, build-up, drop, outro, with programmed energy, density, and velocity variation.
- **Intelligent tension and transitions.** Before a drop, generate contextual risers, sub-drops, or tonal impact sweeps that key-match the session. Commercial path uses a license-allowed adapter. MusicGen and AudioLDM 2 weights stay out of the commercial path unless a grant exists.
- **Dynamic variation injection.** Use symbolic models (music21, pretty_midi; Magenta optional, not primary) to humanize timing, add ghost notes, and write counter-melodies across multitrack sections so loops do not stay static.

## 2. Mix diagnostics and auto-staging

- **Frequency and masking audits.** Sidecar listens to the target bus / stems (not real-time on the audio thread). Spectral analysis flags overlaps (for example mud at 250 Hz kick vs bass, or lead vs vocal) and names the carve.
- **Automated sidechain and ducking.** From stem dynamic curves, pedalboard (offline) applies frequency-specific EQ cuts and ducking only when conflicting elements fire together. Preview before Apply. Not a static compressor preset dump.
- **Untreated-room corrector.** Optional diagnostic: ingest a room sweep or raw mix balance, predict translation in untreated rooms, and propose a compensatory master-bus curve. Apply is explicit.

## 3. Smart sample and sound curation

- **Contextual sample search.** Natural-language query over local sample folders via CLAP (example: “Find a dark, punchy analog snare that sits in the gap of my current lead line”). Results stay local.
- **On-demand texture synthesis.** If a build-up lacks depth, prompt (example: “gritty vinyl ambient rumble in F minor”), synthesize via a license-allowed adapter (Stable Audio Open only after legal review), process with pedalboard, place on Apply.
- **Stem splitter and remixer.** Demucs (MIT) splits imported audio into drums, bass, vocals, and other, so the producer can rearrange or isolate reference material.

## 4. DAW integration and session export

- **Populate the open Live Set.** Arrangement structure, locators, automation (filter sweeps, volume fades), and track colors write through the Live Object Model. This is the Ableton “project file” outcome.
- **Do not write `.als` files.** Unofficial parsers remain rejected. Ableton persistence is Live’s own save after LOM writes.
- **Cross-DAW export.** MIDI type-1 multitracks plus rendered stems / file-drop. Logic, GarageBand, and FL do not receive project rewrite. GarageBand has no arrangement API.
- **Non-destructive VST automation rehearsal.** dawdreamer may host third-party VST3/AU **headlessly offline** to audition automated parameter moves and save sidecar session state. It is not a replacement DAW. Steinberg/Apple hosting remains an owner legal action.

## Constraints that still hold

- No ML, CLAP, Demucs, or generation on the Live audio thread.
- No MusicGen / AudioLDM 2 / other CC-BY-NC weights in the commercial path.
- Prompt, host-track follow, drop-in, reference, reverence, and abstraction remain required chrome.
- Preview / analyze / audit / audition never write. Only Apply writes.
- Sidecar binds 127.0.0.1. User audio stays local in V1.
