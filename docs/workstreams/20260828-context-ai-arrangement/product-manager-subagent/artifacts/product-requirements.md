# Context product requirements

Owner revision 2026-08-28: prompt-driven, project-aware instrument/effect, then co-producer capabilities. See `docs/decisions/2026-08-28-context-granular-intent.md` and `docs/decisions/2026-08-28-context-coproducer-capabilities.md`. License locks (C-7) still hold. No `.als` write.

## User, problem, outcome

A Live 12 producer inserts Context on a track. The device hears that track, sees the rest of the set, and takes the next granular step from a prompt. Outcome: previewed, undoable writes — a mix of insert effect and session instrument.

## Journeys

1. **Track follow.** Device on Drums. Prompt “expand on this riff” or “add a bridge”. Sidecar uses host-track audio/MIDI plus `ProjectSnapshot`. Preview, then Apply.
2. **Drop-in.** User drops a loop into the device. Prompt “add an instrument”, “remove a layer”, or “add this effect”. Preview, then Apply or audition wet.
3. **Reference.** User drops any audio into Reference. Sets reverence and abstraction. Prompt describes the desired relation. Preview, then Apply.
4. **Project scope.** Scope = set. Prompt can add structure that touches other unlocked tracks. Locks protect what must not change.
5. **Fail closed.** Sidecar down: prompt/analyze/apply disabled.
6. **Loop-to-song.** 4- or 8-bar loop + genre target → ~3-minute intro / verse / build-up / drop / outro with energy, density, and velocity variation.
7. **Mix audit.** Masking hits shown; ducking and room curves apply only on Apply.
8. **Curation.** CLAP local search; license-allowed texture synth; Demucs isolate/rearrange.
9. **Session populate.** LOM writes structure, automation, and colors. MIDI/stem export for other DAWs. No `.als` file.

Analyze, preview, audit, and audition never write. Apply writes. Live Undo reverts.

## Requirements

C-1–C-9 remain. Added:

- C-10: Non-empty prompt required to run.
- C-11: Host-track follow + full `ProjectSnapshot`.
- C-12: Drop-in slot.
- C-13: Reference slot, reverence, abstraction (0–1).
- C-14: Scope, amount, wet, locks, focus, tempo/key lock, variation/replace, target section, audition vs apply.
- C-15: Loop-to-song from 4- or 8-bar loop + genre target.
- C-16: Key-matched transitions via allowed adapters only.
- C-17: Symbolic variation on unlocked MIDI.
- C-18: Read-only frequency/masking audit.
- C-19: Offline frequency-specific ducking; Apply explicit.
- C-20: Optional room-corrector master-bus curve; Apply explicit.
- C-21: CLAP search over local sample folders.
- C-22: Texture synthesis after legal review of the adapter.
- C-23: Demucs stem split.
- C-24: LOM populate (locators, automation, colors) + MIDI/stem export. No `.als` write.

Product rules:

- P-1: Apply is explicit. Analyze, prompt-preview, mix audit, and audition do not write clips unless Apply (or an explicit commit) is used.
- P-2: Do not claim Logic/GarageBand/FL project arrangement. Do not claim `.als` export.
- P-3: Prompt UI is required. Generation **adapters** stay license-gated and off until an allowed backend exists. Do not ship MusicGen or AudioLDM 2 weights.
- P-4: Sidecar-down disables Prompt run, Analyze, and Apply.
- P-5: Inspect still shows tempo, key, energy, section candidates, and inferred host role.
- P-6: Default Apply creates new clips/locators and does not overwrite locked items. Unlocked replace is opt-in via variation=false + amount.
- P-7: Demucs remains optional after the writer harness (used for “remove a layer” on a mix).
- P-8: On a drum host track, prefer drum-appropriate actions unless the prompt clearly targets another role or scope=set.

## Example prompts the contract must parse as intent, not decoration

- add a bridge
- expand on this riff
- add an instrument
- remove a layer
- add this effect
- inspired by the reference, keep my drums
- find a dark punchy analog snare that sits in the gap of my lead
- gritty vinyl ambient rumble in F minor
- build a 3-minute Melodic Techno arrangement from this loop

## Metrics

Baselines unknown. Do not invent numbers.

## Non-goals

In-process MusicGen/AudioLDM 2, unofficial `.als` write, dawdreamer-as-DAW, real-time generative accompaniment on the audio thread, AAX, FMOD/Wwise, claiming GarageBand arranges the project.
