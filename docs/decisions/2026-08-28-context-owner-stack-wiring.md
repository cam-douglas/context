# Decision: wire the owner-provided stack into the sidecar

Date: 2026-08-28

## Decision

The owner asked to install and use the arrangement-engine stack (librosa, scipy, music21, mido, pretty_midi, pedalboard, pyroomacoustics, and gated adapters for Demucs/CLAP/MusicGen/commercial APIs). Those libraries are now imported on the sidecar compose/analysis/MIDI/DSP path. JUCE remains the frontend.

2026-08-30: mido writes the `.mid` file. Magenta NoteSequence quantize uses official `note-seq` in the torch sidecar. MelodyRNN and MusicVAE run in an isolated `sidecar/.venv-magenta` TensorFlow process and generate notes only. Stable Audio Open stays the WAV generator. If the Magenta worker or checkpoints are missing, compose uses `notes_for` and reports that — no stand-in MelodyRNN. pretty_midi remains the MIDI fallback.

2026-08-30: pyroomacoustics is on the compose path. After a WAV is written, `apply_room_to_wav` convolves it with a ShoeBox IR. Abstraction grows the room and wet mix; reverence shrinks and absorbs. Pedalboard reverb stays light so the IR owns the space. If the generator writes no WAV, room is skipped.

2026-08-30: Demucs, CLAP, MusicGen, and Stable Audio Open are wired. Compose splits the written WAV (or dropped reference) with Demucs when `CONTEXT_ENABLE_DEMUCS=1`. `/search` and compose sample-library lookup rank files with transformers CLAP (`laion/clap-htsat-unfused`) when `CONTEXT_ENABLE_CLAP=1`. MusicGen and Stable Audio Open remain the rotate generate path; `/synthesize` calls the same adapters when `CONTEXT_ENABLE_GENERATION=1`. AudioLDM 2 stays blocked. `run-sidecar.sh` turns the three flags on. First live call may download weights into `CONTEXT_MODEL_CACHE_DIR`.

## Still forbidden

- Overwriting a user's source `.als`. Session export clones and writes a new file (see `docs/decisions/2026-08-30-als-json-session-export.md`).
- Binding the sidecar off `127.0.0.1`.
- Storing API key values in the repo.
- Vendoring MusicGen / AudioLDM 2 / Demucs / CLAP weights.

## Status

Implemented in `sidecar/`. Heavy models remain import-gated. Commercial APIs wait on env names in the process environment.
