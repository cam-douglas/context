# Context plug-in host

JUCE 8 audio effect: **AU**, **VST3**, and a **standalone app**. Same localhost sidecar as the parked Max device. Apply never rewrites a DAW project.

## Build

```bash
bash scripts/build-plugin.sh
```

Clones JUCE 8.0.8 into `plugin/third_party/JUCE` (gitignored), then builds Release arm64.

## Run without a DAW

```bash
open "plugin/build/Context_artefacts/Release/Standalone/Context 8.app"
```

Type what to make, then **Audition** (temporary in-device play) or **Apply** (keeps files). A VST cannot rewrite an Ableton Live Set. Drag the in-plugin waveform into Live. Permanent files go to `~/Library/Application Support/Context/Plugin`. Audition files live in `.audition` and are deleted when you stop Audition unless you Apply. Drop a reference WAV onto the device to steer the next generation. Dials are Reverence (how faithfully it follows the prompt/reference) and Abstraction (how washed/transformed the clip is). Turn them, then generate again.

## Load in Ableton Live 11 Suite (Mac)

1. Rescan plug-ins if needed (Preferences → Plug-Ins → Rescan).
2. Browser → **Audio Units** → Context → **Context 8**. Do not load leftover Context 2–7.
3. Drop it on an audio track. It is an insert: the track audio passes through.
4. Apply writes files to Context/Plugin. Drag the waveform onto a track. This does **not** create clips via LiveAPI.

## Sidecar

The sidecar is a LaunchAgent on `127.0.0.1:8765` (`bash scripts/install-sidecar-agent.sh`). Opening the plug-in kickstarts it if health is down. Apply still writes local files if health is down.

## Legal

JUCE 8 is AGPLv3 unless you buy a commercial license. Do not distribute a VST3 until you accept Steinberg’s SDK terms. Apple signing is required before sharing binaries off this Mac.
