---
schema_version: 1
task_id: 20260830-demucs-clap-generation
title: Wire Demucs, MusicGen, Stable Audio Open, and CLAP
status: implemented_local
risk_tier: moderate
---

# Workstream: Demucs / CLAP / generation

Required: software-engineer-subagent (sidecar adapters on compose/search/stems).
Skipped: product-manager (owner specified the four tools), ui-ux (no new chrome), security-engineer (still 127.0.0.1; no secrets; residual: first-run weight download into Application Support), growth-marketing (no launch), project-lead (local wiring only).

Locks: 127.0.0.1 only, no unofficial `.als` write, no key values in git, no AudioLDM 2, no stand-in audio.
