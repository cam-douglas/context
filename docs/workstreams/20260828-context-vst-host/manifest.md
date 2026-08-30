---
schema_version: 1
task_id: 20260828-context-vst-host
title: Context JUCE AU/VST3/Standalone host
source_request: Max isn't working; turn Context into a standalone VST plugin
status: implemented_local
risk_tier: moderate
created_at: 2026-08-28T09:41:00Z
updated_at: 2026-08-28T09:41:00Z
revision: 1
owner: user-operator
active_role: software-engineer-subagent
current_gate: implementation
---

# Workstream Manifest: Context JUCE host

## 1. Objective and requested outcome

Ship a loadable Context plug-in (AU + VST3) and a standalone app that talks to the existing sidecar and writes file-drop MIDI/audio. Stop requiring Max for Live for daily use.

## 2. Source request and project context

Owner: Max is not working; convert the project to a standalone VST. Existing sidecar, fixtures, and file-drop export stay. Decision: `docs/decisions/2026-08-28-context-juce-host-primary.md`.

## 3. Scope and non-goals

In: JUCE host, localhost sidecar client, `~/Documents/Context Drops`, Live/Logic file-drop. Out: Live Set rewrite, `.als` write, MusicGen, plugin-store publish, signing.

## 4. Risk classification

- Impacted domains: desktop audio plug-in, local HTTP
- Product/user impact: primary host changes from Max to JUCE
- Data, privacy, identity, or compliance impact: none beyond localhost
- Security/abuse exposure: plugin must bind/call 127.0.0.1 only
- Production/infrastructure impact: none
- Reversibility: Max tree kept
- Release significance: local owner build only
- Selected tier and evidence: **Tier 2** — new user-visible host, local only, reversible

## 5. Role routing matrix

| Role ID | Required or skipped | Reason/evidence | Predecessor | Owned paths | Status | Handoff |
|---|---|---|---|---|---|---|
| `product-manager-subagent` | required | Host/journey change (file-drop, not Live rewrite) | intake | `docs/decisions/2026-08-28-context-juce-host-primary.md` | complete | this manifest |
| `ui-ux-developer-subagent` | required | New plug-in chrome (prompt, knobs, Apply, status) | PM | `plugin/src/PluginEditor.*` | complete | editor implements existing chrome rows |
| `software-engineer-subagent` | required | JUCE CMake + sidecar client + drop writer | UX | `plugin/` | in_progress | build evidence |
| `security-engineer-subagent` | required | New network client in a plug-in | SE | `plugin/src/SidecarClient.*` | pending | 127.0.0.1 only |
| `growth-marketing-subagent` | skipped | No public launch or claims change beyond existing forbidden-claim list | — | — | skipped | no positioning work |
| `project-lead-subagent` | required | Reconcile host pivot and owner handoff | SE+Sec | `docs/workstreams/20260828-context-vst-host/delivery/` | pending | after build |

## 6. Requirement traceability

| Requirement ID | Requirement | Source | Owner role | Acceptance evidence | Status |
|---|---|---|---|---|---|
| V-1 | Standalone app launches without Max | owner | SE | `Context.app` exists | pending |
| V-2 | AU and/or VST3 built for this Mac | owner | SE | `.component` / `.vst3` | pending |
| V-3 | Apply writes MIDI+WAV to Context Drops | owner | SE | files on disk | pending |
| V-4 | Sidecar calls 127.0.0.1 only | lock | Sec | SidecarClient | pending |
| V-5 | No `.als` / no DAW project rewrite | lock | PM | drop folder only | pending |

## 7. Dependency and gate order

Intake → PM/UX contract (this decision + chrome reuse) → SE build → Sec review of client → PL handoff.

## 8. Path and external-system ownership

| Path or system | Writer | Read-only reviewers | Allowed operation | Ownership window |
|---|---|---|---|---|
| `plugin/` | SE | Sec, PL | create/build | this task |
| `sidecar/` | SE (read; export already exists) | — | no contract break | this task |
| `max/` | none | — | parked | — |

## 9. Tool and MCP constraints

CMake 4.1 + Xcode 28 toolchain. JUCE 8 via git clone into `plugin/third_party/JUCE` (not vendored). No Steinberg distribution.

## 10. Decisions, clarifications, and provisional assumptions

- `verified`: Live 11 Max harness is not the owner path.
- `verified`: File-drop is the write path for AU/VST3.
- `provisional`: Ableton Live 11 Suite will load the AU (Audio Units). VST3 also built.
- `provisional`: JUCE splash remains on (AGPL / no commercial JUCE license).

## 11. Active blockers and remediation loops

| Finding or requirement | Owner | Status | Invalidated gates | Recheck requirement |
|---|---|---|---|---|
| Max on-track Apply inert | superseded by this host | open in Max blocker file | M4L C-5 | plugin V-1–V-3 |

## 12. Artifact and evidence index

- Decision: `docs/decisions/2026-08-28-context-juce-host-primary.md`
- Plan: `docs/plans/phase_8_juce_host_plan.md`

## 13. Residual risks and human actions

Steinberg distribution, Apple signing, JUCE commercial license, plugin-store publish.

## 14. Owner decisions and approvals

Owner asked to abandon Max operation in favor of a standalone VST. File-drop (no Live Set rewrite) is the defensible default.

## 15. Closure

- Final verdict: open until build + drop-folder evidence
- Owner handoff: pending
- Remaining manual actions: load AU in Live, drag files from Context Drops
