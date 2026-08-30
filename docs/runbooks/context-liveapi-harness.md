# Runbook: Context LiveAPI harness

## Sidecar (no Live required)

```bash
cd sidecar
CONTEXT_SIDECAR_PORT=8765 PYTHONPATH=src python -m context_sidecar.http
```

In another shell:

```bash
cd sidecar
PYTHONPATH=src python -m unittest tests.test_http tests.test_device tests.test_snapshot tests.test_schema tests.test_intent -v
```

Bind is `127.0.0.1` only. Empty prompt returns HTTP 400.

## Fixtures

```bash
python fixtures/generate.py
```

Creates `fixtures/silence.wav` (1s silent stereo) and `fixtures/empty.mid` (empty one-bar MIDI).

## Machine detected (2026-08-28)

- Ableton **Live 11 Suite 11.3.43** at `/Applications/Ableton Live 11 Suite.app` (includes Max for Live).
- **Max 9.0.4** at `/Applications/Max.app` (v8 available).
- Live 12 is not installed. Use Live 11 Suite for the harness. JS LiveAPI scripts are ES5-compatible.
- Project copies: `~/Documents/Max 9/Projects/Context` and `~/Documents/Max 8/Max for Live Devices/Context`.

Owner smoke (no Live): `bash scripts/owner-smoke.sh`

## Live + Max for Live checklist (owner machine)

C-5 write evidence is UNVERIFIED until these steps run.

1. Start the sidecar on localhost (`bash scripts/owner-smoke.sh` or `PYTHONPATH=src python -m context_sidecar.http` from `sidecar/`).
2. Open **Live 11 Suite** (or Live 12 if you install it later).
3. **Do not use standalone `/Applications/Max.app` (Max 9 trial).** That build cannot save Max for Live devices. Use Live’s bundled Max 8.5.8 instead:
   1. Quit Max 9 if it is open.
   2. Live → Preferences → File/Folder (or Plug-Ins) → **Max Application** → choose  
      `/Applications/Ableton Live 11 Suite.app/Contents/App-Resources/Max/Max.app`
   3. Restart Live.
   4. Browser → Audio Effects → Max for Live → **Max Audio Effect**. Drop it on an unlocked audio track.
   5. Create → **Insert MIDI Track** (unlocked, not frozen).
   6. On the audio-track device title bar, click the Max **Edit** button (yellow/pencil). Max 8.5.8 opens under the Suite license.

   **Do not File → Open `Context.maxpat`.** That opens a detached window. The Live device stays empty, so Apply on the track does nothing.

   **Do not drag `Context.amxd` from the repo or Documents into Live.** Those copies are source JSON, not a Live-loadable device.

4. Type the harness into the **on-track** Edit window (this is the only reliable Live 11 path):
   1. In that Edit window, unlock the patcher (**Cmd+E**).
   2. Click empty canvas and type this object, then Enter:

      `js /Users/camdouglas/context/max/context/code/context_harness.js`

      The object must stay white/grey, not red. If it is red, the path is wrong.
   3. Type `b` then Enter (a circle **button**). Type `apply` then Enter (a message box).
   4. Connect **button → apply → js**.
   5. Optional: type `prepend set` and `live.comment`, then connect the **right** outlet of `js` → `prepend set` → `live.comment`.
   6. **Cmd+S**. Close or keep the editor. **View → Max Window** should show `Context: harness loaded` and a track count.
   7. In Live, press **Tab** until you see **Session View** (the clip-slot grid, not the timeline).
   8. Click the circle button (or Apply). A MIDI clip named **Context** should appear on the MIDI track. Status / Max Window reports the write.
   9. **Cmd+Z** removes the clip.

   File → Open of `Context.maxpat` is optional and only useful if you **copy/paste its objects into this same Edit window**. Opening it as its own window is not the plugin.

4b. Confirm chrome: health, host strip, prompt, drop-in, reference, reverence, abstraction, amount, wet, inspect, preview, Audition, Apply, status.
5. Empty prompt: Run stays disabled. Status: `Type what to do next, then run.`
6. Sidecar is optional for this Live 11 write test. Later Run/Apply product gates still fail-closed when the sidecar is down.
7. Restart sidecar. Type `add a bridge`. Run. Preview JSON appears. Audition does **not** create clips.
8. Live 11: Apply writes a **Session** MIDI clip via `clip_slots N create_clip`. It also tries Live 12 `create_audio_clip` / `create_midi_clip` and `duplicate_clip_to_arrangement` when those exist. Look at Session View first.
9. Live Undo removes the clip.
10. Frozen tracks are skipped. A set with no unlocked MIDI track must surface that error, not a success.

## Snapshot dump

Bang `snapshot` on `liveapi_snapshot.js`. The JSON must include `host_track` and `project.tracks` (host plus any other tracks). A drum-named host track must report `inferred_role: drums`.
