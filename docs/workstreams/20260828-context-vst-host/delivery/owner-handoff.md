# Owner handoff: Context JUCE host

Date: 2026-08-30

## What works now

Context 5 is a real plug-in on this Mac:

- Standalone: `plugin/build/Context_artefacts/Release/Standalone/Context 5.app`
- Audio Unit: `~/Library/Audio/Plug-Ins/Components/Context 5.component`
- VST3: `~/Library/Audio/Plug-Ins/VST3/Context 5.vst3`

A VST cannot rewrite an Ableton Live Set. Keep the clip in the device as a waveform, then drag it onto a track. Permanent files go to `~/Library/Application Support/Context/Plugin`. Audition files live in `Plugin/.audition` and are deleted when you stop Audition unless you Apply.

## What you do

1. Rescan plug-ins. Load **Context 5**, not leftover Context 2–4.
2. Type what to make. Optional: drop a reference WAV/AIFF/FLAC/MP3 onto the device.
3. Set Reverence, Abstraction, Amount, and Wet.
4. **Audition** plays a temporary clip. **Stop** deletes it. **Apply** keeps it in Context/Plugin.
5. Drag the waveform into Live. MIDI still needs an instrument.

Sidecar: `bash sidecar/scripts/run-sidecar.sh` on `127.0.0.1:8765`.

## Still later / legal

Steinberg VST3 distribution, Apple signing, JUCE commercial license if you close the source. Do not publish to a plug-in store yet. Stable Audio Open is the active rotation slot and falls back to pedalboard until that package is installed.
