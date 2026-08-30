# Context Max Project

Unfrozen Max for Live **audio effect**: hears the host track (`plugin~` / `plugout~`) and writes the set through LiveAPI.

## Layout

```text
max/context/
  Context.maxproj
  Context.maxpat          source patcher (also copied as Context.amxd JSON)
  Context.amxd            unfrozen source document (same patcher JSON)
  code/context_device.js
  code/liveapi_snapshot.js
  code/liveapi_writer.js
  code/sidecar_client.js  node.script HTTP client
```

Do not freeze this device for distribution until the Live harness checklist in `docs/runbooks/context-liveapi-harness.md` passes.

## Chrome (phase 1)

Header health, host strip, prompt + Run, drop-in path, reference path, reverence, abstraction, amount, wet, inspect, preview, Audition, Apply, status. Audition never writes. On Live 11, Apply uses Session `create_clip` (clip named Context). Live 12 arrangement `create_audio_clip` / `create_midi_clip` are used when present.
