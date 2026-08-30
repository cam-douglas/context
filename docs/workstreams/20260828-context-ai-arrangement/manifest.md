---
schema_version: 1
task_id: 20260828-context-ai-arrangement
title: Context AI arrangement engine
source_request: /launch-pipeline — Max for Live plus cross-DAW AI compose/arrange; owner named the product Context
status: phase_7_checklist
risk_tier: high
created_at: 2026-08-28T08:40:00Z
updated_at: 2026-08-28T09:20:00Z
revision: 5
owner: user-operator
active_role: user-operator
current_gate: owner-live-checklist
---

# Workstream Manifest: Context AI arrangement engine

## 1. Objective and requested outcome

Found and deliver Context: a prompt-driven Max for Live co-producer that hears the host track, holds whole-set context, and writes undoable edits. Drop-in, reference, reverence, abstraction, then loop-to-song, mix audits, CLAP search, allowed generation, Demucs, and LOM session populate. Later: VST3/AU file-drop host. No `.als` write.

## 2. Source request and project context

User invoked `/launch-pipeline` with a Max-for-Live plus any-DAW plugin requirement and a large open-source/AI catalog. Owner renamed the product to Context and authorized Build.

## 3. Scope and non-goals

In scope: strategy, phase 0 foundations, sidecar contract, Max Project skeleton, role pipeline, license matrix.

Non-goals: shipping every listed model, `.als` write, production plugin-store publish, paid API spend, weakening governance hooks.

## 4. Risk classification

- Impacted domains: product, UX, audio plugin, local ML/DSP, licenses, privacy of user stems
- Product/user impact: new user-facing device
- Data, privacy, identity, or compliance impact: user audio on disk; optional later cloud adapters
- Security/abuse exposure: localhost sidecar, model weights, future API keys
- Production/infrastructure impact: none yet
- Reversibility: planning and local code are reversible; plugin store and licenses are not
- Release significance: new product
- Selected tier and evidence: **Tier 3** — user audio, license/commercial claims, plugin distribution, possible network adapters

## 5. Role routing matrix

Every canonical role is required.

| Role ID | Required or skipped | Reason/evidence | Predecessor | Owned paths | Status | Handoff |
|---|---|---|---|---|---|---|
| `product-manager-subagent` | required | New product, scope, acceptance | lead intake | `docs/workstreams/20260828-context-ai-arrangement/product-manager-subagent/` | planning | pending |
| `ui-ux-developer-subagent` | required | Device UI, apply/preview, error states | PM handoff | `.../ui-ux-developer-subagent/` | pending | pending |
| `software-engineer-subagent` | required | Sidecar, Max device, tests | UI/UX handoff | `sidecar/`, `max/context/`, later `plugin/` | pending | pending |
| `security-engineer-subagent` | required | Tier 3, audio privacy, licenses | Engineering handoff | `.../security-engineer-subagent/` | pending | pending |
| `growth-marketing-subagent` | required | Positioning, claims, Ableton community | Security handoff | `.../growth-marketing-subagent/` | pending | pending |
| `project-lead-subagent` | required | Tier 1–4 reconciliation | Growth handoff | `.../project-lead-subagent/`, `delivery/` | pending | pending |

## 6. Requirement traceability

| Requirement ID | Requirement | Source | Owner role | Acceptance evidence | Status |
|---|---|---|---|---|---|
| C-1 | Frozen `.amxd` loads in Live 12 + Max for Live | blueprint | software-engineer-subagent | phase 1 device load | planned |
| C-2 | Sidecar localhost; fail closed if down | blueprint | software-engineer-subagent | health check + UI error | planned |
| C-3 | Analyze clips for tempo/key/energy/sections | blueprint | software-engineer-subagent | fixture tests | planned |
| C-4 | Previewable arrangement schema | blueprint | product-manager-subagent | schema + UI spec | planned |
| C-5 | LOM apply with undo | blueprint | software-engineer-subagent | LiveAPI harness | planned |
| C-6 | Optional Demucs split | blueprint | software-engineer-subagent | later phase | planned |
| C-7 | No CC-BY-NC weights in commercial path | blueprint | security-engineer-subagent | license matrix | planned |
| C-8 | No secrets in repo | blueprint | security-engineer-subagent | scan | planned |
| C-9 | Cross-DAW host after V1 | blueprint | product-manager-subagent | phase map | planned |
| C-10 | Required prompt field | owner 2026-08-28 | ui-ux-developer-subagent | intent schema + UI spec | planned |
| C-11 | Host-track follow + ProjectSnapshot | owner 2026-08-28 | software-engineer-subagent | intent schema | in_progress |
| C-12 | Drop-in modify | owner 2026-08-28 | software-engineer-subagent | intent schema | in_progress |
| C-13 | Reference + reverence + abstraction | owner 2026-08-28 | software-engineer-subagent | intent schema | in_progress |
| C-14 | Scope, amount, wet, locks, focus, locks | owner 2026-08-28 | ui-ux-developer-subagent | design spec | planned |
| C-15 | Loop-to-song + genre | owner 2026-08-28 | software-engineer-subagent | phase 3 | planned |
| C-16 | Key-matched transitions (allowed adapters) | owner 2026-08-28 | software-engineer-subagent | phase 4 | planned |
| C-17 | Symbolic variation | owner 2026-08-28 | software-engineer-subagent | phase 3 | planned |
| C-18 | Mix masking audit | owner 2026-08-28 | software-engineer-subagent | phase 2 | planned |
| C-19 | Offline ducking | owner 2026-08-28 | software-engineer-subagent | phase 5 | planned |
| C-20 | Room-corrector curve | owner 2026-08-28 | software-engineer-subagent | phase 5 | planned |
| C-21 | CLAP local sample search | owner 2026-08-28 | software-engineer-subagent | phase 4 | planned |
| C-22 | Texture synthesis (reviewed adapter) | owner 2026-08-28 | software-engineer-subagent | phase 4 | planned |
| C-23 | Demucs stems | owner 2026-08-28 | software-engineer-subagent | phase 4 | planned |
| C-24 | LOM populate + MIDI/stem export; no `.als` | owner 2026-08-28 | software-engineer-subagent | phases 3 and 6 | planned |

## 7. Dependency and gate order

Intake → PM → UI/UX → Engineering → Security → Growth → Project Lead → owner.

## 8. Path and external-system ownership

| Path or system | Writer | Read-only reviewers | Allowed operation | Ownership window |
|---|---|---|---|---|
| `docs/blueprints/2026-08-28_context.md` | lead | all roles | create/update | phase 0 |
| `docs/plans/phase_0_foundations_plan.md` | lead | all roles | create/update | phase 0 |
| `docs/workstreams/20260828-context-ai-arrangement/` | lead | roles | materialize role artifacts | until closure |
| `sidecar/` | software-engineer-subagent | Security, Project Lead | implement | after UI/UX handoff |
| `max/context/` | software-engineer-subagent | Security, Project Lead | implement | phase 1 |
| `.cursor/STATE.md` | lead | Project Lead | update | continuous |
| Ableton Live / Max | owner machine | Engineering | local test | phase 1+ |
| Cloud APIs | none | Security | not authorized | deferred |

## 9. Tool and MCP constraints

No production MCP mutations. No secret reads. Browser/Figma unused until UI/UX verifies access. Official docs already captured in `docs/research/context-stack.md`.

## 10. Decisions, clarifications, and provisional assumptions

- `verified`: product name is Context
- `verified`: prompt, project context, drop-in, reference, reverence, abstraction
- `provisional`: Ableton-first V1; generation adapters license-gated; RNBO/JUCE later
- `verified`: owner repair + bootstrap READY (2026-08-28T08:53:05.350Z)

## 11. Active blockers and remediation loops

| Finding or requirement | Owner | Status | Invalidated gates | Recheck requirement |
|---|---|---|---|---|
| Missing protected `AGENTS.md` / `.cursorignore` / governance workflow | owner | resolved | bootstrap, preflight READY | preflight READY 2026-08-28T08:53:05.350Z |

## 12. Artifact and evidence index

- Blueprint: `docs/blueprints/2026-08-28_context.md`
- Research: `docs/research/context-stack.md`
- Name decision: `docs/decisions/2026-08-28-context-product-name.md`
- Granular intent: `docs/decisions/2026-08-28-context-granular-intent.md`
- Co-producer capabilities: `docs/decisions/2026-08-28-context-coproducer-capabilities.md`
- Phase 0: `docs/plans/phase_0_foundations_plan.md`
- Phase 1: `docs/plans/phase_1_liveapi_harness_plan.md`
- Resolved blocker: `.cursor/memory/blockers-fixed/control-plane-bootstrap.md`
- Owner repair: `docs/handover/apply-missing-control-plane-files.sh`

## 13. Residual risks and human actions

Protected-file repair is done. Live 12 + Max for Live required for phase 1 validation. Steinberg/Apple/JUCE licenses deferred.

## 14. Owner decisions and approvals

Recorded: name = Context. Build authorized. Production publish not authorized.

## 15. Closure

- Final verdict: open
- Owner handoff: not started
- Closure evidence: none
- Remaining manual actions: Live 12 + Max for Live for phase 1
