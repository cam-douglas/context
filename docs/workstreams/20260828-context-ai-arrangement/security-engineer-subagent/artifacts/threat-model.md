# Context threat model (phase 0)

## Assets

User audio/MIDI, arrangement JSON, future model weights, future API keys.

## Actors

Local producer (trusted on-machine), malware on the same machine, future remote API vendor.

## Boundaries

Max device (Live process) → localhost HTTP → sidecar. No internet in V1.

## Threats

- T1: Sidecar bound beyond localhost → LAN exposure of user audio.
- T2: Path traversal in `file_path` when creating clips.
- T3: Secrets in Max presets or markdown.
- T4: Shipping CC-BY-NC weights in a commercial build.
- T5: Prompt/model output used as shell commands.

## Controls

- Bind 127.0.0.1 only.
- Allow only user-selected or sidecar-written paths.
- `CONTEXT_ENABLE_GENERATION` default 0.
- License matrix in `docs/research/context-stack.md`.
- Never interpolate model text into a shell.
