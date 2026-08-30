# SE evidence: JUCE host

- `bash scripts/build-plugin.sh` succeeded on 2026-08-28 (AppleClang 17, CMake 4.1, JUCE 8.0.8).
- Binaries:
  - `plugin/build/Context_artefacts/Release/Standalone/Context.app`
  - `~/Library/Audio/Plug-Ins/Components/Context.component`
  - `~/Library/Audio/Plug-Ins/VST3/Context.vst3`
- `CONTEXT_SMOKE_APPLY=1` standalone write created:
  - `~/Documents/Context Drops/Context.mid` (SMF, track name Context, C3)
  - `~/Documents/Context Drops/Context.wav` (16-bit stereo 44.1 kHz from fixtures)
- Sidecar client hardcodes `127.0.0.1`. Audio thread is pass-through only.
