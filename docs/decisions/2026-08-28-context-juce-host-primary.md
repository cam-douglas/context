# Decision: JUCE AU / VST3 / Standalone is the primary Context host

Date: 2026-08-28

## Decision

The primary Context host on this Mac is a JUCE audio plug-in: **Audio Unit**, **VST3**, and a **standalone app**. Max for Live remains in the tree but is not the path we ask the owner to operate.

## Why

- Live 11 + Max 8.5.8 did not yield a verified on-track write. File → Open left the Live device inert.
- Live 11 cannot use Live 12 arrangement clip APIs.
- The owner asked to stop depending on Max and ship a standalone plug-in.

## Product consequence (do not revert)

A VST3 or AU **cannot rewrite an Ableton Live Set**. Apply writes MIDI and audio into `~/Documents/Context Drops` (file-drop). The user drags those files into any DAW. This is the same cross-DAW contract already locked for Logic / GarageBand / FL. Do not claim project rewrite.

The Python sidecar on `127.0.0.1` stays the brain. The plug-in is a thin host: hear the track, collect prompt/knobs, call localhost, export files.

## Legal still owner-only

- Steinberg VST3 SDK terms apply to **distributing** a VST3. Local build for this machine is for development.
- JUCE 8 is AGPLv3 unless a commercial JUCE license is purchased. Source stays in this repository.
- Apple code signing is required before sharing an AU/VST3 off this Mac.

## Status

Implemented as `plugin/` (JUCE CMake). Max devices are parked, not deleted.
