# Working memory

## Durable directives

- Execute agent-capable work directly; do not delegate routine implementation or investigation to the user.
- Use the sequential planning lifecycle for new projects and major implementations: phase 0 maps the full project, each later phase plan is generated only after the previous phase is implemented and verified, and closure produces `docs/plans/final_implementation_checklist.md`.
- Defer non-blocking human-only actions and missing credential values to the final phase while completing all possible code, configuration, adapters, tests, documentation, and environment-variable wiring first.
- Read `/AGENTS.md` first on every substantive turn and route detailed instructions through `/INSTRUCTIONS.md`.
- Use `/launch-pipeline` and `/instructions/LAUCH.md` as the linked entry point for a raw idea, major change, resume, remediation, or closure.
- Launch is preflight-first and bootstrap-gated: run read-only `/skills/launch-pipeline/scripts/preflight.mjs` before mode selection. Every pre-Build Cursor plan must close with `bash .cursor/scripts/bootstrap.sh` as the first post-Build action, then run that command after Build or explicit Agent-mode implementation authorization.
- Use adaptive role routing for substantive work: record required/skipped canonical roles, require role charters before action, and preserve evidence-backed handoffs under `docs/workstreams/`.
- Treat prompts and role identities as guidance, not production authorization; deterministic policy and external access controls govern sensitive actions.
- Never store passwords, tokens, private keys, or secret values in agent markdown, plans, memories, logs, or templates.

## Memory role

This file is a concise durable memory and index. Store only standing directives, stable decisions, high-level architecture notes, and links to canonical detail.

Operational history belongs in `/memory/memories/YYYY-MM-DD-continuation.md` or a topic-specific memory. Unresolved issues belong in `blockers/`; exact procedures belong in `runbooks/`; stable repeatable procedures belong in `/skills/`.

## System index

- Operating contract: `/AGENTS.md`
- Startup: `/BOOTSTRAP.md` and `/scripts/bootstrap.sh`
- Instruction router: `/INSTRUCTIONS.md`
- Product lifecycle launcher: `/instructions/LAUCH.md` and `/skills/launch-pipeline/SKILL.md`
- Project planning: `/instructions/PROJECT_PLANNING.md`
- Product strategy: `/instructions/STRATEGY.md`
- Sub-agent orchestration: `/instructions/SUBAGENTS.md`
- Canonical roles and stage gates: `/instructions/ROLES.md`
- Native role adapters: `/agents/`
- Live state: `/STATE.md`
- Plans: `docs/plans/`
- Strategic blueprints: `docs/blueprints/`
- Decisions: `docs/decisions/`
- Task workstreams and role handoffs: `docs/workstreams/`
- Agent role pipeline decision: `docs/decisions/2026-08-18-agent-role-pipeline.md`
- External governance setup: `docs/handover/agent-governance-operator-setup.md`
- Skills: `/SKILLS.md` and `/skills/`
- Tools: `/TOOLS.md`
- Active blockers: `/memory/blockers/`
- Runbooks: `/memory/runbooks/`
- Agent workspace layout: `/memory/runbooks/agent-workspace.md`
- Bootstrap procedure: `/memory/runbooks/agent-config-bootstrap.md`

## Durable product decisions

- The product is **Context** (device), distinct from this repository also named context. Decision: `docs/decisions/2026-08-28-context-product-name.md`.
- Primary host is JUCE AU / VST3 / Standalone (`plugin/`). Max for Live is parked. Apply still file-drops WAV/MIDI. Session export writes a cloned `.als` + als-json; the source set is never overwritten. DawDreamer 0.9.0 renders offline. Permanent files: `~/Library/Application Support/Context/Plugin`. Owner 2026-08-29 rotates the main generator on the word "rotate". Current slot: **audioldm2** via diffusers `AudioLDM2Pipeline` + `cvssp/audioldm2-music` (NC weights; `/synthesize` stays blocked). AudioLDM 2 VAE/vocoder decode runs on CPU; silent WAVs are rejected. Current host: **Context 14**. Typed request leads AudioLDM 2 conditioning. Other local generate slots: MusicGen and Stable Audio Open. Notes: Magenta MelodyRNN/MusicVAE in isolated TF venv, else `notes_for`. MIDI: music21 + note-seq + mido. Room: pyroomacoustics. Stems: Demucs. Sample search: in-plugin Library panel plus transformers CLAP `/search`. Decisions: `docs/decisions/2026-08-28-context-owner-stack-wiring.md`, `docs/decisions/2026-08-30-als-json-session-export.md`.
- Owner 2026-08-28: Context is a prompt-driven instrument/effect with project context, drop-in, reference, reverence, and abstraction. Decision: `docs/decisions/2026-08-28-context-granular-intent.md`.
- Owner 2026-08-28: Context is also a co-producer (loop-to-song, mix diagnostics, CLAP, Demucs, LOM populate). Decision: `docs/decisions/2026-08-28-context-coproducer-capabilities.md`.
- Blueprint: `docs/blueprints/2026-08-28_context.md`. Workstream: `docs/workstreams/20260828-context-ai-arrangement/`.
- Prompt ranks: SYSTEM = RULES (hard gate) > NEGATIVE (hard reject) > REQUEST (the face prompt; suggestion only). Defaults live in `plugin/src/PromptPolicy.h`. Open **Prompts** in the header to edit SYSTEM, RULES, or NEGATIVE. Live caches AU binaries; a rescan does not reload a device already on a track - ship a new plugin code when the owner cannot see UI changes.
- Owner 2026-08-30: plugin UI is ASCII only. No special or foreign characters in labels, status, menus, or preview text. Helper: `plugin/src/AsciiUi.h`.
- Agent-executable phases 1–7 remain in the tree. Phase 8 JUCE host is built on this Mac. Max C-5 is unverified and is not the owner path. Checklist: `docs/plans/final_implementation_checklist.md`.

## Existing workflow references

- Vercel: `/skills/vercel-deploy-workflow/SKILL.md` and `/memory/runbooks/vercel-workflow.md`
- Supabase: `/skills/supabase-linked-migrations/SKILL.md` and `/memory/runbooks/supabase-cli-macos.md`
