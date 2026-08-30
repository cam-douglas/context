# Fixed: invalid HTTP response during generation

## Symptoms

- Context 5 showed `invalid HTTP response` while Audition/Apply/Run was generating.

## Cause

- `/health` was a heavy probe. The editor polled it at 8 Hz with a 2s timeout on the UI thread.
- A failed health check ran `launchctl kickstart -k`, which killed the sidecar mid-Stable-Audio-Open generate. The plugin then saw a socket close with no HTTP headers.
- `/intent` also ran a full compose on an 8s timeout (`CONTEXT_COMPOSE_ON_INTENT` defaulted on).

## Fix

- Cheap `/health`; full probe only on `/health?full=1`.
- Supervisor never restarts a sidecar that is already listening on 8765.
- Editor skips health polls while compose is busy.
- `/intent` no longer composes by default.
- Compose exceptions return JSON instead of a bare TCP close.
- Automatic Demucs after generate is opt-in (`stems: true`); use `POST /stems`.

## Verified

- Sidecar tests: `tests.test_http`, `tests.test_compose`, `tests.test_generation_rotate`, `tests.test_phase2_to_6` OK.
- Context 5 AU/VST3 rebuilt and copied into `~/Library/Audio/Plug-Ins`.
- Live `/health` returns the lightweight ready payload; generator remains `stable_audio_open`.
