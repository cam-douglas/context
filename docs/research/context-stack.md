# Context stack and documentation corpus

Verified 2026-08-28. Do not treat the original master technology list as the architecture.

## Official Max / Ableton

- Live Object Model Track API, including `create_audio_clip` and `create_midi_clip`: https://docs.cycling74.com/apiref/lom/track/
- LiveAPI JavaScript client: https://docs.cycling74.com/apiref/js/liveapi/
- LOM overview: https://docs.cycling74.com/legacy/max8/vignettes/live_object_model
- Freeze devices for distribution: https://docs.cycling74.com/userguide/m4l/live_freezing/
- Max for Live production guidelines: https://maxforlive.com/resources/M4L-Production-Guidelines.pdf
- Max for Live edition: included in Live Suite; add-on for Live Standard; not available on Intro/Lite. https://help.ableton.com/hc/en-us/articles/206407124-Buying-Max-for-Live
- `node.script` cannot call LiveAPI; bridge through `v8` / `js` or Max objects (Cycling '74 forum, Florian).
- Prefer Max 9 `v8` on Live 12.2+: https://adammurray.link/max-for-live/v8-in-live/

## RNBO / plugin export

- RNBO + Max for Live: https://rnbo.cycling74.com/learn/rnbo-and-max-for-live
- VST3/AU export: https://rnbo.cycling74.com/learn/audio-plugin-target-export-overview
- Export licensing: https://support.cycling74.com/hc/en-us/articles/10730637742483-RNBO-Export-Licensing-FAQ
- RNBO is a compiled DSP graph. It cannot host Python or PyTorch models.

## Host format facts

- Logic Pro and GarageBand: AU only.
- FL Studio and most Windows DAWs: VST3.
- Pro Tools: AAX — out of V1.
- GarageBand can load an AU but has no arrangement API. Cross-DAW V1 claim is file drop, not project rewrite.
- Closed-source VST3 needs a Steinberg license. Apple binaries need code signing. JUCE wrappers may need a JUCE license.

## License matrix

| Component | License / terms | V1 commercial status |
|---|---|---|
| Demucs (`adefossez/demucs`) | MIT | Allowed |
| librosa, scipy, music21, pretty_midi, mido, pedalboard | OSI-style open licenses; confirm per pin | Allowed after pin review |
| AudioCraft / MusicGen weights | CC-BY-NC | Blocked without a Meta grant |
| AudioLDM 2 weights | Typically research / non-commercial — confirm card | Blocked commercially unless grant |
| Stable Audio Open | Stability Community License, commercial caps | Adapter only after legal review |
| CLAP (LAION) | Open weights; confirm pin | Allowed for local sample search after pin review |
| HeartMuLa / HeartCodec | Apache-2.0 (verify card at use) | Later optional local adapter; GPU-heavy |
| Magenta | Apache-2.0, aging TensorFlow stack | Optional; not primary (prefer music21 / pretty_midi) |
| dawdreamer | BSD-style; hosts third-party plugins | Offline renderer only; not a DAW. Plugin SDK licenses are owner legal |
| ElevenLabs / Suno / Udio | Paid APIs, output terms vary | Deferred; owner billing and Security |
| `.als` write | Unofficial reverse engineering | Allowed as a cloned export only; never overwrite the source set |

## Rejected as V1 architecture

- Running generative models inside the plugin audio thread
- Treating a Max for Live `.amxd` as a Logic/FL plugin
- Writing `.als` files as the Ableton export path (LOM populate + Live save is the Ableton outcome)
- dawdreamer as a replacement DAW (offline VST rehearsal only)
- FMOD / Wwise
- Web Audio as the product
- Embedding every listed model
