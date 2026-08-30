# Decision: Context is a prompt-driven, project-aware instrument/effect

- Status: accepted
- Date: 2026-08-28
- Owner: user/operator

## Decision

While Context is inserted on a track, it holds **project context** (the open Live Set or, later, a DAW snapshot) plus **host-track audio/MIDI**. The user steers it with a prompt field. Drop-in loops and a reference slot are first-class. Knobs **reverence** and **abstraction** scale reference fidelity versus creative freedom.

This supersedes the earlier provisional rule “V1 ships no generation UI.” The prompt is required chrome. License locks still apply: no MusicGen / CC-BY-NC weights in the commercial path; adapters stay gated.

## Required surfaces

- Prompt: “add a bridge”, “expand on this riff”, “add an instrument”, “remove a layer”, “add this effect”
- Host-track follow: device on a drum track hears that track and prefers drum-appropriate edits
- Whole-set context: other tracks, locators, tempo, key, playhead, loop
- Drop-in: sample or loop into the device, then prompt-modify
- Reference: any audio; generate similar or inspired material
- Reverence (0–1): closeness to the reference
- Abstraction (0–1): freedom versus sticking to the prompt

## Additional controls (accepted as product, not optional nice-to-haves)

- Scope: this track, selection, or whole set
- Amount: how much existing material may change
- Wet: insert-effect mix when auditioning on the host track
- Locks: tracks or clips that must not be rewritten
- Focus: playhead, loop brace, or selected clip
- Tempo/key lock
- Variation versus replace
- Audition (preview in-device) versus Apply (write to the set)
- Target section label when adding structure

## Consequences

- Device is both an **audio/MIDI effect** (hears the host track) and a **session instrument** (LiveAPI writes elsewhere in the set).
- Sidecar contract includes `IntentRequest` and `ProjectSnapshot`, not only an arrangement plan.
- Preview before apply remains mandatory.
