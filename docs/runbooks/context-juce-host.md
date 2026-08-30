# Runbook: Context JUCE host

## Build

```bash
bash scripts/build-plugin.sh
```

Evidence of a good build:

- `plugin/build/Context_artefacts/Release/Standalone/Context 7.app`
- `~/Library/Audio/Plug-Ins/Components/Context 7.component`
- `~/Library/Audio/Plug-Ins/VST3/Context 7.vst3`

## Standalone smoke

```bash
open "plugin/build/Context_artefacts/Release/Standalone/Context 7.app"
```

Type a prompt, then **Audition** or **Apply**. Load **Context 7**, not leftover Context 2–6. Permanent files: `~/Library/Application Support/Context/Plugin`. Drag the waveform into the DAW. Do not drag leftover `HOUSE-LOOP.wav`.

## Sidecar

The sidecar prefers a user LaunchAgent (`com.context.sidecar`) on `127.0.0.1:8765`. launchd is often throttled on this Mac; fallback:

```bash
bash sidecar/scripts/run-sidecar.sh
```

Opening Context 7 also kickstarts the supervisor if health is down. Logs: `~/Library/Logs/Context/sidecar.log`.

```bash
bash scripts/install-sidecar-agent.sh
curl -s http://127.0.0.1:8765/health
curl -s -X POST http://127.0.0.1:8765/rotate
```

## Ableton Live 11 Suite

Preferences → Plug-Ins → enable Audio Units and VST3 → Rescan. Load **Context 7**, not leftover Context 2–6. A rescan does not reload a device already on a track. The sample library is docked in the editor. Apply writes to Context/Plugin. Drag the waveform, not `HOUSE-LOOP.wav`. The device cannot create Live clips via LiveAPI.

## Do not

- Do not expect the plug-in to create Live clips via LiveAPI.
- Do not drag repo `Context.amxd` into Live.
- Do not claim Logic/GarageBand/FL project rewrite.
- Do not write into the signed `.vst3` / `.component` bundle.
