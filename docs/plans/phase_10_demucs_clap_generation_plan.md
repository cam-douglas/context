---
plan: phase_10_demucs_clap_generation
status: implemented
created: 2026-08-30
updated: 2026-08-30
owner: lead-agent
source_phase: docs/plans/phase_9_owner_stack_plan.md
workstream: docs/workstreams/20260830-demucs-clap-generation/manifest.md
---

# Phase 10: Demucs, CLAP, MusicGen, Stable Audio Open

## 1. Objective

Wire the owner-requested heavy audio tools into the sidecar so they actually run: Demucs stem split, CLAP text-to-sample search, MusicGen and Stable Audio Open generation.

## 2. Relation to project end-state

Completes the co-producer stack from `docs/decisions/2026-08-28-context-coproducer-capabilities.md` on the JUCE file-drop path.

## 3. Entry criteria and inherited evidence

Phase 9 compose path is live: pedalboard, pyroomacoustics, mido, note-seq. MusicGen and Stable Audio Open already have rotate adapters. Demucs and CLAP were flag-gated stubs.

## 4. Scope

- Real Demucs split on a written compose WAV and `/stems`
- Real CLAP ranking on `/search` and compose sample-library lookup
- MusicGen + Stable Audio Open remain the rotate generate path; `/synthesize` calls the same adapters
- Enable flags in `run-sidecar.sh` so the live process uses them

## 5. Non-goals

`.als` write, AudioLDM 2, commercial Suno/Udio/ElevenLabs calls, plugin chrome for a search UI, vendoring weights in git.

## 6. Assumptions

- CLAP via `transformers` (`laion/clap-htsat-unfused`) instead of `laion_clap` (not installed; transformers already is).
- Demucs MIT is allowed. MusicGen stays local/experimental (CC-BY-NC). Stable Audio Open still needs the Hugging Face license accept.
- First live call may download weights into `CONTEXT_MODEL_CACHE_DIR`.
- Unit tests keep flags at `0` so they do not download models.

## 7. Files

- `sidecar/src/context_sidecar/stems.py`
- `sidecar/src/context_sidecar/search.py`
- `sidecar/src/context_sidecar/adapters.py`
- `sidecar/src/context_sidecar/compose.py`
- `sidecar/src/context_sidecar/stack.py`
- `sidecar/scripts/run-sidecar.sh`
- `sidecar/tests/test_heavy_adapters.py`

## 8. Validation

- `tests.test_heavy_adapters`, `tests.test_compose`, `tests.test_phase2_to_6` pass with flags off.
- Mocked Demucs/CLAP tests prove compose records `backends.stems=demucs` and `backends.search=clap`.
- `demucs` 4.1.0 is installed in `sidecar/.venv`. CLAP uses transformers (`laion/clap-htsat-unfused`) on first enabled search.

## 9. Adaptive role map

| Role ID | Required or skipped | Reason |
|---|---|---|
| software-engineer-subagent | required | Adapter implementation |
| product-manager-subagent | skipped | Owner named the tools |
| ui-ux-developer-subagent | skipped | No chrome |
| security-engineer-subagent | skipped | No new bind; localhost only |
| growth-marketing-subagent | skipped | No launch |
| project-lead-subagent | skipped | Local wiring |

## 10. Environment-variable registry

| Variable | Purpose |
|---|---|
| CONTEXT_ENABLE_DEMUCS | Run Demucs when a WAV exists |
| CONTEXT_ENABLE_CLAP | Rank local samples with CLAP |
| CONTEXT_ENABLE_GENERATION | Allow `/synthesize` MusicGen/SAO |
| CONTEXT_SAMPLE_LIBRARY | Folder CLAP searches |
| CONTEXT_MODEL_CACHE_DIR | Weight cache |

## 11. Next Plan Generation Prompt

After this phase is verified, generate `docs/plans/phase_11_<slug>_plan.md` from the remaining owner-stack gaps (plugin search/stems chrome, SAO license, Magenta checkpoints).
