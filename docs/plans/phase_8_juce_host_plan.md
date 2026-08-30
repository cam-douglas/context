---
plan: phase_8_juce_host
status: implemented
created: 2026-08-28
updated: 2026-08-28
owner: lead-agent
source_phase: docs/plans/phase_6_cross_daw_host_plan.md
workstream: docs/workstreams/20260828-context-vst-host/manifest.md
---

# Phase 8: JUCE AU / VST3 / Standalone host

## 1. Objective

Replace Max-for-Live as the owner-operated host with a JUCE plug-in and standalone app that uses the existing sidecar and writes file-drop MIDI/audio.

## 2. Relation to project end-state

This is the Phase 6 thin host, pulled forward because the Live 11 Max harness did not work.

## 3. Entry criteria and inherited evidence

Sidecar 44 tests + owner-smoke. Export helper exists. Max C-5 unverified.

## 4. Scope

JUCE 8 CMake project: pass-through effect, chrome (prompt, knobs, Run, Audition, Apply, status), `127.0.0.1` sidecar client, `~/Documents/Context Drops`.

## 5. Non-goals

Live Set rewrite, `.als`, MusicGen, signing, store publish, freezing Max.

## 6. Current-state audit

`plugin/` had only a README. `max/` is parked.

## 7. Assumptions, constraints, risks, and decisions

See `docs/decisions/2026-08-28-context-juce-host-primary.md`.

## 8. Dependencies

CMake, Xcode, network to clone JUCE 8.0.8. Sidecar optional for first Apply (local fixtures still drop).

## 9. Architecture and affected systems

Host (JUCE, no DSP ML) ↔ localhost JSON ↔ `sidecar/`. Write path is files, not LOM.

## 10. Files and paths in scope

`plugin/CMakeLists.txt`, `plugin/src/*`, `scripts/build-plugin.sh`, runbook, decision, this plan.

## 11. Supporting documents to create or update

`docs/runbooks/context-juce-host.md`, `plugin/README.md`, STATE, checklist.

## 12. Ordered implementation tasks

1. Record decision + workstream.
2. Implement JUCE host + drop writer + sidecar client.
3. Build AU, VST3, Standalone; copy into macOS plug-in folders.
4. Validate binaries exist; record residual legal actions.

## 13. Validation

`Context.app` exists. AU and VST3 bundles exist. Apply creates files under Context Drops when run.

## 14. Deferred human actions

Load the AU in Live; drag dropped files; Steinberg/Apple/JUCE licenses for distribution.

## 15. Acceptance criteria

Standalone launches. Plug-in formats built. Apply is file-drop only. Sidecar client targets 127.0.0.1 only.

## 16. Next-plan prompt

After V-1–V-3 verified, generate a harden/signing plan only if the owner wants to distribute off this Mac.
